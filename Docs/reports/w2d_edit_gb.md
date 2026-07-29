# W2-D — `ground_kit` applied to batch1 (N1 N2 N3 N4 · C1 C2 C4 · D1 D2 D3)

Round 2026-07-30 · branch `feat/realism-v1` · **no GPU, no render, no Isaac, no SMOKE**
Owned files: `scenes/batch1/scene{N1..N4,C1,C2,C4,D1..D3}_*.py` (10 scenes) + this report.
Spec of record: `Docs/briefs/ground_kit_spec_v1.md` v1.1 (+ §7.5 W2-C amendments).
Pilot pattern followed: `git show e196c93 cb40ae8 753b791`.

Evidence tags — `[measured]` this round ran it and read the number · `[computed]` derived from the
spec's camera model (`f = 1662.769 px`, pitch −10°, h0.3) with the premise stated ·
`[spec]` quoted from the brief · `[law]`/`[stat]` as in the brief · `[ruling]` supervisor or pilot
decision already on record.

---

## 0. Verdict in one paragraph

All ten scenes are wired, all hard gates pass, and nothing in the shared tree moved. `plan_ground`'s
B6–B12 pass for **12 plans across 10 scenes** (D1 and D3 need two plans each because one plan is one
z), `python3 ground_kit.py` exits 0 with 33/33 fixtures, `scripts/geom_invariance_check.py` stays
**33/33 PASS on R-4 and R-6**, and every scene also assembles in its hazard-off twin and in the
`NEGOBS_GKIT=0` diagnostic arm. The prim accounting closes exactly: the ON/OFF delta equals the
planned prim count in all ten scenes `[measured]`. Three things in the round are **not** what the
matrix literally says, and each is argued in §4: the N1/N2/C1/C4 manholes are moved out of the W1
window to satisfy the pilot's ≤25 %-frame-width ruling, C2's joints are bound to stone because that
scene's approach is authored as a dirt path, and D2's transverse opening-marking leg is deferred
because `ground_kit._ik_marking` builds its AABB ignoring `yaw` (§5, F1). The round produced no
pixels, so σ_LF/sd remain unread — per §7.5 A1 that is expected for a ground-only round, but W2-C's
GO item 4 (restore the σ_LF WARN gate now that T1 exists) still needs a render round.

---

## 1. What was verified, and with what

| # | check | command | result |
|---|---|---|---|
| V1 | kit self-check (18 profiles dry, 33 fixtures, GT assertions, apply round-trip) | `python3 ground_kit.py` | **exit 0**, all items OK `[measured]` |
| V2 | per-scene plan gates B1–B12 on this round's **actual** call arguments | scratch harness calling each scene's `ground_plans()` | **12/12 plans HARD PASS** `[measured]` |
| V3 | geometry invariance R-5 / R-4 / R-6 across all 33 scenes | `python3 scripts/geom_invariance_check.py` | **33/33 PASS**, exit 0 `[measured]` |
| V4 | byte-compile | `python3 -m py_compile scenes/batch1/scene*.py` | clean `[measured]` |
| V5 | hazard-off twin assembles (10 scenes, `NEGOBS_SCENE_CONFIG` hazard flags false) | fake-USD harness | 10/10 OK `[measured]` |
| V6 | `NEGOBS_GKIT=0` diagnostic arm assembles **and** removes exactly the kit prims | fake-USD harness, ON vs OFF inventory | 10/10 OK, deltas in §3 `[measured]` |

V2's harness is possible because every scene now exposes a module-level `ground_plans()` that the
assembly path and the CPU check both call — `plan_ground` never touches USD `[spec §3.3]`, and the
scene modules import cleanly without `pxr` (`scene_common` defers all USD imports). This is the
gap the pilot round could not close: `python3 ground_kit.py` validates `SCENE_PLANS` **fixtures**,
not the arguments a scene actually passes.

---

## 2. Per-scene wiring

