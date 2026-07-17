from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


SRC = Path(__file__).parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rogii.particle import ParticleConfig, predict_particle_ensemble


class ParticleTests(unittest.TestCase):
    def test_particle_output_is_finite_and_aligned(self) -> None:
        tw_tvt = np.arange(0.0, 31.0, 0.5)
        tw_gr = 80.0 + 25.0 * np.sin(tw_tvt / 2.0)
        target = np.linspace(10.0, 15.0, 60)
        z = np.linspace(-100.0, -105.0, 60)
        frame = pd.DataFrame(
            {
                "MD": np.arange(60, dtype=float),
                "Z": z,
                "GR": np.interp(target, tw_tvt, tw_gr),
                "TVT": target,
                "TVT_input": np.r_[target[:30], np.full(30, np.nan)],
            }
        )
        typewell = pd.DataFrame({"TVT": tw_tvt, "GR": tw_gr})
        indices, prediction, diagnostics = predict_particle_ensemble(
            frame,
            typewell,
            config=ParticleConfig(particles=100, seeds=4, initial_u_sigma=1.0),
        )
        np.testing.assert_array_equal(indices, np.arange(30, 60))
        self.assertTrue(np.isfinite(prediction).all())
        self.assertGreaterEqual(diagnostics.effective_seed_count, 1.0)


if __name__ == "__main__":
    unittest.main()
