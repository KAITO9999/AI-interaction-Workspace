#!/usr/bin/env python3
"""Bounded subprocess supervision shared by AgentKit workflow tools.

Commands are argument vectors, never shell strings. Output is drained continuously
but only a bounded tail is retained. POSIX timeouts terminate the command's process
group to avoid leaving ordinary child processes behind.
"""
from __future__ import annotations

import math
import os
import signal
import subprocess
import sys
import threading
import time
from typing import Callable
from pathlib import Path
from typing import Sequence

DEFAULT_OUTPUT_LIMIT = 12_000
DEFAULT_TERMINATE_GRACE = 0.4


def process_status(result: dict[str, object]) -> str:
    """Map process outcomes to stable, non-overlapping report statuses."""
    if result.get("timed_out"):
        return "TIMEOUT"
    if result.get("launch_error"):
        return "UNAVAILABLE"
    if result.get("capture_error"):
        return "FAIL"
    return "PASS" if result.get("returncode") == 0 else "FAIL"


def _capture_tail(
    stream: object,
    retained: bytearray,
    state: dict[str, object],
    finished: threading.Event,
    limit: int,
    passthrough: object | None = None,
) -> None:
    last_byte = b""
    try:
        fd = stream.fileno()  # type: ignore[attr-defined]
        while True:
            chunk = os.read(fd, 4096)
            if not chunk:
                break
            state["total"] = int(state["total"]) + len(chunk)
            state["lines"] = int(state["lines"]) + chunk.count(b"\n")
            last_byte = chunk[-1:]
            retained.extend(chunk)
            if len(retained) > limit:
                del retained[:-limit]
            if passthrough is not None:
                try:
                    buffer = getattr(passthrough, "buffer", None)
                    if buffer is not None:
                        buffer.write(chunk)
                        buffer.flush()
                    else:
                        passthrough.write(chunk.decode("utf-8", errors="replace"))  # type: ignore[attr-defined]
                        passthrough.flush()  # type: ignore[attr-defined]
                except (OSError, UnicodeError, ValueError) as exc:
                    state["stream_error"] = f"{type(exc).__name__}: {exc}"
                    passthrough = None
    except OSError as exc:
        state["read_error"] = f"{type(exc).__name__}: {exc}"
    finally:
        state["lines"] = int(state["lines"]) + (1 if int(state["total"]) and last_byte != b"\n" else 0)
        finished.set()


def _signal_process_tree(process: subprocess.Popen[bytes], sig: int) -> None:
    try:
        if os.name == "posix":
            os.killpg(process.pid, sig)
        elif process.poll() is None:
            if sig == getattr(signal, "SIGKILL", signal.SIGTERM):
                process.kill()
            else:
                process.terminate()
    except (ProcessLookupError, PermissionError, OSError):
        pass


def _terminate_process_tree(
    process: subprocess.Popen[bytes], grace: float = DEFAULT_TERMINATE_GRACE
) -> None:
    """Terminate a timed-out process and, on POSIX, its inherited process group."""
    _signal_process_tree(process, signal.SIGTERM)
    try:
        process.wait(timeout=grace)
    except subprocess.TimeoutExpired:
        pass
    _signal_process_tree(process, getattr(signal, "SIGKILL", signal.SIGTERM))
    try:
        process.wait(timeout=max(grace, 0.1))
    except subprocess.TimeoutExpired:
        pass


def _join_readers(threads: list[threading.Thread], streams: tuple[object, object]) -> None:
    for thread in threads:
        thread.join(timeout=1.0)
    # Close both pipe objects even when their reader threads already exited.
    # A stuck reader is unblocked by closing its descriptor before the final join.
    for stream in streams:
        try:
            stream.close()  # type: ignore[attr-defined]
        except OSError:
            pass
    for thread in threads:
        thread.join(timeout=0.2)


