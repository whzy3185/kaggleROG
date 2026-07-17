from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


SRC = Path(__file__).parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rogii.baselines import predict_suffix


class BaselineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.frame = pd.DataFrame(
            {
                "MD": [0.0, 1.0, 2.0, 3.0, 4.0],
                "Z": [-10.0, -11.0, -12.0, -13.0, -14.0],
                "TVT": [15.0, 16.2, 17.4, 18.6, 19.8],
                "TVT_input": [15.0, 16.2, 17.4, np.nan, np.nan],
            }
        )

    def test_anchor_uses_only_last_visible_value(self) -> None:
        indices, prediction = predict_suffix(self.frame, "anchor")
        np.testing.assert_array_equal(indices, [3, 4])
        np.testing.assert_allclose(prediction, [17.4, 17.4])

    def test_u_hold_follows_future_z(self) -> None:
        _, prediction = predict_suffix(self.frame, "u_hold")
        np.testing.assert_allclose(prediction, [18.4, 19.4])

    def test_linear_u_recovers_linear_state(self) -> None:
        _, prediction = predict_suffix(self.frame, "u_linear_all")
        np.testing.assert_allclose(prediction, [18.6, 19.8])

    def test_synthetic_cut_uses_training_tvt_before_cut(self) -> None:
        masked = self.frame.copy()
        masked["TVT_input"] = np.nan
        indices, prediction = predict_suffix(masked, "anchor", cut_index=2)
        np.testing.assert_array_equal(indices, [2, 3, 4])
        np.testing.assert_allclose(prediction, [16.2, 16.2, 16.2])

    def test_rejects_non_contiguous_prefix(self) -> None:
        bad = self.frame.copy()
        bad.loc[4, "TVT_input"] = 19.8
        with self.assertRaisesRegex(ValueError, "contiguous suffix"):
            predict_suffix(bad, "anchor")


if __name__ == "__main__":
    unittest.main()
