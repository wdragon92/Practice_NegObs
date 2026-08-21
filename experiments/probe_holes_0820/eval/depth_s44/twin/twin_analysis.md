# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/probe_holes_0820/eval/depth_s44/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/probe_holes_0820/eval/depth_s44/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/probe_holes_0820/dataset_manifest_probe.json`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 1e-06 · paired bootstrap 10000x seed 42

pairs found **72** · pose-matched (kept) **72** · excluded **0** · kept pairs carrying >=1 GT cell **72** (delta_score > 0 in 45/72)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 15 | 0.1045 [0.0527, 0.1632] * | 0.1615 [0.1281, 0.1997] * |
| E | 27 | 0.0565 [0.0429, 0.0698] * | 0.0336 [0.0228, 0.0448] * |
| H | 30 | 0.0000 [0.0000, 0.0000] * | -0.0000 [-0.0000, 0.0000] |
| all | 72 | 0.0430 [0.0290, 0.0600] * | 0.0462 [0.0310, 0.0641] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 6 | 0.0074 [0.0000, 0.0149] * | 3 | 0.0000 [0.0000, 0.0000] * |
| 2 [2,5) m | 51 | 0.0439 [0.0305, 0.0594] * | 21 | 0.0000 [0.0000, 0.0000] * |
| 3a [5,8) m | 21 | 0.0934 [0.0553, 0.1381] * | 3 | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 18 | 0.0136 [0.0005, 0.0287] * | 9 | 0.0000 [0.0000, 0.0000] |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| probeH1 | 24 | 0 | 1.00 | 0.0752 | 0.1108 |
| probeH2 | 24 | 0 | 1.00 | 0.0537 | 0.0279 |
| probeH3 | 24 | 0 | 1.00 | 0.0000 | 0.0000 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/probe_holes_0820/eval/depth_s44/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
