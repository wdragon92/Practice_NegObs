# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/runs/v3a/rgb_s42_aux/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.3763 [0.2809, 0.4767] | 0.4193 [0.3185, 0.5133] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.3750 [0.2658, 0.4881] | 0.2431 [0.1683, 0.3183] | 72 |
| **any tier (frame detection rate)** | 0.3758 [0.3034, 0.4512] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1597 [0.1178, 0.2027] |
| cell FPR (off frames) | 0.0302 [0.0205, 0.0410] |
| cell FPR (negative cells of on frames) | 0.0270 [0.0179, 0.0373] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.4924 [0.3167, 0.6667] | 0.0118 [0.0029, 0.0227] |
| 3a [5,8) m | 0.2940 [0.2087, 0.3823] | 0.0257 [0.0136, 0.0395] |
| 3b [8,12) m | 0.3788 [0.3053, 0.4526] | 0.0833 [0.0567, 0.1121] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4439 [0.3674, 0.5137] |
| cell recall | 0.3558 [0.2851, 0.4264] |
| cell precision | 0.5898 [0.4975, 0.6746] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.3763 [0.2809, 0.4767] | 0.4193 [0.3185, 0.5133] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.3750 [0.2658, 0.4881] | 0.2431 [0.1683, 0.3183] | 72 |
| **any tier (frame detection rate)** | 0.3758 [0.3034, 0.4512] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1597 [0.1178, 0.2027] |
| cell FPR (off frames) | 0.0302 [0.0205, 0.0410] |
| cell FPR (negative cells of on frames) | 0.0270 [0.0179, 0.0373] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.4924 [0.3167, 0.6667] | 0.0118 [0.0029, 0.0227] |
| 3a [5,8) m | 0.2940 [0.2087, 0.3823] | 0.0257 [0.0136, 0.0395] |
| 3b [8,12) m | 0.3788 [0.3053, 0.4526] | 0.0833 [0.0567, 0.1121] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4439 [0.3674, 0.5137] |
| cell recall | 0.3558 [0.2851, 0.4264] |
| cell precision | 0.5898 [0.4975, 0.6746] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4608 | 0.4439 | 0.4017 |
| cell_recall | 0.4358 | 0.3558 | 0.2817 |
| cell_precision | 0.4888 | 0.5898 | 0.6998 |
| frame_det_rate | 0.4667 | 0.3758 | 0.3152 |
| frame_recall_V | 0.4731 | 0.3763 | 0.3548 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.4583 | 0.3750 | 0.2639 |
| cell_recall_V | 0.4831 | 0.4193 | 0.3555 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.3519 | 0.2431 | 0.1505 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.5833 | 0.4924 | 0.3864 |
| band3_cell_recall | 0.3937 | 0.2940 | 0.2310 |
| band4_cell_recall | 0.4485 | 0.3788 | 0.3015 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0257 | 0.0118 | 0.0042 |
| band3_cell_fpr_off | 0.0535 | 0.0257 | 0.0139 |
| band4_cell_fpr_off | 0.1271 | 0.0833 | 0.0451 |
| frame_fa_off | 0.2535 | 0.1597 | 0.0938 |
| cell_fpr_off | 0.0516 | 0.0302 | 0.0158 |
| cell_fpr_on_neg | 0.0548 | 0.0270 | 0.0118 |
