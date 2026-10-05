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

## First run: blocked at integration

The first run followed the design above on `af4f3d5`, at reasoning effort `none` for all
271 recorded model calls. It did not reach materials or a final render. Two newly
exposed workflow defects stopped it.

- [#51](https://github.com/bddap-bot/photo-to-scene/issues/51): the medium-tier
  critic routed critic GOTO 1 to `object:horse_plinth`, a small-tier object not yet
  built. After that single-object reentry, the driver went straight to integration.
  The other 21 small-tier objects and the small-tier review never ran. After the
  integration reserve's blockout reentry, the large-tier critic routed critic GOTO 2 to
  `object:sofa`, and the same skip repeated. Integration received 48 of 69 assets.
- [#52](https://github.com/bddap-bot/photo-to-scene/issues/52): the observed
  footprint gate now measures every placed triangle. That came to 2,916,424 triangles
  and a 177 MB measurement for just 48 assets. The shapely outline step then ran the job
  out of memory: about 23 GB resident plus 10 GB swap. The OOM killer stopped three
  consecutive integration entries (sequences 133–135) before any critic ran. Alone
  under a 12 GB address-space cap, the observer fails with `std::bad_alloc` after
  107 s. The combined-fixes run peaked at about 4 GB for the whole job.

Every further integration attempt re-runs that gate, so the run was halted there rather
than resumed again. No prompt, budget or candidate was changed.

| Measure | Combined-fixes run | Post-defects first run (blocked) |
|---|---|---|
| Workflow | `034bebf`, effort `none` | `af4f3d5`, effort `none` (271/271 calls) |
| Furthest stage | Final render after supervised finalization | Integration; observed gate never completed |
| Final observed spatial gate | Pass; 0 errors, 81 assets | Not reached (#52); 21 of 69 assets never built (#51) |
| In-run scene critic | Integration 7/10; materials 6/10 | None; tier reviews 8, 8, 7, 7 |
| Detail objects | 81/81 finalized; mean 6.67; 13 at least 8 | 44 of 66 observed objects finalized, mean 7.05, 15 at least 8; 3 inferred structures built unscored; 21 never built |
| Builder GOTOs | 2 blockout, 3 ceiling detail, 1 reserved integration | 5 detail-to-blockout contract repairs, 1 reserved integration repair; none from neighbour-ownership claims |
| Critic GOTOs | 2 tier, 1 materials | 2 tier-to-object routes (#51) |
| Refused repairs | 61 at caps; 26 invalid-target | 15 builder requests at the cap; 0 invalid targets; 0 critic route rejections |
| Recorded sequences | 360 scored, 10 unscored | 121 scored, 3 inferred unscored, 6 redirects recorded with time; 5 lost to interruptions |
| Summed attempt time | 99,501 s scored | 31,478 s scored + 254 s inferred + 3,162 s redirected |
| Model-call tokens | Not derived | 7,588,322 |
| Driver-enforced model stops | 1 | 0 |
| Infrastructure interruptions | 4, plus a final-render wrapper stop | 5: two host restarts and three OOM kills (#52) |

Observed fix effects, from one run: no validator crash (#35, #49); no invalid GOTO
target or invented critic ID (#39, #46); every builder redirect recorded with its
seconds (#38); inferred structure built without crops or critics (#40); and no
detail-sourced GOTO caused by a neighbour-ownership claim (#36, #43). The budget fixes
(#47, #48) were not reached.

The two host restarts were resumed at `detail`, which repeats the large-tier review.
The OOM kills were resumed at `integrate`. Each such continuation restarts the
in-memory stage 5/6 clock.

A complete measurement needs #51 and #52 fixed first. It will be a fresh run from an
empty directory, with its workflow revision recorded here before it starts.

## Second run: design recorded before execution

The complete measurement is a fresh run on workflow
`4d845833df4e084af59ff46f4fdf8c1647ddc6db`, which adds the fixes for #51 and #52 to `af4f3d5`.
Everything else in the design above stays fixed: the same photograph, `gpt-6-astra` at
reasoning effort `none` matching the combined-fixes run, an empty run directory, an
exported workflow tree, and no tuning.

Expected additional changes:

| Fix | Expected observable change |
|---|---|
| #51 | A critic GOTO to an object resumes the detail stage. Every object is built and every tier review runs before integration; a reentered object keeps its tier. |
| #52 | The observed footprint gate measures outline runs instead of triangles, so integration completes its gate and critic in bounded memory. No OOM interruption. |

The first run's records remain in its archive; none of its state seeds the second run.

## Second run: results

The second run started at an empty directory on `4d84583` and ended with a normal
driver `COMPLETE` after 56,613 s. It had no infrastructure interruption and needed no
supervised finalization. The [rerun report](../../examples/wilson-house/post-defects/report.md)
holds the full table, per-stage time and tokens, renders and evidence.

| Measure | Combined-fixes run | Post-defects second run |
|---|---|---|
| Workflow | `034bebf`, effort `none` | `4d84583`, effort `none` (587/587 calls) |
| Finalization | Supervised, after an over-budget redirect | Normal driver exit |
| Infrastructure interruptions | 4, plus a final-render wrapper stop | 0; 3 model calls failed on provider capacity |
| Final observed spatial gate | Pass; 0 errors, 81 assets | Fail; 69 errors at materials on a stale assembly (#54); integration 20 on each attempt |
| In-run scene critic | Integration 7/10; materials 6/10 | None: gate-rejected |
| Detail objects | 81/81; mean 6.67; 13 at least 8 | 66/66 observed; mean 7.29; 28 at least 8; 2 inferred |
| GOTO spend | 6 builder, 3 critic | 7 builder (4 facing repairs, 1 forward hand-off, 2 reserves); 5 critic, tier to object |
| Refused repairs | 61 at caps; 26 invalid targets | 52 at caps; 0 invalid targets |
| Summed attempt time | 99,501 s | 55,890 s (scored, inferred and redirected) |
| End-to-end elapsed | 122,363 s | 56,613 s |

Expected effects that held: no validator crash (#35, #49); no invalid target or
invented critic ID (#39, #46); every redirect recorded with its time (#38); inferred
structure unscored (#40); object reentries resuming detail with all assets built (#51);
observed gates finishing without an OOM (#52); and a normal exit (#47, #48). The stage
5/6 cap could not finalize until a saved materials scene existed, so upstream repair ran
after it expired.

Newly exposed defects, each filed separately:
[#53](https://github.com/bddap-bot/photo-to-scene/issues/53), forward hand-offs spend
repair GOTOs;
[#54](https://github.com/bddap-bot/photo-to-scene/issues/54), integration skips its
attempts after an upstream repair, leaving materials a stale assembly; and
[#55](https://github.com/bddap-bot/photo-to-scene/issues/55), blockout facing is never
checked against the room.
