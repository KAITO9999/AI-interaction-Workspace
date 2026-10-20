# Executor++ — plan

Status: planned; application implementation has not started.

## P0 — Freeze the capability boundary and host integration strategy

- **Outcome:** a capability matrix separates features implementable in the app/MCP server from features requiring a supported ChatGPT host API.
- **Prerequisite:** inspect available host APIs, connector/plugin constraints, Android background execution rules, and authentication requirements.
- **Checks:** classify each feature as supported, conditional, fallback-only, or unavailable; document evidence and test method.
- **Queue decision:** implement the queue in the app. If a request arrives while a task is running, show a clear “キューに追加しました” status, persist the request, let the current task reach a safe stopping point, then ask the user to confirm/review the queued request before execution. Do not pretend this inserts a message into the active model generation if the host does not support that.
- **GPT access decision:** plan both (a) native/in-host access using supported ChatGPT/plugin/app integration surfaces and (b) direct API access using official API credentials/authorization. Keep these as separate adapters with separate permission, cost, context, and capability explanations; do not scrape private app internals or collect account passwords.
- **Complete when:** queueing, connector lifecycle control, notification delivery, visible AI-log capture, conversation editing, and both GPT access routes have explicit supported-path/fallback behavior; no unsupported capability is represented as guaranteed.

## P1 — Establish the project records and requirements baseline

- **Outcome:** requirements, architecture decisions, work models, and handoff rules are stored in this project record.
- **Complete when:** the four canonical project files exist and requirements are cross-checked against the user request.
- **State:** project record created on the current work branch; requirement coverage review pending.

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
- **Queued request UX:** while a job is running, allow the user to submit another request into a durable app queue; show “キューに追加しました”; do not interrupt the current job mid-step. After the current job reaches a safe completion/checkpoint, display the queued request for user review/confirmation before starting it. Support reorder, cancel, edit, and dependency labels for queued requests.
- **MCP lifecycle:** distribute supported MCP server packages through the app; manage installation, configuration, start/stop, update, health checks, logs, and recovery through the app, subject to platform permissions.
- **Checks:** UI/accessibility tests, event-delivery tests, background/foreground transition tests, Android version compatibility.
- **Complete when:** user can see current state and recover from a stopped or failed task without reconstructing it from chat history.

## P5 — Storage and authentication integration

- **Outcome:** storage adapter design supports Android SAF and eligible connected providers (e.g. Google Drive, Dropbox, Proton Drive or file-manager integrations only where supported); app authentication is evaluated separately from MCP authentication.
- **Checks:** permission denial, revoked authorization, provider unavailable, offline, large artifact, and path/URI persistence cases.
- **Complete when:** provider support is verified individually, authorization is least-privilege, and credentials are not embedded in source or logs.

## P6 — Battery and notification controls

- **Outcome:** low-cost standby/keep-alive is evaluated as an app feature, alongside opt-in battery-optimization exemption guidance and robust progress/attention notifications.
- **Checks:** permission denied, app force-stop, Doze/background restrictions, notification permission denied, duplicate/reordered events, and retry after network loss. Measure battery/network cost rather than claiming “always on” without measurements.
- **Complete when:** limitations are explained, notifications are not falsely guaranteed, and the user can resume from persisted state.

## P7 — Verification, release preparation and icon

- **Outcome:** reproducible test results, help documentation, app/MCP packaging plan, and product icon asset.
- **Checks:** unit/integration tests, static checks, Android runtime test on a supported environment, security review of workspace isolation, dependency/omission audit, and user-facing capability claims review.
- **Complete when:** evidence and known limitations are recorded; no runtime behavior is marked verified without an observed test.

## P8 — Asset cache, safe web input, context handoff and concurrent goals

