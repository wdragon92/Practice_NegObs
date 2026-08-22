# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `experiments/dayrun_0820/runs/yolo_oracle_ceiling_full/per_frame.csv`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.25 · tau_star = 0.25 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 2691 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.25

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4000 [0.3297, 0.4722] | 0.0643 [0.0504, 0.0793] | 180 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 96 |
| **any tier (frame detection rate)** | 0.2202 [0.1763, 0.2654] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (negative cells of on frames) | 0.1196 [0.1083, 0.1313] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.3333 [0.2414, 0.4382] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.1429 [0.1071, 0.1826] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.0241 [0.0115, 0.0390] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.0045 [0.0015, 0.0084] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0693 [0.0532, 0.0862] |
| cell recall | 0.0446 [0.0342, 0.0556] |
| cell precision | 0.1550 [0.1170, 0.1961] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.25

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4000 [0.3297, 0.4722] | 0.0643 [0.0504, 0.0793] | 180 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 96 |
| **any tier (frame detection rate)** | 0.2202 [0.1763, 0.2654] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (negative cells of on frames) | 0.1196 [0.1083, 0.1313] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.3333 [0.2414, 0.4382] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.1429 [0.1071, 0.1826] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.0241 [0.0115, 0.0390] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.0045 [0.0015, 0.0084] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0693 [0.0532, 0.0862] |
| cell recall | 0.0446 [0.0342, 0.0556] |
| cell precision | 0.1550 [0.1170, 0.1961] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.0693 | 0.0693 | 0.0693 |
| cell_recall | 0.0446 | 0.0446 | 0.0446 |
| cell_precision | 0.1550 | 0.1550 | 0.1550 |
| frame_det_rate | 0.2202 | 0.2202 | 0.2202 |
| frame_recall_V | 0.4000 | 0.4000 | 0.4000 |
| frame_recall_E | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_H | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_V | 0.0643 | 0.0643 | 0.0643 |
| cell_recall_E | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_H | 0.0000 | 0.0000 | 0.0000 |
| band1_cell_recall | 0.3333 | 0.3333 | 0.3333 |
| band2_cell_recall | 0.1429 | 0.1429 | 0.1429 |
| band3_cell_recall | 0.0241 | 0.0241 | 0.0241 |
| band4_cell_recall | 0.0045 | 0.0045 | 0.0045 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| frame_fa_off | 0.0000 | 0.0000 | 0.0000 |
| cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| cell_fpr_on_neg | 0.1196 | 0.1196 | 0.1196 |
