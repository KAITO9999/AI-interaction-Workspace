# ReForge Visuals — editing / handoff

Current status: **Candidate 3.24.2 packaged and all static checks pass; in-world validation remains active/pending.** The output add-on was produced locally at `/mnt/data/ReForge_Visuals-3.24.2.mcaddon`; it has not been committed as a binary to this public repository.

## Active work

### RFV-3242 — water tint and full static defect audit

- **Status:** static implementation complete; awaiting in-world validation
- **Actor:** AI
- **Work mode:** mixed (local archive inspection/tests plus official documentation and GitHub connector research)
- **Scope:** supplied `ReForge_Visuals-3.24.1.mcaddon`; patch candidate `3.24.2`.
- **Verified cause candidate:** in all six subpacks default water had `biome_water_color_contribution=0.04`; current biome `surface_color` values mostly specify blue `#4077E4`. Official documentation explains that this 0–1 factor controls how much biome surface color tints Vibrant Visuals water and gives 0.2 as an example: https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/watercustomization?view=minecraft-bedrock-stable.
- **Water routing:** 53 client biomes use `reforge_visuals:default_water`, 6 use `ocean_water`, 4 use `warm_ocean_water`, 2 use `river_water`; 7 have no explicit water identifier. Ocean/warm-ocean values remain 0.14, while default water is now 0.20 and river water 0.12.
- **Changes:** synchronized 71 legacy water colors; added `minecraft:swampland` to water-biome classification; corrected four medium-shadow `sampleWidth=1.25` values to 1.0 and corrected the label; stopped unresolved weather-fog key generation below Y=31 and reset its altitude transition latch.
- **Checks run:** full static audit on a clean extraction of the built archive reports 0 findings; 1,149 JSON parse/duplicate-key checks pass; 12 JS files pass Node syntax/import resolution; 513 fog IDs and 338 generated/static references checked; all six subpacks and wave schemas pass; 12 OGG and 9 PNG assets checked; 8 regression tests pass; ZIP CRC/path checks pass. Compared with the original archive, 1,172 existing members are byte-identical, 20 changed and only root `CHANGELOG.md` added; no original member removed.
- **Evidence:** local handoff report `/mnt/data/ReForge_Visuals-3.24.2-audit.txt`; regression suite `/mnt/data/reforge_audit/test_regressions.py`; full audit `/mnt/data/reforge_audit/full_audit.py`.
- **UNKNOWN:** no Bedrock in-world session, Content Log, screenshots, target-device or multiplayer performance test ran. The static change is a supported tuning choice but the rendered improvement cannot be guaranteed until checked in-game.
- **Next action / receiver:** test exact candidate 3.24.2 in a real world, with Vibrant Visuals both on/off, across default water, river, ocean, swamp/mangrove/lush-cave biomes and relevant subpack tiers; capture Content Log and visual evidence. Only then close the water-color issue.

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

- **ID / timestamp:** RFV-3242-static / 2026-10-15
- **Sender → receiver:** AI audit → next worker or user
- **Actor:** AI
- **Work mode:** mixed
- **Purpose / scope:** full static audit and release candidate check
- **Command(s):** `REFORGE_ROOT=/mnt/data/reforge_audit/release_extract python /mnt/data/reforge_audit/full_audit.py`; `REFORGE_SOURCE_ROOT=/mnt/data/reforge_audit/release_extract python -m unittest -v /mnt/data/reforge_audit/test_regressions.py`; archive ZIP integrity check
- **Result:** audit `issues_total: 0`; regression suite 8/8 OK; Node syntax/import checks pass for 12 JS files; ZIP CRC PASS and unsafe paths 0
- **Evidence path / URL:** `/mnt/data/ReForge_Visuals-3.24.2-audit.txt`
- **Classification:** FACT for static results; UNKNOWN for in-world appearance
- **Known limits / not checked:** runtime rendering, Content Log, target-device, multiplayer performance
- **Next action:** execute P1 in [PLAN.md](PLAN.md), record actual runtime version and visual/Content Log outcomes before considering the issue closed
