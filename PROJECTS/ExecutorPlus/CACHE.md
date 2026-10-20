# Executor++ — cache

Status: requirements captured; no implementation or runtime validation claimed.
Last reviewed: 2026-10-21

## Verified repository facts

- The workspace repository defines exactly four canonical files for each active project: `WORK_MODELS.md`, `PLAN.md`, `CACHE.md`, and `IN_PROGRESS.md`.
- The public repository must not contain raw private conversations, personal data, credentials, private source material, or private workspace URLs.
- AgentKit is available under `TOOLS/AgentKit/`; its workflow recommends fetching only relevant source, recording exact checks and limitations, and using a bounded Git retrieval attempt only if connector retrieval cannot provide the needed files.

## User requirements captured

- Executor++ is intended to combine an app, MCP server(s), and connector-facing functionality.
- Long-running work must be a distinct large-scale feature labelled as suitable for very complex and time-consuming tasks.
- Work state must be isolated by conversation and persisted outside the chat transcript.
- The checklist must require initial confirmation, intermediate review, and final verification.
- Termination requests must follow a staged warning/handoff process without trapping the user indefinitely.
- The app should show work status and available AI input/output logs, while MCP tools enable GPT to inspect and operate on the workspace.
- Add battery-optimization exemption guidance and GPT-related notifications as candidate features.
- Earlier requirements also include an app-managed asset cache, storage-provider selection, whitelist-based external text input, context handoff, connector/MCP lifecycle management, queued work, parallel task execution, suggestions, Auth0 evaluation, and a designed icon.

## Decisions

- The app platform remains a candidate decision: native Android/Kotlin is the default working hypothesis because SAF and battery/notification controls are Android-specific; verify before implementation.
- Auth0 is a candidate for app authentication, not a substitute for MCP client authentication or storage-provider authorization.
- The workspace should preserve event logs and artifacts, not attempt to capture hidden model reasoning or host-internal data that the integration does not expose.
- Battery-optimization exemption is optional and OS-mediated; it cannot guarantee uninterrupted background execution.
- Host-specific behavior such as injecting a queue during inference or directly ending a host connector must be gated by actual API support, with an explicit fallback if unsupported.
- Public GitHub project records contain requirements and safe summaries only, not raw chat logs or secrets.

## Initial research leads for checklist/help design

These are initial research leads, not yet a complete systematic review. The help feature should revisit the sources, inspect methods/limitations, and distinguish source findings from product recommendations.

- **HiAgent: Hierarchical Working Memory Management for Solving Long-Horizon Agent Tasks with Large Language Model** (ACL 2025): proposes subgoal-based memory chunks and selective replacement of old action-observation history; the paper reports improved results across five long-horizon tasks. Design implication: persist structured subgoals and retrieve only relevant evidence rather than repeatedly injecting the entire transcript. Source: https://aclanthology.org/2025.acl-long.1575/
- **Can We Rely on LLM Agents to Draft Long-Horizon Plans? Let's Take TravelPlanner as an Example** (arXiv, 2024): reports failures to attend to important information in long/noisy contexts and limitations in plan refinement. Design implication: plans need explicit constraints, acceptance checks, and independent review rather than trusting a generated plan as complete. Source: https://arxiv.org/abs/2408.06318
- **AMA-Bench: Evaluating Long-Horizon Memory for Agentic Applications** (PMLR/ICML 2026): evaluates memory over action-observation trajectories and reports weaknesses in systems that lose causal/objective information through lossy retrieval. Design implication: keep dependencies, causal links, state changes, and objective-linked evidence in addition to similarity-searchable notes. Source: https://proceedings.mlr.press/v306/zhao26bs.html
- **The Effects of Test-Driven Development on External Quality and Productivity: A Meta-Analysis** (IEEE TSE, 2013): synthesizes 27 studies; reported effects vary by context, with a small positive average quality effect and little clear overall productivity effect. Design implication: make tests and observed results mandatory evidence for implementation claims, but do not promise that TDD universally increases speed. Source: https://doi.org/10.1109/TSE.2012.28
- **ACM SIGSOFT Empirical Standards for Software Engineering**: offers method-specific checklists for evaluating research quality and validity. Design implication: the help content should include evidence quality, limitations, reproducibility, and validity checks rather than only a task list. Source: https://www2.sigsoft.org/EmpiricalStandards/

## Unknowns requiring evidence

- Whether the target GPT host supports mid-inference queue injection, reliable asynchronous connector continuation, connector lifecycle control, and access to full input/output logs.
- Which selected storage providers expose stable APIs/URIs and can be integrated under their current terms and permissions.
- Auth0 SDK version and setup method; must be checked at implementation time, and no client secret may be embedded in the app.
- Actual Android background execution behavior on supported OS/device versions.
