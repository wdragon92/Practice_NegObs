# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/eval_v2corr/b2_s44/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/eval_v2corr/b2_s44/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/dataset_manifest_v2corr.json`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **408** · pose-matched (kept) **366** · excluded **42** · kept pairs carrying >=1 GT cell **327** (delta_score > 0 in 262/327)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 177 | 0.3579 [0.3055, 0.4097] * | 0.3661 [0.3140, 0.4175] * |
| E | 45 | -0.0006 [-0.0016, 0.0002] | -0.0006 [-0.0015, 0.0003] |
| H | 96 | 0.1867 [0.1272, 0.2487] * | 0.1866 [0.1270, 0.2487] * |
| all | 366 | 0.2486 [0.2121, 0.2846] * | 0.2455 [0.2121, 0.2788] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 27 | 0.0302 [0.0187, 0.0435] * | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 93 | 0.3009 [0.2372, 0.3677] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 201 | 0.2907 [0.2386, 0.3446] * | 33 | 0.0938 [0.0363, 0.1644] * |
| 3b [8,12) m | 327 | 0.2318 [0.1958, 0.2675] * | 96 | 0.1867 [0.1271, 0.2487] * |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 72 | 0 | 1.00 | 0.4050 | 0.4051 |
| scene07 | 30 | 42 | 0.42 | 0.3868 | 0.4502 |
| scene14 | 72 | 0 | 1.00 | 0.3599 | 0.3674 |
| scene15 | 72 | 0 | 1.00 | 0.1412 | 0.1414 |
| scene18 | 72 | 0 | 1.00 | 0.0242 | 0.0242 |
| sceneC2 | 24 | 0 | 1.00 | 0.3478 | 0.3480 |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.0186 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/eval_v2corr/b2_s44/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
