# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `runs/yolo_s42/cells_test/per_frame.csv`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.25 · tau_star = 0.25 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 2691 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.25

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.1167 [0.0714, 0.1657] | 0.0182 [0.0108, 0.0264] | 180 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 96 |
| **any tier (frame detection rate)** | 0.0642 [0.0388, 0.0923] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0049 [0.0000, 0.0125] |
| cell FPR (off frames) | 0.0004 [0.0000, 0.0010] |
| cell FPR (negative cells of on frames) | 0.0035 [0.0017, 0.0057] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1026 [0.0412, 0.1731] | 0.0005 [0.0000, 0.0015] |
| 2 [2,5) m | 0.0476 [0.0202, 0.0797] | 0.0010 [0.0000, 0.0031] |
| 3a [5,8) m | 0.0023 [0.0000, 0.0059] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.0015 [0.0000, 0.0039] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0248 [0.0145, 0.0360] |
| cell recall | 0.0126 [0.0073, 0.0185] |
| cell precision | 0.6071 [0.4286, 0.7692] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.25

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.1167 [0.0714, 0.1657] | 0.0182 [0.0108, 0.0264] | 180 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 96 |
| **any tier (frame detection rate)** | 0.0642 [0.0388, 0.0923] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0049 [0.0000, 0.0125] |
| cell FPR (off frames) | 0.0004 [0.0000, 0.0010] |
| cell FPR (negative cells of on frames) | 0.0035 [0.0017, 0.0057] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1026 [0.0412, 0.1731] | 0.0005 [0.0000, 0.0015] |
| 2 [2,5) m | 0.0476 [0.0202, 0.0797] | 0.0010 [0.0000, 0.0031] |
| 3a [5,8) m | 0.0023 [0.0000, 0.0059] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.0015 [0.0000, 0.0039] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0248 [0.0145, 0.0360] |
| cell recall | 0.0126 [0.0073, 0.0185] |
| cell precision | 0.6071 [0.4286, 0.7692] |

## 2. Threshold sweep

| metric | tau=0.1 | tau=0.25 | tau=0.5 |
|---|---|---|---|
| cell_f1 | 0.0330 | 0.0248 | 0.0096 |
| cell_recall | 0.0171 | 0.0126 | 0.0048 |
| cell_precision | 0.4600 | 0.6071 | 0.6842 |
| frame_det_rate | 0.0887 | 0.0642 | 0.0306 |
| frame_recall_V | 0.1556 | 0.1167 | 0.0556 |
| frame_recall_E | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_H | 0.0104 | 0.0000 | 0.0000 |
| cell_recall_V | 0.0241 | 0.0182 | 0.0070 |
| cell_recall_E | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_H | 0.0021 | 0.0000 | 0.0000 |
| band1_cell_recall | 0.1624 | 0.1026 | 0.0342 |
| band2_cell_recall | 0.0529 | 0.0476 | 0.0238 |
| band3_cell_recall | 0.0034 | 0.0023 | 0.0000 |
| band4_cell_recall | 0.0030 | 0.0015 | 0.0000 |
| band1_cell_fpr_off | 0.0015 | 0.0005 | 0.0000 |
| band2_cell_fpr_off | 0.0015 | 0.0010 | 0.0000 |
| band3_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| frame_fa_off | 0.0098 | 0.0049 | 0.0000 |
| cell_fpr_off | 0.0007 | 0.0004 | 0.0000 |
| cell_fpr_on_neg | 0.0088 | 0.0035 | 0.0011 |
