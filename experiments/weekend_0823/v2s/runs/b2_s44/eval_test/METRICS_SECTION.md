# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/b2_s44/best.pt`
grid: **PROVISIONAL-GRID-V2S** (4 bands x 10 sectors = 40 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.64 (fitted on **val**, val cell-F1 0.4854) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 4998 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6611 [0.5912, 0.7289] | 0.2493 [0.2097, 0.2920] | 180 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.2188 [0.1379, 0.3028] | 0.0947 [0.0584, 0.1332] | 96 |
| **any tier (frame detection rate)** | 0.4281 [0.3743, 0.4820] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1275 [0.0952, 0.1603] |
| cell FPR (off frames) | 0.0105 [0.0075, 0.0137] |
| cell FPR (negative cells of on frames) | 0.0391 [0.0306, 0.0483] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0742 [0.0330, 0.1255] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.1297 [0.0965, 0.1666] | 0.0005 [0.0000, 0.0015] |
| 3b [8,12) m | 0.2797 [0.2405, 0.3198] | 0.0414 [0.0297, 0.0539] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2893 [0.2512, 0.3288] |
| cell recall | 0.1899 [0.1605, 0.2213] |
| cell precision | 0.6072 [0.5473, 0.6649] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.64

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6222 [0.5517, 0.6932] | 0.2130 [0.1769, 0.2526] | 180 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 45 |
| H | 0.1875 [0.1111, 0.2667] | 0.0677 [0.0382, 0.0992] | 96 |
| **any tier (frame detection rate)** | 0.3976 [0.3438, 0.4510] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1029 [0.0741, 0.1330] |
| cell FPR (off frames) | 0.0075 [0.0052, 0.0100] |
| cell FPR (negative cells of on frames) | 0.0293 [0.0225, 0.0365] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0574 [0.0229, 0.1024] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.0934 [0.0644, 0.1260] | 0.0002 [0.0000, 0.0008] |
| 3b [8,12) m | 0.2477 [0.2106, 0.2857] | 0.0297 [0.0205, 0.0398] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2559 [0.2188, 0.2949] |
| cell recall | 0.1601 [0.1339, 0.1889] |
| cell precision | 0.6380 [0.5753, 0.6984] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.3303 | 0.2893 | 0.2365 |
| cell_recall | 0.2335 | 0.1899 | 0.1445 |
| cell_precision | 0.5640 | 0.6072 | 0.6516 |
| frame_det_rate | 0.4587 | 0.4281 | 0.3823 |
| frame_recall_V | 0.6833 | 0.6611 | 0.6111 |
| frame_recall_E | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_H | 0.2812 | 0.2188 | 0.1562 |
| cell_recall_V | 0.2976 | 0.2493 | 0.1935 |
| cell_recall_E | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_H | 0.1550 | 0.0947 | 0.0554 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.1064 | 0.0742 | 0.0434 |
| band3_cell_recall | 0.1660 | 0.1297 | 0.0815 |
| band4_cell_recall | 0.3354 | 0.2797 | 0.2278 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0010 | 0.0005 | 0.0002 |
| band4_cell_fpr_off | 0.0632 | 0.0414 | 0.0230 |
| frame_fa_off | 0.1765 | 0.1275 | 0.0833 |
| cell_fpr_off | 0.0161 | 0.0105 | 0.0058 |
| cell_fpr_on_neg | 0.0565 | 0.0391 | 0.0257 |
