# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/fusion/s44/fused_max/per_frame.csv`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 2691 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6333 [0.5615, 0.7022] | 0.2755 [0.2273, 0.3268] | 180 |
| E | 0.1556 [0.0571, 0.2683] | 0.0402 [0.0125, 0.0762] | 45 |
| H | 0.5938 [0.4947, 0.6907] | 0.2505 [0.2031, 0.3017] | 96 |
| **any tier (frame detection rate)** | 0.5596 [0.5059, 0.6146] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2328 [0.1922, 0.2734] |
| cell FPR (off frames) | 0.0289 [0.0230, 0.0352] |
| cell FPR (negative cells of on frames) | 0.0556 [0.0463, 0.0653] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0427 [0.0110, 0.0787] | 0.0039 [0.0011, 0.0073] |
| 2 [2,5) m | 0.1720 [0.1060, 0.2436] | 0.0152 [0.0067, 0.0256] |
| 3a [5,8) m | 0.2034 [0.1604, 0.2500] | 0.0240 [0.0156, 0.0331] |
| 3b [8,12) m | 0.3047 [0.2632, 0.3467] | 0.0725 [0.0569, 0.0887] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3354 [0.2935, 0.3775] |
| cell recall | 0.2419 [0.2063, 0.2797] |
| cell precision | 0.5466 [0.4883, 0.6004] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6333 [0.5615, 0.7022] | 0.2755 [0.2273, 0.3268] | 180 |
| E | 0.1556 [0.0571, 0.2683] | 0.0402 [0.0125, 0.0762] | 45 |
| H | 0.5938 [0.4947, 0.6907] | 0.2505 [0.2031, 0.3017] | 96 |
| **any tier (frame detection rate)** | 0.5596 [0.5059, 0.6146] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2328 [0.1922, 0.2734] |
| cell FPR (off frames) | 0.0289 [0.0230, 0.0352] |
| cell FPR (negative cells of on frames) | 0.0556 [0.0463, 0.0653] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0427 [0.0110, 0.0787] | 0.0039 [0.0011, 0.0073] |
| 2 [2,5) m | 0.1720 [0.1060, 0.2436] | 0.0152 [0.0067, 0.0256] |
| 3a [5,8) m | 0.2034 [0.1604, 0.2500] | 0.0240 [0.0156, 0.0331] |
| 3b [8,12) m | 0.3047 [0.2632, 0.3467] | 0.0725 [0.0569, 0.0887] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3354 [0.2935, 0.3775] |
| cell recall | 0.2419 [0.2063, 0.2797] |
| cell precision | 0.5466 [0.4883, 0.6004] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3916 | 0.3354 | 0.2568 |
| cell_recall | 0.3411 | 0.2419 | 0.1605 |
| cell_precision | 0.4597 | 0.5466 | 0.6419 |
| frame_det_rate | 0.6820 | 0.5596 | 0.3945 |
| frame_recall_V | 0.7222 | 0.6333 | 0.5167 |
| frame_recall_E | 0.3111 | 0.1556 | 0.0444 |
| frame_recall_H | 0.7604 | 0.5938 | 0.3229 |
| cell_recall_V | 0.3671 | 0.2755 | 0.1972 |
| cell_recall_E | 0.1121 | 0.0402 | 0.0057 |
| cell_recall_H | 0.3992 | 0.2505 | 0.1253 |
| band1_cell_recall | 0.0769 | 0.0427 | 0.0342 |
| band2_cell_recall | 0.2672 | 0.1720 | 0.1190 |
| band3_cell_recall | 0.3138 | 0.2034 | 0.1287 |
| band4_cell_recall | 0.4035 | 0.3047 | 0.2044 |
| band1_cell_fpr_off | 0.0064 | 0.0039 | 0.0025 |
| band2_cell_fpr_off | 0.0333 | 0.0152 | 0.0015 |
| band3_cell_fpr_off | 0.0809 | 0.0240 | 0.0093 |
| band4_cell_fpr_off | 0.1412 | 0.0725 | 0.0294 |
| frame_fa_off | 0.3407 | 0.2328 | 0.1250 |
| cell_fpr_off | 0.0654 | 0.0289 | 0.0107 |
| cell_fpr_on_neg | 0.0997 | 0.0556 | 0.0282 |
