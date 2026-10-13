# GitLab to GitHub source parity audit

Reviewed: 2026-10-13  
GitLab source: ai-work-space2/ai-integration-workspace (project ID 87336047, default branch main)  
GitHub destination: KAITO9999/AI-interaction-Workspace (main)

## Tree-level mapping

| GitLab source item | GitHub destination / treatment | Result |
|---|---|---|
| README.md | README.md, rewritten as GitHub entry point | Adapted |
| .gitlab-ci.yml | .github/workflows/agentkit-tests.yml | Replaced with GitHub Actions |
| DOCS/SPACE_CLASSIFICATION.md | Same path | Preserved |
| DOCS/gitlab_operations.md | DOCS/GITHUB_WORKFLOW.md | Platform-specific workflow rewritten |
| CACHE/ReForge_Visuals-Implementation-Cache.txt | PROJECTS/ReForge-Visuals/IMPLEMENTATION_CACHE.md | Relocated and updated for 3.24.1 |
| TASKS/ReForge_Visuals-Implementation-Plan.md | PROJECTS/ReForge-Visuals/IMPLEMENTATION_PLAN.md | Relocated; stale and low-benefit approaches removed |
| TASKS/tasks.md | TASKS/tasks.md | Preserved and refreshed |
| STATE/workspace_state.md | STATE/workspace_state.md | Preserved and refreshed |
| RULES/COMMIT_RULES.md | RULES/COMMIT_RULES.md | Preserved and extended |
| RULES/CONVERSATION_RULES.md | Same path | Preserved |
| RULES/FILE_CHANGE_RULES.md | Same path | Preserved |
| RULES/PUBLIC_DATA_RULES.md | Same path | Preserved |
| RULES/SCOPE_AND_REPORT_RULES.md | Same path | Preserved |
| RULES/TRUTH_AND_ERROR_RULES.md | Same path | Preserved |
| RULES/WORK_CLAIM_RULES.md | Same path | Preserved and extended |
| Empty .gitkeep placeholders under DOCS, LOGS, SRC | Omitted where populated structure no longer needs them | Intentional |
| Private workspace URL in historical material | Not copied to public repository | Intentional privacy boundary |

## Comparison outcome

The current GitLab tree was re-read and mapped to the migrated public structure. At the file-tree level, every substantive public source item has a destination or an explicit transformation above. Empty placeholders and a private-workspace reference are intentional omissions.

This is a tree/content-purpose comparison, not a claim that GitHub and GitLab are byte-identical or automatically synchronized. GitLab is unchanged. Changes on GitHub must be backported deliberately if both repositories still need updates.

## Added workflow capabilities

- AgentKit now provides actual PATH executable inventory without running discovered commands.
- A TypeScript wrapper uses an existing tsc for compile and no-emit checking without silently installing dependencies.
- Change records identify actor type (AI/human), work mode (online/offline/mixed) and affected paths.
- Pull-request CI checks append-only provenance and coverage of changed paths.
- A static mcaddon/mcpack audit checks archive structure, JSON, manifests and optional JavaScript syntax.
- ReForge planning/cache documents were reconciled with the supplied 3.24.1 package. Static results are not runtime test results.
