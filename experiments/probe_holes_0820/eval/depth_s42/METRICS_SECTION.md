# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **probe** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 144 | 72 | 72 | 72 | 15 | 27 | 30 | 3 | 189 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.2000 [0.0000, 0.4286] | 0.2000 [0.0000, 0.4412] | 15 |
| E | 0.1111 [0.0000, 0.2424] | 0.0476 [0.0000, 0.1154] | 27 |
| H | 0.4000 [0.2273, 0.5806] | 0.4444 [0.2459, 0.6447] | 30 |
| **any tier (frame detection rate)** | 0.2500 [0.1548, 0.3529] | — | 72 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3333 [0.2241, 0.4444] |
| cell FPR (off frames) | 0.1521 [0.0898, 0.2194] |
| cell FPR (negative cells of on frames) | 0.1655 [0.1035, 0.2337] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.3158 [0.1842, 0.4519] | 0.1667 [0.0845, 0.2571] |
| 3a [5,8) m | 0.3000 [0.1000, 0.5217] | 0.1833 [0.1000, 0.2725] |
| 3b [8,12) m | 0.1111 [0.0000, 0.2609] | 0.2583 [0.1649, 0.3552] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1448 [0.0932, 0.1918] |
| cell recall | 0.2540 [0.1492, 0.3674] |
| cell precision | 0.1013 [0.0660, 0.1365] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.2000 [0.0000, 0.4286] | 0.2000 [0.0000, 0.4412] | 15 |
| E | 0.1111 [0.0000, 0.2424] | 0.0476 [0.0000, 0.1154] | 27 |
| H | 0.4000 [0.2273, 0.5806] | 0.4444 [0.2459, 0.6447] | 30 |
| **any tier (frame detection rate)** | 0.2500 [0.1548, 0.3529] | — | 72 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3333 [0.2241, 0.4444] |
| cell FPR (off frames) | 0.1521 [0.0898, 0.2194] |
| cell FPR (negative cells of on frames) | 0.1655 [0.1035, 0.2337] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.3158 [0.1842, 0.4519] | 0.1667 [0.0845, 0.2571] |
| 3a [5,8) m | 0.3000 [0.1000, 0.5217] | 0.1833 [0.1000, 0.2725] |
| 3b [8,12) m | 0.1111 [0.0000, 0.2609] | 0.2583 [0.1649, 0.3552] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1448 [0.0932, 0.1918] |
| cell recall | 0.2540 [0.1492, 0.3674] |
| cell precision | 0.1013 [0.0660, 0.1365] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.1440 | 0.1448 | 0.1429 |
| cell_recall | 0.2857 | 0.2540 | 0.2381 |
| cell_precision | 0.0963 | 0.1013 | 0.1020 |
| frame_det_rate | 0.3333 | 0.2500 | 0.2083 |
| frame_recall_V | 0.2000 | 0.2000 | 0.2000 |
| frame_recall_E | 0.2222 | 0.1111 | 0.0000 |
| frame_recall_H | 0.5000 | 0.4000 | 0.4000 |
| cell_recall_V | 0.2000 | 0.2000 | 0.2000 |
| cell_recall_E | 0.0952 | 0.0476 | 0.0000 |
| cell_recall_H | 0.4815 | 0.4444 | 0.4444 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.3421 | 0.3158 | 0.3158 |
| band3_cell_recall | 0.3000 | 0.3000 | 0.3000 |
| band4_cell_recall | 0.2222 | 0.1111 | 0.0000 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.1750 | 0.1667 | 0.1667 |
| band3_cell_fpr_off | 0.2000 | 0.1833 | 0.1667 |
| band4_cell_fpr_off | 0.3167 | 0.2583 | 0.2167 |
| frame_fa_off | 0.5000 | 0.3333 | 0.2917 |
| cell_fpr_off | 0.1729 | 0.1521 | 0.1375 |
| cell_fpr_on_neg | 0.2062 | 0.1655 | 0.1583 |
