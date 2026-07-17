#!/usr/bin/env python3
"""Validate a ROGII submission against the official sample file."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Sequence


EXPECTED_HEADER = ["id", "tvt"]


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        header = list(reader.fieldnames or [])
        rows = list(reader)
    return header, rows


def validate_submission(sample_path: Path, submission_path: Path) -> dict[str, float | int]:
    sample_header, sample_rows = _read_csv(sample_path)
    submission_header, submission_rows = _read_csv(submission_path)

    if sample_header != EXPECTED_HEADER:
        raise ValueError(f"Unexpected sample header: {sample_header!r}")
    if submission_header != EXPECTED_HEADER:
        raise ValueError(f"Submission header must be {EXPECTED_HEADER!r}, got {submission_header!r}")
    if len(sample_rows) != len(submission_rows):
        raise ValueError(
            f"Row count mismatch: sample={len(sample_rows)}, submission={len(submission_rows)}"
        )

    sample_ids = [row["id"] for row in sample_rows]
    submission_ids = [row["id"] for row in submission_rows]
    if submission_ids != sample_ids:
        for index, (expected, actual) in enumerate(zip(sample_ids, submission_ids)):
            if expected != actual:
                raise ValueError(
                    f"ID order mismatch at row {index + 2}: expected={expected!r}, actual={actual!r}"
                )
        raise ValueError("Submission IDs do not exactly match the sample IDs")
    if len(set(submission_ids)) != len(submission_ids):
        raise ValueError("Submission contains duplicate IDs")

    values: list[float] = []
    for index, row in enumerate(submission_rows, start=2):
        try:
            value = float(row["tvt"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid tvt at row {index}: {row['tvt']!r}") from exc
        if not math.isfinite(value):
            raise ValueError(f"Non-finite tvt at row {index}: {row['tvt']!r}")
        values.append(value)

    return {
        "rows": len(values),
        "min_tvt": min(values) if values else math.nan,
        "max_tvt": max(values) if values else math.nan,
        "mean_tvt": sum(values) / len(values) if values else math.nan,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sample", type=Path, help="Path to sample_submission.csv")
    parser.add_argument("submission", type=Path, help="Path to submission.csv")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = validate_submission(args.sample, args.submission)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
