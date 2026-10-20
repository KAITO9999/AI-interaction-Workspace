"""Static JavaScript workload review with explicit user-supplied target profiles.

This tool never probes the host. It reports workload signals and does not invent wall-clock
runtime values when execution counts or calibrated cost data are unavailable.
"""
from __future__ import annotations

import argparse
import hashlib
import math
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.1.0"
JS_EXTENSIONS = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "target", ".next", ".agentkit-logs"}
API_PATTERNS = [
    (re.compile(r"\bfetch\s*\("), "fetch", "NETWORK", "Network request", "Network duration depends on server, connection, cache, and response size."),
    (re.compile(r"\bXMLHttpRequest\b|\.send\s*\("), "xhr", "NETWORK", "XHR/send call", "Transport and event timing are runtime-dependent."),
    (re.compile(r"\b(JSON\s*\.\s*parse|JSON\s*\.\s*stringify)\s*\("), "json", "CPU_MEMORY", "JSON serialization/parsing", "Cost depends heavily on payload size and object shape."),
    (re.compile(r"\b(setInterval|setTimeout)\s*\("), "timer", "SCHEDULING", "Timer scheduling", "Timer callbacks may repeat; inspect interval, cancellation, and callback work."),
    (re.compile(r"\b(requestAnimationFrame)\s*\("), "frame", "SCHEDULING", "Per-frame callback", "Work can repeat at display-frame frequency; inspect the callback body."),
    (re.compile(r"\.(map|filter|reduce|sort|flatMap)\s*\("), "collection", "CPU", "Collection operation", "Work generally scales with collection size; sort is commonly O(n log n)."),
    (re.compile(r"\b(new\s+(Array|Map|Set|Object|Uint8Array|Float32Array|ArrayBuffer))\b"), "allocation", "MEMORY", "Allocation candidate", "Memory and garbage-collection costs depend on allocation size and lifetime."),
]
LOOP_RE = re.compile(r"\b(for|while|do)\b")
FUNCTION_RE = re.compile(r"\bfunction\s*([A-Za-z_$][\w$]*)?\s*\(|\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:function\b|\([^)]*\)\s*=>|[A-Za-z_$][\w$]*\s*=>)")

def mask_js(source: str) -> str:
    """Mask JS/TS comments and string/template literals while retaining offsets/newlines."""
    chars = list(source)
    i = 0
    quote = None
    escaped = False
    block = False
    line_comment = False
    while i < len(chars):
        ch = source[i]
        nxt = source[i:i + 2]
        if line_comment:
            if ch == "\n":
                line_comment = False
            else:
                chars[i] = " "
            i += 1
            continue
        if block:
            if nxt == "*/":
                chars[i] = chars[i + 1] = " "
                block = False
                i += 2
            else:
                if ch != "\n":
                    chars[i] = " "
                i += 1
            continue
        if quote:
            if ch != "\n":
                chars[i] = " "
            if escaped:
                escaped = False
            elif ch == "\\\\":
                escaped = True
            elif ch == quote:
                quote = None
            i += 1
            continue
        if nxt == "//":
            chars[i] = chars[i + 1] = " "
            line_comment = True
            i += 2
        elif nxt == "/*":
            chars[i] = chars[i + 1] = " "
            block = True
            i += 2
        elif ch in {"'", '"', "`"}:
            chars[i] = " "
            quote = ch
            i += 1
        else:
            i += 1
    return "".join(chars)

def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")

def input_file_info(path: Path | None) -> dict | None:
    if path is None:
        return None
    try:
        return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    except OSError as exc:
        return {"path": str(path), "sha256": None, "read_error": f"{type(exc).__name__}: {exc}"}

def find_js_files(root: Path, explicit: list[str]) -> list[Path]:
    if explicit:
        found = []
        for item in explicit:
            path = (root / item).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                raise ValueError(f"--file must name an existing file under root: {item}")
            if path.suffix.lower() not in JS_EXTENSIONS:
                raise ValueError(f"unsupported JavaScript/TypeScript extension: {item}")
            found.append(path)
        return sorted(set(found))
    return sorted(path for path in root.rglob("*")
                  if path.is_file() and path.suffix.lower() in JS_EXTENSIONS
                  and not any(part in SKIP_DIRS for part in path.relative_to(root).parts))

