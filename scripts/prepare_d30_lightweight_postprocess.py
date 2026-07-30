"""Prepare lightweight D30 post-process kernels from audited private outputs.

The full non-branch refresh twice received an empty competition train mount.
These CPU-only kernels avoid rerunning the upstream model: they locate our own
previously audited outputs by exact file SHA-256, verify inherited ID order,
and test two pre-registered interactions.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "pulled_20260730" / "private_runs"
BASE_SHA = "d6096142da6363303f35d719dd86990706dd6c90d59257a110fc9e35464dfff8"
NONBRANCH_SHA = "51d31770acfd657d27ad5b4ad07968ce05f2ae3c784f0faa47b74d682d1405eb"
GS16_SHA = "1591f9eb5af4ae2f81be86d55120b42bcc20c65614eb974bfe15725b7f6aaa27"
DRIFT_SHA = "398d38612dc910fa7502ffc814df16412930cedd1136ab42d855b6ea7f2f3010"


def code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source,
    }


def markdown_cell(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source}


def notebook(title: str, explanation: str, route: str, formula: str) -> dict:
    source = f'''from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

EXPECTED = {{
    "base": "{BASE_SHA}",
    "nonbranch": "{NONBRANCH_SHA}",
    "third": "{GS16_SHA if route == "gs16_nonbranch_transfer" else DRIFT_SHA}",
}}

def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

found = {{}}
for path in sorted(Path("/kaggle/input").rglob("submission.csv")):
    digest = file_sha(path)
    for name, expected in EXPECTED.items():
        if digest == expected:
            found[name] = path
if set(found) != set(EXPECTED):
    raise RuntimeError(f"Missing exact audited parents: found={{found}}, expected={{EXPECTED}}")

frames = {{name: pd.read_csv(path) for name, path in found.items()}}
base = frames["base"]
nonbranch = frames["nonbranch"]
third = frames["third"]
for name, frame in frames.items():
    if list(frame.columns) != ["id", "tvt"] or len(frame) != 14151:
        raise RuntimeError(f"Invalid {{name}} columns or row count")
    frame["id"] = frame["id"].astype(str)
    if frame["id"].duplicated().any() or not frame["id"].equals(base["id"]):
        raise RuntimeError(f"Invalid or misaligned IDs in {{name}}")
    if not np.isfinite(pd.to_numeric(frame["tvt"], errors="coerce")).all():
        raise RuntimeError(f"Non-finite predictions in {{name}}")

b = base["tvt"].to_numpy(float)
n = nonbranch["tvt"].to_numpy(float)
t = third["tvt"].to_numpy(float)
{formula}
if not np.isfinite(pred).all():
    raise RuntimeError("Final predictions are non-finite")

submission = pd.DataFrame({{"id": base["id"], "tvt": pred}})
submission.to_csv("/kaggle/working/submission.csv", index=False)
out_path = Path("/kaggle/working/submission.csv")
report = {{
    "route": "{route}",
    "rows": int(len(submission)),
    "ordered_unique_ids": True,
    "parent_order_inherited_from_audited_d25_a27": True,
    "finite_tvt": True,
    "file_sha256": file_sha(out_path),
    "prediction_sha256": hashlib.sha256(np.asarray(pred, dtype="<f8").tobytes()).hexdigest(),
    "parent_file_sha256": EXPECTED,
    "rms_from_base_ft": float(np.sqrt(np.mean((pred - b) ** 2))),
    "rms_from_nonbranch_ft": float(np.sqrt(np.mean((pred - n) ** 2))),
    "rms_from_third_ft": float(np.sqrt(np.mean((pred - t) ** 2))),
    "max_abs_from_base_ft": float(np.max(np.abs(pred - b))),
    "changed_rows_from_base": int(np.count_nonzero(pred - b)),
    **extra,
}}
Path("/kaggle/working/d30_final_audit.json").write_text(
    json.dumps(report, indent=2) + "\\n", encoding="utf-8"
)
print("D30 FINAL AUDIT", report)
'''
    return {
        "cells": [
            markdown_cell(f"# {title}\n\n{explanation}\n"),
            code_cell(source),
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.12.0"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def write_run(
    name: str,
    slug: str,
    title: str,
    explanation: str,
    route: str,
    formula: str,
    kernel_sources: list[str],
) -> dict:
    run_dir = OUT / name
    run_dir.mkdir(parents=True, exist_ok=True)
    nb = notebook(title, explanation, route, formula)
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
        "kernel_sources": kernel_sources,
        "competition_sources": ["rogii-wellbore-geology-prediction"],
        "model_sources": [],
    }
    (run_dir / "notebook.ipynb").write_text(
        json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    (run_dir / "kernel-metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    code = "".join(cell.get("source", "") for cell in nb["cells"] if cell["cell_type"] == "code")
    return {
        "name": name,
        "slug": metadata["id"],
        "prepared_code_hash": hashlib.sha256(code.encode()).hexdigest(),
    }


def main() -> None:
    results = [
        write_run(
            "gs16_nonbranch_transfer",
            "rogii-d30-gs160-nonbranch-transfer-r1",
            "ROGII D30 GS160 Nonbranch Transfer R1",
            (
                "A lightweight interaction test using only this account's audited private "
                "outputs. It transfers the measured D29 5% non-branch delta onto the "
                "independent GS1.60 run. Exact parent SHA-256 checks prevent silent lineage "
                "drift. Raunak Dey and upstream authors retain credit."
            ),
            "gs16_nonbranch_transfer",
            '''delta_nonbranch = n - b
pred = t + delta_nonbranch
extra = {
    "nonbranch_delta_rms_ft": float(np.sqrt(np.mean(delta_nonbranch ** 2))),
    "nonbranch_delta_max_abs_ft": float(np.max(np.abs(delta_nonbranch))),
}''',
            [
                "muelsyse111/rogii-d25-a27-narrow-smooth",
                "muelsyse111/rogii-d29-a27-nonbranch-shape-r1",
                "muelsyse111/rogii-d30-a27-gs160-isolated-r1",
            ],
        ),
        write_run(
            "nonbranch_drift_agreement_static",
            "rogii-d30-nonbranch-drift-agreement-static-r1",
            "ROGII D30 Nonbranch Drift Agreement Static R1",
            (
                "A lightweight agreement gate using only this account's audited private "
                "outputs. The measured D29 non-branch delta is retained, while the prefix-U "
                "drift delta is added only where both corrections have the same non-zero "
                "sign. Exact parent SHA-256 checks prevent silent lineage drift. Raunak Dey "
                "and upstream authors retain credit."
            ),
            "nonbranch_drift_agreement_static",
            '''delta_nonbranch = n - b
delta_drift = t - b
agree = (delta_nonbranch * delta_drift) > 0
pred = n + np.where(agree, delta_drift, 0.0)
extra = {
    "agreement_rows": int(agree.sum()),
    "agreement_drift_rms_ft": float(np.sqrt(np.mean(np.where(agree, delta_drift, 0.0) ** 2))),
    "nonbranch_delta_rms_ft": float(np.sqrt(np.mean(delta_nonbranch ** 2))),
}''',
            [
                "muelsyse111/rogii-d25-a27-narrow-smooth",
                "muelsyse111/rogii-d29-a27-nonbranch-shape-r1",
                "muelsyse111/rogii-d30-a27-prefix-u-drift",
            ],
        ),
    ]
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
