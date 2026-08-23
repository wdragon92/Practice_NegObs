# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s42/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.63 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 369 | 219 | 45 | 96 | 7 | 2856 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.7763 [0.7189, 0.8308] | 0.4708 [0.4159, 0.5265] | 219 |
| E | 0.6000 [0.4528, 0.7436] | 0.3592 [0.2626, 0.4556] | 45 |
| H | 0.5938 [0.4946, 0.6923] | 0.2527 [0.1989, 0.3107] | 96 |
| **any tier (frame detection rate)** | 0.7127 [0.6658, 0.7585] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.3750 [0.3283, 0.4218] |
| cell FPR (off frames) | 0.0527 [0.0443, 0.0615] |
| cell FPR (negative cells of on frames) | 0.0875 [0.0734, 0.1023] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.3360 [0.2446, 0.4326] | 0.0088 [0.0030, 0.0162] |
| 3a [5,8) m | 0.4074 [0.3508, 0.4638] | 0.0662 [0.0488, 0.0842] |
| 3b [8,12) m | 0.4891 [0.4441, 0.5330] | 0.1358 [0.1151, 0.1565] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4876 [0.4469, 0.5254] |
| cell recall | 0.4233 [0.3806, 0.4658] |
| cell precision | 0.5749 [0.5253, 0.6210] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.63

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.7169 [0.6562, 0.7756] | 0.3937 [0.3436, 0.4452] | 219 |
| E | 0.5333 [0.3864, 0.6809] | 0.1983 [0.1310, 0.2694] | 45 |
| H | 0.4792 [0.3804, 0.5794] | 0.1783 [0.1343, 0.2257] | 96 |
| **any tier (frame detection rate)** | 0.6369 [0.5868, 0.6855] | — | 369 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2941 [0.2506, 0.3382] |
| cell FPR (off frames) | 0.0353 [0.0288, 0.0420] |
| cell FPR (negative cells of on frames) | 0.0635 [0.0515, 0.0762] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.2513 [0.1692, 0.3383] | 0.0034 [0.0000, 0.0089] |
| 3a [5,8) m | 0.3244 [0.2737, 0.3743] | 0.0461 [0.0324, 0.0604] |
| 3b [8,12) m | 0.3918 [0.3483, 0.4347] | 0.0917 [0.0751, 0.1090] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4323 [0.3909, 0.4715] |
| cell recall | 0.3361 [0.2976, 0.3753] |
| cell precision | 0.6057 [0.5526, 0.6552] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5321 | 0.4876 | 0.3901 |
| cell_recall | 0.5574 | 0.4233 | 0.2843 |
| cell_precision | 0.5090 | 0.5749 | 0.6213 |
| frame_det_rate | 0.8157 | 0.7127 | 0.5583 |
| frame_recall_V | 0.8402 | 0.7763 | 0.6712 |
| frame_recall_E | 0.7111 | 0.6000 | 0.4000 |
| frame_recall_H | 0.7917 | 0.5938 | 0.3750 |
| cell_recall_V | 0.5826 | 0.4708 | 0.3462 |
| cell_recall_E | 0.5833 | 0.3592 | 0.1178 |
| cell_recall_H | 0.4183 | 0.2527 | 0.1359 |
| band1_cell_recall | 0.0171 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.4709 | 0.3360 | 0.2143 |
| band3_cell_recall | 0.5522 | 0.4074 | 0.2694 |
| band4_cell_recall | 0.6259 | 0.4891 | 0.3340 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0319 | 0.0088 | 0.0029 |
| band3_cell_fpr_off | 0.1137 | 0.0662 | 0.0328 |
| band4_cell_fpr_off | 0.2284 | 0.1358 | 0.0681 |
| frame_fa_off | 0.4779 | 0.3750 | 0.2255 |
| cell_fpr_off | 0.0935 | 0.0527 | 0.0260 |
| cell_fpr_on_neg | 0.1457 | 0.0875 | 0.0534 |
