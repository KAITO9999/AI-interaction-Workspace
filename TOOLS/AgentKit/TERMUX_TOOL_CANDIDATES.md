# Termux Tool Inventory and AgentKit Candidates

**Observed:** 2026-10-20, through the connected Termux command inventory and PATH checks. The MCP inventory reported 1,016 executable names. This is a snapshot, not a guarantee that every command is runnable in every shell or project directory.

## Existing tools verified on PATH

| Capability | Commands observed | AgentKit implication |
|---|---|---|
| Python | `python`, `python3`, `pip` | Keep standard-library fallbacks dependency-light; test on Python 3.14.6 |
| Search | `rg`, `grep` | Prefer ripgrep, retain a bounded Python fallback |
| JSON | `jq` | Validate JSON through a fixed argv invocation; Python `json` remains fallback |
| Archives | `7z`, `tar`, `unzip`, `zip` | Prefer 7-Zip for listing multiple archive formats; current Python fallback intentionally lists ZIP only |
| Hashing | `sha256sum`, `openssl`, `rhash` | Use SHA-256 as a stable verification primitive |
| Python lint | `ruff` | Candidate for a dedicated lint task; do not install a second linter by default |
| Shell lint | `shellcheck` | Candidate for shell-script static analysis; `sh -n` is a weaker syntax-only fallback |
| JavaScript / TypeScript | `node`, `npm`, `npx`, `tsc` | Existing AgentKit `compile-ts` already covers compilation; avoid duplicating it |
| Git / GitHub | `git`, `gh` | Could report repository state, but never execute authenticated or mutating commands without a separate explicit request |
| Transfer / network | `curl`, `wget`, `rsync`, `ssh` | Use only in separately opted-in network workflows; do not auto-run as a generic fallback |
| Database | `sqlite3` | Potential read-only SQLite inspection task with query restrictions and explicit database path |
| Binary inspection | `file`, `7z`, `openssl` | Potential metadata/format probes without extraction or execution |
| Existing agent tools | `HyAI`, `codex`, `opencode`, `fallow-mcp`, `termux-native-mcp` | Treat as orchestration/integration candidates; inspect each tool's contract before invoking or wrapping |

## Prioritized candidate backlog

### P1 — Python lint task

- **Command:** `ruff check`.
- **Fallback:** `python -m compileall` or `py_compile` for syntax only.
- **Value:** Distinguishes syntax validity from lint diagnostics, while avoiding a new dependency in Termux.
- **Guardrail:** Report the fallback as syntax-only, never as lint-equivalent.

### P1 — Shell script audit

- **Command:** `shellcheck`.
- **Fallback:** `sh -n` only for POSIX shell syntax.
- **Value:** Detects quoting, portability, and common shell hazards in AgentKit and workspace scripts.
- **Guardrail:** Select shell dialect explicitly; do not claim `sh -n` catches ShellCheck findings.

### P2 — Archive inspection expansion

- **Command:** `7z l` (implemented in the resolver).
- **Fallback:** Python `zipfile`, limited to ZIP-compatible files.
- **Value:** Supports listing formats beyond ZIP when 7-Zip is installed.
- **Guardrail:** List only by default. Extraction requires a separate feature with path traversal, symlink, size, and decompression-bomb protections.

### P2 — Read-only SQLite inspection

- **Command:** `sqlite3`.
- **Fallback:** Python `sqlite3` opened in read-only URI mode.
- **Value:** Inspect schema, table names, and row counts without adding a package.
- **Guardrail:** Do not accept arbitrary SQL by default; reject writes/DDL and never open unknown databases in writable mode.

### P3 — File-type and integrity report

- **Commands:** `file`, `sha256sum`, optionally `openssl`.
- **Fallback:** Python magic-byte checks for a short allowlist and `hashlib`.
- **Value:** Verify downloaded or generated artifacts before parsing.
- **Guardrail:** File-type detection is advisory; never execute files based on their reported type.

### P3 — Repository state summary

- **Command:** `git status --short --branch` and bounded `git diff --check`.
- **Fallback:** None; Git semantics should not be simulated by a Python approximation.
- **Value:** A safe preflight before edits or PR preparation.
- **Guardrail:** Read-only only; commits, resets, pushes, and PR merges stay behind explicit user intent.

## Implementation rules

1. Inventory results are informational, not an execution allowlist.
2. Prefer tools already installed; do not install tools merely because they appear in the candidate backlog.
3. Every subprocess uses an argv list, a timeout, and bounded output. No shell interpolation.
4. Install attempts are opt-in, package names are allowlisted, and no automatic privilege escalation or retry is allowed.
5. Tests must exercise both the external-command path and the fallback path. State compatibility limits plainly.
6. Existing capabilities (`compile-ts`, command inventory, change ledger, add-on audit) must be reused rather than duplicated.
