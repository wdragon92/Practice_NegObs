# W2 fix batch — the one post-round fix pass and its re-render `260730_w2d_fix`

Author: W2 fix batch (MAIN tree, branch `feat/realism-v1`) · 2026-07-30 · GPU exclusive,
sequential single-instance renders, `NEGOBS_PT_FAST=1`, `MODE=pt`, arm `NEGOBS_LOOK_V1=1` +
`NEGOBS_DETAIL_SCALE=2` + `NEGOBS_DETAIL_ROUGH_GAIN=0` — **identical arm to the judge round**, so
every delta below is content, not settings.
Inputs: `tonglam_v2.md` (eyes verdicts, fix list F1–F5), `w2d_round_v1.md` (blockers B1–B3, gate
tables), `w2d_kitfix_v1.md`.
Every number is `[measured]` from a PNG or from code executed this session.

---

## 0. Verdict in one paragraph

**All three blockers are closed and no hazard gate moved.** The round is 33 scenes · 452 cuts ·
27.5 min · **0 non-zero exits**, and against the judge round `regression_check` v2.1 returns
**GRAZE FAIL 0 · WARN 0**, **OCCL 0 issues**, **PHOTO 0 issues**, and **12 FAIL cuts, every one of
them FRAME** — the block-occupancy class that the fix batch was *supposed* to move, and each of the
12 traces to a named fix (§3.1). B1+B3 (scene19 membrane) go from `flat_gnd` **94.81 → 0.03** with
`edge%` **0.7 → 76.1** and `w80` still 1.1 (bar: 40); B2 (scene11 plate) goes **53.12 → 9.23** with
`edge%` **3.3 → 63.1**. The F1 audit found the family had **one** cause — the kit's ground-class
decal materials fell to look classes that are excluded from texture promotion **by design** — so the
fix is a classifier entry plus a binding correction, not 33 hand-tunings, and it is now guarded by a
reusable check (`scripts/const_color_audit.py`, 139 ground-class wirings, violations 0). The one
place the round pays is **σ_LF**: clearing drops 11/33 → 9/33 because scenes 07 and 10 lose the gate.
That is not a regression of the ground — in both scenes `edge%` **rises** (07: 64.6 → 90.3, 10: 78.6
→ 84.3) while `flat_gnd` stays under 1.0. The σ_LF those two scenes were scoring came from the
boulder field and the 12 mm leaf rims, i.e. **from the defect F2/F3 were sent to remove**; this is
the same adjudication `w2d_round_v1.md` §4.4 already applied to scene08's −20.55. One iteration was
spent, on scene17 (§2.4).

---

## 1. What was applied — F1 to F5

CPU self-check after each, in the order below. No spec text was edited. The W3 exclusion list
(scene14 V-notch, sceneC2 leaf boundary, sceneD4 ground) was not touched.

### F1 — the constant-colour material family

**Cause, stated once.** `tonglam_v2.md` §2.13-1 grouped seven symptoms (scene19 membrane, scene11
plate, sceneN2 crack ribbons, N1/N3/N4/N5 grey mats, scene20 white patches, scene18 ghost
rectangles) as "one binding/tone code path". The audit confirms they are literally one path, and it
is not a bug in the material factory — it is a **classification miss**:

* `scene_common.make_pbr` routes a constant-colour material to the NegObsGround MDL (and then to
  texture promotion) **only if its look class is in `_CONST_MDL_CLASSES`**. `paint`, `metal`,
  `glass`, `water`, `sign` and `misc` are excluded *deliberately* — for lane paint, a steel rail or
  a joint sealant a constant colour is physically correct (v5.1 §4).
* The kit's ground-class decal roles were bound to exactly those classes. `Coating` (scene19's roof
  membrane), `GKitStain`, `GkWear`, `GKitSalt` matched **no `_LOOK_RULES` keyword at all** and fell
  to `misc`; N1/N2/N3/N4/N5 bound `crack` and `stain_*` to their `Joint` sealant material (`paint`);
  scene11 bound `crack` to `Steel` (`metal`) and its whole wear/stain set to `Band` (`paint`);
  scene20 bound `wear`/`stain_*` to `Curb`; sceneC4 to `Tide` (`water`); sceneD1 to `BandBlack`
  (`paint`) and `Rubber` (`misc`); scene09 to `Seam` (`water`); scene16 to `Band` (`paint`).
