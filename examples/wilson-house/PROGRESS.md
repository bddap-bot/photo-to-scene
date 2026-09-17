# Wilson House example progress

RESUMABLE: 35/99 detail objects finalized; active stage `object:lamp_table`. Final gate score is not yet measured; latest available visual critic: 7/10 (`object:window_sill_right`).

- Initial workflow: `05b4bad57d40f982c0ca4209af511e90c8f2454c`
- Detail prompt driver fix: `ce3c95c9ca51d8a5663cbbe170d00781220e9714`
- Resumed published workflow: `ed4bc7e691ec081840040e3acc7918af97c712b5`
- Pipeline input: `highsm-17640-full.jpg` (6114×4842); no input downscaling.
- Published source: `source.jpg` (1529×1211).
- Completed detail objects under current contracts: 35/99.
- Recorded attempts: 99; latest sequence: 145.
- Next `PHOTO_TO_SCENE_STAGE`: `detail`.
- Resume command (from the repository root): `BOTQ_ARTIFACTS_DIR=/home/bot/.local/state/botq/artifacts/3761 PHOTO_TO_SCENE_ROOT=/home/bot/scratch/photo-to-scene/example/work PHOTO_TO_SCENE_STAGE=detail ./pipeline.sh /home/bot/scratch/photo-to-scene/example/highsm-17640-full.jpg`

## Completed detail objects

| Object | Best recorded score | Attempts |
|---|---:|---:|
| floor | 6/10 | 2 |
| ceiling | 7/10 | 2 |
| wall_w | 7/10 | 2 |
| north_left | 5/10 | 2 |
| north_below | 8/10 | 1 |
| north_above | 2/10 | 2 |
| cornice_n | 7/10 | 2 |
| baseboard_n | 0/10 | 2 |
| mantel | 6/10 | 2 |
| firebox | 7/10 | 2 |
| hearth | 7/10 | 2 |
| portrait | 0/10 | 2 |
| sheer_0 | 7/10 | 2 |
| sheer_1 | 0/10 | 2 |
| curtain_rail | 6/10 | 2 |
| drape_0 | 0/10 | 2 |
| drape_1 | 5/10 | 2 |
| drape_2 | 6/10 | 2 |
| radiator | 8/10 | 2 |
| rug | 8/10 | 2 |
| sofa | 6/10 | 2 |
| desk | 0/10 | 2 |
| bookcase | 0/10 | 2 |
| gold_chair | 7/10 | 2 |
| red_chair | 0/10 | 2 |
| round_table | 0/10 | 2 |
| rocker | 0/10 | 2 |
| display_table | 0/10 | 2 |
| orange_chair | 0/10 | 2 |
| tablecloth | 6/10 | 2 |
| desk_bowl | 8/10 | 1 |
| fire_screen | 8/10 | 1 |
| walking_cane | 8/10 | 1 |
| window_sill_right | 7/10 | 2 |
| fireplace_fender | 4/10 | 2 |

The full attempt history and score definitions are in [report.md](report.md) and [scores.md](scores.md).
