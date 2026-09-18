# Wilson House worked example

RESUMABLE: 5/99 detail objects finalized; active stage `object:desk`, attempt 1, sequence 171. Final scene gate and critic scores are not yet measured; latest available visual critic: 7/10 (`object:sofa`).

The Library of Congress photograph is the reconstruction reference; [ATTRIBUTION.md](ATTRIBUTION.md) gives the credit, rights statement, and full-resolution link. The pipeline received the 6114×4842 full-resolution JPEG. The repository source is the supplied 1529×1211 copy.

## Workflow provenance

The run began with an empty work directory on `05b4bad57d40f982c0ca4209af511e90c8f2454c`. The generic asset builder was seeded by the driver. The scene-agnostic detail prompt fix `ce3c95c9ca51d8a5663cbbe170d00781220e9714` preceded the saved detail checkpoint.

This continuation uses the published main tip `ed4bc7e691ec081840040e3acc7918af97c712b5`, including the footprint tiers, whole-photo detail context, identification review, and separate builder/critic GOTO allowances. The existing contracts, completed attempts, and artifacts were retained. This is a continuation across workflow revisions, not a fresh measurement of one revision. The published prompts, driver, contracts, and budgets were not tuned for the photograph.

## Attempt measurements

The complete per-attempt table below separates machine gates from visual judgments. A passing gate is represented as 10/10, a failure as 0/10, and an unavailable measurement as a dash. Seconds are the driver-recorded elapsed time for each completed attempt; interrupted attempts are not included. The change column summarizes the correction supplied to that attempt, not a claim that the correction succeeded. Full correction context and resulting findings are retained in [scores.md](scores.md).

