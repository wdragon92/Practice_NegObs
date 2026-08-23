# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 96 | 48 | 48 | 39 | 12 | 0 | 27 | 1 | 189 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9167 [0.7273, 1.0000] | 0.5167 [0.3200, 0.7200] | 12 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.2963 [0.1304, 0.4783] | 0.1163 [0.0450, 0.1957] | 27 |
| **any tier (frame detection rate)** | 0.4872 [0.3333, 0.6429] | — | 39 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3333 [0.2000, 0.4706] |
| cell FPR (off frames) | 0.0406 [0.0223, 0.0610] |
| cell FPR (negative cells of on frames) | 0.0571 [0.0347, 0.0827] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.1333 [0.0766, 0.1955] |
| 3b [8,12) m | 0.2434 [0.1487, 0.3446] | 0.0292 [0.0042, 0.0615] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2893 [0.1915, 0.3718] |
| cell recall | 0.2434 [0.1487, 0.3446] |
| cell precision | 0.3566 [0.2549, 0.4385] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9167 [0.7273, 1.0000] | 0.5167 [0.3200, 0.7200] | 12 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.2963 [0.1304, 0.4783] | 0.1163 [0.0450, 0.1957] | 27 |
| **any tier (frame detection rate)** | 0.4872 [0.3333, 0.6429] | — | 39 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3333 [0.2000, 0.4706] |
| cell FPR (off frames) | 0.0406 [0.0223, 0.0610] |
| cell FPR (negative cells of on frames) | 0.0571 [0.0347, 0.0827] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | n/a [n/a, n/a] | 0.1333 [0.0766, 0.1955] |
| 3b [8,12) m | 0.2434 [0.1487, 0.3446] | 0.0292 [0.0042, 0.0615] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2893 [0.1915, 0.3718] |
| cell recall | 0.2434 [0.1487, 0.3446] |
| cell precision | 0.3566 [0.2549, 0.4385] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3968 | 0.2893 | 0.2222 |
| cell_recall | 0.3915 | 0.2434 | 0.1587 |
| cell_precision | 0.4022 | 0.3566 | 0.3704 |
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
| band1_cell_fpr_off | 0.0042 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.1583 | 0.1333 | 0.0875 |
| band4_cell_fpr_off | 0.0542 | 0.0292 | 0.0083 |
| frame_fa_off | 0.3750 | 0.3333 | 0.2708 |
| cell_fpr_off | 0.0542 | 0.0406 | 0.0240 |
| cell_fpr_on_neg | 0.0752 | 0.0571 | 0.0363 |
