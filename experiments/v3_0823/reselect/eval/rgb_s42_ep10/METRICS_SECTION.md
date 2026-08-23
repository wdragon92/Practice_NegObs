# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/reselect/rgb_s42_repro/ep10.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.63 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 369 | 219 | 45 | 96 | 7 | 2856 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.5160 [0.4493, 0.5837] | 0.1588 [0.1311, 0.1883] | 219 |
| E | 0.1333 [0.0435, 0.2391] | 0.0287 [0.0072, 0.0556] | 45 |
| H | 0.1667 [0.0961, 0.2427] | 0.0382 [0.0219, 0.0552] | 96 |
| **any tier (frame detection rate)** | 0.3713 [0.3216, 0.4209] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0858 [0.0593, 0.1141] |
| cell FPR (off frames) | 0.0065 [0.0043, 0.0090] |
| cell FPR (negative cells of on frames) | 0.0232 [0.0179, 0.0290] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0635 [0.0242, 0.1117] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.1684 [0.1336, 0.2045] | 0.0152 [0.0088, 0.0225] |
| 3b [8,12) m | 0.1204 [0.0966, 0.1461] | 0.0108 [0.0057, 0.0168] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2075 [0.1754, 0.2396] |
| cell recall | 0.1229 [0.1021, 0.1448] |
| cell precision | 0.6660 [0.6000, 0.7271] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.63

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4064 [0.3411, 0.4737] | 0.1029 [0.0818, 0.1249] | 219 |
| E | 0.0444 [0.0000, 0.1154] | 0.0086 [0.0000, 0.0231] | 45 |
| H | 0.0833 [0.0319, 0.1429] | 0.0170 [0.0068, 0.0281] | 96 |
| **any tier (frame detection rate)** | 0.2683 [0.2229, 0.3152] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0466 [0.0270, 0.0682] |
| cell FPR (off frames) | 0.0036 [0.0019, 0.0054] |
| cell FPR (negative cells of on frames) | 0.0151 [0.0110, 0.0196] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0238 [0.0000, 0.0580] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.1100 [0.0845, 0.1370] | 0.0098 [0.0046, 0.0159] |
| 3b [8,12) m | 0.0762 [0.0574, 0.0963] | 0.0044 [0.0015, 0.0082] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1376 [0.1114, 0.1643] |
| cell recall | 0.0767 [0.0611, 0.0930] |
| cell precision | 0.6677 [0.5905, 0.7372] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3561 | 0.2075 | 0.1057 |
| cell_recall | 0.2482 | 0.1229 | 0.0574 |
| cell_precision | 0.6297 | 0.6660 | 0.6667 |
| frame_det_rate | 0.6125 | 0.3713 | 0.2358 |
| frame_recall_V | 0.7260 | 0.5160 | 0.3607 |
| frame_recall_E | 0.4444 | 0.1333 | 0.0444 |
| frame_recall_H | 0.4062 | 0.1667 | 0.0625 |
| cell_recall_V | 0.2967 | 0.1588 | 0.0772 |
| cell_recall_E | 0.1351 | 0.0287 | 0.0057 |
| cell_recall_H | 0.1146 | 0.0382 | 0.0127 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.1825 | 0.0635 | 0.0132 |
| band3_cell_recall | 0.2952 | 0.1684 | 0.0842 |
| band4_cell_recall | 0.2565 | 0.1204 | 0.0571 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0382 | 0.0152 | 0.0054 |
| band4_cell_fpr_off | 0.0490 | 0.0108 | 0.0039 |
| frame_fa_off | 0.2132 | 0.0858 | 0.0270 |
| cell_fpr_off | 0.0218 | 0.0065 | 0.0023 |
| cell_fpr_on_neg | 0.0451 | 0.0232 | 0.0119 |
