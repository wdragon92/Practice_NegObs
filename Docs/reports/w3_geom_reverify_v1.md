# W3 · WP-T3 — geometry re-verification on real USD stages

> **Wave**: W3 · **WP**: T3 (Track T, WINDOW 0) · **Date**: 2026-07-30 · **Branch**: `feat/realism-v1`
> **Spec**: `Docs/briefs/w3_execution_spec_v1.md` §4.1 (T3 row) · §5.3 (`T3 ─► CB-9`) · §6.2 (T3 obligation)
> **Owns**: this file only.
>
> **Release condition discharged**: spec §5.3 states `T3 ─────► CB-9 (scene06 may not be cut before
> the numbers are re-verified)`. Every S06-A number named in §2 C-3 and in survey B's A-1…A-4 tables
> is graded below as **CONFIRMED** or **CORRECTED with the measured value**. §7 lists what CB-9 and
> K4(d) must do differently as a result.

---

## 0. Verdict table — read this before touching `scene_common.py` or `scene06`

`[measured-usd]` = read back from a composed `Usd.Stage` built by the shipped builders (§1).
`[computed]` = closed-form re-derivation from the shipped code path. `[static]` = AST/grep census.

| # | Source claim | Verdict | Measured value | Ev |
|---|---|---|---|---|
| **1** | **scene06 landing "union outer radius swings 3.3000 → 3.3990 = 99.0 mm"** (survey B S06-A A-2, quoted as a headline; spec §2 C-3) | **CORRECTED — strike 99.0 mm permanently** | union rim swings **3.30000 → 3.30746 = 7.46 mm**; max corner radius **3.30748 = 7.48 mm**. RT-I R4's 7.5 mm reproduces exactly. 3.3990 is `3.30 × 1.03` — the tangential margin applied to a radius | `[measured-usd]` |
| **2** | landing outer corner radius **3.3075 m** | **CONFIRMED** | **3.307479 m** | `[measured-usd]` |
| **3** | `Spiral/Step_*` rim sawtooth **+17.6 mm** past `r_out`; corner radius **3.3176** | **CONFIRMED** | **+17.641 mm**; **3.317641 m** | `[measured-usd]` |
| **4** | `SpiralFascia` corner radius **3.3305**, rim sawtooth **+0.5 mm** ("fine — fine segmentation hides it") | **CORRECTED (conclusion survives)** | **3.334159 m → +4.16 mm**, 8.3× the claim. The survey applied the box-corner formula without the `rotX` tilt; the tilt swings the 780 mm-thick slab's corners tangentially. Still sub-5 mm, so "fine" stands | `[measured-usd]` |
| **5** | `Spiral/Step_*` r_in overwidth **2.27×** | **CONFIRMED** | **2.266×** (683.349 mm box vs 301.566 mm true chord at r_in 1.50) | `[measured-usd]` |
| **6** | `Landing/Seg_*` r_in overwidth **7.08×** | **CONFIRMED** | **7.0813×** (444.610 mm box vs 62.787 mm true chord at r_in 0.48) | `[measured-usd]` |
| **7** | `SpiralFascia` r_in width **111.9 mm (1.07×)** | **CONFIRMED (0.5 mm refinement)** | **112.393 mm, 1.0652×** | `[measured-usd]` |
| **8** | box widths **683.3 / 444.6 / 119.7 mm**; true widths @r_out **663.4 / 431.7 / 116.2 mm**; margin **1.030×** | **CONFIRMED, all six** | **683.349 / 444.610 / 119.720** and **663.445 / 431.661 / 116.233**; margin **1.03000** on all three | `[measured-usd]` |
| **9** | **23 coplanar overlap bands of 12.9 mm** along the landing top face | **CONFIRMED, and it is a floor not a total** | 23 adjacent pairs ✔; band width **12.95 mm** at exactly `r_out` `[computed]`, **13.42 mm** measured at `0.999·r_out`. But **123** of the 276 segment pairs overlap, **8.551 m² (49.4 % of the 17.322 m² covered footprint) is covered by ≥ 2 coplanar slabs**, max stacking depth **7** | `[measured-usd]` |
| **10** | fascia sawtooth **+153.6 mm / −38.4 mm**, 26× round the helix, **192 mm** amplitude | **CONFIRMED as the design line · CORRECTED as built** | design line exactly **+153.600 / −38.400**, amplitude **192.000 mm** `[computed]`. **As built the whole fascia top line sits +16.34 mm above its own design line** (§3 NF-1), so the measured lip is **+165.85 / −26.20 mm, amplitude 192.05 mm**, 26× round the helix ✔ | `[measured-usd]` |
| **11** | landing body runs **348 mm** up through the deck box | **CONFIRMED** | landing top **4.99800**, deck soffit **4.65000** → **348.0 mm**; landing top sits **2.0 mm** under the deck top (5.00000) ✔ | `[measured-usd]` |
| **12** | overlap footprint **3.0 m × 3.3 m = 9.9 m²** | **CONFIRMED as the bbox; refined** | overlap bbox x **2.000…5.000**, y **−13.000…−9.6925** → **9.922 m²**; **true intersection area 9.192 m²** | `[measured-usd]` |
| **13** | landing footprint **x 0.20…6.80, y −13.00…−9.70** | **CORRECTED** | **x 0.1925…6.8075, y −13.1904…−9.6925**. The back edge is **not** the y = −13.000 diameter: it is a 24-tooth sawtooth reaching **190.4 mm behind it** (§3 NF-2) | `[measured-usd]` |
| **14** | scene06 code comment: "the last segment overshoots 180 deg by **0.11 deg**" (`scene06:1237-1239`) | **CONFIRMED at r_out only — the comment is materially misleading** | at `r_out` the overshoot is **0.1039°** ✔; at `r_in` the same box overshoots by **21.10°**, i.e. **190.9 mm** of solid past the diameter. The comment's "no effect on reading or walking" is derived from the outer number and does not hold at the inner one | `[measured-usd]` |
| **15** | railing `outer_r = 3.36` stands **60 mm** outboard of the tread edge and **30 mm** outboard of the fascia face | **CONFIRMED** | post centre radius **3.360000**; tread `r_out` 3.30 → **+60.0 mm**; fascia `r_out` 3.33 → **+30.0 mm**; post outer face at **3.390** | `[measured-usd]` |
| **16** | prim counts **26 / 24 / 150** for `Spiral/Step_*` · `Landing/Seg_*` · `SpiralFascia` | **CONFIRMED** | 26 / 24 / 150 | `[measured-usd]` |
| **17** | spec §10.5 S06-A item 1 fallback: "cap Δθ so the **r_in overwidth ≤ 1.05×** — for the landing that needs **seg ≈ 165**" | **REFUTED — no value of `seg` can satisfy it** | the r_in overwidth ratio is `margin · r_out / r_in` = **7.08125 at every Δθ** (measured at seg 24 / 48 / 96 / 165 / 330 / 1000). Only the *absolute* overhang shrinks (190.9 → 27.8 → 4.6 mm). §4 gives the corrected criterion | `[computed]` |
| **18** | spec §10.5 S06-A item 7 / §8 GT-6: the convention fix also touches **13** (`build_helix_ramp`, car-park ramp) | **REFUTED** | `scenes/main/scene13_apartment_parking_entry.py` contains **zero** `build_arc_steps` / `build_helix_steps` / `build_helix_ramp` call sites. Its ramp is `sc.build_slope` × 3 (`scene13:846-852`). The spiral parking ramp lives in `scenes/archive_v3/scene13_helical_parkingramp.py` and is not in the wave | `[static]` |
| **19** | spec §10.5 S06-A item 7: **05 (10 `build_arc_steps` sites)**, **19 (4)** | **CORRECTED / CONFIRMED** | **scene05 = 12** call sites (`:997, 1092, 1102, 1115, 1126, 1138, 1162, 1171, 1197, 1358, 1423, 1436`); **scene19 = 4** ✔ (`:834, 860, 1025, 1043`); scene06 = 4 `build_arc_steps` + 1 `build_helix_steps` + 3 `build_helix_ramp` | `[static]` |
| **20** | **scene09 waterline z = −5.240** (survey B, scene09 fact table) | **CORRECTED** | the water plane is at **z = −5.190**. `compute_steps()` returns `water_z = steps[30].top + water_extra = −5.240 + 0.050`; `sc.build_water` puts the slab **top face** at `water_z`, measured **−5.18999999** on the stage. **−5.240 is the tread the water stands 50 mm above**, not the waterline | `[measured-usd]` |
| **21** | scene09 waterline at **x ≈ 11.92**; **bottom 6 steps submerged**; 36 steps; run **13.96** / drop **6.12**; landings at step 11 (x 3.74–4.94, z −2.040) and step 23 (x 8.68–9.88, z −4.080) | **CONFIRMED, all of it** | waterline x **11.920** (riser face of step 30, whose top is −5.240 and whose predecessor's top is −5.100 — the −5.190 plane cuts that riser); submerged tops **−5.24 / −5.40 / −5.58 / −5.78 / −5.96 / −6.12** = **6**; 36 steps; run **13.960**; drop **6.120**; landings exactly as claimed | `[measured-usd]` |
| **22** | S09-A `stair_flank_raking`: bearing **130.8°**, pitch **−5.5°**, range **14.60 m**, eye **3.04 m** over the water | **3 CONFIRMED / 1 CORRECTED** | bearing **130.815°** ✔ · pitch **−5.502°** ✔ · range **14.6017 m** ✔ · eye height over water **2.990 m** (3.04 is the height above the −5.240 tread, not above the water plane) | `[computed]` |
| **23** | C0-7: `build_railing_line` balusters satisfy the statutory **≤ 100 mm 안목** | **CONFIRMED** | measured on real cylinder prims: pitch **116.0 mm**, baluster Ø **18.0 mm**, **clear opening 98.0 mm** — uniform across the whole line, ≤ 100 mm ✔ | `[measured-usd]` |
| **24** | C0-7: "간살·손잡이 are inside the `LOOK_V1` gate, so **현행 렌더에는 간살이 0개**" | **CONFIRMED for the W1 v7/v8 renders · STALE for the current channel** | the gate is now `LOOK_GEO`, and `LOOK_GEO` defaults to 1 whenever `NEGOBS_LOOK_V1=1` (`scene_common.py:190-192`). **Every round runner since `run_260730_*` exports `NEGOBS_LOOK_V1=1`**, and spec §7.2 fixes the same channel for GATE-1. Balusters are **ON** in every W3-judged frame | `[static]` |
| **25** | C0-7: "scene01 — `build_railing_line` 사용 **0회**, 자체 구현" | **CONFIRMED** | 0 call sites in scene01; its rail is local at `scene01:1057ff` under `cfg["cue_railing"]` | `[static]` |
| **26** | C0-7: "scene02 — 계단 벽부 레일 2선만 공용 빌더; 피트 둘레 난간 3면은 로컬 `hrail()`" | **PARTLY CORRECTED** | scene02 now has **zero** `build_railing_line` calls — the stair guardrail was replaced by a statutory handrail (`stair_rail` dict, `scene02:198-199`; the old call is documented as removed at `scene02:177-180`). The pit perimeter is still local `hrail()` (`scene02:819-849`), so the two-rails-only silhouette defect stands, but the "2 of 3 implementations miss the statutory path" framing must be re-stated as **2 local implementations (01, 02) vs 1 shared builder** | `[static]` |
| **27** | C0-7: scene02 pit rail height = parapet 0.15 + `rail_h` 0.90 = **1.05 m**, below the 1.10 m guideline | **CONFIRMED** | `scene02:815-817` computes `base_z = 0.15`, `top_z = base_z + 0.9 = 1.05` verbatim | `[static]` |
| **28** | C0-7: "scene03/04/05 — 난간 기본 OFF" | **CONFIRMED** | `cue_railing` defaults `False` in scene03 (`:81`), scene04 (`:65`), scene05 (`:81`) | `[static]` |

**Census that K4(a)'s "prove the ≤ 100 mm gate on every railing call site" obligation needs**
`[static]`: **16 live `build_railing_line` call sites across 14 scenes** — 03 · 07 · 08 (×2) · 10 ·
11 (×2) · 14 · 17 · 20 · 21 · C1 · C2 · C4 · D3 · N4. **No call site overrides `baluster_gap`**, so
all of them inherit the 98 mm clear opening. **One call site disables balusters outright**:
`scene10_park_deck_switchback.py:1195` passes `baluster_r=0.0` (the `if LOOK_GEO and baluster_r > 0`
gate at `scene_common.py:1733` then skips the loop). scene10 is therefore the single scene where the
statutory infill is absent by construction, and it is the one row K4(a) has to adjudicate rather
than merely verify.

---

## 1. Method — what "re-verified" means here

`pxr` is absent from the project venv, and the scene mains require `sc.boot()` (Isaac Sim), so a
full-scene composition is not reachable on CPU. The measurement path used instead is **not**
authored-value recomputation: it builds a **real `Usd.Stage`** by calling the **shipped builders**
with the **shipped `PARAMS`**, then reads world-space geometry back out of the composed xform ops.

```bash
python3 -m venv /tmp/usdvenv && /tmp/usdvenv/bin/pip install usd-core numpy   # usd-core 26.8
```

- `scene_common.py` imports cleanly under plain CPython (`numpy`/`facade_kit`/`stair_kit` only at
  module level; `pxr` is a deferred import inside every function). `scenes/main/scene06_*.py` and
  `scenes/main/scene09_*.py` also import cleanly — `PARAMS`, `_step_deg()`, `_spiral_z_at()`,
  `_fascia_z()`, `_fascia_span()`, `compute_steps()` are all module level. So the values fed to the
  builders are the **shipped** ones, not transcribed ones.
- The stage is built with `sc.build_helix_steps` / `sc.build_helix_ramp` / `sc.build_arc_steps` /
  `sc.add_box` / `sc.add_cylinder` / `sc.build_water` / `sc.build_straight_stairs` /
  `sc.build_railing_line` at the exact call signatures used in `scene06:1211-1246`,
  `scene06:1287`, `scene06:1446-1466`, `scene09:1135`, and the scene03 railing call site.
  `mtl=None` throughout (`_bind_mtl` is a no-op on `None`) — materials do not move geometry.
- Every number is then read with
  `UsdGeom.Xformable(prim).ComputeLocalToWorldTransform()` applied to the Cube's exact local
  extent `[-1,1]³`, i.e. **exact world corners**, not a `BBoxCache` approximation. Solid queries use
  an exact analytic vertical-line/oriented-box intersection (invert the composed matrix, intersect
  three slabs). Footprint intersections use Sutherland–Hodgman convex clipping (exact), not a grid,
  except for the coverage-multiplicity map, which is a declared 20 mm grid.
- Rim profiles are 60-step bisections on the union of the segment footprints at 0.01° azimuth
  resolution (18 001 samples over the landing's 180°); the fascia lip profile is 60 001 azimuth
  samples at a probe radius of **3.26 m**, chosen because it lies inside **both** the fascia band
  (3.22–3.33) and the tread band (1.50–3.30), so the two surfaces are compared **at the same
  (x, y)** rather than through two separate analytic models.

**CPU pre-flight (spec §6.1).** This WP writes one Markdown file and no Python, so `py_compile` has
no target and no scene is touched. `python3 scripts/geom_invariance_check.py` was run against the
untouched tree and reports **[R-4] MTL 0/1 해시 일치 33/33 ✔ PASS** and **[R-6] V1=1 3자 일치 33/33
✔ PASS** — recorded here as the pre-CB-9 baseline. `scripts/placement_lint.py` (T1) does not exist
yet; nothing in this WP is gated on it.

---

## 2. S06-A — the four defects, re-graded

### A-1 · fascia sawtooth — **CONFIRMED, and worse as built**

The design line is exactly what survey B says. Within step *i*, `_fascia_z(a) − tread_i` runs from
**+153.600 mm** at the step start to **−38.400 mm** at the step end, amplitude **192.000 mm =
one riser**, repeating 26 times `[computed]`. `_fascia_z`'s own docstring states the same values;
they reproduce.

What the render actually shows is **larger**: measured over the ring interior, the lip runs
**+165.85 mm / −26.20 mm**, amplitude **192.05 mm** `[measured-usd]`. The whole profile is displaced
**+16.34 mm** (range 16.26 – 16.43 over 59 001 samples) because of NF-1 below. The two ±4.1 mm
end-clips against the ideal ±16.34 shift are the tread boxes' own 0.245° tangential overshoot
holding the previous, 192 mm-higher step one sample longer — i.e. the two defects interact.

Consequence for the build spec: **item 3's "top z = that tread's z + a fixed 20–30 mm nib" cannot be
authored through `build_helix_ramp` as it stands** — the builder would silently add 16 mm to a 25 mm
nib. Rebuilding the fascia as one *stepped* (horizontal-topped) segment per tread makes the tilt
zero and the artefact disappears with it; that is another reason to prefer the stepped form over
patching `z_off`.

### A-2 · constant-chord segment boxes — **every figure CONFIRMED except the headline**

The whole A-2 table reproduces to 3 significant figures (verdict rows 2, 3, 5–8) with the single
exception of the **99.0 mm** headline, which is refuted (row 1), and the fascia corner radius, which
was under-measured (row 4).

The number that matters most for the repair is not in the table at all. The 7.08× inner overwidth is
not a rim cosmetic — it is a **stacking factor**:

| quantity | measured |
|---|---|
| landing footprint covered by ≥ 1 segment | **17.322 m²** |
| ideal annular sector `π/2·(3.30² − 0.48²)` | **16.744 m²** |
| covered by **≥ 2** coplanar segments (all at `z_top = 4.998`) | **8.551 m² = 49.4 %** |
| max stacking depth | **7** |
| overlapping segment pairs | **123** (23 of them adjacent) |
| radius below which every box overlaps its neighbour | **3.392 m** — i.e. the entire landing |

The measured max depth of **7** is the 7.081× overwidth ratio read back as an integer: at `r_in` each
box spans 7.08 neighbour pitches, so 7 slabs share the same plane there. That is the mechanism behind
"surface acne and shard slivers", and it is invariant under `seg` (§4).

### A-3 · landing ↔ deck interpenetration — **CONFIRMED**

Landing top **4.998**, base **4.498**; deck top **5.000**, soffit **4.650**. The landing body runs
**348.0 mm** up through the deck; the landing top face sits **2.0 mm** below the deck top. Footprint
overlap bbox **x 2.000…5.000 × y −13.000…−9.6925 = 9.922 m²**, true intersection area **9.192 m²**.
All `[measured-usd]`.

### A-4 · railing posts outboard — **CONFIRMED**

Post centres measured at radius **3.360000**; +60.0 mm outboard of the tread nosing (3.30) and
+30.0 mm outboard of the fascia face (3.33); post outer face at **3.390**. Item 5's proposed 3.24
puts the post outer face at 3.270, inboard of the nosing ✔ — but note the post then sits **inside the
fascia radial band (3.22–3.33)**, so `spiral_selfcheck` should assert post-vs-fascia clearance as
well as `post centre ≤ r_out − 0.05`, or the 3.24 posts will interpenetrate the new stepped fascia
over the nib height.

---

## 3. New defects found during re-verification — not in S06-A

### NF-1 · `build_helix_ramp` displaces the top face it is asked to place `[measured-usd]`

`_oriented_box` composes `translate → rotZ → rotX → scale` and `build_helix_ramp` sets
`cz = z_top − thick/2`, i.e. it places the **box centre** and then tilts about that centre. For a
slab of thickness `t` tilted by `θ`, the top face plane in the segment frame is
`z'(y') = y'·tan θ + (t/2)/cos θ`, so the surface is:

- **shifted tangentially** by `(t/2)·sin θ`, and
- **raised** by `(t/2)·(1/cos θ − 1)` at the placement azimuth.

Measured on the shipped rings:

| ring | thick | tilt | tangential shift | z lift (predicted) | z lift (measured) |
|---|---|---|---|---|---|
| `SpiralFascia` | 0.78 | **−16.232°** | **109.0 mm** | +16.19 mm | **+16.34 mm** |
| `SpiralSoffit` | 0.34 | **−21.749°** | **63.0 mm** | +13.03 mm | **+13.03 mm** |
| `RailOuterTop` (pipe) | 0.064 | −15.844° | 8.7 mm | +1.26 mm | — |
| `RailInnerTop` (pipe) | 0.064 | **−33.513°** | 17.7 mm | +6.38 mm | — |

> **AMENDMENT `[supervisor 07-31 · micro-docs batch · source `w3_k4_v1.md` §5.3 / finding K4-F3]`.**
> ~~compensate `cz` by `(t/2)(1/cos θ − 1)` **and** the tangential origin by `(t/2)·sin θ`~~ —
> **the two terms above are correct as a *diagnosis* and wrong as a *prescription*: applied
> together they double-count.** The tangential move slides the sloped plane, which changes its
> height at the placement azimuth by `−tan θ · ds`, so the compensation over-shoots. Measured on
> the fascia ring (`t` 0.78, tilt −14.05°) by K4(d): raw defect **+12.03 mm**, and this report's
> pair over-corrects it to **−23.7 mm** — a bigger error than the one being fixed, and of the
> opposite sign. Solving both conditions simultaneously,
>
> ```
> z(u) = cz + (t/2)/cosθ + (u − s)·tanθ ,   s = (t/2)·sinθ ,   z(0) = z_top
>   =>  cz = z_top − (t/2)/cosθ + s·tanθ = z_top − (t/2)·cosθ
> ```
>
> so the z term is **`+(t/2)(1 − cos θ)`**, *not* `−(t/2)(1/cos θ − 1)`. Verified by K4(d): lift
> **+12.028 mm → 0.000** and tangential offset **+94.68 mm → 0.000**. The tangential term
> `(t/2)·sin θ` is unchanged; only the z term is re-derived. **Everything else in NF-1 stands** —
> the defect is real, the measured column below reproduces, and the fix still belongs to K4(d),
> where it landed at `5ceb76a` (default OFF, GT-6 split proof empty: 31,017 rows, 0 differ).
> Cross-noted in `Docs/audit_v4/gt_changes_w3.md` §3 GT-6 (`§10 MD-5`).

The fascia's 109 mm tangential shift is **0.95 of one segment pitch** (114.3 mm), so the ring's top
surface is still continuous — the top face of segment *j* covers the azimuth of segment *j+1*, and
the span (114.95 mm) just exceeds the pitch (114.31 mm) by 0.64 mm. The ring is therefore *lucky*,
not correct: any change to `thick`, `seg_per_deg` or the helix slope moves the shift off the pitch
and opens real gaps in the top surface. **This is a `scene_common` defect, so it belongs to K4(d),
not to S4.** Fixing it is one line — place the top-face centre, i.e. compensate `cz` by
`(t/2)(1/cos θ − 1)` and the tangential origin by `(t/2)·sin θ` — and it is *required* before item 3's
20–30 mm nib means anything.

### NF-2 · the landing's straight edge is a 190 mm sawtooth `[measured-usd]`

`build_arc_steps` gives every box the same tangential width, so at `r_in` the first and last boxes
protrude **190.9 mm** perpendicular past the a0 / a1 rays. On the landing that is the y = −13.000
diameter — the line where the landing meets step 0 and the deck. Measured union extent
**y_min = −13.1904**, i.e. **190.4 mm of solid behind the nominal straight edge**, in 24 teeth.
The same 190.9 mm applies at both ends of every spiral tread: step 0's box corners span azimuth
**172.94°…198.60°** against a nominal 180°…191.54°.

This is the missing half of the scene06 comment at `:1237-1239` (verdict row 14): the comment records
the 0.11° outer overshoot as harmless and never mentions that the same box overshoots by 21.10° at
the inner radius. A true annular-sector mesh removes both.

### NF-3 · the fascia ring's leading end is a 388 mm notch `[measured-usd]`

Because of NF-1's 109 mm tangential shift, the first fascia segment's top face begins **51.6 mm ahead
of** its own placement azimuth, and nothing covers the gap. Over **a = 180.0°…181.7°** the topmost
fascia surface is the tilted end face rather than the top face, dipping to **−387.9 mm below the
design line at a = 180.000°**. At r ≈ 3.26 that is a ~99 mm-long, ~0.39 m-deep notch at the head of
the flight — squarely inside the `pt_noon_broken_rail` frame. It disappears with NF-1 or with the
stepped fascia.

---

## 4. Why the box fallback in spec §10.5 cannot be made to work

Spec §10.5 S06-A item 1 offers, as the fallback to the annular-sector mesh, "cap Δθ so the r_in
overwidth ≤ 1.05× — but for the landing that needs `seg ≈ 165`". **That criterion is unreachable at
any `seg`** `[computed]`:

```
box width      = 2·r_out·sin(Δθ/2)·margin
true width@r_in = 2·r_in ·sin(Δθ/2)
ratio           = margin · r_out / r_in          ← sin(Δθ/2) cancels
```

so the landing's ratio is `1.03 × 3.30 / 0.48 = **7.08125** at every Δθ`. Measured at
`seg ∈ {24, 48, 96, 165, 330, 1000}`: **7.08125** in all six cases. Only the absolute overhang moves:

| seg | Δθ | box width | overhang each side at r_in | neighbours covered at r_in |
|---|---|---|---|---|
| 24 (shipped) | 7.500° | 444.61 mm | **190.9 mm** | 7.08 |
| 165 (spec) | 1.091° | 64.72 mm | **27.8 mm** | 7.08 |
| 1000 | 0.180° | 10.68 mm | **4.6 mm** | 7.08 |

The spiral treads behave identically: **2.266×** at 1, 3 or 10 segments per step; the overhang falls
190.9 → 63.7 → 19.1 mm. So the survey's "seg per step ≈ 3" also buys absolute millimetres, not the
ratio.

**The corrected statement, for whoever writes the fix.** A single constant chord cannot serve two
radii: basing it on `r_in` instead leaves a `1 − 1.05·r_in/r_out` = **84.7 %** gap at `r_out`. Holding
≤ 1.05× at *every* radius with boxes requires **radial** subdivision into bands of ratio ≤ 1.05:

| element | r_out/r_in | radial bands needed | boxes after | boxes now |
|---|---|---|---|---|
| Landing | 6.875 | **40** | **960** | 24 |
| Spiral tread (each) | 2.200 | **17** | **17 × 26 = 442** | 26 |
| Fascia | 1.034 | 1 | 150 | 150 |

1 402 boxes to avoid one mesh. Two further facts remove the prim-budget objection that motivated the
fallback in the first place: (i) a true annular-sector solid is **one `UsdGeom.Mesh` prim for the
whole ring**, so the landing goes **24 prims → 1** and the spiral **26 → 26 or fewer**, a prim
*reduction*; (ii) spec §12-14 already rules that triangle count is not the budget. **Option (a), the
mesh, is the only viable route — the fallback clause should be struck rather than kept as an
alternative.**

---

## 5. scene09 — the waterline

`compute_steps()` (`scene09:430-452`) is the single source. Re-run against the shipped `PARAMS`:

```
risers   [0.14, 0.16, 0.18, 0.20, 0.18, 0.16] cycled, 36 steps
treads   0.34, landings 1.20 at step index 11 and 23
z_top     0.000        z_bot    −6.120        base_z  −6.720
idx6 = 36 − 6 = 30 → steps[30] = (xa 11.920, xb 12.260, top −5.240)
water_z  = −5.240 + water_extra 0.050 = **−5.190**
band_hi  = −5.190 + 3 × 0.170 = −4.680
```

`sc.build_water(..., water_z, ...)` authors a slab whose **top face is at `water_z`**; measured on the
stage: top **−5.18999999**, bottom **−5.39000000**, x0 **11.920**. So **the water surface is
z = −5.190**, and **−5.240 is the tread it stands 50 mm above** — the two numbers are one riser apart
in the source and were collapsed in the fact table.

Everything else in that row is right (verdict row 21). The waterline **x ≈ 11.92 is correct for a
different reason than stated**: step 29's top is −5.100 and step 30's is −5.240, so the −5.190 plane
cuts the **riser face** at x = 11.920 — it does not lie on a tread at all, which is exactly what makes
it a clean vertical waterline in a raking cut.

**Downstream**: the S09-A `stair_flank_raking` justification "eye … 3.04 m above [the water]" becomes
**2.99 m**. Bearing 130.815°, pitch −5.502°, range 14.6017 m all reproduce. Nothing in the camera
tuple changes; only the sentence describing it does. `look_check`/gallery captions and the scene
BANNER should say **−5.190**.

---

## 6. C0-7 — the baluster numbers

Built one real `build_railing_line` at the scene03 signature (`rail_h=0.9`, everything else default),
with `NEGOBS_LOOK_GEO=1`, and measured the cylinder prims:

| quantity | source | measured |
|---|---|---|
| pitch `2·baluster_r + baluster_gap` | 0.009, 0.098 | **116.0 mm** |
| baluster diameter | 0.018 | **18.0 mm** |
| **clear opening (안목)** | claimed ≤ 100 mm | **98.0 mm**, identical on every bay |
| statutory limit | 「도로안전시설 설치 및 관리 지침」 guardrail | 100 mm |
| verdict | | **PASS with 2 mm margin** |

So the *specification* inside `build_railing_line` is correct and does not need re-dimensioning. The
C0-7 defect is entirely about **reach**, and its inventory has drifted since W1 (verdict rows 24-26):

1. `LOOK_V1` → the gate is now `LOOK_GEO`, and `LOOK_GEO` is 1 whenever `NEGOBS_LOOK_V1=1`
   (`scene_common.py:190-192`). Every round runner from `run_260730_*` onward, and spec §7.2's
   GATE-1 channel, set it. **Balusters are present in the frames W3 judges.** The v7/v8 finding was
   true when written and is no longer the current state; K4(a)'s work is to move them out of the
   A/B gate, not to make them appear.
2. `scene_common.py:1686` is the builder (the audit cites `:1320` — pure line drift).
3. **16 live call sites in 14 scenes**, none overriding `baluster_gap`, **one** (`scene10:1195`)
   disabling balusters with `baluster_r=0.0`.
4. **Two local railing implementations remain outside the builder**: scene01's (`scene01:1057ff`) and
   scene02's pit-perimeter `hrail()` (`scene02:819-849`, top rail + mid rail + posts, no infill,
   `top_z = 0.15 + 0.90 = 1.05 m` — below the 1.10 m guideline, confirmed). scene02's *stair* rail is
   no longer one of them: it was replaced by a statutory handrail and no longer calls the shared
   builder at all.

---

## 7. What CB-9, K4(d) and the ledger must do with this

**CB-9 is released.** Every S06-A number it depends on is graded above.

1. **Never quote 99.0 mm again.** The landing rim swing is **7.46 mm**. Anywhere the 99.0 mm figure
   justified a repair, the justification is the **7.08× / 49.4 % / depth-7 coplanar stacking**
   (§2 A-2) — a bigger defect than the one that was quoted, so no repair item is weakened.
2. **Drop the box fallback from §10.5 item 1.** It is unreachable as written (§4). Author the
   annular-sector mesh.
3. **Fix `build_helix_ramp`'s top-face placement in the same K4(d) commit** (NF-1). Without it,
   item 3's 20–30 mm nib is authored 16 mm high, the soffit ring stays 13 mm off its own line, and
   the inner rail pipe stays 6.4 mm off the tread line. It is a shared-module defect, so S4 cannot
   fix it from `scene06`.
   **AMENDMENT `[supervisor 07-31 · micro-docs batch · `w3_k4_v1.md` §5.3 / K4-F3]`** — the
   instruction stands, **the formula in §3 does not**: ~~compensate `cz` by `(t/2)(1/cos θ − 1)`
   and the tangential origin by `(t/2)·sin θ`~~ over-corrects a **+12.03 mm** defect to
   **−23.7 mm** when both terms are applied. The correct z term is **`+(t/2)(1 − cos θ)`** (the
   tangential term is unchanged); verified lift +12.028 mm → 0.000, tangential +94.68 mm → 0.000.
   **Landed at `5ceb76a`, default OFF**, with GT-6's split proof empty (31,017 rows / 0 differ).
   Full derivation at §3 NF-1 above; cross-noted in `gt_changes_w3.md` §3 GT-6 (`§10 MD-5`).
4. **`spiral_selfcheck` should gain two assertions** beyond the four in §10.5 item 6: (a) no segment
   footprint extends past the ring's a0/a1 rays by more than 5 mm at **any** radius (kills NF-2);
   (b) the fascia top surface is continuous — no azimuth in `[a0, a1]` where the top face of the
   union drops more than the nib below the design line (kills NF-3).
5. **GT-6 needs two edits** — the ledger belongs to T5, this is the input it needs:
   - **scene13 is not affected.** It has no arc/helix call site (verdict row 18). "05 · 19 · 13 share
     the builder" → **05 · 19**. Archive judge baselines for **05 · 06 · 19** only; scene13's re-render
     obligation comes from GT-5 (the curb step), not from GT-6.
   - **scene05 has 12 call sites, not 10** (verdict row 19) — the blast radius of K4(d) is 20 % larger
     than booked.
   - GT-6 lists "landing top 4.998 → **5.000**" among its changes while asserting "top-face z
     unchanged". Those are inconsistent: that is a **+2 mm move of a walked top face**. It is far
     below any drop threshold, but the prim-hash / GT-delta diff GT-6 demands **will not come back
     empty** if the landing top moves, and §8 says "a non-empty diff is a defect, not a new baseline".
     Either exclude the landing top face from the invariance claim explicitly, or keep `top_z` at
     4.998 and remove the interpenetration by clipping the azimuth alone.
6. **scene09's waterline is −5.190.** S5 owns the scene; the correction is documentation-only (no
   geometry moves), but the S09-A cut rationale and the BANNER should carry the right number, and the
   "3.04 m above water" phrase becomes **2.99 m**.

