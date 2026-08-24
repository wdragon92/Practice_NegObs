# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/runs/v3a/rgb_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.3871 [0.2892, 0.4884] | 0.2318 [0.1634, 0.3032] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.5000 [0.3824, 0.6136] | 0.1829 [0.1290, 0.2443] | 72 |
| **any tier (frame detection rate)** | 0.4364 [0.3613, 0.5125] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2257 [0.1769, 0.2746] |
| cell FPR (off frames) | 0.0215 [0.0160, 0.0276] |
| cell FPR (negative cells of on frames) | 0.0193 [0.0131, 0.0264] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2576 [0.1260, 0.4096] | 0.0021 [0.0000, 0.0056] |
| 3a [5,8) m | 0.1785 [0.1100, 0.2530] | 0.0090 [0.0028, 0.0171] |
| 3b [8,12) m | 0.2348 [0.1864, 0.2855] | 0.0750 [0.0566, 0.0942] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3080 [0.2452, 0.3687] |
| cell recall | 0.2142 [0.1655, 0.2652] |
| cell precision | 0.5480 [0.4527, 0.6357] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.3871 [0.2892, 0.4884] | 0.2318 [0.1634, 0.3032] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.5000 [0.3824, 0.6136] | 0.1829 [0.1290, 0.2443] | 72 |
| **any tier (frame detection rate)** | 0.4364 [0.3613, 0.5125] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2257 [0.1769, 0.2746] |
| cell FPR (off frames) | 0.0215 [0.0160, 0.0276] |
| cell FPR (negative cells of on frames) | 0.0193 [0.0131, 0.0264] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2576 [0.1260, 0.4096] | 0.0021 [0.0000, 0.0056] |
| 3a [5,8) m | 0.1785 [0.1100, 0.2530] | 0.0090 [0.0028, 0.0171] |
| 3b [8,12) m | 0.2348 [0.1864, 0.2855] | 0.0750 [0.0566, 0.0942] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3080 [0.2452, 0.3687] |
| cell recall | 0.2142 [0.1655, 0.2652] |
| cell precision | 0.5480 [0.4527, 0.6357] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3910 | 0.3080 | 0.2082 |
| cell_recall | 0.3392 | 0.2142 | 0.1250 |
| cell_precision | 0.4615 | 0.5480 | 0.6224 |
| frame_det_rate | 0.5697 | 0.4364 | 0.3212 |
| frame_recall_V | 0.4839 | 0.3871 | 0.3548 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.6806 | 0.5000 | 0.2778 |
| cell_recall_V | 0.3372 | 0.2318 | 0.1471 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.3426 | 0.1829 | 0.0856 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.4167 | 0.2576 | 0.1439 |
| band3_cell_recall | 0.2651 | 0.1785 | 0.1050 |
| band4_cell_recall | 0.3803 | 0.2348 | 0.1379 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0097 | 0.0021 | 0.0007 |
| band3_cell_fpr_off | 0.0194 | 0.0090 | 0.0028 |
| band4_cell_fpr_off | 0.1604 | 0.0750 | 0.0299 |
| frame_fa_off | 0.3715 | 0.2257 | 0.1042 |
| cell_fpr_off | 0.0474 | 0.0215 | 0.0083 |
| cell_fpr_on_neg | 0.0443 | 0.0193 | 0.0094 |
