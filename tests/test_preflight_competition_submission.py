import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.preflight_competition_submission import (
    _normalise_d29_lineage,
    mounted_submission_hits,
)
from scripts.submit_code_version import enforce_submission_state, load_gate_report


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
