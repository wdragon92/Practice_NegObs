# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/eval_v2corr/yolo_s44/cells_test/per_frame.csv`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.25 · tau_star = 0.25 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 369 | 219 | 45 | 96 | 7 | 2856 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.25

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.1416 [0.0977, 0.1897] | 0.0173 [0.0120, 0.0229] | 219 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 96 |
| **any tier (frame detection rate)** | 0.0840 [0.0569, 0.1129] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0417 [0.0231, 0.0618] |
| cell FPR (off frames) | 0.0025 [0.0013, 0.0037] |
| cell FPR (negative cells of on frames) | 0.0053 [0.0034, 0.0073] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1026 [0.0519, 0.1574] | 0.0074 [0.0034, 0.0121] |
| 2 [2,5) m | 0.0608 [0.0381, 0.0860] | 0.0025 [0.0005, 0.0048] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0238 [0.0163, 0.0318] |
| cell recall | 0.0123 [0.0083, 0.0164] |
| cell precision | 0.4217 [0.3093, 0.5341] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.25

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.1416 [0.0977, 0.1897] | 0.0173 [0.0120, 0.0229] | 219 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 96 |
| **any tier (frame detection rate)** | 0.0840 [0.0569, 0.1129] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0417 [0.0231, 0.0618] |
| cell FPR (off frames) | 0.0025 [0.0013, 0.0037] |
| cell FPR (negative cells of on frames) | 0.0053 [0.0034, 0.0073] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1026 [0.0519, 0.1574] | 0.0074 [0.0034, 0.0121] |
| 2 [2,5) m | 0.0608 [0.0381, 0.0860] | 0.0025 [0.0005, 0.0048] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0238 [0.0163, 0.0318] |
| cell recall | 0.0123 [0.0083, 0.0164] |
| cell precision | 0.4217 [0.3093, 0.5341] |

## 2. Threshold sweep

| metric | tau=0.1 | tau=0.25 | tau=0.5 |
|---|---|---|---|
| cell_f1 | 0.0350 | 0.0238 | 0.0165 |
| cell_recall | 0.0186 | 0.0123 | 0.0084 |
| cell_precision | 0.3118 | 0.4217 | 0.5217 |
| frame_det_rate | 0.0976 | 0.0840 | 0.0596 |
| frame_recall_V | 0.1598 | 0.1416 | 0.1005 |
| frame_recall_E | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_H | 0.0104 | 0.0000 | 0.0000 |
| cell_recall_V | 0.0247 | 0.0173 | 0.0119 |
| cell_recall_E | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_H | 0.0064 | 0.0000 | 0.0000 |
| band1_cell_recall | 0.1368 | 0.1026 | 0.0427 |
| band2_cell_recall | 0.0899 | 0.0608 | 0.0503 |
| band3_cell_recall | 0.0034 | 0.0000 | 0.0000 |
| band4_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band1_cell_fpr_off | 0.0113 | 0.0074 | 0.0039 |
| band2_cell_fpr_off | 0.0078 | 0.0025 | 0.0010 |
| band3_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.0005 | 0.0000 | 0.0000 |
| frame_fa_off | 0.0662 | 0.0417 | 0.0221 |
| cell_fpr_off | 0.0049 | 0.0025 | 0.0012 |
| cell_fpr_on_neg | 0.0145 | 0.0053 | 0.0023 |
