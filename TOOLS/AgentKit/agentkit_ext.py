#!/usr/bin/env python3
"""Optional AgentKit tools: PATH inventory, TypeScript compilation, change provenance, and Bedrock addon audit."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

VERSION = "0.2.0"
SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__", "target", "dist", "build", ".next", ".cache"}


def now_local() -> dt.datetime:
    return dt.datetime.now().astimezone()


def executable_inventory(path_value: str | None = None, all_path_entries: bool = False, query: str = "") -> dict[str, Any]:
    """List executable files in PATH without executing discovered commands."""
    path_value = os.environ.get("PATH", "") if path_value is None else path_value
    found: list[dict[str, str]] = []
    seen: set[str] = set()
    directories = [Path(p or ".").expanduser() for p in path_value.split(os.pathsep)]
    for order, directory in enumerate(directories):
        try:
            with os.scandir(directory) as entries:
                names = sorted(entries, key=lambda entry: entry.name.casefold())
                for entry in names:
                    name = entry.name
                    if not name or name.startswith("."):
                        continue
                    if query and query.casefold() not in name.casefold():
                        continue
                    try:
                        if not entry.is_file(follow_symlinks=True) or not os.access(entry.path, os.X_OK):
                            continue
                    except OSError:
                        continue
                    if not all_path_entries and name in seen:
                        continue
                    seen.add(name)
                    try:
                        resolved = str(Path(entry.path).resolve())
                    except OSError:
                        resolved = entry.path
                    found.append({"command": name, "path": resolved, "path_index": str(order)})
        except (FileNotFoundError, NotADirectoryError, PermissionError, OSError):
            continue
    return {
        "generated_local": now_local().isoformat(timespec="seconds"),
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "path_entries_scanned": len(directories),
        "all_path_entries": all_path_entries,
        "filter": query,
        "count": len(found),
        "commands": found,
        "limitations": ["Lists external executable files in PATH only.", "Shell built-ins, aliases, functions, and commands not on PATH are not included.", "Discovered executables are never run by this command."],
    }


def format_inventory(report: dict[str, Any], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if output_format == "tsv":
        lines = ["command\tpath\tpath_index"]
        lines.extend(f"{item['command']}\t{item['path']}\t{item['path_index']}" for item in report["commands"])
        return "\n".join(lines) + "\n"
    lines = [
        "# PATH command inventory", "",
        f"Generated (local): {report['generated_local']}",
        f"Generated (UTC): {report['generated_utc']}",
        f"PATH entries scanned: {report['path_entries_scanned']}",
        f"Commands listed: {report['count']}",
        f"All duplicate PATH entries: {report['all_path_entries']}", "",
        "| Command | Resolved path | PATH order |", "|---|---|---:|",
    ]
    for item in report["commands"]:
        name = item["command"].replace("|", "\\|").replace("\n", " ")
        path = item["path"].replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {name} | {path} | {item['path_index']} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    return "\n".join(lines) + "\n"


def command_inventory(args: argparse.Namespace) -> int:
    report = executable_inventory(all_path_entries=args.all_path_entries, query=args.filter)
    content = format_inventory(report, args.format)
    if args.output:
        target = Path(args.output).expanduser()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"Saved {report['count']} commands to: {target.resolve()}")
    else:
        print(content, end="")
    if report["count"] == 0:
        print("WARNING: no PATH executables matched the selection.", file=sys.stderr)
    return 0


def discover_ts_files(root: Path, explicit: list[str]) -> list[Path]:
    if explicit:
        candidates = [(root / item).resolve() if not Path(item).is_absolute() else Path(item).resolve() for item in explicit]
    else:
        candidates = []
        for directory, dirs, names in os.walk(root):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith("."))
            for name in sorted(names):
                source = Path(directory) / name
                if source.suffix.lower() == ".ts" and not name.endswith(".d.ts"):
                    candidates.append(source.resolve())
                elif source.suffix.lower() == ".tsx":
                    raise ValueError(f"Found TSX without tsconfig.json: {source}; add a tsconfig.json instead of guessing JSX mode.")
                if len(candidates) > 10000:
                    raise ValueError("More than 10,000 TypeScript files; use tsconfig.json or specify --file.")
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in candidates:
        if path in seen:
            continue
        seen.add(path)
        if not path.is_file():
            raise FileNotFoundError(f"TypeScript input not found: {path}")
        if path.suffix.lower() not in {".ts", ".tsx"}:
            raise ValueError(f"Not a .ts/.tsx input: {path}")
        if not path.is_relative_to(root):
            raise ValueError(f"Input is outside the selected root: {path}")
        unique.append(path)
    return unique


def compile_typescript(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: project root is not a directory: {root}", file=sys.stderr)
        return 2
    compiler = shutil.which(args.compiler)
    if not compiler:
        print(f"ERROR: TypeScript compiler not found on PATH: {args.compiler}", file=sys.stderr)
        print("Install it in the project with: npm install --save-dev typescript", file=sys.stderr)
        return 127
    config = root / "tsconfig.json"
    try:
        if config.exists():
            if args.file:
                raise ValueError("--file cannot be combined with tsconfig.json mode; run the project configuration as a whole.")
            command = [compiler, "--project", str(config), "--pretty", "false"]
        else:
            files = discover_ts_files(root, args.file)
            if not files:
                print("ERROR: no .ts source files found and tsconfig.json is absent.", file=sys.stderr)
                return 2
            if any(p.suffix.lower() == ".tsx" for p in files):
                raise ValueError("TSX input requires a project tsconfig.json so JSX output can be configured safely.")
            command = [compiler, "--pretty", "false", "--target", args.target, "--module", args.module, "--moduleResolution", "node", "--skipLibCheck", *map(str, files)]
        if args.check:
            command.extend(["--noEmit", "true"])
            print(f"Type-check only; no JavaScript will be written. root={root}")
        else:
            out_dir = (root / args.out_dir).resolve() if not Path(args.out_dir).is_absolute() else Path(args.out_dir).resolve()
            command.extend(["--noEmit", "false", "--outDir", str(out_dir)])
            print(f"Compile TypeScript to JavaScript. root={root}; outDir={out_dir}")
    except (ValueError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print("Compiler:", compiler)
    try:
        result = subprocess.run(command, cwd=root, check=False, timeout=args.timeout)
    except subprocess.TimeoutExpired:
        print(f"ERROR: compiler timed out after {args.timeout}s; no automatic retry.", file=sys.stderr)
        return 124
    except OSError as exc:
        print(f"ERROR: could not start compiler: {exc}", file=sys.stderr)
        return 126
    if result.returncode == 0:
        print("TypeScript compiler exited successfully.")
    else:
        print(f"TypeScript compiler exited with status {result.returncode}.", file=sys.stderr)
    return result.returncode


def git_value(root: Path, *arguments: str) -> str | None:
    try:
        result = subprocess.run(["git", *arguments], cwd=root, capture_output=True, text=True, timeout=2, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else None


def record_change(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: root is not a directory: {root}", file=sys.stderr)
        return 2
    summary = " ".join(args.summary.split())
    if not summary:
        print("ERROR: --summary must not be empty.", file=sys.stderr)
        return 2
    output = Path(args.output).expanduser()
    target = (root / output).resolve() if not output.is_absolute() else output.resolve()
    if not output.is_absolute() and not target.is_relative_to(root):
        print("ERROR: relative ledger path escapes the selected root.", file=sys.stderr)
        return 2
    local = now_local()
    record = {
        "schema_version": 1,
        "timestamp_local": local.isoformat(timespec="seconds"),
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "actor_type": args.actor,
        "work_mode": args.mode,
        "summary": summary,
        "paths": sorted(set(args.path)),
        "git_branch": git_value(root, "branch", "--show-current"),
        "git_head": git_value(root, "rev-parse", "--short", "HEAD"),
    }
    # Do not include raw prompts, conversation logs, credentials, or personal data in this public ledger.
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
    with target.open("a", encoding="utf-8") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    print(f"Recorded {record['actor_type']} / {record['work_mode']} change: {target}")
    print("Review the record before committing it to a public repository.")
    return 0


def validate_addon(args: argparse.Namespace) -> int:
    source = Path(args.archive).expanduser().resolve()
    report: dict[str, Any] = {"archive": str(source), "checks": [], "errors": [], "warnings": [], "file_count": 0, "json_count": 0, "js_count": 0, "versions": {}}
    def passed(label: str, detail: str) -> None:
        report["checks"].append({"check": label, "status": "PASS", "detail": detail})
    def failed(label: str, detail: str) -> None:
        report["errors"].append({"check": label, "detail": detail})
    if not source.is_file() or not zipfile.is_zipfile(source):
        failed("archive", "Input does not exist or is not a ZIP-compatible mcaddon/mcpack archive.")
        return finish_audit(report, args.json)
    try:
        with zipfile.ZipFile(source) as archive:
            bad_member = archive.testzip()
            if bad_member:
                failed("zip_integrity", f"CRC failure in archive member: {bad_member}")
            else:
                passed("zip_integrity", "ZIP CRC test completed with no corrupt member.")
            infos = [info for info in archive.infolist() if not info.is_dir()]
            report["file_count"] = len(infos)
            unsafe = [info.filename for info in infos if PurePosixPath(info.filename).is_absolute() or ".." in PurePosixPath(info.filename).parts or "\\" in info.filename]
            if unsafe:
                failed("archive_paths", f"Unsafe member paths: {unsafe[:10]}")
            else:
                passed("archive_paths", f"No absolute/path-traversal members among {len(infos)} files.")
            names = {info.filename for info in infos}
            manifests: dict[str, dict[str, Any]] = {}
            for key in ("BP/manifest.json", "RP/manifest.json"):
                if key in names:
                    try:
                        manifests[key] = json.loads(archive.read(key).decode("utf-8-sig"))
                    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                        failed("manifest_json", f"{key}: {exc}")
            if not manifests:
                failed("manifest_presence", "No BP/manifest.json or RP/manifest.json at expected pack paths.")
            else:
                for key, manifest in manifests.items():
                    header = manifest.get("header", {})
                    version = header.get("version")
                    report["versions"][key] = version
                    if not isinstance(version, (str, list)) or not version:
                        failed("manifest_version", f"{key} has a missing or invalid header.version.")
                    if not header.get("uuid"):
                        failed("manifest_uuid", f"{key} has no header.uuid.")
                    for index, module in enumerate(manifest.get("modules", [])):
                        if not module.get("uuid") or not module.get("version"):
                            failed("module_metadata", f"{key} module {index} is missing uuid/version.")
                    passed("manifest_parse", f"Parsed {key}; version={version}.")
                bp = manifests.get("BP/manifest.json")
                rp = manifests.get("RP/manifest.json")
                if bp and rp:
                    bv = bp.get("header", {}).get("version")
                    rv = rp.get("header", {}).get("version")
                    if bv != rv:
                        failed("pack_version_match", f"BP version {bv!r} differs from RP version {rv!r}.")
                    else:
                        passed("pack_version_match", f"BP and RP versions both equal {bv!r}.")
                    rp_uuid = rp.get("header", {}).get("uuid")
                    dependencies = bp.get("dependencies", [])
                    matches = [dep for dep in dependencies if dep.get("uuid") == rp_uuid]
                    if not matches:
                        failed("pack_dependency", "BP manifest has no dependency on RP header UUID.")
                    elif not any(dep.get("version") == rv for dep in matches):
                        failed("pack_dependency_version", f"BP RP dependency does not match RP version {rv!r}.")
                    else:
                        passed("pack_dependency", "BP dependency UUID/version matches the RP pack.")
            json_errors: list[str] = []
            for info in infos:
                if not info.filename.lower().endswith(".json"):
                    continue
                try:
                    json.loads(archive.read(info).decode("utf-8-sig"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    json_errors.append(f"{info.filename}: {exc}")
            report["json_count"] = sum(info.filename.lower().endswith(".json") for info in infos)
            if json_errors:
                failed("json_files", f"{len(json_errors)} invalid JSON file(s); first examples: {json_errors[:10]}")
            else:
                passed("json_files", f"All {report['json_count']} JSON files parse successfully.")
            js_files = [info for info in infos if info.filename.lower().endswith(".js")]
            report["js_count"] = len(js_files)
            node = None if args.no_js_check else shutil.which(args.node)
            if args.no_js_check:
                report["warnings"].append({"check": "js_syntax", "detail": "Skipped by --no-js-check."})
            elif not node:
                report["warnings"].append({"check": "js_syntax", "detail": f"Node runtime not found ({args.node}); JavaScript syntax not checked."})
            else:
                js_errors = []
                with tempfile.TemporaryDirectory(prefix="agentkit-addon-") as temp_dir:
                    for index, info in enumerate(js_files):
                        temp_file = Path(temp_dir) / f"script_{index}.mjs"
                        temp_file.write_bytes(archive.read(info))
                        try:
                            check = subprocess.run([node, "--check", str(temp_file)], capture_output=True, text=True, timeout=args.js_timeout, check=False)
                        except subprocess.TimeoutExpired:
                            js_errors.append(f"{info.filename}: node --check timed out")
                            continue
                        if check.returncode:
                            js_errors.append(f"{info.filename}: {(check.stderr or check.stdout).strip()[:300]}")
                if js_errors:
                    failed("js_syntax", f"{len(js_errors)} JavaScript file(s) failed syntax check; examples: {js_errors[:10]}")
                else:
                    passed("js_syntax", f"Node syntax check passed for all {len(js_files)} JavaScript files.")
            if not report["errors"]:
                passed("static_archive_audit", "No error-level static issues found. This does not prove Minecraft runtime behavior.")
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        failed("archive_read", f"Could not read archive: {type(exc).__name__}: {exc}")
    return finish_audit(report, args.json)


def finish_audit(report: dict[str, Any], json_path: str | None) -> int:
    content = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if json_path:
        target = Path(json_path).expanduser()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print("JSON report:", target.resolve())
    print(f"Archive: {report['archive']}")
    print(f"Files: {report['file_count']} | JSON: {report['json_count']} | JavaScript: {report['js_count']}")
    for check in report["checks"]:
        print(f"PASS {check['check']}: {check['detail']}")
    for warning in report["warnings"]:
        print(f"WARN {warning['check']}: {warning['detail']}")
    for error in report["errors"]:
        print(f"FAIL {error['check']}: {error['detail']}", file=sys.stderr)
    print("Static checks do not replace a Minecraft world/Content Log smoke test.")
    return 1 if report["errors"] else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agentkit-ext", description="AgentKit extensions for environment inventory, TypeScript, provenance, and addon audits.")
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="command", required=True)

    item = sub.add_parser("commands", help="List executable commands found in PATH without running them.")
    item.add_argument("--filter", default="", help="Only include command names containing this substring.")
    item.add_argument("--all-path-entries", action="store_true", help="Show shadowed duplicate command names from later PATH entries too.")
    item.add_argument("--format", choices=("markdown", "json", "tsv"), default="markdown")
    item.add_argument("--output", help="Write the table/report to a file instead of stdout.")
    item.set_defaults(handler=command_inventory)

    item = sub.add_parser("compile-ts", help="Compile TypeScript to JavaScript or run a no-emit type check using tsc.")
    item.add_argument("--root", default=".", help="Explicit project root.")
    item.add_argument("--file", action="append", default=[], help="TypeScript input relative to root; may be repeated.")
    item.add_argument("--out-dir", default="dist", help="Output directory for build mode (default: dist).")
    item.add_argument("--check", action="store_true", help="Type-check only; do not emit JavaScript.")
    item.add_argument("--compiler", default="tsc", help="Compiler executable name (default: tsc).")
    item.add_argument("--target", default="ES2022", help="Target used when tsconfig.json is absent.")
    item.add_argument("--module", default="ESNext", help="Module format used when tsconfig.json is absent.")
    item.add_argument("--timeout", type=int, default=120, choices=range(1, 601), help="Compiler timeout in seconds (1..600).")
    item.set_defaults(handler=compile_typescript)

    item = sub.add_parser("record-change", help="Append actor/mode provenance to a JSONL ledger.")
    item.add_argument("--root", default=".")
    item.add_argument("--actor", choices=("ai", "human"), required=True)
    item.add_argument("--mode", choices=("online", "offline", "mixed"), required=True)
    item.add_argument("--summary", required=True)
    item.add_argument("--path", action="append", default=[], help="Changed path; may be repeated.")
    item.add_argument("--output", default="LOGS/change-ledger.jsonl")
    item.set_defaults(handler=record_change)

    item = sub.add_parser("audit-addon", help="Statically inspect a mcaddon/mcpack ZIP without extracting it.")
    item.add_argument("archive")
    item.add_argument("--json", help="Optional JSON report path.")
    item.add_argument("--node", default="node", help="Node.js executable for optional syntax validation.")
    item.add_argument("--js-timeout", type=int, default=10, choices=range(1, 121))
    item.add_argument("--no-js-check", action="store_true", help="Skip Node.js syntax checks explicitly.")
    item.set_defaults(handler=validate_addon)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except KeyboardInterrupt:
        print("Interrupted; no automatic retry.", file=sys.stderr)
        return 130
    except (OSError, ValueError) as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
