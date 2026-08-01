from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rogii.geoanchor_oof import (  # noqa: E402
    OOFReplay,
    contact_trajectory,
    summarize_by_well,
)


def test_summarize_by_well_uses_suffix_row_weights():
    index = pd.DataFrame(
        {
            "well_id": ["a", "a", "b"],
            "target": [1.0, 3.0, 2.0],
        }
    )
    replay = OOFReplay(
        index=index,
        base_predictions=pd.DataFrame({"base": [1.0, 1.0, 1.0]}),
        ridge_prediction=np.array([1.0, 2.0, 2.0]),
        warmup_prediction=np.array([0.0, 0.0, 0.0]),
        trainer_audit=pd.DataFrame(),
        ridge_fold_audit=pd.DataFrame(),
    )
    detail = summarize_by_well(replay).set_index("well_id")
    assert detail.loc["a", "n_eval"] == 2
    assert np.isclose(detail.loc["a", "rmse_anchor"], np.sqrt(5.0))
    assert np.isclose(detail.loc["a", "rmse_ridge"], np.sqrt(0.5))
    assert np.isclose(detail.loc["b", "rmse_ridge"], 0.0)


def test_contact_trajectory_uses_only_named_offset_column():
    z = 100.0 + np.arange(60)
    formation = 10.0 + 0.5 * np.arange(60)
    raw = 200.0 - z + formation
    visible = raw + 890.0
    visible[-1] = np.nan
    horizontal = pd.DataFrame(
        {
            "Z": z,
            "EGFDU": formation,
            "TVT_input": visible,
            "TVT": np.full(60, -9999.0),
        }
    )
    typewell = pd.DataFrame({"Geology": ["EGFDU"], "TVT": [200.0]})
    prediction = contact_trajectory(
        horizontal,
        typewell,
        offset_target_col="TVT_input",
    )
    assert np.allclose(prediction, raw + 890.0)
