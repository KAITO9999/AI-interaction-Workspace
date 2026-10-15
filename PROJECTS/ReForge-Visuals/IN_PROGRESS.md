# ReForge Visuals — editing / handoff

Current status: **Active audit and patch preparation for ReForge Visuals 3.24.2.** No Bedrock runtime has been run in this environment.

## Active work

### RFV-3242 — water tint and full static defect audit

- **Status:** investigating / implementing / validating
- **Actor:** AI
- **Work mode:** mixed (local archive inspection plus official documentation / GitHub connector research)
- **Scope:** supplied `ReForge_Visuals-3.24.1.mcaddon`; focus on per-biome water tint, then full static integrity/reference/syntax audit. Intended patch version: 3.24.2.
- **Reproduction / inputs:** static inspection found `RP/subpacks/*/water/water.json` sets `biome_water_color_contribution` to `0.04` in all six subpacks. Most ordinary biomes set `surface_color` to `#4077E4`. Official Water Effects docs state the contribution controls how much that per-biome color mixes into Vibrant Visuals water and show `0.2` as an example. This is a grounded cause candidate; visual effect still needs in-world verification.
- **Hypothesis:** INTERPRETATION — the 4% contribution makes blue biome tint too weak in Vibrant Visuals; old root `RP/biomes_client.json` may also be stale/conflicting and needs comparison with modern per-biome definitions.
- **Edits:** not applied to the release archive yet; first establish failing static regression checks, then patch source copy and package a new version.
- **Checks run so far:** ZIP CRC/path validation passed for 1,249 entries; extraction contained BP and RP directly. All JSON/JS and cross-resource references remain under full audit.
- **Unrun checks / unknowns:** in-world water appearance, target Bedrock version loading, Content Log, performance and platform-specific packaging.
- **Next action / receiver:** finish the identifier/schema sweep, write regression checks, patch water configs and any proven static defects, then validate and package 3.24.2.

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

No separate command handoff has been recorded yet. The active item above is the current task state; append distinct records only for results that materially help another worker continue.
