# Pipeline stages and contracts

The pipeline treats reconstruction as a sequence of durable, reviewable contracts. Each builder starts with the reference image and the smallest relevant on-disk state. A fresh critic scores its result. Builders never communicate hidden scene state to later stages.

## Coordinate and file contracts

All measurements use metres. The room coordinate origin is a floor corner, with `x` along the far wall, `y` toward the camera, and `z` upward.

`floorplan.json` describes the room polygon, wall heights, openings, fixed architectural features, camera pose and optics, a scale anchor, and the derivation of inferred dimensions.

`objects.json` is an exhaustive array of visible objects. Each entry carries a stable identifier, proposed and object-reviewed labels, the reason for any confirmation or correction, a source-image crop rectangle, room-space bounding box, contact relationship, material observation, confidence, and a source-grounded spatial contract. The contract fixes one local-to-room frame, facing, footprint, confidence-aware semantic regions, relationships, ownership, and applicable aperture visibility.

`assets/<id>.py` exposes `build(entry, collection=None)`. It creates recognisable geometry and material in one normalized local frame and returns the Blender objects it creates. Integration applies the contracted frame once and rejects any measured invariant that does not round-trip.

Critics write JSON matching `verdict.schema.json`: a numeric score, summary, concrete corrections, the stage responsible for the first correction, and identification-specific wrong-label and missing-object arrays.

## Prompt requirement classes

Prompts distinguish checked facts and hand-off invariants from encouraged methods. A hard requirement names both its machine gate and the builder's recourse in the same line; methods, style, and micro-geometry remain preferences that may be overridden when the reason is recorded in `state/attempt-notes.md`. Critics judge the result against the photograph, not adherence to a method.

## Stages

1. **Floorplan** estimates room geometry, fixed features, scale, and camera, then renders a top-down diagram.
2. **Blockout** inventories every visible object and renders neutral primitives plus a 50% reference overlay. This stage evaluates projection and placement without material distractions.
3. **Identify** produces an enlarged labelled crop for every object and a contact sheet, then corrects labels and omissions.
4. **Detail** sorts objects by contracted footprint into large, medium, and small tiers. Each fresh builder receives one crop, the whole photograph, and one object entry; it confirms or corrects the proposed label, then renders the asset alone. After each tier, a fresh critic reviews a cumulative composition before the next tier starts.
5. **Integrate** assembles the shell and all asset builders, resolves contact relationships, and evaluates placement, intersections, floating geometry, gaps, and camera fit.
6. **Materials** preserves asset materials while adding shell materials, lighting, colour management, and a final photographic render.

Stages 1, 2, 5, and each final evaluation permit up to three attempts; identification and each object permit up to two. A score of 8/10 passes. When attempts are exhausted, the highest-scoring result remains authoritative.

## GOTO and correction rules

Builders and critics may assign a defect to `floorplan`, `blockout`, `identify`, `detail`, `object:<id>`, `integrate`, or `materials`. An object target is valid only when its identifier exists in `objects.json`. An invalid target is rejected without consuming the global allowance; the originating stage receives one correction opportunity, and a second invalid request is ignored.

After integration or materials, a score below 8 may return to the stage named by the highest-priority correction. Forward execution then resumes from the repaired contract. At most five valid GOTOs are taken. The integration/materials portion also has a 3.5-hour cap, after which the best saved materials scene is finalized.

All spatial corrections return to blockout, the sole spatial authority. Detail may refine geometry and materials but cannot mutate pose, dimensions, facing, footprint, semantic regions, relationships, or ownership.

## Asset checks

Before an isolated detail render reaches its critic, the driver checks that the asset exists, differs from the placeholder and every other asset, defines the required build function, references texture files only inside the run's `textures/` directory, and produced a render newer than the current attempt marker. A failure becomes a scored attempt with the validation message as feedback. Blockout declarations and measured integration invariants pass the same machine gate; an integration or materials failure produces a 0/10 verdict whose corrections contain the concrete validator errors. Aperture visibility is sampled and checked again after final materials.

## Resume behavior

Contracts, verdicts, attempt copies, counters, records, object tiers, and best results live on disk. `PHOTO_TO_SCENE_STAGE` selects the first stage for a resumed run. The detail loop reads prior scores and attempts, skips objects already scoring at least 8 or already at their attempt cap, appends progress after every object, and records the active tier with each result. The best materials scene is retained whenever its score improves, so finalization does not depend on the last attempt being the best.
