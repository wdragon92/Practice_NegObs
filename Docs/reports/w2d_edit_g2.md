# W2-D G2 — ground_kit applied to scene07 · 08 · 09 · 10 · 11 · 12

Author: W2-D group 2 (MAIN tree, branch `feat/realism-v1`) · Date 2026-07-30
Scope: scene edits only, **no renders, no GPU, no Isaac, no SMOKE, no commit.**
Evidence tags: `[measured]` = read out of code executed this session · `[calc]` = derived from
the verified frame model (`f = 1662.769 px`, pitch −10°, 1920×1080) · `[ruling]` = a standing
decision · `[spec]` = `Docs/briefs/ground_kit_spec_v1.md`.

---

## 0. Verdict

All six scenes are wired, all six run end-to-end through `main()` under the CPU harness, and
every hard gate holds. `python3 ground_kit.py` exits **0** and `scripts/geom_invariance_check.py`
returns **33/33 PASS** on both R-4 and R-6. The kit's own dry self-check still evaluates the
`SCENE_PLANS` fixtures, which are nominal; the numbers that matter — the ones produced by the
scenes' real `PARAMS` — are in §3 and were obtained by calling each scene's new `ground_plan()`
directly.

The round also found **six defects in `ground_kit.py`** that no CPU gate reports, one of which
would have silently nulled the single largest prim spend in the group (scene12's 120 plank
gaps). `ground_kit.py` is not mine to edit, so two of them are worked around inside the scene
files in a way the standing ruling already prescribes, and all six are written up in §5 for the
kit owner. **None of them blocks the GPU round.**

---

## 1. What was wired

| scene | profile | plan(s) | region (scene coords) | z | drop edge | geom prims | scatter |
|---|---|---|---|---:|---|---:|---:|
| 07 temple | P12 `courtyard_dg` | `ground_plan` | x −12.0…−0.80, y ±1.50 | 0.000 | courtyard shoulder x = 0 | 11 | 340 |
| 08 sunken plaza | P3 `sidewalk_block` | `ground_plan` + `ground_plan_pit` | x −12.0…−0.95, y ±4.0 · court x 2…10, y ±3 | 0.000 / −4.498 | pit near edge x = 0 | 51 + 2 | 0 |
| 09 ghat | P2 `plaza_water` | `ground_plan` | x −12.0…−0.80, y ±5.0 | 0.000 | stair head x = 0 | 35 | 0 |
| 10 park deck | P18 `deck_trail_hybrid` | `ground_plan` + `ground_plan_deck` | trail x −12.0…−1.60, y ±0.85 · deck x −1.5…0, y ±1.40 | 0.002 / −0.005 | deck far edge x = 0 | 7 + 10 | 190 + 30 |
| 11 footbridge | P9 `bridge_deck` | `ground_plan` | x −13.2…15.0, y ±1.20 | 5.500 | stair head s = 0 (world x = 15) | 35 | 0 |
| 12 riverside deck | P10 `deck_timber` | `ground_plan` + `ground_plan_deck` | x −18…0, y ±1.25 | 0.000 | deck end x = 0 | 9 + 120 | 0 |

`[measured]` totals: **280 geometry prims + 560 scatter instances** across the six.
Every profile stays inside its own `prim_cap` (`B10` passes on every plan).

**Shape of the integration.** Each scene gained (a) `import ground_kit as gk`, (b) a
`PARAMS["gkit"]` block holding every coordinate, (c) a module-level `ground_plan()` (plus a
second plan where two z levels are needed) that is **pure CPU and touches no USD**, and (d) a
`build_ground_kit(M)` inside `main()` that calls `gk.apply_ground`. Splitting the plan out of
`main()` is the one structural difference from the pilot pattern: it makes the plan callable
without Isaac, which is how every number in §3 was produced.

**P-A (skin exclusion)** is registered before the slab box exists, as the pilots do:
`Plate_Courtyard` (07), `Plaza_W` (08), `Terrace` (09), `Plate_TrailPath` + `EntryDeck` (10),
`Deck` (11, 12). For 07/08/09 this is load-bearing — those slabs are ≥ 4 m on both axes with a
paving/stone/gravel material, so `_skin_wanted` would otherwise cover them with a skin whose top
is +6.5…16.5 mm and bury every 0.6–3 mm element `[spec §1.1]`. For 10/11/12 the slabs are
1.7–2.5 m wide and already fail the skin's 4 m test; they are registered anyway so the guarantee
does not depend on a width a later edit could change.

