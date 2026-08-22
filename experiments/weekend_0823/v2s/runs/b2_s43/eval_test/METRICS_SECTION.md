# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/b2_s43/best.pt`
grid: **PROVISIONAL-GRID-V2S** (4 bands x 10 sectors = 40 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.77 (fitted on **val**, val cell-F1 0.5214) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 4998 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8667 [0.8154, 0.9153] | 0.2925 [0.2559, 0.3306] | 180 |
| E | 0.0444 [0.0000, 0.1136] | 0.0044 [0.0000, 0.0125] | 45 |
| H | 0.5938 [0.4945, 0.6916] | 0.2374 [0.1947, 0.2777] | 96 |
| **any tier (frame detection rate)** | 0.6636 [0.6122, 0.7147] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3211 [0.2746, 0.3670] |
| cell FPR (off frames) | 0.0240 [0.0192, 0.0292] |
| cell FPR (negative cells of on frames) | 0.0761 [0.0643, 0.0883] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0854 [0.0473, 0.1287] | 0.0034 [0.0007, 0.0073] |
| 3a [5,8) m | 0.1310 [0.0970, 0.1667] | 0.0120 [0.0060, 0.0188] |
| 3b [8,12) m | 0.3865 [0.3482, 0.4252] | 0.0806 [0.0662, 0.0957] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3270 [0.2960, 0.3569] |
| cell recall | 0.2445 [0.2170, 0.2726] |
| cell precision | 0.4935 [0.4450, 0.5411] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.77

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8444 [0.7903, 0.8958] | 0.2264 [0.1968, 0.2570] | 180 |
| E | 0.0444 [0.0000, 0.1136] | 0.0030 [0.0000, 0.0079] | 45 |
| H | 0.3438 [0.2500, 0.4388] | 0.1390 [0.1038, 0.1728] | 96 |
| **any tier (frame detection rate)** | 0.5749 [0.5205, 0.6292] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2157 [0.1762, 0.2563] |
| cell FPR (off frames) | 0.0128 [0.0096, 0.0164] |
| cell FPR (negative cells of on frames) | 0.0478 [0.0388, 0.0570] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0448 [0.0214, 0.0731] | 0.0007 [0.0000, 0.0023] |
| 3a [5,8) m | 0.0808 [0.0554, 0.1079] | 0.0059 [0.0017, 0.0111] |
| 3b [8,12) m | 0.3033 [0.2686, 0.3388] | 0.0446 [0.0344, 0.0557] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2728 [0.2449, 0.3005] |
| cell recall | 0.1817 [0.1598, 0.2041] |
| cell precision | 0.5476 [0.4948, 0.5999] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3645 | 0.3270 | 0.2907 |
| cell_recall | 0.3011 | 0.2445 | 0.2001 |
| cell_precision | 0.4617 | 0.4935 | 0.5316 |
| frame_det_rate | 0.6911 | 0.6636 | 0.5994 |
| frame_recall_V | 0.8722 | 0.8667 | 0.8611 |
| frame_recall_E | 0.0444 | 0.0444 | 0.0444 |
| frame_recall_H | 0.6667 | 0.5938 | 0.3958 |
| cell_recall_V | 0.3508 | 0.2925 | 0.2459 |
| cell_recall_E | 0.0104 | 0.0044 | 0.0030 |
| cell_recall_H | 0.3272 | 0.2374 | 0.1685 |
| band1_cell_recall | 0.0089 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.1289 | 0.0854 | 0.0588 |
| band3_cell_recall | 0.1792 | 0.1310 | 0.0952 |
| band4_cell_recall | 0.4568 | 0.3865 | 0.3272 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0074 | 0.0034 | 0.0010 |
| band3_cell_fpr_off | 0.0194 | 0.0120 | 0.0069 |
| band4_cell_fpr_off | 0.1257 | 0.0806 | 0.0525 |
| frame_fa_off | 0.4216 | 0.3211 | 0.2402 |
| cell_fpr_off | 0.0381 | 0.0240 | 0.0151 |
| cell_fpr_on_neg | 0.1001 | 0.0761 | 0.0561 |