---

## 8. Reproduction

```bash
python3 -m venv /tmp/usdvenv && /tmp/usdvenv/bin/pip install usd-core numpy   # usd-core 26.8

# the three measurement passes (they compose real USD stages from the shipped builders)
NEGOBS_LOOK_GEO=1 /tmp/usdvenv/bin/python t3_geom_reverify.py    # verdict rows 1-16, 20-23
NEGOBS_LOOK_GEO=1 /tmp/usdvenv/bin/python t3_geom_reverify2.py   # A-1 profile, NF-1/NF-3, coverage map
NEGOBS_LOOK_GEO=1 /tmp/usdvenv/bin/python t3_geom_reverify3.py   # NF-2, seg sweep, corner radii

# call-site censuses (AST, not grep-by-eye)
python3 - <<'PY'   # build_railing_line sites + baluster kwargs
import ast, glob
for f in sorted(glob.glob('scenes/main/*.py') + glob.glob('scenes/batch1/*.py')):
    t = ast.parse(open(f, encoding='utf-8').read())
    for n in ast.walk(t):
        if isinstance(n, ast.Call) and ast.unparse(n.func).endswith('build_railing_line'):
            kw = {k.arg: ast.unparse(k.value) for k in n.keywords}
            print(f, n.lineno, kw.get('baluster_r', 'default'), kw.get('baluster_gap', 'default'))
PY
grep -rn "build_arc_steps(\|build_helix_steps(\|build_helix_ramp(" scenes/main scenes/batch1

# CPU pre-flight recorded in §1
python3 scripts/geom_invariance_check.py        # [R-4] 33/33 PASS · [R-6] 33/33 PASS
```

The three scripts live in this session's scratchpad
(`/tmp/claude-1000/-home-vislab-Desktop-work-sy/5ee36dfd-2b10-441f-abd8-7cf6372faec2/scratchpad/`).
They are throwaway measurement harnesses, not repo tooling: T3 owns no `scripts/` path under spec
§4.1, and the durable artefact is this report. Anything that needs to become a permanent gate belongs
in **T1's `scripts/placement_lint.py`** or in **`spiral_selfcheck` (S4)**, per §7 items 4 and 5.
