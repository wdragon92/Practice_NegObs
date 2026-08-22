# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 24 | 24 | 0 | 0 | 1 | 168 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.3571 [0.3224, 0.3986] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.1333 [0.1187, 0.1483] |
| cell FPR (negative cells of on frames) | 0.0000 [0.0000, 0.0000] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.6667 [0.5333, 0.7937] | 0.3333 [0.2214, 0.4417] |
| 3b [8,12) m | 0.1379 [0.0506, 0.2286] | 0.2000 [0.1200, 0.2815] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4110 [0.3448, 0.4644] |
| cell recall | 0.3571 [0.3224, 0.3986] |
| cell precision | 0.4839 [0.3413, 0.6320] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.3571 [0.3224, 0.3986] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.1333 [0.1187, 0.1483] |
| cell FPR (negative cells of on frames) | 0.0000 [0.0000, 0.0000] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.6667 [0.5333, 0.7937] | 0.3333 [0.2214, 0.4417] |
| 3b [8,12) m | 0.1379 [0.0506, 0.2286] | 0.2000 [0.1200, 0.2815] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4110 [0.3448, 0.4644] |
| cell recall | 0.3571 [0.3224, 0.3986] |
| cell precision | 0.4839 [0.3413, 0.6320] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4040 | 0.4110 | 0.4014 |
| cell_recall | 0.3631 | 0.3571 | 0.3452 |
| cell_precision | 0.4552 | 0.4839 | 0.4793 |
| frame_det_rate | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_V | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | n/a | n/a | n/a |
| cell_recall_V | 0.3631 | 0.3571 | 0.3452 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | n/a | n/a | n/a |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_recall | 0.6806 | 0.6667 | 0.6389 |
| band4_cell_recall | 0.1379 | 0.1379 | 0.1379 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0083 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.3667 | 0.3333 | 0.3250 |
| band4_cell_fpr_off | 0.2250 | 0.2000 | 0.2000 |
| frame_fa_off | 1.0000 | 1.0000 | 1.0000 |
| cell_fpr_off | 0.1500 | 0.1333 | 0.1313 |
| cell_fpr_on_neg | 0.0032 | 0.0000 | 0.0000 |
