#!/usr/bin/env python3
"""Build the deterministic last-visible-TVT submission in official ID order."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]


def build_anchor_submission(data_dir: Path, output_path: Path) -> pd.DataFrame:
    sample_path = data_dir / "sample_submission.csv"
    test_dir = data_dir / "test"
    sample = pd.read_csv(sample_path)
    if list(sample.columns) != ["id", "tvt"]:
        raise ValueError(f"Unexpected sample columns: {list(sample.columns)!r}")

    predictions: dict[str, float] = {}
    for path in sorted(test_dir.glob("*__horizontal_well.csv")):
        well_id = path.name.removesuffix("__horizontal_well.csv")
        frame = pd.read_csv(path, usecols=["TVT_input"])
        observed = frame["TVT_input"].notna().to_numpy()
        missing = np.flatnonzero(~observed)
        if not len(missing) or missing[0] == 0 or observed[missing[0] :].any():
            raise ValueError(f"{well_id}: TVT_input must have a visible prefix and missing suffix")
        anchor = float(frame.loc[missing[0] - 1, "TVT_input"])
        for row_index in missing:
            predictions[f"{well_id}_{row_index}"] = anchor

    expected_ids = sample["id"].astype(str)
    unknown = sorted(set(predictions).difference(expected_ids))
    missing_ids = sorted(set(expected_ids).difference(predictions))
    if unknown or missing_ids:
        raise ValueError(
            f"Prediction/sample ID mismatch: unknown={unknown[:3]!r}, missing={missing_ids[:3]!r}"
        )
    submission = pd.DataFrame(
        {"id": expected_ids, "tvt": expected_ids.map(predictions).astype(float)}
    )
    if not np.isfinite(submission["tvt"]).all():
        raise ValueError("Submission contains non-finite predictions")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    submission.to_csv(output_path, index=False)
    return submission


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=REPO_ROOT / "data" / "raw" / "competition",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "outputs" / "submission_anchor.csv",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    submission = build_anchor_submission(args.data_dir, args.output)
    print(
        f"wrote {args.output} with {len(submission)} rows; "
        f"tvt range [{submission.tvt.min():.3f}, {submission.tvt.max():.3f}]"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
