# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s42_aux/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.43 (fitted on **val**, val cell-F1 0.4898) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 2691 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6389 [0.5684, 0.7090] | 0.4630 [0.3944, 0.5314] | 180 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.7188 [0.6279, 0.8081] | 0.6072 [0.5333, 0.6771] | 96 |
| **any tier (frame detection rate)** | 0.5627 [0.5093, 0.6172] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1667 [0.1311, 0.2028] |
| cell FPR (off frames) | 0.0230 [0.0167, 0.0300] |
| cell FPR (negative cells of on frames) | 0.0636 [0.0513, 0.0769] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.3810 [0.2833, 0.4798] | 0.0010 [0.0000, 0.0025] |
| 3a [5,8) m | 0.3793 [0.3158, 0.4453] | 0.0221 [0.0120, 0.0337] |
| 3b [8,12) m | 0.5098 [0.4558, 0.5629] | 0.0691 [0.0513, 0.0879] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5255 [0.4755, 0.5717] |
| cell recall | 0.4274 [0.3754, 0.4801] |
| cell precision | 0.6821 [0.6301, 0.7311] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.43

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6667 [0.5969, 0.7356] | 0.4834 [0.4150, 0.5517] | 180 |
| E | 0.0222 [0.0000, 0.0741] | 0.0029 [0.0000, 0.0096] | 45 |
| H | 0.7396 [0.6504, 0.8256] | 0.6794 [0.6071, 0.7457] | 96 |
| **any tier (frame detection rate)** | 0.5872 [0.5346, 0.6413] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1985 [0.1601, 0.2382] |
| cell FPR (off frames) | 0.0327 [0.0246, 0.0414] |
| cell FPR (negative cells of on frames) | 0.0773 [0.0636, 0.0917] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.4074 [0.3090, 0.5076] | 0.0025 [0.0000, 0.0057] |
| 3a [5,8) m | 0.4149 [0.3505, 0.4802] | 0.0319 [0.0186, 0.0468] |
| 3b [8,12) m | 0.5339 [0.4798, 0.5870] | 0.0966 [0.0751, 0.1187] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5313 [0.4828, 0.5763] |
| cell recall | 0.4545 [0.4013, 0.5076] |
| cell precision | 0.6393 [0.5874, 0.6885] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5278 | 0.5255 | 0.4794 |
| cell_recall | 0.5002 | 0.4274 | 0.3445 |
| cell_precision | 0.5587 | 0.6821 | 0.7883 |
| frame_det_rate | 0.6330 | 0.5627 | 0.4618 |
| frame_recall_V | 0.6944 | 0.6389 | 0.5389 |
| frame_recall_E | 0.0444 | 0.0000 | 0.0000 |
| frame_recall_H | 0.8021 | 0.7188 | 0.5625 |
| cell_recall_V | 0.5182 | 0.4630 | 0.3987 |
| cell_recall_E | 0.0057 | 0.0000 | 0.0000 |
| cell_recall_H | 0.7941 | 0.6072 | 0.3885 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.4524 | 0.3810 | 0.3148 |
| band3_cell_recall | 0.4701 | 0.3793 | 0.3046 |
| band4_cell_recall | 0.5777 | 0.5098 | 0.4095 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0039 | 0.0010 | 0.0000 |
| band3_cell_fpr_off | 0.0525 | 0.0221 | 0.0108 |
| band4_cell_fpr_off | 0.1505 | 0.0691 | 0.0270 |
| frame_fa_off | 0.2819 | 0.1667 | 0.0735 |
| cell_fpr_off | 0.0517 | 0.0230 | 0.0094 |
| cell_fpr_on_neg | 0.1172 | 0.0636 | 0.0314 |
