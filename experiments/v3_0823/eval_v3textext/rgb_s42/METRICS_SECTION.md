# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.63 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.5591 [0.4583, 0.6596] | 0.3438 [0.2653, 0.4256] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.6111 [0.4933, 0.7222] | 0.3380 [0.2709, 0.4020] | 72 |
| **any tier (frame detection rate)** | 0.5818 [0.5063, 0.6566] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.7396 [0.6884, 0.7885] |
| cell FPR (off frames) | 0.1786 [0.1580, 0.2005] |
| cell FPR (negative cells of on frames) | 0.1502 [0.1297, 0.1711] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2879 [0.1428, 0.4533] | 0.1021 [0.0718, 0.1347] |
| 3a [5,8) m | 0.2808 [0.2191, 0.3415] | 0.2472 [0.2113, 0.2855] |
| 3b [8,12) m | 0.4015 [0.3389, 0.4625] | 0.3653 [0.3295, 0.4014] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2467 [0.2020, 0.2902] |
| cell recall | 0.3417 [0.2860, 0.3973] |
| cell precision | 0.1930 [0.1519, 0.2359] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.63

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4839 [0.3846, 0.5862] | 0.2891 [0.2199, 0.3627] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.5278 [0.4118, 0.6447] | 0.2523 [0.1979, 0.3060] | 72 |
| **any tier (frame detection rate)** | 0.5030 [0.4268, 0.5802] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.6875 [0.6345, 0.7401] |
| cell FPR (off frames) | 0.1392 [0.1219, 0.1581] |
| cell FPR (negative cells of on frames) | 0.1134 [0.0970, 0.1307] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2045 [0.0808, 0.3504] | 0.0701 [0.0454, 0.0975] |
| 3a [5,8) m | 0.2257 [0.1714, 0.2817] | 0.1944 [0.1626, 0.2288] |
| 3b [8,12) m | 0.3303 [0.2734, 0.3885] | 0.2924 [0.2593, 0.3268] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2323 [0.1885, 0.2746] |
| cell recall | 0.2758 [0.2272, 0.3263] |
| cell precision | 0.2006 [0.1568, 0.2464] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.2508 | 0.2467 | 0.2293 |
| cell_recall | 0.4367 | 0.3417 | 0.2492 |
| cell_precision | 0.1759 | 0.1930 | 0.2124 |
| frame_det_rate | 0.7212 | 0.5818 | 0.4909 |
| frame_recall_V | 0.6989 | 0.5591 | 0.4731 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.7500 | 0.6111 | 0.5139 |
| cell_recall_V | 0.4271 | 0.3438 | 0.2643 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.4537 | 0.3380 | 0.2222 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.3485 | 0.2879 | 0.1515 |
| band3_cell_recall | 0.3780 | 0.2808 | 0.2126 |
| band4_cell_recall | 0.5061 | 0.4015 | 0.3000 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.1604 | 0.1021 | 0.0486 |
| band3_cell_fpr_off | 0.3361 | 0.2472 | 0.1715 |
| band4_cell_fpr_off | 0.5118 | 0.3653 | 0.2521 |
| frame_fa_off | 0.8438 | 0.7396 | 0.6424 |
| cell_fpr_off | 0.2521 | 0.1786 | 0.1181 |
| cell_fpr_on_neg | 0.2200 | 0.1502 | 0.0941 |
