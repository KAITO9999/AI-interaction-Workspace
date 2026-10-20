# Existing-tool replacement and environment probe policy

- Diagnostic discovery and practical fallback execution are separate tools.
- If a standard command exists, do not shadow, partially emulate, or replace it. Fallback is eligible only when the command is absent or explicitly selected by the user.
- Probe candidate executables and capabilities without running arbitrary candidates. Any active test must be bounded, read-only where possible, and clearly identify side effects.
- One write-permission test may attempt a designated path. On denial, report the exact error to stderr/log and stop trying alternate paths unless the user explicitly configured another path.
- Never install packages, elevate privileges, bypass agent/OS policies, access credentials, or claim a fallback is equivalent to syscall tracing when it only records process metadata.
- Test real substitution behavior in CI using harmless fixtures. Report what was tested, the environment, skipped cases, and limitations.
- Route probing is separate from the practical downloader; a successful HEAD or range request does not prove a full download will succeed.
