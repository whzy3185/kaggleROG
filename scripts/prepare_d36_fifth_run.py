#!/usr/bin/env python3
"""Prepare the D36 fifth-route private full-source reproduction.

The upstream modelling cells and attached model/data sources are retained
unchanged.  We add attribution and the existing read-only hidden-output audit;
no public notebook output is attached as a prediction parent.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from prepare_d35_diverse_runs import audit_cell, code_sha, strip_runtime


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "artifacts" / "d36_sources" / "brian"
OUT_DIR = ROOT / "research" / "pulled_20260804" / "private_runs" / "akiiro"
UPSTREAM = "brianbovell/akiirolabs-tvt-prediction-model"
KERNEL = "muelsyse111/rogii-d36-akiiro-full-source"
TITLE = "ROGII D36 Akiiro Full Source"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    metadata = read_json(SOURCE_DIR / "kernel-metadata.json")
    original = read_json(SOURCE_DIR / metadata["code_file"])
    upstream_sha = code_sha(original)

    notebook = copy.deepcopy(original)
    strip_runtime(notebook)
    notebook["cells"].insert(
        0,
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": (
                f"# {TITLE}\n\n"
                f"Private full-source reproduction of [{UPSTREAM}]"
                f"(https://www.kaggle.com/code/{UPSTREAM}). Brian Bovell and "
                "the credited upstream model authors retain full credit. "
                "The current hidden predictions are recomputed from competition "
                "data and the upstream public model/data artifacts; no public "
                "notebook submission file is mounted or used as a prediction "
                "parent. Page-reported scores are not inherited.\n"
            ),
        },
    )
    notebook["cells"].append(audit_cell("akiiro", UPSTREAM, upstream_sha))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    notebook_path = OUT_DIR / "notebook.ipynb"
    notebook_path.write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )

    metadata.pop("id_no", None)
    metadata.update(
        {
            "id": KERNEL,
            "title": TITLE,
            "code_file": notebook_path.name,
            "is_private": True,
            "enable_internet": False,
        }
    )
    (OUT_DIR / "kernel-metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    manifest = {
        "route": "akiiro",
        "kernel": KERNEL,
        "upstream": UPSTREAM,
        "upstream_code_sha256": upstream_sha,
        "prepared_code_sha256": code_sha(notebook),
        "notebook_sha256": hashlib.sha256(notebook_path.read_bytes()).hexdigest(),
        "dataset_sources": metadata.get("dataset_sources", []),
        "kernel_sources": metadata.get("kernel_sources", []),
        "competition_sources": metadata.get("competition_sources", []),
    }
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
