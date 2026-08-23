# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.71 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 369 | 219 | 45 | 96 | 7 | 2856 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9543 [0.9254, 0.9805] | 0.4807 [0.4398, 0.5223] | 219 |
| E | 0.9111 [0.8182, 0.9804] | 0.5115 [0.4260, 0.6026] | 45 |
| H | 0.8750 [0.8061, 0.9368] | 0.5287 [0.4748, 0.5885] | 96 |
| **any tier (frame detection rate)** | 0.9187 [0.8909, 0.9458] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.4779 [0.4296, 0.5272] |
| cell FPR (off frames) | 0.0598 [0.0515, 0.0684] |
| cell FPR (negative cells of on frames) | 0.0577 [0.0480, 0.0679] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.3148 [0.2339, 0.3982] | 0.0069 [0.0016, 0.0137] |
| 3a [5,8) m | 0.2705 [0.2235, 0.3193] | 0.0319 [0.0213, 0.0434] |
| 3b [8,12) m | 0.7136 [0.6838, 0.7429] | 0.2005 [0.1754, 0.2270] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5570 [0.5280, 0.5849] |
| cell recall | 0.4933 [0.4613, 0.5264] |
| cell precision | 0.6396 [0.5990, 0.6789] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.71

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8721 [0.8259, 0.9147] | 0.3437 [0.3086, 0.3801] | 219 |
| E | 0.7111 [0.5744, 0.8400] | 0.2500 [0.1844, 0.3238] | 45 |
| H | 0.6979 [0.6044, 0.7895] | 0.4098 [0.3570, 0.4669] | 96 |
| **any tier (frame detection rate)** | 0.7967 [0.7548, 0.8379] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2917 [0.2482, 0.3364] |
| cell FPR (off frames) | 0.0300 [0.0244, 0.0359] |
| cell FPR (negative cells of on frames) | 0.0347 [0.0271, 0.0431] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.1534 [0.0896, 0.2225] | 0.0025 [0.0005, 0.0054] |
| 3a [5,8) m | 0.1369 [0.1050, 0.1704] | 0.0162 [0.0097, 0.0236] |
| 3b [8,12) m | 0.5449 [0.5107, 0.5788] | 0.1015 [0.0824, 0.1218] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4599 [0.4303, 0.4899] |
| cell recall | 0.3435 [0.3156, 0.3724] |
| cell precision | 0.6957 [0.6513, 0.7385] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5934 | 0.5570 | 0.4657 |
| cell_recall | 0.6275 | 0.4933 | 0.3505 |
| cell_precision | 0.5628 | 0.6396 | 0.6937 |
| frame_det_rate | 0.9810 | 0.9187 | 0.8022 |
| frame_recall_V | 0.9863 | 0.9543 | 0.8767 |
| frame_recall_E | 1.0000 | 0.9111 | 0.7333 |
| frame_recall_H | 0.9688 | 0.8750 | 0.6979 |
| cell_recall_V | 0.6103 | 0.4807 | 0.3506 |
| cell_recall_E | 0.7356 | 0.5115 | 0.2615 |
| cell_recall_H | 0.6115 | 0.5287 | 0.4140 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.5000 | 0.3148 | 0.1587 |
| band3_cell_recall | 0.4141 | 0.2705 | 0.1403 |
| band4_cell_recall | 0.8395 | 0.7136 | 0.5551 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0162 | 0.0069 | 0.0025 |
| band3_cell_fpr_off | 0.0775 | 0.0319 | 0.0172 |
| band4_cell_fpr_off | 0.3515 | 0.2005 | 0.1054 |
| frame_fa_off | 0.6814 | 0.4779 | 0.3064 |
| cell_fpr_off | 0.1113 | 0.0598 | 0.0312 |
| cell_fpr_on_neg | 0.0913 | 0.0577 | 0.0353 |
