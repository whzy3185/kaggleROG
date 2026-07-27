"""Prepare audited D27 private scoring notebooks.

D27 reserves exactly one submission for an exact current-source reproduction
of the public Frontier II artifact. Structural candidates are added only after
they pass the pre-registered local gates.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from prepare_d25_private_runs import notebook_path, read_json, strip_runtime


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "pulled_20260727" / "private_runs"
FRONTIER_SOURCE = ROOT / "research" / "pulled_20260727" / "frontier_ii"
FRONTIER_EXPECTED_SHA = (
    "bf48603db1b8ab3406a525ef7ef1a3b77424075de1c740f1af8c4cbec8feadd8"
)


GATED_ENSEMBLE_CELL = r'''# D27 uncertainty-gated cross-branch ensemble.
# This is hidden-run compatible: all weights are derived from the run-local
# SP45 and learned trajectories, never from visible well IDs or score labels.
import json as _dge_json
from pathlib import Path as _DgePath
import numpy as _dge_np
import pandas as _dge_pd

_DGE_WORK = _DgePath('/kaggle/working') if _DgePath('/kaggle/working').exists() else _DgePath('.')
_DGE_SUB = _DGE_WORK / 'submission.csv'
_DGE_SP45 = _DGE_WORK / 'sp45_projection_submission.csv'
_DGE_LEARNED = _DGE_WORK / 'learned_trajectory_submission.csv'
if not (_DGE_SUB.exists() and _DGE_SP45.exists() and _DGE_LEARNED.exists()):
    raise RuntimeError('D27 gated ensemble requires run-local SP45 and learned outputs')
_dge_base = _dge_pd.read_csv(_DGE_SUB)
_dge_sp = _dge_pd.read_csv(_DGE_SP45)
_dge_lr = _dge_pd.read_csv(_DGE_LEARNED)
for _dge_frame, _dge_name in ((_dge_base, 'base'), (_dge_sp, 'sp45'), (_dge_lr, 'learned')):
    if list(_dge_frame.columns) != ['id', 'tvt']:
        raise RuntimeError(f'D27 gated ensemble invalid {_dge_name} schema')
    if not _dge_frame['id'].astype(str).equals(_dge_base['id'].astype(str)):
        raise RuntimeError(f'D27 gated ensemble {_dge_name} id mismatch')
_dge_s = _dge_pd.to_numeric(_dge_sp['tvt'], errors='coerce').to_numpy(float)
_dge_l = _dge_pd.to_numeric(_dge_lr['tvt'], errors='coerce').to_numpy(float)
if not (_dge_np.isfinite(_dge_s).all() and _dge_np.isfinite(_dge_l).all()):
    raise RuntimeError('D27 gated ensemble non-finite component')
_dge_abs = _dge_np.abs(_dge_s - _dge_l)
# Agreement earns the learned OOF branch more weight; strong disagreement
# falls back toward the physical/PF anchor. The scale is fixed before LB.
_dge_w_sp = _dge_np.clip(0.05 + 0.80 * (_dge_abs / 8.0), 0.05, 0.85)
_dge_final = _dge_w_sp * _dge_s + (1.0 - _dge_w_sp) * _dge_l
if not _dge_np.isfinite(_dge_final).all():
    raise RuntimeError('D27 gated ensemble produced non-finite predictions')
_dge_base['tvt'] = _dge_final
_dge_base.to_csv(_DGE_SUB, index=False)
_dge_well = _dge_base['id'].astype(str).str.rsplit('_', n=1).str[0]
_dge_rows = []
for _dge_wid in sorted(_dge_well.unique()):
    _dge_m = _dge_well.eq(_dge_wid).to_numpy()
    _dge_rows.append({
        'well': str(_dge_wid),
        'rows': int(_dge_m.sum()),
        'median_abs_branch_gap_ft': float(_dge_np.median(_dge_abs[_dge_m])),
        'p90_abs_branch_gap_ft': float(_dge_np.quantile(_dge_abs[_dge_m], 0.90)),
        'mean_sp45_weight': float(_dge_np.mean(_dge_w_sp[_dge_m])),
    })
_dge_pd.DataFrame(_dge_rows).to_csv(_DGE_WORK / 'd27_gated_ensemble_report.csv', index=False)
(_DGE_WORK / 'd27_gated_ensemble_summary.json').write_text(
    _dge_json.dumps({
        'hidden_run_compatible': True,
        'rows': int(len(_dge_final)),
        'mean_sp45_weight': float(_dge_w_sp.mean()),
        'min_sp45_weight': float(_dge_w_sp.min()),
        'max_sp45_weight': float(_dge_w_sp.max()),
        'rms_from_sp45_ft': float(_dge_np.sqrt(_dge_np.mean((_dge_final - _dge_s) ** 2))),
    }, indent=2) + '\n',
    encoding='utf-8',
)
print('D27 gated ensemble complete:', _dge_rows)
'''


RESIDUAL_HEAVY_CELL = r'''# D27 grouped-OOF residual-heavy post-contact transaction.
# The learned and SP45 components are run-local and therefore work on hidden
# wells. Applying this after the contact guard prevents a successful contact
# reconstruction from silently making the experiment byte-inert.
import json as _drh_json
from pathlib import Path as _DrhPath
import numpy as _drh_np
import pandas as _drh_pd

_DRH_WORK = _DrhPath('/kaggle/working') if _DrhPath('/kaggle/working').exists() else _DrhPath('.')
_DRH_SUB = _DRH_WORK / 'submission.csv'
_DRH_SP45 = _DRH_WORK / 'sp45_projection_submission.csv'
_DRH_LEARNED = _DRH_WORK / 'learned_trajectory_submission.csv'
_DRH_W_SP45 = 0.15
if not (_DRH_SUB.exists() and _DRH_SP45.exists() and _DRH_LEARNED.exists()):
    raise RuntimeError('D27 residual-heavy route requires run-local branch outputs')
_drh_base = _drh_pd.read_csv(_DRH_SUB)
_drh_sp = _drh_pd.read_csv(_DRH_SP45)
_drh_lr = _drh_pd.read_csv(_DRH_LEARNED)
for _drh_frame, _drh_name in ((_drh_base, 'base'), (_drh_sp, 'sp45'), (_drh_lr, 'learned')):
    if list(_drh_frame.columns) != ['id', 'tvt']:
        raise RuntimeError(f'D27 residual-heavy invalid {_drh_name} schema')
    if not _drh_frame['id'].astype(str).equals(_drh_base['id'].astype(str)):
        raise RuntimeError(f'D27 residual-heavy {_drh_name} id mismatch')
_drh_s = _drh_pd.to_numeric(_drh_sp['tvt'], errors='coerce').to_numpy(float)
_drh_l = _drh_pd.to_numeric(_drh_lr['tvt'], errors='coerce').to_numpy(float)
_drh_old = _drh_pd.to_numeric(_drh_base['tvt'], errors='coerce').to_numpy(float)
_drh_final = _DRH_W_SP45 * _drh_s + (1.0 - _DRH_W_SP45) * _drh_l
if not _drh_np.isfinite(_drh_final).all():
    raise RuntimeError('D27 residual-heavy route produced non-finite predictions')
_drh_base['tvt'] = _drh_final
_drh_base.to_csv(_DRH_SUB, index=False)
(_DRH_WORK / 'd27_residual_heavy_summary.json').write_text(
    _drh_json.dumps({
        'hidden_run_compatible': True,
        'w_sp45': _DRH_W_SP45,
        'w_grouped_oof_learned': 1.0 - _DRH_W_SP45,
        'rows': int(len(_drh_final)),
        'rms_from_post_contact_base_ft': float(_drh_np.sqrt(_drh_np.mean((_drh_final - _drh_old) ** 2))),
        'rms_between_components_ft': float(_drh_np.sqrt(_drh_np.mean((_drh_l - _drh_s) ** 2))),
    }, indent=2) + '\n',
    encoding='utf-8',
)
print('D27 residual-heavy post-contact transaction complete')
'''


CONTACT_CONSENSUS_CELL = r'''# D27 multi-contact geometric consensus.
# Candidate surfaces use the six run-local formation contacts and are admitted
# only by visible-prefix compatibility. There are no visible well IDs here.
import json as _dcc_json
from pathlib import Path as _DccPath
import numpy as _dcc_np
import pandas as _dcc_pd

_DCC_WORK = _DccPath('/kaggle/working') if _DccPath('/kaggle/working').exists() else _DccPath('.')
_DCC_SUB = _DCC_WORK / 'submission.csv'
_DCC_REFS = ('ANCC', 'ASTNU', 'ASTNL', 'EGFDU', 'EGFDL', 'BUDA')
_DCC_PREFIX_LIMIT = 4.0
_DCC_BLEND = 0.90
_DCC_MOVE_CAP = 8.0
if '_ov_tvt_from_contacts' not in globals():
    raise RuntimeError('D27 contact consensus requires the guarded-contact primitives')
_dcc_sub = _dcc_pd.read_csv(_DCC_SUB)
if list(_dcc_sub.columns) != ['id', 'tvt']:
    raise RuntimeError('D27 contact consensus invalid submission schema')
_dcc_sub['well'] = _dcc_sub['id'].astype(str).str.rsplit('_', n=1).str[0]
_dcc_sub['row_idx'] = _dcc_pd.to_numeric(
    _dcc_sub['id'].astype(str).str.rsplit('_', n=1).str[-1], errors='raise'
).astype(int)
_dcc_pred = _dcc_pd.to_numeric(_dcc_sub['tvt'], errors='coerce').to_numpy(float)
_dcc_rows = []
for _dcc_wid, _dcc_group in _dcc_sub.groupby('well', sort=True):
    _dcc_hw_te_path = _DATA / 'test' / f'{_dcc_wid}__horizontal_well.csv'
    _dcc_hw_tr_path = _DATA / 'train' / f'{_dcc_wid}__horizontal_well.csv'
    _dcc_tw_tr_path = _DATA / 'train' / f'{_dcc_wid}__typewell.csv'
    if not (_dcc_hw_te_path.exists() and _dcc_hw_tr_path.exists() and _dcc_tw_tr_path.exists()):
        _dcc_rows.append({'well': str(_dcc_wid), 'status': 'missing_same_well_inputs'})
        continue
    _dcc_hw_te = _dcc_pd.read_csv(_dcc_hw_te_path)
    _dcc_hw_tr = _dcc_pd.read_csv(_dcc_hw_tr_path)
    _dcc_tw_tr = _dcc_pd.read_csv(_dcc_tw_tr_path)
    _dcc_md_te = _dcc_pd.to_numeric(_dcc_hw_te['MD'], errors='coerce').to_numpy(float)
    _dcc_known = _dcc_hw_te['TVT_input'].notna().to_numpy()
    _dcc_known_tvt = _dcc_pd.to_numeric(
        _dcc_hw_te.loc[_dcc_known, 'TVT_input'], errors='coerce'
    ).to_numpy(float)
    _dcc_candidates = []
    _dcc_meta = []
    for _dcc_ref in _DCC_REFS:
        _dcc_phys = _ov_tvt_from_contacts(_dcc_hw_tr, _dcc_tw_tr, _dcc_ref)
        if _dcc_phys is None:
            continue
        _dcc_md_tr = _dcc_pd.to_numeric(_dcc_hw_tr['MD'], errors='coerce').to_numpy(float)
        _dcc_ok = _dcc_np.isfinite(_dcc_md_tr) & _dcc_np.isfinite(_dcc_phys)
        if int(_dcc_ok.sum()) < 100:
            continue
        _dcc_order = _dcc_np.argsort(_dcc_md_tr[_dcc_ok])
        _dcc_md = _dcc_md_tr[_dcc_ok][_dcc_order]
        _dcc_path = _dcc_np.asarray(_dcc_phys, dtype=float)[_dcc_ok][_dcc_order]
        _dcc_full = _dcc_np.interp(_dcc_md_te, _dcc_md, _dcc_path)
        _dcc_pk = _dcc_full[_dcc_known]
        _dcc_valid = _dcc_np.isfinite(_dcc_pk) & _dcc_np.isfinite(_dcc_known_tvt)
        if int(_dcc_valid.sum()) < 50:
            continue
        # A robust prefix-only datum calibration absorbs formation-reference
        # bias without reading the hidden suffix target.
        _dcc_bias = float(_dcc_np.median(_dcc_known_tvt[_dcc_valid] - _dcc_pk[_dcc_valid]))
        _dcc_bias = float(_dcc_np.clip(_dcc_bias, -4.0, 4.0))
        _dcc_full = _dcc_full + _dcc_bias
        _dcc_rmse = float(_dcc_np.sqrt(
            _dcc_np.mean((_dcc_full[_dcc_known][_dcc_valid] - _dcc_known_tvt[_dcc_valid]) ** 2)
        ))
        if _dcc_rmse <= _DCC_PREFIX_LIMIT:
            _dcc_candidates.append(_dcc_full)
            _dcc_meta.append((_dcc_ref, _dcc_rmse, _dcc_bias))
    if not _dcc_candidates:
        _dcc_rows.append({'well': str(_dcc_wid), 'status': 'no_prefix_compatible_contact'})
        continue
    _dcc_stack = _dcc_np.stack(_dcc_candidates)
    _dcc_r = _dcc_np.asarray([m[1] for m in _dcc_meta], dtype=float)
    _dcc_w = 1.0 / _dcc_np.maximum(_dcc_r, 0.25) ** 2
    _dcc_w /= _dcc_w.sum()
    _dcc_consensus = _dcc_w @ _dcc_stack
    _dcc_positions = _dcc_group.index.to_numpy(int)
    _dcc_ri = _dcc_group['row_idx'].to_numpy(int)
    _dcc_base = _dcc_pred[_dcc_positions]
    _dcc_target = _dcc_consensus[_dcc_ri]
    _dcc_move = _dcc_np.clip(_dcc_target - _dcc_base, -_DCC_MOVE_CAP, _DCC_MOVE_CAP)
    _dcc_final = _dcc_base + _DCC_BLEND * _dcc_move
    _dcc_pred[_dcc_positions] = _dcc_final
    _dcc_rows.append({
        'well': str(_dcc_wid),
        'status': 'applied',
        'contacts': '|'.join(m[0] for m in _dcc_meta),
        'prefix_rmse': '|'.join(f'{m[1]:.6f}' for m in _dcc_meta),
        'prefix_bias_ft': '|'.join(f'{m[2]:.6f}' for m in _dcc_meta),
        'rows': int(len(_dcc_positions)),
        'rms_move_ft': float(_dcc_np.sqrt(_dcc_np.mean((_dcc_final - _dcc_base) ** 2))),
        'max_abs_move_ft': float(_dcc_np.max(_dcc_np.abs(_dcc_final - _dcc_base))),
    })
if not _dcc_np.isfinite(_dcc_pred).all():
    raise RuntimeError('D27 contact consensus produced non-finite predictions')
_dcc_sub['tvt'] = _dcc_pred
_dcc_sub[['id', 'tvt']].to_csv(_DCC_SUB, index=False)
_dcc_pd.DataFrame(_dcc_rows).to_csv(_DCC_WORK / 'd27_contact_consensus_report.csv', index=False)
(_DCC_WORK / 'd27_contact_consensus_summary.json').write_text(
    _dcc_json.dumps({
        'hidden_run_compatible': True,
        'contacts': list(_DCC_REFS),
        'prefix_rmse_limit': _DCC_PREFIX_LIMIT,
        'blend': _DCC_BLEND,
        'move_cap_ft': _DCC_MOVE_CAP,
        'well_reports': _dcc_rows,
    }, indent=2) + '\n',
    encoding='utf-8',
)
print('D27 contact consensus:', _dcc_rows)
'''


def final_contract_cell(route: str, expected_sha: str | None = None) -> dict:
    expected = repr(expected_sha)
    code = f'''# D27 immutable final-output contract (read-only).
import hashlib as _d27_hashlib
import json as _d27_json
from pathlib import Path as _D27Path
import numpy as _d27_np
import pandas as _d27_pd

_D27_ROUTE = {route!r}
_D27_EXPECTED_SHA = {expected}
_D27_WORK = _D27Path('/kaggle/working') if _D27Path('/kaggle/working').exists() else _D27Path('.')
_D27_SUB = _D27_WORK / 'submission.csv'
_d27_roots = []
if globals().get('CFG') is not None:
    for _d27_attr in ('DATA', 'dataset_path'):
        if hasattr(CFG, _d27_attr):
            _d27_roots.append(_D27Path(getattr(CFG, _d27_attr)))
_d27_roots.extend([
    _D27Path('/kaggle/input/competitions/rogii-wellbore-geology-prediction'),
    _D27Path('/kaggle/input/rogii-wellbore-geology-prediction'),
])
_D27_SAMPLE = next(
    (_root / 'sample_submission.csv' for _root in _d27_roots
     if (_root / 'sample_submission.csv').exists()),
    None,
)
if _D27_SAMPLE is None:
    raise RuntimeError('D27 contract could not locate sample_submission.csv')
_d27_sub = _d27_pd.read_csv(_D27_SUB)
_d27_sample = _d27_pd.read_csv(_D27_SAMPLE)
if list(_d27_sub.columns) != ['id', 'tvt'] or len(_d27_sub) != 14151 or len(_d27_sample) != 14151:
    raise RuntimeError('D27 invalid columns or row count')
_d27_sub['id'] = _d27_sub['id'].astype(str)
_d27_sample['id'] = _d27_sample['id'].astype(str)
if _d27_sub['id'].duplicated().any() or not _d27_sub['id'].equals(_d27_sample['id']):
    raise RuntimeError('D27 IDs are duplicated or out of sample order')
_d27_pred = _d27_pd.to_numeric(_d27_sub['tvt'], errors='coerce').to_numpy(dtype=float)
if not _d27_np.isfinite(_d27_pred).all():
    raise RuntimeError('D27 predictions contain non-finite values')
_d27_sha = _d27_hashlib.sha256(_D27_SUB.read_bytes()).hexdigest()
if _D27_EXPECTED_SHA is not None and _d27_sha != _D27_EXPECTED_SHA:
    raise RuntimeError(
        f'D27 exact-reproduction SHA mismatch: {{_d27_sha}} != {{_D27_EXPECTED_SHA}}'
    )
_d27_report = {{
    'route': _D27_ROUTE,
    'rows': int(len(_d27_sub)),
    'ordered_unique_ids': True,
    'finite_tvt': True,
    'file_sha256': _d27_sha,
    'expected_sha256': _D27_EXPECTED_SHA,
    'expected_sha256_match': _D27_EXPECTED_SHA is None or _d27_sha == _D27_EXPECTED_SHA,
    'prediction_sha256': _d27_hashlib.sha256(
        _d27_np.asarray(_d27_pred, dtype='<f8').tobytes()
    ).hexdigest(),
    'tvt_min': float(_d27_pred.min()),
    'tvt_max': float(_d27_pred.max()),
    'tvt_mean': float(_d27_pred.mean()),
}}
(_D27_WORK / 'd27_final_audit.json').write_text(
    _d27_json.dumps(_d27_report, indent=2) + '\\n',
    encoding='utf-8',
)
print('D27 FINAL AUDIT', _d27_report)
'''
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": code,
    }


def prepare_frontier_repro() -> dict:
    source_notebook = read_json(notebook_path(FRONTIER_SOURCE))
    notebook = copy.deepcopy(source_notebook)
    notebook["cells"].insert(
        0,
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": (
                "# ROGII D27 Frontier II Exact Reproduction\n\n"
                "Exact current-source private reproduction of prvsiyan's "
                "[`rogii-public-score-frontier-ii-visuals`]"
                "(https://www.kaggle.com/code/prvsiyan/"
                "rogii-public-score-frontier-ii-visuals). The public score "
                "claim is not inherited. This Version 1 must reproduce the "
                "downloaded public artifact byte-for-byte or abort before it "
                "can be considered for submission.\n"
            ),
        },
    )
    notebook["cells"].append(
        final_contract_cell("frontier_ii_exact", FRONTIER_EXPECTED_SHA)
    )
    strip_runtime(notebook)

    out_dir = OUT / "frontier_ii_exact"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "notebook.ipynb").write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    metadata = read_json(FRONTIER_SOURCE / "kernel-metadata.json")
    metadata.pop("id_no", None)
    metadata.update(
        {
            "id": "muelsyse111/rogii-d27-frontier-ii-exact-repro",
            "title": "ROGII D27 Frontier II Exact Repro",
            "code_file": "notebook.ipynb",
            "is_private": True,
            "enable_tpu": False,
            "enable_internet": False,
        }
    )
    (out_dir / "kernel-metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "route": "frontier_ii_exact",
        "slug": metadata["id"],
        "expected_sha256": FRONTIER_EXPECTED_SHA,
    }


def _cell_source(cell: dict) -> str:
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else str(source)


def _find_cell(notebook: dict, needle: str) -> int:
    matches = [
        index
        for index, cell in enumerate(notebook["cells"])
        if needle in _cell_source(cell)
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one notebook cell containing {needle!r}, got {matches}")
    return matches[0]


def _code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source,
    }


def prepare_structural_route(
    *,
    route: str,
    slug: str,
    title: str,
    description: str,
    mutate,
) -> dict:
    notebook = copy.deepcopy(read_json(notebook_path(FRONTIER_SOURCE)))
    notebook["cells"].insert(
        0,
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": (
                f"# {title}\n\n"
                f"{description}\n\n"
                "This D27 Version 1 is a hidden-run-compatible structural "
                "experiment derived from prvsiyan's Frontier II source. It "
                "contains no visible well IDs in the added scoring mechanism "
                "and inherits no source-team leaderboard score.\n"
            ),
        },
    )
    mutate(notebook)
    notebook["cells"].append(final_contract_cell(route))
    strip_runtime(notebook)

    out_dir = OUT / route
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "notebook.ipynb").write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    metadata = read_json(FRONTIER_SOURCE / "kernel-metadata.json")
    metadata.pop("id_no", None)
    metadata.pop("machine_shape", None)
    metadata.update(
        {
            "id": slug,
            "title": title,
            "code_file": "notebook.ipynb",
            "is_private": True,
            "enable_gpu": False,
            "enable_tpu": False,
            "enable_internet": False,
        }
    )
    (out_dir / "kernel-metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {"route": route, "slug": slug, "expected_sha256": None}


def mutate_residual_heavy(notebook: dict) -> None:
    index = _find_cell(notebook, "## Visible-Prefix Calibration")
    notebook["cells"].insert(index, _code_cell(RESIDUAL_HEAVY_CELL))


def mutate_beam_posterior(notebook: dict) -> None:
    index = _find_cell(notebook, "SUBMISSION_PROFILE = 'vp_balanced_modelpkg_005'")
    source = _cell_source(notebook["cells"][index])
    source = source.replace(
        "SUBMISSION_PROFILE = 'vp_balanced_modelpkg_005'",
        "SUBMISSION_PROFILE = 'bimodal_guarded'",
        1,
    )
    source += (
        "\n# D27 state-space posterior route: use a wider generic datum scan and "
        "retain posterior uncertainty.\n"
        "BIMODAL_DZ_RANGE = 28.0\n"
        "BIMODAL_DZ_STEP = 0.5\n"
        "BUNDLE_MIN = 8.0\n"
        "BUNDLE_MAX = 28.0\n"
        "BIMODAL_J_RATIO_EPS = 0.25\n"
        "BIMODAL_TRIGGER_MIN_MEDIAN_DIFF = 8.0\n"
        "BIMODAL_TRIGGER_MIN_P90_DIFF = 12.0\n"
        "BIMODAL_TRIGGER_MIN_BIG_DIFF_FRAC = 0.10\n"
        "BIMODAL_TRIGGER_BIG_DIFF_THRESHOLD = 10.0\n"
        "RUN_GUARDED_OVERLAP_OVERRIDE = False\n"
        "print('D27 beam route disables the byte-overwriting contact guard')\n"
        "print('D27 beam posterior scan enabled')\n"
    )
    notebook["cells"][index]["source"] = source


def mutate_gated_ensemble(notebook: dict) -> None:
    index = _find_cell(notebook, "## Visible-Prefix Calibration")
    notebook["cells"].insert(index, _code_cell(GATED_ENSEMBLE_CELL))


def mutate_contact_consensus(notebook: dict) -> None:
    index = _find_cell(notebook, "# Final submission audit:")
    notebook["cells"].insert(index, _code_cell(CONTACT_CONSENSUS_CELL))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    prepared = [prepare_frontier_repro()]
    prepared.append(
        prepare_structural_route(
            route="residual_heavy",
            slug="muelsyse111/rogii-d27-residual-postcontact-r1",
            title="ROGII D27 Residual Postcontact R1",
            description=(
                "Tests a materially stronger grouped-OOF learned-trajectory "
                "residual branch (85%) against the physical/PF anchor (15%)."
            ),
            mutate=mutate_residual_heavy,
        )
    )
    prepared.append(
        prepare_structural_route(
            route="beam_posterior",
            slug="muelsyse111/rogii-d27-beam-posterior-no-contact",
            title="ROGII D27 Beam Posterior No Contact",
            description=(
                "Tests a widened heel-calibrated GR datum scan with posterior "
                "branch averaging, prefix trust, and state uncertainty gates."
            ),
            mutate=mutate_beam_posterior,
        )
    )
    prepared.append(
        prepare_structural_route(
            route="contact_consensus",
            slug="muelsyse111/rogii-d27-contact-sixform-r2",
            title="ROGII D27 Contact Sixform R2",
            description=(
                "Tests a robust six-formation geometric consensus admitted "
                "only by visible-prefix compatibility."
            ),
            mutate=mutate_contact_consensus,
        )
    )
    prepared.append(
        prepare_structural_route(
            route="gated_ensemble",
            slug="muelsyse111/rogii-d27-adaptive-branchgate-r1",
            title="ROGII D27 Adaptive Branchgate R1",
            description=(
                "Tests row-adaptive weighting of the grouped-OOF learned "
                "trajectory and physical/PF trajectory from their run-local "
                "disagreement."
            ),
            mutate=mutate_gated_ensemble,
        )
    )
    print(json.dumps(prepared, indent=2))


if __name__ == "__main__":
    main()