* A ground prim bound to one of those gets **no texture, no bevel, no detail normal** — a dead
  plane. scene19's membrane is the extreme: `flat_gnd` 94.8, `edge%` 1.4.

**Fix, in three parts.**

| # | where | change |
|---|---|---|
| F1-a | `scene_common._LOOK_RULES` | ground-decal vocabulary added to the (last, widest) `concrete` bucket: `coating · membrane · stain · wear · crack · silt · efflor · salt`. Ordering is safe because `concrete` is last — `StoneStain` still resolves stone, `Asphalt` still asphalt, `GkMoss` still veg `[measured]`. |
| F1-b | 14 scenes | ground-class decal roles rebound to two new ground-class materials, `Looks/GKitCrack` (0.055 dark, cracks / cut lips) and `Looks/GKitStain` (0.20, wear / stains / silt) — both classify as concrete and promote to `concrete_floor` with the intended albedo preserved. Scenes: 09 · 11 · 16 · 18 · 20 · C4 · D1 · D2 · N1 · N2 · N3 · N4 · N5 (+19 via F1-a alone). |
| F1-c | `scene_common.LOOK_CLASS["veg"]` + `_promote_const_to_texture` | new per-class `max_spread`, applied **only when the promotion brightens**. `veg` gets 3.0. |

**F1-c is the scene11 "shrub" item, and the diagnosis differs from the eyes' guess.** The
grey-lilac ball clusters are not Rhododendron hulls — they are scene11's `TreeBand`/`TreeBlob`
prims bound to `Looks/LeafFar{A,B,C}`, the three low-saturation grey-greens the v7 ruling added for
aerial perspective. The grass texture's blue channel is nearly empty, so those constants promoted
with per-channel multipliers of **(1.29, 0.94, 2.87) / (0.95, 0.74, 2.22) / (1.63, 1.11, 3.79)**
`[measured]`: the *mean* colour is preserved exactly, but the per-pixel blue is amplified up to
3.8×, turning grass-blade noise into lilac speckle — which reads as granite. The old guard
(`spread <= 4.0`) let all three through at 3.04 / 3.02 / 3.41. Capping veg at 3.0 **only when the
promotion brightens** rejects exactly those three and changes nothing else in the library: sceneC2's
`CanopyA` has a wider spread (3.34) but darkens (max ratio 0.94), so it keeps its texture `[measured
— full-corpus simulation, 60 promoted veg constants]`. The three rejected fall back to constant-MDL
green — correct hue, and the tree band is W3 scope anyway.

**scene19 also carried a declared-vs-bound defect (B3).** The scene's own comment cites the
director-approved band 0.16–0.22 and `GROUND_DIMENSIONS["membrane_albedo"] = 0.19`, but bound
`(0.115, 0.150, 0.120)` = luminance **0.1405**, i.e. below its own declaration. That is why the
de-whitened membrane collapsed to near-black in building shadow (`entry_gate` −47, `upper_approach`
−57). Rescaled to luminance 0.19 keeping the green hue exactly: `(0.155, 0.203, 0.162)`. This is a
bug fix against the declaration, not a spec change.

### F2 — D-5 rock scatter (04 · 07 · 10)

All four levers from `tonglam_v2.md` §2.6, and one of them needed a mechanism change:

* **scale** — `scale_jitter` `(0.75, 1.25) → (0.38, 0.62)`, taking the pool's native 0.16–0.24 m
  stones to φ 0.06–0.15 m, inside the `φ ≤ 0.12` the trail statistic describes. The parameter
  existed on the callback but ground_kit never passed it; `_scatter_pool_kw` now does.
