# W2-D · g3 — `ground_kit` applied to scene 14 · 16 · 17 · 18 · 19 · 20 · 21

**Date** 2026-07-30 · **Branch** `feat/realism-v1` (post-merge, uncommitted) ·
**Spec** `Docs/briefs/ground_kit_spec_v1.md` v1.1 + §7.5 amendments ·
**Pattern** pilots `e196c93` (N5) · `cb40ae8` (15) · `753b791` (13)

**Scope.** Seven scene files wired to `plan_ground` / `apply_ground`, per-scene elements
placed from the §5 matrix rows, `SKIN_EXCLUDE` registered on every stage the kit decorates,
tactile per the §12.4 final register. No renders, no GPU, no SMOKE, no commit.
Files touched — and **only** these:

```
scenes/main/scene14_grandstair_illusion.py
scenes/main/scene16_canopy_shadow.py
scenes/main/scene17_ramp_pair_hangang.py
scenes/main/scene18_wavy_artstair.py
scenes/main/scene19_fan_winder.py
scenes/main/scene20_diagonal_oblique.py
scenes/main/scene21_monumental_selfocclude.py
Docs/reports/w2d_edit_g3.md                     (this file)
```

---

## 1. Result table `[실측 — runtime, stub harness]`

Prim counts are what `apply_ground` actually created in the scene (they equal the planned
count in all seven, checked by the round-trip assertion inside `apply_ground`).

| scene | profile | region (x0,y0,x1,y1) | edge `s` | z | prims | δmax | unit_cell → T1 | tactile |
|---|---|---|---|---|---|---|---|---|
| 14 | P1 `plaza_granite` | −12.0, −4.0, −0.5, 4.0 | 0.0 | 0.000 | **50** | 0.1185 | 0.600 @ (0,0) | OFF (illusion) |
| 16 | P3 `sidewalk_block` | −12.0, −2.5, 0.0, 2.5 | 0.0 | 0.000 | **52** | 0.1081 | 0.300 @ (0,0) | **ON — entrance** |
| 17 | P13 `levee_paved` | −7.5, −6.0, 0.0, 6.0 | 0.0 | **0.006** | **54** | 0.1198 | 0.200 @ (0,0) | OFF (p 0.24) |
| 18 | P1 `plaza_granite` | −12.0, −5.0, −0.5, 5.0 | **−0.245** | 0.000 | **51** | 0.1109 | 0.600 @ (0,0) | OFF (non-practice) |
| 19 | P6 `roof_membrane` | 4.25, −8.75, 16.75, 3.75 | **+7.6** (axis −x, origin x 11.6) | 0.000 | **41** | 0.0020 | None (no grid) | OFF (private roof) |
| 20 | P1 `plaza_granite` | −13.0, −3.0, **−2.0**, 3.0 | 0.0 | 0.000 | **49** | 0.1051 | 0.600 @ (0,0) | OFF (illusion) |
| 21 | P1 `plaza_granite` | −12.0, −4.0, −0.5, 4.0 | 0.0 | 0.000 | **47** | 0.1177 | 0.600 @ (0,0) | OFF (illusion) |

δmax is the weed-band height after the GT-E5 ramp clamp; every non-vegetation element is
inside `GT_DELTA` 0.020. **No `gt_changes` entry was produced by any of the seven** — this
batch creates **zero unlabelled drops**.

### Gate status (`frame_budget`, evaluated inside `plan_ground`)

| scene | B6 E1′ | B7 E2 | B8 V | B9 albedo | B10 budget | B11 tactile | B12 invariant | soft warns |
|---|---|---|---|---|---|---|---|---|
| 14 | OK | OK | OK | OK | 50/60 | OK | OK | B4, B5 |
| 16 | OK | OK | OK | OK | 52/60 | OK | OK | B4, B5 |
| 17 | OK | OK | OK | OK | 54/60 | OK | OK | B4, B5 |
| 18 | OK | OK | OK | OK | 51/60 | OK | OK | B4, B5 |
| 19 | OK | OK | OK | OK | 41/60 | OK | OK | B3, B5 |
| 20 | OK | OK | OK | OK | 49/60 | OK | OK | B4, B5 |
| 21 | OK | OK | OK | OK | 47/60 | OK | OK | B5 |

**All hard gates (B6–B12) pass on all seven.** B1/B2 (near-window area element, screen
width ≥ 20 %) now pass on all seven as well — see §3.

