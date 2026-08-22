# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 18 | 9 | 0 | 9 | 1 | 78 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4444 [0.1111, 0.8000] | 0.2667 [0.0333, 0.5333] | 9 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.4444 [0.1111, 0.8000] | 0.2727 [0.0435, 0.5938] | 9 |
| **any tier (frame detection rate)** | 0.4444 [0.2105, 0.6842] | — | 18 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (negative cells of on frames) | 0.1244 [0.0502, 0.2152] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.2692 [0.1045, 0.4615] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2819 [0.1351, 0.4122] |
| cell recall | 0.2692 [0.1045, 0.4615] |
| cell precision | 0.2958 [0.1667, 0.4667] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4444 [0.1111, 0.8000] | 0.2667 [0.0333, 0.5333] | 9 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.4444 [0.1111, 0.8000] | 0.2727 [0.0435, 0.5938] | 9 |
| **any tier (frame detection rate)** | 0.4444 [0.2105, 0.6842] | — | 18 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (negative cells of on frames) | 0.1244 [0.0502, 0.2152] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.2692 [0.1045, 0.4615] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2819 [0.1351, 0.4122] |
| cell recall | 0.2692 [0.1045, 0.4615] |
| cell precision | 0.2958 [0.1667, 0.4667] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4151 | 0.2819 | 0.1538 |
| cell_recall | 0.5641 | 0.2692 | 0.1154 |
| cell_precision | 0.3284 | 0.2958 | 0.2308 |
| frame_det_rate | 0.7778 | 0.4444 | 0.2778 |
| frame_recall_V | 0.6667 | 0.4444 | 0.3333 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.8889 | 0.4444 | 0.2222 |
| cell_recall_V | 0.4444 | 0.2667 | 0.1556 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.7273 | 0.2727 | 0.0606 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | n/a | n/a | n/a |
| band4_cell_recall | 0.5641 | 0.2692 | 0.1154 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.0083 | 0.0000 | 0.0000 |
| frame_fa_off | 0.0417 | 0.0000 | 0.0000 |
| cell_fpr_off | 0.0021 | 0.0000 | 0.0000 |
| cell_fpr_on_neg | 0.2214 | 0.1244 | 0.0746 |
