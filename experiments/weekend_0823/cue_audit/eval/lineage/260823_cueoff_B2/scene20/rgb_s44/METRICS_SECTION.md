# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 18 | 9 | 0 | 9 | 1 | 78 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.8667 [0.7000, 1.0000] | 9 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.6667 [0.3333, 1.0000] | 0.5758 [0.2800, 0.8182] | 9 |
| **any tier (frame detection rate)** | 0.8333 [0.6429, 1.0000] | — | 18 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0833 [0.0000, 0.2105] |
| cell FPR (off frames) | 0.0042 [0.0000, 0.0105] |
| cell FPR (negative cells of on frames) | 0.1244 [0.0813, 0.1709] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.7436 [0.5882, 0.8767] | 0.0167 [0.0000, 0.0421] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6170 [0.5286, 0.6839] |
| cell recall | 0.7436 [0.5882, 0.8767] |
| cell precision | 0.5273 [0.4500, 0.5970] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.8667 [0.7000, 1.0000] | 9 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.6667 [0.3333, 1.0000] | 0.5758 [0.2800, 0.8182] | 9 |
| **any tier (frame detection rate)** | 0.8333 [0.6429, 1.0000] | — | 18 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0833 [0.0000, 0.2105] |
| cell FPR (off frames) | 0.0042 [0.0000, 0.0105] |
| cell FPR (negative cells of on frames) | 0.1244 [0.0813, 0.1709] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.7436 [0.5882, 0.8767] | 0.0167 [0.0000, 0.0421] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6170 [0.5286, 0.6839] |
| cell recall | 0.7436 [0.5882, 0.8767] |
| cell precision | 0.5273 [0.4500, 0.5970] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.6154 | 0.6170 | 0.6012 |
| cell_recall | 0.8718 | 0.7436 | 0.6282 |
| cell_precision | 0.4755 | 0.5273 | 0.5765 |
| frame_det_rate | 0.8333 | 0.8333 | 0.7778 |
| frame_recall_V | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.6667 | 0.6667 | 0.5556 |
| cell_recall_V | 0.9111 | 0.8667 | 0.8222 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.8182 | 0.5758 | 0.3636 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | n/a | n/a | n/a |
| band4_cell_recall | 0.8718 | 0.7436 | 0.6282 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.0417 | 0.0167 | 0.0083 |
| frame_fa_off | 0.1250 | 0.0833 | 0.0417 |
| cell_fpr_off | 0.0104 | 0.0042 | 0.0021 |
| cell_fpr_on_neg | 0.1741 | 0.1244 | 0.0871 |
