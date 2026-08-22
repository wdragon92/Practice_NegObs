# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.45 (fitted on **val**, val cell-F1 0.5458) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 2691 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6500 [0.5799, 0.7208] | 0.2872 [0.2433, 0.3344] | 180 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.2083 [0.1290, 0.2929] | 0.0934 [0.0569, 0.1323] | 96 |
| **any tier (frame detection rate)** | 0.4190 [0.3651, 0.4732] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1078 [0.0791, 0.1393] |
| cell FPR (off frames) | 0.0104 [0.0067, 0.0147] |
| cell FPR (negative cells of on frames) | 0.0453 [0.0346, 0.0567] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.1958 [0.1250, 0.2711] | 0.0020 [0.0000, 0.0061] |
| 3a [5,8) m | 0.1563 [0.1204, 0.1958] | 0.0049 [0.0010, 0.0102] |
| 3b [8,12) m | 0.2790 [0.2376, 0.3219] | 0.0348 [0.0240, 0.0467] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3219 [0.2811, 0.3623] |
| cell recall | 0.2155 [0.1829, 0.2501] |
| cell precision | 0.6353 [0.5755, 0.6924] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.45

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6556 [0.5848, 0.7257] | 0.3012 [0.2561, 0.3495] | 180 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.2083 [0.1290, 0.2929] | 0.1019 [0.0623, 0.1439] | 96 |
| **any tier (frame detection rate)** | 0.4220 [0.3676, 0.4765] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1176 [0.0873, 0.1497] |
| cell FPR (off frames) | 0.0113 [0.0076, 0.0156] |
| cell FPR (negative cells of on frames) | 0.0506 [0.0393, 0.0626] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2037 [0.1308, 0.2809] | 0.0025 [0.0000, 0.0070] |
| 3a [5,8) m | 0.1655 [0.1289, 0.2056] | 0.0049 [0.0010, 0.0102] |
| 3b [8,12) m | 0.2934 [0.2505, 0.3370] | 0.0377 [0.0267, 0.0500] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3324 [0.2917, 0.3726] |
| cell recall | 0.2267 [0.1932, 0.2618] |
| cell precision | 0.6231 [0.5652, 0.6781] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3892 | 0.3219 | 0.2565 |
| cell_recall | 0.2847 | 0.2155 | 0.1583 |
| cell_precision | 0.6153 | 0.6353 | 0.6762 |
| frame_det_rate | 0.4495 | 0.4190 | 0.3700 |
| frame_recall_V | 0.7000 | 0.6500 | 0.5944 |
| frame_recall_E | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_H | 0.2188 | 0.2083 | 0.1458 |
| cell_recall_V | 0.3800 | 0.2872 | 0.2170 |
| cell_recall_E | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_H | 0.1210 | 0.0934 | 0.0446 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.2593 | 0.1958 | 0.1323 |
| band3_cell_recall | 0.2172 | 0.1563 | 0.1241 |
| band4_cell_recall | 0.3612 | 0.2790 | 0.2021 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0025 | 0.0020 | 0.0015 |
| band3_cell_fpr_off | 0.0078 | 0.0049 | 0.0025 |
| band4_cell_fpr_off | 0.0471 | 0.0348 | 0.0235 |
| frame_fa_off | 0.1446 | 0.1078 | 0.0711 |
| cell_fpr_off | 0.0143 | 0.0104 | 0.0069 |
| cell_fpr_on_neg | 0.0662 | 0.0453 | 0.0271 |