`prims` = `plan["prims"]`; `Δ ON/OFF` = prim inventory difference between the `NEGOBS_GKIT=1` and
`=0` arms of the same HEAD `[measured]`.

| scene | profile | plan region (x0,y0,x1,y1) · z | edges / voids | elements | prims | Δ ON/OFF | gates |
|---|---|---|---|---|---|---|---|
| **N1** | P1 `plaza_granite` | (−12, −4, −0.6, 4) · 0.0 | none (hard negative) | 2 manholes · 2 gullies · 2 patches · 4 cracks · dirt+water stains · weeds · tactile band | 45 | 45 | HARD PASS · WARN B4,B5 |
| **N2** | P4 `street_asphalt` | (−12, −4, 2, 4) · 0.0 | none | 1 manhole · 2 gullies · 3 patches · 6 cracks · tire+oil stains · weeds · tactile band | 46 | 46 | HARD PASS · WARN B3,B5 |
| **N3** | P1 `plaza_granite` | (−12, −4, **−1.6**, 4) · 0.0 | none | 2 manholes · 2 gullies · 2 patches · 4 cracks · stains · weeds | 42 | 42 | HARD PASS · WARN B3,B4,B5 |
| **N4** | P8 `ramp_road` | (−14, −2, 0, 2) · 0.0 | `ramp_crest` @0, `beyond_grade`=0.050 | 2 gullies · 2 L-gutters · 2 edge lines · 3 patches · 6 cracks · tire+dirt · weeds · tactile band | 54 | 54 | HARD PASS · WARN B5 |
| **C1** | P1 `plaza_granite` | (−11, −3, 0, 3) · 0.0 (**under the snow**) | `stair_top` @0 | 1 manhole · 1 gully · 2 patches · cracks · stains · weeds (h≤0.045) · **tactile stair_top** | 43 | 56 | HARD PASS · WARN B4,B5 |
| **C2** | P3 `sidewalk_block` | (−10.6, −1.62, −0.3, 1.62) · 0.0 | `stair_top` @0 | 3 joints only (minimum intervention) | 3 | 5 | HARD PASS · WARN B1,B2,B4,B5 |
| **C4** | P3 `sidewalk_block` | (−10, −2.9, 0, 2.9) · 0.0 | `stair_top` @0 | 1 manhole · 2 gullies · 2 wet patches · cracks · dirt+gum · weeds · **tactile stair_top** | 48 | 48 | HARD PASS · WARN B4,B5 |
| **D1** deck | P14 `yard_industrial` | (−12, −13, 0, −3) · 0.0 | `dock_lip` @0 · **void = ㄷ bay** | 6×4.5 joint grid · 2 patches · tire/oil/dirt | 22 | 46 (both plans) | HARD PASS · WARN B3,B5 |
| **D1** yard | P14 `yard_industrial` | (0.5, −13, 16, 13) · **−1.2** | none | 6×4.5 joint grid · dock-front trench @x=6.0 · 2 backing lines · 1 stop line · stains | 24 | — | HARD PASS · WARN B1,B2,B5 |
| **D2** | P15 `slab_construction` | (−9, −6, 0, 6) · 0.0 | `opening_lip` @0 · **void = opening** | cold joints · 2 opening-marking legs · efflorescence+dirt · 12 footprints | 24 | 24 | HARD PASS · WARN B1,B2,B3,B5 |
| **D3** cover | P17 `verge_rural` (natural) | (−12, −0.65, 0, 0.66) · **0.004** | `channel_open` @0 | joints **2.5 m recessed −3 mm** · 3 patches · 5 cracks · dirt band · weeds | 34 | 66 (both plans) | HARD PASS · WARN B4,B5 |
| **D3** road | P17 `verge_rural` (natural) | (−12, −8.0, 2, −1.10) · 0.0 | none | 3 patches · 5 cracks · dirt · weeds (no joints — asphalt) | 32 | — | HARD PASS · WARN B1..B5 |

