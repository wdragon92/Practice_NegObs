# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **probe** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s44/best.pt`
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
| H | 0.1000 [0.0000, 0.2174] | 0.0741 [0.0000, 0.1750] | 30 |
| **any tier (frame detection rate)** | 0.0417 [0.0000, 0.0921] | — | 72 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0833 [0.0267, 0.1519] |
| cell FPR (off frames) | 0.0104 [0.0024, 0.0213] |
| cell FPR (negative cells of on frames) | 0.0072 [0.0015, 0.0150] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0526 [0.0000, 0.1214] | 0.0222 [0.0000, 0.0575] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0028 [0.0000, 0.0092] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.0167 [0.0000, 0.0373] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0548 [0.0000, 0.1221] |
| cell recall | 0.0317 [0.0000, 0.0753] |
| cell precision | 0.2000 [0.0000, 0.4091] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 15 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 27 |
| H | 0.1000 [0.0000, 0.2174] | 0.0741 [0.0000, 0.1750] | 30 |
| **any tier (frame detection rate)** | 0.0417 [0.0000, 0.0921] | — | 72 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0833 [0.0267, 0.1519] |
| cell FPR (off frames) | 0.0104 [0.0024, 0.0213] |
| cell FPR (negative cells of on frames) | 0.0072 [0.0015, 0.0150] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.0526 [0.0000, 0.1214] | 0.0222 [0.0000, 0.0575] |
| 3a [5,8) m | 0.0000 [0.0000, 0.0000] | 0.0028 [0.0000, 0.0092] |
| 3b [8,12) m | 0.0000 [0.0000, 0.0000] | 0.0167 [0.0000, 0.0373] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.0548 [0.0000, 0.1221] |
| cell recall | 0.0317 [0.0000, 0.0753] |
| cell precision | 0.2000 [0.0000, 0.4091] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.0759 | 0.0548 | 0.0299 |
| cell_recall | 0.0476 | 0.0317 | 0.0159 |
| cell_precision | 0.1875 | 0.2000 | 0.2500 |
| frame_det_rate | 0.0417 | 0.0417 | 0.0139 |
| frame_recall_V | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_E | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_H | 0.1000 | 0.1000 | 0.0333 |
| cell_recall_V | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_E | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_H | 0.1111 | 0.0741 | 0.0370 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.0789 | 0.0526 | 0.0263 |
| band3_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0361 | 0.0222 | 0.0083 |
| band3_cell_fpr_off | 0.0083 | 0.0028 | 0.0000 |
| band4_cell_fpr_off | 0.0222 | 0.0167 | 0.0083 |
| frame_fa_off | 0.0972 | 0.0833 | 0.0556 |
| cell_fpr_off | 0.0167 | 0.0104 | 0.0042 |
| cell_fpr_on_neg | 0.0120 | 0.0072 | 0.0024 |
