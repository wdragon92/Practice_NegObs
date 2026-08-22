# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 24 | 6 | 0 | 18 | 1 | 168 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6667 [0.2500, 1.0000] | 0.1667 [0.0435, 0.3333] | 6 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.1111 [0.0000, 0.2727] | 0.0238 [0.0000, 0.0596] | 18 |
| **any tier (frame detection rate)** | 0.2500 [0.0870, 0.4333] | — | 24 |

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
| 3a [5,8) m | 0.1389 [0.0455, 0.2500] | 0.3333 [0.2214, 0.4417] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.2000 [0.1200, 0.2815] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0826 [0.0261, 0.1447] |
| cell recall | 0.0595 [0.0190, 0.1084] |
| cell precision | 0.1351 [0.0411, 0.2623] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6667 [0.2500, 1.0000] | 0.1667 [0.0435, 0.3333] | 6 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.1111 [0.0000, 0.2727] | 0.0238 [0.0000, 0.0596] | 18 |
| **any tier (frame detection rate)** | 0.2500 [0.0870, 0.4333] | — | 24 |

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
| 3a [5,8) m | 0.1389 [0.0455, 0.2500] | 0.3333 [0.2214, 0.4417] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.2000 [0.1200, 0.2815] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0826 [0.0261, 0.1447] |
| cell recall | 0.0595 [0.0190, 0.1084] |
| cell precision | 0.1351 [0.0411, 0.2623] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.1176 | 0.0826 | 0.0506 |
| cell_recall | 0.0893 | 0.0595 | 0.0357 |
| cell_precision | 0.1724 | 0.1351 | 0.0870 |
| frame_det_rate | 0.2917 | 0.2500 | 0.2083 |
| frame_recall_V | 0.6667 | 0.6667 | 0.5000 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.1667 | 0.1111 | 0.1111 |
| cell_recall_V | 0.2143 | 0.1667 | 0.0952 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.0476 | 0.0238 | 0.0159 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_recall | 0.1944 | 0.1389 | 0.0833 |
| band4_cell_recall | 0.0115 | 0.0000 | 0.0000 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0083 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.3667 | 0.3333 | 0.3250 |
| band4_cell_fpr_off | 0.2250 | 0.2000 | 0.2000 |
| frame_fa_off | 1.0000 | 1.0000 | 1.0000 |
| cell_fpr_off | 0.1500 | 0.1333 | 0.1313 |
| cell_fpr_on_neg | 0.0000 | 0.0000 | 0.0000 |
