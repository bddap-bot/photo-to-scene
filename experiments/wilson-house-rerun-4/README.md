# Wilson House: fourth rerun, after workflow defects #58–#61

## Design recorded before execution

Requirement: measure what the fixes for #58–#61 change on the public Wilson House
example, against the [third rerun](../wilson-house-rerun-3/README.md) ("rerun 3",
published in `examples/wilson-house/rerun-3/` at `b290369`), without
photograph-specific tuning. Confirm #58 end to end: the final spatial gate's errors,
and whether the open seam at the west/north wall corner below the cornice is gone.

The simplest design repeats rerun 3's protocol once: one fresh end-to-end run from an
empty run directory, the same full-resolution photograph, and unchanged prompts,
driver, budgets and builders. Publish into `examples/wilson-house/rerun-4/`, beside the
earlier results, and leave every earlier result and experiment intact. No workflow code
is added for the experiment.

### Fixed configuration

- Workflow: `5acde1f9f6ec5a8cde09e791ff1f499829171bda`. It contains the landings for
  #58 (`8811df3`), #59 (`f018a0a`), #60 (`b27a917`) and #61 (`49fcbd2`). The later
  `5acde1f` restores the first best integration attempt on a score tie, as every other
  stage already did. The run executes from an exported copy of that tree, so later
  commits cannot enter mid-run.
- Model: `gpt-6-astra` through Codex CLI 0.156.0, reasoning effort **`none`**, the
  same model and effort as rerun 3 and rerun 2. Every child transcript header is
  counted after the run to confirm it.
- Input: the original 6114×4842 Library of Congress JPEG, SHA-256
  `2f51726bfcb4f24445bb301131ad322f278d5f2412bfa4f926f6d602799a735a`, credited in
  [the example attribution](../../examples/wilson-house/ATTRIBUTION.md).
- Rendering device: the pipeline's own choice; nothing is forced.

### Dependency rationale

- The full-resolution photograph controls input quality, as in rerun 3.
- Codex supplies builders and critics; holding its model and effort fixed removes that
  confound.
- Nix supplies Python, Blender and ImageMagick: contract checks, scene builds and
  renders, and comparison images.

### Rerun 3, the comparison target

Its published record (`report.md`, `scores.md`, `measurements.json` at `b290369`) is
the baseline; every rerun-3 number in the results comes from it. In summary: workflow
`f5ca045`, effort `none` on every call, normal driver exit after one infrastructure
interruption during detail. The final observed spatial gate failed on 3 asset-geometry
errors (the rocker's footprint and `open_back` region, the fire tools' footprint) on
every integration attempt and at materials. No in-run scene critic ran. The render
shows an open seam at the west/north wall corner below the cornice.

### Expected effects, to be checked rather than presumed

| Fix | Rerun 3 observation | Expected observable change |
|---|---|---|
| #58 | Detail accepted assets that missed their contracts; the rocker and fire-tools errors surfaced only at integration, and every repair routed to blockout, which rebuilt nothing. An open seam showed at the west/north wall corner. | Detail rejects an attempt whose lone-placed asset misses its footprint or regions, with the measured deviation, so those errors are repaired in-stage. An integration or materials gate failure made only of asset geometry routes to `object:<id>`, not blockout. The final gate carries no footprint or region error that detail accepted. Whether the wall seam closes is open: the footprint check sees a wall gap only beyond its 0.03 m tolerance. |
| #59 | The facing gate required a sofa and a footstool to face like the fender and a chair, and advised a floorplan GOTO for it. | Facing propagates only from entries without `supported_by`; no furniture-to-furniture facing requirement and no floorplan GOTO for a furniture "wall". |
| #60 | Refused contract-repair requests were dropped once detail's allowance was spent; swapped book rows, a 12 mm box and low tiebacks were requested repeatedly. | Refused requests are kept in `state/pending_repairs.json`, reach the tier review and the next dispatched GOTO to their target, and leftovers are listed in `scores.md`. Fewer repeated identical refusals. |
| #61 | About 18,000 s of upstream repair ran after the stage 5/6 budget expired. | After expiry no GOTO is available; if no materials scene is saved, one materials attempt runs on the best integration and the run finalizes. No upstream repair after expiry. |

The headline measures are the final observed gate and its error count, whether an
in-run integration or materials critic ran and its score, the detail-object
finalization and mean, and the wall seam in the final render. A passing gate is not
presumed.

### Execution and reporting protocol

1. Land this design first. Record the start time and the exported workflow tree.
2. Run `pipeline.sh` unmodified with a fresh `PHOTO_TO_SCENE_ROOT`. Observe all child
   processes to completion. If infrastructure interrupts the run, resume on the same
   tree with `PHOTO_TO_SCENE_STAGE` and record the stop, the gap and the resume point.
   A continuation during integration or materials restarts the in-memory stage 5/6
   clock and is reported.
3. Do not tune prompts, budgets or candidates. A low score is a measured result. If the
   run needs supervised finalization, the report says so.
4. Derive from saved records and logs the same measures as rerun 3: final gate and
   error count, in-run critic scores, finalized objects and their mean score, GOTO
   spend by stage, refused and kept repair requests, invalid-target requests, recorded
   and known attempt sequences, summed attempt seconds, per-stage time and tokens,
   driver-enforced model stops, final render time, end-to-end elapsed time and
   finalization mode. For #58, also count detail rejections carrying a measured
   footprint or region deviation and gate verdicts routed to `object:<id>`.
5. Publish the same artefacts as rerun 3: the before/after table with a rerun-3
   column, scores and contracts, `final.png`, the photo/render side-by-side, and a
   labelled rerun-3/rerun-4 comparison. Inspect the west/north wall corner in the
   final render. View every published render before landing. File each newly exposed
   defect separately.

This is one stochastic comparison, not a per-fix ablation. A different object count
is an outcome.
