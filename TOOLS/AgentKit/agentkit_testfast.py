"""Environment-aware unittest runner with explicit quick selection, skip logs, and calibrated estimates."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import platform
import statistics
import sys
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.1.0"
LOG_DIR_DEFAULT = ".agentkit-logs"

def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item

def environment_profile(root: Path) -> dict:
    memory_kb = None
    try:
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("MemTotal:"):
                memory_kb = int(line.split()[1])
                break
    except (OSError, ValueError, IndexError):
        pass
    minecraft_signals = []
    try:
        for path in root.rglob("*"):
            if any(part in {".git", "node_modules", ".venv", "venv", "build", "dist"} for part in path.parts):
                continue
            if path.is_file() and (path.suffix.lower() in {".mcaddon", ".mcpack"} or
                    (path.name == "manifest.json" and any(part.lower() in {"behavior_packs", "resource_packs", "behavior_pack", "resource_pack"} for part in path.parts))):
                minecraft_signals.append(str(path.relative_to(root)))
                if len(minecraft_signals) >= 20:
                    break
    except OSError:
        pass
    profile = {
        "os": platform.system(),
        "os_release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "cpu_count": os.cpu_count(),
        "memory_total_kb": memory_kb,
        "minecraft_addon_signals": minecraft_signals,
        "minecraft_like_environment": bool(minecraft_signals),
    }
    stable = {key: profile[key] for key in ("os", "machine", "python", "implementation", "cpu_count", "memory_total_kb", "minecraft_like_environment")}
    profile["fingerprint"] = hashlib.sha256(json.dumps(stable, sort_keys=True).encode()).hexdigest()[:16]
    if profile["minecraft_like_environment"]:
        profile["prediction_warning"] = "Minecraft add-on signals found. Runtime predictions can be inaccurate because game engine/version, script APIs, device performance, and in-game state are not fully measured. Probe the actual target environment before relying on estimates."
    else:
        profile["prediction_warning"] = "Host metadata is a partial environment probe; external services, thermal/power limits, virtualized CPU, and runtime-specific conditions may still affect duration."
    return profile

def append_jsonl(path: Path, record: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")

def read_history(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                item = json.loads(line)
                if isinstance(item, dict):
                    records.append(item)
    except (OSError, json.JSONDecodeError):
        return []
    return records

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Project/test discovery root.")
    parser.add_argument("--pattern", default="test*.py")
    parser.add_argument("--quick", action="store_true", help="Run only tests whose IDs contain smoke, fast, sanity, or critical.")
    parser.add_argument("--skip", action="append", default=[], help="Explicit test-ID substring to skip; repeatable and logged.")
    parser.add_argument("--log-dir", default=LOG_DIR_DEFAULT)
    parser.add_argument("--list", action="store_true", help="List discovered tests without running.")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: test root is not a directory: {root}", file=sys.stderr)
        return 2
    profile = environment_profile(root)
    print("Environment probe:")
    print(json.dumps(profile, ensure_ascii=False, indent=2))
    print("Prediction caution: " + profile["prediction_warning"])
    loader = unittest.defaultTestLoader
    try:
        suite = loader.discover(str(root), pattern=args.pattern, top_level_dir=str(root))
        tests = list(flatten(suite))
    except Exception as exc:
        print(f"ERROR: test discovery failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    tests = sorted(tests, key=lambda test: test.id())
    if not tests:
        print("ERROR: no tests discovered; refusing to claim a successful quick run.", file=sys.stderr)
        return 2
    if args.quick:
        quick_tokens = ("smoke", "fast", "sanity", "critical")
        included = [test for test in tests if any(token in (test.id() + " " + getattr(test, "_testMethodName", "")).lower() for token in quick_tokens)]
    else:
        included = list(tests)
    skipped_by_mode = [test for test in tests if test not in included]
    explicitly_skipped = [test for test in included if any(value.lower() in (test.id() + " " + getattr(test, "_testMethodName", "")).lower() for value in args.skip)]
    skipped = skipped_by_mode + explicitly_skipped
    selected = [test for test in included if test not in explicitly_skipped]
    if not selected:
        print("ERROR: selection contains zero tests; refusing to report success.", file=sys.stderr)
        return 2
    print(f"Discovered {len(tests)} tests; selected {len(selected)}; skipped {len(skipped)}.")
    if args.list:
        for test in selected:
            print("RUN  " + test.id())
        for test in skipped:
            print("SKIP " + test.id())
        return 0
    selection_signature = hashlib.sha256("\n".join(test.id() for test in selected).encode()).hexdigest()[:16]
    log_dir = Path(args.log_dir)
    if not log_dir.is_absolute():
        log_dir = root / log_dir
    runtime_log = log_dir / "test-runtime.jsonl"
    skip_log = log_dir / "test-skips.jsonl"
    history = read_history(runtime_log)
    matching = [item["elapsed_seconds"] for item in history
                if item.get("environment_fingerprint") == profile["fingerprint"]
                and item.get("selection_signature") == selection_signature
                and isinstance(item.get("elapsed_seconds"), (int, float))]
    if matching:
        estimate = statistics.median(matching)
        confidence = "HIGH" if len(matching) >= 10 else "MEDIUM" if len(matching) >= 3 else "LOW"
        if profile["minecraft_like_environment"]:
            confidence = "LOW"
    else:
        estimate, confidence = None, "INSUFFICIENT_DATA"
    if estimate is None:
        print("Estimated runtime: unavailable (no matching calibration history; no fabricated estimate).")
    else:
        print(f"Estimated runtime: {estimate:.2f}s from {len(matching)} matching prior run(s); confidence={confidence}.")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    for test in skipped:
        append_jsonl(skip_log, {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "run_id": run_id,
            "test_id": test.id(), "reason": "quick mode excluded test" if test in skipped_by_mode else "explicit --skip substring",
            "quick_mode": args.quick, "selection_signature": selection_signature, "environment_fingerprint": profile["fingerprint"]})
    start = time.perf_counter()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(selected))
    elapsed = time.perf_counter() - start
    record = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "run_id": run_id, "tool": "agentkit_testfast",
        "root": str(root), "environment": profile, "environment_fingerprint": profile["fingerprint"],
        "selection_signature": selection_signature, "quick_mode": args.quick, "discovered_count": len(tests),
        "selected_count": len(selected), "skipped_count": len(skipped), "elapsed_seconds": round(elapsed, 6),
        "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
        "estimate_before_run_seconds": estimate, "estimate_confidence": confidence,
        "warning": "Quick/skip runs are partial verification; run the full suite before release or merge."}
    append_jsonl(runtime_log, record)
    print(f"Measured runtime: {elapsed:.3f}s. Runtime log: {runtime_log}")
    print(f"Skipped-test log: {skip_log}")
    if args.quick or args.skip:
        print("WARNING: partial test selection used. Run without --quick/--skip before release or merge.")
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    raise SystemExit(main())
