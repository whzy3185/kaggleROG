from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rogii.local_score import analyze_package, pooled_rmse  # noqa: E402


def _package(candidate_scale: float) -> pd.DataFrame:
    rows = []
    for well in range(20):
        n_eval = 100 + well
        field = well % 5
        for candidate, rmse in (("anchor", 10.0), ("candidate", candidate_scale)):
            rows.append(
                {
                    "package": "synthetic",
                    "candidate": candidate,
                    "well_id": f"w{well:02d}",
                    "n_eval": n_eval,
                    "sse": rmse**2 * n_eval,
                    "validation_scope": "unit test",
                    "field": field,
                }
            )
    return pd.DataFrame(rows)


def test_pooled_rmse_uses_row_weights():
    frame = pd.DataFrame({"sse": [100.0, 900.0], "n_eval": [1, 9]})
    assert np.isclose(pooled_rmse(frame), 10.0)


def test_bootstrap_supports_uniform_improvement():
    summary = analyze_package(
        _package(9.0),
        reference_candidate="anchor",
        public_wells=10,
        private_wells=15,
        iterations=500,
        seed=7,
    )
    candidate = summary.set_index("candidate").loc["candidate"]
    assert np.isclose(candidate["pooled_rmse"], 9.0)
    assert np.isclose(candidate["delta_vs_reference"], -1.0)
    assert candidate["private148_delta_q95"] < 0
    assert np.isclose(candidate["private148_p_improve"], 1.0)


def test_bootstrap_rejects_uniform_degradation():
    summary = analyze_package(
        _package(11.0),
        reference_candidate="anchor",
        public_wells=10,
        private_wells=15,
        iterations=500,
        seed=9,
    )
    candidate = summary.set_index("candidate").loc["candidate"]
    assert candidate["private148_delta_q05"] > 0
    assert candidate["verdict"] == "rejected"


def test_numerical_tie_is_not_reported_as_promising():
    summary = analyze_package(
        _package(10.0 - 1e-12),
        reference_candidate="anchor",
        public_wells=10,
        private_wells=15,
        iterations=500,
        seed=11,
    )
    candidate = summary.set_index("candidate").loc["candidate"]
    assert candidate["verdict"] == "inconclusive"
