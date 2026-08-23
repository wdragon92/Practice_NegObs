# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/newmodels/runs/tu-convnext_tiny_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.3 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 369 | 219 | 45 | 96 | 7 | 2856 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.2819 [0.2647, 0.3008] | 219 |
| E | 1.0000 [1.0000, 1.0000] | 0.3879 [0.3454, 0.4419] | 45 |
| H | 1.0000 [1.0000, 1.0000] | 0.4968 [0.4569, 0.5440] | 96 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.1500 [0.1500, 0.1500] |
| cell FPR (negative cells of on frames) | 0.0509 [0.0446, 0.0572] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.6490 [0.6395, 0.6595] | 0.6000 [0.6000, 0.6000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3597 [0.3431, 0.3763] |
| cell recall | 0.3340 [0.3165, 0.3537] |
| cell precision | 0.3897 [0.3583, 0.4203] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.3

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.4421 [0.4171, 0.4695] | 219 |
| E | 1.0000 [1.0000, 1.0000] | 0.6207 [0.5587, 0.6979] | 45 |
| H | 1.0000 [1.0000, 1.0000] | 0.7325 [0.6801, 0.7918] | 96 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.2500 [0.2500, 0.2500] |
| cell FPR (negative cells of on frames) | 0.1075 [0.0967, 0.1182] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4239 [0.4010, 0.4460] |
| cell recall | 0.5147 [0.4898, 0.5418] |
| cell precision | 0.3603 [0.3301, 0.3902] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4239 | 0.3597 | 0.0000 |
| cell_recall | 0.5147 | 0.3340 | 0.0000 |
| cell_precision | 0.3603 | 0.3897 | n/a |
| frame_det_rate | 1.0000 | 1.0000 | 0.0000 |
| frame_recall_V | 1.0000 | 1.0000 | 0.0000 |
| frame_recall_E | 1.0000 | 1.0000 | 0.0000 |
| frame_recall_H | 1.0000 | 1.0000 | 0.0000 |
| cell_recall_V | 0.4421 | 0.2819 | 0.0000 |
| cell_recall_E | 0.6207 | 0.3879 | 0.0000 |
| cell_recall_H | 0.7325 | 0.4968 | 0.0000 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_recall | 1.0000 | 0.6490 | 0.0000 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 1.0000 | 0.6000 | 0.0000 |
| frame_fa_off | 1.0000 | 1.0000 | 0.0000 |
| cell_fpr_off | 0.2500 | 0.1500 | 0.0000 |
| cell_fpr_on_neg | 0.1075 | 0.0509 | 0.0000 |
