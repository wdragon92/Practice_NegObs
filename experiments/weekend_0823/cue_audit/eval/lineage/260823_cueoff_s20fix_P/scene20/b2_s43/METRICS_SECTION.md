# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 72 | 48 | 24 | 39 | 12 | 0 | 27 | 1 | 183 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9167 [0.7143, 1.0000] | 0.6333 [0.4333, 0.8125] | 12 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 1.0000 [1.0000, 1.0000] | 0.6829 [0.5776, 0.7857] | 27 |
| **any tier (frame detection rate)** | 0.9744 [0.9143, 1.0000] | — | 39 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0833 [0.0000, 0.2105] |
| cell FPR (off frames) | 0.0083 [0.0000, 0.0211] |
| cell FPR (negative cells of on frames) | 0.4234 [0.3714, 0.4716] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0333 [0.0000, 0.0842] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.6667 [0.5745, 0.7563] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3824 [0.3208, 0.4391] |
| cell recall | 0.6667 [0.5745, 0.7563] |
| cell precision | 0.2681 [0.2165, 0.3188] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9167 [0.7143, 1.0000] | 0.6333 [0.4333, 0.8125] | 12 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 1.0000 [1.0000, 1.0000] | 0.6829 [0.5776, 0.7857] | 27 |
| **any tier (frame detection rate)** | 0.9744 [0.9143, 1.0000] | — | 39 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0833 [0.0000, 0.2105] |
| cell FPR (off frames) | 0.0083 [0.0000, 0.0211] |
| cell FPR (negative cells of on frames) | 0.4234 [0.3714, 0.4716] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0333 [0.0000, 0.0842] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.6667 [0.5745, 0.7563] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3824 [0.3208, 0.4391] |
| cell recall | 0.6667 [0.5745, 0.7563] |
| cell precision | 0.2681 [0.2165, 0.3188] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4317 | 0.3824 | 0.2131 |
| cell_recall | 0.9836 | 0.6667 | 0.2131 |
| cell_precision | 0.2765 | 0.2681 | 0.2131 |
| frame_det_rate | 1.0000 | 0.9744 | 0.6923 |
| frame_recall_V | 1.0000 | 0.9167 | 0.6667 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 1.0000 | 1.0000 | 0.7037 |
| cell_recall_V | 1.0000 | 0.6333 | 0.1667 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.9756 | 0.6829 | 0.2358 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | n/a | n/a | n/a |
| band4_cell_recall | 0.9836 | 0.6667 | 0.2131 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0667 | 0.0333 | 0.0000 |
| band3_cell_fpr_off | 0.0417 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.0250 | 0.0000 | 0.0000 |
| frame_fa_off | 0.1250 | 0.0833 | 0.0000 |
| cell_fpr_off | 0.0333 | 0.0083 | 0.0000 |
| cell_fpr_on_neg | 0.5856 | 0.4234 | 0.1853 |
