# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **probe** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 144 | 72 | 72 | 72 | 15 | 27 | 30 | 3 | 189 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 15 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 27 |
| H | 0.3000 [0.1379, 0.4688] | 0.3333 [0.1481, 0.5333] | 30 |
| **any tier (frame detection rate)** | 0.1250 [0.0526, 0.2029] | — | 72 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1667 [0.0845, 0.2571] |
| cell FPR (off frames) | 0.0979 [0.0429, 0.1604] |
| cell FPR (negative cells of on frames) | 0.0935 [0.0420, 0.1496] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0083 [0.0000, 0.0189] |
| 2 [2,5) m | 0.1842 [0.0769, 0.2982] | 0.1250 [0.0540, 0.2063] |
| 3a [5,8) m | 0.2000 [0.0000, 0.4118] | 0.1333 [0.0611, 0.2159] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.1250 [0.0540, 0.2063] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1139 [0.0519, 0.1682] |
| cell recall | 0.1429 [0.0568, 0.2366] |
| cell precision | 0.0947 [0.0461, 0.1433] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 15 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 27 |
| H | 0.3000 [0.1379, 0.4688] | 0.3333 [0.1481, 0.5333] | 30 |
| **any tier (frame detection rate)** | 0.1250 [0.0526, 0.2029] | — | 72 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1667 [0.0845, 0.2571] |
| cell FPR (off frames) | 0.0979 [0.0429, 0.1604] |
| cell FPR (negative cells of on frames) | 0.0935 [0.0420, 0.1496] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0083 [0.0000, 0.0189] |
| 2 [2,5) m | 0.1842 [0.0769, 0.2982] | 0.1250 [0.0540, 0.2063] |
| 3a [5,8) m | 0.2000 [0.0000, 0.4118] | 0.1333 [0.0611, 0.2159] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.1250 [0.0540, 0.2063] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1139 [0.0519, 0.1682] |
| cell recall | 0.1429 [0.0568, 0.2366] |
| cell precision | 0.0947 [0.0461, 0.1433] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.0995 | 0.1139 | 0.1192 |
| cell_recall | 0.1746 | 0.1429 | 0.1429 |
| cell_precision | 0.0696 | 0.0947 | 0.1023 |
| frame_det_rate | 0.2083 | 0.1250 | 0.1250 |
| frame_recall_V | 0.2000 | 0.0000 | 0.0000 |
| frame_recall_E | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_H | 0.4000 | 0.3000 | 0.3000 |
| cell_recall_V | 0.0667 | 0.0000 | 0.0000 |
| cell_recall_E | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_H | 0.3704 | 0.3333 | 0.3333 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.1842 | 0.1842 | 0.1842 |
| band3_cell_recall | 0.3000 | 0.2000 | 0.2000 |
| band4_cell_recall | 0.1111 | 0.0000 | 0.0000 |
| band1_cell_fpr_off | 0.0417 | 0.0083 | 0.0000 |
| band2_cell_fpr_off | 0.1250 | 0.1250 | 0.1167 |
| band3_cell_fpr_off | 0.2000 | 0.1333 | 0.1250 |
| band4_cell_fpr_off | 0.2500 | 0.1250 | 0.1250 |
| frame_fa_off | 0.4167 | 0.1667 | 0.1250 |
| cell_fpr_off | 0.1542 | 0.0979 | 0.0917 |
| cell_fpr_on_neg | 0.1751 | 0.0935 | 0.0839 |
