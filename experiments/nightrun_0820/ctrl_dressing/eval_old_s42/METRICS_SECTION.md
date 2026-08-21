# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/nightrun_0820/ctrl_dressing/eval_old_s42/per_frame_src.csv`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 96 | 48 | 48 | 24 | 24 | 0 | 0 | 2 | 237 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6250 [0.4231, 0.8182] | 0.2616 [0.1646, 0.3554] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 0.6250 [0.4231, 0.8182] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.6042 [0.4583, 0.7442] |
| cell FPR (off frames) | 0.1313 [0.0910, 0.1744] |
| cell FPR (negative cells of on frames) | 0.2310 [0.1715, 0.2881] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0750 [0.0275, 0.1333] |
| 3a [5,8) m | 0.3210 [0.1852, 0.4605] | 0.1792 [0.1208, 0.2408] |
| 3b [8,12) m | 0.3429 [0.1892, 0.4951] | 0.2708 [0.1897, 0.3535] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2095 [0.1176, 0.2975] |
| cell recall | 0.2616 [0.1646, 0.3554] |
| cell precision | 0.1746 [0.0872, 0.2794] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6250 [0.4231, 0.8182] | 0.2616 [0.1646, 0.3554] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 0.6250 [0.4231, 0.8182] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.6042 [0.4583, 0.7442] |
| cell FPR (off frames) | 0.1313 [0.0910, 0.1744] |
| cell FPR (negative cells of on frames) | 0.2310 [0.1715, 0.2881] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0750 [0.0275, 0.1333] |
| 3a [5,8) m | 0.3210 [0.1852, 0.4605] | 0.1792 [0.1208, 0.2408] |
| 3b [8,12) m | 0.3429 [0.1892, 0.4951] | 0.2708 [0.1897, 0.3535] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2095 [0.1176, 0.2975] |
| cell recall | 0.2616 [0.1646, 0.3554] |
| cell precision | 0.1746 [0.0872, 0.2794] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.2399 | 0.2095 | 0.1535 |
| cell_recall | 0.3882 | 0.2616 | 0.1519 |
| cell_precision | 0.1736 | 0.1746 | 0.1552 |
| frame_det_rate | 0.7500 | 0.6250 | 0.4583 |
| frame_recall_V | 0.7500 | 0.6250 | 0.4583 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | n/a | n/a | n/a |
| cell_recall_V | 0.3882 | 0.2616 | 0.1519 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | n/a | n/a | n/a |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_recall | 0.4568 | 0.3210 | 0.2222 |
| band4_cell_recall | 0.5238 | 0.3429 | 0.1714 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.2458 | 0.0750 | 0.0250 |
| band3_cell_fpr_off | 0.2875 | 0.1792 | 0.0750 |
| band4_cell_fpr_off | 0.3167 | 0.2708 | 0.2042 |
| frame_fa_off | 0.6458 | 0.6042 | 0.4792 |
| cell_fpr_off | 0.2125 | 0.1313 | 0.0760 |
| cell_fpr_on_neg | 0.3237 | 0.2310 | 0.1701 |
