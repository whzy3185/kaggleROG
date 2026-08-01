"""Submit one hard-gated Kaggle Code version to a notebook-only competition.

The default is a dry run.  ``--execute`` is accepted only after the gate
report, exact remote source, exact remote output, daily budget, unresolved
submission state, and 30-minute spacing have all passed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from kaggle.api.kaggle_api_extended import KaggleApi

try:
    from scripts.preflight_competition_submission import (
        code_sha256,
        metadata_contract,
        object_sha256,
    )
except ModuleNotFoundError:  # Direct ``python scripts/...`` execution.
    from preflight_competition_submission import (
        code_sha256,
        metadata_contract,
        object_sha256,
    )


SHANGHAI = ZoneInfo("Asia/Shanghai")


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_gate_report(
    path: Path, *, competition: str, kernel: str, version: int, file_name: str
) -> dict:
    report = json.loads(path.read_text(encoding="utf-8"))
    expected = {
        "competition": competition,
        "kernel": kernel,
        "kernel_version": version,
        "submission_file": file_name,
    }
    if report.get("passed") is not True:
        raise RuntimeError("Gate report is not passing")
    for key, value in expected.items():
        if report.get(key) != value:
            raise RuntimeError(
                f"Gate report mismatch for {key}: {report.get(key)!r} != {value!r}"
            )
    if not report.get("candidate", {}).get("code_sha256"):
        raise RuntimeError("Gate report has no executable-code SHA-256")
    if not report.get("candidate", {}).get("metadata_contract_sha256"):
        raise RuntimeError("Gate report has no metadata-contract SHA-256")
    if not report.get("output", {}).get("submission_sha256"):
        raise RuntimeError("Gate report has no submission SHA-256")
    return report


def verify_remote_artifacts(api: KaggleApi, report: dict) -> dict:
    kernel = report["kernel"]
    version = int(report["kernel_version"])
    # Kaggle's private-kernel pull endpoint exposes the current source/output;
    # the requested immutable version is still used by competition_submit_code.
    # A later push therefore invalidates the gate unless both artifacts remain
    # byte-identical to the audited version.
    status = str(api.kernels_status(kernel))
    if "COMPLETE" not in status.upper():
        raise RuntimeError(f"Private Code version is not complete: {status}")
    with tempfile.TemporaryDirectory(prefix="rogii-submit-gate-") as temp:
        root = Path(temp)
        source_dir = root / "source"
        output_dir = root / "output"
        source_dir.mkdir()
        output_dir.mkdir()
        api.kernels_pull(kernel, str(source_dir), metadata=True, quiet=True)
        metadata_path = source_dir / "kernel-metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        remote_metadata_contract_sha = object_sha256(metadata_contract(metadata))
        expected_metadata_contract_sha = report["candidate"][
            "metadata_contract_sha256"
        ]
        if remote_metadata_contract_sha != expected_metadata_contract_sha:
            raise RuntimeError(
                "Remote kernel metadata differs from the gated contract: "
                f"{remote_metadata_contract_sha} != {expected_metadata_contract_sha}"
            )
        notebook_path = source_dir / str(metadata.get("code_file", "notebook.ipynb"))
        remote_notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        remote_notebook_sha = file_sha(notebook_path)
        remote_code_sha = code_sha256(remote_notebook)
        expected_code_sha = report["candidate"]["code_sha256"]
        if remote_code_sha != expected_code_sha:
            raise RuntimeError(
                "Exact remote executable code differs from the gated source: "
                f"{remote_code_sha} != {expected_code_sha}"
            )
        api.kernels_output(
            kernel,
            str(output_dir),
            file_pattern=rf"^{re.escape(report['submission_file'])}$",
            force=True,
            quiet=True,
        )
        remote_submission = output_dir / report["submission_file"]
        remote_submission_sha = file_sha(remote_submission)
        expected_submission_sha = report["output"]["submission_sha256"]
        if remote_submission_sha != expected_submission_sha:
            raise RuntimeError(
                "Exact remote output differs from the gated output: "
                f"{remote_submission_sha} != {expected_submission_sha}"
            )
    return {
        "private_status": status,
        "remote_notebook_sha256": remote_notebook_sha,
        "remote_code_sha256": remote_code_sha,
        "remote_metadata_contract_sha256": remote_metadata_contract_sha,
        "remote_submission_sha256": remote_submission_sha,
    }


def enforce_submission_state(api: KaggleApi, competition: str) -> dict:
    rows = [
        row
        for row in (api.competition_submissions(competition, page_size=100) or [])
        if row is not None
    ]
    now_utc = datetime.now(timezone.utc)
    today = now_utc.astimezone(SHANGHAI).date()
    dated: list[tuple[datetime, object]] = []
    for row in rows:
        value = getattr(row, "date", None)
        if not isinstance(value, datetime):
            continue
        aware = value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
        dated.append((aware.astimezone(timezone.utc), row))
    if not dated:
        raise RuntimeError("Could not verify prior submission state; refusing to submit")
    dated.sort(key=lambda item: item[0], reverse=True)
    unresolved = [
        row
        for _, row in dated
        if not str(getattr(row, "public_score", "") or "").strip()
        and not str(getattr(row, "error_description", "") or "").strip()
    ]
    if unresolved:
        refs = [int(getattr(row, "ref")) for row in unresolved]
        raise RuntimeError(f"Unresolved prior competition submissions exist: {refs}")
    today_rows = [
        row for when, row in dated if when.astimezone(SHANGHAI).date() == today
    ]
    failed_today = [
        row
        for row in today_rows
        if str(getattr(row, "error_description", "") or "").strip()
    ]
    if failed_today:
        refs = [int(getattr(row, "ref")) for row in failed_today]
        raise RuntimeError(f"A submission failed today; slate is stopped: {refs}")
    if len(today_rows) >= 5:
        raise RuntimeError(f"Daily budget exhausted: {len(today_rows)}/5")
    latest_time = dated[0][0]
    elapsed_minutes = (now_utc - latest_time).total_seconds() / 60.0
    if elapsed_minutes < 30.0:
        raise RuntimeError(
            f"30-minute interval not satisfied: {elapsed_minutes:.1f} minutes"
        )
    return {
        "today_used": len(today_rows),
        "today_remaining": 5 - len(today_rows),
        "minutes_since_latest": elapsed_minutes,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--competition", required=True)
    parser.add_argument("--kernel", required=True, help="owner/slug")
    parser.add_argument("--version", type=int, required=True)
    parser.add_argument("--file", default="submission.csv")
    parser.add_argument("--message", required=True)
    parser.add_argument("--gate-report", type=Path, required=True)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually create the competition ref after every fail-closed check",
    )
    args = parser.parse_args()

    report = load_gate_report(
        args.gate_report,
        competition=args.competition,
        kernel=args.kernel,
        version=args.version,
        file_name=args.file,
    )
    api = KaggleApi()
    api.authenticate()
    remote = verify_remote_artifacts(api, report)
    state = enforce_submission_state(api, args.competition)
    if not args.execute:
        print(
            json.dumps(
                {
                    "eligible": True,
                    "submitted": False,
                    "reason": "dry run; pass --execute to create a competition ref",
                    "competition": args.competition,
                    "kernel": args.kernel,
                    "kernel_version": args.version,
                    "file": args.file,
                    "remote": remote,
                    "submission_state": state,
                },
                indent=2,
            )
        )
        return
    response = api.competition_submit_code(
        file_name=args.file,
        message=args.message,
        competition=args.competition,
        kernel=args.kernel,
        kernel_version=args.version,
        quiet=True,
    )
    result = {
        "ref": int(response.ref),
        "message": str(response.message or ""),
        "competition": args.competition,
        "kernel": args.kernel,
        "kernel_version": args.version,
        "file": args.file,
        "gate_report": str(args.gate_report.resolve()),
        "remote": remote,
        "submission_state_before_submit": state,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
