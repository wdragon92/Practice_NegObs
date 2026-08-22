# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/depth_s43/eval_test/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/depth_s43/eval_test/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/dataset_manifest_v2s_full.json`
grid: **PROVISIONAL-GRID-V2S** (4 bands x 10 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **408** · pose-matched (kept) **366** · excluded **42** · kept pairs carrying >=1 GT cell **312** (delta_score > 0 in 306/312)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 165 | 0.5500 [0.5075, 0.5917] * | 0.5519 [0.5102, 0.5932] * |
| E | 45 | 0.5723 [0.4431, 0.6995] * | 0.5721 [0.4430, 0.6994] * |
| H | 96 | 0.3623 [0.2902, 0.4342] * | 0.3647 [0.2931, 0.4363] * |
| all | 366 | 0.4864 [0.4486, 0.5243] * | 0.4337 [0.3976, 0.4697] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 27 | 0.3948 [0.2673, 0.5276] * | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 93 | 0.3756 [0.3053, 0.4463] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 201 | 0.3537 [0.3025, 0.4053] * | 33 | 0.2379 [0.1154, 0.3644] * |
| 3b [8,12) m | 312 | 0.4794 [0.4416, 0.5169] * | 96 | 0.3622 [0.2901, 0.4340] * |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 72 | 0 | 1.00 | 0.6724 | 0.6724 |
| scene07 | 30 | 42 | 0.42 | 0.8267 | 0.3740 |
| scene14 | 72 | 0 | 1.00 | 0.5437 | 0.4984 |
| scene15 | 72 | 0 | 1.00 | 0.1001 | 0.1099 |
| scene18 | 72 | 0 | 1.00 | 0.6211 | 0.6210 |
| sceneC2 | 24 | 0 | 1.00 | 0.4412 | 0.4412 |
| sceneN3 | 24 | 0 | 1.00 | n/a | -0.0000 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/depth_s43/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
