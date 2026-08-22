# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/b2_s42/best.pt`
grid: **PROVISIONAL-GRID-V2S** (4 bands x 10 sectors = 40 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.53 (fitted on **val**, val cell-F1 0.4913) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 4998 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6778 [0.6079, 0.7458] | 0.2479 [0.2082, 0.2892] | 180 |
| E | 0.0222 [0.0000, 0.0769] | 0.0030 [0.0000, 0.0105] | 45 |
| H | 0.1979 [0.1204, 0.2821] | 0.0504 [0.0279, 0.0764] | 96 |
| **any tier (frame detection rate)** | 0.4373 [0.3820, 0.4922] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0907 [0.0638, 0.1201] |
| cell FPR (off frames) | 0.0105 [0.0060, 0.0156] |
| cell FPR (negative cells of on frames) | 0.0353 [0.0267, 0.0445] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0364 [0.0057, 0.0770] | 0.0002 [0.0000, 0.0008] |
| 3a [5,8) m | 0.1253 [0.0911, 0.1631] | 0.0066 [0.0007, 0.0142] |
| 3b [8,12) m | 0.2785 [0.2366, 0.3212] | 0.0350 [0.0215, 0.0499] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2814 [0.2419, 0.3207] |
| cell recall | 0.1825 [0.1533, 0.2133] |
| cell precision | 0.6150 [0.5427, 0.6841] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.53

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6722 [0.6023, 0.7412] | 0.2390 [0.2004, 0.2798] | 180 |
| E | 0.0222 [0.0000, 0.0769] | 0.0030 [0.0000, 0.0105] | 45 |
| H | 0.1875 [0.1121, 0.2700] | 0.0443 [0.0232, 0.0694] | 96 |
| **any tier (frame detection rate)** | 0.4312 [0.3757, 0.4856] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0809 [0.0551, 0.1086] |
| cell FPR (off frames) | 0.0099 [0.0055, 0.0150] |
| cell FPR (negative cells of on frames) | 0.0339 [0.0255, 0.0428] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0308 [0.0028, 0.0700] | 0.0002 [0.0000, 0.0008] |
| 3a [5,8) m | 0.1172 [0.0840, 0.1539] | 0.0066 [0.0007, 0.0142] |
| 3b [8,12) m | 0.2708 [0.2294, 0.3129] | 0.0328 [0.0195, 0.0475] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2729 [0.2337, 0.3121] |
| cell recall | 0.1753 [0.1468, 0.2050] |
| cell precision | 0.6160 [0.5434, 0.6866] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3334 | 0.2814 | 0.2296 |
| cell_recall | 0.2363 | 0.1825 | 0.1399 |
| cell_precision | 0.5659 | 0.6150 | 0.6413 |
| frame_det_rate | 0.5352 | 0.4373 | 0.3761 |
| frame_recall_V | 0.7333 | 0.6778 | 0.6278 |
| frame_recall_E | 0.0444 | 0.0222 | 0.0222 |
| frame_recall_H | 0.3854 | 0.1979 | 0.0833 |
| cell_recall_V | 0.3079 | 0.2479 | 0.1947 |
| cell_recall_E | 0.0059 | 0.0030 | 0.0015 |
| cell_recall_H | 0.1169 | 0.0504 | 0.0197 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.0574 | 0.0364 | 0.0182 |
| band3_cell_recall | 0.1861 | 0.1253 | 0.0840 |
| band4_cell_recall | 0.3423 | 0.2785 | 0.2241 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0020 | 0.0002 | 0.0000 |
| band3_cell_fpr_off | 0.0088 | 0.0066 | 0.0051 |
| band4_cell_fpr_off | 0.0630 | 0.0350 | 0.0225 |
| frame_fa_off | 0.1642 | 0.0907 | 0.0539 |
| cell_fpr_off | 0.0184 | 0.0105 | 0.0069 |
| cell_fpr_on_neg | 0.0534 | 0.0353 | 0.0246 |