- **Outcome:** implement the earlier Executor++ requirements that are separate from long-work mode and ensure they are not lost while building the app.
- **Asset cache:** accept image, GIF, video, text, JavaScript, and other supported file types; GIF-to-video conversion may be used as an operational representation while retaining original-file provenance. At inference completion, summarize artifacts by storage location/group/folder, count, filename, format, size, and original/derived relation. Ask the user what to retain; discard unselected temporary items according to an explicit retention policy.
- **Storage selection:** let the user choose a supported destination/provider in app settings; treat selected locations as provider-specific URIs/handles, not assume every cloud provider behaves like a local filesystem path.
- **StartPage and safe external text input:** provide StartPage access through the connector-management layer and a whitelist-based gateway for text entry into approved search fields/sites (e.g. StartPage, YouTube, Reddit); validate destination and payload, block arbitrary navigation/script execution, and log the action.
- **Context handoff:** support three reduction levels; abbreviate items longer than 80 characters with an ellipsis and expose an expansion path; show the latest five items first, with older items paged in groups of five; show full content when the set contains ten or fewer items. Test boundary counts, Unicode length, empty sets, and expansion.
- **Concurrent goals and queue:** allow independent tool goals to run concurrently when safe, record per-goal status, notify GPT of completed calls while other work continues, and implement queued follow-up requests in the app even if host-side mid-inference injection is unavailable. A queued request must wait until the active task reaches a safe stopping point, then require user review/confirmation before execution. Use bounded concurrency, cancellation, idempotency and conflict handling.
- **Complete when:** every subfeature has tests, permissions and failure behavior documented, and a requirement-by-requirement gap check shows no omitted requirement.

## P9 — Connector management, conversation correction, and alternate GPT access

- **Conversation self-correction/editing:** investigate supported APIs for editing or correcting a conversation through connector management. If the host does not permit editing existing messages, provide a transparent alternative such as a corrected follow-up, revision proposal, or exported edited copy; never claim to rewrite host history when it cannot.
- **StartPage connector access:** manage the StartPage connection, access policy, approved destinations, and text-input allowlist from connector settings; keep the actual safe search-input gateway in P8.
- **GPT access beyond MCP — provide both routes:** (A) native/in-host integration through supported ChatGPT app/plugin/extension surfaces, with capability limits explicitly documented; and (B) direct API access through the official API using a separately configured API credential/authorization flow, with usage/cost limits and context transfer controls. Keep adapters, permissions and audit logs separate. Do not scrape private app internals, bypass platform restrictions, or request/store the user's ChatGPT account password. If a native route is unavailable, provide the supported fallback; if API access is unconfigured, offer setup instructions rather than silently failing.
- **Complete when:** the host capability matrix documents whether each feature is native, API-backed, fallback-only, or unavailable, with permission/security review and tests for every implemented path.


## P10 — AI handoff bundle and task observability (recommended addition)

- **Outcome:** every long or multi-tool task can be handed to another agent/session without relying on hidden chat history.
- **Handoff bundle:** objective and acceptance criteria; current plan/checklist and completion percentage; current state and next action; constraints and decisions with rationale; relevant files/paths and exact versions/commit IDs; commands executed and summarized outputs; tests run with pass/fail evidence; unresolved risks/blockers; required permissions/credentials by *name only* (never secret values); dependency graph; rollback/recovery steps.
- **Change/provenance log:** record who/what changed which artifact, when, why, and which validation ran. Keep append-only event records where practical and distinguish observed facts from AI assumptions.
- **Environment snapshot:** intentionally excluded as an automatic AI-generated handoff requirement because inferred environment data can be wrong. If environment details are needed, display directly observed facts, their source/time, and explicitly unknown fields for user review; never let an unverified inference silently become a precondition.
- **Reproducible failure bundle:** record exact reproduction steps, expected vs actual result, minimal safe input/sample, relevant error excerpts, affected version, and regression test. Redact secrets and sensitive user data.
- **Permission and side-effect policy:** record per-tool access mode (read/write/delete/external-send), scope, reversibility, approval requirement, and applicable user decision. Enforce this policy in the tool execution layer, not only in prompts.
- **Context packet builder:** create a compact, redacted, project-specific context packet with source links and hashes; include only minimum relevant context and avoid cross-conversation leakage. Support export/import for another model/agent.
- **Failure/retry protocol:** classify transient/permanent/permission/conflict failures; bounded retries with backoff; idempotency keys; checkpoint before destructive actions; require confirmation for irreversible or external side effects.
- **Acceptance/verification packet:** map each acceptance criterion to evidence, tests, screenshots/log references, and known limitations; do not treat generated claims as proof.
- **Complete when:** a new session/agent can resume from the bundle, independently verify the state, and avoid repeating already-completed work.


## P11 — Research-informed recovery, evidence and agent-security controls

