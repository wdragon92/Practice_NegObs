# S3 — scene07 / scene10 archetype rebuild spec v1

> **Wave**: W3 · **Track**: S3 (`Docs/briefs/w3_execution_spec_v1.md` §4.3) · **Kind**: design spec, **no code**
> **Date**: 2026-07-30 · **Branch**: `feat/realism-v1` · **Repo**: `/home/vislab/Desktop/work_sy/Practice_NegObs`
> **Releases**: execution-spec §9 parked rows **P-1 (scene07 archetype)** and **P-2 (scene10 archetype)**.
> Their release gate — *"user reference images"* `[ruled 07-30]` §1.7 — **has fired**. This document is
> the artefact the gate was waiting for. It does **not** amend the execution spec; it fills the two
> holes the execution spec left open, and every ruling in §1 / §12 of that spec still governs.
>
> **Files written by this task**: this file only. No scene file, no shared module, no ledger.
>
> **Evidence tags** — `[ref]` read off one of the two user-supplied target images (§0.1) ·
> `[measured]` recomputed this session from the authoring code (analytic; `pxr` is **not installed
> here**, so nothing below is measured off a built stage) · `[cite]` quoted from an in-repo document ·
> `[law]` statute / standard text · `[photo]` a harvested reference photograph ·
> `[assumed]` stated inference with the reasoning attached.

---

## 0. What changed, and what this document is for

### 0.1 The fidelity target is now two images, not a photo panel

The user rejected the harvested reference set and supplied two generated target images. **These two
images are the fidelity target.** Verbatim instruction: *"reference Scene07, Scene10 generated Image
and make similar. Dont create person in image."*

| ID | Path | Subject |
|---|---|---|
| **G7** | `Docs/reference_photos/Generated Image - Scene07.jpg` (1408 × 768) | Korean temple approach — irregular natural-stone slab stair, heavy moss, boulder kerb, fern understory, full summer canopy tunnel, temple tile-roof cluster at the crest |
| **G10** | `Docs/reference_photos/Generated Image - Scene10.jpg` (1408 × 768) | Korean mountain-park timber deck switchback — preservative-treated softwood, square-section railings with capped newels, deep turn landings, one lattice infill bay, leaf-off canopy, continuous brown litter |

Both images contain a human figure (G7: a monk mid-flight; G10: none). **Composition reference only.**
`w3_execution_spec_v1.md` §12-10 — *no people, no vehicles* — is unchanged and unchangeable by a
reference image. Nothing in §1.A / §2.A below places a figure.

The harvested panels (`Docs/reference_photos/w3/temple_precinct/`, 12 files, Buseoksa-heavy;
`Docs/reference_photos/w3/park_trail/`, **3 files**) remain usable as **secondary corroboration
only**, and the park_trail panel is still the n ≥ 8 evidence gap that
`w3_intake_06_10.md` §9.2 recorded. G10 does not close that gap for GATE-3 purposes — it closes it
for *design* purposes. §8-OQ4 asks the supervisor to say which.

### 0.2 The single most consequential framing fact

**G7 is the reverse of scene07's judged direction.** scene07's travel axis is **+X descending**
(`scene07:127`), the temple sits at −X (`hall.cx = −18.0`, `gate.cx = −5.6`), and **all 9 preset grid
cuts look +X, away from the temple** (`sc.grid_views(0.0)` = h{0.3,0.9,1.8} × d{2,5,10} at pitch −10°,
`scene_common.py:3265`, called at `scene07:631`). G7 looks **up the stair toward the temple** — i.e. it
corresponds to our existing `gate_frame` cut (`scene07:644`), which is 1 of 14 cuts and **not** one of
the 5 preset cuts in the current baseline round `260731_w3_cb2`.

Consequence, and it governs the whole budget: **the archetype must be carried by the stair surface,
the moss, the kerb boulders, the fern margins and the canopy — all of which are in every grid cut —
and not by the roof cluster, which is only ever in `gate_frame`.** A rebuild that spends its effort
on the temple backdrop will not move a single judged frame. §4.1 allocates accordingly.

scene10 has no equivalent inversion: G10's oblique-from-above read matches the scene's `reversal`
and `from_below` cuts, and the deck itself is in every grid cut.

### 0.3 Hard constraints carried into every section (full statement in §7)

1. **No humans, no vehicles** — in either scene, in any cut. `[ruled]` §12-10.
2. **No nosing strip on scene07.** RF-5 is already law: *"stone & natural 07·03·04·09 → absent"*,
   licensed by 편의증진법 시행규칙 별표1 제8호 마.(2) `[cite]` §10.7 RF-5. `cue_nosing=False`
   (`scene07:152`) stays False and the `build_nosing` path is never called from 07.
   **Now independently confirmed at source** `[law]`: 산림청 「등산로 정비 매뉴얼」 특별시방서 13-2 나
   (p.165) makes the anti-slip measure for a 자연석 계단 *the stone itself* —
   *"**거친 면을 발판으로 미끄러짐을 방지**한다"*. The rough face **is** the treatment.
3. **Tactile stays default-OFF** in both scenes (`cue_tactile=False`, `scene07:149` / `scene10:173`).
   §12-6: *do not switch tactile ON*.
4. **Do not undo CB-2.** Commit `11d1e56` replaced the rectangle stacks with `build_carpet_mask`
   lobes: scene07 **9 lobes + 128 feather cards**, scene10 **12 → 4 lobes**. Both survive every
   proposal below; where a lobe moves, it moves as a *coordinate* change, never back to a rectangle.
5. **NEW-SCENE design stays banned.** 07 and 10 are **rebuilt in place**. No scene is added, no scene
   is split, no scene id is reused.
6. **Total drop is frozen** in both scenes: 07 keeps `STAIR_DROP = 4.2` / `SIDE_DROP = 1.8`
   (`scene07:160-161`); 10 keeps **6.60 m** (`w3_execution_spec_v1.md` §9 P-2, verbatim). Every
   number below is derived *inside* those two constants.
7. **scene10's `rail.broken_landing = 0` survives the rebuild** (§9 P-2, verbatim) — the missing
   railing bay at landing 0 is this scene's negative-obstacle cue.

### 0.4 Reading map

The brief asked for A–G per scene. A (archetype) and B (gap table) are genuinely scene-local and sit
inside §1 (scene07) and §2 (scene10). C–G are cross-cutting — one asset manifest, one GT protocol,
one execution window — so they are single sections with a **`07 ·` / `10 ·` subsection each**:

| Brief item | Where | Per-scene split |
|---|---|---|
| **A** archetype target | §1.A · §2.A | — |
| **B** gap table incl. season audit | §1.B · §2.B | — |
| **C** asset-first mapping | **§3** | §3.2 (07) · §3.3 (10) |
| **D** buildable numbers | **§4** | §4.1 (07) · §4.2 (10) |
| **E** GT impact + draft ledger rows | **§5** | §5.2 (07) · §5.3 (10) |
| **F** WINDOW 3 execution plan | **§6** | commit sequence covers both |
| **G** hard constraints | **§7** | applies to both |

---

# 1. scene07 — Korean temple natural-stone slab stair

`scenes/main/scene07_temple_stone_path.py` (1542 lines) · `/World/Scene07` · owner **S3**

## 1.A Archetype target, read off G7

### 1.A.1 What the archetype is

G7 settles the three-way candidate question that `w3_intake_06_10.md` §4 left open
(C1 장대석 / C2 자연석 / C3 hybrid) **in favour of C2, 자연석 계단 (bedded natural stone)** — and
sharpens it well past the intake's description. It is **not** 장대석: there is not one dressed bar
anywhere in the frame, no 소맷돌 cheek stone, no 지대석 bottom course, no hairline joint. It is also
not the intake's "2–4 chunky split blocks": the slabs are **wide, flat and thin-ish**, laid like
paving flags rather than stacked like rubble.

**The defining seven, all `[ref]`:**

1. **Each step is a course of 2–4 large irregular slabs laid side by side across the flight**, packed
   tight. The joints between slabs within a course are **hairline to ~60 mm**, filled with soil and
   moss — never open slope.
2. **Wide flat slabs, deep treads, low rises.** Tread depth clearly exceeds a stepping-stone's: the
   walked surface of one course is roughly 1.5–2× the height of its own riser face, and several
   courses read as near-flat landings a foot and a half deep.
3. **The nosing line of a course is broken, not straight** — each slab's front edge stands 50–120 mm
   forward or back of its neighbour's, so the course reads as one rising surface with a ragged front,
   which is exactly the negative-obstacle cue the scene needs and is the *real* cue.
4. **Every slab is bedded.** Nothing overhangs open air; the course below carries the course above.
   There is no visible cantilever and no shadow-void under a nosing.
5. **Moss is zoned, not uniform.** Riser faces and the outer thirds of the flight are heavily
   green-crusted; the walked centre band is pale grey with white lichen and no moss at all. The moss
   fraction is a function of distance from the walk centreline and of face orientation
   (vertical/north faces mossy, horizontal walked faces clean).
6. **A discontinuous kerb of rough boulders flanks both edges** — chunkier, rounder and *taller* than
   the tread slabs, standing 0.15–0.35 m proud of the adjacent tread, mossy on top, spaced with gaps
   rather than laid as a continuous edge. They are a retaining/edging device, not a handrail.
7. **Continuous deciduous canopy tunnel with dappled light.** The stair is lit in patches; the
   background is a bright haze of backlit leaves, not a black wall.

### 1.A.2 Element inventory with frame positions

Frame coordinates are normalised `(u, v)` on G7, origin top-left, `u` → right, `v` → down.

| # | Element | Frame band | Read | Our scene equivalent |
|---|---|---|---|---|
| E7-1 | Stone stair, foreground courses | `u 0.22–0.80`, `v 0.55–1.00` | 2–4 slabs per course, ragged nosing, moss on risers | `Stone_*` 24 discrete pavers (`scene07:1124-1133`) |
| E7-2 | Stone stair, mid + crest courses | `u 0.36–0.62`, `v 0.33–0.58` | narrows with height, ~25–30 courses total in frame | same |
| E7-3 | Kerb boulders, left run | `u 0.18–0.32`, `v 0.36–0.92` | discontinuous, 0.4–0.9 m, proud of the tread line | **absent** |
| E7-4 | Kerb boulders, right run | `u 0.62–0.82`, `v 0.36–0.90` | same, denser | **absent** |
| E7-5 | Fern / understory band, left | `u 0.02–0.28`, `v 0.42–0.68` | ferns at the tree feet, waist-high, green | `shrubs` blobs (`scene07:294-296`) |
| E7-6 | Understory bank, right | `u 0.72–1.00`, `v 0.28–0.85` | dense shrub + fern bank rising away from the stair | same |
| E7-7 | Large tree trunks, near | `u 0.00–0.30` and `u 0.72–0.92`, full height | 0.6–1.2 m Ø, moss/lichen on bark, frame the shot | `pines` (`scene07:286-289`), `trunk_r = 0.11` |
| E7-8 | Canopy tunnel | `v 0.00–0.30` across, plus both margins | full summer leaf, backlit, dappled floor | `canopy_a/b` blobs or veg assets |
| E7-9 | Temple roof cluster | `u 0.33–0.78`, `v 0.15–0.42` | **3–4 roofs** at staggered depth; nearest is a 팔작 hip-and-gable with strongly upturned eaves, visible rafter-end dentil row, dark grey 기와, white gable render; a red-painted wall fragment below-left; a further roof higher right | `hall` (1 gable silhouette, `scene07:281-284`) + `gate` (`scene07:263-266`) |
| E7-10 | Wooden pole | `u ≈ 0.155`, `v 0.10–0.62` | one slender dark timber pole, ~0.15 m Ø, left of the stair, no crossarm → lamp/service pole | **absent** |
| E7-11 | Leaf litter | thin margins only, `u 0.05–0.22 / 0.80–0.98`, `v 0.55–0.85` | brown litter accumulates **at the margins and in joints**, never as a carpet on the walked surface | **9 lobes, dominant ground story** (`scene07:236-238, 251-252`) |
| E7-12 | (excluded) human figure | `u 0.55–0.58`, `v 0.33–0.47` | monk, ascending | **must not be built** |

### 1.A.3 Season identity — pinned

**scene07 = lush summer (성하).** Pinned, single season, no exceptions. The whole frame is one
season: full green canopy, green fern understory, green moss, and litter present only as a thin
margin accumulation. `[ref]`

This pin is the operative half of the section, because **scene07 is currently built as two seasons at
once** — see §1.B-S.

---

## 1.B Gap table — current code vs G7

`file:line` refs are to the tree at `66aba5a` (post-CB-2). Every "current" value is `[measured]`
(recomputed from the authoring code this session), not read off a stage.

### 1.B-1 The stair itself — the archetype failure

| # | Element | Current (file:line) | Current value `[measured]` | G7 target `[ref]` | Verdict |
|---|---|---|---|---|---|
| **A1** | Step primitive | `scene07:1129` `sc._oriented_box` per stone | **1 rectangular box per step**, 24 total | **2–4 slabs across the width per course** | **REBUILD** |
| **A2** | Inter-step gap | `scene07:166` `gap=(0.05,0.30)` → `:509` | min **0.050** / max **0.276** / mean **0.177 m**; **the gaps consume 4.08 m of a 11.99 m run = 34.0 % of the flight is bare slope** | joints **0.00–0.06 m**, soil/moss filled; **0 % open slope** | **ABOLISH** |
| **A3** | Course count / rise | `scene07:165` `n=24`; `:507` | 24 steps, rise min **0.111** / max **0.232** / mean **0.174 m**, spread **0.121** | 26–30 courses; rise band **0.12–0.20**, mean ≈ 0.155 | **RE-TABLE** |
| **A4** | Tread depth | `:166` `depth=(0.28,0.40)`, scaled ×0.9613 at `:500` | **0.270–0.384 m**, mean 0.325 | **0.36–0.55 m**, mean ≈ 0.44 (deep treads are the archetype's signature) | **WIDEN** |
| **A5** | Slab width across flight | `:166` `w=(0.50,1.10)` | 0.510–1.036 m, mean 0.755 — **one slab spans the whole "flight"** | per-slab 0.55–1.30 m, **2–4 per course**, course total = corridor width | **REBUILD** |
| **A6** | Lateral offset | `:505` `cy` | −0.247 … +0.130 m per stone | **0** — a course spans the corridor; the ragged edge comes from slab ends, not from sliding the step sideways | **ABOLISH** (`w3_intake_06_10.md` §1.0 already ruled this an archetype error, not a jitter question) |
| **A7** | Per-step yaw / tilt | `:168` `rz=4.0, rx=2.5`, applied `:1133` | yaw ±4.0°, tilt ±2.5° | keep a **capped ±3.0° per-slab yaw** (adopted J-14 ruling, `[cite]` §1.2) + bedding tilt; **no course-level yaw** | **CAP, do not abolish** |
| **A8** | Canted knob | `scene07:174-179`, built `:1135-1140` | **24 extra prims**, yaw ±10–20°, tilt ±3–9°, hung 50–80 mm under the stone top | **nothing like it exists** — the archetype has no subsidiary lump | **DELETE** (§9 P-1: *"the knob dies with whichever archetype wins"*) |
| **A9** | Bedding / float | thickness `pr + em`, **0.129–0.240 m**, embed 0.10–0.18 `:507` | stones are individually seated on the corridor plane, and with a 34 % gap fraction several read as cantilevered over shadow `[cite]` `w3_intake_06_10.md` §4 | **solid to a base plane**; the course below carries the course above; zero visible void under a nosing | **REBUILD** |
| **A10** | Edge condition | none | no kerb, no cheek stone, no handrail | **discontinuous boulder kerb both sides** (E7-3/E7-4) | **ADD** |
| **A11** | Entry / exit steps | `:581-582` | entry **+0.002 m** (yard → stone 1), exit **+0.201 m** (last stone → approach) | entry ≈ one rise; exit ≈ one rise, not a 201 mm orphan lip | **RE-TABLE with A3** |
| **A12** | Nosing strip | `scene07:152` `cue_nosing=False` | absent | absent | **CORRECT — do not touch** (§4-2) |

> **A2 is the headline.** 34.0 % of scene07's stair is not stair. Whatever else is done, the run has
> to be re-budgeted so that the *stone* consumes the run and the joints consume ≤ 4 %.

### 1.B-2 Margins, dressing, backdrop

| # | Element | Current (file:line) | Current value | G7 target | Verdict |
|---|---|---|---|---|---|
| **B1** | Kerb boulders | — | absent | 0.4–0.9 m boulders, both edges, discontinuous | **ADD** (E7-3/4) |
| **B2** | Fern / understory | `scene07:294-296` `shrubs`, 8 clumps of 3 ellipsoid blobs (`:297-300`) | generic blob shrubs, 3 of 8 on the north bank | **fern band at the tree feet on both margins**, dense, waist-high | **REPLACE + DENSIFY** |
| **B3** | Near tree trunks | `scene07:286-290` `pines`, 8 trees, `trunk_r = 0.11` (Ø220 mm) | 8 slender trunks | 0.6–1.2 m Ø old-growth trunks framing the shot at both margins | **UP-SCALE the two framing trees**; keep the rest |
| **B4** | Species | `scene_common.py:2443-2444` coordinate-hash draw from a 5-species pool | **every tree draws independently**; prims literally named `Pine_*` (`scene07:697`) can render as elm/oak | one species for the courtyard group; `[cite]` §10.2 assigns **Chinese_Juniper** to 07's courtyard | **consumes K4(b) `species=` kwarg** — S3 writes the `veg=` PARAMS row only |
| **B5** | Roof backdrop | `scene07:281-284` `hall` (1 podium + 5 posts + 1 gable) + `:263-266` `gate` | **2 roofs total**, both flat-gable `build_slope` pairs, no upturned eave, no rafter row | **3–4 roofs at staggered depth**, upturned eaves, ridge/hip lines, one red-wall fragment | **EXPAND** — but see §0.2: only visible in `gate_frame` |
| **B6** | Wooden pole | — | absent | 1 pole, ~0.15 m Ø, left of the stair, mid-slope | **ADD** (1 prim; cheap, and it is in `gate_frame`) |
| **B7** | Ridge backdrop | `scene07:310-327` 7 ridge boxes + `:330-331` 5 crest hedges | a 3-tier staggered ridge system built to cure a *black wall* defect | **G7 has no distant ridge at all** — the canopy closes the frame | **KEEP as-is.** The ridge is only in the +X cuts, where G7 says nothing. Do not delete a working horizon fix on the strength of a photo that faces the other way |

### 1.B-S Season audit — every element against the summer pin

**Finding: scene07 is currently a summer canopy over an autumn floor.** `[measured]`

| Element | file:line | Season it reads | Against the summer pin |
|---|---|---|---|
| `PathCorridor` slope material | `scene07:227` `"leaf"` → `M["leaf"]` = `tex("leaf_ground", …)` `:1013` | **autumn** — `scene_common.py:121-123` names the role *"Fallen-leaf ground (C2)"* | **CONFLICT** — the ground between the stones is a brown fallen-leaf texture |
| `SouthTerraceA/B/C`, `Approach` | `:217-219`, `:228` `"leaf"` | **autumn** | **CONFLICT** — the entire lower terrace, i.e. the whole south drop that is the scene's positive GT face, is autumn litter |
| 6 corridor leaf lobes | `:236-238` + `:1156-1167` | **autumn** | **PARTIAL** — margin accumulation is correct in summer; a carpet over the walked surface is not |
| 3 yard leaf lobes | `:251-252` + `:1168-1178` | **autumn** | **PARTIAL** — same |
| 128 feather leaf cards | `:1191-1201`, pool `sct_debris_leaves_dry_*` / `VEG_DEBRIS` | **autumn** (dry brown leaf assets) | **PARTIAL** — allowed as a scene-identity exception (`ground_kit.py:46`), but the *quantity* is an autumn quantity |
| Canopy albedo | `:360` `canopy_a/b` dark green | **summer** | OK |
| Grass | `:357` `grass_tint (0.55,0.68,0.42)` | **summer** | OK |
| Moss tint | `:172` `tint_moss (0.74,0.84,0.70)`, applied to **1 stone in 3** (`moss_every=3`) | **summer** | OK in kind, wrong in distribution (§4.1-3) |
| Tree species pool | `scene_common.py:2118-2125` | summer-green; `Japanese_Cherry` **deleted** for exactly this class of error (`scene_common.py:2101`) | OK — **and this is the precedent** |

**The cherry-blossom precedent applies in reverse here.** `Japanese_Cherry` was deleted because its
texture is 0.0 % green pixels — a spring asset leaking into all-season scenes `[cite]`
`scene_common.py:2098-2101`. scene07 is doing the same thing with `leaf_ground`: an **autumn** ground
texture bound to five plates and two slopes in a scene whose canopy, grass and moss are all summer.
The fix is symmetric with the cherry ruling: **judge by pixels, not by the role's name**, and
re-bind the corridor and terrace surfaces to a summer ground (moist forest soil + moss + fern litter),
keeping `leaf_ground` **only** for the margin lobes where G7 actually shows brown litter.

**Ruling requested** (§8-OQ1): re-binding `PathCorridor` / `SouthTerrace*` / `Approach` off
`leaf_ground` needs either an existing summer ground role or a procured texture. §3.2 answers with
the asset route.

---

# 2. scene10 — Korean mountain-park timber deck switchback

`scenes/main/scene10_park_deck_switchback.py` (1497 lines) · `/World/Scene10` · owner **S3**

## 2.A Archetype target, read off G10

### 2.A.1 What the archetype is

G10 confirms the intake's diagnosis (*"reads as an apartment emergency stair"*, `w3_intake_06_10.md`
§7) and **partly overturns its proposed cure**. Intake candidate **D1** proposed *"galvanised steel
posts + C-channel stringers + timber tread"* on the hypothesis that real Korean deck stairs of this
height are hot-dip-galvanised framed. **G10 refutes that as the visible archetype**: everything the
walker sees — newels, rails, balusters, stringers, treads, landings — is **timber**. Metal appears
only as concealed support under a flight (one grey column is visible in shadow under the upper
flight, `u ≈ 0.79`, `v ≈ 0.20`) and it is *not* part of the read. **D1's galvanised-frame clause is
withdrawn**; D1's riser/tread/width/rest-platform clauses survive and are sharpened below.

