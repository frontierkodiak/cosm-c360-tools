The output clips have all-black frames. We need to narrow down the cause.
- The filter complex we are using here has no meaningful difference from the filter complex in the previous (known-good) version from the standalone version of the script.






# DEBUGGING

## Test Each Tile Individually:
Extract and encode just [0:v:0] without cropping:

```bash
ffmpeg -i /datasets/dataZoo/clients/ladybird_data/LADYBIRD/failed_copy/0H/0M/0S/0.ts -map 0:v:0 -c copy single_tile_0.mp4 \
&& ffmpeg -i /datasets/dataZoo/clients/ladybird_data/LADYBIRD/failed_copy/0H/0M/0S/0.ts -map 0:v:1 -c copy single_tile_1.mp4 \
&& ffmpeg -i /datasets/dataZoo/clients/ladybird_data/LADYBIRD/failed_copy/0H/0M/0S/0.ts -map 0:v:2 -c copy single_tile_2.mp4 \
&& ffmpeg -i /datasets/dataZoo/clients/ladybird_data/LADYBIRD/failed_copy/0H/0M/0S/0.ts -map 0:v:3 -c copy single_tile_3.mp4
```
Check if single_tile_0.mp4 shows any content. Repeat for [0:v:1], [0:v:2], and [0:v:3].

**RESULT**:
- single_tile_0.mp4 shows content
- single_tile_1.mp4 shows content
- single_tile_2.mp4 shows content
- single_tile_3.mp4 shows content
All look correct.
