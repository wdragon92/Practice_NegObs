# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 24 | 6 | 0 | 18 | 1 | 168 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.9286 [0.8000, 1.0000] | 6 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 1.0000 [1.0000, 1.0000] | 0.7857 [0.6322, 0.9184] | 18 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3750 [0.1905, 0.5769] |
| cell FPR (off frames) | 0.0250 [0.0115, 0.0400] |
| cell FPR (negative cells of on frames) | 0.1058 [0.0588, 0.1633] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 1.0000 [1.0000, 1.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.7500 [0.5714, 0.8936] | 0.0750 [0.0240, 0.1360] |
| 3b [8,12) m | 0.8621 [0.7570, 0.9605] | 0.0250 [0.0000, 0.0545] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.7863 [0.7179, 0.8365] |
| cell recall | 0.8214 [0.6985, 0.9236] |
| cell precision | 0.7541 [0.6920, 0.8118] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.9286 [0.8000, 1.0000] | 6 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 1.0000 [1.0000, 1.0000] | 0.7857 [0.6322, 0.9184] | 18 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3750 [0.1905, 0.5769] |
| cell FPR (off frames) | 0.0250 [0.0115, 0.0400] |
| cell FPR (negative cells of on frames) | 0.1058 [0.0588, 0.1633] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 1.0000 [1.0000, 1.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.7500 [0.5714, 0.8936] | 0.0750 [0.0240, 0.1360] |
| 3b [8,12) m | 0.8621 [0.7570, 0.9605] | 0.0250 [0.0000, 0.0545] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.7863 [0.7179, 0.8365] |
| cell recall | 0.8214 [0.6985, 0.9236] |
| cell precision | 0.7541 [0.6920, 0.8118] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.8130 | 0.7863 | 0.7963 |
| cell_recall | 0.8929 | 0.8214 | 0.7679 |
| cell_precision | 0.7463 | 0.7541 | 0.8269 |
| frame_det_rate | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_V | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 1.0000 | 1.0000 | 1.0000 |
| cell_recall_V | 0.9286 | 0.9286 | 0.9286 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.8810 | 0.7857 | 0.7143 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | 1.0000 | 1.0000 | 0.6667 |
| band3_cell_recall | 0.7500 | 0.7500 | 0.7500 |
| band4_cell_recall | 1.0000 | 0.8621 | 0.7931 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.1000 | 0.0750 | 0.0000 |
| band4_cell_fpr_off | 0.0250 | 0.0250 | 0.0000 |
| frame_fa_off | 0.3750 | 0.3750 | 0.0000 |
| cell_fpr_off | 0.0312 | 0.0250 | 0.0000 |
| cell_fpr_on_neg | 0.1154 | 0.1058 | 0.0865 |
