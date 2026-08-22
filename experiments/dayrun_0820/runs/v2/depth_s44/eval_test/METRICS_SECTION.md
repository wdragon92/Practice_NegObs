# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.6 (fitted on **val**, val cell-F1 0.6568) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 2691 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9000 [0.8538, 0.9408] | 0.6849 [0.6367, 0.7293] | 180 |
| E | 0.6000 [0.4545, 0.7436] | 0.4224 [0.3486, 0.4864] | 45 |
| H | 0.4375 [0.3404, 0.5364] | 0.5223 [0.4288, 0.6070] | 96 |
| **any tier (frame detection rate)** | 0.7064 [0.6561, 0.7553] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0662 [0.0434, 0.0916] |
| cell FPR (off frames) | 0.0191 [0.0102, 0.0294] |
| cell FPR (negative cells of on frames) | 0.1256 [0.1007, 0.1522] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.2308 [0.1391, 0.3265] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.5476 [0.4457, 0.6433] | 0.0294 [0.0145, 0.0470] |
| 3a [5,8) m | 0.5276 [0.4604, 0.5927] | 0.0294 [0.0172, 0.0434] |
| 3b [8,12) m | 0.7376 [0.6937, 0.7779] | 0.0176 [0.0071, 0.0304] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6421 [0.6046, 0.6760] |
| cell recall | 0.6210 [0.5822, 0.6575] |
| cell precision | 0.6647 [0.6102, 0.7162] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.6

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8667 [0.8152, 0.9140] | 0.6013 [0.5504, 0.6478] | 180 |
| E | 0.6000 [0.4545, 0.7436] | 0.4052 [0.3354, 0.4654] | 45 |
| H | 0.4375 [0.3404, 0.5364] | 0.4650 [0.3721, 0.5482] | 96 |
| **any tier (frame detection rate)** | 0.6881 [0.6372, 0.7373] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0368 [0.0198, 0.0563] |
| cell FPR (off frames) | 0.0129 [0.0057, 0.0213] |
| cell FPR (negative cells of on frames) | 0.0954 [0.0734, 0.1194] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1282 [0.0809, 0.1793] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.4603 [0.3540, 0.5618] | 0.0235 [0.0111, 0.0378] |
| 3a [5,8) m | 0.4931 [0.4280, 0.5569] | 0.0176 [0.0075, 0.0295] |
| 3b [8,12) m | 0.6516 [0.6069, 0.6943] | 0.0103 [0.0029, 0.0196] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6175 [0.5797, 0.6522] |
| cell recall | 0.5507 [0.5110, 0.5880] |
| cell precision | 0.7027 [0.6446, 0.7567] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.6180 | 0.6421 | 0.5689 |
| cell_recall | 0.7269 | 0.6210 | 0.4693 |
| cell_precision | 0.5375 | 0.6647 | 0.7221 |
| frame_det_rate | 0.8165 | 0.7064 | 0.6606 |
| frame_recall_V | 1.0000 | 0.9000 | 0.8333 |
| frame_recall_E | 0.6000 | 0.6000 | 0.6000 |
| frame_recall_H | 0.5625 | 0.4375 | 0.4062 |
| cell_recall_V | 0.8119 | 0.6849 | 0.5161 |
| cell_recall_E | 0.4310 | 0.4224 | 0.3621 |
| cell_recall_H | 0.6051 | 0.5223 | 0.3694 |
| band1_cell_recall | 0.4872 | 0.2308 | 0.0513 |
| band2_cell_recall | 0.7540 | 0.5476 | 0.4206 |
| band3_cell_recall | 0.6241 | 0.5276 | 0.4310 |
| band4_cell_recall | 0.8077 | 0.7376 | 0.5452 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0574 | 0.0294 | 0.0147 |
| band3_cell_fpr_off | 0.1265 | 0.0294 | 0.0132 |
| band4_cell_fpr_off | 0.0588 | 0.0176 | 0.0088 |
| frame_fa_off | 0.2279 | 0.0662 | 0.0221 |
| cell_fpr_off | 0.0607 | 0.0191 | 0.0092 |
| cell_fpr_on_neg | 0.2172 | 0.1256 | 0.0752 |
