# AgentKit — plan

## P0 — MCP configuration discovery and execution-route selection

- **Outcome:** inspect supported local MCP configuration locations safely, inventory configured server metadata without secret values, and automatically choose a permitted route for supported tasks.
- **Implementation:** `TOOLS/AgentKit/agentkit_mcp.py` inventories known Claude Desktop/Code, Cursor, VS Code and Codex config paths plus explicit config paths. `TOOLS/AgentKit/agentkit_routes.py` selects the first available allowlisted command or a documented AgentKit fallback.
- **Safety:** no credential-store, shell-history, arbitrary home-directory or conversation-history scanning; no secret values, raw server arguments or URL query/path output; no auto-install; no security/permission bypass.
- **Important boundary:** local configuration discovery cannot observe MCP connections managed by the hosted GPT process. Use host-provided connection/tool metadata for that layer. Configured is not the same as reachable, authenticated or functional.
- **Complete when:** fixture tests cover common config shapes, malformed files, redaction, empty results, route precedence, fallback warnings and execution failures; CI passes; live connection state remains explicitly marked unknown unless independently verified.

## P1 — Ruff-compatible route with honest reduced fallback

- **Outcome:** use official Ruff when available; otherwise run a bounded Python standard-library fallback for the subset that AgentKit can implement safely.
- **Fallback support:** syntax/parse errors (E999) and conservative unused-import checks (F401). No source mutation or automatic fix.
- **Limitations:** this fallback is not Ruff-compatible; it does not implement all Ruff rules, configuration semantics, scope analysis, formatting or autofix. Formatting must use official Ruff; if unavailable, return an explicit unsupported status.
- **Complete when:** tests prove route selection, syntax failure, unused-import detection, clean-file behavior, no source mutation and explicit unsupported formatting; reports identify the engine and compatibility level.

## P2 — Unified route reports and verification

- **Outcome:** make each route choice explainable and verifiable.
- **Required report fields:** task, selected route/command, fallback identity, compatibility level, whether installation occurred (false by default), exit status and observed output where available.
- **Checks:** do not treat PATH presence or configuration entries as proof of successful execution. Keep route selection separate from task success; verify outputs/postconditions after execution.
- **Safety:** no arbitrary shell construction, no automatic retries after uncertain side effects, bounded timeouts/output where subprocesses are used, and explicit approval for consequential external operations.

## P3 — Maintain existing AgentKit utilities and project-specific validation

- Preserve the existing environment inventory, TypeScript compile helper, provenance ledger, archive/add-on audit, mobile preflight, and task-specific command resolver.
- Add regression tests for path containment, malformed config, unknown commands, timeouts, output limits, and fallback compatibility as those code paths are changed.
- Keep static preflight distinct from runtime validation; never claim device or remote MCP behavior from static configuration alone.

## Out of scope for AgentKit

- Browser automation frameworks and adapters, including Playwright.
- Local LLM installation, model serving and model-performance evaluation.
- These may be handled as separate projects, but they are not AgentKit tasks and are not part of this plan.

## Current state

- **Implemented in source:** initial environment discovery, task-specific resolver and Python substitutes, provenance records, TypeScript compile helper, add-on audit and mobile compatibility preflight.
- **New source added in this work:** local MCP config inventory, Ruff-aware wrapper with reduced standard-library fallback, and an automatic route selector.
- **Validation status:** implementation must be checked by the current GitHub Actions run before being described as CI-verified. Local config discovery does not verify GPT-hosted MCP connection state.
