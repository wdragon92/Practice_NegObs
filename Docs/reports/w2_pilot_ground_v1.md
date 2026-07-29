# W2-B — ground_kit GPU pilot round (sceneN5 · scene15 · scene13)

Author: W2-B (MAIN tree, branch `feat/realism-v1`) · Date 2026-07-29 · GPU exclusive, renders
sequential, single instance, `NEGOBS_PT_FAST=1`, `MODE=pt`, `NEGOBS_LOOK_V1=1`.
Every number below is `[measured]` from a PNG or from code executed this session, `[calc]` from the
verified frame model, or `[assumed]` with the reason stated.

---

## 0. Verdict in one paragraph

The blocking verification (§1.4 P-A A/B on `sceneN5`) **passes with margin**: manhole-ROI dark
pixels 0.020 % → **5.906 %** (line ≥ 4.5 %; look-OFF reference `ctx2` is 5.884 %), strong-yellow
tactile pixels 118 → **12,149 px** (line ≥ 1,500; §12.5 stretch target 8,000 also cleared). The
`scene15` manhole was de-dominated from 56.1 % to **17.8 % measured** frame width. All three scenes
render, all three are committed, `python3 ground_kit.py` exits 0 throughout. **But the round found
two defects that were invisible to every CPU gate**, one of which silently nulled most of the kit's
output: (a) `apply_ground` never resolved a positionally-passed material dict, so the first render
crashed; (b) **every recessed element — joints, cracks, and ~half of all manholes — rendered zero
pixels**, because the kit modelled a recess as a plate below the pavement top while the pavement is
a *solid* box. Both are fixed and re-rendered. Separately, two findings block clean adjudication:
`r2_on` is **not** a valid A/B baseline (ten 07-29 commits intervene; cherry blossoms now appear in
every cut), and the GT-E4 twin re-derivation of the GRAZE detection floor comes out at
**0 / 16 = 0.0 %** on real drops. **Verdict for W2-C: NO-GO as stated, conditional GO on four
items in §7.**

---

## 1. Preflight (CPU, before any render)

### 1.1 P1(a) — GT-E2 / B7 row-scale ambiguity `[fixed]`

Red-team finding G-1 confirmed and resolved end-to-end. `regression_check.GRAZE_LONG = 960`, so the
checker works on a **960 × 540** image and its constants `GRAZE_HW 3 + GRAZE_SMOOTH 3 +
GRAZE_SLACK 2 = 8` are **@540 rows**. `cam_row()` returns **@1080 rows**. v1.1 compared the two
directly, so B7 enforced 16 @1080 = **8 @540 = exactly the filter footprint radius**, i.e. half the
derived "two responses fully separated" strength.

Row units are now explicit everywhere (`ground_kit.py`):

| name | value | axis |
|---|---:|---|
| `GRAZE_WORK_LONG` / `GRAZE_WORK_H` | 960 / 540 | — |
| `ROWS_1080_PER_WORK` | 2.0 | — |
| `GRAZE_FOOTPRINT_WORK` | 8 | @540 |
| `GRAZE_ROW_SEP_WORK` | 16 | @540 |
| `GRAZE_FOOTPRINT_1080` | 16.0 | @1080 |
| `GRAZE_ROW_SEP_1080` | 32.0 | @1080 |

plus `to_work_rows()` / `to_1080_rows()` and a `cam_row` docstring that names its axis.

**The derived strength is not uniformly achievable, and that is a measured fact, not a judgement**
`[calc]`:

| cut | E band (ground dist.) | band row span @1080 / @540 | max reachable separation @540 |
|---|---|---|---|
| d2 | 1.4 – 4.4 m | 238.50 / 119.25 | 67.5 → 16 @540 **reachable** |
| d5 | 3.5 – 11.0 m | 98.23 / 49.12 | 27.6 → **reachable** |
| **d10** | **7.0 – 22.0 m** | **49.60 / 24.80** | **13.92 → unreachable** |

At d10 the whole E band is 24.80 rows @540 with the edge row inside it; no position in the band can
reach 16 @540. Enforcing it literally would mean "zero transverse lines in the d10 E band", which
kills §5.1 P1's own periodic-joint prescription *and* contradicts GT-E2's own "≤ 1 line" wording.
`graze_row_sep_1080(d, h)` therefore **computes** the binding bound per cut: full separation where
the band admits it, footprint bound where it does not. Below footprint the responses genuinely
merge, so that remains a hard fail everywhere. **The gate is strictly stronger than v1.1 at every
cut and never demands the impossible.**

