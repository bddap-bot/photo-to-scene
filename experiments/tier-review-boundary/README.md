# Tier review invocation boundary

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

## Results

Pending measurement.
