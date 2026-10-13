# ReForge Visuals — editing / handoff

Current status: **No active gameplay-code edit.** Static review has completed; runtime validation remains planned and must not be described as active work or as passed.

## Active work

- None currently active.
- When a runtime test, investigation or bug fix starts, move that item from [PLAN.md](PLAN.md) here before implementation/testing and complete the fields below.
- Bug fixes, reproduction attempts, regression investigations and refactors all belong here while active, not only new features.

## Active item template

### Short ID — title

- **Status:** investigating / implementing / validating / blocked
- **Actor:** AI / human / both; split path ownership if needed
- **Work mode:** online / offline / mixed, based on the actual route used
- **Scope:** intended result and affected paths
- **Reproduction / inputs:** artifact, runtime, steps and expected versus actual behavior
- **Hypothesis:** label as INTERPRETATION until verified
- **Edits:** paths and rationale
- **Checks run:** exact command, working directory, exit code/status and observed result
- **Unrun checks / unknowns:** explicit
- **Next action / receiver:** unambiguous continuation step

## Handoff inbox — command output and findings

Append one record per related command set so another AI/person can consume results without reopening every large file or relying on chat history. Keep each record public-safe and concise.

### Handoff record template

- **ID / timestamp:**
- **Sender → receiver:**
- **Actor:** AI / human
- **Work mode:** online / offline / mixed
- **Purpose / scope:**
- **Command(s) and working directory:**
- **Result:** exit code/status and exact relevant stdout/stderr excerpt; state explicitly if output was truncated
- **Evidence path / URL:** durable artifact when available; never invent one
- **Classification:** FACT / INTERPRETATION / DECISION / UNKNOWN
- **Known limits / not checked:**
- **Next action:**

## Handoff records

No active handoff records. Add the first record using the template above; do not add empty placeholder entries that could be mistaken for evidence.
