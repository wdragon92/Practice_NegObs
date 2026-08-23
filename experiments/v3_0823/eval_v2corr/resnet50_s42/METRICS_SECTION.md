# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/newmodels/runs/resnet50_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.72 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 369 | 219 | 45 | 96 | 7 | 2856 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8356 [0.7854, 0.8837] | 0.5208 [0.4637, 0.5779] | 219 |
| E | 0.5111 [0.3636, 0.6596] | 0.1839 [0.1215, 0.2444] | 45 |
| H | 0.4688 [0.3694, 0.5714] | 0.3185 [0.2321, 0.4075] | 96 |
| **any tier (frame detection rate)** | 0.6992 [0.6512, 0.7460] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2132 [0.1744, 0.2536] |
| cell FPR (off frames) | 0.0319 [0.0242, 0.0406] |
| cell FPR (negative cells of on frames) | 0.1205 [0.1039, 0.1385] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0427 [0.0000, 0.1389] | 0.0010 [0.0000, 0.0031] |
| 2 [2,5) m | 0.5132 [0.4164, 0.6074] | 0.0265 [0.0149, 0.0395] |
| 3a [5,8) m | 0.4366 [0.3807, 0.4916] | 0.0407 [0.0272, 0.0559] |
| 3b [8,12) m | 0.4707 [0.4245, 0.5167] | 0.0593 [0.0438, 0.0767] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5084 [0.4684, 0.5452] |
| cell recall | 0.4482 [0.4031, 0.4931] |
| cell precision | 0.5874 [0.5438, 0.6292] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.72

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.7443 [0.6845, 0.8026] | 0.4070 [0.3531, 0.4610] | 219 |
| E | 0.3111 [0.1765, 0.4524] | 0.0891 [0.0453, 0.1356] | 45 |
| H | 0.2812 [0.1910, 0.3736] | 0.1953 [0.1221, 0.2717] | 96 |
| **any tier (frame detection rate)** | 0.5610 [0.5088, 0.6119] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1176 [0.0875, 0.1500] |
| cell FPR (off frames) | 0.0150 [0.0100, 0.0207] |
| cell FPR (negative cells of on frames) | 0.0669 [0.0548, 0.0805] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0085 [0.0000, 0.0278] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.4233 [0.3307, 0.5166] | 0.0098 [0.0033, 0.0179] |
| 3a [5,8) m | 0.2851 [0.2360, 0.3361] | 0.0191 [0.0103, 0.0294] |
| 3b [8,12) m | 0.3667 [0.3235, 0.4111] | 0.0309 [0.0198, 0.0436] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4451 [0.4012, 0.4870] |
| cell recall | 0.3340 [0.2920, 0.3761] |
| cell precision | 0.6667 [0.6172, 0.7125] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5319 | 0.5084 | 0.4556 |
| cell_recall | 0.5420 | 0.4482 | 0.3477 |
| cell_precision | 0.5221 | 0.5874 | 0.6607 |
| frame_det_rate | 0.7832 | 0.6992 | 0.5772 |
| frame_recall_V | 0.8858 | 0.8356 | 0.7626 |
| frame_recall_E | 0.6000 | 0.5111 | 0.3111 |
| frame_recall_H | 0.6146 | 0.4688 | 0.3021 |
| cell_recall_V | 0.6063 | 0.5208 | 0.4199 |
| cell_recall_E | 0.3103 | 0.1839 | 0.1006 |
| cell_recall_H | 0.4225 | 0.3185 | 0.2123 |
| band1_cell_recall | 0.0769 | 0.0427 | 0.0085 |
| band2_cell_recall | 0.5873 | 0.5132 | 0.4259 |
| band3_cell_recall | 0.5511 | 0.4366 | 0.3053 |
| band4_cell_recall | 0.5619 | 0.4707 | 0.3803 |
| band1_cell_fpr_off | 0.0039 | 0.0010 | 0.0000 |
| band2_cell_fpr_off | 0.0436 | 0.0265 | 0.0108 |
| band3_cell_fpr_off | 0.0623 | 0.0407 | 0.0221 |
| band4_cell_fpr_off | 0.1181 | 0.0593 | 0.0314 |
| frame_fa_off | 0.3456 | 0.2132 | 0.1275 |
| cell_fpr_off | 0.0570 | 0.0319 | 0.0161 |
| cell_fpr_on_neg | 0.1795 | 0.1205 | 0.0715 |
