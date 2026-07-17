from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import pandas as pd


SCRIPT = Path(__file__).parents[1] / "scripts" / "build_trend_submission.py"
SPEC = importlib.util.spec_from_file_location("build_trend_submission", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TrendSubmissionTests(unittest.TestCase):
    def test_builds_expected_linear_shrinkage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "test").mkdir()
            pd.DataFrame(
                {"MD": [0.0, 1.0, 2.0, 3.0], "TVT_input": [10.0, 10.1, None, None]}
            ).to_csv(root / "test" / "w__horizontal_well.csv", index=False)
            pd.DataFrame({"id": ["w_2", "w_3"], "tvt": [0.0, 0.0]}).to_csv(
                root / "sample_submission.csv", index=False
            )
            result = MODULE.build_trend_submission(
                root, root / "submission.csv", alpha=0.5, window=30
            )
            self.assertAlmostEqual(result.loc[0, "tvt"], 10.15)
            self.assertAlmostEqual(result.loc[1, "tvt"], 10.20)


if __name__ == "__main__":
    unittest.main()
