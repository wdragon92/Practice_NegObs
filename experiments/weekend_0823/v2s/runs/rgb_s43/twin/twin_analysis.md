# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/rgb_s43/eval_test/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/rgb_s43/eval_test/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/dataset_manifest_v2s_full.json`
grid: **PROVISIONAL-GRID-V2S** (4 bands x 10 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 0.15 · paired bootstrap 10000x seed 42

pairs found **408** · pose-matched (kept) **366** · excluded **42** · kept pairs carrying >=1 GT cell **312** (delta_score > 0 in 263/312)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 165 | 0.3852 [0.3423, 0.4284] * | 0.3873 [0.3445, 0.4302] * |
| E | 45 | 0.0421 [-0.0157, 0.1045] | 0.0310 [-0.0281, 0.0946] |
| H | 96 | 0.0955 [0.0702, 0.1228] * | 0.1117 [0.0832, 0.1427] * |
| all | 366 | 0.2426 [0.2124, 0.2736] * | 0.2623 [0.2330, 0.2915] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 27 | 0.1408 [0.0653, 0.2242] * | 0 | n/a [n/a, n/a] |
| 2 [2,5) m | 93 | 0.4094 [0.3355, 0.4844] * | 0 | n/a [n/a, n/a] |
| 3a [5,8) m | 201 | 0.3011 [0.2546, 0.3488] * | 33 | 0.1117 [0.0674, 0.1615] * |
| 3b [8,12) m | 312 | 0.2427 [0.2124, 0.2730] * | 96 | 0.0969 [0.0706, 0.1245] * |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 72 | 0 | 1.00 | 0.5550 | 0.5561 |
| scene07 | 30 | 42 | 0.42 | 0.5782 | 0.6024 |
| scene14 | 72 | 0 | 1.00 | 0.1681 | 0.1901 |
| scene15 | 72 | 0 | 1.00 | 0.1274 | 0.1379 |
| scene18 | 72 | 0 | 1.00 | 0.0473 | 0.0361 |
| sceneC2 | 24 | 0 | 1.00 | 0.3582 | 0.3569 |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.1294 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/rgb_s43/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
