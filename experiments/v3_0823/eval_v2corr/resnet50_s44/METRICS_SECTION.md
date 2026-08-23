# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/newmodels/runs/resnet50_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.58 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 369 | 219 | 45 | 96 | 7 | 2856 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6804 [0.6176, 0.7409] | 0.4965 [0.4363, 0.5566] | 219 |
| E | 0.6444 [0.5000, 0.7838] | 0.4885 [0.3676, 0.6000] | 45 |
| H | 0.2188 [0.1389, 0.3056] | 0.0828 [0.0444, 0.1277] | 96 |
| **any tier (frame detection rate)** | 0.5501 [0.4974, 0.6006] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1912 [0.1542, 0.2302] |
| cell FPR (off frames) | 0.0272 [0.0206, 0.0344] |
| cell FPR (negative cells of on frames) | 0.0541 [0.0417, 0.0673] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.3624 [0.2673, 0.4611] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.5006 [0.4401, 0.5600] | 0.0270 [0.0161, 0.0392] |
| 3b [8,12) m | 0.4340 [0.3854, 0.4818] | 0.0819 [0.0613, 0.1038] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5325 [0.4873, 0.5747] |
| cell recall | 0.4275 [0.3797, 0.4747] |
| cell precision | 0.7058 [0.6562, 0.7523] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.58

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6393 [0.5742, 0.7023] | 0.4619 [0.4030, 0.5208] | 219 |
| E | 0.6000 [0.4516, 0.7429] | 0.3994 [0.2922, 0.5014] | 45 |
| H | 0.1250 [0.0625, 0.1942] | 0.0403 [0.0178, 0.0667] | 96 |
| **any tier (frame detection rate)** | 0.4959 [0.4448, 0.5462] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1446 [0.1114, 0.1788] |
| cell FPR (off frames) | 0.0206 [0.0147, 0.0271] |
| cell FPR (negative cells of on frames) | 0.0436 [0.0323, 0.0554] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.3280 [0.2363, 0.4240] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.4602 [0.4011, 0.5179] | 0.0186 [0.0093, 0.0293] |
| 3b [8,12) m | 0.3850 [0.3376, 0.4313] | 0.0637 [0.0452, 0.0836] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5052 [0.4584, 0.5486] |
| cell recall | 0.3852 [0.3387, 0.4302] |
| cell precision | 0.7338 [0.6826, 0.7822] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5752 | 0.5325 | 0.4405 |
| cell_recall | 0.5368 | 0.4275 | 0.3099 |
| cell_precision | 0.6196 | 0.7058 | 0.7616 |
| frame_det_rate | 0.6721 | 0.5501 | 0.4146 |
| frame_recall_V | 0.7671 | 0.6804 | 0.5525 |
| frame_recall_E | 0.7333 | 0.6444 | 0.5333 |
| frame_recall_H | 0.4271 | 0.2188 | 0.0521 |
| cell_recall_V | 0.5905 | 0.4965 | 0.3863 |
| cell_recall_E | 0.6695 | 0.4885 | 0.2672 |
| cell_recall_H | 0.2017 | 0.0828 | 0.0127 |
| band1_cell_recall | 0.0085 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.4788 | 0.3624 | 0.2381 |
| band3_cell_recall | 0.5926 | 0.5006 | 0.3715 |
| band4_cell_recall | 0.5599 | 0.4340 | 0.3156 |
| band1_cell_fpr_off | 0.0005 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0044 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0593 | 0.0270 | 0.0123 |
| band4_cell_fpr_off | 0.1461 | 0.0819 | 0.0490 |
| frame_fa_off | 0.3211 | 0.1912 | 0.0980 |
| cell_fpr_off | 0.0526 | 0.0272 | 0.0153 |
| cell_fpr_on_neg | 0.0965 | 0.0541 | 0.0287 |
