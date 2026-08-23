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
| V | 0.4839 [0.3837, 0.5865] | 0.6172 [0.5381, 0.6847] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.7917 [0.6933, 0.8833] | 0.7639 [0.6734, 0.8401] | 72 |
| **any tier (frame detection rate)** | 0.6182 [0.5449, 0.6914] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2604 [0.2096, 0.3125] |
| cell FPR (off frames) | 0.1448 [0.1132, 0.1771] |
| cell FPR (negative cells of on frames) | 0.0961 [0.0725, 0.1219] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0187 [0.0081, 0.0319] |
| 2 [2,5) m | 0.6136 [0.4522, 0.7681] | 0.1458 [0.1082, 0.1856] |
| 3a [5,8) m | 0.8189 [0.7623, 0.8662] | 0.2000 [0.1570, 0.2442] |
| 3b [8,12) m | 0.6227 [0.5525, 0.6907] | 0.2146 [0.1700, 0.2597] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4908 [0.4294, 0.5487] |
| cell recall | 0.6700 [0.6122, 0.7228] |
| cell precision | 0.3873 [0.3244, 0.4524] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.21

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4839 [0.3837, 0.5865] | 0.6406 [0.5610, 0.7073] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.8333 [0.7429, 0.9155] | 0.8542 [0.7920, 0.9056] | 72 |
| **any tier (frame detection rate)** | 0.6364 [0.5629, 0.7079] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2708 [0.2195, 0.3233] |
| cell FPR (off frames) | 0.1672 [0.1326, 0.2021] |
| cell FPR (negative cells of on frames) | 0.1191 [0.0921, 0.1478] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0187 [0.0081, 0.0319] |
| 2 [2,5) m | 0.7045 [0.5723, 0.8252] | 0.1833 [0.1411, 0.2273] |
| 3a [5,8) m | 0.8425 [0.7869, 0.8879] | 0.2292 [0.1823, 0.2774] |
| 3b [8,12) m | 0.6773 [0.6132, 0.7382] | 0.2375 [0.1904, 0.2852] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4828 [0.4228, 0.5399] |
| cell recall | 0.7175 [0.6645, 0.7659] |
| cell precision | 0.3638 [0.3050, 0.4245] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4892 | 0.4908 | 0.5069 |
| cell_recall | 0.7075 | 0.6700 | 0.6425 |
| cell_precision | 0.3738 | 0.3873 | 0.4186 |
| frame_det_rate | 0.6364 | 0.6182 | 0.5455 |
| frame_recall_V | 0.4839 | 0.4839 | 0.4839 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.8333 | 0.7917 | 0.6250 |
| cell_recall_V | 0.6328 | 0.6172 | 0.5938 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.8403 | 0.7639 | 0.7292 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.6591 | 0.6136 | 0.5227 |
| band3_cell_recall | 0.8425 | 0.8189 | 0.7953 |
| band4_cell_recall | 0.6682 | 0.6227 | 0.6045 |
| band1_cell_fpr_off | 0.0187 | 0.0187 | 0.0125 |
| band2_cell_fpr_off | 0.1646 | 0.1458 | 0.1292 |
| band3_cell_fpr_off | 0.2188 | 0.2000 | 0.1708 |
| band4_cell_fpr_off | 0.2333 | 0.2146 | 0.1938 |
| frame_fa_off | 0.2708 | 0.2604 | 0.2292 |
| cell_fpr_off | 0.1589 | 0.1448 | 0.1266 |
| cell_fpr_on_neg | 0.1112 | 0.0961 | 0.0750 |
