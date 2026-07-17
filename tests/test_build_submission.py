from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import pandas as pd


SCRIPT = Path(__file__).parents[1] / "scripts" / "build_anchor_submission.py"
SPEC = importlib.util.spec_from_file_location("build_anchor_submission", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class BuildSubmissionTests(unittest.TestCase):
    def test_builds_in_sample_order(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "test").mkdir()
            pd.DataFrame(
                {"TVT_input": [10.0, 11.0, None, None]}
            ).to_csv(root / "test" / "well_a__horizontal_well.csv", index=False)
            pd.DataFrame(
                {"id": ["well_a_3", "well_a_2"], "tvt": [0.0, 0.0]}
            ).to_csv(root / "sample_submission.csv", index=False)
            output = root / "submission.csv"
            result = MODULE.build_anchor_submission(root, output)
            self.assertEqual(result["id"].tolist(), ["well_a_3", "well_a_2"])
            self.assertEqual(result["tvt"].tolist(), [11.0, 11.0])
            self.assertTrue(output.exists())


if __name__ == "__main__":
    unittest.main()
