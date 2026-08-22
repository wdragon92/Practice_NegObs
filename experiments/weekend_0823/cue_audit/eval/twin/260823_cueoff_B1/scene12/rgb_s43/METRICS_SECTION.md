# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.5 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 48 | 24 | 24 | 24 | 24 | 0 | 0 | 1 | 129 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.5426 [0.4790, 0.6087] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.1313 [0.1130, 0.1533] |
| cell FPR (negative cells of on frames) | 0.0199 [0.0080, 0.0337] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.2564 [0.1111, 0.4000] | 0.1500 [0.0741, 0.2316] |
| 3b [8,12) m | 0.6667 [0.6421, 0.6923] | 0.3750 [0.2960, 0.4480] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5204 [0.4242, 0.5968] |
| cell recall | 0.5426 [0.4790, 0.6087] |
| cell precision | 0.5000 [0.3577, 0.6345] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 1.0000 [1.0000, 1.0000] | 0.5426 [0.4790, 0.6087] | 24 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| **any tier (frame detection rate)** | 1.0000 [1.0000, 1.0000] | — | 24 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 1.0000 [1.0000, 1.0000] |
| cell FPR (off frames) | 0.1313 [0.1130, 0.1533] |
| cell FPR (negative cells of on frames) | 0.0199 [0.0080, 0.0337] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | n/a [n/a, n/a] | 0.0000 [0.0000, 0.0000] |
| 3a [5,8) m | 0.2564 [0.1111, 0.4000] | 0.1500 [0.0741, 0.2316] |
| 3b [8,12) m | 0.6667 [0.6421, 0.6923] | 0.3750 [0.2960, 0.4480] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5204 [0.4242, 0.5968] |
| cell recall | 0.5426 [0.4790, 0.6087] |
| cell precision | 0.5000 [0.3577, 0.6345] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5646 | 0.5204 | 0.4400 |
| cell_recall | 0.6434 | 0.5426 | 0.4264 |
| cell_precision | 0.5030 | 0.5000 | 0.4545 |
| frame_det_rate | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_V | 1.0000 | 1.0000 | 1.0000 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | n/a | n/a | n/a |
| cell_recall_V | 0.6434 | 0.5426 | 0.4264 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | n/a | n/a | n/a |
| band1_cell_recall | n/a | n/a | n/a |
| band2_cell_recall | n/a | n/a | n/a |
| band3_cell_recall | 0.5897 | 0.2564 | 0.1538 |
| band4_cell_recall | 0.6667 | 0.6667 | 0.5444 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_fpr_off | 0.1500 | 0.1500 | 0.1500 |
| band4_cell_fpr_off | 0.4000 | 0.3750 | 0.3750 |
| frame_fa_off | 1.0000 | 1.0000 | 1.0000 |
| cell_fpr_off | 0.1375 | 0.1313 | 0.1313 |
| cell_fpr_on_neg | 0.0456 | 0.0199 | 0.0085 |
