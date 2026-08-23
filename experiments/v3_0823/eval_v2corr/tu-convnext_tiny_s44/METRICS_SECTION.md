# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/newmodels/runs/tu-convnext_tiny_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.33 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 369 | 219 | 45 | 96 | 7 | 2856 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4612 [0.3959, 0.5276] | 0.0598 [0.0513, 0.0690] | 219 |
| E | 0.8667 [0.7586, 0.9565] | 0.1121 [0.0963, 0.1302] | 45 |
| H | 0.6250 [0.5269, 0.7204] | 0.1316 [0.1166, 0.1469] | 96 |
| **any tier (frame detection rate)** | 0.5420 [0.4917, 0.5918] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.7279 [0.6848, 0.7707] |
| cell FPR (off frames) | 0.0425 [0.0394, 0.0457] |
| cell FPR (negative cells of on frames) | 0.0083 [0.0056, 0.0113] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.1510 [0.1379, 0.1647] | 0.1701 [0.1575, 0.1826] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1280 [0.1164, 0.1398] |
| cell recall | 0.0777 [0.0704, 0.0856] |
| cell precision | 0.3622 [0.3199, 0.4051] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.33

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.7352 [0.6751, 0.7920] | 0.2636 [0.2416, 0.2862] | 219 |
| E | 1.0000 [1.0000, 1.0000] | 0.4856 [0.4337, 0.5506] | 45 |
| H | 0.8646 [0.7922, 0.9302] | 0.5520 [0.5086, 0.5975] | 96 |
| **any tier (frame detection rate)** | 0.7940 [0.7514, 0.8347] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.8725 [0.8396, 0.9040] |
| cell FPR (off frames) | 0.1658 [0.1586, 0.1726] |
| cell FPR (negative cells of on frames) | 0.0407 [0.0330, 0.0488] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.0011 [0.0000, 0.0036] | 0.0015 [0.0000, 0.0040] |
| 3b [8,12) m | 0.6571 [0.6248, 0.6872] | 0.6618 [0.6332, 0.6887] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3587 [0.3362, 0.3808] |
| cell recall | 0.3386 [0.3170, 0.3618] |
| cell precision | 0.3813 [0.3453, 0.4169] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3959 | 0.1280 | 0.0000 |
| cell_recall | 0.4167 | 0.0777 | 0.0000 |
| cell_precision | 0.3771 | 0.3622 | n/a |
| frame_det_rate | 0.8645 | 0.5420 | 0.0000 |
| frame_recall_V | 0.8037 | 0.4612 | 0.0000 |
| frame_recall_E | 1.0000 | 0.8667 | 0.0000 |
| frame_recall_H | 0.9583 | 0.6250 | 0.0000 |
| cell_recall_V | 0.3195 | 0.0598 | 0.0000 |
| cell_recall_E | 0.5862 | 0.1121 | 0.0000 |
| cell_recall_H | 0.7049 | 0.1316 | 0.0000 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_recall | 0.0056 | 0.0000 | 0.0000 |
| band4_cell_recall | 0.8061 | 0.1510 | 0.0000 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0123 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.8127 | 0.1701 | 0.0000 |
| frame_fa_off | 0.9436 | 0.7279 | 0.0000 |
| cell_fpr_off | 0.2062 | 0.0425 | 0.0000 |
| cell_fpr_on_neg | 0.0534 | 0.0083 | 0.0000 |
