# Wilson House: rerun on the combined workflow fixes

## Design recorded before execution

Requirement: rerun the public Wilson House example after #21, #23, and #32 are
verified, measuring the current workflow against the published baseline without
photograph-specific tuning.

The simplest design is one fresh end-to-end run, using the original full-resolution
Library of Congress photograph, unchanged prompts, driver, budgets, and builders.
Use a dedicated run directory and publish into a new `combined-fixes/` subdirectory
of `examples/wilson-house/`; retain the baseline renders and scores and link both
runs from the example report. Do not alter the mesh A/B or layout-oracle experiments.
No additional workflow structure or implementation is needed.

### Dependency rationale

- The original 6114×4842 photograph controls input quality; the repository's
  1529×1211 preview would change the comparison. Its attribution and download link
  are in `examples/wilson-house/ATTRIBUTION.md`.
- Codex supplies the workflow's builders and critics; record its version, selected
  model and reasoning effort rather than silently assuming the baseline settings.
- Nix supplies the existing Python, Blender and ImageMagick toolchain; Python checks
  contracts, Blender builds and renders scenes, and ImageMagick creates comparisons.
- The GPU admission gate is required before any GPU allocation on the shared 8 GB
  device. CPU rendering remains the baseline-compatible default. Do not introduce
  host-wide synthetic load or a workload benchmark into this experiment.
- Accepted #21, #23 and #32 fixes are start prerequisites. In particular, a landed
  but rejected candidate is not an accepted prerequisite.

### What the baseline measured

The published run continued across three workflow revisions, ending at
`428a8fbd94d5dc66d01e975c063a160f22a8f9d1`; it was not a fresh run of one revision.
It finalized 99/99 objects, but integration and materials each reported the same
68 observed spatial-contract errors. The final scene gate was 0/10 and no in-run
scene critic ran. A separate post-run materials critic scored the final render
7/10. This distinction must survive the comparison.

All five builder GOTOs were spent on `object:wall_w`. Five critic GOTOs were spent
before integration, three on tier non-verdicts. Later requests were refused 190
times; another 23 named no valid stage. There were 386 recorded attempts and
118,534 seconds (32.9 hours) of summed attempt time. The final render call took
611 seconds. Full end-to-end wall time was not retained; the last continuation
alone took 8 h 19 min. Do not present summed attempt time as elapsed wall time.

### Expected effects, to be checked rather than presumed

| Fix | Expected observable change |
|---|---|
| #21 | Annotation-only contract changes retain detail attempt budgets and accepted assets; actual spatial changes still invalidate them. |
| #23 | Tier non-verdicts retry criticism without consuming a GOTO; accepted spatial redirects receive the composition cross-check. |
| #26 | Integration and materials can each request a reserved blockout repair even after early GOTO exhaustion. |
| #27 | Contradictory support declarations fail at blockout with actionable measured errors, before downstream integration. |
| #29 | Input-photo references stay run-relative without manual publication rewrites. |
| #30 | Model liveness accounting inspects the call tree rather than scanning host-wide processes. |
| #31 | Tier retry regression checks are independent of watchdog timing; no direct quality improvement is assumed. |
| #32 | Starved CPU-bound children remain live while sleeping calls still reach the idle cutoff. Measure natural run outcomes; do not synthesize host load. |

### Execution and reporting protocol

1. Confirm prerequisite acceptance and record the exact workflow SHA, tool/model
   configuration, input checksum and dimensions, start time, and rendering device.
   Start with an empty dedicated run directory; do not seed old objects or contracts.
2. Execute the existing pipeline with its own attempt/GOTO limits. Keep complete
   attempt records, verdicts, logs, contracts and final assets. Observe all child
   processes to completion. Record stop/restart reasons and active elapsed intervals
   if infrastructure prevents one continuous run. Do not tune prompts or budgets.
3. Derive measures from the saved records and logs: final gate and error count,
   in-run critic score, per-stage attempts and stopped calls, GOTO spend split by
   builder/critic and source stage (including reserves), refused requests by stage,
   finalized objects, summed attempt seconds and actual elapsed time.
