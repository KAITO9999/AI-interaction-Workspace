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
TESTFAST = ROOT / "agentkit_testfast.py"
JSLOAD = ROOT / "agentkit_js_load.py"

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

    def test_audit_ignores_commented_out_code_and_string_literals(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.py").write_text(
                "# TODO eval('not code') while True:\n"
                "def sample():\n"
                "    text = \"eval('not code') TODO while True:\"\n"
                "    return text\n",
                encoding="utf-8",
            )
            (root / "sample.js").write_text(
                "// TODO eval('not code')\n"
                "const text = \"eval('not code')\";\n"
                "/* while (true) { eval('not code'); } */\n",
                encoding="utf-8",
            )
            result = run(AUDIT, str(root), "--json", "report.json")
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads((root / "report.json").read_text(encoding="utf-8"))
            false_positives = [item for item in report["findings"]
                                if item["title"] in {"Dynamic eval call", "Deferred-work marker", "Unbounded loop pattern"}]
            self.assertEqual(false_positives, [])

    def test_testfast_skips_exact_source_file_not_substring(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "test_alpha.py").write_text(
                "import unittest\nclass Alpha(unittest.TestCase):\n"
                "    def test_one(self): self.assertTrue(True)\n",
                encoding="utf-8",
            )
            (root / "test_alphabet.py").write_text(
                "import unittest\nclass Alphabet(unittest.TestCase):\n"
                "    def test_two(self): self.assertTrue(True)\n",
                encoding="utf-8",
            )
            result = run(TESTFAST, "--root", str(root), "--skip-file", "test_alpha.py", "--log-dir", "logs")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertIn("Ran 1 test", result.stderr + result.stdout)
            self.assertIn("test_two", result.stderr + result.stdout)
            self.assertNotIn("test_one", result.stderr + result.stdout)
            skips = (root / "logs" / "test-skips.jsonl").read_text(encoding="utf-8")
            self.assertIn("test_one", skips)
            self.assertNotIn("test_two", skips)

    def test_js_load_model_is_explicit_and_does_not_probe_host(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "main.js").write_text(
                "async function tick(items) {\n"
                "  for (const item of items) {\n"
                "    await fetch('/api/data');\n"
                "  }\n"
                "}\n"
                "export function publicEntry() {}\n"
                "function maybeUnused() {}\n",
                encoding="utf-8",
            )
            result = run(JSLOAD, "--root", str(root), "--profile", "mid", "--json", "load.json")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertNotIn("Environment probe", result.stdout)
            report = json.loads((root / "load.json").read_text(encoding="utf-8"))
            self.assertEqual(report["profile"]["tier"], "mid")
            self.assertFalse(report["profile"]["auto_detected"])
            self.assertIn("runtime_estimate", report)
            self.assertIsNone(report["runtime_estimate"]["milliseconds"])
            self.assertTrue(any(item["category"] == "API_LOAD" for item in report["findings"]))
            self.assertTrue(any(item["title"] == "Call site inside loop" for item in report["findings"]))
            unused = [item for item in report["findings"] if item["title"] == "Function may have no direct references"]
            self.assertEqual([item["detail"].split()[0] for item in unused], ["maybeUnused"])

    def test_js_load_uses_explicit_workload_and_profile_calibration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "main.js").write_text("function run() { fetch('/data'); }\\n", encoding="utf-8")
            (root / "workload.json").write_text(json.dumps({
                "schema_version": 1,
                "operations": [
                    {"kind": "cpu_ops", "count": 1000},
                    {"kind": "memory_bytes", "count": 2000},
                    {"kind": "api", "name": "fetch", "count": 2, "concurrency": 1},
                ],
            }), encoding="utf-8")
            (root / "calibration.json").write_text(json.dumps({
                "schema_version": 1,
                "target_runtime": "test runtime",
                "profiles": {
                    "mid": {
                        "samples": 10,
                        "cpu_ops_per_second": [1000, 2000],
                        "memory_bytes_per_second": [1000, 2000],
                        "api_latency_ms": {"fetch": [10, 20]},
                    }
                },
            }), encoding="utf-8")
            result = run(JSLOAD, "--root", str(root), "--profile", "mid",
                         "--workload-json", "workload.json", "--calibration-json", "calibration.json",
                         "--json", "load.json")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            report = json.loads((root / "load.json").read_text(encoding="utf-8"))
            estimate = report["runtime_estimate"]
            self.assertEqual(estimate["range_ms"], [1520.0, 3040.0])
            self.assertEqual(estimate["confidence"], "HIGH")
            self.assertEqual(estimate["components"]["api_wait_ms"], [20.0, 40.0])

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


    def test_audit_confidence_ranks_duplicates_and_separates_performance_log(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "one.py").write_text("def alpha():\n    return 1234567890123456789012345678901234567890\n", encoding="utf-8")
            (root / "two.py").write_text("def beta():\n    return 1234567890123456789012345678901234567890\n", encoding="utf-8")
            result = run(AUDIT, str(root), "--log-dir", "logs", "--json", "report.json")
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads((root / "report.json").read_text(encoding="utf-8"))
            duplicate_findings = [item for item in report["findings"] if item["category"] == "DUPLICATION"]
            self.assertTrue(duplicate_findings)
            self.assertTrue(all(item["detection_confidence"] == "HIGH" for item in duplicate_findings))
            self.assertTrue(all(item["review_recommended"] is False for item in duplicate_findings))
            self.assertTrue((root / "logs" / "code-audit-findings.jsonl").exists())
            performance = json.loads((root / "logs" / "code-audit-performance.jsonl").read_text(encoding="utf-8").splitlines()[0])
            self.assertGreaterEqual(performance["elapsed_seconds"], 0)
            self.assertGreater(performance["bytes_read"], 0)

    def test_testfast_quick_mode_logs_skipped_tests_and_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "test_sample.py").write_text(
                "import unittest\nclass Sample(unittest.TestCase):\n"
                "    def test_fast_smoke(self): self.assertTrue(True)\n"
                "    def test_slow_full(self): self.assertTrue(True)\n",
                encoding="utf-8",
            )
            script = ROOT / "agentkit_testfast.py"
            result = run(script, "--root", str(root), "--quick", "--log-dir", "logs")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertIn("Environment probe", result.stdout)
            self.assertIn("partial test selection", result.stdout)
            runtime = json.loads((root / "logs" / "test-runtime.jsonl").read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(runtime["selected_count"], 1)
            self.assertEqual(runtime["skipped_count"], 1)
            self.assertIn("environment_fingerprint", runtime)
            skips = (root / "logs" / "test-skips.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(skips), 1)
            self.assertIn("test_slow_full", skips[0])

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
