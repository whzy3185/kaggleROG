"""Leak-aware local score simulation for ROGII well-level CV artifacts.

The public and private leaderboard slices are collections of complete wells.
Consequently, uncertainty must be estimated by resampling wells rather than
individual rows.  This module normalizes the repository's historical CV
artifacts to one row per ``(package, candidate, well)`` and provides paired
well-bootstrap summaries.

The simulator estimates a distribution of scores on a new well sample.  It
does not claim to recover the undisclosed Kaggle split or convert arbitrary CV
scores to leaderboard scores.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd


TIDY_COLUMNS = (
    "package",
    "candidate",
    "well_id",
    "n_eval",
    "sse",
    "validation_scope",
)


def _well_id(path: Path) -> str:
    return path.name.removesuffix("__horizontal_well.csv")


def _deterministic_kmeans(xy: np.ndarray, *, k: int, seed: int) -> np.ndarray:
    """Small dependency-free k-means used only to define diagnostic fields."""

    xy = np.asarray(xy, dtype=float)
    if xy.ndim != 2 or xy.shape[1] != 2:
        raise ValueError("xy must have shape (n_wells, 2)")
    if not 1 <= k <= len(xy):
        raise ValueError("k must be between one and the number of wells")
    z = (xy - xy.mean(axis=0)) / (xy.std(axis=0) + 1e-12)
    rng = np.random.default_rng(seed)
    centers = z[rng.choice(len(z), size=k, replace=False)].copy()
    labels = np.full(len(z), -1, dtype=int)
    for _ in range(100):
        distances = ((z[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        updated = distances.argmin(axis=1)
        if np.array_equal(updated, labels):
            break
        labels = updated
        for field in range(k):
            members = z[labels == field]
            if len(members):
                centers[field] = members.mean(axis=0)
    return labels


def load_well_metadata(
    train_dir: Path,
    *,
    field_count: int = 5,
    field_seed: int = 0,
) -> pd.DataFrame:
    """Read target-row counts and spatial centroids for every training well."""

    rows: list[dict[str, float | int | str]] = []
    for path in sorted(train_dir.glob("*__horizontal_well.csv")):
        frame = pd.read_csv(path, usecols=["X", "Y", "TVT_input"])
        n_eval = int(frame["TVT_input"].isna().sum())
        if n_eval <= 0:
            continue
        rows.append(
            {
                "well_id": _well_id(path),
                "n_eval_truth": n_eval,
                "x": float(pd.to_numeric(frame["X"], errors="coerce").median()),
                "y": float(pd.to_numeric(frame["Y"], errors="coerce").median()),
            }
        )
    metadata = pd.DataFrame(rows)
    if metadata.empty:
        raise FileNotFoundError(f"No usable horizontal wells under {train_dir}")
    if not np.isfinite(metadata[["x", "y"]].to_numpy(dtype=float)).all():
        raise ValueError("Well centroids contain non-finite coordinates")
    metadata["field"] = _deterministic_kmeans(
        metadata[["x", "y"]].to_numpy(dtype=float),
        k=min(field_count, len(metadata)),
        seed=field_seed,
    )
    return metadata


def _finalize_tidy(frame: pd.DataFrame, metadata: pd.DataFrame) -> pd.DataFrame:
    missing = set(TIDY_COLUMNS).difference(frame.columns)
    if missing:
        raise ValueError(f"Normalized CV frame is missing {sorted(missing)}")
    out = frame.loc[:, TIDY_COLUMNS].copy()
    out["well_id"] = out["well_id"].astype(str)
    out["n_eval"] = pd.to_numeric(out["n_eval"], errors="raise").astype(int)
    out["sse"] = pd.to_numeric(out["sse"], errors="raise").astype(float)
    if (out["n_eval"] <= 0).any() or (out["sse"] < 0).any():
        raise ValueError("CV rows require positive n_eval and non-negative SSE")
    if not np.isfinite(out[["n_eval", "sse"]].to_numpy(dtype=float)).all():
        raise ValueError("CV rows contain non-finite values")
    if out.duplicated(["package", "candidate", "well_id"]).any():
        raise ValueError("CV artifact contains duplicate package/candidate/well rows")
    out = out.merge(metadata[["well_id", "field"]], on="well_id", how="left", validate="many_to_one")
    if out["field"].isna().any():
        missing_wells = sorted(out.loc[out["field"].isna(), "well_id"].unique())
        raise ValueError(f"CV artifact references unknown wells: {missing_wells[:5]}")
    out["field"] = out["field"].astype(int)
    return out


def load_baseline_package(path: Path, metadata: pd.DataFrame) -> pd.DataFrame:
    raw = pd.read_csv(path)
    raw = raw.loc[raw["start"].eq("true_start")].copy()
    raw["package"] = "baseline_true_start"
    raw["validation_scope"] = "all-well target-safe replay"
    return _finalize_tidy(raw, metadata)


def _load_wide_rmse_package(
    path: Path,
    metadata: pd.DataFrame,
    *,
    package: str,
    validation_scope: str,
) -> pd.DataFrame:
    raw = pd.read_csv(path)
    candidates = [column.removeprefix("rmse_") for column in raw.columns if column.startswith("rmse_")]
    rows: list[pd.DataFrame] = []
    for candidate in candidates:
        part = raw[["well_id", "n_eval", f"rmse_{candidate}"]].copy()
        part["candidate"] = candidate
        part["sse"] = part[f"rmse_{candidate}"] ** 2 * part["n_eval"]
        part["package"] = package
        part["validation_scope"] = validation_scope
        rows.append(part)
    if not rows:
        raise ValueError(f"No rmse_* candidates found in {path}")
    return _finalize_tidy(pd.concat(rows, ignore_index=True), metadata)


def load_particle_package(path: Path, metadata: pd.DataFrame) -> pd.DataFrame:
    return _load_wide_rmse_package(
        path,
        metadata,
        package="independent_particle_30w",
        validation_scope="30-well target-safe exploratory replay",
    )


def load_particle_full_package(path: Path, metadata: pd.DataFrame) -> pd.DataFrame:
    return _load_wide_rmse_package(
        path,
        metadata,
        package="independent_particle_400p16s_t5_773w",
        validation_scope="773-well target-safe replay at 400 particles, 16 seeds, temperature 5",
    )


def load_particle_historical_package(path: Path, metadata: pd.DataFrame) -> pd.DataFrame:
    return _load_wide_rmse_package(
        path,
        metadata,
        package="historical_particle_300p8s_t20_773w",
        validation_scope="exact 773-well replay of the submitted 300-particle, 8-seed, temperature-20 package",
    )


def load_sequence_package(path: Path, metadata: pd.DataFrame) -> pd.DataFrame:
    return _load_wide_rmse_package(
        path,
        metadata,
        package="first_order_hmm_5w",
        validation_scope="5-well target-safe smoke test",
    )


def load_neighbor_package(
    path: Path,
    metadata: pd.DataFrame,
    baseline_path: Path,
) -> pd.DataFrame:
    return _load_neighbor_variant(
        path,
        metadata,
        baseline_path,
        package="neighbor_profile_loo",
        validation_scope="leave-one-well-out; donors not excluded by field",
    )


def load_neighbor_field_package(
    path: Path,
    metadata: pd.DataFrame,
    baseline_path: Path,
) -> pd.DataFrame:
    return _load_neighbor_variant(
        path,
        metadata,
        baseline_path,
        package="neighbor_profile_field_holdout",
        validation_scope="5-way spatial field holdout; all same-field donors excluded",
    )


def _load_neighbor_variant(
    path: Path,
    metadata: pd.DataFrame,
    baseline_path: Path,
    *,
    package: str,
    validation_scope: str,
) -> pd.DataFrame:
    raw = pd.read_csv(path)
    raw["candidate"] = raw.apply(
        lambda row: f"distance_{float(row['threshold']):g}_blend_{float(row['blend']):g}",
        axis=1,
    )
    raw["package"] = package
    raw["validation_scope"] = validation_scope
    parts = [raw]

    baseline = pd.read_csv(baseline_path)
    baseline = baseline.loc[
        baseline["start"].eq("true_start") & baseline["candidate"].eq("anchor"),
        ["well_id", "n_eval", "sse"],
    ].copy()
    baseline["candidate"] = "anchor"
    baseline["package"] = package
    baseline["validation_scope"] = f"{validation_scope} control"
    parts.append(baseline)
    return _finalize_tidy(pd.concat(parts, ignore_index=True), metadata)


def load_gbdt_gate_package(path: Path, metadata: pd.DataFrame) -> pd.DataFrame:
    raw = pd.read_csv(path).rename(columns={"well": "well_id"})
    raw = raw.merge(
        metadata[["well_id", "n_eval_truth"]],
        on="well_id",
        how="left",
        validate="one_to_one",
    )
    rows: list[pd.DataFrame] = []
    for candidate in ("baseline", "corrected"):
        part = raw[["well_id", "n_eval_truth", f"{candidate}_rmse"]].copy()
        part = part.rename(columns={"n_eval_truth": "n_eval"})
        part["candidate"] = candidate
        part["sse"] = part[f"{candidate}_rmse"] ** 2 * part["n_eval"]
        part["package"] = "blacklions_gbdt_gate_oof"
        part["validation_scope"] = "reported 773-well OOF; source gate audit"
        rows.append(part)
    return _finalize_tidy(pd.concat(rows, ignore_index=True), metadata)


def pooled_rmse(frame: pd.DataFrame) -> float:
    return math.sqrt(float(frame["sse"].sum()) / int(frame["n_eval"].sum()))


def _bootstrap_scores(
    candidate: pd.DataFrame,
    reference: pd.DataFrame,
    *,
    sample_wells: int,
    iterations: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    paired = candidate[["well_id", "n_eval", "sse"]].merge(
        reference[["well_id", "n_eval", "sse"]],
        on="well_id",
        suffixes=("_candidate", "_reference"),
        validate="one_to_one",
    )
    if not np.array_equal(paired["n_eval_candidate"], paired["n_eval_reference"]):
        raise ValueError("Candidate and reference row counts differ")
    rng = np.random.default_rng(seed)
    n_wells = len(paired)
    candidate_scores = np.empty(iterations, dtype=float)
    deltas = np.empty(iterations, dtype=float)
    batch = 256
    n_eval = paired["n_eval_candidate"].to_numpy(dtype=float)
    sse_candidate = paired["sse_candidate"].to_numpy(dtype=float)
    sse_reference = paired["sse_reference"].to_numpy(dtype=float)
    for start in range(0, iterations, batch):
        stop = min(start + batch, iterations)
        draw = rng.integers(0, n_wells, size=(stop - start, sample_wells))
        denominators = n_eval[draw].sum(axis=1)
        candidate_batch = np.sqrt(sse_candidate[draw].sum(axis=1) / denominators)
        reference_batch = np.sqrt(sse_reference[draw].sum(axis=1) / denominators)
        candidate_scores[start:stop] = candidate_batch
        deltas[start:stop] = candidate_batch - reference_batch
    return candidate_scores, deltas


def _evidence_grade(wells: int) -> str:
    if wells >= 500:
        return "strong"
    if wells >= 100:
        return "partial"
    if wells >= 30:
        return "exploratory"
    return "smoke"


def analyze_package(
    frame: pd.DataFrame,
    *,
    reference_candidate: str,
    public_wells: int = 52,
    private_wells: int = 148,
    iterations: int = 10_000,
    seed: int = 20260801,
) -> pd.DataFrame:
    """Return deterministic metrics and paired well-bootstrap intervals."""

    packages = frame["package"].unique()
    if len(packages) != 1:
        raise ValueError("analyze_package expects exactly one package")
    reference = frame.loc[frame["candidate"].eq(reference_candidate)].copy()
    if reference.empty:
        raise ValueError(f"Reference candidate {reference_candidate!r} is absent")
    rows: list[dict[str, float | int | str]] = []
    for number, (candidate_name, candidate) in enumerate(frame.groupby("candidate", sort=True)):
        common = candidate["well_id"].isin(reference["well_id"])
        candidate = candidate.loc[common].copy()
        ref = reference.loc[reference["well_id"].isin(candidate["well_id"])].copy()
        candidate = candidate.sort_values("well_id")
        ref = ref.sort_values("well_id")
        if not candidate["well_id"].reset_index(drop=True).equals(ref["well_id"].reset_index(drop=True)):
            raise ValueError("Candidate/reference well alignment failed")

        score = pooled_rmse(candidate)
        ref_score = pooled_rmse(ref)
        public_scores, public_delta = _bootstrap_scores(
            candidate,
            ref,
            sample_wells=public_wells,
            iterations=iterations,
            seed=seed + number * 17,
        )
        private_scores, private_delta = _bootstrap_scores(
            candidate,
            ref,
            sample_wells=private_wells,
            iterations=iterations,
            seed=seed + number * 17 + 1,
        )
        field_scores = [pooled_rmse(group) for _, group in candidate.groupby("field")]
        rmse_well = np.sqrt(candidate["sse"].to_numpy() / candidate["n_eval"].to_numpy())
        grade = _evidence_grade(len(candidate))
        delta_q95 = float(np.quantile(private_delta, 0.95))
        delta_q05 = float(np.quantile(private_delta, 0.05))
        delta = score - ref_score
        if candidate_name == reference_candidate:
            verdict = "control"
        elif delta_q05 > 0:
            verdict = "rejected"
        elif grade == "strong" and delta <= -0.10 and delta_q95 < 0:
            verdict = "locally_supported"
        elif delta < -1e-9:
            verdict = "promising_but_inconclusive"
        else:
            verdict = "inconclusive"
        rows.append(
            {
                "package": packages[0],
                "candidate": candidate_name,
                "reference": reference_candidate,
                "validation_scope": candidate["validation_scope"].iloc[0],
                "wells": len(candidate),
                "rows": int(candidate["n_eval"].sum()),
                "evidence_grade": grade,
                "pooled_rmse": score,
                "delta_vs_reference": delta,
                "well_win_rate": float(
                    (
                        candidate["sse"].to_numpy() / candidate["n_eval"].to_numpy()
                        < ref["sse"].to_numpy() / ref["n_eval"].to_numpy()
                    ).mean()
                ),
                "macro_rmse": float(rmse_well.mean()),
                "p90_rmse": float(np.quantile(rmse_well, 0.90)),
                "p95_rmse": float(np.quantile(rmse_well, 0.95)),
                "worst_rmse": float(rmse_well.max()),
                "target_field_mean_rmse": float(np.mean(field_scores)),
                "target_field_worst_rmse": float(np.max(field_scores)),
                "public52_median": float(np.median(public_scores)),
                "public52_q05": float(np.quantile(public_scores, 0.05)),
                "public52_q95": float(np.quantile(public_scores, 0.95)),
                "public52_delta_q05": float(np.quantile(public_delta, 0.05)),
                "public52_delta_q95": float(np.quantile(public_delta, 0.95)),
                "private148_median": float(np.median(private_scores)),
                "private148_q05": float(np.quantile(private_scores, 0.05)),
                "private148_q95": float(np.quantile(private_scores, 0.95)),
                "private148_delta_q05": delta_q05,
                "private148_delta_q95": delta_q95,
                "private148_p_improve": float((private_delta < 0).mean()),
                "verdict": verdict,
            }
        )
    return pd.DataFrame(rows)
