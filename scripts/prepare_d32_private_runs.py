"""Prepare full-source private Kaggle Code runs for D32 recovery research.

The non-branch variants clone the scored D29 notebook and rebuild every
prediction in-run. They never mount a prior public ``submission.csv``.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "research" / "pulled_20260801" / "code_audit" / "rogii-geoanchor"
D29_FULL = ROOT / "research" / "pulled_20260729" / "private_runs" / "a27_nonbranch_r1"
OUT = ROOT / "research" / "pulled_20260801" / "private_runs"
GEO_EXPECTED_PRED_SHA = (
    "f68101a235883a67158a42a60929ac41014d4c6f358c494a16ed535a852cb856"
)
PARENT_FILE_SHAS = {
    "d25_a27": "d6096142da6363303f35d719dd86990706dd6c90d59257a110fc9e35464dfff8",
    "d29_nonbranch": "51d31770acfd657d27ad5b4ad07968ce05f2ae3c784f0faa47b74d682d1405eb",
}
SPECS = [
    ("nonbranch_10", "rogii-d32-full-nonbranch10-r1", "ROGII D32 Full Nonbranch10 R1", 2.0),
    ("nonbranch_15", "rogii-d32-full-nonbranch15-gpu-r2", "ROGII D32 Full Nonbranch15 GPU R2", 3.0),
    ("nonbranch_20", "rogii-d32-full-nonbranch20-gpu-r2", "ROGII D32 Full Nonbranch20 GPU R2", 4.0),
    ("nonbranch_30", "rogii-d32-full-nonbranch30-gpu-r2", "ROGII D32 Full Nonbranch30 GPU R2", 6.0),
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


def exact_audit_cell() -> dict:
    source = f'''# D32 immutable exact-reproduction output contract (read-only).
import hashlib as _d32_hashlib
import json as _d32_json
from pathlib import Path as _D32Path
import numpy as _d32_np
import pandas as _d32_pd

_D32_EXPECTED_PRED_SHA = {GEO_EXPECTED_PRED_SHA!r}
_D32_WORK = _D32Path('/kaggle/working') if _D32Path('/kaggle/working').exists() else _D32Path('.')
_D32_SUB = _D32_WORK / 'submission.csv'
_d32_sample_paths = list(_D32Path('/kaggle/input').rglob('sample_submission.csv'))
if not _d32_sample_paths:
    raise RuntimeError('D32 could not locate sample_submission.csv')
_d32_sub = _d32_pd.read_csv(_D32_SUB)
_d32_sample = _d32_pd.read_csv(_d32_sample_paths[0])
_d32_sub['id'] = _d32_sub['id'].astype(str)
_d32_sample['id'] = _d32_sample['id'].astype(str)
if (list(_d32_sub.columns) != ['id', 'tvt'] or len(_d32_sub) != 14151 or
        _d32_sub['id'].duplicated().any() or
        not _d32_sub['id'].equals(_d32_sample['id'])):
    raise RuntimeError('D32 exact reproduction failed the ID contract')
_d32_pred = _d32_pd.to_numeric(_d32_sub['tvt'], errors='coerce').to_numpy(float)
if not _d32_np.isfinite(_d32_pred).all():
    raise RuntimeError('D32 exact reproduction contains non-finite predictions')
_d32_pred_sha = _d32_hashlib.sha256(
    _d32_np.asarray(_d32_pred, dtype='<f8').tobytes()
).hexdigest()
if _d32_pred_sha != _D32_EXPECTED_PRED_SHA:
    raise RuntimeError(
        f'D32 GeoAnchor prediction SHA mismatch: {{_d32_pred_sha}} != '
        f'{{_D32_EXPECTED_PRED_SHA}}'
    )
_d32_report = {{
    'route': 'd32_geoanchor_exact_source',
    'rows': int(len(_d32_sub)),
    'ordered_unique_ids': True,
    'finite_tvt': True,
    'expected_prediction_sha256': _D32_EXPECTED_PRED_SHA,
    'prediction_sha256': _d32_pred_sha,
    'file_sha256': _d32_hashlib.sha256(_D32_SUB.read_bytes()).hexdigest(),
}}
(_D32_WORK / 'd32_final_audit.json').write_text(
    _d32_json.dumps(_d32_report, indent=2) + '\\n', encoding='utf-8'
)
print('D32 FINAL AUDIT', _d32_report)
'''
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source,
    }


def prepare_geoanchor() -> dict:
    metadata = read_json(PUBLIC / "kernel-metadata.json")
    source_path = PUBLIC / metadata["code_file"]
    original = read_json(source_path)
    notebook = copy.deepcopy(original)
    strip_runtime(notebook)
    notebook["cells"].insert(
        0,
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": (
                "# D32 exact GeoAnchor source reproduction\n\n"
                "This private Version 1 reproduces Lucifer19's public "
                "[ROGII GeoAnchor](https://www.kaggle.com/code/lucifer19/"
                "rogii-geoanchor) modelling code and parameters unchanged. "
                "The upstream author retains full credit. Embedded score "
                "claims are not inherited; only this account's measured "
                "result will be reported. The appended cell is read-only.\n"
            ),
        },
    )
    notebook["cells"].append(exact_audit_cell())
    out_dir = OUT / "geoanchor_exact"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "notebook.ipynb").write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    metadata.pop("id_no", None)
    metadata.update(
        {
            "id": "muelsyse111/rogii-d32-geoanchor-exact-reproduction",
            "title": "ROGII D32 GeoAnchor Exact Reproduction",
            "code_file": "notebook.ipynb",
            "is_private": True,
            "enable_internet": False,
        }
    )
    (out_dir / "kernel-metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "route": "geoanchor_exact",
        "kernel": metadata["id"],
        "upstream_code_hash": code_hash(original),
        "prepared_upstream_code_hash": code_hash({"cells": notebook["cells"][1:-1]}),
        "expected_prediction_sha256": GEO_EXPECTED_PRED_SHA,
    }


def prepare_shape(name: str, slug: str, title: str, scale: float) -> dict:
    raise RuntimeError(
        "Retired: static parent-submission notebooks fail Kaggle hidden reruns. "
        "Use prepare_full_shape only."
    )
    percent = int(round(scale * 5))
    source = f'''# D32 fail-closed non-branch shape strength test.
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

WORK = Path('/kaggle/working') if Path('/kaggle/working').exists() else Path('.')
INPUT = Path('/kaggle/input')
EXPECTED = {PARENT_FILE_SHAS!r}
SCALE_FROM_MEASURED_5PCT = {scale!r}
NONBRANCH_WELLS = {{'000d7d20', '00bbac68'}}

def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def find_parent(expected_sha):
    matches = []
    for path in INPUT.rglob('submission.csv'):
        try:
            if file_sha(path) == expected_sha:
                matches.append(path)
        except OSError:
            pass
    if len(matches) != 1:
        raise RuntimeError(f'D32 expected one parent {{expected_sha}}, found {{matches}}')
    return matches[0]

paths = {{name: find_parent(sha) for name, sha in EXPECTED.items()}}
frames = {{name: pd.read_csv(path) for name, path in paths.items()}}
sample_paths = list(INPUT.rglob('sample_submission.csv'))
if not sample_paths:
    raise RuntimeError('D32 could not locate sample_submission.csv')
sample = pd.read_csv(sample_paths[0])
sample['id'] = sample['id'].astype(str)
for key, frame in frames.items():
    frame['id'] = frame['id'].astype(str)
    if (list(frame.columns) != ['id', 'tvt'] or len(frame) != 14151 or
            frame['id'].duplicated().any() or not frame['id'].equals(sample['id'])):
        raise RuntimeError(f'D32 invalid parent contract: {{key}}')

d25 = frames['d25_a27']['tvt'].to_numpy(float)
d29 = frames['d29_nonbranch']['tvt'].to_numpy(float)
well = sample['id'].str.split('_', n=1).str[0]
mask = well.isin(NONBRANCH_WELLS).to_numpy()
pred = d25.copy()
pred[mask] += SCALE_FROM_MEASURED_5PCT * (d29[mask] - d25[mask])
if not np.isfinite(pred).all():
    raise RuntimeError('D32 shape formula produced non-finite values')
submission = sample[['id']].copy()
submission['tvt'] = pred
submission.to_csv(WORK / 'submission.csv', index=False)
written = pd.read_csv(WORK / 'submission.csv')['tvt'].to_numpy(float)

def rms(a, b):
    return float(np.sqrt(np.mean((a - b) ** 2)))

report = {{
    'route': {name!r},
    'nominal_nonbranch_weight_pct': {percent},
    'scale_from_measured_5pct': SCALE_FROM_MEASURED_5PCT,
    'active_wells': sorted(NONBRANCH_WELLS),
    'rows': int(len(submission)),
    'changed_rows': int(np.count_nonzero(written != d25)),
    'ordered_unique_ids': True,
    'finite_tvt': True,
    'parent_paths': {{key: str(path) for key, path in paths.items()}},
    'parent_file_sha256': EXPECTED,
    'file_sha256': file_sha(WORK / 'submission.csv'),
    'prediction_sha256': hashlib.sha256(np.asarray(written, dtype='<f8').tobytes()).hexdigest(),
    'rms_vs_d25_ft': rms(written, d25),
    'rms_vs_d29_ft': rms(written, d29),
    'max_abs_vs_d25_ft': float(np.max(np.abs(written - d25))),
    'branch_well_max_abs_vs_d25_ft': float(np.max(np.abs(written[~mask] - d25[~mask]))),
}}
(WORK / 'd32_final_audit.json').write_text(
    json.dumps(report, indent=2) + '\\n', encoding='utf-8'
)
print('D32 FINAL AUDIT', report)
'''
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": (
                    f"# {title}\n\n"
                    "A pre-registered strength test of the centred non-branch "
                    "shape that measured 6.455 at 5%. The branch well is held "
                    "exactly at the controlled D25 A27 parent, so no constant "
                    "leaderboard-directed shift is introduced. Parents derive "
                    "from Raunak Dey's public stack; upstream credit is retained.\n"
                ),
            },
            {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": source},
        ],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    out_dir = OUT / name
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "notebook.ipynb").write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    metadata = {
        "id": f"muelsyse111/{slug}",
        "title": title,
        "code_file": "notebook.ipynb",
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": False,
        "enable_tpu": False,
        "enable_internet": False,
        "keywords": [],
        "dataset_sources": [],
        "kernel_sources": [
            "muelsyse111/rogii-d25-a27-narrow-smooth",
            "muelsyse111/rogii-d29-a27-nonbranch-shape-r1",
        ],
        "competition_sources": ["rogii-wellbore-geology-prediction"],
        "model_sources": [],
    }
    (out_dir / "kernel-metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {"route": name, "kernel": metadata["id"], "weight_pct": percent, "code_hash": code_hash(notebook)}


def prepare_full_shape(
    name: str,
    slug: str,
    title: str,
    scale: float,
    *,
    out_root: Path | None = None,
    route_label: str | None = None,
) -> dict:
    """Clone the scored D29 full source so hidden wells are rebuilt in-run."""
    percent = int(round(scale * 5))
    weight = percent / 100.0
    clip = 0.18 * scale
    source_path = D29_FULL / "notebook.ipynb"
    original = read_json(source_path)
    notebook = copy.deepcopy(original)
    replace_once(notebook, "_D29N_WEIGHT = 0.05", f"_D29N_WEIGHT = {weight:.2f}")
    replace_once(
        notebook,
        "        -0.18,\n        0.18,",
        f"        -{clip:.2f},\n        {clip:.2f},",
    )
    route_label = route_label or f"d32_full_nonbranch_{percent}"
    replace_once(notebook, "a27_nonbranch_r1", route_label)
    replace_once(
        notebook,
        "len(_d29_sub) != 14151 or len(_d29_sample) != 14151",
        "len(_d29_sub) != len(_d29_sample)",
    )
    notebook["cells"].insert(
        0,
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": (
                f"# {title}\n\n"
                "A full hidden-run-compatible derivative of this account's "
                "measured D29 5% non-branch route. Every upstream modelling "
                "cell is retained; only the centred non-branch weight and its "
                "proportional safety clip change. The PF-selected branch is "
                "excluded dynamically on every evaluation well set. The "
                "underlying stack originates with Raunak Dey, who retains "
                "upstream credit.\n"
            ),
        },
    )
    config_index = next(
        index
        for index, cell in enumerate(notebook["cells"])
        if cell.get("cell_type") == "code"
        and "COMPETITION_DATA_ROOT =" in source_text(cell)
    )
    notebook["cells"].insert(
        config_index + 1,
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": (
                "# Deployment preflight: stop before model construction if the "
                "competition mount is absent.\n"
                "from pathlib import Path as _PreflightPath\n"
                "_preflight_root = _PreflightPath(COMPETITION_DATA_ROOT)\n"
                "_preflight_train = sorted((_preflight_root / 'train').glob("
                "'*__horizontal_well.csv'))\n"
                "_preflight_test = sorted((_preflight_root / 'test').glob("
                "'*__horizontal_well.csv'))\n"
                "_preflight_sample = _preflight_root / 'sample_submission.csv'\n"
                "if not _preflight_train or not _preflight_test or not "
                "_preflight_sample.exists():\n"
                "    raise RuntimeError(\n"
                "        f'competition mount unavailable: root={_preflight_root}, ' "
                "        f'train={len(_preflight_train)}, test={len(_preflight_test)}, ' "
                "        f'sample={_preflight_sample.exists()}'\n"
                "    )\n"
                "print('deployment preflight:', len(_preflight_train), "
                "len(_preflight_test), _preflight_sample)\n"
            ),
        },
    )
    strip_runtime(notebook)
    out_dir = (out_root or OUT) / f"full_{name}"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "notebook.ipynb").write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    metadata = read_json(D29_FULL / "kernel-metadata.json")
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
    (out_dir / "kernel-metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "route": f"full_{name}",
        "kernel": metadata["id"],
        "weight_pct": percent,
        "clip_ft": clip,
        "source_code_hash": code_hash(original),
        "prepared_code_hash": code_hash(notebook),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    reports = [prepare_geoanchor()]
    reports.extend(prepare_full_shape(*spec) for spec in SPECS)
    print(json.dumps(reports, indent=2))


if __name__ == "__main__":
    main()
