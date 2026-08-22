# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 18 | 9 | 0 | 9 | 1 | 78 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.5556 [0.2000, 0.8750] | 0.3778 [0.1000, 0.6667] | 9 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.2222 [0.0000, 0.5000] | 0.0606 [0.0000, 0.1304] | 9 |
| **any tier (frame detection rate)** | 0.3889 [0.1667, 0.6250] | — | 18 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0417 [0.0000, 0.1364] |
| cell FPR (off frames) | 0.0063 [0.0000, 0.0205] |
| cell FPR (negative cells of on frames) | 0.0597 [0.0157, 0.1164] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.2436 [0.0741, 0.4337] | 0.0250 [0.0000, 0.0818] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3065 [0.1194, 0.4394] |
| cell recall | 0.2436 [0.0741, 0.4337] |
| cell precision | 0.4130 [0.2692, 0.5455] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.5556 [0.2000, 0.8750] | 0.3778 [0.1000, 0.6667] | 9 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.2222 [0.0000, 0.5000] | 0.0606 [0.0000, 0.1304] | 9 |
| **any tier (frame detection rate)** | 0.3889 [0.1667, 0.6250] | — | 18 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0417 [0.0000, 0.1364] |
| cell FPR (off frames) | 0.0063 [0.0000, 0.0205] |
| cell FPR (negative cells of on frames) | 0.0597 [0.0157, 0.1164] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.2436 [0.0741, 0.4337] | 0.0250 [0.0000, 0.0818] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3065 [0.1194, 0.4394] |
| cell recall | 0.2436 [0.0741, 0.4337] |
| cell precision | 0.4130 [0.2692, 0.5455] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4034 | 0.3065 | 0.2022 |
| cell_recall | 0.6026 | 0.2436 | 0.1154 |
| cell_precision | 0.3032 | 0.4130 | 0.8182 |
| frame_det_rate | 0.6667 | 0.3889 | 0.2222 |
| frame_recall_V | 1.0000 | 0.5556 | 0.4444 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.3333 | 0.2222 | 0.0000 |
| cell_recall_V | 0.8444 | 0.3778 | 0.2000 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.2727 | 0.0606 | 0.0000 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | n/a | n/a | n/a |
| band4_cell_recall | 0.6026 | 0.2436 | 0.1154 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.1417 | 0.0250 | 0.0000 |
| frame_fa_off | 0.2500 | 0.0417 | 0.0000 |
| cell_fpr_off | 0.0354 | 0.0063 | 0.0000 |
| cell_fpr_on_neg | 0.2264 | 0.0597 | 0.0050 |