| Stage | Attempt | Gate score | Critic score | Seconds | What changed |
|---|---:|---:|---:|---:|---|
| floorplan | 1 | — | 5/10 | 272 | Initial entry or forward rebuild. |
| floorplan | 2 | — | 7/10 | 314 | Reconcile camera framing with the window-wall furniture positions. The specified projection places the draped-table center beyond the right image edge and the orange chair farther outside, whereas both are visible in the photograph.… |
| floorplan | 3 | — | 7/10 | 424 | Refine the draped table and orange chair elevations and depth. Their projected floor extents reach roughly y=1214 and y=1329, while the photograph places their visible bases around y=1080 and y=1160. Preserve the orange chair’s… |
| blockout | 1 | 10/10 | 6/10 | 570 | Initial entry or forward rebuild. |
| blockout | 2 | 10/10 | 6/10 | 218 | Lower the rear ceiling corner by approximately 3% of image height to align the wall–ceiling junction with the photograph. |
| blockout | 3 | 10/10 | 7/10 | 258 | Replace the rectangular curtain blocks with long, gathered drapes and diagonal sweeps toward the tiebacks |
| identify | 1 | — | 8/10 | 522 | Initial entry or forward rebuild. |
| object:wall_w | 1 | 0/10 | — | 56 | Initial entry or forward rebuild. |
| blockout | 1 | 10/10 | 7/10 | 137 | Initial entry or forward rebuild. |
| blockout | 2 | 10/10 | 7/10 | 258 | Raise the rear ceiling corner by approximately 25 pixels in the 1019×807 render, aligning the adjoining cornice edges with the photograph. |
| blockout | 3 | 10/10 | 7/10 | 270 | Reduce the foreground sofa’s oversized rounded back: its lower outline extends roughly 25–35 pixels too low in the 1019-pixel-wide overlay. Lower the crest of its right foreground arm by about 20 pixels. |
| identify | 1 | — | 8/10 | 252 | Initial entry or forward rebuild. |
| object:wall_w | 1 | 10/10 | 3/10 | 162 | Initial entry or forward rebuild. |
| blockout | 1 | 10/10 | 7/10 | 245 | The appended correction requires a projecting chimney breast and raised architectural trim. The supplied plaster body is confined to world X=-0.25..0 and assigns children to external ownership. The visible room-side projection exceeds… |
| blockout | 2 | 10/10 | 7/10 | 324 | Lower the rear ceiling corner approximately 25 pixels in the 1019×807 render to match the photograph, adjusting the adjoining cornice slopes. |
| blockout | 3 | 10/10 | 8/10 | 246 | Lower the window cornice toward the right edge by approximately 4% of image height, and add the photograph’s outer-right tied-back curtain panel. |
| identify | 1 | — | 9/10 | 195 | Initial entry or forward rebuild. |
| object:wall_w | 1 | 10/10 | 6/10 | 224 | Initial entry or forward rebuild. |
| blockout | 1 | 10/10 | 7/10 | 305 | The requested portrait-oriented chimney panel conflicts with its contracted 2.38 m width and 2.05 m height. Changing its proportions and widening rails requires revised spatial regions. |
| blockout | 2 | 10/10 | 7/10 | 366 | Flatten the ceiling: remove the diagonal facet running from the upper-right area toward the back cornice |
| blockout | 3 | 10/10 | 8/10 | 206 | Raise the rear ceiling/cornice junction by approximately 20–25 pixels at the 1019-pixel overlay width |
| identify | 1 | — | 8/10 | 171 | Initial entry or forward rebuild. |
| object:wall_w | 1 | 10/10 | 7/10 | 258 | Initial entry or forward rebuild. |
| blockout | 1 | 10/10 | 7/10 | 236 | Requested panel layout changes conflict with declared spatial region envelopes. |
| blockout | 2 | 10/10 | 7/10 | 244 | Move the foreground left table and its bowl rightward and downward in the image. The bowl should center near 17% image width and 85% image height |
| blockout | 3 | 10/10 | 8/10 | 264 | Raise the ceiling/cornice junction at the rear wall corner approximately 8–10 pixels in the 1019×807 comparison. |
| identify | 1 | — | 10/10 | 187 | Initial entry or forward rebuild. |
| object:wall_w | 1 | 10/10 | 7/10 | 111 | Initial entry or forward rebuild. |
| blockout | 1 | 10/10 | 7/10 | 251 | The builder GOTO cap is reached. Continue and complete the current stage without another GOTO. |
| blockout | 2 | 10/10 | 7/10 | 282 | Reduce the fireplace’s dark opening and lower its top: the photograph places it roughly at x=17–33%, y=63–79%, while the blockout opening extends higher and farther left. Preserve the surrounding masonry. |
| blockout | 3 | 10/10 | 7/10 | 213 | Lower the ceiling/cornice junction at the rear wall corner by approximately 2% of image height to match the photograph. |
| identify | 1 | — | 10/10 | 135 | Initial entry or forward rebuild. |
| object:wall_w | 1 | 10/10 | 7/10 | 159 | Initial entry or forward rebuild. |
| object:wall_w | 2 | 10/10 | 7/10 | 67 | GOTO cap fallback: retained the fresh, contract-valid attempt-1 asset after the builder repeated the same spatial recourse. |
| object:floor | 1 | 10/10 | 6/10 | 155 | Initial entry or forward rebuild. |
| object:floor | 2 | 10/10 | 6/10 | 64 | GOTO cap fallback: retained the fresh, contract-valid attempt-1 asset after the builder repeated a request for the separately owned rug. |
| object:rug | 1 | 0/10 | — | 176 | Initial entry or forward rebuild. |
| object:rug | 2 | 10/10 | 8/10 | 77 | asset check failed: texture reference /rug_albedo.png is outside ROOT/textures |
| object:sofa | 1 | 10/10 | 6/10 | 293 | Initial entry or forward rebuild. |
| object:sofa | 2 | 10/10 | 6/10 | 122 | GOTO cap fallback: retained the fresh, contract-valid attempt-1 asset after the builder repeated a spatial-region recourse. |
| object:ceiling | 1 | 10/10 | 7/10 | 131 | Initial entry or forward rebuild. |
| object:ceiling | 2 | 10/10 | 7/10 | 92 | GOTO cap fallback: retained the fresh, contract-valid attempt-1 asset after repeated out-of-region cornice recourse. |
| object:north_above | 1 | 10/10 | 2/10 | 154 | Initial entry or forward rebuild. |
| object:north_above | 2 | 10/10 | 2/10 | 79 | GOTO cap fallback: retained the fresh, contract-valid attempt-1 asset after the builder requested externally owned ornament outside the declared plaster region. |
| object:mantel | 1 | 0/10 | — | 56 | Initial entry or forward rebuild. |
| object:mantel | 1 | 10/10 | 6/10 | 224 | Initial entry or forward rebuild. |
| object:mantel | 2 | 10/10 | 6/10 | 76 | GOTO cap fallback: retained the fresh, contract-valid attempt-1 asset after the builder requested separately owned marble outside the declared mantel regions. |
| object:sheer_1 | 1 | 0/10 | — | 180 | Initial entry or forward rebuild. |
| object:sheer_1 | 2 | 0/10 | — | 93 | asset check failed: texture reference /sheer_1_lace_density.png is outside ROOT/textures |
| object:cornice_n | 1 | 10/10 | 7/10 | 148 | Initial entry or forward rebuild. |
| object:cornice_n | 2 | 10/10 | 6/10 | 146 | Increase the height and relief of the ornamental band relative to the upper rails. |
| object:desk | 1 | 10/10 | 0/10 | 63 | GOTO cap fallback: no contract-valid detail asset exists because the visible desk apron has no owned spatial region. |
| object:desk | 2 | 10/10 | 0/10 | 1 | GOTO cap fallback: no contract-valid detail asset exists because the visible desk apron has no owned spatial region. |
| object:portrait | 1 | 0/10 | — | 269 | Initial entry or forward rebuild. |
| object:portrait | 2 | 0/10 | — | 89 | asset check failed: texture reference /portrait_source.png is outside ROOT/textures |
| object:rocker | 1 | 0/10 | — | 76 | Initial entry or forward rebuild. |
| object:rocker | 2 | 0/10 | — | 83 | asset check failed: state/detail_rocker.png is not a fresh render from this builder attempt |
| object:drape_0 | 1 | 0/10 | — | 69 | Initial entry or forward rebuild. |
| object:drape_0 | 2 | 0/10 | — | 70 | asset check failed: state/detail_drape_0.png is not a fresh render from this builder attempt |
| object:baseboard_n | 1 | 0/10 | — | 70 | Initial entry or forward rebuild. |
| object:baseboard_n | 2 | 0/10 | — | 60 | asset check failed: assets/baseboard_n.py does not exist |
| object:drape_2 | 1 | 10/10 | 6/10 | 168 | Initial entry or forward rebuild. |
| object:drape_2 | 2 | 0/10 | — | 74 | Make the upper drape fuller with broad, irregular folds and a deeper sagging sweep into the gather |
| object:north_left | 1 | 10/10 | 5/10 | 88 | Initial entry or forward rebuild. |
| object:north_left | 2 | 0/10 | — | 62 | Add the prominent narrow gold perimeter molding, including its beveled profile and darker inner border. |
| object:sheer_0 | 1 | 0/10 | — | 132 | Initial entry or forward rebuild. |
| object:sheer_0 | 2 | 10/10 | 7/10 | 120 | asset check failed: texture reference /sheer_1_lace_density.png is outside ROOT/textures |
| object:north_below | 1 | 10/10 | 8/10 | 185 | Initial entry or forward rebuild. |
| object:curtain_rail | 1 | 10/10 | 6/10 | 156 | Initial entry or forward rebuild. |
| object:curtain_rail | 2 | 0/10 | — | 47 | Replace the uniform braided pattern with broader, varied floral and scroll relief, giving the rail a less regular silhouette. |
| object:firebox | 1 | 0/10 | — | 74 | Initial entry or forward rebuild. |
| object:firebox | 2 | 10/10 | 7/10 | 133 | asset check failed: assets/firebox.py does not exist |
| object:gold_chair | 1 | 10/10 | 7/10 | 226 | Initial entry or forward rebuild. |
| object:gold_chair | 2 | 10/10 | 7/10 | 200 | Restore the exposed turned wooden arm supports and thicker decorated front rail |
| object:orange_chair | 1 | 0/10 | — | 71 | Initial entry or forward rebuild. |
| object:orange_chair | 2 | 0/10 | — | 83 | asset check failed: assets/orange_chair.py does not exist |
| object:fire_screen | 1 | 10/10 | 8/10 | 156 | Initial entry or forward rebuild. |
| object:drape_1 | 1 | 10/10 | 5/10 | 116 | Initial entry or forward rebuild. |
| object:drape_1 | 2 | 0/10 | — | 75 | Lower the gathering point to roughly 40% of the curtain height and deepen the upper panel’s curved, hanging sweep. |
| object:display_table | 1 | 0/10 | — | 90 | Initial entry or forward rebuild. |
| object:display_table | 2 | 0/10 | — | 88 | asset check failed: assets/display_table.py does not exist |
| object:red_chair | 1 | 0/10 | — | 88 | Initial entry or forward rebuild. |
| object:red_chair | 2 | 0/10 | — | 74 | asset check failed: assets/red_chair.py does not exist |
| object:bookcase | 1 | 0/10 | — | 61 | Initial entry or forward rebuild. |
| object:bookcase | 2 | 0/10 | — | 70 | asset check failed: assets/bookcase.py does not exist |
| object:round_table | 1 | 0/10 | — | 49 | Initial entry or forward rebuild. |
| object:round_table | 2 | 0/10 | — | 82 | asset check failed: assets/round_table.py does not exist |
| object:walking_cane | 1 | 10/10 | 8/10 | 162 | Initial entry or forward rebuild. |
| object:desk_bowl | 1 | 10/10 | 8/10 | 139 | Initial entry or forward rebuild. |
| object:radiator | 1 | 10/10 | 6/10 | 144 | Initial entry or forward rebuild. |
| object:radiator | 2 | 10/10 | 8/10 | 102 | Enlarge and space out the dark openings to match the crop’s visible rows of holes. |
| object:hearth | 1 | 10/10 | 7/10 | 108 | Initial entry or forward rebuild. |
| object:hearth | 2 | 10/10 | 7/10 | 93 | Replace the directional wood-like streaks with subtle dark stone variation and a smoother surface. |
| object:fireplace_fender | 1 | 10/10 | 4/10 | 272 | Initial entry or forward rebuild. |
| object:fireplace_fender | 2 | 10/10 | 4/10 | 248 | Thicken the horizontal rails substantially and make the turned posts shorter and fuller, with prominent ball finials and bulbous lower bodies. |
| object:tablecloth | 1 | 10/10 | 5/10 | 227 | Initial entry or forward rebuild. |
| object:tablecloth | 2 | 10/10 | 6/10 | 180 | Add deeper, irregular vertical folds and a softer tabletop-to-hanging transition |
| object:window_sill_right | 1 | 10/10 | 7/10 | 153 | Initial entry or forward rebuild. |
| object:window_sill_right | 2 | 10/10 | 7/10 | 92 | Increase the fascia height beneath the top lip to match the broader flat wooden band in the crop. |
| object:lamp_table | 1 | 10/10 | 4/10 | 265 | Initial entry or forward rebuild. |
| object:lamp_table | 2 | 10/10 | 4/10 | 244 | Increase the depth of the apron/drawer section beneath the tabletop and make its small round hardware more prominent. |
| object:north_right | 1 | 10/10 | 3/10 | 265 | Initial entry or forward rebuild. |
| object:north_right | 2 | 10/10 | 5/10 | 253 | Shape the upper fabric into a diagonal sweep gathered at a tieback around two-fifths of the visible height, then let the lower folds fan outward. |
| object:window_sill_left | 1 | 10/10 | 7/10 | 121 | Initial entry or forward rebuild. |
| object:window_sill_left | 2 | 10/10 | 6/10 | 227 | Increase the fascia height relative to its length, retaining a broad, mostly flat central face. |
| object:stool | 1 | 10/10 | 6/10 | 191 | Initial entry or forward rebuild. |
| object:stool | 2 | 10/10 | 7/10 | 316 | Shorten and thicken the legs, with fuller curved knees and broader carved feet. |
| object:globe | 1 | 10/10 | 7/10 | 385 | Initial entry or forward rebuild. |
| object:globe | 2 | 10/10 | 7/10 | 306 | Reshape the pedestal into a smooth upper pear-shaped turning above one rounded, fluted lower bulb |
| object:desk_papers | 1 | 10/10 | 6/10 | 191 | Initial entry or forward rebuild. |
| object:desk_papers | 2 | 10/10 | 7/10 | 184 | Add visibly offset sheets with irregular, slightly curled edges and a thicker layered profile along the front and right sides. |
| tier:large | 1 | — | 0/10 | 145 | Integrated footprint tier before descending. |
| blockout | 1 | 10/10 | 8/10 | 234 | blockout: Reduce the foreground table’s rightward extent. Its visible edge reaches roughly 51% of image width at the bottom, versus 27% in the reference, obscuring too much of the sofa. |
| identify | 1 | — | 9/10 | 143 | Initial entry or forward rebuild. |
| object:ceiling | 1 | 10/10 | 7/10 | 110 | Initial entry or forward rebuild. |
| object:ceiling | 2 | 10/10 | 7/10 | 268 | Add the deep, layered cornice with a repeating carved gold-brown band beneath the ceiling edge. |
| object:floor | 1 | 10/10 | 6/10 | 110 | Initial entry or forward rebuild. |
| object:floor | 2 | 10/10 | 8/10 | 400 | Add the large rectangular rug covering most of the visible floor, with a dense red, navy, and cream field and layered floral borders. |
| object:rug | 1 | 10/10 | 8/10 | 114 | Initial entry or forward rebuild. |
| object:wall_w | 1 | 10/10 | 7/10 | 127 | Initial entry or forward rebuild. |
| object:wall_w | 2 | 10/10 | 6/10 | 266 | Extend the chimney-breast panel downward toward mantel height |
| object:sofa | 1 | 10/10 | 6/10 | 198 | Initial entry or forward rebuild. |
| object:sofa | 2 | 10/10 | 7/10 | 247 | Thicken the back’s top roll substantially and blend it into the padded back |

