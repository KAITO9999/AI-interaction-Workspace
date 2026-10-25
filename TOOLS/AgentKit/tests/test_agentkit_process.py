import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import agentkit_process


class AgentKitProcessTests(unittest.TestCase):
    def test_runs_argv_without_shell_interpolation(self):
        result = agentkit_process.run_process(
            [sys.executable, "-c", "import sys; print(sys.argv[1])", "$(echo should-not-run); value"],
            timeout=3,
        )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["stdout"].strip(), "$(echo should-not-run); value")
        self.assertFalse(result["timed_out"])

    def test_timeout_is_distinct_from_nonzero_exit(self):
        timeout = agentkit_process.run_process(
            [sys.executable, "-c", "import time; time.sleep(5)"], timeout=0.2
        )
        failure = agentkit_process.run_process(
            [sys.executable, "-c", "raise SystemExit(7)"], timeout=3
        )
        self.assertEqual((timeout["status"], timeout["returncode"]), ("TIMEOUT", 124))
        self.assertTrue(timeout["timed_out"])
        self.assertIn("TIMEOUT after", timeout["stderr"])
        self.assertEqual((failure["status"], failure["returncode"]), ("FAIL", 7))
        self.assertFalse(failure["timed_out"])

    def test_missing_executable_is_unavailable_not_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = str(Path(directory) / "does-not-exist")
            result = agentkit_process.run_process([missing], timeout=2)
        self.assertEqual(result["status"], "UNAVAILABLE")
        self.assertEqual(result["returncode"], 127)
        self.assertTrue(result["launch_error"])

    def test_output_is_drained_but_only_bounded_tail_is_kept(self):
        result = agentkit_process.run_process(
            [sys.executable, "-c", "import sys; sys.stdout.write('x' * 50000)"],
            timeout=3,
            output_limit=128,
        )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["stdout"], "x" * 128)
        self.assertTrue(result["stdout_truncated"])
        self.assertFalse(result["stderr_truncated"])

    @unittest.skipUnless(os.name == "posix", "process-group behavior is POSIX-specific")
    def test_timeout_terminates_descendants_in_process_group(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "child-survived"
            child_code = (
                "import time; from pathlib import Path; time.sleep(0.8); "
                f"Path({str(marker)!r}).write_text('alive')"
            )
            parent_code = (
                "import subprocess,sys,time; "
                "subprocess.Popen([sys.executable, '-c', sys.argv[1]]); "
                "time.sleep(30)"
            )
            # The child inherits the supervised process group and must be killed.
            result = agentkit_process.run_process(
                [sys.executable, "-c", parent_code, child_code], timeout=0.2
            )
            self.assertEqual(result["status"], "TIMEOUT")
            time.sleep(0.9)
            self.assertFalse(marker.exists())

    def test_invalid_arguments_and_limits_are_rejected(self):
        with self.assertRaises(ValueError):
            agentkit_process.run_process([], timeout=1)
        with self.assertRaises(ValueError):
            agentkit_process.run_process([sys.executable, "-c", "pass"], timeout=0)
        with self.assertRaises(ValueError):
            agentkit_process.run_process([sys.executable, "-c", "pass"], timeout=1, output_limit=0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
