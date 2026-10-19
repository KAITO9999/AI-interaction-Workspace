import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "agentkit_agents.py"
sys.path.insert(0, str(SCRIPT.parent))
import agentkit_agents


class AgentDiscoveryTests(unittest.TestCase):
    def test_local_cli_detection_does_not_claim_authentication(self):
        report = agentkit_agents.discover(lambda name: "/fake/bin/" + name if name == "opencode" else None)
        by_id = {item["id"]: item for item in report["agents"]}
        self.assertEqual(by_id["opencode"]["status"], "cli_detected")
        self.assertEqual(by_id["claude-code"]["status"], "not_detected")
        self.assertIn("authentication", report["detection_scope"])

    def test_hosted_chatgpt_is_not_inferred_from_local_path(self):
        report = agentkit_agents.discover(lambda _name: "/fake/bin/tool")
        chatgpt = next(item for item in report["agents"] if item["id"] == "chatgpt")
        self.assertEqual(chatgpt["status"], "not_locally_detectable")
        self.assertIn("localhost", chatgpt["notes"])

    def test_json_cli_output_is_valid_and_can_filter_agent(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--json", "--agent", "codex"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual([item["id"] for item in report["agents"]], ["codex"])
        self.assertIn("termux-command-execution", report["capability_routes"])

    def test_mcp_profiles_expose_transports_and_verification(self):
        report = agentkit_agents.discover(lambda _name: None)
        by_id = {item["id"]: item for item in report["agents"]}
        for key in ("codex", "claude-code", "opencode"):
            self.assertIn("mcp-stdio", by_id[key]["transports"])
            self.assertTrue(by_id[key]["verification_hint"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