Consequences, all re-measured:

* `scene13` 13-3 entry trench moved **x 0.35 → 0.52** (frame half-width 0.19 ⇒ near boundary
  +0.16 → **+0.33 m** beyond the crest). d2 separation **18.12 → 34.70 rows @1080 = 9.06 → 17.35
  @540** `[calc]`. Still beyond the crest, so the C-2 (d2-only) invariant is untouched. Lane-line
  start moved 0.6 → 0.80 m so paint no longer runs over the steel frame.
* `EXPECTED_FP` now carries **both** axes: `rows` (@1080, spec §12.3 notation) and `rows_work`
  (@540, what the GRAZE JSON consumer actually reports). Round judges must match `rows_work`.
* **Spec §12.3's d5 sample is superseded**: `(348, 356)` → **`(348, 371)`** @1080 =
  `(166, 194)` @540. At the corrected scale the band's far boundary (Δ 22.1 @1080 = 11.1 @540) is
  also inside the merge zone, so it joins the registry. The d10 sample `(297, 304)` is unchanged.
* Every other B7 near-miss across the 33 fixtures is either a periodic joint at d10 (Δ 19.1–21.8
  @1080, passes the footprint bound) or a `TACTILE_SITES`-registered GT-E2-x exception.

### 1.2 P1(b) — `scene15` manhole re-placement `[fixed]`

Red-team finding G-2 confirmed: at `x = −4.00` the manhole sits at ground distance **1.00 m** from
the d5 eye ⇒ `f·0.648/1.00` = **1,077.5 px = 56.1 %** of frame width `[calc]`. The report's
"280 px / 14.6 %" was the *old* x = −1.15 position's number.

**≤ 25 % is unreachable anywhere inside W1** (0.564–2.00 m): even at W1's far limit X = 2.00 the
disc is 538.7 px = **28.1 %** `[calc]`. The manhole therefore moves to the second-priority window
**W2** (2.00–3.00 m): **x = −2.40** ⇒ X = 2.60 m ⇒ 414.4 px = **21.6 %** predicted, **342 px =
17.8 % measured** on the render (the measured figure counts only the disc core that clears the
|Δ| > 25 threshold). At d2 it is behind the eye (X = −0.40) so it is invisible there and the d2
near-window is carried by repair patch #1 as designed; at d10 it is 141.8 px = 7.4 %.

Interference re-checked `[calc]`: disc x [−2.724, −2.076] × y [−0.474, 0.174] clears joint `JX_3`
(x = −3.00), patch #1 (x −1.557…−0.843), the U-gutter (y −0.875…−0.625) and the grime bands
(|y| ≥ 0.75). No z-fighting. The `SCENE_PLANS` fixture was synced to the same coordinate (it still
held the pre-M9 value −1.15).

### 1.3 P2 — tooling verification `[measured]` — **blocker cleared**

`scripts/near_ground_stats.py` reproduces its published anchors on existing renders:

| cut | metric | tool | published |
|---|---|---:|---:|
| `scene01/v7_pt/h0.3_d2` | L_mu / wht% / σ_LF / edge% / struct% | 0.865 / 98.2 / 0.72 / 16.4 / 5.0 | identical |
| `scene18/v7_pt/h0.3_d2` | sd / mean | 5.7 / 221 | identical |
| `scene09/v8_pt/h0.3_d2` | sd / mean / >224 % | 13.3 / 209 / 3.56 | identical |
| `scene17/v8_pt/h0.3_d2` | sd / mean / flat% | 4.2 / 166 / 99.78 | identical |
| `scene12/v8_pt/h0.3_d2` | sd / mean | 12.7 / 112 | identical |
| `scene03/v7_pt/h0.3_d5` | sd / mean | 35.7 / 144 | identical |
| `flat_gnd` medians `r2_on` | scene13 / scene14 / sceneC1 | 12.1 / 31.3 / 98.3 | identical |

`regression_check.py` v2.1 on the two known T3 pairs: **GRAZE quiet on both**
(`scene13 v6_rt→v7_rt`, `scene07 r1_on→r2_on`), matching `w2_tools_v1.md` §4.4. The residual
FAILs on those pairs are FRAME/PHOTO, not GRAZE. Ground-kit report §7.3's blocker is closed.

### 1.4 P3 — round stamp `[measured]`

Written by the round driver into every capture directory as `round_stamp.json`, and reproduced in
the driver's header. The stamp is **"material state = r2_on (MDL v1.8.0 equivalent, detail
unwired)"**, and it is verified rather than asserted:

