import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.preflight_competition_submission import (
    _normalise_d29_lineage,
    mounted_submission_hits,
    prediction_sha,
    sha256_file,
)
from scripts.preflight_d35_exact_upstream import build_report as build_d35_report
from scripts.submit_code_version import (
    enforce_submission_state,
    load_gate_report,
    validate_scored_canary_report,
)


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


def test_lineage_normalizer_accepts_d34_hardened_route_label():
    assert _normalise_d29_lineage(
        ["_D29_ROUTE = 'd34_hardened_nonbranch_20'\n"]
    ) == ["_D29_ROUTE = 'a27_nonbranch_r1'\n"]


def test_public_submission_is_allowed_for_research_but_not_hidden_parent():
    assert mounted_submission_hits(
        "pd.read_csv('/kaggle/working/submission.csv')"
    ) == []
    assert mounted_submission_hits(
        "INPUT.rglob('submission.csv')"
    ) == ["INPUT alias submission discovery"]
    assert mounted_submission_hits(
        "pd.read_csv('/kaggle/input/other-kernel/submission.csv')"
    ) == ["direct /kaggle/input submission path"]


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
            "lineage_code_sha256": "d" * 64,
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


def test_diverse_canary_exception_is_exact_upstream_and_same_competition_only():
    current = {
        "passed": True,
        "competition": "comp",
        "candidate": {
            "lineage_code_sha256": "a" * 64,
            "lineage_mode": "exact_upstream",
        },
    }
    canary = {
        "passed": True,
        "competition": "comp",
        "candidate": {
            "lineage_code_sha256": "b" * 64,
            "lineage_mode": "exact_upstream",
        },
    }
    with pytest.raises(RuntimeError, match="does not share"):
        validate_scored_canary_report(current, canary)
    validate_scored_canary_report(
        current, canary, allow_diverse_exact_upstream=True
    )
    canary["candidate"]["lineage_mode"] = "normalized_local"
    with pytest.raises(RuntimeError, match="two exact-upstream"):
        validate_scored_canary_report(
            current, canary, allow_diverse_exact_upstream=True
        )
    canary["candidate"]["lineage_mode"] = "exact_upstream"
    canary["competition"] = "other"
    with pytest.raises(RuntimeError, match="competition mismatch"):
        validate_scored_canary_report(
            current, canary, allow_diverse_exact_upstream=True
        )


class _FakeApi:
    def __init__(self, rows):
        self.rows = rows

    def competition_submissions(self, competition, page_size=100):
        assert competition == "comp"
        assert page_size == 100
        return self.rows


def _submission(ref, minutes_ago, *, score="", error=""):
    date = (datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)).replace(
        tzinfo=None
    )
    return SimpleNamespace(
        ref=ref, date=date, public_score=score, error_description=error
    )


def test_unresolved_submission_blocks_without_scored_canary():
    api = _FakeApi([_submission(2, 31), _submission(1, 90, score="6.455")])
    with pytest.raises(RuntimeError, match="no scored canary"):
        enforce_submission_state(api, "comp")


def test_scored_canary_allows_same_day_pending_after_spacing():
    api = _FakeApi([_submission(2, 31), _submission(1, 90, score="6.455")])
    state = enforce_submission_state(api, "comp", scored_canary_ref=1)
    assert state["unresolved_today"] == [2]
    assert state["scored_canary_score"] == "6.455"


def test_historical_scored_lineage_allows_today_pending_after_spacing():
    api = _FakeApi([_submission(2, 31), _submission(1, 1500, score="6.455")])
    state = enforce_submission_state(api, "comp", scored_canary_ref=1)
    assert state["unresolved_today"] == [2]
    assert state["scored_canary_ref"] == 1


def test_d35_exact_upstream_gate_accepts_only_appended_dynamic_audit(tmp_path):
    upstream = tmp_path / "upstream"
    candidate = tmp_path / "candidate"
    output = tmp_path / "output"
    upstream.mkdir()
    candidate.mkdir()
    output.mkdir()
    upstream_meta = {
        "id": "author/source",
        "code_file": "source.ipynb",
        "enable_gpu": False,
        "enable_tpu": False,
        "enable_internet": False,
        "dataset_sources": ["author/artifacts"],
        "kernel_sources": [],
        "competition_sources": ["rogii-wellbore-geology-prediction"],
        "model_sources": [],
    }
    candidate_meta = {
        **upstream_meta,
        "id": "owner/private",
        "code_file": "notebook.ipynb",
        "is_private": True,
    }
    model_code = "print('model')\n"
    audit_code = (
        "# D35 dynamic hidden-run output contract (read-only).\n"
        "competition='rogii-wellbore-geology-prediction'\n"
        "if len(_d35_sub) != len(_d35_sample): pass\n"
        "assert _d35_sub['id'].equals(_d35_sample['id'])\n"
    )

    def notebook(sources):
        return {
            "cells": [
                {"cell_type": "code", "source": source, "outputs": [], "execution_count": None}
                for source in sources
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 5,
        }

    (upstream / "kernel-metadata.json").write_text(json.dumps(upstream_meta), encoding="utf-8")
    (candidate / "kernel-metadata.json").write_text(json.dumps(candidate_meta), encoding="utf-8")
    (upstream / "source.ipynb").write_text(json.dumps(notebook([model_code])), encoding="utf-8")
    (candidate / "notebook.ipynb").write_text(
        json.dumps(notebook([model_code, audit_code])), encoding="utf-8"
    )
    sample = tmp_path / "sample_submission.csv"
    sample.write_text("id,tvt\na_0,0\na_1,0\n", encoding="utf-8")
    submission = output / "submission.csv"
    submission.write_text("id,tvt\na_0,1.5\na_1,2.5\n", encoding="utf-8")
    (output / "d35_final_audit.json").write_text(
        json.dumps(
            {
                "submission_sha256": sha256_file(submission),
                "prediction_sha256": prediction_sha(submission),
                "ordered_unique_ids": True,
                "finite_tvt": True,
                "rows": 2,
            }
        ),
        encoding="utf-8",
    )
    (output / "run.log").write_text("completed\n", encoding="utf-8")
    report = build_d35_report(
        candidate_dir=candidate,
        upstream_dir=upstream,
        output_dir=output,
        sample=sample,
        kernel="owner/private",
        version=1,
        competition="rogii-wellbore-geology-prediction",
    )
    assert report["passed"] is True
    assert report["candidate"]["lineage_mode"] == "exact_upstream"

    changed = notebook([model_code + "print('changed')\n", audit_code])
    (candidate / "notebook.ipynb").write_text(json.dumps(changed), encoding="utf-8")
    report = build_d35_report(
        candidate_dir=candidate,
        upstream_dir=upstream,
        output_dir=output,
        sample=sample,
        kernel="owner/private",
        version=1,
        competition="rogii-wellbore-geology-prediction",
    )
    failed = {row["name"]: row["status"] for row in report["checks"]}
    assert failed["exact_upstream_modelling_code"] == "fail"
