# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **probe** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 144 | 72 | 72 | 72 | 15 | 27 | 30 | 3 | 189 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.2000 [0.0000, 0.4286] | 0.0889 [0.0000, 0.2174] | 15 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 27 |
| H | 0.2333 [0.0882, 0.3929] | 0.1728 [0.0563, 0.3111] | 30 |
| **any tier (frame detection rate)** | 0.1389 [0.0633, 0.2222] | — | 72 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1806 [0.0952, 0.2763] |
| cell FPR (off frames) | 0.0319 [0.0113, 0.0583] |
| cell FPR (negative cells of on frames) | 0.0352 [0.0175, 0.0562] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0965 [0.0183, 0.1930] | 0.0417 [0.0000, 0.0946] |
| 3a [5,8) m | 0.1667 [0.0333, 0.3448] | 0.0333 [0.0056, 0.0706] |
| 3b [8,12) m | 0.0741 [0.0000, 0.1739] | 0.0528 [0.0247, 0.0853] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1212 [0.0532, 0.1873] |
| cell recall | 0.0952 [0.0383, 0.1622] |
| cell precision | 0.1667 [0.0816, 0.2526] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.2000 [0.0000, 0.4286] | 0.0889 [0.0000, 0.2174] | 15 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 27 |
| H | 0.2333 [0.0882, 0.3929] | 0.1728 [0.0563, 0.3111] | 30 |
| **any tier (frame detection rate)** | 0.1389 [0.0633, 0.2222] | — | 72 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1806 [0.0952, 0.2763] |
| cell FPR (off frames) | 0.0319 [0.0113, 0.0583] |
| cell FPR (negative cells of on frames) | 0.0352 [0.0175, 0.0562] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0965 [0.0183, 0.1930] | 0.0417 [0.0000, 0.0946] |
| 3a [5,8) m | 0.1667 [0.0333, 0.3448] | 0.0333 [0.0056, 0.0706] |
| 3b [8,12) m | 0.0741 [0.0000, 0.1739] | 0.0528 [0.0247, 0.0853] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1212 [0.0532, 0.1873] |
| cell recall | 0.0952 [0.0383, 0.1622] |
| cell precision | 0.1667 [0.0816, 0.2526] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.1212 | 0.1212 | 0.0913 |
| cell_recall | 0.1164 | 0.0952 | 0.0635 |
| cell_precision | 0.1264 | 0.1667 | 0.1622 |
| frame_det_rate | 0.1806 | 0.1389 | 0.0833 |
| frame_recall_V | 0.2667 | 0.2000 | 0.1333 |
| frame_recall_E | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_H | 0.3000 | 0.2333 | 0.1333 |
| cell_recall_V | 0.1111 | 0.0889 | 0.0444 |
| cell_recall_E | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_H | 0.2099 | 0.1728 | 0.1235 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.0965 | 0.0965 | 0.0789 |
| band3_cell_recall | 0.2333 | 0.1667 | 0.1000 |
| band4_cell_recall | 0.1481 | 0.0741 | 0.0000 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0417 | 0.0417 | 0.0389 |
| band3_cell_fpr_off | 0.0556 | 0.0333 | 0.0306 |
| band4_cell_fpr_off | 0.1028 | 0.0528 | 0.0250 |
| frame_fa_off | 0.2639 | 0.1806 | 0.0833 |
| cell_fpr_off | 0.0500 | 0.0319 | 0.0236 |
| cell_fpr_on_neg | 0.0639 | 0.0352 | 0.0224 |
