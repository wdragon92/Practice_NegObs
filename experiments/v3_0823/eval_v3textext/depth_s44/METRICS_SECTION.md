# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.6 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4839 [0.3837, 0.5865] | 0.5312 [0.4500, 0.6041] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.6667 [0.5571, 0.7750] | 0.4722 [0.3907, 0.5533] | 72 |
| **any tier (frame detection rate)** | 0.5636 [0.4897, 0.6402] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2292 [0.1815, 0.2785] |
| cell FPR (off frames) | 0.0948 [0.0706, 0.1204] |
| cell FPR (negative cells of on frames) | 0.0513 [0.0346, 0.0697] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.2222 [0.0000, 0.4000] | 0.0083 [0.0000, 0.0190] |
| 2 [2,5) m | 0.5455 [0.3580, 0.7230] | 0.0979 [0.0671, 0.1315] |
| 3a [5,8) m | 0.4724 [0.3872, 0.5573] | 0.1208 [0.0877, 0.1557] |
| 3b [8,12) m | 0.5364 [0.4731, 0.5978] | 0.1521 [0.1157, 0.1903] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4722 [0.4079, 0.5324] |
| cell recall | 0.5100 [0.4514, 0.5666] |
| cell precision | 0.4397 [0.3614, 0.5200] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.6

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4839 [0.3837, 0.5865] | 0.4883 [0.4101, 0.5579] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.6667 [0.5571, 0.7750] | 0.4236 [0.3469, 0.5000] | 72 |
| **any tier (frame detection rate)** | 0.5636 [0.4897, 0.6402] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2083 [0.1632, 0.2563] |
| cell FPR (off frames) | 0.0786 [0.0562, 0.1027] |
| cell FPR (negative cells of on frames) | 0.0355 [0.0210, 0.0522] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1111 [0.0000, 0.2000] | 0.0063 [0.0000, 0.0142] |
| 2 [2,5) m | 0.4773 [0.2920, 0.6579] | 0.0729 [0.0455, 0.1031] |
| 3a [5,8) m | 0.3937 [0.3133, 0.4744] | 0.1021 [0.0719, 0.1344] |
| 3b [8,12) m | 0.5182 [0.4554, 0.5791] | 0.1333 [0.1003, 0.1687] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4703 [0.4067, 0.5291] |
| cell recall | 0.4650 [0.4087, 0.5194] |
| cell precision | 0.4757 [0.3900, 0.5638] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4632 | 0.4722 | 0.4558 |
| cell_recall | 0.6050 | 0.5100 | 0.4125 |
| cell_precision | 0.3752 | 0.4397 | 0.5093 |
| frame_det_rate | 0.6000 | 0.5636 | 0.5455 |
| frame_recall_V | 0.4839 | 0.4839 | 0.4839 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.7500 | 0.6667 | 0.6250 |
| cell_recall_V | 0.5938 | 0.5312 | 0.4570 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.6250 | 0.4722 | 0.3333 |
| band1_cell_recall | 0.4444 | 0.2222 | 0.1111 |
| band2_cell_recall | 0.5682 | 0.5455 | 0.4545 |
| band3_cell_recall | 0.6063 | 0.4724 | 0.3622 |
| band4_cell_recall | 0.6182 | 0.5364 | 0.4455 |
| band1_cell_fpr_off | 0.0125 | 0.0083 | 0.0063 |
| band2_cell_fpr_off | 0.1333 | 0.0979 | 0.0583 |
| band3_cell_fpr_off | 0.1833 | 0.1208 | 0.0771 |
| band4_cell_fpr_off | 0.2208 | 0.1521 | 0.1146 |
| frame_fa_off | 0.3125 | 0.2292 | 0.1875 |
| cell_fpr_off | 0.1375 | 0.0948 | 0.0641 |
| cell_fpr_on_neg | 0.0914 | 0.0513 | 0.0237 |
