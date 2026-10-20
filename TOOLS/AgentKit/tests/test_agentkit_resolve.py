import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "agentkit_resolve.py"


def run(*args, env=None):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=env, timeout=10, check=False)


class ResolverTests(unittest.TestCase):
    def empty_path_env(self, directory):
        env = os.environ.copy()
        env["PATH"] = str(directory)
        return env

    def test_json_fallback_valid_and_invalid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid = root / "ok.json"
            valid.write_text('{"ok": true}', encoding="utf-8")
            result = run("json-check", str(valid), "--prefer-fallback", env=self.empty_path_env(root / "empty"))
            self.assertEqual(result.returncode, 0, result.stderr)
            valid.write_text("{bad", encoding="utf-8")
            result = run("json-check", str(valid), "--prefer-fallback", env=self.empty_path_env(root / "empty"))
            self.assertEqual(result.returncode, 5)
            self.assertIn("INVALID JSON", result.stderr)

    def test_search_fallback_skips_dependency_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "src" / "main.py").write_text("needle here\n", encoding="utf-8")
            (root / "node_modules").mkdir()
            (root / "node_modules" / "vendor.js").write_text("needle hidden\n", encoding="utf-8")
            result = run("search", str(root), "--pattern", "needle", "--prefer-fallback", env=self.empty_path_env(root / "empty"))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("main.py:1:needle here", result.stdout)
            self.assertNotIn("vendor.js", result.stdout)

    def test_find_files_fallback_filters_by_name(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "alpha.txt").write_text("a", encoding="utf-8")
            (root / "beta.py").write_text("b", encoding="utf-8")
            result = run("find-files", str(root), "--pattern", ".py", "--prefer-fallback", env=self.empty_path_env(root / "empty"))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("beta.py", result.stdout)
            self.assertNotIn("alpha.txt", result.stdout)

    def test_archive_list_and_sha256_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive_path = root / "sample.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("inside.txt", "hello")
            result = run("archive-list", str(archive_path), "--prefer-fallback", env=self.empty_path_env(root / "empty"))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("inside.txt", result.stdout)
            file_path = root / "data.bin"
            file_path.write_bytes(b"hello")
            result = run("sha256", str(file_path), "--prefer-fallback", env=self.empty_path_env(root / "empty"))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(hashlib.sha256(b"hello").hexdigest(), result.stdout)

    def test_json_report_is_read_only_and_machine_readable(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run("json-check", ".", "--json-report", env=self.empty_path_env(Path(directory) / "empty"))
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["task"], "json-check")
            self.assertTrue(report["fallback_available"])
            self.assertIn("python_fallback", report)

    def test_missing_install_mapping_does_not_run_without_opt_in(self):
        with tempfile.TemporaryDirectory() as directory:
            env = self.empty_path_env(Path(directory) / "empty")
            result = run("json-check", "missing.json", env=env)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("Python standard-library fallback", result.stdout)
            self.assertNotIn("INSTALL ATTEMPT", result.stdout)


    def test_install_opt_in_tries_preferred_tool_before_available_alternative(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bins = root / "bin"
            bins.mkdir()
            brew = bins / "brew"
            brew.write_text("#!/bin/sh\nprintf '%s\\n' \"$*\" > \"$CAPTURE_INSTALL\"\nexit 1\n", encoding="utf-8")
            brew.chmod(0o755)
            find = bins / "find"
            find.write_text("#!/bin/sh\necho fake-find-ran\nexit 0\n", encoding="utf-8")
            find.chmod(0o755)
            capture = root / "install.txt"
            env = self.empty_path_env(bins)
            env["CAPTURE_INSTALL"] = str(capture)
            result = run("find-files", str(root), "--pattern", "alpha", "--install", env=env)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertIn("install fd", capture.read_text(encoding="utf-8"))
            self.assertIn("Preferred command installation failed", result.stderr)
            self.assertIn("fake-find-ran", result.stdout)


    def test_json_fallback_invalid_json_uses_jq_exit_code(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "invalid.json"
            target.write_text('{"ok": }\\n', encoding="utf-8")
            result = run("json-check", str(target), "--prefer-fallback", env=self.empty_path_env(root / "empty"))
            self.assertEqual(result.returncode, 5, result.stdout + result.stderr)
            self.assertIn("INVALID JSON", result.stderr)

    def test_json_fallback_empty_input_matches_jq_empty_filter(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "empty.json"
            target.write_text("  \\n\\t", encoding="utf-8")
            result = run("json-check", str(target), "--prefer-fallback", env=self.empty_path_env(root / "empty"))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_json_fallback_accepts_multiple_json_texts_like_jq(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "stream.json"
            target.write_text('{"one": 1}\\n[2, 3]\\nnull\\n', encoding="utf-8")
            result = run("json-check", str(target), "--prefer-fallback", env=self.empty_path_env(root / "empty"))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_json_fallback_missing_file_uses_jq_system_error_exit_code(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "missing.json"
            result = run("json-check", str(target), "--prefer-fallback", env=self.empty_path_env(root / "empty"))
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("ERROR reading file", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
