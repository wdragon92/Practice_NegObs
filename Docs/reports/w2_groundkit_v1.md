# W2-A3 — `ground_kit.py` implementation + pilot scene integration

Author: W2-A3 (MAIN tree) · Date 2026-07-29 · Spec: `Docs/briefs/ground_kit_spec_v1.md` **v1.1**
Mode: **CPU only** — no GPU, no render, no Isaac, no `NEGOBS_SMOKE` (M6 reserves SMOKE for the
GPU-owner agent). Every number below is `[measured]` from code/PNG, `[calc]` from the frame model,
`[law]`/`[spec-doc]` from statute or KCS, or `[assumed]` with the reason stated.

---

## 0. Result in one paragraph

`ground_kit.py` (2,627 lines) is implemented at repo root with symlinks in `scenes/main/` and
`scenes/batch1/`. It re-exports `infra_kit`'s `Kit` / `det_seed` / `det_rng` / `_bay_joints` /
`kit_from_scene_common` / `dry_kit` (no reimplementation), carries the `GROUND_DIMENSIONS` ledger
including the `unit_cell` reverse contract, defines **19 profiles** (18 from §4.1 incl. P18
`deck_trail_hybrid`, plus the `tunnel_under` sub-variant), the **15 new sub-builders** of §4.3, and
the three API layers `plan_ground` / `frame_budget` / `apply_ground` with gates **B1–B12**.
`python3 ground_kit.py` **exits 0**: it dry-runs all 33 scene plans, asserts prim budgets,
`GT_DELTA = 0.020`, opening intersections 0, and passes hard gates B6–B12 on 33/33 scenes.
`scene_common.py` received exactly the W2-0 P-A addition (`SKIN_EXCLUDE`, `skin_exclude()`, one
guard line at the top of `_skin_wanted`, `"gkit"` in `_SKIN_DENY`) and nothing else. Three pilot
scenes (N5, 15, 13) are wired. **Seven spec defects/conflicts were found during implementation**
and are listed in §6 — two of them need a supervisor ruling before the GPU phase.

---

## 1. Files touched (only my assignment)

| File | Change | Lines |
|---|---|---|
| `/home/vislab/Desktop/work_sy/Practice_NegObs/ground_kit.py` | **new** | 2,627 |
| `/home/vislab/Desktop/work_sy/Practice_NegObs/scenes/main/ground_kit.py` | symlink → `../../ground_kit.py` | — |
| `/home/vislab/Desktop/work_sy/Practice_NegObs/scenes/batch1/ground_kit.py` | symlink → `../../ground_kit.py` | — |
| `/home/vislab/Desktop/work_sy/Practice_NegObs/scene_common.py` | W2-0 P-A only | +20 / −1 |
| `/home/vislab/Desktop/work_sy/Practice_NegObs/scenes/batch1/sceneN5_flush_grating.py` | pilot | +64 / −5 |
| `/home/vislab/Desktop/work_sy/Practice_NegObs/scenes/main/scene15_alley_labyrinth.py` | pilot | +69 |
| `/home/vislab/Desktop/work_sy/Practice_NegObs/scenes/main/scene13_apartment_parking_entry.py` | pilot | +78 |

No git operations were performed. `assets/NegObsGround.mdl`, `assets/download_vegetation.py`,
`scripts/regression_check.py` also show as dirty in `git status` — those are **other agents'** work,
untouched by me.

### 1.1 `scene_common.py` merge point (for the worktree agent who owns the rest)

Only two hunks, both self-contained; a worktree branch that edits other regions of
`scene_common.py` will merge cleanly unless it also edits these exact lines:

1. **Immediately above `def _skin_wanted(...)`** — inserts `SKIN_EXCLUDE = set()` +
   `def skin_exclude(*paths)` + comment block, and inserts the guard as the **first statement**
   of `_skin_wanted`:
   ```python
   if str(path) in SKIN_EXCLUDE or any(str(path).startswith(p)
                                       for p in SKIN_EXCLUDE):
       return False
   ```
2. **`_SKIN_DENY` tuple literal** — appended `"gkit"` (the only *modified* pre-existing line in
   the whole file).

