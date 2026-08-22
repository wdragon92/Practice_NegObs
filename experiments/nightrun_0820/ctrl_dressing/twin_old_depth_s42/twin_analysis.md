# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/nightrun_0820/ctrl_dressing/eval_old_depth_s42/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/nightrun_0820/ctrl_dressing/eval_old_depth_s42/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/dataset_manifest_v2_full.json`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **48** · pose-matched (kept) **48** · excluded **0** · kept pairs carrying >=1 GT cell **24** (delta_score > 0 in 21/24)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 24 | 0.5728 [0.4396, 0.6995] * | 0.5662 [0.4311, 0.6955] * |
| E | 0 | n/a [n/a, n/a] | n/a [n/a, n/a] |
| H | 0 | n/a [n/a, n/a] | n/a [n/a, n/a] |
| all | 48 | 0.5728 [0.4396, 0.6995] * | 0.2832 [0.1837, 0.3891] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 0 | n/a [n/a, n/a] | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 12 | 0.1902 [0.0937, 0.2866] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 21 | 0.5316 [0.3676, 0.6929] * | 0 | n/a [n/a, n/a] |
| 3b [8,12) m | 24 | 0.6459 [0.5194, 0.7582] * | 0 | n/a [n/a, n/a] |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| sceneC2 | 24 | 0 | 1.00 | 0.5728 | 0.5662 |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.0002 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/nightrun_0820/ctrl_dressing/twin_old_depth_s42/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
