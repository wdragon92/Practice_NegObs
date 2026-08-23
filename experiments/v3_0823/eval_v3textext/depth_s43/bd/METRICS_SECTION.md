# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.21 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4839 [0.3837, 0.5865] | 0.6289 [0.5470, 0.7002] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.7500 [0.6461, 0.8472] | 0.8056 [0.7162, 0.8793] | 72 |
| **any tier (frame detection rate)** | 0.6000 [0.5269, 0.6739] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1875 [0.1433, 0.2340] |
| cell FPR (off frames) | 0.1182 [0.0876, 0.1502] |
| cell FPR (negative cells of on frames) | 0.0980 [0.0729, 0.1258] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0271 [0.0108, 0.0464] |
| 2 [2,5) m | 0.5909 [0.4082, 0.7661] | 0.1146 [0.0800, 0.1502] |
| 3a [5,8) m | 0.8583 [0.8048, 0.9010] | 0.1646 [0.1228, 0.2077] |
| 3b [8,12) m | 0.6455 [0.5731, 0.7130] | 0.1667 [0.1247, 0.2106] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5261 [0.4637, 0.5835] |
| cell recall | 0.6925 [0.6333, 0.7476] |
| cell precision | 0.4242 [0.3585, 0.4922] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.21

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.5161 [0.4156, 0.6186] | 0.6680 [0.5911, 0.7324] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.8333 [0.7429, 0.9155] | 0.8542 [0.7866, 0.9091] | 72 |
| **any tier (frame detection rate)** | 0.6545 [0.5824, 0.7256] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2188 [0.1713, 0.2680] |
| cell FPR (off frames) | 0.1375 [0.1051, 0.1712] |
| cell FPR (negative cells of on frames) | 0.1217 [0.0941, 0.1510] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0292 [0.0122, 0.0496] |
| 2 [2,5) m | 0.6818 [0.5325, 0.8235] | 0.1333 [0.0958, 0.1723] |
| 3a [5,8) m | 0.8661 [0.8134, 0.9084] | 0.1896 [0.1461, 0.2351] |
| 3b [8,12) m | 0.7000 [0.6368, 0.7606] | 0.1979 [0.1540, 0.2438] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5144 [0.4547, 0.5700] |
| cell recall | 0.7350 [0.6828, 0.7826] |
| cell precision | 0.3957 [0.3351, 0.4576] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5185 | 0.5261 | 0.5223 |
| cell_recall | 0.7175 | 0.6925 | 0.6600 |
| cell_precision | 0.4059 | 0.4242 | 0.4321 |
| frame_det_rate | 0.6364 | 0.6000 | 0.5273 |
| frame_recall_V | 0.5161 | 0.4839 | 0.4516 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.7917 | 0.7500 | 0.6250 |
| cell_recall_V | 0.6562 | 0.6289 | 0.5977 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.8264 | 0.8056 | 0.7708 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.6136 | 0.5909 | 0.5455 |
| band3_cell_recall | 0.8661 | 0.8583 | 0.8268 |
| band4_cell_recall | 0.6818 | 0.6455 | 0.6136 |
| band1_cell_fpr_off | 0.0271 | 0.0271 | 0.0250 |
| band2_cell_fpr_off | 0.1250 | 0.1146 | 0.1062 |
| band3_cell_fpr_off | 0.1833 | 0.1646 | 0.1521 |
| band4_cell_fpr_off | 0.1833 | 0.1667 | 0.1583 |
| frame_fa_off | 0.2188 | 0.1875 | 0.1667 |
| cell_fpr_off | 0.1297 | 0.1182 | 0.1104 |
| cell_fpr_on_neg | 0.1125 | 0.0980 | 0.0888 |