* **burial** — the old `sink = zmax − expose` could not survive a rescale. `scale_mul` is authored
  as a scale op *after* the translate, so `sink` is an absolute offset that does not follow the
  instance size; shrinking the rocks under a fixed `sink` would have swallowed them. Replaced by a
  **burial fraction**: since the asset origin is the rock centre,
  `burial = 0.5 + sink / (2·zmax·scale)`, so `sink = (burial − 0.5)·2·zmax·s_mean`. `burial = 0.38`
  gives 12–42 % buried across the pool (mean ≈ 35 %) and, being a 4 mm *lift*, cannot float even the
  smallest stone.
* **count** — profile `cover`/`count` cut (P11 0.18/250 → 0.10/150 · P12 0.14/330 → 0.09/200 · P18
  0.12/180 → 0.08/110) plus scene overrides (07 `gravel_n` 270 → 180, 10 120 → 85). Note the
  binding lever differs per scene: 04 was count-limited, 07 and 10 were cover-limited.
  **Applied instances 591 → 391** `[measured, render log]`: 04 250 → 150 · 07 223 → 153 ·
  10 118+18 → 88+18.
* **albedo** — the procured rock basecolor measures linear **0.23**, already inside the
  "grey debris 0.18~0.30" convention, so the "near-white" read is size-and-sun, not albedo. A
  dulling hook was still added and used: `scatter_debris(mtl=...)` binds a material over the
  instance with `strongerThanDescendants` (needed because `/Asset` is instanceable), and 04/07/10
  bind a new `Looks/GkRock` — the real gravel texture at 0.30 m tiling, tint 0.82 → linear ≈ 0.19,
  the middle of the band. No binding failure logged in any of the three `[measured]`.

### F3 — decal rectangle boundaries

* `build_patch_field(cutline=...)` **defaults to False**. The four 20 mm strokes it laid round each
  patch perimeter are the "drawn dark outline frame" of 10 / D3 / 03. No caller ever passed the
  flag, so this switches the whole library off at once; the argument stays.
* `build_patch_field(yaw_max=14°)` and `build_stain_field` yaw ±22° on the **non-directional**
  kinds only — `grime_band` (a wall junction) and `tire` (a wheel track) stay axis-aligned. The AABB
  handed to `_elem` is the exact rotated one (`_obb_aabb`), so region containment and the GT-E2
  verdict see the true footprint.
* scene07 `leaf_band["proud"]` **0.012 → 0.004** and scene10 `leaf["proud"]` **0.012 → 0.005**: a
  12 mm vertical rim round each drift *is* the "edge shadow" that made the leaf masses read as
  carpets laid on the DG.

### F4 — scene17 grass plane

Two levers; the second was the iteration (§2.4).
`Looks/GrassC` and `GrassD` added with a **hue-ratio** break (0.57,0.65,0.36 sun-bleached /
0.46,0.60,0.42 shaded — the two existing tints differed by 5 % *along the same channel ratio*, i.e.
a brightness step, not a hue step) and a **tile-size** break (`scale_m` 1.05 / 1.85 against the
uniform 1.4), dealt out over `Terrace`, `FarBank`, `FlatFill` and a 3-way `Slope_{i}` alternation —
per large prim, never between adjacent ramp steps (the striping the v6 note warns about).

### F5 — manholes, pan-scene

* **Silhouette.** D4 was never a modelling choice: every manhole disc is an analytic
  `UsdGeom.Cylinder`, which Hydra tessellates at its own low default — hence the octagon and the
  12-gon. New `scene_common.add_disc()` emits an n-gon prism as **one `UsdGeom.Mesh`**, so the
  segment count is explicit at **32** (bar: 24) and **no prim or instance budget moves**. Wired
  through a new `infra_kit.Kit.D` (degrades to `Kit.C` if no `disc` helper is injected) into
  `build_manhole`'s frame / lid / boss, plus the scene-local triple-disc manholes of N2 and N5. The
  pit keeps a cylinder — it is a hole below the surface, never seen in silhouette.
