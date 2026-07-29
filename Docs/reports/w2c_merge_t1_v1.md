# W2-C — `w2-surgeon` merge · C2 edge integrity · B12 · T1 A/B pilots

Author: W2-C (MAIN tree, branch `feat/realism-v1`) · 2026-07-29/30 · GPU exclusive, sequential
single-instance renders, `NEGOBS_PT_FAST=1`, `MODE=pt`.
Every number is `[measured]` from a PNG or from code executed this session, `[calc]` from the
verified frame model, or `[assumed]` with the reason stated.

---

## 0. Verdict in one paragraph

The merge landed clean (one trivial conflict, resolved per ruling) and **every post-merge gate
passed before a single frame was rendered**: `py_compile` 36/36, R-5 zero residual `LOOK_V1`,
R-4 33/33, R-6 33/33, `ground_kit.py` exit 0. The C2 A/B then produced the round's most valuable
number: at the *same* `HEAD`, ground_kit's own OCCL contribution is **≤ 0.891 % new dark with a
largest blob of 0.595 %** on the worst cut — against the 21.0 % / 19.5 % the pilot had measured
versus the stale `r2_on`. **D2 is closed: that blob was baseline drift, not ground_kit**, a 23×
overstatement. B12 passed exactly (4 prototypes, 1,784 / 1,784 leaf prims instanced). The T1 pilots
are the round's negative result, and it is a clean one: **the material layer moves the metrics
strongly, and the detail normal contributes essentially none of it** — isolated by a third arm
(`NEGOBS_DETAIL=0`), the detail normal's own share of scene19's Δslope is **+0.0004 out of
+0.1850**. Sweeping `detail_texture_scale` across {12.5, 4, 3, 2} and adding `detail_rough_gain`
up to 0.60 never lifts it above the noise floor. **W2-D: GO on the ground/spread track,
NO-GO on treating the detail normal as a delivered feature.**

**One structural finding the round had to fix before it could run at all**: the §1.6(b) detail-normal
wiring **did not exist in either tree**. W2-A5 shipped MDL v1.9.0 and wrote "Nothing was wired —
the worktree agent owns `_DETAIL_MAP` wiring per §1.6(b)"; `w2-surgeon` never took it up. The T1
A/B had nothing to A/B. It is wired now (commit `dbd58c9`), and defect ① — "the ground branch has
no code path" — is what that wiring closes.

---

## 1. Merge — evidence

`git merge w2-surgeon` into `feat/realism-v1`. Merge commit **`167f75d`**, parents
`e9ee0ac` (main, the collected W2 parallel deliverables) and `deb6e21` (surgeon head).
Base `80e1301`, 35 files, +1,767 / −302.

### 1.1 The one conflict, resolved per ruling

`scenes/batch1/sceneN5_flush_grating.py:703` — both branches converted the tactile material from a
constant colour to the `tactile_yellow` texture. Per ruling, **MAIN's version was kept** (render-
validated: strong-yellow pixels 118 → 12,149 in the pilot) and the surgeon's `bc.tactile_mtl`
duplicate discarded. Functional equivalence verified: same `tactile_yellow_diff/nor`, same 0.30 m
tile, same roughness source.

Tactile routing re-verified end to end after the resolution `[measured — grep + ground_kit run]`:
`ground_kit._ik_tactile` → `ik.build_tactile_pair(... mtl ...)` → op arg `"@tactile"` →
`M["tactile"]` (the kept `PBR(..., sc.tex_path("tactile", ...))`). `python3 ground_kit.py` still
exits 0 with the §12 registry checks green.

### 1.2 Post-merge verification — all pass, run before any render

