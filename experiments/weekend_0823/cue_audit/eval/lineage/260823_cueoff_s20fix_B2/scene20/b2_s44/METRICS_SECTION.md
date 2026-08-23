# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 72 | 48 | 24 | 39 | 12 | 0 | 27 | 1 | 189 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.5000 [0.2000, 0.8000] | 0.2000 [0.0727, 0.3333] | 12 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.2222 [0.0769, 0.3913] | 0.0620 [0.0174, 0.1197] | 27 |
| **any tier (frame detection rate)** | 0.3077 [0.1707, 0.4583] | — | 39 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (negative cells of on frames) | 0.0739 [0.0436, 0.1094] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.1058 [0.0542, 0.1667] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1504 [0.0830, 0.2179] |
| cell recall | 0.1058 [0.0542, 0.1667] |
| cell precision | 0.2597 [0.1711, 0.3472] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.5000 [0.2000, 0.8000] | 0.2000 [0.0727, 0.3333] | 12 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.2222 [0.0769, 0.3913] | 0.0620 [0.0174, 0.1197] | 27 |
| **any tier (frame detection rate)** | 0.3077 [0.1707, 0.4583] | — | 39 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (negative cells of on frames) | 0.0739 [0.0436, 0.1094] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.1058 [0.0542, 0.1667] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1504 [0.0830, 0.2179] |
| cell recall | 0.1058 [0.0542, 0.1667] |
| cell precision | 0.2597 [0.1711, 0.3472] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.2450 | 0.1504 | 0.0833 |
| cell_recall | 0.1958 | 0.1058 | 0.0529 |
| cell_precision | 0.3274 | 0.2597 | 0.1961 |
| frame_det_rate | 0.4359 | 0.3077 | 0.1282 |
| frame_recall_V | 0.7500 | 0.5000 | 0.3333 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.2963 | 0.2222 | 0.0370 |
| cell_recall_V | 0.4167 | 0.2000 | 0.1333 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.0930 | 0.0620 | 0.0155 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | n/a | n/a | n/a |
| band4_cell_recall | 0.1958 | 0.1058 | 0.0529 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| frame_fa_off | 0.0000 | 0.0000 | 0.0000 |
| cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| cell_fpr_on_neg | 0.0986 | 0.0739 | 0.0532 |