**The defining eight, all `[ref]`:**

1. **Every member is square or rectangular sawn timber.** Not one round member in the frame. Our
   scene10 builds posts, balusters and rails as **cylinders** (`CYL`, `scene10:1218`, `:1247`) — this
   single fact is the largest contributor to the fire-escape read, because a run of thin round
   verticals between two thin round horizontals *is* the silhouette of steel balustrade.
2. **Chunky capped newel posts.** At every landing corner and every flight head/foot there is a stout
   square post carrying a distinct oversized **cap block** with a weathered, slightly chamfered top.
   The newel projects clearly above the top rail.
3. **A three-rail bay**: wide flat **top rail** (laid flat, wider than thick — a hand can rest on it),
   a **mid rail**, and in most bays a **bottom rail**, with square balusters spanning between them.
4. **Dense baluster pitch.** Roughly 7 balusters per ~1.1 m bay ⇒ **≈ 150 mm** on centre, clear gap
   ≈ 110 mm. Our current 300 mm pitch of Ø44 rods is half the density and the wrong section.
5. **One lattice / grid infill bay.** Upper right (`u 0.60–0.70`, `v 0.03–0.18` on the full frame): a
   whole bay is filled with a fine square lattice instead of balusters. It is a real and common
   Korean 데크 난간 variant and it is the single cheapest "this is a park, not an egress stair" tell.
6. **Deep turn landings with a genuine change of direction.** The landings are large enough to stand
   two people on and the railing turns a hard 90° corner around a newel. They are not the minimum
   turn plate our 1.40 × 2.80 m slab is.
7. **The run travels across the slope.** Successive flights step *sideways* as well as down; daylight,
   leaf litter and tree trunks show between and under them. Nothing is stacked directly above
   anything else.
8. **Uniform weathered grey-brown patina.** Silvered top faces, darker vertical faces, greenish algae
   in the shaded feet and north faces. Desaturated. Our `wood_color = (0.30, 0.20, 0.12)`
   (`scene10:384`) is a saturated dark red-brown that reads near-black in shadow.

### 2.A.2 Element inventory with frame positions

Normalised `(u, v)` on G10, origin top-left.

| # | Element | Frame band | Read | Our scene equivalent |
|---|---|---|---|---|
| E10-1 | Foreground landing / platform | `u 0.10–0.55`, `v 0.72–1.00` | plank deck, planks parallel to the departing flight, railing turning a corner around a newel | `Landing_k` 1.40 × 2.80 slab (`scene10:1240-1243`) |
| E10-2 | Flight A (bottom, ascending away) | `u 0.30–0.52`, `v 0.55–0.85` | ~5 risers, closed riser faces, 2 planks per tread | `Flight` via `build_open_riser_stairs` (`scene10:1233`) |
| E10-3 | Mid landing + Flight B | `u 0.42–0.62`, `v 0.28–0.58` | ~9 risers | same |
| E10-4 | Upper landing + Flight C, turning right | `u 0.55–0.80`, `v 0.10–0.35` | ~6 risers, **flight offset laterally** — not stacked | **absent** (ours stacks) |
| E10-5 | Top flight | `u 0.72–0.98`, `v 0.00–0.20` | disappears into the trees | — |
| E10-6 | Newel posts (capped) | `u 0.16 / 0.50 / 0.68 / 0.78`, various `v` | square section ~90–100 mm, cap ~120 × 120 × 45, projects 120–200 mm above the rail | `Post_*` cylinders r 0.075 (`scene10:1247`) — **no cap, round** |
| E10-7 | Baluster bays | everywhere | square ~40 × 40 at ≈150 mm pitch | `Bal_*` cylinders r 0.022 at 300 mm (`scene10:1215-1218`) |
| E10-8 | **Lattice infill bay** | `u 0.60–0.70`, `v 0.03–0.18` | square grid panel filling a whole bay | **absent** |
| E10-9 | Under-flight structure | `u 0.55–0.72`, `v 0.15–0.30` | raking stringer + tread soffit + a concealed grey column + a stack of cut logs | `Stringer_*` sloped boxes (`scene_common.py:1976-1981`) |
| E10-10 | Rock outcrop | `u 0.88–1.00`, `v 0.00–0.25` | bedrock breaking the litter slope on the uphill side | **absent** |
| E10-11 | Leaf litter | `u 0.55–1.00`, `v 0.20–1.00` and the left slope | **continuous** brown litter over the whole slope, not patches | 4 lobes (`scene10:290-293`) on **green grass plates** |
| E10-12 | Bare trees | `u 0.00–0.55`, all `v` | slender leafless deciduous trunks + fine twig structure, no canopy mass | 12 `trees` + 12 `hill_trees` with **green** `canopy_a/b` (`scene10:382-383`) or green veg assets |
| E10-13 | Faint city / sky glimpse | `u 0.00–0.10`, `v 0.25–0.45` | pale sky and one indistinct pale mass through the trunks | `FarRidge` grass box (`scene10:253`) |
| E10-14 | Wire / cable | `u 0.60–0.85`, `v 0.05–0.30` | a thin slack cable across the frame | **out of scope** — do not build |

### 2.A.3 Season identity — pinned, with a correction to the brief

**Read of G10** `[ref]`: leafless deciduous canopy **plus** overwintered matted brown litter **plus**
a first flush of small green leaves at the crowns (`u 0.20–0.45`, `v 0.00–0.12`) and green ground
shoots in the lower crop. Those last two are **early-spring** signals. G10 is therefore an
**early-spring (4월) frame**, not a late-autumn one.

**Pin: late autumn (만추), leaf-off.** Reason, and it is the cherry-blossom precedent applied
prospectively: adopting "early spring" would import the green flush — a *seasonal event* element —
into a library whose §12-7 rule is *"no seasonal or event-specific element in any prop"* and whose
only sanctioned seasonal exceptions are `04/07 browned leaves, C1 snow, C2 leaves`
(`ground_kit.py:46`). Late autumn is visually identical to G10 in every element we will actually
build (bare canopy, continuous brown litter, dormant ground) and it is **already the sanctioned
exception** for this scene. The two spring-only elements are therefore **explicitly excluded**:

> **EXCLUDED from scene10 by the season pin**: green leaf flush on any tree; green ground shoots;
> any flowering shrub. `Shrub/Forsythia` and `Shrub/Rhododendron` are already banned or
> flower-disabled for exactly this reason (`scene_common.py:2280-2288`).

### 2.A.4 Season audit — every element against the late-autumn pin

**Finding: scene10 is currently a summer-green scene wearing autumn leaf decals** — the mirror image
of scene07's defect. `[measured]`

| Element | file:line | Season it reads | Against the late-autumn pin |
|---|---|---|---|
| 12 trail/park trees | `scene10:297-302` → `sc.build_tree` | **summer** (green veg asset, or green blob canopy `canopy_a/b` `:382-383`) | **CONFLICT** — the ref's defining element is leaflessness |
| 12 hill / ridge trees | `:353-364` | **summer** | **CONFLICT** |
| 4 far hedges + 4 crest bands | `:341-351` | **summer** green mass | **CONFLICT** (softer — distance) |
| 13 shrub clumps | `:307-316`, blobs `:317-320` | **summer** green | **CONFLICT** |
| 3 berm hedge strips | `:276-277` | **summer** | **CONFLICT** |
| Grass plates (7 of 11 plates + 2 ybanks) | `:242, 248-253, 259-262`, tint `(0.55,0.68,0.42)` `:375` | **summer lawn** — `grass` role is ambientCG Grass001, *"green 98.25 %"* (`scene_common.py:64`) | **CONFLICT** — a late-autumn Korean park slope is straw/olive, not lawn green |
| 4 ground leaf lobes | `:290-293` | autumn | **OK, but far too little** — the ref is *continuous* litter |
| 2 tread leaf bands | `:279-282`, built `:1272-1281` | autumn | OK — this is the GT cue, keep |
| Deck timber tone | `:373-374, 384` | season-neutral, but **wrong value** (§2.B) | see B7 |

The honest summary `[measured]`: **scene10 currently contains 37 individual green plants**
(12 trail/park trees + 12 hill/ridge trees + 13 shrub clumps) **plus 10 green hedge/crest bands**
(3 berm + 3 far + 4 crest) = **47 green vegetation objects, against 4 brown leaf lobes.**
The reference contains zero green vegetation objects and wall-to-wall litter. This is the single
largest *quantitative* gap in either scene, and unlike the geometry it cannot be closed by
arithmetic — it needs either leafless tree assets or a leafless procedural path (§3.4, §8-OQ3).

---

## 2.B Gap table — current code vs G10

### 2.B-1 The stair and its railing

| # | Element | Current (file:line) | Current value `[measured]` | G10 target `[ref]` | Verdict |
|---|---|---|---|---|---|
| **C1** | Flight arrangement | `scene10:448-470` `compute_flights()` + `:477-481` `band()` | 4 flights alternating between two 1.38 m Y bands 20 mm apart, reversing in X ⇒ **flight 1 sits directly above flight 3, flight 2 above flight 4**, whole stair inside a **3.0 × 2.8 m plan**, vertical clearance 3.01 m | flights **step sideways as they descend**; nothing stacked; daylight and litter visible between them | **REBUILD — this is the emergency-stair silhouette** |
| **C2** | Riser / tread | `:187` `riser=0.165, tread=0.30` | 2R+T = **0.630**, pitch **28.8°** | **`[law]` 0.630 is LEGAL** — inside KCS 34 50 10 3.2.8(3)'s 600–650 window and inside KFS's 600–700 (§4.0 F-1). The intake's *"an interior ratio"* claim is **refuted** | **RE-TABLE for fidelity, not for compliance** (§4.2-1) — a shallower 0.150 / 0.310 reads more outdoor, but this row is **not** the reason the scene fails |
| **C3** | Flight width | `:187` `half_w=0.69` | **1.38 m** | **1.50 m** — `[law]` the statutory cap on forest-land trails (SANJI-183) and `[data]` the mode of 155 real 데크 stair records (47.7 %) | **WIDEN to 1.50, not to 1.8** (§4.0 F-2) |
| **C4** | Landing | `:190` `size=1.4`, `y0/y1 = ∓1.40`, `thick=0.12` | 1.40 (X) × 2.80 (Y) — a minimum turn plate that exists only because it must cover both bands | deep turn landings you can stand on, railing turning a 90° corner on a newel | **RESIZE** |
| **C5** | Rest platform | — | **absent**; 4 × 1.65 m of continuous descent | at least one wide 쉼터/전망 platform in a 6.6 m drop — *the* park-vs-egress signature | **ADD** |
| **C6** | Riser condition | `:1233` `sc.build_open_riser_stairs` | **open risers** (see-through), `gap=0.02` | G10 reads **closed riser boards** | **CONFLICT WITH A DECLARED CUE** — see §8-OQ2, do not resolve unilaterally |
| **C7** | Post section | `:195` `post=dict(r=0.075…)`, built `:1247` `CYL` | **round Ø150 mm** | **square ~100 mm**, capped newels | **REBUILD (round → square)** |
| **C8** | Rail members | `:199-200` `post_r=0.05, bar_t=0.06`, `sc.build_railing_line` (`scene_common.py:1686`) | round Ø100 posts, Ø60 rails, `baluster_r=0.0` (shared balusters deliberately off, `:1207`) | flat-laid rectangular top rail, rectangular mid + bottom rail | **REBUILD (round → rectangular)** |
| **C9** | Balusters | `:201` `bal_r=0.022, bal_step=0.30`, loop `:1211-1218` | **9 per flight side at exactly 300 mm**, round Ø44 | **square ≈40 × 40 at ≈150 mm** | **REBUILD (section + double the density)** |
| **C10** | Lattice infill bay | — | absent | one lattice-panel bay | **ADD** (E10-8) |
| **C11** | Rail height | `:199` `h=1.05` | 1.05 m | **1.10 m** — `[data]` KNPS-RAIL median over 1,227 built trail railings; `[law]` no building rule binds (§4.0 F-3) | **+0.05 m** — a small move, not a redesign |
| **C12** | Broken rail bay | `:200` `broken_landing=0`, applied `:1256` | landing 0 outer run has rails gone, posts remain | — | **KEEP UNCHANGED** (§9 P-2, verbatim) |
| **C13** | Plank gap | `:188` `gap=0.02` | 20 mm inset front and back per tread | — | **KEEP** — graded *excellent* in `tonglam_v2` §2.4 `[cite]` |
| **C14** | Nosing | `:177` `cue_nosing=False` | absent | RF-5 puts 2010s deck 10 in the **cast/grooves** tier, not the applied-strip tier `[cite]` §10.7 | **KEEP absent**; if anything is ever added it is a groove, never a chrome strip |

### 2.B-2 Terrain, materials, dressing

| # | Element | Current (file:line) | Current value | G10 target | Verdict |
|---|---|---|---|---|---|
| **C15** | Ground under the stair | `:241-254` plates; the stair descends inside a cut with a head wall at `x = −1.5` and a 7.40 m `BankCut` | a **shaft** between masonry walls — the docstring says so: *"A pure switchback makes no horizontal progress … the ground along the stair must therefore be effectively vertical"* (`:51-53`) | an **open litter slope** with rock, trunks and daylight around the deck | **REBUILD — the shaft is the other half of the emergency-stair read** |
| **C16** | Wall materials | `:245-247` `rock` (masonry rubble) + `:266-267` `rockface` | quarried-rubble masonry + natural cut face, two-tier east wall + coping | ref has **no built wall at all**; the only hard surface is natural outcrop | **REDUCE** (retain a short head-wall only) |
| **C17** | Rock outcrop | — | absent | bedrock at the uphill margin (E10-10) | **ADD** |
| **C18** | Deck timber tone | `:373` `deck_tint (1.00,0.96,0.90)`, `:374` `stringer_tint (0.72,0.70,0.66)` over `wood_dark` at `scale 1.0`; `:384` `wood_color (0.30,0.20,0.12)` | dark saturated red-brown; reads near-black in shadow (`pt_noon_from_below.png` `[cite]`) | weathered grey-brown, silvered top faces, desaturated | **RE-TONE** (§4.2-3) |
| **C19** | Vegetation season | `:297-364` trees/shrubs/hedges | **47** green objects (§2.A.4) | leafless | **REBUILD or PROCURE** (§3.4, §8-OQ3) |
| **C20** | Litter coverage | 4 lobes (`:290-293`) over ~13 m² of a scene tens of metres across | patchy | **continuous** over the slope | **EXPAND** — as *material* + scatter, not as 40 more lobes |
| **C21** | City glimpse | `:253` `FarRidge` grass box `x 44..78`, top z 3.50 | a green box horizon | a faint pale mass through the trunks at `u 0.00–0.10` | **ADD via `building_kit` BS-4 backdrop** (§3.3) |
| **C22** | Waymarker / bench / pergola | `:329-338` | present, extensively tuned in v6/v7 for the park read | ref has none in frame but they are correct park furniture | **KEEP** — do not delete a v7 fix on the strength of one frame |

