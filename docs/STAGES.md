# Pipeline stages and contracts

The pipeline treats reconstruction as a sequence of durable, reviewable contracts. Each builder starts with the reference image and the smallest relevant on-disk state. A fresh critic scores its result. Builders never communicate hidden scene state to later stages.

## Coordinate and file contracts

All measurements use metres. The room coordinate origin is a floor corner, with `x` along the far wall, `y` toward the camera, and `z` upward.

`floorplan.json` describes the interior room outline as `room.polygon_xy_m`, wall heights, openings, fixed architectural features, camera pose and optics, a scale anchor, and the derivation of inferred dimensions.

`objects.json` is an exhaustive array of visible objects plus any structure the scene needs that the photograph does not show. Each entry carries a stable identifier, proposed and object-reviewed labels, the reason for any confirmation or correction, a source-image crop rectangle, room-space bounding box, contact relationship, material observation, confidence, and a source-grounded spatial contract. The contract fixes one local-to-room frame, whose y axis is the facing, footprint, confidence-aware semantic regions, relationships, ownership, and applicable aperture visibility. An entry for unshown structure, such as a room closure outside the frame, is marked `inferred` and carries no crop rectangle; the declaration gate requires a crop rectangle on every other entry and rejects one on an inferred entry. The declaration gate also derives facing from that outline: an entry lying along a wall, or along the front of an entry so placed that rests on no declared support, faces the wall's interior normal, and an entry supported by one faces within 60 degrees of it.

`assets/<id>.py` exposes `build(entry, collection=None)`. It creates recognisable geometry and material in one normalized local frame. `tools/place.py` is the only code that applies a contracted frame: it builds an asset into its own collection and places one anchor that instances that collection with the frame, so every part, including the asset's own instances, is transformed exactly once. The isolated detail preview and the integrated scene both place through it, so the critic sees the proportions integration produces.

The driver measures what was placed. For every anchor in a saved scene, `tools/place.py measure` records the frame's front, the box of each `spatial_region`-tagged part, and the rendered triangles' floor projection as conservative 5 mm grid row runs, so the record grows with the outline rather than the tessellation; `tools/observe.py` unions those runs, closing gaps narrower than 2 cm, into one outer outline that preserves concavities, and rejects by name an object that projects to disjoint parts, which `footprint_xy` cannot represent. The result is `state/spatial_observed.json`, and the observed gate rejects any invariant that does not round-trip. Aperture luminance is a pixel sample the integrate and materials builders record in `state/aperture_luminance.json`; the driver deletes that file, and the stage's scene, before each of those builder calls.

Critics write JSON matching `verdict.schema.json`: a numeric score, summary, concrete corrections, the stage responsible for the first correction, and identification-specific wrong-label and missing-object arrays.

## Prompt requirement classes

Prompts distinguish checked facts and hand-off invariants from encouraged methods. A hard requirement names both its machine gate and the builder's recourse in the same line; methods, style, and micro-geometry remain preferences that may be overridden when the reason is recorded in `state/attempt-notes.md`. Critics judge the result against the photograph, not adherence to a method.

## Stages

1. **Floorplan** estimates room geometry, fixed features, scale, and camera, then renders a top-down diagram.
2. **Blockout** inventories every visible object and renders neutral primitives plus a 50% reference overlay. This stage evaluates projection and placement without material distractions.
3. **Identify** produces an enlarged labelled crop for every observed object and a contact sheet, then corrects labels and omissions.
4. **Detail** sorts objects by contracted footprint into large, medium, and small tiers. Each fresh builder receives one crop, the whole photograph, and one object entry; it confirms or corrects the proposed label, then renders the asset alone. That entry is the driver's projection of the inventory entry onto its identifier, proposed label, material note, and the checked contract fields: frame, footprint, region identifiers and boxes, relationships, ownership, appearance, and the inferred mark. Source evidence, region confidence, and every other entry field stay out of it, and the same projection keys which earlier attempts of the object still count. After each tier, a fresh critic reviews a cumulative composition before the next tier starts. Inferred entries are built first, from their contract and the whole photograph alone; only the detail asset gate checks them, their labels stay as declared, and the report lists them as unscored inferred structure apart from the scored detail.
5. **Integrate** starts from `state/placed.blend`, in which the driver has placed every asset, adds the shell and camera, and evaluates placement, intersections, floating geometry, gaps, and camera fit.
6. **Materials** preserves asset materials while adding shell materials, lighting, colour management, and a final photographic render.

Stages 1, 2, 5, and 6 permit up to three attempts; identification and each object permit up to two. A score of 8/10 passes. Below it, a verdict naming its own stage retries that stage with the verdict's corrections. When attempts are exhausted, the highest-scoring result remains authoritative.

