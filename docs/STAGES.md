# Pipeline stages and contracts

The pipeline treats reconstruction as a sequence of durable, reviewable contracts. Each builder starts with the reference image and the smallest relevant on-disk state. A fresh critic scores its result. Builders never communicate hidden scene state to later stages.

## Coordinate and file contracts

All measurements use metres. The room coordinate origin is a floor corner, with `x` along the far wall, `y` toward the camera, and `z` upward.

`floorplan.json` describes the room polygon, wall heights, openings, fixed architectural features, camera pose and optics, a scale anchor, and the derivation of inferred dimensions.

`objects.json` is an exhaustive array of visible objects plus any structure the scene needs that the photograph does not show. Each entry carries a stable identifier, proposed and object-reviewed labels, the reason for any confirmation or correction, a source-image crop rectangle, room-space bounding box, contact relationship, material observation, confidence, and a source-grounded spatial contract. The contract fixes one local-to-room frame, facing, footprint, confidence-aware semantic regions, relationships, ownership, and applicable aperture visibility. An entry for unshown structure, such as a room closure outside the frame, is marked `inferred` and carries no crop rectangle; the declaration gate requires a crop rectangle on every other entry and rejects one on an inferred entry.

`assets/<id>.py` exposes `build(entry, collection=None)`. It creates recognisable geometry and material in one normalized local frame. `tools/place.py` is the only code that applies a contracted frame: it builds an asset into its own collection and places one anchor that instances that collection with the frame, so every part, including the asset's own instances, is transformed exactly once. The isolated detail preview and the integrated scene both place through it, so the critic sees the proportions integration produces.

The driver measures what was placed. For every anchor in a saved scene, `tools/place.py measure` records the frame's front, the box of each `spatial_region`-tagged part, and the rendered triangles' floor projection as conservative 5 mm grid row runs, so the record grows with the outline rather than the tessellation; `tools/observe.py` unions those runs, closing gaps narrower than 2 cm, into one outer outline that preserves concavities, and rejects by name an object that projects to disjoint parts, which `footprint_xy` cannot represent. The result is `state/spatial_observed.json`, and the observed gate rejects any invariant that does not round-trip. Aperture luminance is a pixel sample the integrate and materials builders record in `state/aperture_luminance.json`; the driver deletes that file, and the stage's scene, before each of those builder calls.

Critics write JSON matching `verdict.schema.json`: a numeric score, summary, concrete corrections, the stage responsible for the first correction, and identification-specific wrong-label and missing-object arrays.

## Prompt requirement classes

Prompts distinguish checked facts and hand-off invariants from encouraged methods. A hard requirement names both its machine gate and the builder's recourse in the same line; methods, style, and micro-geometry remain preferences that may be overridden when the reason is recorded in `state/attempt-notes.md`. Critics judge the result against the photograph, not adherence to a method.

## Stages

1. **Floorplan** estimates room geometry, fixed features, scale, and camera, then renders a top-down diagram.
2. **Blockout** inventories every visible object and renders neutral primitives plus a 50% reference overlay. This stage evaluates projection and placement without material distractions.
3. **Identify** produces an enlarged labelled crop for every observed object and a contact sheet, then corrects labels and omissions.
4. **Detail** sorts objects by contracted footprint into large, medium, and small tiers. Each fresh builder receives one crop, the whole photograph, and one object entry; it confirms or corrects the proposed label, then renders the asset alone. After each tier, a fresh critic reviews a cumulative composition before the next tier starts. Inferred entries are built first, from their contract and the whole photograph alone; only the detail asset gate checks them, their labels stay as declared, and the report lists them as unscored inferred structure apart from the scored detail.
5. **Integrate** starts from `state/placed.blend`, in which the driver has placed every asset, adds the shell and camera, and evaluates placement, intersections, floating geometry, gaps, and camera fit.
6. **Materials** preserves asset materials while adding shell materials, lighting, colour management, and a final photographic render.

Stages 1, 2, 5, and each final evaluation permit up to three attempts; identification and each object permit up to two. A score of 8/10 passes. When attempts are exhausted, the highest-scoring result remains authoritative.

## GOTO and correction rules

Builders and critics may assign a defect to `floorplan`, `blockout`, `identify`, `detail`, `object:<id>`, `integrate`, or `materials`. An object target is valid only when its identifier exists in `objects.json`. The driver renders that target set, each object with its inventory label, from the current `objects.json` and supplies it to every critic and to every builder whose prompt offers a GOTO.

A builder GOTO is `state/goto.json` holding exactly `{"stage": "<target>", "reason": "<why>"}`. A malformed file or unknown target is rejected without consuming the GOTO allowances; the builder is called again with a correction naming the missing, unexpected, or invalid field, and a second rejected request is ignored.

A critic's `top_stage` is constrained by a verdict schema whose enum is that target set. A verdict naming any other target re-asks only the critic, never the builder, including after a stage's final build attempt; a second invalid route keeps the verdict on the critic's own stage.

