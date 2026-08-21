# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **probe** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 144 | 72 | 72 | 72 | 15 | 27 | 30 | 3 | 189 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 15 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 27 |
| H | 0.2000 [0.0645, 0.3529] | 0.0988 [0.0286, 0.1961] | 30 |
| **any tier (frame detection rate)** | 0.0833 [0.0270, 0.1528] | — | 72 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1250 [0.0533, 0.2083] |
| cell FPR (off frames) | 0.0285 [0.0085, 0.0544] |
| cell FPR (negative cells of on frames) | 0.0320 [0.0113, 0.0578] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0526 [0.0083, 0.1129] | 0.0417 [0.0060, 0.0879] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0389 [0.0094, 0.0767] |
| 3b [8,12) m | 0.0741 [0.0000, 0.1786] | 0.0333 [0.0091, 0.0629] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0576 [0.0168, 0.0997] |
| cell recall | 0.0423 [0.0110, 0.0821] |
| cell precision | 0.0899 [0.0323, 0.1471] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 15 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 27 |
| H | 0.2000 [0.0645, 0.3529] | 0.0988 [0.0286, 0.1961] | 30 |
| **any tier (frame detection rate)** | 0.0833 [0.0270, 0.1528] | — | 72 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1250 [0.0533, 0.2083] |
| cell FPR (off frames) | 0.0285 [0.0085, 0.0544] |
| cell FPR (negative cells of on frames) | 0.0320 [0.0113, 0.0578] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0526 [0.0083, 0.1129] | 0.0417 [0.0060, 0.0879] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0389 [0.0094, 0.0767] |
| 3b [8,12) m | 0.0741 [0.0000, 0.1786] | 0.0333 [0.0091, 0.0629] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0576 [0.0168, 0.0997] |
| cell recall | 0.0423 [0.0110, 0.0821] |
| cell precision | 0.0899 [0.0323, 0.1471] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.0946 | 0.0576 | 0.0472 |
| cell_recall | 0.0794 | 0.0423 | 0.0317 |
| cell_precision | 0.1172 | 0.0899 | 0.0923 |
| frame_det_rate | 0.1389 | 0.0833 | 0.0556 |
| frame_recall_V | 0.1333 | 0.0000 | 0.0000 |
| frame_recall_E | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_H | 0.2667 | 0.2000 | 0.1333 |
| cell_recall_V | 0.0444 | 0.0000 | 0.0000 |
| cell_recall_E | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_H | 0.1605 | 0.0988 | 0.0741 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.1053 | 0.0526 | 0.0351 |
| band3_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_recall | 0.1111 | 0.0741 | 0.0741 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0639 | 0.0417 | 0.0278 |
| band3_cell_fpr_off | 0.0500 | 0.0389 | 0.0306 |
| band4_cell_fpr_off | 0.0500 | 0.0333 | 0.0278 |
| frame_fa_off | 0.1667 | 0.1250 | 0.1250 |
| cell_fpr_off | 0.0410 | 0.0285 | 0.0215 |
| cell_fpr_on_neg | 0.0432 | 0.0320 | 0.0224 |
