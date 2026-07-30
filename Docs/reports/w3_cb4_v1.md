# W3 CB-4 — K3 `building_kit` + `facade_kit` (v1)

> **Wave**: W3 · **Window**: 1 · **WP**: K3 · **CB**: CB-4 · **Date**: 2026-07-31
> **Branch**: `feat/realism-v1` · **Spec**: `Docs/briefs/w3_execution_spec_v1.md` §4.2 K3 · §5.2 CB-4 ·
> §6.2 K3 · §7.2 GATE-1 · §8 GT-12 · §10.8 BS-4
> **Files owned and written**: `/building_kit.py` · `/facade_kit.py` ·
> `scenes/main/building_kit.py`, `scenes/batch1/building_kit.py` *(new symlinks)*
>
> **Verdict: PASS.** Suite **180/180** (was 135/135, +45 checks). The mandated
> `out_max > 0` check is **RED on the pre-CB-4 tree (73 + 712 findings) and green after**.
> `geom_invariance_check` **33/33** with a controlled A/B showing a **zero** hash delta.
> `placement_lint` output **byte-identical** to the pre-CB-4 arm. GATE-1 pilots **20 · 21**
> under the GPU lock: **FAIL 0**, CB-4-attributable delta at the **noise floor**
> (0.07–0.43 LSB, 0 block movement on 10/10 cuts).

---

## 0. What landed

| Row | Status | One line |
|---|---|---|
| **B-F1** glazing burial | **DONE** | 62/62 buried glazing prims un-buried; three distinct burial mechanisms covered, not one |
| **B-F1** `out_max > 0` self-check | **DONE** | `[11]` + `[11a]`; RED before, green after — this is the row that unblocks adoption |
| **B-F2** bay count from `W` | **DONE** | `shopfront_bays(W, tier)`; `prim_budget` grew a `W` term; `BUDGET` v2 re-baseline (4 cells) |
| **B-F3** `lod_dist` from the judged eye set | **DONE (opt-in)** | `judged_eyes()` / `eye_distance()`; measured 12/89 mis-tiered |
| **BS-4** `kind="backdrop"` | **DONE (opt-in)** | `facade_in_frame()` / `should_backdrop()`; 28/89 out of frame, −649 prims if wired |
| **facade AC-unit jitter KEEP** `[ruled §1.2]` | **DONE** | `facade_kit.py` AC u-offset documented as a KEEP with its real-world reason |
| symlinks (R3 §7.4 gap) | **DONE** | `building_kit` had no symlink in `scenes/`; both added |

**Nothing is wired to a scene.** No scene file imports `building_kit`, and the two
`facade_kit` entry points `scene_common.build_building` *does* call
(`build_plinth`, `build_aircon_units`, `build_fire_access_marks`) are byte-unchanged in
behaviour — proven empirically in §5.2, not asserted.

---

## 1. B-F1 — the glazing was 100 % buried, and the suite could not see it

### 1.1 The defect, re-measured

`Facade.world(u, out, z)` documents `out` as *"the distance **outward** from the wall face
(always positive)"*. Every glazing call site passed a **negative** value, so the pane was
pushed **into** the solid mass. Survey R3 §5.1 measured 62 of 62 `GLASS` prims invisible.

Re-measured here against **every overlapping mass box** (a stricter test than R3's, which
only looked at the sign of `out`), on the pre-CB-4 tree at HEAD `d7494f4` `[measured]`:

| element | buried inside | margin | pairs |
|---|---|---|---|
| `Win_{f}_{b}` | `Shell` | −0.0800 m | 40 |
| `ShopGlass_{b}` | `Shell` | −0.1000 m | 12 |
| `FireMark_0_{f}` | `Core_0` | **−0.5880 m** | 8 |
| `WinBand_{f}` | `Shell` / `Podium` | −0.1000 m | 6 |
| `CoreStrip_{i}` | `Core_0` | −0.0300 m | 3 |
| `EntryGlass` | `Podium` | −0.0700 m | 2 |
| `CurtainGlass` | `Podium` | −0.0750 m | 2 |
| **total, 6 kinds × 4 tiers** | | | **73** |
| W ∈ {8,12,28,40} × `base_z` ∈ {−2.15, 0, 3.4} sweep | | | **712** |

