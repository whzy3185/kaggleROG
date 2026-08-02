#!/usr/bin/env python3
"""Fail-closed preflight for a ROGII Kaggle Code competition submission.

This script never submits.  It binds an exact private Code version to its
downloaded source and output, rejects deployment patterns that failed hidden
reruns, and writes a machine-readable gate report.  The submission wrapper
accepts only a passing report whose hashes still match Kaggle.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd

try:
    from scripts.verify_submission import validate_submission
except ModuleNotFoundError:  # Direct ``python scripts/...`` execution.
    from verify_submission import validate_submission


COMPETITION = "rogii-wellbore-geology-prediction"
FATAL_LOG = re.compile(
    r"Traceback|PapermillExecutionError|Segmentation fault|CUDA error|"
    r"out of memory|KeyError:\s*['\"]wid['\"]|competition mount unavailable",
    re.IGNORECASE,
)
MOUNTED_SUBMISSION_PATTERNS = {
    "direct /kaggle/input submission path": re.compile(
        r"/kaggle/input[^'\"\n]*(?<!sample_)submission\.csv", re.IGNORECASE
    ),
    "INPUT alias submission discovery": re.compile(
        r"\bINPUT\s*\.\s*(?:rglob|glob)\s*\(\s*['\"]submission\.csv",
        re.IGNORECASE,
    ),
    "Path('/kaggle/input') submission discovery": re.compile(
        r"Path\s*\(\s*['\"]/kaggle/input['\"]\s*\)\s*\.\s*"
        r"(?:rglob|glob)\s*\(\s*['\"]submission\.csv",
        re.IGNORECASE,
    ),
}
RUNTIME_LIMITS = {
    "SP45_SELECTOR_N_PARTICLES": 500,
    "SP45_SELECTOR_N_SEEDS": 128,
    "VISIBLE_PREFIX_PARTICLES": 350,
    "VISIBLE_PREFIX_FINAL_SEEDS": 48,
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_text(cell: dict[str, Any]) -> str:
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else str(source)


def code_sources(notebook: dict[str, Any]) -> list[str]:
    return [
        source_text(cell)
        for cell in notebook.get("cells", [])
        if cell.get("cell_type") == "code"
    ]


def code_sha256(notebook: dict[str, Any]) -> str:
    payload = json.dumps(
        code_sources(notebook), ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def metadata_contract(metadata: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "id",
        "is_private",
        "enable_gpu",
        "enable_tpu",
        "enable_internet",
        "dataset_sources",
        "kernel_sources",
        "competition_sources",
        "model_sources",
        "docker_image",
        "machine_shape",
    )
    return {key: metadata.get(key) for key in keys}


def object_sha256(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def mounted_submission_hits(source: str) -> list[str]:
    """Find visible-output dependencies in executable competition code.

    This intentionally does not inspect local research scripts and does not
    reject run-local ``/kaggle/working/submission.csv`` reads.
    """
    return [
        label
        for label, pattern in MOUNTED_SUBMISSION_PATTERNS.items()
        if pattern.search(source) is not None
    ]


def prediction_sha(submission_path: Path) -> str:
    values = pd.read_csv(submission_path)["tvt"].to_numpy(float)
    return hashlib.sha256(np.asarray(values, dtype="<f8").tobytes(order="C")).hexdigest()


def _normalise_d29_lineage(sources: list[str]) -> list[str]:
    """Undo the explicitly allowed D29 non-branch deployment edits."""
    result: list[str] = []
    for source in sources:
        if "# Deployment preflight:" in source:
            continue
        source = re.sub(
            r"(?m)^_D29N_WEIGHT[ \t]*=[ \t]*[0-9.]+[ \t]*$",
            "_D29N_WEIGHT = 0.05",
            source,
        )
        source = re.sub(
            r"(_D29N_WEIGHT \* _d29n_smooth,\n\s*)-[0-9.]+,(\n\s*)[0-9.]+,",
            r"\g<1>-0.18,\g<2>0.18,",
            source,
        )
        source = re.sub(
            r"(?:d(?:32|33)_full_nonbranch|d34_hardened_nonbranch)_\d+",
            "a27_nonbranch_r1",
            source,
        )
        source = source.replace(
            "len(_d29_sub) != len(_d29_sample)",
            "len(_d29_sub) != 14151 or len(_d29_sample) != 14151",
        )
        result.append(source)
    return result


class Checks:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def require(self, name: str, condition: bool, detail: str) -> None:
        self.rows.append(
            {"name": name, "status": "pass" if condition else "fail", "detail": detail}
        )

    @property
    def passed(self) -> bool:
        return bool(self.rows) and all(row["status"] == "pass" for row in self.rows)


def build_gate_report(
    *,
    candidate_dir: Path,
    output_dir: Path,
    sample: Path,
    baseline_notebook: Path,
    kernel: str,
    version: int,
    competition: str = COMPETITION,
) -> dict[str, Any]:
    checks = Checks()
    metadata_path = candidate_dir / "kernel-metadata.json"
    metadata: dict[str, Any] = {}
    notebook_path = candidate_dir / "notebook.ipynb"
    notebook: dict[str, Any] = {}
    lineage_code_sha = ""

    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        checks.require("metadata_json", True, str(metadata_path))
    except Exception as exc:
        checks.require("metadata_json", False, repr(exc))

    if metadata:
        notebook_path = candidate_dir / str(metadata.get("code_file", "notebook.ipynb"))
        checks.require("kernel_identity", metadata.get("id") == kernel, str(metadata.get("id")))
        checks.require("private_code", metadata.get("is_private") is True, "is_private must be true")
        checks.require("gpu_runtime", metadata.get("enable_gpu") is True, "T4/GPU is mandatory for this stack")
        checks.require("offline_runtime", metadata.get("enable_internet") is False, "internet must be disabled")
        checks.require(
            "competition_source",
            metadata.get("competition_sources") == [competition],
            repr(metadata.get("competition_sources")),
        )

    try:
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        checks.require("notebook_json", True, str(notebook_path))
    except Exception as exc:
        checks.require("notebook_json", False, repr(exc))

    if notebook:
        sources = code_sources(notebook)
        joined = "\n\n".join(sources)
        baseline: dict[str, Any] = {}
        baseline_joined = ""
        try:
            baseline = json.loads(baseline_notebook.read_text(encoding="utf-8"))
            baseline_joined = "\n\n".join(code_sources(baseline))
            checks.require("baseline_notebook_json", True, str(baseline_notebook))
        except Exception as exc:
            checks.require("baseline_notebook_json", False, repr(exc))
        checks.require(
            "competition_mount_preflight",
            "competition mount unavailable" in joined
            and "sample_submission.csv" in joined
            and competition in joined,
            "must fail before modelling when train/test/sample are absent",
        )
        candidate_public_row_literals = len(re.findall(r"\b14151\b", joined))
        baseline_public_row_literals = len(
            re.findall(r"\b14151\b", baseline_joined)
        )
        checks.require(
            "no_new_fixed_public_row_contract",
            bool(baseline)
            and candidate_public_row_literals <= baseline_public_row_literals,
            (
                "inherited constants from the already-scored baseline are "
                "allowed; new ones are not: "
                f"candidate={candidate_public_row_literals}, "
                f"baseline={baseline_public_row_literals}"
            ),
        )
        external_submission_hits = mounted_submission_hits(joined)
        checks.require(
            "no_visible_submission_as_hidden_parent",
            not external_submission_hits,
            (
                "Reading public submission.csv is allowed in offline research; "
                "a competition notebook must recompute hidden predictions. "
                f"runtime hits={external_submission_hits!r}; "
                f"kernel_sources={metadata.get('kernel_sources', [])!r}"
            ),
        )
        checks.require(
            "writes_run_local_submission",
            "submission.csv" in joined and "to_csv" in joined,
            "notebook must build submission.csv in-run",
        )
        for flag in ("RUN_CV_REPORT", "RUN_FULL_STACK_CV_ABLATION"):
            enabled = re.search(rf"(?m)^\s*{flag}\s*=\s*True\s*$", joined) is not None
            checks.require(f"{flag.lower()}_disabled", not enabled, f"{flag}=False required")
        for variable, maximum in RUNTIME_LIMITS.items():
            match = re.search(rf"(?m)^\s*{variable}\s*=\s*([0-9]+)\s*$", joined)
            value = int(match.group(1)) if match else None
            checks.require(
                f"runtime_cap_{variable.lower()}",
                value is not None and value <= maximum,
                f"value={value!r}, maximum={maximum}",
            )
        try:
            if not baseline:
                raise RuntimeError("baseline notebook did not load")
            same_lineage = _normalise_d29_lineage(sources) == code_sources(baseline)
            lineage_code_sha = object_sha256(_normalise_d29_lineage(sources))
            checks.require(
                "scored_source_lineage",
                same_lineage,
                "only weight, proportional clip, route label, dynamic audit, and preflight may differ",
            )
        except Exception as exc:
            checks.require("scored_source_lineage", False, repr(exc))

    submission_path = output_dir / "submission.csv"
    audit_candidates = [output_dir / "d29_final_audit.json", output_dir / "d32_final_audit.json"]
    audit_path = next((path for path in audit_candidates if path.exists()), audit_candidates[0])
    output_summary: dict[str, Any] = {}
    actual_file_sha = ""
    actual_pred_sha = ""
    try:
        output_summary = validate_submission(sample, submission_path)
        actual_file_sha = sha256_file(submission_path)
        actual_pred_sha = prediction_sha(submission_path)
        checks.require("visible_output_contract", True, json.dumps(output_summary, sort_keys=True))
    except Exception as exc:
        checks.require("visible_output_contract", False, repr(exc))

    audit: dict[str, Any] = {}
    try:
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        audit_ok = (
            audit.get("file_sha256") == actual_file_sha
            and audit.get("prediction_sha256") == actual_pred_sha
            and audit.get("ordered_unique_ids") is True
            and audit.get("finite_tvt") is True
            and audit.get("rows") == output_summary.get("rows")
        )
        checks.require("run_audit_hashes", audit_ok, str(audit_path))
    except Exception as exc:
        checks.require("run_audit_hashes", False, repr(exc))

    log_paths = sorted(output_dir.glob("*.log"))
    fatal_hits: list[str] = []
    for log_path in log_paths:
        log_text = log_path.read_text(encoding="utf-8", errors="replace")
        fatal_hits.extend(sorted(set(match.group(0) for match in FATAL_LOG.finditer(log_text))))
    checks.require("execution_log_present", bool(log_paths), repr([p.name for p in log_paths]))
    checks.require("no_fatal_log_markers", not fatal_hits, repr(fatal_hits))

    report = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "passed": checks.passed,
        "competition": competition,
        "kernel": kernel,
        "kernel_version": version,
        "submission_file": "submission.csv",
        "candidate": {
            "directory": str(candidate_dir.resolve()),
            "notebook_path": str(notebook_path.resolve()),
            "notebook_sha256": sha256_file(notebook_path) if notebook_path.exists() else "",
            "code_sha256": code_sha256(notebook) if notebook else "",
            "lineage_code_sha256": lineage_code_sha,
            "metadata_sha256": sha256_file(metadata_path) if metadata_path.exists() else "",
            "metadata_contract": metadata_contract(metadata) if metadata else {},
            "metadata_contract_sha256": (
                object_sha256(metadata_contract(metadata)) if metadata else ""
            ),
            "baseline_notebook": str(baseline_notebook.resolve()),
            "baseline_notebook_sha256": (
                sha256_file(baseline_notebook) if baseline_notebook.exists() else ""
            ),
        },
        "output": {
            "directory": str(output_dir.resolve()),
            "submission_path": str(submission_path.resolve()),
            "submission_sha256": actual_file_sha,
            "prediction_sha256": actual_pred_sha,
            "audit_path": str(audit_path.resolve()),
            "log_files": [str(path.resolve()) for path in log_paths],
            **output_summary,
        },
        "checks": checks.rows,
    }
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument("--baseline-notebook", type=Path, required=True)
    parser.add_argument("--kernel", required=True)
    parser.add_argument("--version", type=int, required=True)
    parser.add_argument("--competition", default=COMPETITION)
    parser.add_argument("--report", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_gate_report(
        candidate_dir=args.candidate_dir,
        output_dir=args.output_dir,
        sample=args.sample,
        baseline_notebook=args.baseline_notebook,
        kernel=args.kernel,
        version=args.version,
        competition=args.competition,
    )
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
