# ReForge Visuals — cache

Status: **3.24.6 candidate generated; targeted static checks passed; in-world validation pending.**  
Current candidate: `ReForge_Visuals-3.24.6.mcaddon`  
Last reviewed: 2026-10-21

## Historical 3.24.2 evidence (preserved for context)

## Verified facts

- BP and RP header/module versions and their internal dependency versions are 3.24.2 in the generated candidate.
- Minimum engine version remains 1.26.0; `@minecraft/server` 2.9.0 and `@minecraft/server-ui` 2.1.0 remain unchanged.
- The candidate contains 1,193 files: 1,149 JSON files, 12 BP JavaScript files and the added root `CHANGELOG.md` plus existing pack assets.
- `BP/scripts/performance_engine.js` supplies the shared scheduler/queue and remains the primary work-budget gate.
- Current per-biome water definitions assign separate schemas: `reforge_visuals:default_water` (53 client biomes), `ocean_water` (6), `warm_ocean_water` (4), `river_water` (2); 7 definitions have no explicit `water_identifier`.
- Microsoft documents `biome_water_color_contribution` as a 0–1 factor controlling how much `surface_color` from client-biome JSON contributes to Vibrant Visuals water. The official example uses 0.2: [Water Effects](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/watercustomization?view=minecraft-bedrock-stable).
- Client-biome files are the preferred per-biome format; legacy `biomes_client.json` is still loaded for custom content: [Client Biomes overview](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/clientbiomesreference/examples/clientbiomesoverview?view=minecraft-bedrock-stable).

## Completed items moved from PLAN

| Date | Item moved from plan | Result / evidence |
|---|---|---|
| 2026-10-13 | Inspect original 3.24.1 artifact and verify BP/RP versions and dependencies | PASS; manifest/UUID/version pairing verified |
| 2026-10-13 | Check original archive integrity and paths | PASS; ZIP CRC and unsafe-path scan |
| 2026-10-13 | Parse JSON files | PASS; 1,149 / 1,149 |
| 2026-10-13 | Syntax-check JavaScript files | PASS; 12 / 12 with Node |
| 2026-10-13 | Remove stale low-benefit raycast / dummy-entity / N-way approaches from planning | Planning change complete; no gameplay code removed for that old plan |
| 2026-10-15 | Increase ordinary and river water biome-tint contribution | Default water 0.04 → 0.20 and river 0.05 → 0.12 in all six subpacks; eight regression tests pass |
| 2026-10-15 | Reconcile legacy and current biome water colors | 71 legacy water colors synchronized to their current `*.client_biome.json` colors; fog directives and legacy transparency preserved |
| 2026-10-15 | Fix water schema, swamp classification and low-altitude fog routing | `sampleWidth=1.25` corrected to documented maximum 1.0; `minecraft:swampland` classification added; unresolved weather-fog keys below Y=31 suppressed |
| 2026-10-15 | Full static audit and candidate package verification | 1,149 JSON parsed with duplicate-key rejection; 12 JS syntax/import checked; 513 fog IDs and 338 script fog references checked; 9 script sound IDs, 10 sound events, 12 OGG and 9 PNG assets checked; six subpacks / four water definitions each; 0 audit issues; ZIP CRC/path check PASS |

## 3.24.5 water/fog candidate — static evidence only

- Candidate artifact SHA-256: c7198deba6878ba18afbb437ce0824f7b938ca12e124d36ccd4dff7a86061f48; 4,997,537 bytes.
- Static counts: 1,401 archive entries; 1,357 JSON files parsed; 721 fog JSONs; no duplicate archive paths, duplicate fog IDs or JSON errors.
- Full fog inventory: 246 distance.water configs (22 biome base + 44 mode-specific + 180 time-stage/range variants); 23 water volumetric-density configs (22 biome fallback + central VV profile); 293 distance.air configs. All references for 44 mode profiles and 180 time/range variants resolve.
- Static checks passed: both manifests and counterpart dependencies align to 3.24.5; 22 base water distance files at 24; 24 water settings across six subpacks reviewed; 63 surface colors adjusted without opacity change; 22 biome water-volume settings and the VV profile match the lower-density blue-biased gradient; Node syntax and mocked mode/biome/time tests pass.
- Decisions: non-VV swamp 14; desert/mesa capped at 28; mode-specific distance profiles; time progression named time_water_stage_*; subtle blue-green entry/surface tint; waves kept as accent. Density progression still uses absolute world Y, not depth from the local water surface.
- Runtime remains unknown: no Bedrock render, Content Log, target-device, multiplayer or performance test. No global hurt-tint patch was made because the global vanilla override would be broad and compatibility-prone.
- Audit report ReForge_Visuals-3.24.5-audit.txt is a local handoff artifact; not hosted in this repository.