**Natural-scene rule.** 07, 09, 10, 12 run `natural=True` profiles, so `plan_ground` raises on
any `manhole / gully / gutter / marking`. Zero urban infrastructure is present in those four by
construction, not by review. scene12 additionally satisfies the ruling "deck facility — railings
and low lighting allowed, road infrastructure banned": the kit contributes only plank gaps,
staining and a shoreline film band. scene09's park lights are props and untouched here.

---

## 2. Per-scene notes

### 07 — temple forecourt (P12)
Three bands exactly as `[spec §5.7]` asks: the 3.0 m decomposed-granite walking band is the plan
region (y ±1.50) and `edge_break` draws both of its boundary lines; `wear_lane` width 1.20 is the
trodden axis; scatter is 270 gravel over 33.6 m² = **8.04 /m²** against the spec's 8 /m² `[calc]`.
Stains carry two kinds so the "plinth moss band" of §5.7 has a material distinct from tracked soil.

Region x1 is **−0.80**, not the plate edge x = 0. `apply_ground` runs the profile scatter over the
**untrimmed** region, so the region itself is the only lever that keeps ≤ 0.06 m exposed gravel off
the shoulder; `_trim_region` puts the surface elements at the same −0.80 anyway.

### 08 — sunken plaza (P3)
One area element per preset near-window, and the manhole deliberately **not** in W1:

| cut | W1 (scene x) | occupant | screen width |
|---|---|---|---:|
| d2 | −1.436…0 | patch #0 at x −1.25 | 79.8 % |
| d5 | −4.436…−3.0 | patch #1 at x −3.60 | 48.5 % |
| d10 | −9.436…−8.0 | patch #2 at x −8.60 | 53.0 % |
| — | — | manhole x −2.40 → d5 **W2** (X = 2.60) | 21.6 % `[calc]` |

The manhole placement is the scene15 M9-ⓑ result applied directly: a φ0.648 cover anywhere inside
W1 is ≥ 28.1 % of frame width at any distance, so W2 is the only placement that satisfies both
"1 manhole" and "≤ 25 %" `[calc]`. Patch dominance is a different matter — cb40ae8 already ruled
that a flat tone patch does not carry the same near-window-monopoly cost as a 3D cover — and
patch #0's footprint at d2 spans X 0.32…1.18, entirely **below** the d2 GRAZE E band (1.4…4.4),
so it cannot masquerade as an edge signal `[calc]`.

The pit opening is passed as a `void`, so B8 asserts that nothing bridges it.

`ground_plan_pit()` is a second, two-prim plan carrying the single gully that `[spec §5.2]` makes
mandatory at the sunken low point `[시방 오목부 필수]`. It could not ride on the plaza plan
because a plan carries one z and the court floor is 4.498 m lower. It is never visible at h0.3 by
the scene's own design; it exists for the court and overview cuts and for the code to be able to
say the mandatory item is present.

`[spec §12.4]` registers scene08's `opening_ring` and directs it to stay on the scene's own
`build_tactile_ring`, so **no `gk` tactile op is emitted**. The non-conforming variant assigned to
this scene ("2–3 tiles missing") is now implemented: the west band is split around a
`gap_tiles × 0.300 m` gap centred on the walk axis. Verified by running the scene with
`cue_tactile = True`: prim count 684 → 689 `[measured]`.

### 09 — ghat terrace (P2)
`step_x` and `step_y` are overridden to **1.80 m**. The P2 table ships `step_x = 19.80`
(`step_expansion_ghat`, the *expansion* period) and `_compose_ops` emits exactly one joint op, so
over an 11.2 m approach corridor the profile default produces **zero** joint lines — the opposite
of §5.7's "make the slab joints geometric". 1.80 m = 3 × the 0.600 granite cell, so §4.5 U2 holds
and the 19.80 m expansion joint remains a multiple of it (11 ×). Result: 5 transverse + 5
longitudinal joints, with the tick at x = −1.8 dropped automatically by `_edge_guard_ticks`
(Δ = 11.16 rows @1080 < 16 at d10) and x = −3.6 kept (Δ = 28.54) `[calc]`.

