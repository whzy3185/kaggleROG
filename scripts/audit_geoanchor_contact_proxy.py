#!/usr/bin/env python3
"""Audit the contact layer that connects GeoAnchor's 6.568 anchor to R2000."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rogii.geoanchor_oof import contact_proxy_cv, reconstruct_contact_anchor  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-root",
        type=Path,
        default=REPO_ROOT / "data" / "raw" / "competition",
    )
    parser.add_argument(
        "--anchor",
        type=Path,
        default=REPO_ROOT
        / "research"
        / "pulled_20260801"
        / "private_runs"
        / "geoanchor_exact"
        / "output"
        / "submission_anchor_6p568.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "artifacts" / "geoanchor_contact_proxy_audit_20260801",
    )
    args = parser.parse_args()

    train_proxy = contact_proxy_cv(args.data_root / "train")
    anchor = pd.read_csv(args.anchor)
    reconstruction = reconstruct_contact_anchor(args.data_root, anchor)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    train_proxy.to_csv(args.output_dir / "train_contact_proxy_by_well.csv", index=False)
    reconstruction.to_csv(args.output_dir / "anchor_reconstruction_by_well.csv", index=False)

    pooled_proxy = float(
        np.sqrt(train_proxy["sse"].sum() / train_proxy["n_eval"].sum())
    )
    weighted_reconstruction = float(
        np.sqrt(
            np.average(
                reconstruction["rms_from_anchor"] ** 2,
                weights=reconstruction["rows"],
            )
        )
    )
    summary = {
        "train_proxy_wells": len(train_proxy),
        "train_proxy_rows": int(train_proxy["n_eval"].sum()),
        "train_proxy_pooled_rmse": pooled_proxy,
        "test_wells": len(reconstruction),
        "test_rows": int(reconstruction["rows"].sum()),
        "test_files_contain_egfdu": bool(reconstruction["test_has_ref_col"].all()),
        "full_train_truth_contact_rms_from_scored_6p568_anchor": weighted_reconstruction,
        "full_train_truth_contact_max_abs_from_scored_6p568_anchor": float(
            reconstruction["max_abs_from_anchor"].max()
        ),
        "measured_anchor_public_rmse": 6.568,
        "local_score_interpretation": "invalid target proxy, not a leaderboard estimate",
        "reason": (
            "EGFDU and the other formation columns exist in train but not test; the scored "
            "anchor is reconstructed by reading full TVT and formations from overlapping "
            "train wells and interpolating them onto test MD."
        ),
    }
    (args.output_dir / "audit.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
