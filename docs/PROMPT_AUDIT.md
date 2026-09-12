# Prompt imperative audit

This table classifies every source line that contained an imperative before the prompt rewrite. Several dense source lines mixed classes, so each class receives its own row. “Gate / recourse” records the disposition of every literal `must`: checked requirements retain a gate and recourse, while ungated requirements became preferences.

| File | Line | Instruction | Class | Gate / recourse for `must` |
|---|---:|---|---|---|
| `blockout_builder.md` | 1 | Inspect the reference, floorplan, and corrections; write the object inventory and blockout outputs; use GOTO for an upstream defect; constrain I/O. | hand-off-invariant | — |
| `blockout_builder.md` | 1 | Populate the source-grounded frame, footprint, front, regions, relationships, ownership, and aperture fields. | checked-fact-with-recourse | Spatial declaration gate / revise blockout or GOTO floorplan. |
| `blockout_builder.md` | 1 | Build every entry with neutral geometry; use specified render and overlay commands; avoid yaw and lighting work. | method | The old “must build” had no corresponding gate and became a preference. |
| `blockout_builder.md` | 1 | Include decor and small visible items. | micro-geometry | — |
| `blockout_critic.md` | 1 | Inspect supplied images; return schema-valid, read-only JSON with stage fields. | hand-off-invariant | — |
| `blockout_critic.md` | 1 | Score alignment, ignore materials, and report three quantified corrections. | method | — |
| `detail_builder.md` | 1 | Limit inspection to the crop and one entry. | method | — |
| `detail_builder.md` | 3 | Expose `build`, use normalized coordinates, return objects, tag regions, and respect external ownership. | hand-off-invariant | The asset gate checks existence, distinctness, a `build` definition, local texture paths, and render freshness; ungated coordinate and tagging details became preferences; repair the object stage or GOTO blockout. |
| `detail_builder.md` | 3 | Avoid world-bbox sizing; select local textures or procedural materials. | method | — |
| `detail_builder.md` | 3 | Model silhouettes, structural parts, seams, openings, and surface cues as geometry. | micro-geometry | — |
| `detail_builder.md` | 5 | Refine existing files; run the prescribed Blender command; verify and stop after one render. | method | — |
| `detail_builder.md` | 5 | Render at the prescribed resolution, samples, denoising, and studio setup. | style | — |
| `detail_builder.md` | 7 | Apply corrections, use a canonical GOTO target for spatial changes, and constrain I/O. | hand-off-invariant | The old “detail must not mutate” is covered by the asset/observed gates; repair or GOTO blockout. |
| `detail_critic.md` | 1 | Inspect supplied images; return schema-valid, read-only JSON with stage fields. | hand-off-invariant | — |
| `detail_critic.md` | 1 | Score recognition and report three fixes. | method | — |
| `detail_critic.md` | 1 | Weight shape, proportions, components, and material read. | micro-geometry | — |
| `final_builder.md` | 1 | Open the best scene without changing it; produce both required final artifacts; constrain I/O. | hand-off-invariant | — |
| `final_builder.md` | 1 | Use the prescribed Blender and ImageMagick commands, dimensions, samples, threads, denoising, and layout. | method | — |
| `floorplan_builder.md` | 1 | Inspect inputs; write floorplan data and drawing files; constrain I/O. | hand-off-invariant | — |
| `floorplan_builder.md` | 1 | Record the room, fixed features, camera, scale, dimensions, and evidence in metres. | checked-fact-with-recourse | — |
| `floorplan_builder.md` | 1 | Infer from perspective and standard dimensions; render the prescribed diagram with Blender. | method | — |
| `floorplan_critic.md` | 1 | Inspect inputs; return schema-valid, read-only JSON with stage fields. | hand-off-invariant | — |
| `floorplan_critic.md` | 1 | Score photographic consistency and report three numerical corrections. | method | — |
| `identify_builder.md` | 1 | Inspect inputs; correct the inventory; write all crops and the contact sheet; constrain I/O. | hand-off-invariant | — |
| `identify_builder.md` | 1 | Use exact crop boxes, 2× filtering, ImageMagick, and specified labels and tile sizes. | method | — |
| `identify_critic.md` | 1 | Inspect inputs; return schema-valid, read-only JSON with correction arrays and stage. | hand-off-invariant | — |
| `identify_critic.md` | 1 | Score label accuracy and completeness against the photograph. | method | — |
| `integrate_builder.md` | 1 | Read contracts and assets; write assembly and observed-state outputs; use GOTO for upstream defects; constrain I/O. | hand-off-invariant | — |
| `integrate_builder.md` | 1 | Round-trip footprints, fronts, regions, relationships, ownership, and apertures. | checked-fact-with-recourse | Observed spatial-contract gate / GOTO blockout or responsible object stage. |
| `integrate_builder.md` | 1 | Apply one affine placement; avoid independent fitting; preserve materials; use prescribed rendering and overlay commands. | method | — |
| `integrate_builder.md` | 1 | Eliminate visible floating, intersections, gaps, and duplicate child geometry. | micro-geometry | — |
| `integrate_critic.md` | 1 | Inspect inputs; return schema-valid, read-only JSON with correction stages and arrays. | hand-off-invariant | The old `top_stage must match` relationship is not schema-checked and became a preference. |
| `integrate_critic.md` | 1 | Score photographic fit and report three fixes. | method | — |
| `materials_builder.md` | 1 | Read inputs; write the material scene, render, and final observations; use GOTO for upstream defects; constrain I/O. | hand-off-invariant | — |
| `materials_builder.md` | 1 | Preserve apertures and other spatial invariants after materials. | checked-fact-with-recourse | Observed spatial-contract gate / repair materials or GOTO the owning stage. |
| `materials_builder.md` | 1 | Preserve PBR materials; choose maps, procedural surfaces, shell treatment, lighting, exposure, and rendering settings. | style | — |
| `materials_critic.md` | 1 | Inspect inputs; return schema-valid, read-only JSON with correction stages and arrays. | hand-off-invariant | The old `top_stage must match` relationship is not schema-checked and became a preference. |
| `materials_critic.md` | 1 | Score the rendered outcome against the photograph and report three fixes. | method | — |
| `materials_critic.md` | 1 | Deduct for synthetic surfaces and visible artifacts. | style | — |

## Literal hard-instruction counts

Counts are occurrences of the word `must`, the mechanically enforced hard-language marker.

| Prompt | Before | After |
|---|---:|---:|
| `blockout_builder.md` | 1 | 1 |
| `blockout_critic.md` | 0 | 0 |
| `detail_builder.md` | 2 | 1 |
| `detail_critic.md` | 0 | 0 |
| `final_builder.md` | 0 | 0 |
| `floorplan_builder.md` | 0 | 0 |
| `floorplan_critic.md` | 0 | 0 |
| `identify_builder.md` | 0 | 0 |
| `identify_critic.md` | 0 | 0 |
| `integrate_builder.md` | 0 | 1 |
| `integrate_critic.md` | 1 | 0 |
| `materials_builder.md` | 0 | 1 |
| `materials_critic.md` | 1 | 0 |
| **Total** | **5** | **4** |
