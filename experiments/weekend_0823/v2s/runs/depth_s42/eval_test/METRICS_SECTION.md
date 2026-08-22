# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/depth_s42/best.pt`
grid: **PROVISIONAL-GRID-V2S** (4 bands x 10 sectors = 40 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.49 (fitted on **val**, val cell-F1 0.7024) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 4998 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8500 [0.7967, 0.8995] | 0.7196 [0.6576, 0.7772] | 180 |
| E | 0.6000 [0.4545, 0.7436] | 0.6978 [0.5830, 0.7917] | 45 |
| H | 0.4375 [0.3404, 0.5364] | 0.6642 [0.5563, 0.7506] | 96 |
| **any tier (frame detection rate)** | 0.6789 [0.6284, 0.7287] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (negative cells of on frames) | 0.1545 [0.1216, 0.1886] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.3067 [0.1589, 0.4631] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.4832 [0.3806, 0.5827] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.8327 [0.7857, 0.8752] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.7247 [0.6766, 0.7691] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6867 [0.6440, 0.7269] |
| cell recall | 0.7059 [0.6581, 0.7508] |
| cell precision | 0.6686 [0.6102, 0.7275] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.49

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8667 [0.8150, 0.9144] | 0.7238 [0.6624, 0.7815] | 180 |
| E | 0.6000 [0.4545, 0.7436] | 0.6978 [0.5830, 0.7917] | 45 |
| H | 0.4375 [0.3404, 0.5364] | 0.6753 [0.5686, 0.7607] | 96 |
| **any tier (frame detection rate)** | 0.6972 [0.6482, 0.7460] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (negative cells of on frames) | 0.1566 [0.1237, 0.1910] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.3067 [0.1589, 0.4631] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.4958 [0.3938, 0.5945] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.8327 [0.7857, 0.8752] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.7320 [0.6847, 0.7760] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6886 [0.6463, 0.7285] |
| cell recall | 0.7113 [0.6637, 0.7559] |
| cell precision | 0.6672 [0.6090, 0.7261] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.7014 | 0.6867 | 0.6349 |
| cell_recall | 0.7989 | 0.7059 | 0.5876 |
| cell_precision | 0.6252 | 0.6686 | 0.6904 |
| frame_det_rate | 0.8073 | 0.6789 | 0.6147 |
| frame_recall_V | 0.9667 | 0.8500 | 0.7500 |
| frame_recall_E | 0.6000 | 0.6000 | 0.6000 |
| frame_recall_H | 0.5938 | 0.4375 | 0.4062 |
| cell_recall_V | 0.8268 | 0.7196 | 0.5909 |
| cell_recall_E | 0.7244 | 0.6978 | 0.6000 |
| cell_recall_H | 0.7454 | 0.6642 | 0.5720 |
| band1_cell_recall | 0.4800 | 0.3067 | 0.2000 |
| band2_cell_recall | 0.6807 | 0.4832 | 0.3697 |
| band3_cell_recall | 0.8947 | 0.8327 | 0.7143 |
| band4_cell_recall | 0.8002 | 0.7247 | 0.6041 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0029 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.0353 | 0.0000 | 0.0000 |
| frame_fa_off | 0.1544 | 0.0000 | 0.0000 |
| cell_fpr_off | 0.0096 | 0.0000 | 0.0000 |
| cell_fpr_on_neg | 0.1977 | 0.1545 | 0.1163 |
