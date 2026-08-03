#!/usr/bin/env python3
"""Prepare D35 full-source private reproductions with a dynamic output audit.

The upstream modelling cells are copied unchanged.  We add only attribution
markdown and a final read-only contract cell.  Public ``submission.csv`` files
are research references and are never mounted as prediction parents.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "artifacts" / "d35_sources"
OUT = ROOT / "research" / "pulled_20260803" / "private_runs"

SPECS = (
    (
        "v4_exact",
        "rogii-solution-on-6-390-in-lb",
        "daniilkrasnovvv/rogii-solution-on-6-390-in-lb",
        "rogii-d35-v4-exact-full-source",
        "ROGII D35 V4 Exact Full Source",
    ),
    (
        "raunak_stack",
        "rogii-stacked-ensemble",
        "raunakdey07/rogii-stacked-ensemble",
        "rogii-d35-raunak-stack-full-source",
        "ROGII D35 Raunak Stack Full Source",
    ),
    (
        "frontier_blend",
        "rogii-public-frontier-blend-research-visuals",
        "prvsiyan/rogii-public-frontier-blend-research-visuals",
        "rogii-d35-frontier-blend-full-source",
        "ROGII D35 Frontier Blend Full Source",
    ),
    (
        "final_hierarchy",
        "rogii-final-hierarchy",
        "blacklions/rogii-wellbore-geology-prediction-final-hierarch",
        "rogii-d35-final-hierarchy-full-source",
        "ROGII D35 Final Hierarchy Full Source",
    ),
    (
        "shift275",
        "rogii-shift-275",
        "zhexinjiang/rogii-shift-275",
        "rogii-d35-shift-275-full-source",
        "ROGII D35 Shift 275 Full Source",
    ),
)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def source_text(cell: dict) -> str:
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def code_sha(notebook: dict) -> str:
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
            cell["execution_count"] = None
            cell["outputs"] = []
        metadata = cell.get("metadata")
        if isinstance(metadata, dict):
            metadata.pop("execution", None)
            metadata.pop("papermill", None)


def audit_cell(route: str, upstream: str, upstream_code_sha: str) -> dict:
    source = f'''# D35 dynamic hidden-run output contract (read-only).
import hashlib as _d35_hashlib
import json as _d35_json
from pathlib import Path as _D35Path
import numpy as _d35_np
import pandas as _d35_pd

_D35_ROUTE = {route!r}
_D35_UPSTREAM = {upstream!r}
_D35_UPSTREAM_CODE_SHA = {upstream_code_sha!r}
_D35_WORK = _D35Path('/kaggle/working') if _D35Path('/kaggle/working').exists() else _D35Path('.')
_D35_SUB = _D35_WORK / 'submission.csv'
_d35_roots = (
    _D35Path('/kaggle/input/competitions/rogii-wellbore-geology-prediction'),
    _D35Path('/kaggle/input/rogii-wellbore-geology-prediction'),
)
_d35_samples = [p / 'sample_submission.csv' for p in _d35_roots if (p / 'sample_submission.csv').exists()]
if len(_d35_samples) != 1:
    raise RuntimeError(f'D35 expected one official sample_submission.csv, found {{_d35_samples}}')
if not _D35_SUB.exists():
    raise RuntimeError('D35 upstream run did not produce submission.csv')
_d35_sample = _d35_pd.read_csv(_d35_samples[0], dtype={{'id': 'string'}})
_d35_sub = _d35_pd.read_csv(_D35_SUB, dtype={{'id': 'string'}})
if list(_d35_sub.columns) != ['id', 'tvt']:
    raise RuntimeError(f'D35 invalid columns: {{list(_d35_sub.columns)}}')
if len(_d35_sub) != len(_d35_sample) or not _d35_sub['id'].is_unique:
    raise RuntimeError('D35 row-count or unique-ID contract failed')
if not _d35_sub['id'].equals(_d35_sample['id']):
    raise RuntimeError('D35 output IDs do not match official sample order')
_d35_pred = _d35_pd.to_numeric(_d35_sub['tvt'], errors='coerce').to_numpy(float)
if not _d35_np.isfinite(_d35_pred).all():
    raise RuntimeError('D35 output contains non-finite predictions')
_d35_report = {{
    'route': _D35_ROUTE,
    'upstream': _D35_UPSTREAM,
    'upstream_code_sha256': _D35_UPSTREAM_CODE_SHA,
    'rows': int(len(_d35_sub)),
    'ordered_unique_ids': True,
    'finite_tvt': True,
    'submission_sha256': _d35_hashlib.sha256(_D35_SUB.read_bytes()).hexdigest(),
    'prediction_sha256': _d35_hashlib.sha256(
        _d35_np.asarray(_d35_pred, dtype='<f8').tobytes()
    ).hexdigest(),
}}
(_D35_WORK / 'd35_final_audit.json').write_text(
    _d35_json.dumps(_d35_report, indent=2) + '\\n', encoding='utf-8'
)
print('D35 FINAL AUDIT', _d35_report)
'''
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source,
    }


def prepare(spec: tuple[str, str, str, str, str]) -> dict:
    route, source_dir_name, upstream, slug, title = spec
    source_dir = SOURCES / source_dir_name
    metadata_path = source_dir / "kernel-metadata.json"
    metadata = read_json(metadata_path)
    source_path = source_dir / metadata["code_file"]
    original = read_json(source_path)
    upstream_sha = code_sha(original)
    notebook = copy.deepcopy(original)
    strip_runtime(notebook)
    notebook["cells"].insert(
        0,
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": (
                f"# {title}\n\n"
                f"Full-source private reproduction of [{upstream}]"
                f"(https://www.kaggle.com/code/{upstream}). The upstream "
                "authors retain full credit. Page-reported scores are not "
                "inherited; only this account's measured competition result "
                "will be recorded. Public output files are not mounted or "
                "used as hidden prediction parents.\n"
            ),
        },
    )
    notebook["cells"].append(audit_cell(route, upstream, upstream_sha))
    out_dir = OUT / route
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "notebook.ipynb").write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    metadata.pop("id_no", None)
    metadata.update(
        {
            "id": f"muelsyse111/{slug}",
            "title": title,
            "code_file": "notebook.ipynb",
            "is_private": True,
            "enable_internet": False,
        }
    )
    (out_dir / "kernel-metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "route": route,
        "kernel": metadata["id"],
        "upstream": upstream,
        "upstream_code_sha256": upstream_sha,
        "prepared_code_sha256": code_sha(notebook),
        "gpu": bool(metadata.get("enable_gpu")),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = [prepare(spec) for spec in SPECS]
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
