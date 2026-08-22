# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/b2_s42/eval_test/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/b2_s42/eval_test/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/dataset_manifest_v2s_full.json`
grid: **PROVISIONAL-GRID-V2S** (4 bands x 10 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **408** · pose-matched (kept) **366** · excluded **42** · kept pairs carrying >=1 GT cell **312** (delta_score > 0 in 281/312)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 165 | 0.5537 [0.4996, 0.6062] * | 0.5514 [0.4984, 0.6033] * |
| E | 45 | 0.0321 [0.0048, 0.0715] * | 0.0322 [0.0049, 0.0717] * |
| H | 96 | 0.1769 [0.1300, 0.2263] * | 0.1774 [0.1308, 0.2279] * |
| all | 366 | 0.3574 [0.3178, 0.3970] * | 0.3509 [0.3142, 0.3874] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 27 | 0.0446 [0.0278, 0.0624] * | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 93 | 0.1128 [0.0784, 0.1526] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 201 | 0.2675 [0.2214, 0.3157] * | 33 | 0.0636 [0.0373, 0.0957] * |
| 3b [8,12) m | 312 | 0.3543 [0.3145, 0.3942] * | 96 | 0.1769 [0.1299, 0.2268] * |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 72 | 0 | 1.00 | 0.6157 | 0.6157 |
| scene07 | 30 | 42 | 0.42 | 0.8932 | 0.6312 |
| scene14 | 72 | 0 | 1.00 | 0.2491 | 0.2681 |
| scene15 | 72 | 0 | 1.00 | 0.2828 | 0.2824 |
| scene18 | 72 | 0 | 1.00 | 0.0716 | 0.0717 |
| sceneC2 | 24 | 0 | 1.00 | 0.8271 | 0.8236 |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.0239 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/b2_s42/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
