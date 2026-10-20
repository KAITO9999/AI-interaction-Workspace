# Executor++ — plan

Status: planned; application implementation has not started.

## P0 — Freeze the capability boundary and host integration strategy

- **Outcome:** a capability matrix separates features implementable in the app/MCP server from features requiring a supported ChatGPT host API.
- **Prerequisite:** inspect available host APIs, connector/plugin constraints, Android background execution rules, and authentication requirements.
- **Checks:** classify each feature as supported, conditional, fallback-only, or unavailable; document evidence and test method.
- **Complete when:** mid-inference queue insertion, connector lifecycle control, notification delivery, and visible AI-log capture have explicit supported-path/fallback behavior; no unsupported capability is represented as guaranteed.

## P1 — Establish the project records and requirements baseline

- **Outcome:** requirements, architecture decisions, work models, and handoff rules are stored in this project record.
- **Complete when:** the four canonical project files exist and requirements are cross-checked against the user request.
- **State:** project record created on the current work branch; cross-check pending.

## P2 — Research-backed long-work checklist and termination state machine

- **Outcome:** implementable state machine and help content for long-running projects.
- **Includes:** suitability prompt; mandatory initial/intermediate/final checkpoints; dependency-aware checklist; first termination refusal; second termination handoff-plan prompt; subsequent dependency/omission review prompt; resumable paused state.
- **Checks:** test normal completion, blocked-by-user-decision, independent work continuing, first/second/subsequent termination requests, and resume after interruption.
- **Complete when:** transitions are deterministic, there is no infinite refusal loop, and all user-facing messages distinguish complete, paused, blocked, and failed states.

## P3 — Conversation-isolated MCP workspace and durable queue

- **Outcome:** each conversation/project has separate durable state for plans, checklist revisions, event logs, artifacts, dependency edges, user decisions, and resume checkpoints.
- **Prerequisite:** P0 capability matrix and storage interface design.
- **Checks:** isolation tests across two projects; persistence/restart tests; idempotency and concurrent-update tests; migration/backup behavior.
- **Complete when:** restart/resume works from persisted state and authorization prevents cross-project access.

## P4 — App workspace, connector lifecycle and progress UI

- **Outcome:** app can browse workspaces, view input/output records exposed by the integration, inspect artifacts, review checklist progress, and manage connector/MCP server lifecycle.
- **Includes:** 「長期作業を検討…」 and 「長期作業を実行中…」 statuses; event notifications; user confirmation queue; app-visible error and resume controls; GPT-suggested follow-up ideas surfaced as suggestions, not silently executed.
- **Checks:** UI/accessibility tests, event-delivery tests, background/foreground transition tests, Android version compatibility.
- **Complete when:** user can see current state and recover from a stopped or failed task without reconstructing it from chat history.

## P5 — Storage and authentication integration

- **Outcome:** storage adapter design supports Android SAF and eligible connected providers (e.g. Google Drive, Dropbox, Proton Drive or file-manager integrations only where supported); app authentication is evaluated separately from MCP authentication.
- **Checks:** permission denial, revoked authorization, provider unavailable, offline, large artifact, and path/URI persistence cases.
- **Complete when:** provider support is verified individually, authorization is least-privilege, and credentials are not embedded in source or logs.

## P6 — Battery and notification controls

- **Outcome:** opt-in battery-optimization exemption guidance and robust progress/attention notifications.
- **Checks:** permission denied, app force-stop, Doze/background restrictions, notification permission denied, duplicate/reordered events, and retry after network loss.
- **Complete when:** limitations are explained, notifications are not falsely guaranteed, and the user can resume from persisted state.

## P7 — Verification, release preparation and icon

- **Outcome:** reproducible test results, help documentation, app/MCP packaging plan, and product icon asset.
- **Checks:** unit/integration tests, static checks, Android runtime test on a supported environment, security review of workspace isolation, dependency/omission audit, and user-facing capability claims review.
- **Complete when:** evidence and known limitations are recorded; no runtime behavior is marked verified without an observed test.

## P8 — Asset cache, safe web input, context handoff and concurrent goals

- **Outcome:** implement the earlier Executor++ requirements that are separate from long-work mode and ensure they are not lost while building the app.
- **Asset cache:** accept image, GIF, video, text, JavaScript, and other supported file types; GIF-to-video conversion may be used as an operational representation while retaining original-file provenance. At inference completion, summarize artifacts by storage location/group/folder, count, filename, format, size, and original/derived relation. Ask the user what to retain; discard unselected temporary items according to an explicit retention policy.
- **Storage selection:** let the user choose a supported destination/provider in app settings; treat selected locations as provider-specific URIs/handles, not assume every cloud provider behaves like a local filesystem path.
- **Safe external text input:** provide a whitelist-based gateway for text entry into approved search fields/sites (e.g. StartPage, YouTube, Reddit); validate destination and payload, block arbitrary navigation/script execution, and log the action.
- **Context handoff:** support three reduction levels; abbreviate items longer than 80 characters with an ellipsis and expose an expansion path; show the latest five items first, with older items paged in groups of five; show full content when the set contains ten or fewer items. Test boundary counts, Unicode length, empty sets, and expansion.
- **Concurrent goals and queue:** allow independent tool goals to run concurrently when safe, record per-goal status, notify GPT of completed calls while other work continues, and support queued follow-up work only where the host supports it. Use bounded concurrency, cancellation, idempotency and conflict handling.
- **Complete when:** every subfeature has tests, permissions and failure behavior documented, and a requirement-by-requirement gap check shows no omitted requirement.
