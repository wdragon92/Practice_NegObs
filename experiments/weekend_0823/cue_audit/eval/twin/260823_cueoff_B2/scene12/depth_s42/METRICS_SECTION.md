# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 24 | 24 | 0 | 0 | 1 | 129 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8750 [0.7273, 1.0000] | 0.6047 [0.4778, 0.7311] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 0.8750 [0.7273, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.5000 [0.2941, 0.7000] |
| cell FPR (off frames) | 0.0437 [0.0237, 0.0659] |
| cell FPR (negative cells of on frames) | 0.0684 [0.0291, 0.1141] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.6923 [0.4706, 0.8801] | 0.0250 [0.0000, 0.0545] |
| 3b [8,12) m | 0.5667 [0.4651, 0.6742] | 0.1500 [0.0842, 0.2174] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6190 [0.5294, 0.6820] |
| cell recall | 0.6047 [0.4778, 0.7311] |
| cell precision | 0.6341 [0.5310, 0.7257] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8750 [0.7273, 1.0000] | 0.6047 [0.4778, 0.7311] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 0.8750 [0.7273, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.5000 [0.2941, 0.7000] |
| cell FPR (off frames) | 0.0437 [0.0237, 0.0659] |
| cell FPR (negative cells of on frames) | 0.0684 [0.0291, 0.1141] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.6923 [0.4706, 0.8801] | 0.0250 [0.0000, 0.0545] |
| 3b [8,12) m | 0.5667 [0.4651, 0.6742] | 0.1500 [0.0842, 0.2174] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6190 [0.5294, 0.6820] |
| cell recall | 0.6047 [0.4778, 0.7311] |
| cell precision | 0.6341 [0.5310, 0.7257] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.6154 | 0.6190 | 0.6316 |
| cell_recall | 0.6512 | 0.6047 | 0.5581 |
| cell_precision | 0.5833 | 0.6341 | 0.7273 |
| frame_det_rate | 0.8750 | 0.8750 | 0.8750 |
| frame_recall_V | 0.8750 | 0.8750 | 0.8750 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | n/a | n/a | n/a |
| cell_recall_V | 0.6512 | 0.6047 | 0.5581 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | n/a | n/a | n/a |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | 0.6923 | 0.6923 | 0.6923 |
| band4_cell_recall | 0.6333 | 0.5667 | 0.5000 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0250 | 0.0250 | 0.0000 |
| band4_cell_fpr_off | 0.2500 | 0.1500 | 0.0750 |
| frame_fa_off | 0.7500 | 0.5000 | 0.2500 |
| cell_fpr_off | 0.0688 | 0.0437 | 0.0187 |
| cell_fpr_on_neg | 0.0769 | 0.0684 | 0.0513 |
