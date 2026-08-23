# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.45 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6559 [0.5567, 0.7526] | 0.2318 [0.1740, 0.2921] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.2778 [0.1774, 0.3837] | 0.1065 [0.0667, 0.1472] | 72 |
| **any tier (frame detection rate)** | 0.4909 [0.4157, 0.5677] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.5312 [0.4732, 0.5880] |
| cell FPR (off frames) | 0.0764 [0.0634, 0.0913] |
| cell FPR (negative cells of on frames) | 0.1039 [0.0868, 0.1228] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2197 [0.1127, 0.3434] | 0.0514 [0.0309, 0.0754] |
| 3a [5,8) m | 0.1391 [0.0862, 0.1976] | 0.0500 [0.0324, 0.0701] |
| 3b [8,12) m | 0.2152 [0.1747, 0.2581] | 0.2042 [0.1766, 0.2329] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1916 [0.1487, 0.2366] |
| cell recall | 0.1867 [0.1460, 0.2303] |
| cell precision | 0.1968 [0.1470, 0.2527] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.45

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6774 [0.5789, 0.7717] | 0.2565 [0.1941, 0.3214] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.2917 [0.1905, 0.4000] | 0.1134 [0.0730, 0.1560] | 72 |
| **any tier (frame detection rate)** | 0.5091 [0.4329, 0.5862] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.5486 [0.4907, 0.6051] |
| cell FPR (off frames) | 0.0823 [0.0689, 0.0976] |
| cell FPR (negative cells of on frames) | 0.1096 [0.0921, 0.1287] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2576 [0.1368, 0.3926] | 0.0590 [0.0369, 0.0847] |
| 3a [5,8) m | 0.1601 [0.1015, 0.2246] | 0.0535 [0.0353, 0.0741] |
| 3b [8,12) m | 0.2288 [0.1871, 0.2726] | 0.2167 [0.1886, 0.2457] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2033 [0.1584, 0.2501] |
| cell recall | 0.2050 [0.1612, 0.2519] |
| cell precision | 0.2016 [0.1515, 0.2571] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.2398 | 0.1916 | 0.1355 |
| cell_recall | 0.2733 | 0.1867 | 0.1133 |
| cell_precision | 0.2135 | 0.1968 | 0.1683 |
| frame_det_rate | 0.6000 | 0.4909 | 0.4000 |
| frame_recall_V | 0.7957 | 0.6559 | 0.5269 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.3472 | 0.2778 | 0.2361 |
| cell_recall_V | 0.3451 | 0.2318 | 0.1406 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.1458 | 0.1065 | 0.0648 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.3712 | 0.2197 | 0.0909 |
| band3_cell_recall | 0.2336 | 0.1391 | 0.0814 |
| band4_cell_recall | 0.2879 | 0.2152 | 0.1409 |
| band1_cell_fpr_off | 0.0007 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0826 | 0.0514 | 0.0264 |
| band3_cell_fpr_off | 0.0771 | 0.0500 | 0.0326 |
| band4_cell_fpr_off | 0.2639 | 0.2042 | 0.1549 |
| frame_fa_off | 0.6181 | 0.5312 | 0.4549 |
| cell_fpr_off | 0.1061 | 0.0764 | 0.0535 |
| cell_fpr_on_neg | 0.1309 | 0.1039 | 0.0798 |