---

# 3. Asset-first mapping *(brief item C)*

## 3.0 The doctrine, the inventory, and three corrections

**User law**: *"에셋 활용할 수 있는건 최대한 활용"* — every element is mapped to an existing procured
asset before any procedural work is proposed. Execution-spec §1.1: *"the asset route wins unless the
Korean archetype is clearly broken at h0.3."*

**Inventory as it actually is** `[measured]`, independently re-verified this session:

| Root | Count | Licence tier | On disk |
|---|---|---|---|
| `assets/urban/` (`urban_manifest_w3.json` → `assets[]`) | **258** | **T2** Omniverse Content — ML ✅ / render ✅ / **USD redistribution ❌**, gitignored | all present |
| `assets/urban_cc0/` (→ `polyhaven[]`) | **33** | **T1 CC0 / CC-BY** — redistributable | all present |
| `assets/vegetation/` (`veg_manifest_w2.json`) | **44 USD** | T2 | present |
| `assets/scene01/` (`sc.TEX` roles) | **23 PBR sets** | CC0 | present |
| `assets/urban/nv_content/common_assets/shared_textures/` | **145 files**, flat shared pool | T2 (local use) | present |

**Three corrections that change the design, all `[measured]`:**

- **C-A1 — the "~57 temple/hanok/roof-related entries" figure in the task brief is wrong.** A keyword
  sweep returns 172 hits, but **162 of them are `signs_kr` rows matching "korea" in `root_key`**. The
  real count of tile-roofed geometry in the whole catalogue is **one asset**, `typical_building_18`
  (`tile_roof_01` bound to 25.7 % of its triangles) — and it is a **generic Western low-rise**: no
  처마 curve, no 팔작 hip-gable, no rafter row. **Full temple buildings 19… no: 0. Roof-only 0. Parts
  0.** The crest backdrop therefore has **no asset route** (gap **G1**) and stays procedural.
- **C-A2 — there is no moss texture, no moss material and no moss role anywhere.** The repo's existing
  convention is *a green tint on an existing stone texture plus a `moss` token in the prim path* so
  the look layer classes it as vegetation (`scene09:1109` `moss_tint = (0.213, 0.284, 0.185)`;
  `scene_common.py:520, 567` map the path token `moss`/`GkMoss` → material class `veg`). scene07
  already owns half of this: `M["gk_moss"]` at `scene07:1055`.
- **C-A3 — `safety_railing_01` is BANNED** (one of 16 banned substrings enforced by
  `urban_kit._check_banned()`), `typical_building_08_railings` is a rooftop parapet at `zmin +11.0 m`
  that the loader **refuses to place**, and **no wooden railing asset exists**. The railing is
  procedural by necessity as well as by design.

**Loader convention to cite in code** (this is the single call form; neither scene imports urban
assets today — the only call site in the tree is `batch1_common.py:185`):

```python
import urban_kit as uk
uk.add_urban_asset(stage, prim_path, asset_id, pos_m=(x, y, z), yaw_deg=0.0,
                   target_h=None, scale_mul=1.0, tilt_deg=(rx, ry),
                   z_mode=None,        # 'grade' (default) | 'base' | 'attach'
                   scene='07',         # REQUIRED for SCENE_SCOPE'd rows
                   instanceable=True)  # reference lands on <prim_path>/Asset
```

Four loader quirks that must be honoured (§3.4 of the execution spec):
`*_inst.usd` is referenced, never the wrapper · `mpu` is per-asset · ops go on the **parent**, the
reference on the `/Asset` child · **centre-origin scans need `z_mode='base'`** — which includes every
rock scan proposed below.

## 3.1 Coverage summary

| Scene | Elements mapped | Asset-backed | Procedural-by-design | True gaps | **Coverage** |
|---|---|---|---|---|---|
| **07** | 10 | 8 | 3 (stair builder, cheek stones, pole) | **2** (G1 hanok roof, G2 fern) | **~70 %** |
| **10** | 10 | 8 | 3 (railing, grating, plank field) | **1** (G5 weathered-grey plank tone) | **~80 %** |

## 3.2 `07 ·` element → asset

| Element | Asset id / path | Licence | Verified | Fit | Placement note |
|---|---|---|---|---|---|
| **Stone slab step (upgrade path)** | `rock_03_broken` — 1.318 × 1.714 × 0.640 m, 9,832 tri, `zmin −0.006` | T2 | Y | **A** | At `scale_mul` 0.35–0.50 → **0.46–0.86 m across, 0.22–0.32 m thick**, dead on the 자연석 slab band. Yaw-rotate and reuse per slab. `instanceable=True` or the triangle bill is 70 × 9.8k |
| **Stone slab step (baseline)** | `sc.build_worn_stone_stairs` (`scene_common.py:1907`) | — | — | **A** | **This is the archetype builder and scene07 explicitly refuses to use it** (`scene07:44-46`). It already emits 2–4 lateral blocks per course with per-block `jyaw ±3°`, `jz ±0.02`, front/back `jt ±0.10` and a solid base to `base_z` — i.e. §1.A.1 items 1, 3, 4 for free. **Wire this first; `rock_03_broken` is the upgrade, not the baseline** |
| **Kerb boulders, both flanks** | `rock_moss_set_01` (8.005 × 6.949 × 1.768, 63,127 tri, `zmin −0.661`) · `rock_moss_set_02` (8.278 × 3.410 × 1.368, 57,647 tri, `zmin −0.315`) | **CC0 1.0** | Y | **A** | Pre-composed mossy boulder groups — one call fills a whole flank. **`z_mode='base'` is mandatory** (52.4 % / — of triangles sit below the origin). ⚠ `tonglam_v2` §1 row 07 already grades 07 **FAIL** for *"boulder-scale D-5 rocks in dark sink-rings"* (F2): scaling these too small or sinking them reproduces the exact defect |
| Near-field kerb stones, joint fill | `rock_01` (0.241 × 0.316 × 0.164, 3,104 tri) · `rock_02` (0.404 × 0.463 × 0.285, 4,758 tri) | T2 | Y | A | discontinuity fillers between the two big groups |
| Joint gravel / talus | `sc.VEG_ROCKS` = `Rocks/rock_small_{01,08,09,10,15}.usda`, 0.128–0.314 m wide | T2 | Y | A | via `sc.scatter_debris(pool=sc.VEG_ROCKS, sink=…)`; centre-origin, so `sink` must be small |
| **Canopy tunnel — primary** | `Trees/Shumard_Oak.usd`, zmax 10.899, 99,509 tri unique | T2 | Y | **A** | already `VEG_TREES` weight 3; `native_h` **must be zmax**, not bbox height |
| Canopy tunnel — 2nd species | `Trees/Scarlet_Oak.usd`, 10.41 × 10.26 × 12.75, **49,899 tri** | T2 | Y | **A** | **not yet in `VEG_TREES`** — free variety at half Shumard's unique triangles. Admissible under §1.3-3 only as a *declared separate belt*, not as a second species on the same group |
| Backdrop forest wall behind the crest | `Trees/Black_Oak.usd` (25.4 × 24.1 × 19.7) | T2 | Y | A | replaces part of the `ridge_crest` hedge band in `gate_frame` only |
| Courtyard evergreen group | `Trees/Chinese_Juniper.usd` (manifest role literally `temple_office_evergreen`) · `Shrub/Yew.usd` (주목 — *the* temple shrub) · `Shrub/Holly.usd` | T2 | Y | **A** | §10.2's assignment for 07's courtyard group; fixes the `Pine_*` prims currently rendering as elm/oak |
| **Understory bulk** | `veg_shrub_hedge_green_01` — 5.80 × 3.31 × 1.92, **20,894 tri**, verdict PASS | T2 | Y | **A** | cheapest bulk understory mass in the catalogue by an order of magnitude; use for the right-hand bank (E7-6) |
| **Fern stand-in** | `Shrub/Switchgrass.usd` — 2.01 × 2.03 × 1.37, **8,934 tri**, green 100 % | T2 | Y | **C** | **fern does not exist** (gap **G2**): 0 hits across all 291 manifest rows and all 44 vegetation USDs. Switchgrass has the arching-blade silhouette at 8.9k tri, which is the closest available read |
| Joint weeds at the slab joints | `Shrub/Grass_Short_C.usd` (1,598 tri) | T2 | Y | A | already the A1/GT-9 weed asset; joints are exactly the "real discontinuity" the A1 contract asks for |
| **Moss albedo** | `assets/urban_cc0/rock_moss_set_02/textures/rock_moss_set_02_diff_1k.jpg` + `_nor_gl_1k.exr` + `_rough_1k.exr` — **yellow-green 92.86 %**, albedo_lin 0.0812 | **CC0 1.0** | Y | **B** | **Register as a new `sc.TEX["moss"]` role** — zero procurement, redistributable. It is a rock-*with*-moss scan, so it tiles with rock structure: use it as a **joint / riser-base / boulder-top patch**, not as a large-area carpet. Keep the existing tint convention (§C-A2) for the large-area case |
| Summer forest-floor ground (replaces `leaf_ground` on the corridor/terraces) | `sc.TEX["dirt_park"]` darkened + the new `TEX["moss"]` in patches | CC0 | Y | B | §1.B-S: the corridor must stop being an autumn texture. `dirt_park` is already in the tree and already tuned for this scene family (`scene10:372` uses `scale 1.1`) |
| Tile-roof material for the crest cluster | `assets/urban/nv_content/common_assets/shared_textures/tile_roof_01_{a,n}.png` | T2 (local use) | Y | B | **the geometry stays procedural** (gap **G1**) — this only replaces the flat `roof_color = (0.045, 0.030, 0.018)` constant at `scene07:359` |
| Wooden pole (E7-10) | procedural Ø100 mm cylinder + `assets/urban_cc0/modular_wooden_pier/textures/modular_wooden_pier_poles_{diff,nor_gl,rough}_1k.png` | **CC0 1.0** | Y | A (material) | one cylinder; no asset can beat that on cost |

**07 · procedural residue** (elements with **no** adequate asset, in priority order):

| # | Element | Why procedural | Cheapest correct form |
|---|---|---|---|
| **R7-1** | The stair courses themselves | `build_worn_stone_stairs` **is** the archetype builder and is already written | one call; `rock_03_broken` layered on top later |
| **R7-2** | **Temple roof cluster (G1, HIGH)** | 0 tile-roofed Korean geometry in 291 + 33 rows | procedural hip-gable masses + `tile_roof_01` texture. Note §0.2: this is only ever visible in `gate_frame`, so it is the **lowest-value** item in the whole spec despite being the largest gap |
| **R7-3** | Fern band (G2, MEDIUM) | 0 fern assets | `Switchgrass` stand-in now; a CC0 fern atlas on crossed quads is the real fix |
| **R7-4** | Moss as a large-area layer (G3, MEDIUM) | no moss PBR set | tint convention (§C-A2) + the CC0 patch texture above |
| **R7-5** | 소맷돌 / 지대석, if ever wanted | trivial prisms | **not wanted** — G7 shows neither. Recorded so nobody adds them from the intake's C1 candidate |

## 3.3 `10 ·` element → asset