* `assets/NegObsGround.mdl` header reads **v1.9.0** (md5 `16bba896cc007ae12607fdfa252b24f0`), but
  every v1.9.0-added parameter is at an inert default and **no caller binds any of them**
  (`grep` over the whole tree): `detail_bump_factor 0.0` and an invalid `detail_normalmap_texture`
  (both trigger `negobs_detail_normal`'s early return), `detail_rough_gain 0.0` (identity),
  `unit_cell_m/origin float2(0)` (`negobs_unit_gain` returns 1.0). NegObsGround therefore renders
  pixel-identically to v1.8.0.
* T1's detail grain maps `assets/detail_grain_{mineral,granular,brushed}_nor.png` exist on disk and
  are referenced by **nothing** except their generator.
* The Phase-1 E3 detail normal in `scene_common` (OmniPBR, `concrete_wall_nor_dx.jpg`, bump 0.45,
  8 cm) is pre-existing `r2_on` state, unchanged. Render logs confirm `디테일=0` for the
  NegObsGround path.
* Sun angular cap = `NEGOBS_SUN_CAP_DEG` default **1.5** in this tree; the 0.6 change lives only on
  `w2-surgeon`. AE off.

---

## 2. `sceneN5` — the blocking P-A verification

Round: `look_check/sceneN5/w2_pilot` (13 cuts, 73 s). Round 1 preserved at `w2_pilot_r1`.

| # | metric | ROI / cut | before (`r2_on`) | **after** | line | verdict |
|---|---|---|---:|---:|---|---|
| N5-1 | dark-pixel fraction (L < 0.400) | `manhole_pair` px 500–1100 × 350–750 | 0.020 % | **5.906 %** | ≥ 4.5 % | **PASS** |
| N5-2 | \|∇\| p99, central diff | same ROI | 0.0401 | **0.2086** | ≥ 0.165 (75 % of ctx2) | **PASS** |
| N5-2′ | \|∇\| p99, forward diff | same ROI | 0.0575 | **0.2599** | ≥ 0.226 (75 % of ctx2) | **PASS** |
| N5-3 | strong-yellow px | `approach` | 118 | **12,149 (0.586 %)** | ≥ 1,500 | **PASS** |
| N5-3b | same, §12.5 stretch | `approach` | — | **12,149** | ≥ 8,000 | **PASS** |
| — | strong-yellow px | `preset_h0.3_d5` | 88 | **4,433** | — | 50× |
| — | strong-yellow px | `beauty_oblique` | 55 | **11,337** | — | 206× |
| N5-4 | regression v2.1 GRAZE | 13 cuts | — | **1 firing (h0.3_d2)** | FAIL 0 | see §2.2 |
| N5-5 | OCCL new dark blob | h0.3 ×3 | — | **0.0–0.1 %** | no new blob | **PASS** |

**Threshold recovery, stated honestly.** The spec gives the dark-pixel and yellow lines but not
their pixel definitions. The dark threshold was recovered by sweep: **L < 0.400** reproduces both
published anchors to 0.004 pp (`r2_on` 0.020 % vs 0.02, `ctx2` 5.884 % vs 5.88). The yellow rule
`sat > 0.40 ∧ (r−b) > 0.25 ∧ (g−b) > 0.15` reproduces all six published values exactly
(118/88/55 and 2090/1333/680). The **|∇| p99 definition could not be reproduced**: no combination
of luma (Rec.709/601/mean/PIL-L) × operator (central, forward, Sobel, Sobel/4, Sobel/8) ×
percentile (95/99/99.5/99.9) lands on the published 0.079 — the closest, Sobel/8 @p99.9, gives
0.085. Two standard definitions are therefore reported with their own `r2_on`/`ctx2` anchors
re-measured this session, and judged at the same **75 %-of-look-OFF** convention the spec used for
N5-1 and N5-3. Under the literal "≥ 0.30" the forward figure (0.2599) would *fail*; note that
`ctx2` itself measures 0.3019 forward, so "≥ 0.30" is effectively a *100 %-of-look-OFF* line,
stricter than the convention used for the other two sub-tests. **Recovery is 5.2× (central) /
4.5× (forward), reaching 95.0 % / 86.1 % of the look-OFF reference.** Supervisor should confirm
which convention is normative.

### 2.1 Eyes (h0.3 ×3, done before the numeric gates)

| crop | verdict |
|---|---|
| `look_check/sceneN5/w2_pilot_crop/preset_h0.3_d{2,5,10}_before_after.png` | **PASS.** Joints go from smeared ghosts to crisp lines; the drain slot reads as a hard dark band. |
| `look_check/sceneN5/w2_pilot_crop/approach_before_after.png` | **PASS, decisive.** Before: a featureless white sidewalk with zero manholes, gullies, patches, stains or tactile blocks. After: manholes and gullies read as dark discs, repair patches as tone plates, and the legal yellow tactile band is unmistakable in front of the bollard row. This single pair is the clearest evidence that the P-A blocker is resolved. |
| `look_check/sceneN5/w2_pilot_crop/r1_vs_r2_d2_bottom.png` | The near-window manhole (1,268 px, 66 % of frame width at d2) appears **only in round 2** — it was buried in round 1 by the defect in §4.2. |
| `look_check/sceneN5/w2_pilot_crop/tactile_band.png` (4× zoom) | Tactile band and repair patch read correctly. **Defect: weeds render as solid olive cubes.** |
| `look_check/sceneN5/w2_pilot_crop/graze_band_d2.png` | GRAZE band ×2 with the 2.0 m row marked — see §2.2. |

### 2.2 The one GRAZE firing — adjudicated **expected change**

`preset_h0.3_d2`, step 0.8 → 46.1 (ratio 54.4) at row 250/540, column agreement 0.99. Row profile
`[measured]`: rows 496/498 fall by −101.9 / −85.0 while 486–512 elsewhere move ≤ ±3.7.

`cam_row(2.0) = 497.35 @1080 = 248.7 @540` — the response sits exactly on the notional 2.0 m row,
and `sceneN5` has a **construction joint at x = 0** in its own `PARAMS["joints"]` (spacing 3.0,
x0 = −9.0). The checker is measuring **P-A un-burying a pre-existing sidewalk joint**, which is the
entire point of the blocking fix. `sceneN5` is a hard negative (`edges=()`, no drop anywhere), so a
"hidden drop revealed" reading is not available; GT-E4 explicitly re-baselines GRAZE for the first
ground_kit round. The band contains **0 seasonal-asset pixels**, so the firing is not contaminated.
**Verdict: expected change, not a regression.** The checker itself defers this class
("자동 확정 불가 — 그 대역만 잘라서 육안 확인"); the crop is saved.

### 2.3 Latent issue recorded, not fixed

`sceneN5` now has a **double joint grid**: the scene's own `build_joints` (3.0 m, x0 = −9.0,
30 mm wide, +0.6 mm proud) and ground_kit's `Joints/JX_*` (3.0 m, 3.5 mm wide) are co-located at
x = −9, −6, −3, 0. §9.2 step 3 asked for *migration* of existing elements into the kit, not
addition. After the §4.2 fix both now sit at the same top z, so they are coplanar; no z-fighting
speckle is visible in the render, but the 5 ground_kit prims are redundant. **W2-C cleanup item.**

