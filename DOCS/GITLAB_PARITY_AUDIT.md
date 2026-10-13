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
| CACHE/ReForge_Visuals-Implementation-Cache.txt | PROJECTS/ReForge-Visuals/CACHE.md | Relocated and refreshed for 3.24.1 |
| TASKS/ReForge_Visuals-Implementation-Plan.md | PROJECTS/ReForge-Visuals/PLAN.md | Relocated; stale/low-benefit approaches removed and completed static checks moved to cache |
| Project-specific procedures and active task / handoff records | PROJECTS/ReForge-Visuals/WORK_MODELS.md and IN_PROGRESS.md; format in DOCS/PROJECT_WORKFLOW.md | Standardized in GitHub |
| Prompt / agent entrypoints | AGENTS.md, CLAUDE.md, AI_WORKFLOW.md and PROMPTS/README.md | Grouped by purpose; canonical workflow not duplicated |
| TASKS/tasks.md | TASKS/tasks.md | Preserved and refreshed |
| STATE/workspace_state.md | STATE/workspace_state.md | Preserved and refreshed |
| RULES/COMMIT_RULES.md | RULES/COMMIT_RULES.md | Preserved and extended |
| RULES/CONVERSATION_RULES.md | Same path | Preserved |
| RULES/FILE_CHANGE_RULES.md | Same path | Preserved |
| RULES/PUBLIC_DATA_RULES.md | Same path | Preserved |
| RULES/SCOPE_AND_REPORT_RULES.md | Same path | Preserved and linked to project format |
| RULES/TRUTH_AND_ERROR_RULES.md | Same path | Preserved |
| RULES/WORK_CLAIM_RULES.md | Same path | Preserved and linked to active project lifecycle |
| Empty .gitkeep placeholders under DOCS, LOGS, SRC | Omitted where populated structure no longer needs them | Intentional |
| Private workspace URL in historical material | Not copied to public repository | Intentional privacy boundary |

## Comparison outcome

The current GitLab tree was re-read and mapped to the migrated public structure. At the file-tree level, every substantive public source item has a destination or an explicit transformation above. Empty placeholders and a private-workspace reference are intentional omissions.

This is a tree/content-purpose comparison, not a claim that GitHub and GitLab are byte-identical or automatically synchronized. GitLab is unchanged. Changes on GitHub must be backported deliberately if both repositories still need updates.

The project-format and prompt-routing additions describe the current GitHub workflow only; they do not imply that GitLab has received those changes. This audit records semantic mapping, not automatic synchronization.