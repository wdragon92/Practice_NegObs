# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 24 | 24 | 0 | 0 | 1 | 168 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.4107 [0.3548, 0.4802] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.1521 [0.1364, 0.1684] |
| cell FPR (negative cells of on frames) | 0.0032 [0.0000, 0.0104] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.6250 [0.5131, 0.7273] | 0.3583 [0.2609, 0.4500] |
| 3b [8,12) m | 0.2759 [0.1591, 0.3953] | 0.2500 [0.1680, 0.3333] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4437 [0.3624, 0.5112] |
| cell recall | 0.4107 [0.3548, 0.4802] |
| cell precision | 0.4825 [0.3396, 0.6259] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.4107 [0.3548, 0.4802] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.1521 [0.1364, 0.1684] |
| cell FPR (negative cells of on frames) | 0.0032 [0.0000, 0.0104] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.6250 [0.5131, 0.7273] | 0.3583 [0.2609, 0.4500] |
| 3b [8,12) m | 0.2759 [0.1591, 0.3953] | 0.2500 [0.1680, 0.3333] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4437 [0.3624, 0.5112] |
| cell recall | 0.4107 [0.3548, 0.4802] |
| cell precision | 0.4825 [0.3396, 0.6259] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4795 | 0.4437 | 0.4207 |
| cell_recall | 0.4881 | 0.4107 | 0.3631 |
| cell_precision | 0.4713 | 0.4825 | 0.5000 |
| frame_det_rate | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_V | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | n/a | n/a | n/a |
| cell_recall_V | 0.4881 | 0.4107 | 0.3631 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | n/a | n/a | n/a |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_recall | 0.6667 | 0.6250 | 0.5417 |
| band4_cell_recall | 0.3908 | 0.2759 | 0.2529 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.4000 | 0.3583 | 0.3167 |
| band4_cell_fpr_off | 0.3333 | 0.2500 | 0.1917 |
| frame_fa_off | 1.0000 | 1.0000 | 1.0000 |
| cell_fpr_off | 0.1833 | 0.1521 | 0.1271 |
| cell_fpr_on_neg | 0.0128 | 0.0032 | 0.0000 |
