#!/usr/bin/env python3
"""Connect the public GeoAnchor learned OOF core to the local score simulator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rogii.geoanchor_oof import replay_geoanchor_oof, summarize_by_well  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--train-dir",
        type=Path,
        default=REPO_ROOT / "data" / "raw" / "competition" / "train",
    )
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=REPO_ROOT / "artifacts" / "ridge_artifacts_download",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "artifacts" / "geoanchor_learned_oof_20260801",
    )
    args = parser.parse_args()

    replay = replay_geoanchor_oof(args.train_dir, args.artifact_root)
    detail = summarize_by_well(replay)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    detail.to_csv(args.output_dir / "geoanchor_learned_oof_detail.csv", index=False)
    replay.trainer_audit.to_csv(args.output_dir / "trainer_alignment.csv", index=False)
    replay.ridge_fold_audit.to_csv(args.output_dir / "ridge_fold_audit.csv", index=False)

    rows = len(replay.index)
    y = replay.index["target"].to_numpy(dtype=float)
    ridge_rmse = float(np.sqrt(np.mean((replay.ridge_prediction - y) ** 2)))
    warmup_rmse = float(np.sqrt(np.mean((replay.warmup_prediction - y) ** 2)))
    summary = {
        "rows": rows,
        "wells": int(replay.index["well_id"].nunique()),
        "all_trainers_aligned": bool(replay.trainer_audit["aligned"].all()),
        "max_abs_trainer_score_delta": float(replay.trainer_audit["delta"].abs().max()),
        "ridge_group_oof_rmse": ridge_rmse,
        "ridge_warmup_no_pf_rmse": warmup_rmse,
        "public_notebook_pp_pf_weight_not_replayed": 0.09,
        "locally_scored_layers": [
            "five saved base-model OOF vectors",
            "five-fold grouped positive Ridge",
            "85-ft distance warm-up without the unavailable saved PF feature",
        ],
        "not_locally_scored_layers": [
            "PF 0.09 blend from the 7.4 GB saved feature table",
            "selector/projection/visible-prefix transactions",
            "guarded same-well contact override",
            "leaderboard-derived R2000 single-test-well correction",
        ],
        "leaderboard_score_estimate": None,
    }
    (args.output_dir / "audit.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
