# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/b2_s43/eval_test/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/b2_s43/eval_test/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/dataset_manifest_v2s_full.json`
grid: **PROVISIONAL-GRID-V2S** (4 bands x 10 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **408** · pose-matched (kept) **366** · excluded **42** · kept pairs carrying >=1 GT cell **312** (delta_score > 0 in 273/312)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 165 | 0.4736 [0.4137, 0.5312] * | 0.4529 [0.3945, 0.5100] * |
| E | 45 | 0.0302 [-0.0132, 0.0832] | 0.0317 [-0.0120, 0.0850] |
| H | 96 | 0.3926 [0.3278, 0.4575] * | 0.4244 [0.3608, 0.4870] * |
| all | 366 | 0.3819 [0.3406, 0.4225] * | 0.3568 [0.3197, 0.3939] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 27 | 0.0196 [0.0025, 0.0543] * | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 93 | 0.1864 [0.1355, 0.2423] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 201 | 0.2669 [0.2174, 0.3172] * | 33 | 0.0721 [0.0096, 0.1450] * |
| 3b [8,12) m | 312 | 0.3919 [0.3499, 0.4328] * | 96 | 0.4090 [0.3421, 0.4756] * |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 72 | 0 | 1.00 | 0.5650 | 0.5650 |
| scene07 | 30 | 42 | 0.42 | 0.9624 | 0.3117 |
| scene14 | 72 | 0 | 1.00 | 0.5126 | 0.5274 |
| scene15 | 72 | 0 | 1.00 | 0.3393 | 0.3622 |
| scene18 | 72 | 0 | 1.00 | 0.0339 | 0.0348 |
| sceneC2 | 24 | 0 | 1.00 | 0.4991 | 0.4984 |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.0853 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/b2_s43/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
