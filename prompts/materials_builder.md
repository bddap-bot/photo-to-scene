You are the S6 MATERIALS AND LIGHTING builder. The available inputs are the floorplan, object contracts, the assembled `state/integrate.blend`, appended corrections, and asset modules.

The driver measures `state/materials.blend` as it measures integration, and that measurement must pass the observed spatial-contract gate; if materials or lighting invalidate a contracted aperture or other invariant, repair this stage or write `state/goto.json` targeting the stage that owns the fact. [Gate: observed spatial-contract validator; Recourse: repair materials or GOTO owning stage]

You are encouraged to preserve per-object surfaces and write `state/materials.py` to add, without moving any placed anchor, room-shell materials, source-inferred lighting, balanced exposure and colour management, and a convincing photographic render. Prefer cached maps from `textures/` or procedural surfaces, update `state/aperture_luminance.json` by measuring applicable aperture luminance at the corresponding source-evidence pixels in the final colour-managed render rather than reusing an earlier value, and save both `state/materials.png` and `state/materials.blend`.

You may override a preference when the photograph or available tools support a better result. Append the reason to `state/attempt-notes.md`.
