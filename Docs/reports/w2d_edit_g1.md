# W2-D G1 — ground_kit applied to scene01 · 02 · 03 · 04 · 05 · 06

2026-07-30 · branch `feat/realism-v1` · **CPU only — no GPU, no render, no Isaac, no SMOKE**
Owned files: `scenes/main/scene0{1..6}_*.py` (+ this report). `ground_kit.py` was **not** modified.

Spec: `Docs/briefs/ground_kit_spec_v1.md` v1.1 + §7.5 amendments · pilot pattern `e196c93 cb40ae8 753b791`
Riders: `Docs/reports/w2_pilot_ground_v1.md` §7 · `Docs/reports/w2c_merge_t1_v1.md` §6–7

---

## 0. Verdict in one paragraph

All six scenes are wired, all hard gates pass in every toggle arm, and the 33-scene geometry
invariance check stays 33/33. Six of the matrix rows landed as written; **five did not, and in
four of those cases the spec's own arithmetic is what stops them** — the §5.0 C-1′ trench
coordinate is short by the trench frame lip, GT-E2's one-cross-line budget is already spent by
the statutory tactile band in 01/02, §2.3's origin table omits scene05 (which shifts its grid by
−1.5 m, invalidating every §5.1 coordinate for that row), and §5.7's scene03 prescription
survives the supervisor's cycle-track hold only as a natural profile, which P13 is not. Each
deviation below carries the number that forced it. Nothing here is a look judgement: **σ_LF / sd
are not measurable without a render, and per §7.5 A1 they are informative-only in a
ground-only round anyway** — the GPU round that follows owns them (and per W2-C rider #4 it
should restore the σ_LF ≥ 5.0 WARN gate now that T1 exists).

---

## 1. What landed

| scene | profile | region (world) | origin / axis | drop edge | kit prims | scatter | δmax |
|---|---|---|---|---|---|---|---|
| **01** | P1 `plaza_granite` | x −12.0…0.0 · y −5.5…5.5 | (0,0,0) / +x · gy −2.75 | `stairs.x0` = 0 | **46** (47 w/ tactile) | 0 | 0.1141 |
| **02** | P3 `sidewalk_block` | x −12.0…0.0 · y −4.0…4.0 | (0,0,0) / +x | `pit.x0` = 0 | **46** (47 w/ tactile) | 0 | 0.1166 |
| **03** | P13 `levee_paved` *(natural-forced)* | x −12.0…0.0 · y −3.0…3.0 | (0,0,0) / +x | `levee.x1` = 0 | **21 + 1** direct | 0 | 0.0020 |
| **04** | P11 `trail_soil` | x −12.0…−2.4 · y −3.0…1.0 | (0,0,0) / +x | `stairs.x0` = 0 | **7 + 3** direct | 250 | 0.0006 |
| **05** | P1 `plaza_granite` | x −13.5…−3.7 · y −5.0…5.0 | **(−1.5,0,0)** / +x | bowl lip s=0 | **48** | 0 | 0.1019 |
| **06** | P9 `bridge_deck` | x 2.0…5.0 · y −13.0…13.0 | **(3.5,−13,5) / −y** | well rim s=0 | **32** | 0 | 0.0006 |

δmax > `GT_DELTA` in 01/02/03/05 is the weed exception (`exc="weed"`, GT-E5 ramp-clamped), not a
new drop. Every plan is under the §8.1 standard cap of 60 geometry prims. All coordinates are read
from each scene's own `PARAMS` (§7.4); no spec coordinate is hard-coded in a builder call.

### Per-scene element list

* **01** — slab joints 1.8 m + expansion 6.0 m · manholes ×2 `(−3.80,−2.40)` `(−8.40,−2.60)` ·
  stair-head gullies ×2 `(−0.95, ±5.10)` (C-1′) · patch ×2 · crack ×4 · stain dirt/water ·
  weed band · **tactile `stair_top`** (statutory x −0.90…−0.30, full stair width), gated by
  `cfg["cue_tactile"]`, replacing the old local `Tactile` box.
* **02** — interlock joints 3.0 m · manhole `(−1.20,+0.35)` · gullies ×2 `(−0.95, ±3.60)` ·
  patch ×2 · crack ×4 · stain dirt/gum · weed band · **tactile `stair_top`** replacing the old
  `Tactile_Top`; the lower-landing band stays on the existing `sc.build_tactile` path (z = −3.2 is
  a different surface, and the landing redesign is W4).
* **03** — trampled bare-soil patches ×8 (dirt-bound, = §5.7 "답압 노출토 8~12") ·
  stain dirt/water · wear lane along the crest walking route (x = −3.50, |y| ≤ 10) ·
  `build_edge_break` on the landward gravel/grass seam (x = −4.0, |y| ≤ 3.0).
