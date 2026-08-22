# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 24 | 6 | 0 | 18 | 1 | 168 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.2143 [0.1515, 0.3000] | 6 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.3889 [0.1667, 0.6250] | 0.0952 [0.0382, 0.1538] | 18 |
| **any tier (frame detection rate)** | 0.5417 [0.3448, 0.7391] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.1313 [0.1174, 0.1457] |
| cell FPR (negative cells of on frames) | 0.0064 [0.0000, 0.0158] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.2917 [0.1818, 0.4098] | 0.3250 [0.2250, 0.4231] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.2000 [0.1200, 0.2815] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1654 [0.0976, 0.2264] |
| cell recall | 0.1250 [0.0759, 0.1745] |
| cell precision | 0.2442 [0.1277, 0.3875] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.2143 [0.1515, 0.3000] | 6 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.3889 [0.1667, 0.6250] | 0.0952 [0.0382, 0.1538] | 18 |
| **any tier (frame detection rate)** | 0.5417 [0.3448, 0.7391] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.1313 [0.1174, 0.1457] |
| cell FPR (negative cells of on frames) | 0.0064 [0.0000, 0.0158] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.2917 [0.1818, 0.4098] | 0.3250 [0.2250, 0.4231] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.2000 [0.1200, 0.2815] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1654 [0.0976, 0.2264] |
| cell recall | 0.1250 [0.0759, 0.1745] |
| cell precision | 0.2442 [0.1277, 0.3875] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.2061 | 0.1654 | 0.1377 |
| cell_recall | 0.1607 | 0.1250 | 0.1012 |
| cell_precision | 0.2872 | 0.2442 | 0.2152 |
| frame_det_rate | 0.6250 | 0.5417 | 0.5417 |
| frame_recall_V | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.5000 | 0.3889 | 0.3889 |
| cell_recall_V | 0.2381 | 0.2143 | 0.1667 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.1349 | 0.0952 | 0.0794 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_recall | 0.3750 | 0.2917 | 0.2361 |
| band4_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.3333 | 0.3250 | 0.3083 |
| band4_cell_fpr_off | 0.2000 | 0.2000 | 0.2000 |
| frame_fa_off | 1.0000 | 1.0000 | 1.0000 |
| cell_fpr_off | 0.1333 | 0.1313 | 0.1271 |
| cell_fpr_on_neg | 0.0096 | 0.0064 | 0.0032 |
