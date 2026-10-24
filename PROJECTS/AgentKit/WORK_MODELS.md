# AgentKit — work models

Status: smartphone profile preflight implementation active; runtime device testing remains a separate follow-up.

## Model A — environment helper or compatibility preflight

**Use when:** adding a deterministic, standard-library-only helper to inspect an environment or decide whether a target is eligible for a bounded test.

**Procedure:**
1. Fetch the relevant repository source through the GitHub connector first; verify the ref/commit before using it.
2. If connector content cannot be materialized in the execution environment, copy only the required source files and tests into the environment. For bulk retrieval, try Git once with a bounded timeout; stop that route on its first error.
3. Inspect current CLI behavior and tests before changing it. Keep safety-sensitive actions opt-in and do not infer runtime success from static inspection.
4. Add tests for positive, negative, and unknown/unresolved configuration.
5. Run syntax checks and unit tests; use CI when local repository retrieval is unavailable.
6. Record provenance in the change ledger and distinguish static preflight from a real device/emulator run.

**Acceptance:** expected decisions are covered by tests; unknown configuration is not silently treated as compatible; output explains what was and was not tested.

## Model B — smartphone profile matrix

1. Use explicit memory budgets (4/8/12/16 GB) and document them as configurable test budgets, not exact device specifications.
2. Apply Android-version gates only where a target version is defined or explicitly requested.
3. Reject a profile when a known minSdkVersion exceeds the target API. Block for review when the minimum SDK cannot be determined.
4. Do not invent CPU/GPU/core/clock/thermal values absent measured or user-specified evidence.
5. Require emulator or physical-device evidence before claiming runtime compatibility or performance.

## Limits

The profile preflight does not emulate devices, install packages, run the app, or measure memory/CPU/GPU/frame rate, battery, or thermals. The canonical implementation and user instructions live in [AgentKit](../../TOOLS/AgentKit/README.md) and [smartphone test profiles](../../TOOLS/AgentKit/MOBILE_TESTING.md).
## Model C — Python-first workflow tooling and context-bounded inspection

**Use when:** adding reusable read-only repository checks, standard-library inspection tools, or tools intended to reduce agent context consumption.

**Procedure:**
1. Verify upstream command behavior and invoke the official command when present.
2. Use Python standard-library implementations only where they can safely provide the named behavior; otherwise report unavailable.
3. Make weaker fallbacks explicit in machine-readable output (for example, `py_compile` is syntax-only, not Ruff; `sh -n` is syntax-only, not ShellCheck).
4. Apply strict path containment, bounded reads/output, timeouts, and read-only defaults. Avoid arbitrary SQL, shell interpolation, automatic installs, and file execution.
5. Add boundary tests for path traversal, symlinks, byte/line budgets, invalid inputs, missing tools, and read-only behavior.
6. Keep existing core/extension commands separate unless a later measured change proves consolidation improves compatibility without breaking the CLI.

**Acceptance:** each check reports its actual tool and capability; unavailable or partial checks cannot be reported as full passes; tests and CI cover the new behavior.
