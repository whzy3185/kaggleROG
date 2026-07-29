"""Audit downloaded D29 private Version 1 outputs before submission.

The script is read-only unless ``--json-output`` is supplied.  It validates
the immutable notebook audit, the sample-ordered prediction vector, fatal log
markers, distances from the measured D25 A27 parent, and all pairwise
distances among available D29 candidates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "artifacts" / "d29_private_runs"
DEFAULT_BASELINE = (
    ROOT / "artifacts" / "d25_private_runs" / "a27_narrow" / "submission.csv"
)
FATAL = re.compile(
    r"Traceback|RuntimeError|PapermillExecutionError|Segmentation fault|"
    r"CUDA error|out of memory",
    re.IGNORECASE,
)


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pred_sha(values: np.ndarray) -> str:
    return hashlib.sha256(
        np.asarray(values, dtype="<f8").tobytes(order="C")
    ).hexdigest()


def read_submission(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    if list(frame.columns) != ["id", "tvt"]:
        raise RuntimeError(f"{path}: expected id,tvt columns")
    if len(frame) != 14151:
        raise RuntimeError(f"{path}: expected 14151 rows, found {len(frame)}")
    frame["id"] = frame["id"].astype(str)
    if frame["id"].duplicated().any():
        raise RuntimeError(f"{path}: duplicate IDs")
    frame["tvt"] = pd.to_numeric(frame["tvt"], errors="coerce")
    if not np.isfinite(frame["tvt"].to_numpy(float)).all():
        raise RuntimeError(f"{path}: non-finite predictions")
    return frame


def audit_route(directory: Path, baseline: pd.DataFrame) -> tuple[dict, np.ndarray]:
    sub_path = directory / "submission.csv"
    report_path = directory / "d29_final_audit.json"
    if not report_path.exists():
        raise RuntimeError(f"{directory}: missing d29_final_audit.json")
    sub = read_submission(sub_path)
    if not sub["id"].equals(baseline["id"]):
        raise RuntimeError(f"{directory}: IDs differ from baseline order")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    values = sub["tvt"].to_numpy(float)
    actual_file_sha = file_sha(sub_path)
    actual_pred_sha = pred_sha(values)
    if report.get("file_sha256") != actual_file_sha:
        raise RuntimeError(f"{directory}: final file SHA mismatch")
    if report.get("prediction_sha256") != actual_pred_sha:
        raise RuntimeError(f"{directory}: final prediction SHA mismatch")
    log_paths = sorted(directory.glob("*.log"))
    fatal_hits: list[str] = []
    for log_path in log_paths:
        text = log_path.read_text(encoding="utf-8", errors="replace")
        fatal_hits.extend(sorted(set(match.group(0) for match in FATAL.finditer(text))))
    if fatal_hits:
        raise RuntimeError(f"{directory}: fatal log markers {fatal_hits}")
    baseline_values = baseline["tvt"].to_numpy(float)
    delta = values - baseline_values
    return (
        {
            "route": directory.name,
            "rows": int(len(sub)),
            "file_sha256": actual_file_sha,
            "prediction_sha256": actual_pred_sha,
            "rms_from_d25_a27_ft": float(np.sqrt(np.mean(delta**2))),
            "max_abs_from_d25_a27_ft": float(np.max(np.abs(delta))),
            "changed_rows_from_d25_a27": int(np.count_nonzero(delta)),
            "log_files": [path.name for path in log_paths],
            "fatal_log_markers": [],
        },
        values,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()

    baseline = read_submission(args.baseline)
    route_dirs = sorted(
        path
        for path in args.input_root.iterdir()
        if path.is_dir() and (path / "submission.csv").exists()
    )
    if not route_dirs:
        raise RuntimeError(f"No downloaded routes found under {args.input_root}")

    routes: list[dict] = []
    vectors: dict[str, np.ndarray] = {}
    for directory in route_dirs:
        row, values = audit_route(directory, baseline)
        routes.append(row)
        vectors[directory.name] = values

    pairwise: list[dict] = []
    names = sorted(vectors)
    for left_index, left in enumerate(names):
        for right in names[left_index + 1 :]:
            delta = vectors[left] - vectors[right]
            pairwise.append(
                {
                    "left": left,
                    "right": right,
                    "rms_ft": float(np.sqrt(np.mean(delta**2))),
                    "max_abs_ft": float(np.max(np.abs(delta))),
                    "byte_duplicate": bool(np.array_equal(vectors[left], vectors[right])),
                }
            )

    result = {
        "baseline": str(args.baseline),
        "baseline_file_sha256": file_sha(args.baseline),
        "routes": routes,
        "pairwise": pairwise,
    }
    rendered = json.dumps(result, indent=2)
    print(rendered)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