- **Recovery by re-observation:** after a crash, timeout, context compaction, or model/session change, reload the durable checkpoint and re-check the actual workspace/tool state before continuing. Do not blindly replay the last action. Reconcile the recorded intent with observable outcomes and choose retry, skip, or escalation based on evidence.
- **Action receipts and effect ledger:** for state-changing tool calls, persist a request/idempotency key, intended effect, tool response/receipt, observed postcondition, and reconciliation status. Where the provider cannot guarantee idempotency or query the result, explicitly mark the outcome uncertain and ask before repeating a potentially duplicate side effect.
- **Evidence-linked claims:** important completion claims and research conclusions should link to source files, URLs, command outputs, test IDs, or log references. Show the difference between direct observation, source-backed inference, and unverified hypothesis.
- **Context-compaction safeguards:** preserve task goal, acceptance criteria, current checkpoint, decisions, pending actions, blockers, and key evidence before compressing history. Make compressed context recoverable through links to original records; test that compression does not remove required state.
- **Agent-injection evaluation:** test malicious instructions embedded in webpages, files, comments, and tool outputs; external content must be treated as data, not authority. Verify tool allowlists, destination validation, least privilege, and confirmation gates under adversarial inputs.
- **Recovery/fault-injection tests:** simulate app/process termination, network loss, duplicate/reordered events, timeout after a remote side effect, expired authorization, corrupted checkpoint, and interrupted artifact writes. Measure recovery fidelity and ensure no unsafe duplicate action occurs.
- **Complete when:** recovery and security tests cover both normal and adversarial paths; uncertain outcomes remain visible; the system never claims exactly-once execution unless the specific tool/provider contract proves it.


## P12 — Model identity, model capability catalog, and source-required claims

- **Model identity in work records:** whenever a plan, handoff, evaluation, comparison, or implementation note depends on work performed by different models, explicitly record the model's exact displayed name/version (and provider where known) beside the contribution. If the model identity is unavailable, label it "unknown/unverified"; never infer it from writing style.
- **Separate model-characteristics catalog:** maintain a dedicated, extensible catalog (initial examples requested: GPT-6, Sonnet 5, Grok 4.5; add further models over time) separate from the task plan and work-model procedures. Keep one profile per model/version and allow additions without redesigning the schema.
- **Mandatory sourcing:** every factual claim about a model's features, limits, benchmarks, token/pricing rates, context window, modalities, tool use, availability, or comparative performance must include a direct source URL and access/publication date. Prefer official model cards, API docs, release notes and benchmark papers/datasets. For benchmarks, record task, date, setup, scoring method, and source; do not compare scores from incompatible settings as if equivalent.
- **Evidence and uncertainty:** label each field as source-confirmed, independently measured, inferred, disputed, or not verified. Keep source text/links and a short explanation of what the source actually supports. If no reliable source exists, mark unknown rather than filling gaps with model assumptions.
- **Per-task model attribution:** capture the model identity for each substantive model contribution in the provenance/handoff record, along with role, date, relevant output/artifact, and verification status. Do not expose hidden chain-of-thought; record only user-visible outputs and auditable work metadata.
- **Cross-model review:** allow a second, explicitly named model to review requirements, omissions, inconsistencies, security risks, and acceptance evidence. Treat its result as a review signal, not truth; require source/test evidence and human approval for consequential or uncertain changes.
- **AI self-audit:** run a structured completeness/consistency check against the plan, dependencies, user constraints, and acceptance criteria. Report findings with evidence and severity; never silently alter user requirements or treat an AI-generated audit as proof.
- **Complete when:** the catalog schema and update workflow exist; all model-related factual claims in Help/comparison views have sources; task records identify the model where known; unverified names/claims remain clearly marked; and model-review/self-audit tests cover false positives and missing evidence.


## P13 — Integrate high-impact agent tools through the MCP/AgentKit workflow

- **Outcome:** Executor++ can use tested tool adapters instead of relying only on model-generated reasoning.
- **Initial tool set:** Playwright browser automation/UI testing; workspace-scoped shell/filesystem/patching; deterministic test/evaluation harness; optional independent model review.
- **Source and design record:** [AgentKit researched capability tools](../../TOOLS/AgentKit/AGENT_CAPABILITY_TOOLS.md).
- **Capability-aware routing:** probe the target environment first and select an installed, tested adapter; if unavailable, report the limitation and provide a documented fallback rather than pretending the tool ran.
- **Evidence loop:** observe → act → verify → repair → record. Persist command/test results, screenshots/traces, changed paths, exact versions, model attribution, and acceptance evidence. Re-observe after interruption before resuming.
- **Security:** tool definitions and external page/file content are untrusted; constrain browser destinations and filesystem roots, use bounded execution, require confirmation for consequential external/destructive actions, and enforce permissions in the execution layer.
- **Complete when:** each adapter has a capability probe, bounded smoke test, tests for success/failure/timeout, evidence output, and documented limitations. No tool is marked available or tested without observed results.
