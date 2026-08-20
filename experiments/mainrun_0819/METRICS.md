# METRICS — mainrun_0819 consolidated (night-1)

> ## ⚠ PROVISIONAL-GRID-V0 BANNER
> Every number on this page is computed on a polar grid that **does not exist in the
> repository** and was *declared*, not extracted (`DECISIONS.md` D3, `SPEC_CONFLICTS.md`).
> Labels are **derived**, not authored: GT footprint = on/off height-map difference
> (`footprint v2-diff-stepgate`, D10), tiers = depth re-projection (`derived-depth-v0-strict`, D6).
> The train/val/test split is **PROVISIONAL** and awaits sign-off (D18).
> If the grid constants change in the morning, every table below must be regenerated
> (`code/labeling/gridspec_v0.json` → re-derive → re-train, ~40 min, renders reused).
>
> Grid: 5 azimuth sectors A–E over [+31.1°, −31.1°] (12.44° each, A = image-left = +azimuth CCW)
> × 3 distance bands 1 = [0,2) m, 2 = [2,5) m, 3 = [5,12) m. Cell index = band·5 + sector,
> cell name = `<sector><band>` (e.g. `C3` = centre sector, far band). Hazard depth 0.30 m.
> Cell-positive rule: **any footprint sample inside the wedge**.

Run date 2026-08-19/20 · manifest `dataset_manifest_v1.json` · split `split_v1.json`
Sources: `runs/rgb_s42/eval_test/`, `runs/depth_s42/eval_test/`, `runs/compare_rgb_depth/`,
`runs/*/twin/`, `GATES_REPORT.md`, `SPLIT_PROPOSAL.md`.

---

## 1. Evaluation definitions

Authority: `code/eval_polar.py::bundle` (lines 82–112). Stated here verbatim so the paper text
cannot drift from the code.

| term | definition |
|---|---|
| cell positive (prediction) | `p_cell >= tau`, per-cell sigmoid from the 15-way aux head |
| cell positive (GT) | `polar_gt[cell] > 0.5`, i.e. ≥1 footprint sample fell in the wedge |
| hazard-on frame | `toggle_state == "on"` **and** ≥1 GT-positive cell (`n = 141` in test) |
| frame detected (frame recall) | **any** GT-positive cell of that frame fires: `(pred & gt).any()` |
| frame FA rate (off) | fraction of hazard-**off** frames where **any** cell fires (`pred.any()`) |
| cell FPR (off) | fired cells / all cells of off frames (off frames carry 0 GT-positive cells) |
| cell FPR (on-neg) | fired cells / GT-negative cells of on frames |
| cell F1 / recall / precision | micro-averaged over all cells of the subset (on + off frames) |
| band-b cell recall | over GT-positive cells of band *b*, hazard-on frames only |
| tier recall | over hazard-on frames of that tier only; tiers V/E/H, `H_weak` & `none_in_fov` excluded |
| τ_op | fixed operating threshold 0.5, reported for both arms |
| τ* | threshold maximising **val** cell-F1 on a 0.05–0.95 / 0.01 grid, then applied to test |

**Bootstrap method note.** Percentile bootstrap, **10 000 resamples, `numpy.default_rng(seed=42)`,
α = 0.05, frame-level resampling** (`code/bootstrap.py`). CIs are 2.5 / 97.5 percentiles of the
resampled statistic. Paired comparisons (§6) and twin deltas (§7) resample the *pair index*, so the
two arms / two toggle states always move together — the CI is on the **difference**, not a
difference of two independent CIs. `n_valid = 10000/10000` on every reported statistic.

---

## 2. Corpus, labels, split

| item | value |
|---|---|
| render | 33 scenes × 3 light conds (L0/L5/L7) × 8 cameras × 2 arms (hazard on/off) = **1584 frames** |
| seed | 20260819 (identical camera-pose bytes across arms → true twins) |
| sidecars | `<cut>.depth.npy` (f16, distance-to-image-plane) 1583/1584; per-scene-arm height maps 66 |
| label lineage | v0 (per-cut ground plane) → **v2** (twin height-map diff ≥0.30 m + near-boundary step gate, D10) → **v2.1** (pre-gate GT preserved, HOLD flow, D14) |
| held scenes | **4** — `sceneD4` (dark exposure + roof-blind height map), `scene11`, `scene13`, `scene19` (mislabel risk, D17) |
| eligible | **29 scenes / 1392 frames** (192 frames held out) |

### 2.1 Tier distribution (eligible 29 scenes, frame counts)

| subset | V | E | H (strict) | H_weak | none_in_fov | off | frames |
|---|---|---|---|---|---|---|---|
| train (20 sc) | 294 | 21 | 24 | 12 | 129 | 480 | 960 |
| val (2 sc) | 33 | 6 | 0 | 0 | 9 | 48 | 96 |
| test (7 sc) | 111 | 9 | 21 | 0 | 27 | 168 | 336 |
| **total** | **438** | **36** | **45** | **12** | **165** | **696** | **1392** |

Full-manifest (33-scene) totals from `GATES_REPORT.md` G3 are `V 438 · E 36 · H 45 · H_weak 12 ·
none_in_fov 261 · off 792`; the held 4 scenes contribute only `none_in_fov 96` and `off 96`, which
is why V/E/H are unchanged by the hold.

### 2.2 Split (PROVISIONAL, D18 — sign-off pending)

| split | scenes | strict-H frames |
|---|---|---|
| test | `scene05 scene07 scene14 scene15 scene18 sceneC2 sceneN3` | **21** |
| val | `scene10 sceneD3` | 0 (H-free by design, PROOF-9) |
| train | 20 scenes | 24 |
| HOLD | `scene11 scene13 scene19 sceneD4` | 0 (in no split) |

11 split proofs PASS (`SPLIT_PROPOSAL.md` PROOF-1…10 + PROOF-7b). `--force-test scene14`
was used to put the highest-strict-H scene in test for CI width (D18).

### 2.3 Test-set GT mass (denominators for §5, §8)

| stratum | GT-positive cells |
|---|---|
| all hazard-on frames | **981** |
| tier V (111 fr) / E (9 fr) / H (21 fr) | 852 / 39 / 90 |
| band 1 near / 2 mid / 3 far | 117 / 276 / 588 |
| negative cells, off frames | 2520 |
| negative cells, on frames | 1539 |

### 2.4 Tier-threshold sensitivity (GATES_REPORT)

strict-H is **τ-insensitive**: 45 frames at all 9 combinations of τ_int ∈ {1, 50, 200} px ×
τ_edge ∈ {0.02, 0.05, 0.10}. Only the V/E boundary moves (V 417–453, E 33–42). Operating point
used everywhere below: τ_int = 50, τ_edge = 0.02.

---

## 3. Training runs and convergence flags

| run | input | ckpt | epochs run | early stop | best val cell-F1 | at epoch | sec/epoch | flag |
|---|---|---|---|---|---|---|---|---|
| `rgb_s42` | RGB 3ch | `runs/rgb_s42/best.pt` | 16 | @16 (patience 15) | 0.2987 | **1** | 13.8 | ⚠ **CONVERGENCE FLAG** |
| `depth_s42` | depth 1ch (sim, clean) | `runs/depth_s42/best.pt` | 25 | @25 | 0.3259 | 10 | 5.7 | ok |
| `rgb_s43` | RGB 3ch | — | in progress | — | 0.2891 @ ep1 (so far) | — | 13.8 | see §11 |

