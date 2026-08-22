# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/rgb_s43/best.pt`
grid: **PROVISIONAL-GRID-V2S** (4 bands x 10 sectors = 40 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.42 (fitted on **val**, val cell-F1 0.4782) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 4998 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6278 [0.5574, 0.6978] | 0.4660 [0.3945, 0.5359] | 180 |
| E | 0.3556 [0.2162, 0.5000] | 0.1985 [0.1027, 0.3008] | 45 |
| H | 0.2083 [0.1294, 0.2927] | 0.0836 [0.0341, 0.1449] | 96 |
| **any tier (frame detection rate)** | 0.4587 [0.4044, 0.5138] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1544 [0.1195, 0.1891] |
| cell FPR (off frames) | 0.0221 [0.0153, 0.0297] |
| cell FPR (negative cells of on frames) | 0.0823 [0.0663, 0.0993] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0311 [0.0000, 0.0687] | 0.0034 [0.0000, 0.0086] |
| 2 [2,5) m | 0.4972 [0.3939, 0.5987] | 0.0235 [0.0115, 0.0371] |
| 3a [5,8) m | 0.4035 [0.3375, 0.4685] | 0.0277 [0.0164, 0.0403] |
| 3b [8,12) m | 0.3358 [0.2860, 0.3854] | 0.0338 [0.0232, 0.0456] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4513 [0.3961, 0.5005] |
| cell recall | 0.3667 [0.3121, 0.4200] |
| cell precision | 0.5864 [0.5251, 0.6432] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.42

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.7389 [0.6724, 0.8031] | 0.5157 [0.4443, 0.5860] | 180 |
| E | 0.4444 [0.2979, 0.5918] | 0.2800 [0.1655, 0.3986] | 45 |
| H | 0.2708 [0.1858, 0.3619] | 0.1169 [0.0568, 0.1881] | 96 |
| **any tier (frame detection rate)** | 0.5596 [0.5050, 0.6128] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2475 [0.2055, 0.2900] |
| cell FPR (off frames) | 0.0372 [0.0282, 0.0468] |
| cell FPR (negative cells of on frames) | 0.1149 [0.0971, 0.1333] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0622 [0.0142, 0.1197] | 0.0051 [0.0002, 0.0115] |
| 2 [2,5) m | 0.5252 [0.4216, 0.6261] | 0.0341 [0.0195, 0.0503] |
| 3a [5,8) m | 0.4486 [0.3825, 0.5130] | 0.0404 [0.0257, 0.0560] |
| 3b [8,12) m | 0.4007 [0.3497, 0.4523] | 0.0691 [0.0541, 0.0853] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4650 [0.4131, 0.5118] |
| cell recall | 0.4186 [0.3631, 0.4728] |
| cell precision | 0.5230 [0.4675, 0.5756] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4663 | 0.4513 | 0.3557 |
| cell_recall | 0.5078 | 0.3667 | 0.2391 |
| cell_precision | 0.4310 | 0.5864 | 0.6940 |
| frame_det_rate | 0.6881 | 0.4587 | 0.2875 |
| frame_recall_V | 0.8444 | 0.6278 | 0.4667 |
| frame_recall_E | 0.5778 | 0.3556 | 0.1333 |
| frame_recall_H | 0.4271 | 0.2083 | 0.0417 |
| cell_recall_V | 0.6063 | 0.4660 | 0.3253 |
| cell_recall_E | 0.3896 | 0.1985 | 0.0637 |
| cell_recall_H | 0.1747 | 0.0836 | 0.0172 |
| band1_cell_recall | 0.1644 | 0.0311 | 0.0000 |
| band2_cell_recall | 0.5658 | 0.4972 | 0.4230 |
| band3_cell_recall | 0.5263 | 0.4035 | 0.2732 |
| band4_cell_recall | 0.5104 | 0.3358 | 0.1855 |
| band1_cell_fpr_off | 0.0074 | 0.0034 | 0.0010 |
| band2_cell_fpr_off | 0.0574 | 0.0235 | 0.0115 |
| band3_cell_fpr_off | 0.0735 | 0.0277 | 0.0032 |
| band4_cell_fpr_off | 0.1632 | 0.0338 | 0.0076 |
| frame_fa_off | 0.3627 | 0.1544 | 0.0539 |
| cell_fpr_off | 0.0754 | 0.0221 | 0.0058 |
| cell_fpr_on_neg | 0.1872 | 0.0823 | 0.0382 |
