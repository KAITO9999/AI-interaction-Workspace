import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "mobile_test.py"


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=10, check=False)


class MobileTestPreflightTests(unittest.TestCase):
    def make_project(self, root: Path, min_sdk: int | None = 21) -> Path:
        app = root / "app" / "src" / "main"
        app.mkdir(parents=True)
        if min_sdk is not None:
            (app / "AndroidManifest.xml").write_text(
                f'<manifest xmlns:android="http://schemas.android.com/apk/res/android"><uses-sdk android:minSdkVersion="{min_sdk}" /></manifest>',
                encoding="utf-8",
            )
        else:
            (root / "app" / "build.gradle.kts").write_text(
                "android { defaultConfig { minSdk = providers.gradleProperty(\"androidMinSdk\").get().toInt() } }",
                encoding="utf-8",
            )
        return root

    def test_profile_memory_and_default_android_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            self.make_project(Path(directory), 21)
            result = run("--root", directory, "--json", str(Path(directory) / "report.json"))
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            report = json.loads((Path(directory) / "report.json").read_text(encoding="utf-8"))
            profiles = {item["profile"]: item for item in report["profiles"]}
            self.assertEqual({key: value["ram_gb"] for key, value in profiles.items()},
                             {"low-end": 4, "mid-end": 8, "mid-high": 12, "high-end": 16})
            self.assertEqual(profiles["low-end"]["android_version"], 11)
            self.assertEqual(profiles["mid-end"]["android_version"], 15)
            self.assertIsNone(profiles["mid-high"]["android_version"])
            self.assertIsNone(profiles["high-end"]["android_version"])

    def test_low_end_is_rejected_when_android_11_is_incompatible(self):
        with tempfile.TemporaryDirectory() as directory:
            self.make_project(Path(directory), 31)
            result = run("--root", directory, "--profile", "low-end")
            self.assertEqual(result.returncode, 1)
            self.assertIn("rejected_incompatible", result.stdout)
            self.assertIn("Android 11 API 30", result.stdout)

    def test_unknown_min_sdk_blocks_version_gated_profiles(self):
        with tempfile.TemporaryDirectory() as directory:
            self.make_project(Path(directory), None)
            result = run("--root", directory, "--profile", "low-end")
            self.assertEqual(result.returncode, 1)
            self.assertIn("needs_review_min_sdk_unknown", result.stdout)

    def test_explicit_android_version_overrides_profile_default(self):
        with tempfile.TemporaryDirectory() as directory:
            self.make_project(Path(directory), 31)
            result = run("--root", directory, "--profile", "low-end", "--android-version", "15")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertIn("Android 15 (API 35)", result.stdout)

    def test_min_sdk_override_resolves_gradle_variable(self):
        with tempfile.TemporaryDirectory() as directory:
            self.make_project(Path(directory), None)
            result = run("--root", directory, "--profile", "low-end", "--min-sdk", "23")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertIn("status=eligible", result.stdout)

    def test_non_android_project_is_reported_without_claiming_compatibility(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run("--root", directory, "--profile", "low-end")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertIn("not_android_project", result.stdout)
            self.assertIn("Android compatibility was not assessed", result.stdout)

    def test_unknown_android_major_version_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            self.make_project(Path(directory), 21)
            result = run("--root", directory, "--profile", "low-end", "--android-version", "99")
            self.assertEqual(result.returncode, 2)
            self.assertIn("no API mapping", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
