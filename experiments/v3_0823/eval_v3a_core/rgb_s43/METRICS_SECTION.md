# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/runs/v3a/rgb_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 369 | 219 | 45 | 96 | 7 | 2856 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6301 [0.5656, 0.6927] | 0.4773 [0.4131, 0.5442] | 219 |
| E | 0.0222 [0.0000, 0.0732] | 0.0057 [0.0000, 0.0188] | 45 |
| H | 0.6146 [0.5158, 0.7123] | 0.4926 [0.3943, 0.5936] | 96 |
| **any tier (frame detection rate)** | 0.5447 [0.4946, 0.5961] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1765 [0.1400, 0.2137] |
| cell FPR (off frames) | 0.0569 [0.0430, 0.0720] |
| cell FPR (negative cells of on frames) | 0.2517 [0.2164, 0.2887] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0513 [0.0000, 0.1333] | 0.0015 [0.0000, 0.0046] |
| 2 [2,5) m | 0.3836 [0.2891, 0.4819] | 0.0235 [0.0110, 0.0385] |
| 3a [5,8) m | 0.3827 [0.3162, 0.4507] | 0.0574 [0.0383, 0.0785] |
| 3b [8,12) m | 0.4871 [0.4375, 0.5372] | 0.1451 [0.1141, 0.1777] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4121 [0.3705, 0.4518] |
| cell recall | 0.4230 [0.3723, 0.4745] |
| cell precision | 0.4017 [0.3564, 0.4466] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6301 [0.5656, 0.6927] | 0.4773 [0.4131, 0.5442] | 219 |
| E | 0.0222 [0.0000, 0.0732] | 0.0057 [0.0000, 0.0188] | 45 |
| H | 0.6146 [0.5158, 0.7123] | 0.4926 [0.3943, 0.5936] | 96 |
| **any tier (frame detection rate)** | 0.5447 [0.4946, 0.5961] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1765 [0.1400, 0.2137] |
| cell FPR (off frames) | 0.0569 [0.0430, 0.0720] |
| cell FPR (negative cells of on frames) | 0.2517 [0.2164, 0.2887] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0513 [0.0000, 0.1333] | 0.0015 [0.0000, 0.0046] |
| 2 [2,5) m | 0.3836 [0.2891, 0.4819] | 0.0235 [0.0110, 0.0385] |
| 3a [5,8) m | 0.3827 [0.3162, 0.4507] | 0.0574 [0.0383, 0.0785] |
| 3b [8,12) m | 0.4871 [0.4375, 0.5372] | 0.1451 [0.1141, 0.1777] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4121 [0.3705, 0.4518] |
| cell recall | 0.4230 [0.3723, 0.4745] |
| cell precision | 0.4017 [0.3564, 0.4466] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4457 | 0.4121 | 0.3627 |
| cell_recall | 0.5613 | 0.4230 | 0.3081 |
| cell_precision | 0.3696 | 0.4017 | 0.4407 |
| frame_det_rate | 0.7182 | 0.5447 | 0.4092 |
| frame_recall_V | 0.8128 | 0.6301 | 0.5023 |
| frame_recall_E | 0.3333 | 0.0222 | 0.0000 |
| frame_recall_H | 0.7083 | 0.6146 | 0.3958 |
| cell_recall_V | 0.6024 | 0.4773 | 0.3670 |
| cell_recall_E | 0.1149 | 0.0057 | 0.0000 |
| cell_recall_H | 0.7113 | 0.4926 | 0.2781 |
| band1_cell_recall | 0.1282 | 0.0513 | 0.0256 |
| band2_cell_recall | 0.4947 | 0.3836 | 0.2116 |
| band3_cell_recall | 0.4759 | 0.3827 | 0.2929 |
| band4_cell_recall | 0.6646 | 0.4871 | 0.3646 |
| band1_cell_fpr_off | 0.0054 | 0.0015 | 0.0000 |
| band2_cell_fpr_off | 0.0574 | 0.0235 | 0.0088 |
| band3_cell_fpr_off | 0.1118 | 0.0574 | 0.0181 |
| band4_cell_fpr_off | 0.2451 | 0.1451 | 0.0755 |
| frame_fa_off | 0.3358 | 0.1765 | 0.1201 |
| cell_fpr_off | 0.1049 | 0.0569 | 0.0256 |
| cell_fpr_on_neg | 0.3541 | 0.2517 | 0.1712 |
