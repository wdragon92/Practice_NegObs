# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/rgb_s42/eval_test/per_frame.csv`
grid: **PROVISIONAL-GRID-V2S** (4 bands x 10 sectors = 40 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 4998 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6278 [0.5561, 0.6979] | 0.2327 [0.1808, 0.2877] | 180 |
| E | 0.2000 [0.0870, 0.3250] | 0.0785 [0.0296, 0.1358] | 45 |
| H | 0.7188 [0.6264, 0.8061] | 0.2362 [0.1785, 0.3026] | 96 |
| **any tier (frame detection rate)** | 0.5994 [0.5452, 0.6520] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2206 [0.1810, 0.2615] |
| cell FPR (off frames) | 0.0171 [0.0133, 0.0212] |
| cell FPR (negative cells of on frames) | 0.0778 [0.0657, 0.0907] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0267 [0.0000, 0.0663] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2073 [0.1267, 0.2941] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.1992 [0.1513, 0.2494] | 0.0235 [0.0134, 0.0352] |
| 3b [8,12) m | 0.2416 [0.2071, 0.2779] | 0.0449 [0.0339, 0.0569] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2954 [0.2489, 0.3415] |
| cell recall | 0.2135 [0.1747, 0.2538] |
| cell precision | 0.4791 [0.4138, 0.5413] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6278 [0.5561, 0.6979] | 0.2327 [0.1808, 0.2877] | 180 |
| E | 0.2000 [0.0870, 0.3250] | 0.0785 [0.0296, 0.1358] | 45 |
| H | 0.7188 [0.6264, 0.8061] | 0.2362 [0.1785, 0.3026] | 96 |
| **any tier (frame detection rate)** | 0.5994 [0.5452, 0.6520] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2206 [0.1810, 0.2615] |
| cell FPR (off frames) | 0.0171 [0.0133, 0.0212] |
| cell FPR (negative cells of on frames) | 0.0778 [0.0657, 0.0907] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0267 [0.0000, 0.0663] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2073 [0.1267, 0.2941] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.1992 [0.1513, 0.2494] | 0.0235 [0.0134, 0.0352] |
| 3b [8,12) m | 0.2416 [0.2071, 0.2779] | 0.0449 [0.0339, 0.0569] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2954 [0.2489, 0.3415] |
| cell recall | 0.2135 [0.1747, 0.2538] |
| cell precision | 0.4791 [0.4138, 0.5413] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3948 | 0.2954 | 0.1692 |
| cell_recall | 0.3587 | 0.2135 | 0.1016 |
| cell_precision | 0.4389 | 0.4791 | 0.5050 |
| frame_det_rate | 0.7798 | 0.5994 | 0.3425 |
| frame_recall_V | 0.7778 | 0.6278 | 0.4056 |
| frame_recall_E | 0.4667 | 0.2000 | 0.0889 |
| frame_recall_H | 0.9167 | 0.7188 | 0.3229 |
| cell_recall_V | 0.3559 | 0.2327 | 0.1209 |
| cell_recall_E | 0.2281 | 0.0785 | 0.0193 |
| cell_recall_H | 0.4711 | 0.2362 | 0.0800 |
| band1_cell_recall | 0.0667 | 0.0267 | 0.0000 |
| band2_cell_recall | 0.2843 | 0.2073 | 0.1499 |
| band3_cell_recall | 0.3127 | 0.1992 | 0.1015 |
| band4_cell_recall | 0.4369 | 0.2416 | 0.0970 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0051 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0615 | 0.0235 | 0.0093 |
| band4_cell_fpr_off | 0.1216 | 0.0449 | 0.0110 |
| frame_fa_off | 0.3824 | 0.2206 | 0.0980 |
| cell_fpr_off | 0.0471 | 0.0171 | 0.0051 |
| cell_fpr_on_neg | 0.1346 | 0.0778 | 0.0367 |

## 3. Paired comparison (A = this arm, B = `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/depth_s42/eval_test/per_frame.csv`)

816 common frames · paired percentile bootstrap 10000x seed 42 · threshold 0.5

| metric | A | B | A−B [95% CI] | CI excludes 0 |
|---|---|---|---|---|
| cell_f1 | 0.2954 | 0.6867 | -0.3914 [-0.4550, -0.3277] | yes |
| cell_recall | 0.2135 | 0.7059 | -0.4924 [-0.5575, -0.4249] | yes |
| cell_precision | 0.4791 | 0.6686 | -0.1894 [-0.2580, -0.1248] | yes |
| frame_det_rate | 0.5994 | 0.6789 | -0.0795 [-0.1569, 0.0000] | no |
| frame_recall_V | 0.6278 | 0.8500 | -0.2222 [-0.3200, -0.1244] | yes |
| frame_recall_E | 0.2000 | 0.6000 | -0.4000 [-0.5455, -0.2600] | yes |
| frame_recall_H | 0.7188 | 0.4375 | 0.2812 [0.1294, 0.4301] | yes |
| cell_recall_V | 0.2327 | 0.7196 | -0.4868 [-0.5733, -0.3977] | yes |
| cell_recall_E | 0.0785 | 0.6978 | -0.6193 [-0.7141, -0.5103] | yes |
| cell_recall_H | 0.2362 | 0.6642 | -0.4280 [-0.5471, -0.2853] | yes |
| band1_cell_recall | 0.0267 | 0.3067 | -0.2800 [-0.4477, -0.1158] | yes |
| band2_cell_recall | 0.2073 | 0.4832 | -0.2759 [-0.4225, -0.1228] | yes |
| band3_cell_recall | 0.1992 | 0.8327 | -0.6335 [-0.7015, -0.5626] | yes |
| band4_cell_recall | 0.2416 | 0.7247 | -0.4832 [-0.5405, -0.4222] | yes |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 [0.0000, 0.0000] | no |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 [0.0000, 0.0000] | no |
| band3_cell_fpr_off | 0.0235 | 0.0000 | 0.0235 [0.0134, 0.0352] | yes |
| band4_cell_fpr_off | 0.0449 | 0.0000 | 0.0449 [0.0339, 0.0569] | yes |
| frame_fa_off | 0.2206 | 0.0000 | 0.2206 [0.1810, 0.2615] | yes |
| cell_fpr_off | 0.0171 | 0.0000 | 0.0171 [0.0133, 0.0212] | yes |
| cell_fpr_on_neg | 0.0778 | 0.1545 | -0.0767 [-0.1078, -0.0466] | yes |
