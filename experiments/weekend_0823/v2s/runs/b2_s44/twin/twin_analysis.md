# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/b2_s44/eval_test/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/b2_s44/eval_test/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/dataset_manifest_v2s_full.json`
grid: **PROVISIONAL-GRID-V2S** (4 bands x 10 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **408** · pose-matched (kept) **366** · excluded **42** · kept pairs carrying >=1 GT cell **312** (delta_score > 0 in 297/312)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 165 | 0.4569 [0.3961, 0.5173] * | 0.4551 [0.3940, 0.5149] * |
| E | 45 | 0.0019 [0.0008, 0.0038] * | 0.0017 [0.0006, 0.0036] * |
| H | 96 | 0.2237 [0.1650, 0.2844] * | 0.2624 [0.2044, 0.3212] * |
| all | 366 | 0.3111 [0.2696, 0.3527] * | 0.3018 [0.2643, 0.3397] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 27 | 0.0126 [0.0043, 0.0227] * | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 93 | 0.1554 [0.1026, 0.2143] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 201 | 0.2872 [0.2380, 0.3381] * | 33 | 0.0194 [0.0063, 0.0352] * |
| 3b [8,12) m | 312 | 0.3057 [0.2643, 0.3471] * | 96 | 0.2236 [0.1649, 0.2843] * |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 72 | 0 | 1.00 | 0.4599 | 0.4599 |
| scene07 | 30 | 42 | 0.42 | 0.9283 | 0.2517 |
| scene14 | 72 | 0 | 1.00 | 0.3964 | 0.4256 |
| scene15 | 72 | 0 | 1.00 | 0.1593 | 0.2181 |
| scene18 | 72 | 0 | 1.00 | 0.0300 | 0.0298 |
| sceneC2 | 24 | 0 | 1.00 | 0.7750 | 0.7752 |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.1116 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/b2_s44/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
