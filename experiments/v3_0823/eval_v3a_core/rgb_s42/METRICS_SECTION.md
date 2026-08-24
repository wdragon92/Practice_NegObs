# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/runs/v3a/rgb_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 369 | 219 | 45 | 96 | 7 | 2856 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6941 [0.6330, 0.7547] | 0.3694 [0.3184, 0.4228] | 219 |
| E | 1.0000 [1.0000, 1.0000] | 0.7040 [0.6323, 0.7742] | 45 |
| H | 0.6458 [0.5490, 0.7411] | 0.6136 [0.5241, 0.6951] | 96 |
| **any tier (frame detection rate)** | 0.7073 [0.6604, 0.7528] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3529 [0.3068, 0.3986] |
| cell FPR (off frames) | 0.0569 [0.0470, 0.0672] |
| cell FPR (negative cells of on frames) | 0.1972 [0.1707, 0.2242] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0171 [0.0000, 0.0451] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.4127 [0.3154, 0.5094] | 0.0343 [0.0204, 0.0497] |
| 3a [5,8) m | 0.4523 [0.3968, 0.5064] | 0.0858 [0.0665, 0.1055] |
| 3b [8,12) m | 0.4925 [0.4515, 0.5338] | 0.1074 [0.0891, 0.1264] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4548 [0.4184, 0.4898] |
| cell recall | 0.4499 [0.4070, 0.4937] |
| cell precision | 0.4597 [0.4164, 0.5034] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6941 [0.6330, 0.7547] | 0.3694 [0.3184, 0.4228] | 219 |
| E | 1.0000 [1.0000, 1.0000] | 0.7040 [0.6323, 0.7742] | 45 |
| H | 0.6458 [0.5490, 0.7411] | 0.6136 [0.5241, 0.6951] | 96 |
| **any tier (frame detection rate)** | 0.7073 [0.6604, 0.7528] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3529 [0.3068, 0.3986] |
| cell FPR (off frames) | 0.0569 [0.0470, 0.0672] |
| cell FPR (negative cells of on frames) | 0.1972 [0.1707, 0.2242] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0171 [0.0000, 0.0451] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.4127 [0.3154, 0.5094] | 0.0343 [0.0204, 0.0497] |
| 3a [5,8) m | 0.4523 [0.3968, 0.5064] | 0.0858 [0.0665, 0.1055] |
| 3b [8,12) m | 0.4925 [0.4515, 0.5338] | 0.1074 [0.0891, 0.1264] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4548 [0.4184, 0.4898] |
| cell recall | 0.4499 [0.4070, 0.4937] |
| cell precision | 0.4597 [0.4164, 0.5034] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4909 | 0.4548 | 0.4083 |
| cell_recall | 0.5567 | 0.4499 | 0.3533 |
| cell_precision | 0.4390 | 0.4597 | 0.4835 |
| frame_det_rate | 0.8103 | 0.7073 | 0.6125 |
| frame_recall_V | 0.8219 | 0.6941 | 0.5845 |
| frame_recall_E | 1.0000 | 1.0000 | 0.9778 |
| frame_recall_H | 0.7396 | 0.6458 | 0.5521 |
| cell_recall_V | 0.4787 | 0.3694 | 0.2819 |
| cell_recall_E | 0.8276 | 0.7040 | 0.5632 |
| cell_recall_H | 0.6964 | 0.6136 | 0.5138 |
| band1_cell_recall | 0.0342 | 0.0171 | 0.0085 |
| band2_cell_recall | 0.5556 | 0.4127 | 0.3042 |
| band3_cell_recall | 0.5488 | 0.4523 | 0.3648 |
| band4_cell_recall | 0.6034 | 0.4925 | 0.3864 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0559 | 0.0343 | 0.0240 |
| band3_cell_fpr_off | 0.1206 | 0.0858 | 0.0549 |
| band4_cell_fpr_off | 0.1745 | 0.1074 | 0.0574 |
| frame_fa_off | 0.4779 | 0.3529 | 0.2304 |
| cell_fpr_off | 0.0877 | 0.0569 | 0.0341 |
| cell_fpr_on_neg | 0.2481 | 0.1972 | 0.1508 |