* **04** — wear lane + edge litter on the ConnectU landing · stain dirt · gravel/debris scatter
  250 · `build_edge_break` ×3 on the ConnectU seams (x = −3.0 and y = ±3.0).
* **05** — slab joints 1.8 m + expansion 6.0 m · manhole `(−3.90,−0.40)` · gullies ×2
  `(−10.00,0.00)` `(−6.00,−3.00)` · patch ×2 at explicit d2-window sites · crack ×4 ·
  stain dirt/water · weed band. Stage / tiers / ring / lip untouched (W3).
* **06** — expansion joints at y = −9 / 0 / +9 · scuppers ×4 at the deck edges ·
  non-slip coating band (width 2.0, via `wear_lane`) · crack ×4 · stain water/drip.

### `SKIN_EXCLUDE` registrations (P-A, spec §1.2)

| scene | paths | effective today? |
|---|---|---|
| 01 | `/World/Scene01/UpperPlaza` | no — scene01 uses a **local** `add_box` that never calls `_ground_skin`; forward guard |
| 02 | `.../Walk_W` (+ flat-control slabs) | **yes** — `sc.add_box`, 18×16 m `plaza_lower`, passes `_skin_wanted` |
| 03 | `.../LeveeBack`, `/Levee`, `/LeveeRoad`, `/LeveeSpur` | no — `river_band` builds through `sc.build_slope`, which carries no skin; forward guard |
| 04 | `.../UpperFlat`, `/ConnectU` | UpperFlat is 35×50 m `grass`; ConnectU is 3.0 m wide (< 4.0 threshold) |
| 05 | `.../Plaza_W/E/N/S`, `/PlazaRing`, `/PlazaFlat` | **yes** — `Plaza_W` is 9.5×28×0.5 m `plaza_light` |
| 06 | `.../Deck` | no — deck is 3.0 m wide (< 4.0 threshold); forward guard |

---

## 2. Deviations from the matrix — with the number that forced each one

### 2.1 `[계산]` scene01 / 02 stair-head trench: **not built**

Spec §5.1/§5.2 still list a full-width trench at x = −2.55. Two independent B7 failures, both
reproduced with `plan_ground`:

| # | measurement | result |
|---|---|---|
| a | C-1′ sized the **0.30 m slot** but not the frame. `build_trench_drain` adds a lip of `trench_frame_w` = 0.040 m per side, so the near boundary is x = −2.36, not −2.40. `drow(−2.36, d10) = 15.70` rows @1080 against the 16-row floor → **B7 FAIL**. Correct centre is **x = −2.59** (near edge −2.40, drow 16.05). | spec coordinate is 0.04 m short |
| b | Even at −2.59: at d10 the trench (X = 7.41) and the statutory tactile band (X = 9.40) are both inside the E band `[0.7d, 2.2d]`, and both are singular cross lines. GT-E2 allows **one**, and GT-E2-x already assigns that one to the tactile band. → `B7: E 대역 전폭 횡단 단선 2본 이상` | trench and tactile are mutually exclusive |

Verified: with `cue_tactile=False` the corrected trench passes; with `cue_tactile=True` it raises.
A hard gate that depends on an ablation toggle is worse than no trench, and C-1′ ② already moved
the stair-head drainage duty to the two point gullies, which **are** built. Recommend the spec drop
the trench from rows 01/02/14 (14 is not mine) or re-open it as a supervisor item.

### 2.2 `[계산]` scene01 charcoal band re-phasing (2.7 → 1.5 m): **not applied**

§5.1 asks for `spacing 2.7 → 1.5` so the bands stop missing all three near windows. The bands are
full-width, high-contrast (`granite_dark` on `plaza_light`) transverse lines. To enter the **d2**
W1 window a band must sit at x ≥ −1.436, and there:

| band x | drow @ d10 | in E band? |
|---|---|---|
| −1.000 (what spacing 1.5 produces) | **5.65** | yes |
| −1.436 (far end of the d2 W1 window) | **8.53** | yes |
| −2.400 | 16.05 | yes — first compliant |
| −2.500 (**what spacing 2.7 produces today**) | 16.94 | yes — compliant |

So no band spacing can serve the d2 near window without putting a full-width high-contrast line
5.6–8.5 rows from the drop-edge row at d10, i.e. exactly the fusion GT-E2 exists to prevent — and
in the hazard-off twin that line stands alone as an edge signal (GT-E4). The current 2.7 m spacing
is already the compliant one. Left unchanged; the d2 window is filled by the tactile band, patches
and stains instead.

