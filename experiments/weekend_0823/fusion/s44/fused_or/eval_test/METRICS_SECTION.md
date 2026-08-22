# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/fusion/s44/fused_or/per_frame.csv`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 2691 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6556 [0.5843, 0.7243] | 0.2808 [0.2332, 0.3315] | 180 |
| E | 0.1556 [0.0571, 0.2683] | 0.0402 [0.0125, 0.0762] | 45 |
| H | 0.5938 [0.4947, 0.6907] | 0.2505 [0.2031, 0.3017] | 96 |
| **any tier (frame detection rate)** | 0.5719 [0.5176, 0.6271] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2475 [0.2051, 0.2888] |
| cell FPR (off frames) | 0.0301 [0.0241, 0.0364] |
| cell FPR (negative cells of on frames) | 0.0583 [0.0490, 0.0681] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1026 [0.0519, 0.1574] | 0.0074 [0.0034, 0.0121] |
| 2 [2,5) m | 0.1799 [0.1146, 0.2516] | 0.0167 [0.0080, 0.0272] |
| 3a [5,8) m | 0.2034 [0.1604, 0.2500] | 0.0240 [0.0156, 0.0331] |
| 3b [8,12) m | 0.3047 [0.2632, 0.3467] | 0.0725 [0.0569, 0.0887] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3375 [0.2962, 0.3788] |
| cell recall | 0.2456 [0.2105, 0.2833] |
| cell precision | 0.5392 [0.4825, 0.5921] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6556 [0.5843, 0.7243] | 0.2808 [0.2332, 0.3315] | 180 |
| E | 0.1556 [0.0571, 0.2683] | 0.0402 [0.0125, 0.0762] | 45 |
| H | 0.5938 [0.4947, 0.6907] | 0.2505 [0.2031, 0.3017] | 96 |
| **any tier (frame detection rate)** | 0.5719 [0.5176, 0.6271] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2475 [0.2051, 0.2888] |
| cell FPR (off frames) | 0.0301 [0.0241, 0.0364] |
| cell FPR (negative cells of on frames) | 0.0583 [0.0490, 0.0681] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1026 [0.0519, 0.1574] | 0.0074 [0.0034, 0.0121] |
| 2 [2,5) m | 0.1799 [0.1146, 0.2516] | 0.0167 [0.0080, 0.0272] |
| 3a [5,8) m | 0.2034 [0.1604, 0.2500] | 0.0240 [0.0156, 0.0331] |
| 3b [8,12) m | 0.3047 [0.2632, 0.3467] | 0.0725 [0.0569, 0.0887] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3375 [0.2962, 0.3788] |
| cell recall | 0.2456 [0.2105, 0.2833] |
| cell precision | 0.5392 [0.4825, 0.5921] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3936 | 0.3375 | 0.2580 |
| cell_recall | 0.3467 | 0.2456 | 0.1616 |
| cell_precision | 0.4551 | 0.5392 | 0.6388 |
| frame_det_rate | 0.6881 | 0.5719 | 0.3976 |
| frame_recall_V | 0.7333 | 0.6556 | 0.5222 |
| frame_recall_E | 0.3111 | 0.1556 | 0.0444 |
| frame_recall_H | 0.7604 | 0.5938 | 0.3229 |
| cell_recall_V | 0.3735 | 0.2808 | 0.1988 |
| cell_recall_E | 0.1121 | 0.0402 | 0.0057 |
| cell_recall_H | 0.4055 | 0.2505 | 0.1253 |
| band1_cell_recall | 0.1368 | 0.1026 | 0.0427 |
| band2_cell_recall | 0.2804 | 0.1799 | 0.1243 |
| band3_cell_recall | 0.3172 | 0.2034 | 0.1287 |
| band4_cell_recall | 0.4035 | 0.3047 | 0.2044 |
| band1_cell_fpr_off | 0.0093 | 0.0074 | 0.0039 |
| band2_cell_fpr_off | 0.0358 | 0.0167 | 0.0020 |
| band3_cell_fpr_off | 0.0809 | 0.0240 | 0.0093 |
| band4_cell_fpr_off | 0.1412 | 0.0725 | 0.0294 |
| frame_fa_off | 0.3529 | 0.2475 | 0.1275 |
| cell_fpr_off | 0.0668 | 0.0301 | 0.0112 |
| cell_fpr_on_neg | 0.1046 | 0.0583 | 0.0283 |