Two of these were **invisible to R3's own audit** because their `out` was already
positive:

* **`CoreStrip` sat at `out = +0.55` and was still 30 mm inside its own core.** The
  apartment stair/lift core protrudes `CORE_PROUD = 0.60`, so a positive `out` proves
  nothing.
* **`FireMark` — the statutory red triangle — sat 588 mm inside the core.** The single
  40 m fire-access station lands dead centre on the facade, which on a `W = 24 m` slab
  with one core is exactly the core's centre line.

A third mechanism only appears on offices: `build_mass` keeps the **podium** at the full
footprint and sets the **tower** back `SETBACK_OFFICE = 1.20`, so the surface in front of
a ground-floor attachment is the podium, not the shell.

### 1.2 The fix — one mechanism, not seven patches

```
Plan.out_at(u0, u1, z0, z1) -> outward face of the outermost solid volume covering
                               that facade window, floored at 0.0 (the facade plane)
```

fed by a **pure** `mass_faces(p)` that describes every solid volume of a building as
`(u0, u1, z0, z1, out_face)`. Every `glass`/`sign`/`decal` placement now asks where the
wall is and sits `fk.WALL_PROUD = 0.005 m` proud of it — the same 5 mm figure
`scene_common.build_building` settled on at its `WIN_EPS` block
(`scene_common.py:2637-2645`), for the same reason: the shell is a **solid** box, so
without reveal geometry the deepest expressible recess is zero and a coplanar face
z-fights. This satisfies **GT-12** ("glazing moves 5 mm proud").

Call sites converted: `build_window_bands` (bay · band · curtain, and the mullion band
rides the same reference so it stays proud of its glass) · `build_entrance` ·
`build_core` · `build_unit_number` · `_fire` · `fk.build_shopfront` (new `wall_out=`
parameter).

Two side fixes the check forced out:

* **`build_unit_number`** — on a narrow slab (`W ≈ 8 m`) the 동 번호 plate half-overlapped
  the core and 0.515 m of it ended up inside. It now snaps **onto** the core, which is the
  canonical Korean position (above the communal entrance) rather than a compromise.
* **`fk.build_fire_access_marks`** gained `out_fn(u, z)`, so each station sits on whatever
  wall is really at its coordinate. Default `None` = the old flat `out`, which is why
  `scene_common`'s live call is unaffected.

`fk.build_shopfront`'s `inset` parameter is **retained but a no-op**, with the reason
written into the docstring — deleting it would be a signature change, and a signature
change is a 24-call-site edit (spec §6.2 K4-(c) doctrine, applied here by analogy).

### 1.3 The new self-check — why 135/135 was green while nothing was visible

`[5]` counts prims against a budget · `[7]` checks `z ≥ base_z − 0.05` · `[8]` checks path
uniqueness. **None of them asks whether a facade prim is on the outside of the wall.**

`[11]` asserts, for every prim whose **material role** is `glass`/`sign`/`decal`,
`out_max > 0` against **every mass box overlapping it** on both the tangent and the z axis.
It is a **role** check, not a path-name heuristic: `_MockKit` now records the material, and
the check builds with one sentinel material per role, so it cannot be fooled by a rename
and it picks up roles added later. (`_run`'s legacy `Mtls("sh","gl","pa")` collapses
stone/metal/sign/decal onto `parapet` through the fallback chain, which would have made a
role check meaningless — hence a separate `_ROLE_MTLS`.)

`[11a]` cross-validates `mass_faces(p)` **prim-for-prim** against the boxes
`build_mass`/`build_core`/`_b_backdrop` actually emit, for every kind × tier, plus a check
that every mass prim carries a mass role. Without it the visibility check could be
satisfied by a stale model — the one failure mode that would matter.