Architecture both arms: `smp.Unet(resnet34, aux_params={classes:15, pooling:avg})` → `[B,15]`
logits, 24.4 M params, img 512², batch 8, LR 3e-4 linear decay, no augmentation, `max_epochs 150`,
`patience 15`, weight decay 0.

**RGB convergence flag, in full.** `runs/rgb_s42/metrics.csv`: val cell-F1 peaks at epoch 1
(0.2987) and never recovers, while train loss falls 0.320 → 0.023 and val loss rises
0.392 → 0.752. That is a textbook overfit signature, compounded by a **2-scene validation set
(96 frames, 0 strict-H)** whose F1 is noisy at the ±0.05 level epoch to epoch. Two readings are
open and cannot be separated tonight: (a) the RGB arm genuinely learns little beyond epoch 1 from
960 training frames, or (b) the checkpoint selector picked a barely-trained network because the
val signal is too weak to rank checkpoints. Either way, **RGB test numbers below should be read as
a lower bound on what this architecture can do**, and the RGB−Depth gap in §6 is an upper bound on
the true modality gap.

Depth val F1 also peaks early (ep 10 of 25) with a rising val loss, but the peak is mid-run and
the test numbers are far above the val F1, so the checkpoint is not obviously mis-selected.

---

## 4. Headline table @ τ_op = 0.5 (test, 336 frames / 7 scenes)

| metric | RGB U-Net [95% CI] | Depth U-Net [95% CI] |
|---|---|---|
| cell F1 | 0.4415 [0.3797, 0.5005] | **0.6893 [0.6542, 0.7213]** |
| cell recall | 0.4312 [0.3668, 0.4961] | 0.6208 [0.5782, 0.6630] |
| cell precision | 0.4524 [0.3756, 0.5328] | 0.7748 [0.7219, 0.8226] |
| frame recall V (n=111) | 0.6667 [0.5772, 0.7547] | **0.9189 [0.8649, 0.9658]** |
| frame recall E (n=9) | 0.4444 [0.1111, 0.8000] | 0.3333 [0.0000, 0.6667] |
| frame recall H (n=21) | 0.3333 [0.1333, 0.5455] | **0.7143 [0.5000, 0.9000]** |
| frame FA rate, off arm (n=168) | 0.2738 [0.2071, 0.3438] | **0.1607 [0.1071, 0.2195]** |
| cell FPR, off frames | 0.1004 [0.0738, 0.1297] | 0.0298 [0.0175, 0.0439] |
| cell FPR, on-frame negatives | 0.1683 [0.1263, 0.2111] | 0.0663 [0.0501, 0.0841] |

### 4.1 Cell-level tier recall @ τ_op = 0.5

| tier | RGB cell recall [95% CI] | Depth cell recall [95% CI] | GT cells |
|---|---|---|---|
| V | 0.4542 [0.3838, 0.5254] | 0.6479 [0.6058, 0.6919] | 852 |
| E | 0.3077 [0.0400, 0.5833] | 0.2308 [0.0000, 0.4286] | 39 |
| H | 0.2667 [0.0909, 0.4590] | 0.5333 [0.3548, 0.7121] | 90 |

The E tier is the only stratum where RGB is nominally ahead of Depth. With 9 frames / 39 cells its
CI spans a third of the unit interval and it is **not** a finding (see §6: paired CI includes 0).

---

## 5. Threshold-tuned operating point (τ* fitted on val, applied to test)

| arm | τ* | val cell-F1 at τ* | test cell F1 | V frame rec | E frame rec | H frame rec | frame FA off |
|---|---|---|---|---|---|---|---|
| RGB | **0.36** | 0.3325 | 0.4560 [0.3942, 0.5156] | 0.7117 [0.6270, 0.7965] | 0.6667 [0.3333, 1.0000] | 0.4762 [0.2609, 0.7000] | 0.3393 [0.2692, 0.4128] |
| Depth | **0.70** | 0.3684 | 0.5828 [0.5308, 0.6296] | 0.7568 [0.6729, 0.8333] | 0.3333 [0.0000, 0.6667] | 0.5714 [0.3529, 0.7857] | 0.1071 [0.0628, 0.1576] |

Note the two arms move in **opposite directions**: val prefers a lower threshold for RGB (recall
up, FA up) and a higher one for Depth (precision up to 0.839, F1 *down* from 0.689 to 0.583).
The Depth τ* is a val-set artefact — the H-free 2-scene val set cannot see the stratum where the
lower threshold pays off. τ_op = 0.5 is the honest headline for both arms; τ* is reported for
completeness and because the protocol asked for it.

### 5.1 Full threshold sweep (test)

| metric | RGB τ=0.3 | RGB τ=0.5 | RGB τ=0.7 | Depth τ=0.3 | Depth τ=0.5 | Depth τ=0.7 |
|---|---|---|---|---|---|---|
| cell_f1 | 0.4717 | 0.4415 | 0.3899 | 0.7249 | 0.6893 | 0.5828 |
| cell_recall | 0.5311 | 0.4312 | 0.3303 | 0.7737 | 0.6208 | 0.4465 |
| cell_precision | 0.4243 | 0.4524 | 0.4758 | 0.6819 | 0.7748 | 0.8391 |
| frame_recall_V | 0.7477 | 0.6667 | 0.6036 | 0.9189 | 0.9189 | 0.7568 |
| frame_recall_E | 0.6667 | 0.4444 | 0.1111 | 0.6667 | 0.3333 | 0.3333 |
| frame_recall_H | 0.5238 | 0.3333 | 0.1905 | 0.7143 | 0.7143 | 0.5714 |
| cell_recall_V | 0.5434 | 0.4542 | 0.3662 | 0.7993 | 0.6479 | 0.4648 |
| cell_recall_E | 0.4872 | 0.3077 | 0.1282 | 0.3077 | 0.2308 | 0.1538 |
| cell_recall_H | 0.4333 | 0.2667 | 0.0778 | 0.7333 | 0.5333 | 0.4000 |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 | 0.3077 | 0.0513 | 0.0000 |
| band2_cell_recall | 0.4529 | 0.2899 | 0.1630 | 0.8478 | 0.6196 | 0.3370 |
| band3_cell_recall | 0.6735 | 0.5833 | 0.4745 | 0.8316 | 0.7347 | 0.5867 |
| frame_fa_off | 0.3750 | 0.2738 | 0.2143 | 0.2143 | 0.1607 | 0.1071 |
| cell_fpr_off | 0.1508 | 0.1004 | 0.0683 | 0.0548 | 0.0298 | 0.0202 |
| cell_fpr_on_neg | 0.2125 | 0.1683 | 0.1202 | 0.1404 | 0.0663 | 0.0214 |

---

## 6. Paired RGB − Depth comparison (same 336 frames, τ = 0.5)

