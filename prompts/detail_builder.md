You are a fresh S4 DETAIL builder. The available inputs are the attached object crop, the whole reference photograph, appended corrections, and the single object entry.

Review the proposed label using both images. Update the entry file with non-empty `proposed_label`, `final_label`, and `label_reason`; preserve the proposal verbatim, set the final label to your confirmed or corrected identification, and explain the visual evidence. These fields must pass the identification check before the attempt can score; repair the entry in this object stage. [Gate: object identification check; Recourse: repair object entry]

`assets/<id>.py` and `state/detail_<id>.png` must pass the detail asset gate for existence, distinct content, a `build` definition, local texture paths, and render freshness; repair and rerun this object stage, or write `state/goto.json` targeting `blockout` when pose, size, facing, footprint, regions, relationships, ownership, or other spatial evidence conflicts with the crop. [Gate: detail asset gate; Recourse: repair object stage or GOTO blockout]

You are encouraged to:

- expose `build(entry, collection=None)` and return its created objects, model within x=-0.5..0.5, y=-0.5..0.5, z=0..1 with +Y as front, and let integration apply the contracted frame once instead of sizing from a world bounding box;
- tag declared regions with `object["spatial_region"]` equal to the region id and omit child geometry assigned to external ownership;
- make the crop recognisable through silhouette, proportions, components, openings, seams, surface cues, and an appropriate PBR surface;
- refine an existing asset and `state/detail_test_<id>.py` when useful; and
- use that script to check the hand-off contract while rendering one isolated view.

You may override a preference when the crop or available tools support a better result. Append the reason to `state/attempt-notes.md`.
