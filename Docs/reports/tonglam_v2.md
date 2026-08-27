# 통람 v2 — whole-frame eyes verdicts over the W2-D round `260730_w2d_judge`

Author: eyes agent. 2026-07-30.
Method: reused `scene_wholeness_audit_v1.md`'s whole-frame method — for each of the 33 scenes the
three `pt_noon_preset_h0.3_d{2,5,10}` cuts were viewed FIRST (scene19: d2/d3.5/d5 per its preset
grid, substitution as recorded in `_review/w2/meta.json`), then `h0.9_d5` and the scene's beauty
cut. 165 full frames + all 23 captioned crops in `look_check/_experiments/gates/w2d_crops/` + 4
extra mise-en-scène/twin cuts (scene19 `entry_gate`/`upper_approach`, scene21 `crown_graze`,
GKIT=0 twins for scene16 d10 / sceneC4 d5). Bar: **"reads as a real Korean place at the robot
viewpoint"**, not perfection. W3 structural scope (buildings, midground fill, scene05 stage,
era items in `era_consistency_survey_v1.md` §6.2) was **not** allowed to drive a FAIL.

---

## 0. Verdict in one paragraph

**PASS 4 · FLAG 23 · FAIL 6.** The ground game genuinely changed: broom/blocks/granite near
fields, joints, cracks, moss and the tone work read as real surfaces in most scenes, and the six
tone targets landed without a single scene going muddy. The six FAILs are all **this round's own
content**, and they collapse into **three defect families plus one scene**: (1) the
constant-colour material family — scene19's membrane (B1/B3) and scene11's plate (B2) are only
the two worst members of a family that also renders sceneN2's crack decals as flat grey ribbons
and scatters textureless grey mats/patches through N1/N3/N4/N5/20/18; (2) the D-5 rock scatter
reading as boulder rubble in 04/07/10; (3) the leaf/soil decal rectangles with razor edges
(03/07/10/D3/C2); plus (4) scene17, where the swapped grass renders as a billiard leaf-print
plane over ~70 % of the d10 judgment cut and the library's worst manhole instance (near-white
faceted disc on dark asphalt) sits centre-frame at d5. Every one of these is a material-binding
or scatter-parameter fix — **no FAIL requires new geometry.** The carried D3/D4/D5 props (green
weed cubes, faceted manhole discs, near-white manhole albedo) are now the most frequent
*minor* artifact and appear in 12+ scenes' primary cuts.

---

## 1. Per-scene verdicts

Format: verdict — what the whole frame reads as at h0.3; FLAG lists are the minors (→ W3 input
unless marked FIX). W3-scoped observations are marked [W3] and did not affect the verdict.

