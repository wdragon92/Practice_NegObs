# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s43/eval_test/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s43/eval_test/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/dataset_manifest_v2_full.json`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **408** · pose-matched (kept) **366** · excluded **42** · kept pairs carrying >=1 GT cell **312** (delta_score > 0 in 291/312)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 165 | 0.3986 [0.3626, 0.4329] * | 0.3997 [0.3642, 0.4338] * |
| E | 45 | 0.1998 [0.1252, 0.2762] * | 0.2008 [0.1264, 0.2766] * |
| H | 96 | 0.0688 [0.0507, 0.0880] * | 0.0796 [0.0617, 0.0979] * |
| all | 366 | 0.2626 [0.2349, 0.2905] * | 0.2550 [0.2301, 0.2803] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 27 | 0.0923 [0.0623, 0.1237] * | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 93 | 0.3061 [0.2687, 0.3434] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 201 | 0.3681 [0.3282, 0.4084] * | 33 | 0.0995 [0.0645, 0.1376] * |
| 3b [8,12) m | 312 | 0.2554 [0.2277, 0.2835] * | 96 | 0.0588 [0.0427, 0.0757] * |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 72 | 0 | 1.00 | 0.5571 | 0.5571 |
| scene07 | 30 | 42 | 0.42 | 0.4915 | 0.4113 |
| scene14 | 72 | 0 | 1.00 | 0.1091 | 0.1238 |
| scene15 | 72 | 0 | 1.00 | 0.0770 | 0.0814 |
| scene18 | 72 | 0 | 1.00 | 0.1969 | 0.1975 |
| sceneC2 | 24 | 0 | 1.00 | 0.4980 | 0.4980 |
| sceneN3 | 24 | 0 | 1.00 | n/a | -0.0032 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s43/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
