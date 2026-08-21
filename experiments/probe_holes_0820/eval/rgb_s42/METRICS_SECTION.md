# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **probe** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 144 | 72 | 72 | 72 | 15 | 27 | 30 | 3 | 189 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.1333 [0.0000, 0.3333] | 0.0667 [0.0000, 0.1818] | 15 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 27 |
| H | 0.0667 [0.0000, 0.1667] | 0.0741 [0.0000, 0.1875] | 30 |
| **any tier (frame detection rate)** | 0.0556 [0.0128, 0.1143] | — | 72 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0556 [0.0128, 0.1154] |
| cell FPR (off frames) | 0.0167 [0.0007, 0.0413] |
| cell FPR (negative cells of on frames) | 0.0160 [0.0017, 0.0360] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0789 [0.0089, 0.1651] | 0.0278 [0.0000, 0.0725] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0194 [0.0000, 0.0468] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.0194 [0.0000, 0.0468] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0744 [0.0090, 0.1406] |
| cell recall | 0.0476 [0.0053, 0.1018] |
| cell precision | 0.1698 [0.0328, 0.3333] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.1333 [0.0000, 0.3333] | 0.0667 [0.0000, 0.1818] | 15 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 27 |
| H | 0.0667 [0.0000, 0.1667] | 0.0741 [0.0000, 0.1875] | 30 |
| **any tier (frame detection rate)** | 0.0556 [0.0128, 0.1143] | — | 72 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0556 [0.0128, 0.1154] |
| cell FPR (off frames) | 0.0167 [0.0007, 0.0413] |
| cell FPR (negative cells of on frames) | 0.0160 [0.0017, 0.0360] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0789 [0.0089, 0.1651] | 0.0278 [0.0000, 0.0725] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0194 [0.0000, 0.0468] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.0194 [0.0000, 0.0468] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0744 [0.0090, 0.1406] |
| cell recall | 0.0476 [0.0053, 0.1018] |
| cell precision | 0.1698 [0.0328, 0.3333] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.0848 | 0.0744 | 0.0529 |
| cell_recall | 0.0635 | 0.0476 | 0.0317 |
| cell_precision | 0.1277 | 0.1698 | 0.1579 |
| frame_det_rate | 0.0833 | 0.0556 | 0.0278 |
| frame_recall_V | 0.2000 | 0.1333 | 0.0000 |
| frame_recall_E | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_H | 0.1000 | 0.0667 | 0.0667 |
| cell_recall_V | 0.1111 | 0.0667 | 0.0000 |
| cell_recall_E | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_H | 0.0864 | 0.0741 | 0.0741 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.1053 | 0.0789 | 0.0526 |
| band3_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0306 | 0.0278 | 0.0278 |
| band3_cell_fpr_off | 0.0306 | 0.0194 | 0.0167 |
| band4_cell_fpr_off | 0.0389 | 0.0194 | 0.0083 |
| frame_fa_off | 0.1111 | 0.0556 | 0.0278 |
| cell_fpr_off | 0.0250 | 0.0167 | 0.0132 |
| cell_fpr_on_neg | 0.0368 | 0.0160 | 0.0104 |