Paired percentile bootstrap, 10 000×, seed 42. Source `runs/compare_rgb_depth/METRICS_SECTION.md` §3.
Negative = Depth better on recall/F1 metrics; positive = RGB worse on FA metrics (FA is
"lower is better", so a positive Δ means RGB false-alarms more).

| metric | RGB (A) | Depth (B) | A − B [95% CI] | CI excludes 0 |
|---|---|---|---|---|
| cell_f1 | 0.4415 | 0.6893 | −0.2478 [−0.3078, −0.1901] | **yes** |
| cell_recall | 0.4312 | 0.6208 | −0.1896 [−0.2600, −0.1167] | **yes** |
| cell_precision | 0.4524 | 0.7748 | −0.3224 [−0.3870, −0.2557] | **yes** |
| frame_recall_V | 0.6667 | 0.9189 | −0.2523 [−0.3462, −0.1610] | **yes** |
| frame_recall_E | 0.4444 | 0.3333 | +0.1111 [0.0000, 0.3750] | no |
| frame_recall_H | 0.3333 | 0.7143 | −0.3810 [−0.6875, −0.0526] | **yes** |
| cell_recall_V | 0.4542 | 0.6479 | −0.1937 [−0.2652, −0.1210] | **yes** |
| cell_recall_E | 0.3077 | 0.2308 | +0.0769 [−0.1290, 0.3043] | no |
| cell_recall_H | 0.2667 | 0.5333 | −0.2667 [−0.6000, 0.0844] | no |
| band1_cell_recall | 0.0000 | 0.0513 | −0.0513 [−0.0893, −0.0177] | **yes** |
| band2_cell_recall | 0.2899 | 0.6196 | −0.3297 [−0.4327, −0.2258] | **yes** |
| band3_cell_recall | 0.5833 | 0.7347 | −0.1514 [−0.2500, −0.0510] | **yes** |
| frame_fa_off | 0.2738 | 0.1607 | +0.1131 [0.0414, 0.1875] | **yes** |
| cell_fpr_off | 0.1004 | 0.0298 | +0.0706 [0.0472, 0.0969] | **yes** |
| cell_fpr_on_neg | 0.1683 | 0.0663 | +0.1020 [0.0568, 0.1482] | **yes** |

Note the split verdict on the H tier: the **frame-level** H advantage clears 0
(−0.3810 [−0.6875, −0.0526]) but the **cell-level** one does not (−0.2667 [−0.6000, 0.0844]).
With 21 H frames / 90 H cells this is exactly the statistical-power problem the +8-camera
re-render (GAP_REPORT ⑦-1) was prepared for.

**Interpretation guardrail (mandatory when quoting the Depth-H row).** Depth here is *simulated,
noise-free* `distance_to_image_plane`. A strict-H frame is one where the hazard contributes no
interior pixels and no visible rim — but a real drop still removes the **floor return** from that
part of the image, so a clean depth map carries a "missing floor band" geometric signature that a
real time-of-flight or stereo sensor, noisy and drop-out-prone at 5–12 m, would carry far more
weakly. The Depth-H recall of 0.714 should therefore be presented as *"what an idealized range
sensor can read off geometry"*, **not** as an achievable sensor baseline, and **not** as a
general geometry upper bound — per spec, the geometry-upper-bound reading (A9) is scoped to the
V tier only.

---

## 7. Twin (hazard on / off) paired analysis — causal context-use evidence

Same camera pose, same lighting, same seed; the **only** difference is the hazard geometry.
`delta_score` = (max predicted probability over GT-positive cells, on arm) − (same cells, off arm).
`delta_frame` = same over all 15 cells. Paired bootstrap 10 000×, seed 42.
Sources: `runs/rgb_s42/twin/twin_analysis.md`, `runs/depth_s42/twin/twin_analysis.md`.

Pairing: 168 test pairs found → **117 pose-matched (kept), 51 excluded**. Pose keys
`d, h_rel, yaw, pitch, ground_z`, tol 1e-6. **All 51 exclusions are `ground_z` mismatches**
(scene05 6, scene07 21, sceneC2 24) — the camera sampler re-draws a pose when the off-arm geometry
changes the rejection outcome, so the two arms stand on slightly different ground. Of the 117 kept
pairs, 93 carry ≥1 GT-positive cell.

| arm | tier | n pairs | Δ score (GT cells) [95% CI] | Δ frame (all cells) [95% CI] |
|---|---|---|---|---|
| RGB | V | 63 | 0.4062 [0.3242, 0.4885] | 0.4082 [0.3261, 0.4911] |
| RGB | E | 9 | 0.1891 [0.0402, 0.3337] | 0.1891 [0.0402, 0.3337] |
| RGB | H | 21 | 0.2398 [0.1556, 0.3313] | 0.2398 [0.1556, 0.3313] |
| RGB | **all** | 117 | **0.3476 [0.2859, 0.4103]** | 0.3291 [0.2761, 0.3815] |
| Depth | V | 63 | 0.6291 [0.5630, 0.6924] | 0.6262 [0.5600, 0.6896] |
| Depth | E | 9 | 0.0301 [0.0056, 0.0564] | 0.0301 [0.0056, 0.0564] |
| Depth | H | 21 | 0.5842 [0.4482, 0.7139] | 0.5920 [0.4616, 0.7161] |
| Depth | **all** | 117 | **0.5610 [0.4972, 0.6227]** | 0.4458 [0.3823, 0.5105] |

Sign consistency: RGB Δ > 0 on **88 of 93** GT-carrying pairs; Depth on **90 of 93**.
Every CI in the table excludes 0, including the RGB **H** row — i.e. on frames where the hazard
contributes no directly visible pixels, removing the hazard still lowers the RGB model's
probability by 0.24 [0.16, 0.33]. That is the night's cleanest evidence that the RGB arm reads
*context*, not the hazard's own pixels.

### 7.1 Per-scene twin detail

| scene | kept / excluded | match rate | RGB mean Δ score | Depth mean Δ score |
|---|---|---|---|---|
| scene05 | 18 / 6 | 0.75 | 0.6290 | 0.7370 |
| scene07 | 3 / 21 | 0.12 | 0.3794 | 0.8963 |
| scene14 | 24 / 0 | 1.00 | 0.3607 | 0.7378 |
| scene15 | 24 / 0 | 1.00 | 0.2608 | 0.3659 |
| scene18 | 24 / 0 | 1.00 | 0.2064 | 0.4053 |
| sceneC2 | 0 / 24 | 0.00 | n/a | n/a |
| sceneN3 (hard neg) | 24 / 0 | 1.00 | n/a (no GT cells) | n/a (no GT cells) |

`sceneN3` is a hard negative with zero GT cells in both arms; its Δ_frame is 0.2521 for RGB but
0.0001 for Depth — the RGB model's output moves when the *illusion dressing* is removed even
though no hazard exists, which is a shortcut-sensitivity signal worth a line in the paper.
`sceneC2` contributes 0 pairs: all 24 are `ground_z` mismatches, so the scene that dominates the
off-arm false alarms (§9) is absent from the twin analysis entirely.

---

## 8. Distance-band decomposition

