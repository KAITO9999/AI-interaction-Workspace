# AgentKit — cache

Status: smartphone profile preflight implementation and CI validation passed; Android runtime validation pending.
Last reviewed: 2026-10-21

## Verified source facts

- AgentKit previously had core environment probing, executable inventory, TypeScript compilation, provenance recording, add-on auditing, and command resolution.
- The prior source did not contain a smartphone hardware profile matrix with CPU-core, clock, GPU, or thermal parameters.
- Smartphone memory budgets requested for this feature are 4 GB, 8 GB, 12 GB and 16 GB.
- Android 11 maps to API 30 and Android 15 maps to API 35 for the configured compatibility gates.

## Decisions

- Low-end defaults to 4 GB and Android 11/API 30; mid-end defaults to 8 GB and Android 15/API 35; mid-high and high-end default to 12 GB and 16 GB without a default Android-version gate.
- When a literal minSdkVersion exceeds a selected target API, that profile is rejected. An unresolved minimum SDK blocks version-gated profiles for review rather than assuming compatibility.
- The tool is a static preflight and profile planner. It does not claim emulator, physical-device, or performance testing.

## Completed items moved from PLAN

| 2026-10-21 | Add smartphone profile preflight and automated compatibility gate | PASS; 39 AgentKit unit tests passed in GitHub Actions on Ubuntu; Python compilation and shell syntax checks passed; provenance validation passed; 115 repository-local Markdown links checked. Pull request: [#13](https://github.com/KAITO9999/AI-interaction-Workspace/pull/13). Physical-device/emulator tests remain pending.


## Research review — near-unlimited agent capability candidates (2026-10-21)

- **Evidence reviewed:** PAL, ReAct, SWE-agent, SWE-bench, self-consistency, Tree of Thoughts, test-time scaling survey, RAG, Self-Refine, reflection limits, multi-agent debate and a 2026 Nature Machine Intelligence study on collaboration limits.
- **Decision:** prioritize execution with real feedback and objective verification; use retrieval for project knowledge; use bounded adaptive search/repair only when checks show the first attempt failed; keep multi-agent debate optional.
- **Candidate families:** Ollama/llama.cpp (local model serving), Aider/SWE-agent/OpenHands SDK/Cline (agent interfaces), Playwright MCP/Browser Use (browser), Inspect AI/Promptfoo/Hypothesis (evaluation/testing), local Markdown/JSON/Git checkpoints (durable memory), Chroma (optional semantic retrieval), and vLLM (GPU server).
- **Near-unlimited interpretation:** local inference avoids per-token hosted-model fees but remains bounded by hardware, energy, speed, context, model license and model capability. Open-source tools connected to a paid/limited API are not near-unlimited in this sense.
- **Full sources:** see [AGENT_CAPABILITY_TOOLS.md](../../TOOLS/AgentKit/AGENT_CAPABILITY_TOOLS.md).
- **Limitations:** no candidate was installed or run as part of this research pass. Availability, security, hardware fit and end-to-end improvement remain UNKNOWN pending probes and fixed-task evaluation.


## MCP discovery and route selection — 2026-10-21

- **Implementation added, verification pending:** `agentkit_mcp.py` checks known local MCP configuration locations and explicitly supplied files. It emits server names, transport, command basename, host and environment-variable names, but not secret values, server args or URL paths/query strings.
- **Boundary:** local config presence does not establish server reachability/authentication and cannot reveal MCP connections managed by the hosted GPT process.
- **Implementation added, verification pending:** `agentkit_routes.py` selects an available command from an ordered allowlist or routes to an AgentKit fallback, without auto-installation.
- **Implementation added, verification pending:** `agentkit_ruff.py` delegates to official Ruff when found; otherwise it reports E999 and a conservative F401 subset. It is not Ruff-compatible and does not format or rewrite files.
- **Scope decision:** Playwright/browser automation and local LLM installation/serving are excluded from AgentKit's plan.
- **Official Ruff references:** https://github.com/astral-sh/ruff and https://github.com/astral-sh/ruff/blob/main/docs/configuration.md.