4. Publish the rerun's scores, contracts, renders, photograph/render side-by-side,
   and a labeled baseline/rerun visual comparison. View every published render
   before landing. Preserve baseline files and unrelated experiments.
5. Fill the table below beside this design and update the example report with
   evidence and limitations. File each newly exposed workflow defect separately;
   reference existing defects rather than duplicating them. A low score is a valid
   measured result, not a reason to tune the run or discard its candidate.

This is a single stochastic workflow comparison, not a causal ablation of each
fix. A different object count is an outcome, not grounds to force the old inventory.
No post-run critic result may substitute for an absent in-run scene verdict.

## Before/after results

Prerequisite #32 was accepted after correction `034bebfdc1b27d7f515052f33e2f7631c89718db`.
The fresh run uses that workflow revision and Codex CLI 0.156.0, with CPU rendering.
The original JPEG has SHA-256
`2f51726bfcb4f24445bb301131ad322f278d5f2412bfa4f926f6d602799a735a`.
The pipeline transcript reports `gpt-6-astra`, reasoning effort `none`; the
published baseline used `medium`. This configuration difference limits causal
attribution to workflow fixes. Start time: 2026-10-02 14:32:28 -07:00.
The completed result is described in the [rerun report](../../examples/wilson-house/combined-fixes/report.md). It includes four infrastructure continuations, the supervised stop of an over-budget repair branch, and final rendering of the saved best materials candidate. The measured workflow was not patched. The final-render wrapper also received SIGTERM; its surviving Blender child completed under direct observation, followed by verified comparison and publication steps.

| Measure | Published baseline | Combined-fixes rerun |
|---|---|---|
| Workflow | Continued run ending `428a8fb` | Fresh state on `034bebf`; four infrastructure continuations and supervised finalization |
| Final observed spatial gate | 0/10; 68 errors | Pass; zero errors for all 81 assets; footprint-observer caveat below |
| In-run scene critic | Not run: gate blocked | Integration 7/10; selected materials 6/10 |
| Separate post-run critic | 7/10 | Not run |
| Detail objects finalized | 99/99; mean 6.9/10; 33 at least 8 | 81/81; mean 6.67/10; 13 at least 8 |
| Builder GOTO spend by source stage | 5 object; 0 integration/materials | 2 blockout, 3 ceiling detail, 1 reserved integration repair |
| Critic GOTO spend by source stage | 5 tier; 0 integration/materials | 2 tier, 1 materials; final materials redirect stopped over budget |
| Reserved blockout repairs | No reserves in baseline | Integration reserve used; materials reserve unused |
| Refused repairs | 190 at caps; 23 invalid-stage requests separately | 61 at caps; 26 invalid-target requests separately |
| Recorded attempts | 386 | 360 scored records; 370 known sequences including 10 unscored |
| Summed attempt time | 118,534 s (32.9 h) | 99,501 s (27.64 h); excludes unscored work and final rendering |
| Driver-enforced model stops | Not separately derived in published summary | 1: fire-screen attempt 129 reached its 2,100 s bound |
| Final render call | 611 s | 524.74 s Blender; 621 s supervised finalization |
| End-to-end elapsed time | Unavailable; last continuation 8 h 19 min | 122,363 s (33 h 59 min 23 s); includes interruption gaps and supervised finalization |

Baseline evidence: `examples/wilson-house/report.md` and `scores.md`.

## Defects observed during execution

