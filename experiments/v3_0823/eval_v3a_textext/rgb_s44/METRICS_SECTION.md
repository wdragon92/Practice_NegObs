# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/runs/v3a/rgb_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4516 [0.3523, 0.5532] | 0.3568 [0.2741, 0.4394] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.3333 [0.2267, 0.4444] | 0.1713 [0.1017, 0.2465] | 72 |
| **any tier (frame detection rate)** | 0.4000 [0.3272, 0.4753] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2465 [0.1972, 0.2959] |
| cell FPR (off frames) | 0.0701 [0.0512, 0.0902] |
| cell FPR (negative cells of on frames) | 0.0432 [0.0293, 0.0579] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.3561 [0.2283, 0.5000] | 0.0736 [0.0476, 0.1014] |
| 3a [5,8) m | 0.2835 [0.2029, 0.3655] | 0.0854 [0.0574, 0.1155] |
| 3b [8,12) m | 0.2924 [0.2278, 0.3575] | 0.1215 [0.0910, 0.1539] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3239 [0.2607, 0.3847] |
| cell recall | 0.2900 [0.2294, 0.3518] |
| cell precision | 0.3667 [0.2864, 0.4492] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4516 [0.3523, 0.5532] | 0.3568 [0.2741, 0.4394] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.3333 [0.2267, 0.4444] | 0.1713 [0.1017, 0.2465] | 72 |
| **any tier (frame detection rate)** | 0.4000 [0.3272, 0.4753] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2465 [0.1972, 0.2959] |
| cell FPR (off frames) | 0.0701 [0.0512, 0.0902] |
| cell FPR (negative cells of on frames) | 0.0432 [0.0293, 0.0579] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.3561 [0.2283, 0.5000] | 0.0736 [0.0476, 0.1014] |
| 3a [5,8) m | 0.2835 [0.2029, 0.3655] | 0.0854 [0.0574, 0.1155] |
| 3b [8,12) m | 0.2924 [0.2278, 0.3575] | 0.1215 [0.0910, 0.1539] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3239 [0.2607, 0.3847] |
| cell recall | 0.2900 [0.2294, 0.3518] |
| cell precision | 0.3667 [0.2864, 0.4492] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3583 | 0.3239 | 0.2475 |
| cell_recall | 0.4100 | 0.2900 | 0.1842 |
| cell_precision | 0.3182 | 0.3667 | 0.3771 |
| frame_det_rate | 0.5030 | 0.4000 | 0.2727 |
| frame_recall_V | 0.5054 | 0.4516 | 0.3441 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.5000 | 0.3333 | 0.1806 |
| cell_recall_V | 0.4792 | 0.3568 | 0.2331 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.2870 | 0.1713 | 0.0972 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.5379 | 0.3561 | 0.1667 |
| band3_cell_recall | 0.4016 | 0.2835 | 0.1837 |
| band4_cell_recall | 0.4061 | 0.2924 | 0.1955 |
| band1_cell_fpr_off | 0.0076 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.1007 | 0.0736 | 0.0444 |
| band3_cell_fpr_off | 0.1389 | 0.0854 | 0.0625 |
| band4_cell_fpr_off | 0.2146 | 0.1215 | 0.0688 |
| frame_fa_off | 0.4028 | 0.2465 | 0.1493 |
| cell_fpr_off | 0.1155 | 0.0701 | 0.0439 |
| cell_fpr_on_neg | 0.0853 | 0.0432 | 0.0246 |
