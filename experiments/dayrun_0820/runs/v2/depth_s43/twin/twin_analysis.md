# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s43/eval_test/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s43/eval_test/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/dataset_manifest_v2_full.json`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **408** · pose-matched (kept) **366** · excluded **42** · kept pairs carrying >=1 GT cell **312** (delta_score > 0 in 291/312)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 165 | 0.8683 [0.8269, 0.9057] * | 0.8739 [0.8352, 0.9086] * |
| E | 45 | 0.5931 [0.4498, 0.7355] * | 0.5931 [0.4498, 0.7355] * |
| H | 96 | 0.4403 [0.3516, 0.5276] * | 0.4505 [0.3624, 0.5360] * |
| all | 366 | 0.6803 [0.6334, 0.7266] * | 0.6152 [0.5702, 0.6596] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 27 | 0.2490 [0.1036, 0.4098] * | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 93 | 0.7017 [0.6189, 0.7817] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 201 | 0.8139 [0.7667, 0.8575] * | 33 | 0.6675 [0.5200, 0.8029] * |
| 3b [8,12) m | 312 | 0.6559 [0.6081, 0.7028] * | 96 | 0.4403 [0.3516, 0.5276] * |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 72 | 0 | 1.00 | 0.9134 | 0.9130 |
| scene07 | 30 | 42 | 0.42 | 0.9995 | 0.5329 |
| scene14 | 72 | 0 | 1.00 | 0.6486 | 0.5945 |
| scene15 | 72 | 0 | 1.00 | 0.3986 | 0.4409 |
| scene18 | 72 | 0 | 1.00 | 0.6897 | 0.6897 |
| sceneC2 | 24 | 0 | 1.00 | 0.8050 | 0.8012 |
| sceneN3 | 24 | 0 | 1.00 | n/a | -0.0000 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s43/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
