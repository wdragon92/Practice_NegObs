# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/runs/v3a/rgb_s42_aux/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.5484 [0.4479, 0.6512] | 0.5208 [0.4368, 0.6004] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.6250 [0.5079, 0.7369] | 0.4815 [0.3855, 0.5733] | 72 |
| **any tier (frame detection rate)** | 0.5818 [0.5060, 0.6568] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.5417 [0.4828, 0.6000] |
| cell FPR (off frames) | 0.1899 [0.1621, 0.2189] |
| cell FPR (negative cells of on frames) | 0.1268 [0.1052, 0.1491] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0063 [0.0007, 0.0135] |
| 2 [2,5) m | 0.3182 [0.1557, 0.4917] | 0.1333 [0.0976, 0.1709] |
| 3a [5,8) m | 0.4646 [0.3714, 0.5531] | 0.2104 [0.1719, 0.2512] |
| 3b [8,12) m | 0.5894 [0.5174, 0.6608] | 0.4097 [0.3589, 0.4615] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3494 [0.2953, 0.4006] |
| cell recall | 0.5067 [0.4424, 0.5677] |
| cell precision | 0.2667 [0.2171, 0.3183] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.5484 [0.4479, 0.6512] | 0.5208 [0.4368, 0.6004] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.6250 [0.5079, 0.7369] | 0.4815 [0.3855, 0.5733] | 72 |
| **any tier (frame detection rate)** | 0.5818 [0.5060, 0.6568] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.5417 [0.4828, 0.6000] |
| cell FPR (off frames) | 0.1899 [0.1621, 0.2189] |
| cell FPR (negative cells of on frames) | 0.1268 [0.1052, 0.1491] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0063 [0.0007, 0.0135] |
| 2 [2,5) m | 0.3182 [0.1557, 0.4917] | 0.1333 [0.0976, 0.1709] |
| 3a [5,8) m | 0.4646 [0.3714, 0.5531] | 0.2104 [0.1719, 0.2512] |
| 3b [8,12) m | 0.5894 [0.5174, 0.6608] | 0.4097 [0.3589, 0.4615] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3494 [0.2953, 0.4006] |
| cell recall | 0.5067 [0.4424, 0.5677] |
| cell precision | 0.2667 [0.2171, 0.3183] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3361 | 0.3494 | 0.3459 |
| cell_recall | 0.5992 | 0.5067 | 0.4025 |
| cell_precision | 0.2335 | 0.2667 | 0.3032 |
| frame_det_rate | 0.6667 | 0.5818 | 0.4788 |
| frame_recall_V | 0.6022 | 0.5484 | 0.4839 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.7500 | 0.6250 | 0.4722 |
| cell_recall_V | 0.5846 | 0.5208 | 0.4401 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.6250 | 0.4815 | 0.3356 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.3864 | 0.3182 | 0.2197 |
| band3_cell_recall | 0.5827 | 0.4646 | 0.3333 |
| band4_cell_recall | 0.6758 | 0.5894 | 0.4955 |
| band1_cell_fpr_off | 0.0132 | 0.0063 | 0.0000 |
| band2_cell_fpr_off | 0.1778 | 0.1333 | 0.0924 |
| band3_cell_fpr_off | 0.2979 | 0.2104 | 0.1285 |
| band4_cell_fpr_off | 0.5375 | 0.4097 | 0.3042 |
| frame_fa_off | 0.7118 | 0.5417 | 0.4097 |
| cell_fpr_off | 0.2566 | 0.1899 | 0.1313 |
| cell_fpr_on_neg | 0.1934 | 0.1268 | 0.0776 |
