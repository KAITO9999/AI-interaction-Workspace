import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "agentkit_code_audit.py"
ZIPSET = ROOT / "agentkit_zipset.py"
PLAN = ROOT / "agentkit_toolplan.py"

def run(script, *args, env=None):
    return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, env=env, timeout=15, check=False)

class AgentKitAddonTests(unittest.TestCase):
    def test_audit_reports_risky_python_calls_and_call_arity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.py").write_text(
                "def greet(name):\n    return name\n\ngreet()\neval('2 + 2')\n",
                encoding="utf-8",
            )
            result = run(AUDIT, str(root), "--json", str(root / "report.json"))
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads((root / "report.json").read_text(encoding="utf-8"))
            titles = {item["title"] for item in report["findings"]}
            self.assertIn("Dynamic eval call", titles)
            self.assertIn("Possible local call arity mismatch: greet", titles)

    def test_audit_rejects_file_outside_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "root"
            root.mkdir()
            outside = Path(directory) / "outside.py"
            outside.write_text("pass\n", encoding="utf-8")
            result = run(AUDIT, str(root), "--file", "../outside.py")
            self.assertEqual(result.returncode, 2)
            self.assertIn("escapes audit root", result.stderr)

    def test_zip_batch_preserves_nested_folders_and_tags_records(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "incoming"
            output = root / "expanded"
            source.mkdir()
            with zipfile.ZipFile(source / "a.zip", "w") as archive:
                archive.writestr("folder/nested.txt", "alpha")
            with zipfile.ZipFile(source / "b.zip", "w") as archive:
                archive.writestr("b.txt", "beta")
            result = run(ZIPSET, "extract", str(source), "--output", str(output), "--tag", "ticket-42")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertTrue((output / "a（zip）" / "folder" / "nested.txt").is_file())
            self.assertTrue((output / "b（zip）" / "b.txt").is_file())
            manifest = json.loads((output / ".agentkit-zip-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(len(manifest["items"]), 2)
            self.assertIn("ticket-42", manifest["items"][0]["tags"])

    def test_zip_traversal_is_rejected_and_no_outside_file_is_written(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "bad.zip"
            output = root / "expanded"
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("../escape.txt", "bad")
            result = run(ZIPSET, "extract", str(source), "--output", str(output))
            self.assertEqual(result.returncode, 1)
            self.assertFalse((root / "escape.txt").exists())
            self.assertIn("unsafe ZIP member path", result.stderr)

    def test_zip_delete_defaults_to_dry_run_and_requires_yes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "one.zip"
            output = root / "expanded"
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("data.txt", "hello")
            extract = run(ZIPSET, "extract", str(source), "--output", str(output), "--tag", "old")
            self.assertEqual(extract.returncode, 0, extract.stderr)
            manifest = json.loads((output / ".agentkit-zip-manifest.json").read_text(encoding="utf-8"))
            target = Path(manifest["items"][0]["destination"])
            dry = run(ZIPSET, "delete", "--output", str(output), "--all")
            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertTrue(target.exists())
            deleted = run(ZIPSET, "delete", "--output", str(output), "--all", "--yes")
            self.assertEqual(deleted.returncode, 0, deleted.stderr)
            self.assertFalse(target.exists())
            self.assertEqual(json.loads((output / ".agentkit-zip-manifest.json").read_text())["items"], [])

    def test_zip_delete_refuses_manifest_path_outside_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "expanded"
            output.mkdir()
            outside = root / "do-not-delete"
            outside.mkdir()
            (output / ".agentkit-zip-manifest.json").write_text(json.dumps({
                "version": 1,
                "items": [{"id": "evil", "destination": str(outside), "created_epoch": 0, "tags": []}],
            }), encoding="utf-8")
            result = run(ZIPSET, "delete", "--output", str(output), "--all", "--yes")
            self.assertEqual(result.returncode, 2)
            self.assertTrue(outside.exists())

    def test_toolplan_reports_available_path_without_invoking_command(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            marker = root / "ran"
            fake = root / "rg"
            fake.write_text(f"#!{sys.executable}\nfrom pathlib import Path\nPath({str(marker)!r}).write_text('ran')\n", encoding="utf-8")
            fake.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = str(root)
            result = run(PLAN, "search", "--json", env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["candidates"][0]["path"], str(fake))
            self.assertFalse(marker.exists())

if __name__ == "__main__":
    unittest.main(verbosity=2)
