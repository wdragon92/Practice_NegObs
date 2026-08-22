# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/fusion/s43/fused_max/eval_test/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/fusion/s43/fused_max/eval_test/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/dataset_manifest_v2_full.json`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **408** · pose-matched (kept) **366** · excluded **42** · kept pairs carrying >=1 GT cell **312** (delta_score > 0 in 287/312)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 165 | 0.3210 [0.2718, 0.3702] * | 0.3152 [0.2663, 0.3647] * |
| E | 45 | 0.2119 [0.1602, 0.2655] * | 0.1919 [0.1421, 0.2443] * |
| H | 96 | 0.3587 [0.3117, 0.4079] * | 0.3571 [0.3101, 0.4063] * |
| all | 366 | 0.3122 [0.2810, 0.3437] * | 0.3234 [0.2931, 0.3538] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 27 | 0.3127 [0.1945, 0.4365] * | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 93 | 0.3880 [0.3222, 0.4532] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 201 | 0.2678 [0.2140, 0.3227] * | 33 | -0.0756 [-0.1711, 0.0114] |
| 3b [8,12) m | 312 | 0.3107 [0.2808, 0.3416] * | 96 | 0.3587 [0.3118, 0.4079] * |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 72 | 0 | 1.00 | 0.2469 | 0.2469 |
| scene07 | 30 | 42 | 0.42 | 0.7376 | 0.7370 |
| scene14 | 72 | 0 | 1.00 | 0.4396 | 0.4416 |
| scene15 | 72 | 0 | 1.00 | 0.1663 | 0.1685 |
| scene18 | 72 | 0 | 1.00 | 0.2266 | 0.2012 |
| sceneC2 | 24 | 0 | 1.00 | 0.7455 | 0.7379 |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.0975 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/fusion/s43/fused_max/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
