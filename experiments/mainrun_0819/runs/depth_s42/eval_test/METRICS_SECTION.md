# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **test** · ckpt: `experiments/mainrun_0819/runs/depth_s42/best.pt`
tau_op = 0.5 · tau_star = 0.7 (fitted on **val**, val cell-F1 0.3684) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 336 | 168 | 168 | 141 | 111 | 9 | 21 | 7 | 981 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9189 [0.8649, 0.9658] | 0.6479 [0.6058, 0.6919] | 111 |
| E | 0.3333 [0.0000, 0.6667] | 0.2308 [0.0000, 0.4286] | 9 |
| H | 0.7143 [0.5000, 0.9000] | 0.5333 [0.3548, 0.7121] | 21 |

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1607 [0.1071, 0.2195] |
| cell FPR (off frames) | 0.0298 [0.0175, 0.0439] |
| cell FPR (negative cells of on frames) | 0.0663 [0.0501, 0.0841] |

| distance band | cell recall [95% CI] |
|---|---|
| 1 near | 0.0513 [0.0177, 0.0893] |
| 2 mid | 0.6196 [0.5299, 0.7065] |
| 3 far | 0.7347 [0.6746, 0.7909] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6893 [0.6542, 0.7213] |
| cell recall | 0.6208 [0.5782, 0.6630] |
| cell precision | 0.7748 [0.7219, 0.8226] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.7

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.7568 [0.6729, 0.8333] | 0.4648 [0.4085, 0.5199] | 111 |
| E | 0.3333 [0.0000, 0.6667] | 0.1538 [0.0000, 0.2857] | 9 |
| H | 0.5714 [0.3529, 0.7857] | 0.4000 [0.2222, 0.5875] | 21 |

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1071 [0.0628, 0.1576] |
| cell FPR (off frames) | 0.0202 [0.0103, 0.0322] |
| cell FPR (negative cells of on frames) | 0.0214 [0.0138, 0.0300] |

| distance band | cell recall [95% CI] |
|---|---|
| 1 near | 0.0000 [0.0000, 0.0000] |
| 2 mid | 0.3370 [0.2489, 0.4252] |
| 3 far | 0.5867 [0.5179, 0.6518] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5828 [0.5308, 0.6296] |
| cell recall | 0.4465 [0.3941, 0.4984] |
| cell precision | 0.8391 [0.7787, 0.8902] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.7249 | 0.6893 | 0.5828 |
| cell_recall | 0.7737 | 0.6208 | 0.4465 |
| cell_precision | 0.6819 | 0.7748 | 0.8391 |
| frame_recall_V | 0.9189 | 0.9189 | 0.7568 |
| frame_recall_E | 0.6667 | 0.3333 | 0.3333 |
| frame_recall_H | 0.7143 | 0.7143 | 0.5714 |
| cell_recall_V | 0.7993 | 0.6479 | 0.4648 |
| cell_recall_E | 0.3077 | 0.2308 | 0.1538 |
| cell_recall_H | 0.7333 | 0.5333 | 0.4000 |
| band1_cell_recall | 0.3077 | 0.0513 | 0.0000 |
| band2_cell_recall | 0.8478 | 0.6196 | 0.3370 |
| band3_cell_recall | 0.8316 | 0.7347 | 0.5867 |
| frame_fa_off | 0.2143 | 0.1607 | 0.1071 |
| cell_fpr_off | 0.0548 | 0.0298 | 0.0202 |
| cell_fpr_on_neg | 0.1404 | 0.0663 | 0.0214 |
