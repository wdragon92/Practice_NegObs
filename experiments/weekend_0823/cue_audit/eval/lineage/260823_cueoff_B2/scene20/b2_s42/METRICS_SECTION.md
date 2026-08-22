# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 18 | 9 | 0 | 9 | 1 | 78 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.6222 [0.4286, 0.8000] | 9 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 9 |
| **any tier (frame detection rate)** | 0.5000 [0.2667, 0.7333] | — | 18 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2083 [0.0500, 0.3810] |
| cell FPR (off frames) | 0.0250 [0.0065, 0.0474] |
| cell FPR (negative cells of on frames) | 0.1816 [0.0915, 0.2849] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.3590 [0.1774, 0.5395] | 0.1000 [0.0261, 0.1895] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2932 [0.1818, 0.3636] |
| cell recall | 0.3590 [0.1774, 0.5395] |
| cell precision | 0.2478 [0.1778, 0.2881] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.6222 [0.4286, 0.8000] | 9 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 9 |
| **any tier (frame detection rate)** | 0.5000 [0.2667, 0.7333] | — | 18 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2083 [0.0500, 0.3810] |
| cell FPR (off frames) | 0.0250 [0.0065, 0.0474] |
| cell FPR (negative cells of on frames) | 0.1816 [0.0915, 0.2849] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.3590 [0.1774, 0.5395] | 0.1000 [0.0261, 0.1895] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2932 [0.1818, 0.3636] |
| cell recall | 0.3590 [0.1774, 0.5395] |
| cell precision | 0.2478 [0.1778, 0.2881] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3128 | 0.2932 | 0.2619 |
| cell_recall | 0.4231 | 0.3590 | 0.2821 |
| cell_precision | 0.2481 | 0.2478 | 0.2444 |
| frame_det_rate | 0.6111 | 0.5000 | 0.3889 |
| frame_recall_V | 1.0000 | 1.0000 | 0.7778 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.2222 | 0.0000 | 0.0000 |
| cell_recall_V | 0.6667 | 0.6222 | 0.4889 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.0909 | 0.0000 | 0.0000 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | n/a | n/a | n/a |
| band4_cell_recall | 0.4231 | 0.3590 | 0.2821 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.1083 | 0.1000 | 0.0667 |
| frame_fa_off | 0.2500 | 0.2083 | 0.1667 |
| cell_fpr_off | 0.0271 | 0.0250 | 0.0167 |
| cell_fpr_on_neg | 0.2164 | 0.1816 | 0.1493 |
