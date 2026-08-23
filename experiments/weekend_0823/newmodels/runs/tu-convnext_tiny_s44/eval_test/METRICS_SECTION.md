# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `experiments/weekend_0823/newmodels/runs/tu-convnext_tiny_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.33 (fitted on **val**, val cell-F1 0.3129) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 2691 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.5389 [0.4667, 0.6111] | 0.0622 [0.0532, 0.0715] | 180 |
| E | 0.8667 [0.7586, 0.9565] | 0.1121 [0.0963, 0.1302] | 45 |
| H | 0.6250 [0.5269, 0.7204] | 0.1316 [0.1166, 0.1469] | 96 |
| **any tier (frame detection rate)** | 0.5994 [0.5460, 0.6512] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.7279 [0.6848, 0.7707] |
| cell FPR (off frames) | 0.0425 [0.0394, 0.0457] |
| cell FPR (negative cells of on frames) | 0.0090 [0.0061, 0.0121] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.1637 [0.1506, 0.1769] | 0.1701 [0.1575, 0.1826] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1314 [0.1196, 0.1432] |
| cell recall | 0.0806 [0.0729, 0.0886] |
| cell precision | 0.3540 [0.3120, 0.3969] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.33

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.7889 [0.7278, 0.8466] | 0.2663 [0.2440, 0.2895] | 180 |
| E | 1.0000 [1.0000, 1.0000] | 0.4856 [0.4337, 0.5506] | 45 |
| H | 0.8646 [0.7922, 0.9302] | 0.5520 [0.5086, 0.5975] | 96 |
| **any tier (frame detection rate)** | 0.8349 [0.7935, 0.8742] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.8725 [0.8396, 0.9040] |
| cell FPR (off frames) | 0.1658 [0.1586, 0.1726] |
| cell FPR (negative cells of on frames) | 0.0464 [0.0385, 0.0548] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.0011 [0.0000, 0.0037] | 0.0015 [0.0000, 0.0040] |
| 3b [8,12) m | 0.6998 [0.6703, 0.7271] | 0.6618 [0.6332, 0.6887] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3555 [0.3325, 0.3777] |
| cell recall | 0.3452 [0.3227, 0.3694] |
| cell precision | 0.3663 [0.3305, 0.4020] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3913 | 0.1314 | 0.0000 |
| cell_recall | 0.4251 | 0.0806 | 0.0000 |
| cell_precision | 0.3625 | 0.3540 | n/a |
| frame_det_rate | 0.9083 | 0.5994 | 0.0000 |
| frame_recall_V | 0.8611 | 0.5389 | 0.0000 |
| frame_recall_E | 1.0000 | 0.8667 | 0.0000 |
| frame_recall_H | 0.9583 | 0.6250 | 0.0000 |
| cell_recall_V | 0.3232 | 0.0622 | 0.0000 |
| cell_recall_E | 0.5862 | 0.1121 | 0.0000 |
| cell_recall_H | 0.7049 | 0.1316 | 0.0000 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_recall | 0.0057 | 0.0000 | 0.0000 |
| band4_cell_recall | 0.8590 | 0.1637 | 0.0000 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0123 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.8127 | 0.1701 | 0.0000 |
| frame_fa_off | 0.9436 | 0.7279 | 0.0000 |
| cell_fpr_off | 0.2062 | 0.0425 | 0.0000 |
| cell_fpr_on_neg | 0.0602 | 0.0090 | 0.0000 |