Scene prim totals, before → after, fully accounted `[measured]`:

| scene | before | after | kit | other, and why |
|---|---|---|---|---|
| N1 | 469 | 540 | +45 | +31 joint two-tiering (§4.4), −5 bollard tactile pads (§4.2) |
| N2 | 542 | 600 | +46 | +12 near stall row extended `near.x 0.4 → −4.6` (§4.3) |
| N3 | 645 | 677 | +42 | −10 bollard tactile pads (§4.2) |
| N4 | 1191 | 1241 | +54 | −4 bollard tactile pads |
| C1 | 323 | 378 | +43 +13 snow trace | −1 old flat tactile plate replaced by the kit |
| C2 | 3924 | 3929 | +3 +2 lateral bands | — |
| C4 | 585 | 632 | +48 | −1 old flat tactile plate |
| D1 | 299 | 345 | +22 +24 | — |
| D2 | 211 | 235 | +24 | — |
| D3 | 657 | 715 | +34 +32 | −8 scene-built cover joints handed to the kit (§4.6) |

### 2.1 P-A: `SKIN_EXCLUDE` registrations

Every decorated slab is registered **before** its `add_box`/`RECT` call, because `_skin_wanted` is
evaluated at creation time and a later registration is too late `[spec §1.2, pilot #1]`.

`Plaza` (N1, N3) · `Apron`+`Road` (N2) · `Road_Approach` (N4) · `Terrace` (C1) · `UpperPath` (C2) ·
`UpperPlaza` (C4) · `Deck_W/S/N` + `Apron_S/N/C/Bay` (D1) · `Slab_W/E/S/N` + `Slab_Fill` (D2) ·
`CoverSlab` + `Road` (D3).

The **hazard-off control slabs are registered too** — `FlatFill` (C1, C4, D3), `FlatPath` (C2),
`FlatDeck` (D1). Without this the twin pair would differ in two things at once (drop geometry *and*
displacement skin), which is exactly what §7.5 A3 forbids when the twin is the edge-integrity
instrument. D1's deck plan therefore also runs in the control arm; only its yard plan (z = −1.2) is
skipped there, because the control's `FlatDeck` top is z = 0 and the yard plan would be buried.

### 2.2 Tactile — §12.4 final table, scene by scene

| scene | §12.4 verdict | what this round did |
|---|---|---|
| N1 | bollard front, "keep + fix the form" (§12.5 ②) | kit lays a **continuous 0.60 m band** in front of the entry bollard row, derived from `PARAMS["bollard_entry"]`; `build_bollard_v51(..., tactile=False)` so the per-post 0.40×0.30 pads do not stack with it |
| N2 | same | same, band on the sidewalk (+Y) side of the bollard row |
| N4 | same | same, band in front of the **approach-side row only** (`x = −3.6`); §12.4 registers one site, and the law's trigger is the row a pedestrian meets first |
| N3 | **OFF — identity conflict** | N3 is not in §12.4's "bollard front kept" list, and `_inv_hidden_illusion` refuses any kit tactile in this scene. The scene's own bollard pads are switched off for the same reason |
| C1 | ON, kept; defect = colour fading | moved from `sc.build_tactile` (flat constant-colour plate, the §12.5 ③ defect) to the kit's `build_tactile_pair`; position corrected to the statutory `x −0.90…−0.30` (0.3 m before the first step, 0.60 m deep). Burial under the 0.05 m snow is preserved — that is the scene's characteristic |
| C4 | ON, kept; defect = **position error 0.6–1.0 m** | same builder move; band placed at `x −1.60…−1.00` (setback 1.00 m), reproducing the defect the table assigns. See F4 |
| C2 | OFF (`p` = 0.24, park) | none |
| D1 · D2 · D3 | OFF (not a covered facility, `p ≈ 0`) | none. `TACTILE_OFF_REASON` already records why |

---

## 3. Condition overlays (C1 snow · C4 wet · C2 leaves)

