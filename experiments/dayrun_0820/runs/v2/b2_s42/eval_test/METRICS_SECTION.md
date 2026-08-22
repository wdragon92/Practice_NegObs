# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.45 (fitted on **val**, val cell-F1 0.4756) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 2691 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6667 [0.5968, 0.7358] | 0.2578 [0.2191, 0.2985] | 180 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.0833 [0.0312, 0.1413] | 0.0340 [0.0110, 0.0607] | 96 |
| **any tier (frame detection rate)** | 0.3914 [0.3378, 0.4455] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2108 [0.1721, 0.2506] |
| cell FPR (off frames) | 0.0251 [0.0197, 0.0307] |
| cell FPR (negative cells of on frames) | 0.0442 [0.0345, 0.0542] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0714 [0.0329, 0.1192] | 0.0029 [0.0000, 0.0079] |
| 3a [5,8) m | 0.1540 [0.1180, 0.1928] | 0.0083 [0.0040, 0.0134] |
| 3b [8,12) m | 0.2534 [0.2142, 0.2943] | 0.0892 [0.0700, 0.1087] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2735 [0.2356, 0.3101] |
| cell recall | 0.1847 [0.1554, 0.2146] |
| cell precision | 0.5265 [0.4650, 0.5850] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.45

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6833 [0.6154, 0.7514] | 0.2733 [0.2334, 0.3159] | 180 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.0938 [0.0392, 0.1546] | 0.0425 [0.0161, 0.0713] | 96 |
| **any tier (frame detection rate)** | 0.4037 [0.3495, 0.4575] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2181 [0.1788, 0.2587] |
| cell FPR (off frames) | 0.0271 [0.0213, 0.0331] |
| cell FPR (negative cells of on frames) | 0.0481 [0.0377, 0.0585] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0820 [0.0404, 0.1322] | 0.0034 [0.0000, 0.0090] |
| 3a [5,8) m | 0.1644 [0.1262, 0.2053] | 0.0093 [0.0044, 0.0151] |
| 3b [8,12) m | 0.2685 [0.2275, 0.3109] | 0.0956 [0.0755, 0.1161] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2861 [0.2479, 0.3236] |
| cell recall | 0.1970 [0.1668, 0.2283] |
| cell precision | 0.5227 [0.4632, 0.5805] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3340 | 0.2735 | 0.2087 |
| cell_recall | 0.2482 | 0.1847 | 0.1282 |
| cell_precision | 0.5103 | 0.5265 | 0.5610 |
| frame_det_rate | 0.4343 | 0.3914 | 0.3609 |
| frame_recall_V | 0.6889 | 0.6667 | 0.6333 |
| frame_recall_E | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_H | 0.1875 | 0.0833 | 0.0417 |
| cell_recall_V | 0.3376 | 0.2578 | 0.1822 |
| cell_recall_E | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_H | 0.0807 | 0.0340 | 0.0106 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.1349 | 0.0714 | 0.0503 |
| band3_cell_recall | 0.2184 | 0.1540 | 0.0954 |
| band4_cell_recall | 0.3220 | 0.2534 | 0.1833 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0054 | 0.0029 | 0.0005 |
| band3_cell_fpr_off | 0.0162 | 0.0083 | 0.0044 |
| band4_cell_fpr_off | 0.1221 | 0.0892 | 0.0564 |
| frame_fa_off | 0.2525 | 0.2108 | 0.1618 |
| cell_fpr_off | 0.0359 | 0.0251 | 0.0153 |
| cell_fpr_on_neg | 0.0636 | 0.0442 | 0.0265 |
