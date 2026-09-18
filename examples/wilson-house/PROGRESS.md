# Wilson House example progress

RESUMABLE: 11/99 detail objects finalized; active stage `object:curtain_rail`, attempt 1, sequence 184. Final scene gate and critic scores are not yet measured; latest available visual critic: 7/10 (`object:hearth`).

- Initial workflow: `05b4bad57d40f982c0ca4209af511e90c8f2454c`
- Detail prompt driver fix: `ce3c95c9ca51d8a5663cbbe170d00781220e9714`
- Resumed published workflow: `ed4bc7e691ec081840040e3acc7918af97c712b5`
- Pipeline input: `highsm-17640-full.jpg` (6114×4842); no input downscaling.
- Published source: `source.jpg` (1529×1211).
- Completed detail objects under current contracts: 11/99.
- Recorded attempts: 134; latest sequence: 184.
- Next `PHOTO_TO_SCENE_STAGE`: `detail`.
- Resume command (from the repository root): `BOTQ_ARTIFACTS_DIR=/home/bot/.local/state/botq/artifacts/4243 PHOTO_TO_SCENE_ROOT=/home/bot/scratch/photo-to-scene/example/work PHOTO_TO_SCENE_STAGE=detail ./pipeline.sh /home/bot/scratch/photo-to-scene/example/highsm-17640-full.jpg`

## Completed detail objects

| Object | Best recorded score | Attempts |
|---|---:|---:|
| floor | 8/10 | 2 |
| ceiling | 7/10 | 2 |
| wall_w | 7/10 | 2 |
| north_below | 8/10 | 1 |
| north_above | 4/10 | 2 |
| cornice_n | 7/10 | 2 |
| hearth | 7/10 | 2 |
| radiator | 7/10 | 2 |
| rug | 8/10 | 1 |
| sofa | 7/10 | 2 |
| desk | 3/10 | 2 |

The full attempt history and score definitions are in [report.md](report.md) and [scores.md](scores.md).
