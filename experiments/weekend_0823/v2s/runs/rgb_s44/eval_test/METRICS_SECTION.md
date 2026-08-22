# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/weekend_0823/v2s/runs/rgb_s44/best.pt`
grid: **PROVISIONAL-GRID-V2S** (4 bands x 10 sectors = 40 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.55 (fitted on **val**, val cell-F1 0.5620) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 816 | 408 | 408 | 327 | 180 | 45 | 96 | 7 | 4998 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6889 [0.6218, 0.7560] | 0.3305 [0.2752, 0.3883] | 180 |
| E | 0.7556 [0.6250, 0.8780] | 0.5570 [0.4406, 0.6663] | 45 |
| H | 0.1667 [0.0952, 0.2469] | 0.0369 [0.0193, 0.0587] | 96 |
| **any tier (frame detection rate)** | 0.5413 [0.4883, 0.5949] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1397 [0.1068, 0.1746] |
| cell FPR (off frames) | 0.0175 [0.0117, 0.0242] |
| cell FPR (negative cells of on frames) | 0.0708 [0.0569, 0.0859] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0444 [0.0000, 0.1381] | 0.0022 [0.0000, 0.0069] |
| 2 [2,5) m | 0.3319 [0.2418, 0.4266] | 0.0093 [0.0021, 0.0191] |
| 3a [5,8) m | 0.3653 [0.3074, 0.4245] | 0.0390 [0.0245, 0.0548] |
| 3b [8,12) m | 0.2984 [0.2558, 0.3417] | 0.0194 [0.0128, 0.0267] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4092 [0.3588, 0.4561] |
| cell recall | 0.3131 [0.2676, 0.3595] |
| cell precision | 0.5901 [0.5264, 0.6521] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.55

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.5944 [0.5235, 0.6649] | 0.2950 [0.2400, 0.3534] | 180 |
| E | 0.7111 [0.5737, 0.8431] | 0.5037 [0.3880, 0.6127] | 45 |
| H | 0.1250 [0.0632, 0.1947] | 0.0271 [0.0126, 0.0446] | 96 |
| **any tier (frame detection rate)** | 0.4648 [0.4114, 0.5187] | — | 327 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1005 [0.0725, 0.1305] |
| cell FPR (off frames) | 0.0137 [0.0087, 0.0194] |
| cell FPR (negative cells of on frames) | 0.0602 [0.0476, 0.0739] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0356 [0.0000, 0.1185] | 0.0017 [0.0000, 0.0054] |
| 2 [2,5) m | 0.3165 [0.2278, 0.4106] | 0.0088 [0.0019, 0.0183] |
| 3a [5,8) m | 0.3371 [0.2789, 0.3972] | 0.0324 [0.0198, 0.0462] |
| 3b [8,12) m | 0.2529 [0.2117, 0.2950] | 0.0118 [0.0068, 0.0174] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.3823 [0.3295, 0.4318] |
| cell recall | 0.2791 [0.2341, 0.3251] |
| cell precision | 0.6065 [0.5383, 0.6720] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.4963 | 0.4092 | 0.2853 |
| cell_recall | 0.4718 | 0.3131 | 0.1847 |
| cell_precision | 0.5235 | 0.5901 | 0.6270 |
| frame_det_rate | 0.7339 | 0.5413 | 0.3089 |
| frame_recall_V | 0.8722 | 0.6889 | 0.3944 |
| frame_recall_E | 0.8667 | 0.7556 | 0.6222 |
| frame_recall_H | 0.4062 | 0.1667 | 0.0208 |
| cell_recall_V | 0.5029 | 0.3305 | 0.1984 |
| cell_recall_E | 0.7333 | 0.5570 | 0.3304 |
| cell_recall_H | 0.1181 | 0.0369 | 0.0074 |
| band1_cell_recall | 0.1200 | 0.0444 | 0.0044 |
| band2_cell_recall | 0.4622 | 0.3319 | 0.2297 |
| band3_cell_recall | 0.5188 | 0.3653 | 0.2406 |
| band4_cell_recall | 0.4762 | 0.2984 | 0.1518 |
| band1_cell_fpr_off | 0.0047 | 0.0022 | 0.0007 |
| band2_cell_fpr_off | 0.0132 | 0.0093 | 0.0056 |
| band3_cell_fpr_off | 0.0699 | 0.0390 | 0.0179 |
| band4_cell_fpr_off | 0.0824 | 0.0194 | 0.0027 |
| frame_fa_off | 0.3162 | 0.1397 | 0.0735 |
| cell_fpr_off | 0.0425 | 0.0175 | 0.0067 |
| cell_fpr_on_neg | 0.1282 | 0.0708 | 0.0388 |
