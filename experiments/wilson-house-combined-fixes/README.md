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

No rerun has started. The #32 candidate at `fe82e96` was rejected in prerequisite
validation; execution awaits its corrected and accepted replacement.

| Measure | Published baseline | Combined-fixes rerun |
|---|---|---|
| Workflow | Continued run ending `428a8fb` | Pending prerequisite acceptance |
| Final scene gate | 0/10; 68 errors | Not run |
| In-run scene critic | Not run: gate blocked | Not run |
| Separate post-run critic | 7/10 | Not run |
| Detail objects finalized | 99/99 | Not run |
| Builder GOTO spend by stage | 5 object; 0 integrate/materials | Not run |
| Critic GOTO spend by stage | 5 tier; 0 integrate/materials | Not run |
| Reserved blockout repairs | No reserves in baseline | Not run |
| Refused repairs | 190 at caps; 23 invalid-stage requests separately | Not run |
| Recorded attempts | 386 | Not run |
| Summed attempt time | 118,534 s (32.9 h) | Not run |
| Final render call | 611 s | Not run |
| End-to-end elapsed time | Unavailable; last continuation 8 h 19 min | Not run |

Baseline evidence: `examples/wilson-house/report.md` and `scores.md`.