| | pre-CB-4 (HEAD `d7494f4`) | post |
|---|---|---|
| `[11]` standard grid (6 kinds × 4 tiers) | **73** burial pairs / 109 visible-role prims | **0** / 125 |
| `[11]` W × `base_z` sweep | **712** | **0** |
| suite total | 135/135 (blind) | **180/180** |

Reproduction of the RED state:
`/tmp/.../scratchpad/prove_prefix_fail.py` runs the shipped algorithm against
`git show HEAD:building_kit.py` / `:facade_kit.py`.

---

## 2. B-F2 — the bay count now comes from `W`

`_b_shop_house` used `nb = 4 (near) / 3 (mid) / 1 (far)` with `bay_w = max(3.0, W/nb)` — a
floor that can only ever make bays **wider**. On scene20's building C (`W = 28 m`, mid) that
gave three butted glazing panels of **8.93 m** each, against a real Korean neighbourhood
shopfront bay of **3.0–4.5 m**.

```
shopfront_bays(W, tier) = clamp(round(W / 3.60), 1, SHOP_BAY_CAP[tier])
SHOP_BAY_CAP = {near: 10, mid: 8, far: 0, silhouette: 0}
```

`3.60` is survey R3 §5.2's prescribed divisor. The cap is a **prim guard, not a design
target** — a bay costs 2 prims. `far`/`silhouette` build no shopfront at all (survey §6's
LOD table).

| facade | before | after |
|---|---|---|
| `W = 28` mid (scene20 C) | 3 bays, **8.93 m** | 8 bays, **3.50 m** |
| `W = 24` near | 4 bays, 6.00 m | 7 bays, **3.43 m** |
| `W = 12` mid | 3 bays, 4.00 m | 3 bays, 4.00 m (unchanged) |

**Out of band, library-wide: 3 of 89 buildings** — all cases where the prim cap binds on an
extreme facade, and all only slightly over `SHOP_BAY_MAX`:
`scene06 #3` `W = 38` mid → 8 bays at **4.75 m**; `sceneN3 #0/#1` `W = 48` near → 10 bays at
**4.80 m**. `bay_width()` reports these rather than hiding them.

### 2.1 `prim_budget` grew a `W` term, and `BUDGET` was re-baselined

`prim_budget(kind, tier, W=None)` adds `2 × (bays(W) − bays(24 m))` for the two retail
kinds — exactly the shopfront's own per-bay cost. Nothing else grows monotonically with
`W`: `build_window_bands` bay mode is capped at 4 columns and is already at that cap at
24 m, and the balcony run count is bounded by `_unit_runs`. `W=None` reproduces the old
two-argument behaviour exactly (checked).

`BUDGET` **v2 re-baseline**, same rule as v1 (`cap = measured + 3` at `BUDGET_REF_W = 24`):

| cell | v1 | v2 | reason |
|---|---|---|---|
| `shop_house` near | 59 (56) | **65 (62)** | bays 4 → 7 |
| `shop_house` mid | 30 (27) | **38 (35)** | bays 3 → 7 |
| `low_shop` near | 36 (33) | **44 (41)** | bays 3 → 7 |
| `low_shop` mid | 17 (14) | **27 (24)** | bays 2 → 7 |
| every other cell | — | **unchanged** | B-F1 moves glazing, it does not create any |

### 2.2 33-scene prim scan, against the published figure

| | prims |
|---|---|
| current `scene_common.build_building` | 4,546 (of which 2,137 windows) |
| `building_kit` **as published by R3** | 1,855 (**−59.2 %**) |
| `building_kit` **after CB-4**, `eyes` off | **2,069 (−54.5 %)** |
| `building_kit` after CB-4, **`eyes` on** (B-F3 + BS-4) | **1,420 (−68.8 %)** |