| # | check | result |
|---|---|---|
| V1 | `py_compile` on every merged `.py` + ground/infra/stair kits | **36 files, 0 failures** |
| V2 | `geom_invariance_check --assert-no-residual-lookv1` (R-5) | **0 violations**, 40 files scanned, 3 allowed compat-shim lines |
| V3 | R-4 — prim-inventory hash `LOOK_MTL` 0 vs 1 | **33 / 33 PASS** |
| V4 | R-6 — three-way hash including `LOOK_V1=1` | **33 / 33 PASS** |
| V5 | `python3 ground_kit.py` | **exit 0** — 33/33 hard gates, burial guard 0, 33-scene apply round-trip clean |
| V6 | grep — `Japanese_Cherry` in live tables | **0** (comments + the procurement downloader only) |
| V7 | grep — `Forsythia` / `Burning_Bush` in `SHRUB_ORNAMENT` | **0** — `SHRUB_ORNAMENT = {Rhododendron, Juniper}` |
| V8 | grep — `grass_lawn` wired | `TEX["grass"] = grass_lawn_{diff,nor,rough}.jpg`; `aerial_grass_rock` refs 0 in live code |
| V9 | grep — `LOOK_MTL` / `LOOK_GEO` present | 30 occurrences in `scene_common.py`, compat shim at `:189–191` |

`VEG_TREES` after merge `[measured — AST]`: Elm_Sapling 4 · Shumard_Oak 3 · Chinese_Juniper 2 ·
White_Pine 1 · Yellow_Pine 1. `VEG_DEBRIS` equals B-audit A3 verbatim.

R-4/R-6 were re-run a **second** time after the T1 detail wiring landed and still read 33/33 —
the wiring touches shader inputs only, so rule R-1 (materials must not move prims) holds.

---

## 2. C2 — edge integrity by ground ON/OFF A/B (replaces GRAZE silence)

Per ruling C4, GRAZE silence is not evidence. The evidence is a same-session, same-`HEAD`
ground_kit ON/OFF A/B read through OCCL, plus eyes.

**Mechanism** (commit `afef9c4`): `NEGOBS_GKIT=0` makes `apply_ground` return an empty result
before creating anything. The P-A `skin_exclude` call was deliberately placed **before** the switch,
so the displacement-skin state is identical in both arms and the only difference is the kit's own
prims. 22 cuts, 6 runs, ~2 min GPU.

### 2.1 OCCL — the strict gate

Thresholds (`regression_check.py`): new-dark WARN 2.0 / FAIL 8.0 %, largest blob WARN 1.5 / FAIL 5.0 %.

| scene | cut | new dark % | largest blob % | \|Δ\|>25 px % | verdict |
|---|---|---:|---:|---:|---|
| `sceneN5` | h0.3 d2 | **0.000** | **0.000** | 16.73 | PASS |
| | h0.3 d5 | 0.005 | 0.004 | 1.28 | PASS |
| | h0.3 d10 | 0.001 | 0.001 | 2.45 | PASS |
| `scene15` | h0.3 d2 | 0.000 | 0.000 | 9.37 | PASS |
| | h0.3 d5 | 0.005 | 0.004 | 4.52 | PASS |
| | h0.3 d10 | 0.011 | 0.011 | 3.06 | PASS |
| `scene13` | h0.3 d2 | **0.891** | **0.595** | 2.04 | PASS |
| | h0.3 d5 | 0.578 | 0.484 | 1.54 | PASS |
| | h0.3 d10 | 0.114 | 0.101 | 0.38 | PASS |
| | `entry_approach` | 0.306 | 0.296 | 0.68 | PASS |
| | `ramp_graze` | 0.596 | 0.438 | 1.57 | PASS |

**The `scene13` line is the round's headline.** The pilot reported 21.0 % new dark / 19.5 % blob on
this exact cut against `r2_on`. At matched `HEAD` the kit contributes **0.891 % / 0.595 %**. The
darkening was the intervening ten commits, not ground_kit. Defect **D2 is closed**.

### 2.2 Eyes — crops at `look_check/<scene>/w2c_c2_crop/`