| Element | Asset id / path | Licence | Verified | Fit | Placement note |
|---|---|---|---|---|---|
| **Deck board material** | `assets/urban_cc0/modular_wooden_pier/textures/modular_wooden_pier_planks_{diff,nor_gl,rough,metal}_1k.png` — 1024², orange 98.57 %, **albedo_lin 0.0799** | **CC0 1.0** | Y | **A** | the intake's named choice. **Too dark and too warm as-is** — see §4.2-3 for the tint that lands it in the weathered band |
| Deck post material | `…/modular_wooden_pier_poles_{diff,nor_gl,rough}_1k.png` | CC0 1.0 | Y | A | separate 3-map set |
| **Plank field geometry** | `gk.build_deck_planks(kit, path, x0, y0, x1, y1, z, mtl, plank_w=…)` (`ground_kit.py:1464`) | — | — | **A** | already exists and its 10 mm gaps were graded **excellent** (`tonglam_v2` §2.4). **Only the material is missing, not the geometry** |
| **Bare trees** | `Trees/Gray_Birch.usd` · `Trees/Elm_Sapling.usd` · `Trees/Lombardy_Poplar.usd` with `/Root/leaves` deactivated | T2 | Y | **A** | **the leafless gap is solved at zero procurement cost** — see §3.4 |
| Autumn-legal shrubs | `veg_shrub_hedge_yellow_01` (16,116 tri, manifest note *"계절 게이트 대상"*) · `Shrub/Burning_Bush.usd` (**red 30.2 %** — removed from the *global* pool for being autumn, therefore **legal here** by the same scope logic as the dry leaves) · `Shrub/Grass_Short_A/B/C` (orange 17.7–17.9 %, inside the turf gate's `orange ≤ 0.25`) · `Shrub/Switchgrass.usd` (억새, 8,934 tri) | T2 | Y | **A** | this is the whole dormant-vegetation palette and it already exists |
| **Leaf litter, 3D** | `sct_debris_leaves_dry_01…04` — 3,417 / 5,298 / 5,988 / 10,239 tri, orange 34.3 % + red 65.5 %, `SCENE_SCOPE = ("C2","07","10","D3")` | T2 | Y | **A** | **explicitly legal in scene10**. `scene='10'` is **mandatory** on the call or the loader logs `scope_unchecked`. ⚠ the same rows are scoped to `'07'` — **that is a permission, not a recommendation; 07 is summer** |
| Leaf litter, ground material | `sc.TEX["leaf_ground"]` (`assets/scene01/leaf_ground_{diff,nor_dx,rough}.jpg`) | CC0 | Y | A | already bound; the fix is **coverage**, not the texture |
| Leaf litter, fine scatter | `sc.VEG_DEBRIS` = `Debris/{fallcluster1,fallcluster2,maplefall1,oakfall1,oakfall2}.usd` | T2 | Y | A | the CB-2 feather ring already uses these. Coverage is area-driven: `n = A·(−ln(1−cover)) / mean_effective_area` |
| **Rock outcrop (E10-10)** | `rock_moss_set_01` — 8.005 × 6.949 × 1.768 m, 63,127 tri, diff **orange 82.2 %** | **CC0 1.0** | Y | **A** | orange-dominant diffuse ⇒ **the better of the two scans for late autumn**; reserve `_02` (yg 92.9 %) for scene07. `z_mode='base'` |
| Outcrop foot boulders | `rock_03_broken` · `rock_01` · `rock_02` | T2 | Y | A | ⚠ `tonglam_v2` §1 row 10 flags D-5 rocks on the trail legs (F2) — same commit |
| **Distant city glimpse (E10-13)** | `building_kit` **BS-4** `kind="backdrop"` — `should_backdrop()` (`building_kit.py:496`), builder `_b_backdrop()` (`:1613`) | — | — | **A** | *"distant-silhouette-only regardless of distance. **No windows**"*, prim budget **4 (3)** per tier, levels at the statutory 4.0 m/floor. 3–4 prims with no windows **is** what "faint" means. Auto-demote also fires at `d_true > 80 m` |
| Distant city, asset alternative | the 8 `buildings_far` (`Building_178…183`, `Building_19/20`) — 1,354–9,963 tri, **`mpu 0.01`** | T2 | Y | B | `urban_kit` applies the ×0.01 automatically; `far_override='auto'` also binds the §1.11 far-tier albedo override. Cheap, but their value is skyline variety, not faintness |
| Galvanised concealed structure (optional) | `shared_textures/metal_steel_galvanized_01_{a,n}.png` | T2 | Y | A | **only** for the concealed under-flight column G10 shows in shadow. **D1's visible galvanised frame is withdrawn** (§2.A.1) |
| Lattice / grating panel material | `shared_textures/tile_metal_chrome_holes_01_{a,n,orm}.png` (a perforated-metal set; **the texture is not scene-scoped**, only the `traf_barrier_mov_type3_*` assets that use it are) | T2 | Y | B | for a *metal* lattice; **G10's lattice is timber**, so the primary route is a procedural timber grid (R10-2) |
| Rest-platform bench | `painted_wooden_bench` (CC0, 630 tri) | CC0 1.0 | Y | B | `bench_park_02/03` were rejected on **Korean-ness** by W3-R2 §2.3, not on licence |

**10 · procedural residue:**

| # | Element | Why procedural | Cheapest correct form |
|---|---|---|---|
| **R10-1** | **The entire railing** | **no wooden railing asset exists**; `safety_railing_01` is **banned**; `typical_building_08_railings` is a `zmin +11 m` rooftop parapet the loader refuses. And `broken_landing = 0` — the missing bay — **can only be expressed parametrically** | `sc.build_railing_line` (`scene_common.py:1686`) with rectangular sections; see §4.2-2 |
| **R10-2** | Lattice infill bay | 0 grating/lattice/trellis assets | a timber grid: two crossed baluster sets, or `build_open_riser_stairs(..., slits=N)` (`scene_common.py:1972`, *"splits the plate into (slits+1) strips … (grating)"*) re-used as a panel. Two scenes already render gratings (`scene11`, `sceneN5`) |
| **R10-3** | **Weathered-grey plank tone (G5, MEDIUM–HIGH)** | **no weathered/silver-grey timber set exists** — every wood map in the repo is warm or dark brown | interim: desaturate the CC0 pier planks (§4.2-3). Real fix: procure one CC0 weathered-plank set |
| **R10-4** | Deck plank field | see above — the parametric gap is the value | `build_deck_planks` |

## 3.4 The leafless-tree mechanism — the single highest-value finding

`[measured]` with usd-core 26.8 this session. **Every tree in the catalogue is green-foliage**: all
10 measured `veg_manifest_w2` tree/shrub rows read green 74–100 %, **orange 0.000, red 0.000**,
without exception. There is no leafless, no bare-branch and no winter tree asset anywhere.

**But three tree USDs split trunk and leaves into separate prims, and the branch armature lives in
the trunk prim, not the leaf prim:**

| Asset | `/Root` children | trunk tri | leaves tri | trunk bbox | full bbox | Leafless viable |
|---|---|---|---|---|---|---|
| `Trees/Gray_Birch.usd` | `Looks, trunk, leaves` | 118,417 | 138,208 | 2.546 × 2.513 × **3.299** | 2.672 × 2.563 × 3.325 | **YES** — trunk spans **98 %** of the full canopy bbox ⇒ a real bare 자작나무. **−54 % tri** |
| `Trees/Elm_Sapling.usd` | `Looks, trunk, leaves` | 47,334 | 65,934 | 1.654 × 1.660 × **3.043** | 1.742 × 1.750 × 3.087 | **YES** — bare sapling. **−58 % tri** |
| `Trees/Lombardy_Poplar.usd` | `Looks, trunk, leaves` | 101,130 | 316,776 | 4.466 × 4.198 × **13.422** | 4.838 × 4.491 × 13.673 | **YES** — bare 13.4 m. **−76 % tri** |
| `Fraxinus` · `Shumard_Oak` · `Scarlet_Oak` · `Black_Oak` | trunk + 5–6 MASH `PointInstancer`s | — | — | — | — | **NO** — leaves ride inside the branch instancers; killing an instancer removes the branch with it |

**The machinery already exists**: `SEASONAL_SUBPRIMS = {"Shrub/Rhododendron.usd": ("Flowers",)}` and
`_deactivate_seasonal(stage, asset_path, usd_rel)` (`scene_common.py:2149-2172, 2293-2295`), which
`SetActive(False)`s a named child so it leaves composition at zero cost. This is the **same mechanism
the cherry/rhododendron season ruling already sanctioned** — which is why using it here is a
continuation of project policy, not a new device.

**Two cautions that must be in the implementing commit:**

1. **`SEASONAL_SUBPRIMS` is global.** Adding tree rows to it strips leaves in **all 33 scenes**. The
   spec requires a **scene-gated** table (`BARE_SUBPRIMS`, applied only when the calling scene is
   `'10'`) or a `strip_prims=` kwarg on `add_vegetation`. Either is a `scene_common` edit and
   therefore **K4 territory, not S3's** — see §8-OQ3.
2. **`_deactivate_seasonal` is called only from `place_shrubs`** (`scene_common.py:2838`). The tree
   path in `build_tree` (`:2455`) does **not** call it. The call must be added, and it must run
   **before `SetInstanceable(True)`** (`scene_common.py:2473`) — once a prim is instanced its
   descendants live in a shared prototype and per-instance edits are silently ignored. This is the
   same class of silent-inertness bug the repo already documented for the instancing flag itself
   (`scene_common.py:2467-2471`).

## 3.5 Two operational cautions

1. **Never run `assets/verify_urban.py` casually.** It **opens `urban_manifest_w3.json` in `"w"`
   mode** (line 601) and creates `assets/urban/_verify/`. It is a mutator, not an inspector. Invoke
   it only when a manifest refresh is actually intended, and only as
   `/tmp/usdvenv/bin/python assets/verify_urban.py --sheet` per §13.
2. **Budget against `tri_effective`, not `tri_unique`,** on every row with instances — `Shumard_Oak`
   is 99,509 unique but **4,552,624 effective**. §12-14 still governs: *triangle count is not the
   budget, instanceability is* — but the number to state in a commit message is the effective one.

---

# 4. Buildable numbers *(brief item D)*

> **Citation discipline.** Where a number carries `[law]` a Korean standard or statute was read this
> session and is keyed to §4.0. Where it carries `[data]` it is a statistic over a real built-asset
> register. Where it carries `[assumed]` the reasoning is stated and the executor must **not**
> silently upgrade the tag.

## 4.0 The Korean authorities that actually govern these two stairs

| Key | Document | Status for our two scenes |
|---|---|---|
| **KCS-3450** | 조경공사 표준시방서 **KCS 34 50 10 조경구조물** (+ 34 50 15 현장제작설치 시설), 국토교통부고시, 시행 2024-12-16 | **the governing spec** for a park stair/deck |
| **KFS-TRAIL** | 산림청 「등산로 정비 매뉴얼」 (2010, 194 pp) — 표 3-6, 〈표 13-1〉, 그림 3-20…3-32, 특별시방서 11·12·13·17 | **the governing manual** for a trail stair, timber **and stone** |
| **LDS-2016** | **조경설계기준** (한국조경학회 / 국토교통부) §5.9 경사로 · §5.10.2 계단 | **the outdoor landing rule** — see F-4 |
| **KNPS-STAIR** | 공공데이터포털 「국립공원공단_탐방로상 시설-계단」 (2025-08-06), **1,183 rows of real built national-park trail stairs**, KOGL 제한 없음 | **built reality**, `[data]` |
| **KNPS-RAIL** | 공공데이터포털 「국립공원공단_탐방로상 시설-난간」 (2024-09-11), **1,805 rows of real built trail railings** | **built reality**, `[data]` |
| **SANJI-183** | 산지관리법 시행령 제18조의3④ [별표 3의3] 제4호 다 (개정 2020-03-03) | **statutory width cap** on forest-land trails |
| PIRAN-15 | 건축물의 피난·방화구조 등의 기준에 관한 규칙 제15조 | **건축물 only — does NOT bind either scene** |
| HOUSE-18 | 주택건설기준 등에 관한 규정 제16·18조 | **주택단지 only — does NOT bind either scene** |

**Three findings that change what this document proposes.** All three are corrections to the intake,
not to the reference images.

- **F-1 `[law]` — the outdoor stair-proportion window is 2R + T = 600–650 mm**, and it must be
  **uniform over the whole flight**. KCS 34 50 10 **3.2.8(3)**, verbatim:
  > "계단 및 경사로의 규격은 관련 법규에 적합하여야 하며, 이때 단 높이(R)와 너비(T)는
  > **2R+T=60~65 cm**를 유지하되, **전 구간에 걸쳐 동일하여야 하고**, 미끄러지지 않도록 표면
  > 처리하여야 한다."

  KFS-TRAIL p.70 gives the trail version, slightly wider: *"계단높이는 **15cm이하**, 노폭은
  **25~30cm** … **2H+B=60~70cm**"*.
  **Consequence: `w3_intake_06_10.md` §7-2 is refuted.** It called scene10's `2R+T = 0.630` *"an
  interior ratio, not an outdoor one"* and proposed *"riser ≈ 0.15, tread ≈ 0.35–0.40
  (2R+T ≈ 0.65–0.70)"*. **0.630 is squarely inside both windows**, and 0.65–0.70 is partly **outside**
  the governing KCS band. scene10's riser/tread is **not** the defect. The defects are the stacking,
  the width, the railing sections, the missing rest platform and the tone.
- **F-2 `[law]` — 1.5 m is a statutory ceiling, not a mid-band value.** SANJI-183, verbatim:
  > 숲길(산책로·탐방로·등산로·둘레길): *"**너비가 1.5미터 이내일 것.** 다만 … 교통약자의 보행을 돕기
  > 위해 필요한 경우 … 휴식·대피를 위한 장소를 설치하기 위해 필요한 경우 … 1.5미터를 초과할 수 있다."*

  `[data]` KNPS-STAIR, the 155 records whose 시설물명칭 contains "데크": median **1.50 m**;
  **1.50 = 47.7 %**, 1.20 = 18.7 %, 1.30 = 14.2 %, **1.80 = only 9.0 %**.
  **Consequence: the intake's "1.5–1.8 m, typical 1.8" is corrected to "1.2–1.8 m, centre and mode
  1.50 m", and 1.5 m is where the distribution piles up because it is the legal cap.**
- **F-3 `[law]` `[data]` — no building railing rule binds a trail deck.** A trail/park deck stair is
  not a 건축물 and not a 주택단지 facility, so PIRAN-15 (85 cm handrail) and HOUSE-18 (1.2 m guard,
  ≤100 mm 간살 안목) **do not apply**. KCS 34 50 10 3.2.6 sets no numeric height. Built reality
  (KNPS-RAIL, n = 1,227): median **1.10 m**, modes **1.00 (35.8 %) · 1.20 (19.9 %) · 1.10 (15.1 %)**
  — **71 % of real trail railings are 1.0–1.2 m.** What KCS *does* fix is the geometry we care about:
  > **KCS 34 50 10 3.2.6(3)**: *"비탈면에 설치되는 계단난간의 **세로부재는 계단면에 수직**이 되도록
  > 제작, 설치하여야 한다."*

  i.e. balusters stand **plumb**, not raked — which scene10 already does correctly (`scene10:1211-1218`).
- **F-4 `[law]` — there *is* an outdoor landing rule, and it is stricter than the building one.** The
  building rule (계단참 every 3 m of height, 유효너비 ≥ 1,200 mm; PIRAN-15 제15조①1) does not bind a
  park deck — but 조경설계기준 **5.10.2(3)** does:
  > *"높이 **2m**를 넘는 계단에는 **2m 이내마다** 당해 계단의 **유효폭 이상**의 폭으로 **너비 120cm
  > 이상**인 참을 둔다."*

  and 5.9(4) fixes a landing plan size for continuous ramps at **1.5 m × 1.5 m 이상**. The two
  converge on **1,500 × 1,500 mm** for a 1.5 m-wide flight. Separately, KFS-TRAIL 특별시방서 12-3 마
  (p.165) adds a *ground-following* trigger: insert a 계단참 whenever the **stair foot would rise more
  than 300 mm above natural grade**. **Reality caveat**: the KFS bill of quantities specifies a
  **22-riser deck stair as one item with no landing**, i.e. 3.3–4.4 m of unbroken rise — real trail
  stairs on steep ground routinely exceed 5.10.2(3). Our 6-flight plan (max 8 risers = 1.20 m of rise
  per flight) is comfortably inside the rule, so this is a margin, not a constraint.

## 4.1 `07 ·` scene07 buildable numbers

### 4.1-1 The course table

Frozen: `STAIR_RUN = 12.2`, `STAIR_DROP = 4.2`, corridor plane `path_z(x) = −4.2·x/12.2` (19.0°),
walk-line half-width `foot_half = 0.22`, corridor `y ∈ [−1.7, 1.7]`.

The rebuild is a **budget problem**: today **34.0 % of the run is open slope between pavers**.
Target: **0 % open slope**, with visible joints only *within* a course and only up to 60 mm wide.

**The corridor is 19.00° = 34.4 % grade.** `[law]` KFS-TRAIL 특별시방서 13-1 (p.165) applies 돌계단 at
**slope ≥ 15 %** — so a stone stair is the correct treatment here, not an option. And 13-2 다 (p.165)
makes 〈표 13-1〉 govern *"이하에 기술되는 모든 계단공종"*, stone included:

| 표 13-1 row (slope) | H (mm) | B (mm) | 2H+B |
|---|---|---|---|
| 25° | 150 | 310 | 610 |
| **20°** | **150** | **410** | **710** |
| 15° | 150 | 560 | 860 |

| Quantity | Value | Basis |
|---|---|---|
| Courses `n` | **28** | 4.20 / 28 = **0.1500 m** rise and 11.99 / 28 = **0.4282 m** tread ⇒ stair pitch **19.30°**, i.e. the stair follows the 19.00° corridor. **This lands within 18 mm of 〈표 13-1〉's 20° row (150 / 410)** `[law]` KFS-TRAIL 표 13-1, p.166 — the proposal was derived from G7 and then found to coincide with the published Korean table, which is the strongest evidence in this document |
| Mean rise `riser_mu` | **0.150 m** | `[law]` KFS-TRAIL p.70: *"계단높이는 **15cm이하**"*; and every 표 13-1 row from 25° down uses exactly 150 |
| Rise jitter `jr` | **± 0.030** → rise band **0.120–0.180** | `[assumed]` — 표 13-1 and KCS 3.2.8(3) both specify a **uniform** rise, so any spread is a *weathering/settlement* claim, not a design claim. ±0.030 is a settled-stone read; today's ±0.06 spread is neither a built stair nor a stepping-stone path. **The self-check reports it; 통람 judges it** |
| Mean tread `tread_mu` | **0.4282 m** | `11.99 / 28`; the x advance per course. **In a course construction there is no inter-course gap to budget** — see the back-overlap row |
| **Back-overlap `ov`** | **0.12 m** | each slab spans `[xa − ov + U(−jt/2, +jt/2), xb + U(−jt/2, +jt/2)]`, so with `ov > jt/2` **every slab beds onto the course below and the open-joint fraction is 0 by construction**. This is the row that kills A2 |
| Slabs per course `blocks` | **3** (vary 2–4 by course) | §1.A.1-1 |
| Slab width across | `(y1 − y0) / blocks` = 3.40 / 3 = **1.133 m** nominal, ±0.15 m per slab so course seams do not line up | corridor `y −1.7…1.7`; `build_worn_stone_stairs` already overlaps lateral neighbours by 1 mm. **Deliberately larger than the government trail block** — see the scale note below |
| Per-slab front-edge offset `jt` | **± 0.12 m** ⇒ neighbouring slabs in one course differ by up to **0.12 m** | this **is** the ragged nosing of §1.A.1-3 (`[ref]` 50–120 mm) — **do not reduce it**. It is safe to raise it only because `ov` absorbs it |
| **Visible joint width** (between slabs *within* a course) | **0.00–0.06 m** | `[ref]` §1.A.1-1; filled with soil, moss and `Grass_Short_C` |
| Per-slab top-z jitter `jz` | **± 0.020 m** (builder default) | bedding irregularity |
| Per-slab yaw `jyaw` | **± 3.0°** | the adopted J-14 ruling `[cite]` §1.2 — *hand-set masonry genuinely is laid a few degrees out*. **Express it as `jyaw=`, not as a `jitter=`-named kwarg**, or LINT-10 fires (§6.6) |
| Course lateral offset | **0** | A6 — abolished |
| Slab thickness | **0.25 m** | `[law]` KFS-TRAIL 특별시방서 13-2 가 (p.165) fixes 자연석 계단석 at **300 × 300 × 250 mm**; 250 mm is the thickness that survives the temple scale-up |
| Slab base / embedment | solid to `base_z = path_z(x) − 0.35` | `[law]` 13-2 나: *"자연석의 두께에 따라 터파기를 하고 지면을 다진 후 안정되게 놓고"* — the block is set in an excavation to its **full 250 mm thickness**. `−0.35` exceeds that and guarantees nothing floats (A9) |
| **Bedding under each slab** | **고임돌 + 틈메우기돌** — 1–3 small shim stones per slab, then soil fill | `[law]` 13-2 나, verbatim: *"흔들리지 않게 밑에 **고임돌 및 틈메우기돌**을 설치한 후에 주위에서 흙으로 메우고 다지며"*. Buildable as `sc.scatter_debris(pool=sc.VEG_ROCKS, sink=…)` in the joint band — and it is exactly what makes the joints read as filled rather than open |
| **Tread face** | the **rough** face is laid up | `[law]` 13-2 나: *"**거친 면을 발판으로 미끄러짐을 방지**한다"* — the anti-slip measure **is** the rough stone face. **This is the primary-source confirmation of H2**: the statutory anti-slip treatment for a natural-stone stair is the stone itself, not a strip |
| Apron at the flight ends | lower **1.00 m**, upper **≥ 0.50 m** of 돌깔기 beyond the last course | `[law]` KFS-TRAIL p.72 — this is what absorbs the +0.201 m exit lip (A11) instead of an orphan step |
| Entry step (yard z 0 → course 1) | **≈ one rise (0.150)** | today +0.002 — a 2 mm entry is not a step at all |
| Exit step (course 28 → approach z −4.2) | **≤ 0.05 m, up-step** | today **+0.201** — an orphan lip. The junction at `x = 12.2, z = −4.2` is frozen (§5.1), so the table must absorb the difference, not the road |

> **Why 28 and not the intake's 26.** The intake's C1/C2 candidates were sized on 장대석 proportions
> (riser 0.162, tread 0.47). G7 is 자연석 with *lower* rises. 28 courses puts the rise at exactly
> **0.150** — the value every 표 13-1 row from 25° downward uses — and the tread at **0.4282**, which
> is 〈표 13-1〉's 20° row to within 18 mm. **`n` is the one number in this table the executor may
> re-solve**, provided rise stays ≤ 0.150 (KFS p.70 caps it) and 2H+B stays in 600–700.

> **Scale note — the government block is smaller than the temple slab, and that is not a contradiction.**
> `[law]` KFS-TRAIL fixes the 자연석 계단석 at **300 × 300 × 250 mm** with a **300 mm repeating module
> across the flight** and 300 mm margins each side (그림 3-24/3-26, p.74–75) — i.e. a 1.5 m government
> **trail** stair is 5 blocks of 300 across. G7 is a **temple approach**: 2–4 slabs across a ~3 m
> flight, so 0.6–1.3 m each. Both are 자연석 계단; the trail manual sizes for a hand-carried block on a
> 1.5 m path, the temple for a monumental approach. **Our corridor is 3.40 m wide**, so 3 slabs of
> 1.133 m is the temple reading and the KFS 300 mm module is the *floor*, not the target. Keep the
> KFS **thickness** (250 mm), the KFS **bedding** (고임돌 + 틈메우기돌) and the KFS **rough-face**
> rule — those are construction rules and they scale; take the plan size from G7.

> **Which builder — and it is not a free choice.** `sc.build_worn_stone_stairs`
> (`scene_common.py:1907`) is the archetype builder and scene07 explicitly refuses it
> (`scene07:44-46`); wiring it costs one call and it already gives per-course lateral blocks, `jyaw`,
> `jz`, `jt` and a solid base to `base_z`. **But it has no back-overlap term**: `xa` advances by exactly
> `tread_mu` and each block spans `xa + U(−jt/2, jt/2) … xb + U(−jt/2, jt/2)`, so a course's back edge
> can stand up to `jt` behind the previous course's front edge — at `jt = 0.10` that is a **100 mm open
> joint**, which is A2 in miniature. Two ways out:
> **(i) use the shared builder with `jt = 0.06`** — joints ≤ 60 mm, at the cost of a tamer nosing than
> G7 shows; adding an `ov=` kwarg would be a `scene_common` change and therefore **K4's, not S3's**
> (H15).
> **(ii) keep scene07's scene-local generator and rewrite it as courses** with the explicit `ov = 0.12`
> above. **Recommended.** It is the only route that gets a 0 % open-joint fraction *and* the full
> ±0.12 m ragged nosing, it needs no shared-module edit, and it is consistent with the scene already
> owning its own stone code.

**Prim budget** `[measured]`: 28 courses × 3 slabs = **84 slab prims**, replacing 24 stones + 24 knobs
= 48 prims today. Net **+36 prims**. §12-14 governs: *triangle count is not the budget,
instanceability is* — and if `rock_03_broken` is used as the slab, `instanceable=True` makes 84 slabs
one prototype.

### 4.1-1b Korean stone vocabulary — which product each element is

`[law]` 조경설계기준 **2.6.2 (자연석)** and **2.6.3 (다듬돌)** classify the stone products by size. Naming
the right one keeps the executor from mixing archetypes, which is how 07 got a 디딤돌 path on a 19°
slope in the first place.

| Product | Standard definition | Where it belongs in scene07 |
|---|---|---|
| **자연석 계단석** | KFS-TRAIL 13-2 가: **300 × 300 × 250 mm** 산석 | **the course slabs** — scaled up to 1.13 m across for a temple approach (see the scale note) |
| **자연석 판석** | 점판암·사암·응회암 계열의 얇은 판; as paving it must have 답압 강도·내마모성 (2.6.2(7)); KFS uses **T100** | **the aprons** at the top and foot of the flight (1,000 / ≥ 500 mm, KFS p.72) |
| 판석 (다듬돌) | 두께 **< 150 mm**, 너비 ≥ 3 × 두께 (2.6.3(1)) | **not used** — this is a *dressed* flag; our slabs are natural and 250 mm thick |
| **호박돌** | 평균지름 **200–400 mm** (2.6.2(4)) | joint shims (고임돌) and the small end of the kerb line |
| **조약돌** | 지름 **100–200 mm**, 달걀꼴, 미가공 (2.6.2(5)) | 틈메우기돌 in the joints |
| **야면석** | 표면 미가공, 운반 가능한 비교적 큰 석괴 (2.6.2(6)) | **the kerb boulders** (§4.1-2) |
| 사고석 · 견칫돌 · 깬돌 | dressed masonry products, 150–250 mm face etc. (2.6.3(3)(4)(5)) | **not used** — these are 축대/담장 products |
| **디딤돌** | ~300 mm, top set **30 mm above grade**, long axis **perpendicular to travel** (21.5(6)(7)) | **what scene07 builds today, and it is the wrong product.** The standard puts a 디딤돌 30 mm proud on *level* ground; our 24 pavers sit on a 19° slope with 0.05–0.28 m of open ground between them. `[law]` confirmation of the intake's archetype diagnosis |

### 4.1-2 Kerb boulders

| Quantity | Value | Basis |
|---|---|---|
| Line position | `y = ±1.55` centre, i.e. **inboard of the corridor edge (±1.70) and outboard of the walk line (±0.22 + 0.10 clearance)** | §6.5 self-check: no boulder within `foot_half + 0.10` of the walk line |
| Size band | **0.40–0.90 m** across | `[ref]` §1.A.1-6; `rock_moss_set_*` scaled, or `rock_03_broken` unscaled at 1.32 m for the two largest |
| Proud of adjacent tread | **0.15–0.35 m** | `[ref]` |
| Spacing | **discontinuous** — mean 1.6 m centre-to-centre with 2–3 deliberate gaps of ≥ 3 m per flank | `[ref]`; a continuous kerb is the wrong read and would also read as a 장대석 소맷돌 |
| Count | **12–16 per flank** over the 12.2 m run | derived from the spacing |
| Seating | `z_mode='base'`, sink ≤ 0.05 m | **F2 discipline**: `tonglam_v2` §1 row 07 already failed 07 for boulders in *dark sink-rings*. A boulder that sits in a hole is the defect; a boulder that sits **on** the slope with a moss collar is the fix |

### 4.1-3 Moss coverage by zone — the buildable rule

G7's moss is not uniform; it is a function of two variables (§1.A.1-5). Buildable as a per-slab
material choice from the existing 8-material `stone_pool` (`scene07:171-173, 1068-1082`), which today
uses a blind `moss_every = 3`:

| Zone | Definition | Moss fraction | Current |
|---|---|---|---|
| Walked centre band | `\|y\| ≤ 0.35` on a tread top face | **0.00–0.10** | ~0.33 (blind) |
| Tread outer band | `0.35 < \|y\| ≤ 1.70` | **0.35–0.55** | ~0.33 |
| **Riser faces** | every vertical face | **0.60–0.85** | ~0.33 |
| Joints | between slabs and between courses | **1.00** (soil + moss, plus `Grass_Short_C` weeds) | n/a — today they are *open slope* |
| Kerb boulder tops | — | **0.70–0.90** | n/a |
| Terrace / margin | `\|y\| > 1.70` | **0.20** moss + fern/understory | n/a |

**`[law]` moss is a specifiable design attribute in Korea, not incidental weathering.** 조경설계기준
**2.6.2(1)**: *"자연석은 미적인 가치를 지닌 경질의 것으로서 … 다만, **이끼 등 착생식물의 보존이 필요한
산석은 설계서에 이를 명시한다.**"* — the standard contemplates a designer specifying that the moss on a
산석 is to be **preserved**. No Korean document gives a coverage percentage, so the table above is
`[ref]` + `[assumed]`; but the *existence* of zoned, preserved moss on temple-approach stone is
standards-backed, not a stylistic choice.

Implementation: replace `moss_every = 3` with a **zone-driven pool index** — the pool already exists,
only the selection rule is blind. The `moss` path token must be present on the moss materials so
`_look_spec` (`scene_common.py:520, 567`) classes them as `veg`; `M["gk_moss"]` (`scene07:1055`)
already demonstrates the convention.

### 4.1-4 Backdrop plan (lowest priority — `gate_frame` only)

| Element | Plan | Scale check |
|---|---|---|
| Roof cluster | **3 roofs at staggered depth** replacing the single `hall` (`scene07:281-284`): near roof at `cx ≈ −16`, mid at `cx ≈ −24` offset `+cy 8`, far at `cx ≈ −33` offset `−cy 6` | a 팔작 hall at 9.0 × 5.6 m footprint with a 5.2 m ridge is the existing `hall`; keep that mass and clone it twice at 0.85× and 0.7× |
| Eave form | upturned eave: raise the eave-end z by **+0.35 m** over the last 0.8 m of run, i.e. one extra `build_slope` segment at a shallower drop | `[assumed]` — 처마 곡선 is a curve; a two-segment approximation is the cheapest read that is not a flat plane |
| Roof material | `tile_roof_01_{a,n}.png` (§3.2) replacing the `roof_color` constant | — |
| Rafter row | a dentil strip of 20–24 small boxes under the eave of the **near** roof only | `[ref]` — visible only on the nearest roof in G7 |
| Red wall fragment | one 단청-red box under the mid roof's eave, `u 0.33–0.40` in G7 | `[ref]` |
| **Occlusion / sightline** | the roofs must be visible over the crest from `gate_frame`'s eye at `(7.0, 0, path_z(7.0)+1.50)` = `(7.0, 0, −1.91)` looking at `(−5.6, 0, 1.60)` | **compute it in SMOKE, do not eyeball it.** G7's perspective (roof top surfaces seen from a camera that is below the crest) is not self-consistent; the buildable resolution is to place the roofs on the far side of the crest at a ridge z that clears the crest sightline, and **assert that clearance numerically** in the house style |
| Wooden pole | Ø100 mm × 4.5 m cylinder at `(cx ≈ −2.0, cy ≈ +2.6)`, pier-pole texture | `[ref]` E7-10, one prim |
| Distant ridge | **unchanged** (`scene07:310-331`) | §1.B-2 B7 — it is a working horizon fix for the +X cuts, which G7 does not photograph |

### 4.1-5 Season re-bind

| Surface | From | To |
|---|---|---|
| `PathCorridor` slope (`scene07:227`) | `"leaf"` → `leaf_ground` (autumn) | summer forest floor: `dirt_park` darkened, moss patches, `Grass_Short_C` at the joints |
| `SouthTerraceA/B/C`, `Approach` (`:217-219, 228`) | `"leaf"` | same; the terrace is the **grazing judging face**, so its albedo change is a render-gate item (GT-17) |
| 6 corridor lobes (`:236-238`) | carpet over the walked surface | **re-sited to the margins** — `\|cy\| ≥ 1.0`, none crossing the walk line |
| 3 yard lobes (`:251-252`) | keep | keep; a courtyard does collect litter at its edges |
| 128 feather cards (`:1191-1201`) | keep the mechanism | reduce `cover` to the margin density; the pool stays `VEG_DEBRIS` |
| `sct_debris_leaves_dry_*` | scope permits `'07'` | **DO NOT PLACE** — §3.3 note; 07 is summer |

## 4.2 `10 ·` scene10 buildable numbers

### 4.2-1 Stair re-table

Frozen: **total drop 6.600 m**. Read **F-1** and **F-2** in §4.0 first — they overturn the intake's
riser/tread and width claims, and they are the reason this table is much more conservative than the
parked candidate D1.

| Quantity | Current | Target | Basis |
|---|---|---|---|
| **Riser** | 0.165 | **0.150** | 6.600 / 0.150 = **44 risers exactly**. `[law]` KFS-TRAIL p.70 caps trail rise at **150 mm**; every 〈표 13-1〉 row from 25° down uses exactly 150. **Note: the current 0.165 is *also* legal** — 〈표 13-1〉's 30° row is 170/300 — so this row is a *fidelity* change (a shallower outdoor read), not a compliance fix |
| **Tread** | 0.300 | **0.310** | 2R + T = **0.610** `[law]`, inside KCS 34 50 10 3.2.8(3)'s **600–650** and inside KFS's 600–700; pitch **25.8°**. This is 〈표 13-1〉's **25° row (150 / 310) verbatim**. ⚠ the intake's proposed 0.350 gives 2R+T = 650 — the very top of the KCS window — and its stated target band "0.65–0.70" is **partly outside** it. Do not use 0.350 |
| Uniformity | uniform | **uniform (mandatory)** | `[law]` KCS 34 50 10 3.2.8(3): *"전 구간에 걸쳐 동일하여야 하고"*. No per-flight variation, no jitter |
| **Clear width** | 1.38 | **1.50 m** | `[law]` SANJI-183: **≤ 1.5 m is a statutory cap** on forest-land trails (exceptions: 교통약자 / 휴식·대피 장소). `[data]` KNPS-STAIR, 데크-named stairs n = 155: **1.50 m = 47.7 %**, median 1.50; **1.80 m only 9.0 %**. ⚠ the intake's "1.5–1.8, typical 1.8" and this document's earlier 1.60 are both **corrected to 1.50**. `half_w` 0.69 → **0.75** |
| Flights | 4 × 10 | **6 flights: 8, 7, 8, 7, 7, 7** = 44 | G10 shows **short flights with generous landings**. `[law]` KFS-TRAIL 특별시방서 12-3 마 (p.165) is the outdoor landing trigger — see the landing row |
| Flight drop | 1.650 | 1.05–1.20 m | derived |
| Flight run | 3.000 | 2.17–2.48 m | derived (`8 × 0.310 = 2.48`, `7 × 0.310 = 2.17`) |
| Intermediate level surfaces | 4 turn plates 1.40 × 2.80 | 6 flights need **5** intermediates: **4 turn landings 1.50 × 1.50 m** + **1 rest platform 1.50 × 3.00 m**. The entry deck (`entry`, `scene10:192`) and the ground arrival are unchanged in kind | `[law]` 조경설계기준 **5.10.2(3)** — landing width ≥ the stair's own 유효폭 and ≥ 1,200 mm; **5.9(4)** fixes 1.5 × 1.5 m for a continuous run. The two converge on **1,500 × 1,500** for a 1.5 m flight. C4/C5 |
| Rest platform | absent | **1**, after flight 3 (8+7+8 = 23 risers) at **z = −3.450**, the nearest level surface to mid-height (−3.300), with a bench | C5 — *the* park-vs-egress signature. `[law]` SANJI-183's own exception 2) names **휴식·대피를 위한 장소** as a legitimate reason to exceed the 1.5 m width, so the rest platform may be built **wider than the flights** and is the one element that is licensed to be |
| Landing slab thickness | 0.12 | 0.12 (keep) | no reason to change |
| **Landing pitch** | none between flights | **a landing at least every 2.00 m of rise** | `[law]` 조경설계기준 5.10.2(3), *"높이 2m를 넘는 계단에는 2m 이내마다 … 참을 둔다"* — **stricter than the 건축법 3 m rule**, and our 8-riser maximum (1.20 m of rise) clears it with margin (§4.0 F-4) |
| **Landing trigger (ground-following)** | — | insert a 계단참 whenever the **stair foot would rise > 300 mm above natural grade** | `[law]` KFS-TRAIL 특별시방서 **12-3 마** (p.165), verbatim: *"데크계단의 설치시 경관을 고려하여 **계단하단부와 지반과의 높이차가 30cm 이상으로 올라가지 않도록** 시공하고, 필요할 경우에는 **계단참을 설치하여 높이차를 조정**한다."* **This, not the 건축법 3 m rule, is the outdoor landing law** — and it is a *ground-following* rule, which is precisely why a real deck switchback traverses (C1) |
| The 건축법 "3 m마다 1.2 m 계단참" rule | — | **does not apply — and is superseded by a stricter one** | `[law]` PIRAN-15 제15조① binds 건축물 (연면적 200 ㎡ 초과); HOUSE-18 binds 주택단지; a trail deck is neither. **Do not cite 3 m.** Cite 조경설계기준 5.10.2(3)'s **2 m** instead (§4.0 F-4) |
| Plank gap | 0.02 | **0.02 (keep)** | `tonglam_v2` §2.4 graded it excellent |
| Total drop | 6.600 | **6.600 (frozen)** | §9 P-2 |

> **The three identities to state in the commit message**: `44 × 0.150 = 6.600` exactly ·
> `8+7+8+7+7+7 = 44` · `2R + T = 2(0.150) + 0.310 = 0.610 ∈ [0.600, 0.650]` `[law]` KCS 34 50 10
> 3.2.8(3). If the executor re-solves the riser, all three must be re-solved together and re-printed
> by `deck_module_selfcheck`.

> **The honest headline for this sub-section**: *scene10's stair proportions were never the defect.*
> `[law]` `2R + T = 0.630` is inside the governing window and 〈표 13-1〉's 30° row is 170/300. What
> makes the scene read as an apartment scissor stair is **C1 (four flights stacked in a 3.0 × 2.8 m
> masonry shaft)**, **C7–C9 (round steel-looking railing sections at half the real baluster density)**
> and **C18 (near-black timber)** — in that order. An implementer who re-tables the risers and stops
> there will have changed the numbers and not the reading.

### 4.2-2 Railing — sections and pitch

**This is the highest-value single change in scene10.** Everything below replaces a cylinder with a
box, which is a same-cost prim swap. Sections marked `[law]` are read off the dimensioned drawings in
KFS-TRAIL 그림 3-20…3-30 (book p.72–77) — the only primary Korean source that dimensions trail timber.

| Member | Current | Target section | Note |
|---|---|---|---|
| Newel post | `CYL r 0.075` (Ø150 round) | **square 0.100 × 0.100**, height = rail height + **0.15 m** projection | `[law]` **100 × 100 방부각재** is the section KFS-TRAIL dimensions for 목계단 members (그림 3-27/3-28/3-29, p.76–77). The 0.15 m projection is `[ref]` |
| Newel cap | absent | **0.130 × 0.130 × 0.045** box, chamfer optional | `[ref]` — the cap is the strongest single "timber, not steel" tell |
| Intermediate post | `post_r 0.05` (Ø100 round) | **square 0.080 × 0.080** | `[law]` **80 × 80 방부각재** is KFS-TRAIL's secondary member (말뚝, 그림 3-28, p.76). Spacing keeps `1.05 m` unless the flight run forces otherwise |
| Top rail | `bar_t 0.06` round | **rectangular 0.110 (w) × 0.045 (t), laid flat** | `[ref]` §2.A.1-3 — a hand rests on it |
| Mid rail | `mid 0.55` round | **rectangular 0.090 × 0.040**, at 0.45–0.50 of the rail height | |
| Bottom rail | absent | **rectangular 0.090 × 0.040**, 0.10–0.15 m above the tread/deck | present in most G10 bays |
| Baluster | `bal_r 0.022` (Ø44 round) @ **0.300 m** | **square 0.040 × 0.040 @ 0.150 m centres** ⇒ **clear gap 0.110 m** | `[ref]` ≈7 per 1.1 m bay. **The ≤ 100 mm 안목 rule does NOT bind here** — see F-3: it is 주택건설기준 등에 관한 규정 제18조, scoped to 주택단지. No KDS 34 / 자연공원 clause imposing it was found. 110 mm is therefore admissible and matches G10. **The self-check still asserts the clear gap** (so the number is visible), but it asserts it against **0.110 m ± 0.010**, not against a statute |
| Baluster orientation | vertical on rakes (already correct) | **keep vertical (plumb) on rakes** | `[law]` KCS 34 50 10 **3.2.6(3)**: *"비탈면에 설치되는 계단난간의 **세로부재는 계단면에 수직**이 되도록 제작, 설치하여야 한다."* The scene is already compliant (`scene10:1211-1218`) — **record it so nobody "fixes" it to a raked baluster** |
| Rail height | 1.05 | **1.10 m** | `[data]` KNPS-RAIL, n = 1,227 real built trail railings: **median 1.10**, modes 1.00 (35.8 %) · 1.20 (19.9 %) · 1.10 (15.1 %) — **71 % are 1.0–1.2 m**. `[law]` F-3: PIRAN-15 (85 cm handrail) and HOUSE-18 (1.2 m) **do not bind** a trail deck, and KCS 34 50 10 3.2.6 sets no number. ⚠ **this document's earlier 1.20 m proposal and the intake's are both corrected to 1.10** — a 50 mm move from the current value, not a redesign. Use 1.50 m only if a flight is elevated and exposed (KNPS 데크 subset mode, n = 27) |
| **Lattice bay** | absent | **one** bay, a crossed timber grid at ≈0.12 m pitch both ways, filling the full bay between top and bottom rail | `[ref]` E10-8. Place it on a bay that is in `broken_rail` or `reversal`, or it will not appear in any judged cut |
| **Broken bay** | `broken_landing = 0` | **unchanged** | §9 P-2 frozen |
| Fixings, if ever modelled | — | Ø16 × 180 main, Ø10 × 150 secondary | `[law]` KFS-TRAIL 그림 3-20/3-27 (p.72/76). Below h0.3 legibility — record only |
| Ground embedment of a timber post | — | **50–100 mm** below grade, **≥ 30–50 mm** proud of the compacted surface | `[law]` KFS-TRAIL 특별시방서 **17-2** (p.169) — the outdoor answer to RF-1's base-plate question for a *trail* post: it is **embedded**, not plated |
| Shared-builder note | `sc.build_railing_line(..., baluster_r=0.0)` (`scene10:1207`) | keep `baluster_r=0.0` and keep the scene-local baluster loop | the comment at `:1205-1207` records that turning the shared balusters on duplicates the cylinders and the red team found **48 interpenetrating pairs**. That trap survives the section change |

### 4.2-3 Timber tone — the weathered patina

Target: **weathered grey-brown, desaturated, silvered top faces.** `[ref]` §2.A.1-8.

| Parameter | Current | Target | Note |
|---|---|---|---|
| Base map | `TEX["wood_dark"]` (`assets/scene01/wood_dark_*`) | **CC0 `modular_wooden_pier` planks** (§3.3) | the intake's named choice |
| Source albedo | — | **linear 0.0799**, orange 98.57 % `[measured]` | **too dark and far too warm as delivered** |
| Deck tint | `(1.00, 0.96, 0.90)` `:373` | **`(0.92, 0.94, 0.96)`** — a *cool* multiplier, lifting toward grey | inverts the current warm cast |
| Target linear albedo, top faces | ~0.08 | **0.13–0.17** | silvered walked surfaces; still far below the project's 0.55 far-tier cap and the ≤ 0.30 ground clamp |
| Target linear albedo, vertical faces | — | **0.09–0.12** | darker, as in G10 |
| Roughness | `wood_rough 0.85` `:384` | **0.80–0.90 (keep)** | weathered timber is matt |
| Constant-colour `wood_color` | `(0.30, 0.20, 0.12)` `:384` | **`(0.20, 0.19, 0.17)`** | it reads near-black in shadow today (`pt_noon_from_below.png` `[cite]`); this is a near-neutral grey-brown of the same value |
| RF-2 tier | — | **1990s–2000s hot-dip-galvanized tier for the concealed metal only**: albedo 0.45–0.55, **rough 0.45–0.60**, faint spangle, white bloom in crevices `[cite]` §10.7 RF-2 | the *visible* structure is timber, so RF-2's metal ladder applies **only** to the concealed under-flight column. Do **not** apply the universal `metallic 0.9 / rough 0.35` mirror-stainless default anywhere in this scene |
| Algae / weathering detail | — | greenish tint on post feet and shaded north faces, `× (0.92, 0.98, 0.92)` | `[ref]`; cheap, and it is what makes 방부목 read as *outdoor* timber |
| Preservative identity | intake says *"ACQ-treated"* | **ACQ is correct; drop any CCA reference** | `[law]` SMCS-34 표 2.4-1 lists **ACQ-1/ACQ-2, CCFZ, ACC, CCB, CUAZ-1/2, CB-HDO, BB, AAC** as the approved 수용성 방부제 — **CCA is not in the list.** Default treatment class is **3종** (2회 도포/뿜칠) unless specified (표 2.4-2). Matters only for the *initial* tint claim: ACQ leaves a green-tan cast that weathers out, so the silvered target is the aged state, not the delivered state |
| **G5 gap** | — | there is **no weathered/silver-grey plank set in the repo** | the tint above is the interim. Procuring one CC0 weathered-plank set is the real fix and is a **1-line procurement row**, not a blocker |

### 4.2-4 De-stacking and the switchback rhythm

Two options. **The supervisor must choose** (§8-OQ2) because Option A changes the scene's terrain
identity and Option B does not.

**Option A — traversing deck on an open slope (matches G10, larger blast radius).**
The masonry shaft (`BankCut` 7.40 m wall, two-tier east wall, coping, head wall) is reduced to a short
head wall only; the ground becomes a real slope descending along the deck. Six flights migrate along
+X while alternating in Y, so no flight sits above another. Plan footprint grows from `x [−1.4, 4.4]`
to roughly `x [−1.5, 12]` × `y [−2.6, 1.6]`. This is what G10 shows and it is the honest fix for the
intake's *"a park deck switchback travels across the slope"*.

**Option B — de-stack in place (smaller, keeps the terrain).**
Keep the cut, but give each successive flight-pair an **+X migration of 1.6–1.8 m**, so flight 1 and
flight 3 no longer share a footprint. Plan grows to about `x [−1.4, 8.0]`. The masonry stays, so the
"fortress/shaft" half of the emergency-stair read only partly resolves.

| | Option A | Option B |
|---|---|---|
| Fidelity to G10 | **high** | medium |
| Terrain rebuild | plates `:241-254`, ybanks `:257-267`, copings `:272-274`, berm `:276-277` — **most of the scene's terrain** | plates extended in X only |
| GT rows | GT-18 + **GT-19 (ground field)** | GT-18, GT-19 much smaller |
| Dressing re-seating | all `_zone_z` consumers | few |
| Risk | high — this is effectively a terrain rebuild inside a scene rebuild | low |
| Recommendation | **A**, if the wave has the budget; the intake's diagnosis is a terrain diagnosis, not a stair diagnosis | B is a defensible half-measure and is **not** a wrong answer |

### 4.2-5 Backdrop and ground story

| Element | Plan |
|---|---|
| **City glimpse** | `building_kit` **BS-4** `kind="backdrop"` (§3.3), 2–3 masses at `d_true > 80 m` in the `−Y/−X` sector so they appear through the trunks at G10's `u 0.00–0.10`. **0 windows** is the point — `_b_backdrop` gives exactly that at 3–4 prims |
| **Bare trees** | `Gray_Birch` (park-typical 자작나무), `Elm_Sapling` (near field), `Lombardy_Poplar` (the tall verticals) with `/Root/leaves` deactivated — §3.4. The **oaks cannot be stripped**, so any oak in scene10 must be re-assigned or moved to the far backdrop where a green mass reads as distant conifer |
| Dormant ground | `grass` role kept, tint moved from `(0.55, 0.68, 0.42)` to a straw/olive **`(0.62, 0.60, 0.42)`** `[assumed]` — the ambientCG Grass001 map is 98.25 % green, so the tint is the only lever without a new texture |
| **Litter coverage** | continuous, not lobed: `sc.scatter_debris(..., pool=VEG_DEBRIS, cover=…)` over the slope polygons + `sct_debris_leaves_dry_01…04` as near-field hero patches with `scene='10'`. **Keep the 4 CB-2 lobes** as the dense cores; the continuity comes from scatter around them, not from more lobes |
| Rock outcrop | `rock_moss_set_01` at the uphill margin, `z_mode='base'`, plus `rock_03_broken` at its foot. F2 discipline: no dark sink-rings |
| Autumn shrubs | `veg_shrub_hedge_yellow_01`, `Burning_Bush`, `Switchgrass`, `Grass_Short_A/B` replacing the 13 green blob clumps |

---

# 5. GT impact and draft ledger rows *(brief item E)*

## 5.1 Classification, and why both scenes are FULL re-cache

Both scenes' stairs are **walked GT surfaces**, and in both scenes the rebuild changes the z of the
walk line at almost every station along it. There is no invariance argument available and none should
be attempted:

- **scene07** — `path_z()` (`scene07:438-441`) is unchanged (the 19.0° corridor plane is frozen with
  `STAIR_RUN`/`STAIR_DROP`), but the **walked surface is the stone tops, not the corridor plane**.
  Re-tabling from 24 stones (rise 0.111–0.232, mean 0.174, `[measured]`) to a course table with a
  different count and a different rise band moves **every nosing z** and every `top` in
  `STONES` — which is what `stone_metrics()` (`:576-583`) reports and what the hazard registry reads.
  The **entry step +0.002** and the **exit step +0.201** both change.
- **scene10** — riser, tread, flight count, landing z ladder and (under Option A) the ground field all
  change. `compute_flights()` (`:448-470`) is the source of the entire z ladder; nothing downstream of
  it survives.

Neither change is a candidate for the `PROOF-ONLY` class (`gt_changes_w3.md` §2). Both are
`Full re-cache` = **R-1 + R-2 + R-3** (`gt_changes_w3.md` §1).

**Frozen invariants that the re-cache must confirm, not re-baseline:**

| Scene | Invariant | Why it is frozen | Where it is checked today |
|---|---|---|---|
| 07 | corridor plane `path_z(x) = −4.2·x/12.2` | terrain, plates and slopes are all derived from it | `scene07:438-441`, `:1112-1114` |
| 07 | `SIDE_DROP = 1.8` south lateral drop | **this is the scene's primary positive GT** — the unguarded 1.8 m drop past `y = −1.7` | `scene07:161`, `:455` |
| 07 | junction at `x = 12.2, z = −4.2` | the lower approach road must not drift; `stone_layout()`'s docstring already states this as a design rule (`:479-481`) | `:582` exit step |
| 10 | **total drop 6.60 m** | §9 P-2 verbatim | `:474` `TOTAL_DROP` |
| 10 | `broken_landing = 0` bay | §9 P-2 verbatim — the scene's negative-obstacle cue | `:200`, `:1256` |
| 10 | leaf band over treads 1–2 of flight 0 | hazard cue (3) in the scene docstring (`:22-25`) — it must survive the re-table, at the new riser | `:1272-1281` |

## 5.2 `07 ·` draft ledger rows

Ready for **T5-protocol append** (`gt_changes_w3.md` §0-1: *declare before you commit*; §8 template).
Row ids continue from the live ledger's current maximum, **GT-13**. Ids are provisional until T5
allocates them.

```
| **GT-14** | 07 | Stone stair archetype rebuild: 24 discrete pavers (gap 0.050–0.276 m, 34.0 % of the
run bare slope; tread 0.270–0.384; rise 0.111–0.232 mean 0.174; cy ±0.35 lateral) → 28 courses of 2–4
bedded slabs with a 0.12 m back-overlap (open-slope fraction 0 %), visible joints ≤ 0.06 m,
tread_mu 0.4282, rise 0.150 ± 0.030 | **Every
nosing z on the walk line moves.** Entry step at the yard shoulder changes from +0.002 m; exit step at
x = 12.2 changes from +0.201 m — **the exit is an up-step onto the approach road and must stay labelled
an up-step** (GT-1 precedent). Corridor plane path_z, SIDE_DROP 1.8 and the x = 12.2 / z = −4.2 junction
are **invariant and must be re-confirmed, not re-baselined** | **Full re-cache** (R-1+R-2+R-3) — carries
GT-15 and GT-16 | CB-S3-07 · GATE-1 pilot **07** | OPEN |

| **GT-15** | 07 | Kerb boulders added at both corridor shoulders (y ≈ ±1.55…±1.70), 0.4–0.9 m,
standing 0.15–0.35 m proud of the adjacent tread | **New collision/hazard boxes beside the walk line.**
No walked-surface z change on the walk line itself (|y| ≤ 0.22), but the boulders occlude the south
shoulder in grazing cuts, which is the face the scene's positive GT is read from | **Rides GT-14's
re-cache**; additionally verify **no new occlusion of a hazard row** (GT-10 precedent) | CB-S3-07 ·
GATE-1 pilot **07** | OPEN |

| **GT-16** | 07 | Canted-knob deletion (24 prims, `scene07:174-179`, `:1135-1140`, `collider=False`) |
**No walked-surface z change** — the knobs were built below the stone top by construction (`:534`
`drop=(0.050,0.080)` with the stated purpose of leaving the walk GT unchanged). **OCCL baseline moves**:
24 prims leave every cut | **R-3 only** (re-stamp OCCL) — rides GT-14's round | CB-S3-07 · GATE-1 pilot
**07** | OPEN |

| **GT-17** | 07 | Corridor / terrace ground re-bind off `leaf_ground` (autumn) to a summer forest-floor
material; leaf lobes retained but re-sited to the margins | **No geometry, no z change.** Element AABBs
move where a lobe's cx/cy moves (GT-8 class). Albedo change on the terrace face that the grazing cut
judges → treat as a **render-gate** item, not a GT item | **R-3 only** + re-gate on the grazing cut |
CB-S3-07 · GATE-1 pilot **07** | OPEN |
```

## 5.3 `10 ·` draft ledger rows

```
| **GT-18** | 10 | Deck stair re-table: 4 flights × 10 at riser 0.165 / tread 0.300 / width 1.38
(2R+T = 0.630, 28.8°) → 6 flights (8·7·8·7·7·7 = 44) at riser 0.150 / tread 0.310 (2R+T = 0.610),
clear width 1.50 m, with 4 turn landings + 1 rest platform.
**Total drop stays 6.60 m** (§9 P-2) | **The entire descent z ladder moves.** Every tread top, every
landing top and the entry-deck step change. The two leaf-covered treads that carry hazard cue (3)
(`scene10:1272-1281`) move with the new riser and must be re-derived, not re-typed. The landing3 → lower
path proud (currently +0.020 m, `:250` vs `:474`) must be re-verified as 0 < proud ≤ 0.05 | **Full
re-cache** (R-1+R-2+R-3) — carries GT-19…GT-21 | CB-S3-10 · GATE-1 pilot **10** | OPEN |

| **GT-19** | 10 | De-stacking: flights no longer sit vertically above one another; plan footprint grows
from x [−1.4, 4.4] | Walked-surface z is covered by GT-18. **Ground field changes underneath** (Option A:
the masonry shaft becomes an open slope). Every `ground_z(x,y)` station under the new footprint moves,
so **all dressing seat z values are re-derived** (`_zone_z`, `:514-525`) | **Rides GT-18** | CB-S3-10 ·
GATE-1 pilot **10** | OPEN |

| **GT-20** | 10 | Railing rebuild: round Ø150 posts / Ø100 rail posts / Ø60 rails / Ø44 balusters at
300 mm → square timber sections at ≈150 mm baluster pitch, capped newels, one lattice bay.
`broken_landing = 0` **unchanged** | **No walked-surface z change.** Hazard/collision list changes
(post count and section change); **OCCL baseline moves substantially** — this is the largest prim-count
change in the scene | **R-1 + R-3** (registry re-derive + OCCL re-stamp); rides GT-18's R-2 |
CB-S3-10 · GATE-1 pilot **10** | OPEN |

| **GT-21** | 10 | Season re-bind: 41 green vegetation objects → leaf-off; grass plates → dormant tone;
litter coverage from 4 lobes to continuous | **No geometry if executed as material + scatter.** If any
tree is *replaced by a different asset*, its AABB and the `_grid_obstacles` entries move (`:681-688`) |
**R-3 only** if material-only; **R-1 + R-3** if any asset swap changes a tree AABB | CB-S3-10 · GATE-1
pilot **10** | OPEN — **may be split**: the material half is unblocked, the leafless-asset half is
blocked on §8-OQ3 |
```

## 5.4 Protocol notes the executor must not skip

1. **Append before commit** (`gt_changes_w3.md` §0-1). The commit message names the row ids.
2. **One re-cache per scene per batch** (§0-2). GT-14 carries 15/16/17; GT-18 carries 19/20/21. Do not
   run four re-caches on one scene.
3. **Record the command, do not guess it** (§0-3). §4's landing record stays empty until the real
   `scripts/run_data_render.py --run <id> --scenes scene07` (or `scene10`) invocation is pasted.
4. **Do not claim invariance anywhere in these rows.** GT-6's history in this very ledger — a row that
   claimed invariance, was found self-inconsistent by T3, and had to be re-classified to GT class B by a
   supervisor amendment — is the precedent for why an unproven invariance claim costs more than a
   re-cache.
5. **07's exit step is an up-step.** GT-1's rule (b) in §8's template: *"if the change adds a step
   upward, say so — an up-step mislabelled as a drop poisons the GT map."* The last stone currently sits
   **+0.201 m above** the approach road; whatever the new table gives, it is an up-step onto the road,
   not a drop.

---

# 6. WINDOW 3 execution plan for S3 *(brief item F)*

## 6.1 Where this sits in the wave

WINDOW 3 (`w3_execution_spec_v1.md` §5.1) is the scene-file window: eight WPs fully parallel, every
scene single-owned. S3 owns `scene03`, `scene07`, `scene10`, `scene12`, `sceneD3`, `sceneC2` (§4.3).
The archetype rebuild is **CB-10 work** (*"remaining scene work, all eight WPs in parallel"*) — it is
**not** CB-2, which has already landed. Two new named batches are proposed so the two rebuilds can be
piloted separately rather than disappearing into CB-10:

| Batch | Contents | Gate |
|---|---|---|
| **CB-S3-07** | scene07 archetype rebuild + kerb boulders + knob deletion + season re-bind + the 24-gon chord polish | GATE-1 pilot **07** + GT re-cache (GT-14…17) |
| **CB-S3-10** | scene10 archetype rebuild + railing rebuild + de-stacking + season re-bind | GATE-1 pilot **10** + GT re-cache (GT-18…21) |
| **CB-S3-x** | S3's remaining owed items (below), landed first because they are cheap and unblock the lint pin | none (CPU only) |

## 6.2 Commit sequence

Each numbered item is one commit. `검증 없는 확산 금지` — the §6.1 floor
(`py_compile` · `NEGOBS_SMOKE=1` · `geom_invariance_check` · `placement_lint`) runs on every one.

```
S3-1  sceneC2: delete the 4 inert bc.jit_pos/jit_yaw call sites
      (sceneC2_leaf_stairs.py:867, 868, 887, 903)                        [owed, redteam_w3_window1 §5.1]
S3-2  scene07: 24-gon chord polish on the near-field carpet masks         [owed, redteam_w3_window1 §3.1]
S3-3  scene07: knob deletion + jitter caps (A6 cy→0, A7 yaw cap ±3.0)     [GT-16 declared first]
S3-4  scene07: stair archetype rebuild — the course table                 [GT-14 declared first]
S3-5  scene07: kerb boulders + fern margins + framing trunks              [GT-15]
S3-6  scene07: season re-bind (corridor/terrace off leaf_ground) + lobes  [GT-17]
S3-7  scene07: backdrop — roof cluster expansion + wooden pole            [no GT]
      ── GATE-1 pilot 07 ──
S3-8  scene10: railing rebuild (square sections, newels, lattice bay)     [GT-20 declared first]
S3-9  scene10: stair re-table + rest platform                            [GT-18]
S3-10 scene10: de-stacking + terrain consequence                          [GT-19]
S3-11 scene10: season re-bind + litter coverage + rock outcrop + BS-4     [GT-21]
      ── GATE-1 pilot 10 ──
```

**Why S3-1 and S3-2 go first.** They are the two items S3 already owes and neither needs a render:

- **S3-1** — `redteam_w3_window1.md` §5.1 `[cite]`: *"`sceneC2_leaf_stairs.py:867/868/887/903` (×4,
  **S3's file**) … all five are **inert** … **Action**: S3 deletes 4 lines at its next C2 touch (CB-10
  at the latest)"*. They are inert (the shims return `base` / `(0,0)`), so **prim movement is zero and
  no render is owed** — but the wave's exit expectation "LINT-7-static must be 0" is not met until they
  go, and T1 cannot re-pin `expected_call_sites` 24/25 → 0/1 until both S3 and S4 have deleted.
  Landing this first unblocks T1 and K2 (the shim deletion waits on `JIT_LEGACY_CALLS == {0,0}`).
