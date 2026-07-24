"""Prepare the English public Code edition of the measured D23 runner-up."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research" / "pulled_20260723" / "private_runs" / "a31_toe_tilt"
OUT = ROOT / "research" / "published_20260724" / "a31_toe_tilt_measured_6546"


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
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
        metadata = cell.get("metadata")
        if isinstance(metadata, dict):
            metadata.pop("execution", None)
            metadata.pop("papermill", None)


def main() -> None:
    notebook = json.loads((SOURCE / "notebook.ipynb").read_text(encoding="utf-8"))
    original_hash = code_hash(notebook)
    notebook = copy.deepcopy(notebook)
    notebook["cells"].insert(0, {
        "cell_type": "markdown",
        "metadata": {},
        "source": (
            "# ROGII A31 Mean-Preserving Toe Tilt — Measured 6.546\n\n"
            "This English documentation notebook reproduces the exact private scoring "
            "version submitted as ref `54917838`, which measured **6.546 public RMSE** "
            "on 2026-07-23. A27 was the D23 best at 6.476; A31 was the second-best "
            "scored route. The A28 row completed without a published score and is not "
            "misrepresented as a ranked result.\n\n"
            "The upstream A31 mechanism and pipeline are attributed to Yusuke Togashi's "
            "[`yusuketogashi/rogii-another-approch-2nd`]"
            "(https://www.kaggle.com/code/yusuketogashi/rogii-another-approch-2nd). "
            "A31 preserves the qualified branch correction on average while redistributing "
            "up to 0.18 ft smoothly from Heel to Toe. It changes 4,300 rows, preserves the "
            "target-well mean, and is 0.069168 ft RMS from the cap-2 anchor.\n\n"
            "The scoring artifact has 14,151 ordered finite predictions and SHA-256 "
            "`530fcc1bf6d6f699ace887c368f61f44d5d6cd31bf25dd8d3701f99e06c8a1c0`. "
            "This public version is Code and explanation only and must never be submitted "
            "to the competition again.\n"
        ),
    })
    strip_runtime(notebook)
    if code_hash(notebook) != original_hash:
        raise RuntimeError("Public documentation preparation changed scoring code")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "notebook.ipynb").write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    metadata = json.loads((SOURCE / "kernel-metadata.json").read_text(encoding="utf-8"))
    metadata.pop("id_no", None)
    metadata.update({
        "id": "muelsyse111/rogii-a31-toe-tilt-measured-6-546",
        "title": "ROGII A31 Toe Tilt Measured 6.546",
        "code_file": "notebook.ipynb", "is_private": False,
        "enable_gpu": True, "enable_internet": False,
    })
    (OUT / "kernel-metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"code_hash": original_hash, "output": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