* **Albedo.** `ground_kit._ik_manhole` *declares* 0.10 to gate B9, but B9 only ever sees the
  declaration — the scene binds what it likes, and eight scenes bound their stainless handrail
  constant: 01 · 02 · 08 · C1 · C4 at **0.72–0.85**, 17 at 0.66, 05 at 0.33, 15 at 0.30
  `[measured]`. A `Looks/GKitIron` at **(0.10, 0.10, 0.105)**, metallic 0.55, is now defined in
  01 · 02 · 05 · 08 · 15 · 17 · C1 · C4 · N1 · N3 · N4 and bound to `manhole`/`gully`. 18 and 19
  already had one; 13 · 14 · 16 · 20 · 21 · N2 · N5 already bound dark materials.

---

## 2. Verification `[measured]`

### 2.1 CPU, before the render

| check | result |
|---|---|
| `py_compile` | 6 kit/common modules + 33 scenes + `const_color_audit.py` — OK |
| `python3 ground_kit.py` | **exit 0** · hard gates B6–B12 **33/33** · apply-prims = plan-prims 33/33 · unsubstituted material refs 0 · geometry prims **1393 → 1233** (the cutline removal) · scatter instances **740** |
| `scripts/geom_invariance_check.py` | R-5 PASS · **R-4 33/33** · **R-6 33/33** · exit 0 |
| `scripts/valset.py --check` | exit 0 — all three corpora reproduce `w2_tools_v1.md` §4.4 to the digit |
| `scripts/const_color_audit.py` | **139 ground-class wirings · violations 0** |

### 2.2 `scripts/const_color_audit.py` — the new, reusable instrument

Written because F1's rule ("no texture-less constant on any ground-class prim") had no check and
would silently rot. It needs no render: it AST-parses every scene into `M["key"] → (Looks name,
textured?, constant colour)`, parses `M2.update(role=M["key"])` into the kit-role wiring, then for
every **ground-class role** (`patch · crack · wear · silt · litter · edge_break · debris ·
membrane* · groove · stain_*`) resolves the class through `scene_common._look_spec` and simulates
`_promote_const_to_texture` to get the final mode. Two failure conditions:

1. mode `FLAT-OMNI` — a ground prim carrying a texture-less constant;
2. bound albedo **> 0.30** — the "grey debris 0.18~0.30" / no-pure-white convention.

Roles where a constant is physically correct (`joint`, `marking`, `tactile`, `manhole`, `gully`,
`trench*`, `deck`, `weed`, `curb`) are excluded by name, and the exclusion list is in the file.
**It earned its keep on first run**: after the planned F1 edits it still returned 10 violations in
scenes the eyes round never named — sceneC4 (`stain_dirt`/`stain_gum` on `Tide`, water class),
sceneD1 (`crack`/`stain_oil` on `BandBlack`, `stain_tire` on `Rubber`), sceneD2
(`stain_efflorescence` on `Panel`, **albedo 0.39**), scene09 (`crack` on `Seam`), scene16
(`crack`/`stain_gum` on `Band`), and sceneN5 (`crack` — a rebind I had simply missed). All 10 fixed;
`sceneD2` also got a `Looks/GKitSalt` at 0.28 so the efflorescence sits under the albedo cap.

### 2.3 The round

| | |
|---|---|
| round | `look_check/<scene>/260730_w2d_fix/` |
| scenes / cuts | **33 / 452** — same view sets as the judge round |
| wall | **1,647 s = 27.5 min** · mean 49.9 s/scene · 3.64 s/cut incl. boot |
| exits | **0/33 non-zero** |
| stamp | `round_stamp.json` in every directory (round, HEAD, MDL md5 `16bba896…` v1.9.0, full `NEGOBS_*` arm) |
| driver | `scripts/rounds/run_260730_w2d_fix.sh` |

### 2.4 The one iteration — scene17 (F4)

The first pass moved scene17's numbers almost not at all: at `h1.8_d10` (where the defect lives)
σ_LF 10.02 → 10.47 and `flat_gnd` **6.0 → 7.2**, i.e. slightly worse. Cause, found by reading the
factory: `LOOK_CLASS["veg"]` is `mdl="omni"`, so **every grass plane took the plain OmniPBR branch
and none of the MDL de-tiling ever ran** — no `unit_cell` albedo jitter, no `patch_mix` rotation, no
`macro_amp`, no `tri_dither`, and `detail=False` so not even a detail normal. A 4096 px source
world-projected at one tile size onto a 24 × 78 m plane repeats on an exact grid; that is a
*repetition* defect and tint jitter cannot touch it.

