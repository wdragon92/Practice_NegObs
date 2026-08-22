# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/nightrun_0820/ctrl_dressing/eval_old_depth_s43/per_frame_src.csv`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 96 | 48 | 48 | 24 | 24 | 0 | 0 | 2 | 237 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.8228 [0.7841, 0.8646] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0625 [0.0000, 0.1395] |
| cell FPR (off frames) | 0.0281 [0.0000, 0.0628] |
| cell FPR (negative cells of on frames) | 0.0581 [0.0268, 0.0982] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.8824 [0.7200, 1.0000] | 0.0250 [0.0000, 0.0558] |
| 3a [5,8) m | 0.8148 [0.7304, 0.8901] | 0.0375 [0.0000, 0.0837] |
| 3b [8,12) m | 0.8000 [0.6990, 0.9011] | 0.0500 [0.0000, 0.1116] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.7784 [0.7003, 0.8394] |
| cell recall | 0.8228 [0.7841, 0.8646] |
| cell precision | 0.7386 [0.6142, 0.8479] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.8228 [0.7841, 0.8646] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0625 [0.0000, 0.1395] |
| cell FPR (off frames) | 0.0281 [0.0000, 0.0628] |
| cell FPR (negative cells of on frames) | 0.0581 [0.0268, 0.0982] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.8824 [0.7200, 1.0000] | 0.0250 [0.0000, 0.0558] |
| 3a [5,8) m | 0.8148 [0.7304, 0.8901] | 0.0375 [0.0000, 0.0837] |
| 3b [8,12) m | 0.8000 [0.6990, 0.9011] | 0.0500 [0.0000, 0.1116] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.7784 [0.7003, 0.8394] |
| cell recall | 0.8228 [0.7841, 0.8646] |
| cell precision | 0.7386 [0.6142, 0.8479] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.7845 | 0.7784 | 0.7375 |
| cell_recall | 0.8987 | 0.8228 | 0.7468 |
| cell_precision | 0.6961 | 0.7386 | 0.7284 |
| frame_det_rate | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_V | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | n/a | n/a | n/a |
| cell_recall_V | 0.8987 | 0.8228 | 0.7468 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | n/a | n/a | n/a |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | 0.9412 | 0.8824 | 0.8235 |
| band3_cell_recall | 0.8519 | 0.8148 | 0.6667 |
| band4_cell_recall | 0.9143 | 0.8000 | 0.7714 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0250 | 0.0250 | 0.0250 |
| band3_cell_fpr_off | 0.0625 | 0.0375 | 0.0375 |
| band4_cell_fpr_off | 0.0500 | 0.0500 | 0.0500 |
| frame_fa_off | 0.0625 | 0.0625 | 0.0625 |
| cell_fpr_off | 0.0344 | 0.0281 | 0.0281 |
| cell_fpr_on_neg | 0.0830 | 0.0581 | 0.0539 |