Slab loss is 5 patches over 112 m² = 4.5 /100 m², inside the spec's 4–6 band.
`silt_band` and `edge_break` are dropped from the profile for this scene — the silt band belongs
on the submerged steps, not the terrace, and the terrace has no material boundary inside the
frame (the lawns start at |y| = 12, outside the 5.77 m half-width at X = 10 m) `[calc]`. Instead
the scene's own waterline banding was widened from **1.5 to 3.0 steps**, which is literally what
§5.7 row 09 asks for and is the one place in this scene where the water mark is the drop anchor.

### 10 — park deck switchback (P18)
Two plans at two z levels, because §13 measured that d2 is entry deck and d5/d10 are dirt trail.
Plan A: `edge_break` on the dirt↔grass line y = ±0.85 (the ΔE76 15.2 boundary), wear lane 0.90,
soil staining, 120 gravel. Plan B: 9 plank gaps + 1 butt on the entry deck. 10-2 (the ΔE76 27.3
leaf-decal outline, the strongest boundary §13.3 found) is done with two direct
`sc.scatter_debris` rings using `edge_bias`, which skips 65 % of the interior so the debris lands
on the outline rather than filling the rectangle: 2 × 15 = 30 instances. Total scatter 220 against
the 250 cap `[calc]`.

The §7.3 invariant for scene10 ("the upper trail is cut at x = −1.5") holds by construction: plan
A stops at `TrailPath` x1 = −1.6 and every element of plan B carries `deck=True`.

### 11 — footbridge deck (P9)
The only scene in the group whose grid origin is not the world origin: `_grid_shift()` puts it at
(15.0, 0, 5.50) with travel +X, and the plan is given that origin with the edge at forward s = 0.

`gully` is overridden to **0**. `infra_kit.build_gully` sinks a 0.640 m body and the deck slab is
0.400 m thick, so a deck gully would pierce the soffit — the exact surface the `under_grating`
preset looks at. A deck scupper has no builder in the kit; it is a rider (§5, R6), not something
to fake with the wrong part.

`[spec §12.4]` registers `stair_top`/`stair_foot` and keeps them on the scene path, so again no
`gk` tactile op. The assigned non-conforming variant ("bearing off by 15°") is implemented with
`sc._oriented_box`, and the band is pulled back by `half_width × sin(15°)` so that even the
leading corner stops at the tread line — a skewed band that overhung the first tread would be a
GT change, not a mis-installation. Verified with `cue_tactile = True`: 2225 → 2229 prims
`[measured]`.

### 12 — riverside deck (P10)
120 plank gaps + 1 butt at the spec's 0.145/0.005 module, staining, and a shoreline film band at
y 0.65…1.25 — the river-side cantilever strip, which is the one deck edge `build_silt_band` can
describe (it runs bands at constant y). Non-slip paint striping is **not** placed: the kit's only
striping builder is `marking`, which `natural=True` blocks, and inventing a substitute would put
a road-infrastructure primitive into a scene the ruling explicitly fences off.

---

## 3. Gate results — CPU only

