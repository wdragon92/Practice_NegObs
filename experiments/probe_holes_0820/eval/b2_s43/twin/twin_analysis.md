# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/probe_holes_0820/eval/b2_s43/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/probe_holes_0820/eval/b2_s43/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/probe_holes_0820/dataset_manifest_probe.json`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 1e-06 · paired bootstrap 10000x seed 42

pairs found **72** · pose-matched (kept) **72** · excluded **0** · kept pairs carrying >=1 GT cell **72** (delta_score > 0 in 55/72)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 15 | 0.1228 [0.0940, 0.1561] * | 0.0465 [0.0323, 0.0603] * |
| E | 27 | 0.0521 [0.0356, 0.0689] * | 0.0322 [0.0196, 0.0463] * |
| H | 30 | 0.0128 [-0.0012, 0.0298] | 0.0054 [-0.0033, 0.0160] |
| all | 72 | 0.0505 [0.0364, 0.0653] * | 0.0240 [0.0163, 0.0322] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 6 | 0.0457 [0.0127, 0.0790] * | 3 | 0.0264 [-0.0149, 0.0600] |
| 2 [2,5) m | 51 | 0.0666 [0.0484, 0.0855] * | 21 | 0.0212 [0.0017, 0.0446] * |
| 3a [5,8) m | 21 | 0.0338 [0.0188, 0.0508] * | 3 | 0.0007 [-0.0021, 0.0033] |
| 3b [8,12) m | 18 | 0.0120 [0.0004, 0.0239] * | 9 | -0.0074 [-0.0154, 0.0005] |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| probeH1 | 24 | 0 | 1.00 | 0.0979 | 0.0402 |
| probeH2 | 24 | 0 | 1.00 | 0.0569 | 0.0344 |
| probeH3 | 24 | 0 | 1.00 | -0.0034 | -0.0027 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/probe_holes_0820/eval/b2_s43/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