def analyze_file(path: Path, root: Path) -> tuple[list[dict], dict]:
    source = path.read_text(encoding="utf-8", errors="replace")
    code = mask_js(source)
    lines = code.splitlines()
    findings = []
    rel = str(path.relative_to(root))
    loop_lines = [i for i, line in enumerate(lines, 1) if LOOP_RE.search(line)]
    api_call_sites = []
    for number, line in enumerate(lines, 1):
        for pattern, api_name, category, title, detail in API_PATTERNS:
            for match in pattern.finditer(line):
                awaited = bool(re.search(r"\bawait\s+$", line[:match.start()]))
                api_call_sites.append({"line": number, "api": api_name, "category": category, "awaited": awaited})
                findings.append({
                    "path": rel, "line": number, "category": "API_LOAD" if category in {"NETWORK", "SCHEDULING"} else "WORKLOAD",
                    "priority": "MEDIUM",
                    "title": title, "detail": detail, "detection_confidence": "MEDIUM",
                    "review_recommended": True,
                    "evidence": "Call-site pattern only; runtime behavior and invocation frequency are not proven."
                })
                if api_name == "timer":
                    delay = re.search(r"\bsetInterval\s*\([^,]+,\s*(\d+(?:\.\d+)?)", line)
                    if delay and float(delay.group(1)) < 100:
                        findings.append({
                            "path": rel, "line": number, "category": "PERFORMANCE", "priority": "MEDIUM",
                            "title": "Potential high-frequency interval",
                            "detail": f"setInterval delay is {delay.group(1)} ms; callbacks may run at 10 Hz or faster. Confirm that this cadence is needed and that work is bounded.",
                            "detection_confidence": "MEDIUM", "review_recommended": True,
                            "evidence": "Literal delay only; browser throttling and callback execution affect actual frequency."
                        })
    for line_no in loop_lines:
        end_line = line_no
        depth = 0
        started = False
        for idx in range(line_no - 1, len(lines)):
            depth += lines[idx].count("{") - lines[idx].count("}")
            if "{" in lines[idx]:
                started = True
            if started and depth <= 0 and idx >= line_no - 1:
                end_line = idx + 1
                break
            if not started and idx > line_no:
                end_line = idx + 1
                break
        contained = [api for api in api_call_sites if line_no <= api["line"] <= end_line]
        nested = sum(1 for other in loop_lines if line_no < other <= end_line)
        if contained:
            findings.append({
                "path": rel, "line": line_no, "category": "PERFORMANCE", "priority": "HIGH" if any(x["api"] in {"fetch", "xhr", "frame", "timer"} for x in contained) else "MEDIUM",
                "title": "Call site inside loop",
                "detail": f"Found {len(contained)} API/workload call site(s) in the loop body; iteration count is unknown."
                         + (" Nested loop syntax is also present, so multiplicative work is possible." if nested else ""),
                "detection_confidence": "MEDIUM", "review_recommended": True,
                "evidence": "Static loop-body approximation; braces, callbacks, and control flow can affect the region."
            })
            awaited_network = [item for item in contained if item.get("awaited") and item["api"] in {"fetch", "xhr"}]
            if awaited_network:
                findings.append({
                    "path": rel, "line": line_no, "category": "API_LOAD", "priority": "HIGH",
                    "title": "Sequential awaited network call in loop",
                    "detail": "A network-related call appears to be awaited inside a loop. If each iteration depends on the previous response, round-trip latency can accumulate; consider batching or bounded concurrency only if semantics allow.",
                    "detection_confidence": "MEDIUM", "review_recommended": True,
                    "evidence": "Approximate loop region and await syntax; runtime call path and data dependencies are not proven."
                })
        if nested:
            findings.append({
                "path": rel, "line": line_no, "category": "PERFORMANCE", "priority": "MEDIUM",
                "title": "Potential nested-loop cost",
                "detail": "Another loop appears inside this loop's approximate body. Check whether the algorithm is O(n²) or has a smaller bounded inner range.",
                "detection_confidence": "LOW", "review_recommended": True,
                "evidence": "Heuristic nesting, not a parsed control-flow graph."
            })
    declared = []
    for match in FUNCTION_RE.finditer(code):
        name = match.group(1) or match.group(2)
        if name:
            declared.append(name)
    for name in sorted(set(declared)):
        exported = (re.search(r"\bexport\s+(?:default\s+)?(?:async\s+)?function\s+" + re.escape(name) + r"\b", code)
                    or re.search(r"\bexport\s+(?:const|let|var)\s+" + re.escape(name) + r"\b", code))
        if exported:
            continue
        uses = list(re.finditer(r"\b" + re.escape(name) + r"\b", code))
        if len(uses) == 1:
            line = code.count("\n", 0, uses[0].start()) + 1
            findings.append({
                "path": rel, "line": line, "category": "REACHABILITY", "priority": "LOW",
                "title": "Function may have no direct references",
                "detail": f"{name} has no other textual reference in this file. It may still be exported, registered indirectly, called by a framework, or invoked dynamically; confirm intended use before removal.",
                "detection_confidence": "LOW", "review_recommended": True,
                "evidence": "Textual reference check only; imports, exports, reflection, event registration, and cross-file callers are not resolved."
            })
    metric = {
        "path": rel, "language": path.suffix.lower().lstrip("."), "bytes": path.stat().st_size,
        "lines": len(source.splitlines()), "executable_lines_proxy": sum(1 for line in lines if line.strip()),
        "loop_sites": loop_lines, "api_call_sites": api_call_sites,
        "sha256": hashlib.sha256(source.encode()).hexdigest()
    }
    return findings, metric

