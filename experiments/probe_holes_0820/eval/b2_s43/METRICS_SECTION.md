# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **probe** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 144 | 72 | 72 | 72 | 15 | 27 | 30 | 3 | 189 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.7111 [0.5714, 0.8846] | 15 |
| E | 0.2593 [0.1034, 0.4348] | 0.1905 [0.0702, 0.3235] | 27 |
| H | 0.7000 [0.5312, 0.8611] | 0.4938 [0.3562, 0.6517] | 30 |
| **any tier (frame detection rate)** | 0.5972 [0.4848, 0.7101] | — | 72 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.8056 [0.7077, 0.8939] |
| cell FPR (off frames) | 0.2403 [0.1884, 0.2929] |
| cell FPR (negative cells of on frames) | 0.2790 [0.2278, 0.3319] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.5526 [0.4245, 0.6733] | 0.3139 [0.2188, 0.4121] |
| 3a [5,8) m | 0.2333 [0.0789, 0.4118] | 0.3250 [0.2667, 0.3821] |
| 3b [8,12) m | 0.5185 [0.3333, 0.7083] | 0.3222 [0.2500, 0.4000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1736 [0.1373, 0.2092] |
| cell recall | 0.4444 [0.3552, 0.5375] |
| cell precision | 0.1078 [0.0833, 0.1330] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.7111 [0.5714, 0.8846] | 15 |
| E | 0.2593 [0.1034, 0.4348] | 0.1905 [0.0702, 0.3235] | 27 |
| H | 0.7000 [0.5312, 0.8611] | 0.4938 [0.3562, 0.6517] | 30 |
| **any tier (frame detection rate)** | 0.5972 [0.4848, 0.7101] | — | 72 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.8056 [0.7077, 0.8939] |
| cell FPR (off frames) | 0.2403 [0.1884, 0.2929] |
| cell FPR (negative cells of on frames) | 0.2790 [0.2278, 0.3319] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.5526 [0.4245, 0.6733] | 0.3139 [0.2188, 0.4121] |
| 3a [5,8) m | 0.2333 [0.0789, 0.4118] | 0.3250 [0.2667, 0.3821] |
| 3b [8,12) m | 0.5185 [0.3333, 0.7083] | 0.3222 [0.2500, 0.4000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1736 [0.1373, 0.2092] |
| cell recall | 0.4444 [0.3552, 0.5375] |
| cell precision | 0.1078 [0.0833, 0.1330] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.1533 | 0.1736 | 0.1156 |
| cell_recall | 0.6561 | 0.4444 | 0.1376 |
| cell_precision | 0.0868 | 0.1078 | 0.0996 |
| frame_det_rate | 0.8889 | 0.5972 | 0.2778 |
| frame_recall_V | 1.0000 | 1.0000 | 0.5333 |
| frame_recall_E | 0.8148 | 0.2593 | 0.0741 |
| frame_recall_H | 0.9000 | 0.7000 | 0.3333 |
| cell_recall_V | 0.8222 | 0.7111 | 0.2444 |
| cell_recall_E | 0.5714 | 0.1905 | 0.0317 |
| cell_recall_H | 0.6296 | 0.4938 | 0.1605 |
| band1_cell_recall | 0.0556 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.7105 | 0.5526 | 0.1754 |
| band3_cell_recall | 0.6667 | 0.2333 | 0.0333 |
| band4_cell_recall | 0.8148 | 0.5185 | 0.1852 |
| band1_cell_fpr_off | 0.0056 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.5889 | 0.3139 | 0.0722 |
| band3_cell_fpr_off | 0.5750 | 0.3250 | 0.1583 |
| band4_cell_fpr_off | 0.7194 | 0.3222 | 0.0806 |
| frame_fa_off | 0.9583 | 0.8056 | 0.5139 |
| cell_fpr_off | 0.4722 | 0.2403 | 0.0778 |
| cell_fpr_on_neg | 0.4996 | 0.2790 | 0.0983 |