| band | range | GT cells | RGB recall @0.5 [95% CI] | Depth recall @0.5 [95% CI] | paired Δ (RGB−Depth) |
|---|---|---|---|---|---|
| 1 near | [0, 2) m | 117 | 0.0000 [0.0000, 0.0000] | 0.0513 [0.0177, 0.0893] | −0.0513 [−0.0893, −0.0177] |
| 2 mid | [2, 5) m | 276 | 0.2899 [0.1979, 0.3865] | 0.6196 [0.5299, 0.7065] | −0.3297 [−0.4327, −0.2258] |
| 3 far | [5, 12) m | 588 | 0.5833 [0.5009, 0.6649] | 0.7347 [0.6746, 0.7909] | −0.1514 [−0.2500, −0.0510] |

Both arms are monotonically better with distance, and **band 1 is essentially unsolved** (RGB 0.000
at every threshold; Depth 0.308 at τ=0.3 collapsing to 0.051 at τ=0.5). This mirrors the labeling
side exactly: `GATES_REPORT` G5 (fraction of GT-positive cells holding ≥1 re-projected below-ground
pixel) is **0.029 in band 1, 0.475 in band 2, 0.715 in band 3**, mean 0.552 against a 0.80 target.
A drop's floor immediately behind the lip sits in the camera's view shadow, so a near-band cell is
GT-positive *by construction* with no visible below-ground surface. Near-band failure is therefore
a shared property of the label and the prediction, and **should not be reported as a model result
without the G5 caveat** — a 0.30 m drop at 1 m is genuinely unobservable from an eye-height camera
pitched −20…−2°, and whether band 1 belongs in the metric at all is a morning decision (GAP ⑥).

---

## 9. Qualitative panels (12)

`code/make_viz.py`, RGB arm, τ = 0.5. Each panel = RGB frame + GT 15-cell grid + predicted
probability grid, far band drawn on top, sectors A…E left-to-right.

| group | file | scene | tier | GT cells | max p on GT cells |
|---|---|---|---|---|---|
| hit-H | `viz/hitH_01_on__scene14__L0__s20260819__0003.png.png` | scene14 | H | A3–E3 | **0.821** |
| hit-H | `viz/hitH_02_on__scene14__L0__s20260819__0001.png.png` | scene14 | H | A3–E3 | 0.757 |
| hit-H | `viz/hitH_03_on__scene14__L7__s20260819__0001.png.png` | scene14 | H | A3–E3 | 0.754 |
| hit-H | `viz/hitH_04_on__scene14__L7__s20260819__0003.png.png` | scene14 | H | A3–E3 | 0.738 |
| miss-H | `viz/missH_01_on__scene14__L5__s20260819__0000.png.png` | scene14 | H | A3–E3 | 0.092 |
| miss-H | `viz/missH_02_on__scene15__L4__s20260819__0000.png.png` | scene15 | H | C3 only | **0.093** |
| miss-H | `viz/missH_03_on__scene14__L7__s20260819__0004.png.png` | scene14 | H | A3–D3 | 0.168 |
| miss-H | `viz/missH_04_on__scene14__L0__s20260819__0000.png.png` | scene14 | H | A3–E3 | 0.176 |
| FA-off | `viz/fa_off_01_off__sceneC2__L2__s20260819__0005.png.png` | sceneC2 | off | none | 0.982 (8 cells ≥0.5) |
| FA-off | `viz/fa_off_02_off__sceneC2__L3__s20260819__0005.png.png` | sceneC2 | off | none | 0.981 (8 cells) |
| FA-off | `viz/fa_off_03_off__sceneC2__L7__s20260819__0002.png.png` | sceneC2 | off | none | 0.977 (5 cells) |
| FA-off | `viz/fa_off_04_off__sceneC2__L3__s20260819__0002.png.png` | sceneC2 | off | none | 0.976 (5 cells) |

Readings: the hit-H set is a **far-band anticipation** story — every hit fires the whole band-3 row
of a scene14 frame whose drop is hidden behind a flat-continuous illusion. The miss-H set is
**cue-poor geometry**: `missH_02` (scene15 alley) has a single GT cell `C3` at p = 0.093, i.e. the
model sees nothing at all rather than hedging. All four off-arm false alarms are **sceneC2** and
fire at p ≈ 0.98 across 5–8 cells — one scene, confidently wrong, in the arm where the hazard has
been removed. sceneC2 is also the scene with 0/24 twin pose matches, so it is the single most
important scene to look at by eye in the morning.

---

## 10. Label-provenance caveats carried into every number above

| item | status |
|---|---|
| gate verdict | `GATES_REPORT.md` overall verdict = **GATE FAILURE** (G2 fails on `scene06`, kept deliberately: its hazard is out of frame in all 24 cuts, so all-negative is the correct label) |
| G5 | FAIL/NA at 0.552 mean vs 0.80 target; band-3 value 0.715 (see §8) |
| step-gate exclusions | **33 of 1584 frames, 87 GT cells** withheld by the near-boundary step gate, all preserved as `polar_gt_pregate` + `gate_excluded`. Per scene: `scene03` 12 fr / 45 cells (train), `scene07` 18 fr / 39 cells (**test**), `scene02` 3 fr / 3 cells (train). Reverting the gate is a field swap, not a re-derivation — but it would add 39 positive cells (+4.0 %) to the **test** set via scene07, so the headline numbers do move. |
| twin pose mismatch | corpus-wide 183 / 792 pairs mismatch on `ground_z`; test subset 51 / 168 (§7) |
| tier instrument | `derived-depth-v0-strict`; the spec's semantic-ID instrument (A3) does not exist in the repo |
| glass occluders | not detectable by the derived instrument; `scene06`, `scene08`, `scene12` need a human look (GAP ④) |

---

## 11. seed 43 (variance check)

Final (filled 04:05). `rgb_s43` config identical to `rgb_s42` except `seed: 43`.

| run | early stop | best val F1 (ep) | test cell F1 | V | E | H | frame FA (off) | τ* |
|---|---|---|---|---|---|---|---|---|
| rgb_s42 | @16 | 0.2987 (**ep 1** ⚠) | 0.4415 | 0.667 | 0.444 | 0.333 | 0.274 | 0.36 |
| rgb_s43 | @28 | 0.2943 (ep 13) | 0.4880 | 0.721 | 0.000 | 0.048 | 0.143 | 0.92 |
| spread | — | 0.004 | 0.047 | 0.054 | **0.444** | **0.286** | 0.131 | 0.56 |

Two findings, sharper than the mid-training preview above suggested:
1. **The ep-1 collapse did NOT reproduce** — s43 peaked at ep 13 with a healthy curve. The s42
   convergence flag is real but seed-dependent, not a deterministic property of the recipe.
2. **The headline tiers are seed-unstable while V is stable**: H frame recall 0.048 ↔ 0.333 and
   E 0.000 ↔ 0.444 across two seeds with near-identical val F1 (0.294 vs 0.299). Root cause is
   structural: **val contains zero H frames by design (D18)**, so checkpoint selection is blind to
   exactly the behavior the paper headlines. Morning lever: either a small H-carrying val scene, a
   selection metric weighted toward E/H, or multi-seed reporting (recommended for the paper table
   regardless). RGB rows must be presented as a seed range, not a point.

---

## 12. Discrepancies found while assembling (flagged, not fixed)

