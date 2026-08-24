# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/runs/v3a/rgb_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4301 [0.3333, 0.5349] | 0.3451 [0.2670, 0.4228] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.3750 [0.2625, 0.4865] | 0.1389 [0.0780, 0.2126] | 72 |
| **any tier (frame detection rate)** | 0.4061 [0.3312, 0.4823] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.5972 [0.5396, 0.6532] |
| cell FPR (off frames) | 0.1852 [0.1588, 0.2121] |
| cell FPR (negative cells of on frames) | 0.1798 [0.1516, 0.2085] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0007 [0.0000, 0.0022] |
| 2 [2,5) m | 0.2652 [0.1210, 0.4322] | 0.1514 [0.1151, 0.1891] |
| 3a [5,8) m | 0.3412 [0.2552, 0.4311] | 0.2687 [0.2244, 0.3143] |
| 3b [8,12) m | 0.2424 [0.1857, 0.3013] | 0.3201 [0.2812, 0.3601] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1905 [0.1452, 0.2378] |
| cell recall | 0.2708 [0.2123, 0.3321] |
| cell precision | 0.1469 [0.1083, 0.1902] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4301 [0.3333, 0.5349] | 0.3451 [0.2670, 0.4228] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.3750 [0.2625, 0.4865] | 0.1389 [0.0780, 0.2126] | 72 |
| **any tier (frame detection rate)** | 0.4061 [0.3312, 0.4823] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.5972 [0.5396, 0.6532] |
| cell FPR (off frames) | 0.1852 [0.1588, 0.2121] |
| cell FPR (negative cells of on frames) | 0.1798 [0.1516, 0.2085] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0007 [0.0000, 0.0022] |
| 2 [2,5) m | 0.2652 [0.1210, 0.4322] | 0.1514 [0.1151, 0.1891] |
| 3a [5,8) m | 0.3412 [0.2552, 0.4311] | 0.2687 [0.2244, 0.3143] |
| 3b [8,12) m | 0.2424 [0.1857, 0.3013] | 0.3201 [0.2812, 0.3601] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1905 [0.1452, 0.2378] |
| cell recall | 0.2708 [0.2123, 0.3321] |
| cell precision | 0.1469 [0.1083, 0.1902] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.2032 | 0.1905 | 0.1726 |
| cell_recall | 0.3475 | 0.2708 | 0.2008 |
| cell_precision | 0.1435 | 0.1469 | 0.1513 |
| frame_det_rate | 0.4909 | 0.4061 | 0.3333 |
| frame_recall_V | 0.4516 | 0.4301 | 0.4086 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.5417 | 0.3750 | 0.2361 |
| cell_recall_V | 0.4193 | 0.3451 | 0.2578 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.2199 | 0.1389 | 0.0995 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.3636 | 0.2652 | 0.1894 |
| band3_cell_recall | 0.4304 | 0.3412 | 0.2572 |
| band4_cell_recall | 0.3106 | 0.2424 | 0.1788 |
| band1_cell_fpr_off | 0.0007 | 0.0007 | 0.0000 |
| band2_cell_fpr_off | 0.2194 | 0.1514 | 0.0896 |
| band3_cell_fpr_off | 0.3375 | 0.2687 | 0.2188 |
| band4_cell_fpr_off | 0.4062 | 0.3201 | 0.2326 |
| frame_fa_off | 0.6632 | 0.5972 | 0.4896 |
| cell_fpr_off | 0.2410 | 0.1852 | 0.1352 |
| cell_fpr_on_neg | 0.2412 | 0.1798 | 0.1257 |
