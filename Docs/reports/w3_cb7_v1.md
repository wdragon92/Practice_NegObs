# CB-7 — scene02 respec execution (GT-1 sill · GT-2 kerb · GT-3 canopy REBUILD)

> **Wave**: W3 · **Lane**: 1 (kit revival + closures) · **WP**: S2 · **Date**: 2026-07-31
> **Branch**: `feat/realism-v1` · **HEAD at open**: `dc68e74`
> **Files this workflow wrote**: `scenes/main/scene02_underpass.py` · this report ·
> `Docs/reports/regr_260731_w3_cb7.json` · `Docs/reports/regr_260731_w3_cb7_pre.json` ·
> `Docs/reports/_w3_cb7_crops/*.png` · `Docs/audit_v4/gt_changes_w3.md` (§3 status + §4
> landing records for GT-1/GT-2/GT-3 **only**) · `look_check/scene02/260731_w3_cb7{,_pre}/`
> (gitignored) · `dataset/260731_cb7_recache/` (gitignored)
> **Not touched, by instruction**: `scenes/main/scene18*`, `assets/coastal` (S18 lane is live) ·
> every kit (`infra_kit` / `props_kit` / `building_kit` / `facade_kit` / `stair_kit` /
> `scene_common` / `ground_kit` are **consumed**, not edited) · every other scene.
>
> **LAW followed, in order**: `Docs/surveys/w3_intake_v2_images.md` §2 scene02 row · §3(i) ·
> §7-1 · `Docs/audit_v4/gt_changes_w3.md` §0 (append-before-land) and §9-1 (the GT-3 flip) ·
> `Docs/briefs/w3_execution_spec_v1.md` §1.5 (sill / kerb / landing-block clauses; its
> Option-A canopy clause is **superseded** on that one clause) · §6.1 floor · §12 do-not-touch ·
> `Docs/reports/w3_k4_v1.md` (RF-1 / RF-2) · `Docs/reports/w3_k5_v1.md` (`build_curb_line`) ·
> `Docs/reports/w3_s16_v1.md` (BS-4 pattern, canopy reference form).
> **Target image**: `Docs/reference_photos/Generated Image - Scene02.jpg` (**G2**), viewed.

---

## 0. Verdict in one table

| # | Item | Status | Evidence |
|---|---|---|---|
| **GT-1** | Flood sill — apron `x −1.20…0.00`, `y ±2.10`, top **+0.180**, **one** 0.180 riser at `x = −1.20` labelled **UP-STEP**, mandatory handrail on **RF-1** plates in the **RF-2** `sts304_10s` rung | **LANDED** | §2 · self-check [1] · §7 R-1/R-2/R-3 |
| **GT-2** | Kerb rebuilt on `infra_kit.build_curb_line` — 1 m unit blocks, 6 mm joint recess, R10 arris via `LOOK_CLASS["curb"]`, top **+0.020** above the footway, exposure **0.150** above the carriageway | **LANDED** | §3 · self-check [2] |
| **GT-3** | Canopy **content-flipped**: porch deleted → **full-length, enclosed, soffit-lit** canopy `x −1.90…7.15` | **LANDED** | §4 · self-check [3] |
| G2 feel | Enclosed descent + tile-clad walls under a granite coping + BS-4 downtown wall both verges | done | §5 · §8.4 crops |
| Stale block | The v8 landing / mid-rail docstring proposal **deleted**; no prim existed, pit end stays `x1 = 7.0` | done | §6 |
| Deleted prims | 8 paths checked **out** of the hazard/collision lists, residual path-construction 0 | done | self-check [4] |
| Baseline of record | **`260731_w3_cb7`** is scene02's new baseline (13 cuts, stamped) | done | §7.1 |
| Carried defect | **C02-P1** — a K4(b) `Elm_Sapling` + 2 rhododendrons stand **1.0 m** from `beauty_overview`'s eye. **Pre-existing at HEAD**, proved by an isolated A/B | reported, **not fixed** | §8.1 |

**§6.1 floor: all green** (§9). **Self-check `NEGOBS_SMOKE=1` rc 0, 48/48 assertions.**
**Prims 391 → 545 (+154).** Geometry-invariance **33/33 PASS**, `placement_lint` **byte-identical**.

**Prim census, by family** `[measured — isolated-arm prim-inventory diff, HEAD vs this commit]`:

| added | n | | removed | n |
|---|---|---|---|---|
| `Sill/*` (apron + 2 handrails + 4 posts + 4 RF-1 plate groups) | 51 | | `EntryCanopy/*` (porch roof + 4 posts) | 5 |
| `Curb_W` + `Curb_E` (`build_curb_line`) | 82 | | `Building_B/*` (brick slab over the carriageway) | 61 |
| `Canopy/*` | 50 | | `Road/Curb_W` + `Road/Curb_E` | 2 |
| `CityBlock_S/N` (BS-4, 10 buildings) | 30 | | | |
| `StreetApron_*` | 5 | | | |
| `WallTile_S/N` + `WallCoping_S/N` | 4 | | | |
| **total** | **222** | | **total** | **68** |

