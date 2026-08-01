"""Static preflight checks for ROGII notebook CV claims.

These checks deliberately fail closed.  They do not prove that a notebook is
leak-free; they identify known patterns that make the current public/D29
"full-stack" diagnostic unsuitable as leaderboard evidence.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


def _code_sources(path: Path) -> list[str]:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    return [
        "".join(cell.get("source", []))
        for cell in notebook.get("cells", [])
        if cell.get("cell_type") == "code"
    ]


def audit_full_stack_notebook(path: Path) -> dict[str, object]:
    sources = _code_sources(path)
    source = "\n".join(sources)
    ablation_cells = [text for text in sources if "Full-stack bimodal CV ablation" in text]
    ablation = "\n".join(ablation_cells)

    full_cv_enabled = bool(
        re.search(r"^RUN_FULL_STACK_CV_ABLATION\s*=\s*True\s*$", source, re.MULTILINE)
    )
    self_inclusion_calls = len(
        re.findall(r"(?:fi|di)\.impute\(xy,\s*self_wid=None\)", source)
    )
    contact_reads_full_truth = all(
        token in source
        for token in (
            "def _gold_contact_candidate",
            "hw_tr = _gold_pd.read_csv(hw_tr_path)",
            "hw_tr['TVT'].to_numpy",
        )
    )
    has_grouped_ridge_oof = all(
        token in source for token in ("GroupKFold", "ridge_oof_preds", "train_df['well']")
    )
    includes_model_package = "RUN_MODEL_PACKAGE_CORRECTION" in ablation
    includes_guarded_contact = "_gold_reapply_guarded_contact_override" in ablation
    includes_nonbranch_transaction = "d29_nonbranch" in ablation.lower()

    findings = [
        {
            "id": "cv_disabled",
            "severity": "blocker",
            "present": not full_cv_enabled,
            "detail": "RUN_FULL_STACK_CV_ABLATION is not enabled in the stored notebook.",
        },
        {
            "id": "surface_self_inclusion",
            "severity": "blocker",
            "present": self_inclusion_calls > 0,
            "count": self_inclusion_calls,
            "detail": "Train-side surface candidates call the imputer without excluding the held-out well.",
        },
        {
            "id": "contact_full_truth_offset",
            "severity": "blocker",
            "present": contact_reads_full_truth,
            "detail": "The contact candidate reloads the complete training well and computes its offset from TVT truth.",
        },
        {
            "id": "missing_deployment_layers",
            "severity": "blocker",
            "present": not (
                includes_model_package and includes_guarded_contact and includes_nonbranch_transaction
            ),
            "detail": "The diagnostic does not replay model-package, guarded-contact, and D29 non-branch layers together.",
        },
    ]
    blockers = [row["id"] for row in findings if row["severity"] == "blocker" and row["present"]]
    return {
        "notebook": str(path.resolve()),
        "full_cv_enabled": full_cv_enabled,
        "has_grouped_ridge_oof": has_grouped_ridge_oof,
        "ablation_cell_count": len(ablation_cells),
        "surface_self_inclusion_calls": self_inclusion_calls,
        "contact_reads_full_truth": contact_reads_full_truth,
        "includes_model_package": includes_model_package,
        "includes_guarded_contact": includes_guarded_contact,
        "includes_nonbranch_transaction": includes_nonbranch_transaction,
        "findings": findings,
        "blockers": blockers,
        "locally_scoreable_as_stored": len(blockers) == 0,
    }


def prepare_leak_safe_diagnostic_copy(
    source_path: Path,
    output_path: Path,
    *,
    n_wells: int = 30,
    selector_seeds: int = 8,
    data_root: Path | None = None,
) -> dict[str, int | str]:
    """Patch known train-side leaks in a diagnostic copy of the notebook.

    The copy remains a component ablation rather than deployment-parity OOF.
    Its banner and the static audit both preserve that distinction.
    """

    if n_wells < 5:
        raise ValueError("n_wells must be at least five")
    if selector_seeds < 1:
        raise ValueError("selector_seeds must be positive")
    notebook = json.loads(source_path.read_text(encoding="utf-8"))
    data_root_text = str(data_root.resolve()).replace("\\", "/") if data_root else None
    replacements = {
        "RUN_FULL_STACK_CV_ABLATION = False": "RUN_FULL_STACK_CV_ABLATION = True",
        "CV_ABLATION_N_WELLS = 250": f"CV_ABLATION_N_WELLS = {n_wells}",
        "CV_SELECTOR_PF_SEEDS = 24": f"CV_SELECTOR_PF_SEEDS = {selector_seeds}",
        "form_all, _ = fi.impute(xy, self_wid=None)": "form_all, _ = fi.impute(xy, self_wid=wid)",
        "dense, _, _ = di.impute(xy, self_wid=None)": "dense, _, _ = di.impute(xy, self_wid=wid)",
    }
    if data_root_text:
        replacements[
            "COMPETITION_DATA_ROOT = '/kaggle/input/competitions/rogii-wellbore-geology-prediction'"
        ] = f"COMPETITION_DATA_ROOT = {data_root_text!r}"
    counts = {old: 0 for old in replacements}
    contact_count = 0
    contact_old = (
        "        hw_tr = _gold_pd.read_csv(hw_tr_path)\n"
        "        tw_tr = _gold_pd.read_csv(tw_tr_path)"
    )
    contact_new = (
        "        # CV-safe: use only the masked visible prefix for the datum offset.\n"
        "        hw_tr = hw.copy(deep=True)\n"
        "        hw_tr['TVT'] = _gold_pd.to_numeric(hw_tr['TVT_input'], errors='coerce')\n"
        "        tw_tr = _gold_pd.read_csv(tw_tr_path)"
    )
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        text = "".join(cell.get("source", []))
        for old, new in replacements.items():
            found = text.count(old)
            if found:
                text = text.replace(old, new)
                counts[old] += found
        found = text.count(contact_old)
        if found:
            text = text.replace(contact_old, contact_new)
            contact_count += found
        cell["source"] = text.splitlines(keepends=True)

    expected_once = (
        "RUN_FULL_STACK_CV_ABLATION = False",
        "CV_ABLATION_N_WELLS = 250",
        "CV_SELECTOR_PF_SEEDS = 24",
        "form_all, _ = fi.impute(xy, self_wid=None)",
        "dense, _, _ = di.impute(xy, self_wid=None)",
    )
    if data_root_text:
        expected_once += (
            "COMPETITION_DATA_ROOT = '/kaggle/input/competitions/rogii-wellbore-geology-prediction'",
        )
    bad = {key: counts[key] for key in expected_once if counts[key] != 1}
    if bad or contact_count != 1:
        raise ValueError(f"Unexpected notebook patch counts: replacements={bad}, contact={contact_count}")

    banner = {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Leak-safe local CV diagnostic copy\n",
            "\n",
            "This generated copy excludes the held-out well from surface imputers and uses only the masked visible prefix for contact offsets. It still does **not** replay every deployment layer, so its score is component evidence rather than a leaderboard estimate.\n",
        ],
    }
    notebook["cells"].insert(0, banner)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
    return {
        "source": str(source_path.resolve()),
        "output": str(output_path.resolve()),
        "n_wells": n_wells,
        "selector_seeds": selector_seeds,
        "data_root": data_root_text or "unchanged",
        "patched_surface_calls": 2,
        "patched_contact_calls": contact_count,
    }
