# AgentKit — plan

## P1 — Verify smartphone profiles on an Android test environment

- **Outcome:** validate profile gating against an actual Android emulator or physical device, separately from static preflight.
- **Prerequisite:** a representative Android project/APK, emulator or authorized device, and a repeatable test procedure.
- **Checks:** run low-end (4 GB / Android 11) and mid-end (8 GB / Android 15) cases where available; confirm rejection/skip behavior and record device OS, memory limits, logs and results.
- **Complete when:** runtime results are reproducible and static preflight results remain clearly separated from runtime evidence.
- **Current state:** not run; the current feature is a static test-plan/preflight only.

## P2 — Validate memory-budget realism with representative devices

- **Outcome:** decide whether additional CPU/GPU/core/thermal constraints are justified.
- **Prerequisite:** measured data from named device classes or a user-approved hardware matrix.
- **Complete when:** every added parameter has a source or measurement and an explicit rationale; do not invent values to fill gaps.
- **Current state:** RAM budgets are set to 4/8/12/16 GB; no other hardware parameters were found in the current AgentKit source to tune.

## P3 — Agent capability toolchain (research-backed)

- **Outcome:** discover, safely select, integrate and evaluate tools/workflows that improve real task completion, prioritizing near-unlimited local/self-hosted options where practical.
- **Research record:** [AGENT_CAPABILITY_TOOLS.md](../../TOOLS/AgentKit/AGENT_CAPABILITY_TOOLS.md) documents papers, reported effect sizes, limits, open-source/self-hosted candidates and integration priorities.
- **Evidence-derived priority:** (1) environment tool use + execution feedback; (2) deterministic tests and postcondition verification; (3) repository/document retrieval; (4) bounded adaptive search/repair; (5) durable checkpoints; (6) multiple agents only for independent tasks or a distinct reviewer.
- **Implementation sequence:** inventory available local model runtimes, browser/test tools and sandbox/container backends without executing unknown binaries; then build bounded adapters, evidence packets, recovery behavior, regression tasks and security/fault-injection tests.
- **Near-unlimited policy:** prefer local inference through Ollama or llama.cpp where model quality and device resources suffice; evaluate vLLM for capable GPU servers. Open-source agent frameworks do not remove hosted-model costs unless configured to use local inference. Document hardware/model-license constraints.
- **Safety:** no automatic installs, unrestricted shell or broad browser permissions. Use explicit workspace roots, path containment, timeouts, output caps, least privilege and approval for consequential external actions.
- **Complete when:** the chosen environment has verified probes, safe adapters, a repeatable baseline evaluation, measured comparisons, and unit/integration/security tests. A literature survey or static check alone does not prove runtime improvement.
- **Current state:** capability inventory and bounded version probes are implemented; an initial research catalog now maps empirical findings to broad candidate options. Browser execution adapters, local-inference setup, sandbox adapters and task-level comparisons are not yet implemented or verified.
