# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.31 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4194 [0.3222, 0.5196] | 0.1549 [0.1148, 0.1972] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.4028 [0.2933, 0.5173] | 0.1181 [0.0805, 0.1595] | 72 |
| **any tier (frame detection rate)** | 0.4121 [0.3399, 0.4896] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.4583 [0.4023, 0.5151] |
| cell FPR (off frames) | 0.0540 [0.0442, 0.0644] |
| cell FPR (negative cells of on frames) | 0.0502 [0.0402, 0.0609] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.1481 [0.0000, 0.3265] | 0.0056 [0.0000, 0.0142] |
| 2 [2,5) m | 0.0379 [0.0000, 0.0857] | 0.0146 [0.0045, 0.0269] |
| 3a [5,8) m | 0.1155 [0.0712, 0.1620] | 0.0472 [0.0320, 0.0643] |
| 3b [8,12) m | 0.1773 [0.1360, 0.2201] | 0.1486 [0.1238, 0.1746] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1780 [0.1413, 0.2133] |
| cell recall | 0.1417 [0.1117, 0.1725] |
| cell precision | 0.2394 [0.1843, 0.2971] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.31

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.5806 [0.4783, 0.6809] | 0.2695 [0.2142, 0.3240] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.5139 [0.4000, 0.6308] | 0.2199 [0.1552, 0.2941] | 72 |
| **any tier (frame detection rate)** | 0.5515 [0.4759, 0.6286] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.5833 [0.5272, 0.6399] |
| cell FPR (off frames) | 0.1007 [0.0857, 0.1164] |
| cell FPR (negative cells of on frames) | 0.0952 [0.0788, 0.1125] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.3333 [0.0000, 0.7500] | 0.0056 [0.0000, 0.0142] |
| 2 [2,5) m | 0.1061 [0.0432, 0.1795] | 0.0292 [0.0141, 0.0467] |
| 3a [5,8) m | 0.2152 [0.1497, 0.2834] | 0.1132 [0.0876, 0.1402] |
| 3b [8,12) m | 0.2985 [0.2433, 0.3549] | 0.2549 [0.2214, 0.2895] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.2401 [0.1977, 0.2808] |
| cell recall | 0.2517 [0.2092, 0.2962] |
| cell precision | 0.2295 [0.1822, 0.2789] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.2422 | 0.1780 | 0.1364 |
| cell_recall | 0.2592 | 0.1417 | 0.0892 |
| cell_precision | 0.2273 | 0.2394 | 0.2900 |
| frame_det_rate | 0.5697 | 0.4121 | 0.2727 |
| frame_recall_V | 0.5914 | 0.4194 | 0.3333 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.5417 | 0.4028 | 0.1944 |
| cell_recall_V | 0.2747 | 0.1549 | 0.1120 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.2315 | 0.1181 | 0.0486 |
| band1_cell_recall | 0.3333 | 0.1481 | 0.0000 |
| band2_cell_recall | 0.1212 | 0.0379 | 0.0000 |
| band3_cell_recall | 0.2205 | 0.1155 | 0.0709 |
| band4_cell_recall | 0.3061 | 0.1773 | 0.1212 |
| band1_cell_fpr_off | 0.0063 | 0.0056 | 0.0028 |
| band2_cell_fpr_off | 0.0306 | 0.0146 | 0.0049 |
| band3_cell_fpr_off | 0.1153 | 0.0472 | 0.0167 |
| band4_cell_fpr_off | 0.2681 | 0.1486 | 0.0813 |
| frame_fa_off | 0.5938 | 0.4583 | 0.2951 |
| cell_fpr_off | 0.1050 | 0.0540 | 0.0264 |
| cell_fpr_on_neg | 0.0991 | 0.0502 | 0.0241 |
