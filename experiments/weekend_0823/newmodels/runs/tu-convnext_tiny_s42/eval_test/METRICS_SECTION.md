# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `experiments/weekend_0823/newmodels/runs/tu-convnext_tiny_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.31 (fitted on **val**, val cell-F1 0.3277) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 2691 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9333 [0.8941, 0.9674] | 0.0900 [0.0839, 0.0969] | 180 |
| E | 1.0000 [1.0000, 1.0000] | 0.1293 [0.1151, 0.1473] | 45 |
| H | 0.8438 [0.7692, 0.9121] | 0.1720 [0.1553, 0.1915] | 96 |
| **any tier (frame detection rate)** | 0.8991 [0.8649, 0.9306] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.0500 [0.0500, 0.0500] |
| cell FPR (negative cells of on frames) | 0.0208 [0.0181, 0.0235] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.2217 [0.2140, 0.2300] | 0.2000 [0.2000, 0.2000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1677 [0.1587, 0.1767] |
| cell recall | 0.1093 [0.1027, 0.1163] |
| cell precision | 0.3603 [0.3272, 0.3922] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.31

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.4068 [0.3843, 0.4316] | 180 |
| E | 1.0000 [1.0000, 1.0000] | 0.6207 [0.5587, 0.6979] | 45 |
| H | 1.0000 [1.0000, 1.0000] | 0.7325 [0.6801, 0.7918] | 96 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.2500 [0.2500, 0.2500] |
| cell FPR (negative cells of on frames) | 0.1306 [0.1193, 0.1417] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3917 [0.3681, 0.4139] |
| cell recall | 0.4928 [0.4682, 0.5193] |
| cell precision | 0.3250 [0.2951, 0.3549] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4041 | 0.1677 | 0.0000 |
| cell_recall | 0.5697 | 0.1093 | 0.0000 |
| cell_precision | 0.3131 | 0.3603 | n/a |
| frame_det_rate | 1.0000 | 0.8991 | 0.0000 |
| frame_recall_V | 1.0000 | 0.9333 | 0.0000 |
| frame_recall_E | 1.0000 | 1.0000 | 0.0000 |
| frame_recall_H | 1.0000 | 0.8438 | 0.0000 |
| cell_recall_V | 0.4871 | 0.0900 | 0.0000 |
| cell_recall_E | 0.6897 | 0.1293 | 0.0000 |
| cell_recall_H | 0.8025 | 0.1720 | 0.0000 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_recall | 0.2379 | 0.0000 | 0.0000 |
| band4_cell_recall | 1.0000 | 0.2217 | 0.0000 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.2000 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 1.0000 | 0.2000 | 0.0000 |
| frame_fa_off | 1.0000 | 1.0000 | 0.0000 |
| cell_fpr_off | 0.3000 | 0.0500 | 0.0000 |
| cell_fpr_on_neg | 0.1673 | 0.0208 | 0.0000 |
