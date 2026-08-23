# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.45 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9140 [0.8511, 0.9667] | 0.6380 [0.5724, 0.7026] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.7222 [0.6111, 0.8254] | 0.6713 [0.5674, 0.7626] | 72 |
| **any tier (frame detection rate)** | 0.8303 [0.7702, 0.8848] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.8854 [0.8476, 0.9211] |
| cell FPR (off frames) | 0.2757 [0.2549, 0.2972] |
| cell FPR (negative cells of on frames) | 0.2355 [0.2147, 0.2566] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2955 [0.1835, 0.4180] | 0.1181 [0.0911, 0.1477] |
| 3a [5,8) m | 0.6535 [0.5863, 0.7174] | 0.2931 [0.2582, 0.3289] |
| 3b [8,12) m | 0.7455 [0.6838, 0.8025] | 0.6917 [0.6530, 0.7292] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3361 [0.2912, 0.3780] |
| cell recall | 0.6500 [0.5938, 0.7032] |
| cell precision | 0.2266 [0.1899, 0.2634] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.45

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.9247 [0.8646, 0.9753] | 0.6823 [0.6183, 0.7439] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.7778 [0.6750, 0.8701] | 0.7245 [0.6201, 0.8144] | 72 |
| **any tier (frame detection rate)** | 0.8606 [0.8045, 0.9108] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.9097 [0.8758, 0.9416] |
| cell FPR (off frames) | 0.3127 [0.2902, 0.3362] |
| cell FPR (negative cells of on frames) | 0.2623 [0.2395, 0.2847] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.3788 [0.2609, 0.5042] | 0.1514 [0.1186, 0.1872] |
| 3a [5,8) m | 0.7087 [0.6427, 0.7688] | 0.3528 [0.3142, 0.3923] |
| 3b [8,12) m | 0.7833 [0.7227, 0.8384] | 0.7465 [0.7098, 0.7831] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3325 [0.2876, 0.3743] |
| cell recall | 0.6975 [0.6420, 0.7488] |
| cell precision | 0.2183 [0.1829, 0.2537] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3093 | 0.3361 | 0.3187 |
| cell_recall | 0.8000 | 0.6500 | 0.4075 |
| cell_precision | 0.1917 | 0.2266 | 0.2616 |
| frame_det_rate | 0.9152 | 0.8303 | 0.6970 |
| frame_recall_V | 0.9570 | 0.9140 | 0.8065 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.8611 | 0.7222 | 0.5556 |
| cell_recall_V | 0.8034 | 0.6380 | 0.4076 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.7940 | 0.6713 | 0.4074 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.7197 | 0.2955 | 0.0606 |
| band3_cell_recall | 0.7953 | 0.6535 | 0.3543 |
| band4_cell_recall | 0.8515 | 0.7455 | 0.5242 |
| band1_cell_fpr_off | 0.0049 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.2917 | 0.1181 | 0.0215 |
| band3_cell_fpr_off | 0.5139 | 0.2931 | 0.1257 |
| band4_cell_fpr_off | 0.8486 | 0.6917 | 0.4347 |
| frame_fa_off | 0.9479 | 0.8854 | 0.7604 |
| cell_fpr_off | 0.4148 | 0.2757 | 0.1455 |
| cell_fpr_on_neg | 0.3636 | 0.2355 | 0.1189 |
