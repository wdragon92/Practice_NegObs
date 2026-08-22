# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 24 | 24 | 0 | 0 | 1 | 129 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.4574 [0.4046, 0.5064] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.1271 [0.1077, 0.1500] |
| cell FPR (negative cells of on frames) | 0.0256 [0.0110, 0.0424] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.5385 [0.3846, 0.6552] | 0.1583 [0.0769, 0.2462] |
| 3b [8,12) m | 0.4222 [0.3412, 0.4906] | 0.3500 [0.2750, 0.4182] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4574 [0.3679, 0.5283] |
| cell recall | 0.4574 [0.4046, 0.5064] |
| cell precision | 0.4574 [0.3185, 0.5926] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.4574 [0.4046, 0.5064] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.1271 [0.1077, 0.1500] |
| cell FPR (negative cells of on frames) | 0.0256 [0.0110, 0.0424] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.5385 [0.3846, 0.6552] | 0.1583 [0.0769, 0.2462] |
| 3b [8,12) m | 0.4222 [0.3412, 0.4906] | 0.3500 [0.2750, 0.4182] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4574 [0.3679, 0.5283] |
| cell recall | 0.4574 [0.4046, 0.5064] |
| cell precision | 0.4574 [0.3185, 0.5926] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4535 | 0.4574 | 0.4640 |
| cell_recall | 0.4729 | 0.4574 | 0.4496 |
| cell_precision | 0.4357 | 0.4574 | 0.4793 |
| frame_det_rate | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_V | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | n/a | n/a | n/a |
| cell_recall_V | 0.4729 | 0.4574 | 0.4496 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | n/a | n/a | n/a |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | 0.5385 | 0.5385 | 0.5385 |
| band4_cell_recall | 0.4444 | 0.4222 | 0.4111 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.1583 | 0.1583 | 0.1583 |
| band4_cell_fpr_off | 0.3833 | 0.3500 | 0.3250 |
| frame_fa_off | 1.0000 | 1.0000 | 1.0000 |
| cell_fpr_off | 0.1354 | 0.1271 | 0.1208 |
| cell_fpr_on_neg | 0.0399 | 0.0256 | 0.0142 |
