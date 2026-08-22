# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/rgb_s42/best.pt`
grid: **PROVISIONAL-GRID-V2S** (4 bands x 10 sectors = 40 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.43 (fitted on **val**, val cell-F1 0.5549) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 4998 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6278 [0.5561, 0.6979] | 0.2327 [0.1808, 0.2877] | 180 |
| E | 0.2000 [0.0870, 0.3250] | 0.0785 [0.0296, 0.1358] | 45 |
| H | 0.7188 [0.6264, 0.8061] | 0.2362 [0.1785, 0.3026] | 96 |
| **any tier (frame detection rate)** | 0.5994 [0.5452, 0.6520] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2206 [0.1810, 0.2615] |
| cell FPR (off frames) | 0.0171 [0.0133, 0.0212] |
| cell FPR (negative cells of on frames) | 0.0778 [0.0657, 0.0907] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0267 [0.0000, 0.0663] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2073 [0.1267, 0.2941] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.1992 [0.1513, 0.2494] | 0.0235 [0.0134, 0.0352] |
| 3b [8,12) m | 0.2416 [0.2071, 0.2779] | 0.0449 [0.0339, 0.0569] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2954 [0.2489, 0.3415] |
| cell recall | 0.2135 [0.1747, 0.2538] |
| cell precision | 0.4791 [0.4138, 0.5413] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.43

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.7000 [0.6313, 0.7657] | 0.2733 [0.2183, 0.3316] | 180 |
| E | 0.3111 [0.1750, 0.4500] | 0.1141 [0.0525, 0.1842] | 45 |
| H | 0.8333 [0.7551, 0.9062] | 0.3173 [0.2502, 0.3938] | 96 |
| **any tier (frame detection rate)** | 0.6911 [0.6399, 0.7411] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2574 [0.2145, 0.3000] |
| cell FPR (off frames) | 0.0240 [0.0193, 0.0290] |
| cell FPR (negative cells of on frames) | 0.0945 [0.0810, 0.1089] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0356 [0.0000, 0.0915] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2381 [0.1507, 0.3299] | 0.0005 [0.0000, 0.0013] |
| 3a [5,8) m | 0.2350 [0.1826, 0.2895] | 0.0333 [0.0215, 0.0464] |
| 3b [8,12) m | 0.3037 [0.2664, 0.3425] | 0.0623 [0.0485, 0.0770] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3353 [0.2890, 0.3806] |
| cell recall | 0.2603 [0.2187, 0.3038] |
| cell precision | 0.4709 [0.4111, 0.5283] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3948 | 0.2954 | 0.1692 |
| cell_recall | 0.3587 | 0.2135 | 0.1016 |
| cell_precision | 0.4389 | 0.4791 | 0.5050 |
| frame_det_rate | 0.7798 | 0.5994 | 0.3425 |
| frame_recall_V | 0.7778 | 0.6278 | 0.4056 |
| frame_recall_E | 0.4667 | 0.2000 | 0.0889 |
| frame_recall_H | 0.9167 | 0.7188 | 0.3229 |
| cell_recall_V | 0.3559 | 0.2327 | 0.1209 |
| cell_recall_E | 0.2281 | 0.0785 | 0.0193 |
| cell_recall_H | 0.4711 | 0.2362 | 0.0800 |
| band1_cell_recall | 0.0667 | 0.0267 | 0.0000 |
| band2_cell_recall | 0.2843 | 0.2073 | 0.1499 |
| band3_cell_recall | 0.3127 | 0.1992 | 0.1015 |
| band4_cell_recall | 0.4369 | 0.2416 | 0.0970 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0051 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0615 | 0.0235 | 0.0093 |
| band4_cell_fpr_off | 0.1216 | 0.0449 | 0.0110 |
| frame_fa_off | 0.3824 | 0.2206 | 0.0980 |
| cell_fpr_off | 0.0471 | 0.0171 | 0.0051 |
| cell_fpr_on_neg | 0.1346 | 0.0778 | 0.0367 |
