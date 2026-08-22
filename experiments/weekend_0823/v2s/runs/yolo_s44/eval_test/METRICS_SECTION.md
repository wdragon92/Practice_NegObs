# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/yolo_s44/cells_test/per_frame.csv`
grid: **PROVISIONAL-GRID-V2S** (4 bands x 10 sectors = 40 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.25 · tau_star = 0.25 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 4998 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.25

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.1722 [0.1190, 0.2303] | 0.0100 [0.0070, 0.0132] | 180 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 96 |
| **any tier (frame detection rate)** | 0.0948 [0.0642, 0.1272] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0417 [0.0231, 0.0618] |
| cell FPR (off frames) | 0.0012 [0.0007, 0.0019] |
| cell FPR (negative cells of on frames) | 0.0026 [0.0017, 0.0037] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0533 [0.0273, 0.0813] | 0.0037 [0.0017, 0.0060] |
| 2 [2,5) m | 0.0322 [0.0202, 0.0455] | 0.0012 [0.0002, 0.0024] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0138 [0.0094, 0.0183] |
| cell recall | 0.0070 [0.0048, 0.0093] |
| cell precision | 0.4118 [0.3000, 0.5250] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.25

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.1722 [0.1190, 0.2303] | 0.0100 [0.0070, 0.0132] | 180 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 96 |
| **any tier (frame detection rate)** | 0.0948 [0.0642, 0.1272] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0417 [0.0231, 0.0618] |
| cell FPR (off frames) | 0.0012 [0.0007, 0.0019] |
| cell FPR (negative cells of on frames) | 0.0026 [0.0017, 0.0037] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0533 [0.0273, 0.0813] | 0.0037 [0.0017, 0.0060] |
| 2 [2,5) m | 0.0322 [0.0202, 0.0455] | 0.0012 [0.0002, 0.0024] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0138 [0.0094, 0.0183] |
| cell recall | 0.0070 [0.0048, 0.0093] |
| cell precision | 0.4118 [0.3000, 0.5250] |

## 2. Threshold sweep

| metric | tau=0.1 | tau=0.25 | tau=0.5 |
|---|---|---|---|
| cell_f1 | 0.0216 | 0.0138 | 0.0095 |
| cell_recall | 0.0112 | 0.0070 | 0.0048 |
| cell_precision | 0.3094 | 0.4118 | 0.5217 |
| frame_det_rate | 0.1101 | 0.0948 | 0.0673 |
| frame_recall_V | 0.1944 | 0.1722 | 0.1222 |
| frame_recall_E | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_H | 0.0104 | 0.0000 | 0.0000 |
| cell_recall_V | 0.0152 | 0.0100 | 0.0069 |
| cell_recall_E | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_H | 0.0037 | 0.0000 | 0.0000 |
| band1_cell_recall | 0.0711 | 0.0533 | 0.0222 |
| band2_cell_recall | 0.0518 | 0.0322 | 0.0266 |
| band3_cell_recall | 0.0019 | 0.0000 | 0.0000 |
| band4_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band1_cell_fpr_off | 0.0056 | 0.0037 | 0.0020 |
| band2_cell_fpr_off | 0.0039 | 0.0012 | 0.0005 |
| band3_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.0002 | 0.0000 | 0.0000 |
| frame_fa_off | 0.0662 | 0.0417 | 0.0221 |
| cell_fpr_off | 0.0025 | 0.0012 | 0.0006 |
| cell_fpr_on_neg | 0.0075 | 0.0026 | 0.0011 |
