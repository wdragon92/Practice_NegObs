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
| V | 0.2903 [0.2000, 0.3846] | 0.3451 [0.2337, 0.4571] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.1944 [0.1071, 0.2923] | 0.1736 [0.0846, 0.2692] | 72 |
| **any tier (frame detection rate)** | 0.2485 [0.1842, 0.3161] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0278 [0.0104, 0.0484] |
| cell FPR (off frames) | 0.0071 [0.0025, 0.0127] |
| cell FPR (negative cells of on frames) | 0.0154 [0.0075, 0.0248] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.6667 [0.2222, 1.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.3030 [0.1327, 0.4854] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.2808 [0.1899, 0.3764] | 0.0042 [0.0000, 0.0100] |
| 3b [8,12) m | 0.2652 [0.1959, 0.3367] | 0.0243 [0.0088, 0.0426] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4119 [0.3177, 0.4956] |
| cell recall | 0.2833 [0.2036, 0.3643] |
| cell precision | 0.7539 [0.6684, 0.8322] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.2903 [0.2000, 0.3846] | 0.3451 [0.2337, 0.4571] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.1944 [0.1071, 0.2923] | 0.1736 [0.0846, 0.2692] | 72 |
| **any tier (frame detection rate)** | 0.2485 [0.1842, 0.3161] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0278 [0.0104, 0.0484] |
| cell FPR (off frames) | 0.0071 [0.0025, 0.0127] |
| cell FPR (negative cells of on frames) | 0.0154 [0.0075, 0.0248] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.6667 [0.2222, 1.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.3030 [0.1327, 0.4854] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.2808 [0.1899, 0.3764] | 0.0042 [0.0000, 0.0100] |
| 3b [8,12) m | 0.2652 [0.1959, 0.3367] | 0.0243 [0.0088, 0.0426] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4119 [0.3177, 0.4956] |
| cell recall | 0.2833 [0.2036, 0.3643] |
| cell precision | 0.7539 [0.6684, 0.8322] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4539 | 0.4119 | 0.3474 |
| cell_recall | 0.3408 | 0.2833 | 0.2200 |
| cell_precision | 0.6794 | 0.7539 | 0.8250 |
| frame_det_rate | 0.2727 | 0.2485 | 0.1697 |
| frame_recall_V | 0.3226 | 0.2903 | 0.2258 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.2083 | 0.1944 | 0.0972 |
| cell_recall_V | 0.3984 | 0.3451 | 0.2799 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.2384 | 0.1736 | 0.1134 |
| band1_cell_recall | 0.6667 | 0.6667 | 0.4444 |
| band2_cell_recall | 0.3258 | 0.3030 | 0.2803 |
| band3_cell_recall | 0.3543 | 0.2808 | 0.2178 |
| band4_cell_recall | 0.3227 | 0.2652 | 0.2000 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0076 | 0.0042 | 0.0007 |
| band4_cell_fpr_off | 0.0507 | 0.0243 | 0.0118 |
| frame_fa_off | 0.0729 | 0.0278 | 0.0208 |
| cell_fpr_off | 0.0146 | 0.0071 | 0.0031 |
| cell_fpr_on_neg | 0.0239 | 0.0154 | 0.0083 |
