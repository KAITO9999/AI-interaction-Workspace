import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

MODULE_PATH = Path(__file__).resolve().parents[1] / "agentkit_capabilities.py"
SPEC = importlib.util.spec_from_file_location("agentkit_capabilities", MODULE_PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(module)


class CapabilityProbeTests(unittest.TestCase):
    def test_discovery_has_schema_and_does_not_execute(self):
        with mock.patch.object(module.shutil, "which", return_value=None) as which:
            report = module.discover(path_value="")
        self.assertEqual(report["schema_version"], 1)
        self.assertFalse(report["discovery_executes_commands"])
        self.assertFalse(report["version_probes_requested"])
        self.assertTrue(report["tools"])
        self.assertTrue(all(not item["installed"] for item in report["tools"]))
        which.assert_called()

    def test_discovery_reports_observed_paths_only(self):
        with mock.patch.object(module.shutil, "which", side_effect=lambda name, path=None: "/opt/bin/" + name if name == "git" else None):
            report = module.discover(path_value="/opt/bin")
        git = next(item for item in report["tools"] if item["name"] == "git")
        self.assertTrue(git["installed"])
        self.assertEqual(git["path"], "/opt/bin/git")
        self.assertEqual(git["probe_status"], "not_run")
        self.assertIsNone(git["version"])

    def test_version_probe_uses_fixed_argv_without_shell(self):
        report = module.discover(path_value="")
        report["tools"][0].update({"installed": True, "path": "/safe/playwright-cli"})
        with mock.patch.object(module.subprocess, "run", return_value=mock.Mock(stdout="1.2.3\n", returncode=0)) as run:
            module.probe_versions(report, timeout=0.5, output_limit=20)
        args, kwargs = run.call_args
        self.assertEqual(args[0], ["/safe/playwright-cli", "--version"])
        self.assertFalse(kwargs["shell"])
        self.assertEqual(kwargs["timeout"], 0.5)
        self.assertEqual(report["tools"][0]["version"], "1.2.3")
        self.assertEqual(report["tools"][0]["probe_status"], "version_ok")

    def test_timeout_is_reported_not_retried(self):
        report = module.discover(path_value="")
        report["tools"][0].update({"installed": True, "path": "/safe/playwright-cli"})
        with mock.patch.object(module.subprocess, "run", side_effect=module.subprocess.TimeoutExpired(cmd="x", timeout=0.1)) as run:
            module.probe_versions(report, timeout=0.1)
        self.assertEqual(run.call_count, 1)
        self.assertEqual(report["tools"][0]["probe_status"], "timeout")

    def test_output_is_bounded(self):
        report = module.discover(path_value="")
        report["tools"][0].update({"installed": True, "path": "/safe/playwright-cli"})
        with mock.patch.object(module.subprocess, "run", return_value=mock.Mock(stdout="X" * 900, returncode=0)):
            module.probe_versions(report, output_limit=31)
        self.assertEqual(len(report["tools"][0]["version"]), 31)

    def test_markdown_includes_sources_and_limits(self):
        report = module.discover(path_value="")
        markdown = module.render_markdown(report)
        self.assertIn("https://playwright.dev/docs/getting-started-cli", markdown)
        self.assertIn("does not prove", markdown)

    def test_cli_rejects_unbounded_timeout(self):
        with self.assertRaises(SystemExit) as exc:
            module.main(["--timeout", "100"])
        self.assertEqual(exc.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
