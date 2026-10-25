import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "agentkit_work.py"
sys.path.insert(0, str(SCRIPT.parent))
import agentkit_work


def run(*args, cwd=None, env=None, timeout=15):
    return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=cwd, env=env,
                          capture_output=True, text=True, timeout=timeout, check=False)


class AgentKitWorkTests(unittest.TestCase):
    def test_context_reads_requested_line_range_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.py").write_text("one\ntwo\nthree\nfour\n", encoding="utf-8")
            result = run("context", "--root", directory, "--target", "sample.py",
                         "--start", "2", "--end", "3", "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual([(m["line"], m["text"]) for m in report["matches"]], [(2, "two"), (3, "three")])

    def test_context_search_caps_output_and_skips_dependency_dirs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "src" / "a.py").write_text("needle\nneedle\nneedle\n", encoding="utf-8")
            (root / "node_modules").mkdir()
            (root / "node_modules" / "bad.js").write_text("needle\n", encoding="utf-8")
            result = run("context", "--root", directory, "--pattern", "needle", "--max-lines", "2", "--json")
            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(len(report["matches"]), 2)
            self.assertTrue(report["truncated"])
            self.assertTrue(all("node_modules" not in item["path"] for item in report["matches"]))

    def test_context_rejects_path_escape_and_invalid_regex(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = run("context", "--root", directory, "--target", "../outside", "--json")
            self.assertEqual(result.returncode, 1)
            self.assertIn("escapes root", json.loads(result.stdout)["errors"][0])
            (root / "a.txt").write_text("abc", encoding="utf-8")
            result = run("context", "--root", directory, "--pattern", "[", "--regex", "--json")
            self.assertEqual(result.returncode, 1)
            self.assertIn("regular expression", json.loads(result.stdout)["summary"])

    def test_context_does_not_follow_symlink_outside_root(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            secret = Path(outside) / "secret.txt"
            secret.write_text("needle-secret", encoding="utf-8")
            try:
                (root / "escape.txt").symlink_to(secret)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            result = run("context", "--root", directory, "--pattern", "needle", "--json")
            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(report["matches"], [])

    def test_artifact_inspect_reports_hash_and_magic_without_modifying(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "image.png"
            payload = b"\x89PNG\r\n\x1a\n" + b"test"
            path.write_bytes(payload)
            before = path.read_bytes()
            result = run("artifact-inspect", str(path), "--json")
            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(report["artifacts"][0]["magic_type"], "PNG image")
            self.assertEqual(len(report["artifacts"][0]["sha256"]), 64)
            self.assertEqual(path.read_bytes(), before)

    def test_artifact_inspect_omits_hash_when_byte_budget_exceeded(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "large.bin"
            path.write_bytes(b"x" * 100)
            result = run("artifact-inspect", str(path), "--max-bytes", "10", "--json")
            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(report["status"], "LIMIT")
            self.assertEqual(report["artifacts"][0]["status"], "LIMIT")
            self.assertNotIn("sha256", report["artifacts"][0])

    def test_sqlite_inspection_reports_schema_and_counts_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.db"
            conn = sqlite3.connect(path)
            conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT)")
            conn.executemany("INSERT INTO items(name) VALUES (?)", [("a",), ("b",)])
            conn.commit()
            conn.close()
            before = path.read_bytes()
            result = run("sqlite-inspect", str(path), "--row-counts", "--integrity-check", "--json")
            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertEqual(report["tables"][0]["row_count"], 2)
            self.assertEqual(report["checks"][0]["status"], "PASS")
            self.assertEqual(path.read_bytes(), before)

    def test_sqlite_inspection_rejects_missing_database(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run("sqlite-inspect", str(Path(directory) / "missing.db"), "--json")
            self.assertEqual(result.returncode, 1)
            self.assertTrue(json.loads(result.stdout)["errors"])

    def test_lint_python_uses_explicit_files_and_rejects_path_escape(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            good = root / "good.py"
            good.write_text("value = 1\n", encoding="utf-8")
            result = run("lint-python", "--root", directory, "--file", "good.py", "--json")
            self.assertIn(result.returncode, (0, 1))  # Ruff may report style; syntax is still checked.
            result = run("lint-python", "--root", directory, "--file", str(Path(outside) / "x.py"), "--json")
            self.assertEqual(result.returncode, 1)
            self.assertIn("escapes root", json.loads(result.stdout)["errors"][0])

    def test_audit_shell_rejects_unknown_dialect(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x.sh"
            path.write_text("echo ok\n", encoding="utf-8")
            result = run("audit-shell", "--root", directory, "--dialect", "fish", "--json")
            self.assertEqual(result.returncode, 2)
            self.assertIn("invalid choice", result.stderr)

    def test_repo_check_does_not_initialize_non_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run("repo-check", "--root", directory, "--json")
            self.assertEqual(result.returncode, 1)
            self.assertIn("not a Git work tree", json.loads(result.stdout)["errors"][0])
            self.assertFalse((Path(directory) / ".git").exists())


    def test_context_rejects_invalid_line_ranges_and_enforces_byte_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "a.txt").write_text("123456\nneedle\n", encoding="utf-8")
            result = run("context", "--root", directory, "--start", "0", "--json")
            self.assertEqual(result.returncode, 1)
            self.assertIn("line numbers", json.loads(result.stdout)["errors"][0])
            result = run("context", "--root", directory, "--pattern", "needle", "--max-bytes", "3", "--json")
            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(report["matches"], [])
            self.assertTrue(report["truncated"])

    def test_repo_check_reports_real_git_status_without_mutating(self):
        if not shutil.which("git"):
            self.skipTest("git unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            init = subprocess.run(["git", "init", str(root)], capture_output=True, text=True, timeout=10)
            if init.returncode:
                self.skipTest("git init unavailable")
            (root / "untracked.txt").write_text("x\n", encoding="utf-8")
            result = run("repo-check", "--root", directory, "--json")
            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            status = next(item for item in report["checks"] if item["name"] == "status")
            self.assertIn("untracked.txt", status["stdout"])
            self.assertTrue(report["read_only"])
            self.assertFalse((root / ".git" / "index").exists())

    def test_help_and_version_are_available(self):
        result = run("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("context", result.stdout)
        result = run("--version")
        self.assertEqual(result.returncode, 0)
        self.assertIn("0.1.0", result.stdout)


    def test_auto_lint_skips_symlink_files_to_outside_root(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            (root / "safe.py").write_text("value = 1\n", encoding="utf-8")
            external = Path(outside) / "outside.py"
            external.write_text("import os\n", encoding="utf-8")
            try:
                (root / "escape.py").symlink_to(external)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            from unittest.mock import patch
            with patch("agentkit_work.shutil.which", return_value=None):
                report = agentkit_work.lint_python(root, [], 5)
            self.assertEqual(report["status"], "PASS")
            self.assertEqual([item["file"] for item in report["findings"]], ["safe.py"])

    def test_zero_discovered_scripts_is_unavailable_not_success(self):
        with tempfile.TemporaryDirectory() as directory:
            report = agentkit_work.audit_shell(Path(directory), [], "sh", 2)
            self.assertEqual(report["status"], "UNAVAILABLE")
            self.assertTrue(report["errors"])

    def test_process_timeout_status_is_preserved_by_lint_integration(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.py").write_text("value = 1\n", encoding="utf-8")
            timeout_result = {
                "status": "TIMEOUT", "returncode": 124, "stdout": "", "stderr": "TIMEOUT",
                "timed_out": True, "launch_error": None, "stdout_truncated": False,
                "stderr_truncated": False, "duration_seconds": 1, "batch_count": 1,
            }
            with patch("agentkit_work.shutil.which", return_value="/fake/ruff"), patch(
                "agentkit_work._run_file_batches", return_value=timeout_result
            ):
                report = agentkit_work.lint_python(root, ["sample.py"], 1)
            self.assertEqual(report["status"], "TIMEOUT")
            self.assertEqual(report["checks"][0]["status"], "TIMEOUT")



    def test_native_finding_cap_is_reported_as_limit_not_pass(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.py").write_text("import os\nimport json\n", encoding="utf-8")
            with patch("agentkit_work.shutil.which", return_value=None), patch(
                "agentkit_work.MAX_REPORTED_FINDINGS", 1
            ):
                report = agentkit_work.lint_python(root, [], 5)
            self.assertEqual(report["status"], "LIMIT")
            self.assertTrue(report["findings_truncated"])
            self.assertEqual(sum(len(item["findings"]) for item in report["findings"]), 1)

    def test_lint_batches_do_not_call_truncated_output_a_pass(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sample = root / "sample.py"
            sample.write_text("value = 1\n", encoding="utf-8")
            mocked = {
                "returncode": 0, "stdout": "partial", "stderr": "", "timed_out": False,
                "launch_error": None, "capture_error": None,
                "stdout_truncated": True, "stderr_truncated": False,
            }
            with patch("agentkit_work.run_argv", return_value=mocked):
                report = agentkit_work._run_file_batches("/fake/ruff", ["check"], [sample], 5, root)
            self.assertEqual(report["status"], "LIMIT")
            self.assertEqual(report["returncode"], 1)
            self.assertTrue(report["stdout_truncated"])

    def test_file_discovery_reports_limit_without_claiming_complete_scan(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "a.py").write_text("a = 1\n", encoding="utf-8")
            (root / "b.py").write_text("b = 2\n", encoding="utf-8")
            paths, limited = agentkit_work._discover_files(root, root, ".py", limit=1)
            self.assertEqual(len(paths), 1)
            self.assertTrue(limited)



if __name__ == "__main__":
    unittest.main(verbosity=2)
