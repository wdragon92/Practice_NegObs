# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s42/eval_test/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s42/eval_test/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/dataset_manifest_v2_full.json`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **408** · pose-matched (kept) **366** · excluded **42** · kept pairs carrying >=1 GT cell **312** (delta_score > 0 in 267/312)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 165 | 0.3066 [0.2496, 0.3645] * | 0.3051 [0.2484, 0.3628] * |
| E | 45 | 0.0054 [0.0024, 0.0093] * | 0.0133 [0.0032, 0.0298] * |
| H | 96 | 0.0735 [0.0340, 0.1125] * | 0.0743 [0.0348, 0.1132] * |
| all | 366 | 0.1857 [0.1507, 0.2219] * | 0.1651 [0.1341, 0.1980] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 27 | 0.0164 [0.0038, 0.0319] * | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 93 | 0.1730 [0.1230, 0.2275] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 201 | 0.2364 [0.1863, 0.2868] * | 33 | -0.0201 [-0.0992, 0.0464] |
| 3b [8,12) m | 312 | 0.1844 [0.1499, 0.2202] * | 96 | 0.0903 [0.0599, 0.1233] * |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 72 | 0 | 1.00 | 0.2388 | 0.2387 |
| scene07 | 30 | 42 | 0.42 | 0.7282 | 0.1284 |
| scene14 | 72 | 0 | 1.00 | 0.1301 | 0.1269 |
| scene15 | 72 | 0 | 1.00 | 0.1370 | 0.1413 |
| scene18 | 72 | 0 | 1.00 | 0.0016 | 0.0067 |
| sceneC2 | 24 | 0 | 1.00 | 0.7419 | 0.7419 |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.0740 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s42/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
