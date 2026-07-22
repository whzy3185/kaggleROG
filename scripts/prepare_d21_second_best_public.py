"""Prepare the English public Code edition of the measured D21 runner-up."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "research"
    / "pulled_20260721"
    / "private_runs"
    / "mha250sep2_wellbias"
)
OUT = (
    ROOT
    / "research"
    / "published_20260722"
    / "mha250sep2_wellbias_measured_6832"
)


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


def main() -> None:
    notebook = json.loads((SOURCE / "notebook.ipynb").read_text(encoding="utf-8"))
    original_hash = code_hash(notebook)
    notebook = copy.deepcopy(notebook)
    notebook["cells"].insert(
        0,
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": (
                "# ROGII MHA250SEP2 + WellBias — Measured 6.832\n\n"
                "This English documentation notebook reproduces the exact private scoring "
                "version submitted as ref `54869268`, which measured **6.832 public RMSE** "
                "on 2026-07-21. It was the second-best of this account's five D21 routes; "
                "the alpha-2.6 interaction scored 6.829.\n\n"
                "The MHA250SEP2 base is attributed to WBF_USA_NYC's "
                "[`wbfranci/rogii-det-mha250sep2-public6858`]"
                "(https://www.kaggle.com/code/wbfranci/rogii-det-mha250sep2-public6858), "
                "which credits Kun Zhang. The bounded grouped-OOF prefix-GR WellBias "
                "overlay is attributed to Chiekh ALLOUL's "
                "[`chiekhalloul/rogii-det-wellbias-prefix-r1`]"
                "(https://www.kaggle.com/code/chiekhalloul/rogii-det-wellbias-prefix-r1).\n\n"
                "The scoring artifact had 14,151 ordered finite predictions, SHA-256 "
                "`3d1069d2d40eeb3e508d73318aedcd8d164a1177b2075d9bc9608d3fa49a583d`, "
                "and no fatal log markers. This public version is for Code and explanation "
                "only; it must not be submitted to the competition again.\n"
            ),
        },
    )
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
            "id": "muelsyse111/rogii-mha250sep2-wellbias-measured-6-832",
            "title": "ROGII MHA250SEP2 WellBias Measured 6.832",
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
