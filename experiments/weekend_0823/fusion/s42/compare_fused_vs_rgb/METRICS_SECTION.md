# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `experiments/weekend_0823/fusion/s42/fused_or/per_frame.csv`
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

## 3. Paired comparison (A = this arm, B = `experiments/dayrun_0820/runs/v2/rgb_s42/eval_test/per_frame.csv`)

816 common frames · paired percentile bootstrap 10000x seed 42 · threshold 0.5

| metric | A | B | A−B [95% CI] | CI excludes 0 |
|---|---|---|---|---|
| cell_f1 | 0.4912 | 0.4852 | 0.0060 [0.0017, 0.0110] | yes |
| cell_recall | 0.4418 | 0.4322 | 0.0097 [0.0048, 0.0152] | yes |
| cell_precision | 0.5530 | 0.5530 | 0.0000 [-0.0043, 0.0044] | no |
| frame_det_rate | 0.7492 | 0.7309 | 0.0183 [0.0059, 0.0342] | yes |
| frame_recall_V | 0.8611 | 0.8278 | 0.0333 [0.0107, 0.0621] | yes |
| frame_recall_E | 0.6000 | 0.6000 | 0.0000 [0.0000, 0.0000] | no |
| frame_recall_H | 0.5938 | 0.5938 | 0.0000 [0.0000, 0.0000] | no |
| cell_recall_V | 0.5032 | 0.4893 | 0.0139 [0.0070, 0.0218] | yes |
| cell_recall_E | 0.3592 | 0.3592 | 0.0000 [0.0000, 0.0000] | no |
| cell_recall_H | 0.2527 | 0.2527 | 0.0000 [0.0000, 0.0000] | no |
| band1_cell_recall | 0.1026 | 0.0000 | 0.1026 [0.0412, 0.1731] | yes |
| band2_cell_recall | 0.3624 | 0.3360 | 0.0265 [0.0027, 0.0563] | yes |
| band3_cell_recall | 0.4126 | 0.4103 | 0.0023 [0.0000, 0.0059] | no |
| band4_cell_recall | 0.5136 | 0.5121 | 0.0015 [0.0000, 0.0039] | no |
| band1_cell_fpr_off | 0.0005 | 0.0000 | 0.0005 [0.0000, 0.0015] | no |
| band2_cell_fpr_off | 0.0098 | 0.0088 | 0.0010 [0.0000, 0.0031] | no |
| band3_cell_fpr_off | 0.0662 | 0.0662 | 0.0000 [0.0000, 0.0000] | no |
| band4_cell_fpr_off | 0.1358 | 0.1358 | 0.0000 [0.0000, 0.0000] | no |
| frame_fa_off | 0.3775 | 0.3750 | 0.0025 [0.0000, 0.0077] | no |
| cell_fpr_off | 0.0531 | 0.0527 | 0.0004 [0.0000, 0.0010] | no |
| cell_fpr_on_neg | 0.0965 | 0.0933 | 0.0033 [0.0016, 0.0053] | yes |
