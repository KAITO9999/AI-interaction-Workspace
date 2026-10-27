# ReForge Visuals — editing / handoff

Current status: **Candidate 3.24.6 packaged; static ZIP/JSON/manifest/profile and mocked controller checks pass; in-world validation pending.** Binary assets remain local handoff artifacts and are not committed to this public repository.

## Active work

### RFV-3245 — Separate VV/non-VV water fog and tune color progression

- **Status:** static implementation complete; awaiting Bedrock runtime and visual validation
- **Actor:** AI
- **Work mode:** mixed (local archive build/inspection, official documentation, GitHub connector review and read-only Termux environment inspection). HyAI Lane was not used.
- **Scope:** input candidate ReForge_Visuals-3.24.4.mcaddon; output ReForge_Visuals-3.24.6.mcaddon.
- **Intent:** standard water distance 24; non-VV swamp 14; desert and mesa capped at 28; biome-specific short/middle/wide distances split between VV (graphicsMode=Deferred) and non-VV. Preserve water substance/opacity and the blue depth feel; apply only a slight blue-green surface/entry tint. Waves remain an accent.
- **Water/fog sweep:** parsed all 721 fog JSON files (452 weather, 180 time-progressive stages, 44 mode-specific water-distance profiles, 22 altitude, 22 biome, 1 other). Reviewed 246 distance.water configurations, 23 water volumetric-density configurations, 293 distance.air configurations, all 22 biome fogs, 71 client-biome water appearances and all 24 water settings across six subpacks.
- **Edits:** generated 44 VV/non-VV distance profiles; standardized 22 base biome water ranges to 24; generated 180 time-stage/range variants so time progression does not flatten the active distance; renamed active identifiers/labels to time_water_stage_* / reforge_time_water; retained old reforge_night_water only for one-time old-stack cleanup. VV depth volume is dynamically pushed only in VV mode.
- **Color/depth tuning:** nudged blue/cobalt client-biome palette slightly toward blue-green in 63 files without changing surface_opacity. Base/entry water fog colors get a restrained green bias. VV chlorophyll rose slightly while biome contribution and caustics settings stayed unchanged. All 22 biome fallback volumes and the central VV volume now use max_density=0.38, max_density_height=0, zero_density_height=72 with blue-biased scattering and red/green absorption stronger than blue absorption. This replaces the old 0.58 / Y=0..63 profile. The coordinates are absolute world Y, not depth relative to local water surface.
- **Wave treatment:** on active higher subpacks, wave depth/mix/pull/speed were reduced; disabled tiers remain disabled and water opacity was left unchanged.
- **Damage flash:** deliberately unchanged. The pack has no existing entity/render-controller/material override path. Global vanilla-mob hurt tint would require broad render-controller replacements with compatibility risk; official render-controller fields are per-controller, not a pack-wide tint switch.
- **Checks run:** size 4,997,541 bytes; SHA-256 c7198deba6878ba18afbb437ce0824f7b938ca12e124d36ccd4dff7a86061f48. All 21 static/mocked checks passed: ZIP CRC, duplicate paths, all 1,357 JSON parse, unique fog IDs, both manifests/dependencies at 3.24.6, base/variant ranges and references, surface opacity, water volume parameters, stale-name scan, Node syntax and mocked mode/biome/time transitions.
- **UNKNOWN / not run:** no Bedrock launch, Content Log, actual rendering/screenshot, target-device or multiplayer measurement. AgentKit audit-addon exists on Termux but could not run on this exact candidate because Termux cannot read the session's /mnt/data path; a local static audit was used instead. The artifact was not copied to Android /storage/emulated/0/Download; no transfer path was available. HyAI Lane was not used.
- **Next action / receiver:** import the exact 3.24.6 artifact into a real world and complete P1 in PLAN.md, testing VV and Simple. Check mode switches, underwater biome changes, entry transition and Content Log before declaring the visual issue fixed.

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


### Handoff record — RFV-3245 static candidate / 2026-10-21

