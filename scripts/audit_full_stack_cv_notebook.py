#!/usr/bin/env python3
"""Audit whether a ROGII notebook's full-stack CV is usable as local evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rogii.notebook_cv_audit import audit_full_stack_notebook  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "notebook",
        type=Path,
        nargs="?",
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
        default=REPO_ROOT / "artifacts" / "local_score_simulation_20260801" / "full_stack_cv_preflight.json",
    )
    args = parser.parse_args()
    report = audit_full_stack_notebook(args.notebook)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["locally_scoreable_as_stored"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
