# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 72 | 48 | 24 | 39 | 12 | 0 | 27 | 1 | 189 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9167 [0.7143, 1.0000] | 0.5167 [0.3250, 0.7200] | 12 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.2963 [0.1304, 0.4800] | 0.1163 [0.0458, 0.1966] | 27 |
| **any tier (frame detection rate)** | 0.4872 [0.3265, 0.6410] | — | 39 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (negative cells of on frames) | 0.0571 [0.0347, 0.0828] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.2434 [0.1492, 0.3443] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3297 [0.2281, 0.4159] |
| cell recall | 0.2434 [0.1492, 0.3443] |
| cell precision | 0.5111 [0.4595, 0.5614] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9167 [0.7143, 1.0000] | 0.5167 [0.3250, 0.7200] | 12 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.2963 [0.1304, 0.4800] | 0.1163 [0.0458, 0.1966] | 27 |
| **any tier (frame detection rate)** | 0.4872 [0.3265, 0.6410] | — | 39 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (negative cells of on frames) | 0.0571 [0.0347, 0.0828] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.2434 [0.1492, 0.3443] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3297 [0.2281, 0.4159] |
| cell recall | 0.2434 [0.1492, 0.3443] |
| cell precision | 0.5111 [0.4595, 0.5614] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4596 | 0.3297 | 0.2429 |
| cell_recall | 0.3915 | 0.2434 | 0.1587 |
| cell_precision | 0.5564 | 0.5111 | 0.5172 |
| frame_det_rate | 0.6410 | 0.4872 | 0.3590 |
| frame_recall_V | 1.0000 | 0.9167 | 0.8333 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.4815 | 0.2963 | 0.1481 |
| cell_recall_V | 0.6833 | 0.5167 | 0.4167 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.2558 | 0.1163 | 0.0388 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | n/a | n/a | n/a |
| band4_cell_recall | 0.3915 | 0.2434 | 0.1587 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0083 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| frame_fa_off | 0.0417 | 0.0000 | 0.0000 |
| cell_fpr_off | 0.0021 | 0.0000 | 0.0000 |
| cell_fpr_on_neg | 0.0752 | 0.0571 | 0.0363 |
