# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.45 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 369 | 219 | 45 | 96 | 7 | 2856 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6484 [0.5848, 0.7113] | 0.2972 [0.2559, 0.3420] | 219 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.2083 [0.1290, 0.2929] | 0.0934 [0.0569, 0.1323] | 96 |
| **any tier (frame detection rate)** | 0.4390 [0.3875, 0.4901] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1078 [0.0791, 0.1393] |
| cell FPR (off frames) | 0.0104 [0.0067, 0.0147] |
| cell FPR (negative cells of on frames) | 0.0345 [0.0249, 0.0450] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.1958 [0.1250, 0.2711] | 0.0020 [0.0000, 0.0061] |
| 3a [5,8) m | 0.1582 [0.1231, 0.1971] | 0.0049 [0.0010, 0.0102] |
| 3b [8,12) m | 0.2925 [0.2538, 0.3327] | 0.0348 [0.0240, 0.0467] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3423 [0.3031, 0.3810] |
| cell recall | 0.2258 [0.1945, 0.2591] |
| cell precision | 0.7065 [0.6539, 0.7560] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.45

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6575 [0.5938, 0.7198] | 0.3126 [0.2701, 0.3579] | 219 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.2083 [0.1290, 0.2929] | 0.1019 [0.0623, 0.1439] | 96 |
| **any tier (frame detection rate)** | 0.4444 [0.3934, 0.4958] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1176 [0.0873, 0.1497] |
| cell FPR (off frames) | 0.0113 [0.0076, 0.0156] |
| cell FPR (negative cells of on frames) | 0.0390 [0.0290, 0.0500] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2037 [0.1308, 0.2809] | 0.0025 [0.0000, 0.0070] |
| 3a [5,8) m | 0.1672 [0.1315, 0.2070] | 0.0049 [0.0010, 0.0102] |
| 3b [8,12) m | 0.3088 [0.2694, 0.3501] | 0.0377 [0.0267, 0.0500] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3546 [0.3159, 0.3929] |
| cell recall | 0.2381 [0.2059, 0.2722] |
| cell precision | 0.6946 [0.6431, 0.7422] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4184 | 0.3423 | 0.2691 |
| cell_recall | 0.3004 | 0.2258 | 0.1642 |
| cell_precision | 0.6892 | 0.7065 | 0.7444 |
| frame_det_rate | 0.4770 | 0.4390 | 0.3875 |
| frame_recall_V | 0.7078 | 0.6484 | 0.5890 |
| frame_recall_E | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_H | 0.2188 | 0.2083 | 0.1458 |
| cell_recall_V | 0.3961 | 0.2972 | 0.2216 |
| cell_recall_E | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_H | 0.1210 | 0.0934 | 0.0446 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.2593 | 0.1958 | 0.1323 |
| band3_cell_recall | 0.2222 | 0.1582 | 0.1235 |
| band4_cell_recall | 0.3823 | 0.2925 | 0.2102 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0025 | 0.0020 | 0.0015 |
| band3_cell_fpr_off | 0.0078 | 0.0049 | 0.0025 |
| band4_cell_fpr_off | 0.0471 | 0.0348 | 0.0235 |
| frame_fa_off | 0.1446 | 0.1078 | 0.0711 |
| cell_fpr_off | 0.0143 | 0.0104 | 0.0069 |
| cell_fpr_on_neg | 0.0509 | 0.0345 | 0.0198 |
