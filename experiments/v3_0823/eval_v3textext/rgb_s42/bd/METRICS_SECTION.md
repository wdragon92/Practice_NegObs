# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.63 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.3763 [0.2785, 0.4762] | 0.2005 [0.1344, 0.2751] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.2222 [0.1304, 0.3226] | 0.2060 [0.1142, 0.3055] | 72 |
| **any tier (frame detection rate)** | 0.3091 [0.2387, 0.3818] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0521 [0.0279, 0.0793] |
| cell FPR (off frames) | 0.0057 [0.0026, 0.0095] |
| cell FPR (negative cells of on frames) | 0.0211 [0.0129, 0.0309] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.1515 [0.0408, 0.2941] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.2756 [0.2036, 0.3526] | 0.0118 [0.0052, 0.0195] |
| 3b [8,12) m | 0.1788 [0.1244, 0.2365] | 0.0111 [0.0021, 0.0222] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3092 [0.2355, 0.3806] |
| cell recall | 0.2025 [0.1482, 0.2607] |
| cell precision | 0.6532 [0.5435, 0.7512] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.63

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.2796 [0.1895, 0.3736] | 0.1341 [0.0845, 0.1886] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.2222 [0.1304, 0.3226] | 0.1458 [0.0777, 0.2235] | 72 |
| **any tier (frame detection rate)** | 0.2545 [0.1892, 0.3230] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0451 [0.0226, 0.0707] |
| cell FPR (off frames) | 0.0040 [0.0017, 0.0068] |
| cell FPR (negative cells of on frames) | 0.0145 [0.0080, 0.0223] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0833 [0.0000, 0.1944] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.1995 [0.1433, 0.2596] | 0.0076 [0.0029, 0.0133] |
| 3b [8,12) m | 0.1197 [0.0742, 0.1679] | 0.0083 [0.0014, 0.0171] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2282 [0.1668, 0.2886] |
| cell recall | 0.1383 [0.0976, 0.1817] |
| cell precision | 0.6510 [0.5300, 0.7610] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3856 | 0.3092 | 0.1922 |
| cell_recall | 0.2950 | 0.2025 | 0.1125 |
| cell_precision | 0.5566 | 0.6532 | 0.6585 |
| frame_det_rate | 0.4424 | 0.3091 | 0.2242 |
| frame_recall_V | 0.5161 | 0.3763 | 0.2366 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.3472 | 0.2222 | 0.2083 |
| cell_recall_V | 0.2982 | 0.2005 | 0.1055 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.2894 | 0.2060 | 0.1250 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.2424 | 0.1515 | 0.0455 |
| band3_cell_recall | 0.3648 | 0.2756 | 0.1601 |
| band4_cell_recall | 0.2773 | 0.1788 | 0.1030 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0007 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0292 | 0.0118 | 0.0063 |
| band4_cell_fpr_off | 0.0319 | 0.0111 | 0.0063 |
| frame_fa_off | 0.1250 | 0.0521 | 0.0382 |
| cell_fpr_off | 0.0155 | 0.0057 | 0.0031 |
| cell_fpr_on_neg | 0.0423 | 0.0211 | 0.0114 |