- **Actor:** AI
- **Work mode:** mixed
- **Purpose / scope:** static validation and handoff for VV/non-VV water/fog rework.
- **Command(s):** python /tmp/build_reforge_3245.py; local archive checks; Node --check; Node mocked-controller test.
- **Result:** candidate written; 21 checks passed; complete fog inventory captured in the audit report.
- **Evidence:** ReForge_Visuals-3.24.6.mcaddon and ReForge_Visuals-3.24.6-audit.txt are local handoff artifacts. Artifact SHA-256 is recorded in RFV-3245.
- **Classification:** FACT for static checks; UNKNOWN for real Bedrock rendering.
- **Known limits:** no game runtime; no Termux copy of the exact artifact; no global mob hurt-color patch.
- **Next action:** run candidate in-world with VV and Simple, capture visual/Content Log evidence, then record the results.


### Follow-up — RFV-3246 / restore non-VV 32-block baseline

- Request: restore non-VV default water fog to 32 blocks.
- Change: WATER_DISTANCE_RANGES.nonvv.default 24 → 32 and water_distance_nonvv_default.json fog_end 24 → 32. VV default remains 24; swamp remains 14; desert/mesa remain 28. Existing time-stage 32-block variants are reused.
- Verification: ZIP CRC, duplicate paths, all 1,357 JSON parses, manifest versions 3.24.6, profile/default agreement and exceptions all pass.
- Artifact: ReForge_Visuals-3.24.6.mcaddon; SHA-256 9985a0619b1c8a29cfe7c78bffddfd40e5fc7389809da8711179622ee6e14a90.
- Runtime: not tested in Bedrock.



### RFV-410 — Sun/moon texture refresh and staged candle-color utility lights

- **Status:** candidate built; static checks passed; P4 runtime validation pending
- **Actor:** AI
- **Work mode:** mixed (local archive/asset work plus official/public source and GitHub/GitLab review)
- **Scope:** generated a local 4.1.0 candidate from the supplied 4.0.6 artifact; added only the Bedrock sky texture paths `textures/environment/sun.png`, `sun_vv.png`, and `moon_phases.png`; added four custom candle-color helper blocks and matching RP local-light settings; aligned BP/RP manifests, reciprocal dependency and changelog to 4.1.0.
- **Baseline evidence:** the local input reports BP/RP 4.0.6. The public GitHub project record describes a separate 3.24.6 line. This work does not overwrite or imply binary parity with that line. The reviewed GitLab plan concerns light shafts/cache work, not candles; GitHub remains the planning destination.
- **Implemented:** default 12×12 logical sun, matching VV variant, eight moon phases; separate 8×8 and 16×16 standalone size-test packs; four point-light blocks with level/color pairs 3/`#FFF0E8`, 6/`#F4A9C4`, 9/`#E95F79`, 12/`#FF302E`; visible hotbar icons for transparent helper blocks. Ordinary vanilla candle block states are not automatically remapped to these four IDs.
- **Targeted checks run:** `python build_reforge_410.py`; `python verify_reforge_410.py` in the temporary artifact workspace. These checks report 2,008 JSON parses with duplicate-key rejection and 12 JavaScript syntax checks; main and nested archive CRC/path checks; manifest/dependency/version alignment; unchanged external API versions; unchanged PBR subpack ordering; PNG dimensions/decoding; helper-block/icon/local-light agreement; exact path delta (five changed, eleven added, zero removed). Evidence output: local `ReForge_Visuals-4.1.0-build-report.json`.
- **Canonical audit not run:** the active artifact workspace did not include a co-located checkout for `TOOLS/AgentKit/agentkit_ext.py audit-addon`; targeted checks are supplementary and must not be described as the canonical audit.
- **Unknown / not run:** no Bedrock launch, in-world screen capture, Content Log test, or target-device check. Sun apparent scale, VV bloom, moon phase mapping, colored point-light appearance and block interaction remain unverified.
- **Next action / receiver:** run the canonical AgentKit add-on audit as specified in [P4 in PLAN.md](PLAN.md), then complete the real Bedrock-world checks. Test both graphics modes, compare 8×8/12×12/16×16 test packs one at a time, and verify helper-block placement/removal and all PBR tiers before claiming runtime completion.
