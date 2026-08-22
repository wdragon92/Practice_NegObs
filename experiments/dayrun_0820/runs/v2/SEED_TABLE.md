# Recipe v2 — 3-seed summary

root `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/runs/v2` · models ['rgb', 'depth', 'b2'] · seeds [42, 43, 44] · grid **PROVISIONAL-GRID-V1** (20 cells)

`mean ± range/2` over seeds. The spread is seed variability, **not** a confidence interval — per-run bootstrap CIs live in each run's `METRICS_SECTION.md`.

## 1. Headline table (tau_op = 0.5)

| model | n seeds | frame_recall_H | frame_recall_E | frame_recall_V | frame_det_rate | frame_fa_off | cell_fpr_off | cell_f1 | cell_recall | cell_precision | band1_cell_recall | band2_cell_recall | band3_cell_recall | band4_cell_recall | band1_cell_fpr_off | band2_cell_fpr_off | band3_cell_fpr_off | band4_cell_fpr_off |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rgb | 3 | 0.688 ± 0.141 | 0.556 ± 0.378 | 0.796 ± 0.164 | 0.730 ± 0.179 | 0.359 ± 0.127 | 0.047 ± 0.016 | 0.450 ± 0.102 | 0.385 ± 0.125 | 0.566 ± 0.021 | 0.000 ± 0.000 | 0.265 ± 0.097 | 0.297 ± 0.103 | 0.511 ± 0.206 | 0.000 ± 0.000 | 0.010 ± 0.004 | 0.041 ± 0.021 | 0.136 ± 0.064 |
| depth | 3 | 0.438 ± 0.031 | 0.600 ± 0.000 | 0.917 ± 0.042 | 0.716 ± 0.014 | 0.042 ± 0.029 | 0.009 ± 0.008 | 0.677 ± 0.031 | 0.652 ± 0.031 | 0.705 ± 0.031 | 0.188 ± 0.064 | 0.579 ± 0.032 | 0.671 ± 0.110 | 0.701 ± 0.051 | 0.000 ± 0.000 | 0.011 ± 0.015 | 0.013 ± 0.013 | 0.012 ± 0.006 |
| b2 | 3 | 0.229 ± 0.156 | 0.178 ± 0.267 | 0.730 ± 0.111 | 0.499 ± 0.148 | 0.238 ± 0.143 | 0.035 ± 0.029 | 0.340 ± 0.075 | 0.276 ± 0.121 | 0.527 ± 0.108 | 0.000 ± 0.000 | 0.160 ± 0.071 | 0.244 ± 0.134 | 0.354 ± 0.138 | 0.000 ± 0.000 | 0.009 ± 0.010 | 0.033 ± 0.040 | 0.097 ± 0.066 |

## 2. Twin on−off delta (kept pose-matched pairs) + tau*

| model | n seeds | twin delta (all) | twin delta (H tier) | tau* | best epoch |
|---|---|---|---|---|---|
| rgb | 3 | 0.314 ± 0.007 | 0.285 ± 0.094 | 0.55 ± 0.20 | 19.0 ± 8.0 |
| depth | 3 | 0.608 ± 0.078 | 0.407 ± 0.037 | 0.39 ± 0.20 | 16.0 ± 13.5 |
| b2 | 3 | 0.234 ± 0.038 | 0.110 ± 0.059 | 0.45 ± 0.00 | 5.7 ± 3.5 |

## 3. Per-seed detail

