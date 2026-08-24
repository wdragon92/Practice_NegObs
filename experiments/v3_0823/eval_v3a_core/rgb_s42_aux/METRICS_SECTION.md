# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/runs/v3a/rgb_s42_aux/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 369 | 219 | 45 | 96 | 7 | 2856 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.7215 [0.6611, 0.7800] | 0.5287 [0.4702, 0.5860] | 219 |
| E | 0.9111 [0.8163, 0.9796] | 0.5144 [0.4572, 0.5730] | 45 |
| H | 0.6250 [0.5269, 0.7204] | 0.7665 [0.6940, 0.8307] | 96 |
| **any tier (frame detection rate)** | 0.7100 [0.6621, 0.7556] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3873 [0.3399, 0.4359] |
| cell FPR (off frames) | 0.1158 [0.0963, 0.1363] |
| cell FPR (negative cells of on frames) | 0.2195 [0.1884, 0.2516] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0083 [0.0020, 0.0159] |
| 2 [2,5) m | 0.5529 [0.4503, 0.6513] | 0.1328 [0.1048, 0.1630] |
| 3a [5,8) m | 0.3782 [0.3163, 0.4398] | 0.0995 [0.0745, 0.1263] |
| 3b [8,12) m | 0.7286 [0.6865, 0.7690] | 0.2225 [0.1881, 0.2575] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4913 [0.4534, 0.5269] |
| cell recall | 0.5662 [0.5218, 0.6103] |
| cell precision | 0.4340 [0.3909, 0.4763] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.7215 [0.6611, 0.7800] | 0.5287 [0.4702, 0.5860] | 219 |
| E | 0.9111 [0.8163, 0.9796] | 0.5144 [0.4572, 0.5730] | 45 |
| H | 0.6250 [0.5269, 0.7204] | 0.7665 [0.6940, 0.8307] | 96 |
| **any tier (frame detection rate)** | 0.7100 [0.6621, 0.7556] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3873 [0.3399, 0.4359] |
| cell FPR (off frames) | 0.1158 [0.0963, 0.1363] |
| cell FPR (negative cells of on frames) | 0.2195 [0.1884, 0.2516] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0083 [0.0020, 0.0159] |
| 2 [2,5) m | 0.5529 [0.4503, 0.6513] | 0.1328 [0.1048, 0.1630] |
| 3a [5,8) m | 0.3782 [0.3163, 0.4398] | 0.0995 [0.0745, 0.1263] |
| 3b [8,12) m | 0.7286 [0.6865, 0.7690] | 0.2225 [0.1881, 0.2575] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4913 [0.4534, 0.5269] |
| cell recall | 0.5662 [0.5218, 0.6103] |
| cell precision | 0.4340 [0.3909, 0.4763] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4939 | 0.4913 | 0.4808 |
| cell_recall | 0.6572 | 0.5662 | 0.4835 |
| cell_precision | 0.3956 | 0.4340 | 0.4782 |
| frame_det_rate | 0.8455 | 0.7100 | 0.6396 |
| frame_recall_V | 0.8767 | 0.7215 | 0.6256 |
| frame_recall_E | 1.0000 | 0.9111 | 0.8000 |
| frame_recall_H | 0.7396 | 0.6250 | 0.6250 |
| cell_recall_V | 0.6311 | 0.5287 | 0.4397 |
| cell_recall_E | 0.5977 | 0.5144 | 0.4109 |
| cell_recall_H | 0.8132 | 0.7665 | 0.7261 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.6058 | 0.5529 | 0.4709 |
| band3_cell_recall | 0.4680 | 0.3782 | 0.3030 |
| band4_cell_recall | 0.8374 | 0.7286 | 0.6347 |
| band1_cell_fpr_off | 0.0186 | 0.0083 | 0.0025 |
| band2_cell_fpr_off | 0.1961 | 0.1328 | 0.0779 |
| band3_cell_fpr_off | 0.1559 | 0.0995 | 0.0642 |
| band4_cell_fpr_off | 0.3324 | 0.2225 | 0.1407 |
| frame_fa_off | 0.5123 | 0.3873 | 0.2500 |
| cell_fpr_off | 0.1757 | 0.1158 | 0.0713 |
| cell_fpr_on_neg | 0.2704 | 0.2195 | 0.1744 |
