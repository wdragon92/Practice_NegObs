# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/eval_v2corr/depth_s44/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/eval_v2corr/depth_s44/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/dataset_manifest_v2corr.json`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **408** · pose-matched (kept) **366** · excluded **42** · kept pairs carrying >=1 GT cell **327** (delta_score > 0 in 309/327)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 177 | 0.6164 [0.5660, 0.6659] * | 0.6160 [0.5653, 0.6662] * |
| E | 45 | 0.5368 [0.4102, 0.6625] * | 0.5368 [0.4102, 0.6625] * |
| H | 96 | 0.3666 [0.2850, 0.4472] * | 0.3675 [0.2862, 0.4479] * |
| all | 366 | 0.5224 [0.4807, 0.5643] * | 0.4746 [0.4343, 0.5147] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 27 | 0.4473 [0.3313, 0.5573] * | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 93 | 0.5348 [0.4694, 0.5999] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 201 | 0.4398 [0.3820, 0.4973] * | 33 | 0.3015 [0.1654, 0.4416] * |
| 3b [8,12) m | 327 | 0.5269 [0.4869, 0.5675] * | 96 | 0.3786 [0.2984, 0.4572] * |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 72 | 0 | 1.00 | 0.7924 | 0.7924 |
| scene07 | 30 | 42 | 0.42 | 0.6116 | 0.5469 |
| scene14 | 72 | 0 | 1.00 | 0.6074 | 0.5557 |
| scene15 | 72 | 0 | 1.00 | 0.0864 | 0.0781 |
| scene18 | 72 | 0 | 1.00 | 0.6599 | 0.6599 |
| sceneC2 | 24 | 0 | 1.00 | 0.2962 | 0.2952 |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.0000 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/eval_v2corr/depth_s44/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