## GOTO history

- rejected origin=builder requested= reason=target is not in canonical stage set
- cap request ignored origin=builder requested=blockout reason=wall_w has a facing/frame conflict: its broad room-facing plaster surface is at world X=0, with normal (+1,0), but front_xy and frame.y_axis_xy are (0,-1), tangent to that surface. The declared local front therefore describes the narrow end of the wall. Correct the blockout frame before detail construction, preserving the existing world envelope and corrected shell height. Proposed frame: origin_xyz [-0.125,3.4,0], x_axis_xy [0,-1], y_axis_xy [1,0], size_xyz [6.8,0.25,3.7139255], front_xy [1,0]. Preserve body region bounds, floor support, and external child ownership; regenerate ordered footprint from the corrected frame. Reissue the object entry after validating the contract. This request uses the canonical stage field to repair the previous rejected GOTO.
- count=1 origin=builder stage=blockout reason=Spatial facing conflict in wall_w: the broad room-facing plaster plane at world X=0 has normal (+1,0), but the supplied front_xy and frame.y_axis_xy are (0,-1), tangent to that plane. Correct the frame in blockout and reissue the entry before detail construction. Preserve the existing world bounds, corrected height, body region, floor support, and external child ownership. The previous routing request was ignored due to the driver re-entry cap; this spatial conflict remains unresolved.
- count=2 origin=builder stage=blockout reason=The appended correction requires a projecting chimney breast and raised architectural trim. The supplied plaster body is confined to world X=-0.25..0 and assigns children to external ownership. The visible room-side projection exceeds that body region and footprint; incorporating externally owned trim conflicts with ownership. The corrected facing is already consistent with the crop.
- count=3 origin=builder stage=blockout reason=The requested portrait-oriented chimney panel conflicts with its contracted 2.38 m width and 2.05 m height. Changing its proportions and widening rails requires revised spatial regions.
- count=4 origin=builder stage=blockout reason=Requested panel layout changes conflict with declared spatial region envelopes.
- count=5 origin=builder stage=blockout reason=Appended corrections require spatial changes: the central panel bottom is fixed at z=1.74 m with a declared 0.16 m mantel gap, and chimney projection is fixed at 0.38 m. Lowering the panel and deepening the breast would violate the supplied region contract.
- cap reached origin=builder requested=floorplan reason=The appended correction calls for lowering the central panel and deepening the chimney breast, but the supplied wall_w contract fixes the panel bottom at z=1.74 m with a 0.16 m gap above the 1.58 m mantel, and fixes chimney projection at 0.38 m. The latter is also fixed_features.chimney.size_m[0] in floorplan.json. Implementing the requested spatial changes requires coordinated revision of these dimensions and their camera projection; changing only the detail mesh would violate the declared regions. Return to floorplan to resolve the projection conflict before rebuilding blockout.
- cap reached origin=builder requested=blockout reason=Appended crop corrections require changing explicit spatial region envelopes. Current detail already implements the contracted central panel bottom, width, margins, near-side width and maximum cornice projection; further directional changes cannot be performed within those envelopes.
- cap reached origin=builder requested=blockout reason=The appended correction requires a large patterned rug covering most of the floor, but the supplied Wood floor contract assigns children to external ownership and declares only a body region ending at z=0. Adding the rug within this detail asset would invent ownership, footprint and elevation outside the declared region.
- cap reached origin=builder requested=blockout reason=The appended sofa silhouette corrections conflict with the authoritative exact region meshes. The current back is a separate narrow crest over a slab-shaped rear panel, and the rolled arms are tall narrow ellipsoids. The detail test enforces exact region bounds. Revise these spatial regions before rebuilding detail rather than silently changing the contracted padding envelopes.
- cap reached origin=builder requested=blockout reason=Deep perimeter cornice beneath ceiling conflicts with the sole exact slab region and rear minimum bound.
- cap reached origin=builder requested=blockout reason=Direct floor contact conflicts with the elevated above-window body in the crop and authoritative mesh.
- cap reached origin=builder requested=blockout reason=The requested ornament conflicts with ownership.children=external and the sole declared plaster body region.
- cap reached origin=builder requested=blockout reason=Shelf begins at z=1.48 m while both piers and carved_frieze end at z=1.45 m, leaving a 0.03 m unassigned gap. The crop shows continuous stepped supporting mouldings between frieze and shelf. Filling the gap requires changing region extents or adding an owned region.
- cap request ignored origin=builder requested= reason=The supplied regions leave an unsupported 0.03 m gap between the pier/frieze tops at z=1.45 and shelf bottom at z=1.48. The crop shows continuous supporting cornice molding in this location. With children externally owned, detail cannot assign this missing connecting geometry without resolving its region and ownership.
- cap reached origin=builder requested=blockout reason=Requested marble inner surround lies outside the four declared mantel regions; resolve regions and ownership before detail refinement.
- cap reached origin=builder requested=blockout reason=The crop shows a broad continuous dark wooden panel with raised carved framing beneath the studded near tabletop edge. The desk contract declares only a top at world Z=0.74..0.80 and four narrow corner legs below it. No region contains the visible panel between those legs, and children are externally owned. Modeling that panel in the detail stage would introduce unassigned geometry or incorrectly tag it as a leg/top.
- cap reached origin=builder requested=blockout reason=Isolated detail render reproduces the accepted region geometry but exposes a crop conflict in runner curvature and floor-support topology. This requires a spatial correction, not a material/detail adjustment.
- cap request ignored origin=builder requested=blockout reason=Runner and leg regions conflict with the crop: runners curl up to seat height and legs extend below them to the floor. The crop shows shallow broad wooden runners supporting the leg ends.
- cap reached origin=builder requested=blockout reason=The supplied runner and leg regions conflict with the crop: runners rise to 0.423338 m, above the seat underside at 0.397800 m, and legs extend to floor level below the runner rails. The crop shows shallow broad runners beneath the leg ends. The existing isolated render confirms excessive runner curvature.
- cap request ignored origin=builder requested=blockout reason=Runner and leg regions conflict with the crop: runners curl up to seat height and legs extend below the rails. The crop shows shallow broad runners beneath the leg ends.
- cap reached origin=builder requested=blockout reason=The supplied regional meshes conflict with the crop silhouette. A fresh isolated render preserving the contracted frame shows a central gather and a strongly diagonal tail, whereas the crop shows a gather near the left edge and a near-vertical hanging tail. Detail material work cannot repair those spatial relationships without revising the declared meshes and envelopes.
- cap request ignored origin=builder requested=blockout reason=Supplied spatial meshes conflict with the crop: central gather, upper fabric fanning to both sides, and strongly slanted lower tail instead of a left-side gather, dominant rightward diagonal sweep, and nearly vertical tail.
- cap reached origin=builder requested=blockout reason=The supplied spatial meshes conflict with the crop: the gather is near the center of the upper fan and the long tail slants strongly sideways, whereas the crop shows a left-side gather, a nearly vertical tail, and a dominant sweep upward to the right. A new render alone cannot repair this spatial conflict.
- cap request ignored origin=builder requested=blockout reason=The supplied spatial meshes conflict with the crop silhouette: central gather, two-sided upper fan, and strongly slanted lower tail instead of a left-side gather, dominant rightward sweep, and nearly vertical tail.
- cap reached origin=builder requested=blockout reason=Crop/object evidence mismatch: the crop shows furniture and a perforated under-window panel with horizontal trim, but no identifiable floor junction or baseboard. The contract assigns this visible extent to a 7.2 m wide, 0.17 m high floor-supported strip. Reconcile the source assignment before detailing the visible panel as that strip.
- cap request ignored origin=builder requested=blockout reason=The crop shows under-window trim and a perforated panel behind furnishings, but no identifiable floor junction or baseboard. The contracted floor-supported body (7.2 x 0.14 x 0.17 m) cannot be verified against the supplied visible evidence.
- cap reached origin=builder requested=blockout reason=Source assignment requires reconciliation: the crop shows under-window trim and a perforated panel behind furniture, without an identifiable floor junction or baseboard. It does not establish the contracted floor-supported 7.2 x 0.14 x 0.17 m strip.
- cap request ignored origin=builder requested=blockout reason=Source assignment conflicts with the identifiable architectural evidence: the crop shows under-window mouldings and a perforated panel behind furnishings, while the contract specifies a floor-supported 0.17 m baseboard. No floor junction is identifiable.
- cap reached origin=builder requested=blockout reason=The requested visible gold tieback conflicts with spatial_contract.ownership.children=external. The existing builder explicitly excludes the externally owned tieback.
- cap request ignored origin=builder requested=blockout reason=The requested gold tieback conflicts with spatial_contract.ownership.children=external. The builder explicitly excludes the tieback and the entry declares only cloth regions.
- rejected origin=builder requested= reason=target is not in canonical stage set
- cap request ignored origin=builder requested= reason=Required gold molding and surrounding framing conflict with external child ownership; only the plaster body region is declared. Recess placement needs reconciliation.
- cap reached origin=builder requested=blockout reason=The requested large upper medallion ornament conflicts with external child ownership and lacks a declared region. The existing detail explicitly excludes surrounding wall ornament. Resolve ownership and extent before adding it.
- cap request ignored origin=builder requested=blockout reason=The requested large upper ornament with oval medallions and a central vertical support conflicts with the supplied external child ownership and rail-only body region. The crop shows the ornament continuing beyond the upper crop boundary, so its full extent cannot be established from this input.
- cap reached origin=builder requested=blockout reason=The crop prominently shows a separate framed mesh fire screen in front of a dark fireplace opening. The supplied entry declares only the opening body, with children externally owned and no screen region or attachment relationship. Assigning the visible screen assembly to this detail asset would assume ownership that the contract does not grant.
- cap request ignored origin=builder requested=blockout reason=The crop shows a prominent framed mesh screen, but the entry declares only the shallow opening body and assigns children to external ownership. Screen ownership and front-plane placement need upstream reconciliation.
- cap reached origin=builder requested=blockout reason=Declared region meshes disconnect the rolled arm pads from the upholstered supports and all feet from the base; rear feet also lie wholly behind the base. The crop shows continuous upholstered arms and an attached dark wooden foot beneath the chair. Repair requires spatial region and support/footprint reconciliation before detail.
- cap request ignored origin=builder requested=blockout reason=Declared regions remain disconnected: arm pads float above supports and all feet terminate below the chair body. Rear feet also lie behind the base. The crop shows continuous upholstered arms and an attached turned wooden foot.
- rejected origin=builder requested= reason=target is not in canonical stage set
- cap request ignored origin=builder requested=blockout reason=Exact contracted region meshes contain disconnected arm pads and feet inconsistent with the crop. Repair requires changing spatial regions, so S4 cannot honestly pass the detail gate within this contract.
- cap reached origin=builder requested=blockout reason=The requested lower gathered waist and continuous hanging sweep conflict with the declared cloth regions; the visible gold tieback also requires coordinated external ownership and placement.
- cap request ignored origin=builder requested=blockout reason=Requested lower gathered waist and deeper hanging sweep conflict with the declared cloth regions; the visible ornate gold tieback also requires explicit ownership and placement.
- cap reached origin=builder requested=blockout reason=The crop shows broad cloth panels hanging far below the tabletop, but the contract declares only a top and four narrow leg regions. Cloth ownership is unspecified while children are external.
- cap request ignored origin=builder requested=blockout reason=Declared regions omit the broad hanging tablecloth visible in the crop; cloth ownership is unresolved under children=external.
- cap reached origin=builder requested=blockout reason=The crop shows broad cloth hanging below the tabletop between the legs. Declared regions cover only top (world z=0.81..0.87 m) and four narrow legs, with no hanging-cloth region. Children are external and cloth ownership is unspecified.
- cap request ignored origin=builder requested=blockout reason=The crop-visible hanging tablecloth has no declared spatial region or explicit ownership. Only the tabletop at z=0.81..0.87 m and four narrow legs are declared; children are externally owned.
- cap reached origin=builder requested=blockout reason=The declared arm and seat regions cannot contain the crop-visible continuous upholstered arm sides. Both arm regions start at world z=0.504 m, while the seat region ends at z=0.4935 m. This forces a 0.0105 m opening beneath each arm outside the back region. The crop shows solid red upholstery descending from the rolled arms into the seat/base, most clearly on the image-right side. No connecting side region is declared, and external child ownership does not authorize inventing one in detail.
- cap request ignored origin=builder requested=blockout reason=Arm regions leave an uncovered vertical gap above the seat, conflicting with the crop-visible continuous upholstered sides below the rolled arms.
- cap reached origin=builder requested=blockout reason=Crop-visible continuous upholstered sides conflict with region coverage: both arms start at z=0.504 m, above the seat top at z=0.4935 m, leaving a 10.5 mm gap away from the back.
- cap request ignored origin=builder requested=blockout reason=The crop shows continuous upholstered arm sides joining the seat/base. Both arm regions start at z=0.504 m while the seat ends at z=0.4935 m. Away from the back, no declared chair region covers this 0.0105 m interval.
- cap reached origin=builder requested=blockout reason=The crop-visible bookcase has intermediate vertical wooden side slats between its corner posts. The supplied contract declares only four narrow corner-post regions and four horizontal shelf regions; no region covers these integral frame members between shelf levels. Faithful detail geometry would exceed the declared component regions.
- cap request ignored origin=builder requested=blockout reason=The crop shows integral vertical wooden side slats between the corner posts. The complete entry declares only four corner-post regions and four horizontal shelf regions, leaving the inter-shelf slats without spatial coverage. A faithful detail asset requires coordinated bookcase-owned side-frame regions.
- cap reached origin=builder requested=blockout reason=The crop shows integral vertical wooden side slats between the corner posts and across the open shelf tiers. The supplied contract has only four corner-post regions and four horizontal shelf regions; none covers these inter-shelf side members. The missing-asset correction does not resolve that spatial conflict.
- cap request ignored origin=builder requested= reason=The crop shows integral vertical wooden side slats spanning the open shelf tiers. The complete current entry contains only four corner-post regions and four shelf regions; none covers the inter-shelf side slats. This is a region-coverage conflict with the crop.
- rejected origin=builder requested= reason=target is not in canonical stage set
- cap request ignored origin=builder requested=blockout reason=The crop-visible curved splayed base requires table-owned geometry outside the narrow pedestal above the declared foot region. The foot region ends at z=0.07 m, while all geometry above that height is constrained to the pedestal's 0.10 x 0.10 m cross-section until the tabletop. This does not cover the raised curved legs visible beneath the turned shaft.
- cap reached origin=builder requested=blockout reason=The raised curved splayed table base extends beyond the narrow pedestal above the declared foot ceiling of 0.07 m. Faithful geometry conflicts with current region coverage.
- cap request ignored origin=builder requested=blockout reason=The crop shows a raised curved splayed base extending outside the narrow 0.10 x 0.10 m pedestal above the foot region ceiling at z=0.07 m. Integral base geometry conflicts with declared region coverage.
- cap reached origin=builder requested=blockout reason=Declared rails reach the post tops, conflicting with raised ball finials in the crop; lower perimeter metalwork lacks region coverage.
- cap reached origin=builder requested=blockout reason=The crop and appended corrections conflict with narrow post regions and missing base-frame and rear-support regions. Faithful detail repair requires coordinated spatial revision.
- cap reached origin=builder requested=blockout reason=The visible deep drawer/apron below the tabletop has no spatial region. The top is restricted to world z=0.69..0.75 m; the remaining four regions are isolated narrow legs. A spanning apron below the top cannot fit those regions.
- cap reached origin=builder requested=blockout reason=The deeper drawer/apron and lower horizontal framing requested from the reference conflict with the supplied regions. The top occupies only world z=0.69..0.75 m; all other regions are isolated 0.05 m square leg boxes. These force an implausibly shallow drawer and cannot contain spanning lower framing.
- cap reached origin=builder requested=blockout reason=The crop depicts a hanging rust-orange curtain, but the contract assigns a floor-supported plaster wall slab. Resolve identity, regions and ownership before detail.
- cap reached origin=builder requested=blockout reason=Confirmed gathered velvet curtain is assigned a floor-supported plaster-wall slab. Its crop overlaps drape_2, which already identifies the same right-window gathered curtain. Correcting the silhouette and adding the gold tieback requires spatial and ownership reconciliation.
- cap reached origin=builder requested=blockout reason=The contracted 1.70 m length and 0.08 m height make the sill/apron too slender to reproduce the photographed broad fascia and wide lower trim or satisfy the requested fascia height increase.
- cap reached origin=builder requested=blockout reason=The contracted length of 1.70 m and total height of 0.08 m (height/length 0.047) produce the overly slender isolated render and conflict with the requested taller broad fascia.
- cap reached origin=builder requested=blockout reason=The requested deeper continuous apron and broader feet conflict with the supplied spatial regions. Top coverage is restricted to z=0.19..0.25 m, with no continuous apron region below it. Each leg is restricted to a 0.05 by 0.05 m footprint and extends to z=0.19 m.
- cap reached origin=builder requested=blockout reason=The base region is confined to z=0..0.10 m, with only a 0.05 m square stem above it until z=0.53 m. The broad curved tripod legs in the crop rise roughly a quarter to a third of the object height and cannot fit these region envelopes.
- cap reached origin=builder requested=blockout reason=The base region z=0..0.10 m permits only 10.5 percent of total object height, conflicting with the requested high leg shoulders. Crop shoulders near y=540..565 of 763 pixels lie approximately 26–29 percent above the lowest foot. The 0.05 m stem width also needs review for the rounded bulb.
- count=1 origin=critic stage=blockout reason=blockout: Reduce the foreground table’s rightward extent. Its visible edge reaches roughly 51% of image width at the bottom, versus 27% in the reference, obscuring too much of the sofa.
- cap reached origin=builder requested=blockout reason=The reference and requested corrections require a stepped ceiling perimeter around the projecting left chimney wall, but the ceiling contract supplies only a rectangular eight-vertex slab. The deep cornice descends below the ceiling body envelope at the rear junction and overlaps the separately declared cornice_n object. Faithful detail requires coordinated footprint, region and ownership repair.
- rejected origin=builder requested= reason=target is not in canonical stage set
- cap reached origin=builder requested=blockout reason=Rug is separately owned and supported by floor. Its z=0..0.015 m envelope lies above floor body z=-0.08..0 m, whose children are external. Adding it to floor would conflict with ownership and bounds.
- cap reached origin=builder requested=blockout reason=The supplied corrections conflict with fixed wall panel region extents and the cornice projection envelope. Revise spatial regions and related metadata before S4 refinement; do not silently alter the contracted frame in the detail builder.
- cap reached origin=builder requested=blockout reason=Spatial region silhouettes conflict with the supplied crop: back_crest is a separate narrow bolster over a slab-like rounded_back, and rolled_arm regions produce tall narrow oval ends instead of broad, low, softly outward-rolled padding. Existing isolated render confirms this mismatch. Revise authoritative padding meshes before detail rebuilding.
- cap reached origin=builder requested=blockout reason=The authoritative padding regions conflict with the crop and explicit silhouette corrections. Detail currently reproduces a separate narrow crest above a flat back and narrow upright oval arms. Revise spatial padding meshes before detail can satisfy the reference.
- cap reached origin=builder requested=blockout reason=The visible continuous carved desk panel beneath the studded tabletop edge has no assigned spatial region. The complete desk entry declares only a top at world z=0.7400000095..0.7999999523 and four narrow corner legs below it. Filling the broad space between legs would conflict with those regions; children are externally owned. Repair the structural regions before building the detail asset.