### Per-cut near-window fill `[계산 — frame_budget]`

| scene | d2 W1 area / % | d5 W1 area / % | d10 (or d3.5/d5) W1 area / % |
|---|---|---|---|
| 14 | 1 / 69.8 | 1 / 38.7 | 0 / 0 |
| 16 | 1 / 65.5 | 1 / 51.0 | 1 / 45.4 |
| 17 | 1 / 66.8 | 2 / 200.0 | 0 / 0 |
| 18 | 1 / 100.0 | 1 / 48.4 | 1 / 53.6 |
| 19 | 1 / 55.3 | 1 / 69.1 (d3.5) | 1 / 29.2 (d5) |
| 20 | 0 / 0 | 1 / 45.0 | 1 / 38.7 |
| 21 | 1 / 94.4 | 1 / 46.7 | 0 / 0 |

---

## 2. Corrections this round made to the spec's own numbers

### 2.1 scene14 trench centre **−2.55 → −2.59** `[계산]`

C-1′ derives the stair-head trench centre from a **0.30 m wide** trench: near lip −2.40,
`drow(−2.40, 10) = 16.05 rows @1080 ≥ 16` — a 0.05-row margin. But `build_trench_drain`
frames the cover: the frame is `width + 2·trench_frame_w` = 0.30 + 2·0.040 = **0.38**, so a
trench centred on −2.55 actually has its near lip at **−2.36**, and

```
drow(−2.36, 10) = 15.70  <  16  →  B7 FAIL
```

Centre **−2.59** puts the frame lip back on −2.40 exactly (16.05 rows). This is the same
class of correction scene13 already applied to its entry trench (0.35 → 0.52, same cause:
the judged object is the boundary line, not the nominal footprint — §5.0 C-1′ note).
Recorded because §5.1 rows for **01 and 02 carry the same −2.55 figure** and are outside
this mission's file set.

### 2.2 scene18 edge `s` = **−0.245**, not 0

scene18's drop edge is the wavy stair head `_front_x(−1, y) = amp·sin(k·y − φ)`, a band
spanning ±0.245 m in x. GT-E1′/GT-E2 have to be measured from its **nearest** point or the
0.80 m standoff is optimistic by a full amplitude. `edge_s = −stair.amp` is read from
PARAMS, so it tracks any future amplitude change (§7.4).

### 2.3 scene19 `origin` is the **grid origin**, not the drop edge

`frame_budget` computes each element's ground distance as `X = d + s`, i.e. it assumes the
eye sits at `s = −d`. So `plan_ground(origin=...)` must be the **preset grid origin**, and
the drop edge goes into `edges` at whatever `s` it really has. scene19 mirrors
`grid_views` about `xref = 5.8`, so the grid origin is world **x = 11.6** with progression
**−X**, and the roof deck's west lip (`upper.x0` = 4.0) is at `s = 11.6 − 4.0 = 7.6`.
`dists` is (2, 3.5, 5) to match `build_views` — d10 is off-roof by design.

> The `SCENE_PLANS["scene19"]` fixture in `ground_kit.py` uses `origin=(9.04, 0, 0)` with
> `edges=_E0` (edge at the origin). Those are check fixtures and they pass their own gates,
> but they place the edge 2.56 m from where the roof lip actually is and put the region
> partly outside the deck (`x1 = 21.0` vs deck `x1 = 17.0`). Not changed here — `ground_kit.py`
> is outside this mission's file set. **Rider R1** below.

---

## 3. Deviations from the §5 matrix, and why

