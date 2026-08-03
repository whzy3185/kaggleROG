#!/usr/bin/env python3
"""Fail-closed gate for D35 exact full-source upstream reproductions."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.preflight_competition_submission import (
    Checks,
    COMPETITION,
    FATAL_LOG,
    code_sha256,
    code_sources,
    metadata_contract,
    mounted_submission_hits,
    object_sha256,
    prediction_sha,
    sha256_file,
)
from scripts.verify_submission import validate_submission


AUDIT_PREFIX = "# D35 dynamic hidden-run output contract (read-only)."
UPSTREAM_METADATA_KEYS = (
    "enable_gpu",
    "enable_tpu",
    "dataset_sources",
    "kernel_sources",
    "competition_sources",
    "model_sources",
    "docker_image",
    "machine_shape",
)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_report(
    *,
    candidate_dir: Path,
    upstream_dir: Path,
    output_dir: Path,
    sample: Path,
    kernel: str,
    version: int,
    competition: str,
) -> dict:
    checks = Checks()
    candidate_meta_path = candidate_dir / "kernel-metadata.json"
    upstream_meta_path = upstream_dir / "kernel-metadata.json"
    candidate_meta = read_json(candidate_meta_path)
    upstream_meta = read_json(upstream_meta_path)
    candidate_nb_path = candidate_dir / candidate_meta["code_file"]
    upstream_nb_path = upstream_dir / upstream_meta["code_file"]
    candidate_nb = read_json(candidate_nb_path)
    upstream_nb = read_json(upstream_nb_path)

    checks.require("kernel_identity", candidate_meta.get("id") == kernel, str(candidate_meta.get("id")))
    checks.require("private_code", candidate_meta.get("is_private") is True, "private Version 1 required")
    checks.require("offline_runtime", candidate_meta.get("enable_internet") is False, "internet must be disabled")
    checks.require(
        "competition_source",
        candidate_meta.get("competition_sources") == [competition],
        repr(candidate_meta.get("competition_sources")),
    )
    for key in UPSTREAM_METADATA_KEYS:
        checks.require(
            f"upstream_metadata_{key}",
            candidate_meta.get(key) == upstream_meta.get(key),
            f"candidate={candidate_meta.get(key)!r}; upstream={upstream_meta.get(key)!r}",
        )

    candidate_code = code_sources(candidate_nb)
    upstream_code = code_sources(upstream_nb)
    audit_cells = [source for source in candidate_code if source.startswith(AUDIT_PREFIX)]
    checks.require("one_dynamic_audit_cell", len(audit_cells) == 1, f"count={len(audit_cells)}")
    checks.require(
        "exact_upstream_modelling_code",
        len(candidate_code) == len(upstream_code) + 1
        and candidate_code[:-1] == upstream_code
        and candidate_code[-1].startswith(AUDIT_PREFIX),
        f"candidate_code_cells={len(candidate_code)}; upstream_code_cells={len(upstream_code)}",
    )
    joined = "\n\n".join(candidate_code)
    hits = mounted_submission_hits(joined)
    checks.require("no_visible_submission_as_hidden_parent", not hits, repr(hits))
    checks.require(
        "dynamic_official_sample_contract",
        competition in candidate_code[-1]
        and "len(_d35_sub) != len(_d35_sample)" in candidate_code[-1]
        and "_d35_sub['id'].equals(_d35_sample['id'])" in candidate_code[-1],
        "audit must inherit hidden row count and exact official ID order",
    )

    submission_path = output_dir / "submission.csv"
    audit_path = output_dir / "d35_final_audit.json"
    output_summary: dict = {}
    file_sha = ""
    pred_sha = ""
    try:
        output_summary = validate_submission(sample, submission_path)
        file_sha = sha256_file(submission_path)
        pred_sha = prediction_sha(submission_path)
        checks.require("visible_output_contract", True, json.dumps(output_summary, sort_keys=True))
    except Exception as exc:
        checks.require("visible_output_contract", False, repr(exc))
    try:
        audit = read_json(audit_path)
        audit_ok = (
            audit.get("submission_sha256") == file_sha
            and audit.get("prediction_sha256") == pred_sha
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
        text = log_path.read_text(encoding="utf-8", errors="replace")
        fatal_hits.extend(sorted(set(match.group(0) for match in FATAL_LOG.finditer(text))))
    checks.require("execution_log_present", bool(log_paths), repr([path.name for path in log_paths]))
    checks.require("no_fatal_log_markers", not fatal_hits, repr(fatal_hits))

    lineage_sha = object_sha256(upstream_code)
    return {
        "schema_version": 2,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "passed": checks.passed,
        "competition": competition,
        "kernel": kernel,
        "kernel_version": version,
        "submission_file": "submission.csv",
        "candidate": {
            "lineage_mode": "exact_upstream",
            "directory": str(candidate_dir.resolve()),
            "upstream_directory": str(upstream_dir.resolve()),
            "notebook_path": str(candidate_nb_path.resolve()),
            "notebook_sha256": sha256_file(candidate_nb_path),
            "code_sha256": code_sha256(candidate_nb),
            "lineage_code_sha256": lineage_sha,
            "metadata_sha256": sha256_file(candidate_meta_path),
            "metadata_contract": metadata_contract(candidate_meta),
            "metadata_contract_sha256": object_sha256(metadata_contract(candidate_meta)),
            "baseline_notebook": str(upstream_nb_path.resolve()),
            "baseline_notebook_sha256": sha256_file(upstream_nb_path),
        },
        "output": {
            "directory": str(output_dir.resolve()),
            "submission_path": str(submission_path.resolve()),
            "submission_sha256": file_sha,
            "prediction_sha256": pred_sha,
            "audit_path": str(audit_path.resolve()),
            "log_files": [str(path.resolve()) for path in log_paths],
            **output_summary,
        },
        "checks": checks.rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--upstream-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument("--kernel", required=True)
    parser.add_argument("--version", type=int, required=True)
    parser.add_argument("--competition", default=COMPETITION)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = build_report(
        candidate_dir=args.candidate_dir,
        upstream_dir=args.upstream_dir,
        output_dir=args.output_dir,
        sample=args.sample,
        kernel=args.kernel,
        version=args.version,
        competition=args.competition,
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