| crop | verdict |
|---|---|
| `scene13/d2_crest_zoom.png` (×2.6 brightness) | **PASS.** The crest highlight line survives in the ON arm; the entry trench attaches as a *separate* dark line **beyond** the crest, which is the designed x 0.35 → 0.52 relocation. GT-E2 margin Δ 17.35 @540. |
| `scene13/entry_curb.png` | **Gate 13-1 (redefined) PASS.** Both ramp curbs are unmistakable light strips down the ramp walls in `entry_approach`; the d5 manhole and the entry trench also read. Nothing of the sort in the OFF arm. **No preset camera was added** — `entry_approach` and `ramp_graze` are pre-existing mise-en-scène cuts. |
| `scene13/rampgraze_zoom.png` | Curbs again visible; the ramp mouth stays open and black in both arms — no burial. |
| `sceneN5/preset_h0.3_d2_bottom512.png` | The near-window manhole appears at 66 % frame width, as designed. This is the whole FRAME FAIL. **Defects confirmed: the disc is a visible octagon (D4) and renders near-black.** |
| `scene15/d5_bottomhalf.png` | U-gutter and boundary strips read; **the manhole is barely distinguishable from the pavement (D5)**. Frame fill stays materially dependent on T1. |

### 2.3 The remaining regression firings, adjudicated

| firing | reading |
|---|---|
| `sceneN5` d2 **FAIL** FRAME 63 % block shift + PHOTO mean −27.8 | The near-window manhole entering frame. OCCL 0.000/0.000 ⇒ not a burial. `sceneN5` is a hard negative (`edges=()`), so there is no drop to bury. **Expected change.** |
| `sceneN5` d5 WARN GRAZE (step 6.2 → 24.7) | A ground_kit joint/line in a *notional* edge band on a scene with no drop. Per ruling C4 this is not edge evidence either way. |
| `scene13` d2 **FAIL** GRAZE (step 15.8 → 15.8, ratio **1.00**) | The step magnitude did not change at all; only the checker's "locality" score fired. The eyes crop shows the crest line intact. |
| `scene13` `ramp_graze` WARN GRAZE ("line collapsed", 2.0 → 1.9) | A 5 % step change — noise-level. Mouth open in both arms. |
| `scene15` all three cuts | **PASS / PASS / PASS**, FAIL 0 WARN 0. |

**Per-scene C2 verdict: `sceneN5` PASS · `scene15` PASS · `scene13` PASS.** No ground_kit element
buries a drop edge or the camera in any of the eleven cuts.

### 2.4 Bug found and fixed by the A/B itself

The OFF arm's return dict omitted `materials_needed`, so `scene13` — the only scene that reads that
key — died with `KeyError` in the OFF arm only. Fixed by making the key set identical to the normal
return, plus a key-set parity assertion in the round script. Worth recording because it is the same
*class* as the pilot's `apply_ground` positional-material crash: **a code path that only the
diagnostic arm exercises is a code path nobody tests.**

---

## 3. B7 — tactile dot Ø 38.1 → 25 mm

**The size lived in the texture generator, not in the relief.**
`assets/scene01/download_scene01_assets.py` had `dot_d = N / 8.0` = 128 px on a 1024 px tile =
**37.5 mm** nominal (38.1 measured including the rim). Now parameterised as
`TACTILE_TILE_MM = 300.0` / `TACTILE_DOT_D_MM = 25.0`.

§12 gates re-measured with one measurer, before vs after `[measured]`:

| gate | before | after | requirement |
|---|---:|---:|---|
| dot count | 36 | **36** | 36 = 6×6 `[law]` |
| pitch | 49.8 mm | **49.8 mm** | 50 `[law]` |
| area-equivalent diameter | 38.2 mm | **25.7 mm** | 22–25 common practice |
| **dot-area share** | 45.9 % | **20.8 %** | ≈19.6 % practice — the reason for the ruling |
| linear albedo | 0.4841 | **0.4504** | < 0.55 (§12.5-4 cap) |
| dot-top vs floor luminance step | +0.1387 | +0.1360 | preserved |
| `python3 ground_kit.py` | exit 0 | **exit 0** | B9 albedo + B11 registry included |

The PNG itself is `.gitignore`d (`assets/scene01/*`); the generator is the source of truth. The
manifest and two docstrings were synced.

