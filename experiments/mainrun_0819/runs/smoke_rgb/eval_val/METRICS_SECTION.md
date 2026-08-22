# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **val** · ckpt: `experiments/mainrun_0819/runs/smoke_rgb/best.pt`
tau_op = 0.5 · tau_star = 0.95 (fitted on **val**, val cell-F1 0.2834) · bootstrap 200x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 96 | 48 | 48 | 39 | 33 | 6 | 0 | 2 | 129 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4545 [0.2857, 0.6211] | 0.3500 [0.1961, 0.5371] | 33 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 6 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3750 [0.2380, 0.5002] |
| cell FPR (off frames) | 0.1694 [0.1031, 0.2381] |
| cell FPR (negative cells of on frames) | 0.3249 [0.2308, 0.4170] |

| distance band | cell recall [95% CI] |
|---|---|
| 1 near | 0.0000 [0.0000, 0.0000] |
| 2 mid | 0.0000 [0.0000, 0.0000] |
| 3 far | 0.5185 [0.3430, 0.6522] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1732 [0.1096, 0.2344] |
| cell recall | 0.3256 [0.1892, 0.4797] |
| cell precision | 0.1180 [0.0734, 0.1575] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.95

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4545 [0.2857, 0.6211] | 0.2917 [0.1717, 0.4527] | 33 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 6 |
| H | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2083 [0.1020, 0.3261] |
| cell FPR (off frames) | 0.0417 [0.0209, 0.0681] |
| cell FPR (negative cells of on frames) | 0.0897 [0.0605, 0.1246] |

| distance band | cell recall [95% CI] |
|---|---|
| 1 near | 0.0000 [0.0000, 0.0000] |
| 2 mid | 0.0000 [0.0000, 0.0000] |
| 3 far | 0.4321 [0.2857, 0.5626] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2834 [0.1824, 0.3707] |
| cell recall | 0.2713 [0.1547, 0.4098] |
| cell precision | 0.2966 [0.2034, 0.3631] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.1445 | 0.1732 | 0.2132 |
| cell_recall | 0.3333 | 0.3256 | 0.3256 |
| cell_precision | 0.0923 | 0.1180 | 0.1585 |
| frame_recall_V | 0.4848 | 0.4545 | 0.4545 |
| frame_recall_E | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_H | n/a | n/a | n/a |
| cell_recall_V | 0.3583 | 0.3500 | 0.3500 |
| cell_recall_E | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_H | n/a | n/a | n/a |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band3_cell_recall | 0.5309 | 0.5185 | 0.5185 |
| frame_fa_off | 0.4167 | 0.3750 | 0.3542 |
| cell_fpr_off | 0.2667 | 0.1694 | 0.1111 |
| cell_fpr_on_neg | 0.3909 | 0.3249 | 0.2420 |
