"""Prepare the five pre-registered D24 A27 frontier notebooks.

D23 measured A27 weight 0.10 at 6.476, while the A31 zero-mean Toe tilt
measured 6.546.  D24 brackets the A27 weight and tests two transparent
A27-by-A31 shape composites without reusing the harmful WellBias layer.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "pulled_20260723" / "raunak_stack"
OUT = ROOT / "research" / "pulled_20260724" / "private_runs"


SPECS = [
    ("a27_w008", "rogii-d24-a27-w008", "ROGII D24 A27 W008", 0.08, False),
    ("a27_w012", "rogii-d24-a27-w012", "ROGII D24 A27 W012", 0.12, False),
    ("a27_w015", "rogii-d24-a27-w015", "ROGII D24 A27 W015", 0.15, False),
    ("a27_w010_toe", "rogii-d24-a27-w010-toe", "ROGII D24 A27 W010 Toe", 0.10, True),
    ("a27_w012_toe", "rogii-d24-a27-w012-toe-r1", "ROGII D24 A27 W012 Toe R1", 0.12, True),
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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


def insert_before_final_audit(notebook: dict, cell: dict) -> None:
    indexes = [
        i
        for i, item in enumerate(notebook.get("cells", []))
        if item.get("cell_type") == "code"
        and "# Final submission audit:" in source_text(item)
    ]
    if len(indexes) != 1:
        raise RuntimeError(f"Expected one final audit cell, found {indexes}")
    notebook["cells"].insert(indexes[0], copy.deepcopy(cell))


def toe_tilt_cell() -> dict:
    code = r'''# D24 A31-derived layer: mean-preserving Heel-to-Toe tilt after A27.
# Attribution: yusuketogashi/rogii-another-approch-2nd.
import hashlib as _d24t_hashlib
import json as _d24t_json
from pathlib import Path as _D24TPath
import numpy as _d24t_np
import pandas as _d24t_pd

_D24T_CAP = 0.18
_D24T_TARGET = '00e12e8b'
_D24T_TARGET_ROWS = 4301
_D24T_WORK = _D24TPath('/kaggle/working') if _D24TPath('/kaggle/working').exists() else _D24TPath('.')
_D24T_SUB = _D24T_WORK / 'submission.csv'
_D24T_BRANCH = _D24T_WORK / 'pf_seed_branch_hedge_report.csv'

_d24t_roots = []
if globals().get('CFG') is not None:
    for _d24t_attr in ('DATA', 'dataset_path'):
        if hasattr(CFG, _d24t_attr):
            _d24t_roots.append(_D24TPath(getattr(CFG, _d24t_attr)))
_d24t_roots.extend([
    _D24TPath('/kaggle/input/competitions/rogii-wellbore-geology-prediction'),
    _D24TPath('/kaggle/input/rogii-wellbore-geology-prediction'),
])
_D24T_SAMPLE = next((_r / 'sample_submission.csv' for _r in _d24t_roots if (_r / 'sample_submission.csv').exists()), None)
if _D24T_SAMPLE is None:
    raise RuntimeError('D24 Toe layer could not locate sample_submission.csv')

_d24t_sub = _d24t_pd.read_csv(_D24T_SUB)
_d24t_sample = _d24t_pd.read_csv(_D24T_SAMPLE)
if list(_d24t_sub.columns) != ['id', 'tvt'] or len(_d24t_sub) != 14151:
    raise RuntimeError('D24 Toe layer received an invalid submission')
_d24t_sub['id'] = _d24t_sub['id'].astype(str)
_d24t_sample['id'] = _d24t_sample['id'].astype(str)
if not _d24t_sub['id'].equals(_d24t_sample['id']):
    raise RuntimeError('D24 Toe layer ID order mismatch')
if not _D24T_BRANCH.exists():
    raise RuntimeError('D24 Toe layer missing branch report')
_d24t_branch = _d24t_pd.read_csv(_D24T_BRANCH)
_d24t_applied = _d24t_branch.loc[_d24t_branch['reason'].astype(str).eq('applied')]
if len(_d24t_applied) != 1:
    raise RuntimeError(f'D24 Toe layer expected one applied branch, found {len(_d24t_applied)}')
if str(_d24t_applied.iloc[0]['well']) != _D24T_TARGET or abs(float(_d24t_applied.iloc[0]['shift']) - 2.0) > 1e-9:
    raise RuntimeError('D24 Toe layer found an unexpected source branch')

_d24t_parts = _d24t_sub['id'].str.rsplit('_', n=1, expand=True)
_d24t_well = _d24t_parts[0].astype(str)
_d24t_row = _d24t_pd.to_numeric(_d24t_parts[1], errors='raise').astype(int)
_d24t_mask = _d24t_well.eq(_D24T_TARGET).to_numpy()
if int(_d24t_mask.sum()) != _D24T_TARGET_ROWS:
    raise RuntimeError(f'D24 Toe layer target row mismatch: {int(_d24t_mask.sum())}')
_d24t_order = _d24t_np.argsort(_d24t_row.to_numpy()[_d24t_mask])
_d24t_increment_ordered = _d24t_np.linspace(-_D24T_CAP, _D24T_CAP, _D24T_TARGET_ROWS, dtype=float)
_d24t_increment_ordered -= float(_d24t_increment_ordered.mean())
_d24t_increment = _d24t_np.empty_like(_d24t_increment_ordered)
_d24t_increment[_d24t_order] = _d24t_increment_ordered

_d24t_before = _d24t_sub['tvt'].to_numpy(dtype=float)
_d24t_after = _d24t_before.copy()
_d24t_after[_d24t_mask] += _d24t_increment
if not _d24t_np.isfinite(_d24t_after).all() or abs(float(_d24t_increment.mean())) > 1e-12:
    raise RuntimeError('D24 Toe layer failed finite or zero-mean contract')
_d24t_out = _d24t_sub.copy()
_d24t_out['tvt'] = _d24t_after
_d24t_out.to_csv(_D24T_SUB, index=False)

_d24t_report = {
    'strategy': 'A27 plus A31-derived zero-mean Heel-to-Toe tilt',
    'source_attribution': 'yusuketogashi/rogii-another-approch-2nd',
    'target_well': _D24T_TARGET,
    'target_rows': int(_d24t_mask.sum()),
    'tilt_cap_ft': float(_D24T_CAP),
    'mean_increment_ft': float(_d24t_increment.mean()),
    'max_abs_increment_ft': float(_d24t_np.max(_d24t_np.abs(_d24t_increment))),
    'changed_rows': int(_d24t_np.count_nonzero(_d24t_after != _d24t_before)),
    'final_prediction_sha256': _d24t_hashlib.sha256(_d24t_np.asarray(_d24t_after, dtype='<f8').tobytes()).hexdigest(),
}
(_D24T_WORK / 'd24_toe_tilt_report.json').write_text(_d24t_json.dumps(_d24t_report, indent=2) + '\n', encoding='utf-8')
print('D24 TOE TILT', _d24t_report)
'''
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": code,
    }


def final_audit_cell(route: str, weight: float, toe: bool) -> dict:
    code = f'''# D24 immutable final-output contract (read-only).
import hashlib as _d24_hashlib
import json as _d24_json
from pathlib import Path as _D24Path
import numpy as _d24_np
import pandas as _d24_pd

_D24_ROUTE = {route!r}
_D24_WEIGHT = {weight!r}
_D24_TOE = {toe!r}
_D24_WORK = _D24Path('/kaggle/working') if _D24Path('/kaggle/working').exists() else _D24Path('.')
_D24_SUB = _D24_WORK / 'submission.csv'
_d24_roots = []
if globals().get('CFG') is not None:
    for _d24_attr in ('DATA', 'dataset_path'):
        if hasattr(CFG, _d24_attr):
            _d24_roots.append(_D24Path(getattr(CFG, _d24_attr)))
_d24_roots.extend([_D24Path('/kaggle/input/competitions/rogii-wellbore-geology-prediction'), _D24Path('/kaggle/input/rogii-wellbore-geology-prediction')])
_D24_SAMPLE = next((_r / 'sample_submission.csv' for _r in _d24_roots if (_r / 'sample_submission.csv').exists()), None)
if _D24_SAMPLE is None:
    raise RuntimeError('D24 contract could not locate sample_submission.csv')
_d24_sub = _d24_pd.read_csv(_D24_SUB)
_d24_sample = _d24_pd.read_csv(_D24_SAMPLE)
if list(_d24_sub.columns) != ['id', 'tvt'] or len(_d24_sub) != 14151 or len(_d24_sample) != 14151:
    raise RuntimeError('D24 invalid columns or row count')
_d24_sub['id'] = _d24_sub['id'].astype(str)
_d24_sample['id'] = _d24_sample['id'].astype(str)
if _d24_sub['id'].duplicated().any() or not _d24_sub['id'].equals(_d24_sample['id']):
    raise RuntimeError('D24 IDs are duplicated or out of sample order')
_d24_pred = _d24_pd.to_numeric(_d24_sub['tvt'], errors='coerce').to_numpy(dtype=float)
if not _d24_np.isfinite(_d24_pred).all():
    raise RuntimeError('D24 predictions contain non-finite values')
_d24_report = {{
    'route': _D24_ROUTE, 'a27_weight': _D24_WEIGHT, 'toe_tilt': _D24_TOE,
    'rows': int(len(_d24_sub)), 'ordered_unique_ids': True, 'finite_tvt': True,
    'file_sha256': _d24_hashlib.sha256(_D24_SUB.read_bytes()).hexdigest(),
    'prediction_sha256': _d24_hashlib.sha256(_d24_np.asarray(_d24_pred, dtype='<f8').tobytes()).hexdigest(),
    'tvt_min': float(_d24_pred.min()), 'tvt_max': float(_d24_pred.max()), 'tvt_mean': float(_d24_pred.mean()),
}}
(_D24_WORK / 'd24_final_audit.json').write_text(_d24_json.dumps(_d24_report, indent=2) + '\\n', encoding='utf-8')
print('D24 FINAL AUDIT', _d24_report)
'''
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": code}


def prepare(name: str, slug: str, title: str, weight: float, toe: bool) -> dict:
    source_path = next(SOURCE.glob("*.ipynb"))
    original = read_json(source_path)
    notebook = copy.deepcopy(original)
    replace_once(notebook, "_A27_WEIGHT = 0.10", f"_A27_WEIGHT = {weight:.2f}")
    if toe:
        insert_before_final_audit(notebook, toe_tilt_cell())

    body = (
        "This private scoring experiment starts from Raunak Dey's "
        "[`raunakdey07/rogii-stacked-ensemble`]"
        "(https://www.kaggle.com/code/raunakdey07/rogii-stacked-ensemble), "
        f"whose A27 mechanism measured 6.476 for this account at weight 0.10. "
        f"This route changes only the centered PF-1.3 shape weight to **{weight:.2f}**."
    )
    if toe:
        body += (
            " It then adds the zero-mean 0.18 ft Heel-to-Toe idea from Yusuke Togashi's "
            "[`yusuketogashi/rogii-another-approch-2nd`]"
            "(https://www.kaggle.com/code/yusuketogashi/rogii-another-approch-2nd)."
        )
    body += " Source authors retain credit; only this account's audited run score will be reported."
    notebook["cells"].insert(0, {"cell_type": "markdown", "metadata": {}, "source": f"# {title}\n\n{body}\n"})
    notebook["cells"].append(final_audit_cell(name, weight, toe))
    strip_runtime(notebook)

    out_dir = OUT / name
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "notebook.ipynb").write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    metadata = read_json(SOURCE / "kernel-metadata.json")
    metadata.pop("id_no", None)
    metadata.update({
        "id": f"muelsyse111/{slug}", "title": title, "code_file": "notebook.ipynb",
        "is_private": True, "enable_gpu": True, "enable_internet": False,
    })
    (out_dir / "kernel-metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "name": name, "slug": metadata["id"], "a27_weight": weight, "toe_tilt": toe,
        "source_code_hash": code_hash(original), "prepared_code_hash": code_hash(notebook),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print(json.dumps([prepare(*spec) for spec in SPECS], indent=2))


if __name__ == "__main__":
    main()
