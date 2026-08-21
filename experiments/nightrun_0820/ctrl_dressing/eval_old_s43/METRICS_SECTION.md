# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/nightrun_0820/ctrl_dressing/eval_old_s43/per_frame_src.csv`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 96 | 48 | 48 | 24 | 24 | 0 | 0 | 2 | 237 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9167 [0.7857, 1.0000] | 0.4219 [0.3578, 0.4821] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 0.9167 [0.7857, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3542 [0.2200, 0.4898] |
| cell FPR (off frames) | 0.0302 [0.0178, 0.0436] |
| cell FPR (negative cells of on frames) | 0.0788 [0.0592, 0.0980] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2353 [0.0000, 0.4676] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.2469 [0.1149, 0.3830] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.6476 [0.5000, 0.7841] | 0.1208 [0.0711, 0.1746] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4728 [0.3918, 0.5318] |
| cell recall | 0.4219 [0.3578, 0.4821] |
| cell precision | 0.5376 [0.3929, 0.6618] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9167 [0.7857, 1.0000] | 0.4219 [0.3578, 0.4821] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 0.9167 [0.7857, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3542 [0.2200, 0.4898] |
| cell FPR (off frames) | 0.0302 [0.0178, 0.0436] |
| cell FPR (negative cells of on frames) | 0.0788 [0.0592, 0.0980] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2353 [0.0000, 0.4676] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.2469 [0.1149, 0.3830] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.6476 [0.5000, 0.7841] | 0.1208 [0.0711, 0.1746] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4728 [0.3918, 0.5318] |
| cell recall | 0.4219 [0.3578, 0.4821] |
| cell precision | 0.5376 [0.3929, 0.6618] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5788 | 0.4728 | 0.4022 |
| cell_recall | 0.6118 | 0.4219 | 0.3038 |
| cell_precision | 0.5492 | 0.5376 | 0.5950 |
| frame_det_rate | 1.0000 | 0.9167 | 0.8750 |
| frame_recall_V | 1.0000 | 0.9167 | 0.8750 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | n/a | n/a | n/a |
| cell_recall_V | 0.6118 | 0.4219 | 0.3038 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | n/a | n/a | n/a |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | 0.4902 | 0.2353 | 0.1176 |
| band3_cell_recall | 0.3951 | 0.2469 | 0.1605 |
| band4_cell_recall | 0.8381 | 0.6476 | 0.5048 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0083 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.1875 | 0.1208 | 0.0750 |
| frame_fa_off | 0.4792 | 0.3542 | 0.2500 |
| cell_fpr_off | 0.0490 | 0.0302 | 0.0187 |
| cell_fpr_on_neg | 0.0996 | 0.0788 | 0.0429 |