Net **+154** → **391 → 545**, inventory hash `a4c3a5f9`. The 10 canopy `SphereLight`s are lights,
not geometry, and are outside this census.

---

## 1. Why this scene needed a respec before it could be cut

`w3_execution_spec_v1.md` §1.5 ruled **Option A — delete the canopy**, and the ledger carried that
as **GT-3**. The user's second review reversed it twice over: *"Scene2 참조해서 좀 더 지하도
느낌으로"* and, pan-scene, *"지하 진입로 같은 경우에는 웬만하면 캐노피 진입로 끝까지 달려있도록
만들도록 하고"*. **G2** settles it in the image: a full-width canopy over the entire opening with
soffit lighting — Option **B** of 02-A. The supervisor confirmed the reversal (intake §7-1) and the
ledger batch executed the content flip (§9-1) while leaving the row's class (`R-3`), its gate
(CB-7 · GATE-1 pilot 02) and its status (`OPEN`) alone, with the standing instruction that
**CB-7 must be re-spec'd before it is cut**. This workflow is that cut.

Measured pre-state `[repro, this session]` — `scene02:240` at HEAD:
`canopy=dict(x0=-1.8, x1=0.6, y0=-2.45, y1=2.45, z_roof=2.7, post_r=0.08, roof_t=0.14)`
⇒ 2.40 × 4.90 m on four free posts covering **0.60 m of a ≈7.6 m descent**. Five prims, all with
colliders. Deleted.

---

## 2. GT-1 — the flood sill

### 2.1 Law, and the one clause everybody had missed

`w3_evidence_close_v1.md` §1.1 quotes 행안부 「지하공간 침수방지를 위한 수방기준 실무매뉴얼」
**3-1-1 해설(2)** verbatim: *"18cm 높이의 계단 1~3개"*, and — the clause the earlier intake rows did
not carry — *"난간은 … **반드시 설치**"*. So the sill is **not optional dressing**: it is a flood
structure whose 계단폭 doubles as a 둑마루, and it **always** carries a handrail. Both are built.

### 2.2 What was built

