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

---

## Resume chain 0821

*Appended 2026-08-21 (GPU freed 11:46, chain A1 → A2 → C2 → C1 complete). **Append only — §1–§13
and the `Night 0820→0821 update` section above are unmodified.** This section supersedes **N.9**,
which listed these four items as prepared-not-measured; every row of N.9 is now closed here.
Denominators unchanged from the night section: v2 test = 816 frames = 408 on (V 180 · E 45 · H 96 ·
H_weak 6 · none_in_fov 81) + 408 off, grid `PROVISIONAL-GRID-V1` (5 sectors × 4 bands
[0,2)/[2,5)/[5,8)/[8,12) m). **These are new measurements, not re-analysis.***

### R.1 YOLOv8n detector baseline, 3 seeds (A1) — main-table row 4

Source `experiments/dayrun_0820/runs/yolo_s{42,43,44}/eval_test/metrics.json`, block `point.op`.
τ = **0.25** for this row only (approval item #1: τ_op 0.5 for U-Net rows, 0.25 for the detector row).
`tau_star` = `tau_op` = 0.25 in all three files; `tau_star_val_f1` is null (not fitted).
Mapping rule `experiments/dayrun_0820/code/yolo/det2cell.py`, documented in
`experiments/dayrun_0820/METRICS_NOTES_yolo.md`.

| metric | s42 | s43 | s44 | mean | ±range/2 | sd |
|---|---|---|---|---|---|---|
| frame_recall_V | 0.1167 | 0.1611 | 0.1722 | **0.1500** | 0.0278 | 0.0294 |
| **frame_recall_E** | **0.0000** | **0.0000** | **0.0000** | **0.0000** | 0.0000 | 0.0000 |
| **frame_recall_H** | **0.0000** | **0.0000** | **0.0000** | **0.0000** | 0.0000 | 0.0000 |
| frame_det_rate | 0.0642 | 0.0887 | 0.0948 | 0.0826 | 0.0153 | 0.0162 |
| frame_fa_off | 0.0049 | 0.0245 | 0.0417 | 0.0237 | 0.0184 | 0.0184 |
| cell_f1 | 0.0248 | 0.0293 | 0.0252 | 0.0264 | 0.0023 | 0.0025 |
| cell_recall | 0.0126 | 0.0152 | 0.0130 | 0.0136 | 0.0013 | 0.0014 |
| cell_precision | 0.6071 | 0.3868 | 0.4217 | 0.4719 | 0.1102 | 0.1184 |
| cell_fpr_off | 0.00037 | 0.00159 | 0.00245 | 0.00147 | 0.00104 | 0.00105 |
| cell_fpr_on_neg | 0.00347 | 0.00951 | 0.00512 | 0.00603 | 0.00302 | 0.00311 |
| **cell_recall_V** | 0.0182 | 0.0220 | 0.0188 | 0.0196 | 0.0019 | 0.0020 |
| **cell_recall_E** | **0.0000** | **0.0000** | **0.0000** | **0.0000** | 0.0000 | 0.0000 |
| **cell_recall_H** | **0.0000** | **0.0000** | **0.0000** | **0.0000** | 0.0000 | 0.0000 |
| band1_cell_recall | 0.1026 | 0.1624 | 0.1026 | 0.1225 | 0.0299 | 0.0345 |
| band2_cell_recall | 0.0476 | 0.0582 | 0.0608 | 0.0556 | 0.0066 | 0.0070 |
| band3_cell_recall | 0.0023 | 0.0000 | 0.0000 | 0.0008 | 0.0011 | 0.0013 |
| band4_cell_recall | 0.0015 | 0.0000 | 0.0000 | 0.0005 | 0.0008 | 0.0009 |
| band1_cell_fpr_off | 0.00049 | 0.00441 | 0.00735 | 0.00408 | 0.00343 | 0.00344 |
| band2_cell_fpr_off | 0.00098 | 0.00196 | 0.00245 | 0.00180 | 0.00074 | 0.00075 |
| band3_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| band4_cell_fpr_off | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

`mean ± range/2` is the convention of `SEED_TABLE.md` §1 and is what the table row quotes; the sample
sd is given so either can be cited without recomputation. For the headline V figure the two agree to
two decimals (0.028 vs 0.029).

**D22 ceiling — confirmed, zero leak.** E and H recall are identically 0 on all three seeds at both
frame and cell level. This is the constructive bound of the `det2cell` rule (a box over hazard pixels
cannot exist for a hazard with no visible pixels), measured before training by the oracle-box
diagnostic in `METRICS_NOTES_yolo.md` §3. Nonzero here = mapping leak; the alarm did not fire on any
seed.

**Sub-operating-threshold exception (footnote-level).** From the `sweep` blocks, at τ = 0.10 —
*below* the operating point — s42 and s44 each show `frame_recall_H` = 0.010417 (= 1 hazard frame of
96) with `cell_recall_H` 0.00212 and 0.00637 respectively; s43 stays at 0.000. At τ = 0.25, 0.50 and
above, all three are exactly 0. Attribution: a single low-confidence box landing in a near band via
the mapping's documented near-band bias (`METRICS_NOTES_yolo.md` §2), not H-tier detection.

**Band shape.** All detector recall is near-band: band 1 0.1225, band 2 0.0556, bands 3a/3b ≈ 0.
Off-arm cell FPR is likewise confined to bands 1–2 (bands 3a/3b exactly 0 on every seed).

### R.2 Auxiliary pixel-loss ablation, rgb s42 (A2) — appendix, NOT main table

Arm `experiments/dayrun_0820/runs/v2/rgb_s42_aux/eval_test/metrics.json` · paired comparison
`experiments/dayrun_0820/runs/v2/compare_aux_vs_base_s42/METRICS_SECTION.md` §3.
816 common frames, paired percentile bootstrap 10000×, seed 42, threshold 0.5, A = aux, B = base
`rgb_s42`. Config delta is a single variable: `aux_enabled=True`, `aux_lambda=0.5`, 648 amodal masks
(`experiments/dayrun_0820/annotations/amodal`); encoder `resnet34-unet-aux` 24.447 M, selector
`0.5*val_f1 + 0.5*val_h_frame_recall`, `oversample_h` 4.0, `aug` off, `hflip` on — all identical to
base. `tau_star` 0.43 (fitted on val) but the comparison and both point tables use τ = 0.5.

| metric | aux (A) | base (B) | A−B [95 % CI] | CI ∌ 0 |
|---|---|---|---|---|
| cell_f1 | 0.5255 | 0.4852 | **+0.0403** [0.0001, 0.0786] | yes (lower bound 1e-4) |
| cell_recall | 0.4274 | 0.4322 | −0.0048 [−0.0488, 0.0377] | no |
| cell_precision | 0.6821 | 0.5530 | **+0.1291** [0.0885, 0.1690] | yes |
| frame_det_rate | 0.5627 | 0.7309 | **−0.1682** [−0.2296, −0.1064] | yes |
| frame_recall_V | 0.6389 | 0.8278 | **−0.1889** [−0.2551, −0.1257] | yes |
| frame_recall_E | 0.0000 | 0.6000 | **−0.6000** [−0.7436, −0.4528] | yes |
| **frame_recall_H** | 0.7188 | 0.5938 | +0.1250 [**−0.0096**, 0.2526] | **no** |
| cell_recall_V | 0.4630 | 0.4893 | −0.0263 [−0.0758, 0.0205] | no |
| cell_recall_E | 0.0000 | 0.3592 | **−0.3592** [−0.4556, −0.2626] | yes |
| **cell_recall_H** | 0.6072 | 0.2527 | **+0.3546** [0.2768, 0.4302] | yes |
| band1_cell_recall | 0.0000 | 0.0000 | 0.0000 [0.0000, 0.0000] | no |
| band2_cell_recall | 0.3810 | 0.3360 | +0.0450 [−0.0129, 0.1066] | no |
| band3_cell_recall | 0.3793 | 0.4103 | −0.0310 [−0.0984, 0.0336] | no |
| band4_cell_recall | 0.5098 | 0.5121 | −0.0023 [−0.0577, 0.0517] | no |
| band2_cell_fpr_off | 0.0010 | 0.0088 | −0.0078 [−0.0154, −0.0019] | yes |
| band3_cell_fpr_off | 0.0221 | 0.0662 | **−0.0441** [−0.0591, −0.0301] | yes |
| band4_cell_fpr_off | 0.0691 | 0.1358 | **−0.0667** [−0.0867, −0.0467] | yes |
| frame_fa_off | 0.1667 | 0.3750 | **−0.2083** [−0.2531, −0.1646] | yes |
| cell_fpr_off | 0.0230 | 0.0527 | **−0.0297** [−0.0372, −0.0222] | yes |
| cell_fpr_on_neg | 0.0636 | 0.0933 | −0.0296 [−0.0450, −0.0142] | yes |

Aux-arm bootstrap CIs at its own operating point (from `rgb_s42_aux/eval_test/METRICS_SECTION.md`
§1a): frame recall V 0.6389 [0.5684, 0.7090] · E 0.0000 [0.0000, 0.0000] · H 0.7188 [0.6279, 0.8081] ·
frame det rate 0.5627 [0.5093, 0.6172] · frame FA off 0.1667 [0.1311, 0.2028] · cell FPR off
0.0230 [0.0167, 0.0300] · cell F1 0.5255 [0.4755, 0.5717].

**Twin evidence (independent of the paired table).** `rgb_s42_aux/twin/twin_analysis.md`: 408 pairs,
366 pose-matched (42 excluded, tol 0.15), 312 carrying ≥1 GT cell, delta_score > 0 in 284/312.
Δ_score by tier — V 0.4927 [0.4302, 0.5528]\* · E 0.0337 [0.0119, 0.0611]\* · **H 0.3256 [0.2701,
0.3826]\*** · all 0.3675 [0.3261, 0.4087]\*. Against base `rgb_s42` (twin all 0.310, twin H 0.170,
`SEED_TABLE.md` §3) the **H-tier twin Δ nearly doubles, 0.170 → 0.326**.

**Caveats attached to every citation of this block.** (i) The frame-level H gain +0.1250 has a CI
containing zero — quote the cell-level +0.3546 or nothing. (ii) n = 1 seed, against a base RGB
3-seed H spread of ±0.141 (`SEED_TABLE.md` §1), so the frame-level move is inside seed noise.
(iii) Position is appendix / development narrative; the main table stays at four rows (approval #2).

### R.3 Dressing-preserving off-arm control, sceneC2 + sceneN3 (C2)

Source `experiments/nightrun_0820/ctrl_dressing/CTRL_TABLE.md` (+ `ctrl_numbers.json`).
τ = 0.5, RGB recipe-v2 checkpoints, seeds 42/43/44. **old off** = `dataset/260819_main_off` (toggle
also deleted the leaf mound, the railing, and in N3 the mural) · **new off** =
`dataset/260820_ctrloff` (`keep_dressing`: hazard geometry only). Both pair against the **same** on
arm `dataset/260819_main_on`. Every off frame carries all-zero GT, so `FA_frame` is a pure
false-alarm rate. 24 frames per scene-arm; pairs kept 24/24 in every cell of the table.

**Twin Δ_frame (pose-matched, tol 0.15 m):**

| scene | arm | s42 | s43 | s44 | mean ±half-range | Δ_score mean |
|---|---|---|---|---|---|---|
| sceneC2 | **old off** | 0.476 | 0.738 | 0.884 | **0.699 ±0.204** | 0.688 ±0.178 |
| sceneC2 | **new off** | 0.185 | 0.214 | 0.090 | **0.163 ±0.062** | 0.151 ±0.060 |
| sceneN3 | old off | 0.031 | 0.098 | 0.052 | 0.060 ±0.033 | n/a (no GT-positive cell on on-arm) |
| sceneN3 | **new off** | 0.000 | −0.001 | −0.002 | **−0.001 ±0.001** | n/a |

**Decomposition.** (0.699 − 0.163) / 0.699 = **0.767** → **≈77 % of the old sceneC2 delta was the
removed dressing, ≈23 % (0.163) is the hazard geometry itself.** The residual is same-signed on all
three seeds.

**Off-arm firing (pure false alarms, all-zero GT):**

| scene | arm | s42 | s43 | s44 | FA_frame mean ±half-range | cells/frame | mean max p |
|---|---|---|---|---|---|---|---|
| sceneC2 | old off | 0.208 | 0.000 | 0.000 | 0.069 ±0.104 | 0.08 ±0.12 | 0.115 ±0.110 |
| sceneC2 | **new off** | 0.500 | 0.625 | 0.917 | **0.681 ±0.208** | 2.11 ±0.33 | 0.651 ±0.142 |
| sceneN3 | old off | 1.000 | 0.708 | 0.708 | 0.806 ±0.146 | 2.97 ±1.90 | 0.750 ±0.133 |
| sceneN3 | new off | 1.000 | 0.917 | 0.750 | 0.889 ±0.125 | 4.01 ±2.42 | 0.811 ±0.103 |

Reading per `CTRL_TABLE.md` §4: `FA_frame(new) > FA_frame(old)` = **the dressing is what the model
fires on**. With dressing present and hazard absent the model fires on 68 % of safe frames at mean
max p 0.651 — cue-consistent, and a shortcut. Limitations section, not results.

**sceneN3 null control.** Its dressing is a wall mural (1–2 mm of paint on flat floor), so the
`keep_dressing` off arm is structurally the on arm — heightmap gate: `max |new−on| = 0.000000 m`,
NaN pattern equal. Expected twin Δ ≈ 0; measured **−0.001 ±0.001**. The apparatus contributes no
delta of its own.

**Pairing QC.** Shared on-arm rows 48 per seed; `max |dp|` between the new evaluation and the frozen
one = **0.00e+00 on all three seeds** (threshold for voiding the comparison is ~1e-5). Both off arms
therefore see byte-identical on-arm predictions.

**Relation to the headline.** This corrects the **all-tier** twin Δ only. `sceneC2` contributes zero
H-tier pose-matched pairs (§7.1 and N.1 above), so the §5.3 headline H claim is untouched — N.1
already showed the H-tier Δ unchanged to four decimals under exact-pose-only stratification.

**Gate history (method note, and a corrected number).** The first gate pass returned **24 PASS /
1 FAIL of 25** and evaluation was correctly refused (`logs/eval.log:32–35`, brief §4 C2 "게이트 통과
후에만 평가"). The failing check was *"C2 rest of x<0 differs only in the coping band"*: 39 cells
outside the declared coping band differed, e.g. x = −0.45, y = −1.60, +0.23765 → +0.13000. Adjudication
found the cause to be the **gate's own mask**, not the scene: the removed coping is a rotated box, and
the check bounded it by an axis-aligned box, so the AABB overhang put genuinely-coping cells outside
the band the check would accept. Evidence that no scene, pose or appearance property changed: the
**camera datum strip** (x<0, |y| ≤ 0.9 — the only region `AabbPrefilter.ground_z(-d, y)` ever samples)
was `max |new−on| = 0.000000 m over 1440 cells` **in the failing pass as well as the passing one**,
and `sceneC2`/`sceneN3` cam dicts were byte-equal on all 24/24 cuts in both. Mound-B footprint
likewise 0.000000 m over 1326 cells. The mask was corrected to the rotated extent and the gate
returned **25 checks · 0 FAIL · 0 WARN** (`logs/eval.log:67–69`), with the same check now reporting
117 differing cells all inside `1.28 ≤ |y| ≤ 1.62 & x ≥ −0.48419`. **No pixel was re-rendered between
the two gate passes**; the numbers in the tables above come from the single render that both passes
examined.

### R.4 Hole-type zero-shot probe, 3 scenes × 144 frames × 9 checkpoints (C1)

Sources `experiments/probe_holes_0820/PROBE_TABLE.md` (+ `PROBE_TABLE.json`) and `TIER_TABLE.md`.
Manifest `dataset_manifest_probe.json`, rounds `260821_probe_on` / `260821_probe_off`, 144 frames
(3 scenes × 24 on + 24 off), grid `PROVISIONAL-GRID-V1`, checkpoints = the nine frozen recipe-v2 runs
under `experiments/dayrun_0820/runs/v2`. **τ = 0.5, frozen by absolute rule 3 and NOT refitted**
(`val` deliberately empty in `split_probe.json`). **Evaluation only — no probe frame may ever enter
training** (brief §4 C1).

**Tier design landed as specified** (`TIER_TABLE.md`, per scene-arm, on rows, 24 frames each):

| scene | GT-positive | V | E | H | design intent | met |
|---|---|---|---|---|---|---|
| probeH1 | 24 | **15** | 3 | 6 | V-dominant | yes |
| probeH2 | 24 | 0 | **24** | 0 | pure E | yes (24/24) |
| probeH3 | 24 | 0 | 0 | **24** | pure H | yes (24/24) |

Off arms: 24 frames each, 0 GT-positive, all "other". Every on-row GT-positive count equals the frame
count, so no cut put the hole outside the 12 m grid.

**Per-scene frame recall and off-arm FA @ τ = 0.5:**

| ckpt | H1 recall | H1 FA | H2 recall (pure E) | H2 FA | **H3 recall (pure H)** | **H3 FA** |
|---|---|---|---|---|---|---|
| rgb_s42 | 0.083 | 0.000 | 0.000 | 0.000 | **0.083** | 0.167 |
| rgb_s43 | 0.125 | 0.000 | 0.000 | 0.000 | **0.292** | 0.542 |
| rgb_s44 | 0.000 | 0.000 | 0.000 | 0.000 | **0.125** | 0.250 |
| depth_s42 | 0.125 | 0.125 | 0.125 | 0.375 | **0.500** | 0.500 |
| depth_s43 | 0.000 | 0.125 | 0.000 | 0.000 | **0.625** | 0.625 |
| depth_s44 | 0.000 | 0.000 | 0.000 | 0.000 | **0.375** | 0.500 |
| b2_s42 | 0.000 | 0.000 | 0.000 | 0.042 | 0.250 | 0.333 |
| **b2_s43** | **1.000** | **0.917** | 0.167 | 0.750 | 0.625 | 0.750 |
| b2_s44 | 0.000 | 0.000 | 0.000 | 0.000 | 0.250 | 0.250 |

*(PROBE_TABLE §2 also reports rgb H3 recall as 0.083 / 0.292 / 0.125; the headline §1 table gives
rgb_s44 H-tier recall 0.100 because §1 pools all H-tier frames across the three scenes — 30 H frames
= 24 from H3 + 6 from H1 — rather than the 24 of H3 alone. Both are correct; state which denominator
is in use. The pooled §1 H figures are rgb 0.067 / 0.233 / 0.100, depth 0.400 / 0.500 / 0.300,
b2 0.200 / 0.700 / 0.200.)*

**The split.** Pure-H (probeH3) recall: **RGB 0.083 / 0.292 / 0.125, Depth 0.500 / 0.625 / 0.375** —
Depth roughly triples RGB. This **inverts the main table**, where RGB leads Depth on the H tier
(0.688 ± 0.141 vs 0.438 ± 0.031, §4 / `SEED_TABLE.md` §1). Pure-E (probeH2) recall collapses for both
(RGB 0.000 on all seeds; Depth 0.125 / 0.000 / 0.000).

**probeH2 adjacent hazard-free sector metric — COMPUTED**, `PROBE_TABLE.md` §3. Definition: the
hazard sits in one lateral sector; `adjacent` = one sector away in the same band, `far` = two or more.

| ckpt | adj cells | adj fired | adj cell rate | adj frame rate | far cell rate |
|---|---|---|---|---|---|
| rgb_s42 / rgb_s43 / rgb_s44 | 48 | 0 | 0.000 | 0.000 | 0.000 |
| depth_s43 / depth_s44 | 48 | 0 | 0.000 | 0.000 | 0.000 |
| b2_s42 / b2_s44 | 48 | 0 | 0.000 | 0.000 | 0.000 |
| **depth_s42** | 48 | 6 | **0.125** | 0.250 | **0.000** |
| **b2_s43** | 48 | 9 | **0.188** | 0.375 | 0.045 |

Seven of nine fire on zero adjacent cells. `depth_s42` = clean angular blur (adjacent 0.125 against a
far rate of exactly 0.000). `b2_s43` = nonzero far rate too, consistent with the outlier reading below.

**Outlier flag — `b2_s43`.** Frame recall 1.000 on probeH1 with off-arm **FA 0.917** on the same
scene, 0.750 on both others, headline cell FPR 0.240 and frame FA 0.806. Its sibling seeds score
0.000 recall / 0.000 FA on probeH1. This is a firing-rate artefact, not detection. **Do not average
B2 probe numbers over seeds; always show FA beside recall.** More generally, across the probe FA
tracks recall (Depth H3: recall 0.500/0.625/0.375 against FA 0.500/0.625/0.500), so the probe
evidences transfer of a *firing tendency* at least as much as transfer of discrimination.

**Twin analysis** ran at the DEFAULT pose tolerance `--tol 1e-6` (not the D20 0.15 m rescue), per
`PROBE_TABLE.md` §4; per-checkpoint files at `experiments/probe_holes_0820/eval/<ckpt>/twin/twin_analysis.md`.

**Fix history (method notes — three bugs between first launch and the numbers above).**
1. **Illegal prim name → silent empty `SdfPath`.** `probe_common.build_kerb_line` composed prim paths
   as `f"{root}/Kerb_{int(round(y*100))}"`; at y = −3.60 this yields `Kerb_-360`, and a leading dash
   is not a valid USD identifier. `SdfPath.AppendChild` **warns and returns an empty path** rather
   than raising (`logs/probe.log:597`, "Invalid prim name 'Kerb_-360'"), so the failure surfaced one
   call later as `UsdGeom.Cube.Define(stage, <>)` → `Tf.ErrorException: Path must be an absolute
   path: <>` (`logs/probe.log:599–625`). Every render died; **all three scenes × both arms produced 0
   cuts.** Only reachable after Isaac boot, which is why the pre-boot CPU gate (47/47 PASS, D29) and
   the `NEGOBS_SMOKE=1` gate (6/6) both missed it.
2. **Poisoned resume — Isaac exits 0 on scene failure.** Because the failing invocations still exited
   0, the driver marked conditions done and the resume path would have *skipped* the empty work
   (`logs/probe.log:3279–3280`: "0 cuts on disk across 3 scene dir(s) … this is NOT a checker
   finding"). Fixed with a de-poison pass that withdraws `done_conds` from any zero-cut scene before
   retrying (`logs/probe.log:3296`: withdrew L0/L5/L7 from all three scenes). Without it the chain
   would have reported "resumed successfully" over an empty dataset.
3. **Checker crash on the empty run.** The post-render checker assumed ≥1 cut and crashed instead of
   reporting; it now emits the explicit zero-cut diagnostic quoted above, which is what pointed at the
   render traceback rather than at itself.
   After the fixes, a 1-scene GPU smoke verified a fit of −0.600 before the full probe, which then ran
   clean: probeH1 on/off 24 cuts each at 3.672 / 3.852 s per cut, probeH2 3.698 / 3.578, probeH3
   3.425 / 3.599 — **72 cuts per arm, 259.0 s and 264.8 s wall including 3 boots each**
   (`logs/probe.log:4836–7354`).

### R.5 N.9 closure

| N.9 item | state now | where |
|---|---|---|
| YOLO s43 / s44 (3-seed row 4) | **measured** — row 4 final, E/H ceiling confirmed 3/3 | R.1 |
| aux pixel-loss run + paired ablation | **measured** — appendix row, 1 seed | R.2 |
| C2/N3 appearance-preserving off arm | **measured** — 3 RGB seeds, gate 25/25 | R.3 |
| hole zero-shot probe | **measured** — 144 frames × 9 checkpoints | R.4 |

Still open (optional, not blocking): **Depth-arm C2 control evaluation.** D28 justifies it
(`sceneC2` is 76.1 % of Depth's off-arm cell fires) and the recommendation in the morning report was
RGB 3 seeds + Depth 3 seeds; only the RGB 3 seeds were run in this chain. The rendered
`260820_ctrloff` round is reusable as-is, so the outstanding cost is checkpoint inference only.
The RGB result stands without it.

---

## RED-TEAM RESPONSE 0823 (appended 2026-08-23 — D35)

Everything in this block is **new measurement on frozen artefacts**: no re-training, no re-render, no GPU, and **no number above this line is edited**.  Where a figure here contradicts one above, the correction is stated explicitly and the older text is left in place as the record.  Source scripts and full tables: `experiments/weekend_0823/rt_response/` (`code/*.py`, `F*.md`, `*.json`).  Consolidated finding→response→residual-risk ledger: `experiments/weekend_0823/redteam/REDTEAM_0823.md`.


### RT.1 FA-matched tier recall (R1-F1) — the H column of §4 is read at two different operating points

§4 prints RGB's H recall at an off-arm frame FA of 0.359 and Depth's at 0.042 in the same column — an 8.6× difference in false-alarm rate.  Sweeping τ per run so the off-arm FA hits a common target and reading tier recall there (`rt_response/code/f1_fa_matched.py`, τ from the empirical order statistics of the off-arm per-frame max probability, FA resolution 1/408 = 0.0025):

**H frame recall at matched off-arm FA, 3-seed mean ± half-range** (n = 96 H, 408 off)

| matched FA | RGB | Depth | B2 | Δ (Depth − RGB) |
|---|---|---|---|---|
| 0.359 | 0.729 ± 0.135 | **0.781 ± 0.078** | 0.399 ± 0.078 | +0.052 |
| 0.200 | 0.483 ± 0.172 | **0.562 ± 0.031** | 0.198 ± 0.141 | +0.080 |
| 0.100 | 0.326 ± 0.229 | **0.510 ± 0.078** | 0.097 ± 0.099 | +0.184 |
| 0.050 | 0.243 ± 0.208 | **0.479 ± 0.094** | 0.031 ± 0.036 | +0.236 |

Same sweep, V and E:

| matched FA | RGB V | Depth V | B2 V | RGB E | Depth E | B2 E |
|---|---|---|---|---|---|---|
| 0.359 | 0.809 | 0.994 | 0.800 | 0.570 | 0.733 | 0.193 |
| 0.200 | 0.669 | 0.983 | 0.746 | 0.296 | 0.600 | 0.126 |
| 0.100 | 0.530 | 0.956 | 0.646 | 0.081 | 0.600 | 0.089 |
| 0.050 | 0.443 | 0.939 | 0.552 | 0.015 | 0.600 | 0.022 |

**Reading.** Depth ≥ RGB at every matched point, and the gap widens as FA is tightened (+0.052 at FA 0.359 → +0.236 at FA 0.05).  The H-column ordering printed in §4 is an operating-point artefact, not an effect.  **What survives is the weaker and still useful claim: RGB is not zero** — 0.326 ± 0.229 at FA 0.10, against a twin-conditional adapter-free detector rate of 0.038 on the same tier (RT.3).  Per-seed τ and per-tier values: `rt_response/F1_FA_MATCHED.md`.  Full recall–FA curves for all three arms and all three seeds: `rt_response/figs/fig_f1_recall_vs_fa.png`.


### RT.2 Twin-conditional recall (R2 §4.3-F2) — separating conditional from unconditional firing

The twin is this corpus's intervention device; applying it to recall itself costs no extra render and no extra inference.  A hazard-ON frame is a **twin-conditional hit** iff `max_on_gt ≥ τ` **and** `max_off_gt < τ` on the pose-exact twin of the same cut (τ = 0.5, KEPT pairs, `rt_response/code/f2_twin_conditional.py`).


**H tier** (n = 96 kept pairs)

| model | recall as published | **twin-conditional recall** | off-arm twin fire rate | share of fires that are unconditional |
|---|---|---|---|---|
| rgb | 0.688 ± 0.141 | **0.375 ± 0.115** (0.229/0.438/0.458) | 0.330 | 0.447 |
| depth | 0.438 ± 0.031 | **0.438 ± 0.031** (0.406/0.469/0.438) | 0.000 | 0.000 |
| b2 | 0.229 ± 0.156 | **0.122 ± 0.068** (0.073/0.083/0.208) | 0.118 | 0.305 |

**E tier** (n = 45 kept pairs)

| model | recall as published | **twin-conditional recall** | off-arm twin fire rate | share of fires that are unconditional |
|---|---|---|---|---|
| rgb | 0.556 ± 0.378 | **0.207 ± 0.111** (0.222/0.311/0.089) | 0.370 | 0.572 |
| depth | 0.600 ± 0.000 | **0.600 ± 0.000** (0.600/0.600/0.600) | 0.000 | 0.000 |
| b2 | 0.178 ± 0.267 | **0.133 ± 0.200** (0.000/0.400/0.000) | 0.059 | 0.250 |

**V tier** (n = 165 kept pairs)

| model | recall as published | **twin-conditional recall** | off-arm twin fire rate | share of fires that are unconditional |
|---|---|---|---|---|
| rgb | 0.820 ± 0.136 | **0.440 ± 0.055** (0.479/0.370/0.473) | 0.382 | 0.446 |
| depth | 0.927 ± 0.036 | **0.873 ± 0.045** (0.891/0.909/0.818) | 0.055 | 0.059 |
| b2 | 0.711 ± 0.115 | **0.410 ± 0.073** (0.345/0.491/0.394) | 0.303 | 0.422 |

**Reading.** **Depth's H response is entirely hazard-conditional** — 0 of 96 pairs fire on the hazard-deleted twin, on all three seeds, so its twin-conditional recall equals its published recall exactly.  **RGB's does not**: 44.7 % of its H fires also fire when the hazard is gone, and its H recall falls 0.688 → 0.375.  The two arms were not counting the same thing.  Per-run and per-scene decomposition: `rt_response/F2_TWIN_CONDITIONAL.md`.


### RT.3 Adapter-free detector metric (R1-F3) — correcting the scope of the R.1 "constructive zero"

R.1 reads the YOLO row's E/H = 0.000 as a bound on *the detection paradigm*.  `METRICS_NOTES_yolo.md` §0 already says the opposite — *"every property of that adapter is a property of the adapter"* — and §3 proves it: the amodal GT boxes injected as conf-1.0 detections also score E = H = 0.000 **before any training**.  The bound as printed is therefore a bound on `det2cell`, not on detectors.

This section removes the adapter.  A hazard-ON frame is an **image-space hit** iff some stored detection (conf ≥ τ_conf) has IoU > t with some amodal GT box of that frame — no grid, no ground projection (`rt_response/code/f3_adapter_free_yolo.py`, 3 seeds).

| tier | n | any detection | **IoU > 0** | IoU > 0.1 | IoU > 0.3 | mean best IoU | mean largest GT box area |
|---|---|---|---|---|---|---|---|
| V | 180 | 0.393 ± 0.103 | **0.378 ± 0.086** | 0.356 | 0.317 | 0.239 | 0.434 |
| E | 45 | 0.259 ± 0.233 | **0.259 ± 0.233** | 0.259 | 0.259 | 0.182 | 0.585 |
| H | 96 | 0.167 ± 0.094 | **0.066 ± 0.036** | 0.052 | 0.031 | 0.016 | 0.193 |
| H_weak | 6 | 0.167 ± 0.250 | **0.167 ± 0.250** | 0.000 | 0.000 | 0.003 | 0.024 |
| none_in_fov | 81 | 0.214 ± 0.136 | **0.012 ± 0.012** | 0.008 | 0.000 | 0.002 | 0.145 |

τ_conf = 0.25, the adapter's operating point.  **The H rate is not zero.**  The bound is recovered only by adding the hazard-blind control: score the **off twin's** detections against the **on** frame's amodal GT boxes (same scene, same cut, same dressing, hazard geometry deleted).

| tier | n | on-arm IoU>0 | off-twin IoU>0 (hazard-blind) | on − off | **twin-conditional IoU>0** |
|---|---|---|---|---|---|
| *τ_conf = 0.25* | | | | | |
| V | 180 | 0.378 | 0.041 | +0.337 | **0.346 ± 0.064** |
| E | 45 | 0.259 | 0.148 | +0.111 | **0.170 ± 0.156** |
| H | 96 | 0.066 | 0.076 | -0.010 | **0.038 ± 0.010** |
| *τ_conf = 0.05* | | | | | |
| V | 180 | 0.615 | 0.156 | +0.459 | **0.487 ± 0.008** |
| E | 45 | 0.593 | 0.422 | +0.170 | **0.311 ± 0.022** |
| H | 96 | 0.302 | 0.233 | +0.069 | **0.142 ± 0.062** |

**Reading, and the sentence R.1 must be replaced by.** Two bounds apply to row 4 and they must not be conflated.  (i) *Our* ground-projection adapter cannot map a box to an E- or H-tier cell at all — the oracle-box diagnostic fixes that at 0.000 before training, so the published 0 is a property of the adapter.  (ii) With the adapter removed, the detector *does* place boxes near hidden hazards at a low rate (H 0.066 at IoU > 0), but the hazard-blind twin rate is 0.076, so the **twin-conditional rate is −0.010 — indistinguishable from zero — against +0.337 on the V tier**, where the same control shows the detector is strongly hazard-conditional.  At the storage floor τ_conf = 0.05 the H twin-conditional rate rises to 0.142 and must be reported alongside.

**One further honesty note.** This detector is not visibility-trained but **amodal-trained**: all 96 test H frames carry a non-empty GT box, and for a fully occluded hazard that box necessarily covers the occluder (in scene14 the plaza and the building facade — `METRICS_NOTES_yolo.md` §4).  Asking a detector to reproduce an image-undetermined target is itself a limitation of the baseline, and it is ours to state first.  Adapter ceiling for the V column, for the same reason: frame-det 0.404 / V 0.514 / cell recall 0.074.  Parameter counts are asymmetric too (yolov8n 3.2 M · ResNet34-U-Net 24.4 M · SegFormer-B2 ≈ 27 M).


### RT.4 `FA_in-scene` — the false-alarm tier that is in no denominator (R1-F4), and a correction to N.3 / R.3

`none_in_fov` is a hazard-ON frame whose hazard falls outside the grid (past 12 m or outside ±31.1°).  Its GT row is all-zero, so **every firing is a false positive** — yet it is in neither published denominator: not in recall (no GT-positive cell) and not in `frame_fa_off` (it is an on-arm frame).  **81 of the 816 test rows, 19.9 % of the 408 hazard-ON rows.**  τ = 0.5, `rt_response/code/f4_none_in_fov.py`.

| run | n | **`FA_in-scene`** | reported `frame_fa_off` | ratio | cells/frame | mean max p |
|---|---|---|---|---|---|---|
| rgb_s42 | 81 | **0.790** | 0.375 | ×2.1 | 4.22 | 0.758 |
| rgb_s43 | 81 | **0.963** | 0.478 | ×2.0 | 3.16 | 0.881 |
| rgb_s44 | 81 | **0.642** | 0.223 | ×2.9 | 1.86 | 0.627 |
| depth_s42 | 81 | **0.593** | 0.051 | ×11.5 | 4.89 | 0.561 |
| depth_s43 | 81 | **0.444** | 0.007 | ×60.4 | 4.04 | 0.409 |
| depth_s44 | 81 | **0.444** | 0.066 | ×6.7 | 4.41 | 0.483 |
| b2_s42 | 81 | **0.519** | 0.211 | ×2.5 | 1.74 | 0.546 |
| b2_s43 | 81 | **0.926** | 0.395 | ×2.3 | 7.17 | 0.839 |
| b2_s44 | 81 | **0.469** | 0.108 | ×4.4 | 1.51 | 0.472 |

3-seed mean: RGB **0.798 ± 0.160** vs reported 0.359 (×2.2) · Depth **0.494 ± 0.074** vs 0.042 (×11.9) · B2 **0.638 ± 0.228** vs 0.238 (×2.7).  By scene: scene07 n=51 · scene14 n=6 · sceneN3 n=24.

| run | scene07 | scene14 | sceneN3 |
|---|---|---|---|
| rgb_s42 | 0.725 | 0.500 | 1.000 |
| rgb_s43 | 1.000 | 1.000 | 0.875 |
| rgb_s44 | 0.608 | 0.500 | 0.750 |
| depth_s42 | 0.882 | 0.000 | 0.125 |
| depth_s43 | 0.706 | 0.000 | 0.000 |
| depth_s44 | 0.706 | 0.000 | 0.000 |
| b2_s42 | 0.608 | 0.000 | 0.458 |
| b2_s43 | 1.000 | 0.333 | 0.917 |
| b2_s44 | 0.588 | 0.500 | 0.208 |

**CORRECTION to R.3 (and to the N.3 reading of the null control).** R.3 records `sceneN3` as *"behaved as designed … the apparatus contributes no delta of its own"*, on the strength of a twin Δ of −0.001.  The Δ ≈ 0 statement is correct and the apparatus claim stands.  What the sentence does not say is **why** Δ is 0, and for the RGB arm the answer is not "both arms are quiet":

| run | sceneN3 on-arm fire rate | off-arm fire rate | on mean max p | on cells/frame |
|---|---|---|---|---|
| rgb_s42 | **1.000** | **1.000** | 0.946 | 6.83 |
| rgb_s43 | **0.875** | **0.708** | 0.745 | 1.88 |
| rgb_s44 | **0.750** | **0.708** | 0.738 | 3.21 |
| depth_s42 | **0.125** | **0.125** | 0.111 | 0.12 |
| depth_s43 | **0.000** | **0.000** | 0.002 | 0.00 |
| depth_s44 | **0.000** | **0.000** | 0.101 | 0.00 |
| b2_s42 | **0.458** | **0.375** | 0.468 | 1.58 |
| b2_s43 | **0.917** | **0.917** | 0.789 | 4.62 |
| b2_s44 | **0.208** | **0.208** | 0.230 | 0.88 |

`sceneN3` contains **no drop-off in either arm** (its hazard is a trompe-l'œil mural, 1–2 mm of paint on flat floor), so both arms are pure negatives.  **RGB fires on 0.75–1.00 of them at mean max p 0.74–0.95** — the null control did not pass, the RGB model failed it, and Δ ≈ 0 records saturation on both arms rather than silence on both.  **Depth is genuinely quiet there (0.000–0.125 on both arms), and B2 is mixed** (0.208–0.917), so the correction is arm-specific and must not be written as a blanket statement.  This belongs in the limitations section as the single clearest measurement of scene-level shortcut behaviour in the RGB arm, next to the C2 dressing decomposition (≈ 77 % dressing) already in R.3.


### RT.5 Scene-cluster bootstrap (R2 §4.2) — which confidence intervals survive

`code/bootstrap.py` handles pairing correctly (one shared resample index across both arms) but resamples **frames** i.i.d.  Test frames are clustered by scene: one scene contributes up to 72 frames that are the same geometry under different lighting and camera cuts.  Recomputed with `scene_id` as the resampling unit, 10 000 draws (`rt_response/code/f5_cluster_ci.py`; **the canonical `bootstrap.py` is not modified** — the cluster function exists only in that isolated script).

**Off-arm FA — 7 clusters, CI reportable:**

| run | FA | frame-i.i.d. 95 % CI | **scene-cluster 95 % CI** | width ratio |
|---|---|---|---|---|
| rgb_s42 | 0.375 | [0.328, 0.422] | **[0.162, 0.647]** | **×5.2** |
| rgb_s43 | 0.478 | [0.430, 0.527] | **[0.284, 0.643]** | **×3.7** |
| rgb_s44 | 0.223 | [0.183, 0.263] | **[0.061, 0.458]** | **×5.0** |
| depth_s42 | 0.051 | [0.031, 0.074] | **[0.012, 0.125]** | **×2.6** |
| depth_s43 | 0.007 | [0.000, 0.017] | **[0.000, 0.029]** | **×1.7** |
| depth_s44 | 0.066 | [0.043, 0.092] | **[0.006, 0.158]** | **×3.2** |
| b2_s42 | 0.211 | [0.172, 0.251] | **[0.064, 0.380]** | **×4.0** |
| b2_s43 | 0.395 | [0.348, 0.442] | **[0.172, 0.699]** | **×5.6** |
| b2_s44 | 0.108 | [0.079, 0.139] | **[0.011, 0.261]** | **×4.2** |

**H and E — the CI is withdrawn, not widened.**  test H spans **2** scene clusters (scene14 60, scene15 36); test E spans **1** (scene18 45).  With 2 clusters the bootstrap can draw only 3 distinct multisets, so any interval it returns is an artefact of that enumeration.  Per §5.2/§5.3 of the draft, the replacement is the per-scene value printed beside the **same scene's** off-arm FA:

| run | H recall (pooled) | scene14 recall (n=60) | scene14 off-FA | scene15 recall (n=36) | scene15 off-FA |
|---|---|---|---|---|---|
| rgb_s42 | 0.594 | 0.467 | 0.181 | 0.806 | 0.889 |
| rgb_s43 | 0.875 | 0.983 | 0.542 | 0.694 | 0.500 |
| rgb_s44 | 0.594 | 0.667 | 0.083 | 0.472 | 0.708 |
| depth_s42 | 0.406 | 0.650 | 0.000 | 0.000 | 0.083 |
| depth_s43 | 0.469 | 0.650 | 0.000 | 0.167 | 0.000 |
| depth_s44 | 0.438 | 0.700 | 0.000 | 0.000 | 0.208 |
| b2_s42 | 0.083 | 0.133 | 0.125 | 0.000 | 0.014 |
| b2_s43 | 0.396 | 0.100 | 0.069 | 0.889 | 0.986 |
| b2_s44 | 0.208 | 0.333 | 0.000 | 0.000 | 0.014 |

On `scene15` two of three RGB seeds fire on **more** hazard-free frames of that scene than they detect hidden drops in it (0.806 vs 0.889 · 0.472 vs 0.708), and `b2_s43` is 0.889 vs 0.986.  scene15 supplies 37.5 % of the H denominator and close to no discriminative evidence; scene14 carries the effect for both arms.


**CORRECTION to `runs/v2/SEED_TABLE.md` §5.1/§5.2 (auxiliary pixel-loss ablation).** Same 816 rows, paired aux − base on rgb seed 42, one resample draw shared by both arms:

| metric | Δ | frame-i.i.d. 95 % CI | scene-cluster 95 % CI | verdict |
|---|---|---|---|---|
| cell_f1 | +0.0403 | [0.0001, 0.0786] | [-0.2580, 0.2054] | **significance does not survive clustering** |
| cell_precision | +0.1291 | [0.0885, 0.1690] | [-0.1620, 0.2458] | **significance does not survive clustering** |
| cell_recall_H | +0.3546 | [0.2768, 0.4302] | [-0.1429, 0.4625] | **significance does not survive clustering** |
| frame_det_rate | -0.1682 | [-0.2296, -0.1064] | [-0.4818, 0.1594] | **significance does not survive clustering** |
| frame_recall_H | +0.1250 | [-0.0096, 0.2526] | [-0.4167, 0.4500] | was not significant either way |
| frame_fa_off | -0.2083 | [-0.2531, -0.1646] | [-0.3627, -0.0613] | survives |
| cell_fpr_off | -0.0297 | [-0.0372, -0.0222] | [-0.0650, -0.0048] | survives |
| frame_recall_V | -0.1889 | [-0.2551, -0.1257] | [-0.4444, -0.0290] | survives |
| frame_recall_E | -0.6000 | [-0.7436, -0.4528] | [-0.6000, -0.6000] | **degenerate** — support is 1 scene (scene18); report no CI |
| cell_recall_E | -0.3592 | [-0.4556, -0.2626] | [-0.3592, -0.3592] | **degenerate** — support is 1 scene (scene18); report no CI |

Two consequences.  (a) The `cell_f1 +0.0403 [0.0001, 0.0786] yes (barely)` row must have its significance claim withdrawn — under scene resampling it is [-0.2580, 0.2054].  (b) **More seriously**, §5.2 calls `cell_recall_H` **+0.3546** *"the single largest confirmed effect in the table, and the one that matters for this paper's thesis"*; under scene resampling that interval is [-0.1429, 0.4625] and **includes zero**.  The frame-level interval was measuring within-scene variation across the same two H scenes.  That sentence needs the same withdrawal, and it is the more consequential of the two.


### RT.6 strict-H twin pixel-difference audit (R1-F7) — what remains visible when the hazard contributes zero pixels

strict-H is a **geometric** predicate: `int_px == 0 ∧ edge_vis == 0`, i.e. the hazard prism re-projects to zero pixels.  It does not forbid the hazard from changing the image through shadow, ambient occlusion, GI bounce or mesh seams.  All 96 test H twin pairs were re-read at native 1920×1080 and differenced, `d = max_c |on_c − off_c|` (`rt_response/code/f7_hpair_pixdiff.py`; all 96 verified pose-exact to 1e-6, consistent with N.1's H 96 EXACT / 0 TOL / 0 EXCL).

**Calibration first.** `sceneN3`'s `keep_dressing` off arm is geometrically identical to its on arm (R.3: heightmap `max |Δ| = 0.000000 m`), so its render-to-render difference is pure path-tracer / denoiser nondeterminism:

| reference pair | n | median px ≥ 2/255 | median px ≥ 8/255 | **median px ≥ 32/255** | median magnitude over changed px |
|---|---|---|---|---|---|
| renderer noise floor (N3, identical geometry) | 24 | 916,841 (**44.2 % of frame**) | 27571 | **50** | 3.19 |
| hazard-only (C2 `keep_dressing`, drop deleted, dressing kept) | 24 | 1,270,241 | 875,005 | 698,078 | 61.87 |

A 2/255 threshold flips 44 % of the frame on two renders of the *same* geometry, so ≥ 32/255 is the level that carries scene content (floor: 50 px of 2 073 600).

| set | n | pairs with zero difference | median px ≥ 32/255 | min | % of frame | × noise floor |
|---|---|---|---|---|---|---|
| all test strict-H | 96 | **0** | 93,606 | 2,211 | 4.51 % | ×1872 |
| scene14 | 60 | **0** | 156,977 | 42,797 | 7.57 % | ×3140 |
| scene15 | 36 | **0** | 7,106 | 2,211 | 0.34 % | ×142 |

**strict-H is never optically empty in this corpus.**  0 of 96 pairs are identical and the quietest still carries 2,211 pixels at ≥ 32/255, 44× the noise floor.  The zero-difference consistency gate has no pair to run on.  81.2 % of the residual falls inside the amodal hazard silhouette (the prism projected ignoring occlusion) and 44.5 % inside the GT-positive wedges — but note that for a fully occluded hazard the amodal silhouette necessarily covers the occluder too, so containment means *co-located with the hazard's line of sight*, not *the hazard's own pixels*.

**The scene split matches the twin-Δ split exactly.**  scene14's residual is 22.1× larger in count and 7.6× larger in per-pixel magnitude than scene15's; scene15's mean magnitude over changed pixels (4.78) is only 1.5× the renderer noise floor (3.19).  That is the same 60/36 split that carries the H twin Δ (scene14 rgb .278/.448/.558, depth .577–.645; scene15 rgb −.010/.209/−.058).  **Two independent measurements — model response and raw pixels — pick out the same scene.**

**Does the residual grade the response?**  Spearman ρ between log10(residual px ≥ 32/255) and that pair's `delta_score` is positive in all nine runs (0.27–0.83 pooled).  Within scene, **Depth is positive in all six cells (0.08–0.69) and its scene14 quiet→loud residual tercile moves Δ from 0.34–0.40 to 0.83–0.93; RGB is inconsistent** (−0.13 to +0.39).  The residual optical evidence is what the Depth arm tracks; the RGB arm's H response is not graded by how much is visible — the same diagnosis RT.2 reaches from the twin-conditional side.

**Scope limit this imposes on every twin Δ in this document (R1-F12).**  The toggle is `SCENE_CONFIG['hazard_stairs']`.  In `scene14` that branch builds the shoulder massif, the side slopes, the stair, the step coursing, the parapets, the cues **and** the autumn litter, and `False` replaces all of it with a flat fill (`scenes/main/scene14_grandstair_illusion.py:1885-1898`); in `scene15` it removes the stair and the bend and extends the alley flat (`scenes/main/scene15_alley_labyrinth.py:2301-2304`).  Every Δ is therefore a sensitivity to {the drop's indirect optics} ∪ {every object inside that branch}, not to the drop geometry alone.  Figures: `rt_response/panels/h_diff_contact_sheet.png` (six pairs = min/median/max residual within each scene, selection rule fixed before inspection).


### RT.7 Document corrections (R3 §1.4, §1.5) — append-only, nothing above is edited

**(a) §2.4 τ_edge is printed as 0.02; the value used everywhere is 0.05.**  `code/labeling/labeler.py` has `TAU_INT_DEF, TAU_EDGE_DEF = 50, 0.05`, and `dataset_manifest_v2_full.json` `meta.tau_strict` is `{tau_int: 50, tau_edge: 0.05}`.  **No number changes** — see (b) for why.

**(b) The τ_edge sensitivity argument in §2.4 is vacuous as written, and the honest version is stronger.**  "strict-H is τ-insensitive: 45 frames at all 9 combinations" is true but tautological: `labeler.tier_of` defines H as `int_px == 0 and edge_vis == 0`, a predicate neither threshold enters, so no sweep could have moved it.  What the data actually shows is that **τ_edge is unconstrained by this corpus**: `edge_ratio` is bimodal — exactly 0 or ≥ 0.44 (v1 n = 93: 57 zeros, 36 non-zero with min 0.505; v2_full n = 345: 273 zeros, 72 non-zero with min 0.44), and the swept grid {0.02, 0.05, 0.10} lies entirely inside an interval containing no data.  Replacement sentence: *"Lip visibility is effectively binary in this corpus (edge_ratio = 0 or ≥ 0.44), so the E/H boundary is independent of τ_edge; 0.05 is an arbitrary representative of the empty interval (0, 0.44) and there is nothing to tune.  τ_int = 50 px is the threshold that does move results — it defines the V/H_weak boundary and shifts corpus V 726 → 657 and H_weak 0 → 57 across a 1 → 200 sweep — while headline strict-H is invariant to both by definition."*

**(c) `dayrun_0820/SPLIT_PROPOSAL_v2_full.md` — the `frames` column is not the split size.**  That column holds the `V+E+H+off` subtotal, which omits `H_weak` and `none_in_fov`.  Recomputed directly from `dataset_manifest_v2_full.json` + `split_v2_full.json`:

| split | V | E | H | H_weak | none_in_fov | off | **true frames** | doc's `frames` |
|---|---|---|---|---|---|---|---|---|
| train | 438 | 21 | 141 | 21 | 147 | 768 | **1536** | 1368 |
| val | 75 | 6 | 6 | 3 | 54 | 144 | **288** | 231 |
| test | 180 | 45 | 96 | 6 | 81 | 408 | **816** | 729 |
| hold | 0 | 0 | 0 | 0 | 96 | 96 | **192** | 192 |
| **non-hold total** | 693 | 72 | 243 | 30 | 282 | 1320 | **2640** | 2328 |

The same document's `PROOF-4` states *"every non-held frame resolves to exactly one split: 0 bad of **2640**"*, so the file asserts both 2640 and 2328; the difference 312 = H_weak 30 + none_in_fov 282.  §N of this file already writes `test 816 = 408 on + 408 off` correctly.  Fix: rename the column `V+E+H+off` and add the two missing tier columns.  This is exactly the frame-count audit trap §12.3-⑥ predicted a reviewer would spring.


### RT.8 What this block does **not** close

| # | open item | why it cannot close in this window |
|---|---|---|
| RR1 | test strict-H rests on **2 scenes, 1 of which carries the effect** | test set is frozen; no new test scene can be rendered.  The response is claim scope, not data |
| RR2 | `SEED_TABLE` §5.2's `cell_recall_H` significance claim | needs an edit to that file (append-only rule) — flagged in RT.5, sign-off item |
| RR3 | decomposing the strict-H residual into shadow vs co-removed structure | needs the CUE-OFF render arm with a placebo arm (D35) |
| RR4 | monocular-depth baseline (R1-F9) | not run; limitations sentence is the minimum response |
| RR5 | related-work paragraph on amodal completion / BEV layout hallucination (R1-F5) | writing task, GPU 0 |
| RR6 | no experiment treats a cue as a manipulated variable (R1-F6) | needs the B1 cue-OFF render |
