# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/depth_s42/eval_test/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/depth_s42/eval_test/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/dataset_manifest_v2s_full.json`
grid: **PROVISIONAL-GRID-V2S** (4 bands x 10 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **408** · pose-matched (kept) **366** · excluded **42** · kept pairs carrying >=1 GT cell **312** (delta_score > 0 in 309/312)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 165 | 0.6640 [0.6170, 0.7087] * | 0.6662 [0.6204, 0.7099] * |
| E | 45 | 0.5319 [0.4082, 0.6527] * | 0.5319 [0.4082, 0.6527] * |
| H | 96 | 0.3700 [0.2908, 0.4487] * | 0.3682 [0.2884, 0.4470] * |
| all | 366 | 0.5436 [0.5023, 0.5851] * | 0.5175 [0.4778, 0.5559] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 27 | 0.4467 [0.3106, 0.5845] * | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 93 | 0.5144 [0.4465, 0.5812] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 201 | 0.7187 [0.6687, 0.7669] * | 33 | 0.6364 [0.4748, 0.7856] * |
| 3b [8,12) m | 312 | 0.5338 [0.4935, 0.5751] * | 96 | 0.3691 [0.2902, 0.4475] * |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 72 | 0 | 1.00 | 0.7322 | 0.7322 |
| scene07 | 30 | 42 | 0.42 | 0.9420 | 0.8368 |
| scene14 | 72 | 0 | 1.00 | 0.6010 | 0.5510 |
| scene15 | 72 | 0 | 1.00 | 0.0962 | 0.1028 |
| scene18 | 72 | 0 | 1.00 | 0.6541 | 0.6541 |
| sceneC2 | 24 | 0 | 1.00 | 0.7312 | 0.7248 |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.0000 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/depth_s42/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
