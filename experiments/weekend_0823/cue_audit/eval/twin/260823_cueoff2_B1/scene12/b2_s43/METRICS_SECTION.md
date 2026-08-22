# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 24 | 6 | 0 | 18 | 1 | 168 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.5000 [0.0000, 1.0000] | 0.1190 [0.0000, 0.3143] | 6 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.2778 [0.0769, 0.5000] | 0.0873 [0.0247, 0.1519] | 18 |
| **any tier (frame detection rate)** | 0.3333 [0.1500, 0.5263] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.8750 [0.7273, 1.0000] |
| cell FPR (off frames) | 0.1313 [0.1056, 0.1533] |
| cell FPR (negative cells of on frames) | 0.0160 [0.0038, 0.0298] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.2222 [0.0964, 0.3662] | 0.3750 [0.2538, 0.4909] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.1500 [0.0632, 0.2480] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1270 [0.0549, 0.1961] |
| cell recall | 0.0952 [0.0408, 0.1553] |
| cell precision | 0.1905 [0.0769, 0.3218] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.5000 [0.0000, 1.0000] | 0.1190 [0.0000, 0.3143] | 6 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.2778 [0.0769, 0.5000] | 0.0873 [0.0247, 0.1519] | 18 |
| **any tier (frame detection rate)** | 0.3333 [0.1500, 0.5263] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.8750 [0.7273, 1.0000] |
| cell FPR (off frames) | 0.1313 [0.1056, 0.1533] |
| cell FPR (negative cells of on frames) | 0.0160 [0.0038, 0.0298] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.2222 [0.0964, 0.3662] | 0.3750 [0.2538, 0.4909] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.1500 [0.0632, 0.2480] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1270 [0.0549, 0.1961] |
| cell recall | 0.0952 [0.0408, 0.1553] |
| cell precision | 0.1905 [0.0769, 0.3218] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.2614 | 0.1270 | 0.0000 |
| cell_recall | 0.2738 | 0.0952 | 0.0000 |
| cell_precision | 0.2500 | 0.1905 | 0.0000 |
| frame_det_rate | 0.6250 | 0.3333 | 0.0000 |
| frame_recall_V | 0.6667 | 0.5000 | 0.0000 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.6111 | 0.2778 | 0.0000 |
| cell_recall_V | 0.2381 | 0.1190 | 0.0000 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.2857 | 0.0873 | 0.0000 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_recall | 0.4167 | 0.2222 | 0.0000 |
| band4_cell_recall | 0.1839 | 0.0000 | 0.0000 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.4333 | 0.3750 | 0.2667 |
| band4_cell_fpr_off | 0.5750 | 0.1500 | 0.0417 |
| frame_fa_off | 1.0000 | 0.8750 | 0.7500 |
| cell_fpr_off | 0.2521 | 0.1313 | 0.0771 |
| cell_fpr_on_neg | 0.0545 | 0.0160 | 0.0000 |
