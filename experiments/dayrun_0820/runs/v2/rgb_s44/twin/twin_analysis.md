# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s44/eval_test/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s44/eval_test/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/dataset_manifest_v2_full.json`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **408** · pose-matched (kept) **366** · excluded **42** · kept pairs carrying >=1 GT cell **312** (delta_score > 0 in 249/312)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 165 | 0.4083 [0.3509, 0.4647] * | 0.4173 [0.3600, 0.4737] * |
| E | 45 | 0.0494 [-0.0069, 0.1110] | 0.0456 [-0.0107, 0.1069] |
| H | 96 | 0.3267 [0.2492, 0.4037] * | 0.3157 [0.2426, 0.3880] * |
| all | 366 | 0.3232 [0.2807, 0.3656] * | 0.3429 [0.3041, 0.3818] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 27 | 0.0036 [-0.0010, 0.0086] | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 93 | 0.2192 [0.1698, 0.2712] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 201 | 0.2846 [0.2366, 0.3336] * | 33 | 0.0326 [-0.0104, 0.0844] |
| 3b [8,12) m | 312 | 0.3032 [0.2609, 0.3463] * | 96 | 0.3352 [0.2561, 0.4134] * |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 72 | 0 | 1.00 | 0.5061 | 0.5058 |
| scene07 | 30 | 42 | 0.42 | 0.4940 | 0.7403 |
| scene14 | 72 | 0 | 1.00 | 0.5440 | 0.5227 |
| scene15 | 72 | 0 | 1.00 | 0.0279 | 0.0489 |
| scene18 | 72 | 0 | 1.00 | 0.0475 | 0.0455 |
| sceneC2 | 24 | 0 | 1.00 | 0.8372 | 0.8841 |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.0518 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s44/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
