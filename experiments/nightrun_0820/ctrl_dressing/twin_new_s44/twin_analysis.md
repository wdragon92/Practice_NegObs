# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/nightrun_0820/ctrl_dressing/eval_new_s44/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/nightrun_0820/ctrl_dressing/eval_new_s44/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/nightrun_0820/ctrl_dressing/manifest_ctrl.json`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **48** · pose-matched (kept) **48** · excluded **0** · kept pairs carrying >=1 GT cell **24** (delta_score > 0 in 19/24)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 24 | 0.0921 [-0.0063, 0.1833] | 0.0902 [0.0380, 0.1463] * |
| E | 0 | n/a [n/a, n/a] | n/a [n/a, n/a] |
| H | 0 | n/a [n/a, n/a] | n/a [n/a, n/a] |
| all | 48 | 0.0921 [-0.0063, 0.1833] | 0.0443 [0.0165, 0.0762] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 0 | n/a [n/a, n/a] | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 12 | 0.0611 [-0.0394, 0.1574] | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 21 | 0.3737 [0.1987, 0.5562] * | 0 | n/a [n/a, n/a] |
| 3b [8,12) m | 24 | 0.0659 [-0.0402, 0.1654] | 0 | n/a [n/a, n/a] |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| sceneC2 | 24 | 0 | 1.00 | 0.0921 | 0.0902 |
| sceneN3 | 24 | 0 | 1.00 | n/a | -0.0016 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/nightrun_0820/ctrl_dressing/twin_new_s44/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
