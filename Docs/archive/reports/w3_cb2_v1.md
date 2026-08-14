# CB-2 — ground_kit decal/jitter batch + the five F3 scenes

> **Wave**: W3 · **Window**: 1 · **WP**: K1 (`ground_kit.py`) + S3 (the F3 co-landing group)
> **Kind**: commit-batch report · **Date**: 2026-07-31 · **Branch**: `feat/realism-v1`
> **Base**: HEAD `d7494f4` · **Authority**: `Docs/briefs/w3_execution_spec_v1.md` (the spec is law)
> · **GT ledger**: `Docs/audit_v4/gt_changes_w3.md` (GT-8, GT-9 landing records filled)
> **Render gate**: GATE-1, round `260731_w3_cb2`, pilots **03 · 07 · C2 · 01**

---

## 0. Verdict

**PASS.** All four pre-flight gates green, the GATE-1 pilot regression is **FAIL 0**, and the
pilot's own named acceptance criterion (spec §7.2: *"No decal with a straight edge that is not a
construction joint, a saw cut or a kerb. 07's leaf carpets and C2's leaf mass stop being
rectangles"*) is met and shown in §6.

| gate | result |
|---|---|
| `py_compile` on every touched file | clean |
| `python3 ground_kit.py` | **exit 0**, all 33 scene plans PASS |
| `python3 scripts/geom_invariance_check.py` | **R-4 33/33 · R-6 33/33 ✔ PASS** |
| `python3 scripts/placement_lint.py --scenes all` | **LINT-8 295 → 0**, every other check byte-identical (§3) |
| `scripts/regression_check.py` (GATE-1, 20 cuts) | **FAIL 0** · WARN 6 · INFO 1 · PASS 13 (§5) |

---

## 1. What landed

### 1.1 K1 — `ground_kit.py`

| row | change | evidence |
|---|---|---|
| **J-1** | `build_patch_field`: `yaw_max=14.0` random splay → `yaw_deg` taken from the **profile's declared module axis** (0.0 for every row in the `unit_cell` ledger). The rectangle **stays** — a real 절삭·덧씌우기 patch *is* a saw-cut rectangle | spec §10.1 row 1 · §10.5 DEC-3 |
| **J-2** | `build_stain_field`: `U(−22°, +22°)` free-blot yaw abolished; the six free-form kinds are now **DEC-1 lobes** instead of rotated rectangles. `grime_band` / `tire` keep their rectangles and their yaw 0 — their straight edges are real (a wall junction, a tyre) | spec §10.1 row 2 |
| **J-7** | `build_footprints`: the ±6° splay **kept** per §1.2; the AABB now uses the **jittered** angle. Before, the prim was authored at `ang + U(−6,+6)` while `_elem` registered `_obb_aabb(..., ang)` | spec §1.2 |
| **DEC-1** | new `build_blot()` — closed N-gon, radii `r*(1 + U(−rough,rough))`, once-smoothed circularly, **1 Mesh prim**, exact polygon AABB, no alpha / no opacity / no texture. Single upward face, **zero thickness**: the 8 mm rim every other decal carries is half of the "carpet laid on the ground" read | spec §10.5 DEC-1 |
| **DEC-2** | new `build_carpet_mask()` — `build_blot` at `n=24`, `rough` 0.15–0.20, plus a **feather ring** returned as a `scatter_req` for the injected `scatter_debris`. **Drift bias raises** (`drift=` is refused) — it is parked with P-4's evidence | spec §10.5 DEC-2 · §9 P-4 |
| **DEC-3** | patch axis lock + `_snap_module()`: `w`/`h` quantised to **whole or half flags**, `cx`/`cy` quantised so the patch **edges land on joint lines**. `plaza_granite` patch count 2 → 1 | spec §10.5 DEC-3 |
| **A1** | `_build_weed_band`: `lines=` line-seeding contract (`_weed_sites` + `_weed_seed_lines` derive the paving joints and manhole/gully frame perimeters the same profile emits) **and** the cube → `Shrub/Grass_Short_C.usd`. `plaza_granite` weed count 6 → 0 | spec §10.5 A1 · GT-9 |
| **G-6** | `deposition_cover_fn()` + `G6_GATED` / `G6_LAMBDA_EDGE` / `G6_SIGMA_TRACK` — **prepared and gated**: the signature and the three terms exist and are documented, the body raises, nothing calls it | spec §1.8 · §9 P-4 |
| **GT-8** | `_obb_aabb` → `_box_aabb` on every patch and stain (a consequence of J-1/J-2, not a separate edit) | ledger §3/§4 GT-8 |
| **GT-9** | weed asset + the **GT-E5-clamped** scale, written back by `_writeback_weed_heights` | ledger §3/§4 GT-9 |