**The −59.2 % headline moves to −54.5 %.** The +214 prims are B-F2 buying real Korean bay
rhythm on 39 retail buildings, and they are bought back several times over the moment B-F3
and BS-4 are wired: −649 prims (−31.4 %) from the same 89 buildings. Both figures should be
quoted in BS-2's adoption case; the −59.2 % one should not be quoted again.

**Carried-forward budget overruns (pre-existing at HEAD, not caused by CB-4, reproduced
identically before and after):** `scene13` apt/mid 26 > 23 · `scene21` office/mid 16 > 15.
Both are the apt balcony-run and office-tier cells, neither of which CB-4 touches.

---

## 3. B-F3 — `lod_dist` from the judged eye set

The default `dist` was `abs(facade plane coordinate)`, i.e. it assumed the camera sits at
the origin and ignored both the eye's standoff and the building's lateral offset.

```
judged_eyes(gy)  -> [(-d, gy, h)] for h in (0.3,0.9,1.8), d in (2,5,10)   # grid_views
eye_distance(p, eyes) -> min over eyes of |eye - nearest point of the facade rectangle|
```

Measured over all **89** `bd` dicts in the 33 scenes, using **each scene's own `gy`** parsed
from its `sc.grid_views(...)` call (21 scenes pass `0.0`; `scene01` −2.75, `sceneD4` −3.6,
`scene10` 0.4; 4 pass a non-literal and fall back to 0.0) `[measured]`:

| | this measurement | R3 §2 as published |
|---|---|---|
| wrong LOD tier | **12 / 89 (13.5 %)** — 3 promoted, 9 demoted | 16 / 89 (18.0 %) |
| `d_default − d_true` mean | **−2.6 m** | −4.4 m |
| median | **−2.0 m** | −5.0 m |
| range | **−46.1 … +10.0 m** | −49.0 … +10.0 m |

**Discrepancy, stated rather than reconciled away.** The spec's own backdrop policy
(§10.8) defines `d_true` as *"nearest judged eye to the nearest point of the facade
rectangle"* — a **min over the eye set** — and that is what shipped. R3's convention is not
recoverable from its text; a single-eye variant reproduces R3's median (−5.0) and lower
bound (−49.0) at the `h0.3_d5` eye and its upper bound (+10.0) at `h0.3_d10`, so R3
appears to have aggregated per-cut rather than taking the minimum. **The spec is law, so
the min-over-eyes figure is the one to carry forward.** No `bd` in the tree sets
`lod_dist`, so this defect is currently live on all 89.

