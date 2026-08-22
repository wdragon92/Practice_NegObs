# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `runs/yolo_s44/cells_test/per_frame.csv`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.25 · tau_star = 0.25 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 2691 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.25

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.1722 [0.1190, 0.2303] | 0.0188 [0.0131, 0.0248] | 180 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 96 |
| **any tier (frame detection rate)** | 0.0948 [0.0642, 0.1272] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0417 [0.0231, 0.0618] |
| cell FPR (off frames) | 0.0025 [0.0013, 0.0037] |
| cell FPR (negative cells of on frames) | 0.0051 [0.0033, 0.0070] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1026 [0.0519, 0.1574] | 0.0074 [0.0034, 0.0121] |
| 2 [2,5) m | 0.0608 [0.0381, 0.0860] | 0.0025 [0.0005, 0.0048] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0252 [0.0172, 0.0335] |
| cell recall | 0.0130 [0.0088, 0.0173] |
| cell precision | 0.4217 [0.3093, 0.5341] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.25

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.1722 [0.1190, 0.2303] | 0.0188 [0.0131, 0.0248] | 180 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 96 |
| **any tier (frame detection rate)** | 0.0948 [0.0642, 0.1272] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0417 [0.0231, 0.0618] |
| cell FPR (off frames) | 0.0025 [0.0013, 0.0037] |
| cell FPR (negative cells of on frames) | 0.0051 [0.0033, 0.0070] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1026 [0.0519, 0.1574] | 0.0074 [0.0034, 0.0121] |
| 2 [2,5) m | 0.0608 [0.0381, 0.0860] | 0.0025 [0.0005, 0.0048] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0252 [0.0172, 0.0335] |
| cell recall | 0.0130 [0.0088, 0.0173] |
| cell precision | 0.4217 [0.3093, 0.5341] |

## 2. Threshold sweep

| metric | tau=0.1 | tau=0.25 | tau=0.5 |
|---|---|---|---|
| cell_f1 | 0.0370 | 0.0252 | 0.0175 |
| cell_recall | 0.0197 | 0.0130 | 0.0089 |
| cell_precision | 0.3118 | 0.4217 | 0.5217 |
| frame_det_rate | 0.1101 | 0.0948 | 0.0673 |
| frame_recall_V | 0.1944 | 0.1722 | 0.1222 |
| frame_recall_E | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_H | 0.0104 | 0.0000 | 0.0000 |
| cell_recall_V | 0.0268 | 0.0188 | 0.0129 |
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
| cell_fpr_on_neg | 0.0141 | 0.0051 | 0.0022 |
