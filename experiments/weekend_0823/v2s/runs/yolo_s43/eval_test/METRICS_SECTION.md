# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/yolo_s43/cells_test/per_frame.csv`
grid: **PROVISIONAL-GRID-V2S** (4 bands x 10 sectors = 40 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.25 · tau_star = 0.25 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 4998 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.25

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.1611 [0.1098, 0.2164] | 0.0120 [0.0078, 0.0165] | 180 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 96 |
| **any tier (frame detection rate)** | 0.0887 [0.0594, 0.1200] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0245 [0.0102, 0.0405] |
| cell FPR (off frames) | 0.0008 [0.0003, 0.0014] |
| cell FPR (negative cells of on frames) | 0.0061 [0.0039, 0.0086] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0933 [0.0481, 0.1420] | 0.0022 [0.0009, 0.0037] |
| 2 [2,5) m | 0.0294 [0.0161, 0.0448] | 0.0010 [0.0000, 0.0025] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0164 [0.0105, 0.0227] |
| cell recall | 0.0084 [0.0054, 0.0117] |
| cell precision | 0.3387 [0.2222, 0.4640] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.25

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.1611 [0.1098, 0.2164] | 0.0120 [0.0078, 0.0165] | 180 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 96 |
| **any tier (frame detection rate)** | 0.0887 [0.0594, 0.1200] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0245 [0.0102, 0.0405] |
| cell FPR (off frames) | 0.0008 [0.0003, 0.0014] |
| cell FPR (negative cells of on frames) | 0.0061 [0.0039, 0.0086] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0933 [0.0481, 0.1420] | 0.0022 [0.0009, 0.0037] |
| 2 [2,5) m | 0.0294 [0.0161, 0.0448] | 0.0010 [0.0000, 0.0025] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0164 [0.0105, 0.0227] |
| cell recall | 0.0084 [0.0054, 0.0117] |
| cell precision | 0.3387 [0.2222, 0.4640] |

## 2. Threshold sweep

| metric | tau=0.1 | tau=0.25 | tau=0.5 |
|---|---|---|---|
| cell_f1 | 0.0253 | 0.0164 | 0.0095 |
| cell_recall | 0.0132 | 0.0084 | 0.0048 |
| cell_precision | 0.2946 | 0.3387 | 0.4211 |
| frame_det_rate | 0.1162 | 0.0887 | 0.0550 |
| frame_recall_V | 0.2111 | 0.1611 | 0.1000 |
| frame_recall_E | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_H | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_V | 0.0189 | 0.0120 | 0.0069 |
| cell_recall_E | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_H | 0.0000 | 0.0000 | 0.0000 |
| band1_cell_recall | 0.1511 | 0.0933 | 0.0578 |
| band2_cell_recall | 0.0448 | 0.0294 | 0.0154 |
| band3_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band1_cell_fpr_off | 0.0042 | 0.0022 | 0.0010 |
| band2_cell_fpr_off | 0.0039 | 0.0010 | 0.0005 |
| band3_cell_fpr_off | 0.0002 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.0002 | 0.0000 | 0.0000 |
| frame_fa_off | 0.0539 | 0.0245 | 0.0123 |
| cell_fpr_off | 0.0021 | 0.0008 | 0.0004 |
| cell_fpr_on_neg | 0.0109 | 0.0061 | 0.0024 |