- [#35](https://github.com/bddap-bot/photo-to-scene/issues/35): a wrapped object
  inventory crashes declaration validation before a structured error is written;
  the next attempt receives only a generic gate-failed correction. Reproduced
  from blockout sequence 8, then recovered by the workflow in sequence 9.
- [#36](https://github.com/bddap-bot/photo-to-scene/issues/36): the per-object
  critic requests adjacent geometry owned by separate objects. Ceiling verdicts
  at sequences 14 and 20 requested separately owned cornice/trim, causing builder
  GOTOs 2 and 3 to blockout. This is not fixed or tuned within the measured run.
- [#37](https://github.com/bddap-bot/photo-to-scene/issues/37): appearance handoff metadata also restarted the ceiling at sequence 26 despite
  unchanged geometry and material wording; the recorded source/region-confidence
  exclusions do not cover these added ownership reminders. See the separately
  filed annotation-cache defect; the floor was reused in the same reentry.
- [#38](https://github.com/bddap-bot/photo-to-scene/issues/38): builder redirects
  bypass scored attempt/time records. Report actual elapsed time and stage-entry
  counts separately from the scored-record sum.
- [#39](https://github.com/bddap-bot/photo-to-scene/issues/39): the detail builder
  uses `target` rather than the driver's `stage` in its GOTO JSON; generic invalid
  stage feedback fails to correct the shape on retry (ceiling sequence 40).
- [#40](https://github.com/bddap-bot/photo-to-scene/issues/40): the inferred hidden
  wall W3 is scored against a window-and-curtain crop. The 0/10 at sequence 53 is
  a visual verdict against an unrelated target, not a failed machine gate.
- [#41](https://github.com/bddap-bot/photo-to-scene/issues/41): selecting rug
  attempt 45 restores its script and scored render but leaves attempt 46's
  overwritten texture live. Selected detail renders may not represent the
  dependency state subsequently consumed by integration. The same defect recurred
  when tablecloth attempt 172 (6/10) was restored after attempt 173 (5/10),
  retaining the latter attempt's rewritten texture. Display table G repeated it
  after tied 6/10 attempts 174 and 175.
- [#42](https://github.com/bddap-bot/photo-to-scene/issues/42): C's sequence 71
  preview renders normalized geometry without applying the contracted axis sizes;
  sequence 72 changes that convention as well as the mesh. The first critic's
  squat-back correction therefore evaluates different proportions from integration.
- [#43](https://github.com/bddap-bot/photo-to-scene/issues/43): firebox detail
  relabeling acquired the mesh screen's panels, rail and pulls despite a separate
  `firescreen` inventory entry. The latter builder generated those same visible
  components again at sequence 129; isolated checks do not reconcile ownership
  after identification changes. The same ownership overlap appears in display
  table G, whose scored asset includes a continuous floral drape despite its
  external-child ownership and a separate supported `tablecloth` object. This
  differs from the critic-driven requests in #36.
- [#44](https://github.com/bddap-bot/photo-to-scene/issues/44): accepted blockout
  revisions changed trim region width, spacing and height but retained obsolete
  numeric appearance instructions. The next detail builder found the contradiction
  and requested another spatial repair; declaration success did not establish
  consistency between the regions and those free-form instructions.
- [#45](https://github.com/bddap-bot/photo-to-scene/issues/45): integration
  replaces the measured L-shaped floor footprint with its enclosing rectangle,
  creating a false footprint failure despite matching main and recess regions.
  This is one contributor to the first integration gate's 70 errors, not evidence
  that the other asset mismatches are false. The reserved repair subsequently
  reached zero observed errors by declaring the enclosing rectangle while retaining
  the L-shaped floor geometry. That result does not resolve the observer defect
  or establish that its footprint comparison is correct.
- [#46](https://github.com/bddap-bot/photo-to-scene/issues/46): the integration critic
  emits nonexistent object stage IDs without a supplied inventory mapping. Sequence
  368 requested `object:foreground_bowl` instead of `object:bowl`; the driver rejected
  the route, and the exhausted integration loop advanced to materials without a
  corrected critic route. No critic GOTO was consumed.
- [#47](https://github.com/bddap-bot/photo-to-scene/issues/47): an expired
  integration/materials budget still permits earlier-stage repair work. After
  materials 369 saved a 6/10 candidate, its floorplan redirect entered sequence
  370 at 17,075 seconds on a 12,600-second clock. The over-budget branch was
  stopped under supervision; the existing final-render stage finalized the saved
  candidate. This is reported as supervised finalization, not a normal driver exit.
