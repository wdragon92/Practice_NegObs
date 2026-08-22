# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/rgb_s42/eval_test/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/rgb_s42/eval_test/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/dataset_manifest_v2s_full.json`
grid: **PROVISIONAL-GRID-V2S** (4 bands x 10 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **408** · pose-matched (kept) **366** · excluded **42** · kept pairs carrying >=1 GT cell **312** (delta_score > 0 in 266/312)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 165 | 0.3691 [0.3228, 0.4156] * | 0.3550 [0.3051, 0.4039] * |
| E | 45 | -0.0048 [-0.0797, 0.0679] | -0.0056 [-0.0876, 0.0737] |
| H | 96 | 0.2798 [0.2350, 0.3242] * | 0.2731 [0.2278, 0.3183] * |
| all | 366 | 0.2857 [0.2524, 0.3185] * | 0.2855 [0.2540, 0.3168] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 27 | 0.0624 [0.0131, 0.1275] * | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 93 | 0.2372 [0.1788, 0.2980] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 201 | 0.2098 [0.1645, 0.2549] * | 33 | 0.0175 [-0.0054, 0.0386] |
| 3b [8,12) m | 312 | 0.2873 [0.2572, 0.3177] * | 96 | 0.2914 [0.2480, 0.3340] * |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 72 | 0 | 1.00 | 0.4658 | 0.4660 |
| scene07 | 30 | 42 | 0.42 | 0.6532 | 0.5706 |
| scene14 | 72 | 0 | 1.00 | 0.3963 | 0.3925 |
| scene15 | 72 | 0 | 1.00 | 0.2435 | 0.2126 |
| scene18 | 72 | 0 | 1.00 | -0.0018 | -0.0017 |
| sceneC2 | 24 | 0 | 1.00 | 0.3380 | 0.3019 |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.1304 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/rgb_s42/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
