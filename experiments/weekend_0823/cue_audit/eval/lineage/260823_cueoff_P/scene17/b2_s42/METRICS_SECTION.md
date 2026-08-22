# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 24 | 0 | 0 | 24 | 1 | 147 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 1.0000 [1.0000, 1.0000] | 0.9660 [0.9306, 0.9934] | 24 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0417 [0.0000, 0.1364] |
| cell FPR (off frames) | 0.0021 [0.0000, 0.0068] |
| cell FPR (negative cells of on frames) | 0.0030 [0.0000, 0.0099] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.8810 [0.7500, 0.9773] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 1.0000 [1.0000, 1.0000] | 0.0083 [0.0000, 0.0273] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.9759 [0.9551, 0.9926] |
| cell recall | 0.9660 [0.9306, 0.9934] |
| cell precision | 0.9861 [0.9632, 1.0000] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 1.0000 [1.0000, 1.0000] | 0.9660 [0.9306, 0.9934] | 24 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0417 [0.0000, 0.1364] |
| cell FPR (off frames) | 0.0021 [0.0000, 0.0068] |
| cell FPR (negative cells of on frames) | 0.0030 [0.0000, 0.0099] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.8810 [0.7500, 0.9773] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 1.0000 [1.0000, 1.0000] | 0.0083 [0.0000, 0.0273] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.9759 [0.9551, 0.9926] |
| cell recall | 0.9660 [0.9306, 0.9934] |
| cell precision | 0.9861 [0.9632, 1.0000] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.9732 | 0.9759 | 0.9720 |
| cell_recall | 0.9864 | 0.9660 | 0.9456 |
| cell_precision | 0.9603 | 0.9861 | 1.0000 |
| frame_det_rate | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_V | n/a | n/a | n/a |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 1.0000 | 1.0000 | 1.0000 |
| cell_recall_V | n/a | n/a | n/a |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.9864 | 0.9660 | 0.9456 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | 0.9524 | 0.8810 | 0.8333 |
| band4_cell_recall | 1.0000 | 1.0000 | 0.9905 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.0333 | 0.0083 | 0.0000 |
| frame_fa_off | 0.0833 | 0.0417 | 0.0000 |
| cell_fpr_off | 0.0083 | 0.0021 | 0.0000 |
| cell_fpr_on_neg | 0.0060 | 0.0030 | 0.0000 |
