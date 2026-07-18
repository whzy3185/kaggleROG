import importlib.util
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "analyze_candidate_disagreement.py"
SPEC = importlib.util.spec_from_file_location("candidate_disagreement", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class CandidateDisagreementTests(unittest.TestCase):
    def test_load_candidate_accepts_exact_contract(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "submission.csv"
            frame = pd.DataFrame({"id": ["well_a_1", "well_a_2"], "tvt": [1.0, 2.0]})
            frame.to_csv(path, index=False)

            prediction, manifest = MODULE.load_candidate(
                "candidate",
                path,
                expected_ids=frame["id"],
            )

            np.testing.assert_allclose(prediction, [1.0, 2.0])
            self.assertEqual(manifest["rows"], 2)
            self.assertEqual(len(manifest["sha256"]), 64)

    def test_load_candidate_rejects_reordered_ids(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "submission.csv"
            pd.DataFrame(
                {"id": ["well_a_2", "well_a_1"], "tvt": [2.0, 1.0]}
            ).to_csv(path, index=False)

            with self.assertRaisesRegex(ValueError, "ID order differs"):
                MODULE.load_candidate(
                    "candidate",
                    path,
                    expected_ids=pd.Series(["well_a_1", "well_a_2"]),
                )


if __name__ == "__main__":
    unittest.main()
