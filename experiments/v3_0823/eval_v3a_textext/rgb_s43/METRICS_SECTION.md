# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/runs/v3a/rgb_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4301 [0.3299, 0.5326] | 0.4714 [0.3604, 0.5757] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.1667 [0.0843, 0.2568] | 0.1551 [0.0688, 0.2473] | 72 |
| **any tier (frame detection rate)** | 0.3152 [0.2452, 0.3871] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3056 [0.2527, 0.3593] |
| cell FPR (off frames) | 0.0899 [0.0686, 0.1131] |
| cell FPR (negative cells of on frames) | 0.0882 [0.0671, 0.1112] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.6667 [0.2222, 1.0000] | 0.0160 [0.0035, 0.0315] |
| 2 [2,5) m | 0.4091 [0.2216, 0.6048] | 0.0292 [0.0120, 0.0491] |
| 3a [5,8) m | 0.3727 [0.2724, 0.4753] | 0.1000 [0.0697, 0.1331] |
| 3b [8,12) m | 0.3258 [0.2515, 0.4000] | 0.2146 [0.1716, 0.2585] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3366 [0.2615, 0.4066] |
| cell recall | 0.3575 [0.2735, 0.4398] |
| cell precision | 0.3180 [0.2417, 0.3936] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4301 [0.3299, 0.5326] | 0.4714 [0.3604, 0.5757] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.1667 [0.0843, 0.2568] | 0.1551 [0.0688, 0.2473] | 72 |
| **any tier (frame detection rate)** | 0.3152 [0.2452, 0.3871] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3056 [0.2527, 0.3593] |
| cell FPR (off frames) | 0.0899 [0.0686, 0.1131] |
| cell FPR (negative cells of on frames) | 0.0882 [0.0671, 0.1112] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.6667 [0.2222, 1.0000] | 0.0160 [0.0035, 0.0315] |
| 2 [2,5) m | 0.4091 [0.2216, 0.6048] | 0.0292 [0.0120, 0.0491] |
| 3a [5,8) m | 0.3727 [0.2724, 0.4753] | 0.1000 [0.0697, 0.1331] |
| 3b [8,12) m | 0.3258 [0.2515, 0.4000] | 0.2146 [0.1716, 0.2585] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3366 [0.2615, 0.4066] |
| cell recall | 0.3575 [0.2735, 0.4398] |
| cell precision | 0.3180 [0.2417, 0.3936] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3207 | 0.3366 | 0.3137 |
| cell_recall | 0.4592 | 0.3575 | 0.2592 |
| cell_precision | 0.2464 | 0.3180 | 0.3972 |
| frame_det_rate | 0.4970 | 0.3152 | 0.2242 |
| frame_recall_V | 0.6774 | 0.4301 | 0.3333 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.2639 | 0.1667 | 0.0833 |
| cell_recall_V | 0.5820 | 0.4714 | 0.3698 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.2407 | 0.1551 | 0.0625 |
| band1_cell_recall | 0.6667 | 0.6667 | 0.3333 |
| band2_cell_recall | 0.4621 | 0.4091 | 0.3030 |
| band3_cell_recall | 0.4409 | 0.3727 | 0.2835 |
| band4_cell_recall | 0.4606 | 0.3258 | 0.2333 |
| band1_cell_fpr_off | 0.0243 | 0.0160 | 0.0104 |
| band2_cell_fpr_off | 0.0653 | 0.0292 | 0.0222 |
| band3_cell_fpr_off | 0.1938 | 0.1000 | 0.0458 |
| band4_cell_fpr_off | 0.3729 | 0.2146 | 0.1139 |
| frame_fa_off | 0.4896 | 0.3056 | 0.1493 |
| cell_fpr_off | 0.1641 | 0.0899 | 0.0481 |
| cell_fpr_on_neg | 0.1623 | 0.0882 | 0.0428 |
