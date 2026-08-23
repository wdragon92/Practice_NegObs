# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.31 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.2473 [0.1628, 0.3370] | 0.1198 [0.0714, 0.1743] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.0972 [0.0323, 0.1724] | 0.0741 [0.0239, 0.1323] | 72 |
| **any tier (frame detection rate)** | 0.1818 [0.1242, 0.2420] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0139 [0.0033, 0.0289] |
| cell FPR (off frames) | 0.0024 [0.0002, 0.0058] |
| cell FPR (negative cells of on frames) | 0.0088 [0.0043, 0.0141] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1481 [0.0000, 0.3265] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.1136 [0.0163, 0.2308] | 0.0028 [0.0000, 0.0088] |
| 3a [5,8) m | 0.1260 [0.0751, 0.1818] | 0.0014 [0.0000, 0.0036] |
| 3b [8,12) m | 0.0864 [0.0466, 0.1300] | 0.0056 [0.0007, 0.0141] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1800 [0.1206, 0.2395] |
| cell recall | 0.1033 [0.0665, 0.1433] |
| cell precision | 0.6966 [0.5825, 0.8010] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.31

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.2903 [0.1980, 0.3838] | 0.1836 [0.1217, 0.2497] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.1944 [0.1081, 0.2923] | 0.1296 [0.0583, 0.2103] | 72 |
| **any tier (frame detection rate)** | 0.2485 [0.1845, 0.3165] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0833 [0.0536, 0.1169] |
| cell FPR (off frames) | 0.0123 [0.0065, 0.0196] |
| cell FPR (negative cells of on frames) | 0.0224 [0.0141, 0.0315] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.2963 [0.0000, 0.6531] | 0.0028 [0.0000, 0.0080] |
| 2 [2,5) m | 0.1742 [0.0555, 0.3109] | 0.0097 [0.0027, 0.0193] |
| 3a [5,8) m | 0.2178 [0.1432, 0.2957] | 0.0139 [0.0062, 0.0237] |
| 3b [8,12) m | 0.1258 [0.0771, 0.1769] | 0.0229 [0.0114, 0.0375] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2510 [0.1845, 0.3130] |
| cell recall | 0.1642 [0.1158, 0.2146] |
| cell precision | 0.5324 [0.4267, 0.6250] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.2566 | 0.1800 | 0.1159 |
| cell_recall | 0.1700 | 0.1033 | 0.0625 |
| cell_precision | 0.5231 | 0.6966 | 0.7979 |
| frame_det_rate | 0.2485 | 0.1818 | 0.1273 |
| frame_recall_V | 0.2903 | 0.2473 | 0.1613 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.1944 | 0.0972 | 0.0833 |
| cell_recall_V | 0.1888 | 0.1198 | 0.0716 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.1366 | 0.0741 | 0.0463 |
| band1_cell_recall | 0.2963 | 0.1481 | 0.0000 |
| band2_cell_recall | 0.1742 | 0.1136 | 0.0606 |
| band3_cell_recall | 0.2231 | 0.1260 | 0.0787 |
| band4_cell_recall | 0.1333 | 0.0864 | 0.0561 |
| band1_cell_fpr_off | 0.0028 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0118 | 0.0028 | 0.0000 |
| band3_cell_fpr_off | 0.0153 | 0.0014 | 0.0000 |
| band4_cell_fpr_off | 0.0243 | 0.0056 | 0.0014 |
| frame_fa_off | 0.0868 | 0.0139 | 0.0035 |
| cell_fpr_off | 0.0135 | 0.0024 | 0.0003 |
| cell_fpr_on_neg | 0.0237 | 0.0088 | 0.0037 |
