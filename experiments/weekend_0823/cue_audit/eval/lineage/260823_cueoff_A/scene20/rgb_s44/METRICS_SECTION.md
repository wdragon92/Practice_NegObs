# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 15 | 9 | 0 | 6 | 1 | 72 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.9111 [0.8000, 1.0000] | 9 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 1.0000 [1.0000, 1.0000] | 0.9259 [0.7778, 1.0000] | 6 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 15 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0833 [0.0000, 0.2105] |
| cell FPR (off frames) | 0.0042 [0.0000, 0.0105] |
| cell FPR (negative cells of on frames) | 0.2279 [0.1638, 0.2925] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.9167 [0.8333, 0.9857] | 0.0167 [0.0000, 0.0421] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5665 [0.4671, 0.6473] |
| cell recall | 0.9167 [0.8333, 0.9857] |
| cell precision | 0.4099 [0.3155, 0.4969] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.9111 [0.8000, 1.0000] | 9 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 1.0000 [1.0000, 1.0000] | 0.9259 [0.7778, 1.0000] | 6 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 15 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0833 [0.0000, 0.2105] |
| cell FPR (off frames) | 0.0042 [0.0000, 0.0105] |
| cell FPR (negative cells of on frames) | 0.2279 [0.1638, 0.2925] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.9167 [0.8333, 0.9857] | 0.0167 [0.0000, 0.0421] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5665 [0.4671, 0.6473] |
| cell recall | 0.9167 [0.8333, 0.9857] |
| cell precision | 0.4099 [0.3155, 0.4969] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5393 | 0.5665 | 0.5700 |
| cell_recall | 1.0000 | 0.9167 | 0.7917 |
| cell_precision | 0.3692 | 0.4099 | 0.4453 |
| frame_det_rate | 1.0000 | 1.0000 | 0.9333 |
| frame_recall_V | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 1.0000 | 1.0000 | 0.8333 |
| cell_recall_V | 1.0000 | 0.9111 | 0.8444 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 1.0000 | 0.9259 | 0.7037 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | n/a | n/a | n/a |
| band4_cell_recall | 1.0000 | 0.9167 | 0.7917 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.0417 | 0.0167 | 0.0083 |
| frame_fa_off | 0.1250 | 0.0833 | 0.0417 |
| cell_fpr_off | 0.0104 | 0.0042 | 0.0021 |
| cell_fpr_on_neg | 0.2892 | 0.2279 | 0.1716 |
