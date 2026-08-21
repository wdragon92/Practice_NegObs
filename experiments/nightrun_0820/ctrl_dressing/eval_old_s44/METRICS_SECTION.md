# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/nightrun_0820/ctrl_dressing/eval_old_s44/per_frame_src.csv`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 96 | 48 | 48 | 24 | 24 | 0 | 0 | 2 | 237 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9167 [0.7857, 1.0000] | 0.4346 [0.3318, 0.5413] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 0.9167 [0.7857, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3542 [0.2195, 0.4906] |
| cell FPR (off frames) | 0.0677 [0.0389, 0.0992] |
| cell FPR (negative cells of on frames) | 0.1342 [0.0994, 0.1698] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0333 [0.0000, 0.0884] |
| 3a [5,8) m | 0.4444 [0.2841, 0.6129] | 0.1000 [0.0542, 0.1524] |
| 3b [8,12) m | 0.6381 [0.4900, 0.7746] | 0.1375 [0.0780, 0.2038] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4104 [0.2985, 0.5009] |
| cell recall | 0.4346 [0.3318, 0.5413] |
| cell precision | 0.3887 [0.2524, 0.5179] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9167 [0.7857, 1.0000] | 0.4346 [0.3318, 0.5413] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 0.9167 [0.7857, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3542 [0.2195, 0.4906] |
| cell FPR (off frames) | 0.0677 [0.0389, 0.0992] |
| cell FPR (negative cells of on frames) | 0.1342 [0.0994, 0.1698] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0000 [0.0000, 0.0000] | 0.0333 [0.0000, 0.0884] |
| 3a [5,8) m | 0.4444 [0.2841, 0.6129] | 0.1000 [0.0542, 0.1524] |
| 3b [8,12) m | 0.6381 [0.4900, 0.7746] | 0.1375 [0.0780, 0.2038] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4104 [0.2985, 0.5009] |
| cell recall | 0.4346 [0.3318, 0.5413] |
| cell precision | 0.3887 [0.2524, 0.5179] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4184 | 0.4104 | 0.3866 |
| cell_recall | 0.5190 | 0.4346 | 0.3418 |
| cell_precision | 0.3504 | 0.3887 | 0.4451 |
| frame_det_rate | 0.9167 | 0.9167 | 0.8750 |
| frame_recall_V | 0.9167 | 0.9167 | 0.8750 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | n/a | n/a | n/a |
| cell_recall_V | 0.5190 | 0.4346 | 0.3418 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | n/a | n/a | n/a |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | 0.0588 | 0.0000 | 0.0000 |
| band3_cell_recall | 0.5309 | 0.4444 | 0.3704 |
| band4_cell_recall | 0.7333 | 0.6381 | 0.4857 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0333 | 0.0333 | 0.0125 |
| band3_cell_fpr_off | 0.1542 | 0.1000 | 0.0583 |
| band4_cell_fpr_off | 0.2042 | 0.1375 | 0.0833 |
| frame_fa_off | 0.4167 | 0.3542 | 0.2917 |
| cell_fpr_off | 0.0979 | 0.0677 | 0.0385 |
| cell_fpr_on_neg | 0.1853 | 0.1342 | 0.0885 |