- **S3-2** — `redteam_w3_window1.md` §3.1 `[cite]`: on scene07's `h0.3_d2`, *"at ~1 m the 24-gon chord
  segments are faintly readable on the left indent — if 통람 v3 flags it, raise `n` or feather density
  for near-field masks (cosmetic knob, K1)"*. The knob is scene-side in 07: `n=24` at `scene07:1161`
  and `:1173`. Raising `n` for the **near-field** masks only (the yard drifts at cx −2.6 / −7.6, and
  corridor drift 0 at cx ≈ 1.30) keeps the prim count at 1 per lobe (a `build_blot` N-gon is one Mesh
  regardless of `n`, `[cite]` §10.5 DEC-1) and costs nothing. **Do this before the rebuild**, because
  S3-6 moves those same lobes and a combined commit would make the chord fix unattributable.

## 6.3 Pilots

Full presets, both scenes, per `w3_execution_spec_v1.md` §7.2 and the **order-prefix rule** (§4.4 X1:
*render the full preset prefix and discard extras — PT/DLSS accumulation carries frame history*).

| Pilot | Scene | Cuts | Compare against |
|---|---|---|---|
| **P07** | scene07 | full preset set + `stone_rhythm`, `grazing_edge`, `side_slope`, `gate_frame`, `temple_walk` | see §6.4 — **not a single baseline** |
| **P10** | scene10 | full preset set + `reversal`, `through_treads`, `broken_rail`, `leaf_edge`, `from_below` | see §6.4 |

