# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 24 | 24 | 0 | 0 | 1 | 129 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.7917 [0.6087, 0.9524] | 0.2791 [0.1966, 0.3516] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 0.7917 [0.6087, 0.9524] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.1437 [0.1232, 0.1667] |
| cell FPR (negative cells of on frames) | 0.0000 [0.0000, 0.0000] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.2564 [0.1000, 0.4001] | 0.1750 [0.0842, 0.2737] |
| 3b [8,12) m | 0.2889 [0.2022, 0.3636] | 0.4000 [0.3130, 0.4783] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3077 [0.2069, 0.3906] |
| cell recall | 0.2791 [0.1966, 0.3516] |
| cell precision | 0.3429 [0.2017, 0.5000] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.7917 [0.6087, 0.9524] | 0.2791 [0.1966, 0.3516] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 0.7917 [0.6087, 0.9524] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.1437 [0.1232, 0.1667] |
| cell FPR (negative cells of on frames) | 0.0000 [0.0000, 0.0000] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.2564 [0.1000, 0.4001] | 0.1750 [0.0842, 0.2737] |
| 3b [8,12) m | 0.2889 [0.2022, 0.3636] | 0.4000 [0.3130, 0.4783] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3077 [0.2069, 0.3906] |
| cell recall | 0.2791 [0.1966, 0.3516] |
| cell precision | 0.3429 [0.2017, 0.5000] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4719 | 0.3077 | 0.2000 |
| cell_recall | 0.4884 | 0.2791 | 0.1628 |
| cell_precision | 0.4565 | 0.3429 | 0.2593 |
| frame_det_rate | 0.9167 | 0.7917 | 0.4583 |
| frame_recall_V | 0.9167 | 0.7917 | 0.4583 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | n/a | n/a | n/a |
| cell_recall_V | 0.4884 | 0.2791 | 0.1628 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | n/a | n/a | n/a |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | 0.4615 | 0.2564 | 0.1538 |
| band4_cell_recall | 0.5000 | 0.2889 | 0.1667 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.1917 | 0.1750 | 0.1583 |
| band4_cell_fpr_off | 0.4167 | 0.4000 | 0.3417 |
| frame_fa_off | 1.0000 | 1.0000 | 1.0000 |
| cell_fpr_off | 0.1521 | 0.1437 | 0.1250 |
| cell_fpr_on_neg | 0.0057 | 0.0000 | 0.0000 |