## Codex calls and elapsed cost

The legacy checkpoint does not retain a complete call-level trace. Builder counts below are reconstructed lower bounds from stage entries and capped reentry logs; critic counts count saved non-gate verdicts. The continuation column counts Codex CLI startup records directly and classifies their stage from the published prompt. It overlaps the other columns and must not be added to them. Calls inside a builder are not driver calls.

| Stage | Recorded builder starts/reentries (lower bound) | Saved critic calls | Counted continuation calls |
|---|---:|---:|---:|
| blockout | 22 | 19 | 2 |
| floorplan | 3 | 3 | 0 |
| identify | 7 | 7 | 2 |
| object | 183 | 64 | 84 |
| tier | 0 | 1 | 4 |

Total recorded attempt time: 21516 seconds. The elapsed time includes model calls, rendering, and checks; it excludes the pause between continuations. Currency cost is not available in the retained logs.

## Defects

- [#16](https://github.com/bddap-bot/photo-to-scene/issues/16): invalid builder GOTO consumed an attempt; fixed by `694f71fce48367189899d6b9dd01d0d36598cfda`.
- [#17](https://github.com/bddap-bot/photo-to-scene/issues/17): capped builder GOTO retried indefinitely; fixed by `2a85afd92f627a329f0b31f1c8094c8c1141399d`.
- [#18](https://github.com/bddap-bot/photo-to-scene/issues/18): composed local texture paths failed the asset gate; fixed by `5e18e863f0fd67824bda9e92c27a653453fee59d`.
- [#19](https://github.com/bddap-bot/photo-to-scene/issues/19): dense inline contracts exceeded the request limit; fixed by `24504f7b57edae4bfa540b37242744ecf0ce3661`.

- [#21](https://github.com/bddap-bot/photo-to-scene/issues/21): a blockout GOTO that only added region confidence changed every contract hash and discarded 41 finalized objects; the detail stage restarted at 0/99.

## Artifacts and continuation

The contracts are [floorplan.json](floorplan.json) and [objects.json](objects.json). Stage images are in [renders/](renders/), and detailed findings are in [scores.md](scores.md). Blender scenes and texture directories are excluded from the repository.

See [PROGRESS.md](PROGRESS.md) for the exact resume command and completed objects.