Both scenes' mise-en-scène cuts are the diagnostic ones and must be in the pilot: for 07,
`stone_rhythm` is the only cut that reads the course structure at close range and `gate_frame` is the
**only** cut where the roof cluster and the wooden pole exist at all (§0.2); for 10, `through_treads`
and `broken_rail` are the two cuts that read the railing section, which is the whole point of S3-8.

## 6.4 Regression adjudication — the 5-cut round trap

`redteam_w3_window1.md` §5.3 `[cite]`: *"`260731_w3_cb2` has 5 cuts; the retired `260730_w2d_fix` has
13. A naive 13-cut GATE-2 comparison against the new baseline will emit **8 MISSING FAILs per pilot
scene** … the comma fallback selects whole rounds, it does not mix per-cut."*

**S3's two scenes are on opposite sides of that trap, which makes it worse here than anywhere else in
the wave** `[measured]`:

| Scene | Latest round on disk | Cuts | Contains CB-2's scene edits? |
|---|---|---|---|
| **scene07** | `look_check/scene07/260731_w3_cb2` (`round_stamp.json`: `git_head c2676d6`, `cuts 5`, `NEGOBS_VIEWS = preset_h0.3_d2,preset_h0.3_d5,preset_h0.3_d10,preset_h0.9_d2,preset_h0.9_d5`) | **5** | **yes** |
| **scene10** | `look_check/scene10/260730_w2d_fix` | **13** | **no** — CB-2 changed scene10 (`11d1e56`, +29/−23 lines, 12 → 4 lobes) and scene10 was **not in CB-2's pilot set** (pilots were 03 · 07 · C2 · 01) |

