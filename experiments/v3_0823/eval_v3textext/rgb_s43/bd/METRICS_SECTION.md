# METRICS_SECTION — polar hazard grid

arm: **rgb** · subset: **test** · ckpt: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2/rgb_s43/best.pt`
grid: **PROVISIONAL-GRID-V1** (4 bands x 5 sectors = 20 cells, edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
tau_op = 0.5 · tau_star = 0.71 (fitted on **val**, val cell-F1 n/a) · bootstrap 10000x seed 42

## 0. Subset composition

| frames | on | off | hazard-on | V | E | H | scenes | pos cells |
|---|---|---|---|---|---|---|---|---|
| 576 | 288 | 288 | 165 | 93 | 0 | 72 | 6 | 1200 |

## 1a. Stratified recall by evidence tier @ tau_op = 0.5

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.6022 [0.5048, 0.7011] | 0.5677 [0.4768, 0.6502] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.2917 [0.1884, 0.4000] | 0.3611 [0.2324, 0.4878] | 72 |
| **any tier (frame detection rate)** | 0.4667 [0.3908, 0.5422] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.2257 [0.1783, 0.2758] |
| cell FPR (off frames) | 0.0724 [0.0536, 0.0937] |
| cell FPR (negative cells of on frames) | 0.0329 [0.0223, 0.0445] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.5833 [0.4026, 0.7570] | 0.0382 [0.0199, 0.0603] |
| 3a [5,8) m | 0.5617 [0.4639, 0.6556] | 0.0806 [0.0547, 0.1098] |
| 3b [8,12) m | 0.4561 [0.3798, 0.5315] | 0.1708 [0.1303, 0.2140] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.5019 [0.4308, 0.5651] |
| cell recall | 0.4933 [0.4160, 0.5654] |
| cell precision | 0.5108 [0.4286, 0.5910] |

## 1b. Stratified recall by evidence tier @ tau_star = 0.71

| tier | frame recall [95% CI] | cell recall [95% CI] | n frames |
|---|---|---|---|
| V | 0.4946 [0.3913, 0.5960] | 0.4531 [0.3533, 0.5466] | 93 |
| E | n/a [n/a, n/a] | n/a [n/a, n/a] | 0 |
| H | 0.2500 [0.1525, 0.3521] | 0.3218 [0.2010, 0.4432] | 72 |
| **any tier (frame detection rate)** | 0.3879 [0.3132, 0.4620] | — | 165 |

> frame detection rate = fraction of hazard frames where ANY GT-positive cell fires. It is the V0<->V1 continuity metric: splitting a band in two cannot change it, so V0 and V1 numbers are directly comparable on this row.

| false alarms | value [95% CI] |
|---|---|
| frame-FA rate (off frames) | 0.1701 [0.1277, 0.2148] |
| cell FPR (off frames) | 0.0571 [0.0408, 0.0754] |
| cell FPR (negative cells of on frames) | 0.0173 [0.0098, 0.0262] |

| distance band | cell recall [95% CI] | cell FPR on off-arm [95% CI] |
|---|---|---|
| 1 [0,2) m | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] |
| 2 [2,5) m | 0.4773 [0.2880, 0.6639] | 0.0236 [0.0087, 0.0422] |
| 3a [5,8) m | 0.4514 [0.3553, 0.5446] | 0.0556 [0.0327, 0.0816] |
| 3b [8,12) m | 0.3818 [0.3063, 0.4554] | 0.1493 [0.1101, 0.1906] |

| overall | value [95% CI] |
|---|---|
| cell F1 | 0.4649 [0.3878, 0.5346] |
| cell recall | 0.4058 [0.3278, 0.4796] |
| cell precision | 0.5441 [0.4497, 0.6348] |

## 2. Threshold sweep

| metric | tau=0.3 | tau=0.5 | tau=0.7 |
|---|---|---|---|
| cell_f1 | 0.5296 | 0.5019 | 0.4685 |
| cell_recall | 0.6083 | 0.4933 | 0.4117 |
| cell_precision | 0.4689 | 0.5108 | 0.5435 |
| frame_det_rate | 0.6364 | 0.4667 | 0.4000 |
| frame_recall_V | 0.7634 | 0.6022 | 0.5161 |
| frame_recall_E | n/a | n/a | n/a |
| frame_recall_H | 0.4722 | 0.2917 | 0.2500 |
| cell_recall_V | 0.6940 | 0.5677 | 0.4609 |
| cell_recall_E | n/a | n/a | n/a |
| cell_recall_H | 0.4560 | 0.3611 | 0.3241 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_recall | 0.7045 | 0.5833 | 0.4848 |
| band3_cell_recall | 0.6693 | 0.5617 | 0.4541 |
| band4_cell_recall | 0.5788 | 0.4561 | 0.3894 |
| band1_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 |
| band2_cell_fpr_off | 0.0604 | 0.0382 | 0.0236 |
| band3_cell_fpr_off | 0.1160 | 0.0806 | 0.0563 |
| band4_cell_fpr_off | 0.2139 | 0.1708 | 0.1500 |
| frame_fa_off | 0.3299 | 0.2257 | 0.1701 |
| cell_fpr_off | 0.0976 | 0.0724 | 0.0575 |
| cell_fpr_on_neg | 0.0581 | 0.0329 | 0.0184 |