| model | seed | frame_recall_H | frame_recall_E | frame_recall_V | frame_det_rate | frame_fa_off | cell_fpr_off | cell_f1 | cell_recall | cell_precision | twin all | twin H | tau* | best ep | sel | stop |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rgb | 42 | 0.594 | 0.600 | 0.828 | 0.731 | 0.375 | 0.053 | 0.485 | 0.432 | 0.553 | 0.310 | 0.170 | 0.63 | 9 | 0.732 | early_stop@24 |
| rgb | 43 | 0.875 | 0.911 | 0.944 | 0.908 | 0.478 | 0.060 | 0.535 | 0.486 | 0.594 | 0.309 | 0.359 | 0.71 | 23 | 0.721 | early_stop@38 |
| rgb | 44 | 0.594 | 0.156 | 0.617 | 0.550 | 0.223 | 0.028 | 0.330 | 0.236 | 0.551 | 0.323 | 0.327 | 0.31 | 25 | 0.729 | early_stop@40 |
| depth | 42 | 0.406 | 0.600 | 0.967 | 0.734 | 0.051 | 0.004 | 0.705 | 0.683 | 0.727 | 0.621 | 0.413 | 0.36 | 15 | 0.828 | early_stop@30 |
| depth | 43 | 0.469 | 0.600 | 0.883 | 0.706 | 0.007 | 0.003 | 0.685 | 0.651 | 0.723 | 0.680 | 0.440 | 0.21 | 30 | 0.801 | early_stop@45 |
| depth | 44 | 0.438 | 0.600 | 0.900 | 0.706 | 0.066 | 0.019 | 0.642 | 0.621 | 0.665 | 0.524 | 0.367 | 0.6 | 3 | 0.825 | early_stop@18 |
| b2 | 42 | 0.083 | 0.000 | 0.667 | 0.391 | 0.211 | 0.025 | 0.273 | 0.185 | 0.526 | 0.186 | 0.073 | 0.45 | 8 | 0.736 | early_stop@23 |
| b2 | 43 | 0.396 | 0.533 | 0.872 | 0.688 | 0.395 | 0.069 | 0.424 | 0.427 | 0.420 | 0.263 | 0.069 | 0.45 | 1 | 0.737 | early_stop@16 |
| b2 | 44 | 0.208 | 0.000 | 0.650 | 0.419 | 0.108 | 0.010 | 0.322 | 0.216 | 0.635 | 0.253 | 0.187 | 0.45 | 8 | 0.773 | early_stop@23 |

---

## 4th row + appendix (0821 chain)

*Appended 2026-08-21 by the resumed GPU chain (A1 · A2). **Sections 1–3 above are unmodified.**
Section 4 below is the **main-table row 4** — it joins rgb/depth/b2 in the paper's 4-row table.
Section 5 is **appendix only** and must NOT be added to that table (D-approval #2 / brief A2:
"결과는 부록·발전 서사용, 본 표는 4행 유지").*

### 4. MAIN TABLE ROW 4 — YOLOv8n detector baseline (3 seeds)

Provenance: `experiments/dayrun_0820/runs/yolo_s{42,43,44}/eval_test/metrics.json`, block
`point.op`. Same 816-frame v2 test set, same grid, same 20 cells as sections 1–3.
**τ = 0.25 for this row only** (approval item #1: τ_op = 0.5 stays for the U-Net rows; the detector
row runs at its own confidence threshold). Mapping rule: `code/yolo/det2cell.py`,
documented in `experiments/dayrun_0820/METRICS_NOTES_yolo.md`.

| model | n seeds | frame_recall_H | frame_recall_E | frame_recall_V | frame_det_rate | frame_fa_off | cell_fpr_off | cell_f1 | cell_recall | cell_precision | band1_cell_recall | band2_cell_recall | band3_cell_recall | band4_cell_recall |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| yolov8n @ τ0.25 | 3 | **0.000 ± 0.000** | **0.000 ± 0.000** | 0.150 ± 0.028 | 0.083 ± 0.015 | 0.024 ± 0.018 | 0.0015 ± 0.0010 | 0.026 ± 0.002 | 0.014 ± 0.001 | 0.472 ± 0.110 | 0.123 ± 0.030 | 0.056 ± 0.007 | 0.001 ± 0.001 | 0.000 ± 0.001 |

`mean ± range/2` over seeds, matching the convention of section 1. (Sample sd for the headline
V figure is 0.029, i.e. the same to two decimals; quote either, but say which.)

