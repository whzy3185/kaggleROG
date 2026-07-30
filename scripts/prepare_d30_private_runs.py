"""Prepare five audited D30 private Kaggle Code runs.

D29 measured 6.541 / 6.517 / 6.560 / 6.455 / 6.530.  The only positive
mechanism was the bounded non-branch shape, but its 0.014 ft gain is below the
pre-registered 0.030 ft parent-promotion threshold.  D30 therefore keeps the
measured D25 A27 15/7 route as the controlled parent and prepares:

1. the exact current public source of Evgendvorkin's highest-score Code page;
2. an A27 route with the likelihood-PF GR scale isolated at 1.60;
3. an execution-stability refresh of the measured D29 non-branch route;
4. a bounded prefix-U drift calibration after A27;
5. non-branch shape plus rowwise agreement-gated prefix-U drift.

Only private Version 1 outputs that pass the final contract are eligible for
competition submission.  Public documentation versions are never eligible.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAUNAK = ROOT / "research" / "pulled_20260723" / "raunak_stack"
EVG = ROOT / "research" / "pulled_20260729" / "code_audit" / "evgendvorkin"
D29_NONBRANCH = (
    ROOT / "research" / "pulled_20260729" / "private_runs" / "a27_nonbranch_r1"
)
OUT = ROOT / "research" / "pulled_20260730" / "private_runs"


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


def make_a27_15_7(dynamic_source_guard: bool = False) -> dict:
    notebook = read_json(notebook_path(RAUNAK))
    replace_once(notebook, "_A27_ROLL_MEDIAN = 31", "_A27_ROLL_MEDIAN = 15")
    replace_once(notebook, "_A27_ROLL_MEAN = 11", "_A27_ROLL_MEAN = 7")
    if dynamic_source_guard:
        replace_once(
            notebook,
            "_A27_EXPECTED_SOURCE_FILE_SHA = "
            "'b192d3f348ae00680dc4df942b95cef5fd708c636a741f77dfb6b6e89b9ded4a'",
            "_A27_EXPECTED_SOURCE_FILE_SHA = None",
        )
        replace_once(
            notebook,
            "_A27_EXPECTED_SOURCE_PRED_SHA = "
            "'5e7b6d65f54498ffc2d071b705385da11e5aa2e6c3a4d16d4a2d7439878ba328'",
            "_A27_EXPECTED_SOURCE_PRED_SHA = None",
        )
        replace_once(
            notebook,
            "_A27_EXPECTED_TARGET = '00e12e8b'",
            "_A27_EXPECTED_TARGET = None",
        )
        replace_once(
            notebook,
            "_A27_EXPECTED_TARGET_ROWS = 4301",
            "_A27_EXPECTED_TARGET_ROWS = None",
        )
        replace_once(
            notebook,
            "if _source_pred_sha != _A27_EXPECTED_SOURCE_PRED_SHA:",
            "if (_A27_EXPECTED_SOURCE_PRED_SHA is not None and "
            "_source_pred_sha != _A27_EXPECTED_SOURCE_PRED_SHA):",
        )
        replace_once(
            notebook,
            "if _target != _A27_EXPECTED_TARGET:",
            "if (_A27_EXPECTED_TARGET is not None and "
            "_target != _A27_EXPECTED_TARGET):",
        )
        replace_once(
            notebook,
            "if int(_mask.sum()) != _A27_EXPECTED_TARGET_ROWS:",
            "if (_A27_EXPECTED_TARGET_ROWS is not None and "
            "int(_mask.sum()) != _A27_EXPECTED_TARGET_ROWS):",
        )
    return notebook


def nonbranch_shape_cell() -> dict:
    return code_cell(
        r'''# D30 measured non-branch shape with an explicit pre-layer snapshot.
import json as _d30n_json
from pathlib import Path as _D30NPath
import numpy as _d30n_np
import pandas as _d30n_pd

_D30N_WEIGHT = 0.05
_D30N_WORK = _D30NPath('/kaggle/working') if _D30NPath('/kaggle/working').exists() else _D30NPath('.')
_D30N_SUB = _D30N_WORK / 'submission.csv'
_D30N_CONTACT = _D30N_WORK / 'submission_before_branch_hedge.csv'
_D30N_LEARNED = _D30N_WORK / 'submission_sp45_learned_w0.60.csv'
_D30N_BRANCH = _D30N_WORK / 'pf_seed_branch_hedge_report.csv'
_d30n_sub = _d30n_pd.read_csv(_D30N_SUB)
_d30n_contact = _d30n_pd.read_csv(_D30N_CONTACT)
_d30n_learned = _d30n_pd.read_csv(_D30N_LEARNED)
if not _d30n_sub['id'].astype(str).equals(_d30n_contact['id'].astype(str)) or not _d30n_sub['id'].astype(str).equals(_d30n_learned['id'].astype(str)):
    raise RuntimeError('D30 nonbranch candidate alignment failure')
_d30n_sub.to_csv(_D30N_WORK / 'submission_before_d30_nonbranch.csv', index=False)
_d30n_branch = _d30n_pd.read_csv(_D30N_BRANCH)
_d30n_applied = set(
    _d30n_branch.loc[_d30n_branch.get('reason', '').astype(str).eq('applied'), 'well'].astype(str)
)
_d30n_well = _d30n_sub['id'].astype(str).str.split('_', n=1).str[0]
_d30n_row = _d30n_pd.to_numeric(
    _d30n_sub['id'].astype(str).str.rsplit('_', n=1).str[-1],
    errors='raise',
).to_numpy(int)
_d30n_tvt = _d30n_pd.to_numeric(_d30n_sub['tvt'], errors='coerce').to_numpy(float)
_d30n_contact_v = _d30n_pd.to_numeric(_d30n_contact['tvt'], errors='coerce').to_numpy(float)
_d30n_learned_v = _d30n_pd.to_numeric(_d30n_learned['tvt'], errors='coerce').to_numpy(float)
_d30n_before = _d30n_tvt.copy()
_d30n_rows = []
for _d30n_wid in sorted(set(_d30n_well) - _d30n_applied):
    _d30n_mask = _d30n_well.eq(_d30n_wid).to_numpy()
    _d30n_order = _d30n_np.argsort(_d30n_row[_d30n_mask])
    _d30n_inverse = _d30n_np.empty_like(_d30n_order)
    _d30n_inverse[_d30n_order] = _d30n_np.arange(len(_d30n_order))
    _d30n_raw = _d30n_np.clip(
        (_d30n_learned_v - _d30n_contact_v)[_d30n_mask][_d30n_order],
        -4.0,
        4.0,
    )
    _d30n_s = _d30n_pd.Series(_d30n_raw)
    _d30n_smooth = (
        _d30n_s.rolling(15, center=True, min_periods=1).median()
        .rolling(7, center=True, min_periods=1).mean()
        .to_numpy(float)
    )
    _d30n_smooth -= float(_d30n_np.mean(_d30n_smooth))
    _d30n_move_ordered = _d30n_np.clip(
        _D30N_WEIGHT * _d30n_smooth,
        -0.18,
        0.18,
    )
    _d30n_move_ordered -= float(_d30n_np.mean(_d30n_move_ordered))
    _d30n_move = _d30n_move_ordered[_d30n_inverse]
    _d30n_tvt[_d30n_mask] += _d30n_move
    _d30n_rows.append({
        'well': _d30n_wid,
        'rows': int(_d30n_mask.sum()),
        'rms_move_ft': float(_d30n_np.sqrt(_d30n_np.mean(_d30n_move ** 2))),
        'max_abs_move_ft': float(_d30n_np.max(_d30n_np.abs(_d30n_move))),
    })
if not _d30n_np.isfinite(_d30n_tvt).all():
    raise RuntimeError('D30 nonbranch shape produced non-finite values')
_d30n_sub['tvt'] = _d30n_tvt
_d30n_sub.to_csv(_D30N_SUB, index=False)
(_D30N_WORK / 'd30_nonbranch_shape_report.json').write_text(
    _d30n_json.dumps({
        'weight': _D30N_WEIGHT,
        'excluded_applied_wells': sorted(_d30n_applied),
        'wells': _d30n_rows,
        'changed_rows': int(_d30n_np.count_nonzero(_d30n_tvt != _d30n_before)),
        'rms_move_ft': float(_d30n_np.sqrt(_d30n_np.mean((_d30n_tvt - _d30n_before) ** 2))),
    }, indent=2) + '\n',
    encoding='utf-8',
)
print('D30 nonbranch shape:', _d30n_rows)
'''
    )


def prefix_drift_cell(agreement_gate: bool) -> dict:
    source = r'''# D30 bounded prefix-U slope continuation.
import json as _d30d_json
from pathlib import Path as _D30DPath
import numpy as _d30d_np
import pandas as _d30d_pd

_D30D_AGREEMENT_GATE = False
_D30D_SHRINK = 0.35
_D30D_CAP = 1.50
_D30D_MIN_PREFIX = 80
_D30D_TAIL_LONG = 160
_D30D_TAIL_SHORT = 80
_D30D_MAX_SLOPE_DISAGREEMENT = 0.010
_D30D_WORK = _D30DPath('/kaggle/working') if _D30DPath('/kaggle/working').exists() else _D30DPath('.')
_D30D_SUB = _D30D_WORK / 'submission.csv'
_d30d_roots = []
if globals().get('CFG') is not None:
    for _d30d_attr in ('DATA', 'dataset_path'):
        if hasattr(CFG, _d30d_attr):
            _d30d_roots.append(_D30DPath(getattr(CFG, _d30d_attr)))
_d30d_roots.extend([
    _D30DPath('/kaggle/input/competitions/rogii-wellbore-geology-prediction'),
    _D30DPath('/kaggle/input/rogii-wellbore-geology-prediction'),
])
_D30D_DATA = next((_r for _r in _d30d_roots if (_r / 'test').exists()), None)
if _D30D_DATA is None:
    raise RuntimeError('D30 drift layer could not locate test data')
_d30d_sub = _d30d_pd.read_csv(_D30D_SUB)
_d30d_well = _d30d_sub['id'].astype(str).str.split('_', n=1).str[0]
_d30d_row = _d30d_pd.to_numeric(
    _d30d_sub['id'].astype(str).str.rsplit('_', n=1).str[-1],
    errors='raise',
).to_numpy(int)
_d30d_tvt = _d30d_pd.to_numeric(_d30d_sub['tvt'], errors='coerce').to_numpy(float)
_d30d_before = _d30d_tvt.copy()
_d30d_shape_delta = None
if _D30D_AGREEMENT_GATE:
    _d30d_pre_path = _D30D_WORK / 'submission_before_d30_nonbranch.csv'
    if not _d30d_pre_path.exists():
        raise RuntimeError('D30 agreement gate missing pre-nonbranch snapshot')
    _d30d_pre = _d30d_pd.read_csv(_d30d_pre_path)
    if not _d30d_sub['id'].astype(str).equals(_d30d_pre['id'].astype(str)):
        raise RuntimeError('D30 agreement snapshot ID mismatch')
    _d30d_shape_delta = (
        _d30d_tvt
        - _d30d_pd.to_numeric(_d30d_pre['tvt'], errors='coerce').to_numpy(float)
    )
_d30d_reports = []
for _d30d_wid in sorted(set(_d30d_well)):
    _d30d_hw = _d30d_pd.read_csv(_D30D_DATA / 'test' / f'{_d30d_wid}__horizontal_well.csv')
    _d30d_known = _d30d_hw['TVT_input'].notna().to_numpy()
    _d30d_known_idx = _d30d_np.flatnonzero(_d30d_known)
    if len(_d30d_known_idx) < _D30D_MIN_PREFIX:
        _d30d_reports.append({'well': _d30d_wid, 'active': False, 'reason': 'short_prefix'})
        continue
    _d30d_mask = _d30d_well.eq(_d30d_wid).to_numpy()
    _d30d_rows = _d30d_row[_d30d_mask]
    _d30d_order = _d30d_np.argsort(_d30d_rows)
    _d30d_rows_o = _d30d_rows[_d30d_order]
    _d30d_md_eval = _d30d_hw.loc[_d30d_rows_o, 'MD'].to_numpy(float)
    _d30d_z_eval = _d30d_hw.loc[_d30d_rows_o, 'Z'].to_numpy(float)
    _d30d_pred_o = _d30d_tvt[_d30d_mask][_d30d_order]
    _d30d_long_idx = _d30d_known_idx[-min(_D30D_TAIL_LONG, len(_d30d_known_idx)):]
    _d30d_short_idx = _d30d_known_idx[-min(_D30D_TAIL_SHORT, len(_d30d_known_idx)):]
    def _d30d_slope(_idx, _values):
        _x = _d30d_hw.loc[_idx, 'MD'].to_numpy(float)
        if len(_x) < 3 or float(_d30d_np.ptp(_x)) <= 1e-9:
            return 0.0
        return float(_d30d_np.polyfit(_x - _x[0], _values, 1)[0])
    _d30d_u_long = (
        _d30d_hw.loc[_d30d_long_idx, 'TVT_input'].to_numpy(float)
        + _d30d_hw.loc[_d30d_long_idx, 'Z'].to_numpy(float)
    )
    _d30d_u_short = (
        _d30d_hw.loc[_d30d_short_idx, 'TVT_input'].to_numpy(float)
        + _d30d_hw.loc[_d30d_short_idx, 'Z'].to_numpy(float)
    )
    _d30d_s_long = _d30d_slope(_d30d_long_idx, _d30d_u_long)
    _d30d_s_short = _d30d_slope(_d30d_short_idx, _d30d_u_short)
    _d30d_prefix_consistent = abs(_d30d_s_long - _d30d_s_short) <= _D30D_MAX_SLOPE_DISAGREEMENT
    _d30d_n_head = min(_D30D_TAIL_SHORT, len(_d30d_rows_o))
    _d30d_u_pred_head = _d30d_pred_o[:_d30d_n_head] + _d30d_z_eval[:_d30d_n_head]
    _d30d_s_pred = (
        float(_d30d_np.polyfit(
            _d30d_md_eval[:_d30d_n_head] - _d30d_md_eval[0],
            _d30d_u_pred_head,
            1,
        )[0])
        if _d30d_n_head >= 3 else 0.0
    )
    _d30d_delta_s = 0.5 * (_d30d_s_long + _d30d_s_short) - _d30d_s_pred
    _d30d_move_o = _d30d_np.clip(
        _D30D_SHRINK * _d30d_delta_s * (_d30d_md_eval - _d30d_md_eval[0]),
        -_D30D_CAP,
        _D30D_CAP,
    )
    _d30d_active = bool(_d30d_prefix_consistent and _d30d_np.max(_d30d_np.abs(_d30d_move_o)) >= 0.02)
    _d30d_gate_rate = 1.0
    if _d30d_active and _D30D_AGREEMENT_GATE:
        _d30d_shape_o = _d30d_shape_delta[_d30d_mask][_d30d_order]
        _d30d_agree = (
            (_d30d_np.abs(_d30d_shape_o) > 1e-9)
            & (_d30d_np.sign(_d30d_shape_o) == _d30d_np.sign(_d30d_move_o))
        )
        _d30d_gate_rate = float(_d30d_np.mean(_d30d_agree))
        _d30d_move_o = _d30d_np.where(_d30d_agree, _d30d_move_o, 0.0)
        _d30d_active = bool(_d30d_np.max(_d30d_np.abs(_d30d_move_o)) >= 0.02)
    if _d30d_active:
        _d30d_target_idx = _d30d_np.flatnonzero(_d30d_mask)[_d30d_order]
        _d30d_tvt[_d30d_target_idx] += _d30d_move_o
    _d30d_reports.append({
        'well': _d30d_wid,
        'active': _d30d_active,
        'prefix_slope_long': _d30d_s_long,
        'prefix_slope_short': _d30d_s_short,
        'predicted_u_slope_head': _d30d_s_pred,
        'slope_delta': _d30d_delta_s,
        'prefix_consistent': bool(_d30d_prefix_consistent),
        'agreement_rate': _d30d_gate_rate,
        'max_abs_move_ft': float(_d30d_np.max(_d30d_np.abs(_d30d_move_o))),
    })
if not _d30d_np.isfinite(_d30d_tvt).all():
    raise RuntimeError('D30 prefix drift produced non-finite values')
_d30d_sub['tvt'] = _d30d_tvt
_d30d_sub.to_csv(_D30D_SUB, index=False)
(_D30D_WORK / 'd30_prefix_drift_report.json').write_text(
    _d30d_json.dumps({
        'agreement_gate': _D30D_AGREEMENT_GATE,
        'shrink': _D30D_SHRINK,
        'cap_ft': _D30D_CAP,
        'wells': _d30d_reports,
        'changed_rows': int(_d30d_np.count_nonzero(_d30d_tvt != _d30d_before)),
        'rms_move_ft': float(_d30d_np.sqrt(_d30d_np.mean((_d30d_tvt - _d30d_before) ** 2))),
    }, indent=2) + '\n',
    encoding='utf-8',
)
print('D30 prefix drift:', _d30d_json.dumps(_d30d_reports, indent=2))
'''
    if agreement_gate:
        source = source.replace(
            "_D30D_AGREEMENT_GATE = False",
            "_D30D_AGREEMENT_GATE = True",
        )
    return code_cell(source)


def final_audit_cell(route: str) -> dict:
    return code_cell(
        f'''# D30 immutable final-output contract.
import hashlib as _d30_hashlib
import json as _d30_json
from pathlib import Path as _D30Path
import numpy as _d30_np
import pandas as _d30_pd

_D30_ROUTE = {route!r}
_D30_WORK = _D30Path('/kaggle/working') if _D30Path('/kaggle/working').exists() else _D30Path('.')
_D30_SUB = _D30_WORK / 'submission.csv'
_d30_roots = []
if globals().get('CFG') is not None:
    for _d30_attr in ('DATA', 'dataset_path'):
        if hasattr(CFG, _d30_attr):
            _d30_roots.append(_D30Path(getattr(CFG, _d30_attr)))
_d30_roots.extend([
    _D30Path('/kaggle/input/competitions/rogii-wellbore-geology-prediction'),
    _D30Path('/kaggle/input/rogii-wellbore-geology-prediction'),
])
_D30_SAMPLE = next(
    (_root / 'sample_submission.csv' for _root in _d30_roots
     if (_root / 'sample_submission.csv').exists()),
    None,
)
if _D30_SAMPLE is None:
    raise RuntimeError('D30 contract could not locate sample_submission.csv')
_d30_sub = _d30_pd.read_csv(_D30_SUB)
_d30_sample = _d30_pd.read_csv(_D30_SAMPLE)
if list(_d30_sub.columns) != ['id', 'tvt'] or len(_d30_sub) != 14151 or len(_d30_sample) != 14151:
    raise RuntimeError('D30 invalid columns or row count')
_d30_sub['id'] = _d30_sub['id'].astype(str)
_d30_sample['id'] = _d30_sample['id'].astype(str)
if _d30_sub['id'].duplicated().any() or not _d30_sub['id'].equals(_d30_sample['id']):
    raise RuntimeError('D30 IDs are duplicated or out of sample order')
_d30_pred = _d30_pd.to_numeric(_d30_sub['tvt'], errors='coerce').to_numpy(float)
if not _d30_np.isfinite(_d30_pred).all():
    raise RuntimeError('D30 predictions contain non-finite values')
_d30_report = {{
    'route': _D30_ROUTE,
    'rows': int(len(_d30_sub)),
    'ordered_unique_ids': True,
    'finite_tvt': True,
    'file_sha256': _d30_hashlib.sha256(_D30_SUB.read_bytes()).hexdigest(),
    'prediction_sha256': _d30_hashlib.sha256(
        _d30_np.asarray(_d30_pred, dtype='<f8').tobytes()
    ).hexdigest(),
    'tvt_min': float(_d30_pred.min()),
    'tvt_max': float(_d30_pred.max()),
    'tvt_mean': float(_d30_pred.mean()),
    'tvt_std': float(_d30_pred.std()),
}}
(_D30_WORK / 'd30_final_audit.json').write_text(
    _d30_json.dumps(_d30_report, indent=2) + '\\n',
    encoding='utf-8',
)
print('D30 FINAL AUDIT', _d30_report)
'''
    )


def metadata_for(source: Path, slug: str, title: str) -> dict:
    metadata = read_json(source / "kernel-metadata.json")
    metadata.pop("id_no", None)
    metadata.update(
        {
            "id": f"muelsyse111/{slug}",
            "title": title,
            "code_file": "notebook.ipynb",
            "is_private": True,
            "enable_gpu": True,
            "enable_internet": False,
        }
    )
    return metadata


def write_run(name: str, notebook: dict, metadata: dict, source_hash: str) -> dict:
    strip_runtime(notebook)
    out_dir = OUT / name
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "notebook.ipynb").write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    (out_dir / "kernel-metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "name": name,
        "slug": metadata["id"],
        "source_code_hash": source_hash,
        "prepared_code_hash": code_hash(notebook),
    }


def prepare_evg_current() -> dict:
    original = read_json(notebook_path(EVG))
    notebook = copy.deepcopy(original)
    notebook["cells"].insert(
        0,
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": (
                "# ROGII D30 Evg Current-Source Control\n\n"
                "Exact current scoring source from "
                "[Evgendvorkin's public notebook](https://www.kaggle.com/code/"
                "evgendvorkin/roggi-physics-lb-7-872-v48). The page-level "
                "historical best score is not inherited; only this account's "
                "private Version 1 score will be reported. Upstream authors "
                "retain credit.\n"
            ),
        },
    )
    notebook["cells"].append(final_audit_cell("evg_current"))
    return write_run(
        "evg_current",
        notebook,
        metadata_for(EVG, "rogii-d30-evg-current-source-control", "ROGII D30 Evg Current Source"),
        code_hash(original),
    )


def prepare_gs16() -> dict:
    notebook = make_a27_15_7(dynamic_source_guard=True)
    original_hash = code_hash(notebook)
    replace_once(
        notebook,
        "gs = float(np.clip(np.nanstd(kn.GR.fillna(0).values - tw_at_k), 10., 60.)) * 1.3",
        "gs = float(np.clip(np.nanstd(kn.GR.fillna(0).values - tw_at_k), 10., 60.)) * 1.6",
    )
    notebook["cells"].insert(
        0,
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": (
                "# ROGII D30 A27 GS1.60 Isolated\n\n"
                "Controlled derivative of Raunak Dey's public stack. It keeps "
                "A27 weight 0.10 and smoothing 15/7 while changing only the "
                "likelihood-PF GR scale multiplier from 1.30 to 1.60. The "
                "branch target and source hashes are discovered from the "
                "run-local private execution rather than fixed visible IDs. "
                "Upstream authors retain credit.\n"
            ),
        },
    )
    notebook["cells"].append(final_audit_cell("a27_gs16"))
    return write_run(
        "a27_gs16",
        notebook,
        metadata_for(
            RAUNAK,
            "rogii-d30-a27-gs160-isolated-r1",
            "ROGII D30 A27 GS160 Isolated R1",
        ),
        original_hash,
    )


def prepare_nonbranch_refresh() -> dict:
    original = read_json(notebook_path(D29_NONBRANCH))
    notebook = copy.deepcopy(original)
    notebook["cells"].insert(
        0,
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": (
                "# ROGII D30 Nonbranch Stability Refresh\n\n"
                "Execution-stability refresh of the D29 non-branch shape route "
                "measured at 6.455. No score is inherited; this private Version "
                "1 tests whether the small gain survives a fresh PF execution. "
                "Raunak Dey and upstream authors retain credit.\n"
            ),
        },
    )
    notebook["cells"].append(final_audit_cell("nonbranch_refresh"))
    return write_run(
        "nonbranch_refresh",
        notebook,
        metadata_for(
            D29_NONBRANCH,
            "rogii-d30-nonbranch-stability-refresh-r1",
            "ROGII D30 Nonbranch Stability Refresh R1",
        ),
        code_hash(original),
    )


def prepare_dual_seedbank() -> dict:
    notebook = make_a27_15_7()
    original_hash = code_hash(notebook)
    replace_once(notebook, "PF_SEEDS = 128", "PF_SEEDS = 256")
    notebook["cells"].insert(
        0,
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": (
                "# ROGII D30 A27 Dual Seed Bank\n\n"
                "Variance-control derivative of Raunak Dey's public stack. "
                "Only the learned likelihood-PF seed count changes from 128 "
                "to 256; particles, selector PF, A27 weight 0.10, smoothing "
                "15/7, and all postprocessing remain fixed. This is the "
                "pre-registered fallback because the current public-frontier "
                "control reproduced a known duplicate output. Upstream authors "
                "retain credit.\n"
            ),
        },
    )
    notebook["cells"].append(final_audit_cell("a27_dual_seedbank"))
    return write_run(
        "a27_dual_seedbank",
        notebook,
        metadata_for(
            RAUNAK,
            "rogii-d30-a27-dual-seed-bank",
            "ROGII D30 A27 Dual Seed Bank",
        ),
        original_hash,
    )


def prepare_prefix_drift() -> dict:
    notebook = make_a27_15_7()
    original_hash = code_hash(notebook)
    insert_after_a27(notebook, [prefix_drift_cell(False)])
    notebook["cells"].insert(
        0,
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": (
                "# ROGII D30 A27 Prefix-U Drift\n\n"
                "A27 15/7 plus a bounded continuation of the run-local visible "
                "prefix U=TVT+Z slope. The slope must agree across 160-row and "
                "80-row tails; correction shrinkage is 0.35 and cap is 1.5 ft. "
                "No fixed test-well ID is used. Upstream authors retain credit.\n"
            ),
        },
    )
    notebook["cells"].append(final_audit_cell("a27_prefix_drift"))
    return write_run(
        "a27_prefix_drift",
        notebook,
        metadata_for(RAUNAK, "rogii-d30-a27-prefix-u-drift", "ROGII D30 A27 Prefix-U Drift"),
        original_hash,
    )


def prepare_agreement() -> dict:
    notebook = make_a27_15_7()
    original_hash = code_hash(notebook)
    insert_after_a27(notebook, [nonbranch_shape_cell(), prefix_drift_cell(True)])
    notebook["cells"].insert(
        0,
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": (
                "# ROGII D30 Nonbranch-Drift Agreement\n\n"
                "A27 15/7 plus the measured 5% non-branch shape. Prefix-U drift "
                "is added only on rows where its sign agrees with the "
                "non-branch correction; all moves remain run-local and capped. "
                "Upstream authors retain credit.\n"
            ),
        },
    )
    notebook["cells"].append(final_audit_cell("nonbranch_drift_agreement"))
    return write_run(
        "nonbranch_drift_agreement",
        notebook,
        metadata_for(
            RAUNAK,
            "rogii-d30-nonbranch-drift-agreement",
            "ROGII D30 Nonbranch Drift Agreement",
        ),
        original_hash,
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    results = [
        prepare_evg_current(),
        prepare_gs16(),
        prepare_nonbranch_refresh(),
        prepare_dual_seedbank(),
        prepare_prefix_drift(),
        prepare_agreement(),
    ]
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
