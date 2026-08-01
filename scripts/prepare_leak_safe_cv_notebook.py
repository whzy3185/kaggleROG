#!/usr/bin/env python3
"""Create a visibly labelled, leak-safe D29 component-CV notebook copy."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rogii.notebook_cv_audit import (  # noqa: E402
    audit_full_stack_notebook,
    prepare_leak_safe_diagnostic_copy,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=REPO_ROOT
        / "research"
        / "pulled_20260729"
        / "private_runs"
        / "a27_nonbranch_r1"
        / "notebook.ipynb",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT
        / "artifacts"
        / "local_score_simulation_20260801"
        / "d29_leak_safe_component_cv.ipynb",
    )
    parser.add_argument("--n-wells", type=int, default=30)
    parser.add_argument("--selector-seeds", type=int, default=8)
    parser.add_argument(
        "--data-root",
        type=Path,
        default=REPO_ROOT / "data" / "raw" / "competition",
    )
    args = parser.parse_args()
    patch_report = prepare_leak_safe_diagnostic_copy(
        args.source,
        args.output,
        n_wells=args.n_wells,
        selector_seeds=args.selector_seeds,
        data_root=args.data_root,
    )
    report = {"patch": patch_report, "post_patch_audit": audit_full_stack_notebook(args.output)}
    report_path = args.output.with_suffix(".audit.json")
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
