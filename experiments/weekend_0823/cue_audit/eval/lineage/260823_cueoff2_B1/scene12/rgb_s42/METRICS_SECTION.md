# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 24 | 0 | 0 | 24 | 1 | 63 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.4167 [0.2174, 0.6190] | 0.3016 [0.1500, 0.4576] | 24 |
| **any tier (frame detection rate)** | 0.4167 [0.2174, 0.6190] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (negative cells of on frames) | 0.0216 [0.0000, 0.0526] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.3077 [0.0909, 0.5517] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.2917 [0.1429, 0.4375] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4176 [0.2192, 0.6000] |
| cell recall | 0.3016 [0.1500, 0.4576] |
| cell precision | 0.6786 [0.3667, 1.0000] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.4167 [0.2174, 0.6190] | 0.3016 [0.1500, 0.4576] | 24 |
| **any tier (frame detection rate)** | 0.4167 [0.2174, 0.6190] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (off frames) | 0.0000 [0.0000, 0.0000] |
| cell FPR (negative cells of on frames) | 0.0216 [0.0000, 0.0526] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.3077 [0.0909, 0.5517] | 0.0000 [0.0000, 0.0000] |
| 3b [8,12) m | 0.2917 [0.1429, 0.4375] | 0.0000 [0.0000, 0.0000] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4176 [0.2192, 0.6000] |
| cell recall | 0.3016 [0.1500, 0.4576] |
| cell precision | 0.6786 [0.3667, 1.0000] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5789 | 0.4176 | 0.2703 |
| cell_recall | 0.5238 | 0.3016 | 0.1587 |
| cell_precision | 0.6471 | 0.6786 | 0.9091 |
| frame_det_rate | 0.6250 | 0.4167 | 0.2083 |
| frame_recall_V | n/a | n/a | n/a |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.6250 | 0.4167 | 0.2083 |
| cell_recall_V | n/a | n/a | n/a |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.5238 | 0.3016 | 0.1587 |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | 0.5385 | 0.3077 | 0.2308 |
| band4_cell_recall | 0.5000 | 0.2917 | 0.0417 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| frame_fa_off | 0.0000 | 0.0000 | 0.0000 |
| cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| cell_fpr_on_neg | 0.0432 | 0.0216 | 0.0024 |