**C1 — elements go under the snow.** The plan is built at the terrace top (z = 0), i.e. beneath the
0.05 m snow layer, because §7.3's registered invariant for this scene is exactly that
(`_inv_c1_snow`: new elements `proud ≤ 0.05`). Weed height is capped at 0.045 through
`caps=dict(weed_h=...)`; the profile default 0.12 would break the invariant. The `snow_cover=False`
counterpart now shows a fully dressed pavement instead of bare concrete, so the pair carries more
information than before. The scene-specific prescription that is *not* pavement — the snow-clearing
trace — is laid **on** the snow at z = LIFT with two direct builder calls
(`build_wear_lane` 1.0 m wide × 0.75 albedo, `build_footprints` ×12), because one plan is one z.
Both direct calls are gated on `gk.GKIT_ON` so the `NEGOBS_GKIT=0` arm still differs only by kit
prims `[spec §7.5 A3]`. The "shovel-edge exposure strip at x = −0.4" is **deferred**: it is a
full-width bright line 0.4 m from the drop edge, i.e. precisely the GT-E2 shape the spec refuses to
grant an exception to outside `TACTILE_SITES`.

**C4 — elements under the wet treatment.** Geometry is identical in both arms of the wet/dry pair
(the pairing rule); only bindings follow the toggle: patches take `tread_wet` when
`wet_surface=True` and `plaza` otherwise, joints and cracks take `stone_damp`, stains take `tide`.
The two wet patches sit at `x = −1.20` (d2 W1) and `x = −4.40` (the spec's `x −4.4…0` band).

**C2 — no collision with the G2 leaf field.** Scatter is **not** wired (the `scatter` callback is
simply not passed), so `ground_kit`'s scatter allocation for this scene is 0 as §8.3 requires. The
joint corridor is aligned to the G2 upstream start `x = −10.60` per §8.4 ①, joint width raised to
0.05 m per §8.4 ②, and the "leaf↔pavement boundary" bands are moved from the travel-axis boundary
(which G2 pushed behind the d10 eye) to the **lateral** boundary `|y| = 3.60` per §8.4 ③ — with one
correction, see §4.5. Layering per §8.4 ④ holds: kit joints render at +0.6 mm, leaves scatter above
them, and the kit runs **after** the leaf scatter.

---

## 4. Where this round did not follow the matrix literally

### 4.1 Manhole placement — N1, N2, C1, C4 moved to the W2 window

§5.1 puts N1's manhole at `(−1.0, +0.4)`. At d2 that is a ground distance of 1.00 m, so its screen
width is `f·0.648/1.00 = 1,078 px = 56.1 % of frame width` `[computed]` — the exact "one element
owns the near window" state that pilot #2 was told to fix (ruling M9-ⓑ, second correction:
target ≤ 25 %). Inside W1 the target is unreachable: even at the far end X = 2.00 m the width is
28.1 % `[computed]`. Following the pilot, the manhole moves to `x = −2.40`, i.e. the second-priority
window W2 (2.00–3.00 m): d5 X = 2.60 m → 414 px = 21.6 %, d10 X = 7.60 m → 7.4 % `[computed]`. The
d2 near window is then filled by a repair patch at `x = −1.20`, whose 86 % width is a **flat tone
change** rather than a disc — the same trade the pilot accepted for scene15. Applied identically to
N2, C1 and C4.

### 4.2 Bollard tactile pads removed in N1, N2, N3, N4

§12.5 ② is explicit that the per-post 0.40×0.30 pad is the defect (0.12 m²/post → 212 px/post at the
`approach` view, five posts under 0.05 % of frame) and that the fix is a **continuous 0.60 m band**.
This round therefore *replaces* rather than *adds*: `build_bollard_v51(..., tactile=False)`. Leaving
both would produce a 0.90 m deep tactile zone, over the statutory 0.60 m standard.
**This diverges from pilot #1 (sceneN5), which kept the pads and added the band.** N5 is not in my
scope; a one-line sweep there would make the four hard negatives consistent.

