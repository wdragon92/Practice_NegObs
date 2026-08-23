# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/b2_s44/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.45 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.2796 [0.1910, 0.3736] | 0.1706 [0.1114, 0.2310] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.0278 [0.0000, 0.0735] | 0.0116 [0.0000, 0.0304] | 72 |
| **any tier (frame detection rate)** | 0.1697 [0.1143, 0.2289] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1007 [0.0679, 0.1375] |
| cell FPR (off frames) | 0.0179 [0.0111, 0.0257] |
| cell FPR (negative cells of on frames) | 0.0237 [0.0148, 0.0337] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0741 [0.0000, 0.1905] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.4015 [0.2459, 0.5641] | 0.0521 [0.0328, 0.0739] |
| 3a [5,8) m | 0.1549 [0.0997, 0.2133] | 0.0174 [0.0096, 0.0267] |
| 3b [8,12) m | 0.0333 [0.0179, 0.0512] | 0.0021 [0.0000, 0.0048] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1758 [0.1149, 0.2357] |
| cell recall | 0.1133 [0.0723, 0.1557] |
| cell precision | 0.3919 [0.2616, 0.5159] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.45

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.3011 [0.2111, 0.3980] | 0.2005 [0.1354, 0.2667] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.0278 [0.0000, 0.0735] | 0.0116 [0.0000, 0.0304] | 72 |
| **any tier (frame detection rate)** | 0.1818 [0.1257, 0.2431] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1111 [0.0757, 0.1495] |
| cell FPR (off frames) | 0.0234 [0.0152, 0.0328] |
| cell FPR (negative cells of on frames) | 0.0320 [0.0211, 0.0438] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0741 [0.0000, 0.1905] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.4394 [0.2892, 0.5968] | 0.0667 [0.0442, 0.0925] |
| 3a [5,8) m | 0.1811 [0.1183, 0.2480] | 0.0229 [0.0131, 0.0343] |
| 3b [8,12) m | 0.0455 [0.0262, 0.0674] | 0.0042 [0.0007, 0.0085] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.1939 [0.1299, 0.2568] |
| cell recall | 0.1325 [0.0870, 0.1798] |
| cell precision | 0.3614 [0.2444, 0.4759] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.2549 | 0.1758 | 0.0995 |
| cell_recall | 0.2125 | 0.1133 | 0.0550 |
| cell_precision | 0.3184 | 0.3919 | 0.5238 |
| frame_det_rate | 0.2121 | 0.1697 | 0.1152 |
| frame_recall_V | 0.3333 | 0.2796 | 0.1828 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.0556 | 0.0278 | 0.0278 |
| cell_recall_V | 0.3164 | 0.1706 | 0.0820 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.0278 | 0.0116 | 0.0069 |
| band1_cell_recall | 0.1111 | 0.0741 | 0.0000 |
| band2_cell_recall | 0.6515 | 0.4015 | 0.2045 |
| band3_cell_recall | 0.2756 | 0.1549 | 0.0866 |
| band4_cell_recall | 0.0924 | 0.0333 | 0.0091 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.1083 | 0.0521 | 0.0153 |
| band3_cell_fpr_off | 0.0556 | 0.0174 | 0.0042 |
| band4_cell_fpr_off | 0.0194 | 0.0021 | 0.0007 |
| frame_fa_off | 0.1493 | 0.1007 | 0.0417 |
| cell_fpr_off | 0.0458 | 0.0179 | 0.0050 |
| cell_fpr_on_neg | 0.0618 | 0.0237 | 0.0068 |