| # | scene | matrix says | what was done | reason |
|---|---|---|---|---|
| D-1 | 17 | ⑥ "L형 측구 + 빗물받이 22 m" | `gutter_L = 0`; a **linear trench drain at x = −4.15** (bike/green boundary) plus 2 gullies on that line | `build_gutter_L` is a carriageway-edge detail and `_compose_ops` always lays it at **y = const spanning x0..x1**, i.e. *across* the crown. On this scene the road runs along **Y**, so the kit's gutter would be perpendicular to the road it drains. The trench carries the same function with the correct orientation and is still a **planned, gated** element. GT-E2: the trench is at X = 0.85 (d5) and X = 5.85 (d10), both **outside** the E band [0.7d, 2.2d] `[계산]` |
| D-2 | 17 | ⑤ "블록 침하 ±3 mm (2×2 단위)" | not placed | it is a per-cell perturbation of the paving unit, which §4.4 assigns to **T1** (MDL unit jitter). The kit's obligation is the ledger, and `unit_cell = 0.200 @ (0,0)` is handed over |
| D-3 | 18 | "모래 밀림 띠 = 해안측 포장 가장자리" | two bands on the walkway's **lee lateral margin** (y ≈ −4.4 / −3.9) | `build_silt_band` emits X-long strips at y = const, so it cannot draw a band along an x = const seaward edge; and on this scene the seaward edge of the upper walkway **is** the hazard edge, inside the 0.80 m exclusion. Wind-driven sand piling against the lateral kerb is the same phenomenon in the geometry the builder can express |
| D-4 | 16 | "캐노피 낙수 얼룩 띠 (처마 투영선)" | carried as `stain` kind **"drip" decals** inside the trimmed region, not as a continuous line at the eaves | the west eaves projection is `canopy.x0 = −1.0`, only 1.0 m in front of the drop: `drow(−1.0, d10) = 5.65 @1080` against a 16-row floor → a transverse band there is a GT-E2 violation `[계산]` |
| D-5 | 20 | "밴드 x −13…−0.5, 7본" | 7 bands emitted, but each band's **+y end is clamped to the mesa boundary** `y ≤ 1.7321·\|x\|` | the mesa is (axis-aligned plaza ∪ 30° wedge) and the wedge's east boundary is the world line `x = −0.5774·y`. A full-width ±8 band at x = −3 would float in mid-air for y > 5.196. Clamping keeps the prescription and, because the bands now terminate on the diagonal, strengthens rather than weakens the scene's "axis-aligned props vs 30° edge" theme |
| D-6 | 20 | region reaching the edge | region `x1 = **−2.0**` | same diagonal. A rectangle is wholly on the mesa only if `x1 ≤ −0.5774·\|y\|max`; with y = ±3.0 that is `x1 ≤ −1.73`, and −2.0 keeps 0.27 m of corner margin `[계산]`. **Consequence: the kit cannot fill the d2 near window (x −1.44…0) in scene20 at all** — that window lies beyond the diagonal across most of the frame width. This is geometry, not an omission |
| D-7 | 18 | "alley pole" allowed here | not placed | the pole body is props-team scope, there is no pole in `PARAMS`, and §7.4 forbids hard-coding a document coordinate. A `PARAMS`-driven base grime/weed band is a two-line addition once props land it |
| D-8 | 16 | P3 profile default `gutter_L = 1` | `gutter_L = 0` | an L gutter is a carriageway-edge detail; this walk has grass on both sides and no roadway (§4.2 call convention) |

---

## 4. Tactile — §12.4 register as executed

| scene | §12.4 verdict | executed |
|---|---|---|
| 16 | **ON 신설 ★** — building main entrance, 0.6 m × full width, defect type "obstruction" | `tactile=("entrance",)`, band `x −6.00…−5.40`, `y ±2.5`, **unconditional** |
| 14 · 20 · 21 | OFF — identity conflict (hidden illusion) | `tactile=()`; gate **B12 `_inv_hidden_illusion`** refuses a tactile element or any bright (albedo > 0.28) full-width transverse line for these three, so it cannot be reintroduced by accident |
| 17 | OFF — `p = 0.24` (riverside park) | `tactile=()` |
| 18 | OFF — wave-form, 300 mm grid not practice | `tactile=()` |
| 19 | OFF — private rooftop, not a covered facility | `tactile=()` |

**Why scene16's band is unconditional and not under `cue_tactile`.** The two pilots differ:
scene13 gated its kit tactile on the toggle, sceneN5 did not. The deciding property is what
the site is *for*. §12.4 marks 16 as the cue+/label− quadrant filler (§12.6): a band placed
deliberately **away from any drop**. It cannot leak a hazard cue into a cue-OFF cut, so
toggle integrity is not at stake, and gating it would empty the quadrant in every default
render. scene16's own stair-head and bollard tactile paths remain toggle-bound, unchanged.
No `EXPECTED_FP` entry is needed: the trigger is "주출입구", which is not in `_FP_TRIGGERS`,
and the band sits 5.4 m clear of the edge.

---

## 5. `SKIN_EXCLUDE` (P-A) registrations

