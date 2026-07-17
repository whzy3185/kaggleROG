from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "verify_submission.py"
SPEC = importlib.util.spec_from_file_location("verify_submission", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class VerifySubmissionTests(unittest.TestCase):
    def _write(self, root: Path, name: str, text: str) -> Path:
        path = root / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_valid_submission(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sample = self._write(root, "sample.csv", "id,tvt\na_1,0\na_2,0\n")
            submission = self._write(root, "submission.csv", "id,tvt\na_1,1.5\na_2,2.5\n")
            summary = MODULE.validate_submission(sample, submission)
            self.assertEqual(summary["rows"], 2)
            self.assertEqual(summary["mean_tvt"], 2.0)

    def test_rejects_wrong_id_order(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sample = self._write(root, "sample.csv", "id,tvt\na_1,0\na_2,0\n")
            submission = self._write(root, "submission.csv", "id,tvt\na_2,1\na_1,2\n")
            with self.assertRaisesRegex(ValueError, "ID order mismatch"):
                MODULE.validate_submission(sample, submission)

    def test_rejects_non_finite_value(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sample = self._write(root, "sample.csv", "id,tvt\na_1,0\n")
            submission = self._write(root, "submission.csv", "id,tvt\na_1,nan\n")
            with self.assertRaisesRegex(ValueError, "Non-finite"):
                MODULE.validate_submission(sample, submission)


if __name__ == "__main__":
    unittest.main()
