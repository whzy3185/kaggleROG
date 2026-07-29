"""Prepare five audited D29 private Kaggle Code runs.

D28 measured the refreshed cap2 control at 6.520, A27+Q0522 at 6.486, and
A27+U-continuity8 at 6.576.  D29 returns to the measured A27 15/7 parent and
tests four bounded, run-local mechanisms plus an interaction:

* half-Q branch continuation (+0.261 ft);
* reverse half-Q branch continuation (-0.261 ft);
* a 5% centered learned/contact shape on non-branch wells;
* a short, gated U-boundary fade (cap 2 ft, tau 80 ft MD).

The exact A27 refresh is an execution-stability audit.  If it reproduces the
known D25 artifact, it is not eligible to consume a competition slot.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "pulled_20260723" / "raunak_stack"
OUT = ROOT / "research" / "pulled_20260729" / "private_runs"

SPECS = [
    {
        "name": "a27_exact",
        "slug": "rogii-d29-a27-exact-refresh",
        "title": "ROGII D29 A27 Exact Refresh",
        "q_shift": 0.0,
        "nonbranch": False,
        "boundary": False,
    },
    {
        "name": "a27_q0261",
        "slug": "rogii-d29-a27-dynamic-q0261",
        "title": "ROGII D29 A27 Dynamic Q0261",
        "q_shift": 0.261,
        "nonbranch": False,
        "boundary": False,
    },
    {
        "name": "a27_qneg0261",
        "slug": "rogii-d29-a27-dynamic-qneg0261",
        "title": "ROGII D29 A27 Dynamic Qneg0261",
        "q_shift": -0.261,
        "nonbranch": False,
        "boundary": False,
    },
    {
        "name": "a27_nonbranch_r1",
        "slug": "rogii-d29-a27-nonbranch-shape-r1",
        "title": "ROGII D29 A27 Nonbranch Shape R1",
        "q_shift": 0.0,
        "nonbranch": True,
        "boundary": False,
    },
    {
        "name": "a27_boundary_r1",
        "slug": "rogii-d29-a27-boundary-soft80-r1",
        "title": "ROGII D29 A27 Boundary Soft80 R1",
        "q_shift": 0.0,
        "nonbranch": False,
        "boundary": True,
    },
    {
        "name": "a27_combo",
        "slug": "rogii-d29-a27-q0261-shape-boundary",
        "title": "ROGII D29 A27 Q0261 Shape Boundary",
        "q_shift": 0.261,
        "nonbranch": True,
        "boundary": True,
    },
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def notebook_path(directory: Path) -> Path:
    paths = sorted(directory.glob("*.ipynb"))
    if len(paths) != 1:
        raise RuntimeError(f"Expected one notebook in {directory}, found {paths}")
    return paths[0]


def source_text(cell: dict) -> str:
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else value


def code_hash(notebook: dict) -> str:
    payload = "\n\n".join(
        source_text(cell)
        for cell in notebook.get("cells", [])
        if cell.get("cell_type") == "code"
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def strip_runtime(notebook: dict) -> None:
    notebook.get("metadata", {}).pop("papermill", None)
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
        metadata = cell.get("metadata")
        if isinstance(metadata, dict):
            metadata.pop("execution", None)
            metadata.pop("papermill", None)


def replace_once(notebook: dict, old: str, new: str) -> None:
    count = 0
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        text = source_text(cell)
        found = text.count(old)
        if found:
            cell["source"] = text.replace(old, new)
            count += found
    if count != 1:
        raise RuntimeError(f"Expected one replacement for {old!r}, found {count}")


def code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source,
    }


def insert_after_a27(notebook: dict, cells: list[dict]) -> None:
    indexes = [
        index
        for index, cell in enumerate(notebook.get("cells", []))
        if cell.get("cell_type") == "code"
        and "# A27: restore 10% of the PF-1.3 trajectory shape" in source_text(cell)
    ]
    if len(indexes) != 1:
        raise RuntimeError(f"Expected one A27 scoring cell, found {indexes}")
    position = indexes[0] + 1
    for offset, cell in enumerate(cells):
        notebook["cells"].insert(position + offset, copy.deepcopy(cell))


def q_cell(extra: float) -> dict:
    source = r'''# D29 half-Q continuation, discovered from the run-local branch report.
import json as _d29q_json
from pathlib import Path as _D29QPath
import numpy as _d29q_np
import pandas as _d29q_pd

_D29Q_EXTRA = 0.261
_D29Q_WORK = _D29QPath('/kaggle/working') if _D29QPath('/kaggle/working').exists() else _D29QPath('.')
_D29Q_SUB = _D29Q_WORK / 'submission.csv'
_D29Q_BRANCH = _D29Q_WORK / 'pf_seed_branch_hedge_report.csv'
_d29q_sub = _d29q_pd.read_csv(_D29Q_SUB)
_d29q_report = _d29q_pd.read_csv(_D29Q_BRANCH)
if list(_d29q_sub.columns) != ['id', 'tvt']:
    raise RuntimeError('D29 Q0261 expected id,tvt schema')
_d29q_active = _d29q_report.loc[
    _d29q_report.get('reason', '').astype(str).eq('applied')
].copy()
if len(_d29q_active) < 1:
    raise RuntimeError('D29 Q0261 found no applied branch')
_d29q_well = _d29q_sub['id'].astype(str).str.split('_', n=1).str[0]
_d29q_tvt = _d29q_pd.to_numeric(_d29q_sub['tvt'], errors='coerce').to_numpy(float)
_d29q_before = _d29q_tvt.copy()
_d29q_rows = []
for _d29q_wid in _d29q_active['well'].astype(str):
    _d29q_mask = _d29q_well.eq(_d29q_wid).to_numpy()
    if not bool(_d29q_mask.any()):
        raise RuntimeError(f'D29 Q0261 missing rows for {_d29q_wid}')
    _d29q_tvt[_d29q_mask] += _D29Q_EXTRA
    _d29q_rows.append({'well': _d29q_wid, 'rows': int(_d29q_mask.sum())})
if not _d29q_np.isfinite(_d29q_tvt).all():
    raise RuntimeError('D29 Q0261 produced non-finite values')
_d29q_sub['tvt'] = _d29q_tvt
_d29q_sub.to_csv(_D29Q_SUB, index=False)
(_D29Q_WORK / 'd29_q0261_report.json').write_text(
    _d29q_json.dumps({
        'extra_shift_ft': _D29Q_EXTRA,
        'branches': _d29q_rows,
        'changed_rows': int(_d29q_np.count_nonzero(_d29q_tvt != _d29q_before)),
        'rms_move_ft': float(_d29q_np.sqrt(_d29q_np.mean((_d29q_tvt - _d29q_before) ** 2))),
    }, indent=2) + '\n',
    encoding='utf-8',
)
print('D29 Q0261:', _d29q_rows)
'''
    if extra < 0:
        source = (
            source.replace(
                "# D29 half-Q continuation",
                "# D29 reverse half-Q continuation",
            )
            .replace("_D29Q_EXTRA = 0.261", "_D29Q_EXTRA = -0.261")
            .replace("D29 Q0261", "D29 Qneg0261")
            .replace("d29_q0261_report.json", "d29_qneg0261_report.json")
        )
    return code_cell(source)


def nonbranch_shape_cell() -> dict:
    return code_cell(
        r'''# D29 bounded A27-shape transfer to wells not selected by the PF branch hedge.
import json as _d29n_json
from pathlib import Path as _D29NPath
import numpy as _d29n_np
import pandas as _d29n_pd

_D29N_WEIGHT = 0.05
_D29N_WORK = _D29NPath('/kaggle/working') if _D29NPath('/kaggle/working').exists() else _D29NPath('.')
_D29N_SUB = _D29N_WORK / 'submission.csv'
_D29N_CONTACT = _D29N_WORK / 'submission_before_branch_hedge.csv'
_D29N_LEARNED = _D29N_WORK / 'submission_sp45_learned_w0.60.csv'
_D29N_BRANCH = _D29N_WORK / 'pf_seed_branch_hedge_report.csv'
_d29n_sub = _d29n_pd.read_csv(_D29N_SUB)
_d29n_contact = _d29n_pd.read_csv(_D29N_CONTACT)
_d29n_learned = _d29n_pd.read_csv(_D29N_LEARNED)
if not _d29n_sub['id'].astype(str).equals(_d29n_contact['id'].astype(str)) or not _d29n_sub['id'].astype(str).equals(_d29n_learned['id'].astype(str)):
    raise RuntimeError('D29 nonbranch candidate alignment failure')
_d29n_branch = _d29n_pd.read_csv(_D29N_BRANCH)
_d29n_applied = set(
    _d29n_branch.loc[_d29n_branch.get('reason', '').astype(str).eq('applied'), 'well'].astype(str)
)
_d29n_well = _d29n_sub['id'].astype(str).str.split('_', n=1).str[0]
_d29n_row = _d29n_pd.to_numeric(
    _d29n_sub['id'].astype(str).str.rsplit('_', n=1).str[-1],
    errors='raise',
).to_numpy(int)
_d29n_tvt = _d29n_pd.to_numeric(_d29n_sub['tvt'], errors='coerce').to_numpy(float)
_d29n_contact_v = _d29n_pd.to_numeric(_d29n_contact['tvt'], errors='coerce').to_numpy(float)
_d29n_learned_v = _d29n_pd.to_numeric(_d29n_learned['tvt'], errors='coerce').to_numpy(float)
_d29n_before = _d29n_tvt.copy()
_d29n_rows = []
for _d29n_wid in sorted(set(_d29n_well) - _d29n_applied):
    _d29n_mask = _d29n_well.eq(_d29n_wid).to_numpy()
    _d29n_order = _d29n_np.argsort(_d29n_row[_d29n_mask])
    _d29n_inverse = _d29n_np.empty_like(_d29n_order)
    _d29n_inverse[_d29n_order] = _d29n_np.arange(len(_d29n_order))
    _d29n_raw = _d29n_np.clip(
        (_d29n_learned_v - _d29n_contact_v)[_d29n_mask][_d29n_order],
        -4.0,
        4.0,
    )
    _d29n_s = _d29n_pd.Series(_d29n_raw)
    _d29n_smooth = (
        _d29n_s.rolling(15, center=True, min_periods=1).median()
        .rolling(7, center=True, min_periods=1).mean()
        .to_numpy(float)
    )
    _d29n_smooth -= float(_d29n_np.mean(_d29n_smooth))
    _d29n_move_ordered = _d29n_np.clip(
        _D29N_WEIGHT * _d29n_smooth,
        -0.18,
        0.18,
    )
    _d29n_move_ordered -= float(_d29n_np.mean(_d29n_move_ordered))
    _d29n_move = _d29n_move_ordered[_d29n_inverse]
    _d29n_tvt[_d29n_mask] += _d29n_move
    _d29n_rows.append({
        'well': _d29n_wid,
        'rows': int(_d29n_mask.sum()),
        'rms_move_ft': float(_d29n_np.sqrt(_d29n_np.mean(_d29n_move ** 2))),
        'max_abs_move_ft': float(_d29n_np.max(_d29n_np.abs(_d29n_move))),
    })
if not _d29n_np.isfinite(_d29n_tvt).all():
    raise RuntimeError('D29 nonbranch shape produced non-finite values')
_d29n_sub['tvt'] = _d29n_tvt
_d29n_sub.to_csv(_D29N_SUB, index=False)
(_D29N_WORK / 'd29_nonbranch_shape_report.json').write_text(
    _d29n_json.dumps({
        'weight': _D29N_WEIGHT,
        'excluded_applied_wells': sorted(_d29n_applied),
        'wells': _d29n_rows,
        'changed_rows': int(_d29n_np.count_nonzero(_d29n_tvt != _d29n_before)),
        'rms_move_ft': float(_d29n_np.sqrt(_d29n_np.mean((_d29n_tvt - _d29n_before) ** 2))),
    }, indent=2) + '\n',
    encoding='utf-8',
)
print('D29 nonbranch shape:', _d29n_rows)
'''
    )


def boundary_cell() -> dict:
    return code_cell(
        r'''# D29 short, thresholded continuity fade from the visible U=TVT+Z handoff.
import json as _d29b_json
from pathlib import Path as _D29BPath
import numpy as _d29b_np
import pandas as _d29b_pd

_D29B_THRESHOLD = 0.50
_D29B_CAP = 2.0
_D29B_TAU = 80.0
_D29B_WORK = _D29BPath('/kaggle/working') if _D29BPath('/kaggle/working').exists() else _D29BPath('.')
_D29B_SUB = _D29B_WORK / 'submission.csv'
_d29b_roots = []
if globals().get('CFG') is not None:
    for _d29b_attr in ('DATA', 'dataset_path'):
        if hasattr(CFG, _d29b_attr):
            _d29b_roots.append(_D29BPath(getattr(CFG, _d29b_attr)))
_d29b_roots.extend([
    _D29BPath('/kaggle/input/competitions/rogii-wellbore-geology-prediction'),
    _D29BPath('/kaggle/input/rogii-wellbore-geology-prediction'),
])
_D29B_DATA = next((_r for _r in _d29b_roots if (_r / 'test').exists()), None)
if _D29B_DATA is None:
    raise RuntimeError('D29 boundary layer could not locate test data')
_d29b_sub = _d29b_pd.read_csv(_D29B_SUB)
_d29b_well = _d29b_sub['id'].astype(str).str.split('_', n=1).str[0]
_d29b_row = _d29b_pd.to_numeric(
    _d29b_sub['id'].astype(str).str.rsplit('_', n=1).str[-1],
    errors='raise',
).to_numpy(int)
_d29b_tvt = _d29b_pd.to_numeric(_d29b_sub['tvt'], errors='coerce').to_numpy(float)
_d29b_before = _d29b_tvt.copy()
_d29b_reports = []
for _d29b_wid in sorted(set(_d29b_well)):
    _d29b_hw = _d29b_pd.read_csv(_D29B_DATA / 'test' / f'{_d29b_wid}__horizontal_well.csv')
    _d29b_known = _d29b_hw['TVT_input'].notna().to_numpy()
    if not bool(_d29b_known.any()):
        continue
    _d29b_last = int(_d29b_np.flatnonzero(_d29b_known)[-1])
    _d29b_mask = _d29b_well.eq(_d29b_wid).to_numpy()
    _d29b_rows = _d29b_row[_d29b_mask]
    _d29b_order = _d29b_np.argsort(_d29b_rows)
    _d29b_rows_ordered = _d29b_rows[_d29b_order]
    _d29b_first_row = int(_d29b_rows_ordered[0])
    _d29b_u_last = float(_d29b_hw.loc[_d29b_last, 'TVT_input'] + _d29b_hw.loc[_d29b_last, 'Z'])
    _d29b_values = _d29b_tvt[_d29b_mask][_d29b_order]
    _d29b_z = _d29b_hw.loc[_d29b_rows_ordered, 'Z'].to_numpy(float)
    _d29b_md = _d29b_hw.loc[_d29b_rows_ordered, 'MD'].to_numpy(float)
    _d29b_gap = float(_d29b_values[0] + _d29b_z[0] - _d29b_u_last)
    _d29b_first_move = 0.0
    if abs(_d29b_gap) >= _D29B_THRESHOLD:
        _d29b_first_move = float(-_d29b_np.clip(_d29b_gap, -_D29B_CAP, _D29B_CAP))
        _d29b_move = _d29b_first_move * _d29b_np.exp(-(_d29b_md - _d29b_md[0]) / _D29B_TAU)
        _d29b_new = _d29b_values + _d29b_move
        _d29b_target_idx = _d29b_np.flatnonzero(_d29b_mask)[_d29b_order]
        _d29b_tvt[_d29b_target_idx] = _d29b_new
    _d29b_reports.append({
        'well': _d29b_wid,
        'rows': int(_d29b_mask.sum()),
        'boundary_gap_u_before': _d29b_gap,
        'first_move_ft': _d29b_first_move,
    })
if not _d29b_np.isfinite(_d29b_tvt).all():
    raise RuntimeError('D29 boundary layer produced non-finite values')
_d29b_sub['tvt'] = _d29b_tvt
_d29b_sub.to_csv(_D29B_SUB, index=False)
(_D29B_WORK / 'd29_boundary_soft80_report.json').write_text(
    _d29b_json.dumps({
        'threshold_ft': _D29B_THRESHOLD,
        'cap_ft': _D29B_CAP,
        'tau_md_ft': _D29B_TAU,
        'wells': _d29b_reports,
        'changed_rows': int(_d29b_np.count_nonzero(_d29b_tvt != _d29b_before)),
        'rms_move_ft': float(_d29b_np.sqrt(_d29b_np.mean((_d29b_tvt - _d29b_before) ** 2))),
    }, indent=2) + '\n',
    encoding='utf-8',
)
print('D29 boundary soft80:', _d29b_reports)
'''
    )


def final_audit_cell(route: str) -> dict:
    return code_cell(
        f'''# D29 immutable final-output contract (read-only).
import hashlib as _d29_hashlib
import json as _d29_json
from pathlib import Path as _D29Path
import numpy as _d29_np
import pandas as _d29_pd

_D29_ROUTE = {route!r}
_D29_WORK = _D29Path('/kaggle/working') if _D29Path('/kaggle/working').exists() else _D29Path('.')
_D29_SUB = _D29_WORK / 'submission.csv'
_d29_roots = []
if globals().get('CFG') is not None:
    for _d29_attr in ('DATA', 'dataset_path'):
        if hasattr(CFG, _d29_attr):
            _d29_roots.append(_D29Path(getattr(CFG, _d29_attr)))
_d29_roots.extend([
    _D29Path('/kaggle/input/competitions/rogii-wellbore-geology-prediction'),
    _D29Path('/kaggle/input/rogii-wellbore-geology-prediction'),
])
_D29_SAMPLE = next(
    (_root / 'sample_submission.csv' for _root in _d29_roots
     if (_root / 'sample_submission.csv').exists()),
    None,
)
if _D29_SAMPLE is None:
    raise RuntimeError('D29 contract could not locate sample_submission.csv')
_d29_sub = _d29_pd.read_csv(_D29_SUB)
_d29_sample = _d29_pd.read_csv(_D29_SAMPLE)
if list(_d29_sub.columns) != ['id', 'tvt'] or len(_d29_sub) != 14151 or len(_d29_sample) != 14151:
    raise RuntimeError('D29 invalid columns or row count')
_d29_sub['id'] = _d29_sub['id'].astype(str)
_d29_sample['id'] = _d29_sample['id'].astype(str)
if _d29_sub['id'].duplicated().any() or not _d29_sub['id'].equals(_d29_sample['id']):
    raise RuntimeError('D29 IDs are duplicated or out of sample order')
_d29_pred = _d29_pd.to_numeric(_d29_sub['tvt'], errors='coerce').to_numpy(float)
if not _d29_np.isfinite(_d29_pred).all():
    raise RuntimeError('D29 predictions contain non-finite values')
_d29_report = {{
    'route': _D29_ROUTE,
    'rows': int(len(_d29_sub)),
    'ordered_unique_ids': True,
    'finite_tvt': True,
    'file_sha256': _d29_hashlib.sha256(_D29_SUB.read_bytes()).hexdigest(),
    'prediction_sha256': _d29_hashlib.sha256(
        _d29_np.asarray(_d29_pred, dtype='<f8').tobytes()
    ).hexdigest(),
    'tvt_min': float(_d29_pred.min()),
    'tvt_max': float(_d29_pred.max()),
    'tvt_mean': float(_d29_pred.mean()),
    'tvt_std': float(_d29_pred.std()),
}}
(_D29_WORK / 'd29_final_audit.json').write_text(
    _d29_json.dumps(_d29_report, indent=2) + '\\n',
    encoding='utf-8',
)
print('D29 FINAL AUDIT', _d29_report)
'''
    )


def prepare(spec: dict) -> dict:
    original = read_json(notebook_path(SOURCE))
    notebook = copy.deepcopy(original)
    replace_once(notebook, "_A27_ROLL_MEDIAN = 31", "_A27_ROLL_MEDIAN = 15")
    replace_once(notebook, "_A27_ROLL_MEAN = 11", "_A27_ROLL_MEAN = 7")

    post_cells: list[dict] = []
    q_shift = float(spec.get("q_shift", 0.0))
    if q_shift:
        post_cells.append(q_cell(q_shift))
    if spec["nonbranch"]:
        post_cells.append(nonbranch_shape_cell())
    if spec["boundary"]:
        post_cells.append(boundary_cell())
    if post_cells:
        insert_after_a27(notebook, post_cells)

    enabled = ["A27 15/7 control"]
    if q_shift:
        enabled.append(f"run-local {q_shift:+.3f} ft signed half-Q")
    if spec["nonbranch"]:
        enabled.append("5% centered non-branch shape")
    if spec["boundary"]:
        enabled.append("gated cap-2/tau-80 U-boundary fade")
    intro = (
        f"# {spec['title']}\n\n"
        "Controlled derivative of Raunak Dey's "
        "[`rogii-stacked-ensemble`](https://www.kaggle.com/code/"
        "raunakdey07/rogii-stacked-ensemble). Tested mechanism: **"
        + " + ".join(enabled)
        + "**. The upstream authors retain credit; only this account's own "
        "audited score is reported. This private Version 1 is the only version "
        "eligible for competition submission.\n"
    )
    notebook["cells"].insert(
        0,
        {"cell_type": "markdown", "metadata": {}, "source": intro},
    )
    notebook["cells"].append(final_audit_cell(spec["name"]))
    strip_runtime(notebook)

    out_dir = OUT / spec["name"]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "notebook.ipynb").write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    metadata = read_json(SOURCE / "kernel-metadata.json")
    metadata.pop("id_no", None)
    metadata.update(
        {
            "id": f"muelsyse111/{spec['slug']}",
            "title": spec["title"],
            "code_file": "notebook.ipynb",
            "is_private": True,
            "enable_gpu": True,
            "enable_internet": False,
        }
    )
    (out_dir / "kernel-metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "name": spec["name"],
        "slug": metadata["id"],
        "q_shift": q_shift,
        "nonbranch": spec["nonbranch"],
        "boundary": spec["boundary"],
        "source_code_hash": code_hash(original),
        "prepared_code_hash": code_hash(notebook),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print(json.dumps([prepare(spec) for spec in SPECS], indent=2))


if __name__ == "__main__":
    main()