Every registration is placed **before** the corresponding `add_box`, because `add_box`
evaluates `_skin_wanted` inline — a later call is too late (the N5 pilot's finding).
Both arms of every hazard twin are covered, so the `NEGOBS_GKIT=0` A/B measures only the
kit prims (§7.5 A3).

| scene | paths |
|---|---|
| 14 | `UpperPlazaW`, `UpperPlazaS`, `UpperPlazaN`, `UpperPlaza` |
| 16 | `Walk_W`, `FlatWalk` (twin) |
| 17 | `WalkBand`, `BikeBand` |
| 18 | every `Walk_upper*` slab (prefix-registered inside `_slab`, so the 40 wave segments are covered without enumerating them) |
| 19 | `Walk_upper`, `Walk_lower` |
| 20 | `UpperPlaza`, `FlatPlaza` (twin) |
| 21 | `Terrace` |

---

## 6. Scene-level changes the matrix asked for (not kit elements)

| scene | change | source |
|---|---|---|
| 17 | `M["asphalt"]` constant colour → **real PBR** (`asphalt` diff/nor/rough, `scale = 3.0`, tint (0.42,0.42,0.45)). The texture set has been in `assets/scene01` all along and this scene simply never bound it — the batch's worst frame (d2 flat 99.78 %) was flat because a constant-colour road has no spatial frequency at grazing angle | §5.9 ① |
| 17 | crown re-cut: bike **3.0 → 4.0** (x −4.0…0), **0.5 m planting strip** (x −4.5…−4.0, new `GreenStrip` prim), walk relocated to x −7.5…−4.5. `crown_bike.proud` 0.004 → **0.006** so both hard bands share one top plane at z = +0.006, which is the plane `plan_ground(z=...)` is given. `crown_line.x` −1.5 → −2.0 (centre of the widened bike road), z 0.010 → 0.008 (2 mm proud instead of 8). `crown_lights` x −6.4 → **−7.9** — the old x would have put lighting poles in the middle of the relocated footway | §5.9 ②, §5.7 ruling 07-29 ("자전거도로는 scene17 제방만 유효") |
| 19 | `parapet_color` (0.90, 0.90, 0.87) → **(0.40, 0.40, 0.385)**, rough 0.60 → 0.66. One constant is bound to every parapet, guard and gate post in the scene; it is the direct cause of scene19 being the #1 near-white offender | §5.6 19-2 ("상수색 폐기") |
| 19 | parapet **turn-up + coping**: the waterproofing coat wraps each roof parapet's inner face for 0.30 m in the deck's green (`coating_color`, the M2 0.16–0.22 band at its 0.19 centre), and a 0.50 m coping caps it, centred so it overhangs 0.125 m each side. 12 mm plates, no GT change; the `roof_context` eye sits at z 1.9, above the 1.15–1.20 crown, so no new occlusion | §5.6 19-2 |
| 20 | charcoal band series extended x1 −5.0 → −0.5 (7 bands), with the per-band mesa clamp of D-5 | §5.1 scene20 row |
| 18 · 19 | four/two dedicated dark kit materials (`gk_joint`, `gk_iron`, `gk_stain`, `gk_salt` / `gk_iron`, `gk_stain`, `coating`) so the **declared** albedo and the **bound** material agree — defect **D5** of `w2_pilot_ground_v1` §7 (B9 gates a declared value while the scene binds anything). Scenes 14/16/17/20/21 already owned suitable dark materials (`band_dark`, `granite_dark`, `conc`, `curb`) and bind those | D5 |

---

## 7. Verification `[실측]`

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs
unset PYTHONPATH VIRTUAL_ENV
python3 ground_kit.py                                     # exit 0, 33/33 hard gates
python3 scripts/geom_invariance_check.py \
        --scenes scene14,scene16,scene17,scene18,scene19,scene20,scene21
python3 -m py_compile scenes/main/scene1{4,6,7,8,9}_*.py scenes/main/scene2{0,1}_*.py
NEGOBS_SELFCHECK=1 python3 scenes/main/scene18_wavy_artstair.py   # wave + horizon
```

| check | result |
|---|---|
| `python3 ground_kit.py` | **exit 0**, output byte-identical to the pre-edit run (this batch touches no fixture) |
| `geom_invariance_check.py --scenes <my 7>` | **R-4 7/7 ✔ · R-6 7/7 ✔**, assembly 7/7 in all three arms |
| `geom_invariance_check.py` (all 33) | **R-5 ✔ · R-4 33/33 ✔ · R-6 33/33 ✔** (final run, exit 0). Prims: 14 → 871, 16 → 604, 17 → 972, 18 → 1957, 19 → 288, 20 → 490, 21 → 538 |
| hazard-off twins (`NEGOBS_SCENE_CONFIG={"hazard_stairs":false}`) | all 7 assemble, kit runs in both arms (7/7 `[ground_kit]` lines) |
| `py_compile` | 7/7 OK |
| scene18 `NEGOBS_SELFCHECK=1` | **SELFCHECK OK** — wave geometry and sea-horizon visibility unchanged by this round |
| prim delta = plan prims | 14 +50, 16 +52, 17 +55 (54 kit + `GreenStrip`), 18 +51, 19 +55 (41 kit + 14 turn-up/coping), 20 +51 (49 kit + 2 bands), 21 +47 — every kit delta equals its planned count |

---

## 8. Riders for the GPU round

| # | item | why it matters |
|---|---|---|
| **R1** | `SCENE_PLANS["scene19"]` fixture: `origin` 9.04 and `region x1` 21.0 do not match the scene (grid origin 11.6, deck ends at 17.0, drop lip at s = 7.6). The fixture passes its own gates, so nothing fails today — but it is a check fixture that no longer checks the scene. `ground_kit.py` is outside this mission's file set | a future edit "aligned to the fixture" would move elements off the roof |
| **R2** | §5.1 rows for **01 and 02** carry trench centre −2.55. With the 0.040 frame lip that is `drow = 15.70 < 16` at d10 (§2.1). Those two scenes belong to other g-batches | same B7 failure, same fix (−2.59) |
| **R3** | B5 (≥ 6 soiling decals with X ≤ 3) warns on all seven, as it did on all three pilots. It is structural: 8–12 decals scattered over a 10–12 m region put 1–3 in any single 1–2 m counting window. Either the target or the placement model needs a ruling | the gate currently cannot pass by design |
| **R4** | Near-window monopoly: scene18 d2 = 100 %, scene21 d2 = 94 %, scene14 d2 = 70 % — a single repair patch. At d2 the frame half-width is 0.33–1.15 m over the whole W1, so **any** 0.7–0.9 m object there fills the frame. The scene15 pilot ruled a patch at 86.6 % acceptable ("a tone change, not an object") while a manhole disc at 56 % was not | eyes-on confirmation wanted in the 13-cut round |
| **R5** | scene17's asphalt tint (0.42, 0.42, 0.45) and scene19's parapet (0.40, 0.40, 0.385) are this round's guesses at a target mean; both are T1's domain in the end | re-measure after the render, adjust in T1 not here |
| **R6** | scene20 d2 near window is unfillable by the kit (D-6). If the d2 cut needs near-field structure it must come from geometry that follows the diagonal — a rot-group-local element, which the kit's axis-aligned region model cannot express | decide before judging scene20's d2 on σ_LF |
| **R7** | §7.5 A1: σ_LF / sd stay informative-only for ground-only rounds, but **T1 now exists**, so the first post-T1 round should restore the σ_LF ≥ 5.0 WARN gate (w2c rider 4). These seven should be measured under that gate | otherwise T1's absence keeps being mis-attributed to the kit |

---

## 9. Blockers

**None for this batch.** Final state: `python3 ground_kit.py` exit 0 · 33/33 hard gates ·
`geom_invariance_check.py` R-5 ✔ / R-4 33/33 ✔ / R-6 33/33 ✔ · `py_compile` 7/7.

One note on the working tree, for the supervisor's merge. The tree is being edited
concurrently by the other W2-D batches — `git status` shows `ground_kit.py`,
`scene_common.py`, `infra_kit.py`, `facade_kit.py`, `stair_kit.py`, `scripts/regression_check.py`,
scenes 01–12 and the batch1 set all modified alongside these seven. Two consequences:

1. An intermediate 33-scene run during this session aborted on
   `✗ sceneD2: NameError: name 'build_ground_kit' is not defined` — a mid-edit state in
   another agent's file. It cleared on the re-run and is recorded here only so that the same
   symptom is not mistaken for a regression if it reappears while batches are still landing.
2. The gate numbers above were measured against the **current** `ground_kit.py`, which other
   batches are also editing. If the kit changes further before merge, re-run
   `python3 ground_kit.py` and `scripts/geom_invariance_check.py` once at the merge point.
