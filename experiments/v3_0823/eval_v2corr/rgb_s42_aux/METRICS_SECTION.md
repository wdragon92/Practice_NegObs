# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s42_aux/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.43 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 369 | 219 | 45 | 96 | 7 | 2856 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.5982 [0.5333, 0.6634] | 0.4411 [0.3772, 0.5045] | 219 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.7188 [0.6279, 0.8081] | 0.6072 [0.5333, 0.6771] | 96 |
| **any tier (frame detection rate)** | 0.5501 [0.5000, 0.6011] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1667 [0.1311, 0.2028] |
| cell FPR (off frames) | 0.0230 [0.0167, 0.0300] |
| cell FPR (negative cells of on frames) | 0.0594 [0.0480, 0.0714] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.3810 [0.2833, 0.4798] | 0.0010 [0.0000, 0.0025] |
| 3a [5,8) m | 0.3704 [0.3082, 0.4349] | 0.0221 [0.0120, 0.0337] |
| 3b [8,12) m | 0.4823 [0.4315, 0.5336] | 0.0691 [0.0513, 0.0879] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5209 [0.4728, 0.5659] |
| cell recall | 0.4142 [0.3646, 0.4640] |
| cell precision | 0.7017 [0.6523, 0.7474] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.43

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6210 [0.5565, 0.6861] | 0.4604 [0.3963, 0.5242] | 219 |
| E | 0.0222 [0.0000, 0.0741] | 0.0029 [0.0000, 0.0096] | 45 |
| H | 0.7396 [0.6504, 0.8256] | 0.6794 [0.6071, 0.7457] | 96 |
| **any tier (frame detection rate)** | 0.5718 [0.5222, 0.6240] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1985 [0.1601, 0.2382] |
| cell FPR (off frames) | 0.0327 [0.0246, 0.0414] |
| cell FPR (negative cells of on frames) | 0.0732 [0.0602, 0.0866] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.4074 [0.3090, 0.5076] | 0.0025 [0.0000, 0.0057] |
| 3a [5,8) m | 0.4052 [0.3419, 0.4687] | 0.0319 [0.0186, 0.0468] |
| 3b [8,12) m | 0.5054 [0.4545, 0.5571] | 0.0966 [0.0751, 0.1187] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5276 [0.4807, 0.5714] |
| cell recall | 0.4405 [0.3896, 0.4910] |
| cell precision | 0.6576 [0.6081, 0.7035] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5261 | 0.5209 | 0.4717 |
| cell_recall | 0.4849 | 0.4142 | 0.3330 |
| cell_precision | 0.5749 | 0.7017 | 0.8087 |
| frame_det_rate | 0.6152 | 0.5501 | 0.4499 |
| frame_recall_V | 0.6484 | 0.5982 | 0.4977 |
| frame_recall_E | 0.0444 | 0.0000 | 0.0000 |
| frame_recall_H | 0.8021 | 0.7188 | 0.5625 |
| cell_recall_V | 0.4936 | 0.4411 | 0.3778 |
| cell_recall_E | 0.0057 | 0.0000 | 0.0000 |
| cell_recall_H | 0.7941 | 0.6072 | 0.3885 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.4524 | 0.3810 | 0.3148 |
| band3_cell_recall | 0.4590 | 0.3704 | 0.2974 |
| band4_cell_recall | 0.5476 | 0.4823 | 0.3857 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0039 | 0.0010 | 0.0000 |
| band3_cell_fpr_off | 0.0525 | 0.0221 | 0.0108 |
| band4_cell_fpr_off | 0.1505 | 0.0691 | 0.0270 |
| frame_fa_off | 0.2819 | 0.1667 | 0.0735 |
| cell_fpr_off | 0.0517 | 0.0230 | 0.0094 |
| cell_fpr_on_neg | 0.1135 | 0.0594 | 0.0279 |