#### 4.1 Per-seed detail

| model | seed | frame_recall_H | frame_recall_E | frame_recall_V | frame_det_rate | frame_fa_off | cell_fpr_off | cell_f1 | cell_recall | cell_precision | band1_cell_recall |
|---|---|---|---|---|---|---|---|---|---|---|---|
| yolov8n | 42 | 0.000 | 0.000 | 0.117 | 0.064 | 0.005 | 0.0004 | 0.025 | 0.013 | 0.607 | 0.103 |
| yolov8n | 43 | 0.000 | 0.000 | 0.161 | 0.089 | 0.025 | 0.0016 | 0.029 | 0.015 | 0.387 | 0.162 |
| yolov8n | 44 | 0.000 | 0.000 | 0.172 | 0.095 | 0.042 | 0.0025 | 0.025 | 0.013 | 0.422 | 0.103 |

#### 4.2 What the row establishes

**The D22 constructive ceiling is confirmed on all three seeds, with zero mapping leak.**
`frame_recall_E` and `frame_recall_H` are **exactly 0.000 on 42, 43 and 44** — cell-level too
(`cell_recall_E` = `cell_recall_H` = 0.000 everywhere). Per `METRICS_NOTES_yolo.md` §1 and §3 this
is the *required* result, not a disappointment: the `det2cell` mapping projects a detected box onto
the ground plane, so a hazard with no visible pixels can produce no box and therefore no cell. A
nonzero E/H number here would have been a **mapping-leak alarm**, and the alarm did not fire.

Two honest footnotes:

1. **The zero is exact at τ_op = 0.25 and at every τ above it.** In the sub-operating sweep row
   τ = 0.10, seeds 42 and 44 each show `frame_recall_H` = 0.0104 — that is **1 hazard frame of 96**,
   with `cell_recall_H` 0.0021 / 0.0064. It is a single low-confidence box landing in a near band via
   the mapping's known near-band bias (`METRICS_NOTES_yolo.md` §2), not H-tier perception. Quote the
   ceiling at the operating point; if the sweep is shown, this line goes with it.
2. **The V number is a floor, not the detector's ability.** V recall 0.150 with cell precision 0.472
   says the detector finds a minority of visible drops and places roughly half of those correctly.
   The row's argument is about the E/H columns; do not over-read the V column as "YOLO cannot see".

Seed spread is the story on FA: `frame_fa_off` runs 0.005 → 0.025 → 0.042 across seeds — an
8-fold range on a 3-seed sample. Report it as ±range/2 and do not claim a difference against any
U-Net arm on the strength of it.

---

### 5. APPENDIX (NOT the main table) — auxiliary pixel-loss ablation, rgb seed 42

Provenance: arm `experiments/dayrun_0820/runs/v2/rgb_s42_aux/eval_test/metrics.json` ·
paired comparison `experiments/dayrun_0820/runs/v2/compare_aux_vs_base_s42/METRICS_SECTION.md` §3
(816 common frames, paired percentile bootstrap 10000x, seed 42, τ = 0.5).
**One seed only. This is a development-narrative row, not a result row.**

Config delta vs base `rgb_s42` is a clean single variable: identical encoder
(`resnet34-unet-aux`, 24.447 M params), identical selector
(`0.5*val_f1 + 0.5*val_h_frame_recall`), identical `oversample_h` 4.0, `aug` off, seed 42 —
only `aux_enabled=True`, `aux_lambda=0.5`, 648 amodal masks
(`experiments/dayrun_0820/annotations/amodal`).

| arm | frame_recall_V | frame_recall_E | frame_recall_H | frame_det_rate | frame_fa_off | cell_f1 | cell_recall | cell_precision | cell_fpr_off | twin Δ (all) | twin Δ (H) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| rgb_s42 **base** | 0.828 | 0.600 | 0.594 | 0.731 | 0.375 | 0.485 | 0.432 | 0.553 | 0.053 | 0.310 | 0.170 |
| rgb_s42 **+aux** | 0.639 | **0.000** | 0.719 | 0.563 | **0.167** | **0.525** | 0.427 | **0.682** | **0.023** | 0.368 | **0.326** |

