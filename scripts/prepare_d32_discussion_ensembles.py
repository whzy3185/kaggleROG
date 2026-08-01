"""Prepare two fail-closed D32 ensembles motivated by Kaggle discussions.

The public leaderboard covers a small fixed well subset.  The remaining D32
slots therefore average materially distinct audited outputs instead of fitting
another one-well direction.  Every parent is resolved by its immutable file
SHA-256, and the final prediction hash is fixed before either slot is used.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "pulled_20260801" / "private_runs"
LOCAL_PARENTS = {
    "d29": ROOT
    / "artifacts"
    / "d29_private_runs"
    / "a27_nonbranch_r1"
    / "submission.csv",
    "geo": OUT / "geoanchor_exact" / "output" / "submission.csv",
    "roman": OUT / "roman_smartest_exact" / "output" / "submission.csv",
    "tamer": OUT / "tamerlan_det_agi_exact" / "output" / "submission.csv",
}
PARENT_FILE_SHAS = {
    "d29": "51d31770acfd657d27ad5b4ad07968ce05f2ae3c784f0faa47b74d682d1405eb",
    "geo": "3d7eaa3e199f7ec07069f722109eff4fdd52090ccc04862695d8e7d955b7f0cc",
    "roman": "2de39613babbc2860b8eefe4e41ea322e8ca9c788a812806a129c9412cd31598",
    "tamer": "27160e23d1e035efd79f2678e73b594b981f27c7496b9d9aae3db5ff85d5a3e4",
}
SPECS = (
    {
        "name": "discussion_consensus4",
        "slug": "rogii-d32-discussion-four-way-consensus",
        "title": "ROGII D32 Discussion Four-Way Consensus",
        "mode": "weighted_mean",
        "parents": ("d29", "geo", "roman", "tamer"),
        "weights": (0.25, 0.25, 0.25, 0.25),
        "reason": (
            "equal-weight consensus of the account's measured D29 best and "
            "three distinct exact public reproductions"
        ),
    },
    {
        "name": "discussion_robust_middle_pair",
        "slug": "rogii-d32-discussion-robust-middle-pair-consensus",
        "title": "ROGII D32 Discussion Robust Middle-Pair Consensus",
        "mode": "median",
        "parents": ("d29", "geo", "roman", "tamer"),
        "weights": None,
        "reason": (
            "row-wise median of four distinct routes, equal to averaging the "
            "middle pair and rejecting the two row-wise extremes"
        ),
    },
)
KERNEL_SOURCES = [
    "muelsyse111/rogii-d29-a27-nonbranch-shape-r1",
    "lucifer19/rogii-geoanchor",
    "romanrozen/rogii-smartest-solution",
    "tamerlanomralinov/hahaha-det-agi",
]


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_local_parents() -> tuple[pd.Series, dict[str, np.ndarray]]:
    sample = pd.read_csv(ROOT / "data" / "raw" / "competition" / "sample_submission.csv")
    sample["id"] = sample["id"].astype(str)
    values: dict[str, np.ndarray] = {}
    for name, path in LOCAL_PARENTS.items():
        if file_sha(path) != PARENT_FILE_SHAS[name]:
            raise RuntimeError(f"Local parent SHA mismatch: {name}")
        frame = pd.read_csv(path)
        frame["id"] = frame["id"].astype(str)
        if (
            list(frame.columns) != ["id", "tvt"]
            or len(frame) != 14151
            or frame["id"].duplicated().any()
            or not frame["id"].equals(sample["id"])
        ):
            raise RuntimeError(f"Local parent contract failed: {name}")
        prediction = pd.to_numeric(frame["tvt"], errors="coerce").to_numpy(float)
        if not np.isfinite(prediction).all():
            raise RuntimeError(f"Local parent contains non-finite values: {name}")
        values[name] = prediction
    return sample["id"], values


def prediction_sha(values: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(values, dtype="<f8").tobytes()).hexdigest()


def rms(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.sqrt(np.mean((left - right) ** 2)))


def notebook_code(spec: dict, expected_prediction_sha: str) -> str:
    return f'''# D32 fail-closed discussion-derived ensemble.
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

WORK = Path('/kaggle/working') if Path('/kaggle/working').exists() else Path('.')
INPUT = Path('/kaggle/input')
EXPECTED_PARENT_SHAS = {PARENT_FILE_SHAS!r}
PARENTS = {spec["parents"]!r}
WEIGHTS = {spec["weights"]!r}
MODE = {spec["mode"]!r}
EXPECTED_PREDICTION_SHA = {expected_prediction_sha!r}

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
            f'D32 expected exactly one parent {{expected_sha}}, found {{matches}}'
        )
    return matches[0]

paths = {{name: find_parent(sha) for name, sha in EXPECTED_PARENT_SHAS.items()}}
sample_paths = list(INPUT.rglob('sample_submission.csv'))
if not sample_paths:
    raise RuntimeError('D32 could not locate sample_submission.csv')
sample = pd.read_csv(sample_paths[0])
sample['id'] = sample['id'].astype(str)
frames = {{name: pd.read_csv(path) for name, path in paths.items()}}
values = {{}}
for name, frame in frames.items():
    frame['id'] = frame['id'].astype(str)
    if (
        list(frame.columns) != ['id', 'tvt']
        or len(frame) != 14151
        or frame['id'].duplicated().any()
        or not frame['id'].equals(sample['id'])
    ):
        raise RuntimeError(f'D32 invalid parent contract: {{name}}')
    values[name] = pd.to_numeric(frame['tvt'], errors='coerce').to_numpy(float)
    if not np.isfinite(values[name]).all():
        raise RuntimeError(f'D32 non-finite parent: {{name}}')

if MODE == 'weighted_mean':
    prediction = sum(weight * values[name] for name, weight in zip(PARENTS, WEIGHTS))
elif MODE == 'median':
    prediction = np.median(np.vstack([values[name] for name in PARENTS]), axis=0)
else:
    raise RuntimeError(f'D32 unknown ensemble mode: {{MODE}}')
if not np.isfinite(prediction).all():
    raise RuntimeError('D32 ensemble produced non-finite predictions')
actual_prediction_sha = hashlib.sha256(
    np.asarray(prediction, dtype='<f8').tobytes()
).hexdigest()
if actual_prediction_sha != EXPECTED_PREDICTION_SHA:
    raise RuntimeError(
        f'D32 prediction SHA mismatch: {{actual_prediction_sha}} != '
        f'{{EXPECTED_PREDICTION_SHA}}'
    )
submission = sample[['id']].copy()
submission['tvt'] = prediction
submission.to_csv(WORK / 'submission.csv', index=False)

def rms(a, b):
    return float(np.sqrt(np.mean((a - b) ** 2)))

report = {{
    'route': {spec["name"]!r},
    'discussion_reason': {spec["reason"]!r},
    'rows': int(len(submission)),
    'ordered_unique_ids': True,
    'finite_tvt': True,
    'parents': PARENTS,
    'mode': MODE,
    'weights': WEIGHTS,
    'parent_paths': {{name: str(path) for name, path in paths.items()}},
    'parent_file_sha256': EXPECTED_PARENT_SHAS,
    'prediction_sha256': actual_prediction_sha,
    'file_sha256': file_sha(WORK / 'submission.csv'),
    'rms_vs_parent_ft': {{name: rms(prediction, value) for name, value in values.items()}},
    'max_abs_vs_parent_ft': {{
        name: float(np.max(np.abs(prediction - value)))
        for name, value in values.items()
    }},
}}
(WORK / 'd32_discussion_audit.json').write_text(
    json.dumps(report, indent=2) + '\\n', encoding='utf-8'
)
print('D32 DISCUSSION FINAL AUDIT', report)
'''


def prepare(spec: dict, parent_values: dict[str, np.ndarray]) -> dict:
    if spec["mode"] == "weighted_mean":
        prediction = sum(
            weight * parent_values[name]
            for name, weight in zip(spec["parents"], spec["weights"])
        )
    elif spec["mode"] == "median":
        prediction = np.median(
            np.vstack([parent_values[name] for name in spec["parents"]]), axis=0
        )
    else:
        raise ValueError(spec["mode"])
    expected_sha = prediction_sha(prediction)
    code = notebook_code(spec, expected_sha)
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": (
                    f"# {spec['title']}\n\n"
                    "This private candidate follows the Discussion guidance to "
                    "trust broad validation, avoid fitting the approximately 52-well "
                    "public slice, and use genuinely different predictions as a risk "
                    "control. It uses only immutable full-output parents and no "
                    "leaderboard-derived row selection. Motivation: "
                    f"{spec['reason']}.\n\n"
                    "Discussion attribution: Tony Li's final-submission thread, "
                    "Tucker Arrants' CV/seed analysis, souldrive's public-ruler "
                    "analysis, Georgy Mamarin's noise-floor analysis, and David "
                    "Rouyre's known-TVT/typewell correction discussion. Public "
                    "notebook authors retain full upstream credit.\n"
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
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
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
        "kernel_sources": KERNEL_SOURCES,
        "competition_sources": ["rogii-wellbore-geology-prediction"],
        "model_sources": [],
    }
    (out_dir / "kernel-metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "route": spec["name"],
        "kernel": metadata["id"],
        "parents": spec["parents"],
        "mode": spec["mode"],
        "weights": spec["weights"],
        "expected_prediction_sha256": expected_sha,
        "rms_vs_parent_ft": {
            name: rms(prediction, values) for name, values in parent_values.items()
        },
    }


def main() -> None:
    _, parent_values = load_local_parents()
    print(json.dumps([prepare(spec, parent_values) for spec in SPECS], indent=2))


if __name__ == "__main__":
    main()
