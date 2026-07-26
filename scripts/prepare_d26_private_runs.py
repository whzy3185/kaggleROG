"""Prepare the five pre-registered D26 private scoring notebooks.

D25 measured A27 median/mean smoothing windows 15/7 at 6.469, improving the
previous 31/11 result at 6.476, while 61/21 regressed to 6.485. D26 therefore
reserves four slots for a local smoothing-scale grid and one slot for the
genuinely distinct current public A28/Q0522 pair-blend source.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from prepare_d25_private_runs import (
    code_hash,
    notebook_path,
    read_json,
    replace_once,
    strip_runtime,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "pulled_20260726" / "private_runs"
A27_SOURCE = ROOT / "research" / "pulled_20260723" / "raunak_stack"
PAIRBLEND_SOURCE = (
    ROOT / "research" / "pulled_20260726" / "prvsiyan_frontier"
)


SPECS = [
    {
        "name": "pairblend_w050",
        "slug": "rogii-d26-a28-q0522-pairblend-repro",
        "title": "ROGII D26 A28 Q0522 PairBlend Repro",
        "kind": "public",
    },
    {
        "name": "a27_m07_u03",
        "slug": "rogii-d26-a27-smooth-07-03",
        "title": "ROGII D26 A27 Smooth 07 03",
        "kind": "a27",
        "median": 7,
        "mean": 3,
    },
    {
        "name": "a27_m11_u05",
        "slug": "rogii-d26-a27-smooth-11-05",
        "title": "ROGII D26 A27 Smooth 11 05",
        "kind": "a27",
        "median": 11,
        "mean": 5,
    },
    {
        "name": "a27_m13_u07",
        "slug": "rogii-d26-a27-smooth-13-07",
        "title": "ROGII D26 A27 Smooth 13 07",
        "kind": "a27",
        "median": 13,
        "mean": 7,
    },
    {
        "name": "a27_m19_u09",
        "slug": "rogii-d26-a27-smooth-19-09",
        "title": "ROGII D26 A27 Smooth 19 09",
        "kind": "a27",
        "median": 19,
        "mean": 9,
    },
]


def final_audit_cell(route: str) -> dict:
    code = f'''# D26 immutable final-output contract (read-only).
import hashlib as _d26_hashlib
import json as _d26_json
from pathlib import Path as _D26Path
import numpy as _d26_np
import pandas as _d26_pd

_D26_ROUTE = {route!r}
_D26_WORK = _D26Path('/kaggle/working') if _D26Path('/kaggle/working').exists() else _D26Path('.')
_D26_SUB = _D26_WORK / 'submission.csv'
_d26_roots = []
if globals().get('CFG') is not None:
    for _d26_attr in ('DATA', 'dataset_path'):
        if hasattr(CFG, _d26_attr):
            _d26_roots.append(_D26Path(getattr(CFG, _d26_attr)))
_d26_roots.extend([
    _D26Path('/kaggle/input/competitions/rogii-wellbore-geology-prediction'),
    _D26Path('/kaggle/input/rogii-wellbore-geology-prediction'),
])
_D26_SAMPLE = next(
    (_root / 'sample_submission.csv' for _root in _d26_roots
     if (_root / 'sample_submission.csv').exists()),
    None,
)
if _D26_SAMPLE is None:
    raise RuntimeError('D26 contract could not locate sample_submission.csv')
_d26_sub = _d26_pd.read_csv(_D26_SUB)
_d26_sample = _d26_pd.read_csv(_D26_SAMPLE)
if list(_d26_sub.columns) != ['id', 'tvt'] or len(_d26_sub) != 14151 or len(_d26_sample) != 14151:
    raise RuntimeError('D26 invalid columns or row count')
_d26_sub['id'] = _d26_sub['id'].astype(str)
_d26_sample['id'] = _d26_sample['id'].astype(str)
if _d26_sub['id'].duplicated().any() or not _d26_sub['id'].equals(_d26_sample['id']):
    raise RuntimeError('D26 IDs are duplicated or out of sample order')
_d26_pred = _d26_pd.to_numeric(_d26_sub['tvt'], errors='coerce').to_numpy(dtype=float)
if not _d26_np.isfinite(_d26_pred).all():
    raise RuntimeError('D26 predictions contain non-finite values')
_d26_report = {{
    'route': _D26_ROUTE,
    'rows': int(len(_d26_sub)),
    'ordered_unique_ids': True,
    'finite_tvt': True,
    'file_sha256': _d26_hashlib.sha256(_D26_SUB.read_bytes()).hexdigest(),
    'prediction_sha256': _d26_hashlib.sha256(
        _d26_np.asarray(_d26_pred, dtype='<f8').tobytes()
    ).hexdigest(),
    'tvt_min': float(_d26_pred.min()),
    'tvt_max': float(_d26_pred.max()),
    'tvt_mean': float(_d26_pred.mean()),
}}
(_D26_WORK / 'd26_final_audit.json').write_text(
    _d26_json.dumps(_d26_report, indent=2) + '\\n',
    encoding='utf-8',
)
print('D26 FINAL AUDIT', _d26_report)
'''
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": code,
    }


def prepare(spec: dict) -> dict:
    if spec["kind"] == "public":
        source_dir = PAIRBLEND_SOURCE
        intro = (
            f"# {spec['title']}\n\n"
            "Exact current-source private reproduction of prvsiyan's "
            "[`rogii-public-frontier-blend-research-visuals`]"
            "(https://www.kaggle.com/code/prvsiyan/"
            "rogii-public-frontier-blend-research-visuals). Its report cites "
            "a 6.433 public reference, but this run inherits no score claim: "
            "only this account's own audited result will be recorded. The "
            "scoring vector is the run-local 50:50 A28/Q0522 pair blend.\n"
        )
    else:
        source_dir = A27_SOURCE
        intro = (
            f"# {spec['title']}\n\n"
            "Controlled derivative of Raunak Dey's "
            "[`raunakdey07/rogii-stacked-ensemble`]"
            "(https://www.kaggle.com/code/raunakdey07/rogii-stacked-ensemble). "
            "It retains the measured A27 weight 0.10 and 0.35-ft clip and "
            "changes only the centered PF-1.3 smoothing windows to "
            f"{spec['median']}/{spec['mean']}. Source authors retain credit; "
            "only this account's own audited score is reported.\n"
        )

    original = read_json(notebook_path(source_dir))
    notebook = copy.deepcopy(original)
    if spec["kind"] == "a27":
        replace_once(
            notebook,
            "_A27_ROLL_MEDIAN = 31",
            f"_A27_ROLL_MEDIAN = {spec['median']}",
        )
        replace_once(
            notebook,
            "_A27_ROLL_MEAN = 11",
            f"_A27_ROLL_MEAN = {spec['mean']}",
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
    metadata = read_json(source_dir / "kernel-metadata.json")
    metadata.pop("id_no", None)
    metadata.update(
        {
            "id": f"muelsyse111/{spec['slug']}",
            "title": spec["title"],
            "code_file": "notebook.ipynb",
            "is_private": True,
            "enable_gpu": spec["kind"] == "a27",
            "enable_tpu": False,
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
        "kind": spec["kind"],
        "source_code_hash": code_hash(original),
        "prepared_code_hash": code_hash(notebook),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print(json.dumps([prepare(spec) for spec in SPECS], indent=2))


if __name__ == "__main__":
    main()
