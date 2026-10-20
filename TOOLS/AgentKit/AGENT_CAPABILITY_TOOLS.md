# AgentKit — researched agent capability tools

Status: researched and prioritized for integration; external packages have not been installed by this document, and no runtime integration is claimed verified.

## Goal

Increase practical task completion by giving an AI a controlled loop of observe → act → verify → repair → record → resume. Prefer deterministic, auditable tools over simply adding more tool descriptions.

## Priority order

### Tier 1 — Browser automation and real UI verification

**Candidate:** Playwright. Choose one entry path per environment:
- `playwright-cli` for coding-agent workflows where concise command output and on-demand skills reduce context use.
- `@playwright/mcp` for structured browser interaction and iterative exploration.
- `@playwright/test` for repeatable end-to-end tests, assertions, reports, and traces.

Official sources:
- Coding-agent CLI and MCP comparison: https://playwright.dev/docs/getting-started-cli
- MCP introduction and capability configuration: https://playwright.dev/mcp/introduction
- MCP capabilities (testing, storage, network, vision, PDF, DevTools): https://playwright.dev/mcp/capabilities
- Test installation and browser support: https://playwright.dev/docs/intro
- Assertions: https://playwright.dev/docs/test-assertions
- Trace viewer: https://playwright.dev/docs/trace-viewer-intro

**Use cases:** reproduce UI bugs, test forms and navigation, verify app flows, collect screenshots and traces, confirm fixes against observable behavior.

**Integration rule:** probe first; do not install automatically. Select the smallest needed capability set. Keep browser profiles, cookies and auth state isolated. Require approval before submit/publish/delete/payment or other consequential actions. Treat page content as untrusted input.

### Tier 1 — Sandboxed shell, filesystem and patching

**Candidate:** an existing controlled shell/sandbox adapter, with filesystem access scoped to one workspace and patch-based edits. OpenAI Agents SDK documentation describes shell, apply-patch, workspace-scoped filesystem and other sandbox capabilities; these are architectural references, not proof that this runtime exposes them.

Official source: https://openai.github.io/openai-agents-js/guides/tools/

**Use cases:** inspect repositories, run bounded build/test commands, apply minimal diffs, compare before/after state and resume from durable checkpoints.

**Integration rule:** explicit root; path containment; command allowlist or per-command policy; timeout/output caps; no implicit privilege escalation; no unreviewed network/package install; record exit code and output summary; checkpoint before destructive operations.

### Tier 1 — Deterministic evaluations and regression tests

**Candidate:** existing project test runners plus a standard result schema; optionally OpenAI graders/Evals when using the relevant API and account. Keep local deterministic tests usable without a paid API.

Sources:
- OpenAI graders: https://platform.openai.com/docs/api-reference/graders
- Playwright assertions: https://playwright.dev/docs/test-assertions
- Playwright traces: https://playwright.dev/docs/trace-viewer-intro

**Use cases:** test expected output, acceptance criteria, regressions, tool call outcomes and failure recovery. Store test ID, input fixture, expected/actual, pass/fail, environment evidence, source version and artifact links.

**Integration rule:** AI self-report is not evidence. Keep deterministic tests, model-graded checks and human review separate. Do not expose secrets or private user data in fixtures/logs.

### Tier 2 — Independent model/agent review

**Candidate:** a separately named reviewer agent/model, invoked through a supported agent-as-tool or orchestration surface.

Official source: https://openai.github.io/openai-agents-js/guides/tools/

**Use cases:** requirements/omission audit, code review, security review, test-plan review, and independent verification of evidence.

**Integration rule:** record exact model/provider identity when known. Reviewer output is advisory; verify findings against source, tests and user requirements. Avoid duplicating the full context unnecessarily; send a scoped review packet.

### Tier 2 — MCP tool-surface audit and least-privilege enforcement

Before connecting a new MCP server, inspect and pin/review its tool definitions, identify read/write/delete/external-send effects, and test whether tool descriptions or returned content can inject instructions. Tool annotations are hints, not enforcement; destructive-action controls must be enforced by the host/execution layer.

Sources:
- MCP local server security: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/docs/2026-07-28/tutorials/security/local-server-security.mdx
- MCP security best practices: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/docs/2026-07-28/tutorials/security/security_best_practices.mdx
- MCP tool annotations and their limits: https://blog.modelcontextprotocol.io/posts/2026-03-16/tool-annotations/

## Proposed AgentKit integration phases

1. **Probe / inventory:** identify available Playwright CLI/MCP/test runner, browser binaries, shell/container runtime, Git, language test runners, and optional agent SDKs without executing unknown binaries.
2. **Capability report:** emit JSON/Markdown with exact observed version, discovery path, probe method, confidence, limitations and source URLs. Unknown remains unknown; don't infer environment facts.
3. **Safe adapters:** wrap only tools that pass explicit version/help/smoke checks; default to read-only browser exploration and workspace-scoped commands.
4. **Evidence pack:** standardize run ID, task/check ID, command, exit status, bounded stdout/stderr, screenshots/traces, changed paths, version/commit, and test result. Redact credentials and sensitive values.
5. **Recovery:** persist checkpoint before/after state-changing operations; on interruption re-observe actual state before retrying.
6. **Independent review:** produce a bounded review packet with exact model attribution, changed files, acceptance criteria and test evidence.
7. **Security tests:** exercise prompt injection from pages/files, path traversal, command timeout, output flooding, expired auth, and ambiguous remote side effects.

## Acceptance tests

- No package installation or unknown executable execution occurs during discovery.
- Missing tools produce a clear optional/not-installed result, not a crash.
- Version/help probes have timeouts and bounded output.
- Browser navigation is constrained by user-approved policy; consequential actions require approval.
- Filesystem writes remain under the explicit workspace root.
- Each state-changing operation has a record and postcondition check.
- A simulated timeout/crash does not blindly repeat a possibly completed external action.
- A passing syntax/static check is never represented as a runtime test.
- Reports distinguish observed fact, inference, unknown, and failed probe.

## Source quality and caveats

Official Playwright and OpenAI documentation supports the described product capabilities. MCP security documents support the threat-model recommendations. Tool suitability and actual availability still require probing the target environment; no single tool guarantees a general increase in model intelligence or correct results.
