# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `experiments/mainrun_0819/runs/rgb_s42/eval_test/per_frame.csv`
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

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

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

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

## 3. Paired comparison (A = this arm, B = `experiments/mainrun_0819/runs/depth_s42/eval_test/per_frame.csv`)

336 common frames · paired percentile bootstrap 10000x seed 42 · threshold 0.5

| metric | A | B | A−B [95% CI] | CI excludes 0 |
|---|---|---|---|---|
| cell_f1 | 0.4415 | 0.6893 | -0.2478 [-0.3078, -0.1901] | yes |
| cell_recall | 0.4312 | 0.6208 | -0.1896 [-0.2600, -0.1167] | yes |
| cell_precision | 0.4524 | 0.7748 | -0.3224 [-0.3870, -0.2557] | yes |
| frame_recall_V | 0.6667 | 0.9189 | -0.2523 [-0.3462, -0.1610] | yes |
| frame_recall_E | 0.4444 | 0.3333 | 0.1111 [0.0000, 0.3750] | no |
| frame_recall_H | 0.3333 | 0.7143 | -0.3810 [-0.6875, -0.0526] | yes |
| cell_recall_V | 0.4542 | 0.6479 | -0.1937 [-0.2652, -0.1210] | yes |
| cell_recall_E | 0.3077 | 0.2308 | 0.0769 [-0.1290, 0.3043] | no |
| cell_recall_H | 0.2667 | 0.5333 | -0.2667 [-0.6000, 0.0844] | no |
| band1_cell_recall | 0.0000 | 0.0513 | -0.0513 [-0.0893, -0.0177] | yes |
| band2_cell_recall | 0.2899 | 0.6196 | -0.3297 [-0.4327, -0.2258] | yes |
| band3_cell_recall | 0.5833 | 0.7347 | -0.1514 [-0.2500, -0.0510] | yes |
| frame_fa_off | 0.2738 | 0.1607 | 0.1131 [0.0414, 0.1875] | yes |
| cell_fpr_off | 0.1004 | 0.0298 | 0.0706 [0.0472, 0.0969] | yes |
| cell_fpr_on_neg | 0.1683 | 0.0663 | 0.1020 [0.0568, 0.1482] | yes |