1. **Step-gate exclusion count.** The night brief carries "12 frames / 45 cells". The final
   `GATES_REPORT.md` total is **33 frames / 87 cells**. 12/45 is `scene03` alone and matches the
   pre-rescue label pass (`STATUS.md` 01:50); `scene02` and `scene07` gained exclusions when their
   height maps were rebuilt by depth fusion (D17). The 33/87 figure is the current one, and unlike
   12/45 it touches the **test** split.
2. **Tier totals, 33-scene vs 29-scene.** Brief says `none 165 / off 696`; `GATES_REPORT` G3 says
   `none_in_fov 261 / off 792`. Both are right — G3 counts all 33 manifest scenes, the brief counts
   the 29 eligible ones. Difference is exactly the 4 held scenes (96 + 96). No action; stated so the
   paper does not quote two numbers for one thing.
3. **miss-H panel attribution.** The brief describes miss-H as "scene15 alley cue-poor miss 0.093".
   That is `missH_02` only; the other three miss-H panels are **scene14**. The 0.093 value is
   confirmed (0.0932). Panel captions should name the scene per panel.
4. **`runs/compare_rgb_depth/METRICS_SECTION.md` header.** It reports `tau_star = 0.5 (fitted on
   val, val cell-F1 n/a)` and its §1a/§1b are identical — an artefact of running the report writer
   over a per-frame CSV instead of a checkpoint. Only **§3 (the paired table)** of that file is
   meaningful; §1–2 duplicate `runs/rgb_s42/eval_test/`.
5. **Depth E-tier is a regression, not a win.** Depth frame recall E = 0.333 < RGB 0.444. It sits
   in the brief's headline list without comment; the paired CI ([0.0000, 0.3750]) includes 0 and
   n = 9, so nothing can be claimed either way.
6. **Gate verdict is FAILURE.** The brief's headline facts do not mention that `GATES_REPORT.md`
   ends in `GATE FAILURE` (G2 on `scene06`, G5 below target). Both failures are documented and
   deliberate, but "gates passed" must not appear in the paper text.

---

## 13. Links (relative to this file)

| what | path |
|---|---|
| RGB test metrics (md / json) | [`runs/rgb_s42/eval_test/METRICS_SECTION.md`](runs/rgb_s42/eval_test/METRICS_SECTION.md) · [`metrics.json`](runs/rgb_s42/eval_test/metrics.json) |
| RGB per-frame predictions | [`runs/rgb_s42/eval_test/per_frame.csv`](runs/rgb_s42/eval_test/per_frame.csv) (+ `_on` / `_off` / `_val`) |
| Depth test metrics | [`runs/depth_s42/eval_test/METRICS_SECTION.md`](runs/depth_s42/eval_test/METRICS_SECTION.md) · [`metrics.json`](runs/depth_s42/eval_test/metrics.json) |
| paired RGB↔Depth | [`runs/compare_rgb_depth/METRICS_SECTION.md`](runs/compare_rgb_depth/METRICS_SECTION.md) §3 · [`per_frame.csv`](runs/compare_rgb_depth/per_frame.csv) |
| twin analysis | [`runs/rgb_s42/twin/twin_analysis.md`](runs/rgb_s42/twin/twin_analysis.md) · [`runs/depth_s42/twin/twin_analysis.md`](runs/depth_s42/twin/twin_analysis.md) · `twin_pairs.csv` |
| training curves | [`runs/rgb_s42/metrics.csv`](runs/rgb_s42/metrics.csv) · [`runs/depth_s42/metrics.csv`](runs/depth_s42/metrics.csv) · [`runs/rgb_s43/metrics.csv`](runs/rgb_s43/metrics.csv) |
| labels & gates | [`GATES_REPORT.md`](GATES_REPORT.md) · [`code/labeling/gridspec_v0.json`](code/labeling/gridspec_v0.json) · [`annotations/hold_scenes.json`](annotations/hold_scenes.json) |
| split | [`SPLIT_PROPOSAL.md`](SPLIT_PROPOSAL.md) · [`split_v1.json`](split_v1.json) |
| decisions / open items | [`DECISIONS.md`](DECISIONS.md) · [`GAP_REPORT.md`](GAP_REPORT.md) · [`SPEC_CONFLICTS.md`](SPEC_CONFLICTS.md) |
| panels | [`viz/`](viz/) (12 png) · audit overlays [`audit_samples/`](audit_samples/) (30 png) |
| eval / bootstrap code | [`code/eval_polar.py`](code/eval_polar.py) · [`code/bootstrap.py`](code/bootstrap.py) · [`code/twin_analysis.py`](code/twin_analysis.py) |

---

## Night 0820→0821 update

*Appended 2026-08-21 (NIGHTRUN 0820, brief P3-D1). **Append only — §1–§13 above are unmodified.**
Every number here is a CPU recomputation over the **frozen** recipe-v2 artefacts
(`experiments/dayrun_0820/runs/v2/{rgb,depth,b2}_s{42,43,44}`, corpus `dataset_manifest_v2_full.json`
2832 frames, split `split_v2_full.json`, grid `PROVISIONAL-GRID-V1` = 5 sectors × 4 bands
[0,2)/[2,5)/[5,8)/[8,12) m, τ_op = 0.5). v2 test = 816 frames = 408 on (V 180 · E 45 · H 96 ·
H_weak 6 · none_in_fov 81) + 408 off. **Note the denominator change from §4 above**, which is the
v1 336-frame test — v1 and v2 numbers are not directly comparable except on the byte-identical
subsets explicitly named below. No GPU ran: YOLO s43/44, the aux run, the C2 control round and the
hole probe are all prepared-not-run, so the 4-row headline table is unchanged.*

Sources, in order of citation: `nightrun_0820/narrative/diag_v2/DIAG_V2.md` (+ `diag_v2_numbers.json`) ·
`nightrun_0820/TWIN_STRATIFICATION.md` · `nightrun_0820/STRADDLE_REPORT.md` ·
`nightrun_0820/tau_curves/TAU_CURVES.md` (+ `tau_curves.csv`, `tau_best.json`).
Sanity gate: the recomputed all-band twin Δ reproduces every run's `twin/twin_pairs.csv`
`delta_score` to **max |dev| = 0.0000 on all 9 runs**, and the seed means reproduce
`runs/v2/SEED_TABLE.md` §1–§2 exactly — these are the published statistics split, not a
second measurement.

### N.1 Twin Δ stratified by pairing exactness (B5) — the D20 tolerance audit

Strata over the 408 test twin pairs: **EXACT** = all five pose keys (`d`, `h_rel`, `yaw`, `pitch`,
`ground_z`) equal within 1e-6, n = 312 · **TOL** = `|Δground_z| ∈ (1e-6, 0.15]`, n = 54 (the layer
D20 rescued) · **EXCL** = `|Δground_z| > 0.15`, n = 42, never in any published number. Pose audit:
**no pair anywhere differs on a key other than `ground_z`**. Pairing is model-independent, so the
strata are identical across all 9 runs.

