"""Prepare the five pre-registered D28 private Kaggle Code runs.

D27 rejected four large structural departures from the measured A27 frontier.
D28 therefore keeps one exact reproduction of the newest public 6.213 claim
and spends the other four slots on controlled extensions of the measured
6.469 A27 route:

* a dynamic +0.522 ft branch-level continuation;
* the independently published U-continuity handoff fade;
* a higher-resolution PF likelihood ensemble;
* the interaction of higher PF resolution, branch continuation, and
  U-continuity.

The public title score is treated only as a source claim.  Every private run
gets a final ordered-ID, finite-value, and SHA-256 contract.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "pulled_20260728" / "private_runs"
LEONID_SOURCE = ROOT / "research" / "pulled_20260728" / "leonid_6213"
A27_SOURCE = ROOT / "research" / "pulled_20260723" / "raunak_stack"
UCONT_SOURCE = ROOT / "research" / "pulled_20260723" / "ucont8_probe"


SPECS = [
    {
        "name": "leonid_6213_exact",
        "slug": "rogii-d28-leonid-6213-exact",
        "title": "ROGII D28 Leonid 6.213 Exact Repro",
        "kind": "public_exact",
        "q0522": False,
        "ucont": False,
        "hires": False,
    },
    {
        "name": "a27_q0522",
        "slug": "rogii-d28-a27-q0522",
        "title": "ROGII D28 A27 plus Dynamic Q0522",
        "kind": "a27",
        "q0522": True,
        "ucont": False,
        "hires": False,
    },
    {
        "name": "a27_ucont8",
        "slug": "rogii-d28-a27-ucont8",
        "title": "ROGII D28 A27 plus U-Continuity8",
        "kind": "a27",
        "q0522": False,
        "ucont": True,
        "hires": False,
    },
    {
        "name": "a27_pf192p650",
        "slug": "rogii-d28-a27-pf192p650-r1",
        "title": "ROGII D28 A27 PF192 P650 R1",
        "kind": "a27",
        "q0522": False,
        "ucont": False,
        "hires": True,
    },
    {
        "name": "a27_pf192_q_u",
        "slug": "rogii-d28-a27-pf192-q-u-r1",
        "title": "ROGII D28 A27 PF192 Q0522 UCont R1",
        "kind": "a27",
        "q0522": True,
        "ucont": True,
        "hires": True,
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
    pos = indexes[0] + 1
    for offset, cell in enumerate(cells):
        notebook["cells"].insert(pos + offset, copy.deepcopy(cell))


def q0522_cell() -> dict:
    return code_cell(
        r'''# D28 dynamic Q0522 continuation after the centered A27 shape move.
# The applied branch is discovered from the run-local PF report; no visible
# well ID is embedded in this transaction.
import json as _d28q_json
from pathlib import Path as _D28QPath
import numpy as _d28q_np
import pandas as _d28q_pd

_D28Q_EXTRA = 0.522
_D28Q_WORK = _D28QPath('/kaggle/working') if _D28QPath('/kaggle/working').exists() else _D28QPath('.')
_D28Q_SUB = _D28Q_WORK / 'submission.csv'
_D28Q_REPORT = _D28Q_WORK / 'pf_seed_branch_hedge_report.csv'
if not _D28Q_SUB.exists() or not _D28Q_REPORT.exists():
    raise RuntimeError('D28 Q0522 requires submission.csv and the PF branch report')

_d28q_sub = _d28q_pd.read_csv(_D28Q_SUB)
_d28q_br = _d28q_pd.read_csv(_D28Q_REPORT)
if list(_d28q_sub.columns) != ['id', 'tvt']:
    raise RuntimeError('D28 Q0522 expected id,tvt submission schema')
_d28q_applied = _d28q_br.loc[
    _d28q_br.get('reason', '').astype(str).eq('applied')
].copy()
if len(_d28q_applied) < 1:
    raise RuntimeError('D28 Q0522 found no run-local applied PF branch')

_d28q_well = _d28q_sub['id'].astype(str).str.split('_', n=1).str[0]
_d28q_row = _d28q_pd.to_numeric(
    _d28q_sub['id'].astype(str).str.rsplit('_', n=1).str[-1],
    errors='raise',
).astype(int)
_d28q_tvt = _d28q_pd.to_numeric(
    _d28q_sub['tvt'], errors='coerce'
).to_numpy(dtype=float)
_d28q_before = _d28q_tvt.copy()
_d28q_rows = []
for _, _d28q_info in _d28q_applied.iterrows():
    _d28q_wid = str(_d28q_info['well'])
    _d28q_mask = _d28q_well.eq(_d28q_wid).to_numpy()
    _d28q_eval = _d28q_info.get('eval_rows')
    if isinstance(_d28q_eval, str) and _d28q_eval.strip():
        try:
            _d28q_eval_values = set(int(x) for x in _d28q_json.loads(_d28q_eval))
            _d28q_mask &= _d28q_row.isin(_d28q_eval_values).to_numpy()
        except Exception:
            pass
    if not bool(_d28q_mask.any()):
        raise RuntimeError(f'D28 Q0522 branch { _d28q_wid } has no submission rows')
    _d28q_tvt[_d28q_mask] += _D28Q_EXTRA
    _d28q_rows.append({
        'well': _d28q_wid,
        'rows': int(_d28q_mask.sum()),
        'extra_shift_ft': float(_D28Q_EXTRA),
    })

if not _d28q_np.isfinite(_d28q_tvt).all():
    raise RuntimeError('D28 Q0522 produced non-finite predictions')
_d28q_sub['tvt'] = _d28q_tvt
_d28q_sub.to_csv(_D28Q_SUB, index=False)
(_D28Q_WORK / 'd28_q0522_report.json').write_text(
    _d28q_json.dumps({
        'strategy': 'run-local applied PF branches plus 0.522 ft after A27',
        'branches': _d28q_rows,
        'changed_rows': int(_d28q_np.count_nonzero(_d28q_tvt != _d28q_before)),
        'rms_move_ft': float(_d28q_np.sqrt(_d28q_np.mean((_d28q_tvt - _d28q_before) ** 2))),
    }, indent=2) + '\n',
    encoding='utf-8',
)
print('D28 dynamic Q0522:', _d28q_rows)
'''
    )


def ucont_cell() -> dict:
    source = read_json(notebook_path(UCONT_SOURCE))
    matches = [
        cell
        for cell in source.get("cells", [])
        if cell.get("cell_type") == "code"
        and "# Target-free post-composition U-continuity fade." in source_text(cell)
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one U-continuity cell, found {len(matches)}")
    return copy.deepcopy(matches[0])


def final_audit_cell(route: str) -> dict:
    return code_cell(
        f'''# D28 immutable final-output contract (read-only).
import hashlib as _d28_hashlib
import json as _d28_json
from pathlib import Path as _D28Path
import numpy as _d28_np
import pandas as _d28_pd

_D28_ROUTE = {route!r}
_D28_WORK = _D28Path('/kaggle/working') if _D28Path('/kaggle/working').exists() else _D28Path('.')
_D28_SUB = _D28_WORK / 'submission.csv'
_d28_roots = []
if globals().get('CFG') is not None:
    for _d28_attr in ('DATA', 'dataset_path'):
        if hasattr(CFG, _d28_attr):
            _d28_roots.append(_D28Path(getattr(CFG, _d28_attr)))
_d28_roots.extend([
    _D28Path('/kaggle/input/competitions/rogii-wellbore-geology-prediction'),
    _D28Path('/kaggle/input/rogii-wellbore-geology-prediction'),
])
_D28_SAMPLE = next(
    (_root / 'sample_submission.csv' for _root in _d28_roots
     if (_root / 'sample_submission.csv').exists()),
    None,
)
if _D28_SAMPLE is None:
    raise RuntimeError('D28 contract could not locate sample_submission.csv')
_d28_sub = _d28_pd.read_csv(_D28_SUB)
_d28_sample = _d28_pd.read_csv(_D28_SAMPLE)
if list(_d28_sub.columns) != ['id', 'tvt'] or len(_d28_sub) != 14151 or len(_d28_sample) != 14151:
    raise RuntimeError('D28 invalid columns or row count')
_d28_sub['id'] = _d28_sub['id'].astype(str)
_d28_sample['id'] = _d28_sample['id'].astype(str)
if _d28_sub['id'].duplicated().any() or not _d28_sub['id'].equals(_d28_sample['id']):
    raise RuntimeError('D28 IDs are duplicated or out of sample order')
_d28_pred = _d28_pd.to_numeric(_d28_sub['tvt'], errors='coerce').to_numpy(dtype=float)
if not _d28_np.isfinite(_d28_pred).all():
    raise RuntimeError('D28 predictions contain non-finite values')
_d28_report = {{
    'route': _D28_ROUTE,
    'rows': int(len(_d28_sub)),
    'ordered_unique_ids': True,
    'finite_tvt': True,
    'file_sha256': _d28_hashlib.sha256(_D28_SUB.read_bytes()).hexdigest(),
    'prediction_sha256': _d28_hashlib.sha256(
        _d28_np.asarray(_d28_pred, dtype='<f8').tobytes()
    ).hexdigest(),
    'tvt_min': float(_d28_pred.min()),
    'tvt_max': float(_d28_pred.max()),
    'tvt_mean': float(_d28_pred.mean()),
    'tvt_std': float(_d28_pred.std()),
}}
(_D28_WORK / 'd28_final_audit.json').write_text(
    _d28_json.dumps(_d28_report, indent=2) + '\\n',
    encoding='utf-8',
)
print('D28 FINAL AUDIT', _d28_report)
'''
    )


def prepare(spec: dict) -> dict:
    if spec["kind"] == "public_exact":
        source_dir = LEONID_SOURCE
        intro = (
            f"# {spec['title']}\n\n"
            "Exact current-source private reproduction of Leonid Zaporozhets' "
            "[`new-strategy-score-6-213`](https://www.kaggle.com/code/"
            "leonidzaporozhets/new-strategy-score-6-213). The title's 6.213 "
            "is retained only as an upstream claim: this account reports only "
            "its own audited score. The source differs from the earlier "
            "high-scoring-reproducible control by reducing the balanced "
            "visible-prefix cap from 0.40 to 0.36 and clip maximum from 30 to "
            "28. No scoring code is otherwise changed.\n"
        )
    else:
        source_dir = A27_SOURCE
        labels = ["measured A27 15/7 shape"]
        if spec["hires"]:
            labels.append("192-seed / 650-particle PF likelihood ensemble")
        if spec["q0522"]:
            labels.append("run-local +0.522 ft applied-branch continuation")
        if spec["ucont"]:
            labels.append("target-free U-continuity8 handoff fade")
        intro = (
            f"# {spec['title']}\n\n"
            "Controlled derivative of Raunak Dey's "
            "[`rogii-stacked-ensemble`](https://www.kaggle.com/code/"
            "raunakdey07/rogii-stacked-ensemble), with the U-continuity layer "
            "attributed to ymuroya47 when enabled. Tested mechanism: **"
            + " + ".join(labels)
            + "**. The source authors retain credit; only this account's own "
            "audited score is reported.\n"
        )

    original = read_json(notebook_path(source_dir))
    notebook = copy.deepcopy(original)
    if spec["kind"] == "a27":
        replace_once(notebook, "_A27_ROLL_MEDIAN = 31", "_A27_ROLL_MEDIAN = 15")
        replace_once(notebook, "_A27_ROLL_MEAN = 11", "_A27_ROLL_MEAN = 7")
        if spec["hires"]:
            replace_once(
                notebook,
                "SP45_SELECTOR_N_PARTICLES = 500",
                "SP45_SELECTOR_N_PARTICLES = 650",
            )
            replace_once(
                notebook,
                "SP45_SELECTOR_N_SEEDS = 128",
                "SP45_SELECTOR_N_SEEDS = 192",
            )
            # The high-resolution PF changes the run-local cap2 anchor before
            # A27.  Preserve the source guard by pinning the independently
            # observed 192-seed / 650-particle prediction hash instead of
            # weakening or removing the contract.
            replace_once(
                notebook,
                "_A27_EXPECTED_SOURCE_PRED_SHA = '5e7b6d65f54498ffc2d071b705385da11e5aa2e6c3a4d16d4a2d7439878ba328'",
                "_A27_EXPECTED_SOURCE_PRED_SHA = 'efd9c82f64b06cbd70aa762d8cb6502ba24da560549b5a98fe41a4a29be2b9d2'",
            )
        post_cells = []
        if spec["q0522"]:
            post_cells.append(q0522_cell())
        if spec["ucont"]:
            post_cells.append(ucont_cell())
        if post_cells:
            insert_after_a27(notebook, post_cells)

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
        "q0522": spec["q0522"],
        "ucont": spec["ucont"],
        "hires": spec["hires"],
        "source_code_hash": code_hash(original),
        "prepared_code_hash": code_hash(notebook),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print(json.dumps([prepare(spec) for spec in SPECS], indent=2))


if __name__ == "__main__":
    main()
