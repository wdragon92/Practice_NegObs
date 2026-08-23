# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.21 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 369 | 219 | 45 | 96 | 7 | 2856 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8630 [0.8145, 0.9065] | 0.6899 [0.6371, 0.7386] | 219 |
| E | 0.6000 [0.4545, 0.7436] | 0.5776 [0.4757, 0.6635] | 45 |
| H | 0.4688 [0.3704, 0.5699] | 0.5096 [0.4056, 0.6004] | 96 |
| **any tier (frame detection rate)** | 0.7154 [0.6686, 0.7614] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0074 [0.0000, 0.0167] |
| cell FPR (off frames) | 0.0033 [0.0000, 0.0075] |
| cell FPR (negative cells of on frames) | 0.1046 [0.0842, 0.1270] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.2308 [0.0750, 0.4000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.6111 [0.5098, 0.7041] | 0.0029 [0.0000, 0.0067] |
| 3a [5,8) m | 0.7475 [0.6989, 0.7929] | 0.0044 [0.0000, 0.0100] |
| 3b [8,12) m | 0.6245 [0.5778, 0.6688] | 0.0059 [0.0000, 0.0133] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6977 [0.6633, 0.7291] |
| cell recall | 0.6450 [0.6022, 0.6838] |
| cell precision | 0.7599 [0.7172, 0.8009] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.21

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9315 [0.8962, 0.9631] | 0.7656 [0.7145, 0.8109] | 219 |
| E | 0.6000 [0.4545, 0.7436] | 0.6379 [0.5268, 0.7311] | 45 |
| H | 0.5312 [0.4327, 0.6322] | 0.5669 [0.4699, 0.6501] | 96 |
| **any tier (frame detection rate)** | 0.7724 [0.7295, 0.8144] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0147 [0.0048, 0.0272] |
| cell FPR (off frames) | 0.0048 [0.0004, 0.0103] |
| cell FPR (negative cells of on frames) | 0.1476 [0.1233, 0.1736] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.2564 [0.0847, 0.4425] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.7222 [0.6311, 0.8084] | 0.0044 [0.0000, 0.0100] |
| 3a [5,8) m | 0.8215 [0.7771, 0.8625] | 0.0088 [0.0015, 0.0180] |
| 3b [8,12) m | 0.6857 [0.6428, 0.7277] | 0.0059 [0.0000, 0.0133] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.7142 [0.6811, 0.7446] |
| cell recall | 0.7153 [0.6742, 0.7522] |
| cell precision | 0.7131 [0.6719, 0.7542] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.7106 | 0.6977 | 0.6814 |
| cell_recall | 0.6912 | 0.6450 | 0.5987 |
| cell_precision | 0.7311 | 0.7599 | 0.7906 |
| frame_det_rate | 0.7317 | 0.7154 | 0.6667 |
| frame_recall_V | 0.8767 | 0.8630 | 0.8082 |
| frame_recall_E | 0.6000 | 0.6000 | 0.6000 |
| frame_recall_H | 0.5000 | 0.4688 | 0.4062 |
| cell_recall_V | 0.7344 | 0.6899 | 0.6454 |
| cell_recall_E | 0.6293 | 0.5776 | 0.5259 |
| cell_recall_H | 0.5605 | 0.5096 | 0.4650 |
| band1_cell_recall | 0.2564 | 0.2308 | 0.2051 |
| band2_cell_recall | 0.6825 | 0.6111 | 0.5794 |
| band3_cell_recall | 0.7946 | 0.7475 | 0.7037 |
| band4_cell_recall | 0.6653 | 0.6245 | 0.5714 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0029 | 0.0029 | 0.0029 |
| band3_cell_fpr_off | 0.0074 | 0.0044 | 0.0044 |
| band4_cell_fpr_off | 0.0059 | 0.0059 | 0.0059 |
| frame_fa_off | 0.0074 | 0.0074 | 0.0074 |
| cell_fpr_off | 0.0040 | 0.0033 | 0.0033 |
| cell_fpr_on_neg | 0.1307 | 0.1046 | 0.0803 |
