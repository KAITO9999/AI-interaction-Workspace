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

## Unknowns requiring evidence

- Whether the target GPT host supports mid-inference queue injection, reliable asynchronous connector continuation, connector lifecycle control, and access to full input/output logs.
- Which selected storage providers expose stable APIs/URIs and can be integrated under their current terms and permissions.
- Auth0 SDK version and setup method; must be checked at implementation time, and no client secret may be embedded in the app.
- Actual Android background execution behavior on supported OS/device versions.
