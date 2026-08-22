# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/fusion/s44/fused_max/eval_test/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/fusion/s44/fused_max/eval_test/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/dataset_manifest_v2_full.json`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **408** · pose-matched (kept) **366** · excluded **42** · kept pairs carrying >=1 GT cell **312** (delta_score > 0 in 254/312)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 165 | 0.4258 [0.3682, 0.4815] * | 0.4289 [0.3707, 0.4845] * |
| E | 45 | 0.0494 [-0.0069, 0.1110] | 0.0559 [-0.0021, 0.1184] |
| H | 96 | 0.3267 [0.2492, 0.4037] * | 0.3024 [0.2318, 0.3731] * |
| all | 366 | 0.3324 [0.2895, 0.3743] * | 0.3459 [0.3075, 0.3847] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 27 | 0.2025 [0.0893, 0.3255] * | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 93 | 0.2791 [0.2228, 0.3371] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 201 | 0.2861 [0.2382, 0.3351] * | 33 | 0.0386 [-0.0058, 0.0902] |
| 3b [8,12) m | 312 | 0.3032 [0.2609, 0.3463] * | 96 | 0.3352 [0.2561, 0.4134] * |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 72 | 0 | 1.00 | 0.5270 | 0.5256 |
| scene07 | 30 | 42 | 0.42 | 0.5786 | 0.7572 |
| scene14 | 72 | 0 | 1.00 | 0.5440 | 0.5049 |
| scene15 | 72 | 0 | 1.00 | 0.0279 | 0.0364 |
| scene18 | 72 | 0 | 1.00 | 0.0596 | 0.0640 |
| sceneC2 | 24 | 0 | 1.00 | 0.8372 | 0.8841 |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.0518 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/fusion/s44/fused_max/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
