import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

AGENTKIT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENTKIT_DIR))
import agentkit_watch
import agentkit_work


class AgentKitLogicBoundaryTests(unittest.TestCase):
    def test_watcher_snapshot_changes_only_when_content_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "src" / "main.py"
            target.parent.mkdir()
            target.write_text("value = 1\n", encoding="utf-8")
            first = agentkit_watch.snapshot(root, ["src"])
            same = agentkit_watch.snapshot(root, ["src"])
            self.assertEqual(first[0], same[0])
            target.write_text("value = 2\n", encoding="utf-8")
            changed = agentkit_watch.snapshot(root, ["src"])
            self.assertNotEqual(first[0], changed[0])
            self.assertEqual(list(changed[1]), ["src/main.py"])

    def test_watcher_snapshot_rejects_root_escape_and_skips_nested_symlinks(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            external = Path(outside) / "private.txt"
            external.write_text("secret", encoding="utf-8")
            (root / "src").mkdir()
            try:
                (root / "src" / "outside.txt").symlink_to(external)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            digest, files, warnings = agentkit_watch.snapshot(root, ["src", "../outside"])
            self.assertTrue(digest)
            self.assertNotIn("src/outside.txt", files)
            self.assertIn("../outside", warnings)

    def test_watcher_run_check_preserves_argv_and_bounds_timeout(self):
        result = agentkit_watch.run_check(
            [sys.executable, "-c", "print('$HOME')"], Path.cwd(), 5)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["stdout"].strip(), "$HOME")
        timed = agentkit_watch.run_check(
            [sys.executable, "-c", "import time; time.sleep(2)"], Path.cwd(), 1)
        self.assertEqual(timed["status"], "TIMEOUT")
        self.assertTrue(timed["timed_out"])

    def test_context_regex_casefold_and_exact_line_numbers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "notes.txt").write_text("Alpha\nbeta ALPHA\ngamma\n", encoding="utf-8")
            report = agentkit_work.context_inspect(
                root, "notes.txt", None, None, "alpha", True, 10, 100, True)
            self.assertEqual([(m["line"], m["text"]) for m in report["matches"]],
                             [(1, "Alpha"), (2, "beta ALPHA")])

    def test_context_byte_budget_reports_truncation_without_partial_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "large.txt").write_text("needle" * 20, encoding="utf-8")
            report = agentkit_work.context_inspect(
                root, ".", None, None, "needle", False, 10, 5, False)
            self.assertTrue(report["truncated"])
            self.assertEqual(report["matches"], [])
            self.assertLessEqual(report["files_scanned_bytes"], 5)

    def test_artifact_extension_hint_does_not_claim_unknown_formats(self):
        self.assertIsNone(agentkit_work._extension_hint(".bin", "unknown / not in magic allowlist"))
        self.assertFalse(agentkit_work._extension_hint(".png", "JPEG image"))
        self.assertTrue(agentkit_work._extension_hint(".apk", "ZIP archive"))

    def test_repo_check_rejects_nonexistent_root_without_side_effects(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "not-created"
            report = agentkit_work.repo_check(root, 1)
            self.assertTrue(report["errors"])
            self.assertFalse(root.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
