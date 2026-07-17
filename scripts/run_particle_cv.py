#!/usr/bin/env python3
"""Backtest the independent particle ensemble on a deterministic well sample."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rogii.baselines import predict_suffix  # noqa: E402
from rogii.particle import ParticleConfig, predict_particle_ensemble  # noqa: E402


def _evaluate_one(
    path: Path,
    *,
    number: int,
    seed: int,
    config: ParticleConfig,
) -> tuple[int, dict[str, float | int | str]]:
    well_id = path.name.removesuffix("__horizontal_well.csv")
    frame = pd.read_csv(path)
    typewell = pd.read_csv(path.with_name(f"{well_id}__typewell.csv"))
    indices, anchor = predict_suffix(frame, "anchor")
    particle_indices, particle, diagnostics = predict_particle_ensemble(
        frame,
        typewell,
        config=config,
        seed_base=seed + number * 1000,
    )
    if not np.array_equal(indices, particle_indices):
        raise AssertionError("Candidate row alignment mismatch")
    truth = frame["TVT"].to_numpy(dtype=float, copy=False)[indices]
    candidates = {
        "anchor": anchor,
        "particle": particle,
        "blend50": 0.5 * anchor + 0.5 * particle,
        "blend65": 0.35 * anchor + 0.65 * particle,
        "blend75": 0.25 * anchor + 0.75 * particle,
    }
    record: dict[str, float | int | str] = {
        "well_id": well_id,
        "n_eval": len(indices),
        "gr_sigma": diagnostics.gr_sigma,
        "initial_rate": diagnostics.initial_rate,
        "effective_seeds": diagnostics.effective_seed_count,
        "best_seed_weight": diagnostics.best_seed_weight,
    }
    for name, prediction in candidates.items():
        error = prediction - truth
        sse = float(np.dot(error, error))
        record[f"sse_{name}"] = sse
        record[f"rmse_{name}"] = math.sqrt(sse / len(error))
    return number, record


def evaluate(
    train_dir: Path,
    *,
    sample_size: int,
    seed: int,
    config: ParticleConfig,
    jobs: int = 1,
) -> tuple[pd.DataFrame, dict[str, object]]:
    paths = sorted(train_dir.glob("*__horizontal_well.csv"))
    if sample_size < len(paths):
        paths = sorted(np.random.default_rng(seed).choice(paths, size=sample_size, replace=False))
    names = ("anchor", "particle", "blend50", "blend65", "blend75")
    started = time.perf_counter()
    tasks = [
        delayed(_evaluate_one)(path, number=number, seed=seed, config=config)
        for number, path in enumerate(paths, start=1)
    ]
    outputs = Parallel(n_jobs=jobs, verbose=5 if jobs != 1 else 0)(tasks)
    outputs.sort(key=lambda item: item[0])
    rows = [record for _, record in outputs]
    for number, record in outputs:
        print(
            f"{number:03d}/{len(paths)} {record['well_id']} anchor={record['rmse_anchor']:.3f} "
            f"particle={record['rmse_particle']:.3f}",
            flush=True,
        )
    detail = pd.DataFrame(rows)
    total_rows = int(detail["n_eval"].sum())
    summary: dict[str, object] = {
        "sample_size": len(paths),
        "seed": seed,
        "jobs": jobs,
        "seconds": time.perf_counter() - started,
        "config": config.__dict__,
        "pooled_rmse": {
            name: math.sqrt(float(detail[f"sse_{name}"].sum()) / total_rows) for name in names
        },
        "well_win_rate_vs_anchor": float(
            (detail["rmse_particle"] < detail["rmse_anchor"]).mean()
        ),
    }
    return detail, summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--train-dir",
        type=Path,
        default=REPO_ROOT / "data" / "raw" / "competition" / "train",
    )
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "artifacts" / "particle_cv")
    parser.add_argument("--sample-size", type=int, default=30)
    parser.add_argument("--seed", type=int, default=20260717)
    parser.add_argument("--particles", type=int, default=400)
    parser.add_argument("--seeds", type=int, default=16)
    parser.add_argument("--temperature", type=float, default=5.0)
    parser.add_argument("--jobs", type=int, default=1)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = ParticleConfig(
        particles=args.particles,
        seeds=args.seeds,
        likelihood_temperature=args.temperature,
    )
    detail, summary = evaluate(
        args.train_dir,
        sample_size=args.sample_size,
        seed=args.seed,
        config=config,
        jobs=args.jobs,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    detail.to_csv(args.output_dir / "particle_detail.csv", index=False)
    (args.output_dir / "particle_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