After integration or materials, a score below 8 may return to the stage named by the highest-priority correction. Forward execution then resumes from the repaired contract.

Builders and critics each have an ordinary allowance of five accepted GOTOs. Once an origin's allowance is exhausted, integration and materials each retain one blockout-only GOTO, shared by builder and critic. Neither early stages nor integration can spend materials' reserve. Counts and reserve use persist across resume; old checkpoints keep their spent counts and gain the two reserves. A fresh run therefore accepts at most 12 GOTOs, independent of object count. Exhausted builder requests receive one bounded fallback call with correction context; exhausted critic requests advance.

A 3.5-hour cap starts at the first integration or materials attempt of one pipeline invocation. Once it has expired and a materials scene is saved, the run finalizes that scene instead of starting any further attempt of any stage, whether a retry within a stage or an earlier stage requested by a GOTO. While normal stage execution and that budget permit, each reserve provides one repair opportunity; it does not guarantee a successful repair. See the [focused control-flow measurement](../experiments/goto-reserve/README.md).

All spatial corrections return to blockout, the sole spatial authority. Detail may refine geometry and materials but cannot mutate pose, dimensions, facing, footprint, semantic regions, relationships, or ownership.

## Asset checks

Before an isolated detail render reaches its critic, the driver checks that the asset exists, differs from the placeholder and every other asset, and defines the required build function. It then imports the asset and calls `build` in headless Blender, and rejects the attempt if any image it loads, through Blender or a Python file read, has a relative path or resolves outside `textures/<id>/`. Finally it places the asset through `tools/place.py` and renders the critic's isolated view `state/detail_<id>.png` from that placement. An attempt failing any gate is never kept as the object's candidate. Each kept attempt's snapshot carries `textures/<id>/` with its script, render and entry. Restoring the best attempt restores that directory too, and every later builder call, including tiers, integration, materials and the final render, first restores each other object's selected candidate from its snapshot. A failure becomes a scored attempt with the validation message as feedback. Blockout declarations and measured integration invariants pass the same machine gate, which applies one clearance and support rule to declared and measured geometry. A blockout, integration, or materials failure produces a 0/10 verdict whose corrections contain the concrete validator errors; a blockout attempt with an invalid declaration is never kept. Aperture visibility is sampled and checked again after final materials.

## Model call bounds

Every builder and critic call is stopped after `MODEL_SECONDS` (2100 s, set in `pipeline.sh`); the final render call gets 4800 s. A call is also stopped after 1500 s in which it prints no non-whitespace character while its descendant processes, not the Codex process itself, together use less than 0.1 CPU-seconds between one-second polls. A silent Blender render therefore keeps its call alive, while a whitespace stream or a hang does not. A stop signals the Codex process and every descendant.

Each bound is three times the slowest traced attempt, rounded up to five minutes. An attempt covers its builder call, its critic call, and its gates, so it bounds each call from above. The traces are the attempt records of five runs, including the [Wilson House example](../examples/wilson-house/scores.md); the final render is timed from the end of materials to completion in the three runs that finished.

| Stage | Slowest traced attempt | Bound |
|---|---:|---:|
| floorplan | 506 s | 2100 s |
| blockout | 570 s | 2100 s |
| identify | 522 s | 2100 s |
| detail, per object | 614 s | 2100 s |
| tier review | 369 s | 2100 s |
| integrate | 644 s | 2100 s |
| materials | 298 s | 2100 s |
| final render | 1548 s | 4800 s |

The tier row excludes six Wilson House tier reviews that ran 66 to 188 minutes; none changed a file in the work directory after its first three minutes. The 1500 s idle bound is about 2.4 times the longest silence, 621 s, observed between events in recorded Codex CLI sessions.

A stopped call, or one that exits non-zero, produces a 0/10 verdict whose correction names the failure. That verdict counts as an attempt of the current stage under its usual limits, but its files are never restored as the stage's best result. When an object's detail attempts end, including on a GOTO, the driver replaces `assets/<id>.py` and its render with the best completed attempt's copies, or removes them when no attempt completed. A tier review whose call fails is retried once with the failure as its correction; after a second failure the run continues as though the tier passed. Floorplan, blockout, identify, or integrate stops the run when none of its attempts completed, and a failed final render call stops the run. When two consecutive calls exit non-zero, the driver exits without recording the second, so an unreachable model service costs one attempt rather than every remaining one. `state/model_failed` carries the first of those failures across a resume until a call completes or is stopped.

## Resume behavior

Contracts, verdicts, attempt copies, counters, records, object tiers, and best results live on disk; the 3.5-hour cap does not, so a resumed run starts a fresh one. `PHOTO_TO_SCENE_STAGE` selects the first stage for a resumed run. The detail loop reads prior scores and attempts, skips objects already scoring at least 8 or already at their attempt cap, appends progress after every object, and records the active tier with each result. The best materials scene is retained whenever its score improves, so finalization does not depend on the last attempt being the best.
