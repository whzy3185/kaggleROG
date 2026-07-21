"""Prepare the five pre-registered D21 private Kaggle notebook runs.

The exact public controls retain every code cell from their source notebooks.
Derived variants change only the declared midpoint-hedge tuple and, for the two
combination routes, insert the already-audited grouped-OOF WellBias cell before
the source notebook's final hidden-set contract.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PULLED = ROOT / "research" / "pulled_20260721"
OUT = PULLED / "private_runs"


def read_notebook(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def source_text(cell: dict) -> str:
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else source


def set_source_text(cell: dict, value: str) -> None:
    cell["source"] = value


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


def replace_midhedge_tuple(notebook: dict, old: str, new: str) -> None:
    replacements = 0
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        text = source_text(cell)
        count = text.count(old)
        if count:
            set_source_text(cell, text.replace(old, new))
            replacements += count
    if replacements != 1:
        raise RuntimeError(f"Expected one midpoint tuple replacement, found {replacements}")


def find_wellbias_cell() -> dict:
    candidates = list(
        (
            PULLED.parent
            / "pulled_20260720"
            / "private_runs"
            / "mha160_wellbias"
        ).glob("*.ipynb")
    )
    if len(candidates) != 1:
        raise RuntimeError(f"Expected one D20 WellBias notebook, found {candidates}")
    notebook = read_notebook(candidates[0])
    matches = [
        cell
        for cell in notebook.get("cells", [])
        if "well-bias overlay complete" in source_text(cell)
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one WellBias cell, found {len(matches)}")
    return copy.deepcopy(matches[0])


def insert_wellbias_before_contract(notebook: dict, overlay: dict) -> None:
    contract_indexes = [
        index
        for index, cell in enumerate(notebook.get("cells", []))
        if cell.get("cell_type") == "markdown"
        and "# Hidden-rerun submission contract" in source_text(cell)
    ]
    if len(contract_indexes) != 1:
        raise RuntimeError(f"Expected one hidden contract marker, found {contract_indexes}")
    notebook["cells"].insert(contract_indexes[0], copy.deepcopy(overlay))


def attribution_cell(title: str, body: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": f"# {title}\n\n{body}\n",
    }


def prepare(
    *,
    name: str,
    source_dir: str,
    source_notebook: str,
    slug: str,
    title: str,
    attribution: str,
    tuple_change: tuple[str, str] | None = None,
    add_wellbias: bool = False,
) -> dict:
    source_path = PULLED / source_dir / source_notebook
    source_meta = json.loads(
        (PULLED / source_dir / "kernel-metadata.json").read_text(encoding="utf-8")
    )
    original = read_notebook(source_path)
    notebook = copy.deepcopy(original)
    if tuple_change is not None:
        replace_midhedge_tuple(notebook, *tuple_change)
    if add_wellbias:
        insert_wellbias_before_contract(notebook, find_wellbias_cell())
    notebook["cells"].insert(0, attribution_cell(title, attribution))
    strip_runtime(notebook)

    out_dir = OUT / name
    out_dir.mkdir(parents=True, exist_ok=True)
    code_file = "notebook.ipynb"
    (out_dir / code_file).write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    metadata = copy.deepcopy(source_meta)
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
        "source_code_hash": code_hash(original),
        "prepared_code_hash": code_hash(notebook),
        "wellbias": add_wellbias,
        "tuple_change": tuple_change,
    }


def main() -> None:
    source_tuple = (
        "_MH_ALPHA, _MH_MINMASS, _MH_SEPLO, _MH_SEPHI, _MH_CAP = "
        "2.5, 0.22, 2.0, 40.0, 4.0"
    )
    alpha260_tuple = (
        "_MH_ALPHA, _MH_MINMASS, _MH_SEPLO, _MH_SEPHI, _MH_CAP = "
        "2.6, 0.22, 2.0, 40.0, 4.0"
    )
    common_source = (
        "Exact public source: WBF_USA_NYC's "
        "[`wbfranci/rogii-det-mha250sep2-public6858`]"
        "(https://www.kaggle.com/code/wbfranci/rogii-det-mha250sep2-public6858), "
        "which credits Kun Zhang's `beicicc/rogii-mha160-sep3-r2-20260720`. "
        "Source-team score claims remain source-team results; this account reports only "
        "scores measured from the audited private version."
    )
    specs = [
        dict(
            name="mha250sep2_repro",
            source_dir="mha250sep2",
            source_notebook="rogii-det-mha250sep2-public6858.ipynb",
            slug="muelsyse111/rogii-d21-mha250sep2-repro",
            title="ROGII D21 MHA250SEP2 Repro",
            attribution=common_source + " No prediction code is changed in this control.",
        ),
        dict(
            name="mha260sep3_repro",
            source_dir="mha260sep3",
            source_notebook="rogii-mha260-sep3-frontier.ipynb",
            slug="muelsyse111/rogii-d21-mha260sep3-repro",
            title="ROGII D21 MHA260SEP3 Repro",
            attribution=(
                "Exact public source: WBF_USA_NYC's "
                "[`wbfranci/rogii-mha260-sep3-frontier`]"
                "(https://www.kaggle.com/code/wbfranci/rogii-mha260-sep3-frontier). "
                "No prediction code is changed; source-team claims remain attributed."
            ),
        ),
        dict(
            name="mha260sep2",
            source_dir="mha250sep2",
            source_notebook="rogii-det-mha250sep2-public6858.ipynb",
            slug="muelsyse111/rogii-d21-mha260sep2-frontier",
            title="ROGII D21 MHA260SEP2 Frontier",
            attribution=(
                common_source
                + " The only scoring change is midpoint alpha 2.5 to 2.6; "
                "separation floor 2.0, minimum mass 0.22, and cap 4.0 are unchanged."
            ),
            tuple_change=(source_tuple, alpha260_tuple),
        ),
        dict(
            name="mha250sep2_wellbias",
            source_dir="mha250sep2",
            source_notebook="rogii-det-mha250sep2-public6858.ipynb",
            slug="muelsyse111/rogii-d21-mha250sep2-wellbias",
            title="ROGII D21 MHA250SEP2 WellBias",
            attribution=(
                common_source
                + " The bounded grouped-OOF prefix-GR random-forest datum overlay is "
                "attributed to Chiekh ALLOUL's "
                "[`chiekhalloul/rogii-det-wellbias-prefix-r1`]"
                "(https://www.kaggle.com/code/chiekhalloul/rogii-det-wellbias-prefix-r1)."
            ),
            add_wellbias=True,
        ),
        dict(
            name="mha260sep2_wellbias",
            source_dir="mha250sep2",
            source_notebook="rogii-det-mha250sep2-public6858.ipynb",
            slug="muelsyse111/rogii-d21-mha260sep2-wellbias",
            title="ROGII D21 MHA260SEP2 WellBias",
            attribution=(
                common_source
                + " This changes only alpha 2.5 to 2.6 and then inserts Chiekh "
                "ALLOUL's audited grouped-OOF prefix-GR WellBias overlay before the "
                "final hidden-set contract."
            ),
            tuple_change=(source_tuple, alpha260_tuple),
            add_wellbias=True,
        ),
    ]
    results = [prepare(**spec) for spec in specs]
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
