"""Prepare the English public Code edition of the measured D22 runner-up tier."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "pulled_20260722" / "private_runs" / "p100_cap25"
OUT = ROOT / "research" / "published_20260723" / "p100_cap25_measured_6667"


def source_text(cell: dict) -> str:
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else value


def code_hash(notebook: dict) -> str:
    text = "\n\n".join(
        source_text(cell)
        for cell in notebook.get("cells", [])
        if cell.get("cell_type") == "code"
    )
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def strip_runtime(notebook: dict) -> None:
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
        metadata = cell.get("metadata")
        if isinstance(metadata, dict):
            metadata.pop("execution", None)
            metadata.pop("papermill", None)


def main() -> None:
    source_path = SOURCE / "notebook.ipynb"
    notebook = json.loads(source_path.read_text(encoding="utf-8"))
    original_hash = code_hash(notebook)
    notebook = copy.deepcopy(notebook)
    notebook["cells"].insert(
        0,
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": (
                "# ROGII P100 Branch Cap 2.5 — Measured 6.667\n\n"
                "This English documentation notebook reproduces the exact private scoring "
                "version submitted as ref `54895437`, which measured **6.667 public RMSE** "
                "on 2026-07-22. The two WellBias variants tied for the best D22 score at "
                "6.638; three no-WellBias cap variants tied for the runner-up tier at 6.667. "
                "Cap 2.5 is published as the representative runner-up because it is a clean "
                "single-variable continuation of the source's 2.0 ft branch cap.\n\n"
                "The base is attributed to Prvi Siyan's "
                "[`prvsiyan/rogii-p100-0-010-seed-ensemble-frontier-visuals`]"
                "(https://www.kaggle.com/code/prvsiyan/rogii-p100-0-010-seed-ensemble-frontier-visuals), "
                "which reproduces Janson's "
                "[`johnjanson/hahaha-nondet-agi`]"
                "(https://www.kaggle.com/code/johnjanson/hahaha-nondet-agi). "
                "Relative to the 2.0 ft control, only well `00e12e8b` changes: 4,301 rows "
                "move by exactly +0.5 ft (0.275652 ft global RMS).\n\n"
                "The scoring artifact contains 14,151 ordered finite predictions, has "
                "SHA-256 `2d2d40b94a9940911d84d4fb8364f987811bb45a68e1ed66e289492960778494`, "
                "and passed the final-file and fatal-log audits. This public version is Code "
                "and explanation only; it must never be submitted to the competition again.\n"
            ),
        },
    )
    strip_runtime(notebook)
    if code_hash(notebook) != original_hash:
        raise RuntimeError("Public documentation preparation changed scoring code")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "notebook.ipynb").write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    metadata = json.loads((SOURCE / "kernel-metadata.json").read_text(encoding="utf-8"))
    metadata.pop("id_no", None)
    metadata.update(
        {
            "id": "muelsyse111/rogii-p100-cap2-5-measured-6-667",
            "title": "ROGII P100 Cap2.5 Measured 6.667",
            "code_file": "notebook.ipynb",
            "is_private": False,
            "enable_gpu": True,
            "enable_internet": False,
        }
    )
    (OUT / "kernel-metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"code_hash": original_hash, "output": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
