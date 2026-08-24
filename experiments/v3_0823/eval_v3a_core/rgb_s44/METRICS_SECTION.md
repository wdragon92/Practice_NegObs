# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/v3_0823/runs/v3a/rgb_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 369 | 219 | 45 | 96 | 7 | 2856 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6393 [0.5760, 0.7028] | 0.2987 [0.2541, 0.3460] | 219 |
| E | 0.3333 [0.2000, 0.4750] | 0.0977 [0.0511, 0.1535] | 45 |
| H | 0.5312 [0.4304, 0.6296] | 0.3163 [0.2519, 0.3806] | 96 |
| **any tier (frame detection rate)** | 0.5718 [0.5217, 0.6223] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1103 [0.0799, 0.1415] |
| cell FPR (off frames) | 0.0142 [0.0097, 0.0192] |
| cell FPR (negative cells of on frames) | 0.0632 [0.0492, 0.0785] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.1825 [0.1206, 0.2517] | 0.0010 [0.0000, 0.0031] |
| 3a [5,8) m | 0.2334 [0.1868, 0.2839] | 0.0255 [0.0157, 0.0368] |
| 3b [8,12) m | 0.3510 [0.3138, 0.3894] | 0.0304 [0.0199, 0.0420] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3868 [0.3470, 0.4257] |
| cell recall | 0.2777 [0.2426, 0.3138] |
| cell precision | 0.6375 [0.5813, 0.6922] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6393 [0.5760, 0.7028] | 0.2987 [0.2541, 0.3460] | 219 |
| E | 0.3333 [0.2000, 0.4750] | 0.0977 [0.0511, 0.1535] | 45 |
| H | 0.5312 [0.4304, 0.6296] | 0.3163 [0.2519, 0.3806] | 96 |
| **any tier (frame detection rate)** | 0.5718 [0.5217, 0.6223] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1103 [0.0799, 0.1415] |
| cell FPR (off frames) | 0.0142 [0.0097, 0.0192] |
| cell FPR (negative cells of on frames) | 0.0632 [0.0492, 0.0785] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.1825 [0.1206, 0.2517] | 0.0010 [0.0000, 0.0031] |
| 3a [5,8) m | 0.2334 [0.1868, 0.2839] | 0.0255 [0.0157, 0.0368] |
| 3b [8,12) m | 0.3510 [0.3138, 0.3894] | 0.0304 [0.0199, 0.0420] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3868 [0.3470, 0.4257] |
| cell recall | 0.2777 [0.2426, 0.3138] |
| cell precision | 0.6375 [0.5813, 0.6922] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4884 | 0.3868 | 0.2550 |
| cell_recall | 0.4352 | 0.2777 | 0.1555 |
| cell_precision | 0.5564 | 0.6375 | 0.7093 |
| frame_det_rate | 0.7995 | 0.5718 | 0.3984 |
| frame_recall_V | 0.7991 | 0.6393 | 0.4977 |
| frame_recall_E | 0.6889 | 0.3333 | 0.1778 |
| frame_recall_H | 0.8542 | 0.5312 | 0.3125 |
| cell_recall_V | 0.4377 | 0.2987 | 0.1795 |
| cell_recall_E | 0.2500 | 0.0977 | 0.0431 |
| cell_recall_H | 0.5478 | 0.3163 | 0.1401 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.3307 | 0.1825 | 0.0899 |
| band3_cell_recall | 0.3726 | 0.2334 | 0.1246 |
| band4_cell_recall | 0.5347 | 0.3510 | 0.2034 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0132 | 0.0010 | 0.0000 |
| band3_cell_fpr_off | 0.0578 | 0.0255 | 0.0078 |
| band4_cell_fpr_off | 0.1034 | 0.0304 | 0.0044 |
| frame_fa_off | 0.2157 | 0.1103 | 0.0270 |
| cell_fpr_off | 0.0436 | 0.0142 | 0.0031 |
| cell_fpr_on_neg | 0.1197 | 0.0632 | 0.0296 |
