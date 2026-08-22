# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/rgb_s44/eval_test/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/rgb_s44/eval_test/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/dataset_manifest_v2s_full.json`
grid: **PROVISIONAL-GRID-V2S** (4 bands x 10 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **408** · pose-matched (kept) **366** · excluded **42** · kept pairs carrying >=1 GT cell **312** (delta_score > 0 in 273/312)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 165 | 0.4114 [0.3631, 0.4599] * | 0.4125 [0.3642, 0.4609] * |
| E | 45 | 0.4109 [0.3263, 0.4928] * | 0.3814 [0.2877, 0.4698] * |
| H | 96 | 0.0610 [0.0354, 0.0880] * | 0.0668 [0.0380, 0.0970] * |
| all | 366 | 0.2973 [0.2625, 0.3329] * | 0.2920 [0.2605, 0.3241] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 27 | 0.1209 [0.0614, 0.1947] * | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 93 | 0.3521 [0.2809, 0.4246] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 201 | 0.3487 [0.2989, 0.3984] * | 33 | -0.0208 [-0.0765, 0.0228] |
| 3b [8,12) m | 312 | 0.2843 [0.2522, 0.3163] * | 96 | 0.0674 [0.0444, 0.0927] * |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 72 | 0 | 1.00 | 0.5998 | 0.5997 |
| scene07 | 30 | 42 | 0.42 | 0.7915 | 0.5623 |
| scene14 | 72 | 0 | 1.00 | 0.1175 | 0.1352 |
| scene15 | 72 | 0 | 1.00 | 0.0805 | 0.0820 |
| scene18 | 72 | 0 | 1.00 | 0.3430 | 0.3211 |
| sceneC2 | 24 | 0 | 1.00 | 0.2743 | 0.2786 |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.0576 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/rgb_s44/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
