# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 72 | 48 | 24 | 39 | 12 | 0 | 27 | 1 | 183 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.9667 [0.9167, 1.0000] | 12 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 1.0000 [1.0000, 1.0000] | 0.9187 [0.8768, 0.9588] | 27 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 39 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.9583 [0.8571, 1.0000] |
| cell FPR (off frames) | 0.1979 [0.1588, 0.2370] |
| cell FPR (negative cells of on frames) | 0.2085 [0.1509, 0.2684] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0083 [0.0000, 0.0286] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0833 [0.0250, 0.1565] |
| 3b [8,12) m | 0.9344 [0.9016, 0.9645] | 0.7000 [0.5793, 0.8100] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5597 [0.4861, 0.6252] |
| cell recall | 0.9344 [0.9016, 0.9645] |
| cell precision | 0.3995 [0.3283, 0.4714] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.9667 [0.9167, 1.0000] | 12 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 1.0000 [1.0000, 1.0000] | 0.9187 [0.8768, 0.9588] | 27 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 39 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.9583 [0.8571, 1.0000] |
| cell FPR (off frames) | 0.1979 [0.1588, 0.2370] |
| cell FPR (negative cells of on frames) | 0.2085 [0.1509, 0.2684] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0083 [0.0000, 0.0286] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0833 [0.0250, 0.1565] |
| 3b [8,12) m | 0.9344 [0.9016, 0.9645] | 0.7000 [0.5793, 0.8100] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5597 [0.4861, 0.6252] |
| cell recall | 0.9344 [0.9016, 0.9645] |
| cell precision | 0.3995 [0.3283, 0.4714] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4993 | 0.5597 | 0.5885 |
| cell_recall | 0.9617 | 0.9344 | 0.8634 |
| cell_precision | 0.3372 | 0.3995 | 0.4463 |
| frame_det_rate | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_V | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 1.0000 | 1.0000 | 1.0000 |
| cell_recall_V | 1.0000 | 0.9667 | 0.8500 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.9431 | 0.9187 | 0.8699 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | n/a | n/a | n/a |
| band4_cell_recall | 0.9617 | 0.9344 | 0.8634 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0500 | 0.0083 | 0.0000 |
| band3_cell_fpr_off | 0.1833 | 0.0833 | 0.0167 |
| band4_cell_fpr_off | 0.8833 | 0.7000 | 0.4917 |
| frame_fa_off | 1.0000 | 0.9583 | 0.7917 |
| cell_fpr_off | 0.2792 | 0.1979 | 0.1271 |
| cell_fpr_on_neg | 0.2728 | 0.2085 | 0.1737 |
