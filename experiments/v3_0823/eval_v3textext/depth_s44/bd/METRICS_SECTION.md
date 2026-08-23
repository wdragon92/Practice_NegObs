# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.6 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4839 [0.3837, 0.5865] | 0.6406 [0.5638, 0.7070] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.6667 [0.5571, 0.7750] | 0.7222 [0.6331, 0.8009] | 72 |
| **any tier (frame detection rate)** | 0.5636 [0.4897, 0.6402] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1771 [0.1338, 0.2218] |
| cell FPR (off frames) | 0.1005 [0.0732, 0.1293] |
| cell FPR (negative cells of on frames) | 0.0776 [0.0571, 0.0999] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.2222 [0.0000, 0.4000] | 0.0146 [0.0054, 0.0259] |
| 2 [2,5) m | 0.6818 [0.5053, 0.8475] | 0.1104 [0.0757, 0.1463] |
| 3a [5,8) m | 0.7165 [0.6378, 0.7888] | 0.1292 [0.0935, 0.1663] |
| 3b [8,12) m | 0.6591 [0.5876, 0.7260] | 0.1479 [0.1086, 0.1891] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5475 [0.4854, 0.6037] |
| cell recall | 0.6700 [0.6139, 0.7217] |
| cell precision | 0.4629 [0.3920, 0.5339] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.6

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4839 [0.3837, 0.5865] | 0.6055 [0.5265, 0.6759] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.6250 [0.5135, 0.7368] | 0.7014 [0.6066, 0.7859] | 72 |
| **any tier (frame detection rate)** | 0.5455 [0.4702, 0.6220] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1667 [0.1241, 0.2111] |
| cell FPR (off frames) | 0.0901 [0.0643, 0.1170] |
| cell FPR (negative cells of on frames) | 0.0645 [0.0460, 0.0847] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1111 [0.0000, 0.2000] | 0.0063 [0.0026, 0.0105] |
| 2 [2,5) m | 0.6591 [0.4718, 0.8361] | 0.1000 [0.0669, 0.1343] |
| 3a [5,8) m | 0.6693 [0.5848, 0.7481] | 0.1187 [0.0841, 0.1555] |
| 3b [8,12) m | 0.6409 [0.5688, 0.7086] | 0.1354 [0.0976, 0.1746] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5523 [0.4905, 0.6082] |
| cell recall | 0.6400 [0.5811, 0.6946] |
| cell precision | 0.4858 [0.4120, 0.5598] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5210 | 0.5475 | 0.5494 |
| cell_recall | 0.7275 | 0.6700 | 0.6050 |
| cell_precision | 0.4059 | 0.4629 | 0.5031 |
| frame_det_rate | 0.6182 | 0.5636 | 0.5455 |
| frame_recall_V | 0.4839 | 0.4839 | 0.4839 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.7917 | 0.6667 | 0.6250 |
| cell_recall_V | 0.6875 | 0.6406 | 0.5703 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.7986 | 0.7222 | 0.6667 |
| band1_cell_recall | 0.4444 | 0.2222 | 0.1111 |
| band2_cell_recall | 0.7727 | 0.6818 | 0.6364 |
| band3_cell_recall | 0.7717 | 0.7165 | 0.6299 |
| band4_cell_recall | 0.7045 | 0.6591 | 0.6045 |
| band1_cell_fpr_off | 0.0292 | 0.0146 | 0.0021 |
| band2_cell_fpr_off | 0.1375 | 0.1104 | 0.0938 |
| band3_cell_fpr_off | 0.1708 | 0.1292 | 0.1062 |
| band4_cell_fpr_off | 0.1812 | 0.1479 | 0.1271 |
| frame_fa_off | 0.2188 | 0.1771 | 0.1667 |
| cell_fpr_off | 0.1297 | 0.1005 | 0.0823 |
| cell_fpr_on_neg | 0.1164 | 0.0776 | 0.0533 |
