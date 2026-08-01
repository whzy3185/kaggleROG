from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rogii.notebook_cv_audit import (  # noqa: E402
    audit_full_stack_notebook,
    prepare_leak_safe_diagnostic_copy,
)


def test_d29_full_stack_preflight_fails_closed():
    path = (
        ROOT
        / "research"
        / "pulled_20260729"
        / "private_runs"
        / "a27_nonbranch_r1"
        / "notebook.ipynb"
    )
    report = audit_full_stack_notebook(path)
    assert report["has_grouped_ridge_oof"] is True
    assert report["surface_self_inclusion_calls"] == 2
    assert report["contact_reads_full_truth"] is True
    assert report["locally_scoreable_as_stored"] is False
    assert set(report["blockers"]) == {
        "cv_disabled",
        "surface_self_inclusion",
        "contact_full_truth_offset",
        "missing_deployment_layers",
    }


def test_diagnostic_copy_removes_known_train_side_leaks(tmp_path):
    source = (
        ROOT
        / "research"
        / "pulled_20260729"
        / "private_runs"
        / "a27_nonbranch_r1"
        / "notebook.ipynb"
    )
    output = tmp_path / "leak_safe.ipynb"
    prepare_leak_safe_diagnostic_copy(
        source,
        output,
        n_wells=12,
        selector_seeds=3,
        data_root=ROOT / "data" / "raw" / "competition",
    )
    report = audit_full_stack_notebook(output)
    assert report["full_cv_enabled"] is True
    assert report["surface_self_inclusion_calls"] == 0
    assert report["contact_reads_full_truth"] is False
    assert report["blockers"] == ["missing_deployment_layers"]
    assert report["locally_scoreable_as_stored"] is False