**New finding carried (D10).** The generator normalises the height field to [0, 1] and then applies a
fixed `strength = 3.0` to the Sobel gradients, so **smaller dots get steeper normals**. Encoded
tangent angle p99 went 68.1° → 70.1°, while the legal geometry (Ø 25, h 6) tops out at 51.3°. The
*relative* error actually improved (1.92× → 1.37×, because Ø 37.5 h 6 implies only 35.5°), so this is
not a regression — but the generator's normal strength is not derived from the statutory 6 mm and
should be. Left untouched: it is outside the B7 ruling and would change the shading of all 24 wired
tactile sites.

---

## 4. B12 — G2 instancing runtime check, and the sceneC2 round

### 4.1 B12 — PASS

Run through `NEGOBS_SMOKE=1` (the check is now embedded in `sceneC2`, so it is re-runnable):

```
[B12] 프로토타입 4개 (≥1 필요) · 낙엽 Asset 프림 1784개 · IsInstance True 1784개 (100.0 %)
       · /__Prototype_1 자손 6   · /__Prototype_2 자손 6
       · /__Prototype_3 자손 8   · /__Prototype_4 자손 13
[B12] PASS — 프로토타입 ≥1 ∧ 전 낙엽 인스턴스화
```

Unique vertex data therefore does **not** multiply by 1,784, so the §8.3 triangle budget
(10.84 M logical / 12 M cap) stands. This gate needed `pxr` at runtime and could not be run by any
CPU-only agent — it was budget-doc gate 0 and blocker B11 on the surgeon's list.

### 4.2 sceneC2 13-cut round — `look_check/sceneC2/w2c_g2/`

**Leaf count 1,784 confirmed** (budget doc predicted 1,689 with the pre-A3 coverage ledger; the
+5.6 % is exactly the A3 re-ledger, as the surgeon predicted). **Render time 55 s for 13 cuts =
4.2 s/cut including boot** `[measured]`.

Eyes gates:

| gate | result | evidence |
|---|---|---|
| no plank ("장판") leaves | **PASS** | d2/d5 near field is individual 3D leaves with their own cast shadows |
| no rectangular leaf-field boundary | **PASS** | column-profile max gradient of the orange mask, frame edges excluded: **0.0037–0.0074 /px** across 5 cuts. The larger *row* gradients (0.0094–0.0157) are the mound crest against sky, which is geometrically correct. |
| leaf / texture tone match | **PASS** | `leaf_ground` texture band R/G **1.429**, sat 0.567 sits *between* the 3D leaves' near-field (1.233) and mound-top (1.624) readings. The "yellow band" impression at d5 is the mound's shaded front face, not a hue mismatch. |
| no blossom / seasonal asset | **PASS** | pink pixels 0 by eye and by mask |

Regression v2.1 vs `leaf3d` — **FAIL 4 · WARN 7 · PASS 2**, adjudicated by class:

| class | count | adjudication |
|---|---|---|
| FRAME (FAIL 4, WARN 6) 12–51 % block shift | 10 | **Expected — G2 extent** (near band → 132 m² global) **+ grass swap** (Grass001, 1.4 m tile). FRAME is not a hazard gate in a round whose purpose is a content change. |
| OCCL (FAIL 1, WARN 5) new dark 1.3–8.2 % | 6 | **Expected — G2 extent.** Largest connected blob **0.0–0.4 %** against WARN 1.5 / FAIL 5.0. Spec §7.2 S4 makes the *blob* the burial symptom, and 1,784 dispersed leaf shadows is precisely the signature of a large new-dark area with a tiny blob. |
| PHOTO (WARN 1) d10 mean −22.0 | 1 | **Expected — albedo.** Leaves (≈0.15) now cover ground that was bright grass/soil, plus sun cap 1.5° → 0.6° hardening shadows. |
| CAPTURE (INFO 6) | 6 | The known `manifest ok=false` false positive. All 13 PNGs decoded and measured. |
| GRAZE (INFO 1) | 1 | Carried absolute state, not a new firing. |

