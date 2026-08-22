# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s42_aux/eval_test/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s42_aux/eval_test/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/dataset_manifest_v2_full.json`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **408** · pose-matched (kept) **366** · excluded **42** · kept pairs carrying >=1 GT cell **312** (delta_score > 0 in 284/312)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 165 | 0.4927 [0.4302, 0.5528] * | 0.4881 [0.4248, 0.5484] * |
| E | 45 | 0.0337 [0.0119, 0.0611] * | 0.0332 [0.0111, 0.0608] * |
| H | 96 | 0.3256 [0.2701, 0.3826] * | 0.3101 [0.2538, 0.3687] * |
| all | 366 | 0.3675 [0.3261, 0.4087] * | 0.3711 [0.3335, 0.4092] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 27 | 0.0256 [0.0117, 0.0433] * | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 93 | 0.4076 [0.3271, 0.4899] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 201 | 0.3428 [0.2901, 0.3974] * | 33 | 0.1632 [0.1000, 0.2299] * |
| 3b [8,12) m | 312 | 0.3685 [0.3273, 0.4100] * | 96 | 0.3328 [0.2764, 0.3913] * |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 72 | 0 | 1.00 | 0.8444 | 0.8444 |
| scene07 | 30 | 42 | 0.42 | 0.7123 | 0.7551 |
| scene14 | 72 | 0 | 1.00 | 0.4754 | 0.4608 |
| scene15 | 72 | 0 | 1.00 | 0.1113 | 0.0949 |
| scene18 | 72 | 0 | 1.00 | 0.0229 | 0.0226 |
| sceneC2 | 24 | 0 | 1.00 | 0.3560 | 0.3560 |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.0918 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s42_aux/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
