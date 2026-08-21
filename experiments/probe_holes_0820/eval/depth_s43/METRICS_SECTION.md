# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **probe** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 144 | 72 | 72 | 72 | 15 | 27 | 30 | 3 | 189 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 15 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 27 |
| H | 0.5000 [0.3200, 0.6786] | 0.4815 [0.2857, 0.6809] | 30 |
| **any tier (frame detection rate)** | 0.2083 [0.1176, 0.3065] | — | 72 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2500 [0.1528, 0.3553] |
| cell FPR (off frames) | 0.1354 [0.0743, 0.2020] |
| cell FPR (negative cells of on frames) | 0.1391 [0.0833, 0.2002] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2895 [0.1630, 0.4184] | 0.1750 [0.0928, 0.2656] |
| 3a [5,8) m | 0.2000 [0.0000, 0.4118] | 0.1833 [0.1000, 0.2735] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.1833 [0.1041, 0.2704] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1307 [0.0768, 0.1805] |
| cell recall | 0.2063 [0.1092, 0.3116] |
| cell precision | 0.0956 [0.0570, 0.1342] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 15 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 27 |
| H | 0.5000 [0.3200, 0.6786] | 0.4815 [0.2857, 0.6809] | 30 |
| **any tier (frame detection rate)** | 0.2083 [0.1176, 0.3065] | — | 72 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2500 [0.1528, 0.3553] |
| cell FPR (off frames) | 0.1354 [0.0743, 0.2020] |
| cell FPR (negative cells of on frames) | 0.1391 [0.0833, 0.2002] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2895 [0.1630, 0.4184] | 0.1750 [0.0928, 0.2656] |
| 3a [5,8) m | 0.2000 [0.0000, 0.4118] | 0.1833 [0.1000, 0.2735] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.1833 [0.1041, 0.2704] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1307 [0.0768, 0.1805] |
| cell recall | 0.2063 [0.1092, 0.3116] |
| cell precision | 0.0956 [0.0570, 0.1342] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.1256 | 0.1307 | 0.1379 |
| cell_recall | 0.2222 | 0.2063 | 0.1905 |
| cell_precision | 0.0875 | 0.0956 | 0.1081 |
| frame_det_rate | 0.2083 | 0.2083 | 0.1667 |
| frame_recall_V | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_E | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_H | 0.5000 | 0.5000 | 0.4000 |
| cell_recall_V | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_E | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_H | 0.5185 | 0.4815 | 0.4444 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.3158 | 0.2895 | 0.2632 |
| band3_cell_recall | 0.2000 | 0.2000 | 0.2000 |
| band4_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band1_cell_fpr_off | 0.0333 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.1917 | 0.1750 | 0.1500 |
| band3_cell_fpr_off | 0.2083 | 0.1833 | 0.1667 |
| band4_cell_fpr_off | 0.2000 | 0.1833 | 0.1417 |
| frame_fa_off | 0.2917 | 0.2500 | 0.1667 |
| cell_fpr_off | 0.1583 | 0.1354 | 0.1146 |
| cell_fpr_on_neg | 0.1679 | 0.1391 | 0.1055 |
