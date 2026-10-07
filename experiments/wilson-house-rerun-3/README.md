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

## Results

The run started from an empty directory on `f5ca045` and ended with a normal driver `COMPLETE` after 133,078 s, with no supervised finalization. One infrastructure interruption stopped it during detail. It resumed at `detail` on the same tree in under a minute, losing sequence 239, and that continuation restarted the stage 5/6 clock. The [rerun 3 report](../../examples/wilson-house/rerun-3/report.md) holds the full table, per-stage time and tokens, renders and evidence.

| Measure | Rerun 2 | Rerun 3 |
|---|---|---|
| Workflow | `4d84583`, effort `none` (587/587 calls) | `f5ca045`, effort `none` (769/769 calls) |
| Finalization | Normal driver exit | Normal driver exit |
| Infrastructure interruptions | 0; 3 provider-capacity failures | 1, resumed at `detail`; 0 provider-capacity failures |
| Final observed spatial gate | Fail; 69 errors at materials on a stale assembly; integration 20 on each attempt | Fail; 3 errors at materials on the current assembly; integration 3 on each of 9 attempts |
| In-run scene critic | None: gate-rejected | None: gate-rejected |
| Detail objects | 66/66 observed; mean 7.29; 28 at least 8; 2 inferred | 65/65 observed; mean 7.46; 34 at least 8; 2 inferred |
| GOTO spend | 7 builder (4 facing, 1 forward hand-off, 2 reserves); 5 critic | 10 builder, at most 2 per stage, none for facing or hand-off; 4 critic |
| Refused repairs | 52 at caps; 0 invalid targets | 71 at caps (60 builder, 11 critic within tiers); 0 invalid targets |
| Summed attempt time | 55,890 s | 131,991 s |
| End-to-end elapsed | 56,613 s | 133,078 s |

Expected effects that held:

- #55: no facing GOTO and no facing refusal.
- #53: no forward hand-off spent; one was ignored at no cost.
- #54: fresh integration attempts after every upstream repair, and materials measured the current assembly.
- #56: per-stage allowances, with integration and materials spending their own.

#50 was not separately measurable. Its observable proxy, no repair citing an out-of-contract field, held.

The final gate now fails on three asset-geometry errors that detail accepted, not on stale or facing errors. Rerun 3 also took 2.4 times as long, mostly in detail, where 60 refused blockout requests each cost an attempt.

Newly exposed defects, each filed separately:

- [#58](https://github.com/bddap-bot/photo-to-scene/issues/58): detail never checks a placed asset against its contract, and the resulting gate failures have no repair path.
- [#59](https://github.com/bddap-bot/photo-to-scene/issues/59): the facing gate treats contact with a furniture front as wall-mounting.
- [#60](https://github.com/bddap-bot/photo-to-scene/issues/60): refused contract-repair requests are dropped once detail's allowance is spent.
- [#61](https://github.com/bddap-bot/photo-to-scene/issues/61): an expired stage 5/6 budget still launches upstream repair until a materials scene is saved.