Two consequences the executor must plan for:

1. **scene10 carries an unrendered CB-2 delta.** Its newest image predates its current code. Any
   `260730_w2d_fix → CB-S3-10` diff therefore contains **CB-2's leaf-lobe change plus the archetype
   rebuild, entangled**. Fix: render **one clean intermediate round of scene10 at HEAD before S3-8**
   (5 cuts is enough — match `260731_w3_cb2`'s view list exactly so the two scenes share a comparison
   basis), stamp it, and use *that* as the rebuild's baseline. Without it the rebuild inherits an
   unattributed delta and the CB-2 F3 work for scene10 stays unverified for the rest of the wave.
2. **Never compare 07 and 10 against "the baseline" as if it were one thing.** Per
   `redteam_w3_window1.md` §5.3's action: state in the round stamp which baseline each pair uses, or
   stamp the S3 round as a fresh full baseline in one step and say so. A `regression_check` run without
   `--only` across both scenes will produce MISSING FAILs that are an artefact, not a regression.

**Expected true regressions, declared in advance** (so a reviewer can tell signal from artefact): both
rebuilds are *intended* to move every pixel of the stair. `FRAME` deviations on every cut are the
expected result, not a failure. The gates that still mean something are **DARK / BLOWN / OCCL** and the
`near_ground_stats` band — those must not move for reasons other than the declared geometry change.
`ori_axis` is **advisory, never a gate** (§6.3 of the execution spec).

## 6.5 Self-check additions

Both scenes already print a SMOKE table (`scene07:702-…`, `scene10:692-…`). Additions, in the house
style (`scene05.podium_step_selfcheck` / `scene09.roof_normal_selfcheck` / the new `spiral_selfcheck`):

**`stone_course_selfcheck()` — scene07**

| Assertion | Threshold | Why |
|---|---|---|
| open-slope fraction = Σ(course-to-course gaps > 0) / run | **0.000** | A2 — the headline defect, currently **0.340**. With the `ov = 0.12` back-overlap this is 0 by construction, so assert it rather than budget it |
| widest visible within-course joint | **≤ 0.060 m** | §1.A.1-1 |
| every course covers the walk line `\|y\| ≤ foot_half` | 100 % | already checked per stone (`:728`); must survive the course rewrite |
| no slab overhangs air: each slab's base ≥ the course below's top | 100 % | A9 — bedding |
| rise table min/max/mean/spread | inside the declared band | A3 |
| exit step at `x = 12.2` | **labelled up-step**, magnitude printed | GT-14 rule (b) |
| kerb boulder clearance from the walk line | `\|y\| ≥ foot_half + 0.10` | GT-15 — a boulder must not stand in the walked corridor |
| moss coverage fraction by zone | printed, not asserted | §4.1 — a reported quantity so 통람 can judge it |

**`deck_module_selfcheck()` — scene10**

| Assertion | Threshold | Why |
|---|---|---|
| **no two flights share a plan footprint** | overlap area = 0 | C1 — the de-stacking is the fix; assert it or it will regress |
| 2R+T | inside the declared outdoor band | C2 |
| clear width between railings | **1.500 m ± 0.010** | C3; `[law]` SANJI-183 caps forest-land trails at 1.5 m |
| **2R + T** | **∈ [0.600, 0.650]** | `[law]` KCS 34 50 10 3.2.8(3) — assert the window, print the value |
| riser/tread uniform over every flight | true | `[law]` same clause: *"전 구간에 걸쳐 동일"* |
| baluster clear gap | **0.110 m ± 0.010** | `[ref]`; F-3 — no statute binds it, so the check exists to make the number visible, not to enforce a law |
| every baluster plumb (not raked) | true | `[law]` KCS 34 50 10 3.2.6(3) |
| baluster clear gap | ≤ the child-safety limit (§4.2) | C9 |
| total drop | **= 6.600 m exactly** | §9 P-2 frozen |
| `broken_landing` bay still missing its rails, posts still present | true | §9 P-2 frozen |
| leaf band still lands on treads 1–2 of flight 0 at the **new** riser | true | GT-18 |
| landing3 top vs lower ground proud | `0 < proud ≤ 0.05` | already checked (`:754-757`); must survive |

## 6.6 `placement_lint` expectations

`scripts/placement_lint.py` + `Docs/briefs/placement_rules_v1.yaml` (T1). Neither scene has a
`PLACEMENT` block today; adding one is *additive and geometry-free* (§10.4), and both scenes need one
because both gain or move furniture-class objects.

| Check | scene07 expectation | scene10 expectation |
|---|---|---|
| **LINT-1** tree ≥ 1.00 m from `kerb_lines` | no kerb line in a temple approach — declare **none**, so the check is vacuous | same |
| **LINT-2/3** route pitch 6–8 m, bearing ± 0.5° | 07's `pines` are a **courtyard group**, not a street row — declare as a group, **not** a `route`, exactly as X4 did for scene13's apartment planting (`[cite]` §1.2) | 10's `trees` are a park scatter, not a route — same treatment |
| **LINT-4** one species per route | consumes K4(b); 07's declared species per §10.2 (**Chinese_Juniper** for the courtyard group) | 10's per §10.2 |
| **LINT-7** furniture yaw ∈ declared anchor bearings ± 0.5° | the **kerb boulders are not furniture** — a boulder has no build axis, exactly like the `build_tree` yaw exemption (§12-15). Declare them exempt in the rules file, or LINT-7 will fire on every boulder | the **capped newel posts are furniture** and must be at the deck bearing; the lattice bay likewise |
| **LINT-8** no `rotz ≠ 0` on patch/stain | 07 has none; currently **0 violations** library-wide after CB-2 (295 → 0) | same |
| **LINT-10** any `jitter=` kwarg > 0 | **watch this one**: A7 keeps a capped ±3.0° per-slab yaw. If it is expressed as a `jitter=`-named kwarg it trips LINT-10. Express it as the adopted `jyaw=3.0` convention of `build_worn_stone_stairs` (`scene_common.py:1909`), which J-14 already exempted `[cite]` §1.2 | no per-instance jitter survives in the deck |
| **LINT-7-static** | — | after S3-1, `sceneC2` contributes **0**; the library total goes 5 → 1 (S4's `sceneN5:386` remains) |

## 6.7 Interaction with S3's other owed items

| Item | Status | Interaction with the rebuild |
|---|---|---|
| sceneC2 4 inert jit sites | **owed**, S3-1 | none — different file; land first |
| scene07 24-gon chord polish | **owed**, S3-2 | **direct** — S3-6 moves the same masks; land the polish first so it is attributable |
| F2 rock scatter / F3 decal boundary (03 · 07 · 10 · D3 · C2) | **landed at CB-2** (`11d1e56`) | do not redo. 07's 9 lobes and 10's 4 lobes are the CB-2 product; the rebuild re-sites them, never re-rectangularises them |
| 03-A…03-D, E3 D3 fence, B2a, B3, N-A7 (12) | separate S3 rows | file-disjoint; no ordering constraint |
| P-13 kerbless confirmation for 03 · 12 | parked on evidence | unrelated to 07/10 |
| **scene10 unrendered CB-2 delta** | **newly identified here** | §6.4-1 — must be rendered and stamped before S3-8 |

---

# 7. Hard constraints *(brief item G)*

These are not recommendations. An implementer who breaks one introduces a regression that the gates
will not necessarily catch.

| # | Constraint | Source | How it is checked |
|---|---|---|---|
| **H1** | **No humans. No vehicles.** In either scene, in any cut, in any backdrop, at any distance. G7's monk is composition reference only | `w3_execution_spec_v1.md` §12-10; user, standing | prim-name grep in the pre-flight; `ground_kit.py:46` already lists person/vehicle objects as a **forbidden API** |
| **H2** | **No nosing strip on scene07.** `cue_nosing = False` (`scene07:152`) stays False; `build_nosing` (`scene_common.py:1661`) is never called from 07 | RF-5 `[cite]` §10.7 + 편의증진법 시행규칙 별표1 제8호 마.(2); **and now primary** `[law]` KFS-TRAIL 특별시방서 13-2 나 (p.165): *"거친 면을 발판으로 미끄러짐을 방지한다"* — the rough stone face **is** the statutory anti-slip treatment | SCENE_CONFIG assertion in SMOKE |
| **H3** | **Tactile stays default-OFF** in both scenes. Do not switch it on, do not add a pad, do not "improve" it | §12-6; P-10 / P-12 are supervisor-owned | `cue_tactile` assertion; `TACTILE_SITES` registration is the only enabling path and neither scene is in it |
| **H4** | **Do not undo CB-2.** scene07's 9 carpet-mask lobes + 128 feather cards and scene10's 4 lobes are the CB-2 product (`11d1e56`). A lobe may **move**; it may never become a rectangle again, and `build_carpet_mask` may not be replaced by `BOX` | §1.9-2; `tonglam_v2` §2.13-2 | LINT-8 (0 violations library-wide today, down from 295); the §10.6 all-scene checklist item *"no decal has a straight edge that is not a construction joint, a saw cut or a kerb"* |
| **H5** | **NEW-SCENE design is banned.** 07 and 10 are rebuilt **in place**. No new scene, no split, no scene id reuse, no new scene file | standing user decision | file-list review at commit |
| **H6** | **Total drop frozen**: 07 `STAIR_DROP = 4.2` and `SIDE_DROP = 1.8`; 10 **6.600 m** | §9 P-2 verbatim; 07's terrain is derived from `path_z` | `stone_course_selfcheck` / `deck_module_selfcheck` (§6.5) |
| **H7** | **`rail.broken_landing = 0` survives** — the missing railing bay at landing 0 is scene10's negative-obstacle cue | §9 P-2 verbatim | `deck_module_selfcheck` |
| **H8** | **07's south lateral drop (`SIDE_DROP = 1.8`) is the scene's primary positive GT** and must not be softened, guarded, kerbed or railed. The kerb boulders go on the corridor shoulder at `y ±1.55`, **not** on the terrace edge at `y −1.7` | scene docstring `scene07:19-23`; `cue_railing = False` at `:147` is correct and stays | `stone_course_selfcheck` boulder-position assertion |
| **H9** | **No seasonal or event-specific element.** 07 = summer, 10 = late autumn, each pinned; the sanctioned exceptions are only `04/07 browned leaves · C1 snow · C2 leaves` | §12-7; `ground_kit.py:46` | the season audits, §1.B-S and §2.A.4 |
| **H10** | **`sct_debris_leaves_dry_*` may be placed in 10, not in 07** — `SCENE_SCOPE` permits `'07'` but 07 is summer. A scope permission is not a recommendation | `urban_kit` `SCENE_SCOPE`; H9 | `scene=` argument review |
| **H11** | **`veg_shrub_hedge_round_01` is in `REFUSED_IDS`** and `safety_railing_01` is in the 16 banned substrings — the loader raises on both. Do not route around `_check_banned()` | `urban_kit._check_banned()` | loader raises |
| **H12** | **Do not delete a working v6/v7 fix on the strength of one reference frame.** Specifically: 07's 3-tier staggered ridge + crest bands (a cure for a pure-black horizon), 07's sun `SUN_AZ_OFFSET = 206.5` (a cure for the gate shadow landing on the judged ground band), 10's waymarker/bench/pergola park anchors (a v7 framing fix), and 10's `SUN_AZ_OFFSET = 216.5` | scene docstrings `scene07:94-115`, `scene10:110-140` | change review |
| **H13** | **No atmospheric perspective** to hide far detail | §12-8 | — |
| **H14** | **Do not re-litigate the D-5 rock prop or the manhole silhouette.** W2 F2/F3 closed both. What is in scope here is rock **placement** (no dark sink-rings), not the prop | §12-11 | — |
| **H15** | **Signature-preserving changes only** in any shared builder S3 touches. A signature change is a 33-scene edit and is not authorised to S3 — and in practice S3 should touch **no** shared module: `scene_common` / `ground_kit` belong to K4 / K1 | §6.2-K4(c); §4.2 file ownership | file-ownership check at commit |
| **H16** | **`gate_frame` is not a judged frame.** Effort spent there is real but low-yield. Do not trade stair fidelity for backdrop fidelity | §0.2 | — |

---

# 8. Open questions requiring a supervisor ruling

Ordered by how much they block. **Nothing in §6.2's commit sequence past S3-2 should be cut before
OQ-1 … OQ-3 are answered.**

**OQ-1 — scene07's autumn ground under a summer canopy: which way does it resolve?**
The corridor and all three terraces are bound to `leaf_ground`, an **autumn** texture
(`scene_common.py:121-123`, *"Fallen-leaf ground (C2)"*), while the canopy, grass and moss are summer.
G7 is unambiguously summer. **Recommendation: re-bind the corridor and terraces to a summer forest
floor and keep `leaf_ground` only for the margin lobes** (§4.1-5). The cost is that 07's terrace
albedo changes, and the terrace is the face the grazing cut judges (GT-17). The alternative — repin
07 to autumn — contradicts G7 and would also require deleting the fern/moss story, so it is not
recommended, but it is cheaper. **The supervisor owns the choice because it moves a judged surface.**

**OQ-2 — scene10's open risers vs G10's closed risers.**
Hazard cue (2) in the scene's own docstring is *"Open risers — the flight below and the ground show
through between the timber treads. With no tread/riser light-dark pair, the nosing cut line never
forms"* (`scene10:21-23`), realised by `build_open_riser_stairs` (`:1233`) and read by the
`through_treads` cut. **G10 shows closed riser boards.** Three ways out:
(a) keep open risers and accept the divergence from G10 — the cue is a declared dataset feature and
G10 is one frame; (b) close the risers and move the concealment cue onto the leaf-covered treads
(cue 3), which G10 *does* support; (c) split — closed risers on the flights that appear in the grid
cuts, open on one flight that `through_treads` looks at, which is real (Korean deck stairs are built
both ways) but is also the kind of scene-internal inconsistency the wave is trying to remove.
**Recommendation: (a) — keep the open risers.** The dataset cue outranks one reference frame, and the
emergency-stair read comes from the *stacking and the round railing*, not from the risers.
**Do not resolve this unilaterally.**

**OQ-3 — the leafless-tree mechanism is a `scene_common` edit, and S3 does not own `scene_common`.**
§3.4's fix (a scene-gated `BARE_SUBPRIMS` table + a `_deactivate_seasonal` call in `build_tree` before
`SetInstanceable(True)`) lands in `/scene_common.py`, which is **K4's file** (§4.2), and `scene_common`
is exclusive to WINDOW 2, which has already closed. Either K4 re-opens for a small additive change, or
scene10's bare trees wait for WINDOW 5, or scene10 ships with green trees in an autumn frame — which
is the defect this document was written to remove. **Recommendation: a K4 micro-commit, since the
change is additive, signature-preserving and gated by a scene id.**

