# Wilson House: rerun after workflow defects #35–#49

## Design recorded before execution

Requirement: measure what the fixes for #35–#49 change on the public Wilson House
example, against the [combined-fixes rerun](../wilson-house-combined-fixes/README.md),
without photograph-specific tuning.

The simplest design repeats that run's protocol once: one fresh end-to-end run from an
empty run directory, the same full-resolution photograph, and unchanged prompts, driver,
budgets and builders. Publish into `examples/wilson-house/post-defects/`, beside the
combined-fixes and original results, and leave every earlier result and experiment
intact. No workflow code is added for the experiment.

### Fixed configuration

- Workflow: `af4f3d519886df1c47c0d68540dd04c3c3a36a6f`. The run executes from an
  exported copy of that tree, so later commits cannot enter mid-run.
- Model: `gpt-6-astra` through Codex CLI 0.156.0, reasoning effort **`none`**. This
  matches the combined-fixes run, the comparison target. The original published
  baseline used `medium`; the combined-fixes comparison mixed the two. Here the effort
  stays `none` for every call, and every child transcript header is counted after the
  run to confirm it.
- Input: the original 6114×4842 Library of Congress JPEG, SHA-256
  `2f51726bfcb4f24445bb301131ad322f278d5f2412bfa4f926f6d602799a735a`, credited in
  [the example attribution](../../examples/wilson-house/ATTRIBUTION.md).
- Rendering device: the pipeline's own choice; nothing is forced.

### Dependency rationale

- The full-resolution photograph controls input quality; the 1529×1211 preview would
  change the comparison.
- Codex supplies builders and critics; its model and effort are the confound this
  design removes.
- Nix supplies Python, Blender and ImageMagick: contract checks, scene builds and
  renders, and comparison images.

### Expected effects, to be checked rather than presumed

| Fix | Combined-fixes observation | Expected observable change |
|---|---|---|
| #35, #49 | A wrapped inventory crashed validation; the retry got a generic correction. | Malformed inventories, entry fields and observed records produce structured gate errors; no validator crash appears in the log. |
| #36, #43 | Ceiling critics requested separately owned trim, costing builder GOTOs; relabeled details duplicated a screen and a drape. | Builders and critics see overlapping owned entries; a claimed neighbour fails identification instead of redirecting to blockout. Fewer detail-sourced builder GOTOs. |
| #37, #44 | Appearance handoff metadata reset a ceiling budget; stale numeric appearance text survived spatial revisions. | The contract carries only machine-checked fields, so annotation changes no longer invalidate details and no stale numeric instruction can contradict a region. |
| #38 | Six builder redirects left no scored record or time. | Every redirected builder attempt is recorded with its seconds; known sequences equal recorded sequences plus infrastructure losses. |
| #39, #46 | 26 invalid-target requests; a scene critic invented `object:foreground_bowl`. | One canonical target list with labels; an invalid critic target is re-asked in the same loop. Invalid-target refusals near zero. |
| #40 | Inferred hidden wall W3 was scored 0/10 against a window crop. | Inferred structure gets no crop and no critic and is reported unscored. |
| #41 | Restoring a best rug, tablecloth or table attempt kept a later attempt's texture. | Each candidate keeps its textures; the selected detail's textures are the ones integrated. |
| #42, #45 | Detail previews ignored contracted axis sizes; the footprint observer replaced the L-shaped floor with its bounding rectangle. | One driver tool places every asset by its contract frame and measures what it placed; concave footprints are compared as declared. |
| #47, #48 | An expired integration/materials budget still launched a floorplan repair; finalization had to be supervised. | The budget is checked at every attempt start and an expired budget finalizes the saved best materials scene. The run should end with a normal driver `COMPLETE`, without supervision. |

### Execution and reporting protocol

1. Land this design first. Record the start time and the exported workflow tree.
2. Run `pipeline.sh` unmodified with a fresh `PHOTO_TO_SCENE_ROOT`. Observe all child
   processes to completion. If infrastructure interrupts the run, resume on the same
   tree with `PHOTO_TO_SCENE_STAGE` and record the stop, the gap and the resume point.
   The stage 5/6 elapsed cap is held in driver memory, so a continuation during
   integration or materials restarts that clock; any such continuation is reported.
3. Do not tune prompts, budgets or candidates. A low score is a measured result.
4. Derive from saved records and logs: final gate and error count, in-run critic
   scores, finalized objects and their mean score, GOTO spend by origin and source
   stage including reserves, refused and invalid-target requests, recorded and known
   attempt sequences, summed attempt seconds by class, driver-enforced model stops,
   final render time, end-to-end elapsed time, and whether finalization needed
   supervision.
5. Publish the same artefacts as the combined-fixes run: before/after table with a
   combined-fixes column, scores and contracts, `final.png`, the photo/render
   side-by-side, and a labelled combined-fixes/rerun comparison. View every published
   render before landing. File each newly exposed defect separately.

This is one stochastic comparison, not a per-fix ablation. A different object count
is an outcome.
