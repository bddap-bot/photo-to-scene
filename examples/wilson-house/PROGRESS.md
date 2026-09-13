# Wilson House example progress

- Workflow: `05b4bad57d40f982c0ca4209af511e90c8f2454c`
- Pipeline input: `/home/bot/scratch/photo-to-scene/example/highsm-17640-full.jpg` (6114×4842)
- Completed stages: floorplan, blockout, identify
- Floorplan scores: 5/10, 7/10, 7/10; authoritative attempt 2
- Initial blockout scores: 6/10, 6/10, 7/10; authoritative attempt 3
- Corrective blockout scores: 7/10, 7/10, 7/10; authoritative attempt 3
- Initial identify score: 8/10 on attempt 1
- Corrective identify score: 8/10 on attempt 1
- Object contracts: 142, declaration and crop gates passed
- Detail progress: `wall_w` requested a spatial correction; no asset completed
- GOTO history: builder → `blockout` for the `wall_w` facing/frame conflict
- Defect found: [#16](https://github.com/bddap-bot/photo-to-scene/issues/16), invalid builder GOTO suppresses the first valid retry and consumes a detail attempt
- Corrective geometry: wall facing fixed; ceiling, gold chair, stool, sofa, rocker, and orange chair silhouettes revised; all 139 declarations pass
- Identification corrections: fixed hearth and microphone labels/crops, clarified the writing table, and added hanging tieback and fire-tool-holder entries
- Current stage: detail, object `wall_w`
- Next `PHOTO_TO_SCENE_STAGE`: `detail`
- Resume command: `PHOTO_TO_SCENE_ROOT=/home/bot/scratch/photo-to-scene/example/work PHOTO_TO_SCENE_STAGE=detail ./pipeline.sh /home/bot/scratch/photo-to-scene/example/highsm-17640-full.jpg`
