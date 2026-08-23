# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/eval_v2corr/rgb_s42/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/eval_v2corr/rgb_s42/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/dataset_manifest_v2corr.json`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **408** · pose-matched (kept) **366** · excluded **42** · kept pairs carrying >=1 GT cell **327** (delta_score > 0 in 283/327)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 177 | 0.4625 [0.4087, 0.5152] * | 0.4693 [0.4150, 0.5226] * |
| E | 45 | 0.1637 [0.1250, 0.2034] * | 0.1698 [0.1208, 0.2184] * |
| H | 96 | 0.1701 [0.1237, 0.2176] * | 0.1697 [0.1219, 0.2199] * |
| all | 366 | 0.3314 [0.2947, 0.3689] * | 0.3283 [0.2927, 0.3642] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 27 | 0.0883 [0.0540, 0.1269] * | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 93 | 0.3675 [0.2958, 0.4380] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 201 | 0.3504 [0.2965, 0.4051] * | 33 | -0.0486 [-0.1287, 0.0191] |
| 3b [8,12) m | 327 | 0.3342 [0.2976, 0.3711] * | 96 | 0.1850 [0.1388, 0.2328] * |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 72 | 0 | 1.00 | 0.6822 | 0.6822 |
| scene07 | 30 | 42 | 0.42 | 0.7738 | 0.8460 |
| scene14 | 72 | 0 | 1.00 | 0.2809 | 0.2827 |
| scene15 | 72 | 0 | 1.00 | 0.0166 | 0.0159 |
| scene18 | 72 | 0 | 1.00 | 0.1628 | 0.1666 |
| sceneC2 | 24 | 0 | 1.00 | 0.4805 | 0.4762 |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.0311 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/eval_v2corr/rgb_s42/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
