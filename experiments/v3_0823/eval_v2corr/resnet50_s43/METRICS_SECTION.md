# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/newmodels/runs/resnet50_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.36 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 369 | 219 | 45 | 96 | 7 | 2856 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.7717 [0.7149, 0.8274] | 0.3952 [0.3486, 0.4430] | 219 |
| E | 0.1333 [0.0435, 0.2439] | 0.0287 [0.0078, 0.0564] | 45 |
| H | 0.2396 [0.1569, 0.3267] | 0.0743 [0.0444, 0.1084] | 96 |
| **any tier (frame detection rate)** | 0.5501 [0.4987, 0.6011] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3431 [0.2980, 0.3893] |
| cell FPR (off frames) | 0.0391 [0.0331, 0.0454] |
| cell FPR (negative cells of on frames) | 0.0728 [0.0618, 0.0842] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2857 [0.2019, 0.3733] | 0.0034 [0.0000, 0.0082] |
| 3a [5,8) m | 0.2132 [0.1718, 0.2567] | 0.0157 [0.0084, 0.0238] |
| 3b [8,12) m | 0.3776 [0.3345, 0.4213] | 0.1373 [0.1162, 0.1593] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3865 [0.3452, 0.4262] |
| cell recall | 0.2987 [0.2611, 0.3374] |
| cell precision | 0.5475 [0.4949, 0.5966] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.36

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8265 [0.7739, 0.8756] | 0.4782 [0.4268, 0.5308] | 219 |
| E | 0.4222 [0.2750, 0.5714] | 0.1121 [0.0661, 0.1626] | 45 |
| H | 0.3542 [0.2588, 0.4522] | 0.1189 [0.0800, 0.1620] | 96 |
| **any tier (frame detection rate)** | 0.6585 [0.6096, 0.7060] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.4020 [0.3550, 0.4491] |
| cell FPR (off frames) | 0.0607 [0.0519, 0.0697] |
| cell FPR (negative cells of on frames) | 0.1161 [0.1006, 0.1321] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.3704 [0.2727, 0.4695] | 0.0167 [0.0078, 0.0267] |
| 3a [5,8) m | 0.2783 [0.2309, 0.3290] | 0.0319 [0.0216, 0.0430] |
| 3b [8,12) m | 0.4680 [0.4227, 0.5139] | 0.1941 [0.1681, 0.2212] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4267 [0.3875, 0.4652] |
| cell recall | 0.3768 [0.3356, 0.4185] |
| cell precision | 0.4920 [0.4436, 0.5374] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4430 | 0.3865 | 0.3050 |
| cell_recall | 0.4198 | 0.2987 | 0.1989 |
| cell_precision | 0.4689 | 0.5475 | 0.6536 |
| frame_det_rate | 0.7154 | 0.5501 | 0.4363 |
| frame_recall_V | 0.8447 | 0.7717 | 0.6804 |
| frame_recall_E | 0.5778 | 0.1333 | 0.0000 |
| frame_recall_H | 0.4583 | 0.2396 | 0.0938 |
| cell_recall_V | 0.5208 | 0.3952 | 0.2720 |
| cell_recall_E | 0.1667 | 0.0287 | 0.0000 |
| cell_recall_H | 0.1550 | 0.0743 | 0.0276 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.4259 | 0.2857 | 0.1190 |
| band3_cell_recall | 0.3199 | 0.2132 | 0.1291 |
| band4_cell_recall | 0.5122 | 0.3776 | 0.2776 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0304 | 0.0034 | 0.0000 |
| band3_cell_fpr_off | 0.0387 | 0.0157 | 0.0078 |
| band4_cell_fpr_off | 0.2260 | 0.1373 | 0.0593 |
| frame_fa_off | 0.4412 | 0.3431 | 0.1789 |
| cell_fpr_off | 0.0738 | 0.0391 | 0.0168 |
| cell_fpr_on_neg | 0.1425 | 0.0728 | 0.0309 |
