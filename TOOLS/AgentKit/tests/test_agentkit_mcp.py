import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "agentkit_mcp.py"


def run(*args, env=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, env=env, timeout=10, check=False
    )


class McpDiscoveryTests(unittest.TestCase):
    def test_discovers_project_mcp_config_without_exposing_secret_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / ".mcp.json"
            config.write_text(json.dumps({
                "mcpServers": {
                    "local-tool": {
                        "command": "python3",
                        "args": ["server.py", "--token", "TOP_SECRET"],
                        "env": {"API_TOKEN": "TOP_SECRET"}
                    },
                    "remote-tool": {"url": "https://mcp.example.test/sse?token=TOP_SECRET"}
                }
            }), encoding="utf-8")
            result = run("--root", str(root), "--home", str(root / "home"), "--format", "json")
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            servers = {item["name"]: item for item in report["servers"]}
            self.assertIn("local-tool", servers)
            self.assertEqual(servers["local-tool"]["command"], "python3")
            self.assertEqual(servers["local-tool"]["env_keys"], ["API_TOKEN"])
            self.assertEqual(servers["remote-tool"]["transport"], "http")
            self.assertNotIn("TOP_SECRET", result.stdout)
            self.assertNotIn("server.py", result.stdout)

    def test_discovers_codex_toml_and_client_specific_transport(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            codex = home / ".codex" / "config.toml"
            codex.parent.mkdir(parents=True)
            codex.write_text(
                '[mcp_servers."codex-local"]\ncommand = "node"\nargs = ["server.js"]\n'
                '[mcp_servers."codex-remote"]\nurl = "https://mcp.example.test/sse?token=HIDDEN"\ntype = "sse"\n',
                encoding="utf-8"
            )
            result = run("--root", str(root / "project"), "--home", str(home), "--format", "json")
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            servers = {item["name"]: item for item in report["servers"]}
            self.assertEqual(servers["codex-local"]["command"], "node")
            self.assertEqual(servers["codex-remote"]["transport"], "sse")
            self.assertNotIn("server.js", result.stdout)
            self.assertNotIn("HIDDEN", result.stdout)

    def test_supports_jsonc_comments_without_leaking_comment_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".vscode").mkdir()
            config = root / ".vscode" / "mcp.json"
            config.write_text(
                '// local MCP config\n{\n  "servers": {\n'
                '    "commented": { "type": "stdio", "command": "python3", "args": ["--secret", "DO_NOT_PRINT"] },\n'
                '  },\n}\n',
                encoding="utf-8"
            )
            result = run("--root", str(root), "--home", str(root / "home"), "--format", "json")
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["servers"][0]["name"], "commented")
            self.assertNotIn("DO_NOT_PRINT", result.stdout)

    def test_reports_invalid_config_without_crashing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".mcp.json").write_text("{broken", encoding="utf-8")
            result = run("--root", str(root), "--home", str(root / "home"), "--format", "json")
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(len(report["config_errors"]), 1)
            self.assertIn(".mcp.json", report["config_errors"][0]["path"])

    def test_no_config_is_an_explicit_empty_result(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = run("--root", str(root), "--home", str(root / "home"), "--format", "json")
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["servers"], [])
            self.assertEqual(report["status"], "no_local_mcp_config_found")
            self.assertIn("GPT-hosted MCP connections are not observable", " ".join(report["limitations"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
