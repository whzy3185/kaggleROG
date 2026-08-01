import json
from pathlib import Path

import pytest

from scripts.preflight_competition_submission import _normalise_d29_lineage
from scripts.submit_code_version import load_gate_report


def test_lineage_normalizer_removes_only_declared_deployment_edits():
    candidate = [
        "# Deployment preflight: stop before model construction\nraise RuntimeError('competition mount unavailable')",
        "_D29N_WEIGHT = 0.25\n",
        "_d29n_move_ordered = f(\n    _D29N_WEIGHT * _d29n_smooth,\n    -0.90,\n    0.90,\n)\n",
        "_D29_ROUTE = 'd32_full_nonbranch_25'\n"
        "if len(_d29_sub) != len(_d29_sample):\n    pass\n",
    ]
    assert _normalise_d29_lineage(candidate) == [
        "_D29N_WEIGHT = 0.05\n",
        "_d29n_move_ordered = f(\n    _D29N_WEIGHT * _d29n_smooth,\n    -0.18,\n    0.18,\n)\n",
        "_D29_ROUTE = 'a27_nonbranch_r1'\n"
        "if len(_d29_sub) != 14151 or len(_d29_sample) != 14151:\n    pass\n",
    ]


def _write_report(path: Path, **updates) -> None:
    report = {
        "passed": True,
        "competition": "comp",
        "kernel": "owner/slug",
        "kernel_version": 2,
        "submission_file": "submission.csv",
        "candidate": {
            "code_sha256": "a" * 64,
            "metadata_contract_sha256": "c" * 64,
        },
        "output": {"submission_sha256": "b" * 64},
    }
    report.update(updates)
    path.write_text(json.dumps(report), encoding="utf-8")


def test_submit_wrapper_rejects_failed_gate(tmp_path):
    path = tmp_path / "gate.json"
    _write_report(path, passed=False)
    with pytest.raises(RuntimeError, match="not passing"):
        load_gate_report(
            path,
            competition="comp",
            kernel="owner/slug",
            version=2,
            file_name="submission.csv",
        )


def test_submit_wrapper_rejects_version_mismatch(tmp_path):
    path = tmp_path / "gate.json"
    _write_report(path)
    with pytest.raises(RuntimeError, match="kernel_version"):
        load_gate_report(
            path,
            competition="comp",
            kernel="owner/slug",
            version=3,
            file_name="submission.csv",
        )