`p.z_ceil = fk.frame_ceiling(d_true)` is exposed for backdrop policy (2) ("build nothing
above `z_ceil`"). **Enforcing it is BS-2/BS-3, not CB-4** — CB-4 computes it and stops.

---

## 4. BS-4 — `kind="backdrop"` for out-of-frame buildings

`facade_in_frame(p, eyes, half_deg=30)` applies the spec's rule to the **whole facade
segment**, not its centre: a long wall can be out of frame at both ends and still cross the
view axis, and a point behind the eye never counts.

**±30° is measured, not a convention**: the capture is 1920×1080 (`scene_common.py:852`)
and vFOV is 36° (`fk.CAM_VFOV`), so the horizontal half-angle is
`atan(tan 18° · 16/9) = 30.006°`. The scenes' own camera checks already write it as ±30°
(`scene21:181`).

Library-wide: **28 of 89** buildings are outside ±30° of every judged eye. Wiring
`eyes=` demotes them to the 3-prim silhouette builder — a **negative** prim cost.

On the five repeated-brick scenes R3 examined (12 buildings) `[measured]`:

| scene | building | verdict | prims |
|---|---|---|---|
| scene01 | `D` (#3) | out of frame → backdrop | 34 → 3 |
| scene20 | `E` (#2) | out of frame → backdrop | 14 → 3 |
| sceneC1 | `#1` | out of frame → backdrop | 6 → 3 |
| scene21 | `#1` | in frame, but `d_true` 18 → 28.4 m ⇒ near → **mid** | 62 → 40 |
| | | **scene totals** | 429 → 362 |

**3 of 12, not R3's 4 of 12.** The one disagreement is `scene01`'s building `L` (#1): its
east end bears **−29.0°** from the `h*/d10` eye — **1.0° inside** the ±30° limit, so under
the spec's literal "no point of the facade" rule it is in frame. Handing this to **S1** and
**X3**: it is a boundary case, and it is the difference between building `L` getting 56
prims or 3. Note the spec §10.8 itself already **declines** R3's out-of-frame call on
scene20's building `D` for the same reason ("computed in frame for `oblique_overview`
11.1°"), and the implementation agrees with the spec there.

`backdrop_demote=False` keeps the A/B control arm available.

---

## 5. Verification

### 5.1 CPU pre-flight (spec §6.1)

| gate | result |
|---|---|
| `python3 -m py_compile building_kit.py facade_kit.py scenes/{main,batch1}/building_kit.py` | clean |
| `python3 building_kit.py` | **180/180** + 33-scene scan |
| `python3 scripts/geom_invariance_check.py` | **R-4 33/33 · R-6 33/33 PASS** |
| `python3 scripts/placement_lint.py --scenes all` | exit 1 (baseline violations), **byte-identical** to the pre-CB-4 arm |
| `NEGOBS_SMOKE=1` per scene touched | n/a — **no scene file touched** |

### 5.2 Controlled A/B — the tree was mutating, so the delta was isolated

Concurrent W3 agents were writing `ground_kit.py` (13:14) and `batch1_common.py` +
10 scene files while this WP ran, and a naive before/after diff of `placement_lint` showed
their work, not mine (`jit_call_sites` 24 → 5 is CB-3; the patch-count and prim-count
movement is CB-2). One `geom_invariance_check` run even aborted with
`scene10: KeyError: 'rough'` — a transient mid-write state of another agent's file.

So the delta was isolated by swapping **only** `building_kit.py` + `facade_kit.py` between
HEAD and CB-4 on an otherwise **frozen** tree (md5-verified frozen before and after each
pair):

| A/B | result |
|---|---|
| `geom_invariance_check` per-scene hashes, HEAD kit vs CB-4 kit | **IDENTICAL, 33/33** |
| `placement_lint --scenes all` full output, HEAD kit vs CB-4 kit | **IDENTICAL** — CB-4 adds 0 findings |

This is the direct proof that CB-4 changes **no live scene geometry**: the kit is unwired,
and the three `facade_kit` functions `scene_common.build_building` does call are
behaviour-identical (`build_plinth` untouched · `build_aircon_units` comment-only ·
`build_fire_access_marks` gained `out_fn=None`, and with `None` it computes
`o = float(out)`).

### 5.3 GATE-1 pilots 20 · 21 (spec §7.2)

Round `260731_w3_cb4`, 5 cuts each in the exact `grid_views` **order prefix**
(`preset_h0.3_d2 · h0.3_d5 · h0.3_d10 · h0.9_d2 · h0.9_d5` — these are the first five in
grid order, so nothing is discarded). Channel identical to the frozen judge round:
`pt · PT_FAST=1 · LOOK_V1=1 · DETAIL_SCALE=2 · DETAIL_ROUGH_GAIN=0`. GPU exclusive under
`flock -w 7200 /tmp/negobs_gpu.lock` (queued behind CB-2's pilot), sequential, one process
per scene. Stamped with `scripts/stamp_round.py`. Written to
`look_check/_experiments/gates/scene{20,21}/260731_w3_cb4/` — a gate probe, not a judgement
grid (`look_check/README.md` §1).

| | scene20 | scene21 |
|---|---|---|
| cuts / exit / wall clock | 5 / 0 / 27.6 s | 5 / 0 / 29.8 s |
| vs baseline `260730_w2d_fix` | **FAIL 0** · WARN 1 · INFO 2 · PASS 2 | **FAIL 0** · WARN 2 · PASS 3 |

**The two scene21 WARNs are not CB-4's.** They are `[FRAME]` block-occupancy shifts of
22 % (`h0.3_d2`) and 13 % (`h0.3_d5`). A **control arm** (`260731_w3_cb4ctl`: pre-CB-4 kit,
same working tree, tree md5-frozen across both renders) reproduces them **to the digit** —
same 22 % / 13 %, same max deviations 95/255 and 85/255. They belong to the concurrent
in-flight ground/decal work, and they are exactly the baseline movement spec §7.3 predicts:
*"`regr_260730_w2d_fix.json` stops being the comparison baseline at CB-2, when
`_obb_aabb → _box_aabb` changes every patch and stain AABB."*

**The CB-4-attributable delta, control arm → CB-4 arm on the identical tree:**

| | scene20 | scene21 |
|---|---|---|
| verdict | FAIL 0 · WARN 3 `UNCHANGED` · INFO 1 · PASS 1 | FAIL 0 · WARN 3 `UNCHANGED` · INFO 2 |
| mean difference | 0.07 – 0.43 LSB | 0.26 – 0.42 LSB |
| pixels over 4 LSB | 0.002 – 0.076 % | 0.060 – 0.095 % |
| block movement | **0 on all 5** | **0 on all 5** |

`UNCHANGED` is the regression checker reporting *"practically identical to the previous
round"* — i.e. the **noise floor**, which is precisely what the brief predicted for an
unwired kit ("scenes unchanged → expect noise-floor regression; the pilot proves no
accidental wiring"). PT is stochastic per run, so the PNGs are not bit-identical; the
metrics are.

**GATE-1 CB-4: PASS.**

### 5.4 GT

**GT-12** (`building_kit` B-F1 glazing un-burial, 23 scenes, above ground, no GT — action
"None; OCCL re-check only"). No GT ledger row is due: the kit is unwired, the OCCL
baseline cannot move, and §5.2 proves the 33 geometry hashes are unchanged. The GT-12 row
becomes live at **BS-2 adoption**, not here.

---

## 6. Interaction notes — `urban_kit` far tier (T4-Q1 `[supervisor]`)

`urban_kit` is the authority on the far tier; `building_kit` neither reads nor duplicates
it. Recording the ruling where the building track will look for it:

* **The far-tier override stays.** Its substance is **`metallic_constant` 1.0 → 0.0**, not
  the albedo scale. Every material in the eight `bldgs_01_distant/Building_*` authors
  `metallic_constant = 1.0` with `metallic_texture_influence = 0.0`, and
  `SimPBR.mdl:792` evaluates `metallic = lerp(metallic_constant, ORM.z, influence) = 1.0`
  `[measured — urban_kit.py:305-310]`. Eight fully **metallic** skyline walls is the defect;
  a metal BSDF has no diffuse lobe, so an albedo cap on it is meaningless.
* **The albedo scale is a no-op guard.** The tier's worst case is
  `house_wall_001 0.874 × diffuse_tint 0.611 = 0.534`, already inside the ≤ 0.55 project
  band `[measured — urban_kit.py:293]`. It stays as a guard, not as the fix.
* **Consequence for BS-3/BS-4.** A `kind="backdrop"` building and a far-tier **asset**
  backdrop are different instruments and must not be swapped for each other in a gate:
  `building_kit`'s backdrop is 3–4 procedural prims with the scene's own materials and no
  GI signature of its own, whereas the asset tier carries the `[ruled §1.11]` material
  override and **moves the judged ground band** (Δσ_LF up to −0.32, ≈4× the noise floor —
  C-20). Spec §10.8-(4) therefore re-gates any far-tier binding change on **B45/B30**, and
  that obligation belongs to the asset arm only. BS-4 as implemented here touches no
  material and cannot move σ_LF.
* **Dressing.** Quirk 7 (asset backdrops must be dressed with the `facade_kit` attachment
  layer) is BS-6 and lands in the adoption batch. `facade_kit`'s attachment builders are
  ready for it: they take a `Facade`, not a `bd`, so they bind to an asset's measured
  bounding box the same way they bind to a procedural shell.

---

## 7. New findings and open items

| # | Finding | Evidence | Owner |
|---|---|---|---|
| **B-F7** *(new)* | **The office curtain wall floats in front of its own tower above the podium.** `build_mass` keeps the podium at the full footprint and sets the tower back `SETBACK_OFFICE = 1.20`, but the curtain wall is one prim on the facade plane. At `office/near` **75 % of its height (21.00 m of 27.95 m) stands 1.255 m proud of the tower face** `[measured]`. **Pre-existing** — before CB-4 it floated 1.125 m; un-burying it from the podium added 0.105 m. Invisible in every judged cut (the frame ceiling at 14 m is 2.27 m), which is why nothing caught it. Cheap fix: split the curtain glass at `z_pod` and reference each half with `out_at` — **+1 prim**, inside the current `office` near/mid budget (28/31, 12/15). **Recorded, not implemented**: it is a design change beyond CB-4's rows | `building_kit.build_mass` / `build_window_bands` | K3 → BS-2 |
| **BS-4 boundary** | `scene01` building `L` bears **−29.0°** from the `h*/d10` eye — 1.0° inside ±30°, so this implementation calls it **in frame** where R3 called it out. Worth 53 prims | §4 | S1 · X3 |
| **B-F3 convention** | 12/89 (13.5 %) mis-tiered under the spec's min-over-eyes rule vs R3's published 16/89 (18.0 %). R3's convention is not recoverable from its text | §3 | X3 (do not re-quote 18.0 %) |
| **Prim headline** | **−54.5 %** unwired / **−68.8 %** with `eyes` wired. R3's **−59.2 %** is superseded | §2.2 | BS-2 |
| **Carried forward** | `scene13` apt/mid 26 > 23 · `scene21` office/mid 16 > 15 — both pre-existing at HEAD, both outside CB-4's rows | §2.1 | K3 → BS-2 |
| **Not done here** | Window **reveals** (a real recess needs ~4 prims/bay) — parked to the spandrel decomposition. `fk.build_shopfront(inset=)` is kept as the hook | | K3 |
| **Not in CB-4** | **BS-1** `brick_red` `scale_m` 2.0 → 0.90–1.10 is K3's but is gated on a mortar-grid overlay render and **must not ship 0.87** (C-19); **BS-2/3/5/6** are the adoption batch | spec §10.8 | K3 |

---

## 8. Reproduction

```bash
python3 -m py_compile building_kit.py facade_kit.py
python3 building_kit.py                  # 180/180 + 33-scene scan + B-F1/B-F2/B-F3/BS-4 measurements
python3 scripts/geom_invariance_check.py # 33/33
python3 scripts/placement_lint.py --scenes all --rules Docs/briefs/placement_rules_v1.yaml

# the RED state of the new check, against HEAD d7494f4
git show HEAD:building_kit.py > /tmp/prefix/building_kit.py
git show HEAD:facade_kit.py  > /tmp/prefix/facade_kit.py
python3 /tmp/.../scratchpad/prove_prefix_fail.py     # 73 + 712 findings

# GATE-1 pilot (GPU exclusive)
flock -w 7200 /tmp/negobs_gpu.lock /tmp/.../scratchpad/run_cb4_pilot.sh
python3 scripts/regression_check.py \
  --before look_check/scene20/260730_w2d_fix \
  --after  look_check/_experiments/gates/scene20/260731_w3_cb4 \
  --only preset_h0.3_d2,preset_h0.3_d5,preset_h0.3_d10,preset_h0.9_d2,preset_h0.9_d5
```
