# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 24 | 0 | 0 | 24 | 1 | 63 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.7500 [0.5713, 0.9130] | 0.5714 [0.4355, 0.6923] | 24 |
| **any tier (frame detection rate)** | 0.7500 [0.5713, 0.9130] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (negative cells of on frames) | 0.1079 [0.0699, 0.1484] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.5000 [0.2143, 0.7917] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.6000 [0.4167, 0.7674] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5000 [0.3960, 0.5872] |
| cell recall | 0.5714 [0.4355, 0.6923] |
| cell precision | 0.4444 [0.3433, 0.5571] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.7500 [0.5713, 0.9130] | 0.5714 [0.4355, 0.6923] | 24 |
| **any tier (frame detection rate)** | 0.7500 [0.5713, 0.9130] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (negative cells of on frames) | 0.1079 [0.0699, 0.1484] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.5000 [0.2143, 0.7917] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.6000 [0.4167, 0.7674] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5000 [0.3960, 0.5872] |
| cell recall | 0.5714 [0.4355, 0.6923] |
| cell precision | 0.4444 [0.3433, 0.5571] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5085 | 0.5000 | 0.1667 |
| cell_recall | 0.7143 | 0.5714 | 0.1429 |
| cell_precision | 0.3947 | 0.4444 | 0.2000 |
| frame_det_rate | 0.8750 | 0.7500 | 0.2500 |
| frame_recall_V | n/a | n/a | n/a |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.8750 | 0.7500 | 0.2500 |
| cell_recall_V | n/a | n/a | n/a |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.7143 | 0.5714 | 0.1429 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | 0.6667 | 0.5000 | 0.0000 |
| band4_cell_recall | 0.7333 | 0.6000 | 0.2000 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| frame_fa_off | 0.0000 | 0.0000 | 0.0000 |
| cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| cell_fpr_on_neg | 0.1655 | 0.1079 | 0.0863 |
