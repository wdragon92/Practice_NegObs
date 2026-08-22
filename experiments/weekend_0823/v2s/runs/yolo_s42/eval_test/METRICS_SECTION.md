# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/yolo_s42/cells_test/per_frame.csv`
grid: **PROVISIONAL-GRID-V2S** (4 bands x 10 sectors = 40 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.25 · tau_star = 0.25 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 4998 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.25

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.1167 [0.0714, 0.1657] | 0.0091 [0.0054, 0.0133] | 180 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 96 |
| **any tier (frame detection rate)** | 0.0642 [0.0388, 0.0923] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0049 [0.0000, 0.0125] |
| cell FPR (off frames) | 0.0002 [0.0000, 0.0007] |
| cell FPR (negative cells of on frames) | 0.0021 [0.0011, 0.0034] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0533 [0.0215, 0.0900] | 0.0002 [0.0000, 0.0008] |
| 2 [2,5) m | 0.0252 [0.0107, 0.0423] | 0.0007 [0.0000, 0.0023] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.0008 [0.0000, 0.0021] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0127 [0.0074, 0.0185] |
| cell recall | 0.0064 [0.0037, 0.0094] |
| cell precision | 0.5333 [0.3600, 0.7045] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.25

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.1167 [0.0714, 0.1657] | 0.0091 [0.0054, 0.0133] | 180 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 96 |
| **any tier (frame detection rate)** | 0.0642 [0.0388, 0.0923] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0049 [0.0000, 0.0125] |
| cell FPR (off frames) | 0.0002 [0.0000, 0.0007] |
| cell FPR (negative cells of on frames) | 0.0021 [0.0011, 0.0034] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0533 [0.0215, 0.0900] | 0.0002 [0.0000, 0.0008] |
| 2 [2,5) m | 0.0252 [0.0107, 0.0423] | 0.0007 [0.0000, 0.0023] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.0008 [0.0000, 0.0021] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0127 [0.0074, 0.0185] |
| cell recall | 0.0064 [0.0037, 0.0094] |
| cell precision | 0.5333 [0.3600, 0.7045] |

## 2. Threshold sweep

| metric | tau=0.1 | tau=0.25 | tau=0.5 |
|---|---|---|---|
| cell_f1 | 0.0176 | 0.0127 | 0.0052 |
| cell_recall | 0.0090 | 0.0064 | 0.0026 |
| cell_precision | 0.4091 | 0.5333 | 0.6500 |
| frame_det_rate | 0.0887 | 0.0642 | 0.0306 |
| frame_recall_V | 0.1556 | 0.1167 | 0.0556 |
| frame_recall_E | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_H | 0.0104 | 0.0000 | 0.0000 |
| cell_recall_V | 0.0123 | 0.0091 | 0.0037 |
| cell_recall_E | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_H | 0.0025 | 0.0000 | 0.0000 |
| band1_cell_recall | 0.0889 | 0.0533 | 0.0178 |
| band2_cell_recall | 0.0280 | 0.0252 | 0.0126 |
| band3_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_recall | 0.0020 | 0.0008 | 0.0000 |
| band1_cell_fpr_off | 0.0010 | 0.0002 | 0.0000 |
| band2_cell_fpr_off | 0.0010 | 0.0007 | 0.0000 |
| band3_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| frame_fa_off | 0.0098 | 0.0049 | 0.0000 |
| cell_fpr_off | 0.0005 | 0.0002 | 0.0000 |
| cell_fpr_on_neg | 0.0050 | 0.0021 | 0.0006 |
