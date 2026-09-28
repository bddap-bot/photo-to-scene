# Mira-Scene feasibility and layout experiment

Decision target: can measured per-object layout improve the existing blockout,
and can generated meshes replace procedural detail builders on an 8 GB GPU?
This is an evaluation dependency, not a workflow dependency. No workflow code changes.

## Design and method (recorded before evaluation)

- Input: only the [public example photograph](../../examples/wilson-house/source.jpg), Library of Congress highsm.17640; [source and rights](../../examples/wilson-house/ATTRIBUTION.md).
- Baseline workflow: `adbd61ae79ce9be1e5839ebaa801fb4d86f6e9a9`.
- Evaluation dependency: Mira-Scene, with its exact source revision and checkpoint IDs to be recorded in the results.
- First settle checkpoint licenses and hardware feasibility for GeForce RTX 2080, 8192 MiB. Inspect the released pipeline and primary model documentation. Clone third-party source into isolated scratch; run any installation or inference through `run-untrusted`. Do not use bundled scene images.
- If a documented binding memory requirement exceeds this GPU and no supported fitting configuration is established, stop at box 1. Record that bound, distinguish it from measured peak memory, and leave inference runtime and candidate scores unmeasured.
- Otherwise run only the public input, retain per-instance transformations, and compare footprint, front and scale with the existing blockout using `tools/spatial-contract.py`. This gate checks contracts and observed invariants, not independent photo ground truth. Keep photo assessment distinct from contract conformity.
- Assess the plugged-in mesh backend separately: version, checkpoint licenses, memory including available FP8/offload modes, output formats and whether its transformations support footprint, front and aperture validation.
- Publish a results table. A demonstrated layout win opens a design issue for seeding `objects.json` without changing builders; failure of hardware feasibility or a measured loss closes #24. Do not claim a visual or spatial loss without inference.
