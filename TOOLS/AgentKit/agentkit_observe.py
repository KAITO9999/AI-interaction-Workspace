#!/usr/bin/env python3
"""Run a child task with bounded, best-effort observation and explicit fallbacks.

AgentKit is designed to combine tools already present in a restricted agent
runtime so useful checks can still run when a preferred tool is missing. It
does not bypass OS/agent policy, escalate privileges, or claim syscall tracing
when only process/output telemetry was available.

This practical runner is intentionally separate from agentkit_env.py, which
only diagnoses the environment. The runner performs one initial log-file write
as its write-permission test. If denied, it reports the failure to stderr and
stops without repeatedly probing other paths. If allowed, it records timestamped
events and periodic metadata for the child process it starts.
"""
from __future__ import annotations

import argparse
import json
import os
import queue
import shutil
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "0.1.0"
MAX_DURATION = 3600.0
MAX_INTERVAL = 60.0


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def emit_stderr_record(event: str, **fields: Any) -> None:
    print(json.dumps({"time": now(), "event": event, **fields}, ensure_ascii=False), file=sys.stderr, flush=True)


def initial_log_file(log_dir: Path) -> tuple[Path | None, str | None]:
    """Make exactly one file-creation attempt; never probe alternate locations."""
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "events.txt"
        with log_path.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps({
                "time": now(),
                "event": "write_probe_succeeded",
                "log_path": str(log_path.resolve()),
                "note": "This file creation was the single initial write-permission probe.",
            }, ensure_ascii=False) + "\n")
            stream.flush()
        return log_path, None
    except OSError as exc:
        return None, f"{type(exc).__name__}: {exc}"


