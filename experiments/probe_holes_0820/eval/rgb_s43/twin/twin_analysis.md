# TWIN_ANALYSIS — on/off paired context-causality

on: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/probe_holes_0820/eval/rgb_s43/per_frame_on.csv` · off: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/probe_holes_0820/eval/rgb_s43/per_frame_off.csv` · manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/probe_holes_0820/dataset_manifest_probe.json`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors)
pose keys: `d,h_rel,yaw,pitch,ground_z` · tol 1e-06 · paired bootstrap 10000x seed 42

pairs found **72** · pose-matched (kept) **72** · excluded **0** · kept pairs carrying >=1 GT cell **72** (delta_score > 0 in 52/72)

`*` marks a CI excluding 0.

## 1. Mean delta by tier (paired bootstrap 95% CI)

| tier | n pairs | delta_score (GT cells) [95% CI] | delta_frame (all cells) [95% CI] |
|---|---|---|---|
| V | 15 | 0.2275 [0.1113, 0.3622] * | 0.3752 [0.2675, 0.4789] * |
| E | 27 | 0.0111 [0.0036, 0.0198] * | 0.0288 [0.0134, 0.0471] * |
| H | 30 | 0.0011 [-0.0030, 0.0053] | 0.0006 [-0.0018, 0.0031] |
| all | 72 | 0.0520 [0.0230, 0.0879] * | 0.0892 [0.0515, 0.1322] * |

> delta_score is n/a where no kept pair of that tier has a GT-positive cell; `all` covers every kept pair, including tiers off/H_weak/none_in_fov.

## 2. Mean delta by distance band (GT-positive cells of that band only)

| band | n pairs w/ GT in band | delta [95% CI] | n H pairs | delta on H tier [95% CI] |
|---|---|---|---|---|
| 1 [0,2) m | 6 | 0.0078 [0.0001, 0.0192] * | 3 | 0.0001 [-0.0000, 0.0002] |
| 2 [2,5) m | 51 | 0.0401 [0.0171, 0.0688] * | 21 | 0.0006 [-0.0007, 0.0022] |
| 3a [5,8) m | 21 | 0.1026 [0.0190, 0.2062] * | 3 | 0.0072 [-0.0350, 0.0378] |
| 3b [8,12) m | 18 | 0.0103 [0.0012, 0.0212] * | 9 | 0.0012 [-0.0057, 0.0083] |

> A band row answers 'is the model's firing in this band caused by the drop, or is it a distance prior?' — a near-zero delta with a high recall in the same band is the prior signature.

## 3. Per-scene pairs and mean delta

| scene | kept | excluded | match rate | mean delta_score | mean delta_frame |
|---|---|---|---|---|---|
| probeH1 | 24 | 0 | 1.00 | 0.1490 | 0.2412 |
| probeH2 | 24 | 0 | 1.00 | 0.0057 | 0.0257 |
| probeH3 | 24 | 0 | 1.00 | 0.0012 | 0.0009 |

per-pair rows: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/probe_holes_0820/eval/rgb_s43/twin/twin_pairs.csv` (`kept`/`mismatch` carry the pose-filter verdict).