| element | value | note |
|---|---|---|
| apron | `x −1.20 … 0.00` · `y ±2.10` · top **z = +0.180** | 0.35 m wider than the opening half-width on each side, so the riser face is continuous across the whole mouth |
| riser | one, at `x = −1.20`, **0.180 m** | 0.180 ≤ the 0.180 statutory ceiling; **1** step of the statutory 1–3 |
| drop edge | `x = 0`, now **3.380 m** (was 3.200) | GT-1's declared figure, reproduced by the self-check |
| stair | 20 × **0.169** riser, tread **0.320**, `z_top = +0.180` | 0.180 − 20 × 0.169 = **−3.200** exactly: the foot still lands on the lower landing, and the tunnel, the portal and the lower landing do **not** move |
| parapet / lintel | +0.15 → **+0.18** | flush with the apron — the 둑마루 reading, and it closes the 30 mm seam the raise would otherwise open at `x = 0` |
| handrail | `y = ±1.68`, `x −1.12 … −0.32`, 0.85 m above the apron, φ34 | meets the stair handrail's top extension (raised 0.30 → **0.32**, still ≥ the statutory 0.30) at `x = −0.32`, same `z = 1.030`: the two read as **one** line |
| RF-1 | 4 posts × (bedding + 100 × 100 8T plate + 4 × Ø16 anchors + 4 nuts + drill-dust ring) | `props_kit.build_base_plate`, unmodified |
| RF-2 | `sts304_10s` | the sill is a 2024 retrofit; the entrance is not. **The contrast is the deliverable** (props_kit's own instruction), so every other post in the scene stays cast-in and the canopy columns get a **mortar collar**, not a plate |

**Why 0.169 and not 21 steps.** Three ways to absorb the +0.18: (a) re-space to 21 steps → run
6.72 m, which collides with the lower landing at `x = 6.4`; (b) 21 steps at tread 0.3048 → the
0.320 nosing period breaks, and that period **is** this scene's silhouette cue; (c) 20 × 0.169 →
run, tread, period, landing, tunnel and portal all bit-identical, one riser value changes, and
0.169 stays inside the 0.18 statutory ceiling. (c) is what landed.

**Consequence the sill forces, and it is not optional**: the `gkit` manhole sat at
**(−1.20, +0.35)** — *inside the apron footprint*, i.e. it would have been buried under the 0.18 m
platform. Moved to **(−2.90, +1.10)**. The old coordinate is also one of the "solved from the d5
frame occupancy" sites K5's G-4 census flags (the code comment literally says *"lands in the d2
near window"*), so the move is a correction in both directions. Manholes are flush ⇒ **no GT
change** (K5 J-11 keep-at-zero).

### 2.3 Two spec §1.5 companions that were **not** built, and why

1. **The 1:12 accessibility ramp.** GT-1's §3 row fixes the geometry as *"raised apron … ; one
   0.18 m riser at x = −1.20"*. A ramp is a walked surface with a z gradient — new GT geometry that
   **no row declares**. §0-1 forbids landing it. Prepared, not built; it needs its own row.
2. **The `x = −1.30` linear trench grating.** Refused on this scene's own **measured** evidence:
   `Docs/reports/w2d_edit_g1.md` §3 records that a stair-head trench pushes `drow` to 15.7 rows at
   d10 and adds a second singular cross line, which GT-E2 caps at one — and the sill riser is now
   that one line. The apron instead sheds sideways to the **two existing gullies** at
   `(−0.95, ±3.60)`, which sit 1.50 m clear of the apron edge on the same `x` band; the spec's own
   words were *"connected to the existing gully"*.

Both are recorded in the scene docstring so the next owner does not re-litigate them silently.

---

## 3. GT-2 — the kerb, and the number that forced the carriageway down

`build_curb_line`'s own docstring names scene02 as **the library's one outright shape error**:
`curb_top +0.10` above a 0.0 footway is a 100 mm trip line running the length of the walk.

The row asks for two things at once — *exposure above the carriageway 150 mm* **and** *curb top
flush … +20 mm above the footway*. With the footway at 0.000 those two fix the carriageway datum:
`z_road = 0.020 − 0.150 = −0.130`. So `road.top` moves **−0.020 → −0.130**. That is not a taste
edit; it is the only value at which the row is satisfiable, and `walk_a/walk_b` follow
(7.70/13.30 → **7.80/13.20**) so the sidewalk cut face meets the 0.20 m block body with no gap.

Measured, from the builder, on both lines `[repro — self-check [2], `dry_kit` A/B]`:

| | W line | E line |
|---|---|---|
| blocks / prims | 40 / **41** | 40 / **41** |
| unit inside the judged window | **1.000 m × 28 blocks** (min 0.994) | same |
| unit outside it | 7.66 m ≈ `far_unit` 8.0 | same |
| curb top | **+0.0200** | **+0.0200** |
| exposure above carriageway | **0.1500** | **0.1500** |
| `gt_drop` | **0.1500** | **0.1500** |
| `strict=True` warnings | **0** | **0** |

* `road_side` — `"right"` on the west line, `"left"` on the east, determined by an A/B on the
  builder, not by reading the convention off the docstring: block centres land at `x 7.9` and
  `x 13.1`, i.e. bodies at 7.80–8.00 and 13.00–13.20, on the footway side of each kerb face.
* `gutter=False`. This scene switched `gutter_L` **off** in W2-D with a measured reason recorded in
  its own `gkit` note (spec §5.2 puts 02's L gutter at `x = 7.85`, behind the pit and outside every
  h0.3 near window). Keeping it off means `gt_drop = height` exactly, with no cross-fall term — which
  is what GT-2's row says.
* `lod_span` = the judged band `y −14 … +14` (arc length 46 … 74 on a line that starts at
  `y = −60`), `far_unit = 8.0`. **41 prims per 120 m line instead of 121**, and the 1 m product
  rhythm is preserved exactly where a judged eye can resolve it.
* Material: a new `Looks/Curb` binding. `check_arris_role(sc)` asserted live — `LOOK_CLASS['curb']`
  bevel **10.0 mm**, so the R10 arris costs **0 prims**. S06-B item 3's `curb_granite_light` role is
  **not authored** (procurement HOLD this wave); `marble_light` is bound as the stand-in, which is
  the same stand-in K5's own test stage used, and `granite_dark` stays forbidden.

---

## 4. GT-3 — the canopy, as amended

### 4.1 Form

`x −1.90 … 7.15` (9.05 m) × `y ±2.45`, roof underside **z 2.70**.

| part | built | source |
|---|---|---|
| roof deck + 3 eaves fascias | 1 + 3 prims, 0.40 m eaves past the wall outer face | G2 · scene16's flat-deck precedent |
| transverse beams | **8** at 1.30 m | G2 shows ~7 over the opening. These are main beams, **not** C4 rafters, so the 300–450 mm rafter band does not apply `[practice]` |
| column line | **5 pairs** at 2.26 m, 0.12 × 0.12 box section, on the wall centre line `y = ±1.95` | G2 |
| column bases | mortar collar (cast-in) — **not** RF-1 | the RF-1 contrast (§2.2) |
| side infill | one opaque valance per bay per flank, `z 1.75 … 2.70`, plane `y = ±2.02` | §4.2 |
| soffit | 2 rows × **5** recessed 1.20 m battens at **2.20 m** pitch, each with its own `SphereLight` (40 000, Ø0.10, 0.93/0.96/1.00) | Korean underpass canopies run 1.2 m battens at 2.0–2.5 m centres `[practice]`; G2 shows two rows |

Coverage, printed by the scene at assembly and asserted by the self-check:
**approach 1.90 m** (GT-3/U-5 ask for ≥ 1.00; scene16 — the in-library reference at `:84` — has
exactly 1.00) **+ the sill riser and its apron + the whole 6.40 m descent + the lower landing +
0.15 m past the pit rear.**

**The front edge is at −1.90, not −2.20, for a measured reason.** The nearest judged eye is
`preset_h*_d2` at `x = −2.00`; at −1.90 all **9** grid cuts stand outside the enclosure and the h/d
grid goes on measuring the approach rather than the interior. `pit_edge` (−0.5, 0, 1.7) and
`inside_looking_up` (6.6, 0, −2.7) are **declared interior cuts** — they are the ones the soffit
battens exist for. The self-check gates this.

### 4.2 The infill: an arm that was built, rendered, measured and rejected

**r1** built the side infill as GT-3's word suggests at first reading — full-height **glazing**
from the perimeter-rail top (1.05) to a spandrel, using the library's `glass` material.
That material is an **opaque dark constant** `(0.06, 0.09, 0.12)` — correct for a 1.2 × 1.6 m
window, catastrophic as a 9 m × 1.35 m wall. Measured on the r1 round:

| cut | r1 (glazing) | r2/r3 (valance) |
|---|---|---|
| `beauty_overview` | **DARK** fires + PHOTO | DARK gone |
| `preset_h1.8_d2` | PHOTO mean **−45.8** | PHOTO gone |
| `preset_h1.8_d5` | PHOTO −25.8 | gone |
| `inside_looking_up` | PHOTO | gone |
| BS-4 street wall | **hidden behind the panels** | reads through the flanks |

The last row is the decisive one: r1's enclosure hid the dense downtown wall that the *same commit*
had just built, which is the opposite of what G2 shows — in G2 the shops read **past** the canopy
flanks at eye level. r2 therefore puts the infill where a real 지하보도 canopy has it: a **0.95 m
deep valance** under the roof, over an open ventilation band. The flank below it is closed by the
parapet (0 → 0.18) and the perimeter guard (0.18 → 1.08); the band **1.08 → 1.75** is left open,
deliberately, and is declared as such rather than hidden `[practice]`.

Evidence kept: `Docs/reports/_w3_cb7_crops/cb7_r1_glazing_rejected_beauty.png`.

> **Supervisor question S02-Q1.** GT-3's word is *"side infill"*. This commit reads that as
> *parapet + guard + valance*, closed above eye height and open at hand height. If the intent was a
> literally sealed flank, say so and it is one parameter (`canopy.infill_z0` 1.75 → 1.08) plus a
> non-`glass` panel material — but it will hide the BS-4 wall again, and that is the trade.

---

## 5. G2 feel — finishes and backdrop

**Wall finishes.** The 300 mm retaining wall is split into a 260 mm structural body, a **40 mm tile
cladding** on the inner face and a **60 mm granite coping** oversailing 20 mm each side (the drip
line G2 shows). The three solids abut face to face — the shared planes are interior and never both
visible, the same technique the sidewalk cut faces already use against the wall outer faces, so no
Z-fighting. +6 prims.

**What was deliberately *not* re-litigated.** G2's flanking walls are chest-height tiled parapets
with the canopy standing on them and no separate guard rail. Adopting that would delete this scene's
perimeter railing — which is simultaneously the fall protection for a **3.38 m** hole in a public
sidewalk and, per the file's own docstring, the scene's grazing-angle identity cue (*"from h0.3 at
distance the pit reads flat and only the perimeter rail floats"*). Neither is inside CB-7's brief.
Recorded as **S02-Q2** for the supervisor; not touched.

**BS-4.** `building_kit.plan_building(kind="backdrop", eyes=judged_eyes(0.0))` +
`build_korean_building`, 5 blocks per verge, facade lines at `|y| = 9`, heights 10.5–22 m.
Measured at assembly: **30 prims / 10 buildings, 4 in frame, 6 auto-demoted by BS-4**, plus 5 apron
strips. Two defects close with it:

* the old `buildings.B` brick slab ran `x −14 … 10` at `y 9 … 13` and therefore **straddled the
  carriageway at x 8 … 10**. Deleted; the north row replaces it, with the corner gap the cross
  street needs (`x 7.60 … 13.40`). `buildings.C` (the +X vista beyond the crossing) stays.
* the last strip of undesigned turf the judged cuts saw — `x 16 … 20` straight down the travel
  axis, a green band in every h1.8 cut — is paved by the 5th apron strip at the existing ground top
  + 10 mm. No walked surface moves.

---

## 6. The stale landing block

`scene02:29-33` / `:64-79` carried the v8 *"DESIGN PROPOSAL AND IS NOT YET REFLECTED IN THE CODE"*
statutory-landing + mid-rail table. **Deleted**, per spec §1.5 and
`era_consistency_survey_v1.md:881` (*02 landing (L1) = CANCEL* — 지하보도 is a 도로 부속물, outside
건축법 in every era, and landings are never retrofitted). It authored **no prim**, so nothing leaves
the stage by the deletion and the pit end stays `x1 = 7.0`. Two riders that die with it and are
recorded here so they are not resurrected: the `gy = −0.875` preset shift (there is no mid rail to
avoid, so `grid_views(0.0)` stands) and the `+1.20` downstream shift of the pit, tunnel, road and
signs (never implemented, and now contradicted by the sill's own arithmetic).

---

## 7. Rounds, and the baseline problem this scene had

**scene02 had no 13-cut baseline after GT-8.** Its last round, `260730_w2d_fix`, was captured at
HEAD `386fc88` — before GT-8/GT-9 (K1 ground_kit), K4(0)/(a)/(b)/(c)/(d), K5 and T4 all landed. So
this workflow rendered **two** rounds under `flock -w 7200 /tmp/negobs_gpu.lock`, in the same arm
(`NEGOBS_CAPTURE_MODE=pt · NEGOBS_PT_FAST=1 · NEGOBS_LOOK_V1=1 · NEGOBS_DETAIL_SCALE=2 ·
NEGOBS_DETAIL_ROUGH_GAIN=0`, 13 cuts, stamped):

| round | tree | purpose |
|---|---|---|
| `260731_w3_cb7_pre` | **HEAD `dc68e74`, isolated `git archive` arm**, scene02 untouched | the contemporaneous baseline scene02 never had — it isolates the *carried* deltas from CB-7's |
| **`260731_w3_cb7`** | HEAD + this commit | **scene02's new baseline of record** |

### 7.1 The split, and why it matters

| pair | FAIL | WARN | PASS | what it says |
|---|---|---|---|---|
| `260730_w2d_fix` → `260731_w3_cb7_pre` | 1 | 7 | 5 | **carried deltas alone** (GT-8/9, K4, K5, T4) |
| `260730_w2d_fix` → `260731_w3_cb7` | 12 | 1 | 0 | carried + CB-7, i.e. the figure the stale baseline gives |
| **`260731_w3_cb7_pre` → `260731_w3_cb7`** | **11** | **2** | 0 | **CB-7's own contribution** |

The single FAIL in the carried-only pair is `beauty_overview` — **PHOTO mean 160.6 → 103.1
(−57.5) · OCCL new-dark 32.8 % · blob 19.7 %**, with **nothing from this commit in the tree**.
That is defect **C02-P1** (§8.1). Against the stale baseline the same cut reads −72.3 / 40.4 %;
against the contemporaneous one it reads **OCCL 7.1 % and no PHOTO at all**. Adjudicating CB-7
against `260730_w2d_fix` alone would have charged 57 mean-points of somebody else's regression to
this commit.

### 7.2 `260731_w3_cb7_pre → 260731_w3_cb7` — CB-7's own numbers

| cut | verdict | mean | dark % | new-dark | blob | block shift | reason |
|---|---|---|---|---|---|---|---|
| approach | FAIL | 156.0 | 4.2 | 3.2 | 1.3 | 54 | FRAME, OCCL |
| beauty_overview | FAIL | 88.3 | 41.6 | 7.1 | 4.9 | 59 | FRAME, OCCL |
| inside_looking_up | FAIL | 69.4 | 29.4 | 3.4 | 0.3 | 55 | FRAME, OCCL, PHOTO |
| pit_edge | FAIL | 91.6 | 11.0 | 4.8 | 1.3 | 83 | FRAME, OCCL, PHOTO |
| preset_h0.3_d2 | FAIL | 168.5 | 2.9 | 2.0 | 0.3 | 82 | FRAME, OCCL, **GRAZE** |
| preset_h0.3_d5 | FAIL | 159.9 | 3.1 | 2.4 | 1.1 | 29 | FRAME, OCCL, **GRAZE** |
| preset_h0.3_d10 | WARN | 161.3 | 4.0 | 2.8 | 0.7 | 24 | FRAME, OCCL |
| preset_h0.9_d2 | FAIL | 112.0 | 8.1 | 3.3 | 0.8 | 75 | FRAME, OCCL |
| preset_h0.9_d5 | FAIL | 150.8 | 3.9 | 3.0 | 1.1 | 54 | FRAME, OCCL |
| preset_h0.9_d10 | WARN | 156.4 | 4.7 | 3.5 | 1.1 | 36 | FRAME, OCCL |
| preset_h1.8_d2 | FAIL | 106.0 | 8.4 | 3.6 | 1.2 | 86 | FRAME, OCCL |
| preset_h1.8_d5 | FAIL | 140.8 | 5.7 | 3.0 | 1.8 | 69 | FRAME, OCCL |
| preset_h1.8_d10 | FAIL | 151.2 | 5.6 | 4.2 | 1.6 | 46 | FRAME, OCCL |

JSON: `Docs/reports/regr_260731_w3_cb7.json` (CB-7's own) and
`Docs/reports/regr_260731_w3_cb7_pre.json` (carried-only).

* **DARK: 0 cuts.** BLOWN: 0.
* **OCCL fires on 13/13 — declared.** GT-3 as amended states it in terms:
  *"prims are ADDED, not removed: the sign of the prim delta flips, and the OCCL move is LARGER
  than the deletion it replaces."* A 9.05 × 4.90 m roof at z 2.70 over the judged axis is what that
  sentence buys. New-dark stays **≤ 4.8 %** on every cut except `beauty_overview` (7.1 %, the cut
  that also carries C02-P1) and near-band new-dark is **0.0 %** on 9 of 13.
* **FRAME on 13/13 — declared.** The commit adds a full-length canopy, a sill, a rebuilt kerb and a
  street wall on both verges. FRAME is measured after tone normalisation, so it is saying exactly
  what it should: the composition changed on purpose.
* **PHOTO on 2 cuts, both interior.** `pit_edge` −30.0 mean / dark +5.0 pp and
  `inside_looking_up` — these are the two **declared interior cuts** (§4.1), and a canopy over a
  descent is a shading device. The soffit battens carry them: without the 10 lights the same cuts
  went to DARK in r1.

### 7.3 GRAZE on `preset_h0.3_d2` and `_d5` — adjudicated visually, as the metric demands

> `[v2.1][의심] 은닉 — 국소도 47.8 (에지 50.1 − 근경 2.4) · 열 일치율 0.76 · 단차 54.3→2.0
> (비 0.04) · 최대 변화 y145 … 에지 대역 y131~212/540`

Crops: `_w3_cb7_crops/cb7_graze_band_h0.3_d5_{pre,new}.png` (rows 262–424 of 1080, i.e. exactly the
band the tool names).

* **pre**: the drop-edge band shows the pit as a dark trench with the far parapet past it.
* **new**: the band is filled by the **sill riser face** — a 0.18 m granite upstand standing across
  the full mouth, 0.80 m in front of the near lip. The trench is gone.

**Verdict: not a regression — it is GT-1 working.** The tool is measuring exactly the geometry the
행안부 manual mandates: raising the near lip by 0.18 m makes the grazing sight line from h 0.3
steeper, so it reaches *less* of the pit floor than before. The scene docstring already predicted it
(*"h0.3 concealment is strengthened, not weakened"*). For a **T3 negative-obstacle** scene whose
stated identity is *"from a low viewpoint the pit reads as completely flat ground"*, more
concealment is on-thesis, not off it. Note what replaces the drop cue in that band: an **UP-STEP**,
which `hazard_registry()` labels as such and which must never be written into a drop list.

This is the third live instance of the **D14** class (`regression_check.py` does not read
`EXPECTED_FP`); cite it when D14 is closed.

### 7.4 `near_ground_stats` — the h0.3 triple

| cut | sd | mean | wht % | σ_LF | edg % | f_gnd |
|---|---|---|---|---|---|---|
| d2 pre → new | 42.1 → **11.9 → 11.6** | 157 → 192 | 3.0 → 26.9 → **12.4** | 16.4 → 1.33 | 34.6 → 44.8 | 25.8 → **6.1** |
| d5 pre → new | 29.3 → 28.8 | 172 → 174 | 3.8 → 4.8 | 10.4 → 10.2 | 55.8 → 52.0 | 0.1 → 1.5 |
| d10 pre → new | 17.8 → 17.2 | 182 → 183 | 4.9 → 5.1 | 2.70 → 2.57 | 61.3 → 59.1 | 0.0 → 0.0 |

d5 and d10 barely move. d2 is the sill's cut and it moved three ways:

* **`flat_gnd` 25.8 → 6.1** and **`flat%` 31.4 → 0.07** — a large improvement. The pre-state's
  near field at d2 was a featureless paved plane; the sill puts a textured granite face and a joint
  line into it.
* **`wht%` 3.0 → 26.9 → 12.4.** The r2 arm bound the coping/apron/kerb at a cream
  `(0.90, 0.90, 0.88)`, and a 1.20 × 4.20 m cream plate 0.8 m in front of an h 0.3 eye is precisely
  the *"large near-white area"* the v5.1 §4 parapet ruling (0.90 → 0.72) already outlawed. r3 pulls
  the granite tint to **(0.72, 0.71, 0.68)** and the tile to (0.88, 0.86, 0.80) — which is also
  closer to real Korean 화강암, which is mid-grey, not cream. **26.9 → 12.4.** It remains above the
  library-wide `≥2` WARN line; going lower would mean lying about the material, so it is recorded,
  not tuned away.
* **`sd` 42.1 → 11.6** — the pre-state's d2 sd was inflated by the pit's dark trench occupying the
  near band. With the sill in front of it the band is a lit granite face. Both readings are below
  the 32 WARN line in the library-wide sense; the WARN set is otherwise unchanged.

---

## 8. Findings

### 8.1 C02-P1 — a tree stands 1.0 m from `beauty_overview`'s eye (**carried, not mine**)

`PARAMS["planters"][0] = (-8.0, -5.0)`; the `beauty_overview` eye is `(-7.0, -5.0, 3.0)`. Isolated
A/B prim dump on the same tree (HEAD arm vs this commit) — **byte-identical rows**:

```
/World/Scene02/Planter_0/Grass|Cube|T=(-8.0, -5.0, 0.2);S=(1.25, 1.25, 0.2)
/World/Scene02/Planter_0/Veg |Xform|T=(-8.0, -5.0, 0.4);RZ=303.14;S=(1.060,1.060,1.060)  → Elm_Sapling.usd
/World/Scene02/Planter_0/Shrub/Sh_0|Xform|T=(-7.38, -4.38, 0.587) → Rhododendron_noflower.usda
/World/Scene02/Planter_0/Shrub/Sh_1|Xform|T=(-8.62, -5.62, 0.565) → Rhododendron_noflower.usda
```

The planter is unchanged by CB-7, but **K4(b)** turned its crown into a real 1.06-scaled
`Elm_Sapling` USD and `place_shrubs` added two rhododendrons — after `260730_w2d_fix` was captured.
The result is a 2.5 × 2.5 m soil box and a sapling **1.0 m** from a judged eye, filling the lower
half of the frame with foliage. Measured cost on the HEAD arm alone: **PHOTO −57.5 mean, OCCL
32.8 % new-dark, blob 19.7 %, FRAME 81 %**.

**Not fixed here.** Re-siting a planter is not in CB-7's brief and would move a judged cut's
composition for a reason unrelated to GT-1/2/3, muddying exactly the adjudication §7.1 exists to
make clean. Handed to Lane 1 / whoever owns the next scene02 pass: the cheapest fix is
`planters[0]` → roughly `(-11.0, -6.2)`, which is 4.3 m from the eye and still on the verge.
**The same class almost certainly exists in other scenes** — any scene whose `beauty_overview` eye
sits within a few metres of a `build_planter` call now has a real tree in its lap. A one-line
census across the 33 scenes is worth a T-lane ticket.

### 8.2 Deferred, recorded, not attempted

| id | item | why deferred | who |
|---|---|---|---|
| **R02-2** | G2's centre-bay escalator → *"decline it, build three stair bays instead"* | intake (g) **recommends**; §7's eight rulings never adjudicated it, and CB-7's brief does not carry it. Three bays would also re-open the mid-rail question the v8 deletion just closed | supervisor |
| **R02-3** | tactile at the stair head | §12 do-not-touch **6** says *"Do not switch tactile ON"*, R16-2 put the whole tactile question under **EXECUTION HELD** until the scene-renumbering round, and CB-7's brief does not list it. `cue_tactile` stays `False`; the `stair_top` registry site is already wired and fires the moment the toggle flips | supervisor, at renumbering |
| **GT-1 ramp** | 1:12 accessibility ramp on one side of the apron | undeclared GT geometry (§2.3) | needs its own ledger row |
| **PLACEMENT** | scene02 declares no `PLACEMENT` block, so LINT-1/2/3/4 degrade to `nodata` | it needs the `kerb_lines` datum — which **this commit now creates**. First scene in the library that can actually declare one | Lane 1, next pass |
| **LINT-6 / LINT-9** | 4 bollard ERRORs + the blocked M1–M6 setback gate | pre-existing and **byte-identical** pre/post (§9) | T1 / P-7 |
| **C02-P1** | §8.1 | above | Lane 1 |

### 8.3 Corrections this window found in the LAW documents

| document | claim | correction |
|---|---|---|
| `w3_execution_spec_v1.md` §1.5 | *"Linear grating at `x = −1.30` … or the sill reads arbitrary"* | Contradicted by this scene's own **measured** B7 finding (`w2d_edit_g1.md` §3). Not built; the apron sheds to the existing gullies. §2.3 |
| `w3_execution_spec_v1.md` §1.5 | *"scene02's curb top currently stands 100 mm above the footway … the scene's own docstring at `:860-861` says so"* | The docstring line is right, but the fix is **not** achievable by moving the kerb alone: the carriageway datum has to drop to −0.130 or the two halves of GT-2 cannot both hold. §3 |
| `w3_intake_v2_images.md` §2 scene02 (d) | *"the parapet gets tile cladding + granite coping"* | Executed as cladding on the wall faces. It cannot mean "raise the parapet to G2's chest height" without deleting the perimeter guard on a 3.38 m drop — flagged as **S02-Q2**, not assumed. §5 |
| `gt_changes_w3.md` §3 GT-1 | *"Full re-cache (R-1+R-2+R-3) — carries GT-2 and GT-3"* | Honoured in full: R-2 was run (§9), which no other W3 scene row except GT-14 has actually done |

### 8.4 Crops vs G2 — `Docs/reports/_w3_cb7_crops/`

| file | what it shows |
|---|---|
| `G2_matched_crop.png` | the reference: full-width canopy over the whole opening, soffit battens in two rows, tiled flanks under a stone coping, dense block both sides |
| `cb7_approach.png` | the same read at eye level: enclosure to the end of the approach, sill apron, handrails converging into the pit, RF-1 plates legible |
| `cb7_pit_edge.png` | tile cladding + coping inside the mouth, soffit battens overhead, the descent reading dark against the lit approach |
| `cb7_preset_h1.8_d10.png` | the whole archetype in one frame — canopy, sill, BS-4 wall on both verges |
| `cb7_preset_h0.3_{d2,d5,d10}_pre_over_new.png` | pre over new, bottom 65 % of the frame: the h0.3 read |
| `cb7_graze_band_h0.3_d5_{pre,new}.png` | §7.3's adjudication band |
| `cb7_r1_glazing_rejected_beauty.png` | §4.2's rejected arm, kept as evidence |

Read against G2, the archetype now matches on its four structural facts: a canopy that **runs the
full length of the approach**, a **raised, granite-topped entrance sill**, **tiled flanking walls
under a stone coping**, and a **continuous block frontage on both sides**. What G2 has and 02 still
does not: shopfront glazing and signage at grade (the backdrop tier emits none, by design), the
centre-bay escalator (declined, R02-2), and the wet overcast tone — 02 is a noon-sun scene by
identity, and the dark-zone gradient is its judging subject.

---

## 9. Verification floor (§6.1) — every item, on this commit

```
python3 -m py_compile scenes/main/scene02_underpass.py                 ✔
NEGOBS_SMOKE=1 python3 scenes/main/scene02_underpass.py                ✔  rc 0 · 48/48 assertions
python3 scripts/geom_invariance_check.py --scenes scene02              ✔  R-4 1/1 · R-6 1/1 · 545 prims · a4c3a5f9
python3 scripts/geom_invariance_check.py            (ISOLATED ARM, 33) ✔  R-4 33/33 · R-6 33/33 · R-5 0
python3 scripts/placement_lint.py --scenes scene02  (ISOLATED A/B)     ✔  findings byte-identical pre vs post
python3 scripts/const_color_audit.py                                   ✔  137 wirings · 0 violations
python3 scripts/regression_check.py  (2 pairs, §7)                     ✔  JSON x2
python3 scripts/near_ground_stats.py --gate  (h0.3 x3, 2 rounds)       ✔  §7.4
python3 scripts/stamp_round.py look_check/scene02/260731_w3_cb7 …      ✔  13 cuts · HEAD dc68e74
python3 scripts/run_data_render.py --run 260731_cb7_recache …          ✔  12 cuts · 44.8 s · r_reject 0.0
python3 scripts/check_data_run.py 260731_cb7_recache                   ✔  DATA RUN CHECK PASS
```

**The 33-scene runs were executed in ISOLATED `git archive` arms**, per the K4M/RT precedent, because
the S18 lane is landing commits on `scenes/main/scene18*` and `assets/coastal` in the shared working
tree. Arm construction: `git archive HEAD | tar -x -C <arm>` twice, `assets` symlinked back to the
real tree, and this commit's `scene02_underpass.py` copied into the "new" arm only. The lint A/B is
therefore a true single-variable comparison — the only difference between the two arms is this file.

`placement_lint` on scene02, identical in both arms: **LINT-6 4 ERROR + 2 WARN** (bollard run,
pre-existing), **LINT-9 1 BLOCKED** (P-7 parked), **LINT-1/2/3/4/5/7 + PLACEMENT 7 WARN**, all
`nodata`/`gated`/`inferred`. Nothing this commit did moved a lint verdict in either direction.

---

## 10. Commits

| commit | pathspec |
|---|---|
| **`6edce66`** | `scenes/main/scene02_underpass.py` · `Docs/reports/w3_cb7_v1.md` · `Docs/reports/regr_260731_w3_cb7{,_pre}.json` · `Docs/reports/_w3_cb7_crops/` — the **one** CB-7 commit that items (1)–(5) of the brief land in |
| **`b7abe89`** | `Docs/audit_v4/gt_changes_w3.md` — the GT-1/2/3 landing records, split off because §4 records the commit hash and because that file is shared with the ledger owner (the `dc68e74` precedent does the same) |

Neither commit touches `scenes/main/scene18*` or `assets/coastal` (`git diff --name-only
dc68e74..HEAD` over those globs returns nothing), nor any kit, nor any other scene.

---

## 11. GT ledger — what this workflow wrote

`Docs/audit_v4/gt_changes_w3.md` §3 status `OPEN → LANDED` on **GT-1, GT-2, GT-3 only**, and §4
landing records filled with the commands actually run and their results. No other row, section or
figure in that file was touched, and no text was deleted — the file's own §0-3 rule
(*"record the command, do not guess it"*) and the GT-6 annotate-in-place precedent both apply.