class EventLogger:
    """Append until a write fails; after that, never attempt filesystem writes again."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.enabled = True

    def event(self, event: str, **fields: Any) -> bool:
        record = {"time": now(), "event": event, **fields}
        if not self.enabled:
            emit_stderr_record(event, **fields, persistence_disabled=True)
            return False
        try:
            with self.path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
                stream.flush()
            return True
        except OSError as exc:
            self.enabled = False
            emit_stderr_record(
                "log_write_failed",
                path=str(self.path),
                error_type=type(exc).__name__,
                error=str(exc),
                fallback="all further events go to stderr; no alternate path or filesystem retry",
            )
            return False


def proc_snapshot(pid: int) -> dict[str, Any]:
    """Read metadata for the process started by this tool; never attach to other PIDs."""
    result: dict[str, Any] = {"pid": pid, "observed_at": now()}
    proc = Path("/proc") / str(pid)
    try:
        result["cmdline"] = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode(
            "utf-8", errors="replace"
        ).strip()[:2000]
    except OSError as exc:
        result["cmdline_error"] = f"{type(exc).__name__}: {exc}"
    try:
        status: dict[str, str] = {}
        for line in (proc / "status").read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith(("Name:", "State:", "PPid:", "Threads:", "VmRSS:", "Uid:")):
                key, _, value = line.partition(":")
                status[key] = value.strip()
        result["status"] = status
    except OSError as exc:
        result["status_error"] = f"{type(exc).__name__}: {exc}"
    try:
        raw_stat = (proc / "stat").read_text(encoding="utf-8")
        _, separator, remainder = raw_stat.partition(") ")
        fields = remainder.split() if separator else []
        if len(fields) > 19:
            result["stat"] = {
                "state": fields[0],
                "parent_pid": fields[1],
                "user_ticks": fields[11],
                "system_ticks": fields[12],
                "start_ticks": fields[19],
            }
    except (OSError, IndexError, ValueError) as exc:
        result["stat_error"] = f"{type(exc).__name__}: {exc}"
    try:
        io_fields: dict[str, str] = {}
        for line in (proc / "io").read_text(encoding="utf-8").splitlines():
            key, _, value = line.partition(":")
            io_fields[key] = value.strip()
        result["io"] = io_fields
    except OSError as exc:
        result["io_error"] = f"{type(exc).__name__}: {exc}"
    result["proc_metadata_available"] = proc.exists()
    return result


def _reader(stream: Any, messages: queue.Queue[tuple[str, str | None]]) -> None:
    try:
        for line in iter(stream.readline, ""):
            messages.put(("output", line.rstrip("\n")))
    except (OSError, ValueError) as exc:
        messages.put(("reader_error", f"{type(exc).__name__}: {exc}"))
    finally:
        messages.put(("eof", None))


def run_observed(command: list[str], log_dir: Path, interval: float, duration: float,
                 trace: str = "auto") -> int:
    log_path, write_error = initial_log_file(log_dir)
    if log_path is None:
        emit_stderr_record(
            "write_probe_denied",
            requested_log_dir=str(log_dir),
            error=write_error,
            action="stopped after one write attempt; no alternate path or retry was attempted",
        )
        return 2

    strace = shutil.which("strace")
    trace_prefix: list[str] = []
    trace_log = log_dir / "syscalls.txt"
    trace_mode = "not_requested"
    if trace == "off":
        trace_mode = "disabled_by_user"
    elif strace:
        trace_prefix = [strace, "-f", "-tt", "-T", "-s", "256", "-o", str(trace_log), "--"]
        trace_mode = "strace_attempted"
    else:
        trace_mode = "fallback_process_and_output_telemetry"
    logger = EventLogger(log_path)
    logger.event(
        "session_start", version=VERSION, cwd=os.getcwd(),
        log_dir=str(log_dir.resolve()), command=command, trace_mode=trace_mode,
        syscall_log=str(trace_log) if trace_prefix else None,
        fallback_note=(
            "No strace found: process metadata and captured output are observational fallbacks, "
            "not system-call tracing."
            if not strace and trace != "off" else None
        ),
        duration_limit_seconds=duration, sample_interval_seconds=interval,
    )

    argv = trace_prefix + command
    try:
        process = subprocess.Popen(
            argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
            bufsize=1, close_fds=True, start_new_session=(os.name == "posix"),
        )
    except OSError as exc:
        logger.event("process_start_failed", argv=argv,
                     error_type=type(exc).__name__, error=str(exc))
        emit_stderr_record("process_start_failed", argv=argv, error=str(exc), log_path=str(log_path))
        return 127

    logger.event("process_started", pid=process.pid, argv=argv)
    messages: queue.Queue[tuple[str, str | None]] = queue.Queue()
    assert process.stdout is not None
    reader = threading.Thread(target=_reader, args=(process.stdout, messages), daemon=True)
    reader.start()
    start = time.monotonic()
    next_sample = start
    sample_number = 0
    reader_eof = False
    timed_out = False
    logging_available = True

    try:
        while True:
            current = time.monotonic()
            if current >= next_sample and process.poll() is None:
                sample_number += 1
                snapshot = proc_snapshot(process.pid)
                if logging_available:
                    logging_available = logger.event("process_sample",
                                                       sample_number=sample_number, **snapshot)
                next_sample = current + interval

            try:
                kind, value = messages.get(timeout=min(0.1, interval))
                if kind == "output" and value is not None:
                    if logging_available:
                        logging_available = logger.event("child_output", line=value)
                    print(value, flush=True)
                elif kind == "reader_error":
                    if logging_available:
                        logging_available = logger.event("output_reader_error", detail=value)
                elif kind == "eof":
                    reader_eof = True
            except queue.Empty:
                pass

            if process.poll() is not None and reader_eof:
                break
            if time.monotonic() - start >= duration and process.poll() is None:
                timed_out = True
                logger.event("duration_limit_reached", seconds=duration)
                try:
                    if os.name == "posix":
                        os.killpg(process.pid, signal.SIGTERM)
                    else:
                        process.terminate()
                except OSError as exc:
                    logger.event("terminate_failed", error=str(exc))
                try:
                    process.wait(timeout=2.0)
                except subprocess.TimeoutExpired:
                    try:
                        if os.name == "posix":
                            os.killpg(process.pid, signal.SIGKILL)
                        else:
                            process.kill()
                    except OSError as exc:
                        logger.event("kill_failed", error=str(exc))
                break
    except KeyboardInterrupt:
        logger.event("interrupted_by_user")
        try:
            if os.name == "posix":
                os.killpg(process.pid, signal.SIGTERM)
            else:
                process.terminate()
        except OSError:
            pass
        try:
            process.wait(timeout=2.0)
        except subprocess.TimeoutExpired:
            process.kill()
    finally:
        try:
            return_code = process.wait(timeout=2.0)
        except subprocess.TimeoutExpired:
            process.kill()
            return_code = process.wait()
        try:
            process.stdout.close()
        except OSError:
            pass

    logger.event("session_end", pid=process.pid, returncode=return_code,
                 timed_out=timed_out, elapsed_seconds=round(time.monotonic() - start, 3),
                 sample_count=sample_number, syscall_log=str(trace_log) if trace_prefix else None,
                 syscall_trace_claimed=bool(trace_prefix and trace_log.exists() and trace_log.stat().st_size > 0))
    print(f"AgentKit observation log: {log_path}", file=sys.stderr)
    if trace_prefix:
        print(f"Syscall trace (if permitted): {trace_log}", file=sys.stderr)
    if timed_out:
        return 124
    return return_code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a child command with bounded process/output observation and safe fallbacks."
    )
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument("--log-dir", required=True, help="explicit directory for logs; no alternate path is probed")
    parser.add_argument("--interval", type=float, default=1.0, help="process sample interval in seconds (0.2–60)")
    parser.add_argument("--duration", type=float, default=60.0, help="maximum runtime in seconds (0.1–3600)")
    parser.add_argument("--trace", choices=("auto", "off"), default="auto",
                        help="auto uses strace when present; otherwise uses non-equivalent telemetry")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="child command, usually after --")
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("a child command is required after --")
    if not 0.2 <= args.interval <= MAX_INTERVAL:
        parser.error(f"--interval must be between 0.2 and {MAX_INTERVAL}")
    if not 0.1 <= args.duration <= MAX_DURATION:
        parser.error(f"--duration must be between 0.1 and {MAX_DURATION}")
    return run_observed(command, Path(args.log_dir).expanduser(), args.interval, args.duration, args.trace)


if __name__ == "__main__":
    raise SystemExit(main())
