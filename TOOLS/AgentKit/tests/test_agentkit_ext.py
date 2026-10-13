import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "agentkit_ext.py"


def run(*args, env=None, timeout=10):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=env, timeout=timeout, check=False)


class AgentKitExtensionTests(unittest.TestCase):
    def test_command_inventory_lists_executable_without_running_it(self):
        with tempfile.TemporaryDirectory() as directory:
            cmd = Path(directory) / "demo-tool"
            marker = Path(directory) / "executed-marker"
            cmd.write_text(f"#!{sys.executable}\nfrom pathlib import Path\nPath({str(marker)!r}).write_text('bad')\n", encoding="utf-8")
            cmd.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = directory
            result = run("commands", "--format", "json", env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual([item["command"] for item in report["commands"]], ["demo-tool"])
            self.assertFalse(marker.exists())

    def test_command_inventory_filters_commands(self):
        with tempfile.TemporaryDirectory() as directory:
            for name in ("tsc", "node", "npm"):
                file = Path(directory) / name
                file.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
                file.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = directory
            result = run("commands", "--filter", "ts", "--format", "tsv", env=env)
            self.assertEqual(result.returncode, 0)
            self.assertIn("tsc\t", result.stdout)
            self.assertNotIn("node\t", result.stdout)

    def test_compile_typescript_invokes_tsc_without_shell(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            bins = Path(directory) / "bin"
            root.mkdir()
            bins.mkdir()
            (root / "main.ts").write_text("const value: number = 1;\n", encoding="utf-8")
            capture = Path(directory) / "args.json"
            fake = bins / "tsc"
            fake.write_text(f"#!{sys.executable}\nimport json, os, sys\nfrom pathlib import Path\nPath(os.environ['CAPTURE_ARGS']).write_text(json.dumps(sys.argv[1:]))\n", encoding="utf-8")
            fake.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = str(bins)
            env["CAPTURE_ARGS"] = str(capture)
            result = run("compile-ts", "--root", str(root), "--out-dir", "out", env=env)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            argv = json.loads(capture.read_text())
            self.assertIn("--outDir", argv)
            self.assertIn(str(root / "out"), argv)

    def test_compile_typescript_missing_compiler_has_clear_exit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            root.mkdir()
            (root / "main.ts").write_text("export {};\n", encoding="utf-8")
            env = os.environ.copy()
            env["PATH"] = str(Path(directory) / "empty")
            result = run("compile-ts", "--root", str(root), env=env)
            self.assertEqual(result.returncode, 127)
            self.assertIn("npm install --save-dev typescript", result.stderr)

    def test_record_change_stores_actor_mode_and_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = run("record-change", "--root", str(root), "--actor", "ai", "--mode", "mixed", "--summary", " updated tooling ", "--path", "TOOLS/a.py", "--path", "README.md")
            self.assertEqual(result.returncode, 0, result.stderr)
            record = json.loads((root / "LOGS/change-ledger.jsonl").read_text().splitlines()[0])
            self.assertEqual(record["actor_type"], "ai")
            self.assertEqual(record["work_mode"], "mixed")
            self.assertEqual(record["paths"], ["README.md", "TOOLS/a.py"])
            self.assertIn("timestamp_utc", record)

    def test_record_change_rejects_ledger_path_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run("record-change", "--root", directory, "--actor", "human", "--mode", "offline", "--summary", "test", "--output", "../escape.jsonl")
            self.assertEqual(result.returncode, 2)

    def test_addon_audit_accepts_consistent_minimal_package(self):
        with tempfile.TemporaryDirectory() as directory:
            archive_path = Path(directory) / "valid.mcaddon"
            bp = {"header": {"uuid": "bp-id", "version": "1.0.0"}, "modules": [{"uuid": "bp-module", "version": "1.0.0"}], "dependencies": [{"uuid": "rp-id", "version": "1.0.0"}]}
            rp = {"header": {"uuid": "rp-id", "version": "1.0.0"}, "modules": [{"uuid": "rp-module", "version": "1.0.0"}]}
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("BP/manifest.json", json.dumps(bp))
                archive.writestr("RP/manifest.json", json.dumps(rp))
                archive.writestr("BP/config.json", '{"ok": true}')
            result = run("audit-addon", str(archive_path), "--no-js-check")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertIn("pack_version_match", result.stdout)

    def test_addon_audit_detects_version_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            archive_path = Path(directory) / "bad.mcaddon"
            bp = {"header": {"uuid": "bp-id", "version": "1.0.0"}, "modules": [], "dependencies": [{"uuid": "rp-id", "version": "2.0.0"}]}
            rp = {"header": {"uuid": "rp-id", "version": "2.0.0"}, "modules": []}
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("BP/manifest.json", json.dumps(bp))
                archive.writestr("RP/manifest.json", json.dumps(rp))
            result = run("audit-addon", str(archive_path), "--no-js-check")
            self.assertEqual(result.returncode, 1)
            self.assertIn("pack_version_match", result.stderr)


    def test_addon_audit_rejects_single_backslash_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            archive_path = Path(directory) / "unsafe.mcaddon"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("BP\\manifest.json", "{}")
            result = run("audit-addon", str(archive_path), "--no-js-check")
            self.assertEqual(result.returncode, 1)
            self.assertIn("archive_paths", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
