"""Prepare the five pre-registered D22 private Kaggle notebook runs.

The public P100 notebook reproduces johnjanson/hahaha-nondet-agi Version 1 and
its downloaded submission.csv is byte-identical to that source output.  The
D22 grid keeps that exact cap-2 control, changes only the active branch-hedge
cap for two ladder points, and crosses the first two caps with the previously
audited grouped-OOF WellBias overlay.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PULLED = ROOT / "research" / "pulled_20260722"
SOURCE_DIR = PULLED / "p100_seed_ensemble"
OUT = PULLED / "private_runs"


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
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
        metadata = cell.get("metadata")
        if isinstance(metadata, dict):
            metadata.pop("execution", None)
            metadata.pop("papermill", None)


def replace_once(notebook: dict, old: str, new: str) -> None:
    matches = 0
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        text = source_text(cell)
        count = text.count(old)
        if count:
            cell["source"] = text.replace(old, new)
            matches += count
    if matches != 1:
        raise RuntimeError(f"Expected one replacement for {old!r}, found {matches}")


def find_wellbias_cell() -> dict:
    source_dir = (
        PULLED.parent
        / "pulled_20260720"
        / "private_runs"
        / "mha160_wellbias"
    )
    notebooks = list(source_dir.glob("*.ipynb"))
    if len(notebooks) != 1:
        raise RuntimeError(f"Expected one D20 WellBias notebook, found {notebooks}")
    matches = [
        cell
        for cell in read_json(notebooks[0]).get("cells", [])
        if "well-bias overlay complete" in source_text(cell)
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one WellBias cell, found {len(matches)}")
    return copy.deepcopy(matches[0])


def insert_before_contract(notebook: dict, cell: dict) -> None:
    indexes = [
        index
        for index, item in enumerate(notebook.get("cells", []))
        if item.get("cell_type") == "markdown"
        and "# Hidden-rerun submission contract" in source_text(item)
    ]
    if len(indexes) != 1:
        raise RuntimeError(f"Expected one hidden contract marker, found {indexes}")
    notebook["cells"].insert(indexes[0], copy.deepcopy(cell))


def markdown(title: str, body: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": f"# {title}\n\n{body}\n",
    }


def prepare(*, name: str, slug: str, title: str, cap: float, wellbias: bool) -> dict:
    source_path = next(SOURCE_DIR.glob("*.ipynb"))
    original = read_json(source_path)
    notebook = copy.deepcopy(original)
    if cap != 2.0:
        replace_once(notebook, "_BH_CAP = 2.00", f"_BH_CAP = {cap:.2f}")
    if wellbias:
        insert_before_contract(notebook, find_wellbias_cell())

    change = (
        "No scoring code is changed in this exact control."
        if cap == 2.0 and not wellbias
        else f"The branch-hedge cap is set to {cap:.2f} ft"
        + (
            ", followed by the audited grouped-OOF prefix-GR WellBias overlay."
            if wellbias
            else "; all other scoring parameters are unchanged."
        )
    )
    attribution = (
        "Exact public base: Prvi Siyan's "
        "[`prvsiyan/rogii-p100-0-010-seed-ensemble-frontier-visuals`]"
        "(https://www.kaggle.com/code/prvsiyan/rogii-p100-0-010-seed-ensemble-frontier-visuals), "
        "which reproduces Janson's `johnjanson/hahaha-nondet-agi` Version 1 "
        "and attributes its measured 6.594 public score to that source version. "
        "This account reports only its own audited submission score. "
        + change
    )
    if wellbias:
        attribution += (
            " WellBias is attributed to Chiekh ALLOUL's "
            "[`chiekhalloul/rogii-det-wellbias-prefix-r1`]"
            "(https://www.kaggle.com/code/chiekhalloul/rogii-det-wellbias-prefix-r1)."
        )
    notebook["cells"].insert(0, markdown(title, attribution))
    strip_runtime(notebook)

    out_dir = OUT / name
    out_dir.mkdir(parents=True, exist_ok=True)
    code_file = "notebook.ipynb"
    (out_dir / code_file).write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    metadata = read_json(SOURCE_DIR / "kernel-metadata.json")
    metadata.pop("id_no", None)
    metadata.update(
        {
            "id": slug,
            "title": title,
            "code_file": code_file,
            "is_private": True,
            "enable_gpu": True,
            "enable_internet": False,
        }
    )
    (out_dir / "kernel-metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "name": name,
        "slug": slug,
        "cap": cap,
        "wellbias": wellbias,
        "source_code_hash": code_hash(original),
        "prepared_code_hash": code_hash(notebook),
    }


def main() -> None:
    specs = [
        ("p100_cap2_repro", "rogii-d22-p100-cap2-repro", "ROGII D22 P100 Cap2 Repro", 2.0, False),
        ("p100_cap25", "rogii-d22-p100-cap2-5", "ROGII D22 P100 Cap2.5", 2.5, False),
        ("p100_cap3", "rogii-d22-p100-cap3", "ROGII D22 P100 Cap3", 3.0, False),
        ("p100_cap2_wellbias", "rogii-d22-p100-cap2-wellbias", "ROGII D22 P100 Cap2 WellBias", 2.0, True),
        ("p100_cap25_wellbias", "rogii-d22-p100-cap2-5-wellbias", "ROGII D22 P100 Cap2.5 WellBias", 2.5, True),
    ]
    results = [
        prepare(
            name=name,
            slug=f"muelsyse111/{slug}",
            title=title,
            cap=cap,
            wellbias=wellbias,
        )
        for name, slug, title, cap, wellbias in specs
    ]
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