> `leaf3d` is a baseline that t1 spec §7.1 `[v1.1 T2]` **forbids citing**. It was used here only to
> classify expected differences, never to derive a threshold.

New observation carried: distant shrubs read as a row of identical green hemispheres at d2 — same
proxy-geometry family as D3 (weeds as olive cubes).

---

## 5. T1 A/B pilots

### 5.0 Precondition the round had to build first

`_DETAIL_MAP` (§1.6(b)) was unimplemented in both trees. `grep` over MAIN and the worktree found
`detail_normalmap_texture` bound in exactly one place — the **OmniPBR** branch, with the single
legacy map `concrete_wall_nor_dx.jpg`, which §1.2 itself classifies as *not a detail map*
(macro 4.1 %, slope −0.71). The MDL/ground branch bound nothing. Commit `dbd58c9` wires the §1.6(b)
tables into both branches. MDL type trap recorded: `detail_texture_scale` is **`float` in the MDL**
and `float2` in OmniPBR; the wrong type is silently ignored.

**MDL v1.9.0 first compile: 0 errors across all 11 runs** `[measured — console grep]`.

### 5.1 The decomposition — the round's most important table

`scene19`, h0.3 3-cut medians, control = `LOOK_MTL=0 LOOK_GEO=1`:

| arm | slope | sat_mu | flat_gnd | Δslope | Δflat_gnd |
|---|---:|---:|---:|---:|---:|
| control `t1_mtl_off` | −2.5921 | 0.0320 | 3.9152 | — | — |
| `t1_mtl_on` **detail OFF** (`NEGOBS_DETAIL=0`) | −2.4074 | 0.0326 | 1.4147 | **+0.1846** | **−2.5004** |
| `t1_mtl_on_s2` detail ON | −2.4071 | 0.0327 | 1.4681 | +0.1850 | −2.4470 |

**The detail normal's own share is Δslope +0.0004 and Δflat_gnd +0.053** — the latter is a slight
*worsening*. Everything the material layer achieves comes from MDL promotion, macro modulation,
triplanar sampling, weathering and bevel. Without this third arm the round would have reported
"T1 works" and silently credited it to the feature that does nothing.

### 5.2 `detail_texture_scale` sweep — metrics null, pixels monotone

| arm (`scene19`) | Δslope vs control | Δflat_gnd | pixel Δ vs `s12.5`, >2 LSB | same, bottom-512 crop |
|---|---:|---:|---:|---:|
| `s12.5` (spec default, 8 cm tile) | +0.1833 | −2.4427 | — | — |
| `s4` (25 cm) | +0.1815 | −2.4254 | 3.35 % | 6.76 % |
| `s3` (33 cm) | +0.1825 | −2.4241 | 4.49 % | 9.17 % |
| `s2` (50 cm) | +0.1850 | −2.4470 | **6.72 %** | **14.97 %** |
| `s2` + `rough_gain 0.30` | +0.1849 | −2.4508 | 6.93 % | — |
| `s2` + `rough_gain 0.60` | +0.1845 | −2.4732 | 7.48 % | — |

Metric spread across the whole sweep is Δslope ≤ 0.0017 — **below the §7.1 noise floor of 0.015**
(the `r2_on↔balust` maximum). The pixel effect is real and monotone in tile size, but stays at
≤ 1.2 LSB mean.

Eyes, 4-split proximity crop per §7.2-4 (`look_check/scene19/t1_crop/`):

* `ab_s12.5.png` (control vs experiment) — **a clear, legible difference**: deeper joints, stronger
  crack contrast, more surface grain. The material layer passes the eyes test.
* `sweep_12.5_vs_2.png` — **indistinguishable**. And the repetition artefact R1 warned about for a
  0.5 m tile is **not observed** — the grain is too weak to repeat visibly.

**Chosen `detail_texture_scale` = 2.0** (0.5 m tile): largest measurable effect, no repetition
observed, identical cost. This is a choice among nulls, not a gate pass. **`detail_rough_gain` stays
at 0** — 0.60 is still inside the noise, and turning on an unjustified knob is worse than leaving
the MDL default.

