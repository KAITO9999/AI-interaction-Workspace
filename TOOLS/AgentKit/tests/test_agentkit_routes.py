import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "agentkit_routes.py"


class RouteSelectionTests(unittest.TestCase):
    def test_plan_selects_python_fallback_when_preferred_command_is_absent(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "python-lint", "--plan", "--force-fallback"],
            capture_output=True, text=True, timeout=10, check=False
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["route"], "agentkit_fallback")
        self.assertFalse(report["automatic_install"])

    def test_execution_prints_compatibility_warning_for_fallback(self):
        with __import__("tempfile").TemporaryDirectory() as directory:
            source = Path(directory) / "sample.py"
            source.write_text("value = 1\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "python-lint", str(source), "--force-fallback"],
                capture_output=True, text=True, timeout=10, check=False
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("注意、代替コマンドな為既存とは動作が異なります。", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
