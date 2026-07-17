#!/usr/bin/env python3
"""Fit a one-parameter prefix-trend shrinkage and build a safe submission."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]


def _boundary(values: pd.Series) -> int:
    observed = values.notna().to_numpy()
    missing = np.flatnonzero(~observed)
    if not len(missing) or missing[0] < 2 or observed[missing[0] :].any():
        raise ValueError("TVT_input must have at least two visible rows and one missing suffix")
    return int(missing[0])


def _tail_slope(md: np.ndarray, tvt: np.ndarray, boundary: int, window: int) -> float:
    x = md[max(0, boundary - window) : boundary]
    y = tvt[max(0, boundary - window) : boundary]
    centered = x - x.mean()
    denominator = float(np.dot(centered, centered))
    slope = 0.0 if denominator <= 1e-12 else float(np.dot(centered, y - y.mean()) / denominator)
    return float(np.clip(slope, -0.1, 0.1))


def fit_shrinkage(train_dir: Path, *, window: int = 30, folds: int = 5) -> dict[str, object]:
    rows: list[dict[str, float | int | str]] = []
    for path in sorted(train_dir.glob("*__horizontal_well.csv")):
        frame = pd.read_csv(path, usecols=["MD", "TVT", "TVT_input"])
        boundary = _boundary(frame["TVT_input"])
        md = frame["MD"].to_numpy(dtype=float, copy=False)
        truth = frame["TVT"].to_numpy(dtype=float, copy=False)
        anchor = float(frame.loc[boundary - 1, "TVT_input"])
        base_error = anchor - truth[boundary:]
        slope = _tail_slope(md, truth, boundary, window)
        raw_adjustment = slope * (md[boundary:] - md[boundary - 1])
        rows.append(
            {
                "well_id": path.name.removesuffix("__horizontal_well.csv"),
                "a": float(np.dot(raw_adjustment, raw_adjustment)),
                "b": float(np.dot(base_error, raw_adjustment)),
                "c": float(np.dot(base_error, base_error)),
                "n": len(base_error),
            }
        )
    if not rows:
        raise FileNotFoundError(f"No training wells under {train_dir}")

    stats = pd.DataFrame(rows)
    stats["fold"] = np.arange(len(stats)) % folds
    oof_sse = 0.0
    fold_alphas: list[float] = []
    for fold in range(folds):
        training = stats["fold"] != fold
        validation = ~training
        denominator = float(stats.loc[training, "a"].sum())
        alpha = 0.0 if denominator <= 1e-12 else float(
            np.clip(-stats.loc[training, "b"].sum() / denominator, 0.0, 1.0)
        )
        fold_alphas.append(alpha)
        group = stats.loc[validation]
        oof_sse += float((group["c"] + 2 * alpha * group["b"] + alpha**2 * group["a"]).sum())

    denominator = float(stats["a"].sum())
    alpha = 0.0 if denominator <= 1e-12 else float(
        np.clip(-stats["b"].sum() / denominator, 0.0, 1.0)
    )
    n_rows = int(stats["n"].sum())
    anchor_rmse = math.sqrt(float(stats["c"].sum()) / n_rows)
    fitted_sse = float((stats["c"] + 2 * alpha * stats["b"] + alpha**2 * stats["a"]).sum())
    return {
        "alpha": alpha,
        "window": window,
        "folds": folds,
        "fold_alphas": fold_alphas,
        "wells": len(stats),
        "rows": n_rows,
        "anchor_pooled_rmse": anchor_rmse,
        "oof_trend_pooled_rmse": math.sqrt(oof_sse / n_rows),
        "full_fit_trend_pooled_rmse": math.sqrt(fitted_sse / n_rows),
    }


def build_trend_submission(
    data_dir: Path,
    output_path: Path,
    *,
    alpha: float,
    window: int,
) -> pd.DataFrame:
    sample = pd.read_csv(data_dir / "sample_submission.csv")
    if list(sample.columns) != ["id", "tvt"]:
        raise ValueError(f"Unexpected sample columns: {list(sample.columns)!r}")
    prediction_by_id: dict[str, float] = {}
    for path in sorted((data_dir / "test").glob("*__horizontal_well.csv")):
        well_id = path.name.removesuffix("__horizontal_well.csv")
        frame = pd.read_csv(path, usecols=["MD", "TVT_input"])
        boundary = _boundary(frame["TVT_input"])
        md = frame["MD"].to_numpy(dtype=float, copy=False)
        prefix_tvt = frame["TVT_input"].to_numpy(dtype=float, copy=False)
        anchor = float(prefix_tvt[boundary - 1])
        slope = _tail_slope(md, prefix_tvt, boundary, window)
        indices = np.arange(boundary, len(frame), dtype=int)
        prediction = anchor + alpha * slope * (md[indices] - md[boundary - 1])
        prediction_by_id.update(
            {f"{well_id}_{index}": float(value) for index, value in zip(indices, prediction)}
        )

    sample_ids = sample["id"].astype(str)
    if set(prediction_by_id) != set(sample_ids):
        raise ValueError("Prediction IDs do not exactly match sample IDs")
    submission = pd.DataFrame(
        {"id": sample_ids, "tvt": sample_ids.map(prediction_by_id).astype(float)}
    )
    if not np.isfinite(submission["tvt"]).all():
        raise ValueError("Submission contains non-finite values")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    submission.to_csv(output_path, index=False)
    return submission


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir", type=Path, default=REPO_ROOT / "data" / "raw" / "competition"
    )
    parser.add_argument(
        "--output", type=Path, default=REPO_ROOT / "outputs" / "submission_trend.csv"
    )
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--folds", type=int, default=5)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = fit_shrinkage(args.data_dir / "train", window=args.window, folds=args.folds)
    submission = build_trend_submission(
        args.data_dir,
        args.output,
        alpha=float(summary["alpha"]),
        window=args.window,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"wrote {args.output} with {len(submission)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
