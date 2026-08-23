# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `experiments/weekend_0823/newmodels/runs/resnet50_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.36 (fitted on **val**, val cell-F1 0.5438) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 2691 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.7833 [0.7222, 0.8432] | 0.3912 [0.3419, 0.4419] | 180 |
| E | 0.1333 [0.0435, 0.2439] | 0.0287 [0.0078, 0.0564] | 45 |
| H | 0.2396 [0.1569, 0.3267] | 0.0743 [0.0444, 0.1084] | 96 |
| **any tier (frame detection rate)** | 0.5260 [0.4716, 0.5802] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3431 [0.2980, 0.3893] |
| cell FPR (off frames) | 0.0391 [0.0331, 0.0454] |
| cell FPR (negative cells of on frames) | 0.0845 [0.0720, 0.0976] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2857 [0.2019, 0.3733] | 0.0034 [0.0000, 0.0082] |
| 3a [5,8) m | 0.2138 [0.1714, 0.2576] | 0.0157 [0.0084, 0.0238] |
| 3b [8,12) m | 0.3643 [0.3185, 0.4107] | 0.1373 [0.1162, 0.1593] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3657 [0.3226, 0.4078] |
| cell recall | 0.2887 [0.2495, 0.3288] |
| cell precision | 0.4987 [0.4408, 0.5527] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.36

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8278 [0.7701, 0.8816] | 0.4700 [0.4161, 0.5257] | 180 |
| E | 0.4222 [0.2750, 0.5714] | 0.1121 [0.0661, 0.1626] | 45 |
| H | 0.3542 [0.2588, 0.4522] | 0.1189 [0.0800, 0.1620] | 96 |
| **any tier (frame detection rate)** | 0.6361 [0.5836, 0.6871] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.4020 [0.3550, 0.4491] |
| cell FPR (off frames) | 0.0607 [0.0519, 0.0697] |
| cell FPR (negative cells of on frames) | 0.1306 [0.1136, 0.1479] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.3704 [0.2727, 0.4695] | 0.0167 [0.0078, 0.0267] |
| 3a [5,8) m | 0.2782 [0.2300, 0.3293] | 0.0319 [0.0216, 0.0430] |
| 3b [8,12) m | 0.4495 [0.4017, 0.4978] | 0.1941 [0.1681, 0.2212] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4010 [0.3587, 0.4423] |
| cell recall | 0.3634 [0.3207, 0.4070] |
| cell precision | 0.4472 [0.3951, 0.4963] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4158 | 0.3657 | 0.2904 |
| cell_recall | 0.4054 | 0.2887 | 0.1921 |
| cell_precision | 0.4267 | 0.4987 | 0.5949 |
| frame_det_rate | 0.6942 | 0.5260 | 0.4159 |
| frame_recall_V | 0.8389 | 0.7833 | 0.7056 |
| frame_recall_E | 0.5778 | 0.1333 | 0.0000 |
| frame_recall_H | 0.4583 | 0.2396 | 0.0938 |
| cell_recall_V | 0.5113 | 0.3912 | 0.2701 |
| cell_recall_E | 0.1667 | 0.0287 | 0.0000 |
| cell_recall_H | 0.1550 | 0.0743 | 0.0276 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.4259 | 0.2857 | 0.1190 |
| band3_cell_recall | 0.3195 | 0.2138 | 0.1322 |
| band4_cell_recall | 0.4917 | 0.3643 | 0.2692 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0304 | 0.0034 | 0.0000 |
| band3_cell_fpr_off | 0.0387 | 0.0157 | 0.0078 |
| band4_cell_fpr_off | 0.2260 | 0.1373 | 0.0593 |
| frame_fa_off | 0.4412 | 0.3431 | 0.1789 |
| cell_fpr_off | 0.0738 | 0.0391 | 0.0168 |
| cell_fpr_on_neg | 0.1580 | 0.0845 | 0.0393 |
