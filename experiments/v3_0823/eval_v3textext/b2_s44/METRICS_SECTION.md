# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.45 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6344 [0.5349, 0.7326] | 0.2969 [0.2232, 0.3750] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.3472 [0.2388, 0.4606] | 0.1968 [0.1303, 0.2663] | 72 |
| **any tier (frame detection rate)** | 0.5091 [0.4335, 0.5864] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.4688 [0.4101, 0.5251] |
| cell FPR (off frames) | 0.0849 [0.0704, 0.1000] |
| cell FPR (negative cells of on frames) | 0.0879 [0.0724, 0.1043] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2424 [0.1269, 0.3727] | 0.0319 [0.0159, 0.0510] |
| 3a [5,8) m | 0.2362 [0.1715, 0.3042] | 0.0875 [0.0646, 0.1120] |
| 3b [8,12) m | 0.2894 [0.2332, 0.3493] | 0.2201 [0.1869, 0.2534] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2605 [0.2080, 0.3121] |
| cell recall | 0.2608 [0.2076, 0.3171] |
| cell precision | 0.2602 [0.2026, 0.3205] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.45

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6667 [0.5700, 0.7609] | 0.3242 [0.2476, 0.4049] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.3472 [0.2388, 0.4606] | 0.2060 [0.1388, 0.2749] | 72 |
| **any tier (frame detection rate)** | 0.5273 [0.4529, 0.6043] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.4931 [0.4349, 0.5495] |
| cell FPR (off frames) | 0.0918 [0.0767, 0.1078] |
| cell FPR (negative cells of on frames) | 0.0963 [0.0799, 0.1134] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0370 [0.0000, 0.1250] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2803 [0.1593, 0.4130] | 0.0354 [0.0186, 0.0551] |
| 3a [5,8) m | 0.2703 [0.2009, 0.3431] | 0.0924 [0.0695, 0.1173] |
| 3b [8,12) m | 0.2985 [0.2415, 0.3585] | 0.2396 [0.2053, 0.2741] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2698 [0.2169, 0.3217] |
| cell recall | 0.2817 [0.2266, 0.3392] |
| cell precision | 0.2588 [0.2027, 0.3183] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.2953 | 0.2605 | 0.2417 |
| cell_recall | 0.3467 | 0.2608 | 0.2092 |
| cell_precision | 0.2573 | 0.2602 | 0.2862 |
| frame_det_rate | 0.5758 | 0.5091 | 0.4182 |
| frame_recall_V | 0.7312 | 0.6344 | 0.5161 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.3750 | 0.3472 | 0.2917 |
| cell_recall_V | 0.4049 | 0.2969 | 0.2357 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.2431 | 0.1968 | 0.1620 |
| band1_cell_recall | 0.0370 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.4091 | 0.2424 | 0.1515 |
| band3_cell_recall | 0.3438 | 0.2362 | 0.1732 |
| band4_cell_recall | 0.3485 | 0.2894 | 0.2500 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0500 | 0.0319 | 0.0174 |
| band3_cell_fpr_off | 0.1187 | 0.0875 | 0.0632 |
| band4_cell_fpr_off | 0.2861 | 0.2201 | 0.1653 |
| frame_fa_off | 0.5417 | 0.4688 | 0.3924 |
| cell_fpr_off | 0.1137 | 0.0849 | 0.0615 |
| cell_fpr_on_neg | 0.1197 | 0.0879 | 0.0596 |
