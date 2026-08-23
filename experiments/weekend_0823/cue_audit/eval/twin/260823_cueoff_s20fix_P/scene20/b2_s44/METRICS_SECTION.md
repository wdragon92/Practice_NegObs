# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 96 | 48 | 48 | 39 | 12 | 0 | 27 | 1 | 183 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8333 [0.5833, 1.0000] | 0.5500 [0.3600, 0.7250] | 12 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.7037 [0.5217, 0.8750] | 0.3089 [0.2047, 0.4231] | 27 |
| **any tier (frame detection rate)** | 0.7436 [0.6052, 0.8750] | — | 39 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (negative cells of on frames) | 0.1506 [0.0985, 0.2102] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.3880 [0.2911, 0.4889] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3827 [0.3096, 0.4552] |
| cell recall | 0.3880 [0.2911, 0.4889] |
| cell precision | 0.3777 [0.3039, 0.4688] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8333 [0.5833, 1.0000] | 0.5500 [0.3600, 0.7250] | 12 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.7037 [0.5217, 0.8750] | 0.3089 [0.2047, 0.4231] | 27 |
| **any tier (frame detection rate)** | 0.7436 [0.6052, 0.8750] | — | 39 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (negative cells of on frames) | 0.1506 [0.0985, 0.2102] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.3880 [0.2911, 0.4889] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3827 [0.3096, 0.4552] |
| cell recall | 0.3880 [0.2911, 0.4889] |
| cell precision | 0.3777 [0.3039, 0.4688] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4326 | 0.3827 | 0.2830 |
| cell_recall | 0.5082 | 0.3880 | 0.2459 |
| cell_precision | 0.3765 | 0.3777 | 0.3333 |
| frame_det_rate | 0.8205 | 0.7436 | 0.5128 |
| frame_recall_V | 1.0000 | 0.8333 | 0.7500 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.7407 | 0.7037 | 0.4074 |
| cell_recall_V | 0.6333 | 0.5500 | 0.3833 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.4472 | 0.3089 | 0.1789 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | n/a | n/a | n/a |
| band4_cell_recall | 0.5082 | 0.3880 | 0.2459 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0042 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| frame_fa_off | 0.0208 | 0.0000 | 0.0000 |
| cell_fpr_off | 0.0010 | 0.0000 | 0.0000 |
| cell_fpr_on_neg | 0.1969 | 0.1506 | 0.1158 |