def load_calibration(path: Path | None) -> dict | None:
    if path is None:
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not read calibration JSON: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("calibration JSON must be an object with schema_version=1")
    return data

def load_workload(path: Path | None) -> dict | None:
    if path is None:
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not read workload JSON: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1 or not isinstance(data.get("operations"), list) or not data["operations"]:
        raise ValueError("workload JSON must be an object with schema_version=1 and a non-empty operations array")
    for index, operation in enumerate(data["operations"]):
        if not isinstance(operation, dict) or operation.get("kind") not in {"cpu_ops", "memory_bytes", "working_set_bytes", "api"}:
            raise ValueError(f"workload operation {index} must have kind cpu_ops, memory_bytes, working_set_bytes, or api")
        count = operation.get("count")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError(f"workload operation {index} count must be a non-negative integer")
        if operation["kind"] == "api":
            if not isinstance(operation.get("name"), str) or not operation["name"]:
                raise ValueError(f"workload API operation {index} requires a non-empty name")
            concurrency = operation.get("concurrency")
            if isinstance(concurrency, bool) or not isinstance(concurrency, int) or concurrency < 1:
                raise ValueError(f"workload API operation {index} requires positive integer concurrency")
            if count and concurrency > count:
                operation["concurrency"] = int(count)
    return data

def unavailable_estimate(reason: str, required_inputs: list[str]) -> dict:
    return {"milliseconds": None, "range_ms": None, "confidence": "INSUFFICIENT_DATA",
            "reason": reason, "required_inputs": required_inputs}

