# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/nightrun_0820/ctrl_dressing/eval_old_s44/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/nightrun_0820/ctrl_dressing/eval_old_s44/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/dataset_manifest_v2_full.json`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **48** · pose-matched (kept) **48** · excluded **0** · kept pairs carrying >=1 GT cell **24** (delta_score > 0 in 24/24)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 24 | 0.8372 [0.7321, 0.9208] * | 0.8841 [0.8261, 0.9334] * |
| E | 0 | n/a [n/a, n/a] | n/a [n/a, n/a] |
| H | 0 | n/a [n/a, n/a] | n/a [n/a, n/a] |
| all | 48 | 0.8372 [0.7321, 0.9208] * | 0.4679 [0.3457, 0.5916] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 0 | n/a [n/a, n/a] | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 12 | 0.1702 [0.0917, 0.2555] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 21 | 0.6834 [0.5206, 0.8324] * | 0 | n/a [n/a, n/a] |
| 3b [8,12) m | 24 | 0.8110 [0.6997, 0.9007] * | 0 | n/a [n/a, n/a] |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| sceneC2 | 24 | 0 | 1.00 | 0.8372 | 0.8841 |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.0518 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/nightrun_0820/ctrl_dressing/twin_old_s44/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
