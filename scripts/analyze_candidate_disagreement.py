#!/usr/bin/env python3
"""Audit prediction diversity across multiple ROGII submission candidates.

The script never reads hidden labels. It checks the submission contract, computes
pairwise prediction distances, and ranks wells by cross-candidate disagreement.
This is intended as a pre-submission routing signal, not as a score estimator.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd


def parse_candidate(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("candidate must use LABEL=PATH")
    label, path = value.split("=", 1)
    label = label.strip()
    if not label:
        raise argparse.ArgumentTypeError("candidate label cannot be empty")
    return label, Path(path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_candidate(
    label: str,
    path: Path,
    *,
    expected_ids: pd.Series,
) -> tuple[np.ndarray, dict[str, object]]:
    frame = pd.read_csv(path)
    if list(frame.columns) != ["id", "tvt"]:
        raise ValueError(f"{label}: expected columns ['id', 'tvt'], got {list(frame.columns)}")
    if len(frame) != len(expected_ids):
        raise ValueError(f"{label}: expected {len(expected_ids)} rows, got {len(frame)}")
    if not frame["id"].astype(str).equals(expected_ids.astype(str)):
        raise ValueError(f"{label}: ID order differs from the sample submission")
    prediction = frame["tvt"].to_numpy(dtype=float)
    if not np.isfinite(prediction).all():
        raise ValueError(f"{label}: non-finite prediction detected")
    return prediction, {
        "label": label,
        "path": str(path.resolve()),
        "rows": len(frame),
        "sha256": sha256(path),
        "mean": float(prediction.mean()),
        "std": float(prediction.std()),
        "min": float(prediction.min()),
        "max": float(prediction.max()),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument(
        "--candidate",
        action="append",
        type=parse_candidate,
        required=True,
        help="Repeat LABEL=PATH for every audited candidate.",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    sample = pd.read_csv(args.sample)
    if "id" not in sample:
        raise ValueError("sample submission has no id column")
    ids = sample["id"].astype(str)
    well_ids = ids.str.rsplit("_", n=1).str[0]

    predictions: dict[str, np.ndarray] = {}
    manifests: list[dict[str, object]] = []
    for label, path in args.candidate:
        if label in predictions:
            raise ValueError(f"duplicate label: {label}")
        prediction, manifest = load_candidate(label, path, expected_ids=ids)
        predictions[label] = prediction
        manifests.append(manifest)

    if len(predictions) < 2:
        raise ValueError("at least two candidates are required")

    pairwise_rows: list[dict[str, object]] = []
    for left, right in itertools.combinations(predictions, 2):
        delta = predictions[left] - predictions[right]
        pairwise_rows.append(
            {
                "left": left,
                "right": right,
                "rms_delta": float(np.sqrt(np.mean(np.square(delta)))),
                "mean_delta": float(delta.mean()),
                "mean_abs_delta": float(np.abs(delta).mean()),
                "p95_abs_delta": float(np.quantile(np.abs(delta), 0.95)),
                "max_abs_delta": float(np.abs(delta).max()),
                "correlation": float(np.corrcoef(predictions[left], predictions[right])[0, 1]),
            }
        )

    matrix = np.column_stack(list(predictions.values()))
    row_disagreement = matrix.std(axis=1)
    long = pd.DataFrame(
        {
            "id": ids,
            "well_id": well_ids,
            "candidate_std": row_disagreement,
            "candidate_range": matrix.max(axis=1) - matrix.min(axis=1),
        }
    )
    well = (
        long.groupby("well_id", sort=False)
        .agg(
            rows=("id", "size"),
            mean_candidate_std=("candidate_std", "mean"),
            rms_candidate_std=("candidate_std", lambda x: float(np.sqrt(np.mean(np.square(x))))),
            p95_candidate_range=("candidate_range", lambda x: float(np.quantile(x, 0.95))),
            max_candidate_range=("candidate_range", "max"),
        )
        .reset_index()
        .sort_values(["rms_candidate_std", "max_candidate_range"], ascending=False)
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    pairwise = pd.DataFrame(pairwise_rows).sort_values("rms_delta", ascending=False)
    pairwise.to_csv(args.output_dir / "pairwise_candidate_distance.csv", index=False)
    long.to_csv(args.output_dir / "row_candidate_disagreement.csv", index=False)
    well.to_csv(args.output_dir / "well_candidate_disagreement.csv", index=False)
    report = {
        "sample_path": str(args.sample.resolve()),
        "rows": len(sample),
        "wells": int(well_ids.nunique()),
        "candidate_count": len(predictions),
        "candidates": manifests,
        "pairwise": pairwise_rows,
        "highest_disagreement_wells": well.head(20).to_dict(orient="records"),
        "interpretation": (
            "Disagreement is an uncertainty and routing diagnostic only. "
            "It must not be interpreted as hidden-label accuracy."
        ),
    }
    (args.output_dir / "candidate_disagreement_report.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(pairwise.to_string(index=False))
    print("\nHighest-disagreement wells")
    print(well.head(20).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
