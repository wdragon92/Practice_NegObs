# TWIN_ANALYSIS — on/off paired context-causality

on: `experiments/mainrun_0819/runs/rgb_s42/eval_test/per_frame_on.csv` · off: `experiments/mainrun_0819/runs/rgb_s42/eval_test/per_frame_off.csv` · manifest: `experiments/mainrun_0819/dataset_manifest_v1.json`
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 1e-06 · paired bootstrap 10000x seed 42

pairs found **168** · pose-matched (kept) **117** · excluded **51** · kept pairs carrying >=1 GT cell **93** (delta_score > 0 in 88/93)

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 63 | 0.4062 [0.3242, 0.4885] | 0.4082 [0.3261, 0.4911] |
| E | 9 | 0.1891 [0.0402, 0.3337] | 0.1891 [0.0402, 0.3337] |
| H | 21 | 0.2398 [0.1556, 0.3313] | 0.2398 [0.1556, 0.3313] |
| all | 117 | 0.3476 [0.2859, 0.4103] | 0.3291 [0.2761, 0.3815] |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 18 | 6 | 0.75 | 0.6290 | 0.6290 |
| scene07 | 3 | 21 | 0.12 | 0.3794 | 0.3794 |
| scene14 | 24 | 0 | 1.00 | 0.3607 | 0.3607 |
| scene15 | 24 | 0 | 1.00 | 0.2608 | 0.2660 |
| scene18 | 24 | 0 | 1.00 | 0.2064 | 0.2064 |
| sceneC2 | 0 | 24 | 0.00 | n/a | n/a |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.2521 |

per-pair rows: `experiments/mainrun_0819/runs/rgb_s42/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
