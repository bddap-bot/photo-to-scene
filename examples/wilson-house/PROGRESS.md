# Wilson House example progress

The [combined-fixes rerun](combined-fixes/report.md) is published separately: 81/81 contracts finalized, zero final observed errors, and a 6/10 in-run materials score. It required supervised finalization after an expired-budget redirect. The original baseline below is preserved.

The [post-defects rerun](post-defects/report.md) is published separately: all 68 assets built, mean detail score 7.29 over 66 observed objects, and a normal driver exit with no supervised finalization. It failed the observed gate (20 errors at integration, 69 at materials on a stale assembly), so no in-run scene critic ran.

The [third rerun](rerun-3/report.md) is published separately: all 67 assets built, mean detail score 7.46 over 65 observed objects, and a normal driver exit with no supervised finalization after one infrastructure continuation. It failed the observed gate on 3 asset-geometry errors at both integration and materials, so no in-run scene critic ran.

COMPLETE: 99/99 detail objects finalized; integrate, materials, and the final render ran on `428a8fb`. 386 attempt records, latest sequence 431. Results are in [report.md](report.md).

- Initial workflow: `05b4bad57d40f982c0ca4209af511e90c8f2454c`
- Final workflow: `428a8fbd94d5dc66d01e975c063a160f22a8f9d1`
- Pipeline input: `highsm-17640-full.jpg` (6114×4842, the full-resolution file linked in [ATTRIBUTION.md](ATTRIBUTION.md)); no input downscaling.
- Published source: `source.jpg` (1529×1211).

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
| firebox | 7/10 | 2 |
| hearth | 7/10 | 2 |
| portrait | 8/10 | 1 |
| sheer_0 | 7/10 | 2 |
| sheer_1 | 7/10 | 2 |
| curtain_rail | 5/10 | 2 |
| drape_0 | 7/10 | 2 |
| tieback_0 | 6/10 | 2 |
| drape_1 | 7/10 | 2 |
| tieback_1 | 6/10 | 2 |
| drape_2 | 7/10 | 2 |
| rail_crest | 7/10 | 2 |
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
| candlestick_0 | 8/10 | 2 |
| candle_0 | 8/10 | 1 |
| candlestick_1 | 7/10 | 2 |
| candle_1 | 8/10 | 1 |
| mantel_clock | 8/10 | 1 |
| mantel_clock_face | 8/10 | 2 |
| sconce | 4/10 | 2 |
| microphone | 8/10 | 1 |
| book_0_0 | 8/10 | 2 |
| book_0_1 | 8/10 | 1 |
| book_0_2 | 8/10 | 1 |
| book_0_3 | 7/10 | 2 |
| book_0_4 | 7/10 | 2 |
| book_0_5 | 7/10 | 2 |
| book_0_6 | 8/10 | 2 |
| book_1_0 | 8/10 | 1 |
| book_1_1 | 7/10 | 2 |
| book_1_2 | 8/10 | 1 |
| book_1_3 | 7/10 | 2 |
| book_2_0 | 8/10 | 2 |
| book_2_1 | 8/10 | 1 |
| table_lamp | 8/10 | 2 |
| open_book | 8/10 | 1 |
| tablecloth | 6/10 | 2 |
| photo_frame_0 | 8/10 | 1 |
| photo_image_0 | 8/10 | 1 |
| photo_frame_1 | 8/10 | 1 |
| photo_image_1 | 9/10 | 1 |
| statue | 6/10 | 2 |
| stationery_box | 8/10 | 2 |
| stationery_0 | 7/10 | 2 |
| stationery_1 | 7/10 | 2 |
| stationery_2 | 5/10 | 2 |
| small_cup | 7/10 | 2 |
| table_tray | 6/10 | 2 |
| desk_bowl | 8/10 | 1 |
| desk_papers | 7/10 | 2 |
| desk_book | 6/10 | 2 |
| desk_tray | 8/10 | 2 |
| horse_pedestal | 7/10 | 2 |
| she_wolf_figurine | 5/10 | 2 |
| desk_photo_0 | 7/10 | 2 |
| desk_photo_1 | 7/10 | 2 |
| desk_photo_2 | 7/10 | 2 |
| fire_screen | 7/10 | 2 |
| andiron_0 | 4/10 | 2 |
| andiron_ball_0 | 8/10 | 1 |
| andiron_1 | 6/10 | 2 |
| andiron_ball_1 | 8/10 | 1 |
| fire_tool_0 | 7/10 | 2 |
| fire_tool_1 | 7/10 | 2 |
| fire_tool_2 | 6/10 | 2 |
| walking_cane | 8/10 | 1 |
| tieback_hanging_0 | 6/10 | 2 |
| tieback_hanging_1 | 5/10 | 2 |
| fire_tool_stand | 7/10 | 2 |
| window_sill_left | 8/10 | 2 |
| window_sill_right | 7/10 | 2 |
| window_frame_left | 8/10 | 1 |
| window_frame_middle | 7/10 | 2 |
| fireplace_fender | 4/10 | 2 |
| window_frame_right | 7/10 | 2 |
| book_rest_gallery | 6/10 | 2 |

The full attempt history and score definitions are in [report.md](report.md) and [scores.md](scores.md).
