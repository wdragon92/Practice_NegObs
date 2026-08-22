# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/fusion/s42/fused_or/eval_test/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/fusion/s42/fused_or/eval_test/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/dataset_manifest_v2_full.json`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **408** · pose-matched (kept) **366** · excluded **42** · kept pairs carrying >=1 GT cell **312** (delta_score > 0 in 269/312)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 165 | 0.4598 [0.4063, 0.5133] * | 0.4591 [0.4057, 0.5129] * |
| E | 45 | 0.1637 [0.1250, 0.2034] * | 0.1652 [0.1159, 0.2144] * |
| H | 96 | 0.1701 [0.1237, 0.2176] * | 0.1697 [0.1219, 0.2199] * |
| all | 366 | 0.3197 [0.2836, 0.3571] * | 0.3357 [0.2998, 0.3719] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 27 | 0.2952 [0.2009, 0.3999] * | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 93 | 0.3966 [0.3232, 0.4700] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 201 | 0.3542 [0.3006, 0.4087] * | 33 | -0.0486 [-0.1287, 0.0191] |
| 3b [8,12) m | 312 | 0.3177 [0.2820, 0.3547] * | 96 | 0.1850 [0.1388, 0.2328] * |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 72 | 0 | 1.00 | 0.6822 | 0.6822 |
| scene07 | 30 | 42 | 0.42 | 0.7860 | 0.8460 |
| scene14 | 72 | 0 | 1.00 | 0.2809 | 0.2827 |
| scene15 | 72 | 0 | 1.00 | 0.0166 | 0.0159 |
| scene18 | 72 | 0 | 1.00 | 0.1906 | 0.1916 |
| sceneC2 | 24 | 0 | 1.00 | 0.5185 | 0.5142 |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.0311 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/fusion/s42/fused_or/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