def estimate_runtime(profile_name: str, workload: dict | None, calibration: dict | None, target_specs: dict) -> dict:
    if workload is not None and not any(op["kind"] in {"cpu_ops", "memory_bytes", "api"} and op["count"] > 0 for op in workload["operations"]):
        return unavailable_estimate("The workload contains no duration-bearing operations; a working-set size alone is not an execution-time estimate.", ["at least one positive cpu_ops, memory_bytes, or api operation"])
    if workload is None or calibration is None:
        missing = []
        if workload is None:
            missing.append("workload JSON with bounded operation counts and API concurrency")
        if calibration is None:
            missing.append("measured target-runtime calibration JSON for the selected profile")
        return unavailable_estimate("No total runtime is calculated without both an explicit workload scenario and target-runtime calibration.", missing)
    profiles = calibration.get("profiles")
    if not isinstance(profiles, dict):
        return unavailable_estimate("Calibration is missing a profiles object.", ["calibration profiles object"])
    profile_data = profiles.get(profile_name)
    if not isinstance(profile_data, dict):
        return unavailable_estimate(f"Calibration has no profile named {profile_name}.", [f"profiles.{profile_name} in calibration JSON"])
    target_runtime = calibration.get("target_runtime")
    if not isinstance(target_runtime, str) or not target_runtime.strip():
        return unavailable_estimate("Calibration is missing target_runtime metadata.", ["calibration target_runtime"])
    def valid_range(value):
        return (isinstance(value, list) and len(value) == 2
                and all(not isinstance(item, bool) and isinstance(item, (int, float)) and item > 0 for item in value)
                and value[0] <= value[1])
    cpu_rate = profile_data.get("cpu_ops_per_second")
    memory_rate = profile_data.get("memory_bytes_per_second")
    scaling_adjustments = []
    target_clock = target_specs.get("clock_ghz")
    reference_clock = profile_data.get("reference_clock_ghz")
    if valid_range(cpu_rate) and isinstance(target_clock, (int, float)) and isinstance(reference_clock, (int, float)) and reference_clock > 0:
        if profile_data.get("allow_linear_clock_scaling") is True:
            factor = float(target_clock) / float(reference_clock)
            cpu_rate = [float(rate) * factor for rate in cpu_rate]
            scaling_adjustments.append(f"CPU throughput rates scaled by target/reference clock ratio {factor:.4f}; this is an explicit linear assumption, not a universal CPU law.")
        elif float(target_clock) != float(reference_clock):
            scaling_adjustments.append("Target clock differs from calibration reference, but calibration did not authorize linear scaling; CPU rates were left unchanged.")
    target_bandwidth = target_specs.get("memory_bandwidth_gbps")
    reference_bandwidth = profile_data.get("reference_memory_bandwidth_gbps")
    if valid_range(memory_rate) and isinstance(target_bandwidth, (int, float)) and isinstance(reference_bandwidth, (int, float)) and reference_bandwidth > 0:
        if profile_data.get("allow_linear_memory_bandwidth_scaling") is True:
            factor = float(target_bandwidth) / float(reference_bandwidth)
            memory_rate = [float(rate) * factor for rate in memory_rate]
            scaling_adjustments.append(f"Memory throughput rates scaled by target/reference bandwidth ratio {factor:.4f}; this assumes matching access patterns.")
        elif float(target_bandwidth) != float(reference_bandwidth):
            scaling_adjustments.append("Target memory bandwidth differs from calibration reference, but calibration did not authorize scaling; measured rates were left unchanged.")
    api_rates = profile_data.get("api_latency_ms", {})
    if not isinstance(api_rates, dict):
        api_rates = {}
    missing = []
    needs_cpu = any(op["kind"] == "cpu_ops" and op["count"] for op in workload["operations"])
    needs_memory = any(op["kind"] == "memory_bytes" and op["count"] for op in workload["operations"])
    working_sets = [op["count"] for op in workload["operations"] if op["kind"] == "working_set_bytes" and op["count"]]
    target_memory_gb = target_specs.get("memory_gb")
    if working_sets and isinstance(target_memory_gb, (int, float)) and target_memory_gb > 0:
        if max(working_sets) > float(target_memory_gb) * 1_000_000_000:
            return unavailable_estimate("A declared working set exceeds the specified total physical memory; this workload estimate is invalid until the scenario or target memory assumptions are corrected.", ["reduce working_set_bytes or specify a larger target memory capacity"])
    if needs_cpu and not valid_range(cpu_rate):
        missing.append("profiles." + profile_name + ".cpu_ops_per_second [minimum, maximum]")
    if needs_memory and not valid_range(memory_rate):
        missing.append("profiles." + profile_name + ".memory_bytes_per_second [minimum, maximum]")
    for operation in workload["operations"]:
        if operation["kind"] == "api" and operation["count"] and not valid_range(api_rates.get(operation["name"])):
            missing.append("profiles." + profile_name + ".api_latency_ms." + operation["name"] + " [minimum, maximum]")
    if missing:
        return unavailable_estimate("Calibration does not contain valid measured ranges for every workload category.", sorted(set(missing)))
    cpu_low = cpu_high = memory_low = memory_high = api_low = api_high = 0.0
    api_operation_costs = []
    for operation in workload["operations"]:
        count = float(operation["count"])
        if operation["kind"] == "cpu_ops" and count:
            cpu_low += count / float(cpu_rate[1]) * 1000
            cpu_high += count / float(cpu_rate[0]) * 1000
        elif operation["kind"] == "memory_bytes" and count:
            memory_low += count / float(memory_rate[1]) * 1000
            memory_high += count / float(memory_rate[0]) * 1000
        elif operation["kind"] == "working_set_bytes":
            continue
        elif operation["kind"] == "api" and count:
            latency_low, latency_high = api_rates[operation["name"]]
            batches = math.ceil(count / operation["concurrency"])
            op_low = batches * float(latency_low)
            op_high = batches * float(latency_high)
            api_low += op_low
            api_high += op_high
            api_operation_costs.append({"name": operation["name"], "count": int(count),
                                        "concurrency": operation["concurrency"], "serialized_batches": batches,
                                        "accumulated_wait_ms": [round(op_low, 3), round(op_high, 3)]})
    low = round(cpu_low + memory_low + api_low, 3)
    high = round(cpu_high + memory_high + api_high, 3)
    samples = profile_data.get("samples", 0)
    confidence = "HIGH" if isinstance(samples, int) and samples >= 10 else "MEDIUM" if isinstance(samples, int) and samples >= 3 else "LOW"
    return {"milliseconds": round((low + high) / 2, 3), "range_ms": [low, high], "confidence": confidence,
            "target_runtime": target_runtime, "calibration_samples": samples if isinstance(samples, int) else 0,
            "assumption": "Serial component sum; API concurrency is represented by explicit batches. CPU and memory ranges must be measured on the selected target runtime.",
            "components": {"cpu_ms": [round(cpu_low, 3), round(cpu_high, 3)],
                           "memory_transfer_ms": [round(memory_low, 3), round(memory_high, 3)],
                           "api_wait_ms": [round(api_low, 3), round(api_high, 3)], "api_operations": api_operation_costs},
            "required_inputs": [], "scaling_adjustments": scaling_adjustments}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Source root. Does not trigger host environment probing.")
    parser.add_argument("--file", action="append", default=[], help="Relative JS/TS source file; repeatable.")
    parser.add_argument("--profile", choices=["low", "mid", "mid-high", "high-end"], required=True,
                        help="User-selected target tier; no device is detected automatically.")
    parser.add_argument("--clock-ghz", type=float, help="Assumed target clock in GHz (user supplied).")
    parser.add_argument("--cores", type=int, help="Assumed target CPU core count (user supplied).")
    parser.add_argument("--memory-gb", type=float, help="Assumed target memory capacity in GB (user supplied).")
    parser.add_argument("--memory-bandwidth-gbps", type=float, help="Assumed memory bandwidth in GB/s (user supplied).")
    parser.add_argument("--workload-template", help="Write a source-linked workload template that requires manual count/concurrency assumptions.")
    parser.add_argument("--workload-json", help="Explicit scenario JSON with operation counts and API concurrency assumptions.")
    parser.add_argument("--calibration-json", help="Measured schema-v1 cost ranges for the selected target profile.")
    parser.add_argument("--json", dest="json_path", help="Write a JSON report; relative paths resolve against --root.")
    parser.add_argument("--log-dir", default=".agentkit-logs")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: root is not a directory: {root}", file=sys.stderr)
        return 2
    for option_name, value in (("--clock-ghz", args.clock_ghz), ("--cores", args.cores),
                               ("--memory-gb", args.memory_gb), ("--memory-bandwidth-gbps", args.memory_bandwidth_gbps)):
        if value is not None and value <= 0:
            print(f"ERROR: {option_name} must be greater than zero.", file=sys.stderr)
            return 2
    profile = {"tier": args.profile, "auto_detected": False, "clock_ghz": args.clock_ghz, "cores": args.cores,
               "memory_gb": args.memory_gb, "memory_bandwidth_gbps": args.memory_bandwidth_gbps,
               "note": "All target specifications are user-supplied assumptions. Tier names alone do not determine execution speed."}
    try:
        files = find_js_files(root, args.file)
        calibration_path = Path(args.calibration_json) if args.calibration_json else None
        if calibration_path and not calibration_path.is_absolute():
            calibration_path = root / calibration_path
        calibration = load_calibration(calibration_path)
        workload_path = Path(args.workload_json) if args.workload_json else None
        if workload_path and not workload_path.is_absolute():
            workload_path = root / workload_path
        workload = load_workload(workload_path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    findings, metrics = [], []
    for path in files:
        try:
            found, metric = analyze_file(path, root)
        except OSError as exc:
            print(f"ERROR: cannot read {path}: {exc}", file=sys.stderr)
            return 2
        findings.extend(found)
        metrics.append(metric)
    json_output_path = Path(args.json_path) if args.json_path else None
    if json_output_path:
        if not json_output_path.is_absolute():
            json_output_path = root / json_output_path
        json_output_path = json_output_path.resolve()
    log_dir = Path(args.log_dir)
    if not log_dir.is_absolute():
        log_dir = root / log_dir
    log_dir = log_dir.resolve()
    log = log_dir / "js-load-analysis.jsonl"
    protected_inputs = {path.resolve() for path in files}
    if workload_path:
        protected_inputs.add(workload_path.resolve())
    if calibration_path:
        protected_inputs.add(calibration_path.resolve())
    if json_output_path:
        if json_output_path in protected_inputs or json_output_path == log:
            print("ERROR: --json must not overwrite source, workload, calibration, or log files.", file=sys.stderr)
            return 2
    template_path = Path(args.workload_template) if args.workload_template else None
    if template_path:
        if not template_path.is_absolute():
            template_path = root / template_path
        template_path = template_path.resolve()
        if template_path in protected_inputs or template_path == log or template_path == json_output_path:
            print("ERROR: --workload-template must not overwrite source, workload, calibration, report, or log files.", file=sys.stderr)
            return 2
        template = {
            "schema_version": 1,
            "template_only": True,
            "target_profile": profile,
            "source_observations": [
                {"path": item["path"], "loop_sites": item["loop_sites"], "api_call_sites": item["api_call_sites"]}
                for item in metrics
            ],
            "operation_candidates": [
                {"kind": "api", "name": api_name,
                 "source_sites": [{"path": item["path"], "line": site["line"], "loop_sites_in_file": item["loop_sites"]}
                                  for item in metrics for site in item["api_call_sites"] if site["api"] == api_name],
                 "count": None, "concurrency": None}
                for api_name in sorted({site["api"] for item in metrics for site in item["api_call_sites"]})
            ],
            "required_user_inputs": [
                "Replace null API count/concurrency values with measured or explicitly assumed per-run values.",
                "Add CPU operation counts and memory traffic/working-set sizes for the same scenario when relevant.",
                "Bound loop iteration counts and function invocation counts; source syntax alone cannot determine them.",
                "Use measured calibration ranges for the selected target runtime/profile."
            ],
            "note": "This template is not valid estimator input until converted into a workload JSON with explicit operations and counts."
        }
        try:
            template_path.parent.mkdir(parents=True, exist_ok=True)
            template_path.write_text(json.dumps(template, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"ERROR: could not write workload template: {exc}", file=sys.stderr)
            return 2
    runtime_estimate = estimate_runtime(args.profile, workload, calibration, profile)
    if calibration is not None:
        runtime_estimate["calibration_loaded"] = True
    if workload is not None:
        runtime_estimate["workload_loaded"] = True
    for api_operation in runtime_estimate.get("components", {}).get("api_operations", []):
        if api_operation["count"] > api_operation["concurrency"]:
            wait_high = api_operation["accumulated_wait_ms"][1]
            findings.append({
                "path": "<workload-json>", "line": 1, "category": "API_LOAD",
                "priority": "HIGH" if wait_high >= 1000 else "MEDIUM",
                "title": "Multiple API batches in workload scenario",
                "detail": f"{api_operation['name']}: {api_operation['count']} call(s) at concurrency {api_operation['concurrency']} require {api_operation['serialized_batches']} latency batch(es); calibrated accumulated wait range is {api_operation['accumulated_wait_ms'][0]:.3f}–{wait_high:.3f} ms. Consider batching or bounded concurrency only if API semantics, rate limits, and ordering allow.",
                "detection_confidence": "MEDIUM", "review_recommended": True,
                "evidence": "Derived from explicit workload counts and target-runtime latency calibration, not inferred from source text."
            })
    cpu_component = runtime_estimate.get("components", {}).get("cpu_ms")
    if cpu_component and cpu_component[1] >= 50 and any(token in runtime_estimate.get("target_runtime", "").lower() for token in ("browser", "chrome", "firefox", "safari", "web")):
        findings.append({
            "path": "<workload-json>", "line": 1, "category": "PERFORMANCE", "priority": "HIGH",
            "title": "Estimated CPU phase may become a long task",
            "detail": f"Calibrated CPU component upper bound is {cpu_component[1]:.3f} ms. If this work executes as one browser main-thread task, it exceeds the 50 ms Long Tasks threshold and may delay input; split/yield only where semantics allow.",
            "detection_confidence": "MEDIUM", "review_recommended": True,
            "evidence": "Chrome Long Tasks threshold: https://developer.chrome.com/docs/web-platform/long-animation-frames"
        })
    report = {"tool": "agentkit_js_load", "version": VERSION, "generated_utc": datetime.now(timezone.utc).isoformat(),
              "root": str(root), "profile": profile, "files_scanned": len(metrics), "metrics": metrics,
              "inputs": {
                  "workload_json": input_file_info(workload_path),
                  "calibration_json": input_file_info(calibration_path),
              },
              "workload_scenario": workload,
              "findings": sorted(findings, key=lambda x: (x["path"], x["line"], x["title"])),
              "runtime_estimate": runtime_estimate,
              "model_policy": ["No host environment discovery or automatic target inference.",
                               "Tier names are labels, not hidden performance multipliers.",
                               "Clock and bandwidth affect rates only when the calibration explicitly authorizes a scaling model.",
                               "Core count is not multiplied into main-thread JavaScript throughput; worker/parallel execution needs a separate workload model.",
                               "Clock scaling is a linear assumption only when explicitly enabled; it may not hold across CPU architectures or JS engines.",
                               "Static call-site findings do not prove dynamic call counts or dead code.",
                               "Runtime estimate remains unavailable rather than inventing precision when workload bounds or calibrated rates are missing."]}
    try:
        for item in report["findings"]:
            append_jsonl(log, {"timestamp_utc": report["generated_utc"], "record_type": "finding",
                               "profile": profile, **item})
        append_jsonl(log, {"timestamp_utc": report["generated_utc"], "record_type": "summary",
                           "tool": "agentkit_js_load", "profile": profile, "files_scanned": len(metrics),
                           "findings_count": len(findings), "runtime_estimate": runtime_estimate,
                           "input_hashes": report["inputs"]})
    except OSError as exc:
        print(f"ERROR: could not append analysis log: {exc}", file=sys.stderr)
        return 2
    report["log"] = str(log)
    if template_path:
        report["workload_template"] = str(template_path)
    if json_output_path:
        try:
            json_output_path.parent.mkdir(parents=True, exist_ok=True)
            json_output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"ERROR: could not write JSON report: {exc}", file=sys.stderr)
            return 2
    for item in report["findings"]:
        print(f"[{item['priority']}/{item['detection_confidence']}] {item['category']} {item['path']}:{item['line']} — {item['title']}: {item['detail']}")
    print(f"Scanned {len(metrics)} JS/TS file(s); findings: {len(findings)}.")
    if runtime_estimate["milliseconds"] is None:
        print("Runtime estimate: unavailable — " + runtime_estimate["reason"])
    else:
        print(f"Estimated runtime: {runtime_estimate['range_ms'][0]:.3f}–{runtime_estimate['range_ms'][1]:.3f} ms (midpoint {runtime_estimate['milliseconds']:.3f} ms; confidence={runtime_estimate['confidence']}).")
    if template_path:
        print(f"Workload template: {template_path}")
    print(f"Analysis log: {log}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
