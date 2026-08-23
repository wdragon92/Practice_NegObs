# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.6 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 369 | 219 | 45 | 96 | 7 | 2856 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8904 [0.8472, 0.9302] | 0.7018 [0.6562, 0.7445] | 219 |
| E | 0.6000 [0.4545, 0.7436] | 0.4224 [0.3486, 0.4864] | 45 |
| H | 0.4375 [0.3404, 0.5364] | 0.5223 [0.4288, 0.6070] | 96 |
| **any tier (frame detection rate)** | 0.7236 [0.6769, 0.7679] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0662 [0.0434, 0.0916] |
| cell FPR (off frames) | 0.0191 [0.0102, 0.0294] |
| cell FPR (negative cells of on frames) | 0.1018 [0.0816, 0.1236] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.2308 [0.1391, 0.3265] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.5476 [0.4457, 0.6433] | 0.0294 [0.0145, 0.0470] |
| 3a [5,8) m | 0.5387 [0.4719, 0.6032] | 0.0294 [0.0172, 0.0434] |
| 3b [8,12) m | 0.7510 [0.7107, 0.7884] | 0.0176 [0.0071, 0.0304] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6771 [0.6460, 0.7052] |
| cell recall | 0.6366 [0.5998, 0.6711] |
| cell precision | 0.7232 [0.6785, 0.7655] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.6

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8630 [0.8155, 0.9067] | 0.6098 [0.5623, 0.6535] | 219 |
| E | 0.6000 [0.4545, 0.7436] | 0.4052 [0.3354, 0.4654] | 45 |
| H | 0.4375 [0.3404, 0.5364] | 0.4650 [0.3721, 0.5482] | 96 |
| **any tier (frame detection rate)** | 0.7073 [0.6601, 0.7527] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0368 [0.0198, 0.0563] |
| cell FPR (off frames) | 0.0129 [0.0057, 0.0213] |
| cell FPR (negative cells of on frames) | 0.0769 [0.0596, 0.0959] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1282 [0.0809, 0.1793] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.4603 [0.3540, 0.5618] | 0.0235 [0.0111, 0.0378] |
| 3a [5,8) m | 0.5051 [0.4403, 0.5678] | 0.0176 [0.0075, 0.0295] |
| 3b [8,12) m | 0.6510 [0.6095, 0.6906] | 0.0103 [0.0029, 0.0196] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6429 [0.6106, 0.6727] |
| cell recall | 0.5588 [0.5213, 0.5946] |
| cell precision | 0.7568 [0.7111, 0.8001] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.6522 | 0.6771 | 0.5876 |
| cell_recall | 0.7416 | 0.6366 | 0.4737 |
| cell_precision | 0.5820 | 0.7232 | 0.7736 |
| frame_det_rate | 0.8374 | 0.7236 | 0.6585 |
| frame_recall_V | 1.0000 | 0.8904 | 0.8082 |
| frame_recall_E | 0.6000 | 0.6000 | 0.6000 |
| frame_recall_H | 0.5625 | 0.4375 | 0.4062 |
| cell_recall_V | 0.8249 | 0.7018 | 0.5208 |
| cell_recall_E | 0.4310 | 0.4224 | 0.3621 |
| cell_recall_H | 0.6051 | 0.5223 | 0.3694 |
| band1_cell_recall | 0.4872 | 0.2308 | 0.0513 |
| band2_cell_recall | 0.7540 | 0.5476 | 0.4206 |
| band3_cell_recall | 0.6330 | 0.5387 | 0.4444 |
| band4_cell_recall | 0.8245 | 0.7510 | 0.5388 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0574 | 0.0294 | 0.0147 |
| band3_cell_fpr_off | 0.1265 | 0.0294 | 0.0132 |
| band4_cell_fpr_off | 0.0588 | 0.0176 | 0.0088 |
| frame_fa_off | 0.2279 | 0.0662 | 0.0221 |
| cell_fpr_off | 0.0607 | 0.0191 | 0.0092 |
| cell_fpr_on_neg | 0.1934 | 0.1018 | 0.0605 |
