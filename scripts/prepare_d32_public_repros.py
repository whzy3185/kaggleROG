"""Prepare exact private reproductions of two distinct public ROGII notebooks."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PULLED = ROOT / "research" / "pulled_20260801" / "code_audit"
OUT = ROOT / "research" / "pulled_20260801" / "private_runs"
SPECS = (
    {
        "name": "roman_smartest_exact",
        "source": PULLED / "rogii-smartest-solution",
        "private_id": "muelsyse111/rogii-d32-roman-smartest-exact-reproduction",
        "private_title": "ROGII D32 Roman Smartest Exact Reproduction",
        "author": "Roman Rozen",
        "public_url": "https://www.kaggle.com/code/romanrozen/rogii-smartest-solution",
        "expected_prediction_sha": "cd4cb205a4002daa51916eb252514eb2fddca8e5c584561cc7919e8dfcc6fd5f",
    },
    {
        "name": "tamerlan_det_agi_exact",
        "source": PULLED / "tamerlan-det-agi",
        "private_id": "muelsyse111/rogii-d32-tamerlan-det-agi-exact-reproduction",
        "private_title": "ROGII D32 Tamerlan Det AGI Exact Reproduction",
        "author": "Tamerlan Omralinov",
        "public_url": "https://www.kaggle.com/code/tamerlanomralinov/hahaha-det-agi",
        "expected_prediction_sha": "b88477383b0f374e379386e190add32ee0a22ad0133f5505ded6e37e978693d1",
    },
)


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


def audit_cell(expected_prediction_sha: str, route: str) -> dict:
    source = f'''# D32 immutable public-reproduction output contract (read-only).
import hashlib as _d32_hashlib
import json as _d32_json
from pathlib import Path as _D32Path
import numpy as _d32_np
import pandas as _d32_pd

_D32_EXPECTED_PRED_SHA = {expected_prediction_sha!r}
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
        f'D32 public prediction SHA mismatch: {{_d32_pred_sha}} != {{_D32_EXPECTED_PRED_SHA}}'
    )
_d32_report = {{
    'route': {route!r},
    'rows': int(len(_d32_sub)),
    'ordered_unique_ids': True,
    'finite_tvt': True,
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


def prepare(spec: dict) -> dict:
    metadata_path = spec["source"] / "kernel-metadata.json"
    public_metadata = read_json(metadata_path)
    original = read_json(spec["source"] / public_metadata["code_file"])
    notebook = copy.deepcopy(original)
    strip_runtime(notebook)
    original_code_hash = code_hash(original)
    prepared_public_code_hash = code_hash(notebook)
    if original_code_hash != prepared_public_code_hash:
        raise RuntimeError(f"Public code hash changed while stripping runtime for {spec['name']}")
    notebook["cells"].insert(
        0,
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": (
                f"# {spec['private_title']}\n\n"
                f"This private Version 1 reproduces [{public_metadata['title']}]"
                f"({spec['public_url']}) without changing its public modelling code. "
                f"{spec['author']} retains full upstream credit. Page titles and embedded "
                "score statements are not inherited; only this account's measured result "
                "will be reported. The appended audit cell is read-only.\n"
            ),
        },
    )
    notebook["cells"].append(audit_cell(spec["expected_prediction_sha"], spec["name"]))
    out_dir = OUT / spec["name"]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "notebook.ipynb").write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    private_metadata = copy.deepcopy(public_metadata)
    private_metadata.pop("id_no", None)
    private_metadata.update(
        {
            "id": spec["private_id"],
            "title": spec["private_title"],
            "code_file": "notebook.ipynb",
            "is_private": True,
            "enable_internet": False,
        }
    )
    (out_dir / "kernel-metadata.json").write_text(
        json.dumps(private_metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "route": spec["name"],
        "kernel": spec["private_id"],
        "public_code_hash": original_code_hash,
        "expected_prediction_sha": spec["expected_prediction_sha"],
    }


def main() -> None:
    print(json.dumps([prepare(spec) for spec in SPECS], indent=2))


if __name__ == "__main__":
    main()
