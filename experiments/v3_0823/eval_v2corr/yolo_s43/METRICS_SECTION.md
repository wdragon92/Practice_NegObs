# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/eval_v2corr/yolo_s43/cells_test/per_frame.csv`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.25 · tau_star = 0.25 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 369 | 219 | 45 | 96 | 7 | 2856 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.25

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.1324 [0.0900, 0.1792] | 0.0203 [0.0134, 0.0276] | 219 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 96 |
| **any tier (frame detection rate)** | 0.0786 [0.0525, 0.1068] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0245 [0.0102, 0.0405] |
| cell FPR (off frames) | 0.0016 [0.0006, 0.0028] |
| cell FPR (negative cells of on frames) | 0.0098 [0.0062, 0.0139] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1624 [0.0820, 0.2500] | 0.0044 [0.0019, 0.0075] |
| 2 [2,5) m | 0.0582 [0.0336, 0.0856] | 0.0020 [0.0000, 0.0050] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0277 [0.0181, 0.0379] |
| cell recall | 0.0144 [0.0094, 0.0197] |
| cell precision | 0.3868 [0.2609, 0.5177] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.25

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.1324 [0.0900, 0.1792] | 0.0203 [0.0134, 0.0276] | 219 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 96 |
| **any tier (frame detection rate)** | 0.0786 [0.0525, 0.1068] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0245 [0.0102, 0.0405] |
| cell FPR (off frames) | 0.0016 [0.0006, 0.0028] |
| cell FPR (negative cells of on frames) | 0.0098 [0.0062, 0.0139] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1624 [0.0820, 0.2500] | 0.0044 [0.0019, 0.0075] |
| 2 [2,5) m | 0.0582 [0.0336, 0.0856] | 0.0020 [0.0000, 0.0050] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0277 [0.0181, 0.0379] |
| cell recall | 0.0144 [0.0094, 0.0197] |
| cell precision | 0.3868 [0.2609, 0.5177] |

## 2. Threshold sweep

| metric | tau=0.1 | tau=0.25 | tau=0.5 |
|---|---|---|---|
| cell_f1 | 0.0381 | 0.0277 | 0.0151 |
| cell_recall | 0.0203 | 0.0144 | 0.0077 |
| cell_precision | 0.3069 | 0.3868 | 0.4400 |
| frame_det_rate | 0.1030 | 0.0786 | 0.0488 |
| frame_recall_V | 0.1735 | 0.1324 | 0.0822 |
| frame_recall_E | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_H | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_V | 0.0287 | 0.0203 | 0.0109 |
| cell_recall_E | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_H | 0.0000 | 0.0000 | 0.0000 |
| band1_cell_recall | 0.2308 | 0.1624 | 0.1111 |
| band2_cell_recall | 0.0820 | 0.0582 | 0.0238 |
| band3_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band1_cell_fpr_off | 0.0074 | 0.0044 | 0.0020 |
| band2_cell_fpr_off | 0.0069 | 0.0020 | 0.0010 |
| band3_cell_fpr_off | 0.0005 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.0005 | 0.0000 | 0.0000 |
| frame_fa_off | 0.0539 | 0.0245 | 0.0123 |
| cell_fpr_off | 0.0038 | 0.0016 | 0.0007 |
| cell_fpr_on_neg | 0.0189 | 0.0098 | 0.0041 |
