# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/depth_s44/best.pt`
grid: **PROVISIONAL-GRID-V2S** (4 bands x 10 sectors = 40 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.31 (fitted on **val**, val cell-F1 0.6375) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 4998 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9333 [0.8934, 0.9671] | 0.7410 [0.6836, 0.7944] | 180 |
| E | 0.6000 [0.4545, 0.7436] | 0.5956 [0.4922, 0.6815] | 45 |
| H | 0.4688 [0.3696, 0.5684] | 0.5978 [0.4916, 0.6853] | 96 |
| **any tier (frame detection rate)** | 0.7339 [0.6861, 0.7812] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0221 [0.0096, 0.0370] |
| cell FPR (off frames) | 0.0048 [0.0006, 0.0101] |
| cell FPR (negative cells of on frames) | 0.1293 [0.1064, 0.1542] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.2133 [0.0708, 0.3664] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.6134 [0.5179, 0.7052] | 0.0044 [0.0000, 0.0100] |
| 3a [5,8) m | 0.7801 [0.7342, 0.8229] | 0.0066 [0.0015, 0.0132] |
| 3b [8,12) m | 0.7101 [0.6618, 0.7562] | 0.0081 [0.0007, 0.0173] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6946 [0.6575, 0.7292] |
| cell recall | 0.6963 [0.6519, 0.7372] |
| cell precision | 0.6930 [0.6428, 0.7405] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.31

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9667 [0.9375, 0.9894] | 0.7899 [0.7328, 0.8434] | 180 |
| E | 0.6000 [0.4545, 0.7436] | 0.6133 [0.5074, 0.7013] | 45 |
| H | 0.5000 [0.4017, 0.6000] | 0.6642 [0.5669, 0.7421] | 96 |
| **any tier (frame detection rate)** | 0.7706 [0.7249, 0.8160] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0515 [0.0309, 0.0735] |
| cell FPR (off frames) | 0.0064 [0.0015, 0.0126] |
| cell FPR (negative cells of on frames) | 0.1656 [0.1400, 0.1933] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.2533 [0.0928, 0.4266] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.6975 [0.6051, 0.7840] | 0.0059 [0.0000, 0.0133] |
| 3a [5,8) m | 0.8195 [0.7743, 0.8611] | 0.0088 [0.0022, 0.0174] |
| 3b [8,12) m | 0.7540 [0.7076, 0.7975] | 0.0110 [0.0037, 0.0202] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6955 [0.6590, 0.7289] |
| cell recall | 0.7443 [0.7010, 0.7845] |
| cell precision | 0.6526 [0.6050, 0.6980] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.6961 | 0.6946 | 0.6954 |
| cell_recall | 0.7485 | 0.6963 | 0.6393 |
| cell_precision | 0.6505 | 0.6930 | 0.7623 |
| frame_det_rate | 0.7798 | 0.7339 | 0.6697 |
| frame_recall_V | 0.9833 | 0.9333 | 0.8667 |
| frame_recall_E | 0.6000 | 0.6000 | 0.6000 |
| frame_recall_H | 0.5000 | 0.4688 | 0.3750 |
| cell_recall_V | 0.7933 | 0.7410 | 0.6810 |
| cell_recall_E | 0.6178 | 0.5956 | 0.5600 |
| cell_recall_H | 0.6716 | 0.5978 | 0.5351 |
| band1_cell_recall | 0.2800 | 0.2133 | 0.2133 |
| band2_cell_recall | 0.6975 | 0.6134 | 0.5546 |
| band3_cell_recall | 0.8214 | 0.7801 | 0.7237 |
| band4_cell_recall | 0.7588 | 0.7101 | 0.6480 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0059 | 0.0044 | 0.0000 |
| band3_cell_fpr_off | 0.0088 | 0.0066 | 0.0015 |
| band4_cell_fpr_off | 0.0125 | 0.0081 | 0.0044 |
| frame_fa_off | 0.0662 | 0.0221 | 0.0147 |
| cell_fpr_off | 0.0068 | 0.0048 | 0.0015 |
| cell_fpr_on_neg | 0.1677 | 0.1293 | 0.0859 |
