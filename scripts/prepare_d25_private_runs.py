"""Prepare five pre-registered D25 private scoring notebooks.

D24 showed that changing only the A27 residual weight or adding the full
0.18-ft Toe ramp did not beat the measured 6.476 A27 result.  D25 therefore
uses two distinct current public-source routes and three controlled A27 shape
ablations that change smoothing or clipping rather than weight.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "pulled_20260725" / "private_runs"
A27_SOURCE = ROOT / "research" / "pulled_20260723" / "raunak_stack"
PUBLIC_SOURCES = {
    "a28_dynq": ROOT / "research" / "pulled_20260725" / "prvsiyan_frontier_blend",
    "gs130_q0522": ROOT / "research" / "pulled_20260725" / "losist_frontier639",
}


SPECS = [
    {
        "name": "a28_dynq",
        "slug": "rogii-d25-a28-dynq0522-noreader",
        "title": "ROGII D25 A28 DYNQ0522 NoReader",
        "kind": "public",
        "attribution": (
            "Exact current-source private reproduction of prvsiyan's "
            "[`rogii-public-frontier-blend-research-visuals`]"
            "(https://www.kaggle.com/code/prvsiyan/"
            "rogii-public-frontier-blend-research-visuals), excluding only its "
            "unavailable Reader checkpoint overlay, which precedes and is "
            "overwritten by the restored A28 candidate."
        ),
    },
    {
        "name": "gs130_q0522",
        "slug": "rogii-d25-gs130-q0522-repro",
        "title": "ROGII D25 GS130 Q0522 Repro",
        "kind": "public",
        "attribution": (
            "Exact current-source private reproduction of LosiSt's "
            "[`rogii-fork-frontier-lab-639`]"
            "(https://www.kaggle.com/code/losist/rogii-fork-frontier-lab-639), "
            "which attributes the 45-cell base to hjyact."
        ),
    },
    {
        "name": "a27_narrow",
        "slug": "rogii-d25-a27-narrow-smooth",
        "title": "ROGII D25 A27 Narrow Smooth",
        "kind": "a27",
        "median": 15,
        "mean": 7,
        "clip": 0.35,
    },
    {
        "name": "a27_wide",
        "slug": "rogii-d25-a27-wide-smooth",
        "title": "ROGII D25 A27 Wide Smooth",
        "kind": "a27",
        "median": 61,
        "mean": 21,
        "clip": 0.35,
    },
    {
        "name": "a27_clip025",
        "slug": "rogii-d25-a27-clip025",
        "title": "ROGII D25 A27 Clip025",
        "kind": "a27",
        "median": 31,
        "mean": 11,
        "clip": 0.25,
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


def remove_code_cell_with_marker(notebook: dict, marker: str) -> None:
    indexes = [
        index
        for index, cell in enumerate(notebook.get("cells", []))
        if cell.get("cell_type") == "code" and marker in source_text(cell)
    ]
    if len(indexes) != 1:
        raise RuntimeError(
            f"Expected one code cell containing {marker!r}, found {indexes}"
        )
    del notebook["cells"][indexes[0]]


def final_audit_cell(route: str) -> dict:
    code = f'''# D25 immutable final-output contract (read-only).
import hashlib as _d25_hashlib
import json as _d25_json
from pathlib import Path as _D25Path
import numpy as _d25_np
import pandas as _d25_pd

_D25_ROUTE = {route!r}
_D25_WORK = _D25Path('/kaggle/working') if _D25Path('/kaggle/working').exists() else _D25Path('.')
_D25_SUB = _D25_WORK / 'submission.csv'
_d25_roots = []
if globals().get('CFG') is not None:
    for _d25_attr in ('DATA', 'dataset_path'):
        if hasattr(CFG, _d25_attr):
            _d25_roots.append(_D25Path(getattr(CFG, _d25_attr)))
_d25_roots.extend([
    _D25Path('/kaggle/input/competitions/rogii-wellbore-geology-prediction'),
    _D25Path('/kaggle/input/rogii-wellbore-geology-prediction'),
])
_D25_SAMPLE = next(
    (_root / 'sample_submission.csv' for _root in _d25_roots
     if (_root / 'sample_submission.csv').exists()),
    None,
)
if _D25_SAMPLE is None:
    raise RuntimeError('D25 contract could not locate sample_submission.csv')
_d25_sub = _d25_pd.read_csv(_D25_SUB)
_d25_sample = _d25_pd.read_csv(_D25_SAMPLE)
if list(_d25_sub.columns) != ['id', 'tvt'] or len(_d25_sub) != 14151 or len(_d25_sample) != 14151:
    raise RuntimeError('D25 invalid columns or row count')
_d25_sub['id'] = _d25_sub['id'].astype(str)
_d25_sample['id'] = _d25_sample['id'].astype(str)
if _d25_sub['id'].duplicated().any() or not _d25_sub['id'].equals(_d25_sample['id']):
    raise RuntimeError('D25 IDs are duplicated or out of sample order')
_d25_pred = _d25_pd.to_numeric(_d25_sub['tvt'], errors='coerce').to_numpy(dtype=float)
if not _d25_np.isfinite(_d25_pred).all():
    raise RuntimeError('D25 predictions contain non-finite values')
_d25_report = {{
    'route': _D25_ROUTE,
    'rows': int(len(_d25_sub)),
    'ordered_unique_ids': True,
    'finite_tvt': True,
    'file_sha256': _d25_hashlib.sha256(_D25_SUB.read_bytes()).hexdigest(),
    'prediction_sha256': _d25_hashlib.sha256(
        _d25_np.asarray(_d25_pred, dtype='<f8').tobytes()
    ).hexdigest(),
    'tvt_min': float(_d25_pred.min()),
    'tvt_max': float(_d25_pred.max()),
    'tvt_mean': float(_d25_pred.mean()),
}}
(_D25_WORK / 'd25_final_audit.json').write_text(
    _d25_json.dumps(_d25_report, indent=2) + '\\n',
    encoding='utf-8',
)
print('D25 FINAL AUDIT', _d25_report)
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
        source_dir = PUBLIC_SOURCES[spec["name"]]
        intro = (
            f"# {spec['title']}\n\n"
            f"{spec['attribution']} The source is reproduced without a scoring "
            "claim; only this account's own audited result will be recorded. "
            "This is a private scoring Version 1 and no later documentation "
            "version may be competition-submitted.\n"
        )
    else:
        source_dir = A27_SOURCE
        intro = (
            f"# {spec['title']}\n\n"
            "Controlled derivative of Raunak Dey's "
            "[`raunakdey07/rogii-stacked-ensemble`]"
            "(https://www.kaggle.com/code/raunakdey07/rogii-stacked-ensemble). "
            "It retains A27 weight 0.10 and changes only the centered PF-1.3 "
            f"shape smoothing to median/mean windows {spec['median']}/"
            f"{spec['mean']} with a {spec['clip']:.2f} ft clip. Source authors "
            "retain credit; only this account's own audited score is reported.\n"
        )

    original = read_json(notebook_path(source_dir))
    notebook = copy.deepcopy(original)
    if spec["name"] == "a28_dynq":
        # The public draft contains a Reader overlay whose ckpt_v3 dataset is
        # absent from its own metadata.  It aborts before the later A28 restore
        # and would be overwritten by that restore even if it ran.  Removing
        # only this unavailable layer preserves the pre-registered
        # A28+DYNQ0522 scoring hypothesis.
        remove_code_cell_with_marker(
            notebook,
            "# ===================== READER OVERLAY",
        )
    elif spec["kind"] == "a27":
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
        replace_once(
            notebook,
            "_move_ordered = _a27_np.clip(_move_ordered, -0.35, 0.35)",
            (
                "_move_ordered = _a27_np.clip("
                f"_move_ordered, -{spec['clip']:.2f}, {spec['clip']:.2f})"
            ),
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
        "kind": spec["kind"],
        "source_code_hash": code_hash(original),
        "prepared_code_hash": code_hash(notebook),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print(json.dumps([prepare(spec) for spec in SPECS], indent=2))


if __name__ == "__main__":
    main()
