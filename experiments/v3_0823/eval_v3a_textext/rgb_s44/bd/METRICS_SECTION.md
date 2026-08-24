# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/runs/v3a/rgb_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.3333 [0.2386, 0.4312] | 0.2760 [0.1887, 0.3659] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.2917 [0.1875, 0.4000] | 0.2685 [0.1671, 0.3701] | 72 |
| **any tier (frame detection rate)** | 0.3152 [0.2452, 0.3879] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0764 [0.0465, 0.1085] |
| cell FPR (off frames) | 0.0068 [0.0038, 0.0101] |
| cell FPR (negative cells of on frames) | 0.0164 [0.0093, 0.0243] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.1818 [0.0652, 0.3197] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.2992 [0.2129, 0.3890] | 0.0014 [0.0000, 0.0044] |
| 3b [8,12) m | 0.2879 [0.2209, 0.3560] | 0.0257 [0.0141, 0.0388] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3995 [0.3211, 0.4719] |
| cell recall | 0.2733 [0.2074, 0.3416] |
| cell precision | 0.7421 [0.6746, 0.8051] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.3333 [0.2386, 0.4312] | 0.2760 [0.1887, 0.3659] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.2917 [0.1875, 0.4000] | 0.2685 [0.1671, 0.3701] | 72 |
| **any tier (frame detection rate)** | 0.3152 [0.2452, 0.3879] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0764 [0.0465, 0.1085] |
| cell FPR (off frames) | 0.0068 [0.0038, 0.0101] |
| cell FPR (negative cells of on frames) | 0.0164 [0.0093, 0.0243] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.1818 [0.0652, 0.3197] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.2992 [0.2129, 0.3890] | 0.0014 [0.0000, 0.0044] |
| 3b [8,12) m | 0.2879 [0.2209, 0.3560] | 0.0257 [0.0141, 0.0388] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3995 [0.3211, 0.4719] |
| cell recall | 0.2733 [0.2074, 0.3416] |
| cell precision | 0.7421 [0.6746, 0.8051] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4456 | 0.3995 | 0.3351 |
| cell_recall | 0.3567 | 0.2733 | 0.2108 |
| cell_precision | 0.5936 | 0.7421 | 0.8161 |
| frame_det_rate | 0.4303 | 0.3152 | 0.2606 |
| frame_recall_V | 0.4086 | 0.3333 | 0.2903 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.4583 | 0.2917 | 0.2222 |
| cell_recall_V | 0.3477 | 0.2760 | 0.2227 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.3727 | 0.2685 | 0.1898 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.2500 | 0.1818 | 0.0985 |
| band3_cell_recall | 0.3885 | 0.2992 | 0.2231 |
| band4_cell_recall | 0.3742 | 0.2879 | 0.2348 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0007 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0076 | 0.0014 | 0.0000 |
| band4_cell_fpr_off | 0.0861 | 0.0257 | 0.0076 |
| frame_fa_off | 0.1944 | 0.0764 | 0.0174 |
| cell_fpr_off | 0.0236 | 0.0068 | 0.0019 |
| cell_fpr_on_neg | 0.0344 | 0.0164 | 0.0101 |
