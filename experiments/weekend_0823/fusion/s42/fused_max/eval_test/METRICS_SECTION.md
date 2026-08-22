# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/fusion/s42/fused_max/per_frame.csv`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 2691 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8333 [0.7760, 0.8859] | 0.4936 [0.4337, 0.5541] | 180 |
| E | 0.6000 [0.4528, 0.7436] | 0.3592 [0.2626, 0.4556] | 45 |
| H | 0.5938 [0.4946, 0.6923] | 0.2527 [0.1989, 0.3107] | 96 |
| **any tier (frame detection rate)** | 0.7339 [0.6846, 0.7816] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3750 [0.3283, 0.4218] |
| cell FPR (off frames) | 0.0527 [0.0443, 0.0615] |
| cell FPR (negative cells of on frames) | 0.0943 [0.0794, 0.1099] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0342 [0.0000, 0.0809] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.3466 [0.2553, 0.4415] | 0.0088 [0.0030, 0.0162] |
| 3a [5,8) m | 0.4103 [0.3531, 0.4679] | 0.0662 [0.0488, 0.0842] |
| 3b [8,12) m | 0.5121 [0.4640, 0.5584] | 0.1358 [0.1151, 0.1565] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4871 [0.4452, 0.5267] |
| cell recall | 0.4352 [0.3901, 0.4797] |
| cell precision | 0.5531 [0.5017, 0.6012] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8333 [0.7760, 0.8859] | 0.4936 [0.4337, 0.5541] | 180 |
| E | 0.6000 [0.4528, 0.7436] | 0.3592 [0.2626, 0.4556] | 45 |
| H | 0.5938 [0.4946, 0.6923] | 0.2527 [0.1989, 0.3107] | 96 |
| **any tier (frame detection rate)** | 0.7339 [0.6846, 0.7816] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3750 [0.3283, 0.4218] |
| cell FPR (off frames) | 0.0527 [0.0443, 0.0615] |
| cell FPR (negative cells of on frames) | 0.0943 [0.0794, 0.1099] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0342 [0.0000, 0.0809] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.3466 [0.2553, 0.4415] | 0.0088 [0.0030, 0.0162] |
| 3a [5,8) m | 0.4103 [0.3531, 0.4679] | 0.0662 [0.0488, 0.0842] |
| 3b [8,12) m | 0.5121 [0.4640, 0.5584] | 0.1358 [0.1151, 0.1565] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4871 [0.4452, 0.5267] |
| cell recall | 0.4352 [0.3901, 0.4797] |
| cell precision | 0.5531 [0.5017, 0.6012] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5292 | 0.4871 | 0.3934 |
| cell_recall | 0.5756 | 0.4352 | 0.2928 |
| cell_precision | 0.4897 | 0.5531 | 0.5992 |
| frame_det_rate | 0.8410 | 0.7339 | 0.5719 |
| frame_recall_V | 0.8944 | 0.8333 | 0.7278 |
| frame_recall_E | 0.7111 | 0.6000 | 0.4000 |
| frame_recall_H | 0.7917 | 0.5938 | 0.3750 |
| cell_recall_V | 0.6125 | 0.4936 | 0.3650 |
| cell_recall_E | 0.5833 | 0.3592 | 0.1178 |
| cell_recall_H | 0.4183 | 0.2527 | 0.1359 |
| band1_cell_recall | 0.0940 | 0.0342 | 0.0171 |
| band2_cell_recall | 0.4974 | 0.3466 | 0.2275 |
| band3_cell_recall | 0.5552 | 0.4103 | 0.2736 |
| band4_cell_recall | 0.6538 | 0.5121 | 0.3484 |
| band1_cell_fpr_off | 0.0005 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0328 | 0.0088 | 0.0029 |
| band3_cell_fpr_off | 0.1137 | 0.0662 | 0.0328 |
| band4_cell_fpr_off | 0.2284 | 0.1358 | 0.0681 |
| frame_fa_off | 0.4779 | 0.3750 | 0.2255 |
| cell_fpr_off | 0.0939 | 0.0527 | 0.0260 |
| cell_fpr_on_neg | 0.1551 | 0.0943 | 0.0576 |
