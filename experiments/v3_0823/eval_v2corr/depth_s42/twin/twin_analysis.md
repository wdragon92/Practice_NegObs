# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/eval_v2corr/depth_s42/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/eval_v2corr/depth_s42/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/dataset_manifest_v2corr.json`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **408** · pose-matched (kept) **366** · excluded **42** · kept pairs carrying >=1 GT cell **327** (delta_score > 0 in 300/327)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 177 | 0.7596 [0.7165, 0.8016] * | 0.7573 [0.7142, 0.7994] * |
| E | 45 | 0.5741 [0.4366, 0.7102] * | 0.5739 [0.4364, 0.7100] * |
| H | 96 | 0.4131 [0.3236, 0.5013] * | 0.4185 [0.3299, 0.5065] * |
| all | 366 | 0.6202 [0.5766, 0.6634] * | 0.5734 [0.5306, 0.6148] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 27 | 0.1440 [0.0613, 0.2392] * | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 93 | 0.5992 [0.5274, 0.6716] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 201 | 0.7233 [0.6734, 0.7710] * | 33 | 0.6318 [0.4662, 0.7842] * |
| 3b [8,12) m | 327 | 0.6135 [0.5699, 0.6570] * | 96 | 0.4131 [0.3236, 0.5014] * |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 72 | 0 | 1.00 | 0.8811 | 0.8811 |
| scene07 | 30 | 42 | 0.42 | 0.7184 | 0.7412 |
| scene14 | 72 | 0 | 1.00 | 0.6756 | 0.6193 |
| scene15 | 72 | 0 | 1.00 | 0.2135 | 0.2148 |
| scene18 | 72 | 0 | 1.00 | 0.7022 | 0.7021 |
| sceneC2 | 24 | 0 | 1.00 | 0.5728 | 0.5662 |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.0002 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/eval_v2corr/depth_s42/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