| stratum | n | V | E | **H** | H_weak/none | carries ≥1 GT+ cell |
|---|---|---|---|---|---|---|
| EXACT | 312 | 132 | 45 | **96** | 39 | 279 |
| TOL | 54 | 33 | 0 | **0** | 21 | 33 |
| EXCL | 42 | 15 | 0 | 0 | 27 | 15 |

**H-tier twin Δ, EXACT-only vs published (kept = EXACT + TOL), 3-seed mean ± range/2**

| model | EXACT-only H Δ | published H Δ | difference | EXACT CI excludes 0 |
|---|---|---|---|---|
| rgb | **0.285 ± 0.094** | 0.285 ± 0.094 | **+0.0000** | 3/3 seeds |
| depth | **0.407 ± 0.037** | 0.407 ± 0.037 | **+0.0000** | 3/3 seeds |
| b2 | **0.110 ± 0.059** | 0.110 ± 0.059 | **+0.0000** | 3/3 seeds |

Per-seed EXACT-only H Δ [95 % CI, 10 000× paired bootstrap, seed 42, `code/bootstrap.py`]:
rgb 0.1701 [0.1243, 0.2181] · 0.3587 [0.3113, 0.4071] · 0.3267 [0.2478, 0.4066];
depth 0.4131 [0.3242, 0.5039] · 0.4403 [0.3533, 0.5291] · 0.3666 [0.2854, 0.4494];
b2 0.0735 [0.0342, 0.1124] · 0.0688 [0.0511, 0.0881] · 0.1867 [0.1287, 0.2499]. **9/9 exclude 0.**

The identity is structural, not luck: the TOL layer contains **0 H-tier and 0 E-tier pairs**.

**All-tier Δ is a different story — it is inflated by the TOL layer.** Published (kept) minus
EXACT-only: **rgb +0.041 · depth +0.001 · b2 +0.037**. TOL Δ runs 0.41–0.72 against EXACT's 0.26–0.28
(rgb), and 48 of the 54 TOL pairs sit in two scenes — `scene07` (24, Δ_rgb 0.740) and `sceneC2`
(24, Δ_rgb 0.688, the non-appearance-preserving toggle). Measured `|Δground_z|` in the TOL layer:
0.0012 / 0.0015 / 0.003 / 0.004 / 0.0163 / 0.0164 / 0.1137 m (EXCL: 3.57 / 4.02 m = scene datum change).

### N.2 H-tier twin Δ by band (B2-ii) — the band-3b restriction

96 H pairs, 3-seed mean ± range/2 · s42 point [95 % CI].

| band | n pairs | GT cells | RGB | Depth | B2 |
|---|---|---|---|---|---|
| 3a `[5,8)` | 33 | 126 | **−0.031 ± 0.054** · −0.049 [−0.127, **+0.017**] **CI ∋ 0** | +0.534 ± 0.183 · 0.632 [0.472, 0.782] | +0.058 ± 0.060 · −0.020 [−0.098, **+0.044**] **CI ∋ 0** |
| 3b `[8,12)` | 96 | 345 | **+0.293 ± 0.087** · 0.185 [0.138, 0.233] | +0.411 ± 0.031 · 0.413 [0.324, 0.502] | +0.112 ± 0.064 · 0.090 [0.059, 0.124] |
| all | 96 | 471 | 0.285 ± 0.094 · 0.170 [0.124, 0.218] | 0.407 ± 0.037 · 0.413 [0.324, 0.502] | 0.110 ± 0.059 · 0.073 [0.034, 0.114] |

RGB s42, H tier, band 3a: mean p(on) = 0.243 vs mean p(off) = **0.292** (off higher); 55 % of the 33
pairs have Δ > 0. **The H claim is a band-3b claim for RGB and must not be stated for band 3a.**
All-tier by band (366 kept pairs), for reference: RGB 0.044 / 0.321 / 0.301 / 0.309 and Depth
0.280 / 0.612 / 0.659 / 0.599 over bands 1 / 2 / 3a / 3b — every band × model cell excludes 0 on the
s42 bootstrap.

### N.3 The Depth H-recall decline is composition, not regression (B1)

**Premise, measured.** The v2 H set is far-*exclusive*: 0 of 96 H frames carry a GT cell in band 1 or
band 2, 96/96 carry one in band 3b, 33/96 also in 3a; `cam.d` mean 8.57 m (4.59–11.21) against V's
4.99 m; 75 of 96 come from the boost rounds. H frame recall therefore equals band-3b H frame recall
in 8 of the 9 runs (exception B2 s43: 38/96 vs 35/96).

**Control on the byte-identical frames** (v2 test's 21 main-round H frames = v1 test's 21 H frames,
verified by frame-id set equality against `dataset_manifest_v1.json` + `split_v1.json`):

| H frame recall | v1 recipe s42 (§4 above) | v2 recipe, same 21 frames, 3-seed mean ± range/2 | v2, the 75 new boost H frames |
|---|---|---|---|
| RGB | 0.3333 | **0.952 ± 0.048** | 0.613 ± 0.173 |
| Depth | **0.7143** | **0.857 ± 0.000** (18/21, all seeds) | 0.320 ± 0.040 |
| B2 | — | 0.349 ± 0.071 | 0.196 ± 0.207 |

v2-Depth **beats** v1-Depth on v1's own H frames. The headline 0.714 → 0.438 is therefore **100 % a
test-set composition change.**

**The working range axis is camera standoff, not the band label — H frame recall, 3-seed mean [per seed]**

| standoff | n frames | RGB | Depth | B2 |
|---|---|---|---|---|
| `d < 7` m | 24 | 0.917 [0.875/1.000/0.875] | 0.833 [0.750/1.000/0.750] | 0.333 |
| `7 ≤ d < 9` m | 30 | 0.644 [0.500/0.933/0.500] | 0.733 [0.700/0.700/0.800] | 0.133 |
| **`d ≥ 9` m** | **42** | **0.587** [0.500/0.762/0.500] | **0.000 [0.000/0.000/0.000]** | 0.238 |

Check: (24·0.833 + 30·0.733 + 42·0)/96 = 0.438 = Depth's SEED_TABLE H recall. The band form of the
test is not usable — Depth's 3b − 3a gap is −0.230 / −0.168 / **+0.165** across seeds, and on the 33
H frames carrying GT in *both* bands Depth is better far (frame 0.697 vs 0.515).

**Band-restricted H recall (frame / cell), 3-seed mean ± range/2:** 3a (33 fr, 126 cells) RGB
0.101 ± 0.091 / 0.042 · Depth 0.515 ± 0.182 / 0.595 · B2 0.202 ± 0.258 / 0.087 · 3b (96 fr, 345 cells)
RGB 0.688 ± 0.141 / 0.454 · Depth 0.438 ± 0.031 / 0.516 · B2 0.219 ± 0.141 / 0.100.

### N.4 Prior ↔ false-alarm coupling, v1 → v2 (B2-i)

Spearman ρ between the 20-cell train positive rate (768 on-arm frames of the 19 train scenes) and the
20-cell off-arm predicted-positive rate (408 test off frames, τ = 0.5). Own implementation, same code
path as `diag_v1.py`; permutation p from 200 000 shuffles.