---

## 3. `scene15` — 8-element alley fill

Round: `look_check/scene15/w2_pilot` (13 cuts, 51 s). Plan: 47 prims + 2 grating, δmax 0.0824.

| # | metric | cut | before | **after** | line | verdict |
|---|---|---|---:|---:|---|---|
| 15-1 | σ_LF (bottom 30 %) | h0.3 d2/d5/d10 | 0.76 / 0.69 / 0.67 | **0.80 / 0.69 / 0.66** | ≥ 5.0 (WARN) | **not met** |
| 15-2 | sd (bottom 45 %) | h0.3 d2/d5/d10 | 15.9 / 15.9 / 16.1 | **16.3 / 15.9 / 16.5** | ≥ 32 (WARN) | **not met** |
| 15-3 | d5 manhole screen width | h0.3_d5 | 1,078 px = 56.1 % | **342 px = 17.8 %** | ≤ ~25 % | **PASS** |
| 15-4 | 0–5 m flat% | h0.3 d5 | 3.7 | 5.5 | informative | — |
| 15-5 | GRAZE, hazard-off twin | 4 cuts ×2 dir | — | **0 firings** | no new edge response | **PASS** |
| 15-6 | regression v2.1 | 13 cuts | — | **FAIL 0 · WARN 0 · PASS 7 · INFO 6** | FAIL 0 | **PASS** |
| — | white % / >224 % | bottom 45 % | 0.0 / 0.00 | 0.0 / 0.00 | ≤ 2 / ≤ 5 | **PASS** |

`scene15` is the only scene whose regression is completely clean against `r2_on`, which is itself
informative: the alley has no façade/vegetation in the judging band, so the 07-29 contamination
(§5) does not reach it.

