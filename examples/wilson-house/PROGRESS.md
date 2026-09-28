# Wilson House example progress

RESUMABLE: 33/99 detail objects finalized under current contracts; 266 attempt records, latest sequence 312. Latest driver event: `ENTER object:drape_0 attempt=2 sequence=312`.

- Initial workflow: `05b4bad57d40f982c0ca4209af511e90c8f2454c`
- Current workflow: `428a8fbd94d5dc66d01e975c063a160f22a8f9d1`
- Pipeline input: `highsm-17640-full.jpg` (6114×4842, the full-resolution file linked in [ATTRIBUTION.md](ATTRIBUTION.md)); no input downscaling.
- Published source: `source.jpg` (1529×1211).
- Next `PHOTO_TO_SCENE_STAGE`: `detail`.
- Resume, from the repository root, with the retained work directory of this run:

```sh
PHOTO_TO_SCENE_ROOT=/absolute/path/to/work PHOTO_TO_SCENE_STAGE=detail ./pipeline.sh /absolute/path/to/highsm-17640-full.jpg
```

The driver resumes from its recorded attempt counts; an attempt interrupted before its record has no score.

## Finalized detail objects

| Object | Best recorded score | Attempts |
|---|---:|---:|
| floor | 8/10 | 2 |
| ceiling | 7/10 | 2 |
| wall_w | 7/10 | 2 |
| north_left | 7/10 | 2 |
| north_right | 7/10 | 2 |
| north_below | 8/10 | 1 |
| north_above | 6/10 | 2 |
| cornice_n | 8/10 | 1 |
| baseboard_n | 6/10 | 2 |
| mantel | 6/10 | 2 |
| hearth | 7/10 | 2 |
| sheer_1 | 7/10 | 2 |
| curtain_rail | 5/10 | 2 |
| radiator | 7/10 | 2 |
| rug | 8/10 | 1 |
| sofa | 7/10 | 2 |
| desk | 3/10 | 2 |
| bookcase | 5/10 | 2 |
| globe | 7/10 | 2 |
| gold_chair | 7/10 | 2 |
| red_chair | 6/10 | 2 |
| lamp_table | 4/10 | 2 |
| round_table | 7/10 | 2 |
| rocker | 5/10 | 2 |
| display_table | 3/10 | 2 |
| orange_chair | 5/10 | 2 |
| stool | 7/10 | 2 |
| tablecloth | 6/10 | 2 |
| desk_bowl | 8/10 | 1 |
| desk_papers | 7/10 | 2 |
| window_sill_left | 8/10 | 2 |
| window_sill_right | 7/10 | 2 |
| fireplace_fender | 4/10 | 2 |

The full attempt history and score definitions are in [report.md](report.md) and [scores.md](scores.md).
