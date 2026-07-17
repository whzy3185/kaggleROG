from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


SRC = Path(__file__).parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rogii.sequence import HMMConfig, predict_gr_hmm


class SequenceTests(unittest.TestCase):
    def test_hmm_tracks_unambiguous_typewell_signature(self) -> None:
        tvt_grid = np.arange(0.0, 40.5, 0.5)
        type_gr = 80.0 + 30.0 * np.sin(tvt_grid / 2.7) + 0.5 * tvt_grid
        target = np.linspace(10.0, 20.0, 80)
        horizontal_gr = np.interp(target, tvt_grid, type_gr)
        frame = pd.DataFrame(
            {
                "MD": np.arange(len(target), dtype=float),
                "GR": horizontal_gr,
                "TVT": target,
                "TVT_input": np.r_[target[:40], np.full(40, np.nan)],
            }
        )
        typewell = pd.DataFrame({"TVT": tvt_grid, "GR": type_gr})
        indices, prediction, posterior_std, diagnostics = predict_gr_hmm(
            frame,
            typewell,
            config=HMMConfig(
                step=0.25,
                half_width=15.0,
                position_sigma=0.25,
                max_abs_drift=0.2,
                min_gr_sigma=1.0,
                max_gr_sigma=5.0,
            ),
        )
        self.assertEqual(len(indices), 40)
        self.assertLess(float(np.sqrt(np.mean((prediction - target[indices]) ** 2))), 1.0)
        self.assertTrue(np.isfinite(posterior_std).all())
        self.assertLess(diagnostics.max_edge_mass, 0.25)


if __name__ == "__main__":
    unittest.main()
