# Bounded blockout repair reserve

## Design and method

The control-flow requirement is that repeated early GOTO requests cannot consume
integration's or materials' final route to blockout. The baseline has independent
builder and critic pools of five accepted GOTOs each.

Evaluate retaining those pools and adding one blockout-only reserve for integration
and one for materials, each shared by builder and critic. Spend the ordinary pool
first. Persist reserve use before dispatch, including across process restarts.
Existing count files retain their meaning; an old exhausted checkpoint gains the
two reserves without resetting its counts. This permits at most 12 accepted GOTOs
from a fresh state, independent of object count. A single stage can consume both
ordinary pools but cannot consume the other whole-scene stage's reserve.

Use deterministic synthetic requests through the driver's builder and dispatch
loop. Saturate early builder and critic requests; then request blockout repeatedly
from integration and materials. Check delivered correction text, separate reserve
use, refusals of other targets, finite exhaustion, and state persistence across a
new process. Include checkpoints with separate counts and the older combined count.
Compare the baseline and candidate using the same request schedule. Run the full
control-flow regression suite and repository checks after implementation.

Per-object allowances and object-count scaling increase the worst-case work with
inventory size and still need protection against a single stage. A two-slot reserve
is the smallest additive policy that gives both whole-scene stages one independent
repair opportunity. One opportunity may be insufficient to fix a contract; this
measurement checks reachability and bounds, not rendered quality or spatial success.

## Results

The synthetic schedule repeatedly requests blockout from one early object and its
tier review, then from integration and materials. The candidate covers all four
builder/critic origin pairings for the two whole-scene stages across three starting
states (12 scenarios), each followed by a second process using the saved state.
The comparison removes the reserve branch and repeats one origin pairing per
starting state (three scenarios).

| Starting state | Accepted GOTOs without reserve | Accepted GOTOs with reserve | Integration repairs with reserve | Materials repairs with reserve | Extra GOTOs after candidate resume |
|---|---:|---:|---:|---:|---:|
| Fresh counts | 10 | 12 | 1 | 1 | 0 |
| Builder and critic counts both five | 0 | 2 | 1 | 1 | 0 |
| Legacy combined count ten | 5 | 7 | 1 | 1 | 0 |

Without the reserve neither whole-scene stage reached blockout. Legacy combined
counts retain the existing migration rule: charge the builder count and initialize
the critic count to zero. The five remaining ordinary critic GOTOs are consumed by
early requests in that scenario.

Repair dispatch preserves the requesting stage's synthetic footprint or region
correction text. A separate two-process scenario rejects a non-blockout target
without spending integration's reserve, lets materials use its reserve, then swaps
origins and verifies that only integration can spend a reserve. A failed reserve
state write stops before dispatch. Tier exhaustion still descends through all three
tiers. Spatial validators and their acceptance criteria are unchanged.

The first concurrent regression runs exposed a 15-second synthetic-process timeout
and an existing model-call timing assertion. The new synthetic harness uses a
300-second process deadline; exact accepted-count, feedback, and exhaustion
assertions remain in place. These are control-flow measurements with mocked stage
work, not timings or quality scores for reconstruction. The two reserves add at
most two backward transitions; each transition can rebuild downstream stages under
their existing attempt and model-call bounds. Normal stage execution and the
existing wallclock budget still constrain when those transitions can run.

The selected tradeoff is fixed additional work and independent whole-scene access,
with only one reserved repair per stage. Object-count scaling or per-object pools
would allow more repairs but increase the worst-case work with inventory size.