Iteration: scene17's four turf materials renamed `Looks/TurfSoil{,B,C,D}`, which classifies as
**soil** (`mdl="ground"`, `patch=1.0`) — the same grass texture, now through NegObsGround with patch
rotation and macro modulation. Scene-local; no other scene's grass is affected.

| scene17 | judge | fix (OmniPBR) | **fix (ground MDL, kept)** |
|---|---:|---:|---:|
| `h1.8_d10` σ_LF | 10.02 | 10.47 | **10.44** |
| `h1.8_d10` flat5m | 10.4 | 11.3 | **9.6** |
| `h1.8_d10` flat_gnd | 6.0 | 7.2 | **5.3** |
| `h0.3` median edge | 79.2 | 82.9 | **98.8** |
| `h0.3` median `edge%` | 74.9 | 81.4 | **83.2** |
| `h0.3` median flat_gnd | 2.68 | 3.27 | **2.29** |

Both flatness measures now sit **below the judge baseline** on both cut sets, where the OmniPBR
variant was above it. Gates re-run after the iteration: audit 0 · `ground_kit` exit 0 · geom R-4/R-6
1/1 for scene17 · `valset --check` exit 0.

---

## 3. Gates — `regression_check` v2.1 vs `260730_w2d_judge` `[measured]`

`--before-round 260730_w2d_judge --after-round 260730_w2d_fix` → `Docs/reports/regr_260730_w2d_fix.json`,
452 cuts.

| verdict | cuts | | code | FAIL | WARN | INFO |
|---|---:|---|---|---:|---:|---:|
| PASS | 261 | | **GRAZE** | **0** | **0** | 7 |
| WARN | 94 | | **OCCL** | **0** | **0** | 0 |
| INFO | 85 | | **PHOTO** | **0** | **0** | 0 |
| **FAIL** | **12** | | FRAME | 12 | 42 | 0 |
| | | | DARK / WHITE | 0 / 0 | 0 / 1 | 28 / 25 |
| | | | UNCHANGED / CAPTURE | 0 | 52 / 0 | 0 / 71 |

**GRAZE FAIL 0 · WARN 0.** The judge round's 8 GRAZE FAILs were against baselines predating ~20 W2
commits; measured against the judge round itself there is nothing left, and that includes the two
firings ruled attributable to ground_kit (scene16 `h0.3_d10`, sceneC4 `h0.3_d5`). Those two are
**still legitimately present as content** — both rounds carry the mandated tactile band, so the
detector sees no change. They are adjudicated legit in `w2d_round_v1.md` §3.2 and the structural
close-out (**D14**, wiring `EXPECTED_FP` into `regression_check`) remains open with the supervisor;
this batch did not touch it.

**OCCL 0 and PHOTO 0** is the direct measure that B3 is closed: the judge round's only two OCCL
FAILs and 11 of its 13 PHOTO FAILs were scene19 going near-black, and neither class fires anywhere
now.

### 3.1 The 12 FRAME FAILs — every one attributable to F1–F5

FRAME is block occupancy after global tone normalisation, i.e. it measures composition; a round
whose whole purpose is to change ground materials, scatter density and decal shape must move it.
`w2c_merge_t1_v1.md` §4.2 already ruled FRAME "not a hazard gate in a round whose purpose is a
content change".

