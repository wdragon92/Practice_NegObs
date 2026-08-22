# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/depth_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 24 | 6 | 0 | 18 | 1 | 168 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.5714 [0.2000, 0.7778] | 6 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.8333 [0.6429, 1.0000] | 0.5476 [0.4286, 0.6585] | 18 |
| **any tier (frame detection rate)** | 0.8750 [0.7273, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (negative cells of on frames) | 0.0577 [0.0362, 0.0817] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.3333 [0.1786, 0.4787] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.7931 [0.6567, 0.9000] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6667 [0.5745, 0.7437] |
| cell recall | 0.5536 [0.4478, 0.6504] |
| cell precision | 0.8378 [0.7831, 0.8862] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.5714 [0.2000, 0.7778] | 6 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.8333 [0.6429, 1.0000] | 0.5476 [0.4286, 0.6585] | 18 |
| **any tier (frame detection rate)** | 0.8750 [0.7273, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (negative cells of on frames) | 0.0577 [0.0362, 0.0817] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.3333 [0.1786, 0.4787] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.7931 [0.6567, 0.9000] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6667 [0.5745, 0.7437] |
| cell recall | 0.5536 [0.4478, 0.6504] |
| cell precision | 0.8378 [0.7831, 0.8862] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.7544 | 0.6667 | 0.5610 |
| cell_recall | 0.7679 | 0.5536 | 0.4107 |
| cell_precision | 0.7414 | 0.8378 | 0.8846 |
| frame_det_rate | 1.0000 | 0.8750 | 0.7500 |
| frame_recall_V | 1.0000 | 1.0000 | 0.5000 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 1.0000 | 0.8333 | 0.8333 |
| cell_recall_V | 0.7857 | 0.5714 | 0.5000 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.7619 | 0.5476 | 0.3810 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | 1.0000 | 0.0000 | 0.0000 |
| band3_cell_recall | 0.5000 | 0.3333 | 0.2917 |
| band4_cell_recall | 0.9655 | 0.7931 | 0.5517 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.0250 | 0.0000 | 0.0000 |
| frame_fa_off | 0.1250 | 0.0000 | 0.0000 |
| cell_fpr_off | 0.0063 | 0.0000 | 0.0000 |
| cell_fpr_on_neg | 0.1346 | 0.0577 | 0.0288 |
