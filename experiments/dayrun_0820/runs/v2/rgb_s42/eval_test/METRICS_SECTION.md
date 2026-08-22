# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.63 (fitted on **val**, val cell-F1 0.4733) · bootstrap 10000x seed 42

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

## 1b. Stratified recall by evidence tier @ tau_star = 0.63

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.7667 [0.7021, 0.8286] | 0.4089 [0.3549, 0.4648] | 180 |
| E | 0.5333 [0.3864, 0.6809] | 0.1983 [0.1310, 0.2694] | 45 |
| H | 0.4792 [0.3804, 0.5794] | 0.1783 [0.1343, 0.2257] | 96 |
| **any tier (frame detection rate)** | 0.6514 [0.6000, 0.7023] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2941 [0.2506, 0.3382] |
| cell FPR (off frames) | 0.0353 [0.0288, 0.0420] |
| cell FPR (negative cells of on frames) | 0.0688 [0.0563, 0.0820] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2513 [0.1692, 0.3383] | 0.0034 [0.0000, 0.0089] |
| 3a [5,8) m | 0.3253 [0.2741, 0.3766] | 0.0461 [0.0324, 0.0604] |
| 3b [8,12) m | 0.4095 [0.3634, 0.4552] | 0.0917 [0.0751, 0.1090] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4308 [0.3883, 0.4720] |
| cell recall | 0.3423 [0.3016, 0.3834] |
| cell precision | 0.5811 [0.5263, 0.6328] |

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
