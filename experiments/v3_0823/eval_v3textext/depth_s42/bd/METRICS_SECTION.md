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
| V | 0.5161 [0.4149, 0.6186] | 0.6719 [0.5944, 0.7377] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.6250 [0.5128, 0.7369] | 0.8056 [0.7213, 0.8739] | 72 |
| **any tier (frame detection rate)** | 0.5636 [0.4886, 0.6403] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1667 [0.1241, 0.2111] |
| cell FPR (off frames) | 0.1115 [0.0823, 0.1419] |
| cell FPR (negative cells of on frames) | 0.0928 [0.0684, 0.1195] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0083 [0.0000, 0.0189] |
| 2 [2,5) m | 0.7045 [0.5403, 0.8529] | 0.1271 [0.0895, 0.1660] |
| 3a [5,8) m | 0.8504 [0.7954, 0.8961] | 0.1604 [0.1189, 0.2029] |
| 3b [8,12) m | 0.6773 [0.6071, 0.7436] | 0.1500 [0.1111, 0.1904] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5523 [0.4885, 0.6102] |
| cell recall | 0.7200 [0.6648, 0.7702] |
| cell precision | 0.4479 [0.3790, 0.5186] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.36

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.5161 [0.4149, 0.6186] | 0.6758 [0.5977, 0.7423] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.7500 [0.6479, 0.8491] | 0.8472 [0.7797, 0.9023] | 72 |
| **any tier (frame detection rate)** | 0.6182 [0.5449, 0.6933] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2292 [0.1809, 0.2786] |
| cell FPR (off frames) | 0.1198 [0.0901, 0.1509] |
| cell FPR (negative cells of on frames) | 0.1013 [0.0760, 0.1289] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0083 [0.0000, 0.0189] |
| 2 [2,5) m | 0.7273 [0.5620, 0.8750] | 0.1292 [0.0916, 0.1681] |
| 3a [5,8) m | 0.8583 [0.8052, 0.9015] | 0.1708 [0.1286, 0.2146] |
| 3b [8,12) m | 0.7000 [0.6338, 0.7626] | 0.1708 [0.1306, 0.2134] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5468 [0.4839, 0.6040] |
| cell recall | 0.7375 [0.6856, 0.7858] |
| cell precision | 0.4345 [0.3686, 0.5017] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5466 | 0.5523 | 0.5601 |
| cell_recall | 0.7475 | 0.7200 | 0.7050 |
| cell_precision | 0.4308 | 0.4479 | 0.4646 |
| frame_det_rate | 0.6364 | 0.5636 | 0.5636 |
| frame_recall_V | 0.5484 | 0.5161 | 0.5161 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.7500 | 0.6250 | 0.6250 |
| cell_recall_V | 0.6836 | 0.6719 | 0.6562 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.8611 | 0.8056 | 0.7917 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.7500 | 0.7045 | 0.6136 |
| band3_cell_recall | 0.8661 | 0.8504 | 0.8425 |
| band4_cell_recall | 0.7091 | 0.6773 | 0.6727 |
| band1_cell_fpr_off | 0.0083 | 0.0083 | 0.0042 |
| band2_cell_fpr_off | 0.1333 | 0.1271 | 0.1187 |
| band3_cell_fpr_off | 0.1708 | 0.1604 | 0.1562 |
| band4_cell_fpr_off | 0.1792 | 0.1500 | 0.1396 |
| frame_fa_off | 0.2500 | 0.1667 | 0.1667 |
| cell_fpr_off | 0.1229 | 0.1115 | 0.1047 |
| cell_fpr_on_neg | 0.1046 | 0.0928 | 0.0816 |
