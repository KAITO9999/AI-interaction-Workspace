import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "agentkit_env.py"
sys.path.insert(0, str(SCRIPT.parent))
import agentkit_env


class EnvironmentProbeTests(unittest.TestCase):
    def test_report_describes_runtime_and_feature_fallbacks(self):
        report = agentkit_env.inspect_environment()
        self.assertEqual(report["tool"], "AgentKit environment capability probe")
        self.assertIn("python_version", report["runtime"])
        self.assertIn("system_call_tracing", report["features"])
        self.assertIn("fallback", report["features"]["system_call_tracing"])
        self.assertFalse(report["active_tests"])

    def test_detection_does_not_claim_network_connectivity(self):
        report = agentkit_env.inspect_environment()
        route = report["features"]["network_access"]
        self.assertIn(route["status"], {"detected_unverified", "blocked"})
        self.assertIn("never tested", route["reason"])

    def test_active_probes_are_local_and_report_subprocess_write(self):
        report = agentkit_env.inspect_environment(active_tests=True)
        self.assertIn("subprocess", report["probes"])
        self.assertIn("write", report["probes"])
        self.assertIsInstance(report["probes"]["subprocess"]["ok"], bool)
        self.assertIsInstance(report["probes"]["write"]["ok"], bool)

    def test_json_cli_output_is_machine_readable_and_feature_filter_works(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--json", "--feature", "json_processing"],
            capture_output=True, text=True, timeout=10, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(list(report["features"]), ["json_processing"])
        self.assertIn("commands", report)
        self.assertIn("limitations", report)

    def test_strace_is_not_claimed_available_without_command(self):
        report = agentkit_env.inspect_environment()
        route = report["features"]["system_call_tracing"]
        found = any(item["command"] == "strace" for item in report["commands"]["found"])
        if not found:
            self.assertEqual(route["status"], "blocked")
        else:
            self.assertEqual(route["status"], "detected_unverified")


if __name__ == "__main__":
    unittest.main(verbosity=2)
