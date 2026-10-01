# Shared-layout mesh comparison

Status: design registered before execution; blocked on mesh checkpoint access.
No A/B inference or scoring has run. No winning arm is named.
Tracked by [issue #25](https://github.com/bddap-bot/photo-to-scene/issues/25).

## Question and fixed inputs

Does editing a generated mesh improve spatial-contract conformity without reducing
photo critic quality, compared with the existing procedural detail builder?
Use only the [public Wilson House photograph](../../examples/wilson-house/source.jpg)
and its [public-domain attribution](../../examples/wilson-house/ATTRIBUTION.md).
The workflow design baseline is `251c087d7b043d733025a3602c0a8782a5531d73`.

Use the fixed object subset `gold_chair`, `round_table`, and `globe`, in that order,
in both arms. These cover upholstery, thin supports and curved geometry. Do not
replace a failed object with a more favorable one. Record failures in the common
denominator of three. Retain identical surrounding blockout context and camera.
No conclusion about the other objects follows from this subset.

## Shared front end

Run the evaluated layout configuration once for the subset. Save masks, canonical
geometry, generated meshes, camera calibration, per-object pose and scale, source
hash, checkpoint revisions and seeds before starting either arm. Both arms read
the same immutable files. Verify hashes and object IDs before each arm.

The evaluation dependency is Mira-Scene revision
`653cba6f4ca328797d44fd7357087573b873366a`; the exact checkpoint and runtime pins
are declared in the [prerequisite report](../mira-scene-layout/README.md).
Use its demonstrated FP32 CPU-offload configuration, groups of three, 10 sampling
steps and guidance 1. Fix the subset group seed to 42. Segmentation uses the
stored crop boxes and the evaluated segmentation substitute. This is a modified
configuration, not a claim about released-default quality.

Placement from the shared layout is the spatial authority. One ingestion path
converts axes and units, preserves IDs, and supplies the existing blockout and
contracts. Do not independently refit either arm to the photograph or replace
failed transforms with baseline placements. Keep semantic fronts, named regions
and apertures explicit; missing observations are failures. Invalid layout prevents
that object's paired run and remains in the reported denominator.

## Detail arms

- **A:** start from the generated per-object mesh. The existing builder model
  harness edits it in Blender using the object crop and zoomed-out photo context.
  The existing detail critic scores the result.
- **B:** reuse the existing procedural-builder detail stage, with the same shared
  placement, inventory, photo references, critic and attempt budget.

Use one detail implementation with a starting-asset choice, not a second detail
pipeline. Fix per-object seeds to 42, 43 and 44 respectively in both arms wherever
sampling is configurable; fix render seed 42. Record model revision and sampling
settings, and explicitly report any harness component that cannot enforce a seed.
Require local inference through the same builder/critic harness for both arms;
verify that configuration before execution. Do not invoke a paid API.

Integrate and materials remain unchanged and use identical settings. Freeze
contracts before comparing the arms. Do not weaken the gate to accommodate either
mesh source. Record any stage redirect that prevents a controlled paired result.

## Measurements and decision

Record each object's gate pass/fail and error categories, critic score, elapsed
wall time including load/edit/retry work, and sampled peak GPU process memory.
Report shared-front-end cost separately and arm A's mesh generation cost explicitly;
do not hide it inside the shared cost when comparing mesh-source costs. Capture
allocator peaks where available and state the memory sampling interval. Alternate
the first arm by object (A/B, B/A, A/B) and report contention; do not stop other work.

Read free GPU memory before every inference stage. Use sandboxed scratch execution
for all third-party installation and inference. Prefer CPU offload and serial
objects on the available 8 GB GPU. If the subset cannot run safely with the free
memory, defer execution rather than infer an idle-card hardware bound. Accept no
new checkpoint agreement and make no purchase as part of this experiment.

Render each integrated arm at the same photo camera. View both renders and the
assembled photo | A | B comparison before publishing any image. Publish per-object
rows and aggregate gate pass count, median critic, total wall time and maximum
object memory peak. Missing results remain missing, never zero-cost successes.

An arm wins only with more object gate passes and no lower median critic than the
other arm across the fixed subset; incomplete paired evidence yields no winner.
Ties or a gate/critic tradeoff yield no winner. Open a follow-up design issue only
for a demonstrated winning arm. Keep all issue checkboxes unchecked until their
stated evidence exists.

## Prerequisite status

The corrected prerequisite demonstrates layout execution at 6372 MiB process peak
and 2557.710 seconds for 90 instances. Its previous hardware rejection is withdrawn.
Its photo-alignment result does not establish mesh feasibility or contract success:
the candidate had 431 contract errors and no mesh backend was executed.

The prerequisite's mesh assessment reports that the default mesh checkpoint is
access-gated; the alternative backend's encoder and background remover rejected
anonymous downloads with approval required. No generated mesh is available from
that evaluation, and an 8 GB offload mesh trial has not completed. This is an access
block, not proof of a license prohibition or a GPU impossibility. Resume only with
authorized checkpoint access and a verified local builder/critic configuration.

| Required A/B evidence | Arm A | Arm B |
|---|---|---|
| Shared meshes and placement consumed | Pending | Pending |
| Spatial-contract result | Not measured | Not measured |
| Detail critic | Not measured | Not measured |
| Per-object wall time / peak GPU memory | Not measured | Not measured |
| Photo-camera render | Not produced | Not produced |

This table records the blocked state, not experimental results. The run, result
appendix and side-by-side image remain outstanding.