`python3 ground_kit.py` → **exit 0**, 33/33 hard gates on the fixtures `[measured]`.
Below are the gates evaluated on the **real scene plans** (each scene's `ground_plan()`),
which is the number that describes what will actually render.

| scene / plan | prims | δmax | hard fails | soft warns | d2 area% / cross / long / decal | d5 | d10 |
|---|---:|---:|---|---|---|---|---|
| 07 | 11 | 0.0006 | — | B1 B2 B3 B5 | 0 / 0 / 1 / 1 | 0 / 0 / 1 / 3 | 0 / 0 / 3 / 1 |
| 08 plaza | 51 | 0.1018 ¹ | — | B3 B4 B5 | 79.8 / 0 / 1 / 0 | 48.5 / 0 / 1 / 1 | 53.0 / 0 / 1 / 2 |
| 08 pit | 2 | 0 | — | B1–B5 | — | — | — |
| 09 | 35 | 0.0020 | — | B5 | 100 / 0 / 1 / 0 | 47.7 / 0 / 1 / 0 | 51.4 / 1 / 3 / 0 |
| 10 trail | 7 | 0.0006 | — | B1 B2 B3 B5 | 0 / 0 / 1 / 0 | 0 / 0 / 1 / 0 | 0 / 0 / 3 / 1 |
| 10 deck | 10 | 0.0200 ² | — | B1 B2 B4 B5 | 0 / **4** / 0 / 0 | — | — |
| 11 | 35 | 0.0020 | — | B3 B4 B5 | 0 / 0 / 1 / 0 | 57.7 / 0 / 1 / 0 | 52.1 / 0 / 1 / 2 |
| 12 surface | 9 | 0.0006 | — | B1–B5 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 2 | 0 / 0 / 0 / 2 |
| 12 planks | 120 | 0.0200 ² | — | B1 B2 B4 B5 | 0 / **8** / 0 / 0 | 0 / 8 / 0 / 0 | 0 / 7 / 0 / 0 |

¹ weed height after the GT-E5 ramp clamp — an exception-registered element, excluded from
`apply_ground`'s δ check. ² plank gap nominal recess, `exc="plank_gap"`, exempt by §6.1.

**`scripts/geom_invariance_check.py` — 33/33 PASS on R-4 and R-6** `[measured]`, with the six
scenes also run in isolation and under the `NEGOBS_GKIT=0` diagnostic arm. The ON/OFF prim delta
is the clean attribution the §7.5 A3 amendment asks for:

| scene | prims OFF | prims ON | Δ | plan geom prims |
|---|---:|---:|---:|---:|
| 07 | 530 | 1141 | 611 | 11 (+ scatter) |
| 08 | 631 | 684 | **53** | 53 |
| 09 | 470 | 505 | **35** | 35 |
| 10 | 677 | 1010 | 333 | 17 (+ scatter) |
| 11 | 2190 | 2225 | **35** | 35 |
| 12 | 674 | 803 | **129** | 129 |

The four scatter-free scenes match their plan prim count exactly `[measured]`; 07 and 10 exceed it
because `scatter_debris` records more than one prim per instance.

**Soft-gate reading.** B1/B2 misses in 07, 10, 12 are structural to the natural profiles: P12,
P18 and P10 have no area builder at all, and §8.2 budgets them as scatter- and line-dominated
(≈9, ≈32, ≈130 prims respectively). B3/B4/B5 misses are largely measurement artefacts of
`frame_budget` rather than missing content — see R4, R5, R6 in §5. Per §7.5 A1 the render-side
σ_LF/sd gates stay informative-only for a ground-only round; they are not claimed here because
this round produced no pixels.

---

## 4. Deviations from the §5 matrix, and why

| # | scene | matrix says | what was done | reason |
|---|---|---|---|---|
| V1 | 07, 10 | `edge_litter` (width 0.25) | **dropped** | `_compose_ops` overrides the width with the region span (3.0 m in 07, 1.70 m in 10 = 12× and 7× the ledger value) and then places the two bands so that together they cover ±span, guaranteeing a full-footprint coplanar overlap with `wear_lane` at an identical top z. See R2. |
| V2 | 09 | P2 `step_x` = 19.80 | `step_x = step_y = 1.80` | at 19.80 the near corridor gets **zero** joints, which contradicts §5.7's "make the slab joints geometric". 1.80 = 3 × 0.600 cell, U2 holds. See R5. |
| V3 | 09 | "submerged silt band" via `silt_band` | scene's own stair banding widened 1.5 → 3.0 steps | the terrace plan cannot reach the submerged steps (different z, different surface); §5.7 asks for the 1.5→3 widening in the same row. |
| V4 | 11 | deck scuppers | `gully = 0`, rider filed | gully body 0.640 m vs deck thickness 0.400 m → pierces the soffit, which `under_grating` looks straight at. |
| V5 | 12 | non-slip paint striping | not placed | the only striping builder is `marking`, blocked by `natural=True`; substituting a road primitive would break the scene12 ruling. |
| V6 | 10, 12 | `deck_planks` inside the main plan | separate plan at a lifted z | otherwise the gap strips render **zero pixels**. See R1 — this is the standing "recess-as-tone, never a plate below the pavement" ruling applied. |

---

## 5. Defects found in `ground_kit.py` (riders — not edited, not mine)

**R1 — `build_deck_planks` buries its own output.** The builder puts the gap strip's top at
`z − 0.020`, i.e. below the deck surface, and scene decks are solid boxes (scene12 slab spans
z −0.14…0). At the deck's own z the strips are sealed inside the slab and render nothing. This is
the identical failure mode `cb40ae8` fixed for joints and manholes with `surface_top_z()`, and it
contradicts the standing ruling "recess-as-tone via `surface_top_z`, never plates below
pavement". **Severity: it would have nulled 120 of scene12's 129 prims and 10 of scene10's 17.**
Worked around scene-side by lifting the plan z to `surface_top_z(deck_top) + 0.020`, which puts
the strip top at deck top + 0.6 mm; verified `[measured]` — element top z = 0.0006 in both scenes.
Proper fix is one line in the builder (use `surface_top_z(z)` as joints do); the scene-side lift
should then be removed.

**R2 — `edge_litter` width is not controllable and collides by construction.**
`_compose_ops` does `kw.pop("width", None)` and then passes `width = abs(y1 - y0)` — the region
span — so the ledger value `edge_litter_w = 0.25` can never take effect. Worse, `build_edge_litter`
centres the two bands at `±width/2` with size `(L, width)`, so together they tile `[−width, +width]`
and always contain the `wear_lane` footprint at an identical top z. For any profile carrying both
(P11 `trail_soil`, P12 `courtyard_dg`, P18 `deck_trail_hybrid` → scenes 04, 07, 10) the overlap is
total, not incidental. Dropped in 07 and 10 (V1).

**R3 — every decal builder emits the same top z, so overlaps z-fight.** `build_stain_field`,
`build_wear_lane`, `build_edge_litter`, `build_edge_break`, `build_silt_band` and
`build_footprints` all place their box top at exactly `z + stain_proud (0.6 mm)`. Where two of
them overlap in XY the shared top plane is coincident and the renderer has no ordering. Measured
in scene07's own plan: `Stain_dirt/dirt_1` (y −0.19…0.31) and `Stain_water/water_1` (y 0.01…0.75)
both sit inside the wear lane (y ±0.60) `[measured]`. Suggested fix: stagger by kind, e.g.
`stain_proud + 0.0002 × kind_index`, which stays far inside `GROUND_PROUD_MIN` tolerances.

**R4 — `_edge_guard_ticks` mixes coordinate frames.** It builds ticks from the region in **world**
coordinates and compares them against `ctx["edges"]`, which are **forward-s** coordinates
(`drow(xx - se, d)` and the band test `0.7d ≤ d + xx - se ≤ 2.2d`). For any scene whose grid
origin is not the world origin the comparison is meaningless. Measured on scene11 (origin
x = 15): the expansion joint at world x = 0 — which is 15 m behind the drop edge — is dropped as
if it sat on the edge, leaving 2 joints where the profile intends 3 `[measured]`. Affects
scene06, scene11, scene19. B7 in `frame_budget` uses the correct `view.s_span`, so this is a
false *drop*, never a false pass; nothing unsafe ships, but content is lost.

**R5 — `frame_budget` judges long strips at the wrong distance.** For an element it takes
`Xm = (Xa + Xb)/2` over the element's whole s-span and clamps to 0.05 m. A 28 m longitudinal band
therefore has its half-width evaluated at 0.05 m (half-width 0.029 m), and any strip offset
laterally by more than that is scored "out of frame". Consequence: scene11's rail-foot rundown
bands at |y| = 1.0 and scene12's shoreline film band score **0** on B4, although at X = 5 m the
frame half-width is 2.89 m and both are comfortably inside it `[calc]`. B4 ≥ 2 is effectively
unreachable for any long corridor. Suggested fix: evaluate long strips at the near end of their
visible span, not the midpoint.

**R6 — two profile-table values are unreachable through `_compose_ops`.** (a) Stain counts are
hardcoded (`n = 2 if grime_band else 4`) and ignore the profile tuple, so B5 (≥ 6 decals within
X ≤ 3 m) cannot be satisfied from the table — at d2 the qualifying band is only ~1 m deep, so
even 8 stains rarely put 6 in it. (b) P2's `step_x` doubles as both the expansion period and the
slab-joint period because only one joint op is emitted (V2/R5 in §4). Also worth noting: B4's
"≥ 2 px at X = 5 m" test rejects interlock joints (3.5 mm → 1.16 px) and plank butt joints
(5 mm → 1.66 px), so those two element classes can never score on it `[calc]`.

**R7 — no deck-scupper builder** (see V4). Minor, but it is the one item of §5.3's scene11 row
that cannot be executed.

---

## 6. Tactile status for the six (§12.4)

| scene | §12.4 verdict | this round |
|---|---|---|
| 07 | OFF — natural scene | no site, `tactile=()` |
| 08 | **ON, `opening_ring`**, defect "2–3 tiles missing" | kept on `build_tactile_ring`; gap implemented |
| 09 | OFF — p = 0.24 + natural | `tactile=()` |
| 10 | OFF — park, p = 0.24 | `tactile=()` |
| 11 | **ON, `stair_top`/`stair_foot`**, defect "bearing off 15°" | kept on the scene path; skew implemented |
| 12 | OFF — natural / deck | `tactile=()` |

`SCENE_CONFIG["cue_tactile"]` defaults are **left as they are** (False for 08 and 11), matching
what the scene13 pilot did — the ON/OFF split is a render-mix variable, not a scene default, and
M10 is still open. The dot Ø 25 mm generator constant is already in force upstream; nothing in
this group re-specifies it.

---

## 7. What this round does not claim

- **No pixels.** No render, no σ_LF/sd, no GRAZE, no OCCL. Per §7.5 A1 those gates are
  informative-only for a ground-only round anyway, and per §7.5 A3 edge integrity must be
  established by a same-session `NEGOBS_GKIT=0` A/B, which is a GPU job. The OFF arm is verified
  to assemble (§3) so that A/B is ready to run.
- **R3 (coplanar decals) is not proven visible.** It is proven *geometric* — coincident top
  planes — and two instances are located. Whether it reads as shimmer at h0.3 is a render
  question; it should be looked for in the GPU round's d2/d5 crops for scene07 and scene10.
- **scene08's court gully is never in an h0.3 preset.** That is the scene's own design (the pit
  is hidden by construction); the gully is there because §5.2 makes it mandatory, and it will
  only be seen in court/overview cuts.
- **Patch dominance at d2** (79.8 % in 08, 100 % in 09) is intentional and precedented, but it is
  the kind of thing a viewer notices. Both are outside the d2 GRAZE E band `[calc]`, so it is an
  aesthetic call for the 통람, not a gate risk.

---

## 8. Reproduce

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs
unset PYTHONPATH VIRTUAL_ENV
source ~/miniconda3/etc/profile.d/conda.sh && conda activate env_isaaclab
export PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1

python3 ground_kit.py                                  # exit 0, 33/33 hard gates
python3 scripts/geom_invariance_check.py               # R-5 -> R-4 -> R-6, 33/33
NEGOBS_GKIT=0 python3 scripts/geom_invariance_check.py \
        --scenes scene07,scene08,scene09,scene10,scene11,scene12   # OFF arm

# real-plan gates (this is what the tables in Sec.3 are)
cd scenes/main && python3 - <<'PY'
import importlib
for name, fns in (("scene07_temple_stone_path", ["ground_plan"]),
                  ("scene08_sunken_plaza", ["ground_plan", "ground_plan_pit"]),
                  ("scene09_ghat_riverfront", ["ground_plan"]),
                  ("scene10_park_deck_switchback", ["ground_plan", "ground_plan_deck"]),
                  ("scene11_footbridge_stairs", ["ground_plan"]),
                  ("scene12_riverside_deck", ["ground_plan", "ground_plan_deck"])):
    M = importlib.import_module(name)
    for fn in fns:
        p = getattr(M, fn)()
        print(name, fn, p["prims"], p["instances"],
              p["budget"]["warn"], p["budget"]["fail"])
PY
```

Files touched (scene files only, no kit, no commit):
`scenes/main/scene07_temple_stone_path.py` · `scene08_sunken_plaza.py` ·
`scene09_ghat_riverfront.py` · `scene10_park_deck_switchback.py` ·
`scene11_footbridge_stairs.py` · `scene12_riverside_deck.py` — plus this report.
