# ReForge Visuals — work models

Status: reusable procedures; the active 4.1.0 candidate and its runtime-validation handoff are tracked in IN_PROGRESS.md.

## Model A — source-first, evidence-gated review and optimization

**Use when:** reviewing a release, investigating a defect, or considering an optimization.

**Inputs:** exact `.mcaddon` artifact, target Bedrock/Script API version, current project records, and a concrete question or reproducible observation.

**Procedure:**
1. Identify the artifact/version; inspect manifests and archive structure.
2. Run `TOOLS/AgentKit/agentkit_ext.py audit-addon` as the canonical first static package audit; do not maintain a parallel equivalent audit route. If the artifact and checkout/tool are not co-located in the active environment, record the canonical audit as NOT RUN and label any targeted checks as supplementary—not as an equivalent AgentKit result.
3. Investigate reported concerns at the relevant source and reproduce the specific issue before proposing a fix.
4. Keep `performance_engine.js` as the primary scheduler/queue/budget path. Do not add a second scheduler or duplicate scan path without evidence.
5. For performance work, record suspected hot path, call frequency, expected visual/gameplay effect, measurement setup, and rollback point before editing.
6. Verify runtime/API changes in a real Bedrock world and inspect Content Log. Measure target-device and multiplayer performance when that is the claim.
7. Record exact commands/results and the next action in `IN_PROGRESS.md`; on completion, move the result to `CACHE.md`.

**Acceptance:** static checks (archive paths/CRC, JSON, JavaScript syntax, manifest consistency as applicable) are recorded separately from runtime checks. Performance claims require a stated test setup and before/after evidence.

**Limits:** static validation alone does not prove runtime behavior, visual quality, multiplayer safety or performance improvement.

## Model B — bug fix / regression

1. Add an `IN_PROGRESS.md` entry before editing, including for seemingly small bug fixes, reproduction attempts, regression investigations and refactors.
2. Capture reproduction steps, expected/actual behavior, artifact/runtime version and affected paths.
3. Label unproven causes as `INTERPRETATION`; update the label only when evidence supports it.
4. Make the smallest scoped correction and add/identify a regression check where possible.
5. Run independent checks and report failures exactly; do not turn missing runtime testing into a pass.
6. Only move the item from `PLAN.md` into the completed section of `CACHE.md` when its completion criteria are met.

## Model C — texture atlas + local-light block extension

**Use when:** adding sky textures or color/brightness variants for custom light-emitting blocks.

1. Verify exact asset paths and atlas dimensions from the matching Bedrock sample/resource version before writing replacement textures.
2. Preserve unrelated sky, cloud, atmosphere and lighting JSON so that texture changes remain composable with other packs.
3. Use nearest-neighbor pixel-art construction at the engine's expected dimensions; validate alpha, layout, phase order and PNG dimensions by script.
4. For per-state lighting that cannot be represented by the current JSON key, prefer distinct custom block identifiers with explicit light emission and local-light color entries. Do not claim vanilla block states are dynamically recolored unless a runtime path actually supports it.
5. Keep new helper-block IDs isolated from `HAND_LIGHT_PREFIX` / the existing dynamic source cleanup set; document exact IDs and practical placement method.
6. Run the canonical AgentKit add-on audit when available, then record archive integrity, JSON duplicate-key/schema-shape checks, manifest/dependency alignment and targeted asset tests. If the canonical CLI is unavailable, state that limit explicitly. Real Bedrock/VV rendering and Content Log remain separate acceptance gates.

**Acceptance:** the pack contains only the intended sun/moon overrides and scoped helper blocks; existing subpacks, manifest UUIDs, dependency versions, and unrelated lighting behavior remain unchanged.

**Limits:** local-light configuration is keyed by block identifier; static validation cannot prove that sky textures render at the intended apparent size or that point-light shadows/colors look correct on every device.

## Duplicate-route exclusions

- Use AgentKit `audit-addon` as the first static package audit; add another route only for a distinct, demonstrated need.
- Use `performance_engine.js` as the shared scheduler/budget gate; no duplicate queue without measurements.
- The project's only record files are `WORK_MODELS.md`, `PLAN.md`, `CACHE.md` and `IN_PROGRESS.md`. Global prompts link here rather than copying these procedures.
