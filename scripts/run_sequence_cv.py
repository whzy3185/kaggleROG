#!/usr/bin/env python3
"""Backtest the independent GR-HMM candidate on a deterministic well sample."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rogii.baselines import predict_suffix  # noqa: E402
from rogii.sequence import HMMConfig, predict_gr_hmm  # noqa: E402


def _well_id(path: Path) -> str:
    return path.name.removesuffix("__horizontal_well.csv")


def evaluate(
    train_dir: Path,
    *,
    sample_size: int,
    seed: int,
    config: HMMConfig,
) -> tuple[pd.DataFrame, dict[str, object]]:
    paths = sorted(train_dir.glob("*__horizontal_well.csv"))
    if sample_size < len(paths):
        paths = list(np.random.default_rng(seed).choice(paths, size=sample_size, replace=False))
        paths.sort()
    rows: list[dict[str, float | int | str]] = []
    pooled: dict[str, list[float]] = {
        name: [0.0, 0.0]
        for name in ("anchor", "hmm", "blend_25_hmm", "blend_50_hmm", "blend_75_hmm")
    }

    for number, path in enumerate(paths, start=1):
        well_id = _well_id(path)
        frame = pd.read_csv(path)
        typewell = pd.read_csv(path.with_name(f"{well_id}__typewell.csv"))
        indices, anchor = predict_suffix(frame, "anchor")
        hmm_indices, hmm, posterior_std, diagnostics = predict_gr_hmm(
            frame, typewell, config=config
        )
        if not np.array_equal(indices, hmm_indices):
            raise AssertionError("Candidate row alignment mismatch")
        truth = frame["TVT"].to_numpy(dtype=float, copy=False)[indices]
        candidates = {
            "anchor": anchor,
            "hmm": hmm,
            "blend_25_hmm": 0.75 * anchor + 0.25 * hmm,
            "blend_50_hmm": 0.50 * anchor + 0.50 * hmm,
            "blend_75_hmm": 0.25 * anchor + 0.75 * hmm,
        }
        record: dict[str, float | int | str] = {
            "well_id": well_id,
            "n_eval": len(indices),
            "gr_gain": diagnostics.gr_gain,
            "gr_offset": diagnostics.gr_offset,
            "gr_sigma": diagnostics.gr_sigma,
            "drift": diagnostics.drift,
            "posterior_std": float(posterior_std.mean()),
            "max_edge_mass": diagnostics.max_edge_mass,
        }
        for name, prediction in candidates.items():
            error = prediction - truth
            sse = float(np.dot(error, error))
            record[f"rmse_{name}"] = math.sqrt(sse / len(error))
            pooled[name][0] += sse
            pooled[name][1] += len(error)
        rows.append(record)
        print(
            f"{number:03d}/{len(paths)} {well_id} "
            f"anchor={record['rmse_anchor']:.3f} hmm={record['rmse_hmm']:.3f}",
            flush=True,
        )

    detail = pd.DataFrame(rows)
    scores = {name: math.sqrt(sse / count) for name, (sse, count) in pooled.items()}
    summary: dict[str, object] = {
        "sample_size": len(paths),
        "seed": seed,
        "config": config.__dict__,
        "pooled_rmse": scores,
        "well_win_rate_vs_anchor": float((detail["rmse_hmm"] < detail["rmse_anchor"]).mean()),
    }
    return detail, summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--train-dir",
        type=Path,
        default=REPO_ROOT / "data" / "raw" / "competition" / "train",
    )
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "artifacts" / "sequence_cv")
    parser.add_argument("--sample-size", type=int, default=30)
    parser.add_argument("--seed", type=int, default=20260717)
    parser.add_argument("--step", type=float, default=0.5)
    parser.add_argument("--half-width", type=float, default=140.0)
    parser.add_argument("--position-sigma", type=float, default=0.32)
    parser.add_argument("--emission-scale", type=float, default=1.0)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = HMMConfig(
        step=args.step,
        half_width=args.half_width,
        position_sigma=args.position_sigma,
        emission_scale=args.emission_scale,
    )
    detail, summary = evaluate(
        args.train_dir,
        sample_size=args.sample_size,
        seed=args.seed,
        config=config,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    detail.to_csv(args.output_dir / "sequence_detail.csv", index=False)
    (args.output_dir / "sequence_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
