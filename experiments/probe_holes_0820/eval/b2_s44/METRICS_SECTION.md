# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **probe** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 144 | 72 | 72 | 72 | 15 | 27 | 30 | 3 | 189 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 15 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 27 |
| H | 0.2000 [0.0667, 0.3514] | 0.1852 [0.0566, 0.3434] | 30 |
| **any tier (frame detection rate)** | 0.0833 [0.0274, 0.1515] | — | 72 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0833 [0.0270, 0.1538] |
| cell FPR (off frames) | 0.0229 [0.0058, 0.0447] |
| cell FPR (negative cells of on frames) | 0.0120 [0.0023, 0.0248] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.1316 [0.0388, 0.2353] | 0.0639 [0.0164, 0.1217] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0278 [0.0029, 0.0600] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1190 [0.0364, 0.2043] |
| cell recall | 0.0794 [0.0223, 0.1484] |
| cell precision | 0.2381 [0.0882, 0.4167] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 15 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 27 |
| H | 0.2000 [0.0667, 0.3514] | 0.1852 [0.0566, 0.3434] | 30 |
| **any tier (frame detection rate)** | 0.0833 [0.0274, 0.1515] | — | 72 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0833 [0.0270, 0.1538] |
| cell FPR (off frames) | 0.0229 [0.0058, 0.0447] |
| cell FPR (negative cells of on frames) | 0.0120 [0.0023, 0.0248] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.1316 [0.0388, 0.2353] | 0.0639 [0.0164, 0.1217] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0278 [0.0029, 0.0600] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1190 [0.0364, 0.2043] |
| cell recall | 0.0794 [0.0223, 0.1484] |
| cell precision | 0.2381 [0.0882, 0.4167] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.1372 | 0.1190 | 0.1021 |
| cell_recall | 0.1005 | 0.0794 | 0.0635 |
| cell_precision | 0.2159 | 0.2381 | 0.2609 |
| frame_det_rate | 0.1111 | 0.0833 | 0.0694 |
| frame_recall_V | 0.0667 | 0.0000 | 0.0000 |
| frame_recall_E | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_H | 0.2333 | 0.2000 | 0.1667 |
| cell_recall_V | 0.0222 | 0.0000 | 0.0000 |
| cell_recall_E | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_H | 0.2222 | 0.1852 | 0.1481 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.1667 | 0.1316 | 0.1053 |
| band3_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band1_cell_fpr_off | 0.0056 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0806 | 0.0639 | 0.0472 |
| band3_cell_fpr_off | 0.0389 | 0.0278 | 0.0194 |
| band4_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| frame_fa_off | 0.0972 | 0.0833 | 0.0694 |
| cell_fpr_off | 0.0312 | 0.0229 | 0.0167 |
| cell_fpr_on_neg | 0.0192 | 0.0120 | 0.0080 |
