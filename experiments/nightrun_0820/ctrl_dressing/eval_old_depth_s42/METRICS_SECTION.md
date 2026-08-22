# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/nightrun_0820/ctrl_dressing/eval_old_depth_s42/per_frame_src.csv`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 96 | 48 | 48 | 24 | 24 | 0 | 0 | 2 | 237 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.5443 [0.4398, 0.6615] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2500 [0.1321, 0.3778] |
| cell FPR (off frames) | 0.0281 [0.0135, 0.0448] |
| cell FPR (negative cells of on frames) | 0.0207 [0.0087, 0.0342] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0588 [0.0000, 0.1273] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.5185 [0.3295, 0.7167] | 0.0500 [0.0200, 0.0840] |
| 3b [8,12) m | 0.8000 [0.7238, 0.8800] | 0.0625 [0.0238, 0.1095] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6324 [0.5383, 0.7117] |
| cell recall | 0.5443 [0.4398, 0.6615] |
| cell precision | 0.7544 [0.6250, 0.8533] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.5443 [0.4398, 0.6615] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2500 [0.1321, 0.3778] |
| cell FPR (off frames) | 0.0281 [0.0135, 0.0448] |
| cell FPR (negative cells of on frames) | 0.0207 [0.0087, 0.0342] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0588 [0.0000, 0.1273] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.5185 [0.3295, 0.7167] | 0.0500 [0.0200, 0.0840] |
| 3b [8,12) m | 0.8000 [0.7238, 0.8800] | 0.0625 [0.0238, 0.1095] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6324 [0.5383, 0.7117] |
| cell recall | 0.5443 [0.4398, 0.6615] |
| cell precision | 0.7544 [0.6250, 0.8533] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.7097 | 0.6324 | 0.5128 |
| cell_recall | 0.6962 | 0.5443 | 0.3797 |
| cell_precision | 0.7237 | 0.7544 | 0.7895 |
| frame_det_rate | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_V | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | n/a | n/a | n/a |
| cell_recall_V | 0.6962 | 0.5443 | 0.3797 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | n/a | n/a | n/a |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | 0.2353 | 0.0588 | 0.0000 |
| band3_cell_recall | 0.6296 | 0.5185 | 0.3333 |
| band4_cell_recall | 0.9714 | 0.8000 | 0.6000 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0250 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0750 | 0.0500 | 0.0375 |
| band4_cell_fpr_off | 0.0875 | 0.0625 | 0.0375 |
| frame_fa_off | 0.2500 | 0.2500 | 0.1250 |
| cell_fpr_off | 0.0469 | 0.0281 | 0.0187 |
| cell_fpr_on_neg | 0.0249 | 0.0207 | 0.0083 |