| scene · cut | Δmean | diff_frac | attributable to |
|---|---:|---:|---|
| scene02 `h0.3_d2` · `h0.3_d5` | −11.1 / +9.0 | 17.6 / 15.6 | **F5** — manhole + gully 0.80 stainless → 0.10 iron, both in the near window |
| scene07 `h0.3_d2` | +9.1 | 30.7 | **F2 + F3** — 223 → 153 rocks at half scale, leaf-drift rim 12 → 4 mm |
| scene11 `h0.3_d5` · `h0.3_d10` | +20.4 / +24.9 | 38.5 / 49.8 | **F1** — the dead plate is gone (`flat_gnd` 53.1 → 9.2) and the tree band stops rendering lilac |
| scene12 `h0.3_d5` · `h0.3_d10` | +11.1 / +11.2 | 25.5 / 21.0 | **F3** — stain/silt decal yaw jitter on the deck near field |
| sceneN1 `h0.3_d5` · `h0.9_d5` | −1.1 / +0.7 | 8.8 / 5.0 | **F1 + F5** — crack/stain off the `Joint` constant, manhole to iron |
| sceneN5 `h0.3_d5` · `h0.9_d10` · `h1.8_d10` | −10.7 / +1.9 / −2.0 | 10.6 / 5.4 / 4.0 | **F5 + F1** — the 12-gon double-rim disc becomes a 32-segment disc; crack rebind |

No scene outside the F1–F5 target set produced a FAIL.

### 3.2 `near_ground_stats` — the blocker targets and the σ_LF trade

Median of the three `h0.3` preset cuts, `--median`.

| | judge | fix | target |
|---|---:|---:|---|
| **scene19 `flat_gnd`** | 94.81 | **0.03** | ≤ 20 — **met with 20 pp to spare** |
| scene19 `edge%` | 0.7 | **76.1** | the plane is a surface again |
| scene19 `w80` | 0.00 | 1.10 | < 40 — kept |
| **scene11 `flat_gnd`** | 53.12 | **9.23** | down from 53.1 — **met** |
| scene11 `edge%` | 3.3 | **63.1** | |
| **scene17 `flat_gnd`** | 2.68 | **2.29** | σ_LF improve — see below |

Other movements worth recording: **scene20 `flat_gnd` 4.89 → 0.13** (the near-white 0.75 kerb
constant off the wear/stain decals — the "glowing plates"); **scene18 `w80` 40.6 → 29.3, σ_LF 1.82 →
3.25, `flat_gnd` 1.69 → 0.17** (ghost rectangles); **sceneN5 σ_LF 5.10 → 9.97, `w80` 79.4 → 70.1**;
**sceneN2 σ_LF 12.88 → 14.05**; **sceneD3 3.74 → 4.95**; **sceneN3 `w80` 9.5 → 7.8, `flat_gnd` 3.02 →
1.88**; **scene04 `w80` 2.4 → 0.3**.

**The σ_LF trade, stated plainly.** σ_LF ≥ 5.0 clearing goes **11/33 → 9/33**: scene07 (14.92 →
4.07) and scene10 (5.72 → 4.00) lose the gate. Five more scenes drop by more than 10 % (02 −16 %,
05 −40 %, 11 −14 %, 14 −30 %, 19 −41 %), none of which changes a gate verdict — 11 stays well clear
at 8.18, and 02/05/14/19 were below 5.0 in both rounds.

This is not the ground going flat, and the same three columns say so in every case:

| scene | σ_LF | `edge%` | `flat_gnd` |
|---|---:|---:|---:|
| scene07 | 14.92 → 4.07 | **64.6 → 90.3** | 0.73 → 0.96 |
| scene10 | 5.72 → 4.00 | **78.6 → 84.3** | 0.63 → 0.55 |
| scene19 | 2.42 → 1.43 | **0.7 → 76.1** | 94.81 → 0.03 |
| scene05 | 3.76 → 2.25 | 51.8 → 53.3 | 0.63 → 0.59 |
| scene02 | 3.21 → 2.70 | 51.4 → 61.3 | 0.12 → 0.09 |

σ_LF is a *low-frequency* luminance spread. What the two gate-losing scenes were scoring it with was
a field of near-white boulders sitting in dark sink rings and photographic leaf rectangles with 12 mm
rims — large tonal blotches, and precisely the content the eyes round FAILed them for. Removing the
blotches removes the low-frequency spread, while high-frequency ground detail **rises** in both.
This is the same reading `w2d_round_v1.md` §4.4 applied to scene08's −20.55 ("not content — the
metric returns to the material's own figure"). Recorded here as a known consequence, not defended as
a win: **if the supervisor wants scene07/10 back over 5.0 it has to come from real ground content,
not from restoring the artifacts.**

---

## 4. Artefacts