### 2.3 `[실측]` scene05 grid origin is shifted and §2.3 does not say so

`build_views()` subtracts 1.5 from every preset eye/tgt so that "distance d" means "d to the bowl
lip at x = −1.5". §2.3's origin table lists 01·06·11·19·D1·D4 — **not 05**. Consequences:

* the §5.1 manhole at x = −3.5 sits exactly on the **d2 eye** (eye_x = −1.5 − 2 = −3.5);
* the §5.1 sump at x = −8.5 is 1.5 m short of the d10 window.

Re-derived with `origin=(−1.5,0,0)`: manhole `(−3.90, −0.40)` → X = 2.60 m at d5, screen width
414 px = **21.6 %** (same W1→W2 construction as the scene15 pilot fix M9-ⓑ; inside W1 a 0.648 m
cover cannot stay under 25 % — 28.1 % even at the far end). Gullies `(−10.00, 0.00)` (d10 window,
X = 1.50) and `(−6.00, −3.00)`.

### 2.4 `[실측]` scene05 joint grid stops at x = −3.70 — a kit defect, not a design choice

See D-1. Cutting the region at −3.70 keeps exactly the tick set an origin-aware guard would keep
(−5.4, −7.2, −9.0, −10.8, −12.6). The two patch **sites** carry the d2 window instead, since
`build_patch_field` honours explicit sites regardless of the region.

### 2.5 `[결재]` scene03 is run as a **natural** profile

The 07-29 ruling ("scene03 은 자연 유지, 자전거도로는 scene17 제방만 유효") removes the paved half
of P13. The scene therefore passes `overrides=dict(natural=True, infra=…0…)`, which makes
`plan_ground` itself raise on any urban infra — the §5.7 "도시 인프라 0건" rule is now enforced by
code rather than by discipline. Interlock joints are switched off too: there is no interlock paving
on this crest (grass + a 3 m gravel band + the stair-head spur), and the ledger's 200 mm unit cell
would draw a grid onto grass. **The `SCENE_PLANS` fixture for scene03 still carries manhole 1 /
gully 2 / gutter_L 1 by profile default** — see D-6.

Also dropped: the §5.7 silt band. `[계산]` the crest top is z = 0 and the water line is at
z = −3.35 (riprap bottom); silt deposition belongs to the 둔치 at z = −3.2, which is outside every
h0.3 near window.

Also dropped: the river-side seam break at x = −1.0. `drow(−1.0, d10) = 5.65` rows, and for
|y| ≤ 1.2 it is gravel-on-gravel (LeveeSpur) so there is no boundary there to break.

### 2.6 `[계산]` scene04 region split at x = −2.40

The scatter field is driven by the plan **region**, and `apply_ground` does not clamp it. Exposed
gravel has exposure ≤ 0.06 m, so GT-E5 demands `|x_e| ≥ 40 × 0.06 = 2.40 m`. The region therefore
ends at −2.40 (d5 and d10 windows sit fully inside it) and the d2 window is filled by the decal
elements, which are +0.6 mm and need only 0.024 m of clearance: wear lane and edge litter get an
explicit centre line on the ConnectU landing. That landing is also the one straight piece of trail
in frame — the PathU polyline meanders out of it (at x = −9 its centre is y = −2.46 while the frame
half width is 1.16 m).

The three ConnectU seams (`build_edge_break`) are direct builder calls because `_compose_ops` can
only emit constant-y lines and the main seam here is constant-x. `drow(−3.0, d10) = 21.76` ≥ 16 ✔.

### 2.7 `[실측]` scene06 joints via `step_y`, coating band via `wear_lane`, no tactile

* This scene travels −Y, so a bridge expansion joint is a **constant-y** line. `step_x` is off and
  `step_y = 9.0` gives y = −9 / 0 / +9 exactly as §5.3 asks. See D-4 for the tagging defect this
  exposes; the joints are safe regardless (`drow(y=−9 → s=−4, d10) = 33.81` ≥ 16).
* The 논슬립 도막 밴드 (width 2.0) is carried by `wear_lane` with an explicit centre line.
  `build_membrane` is a P6 builder whose region is the whole trimmed plan area and cannot express a
  2.0 m band on a 3.0 m deck; its albedo target 0.16~0.22 is a T1 matter anyway (§4.4).
* No tactile: §12.4 puts scene06 on **hold** (the "full width" of a helical flight is undefined),
  so it is absent from `TACTILE_SITES` and any call would raise B11. The scene's own
  `cue_tactile` path is left untouched as the ablation route.

