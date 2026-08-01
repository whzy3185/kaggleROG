"""Replay the public GeoAnchor booster OOF stack against local train suffixes.

The public artifact bundle stores the original row-level out-of-fold
predictions inside five serialized ``koolbox`` Trainer objects.  This module
reconstructs the exact target row order from the competition CSV files,
audits every stored score, and rebuilds the grouped Ridge meta learner.

It intentionally stops before GeoAnchor's leaderboard-derived R2000 layer.
That single-test-well correction has no train-fold analogue and therefore
cannot produce an honest local OOF score.
"""

from __future__ import annotations

import sys
import types
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold


ARTIFACTS = (
    ("lightgbm-1", "lgbmregressor_trainer_20260526182612.pkl"),
    ("lightgbm-2", "lgbmregressor_trainer_20260526190415.pkl"),
    ("lightgbm-3", "lgbmregressor_trainer_20260526192806.pkl"),
    ("catboost-1", "catboostregressor_trainer_20260526193740.pkl"),
    ("catboost-2", "catboostregressor_trainer_20260526194838.pkl"),
)

RIDGE_PARAMS = {
    "random_state": 42,
    "alpha": 1.6602834637650032,
    "tol": 0.0005030247295617308,
    "positive": True,
    "fit_intercept": True,
}


@dataclass(frozen=True)
class OOFReplay:
    index: pd.DataFrame
    base_predictions: pd.DataFrame
    ridge_prediction: np.ndarray
    warmup_prediction: np.ndarray
    trainer_audit: pd.DataFrame
    ridge_fold_audit: pd.DataFrame


def _install_koolbox_pickle_stub() -> None:
    """Provide only the class path required by the serialized Trainer shell."""

    if "koolbox.trainer.trainer" in sys.modules:
        return
    package = types.ModuleType("koolbox")
    package.__path__ = []
    trainer_package = types.ModuleType("koolbox.trainer")
    trainer_package.__path__ = []
    trainer_module = types.ModuleType("koolbox.trainer.trainer")

    class Trainer:
        pass

    Trainer.__module__ = "koolbox.trainer.trainer"
    trainer_module.Trainer = Trainer
    trainer_package.Trainer = Trainer
    package.Trainer = Trainer
    sys.modules.update(
        {
            "koolbox": package,
            "koolbox.trainer": trainer_package,
            "koolbox.trainer.trainer": trainer_module,
        }
    )


def rebuild_suffix_index(train_dir: Path) -> pd.DataFrame:
    """Recreate the exact row order used by the public feature builder."""

    parts: list[pd.DataFrame] = []
    for path in sorted(train_dir.glob("*__horizontal_well.csv")):
        frame = pd.read_csv(path, usecols=["MD", "TVT", "TVT_input"])
        eval_mask = frame["TVT_input"].isna()
        known = frame.loc[~eval_mask]
        if not eval_mask.any() or len(known) < 10 or frame["TVT"].isna().all():
            continue
        well_id = path.name.removesuffix("__horizontal_well.csv")
        row_index = frame.index[eval_mask].to_numpy(dtype=int)
        base = np.float32(known["TVT_input"].iloc[-1])
        last_md = np.float32(known["MD"].iloc[-1])
        target = frame.loc[eval_mask, "TVT"].to_numpy(dtype=np.float32) - base
        if not np.isfinite(target).all():
            raise ValueError(f"Non-finite suffix target in {path}")
        parts.append(
            pd.DataFrame(
                {
                    "well_id": well_id,
                    "row_index": row_index,
                    "id": [f"{well_id}_{row}" for row in row_index],
                    "last_known_tvt": np.full(len(row_index), base, dtype=np.float32),
                    "md_since": (
                        frame.loc[eval_mask, "MD"].to_numpy(dtype=np.float32) - last_md
                    ),
                    "target": target,
                }
            )
        )
    if not parts:
        raise FileNotFoundError(f"No usable training suffixes under {train_dir}")
    result = pd.concat(parts, ignore_index=True)
    if result["id"].duplicated().any():
        raise ValueError("Reconstructed suffix IDs are not unique")
    return result


def _artifact_path(root: Path, filename: str) -> Path:
    matches = list(root.rglob(filename))
    if len(matches) != 1:
        raise FileNotFoundError(
            f"Expected exactly one {filename} below {root}, found {len(matches)}"
        )
    return matches[0]


