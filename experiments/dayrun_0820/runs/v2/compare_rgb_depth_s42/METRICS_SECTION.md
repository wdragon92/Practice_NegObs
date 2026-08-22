# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s42/eval_test/per_frame.csv`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 2691 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8278 [0.7703, 0.8820] | 0.4893 [0.4299, 0.5500] | 180 |
| E | 0.6000 [0.4528, 0.7436] | 0.3592 [0.2626, 0.4556] | 45 |
| H | 0.5938 [0.4946, 0.6923] | 0.2527 [0.1989, 0.3107] | 96 |
| **any tier (frame detection rate)** | 0.7309 [0.6820, 0.7788] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3750 [0.3283, 0.4218] |
| cell FPR (off frames) | 0.0527 [0.0443, 0.0615] |
| cell FPR (negative cells of on frames) | 0.0933 [0.0782, 0.1089] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.3360 [0.2446, 0.4326] | 0.0088 [0.0030, 0.0162] |
| 3a [5,8) m | 0.4103 [0.3531, 0.4679] | 0.0662 [0.0488, 0.0842] |
| 3b [8,12) m | 0.5121 [0.4640, 0.5584] | 0.1358 [0.1151, 0.1565] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4852 [0.4435, 0.5247] |
| cell recall | 0.4322 [0.3876, 0.4766] |
| cell precision | 0.5530 [0.5015, 0.6014] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8278 [0.7703, 0.8820] | 0.4893 [0.4299, 0.5500] | 180 |
| E | 0.6000 [0.4528, 0.7436] | 0.3592 [0.2626, 0.4556] | 45 |
| H | 0.5938 [0.4946, 0.6923] | 0.2527 [0.1989, 0.3107] | 96 |
| **any tier (frame detection rate)** | 0.7309 [0.6820, 0.7788] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3750 [0.3283, 0.4218] |
| cell FPR (off frames) | 0.0527 [0.0443, 0.0615] |
| cell FPR (negative cells of on frames) | 0.0933 [0.0782, 0.1089] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.3360 [0.2446, 0.4326] | 0.0088 [0.0030, 0.0162] |
| 3a [5,8) m | 0.4103 [0.3531, 0.4679] | 0.0662 [0.0488, 0.0842] |
| 3b [8,12) m | 0.5121 [0.4640, 0.5584] | 0.1358 [0.1151, 0.1565] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4852 [0.4435, 0.5247] |
| cell recall | 0.4322 [0.3876, 0.4766] |
| cell precision | 0.5530 [0.5015, 0.6014] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5259 | 0.4852 | 0.3907 |
| cell_recall | 0.5686 | 0.4322 | 0.2902 |
| cell_precision | 0.4891 | 0.5530 | 0.5976 |
| frame_det_rate | 0.8349 | 0.7309 | 0.5688 |
| frame_recall_V | 0.8833 | 0.8278 | 0.7222 |
| frame_recall_E | 0.7111 | 0.6000 | 0.4000 |
| frame_recall_H | 0.7917 | 0.5938 | 0.3750 |
| cell_recall_V | 0.6024 | 0.4893 | 0.3612 |
| cell_recall_E | 0.5833 | 0.3592 | 0.1178 |
| cell_recall_H | 0.4183 | 0.2527 | 0.1359 |
| band1_cell_recall | 0.0171 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.4709 | 0.3360 | 0.2143 |
| band3_cell_recall | 0.5552 | 0.4103 | 0.2736 |
| band4_cell_recall | 0.6538 | 0.5121 | 0.3484 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0319 | 0.0088 | 0.0029 |
| band3_cell_fpr_off | 0.1137 | 0.0662 | 0.0328 |
| band4_cell_fpr_off | 0.2284 | 0.1358 | 0.0681 |
| frame_fa_off | 0.4779 | 0.3750 | 0.2255 |
| cell_fpr_off | 0.0935 | 0.0527 | 0.0260 |
| cell_fpr_on_neg | 0.1527 | 0.0933 | 0.0574 |

## 3. Paired comparison (A = this arm, B = `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s42/eval_test/per_frame.csv`)

816 common frames · paired percentile bootstrap 10000x seed 42 · threshold 0.5

| metric | A | B | A−B [95% CI] | CI excludes 0 |
|---|---|---|---|---|
| cell_f1 | 0.4852 | 0.7046 | -0.2194 [-0.2666, -0.1722] | yes |
| cell_recall | 0.4322 | 0.6834 | -0.2512 [-0.3049, -0.1955] | yes |
| cell_precision | 0.5530 | 0.7272 | -0.1741 [-0.2311, -0.1186] | yes |
| frame_det_rate | 0.7309 | 0.7339 | -0.0031 [-0.0612, 0.0550] | no |
| frame_recall_V | 0.8278 | 0.9667 | -0.1389 [-0.2035, -0.0754] | yes |
| frame_recall_E | 0.6000 | 0.6000 | 0.0000 [-0.0889, 0.0870] | no |
| frame_recall_H | 0.5938 | 0.4062 | 0.1875 [0.0532, 0.3229] | yes |
| cell_recall_V | 0.4893 | 0.7379 | -0.2487 [-0.3192, -0.1776] | yes |
| cell_recall_E | 0.3592 | 0.5431 | -0.1839 [-0.2720, -0.0884] | yes |
| cell_recall_H | 0.2527 | 0.5796 | -0.3270 [-0.4296, -0.2082] | yes |
| band1_cell_recall | 0.0000 | 0.1026 | -0.1026 [-0.2222, 0.0000] | no |
| band2_cell_recall | 0.3360 | 0.5794 | -0.2434 [-0.3689, -0.1189] | yes |
| band3_cell_recall | 0.4103 | 0.7379 | -0.3276 [-0.4024, -0.2494] | yes |
| band4_cell_recall | 0.5121 | 0.7285 | -0.2164 [-0.2689, -0.1645] | yes |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 [0.0000, 0.0000] | no |
| band2_cell_fpr_off | 0.0088 | 0.0000 | 0.0088 [0.0030, 0.0162] | yes |
| band3_cell_fpr_off | 0.0662 | 0.0059 | 0.0603 [0.0427, 0.0790] | yes |
| band4_cell_fpr_off | 0.1358 | 0.0118 | 0.1240 [0.1023, 0.1456] | yes |
| frame_fa_off | 0.3750 | 0.0515 | 0.3235 [0.2725, 0.3738] | yes |
| cell_fpr_off | 0.0527 | 0.0044 | 0.0483 [0.0395, 0.0573] | yes |
| cell_fpr_on_neg | 0.0933 | 0.1196 | -0.0263 [-0.0562, 0.0030] | no |