### 1.2 S3 — the five F3 scenes

| scene | change |
|---|---|
| **07** temple | 6 leaf drifts × 3 stacked rectangles → **6 DEC-2 masks** (`z_fn = path_z`, so every vertex sits on the 19° corridor); 3 yard drifts × 2 rectangles → **3 masks**. **18 + 6 = 24 rectangles → 9 lobes.** Feather ring: 128 leaf cards, clipped to the corridor / courtyard plates. `leaf_band` retires `thick` / `sub_scale` / `sub_off` / `sub_rz` |
| **C2** leaf stairs | the **vertical-face leaf-texture binding bug**: new constant `leafsec` material (0.085, 0.052, 0.028 · rough 0.94) on 11 thin section skins over the exposed vertical faces of `LeafMound_A/B/C` and `LeafDrift_N/S`. **The mound geometry is untouched** — it is what buries steps 1–3 and it is this scene's negative-obstacle identity |
| **10** park deck | 4 ground leaf drifts × 3 stacked rectangles → **4 DEC-2 masks** (12 → 4 prims). The 10-2 leaf ring now runs on **all four** drifts, not only the two trail ones, and is seated on each drift's own zone z |
| **D3** drainage | 6 rectangular bed-leaf plates → **6 lobes** (`rough` 0.20); `thick` retired |
| **03** riverbank | no scene-side decal rectangles of its own — its F3 delta is entirely the ground-kit one (stains → lobes, patch yaw → 0). Its scene-authored patch `sites` are **not** module-snapped because the scene overrides `pave.module=(None, None)` |

---

## 2. Rows deliberately NOT done in CB-2, and why

| row | status | reason |
|---|---|---|
| **03-B** pole/bollard vs the prop-edge rule | **not started** | Depends on `PROP_EDGE` M1–M6, which are **P-7 parked** (`LINT-9` stays `WARN`, 29 BLOCK findings). Spec §1.8: enforcing a guessed setback is worse than none |
| **03-C** one species per route | **blocked** | Needs K4(b) `VEG_SPECIES` / `species=` / `SCENE_SPECIES`, which is **WINDOW 2 / CB-5**. Spec §5.3: `K4(b) → all eight S-WPs' veg= PARAMS` |
| **03-D** shrub replacement | **blocked** | Same edge — `place_shrubs(species=)` and the `randrange` removal at `scene_common.py:2819` are K4(b) |
| **E3** D3 boundary fence | **prep-only, not touched** | §4.3 lists E3 under S3, but §5.2 puts remaining scene work in **CB-10 / WINDOW 3**. CB-2's contents line is explicit: *"the scene-side decal/scatter work in 03 · 07 · 10 · D3 · C2"*. No fence code was written |
| **07 / 10 archetype rebuild** | **PARKED** | §9 P-1 / P-2 — user reference images. Only decals/scatter landed, exactly as §1.7 rules |
| **12** riverside deck | **owned, not in CB-2** | B3 reeds and N-A7 riprap are CB-10 rows. `scene12` is byte-identical in this batch (prim count 803 → 803) |
| **G-6 / 04-B** deposition | **prepared, gated** | §1.8. `deposition_cover_fn` raises; no profile and no scene calls it |
| **DEC-2 drift bias** | **parked** | §10.5 puts it behind P-4's evidence; `build_carpet_mask(drift=…)` raises rather than accepting it silently |

---

## 3. `placement_lint` delta — measured, isolated, zero added findings

The tree is shared with the concurrent CB-3 / CB-4 agents, so a naive before/after would have
attributed their `batch1` jitter removals to CB-2. The delta below is an **A/B at the same
instant**: `ground_kit.py` was swapped to its `HEAD` blob, the linter run, and the working copy
restored (md5-verified). Nothing else in the tree moved between the two runs.

