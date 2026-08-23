# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.45 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 369 | 219 | 45 | 96 | 7 | 2856 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6712 [0.6085, 0.7323] | 0.2666 [0.2299, 0.3052] | 219 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.0833 [0.0312, 0.1413] | 0.0340 [0.0110, 0.0607] | 96 |
| **any tier (frame detection rate)** | 0.4201 [0.3693, 0.4711] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2108 [0.1721, 0.2506] |
| cell FPR (off frames) | 0.0251 [0.0197, 0.0307] |
| cell FPR (negative cells of on frames) | 0.0347 [0.0262, 0.0433] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0714 [0.0329, 0.1192] | 0.0029 [0.0000, 0.0079] |
| 3a [5,8) m | 0.1526 [0.1173, 0.1907] | 0.0083 [0.0040, 0.0134] |
| 3b [8,12) m | 0.2667 [0.2295, 0.3049] | 0.0892 [0.0700, 0.1087] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2921 [0.2557, 0.3273] |
| cell recall | 0.1943 [0.1661, 0.2233] |
| cell precision | 0.5879 [0.5329, 0.6402] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.45

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6895 [0.6270, 0.7511] | 0.2834 [0.2454, 0.3238] | 219 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.0938 [0.0392, 0.1546] | 0.0425 [0.0161, 0.0713] | 96 |
| **any tier (frame detection rate)** | 0.4336 [0.3831, 0.4855] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2181 [0.1788, 0.2587] |
| cell FPR (off frames) | 0.0271 [0.0213, 0.0331] |
| cell FPR (negative cells of on frames) | 0.0377 [0.0287, 0.0470] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0820 [0.0404, 0.1322] | 0.0034 [0.0000, 0.0090] |
| 3a [5,8) m | 0.1639 [0.1261, 0.2041] | 0.0093 [0.0044, 0.0151] |
| 3b [8,12) m | 0.2830 [0.2444, 0.3221] | 0.0956 [0.0755, 0.1161] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3065 [0.2698, 0.3425] |
| cell recall | 0.2076 [0.1784, 0.2381] |
| cell precision | 0.5848 [0.5311, 0.6370] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3611 | 0.2921 | 0.2184 |
| cell_recall | 0.2633 | 0.1943 | 0.1327 |
| cell_precision | 0.5745 | 0.5879 | 0.6163 |
| frame_det_rate | 0.4661 | 0.4201 | 0.3740 |
| frame_recall_V | 0.7032 | 0.6712 | 0.6119 |
| frame_recall_E | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_H | 0.1875 | 0.0833 | 0.0417 |
| cell_recall_V | 0.3531 | 0.2666 | 0.1850 |
| cell_recall_E | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_H | 0.0807 | 0.0340 | 0.0106 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.1349 | 0.0714 | 0.0503 |
| band3_cell_recall | 0.2200 | 0.1526 | 0.0943 |
| band4_cell_recall | 0.3435 | 0.2667 | 0.1878 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0054 | 0.0029 | 0.0005 |
| band3_cell_fpr_off | 0.0162 | 0.0083 | 0.0044 |
| band4_cell_fpr_off | 0.1221 | 0.0892 | 0.0564 |
| frame_fa_off | 0.2525 | 0.2108 | 0.1618 |
| cell_fpr_off | 0.0359 | 0.0251 | 0.0153 |
| cell_fpr_on_neg | 0.0498 | 0.0347 | 0.0209 |
