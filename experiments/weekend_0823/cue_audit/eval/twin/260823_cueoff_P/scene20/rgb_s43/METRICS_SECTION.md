# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 15 | 9 | 0 | 6 | 1 | 72 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.8667 [0.8000, 0.9333] | 9 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 1.0000 [1.0000, 1.0000] | 0.8889 [0.8000, 1.0000] | 6 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 15 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.3333 [0.2516, 0.4263] |
| cell FPR (negative cells of on frames) | 0.2721 [0.2175, 0.3314] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.2167 [0.0720, 0.3905] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.2917 [0.1429, 0.4571] |
| 3b [8,12) m | 0.8750 [0.8276, 0.9277] | 0.8250 [0.7440, 0.9000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3103 [0.2043, 0.4053] |
| cell recall | 0.8750 [0.8276, 0.9277] |
| cell precision | 0.1886 [0.1154, 0.2636] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.8667 [0.8000, 0.9333] | 9 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 1.0000 [1.0000, 1.0000] | 0.8889 [0.8000, 1.0000] | 6 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 15 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.3333 [0.2516, 0.4263] |
| cell FPR (negative cells of on frames) | 0.2721 [0.2175, 0.3314] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.2167 [0.0720, 0.3905] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.2917 [0.1429, 0.4571] |
| 3b [8,12) m | 0.8750 [0.8276, 0.9277] | 0.8250 [0.7440, 0.9000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3103 [0.2043, 0.4053] |
| cell recall | 0.8750 [0.8276, 0.9277] |
| cell precision | 0.1886 [0.1154, 0.2636] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.2845 | 0.3103 | 0.3828 |
| cell_recall | 0.9444 | 0.8750 | 0.8056 |
| cell_precision | 0.1675 | 0.1886 | 0.2511 |
| frame_det_rate | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_V | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 1.0000 | 1.0000 | 1.0000 |
| cell_recall_V | 0.9556 | 0.8667 | 0.8000 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.9259 | 0.8889 | 0.8148 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | n/a | n/a | n/a |
| band4_cell_recall | 0.9444 | 0.8750 | 0.8056 |
| band1_cell_fpr_off | 0.0167 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.2833 | 0.2167 | 0.0833 |
| band3_cell_fpr_off | 0.4167 | 0.2917 | 0.1667 |
| band4_cell_fpr_off | 0.9333 | 0.8250 | 0.6167 |
| frame_fa_off | 1.0000 | 1.0000 | 0.9583 |
| cell_fpr_off | 0.4125 | 0.3333 | 0.2167 |
| cell_fpr_on_neg | 0.3431 | 0.2721 | 0.1691 |
