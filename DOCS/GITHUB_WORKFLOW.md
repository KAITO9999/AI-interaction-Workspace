# GitHub workflow

## Normal change

1. Create a focused branch from `main`.
2. Inspect the existing files and open work before editing.
3. Make a coherent change with relative links for in-repository references.
4. Run relevant tests and the local-link checker.
5. Open a Pull Request with scope, evidence, test results, and remaining uncertainty.
6. Merge only after review and required checks.

Avoid direct large changes to `main`. Do not claim a workflow passed if no run or job result is available.

## CI

The repository uses GitHub Actions for AgentKit checks and Markdown-link validation. External URL availability is not guaranteed by the local-link check; review external links when changing them.

## GitLab source

The former public GitLab workspace is an historical source. Do not maintain two divergent copies silently. When backporting or comparing changes, identify the exact source branch/commit and describe the direction of synchronization.