Conflict risk is limited to those two anchors. `apply_ground` takes the exclude function as an
**injected callback**, so `ground_kit` still never imports `scene_common` (§3.1 preserved).

---

## 2. `python3 ground_kit.py` self-check — full output table

Exit code **0**. Column meaning: `prims` = geometry prims, `scat` = scatter instances (delegated to
`scene_common.scatter_debris`), `δmax` = max |Δz| over elements (weeds/scatter are the GT-E5 ramp
exception; scene13's 0.1200 is the **approved** M4 ramp curb), B1–B5 = best value over the 3 cuts
(advisory), `hard` = B6–B12 (blocking).

| scene | profile | prims | scat | δmax | B1 | B2 % | B3 | B4 | B5 | hard | WARN |
|---|---|---|---|---|---|---|---|---|---|---|---|
| scene01 | plaza_granite | 47 | 0 | 0.1182 | 1 | 46.8 | 2 | 0 | 2 | PASS | B4,B5 |
| scene02 | sidewalk_block | 48 | 0 | 0.1182 | 2 | 107.3 | 1 | 1 | 3 | PASS | B4,B5 |
| scene03 | levee_paved | 53 | 0 | 0.1182 | 1 | 100.0 | 0 | 2 | 1 | PASS | B3,B5 |
| scene04 | trail_soil | 9 | 320 | 0.0006 | 0 | 0.0 | 0 | 5 | 2 | PASS | B1,B2,B3,B5 |
| scene05 | plaza_granite | 46 | 0 | 0.1182 | 2 | 60.5 | 1 | 1 | 1 | PASS | B4,B5 |
| scene06 | bridge_deck | 29 | 0 | 0.0060 | 1 | 20.4 | 0 | 1 | 4 | PASS | B3,B4,B5 |
| scene07 | courtyard_dg | 9 | 400 | 0.0006 | 0 | 0.0 | 0 | 3 | 1 | PASS | B1,B2,B3,B5 |
| scene08 | sidewalk_block | 48 | 0 | 0.1182 | 1 | 57.7 | 1 | 1 | 3 | PASS | B4,B5 |
| scene09 | plaza_water | 26 | 70 | 0.0060 | 0 | 0.0 | 0 | 0 | 0 | PASS | B1,B2,B3,B4,B5 |
| scene10 | **deck_trail_hybrid (P18)** | 19 | 250 | 0.0200 | 0 | 0.0 | 4 | 5 | 2 | PASS | B1,B2,B5 |
| scene11 | bridge_deck | 32 | 0 | 0.0060 | 1 | 17.3 | 0 | 0 | 0 | PASS | B2,B3,B4,B5 |
| scene12 | deck_timber | 70 | 0 | 0.0200 | 0 | 0.0 | 8 | 1 | 3 | PASS | B1,B2,B4,B5 |
| **scene13** | **ramp_parking (pilot)** | **52** | 0 | **0.1200** | 1 | 51.0 | 1 | 2 | 0 | PASS | B5 |
| scene14 | plaza_granite | 46 | 0 | 0.1182 | 0 | 0.0 | 1 | 1 | 1 | PASS | B1,B2,B4,B5 |
| **scene15** | **alley_concrete (pilot)** | **47** | 0 | 0.1182 | 2 | 83.2 | 1 | 7 | 2 | PASS | B5 |
| scene16 | sidewalk_block | 49 | 0 | 0.1182 | 1 | 51.0 | 1 | 1 | 3 | PASS | B4,B5 |
| scene17 | levee_paved | 52 | 0 | 0.1182 | 1 | 100.0 | 0 | 2 | 1 | PASS | B3,B5 |
| scene18 | plaza_granite | 46 | 0 | 0.1182 | 0 | 0.0 | 1 | 1 | 1 | PASS | B1,B2,B4,B5 |
| scene19 | roof_membrane | 31 | 0 | 0.0020 | 1 | 25.1 | 0 | 1 | 1 | PASS | B3,B4,B5 |
| scene20 | plaza_granite | 47 | 0 | 0.1182 | 0 | 0.0 | 1 | 1 | 1 | PASS | B1,B2,B4,B5 |
| scene21 | plaza_granite | 46 | 0 | 0.1182 | 0 | 0.0 | 1 | 1 | 1 | PASS | B1,B2,B4,B5 |
| sceneC1 | plaza_granite | 47 | 0 | 0.0443 | 1 | 37.1 | 2 | 1 | 1 | PASS | B4,B5 |
| sceneC2 | sidewalk_block | 46 | 0 | 0.1182 | 0 | 0.0 | 0 | 1 | 3 | PASS | B1,B2,B3,B4,B5 |
| sceneC4 | sidewalk_block | 47 | 0 | 0.1182 | 1 | 74.2 | 1 | 1 | 3 | PASS | B4,B5 |
| sceneD1 | yard_industrial | 20 | 0 | 0.0030 | 0 | 0.0 | 1 | 5 | 3 | PASS | B1,B2,B5 |
| sceneD2 | slab_construction | 24 | 0 | 0.0030 | 0 | 0.0 | 0 | 1 | 5 | PASS | B1,B2,B3,B4,B5 |
| sceneD3 | verge_rural | 35 | 0 | 0.0939 | 0 | 0.0 | 0 | 0 | 1 | PASS | B1,B2,B3,B4,B5 |
| sceneD4 | platform_indoor | 10 | 0 | 0.0060 | 1 | 37.1 | 1 | 1 | 2 | PASS | B4,B5 |
| sceneN1 | plaza_granite | 47 | 0 | 0.1182 | 1 | 56.1 | 1 | 1 | 1 | PASS | B4,B5 |
| sceneN2 | street_asphalt | 50 | 0 | 0.0939 | 1 | 56.1 | 0 | 3 | 1 | PASS | B3,B5 |
| sceneN3 | plaza_granite | 47 | 0 | 0.1182 | 0 | 0.0 | 1 | 1 | 1 | PASS | B1,B2,B4,B5 |
| sceneN4 | ramp_road | 58 | 0 | 0.0939 | 2 | 200.0 | 0 | 5 | 2 | PASS | B3,B5 |
| **sceneN5** | **sidewalk_block (pilot)** | **50** | 0 | 0.1182 | 1 | 66.0 | 1 | 1 | 2 | PASS | B4,B5 |

**Totals**: 33 scenes · hard gates 33/33 · **1,333 geometry prims** · **1,040 scatter instances**.
Spec §8.2 estimated ≈1,150 + ≈1,000 `[calc]` — the +16 % on prims comes from crack polylines
(§6.4) and is inside every cap (per-profile ≤ 60/140, absolute ≤ 200).

Other self-check sections that pass: camera constants reproduce the spec's Appendix B exactly
(`f = 1662.769`, `row(2.0) = 497.35`, `row(10.0) = 297.97`, `drow(−0.95,10) = 5.34`,
`drow(−2.40,10) = 16.05`, `drow(−0.30,5) = 6.42`); unit-cell rules U1–U4 across all profiles;
tactile registry counts (`K_h = 9`, `K_n = 4`, `P(tactile|hazard) = 0.321`); `EXPECTED_FP` row
derivation; four negative tests that the conventions really do raise `ValueError`
(natural + urban infra, unregistered tactile, prefix without `GKit`, positive-relief joint);
and an `apply_ground` dry round-trip proving plan prims == apply prims and that **every** prim
lands under `{ROOT}/GKit`.

### 2.1 On B1–B5 being advisory

Spec §7.1 lists B1–B12 in one table but only §9.2 step 1 names the self-check's blocking set
("prim count, GT assertions, opening intersections 0, B11, B12"). B1–B5 are *frame-fill targets*
whose real verdict is the post-render σ_LF/sd gate, which §7.1 itself keeps at **WARN for W2**.
Implementation therefore treats **B6–B12 as hard** (`plan_ground` raises) and **B1–B5 as WARN**.
Natural profiles (P11/P12/P18) structurally cannot satisfy B1/B2 — they have no area elements by
regulation (no manholes/gullies in nature scenes) — so a hard B1 would kill the spec's own
prescription. B5 (≥6 stain decals with X ≤ 3 m) fails almost everywhere: reaching it needs ~22
decals per corridor, versus the §8.2 per-profile allowance of 4–12. **B5's threshold is
`[assumed]` in the spec and is not reachable inside the prim budget** — recommend re-deriving it
from n≥30 real samples together with the σ_LF/sd re-calibration at step 8.

---

## 3. What was built

### 3.1 Layer 1 — ledger and registries
`GROUND_DIMENSIONS` (46 keyed 3-tuples `(value, "확인|추정", source)` in `infra_kit` format) plus
`GROUND_DIMENSIONS["unit_cell"]` = the §4.5 reverse contract, **one row per profile**, each
`(cell_m, (ox, oy), source)`. `_assert_unit_cell()` enforces U1 (cell == `pave.module`),
U2 (`step_x`/`step_y` an integer multiple of the cell), U3 (origin present — "period without
origin is contract breach"), U4 (`cell = None` ⇒ jitter forbidden). Also `TACTILE_SITES` (13
scenes), `TACTILE_OFF_REASON` (19 scenes — the code remembers *why* a site is empty, and B11's
error message prints it), `EXPECTED_FP` (16 entries, derived not hardcoded — see §6.3),
`GROUND_INVARIANTS` (B12 callables for N1, N3, 14, 20, 21, 13, 10, C1), and `SCENE_PLANS`
(the 33-scene self-check **fixture**, explicitly *not* the integration coordinate source per §7.4).

### 3.2 Layer 2 — `plan_ground` / `frame_budget`
`plan_ground` composes an op list from the profile, runs every op against `dry_kit()` to obtain
elements + prim counts **without touching USD**, applies the GT-E5 height clamp to
vegetation/scatter, then runs `frame_budget` and raises on any hard-gate failure. `frame_budget`
implements the camera model as hardcoded constants and judges each `h0.3` cut.

### 3.3 Layer 3 — `apply_ground`
Re-runs the identical ops against the real `Kit`, injects `skin_exclude` (P-A) and `scatter`
(`scene_common.scatter_debris` — no new scatter function, per §4.3), refuses any `prefix` without
the `GKit` token, hard-clamps albedo (0.30; 0.55 for tactile) and re-checks GT δ **before**
creating anything. Returns `{prims, instances, elements, gt_delta_max, gt_change_max, gt_changes,
materials_needed, unit_cell}`.

### 3.4 The 15 new sub-builders (all geometry)
`build_joint_grid`, `build_slab_joints`, `build_patch_field`, `build_crack_lines`,
`build_trench_drain`, `build_gutter_U`, `build_groove_band` (**0 prims** — emits a
`materials_needed` request to T1, geometry fallback available), `build_membrane`,
`build_stain_field`, `build_footprints`, `build_wear_lane`, `build_edge_litter`,
`build_edge_break`, `build_deck_planks`, `build_silt_band`. Six `infra_kit` builders are wrapped
by thin `_ik_*` adapters that only attach planning metadata — **no geometry is reimplemented**.

---

## 4. Pilot integrations (no render performed)

### 4.1 `sceneN5_flush_grating.py` — P-A proof setup (+64 / −5)
* `import ground_kit as gk`; new `PARAMS["ground"]` block.
* **P-A**: `sc.skin_exclude()` is called **before** each `add_box` for `Pave_S`, `Pave_N`,
  `Pave_Fill`, `Roadway`. Ordering matters — `add_box` evaluates `_skin_wanted` inline, so
  post-hoc registration is too late. This is the change that un-buries the existing manholes,
  joints and tactile pads.
* **New near-window manhole at (−1.15, +0.30)**, flush, `d_frame = 0.648`, `proud=None`
  (deterministic ±10 mm per KS D 4040). Screen width at d2 = `f·0.648/0.85` = **1,267.6 px =
  66.02 % of frame width** `[calc]` — reproduces the spec's 1,268 px figure to 0.4 px.
* Tactile material rewired from a flat constant colour to the **`tactile` texture role**
  (`tactile_yellow_diff.png` / `tactile_yellow_nor.png`, already registered in
  `scene_common.TEX` but unused) — §12.5 cause ③.
* Bollard-front tactile now goes through `infra_kit.build_tactile_pair` orchestrated by
  `ground_kit` (M11), as a **0.60 m continuous band over x 4.0…11.0** replacing the 5 separate
  0.40×0.30 pads (§12.5 cause ②: 0.12 m²/post → 4.2 m² = 35×).
* Plan: 50 prims, hard gates PASS, WARN B4/B5.

### 4.2 `scene15_alley_labyrinth.py` — 8-element alley fill (+69)
All eight §5.4 elements: 15-1 transverse construction joints (step 3.0 m, width 0.010, recess
−3 mm — the profile authors `groove_w`/`recess` exactly as the §3.4 schema example does; `x = 0`
is auto-dropped by the edge guard), 15-2 manhole, 15-3 wall-side covered U-gutter at y = −0.75,
15-4 two repair patches, 15-5 wall/floor grime bands, 15-6 stair-foot linear grating, 15-7
cracks, 15-8 weeds. Tactile: **none** (§12 — alley p ≈ 0.05, sample 0/12).

* **M9-ⓑ executed**: the manhole moved from x = −1.15 to **x = −4.00** (d5 window). At d2 the old
  position occupied 1,268 px = 66.0 % of frame width and rows 666–1080; at d5 the new position
  is 280 px = 14.6 % `[calc]`. The d2 window's B1/B2 is now carried by repair patch #1 at
  **x = −1.20** (1,663 px, 86.6 %) — still one dominant element, but a flat tone patch rather
  than a black cast-iron disc.
* 15-6 is built with a **separate `build_trench_drain` call inside the 25° `rot_group`** because
  the lower alley lives at local x = 9.3, z = −4.25 — a different frame from the upper-alley plan.
* `sc.skin_exclude(f"{ROOT}/UpperAlley")` before the slab box.
* Plan: 47 prims (+2 for the grating), hard gates PASS, WARN B5 only. Longitudinal-line count
  reaches 7 at d10 (B4 ≥ 2 satisfied with margin) — the U-gutter + covers + grime bands.

### 4.3 `scene13_apartment_parking_entry.py` — ramp curb + entry asphalt (+78)
* **13-1 ramp curb h 0.12 / w 0.30 executed** via `infra_kit.build_ramp_curb` with the scene's own
  `ramp_profile()` segments — **6 prims** (3 segments × 2 sides), matching `infra_kit`'s self-check.
  The v1 `offset` argument does not exist (v1.1 correction B5); the call uses
  `(profile, y_neg=-3.0, y_pos=3.0, height=0.12, width=0.30, sides="both")`.
* **M4 hand-off**: the curb is the only element allowed to exceed `GT_DELTA`. It carries
  `exc="gt_change"`, and `apply_ground` **refuses to build it unless a matching `gt_changes` record
  exists** — an unlabeled drop cannot be created silently. The scene prints, at build time:
  `[GT 인계 · W4] scene13 ramp_curb 낙차 0.120 m 신설 — 라벨 담당 W4.` and the record
  `{"scene": "scene13", "item": "ramp_curb", "drop": 0.12, "label_owner": "W4", "note": …}`
  is returned in `gt_changes` for W4's GT drop map (§6.4, §9.2 step 7).
* **13-8 entry asphalt x −14…0** is the 3-cut workhorse: construction joints @3 m, 2 patches,
  6 cracks, tire-polish stains, weeds, and **manhole in the d5 window**.
* **Ramp-top elements are d2-only, enforced by geometry not by annotation**: the edge is declared
  as `("ramp_crest", 0.0, {"beyond_grade": 0.085})` and `plan_ground` marks any element beyond it
  visible only where the grazing ray slope `h/d` exceeds the transition grade —
  d2: 0.150 > 0.085 **visible**; d5: 0.060 **hidden**; d10: 0.030 **hidden** `[calc]`.
  Invariant `_inv_13_ramp_d2only` (B12) then asserts it. 13-3 entry trench (x = +0.35), 13-4 sump
  trench (x = 23.4), 13-5 lane lines and the curb all resolve to `vis_dists = (2,)`.
* 13-2 grooving emits **0 prims** and a T1 `groove_stripe` material request over x 3.6…20.4
  (§4.4 — geometry would cost 140 prims on a 17 m ramp).
* Manhole at **(−3.90, 0.00)**: y = 0 because at the d5 near-window the frame half-width is only
  0.64 m, so the §5.5 "d5 window" manhole cannot sit at y = 1.6; x = −3.90 clears both DriveLine
  dashes (−6.05…−4.55 and −3.45…−1.95) and the tire-polish bands (|y| 0.575…1.125), so no
  z-fighting.
* Tactile is wired for the registered `bollard` site but stays behind the scene's existing
  `cfg["cue_tactile"]` toggle (currently `False`) — see blocker §7.4.
* Plan: 52 prims, hard gates PASS, WARN B5 only, `δmax = 0.1200` (the approved curb).

---

## 5. Expected gate values for the GPU phase

These are the numbers the GPU-owner agent should assert. Pass/fail thresholds come from spec
§1.4, §12.5 and §7.1; predicted values come from this implementation's CPU plan.

### 5.1 `sceneN5` — P-A A/B (the blocking verification, spec §9.2 step 4)
Compare `look_check/sceneN5/r2_on/` (skin ON, current) against a fresh render with P-A active.
Material state must stay `r2_on` (MDL v1.8.0, detail normals **not** wired) — constraint P3.

| # | Metric | ROI / cut | Current (skin ON) | **Pass line** | Source |
|---|---|---|---|---|---|
| N5-1 | dark-pixel fraction | `manhole_pair`, px 500–1100 × 350–750 | 0.02 % | **≥ 4.5 %** (75 % of ctx2's 5.88 %) | §1.4 |
| N5-2 | \|∇\| p99 | same ROI | 0.079 | **≥ 0.30** | §1.4 |
| N5-3 | strong-yellow pixels | `approach`, `sat>0.40 ∧ (r−b)>0.25 ∧ (g−b)>0.15` | 118 px | **≥ 1,500 px** (72 % of ctx2's 2,090) | §1.4 sub-test |
| N5-3b | same, after §12.5 ②③ (band + texture) | `approach` | — | target **≥ 8,000 px (0.39 %)**, re-derive after render | §12.5 |
| N5-4 | `regression_check.py` DARK/BLOWN | all cuts | — | **FAIL 0** | §1.4 |
| N5-5 | OCCL — largest new dark blob | h0.3 ×3 | — | no new blob (camera-burial symptom) | §7.2 S4 |

Geometric predictions to cross-check against the render:
* new manhole at d2: outer diameter spans **1,267.6 px** horizontally (66.0 % of 1920) `[calc]`;
  at d5 **279.9 px** (14.6 %); at d10 **122 px** (6.3 %).
* the near-window manhole's top row is `row(0.85) ≈ 1080` (bottom of frame) and it reaches up to
  `row(1.174) = 663` `[calc]` — i.e. the lower ~39 % of the frame.

### 5.2 `scene15`
| # | Metric | Cut | Pass line |
|---|---|---|---|
| 15-1 | σ_LF (bottom 30 %, 64× down-sample, ×100) | h0.3 ×3 | **≥ 5.0** (WARN gate; current alley has 0 ground elements) |
| 15-2 | sd (bottom 45 %) | h0.3 ×3 | ≥ 32 (WARN) |
| 15-3 | d2 area coverage | h0.3_d2 | patch #1 ≈ **1,663 px wide (86.6 %)**, manhole absent (M9-ⓑ) |
| 15-4 | d5 area coverage | h0.3_d5 | manhole **280 px (14.6 %)** + patch #2 → B2 = 83.2 % |
| 15-5 | GRAZE, hazard-off twin | all | no new edge response outside `EXPECTED_FP` (scene15 has no tactile ⇒ **no FP registration at all**) |
| 15-6 | white % / >224 % | bottom 45 % | ≤ 2 / ≤ 5 |

### 5.3 `scene13`
| # | Metric | Cut | Pass line |
|---|---|---|---|
| 13-1 | ramp curb visible | h0.3_d2 only | curb top edge present at d2; **absent at d5 and d10** (crest occlusion — this is the scene's hazard) |
| 13-2 | approach asphalt σ_LF | h0.3 ×3 | ≥ 5.0 (WARN) |
| 13-3 | d5 manhole | h0.3_d5 | **981 px (51.1 %)** at X = 1.1 m `[calc]` |
| 13-4 | entry trench | h0.3_d2 | one full-width transverse line, Δ = **24.7 rows** from the crest row (≥ 16) `[calc]` |
| 13-5 | GT map hand-off | build log | one `gt_changes` record, drop 0.120, owner W4 |
| 13-6 | OCCL | h0.3 ×3 | no new dark blob from the curb (it is 0.12 m and lateral) |

### 5.4 Tactile false-positive registry (applies to the 8 hazard-edge scenes)
`EXPECTED_FP` is populated for `scene01, scene02, scene08, scene11, scene13, sceneC1, sceneC4,
sceneD4` × {d5, d10} = **16 entries**. Rows: **d5 → (348, 356)**, **d10 → (297, 304)** for the
statutory band (edge − 0.30 m, depth 0.60 m). d2 is **not** registered — Δ = 42.9 rows there, it
passes GT-E2 on its own. The round judge must not count GRAZE responses inside those row spans as
new false positives (GT-E2-x conditions 1–3).

---

## 6. Spec defects found while implementing (all `[measured]`/`[calc]`)

### 6.1 §5.7 scene09 expansion joint 20 m violates the spec's own U2 rule — **resolved to 19.80 m**
`unit_cell["plaza_water"] = 0.600`; 20.0 / 0.600 = 33.333 → not an integer multiple → U2 failure →
double grid, exactly the artefact §4.5 exists to prevent. KCS 34 6-3 3.3.3⑻ states 20 m as an
**upper bound**, so 33 × 0.600 = **19.80 m** satisfies both. Ledger entry retagged `[calc]`.

### 6.2 §4.3 "4~6 prims per crack" contradicts §8.2's per-profile estimate — **took §8.2**
§8.2 P1 lists "patch+crack = 2+12" for `crack n=4`, i.e. **3 prims/crack**; P13 lists "4+15" for
`n=5`, again 3. Implemented **3 base / 5 branched**. With §4.3's 4–6 the 33-scene total would
exceed several per-profile caps (levee_paved measured 74 > 60 before the fix).

### 6.3 §12.3's `EXPECTED_FP` sample rows are internally inconsistent — **derived instead**
The sample gives `d5 → (348, 356)` and `d10 → (297, 304)`. Reconstructing: d5's pair spans
edge row 348.60 → **near** boundary 355.03; d10's spans edge row 297.98 → **far** boundary 303.02.
The rule that makes both correct is *"register from the edge row to the farthest boundary line
that fails Δ ≥ 16"* — at d5 the far line passes (Δ = 22.1) so it is excluded, at d10 both fail.
`tactile_fp_rows()` implements that rule and reproduces both sample pairs exactly. Hardcoding the
two samples would have been wrong for any scene with a different band depth.

### 6.4 §2.3's scene06 row is off by 0.564 m at both ends — **used the §2.2 definition**
For every other non-standard scene (11, 19, D1, D4) the §2.3 W1 coordinates match the §2.2
geometric definition (X ∈ [0.564, 2.00] ahead of the eye). scene06's row (`y −12.44…−11.0` at d2)
is what you get by pasting the standard scene's *offsets* (−1.44…0) onto a different origin; the
geometric answer is `y −13.00…−11.564`. Implementation follows §2.2. Low impact (scene06 is
spread-phase), but §2.3 should be corrected.

### 6.5 §5.5 13-1 "inner face ±2.60" implies width 0.40, not 0.30 — **built 0.30 → ±2.70**
주차장법 §6①5다 requires the curb's carriageway-side face to be **≥ 30 cm from the wall**. With
`width = 0.30` set against the wall at y = ±3.00, that face lands at ±2.70 and the law is met.
±2.60 would need a 0.40 m curb, which `infra_kit`'s docstring explicitly does not assume. Flagging
rather than silently widening, because the curb is a **GT drop** and its footprint feeds W4.

### 6.6 GT-E2's "≤ 1 full-width transverse line" cannot mean periodic joint grids — **scoped**
Taken literally it kills §5.1's own P1 prescription (1.8 m contraction joints put ~8 lines in the
d10 E-band). Implemented split: the **"≤ 1" count applies only to singular lines** (trench covers,
markings, tactile bands, grime bands — `line="cross"`), while the **Δ ≥ 16 row separation applies
to every line including each periodic joint** (`line="cross_periodic"`), with joints too close to
an edge dropped automatically. That is exactly what §5.4 15-1 does by hand ("x = 0 excluded, edge
no-go zone"), generalised. `plank_gap` elements are exempt from both, per §6.1's exception table
("deck plank gap: required standoff 0 — no occlusion") and §13.4's explicit ruling that the
nearest gap may sit at x = −0.145.

### 6.7 Two implementation bugs my own gates caught (recorded so they are not reintroduced)
* **Rotated-box AABB**: approximating a yaw-rotated strip with a square `max(L, w)` AABB inflated
  the forward extent and made scene13's entry trench appear *visible at d10*, inverting the whole
  point of C-2. Fixed with an exact OBB→AABB (`_obb_aabb`).
* **Lateral frame test**: `min(|t_a|, |t_b|) > halfwidth` discards any element that *spans* the
  frame — every full-width trench and tactile band vanished from the budget. Correct test is
  `t_a > +hw or t_b < −hw`.

---

## 7. Blockers / open items for the GPU pilot phase

1. **Tactile `relief="geom"` is arithmetically incompatible with the prim cap** (§12.5 ③ vs §8.1).
   A dot-relief band is 721 prims per 0.6 × 3.0 m; N5's bollard-front band is 7.0 m →
   **1,706 prims**, 8.5× the absolute cap of 200. W2 therefore ships `relief="normal"` (1 prim)
   plus the `tactile_yellow` texture wiring, which is the §12.5 ③ remedy anyway. **Supervisor
   ruling needed**: accept texture-only relief, or authorise a prim-cap exception for one
   short near-camera segment.
2. **`tactile_yellow_diff/nor` must be bound by T1 before N5 sub-test N5-3b is meaningful.**
   The files exist (`assets/scene01/tactile_yellow_{diff,nor}.png`) and the role is registered in
   `scene_common.TEX["tactile"]`; N5 now calls it, but the other 10 scenes using
   `scene_common.build_tactile` still pass a constant colour (M11 migration is scheduled at spread).
3. **Measurement tooling — resolved during this session by another W2 agent.**
   Spec §9.3 listed `near_ground_stats.py` / σ_LF / `norm_spec.py` as lost with the scratchpad.
   `scripts/near_ground_stats.py` (σ_LF + sd/mean/>224 %) and `scripts/norm_spec.py` now exist and
   parse cleanly. **Not verified by me** (I ran AST checks only, no PNG measurement) — the GPU-owner
   agent should confirm that `near_ground_stats.py` reproduces the spec's reference figures
   (e.g. scene10 h0.3_d2 σ_LF 3.03 / sd 22.4) before trusting §5's thresholds.
4. **`cue_tactile` remains `False` in scene13** (and 01/02/08/11/16). §12.4 lists these as
   "ON 신설", but flipping a scene toggle changes the dataset's cue/label quadrant balance, which
   §12.6 shows is unresolved (M10 pending). The ground_kit call site is wired and gated; flipping
   the toggle is a one-line change once M10 is decided.
5. **Pilot render order (constraint P3)**: N5 must be rendered **before** T1 detail normals are
   merged, otherwise the `|∇| p99 ≥ 0.30` line can be partly met without P-A and the A/B is
   confounded. If that ordering is impossible, stamp "material state = `r2_on` (MDL v1.8.0,
   detail unwired)" into the round script.
6. **hazard-off twins for the pilots** (N5, 15, 13) are required by GT-E4 — the first ground_kit
   round re-baselines GRAZE, so the twin is the only real edge-integrity check. 3 scenes × 4 cuts.

---

## 8. Reproduce (CPU only)

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs
python3 ground_kit.py            # 33-scene dry run + all assertions; exits 0
python3 -m py_compile ground_kit.py scene_common.py \
    scenes/main/scene15_alley_labyrinth.py \
    scenes/main/scene13_apartment_parking_entry.py \
    scenes/batch1/sceneN5_flush_grating.py
python3 -c "import sys; sys.path.insert(0,'scenes/main'); import ground_kit"   # symlink check
```