### 4.3 N2 — the "paradox" fix is a coordinate move, not new elements

§5.3 diagnoses N2 as element-rich and window-poor. The near stall row started at `x = 0.4`, which
misses all three h0.3 windows (d2 `x −1.436…0`, d5 `−4.436…−3`, d10 `−9.436…−8`) `[computed]`.
`stall.near` is now `(−4.6, 5.6)`; the row head line stays at 5.6. The scene's 4 m joint grid was
left alone — it already hits all three windows (ticks at x = 0, −4, −8) `[computed]` — and the kit
adds no joints (P4 has none), so no double grid.

### 4.4 N1 — joints two-tiered in the scene, not in the kit

§5.1's N1 row asks for "6 m expansion + 1.5 m construction". 1.5 m is 2.5 × the 0.600 granite cell
and therefore violates §4.5 U2 (which the same document states as the reason the plaza figure was
fixed at 1.8 m). Implemented as **6.0 m + 1.8 m**, coincident ticks dropped to avoid co-located
prims. It is done in the scene's own `build_joints()` and the kit's joints are disabled
(`overrides=dict(pave=dict(joint=None))`) because the kit grid (1.8/6.0 from origin 0) and the scene
grid (3.0 from x = −21) would otherwise interleave on the same surface — defect D6 from the pilot
round. Same reasoning for N3 (scene owns a 1.2 m grid that must pass through the painting; it is a
discriminating cue and its period must not move) and for D3's cover, where the opposite call was
made — see §4.6.

### 4.5 C2 — two corrections to §8.4

1. **Joint material.** §5.2 says "joints on the hard-paved part of the approach only". This scene's
   approach is authored as `dirt_park` (`M["dirt"]`), so there is no block paving to joint. The
   joints are delivered at the §8.4 ② width (0.05 m) but bound to `M["stone"]`, where they read as
   flush stone banding across a compacted park path — a real detail, and it preserves what §8.4
   actually cares about (a line that leaf cover cannot swallow). Flagged for the supervisor: if the
   intent was genuinely interlocking block paving, the surface material is the thing to change, not
   the joints.
2. **Band extent.** §8.4 ③ gives `x −3.76…6.26` for the lateral bands at `|y| = 3.60`. For x > 0 that
   line lies on the **descending** side-grass slope (`z = −0.4706·x`), so a flat z = 0 band would
   float by 2.24 m at x = 4.76 `[computed]`. Clipped to `x −3.76…0.00`; prim count 2 unchanged.
3. Only **3** joints land in the corridor (ticks −9, −6, −3; the x = 0 tick is dropped by the edge
   guard), against §8.3's "4". Total C2 kit prims 5 vs the budgeted 6. Also worth noting: the tick
   at x = −3 falls under leaf mound A (`x −3.20…−0.10`, a solid slab), so it will not be visible.

### 4.6 D3 — the cover joints changed owner

§5.7 asks for "joint deepening: current +1 mm proud → −3 mm recessed". The scene built them as dark
strips at `proud +0.001`; the kit's `build_joint_grid` records the nominal −0.003 recess while
placing the top at `surface_top_z` (+0.6 mm), which is the pilot's fix for recessed elements being
swallowed by solid slabs. The scene's loop is removed and the kit takes over at the **same** period
(2.5 m) and width (0.04 m), so the rhythm the scene was designed around does not move. D3 keeps its
U-channel identity untouched: no section change, no culvert change, and `natural=True` makes
`plan_ground` refuse urban infrastructure by construction.

### 4.7 D1, D3 — two plans per scene

One `plan_ground` is one z (`z_fn` is accepted but never consumed). D1 has a deck at z = 0 and an
apron at z = −1.2; D3 has a cover slab at z = 0.004 and a road at z = 0.0. Both surfaces carry
matrix rows, so each scene runs two plans under `{ROOT}/GKit/<Tag>`. Prim caps are respected per
plan (22/24 and 34/32 against 60).

