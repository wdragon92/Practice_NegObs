# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 15 | 9 | 0 | 6 | 1 | 72 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.8889 [0.8222, 0.9600] | 9 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 1.0000 [1.0000, 1.0000] | 0.7037 [0.3704, 1.0000] | 6 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 15 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.4583 [0.2500, 0.6667] |
| cell FPR (off frames) | 0.0708 [0.0367, 0.1071] |
| cell FPR (negative cells of on frames) | 0.3922 [0.3132, 0.4724] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.1667 [0.0909, 0.2455] |
| 3b [8,12) m | 0.8194 [0.6792, 0.9286] | 0.1167 [0.0400, 0.2000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3631 [0.2667, 0.4393] |
| cell recall | 0.8194 [0.6792, 0.9286] |
| cell precision | 0.2332 [0.1611, 0.2964] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.8889 [0.8222, 0.9600] | 9 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 1.0000 [1.0000, 1.0000] | 0.7037 [0.3704, 1.0000] | 6 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 15 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.4583 [0.2500, 0.6667] |
| cell FPR (off frames) | 0.0708 [0.0367, 0.1071] |
| cell FPR (negative cells of on frames) | 0.3922 [0.3132, 0.4724] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.1667 [0.0909, 0.2455] |
| 3b [8,12) m | 0.8194 [0.6792, 0.9286] | 0.1167 [0.0400, 0.2000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3631 [0.2667, 0.4393] |
| cell recall | 0.8194 [0.6792, 0.9286] |
| cell precision | 0.2332 [0.1611, 0.2964] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3667 | 0.3631 | 0.3889 |
| cell_recall | 0.9167 | 0.8194 | 0.7778 |
| cell_precision | 0.2292 | 0.2332 | 0.2593 |
| frame_det_rate | 1.0000 | 1.0000 | 0.9333 |
| frame_recall_V | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 1.0000 | 1.0000 | 0.8333 |
| cell_recall_V | 0.9556 | 0.8889 | 0.8667 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.8519 | 0.7037 | 0.6296 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | n/a | n/a | n/a |
| band4_cell_recall | 0.9167 | 0.8194 | 0.7778 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.2083 | 0.1667 | 0.1083 |
| band4_cell_fpr_off | 0.1667 | 0.1167 | 0.0417 |
| frame_fa_off | 0.5833 | 0.4583 | 0.3750 |
| cell_fpr_off | 0.0938 | 0.0708 | 0.0375 |
| cell_fpr_on_neg | 0.4338 | 0.3922 | 0.3480 |