### 2.8 `[시방]` scene02 `gutter_L` switched off

§5.2 puts scene02's L gutter on the kerb line at x = 7.85 — behind the pit and outside every h0.3
near window. The composer would otherwise draw it along the region's own y0 edge (y = −3.85), i.e.
across open sidewalk where no kerb exists.

---

## 3. Defects found (carried to the supervisor — none are in files I own)

| # | defect | evidence | severity |
|---|---|---|---|
| **D-1** | `_edge_guard_ticks` is **origin-unaware**: it feeds the world x of each tick into `drow()`, which expects a forward-s offset. On scene05 (origin −1.5) it drops tick x=−1.8 for the wrong reason (reads drow 11.16, true 1.57) and **keeps** tick x=−3.6 (reads 28.54, true 13.51 < 16) → `plan_ground` raises B7 on `Joints/JX_5`. Affects every scene with a non-zero origin: 01(gy only, safe) · **05** · 06 · 11 · 19 · D1 · D4. | reproduced; region cut at −3.70 as the workaround | high |
| **D-2** | Spec §5.0 C-1′ trench centre x = −2.55 ignores the 0.040 m frame lip → `drow(−2.36, d10) = 15.70 < 16`, i.e. **the corrected coordinate violates the gate it was derived from**. Correct value −2.59. | §2.1(a) | high (spec) |
| **D-3** | GT-E2's "one singular cross line per cut" makes the stair-head trench and the statutory tactile band mutually exclusive in 01/02/14 — the spec asks for both in the same row. | §2.1(b) | high (spec) |
| **D-4** | Line classification is **not axis-aware**: `build_joint_grid` tags constant-x lines `cross_periodic` and constant-y lines `long` regardless of `axis`. On a −Y scene (06) the real transverse joints are tagged `long`, so they escape B7 entirely and inflate B4 instead. | scene06 joints report as `long`; B4 = 2 at d5/d10 | medium |
| **D-5** | `apply_ground` ignores `profile["scatter"]["kind"]` — it calls the callback with no `pool`, so **every** profile's scatter comes from `scene_common.VEG_DEBRIS`, which today is 5 fallen-leaf assets. A "gravel" prescription (P11 04, P12 07, P18 10) renders as autumn leaves. Benign in 04 (leaf piles are already scene identity, §3.1 exception) but it is a seasonal-asset leak everywhere else. | `VEG_DEBRIS` = fallcluster1/2, maplefall1, oakfall1/2 (5/5 present) | medium |
| **D-6** | `SCENE_PLANS["scene03"]` uses `levee_paved` with default infra, so the CPU self-check green-lights **manhole + 2 gullies + L gutter on a natural scene** — a §5.7 violation the gate cannot see (`natural` is a profile flag, and the fixture never sets it). The scene now forces it; the fixture should follow. | `python3 ground_kit.py` row `scene03 … PASS` | medium |
| **D-7** | §2.3 origin table omits scene05, which invalidates the §5.1 coordinates for that row (manhole lands on the d2 eye). | §2.3 | medium (spec) |
| **D-8** | Pre-existing `cue_tactile` boxes in scene01 (`/Tactile`) and scene02 (`/Tactile_Top`) sat at x −0.30…0.00: no statutory 0.30 m set-back and a GT-E1′ violation (6 mm dot needs 40×0.006 = 0.24 m, they had 0). **Fixed** by routing both through ground_kit. | §12.1, §6.2 | fixed here |
| **D-9** | Pre-existing charcoal bands are ungated full-width transverse lines inside the d10 E band: scene05's band at x = −2.00 is s = −0.50 → **drow 2.68** rows @1080. They are scene geometry, so B7 never sees them, but they are the exact GRAZE-fusion pattern GT-E2 forbids for kit elements. scene01's nearest band (x = −2.50, drow 16.94) is compliant. | §2.2 table | medium — round judgement |
| **D-10** | The 33-scene invariance run raced twice with concurrent edits by other agents (sceneC4 written 21:29:35 during a run started 21:30:13 → V1 mismatch; sceneD3 written 21:34:55 during a run started 21:34:52 → MTL mismatch). Both passed on immediate re-run. Not a code defect — a note for whoever reads a red run during the parallel wave. | file mtimes vs run windows | note |

---