| check | HEAD `ground_kit` | CB-2 `ground_kit` | Δ |
|---|---|---|---|
| LINT-1 | 0 E / 26 W | 0 E / 26 W | — |
| LINT-2 | 0 E / 42 W / 1 I | 0 E / 42 W / 1 I | — |
| LINT-3 | 0 E / 26 W | 0 E / 26 W | — |
| LINT-4 | 0 E / 27 W | 0 E / 27 W | — |
| LINT-4b | 49 E | 49 E | — |
| LINT-5 | 0 E / 32 W | 0 E / 32 W | — |
| LINT-6 | 25 E / 49 W | 25 E / 49 W | — |
| LINT-7 | 0 E / 117 W / 1 I | 0 E / 117 W / 1 I | — |
| LINT-7-static | 5 E / 1 W | 5 E / 1 W | — |
| **LINT-8** | **295 E** | **0** | **−295** |
| LINT-9 | 29 BLOCK | 29 BLOCK | — |
| LINT-10 | 0 E / 6 W | 0 E / 6 W | — |
| PLACEMENT | 0 E / 33 W | 0 E / 33 W | — |
| **TOTAL** | **374 E / 359 W / 29 B / 2 I** | **79 E / 359 W / 29 B / 2 I** | **−295 E, nothing else** |

**Documented delta: LINT-8 (no `rotz ≠ 0` on any `patch` / `stain` element) 295 → 0.**
**Added findings: 0.** The residual 79 errors belong to other WPs — LINT-4b (49, species) to
K4(b), LINT-6 (25, bollards) to K4(c)/K2/S1, LINT-7-static (5) to CB-3.

`LINT-10`'s 6 warnings are unchanged and include `scene07:173` and `sceneD3:198`, both mine.
They are `jitter=` kwargs the linter cannot classify and asks the owning WP to adjudicate; both
are **size/interval** variation (`§1.2 X2` keeps those) rather than placement, and neither is a
decal row, so they are left for the CB-10 pass with their classification recorded here.

---

## 4. `ground_kit.py` self-check — 33/33 PASS, and what moved

`python3 ground_kit.py` → exit 0, `ground_kit 자기검산 — 전 항목 통과`.

**Prim counts.** Nine `plaza_granite` scenes drop **7 prims each** (1 patch + 6 weeds):
01 43→36 · 05 40→33 · 14 42→35 · 18 42→35 · 20 43→36 · 21 42→35 · C1 43→36 · N1 37→30 ·
N3 43→36. Every other profile is unchanged in count.

**`frame_budget` movement (spec §6.2-K1 predicted exactly this).**
B2 area-share: `scene08` 81.9 → 44.8 % · `scene19` 92.4 → 68.8 % · `scene15` 87.6 → 83.2 % ·
`sceneN1` 76.7 → 79.9 % · `scene05` 68.2 → 69.3 %.
B5 near-field decal count: `sceneD2` 6 → 5, **the only new soft warning in the library**.
All B1–B5 are soft gates; no hard gate (B6–B12) moved anywhere.

**δmax movement** is GT-9's footprint working as designed — a 0.272 m tuft sits closer to the
edge than a 0.10 m cube, so the GT-E5 ramp clamps harder: `plaza_granite` family 0.1182 →
0.0060–0.0103 (weeds gone), `C2`/`C4`/`15` → 0.0798, `02` → 0.0867, `08` → 0.0947,
`16`/`N5` → 0.1041, `03`/`17`/`D3`/`N2`/`N4` → 0.1121, `13` 0.1182 (unclamped).

**GT-9 numbers, for the ledger.** Native exposure `zmax` **0.1229 m**; ceiling scale
**0.12 / 0.1229 = 0.9764** → exposure **0.1200 m**, footprint **0.2723 m**. Largest shipped
height 0.1182 m (`scene13`) → scale 0.9618, footprint 0.2683 m. **25 of 85 clumps clamped, 0
dropped.** Census **85 instances / 13 scenes**, not the intake's 139 / 22 — A1's own text
deletes `plaza_granite`'s weed row (−54 over 9 scenes). Recorded as ledger watch item **W6**.

---

## 5. GATE-1 — round `260731_w3_cb2`

Channel identical to the frozen judge round: `NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 ·
NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 · NEGOBS_DETAIL_ROUGH_GAIN=0`, GPU-exclusive under
`flock /tmp/negobs_gpu.lock`, sequential, one process per scene.