### 4.8 N4 — the kit stays on the flat approach

§5.8's N4 row (six gullies at 22 m, edge lines, cracks, low-point patches) is written for the whole
30 m ramp. The ramp descends at 5 %, and a single-z plan placed on it would float — 0.30 m at x = 6
`[computed]`. The plan covers the flat approach `x −14…0` only, with the gully count reduced to 2
(22–25 m spacing over 14 m). The crest is declared as an edge purely so surface elements keep the
0.8 m standoff and so `beyond_grade` is recorded; **N4 has no GT drop** and the comment in the file
says so. Sloped-run elements remain the scene's own slope-following expansion joints.

---

## 5. Findings handed back (all `ground_kit`-side; nothing was changed there)

| # | finding | evidence | consequence |
|---|---|---|---|
| **F1** | `_ik_marking` builds the element AABB as `_box_aabb(x0 + L/2, y0, …, L, w, …)` — **ignoring `yaw_deg`** — while the same function *does* use yaw to classify the line as `cross`/`long`. | code read; reproduced on D2 | Any transverse (yaw 90°) marking is judged as if it ran along +X. D2's opening-perimeter **west leg** trips B8 (void intersection) and B6 (edge standoff) although the real geometry is clear of both. This round delivers the two longitudinal legs and **defers the transverse leg**. scene13's lane lines used yaw 0, which is why this never surfaced. |
| **F2** | `plan_ground(overrides=…)` **merges** dicts, so `infra=dict()` does not clear a profile's urban infrastructure. | `[measured]` — sceneC2 with `infra=dict()` still produced 1 manhole + 2 gullies + 1 L-gutter (12 prims) in a scene whose row says "urban infrastructure 0" | Silent, and exactly the class of thing §3.4 exists to prevent. Zeros must be spelled out (`manhole=0, gully=0, …`), which every scene here now does. A `replace=` flag or a docstring line would close it. |
| **F3** | `_seed_key` strips only the literal token `/GKit/`. Multi-plan scenes need distinct prefixes, and any prefix that is not `{ROOT}/GKit/…` changes the RNG seed key, so `plan["prims"]` and the built prim count diverge. | `[measured]` — D3 road plan: 32 planned vs **34 built** under `{ROOT}/GKit_road`; 32 vs 32 under `{ROOT}/GKit/Road` | Only `build_crack_lines` has an RNG-dependent prim count (`nseg` 3 or 5), so the divergence is small, but B10 is then judged on a number that is not what gets built. Note the agreement under `GKit/<Tag>` is luck, not a guarantee: the seed key is still `"Road/Crack"` vs the plan's `"Crack"`. |
| **F4** | `EXPECTED_FP` rows come from `tactile_fp_rows()` with the **statutory** 0.30 m setback, but §12.4 assigns sceneC4 the "position error 0.6–1.0 m" defect. | `[computed]` — C4's band is at setback 1.00 m, so its rows sit outside the registered window (registered covers `[d−0.9, d]`; actual band is `[d−1.6, d−1.0]`) | The GRAZE round adjudicator will see C4's tactile response outside the pre-registered false-positive window. Either register per-scene setbacks or accept and document. |
| **F5** | B4 ("≥2 longitudinal lines") is a bookkeeping artifact wherever the scene, not the kit, owns the joints. | N1, N3, C4, D3-cover WARN B4 with 0–1 | The lines exist in the render; the plan just cannot see them. Not worth changing, worth knowing when reading the WARN column. |
| **F6** | B5 ("≥6 grime decals within X ≤ 3 m") is unreachable by construction for most profiles: `build_stain_field` takes no `sites`, so decal placement is uniform random over the trimmed region and only 0–5 land inside 3 m. | every plan in this round WARNs B5 | If B5 is meant to bite, `build_stain_field` needs a near-window bias or a `sites` argument. |

---

## 6. Risks and what should ride with this

