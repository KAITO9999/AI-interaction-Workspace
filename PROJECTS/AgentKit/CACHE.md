# AgentKit — cache

## Verified baseline

- **2026-10-21:** The repository's [global task list](../../TASKS/tasks.md) records core environment probing, PATH inventory, TypeScript wrapper, static add-on audit, provenance and CI checks as implemented, while Termux/other target smoke tests and real `tsconfig.json` compilation remain pending.
- **2026-10-21:** [AgentKit README](../../TOOLS/AgentKit/README.md) documents core/extension CLI, resolver fallbacks and current safety/compatibility boundaries.
- **2026-10-21:** The open PR search returned [PR #10](https://github.com/KAITO9999/AI-interaction-Workspace/pull/10) and [PR #11](https://github.com/KAITO9999/AI-interaction-Workspace/pull/11). Their current merge state must be rechecked before implementation; presence in a PR does not mean changes are on `main`.
- **2026-10-21:** No open issues were returned by the repository-scoped issue search at plan creation time. This is a snapshot, not a guarantee that no issues exist now.
- **2026-10-21:** The local MCP bridge in the current implementation context is a payload preparation/relay helper, not a generic authenticated MCP client. End-to-end connector behavior is therefore still a separate integration task.
- **2026-10-21:** The current test runner behavior documented in the working context includes substring-based skip selection; file/entry-point-based selection remains a planned change.
- **2026-10-21:** Existing multi-profile, language-audit, virtual-edit, bundle and route-probe work has automated checks in its development branch/CI context, but those results must not be treated as proof that all such code is already merged into the default branch or validated on every target device.

## Decisions

- Use [PLAN.md](PLAN.md) as the sole detailed AgentKit roadmap. The global task list and repository map link to it.
- Sequence work by dependencies and evidence, not guessed calendar dates.
- Treat static source/manifest analysis, CI, host smoke tests and target-runtime tests as different evidence classes.
- Generic language/API signals remain heuristics unless backed by a parser/compiler/runtime result.
- Never claim generic MCP connectivity, GPU support, or precise runtime estimation solely from local extraction, metadata or illustrative profiles.

## Completed items moved from PLAN

No roadmap item has been moved here as completed by this plan-creation change. Existing completed repository work remains documented in the global task list, source files, PRs and their observed CI evidence; do not infer merge state from that history.