def load_base_oof(
    artifact_root: Path,
    target: np.ndarray,
    *,
    alignment_tolerance: float = 1e-7,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load five public OOF vectors and validate their recorded RMSE values."""

    _install_koolbox_pickle_stub()
    columns: dict[str, np.ndarray] = {}
    audit_rows: list[dict[str, float | int | str | bool]] = []
    for name, filename in ARTIFACTS:
        path = _artifact_path(artifact_root, filename)
        trainer = joblib.load(path)
        prediction = np.asarray(trainer.oof_preds, dtype=np.float64).reshape(-1)
        if len(prediction) != len(target):
            raise ValueError(
                f"{name} has {len(prediction):,} OOF rows; expected {len(target):,}"
            )
        if not np.isfinite(prediction).all():
            raise ValueError(f"{name} OOF contains non-finite values")
        computed = float(np.sqrt(np.mean((prediction - target) ** 2)))
        recorded = float(trainer.overall_score)
        delta = computed - recorded
        aligned = abs(delta) <= alignment_tolerance
        audit_rows.append(
            {
                "model": name,
                "artifact": str(path.resolve()),
                "rows": len(prediction),
                "computed_rmse": computed,
                "recorded_rmse": recorded,
                "delta": delta,
                "aligned": aligned,
            }
        )
        if not aligned:
            raise ValueError(
                f"{name} score alignment failed: computed={computed}, recorded={recorded}"
            )
        columns[name] = prediction
    return pd.DataFrame(columns), pd.DataFrame(audit_rows)


def grouped_ridge_oof(
    base_predictions: pd.DataFrame,
    target: np.ndarray,
    groups: np.ndarray,
) -> tuple[np.ndarray, pd.DataFrame]:
    """Rebuild the public five-fold positive Ridge meta learner."""

    x = base_predictions.to_numpy(dtype=np.float64)
    prediction = np.empty(len(target), dtype=np.float64)
    rows: list[dict[str, float | int]] = []
    cv = GroupKFold(n_splits=5)
    for fold, (train_idx, valid_idx) in enumerate(cv.split(x, target, groups=groups)):
        model = Ridge(**RIDGE_PARAMS)
        model.fit(x[train_idx], target[train_idx])
        prediction[valid_idx] = model.predict(x[valid_idx])
        error = prediction[valid_idx] - target[valid_idx]
        row: dict[str, float | int] = {
            "fold": fold,
            "train_rows": len(train_idx),
            "valid_rows": len(valid_idx),
            "valid_wells": len(np.unique(groups[valid_idx])),
            "rmse": float(np.sqrt(np.mean(error**2))),
            "intercept": float(model.intercept_),
        }
        row.update(
            {
                f"coef_{name}": float(value)
                for name, value in zip(base_predictions.columns, model.coef_)
            }
        )
        rows.append(row)
    if not np.isfinite(prediction).all():
        raise ValueError("Ridge OOF contains non-finite values")
    return prediction, pd.DataFrame(rows)


def replay_geoanchor_oof(train_dir: Path, artifact_root: Path) -> OOFReplay:
    index = rebuild_suffix_index(train_dir)
    target = index["target"].to_numpy(dtype=np.float32)
    base, trainer_audit = load_base_oof(artifact_root, target)
    ridge, ridge_audit = grouped_ridge_oof(
        base,
        target,
        index["well_id"].to_numpy(dtype=str),
    )
    warmup = 1.0 - np.exp(
        -np.maximum(index["md_since"].to_numpy(dtype=float), 0.0) / 85.0
    )
    return OOFReplay(
        index=index,
        base_predictions=base,
        ridge_prediction=ridge,
        warmup_prediction=ridge * warmup,
        trainer_audit=trainer_audit,
        ridge_fold_audit=ridge_audit,
    )


def summarize_by_well(replay: OOFReplay) -> pd.DataFrame:
    """Return a compact wide RMSE artifact consumable by the simulator."""

    frame = replay.index[["well_id", "target"]].copy()
    frame["pred_anchor"] = 0.0
    for name in replay.base_predictions:
        frame[f"pred_{name}"] = replay.base_predictions[name].to_numpy(dtype=float)
    frame["pred_ridge"] = replay.ridge_prediction
    frame["pred_ridge_warmup_no_pf"] = replay.warmup_prediction
    prediction_columns = [column for column in frame if column.startswith("pred_")]
    rows: list[dict[str, float | int | str]] = []
    for well_id, part in frame.groupby("well_id", sort=True):
        row: dict[str, float | int | str] = {
            "well_id": well_id,
            "n_eval": len(part),
        }
        target = part["target"].to_numpy(dtype=float)
        for column in prediction_columns:
            error = part[column].to_numpy(dtype=float) - target
            row[f"rmse_{column.removeprefix('pred_')}"] = float(
                np.sqrt(np.mean(error**2))
            )
        rows.append(row)
    return pd.DataFrame(rows)


def contact_trajectory(
    horizontal: pd.DataFrame,
    typewell: pd.DataFrame,
    *,
    ref_col: str = "EGFDU",
    offset_target_col: str,
) -> np.ndarray:
    """Reproduce the public contact equation with an explicit offset source."""

    required_horizontal = {"Z", ref_col, offset_target_col}
    missing = required_horizontal.difference(horizontal.columns)
    if missing:
        raise ValueError(f"Horizontal frame lacks contact columns {sorted(missing)}")
    if not {"Geology", "TVT"}.issubset(typewell.columns):
        raise ValueError("Typewell frame lacks Geology/TVT")
    ref_values = pd.to_numeric(
        typewell.loc[typewell["Geology"].astype(str).eq(ref_col), "TVT"],
        errors="coerce",
    ).dropna()
    if ref_values.empty:
        raise ValueError(f"Typewell has no {ref_col} reference")
    raw = (
        float(ref_values.min())
        - horizontal["Z"].to_numpy(dtype=float)
        + horizontal[ref_col].to_numpy(dtype=float)
    )
    target = pd.to_numeric(horizontal[offset_target_col], errors="coerce").to_numpy(
        dtype=float
    )
    valid = np.isfinite(raw) & np.isfinite(target)
    if int(valid.sum()) < 50:
        raise ValueError(f"Only {int(valid.sum())} valid contact offset rows")
    return raw + float(np.mean(target[valid] - raw[valid]))


def contact_proxy_cv(train_dir: Path, *, ref_col: str = "EGFDU") -> pd.DataFrame:
    """Measure the tempting but non-deployable train-formation proxy score."""

    rows: list[dict[str, float | int | str]] = []
    for horizontal_path in sorted(train_dir.glob("*__horizontal_well.csv")):
        well_id = horizontal_path.name.removesuffix("__horizontal_well.csv")
        typewell_path = train_dir / f"{well_id}__typewell.csv"
        if not typewell_path.exists():
            continue
        horizontal = pd.read_csv(horizontal_path)
        typewell = pd.read_csv(typewell_path)
        eval_mask = horizontal["TVT_input"].isna().to_numpy()
        if not eval_mask.any():
            continue
        prediction = contact_trajectory(
            horizontal,
            typewell,
            ref_col=ref_col,
            offset_target_col="TVT_input",
        )
        target = horizontal["TVT"].to_numpy(dtype=float)[eval_mask]
        error = prediction[eval_mask] - target
        rows.append(
            {
                "well_id": well_id,
                "n_eval": len(error),
                "ref_col": ref_col,
                "sse": float(np.sum(error**2)),
                "rmse": float(np.sqrt(np.mean(error**2))),
            }
        )
    return pd.DataFrame(rows)


def reconstruct_contact_anchor(
    data_root: Path,
    anchor: pd.DataFrame,
    *,
    ref_col: str = "EGFDU",
) -> pd.DataFrame:
    """Reconstruct the scored anchor from overlapping train wells and full TVT."""

    anchor_map = dict(zip(anchor["id"].astype(str), anchor["tvt"].astype(float)))
    rows: list[dict[str, float | int | str]] = []
    for test_path in sorted((data_root / "test").glob("*__horizontal_well.csv")):
        well_id = test_path.name.removesuffix("__horizontal_well.csv")
        test = pd.read_csv(test_path)
        train = pd.read_csv(data_root / "train" / f"{well_id}__horizontal_well.csv")
        typewell = pd.read_csv(data_root / "train" / f"{well_id}__typewell.csv")
        trajectory = contact_trajectory(
            train,
            typewell,
            ref_col=ref_col,
            offset_target_col="TVT",
        )
        valid = np.isfinite(trajectory) & np.isfinite(train["MD"].to_numpy(dtype=float))
        order = np.argsort(train.loc[valid, "MD"].to_numpy(dtype=float))
        train_md = train.loc[valid, "MD"].to_numpy(dtype=float)[order]
        train_tvt = trajectory[valid][order]
        eval_mask = test["TVT_input"].isna().to_numpy()
        row_index = test.index[eval_mask].to_numpy(dtype=int)
        ids = [f"{well_id}_{row}" for row in row_index]
        prediction = np.interp(
            test.loc[eval_mask, "MD"].to_numpy(dtype=float), train_md, train_tvt
        )
        actual = np.asarray([anchor_map[row_id] for row_id in ids], dtype=float)
        difference = prediction - actual
        rows.append(
            {
                "well_id": well_id,
                "rows": len(ids),
                "rms_from_anchor": float(np.sqrt(np.mean(difference**2))),
                "max_abs_from_anchor": float(np.max(np.abs(difference))),
                "test_has_ref_col": ref_col in test.columns,
            }
        )
    return pd.DataFrame(rows)