**Order-prefix rule.** The five gate cuts are the **first five entries of `grid_views()`**, and
`NEGOBS_VIEWS` filters while preserving dict order (`scene_common.py:3304-3307`), so the
rendered sequence is byte-for-byte the prefix a full 13-cut round would produce. Runner lived in
the scratchpad — `scripts/rounds/` is X1-owned and was not touched.

| scene | s | cuts | rc |
|---|---|---|---|
| scene03 | 27.2 | 5 | 0 |
| scene07 | 30.7 → re-rendered twice (§7) | 5 | 0 |
| sceneC2 | 29.2 → re-rendered once (§7) | 5 | 0 |
| scene01 | 25.3 | 5 | 0 |

**Regression v2.1 vs `260730_w2d_fix`** (`Docs/reports/regr_260731_w3_cb2.json`):

```
scene01/03/07 : 15 cuts — FAIL 0 · WARN 6 · INFO 1 · PASS 8
sceneC2       :  5 cuts — FAIL 0 · WARN 0 · INFO 0 · PASS 5
```

No DARK, no BLOWN, no WHITE, no OCCL anywhere. The six warnings are:

- `scene07` **FRAME ×4** (h0.3_d2 28 % · h0.9_d5 17 % · h0.3_d5 12 % · h0.3_d10 11 % occupancy
  shift) — this **is** the deliverable. Frame occupancy is what changes when 24 rectangles
  become 9 lobes.
- `scene01 preset_h0.3_d2` **UNCHANGED** and `scene03 preset_h0.9_d2` **UNCHANGED** — the
  batch's changes do not reach those two frames. Honest and worth stating: scene01's near cut
  looks along a stretch of plaza that carried neither the deleted patch nor a weed.

**Baseline retirement.** Per spec §7.3 and GT-8, `Docs/reports/regr_260730_w2d_fix.json` stops
being the comparison baseline **at this commit**. `Docs/reports/regr_260731_w3_cb2.json` is the
CB-2 stamp; the library-wide replacement is stamped at GATE-2. Every later CB (GT-1, GT-5, GT-7,
GT-11, GT-13) must name which baseline it was checked against — ledger watch item W4.

---

## 6. Eyes — the pilot's named acceptance criterion

`scene07 pt_noon_preset_h0.3_d5`, W2 above / CB-2 below:

- **W2**: three leaf carpets, each an unmistakable hard-edged rectangle laid on the decomposed
  granite, plus a fourth rectangle mid-frame. Straight edges on all four, none of which is a
  construction joint, a saw cut or a kerb.
- **CB-2**: the same four are irregular lobes. **Zero straight edges on any decal in the
  frame.** The 절삭 patches that *are* saw-cut rectangles are still rectangles, now axis-locked.

`scene07 pt_noon_preset_h0.3_d2` shows the same on the near stain lobe (`dirt_1`, 0.59 × 0.43 m
at 0.83 m from the eye — near-field by design, which is what B5 is for).

`sceneC2` is visually near-unchanged in the five preset cuts (5/5 PASS, no block movement):
the section skins are a small-area material correction on faces the preset eyes mostly graze.
They read in the mise-en-scène cuts and in 통람 v3's crest close-up, not here. **Stated plainly
rather than claimed**: C2's F3 delta at the preset viewpoints is subtle.

---

## 7. Two defects this pilot caught, and the fixes

Both were found by **looking at the render**, not by a gate — which is the argument for GATE-1
existing at all.

1. **Feather cards laid flat at z = 0 over a 4.2 m descent.** `scatter_debris` calls
   `ground_fn(px, py)` inside `except Exception: pass` (`scene_common.py:2368-2381`). scene07's
   own `path_z(x)` takes **one** argument, so passing it directly did not raise — it silently
   fell back to the flat `z` argument and hung a band of leaves in mid-air across the frame.
   Fixed with `lambda x, y: path_z(x)`, and the reason is now a comment at the call site so
   nobody "simplifies" it back.
2. **The feather region was derived like a band along a line.** `build_carpet_mask` first
   emitted `line` + `width` (the `build_edge_break` convention). Growing a bbox by half that
   width inflates it by the mask's own diameter and throws cards a metre and a half past the
   carpet onto whatever plate is there. The request now carries an explicit `region` grown by
   the **outer feather only**, plus a `feather_clip` host-plate box; scene07 clips to the
   corridor (`|y| ≤ 1.66`) and to the courtyard.

