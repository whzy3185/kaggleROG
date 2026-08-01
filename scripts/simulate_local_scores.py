#!/usr/bin/env python3
"""Simulate public/private well-sample score distributions from historical CV."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rogii.local_score import (  # noqa: E402
    analyze_package,
    load_baseline_package,
    load_gbdt_gate_package,
    load_neighbor_field_package,
    load_neighbor_package,
    load_particle_package,
    load_particle_full_package,
    load_particle_historical_package,
    load_sequence_package,
    load_well_metadata,
)
from verify_submission import validate_submission  # noqa: E402


D29_SCORES = {
    "a27_exact": (55072903, 6.541),
    "a27_q0261": (55073402, 6.517),
    "a27_qneg0261": (55073985, 6.560),
    "a27_nonbranch_r1": (55074584, 6.455),
    "a27_boundary_r1": (55075184, 6.530),
}


def audit_prior_d29_packages() -> pd.DataFrame:
    """Recheck real historical submission files without pretending to score them."""

    root = REPO_ROOT / "artifacts" / "d29_private_runs"
    recorded = json.loads((root / "audit.json").read_text(encoding="utf-8"))
    audit_by_route = {row["route"]: row for row in recorded["routes"]}
    sample = REPO_ROOT / "data" / "raw" / "competition" / "sample_submission.csv"
    rows: list[dict[str, float | int | str | bool]] = []
    for route, (submission_ref, public_lb) in D29_SCORES.items():
        path = root / route / "submission.csv"
        contract = validate_submission(sample, path)
        actual_sha = hashlib.sha256(path.read_bytes()).hexdigest()
        prior = audit_by_route[route]
        fatal_markers = prior.get("fatal_log_markers", [])
        rows.append(
            {
                "route": route,
                "submission_ref": submission_ref,
                "public_lb": public_lb,
                "rows": int(contract["rows"]),
                "ordered_unique_finite": True,
                "file_sha256": actual_sha,
                "sha_matches_record": actual_sha == prior["file_sha256"],
                "fatal_log_marker_count": len(fatal_markers),
                "rms_from_d25_a27_ft": float(prior["rms_from_d25_a27_ft"]),
                "score_delta_vs_d25_6p469": public_lb - 6.469,
                "locally_scoreable_from_submission_csv": False,
            }
        )
    result = pd.DataFrame(rows).sort_values("submission_ref").reset_index(drop=True)
    if not result["sha_matches_record"].all() or not result["ordered_unique_finite"].all():
        raise RuntimeError("A historical D29 package failed its immutable output contract")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--train-dir",
        type=Path,
        default=REPO_ROOT / "data" / "raw" / "competition" / "train",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "artifacts" / "local_score_simulation_20260801",
    )
    parser.add_argument("--iterations", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260801)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.iterations < 100:
        raise ValueError("iterations must be at least 100")
    metadata = load_well_metadata(args.train_dir)
    baseline_path = REPO_ROOT / "artifacts" / "cv" / "baseline_detail.csv"
    packages = [
        (
            load_baseline_package(baseline_path, metadata),
            "anchor",
        ),
        (
            load_particle_package(
                REPO_ROOT / "artifacts" / "particle_cv" / "particle_detail.csv",
                metadata,
            ),
            "anchor",
        ),
        (
            load_sequence_package(
                REPO_ROOT / "artifacts" / "sequence_cv" / "sequence_detail.csv",
                metadata,
            ),
            "anchor",
        ),
        (
            load_neighbor_package(
                REPO_ROOT / "artifacts" / "neighbor_profile_cv" / "neighbor_profile_detail.csv",
                metadata,
                baseline_path,
            ),
            "anchor",
        ),
        (
            load_neighbor_field_package(
                REPO_ROOT
                / "artifacts"
                / "neighbor_profile_field_holdout_cv_20260801"
                / "neighbor_profile_detail.csv",
                metadata,
                baseline_path,
            ),
            "anchor",
        ),
        (
            load_gbdt_gate_package(
                REPO_ROOT
                / "artifacts"
                / "d32_public_outputs"
                / "gbdt_gate"
                / "all_valid_gbdt_oof_by_well.csv",
                metadata,
            ),
            "baseline",
        ),
    ]
    full_particle_path = (
        REPO_ROOT / "artifacts" / "particle_cv_full_20260801" / "particle_detail.csv"
    )
    if full_particle_path.exists():
        packages.append((load_particle_full_package(full_particle_path, metadata), "anchor"))
    historical_particle_path = (
        REPO_ROOT / "artifacts" / "particle_cv_historical_20260801" / "particle_detail.csv"
    )
    if historical_particle_path.exists():
        packages.append(
            (load_particle_historical_package(historical_particle_path, metadata), "anchor")
        )
    summaries = [
        analyze_package(
            frame,
            reference_candidate=reference,
            iterations=args.iterations,
            seed=args.seed + number * 1009,
        )
        for number, (frame, reference) in enumerate(packages)
    ]
    result = pd.concat(summaries, ignore_index=True)
    result = result.sort_values(["package", "pooled_rmse", "candidate"]).reset_index(drop=True)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output_dir / "candidate_score_simulation.csv", index=False)
    metadata.to_csv(args.output_dir / "well_metadata_and_fields.csv", index=False)
    recorded_particle_rmse = 13.1119
    fresh_historical_particle_rmse = None
    if historical_particle_path.exists():
        replay = pd.read_csv(historical_particle_path)
        fresh_historical_particle_rmse = float(
            (
                (replay["rmse_blend625"] ** 2 * replay["n_eval"]).sum()
                / replay["n_eval"].sum()
            )
            ** 0.5
        )
    particle_calibration_rmse = (
        fresh_historical_particle_rmse
        if fresh_historical_particle_rmse is not None
        else recorded_particle_rmse
    )
    calibration = pd.DataFrame(
        [
            {
                "package": "anchor_true_start_773w",
                "local_rmse": 15.909852870734552,
                "public_lb": 15.883,
                "gap_lb_minus_local": 15.883 - 15.909852870734552,
                "submission_ref": 54778368,
                "local_source": "saved 773-well replay",
            },
            {
                "package": "particle_fixed_0.625_773w",
                "local_rmse": particle_calibration_rmse,
                "public_lb": 12.774,
                "gap_lb_minus_local": 12.774 - particle_calibration_rmse,
                "submission_ref": 54779893,
                "local_source": (
                    "fresh exact 2026-08-01 300-particle 8-seed temperature-20 replay"
                    if fresh_historical_particle_rmse is not None
                    else "historical 300-particle 8-seed temperature-20 replay"
                ),
            },
        ]
    )
    calibration.to_csv(args.output_dir / "historical_cv_lb_calibration.csv", index=False)
    prior_submissions = audit_prior_d29_packages()
    prior_submissions.to_csv(args.output_dir / "prior_submission_package_audit.csv", index=False)
    output_distance_score_correlation = float(
        prior_submissions["rms_from_d25_a27_ft"].corr(prior_submissions["public_lb"])
    )
    historical_particle_replay_check = None
    if fresh_historical_particle_rmse is not None:
        historical_particle_replay_check = {
            "fresh_blend625_rmse": fresh_historical_particle_rmse,
            "recorded_blend625_rmse": recorded_particle_rmse,
            "fresh_minus_recorded": fresh_historical_particle_rmse - recorded_particle_rmse,
            "wells": int(len(replay)),
        }

    verdict_rank = {
        "locally_supported": 0,
        "promising_but_inconclusive": 1,
        "inconclusive": 2,
        "rejected": 3,
    }
    ranked = result.loc[result["candidate"] != result["reference"]].copy()
    ranked["verdict_rank"] = ranked["verdict"].map(verdict_rank)
    best = (
        ranked
        .sort_values(["verdict_rank", "private148_p_improve", "delta_vs_reference"], ascending=[True, False, True])
        .groupby("package", as_index=False)
        .first()
        .drop(columns="verdict_rank")
    )
    audit = {
        "bootstrap_iterations": args.iterations,
        "field_count": int(metadata["field"].nunique()),
        "historical_calibration_rows": len(calibration),
        "prior_submission_packages_revalidated": len(prior_submissions),
        "d29_output_distance_vs_public_score_pearson": output_distance_score_correlation,
        "historical_particle_replay_check": historical_particle_replay_check,
        "packages": int(result["package"].nunique()),
        "candidates": len(result),
        "important_limitations": [
            "bootstrap samples complete training wells; it cannot recover the hidden Kaggle split",
            "neighbor_profile_loo does not exclude all donors from the target field; use the field-holdout package for deployment evidence",
            "the saved 30-well particle and 5-well HMM artifacts remain exploratory; separately named 773-well reruns are stronger evidence",
            "public notebook pretrained models require genuine fold OOF predictions before local scoring",
            "a structurally valid submission CSV has no labels and therefore cannot be locally scored by itself",
        ],
        "best_non_control_by_package": best.to_dict(orient="records"),
    }
    (args.output_dir / "audit.json").write_text(
        json.dumps(audit, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    columns = [
        "package",
        "candidate",
        "wells",
        "pooled_rmse",
        "delta_vs_reference",
        "private148_delta_q05",
        "private148_delta_q95",
        "private148_p_improve",
        "evidence_grade",
        "verdict",
    ]
    print(result[columns].to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print("\nHistorical same-pipeline CV/LB checks")
    print(calibration.to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print("\nPrior D29 submission-package contract checks")
    print(
        prior_submissions[
            [
                "route",
                "submission_ref",
                "public_lb",
                "ordered_unique_finite",
                "sha_matches_record",
                "rms_from_d25_a27_ft",
                "locally_scoreable_from_submission_csv",
            ]
        ].to_string(index=False)
    )
    print(
        "D29 output-distance/public-score Pearson "
        f"(diagnostic only, n=5): {output_distance_score_correlation:.4f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
