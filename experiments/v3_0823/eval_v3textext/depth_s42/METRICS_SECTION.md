# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.36 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4839 [0.3837, 0.5865] | 0.6719 [0.5935, 0.7392] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.6250 [0.5128, 0.7369] | 0.7014 [0.6140, 0.7761] | 72 |
| **any tier (frame detection rate)** | 0.5455 [0.4706, 0.6228] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2917 [0.2401, 0.3449] |
| cell FPR (off frames) | 0.1417 [0.1118, 0.1729] |
| cell FPR (negative cells of on frames) | 0.1007 [0.0769, 0.1263] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.7955 [0.6667, 0.9000] | 0.1500 [0.1103, 0.1913] |
| 3a [5,8) m | 0.8031 [0.7418, 0.8571] | 0.2062 [0.1628, 0.2511] |
| 3b [8,12) m | 0.6182 [0.5477, 0.6853] | 0.2104 [0.1682, 0.2536] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4973 [0.4329, 0.5576] |
| cell recall | 0.6825 [0.6248, 0.7335] |
| cell precision | 0.3911 [0.3252, 0.4591] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.36

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4839 [0.3837, 0.5865] | 0.6797 [0.6003, 0.7476] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.7917 [0.6935, 0.8833] | 0.7847 [0.7165, 0.8426] | 72 |
| **any tier (frame detection rate)** | 0.6182 [0.5455, 0.6919] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3854 [0.3289, 0.4433] |
| cell FPR (off frames) | 0.1604 [0.1295, 0.1926] |
| cell FPR (negative cells of on frames) | 0.1171 [0.0910, 0.1448] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.8409 [0.7083, 0.9474] | 0.1667 [0.1251, 0.2098] |
| 3a [5,8) m | 0.8110 [0.7514, 0.8620] | 0.2188 [0.1745, 0.2647] |
| 3b [8,12) m | 0.6682 [0.6037, 0.7294] | 0.2562 [0.2118, 0.3014] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4893 [0.4265, 0.5487] |
| cell recall | 0.7175 [0.6639, 0.7663] |
| cell precision | 0.3713 [0.3098, 0.4346] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4821 | 0.4973 | 0.5080 |
| cell_recall | 0.7250 | 0.6825 | 0.6350 |
| cell_precision | 0.3611 | 0.3911 | 0.4233 |
| frame_det_rate | 0.6182 | 0.5455 | 0.5455 |
| frame_recall_V | 0.4839 | 0.4839 | 0.4839 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.7917 | 0.6250 | 0.6250 |
| cell_recall_V | 0.6875 | 0.6719 | 0.6367 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.7917 | 0.7014 | 0.6319 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.8636 | 0.7955 | 0.6818 |
| band3_cell_recall | 0.8110 | 0.8031 | 0.7638 |
| band4_cell_recall | 0.6773 | 0.6182 | 0.5773 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.1729 | 0.1500 | 0.1354 |
| band3_cell_fpr_off | 0.2250 | 0.2062 | 0.1729 |
| band4_cell_fpr_off | 0.2750 | 0.2104 | 0.1750 |
| frame_fa_off | 0.4271 | 0.2917 | 0.2500 |
| cell_fpr_off | 0.1682 | 0.1417 | 0.1208 |
| cell_fpr_on_neg | 0.1250 | 0.1007 | 0.0750 |
