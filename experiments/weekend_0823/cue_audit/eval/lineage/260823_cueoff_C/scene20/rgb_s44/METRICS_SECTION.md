# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 0 | 0 | 0 | 0 | 1 | 0 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | n/a [n/a, n/a] | — | 0 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0833 [0.0000, 0.2105] |
| cell FPR (off frames) | 0.0042 [0.0000, 0.0105] |
| cell FPR (negative cells of on frames) | 0.0000 [0.0000, 0.0000] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | n/a [n/a, n/a] | 0.0167 [0.0000, 0.0421] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0000 [0.0000, 0.0000] |
| cell recall | n/a [n/a, n/a] |
| cell precision | 0.0000 [0.0000, 0.0000] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | n/a [n/a, n/a] | — | 0 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0833 [0.0000, 0.2105] |
| cell FPR (off frames) | 0.0042 [0.0000, 0.0105] |
| cell FPR (negative cells of on frames) | 0.0000 [0.0000, 0.0000] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | n/a [n/a, n/a] | 0.0167 [0.0000, 0.0421] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0000 [0.0000, 0.0000] |
| cell recall | n/a [n/a, n/a] |
| cell precision | 0.0000 [0.0000, 0.0000] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.0000 | 0.0000 | 0.0000 |
| cell_recall | n/a | n/a | n/a |
| cell_precision | 0.0000 | 0.0000 | 0.0000 |
| frame_det_rate | n/a | n/a | n/a |
| frame_recall_V | n/a | n/a | n/a |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | n/a | n/a | n/a |
| cell_recall_V | n/a | n/a | n/a |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | n/a | n/a | n/a |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | n/a | n/a | n/a |
| band4_cell_recall | n/a | n/a | n/a |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.0417 | 0.0167 | 0.0083 |
| frame_fa_off | 0.1250 | 0.0833 | 0.0417 |
| cell_fpr_off | 0.0104 | 0.0042 | 0.0021 |
| cell_fpr_on_neg | 0.0021 | 0.0000 | 0.0000 |
