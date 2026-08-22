# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 24 | 24 | 0 | 0 | 1 | 129 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9583 [0.8571, 1.0000] | 0.4651 [0.3520, 0.5764] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 0.9583 [0.8571, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.1333 [0.1152, 0.1553] |
| cell FPR (negative cells of on frames) | 0.1368 [0.0897, 0.1926] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.7179 [0.5806, 0.8537] | 0.1583 [0.0842, 0.2400] |
| 3b [8,12) m | 0.3556 [0.2439, 0.4667] | 0.3750 [0.2960, 0.4480] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3987 [0.2951, 0.4779] |
| cell recall | 0.4651 [0.3520, 0.5764] |
| cell precision | 0.3488 [0.2431, 0.4360] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9583 [0.8571, 1.0000] | 0.4651 [0.3520, 0.5764] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 0.9583 [0.8571, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.1333 [0.1152, 0.1553] |
| cell FPR (negative cells of on frames) | 0.1368 [0.0897, 0.1926] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.7179 [0.5806, 0.8537] | 0.1583 [0.0842, 0.2400] |
| 3b [8,12) m | 0.3556 [0.2439, 0.4667] | 0.3750 [0.2960, 0.4480] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3987 [0.2951, 0.4779] |
| cell recall | 0.4651 [0.3520, 0.5764] |
| cell precision | 0.3488 [0.2431, 0.4360] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4375 | 0.3987 | 0.3693 |
| cell_recall | 0.5426 | 0.4651 | 0.4109 |
| cell_precision | 0.3665 | 0.3488 | 0.3354 |
| frame_det_rate | 1.0000 | 0.9583 | 0.9167 |
| frame_recall_V | 1.0000 | 0.9583 | 0.9167 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | n/a | n/a | n/a |
| cell_recall_V | 0.5426 | 0.4651 | 0.4109 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | n/a | n/a | n/a |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | 0.7179 | 0.7179 | 0.6923 |
| band4_cell_recall | 0.4667 | 0.3556 | 0.2889 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.1917 | 0.1583 | 0.1500 |
| band4_cell_fpr_off | 0.3750 | 0.3750 | 0.3750 |
| frame_fa_off | 1.0000 | 1.0000 | 1.0000 |
| cell_fpr_off | 0.1417 | 0.1333 | 0.1313 |
| cell_fpr_on_neg | 0.1510 | 0.1368 | 0.1197 |
