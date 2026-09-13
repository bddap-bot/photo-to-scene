# Wilson House example progress

- Initial workflow: `05b4bad57d40f982c0ca4209af511e90c8f2454c`
- Detail-prompt driver fix: `ce3c95c9ca51d8a5663cbbe170d00781220e9714`
- Pipeline input: `/home/bot/scratch/photo-to-scene/example/highsm-17640-full.jpg` (6114×4842)
- Completed stages: floorplan, blockout, identify
- Floorplan scores: 5/10, 7/10, 7/10; authoritative attempt 2
- Blockout scores by cycle: 6/6/7, 7/7/7, 7/7/8, 7/7/8, 7/7/8, 7/7/7
- Identify scores by cycle: 8, 8, 9, 8, 10, 10
- Object contracts: 99; declaration and crop gates passed
- Detail objects finalized: 20/99 (`wall_w`, `floor`, `rug`, `sofa`, `ceiling`, `north_above`, `mantel`, `sheer_1`, `cornice_n`, `desk`, `portrait`, `rocker`, `drape_0`, `baseboard_n`, `drape_2`, `north_left`, `sheer_0`, `north_below`, `curtain_rail`, `firebox`)
- Detail best scores: wall_w 7, floor 6, rug 8, sofa 6, ceiling 7, north_above 2, mantel 6, sheer_1 0, cornice_n 7, desk 0, portrait 0, rocker 0, drape_0 0, baseboard_n 0, drape_2 6, north_left 5, sheer_0 7, north_below 8, curtain_rail 6, firebox 7
- Detail attempts through `firebox`: 40; sequence 104 is the last recorded attempt and sequence 105 is an interrupted, unrecorded `gold_chair` start
- Detail render checkpoint: `renders/detail-progress.png` contains the 18 available isolated renders; `desk` and `baseboard_n` have no contract-valid asset
- GOTO history: five accepted detail → `blockout` corrections; later builder GOTOs reached the workflow cap
- Defects: [#16](https://github.com/bddap-bot/photo-to-scene/issues/16), [#17](https://github.com/bddap-bot/photo-to-scene/issues/17), [#18](https://github.com/bddap-bot/photo-to-scene/issues/18), [#19](https://github.com/bddap-bot/photo-to-scene/issues/19)
- Current stage: detail; next object is `gold_chair`
- Next `PHOTO_TO_SCENE_STAGE`: `detail`
- Resume command: `BOTQ_ARTIFACTS_DIR=/home/bot/.local/state/botq/artifacts/3700 PHOTO_TO_SCENE_ROOT=/home/bot/scratch/photo-to-scene/example/work PHOTO_TO_SCENE_STAGE=detail ./pipeline.sh /home/bot/scratch/photo-to-scene/example/highsm-17640-full.jpg`
