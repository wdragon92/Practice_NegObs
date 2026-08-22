# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/fusion/s43/fused_or/per_frame.csv`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 2691 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9500 [0.9171, 0.9788] | 0.4882 [0.4444, 0.5320] | 180 |
| E | 0.9111 [0.8182, 0.9804] | 0.5115 [0.4260, 0.6026] | 45 |
| H | 0.8750 [0.8061, 0.9368] | 0.5287 [0.4748, 0.5885] | 96 |
| **any tier (frame detection rate)** | 0.9113 [0.8806, 0.9413] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.4779 [0.4296, 0.5272] |
| cell FPR (off frames) | 0.0614 [0.0530, 0.0702] |
| cell FPR (negative cells of on frames) | 0.0839 [0.0722, 0.0958] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1624 [0.0820, 0.2500] | 0.0044 [0.0019, 0.0075] |
| 2 [2,5) m | 0.3492 [0.2671, 0.4334] | 0.0088 [0.0030, 0.0162] |
| 3a [5,8) m | 0.2759 [0.2276, 0.3252] | 0.0319 [0.0213, 0.0434] |
| 3b [8,12) m | 0.7157 [0.6836, 0.7473] | 0.2005 [0.1754, 0.2270] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5370 [0.5053, 0.5668] |
| cell recall | 0.4980 [0.4647, 0.5320] |
| cell precision | 0.5826 [0.5386, 0.6248] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9500 [0.9171, 0.9788] | 0.4882 [0.4444, 0.5320] | 180 |
| E | 0.9111 [0.8182, 0.9804] | 0.5115 [0.4260, 0.6026] | 45 |
| H | 0.8750 [0.8061, 0.9368] | 0.5287 [0.4748, 0.5885] | 96 |
| **any tier (frame detection rate)** | 0.9113 [0.8806, 0.9413] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.4779 [0.4296, 0.5272] |
| cell FPR (off frames) | 0.0614 [0.0530, 0.0702] |
| cell FPR (negative cells of on frames) | 0.0839 [0.0722, 0.0958] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1624 [0.0820, 0.2500] | 0.0044 [0.0019, 0.0075] |
| 2 [2,5) m | 0.3492 [0.2671, 0.4334] | 0.0088 [0.0030, 0.0162] |
| 3a [5,8) m | 0.2759 [0.2276, 0.3252] | 0.0319 [0.0213, 0.0434] |
| 3b [8,12) m | 0.7157 [0.6836, 0.7473] | 0.2005 [0.1754, 0.2270] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5370 [0.5053, 0.5668] |
| cell recall | 0.4980 [0.4647, 0.5320] |
| cell precision | 0.5826 [0.5386, 0.6248] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5686 | 0.5370 | 0.4528 |
| cell_recall | 0.6347 | 0.4980 | 0.3512 |
| cell_precision | 0.5149 | 0.5826 | 0.6372 |
| frame_det_rate | 0.9817 | 0.9113 | 0.7951 |
| frame_recall_V | 0.9889 | 0.9500 | 0.8833 |
| frame_recall_E | 1.0000 | 0.9111 | 0.7333 |
| frame_recall_H | 0.9688 | 0.8750 | 0.6979 |
| cell_recall_V | 0.6211 | 0.4882 | 0.3526 |
| cell_recall_E | 0.7356 | 0.5115 | 0.2615 |
| cell_recall_H | 0.6115 | 0.5287 | 0.4140 |
| band1_cell_recall | 0.2051 | 0.1624 | 0.1026 |
| band2_cell_recall | 0.5370 | 0.3492 | 0.1746 |
| band3_cell_recall | 0.4218 | 0.2759 | 0.1437 |
| band4_cell_recall | 0.8401 | 0.7157 | 0.5596 |
| band1_cell_fpr_off | 0.0059 | 0.0044 | 0.0015 |
| band2_cell_fpr_off | 0.0191 | 0.0088 | 0.0034 |
| band3_cell_fpr_off | 0.0775 | 0.0319 | 0.0172 |
| band4_cell_fpr_off | 0.3520 | 0.2005 | 0.1054 |
| frame_fa_off | 0.6863 | 0.4779 | 0.3113 |
| cell_fpr_off | 0.1136 | 0.0614 | 0.0319 |
| cell_fpr_on_neg | 0.1247 | 0.0839 | 0.0508 |
