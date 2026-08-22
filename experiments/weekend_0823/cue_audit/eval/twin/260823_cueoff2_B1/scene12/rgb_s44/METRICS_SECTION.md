# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 24 | 6 | 0 | 18 | 1 | 168 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8333 [0.5000, 1.0000] | 0.2143 [0.1176, 0.2826] | 6 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.5000 [0.2632, 0.7333] | 0.1190 [0.0594, 0.1782] | 18 |
| **any tier (frame detection rate)** | 0.5833 [0.3810, 0.7826] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.1458 [0.1315, 0.1605] |
| cell FPR (negative cells of on frames) | 0.0000 [0.0000, 0.0000] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.3333 [0.2143, 0.4638] | 0.3667 [0.2706, 0.4571] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.2167 [0.1280, 0.3091] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1832 [0.1126, 0.2468] |
| cell recall | 0.1429 [0.0915, 0.1929] |
| cell precision | 0.2553 [0.1339, 0.4059] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8333 [0.5000, 1.0000] | 0.2143 [0.1176, 0.2826] | 6 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.5000 [0.2632, 0.7333] | 0.1190 [0.0594, 0.1782] | 18 |
| **any tier (frame detection rate)** | 0.5833 [0.3810, 0.7826] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.1458 [0.1315, 0.1605] |
| cell FPR (negative cells of on frames) | 0.0000 [0.0000, 0.0000] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.3333 [0.2143, 0.4638] | 0.3667 [0.2706, 0.4571] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.2167 [0.1280, 0.3091] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1832 [0.1126, 0.2468] |
| cell recall | 0.1429 [0.0915, 0.1929] |
| cell precision | 0.2553 [0.1339, 0.4059] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.2562 | 0.1832 | 0.1129 |
| cell_recall | 0.2143 | 0.1429 | 0.0833 |
| cell_precision | 0.3186 | 0.2553 | 0.1750 |
| frame_det_rate | 0.7083 | 0.5833 | 0.3333 |
| frame_recall_V | 1.0000 | 0.8333 | 0.6667 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.6111 | 0.5000 | 0.2222 |
| cell_recall_V | 0.3810 | 0.2143 | 0.1429 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.1587 | 0.1190 | 0.0635 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_recall | 0.4444 | 0.3333 | 0.1944 |
| band4_cell_recall | 0.0460 | 0.0000 | 0.0000 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.3833 | 0.3667 | 0.3500 |
| band4_cell_fpr_off | 0.2417 | 0.2167 | 0.2000 |
| frame_fa_off | 1.0000 | 1.0000 | 1.0000 |
| cell_fpr_off | 0.1562 | 0.1458 | 0.1375 |
| cell_fpr_on_neg | 0.0064 | 0.0000 | 0.0000 |