## 4. Verification (CPU, no render)

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs
python3 -m py_compile scenes/main/scene0{1,2,3,4,5,6}_*.py     # OK
python3 ground_kit.py                                          # exit 0
python3 scripts/geom_invariance_check.py                       # exit 0
```

**`python3 ground_kit.py` → exit 0**, "자기검산 — 전 항목 통과", 33/33 hard gates.
Note the self-check's scene01–06 rows exercise the **fixtures** in `SCENE_PLANS`, not the wiring
added here (they differ deliberately — see D-6 and §2). The wiring itself was verified by replaying
each scene's own `plan_ground` arguments read straight out of its `PARAMS`:

| plan | prims | scatter | δmax | hard gates | WARN |
|---|---|---|---|---|---|
| scene01 `cue_tactile` OFF | 46 | 0 | 0.1141 | **PASS** | B4, B5 |
| scene01 `cue_tactile` ON | 47 | 0 | 0.1141 | **PASS** | B4, B5 |
| scene02 `cue_tactile` OFF | 46 | 0 | 0.1166 | **PASS** | B3, B4, B5 |
| scene02 `cue_tactile` ON | 47 | 0 | 0.1166 | **PASS** | B4, B5 |
| scene03 | 21 | 0 | 0.0020 | **PASS** | B3, B4, B5 |
| scene04 | 7 | 250 | 0.0006 | **PASS** | B1, B2, B3, B5 |
| scene05 | 48 | 0 | 0.1019 | **PASS** | B4, B5 |
| scene06 | 32 | 0 | 0.0006 | **PASS** | B1, B2, B3, B5 |

B1–B5 are frame-fill targets (WARN, §7.1), and per §7.5 A1 the final call belongs to post-render
σ_LF / sd. B1/B2 fill improved to "hit in all three cuts" for 01 (d2 37.1 % with tactile, d5
104.2 %, d10 35.1 %), 02 (d2 107.3 %) and 03 (82.3 / 35.5 / 41.2 %). scene04 and scene06 keep
B1/B2 WARN by construction: `trail_soil` has no area builder at all (its filler is the 250-instance
scatter, which `frame_budget` does not count), and `bridge_deck`'s only area elements are the four
edge scuppers, which sit at |t| = 1.15 m from the deck centre line — just outside the 1.16 m frame
half width at X = 2.0.

**`python3 scripts/geom_invariance_check.py` → exit 0 · R-4 33/33 · R-5 PASS · R-6 33/33.**

| scene | prims | MTL=0 | MTL=1 | V1=1 |
|---|---|---|---|---|
| scene01 | 365 | `268c2386` | `268c2386` | `268c2386` ✔ |
| scene02 | 523 | `cb430e00` | `cb430e00` | `cb430e00` ✔ |
| scene03 | 1556 | `c6340a7d` | `c6340a7d` | `c6340a7d` ✔ |
| scene04 | 1035 | `b9898be8` | `b9898be8` | `b9898be8` ✔ |
| scene05 | 1246 | `55158b19` | `55158b19` | `55158b19` ✔ |
| scene06 | 1619 | `67b17d15` | `67b17d15` | `67b17d15` ✔ |

Toggle arms (all six scenes, all three hash arms, 6/6 ✔ each):

| `NEGOBS_SCENE_CONFIG` | result |
|---|---|
| `{"cue_tactile":true}` | PASS — 01 +1 prim, 02 +2, 03/04/05 +1, 06 +2 (their own cue paths) |
| `{"hazard_stairs":false}` | PASS — the kit runs in the hazard-off arm too for 01–05 (GT-E4 twin parity); scene06 skips it because the control removes the deck |
| `{"cue_scene_dressing":false}` | PASS |

---

## 5. Not done / carried

* **No renders.** σ_LF, sd, OCCL, GRAZE and every eyes judgement belong to the GPU round.
  Per W2-C rider #4, that round should restore the σ_LF ≥ 5.0 WARN gate (§7.5 A1 scoped it out
  only until T1 existed — it now does).
* **scene02 lower landing / underground branch** untouched (`tunnel_under` profile, z = −3.2).
  Landing redesign is W4.
* **scene05 stage / tiers / ring / lip** untouched (W3).
* **sceneD4** untouched (M8 deferral) — not in this batch anyway.
* **Materials.** Every kit element is bound to an existing scene material; the colour-difference
  half of patches/stains is T1's (§4.4), so those elements are currently tone-neutral. This is the
  same condition that kept scene15's σ_LF flat in the pilot (§7.5 A1) and it is expected.
* `unit_cell` is reported unchanged from the ledger by profile. For scene03 the plan now returns
  `levee_paved`'s 0.200 m cell while the scene has **no** modular paving; T1 must not enable unit
  jitter there (U4 class issue, worth a ledger note when D-6 is fixed).
* D-1 … D-7 are `ground_kit.py` / spec fixes and were deliberately **not** made here (file
  ownership). D-1 in particular will re-appear on 11 · 19 · D1 · D4 in the other G-batches.