**σ_LF / sd did not move, and that is the round's most important negative result.** 47 prims of
ground elements changed the bottom-30 % low-frequency std by +0.04. Two causes, both measured:
the recess burial of §4.2 (fixed here, and the fix moved σ_LF by only +0.04 → the burial was not
the whole story), and the fact that **repair patches are bound to the alley's own floor material**
(`patch=M["alley"]`) because §4.4 delegates colour to T1 — so a patch is currently an invisible
rectangle with a thin visible cut-line. The frame-fill objective of the kit is **materially
dependent on T1** and cannot be judged before that merge.

### 3.1 Eyes — "does it read as a Korean alley at h0.3?"

| crop | verdict |
|---|---|
| `look_check/scene15/w2_pilot_crop/d5_r2on_vs_round2.png` | **PARTIAL PASS.** The wall-side U-gutter with covers, the two repair patches, the manhole disc and the grime bands are all present and legible; the alley is no longer an empty tan corridor. |
| `look_check/scene15/w2_pilot_crop/preset_h0.3_d2_before_after.png` | **FAIL at d2.** The near field is still essentially featureless — only a thin light rectangle (patch #1's cut-lines). Nothing else reaches the d2 window. |
| `look_check/scene15/w2_pilot_crop/diff_d5_overlay.png` | Predicted element footprints overlaid on the ×4 difference image — the tool used to prove the manhole was rendering zero pixels in round 1. |
| `look_check/scene15/w2_pilot_crop/manhole_zoom.png` | 3× zoom of the manhole region. |

Look defects visible here and carried to §6: **weeds are green boxes**, the **manhole reads
near-white** (bound to `M["rail"]`, while the kit's declared albedo for B9 is 0.10 = dark cast
iron), and at close range **the manhole disc is a visible octagon**, not a circle.

---

## 4. `scene13` — ramp curb, GT hand-off, `cue_tactile` ON

Round: `look_check/scene13/w2_pilot` (15 cuts, 125 s, `NEGOBS_PT_TOTAL_SPP=256`,
`cue_tactile=true`). Plan: 54 prims, δmax 0.1191, 1 T1 material request (`groove_stripe`).

| # | metric | cut | result | line | verdict |
|---|---|---|---|---|---|
| 13-5 | GT hand-off ledger | build log | **1 `gt_changes` record**, drop 0.120, owner W4, printed verbatim | 1 record | **PASS** |
| 13-4 | entry-trench row separation | h0.3_d2 | **34.70 @1080 = 17.35 @540** (was 18.12 / 9.06) | ≥ 32 @1080 | **PASS** |
| 13-3 | d5 manhole | h0.3_d5 | visible, ≈ 51 % frame width as predicted | present | **PASS** |
| 13-1 | ramp curb visible at d2, absent at d5/d10 | h0.3 ×3 | **unsatisfiable** — see below | — | **N/A** |
| 13-2 | approach asphalt σ_LF | h0.3 ×3 | not adjudicated (baseline invalid, §5) | ≥ 5.0 WARN | — |
| 13-6 | OCCL | h0.3_d2 | new dark 21.0 %, largest blob 19.5 % | no new blob | **not ground_kit** (§5) |
| — | regression v2.1 GRAZE | 15 cuts | **1 firing (h0.3_d5)**, step 56.6→67.6, ratio 1.20 | FAIL 0 | deferred (§5) |
| — | `cue_tactile` ON flip | build | executed via `NEGOBS_SCENE_CONFIG`; §12.4 list honoured | ON | **PASS** |

**13-1 cannot be satisfied as written, and the reason is geometric** `[calc]`. The curb sits at
|y| 2.70–3.00 m (주차장법 §6①5다: carriageway face ≥ 30 cm from the wall at y = ±3.00). At d2 the
frame half-width at the crest is only `0.5774 × 2.0 = 1.15 m`, so **the curb is outside the frame
laterally at d2**; at d5 (2.89 m) and d10 (5.77 m) it is inside the frame but occluded by the crest
per the C-2 invariant. The curb therefore contributes **nothing to any h0.3 judging cut** — it is
visible only in the mise-en-scène cuts. This does not invalidate the curb (it is a statutory member
and an approved GT change whose label W4 will attach), but the §5.3 gate row should be rewritten
against a mise-en-scène cut.

### 4.1 Eyes

| crop | verdict |
|---|---|
| `look_check/scene13/w2_pilot_crop/preset_h0.3_d2_before_after.png` | Near ground turns from brown asphalt to near-black; the OCCL blob is real **but is not ground_kit's** (§5). |
| `look_check/scene13/w2_pilot_crop/d5_hoff_vs_hon.png` | **PASS on the hazard.** The ramp mouth reads as a dark trench with railings and the ramp surface is correctly invisible below the crest — the C-2 grazing-occlusion invariant holds on screen. The d5 manhole is a large dark disc, and its **polygonal tessellation is clearly visible** at this range. |

### 4.2 The defects the pilot caught (both invisible to every CPU gate)

**(a) `apply_ground` never resolved a positional material dict.** The `patch` op passed
`{"patch": "patch", "patch_cut": "patch_cut"}` as a *positional* argument; the substitution rules
only cover `"@key"` strings and the `mtls=` / `mtl*=` keywords, so `build_patch_field` received the
literal string `"patch"` and handed it to `UsdShade.MaterialBindingAPI.Bind()`. The first
`sceneN5` render died with `Boost.Python.ArgumentError`. `dry_kit` never binds, so
`python3 ground_kit.py` was green throughout. **Fixed** (op moved to `mtls=`), plus a guard in
`apply_ground` that inspects the *raw* op definition and raises on any unresolved material
reference, plus a 33-scene `apply_ground` round-trip added to the self-check so this class is now
caught on CPU.

**(b) Every recessed element rendered zero pixels.** v1.1 modelled a recess as a thin plate whose
top sits at `z + recess` (negative). The pavement in these scenes is a **solid box**
(`scene15 UpperAlley` z −6.0…0.0; `sceneN5 Pave_*` 60 mm thick), so such a plate is entirely
enclosed and produces no pixels. Measured on round 1 `[measured]`:

| element | test | result |
|---|---|---|
| `scene15` joint x = −9 at d10 (ground distance 1.00 m) | \|Δ\| vs `r2_on` at its rows | **max 9.5 = no change** |
| `scene15` manhole, predicted rect rows 420–468 cols 849–1263 at d5 | mean before → after | **138.0 → 137.3, \|Δ\|max 31.5** |
| `scene15` manhole, all 13 cuts incl. `beauty_overview` | difference image | **no disc anywhere** |

Manholes had a second, compounding cause: `build_manhole(proud=None)` draws the KS D 4040 flush
tolerance as `U(−10, +10) mm`, and **a negative draw puts the whole lid inside the solid slab**.
Deterministic draws checked across the pilots: `scene15 (−2.40, −0.15)` → −1.73 mm,
`scene13 (−3.90, 0.00)` → −9.07 mm — roughly **half of all 33-scene manholes** were in this state.

Fix: `surface_top_z()` — a recess is rendered as **tone, not depth** (which is what §4.4 prescribes
anyway: geometry owns position, T1 owns colour). Tops move to `+GROUND_PROUD_MIN` (0.6 mm), the
nominal value is preserved as `recess_nominal` in the element ledger, and **GT-E1′ judges the
nominal (≤ 0) value** so a 0.6 mm z-fighting epsilon is not mistaken for real relief.
`_ik_manhole` folds the flush draw to `|raw|` so the deviation survives (0.6–10.6 mm proud) but the
burial cannot. A **burial guard** was added to the self-check: non-exempt elements with
`proud < 0` must be **0** across all 33 scenes (deck plank gaps, trench/gutter seats and the
zero-prim groove band are the declared exemptions). Effect of the fix, measured as round 1 → round 2
on identical cameras: `scene15` d5 manhole region **9,966 px** now differ by > 25;
`sceneN5` d2 **340,425 px** change as the near-window manhole appears.

---

## 5. Why FRAME / PHOTO / OCCL / DARK / WHITE verdicts are withheld

**`look_check/*/r2_on` is not a valid A/B baseline for this round** `[measured]`. It was rendered
on 07-28 22:5x; ten commits landed on 07-29 between it and `HEAD` (vegetation USD swap, shrub
realisation, façade low-rise, stair handrails, railing balusters, leaf litter, infra kit, red-team
fixes, …). Two independent proofs:

1. **Seasonal-asset violation, quantified.** Pink-blossom pixels in `sceneN5`, `r2_on` → `w2_pilot`:
   3 → 65,228 (`h0.3_d2`), 9 → 71,965 (d5), 12 → 76,087 (d10), 8 → 108,829 (`approach`),
   2 → 87,018 (`beauty_oblique`) — i.e. 3.4–5.7 % of every frame is now flowering cherry. The main
   tree still carries `("Trees/Japanese_Cherry.usd", 4.64, 5)` at `scene_common.py:1715`; the
   `w2-surgeon` branch has already deleted it. Confirms `w2_gate_preflight` §1.7's `sceneN3`
   observation and generalises it. This is a standing convention violation
   ("계절/이벤트 특정 요소 금지") and the dominant driver of the FRAME firings.
2. **`scene13` d2 OCCL is provably not ground_kit's.** The new-dark mask covers rows 660–1020
   (99.7 % of the width at rows 720–779). Projecting **all 49** plan elements onto that frame,
   **zero** ground_kit elements fall inside rows 700–1000 × cols 700–1220. Near-ground RGB goes
   (114, 91, 68) → (26, 23, 22) in the hazard-**on** arm and (35.6, 32.4, 31.5) in the hazard-off
   arm — i.e. the darkening is present regardless of ground_kit's hazard state.

The gate ROIs that *are* uncontaminated were checked explicitly: **0 blossom pixels** in the N5-1 /
N5-2 ROI, **0** in the d2 GRAZE band, **0** overlap between the pink and yellow masks. So §2's
pass/fail stands; only the whole-frame structural classes are withheld.

**Recommended remedy** (the method `w2_gate_preflight` §1.2 already validated): a same-session
A/B — `HEAD` with ground_kit vs `HEAD` with the `build_ground_kit()` call disabled — rendered back
to back. That is ~6 minutes of GPU and converts every withheld verdict into an attributable one.

---

## 6. GT-E4 hazard-off twins and the real-pair GRAZE floor

Twins rendered to `look_check/<scene>/w2_pilot_hoff/` — 4 cuts each
(`preset_h0.3_d{2,5,10}` + `preset_h0.9_d10`), same round, same material state:
`sceneN5` `hazard_flush_grating=false` (34 s), `scene15` `hazard_stairs=false` (22 s),
`scene13` `hazard_stairs=false` + `cue_tactile=true` (38 s).

Each pair was run through `regression_check.py` v2.1 in **both** directions —
hazard-off → hazard-on is "a drop appeared" (exposure), hazard-on → hazard-off is "a drop was
removed" (burial):

| scene | real drop | fired | deferred | silent |
|---|---|---:|---:|---:|
| `scene15` (stairs, 4.25 m) | yes | **0 / 8** | 0 | 8 |
| `scene13` (ramp, 3.96 m) | yes | **0 / 8** | 6 | 2 |
| `sceneN5` (flush grating) | **no — control** | **1 / 8** (false positive) | 0 | 7 |

**Real-pair detection rate = 0 / 16 = 0.0 %.** Ten of the sixteen were *adjudicated and silent* —
GRAZE actively concluded "no change" on cuts where a multi-metre drop appeared or vanished. The one
firing in the whole matrix is on the **no-drop control** (`sceneN5 hon→hoff h0.3_d2`, the same
pre-existing joint adjudicated in §2.2), i.e. the only signal GRAZE produced was a false positive.

**This is the answer to the supervisor's option (a), and it is not the answer option (a) expected.**
Re-deriving the injection floor from real pairs does not replace 65.8 % with a better number; it
returns **0 %** and thereby says the real-pair corpus cannot validate GRAZE at all. The honest
caveat is that the two experiments are not equivalent: the synthetic injection reveals a *local*
riser inside an otherwise identical frame, whereas a `hazard_*=false` twin is a **whole-scene
reconfiguration** (scene15 loses its stairs, its bend and its lower alley), so the checker's tone
normalisation and column-agreement machinery classify the change as content, not as an edge event.
**Conclusion: neither the synthetic 65.8 % nor the real-pair 0 % is a usable detection floor.** The
GRAZE checker currently has no validated sensitivity on this dataset, and W2-C must not rely on
GRAZE silence as evidence of edge integrity. A twin design that perturbs *only* the drop — e.g.
raising the lower level to close the drop while leaving all other geometry, materials and lighting
identical — is the experiment that would produce a real floor.

---

## 7. GO / NO-GO for W2-C (branch merge + T1 A/B)

### **NO-GO as stated. Conditional GO on four items.**

The kit is sound in structure — 33/33 hard gates, exit 0, prim budgets held, the GT hand-off works,
the P-A blocker is genuinely resolved with margin — but three of the round's findings would
propagate silently across 30 more scenes if spread began now.

| # | condition | why it blocks | cost |
|---|---|---|---|
| **C1** | **Merge `w2-surgeon` before any further ground round.** | The main tree renders flowering cherry in every cut (65k–109k px/frame). Every FRAME/structure verdict in this round is contaminated by it, and the fix is already written on that branch. | merge only |
| **C2** | **Re-baseline with a same-session A/B** (ground_kit ON vs OFF at the same `HEAD`) for the three pilots. | `r2_on` predates ten commits; FRAME/PHOTO/OCCL are currently unattributable, and §7.2 S4 makes OCCL the single strictest camera-burial check. Without this, the kit is spreading with its most safety-relevant gate unread. | ~6 min GPU |
| **C3** | **Rule on the recess model, then re-check σ_LF on one scene.** | `surface_top_z()` is my fix, not a spec decision: it trades geometric depth for tone. The alternative (splitting the slab around each groove) is a §6.3-class change. Also `scene15` σ_LF is still 0.69 against a 5.0 WARN target, and the frame-fill objective is now shown to be **materially dependent on T1** (patches are bound to the floor material). §9.2 step 8's re-calibration should happen here, not after spread. | ruling + 1 render |
| **C4** | **Do not treat GRAZE silence as edge-integrity evidence** until a drop-only twin design exists (§6). | Real-pair detection is 0/16 with one false positive on the control. GT-E4's premise — that the twin is "the real test" — is not currently met by the tool. | design + re-run |

**Safe to proceed now, independent of the above:** T1's own A/B (`detail_texture_scale`,
`detail_rough_gain`), because the pilots are stamped at a verified detail-unwired state and the
ordering constraint P3 is satisfied — the P-A A/B is measured and committed **before** any detail
normal is wired.

