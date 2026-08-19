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