| what | where | count |
|---|---|---|
| fix round | `look_check/<scene>/260730_w2d_fix/` | 33 dirs · **452 PNG** + `manifest.json` + `round_stamp.json` |
| review gallery (**rebuilt from the fix round**) | `look_check/_review_w2/*.jpg` + `meta.json` | **132 JPEG** (600 px, q80) · 33 scene records with the fix-round gate status |
| crops (**fix round**, judge crops preserved) | `look_check/_experiments/gates/w2d_fix_crops/` + `index.json` | **23 PNG**, same 23 questions as the judge round |
| HQ sheets | `Docs/audit_v4/library_main21_260730_w2d_fix.png` (3840×3798) · `library_batch1_260730_w2d_fix.png` (3840×1974) | 2 |
| machine gates | `Docs/reports/regr_260730_w2d_fix.json` | 452 cut records |
| new check | `scripts/const_color_audit.py` | reusable, exit 1 on violation |

`look_check/**` is gitignored — the sheets, this report and `regr_260730_w2d_fix.json` are the
committed record.

---

## 5. Open — handed on

| # | item | who |
|---|---|---|
| **D14** | `EXPECTED_FP` is still inert on the consumer side. Not touched by this batch (it changes the verdict function the 250-cut corpora calibrate). Both attributable tactile-band firings are quiet against the judge baseline, so nothing is urgent — but the next round with a *new* baseline will manufacture them again. | supervisor |
| σ_LF 07 / 10 | gate lost as a consequence of F2/F3 (§3.2). Needs real ground content, not the artifacts back. | supervisor / W3 |
| F4 completeness | scene17's turf now de-tiles, but the **library-wide** grass problem is untouched: `LOOK_CLASS["veg"]` is `mdl="omni"`, so *no* grass prim in the other 32 scenes gets `unit_cell` / `patch_mix` / `macro_amp`. Promoting veg to a ground class globally is a W3-sized call. | W3 (input list item 3) |
| leaf-mask tooling | F3 removed the outline stroke and the rim shadow and broke the axis alignment, but the masks are still rectangles. Real feathering needs mask tooling. | W3 |
| `GkGap` | scene10/12's plank-gap material is still a texture-less constant and is **deliberately allowlisted** in the audit — it is a dark shadow slot, and §2.4 of the eyes report reads it as correct. Revisit only if it ever renders as a plate. | noted |
| scene19 `mean` | the membrane albedo lift moves the h0.3 median frame mean to 182 (from ~163). `w80` is 1.1, far under the 40 bar, and `flat_gnd` is 0.03 — but an eyes call on overall brightness is owed. | eyes |
| everything in `tonglam_v2.md` §4 | the W3 input list is unchanged by this batch. | W3 |

## 6. Reproduce

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh && conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

python3 scripts/const_color_audit.py          # 139 wirings · violations 0
python3 ground_kit.py                         # exit 0 · 33/33 · prims 1233 · scatter 740
python3 scripts/geom_invariance_check.py      # R-5 · R-4 33/33 · R-6 33/33
python3 scripts/valset.py --check             # 3 corpora reproduce w2_tools §4.4

bash scripts/rounds/run_260730_w2d_fix.sh     # 33 scenes, 452 cuts, 27.5 min

python3 scripts/regression_check.py --scenes 'look_check/scene*' \
  --before-round 260730_w2d_judge --after-round 260730_w2d_fix \
  --fail-only --json Docs/reports/regr_260730_w2d_fix.json
python3 scripts/near_ground_stats.py \
  'look_check/scene19/260730_w2d_fix/pt_noon_preset_h0.3_d*.png' --median --gate

python3 scripts/make_hq_sheet.py --round 260730_w2d_fix --set main21
python3 scripts/make_hq_sheet.py --round 260730_w2d_fix --set batch1
python3 scripts/make_review_gallery.py --round 260730_w2d_fix \
  --out look_check/_review_w2 --status-json Docs/reports/regr_260730_w2d_fix.json
python3 scripts/rounds/crops_260730_w2d.py --round 260730_w2d_fix \
  --out look_check/_experiments/gates/w2d_fix_crops
```
