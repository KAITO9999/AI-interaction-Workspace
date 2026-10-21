import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "agentkit_ruff.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, timeout=10, check=False
    )


class RuffFallbackTests(unittest.TestCase):
    def test_auto_route_prefers_real_ruff_when_available_and_fallback_when_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "sample.py"
            source.write_text("import os\n\nvalue = 1\n", encoding="utf-8")
            empty_bin = root / "empty-bin"
            empty_bin.mkdir()
            import os
            env = os.environ.copy()
            env["PATH"] = str(empty_bin)
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "check", str(source), "--format", "json"],
                capture_output=True, text=True, env=env, timeout=10, check=False
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["engine"], "agentkit-ruff-lite")
            self.assertTrue(any(item["code"] == "F401" for item in report["diagnostics"]))
            self.assertTrue(any(item["code"] == "F841" for item in report["diagnostics"]) is False)

    def test_syntax_error_is_reported_and_nonzero(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "broken.py"
            source.write_text("def broken(:\n", encoding="utf-8")
            result = run("check", str(source), "--format", "json", "--force-fallback")
            self.assertEqual(result.returncode, 1)
            report = json.loads(result.stdout)
            self.assertTrue(any(item["code"] == "E999" for item in report["diagnostics"]))

    def test_clean_file_passes_subset_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "clean.py"
            source.write_text("def add(left, right):\n    return left + right\n", encoding="utf-8")
            result = run("check", str(source), "--format", "json", "--force-fallback")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["diagnostics"], [])

    def test_format_mode_does_not_claim_compatibility_or_rewrite_source(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "sample.py"
            original = "x=  1\n"
            source.write_text(original, encoding="utf-8")
            result = run("format", str(source), "--check", "--force-fallback")
            self.assertEqual(result.returncode, 3)
            self.assertIn("not Ruff-compatible", result.stderr)
            self.assertEqual(source.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
