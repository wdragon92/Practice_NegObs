# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.21 (fitted on **val**, val cell-F1 0.6062) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 2691 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8833 [0.8333, 0.9278] | 0.7026 [0.6460, 0.7542] | 180 |
| E | 0.6000 [0.4545, 0.7436] | 0.5776 [0.4757, 0.6635] | 45 |
| H | 0.4688 [0.3704, 0.5699] | 0.5096 [0.4056, 0.6004] | 96 |
| **any tier (frame detection rate)** | 0.7064 [0.6562, 0.7557] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0074 [0.0000, 0.0167] |
| cell FPR (off frames) | 0.0033 [0.0000, 0.0075] |
| cell FPR (negative cells of on frames) | 0.1179 [0.0945, 0.1435] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.2308 [0.0750, 0.4000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.6111 [0.5098, 0.7041] | 0.0029 [0.0000, 0.0067] |
| 3a [5,8) m | 0.7483 [0.6986, 0.7947] | 0.0044 [0.0000, 0.0100] |
| 3b [8,12) m | 0.6357 [0.5864, 0.6828] | 0.0059 [0.0000, 0.0133] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6850 [0.6460, 0.7205] |
| cell recall | 0.6511 [0.6065, 0.6920] |
| cell precision | 0.7228 [0.6703, 0.7726] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.21

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9333 [0.8947, 0.9674] | 0.7701 [0.7152, 0.8189] | 180 |
| E | 0.6000 [0.4545, 0.7436] | 0.6379 [0.5268, 0.7311] | 45 |
| H | 0.5312 [0.4327, 0.6322] | 0.5669 [0.4699, 0.6501] | 96 |
| **any tier (frame detection rate)** | 0.7523 [0.7051, 0.7982] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0147 [0.0048, 0.0272] |
| cell FPR (off frames) | 0.0048 [0.0004, 0.0103] |
| cell FPR (negative cells of on frames) | 0.1646 [0.1370, 0.1939] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.2564 [0.0847, 0.4425] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.7222 [0.6311, 0.8084] | 0.0044 [0.0000, 0.0100] |
| 3a [5,8) m | 0.8172 [0.7721, 0.8591] | 0.0088 [0.0015, 0.0180] |
| 3b [8,12) m | 0.6878 [0.6414, 0.7330] | 0.0059 [0.0000, 0.0133] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6933 [0.6547, 0.7283] |
| cell recall | 0.7157 [0.6724, 0.7547] |
| cell precision | 0.6723 [0.6224, 0.7211] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.6956 | 0.6850 | 0.6724 |
| cell_recall | 0.6968 | 0.6511 | 0.6065 |
| cell_precision | 0.6944 | 0.7228 | 0.7545 |
| frame_det_rate | 0.7248 | 0.7064 | 0.6697 |
| frame_recall_V | 0.9000 | 0.8833 | 0.8500 |
| frame_recall_E | 0.6000 | 0.6000 | 0.6000 |
| frame_recall_H | 0.5000 | 0.4688 | 0.4062 |
| cell_recall_V | 0.7460 | 0.7026 | 0.6592 |
| cell_recall_E | 0.6293 | 0.5776 | 0.5259 |
| cell_recall_H | 0.5605 | 0.5096 | 0.4650 |
| band1_cell_recall | 0.2564 | 0.2308 | 0.2051 |
| band2_cell_recall | 0.6825 | 0.6111 | 0.5794 |
| band3_cell_recall | 0.7931 | 0.7483 | 0.7034 |
| band4_cell_recall | 0.6765 | 0.6357 | 0.5860 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0029 | 0.0029 | 0.0029 |
| band3_cell_fpr_off | 0.0074 | 0.0044 | 0.0044 |
| band4_cell_fpr_off | 0.0059 | 0.0059 | 0.0059 |
| frame_fa_off | 0.0074 | 0.0074 | 0.0074 |
| cell_fpr_off | 0.0040 | 0.0033 | 0.0033 |
| cell_fpr_on_neg | 0.1448 | 0.1179 | 0.0922 |
