# Commit rules

- Keep each commit to one coherent change.
- Use clear messages such as docs: repair internal links or fix: handle empty probe root.
- Do not describe unfinished work as complete.
- Avoid unrelated generated output and mass formatting.
- Keep the diff reviewable and recoverable.
- For a pull request, append a public-safe entry to LOGS/change-ledger.jsonl using TOOLS/AgentKit/agentkit_ext.py record-change.
- Each record must explicitly identify actor (ai or human) and work mode (online, offline or mixed), plus summary and paths.
- Treat the ledger as append-only. Never rewrite earlier records to make the current state look cleaner.
- Review the entry for private text and machine-local paths before committing; do not log prompts, credentials, private URLs or personal data.
- CI validates actor/mode fields and requires the new entries to cover every modified path in the PR.
