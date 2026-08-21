# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/probe_holes_0820/eval/depth_s42/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/probe_holes_0820/eval/depth_s42/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/probe_holes_0820/dataset_manifest_probe.json`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 1e-06 · paired bootstrap 10000x seed 42

pairs found **72** · pose-matched (kept) **72** · excluded **0** · kept pairs carrying >=1 GT cell **72** (delta_score > 0 in 36/72)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 15 | 0.2787 [0.1791, 0.3924] * | 0.1897 [0.1583, 0.2221] * |
| E | 27 | 0.0724 [0.0448, 0.1005] * | 0.0886 [0.0547, 0.1228] * |
| H | 30 | -0.0001 [-0.0002, -0.0000] * | 0.0001 [-0.0000, 0.0001] |
| all | 72 | 0.0852 [0.0539, 0.1219] * | 0.0728 [0.0515, 0.0946] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 6 | 0.0054 [-0.0002, 0.0111] | 3 | -0.0002 [-0.0002, -0.0002] * |
| 2 [2,5) m | 51 | 0.0957 [0.0570, 0.1417] * | 21 | -0.0001 [-0.0003, -0.0000] * |
| 3a [5,8) m | 21 | 0.1777 [0.0768, 0.2994] * | 3 | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 18 | 0.0133 [-0.0054, 0.0361] | 9 | 0.0000 [0.0000, 0.0000] |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| probeH1 | 24 | 0 | 1.00 | 0.1876 | 0.1414 |
| probeH2 | 24 | 0 | 1.00 | 0.0679 | 0.0769 |
| probeH3 | 24 | 0 | 1.00 | 0.0000 | 0.0000 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/probe_holes_0820/eval/depth_s42/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
