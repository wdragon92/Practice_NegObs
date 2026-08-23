# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.36 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 369 | 219 | 45 | 96 | 7 | 2856 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9452 [0.9132, 0.9733] | 0.7493 [0.7070, 0.7890] | 219 |
| E | 0.6000 [0.4545, 0.7436] | 0.5431 [0.4309, 0.6444] | 45 |
| H | 0.4062 [0.3107, 0.5053] | 0.5796 [0.4717, 0.6712] | 96 |
| **any tier (frame detection rate)** | 0.7480 [0.7025, 0.7918] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0515 [0.0312, 0.0741] |
| cell FPR (off frames) | 0.0044 [0.0024, 0.0067] |
| cell FPR (negative cells of on frames) | 0.0962 [0.0773, 0.1162] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1026 [0.0000, 0.2222] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.5794 [0.4813, 0.6757] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.7407 [0.6859, 0.7921] | 0.0059 [0.0024, 0.0102] |
| 3b [8,12) m | 0.7429 [0.7023, 0.7821] | 0.0118 [0.0061, 0.0183] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.7365 [0.7086, 0.7622] |
| cell recall | 0.6943 [0.6589, 0.7290] |
| cell precision | 0.7841 [0.7471, 0.8194] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.36

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9589 [0.9302, 0.9828] | 0.7864 [0.7468, 0.8238] | 219 |
| E | 0.6000 [0.4545, 0.7436] | 0.5603 [0.4502, 0.6571] | 45 |
| H | 0.4375 [0.3404, 0.5364] | 0.6051 [0.4979, 0.6944] | 96 |
| **any tier (frame detection rate)** | 0.7642 [0.7200, 0.8077] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1250 [0.0943, 0.1579] |
| cell FPR (off frames) | 0.0107 [0.0074, 0.0143] |
| cell FPR (negative cells of on frames) | 0.1148 [0.0943, 0.1362] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1026 [0.0000, 0.2222] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.6349 [0.5358, 0.7290] | 0.0015 [0.0000, 0.0033] |
| 3a [5,8) m | 0.7778 [0.7260, 0.8260] | 0.0118 [0.0058, 0.0187] |
| 3b [8,12) m | 0.7694 [0.7300, 0.8069] | 0.0294 [0.0211, 0.0383] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.7377 [0.7111, 0.7623] |
| cell recall | 0.7269 [0.6926, 0.7593] |
| cell precision | 0.7489 [0.7123, 0.7846] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.7366 | 0.7365 | 0.7180 |
| cell_recall | 0.7447 | 0.6943 | 0.6271 |
| cell_precision | 0.7287 | 0.7841 | 0.8397 |
| frame_det_rate | 0.7724 | 0.7480 | 0.7073 |
| frame_recall_V | 0.9589 | 0.9452 | 0.8767 |
| frame_recall_E | 0.6000 | 0.6000 | 0.6000 |
| frame_recall_H | 0.4688 | 0.4062 | 0.4062 |
| cell_recall_V | 0.8086 | 0.7493 | 0.6632 |
| cell_recall_E | 0.5603 | 0.5431 | 0.5259 |
| cell_recall_H | 0.6178 | 0.5796 | 0.5541 |
| band1_cell_recall | 0.1538 | 0.1026 | 0.0513 |
| band2_cell_recall | 0.6587 | 0.5794 | 0.4444 |
| band3_cell_recall | 0.7879 | 0.7407 | 0.6734 |
| band4_cell_recall | 0.7878 | 0.7429 | 0.6918 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0044 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0162 | 0.0059 | 0.0044 |
| band4_cell_fpr_off | 0.0368 | 0.0118 | 0.0059 |
| frame_fa_off | 0.1324 | 0.0515 | 0.0221 |
| cell_fpr_off | 0.0143 | 0.0044 | 0.0026 |
| cell_fpr_on_neg | 0.1273 | 0.0962 | 0.0605 |