### Defect list carried to W2-C

| # | defect | severity | evidence |
|---|---|---|---|
| D1 | Cherry blossoms in main tree (`scene_common.py:1715`) | **blocking** | §5, pixel counts |
| D2 | `scene13` d2 OCCL 21.0 % / blob 19.5 % — cause unattributed | **blocking until C2** | §5 |
| D3 | Weeds render as solid axis-aligned boxes (olive cubes) | high — visible at d2/d5 in two scenes | `w2_pilot_crop/tactile_band.png`, `scene15` d5 |
| D4 | Manhole discs are visibly polygonal at near range | medium | `scene13` d5, `sceneN5` d2 |
| D5 | `B9` checks a *declared* albedo while scenes bind any material — `scene15` manhole is near-white with a declared albedo of 0.10 | medium — the gate can pass on a value the render contradicts | §3.1 |
| D6 | `sceneN5` double joint grid (scene + kit, co-located) | low — 5 redundant prims | §2.3 |
| D7 | Spec §5.3 gate 13-1 is geometrically unsatisfiable in h0.3 cuts | doc fix | §4 |
| D8 | Spec §12.3 d5 `EXPECTED_FP` sample superseded → `(348, 371)` @1080 | doc fix | §1.1 |
| D9 | \|∇\| p99 definition in §1.4 is unreproducible; 0.30 is a 100 %-of-look-OFF line while its neighbours are 75 % | ruling | §2 |