#### 5.1 Paired CIs (aux − base, 95 %, from `compare_aux_vs_base_s42`)

| metric | aux | base | Δ [95 % CI] | CI excludes 0 |
|---|---|---|---|---|
| cell_f1 | 0.5255 | 0.4852 | **+0.0403** [0.0001, 0.0786] | yes (barely) |
| cell_precision | 0.6821 | 0.5530 | **+0.1291** [0.0885, 0.1690] | yes |
| cell_recall | 0.4274 | 0.4322 | −0.0048 [−0.0488, 0.0377] | no |
| frame_fa_off | 0.1667 | 0.3750 | **−0.2083** [−0.2531, −0.1646] | yes |
| cell_fpr_off | 0.0230 | 0.0527 | **−0.0297** [−0.0372, −0.0222] | yes |
| cell_fpr_on_neg | 0.0636 | 0.0933 | −0.0296 [−0.0450, −0.0142] | yes |
| **frame_recall_H** | 0.7188 | 0.5938 | +0.1250 [**−0.0096**, 0.2526] | **no** |
| **cell_recall_H** | 0.6072 | 0.2527 | **+0.3546** [0.2768, 0.4302] | yes |
| frame_recall_E | 0.0000 | 0.6000 | **−0.6000** [−0.7436, −0.4528] | yes |
| cell_recall_E | 0.0000 | 0.3592 | **−0.3592** [−0.4556, −0.2626] | yes |
| frame_recall_V | 0.6389 | 0.8278 | **−0.1889** [−0.2551, −0.1257] | yes |
| frame_det_rate | 0.5627 | 0.7309 | **−0.1682** [−0.2296, −0.1064] | yes |
| band3_cell_fpr_off | 0.0221 | 0.0662 | −0.0441 [−0.0591, −0.0301] | yes |
| band4_cell_fpr_off | 0.0691 | 0.1358 | −0.0667 [−0.0867, −0.0467] | yes |

#### 5.2 Reading — a precision/H trade bought with the E tier

The pixel-loss arm is **not uniformly better or worse; it moves the operating character**. It buys
precision (+0.129, CI clear) and halves false alarms (0.375 → 0.167, CI clear) while *raising the
H-tier cell recall by +0.355* — the single largest confirmed effect in the table, and the one that
matters for this paper's thesis. The twin evidence agrees independently: the H-tier twin Δ nearly
doubles, 0.170 → 0.326.

**The price is the E tier, and it is total.** `frame_recall_E` goes 0.600 → **0.000**
(CI [−0.744, −0.453]); cell-level E recall 0.359 → 0.000. Rim-only hazards, which the base arm
partly caught, become invisible to the aux arm. V recall also falls 0.828 → 0.639 and the overall
frame detection rate with it (0.731 → 0.563).

**Two caveats that must travel with this row.** (i) The headline-sounding H gain at *frame* level,
+0.125, has a **CI containing zero** ([−0.010, 0.253]); only the *cell*-level H gain is confirmed.
Write the claim at cell level or not at all. (ii) n = 1 seed. Given that the base rgb arm's own
3-seed H spread is ±0.141 (section 1), a single-seed +0.125 frame-level move is inside seed noise.
Nothing here supports a recipe change inside the 8/24 freeze; it supports a "future work" paragraph.

> **[정정 부기, weekend_0823 D41]** §5.2의 `cell_recall_H +0.3546` 유의 주장(프레임
> i.i.d. 부트스트랩 CI [0.0001,…])은 씬-클러스터 재표집에서 [−0.1429, 0.4625]로
> 0을 포함 — **유의 주장 철회**. aux의 생존 효과는 FA/정밀도 계열만
> (`frame_fa_off`·`cell_fpr_off`·`frame_recall_V`). 원장: weekend_0823/rt_response/F5.
