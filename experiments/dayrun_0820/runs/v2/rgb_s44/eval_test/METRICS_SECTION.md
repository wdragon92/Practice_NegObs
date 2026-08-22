# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.31 (fitted on **val**, val cell-F1 0.4852) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 2691 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6167 [0.5443, 0.6871] | 0.2669 [0.2189, 0.3189] | 180 |
| E | 0.1556 [0.0571, 0.2683] | 0.0402 [0.0125, 0.0762] | 45 |
| H | 0.5938 [0.4947, 0.6907] | 0.2505 [0.2031, 0.3017] | 96 |
| **any tier (frame detection rate)** | 0.5505 [0.4957, 0.6053] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2230 [0.1827, 0.2628] |
| cell FPR (off frames) | 0.0277 [0.0218, 0.0339] |
| cell FPR (negative cells of on frames) | 0.0534 [0.0441, 0.0631] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.1429 [0.0788, 0.2154] | 0.0142 [0.0058, 0.0245] |
| 3a [5,8) m | 0.2034 [0.1604, 0.2500] | 0.0240 [0.0156, 0.0331] |
| 3b [8,12) m | 0.3047 [0.2632, 0.3467] | 0.0725 [0.0569, 0.0887] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3304 [0.2877, 0.3731] |
| cell recall | 0.2360 [0.2002, 0.2738] |
| cell precision | 0.5507 [0.4910, 0.6060] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.31

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6889 [0.6199, 0.7564] | 0.3489 [0.2942, 0.4072] | 180 |
| E | 0.3111 [0.1800, 0.4524] | 0.1034 [0.0540, 0.1624] | 45 |
| H | 0.7604 [0.6735, 0.8431] | 0.3885 [0.3270, 0.4569] | 96 |
| **any tier (frame detection rate)** | 0.6636 [0.6113, 0.7164] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3235 [0.2786, 0.3694] |
| cell FPR (off frames) | 0.0610 [0.0500, 0.0725] |
| cell FPR (negative cells of on frames) | 0.0914 [0.0780, 0.1058] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2222 [0.1467, 0.3052] | 0.0309 [0.0173, 0.0462] |
| 3a [5,8) m | 0.3034 [0.2519, 0.3571] | 0.0770 [0.0585, 0.0963] |
| 3b [8,12) m | 0.3982 [0.3529, 0.4439] | 0.1363 [0.1139, 0.1592] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3838 [0.3433, 0.4234] |
| cell recall | 0.3255 [0.2848, 0.3687] |
| cell precision | 0.4674 [0.4158, 0.5168] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3869 | 0.3304 | 0.2517 |
| cell_recall | 0.3326 | 0.2360 | 0.1561 |
| cell_precision | 0.4625 | 0.5507 | 0.6502 |
| frame_det_rate | 0.6697 | 0.5505 | 0.3792 |
| frame_recall_V | 0.7000 | 0.6167 | 0.4889 |
| frame_recall_E | 0.3111 | 0.1556 | 0.0444 |
| frame_recall_H | 0.7604 | 0.5938 | 0.3229 |
| cell_recall_V | 0.3548 | 0.2669 | 0.1908 |
| cell_recall_E | 0.1121 | 0.0402 | 0.0057 |
| cell_recall_H | 0.3992 | 0.2505 | 0.1253 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.2302 | 0.1429 | 0.0979 |
| band3_cell_recall | 0.3138 | 0.2034 | 0.1287 |
| band4_cell_recall | 0.4035 | 0.3047 | 0.2044 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0314 | 0.0142 | 0.0015 |
| band3_cell_fpr_off | 0.0809 | 0.0240 | 0.0093 |
| band4_cell_fpr_off | 0.1412 | 0.0725 | 0.0294 |
| frame_fa_off | 0.3284 | 0.2230 | 0.1127 |
| cell_fpr_off | 0.0634 | 0.0277 | 0.0100 |
| cell_fpr_on_neg | 0.0956 | 0.0534 | 0.0263 |