## GOTO and correction rules

A GOTO repairs an upstream owner. Stages run in the order `floorplan`, `blockout`, `identify`, `detail` with its `object:<id>` stages, each footprint tier's review, `integrate`, `materials`; an object target is valid only when its identifier exists in `objects.json`. A builder's target set holds only the stages before its own, so an object builder may name `floorplan`, `blockout`, or `identify` but no object, and a tier builder may also name `detail` and any object. A critic's target set adds its own stage, which attributes the defect without redirecting. The driver renders each set, objects with their inventory labels, from the current `objects.json` and supplies it to every critic and to every builder whose prompt offers a GOTO. Forward hand-off needs no GOTO: the driver already resumes detail and reuses finalized objects.

A builder GOTO is `state/goto.json` holding exactly `{"stage": "<target>", "reason": "<why>"}`. A malformed file or unknown target is rejected without consuming the GOTO allowances; the builder is called again with a correction naming the missing, unexpected, or invalid field, and a second rejected request is ignored. A well-formed GOTO naming the builder's own stage or a later one is not a repair: the driver logs it as ignored and completes the stage normally, so its critic, best-candidate selection, and forward flow run without spending an allowance.

A critic's `top_stage` is constrained by a verdict schema whose enum is that critic's target set. A verdict naming any other target re-asks only the critic, never the builder, including after a stage's final build attempt; a second invalid route keeps the verdict on the critic's own stage.

After integration or materials, a score below 8 may return to the stage named by the highest-priority correction. Forward execution then resumes from the repaired contract. An `object:<id>` target rebuilds that object within its footprint tier and then resumes detail: objects already scoring at least 8 or at their attempt cap are reused, any other object is built, and a tier is reviewed again only when one of its objects was built after its last review.

Each stage that can request a GOTO has its own allowance of two accepted GOTOs, shared by its builder and critic. All `object:<id>` stages share the `detail` allowance, and each footprint tier's review has its own, so an early stage cannot spend a later stage's repairs. A request from a stage whose allowance is spent does not dispatch: an exhausted builder request receives one bounded fallback call with correction context, and an exhausted critic request advances. A well-formed builder request refused at the cap is kept in `state/pending_repairs.json`, one entry per requesting stage and target that counts its refusals and lists each distinct reason. The tier review of a requesting object's tier receives that tier's kept requests and may route the confirmed ones as one GOTO; every GOTO that dispatches carries all kept requests for its target into the repairing stage's correction context and clears them. Requests still kept at the end are listed under "Outstanding contract repairs" in `scores.md`. Allowance use is written to `state/goto_<stage>` before dispatch and persists across resume; the run stops if that write fails. Eight stages can request a GOTO (`blockout`, `identify`, `detail`, three tier reviews, `integrate`, `materials`), so a run accepts at most 16 GOTOs, independent of object count.

A 3.5-hour cap starts at the first integration or materials attempt of one pipeline invocation. Once it has expired and a materials scene is saved, the run finalizes that scene instead of starting any further attempt of any stage, whether a retry within a stage or an earlier stage requested by a GOTO.

All spatial corrections return to blockout, the sole spatial authority. Detail may refine geometry and materials but cannot mutate pose, dimensions, facing, footprint, semantic regions, relationships, or ownership.

## Asset checks

Before an isolated detail render reaches its critic, the driver checks that the asset exists, differs from the placeholder and every other asset, and defines the required build function. It then imports the asset and calls `build` in headless Blender, and rejects the attempt if any image it loads, through Blender or a Python file read, has a relative path or resolves outside `textures/<id>/`. It then places the asset alone through `tools/place.py measure-alone` and applies the observed gate's own footprint and region checks to that one object, rejecting the attempt with the measured deviation; relationships and aperture luminance need the assembled scene and are checked from integration on. Finally it renders the critic's isolated view `state/detail_<id>.png` from the same placement. An attempt failing any gate is never kept as the object's candidate. Each kept attempt's snapshot carries `textures/<id>/` with its script, render and entry. Restoring the best attempt restores that directory too, and every later builder call, including tiers, integration, materials and the final render, first restores each other object's selected candidate from its snapshot. A failure becomes a scored attempt with the validation message as feedback. Blockout declarations and measured integration invariants pass the same machine gate, which applies one clearance and support rule to declared and measured geometry. A blockout, integration, or materials failure produces a 0/10 verdict whose corrections contain the concrete validator errors; a blockout attempt with an invalid declaration is never kept. When every observed error is placed asset geometry against valid declarations, the validator names the owning objects and the verdict routes to the first `object:<id>`, whose errors lead its corrections, since blockout would keep the contract and rebuild nothing. Aperture visibility is sampled and checked again after final materials.

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
