# Public / private information boundary

This repository is public. If publication permission is unclear, do not publish the information.

## Keep private or out of this repository

- Raw user conversations and private prompts
- Personal data, contact details, account identifiers, or third-party confidential information
- API keys, tokens, passwords, private keys, and authentication material
- Non-public source files, private attachments, and private workspace URLs
- Unreviewed investigation notes that could expose private context or be mistaken for verified facts

Secrets belong in an appropriate secret manager or repository secret store, never in tracked files.

## Suitable for public use after review

- Licensed source code and reusable tools
- Public documentation and collaboration rules
- Sanitized reproduction steps and tests
- Public technical findings with source links and confidence labels
- State/task summaries that do not expose private context

## Moving material into this repository

1. Identify the source and its publication status.
2. Remove secrets, personal data, private links, and unnecessary raw context.
3. Separate fact from interpretation and unresolved assumptions.
4. Keep only context needed by a public contributor.
5. Verify the final diff before publishing.

When uncertain, omit the material and record the gap as `UNKNOWN`.
