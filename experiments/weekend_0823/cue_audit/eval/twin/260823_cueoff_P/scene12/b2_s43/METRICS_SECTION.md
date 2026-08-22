# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 24 | 24 | 0 | 0 | 1 | 129 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.7917 [0.6154, 0.9474] | 0.3953 [0.2881, 0.4907] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 0.7917 [0.6154, 0.9474] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.1833 [0.1614, 0.2083] |
| cell FPR (negative cells of on frames) | 0.0912 [0.0599, 0.1246] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.6410 [0.5000, 0.7273] | 0.2083 [0.1000, 0.3250] |
| 3b [8,12) m | 0.2889 [0.1944, 0.3846] | 0.5250 [0.4296, 0.6083] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3400 [0.2320, 0.4329] |
| cell recall | 0.3953 [0.2881, 0.4907] |
| cell precision | 0.2982 [0.1840, 0.4157] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.7917 [0.6154, 0.9474] | 0.3953 [0.2881, 0.4907] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 0.7917 [0.6154, 0.9474] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.1833 [0.1614, 0.2083] |
| cell FPR (negative cells of on frames) | 0.0912 [0.0599, 0.1246] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.6410 [0.5000, 0.7273] | 0.2083 [0.1000, 0.3250] |
| 3b [8,12) m | 0.2889 [0.1944, 0.3846] | 0.5250 [0.4296, 0.6083] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3400 [0.2320, 0.4329] |
| cell recall | 0.3953 [0.2881, 0.4907] |
| cell precision | 0.2982 [0.1840, 0.4157] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4329 | 0.3400 | 0.1675 |
| cell_recall | 0.6124 | 0.3953 | 0.1318 |
| cell_precision | 0.3347 | 0.2982 | 0.2297 |
| frame_det_rate | 1.0000 | 0.7917 | 0.4583 |
| frame_recall_V | 1.0000 | 0.7917 | 0.4583 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | n/a | n/a | n/a |
| cell_recall_V | 0.6124 | 0.3953 | 0.1318 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | n/a | n/a | n/a |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | 0.6923 | 0.6410 | 0.3077 |
| band4_cell_recall | 0.5778 | 0.2889 | 0.0556 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.2667 | 0.2083 | 0.1000 |
| band4_cell_fpr_off | 0.6417 | 0.5250 | 0.2583 |
| frame_fa_off | 1.0000 | 1.0000 | 0.8750 |
| cell_fpr_off | 0.2271 | 0.1833 | 0.0896 |
| cell_fpr_on_neg | 0.1368 | 0.0912 | 0.0399 |
