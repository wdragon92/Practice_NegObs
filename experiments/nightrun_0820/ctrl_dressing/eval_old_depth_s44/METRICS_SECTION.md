# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/nightrun_0820/ctrl_dressing/eval_old_depth_s44/per_frame_src.csv`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 96 | 48 | 48 | 24 | 24 | 0 | 0 | 2 | 237 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.5696 [0.4405, 0.7000] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1875 [0.0833, 0.3061] |
| cell FPR (off frames) | 0.1000 [0.0362, 0.1727] |
| cell FPR (negative cells of on frames) | 0.0581 [0.0286, 0.0950] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.1765 [0.0000, 0.3507] | 0.1250 [0.0400, 0.2250] |
| 3a [5,8) m | 0.5185 [0.3483, 0.6923] | 0.1375 [0.0553, 0.2304] |
| 3b [8,12) m | 0.8000 [0.6706, 0.9140] | 0.1375 [0.0500, 0.2383] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5294 [0.4087, 0.6311] |
| cell recall | 0.5696 [0.4405, 0.7000] |
| cell precision | 0.4945 [0.3409, 0.6585] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.5696 [0.4405, 0.7000] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1875 [0.0833, 0.3061] |
| cell FPR (off frames) | 0.1000 [0.0362, 0.1727] |
| cell FPR (negative cells of on frames) | 0.0581 [0.0286, 0.0950] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.1765 [0.0000, 0.3507] | 0.1250 [0.0400, 0.2250] |
| 3a [5,8) m | 0.5185 [0.3483, 0.6923] | 0.1375 [0.0553, 0.2304] |
| 3b [8,12) m | 0.8000 [0.6706, 0.9140] | 0.1375 [0.0500, 0.2383] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5294 [0.4087, 0.6311] |
| cell recall | 0.5696 [0.4405, 0.7000] |
| cell precision | 0.4945 [0.3409, 0.6585] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5981 | 0.5294 | 0.2812 |
| cell_recall | 0.8101 | 0.5696 | 0.2278 |
| cell_precision | 0.4741 | 0.4945 | 0.3673 |
| frame_det_rate | 1.0000 | 1.0000 | 0.8750 |
| frame_recall_V | 1.0000 | 1.0000 | 0.8750 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | n/a | n/a | n/a |
| cell_recall_V | 0.8101 | 0.5696 | 0.2278 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | n/a | n/a | n/a |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | 0.6471 | 0.1765 | 0.0000 |
| band3_cell_recall | 0.7407 | 0.5185 | 0.2222 |
| band4_cell_recall | 0.9429 | 0.8000 | 0.3429 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.1875 | 0.1250 | 0.1250 |
| band3_cell_fpr_off | 0.1875 | 0.1375 | 0.1000 |
| band4_cell_fpr_off | 0.2375 | 0.1375 | 0.0750 |
| frame_fa_off | 0.3750 | 0.1875 | 0.1250 |
| cell_fpr_off | 0.1531 | 0.1000 | 0.0750 |
| cell_fpr_on_neg | 0.0913 | 0.0581 | 0.0290 |
