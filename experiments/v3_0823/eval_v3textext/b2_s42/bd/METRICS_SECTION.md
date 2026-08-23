# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.45 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.1828 [0.1075, 0.2637] | 0.0990 [0.0512, 0.1514] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.0139 [0.0000, 0.0469] | 0.0023 [0.0000, 0.0079] | 72 |
| **any tier (frame detection rate)** | 0.1091 [0.0643, 0.1582] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0521 [0.0277, 0.0793] |
| cell FPR (off frames) | 0.0108 [0.0050, 0.0176] |
| cell FPR (negative cells of on frames) | 0.0197 [0.0118, 0.0287] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0985 [0.0080, 0.2059] | 0.0146 [0.0036, 0.0282] |
| 3a [5,8) m | 0.1129 [0.0603, 0.1703] | 0.0250 [0.0125, 0.0395] |
| 3b [8,12) m | 0.0318 [0.0135, 0.0546] | 0.0035 [0.0000, 0.0088] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1078 [0.0552, 0.1634] |
| cell recall | 0.0642 [0.0321, 0.0998] |
| cell precision | 0.3362 [0.1858, 0.4905] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.45

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.2043 [0.1263, 0.2875] | 0.1146 [0.0629, 0.1707] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.0139 [0.0000, 0.0469] | 0.0023 [0.0000, 0.0079] | 72 |
| **any tier (frame detection rate)** | 0.1212 [0.0745, 0.1728] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0556 [0.0311, 0.0842] |
| cell FPR (off frames) | 0.0134 [0.0064, 0.0216] |
| cell FPR (negative cells of on frames) | 0.0235 [0.0138, 0.0345] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0007 [0.0000, 0.0022] |
| 2 [2,5) m | 0.1061 [0.0080, 0.2247] | 0.0181 [0.0061, 0.0326] |
| 3a [5,8) m | 0.1312 [0.0730, 0.1960] | 0.0299 [0.0156, 0.0465] |
| 3b [8,12) m | 0.0379 [0.0177, 0.0622] | 0.0049 [0.0007, 0.0118] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1208 [0.0656, 0.1784] |
| cell recall | 0.0742 [0.0393, 0.1123] |
| cell precision | 0.3260 [0.1855, 0.4764] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.1717 | 0.1078 | 0.0713 |
| cell_recall | 0.1183 | 0.0642 | 0.0392 |
| cell_precision | 0.3128 | 0.3362 | 0.3950 |
| frame_det_rate | 0.1939 | 0.1091 | 0.0606 |
| frame_recall_V | 0.2903 | 0.1828 | 0.1075 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.0694 | 0.0139 | 0.0000 |
| cell_recall_V | 0.1745 | 0.0990 | 0.0612 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.0185 | 0.0023 | 0.0000 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.1591 | 0.0985 | 0.0530 |
| band3_cell_recall | 0.1916 | 0.1129 | 0.0682 |
| band4_cell_recall | 0.0727 | 0.0318 | 0.0212 |
| band1_cell_fpr_off | 0.0014 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0306 | 0.0146 | 0.0090 |
| band3_cell_fpr_off | 0.0458 | 0.0250 | 0.0111 |
| band4_cell_fpr_off | 0.0201 | 0.0035 | 0.0000 |
| frame_fa_off | 0.0833 | 0.0521 | 0.0312 |
| cell_fpr_off | 0.0245 | 0.0108 | 0.0050 |
| cell_fpr_on_neg | 0.0375 | 0.0197 | 0.0094 |