## Historical 3.24.2 — water tint decision

- `RP/subpacks/*/water/water.json`: `biome_water_color_contribution` 0.04 → 0.20.
- `RP/subpacks/*/water/river_water.json`: 0.05 → 0.12.
- Ocean and warm-ocean definitions remain 0.14 because they use separate identifiers and settings; they were not silently given the default-water tuning.
- `RP/biomes_client.json` legacy colors are synchronized with 71 current per-biome definitions, while legacy fog directives and water transparency remain unchanged.
- The stronger mix is a supported tuning choice, not a promise of an exact rendered appearance. Validate it in-world before declaring the visual issue completely closed.

## Historical 3.24.2 — other verified corrections

- Added `minecraft:swampland` to `BP/scripts/biome_cache_engine.js` water-biome classification.
- Corrected all four `sampleWidth=1.25` values in `medium_shadow_24/water/*.json` to 1.0 and matched the pack's subpack label.
- Prevented `fog_controller.js` from emitting per-altitude weather-fog IDs in Y ≤ 30, where standalone resources do not exist; cleared the high-altitude snow transition latch when switching into that band. Underground fog remains authoritative.
- The original archive's 1,172 unchanged members are byte-identical; 20 existing members changed and only root `CHANGELOG.md` was added. No original archive member was removed.

## Historical 3.24.2 — static verification results

- Release archive CRC: PASS; unsafe paths: 0.
- BP/RP manifest consistency: PASS; both report 3.24.2.
- JSON parse / duplicate keys: 1,149 / 1,149 PASS.
- Node syntax and local JS import resolution: 12 scripts PASS; unresolved relative imports: 0.
- Client biome definitions: 72; water surface colors: 71; current/legacy color mismatch: 0.
- Fog identifiers: 513; generated/static references checked: 338; unresolved references: 0.
- Lighting identifiers: 16; cubemap: 1; color grading: 1; particle identifiers: 2.
- Water subpacks: 6; definitions per subpack: 4; schema-range issues: 0.
- Script sound identifiers checked: 9; sounds.json events: 10; OGG assets checked: 12; PNG assets checked: 9.
- Regression suite: 8 / 8 passed.
- Full static audit issue count: 0.
- Audit report: `ReForge_Visuals-3.24.2-audit.txt` was generated for the local handoff; it is not a repository-hosted artifact.

## Historical 3.24.2 — UNKNOWN at that time

- Water appearance in a real Bedrock world with Vibrant Visuals both enabled and disabled.
- Add-on loading and Content Log output on the target Bedrock build/device.
- Sound/fog behavior in-world, multiplayer load, device compatibility and tick/frame cost.
- Exact visual difference produced by the new water contribution values.
- Static analysis cannot prove all runtime API behavior or that a reported in-world visual issue is fully resolved.

See [PLAN.md](PLAN.md) for the remaining runtime validation.


## 3.24.6 follow-up — restore non-VV 32 baseline

- Change: non-VV default profile restored from 24 to 32 blocks in controller and default fog JSON. VV default stays 24; swamp remains 14; desert/mesa remain 28. Existing time-stage 32 variants reused.
- Static checks: ZIP CRC, duplicate paths, 1,357 JSON parses, manifest 3.24.6, profile and JSON agreement passed.
- Artifact SHA-256: 9985a0619b1c8a29cfe7c78bffddfd40e5fc7389809da8711179622ee6e14a90.
- Runtime not tested.