| ρ (prior ↔ off-arm FA) | s42 | s43 | s44 | model mean | p range |
|---|---|---|---|---|---|
| RGB | +0.800 | +0.915 | +0.829 | **+0.848** | 5.0e−6 … 3.5e−5 |
| Depth | +0.682 | +0.637 | +0.466 | +0.595 | 8.7e−4 … 4.0e−2 |
| B2 | +0.905 | +0.874 | +0.772 | +0.850 | 5.0e−6 … 1.5e−4 |

| statistic | v1 (15 cells, s42) | v2 | reading |
|---|---|---|---|
| ρ, RGB | **+0.9626** | **+0.848** | coupling survives, weaker by ~0.11 ρ |
| **FA ÷ prior, far row** | 0.377 (band 3) | **0.234** (3b) · 0.122 (3a) | **magnitude halved** |
| FA ÷ prior, band 2 | 0.243 | **0.062** | ~4× smaller |
| band-1 FA | 0.000 | **0.000** (all models, all seeds) | inert near band replicates at 20 cells |

Off-arm firing rate by band, 3-seed mean: RGB 0.136 / 0.041 / 0.010 / 0.000 and Depth
0.012 / 0.013 / 0.011 / 0.000 and B2 0.097 / 0.033 / 0.009 / 0.000 over bands 3b / 3a / 2 / 1.
Train prior by band (on-arm): 3b 0.583 · 3a 0.334 · 2 0.160 · 1 0.045 (the `config.json`
`train_positive_rate` bias vector is exactly half of this, being computed over both arms; ranks
identical). **Claim to publish: the far-band standing bias was reduced roughly two-fold, not removed.**

### N.5 Off-arm false alarms by scene (B2-iii) — the geography moved

3-seed mean, 408 test off frames, τ = 0.5.

| test off scene | n off | RGB frame FA [per seed] | RGB cell-fire share | Depth frame FA | Depth share | B2 frame FA | B2 share |
|---|---|---|---|---|---|---|---|
| `scene15` | 72 | **0.699 ± 0.194** [0.889/0.500/0.708] | **33.4 %** | 0.097 ± 0.104 | 17.7 % | 0.338 ± 0.486 | 17.4 % |
| `sceneN3` | 24 | 0.806 ± 0.146 | 20.9 % | 0.042 ± 0.062 | 2.8 % | 0.500 ± 0.354 | 17.8 % |
| `scene18` | 72 | 0.352 ± 0.236 | 16.2 % | **0.000** | 0.0 % | 0.037 ± 0.056 | 1.6 % |
| `scene05` | 72 | 0.389 ± 0.312 | 14.8 % | 0.028 ± 0.021 | 3.4 % | 0.356 ± 0.153 | 36.4 % |
| `scene14` | 72 | 0.269 ± 0.229 | 13.3 % | **0.000** | 0.0 % | 0.065 ± 0.062 | 3.6 % |
| `scene07` | 72 | 0.032 ± 0.049 | 1.0 % | **0.000** | 0.0 % | 0.250 ± 0.208 | 12.9 % |
| **`sceneC2`** | 24 | **0.069 ± 0.104** [0.208/0.000/0.000] | **0.5 %** | **0.292 ± 0.125** | **76.1 %** | 0.403 ± 0.271 | 10.3 % |
| **all off** | 408 | **0.359 ± 0.127** | — | **0.042 ± 0.029** | — | 0.238 ± 0.143 | — |
| *v1 anchor, s42, 168 off* | 168 | *0.2738* | — | *0.1607* | — | — | — |

v1 → v2 for RGB: `sceneC2` frame FA **0.875 → 0.069**, its share of cell fires **47.8 % → 0.5 %**,
fires per off frame 5.04 → 0.083 (60× lower), top-2 scene concentration 86.9 % → **54.3 %**, scenes
with zero fires 3 → 0, dominant source `sceneC2` → **`scene15`**. For Depth the concentration went the
other way: `sceneC2` 68.0 % → **76.1 %** of cell fires while overall frame FA fell 0.161 → 0.042.

**The FA rise is not a denominator effect.** RGB off-arm frame FA on the *identical* 168 main-round
off frames: 3-seed mean **0.387** [0.429 / 0.482 / 0.250] against v1 s42's 0.274 on the same frames;
the 240 new boost off frames are the quieter half (0.339). Depth: main 0.060 vs boost 0.029.
B2: main 0.331 vs boost 0.172. Caveat for all per-scene rows: 24–72 off frames of a single scene
(B2 on `scene15` reads 0.014 / 0.986 / 0.014 across seeds).

### N.6 τ sweep (B3) — the operating-point evidence

3-seed mean, test, frame metrics. Full grid τ = 0.05…0.95 step 0.05 in `tau_curves/tau_curves.csv`.

| model | argmax τ of (H − FA) | H / FA / H−FA there | H / FA / H−FA at τ = 0.5 | loss from using 0.5 | amplitude of H−FA over τ∈[0.30,0.70] | per-seed argmax |
|---|---|---|---|---|---|---|
| rgb | 0.35 | 0.809 / 0.464 / **+0.345** | 0.688 / 0.359 / +0.329 | **0.016** | 0.095 | 0.30 / **0.95** / 0.15 |
| depth | 0.15 | 0.667 / 0.184 / **+0.483** | 0.438 / 0.042 / +0.396 | 0.087 | 0.026 | **0.80** / 0.10 / 0.15 |
| b2 | 0.05 | 0.569 / 0.536 / **+0.033** | 0.229 / 0.238 / −0.009 | 0.042 | 0.013 | 0.20 / 0.60 / 0.05 |
| yolo s42 | 0.10 | 0.010 / 0.010 / +0.001 | (τ .25) 0.000 / 0.005 / −0.005 | 0.006 | — | — |

**The τ = 0.5 column reproduces `runs/v2/SEED_TABLE.md` §1 exactly** (same function, same dumps).
Per-seed operating points (the 9+1 scatter): rgb (FA, H) = (0.375, 0.594) / (0.478, 0.875) /
(0.223, 0.594); depth (0.052, 0.406) / (0.007, 0.469) / (0.066, 0.438); b2 (0.211, 0.083) /
(0.395, 0.396) / (0.108, 0.208); **YOLO s42 @ τ 0.25 = (0.005, 0.000)** with E recall 0.000 and
V 0.117 — the detector baseline sits on the origin, as `runs/yolo_s42/eval_test/metrics.json`
records. Decision recorded: **τ_op = 0.5 retained** (YOLO row 0.25). The argmax column is a
diagnostic of how much 0.5 costs, **not** a candidate list: it is fitted on test, and the per-seed
argmax does not reproduce.

Depth's curve is flat over τ ∈ [0.2, 0.7] (FA 0.164 → 0.017), i.e. its logits are near-saturated —
its low H recall is a model property, not a threshold choice. B2's H − FA never exceeds +0.033 at
**any** τ.

### N.7 Grid straddling and cell occupancy (B4)

Frame set = on-arm frames carrying ≥1 GT-positive cell (test 327 / corpus 1038).
Inputs: `dayrun_0820/annotations/labels_v1_full.json` + `runs/v2/rgb_s{42,43,44}/eval_test/per_frame.csv`.

**(i) Boundary crossing rates** (frame basis / unit basis, where a unit is a (frame, sector) pair for
a band boundary and a (frame, band) pair for a sector boundary):

