#!/usr/bin/env python3
"""Prepare the D36 Harshini full-source private reproduction.

This is a Discussion-aligned, validation-first spatial/sequence route.  All
upstream modelling cells are preserved; only attribution and the dynamic
hidden-output audit are added.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from prepare_d35_diverse_runs import audit_cell, code_sha, strip_runtime


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "artifacts" / "d36_sources" / "luffy"
OUT_DIR = ROOT / "research" / "pulled_20260804" / "private_runs" / "harshini"
UPSTREAM = "luffyh04/harshini-submission-f"
KERNEL = "muelsyse111/rogii-d36-harshini-full-source"
TITLE = "ROGII D36 Harshini Full Source"


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
                f"(https://www.kaggle.com/code/{UPSTREAM}). Harshini Reddy "
                "retains full credit. The current hidden predictions are "
                "recomputed from competition train/test data by the unchanged "
                "spatial-imputation, particle-filter and validation-first "
                "pipeline. No public notebook submission file is mounted or "
                "used as a prediction parent; public score claims are not "
                "inherited.\n"
            ),
        },
    )
    notebook["cells"].append(audit_cell("harshini", UPSTREAM, upstream_sha))

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
        "route": "harshini",
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
