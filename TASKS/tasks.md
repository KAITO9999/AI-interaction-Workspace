# Tasks

## Workspace migration
- [x] Identify public GitHub destination and verify write access
- [x] Define a canonical AI workflow and short agent entry points
- [x] Separate project-specific material from global prompts
- [x] Replace GitLab-specific CI setup with GitHub Actions workflow
- [ ] Verify migrated links and tests on the exact commit
- [ ] Review public/private boundary and licensing before merge
- [ ] Decide whether GitLab remains the source of truth or becomes archival

## AgentKit
- [x] Python standard-library environment probe prototype
- [x] POSIX shell fallback and launcher
- [x] File listing pagination, line-range inspection, note fallback, explicit transcript ingestion, timer, capability table
- [ ] Run the full migrated test suite in GitHub Actions
- [ ] Smoke-test Python and shell fallback in target environments
- [ ] Review timeout, input, and filesystem edge cases
- [ ] Evaluate external tools before adding overlapping functionality

## Collaboration features
- [ ] Implement or explicitly reject automated work claims
- [ ] Design private transcript storage without exposing raw content publicly
- [ ] Define supported auto-start/reporting integration
