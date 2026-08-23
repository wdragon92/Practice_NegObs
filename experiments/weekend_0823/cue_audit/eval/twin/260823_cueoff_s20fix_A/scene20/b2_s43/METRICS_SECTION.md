# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 96 | 48 | 48 | 39 | 12 | 0 | 27 | 1 | 183 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.4667 [0.2889, 0.6667] | 12 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.9630 [0.8750, 1.0000] | 0.5447 [0.4364, 0.6556] | 27 |
| **any tier (frame detection rate)** | 0.9744 [0.9143, 1.0000] | — | 39 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0625 [0.0000, 0.1395] |
| cell FPR (off frames) | 0.0115 [0.0000, 0.0298] |
| cell FPR (negative cells of on frames) | 0.3449 [0.2905, 0.3978] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0250 [0.0000, 0.0679] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0167 [0.0000, 0.0476] |
| 3b [8,12) m | 0.5191 [0.4251, 0.6193] | 0.0042 [0.0000, 0.0136] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3411 [0.2768, 0.4034] |
| cell recall | 0.5191 [0.4251, 0.6193] |
| cell precision | 0.2540 [0.1988, 0.3101] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.4667 [0.2889, 0.6667] | 12 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.9630 [0.8750, 1.0000] | 0.5447 [0.4364, 0.6556] | 27 |
| **any tier (frame detection rate)** | 0.9744 [0.9143, 1.0000] | — | 39 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0625 [0.0000, 0.1395] |
| cell FPR (off frames) | 0.0115 [0.0000, 0.0298] |
| cell FPR (negative cells of on frames) | 0.3449 [0.2905, 0.3978] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0250 [0.0000, 0.0679] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0167 [0.0000, 0.0476] |
| 3b [8,12) m | 0.5191 [0.4251, 0.6193] | 0.0042 [0.0000, 0.0136] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3411 [0.2768, 0.4034] |
| cell recall | 0.5191 [0.4251, 0.6193] |
| cell precision | 0.2540 [0.1988, 0.3101] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4053 | 0.3411 | 0.2626 |
| cell_recall | 0.9180 | 0.5191 | 0.2131 |
| cell_precision | 0.2601 | 0.2540 | 0.3421 |
| frame_det_rate | 1.0000 | 0.9744 | 0.7949 |
| frame_recall_V | 1.0000 | 1.0000 | 0.8333 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 1.0000 | 0.9630 | 0.7778 |
| cell_recall_V | 0.9333 | 0.4667 | 0.2000 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.9106 | 0.5447 | 0.2195 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | n/a | n/a | n/a |
| band4_cell_recall | 0.9180 | 0.5191 | 0.2131 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0500 | 0.0250 | 0.0000 |
| band3_cell_fpr_off | 0.0708 | 0.0167 | 0.0000 |
| band4_cell_fpr_off | 0.0500 | 0.0042 | 0.0000 |
| frame_fa_off | 0.2917 | 0.0625 | 0.0000 |
| cell_fpr_off | 0.0427 | 0.0115 | 0.0000 |
| cell_fpr_on_neg | 0.5624 | 0.3449 | 0.0965 |
