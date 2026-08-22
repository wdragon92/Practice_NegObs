# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 24 | 24 | 0 | 0 | 1 | 168 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8750 [0.7273, 1.0000] | 0.3750 [0.2917, 0.4636] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 0.8750 [0.7273, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3750 [0.1905, 0.5769] |
| cell FPR (off frames) | 0.0250 [0.0115, 0.0400] |
| cell FPR (negative cells of on frames) | 0.0000 [0.0000, 0.0000] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.5833 [0.4375, 0.7067] | 0.0750 [0.0240, 0.1360] |
| 3b [8,12) m | 0.2414 [0.1089, 0.3939] | 0.0250 [0.0000, 0.0545] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5185 [0.4248, 0.6025] |
| cell recall | 0.3750 [0.2917, 0.4636] |
| cell precision | 0.8400 [0.7123, 0.9351] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8750 [0.7273, 1.0000] | 0.3750 [0.2917, 0.4636] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 0.8750 [0.7273, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3750 [0.1905, 0.5769] |
| cell FPR (off frames) | 0.0250 [0.0115, 0.0400] |
| cell FPR (negative cells of on frames) | 0.0000 [0.0000, 0.0000] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.5833 [0.4375, 0.7067] | 0.0750 [0.0240, 0.1360] |
| 3b [8,12) m | 0.2414 [0.1089, 0.3939] | 0.0250 [0.0000, 0.0545] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5185 [0.4248, 0.6025] |
| cell recall | 0.3750 [0.2917, 0.4636] |
| cell precision | 0.8400 [0.7123, 0.9351] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5412 | 0.5185 | 0.5067 |
| cell_recall | 0.4107 | 0.3750 | 0.3393 |
| cell_precision | 0.7931 | 0.8400 | 1.0000 |
| frame_det_rate | 1.0000 | 0.8750 | 0.8750 |
| frame_recall_V | 1.0000 | 0.8750 | 0.8750 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | n/a | n/a | n/a |
| cell_recall_V | 0.4107 | 0.3750 | 0.3393 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | n/a | n/a | n/a |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_recall | 0.5833 | 0.5833 | 0.5833 |
| band4_cell_recall | 0.3103 | 0.2414 | 0.1724 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.1000 | 0.0750 | 0.0000 |
| band4_cell_fpr_off | 0.0250 | 0.0250 | 0.0000 |
| frame_fa_off | 0.3750 | 0.3750 | 0.0000 |
| cell_fpr_off | 0.0312 | 0.0250 | 0.0000 |
| cell_fpr_on_neg | 0.0096 | 0.0000 | 0.0000 |
