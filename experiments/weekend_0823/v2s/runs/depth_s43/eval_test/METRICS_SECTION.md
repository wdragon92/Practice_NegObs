# METRICS_SECTION — polar hazard grid

arm: **depth** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/depth_s43/best.pt`
grid: **PROVISIONAL-GRID-V2S** (4 bands x 10 sectors = 40 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.45 (fitted on **val**, val cell-F1 0.6861) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 4998 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8333 [0.7765, 0.8854] | 0.6707 [0.6240, 0.7151] | 180 |
| E | 0.6000 [0.4545, 0.7436] | 0.4356 [0.3618, 0.4972] | 45 |
| H | 0.4688 [0.3690, 0.5686] | 0.5978 [0.5136, 0.6714] | 96 |
| **any tier (frame detection rate)** | 0.6789 [0.6282, 0.7284] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0368 [0.0197, 0.0558] |
| cell FPR (off frames) | 0.0064 [0.0024, 0.0114] |
| cell FPR (negative cells of on frames) | 0.1195 [0.0917, 0.1490] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.2933 [0.1457, 0.4398] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.4160 [0.3106, 0.5167] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.4981 [0.4312, 0.5612] | 0.0118 [0.0030, 0.0224] |
| 3b [8,12) m | 0.7990 [0.7572, 0.8371] | 0.0140 [0.0060, 0.0237] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6525 [0.6139, 0.6883] |
| cell recall | 0.6255 [0.5872, 0.6596] |
| cell precision | 0.6819 [0.6217, 0.7424] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.45

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8667 [0.8150, 0.9148] | 0.6981 [0.6546, 0.7386] | 180 |
| E | 0.6000 [0.4545, 0.7436] | 0.4400 [0.3643, 0.5041] | 45 |
| H | 0.5312 [0.4327, 0.6311] | 0.6125 [0.5288, 0.6873] | 96 |
| **any tier (frame detection rate)** | 0.7156 [0.6667, 0.7638] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0882 [0.0621, 0.1171] |
| cell FPR (off frames) | 0.0134 [0.0075, 0.0203] |
| cell FPR (negative cells of on frames) | 0.1267 [0.0982, 0.1564] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.2933 [0.1457, 0.4398] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.4748 [0.3697, 0.5759] | 0.0007 [0.0000, 0.0017] |
| 3a [5,8) m | 0.5207 [0.4537, 0.5846] | 0.0191 [0.0080, 0.0324] |
| 3b [8,12) m | 0.8124 [0.7711, 0.8497] | 0.0338 [0.0207, 0.0484] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.6547 [0.6167, 0.6897] |
| cell recall | 0.6477 [0.6115, 0.6800] |
| cell precision | 0.6620 [0.6037, 0.7206] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.6349 | 0.6525 | 0.5878 |
| cell_recall | 0.7389 | 0.6255 | 0.4982 |
| cell_precision | 0.5565 | 0.6819 | 0.7168 |
| frame_det_rate | 0.8532 | 0.6789 | 0.6330 |
| frame_recall_V | 1.0000 | 0.8333 | 0.7667 |
| frame_recall_E | 0.8000 | 0.6000 | 0.6000 |
| frame_recall_H | 0.6250 | 0.4688 | 0.4375 |
| cell_recall_V | 0.7976 | 0.6707 | 0.5103 |
| cell_recall_E | 0.5156 | 0.4356 | 0.4222 |
| cell_recall_H | 0.6753 | 0.5978 | 0.5166 |
| band1_cell_recall | 0.4667 | 0.2933 | 0.2133 |
| band2_cell_recall | 0.5882 | 0.4160 | 0.2731 |
| band3_cell_recall | 0.6109 | 0.4981 | 0.3816 |
| band4_cell_recall | 0.8904 | 0.7990 | 0.6650 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0118 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0566 | 0.0118 | 0.0015 |
| band4_cell_fpr_off | 0.1588 | 0.0140 | 0.0000 |
| frame_fa_off | 0.3015 | 0.0368 | 0.0074 |
| cell_fpr_off | 0.0568 | 0.0064 | 0.0004 |
| cell_fpr_on_neg | 0.1781 | 0.1195 | 0.0864 |
