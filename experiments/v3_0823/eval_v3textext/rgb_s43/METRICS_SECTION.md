# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.71 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6989 [0.6047, 0.7927] | 0.5000 [0.4243, 0.5728] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.6111 [0.4930, 0.7260] | 0.2755 [0.2235, 0.3289] | 72 |
| **any tier (frame detection rate)** | 0.6606 [0.5868, 0.7321] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.7500 [0.6993, 0.7985] |
| cell FPR (off frames) | 0.1299 [0.1142, 0.1464] |
| cell FPR (negative cells of on frames) | 0.0792 [0.0663, 0.0930] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0021 [0.0000, 0.0065] |
| 2 [2,5) m | 0.3485 [0.1681, 0.5372] | 0.0389 [0.0213, 0.0598] |
| 3a [5,8) m | 0.3281 [0.2317, 0.4290] | 0.0979 [0.0733, 0.1250] |
| 3b [8,12) m | 0.5030 [0.4443, 0.5612] | 0.3806 [0.3443, 0.4184] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3578 [0.3025, 0.4109] |
| cell recall | 0.4192 [0.3632, 0.4756] |
| cell precision | 0.3120 [0.2537, 0.3713] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.71

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.5806 [0.4819, 0.6796] | 0.4388 [0.3614, 0.5132] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.5000 [0.3833, 0.6164] | 0.2083 [0.1611, 0.2566] | 72 |
| **any tier (frame detection rate)** | 0.5455 [0.4699, 0.6220] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.5729 [0.5167, 0.6293] |
| cell FPR (off frames) | 0.0858 [0.0732, 0.0992] |
| cell FPR (negative cells of on frames) | 0.0404 [0.0329, 0.0484] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0007 [0.0000, 0.0022] |
| 2 [2,5) m | 0.3409 [0.1562, 0.5310] | 0.0146 [0.0048, 0.0268] |
| 3a [5,8) m | 0.2730 [0.1867, 0.3650] | 0.0521 [0.0341, 0.0721] |
| 3b [8,12) m | 0.4212 [0.3641, 0.4788] | 0.2757 [0.2394, 0.3132] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3705 [0.3108, 0.4277] |
| cell recall | 0.3558 [0.2992, 0.4137] |
| cell precision | 0.3864 [0.3145, 0.4582] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3358 | 0.3578 | 0.3723 |
| cell_recall | 0.4733 | 0.4192 | 0.3600 |
| cell_precision | 0.2602 | 0.3120 | 0.3854 |
| frame_det_rate | 0.7333 | 0.6606 | 0.5455 |
| frame_recall_V | 0.7312 | 0.6989 | 0.5806 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.7361 | 0.6111 | 0.5000 |
| cell_recall_V | 0.5352 | 0.5000 | 0.4414 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.3634 | 0.2755 | 0.2153 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.4091 | 0.3485 | 0.3409 |
| band3_cell_recall | 0.3386 | 0.3281 | 0.2782 |
| band4_cell_recall | 0.5833 | 0.5030 | 0.4258 |
| band1_cell_fpr_off | 0.0035 | 0.0021 | 0.0007 |
| band2_cell_fpr_off | 0.0611 | 0.0389 | 0.0146 |
| band3_cell_fpr_off | 0.1660 | 0.0979 | 0.0535 |
| band4_cell_fpr_off | 0.5014 | 0.3806 | 0.2785 |
| frame_fa_off | 0.8785 | 0.7500 | 0.5764 |
| cell_fpr_off | 0.1830 | 0.1299 | 0.0868 |
| cell_fpr_on_neg | 0.1230 | 0.0792 | 0.0414 |