A third, smaller correction was made before rendering: `_snap_module` originally snapped on any
`unit_cell`, which would have quantised `alley_concrete`'s 0.65 m² repair patch onto its **3.0 m
contraction-joint bay** (→ 9 m², destroying the `patch_area_mean` statistic DEC-3 exists to
preserve). Snapping is now restricted to paver-scale modules (`cell ≤ 1.0 m`), which covers
`plaza_granite` 0.6 · `plaza_water` 0.6 · `sidewalk_block` 0.3 · `levee_paved` 0.2 and excludes
the contraction bay and the two 0.145 m plank widths.

---

## 8. Decisions taken, with their spec citation — for review

1. **`plaza_granite` loses its weed row and one patch, library-wide (9 scenes).** §10.5's A1 and
   DEC-3 rows say *"scene01's `plaza_granite` weed count → 0"* and *"scene01's plaza patch count
   drops 2 → 1"*. They name the **profile**. K1 took the literal profile-level reading rather
   than special-casing scene01. This is the single largest blast radius in CB-2 and the easiest
   thing to reverse (one tuple in `GROUND_PROFILES`). Flagged in the ledger as W6.
2. **Free-form stains become lobes.** DEC-1 defines the primitive; §10.6's all-scene checklist
   forbids a decal edge that is not a joint / saw cut / kerb. A soiling blot has none of those,
   so it is the primitive's first consumer. `grime_band` and `tire` keep their rectangles.
3. **`_blot_ring` is normalised to max radius 1**, so the lobe inscribes its `(rx, ry)` box and
   its AABB equals the rectangle it replaces. Without it every element's registered footprint
   would breathe by ±`rough`, which `frame_budget` and the GT-E ladder must not have to guess at.
4. **The weed asset is authored inside `ground_kit`, not through an injected callback.** GT-9
   covers 22 scenes; K1 owns one file. An injected `veg=` callback would have needed 16 scene
   files it does not own, so `_add_weed_asset` mirrors `add_vegetation`'s contract (reference on
   a **child** Xform, per-asset `metersPerUnit`, `SetInstanceable(True)`) with a documented
   cube fallback when the asset or the stage is absent. The module still does not import
   `scene_common`.
5. **`VEG_ASSET_DIR` uses `realpath`, not `abspath`** — `scenes/{main,batch1}/ground_kit.py` are
   symlinks, so `abspath` would have resolved the asset root to `scenes/main/assets/...`.
6. **The patch module comes from `pave["module"]` after `overrides`, not from the `unit_cell`
   ledger.** scene03 forces `module=(None, None)`; reading the ledger instead would have snapped
   its scene-authored `sites` onto a 200 mm grid the scene has disowned.

---

## 9. Files touched

```
ground_kit.py                                   (K1)
scenes/main/scene07_temple_stone_path.py        (S3)
scenes/main/scene10_park_deck_switchback.py     (S3)
scenes/batch1/sceneC2_leaf_stairs.py            (S3)
scenes/batch1/sceneD3_drainage_channel.py       (S3)
Docs/audit_v4/gt_changes_w3.md                  (GT-8 / GT-9 landing records — §4 of that file
                                                 is filled by the owning WP at land)
Docs/reports/w3_cb2_v1.md                       (this file)
Docs/reports/regr_260731_w3_cb2.json            (GATE-1 stamp)
look_check/{scene01,scene03,scene07,sceneC2}/260731_w3_cb2/**
look_check/logs/260731_w3_cb2*
```

`scenes/main/scene03_riverbank.py` and `scenes/main/scene12_riverside_deck.py` are S3-owned and
were **not** edited — 03's F3 delta is entirely ground-kit-side and 12's rows are CB-10.

---

## 10. Carried to CB-10 / later windows

- **03-B · 03-C · 03-D** — blocked on P-7 evidence and on K4(b) species (§2).
- **E3** D3 boundary fence — CB-10.
- **12** B3 reeds · N-A7 riprap — CB-10.
- **`LINT-10`** on `scene07:173` / `sceneD3:198` — adjudicate as size/interval keeps in CB-10.
- **G-6 / DEC-2 drift bias** — WINDOW 5 / CB-11, on T2's plates. The gravel typology the
  evidence-closer routed (rill / edge-accumulation / bead-sheet) is **not** implemented here.
- **σ_LF / B45 / B30** — not measured at GATE-1 (it is a GATE-2 instrument). The decal masks
  change ground content in both directions; spec §7.3's carry-over warning applies.
