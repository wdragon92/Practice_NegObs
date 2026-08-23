# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.31 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 369 | 219 | 45 | 96 | 7 | 2856 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.5479 [0.4817, 0.6136] | 0.2507 [0.2059, 0.2987] | 219 |
| E | 0.1556 [0.0571, 0.2683] | 0.0402 [0.0125, 0.0762] | 45 |
| H | 0.5938 [0.4947, 0.6907] | 0.2505 [0.2031, 0.3017] | 96 |
| **any tier (frame detection rate)** | 0.5203 [0.4683, 0.5722] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2230 [0.1827, 0.2628] |
| cell FPR (off frames) | 0.0277 [0.0218, 0.0339] |
| cell FPR (negative cells of on frames) | 0.0526 [0.0431, 0.0626] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.1429 [0.0788, 0.2154] | 0.0142 [0.0058, 0.0245] |
| 3a [5,8) m | 0.1998 [0.1577, 0.2455] | 0.0240 [0.0156, 0.0331] |
| 3b [8,12) m | 0.2830 [0.2446, 0.3230] | 0.0725 [0.0569, 0.0887] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3233 [0.2822, 0.3646] |
| cell recall | 0.2269 [0.1935, 0.2629] |
| cell precision | 0.5620 [0.5035, 0.6160] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.31

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6256 [0.5610, 0.6893] | 0.3284 [0.2771, 0.3818] | 219 |
| E | 0.3111 [0.1800, 0.4524] | 0.1034 [0.0540, 0.1624] | 45 |
| H | 0.7604 [0.6735, 0.8431] | 0.3885 [0.3270, 0.4569] | 96 |
| **any tier (frame detection rate)** | 0.6314 [0.5819, 0.6826] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3235 [0.2786, 0.3694] |
| cell FPR (off frames) | 0.0610 [0.0500, 0.0725] |
| cell FPR (negative cells of on frames) | 0.0911 [0.0774, 0.1056] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2222 [0.1467, 0.3052] | 0.0309 [0.0173, 0.0462] |
| 3a [5,8) m | 0.2985 [0.2481, 0.3511] | 0.0770 [0.0585, 0.0963] |
| 3b [8,12) m | 0.3694 [0.3282, 0.4133] | 0.1363 [0.1139, 0.1592] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3776 [0.3383, 0.4163] |
| cell recall | 0.3127 [0.2742, 0.3540] |
| cell precision | 0.4765 [0.4256, 0.5255] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3815 | 0.3233 | 0.2439 |
| cell_recall | 0.3200 | 0.2269 | 0.1495 |
| cell_precision | 0.4724 | 0.5620 | 0.6610 |
| frame_det_rate | 0.6396 | 0.5203 | 0.3550 |
| frame_recall_V | 0.6393 | 0.5479 | 0.4247 |
| frame_recall_E | 0.3111 | 0.1556 | 0.0444 |
| frame_recall_H | 0.7604 | 0.5938 | 0.3229 |
| cell_recall_V | 0.3348 | 0.2507 | 0.1785 |
| cell_recall_E | 0.1121 | 0.0402 | 0.0057 |
| cell_recall_H | 0.3992 | 0.2505 | 0.1253 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.2302 | 0.1429 | 0.0979 |
| band3_cell_recall | 0.3086 | 0.1998 | 0.1257 |
| band4_cell_recall | 0.3755 | 0.2830 | 0.1891 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0314 | 0.0142 | 0.0015 |
| band3_cell_fpr_off | 0.0809 | 0.0240 | 0.0093 |
| band4_cell_fpr_off | 0.1412 | 0.0725 | 0.0294 |
| frame_fa_off | 0.3284 | 0.2230 | 0.1127 |
| cell_fpr_off | 0.0634 | 0.0277 | 0.0100 |
| cell_fpr_on_neg | 0.0950 | 0.0526 | 0.0258 |
