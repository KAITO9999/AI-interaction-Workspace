#!/usr/bin/env python3
"""Build a smartphone test matrix and reject incompatible Android targets.

This is a static preflight/planning tool. It does not emulate Android or measure
real device performance.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

VERSION = "0.1.0"

# Memory budgets are explicit profile inputs, not claims about exact device specs.
PROFILES: dict[str, dict[str, Any]] = {
    "low-end": {"label": "ローエンド", "ram_gb": 4, "default_android": 11, "default_api": 30},
    "mid-end": {"label": "ミドルエンド", "ram_gb": 8, "default_android": 15, "default_api": 35},
    "mid-high": {"label": "ミドルハイ", "ram_gb": 12, "default_android": None, "default_api": None},
    "high-end": {"label": "ハイエンド", "ram_gb": 16, "default_android": None, "default_api": None},
}
ANDROID_API = {5: 21, 6: 23, 7: 24, 8: 26, 9: 28, 10: 29, 11: 30, 12: 31, 13: 33, 14: 34, 15: 35, 16: 36}
ANDROID_NS = "{http://schemas.android.com/apk/res/android}"


def android_project(root: Path) -> bool:
    candidates = (
        root / "app" / "src" / "main" / "AndroidManifest.xml",
        root / "src" / "main" / "AndroidManifest.xml",
        root / "AndroidManifest.xml",
    )
    if any(path.is_file() for path in candidates):
        return True
    return any(root.glob("**/build.gradle")) or any(root.glob("**/build.gradle.kts"))


def _parse_sdk(value: str | None) -> int | None:
    if value is None:
        return None
    match = re.fullmatch(r"\s*(\d+)\s*", value)
    return int(match.group(1)) if match else None


def detect_min_sdk(root: Path) -> tuple[int | None, str]:
    """Read a literal minSdk from common Android manifest/Gradle declarations."""
    manifests = [
        root / "app" / "src" / "main" / "AndroidManifest.xml",
        root / "src" / "main" / "AndroidManifest.xml",
        root / "AndroidManifest.xml",
    ]
    for manifest in manifests:
        if not manifest.is_file():
            continue
        try:
            tree = ET.parse(manifest)
            uses_sdk = tree.getroot().find("uses-sdk")
            if uses_sdk is not None:
                raw = uses_sdk.get(ANDROID_NS + "minSdkVersion")
                parsed = _parse_sdk(raw)
                if parsed is not None:
                    return parsed, f"{manifest.relative_to(root).as_posix()} (manifest)"
                if raw is not None:
                    return None, f"{manifest.relative_to(root).as_posix()} (non-literal minSdkVersion)"
        except (ET.ParseError, OSError, ValueError):
            return None, f"{manifest.relative_to(root).as_posix()} (manifest could not be parsed)"

    patterns = (
        re.compile(r"\bminSdk(?:Version)?\s*(?:=\s*)?(?:\(\s*)?(\d+)\s*\)?"),
        re.compile(r"\bminSdk(?:Version)?\s*=\s*(\d+)\b"),
    )
    for gradle in (root / "app" / "build.gradle", root / "app" / "build.gradle.kts", root / "build.gradle", root / "build.gradle.kts"):
        if not gradle.is_file():
            continue
        try:
            content = gradle.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for pattern in patterns:
            match = pattern.search(content)
            if match:
                return int(match.group(1)), f"{gradle.relative_to(root).as_posix()} (Gradle literal)"
    return None, "minSdkVersion not found as a literal"


def android_target(value: int) -> tuple[int, int]:
    if value not in ANDROID_API:
        raise ValueError(f"Android major version {value} has no API mapping; supported explicit versions: {', '.join(map(str, sorted(ANDROID_API)))}")
    return value, ANDROID_API[value]


def build_report(root: Path, selected_profiles: list[str], explicit_android: int | None, min_sdk_override: int | None) -> dict[str, Any]:
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"project root is not a directory: {root}")
    is_android = android_project(root)
    detected_min, source = detect_min_sdk(root) if is_android else (None, "not an Android project")
    min_sdk = min_sdk_override if min_sdk_override is not None else detected_min
    if min_sdk_override is not None:
        source = "--min-sdk override"
    profiles = []
    for name in selected_profiles:
        spec = PROFILES[name]
        if explicit_android is not None:
            version, api = android_target(explicit_android)
            target_source = "--android-version override"
        else:
            version, api = spec["default_android"], spec["default_api"]
            target_source = "profile default" if version is not None else "not configured by profile"
        item: dict[str, Any] = {
            "profile": name,
            "label": spec["label"],
            "ram_gb": spec["ram_gb"],
            "android_version": version,
            "android_api": api,
            "target_source": target_source,
            "eligible": None,
            "status": "planned",
            "reason": "",
        }
        if not is_android:
            item.update(status="not_android_project", eligible=None,
                        reason="Android project markers were not found; Android compatibility was not assessed.")
        elif api is None:
            item.update(status="eligible_android_version_unbounded", eligible=True,
                        reason="This profile has no default Android-version target; set --android-version to enforce a compatibility gate.")
        elif min_sdk is None:
            item.update(status="needs_review_min_sdk_unknown", eligible=False,
                        reason="Cannot confirm compatibility from a literal minSdkVersion; profile test is blocked until minSdk is resolved or --min-sdk is supplied.")
        elif min_sdk > api:
            item.update(status="rejected_incompatible", eligible=False,
                        reason=f"App minSdkVersion {min_sdk} is higher than Android {version} API {api}; this profile is skipped.")
        else:
            item.update(status="eligible", eligible=True,
                        reason=f"App minSdkVersion {min_sdk} is compatible with Android {version} API {api}; this is preflight only.")
        profiles.append(item)
    return {
        "tool": "AgentKit mobile-test preflight",
        "version": VERSION,
        "root": str(root),
        "is_android_project": is_android,
        "min_sdk": min_sdk,
        "min_sdk_source": source,
        "min_sdk_override_used": min_sdk_override is not None,
        "profiles": profiles,
        "limitations": [
            "This command builds a profile matrix and performs static compatibility preflight only.",
            "It does not start an emulator, install an APK, run app tests, or measure CPU/GPU/frame-time/battery behavior.",
            "Gradle variables, version catalogs, convention plugins, and generated manifests may leave minSdkVersion unresolved; review those projects manually.",
            "RAM values are configured test budgets (4/8/12/16 GB), not a guarantee that every device in a marketing tier has that amount of usable memory.",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentkit-mobile-test",
        description="Build a static smartphone profile matrix and preflight Android minSdk compatibility.",
        epilog="Examples: mobile_test.py --root ./app; mobile_test.py --root ./app --profile low-end --android-version 11 --json /tmp/mobile.json",
    )
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument("--root", default=".", help="Android/project root (default: current directory).")
    parser.add_argument("--profile", action="append", choices=sorted(PROFILES),
                        help="Profile to include; repeat to select several. Default: all profiles.")
    parser.add_argument("--android-version", type=int,
                        help="Force a target Android major version for every selected profile (for example 11 or 15).")
    parser.add_argument("--min-sdk", type=int,
                        help="Explicit minSdkVersion override when the project uses Gradle variables or generated configuration.")
    parser.add_argument("--json", help="Write the full report to this path as JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.min_sdk is not None and args.min_sdk < 1:
        parser.error("--min-sdk must be a positive API level")
    try:
        report = build_report(Path(args.root), args.profile or list(PROFILES), args.android_version, args.min_sdk)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(f"AgentKit mobile-test preflight {VERSION} | Android project={report['is_android_project']} | minSdk={report['min_sdk'] if report['min_sdk'] is not None else 'unknown'}")
    for item in report["profiles"]:
        target = f"Android {item['android_version']} (API {item['android_api']})" if item["android_api"] is not None else "Android target unspecified"
        print(f"{item['label']} ({item['ram_gb']} GB): {item['status']} | {target} | {item['reason']}")
    if args.json:
        target = Path(args.json).expanduser()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"JSON report: {target.resolve()}")
    print("NOTE: This is a static preflight/profile plan, not an emulator or physical-device test.")
    return 0 if all(item["eligible"] is not False for item in report["profiles"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
