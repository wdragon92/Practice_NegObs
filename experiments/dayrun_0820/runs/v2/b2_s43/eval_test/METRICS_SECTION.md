# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.45 (fitted on **val**, val cell-F1 0.4880) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 2691 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8722 [0.8212, 0.9192] | 0.5289 [0.4772, 0.5810] | 180 |
| E | 0.5333 [0.3846, 0.6829] | 0.2328 [0.1547, 0.3133] | 45 |
| H | 0.3958 [0.2981, 0.4945] | 0.1614 [0.1086, 0.2252] | 96 |
| **any tier (frame detection rate)** | 0.6881 [0.6366, 0.7370] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3946 [0.3479, 0.4417] |
| cell FPR (off frames) | 0.0685 [0.0584, 0.0790] |
| cell FPR (negative cells of on frames) | 0.1880 [0.1672, 0.2086] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2143 [0.1509, 0.2832] | 0.0225 [0.0146, 0.0312] |
| 3a [5,8) m | 0.4218 [0.3743, 0.4709] | 0.0853 [0.0685, 0.1027] |
| 3b [8,12) m | 0.5294 [0.4766, 0.5831] | 0.1662 [0.1413, 0.1926] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4237 [0.3878, 0.4585] |
| cell recall | 0.4274 [0.3861, 0.4690] |
| cell precision | 0.4202 [0.3758, 0.4628] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.45

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.8944 [0.8473, 0.9375] | 0.5745 [0.5202, 0.6290] | 180 |
| E | 0.5556 [0.4048, 0.7027] | 0.2845 [0.1956, 0.3743] | 45 |
| H | 0.4583 [0.3585, 0.5585] | 0.2166 [0.1515, 0.2897] | 96 |
| **any tier (frame detection rate)** | 0.7217 [0.6718, 0.7697] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.4412 [0.3931, 0.4888] |
| cell FPR (off frames) | 0.0919 [0.0791, 0.1050] |
| cell FPR (negative cells of on frames) | 0.2269 [0.2040, 0.2501] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2910 [0.2167, 0.3698] | 0.0495 [0.0357, 0.0647] |
| 3a [5,8) m | 0.4885 [0.4379, 0.5400] | 0.1123 [0.0920, 0.1337] |
| 3b [8,12) m | 0.5611 [0.5080, 0.6146] | 0.2059 [0.1788, 0.2339] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4291 [0.3931, 0.4636] |
| cell recall | 0.4753 [0.4322, 0.5192] |
| cell precision | 0.3911 [0.3497, 0.4316] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4218 | 0.4237 | 0.3409 |
| cell_recall | 0.6020 | 0.4274 | 0.2467 |
| cell_precision | 0.3246 | 0.4202 | 0.5515 |
| frame_det_rate | 0.8073 | 0.6881 | 0.4954 |
| frame_recall_V | 0.9556 | 0.8722 | 0.7722 |
| frame_recall_E | 0.7556 | 0.5333 | 0.2667 |
| frame_recall_H | 0.5417 | 0.3958 | 0.1042 |
| cell_recall_V | 0.7090 | 0.5289 | 0.3382 |
| cell_recall_E | 0.4080 | 0.2328 | 0.0632 |
| cell_recall_H | 0.3163 | 0.1614 | 0.0212 |
| band1_cell_recall | 0.0085 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.5503 | 0.2143 | 0.0476 |
| band3_cell_recall | 0.6598 | 0.4218 | 0.1954 |
| band4_cell_recall | 0.6312 | 0.5294 | 0.3590 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.1647 | 0.0225 | 0.0000 |
| band3_cell_fpr_off | 0.2186 | 0.0853 | 0.0015 |
| band4_cell_fpr_off | 0.3436 | 0.1662 | 0.0431 |
| frame_fa_off | 0.5760 | 0.3946 | 0.1078 |
| cell_fpr_off | 0.1817 | 0.0685 | 0.0112 |
| cell_fpr_on_neg | 0.3452 | 0.1880 | 0.0821 |
