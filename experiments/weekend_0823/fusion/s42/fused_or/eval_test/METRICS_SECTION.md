# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/fusion/s42/fused_or/per_frame.csv`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 2691 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8611 [0.8084, 0.9105] | 0.5032 [0.4459, 0.5621] | 180 |
| E | 0.6000 [0.4528, 0.7436] | 0.3592 [0.2626, 0.4556] | 45 |
| H | 0.5938 [0.4946, 0.6923] | 0.2527 [0.1989, 0.3107] | 96 |
| **any tier (frame detection rate)** | 0.7492 [0.7009, 0.7961] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3775 [0.3308, 0.4246] |
| cell FPR (off frames) | 0.0531 [0.0447, 0.0619] |
| cell FPR (negative cells of on frames) | 0.0965 [0.0815, 0.1122] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1026 [0.0412, 0.1731] | 0.0005 [0.0000, 0.0015] |
| 2 [2,5) m | 0.3624 [0.2729, 0.4550] | 0.0098 [0.0037, 0.0175] |
| 3a [5,8) m | 0.4126 [0.3560, 0.4703] | 0.0662 [0.0488, 0.0842] |
| 3b [8,12) m | 0.5136 [0.4658, 0.5600] | 0.1358 [0.1151, 0.1565] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4912 [0.4505, 0.5297] |
| cell recall | 0.4418 [0.3979, 0.4853] |
| cell precision | 0.5530 [0.5024, 0.6004] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8611 [0.8084, 0.9105] | 0.5032 [0.4459, 0.5621] | 180 |
| E | 0.6000 [0.4528, 0.7436] | 0.3592 [0.2626, 0.4556] | 45 |
| H | 0.5938 [0.4946, 0.6923] | 0.2527 [0.1989, 0.3107] | 96 |
| **any tier (frame detection rate)** | 0.7492 [0.7009, 0.7961] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3775 [0.3308, 0.4246] |
| cell FPR (off frames) | 0.0531 [0.0447, 0.0619] |
| cell FPR (negative cells of on frames) | 0.0965 [0.0815, 0.1122] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1026 [0.0412, 0.1731] | 0.0005 [0.0000, 0.0015] |
| 2 [2,5) m | 0.3624 [0.2729, 0.4550] | 0.0098 [0.0037, 0.0175] |
| 3a [5,8) m | 0.4126 [0.3560, 0.4703] | 0.0662 [0.0488, 0.0842] |
| 3b [8,12) m | 0.5136 [0.4658, 0.5600] | 0.1358 [0.1151, 0.1565] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4912 [0.4505, 0.5297] |
| cell recall | 0.4418 [0.3979, 0.4853] |
| cell precision | 0.5530 [0.5024, 0.6004] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5300 | 0.4912 | 0.3944 |
| cell_recall | 0.5797 | 0.4418 | 0.2939 |
| cell_precision | 0.4881 | 0.5530 | 0.5992 |
| frame_det_rate | 0.8563 | 0.7492 | 0.5749 |
| frame_recall_V | 0.9222 | 0.8611 | 0.7333 |
| frame_recall_E | 0.7111 | 0.6000 | 0.4000 |
| frame_recall_H | 0.7917 | 0.5938 | 0.3750 |
| cell_recall_V | 0.6184 | 0.5032 | 0.3666 |
| cell_recall_E | 0.5833 | 0.3592 | 0.1178 |
| cell_recall_H | 0.4183 | 0.2527 | 0.1359 |
| band1_cell_recall | 0.1368 | 0.1026 | 0.0171 |
| band2_cell_recall | 0.4974 | 0.3624 | 0.2354 |
| band3_cell_recall | 0.5586 | 0.4126 | 0.2736 |
| band4_cell_recall | 0.6561 | 0.5136 | 0.3484 |
| band1_cell_fpr_off | 0.0005 | 0.0005 | 0.0000 |
| band2_cell_fpr_off | 0.0328 | 0.0098 | 0.0029 |
| band3_cell_fpr_off | 0.1137 | 0.0662 | 0.0328 |
| band4_cell_fpr_off | 0.2284 | 0.1358 | 0.0681 |
| frame_fa_off | 0.4779 | 0.3775 | 0.2255 |
| cell_fpr_off | 0.0939 | 0.0531 | 0.0260 |
| cell_fpr_on_neg | 0.1591 | 0.0965 | 0.0580 |