### 5.3 Gate table — Δ vs control (thresholds `Δslope ≥ 0.05` · `Δsat ≥ 0.015` · `Δflat_gnd ≥ 0.10`)

| scene | Δslope | Δsat_mu | Δflat_gnd | Δflat_pct | slope | sat | flat_gnd |
|---|---:|---:|---:|---:|:--:|:--:|:--:|
| `scene19` (s2) | **+0.1850** | +0.0006 | **−2.4470** | −7.42 | ✔ | ✘ | ✔ |
| `scene07` | +0.0205 | **−0.0382** | **+0.4555** | −11.27 | ✘ | ✔ | ✔ |
| `scene14` | −0.0255 | **−0.0372** | **−12.0125** | −16.31 | ✘ | ✔ | ✔ |
| `sceneC2` (control) | −0.0003 | −0.0414 | +0.0725 | −16.98 | — | — | — |

Every pilot clears **2 of 3** detection thresholds; the material layer is unambiguously above the
noise floor everywhere. `sceneC2` behaves as principle P-3 predicts (small effect is not failure)
and its own gate holds: slope −2.0200 → **−2.0203**, i.e. it did **not** steepen.

**Regression v2.1 across all five A/B pairs: FAIL 0 · WARN 0.** (`scene19`'s four INFO/WHITE rows
are the carried absolute white-level state, not a regression; `scene07`'s two INFO rows are the
`manifest ok=false` false positive.)

### 5.4 §7.3 absolute pass conditions — **all three pilots fall short, and the gap is tone**

| scene | condition | measured | verdict |
|---|---|---:|---|
| `scene19` | `w80 < 40` | **87.54** | ✘ |
| | `sat > 0.10` | **0.0327** | ✘ |
| | `slope > −2.45` | −2.407 | ✔ |
| | `flat_gnd` no worse than 10.0 | 10.03 → **1.47** | ✔ |
| `scene07` | `slope ≥ −2.25` | **−2.375** | ✘ |
| | `sat < 0.24` | **0.2623** | ✘ |
| | `flat_gnd` no worse than 1.7 | 1.68 → **1.60** | ✔ |
| | no slope-stretch by eye | none seen | ✔ |
| `scene14` | `flat_gnd < 20` | **24.83** (from 31.33) | ✘ |
| | slope moves toward target | −1.974 → −2.050 | ✘ (moved away) |
| | channel-clamp colour bias 0 | none seen — the ON arm neutralises the yellow marble cleanly | ✔ |

The failures are **saturation and white level**, not micro-structure. No detail normal at any tile
scale can move `sat_mu` from 0.033 to 0.10.

### 5.5 plaza tone ×0.72 + `scale_m` 1.80 — verified in-pilot on `scene19`

Compared at **matched `LOOK_MTL` state** (`r2_on` → `t1_mtl_on`, both MTL=1), so the tone/scale/
sun-cap change is what moved:

| metric | `r2_on` (pre-merge) | `t1_mtl_on` (post-merge) | Δ |
|---|---:|---:|---:|
| `w80` | 97.71 | **87.54** | **−10.2 pp** |
| `wht%` | 97.52 | 92.43 | −5.1 pp |
| `flat_gnd` | 10.03 | 1.47 | −8.56 |

**Direction correct, magnitude insufficient.** The target is `w80 < 40`; ×0.72 delivered 10 pp of
the 58 pp needed. `scene19` will need the further §5.2 tone measures, not a stronger detail normal.

### 5.6 W-3 resolved — the `scene14` V-notch is real

`look_check/scene14/t1_crop/vnotch_W3.png`. The side parapets in `lower_lookup` render as a
**saw-tooth**: the rake haunch rises to a sharp peak at each landing and drops into a V. It is
**identical in both A/B arms** (`lower_lookup` regression PASS, block shift 0), so it is base
geometry, not a T1 artefact.

