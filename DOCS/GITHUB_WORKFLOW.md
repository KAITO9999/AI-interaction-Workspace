# GitHub workflow

## Normal change

1. Create a focused branch from `main`.
2. Follow the mandatory reread route in [AI_WORKFLOW.md](../AI_WORKFLOW.md) and check the current work scope before editing.
3. Inspect existing files and active work; for a specific project, follow the [four-file project format](PROJECT_WORKFLOW.md) and record active implementation/bug fixes in `IN_PROGRESS.md`.
4. Make a coherent change with relative links for in-repository references.
5. Run relevant tests and the repository-wide local-link checker.
6. Open a Pull Request with scope, evidence, test results, provenance and remaining uncertainty.
7. Merge only after review and required checks.

Use the [prompt/use-case index](../PROMPTS/README.md) to select procedures. Avoid copying prompts or keeping duplicate task/cache routes. Do not claim a workflow passed if no run or job result is available.

## CI

The repository uses GitHub Actions for AgentKit checks, provenance enforcement and Markdown-link validation. The local-link check verifies repository paths, not external URL availability; review external links when changing them. A configured CI job does not count as passed until its actual result is observed.

## GitLab source

The former public GitLab workspace is a historical source. Do not maintain two divergent copies silently. When backporting or comparing changes, identify the exact source branch/commit and describe the direction of synchronization.