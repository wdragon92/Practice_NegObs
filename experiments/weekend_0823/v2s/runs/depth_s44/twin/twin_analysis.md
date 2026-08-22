# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/depth_s44/eval_test/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/depth_s44/eval_test/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/dataset_manifest_v2s_full.json`
grid: **PROVISIONAL-GRID-V2S** (4 bands x 10 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **408** · pose-matched (kept) **366** · excluded **42** · kept pairs carrying >=1 GT cell **312** (delta_score > 0 in 300/312)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 165 | 0.8403 [0.8033, 0.8749] * | 0.8113 [0.7698, 0.8497] * |
| E | 45 | 0.6050 [0.4651, 0.7430] * | 0.6050 [0.4651, 0.7430] * |
| H | 96 | 0.4373 [0.3505, 0.5214] * | 0.4279 [0.3422, 0.5111] * |
| all | 366 | 0.6707 [0.6270, 0.7142] * | 0.6105 [0.5676, 0.6526] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 27 | 0.2724 [0.1299, 0.4312] * | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 93 | 0.7072 [0.6343, 0.7771] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 201 | 0.8346 [0.7950, 0.8713] * | 33 | 0.7797 [0.6799, 0.8689] * |
| 3b [8,12) m | 312 | 0.6320 [0.5883, 0.6769] * | 96 | 0.4051 [0.3191, 0.4898] * |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 72 | 0 | 1.00 | 0.8748 | 0.8748 |
| scene07 | 30 | 42 | 0.42 | 0.9942 | 0.8615 |
| scene14 | 72 | 0 | 1.00 | 0.6410 | 0.5876 |
| scene15 | 72 | 0 | 1.00 | 0.3702 | 0.3149 |
| scene18 | 72 | 0 | 1.00 | 0.7231 | 0.7231 |
| sceneC2 | 24 | 0 | 1.00 | 0.8039 | 0.7321 |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.0000 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/depth_s44/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