| boundary | test frames | test rate | test unit basis | corpus rate | corpus unit basis |
|---|---|---|---|---|---|
| sector A/B | 249/327 | 76.1 % | 79.4 % | 67.6 % | 76.4 % |
| sector B/C | 276/327 | 84.4 % | 86.4 % | 80.9 % | 82.6 % |
| sector C/D | 258/327 | 78.9 % | 84.6 % | 82.4 % | 81.7 % |
| sector D/E | 225/327 | 68.8 % | 81.6 % | 66.2 % | 75.8 % |
| band 2 m (1/2) | 27/327 | 8.3 % | 31.0 % | 8.1 % | 29.6 % |
| band 5 m (2/3a) | 93/327 | 28.4 % | 43.0 % | 26.0 % | 44.2 % |
| **band 8 m (3a/3b)** | 213/327 | **65.1 %** | **63.8 %** | 55.8 % | 52.5 % |

Straddling frame (≥2 sectors or ≥2 bands): **306/327 = 93.6 %** test, 1005/1038 = 96.8 % corpus.
Median GT-positive cells per frame 8 (test) / 6 (corpus); median sectors spanned 5.
**Reconciliation with DAYRUN ②ⓒ's 62.7 %:** that value is the pre-augmentation labels
(`labels_v1.json`), train + eligible scenes, on-arm, (frame, sector) unit basis. The same file's full
on arm gives 66.3 %; the post-augmentation whole corpus gives 52.5 %. The metric did not change — the
corpus did (D21's boost added far E/H frames, many of them single-band 3b). **Quote exactly one of
these with its scope stated.**

**(ii) miss × straddle cross-tab, RGB v2, τ = 0.5** (miss = no GT-positive cell reaches p ≥ 0.5):

| seed | n | miss rate (straddling) | miss rate (flat) | diff [95 % CI, 10k bootstrap] |
|---|---|---|---|---|
| 42 | 327 | 0.275 | 0.190 | +0.084 [−0.105, +0.249] |
| 43 | 327 | 0.072 | 0.381 | **−0.309 [−0.526, −0.102]** |
| 44 | 327 | 0.441 | 0.571 | −0.130 [−0.351, +0.100] |
| pooled (not independent) | 981 | 0.263 | 0.381 | −0.118 [−0.240, +0.005] |

8 m boundary only: diff −0.354 [−0.456, −0.252] (s42) · −0.088 [−0.163, −0.015] (s43) ·
−0.091 [−0.203, +0.023] (s44). H-tier subtable: +0.083 / −0.238 / −0.393 [−0.648, −0.102].
**Verdict: no seed shows straddling significantly increasing misses.** The flat stratum is only
21/327 frames (6.4 %), so this is "no evidence of harm", not "evidence of benefit".

**(iii) Occupancy and over-blocking of GT-positive cells.** Occupancy = the label's 5 cm
height-map-difference footprint samples in the cell ÷ the wedge's analytic capacity
`N(band) = 0.5·dθ·(r_out² − r_in²)/step²`, dθ = 12.44°, step = 0.05 m (N = 173.7 / 911.9 / 1693.5 /
3473.9). Estimator validated by the corpus maximum observed ratio, 1.0018–1.0121 (clipped to 1.0).

| band | n GT+ cells (test) | occ Q1 | **occ median** | occ Q3 | **over-blocking median** | corpus occ median | corpus over-block median |
|---|---|---|---|---|---|---|---|
| 1 `[0,2)` | 117 | 0.115 | **0.288** | 0.472 | **0.712** | 0.121 | 0.879 |
| 2 `[2,5)` | 378 | 0.172 | **0.655** | 0.992 | **0.345** | 0.625 | 0.375 |
| 3a `[5,8)` | 870 | 0.158 | **0.610** | 0.993 | **0.390** | 0.521 | 0.479 |
| 3b `[8,12)` | 1326 | 0.306 | **0.861** | 0.999 | **0.139** | 0.693 | 0.307 |
| all | 2691 | 0.204 | **0.726** | 0.998 | **0.274** | — | — |

Distribution is bimodal (Q3 ≥ 0.99 in bands 2/3a/3b, Q1 0.16–0.31) — do not summarise by the median
alone. Forward-looking figure for the hole probe: a 0.5 × 0.5 m hole is ~100 of 3474 samples, i.e.
**1–3 % occupancy of an `[8,12)` m cell**.

### N.8 Final-val cell coverage (B6) — the §5.3-of-`P1_GRID_V1` flag is cleared

Final val = `scene08` · `scene20` · `sceneD3`, 288 frames (on 144 / off 144, 90 hazard frames).
Positive frames per cell from `_v2_full` `polar_gt` (gated and pre-gate identical; 0 cells withheld):

| cell | A | B | C | D | E | band total |
|---|---|---|---|---|---|---|
| band 1 `[0,2)` | **6** | 9 | 9 | 12 | 9 | 45 (6.6 %) |
| band 2 `[2,5)` | 21 | 24 | 24 | 27 | 21 | 117 (17.1 %) |
| band 3a `[5,8)` | 33 | 36 | 39 | 33 | 33 | 174 (25.4 %) |
| band 3b `[8,12)` | 60 | 72 | 78 | 78 | 60 | 348 (50.9 %) |

**All 20 cells carry ≥6 positive frames — the "val cell 1A has no positives" flag is cleared** (it was
measured on the *old* val: scene10 · 17 · D3). Two dependencies to record: `scene08` alone supplies
the entire band-1 row, and **new caveat on the D19 selector** — 50.9 % of val positives sit in band 3b,
band 1 holds 6.6 %, and val contains only **6 H frames of 90 hazard frames (6.7 %, + 3 H_weak)**
against test's 96/327 (29.4 %). The val cell-F1 selector therefore weights the paper's most important
axis (H tier) and its weakest band almost not at all; checkpoint and τ* selection are effectively
decided by far-range V-tier performance. Changing the selector requires retraining and is **not**
recommended inside the 8/24 freeze — carried as a caveat, not an action.

### N.9 What is prepared but not measured (so no number here is missing by accident)

| item | state | expected cost when the GPU frees |
|---|---|---|
| YOLO s43 / s44 (3-seed row 4) | prepared, not run — `runs/yolo_s42/eval_test/metrics.json` remains the only seed | ~70 min |
| aux pixel-loss run + paired ablation | prepared, dry-run clean | ~25 min |
| C2/N3 appearance-preserving off arm | scene patch + hash/pose gate + rehearsal done. Reference old-off rows recomputed from frozen predictions (s42, τ 0.5): `sceneC2` FA_frame 0.208, cells/frame 0.25, mean max p 0.228, twin Δ_frame 0.476, Δ_score 0.481; `sceneN3` FA_frame 1.000, cells/frame 5.00, mean max p 0.915, Δ_frame 0.031, Δ_score n/a (no GT-positive cell) | ~15 min (render 6–8 min) |
| hole zero-shot probe (3 scenes, 144 frames, 9 frozen checkpoints) | CPU gate all-pass, evaluation-only by construction | render 12–20 min + eval 5–10 min GPU (or ~15 min CPU) |
