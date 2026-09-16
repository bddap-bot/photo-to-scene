# Coarse-to-fine and contextual identification design

## Identification measurement

Two known hard cases were classified in fresh contexts before the workflow choice.

| Input | Perch on barrel | Oven mitt | Correct |
|---|---|---|---:|
| Crop only | table lamp | oven mitt | 1/2 |
| Whole photo only | decorative balance scale | slipper | 0/2 |
| Crop and whole photo | table lamp | oven mitt | 1/2 |

Crop plus whole-photo context is retained. It ties the best measured result while preserving crop detail and giving the object builder evidence about support, scale, and nearby objects. The root stage proposes a label; each object builder records `proposed_label`, `final_label`, and `label_reason`, and may correct the proposal.

## Coarse-to-fine loop

Objects are sorted by contracted footprint area and split deterministically into large, medium, and small thirds. Each tier is built in descending order, rendered cumulatively, and reviewed by a fresh composition critic before work descends to the next tier. Records include the tier that exposed an error.

## Perceptual-leverage increment

The selected run-analysis suggestion is asymmetric call allocation: settle the few large forms jointly in image space before spending calls on the long-tail detail sweep. The cumulative tier render makes this a workflow boundary rather than a prompt preference.

A second selected suggestion records confidence on semantic regions. Critics weight observed boundaries above inferred boundaries behind occlusions, avoiding false precision where a single view cannot establish topology.