---

## 8. Commits

| hash | scene | contents |
|---|---|---|
| `e196c93` | `sceneN5` | ground_kit.py (new) + symlinks + `scene_common` P-A + `sceneN5`; row-scale fix, `EXPECTED_FP` dual axis, apply-layer material guard |
| `cb40ae8` | `scene15` | manhole W1→W2 re-placement; `surface_top_z()` recess fix, manhole flush fold, burial guard |
| `753b791` | `scene13` | entry trench 0.35→0.52, lane lines 0.6→0.80, `cue_tactile` ON round, baseline-invalidity evidence |

`python3 ground_kit.py` exits **0** at every commit: 33/33 hard gates, 1,333 geometry prims,
1,040 scatter instances, 33-scene apply round-trip clean, burial guard 0.

## 9. Reproduce

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh && conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

python3 ground_kit.py                       # CPU self-check, exit 0
python3 scripts/near_ground_stats.py 'look_check/scene15/w2_pilot/pt_noon_preset_h0.3_d*.png'
python3 scripts/regression_check.py --before look_check/scene15/r2_on \
        --after look_check/scene15/w2_pilot
# twins, both directions
python3 scripts/regression_check.py --before look_check/scene13/w2_pilot_hoff \
        --after look_check/scene13/w2_pilot --only preset_h0.3
```

Round driver (with the P3 stamp in its header) and the N5 metric script live in the session
scratchpad; `round_stamp.json` is written into every capture directory. All image artifacts are
under `look_check/**` (gitignored).
