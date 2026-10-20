# Virtual editing and ten-slot policy

- Provide ten isolated scratch slots for parallel review or staged edits.
- Stage changes into overlays; original files remain unchanged until explicit apply.
- Allow inspection and static analysis of staged/partially edited code without requiring a syntactically complete project.
- Every overlay records source path, source hash, timestamp, slot, and diff/provenance.
- Applying is opt-in, requires explicit confirmation, and must fail if the original hash changed since staging.
- Static checks should label parse errors as expected-in-progress when a slot is marked incomplete; do not silently classify them as production defects.
- Avoid merging overlays implicitly. Cross-slot compare/merge must show conflicts and require confirmation.
- Never claim a staged overlay is applied to the original repository.
