#!/usr/bin/env python3
"""Evaluate private-safe baselines at true and synthetic prediction starts."""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rogii.baselines import candidate_names, predict_suffix  # noqa: E402


def _well_id(path: Path) -> str:
    suffix = "__horizontal_well.csv"
    if not path.name.endswith(suffix):
        raise ValueError(path)
    return path.name[: -len(suffix)]


def _synthetic_boundaries(frame: pd.DataFrame, fractions: list[float]) -> list[tuple[str, int]]:
    true_boundary = int(np.flatnonzero(frame["TVT_input"].isna().to_numpy())[0])
    boundaries: list[tuple[str, int]] = []
    for fraction in fractions:
        boundary = int(round(true_boundary * fraction))
        boundary = min(max(boundary, 2), len(frame) - 1)
        boundaries.append((f"cut_{fraction:.2f}", boundary))
    return boundaries


def evaluate(
    train_dir: Path,
    *,
    fractions: list[float],
    limit: int | None = None,
) -> tuple[pd.DataFrame, dict[str, dict[str, float | int]]]:
    paths = sorted(train_dir.glob("*__horizontal_well.csv"))
    if limit is not None:
        paths = paths[:limit]
    if not paths:
        raise FileNotFoundError(f"No horizontal-well CSV files under {train_dir}")

    rows: list[dict[str, float | int | str]] = []
    pooled_sse: dict[tuple[str, str], float] = defaultdict(float)
    pooled_n: dict[tuple[str, str], int] = defaultdict(int)

    for number, path in enumerate(paths, start=1):
        frame = pd.read_csv(path)
        truth = frame["TVT"].to_numpy(dtype=float, copy=False)
        true_boundary = int(np.flatnonzero(frame["TVT_input"].isna().to_numpy())[0])
        starts = [("true_start", true_boundary)] + _synthetic_boundaries(frame, fractions)

        for start_name, boundary in starts:
            synthetic = start_name != "true_start"
            for candidate in candidate_names():
                indices, prediction = predict_suffix(
                    frame,
                    candidate,
                    cut_index=boundary if synthetic else None,
                )
                error = prediction - truth[indices]
                sse = float(np.dot(error, error))
                n_eval = int(len(indices))
                rmse = math.sqrt(sse / n_eval)
                key = (start_name, candidate)
                pooled_sse[key] += sse
                pooled_n[key] += n_eval
                rows.append(
                    {
                        "well_id": _well_id(path),
                        "start": start_name,
                        "candidate": candidate,
                        "boundary": boundary,
                        "n_rows": len(frame),
                        "n_eval": n_eval,
                        "eval_fraction": n_eval / len(frame),
                        "z_span": float(np.ptp(frame["Z"].to_numpy()[indices])),
                        "rmse": rmse,
                        "sse": sse,
                    }
                )
        if number % 100 == 0 or number == len(paths):
            print(f"evaluated {number}/{len(paths)} wells", flush=True)

    detail = pd.DataFrame(rows)
    summary: dict[str, dict[str, float | int]] = {}
    for (start_name, candidate), group in detail.groupby(["start", "candidate"], sort=True):
        key = f"{start_name}/{candidate}"
        n = pooled_n[(start_name, candidate)]
        summary[key] = {
            "wells": int(len(group)),
            "rows": int(n),
            "pooled_rmse": math.sqrt(pooled_sse[(start_name, candidate)] / n),
            "macro_rmse": float(group["rmse"].mean()),
            "median_rmse": float(group["rmse"].median()),
            "p90_rmse": float(group["rmse"].quantile(0.90)),
            "p95_rmse": float(group["rmse"].quantile(0.95)),
            "worst_rmse": float(group["rmse"].max()),
        }
    return detail, summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--train-dir",
        type=Path,
        default=REPO_ROOT / "data" / "raw" / "competition" / "train",
    )
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "artifacts" / "cv")
    parser.add_argument("--fractions", type=float, nargs="*", default=[0.4, 0.6, 0.8])
    parser.add_argument("--limit", type=int)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if any(not 0.0 < value < 1.0 for value in args.fractions):
        raise ValueError("Every synthetic cut fraction must be between zero and one")
    detail, summary = evaluate(args.train_dir, fractions=args.fractions, limit=args.limit)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    detail.to_csv(args.output_dir / "baseline_detail.csv", index=False)
    (args.output_dir / "baseline_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    table = pd.DataFrame.from_dict(summary, orient="index").sort_values(
        ["pooled_rmse", "p95_rmse"]
    )
    print(table.to_string(float_format=lambda value: f"{value:.4f}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