def run_process(
    argv: Sequence[str],
    timeout: float = 30,
    cwd: Path | str | None = None,
    output_limit: int = DEFAULT_OUTPUT_LIMIT,
    terminate_grace: float = DEFAULT_TERMINATE_GRACE,
    stream_output: bool = False,
    on_progress: Callable[[float, float], None] | None = None,
    progress_interval: float = 1.0,
) -> dict[str, object]:
    """Run one command with a deadline, bounded output tails and explicit status.

    A timeout includes a process that exits while a descendant still holds its
    output pipes open. Output is drained concurrently, preventing pipe deadlocks.
    """
    if (
        isinstance(argv, (str, bytes))
        or not argv
        or not all(isinstance(arg, str) for arg in argv)
        or not argv[0]
    ):
        raise ValueError("argv must be a non-empty sequence of strings with a program name")
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be finite and positive")
    if output_limit < 1:
        raise ValueError("output_limit must be positive")
    if not math.isfinite(terminate_grace) or terminate_grace < 0:
        raise ValueError("terminate_grace must be finite and non-negative")
    if not math.isfinite(progress_interval) or progress_interval <= 0:
        raise ValueError("progress_interval must be finite and positive")

    command = list(argv)
    started = time.monotonic()
    try:
        process = subprocess.Popen(
            command,
            cwd=str(cwd) if cwd is not None else None,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            close_fds=True,
            start_new_session=(os.name == "posix"),
        )
    except (OSError, ValueError) as exc:
        result: dict[str, object] = {
            "argv": command,
            "returncode": 127,
            "stdout": "",
            "stderr": f"{type(exc).__name__}: {exc}",
            "duration_seconds": round(time.monotonic() - started, 3),
            "timed_out": False,
            "launch_error": f"{type(exc).__name__}: {exc}",
            "capture_error": None,
            "stdout_truncated": False,
            "stderr_truncated": False,
        }
        result["status"] = process_status(result)
        return result

    stdout_buffer = bytearray()
    stderr_buffer = bytearray()
    stdout_state: dict[str, object] = {"total": 0, "lines": 0, "read_error": None, "stream_error": None}
    stderr_state: dict[str, object] = {"total": 0, "lines": 0, "read_error": None, "stream_error": None}
    stdout_done = threading.Event()
    stderr_done = threading.Event()
    assert process.stdout is not None and process.stderr is not None
    streams: tuple[object, object] = (process.stdout, process.stderr)
    threads = [
        threading.Thread(
            target=_capture_tail,
            args=(process.stdout, stdout_buffer, stdout_state, stdout_done, output_limit,
                  sys.stdout if stream_output else None),
            daemon=True,
        ),
        threading.Thread(
            target=_capture_tail,
            args=(process.stderr, stderr_buffer, stderr_state, stderr_done, output_limit,
                  sys.stderr if stream_output else None),
            daemon=True,
        ),
    ]
    for thread in threads:
        thread.start()

    timed_out = False
    deadline = started + timeout
    next_progress = started + progress_interval
    try:
        while True:
            process_done = process.poll() is not None
            streams_done = stdout_done.is_set() and stderr_done.is_set()
            if process_done and streams_done:
                break
            now = time.monotonic()
            remaining = deadline - now
            if on_progress is not None and now >= next_progress and not process_done:
                on_progress(now - started, max(0.0, remaining))
                next_progress = now + progress_interval
            if remaining <= 0:
                timed_out = True
                _terminate_process_tree(process, terminate_grace)
                break
            time.sleep(min(0.02, remaining))
    except BaseException:
        _terminate_process_tree(process, terminate_grace)
        _join_readers(threads, streams)
        raise

    _join_readers(threads, streams)
    capture_errors = [
        str(value)
        for state in (stdout_state, stderr_state)
        for value in (state.get("read_error"), state.get("stream_error"))
        if value
    ]
    capture_error = "; ".join(capture_errors) or None
    stdout = stdout_buffer.decode("utf-8", errors="replace")
    stderr = stderr_buffer.decode("utf-8", errors="replace")
    if timed_out:
        stderr = (stderr + f"\nTIMEOUT after {timeout:g}s")[-output_limit:]
    if capture_error:
        stderr = (stderr + f"\nOUTPUT CAPTURE ERROR: {capture_error}")[-output_limit:]

    result = {
        "argv": command,
        "returncode": 124 if timed_out else process.returncode if process.returncode is not None else 127,
        "stdout": stdout,
        "stderr": stderr,
        "duration_seconds": round(time.monotonic() - started, 3),
        "timed_out": timed_out,
        "launch_error": None,
        "capture_error": capture_error,
        "stdout_truncated": int(stdout_state["total"]) > output_limit,
        "stderr_truncated": int(stderr_state["total"]) > output_limit,
        "stdout_total_bytes": int(stdout_state["total"]),
        "stderr_total_bytes": int(stderr_state["total"]),
        "stdout_line_count": int(stdout_state["lines"]),
        "stderr_line_count": int(stderr_state["lines"]),
        "stream_output": stream_output,
    }
    result["status"] = process_status(result)
    return result


__all__ = ["DEFAULT_OUTPUT_LIMIT", "process_status", "run_process"]
