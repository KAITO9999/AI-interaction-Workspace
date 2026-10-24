import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "agentkit_watch.py"


def run(*args, timeout=10):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True,
                          text=True, timeout=timeout, check=False)


class AgentKitWatchTests(unittest.TestCase):
    def test_initial_verification_runs_explicit_argv_without_shell(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "src").mkdir()
            result = run("--root", directory, "--watch", "src", "--max-runs", "1",
                         "--json", "--", sys.executable, "-c", "print('verified')")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            events = [json.loads(line) for line in result.stdout.splitlines()]
            self.assertEqual(events[0]["status"], "PASS")
            self.assertIn("verified", events[0]["stdout"])
            self.assertEqual(events[-1]["summary"], "watch stopped")
            self.assertNotIn("stdout", events[-1]["events"][0])

    def test_nonzero_verification_is_reported_as_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "src").mkdir()
            result = run("--root", directory, "--watch", "src", "--max-runs", "1",
                         "--json", "--", sys.executable, "-c", "raise SystemExit(7)")
            self.assertEqual(result.returncode, 1)
            report = json.loads(result.stdout.splitlines()[0])
            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(report["returncode"], 7)

    def test_watch_root_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run("--root", directory, "--watch", "../outside", "--max-runs", "1",
                         "--", sys.executable, "-c", "pass")
            self.assertEqual(result.returncode, 2)
            self.assertIn("initial snapshot failed", result.stderr)

    def test_version_and_help(self):
        result = run("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("--watch", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
