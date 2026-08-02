#!/usr/bin/env python3
"""Prepare the D34 hidden-data-safe non-branch response curve."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.prepare_d32_private_runs import ROOT, prepare_full_shape


OUT = ROOT / "research" / "pulled_20260802" / "private_runs"
SPECS = [
    ("nonbranch_10", "rogii-d34-hardened-nonbranch10-r1", "ROGII D34 Hardened Nonbranch10 R1", 2.0),
    ("nonbranch_15", "rogii-d34-hardened-nonbranch15-r1", "ROGII D34 Hardened Nonbranch15 R1", 3.0),
    ("nonbranch_20", "rogii-d34-hardened-nonbranch20-r1", "ROGII D34 Hardened Nonbranch20 R1", 4.0),
    ("nonbranch_25", "rogii-d34-hardened-nonbranch25-r1", "ROGII D34 Hardened Nonbranch25 R1", 5.0),
    ("nonbranch_30", "rogii-d34-hardened-nonbranch30-r1", "ROGII D34 Hardened Nonbranch30 R1", 6.0),
]
EMPTY_MOUNT_RETRY_SPECS = [
    ("nonbranch_10_r2", "rogii-d34-hardened-nonbranch10-r2", "ROGII D34 Hardened Nonbranch10 R2", 2.0),
    ("nonbranch_20_r2", "rogii-d34-hardened-nonbranch20-r2", "ROGII D34 Hardened Nonbranch20 R2", 4.0),
    ("nonbranch_25_r2", "rogii-d34-hardened-nonbranch25-r2", "ROGII D34 Hardened Nonbranch25 R2", 5.0),
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retry-empty-mount", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    reports = []
    specs = EMPTY_MOUNT_RETRY_SPECS if args.retry_empty_mount else SPECS
    for name, slug, title, scale in specs:
        percent = int(round(scale * 5))
        reports.append(
            prepare_full_shape(
                name,
                slug,
                title,
                scale,
                out_root=OUT,
                route_label=f"d34_hardened_nonbranch_{percent}",
            )
        )
    print(json.dumps(reports, indent=2))


if __name__ == "__main__":
    main()