**OQ-4 — does G10 close the `park_trail` evidence gap for GATE-3?**
`w3_intake_06_10.md` §9.2 requires **n ≥ 8 photos** of 목재 데크 계단 before scene10 is executed;
`Docs/reference_photos/w3/park_trail/` currently holds **3**. G10 is a *generated* image, not a
photograph, and §10.6's T-3 checklist plus X3's rule (*"every verdict names a photograph. A verdict
with no photo name is not a v3 verdict"*) both assume a photo panel. **Recommendation: G10 governs
the design; the photo panel is still owed for 통람 v3.** T2 should top the panel up to n ≥ 8 before
GATE-3, and the panel does **not** block CB-S3-10.

**The gap is now closable — the route was scouted this session.** Hard-verified, open-licence,
individually confirmed Korean timber deck stairs (**4**, URLs only, nothing downloaded):
Commons `File:Wooden_staircase_steps_in_the_forest_of_Hallasan_Park_Eorimok_Trail…jpg` (CC BY-SA 4.0)
· `File:Wooden_staircase_along_Yeongsil_Trail…jpg` (CC BY-SA 4.0) · 산림청 사진자료실 *"검마산자연휴양림
조성(목계단)"* (`forest.go.kr … nttId=82624`, KOGL badge, type not printed) · 공유마당 *월곡산림욕장
데크로드* (`gongu.copyright.or.kr … wrtSn=12248203`, **KOGL Type 1**).
The volume route is **공유마당 `kwd=목계단`: 145 hits / 86 photos, of which KOGL 107 · CC BY 32**, plus
the KOGL Type-1 한국관광공사 관광사진 API (`data.go.kr/data/15101914`, ~100k photos). Both need a
human/authenticated pass to confirm stair content, which is why this is a T2 job and not a blocker.
**Dead ends, recorded so nobody repeats them**: kogl.or.kr's own image search returns 0 for every
query param tried · knps.or.kr 경관사진 carries no KOGL badge · 국립공원 사진전 winners are explicitly
copyright-retained · news/mediahub.seoul.go.kr is predominantly **KOGL Type 4** (no commercial, no
derivatives) · Commons MediaSearch returns **zero** for "데크 계단".
**And a better-than-photos asset was found**: the two 국립공원공단 open CSV inventories
(**1,183 stair records + 1,805 railing records**, KOGL 제한 없음, with dimensions) close the
*dimensional* half of S10-A outright — §4.0 F-2 and F-3 are built on them. The photo panel is now
owed only for the **eyes** half of the T-3 checklist, not for the numbers.

**OQ-5 — CLOSED by research; recorded because it reverses two earlier proposals.**
The question was which authority sets scene10's railing height and baluster gap. **Answer: none of the
building-family ones.** A trail/park deck stair is not a 건축물 and not a 주택단지 facility, so
PIRAN-15 (85 cm handrail, 32–38 mm grip) and HOUSE-18 (1.2 m guard, ≤ 100 mm 간살 안목) **do not
bind it**, and KCS 34 50 10 3.2.6 sets no numeric height at all — it fixes only the *geometry*
(balusters plumb to the tread plane, 3.2.6(3)). The binding evidence is therefore built reality:
`[data]` KNPS-RAIL n = 1,227 → **median 1.10 m, 71 % in 1.0–1.2 m**. §4.2-2 is set to **1.10 m** and
a **0.110 m clear gap**, which reverses this document's own earlier 1.20 m / ≤ 100 mm proposal *and*
the intake's. **The supervisor is asked only to confirm the reversal, not to adjudicate a conflict.**
Residual `[assumed]`: the built pitch of balusters on 방부목 trail railings (100–140 mm c/c) has no
primary source; 150 mm is taken from G10 and is inside no statute either way.

**OQ-6 — Option A or Option B for scene10's de-stacking?** (§4.2-4)
Option A rebuilds the terrain and matches G10; Option B keeps the terrain and half-fixes the read.
**Recommendation: A**, because the intake's diagnosis (*"a park deck switchback travels across the
slope"*) is a terrain diagnosis. But A roughly doubles the scene10 work and adds a second large GT
row, so the supervisor owns the budget call.

**OQ-7 — scene07 course count.** §4.1-1 proposes **28** courses (rise 0.150, tread 0.428) against the
intake's parked candidate of 26 (rise 0.162, tread 0.47), which was sized on 장대석 proportions that
G7 refutes. The change is small and defensible; it is flagged only because the parked row named 26 and
a reviewer comparing the two documents will notice.

**OQ-8 — two procurement rows, neither blocking.**
**G1** — a Korean tile-roof / hanok asset. The catalogue has **zero**; the crest cluster is procedural
either way (§4.1-4). Worth one line in the procurement queue only because 07 is not the only scene
that would use it. **G5** — one CC0 weathered/silver-grey plank texture set. Every wood map in the
repo is warm or dark brown, and G5 is the only element of scene10 where the interim (a cool tint on a
warm map, §4.2-3) is visibly a workaround rather than a fix. **Neither blocks.** `[ruled 07-30]` §1.11
precedent: *"record as an open procurement row, do not block."*

---

# 9. Evidence ledger

## 9.1 Target images (primary, `[ref]`)

| ID | Path | Provenance | Use |
|---|---|---|---|
| **G7** | `Docs/reference_photos/Generated Image - Scene07.jpg` | user-supplied, generated | fidelity target, scene07 |
| **G10** | `Docs/reference_photos/Generated Image - Scene10.jpg` | user-supplied, generated | fidelity target, scene10 |

Both are **generated images, not photographs**. They are authoritative for *design* by user
instruction; they are **not** a substitute for the photo panels that GATE-3 / 통람 v3 require (OQ-4).
Neither is redistributed by this document.

## 9.2 Harvested photographs (secondary, `[photo]`)

`Docs/reference_photos/w3/temple_precinct/` — 12 files, Buseoksa-dominated, licence rows in the
directory's own `LICENSES.csv`. Corroborates 자연석 slab courses and moss zoning, but the Buseoksa
courtyard stairs are **장대석**, i.e. the *other* archetype; use with care.
`Docs/reference_photos/w3/park_trail/` — **3 files** only; the n ≥ 8 gap of `w3_intake_06_10.md` §9.2
is open (OQ-4). Intake photo IDs P07-1 (CC0), P07-2 (CC BY-SA 2.0), P07-3 (CC BY-SA 4.0), P10-1
(CC BY-SA 2.0) remain the reference set of record; the BY-SA rows are URL-only per T2's rule.

## 9.3 In-repo documents consumed `[cite]`

`Docs/briefs/w3_execution_spec_v1.md` §1.1 · §1.2 · §1.3 · §1.7 · §1.8 · §1.9 · §1.11 · §3.4 · §4.2 ·
§4.3 · §5.1 · §5.2 · §6.1 · §6.2 · §6.3 · §8 · §9 (P-1, P-2, P-13, P-14) · §10.2 · §10.4 · §10.5 ·
§10.6 · §10.7 (RF-2, RF-5) · §12 · §13 ·
`Docs/surveys/w3_intake_06_10.md` §0 · §1.0 · §1.1 (J5–J7) · §4 (S07-A) · §7 (S10-A) · §8 · §9 ·
`Docs/audit_v4/gt_changes_w3.md` §0 · §1 · §2 · §3 (GT-6) · §4 · §8 ·
`Docs/reports/redteam_w3_window1.md` §2 · §3.1 · §5.1 · §5.2 · §5.3 · §5.5 ·
`Docs/reports/tonglam_v2.md` §1 rows 07 / 10, §2.4, §2.13-2, §3 (F2/F3) ·
`assets/urban_manifest_w3.json` · `assets/veg_manifest_w2.json` · `urban_kit.py` · `building_kit.py` ·
`ground_kit.py` · `scene_common.py` · `scenes/main/scene07_temple_stone_path.py` ·
`scenes/main/scene10_park_deck_switchback.py` · `scenes/batch1/sceneC2_leaf_stairs.py`.

## 9.4 Numbers recomputed this session `[measured]`

Analytic, from the authoring code — `pxr` is **not installed on this machine**, so nothing here is
measured off a built stage. Re-confirm on usd-core before any of it is cut into code, exactly as T3
was required to do for S06-A.

| Quantity | Value | How |
|---|---|---|
| scene07 stone depth | 0.270 / 0.384 / mean 0.325 m | `stone_layout()` re-run with `seed 707`, scale factor `k = 0.9613` |
| scene07 inter-stone gap | 0.050 / 0.276 / mean 0.177 m, **Σ = 4.082 m** | same |
| **scene07 gap fraction** | **34.0 % of the 11.99 m run** | `4.082 / 11.99` |
| scene07 rise | 0.111 / 0.232 / mean 0.174 m, spread 0.121 | `stone_metrics()` |
| scene07 slab width | 0.510 / 1.036 / mean 0.755 m | `stone_layout()` |
| scene07 `cy` offset | −0.247 … +0.130 m | same |
| scene07 thickness | 0.129 – 0.240 m | same |
| scene07 entry / exit step | **+0.002 / +0.201 m** | `stone_metrics()` |
| scene10 2R+T · pitch | **0.630 · 28.81°** | `PARAMS["flights"]` |
| scene10 flight run / drop / total | 3.00 / 1.65 / **6.60 m** | `compute_flights()` |
| scene10 plan footprint | `x [−1.4, 4.4]` = 5.8 m × `y` 2.8 m | `compute_flights()` + `band()` |
| scene10 inter-flight clearance | 3.01 m | `2 × 1.65 − 0.29` |
| scene10 balusters per flight side | **9 at exactly 0.300 m** | `nb = round(3.00/0.30) − 1` |
| grid preset cuts | **9** (h{0.3,0.9,1.8} × d{2,5,10}, pitch −10°) | `scene_common.py:3265` |
| scene07 baseline round | `260731_w3_cb2`, **5 cuts**, `git_head c2676d6` | `round_stamp.json` |
| scene10 baseline round | `260730_w2d_fix`, **13 cuts**, **pre-CB-2** | directory listing + `git show --numstat 11d1e56` |
| CB-2 delta on scene10 | **+29 / −23 lines**, never rendered | `git show --numstat 11d1e56` |

## 9.5 Korean standards and open datasets read this session `[law]` `[data]`

| Key | Document / dataset | Locator | Used for |
|---|---|---|---|
| **KCS-3450** | 조경공사 표준시방서 **KCS 34 50 10 조경구조물** (+ 34 50 15), 국토교통부고시, 시행 2024-12-16 | `law.go.kr/LSW/admRulLsInfoP.do?admRulSeq=2100000251100`; full text via 나라장터 첨부 | **3.2.8(3)** 2R+T = 600–650 mm, uniform · **3.2.8(2)** landing set on site · **3.2.6(3)** balusters plumb to the tread plane · **3.2.12(2)** railing when height ≥ 2 m · 34 50 15 lumber classes (KS F 1519), 가압식 방부처리 KS F 2219, 방부제 KS M 1701 |
| **KFS-TRAIL** | 산림청 「등산로 정비 매뉴얼」 (2010, 194 pp) | PDF hosted by 서울시 푸른도시여가국, `news.seoul.go.kr/env/archives/527421`. **Text layer is un-extractable** (QuarkXPress CID) — every quote was read from rendered page images. Cited by **book page** (PDF page = book page + 6) | p.70 rise ≤ 150 / tread 250–300 / 2H+B 600–700 · 표 3-6 (p.71) and **〈표 13-1〉 (p.166)** slope→H/B tables · **13-2 가/나/다 (p.165)** 자연석 300 × 300 × 250, 고임돌·틈메우기돌, 거친 면 발판, 표 13-1 applies to all stair types · 13-1 stone stair at slope ≥ 15 % · **12-3 마 (p.165)** 300 mm ground-rise landing trigger · 17-2 (p.169) post embedment 50–100 mm · 그림 3-20…3-32 (p.72–78) member sections · p.72 apron 1,000 / ≥ 500 mm |
| **LDS-2016** | 조경설계기준 §5.9 경사로 · §5.10.2 계단 | 한국조경학회 / 국토교통부 | **5.10.2(3)** landing every 2 m of rise, width ≥ the stair's 유효폭 and ≥ 1,200 mm · **5.9(4)** 1.5 × 1.5 m landing |
| **SANJI-183** | 산지관리법 시행령 제18조의3④ [별표 3의3] 제4호 다 (개정 2020-03-03) | `law.go.kr` official PDF | 숲길 width **≤ 1.5 m**, with the 교통약자 and 휴식·대피 장소 exceptions |
| **KNPS-STAIR** | 공공데이터포털 「국립공원공단_탐방로상 시설-계단」 (2025-08-06), 1,183 rows, **KOGL 이용허락범위 제한 없음** | `data.go.kr/data/15136189/fileData.do` | built stair width distribution; the 155 "데크"-named rows |
| **KNPS-RAIL** | 공공데이터포털 「국립공원공단_탐방로상 시설-난간」 (2024-09-11), 1,805 rows, KOGL | `data.go.kr/data/15136187/fileData.do` | built railing height distribution (n = 1,227 after filtering) |
| PIRAN-15 | 건축물의 피난·방화구조 등의 기준에 관한 규칙 제15조 | `law.go.kr` | **cited only to establish that it does NOT bind** either scene |
| HOUSE-18 | 주택건설기준 등에 관한 규정 제16·18조 | `law.go.kr` | same — the ≤ 100 mm 간살 안목 rule lives here, i.e. in 주택단지, not in a park |
| SMCS-34 | 서울특별시 전문시방서 SMCS 34 조경공사 | 나라장터 첨부 | 방부제 표 2.4-1 (**CCA is absent from the approved 수용성 list**), 처리종별 표 2.4-2 (default 3종) |

**Two caveats the executor must carry.** (1) `KNPS-RAIL`'s height column is literally named
**`폭높이` (width/height)**, so a minority of rows may record width; the population median (1.10 m) is
solid, the 데크/목재 subset medians are weaker. (2) `KFS-TRAIL` contains an **internal disagreement**:
표 3-6 caps rise at 150 mm while 〈표 13-1〉, the worked design table in the same manual, uses 200 mm at
35° and 170 mm at 30°. Real trail decks therefore legitimately run to R = 200 mm — which is why
scene10's current 0.165 is not a defect.

---

## 10. One-paragraph summary for the commit message

scene07's stone stair is the wrong archetype and 34.0 % of its run is bare slope between pavers; G7
settles it as 자연석 계단 — courses of 2–4 bedded slabs with ≤ 60 mm joints, zoned moss, a boulder
kerb and a fern-and-canopy summer margin — and the scene is currently an autumn ground under a summer
canopy. scene10 reads as an apartment scissor stair because four flights stack inside a 3.0 × 2.8 m
masonry shaft with round-section railings at a 300 mm baluster pitch; G10 settles it as a traversing
timber switchback with square capped newels, 150 mm balusters, a lattice bay, deep landings and a
rest platform, in a leaf-off frame where our scene still carries 47 green vegetation objects — and
the Korean standards refute the intake on the two numbers it was surest of: `2R+T = 0.630` is legal
(KCS 34 50 10 3.2.8(3) sets 600–650) and 1.5 m, not 1.8 m, is both the statutory cap on forest land
and the mode of 155 real national-park deck-stair records. Both
stairs are walked GT surfaces, both are FULL re-caches, and asset coverage is ~70 % / ~80 % with the
leafless-tree problem solved at zero procurement cost by deactivating `/Root/leaves` on three
vegetation USDs whose branch armature lives in the trunk prim.