This contradicts all three of the standing claims at once: the `build_parapets` docstring says
v5.1 replaced the stepped parapet with "사선 헌치 + 참 수평" and that joint steps are **zero**;
v6 claims the seam was sealed; the C4 history says 14 and 18 were retired and only 19 remained.
The §7.3 ★ concern — that `scene14`'s `flat_gnd` verdict is measured on top of an unexplained
geometry anomaly — is therefore **substantiated**, and `scene14` fails that gate anyway (24.83 vs
< 20). Repair is out of this mission's scope; see §7 W2-D item 3.

### 5.7 Render budget `[measured]`

| round | cuts | wall | s/cut incl. boot |
|---|---:|---:|---:|
| `scene19` control (`LOOK_MTL=0`, no MDL) | 4 | 16 s | 4.0 |
| `scene19` experiment (full material layer) | 4 | 24 s | 6.0 |
| `scene14` experiment | 4 | 35 s | 8.8 |
| `sceneC2` full round (1,784 leaf instances) | 13 | 55 s | 4.2 |

Material-layer overhead ≈ **+50 % wall time** on a 4-cut round including the MDL first compile.
Extrapolated 33-scene × 4-cut round: **≈ 8–10 min**, consistent with §7.5's estimate.

---

## 6. Defect ledger carried into W2-D

| # | defect | status |
|---|---|---|
| D1 | Cherry blossoms in main tree | **CLOSED** by the merge (`VEG_TREES` verified, 0 pink pixels in the sceneC2 round) |
| D2 | `scene13` d2 OCCL 21.0 % / blob 19.5 % unattributed | **CLOSED** — §2.1. Kit's share is 0.891 % / 0.595 %; the rest was baseline drift |
| D3 | Weeds render as solid olive cubes | open; distant shrubs as identical green hemispheres joins the same family (§4.2) |
| D4 | Manhole discs visibly polygonal at near range | **re-confirmed** at `sceneN5` d2 (§2.2) |
| D5 | B9 checks a declared albedo while scenes bind any material — `scene15` manhole near-white | **re-confirmed** at `scene15` d5 (§2.2) |
| D6 | `sceneN5` double joint grid (5 redundant prims) | open |
| D7 | Gate 13-1 unsatisfiable in h0.3 cuts | **CLOSED** — redefined and passed, spec §7.5 A2 |
| D8 | §12.3 d5 `EXPECTED_FP` sample | **CLOSED** — amended, spec §7.5 A4 |
| D9 | \|∇\| p99 definition unreproducible | still a supervisor ruling item |
| **D10** | Tactile normal-map flank angle is not derived from the statutory 6 mm rise (fixed `strength=3.0`) | **new**, §3 |
| **D11** | `scene14` parapet V-notch is real and contradicts code + history | **new**, §5.6 |
| **D12** | The detail normal is a null at h0.3 at every tested scale | **new**, §5.1–5.2 — this is a spec-level finding, not a bug |
| **D13** | `sceneC2`'s §7.3 slope gate ("not steeper than −1.75") is violated at −2.02 by the *content* round (leaves + grass), while T1's own contribution is −0.0003 | **new** — the gate needs re-baselining against the post-merge control |

---

## 7. GO / NO-GO for W2-D (33-scene spread + full re-render + 통람 v2)

### **GO on the spread. NO-GO on shipping the detail normal as a delivered feature.**

Everything the spread depends on is verified: the merge is clean and gated, ground_kit's edge
integrity is now established by an attributable experiment instead of by GRAZE silence, the leaf
instancing is proven at runtime, and the material layer passes regression with FAIL 0 · WARN 0 on
every pilot pair while showing a legible improvement in the proximity crops.

Four items should ride with the spread rather than block it:

