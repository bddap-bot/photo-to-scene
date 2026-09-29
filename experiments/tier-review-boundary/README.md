# Tier review invocation boundary

Investigation for [issue #28](https://github.com/bddap-bot/photo-to-scene/issues/28).

## Design

Investigate why cumulative-tier critics produce no usable verdict while object
critics complete. Start with the actual command-line invocation and delivered
inputs, then inspect response generation. No cause is assumed.

Use the public Library of Congress Wilson House photograph (highsm.17640) and
published reconstruction renders, or neutral synthetic images. Do not run the
reconstruction pipeline. Preserve the workflow's 2100 s wallclock and 1500 s idle
bounds, descendant CPU liveness, retry limits, and artifact restoration.

1. Compare the tier and object argument shapes through the real executable.
   Record prompt receipt and image attachment behavior before measuring inference.
2. Reproduce the first failing boundary. Change one variable at a time; keep the
   prompt, schema, images, model configuration, and transport fixed unless that
   variable is the controlled intervention. Retain raw transcripts separately.
3. If input delivery is correct, compare bounded tier and object responses, then
   isolate the differing variable. Count completed useful verdicts separately from
   empty or malformed responses, nonzero exits, and timeouts.
4. Verify the minimal repair with focused real calls and regression tests that
   fail without it. A usable verdict has a nonblank visual assessment, actionable
   corrections, and a valid stage; a score alone is insufficient.

Report the number of calls and elapsed times, exact intervention, and limits of
causal attribution. Historical published results describe five idle-bound stops
and one empty verdict in six resumed tier calls, versus 113 completed object
critics. Original raw call streams are not in the retained publication; historical
symptoms alone do not establish the trigger.

## Method and inputs

Design committed before measurement in `2c64d8a`. Calls used Codex CLI 0.156.0,
`gpt-6-astra`, medium reasoning, the original `verdict.schema.json`, and the
pipeline's actual `model()` and `critic()` functions. Each call used a fresh empty
work directory and retained the 2100 s wallclock / 1500 s idle limits and descendant
CPU liveness. Elapsed times include CLI startup and the wrapper's polling/cleanup.
There was no builder or whole-pipeline run.

The baseline prompt is `prompts/tier_critic.md` at `2c64d8a`. The experimental
invocation, with absolute paths substituted for the variables, was:

```bash
critic "$ROOT/verdict.json" detail -i "$REFERENCE" "$RENDER" < "$PROMPT"
```

This expands through the existing wrapper to `codex exec --ephemeral
--skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -C "$ROOT"
--output-schema "$SCHEMA" -o "$ROOT/verdict.json" -i "$REFERENCE" "$RENDER" -`.
The CLI's echoed input confirmed receipt of each intended prompt. Raw call logs,
input hashes, prompts, and verdicts were retained separately.

The reference was the full-resolution 6114×4842 RGB JPEG of
[highsm.17640](../../examples/wilson-house/ATTRIBUTION.md). All three retained tier
renders were 1019×807 RGBA PNGs. The large-tier input is byte-identical to the
[published PNG](../../examples/wilson-house/renders/tier-large.png); medium and
small are the retained renders from the same reconstruction. They depict almost
the same cumulative composition, so these are not three independent scenes.
Only the large-tier comparison is fully reproducible from the public inputs linked
here; the exact medium/small PNGs and object-control images are not included.

![Viewed large-tier input](../../examples/wilson-house/renders/tier-large.png)

| Input | SHA-256 |
|---|---|
| Reference | `2f51726bfcb4f24445bb301131ad322f278d5f2412bfa4f926f6d602799a735a` |
| Large tier | `9af9a9fd9ca0f5e2b79f6ee1f0b30c8cff0afd9b698c5adc9e521fa83bc5dc0a` |
| Medium tier | `17fd657dafe2be1d9f8c254a87e1c13c96244de044fe9fc86ed9c2e37469ffbf` |
| Small tier | `e2e65e882719970aeceb9314c915ca5b5400cb6b13bceb9f9dfad3181be63f49` |

The object control used a retained curtain crop (812×1675 RGB), isolated render
(800×1000 RGBA), and the same full-resolution reference, with the existing object
prompt and stage tag. It tests the real invocation path; because its prompt and
images differ, it is not the single-variable causal comparison.

## Results

Raw historical logs were subsequently located. They confirm six resumed tier
calls: five stopped at the idle bound, and one returned score 0 with an empty
summary, despite substantive corrections. The same log contains 113 completed
object critics. Those historical observations do not by themselves identify a
cause.

Each intervention below starts from the original large-tier call and changes only
the listed variable. The two successful prompt variants were then repeated on the
large render and tested on the other two retained renders.

| Condition | Calls | Useful schema verdicts | Elapsed seconds | Outcome |
|---|---:|---:|---|---|
| Original tier prompt/schema | 1 | 0 | 1509 | Stopped at 1500 s idle bound; no verdict |
| Remove output-schema option | 1 | 0 | 57 | Visual assessment in another JSON shape; no numeric score |
| Append scoring and summary instructions | 4 | 4 | 30, 33, 38, 39 | Large twice, medium, small |
| Append scoring instruction only | 4 | 4 | 36, 37, 37, 29 | Large twice, medium, small |
| Append summary instruction only | 1 | 0 | 1509 | Stopped at idle bound; no verdict |
| Move summary before score in schema properties | 1 | 0 | 1508 | Stopped at idle bound; no verdict |
| Existing per-object critic | 1 | 1 | 16 | Useful object review |

The scoring instruction was exactly `Score the visible composition from 0 to 10.`
The summary instruction was exactly `Write a nonempty summary of the visual
comparison and up to three concrete corrections.` The schema-order control moved
only the `summary` property ahead of `score`; constraints and required fields were
unchanged. The no-schema call searched unsuccessfully for a verdict format before
returning its own JSON shape; this was a diagnostic, not a usable pipeline repair.
An additional CLI startup probe with nonexistent image paths returned an explicit
missing-input verdict within a 15 s outer limit, exit 0; it is excluded from visual
review counts.

All eight scored-prompt tier verdicts contained nonblank visual summaries,
actionable corrections, and a valid `blockout` route. Their scores were 6 or 7;
none was a tier pass. Inspection against the supplied images confirmed useful
observations about the enlarged foreground sofa silhouette, fireplace opening,
rocking-chair proportions, and rug boundary. For example, the first score-only
summary was:

> The camera and major architectural boundaries fit well, and most furniture occupies the correct regions. The foreground sofa, rocking chair, and right armchair still need silhouette corrections before smaller detail work.

## Repair and limits

The workflow requires a numeric score without asking the tier critic to score.
Explicitly requesting that score produced useful verdicts in all eight tier calls
that included the instruction. The score-only comparison holds image bytes,
schema, executable, and model configuration fixed. The successful object prompt
also explicitly requests a 0–10 score.
Neither requesting a summary nor reordering the schema restored a verdict. The
minimal repair adds only the scoring sentence to the tier prompt.

These calls demonstrate a repair on the tested inputs, not the model's internal
decoding mechanism or a universal reliability rate.
The unmodified schema accepts empty summaries, and this experiment does not
replace semantic verdict validation. Historical failures cannot all be assigned
the same internal cause from their logs. No image resizing, model switch,
transport change, schema change, or extra retry is included in the repair. Call
bounds, descendant liveness, failure feedback, retry budgets, and best-artifact
restoration remain unchanged.

## Validation

At process priority −10, the unchanged full suite passed: 33 tests in 179.798 s,
exit 0:

```bash
nix-shell -p python3 --run 'python3 -m unittest -v tools/test-pipeline-control.py tools/test-prompt-policy.py tools/test-spatial-contract.py'
```

Three preceding ordinary runs failed the existing elapsed-time assertion (7, 9, and 7 s against 3–6 s);
the first also cut a stub at its 2 s idle limit. A separate PID-namespace run
failed the busy-child check. These four failed runs are retained as validation
limits; neither tests nor expectations were changed. The successful run included
all watchdog, descendant-liveness, retry, failure-feedback, and restoration tests.

Prompt-policy validation, Python compilation, shellcheck, and diff whitespace
checks also passed. The live baseline/repair contrast supplies the behavioral
regression evidence for this prompt-only change; no test asserts literal prompt
wording. Correctness, premise/taste, and cold-reader reviews found no implementation
blocker; their causal-wording and reproducibility feedback is reflected above.
