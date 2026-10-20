import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "agentkit_observe.py"


class ObserveRunnerTests(unittest.TestCase):
    def test_runs_child_and_records_process_output_and_completion(self):
        with tempfile.TemporaryDirectory() as temporary:
            log_dir = Path(temporary) / "logs"
            result = subprocess.run(
                [
                    sys.executable, str(SCRIPT), "--log-dir", str(log_dir),
                    "--trace", "off", "--interval", "0.2", "--duration", "2",
                    "--", sys.executable, "-c", "print('observe-child-ok')",
                ],
                capture_output=True, text=True, timeout=10, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("observe-child-ok", result.stdout)
            self.assertTrue((log_dir / "events.txt").is_file())
            records = [
                json.loads(line)
                for line in (log_dir / "events.txt").read_text(encoding="utf-8").splitlines()
            ]
            events = [record["event"] for record in records]
            self.assertIn("write_probe_succeeded", events)
            self.assertIn("process_started", events)
            self.assertIn("child_output", events)
            self.assertIn("session_end", events)

    def test_write_failure_is_reported_without_alternate_path_retry(self):
        with tempfile.TemporaryDirectory() as temporary:
            not_a_directory = Path(temporary) / "regular-file"
            not_a_directory.write_text("block directory creation", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable, str(SCRIPT), "--log-dir", str(not_a_directory),
                    "--trace", "off", "--", sys.executable, "-c", "pass",
                ],
                capture_output=True, text=True, timeout=10, check=False,
            )
            self.assertEqual(result.returncode, 2)
            records = [json.loads(line) for line in result.stderr.splitlines()]
            self.assertEqual(records[-1]["event"], "write_probe_denied")
            self.assertIn("no alternate path or retry", records[-1]["action"])
            self.assertFalse((Path(temporary) / "events.txt").exists())

    def test_requires_child_command(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--log-dir", "/tmp/agentkit-test-unused"],
            capture_output=True, text=True, timeout=10, check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("child command is required", result.stderr)

    def test_duration_limit_is_bounded(self):
        result = subprocess.run(
            [
                sys.executable, str(SCRIPT), "--log-dir", "/tmp/agentkit-test-unused",
                "--duration", "99999", "--", sys.executable, "-c", "pass",
            ],
            capture_output=True, text=True, timeout=10, check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("--duration must be between", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