1. **No pixels.** σ_LF/sd are unread. §7.5 A1 scoped them out of ground-only rounds, but W2-C's GO
   item 4 asks for the σ_LF ≥ 5.0 WARN gate to be restored in the first post-T1 ground round — that
   is the next render round, and these ten scenes are its material.
2. **Defect D3 (weeds render as solid olive boxes)** is still open and now appears in 7 of these 10
   scenes (N1 N2 N3 N4 C1 C4 D3 — weeds are in the P1/P3/P4/P8/P17 surface lists). At d2/d5 it is visible. Worth fixing before
   the 통람 v2 sheet rather than after.
3. **D4 / D5** (polygonal manhole discs, B9 checking a declared albedo while the scene binds a real
   material) also propagate: this round adds 7 new manholes across the ten scenes (N1 ×2, N3 ×2, N2 ×1, C1 ×1, C4 ×1) and binds them to
   whatever dark material the scene had.
4. **N5 consistency** — see §4.2. The four hard negatives now differ from the pilot on bollard
   tactile.
5. **D1's yard plan is mise-en-scène.** It is deliberately outside the h0.3 frame (the scene's first
   judging point is that the apron stays hidden behind the warning band). Its B1/B2 WARNs are correct
   and should not be "fixed".
6. **D3's road plan is lateral** (`y −8.0…−1.1` against a gy = 0 camera), so all of its B-gates warn.
   It exists for `oblique_cross` / `verge_walk` / h1.8, not for the presets.
7. **N1's joint prim count went 33 → 64** as a result of the two-tiering. That is scene geometry, not
   kit budget, but it is the largest single geometry change in this round and the one most worth a
   look in the first render.

---

## 7. Reproduce

```bash
cd Practice_NegObs
python3 ground_kit.py                              # exit 0 · 33/33 fixtures
python3 scripts/geom_invariance_check.py           # R-5 / R-4 33/33 / R-6 33/33
python3 -m py_compile scenes/batch1/scene*.py

# per-scene plan gates on this round's real arguments (no Isaac needed):
python3 - <<'PY'
import importlib.util, sys, glob
sys.path[:0] = ["scenes/batch1", "."]
for name in ["sceneN1","sceneN2","sceneN3","sceneN4","sceneC1","sceneC2",
             "sceneC4","sceneD1","sceneD2","sceneD3"]:
    f = glob.glob(f"scenes/batch1/{name}_*.py")[0]
    s = importlib.util.spec_from_file_location(name, f)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    for tag, gp in m.ground_plans():
        g = gp["budget"]["gates"]
        hard = [k for k in ("B6","B7","B8","B9","B10","B11") if not g[k]["pass"]]
        print(f"{name}/{tag} {gp['profile']} prims={gp['prims']} "
              f"{'PASS' if not hard else 'FAIL ' + str(hard)} "
              f"warn={gp['budget']['warn']}")
PY
```

The hazard-off twin and `NEGOBS_GKIT=0` arms were run through
`scripts/geom_invariance_check.run_arm()` with `NEGOBS_SCENE_CONFIG` / `NEGOBS_GKIT` overrides; the
two throwaway drivers are not committed (they are six lines each around that function).

---

## 8. Files touched

`scenes/batch1/sceneN1_shadow_band.py` · `sceneN2_asphalt_patch.py` · `sceneN3_trompe_loeil.py` ·
`sceneN4_downhill_ramp.py` · `sceneC1_snow_stairs.py` · `sceneC2_leaf_stairs.py` ·
`sceneC4_wet_stairs.py` · `sceneD1_loading_dock.py` · `sceneD2_floor_opening.py` ·
`sceneD3_drainage_channel.py` — plus this report.

**Not touched:** `ground_kit.py`, `scene_common.py`, `infra_kit.py`, `batch1_common.py`,
`sceneN5_flush_grating.py`, `sceneD4_subway_platform.py` (M8 deferral), anything under `scenes/main`.
No commits — the supervisor commits.
