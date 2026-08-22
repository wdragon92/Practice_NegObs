# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `experiments/mainrun_0819/runs/rgb_s42/best.pt`
tau_op = 0.5 · tau_star = 0.36 (fitted on **val**, val cell-F1 0.3325) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 336 | 168 | 168 | 141 | 111 | 9 | 21 | 7 | 981 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6667 [0.5772, 0.7547] | 0.4542 [0.3838, 0.5254] | 111 |
| E | 0.4444 [0.1111, 0.8000] | 0.3077 [0.0400, 0.5833] | 9 |
| H | 0.3333 [0.1333, 0.5455] | 0.2667 [0.0909, 0.4590] | 21 |

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2738 [0.2071, 0.3438] |
| cell FPR (off frames) | 0.1004 [0.0738, 0.1297] |
| cell FPR (negative cells of on frames) | 0.1683 [0.1263, 0.2111] |

| distance band | cell recall [95% CI] |
|---|---|
| 1 near | 0.0000 [0.0000, 0.0000] |
| 2 mid | 0.2899 [0.1979, 0.3865] |
| 3 far | 0.5833 [0.5009, 0.6649] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4415 [0.3797, 0.5005] |
| cell recall | 0.4312 [0.3668, 0.4961] |
| cell precision | 0.4524 [0.3756, 0.5328] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.36

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.7117 [0.6270, 0.7965] | 0.5070 [0.4318, 0.5832] | 111 |
| E | 0.6667 [0.3333, 1.0000] | 0.4359 [0.1250, 0.7308] | 9 |
| H | 0.4762 [0.2609, 0.7000] | 0.3667 [0.1758, 0.5672] | 21 |

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3393 [0.2692, 0.4128] |
| cell FPR (off frames) | 0.1377 [0.1058, 0.1728] |
| cell FPR (negative cells of on frames) | 0.1975 [0.1507, 0.2442] |

| distance band | cell recall [95% CI] |
|---|---|
| 1 near | 0.0000 [0.0000, 0.0000] |
| 2 mid | 0.3877 [0.2831, 0.4942] |
| 3 far | 0.6378 [0.5583, 0.7158] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4560 [0.3942, 0.5156] |
| cell recall | 0.4913 [0.4226, 0.5604] |
| cell precision | 0.4254 [0.3539, 0.5009] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4717 | 0.4415 | 0.3899 |
| cell_recall | 0.5311 | 0.4312 | 0.3303 |
| cell_precision | 0.4243 | 0.4524 | 0.4758 |
| frame_recall_V | 0.7477 | 0.6667 | 0.6036 |
| frame_recall_E | 0.6667 | 0.4444 | 0.1111 |
| frame_recall_H | 0.5238 | 0.3333 | 0.1905 |
| cell_recall_V | 0.5434 | 0.4542 | 0.3662 |
| cell_recall_E | 0.4872 | 0.3077 | 0.1282 |
| cell_recall_H | 0.4333 | 0.2667 | 0.0778 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.4529 | 0.2899 | 0.1630 |
| band3_cell_recall | 0.6735 | 0.5833 | 0.4745 |
| frame_fa_off | 0.3750 | 0.2738 | 0.2143 |
| cell_fpr_off | 0.1508 | 0.1004 | 0.0683 |
| cell_fpr_on_neg | 0.2125 | 0.1683 | 0.1202 |
