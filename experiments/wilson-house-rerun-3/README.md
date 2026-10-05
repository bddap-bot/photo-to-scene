# Wilson House: third rerun, after workflow defects #50 and #53–#56

## Design recorded before execution

Requirement: measure what the fixes for #50 and #53–#56 change on the public Wilson
House example, against the [post-defects second run](../wilson-house-post-defects/README.md)
("rerun 2", published in `examples/wilson-house/post-defects/`), without
photograph-specific tuning.

The simplest design repeats rerun 2's protocol once: one fresh end-to-end run from an
empty run directory, the same full-resolution photograph, and unchanged prompts, driver,
budgets and builders. Publish into `examples/wilson-house/rerun-3/`, beside the earlier
results, and leave every earlier result and experiment intact. No workflow code is added
for the experiment.

### Fixed configuration

- Workflow: `f5ca045184c5dac2fbb98f226362e74a57fea12d`. It contains the landings for
  #55 (`addf259`), #53 (`eb10359`), #54 (`c7c990b`), #56 (`d2b11ed`) and #50
  (`64c9376`); the later `f5ca045` changes tests only. The run executes from an
  exported copy of that tree, so later commits cannot enter mid-run.
- Model: `gpt-6-astra` through Codex CLI 0.156.0, reasoning effort **`none`**, the
  same effort as rerun 2 and the combined-fixes run. Every child transcript header is
  counted after the run to confirm it.
- Input: the original 6114×4842 Library of Congress JPEG, SHA-256
  `2f51726bfcb4f24445bb301131ad322f278d5f2412bfa4f926f6d602799a735a`, credited in
  [the example attribution](../../examples/wilson-house/ATTRIBUTION.md).
- Rendering device: the pipeline's own choice; nothing is forced.

### Dependency rationale

- The full-resolution photograph controls input quality, as in rerun 2.
- Codex supplies builders and critics; holding its model and effort fixed removes that
  confound.
- Nix supplies Python, Blender and ImageMagick: contract checks, scene builds and
  renders, and comparison images.

### Rerun 2, the comparison target

Workflow `4d84583`, effort `none` on 587/587 calls, normal driver exit after 56,613 s
with no interruption. Final observed spatial gate failed: integration 20 errors on each
of three attempts, materials 69 errors on a stale assembly (#54). No in-run scene
critic ran. 66/66 observed detail objects finalized, mean best 7.29/10, 28 at least 8,
plus 2 inferred structures. GOTO spend: 7 builder (4 facing repairs, 1 forward
hand-off, 2 reserves), 5 critic. 52 repairs refused at caps.

### Expected effects, to be checked rather than presumed

| Fix | Rerun 2 observation | Expected observable change |
|---|---|---|
| #55 | Walls, cornices, baseboards, the pelmet, the sconce and the clock were declared facing world +Y; four builder GOTOs and about ten refused requests went to facing repairs. | The blockout declaration gate rejects a wrong facing against the room outline, so the blockout builder repairs it in-stage. No detail-to-blockout GOTO for facing. |
| #53 | The blockout builder's forward hand-off to `object:north_cornice` spent a repair GOTO and skipped the blockout critic; four more hand-offs were refused at the cap. | A GOTO to the builder's own or a later stage completes the stage, runs its critic and selection, and spends nothing. No forward hand-off appears among spent or refused GOTOs. |
| #54 | After the materials reserve repair, integration ran no attempt and restored the old assembly; materials measured 69 errors against it. | Integration attempts are keyed to the floorplan, contracts and selected assets. After any upstream reentry, integration runs fresh attempts, and materials receives the assembly built from current contracts. |
| #56 | One run-wide pool; detail and tier reviews spent it, and blockout reserves patched integration and materials. | Each GOTO-capable stage holds two GOTOs shared by its builder and critic; object stages are charged to detail. Integration and materials keep their own allowance; no reserve appears. |
| #50 | Entry fields outside the spatial contract reached detail unchecked; `front_xy` could disagree with the frame. | Detail sees only the closed projection; reuse keys on that projection. No detail repair is driven by a stale or extra entry field. |

The headline measures are the final observed gate and its error count, whether an
in-run integration or materials critic ran and its score, and the detail-object
finalization and mean. A passing gate is not presumed: rerun 2's 20 integration errors
included real disagreements (furniture footprints and regions, an untagged window
opening and shelves) that none of these fixes addresses directly.

### Execution and reporting protocol

1. Land this design first. Record the start time and the exported workflow tree.
2. Run `pipeline.sh` unmodified with a fresh `PHOTO_TO_SCENE_ROOT`. Observe all child
   processes to completion. If infrastructure interrupts the run, resume on the same
   tree with `PHOTO_TO_SCENE_STAGE` and record the stop, the gap and the resume point.
   A continuation during integration or materials restarts the in-memory stage 5/6
   clock and is reported.
3. Do not tune prompts, budgets or candidates. A low score is a measured result. If the
   run needs supervised finalization, the report says so.
4. Derive from saved records and logs the same measures as rerun 2: final gate and
   error count, in-run critic scores, finalized objects and their mean score, GOTO
   spend by stage, refused and invalid-target requests, recorded and known attempt
   sequences, summed attempt seconds, per-stage time and tokens, driver-enforced model
   stops, final render time, end-to-end elapsed time and finalization mode.
5. Publish the same artefacts as rerun 2: the before/after table with a rerun-2
   column, scores and contracts, `final.png`, the photo/render side-by-side, and a
   labelled rerun-2/rerun-3 comparison. View every published render before landing.
   File each newly exposed defect separately.

This is one stochastic comparison, not a per-fix ablation. A different object count
is an outcome.
