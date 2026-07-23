"""Prepare five attributed, audited private D23 Kaggle notebook runs.

The four controls reproduce genuinely distinct current public outputs.  The
fifth route crosses the strongest local-shape control with the previously
audited grouped-OOF prefix-GR WellBias correction.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PULLED = ROOT / "research" / "pulled_20260723"
OUT = PULLED / "private_runs"


SPECS = [
    {
        "name": "a27_pf13_shape",
        "source": "raunak_stack",
        "slug": "muelsyse111/rogii-d23-a27-pf13-shape",
        "title": "ROGII D23 A27 PF13 Shape",
        "source_id": "raunakdey07/rogii-stacked-ensemble",
        "source_url": "https://www.kaggle.com/code/raunakdey07/rogii-stacked-ensemble",
        "mechanism": "exact A27 control: a centered 10% PF-1.3 shape residual on the single branch-hedged well",
        "wellbias": False,
    },
    {
        "name": "a31_toe_tilt",
        "source": "another2",
        "slug": "muelsyse111/rogii-d23-a31-toe-tilt",
        "title": "ROGII D23 A31 Toe Tilt",
        "source_id": "yusuketogashi/rogii-another-approch-2nd",
        "source_url": "https://www.kaggle.com/code/yusuketogashi/rogii-another-approch-2nd",
        "mechanism": "exact A31 control: a zero-mean 0.18 ft Heel-to-Toe tilt on the single qualified PF branch",
        "wellbias": False,
    },
    {
        "name": "a28_pf13_w062",
        "source": "v32",
        "slug": "muelsyse111/rogii-d23-a28-pf13-w062",
        "title": "ROGII D23 A28 PF13 W062",
        "source_id": "takumashiga/rogii-v32",
        "source_url": "https://www.kaggle.com/code/takumashiga/rogii-v32",
        "mechanism": "exact A28 control: 0.62 SP45 plus 0.38 learned PF-1.3 trajectory",
        "wellbias": False,
    },
    {
        "name": "ucont8",
        "source": "ucont8_probe",
        "slug": "muelsyse111/rogii-d23-u-continuity8",
        "title": "ROGII D23 U-Continuity8",
        "source_id": "ymuroya47/rogii-kdrill-f594-ucont8-public-probe-20260722",
        "source_url": "https://www.kaggle.com/code/ymuroya47/rogii-kdrill-f594-ucont8-public-probe-20260722",
        "mechanism": "exact U-continuity control: cap the TVT+Z handoff correction at 8 ft and fade it over 240 ft MD",
        "wellbias": False,
    },
    {
        "name": "a27_pf13_shape_wellbias",
        "source": "raunak_stack",
        "slug": "muelsyse111/rogii-d23-a27-pf13-wb",
        "title": "ROGII D23 A27 PF13 WB",
        "source_id": "raunakdey07/rogii-stacked-ensemble",
        "source_url": "https://www.kaggle.com/code/raunakdey07/rogii-stacked-ensemble",
        "mechanism": "A27 local shape residual crossed with the audited grouped-OOF prefix-GR WellBias correction",
        "wellbias": True,
    },
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


def markdown(title: str, body: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": f"# {title}\n\n{body}\n",
    }


def wellbias_cell() -> dict:
    source_dir = PULLED.parent / "pulled_20260720" / "private_runs" / "mha160_wellbias"
    notebooks = list(source_dir.glob("*.ipynb"))
    if len(notebooks) != 1:
        raise RuntimeError(f"Expected one WellBias source notebook, found {notebooks}")
    matches = [
        cell
        for cell in read_json(notebooks[0]).get("cells", [])
        if "well-bias overlay complete" in source_text(cell)
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one WellBias cell, found {len(matches)}")
    return copy.deepcopy(matches[0])


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


def d23_audit_cell(route: str) -> dict:
    code = f'''# D23 immutable final-output contract (read-only).
import hashlib as _d23_hashlib
import json as _d23_json
from pathlib import Path as _D23Path
import numpy as _d23_np
import pandas as _d23_pd

_D23_ROUTE = {route!r}
_D23_WORK = _D23Path('/kaggle/working') if _D23Path('/kaggle/working').exists() else _D23Path('.')
_D23_SUB = _D23_WORK / 'submission.csv'
_d23_roots = []
if globals().get('CFG') is not None:
    for _d23_attr in ('DATA', 'dataset_path'):
        if hasattr(CFG, _d23_attr):
            _d23_roots.append(_D23Path(getattr(CFG, _d23_attr)))
_d23_roots.extend([
    _D23Path('/kaggle/input/competitions/rogii-wellbore-geology-prediction'),
    _D23Path('/kaggle/input/rogii-wellbore-geology-prediction'),
])
_D23_SAMPLE = next((_r / 'sample_submission.csv' for _r in _d23_roots if (_r / 'sample_submission.csv').exists()), None)
if _D23_SAMPLE is None:
    raise RuntimeError('D23 contract could not locate sample_submission.csv')
_d23_sub = _d23_pd.read_csv(_D23_SUB)
_d23_sample = _d23_pd.read_csv(_D23_SAMPLE)
if list(_d23_sub.columns) != ['id', 'tvt']:
    raise RuntimeError(f'D23 invalid columns: {{list(_d23_sub.columns)}}')
if len(_d23_sub) != 14151 or len(_d23_sample) != 14151:
    raise RuntimeError(f'D23 invalid row count: {{len(_d23_sub)}} / {{len(_d23_sample)}}')
_d23_sub['id'] = _d23_sub['id'].astype(str)
_d23_sample['id'] = _d23_sample['id'].astype(str)
if _d23_sub['id'].duplicated().any() or not _d23_sub['id'].equals(_d23_sample['id']):
    raise RuntimeError('D23 IDs are duplicated or not in exact sample order')
_d23_pred = _d23_pd.to_numeric(_d23_sub['tvt'], errors='coerce').to_numpy(dtype=float)
if not _d23_np.isfinite(_d23_pred).all():
    raise RuntimeError('D23 predictions contain non-finite values')
_d23_report = {{
    'route': _D23_ROUTE,
    'rows': int(len(_d23_sub)),
    'ordered_unique_ids': True,
    'finite_tvt': True,
    'file_sha256': _d23_hashlib.sha256(_D23_SUB.read_bytes()).hexdigest(),
    'prediction_sha256': _d23_hashlib.sha256(_d23_np.asarray(_d23_pred, dtype='<f8').tobytes()).hexdigest(),
    'tvt_min': float(_d23_pred.min()),
    'tvt_max': float(_d23_pred.max()),
    'tvt_mean': float(_d23_pred.mean()),
}}
(_D23_WORK / 'd23_final_audit.json').write_text(_d23_json.dumps(_d23_report, indent=2) + '\\n', encoding='utf-8')
print('D23 FINAL AUDIT', _d23_report)
'''
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": code,
    }


def prepare(spec: dict) -> dict:
    source_dir = PULLED / spec["source"]
    source_paths = list(source_dir.glob("*.ipynb"))
    if len(source_paths) != 1:
        raise RuntimeError(f"Expected one notebook in {source_dir}, found {source_paths}")
    original = read_json(source_paths[0])
    notebook = copy.deepcopy(original)

    if spec["wellbias"]:
        insert_before_final_audit(notebook, wellbias_cell())

    attribution = (
        f"This private scoring reproduction starts from [{spec['source_id']}]"
        f"({spec['source_url']}). The tested mechanism is: **{spec['mechanism']}**. "
        "The upstream authors retain credit for their pipeline and any score they reported; "
        "this account will report only the score of its own audited Kaggle run."
    )
    if spec["wellbias"]:
        attribution += (
            " The overlay is attributed to Chiekh ALLOUL's "
            "[`chiekhalloul/rogii-det-wellbias-prefix-r1`]"
            "(https://www.kaggle.com/code/chiekhalloul/rogii-det-wellbias-prefix-r1)."
        )
    notebook["cells"].insert(0, markdown(spec["title"], attribution))
    notebook["cells"].append(d23_audit_cell(spec["name"]))
    strip_runtime(notebook)

    out_dir = OUT / spec["name"]
    out_dir.mkdir(parents=True, exist_ok=True)
    code_file = "notebook.ipynb"
    (out_dir / code_file).write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    metadata = read_json(source_dir / "kernel-metadata.json")
    metadata.pop("id_no", None)
    metadata.update(
        {
            "id": spec["slug"],
            "title": spec["title"],
            "code_file": code_file,
            "is_private": True,
            "enable_gpu": True,
            "enable_internet": False,
        }
    )
    (out_dir / "kernel-metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "name": spec["name"],
        "slug": spec["slug"],
        "source_id": spec["source_id"],
        "wellbias": spec["wellbias"],
        "source_code_hash": code_hash(original),
        "prepared_code_hash": code_hash(notebook),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print(json.dumps([prepare(spec) for spec in SPECS], indent=2))


if __name__ == "__main__":
    main()