| # | item | why | cost |
|---|---|---|---|
| **1** | Spread with **`detail_texture_scale = 2.0`, `detail_rough_gain = 0`**, and record the detail normal as **measured-null at h0.3** | It costs nothing and is the best of the tested options, but the spec should stop treating §1.6(a) as a realism lever at robot eye height. The lever that works is tone (§5.2/§5.5). | 0 |
| **2** | Re-baseline the §7.3 absolute conditions against the **post-merge control**, not `r2_on` | Three of them are now unreachable for reasons the merge introduced or exposed (`sceneC2` slope, `scene19` w80, `scene14` flat_gnd). Judging the spread against stale absolutes will manufacture failures. | doc |
| **3** | `scene14` V-notch — diagnose or swap the pilot to `scene21` per §7.3 ★ branch B | W-3 is now answered: the notch is real. `scene14`'s `flat_gnd` gate is measured over it and fails anyway. | 1 scene |
| **4** | Restore the **σ_LF ≥ 5.0 WARN gate** in the first post-T1 ground round, per the §7.5 A1 amendment | The amendment scoped it out of ground-only rounds precisely so it could be re-read once materials exist. T1 now exists. | 0 |

**Not blocking, but do not lose:** D3/D4/D5 are all "the proxy geometry is a box/polygon/wrong
albedo" defects visible at d2–d5, and they will be visible in all 33 scenes of the 통람 v2 sheet.

---

## 8. Commits

| hash | contents |
|---|---|
| `e9ee0ac` | W2 parallel deliverables collected — measurement tools ×3, regression v2.1, detail-grain maps ×3, MDL v1.9.0, veg ledger, 5 reports. Pixel-inert by construction. |
| `167f75d` | **merge** `w2-surgeon` — conflict resolved per ruling, 9 post-merge checks green |
| `afef9c4` | `NEGOBS_GKIT` diagnostic switch + ground_kit spec §7.5 amendment (4 gates re-scoped) |
| `0421321` | C2 edge-integrity A/B — OCCL table, eyes crops, D2 closed |
| `c4e3044` | B7 tactile dot Ø 38.1 → 25 mm at the generator + §12 re-verification |
| `dd94501` | B12 G2 instancing runtime check + sceneC2 13-cut round |
| `dbd58c9` | T1 §1.6(b) detail-normal wiring — defect ① closed |
| `e6b5977` | T1 A/B pilots, sweep, decomposition, W-3 resolution |

## 9. Reproduce

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh && conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

python3 scripts/geom_invariance_check.py            # R-5 -> R-4 -> R-6
python3 ground_kit.py                                # exit 0
NEGOBS_SMOKE=1 NEGOBS_LOOK_V1=1 python scenes/batch1/sceneC2_leaf_stairs.py | grep B12

# C2 A/B (both arms, same HEAD)
NEGOBS_GKIT=0 NEGOBS_LOOK_V1=1 NEGOBS_PT_FAST=1 NEGOBS_CAPTURE=1 \
  NEGOBS_CAPTURE_MODE=pt NEGOBS_CAPTURE_DIR=look_check/scene13/w2c_c2_goff \
  NEGOBS_VIEWS=preset_h0.3_d2,preset_h0.3_d5,preset_h0.3_d10 \
  python scenes/main/scene13_apartment_parking_entry.py

# T1 A/B arm
NEGOBS_LOOK_MTL=1 NEGOBS_LOOK_GEO=1 NEGOBS_DETAIL_SCALE=2 NEGOBS_DETAIL_ROUGH_GAIN=0 \
  NEGOBS_PT_FAST=1 NEGOBS_CAPTURE=1 NEGOBS_CAPTURE_MODE=pt \
  NEGOBS_CAPTURE_DIR=look_check/scene19/t1_mtl_on_s2 \
  python scenes/main/scene19_fan_winder.py
# control arm: NEGOBS_LOOK_MTL=0 NEGOBS_LOOK_GEO=1
# detail-only isolation: add NEGOBS_DETAIL=0

python3 scripts/regression_check.py --before look_check/scene19/t1_mtl_off \
        --after look_check/scene19/t1_mtl_on_s2
python3 scripts/near_ground_stats.py 'look_check/scene19/t1_mtl_on_s2/pt_noon_preset_h0.3_d*.png' --median
```

All image artifacts live under `look_check/**` (gitignored); `round_stamp.json` is written into
every capture directory with the git HEAD, MDL md5 and the full `NEGOBS_*` environment.
