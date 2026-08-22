# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `experiments/mainrun_0819/runs/rgb_s43/best.pt`
tau_op = 0.5 · tau_star = 0.92 (fitted on **val**, val cell-F1 0.3692) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 336 | 168 | 168 | 141 | 111 | 9 | 21 | 7 | 981 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.7207 [0.6348, 0.8037] | 0.4261 [0.3544, 0.5040] | 111 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 9 |
| H | 0.0476 [0.0000, 0.1667] | 0.0333 [0.0000, 0.1139] | 21 |

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1429 [0.0915, 0.1976] |
| cell FPR (off frames) | 0.0266 [0.0153, 0.0394] |
| cell FPR (negative cells of on frames) | 0.0559 [0.0406, 0.0729] |

| distance band | cell recall [95% CI] |
|---|---|
| 1 near | 0.0000 [0.0000, 0.0000] |
| 2 mid | 0.2609 [0.1822, 0.3450] |
| 3 far | 0.5000 [0.4220, 0.5784] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4880 [0.4228, 0.5516] |
| cell recall | 0.3731 [0.3096, 0.4410] |
| cell precision | 0.7052 [0.6318, 0.7739] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.92

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.5495 [0.4579, 0.6415] | 0.2077 [0.1633, 0.2562] | 111 |
| E | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 9 |
| H | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 21 |

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.0536 [0.0229, 0.0904] |
| cell FPR (off frames) | 0.0131 [0.0048, 0.0232] |
| cell FPR (negative cells of on frames) | 0.0123 [0.0053, 0.0207] |

| distance band | cell recall [95% CI] |
|---|---|
| 1 near | 0.0000 [0.0000, 0.0000] |
| 2 mid | 0.0471 [0.0172, 0.0820] |
| 3 far | 0.2789 [0.2172, 0.3428] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2926 [0.2358, 0.3492] |
| cell recall | 0.1804 [0.1407, 0.2231] |
| cell precision | 0.7729 [0.6684, 0.8675] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5289 | 0.4880 | 0.4285 |
| cell_recall | 0.4434 | 0.3731 | 0.3007 |
| cell_precision | 0.6551 | 0.7052 | 0.7449 |
| frame_recall_V | 0.7838 | 0.7207 | 0.6126 |
| frame_recall_E | 0.0000 | 0.0000 | 0.0000 |
| frame_recall_H | 0.3333 | 0.0476 | 0.0476 |
| cell_recall_V | 0.4953 | 0.4261 | 0.3451 |
| cell_recall_E | 0.0000 | 0.0000 | 0.0000 |
| cell_recall_H | 0.1444 | 0.0333 | 0.0111 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.3514 | 0.2609 | 0.1630 |
| band3_cell_recall | 0.5748 | 0.5000 | 0.4252 |
| frame_fa_off | 0.2024 | 0.1429 | 0.0893 |
| cell_fpr_off | 0.0393 | 0.0266 | 0.0202 |
| cell_fpr_on_neg | 0.0845 | 0.0559 | 0.0325 |
