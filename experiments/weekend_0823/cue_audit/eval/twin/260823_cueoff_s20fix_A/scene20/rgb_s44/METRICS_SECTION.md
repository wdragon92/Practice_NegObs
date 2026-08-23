# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 96 | 48 | 48 | 39 | 12 | 0 | 27 | 1 | 183 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.9667 [0.8909, 1.0000] | 12 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.7778 [0.6111, 0.9286] | 0.6748 [0.5185, 0.8158] | 27 |
| **any tier (frame detection rate)** | 0.8462 [0.7250, 0.9512] | — | 39 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0625 [0.0000, 0.1395] |
| cell FPR (off frames) | 0.0031 [0.0000, 0.0070] |
| cell FPR (negative cells of on frames) | 0.2329 [0.1804, 0.2889] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0042 [0.0000, 0.0138] |
| 3b [8,12) m | 0.7705 [0.6537, 0.8733] | 0.0083 [0.0000, 0.0213] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5551 [0.4927, 0.6119] |
| cell recall | 0.7705 [0.6537, 0.8733] |
| cell precision | 0.4338 [0.3771, 0.4920] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.9667 [0.8909, 1.0000] | 12 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.7778 [0.6111, 0.9286] | 0.6748 [0.5185, 0.8158] | 27 |
| **any tier (frame detection rate)** | 0.8462 [0.7250, 0.9512] | — | 39 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0625 [0.0000, 0.1395] |
| cell FPR (off frames) | 0.0031 [0.0000, 0.0070] |
| cell FPR (negative cells of on frames) | 0.2329 [0.1804, 0.2889] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0042 [0.0000, 0.0138] |
| 3b [8,12) m | 0.7705 [0.6537, 0.8733] | 0.0083 [0.0000, 0.0213] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5551 [0.4927, 0.6119] |
| cell recall | 0.7705 [0.6537, 0.8733] |
| cell precision | 0.4338 [0.3771, 0.4920] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5058 | 0.5551 | 0.5681 |
| cell_recall | 0.8361 | 0.7705 | 0.6612 |
| cell_precision | 0.3626 | 0.4338 | 0.4979 |
| frame_det_rate | 0.8718 | 0.8462 | 0.7949 |
| frame_recall_V | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.8148 | 0.7778 | 0.7037 |
| cell_recall_V | 1.0000 | 0.9667 | 0.8667 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.7561 | 0.6748 | 0.5610 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | n/a | n/a | n/a |
| band4_cell_recall | 0.8361 | 0.7705 | 0.6612 |
| band1_cell_fpr_off | 0.0125 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0208 | 0.0042 | 0.0000 |
| band4_cell_fpr_off | 0.0375 | 0.0083 | 0.0000 |
| frame_fa_off | 0.1250 | 0.0625 | 0.0000 |
| cell_fpr_off | 0.0177 | 0.0031 | 0.0000 |
| cell_fpr_on_neg | 0.3243 | 0.2329 | 0.1570 |
