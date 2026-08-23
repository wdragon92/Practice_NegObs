# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 96 | 48 | 48 | 39 | 12 | 0 | 27 | 1 | 183 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 12 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.8889 [0.7567, 1.0000] | 0.8537 [0.7126, 0.9730] | 27 |
| **any tier (frame detection rate)** | 0.9231 [0.8293, 1.0000] | — | 39 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1667 [0.0667, 0.2800] |
| cell FPR (off frames) | 0.0323 [0.0090, 0.0620] |
| cell FPR (negative cells of on frames) | 0.4453 [0.3799, 0.5091] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0417 [0.0082, 0.0870] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0458 [0.0115, 0.0894] |
| 3b [8,12) m | 0.9016 [0.8023, 0.9824] | 0.0417 [0.0080, 0.0857] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4552 [0.3927, 0.5138] |
| cell recall | 0.9016 [0.8023, 0.9824] |
| cell precision | 0.3044 [0.2535, 0.3558] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 12 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.8889 [0.7567, 1.0000] | 0.8537 [0.7126, 0.9730] | 27 |
| **any tier (frame detection rate)** | 0.9231 [0.8293, 1.0000] | — | 39 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1667 [0.0667, 0.2800] |
| cell FPR (off frames) | 0.0323 [0.0090, 0.0620] |
| cell FPR (negative cells of on frames) | 0.4453 [0.3799, 0.5091] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0417 [0.0082, 0.0870] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0458 [0.0115, 0.0894] |
| 3b [8,12) m | 0.9016 [0.8023, 0.9824] | 0.0417 [0.0080, 0.0857] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4552 [0.3927, 0.5138] |
| cell recall | 0.9016 [0.8023, 0.9824] |
| cell precision | 0.3044 [0.2535, 0.3558] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3939 | 0.4552 | 0.4983 |
| cell_recall | 0.9235 | 0.9016 | 0.7978 |
| cell_precision | 0.2504 | 0.3044 | 0.3623 |
| frame_det_rate | 0.9744 | 0.9231 | 0.8974 |
| frame_recall_V | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.9630 | 0.8889 | 0.8519 |
| cell_recall_V | 1.0000 | 1.0000 | 0.9167 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.8862 | 0.8537 | 0.7398 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | n/a | n/a | n/a |
| band4_cell_recall | 0.9235 | 0.9016 | 0.7978 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.1250 | 0.0417 | 0.0042 |
| band3_cell_fpr_off | 0.1042 | 0.0458 | 0.0083 |
| band4_cell_fpr_off | 0.1000 | 0.0417 | 0.0042 |
| frame_fa_off | 0.2708 | 0.1667 | 0.0625 |
| cell_fpr_off | 0.0823 | 0.0323 | 0.0042 |
| cell_fpr_on_neg | 0.5495 | 0.4453 | 0.3256 |
