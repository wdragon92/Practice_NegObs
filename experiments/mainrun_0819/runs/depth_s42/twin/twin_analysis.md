# TWIN_ANALYSIS — on/off paired context-causality

on: `experiments/mainrun_0819/runs/depth_s42/eval_test/per_frame_on.csv` · off: `experiments/mainrun_0819/runs/depth_s42/eval_test/per_frame_off.csv` · manifest: `experiments/mainrun_0819/dataset_manifest_v1.json`
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 1e-06 · paired bootstrap 10000x seed 42

pairs found **168** · pose-matched (kept) **117** · excluded **51** · kept pairs carrying >=1 GT cell **93** (delta_score > 0 in 90/93)

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 63 | 0.6291 [0.5630, 0.6924] | 0.6262 [0.5600, 0.6896] |
| E | 9 | 0.0301 [0.0056, 0.0564] | 0.0301 [0.0056, 0.0564] |
| H | 21 | 0.5842 [0.4482, 0.7139] | 0.5920 [0.4616, 0.7161] |
| all | 117 | 0.5610 [0.4972, 0.6227] | 0.4458 [0.3823, 0.5105] |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| scene05 | 18 | 6 | 0.75 | 0.7370 | 0.7370 |
| scene07 | 3 | 21 | 0.12 | 0.8963 | 0.8963 |
| scene14 | 24 | 0 | 1.00 | 0.7378 | 0.7378 |
| scene15 | 24 | 0 | 1.00 | 0.3659 | 0.3653 |
| scene18 | 24 | 0 | 1.00 | 0.4053 | 0.4053 |
| sceneC2 | 0 | 24 | 0.00 | n/a | n/a |
| sceneN3 | 24 | 0 | 1.00 | n/a | 0.0001 |

per-pair rows: `experiments/mainrun_0819/runs/depth_s42/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
