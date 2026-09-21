# Wilson House worked example

RESUMABLE: 33/99 detail objects finalized; active stage `object:sheer_1`, attempt 2, sequence 306. Final scene gate and critic scores are not yet measured; latest available visual critic: 6/10 (`object:sheer_1`).

The Library of Congress photograph is the reconstruction reference; [ATTRIBUTION.md](ATTRIBUTION.md) gives the credit, rights statement, and full-resolution link. The pipeline received the 6114×4842 full-resolution JPEG. The repository source is the supplied 1529×1211 copy.

## Workflow provenance

The run began with an empty work directory on `05b4bad57d40f982c0ca4209af511e90c8f2454c`. The generic asset builder was seeded by the driver. The scene-agnostic detail prompt fix `ce3c95c9ca51d8a5663cbbe170d00781220e9714` preceded the saved detail checkpoint.

This continuation uses the published main tip `ed4bc7e691ec081840040e3acc7918af97c712b5`, including the footprint tiers, whole-photo detail context, identification review, and separate builder/critic GOTO allowances. The existing contracts, completed attempts, and artifacts were retained. This is a continuation across workflow revisions, not a fresh measurement of one revision. The published prompts, driver, contracts, and budgets were not tuned for the photograph.

After 41 objects were finalized, the large-tier composition critic scored 0/10 and returned the run to `blockout`. The blockout builder corrected the foreground table and sofa and added the schema `confidence` field to every region, which changed every contract hash; the detail stage restarted at 0/99 under the new contracts ([#21](https://github.com/bddap-bot/photo-to-scene/issues/21)). The earlier attempts remain in the tables below under their old contract hashes.

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
| object:desk | 1 | 10/10 | 3/10 | 179 | Initial entry or forward rebuild. |
| object:desk | 2 | 10/10 | 3/10 | 219 | Replace the exposed thin legs with the broad, solid paneled wooden front visible beneath the tabletop, including its inset decorative detailing. |
| object:cornice_n | 1 | 10/10 | 7/10 | 131 | Initial entry or forward rebuild. |
| object:cornice_n | 2 | 10/10 | 7/10 | 127 | Increase the ornamental band's height relative to the upper mouldings and stretch its rounded motifs into taller, fluted leaf-like relief. |
| object:north_below | 1 | 10/10 | 8/10 | 135 | Initial entry or forward rebuild. |
| object:north_above | 1 | 10/10 | 2/10 | 125 | Initial entry or forward rebuild. |
| object:north_above | 2 | 10/10 | 4/10 | 415 | Add the projecting, stepped upper cornice with its continuous band of closely repeated carved ornaments. |
| object:radiator | 1 | 10/10 | 7/10 | 111 | Initial entry or forward rebuild. |
| object:radiator | 2 | 10/10 | 7/10 | 173 | Reduce hole size relative to the surrounding lattice and soften the stark black interiors. |
| object:hearth | 1 | 10/10 | 6/10 | 118 | Initial entry or forward rebuild. |
| object:hearth | 2 | 10/10 | 7/10 | 114 | Darken the surface toward charcoal-black and replace directional wood-like streaking with subtle stone mottling. |
| object:curtain_rail | 1 | 10/10 | 5/10 | 253 | Initial entry or forward rebuild. |
| object:curtain_rail | 2 | 10/10 | 6/10 | 274 | Add the large crest right of center, with broad oval, medallion-decorated leaves arranged around a thick upright stem. |
| object:baseboard_n | 1 | 10/10 | 6/10 | 221 | Initial entry or forward rebuild. |
| object:baseboard_n | 2 | 10/10 | 6/10 | 242 | Broaden the flat central band relative to the narrow raised edge moldings. |
| object:orange_chair | 1 | 10/10 | 5/10 | 290 | Initial entry or forward rebuild. |
| object:orange_chair | 2 | 10/10 | 5/10 | 226 | Attach all legs beneath the chair base and shorten them to match the reference's low, stout dark wooden feet |
| object:mantel | 1 | 10/10 | 6/10 | 156 | Initial entry or forward rebuild. |
| object:mantel | 2 | 10/10 | 6/10 | 389 | Add the deep burgundy marble inner surround with pale irregular veining, including its broad lintel and side strips. |
| object:rocker | 1 | 10/10 | 5/10 | 243 | Initial entry or forward rebuild. |
| object:rocker | 2 | 10/10 | 5/10 | 299 | Make the back taller and more reclined, with shaped cane panels, a decorative central splat and oval medallion |
| object:gold_chair | 1 | 10/10 | 7/10 | 123 | Initial entry or forward rebuild. |
| object:gold_chair | 2 | 10/10 | 7/10 | 231 | Make the back taller relative to its width and gently round its upper corners |
| object:fireplace_fender | 1 | 10/10 | 4/10 | 239 | Initial entry or forward rebuild. |
| object:fireplace_fender | 2 | 10/10 | 4/10 | 214 | Thicken the rails and widen the turned posts, giving them pronounced bulbous lower bodies and larger spherical finials above the rail junctions. |
| object:tablecloth | 1 | 10/10 | 6/10 | 109 | Initial entry or forward rebuild. |
| object:tablecloth | 2 | 10/10 | 6/10 | 480 | Simplify and enlarge the ornament into dark floral clusters and a prominent ochre-gold scrolling border on a muted gray-beige ground. |
| object:display_table | 1 | 10/10 | 3/10 | 135 | Initial entry or forward rebuild. |
| object:display_table | 2 | 10/10 | 3/10 | 251 | Add a thick tablecloth covering the entire top and hanging deeply over the front and sides, concealing most of the legs. |
| object:red_chair | 1 | 10/10 | 6/10 | 222 | Initial entry or forward rebuild. |
| object:red_chair | 2 | 10/10 | 6/10 | 308 | Thicken and round the arms, especially their front ends, and integrate them into upholstered side panels rather than leaving separate narrow bolsters. |
| object:window_sill_right | 1 | 10/10 | 7/10 | 126 | Initial entry or forward rebuild. |
| object:window_sill_right | 2 | 10/10 | 6/10 | 281 | Reduce the exposed top depth to match the narrower ledge visible beneath the window. |
| object:lamp_table | 1 | 10/10 | 3/10 | 333 | Initial entry or forward rebuild. |
| object:lamp_table | 2 | 10/10 | 4/10 | 201 | Deepen the upper apron beneath the tabletop to match the broad dark horizontal face visible under the open book. |
| object:bookcase | 1 | 10/10 | 4/10 | 210 | Initial entry or forward rebuild. |
| object:bookcase | 2 | 10/10 | 5/10 | 178 | Add closely spaced vertical wooden slats along the sides, extending through the shelf levels. |
| object:north_right | 1 | 10/10 | 7/10 | 232 | Initial entry or forward rebuild. |
| object:north_right | 2 | 10/10 | 5/10 | 287 | Keep a broad, nearly vertical outer fabric section through the tieback area |
| object:window_sill_left | 1 | 10/10 | 7/10 | 118 | Initial entry or forward rebuild. |
| object:window_sill_left | 2 | 10/10 | 7/10 | 104 | Increase the height of the broad flat fascia beneath the sill lip relative to the narrow molding bands. |
| object:stool | 1 | 10/10 | 7/10 | 116 | Initial entry or forward rebuild. |
| object:stool | 2 | 10/10 | 7/10 | 371 | Shorten the exposed legs and make the apron deeper to match the crop’s squat, substantial silhouette. |
| object:north_left | 1 | 10/10 | 5/10 | 98 | Initial entry or forward rebuild. |
| object:north_left | 2 | 0/10 | — | 183 | Add narrow raised gold-toned moulding around all four edges, with a brighter outer bevel and darker inner recess. |
| object:round_table | 1 | 10/10 | 7/10 | 411 | Initial entry or forward rebuild. |
| object:round_table | 2 | 10/10 | 7/10 | 255 | Add the broad cup-shaped section immediately beneath the tabletop, tapering into the narrower turned shaft. |
| object:desk_bowl | 1 | 10/10 | 8/10 | 119 | Initial entry or forward rebuild. |
| object:globe | 1 | 10/10 | 7/10 | 282 | Initial entry or forward rebuild. |
| object:globe | 2 | 10/10 | 7/10 | 227 | Reduce the globe’s diameter relative to the overall stand height. |
| object:desk_papers | 1 | 10/10 | 7/10 | 125 | Initial entry or forward rebuild. |
| object:desk_papers | 2 | 10/10 | 7/10 | 120 | Warm the paper toward the crop’s ochre tan and add subtle uneven discoloration. |
| object:sheer_1 | 1 | 10/10 | 6/10 | 114 | Initial entry or forward rebuild. |
| object:sheer_1 | 2 | 10/10 | 7/10 | 386 | Match the tall window proportions and add deeper, irregular vertical gathers with a subtly uneven lower hem. |
| tier:large | 1 | — | 0/10 | 3989 | Integrated footprint tier before descending. |
| blockout | 1 | 10/10 | 7/10 | 214 | The comparison needs to be rerun to produce a reliable verdict. |
| blockout | 2 | 10/10 | 7/10 | 288 | Lower the ceiling junction at the rear room corner by approximately 20 pixels in the 1019×807 overlay, matching the photograph’s cornice convergence. |
| blockout | 3 | 10/10 | 8/10 | 307 | Raise the fireplace opening’s upper edge by approximately 3% of image height while keeping the mantel fixed |
| identify | 1 | — | 9/10 | 163 | Initial entry or forward rebuild. |
| object:ceiling | 1 | 10/10 | 7/10 | 203 | Initial entry or forward rebuild. |
| object:ceiling | 2 | 10/10 | 8/10 | 133 | Add shallow relief to the perimeter molding so the two pale lines read as raised trim rather than flat outlines. |
| object:wall_w | 1 | 10/10 | 7/10 | 136 | Initial entry or forward rebuild. |
| object:wall_w | 2 | 10/10 | 7/10 | 269 | Extend the central panel molding downward to just above mantel height |
| object:cornice_n | 1 | 10/10 | 7/10 | 131 | Initial entry or forward rebuild. |
| object:cornice_n | 2 | 10/10 | 8/10 | 197 | Increase the height and projection of the upper moulding relative to the ornament band. |
| object:north_below | 1 | 10/10 | 8/10 | 172 | Initial entry or forward rebuild. |
| object:north_above | 1 | 10/10 | 4/10 | 130 | Initial entry or forward rebuild. |
| object:north_above | 2 | 10/10 | 5/10 | 282 | Add the layered upper cornice with its closely repeated carved relief and narrow rope-like lower molding. |
| object:rocker | 1 | 10/10 | 5/10 | 251 | Initial entry or forward rebuild. |
| object:rocker | 2 | 10/10 | 5/10 | 359 | Flatten the runners into shallow, broad wooden arcs beneath the legs |
| object:mantel | 1 | 10/10 | 5/10 | 258 | Initial entry or forward rebuild. |
| object:mantel | 2 | 10/10 | 6/10 | 346 | Increase the carved frieze height and use large, flowing floral scrollwork with a prominent central motif |
| object:window_sill_right | 1 | 10/10 | 7/10 | 114 | Initial entry or forward rebuild. |
| object:window_sill_right | 2 | 10/10 | 7/10 | 121 | Darken the wood to the crop’s warm brown, especially across the front face. |
| object:north_right | 1 | 10/10 | 6/10 | 227 | Initial entry or forward rebuild. |
| object:north_right | 2 | 10/10 | 7/10 | 207 | Reduce the lateral flare, especially below the tieback, so the lower curtain hangs more vertically. |
| object:window_sill_left | 1 | 10/10 | 7/10 | 93 | Initial entry or forward rebuild. |
| object:window_sill_left | 2 | 10/10 | 8/10 | 252 | Increase the fascia height relative to the sill’s length, preserving the projecting top lip. |
| object:stool | 1 | 10/10 | 7/10 | 114 | Initial entry or forward rebuild. |
| object:stool | 2 | 10/10 | 7/10 | 286 | Shorten the exposed legs and deepen the wooden apron to match the crop’s low, substantial silhouette. |
| object:north_left | 1 | 10/10 | 4/10 | 111 | Initial entry or forward rebuild. |
| object:north_left | 2 | 10/10 | 8/10 | 264 | Add continuous narrow gold molding around the recessed brown field, with stepped inner and outer profiles. |
| object:sheer_1 | 1 | 10/10 | 6/10 | 122 | Initial entry or forward rebuild. |
| object:sheer_1 | 2 | 10/10 | 5/10 | 291 | Make the panel substantially taller relative to its width to match the crop's full-height curtain. |
| tier:large | 1 | — | 0/10 | 5176 | Integrated footprint tier before descending. |
| blockout | 1 | 10/10 | 7/10 | 186 | blockout |
| blockout | 2 | 10/10 | 7/10 | 202 | Move the left edge of the large wall molding surrounding the portrait inward by about 45–50 pixels in the 1019-pixel-wide overlay |
| blockout | 3 | 10/10 | 8/10 | 175 | Make the central curtain fall more vertically and narrow its upper spread |
| identify | 1 | — | 8/10 | 116 | Initial entry or forward rebuild. |
| object:ceiling | 1 | 10/10 | 7/10 | 111 | Initial entry or forward rebuild. |
| object:ceiling | 2 | 10/10 | 7/10 | 233 | Add the projecting, layered perimeter cornice with a cream upper molding and darker gold-brown ornamental band beneath. |
| object:wall_w | 1 | 10/10 | 7/10 | 126 | Initial entry or forward rebuild. |
| object:wall_w | 2 | 10/10 | 6/10 | 252 | Extend the central wall-panel border downward toward mantel height |
| object:cornice_n | 1 | 10/10 | 7/10 | 110 | Initial entry or forward rebuild. |
| object:cornice_n | 2 | 10/10 | 7/10 | 116 | Increase the carved frieze height relative to the upper molding to match the deeper reference band. |
| object:north_above | 1 | 10/10 | 4/10 | 94 | Initial entry or forward rebuild. |
| object:north_above | 2 | 10/10 | 4/10 | 288 | Add the deep ceiling cornice with its repeating carved relief and layered moldings above the panel. |
| object:rocker | 1 | 10/10 | 5/10 | 226 | Initial entry or forward rebuild. |
| object:rocker | 2 | 10/10 | 5/10 | 261 | Replace the four rectangular slatted back panels and horizontal crossbar with fine open cane weaving in tall shaped panels, including the central oval medallion and sculpted crest. |
| object:curtain_rail | 1 | 10/10 | 5/10 | 229 | Initial entry or forward rebuild. |
| object:curtain_rail | 2 | 10/10 | 7/10 | 336 | Add the large branching crest above the rail, with a central stem and broad, decorated leaf-shaped lobes. |
| object:mantel | 1 | 10/10 | 6/10 | 234 | Initial entry or forward rebuild. |
| object:mantel | 2 | 10/10 | 6/10 | 223 | Increase the carved frieze height and fill it with dense, broad acanthus scrollwork |
| object:north_right | 1 | 10/10 | 6/10 | 204 | Initial entry or forward rebuild. |
| object:north_right | 2 | 10/10 | 6/10 | 260 | Deepen and vary the folds, adding broad rounded ridges and overlapping fabric around the gathered section. |
| object:north_left | 1 | 10/10 | 8/10 | 94 | Initial entry or forward rebuild. |
| tier:large | 1 | — | 0/10 | 6884 | Integrated footprint tier before descending. |
| tier:large | 1 | — | 0/10 | 8871 | Integrated footprint tier before descending. |
| blockout | 1 | 10/10 | 7/10 | 127 | Retry the composition comparison. |
| blockout | 2 | 10/10 | 7/10 | 353 | Raise the far-right armchair’s seat and shorten its exposed legs |
| blockout | 3 | 10/10 | 7/10 | 180 | Lower the fireplace opening’s upper edge by about 25 pixels at the 1019-pixel overlay width, keeping the mantel height fixed |
| identify | 1 | — | 9/10 | 122 | Initial entry or forward rebuild. |
| object:curtain_rail | 1 | 10/10 | 5/10 | 197 | Initial entry or forward rebuild. |
| object:curtain_rail | 2 | 10/10 | 5/10 | 347 | Add the large branching crest above the rail: a central upright stem with seven oval, leaf-framed medallions arranged in a broad fan. |
| object:tablecloth | 1 | 10/10 | 6/10 | 86 | Initial entry or forward rebuild. |
| object:tablecloth | 2 | 10/10 | 6/10 | 182 | Soften the straight tabletop edges and introduce broader, uneven hanging folds with a pronounced low corner and higher adjacent hem. |
| tier:large | 1 | — | 2/10 | 4021 | Integrated footprint tier before descending. |
| blockout | 1 | 10/10 | 7/10 | 172 | blockout: Lower the ceiling corner and curtain header in image space. The render's corner is near 19% image height versus roughly 23% in the reference |
| blockout | 2 | 10/10 | 8/10 | 249 | Raise the rear ceiling junction roughly 10–15 pixels in the 1019×807 blockout to better match the photograph’s wall–ceiling edges. |
| identify | 1 | — | 9/10 | 145 | Initial entry or forward rebuild. |
| object:ceiling | 1 | 10/10 | 7/10 | 103 | Initial entry or forward rebuild. |
| object:ceiling | 2 | 10/10 | 7/10 | 188 | Add a deep, stepped perimeter cornice with a repeating carved leaf band beneath the pale upper molding. |
| object:wall_w | 1 | 10/10 | 7/10 | 147 | Initial entry or forward rebuild. |
| object:wall_w | 2 | 10/10 | 7/10 | 301 | Replace the isolated narrow rectangle on the left with the tall panel molding near the wall’s outer edge, as visible in the crop |
| object:sofa | 1 | 10/10 | 6/10 | 127 | Initial entry or forward rebuild. |
| object:sofa | 2 | 10/10 | 7/10 | 306 | Enlarge and round the back’s top roll, especially its visible end, with a clearer transition into the lower rear panel. |
| object:cornice_n | 1 | 10/10 | 8/10 | 81 | Initial entry or forward rebuild. |
| object:north_above | 1 | 10/10 | 6/10 | 83 | Initial entry or forward rebuild. |
| object:north_above | 2 | 10/10 | 4/10 | 229 | Add the projecting upper cornice with its closely repeated carved gold-and-dark vertical motifs. |
| object:mantel | 1 | 10/10 | 6/10 | 252 | Initial entry or forward rebuild. |
| object:mantel | 2 | 10/10 | 6/10 | 240 | Increase the frieze height and fill it with dense, broad acanthus scrolls and flowers |
| object:curtain_rail | 1 | 10/10 | 5/10 | 134 | Initial entry or forward rebuild. |
| object:curtain_rail | 2 | 10/10 | 5/10 | 239 | Add the tall central fan-shaped crest with a central oval medallion and branching oval leaf ornaments, matching the crop's silhouette and scale. |
| object:north_right | 1 | 10/10 | 7/10 | 199 | Initial entry or forward rebuild. |
| object:north_right | 2 | 10/10 | 6/10 | 327 | Deepen the overlapping diagonal folds above the gather and tighten the fabric bunching at the tieback. |
| object:north_left | 1 | 10/10 | 7/10 | 75 | Initial entry or forward rebuild. |
| object:north_left | 2 | 10/10 | 7/10 | 173 | Broaden and simplify the moulding profile, especially the prominent flat left strip |
| object:sheer_1 | 1 | 10/10 | 7/10 | 214 | Initial entry or forward rebuild. |
| object:sheer_1 | 2 | 10/10 | 6/10 | 228 | Match the tall, near floor-length proportions of the visible sheer rather than a wide, shallow rectangle. |

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
- cap reached origin=builder requested=blockout reason=The photographed continuous carved desk panel below the studded tabletop has no owned spatial region. Existing regions contain only a top at z=0.74..0.80 m and four narrow corner legs, so adding the visible panel would violate region containment.
- cap reached origin=builder requested=blockout reason=The photograph and explicit correction require a broad solid paneled front, but the spatial contract declares only top and four narrow leg regions. Tabletop accessories are externally owned and require coordinated ownership/support regions rather than duplicate desk child meshes.
- rejected origin=builder requested= reason=target is not in canonical stage set
- cap reached origin=builder requested=blockout reason=north_above correction requires ownership and region reconciliation: its contract assigns children externally, while requested cornice_n and curtain_rail are separate assets outside its body envelope.
- cap reached origin=builder requested=blockout reason=The large fan-shaped oval-medallion crest above the floral band has no declared owner or region. The entry supplies only a 0.2491915225982666 m-high rail body and declares children external. The existing asset omits the crest. Do not compress the crest into the shallow rail envelope.
- cap reached origin=builder requested=blockout reason=The current 5.05 m-wide frame is only 0.24919 m high including ornaments. The full photograph shows a large crest rising several band heights above the rail. The crop clips its top. The complete silhouette conflicts with this shallow envelope.
- cap reached origin=builder requested=blockout reason=The crop supports elevated moulded trim above the under-window radiator grille, not the contracted 0.17 m high floor-contact baseboard. Existing north_below and radiator entries already claim enclosure and grille components. Elevation and ownership need reconciliation before detail modeling.
- cap reached origin=builder requested=blockout reason=Photographs identify elevated horizontal moulded trim above the radiator grille beneath the windows, but the supplied frame starts at z=0 with floor contact and a supported_by floor relationship.
- cap reached origin=builder requested=blockout reason=Contracted component regions are disconnected and contradict the continuous upholstered sides and attached supporting feet visible in the crop. Repair spatial regions before detail construction.
- cap reached origin=builder requested=blockout reason=The supplied component regions conflict with the photographed connected chair and the explicit corrections. Detail geometry confined to these regions cannot attach all feet or make continuous upholstered sides. Repair the spatial contract before rerunning this object stage.
- rejected origin=builder requested= reason=target is not in canonical stage set
- cap reached origin=builder requested=blockout reason=The requested burgundy marble inner lintel and side strips fall outside every declared mantel region. Below z=1.15 m the piers only cover local x=-0.88..-0.65 and +0.65..+0.88 m; the inner span is unassigned. Resolve marble regions and ownership before detail construction.
- cap reached origin=builder requested=blockout reason=Runner and leg/support regions conflict with crop; isolated render confirms steep curls and detached legs. Repair spatial contract before detail regeneration.
- cap reached origin=builder requested=blockout reason=Supplied regions conflict with reference silhouette and appended corrections. Runner tops reach 0.423338 m above the seat underside at 0.397800 m; leg tops at 0.367200 m leave a 0.030600 m attachment gap. Crossrail and cane-rib regions impose a divided slatted back.
- cap reached origin=builder requested=blockout reason=The supplied component regions conflict with the reference fender: 0.025 m-wide posts over 0.28 m height force slender uprights, rail regions at z=0.315..0.340 m meet the finial tops, and no regions cover the visible low framing or rear return supports. Repair regions and ownership before rebuilding the detail asset.
- cap reached origin=builder requested=blockout reason=Requested corrections conflict with component regions: posts are only 0.025 m wide over 0.28 m height; rail regions at z=0.315..0.340 m leave insufficient space for finials above junctions; no regions cover rear posts or the low base.
- rejected origin=builder requested= reason=target is not in canonical stage set
- cap reached origin=builder requested=blockout reason=The tablecloth drape regions are only 0.020 m deep and the top region only 0.020 m high. The isolated render remains boxlike, whereas the crop shows broad irregular folds and a rounded tabletop-to-drape transition. Review the cloth region envelopes against the photograph and display_table contact before rebuilding the drape. Preserve the confirmed identification, enlarged floral ornament and mostly straight hem.
- cap reached origin=builder requested=blockout reason=Requested integrated cloth conflicts with separate tablecloth ownership and display_table regions limited to top and four legs. Adding drapes here would duplicate external geometry and exceed declared regions.
- cap reached origin=builder requested=blockout reason=Requested fuller arms integrated into upholstered side panels and deeper low seat base conflict with fixed arm and seat regions. Repair region envelopes before rebuilding detail.
- cap reached origin=builder requested=blockout reason=Requested reduction of exposed top depth conflicts with the fixed 0.180000305 m depth, footprint and body envelope. The existing isolated test requires exact world-envelope equality. Repair the spatial contract before rebuilding the narrower ledge.
- rejected origin=builder requested= reason=target is not in canonical stage set
- cap reached origin=builder requested=blockout reason=lamp_table shows a substantial spanning drawer/apron beneath the tabletop, but its top region spans only z=0.69..0.75 m and the remaining regions are four isolated 0.05 m-wide leg boxes. Deeper apron geometry and low framing require region repair and ownership review before detail rebuilding.
- cap reached origin=builder requested=blockout reason=The requested crop-matching detail conflicts with the declared regions and child ownership. The top region covers only z=0.69..0.75 m, and the remaining regions are four isolated 0.05 m square leg columns. A deep spanning apron, heavier recessed supports and lower horizontal framing cannot be modeled inside these regions. The requested open book is currently externally owned.
- cap reached origin=builder requested=blockout reason=The visible integral vertical side slats occupy inter-shelf space outside all eight declared regions (four corner posts and four horizontal shelves). Repair region coverage before detail construction.
- cap reached origin=builder requested=blockout reason=The crop and current corrections require continuous integral side slats and three book-filled compartments, but the spatial contract contains only four corner-post and four shelf regions and assigns children externally. Resolve regions and ownership before detail rebuilding.
- cap reached origin=builder requested=blockout reason=Confirmed curtain identification conflicts with the retained plaster-wall spatial contract: a 1.30 m-wide slab extending from floor to sloping ceiling, explicit floor support, and source interpretation Plaster at right window edge. The crop shows gathered velvet suspended below a separate rail, with its lower extent occluded by the orange chair. Correct suspension, extent and ownership require spatial repair.
- cap reached origin=builder requested=blockout reason=Confirmed suspended curtain conflicts with retained plaster interpretation, ceiling-topped slab region and unsupported floor-contact relationship. Repair spatial contract before detail refinement.
- cap reached origin=builder requested=blockout reason=The requested deeper apron and shorter exposed legs conflict with the declared regions. The top region spans z=0.19–0.25 m, normalized 0.76–1. Below 0.19 m only four narrow leg regions exist. Lowering a full-width apron would violate region containment. The crop shows a substantially deeper frame and shorter exposed feet.
- rejected origin=builder requested= reason=target is not in canonical stage set
- rejected origin=builder requested= reason=target is not in canonical stage set
- rejected origin=builder requested= reason=second invalid target from same stage ignored
- rejected origin=builder requested= reason=target is not in canonical stage set
- cap reached origin=builder requested=blockout reason=round_table foot and pedestal regions conflict with the reference. The foot region ends at z=0.07 m, only 9.7 percent of table height, while the curved splayed feet visibly join the pedestal higher, approximately in the lower quarter of its height. Above 0.07 m the only support region is a 0.10 m square pedestal envelope, excluding the spreading upper feet. Repair foot and pedestal region coverage and review the base footprint against the partly occluded crop. Preserve the circular top, external prop ownership and floor contact. Then resume object:round_table to build the asset and render a fresh isolated view.
- cap reached origin=builder requested=blockout reason=The foot region is restricted to z=0..0.07 m. The crop shows raised foot roots and substantial downward curves through approximately the lower quarter of the table. The existing asset explicitly flattens its feet to satisfy this region. Requested descending feet require spatial region repair.
- cap reached origin=builder requested=blockout reason=The crop shows raised spreading tripod leg roots roughly one quarter to one third of the object height above the floor. The base region ends at z=0.10 m, only 10.5 percent of the 0.95 m height, and the stem above it is only 0.05 m wide. These regions cannot contain the visible rising and spreading legs. Existing detail geometry compresses them into the low base envelope.
- cap reached origin=builder requested=blockout reason=The requested tall descending tripod conflicts with the base region z=0..0.10 m (10.5% of the 0.95 m total height). The crop shows leg roots near the lower third; the 0.05 m-wide stem region cannot own or contain these spreading leg shoulders. Repair the spatial regions before returning to detail.
- rejected origin=builder requested= reason=target is not in canonical stage set
- cap reached origin=builder requested=blockout reason=sheer_1 spatial conflict: body width 3.20 m and height 2.11665 m produce a broad panel, whereas both reference images and the correction require the tall right window field. Re-solve its extent using the contracted camera, not the crop aspect ratio alone. The body depth is limited to 0.025 m and 17 fold regions are fixed thin strips; revise regions to accommodate deeper irregular continuous gathers. Preserve separate ownership of velvet drapes, rail, sill and foreground display objects. Then resume object:sheer_1 for the finer denser branching floral pattern, warmer softer ivory, lower-field translucency, uneven hem and fresh detail render.
- count=2 origin=critic stage=blockout reason=The comparison needs to be rerun to produce a reliable verdict.
- cap reached origin=builder requested=blockout reason=Conflicting ceiling height declarations: the body mesh and frame reflect the latest downward correction, but ceiling_plane retains the previous elevation. Reconcile the plane metadata and connected wall-top/cornice relationships at blockout before detail validation.
- cap reached origin=builder requested=blockout reason=Requested panel placement and extent corrections conflict with the explicit spatial regions; revise blockout before rerunning detail.
- cap reached origin=builder requested=blockout reason=Requested cornice and curtain rail additions conflict with external child ownership. The separate curtain_rail asset explicitly omits the large fan crest because a taller owned region is absent.
- cap reached origin=builder requested=blockout reason=Current contracted runner, leg and back regions conflict with the supplied reference crop. Runner tips rise above the seat underside; legs descend to floor level yet stop short of the seat. The reference shows shallow broad rocking rails supporting connected leg ends. The back has uninterrupted tall cane fields flanking an ornamental central splat, rather than the current full-width mid-back crossrail and heavy vertical ribs.
- rejected origin=builder requested= reason=target is not in canonical stage set
- cap reached origin=builder requested=blockout reason=The requested corrections conflict with contracted component meshes, back pose and support relationships. Runner tips rise above the seat underside, legs stop below the seat, and four cane-panel regions plus back_crossrail enforce the rejected divided back.
- cap reached origin=builder requested=blockout reason=The current carved_frieze region is compressed into z=1.3124473095..1.4500000477 (height 0.1375527382 m), whereas both photographs show a broad carved band below the shelf. The existing detailed frieze spans z=1.15..1.45 (0.30 m), and cannot fit the supplied region without visibly flattening the foliage. The newly owned marble inset_header reaches z=1.3124473095 and occupies the lower part of that former carved band. This is a region-boundary conflict requiring blockout reconciliation, not a material-only repair.
- cap reached origin=builder requested=blockout reason=Requested taller frieze and broader marble jambs conflict with the current component region bounds. Reconcile their shared boundaries and the corrected opening before rebuilding detail.
- cap reached origin=builder requested=blockout reason=Confirmed curtain identification conflicts with inherited plaster-wall body, region extent and floor-support relationship. Detail cannot resolve these spatial conflicts within the current contract.
- cap reached origin=builder requested=blockout reason=Confirmed curtain conflicts with inherited solid plaster region and floor support; reconcile silhouette, suspension and ownership.
- cap reached origin=builder requested=blockout reason=Requested taller fascia and thicker bottom molding conflict with the thin contracted envelope.
- rejected origin=builder requested= reason=target is not in canonical stage set
- cap reached origin=builder requested=blockout reason=The requested deep apron, fuller domed cushion and chunky curved supports conflict with the contracted top region at z=0.19..0.25 m and four support regions only 0.05 m wide. The existing apron and feet nearly fill those regions. Repair the regional proportions before detail remodeling.
- cap reached origin=builder requested=blockout reason=Requested increased panel height relative to width changes the fixed body dimensions. Adding continuous gilt molding conflicts with the current external-child ownership and substrate-only asset.
- cap reached origin=builder requested=blockout reason=Requested substantially taller curtain proportions conflict with the contracted width 3.200000047683716 m and height 2.0052683353424072 m (height/width 0.62665). Existing isolated render is a wide, squat field; the supplied crop and whole photograph show a full-height right-window sheer. Resolve the panel extent against the right opening before detail refinement.
- count=3 origin=critic stage=blockout reason=blockout
- cap reached origin=builder requested=blockout reason=Requested projecting layered perimeter cornice conflicts with current ceiling body extent and separate cornice_n ownership. Resolve at blockout before detail adds this geometry.
- cap reached origin=builder requested=blockout reason=Supplied one-reentry corrections conflict with explicit wall-panel region layout; repair spatial declarations before S4 regeneration.
- cap reached origin=builder requested=blockout reason=Requested cornice and ornate pelmet/crest additions conflict with the external-child ownership and body envelope of north_above. These components already have separate object entries and cannot be duplicated within this panel asset.
- cap reached origin=builder requested=blockout reason=Current declared component regions conflict with the photographed chair: disconnected legs/seat and four-field crossrail back instead of tall cane fields with an oval central ornament. Repair spatial regions and support relationships before rerunning S4.
- cap reached origin=builder requested=blockout reason=Current declared regions and component relationships conflict with the supplied crop and explicit one-reentry corrections; repair the rocker contract before rebuilding detail.
- cap reached origin=builder requested=blockout reason=Confirmed large oval-medallion foliate crest conflicts with the shallow body envelope; existing asset explicitly omits it for lack of a taller owned region.
- rejected origin=builder requested= reason=target is not in canonical stage set
- cap reached origin=builder requested=blockout reason=The complete large branching crest shown above the rail conflicts with the current body-only spatial envelope: frame size 4.733662 x 0.200001 x 0.249192 m and z bounds 2.910509..3.159700 m. The source crop clips the crest top, while the full reference shows its tall silhouette. Existing detail code explicitly omits the crest because no taller owned region exists. Repair the envelope and region ownership before rebuilding detail.
- cap reached origin=builder requested=blockout reason=Current component regions conflict with the photographed proportions: the broad carved frieze is compressed to 0.137553 m, whereas the marble header occupies 0.369060 m. The cream outer uprights are also much wider than the adjacent marble jambs, reversing the visible crop relationship. Repair region boundaries before detail rebuilding.
- cap reached origin=builder requested=blockout reason=The requested substantial carved frieze and continuous cream moulded frame conflict with the current component regions. carved_frieze is only 0.137553 m tall across 1.760 m, while inset_header occupies 0.369060 m vertically immediately below it. The existing detail builder compresses a 0.30 m carving into that shallow allocation. Faithful height and frame corrections require spatial region refitting.
- cap reached origin=builder requested=blockout reason=The confirmed velvet curtain conflicts with the retained plaster-wall spatial contract: a broad 1.30 x 0.25 x 3.938762 m floor-supported box with a ceiling-plane-shaped body mesh. The crop shows gathered textile suspended beneath the rail with its lower extent occluded by the chair.
- cap reached origin=builder requested=blockout reason=The retained 1.30 x 0.25 x 3.94 m floor-supported plaster envelope conflicts with the suspended gathered curtain identified in both photographs; the chair occludes its lower extent.
- rejected origin=critic requested= reason=target is not in canonical stage set
- count=4 origin=critic stage=blockout reason=Retry the composition comparison.
- cap reached origin=builder requested=blockout reason=Resolve crest ownership and assembled silhouette before rerunning detail. The expanded identification crop includes the whole crest, while the rail retains a shallow body-only frame and external-child ownership. The current rail asset duplicates rail_crest as a vertically compressed motif.
- rejected origin=builder requested= reason=target is not in canonical stage set
- cap reached origin=builder requested=blockout reason=Reconcile curtain_rail crest ownership and spatial envelope before detail. The expanded crop and requested correction include a tall branching seven-medallion crest, but curtain_rail retains external-child ownership and a body-only frame 0.249192 m high (top z=3.159700 m). The separately indexed rail_crest reaches z=3.404253 m. Assign the crest to this assembly with explicit regions and revised bounds/frame, and remove duplicate external ownership; verify crest attachment, broad fan silhouette and placement against both photographs. Then resume object:curtain_rail to add the central upright stem and seven oval leaf-framed medallions, thicken the decorative face with dense overlapping floral/foliate relief, and give the small finials fuller varied leaves and sculptural depth. Previous routing used an unrecognized key; the pipeline reads the stage field, now set to the canonical blockout value.
- count=5 origin=critic stage=blockout reason=blockout: Lower the ceiling corner and curtain header in image space. The render's corner is near 19% image height versus roughly 23% in the reference; the curtain header is also too high.
- cap reached origin=builder requested=blockout reason=Requested deep perimeter cornice conflicts with the ceiling body bounds and separately assigned cornice geometry.
- cap reached origin=builder requested=blockout reason=The requested image-left outer-edge panel placement and clearance above the lower horizontal trim conflict with the current explicit wall_panel_0 region meshes. Repair spatial regions before rerunning S4 detail.
- cap reached origin=builder requested=blockout reason=The requested larger rounded top roll and thicker outward-bulging near arm conflict with the existing slim upholstered_body silhouette. The entry provides an exact continuous mesh and explicitly records slimmer foreground back bolster plus bolster_refinement depth_scale=0.75 and height_scale=0.86. This is a component-volume and silhouette correction requiring revised spatial evidence before S4 detail.
- cap reached origin=builder requested=blockout reason=Requested additions conflict with the current external-child ownership and body envelope. The cornice, lower rail and fan-shaped crest are separately contracted objects; adding them to north_above would duplicate ownership and exceed its bounds.
- cap reached origin=builder requested=blockout reason=The supplied region proportions conflict with the reference crop: carved_frieze is restricted to z=1.3124473094940186..1.4500000476837158, only 0.137553 m (8.7% of overall height). The existing detail consequently flattens the foliate panel, while the photograph shows a substantially taller carved band. The marble header is 0.369060 m tall, 2.68 times the frieze height, reversing the visual balance of these adjacent bands in the crop. Repair requires changing shared region boundaries and must occur in blockout.
- cap reached origin=builder requested=blockout reason=Requested frieze height, continuous cream frame and screen conflict with the current region allocation and external-child ownership. The frieze is constrained to z=1.312447..1.450000 (0.137553 m), whereas the marble header occupies z=0.943387..1.312447 (0.369060 m). Existing detail compresses the carving to fit; the crop shows a much taller foliate panel with substantial end consoles and a cream transverse molding before the marble.
- cap reached origin=builder requested=blockout reason=The requested full fan-shaped crest conflicts with external rail_crest ownership and curtain_rail frame/body bounds. Rail height is 0.249192 m and top is 3.078405 m; the separately indexed crest reaches 3.322957 m.
- cap reached origin=builder requested=blockout reason=Confirmed curtain identification conflicts with the inherited plaster-wall body, floor support and uncertain ownership. The broad 1.300 x 0.250 x 3.834 m floor-to-ceiling region requires spatial repair before curtain detail integration.
- rejected origin=builder requested= reason=target is not in canonical stage set
- cap reached origin=builder requested=blockout reason=The confirmed hanging curtain retains a plaster-derived 1.30 m wide floor-supported body and overlaps drape_2. The previous request parsed an empty stage; this request uses the canonical stage key.
- cap reached origin=builder requested=blockout reason=The supplied frame and regions conflict with the tall right-window lace field. Repair spatial evidence before detail scoring.
- cap reached origin=builder requested=blockout reason=The contracted 3.20 m width and 1.92397 m height produce a landscape sheer, conflicting with the tall visible right-window panel and explicit proportion correction. The 17 thin fold regions are separated from the body in depth, constraining continuous varied folds.

## Codex calls and elapsed cost

The legacy checkpoint does not retain a complete call-level trace. Builder counts below are reconstructed lower bounds from stage entries and capped reentry logs; critic counts count saved non-gate verdicts. The continuation column counts Codex CLI startup records directly and classifies their stage from the published prompt. It overlaps the other columns and must not be added to them. Calls inside a builder are not driver calls.

| Stage | Recorded builder starts/reentries (lower bound) | Saved critic calls | Counted continuation calls |
|---|---:|---:|---:|
| blockout | 33 | 30 | 24 |
| floorplan | 3 | 3 | 0 |
| identify | 11 | 11 | 10 |
| object | 370 | 182 | 401 |
| tier | 0 | 6 | 17 |

Total recorded attempt time: 78009 seconds. The elapsed time includes model calls, rendering, and checks; it excludes the pause between continuations. Currency cost is not available in the retained logs.

## Defects

- [#16](https://github.com/bddap-bot/photo-to-scene/issues/16): invalid builder GOTO consumed an attempt; fixed by `694f71fce48367189899d6b9dd01d0d36598cfda`.
- [#17](https://github.com/bddap-bot/photo-to-scene/issues/17): capped builder GOTO retried indefinitely; fixed by `2a85afd92f627a329f0b31f1c8094c8c1141399d`.
- [#18](https://github.com/bddap-bot/photo-to-scene/issues/18): composed local texture paths failed the asset gate; fixed by `5e18e863f0fd67824bda9e92c27a653453fee59d`.
- [#19](https://github.com/bddap-bot/photo-to-scene/issues/19): dense inline contracts exceeded the request limit; fixed by `24504f7b57edae4bfa540b37242744ecf0ce3661`.

- [#21](https://github.com/bddap-bot/photo-to-scene/issues/21): a blockout GOTO that only added region confidence changed every contract hash and discarded 41 finalized objects; the detail stage restarted at 0/99.

## Artifacts and continuation

The contracts are [floorplan.json](floorplan.json) and [objects.json](objects.json). Stage images are in [renders/](renders/), and detailed findings are in [scores.md](scores.md). Blender scenes and texture directories are excluded from the repository.

See [PROGRESS.md](PROGRESS.md) for the exact resume command and completed objects.
