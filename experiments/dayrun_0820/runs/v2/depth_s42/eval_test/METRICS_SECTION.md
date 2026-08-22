# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.36 (fitted on **val**, val cell-F1 0.6667) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 2691 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9667 [0.9378, 0.9893] | 0.7379 [0.6928, 0.7800] | 180 |
| E | 0.6000 [0.4545, 0.7436] | 0.5431 [0.4309, 0.6444] | 45 |
| H | 0.4062 [0.3107, 0.5053] | 0.5796 [0.4717, 0.6712] | 96 |
| **any tier (frame detection rate)** | 0.7339 [0.6854, 0.7812] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0515 [0.0312, 0.0741] |
| cell FPR (off frames) | 0.0044 [0.0024, 0.0067] |
| cell FPR (negative cells of on frames) | 0.1196 [0.0953, 0.1451] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1026 [0.0000, 0.2222] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.5794 [0.4813, 0.6757] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.7379 [0.6819, 0.7905] | 0.0059 [0.0024, 0.0102] |
| 3b [8,12) m | 0.7285 [0.6842, 0.7709] | 0.0118 [0.0061, 0.0183] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.7046 [0.6699, 0.7366] |
| cell recall | 0.6834 [0.6455, 0.7198] |
| cell precision | 0.7272 [0.6771, 0.7753] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.36

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9833 [0.9617, 1.0000] | 0.7765 [0.7349, 0.8164] | 180 |
| E | 0.6000 [0.4545, 0.7436] | 0.5603 [0.4502, 0.6571] | 45 |
| H | 0.4375 [0.3404, 0.5364] | 0.6051 [0.4979, 0.6944] | 96 |
| **any tier (frame detection rate)** | 0.7523 [0.7052, 0.7989] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1250 [0.0943, 0.1579] |
| cell FPR (off frames) | 0.0107 [0.0074, 0.0143] |
| cell FPR (negative cells of on frames) | 0.1382 [0.1126, 0.1649] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1026 [0.0000, 0.2222] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.6349 [0.5358, 0.7290] | 0.0015 [0.0000, 0.0033] |
| 3a [5,8) m | 0.7724 [0.7191, 0.8216] | 0.0118 [0.0058, 0.0187] |
| 3b [8,12) m | 0.7579 [0.7150, 0.7987] | 0.0294 [0.0211, 0.0383] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.7062 [0.6720, 0.7376] |
| cell recall | 0.7168 [0.6809, 0.7512] |
| cell precision | 0.6959 [0.6470, 0.7429] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.7059 | 0.7046 | 0.6853 |
| cell_recall | 0.7358 | 0.6834 | 0.6143 |
| cell_precision | 0.6783 | 0.7272 | 0.7750 |
| frame_det_rate | 0.7615 | 0.7339 | 0.6881 |
| frame_recall_V | 0.9833 | 0.9667 | 0.8833 |
| frame_recall_E | 0.6000 | 0.6000 | 0.6000 |
| frame_recall_H | 0.4688 | 0.4062 | 0.4062 |
| cell_recall_V | 0.8006 | 0.7379 | 0.6479 |
| cell_recall_E | 0.5603 | 0.5431 | 0.5259 |
| cell_recall_H | 0.6178 | 0.5796 | 0.5541 |
| band1_cell_recall | 0.1538 | 0.1026 | 0.0513 |
| band2_cell_recall | 0.6587 | 0.5794 | 0.4444 |
| band3_cell_recall | 0.7828 | 0.7379 | 0.6724 |
| band4_cell_recall | 0.7783 | 0.7285 | 0.6742 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0044 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0162 | 0.0059 | 0.0044 |
| band4_cell_fpr_off | 0.0368 | 0.0118 | 0.0059 |
| frame_fa_off | 0.1324 | 0.0515 | 0.0221 |
| cell_fpr_off | 0.0143 | 0.0044 | 0.0026 |
| cell_fpr_on_neg | 0.1503 | 0.1196 | 0.0839 |
