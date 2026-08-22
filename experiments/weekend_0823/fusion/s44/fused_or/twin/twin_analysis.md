# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/fusion/s44/fused_or/eval_test/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/fusion/s44/fused_or/eval_test/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/dataset_manifest_v2_full.json`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **408** · pose-matched (kept) **366** · excluded **42** · kept pairs carrying >=1 GT cell **312** (delta_score > 0 in 254/312)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 165 | 0.4350 [0.3770, 0.4914] * | 0.4389 [0.3806, 0.4945] * |
| E | 45 | 0.0494 [-0.0069, 0.1110] | 0.0665 [0.0035, 0.1336] * |
| H | 96 | 0.3261 [0.2488, 0.4030] * | 0.2873 [0.2179, 0.3565] * |
| all | 366 | 0.3371 [0.2941, 0.3795] * | 0.3478 [0.3088, 0.3867] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 27 | 0.2582 [0.1161, 0.4075] * | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 93 | 0.2937 [0.2334, 0.3561] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 201 | 0.2877 [0.2397, 0.3363] * | 33 | 0.0445 [-0.0030, 0.0985] |
| 3b [8,12) m | 312 | 0.3031 [0.2607, 0.3461] * | 96 | 0.3346 [0.2556, 0.4126] * |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 72 | 0 | 1.00 | 0.5366 | 0.5340 |
| scene07 | 30 | 42 | 0.42 | 0.6191 | 0.7653 |
| scene14 | 72 | 0 | 1.00 | 0.5432 | 0.4848 |
| scene15 | 72 | 0 | 1.00 | 0.0261 | 0.0377 |
| scene18 | 72 | 0 | 1.00 | 0.0696 | 0.0806 |
| sceneC2 | 24 | 0 | 1.00 | 0.8372 | 0.8841 |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.0518 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/fusion/s44/fused_or/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
