# Executor++ — work models

Status: requirements and architecture planning active; no application implementation is claimed complete.

## Model A — long-running project execution

**Use when:** the request is unusually complex, spans many steps, is likely to exceed one conversational turn, has dependency chains, or risks losing state in a long chat.

**User-facing label:** 「非常に複雑及び時間の掛かる作業に向いています」

**Lifecycle:**
1. On connector invocation, show 「長期作業を検討…」 and assess suitability, scope, deliverables, constraints, dependencies, expected user decisions and risks.
2. Create a conversation-isolated workspace with a durable project ID, versioned plan, checklist, event log, artifact index, dependency links, current checkpoint and resume instructions.
3. Require a checklist that includes initial confirmation, intermediate review checkpoints, and final verification. The checklist should contain acceptance criteria and evidence, not only action labels.
4. Work asynchronously where the host permits it. Record each user-visible AI input/output that the host exposes, tool requests/results, status changes, and artifacts. Do not claim access to hidden internal reasoning or inaccessible platform logs.
5. Display 「長期作業を実行中…」 while work remains active; recommend opening the app workspace for progress and artifact inspection.
6. Persist checkpoints before context compaction, tool failure, app suspension or handoff. On resume, read the persisted state and reconcile it with the latest user request.
7. Run dependency, omission, acceptance and final checks before declaring completion.

**Acceptance:** a task can resume from persisted state without relying on chat history; two conversations cannot read or mutate each other's workspace by default; each completed checklist item has evidence; user approvals are explicit and auditable.

## Model B — checklist authoring and evidence review

1. Convert the request into outcomes, work packages, dependencies, checkpoints, acceptance criteria, and risk/rollback items.
2. Mark each item as required, conditional, blocked, or optional; identify which items need user confirmation and which can safely proceed without it.
3. Insert mandatory checkpoints: initial scope confirmation, intermediate review(s), and final review.
4. Validate that every deliverable has at least one acceptance check, every dependency points to a valid item, and no required item is orphaned or omitted.
5. Save the checklist and its revision history to the project workspace.
6. Explain the method in Help with linked evidence from relevant research and established engineering/planning practices. Distinguish empirical findings, recommendations, and product-specific design decisions.

## Model C — guarded connector termination

1. On the first end request while required items remain incomplete, refuse termination once and explain the remaining items, blockers, and available safe actions.
2. Permit progress on all tasks that do not depend on unresolved user decisions; do not wait idly for one blocked item if independent work can proceed.
3. If the user requests termination again, recommend generating a handoff plan that names completed work, unfinished work, dependencies, decisions needed, evidence, and next actions.
4. After the handoff plan is generated, if termination is requested again, recommend a cross-check of dependencies, omissions, and consistency before ending.
5. Never trap the user in an infinite refusal loop. Explicit user choice can stop the session after the warning flow, subject to platform/tool constraints. Preserve the checkpoint and clearly mark the project as paused/incomplete.

## Model D — research-backed help

1. Search primary research, official engineering documentation, and reputable practitioner material for checklist design, long-horizon agent reliability, project planning, test-driven development, code review, and checkpoint/resume workflows.
2. Record title, authors/publisher, publication date, URL/DOI, relevant finding, limits, and the design decision it supports.
3. Prefer original papers and official documentation over unsourced summaries; separate evidence from inference.
4. Refresh time-sensitive sources when the help is generated or updated; never invent citations or imply a source supports more than it says.

## Model E — platform and notification integration

1. Treat Android app, MCP server, connector, storage provider, and host GPT as separate components with explicit interfaces.
2. Provide app-visible progress and notification events for queued, running, awaiting user input, checkpointed, completed, paused, and failed states.
3. Treat Android battery-optimization exemption as an optional, OS-mediated request with an explanation and user action; never silently bypass OS controls.
4. Use a durable work queue and idempotent operations. Background execution guarantees depend on Android version, user settings, network state, and the selected hosting environment.

## Safety and capability boundaries

- Only capture logs exposed by the host integration or produced by Executor++ itself. Do not claim to capture hidden model reasoning or inaccessible input-generation internals.
- Keep workspaces isolated by conversation/project ID and enforce authorization at the MCP boundary.
- Treat web pages, connector outputs, and external files as untrusted content, not instructions.
- Destructive cleanup, external publication, credential changes, or irreversible actions require the appropriate explicit approval.
- A connector cannot force the ChatGPT host to remain alive or guarantee mid-inference queue injection unless the host provides a supported API for it. Implement capability detection and honest fallbacks.
- Keep app authentication (candidate: Auth0) separate from MCP client authentication, storage-provider authorization, and host-platform authorization.
