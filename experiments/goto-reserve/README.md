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
