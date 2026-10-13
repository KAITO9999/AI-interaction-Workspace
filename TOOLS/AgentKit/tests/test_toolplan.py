import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "toolplan.py"

class ToolplanTests(unittest.TestCase):
    def test_termux_plan_prints_commands_without_installing(self):
        with tempfile.TemporaryDirectory() as empty:
            env = os.environ.copy()
            env["PATH"] = empty
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--platform", "termux", "--format", "json"],
                env=env, capture_output=True, text=True, timeout=5,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["platform"], "termux")
        self.assertTrue(any("pkg install" in cmd for cmd in report["install_commands"]))
        self.assertTrue(any("pip install pytest" in cmd for cmd in report["install_commands"]))
        self.assertTrue(any("npm install --global typescript" in cmd for cmd in report["install_commands"]))
        self.assertTrue(any("No packages are installed automatically." in note for note in report["notes"]))

    def test_installed_command_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            tool = Path(directory) / "git"
            tool.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            tool.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = directory
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--platform", "unknown", "--format", "json"],
                env=env, capture_output=True, text=True, timeout=5,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        git = next(item for item in report["installed"] if item["command"] == "git")
        self.assertTrue(git["installed"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
