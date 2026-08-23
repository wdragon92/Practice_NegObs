# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.45 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4409 [0.3409, 0.5426] | 0.3294 [0.2695, 0.3854] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.2778 [0.1757, 0.3846] | 0.1528 [0.0914, 0.2176] | 72 |
| **any tier (frame detection rate)** | 0.3697 [0.2982, 0.4439] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0799 [0.0500, 0.1126] |
| cell FPR (off frames) | 0.0106 [0.0058, 0.0160] |
| cell FPR (negative cells of on frames) | 0.0053 [0.0024, 0.0087] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.1061 [0.0301, 0.1949] | 0.0007 [0.0000, 0.0022] |
| 3a [5,8) m | 0.2966 [0.2320, 0.3613] | 0.0104 [0.0041, 0.0181] |
| 3b [8,12) m | 0.2909 [0.2279, 0.3563] | 0.0312 [0.0168, 0.0477] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3978 [0.3356, 0.4540] |
| cell recall | 0.2658 [0.2174, 0.3126] |
| cell precision | 0.7896 [0.7017, 0.8647] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.45

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4624 [0.3636, 0.5652] | 0.3789 [0.3155, 0.4372] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.3472 [0.2368, 0.4615] | 0.1921 [0.1234, 0.2624] | 72 |
| **any tier (frame detection rate)** | 0.4121 [0.3381, 0.4884] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1076 [0.0730, 0.1460] |
| cell FPR (off frames) | 0.0167 [0.0102, 0.0239] |
| cell FPR (negative cells of on frames) | 0.0107 [0.0060, 0.0162] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.1591 [0.0741, 0.2558] | 0.0028 [0.0000, 0.0066] |
| 3a [5,8) m | 0.3465 [0.2768, 0.4158] | 0.0201 [0.0107, 0.0312] |
| 3b [8,12) m | 0.3348 [0.2690, 0.4018] | 0.0437 [0.0266, 0.0629] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4351 [0.3728, 0.4899] |
| cell recall | 0.3117 [0.2598, 0.3608] |
| cell precision | 0.7206 [0.6280, 0.8000] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4990 | 0.3978 | 0.1918 |
| cell_recall | 0.4967 | 0.2658 | 0.1075 |
| cell_precision | 0.5013 | 0.7896 | 0.8897 |
| frame_det_rate | 0.5879 | 0.3697 | 0.2121 |
| frame_recall_V | 0.5914 | 0.4409 | 0.2903 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.5833 | 0.2778 | 0.1111 |
| cell_recall_V | 0.5599 | 0.3294 | 0.1432 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.3843 | 0.1528 | 0.0440 |
| band1_cell_recall | 0.0370 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.5227 | 0.1061 | 0.0076 |
| band3_cell_recall | 0.5144 | 0.2966 | 0.1365 |
| band4_cell_recall | 0.5000 | 0.2909 | 0.1152 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0167 | 0.0007 | 0.0000 |
| band3_cell_fpr_off | 0.1000 | 0.0104 | 0.0000 |
| band4_cell_fpr_off | 0.1257 | 0.0312 | 0.0111 |
| frame_fa_off | 0.3160 | 0.0799 | 0.0208 |
| cell_fpr_off | 0.0606 | 0.0106 | 0.0028 |
| cell_fpr_on_neg | 0.0535 | 0.0053 | 0.0000 |
