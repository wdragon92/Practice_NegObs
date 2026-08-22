# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 24 | 24 | 0 | 0 | 1 | 129 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.7500 [0.5652, 0.9130] | 0.6279 [0.4662, 0.7605] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 0.7500 [0.5652, 0.9130] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.5000 [0.3000, 0.7000] |
| cell FPR (off frames) | 0.0437 [0.0250, 0.0630] |
| cell FPR (negative cells of on frames) | 0.0684 [0.0291, 0.1141] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.7692 [0.5588, 0.9231] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.5667 [0.4151, 0.7083] | 0.1750 [0.1000, 0.2522] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6353 [0.5079, 0.7206] |
| cell recall | 0.6279 [0.4662, 0.7605] |
| cell precision | 0.6429 [0.5179, 0.7440] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.7500 [0.5652, 0.9130] | 0.6279 [0.4662, 0.7605] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 0.7500 [0.5652, 0.9130] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.5000 [0.3000, 0.7000] |
| cell FPR (off frames) | 0.0437 [0.0250, 0.0630] |
| cell FPR (negative cells of on frames) | 0.0684 [0.0291, 0.1141] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.7692 [0.5588, 0.9231] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.5667 [0.4151, 0.7083] | 0.1750 [0.1000, 0.2522] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6353 [0.5079, 0.7206] |
| cell recall | 0.6279 [0.4662, 0.7605] |
| cell precision | 0.6429 [0.5179, 0.7440] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.7033 | 0.6353 | 0.5714 |
| cell_recall | 0.7442 | 0.6279 | 0.5116 |
| cell_precision | 0.6667 | 0.6429 | 0.6471 |
| frame_det_rate | 0.8750 | 0.7500 | 0.5000 |
| frame_recall_V | 0.8750 | 0.7500 | 0.5000 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | n/a | n/a | n/a |
| cell_recall_V | 0.7442 | 0.6279 | 0.5116 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | n/a | n/a | n/a |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | 0.7692 | 0.7692 | 0.7692 |
| band4_cell_recall | 0.7333 | 0.5667 | 0.4000 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.2000 | 0.1750 | 0.1500 |
| frame_fa_off | 0.6250 | 0.5000 | 0.3750 |
| cell_fpr_off | 0.0500 | 0.0437 | 0.0375 |
| cell_fpr_on_neg | 0.0684 | 0.0684 | 0.0513 |
