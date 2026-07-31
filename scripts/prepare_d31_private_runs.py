"""Prepare audited D31 private Kaggle Code runs.

D31 treats the public leaderboard as a one-quarter sample of the evaluation
set.  The first route is an exact source reproduction of Blacklions' public
Final Hierarch v6 notebook.  Later routes are deliberately limited to
whole-output risk controls and mechanisms that can be justified without
choosing a direction from a single public score.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = (
    ROOT
    / "research"
    / "pulled_20260731"
    / "code_audit"
    / "rogii-wellbore-geology-prediction-final-hierarch"
)
OUT = ROOT / "research" / "pulled_20260731" / "private_runs"
EXPECTED_PREDICTION_SHA = (
    "f9f96622b9d25526a0f32249b29008a104e7ab3cd895c95b7c1aed2c516de6f1"
)
PARENT_FILE_SHAS = {
    "champion": "9196a563e0d578169045816b9adab16af00d4973aa13e04b9e74ed76208f0c4f",
    "d29_nonbranch": "51d31770acfd657d27ad5b4ad07968ce05f2ae3c784f0faa47b74d682d1405eb",
    "d25_a27": "d6096142da6363303f35d719dd86990706dd6c90d59257a110fc9e35464dfff8",
}
STATIC_SPECS = [
    {
        "name": "blend_75_champion_25_d29",
        "slug": "rogii-d31-blend75-champion-d29",
        "title": "ROGII D31 75 Champion 25 D29 Risk Blend",
        "formula": "blend",
        "champion_weight": 0.75,
    },
    {
        "name": "blend_50_champion_50_d29",
        "slug": "rogii-d31-blend50-champion-d29",
        "title": "ROGII D31 50 Champion 50 D29 Risk Blend",
        "formula": "blend",
        "champion_weight": 0.50,
    },
    {
        "name": "blend_25_champion_75_d29",
        "slug": "rogii-d31-blend25-champion-d29",
        "title": "ROGII D31 25 Champion 75 D29 Risk Blend",
        "formula": "blend",
        "champion_weight": 0.25,
    },
    {
        "name": "champion_plus_nonbranch_delta",
        "slug": "rogii-d31-champion-plus-nonbranch-delta",
        "title": "ROGII D31 Champion Plus Measured Nonbranch Delta",
        "formula": "nonbranch_delta",
    },
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def source_text(cell: dict) -> str:
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else source


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


def audit_cell(route: str, expected_prediction_sha: str) -> dict:
    source = f'''# D31 immutable final-output contract (read-only).
import hashlib as _d31_hashlib
import json as _d31_json
from pathlib import Path as _D31Path
import numpy as _d31_np
import pandas as _d31_pd

_D31_ROUTE = {route!r}
_D31_EXPECTED_PREDICTION_SHA = {expected_prediction_sha!r}
_D31_WORK = _D31Path('/kaggle/working') if _D31Path('/kaggle/working').exists() else _D31Path('.')
_D31_SUB = _D31_WORK / 'submission.csv'
_d31_roots = [
    _D31Path('/kaggle/input/competitions/rogii-wellbore-geology-prediction'),
    _D31Path('/kaggle/input/rogii-wellbore-geology-prediction'),
]
if globals().get('CFG') is not None:
    for _d31_attr in ('DATA', 'dataset_path'):
        if hasattr(CFG, _d31_attr):
            _d31_roots.insert(0, _D31Path(getattr(CFG, _d31_attr)))
_D31_SAMPLE = next(
    (_root / 'sample_submission.csv' for _root in _d31_roots
     if (_root / 'sample_submission.csv').exists()),
    None,
)
if _D31_SAMPLE is None:
    raise RuntimeError('D31 contract could not locate sample_submission.csv')
_d31_sub = _d31_pd.read_csv(_D31_SUB)
_d31_sample = _d31_pd.read_csv(_D31_SAMPLE)
if list(_d31_sub.columns) != ['id', 'tvt'] or len(_d31_sub) != 14151 or len(_d31_sample) != 14151:
    raise RuntimeError('D31 invalid columns or row count')
_d31_sub['id'] = _d31_sub['id'].astype(str)
_d31_sample['id'] = _d31_sample['id'].astype(str)
if _d31_sub['id'].duplicated().any() or not _d31_sub['id'].equals(_d31_sample['id']):
    raise RuntimeError('D31 IDs are duplicated or out of sample order')
_d31_pred = _d31_pd.to_numeric(_d31_sub['tvt'], errors='coerce').to_numpy(float)
if not _d31_np.isfinite(_d31_pred).all():
    raise RuntimeError('D31 predictions contain non-finite values')
_d31_prediction_sha = _d31_hashlib.sha256(
    _d31_np.asarray(_d31_pred, dtype='<f8').tobytes()
).hexdigest()
if _D31_EXPECTED_PREDICTION_SHA and _d31_prediction_sha != _D31_EXPECTED_PREDICTION_SHA:
    raise RuntimeError(
        'D31 exact-reproduction prediction SHA mismatch: '
        f'{{_d31_prediction_sha}} != {{_D31_EXPECTED_PREDICTION_SHA}}'
    )
_d31_report = {{
    'route': _D31_ROUTE,
    'rows': int(len(_d31_sub)),
    'ordered_unique_ids': True,
    'finite_tvt': True,
    'expected_prediction_sha256': _D31_EXPECTED_PREDICTION_SHA,
    'prediction_sha256': _d31_prediction_sha,
    'file_sha256': _d31_hashlib.sha256(_D31_SUB.read_bytes()).hexdigest(),
    'tvt_min': float(_d31_pred.min()),
    'tvt_max': float(_d31_pred.max()),
    'tvt_mean': float(_d31_pred.mean()),
    'tvt_std': float(_d31_pred.std()),
}}
(_D31_WORK / 'd31_final_audit.json').write_text(
    _d31_json.dumps(_d31_report, indent=2) + '\\n',
    encoding='utf-8',
)
print('D31 FINAL AUDIT', _d31_report)
'''
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source,
    }


def prepare_exact_public() -> dict:
    source_path = PUBLIC / "rogii-wellbore-geology-prediction-final-hierarch.ipynb"
    original = read_json(source_path)
    notebook = copy.deepcopy(original)
    strip_runtime(notebook)
    notebook["cells"].insert(
        0,
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": (
                "# D31 exact public-source reproduction\n\n"
                "This private Version 1 reproduces Blacklions' public "
                "[Final Hierarch v6](https://www.kaggle.com/code/blacklions/"
                "rogii-wellbore-geology-prediction-final-hierarch) source "
                "without changing its modelling cells or parameters. The "
                "upstream author retains full credit. Its page-reported 6.390 "
                "is treated only as a claim until this account receives its "
                "own score. The appended cell is a read-only output contract.\n"
            ),
        },
    )
    notebook["cells"].append(
        audit_cell("d31_blacklions_v6_exact_source", EXPECTED_PREDICTION_SHA)
    )

    out_dir = OUT / "blacklions_v6_exact"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "notebook.ipynb").write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )

    metadata = read_json(PUBLIC / "kernel-metadata.json")
    metadata.pop("id_no", None)
    metadata.update(
        {
            "id": "muelsyse111/rogii-d31-blacklions-v6-exact-repro",
            "title": "ROGII D31 Blacklions v6 Exact Reproduction",
            "code_file": "notebook.ipynb",
            "is_private": True,
            "enable_internet": False,
        }
    )
    (out_dir / "kernel-metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "route": "blacklions_v6_exact",
        "kernel": metadata["id"],
        "upstream_code_hash": code_hash(original),
        "prepared_upstream_code_hash": code_hash(
            {"cells": notebook["cells"][1:-1]}
        ),
        "expected_prediction_sha256": EXPECTED_PREDICTION_SHA,
    }


def prepare_static(spec: dict) -> dict:
    """Build a fail-closed lightweight private notebook from pinned parents."""
    formula = spec["formula"]
    if formula == "blend":
        weight = float(spec["champion_weight"])
        expression = (
            f"_d31_pred = {weight:.17g} * _d31_champ_v + "
            f"{1.0 - weight:.17g} * _d31_d29_v"
        )
        formula_note = (
            f"{weight:.0%} exact public champion + "
            f"{1.0 - weight:.0%} measured D29 nonbranch route"
        )
    elif formula == "nonbranch_delta":
        expression = "_d31_pred = _d31_champ_v + (_d31_d29_v - _d31_d25_v)"
        formula_note = (
            "exact public champion plus the full measured D29-minus-D25 "
            "nonbranch delta"
        )
    else:
        raise ValueError(formula)

    code = f'''# D31 fail-closed parent resolution and whole-output risk control.
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

WORK = Path('/kaggle/working') if Path('/kaggle/working').exists() else Path('.')
INPUT = Path('/kaggle/input')
EXPECTED = {PARENT_FILE_SHAS!r}

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
        raise RuntimeError(
            f'D31 expected exactly one parent {{expected_sha}}, found {{matches}}'
        )
    return matches[0]

paths = {{name: find_parent(sha) for name, sha in EXPECTED.items()}}
frames = {{name: pd.read_csv(path) for name, path in paths.items()}}
sample_paths = list(INPUT.rglob('sample_submission.csv'))
if not sample_paths:
    raise RuntimeError('D31 could not locate sample_submission.csv')
sample = pd.read_csv(sample_paths[0])
sample['id'] = sample['id'].astype(str)
for name, frame in frames.items():
    frame['id'] = frame['id'].astype(str)
    if (
        list(frame.columns) != ['id', 'tvt']
        or len(frame) != 14151
        or frame['id'].duplicated().any()
        or not frame['id'].equals(sample['id'])
    ):
        raise RuntimeError(f'D31 invalid parent contract: {{name}}')
    values = pd.to_numeric(frame['tvt'], errors='coerce').to_numpy(float)
    if not np.isfinite(values).all():
        raise RuntimeError(f'D31 non-finite parent: {{name}}')

_d31_champ_v = frames['champion']['tvt'].to_numpy(float)
_d31_d29_v = frames['d29_nonbranch']['tvt'].to_numpy(float)
_d31_d25_v = frames['d25_a27']['tvt'].to_numpy(float)
{expression}
if not np.isfinite(_d31_pred).all():
    raise RuntimeError('D31 formula produced non-finite predictions')
submission = sample[['id']].copy()
submission['tvt'] = _d31_pred
submission.to_csv(WORK / 'submission.csv', index=False)

def rms(a, b):
    return float(np.sqrt(np.mean((a - b) ** 2)))

report = {{
    'route': {spec["name"]!r},
    'formula': {formula_note!r},
    'rows': int(len(submission)),
    'ordered_unique_ids': True,
    'finite_tvt': True,
    'parent_paths': {{name: str(path) for name, path in paths.items()}},
    'parent_file_sha256': EXPECTED,
    'file_sha256': file_sha(WORK / 'submission.csv'),
    'prediction_sha256': hashlib.sha256(
        np.asarray(_d31_pred, dtype='<f8').tobytes()
    ).hexdigest(),
    'rms_vs_champion_ft': rms(_d31_pred, _d31_champ_v),
    'rms_vs_d29_ft': rms(_d31_pred, _d31_d29_v),
    'rms_vs_d25_ft': rms(_d31_pred, _d31_d25_v),
    'max_abs_vs_champion_ft': float(np.max(np.abs(_d31_pred - _d31_champ_v))),
}}
(WORK / 'd31_final_audit.json').write_text(
    json.dumps(report, indent=2) + '\\n',
    encoding='utf-8',
)
print('D31 FINAL AUDIT', report)
'''
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": (
                    f"# {spec['title']}\n\n"
                    "A private, fail-closed risk-control derivative. The "
                    "public champion is from Blacklions' Final Hierarch v6; "
                    "the D25/D29 parents are this account's own audited runs "
                    "derived from Raunak Dey's public stack. Upstream authors "
                    "retain credit. The formula was fixed before receiving "
                    "today's leaderboard scores and applies to the complete "
                    "14,151-row output rather than fitting a public-only row "
                    "subset.\n"
                ),
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": code,
            },
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    out_dir = OUT / spec["name"]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "notebook.ipynb").write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    metadata = {
        "id": f"muelsyse111/{spec['slug']}",
        "title": spec["title"],
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
            "blacklions/rogii-wellbore-geology-prediction-final-hierarch",
            "muelsyse111/rogii-d29-a27-nonbranch-shape-r1",
            "muelsyse111/rogii-d25-a27-narrow-smooth",
        ],
        "competition_sources": ["rogii-wellbore-geology-prediction"],
        "model_sources": [],
    }
    (out_dir / "kernel-metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "route": spec["name"],
        "kernel": metadata["id"],
        "formula": formula_note,
        "code_hash": code_hash(notebook),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    reports = [prepare_exact_public()]
    reports.extend(prepare_static(spec) for spec in STATIC_SPECS)
    print(json.dumps(reports, indent=2))


if __name__ == "__main__":
    main()