| scene | name | verdict | whole-frame read + items |
|---|---|---|---|
| 01 | 캠퍼스 계단 | **FLAG** | Campus plaza reads plausible: granite texture, joints, crack meander, slender rails. Minors: D4+D5 manhole — near-white faceted disc floating proud, centre of d5 (FIX-5); billiard turf, brick+blue facade repetition [W3]. |
| 02 | 지하도 | **FLAG** | Underpass entry plaza reads well (block paving with moss joints, retrofit centre-pipe rail reads real). Minors: D4 disc at d2 bottom-left (FIX-5); stacked-sphere shrubs at d10 [W3-asset]; scalloped litter-bin rim. |
| 03 | 하천 제방 | **FLAG** | Now reads as a levee path + grass bank + river (the v1 "beach" read is mostly resolved). Minors: leaf/DG rectangle carpets with razor edges and a visible edge shadow (FIX-6); dead-flat mirror water [W3]; sphere-cluster shrubs in `meander_air` [W3-asset]; building ground contact still floaty [W3]. |
| 04 | 공원 침목길 | **FAIL** | D-5 scatter breaks the place: at d5/d10 dozens of near-white φ0.2–0.4 m boulders strew the grass/trail — reads as a rubble yard, not a gravel path (FIX-4). Also giant moss-green ellipsoid blobs, cotton-candy hedge, turf seams [W3]. Trail bed itself is fine. |
| 05 | 야외공연장 | **FLAG** | Amphitheatre bowl + granite forecourt read well; tone win visible (no chalk). Minors: manhole disc at d5 (FIX-5); green ellipsoid "shrubs" perched on bowl walls [W3-asset]; faint pale rectangle decal. Stage-disc black wedge gaps seen in `h0.9_d5`/`rim_view` [W3 — stage, excluded]. P1 near-field reclaim confirmed (joint + sealant + moss in the first 1.4 m). |
| 06 | 보행육교 나선 | **FLAG** | Footbridge over a marked road reads right (double-yellow centre line, lane dashes). Minors: smooth green mega-domes dominate the d2 skyline [W3-midground]; spiral rail reads faceted/segmented [W3]; road asphalt shows large slab-seam tiling in overview. Deck tile + anti-slip mat good. |
| 07 | 산사 돌계단 | **FAIL** | Temple forecourt bones are right (wall, gate, plinths), but the h0.3 cuts are dominated by boulder-scale two-tone rocks sitting in dark sink-ring depressions (FIX-4) + photographic leaf-litter rectangles with dead-straight edges that read as carpets laid on the DG (FIX-6). Giant flat green walls [W3]. |
| 08 | 선큰 광장 | **PASS** | Shadowed sunken-plaza entry reads genuinely real: barrier tape + striped bollards (strong Korean cue), herringbone blocks, pit rails. Frame mean ~49 is acceptable as a building-shadow plaza (eyes call on §7 scene08: no action). Minors: D3 cubes + one unfinished white prop in overview; planter bloom (supervisor: season). |
| 09 | 호수공원 수변 | **FLAG** | Machine PASS, eyes: near ground fine (white pavement textured, cracks), but the v1 "stage backdrop" critique is unchanged — black hedge-ball silhouette row + boxes against sky [W3-midground #2 priority], dead teal water [W3], odd mint-green square tiles on the plaza, toy duck boat + brick-textured pavilion roof [W3-asset]. |
| 10 | 공원 데크 갈지자 | **FLAG** | Timber deck switchback + stone pit + log fence read excellent; R1 plank gaps read 2–3 mm real. Minors: D-5 rocks on the trail legs (FIX-4); leaf-patch boundary renders a drawn dark outline (FIX-6); billiard terraces + dome hedges [W3]. |
| 11 | 보도육교 | **FAIL** | B2 confirmed and compounded: huge dead-flat mid-grey plates cover the deck near field (zero texture against textured surround, hard polygon boundary) and the flanking shrubs render as grey-lilac granite-speckled ball clusters at eye level. Together they cover most of the primary frame — reads as an unfinished CG stage (FIX-2). Bridge overview bones (road, stair, shelter) are good. |
| 12 | 수변 데크길 | **FLAG** | Waterside deck reads well (planks, wet cobble band glisten, rope barrier). Minors: proxy reed straws [W3-asset]; hard-edged gravel rectangles; revetment slabs float over the water edge in the air view; flat water [W3]. R1 gaps confirmed 2–3 mm. |
| 13 | 지하주차 진입부 | **FLAG** | Apartment parking-ramp entry reads convincingly (barrier, 안내 sign, canopy, textured anti-slip ramp; v1's "black void asphalt" is fixed). Minors: centre-line dashes render as raised ~2 cm white slabs, not paint; large dark faceted drain disc (FIX-5 family); capsule hedges [W3]. Gate 13-1: ramp side curbs read as curbs, not glowing wall bands. |
| 14 | 착시 대계단 | **FLAG** | h0.3 cuts read as a bright civic plaza (scuffs + cracks + drainage inlays; WHITE warn is borderline-bright but textured). Minors: metal drain channel terminates mid-slab at d2/d5 (unfinished line); D11 V-notch parapets in `lower_lookup`/beauty — adjudicated §2.1, defer-W3. flat_gnd win (18.6) is visible. |
| 15 | 달동네 골목 | **FLAG** | The alley ground is among the library's best (broomed concrete, L-gutters, stucco walls). Minors sitting right in the primary cuts: D3 olive cubes ×3+ (with a black void gap in the gutter slot behind one), near-white faceted manhole at d5 centre (FIX-5), potted mint-ball shrubs [W3-asset]. |
| 16 | 지하보도 입구 | **PASS** | Strongest main scene: granite blocks with moss joints, retrofit pipe rails + yellow nosings, 출구 sign, canopy, planters. GRAZE d10 = the full-width entrance tactile band, visually unmistakable as such (§2.11). Minors: chrome-yellow uniformity [W3 era-D], bloom season (supervisor), far-edge octagon disc. |
| 17 | 한강 제방 | **FAIL** | d2 asphalt near field is good, but the judgment set collapses: d5 carries the library's worst manhole (near-white faceted disc, max contrast on dark asphalt — FIX-5) and d10 is ~70 % swapped-grass rendering as a uniform billiard leaf-print plane (FIX-3/W3-3). Mirror water, ball hedges, stick reeds, blank sign board, bare elevated expressway [W3]. |
| 18 | 바닷가 벽화계단 | **FLAG** | Terrace + village + sea composition holds; tone improved (texture in the granite, no blowout), Jersey barriers good. Minors: ghost pale patch rectangles + outlined square (patch decals lighter than base — FIX-1 family); still a large bright expanse; billiard band + midground vacuum [W3]. |
| 19 | 옥상 winder | **FAIL** | B1+B3 confirmed at full severity: the membrane is a constant sage plane (vector seam lines only — reads as an unlit CAD viewport) and `entry_gate`/`upper_approach` sit ~70 % near-black; the shadowed membrane is a single constant near-black blob (FIX-1). Roof does not read as a place. [W3: rooftop equipment (v1 처방), blank white billboards on sticks, rail 1.1 m era item.] |
| 20 | 대각 사교 | **FLAG** | Clean civic terrace read; tone improved; grey stone accent bands plausible. Minors: two near-pure-white patch decals read as glowing plates (FIX-1 family); D3 cubes ×3; sterile emptiness [W3-midground]. |
| 21 | 기념관 대계단 | **FLAG** | Memorial facade + grand stair genuinely reads (yellow nosings, clean rake cheek walls — no V-notch here); charcoal/cream stone textures excellent (flat_gnd 9.9 visible). Minors: D3 cubes; lower plaza whiteness borderline; facade texture slightly game-like [W3]. `crown_graze` E band shows nothing anomalous (§2.11). |
| C1 | 적설 계단 | **FLAG** | Winter read is strong (cleared broom path, footprint trails, snow-buried bushes/benches, white-on-white rail). Tone win real (w80 18). Minors: near-field snow reads as veined marble at d2 (texture choice), planter caps ditto; thawed leaf stains on the path read oddly colourful. |
| C2 | 낙엽 매몰 계단 | **FLAG** | The leaf blanket itself reads very well (card variety, tone match with DG — no chalk/mud; σ_LF 12.94 shows). Minors: the mass's edges are ruler-straight (a leaf rectangle from the air) and buried risers render as compressed-leaf laminate print faces at d2 (§2.12, FIX-6/W3); hedge balls behind [W3]. |
| C4 | 우후 젖은 계단 | **FLAG** | After-rain forecourt reads striking and mostly right: wet-dry gradient at the pool edge is excellent, tactile field correct (§2.7), colonnade + sunken stairs read. Minors: the wet film is a zero-roughness mirror (reads as glass/standing pool over the whole zone); manhole disc visible in the pool; column crackle texture too strong [W3]; chrome yellow [W3 era-D]. |
| D1 | 하역장 도크 | **PASS** | Loading yard reads real (broom concrete, chevron dock edge, roller doors, crates, butter-yellow lane paint). Only minors: markings are pristine vector-clean [W3 era-E wear]. |
| D2 | 슬래브 개구부 | **FLAG** | Construction-slab site read is acceptable (form-board opening edge, pour joints, keep-out marking, fence). Minors: gravel piles are aggregate-photo-textured primitives (cubes/hemispheres) + one giant egg-shaped blob; rebar dowels read as toy rods [W3-asset]. |
| D3 | 노변 배수로 | **FLAG** | Rural verge + open channel + road reads well (broom texture, gutter, poles, fence). Minors: translucent glass-band backdrop floating at the horizon [W3-midground]; grass-print cube props at the road edge; one leaf patch carries a drawn outline frame (FIX-6); thin floating wire props. |
| D4 | 지하철 승강장 | **PASS** | Old Korean platform reads convincingly — and its tactile strip is the library's only *worn* one (grey-ochre, dulled domes): exactly the era-D target the outdoor scenes lack. Minors: blank signage, empty-sterile [W3]. |
| N1 | 그림자 띠 [HN] | **FLAG** | The hard-negative works: the building-shadow band reads as shadow (texture continuity through it). Minors: D3 cubes ×2, pale faceted disc, flat constant-grey mats ×3 (FIX-1 family), faint ghost outlines. |
| N2 | 아스팔트 패치 [HN] | **FAIL** | The asphalt patches themselves read excellently (aggregate + crack). But the ground_kit crack decals render as **flat mid-grey ribbon strokes** — thick bent polylines with zero texture crossing d2/d5 — too light for cracks, too bent for joints; plus the faceted floating manhole. The confound the scene needs is drowned by artifacts (FIX-1 crack-kind). |
| N3 | 트롱프뢰유 [HN] | **FLAG** | The painted stair illusion is crisp and the scene reads as a real shop-front plaza (안내 sign, awnings, planters). GRAZE d2 = the painting's own line, confirmed not-kit (§2.11). Minors: pale faceted disc, constant dark-grey L-patches (FIX-1 family), crazy-paving texture repeats tile-to-tile, wide flat joint bands. |
| N4 | 완경사 램프 [HN] | **FLAG** | Ramp corridor reads well (aggregate + cracks + moss, board-formed walls, rail shadows raking). Minors: several constant-grey strip patches (FIX-1 family); green cubes perched on the wall ledge; green moss-wash pavement zone reads odd in `h0.9_d5`; chrome-yellow tactile [W3 era-D]. |
| N5 | 플러시 그레이팅 [HN] | **FLAG** | The flush grating reads properly ribbed; plaza + 안내 + roadside tactile line read fine. Minors: the D4 charcoal 12-gon fills the near-left of d2 (double-rim CAD disc — worst D4 close-up, FIX-5); D3 cubes; constant-grey mats; large white expanse borderline. |

**Counts: PASS 4 (08 · 16 · D1 · D4) · FLAG 23 · FAIL 6 (04 · 07 · 11 · 17 · 19 · N2).**
Machine-clean ≠ eyes-clean: of the machine's FAIL-0-WARN-0 set (09 · C2 · D1 · D4), the eyes
pass only D1/D4 and flag 09 (W3 backdrop) and C2 (leaf-mass edges).

---

## 2. Specific adjudications

### 2.1 scene14 V-notch (D11) — settled: real geometry, not projection; defer-W3

Evidence: `s14_vnotch_lower_lookup.png` + full `lower_lookup` + `beauty_overview`.
**It does read wrong to an observer** — both parapet crowns are rows of clean triangular teeth
("folded paper"), obvious in any lookup/oblique view; it is *not* visible in the h0.3 judgment
cuts (parapets edge-on/out of frame).
**Cause ruling:** the two prior analyses are (a) the builder's own docstring/code
(`build_parapets` + `_rake_segments` in `scenes/main/scene14_grandstair_illusion.py`), which
claims a continuous rake-level-rake polyline with 0-step joints — under that claim a rendered
zigzag could only be a projection artifact of the 0.5 m top-face ribbon; and (b)
`w2c_merge_t1_v1.md` §5.6, which showed the notch identical in both T1 A/B arms (base geometry,
not material). The pixels decide it: **sky and background grass show *through* the V valleys**,
and the valleys drop below any connecting polyline — material is genuinely absent between
teeth. A ribbon-projection artifact would show the parapet's inner face inside the notch, never
the background. So the as-rendered geometry is missing its landing-level haunch runs (or has
them a full rail-height low), and each `build_slope` rake — whose end faces are
slope-perpendicular — reads as an isolated triangular tooth. This refines §5.6: real geometry,
specifically an **emission/placement bug contradicting the docstring**, not an intended shape
and not projection.
**Recommendation: defer-W3** (structural repair of the haunch emission), **keep scene14** — its
§7.3 gates now pass and the judgment cuts are unaffected. Do not spend the post-round fix batch
on it.

### 2.2 scene19 — blocker fix list (B1 + B3, one work item)

From `s19_flat_membrane_d2/tone_d2` + d2/d3.5/d5 + `entry_gate`/`upper_approach`:
1. **Rebind the membrane to a textured material** (granule/mottle albedo + roughness + normal
   variation, mid sage-grey ~0.45–0.55): the current constant meets w80<40 with 40 pp margin but
   `w80 0.0 / flat_gnd 94.8 / edge 1.4 %` is a dead plane. Target: flat_gnd back < 20 while
   keeping w80 < 40 (both numbers already have huge margin to trade).
2. **Fix the shadow response / albedo overshoot**: the de-whitened membrane in building shadow
   renders as the single near-black 15 % blob that fires OCCL+PHOTO on `entry_gate` (mean −47)
   and `upper_approach` (−57). Raising the membrane's base albedo per (1) largely solves it;
   verify the g3 parapet 0.40 grey stays (it reads fine where sunlit).
3. Replace the vector-thin seam lines with textured overlap strips (they currently read as CAD
   wireframe hints on the constant field).
W3 (not fix batch): rooftop equipment per v1 처방 (물탱크·실외기·배관), the four blank white
billboards, rail height 1.1 m (era §6.2-B).

### 2.3 scene11 — cause from pixels + fix scope

`s11_flat_plate_d2` / `s11_shrub_grey` + d2/d5/d10: the plate is **material binding, not tone**
— zero pixel variance against fully textured concrete around it, hard polygon boundary with a
corner bevel: a kit patch/overlay prim bound to a constant `OmniPBR` instead of its declared
weathered-concrete texture (the render-side twin of D5 declared-vs-bound). The "shrubs" are
Rhododendron hulls whose foliage material never applied after the `/Asset/Flowers`
de-activation — they render with a granite-speckle grey-lilac, i.e. a stone-family default.
**Fix scope: material rebinding only** — (a) bind the deck patch prims to the intended texture
(or disable them), (b) give the shrub hulls a foliage material or swap to the C2-style leaf
shrub asset. No geometry work. Both are members of the §3 constant-colour family below.

### 2.4 Deck plank gaps 10/12 — closed, reads real

`s10_deck_plank_d2` / `s12_deck_plank_d2` + both d2 frames: gaps read as continuous dark lines
at believable 2–3 mm, plank grain/knots read, no burial. R1 visibly fixed in both scenes.

### 2.5 R3 stain overlaps — quiet

`s07_stain_overlap_d2` / `s10_stain_overlap_d2` + d2 frames: no banding, no double-edge, no
z-fight signature at stain overlaps; boundaries stable in stills. (Stills cannot prove absence
of motion flicker, but nothing suspicious remains.) The visible 07 problem is the patch
*boundary* (§2.6/FIX-6), not the overlap step.

### 2.6 D-5 rocks 04/07/10 — boulders; scale_jitter is right but not sufficient

`s04/s07/s10_rock_scale_d5` + the d5/d10 frames: unambiguous boulder read in all three (φ
0.2–0.4 m apparent, near-white albedo, sitting proud; scene07 adds dark sink-ring depressions
that make them read pasted). **Lever ruling: scale_jitter down (~×0.5 → φ 0.08–0.14) is the
right first lever, but pair it with (a) sink raised from 0.0121 to bury 30–40 % of the small
rocks, (b) a count cap (04 250 / 07 223 / 10 118 are all too dense for a walked path), and
(c) dulling the near-white albedo to mid-grey.** Dropping rows 02/04/14 alone would thin the
field but leave the survivors boulder-sized.

### 2.7 Tactile Ø35 band — correct and legible

`sC4_tactile_d2`: domes read Ø35 mm at 50 mm pitch, 6×6 per tile, correct relief; the shipped
1.00 m position-error wedge reads as deliberate misalignment. Approach visibility is strong at
scene16 d10, N4 d5 (full-width band), N5 roadside line. The one look issue is uniform chrome
saturation — era §6.2-D (worn grey along the walk line), W3. sceneD4's worn strip is the
in-library reference for that target.

### 2.8 scene05 charcoal band at d10 — quiet, accept

`s05_charcoal_d10`: at d10 the band is a soft low-contrast tonal patch, visibly weaker than the
sealed joint and crack lines beside it and nothing like the bowl-lip shadow line. It does not
create a grazing confound for an observer; the GRAZE fusion is the adjudicator's registry
problem (D14/EXPECTED_FP), not a look problem. **Accept; no scene edit.**

### 2.9 Tone round 01/05/18/19/20/C1 — 5 real wins, 1 overshoot, 0 muddy

01 (granite grain restored), 05 (near field reads stone, joint sealant), 20 (accent bands),
C1 (snow holds value, footprints) read clearly less chalky and natural. 18 improved (texture in
the granite) but keeps a borderline-bright expanse plus its lighter-than-base ghost patches.
19 met its numbers by dying (§2.2). **No scene reads muddy**; scene08's dark frame reads as a
legitimately shadowed plaza (eyes call: acceptable, no action).

### 2.10 Pink-bloom census ≤1.05 % — nothing objectionable at h0.3

Residual bloom is visible at h0.3 in 01/08/13/16/N1/N3/C4 — always as small planter/verge
accents ≤~1 % of frame, never near a hazard band, reading as azaleas. Visually fine; whether
May-bloom belongs in an otherwise autumn-leafed library stays a supervisor season-consistency
call, not a defect.

### 2.11 GRAZE 8 — the 2 attributable firings confirmed visually; drift cuts clean

scene16 d10 ON vs GKIT=0 twin: the ON frame carries the full-width yellow entrance tactile band
in the E band; the OFF frame has plain paving and an **identical** stair/entrance line — the
"mandated tactile band, not the edge" explanation is visually exact. sceneC4 d5 pair: same
(yellow band absent in OFF, drop line unchanged; the mirror zone identical). Drift-family spot
checks (scene20 d2/d5, sceneN3 d2, scene14 d2): no kit line at any hazard row — N3's strong
line is its own painted illusion, 20/14 show only pavement banding. Nothing anywhere resembles
a buried or manufactured edge. D14 (wire `EXPECTED_FP` into the adjudicator, option (a)) is the
right close-out; no scene needs a look change for GRAZE.

### 2.12 Grass swap + leaf G2 (C2) — tone matches; boundary is not invisible

Tone: the C2 leaf mass sits naturally against DG and pavement (no chalk, no mud; the machine's
0/0 agrees). Boundary: **not invisible** — the mass terminates in ruler-straight edges (a
perfect rectangle from the air) and the buried risers render as compressed-leaf *laminate
print* on vertical faces at d2. At h0.3 the scattered-leaf feathering at d5/d10 reads genuinely
good. Same mask problem as the leaf rectangles elsewhere → FIX-6 boundary treatment / W3 mask
tooling. Corpus-wide, the swapped *grass texture itself* reads as chopped-leaf mulch when it
fills a frame (17 d10 worst, 10 terraces) — hue-uniform and scale-flat; ranked under W3-3.

### 2.13 Cross-scene: new artifact classes this round (d2 sampled in all 33 scenes)

1. **Constant-colour kit prims** (NEW, the round's largest class): membrane 19, plate 11, crack
   ribbons N2, grey mats/patches N1/N3/N4/N5, near-white patches 20, lighter-than-base ghost
   rectangles 18. One binding/tone code path.
2. **Leaf/soil decal rectangles with razor edges** (NEW): 03/07/10/D3 (+C2 mass edges); 10 and
   D3 add a drawn outline stroke; 03 adds an edge shadow offset.
3. **D-5 boulder scatter** (NEW): 04/07/10; 07 adds dark sink-ring depressions.
4. **Z-fighting: none observed** in any still. Scatter intersections (rocks over leaf patches,
   cubes in gutter slots) show no shimmer artifacts — but scene15's gutter cube sits over an
   unfilled **black void gap**.
5. **Floats**: scene12 revetment slabs hover at the water edge (air view); scene07 stepping
   stones borderline; benches/props otherwise seated.
6. **Raised 3D lane markings**: scene13 centreline dashes are ~2 cm slabs (N2/D1/N4 markings
   are correctly flat paint — so it is scene13's prims, not a global regression).

---

## 3. Ranked fix list — the ONE post-round fix batch (blockers only)

| # | fix | scenes cleared / helped | evidence |
|---|---|---|---|
| **F1** | **Constant-colour material family**: one audit of kit patch/mat/crack/membrane bindings — membrane rebind + shadow-albedo lift (§2.2 items 1–2), scene11 plate rebind + shrub foliage material (§2.3), N2 crack-kind rebind (ribbon strokes → dark textured cracks), then the same pass over N1/N3/N4/N5 grey mats, 20 white patches, 18 ghost rectangles | **clears FAILs 19 · 11 · N2**; de-flags 6 more scenes | `s19_flat_membrane_d2`, `s11_flat_plate_d2`, `s11_shrub_grey`, N2 d2/d5 |
| **F2** | **D-5 scatter re-parameterisation**: scale_jitter ×~0.5 + sink 0.0121→bury 30–40 % + count cap + albedo dulling (§2.6) | **clears FAILs 04 · 07 (with F3) · de-flags 10** | `s04/s07/s10_rock_scale_d5` |
| **F3** | **Decal rectangle boundary treatment**: kill the outline stroke + edge-shadow offset, feather/irregularise the leaf & gravel patch masks (min viable: 07 · 03; full mask tooling may spill to W3) | **needed with F2 to clear 07**; de-flags 03 · 10 · D3 · C2 edges | `s07_stain_overlap_d2` (boundary), 03 d2/d5, `s10_rock_scale_d5` (outline), D3 d5 |
| **F4** | **scene17 grass plane**: tiling scale + hue jitter (or blade layer) so the d10 frame stops reading as one leaf-print carpet; interim acceptable: reduce the grass-filled preset framing | **clears FAIL 17 (with F5)** | 17 d10 |
| **F5** | **Manhole D4/D5 pass** (cheap, pan-scene): silhouette segments ≥24 (or true cylinder + rim detail) and fix the bound albedo to the declared ~0.10 dark iron | removes the worst single prop from 17 d5 + 01 · 02 · 05 · 15 · N5 · N1 · 13 primary cuts | `s01_manhole_d5`, `s15_manhole_d5`, `sN5_manhole_d2`, 17 d5 |

F1–F3 are material/parameter work only; F5 is an asset swap/param; **none of the six FAILs
needs geometry.** Everything else observed goes to W3 below, per the blockers-only rule.

## 4. W3 input list (structure / asset observations, ranked by frame occupancy)

1. **Midground proxy wall**: hedge-ball/dome rows (06 · 09 · 10 · 17 · C2 · N2 · N4 · D3 · 03),
   scene09's black silhouette backdrop (v1 critique #2, unchanged), scene07's giant flat green
   walls, D3's translucent glass-band horizon backdrop.
2. **Buildings**: the brick+blue-window facade still repeats across 01/02/16/20/21/C1/N1/N2/N3/N5
   (v1 #3; the newer grey/tan variants in 03/08/13 show the path); windows are flat tinted
   rectangles, no frames/reveals.
3. **Grass/turf system**: billiard hue-uniform everywhere; the swapped grass texture reads as
   leaf-mulch print at scale (17 d10, 10 terraces, N4 surround) — needs hue/scale jitter or a
   blade layer (F4 is the stopgap for 17 only).
4. **Proxy props**: D3 weed cubes (12+ scenes), shrub sphere clusters (02/03/05/11/12/15),
   reed straws (12/17), D2's aggregate-print primitives + egg boulder, 09's toy duck +
   brick-roof pavilion; scene15 gutter-cube black void.
5. **Water**: constant/mirror planes (03 · 09 · 12 · 17) — ripple normals + shore treatment;
   C4's wet film needs micro-roughness breakup (its wet-dry gradient is already right).
6. **scene14 D11** parapet haunch emission repair (§2.1 — real geometry bug; keep the scene).
7. **scene05 stage** black wedge gaps (already-named W3 item; confirmed visible in 2 cuts).
8. **Era §6.2 riders**: worn tactile (D — sceneD4 is the in-library reference), rail material
   split (C), retrofit-style implementation (E), scene19 rail 1.1 m (B).
9. **Small carried oddities**: scene13 raised centreline slabs; scene14 drain channel ending
   mid-slab; blank signage (17 sign board, D4 platform signs, 19 billboards); C1 near-field
   snow-as-marble veining; N4 green moss-wash zone; scene06 segmented spiral rail; 12 floating
   revetment slabs.
10. **scene08 / scene09 machine-vs-eyes note for the supervisor**: machine PASS does not imply
    eyes PASS (09, C2); the eyes-PASS set is 08 · 16 · D1 · D4.

---

## 5. Files

Verdict basis: `look_check/<scene>/260730_w2d_judge/*.png` (judge round, HEAD `fc69706`) ·
crops `look_check/_experiments/gates/w2d_crops/` · twins
`look_check/_experiments/twins/{scene16,sceneC4}/260730_w2d_goff/` · gate numbers quoted from
`Docs/reports/w2d_round_v1.md` / `regr_260730_w2d.json`. This report: the whole-frame verdict
record for W2-D; supersedes nothing — `scene_wholeness_audit_v1.md` remains the v1 baseline the
①–④ structural critiques are tracked against (① ground fill: largely delivered this round;
② midground: open; ③ buildings: open; ④ over-exposure: largely delivered, 18 residual).
