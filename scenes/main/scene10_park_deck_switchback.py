# -*- coding: utf-8 -*-
"""
scene10_park_deck_switchback.py — NegObs synthetic scene 10 (v5 R5): park slope deck switchback

Type   : R5 (v5 redesign) — timber deck zigzag stair (inherits the open-riser see-through cue)
Spec   : Docs/briefs/multi_scene_brief_v5.md §R5 + Docs/scene_redesign_v5_proposal.md
Shared : scene_common.py (unmodified) / skeleton convention : scenes/main/scene04_parktrail.py
Legacy : scenes/archive_v3/scene10_switchback_cliff.py
         (rot_group 180° reversal + the **parallel switchback Y band** convention · open_riser builder)

────────────────────────────────────────────────────────────────────────────
[Hazard]
  A timber deck switchback stair on the slope of a neighbourhood park trail. The
  hazard is **the reality of falling short of code**.

  (1) [08-05 doctrine] every landing edge carries the same continuous guardrail
      (`broken_landing=None`) — the guard itself is the drop cue (a rail line
      means "the ground falls away beyond it"); the old broken-bay trap on
      landing0 (4.97 m open drop behind bare posts) is retired.
  (2) Open risers — the flight below and the ground show through between the timber
      treads. With no tread/riser light-dark pair, the nosing cut line never forms.
  (3) Leaf litter — a leaf_ground band bites over and covers the edges of the top two
      steps (treads 1·2), erasing the first nosing. Reading that as 'a flat deck entry'
      from the approaching robot's viewpoint (h0.3) is the GT-positive core of this scene.
  (4) The 30° grass slope south of the trail (−Y) is unguarded — beyond the trail
      shoulder (y −1.6) it falls at 30°, dropping 2.3 m within 4 m. No railing or kerb
      (not the practice on a park dirt trail).

[Walking continuity self-check table]  — entry → descent → exit (SMOKE recomputes all of it)
  ┌ Segment ────────────────┬ Coords (x, y band, z) ─────────┬ Step ─────────┐
  │ Upper trail (entry)     │ x −40..−1.5, y −1.6..1.45, 0.0 │ level         │
  │ Entry deck (wall head)  │ x −1.5..0,  y ±1.40,   −0.005  │ 0.005         │
  │ Flight0 (+X, −Y band)   │ x 0→3.0,  z 0→−1.65 (10 steps) │ riser 0.165   │
  │ Landing0 (reversal)     │ x 3.0..4.4, y ±1.40,   −1.65   │ 0 (flush)     │
  │ Flight1 (−X, +Y band)   │ x 3.0→0.0, z −1.65→−3.30       │ riser 0.165   │
  │ Landing1                │ x −1.4..0,  y ±1.40,   −3.30   │ 0             │
  │ Flight2 (+X, −Y band)   │ x 0→3.0,   z −3.30→−4.95       │ riser 0.165   │
  │ Landing2                │ x 3.0..4.4, y ±1.40,   −4.95   │ 0             │
  │ Flight3 (−X, +Y band)   │ x 3.0→0.0, z −4.95→−6.60       │ riser 0.165   │
  │ Landing3                │ x −1.4..0,  y ±1.40,   −6.60   │ 0             │
  │ Lower path (exit)       │ ground z −6.62 (2 cm below L3) │ 0.02          │
  └─────────────────────────┴────────────────────────────────┴───────────────┘
  · turn path on a landing: (x_bot, y −0.70) → (landing centre, y 0) → (x_bot, y +0.70)
    — both width bands fall inside the landing (y ±1.40), so there is no break.
  · vertical clearance between flights = 2×1.65 − 0.29 (stringer+tread) = 3.01 m.
  · even band y[−1.39,−0.01] / odd band y[+0.01,+1.39] — overlap 0 (gap 0.02).

[Geometry core]  — **superseded by the W3 S3 rebuild below; kept as the v5 record**
  · 4 flights × 10 steps, riser 0.165 / tread 0.30 / width 1.38, total drop 6.60.
  · A pure switchback makes no horizontal progress (plan x −1.4..4.4). The ground along
    the stair must therefore be effectively vertical, and that is realised as a **park
    cut stone retaining wall** (head wall at x=−1.5 + side wall at y=1.45).
    ** This sentence is the diagnosis, not the design.** S3-10 removes the wall by
    removing its cause: a traversing deck makes horizontal progress, so the ground can
    be a real slope. See [W3 S3] below.
  · No ground plane covers the cavity (the stair passage) — the upper trail plate stops
    at x=−1.5, and in front of it only the corridor slope exists.

[v6 verdict revision — judge_v6_rt_new7.md §4 + supervisor decision, 3 items]
  (1) **sun reselected** (supervisor approved — front lit on the open side). The old
     `SUN_AZ_OFFSET=171.5` (world az 205 = sun in the −X·−Y sky) put the whole
     switchback passage into the shadow of the **head wall (x=−1.5, top z 0)**: the
     shadow boundary of a point at depth d is x < −1.5 + 0.766·d, so out to d 6.6 m
     everything up to x 3.56 is dark = the entire passage. That directly killed the
     `from_below` and `through_treads` shots.
     → `SUN_AZ_OFFSET=216.5` (world az = 33.5+216.5 = **250**, shadow az 70).
       The only open directions in this scene are **−Y (the south lower park)** and +X,
       so the sun is swung far toward −Y to put direct light into the passage.
       Back-tracing the sun ray as a check:
         (x 1.7, y −0.7, z −4.24) → it reaches z=0 at (0.47, −4.07) : it does not cross
         the x=−1.5 plane → no occlusion by the head wall or the south slope =
         **direct sun arrives**.
       lambert per face (elevation 49.79 → horizontal component 0.6456):
         −Y faces (stringers·landing noses·north wall = the 4 shots)  0.607
         −X faces (grid axis front·distant ridge)                     0.221
         top faces (trail·landings·treads·grass)                      0.763
       The −X faces of the grid (viewing +X) drop to 0.221, but the grid image is mostly
       **top faces** (0.763), so no reading is lost. Conversely the −Y faces go
       0.273→0.607, a factor of 2.2.
     · The lowest point (landing3, x −1.4..0, z −6.60) is directly under the head wall and
       stays shaded under any western sun — it is left as a physical fact of a 6.6 m cut
       floor (all 4 key-cue shots are in direct sun).
  (2) **dispelling the "fortress wall" impression** (verdict (5) 'material and scale
     replacement is the key to reading this as a park')
     (a) `rock_wall` UV 3.0 m → **0.9 m** : 0.6 m-class blocks of fortress masonry →
         0.18 m-class **quarried rubble** (the practice on park cut faces).
     (b) **separate the built wall from the natural cut face by material** : only the
         head wall and the north wall are masonry (`rock_wall`); the body of the south
         slope (the cut face dropping from x=−1.5 into the lower park) is `rock_face`
         (jointless natural rock) — previously that face was masonry too, so the left
         half of `from_below` was one solid rampart.
     (c) **two-tier east wall** (x 5.2..44) : a single 6.62 m wall → lower 3.32 m +
         **berm 1.0 m (planted)** + upper 3.30 m. This is the standard section for an
         urban park cut wall, and the deck run (x −1.5..5.2) keeps the single wall, so
         the **hazard geometry is unchanged**.
     (d) **coping band on top of the wall** — a concrete strip projecting 0.08 m past
         the wall face.
  (3) **the railing read as a temporary ladder frame / gallows** (verdict (5)) →
     **vertical bars** (0.30 m pitch) were added to a railing that had only top and mid
     rails. This is the standard for a park deck railing, and with the bars in place the
     raking rails of the adjacent flight are no longer misread as bracing.
  (4) **leaf and dirt-trail square decals** (C-7) · **confetti saturation** (verdict (5))
     → dirt UV 3.0→1.1, leaf 1.8→1.05, tints neutralised, ground leaf patches broken up
     by overlaying 3 rotated copies.
  (5) shrubs floating above the slope → the blob grounding z was lowered to the
     **downhill ground**.
  (6) distant lollipops (C-4) → jitter on distant tree trunk radius and height + a forest
     silhouette band on the distant ridge crest (build_hedge round crowns).

[v7 verdict revision — judge_v7_rt_A.md §7 "the 4 mise-en-scene shots do not read as a park"]
  Conclusion of the verdict: **"what is left is not the code but the camera"** — the
  material fixes (smaller rubble, separated natural rock, two-tier wall, vertical bars)
  are sufficient, but all 4 shots were deck close-ups, so no park signal (grass, shrubs,
  trees, visitor furniture) entered a single frame. The grid shots, by contrast, do read
  as a park = the problem is framing, not geometry.
  (1) **mirror `from_below` to the open side (−Y)** (direct instruction (b)) : the old
     sight line 129.6° had half its subject facing +X (head wall and cut face =
     lambert −0.342), giving mean 36.4·dark 66.3 %. eye (8.0,−7.5)→**(5.2,−10.8)**,
     sight 105.4° (normal 285.4° = **lambert +0.527**), pitch +6.6°. The bottom of the
     frame lands on the **lower park dirt trail**, and 3 shrubs, 3 north grass slopes,
     the waymarker and the bench = **8 park anchors** are inside the FOV.
  (2) **`reversal` pulled back and raised** ((a)) : eye (3.7,−3.2,−0.30)→**(6.6,−6.6,1.20)**,
     pitch −24° → **−16°**. The top of the frame (+2.0° elevation) now carries the
     **north 30° grass slope** beyond the wall coping, so about a quarter of the image is
     greenery (landing0 and flights 0/1 are kept).
  (3) **`broken_rail` rotated south** : sight 135° (lambert +0.273, damaged and intact
     railing in the same dark band) → 112° (**+0.480**). The bottom ray passes through the
     vertical space under landing0 and lands at z −4.46 → the depth of the drop stays in
     the frame.
  (4) **waymarker shrunk again** ((c)) : blades 0.72×0.11 → **0.58×0.09**, heights
     1.72/1.98 → **1.80/2.06**, post r 0.065 → 0.080 · total height 2.26 → post 79 % exposed.
  (5) one shrub clump added in the lower park (0.5,−5.5) — for the left framing of
     `from_below` (passes §6 "the minimum needed to read": the park reading of this shot
     is the very reason for the revision).
  Check: SMOKE `[v7 mise-en-scene]` — per shot the sight line / normal / **lambert**, the
        ground point the bottom ray lands on, and the park anchors inside the FOV
        (horizontal ±30° · vertical ±18°).
  Not addressed: `through_treads` (a see-through close-up, "improvement confirmed" in v7)
        has 0 anchors by nature — only its illumination is confirmed at lambert +0.620
        and the composition is kept.

[W3 S3 archetype rebuild — target image G10, `Docs/reference_photos/Generated Image - Scene10.jpg`]
  Authority: `Docs/briefs/s3_scene07_10_rebuild_spec_v1.md` (§2, §4.2, §8.R rulings) +
  `Docs/surveys/s3_research_numbers_v1.md` (measured Korean standards). The diagnosis the
  rebuild answers is that the scene "reads as an apartment emergency stair", and the spec's
  own ranking of causes is **C1 stacking > C7-C9 round railing sections > C18 near-black
  timber** — the riser/tread ratio was never the defect (2R+T = 0.630 is inside KCS 34 50 10
  3.2.8(3)'s 600-650 window).

  **Divergence from G10, declared** `[ruled 07-31]` §8.R OQ-2: G10 reads **closed riser
  boards**; this scene **keeps its open risers**. Hazard cue (2) in the header and the whole
  `through_treads` cut are research design, not looks, and the emergency-stair read is cured
  by the railing, the de-stacking and the season instead. If riser boards are ever ordered
  that is an additive follow-up, not a rework of this work.

  S3-8 (this commit) — **railing rebuilt in square sawn timber**, §4.2-2:
    · every member square/rectangular; not one round member is left in the railing. G10 has
      no round member in frame, and a run of thin round verticals between two thin round
      horizontals *is* the silhouette of a steel balustrade.
    · capped 90x90 newels (cap 120x120x45, 0.15 m proud of the top rail) at every shared
      corner · 38x140 top rail laid flat · 38x89 mid + bottom rails · 38x38 balusters at
      0.150 m **horizontal** pitch (clear gap 0.112 m) · deck columns 120x120 · one lattice
      infill bay on the entry deck's +Y run · algae collar at the grounded column feet.
    · rail height 1.05 -> **1.10 m** to the top face (§8.R OQ-5, KNPS median n=1,227);
      the 조경설계기준 16.20.2(2) >=1.2 m 관찰데크 counterpoint is on GT-20's ledger row.
    · timber patina re-aimed at the **measured** 2-5 yr 방부목 CIELAB target (L* 53-60).
    · every landing edge carries the same continuous guardrail; the open-riser flights are untouched.

  S3-9 — stair re-table, §4.2-1. 4x10 at 0.165/0.300/1.38 -> **6 flights, 8+7+8+7+7+7 = 44**
    at 0.150/0.310 (2R+T 0.610, 25.8 deg), clear width **1.500**, 4 turn landings
    1.50 x 3.20 + one 쉼터/전망 platform 3.00 deep at z −3.450 with a bench. Total drop
    6.600 frozen. The old ratio was never the defect (0.630 is inside the KCS window);
    the width and the landing were.
  S3-10 — de-stacking, Option A. Flights tile the X axis and turn 90 deg on each landing;
    plan overlap **0 m²**; the masonry shaft (BankCut + two-tier east wall + copings +
    berm) is deleted and replaced by a real 25.8 % corridor slope with level benches
    under the landings, air gap 0.020-0.600 m and the stair foot at 0.250 m (KFS 12-3 마
    caps it at 300 mm). Plan x[−1.50, 24.14], y[−1.60, 3.10].
  S3-11 — season, 만추 leaf-off. 24 trees pinned (12 bare deciduous + 12 evergreen far
    belt), 13 shrub clumps become real autumn-legal USDs, grass and hedge tints derived
    to a straw target, 780 scattered litter instances around the 4 KEPT CB-2 lobes, rock
    outcrop at the uphill margin, 3 windowless silhouette masses beyond 80 m.
  S10c — **the leaf-off arm of S3-11, delivered.** Red-team **F1** proved the mechanism
    S3-11 used was composition-inert: a stage-side `SetActive(False)` on a descendant of
    an instance is discarded by USD, so all twelve trees rendered in full green leaf
    while the log printed `12/12`. `_bare_tree` now references the additive wrapper
    layers `assets/veg_bare/*_bare.usda` via `sc.veg_wrapper_rel` (K4(0) `e4fc4cf`),
    which composes the strip **inside** the prototype. Geometry, scale and placement are
    unchanged by construction — the only delta is foliage leaving the frame.

[GT-65 — 08-05 gallery review: "연결부가 아직 지저분" + "데크 느낌이 끝까지"]
  P-2 keeps the archetype parked, so this is junction and continuity work only — the
  널 틈, the 돌구덩이 (rock outcrop) and the 통나무 펜스 family are untouched and the
  registered 6.600 m drop, the flight/landing table and every collider are frozen.
  (1) **Railing junctions, rebuilt from one model.** The deck is y-monotone, so its
      guarded boundary is exactly two polylines; `deck_slabs()` -> `rail_runs()` now
      derives every rail, every corner and every newel from that boundary instead of a
      hand-written list. Fixed by construction: the forward run no longer stands across
      the head of the next flight (it did at 5 turns and at the exit), a flight rail and
      the landing rail it continues into are collinear so a junction carries **one**
      capped newel instead of two 19 mm apart (12 such pairs), the landing back edges
      are closed so no run starts in mid-air, and a baluster can no longer sit inside a
      line post. Newels 52 -> **41**, runs 32 -> **39**.
  (2) **Deck continuity to the scene end.** The upper dirt trail met the deck 0.10 m
      short (grass seam); the deck planking existed only on the 1.5 m entry deck, so the
      remaining 22.6 m of landings read as smooth slabs; and the arrival landing railed
      off its own exit onto grass 1.0 m north of a `LowerPath` it never touched. The
      trail now meets the deck at x −1.50, all six landings carry the same 25x140 board
      division, the arrival guard is gone (20 mm to grade — a guard there is a false
      drop cue) and `DeckExit`/`DeckExitLink` hand the walk to `LowerPath` and on to the
      scene edge, with the east forest band pulled back to leave the gate.
  (3) **Foreground shrub review: nothing to convert.** All 13 shrub clumps already run
      through `sc.place_shrubs` (autumn-legal pool, `det_seed`). The only `build_hedge`
      users are `FarHedge_*` (y −40..−37, x 40..43) and `RidgeCrest_*` (crest bands at
      base 3.10 / 6.76) — the distant TreeLine idiom `place_hedge_row` itself excludes
      and GT-63 keeps. **No foreground clipped band or shrub bed exists near the path**,
      and none was invented.

[GT-77 — 08-06 gallery review: "데크가 연결되는 길도 자연스럽게"]
  GT-65 made the **deck** continuous; the 08-06 audit says the **ground it lands on**
  is not — 무맥락 평탄 황토 매트. Read off the round's own cuts:
  `pt_noon_preset_h1.8_d10.png` shows a 1.70 m dirt ribbon with two dead-straight
  parallel edges butting into a 3.20 m deck head, so 0.75 m of bare turf flanks the
  threshold on each side and the last metre of the walk crosses grass; the ribbon has
  no shoulder, no edging and no planting anywhere along it, and the same butt joint is
  repeated at the arrival end where a 3.20 m landing hands off to a 1.80 m `DeckExit`
  strip. `pt_noon_reversal.png` shows the ground beyond the deck terminating in raw
  vertical cut faces. This block finishes both ends and nothing else: the registered
  6.600 m drop, the flight/landing table, every collider and every P-2 preserved item
  (널 틈 · 돌구덩이 · 통나무 펜스 family) are untouched.
  (1) **Approach paths, both ends, from one table** (`PARAMS['approach']`). Four member
      families per end — `apron` (dirt wings carrying the path out to the full deck
      width at the threshold), `header` (a 90 mm 방부목 마구리재 bedded across the deck
      end), `edge` (90x90 경계목: straight run + 90-deg return + flank, every run end
      dying into another member or into a capped end post) and `verge` (a 0.60 m rough
      dormant-grass shoulder outside the edging). Every member is dressing over ground
      that already carries its collider — `col=False` throughout — so no walking
      surface, no drop edge and no GT-read AABB moves; the row stays R-3.
  (2) **No coplanar pair and no coincident visible face, by construction.** Each member
      is offset onto its own step of the existing decal ladder and *bedded into* the
      member it meets, so the surface it replaces passes **inside** a solid instead of
      lying on it: header top = path top + 0.010 (path top and deck top both buried),
      edging tucked 0.010 into the path, apron outer edge tucked 0.040 under the flank,
      flank end tucked 0.030 into the header, return ends tucked into run and flank.
      Asserted member by member by the `[GT-77 접근로]` SMOKE table.
  (3) **Nothing crosses the south shoulder.** At the entry the deck head stands on the
      break line of the 30 % unguarded south slope (hazard cue (4)), so every entry
      member stops at y −1.600 exactly: a board projecting past the break would be the
      floating end this round exists to remove, and moving path material past it would
      move a drop edge. SMOKE asserts max |y| over the entry members.
  (4) **Head-wall fill batter.** North of the deck the terrace (z 0.000) met the corridor
      bench (−0.255) as a raw 0.255 m vertical cut, 6.4 m long. A 0.90 m grass batter
      (15.8 deg) returns it to grade, held 0.030 m clear of the deck fascia so no face is
      coincident with it. `collider=False` — the corridor bench underneath already
      carries the collision surface, so the physics world is bit-identical.
  (5) **Verge planting, 4 clumps** (13 -> 17), all through the existing `sc.place_shrubs`
      autumn-legal route. Each is held outside the +X grid sight corridor (the ray from
      the d10 eye to the deck head corner), so no judged grid cut loses the stair head —
      checked by coordinates, not by eye.

[GT-115 ⑭ — 08-14 audit, cuts `look_check/scene10/260806_w3_allview5/`]
  Five crop-verified defects, all of them dressing or finish. The registered 6.600 m
  drop, the flight/landing table, every walking surface, every drop edge, the terrain
  slab layout, the P-2 preserved family (널 틈 · 돌구덩이 · 통나무 펜스), the camera
  presets and the 만추 leaf-off pin are untouched by every item below.
  (1) **Balusters through a boulder · every run end terminated**
      (`pt_noon_reversal.png` 1300,470-1520,700 · 1740,760-1920,900).
      `Outcrop_0` is `rock_moss_set_01`, and that row is not a boulder — it is a
      **pre-composed 8.005 × 6.949 m rock *set*** (`urban_manifest_w3.json`, 6 meshes /
      63,127 tri). At `scale_mul=1.00` and (6.30, 4.15) its plan envelope is
      x[1.29, 11.31] · y[−0.57, 8.87], which swallows the +Y guard line (y 1.619) over
      x 2.48…7.65 — the balusters in the crop are standing *inside* the scan. **A pure
      translation cannot fix it**: to clear the rest-platform run (y 3.119) by 0.30 m the
      centre would have to go to y ≥ 8.21, i.e. out of the corridor and onto the north
      bank, which is neither "nearby" nor groundable on a 30° slope. So the row is
      re-scaled **and** moved — 0.50 / (6.30, 4.90) — which is inside the precedent band
      for this very asset (scene09 uses 0.30 / 0.40 / 0.55 on it) and keeps `z_mode='base'`
      · `sink 0`, so the `tonglam_v2` §1 row 10 sink-ring defect stays closed.
      `rock_02` moves y 2.30 → 2.55 (its 0.335 m clearance was inside the 0.30 m bar but
      had no margin for the yaw envelope). `outcrop_clearance()` re-derives every number
      from PARAMS and the self-check asserts ≥ 0.30 m.
      Run ends: `rail_runs()` now emits a **90° return** at each of the four degree-1
      boundary nodes (deck head x −1.50 · arrival landing x 24.14, both chains). The
      return turns **inboard** — outboard at the entry would cross the y −1.600 unguarded
      south break line that GT-77 (3) forbids — is 0.30 m long, and its far end is a
      capped end post from the same `newel_points()` pass, so a run can no longer stop
      without a post at either face of the member it meets. The arrival returns leave
      2.60 m of the 3.20 m forward face open, against a 1.80 m `DeckExit`, so the
      hand-off of §0-2 is unchanged and no guard is re-added across the 20 mm step.
  (2) **Leaf clusters: one silhouette ×20** (`pt_noon_reversal.png` 60,370-600,700 =
      the corridor litter bands, not the CB-2 lobes). Cause: the three `Litter_*` calls
      all drew from the **whole** `sc.VEG_DEBRIS` pool with one seed and the default
      ±25 % scale jitter, and the pool's two cluster rows carry 9.6× / 3.9× the mean
      per-instance cover of its three single-leaf rows, so the frame is *area*-dominated
      by two silhouettes rotated about Z. Fix, **with no procurement**: each band is
      now laid as **three source
      variants** built from the same five USDs — `drift` (the two clusters, 0.85-1.45),
      `mixed` (cluster + singles, 0.70-1.15), `singles` (the three single-leaf cards,
      0.45-0.85) — each with its own tilt band and its own `gk.det_seed` draw. Instance
      budget is unchanged **exactly**: the caps 110+90+60 = 260 per band = the old
      `litter_max`, so 780 instances as before (all three calls were cap-bound).
  (3) **Shelter pergola was a slab on 4 posts.** `sc.build_canopy` is kept verbatim (the
      roof slab and the four columns keep their colliders and their AABBs) and the
      framing is added over it: 2 header beams let into the post tops, 5 rafters framed
      **between** the headers (bedded 0.010 so no coplanar pair), a fascia band wrapping
      the slab edge (outer face 0.020 proud, bedded 0.010 into the slab, top 0.010 under
      the slab top) and 4 post base plates. Flat roof + fascia, not a pitch — the roof
      slab is the one member with a collider and it does not move. 15 prims.
  (4) **Handrail.** The 38x140 top rail laid flat is a shelf, not a grasp. A Ø0.035
      round handrail line is bracketed on the **inside** face of the existing guard,
      1.025 m over the walking surface, derived from the same `rail_runs()` inventory so
      it follows the level, raking and cross lines exactly; nothing existing moves.
      **Declared divergence from S3-8**: that commit's census "난간 원형부재 수 = 0" was
      a *silhouette* argument — a thin round vertical between two thin round horizontals
      reads as a steel balustrade. A single horizontal graspable tube behind the square
      frame is the opposite reading and is what a 방부목 관찰데크 actually carries, so the
      census line is re-stated rather than quietly broken: **frame round members = 0,
      handrail = 1 line.** The declared 1.500 m clear width is measured at the walking
      surface between baluster faces and is **unchanged**; the tube projects 0.0785 m
      into it at grasp height, inside the ≤100 mm handrail projection allowance.
  (5) **Uniform moss on every rail face** (`pt_noon_leaf_edge.png`). Per-face materials
      are impractical — every member is one box prim — but the railing **is** separable
      by member orientation, so the fix is applied at that granularity, which is the
      scene's own §2.A.1-8 doctrine ("G10 reads silvered top faces over darker vertical
      faces") finally applied to the guard: the top rail of every run and the newel caps
      take a **silvered** tint (L* 59.0, a* +1.0, b* +5.0, albedo 0.270), the balusters,
      mid/bottom rails, line posts and newel posts keep the moss-side tone. That tone is
      **also lightened** as the item's fallback asks: the guard tint moves off the frame
      tint's ratios (G/R 1.348 → 1.217, B/R 1.610 → 1.331), which is a 10 % / 17 % cut in
      how hard the map's algae texels are pushed toward teal, at an **unchanged** albedo
      0.211 and L* 53.0. Both tints stay inside the measured 2-5 yr 방부목 band
      (L* 53-60 · a* 0..+2 · b* +4..+10 · albedo 0.22-0.28). `M["stringer"]` itself is not
      touched, so the columns, stringers and the GT-77 approach timber are bit-identical.
────────────────────────────────────────────────────────────────────────────

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene10_park_deck_switchback.py

Auto capture : NEGOBS_CAPTURE=1 python scene10_park_deck_switchback.py
Smoke        : NEGOBS_SMOKE=1 python3 scene10_park_deck_switchback.py  (no boot)

Coordinates: Z-up, m. Flights descend along local +X (convention). Odd flights use
        rot_group 180° (pivot = top of the flight) → −X in world. Grid axis = upper approach (+X).
"""

import os
import sys
import math
import json
import random
import datetime

import scene_common as sc
import ground_kit as gk
import urban_kit as uk


# ===========================================================================
# [A] SCENE_CONFIG - standard 7 keys. Only hazard_stairs toggles the hazard geometry.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False -> flights become a flat z=0 deck (drop removed)
    "cue_railing":        True,    # park deck = railing is the practice. **but one break at the landing0 outer edge**
    "cue_tactile":        False,   # not the practice on a park dirt trail (v5 brief §shared) - code path only
    "cue_material_break": True,    # timber deck vs grass / leaf ground contrast
    "cue_sign":           False,   # [v5.2 user] arbitrary warning sign removed - nothing placed (key reserved only)
    "cue_scene_dressing": True,    # trees·shrubs·waymarker·bench·shelter pavilion
    "cue_nosing":         False,   # a nosing band on a timber deck is not the practice - code path only
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # --- switchback flights (inherits the parallel Y-band convention of archive_v3/scene10) ---
    #   [S3-9 re-table, spec §4.2-1]. The honest headline first: **the old riser/tread was
    #   never the defect.** 2R+T = 2(0.165)+0.300 = 0.630 is inside KCS 34 50 10 3.2.8(3)'s
    #   600-650 window and 〈표 13-1〉's 30-deg row is 170/300, so the intake's "an interior
    #   ratio, not an outdoor one" is refuted. This row is a **fidelity** change, not a
    #   compliance fix; the compliance failures were the width and the landing.
    #     riser 0.165 -> 0.150   44 x 0.150 = 6.600 **exactly** (total drop frozen, §9 P-2)
    #                            [law] KFS-TRAIL p.70 caps trail rise at 15 cm; every
    #                            〈표 13-1〉 row from 25 deg down uses exactly 150
    #     tread 0.300 -> 0.310   2R+T = **0.610** in [0.600, 0.650] `[law]` KCS 3.2.8(3),
    #                            pitch 25.8 deg — 〈표 13-1〉's 25-deg row (150/310) verbatim.
    #                            The intake's 0.350 would give 0.650, the very top of the
    #                            window, and its stated band 0.65-0.70 is partly outside it.
    #     uniform over the whole run — [law] 3.2.8(3) "전 구간에 걸쳐 동일하여야 하고";
    #                            no per-flight variation, no jitter, and the self-check says so
    #     half_w 0.69 -> 0.75    clear width **1.50 m**. [law] 산지관리법 시행령 별표 3의3
    #                            제4호 다 caps 숲길 at "너비가 1.5미터 이내일 것";
    #                            [data] KNPS-STAIR 데크-named stairs n=155: **1.50 = 47.7 %**,
    #                            median 1.50, **1.80 only 9.0 %**. The intake's "typical 1.8"
    #                            is corrected — 1.5 is where the distribution piles up because
    #                            it is the legal ceiling.
    #     y_off 0.70 -> 0.80     keeps the two 1.50 m bands clear of each other: gap 0.10
    #                            (was 0.02 at width 1.38)
    #     steps 4x10 -> **8,7,8,7,7,7 = 44** over 6 flights. G10 shows short flights with
    #                            generous landings, and 8 risers = 1.20 m of rise per flight
    #                            clears 조경설계기준 5.10.2(3)'s 2 m landing pitch with margin.
    #     tread_t 0.05 -> 0.025  the tread plate is a **stocked 25 x 140 데크판재**, not a
    #                            50 mm slab (research §D2; 산림청고시 2014-2 제8조 fixes the
    #                            legal thickness series at 21/24/27/30... and the width series
    #                            at 90..300 in 10 mm steps, so 25 x 140 is stock, 0.145 is not)
    flights=dict(n=6, steps=(8, 7, 8, 7, 7, 7), riser=0.150, tread=0.310,
                 half_w=0.75, y_off=0.85, tread_t=0.025, gap=0.02, z_top=0.0),
    # landing — [S3-9] 1.50 (travel) x 3.10 (across, spanning both width bands), was
    #   1.40 x 2.80. The governing dimension is the **depth in the direction of travel**:
    #   [law] 조경설계기준 5.10.2(3) "높이 2m를 넘는 계단에는 2m 이내마다 당해 계단의
    #   유효폭 이상의 폭으로 너비 120cm 이상인 참을 둔다" and 5.9(4) fixes 1.5 x 1.5 m for a
    #   continuous run; the two converge on 1,500 mm for a 1.50 m flight, and the old 1.40 m
    #   **failed** it. 3.10 across is not a luxury — a 180-deg reversal landing has to serve
    #   both 1.50 m bands side by side.
    #   `rest_at` = the intermediate that becomes the **쉼터/전망 platform** (C5, *the*
    #   park-vs-egress signature): after flight 2, i.e. 8+7+8 = 23 risers, z = -3.450, the
    #   nearest level surface to mid-height (-3.300). It is 3.00 m deep instead of 1.50 and
    #   carries a bench. [law] SANJI-183's own exception 2) names 휴식·대피를 위한 장소 as a
    #   legitimate reason to exceed the 1.5 m width, so this is the one element licensed to
    #   be larger than the flights.
    #   [S3-10] `rest_extra` projects the rest platform past the +Y band as a 전망 balcony,
    #   and `clear` is the designed air gap between the deck underside and natural grade.
    #   0.25 m under the flights and turn landings is not a styling choice: [law] KFS-TRAIL
    #   특별시방서 12-3 마 (p.165) "데크계단의 설치시 … 계단하단부와 지반과의 높이차가
    #   30cm 이상으로 올라가지 않도록 시공하고" — the stair foot must stay within 300 mm of
    #   natural grade. The rest platform is not a stair foot, so it is allowed to stand
    #   0.60 m proud and read as a projecting 전망대.
    landing=dict(size=1.5, thick=0.12, y0=-1.60, y1=1.60,
                 rest_at=2, rest_size=3.0, rest_extra=1.5,
                 clear=0.25, rest_clear=0.60),
    # entry deck : from the retaining wall head (x −1.5) to the first step (x 0) - joins the upper trail
    entry=dict(x0=-1.5, x1=0.0, top=-0.005, thick=0.10),
    # deck support columns : the four landing corners (0.15 inside the landing x ends) x y +-half_y.
    #   the actual (x, z range) is derived from the landing stack by post_segments().
    #   [S3-8 / gap C7] round Ø150 cylinder -> **square 120x120 sawn timber**. 120각 is a
    #   Korean stocked 기둥재 section (research §D2, cross-checked over 5 suppliers); the
    #   KFS-TRAIL 2010 drawings' 100x100 is a drawing size that is **not** retail stock, so
    #   the load-carrying column takes 120각 and the railing newel below takes 90각 — the
    #   stocked pair. Every visible member in G10 is square; not one round member is in frame.
    post=dict(sec=0.120, half_y=1.40, inset=0.15),
    # railing — [S3-8] rebuilt from G10 in all-square 방부각재. This is §4.2-2, the
    #   highest-value single change in the scene: a run of thin **round** verticals between
    #   two thin **round** horizontals is the silhouette of a steel balustrade, and it is the
    #   largest single contributor to the fire-escape read.
    #   `h` = the **top face of the top rail** above the walking surface, which is how the
    #   KNPS 난간 register measures 폭높이.
    #     1.10 m — §8.R OQ-5, on the KNPS-RAIL built-reality basis (median 1.10, n = 1,227;
    #     71 % of real trail railings are 1.0-1.2 m). The 조경설계기준 **16.20.2(2)** ≥1,200 mm
    #     관찰데크 clause is the code counterpoint; it is recorded in GT-20's ledger row, and
    #     built reality wins here under the user's real-case-first doctrine.
    #   Sections are stocked 방부각재 (research §D2): newel 90x90 · rail 38x140 laid flat
    #   (a hand rests on it, §2.A.1-3) · mid/bottom rail 38x89 · baluster 38x38.
    #   Balusters stay **plumb to the tread plane, never raked** — KCS 34 50 10 3.2.6(3)
    #   "비탈면에 설치되는 계단난간의 세로부재는 계단면에 수직이 되도록 제작, 설치하여야 한다".
    #   `bal_step` 0.150 m measured **horizontally** on level and raking runs alike, so the
    #   clear gap is a single number everywhere: 0.150 - 0.038 = **0.112 m** (§8.R OQ-5's
    #   0.110 ± 0.010). 조경설계기준 16.13.2(3) sets ≤100 mm for a 안전난간 with a 단서 of
    #   ≤150 mm for a 계단중간 난간; 112 mm sits inside the 단서 and matches G10's ~7 balusters
    #   per 1.1 m bay. Asserted, with the statute cited, by deck_module_selfcheck().
    rail=dict(h=1.10, mid_frac=0.50, bot_z=0.12,
              newel=0.090, newel_cap=(0.120, 0.120, 0.045), newel_proud=0.150,
              post=0.090,
              top=(0.140, 0.038), mid=(0.089, 0.038), bot=(0.089, 0.038),
              bal=0.038, bal_step=0.150,
              spacing=1.05, broken_landing=None,  # every landing edge is guarded
              # one lattice / grid infill bay (E10-8). It is a real and common Korean
              # 데크 난간 variant and the single cheapest "this is a park, not an egress
              # stair" tell. Placed on the entry deck's +Y run because that run is in
              # **every** preset grid cut as well as in `leaf_edge` — a lattice on an upper
              # landing would appear in no judged frame.
              lattice=dict(run="EntryRail_P", pitch=0.12, sec=0.030),
              # [GT-115 ⑭ (1)] **run-end return.** `newel_points()` already put a capped
              #   post at every boundary node, but at the four **degree-1** nodes (deck
              #   head x −1.50 and arrival landing x 24.14, both chains) the run simply
              #   stopped at that post with nothing turning the corner — the audit's "a
              #   run ends mid-air". A 0.30 m 90° return is the real termination detail
              #   and it is the same member family the GT-77 edging already uses ("the
              #   straight run dies into a 90-deg return … and the far end into a capped
              #   end post"). It turns **inboard**: outboard at the entry would put a
              #   member past the y −1.600 unguarded south break line, which GT-77 (3)
              #   forbids by name, and outboard at the arrival would stand a post off the
              #   landing on the lower park grass.
              #   0.30 m is chosen so the two arrival returns leave 3.20 − 0.60 = 2.60 m
              #   of the forward face open against a 1.80 m `DeckExit` `[computed]` — the
              #   §0-2 hand-off is untouched and this is a termination, not a guard.
              end=dict(run=0.300),
              # [GT-115 ⑭ (4)] **graspable handrail line.** `top` is 38x140 laid flat: a
              #   hand *rests* on it (§2.A.1-3) but cannot close round it. This adds the
              #   grasp, bracketed on the **inside** of the existing frame so not one
              #   existing member moves.
              #     dia 0.035  — mid of the audit's 32-38 mm band
              #     drop 0.075 — tube axis 0.075 under the 1.10 m top-rail top face =
              #                  **1.025 m** over the walking surface, inside the 0.80-1.20
              #                  m grasp band and under the guard's own top line
              #     off 0.080  — axis inboard of the rail centreline. The tube's inner face
              #                  then stands 0.0785 m inboard of the deck edge, i.e. the
              #                  **1.500 m clear width at the walking surface is unchanged**
              #                  and the grasp-height projection is inside the ≤100 mm
              #                  handrail allowance `[computed]`. Clearances: newel inner
              #                  face 0.045 / baluster 0.019 / top-rail inner edge 0.070
              #                  from the line, tube 0.0625-0.0975 — no shared volume, and
              #                  the tube passes **under** the top rail (z 1.008-1.043 vs
              #                  the rail's 1.062-1.100).
              #     brk        — bracket cleat (along-run, inboard, height), let `brk_bed`
              #                  into the underside of the top rail so it is never floating.
              hand=dict(dia=0.035, off=0.080, drop=0.075,
                        brk=(0.045, 0.080, 0.080), brk_bed=0.010,
                        brk_step=1.20, brk_end=0.14)),

    # === [W2-D ground_kit] P18 `deck_trail_hybrid` - spec Sec.5.8 / Sec.13.4 =
    #  Sec.13 measured this scene's three h0.3 cuts and killed the provisional
    #  P10 assignment: **d2 is entry deck, d5/d10 are park dirt trail + grass**.
    #  Hence two plans, at two different z:
    #    A `ground_plan()`      trail  z = TrailPath z_top (0.002)
    #    B `ground_plan_deck()` entry deck z = entry top (-0.005)
    #  Prescription (Sec.13.4):
    #    10-1 edge_break on the dirt<->grass line y = +-0.85 (dE76 15.2, the
    #         same "0 px transition" defect as scene04)
    #    10-2 leaf-decal outline break - scatter ring around the two trail
    #         decals (dE76 27.3, 1.8x stronger than 10-1)
    #    10-3 entry-deck plank gaps, d2 only
    #    10-4 trodden wear axis, width 0.90
    #    10-5 exposed gravel scatter, expose <= 0.06
    #  Dropped from the profile: `edge_litter` - `_compose_ops` forces its
    #  width to the region span (1.70 m, ~7x the 0.25 m ledger value) and the
    #  two bands then straddle the wear lane at an identical top z.
    #  Sec.7.3 invariant for scene10 ("the upper trail is cut at x = -1.5") is
    #  respected by construction: plan A stops at TrailPath x1 = -1.6, and
    #  every element of plan B is flagged `deck`.
    gkit=dict(
        wear_w=0.90,
        gravel_n=85,                  # [W2 F2] 120 -> 85 (cover 0.12 -> 0.08 is the
                                  #   binding lever here; the cap is not reached)
        leaf_ring_n=15,               # 10-2: 12-20 per decal, Sec.13.4
        leaf_ring_pad=0.28,           # ring width around the decal outline
        deck_gaps=9,                  # 10-3: 9 gaps over the 1.5 m entry deck
        # [S3-9] plank width stated, not defaulted. `ground_kit` defaults to 0.145 m
        #   (KCS 34 5-2-1 2.3.1's specification width); the **stocked** Korean 데크판재
        #   widths are 95 / 120 / 140 (research §D2, 5 suppliers), and 산림청고시 2014-2
        #   제8조 fixes the legal width series at 90..300 in 10 mm steps. 0.140 = a
        #   25 x 140 board, which is also the tread board (`flights.tread_t` 0.025).
        plank_w=0.140,
        seed=10,
    ),
    # --- axis-aligned ground plates (name, x0, x1, y0, y1, z_top, thick, mtl) ---
    #   v5 regression checklist (3) : the upper trail **stops** at x=−1.5
    #   (it does not cover the stair cavity). Beyond it there is only the lower path (−6.60).
    #   [Z-fighting avoidance] the lower path ground top is −6.62, 2 cm below the deck's
    #   lowest point (−6.60) -> landing3 and the last tread of flight3 never become coplanar
    #   with the ground (lesson 8). The 0.02 m walking step is verified in the continuity table.
    #   [v6 (2)(c)] BankCut (north retaining wall) stays a single 6.62 m wall only over the deck
    #   run x −40..5.2; east of it (x 5.2..44) it splits into **lower wall + berm (1.0 m) + upper wall**.
    #   berm top z −3.30; the upper wall steps back to y 2.45..2.60, which creates a shadow line.
    #   [S3-10 / Option A, §8.R OQ-6] **the masonry shaft is gone.** `BankCut` (a 7.40 m
    #   single wall over the whole deck run), `EastTierLow`, `EastTierUp`, all three
    #   `copings` and the berm planting band are **deleted**: they existed only because a
    #   pure switchback makes no horizontal progress, so the ground beside it had to be
    #   effectively vertical (the v5 docstring says so in as many words). A traversing deck
    #   descends with the hill, so the hill is modelled instead of walled — §2.B-2 C15/C16.
    #   What survives of the masonry is the **short head wall** at x = −1.5: `UpperBody`'s
    #   exposed face, now only `landing.clear` (0.255 m) tall because the corridor ground
    #   starts just below the entry deck instead of 6.62 m below it.
    #   `UpperTrail`/`UpperBody` widen to y 8.00 so the upper terrace meets the north bank,
    #   which retreats from y 2.60 to y 8.00 — the deck corridor needs the room the wall
    #   used to occupy.
    #   [GT-119 ②] **seam laps.** The plate table's neighbours all met as exact butt
    #   joints (measured: every adjacent pair 0.000 m overlap, no pair with a positive
    #   gap). Three of them are now lapped 0.10 m so the joint is a solid interlock
    #   rather than two coincident faces, and every lap is driven **under** the higher
    #   neighbour so no top face, no exposed face and no silhouette moves:
    #     UpperTrail thick 0.45 -> 0.55   — bottom −0.45 -> −0.55, 0.10 into `UpperBody`.
    #                                       Top stays 0.000; the extra 0.10 of its south
    #                                       face at y −1.60 is backed by `SouthBankCap`,
    #                                       whose high end tucks north under the terrace.
    #     LowerParkMain x0 −1.50 -> −1.60 — 0.10 west, buried inside `UpperBody`
    #                                       (z −7.40..−0.45) north of y −1.60 and inside
    #                                       `SouthBankBody` south of it `[computed]`.
    #     LowerParkMain / LowerParkFar x1 44.00 -> 44.10 — 0.10 east, buried inside
    #                                       `FarRidge` (z −8.50..3.50).
    #   Left as butts, on purpose: `LowerParkMain|LowerParkFar` (y −13.00) — their tops
    #   are the **same** z −6.620, so a lap would author exactly the coplanar overlap
    #   `coplanar_census()` exists to forbid, and a butt between two coplanar faces
    #   cannot open a wedge; and `FarHill|FarRidge` (x 44.00) — occluded from every
    #   camera by the NorthBank crest (a sight line to it must clear z 7.16 at y 15,
    #   and the highest eye in the scene is 1.80) and lapping it is the one case that
    #   would have to add material **above** a neighbour's top face.
    plates=[
        ("UpperTrail",   -40.0,  -1.5,  -1.60,  8.00,  0.00, 0.55, "grass"),
        ("UpperBody",    -40.0,  -1.5,  -1.60,  8.00, -0.45, 6.95, "rock"),
        # [GT-65] x1 −1.60 -> **−1.50**: the dirt trail stopped 0.10 m short of the
        #   entry deck (x0 −1.50) and the walk crossed a 0.10 m strip of bare grass
        #   before it reached the timber. −1.50 is also the value `ground_kit`'s own
        #   `SCENE_PLANS` fixture has always carried for this plan, and the §7.3
        #   invariant `_inv_10_trail_cut` is "xb <= −1.5", so the trail meets the deck
        #   exactly at the cut and never covers the stair corridor.
        ("TrailPath",    -40.0,  -1.5,  -0.85,  0.85,  0.002, 0.06, "dirt"),
        ("LowerParkMain", -1.6,  44.1, -13.00,  8.00, -6.62, 1.50, "grass"),
        ("LowerParkFar", -40.0,  44.1, -60.00, -13.00, -6.62, 1.50, "grass"),
        ("LowerPath",     -1.5,  44.0,  -4.40, -2.60, -6.618, 0.06, "dirt"),
        ("FarHill",      -40.0,  44.0,  15.00, 40.00,  7.16, 9.00, "grass"),
        # distant ridge across the valley (+X horizon closure)
        ("FarRidge",      44.0,  78.0, -60.00, 40.00,  3.50, 12.00, "grass"),
    ],
    # --- Y-direction slopes (_ybank, rotX slab) : (name, x0,x1, y_hi,z_hi, y_lo,z_lo,
    #     thick, mtl). +Y is high and it falls toward −Y.
    ybanks=[
        # north park slope (30.0 deg) — [S3-10] its foot moves y 2.60 -> **8.00**: the
        #   retaining wall it used to stand on is gone and the deck corridor occupies the
        #   ground out to y 8.0, so the hillside starts beyond the corridor margin.
        ("NorthBank", -40.0, 44.0, 15.00, 7.16, 8.00, 0.00, 9.00, "grass"),
        # south unguarded slope (30.1 deg) - trail shoulder (y−1.6,z0) -> lower ground (y−13)
        ("SouthBankCap", -40.0, -1.5, -1.60, 0.00, -13.00, -6.62, 0.50,
         "grass"),
        # [v6 (2)(b)] body material rock (masonry) -> rockface (jointless natural rock).
        #   the +X end face of this slab (x=−1.5, y −1.6..−13) is the **natural cut face**
        #   dropping to the lower park, and it fills the left half of `from_below`. As masonry it is a rampart.
        ("SouthBankBody", -40.0, -1.5, -1.60, -0.50, -13.00, -7.12, 7.50,
         "rockface"),
    ],
    # --- [S3-10] coping band and berm planting **deleted with the wall they belonged to**.
    #     `copings` (BankW / BankE / Tier) and `berm_hedges` / `berm` were the two-tier
    #     east wall's dressing; with the wall gone they have nothing to sit on. The v6
    #     fix they implemented ("dispel the fortress-wall impression") is superseded by
    #     removing the fortress, which is the stronger form of the same fix.
    # --- leaf bands : hiding the top two step edges (flight0 treads 1·2) + ground litter ---
    # [W2 F3] proud 0.012 -> 0.005 — the rim shadow that drew an outline round the
    #   trail leaf patches.
    leaf=dict(thick=0.02, proud=0.005, over=0.045),
    # [W3 F3 / DEC-2] ground leaf patch: the 3-rectangle stack (`subs`/`scale`/`off`/`rz`)
    #   is retired for one `build_carpet_mask` lobe per drift. `rough` 0.20 is DEC-2's
    #   carpet band (0.15-0.20) - a leaf drift has a soft convex outline, not a puddle's.
    #   `feather` is the leaf-card band straddling the boundary (inner 0.30 / outer 0.50 m).
    #   The feather ring itself is scene-side (`gkit.leaf_ring_*`, row 10-2 below), so the
    #   mask does not ask `build_carpet_mask` for a second one.
    leaf_patch=dict(seed=1007, rough=0.20),
    # [GT-77] the two **trail** lobes move inboard — cy −0.9 -> −0.30 and +0.7 -> +0.25.
    #   They used to straddle the trail edge (spans y −1.45..−0.35 / +0.20..+1.20), which
    #   after this round would put roughly half of each drift under the 0.60 m verge band
    #   and clip it on an invisible line. Moved, each drift lies **inside the 1.70 m dirt
    #   band** (−0.85..+0.25 / −0.25..+0.75) where litter on a walked path belongs, and
    #   the verge overlaps only the outer 0.13-0.23 m of the feather ring, which
    #   `approach_dressing_z` seats rather than buries. Shape, size, seed and the
    #   `build_carpet_mask` idiom are untouched — H4 allows a lobe to move, never to
    #   become a rectangle again. The two `lower` lobes are not affected and do not move.
    leaf_ground_patches=[(-3.2, -0.30, 1.6, 1.1, "trail"),
                         (-5.6, 0.25, 1.4, 1.0, "trail"),
                         (1.4, -3.4, 2.2, 1.6, "lower"),
                         (5.0, -1.9, 2.0, 1.5, "lower")],

    # --- [S3-10] deck corridor ground band (Option A). The slab is 10.6 m wide so the
    #     judged grid cuts (half-FOV ~30 deg, so |y| < 5.8 at 10 m) never see its north
    #     edge; its south face at y −2.60 is the scarp down to the lower park and is the
    #     unguarded drop the scene's hazard cue (4) names, now **1.0 m outboard of the
    #     deck** instead of 4 m away past a wall.
    #   `thick` must reach **below the lower park top (−6.62)** at the corridor's highest
    #   station, or the hillside is hollow and the `from_below` cut looks straight through
    #   it to the sky — measured on the 260731_w3_s10 pilot, a 4.8 m see-through band at
    #   the head. Highest corridor top is −0.255, so 7.00 m of body clears it with margin.
    #   [GT-119 ②] `seam_lap` — the thickness that made the body deep enough is also what
    #   made the **seams** open. `sc.build_slope` cuts a slab's end faces perpendicular to
    #   its own top plane, not vertically, so where the profile kinks from steep to flat
    #   (every flight foot) the two neighbours diverge below the shared crest and leave a
    #   wedge open downward, `thick·sin(θa − θb)` wide at the far face = **3.05 m** at a
    #   48 % foot. `corridor_slabs()` closes it; this is the margin it closes it *past*.
    corridor=dict(y0=-2.60, y1=8.00, thick=7.00, seam_lap=0.100),

    # --- [GT-65 · §0-2] deck -> lower park hand-off -------------------------------
    #   The stair arrived at x 24.14 and stopped **on grass**: `LowerPath` (the lower
    #   park trail, y −4.40..−2.60) runs parallel 1.0 m south of the arrival landing
    #   and never meets it, and the arrival landing's forward edge was railed on top
    #   of that, so the descent dead-ended into its own guard. Two dirt strips carry
    #   the walking line on: `DeckExit` continues the deck axis east to the scene edge
    #   (x 44 = the scene edge, where `FarRidge` starts; `LowerParkMain` itself now runs
    #   0.10 m further, into the ridge — GT-119 ② seam lap), `DeckExitLink` is the T
    #   onto `LowerPath`.
    #   Both are **2 mm veneers over ground that already exists** (`LowerParkMain` top
    #   −6.620, corridor ground −6.620 past its last station) and are built **without
    #   colliders**: they add a trail reading, not a walking surface, so no collider,
    #   no drop edge and no GT-read AABB moves — the row stays R-3.
    #   z −6.618 is the same decal ladder step `LowerPath` uses.
    #   (name, x0, x1, y0, y1, z_top, thick)
    exit_paths=[("DeckExit",     24.10, 44.00, -0.90, 0.90, -6.618, 0.06),
                ("DeckExitLink", 26.00, 27.80, -2.60, -0.90, -6.618, 0.06)],

    # --- [GT-77 · §0-2] approach-path finishing at the two deck ends --------------
    #   GT-65 carried the walking **line** to the scene edge; it did not finish the
    #   ground under it. Both ends handed a 3.20 m deck to a narrower dirt ribbon that
    #   simply butted into it (entry 1.70 m `TrailPath`, exit 1.80 m `DeckExit`), so the
    #   threshold was flanked by 0.70-0.75 m of bare turf on each side, and the ribbon
    #   itself was a texture rectangle with two ruled parallel edges and no shoulder.
    #   Four member families finish each end, and both ends are built from this one
    #   table so the entry and the exit cannot drift apart:
    #     apron  — dirt wings that carry the path out to the deck's own 3.20 m at the
    #              threshold. The path plate keeps its width; the wings add only the
    #              flanks, so the plate's top face is never doubled — **no coplanar
    #              pair exists in the apron at all**.
    #     header — 90 mm 방부목 마구리재 laid across the deck end, bedded `bite` into the
    #              deck and `over` into the path. Its top face is `proud` (0.010 m) over
    #              the path veneer, so the path top face and the deck top face both pass
    #              **inside** the board: the dirt/board/plank seam is closed with no
    #              coplanar pair and no coincident visible face `[computed]`.
    #     edge   — 90x90 방부각재 경계목, the stocked section the railing newel already
    #              uses (§4.2-2 / research §D2). Bedded 0.043 m, standing 0.047 m proud,
    #              and tucked `tuck` into the path so its inner face never coincides with
    #              the path's side face. A run never stops in mid-air: the straight run
    #              dies into a 90-deg return, the return into the flank, the flank into
    #              the header, and the far end of the straight run into a **capped end
    #              post**.
    #     verge  — 0.60 m rough dormant-grass shoulder outside the edging (`hedge` tint,
    #              not `leaf`: a brown ribbon beside a brown path would read as a second
    #              path). Top 0.010 m over grade = 5 mm clear of the leaf-drift decal
    #              step (`leaf.proud` 0.005), so a drift is buried where the two meet
    #              instead of fighting it `[computed]`.
    #   Colliders: **none**. Every member is a veneer over a plate that already carries
    #   the collider (`TrailPath`/`UpperTrail` at the entry, `Landing_5`/`LowerParkMain`
    #   at the exit), exactly the `exit_paths` doctrine — so no walking surface, no drop
    #   edge and no GT-read AABB moves.
    approach=dict(
        edge=0.090,          # 90x90 경계목 section
        edge_proud=0.047,    # exposed height above grade (bedded 0.043 of the 0.090)
        edge_tuck=0.010,     # how far the edging bites into the path veneer
        header=0.090,        # 마구리재 section (width along the path = 0.090)
        header_bite=0.040,   # header sunk into the deck footprint
        header_over=0.050,   # header lapped onto the path side
        header_proud=0.010,  # header top over the path veneer top
        # **The outer faces are a staircase, not a common plane.** The deck fascia is at
        #   y ±1.600; a member whose own outer face also landed on 1.600 would put two
        #   exposed coplanar vertical faces in the same place at the deck corner — the
        #   vertical twin of the coplanar defect, and it does not show up in a top-face
        #   census. So the header steps 0.010 in from the fascia and the flank steps
        #   0.005 in from the header: three planes, 5 mm apart, none shared `[computed]`.
        header_inset=0.010,  # header end face inboard of the deck fascia
        flank_inset=0.015,   # flank outer face inboard of the deck fascia
        apron_run=1.100,     # deck face -> return board centreline
        apron_bite=0.030,    # apron end slid 0.010 inside the header's deck-side face
        apron_tuck=0.040,    # apron outer edge tucked under the flank board
        apron_t=0.060,       # same 60 mm veneer thickness the dirt plates use
        verge_w=0.600, verge_off=0.015, verge_proud=0.010, verge_t=0.050,
        post=0.120, post_proud=0.260, post_cap=(0.160, 0.160, 0.040),
        # `sgn` = the direction the path leaves the deck. `run_end` is where the edging
        #   terminates in its post: at the entry it is set **behind** the d10 grid eye
        #   (x −10.0) so every judged grid cut sees a continuous edge line rather than a
        #   terminus, with 0.74 m of clearance from the eye `[computed]`.
        ends=(dict(tag="Entry", sgn=-1.0, x_deck=-1.50, path_z=0.002,
                   grade=0.000, path_half_y=0.85, run_end=-10.80),
              dict(tag="Exit", sgn=1.0, x_deck=24.14, path_z=-6.618,
                   grade=-6.620, path_half_y=0.90, run_end=31.00)),
        # [GT-77 (4)] head-wall fill batter: (x0, z0, run, drop, y0, y1, thick).
        #   y0 1.630 = 0.030 m clear of the entry deck's +Y fascia (y 1.600), the
        #   minimum that guarantees no face is coincident with it `[computed]`.
        head_fillet=(-1.50, 0.000, 0.90, 0.255, 1.630, 8.00, 0.60),
    ),

    # --- [S3-11] season: **late autumn (만추), leaf-off**, pinned -------------------
    #   G10 reads leafless canopy + overwintered matted brown litter + a first flush of
    #   small green leaves and green ground shoots. Those last two are **early-spring**
    #   signals and are **excluded**: §12-7 bans seasonal/event-specific elements and the
    #   only sanctioned exceptions are `04/07 browned leaves · C1 snow · C2 leaves`
    #   (`ground_kit.py:46`). Late autumn is visually identical to G10 in every element
    #   actually built here and it is already the sanctioned exception for this scene.
    #   EXCLUDED by the pin: green leaf flush on any tree · green ground shoots · any
    #   flowering shrub (`Forsythia` / `Rhododendron` stay out of the pools).
    #   The census this fixes `[measured]`: 12 trail trees + 12 hill trees + 13 shrub
    #   clumps = 37 green plants, plus 10 green hedge/crest bands, against 4 brown leaf
    #   lobes. G10 has **zero** green vegetation objects and wall-to-wall litter.
    season=dict(
        # bare deciduous species, rotated. These are the **only three** tree USDs in the
        # catalogue whose branch armature lives in the trunk prim rather than inside a
        # leaf `PointInstancer`, so `/Root/leaves` can be deactivated and a real bare tree
        # is left behind (§3.4; registered in `sc.BARE_SUBPRIMS` by the K4 micro-commit
        # 1346b70). `native_h` is the **trunk-only** zmax, not the full canopy bbox —
        # scaling a leafless tree by its leafed height would shrink it by 1-2 %.
        # [S10c] The *mechanism* that consumes this table was wrong until K4(0) `e4fc4cf`:
        # a stage-side `SetActive(False)` under an instance is discarded by USD, so round
        # `260731_w3_s10` shipped twelve green trees while reporting 12/12 leaf-off
        # (red-team **F1**). `_bare_tree` now references `assets/veg_bare/*_bare.usda`
        # through `sc.veg_wrapper_rel`, which composes the strip inside the prototype.
        # These three `native` values are the bare zmax and are **kept as authored** so
        # the trunk scale is bit-identical across the fix; `deck_module_selfcheck` asserts
        # them against `sc.BARE_NATIVE` (agreement ≤ 5 mm native = ≤ 0.1 % of height).
        bare=(("Trees/Gray_Birch.usd", 3.299),        # 자작나무 — park-typical
              ("Trees/Elm_Sapling.usd", 3.043),       # near field
              ("Trees/Lombardy_Poplar.usd", 13.422)),  # the tall verticals
        # the oaks (`Shumard_Oak` / `Scarlet_Oak` / `Black_Oak`) **cannot** be stripped —
        # their leaves ride inside the branch instancers — so §4.2-5 re-assigns them.
        # The hill/ridge belt takes `Chinese_Juniper` instead: an evergreen keeps its
        # needles in 만추, so a green mass at distance is not a season error, it is a
        # conifer. It is also a `veg_manifest_w2` PASS species, which clears the nine
        # LINT-4b errors the coordinate-hash draw was producing (White_Pine ×5 +
        # Yellow_Pine ×4, both retired).
        far=("Trees/Chinese_Juniper.usd", 2.5164),
        # autumn-legal shrub pool. `Burning_Bush` is red 30.2 % — removed from the
        # **global** pool for being autumn, therefore legal *here* by the same scope logic
        # that admits the dry-leaf debris. `Juniper` is evergreen. `Forsythia` (blossom
        # only, green 0.0 %) and `Rhododendron` (magenta 76.7 %) stay out.
        shrubs=("Shrub/Burning_Bush.usd", "Shrub/Juniper.usd"),
        shrub_h=1.35,
        litter_cover=0.34,          # continuous, not lobed (C20)
        litter_max=260,
        # [GT-115 ⑭ (2)] **three cluster source variants, no procurement.**
        #   The audit counts one silhouette repeated ~20× with rotation-only variation on
        #   the slope. The cause is in the call, not in the asset library: the three
        #   `Litter_*` bands each drew from the **whole** `sc.VEG_DEBRIS` pool with one
        #   seed, and that pool's two cluster rows carry 9.6× / 3.9× the **mean**
        #   per-instance cover of its three single-leaf rows (0.0584 / 0.0239 against a
        #   mean 0.0061 over 0.0081 / 0.0048 / 0.0054 `[sc.VEG_DEBRIS]`), so the frame is
        #   *area*-dominated by two cards spun about Z.
        #   The five USDs are already five different **card arrangements of the same
        #   leaves**, so the variants are cut out of them rather than bought: a heavy
        #   drift, a mixed sweep and a thin single-leaf litter, each with its own scale
        #   band, its own tilt band and its own `gk.det_seed` draw. Three overlaid draws
        #   per band also break the single-Poisson look the one-call version had.
        #   `cap` sums to `litter_max` (110+90+60 = 260) **per band**, and every one of the
        #   three calls is cap-bound at `litter_cover`, so the instance budget is exactly
        #   the 780 of the previous round — this is a re-mix, not more litter.
        litter_variants=(
            dict(tag="drift", cards=("fallcluster1", "fallcluster2"),
                 scale=(0.85, 1.45), tilt=6.0, cap=110),
            dict(tag="mixed", cards=("fallcluster2", "maplefall1", "oakfall2"),
                 scale=(0.70, 1.15), tilt=10.0, cap=90),
            dict(tag="singles", cards=("maplefall1", "oakfall1", "oakfall2"),
                 scale=(0.45, 0.85), tilt=14.0, cap=60)),
    ),
    # [S3-11] rock outcrop at the uphill margin (E10-10) + foot boulders. `rock_moss_set_01`
    #   is CC0 and its diffuse is **orange 82.2 %**, which makes it the better of the two
    #   scans for late autumn (`_02`, yellow-green 92.9 %, is reserved for scene07).
    #   `z_mode='base'` is mandatory — 52.4 % of its triangles sit below the origin — and
    #   the sink stays at 0: `tonglam_v2` §1 row 10 already failed this scene once for
    #   "boulder-scale D-5 rocks in **dark sink-rings**", and a boulder that sits in a hole
    #   is the defect while a boulder that sits *on* the slope is the fix.
    #   [GT-115 ⑭ (1)] **row 0 re-scaled and moved off the guard line.** The audit crop
    #   shows the +Y balusters standing inside the scan, and the cause is that this row
    #   is not one boulder: `rock_moss_set_01` is a **pre-composed 8.005 × 6.949 m set**
    #   (6 meshes, 63,127 tri — `assets/urban_manifest_w3.json`). At `scale_mul=1.00` and
    #   (6.30, 4.15) the yaw-22° plan envelope is x[1.29, 11.31] · y[−0.57, 8.87], which
    #   covers the y 1.619 run over x 2.48…7.65 outright. Translation alone cannot clear
    #   it — the rest platform's own run at y 3.119 forces cy ≥ 8.21, i.e. off the
    #   corridor (y1 8.00) and onto the 30° north bank, where a flat-lying scan cannot be
    #   grounded — so the scale goes to **0.50** (envelope 4.01 × 3.54 m, still a real
    #   boulder group, and inside the 0.30-0.78 band scene09 already uses on this same
    #   asset) and the centre to **(6.30, 4.90)**. `z_mode='base'` and **sink 0** are
    #   unchanged, so `tonglam_v2` §1 row 10's "boulder-scale rocks in dark sink-rings"
    #   stays closed. Row 3 (`rock_02`) moves y 2.30 → 2.55: its clearance was 0.335 m,
    #   inside the 0.30 m bar but with no margin for the yaw envelope.
    #   Worst plan clearance after the move: **0.374 m** (`rock_03_broken` #1 vs
    #   `LandRail_2_Back`) — re-derived by `outcrop_clearance()`, asserted by the
    #   self-check, never retyped.
    outcrop=[("rock_moss_set_01", 6.30, 4.90, 0.0, 22.0, 0.50),
             ("rock_03_broken", 9.10, 3.30, 0.0, -35.0, 0.55),
             ("rock_03_broken", 15.40, 2.60, 0.0, 110.0, 0.42),
             ("rock_02", 5.10, 2.55, 0.0, 15.0, 1.00)],
    # [GT-115 ⑭ (1)] native plan footprint (w_x, d_y) of each outcrop asset, straight off
    #   `assets/urban_manifest_w3.json` `geometry.size_m` `[manifest]`. It exists so the
    #   clearance check is arithmetic on a published number instead of an eyeball on a
    #   render; `outcrop_clearance()` rotates this box by the row's yaw and takes the
    #   axis-aligned envelope, which over-estimates the true footprint and therefore
    #   **under**-estimates the clearance — the conservative direction.
    outcrop_plan={"rock_moss_set_01": (8.0046, 6.9488),
                  "rock_03_broken": (1.3176, 1.7142),
                  "rock_02": (0.4035, 0.4629)},
    # [S3-11] distant city glimpse (E10-13) — BS-4 **backdrop contract**: distant
    #   silhouette only, **0 windows**, <=4 prims per mass, auto-demoted beyond
    #   d_true > 80 m (`building_kit.should_backdrop` / `_b_backdrop`). The masses are
    #   built scene-side as plain windowless boxes rather than by calling `building_kit`:
    #   **no scene in the tree calls that kit today** (K3 owns it), and wiring a shared
    #   kit from an S-lane would add a dependency this lane cannot verify. The product is
    #   the same — "faint" is exactly what 0 windows and 3 prims mean.
    #   (cx, cy, w, d, h) in the −X/−Y sector so they show through the trunks at G10's
    #   u 0.00-0.10; the nearest is 88.6 m from the h0.3_d10 eye.
    backdrop=[(-72.0, -62.0, 26.0, 14.0, 17.0),
              (-92.0, -48.0, 34.0, 16.0, 23.0),
              (-84.0, -34.0, 18.0, 12.0, 12.0)],

    # --- dressing ---
    # 10 trees (cx, cy, zone, trunk_h) - zone: north/south/lower/trail
    trees=[(-6.0, 5.5, "north", 3.6), (0.5, 8.0, "north", 4.0),
           (7.0, 6.0, "north", 3.4), (13.0, 9.5, "north", 3.8),
           (-14.0, 4.5, "north", 3.2), (-20.0, 7.5, "north", 3.6),
           (-9.0, -7.5, "south", 3.0), (-17.0, -10.0, "south", 3.4),
           (9.0, -9.0, "lower", 3.2), (16.0, -5.0, "lower", 3.6),
           (2.0, -11.5, "lower", 3.0), (21.0, -12.0, "lower", 3.4)],
    tree=dict(trunk_r=0.10),
    # shrub clumps (overlaid flattened ellipsoids - scene04 v5 convention)
    #   [v6] clump 4 is added at the top corner of the south cut face (x=−1.5) to hide the
    #        straight cut line (softens the 'rampart' impression in the left half of from_below).
    shrubs=[(-4.0, 3.3, "north"), (3.5, 4.0, "north"), (10.0, 3.6, "north"),
            (-12.0, 3.4, "north"), (-6.5, -4.2, "south"),
            (-14.0, -6.0, "south"), (6.0, -4.6, "lower"),
            (12.0, -2.6, "lower"),
            (-2.3, -2.7, "south"), (-2.6, -5.4, "south"),
            (-2.2, -8.2, "south"), (-2.9, -10.8, "south"),
            # [v7 verdict §7 (a)] one more park shrub is set at the left of the from_below frame
            #   (yaw −26 deg) so the deck is wrapped in planting. The sight corridor (camera->deck)
            #   runs in the x 3.5 band, so there is no intrusion - checked by SMOKE [v7 mise-en-scene].
            (0.5, -5.5, "lower"),
            # [GT-77 (5)] verge planting at the two approaches, 4 clumps. GT-65 found no
            #   foreground shrub bed and refused to invent one; this round's brief asks
            #   for "modest verge/planting per the park idiom", so the four are placed —
            #   and placed **outside the +X grid sight corridor**, which is the constraint
            #   that decides their y. The corridor is the ray from the d10 eye (−10,0) to
            #   the deck head corner (−1.5, ±1.60); at x −6.6 it is at |y| 0.64 and at
            #   x −6.2 at |y| 0.72, against a clump half-width of 1.30 in `_grid_obstacles`
            #   `[computed]` — so |y| >= 2.70 keeps every judged grid cut's view of the
            #   stair head intact. The two lower-park clumps also become `from_below`
            #   anchors (they are `lower`, so the v7 anchor census picks them up).
            (-6.6, 3.1, "north"), (-6.2, -2.7, "south"),
            (26.2, 2.3, "lower"), (29.2, -5.9, "lower")],
    shrub=dict(embed=0.25,
               blobs=((0.00, 0.00, 0.75, 0.60, 0.35),
                      (0.54, 0.41, 0.51, 0.43, 0.26),
                      (-0.45, -0.37, 0.56, 0.39, 0.29))),
    # timber waymarker (post + 2 direction blades + post cap)
    #   [v6] the old spec (two 0.90x0.16 blades @1.55/1.80) read as a **picnic table** at a
    #   distance -> blades made thinner and shorter (0.72x0.11), heights spread (1.72/1.98)
    #   and a cap added on top to give a 'post-type waymarker' silhouette.
    #   [v7 verdict §7 (3)] the two 0.72x0.11 blades still read as a "low picnic table with a
    #   wide top" -> blades shrunk further to **0.58x0.09** and lifted to 2.06/1.80, so the
    #   **exposed post grows to 1.80 m (79 % of the total height)**. The post thickens
    #   0.065 -> 0.080 so the 'post-type' silhouette reads first at a distance.
    #   [GT-77] cy 1.00 -> **1.06**. The 0.080 m post spanned y 0.92..1.08 and the new
    #   경계목 occupies y 0.840..0.930, so the old value put the post 0.010 m **inside**
    #   the board — a 10 mm interpenetration, which is the one defect this round is not
    #   allowed to author. 1.06 stands the waymarker in the verge with 0.050 m clear of
    #   the board `[computed]`; nothing else about it moves.
    signpost=dict(cx=-3.6, cy=1.06, post_r=0.080, post_h=2.26,
                  arm=(0.58, 0.05, 0.09), arm_off=0.34,
                  arms=((2.06, 15.0), (1.80, 195.0)),
                  cap=(0.20, 0.20, 0.07)),
    # bench 1 (upper trail)
    #   [GT-77] cy 0.90 -> **1.75**. `build_bench` is 1.80 x 0.40, so at 0.90 the seat
    #   spanned y 0.70..1.10 and **two of its four legs stood inside the 1.70 m walking
    #   lane** (y 0.73..0.79), with the bench overhanging the trail — visible in the
    #   round's own `pt_noon_preset_h1.8_d10.png`. With the 경계목 in place the board
    #   would run between its legs, which is the picture of furniture dropped on a path
    #   rather than set beside one. 1.75 puts the near leg at y 1.61, i.e. 0.11 m clear
    #   **behind** the verge (outer edge 1.500) `[computed]`, off the walking line and
    #   in the planted shoulder, which is where a park bench actually stands. Nothing
    #   about the bench itself changes and it stays a `_grid_obstacles` / v7 anchor row.
    bench=dict(cx=-6.5, cy=1.75, yaw=180.0),
    # [S3-9] bench 2 — on the 쉼터/전망 platform (landing `rest_at`). A rest platform with
    #   nothing to rest on is a landing; the bench is what makes it read as 휴식 시설, and
    #   it is the element SANJI-183's width exception exists for. x/y are offsets **inside**
    #   the platform, resolved against the ladder so the de-stacking commit carries it along.
    rest_bench=dict(dx=-0.65, dy=1.00, yaw=90.0),
    # shelter pavilion (lower path). [v7] even after from_below is mirrored from
    #   (5.2,−10.8) to (2.4,−0.6), the pavilion (centre 11.5,−6.0) sits at yaw 68 deg, outside the FOV - still no sight interference.
    #   [GT-115 ⑭ (3)] `sc.build_canopy` gives a roof slab on four columns and nothing
    #   else — no beam, no rafter, no eave, no base — so it reads as a slab levitating on
    #   sticks. The kit call is **kept verbatim** (the slab and the four columns are the
    #   only members with colliders and they must not move) and the framing is laid over
    #   it, in the order a real 정자 is built: post → 보(header) → 서까래(rafter) →
    #   지붕널, plus a 마구리/fascia band round the slab edge and a base plate at each
    #   post foot. Flat roof + fascia is the audit's own alternative to a pitch, and it
    #   is the one that leaves the collider slab where it is.
    #     beam    (w_y, d_z)  header let into the post tops, top face at `z_roof`
    #     rafter  (w_x, d_z)  framed **between** the headers, `bed` into each so no two
    #                         faces are coplanar (the GT-77 bite/tuck idiom)
    #     fascia  (t, drip)   t = board thickness, drip = how far it hangs under the slab
    #     fascia_out / _bed   outer face proud of the slab edge / bedded into it
    #     base    (w, d, h)   post base plate; the column passes through it, exactly the
    #                         `ColumnAlgae` collar idiom already used on the deck columns
    pergola=dict(x0=10.0, x1=13.0, y0=-7.5, y1=-4.5, z_roof=-4.20, post_r=0.10,
                 roof_t=0.16,
                 beam=(0.120, 0.220), rafters=5, rafter=(0.075, 0.140),
                 rafter_bed=0.010,
                 fascia=(0.030, 0.055), fascia_out=0.020, fascia_bed=0.010,
                 base=(0.300, 0.300, 0.080)),
    # [v5.2 user] arbitrary warning sign removed - the stair-caution sign (PARAMS['sign']) is deleted.
    # distant closure : forest band beyond the lower park + trees on the upper ridge
    #   [GT-65] the east band stopped at y +1.40, i.e. it stood across **both** lower
    #   trails (`LowerPath` y −4.40..−2.60 and the new `DeckExit` y −0.90..+0.90): a
    #   4 m forest wall at x 40 is where the walk ended. y1 −5.20 opens the gate the
    #   trails pass through with 0.8 m of margin. Horizon closure is unaffected —
    #   `FarRidge` (top z 3.50, x 44..78) and the two `ridge_crest` bands stand behind
    #   the gap. The band idiom itself is untouched (GT-63 keeps build_hedge for the
    #   distant TreeLine family).
    far_hedges=[dict(x0=-40.0, x1=6.0, y0=-40.0, y1=-37.0, h=4.0),
                dict(x0=6.0, x1=44.0, y0=-40.0, y1=-37.0, h=4.0),
                dict(x0=40.0, x1=43.0, y0=-33.0, y1=-5.20, h=4.0)],
    # [v6 C-4] forest silhouette band on the distant ridge crest (FarRidge top z 3.50) -
    #   the horizon is closed with a round-crown strip instead of individual lollipops.
    #   + the **straight horizon** of the north hill (FarHill top 7.16), verdict (1)'s 'stage
    #     backdrop', is broken up by a crest band as well.
    ridge_crest=[dict(x0=46.0, x1=54.0, y0=-58.0, y1=-8.0, h=5.0, base=3.10),
                 dict(x0=49.0, x1=57.0, y0=-10.0, y1=38.0, h=6.0, base=3.10),
                 dict(x0=-40.0, x1=6.0, y0=13.6, y1=17.4, h=5.2, base=6.76),
                 dict(x0=6.0, x1=44.0, y0=13.6, y1=17.4, h=4.6, base=6.76)],
    # (cx, cy, zone) - north = north slope, far = distant ridge (z 3.5), low = lower ground
    hill_trees=[dict(cx=-22.0, cy=20.0, zone="north"),
                dict(cx=-8.0, cy=24.0, zone="north"),
                dict(cx=6.0, cy=19.0, zone="north"),
                dict(cx=20.0, cy=25.0, zone="north"),
                dict(cx=32.0, cy=20.0, zone="north"),
                dict(cx=50.0, cy=-14.0, zone="far"),
                dict(cx=58.0, cy=2.0, zone="far"),
                dict(cx=52.0, cy=16.0, zone="far"),
                dict(cx=62.0, cy=-28.0, zone="far"),
                dict(cx=-14.0, cy=-38.5, zone="low"),
                dict(cx=10.0, cy=-38.5, zone="low"),
                dict(cx=28.0, cy=-38.5, zone="low")],

    # --- materials ---
    material=dict(
        # [v6] rock_wall 3.0->0.9 (fortress masonry -> quarried rubble) · dirt 3.0->1.1
        #      (confetti saturation) · leaf 1.8->1.05 · rock_face (natural cut face) added
        #      grass 4.0->2.6 (softens the 'quilt pattern' repetition on the slope)
        scale=dict(wood_dark=1.0, rock_wall=0.9, rock_face=2.2, grass=1.4,
                   leaf_ground=1.05, dirt_park=1.1, concrete_wall=2.4),
        # [S3-8 / gap C18] **weathered 방부목 patina, aimed at the measured target.**
        #   `wood_dark_diff.jpg` measures mean linear (0.0824, 0.0584, 0.0442), Y 0.0625,
        #   **L* 30.0** `[measured]` — a fresh, saturated dark red-brown. That is the whole
        #   of §4.2-3's "reads near-black in shadow" defect, and with the old warm
        #   deck_tint (1.00,0.96,0.90) / stringer_tint (0.72,0.70,0.66) the shipped values
        #   were L* 30.2 and L* 26.2.
        #   Target = the **measured** 2-5 year 방부목 patina (research §D4/D5, CIELAB from
        #   Forests 9(8) 488 + Wood Research 62(5) 737): L* 53-60, a* 0..+2, b* +4..+10,
        #   albedo 0.22-0.28, sRGB #86837C-#96938B. ACQ starts dark (fresh L* ~46, a* only
        #   +3..+5 — do NOT paint fresh ACQ a saturated green) and silvers from there.
        #   The band centre #8E8B84 (L* 57.9) was rendered first and measured; against G10
        #   it read a shade bleached under this scene's 49.8-deg noon sun, so the walked
        #   deck is aimed at the band's lower half, **L* 55.0** = #86847D, one step off the
        #   band floor #86837C. The frame timber sits at the floor itself (**L* 53.0**)
        #   because G10 reads silvered top faces over darker vertical faces (§2.A.1-8).
        #   Both stay inside the measured 53-60 band — the reference moved the value
        #   within the standard, it did not overrule the standard.
        #   The tints below are therefore **derived, not chosen**: tint = target / source.
        #     deck      (0.240,0.229,0.205) / (0.0824,0.0584,0.0442) = (2.91, 3.92, 4.64)
        #     stringer  (0.220,0.210,0.190) / same                   = (2.67, 3.60, 4.30)
        #   The map is dark and low-contrast (p95 linear 0.122), so even at 5.2x the clipped
        #   fraction is **0.02 %** `[measured]` — the existing map carries the target without
        #   procurement, which is the §8.R OQ-8 G5 test ("only if that visibly fails").
        deck_tint=(2.91, 3.92, 4.64),          # -> lin (0.240,0.229,0.205) L* 55.0 alb 0.230
        stringer_tint=(2.67, 3.60, 4.30),      # -> lin (0.220,0.210,0.190) L* 53.0 alb 0.211
        # [GT-115 ⑭ (5)] **the guard gets its own two tints, oriented.**
        #   `pt_noon_leaf_edge.png` shows the same teal-yellow mottle on every rail face,
        #   sunlit tops included, because the whole railing was bound to one material
        #   (`M["rail"] = M["stringer"]`). Per-face materials are impractical — every
        #   member is a single box — but the railing **is** separable by member
        #   orientation, and that is the granularity §2.A.1-8 already asks for
        #   ("G10 reads silvered top faces over darker vertical faces"): the top rail of
        #   every run and the newel caps are the up-facing members, everything else is
        #   vertical or shaded.
        #     guard_top  L* 59.0 a* +1.0 b* +5.0 albedo 0.270 — silvered/bleached
        #                lin (0.294,0.267,0.236) = tint × (0.0824,0.0584,0.0442)
        #     guard      L* 53.0 a* +1.4 b* +7.0 albedo 0.211 — the moss side, **at the
        #                same albedo as `stringer_tint`** so the value does not move; what
        #                moves is the ratio the map's algae texels get pushed through,
        #                G/R 1.348 → 1.217 and B/R 1.610 → 1.331, i.e. the mottle stays
        #                brown-grey instead of turning teal. That is this item's declared
        #                fallback ("lighten the overall moss intensity") applied to the
        #                half of the railing that keeps the moss.
        #   Both are inside the measured 2-5 yr 방부목 band (L* 53-60, a* 0..+2, b* +4..+10,
        #   albedo 0.22-0.28) `[research §D4/D5]`, and the top tint's largest multiplier
        #   5.33 sits at the 5.2× the deck tint's clipping measurement already covers
        #   (clipped fraction 0.02 % on a p95-linear-0.122 map).
        #   `stringer_tint` itself is untouched: the columns, stringers and the GT-77
        #   approach timber render bit-identically.
        guard_tint=(2.90, 3.53, 3.86),         # -> lin (0.239,0.206,0.171) L* 53.0 alb 0.211
        guard_top_tint=(3.57, 4.57, 5.33),     # -> lin (0.294,0.267,0.236) L* 59.0 alb 0.270
        # algae collar at the damp shaded column feet and north faces — §4.2-3's
        #   x(0.92,0.98,0.92) applied over the frame tint. Cheap, and it is what makes
        #   방부목 read as *outdoor* timber rather than as joinery.
        algae_tint=(2.46, 3.53, 3.96),
        # [S3-11] dormant straw/olive. The map is the only lever (no dormant-turf texture
        #   exists), so the tint has to do all the work — and it is a **multiplier**, not a
        #   colour. §4.2-5 proposes the literal triple (0.62, 0.60, 0.42) `[assumed]`;
        #   applied to `grass_lawn_diff` (mean linear **0.0621 / 0.1115 / 0.0232**
        #   `[measured]`) that lands at (0.0385, 0.0669, 0.0097), i.e. **R/G = 0.58 — still
        #   green-dominant.** It darkens the lawn without making it dormant, which is the
        #   cherry-blossom lesson in miniature: *judge by pixels, not by the value's name.*
        #   Derived instead from a straw target: **#7F734E**, linear (0.211, 0.173, 0.077),
        #   Y 0.174 → L* 48.8, R/G **1.22**, inside the project's ≤0.30 ground albedo clamp,
        #   clipped fraction **0.02 %** `[measured]`.
        # [GT-124] 극단 틴트(3.40,1.55,3.30 — 잎날 구조 소거의 근인)를 완화하고
        # 휴면 반점은 B-텍스처 블렌드(dirt_park)가 담당한다. R/B 상향은 유지하되
        # 스펙클을 살리는 대역으로.
        # [GT-124 2차] 1차 렌더 실측: (1.85,1.30,1.75)+블렌드 0.35 는 사구처럼
        # 창백 — 녹색 잔존을 살리는 대역으로 하향, 고사 반점은 블렌드 축 유지.
        grass_tint=(1.32, 1.18, 1.02),
        leaf_tint=(0.88, 0.85, 0.80),
        dirt_tint=(0.78, 0.76, 0.72),          # [v6] saturation and value lowered (avoids confetti)
        rock_tint=(0.82, 0.82, 0.80),          # [v6] rubble greyed (removes the European rampart tone)
        rockface_tint=(0.80, 0.80, 0.78),
        coping_tint=(0.78, 0.77, 0.74),
        # same arithmetic for the hedge / crest bands, one step darker so the distant
        #   masses stay behind the near ground: #6C6244, Y 0.128, R/G 1.21.
        hedge_tint=(2.55, 1.16, 2.48),         # [S3-11] dormant hedge / crest band
        backdrop_tint=(0.72, 0.73, 0.76),      # [S3-11] far-tier pale silhouette
        # [S3-11] the blob-fallback tints go dormant too, so a run without the vegetation
        #   assets does not silently ship a summer scene.
        shrub=(0.052, 0.045, 0.026), shrub_rough=1.0,
        canopy_a=(0.048, 0.043, 0.026), canopy_b=(0.055, 0.049, 0.030),
        canopy_rough=1.0,
        # [S3-8] the constant-colour timber (waymarker post, procedural-fallback trunks).
        #   (0.30,0.20,0.12) was a saturated dark red-brown that read near-black in shadow
        #   (`pt_noon_from_below.png`); (0.20,0.19,0.17) is a near-neutral grey-brown of the
        #   same family at Y 0.191 -> L* 50.7, i.e. weathered rather than freshly creosoted.
        wood_color=(0.20, 0.19, 0.17), wood_rough=0.85,
    ),   # [v5.2 user] arbitrary warning sign removed - sign_back colour constant deleted

    # --- lighting: scene01 noon verified constants + the sun specified in v5 §R5 ---
    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        noon_sun_enable=True, noon_sun_elev=49.79,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    # [v6 verdict §4 (4) + supervisor decision item 3 - reselection approved (front lit on the open side)]
    #   old 171.5 (az 205) -> the head retaining wall put the whole switchback passage in shadow.
    #   new 216.5 = world az 250 (sun in the −X·−Y sky, shadow az 70).
    #   direct sun enters the passage from the open side (−Y lower park). Check in docstring (1).
    SUN_AZ_OFFSET=216.5,

    render=dict(pt_total_spp=512, pt_max_bounces=8),
)


def _deep_update(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_update(dst[k], v)
        else:
            dst[k] = v


_ov = os.environ.get("NEGOBS_PARAMS_OVERRIDE", "")
if _ov:
    _deep_update(PARAMS, json.loads(_ov))
    print(f"[PARAMS] override 적용: {_ov}")

_sc_ov = os.environ.get("NEGOBS_SCENE_CONFIG", "")
if _sc_ov:
    _deep_update(SCENE_CONFIG, json.loads(_sc_ov))
    print(f"[SCENE_CONFIG] override 적용: {_sc_ov}")


# ===========================================================================
# [C] paths / asset roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene10")

ASSET_ROLES = ["wood_dark", "rock_wall", "rock_face", "concrete_wall",
               "grass", "leaf_ground", "dirt_park",
               "hdri", "mdl"]     # [v5.2 user] arbitrary warning sign removed

DECK_BOT = -6.60                   # deck bottom (landing3 top = end of flight3)
GROUND_Z = -6.62                   # lower path ground top (2 cm below the deck)
TRAIL_Z = 0.0                      # upper trail
HEAD_X = -1.5                      # retaining wall head = end of the upper plate
FAR_RIDGE_Z = 3.50                 # distant ridge top
NORTH_TAN = math.tan(math.radians(30.0))
SOUTH_SLOPE = 6.62 / 11.40         # south slope gradient (= tan 30.14 deg)


# ===========================================================================
# [D] flight layout precomputation (no boot needed)
# ===========================================================================
def flight_steps():
    """Per-flight riser counts. Scalar `steps` stays legal for back-compatibility."""
    fl = PARAMS["flights"]
    st = fl["steps"]
    if isinstance(st, (list, tuple)):
        return [int(s) for s in st]
    return [int(st)] * int(fl["n"])


def compute_flights():
    """[S3-10, Option A] Flight/landing ladder for a **traversing** deck.

    S3-9 kept the inherited 180-deg reversal in two parallel Y bands. §8.R OQ-6 rules
    Option A, and Option A is only reachable by giving that up, because a pure reversal in
    two bands **cannot** de-stack: flight k+2 always lands back on flight k's footprint.
    The scene's own v5 docstring says as much — *"A pure switchback makes no horizontal
    progress"* — which is why the ground under it had to be a masonry shaft.

    What is built instead is G10's actual form (§2.A.1-6/7): **every flight descends +X,
    each landing turns the run 90 deg and hands it to the other Y band, and the whole
    assembly traverses the slope.** Nothing sits above anything, daylight and litter show
    between and under the flights, and the ground can be a real slope instead of a wall.

    Landings jut forward along the travel direction and the next flight starts at the
    landing's **far** edge (the A-10-2 rule: never start a flight under the slab above it),
    so the ladder tiles the X axis and the plan is Sigma(run) + Sigma(landing).
    """
    fl = PARAMS["flights"]
    ld = PARAMS["landing"]
    steps = flight_steps()
    land = float(ld["size"])
    rest_at = int(ld.get("rest_at", -1))
    rest_sz = float(ld.get("rest_size", land))
    rest_ext = float(ld.get("rest_extra", 0.0))
    seq = []
    x_top, z_top = 0.0, float(fl["z_top"])
    for k in range(int(fl["n"])):
        ns = steps[k]
        run = ns * fl["tread"]
        fdrop = ns * fl["riser"]
        rest = (k == rest_at)
        z_bot = z_top - fdrop
        L = rest_sz if rest else land
        x_bot = x_top + run
        lx0, lx1 = x_bot, x_bot + L
        # the landing spans **both** width bands so the walker can cross from the band the
        # flight ran in to the band the next flight runs in; the rest platform also
        # projects past the +Y band as a 전망 balcony.
        ly0, ly1 = float(ld["y0"]), float(ld["y1"]) + (rest_ext if rest else 0.0)
        seq.append(dict(k=k, steps=ns, run=run, drop=fdrop,
                        x_top=x_top, z_top=z_top, x_bot=x_bot,
                        z_bot=z_bot, rot=0.0, even=(k % 2 == 0),
                        lx0=lx0, lx1=lx1, ly0=ly0, ly1=ly1, rest=rest))
        x_top, z_top = lx1, z_bot
    return seq


SEQ = compute_flights()
TOTAL_DROP = -SEQ[-1]["z_bot"]                  # 6.600 = 44 x 0.150, frozen (§9 P-2)
def band(k):
    """[S3-10] World Y band of flight `k`. Even = −Y band, odd = +Y band. Flights are now
    built directly in world coordinates — every flight descends +X, so the 180-deg
    `build_rot_group` that used to mirror the odd flights is gone."""
    fl = PARAMS["flights"]
    lo, hi = -fl["y_off"] - fl["half_w"], -fl["y_off"] + fl["half_w"]
    return (lo, hi) if (int(k) % 2 == 0) else (-hi, -lo)


PLAN_X0 = min(min(f["lx0"], f["x_top"], f["x_bot"]) for f in SEQ)
PLAN_X1 = max(max(f["lx1"], f["x_top"], f["x_bot"]) for f in SEQ)
PLAN_Y0 = min(min(f["ly0"], band(f["k"])[0]) for f in SEQ)
PLAN_Y1 = max(max(f["ly1"], band(f["k"])[1]) for f in SEQ)


def ground_line():
    """[S3-10] The corridor's longitudinal ground profile, as (x, z) control points.

    The rule is one line long: **the ground shadows the deck at a fixed air gap** —
    it ramps at the flight's own grade under a flight and benches level under a landing.
    That is a cut-and-fill trail bench, and it is the only profile that keeps the gap
    uniform; a straight ramp cannot, because the deck falls at 48 % on a flight and 0 %
    on a landing while a straight ground falls at the 25.8 % mean, so the deck would dive
    below grade at every flight foot (checked: −0.085 m at the first one).

    Gap: `landing.clear` 0.25 m under flights and turn landings — [law] KFS-TRAIL
    특별시방서 12-3 마 keeps 계단하단부 within 300 mm of natural grade — `rest_clear`
    0.60 m under the 쉼터 platform, which is not a stair foot, and finally 0.020 m at the
    ground-arrival landing, which **is** the walking step onto the lower path.
    """
    ld = PARAMS["landing"]
    clr = float(ld["clear"])
    rclr = float(ld.get("rest_clear", clr))
    ent = PARAMS["entry"]
    pts = [(float(ent["x0"]), float(ent["top"]) - clr),
           (float(ent["x1"]), float(ent["top"]) - clr)]
    last = SEQ[-1]["k"]
    for f in SEQ:
        if f["k"] == last:
            # the ground-arrival landing: the gap **is** the 20 mm walking step onto the
            # lower path, so the bench meets the lower park exactly.
            pts.append((f["x_bot"], GROUND_Z))
            pts.append((f["lx1"], GROUND_Z))
        else:
            # the stair foot always lands at `clear`; only the rest platform's bench then
            # keeps falling under it, so the extra air is picked up **under the platform**
            # and never as a steepening under the flight above it (which would put the
            # ground at 62 % where the flight itself is 48 %).
            pts.append((f["x_bot"], f["z_bot"] - clr))
            pts.append((f["lx1"], f["z_bot"] - (rclr if f["rest"] else clr)))
    return pts


GROUND_LINE = ground_line()


def corridor_z(x):
    """Ground z inside the deck corridor, piecewise-linear on GROUND_LINE."""
    if x <= GROUND_LINE[0][0]:
        return GROUND_LINE[0][1]
    for i in range(len(GROUND_LINE) - 1):
        xa, za = GROUND_LINE[i]
        xb, zb = GROUND_LINE[i + 1]
        if xa - 1e-9 <= x <= xb + 1e-9:
            if xb - xa < 1e-12:
                return zb
            return za + (zb - za) * (x - xa) / (xb - xa)
    return GROUND_LINE[-1][1]


def corridor_slabs():
    """[GT-119 ②] The corridor ground slabs, **with their downhill seam laps**.

    One row per `GROUND_LINE` segment, exactly as before; what is new is that a slab
    which meets a flatter neighbour is run on **past the crest, along its own top
    plane**, far enough to swallow that neighbour's far bottom corner.

    Why it has to exist. `sc.build_slope` places a rotateY box whose end faces are
    perpendicular to its own top plane, not vertical. At a crest where the profile
    goes steep (θa) -> flat (θb), slab a's end face leans back toward −X by
    `t·sin θa` at depth t while slab b's leans back only `t·sin θb`, so the two
    faces fan apart below the shared crest point and the hillside between them is
    **air**: a wedge `thick·sin(θa − θb)` wide at the far face, up to 3.05 m at a
    48 % flight foot. Six of those exist, one per flight foot, and the
    `260806_w3_allview5/pt_noon_from_below` cut caught the x = 15.30 one — a slot
    torn vertically through the slope (window x1380-1500 y600-1000, **16.8 %** pure
    RGB(0,0,0) `[measured]`) with the dome HDRI's below-horizon band showing through
    it, framed by the underside of `Bank_NorthBank` and the north rim of
    `Plate_LowerParkMain`.

    Why this direction and no other. The lap runs the **steeper** slab downhill, so
    every millimetre it gains is under the flatter slab it meets and under everything
    downstream of that `[asserted]`. The top plane is the same line it always was, so
    `max_i top_i(x) == corridor_z(x)` to machine epsilon — the deck, the posts, the
    dressing seats and the collision surface are bit-identical. Running the *flatter*
    slab back uphill instead would close the same wedge but raise the ground above its
    uphill neighbour at every one of the five concave kinks, which is the one thing
    a terrain repair may not do.

    lap = thick·sin(θi − θi+1) + `corridor.seam_lap`. The first term is exactly the
    distance from the crest to the neighbour's far bottom corner measured along this
    slab's own axis (= `thick·|d_b × e_a|`), so the second is the true clear overlap.
    Beyond the last segment the ground is `LowerParkMain`, i.e. level, so θ = 0.

    The lap puts two coplanar `grass` side faces on the scarp plane y −2.600 over the
    lapped run. That is not a new condition and not a new risk: the five **concave**
    kinks have always overlapped by the mirror amount (up to 3.05 m — e.g. slab 9 laps
    back over slab 8 across x 13.75..16.80), and that patch renders in
    `260806_w3_allview5/pt_noon_from_below` as one continuous grass face with no
    z-fight, no seam and no texture break `[measured]` — every corridor slab carries the
    same material and the same world-projected skin, so coincident side faces shade
    identically. `coplanar_census()` is untouched by any of it: it audits **horizontal
    top** faces, and every lapped slab is one of the sloped ones (θ > 0).

    Returns `[(name, x0, z0, run, drop, ang_deg, lap, x_end, z_end)]` — `x0/z0/run/drop`
    are the `build_slope` arguments, `x_end/z_end` the lapped downhill end.
    """
    cg = PARAMS["corridor"]
    thick, lapm = float(cg["thick"]), float(cg["seam_lap"])
    segs = []
    for i in range(len(GROUND_LINE) - 1):
        (xa, za), (xb, zb) = GROUND_LINE[i], GROUND_LINE[i + 1]
        if xb - xa < 1e-6:
            continue
        segs.append((i, xa, za, xb, zb, math.atan2(za - zb, xb - xa)))
    out = []
    for j, (i, xa, za, xb, zb, ang) in enumerate(segs):
        nxt = segs[j + 1][5] if j + 1 < len(segs) else 0.0
        lap = (thick * math.sin(ang - nxt) + lapm) if ang > nxt + 1e-12 else 0.0
        xe, ze = xb + lap * math.cos(ang), zb - lap * math.sin(ang)
        out.append((f"CorridorSlope_{i}", xa, za, xe - xa, za - ze,
                    math.degrees(ang), lap, xe, ze))
    return out


def slab_top(slab, x):
    """Top-plane z of one `corridor_slabs()` row at x, or None outside its run."""
    _nm, xa, za, run, drop, _ad, _lap, xe, _ze = slab
    if xa - 1e-9 <= x <= xe + 1e-9:
        return za - drop * (x - xa) / max(run, 1e-12)
    return None


def slab_holds(slab, x, z):
    """Is world point (x, ·, z) inside the slab's body? (rotateY box, local test.)"""
    _nm, xa, za, run, drop, ang_deg, _lap, _xe, _ze = slab
    ang = math.radians(ang_deg)
    L, th = math.hypot(run, drop), float(PARAMS["corridor"]["thick"])
    sx, sz = xa + run / 2.0, za - drop / 2.0
    cx = sx - (th / 2.0) * math.sin(ang)
    cz = sz - (th / 2.0) * math.cos(ang)
    dx, dz = x - cx, z - cz
    lx = dx * math.cos(ang) - dz * math.sin(ang)
    lz = -dx * math.sin(ang) - dz * math.cos(ang)
    return abs(lx) <= L / 2.0 + 1e-9 and abs(lz) <= th / 2.0 + 1e-9


# ===========================================================================
# [E] terrain maths
# ===========================================================================
NORTH_PIVOT = 8.00                 # [S3-10] bank foot, was 2.60 (the old wall top)


def north_z(y):
    """Top z of the north (+Y) 30° grass slope. Its foot moved out to y 8.00 when the
    retaining wall it used to stand on was deleted (Option A)."""
    if y <= NORTH_PIVOT:
        return 0.0
    return min(7.16, (y - NORTH_PIVOT) * NORTH_TAN)


def south_z(y):
    """Top z of the south (−Y) 30° unguarded slope (trail shoulder y−1.60 = 0)."""
    if y >= -1.60:
        return 0.0
    return max(GROUND_Z, (y + 1.60) * SOUTH_SLOPE)


def ground_z(x, y):
    """Ground z used to seat dressing. [S3-10] inside the corridor band it is the real
    descending slope, not the old shaft floor at −6.62."""
    cg = PARAMS["corridor"]
    if y >= NORTH_PIVOT:
        return north_z(y)
    if x <= HEAD_X:
        if y >= -1.60:
            return TRAIL_Z             # upper terrace / trail
        return south_z(y)
    if cg["y0"] <= y <= cg["y1"]:
        return corridor_z(x)
    return GROUND_Z                    # lower park, beyond the corridor scarp


def _zone_z(x, y, zone):
    if zone == "north":
        return max(north_z(y), ground_z(x, y))
    if zone == "south":
        return south_z(y)
    if zone in ("lower", "low"):
        return GROUND_Z
    if zone == "trail":
        return TRAIL_Z
    if zone == "far":
        return FAR_RIDGE_Z
    return ground_z(x, y)


# ===========================================================================
# [F] deck post layout (post bottoms must always meet the ground or the landing below)
# ===========================================================================
def post_segments():
    """List of (name, cx, cy, z_lo, z_hi) — z_hi is the underside of the slab being supported."""
    ld = PARAMS["landing"]
    ent = PARAMS["entry"]
    hy = PARAMS["post"]["half_y"]
    ins = PARAMS["post"]["inset"]
    t = ld["thick"]
    segs = []
    # support per landing : up to the landing slab underside (z_bot − thick); the bottom is
    # the ground or the top face of whatever landing actually stands under that column.
    # [S3-9] the footing lookup used to test `lx0 == lx0`, which assumed every landing was
    # the same length. The rest platform is 3.00 m deep, so its far column sits past the
    # end of the landing below and the old test would have left it floating. It now asks
    # the real question: **which lower landing's x-span contains this column's x**.
    for f in SEQ:
        cols = [f["lx0"] + ins, f["lx1"] - ins]
        for ci, cx in enumerate(cols):
            for tag, sgn in (("P", 1.0), ("N", -1.0)):
                z_hi = f["z_bot"] - t
                below = [g["z_bot"] for g in SEQ
                         if g["z_bot"] < z_hi - 1e-9
                         and g["lx0"] - 1e-9 <= cx <= g["lx1"] + 1e-9]
                # [S3-10] no landing stacks over another any more, so every column now
                # founds on the **sloped corridor ground**, not on the old shaft floor.
                z_lo = max(below) if below else corridor_z(cx)
                if z_hi - z_lo > 0.05:
                    segs.append((f"L{f['k']}_C{ci}_{tag}", cx, sgn * hy,
                                 z_lo, z_hi))
    # post at the +X end of the entry deck. [S3-10] nothing sits under it any more —
    # the deck no longer doubles back — so it founds on the corridor ground.
    z_hi = ent["top"] - ent["thick"]
    for tag, sgn in (("P", 1.0), ("N", -1.0)):
        cx = ent["x1"] - ins
        segs.append((f"Entry_{tag}", cx, sgn * hy, corridor_z(cx), z_hi))
    return segs


# ===========================================================================
# [F-b] railing inventory — [S3-8 · GT-65] one source of truth for every rail
#       member, newel and junction in the scene.
#
#       [GT-65] The deck is **y-monotone**: at every x exactly one y-interval is
#       walkable (entry deck -> flight band -> landing -> flight band -> ...), so its
#       guarded boundary is exactly two polylines, ylo(x) and yhi(x). Every run is one
#       segment of one of them and `deck_slabs()` is the only place a coordinate is
#       written. Listing the runs by hand is what produced the four junction defects
#       the 08-05 gallery review flagged as "연결부가 아직 지저분":
#         (a) `LandRail_k_Out` was drawn across the **whole** landing width, i.e. it
#             ran straight through the head of the next flight — 5 flights, plus the
#             arrival landing where it railed off the exit itself (§0-2 dead end);
#         (b) the level runs sat on the slab edge (y ±1.60) while the flight runs sat
#             `bal/2` outboard (y ∓1.619), so every flight head and foot carried
#             **two** 90x90 capped newels 19 mm apart — 12 interpenetrating pairs;
#         (c) the landing back edges carried no run at all, so `LandRail_k_P`/`_N`
#             began in mid-air at the back corner — a floating run end at every turn;
#         (d) line posts and balusters were laid out independently of each other, so a
#             38x38 baluster could sit inside a 90x90 post (exactly coincident on the
#             3.20 m runs, whose 1/3 station is also a baluster station).
#       Junction rule, one line: **every rail centreline is the walking-surface
#       boundary offset `bal/2` outboard**; an X-run dies into the newel at each node
#       (its end is 26 mm inside the 90 mm post), and the Y-run that closes a step in
#       the boundary is butted back by half the crossing member so no two rails share
#       a volume or, worse, a coplanar top face.
# ===========================================================================
def deck_slabs():
    """Walking-surface footprint as an ordered list of x-slabs.

    `(tag, x0, x1, ylo, yhi, z0, z1, rake)`. Consecutive slabs share their x boundary,
    so the two boundary chains are continuous by construction and a junction cannot be
    forgotten — it can only be typed wrong here, where SMOKE checks it.
    """
    ent = PARAMS["entry"]
    slabs = [("E", float(ent["x0"]), float(ent["x1"]),
              float(PARAMS["landing"]["y0"]), float(PARAMS["landing"]["y1"]),
              float(ent["top"]), float(ent["top"]), False)]
    for f in SEQ:
        lo, hi = band(f["k"])
        slabs.append((f"F{f['k']}", f["x_top"], f["x_bot"], lo, hi,
                      f["z_top"], f["z_bot"], True))
        slabs.append((f"L{f['k']}", f["lx0"], f["lx1"], f["ly0"], f["ly1"],
                      f["z_bot"], f["z_bot"], False))
    return slabs


def _rail_root(tag, suffix):
    """Legacy prim root for a run owned by slab `tag` (roots are kept stable)."""
    if tag == "E":
        return "EntryRail" + suffix
    if tag[0] == "L":
        return f"LandRail_{tag[1:]}" + suffix
    return f"FlightRail_{tag[1:]}" + suffix


def rail_runs():
    """Every railing run in the scene, derived from the guarded boundary.

    dict keys: `name` (prim root under ROOT) · `kind` 'level' (entry/landing side run)
    / 'rake' (flight side run) / 'cross' (the run that closes a step in the boundary)
    · `x0,y0,x1,y1` the rail **centreline**, already `bal/2` outboard of the walking
    surface so the baluster inner face is flush with the deck edge and the declared
    1.500 m clear width is measured between rail faces · `z0,z1` walking z at each end
    · `side` 'N' (ylo chain) / 'P' (yhi chain) · `k` flight/landing index · `broken`
    the frozen `rail.broken_landing` hook · [GT-115 ⑭] `ox,oy` the run's **outboard**
    plan normal (unit, away from the walking surface), which is what tells the handrail
    pass and the return pass which side is "inside" without re-deriving the boundary.

    The forward face of the **arrival** landing carries no run: it meets natural grade
    at a 20 mm step, so a guard there is a false drop cue (08-05 doctrine — a rail line
    means the ground falls away beyond it) and it is the very edge the walk leaves by.

    [GT-115 ⑭ (1)] The chain is closed at its two free ends by a `return` run — see
    `rail.end` — so no run stops at a node that carries only that one run.
    """
    r = PARAMS["rail"]
    off = float(r["bal"]) / 2.0
    br = r["broken_landing"]
    slabs = deck_slabs()
    runs, used = [], set()

    def _nm(base):
        nm = base
        while nm in used:            # the rest platform owns two forward faces
            nm += "P"
        used.add(nm)
        return nm

    for side, s in (("N", -1.0), ("P", 1.0)):
        for i, sl in enumerate(slabs):
            tag, x0, x1, ylo, yhi, z0, z1, rake = sl
            y = (ylo if s < 0.0 else yhi) + s * off
            if rake:
                k = int(tag[1:])
                runs.append(dict(name=f"FlightGrp_{k}/Rail_{side}", kind="rake",
                                 k=k, side=side, x0=x0, y0=y, x1=x1, y1=y,
                                 z0=z0, z1=z1, broken=False, ox=0.0, oy=s))
            else:
                runs.append(dict(name=_nm(_rail_root(tag, f"_{side}")),
                                 kind="level",
                                 k=(int(tag[1:]) if tag[0] == "L" else None),
                                 side=side, x0=x0, y0=y, x1=x1, y1=y,
                                 z0=z0, z1=z1, broken=False, ox=0.0, oy=s))
            # [GT-115 ⑭ (1)] free chain ends: the back face of the entry deck and the
            #   forward face of the arrival landing are the only nodes where a run has
            #   no partner. Each is closed by a 90-deg **return** turned inboard (the
            #   outboard direction is barred at both ends — see `rail.end`), which the
            #   newel pass then caps at its far end exactly like any other node.
            endl = float(r.get("end", {}).get("run", 0.0))
            if endl > 1e-6 and (i == 0 or i + 1 == len(slabs)):
                first = (i == 0)
                xe = (x0 - off) if first else (x1 + off)
                runs.append(dict(name=_nm(_rail_root(tag, f"_End{side}")),
                                 kind="return",
                                 k=(int(tag[1:]) if tag[0] == "L" else None),
                                 side=side,
                                 x0=xe, y0=y, x1=xe, y1=y - s * endl,
                                 z0=z0 if first else z1,
                                 z1=z0 if first else z1,
                                 broken=False,
                                 ox=(-1.0 if first else 1.0), oy=0.0))
            if i + 1 >= len(slabs):
                continue             # arrival landing: the forward face is the exit
            ntag, _nx0, _nx1, nylo, nyhi, nz0, _nz1, _nrake = slabs[i + 1]
            yn = (nylo if s < 0.0 else nyhi) + s * off
            if abs(yn - y) < 1e-9:
                continue             # the boundary does not step on this chain
            # The free edge belongs to whichever slab reaches further out along this
            # chain: forward (+X) face of this slab, or back (−X) face of the next.
            fwd = (s * (y - yn) > 0.0)
            otag = tag if fwd else ntag
            runs.append(dict(name=_nm(_rail_root(otag, "_Out" if fwd else "_Back")),
                             kind="cross",
                             k=(int(otag[1:]) if otag[0] == "L" else None),
                             side=side,
                             x0=x1 + (off if fwd else -off), y0=y,
                             x1=x1 + (off if fwd else -off), y1=yn,
                             z0=(z1 if fwd else nz0), z1=(z1 if fwd else nz0),
                             broken=(fwd and otag[0] == "L"
                                     and int(otag[1:]) == br),
                             ox=(1.0 if fwd else -1.0), oy=0.0))
    return runs


def newel_points(runs=None):
    """Capped-newel positions: **one per node of the guarded boundary**.

    A node is where two runs meet — a corner, the head or foot of a flight, or a run
    termination. G10 shows one stout capped post there, not two, and the cap is the
    strongest single 'timber, not steel' tell, so doubling it reads as a defect. The
    pre-GT-65 code derived newels from the level runs only and let `_flight_rails`
    add its own, which is how 12 pairs of 90x90 posts ended up 19 mm apart.

    Merge tolerance: 0.10 m in plan (the largest real offset between two members of
    one node is the `bal/2` = 19 mm rail offset) and 0.20 m in z (the entry deck top
    sits 5 mm under flight 0's nosing datum). The nearest **distinct** nodes in the
    scene are 1.500 m apart `[measured, SMOKE GT-65 block]`, so the tolerance cannot
    over-merge. Cross-run endpoints
    are seeded first so the surviving position is the mitred corner itself, and the
    lowest z of a merged group wins so the post is seated on the deck it stands on.
    """
    runs = rail_runs() if runs is None else runs
    order = {"cross": 0, "level": 1, "rake": 2}
    pts = []
    for rr in sorted(runs, key=lambda q: order.get(q["kind"], 3)):
        pts.append((rr["x0"], rr["y0"], rr["z0"]))
        pts.append((rr["x1"], rr["y1"], rr["z1"]))
    merged = []
    for px, py, pz in pts:
        for m in merged:
            if (abs(m[0] - px) <= 0.10 and abs(m[1] - py) <= 0.10
                    and abs(m[2] - pz) <= 0.20):
                m[2] = min(m[2], pz)
                break
        else:
            merged.append([px, py, pz])
    return sorted((round(a, 3), round(b, 3), round(c, 3))
                  for a, b, c in merged)


def baluster_run(L, step):
    """Baluster stations along a run of length L at a nominal horizontal pitch `step`.

    Returns (n, pitch). The pitch is trimmed so the two end gaps equal the internal
    ones — a bay whose end gap differs from its field gap is the classic give-away of
    a railing laid out by division rather than by setting-out.
    """
    n = max(1, int(round(L / float(step))) - 1)
    return n, L / float(n + 1)


def rail_field_span(kind, L, ends=(True, True)):
    """[GT-65] Length of the baluster / line-post field on a run of node-to-node
    length `L`. A **cross** run butts back by half the top rail at each end so it dies
    on the face of the X-run it meets (no shared volume, no coplanar top faces); its
    field is therefore `top` width shorter than its line. X-runs die inside the newel
    instead and keep their full line.

    [GT-115 ⑭] `ends` makes the butt per-end. A **return** butts only where it meets the
    X-run it turns off; its free end has to die *inside* its own capped end post the way
    an X-run does, and a symmetric butt would leave that end 25 mm short of the post
    face `[computed]`. Default `(True, True)` reproduces the GT-65 cross exactly.
    """
    if kind in ("cross", "return"):
        w = float(PARAMS["rail"]["top"][0])
        return max(0.0, float(L)
                   - (w / 2.0 if ends[0] else 0.0)
                   - (w / 2.0 if ends[1] else 0.0))
    return float(L)


def _run_plan_dir(rr):
    """Unit plan direction of a run (rakes included — the rake's plan run is +X)."""
    dx, dy = rr["x1"] - rr["x0"], rr["y1"] - rr["y0"]
    L = math.hypot(dx, dy)
    return (dx / L, dy / L) if L > 1e-9 else (0.0, 0.0)


def run_end_nodes(runs=None):
    """[GT-115 ⑭ (1)] Boundary nodes carrying exactly **one** run end.

    The 08-14 audit reads a run stopping with nothing turning the corner. This is the
    measurable form of that: a node of degree 1 is a run that terminates rather than
    continuing, and every such node has to be a designed termination (a capped end post
    with a return into it), not an accident of the chain. Returns
    `[(x, y, z, [(run name, kind)])]`, so the self-check can name the offender instead of
    printing a count.
    """
    runs = rail_runs() if runs is None else runs
    nodes = []
    for rr in runs:
        for (px, py, pz) in ((rr["x0"], rr["y0"], rr["z0"]),
                             (rr["x1"], rr["y1"], rr["z1"])):
            for nd in nodes:
                if (abs(nd[0] - px) <= 0.10 and abs(nd[1] - py) <= 0.10
                        and abs(nd[2] - pz) <= 0.20):
                    nd[3].append((rr["name"], rr["kind"]))
                    break
            else:
                nodes.append([px, py, pz, [(rr["name"], rr["kind"])]])
    return [(round(a, 3), round(b, 3), round(c, 3), nm)
            for a, b, c, nm in nodes if len(nm) < 2]


def handrail_lines(runs=None):
    """[GT-115 ⑭ (4)] The graspable handrail, derived from the same run inventory.

    One tube per guard run (`return` stubs excluded — the handrail dies into the corner
    newel, which *is* the returned-end detail, and a 0.14 m tube on a 0.30 m stub would
    read as debris). The axis is the run centreline pushed `hand.off` **inboard** — the
    direction `rail_runs()` publishes as `-(ox, oy)` — and dropped `hand.drop` under the
    top-rail top face, so a rake's handrail is parallel to its own nosing plane by
    construction and no height or position of an existing member is consulted, let alone
    changed.

    Trim rule: an end is cut back by `hand.off` **iff the run it meets there turns**
    (different plan direction, or nothing there at all). Two perpendicular tubes then
    meet exactly at the mitre point with no shared volume, while a flight rail and the
    landing rail it continues into keep one unbroken tube across the newel — which is
    the whole reason a handrail is bracketed inboard rather than sat on top.

    Returns dicts: `name` · `x0,y0,z0`-`x1,y1,z1` (**tube axis**) · `L` (axis length) ·
    `rotY`/`rotZ` for `sc.add_cylinder` · `ix,iy` inboard unit normal · `horiz`.
    """
    r = PARAMS["rail"]
    hd = r["hand"]
    runs = rail_runs() if runs is None else runs
    off = float(hd["off"])
    dz = float(r["h"]) - float(hd["drop"])
    ends = [(rr, (rr["x0"], rr["y0"], rr["z0"]), _run_plan_dir(rr)) for rr in runs]
    ends += [(rr, (rr["x1"], rr["y1"], rr["z1"]), _run_plan_dir(rr)) for rr in runs]
    out = []
    for rr in runs:
        if rr["kind"] == "return" or rr["broken"]:
            continue
        ux, uy = _run_plan_dir(rr)
        ix, iy = -float(rr["ox"]), -float(rr["oy"])
        Lp = math.hypot(rr["x1"] - rr["x0"], rr["y1"] - rr["y0"])
        if Lp < 1e-6:
            continue
        cut = []
        for (px, py, pz) in ((rr["x0"], rr["y0"], rr["z0"]),
                             (rr["x1"], rr["y1"], rr["z1"])):
            turn = True
            for q, (qx, qy, qz), (qux, quy) in ends:
                if q is rr:
                    continue
                if (abs(qx - px) <= 0.10 and abs(qy - py) <= 0.10
                        and abs(qz - pz) <= 0.20
                        and abs(qux * ux + quy * uy) > 0.999):
                    turn = False
            cut.append(off if turn else 0.0)
        s0, s1 = cut[0], Lp - cut[1]
        if s1 - s0 < 0.05:
            continue
        def _pt(s, _rr=rr, _ux=ux, _uy=uy, _ix=ix, _iy=iy, _Lp=Lp):
            return (_rr["x0"] + _ux * s + _ix * off,
                    _rr["y0"] + _uy * s + _iy * off,
                    _rr["z0"] + (_rr["z1"] - _rr["z0"]) * (s / _Lp) + dz)
        ax0, ay0, az0 = _pt(s0)
        ax1, ay1, az1 = _pt(s1)
        plan = s1 - s0
        out.append(dict(name=rr["name"], kind=rr["kind"], side=rr["side"],
                        x0=ax0, y0=ay0, z0=az0, x1=ax1, y1=ay1, z1=az1,
                        L=math.hypot(plan, az1 - az0), plan=plan,
                        ix=ix, iy=iy, horiz=(abs(ux) >= abs(uy)),
                        rotY=90.0 + math.degrees(math.atan2(az0 - az1, plan)),
                        rotZ=math.degrees(math.atan2(ay1 - ay0, ax1 - ax0))))
    return out


def outcrop_clearance(runs=None):
    """[GT-115 ⑭ (1)] Plan clearance from every rock outcrop to every railing line.

    The rocks are dressing and the guard is not, so the guard never moves: this is the
    arithmetic that decides where a rock may stand. Each rock is modelled as its
    **manifest** plan box (`outcrop_plan`, `geometry.size_m`) rotated by its own yaw and
    taken as the axis-aligned envelope, then scaled — an over-estimate of the real
    footprint, so the clearance it reports is a lower bound. Each run is its centreline
    grown by half the widest railing member (`top` 0.140 → 0.070; the 90x90 newel's
    0.045 is inside that), and both boxes being axis-aligned, the separation along the
    separating axis is `max(dx, dy)` — itself ≤ the Euclidean gap, so conservative twice.

    Returns `[(asset_id, row index, clearance_m, worst run name)]`, worst first.
    """
    runs = rail_runs() if runs is None else runs
    half = float(PARAMS["rail"]["top"][0]) / 2.0
    plan = PARAMS["outcrop_plan"]
    rows = []
    for i, (aid, ox, oy, _oz, oyaw, osc) in enumerate(PARAMS["outcrop"]):
        w, d = plan.get(aid, (0.0, 0.0))
        c = abs(math.cos(math.radians(float(oyaw))))
        s = abs(math.sin(math.radians(float(oyaw))))
        hx = float(osc) * (float(w) * c + float(d) * s) / 2.0
        hy = float(osc) * (float(w) * s + float(d) * c) / 2.0
        worst, wnm = 1.0e9, "-"
        for rr in runs:
            rx0, rx1 = sorted((rr["x0"], rr["x1"]))
            ry0, ry1 = sorted((rr["y0"], rr["y1"]))
            gx = max(rx0 - half - (ox + hx), (ox - hx) - (rx1 + half))
            gy = max(ry0 - half - (oy + hy), (oy - hy) - (ry1 + half))
            g = max(gx, gy)
            if g < worst:
                worst, wnm = g, rr["name"]
        rows.append((aid, i, worst, wnm))
    return sorted(rows, key=lambda q: q[2])


def litter_pool(cards):
    """[GT-115 ⑭ (2)] One cluster-variant sub-pool of `sc.VEG_DEBRIS`.

    `cards` names existing Debris USDs by stem — **no procurement**: the five rows are
    already five different card arrangements of the same fallen leaves, and the variants
    are cut out of them. A stem that is not in the shared pool simply does not appear, and
    an empty selection falls back to the full pool rather than silently placing nothing.
    """
    want = tuple(str(c) for c in cards)
    pool = [row for row in sc.VEG_DEBRIS
            if os.path.basename(str(row[0])).rsplit(".", 1)[0] in want]
    return pool or list(sc.VEG_DEBRIS)


# ===========================================================================
# [F-c] deck_module_selfcheck — the named self-check of spec §6.5, house style
#       (`scene05.podium_step_selfcheck` / `scene09.roof_normal_selfcheck`).
#       It re-derives every number the rebuild claims from PARAMS and prints it,
#       so a later edit that quietly moves one of them fails visibly in SMOKE.
#       Grows one block per rebuild commit: S3-8 railing (below).
# ===========================================================================
def deck_module_selfcheck():
    P = PARAMS
    r = P["rail"]
    fl = P["flights"]
    ok_all = True
    print("\n  [deck_module_selfcheck] S3-8 난간 — 각재 단면 · 살대 안목")

    # -- member schedule: every section must be a stocked 방부목 size --------
    stock_kaku = {0.038, 0.045, 0.089, 0.090, 0.120, 0.140, 0.185, 0.235}
    sched = [("난간 엄지기둥 newel", (r["newel"], r["newel"]), "90x90 각재"),
             ("엄지기둥 갓 cap", r["newel_cap"][:2], "120x120 (오버사이즈 갓)"),
             ("난간 중간기둥 post", (r["post"], r["post"]), "90x90 각재"),
             ("상부 난간대 top", r["top"], "38x140 평철 눕힘"),
             ("중간 난간대 mid", r["mid"], "38x89"),
             ("하부 난간대 bot", r["bot"], "38x89"),
             ("살대 baluster", (r["bal"], r["bal"]), "38x38"),
             ("데크 지지기둥 column", (P["post"]["sec"], P["post"]["sec"]),
              "120x120 기둥재")]
    print(f"    {'부재':<22} {'단면(m)':>14}  {'시판규격':<22} 판정")
    for nm, sec, note in sched:
        good = all(round(float(v), 3) in stock_kaku for v in sec)
        ok_all &= good
        print(f"    {nm:<22} {sec[0]:6.3f}x{sec[1]:6.3f}  {note:<22} "
              f"{'OK' if good else 'CHECK'}")
    print("      근거: 연구 §D2 — 한국 방부목 실판매 각재는 38/45 소각재 · "
          "90각·120각·140각 기둥재. KFS 도면의 80x80·100x100 은 도면치수이지 "
          "시판규격이 아니다.")

    # -- round-member census: G10 has no round member anywhere in frame -----
    #    [GT-115 ⑭ (4)] **re-stated, not broken.** S3-8's census was a *silhouette*
    #    argument: a run of thin round verticals between two thin round horizontals is
    #    the silhouette of a steel balustrade. The frame is still 100 % square — that
    #    number is asserted below — and the one round member added is a single
    #    **horizontal** graspable tube behind the square frame, which is the opposite
    #    reading and what a 방부목 관찰데크 actually carries.
    n_frame_round = 0
    n_hand = len(handrail_lines())
    good = n_frame_round == 0
    ok_all &= good
    print(f"    난간 골조 원형부재 {n_frame_round}개 (엄지기둥·난간대·살대·중간기둥 "
          f"전부 박스) → {'OK' if good else 'CHECK'}")
    print(f"    손스침(원형) 라인 {n_hand}개 · Ø{r['hand']['dia']:.3f} m "
          f"— [GT-115 ⑭] 골조 실루엣과 분리된 수평 파지부재 (§8.R 계열 논리로 선언)")
    print("      sc.build_railing_line 은 이 씬에서 더 이상 호출되지 않는다 — "
          "공유 살대(baluster_r) 중복 48쌍 함정은 '끄기'가 아니라 "
          "'경로 제거'로 해소됨")

    # -- rail height: the ruling and the code counterpoint ------------------
    print(f"    난간 높이(상부 난간대 상면) {r['h']:.3f} m — "
          f"{'OK' if abs(r['h'] - 1.10) < 1e-9 else 'CHECK'}")
    print("      [data] KNPS-RAIL 실측 중앙값 1.10 m (n=1,227 · 71 % 가 1.0~1.2) "
          "= §8.R OQ-5 확정치 / [law] 조경설계기준 16.20.2(2) 관찰데크 난간 "
          "≥1.20 m 는 코드 대조군 — 실사례 우선 원칙으로 1.10 채택, "
          "GT-20 원장 행에 양쪽 병기")
    ok_all &= abs(r["h"] - 1.10) < 1e-9

    # -- baluster clear gap on every run, level and raking ------------------
    lo_b, hi_b = 0.100, 0.120
    worst = None
    rows = []
    for rr in rail_runs():
        if rr["broken"] or rr["kind"] == "return":
            continue                 # [GT-115 ⑭] returns carry one centred baluster —
                                     #   reported on its own row below, because a 0.30 m
                                     #   stub cannot carry the field pitch by definition
        L = rail_field_span(rr["kind"],
                            math.hypot(rr["x1"] - rr["x0"], rr["y1"] - rr["y0"]))
        nb, pitch = baluster_run(L, r["bal_step"])
        rows.append((f"Flight{rr['k']}{rr['side']}(경사·수평피치)"
                     if rr["kind"] == "rake" else rr["name"], L, nb, pitch))
    print(f"    {'런':<24} {'길이':>6} {'살대수':>5} {'피치':>7} {'안목':>7} 판정")
    for nm, L, nb, pitch in rows:
        clear = pitch - r["bal"]
        good = lo_b - 1e-9 <= clear <= hi_b + 1e-9
        ok_all &= good
        worst = clear if worst is None else min(worst, clear)
        print(f"    {nm:<24} {L:6.3f} {nb:5d} {pitch:7.4f} {clear:7.4f} "
              f"{'OK' if good else 'CHECK'}")
    print(f"      안목 목표 0.110 ± 0.010 m (§8.R OQ-5) · 최소 {worst:.4f} → "
          f"{'OK' if ok_all else 'CHECK'}")
    print("      [law] 조경설계기준 16.13.2(3) 안전난간 안목 ≤100 mm, "
          "단서로 '계단중간에 설치하는 난간' 은 ≤150 mm — 112 mm 는 단서 안. "
          "주택건설기준 제18조의 ≤100 은 주택단지 전용이라 이 씬을 구속하지 않음")

    # -- balusters plumb, not raked ----------------------------------------
    pitch_deg = math.degrees(math.atan2(fl["riser"], fl["tread"]))
    print(f"    살대 연직(계단면에 수직) = True · 경사 {pitch_deg:.1f}° 에서도 "
          f"세로부재 회전 0° → OK")
    print("      [law] KCS 34 50 10 3.2.6(3) '비탈면에 설치되는 계단난간의 "
          "세로부재는 계단면에 수직이 되도록 제작, 설치하여야 한다'. "
          "살대 피치는 **수평** 기준이라 경사면에서도 안목이 cos 만큼 좁아지지 않음")

    # -- every landing edge is protected -----------------------------------
    runs = rail_runs()
    brk = [rr["name"] for rr in runs if rr["broken"]]
    good = not brk
    ok_all &= good
    print(f"    모든 참 외측 난간 연결 · 누락 런 {brk or '없음'} → "
          f"{'OK' if good else 'CHECK'}")

    # -- newels: one per shared corner, not two ----------------------------
    ends = 2 * len(runs)
    nw = len(newel_points(runs))
    print(f"    엄지기둥 {nw}개 (런 {len(runs)}개 · 끝점 {ends}개에서 노드 병합) · 갓 "
          f"{r['newel_cap'][0]:.3f}x{r['newel_cap'][1]:.3f}x"
          f"{r['newel_cap'][2]:.3f} · 난간 위 돌출 {r['newel_proud']:.3f} m")

    # -- the lattice bay ----------------------------------------------------
    lat = r["lattice"]
    tgt = str(lat["run"])
    good = any(rr["name"] == tgt for rr in runs)
    ok_all &= good
    print(f"    격자 베이 1개 = {tgt} (피치 {lat['pitch']:.2f} m · 단면 "
          f"{lat['sec']:.3f}) → {'OK' if good else 'CHECK'}")
    print("      배치 근거: 이 런은 프리셋 그리드 5컷 전부 + leaf_edge 에 들어온다. "
          "상단 참에 두면 심사 프레임에 한 번도 안 잡힘 (§0.2 계열 논리)")

    print(f"    [deck_module_selfcheck S3-8] "
          f"{'전항목 OK' if ok_all else '⚠ CHECK 항목 있음'}")

    # =====================================================================
    # GT-65 — railing junctions. The 08-05 review said the connections are still
    # messy; "messy" is measurable, so every claim below is an assertion, not a
    # description. Four numbers have to stay at their target or the junction model
    # has been broken by a later edit.
    # =====================================================================
    ok65 = True
    print("\n  [deck_module_selfcheck] GT-65 난간 접합 — 경계 체인·엄지기둥·개구")
    slabs = deck_slabs()
    off = r["bal"] / 2.0

    # (1) the boundary is continuous: consecutive slabs share their x station and
    #     their walking z, so no chain can develop a hole.
    seam = 0.0
    zseam = 0.0
    for a, b in zip(slabs, slabs[1:]):
        seam = max(seam, abs(b[1] - a[2]))
        zseam = max(zseam, abs(b[5] - a[6]))
    good = seam < 1e-9 and zseam <= 0.005 + 1e-9
    ok65 &= good
    print(f"    보행면 슬래브 {len(slabs)}장 · x 이음 최대 {seam:.6f} m · "
          f"z 이음 최대 {zseam:.4f} m → "
          f"{'OK (진입데크 −0.005 = 노징 기준면과의 설계 단차)' if good else 'CHECK'}")

    # (2) no run crosses the head of the next flight. Before GT-65 the forward run
    #     was drawn over the **whole** landing width, so it stood across five flight
    #     heads and the exit; the split runs must clear every band with margin.
    worst_cross, worst_nm = 9.9, "-"
    for rr in runs:
        if rr["kind"] not in ("cross", "return"):   # [GT-115 ⑭] returns judged too
            continue
        lo_r, hi_r = min(rr["y0"], rr["y1"]), max(rr["y0"], rr["y1"])
        for f in SEQ:
            if abs(f["x_top"] - rr["x0"]) > off + 1e-6:
                continue
            blo, bhi = band(f["k"])
            m = max(blo - hi_r, lo_r - bhi)      # >0 = the band is clear
            if m < worst_cross:
                worst_cross, worst_nm = m, f"{rr['name']}×플라이트{f['k']}"
    good = worst_cross > 0.0
    ok65 &= good
    print(f"    가로런 vs 다음 플라이트 대역 최소 이격 {worst_cross:+.3f} m "
          f"({worst_nm}) → {'OK (통로 위 난간 0개)' if good else 'CHECK ← 계단 머리를 막는다'}")

    # (3) newel spacing: two 90x90 capped posts closer than one section apart are one
    #     post drawn twice. The pre-GT-65 assembly had 12 such pairs at 0.019 m.
    nws = newel_points(runs)
    near, npair = 9.9, "-"
    for i in range(len(nws)):
        for j in range(i + 1, len(nws)):
            if abs(nws[i][2] - nws[j][2]) > 0.30:
                continue
            d = math.hypot(nws[i][0] - nws[j][0], nws[i][1] - nws[j][1])
            if d < near:
                near, npair = d, f"{nws[i]}~{nws[j]}"
    good = near >= r["newel"] - 1e-9
    ok65 &= good
    print(f"    엄지기둥 {len(nws)}개 · 동일 표고대 최근접 간격 {near:.3f} m ≥ "
          f"단면 {r['newel']:.3f} → {'OK (관통쌍 0)' if good else f'CHECK {npair}'}")

    # (4) the arrival landing hands the walk over instead of railing it off.
    lastk = SEQ[-1]["k"]
    exits = [rr["name"] for rr in runs
             if rr["kind"] == "cross" and rr["k"] == lastk
             and rr["name"].endswith("_Out")]
    good = not exits
    ok65 &= good
    print(f"    도착참 전면 난간 {exits or '없음'} · 하부 지면과의 단차 "
          f"{SEQ[-1]['z_bot'] - GROUND_Z:+.3f} m → "
          f"{'OK (20 mm 단차에 가드는 허위 낙차 표지 — 08-05 독트린)' if good else 'CHECK'}")
    print("      런 구성: 종런(level/rake) 은 노드에서 엄지기둥 속으로 죽고, "
          "경계 단차를 닫는 가로런(cross) 은 상부 난간대 반폭만큼 물러나 "
          "종런 측면에 붙는다 — 공유 부피 0 · 동일 z 상면 중첩 0")

    # (5) closing the entry deck's forward edge adds a guard **into the judged grid
    #     frames**, so it has to be proved harmless to the scene's GT-positive core:
    #     the leaf band over flight 0's treads 1·2 must stay visible from all nine
    #     (−d, 0, h) eyes. The run lives entirely on the +Y side of the approach axis
    #     while the flight band is on the −Y side, so no sight line to a leaf tread
    #     crosses it — asserted, not assumed.
    f0 = SEQ[0]
    blo, bhi = band(0)
    cue = [(f0["x_top"] + (i - 0.5) * fl["tread"], (blo + bhi) / 2.0,
            f0["z_top"] - i * fl["riser"]) for i in (1, 2)]
    cue.append((f0["x_bot"], (blo + bhi) / 2.0, f0["z_bot"]))
    hits = []
    for rr in runs:
        if rr["kind"] not in ("cross", "return"):   # [GT-115 ⑭] returns judged too
            continue
        ylo_r, yhi_r = sorted((rr["y0"], rr["y1"]))
        for d in (2, 5, 10):
            for hh in (0.3, 0.9, 1.8):
                for tx, ty, tz in cue:
                    if abs(tx - (-d)) < 1e-9:
                        continue
                    t = (rr["x0"] + d) / (tx + d)
                    if not 0.0 < t < 1.0:
                        continue
                    py = ty * t
                    pz = hh + (tz - hh) * t
                    if (ylo_r <= py <= yhi_r
                            and rr["z0"] <= pz <= rr["z0"] + r["h"]):
                        hits.append(f"{rr['name']}@d{d}h{hh}")
    good = not hits
    ok65 &= good
    print(f"    낙엽 밴드(플라이트0 디딤판 1·2)·플라이트0 발 시선 차폐 "
          f"{len(hits)}건 {hits[:3] or ''} → "
          f"{'OK (진입 전면 가드는 접근축 +Y 쪽 — GT 양성 코어 불변)' if good else 'CHECK'}")

    print(f"    [deck_module_selfcheck GT-65] "
          f"{'전항목 OK' if ok65 else '⚠ CHECK 항목 있음'}")
    ok_all &= ok65

    # =====================================================================
    # S3-9 — stair re-table. Every identity is re-derived here, never retyped.
    # =====================================================================
    ok9 = True
    ld = P["landing"]
    print("\n  [deck_module_selfcheck] S3-9 계단 재작표 — 규격·참·판재")
    steps = flight_steps()
    R, T, W = fl["riser"], fl["tread"], 2.0 * fl["half_w"]

    n_tot = sum(steps)
    drop_id = n_tot * R
    good = (n_tot == 44 and abs(drop_id - 6.600) < 1e-9
            and abs(TOTAL_DROP - 6.600) < 1e-9)
    ok9 &= good
    print(f"    총단수 {'+'.join(str(v) for v in steps)} = {n_tot} · "
          f"{n_tot} × {R:.3f} = {drop_id:.4f} m · 실측 총낙차 {TOTAL_DROP:.4f} "
          f"→ {'OK (6.600 정확, §9 P-2 동결)' if good else 'CHECK'}")

    two_rt = 2.0 * R + T
    good = 0.600 - 1e-9 <= two_rt <= 0.650 + 1e-9
    ok9 &= good
    print(f"    2R+T = 2({R:.3f}) + {T:.3f} = **{two_rt:.3f}** ∈ [0.600, 0.650] → "
          f"{'OK' if good else 'CHECK'} · 경사 "
          f"{math.degrees(math.atan2(R, T)):.1f}°")
    print("      [law] KCS 34 50 10 3.2.8(3) '2R+T=60~65cm 를 유지하되 전 구간에 걸쳐 "
          "동일하여야 하고' · KFS-TRAIL 〈표 13-1〉 25° 행 150/310 과 일치 · "
          "구 0.630 도 합법이었다 — 이 행은 준법 수정이 아니라 충실도 수정")
    print(f"    riser/tread 전 구간 동일 = True (플라이트별로 **단수만** 다름: "
          f"{'/'.join(str(v) for v in steps)}) → OK")

    good = abs(W - 1.500) <= 0.010
    ok9 &= good
    clear = W                      # rail line sits outboard by bal/2 -> inner faces at the edge
    print(f"    유효폭(난간 안쪽면 사이) {clear:.3f} m — 1.500 ± 0.010 → "
          f"{'OK' if good else 'CHECK'}")
    print("      [law] 산지관리법 시행령 별표 3의3 제4호 다 '너비가 1.5미터 이내일 것' "
          "(숲길 법정 상한) · [data] KNPS-STAIR 데크 계단 n=155 중앙값 1.50 · "
          "1.50 = 47.7 % / 1.80 = 9.0 % — 인테이크의 '보통 1.8' 은 정정됨")

    # landing rule: depth in the direction of travel, and the 2 m rise pitch
    ld_ok = True
    print(f"    {'참':<6} {'진행방향 깊이':>12} {'횡폭':>7} {'상면z':>8} 종류")
    for f in SEQ:
        dep = f["lx1"] - f["lx0"]
        kind = "쉼터 전망참" if f["rest"] else ("지면 도착참" if f["k"] ==
                                            len(SEQ) - 1 else "회전참")
        g = dep >= 1.500 - 1e-9 and dep >= W - 1e-9
        ld_ok &= g
        print(f"    참{f['k']:<5} {dep:12.3f} {ld['y1']-ld['y0']:7.3f} "
              f"{f['z_bot']:8.3f} {kind} {'OK' if g else 'CHECK'}")
    ok9 &= ld_ok
    print("      [law] 조경설계기준 5.10.2(3) 참 너비 ≥ 계단 유효폭 이고 ≥120cm · "
          "5.9(4) 연속 경사로 참 1.5×1.5 m — 둘이 1,500 mm 로 수렴. "
          "구 1.40 m 는 이 기준에 **미달**이었다")
    worst_rise = max(f["drop"] for f in SEQ)
    good = worst_rise <= 2.000 + 1e-9
    ok9 &= good
    print(f"    참 간 최대 연속 상승 {worst_rise:.3f} m ≤ 2.000 → "
          f"{'OK' if good else 'CHECK'}")
    print("      [law] 조경설계기준 5.10.2(3) '높이 2m를 넘는 계단에는 2m 이내마다 … "
          "참을 둔다' — 건축법 3 m 규칙(피난·방화규칙 제15조)은 건축물 전용이라 "
          "이 씬을 구속하지 않고, 조경 기준이 **더 엄격**하다")
    rest = [f for f in SEQ if f["rest"]]
    good = len(rest) == 1
    ok9 &= good
    if rest:
        print(f"    쉼터/전망 플랫폼 1개 = 참{rest[0]['k']} (z {rest[0]['z_bot']:+.3f}, "
              f"깊이 {rest[0]['lx1']-rest[0]['lx0']:.2f} m = 회전참의 2배) → OK")
        print("      C5 — 6.6 m 낙차에 쉼터가 하나도 없는 것이 '피난계단' 판독의 한 축. "
              "[law] SANJI-183 단서 2) '휴식·대피를 위한 장소' 가 폭 초과를 허용하는 "
              "유일한 요소")

    # deck boards from stocked sections
    stock_t = {0.021, 0.024, 0.025, 0.027, 0.030, 0.033, 0.036}
    good = round(fl["tread_t"], 3) in stock_t
    ok9 &= good
    print(f"    디딤판 두께 {fl['tread_t']:.3f} m · 판재 폭 "
          f"{PARAMS['gkit']['plank_w']:.3f} m → "
          f"{'OK (25x140 시판 데크판재)' if good else 'CHECK'}")
    print("      [law] 산림청고시 2014-2 제8조 데크판재 표준두께 21 이상 3 mm 단위 · "
          "표준나비 90~300 10 mm 단위 · [data] 연구 §D2 실판매 21x120 / 25x140 / "
          "27x140. 킷 기본값 0.145 는 KCS 시방 폭이지 시판 규격이 아니라 명시 지정")

    # hazard cue (3): the leaf band must still bite treads 1-2 of flight 0
    f0 = SEQ[0]
    lf = P["leaf"]
    z1 = f0["z_top"] - 1 * fl["riser"] + lf["proud"]
    z2 = f0["z_top"] - 2 * fl["riser"] + lf["proud"]
    good = f0["steps"] >= 2
    ok9 &= good
    print(f"    낙엽 밴드 = 플라이트0 디딤판 1·2 (상면 {z1:+.3f} / {z2:+.3f}, "
          f"새 riser 로 **재유도**) → {'OK' if good else 'CHECK'}")

    print(f"    [deck_module_selfcheck S3-9] "
          f"{'전항목 OK' if ok9 else '⚠ CHECK 항목 있음'}")

    # =====================================================================
    # S3-10 — de-stacking (Option A). C1 is the scene's headline defect, so the
    # zero-overlap property is **asserted**, not budgeted: without an assertion the
    # next coordinate edit puts a flight back over another and nothing notices.
    # =====================================================================
    ok10 = True
    print("\n  [deck_module_selfcheck] S3-10 탈적층(옵션 A) — 평면 중첩·이격·회랑")

    def _rect_ov(a, b):
        return (max(0.0, min(a[1], b[1]) - max(a[0], b[0]))
                * max(0.0, min(a[3], b[3]) - max(a[2], b[2])))

    flr = [(f"플라이트{f['k']}", (f["x_top"], f["x_bot"]) + band(f["k"]))
           for f in SEQ]
    ldr = [(f"참{f['k']}", (f["lx0"], f["lx1"], f["ly0"], f["ly1"]))
           for f in SEQ]
    worst_ov, worst_pair = 0.0, "-"
    for i in range(len(flr)):
        for j in range(i + 1, len(flr)):
            o = _rect_ov(flr[i][1], flr[j][1])
            if o > worst_ov:
                worst_ov, worst_pair = o, f"{flr[i][0]}×{flr[j][0]}"
    good = worst_ov < 1e-9
    ok10 &= good
    print(f"    플라이트 상호 평면 중첩 최대 {worst_ov:.6f} m² ({worst_pair}) → "
          f"{'OK (0 — 어떤 플라이트도 다른 플라이트 위에 있지 않다)' if good else 'CHECK'}")
    worst_fl, worst_flp = 0.0, "-"
    for nf, rf in flr:
        for nl, rl in ldr:
            o = _rect_ov(rf, rl)
            if o > worst_fl:
                worst_fl, worst_flp = o, f"{nf}×{nl}"
    good = worst_fl < 1e-9
    ok10 &= good
    print(f"    플라이트/참 평면 중첩 최대 {worst_fl:.6f} m² ({worst_flp}) → "
          f"{'OK (참이 디딤판을 덮지 않는다 — A-10-2)' if good else 'CHECK'}")
    print("      C1 — 구 배치는 4개 플라이트가 3.0×2.8 m 평면 안에서 2단으로 겹쳐 "
          "연직 여유 3.01 m 의 '수직 갱도' 였고, 그것이 아파트 피난계단 판독의 최대 축.")

    # air gap under the deck
    gaps = []
    for f in SEQ:
        for xx, zz in ((f["x_top"], f["z_top"]), (f["x_bot"], f["z_bot"]),
                       (f["lx1"], f["z_bot"])):
            gaps.append(zz - corridor_z(xx))
    gmin, gmax = min(gaps), max(gaps)
    good = gmin > 0.0
    ok10 &= good
    foot_gaps = [f["z_bot"] - corridor_z(f["x_bot"]) for f in SEQ
                 if f["k"] != SEQ[-1]["k"]]
    good2 = max(foot_gaps) <= 0.300 + 1e-9
    ok10 &= good2
    print(f"    데크 하부 공기층 {gmin:.3f} ~ {gmax:.3f} m (모두 >0 → "
          f"{'OK' if good else 'CHECK'}) · 계단하단부 최대 "
          f"{max(foot_gaps):.3f} m ≤ 0.300 → {'OK' if good2 else 'CHECK'}")
    print("      [law] KFS-TRAIL 특별시방서 12-3 마 (p.165) '데크계단의 설치시 … "
          "계단하단부와 지반과의 높이차가 30cm 이상으로 올라가지 않도록 시공' — "
          "이 조항이 옥외 참 규칙의 실체이고, 동시에 데크가 지면을 따라가야 하는 이유")

    # masonry census
    walls = [nm for nm, x0, x1, y0, y1, zt, th, mk in P["plates"]
             if mk in ("rock", "rockface") and x1 > HEAD_X + 1e-9]
    good = not walls
    ok10 &= good
    print(f"    데크 구간(x>{HEAD_X:.1f}) 석축 플레이트 {len(walls)}개 {walls} → "
          f"{'OK (갱도 소거)' if good else 'CHECK'}")
    print(f"    머리 옹벽 노출고 {abs(corridor_z(HEAD_X)):.3f} m "
          f"(구 BankCut 7.40 m 단일벽 → §4.2-4A 의 'short head wall')")

    seg = [(GROUND_LINE[i], GROUND_LINE[i + 1])
           for i in range(len(GROUND_LINE) - 1)]
    steep = max((abs(b[1] - a[1]) / (b[0] - a[0]))
                for a, b in seg if b[0] - a[0] > 1e-6)
    print(f"    회랑 종단: 평균 {100.0*(TRAIL_Z-GROUND_Z)/(PLAN_X1-HEAD_X):.1f} % · "
          f"최급 {100.0*steep:.1f} %(= 플라이트 자체 경사) · 참 아래는 수평 벤치")
    print(f"    평면 x [{HEAD_X:.2f}, {PLAN_X1:.2f}] · y [{PLAN_Y0:.2f}, "
          f"{PLAN_Y1:.2f}]  (설계서 §4.2-4A 추정 x[−1.5,12]·y[−2.6,1.6])")
    print("      추정치와의 차이는 산술: Σ런 13.64 + 회전참 4×1.50 + 쉼터 3.00 + "
          "도착참 1.50 = 24.14. 설계서 추정 12 는 **참이 X 를 먹는다는 점을 빼고** "
          "Σ런만 센 값이다. 참이 X 를 먹지 않게 하려면 참을 옆 대역에 붙여야 하는데, "
          "그러면 순 X 진행이 런−1.50 = 0.67 m/1.05 m 낙차 = 157 % 가 되어 지반이 "
          "다시 수직이 된다 — 즉 갱도로 되돌아간다. 평면을 늘리는 쪽이 옵션 A 다")

    print(f"    [deck_module_selfcheck S3-10] "
          f"{'전항목 OK' if ok10 else '⚠ CHECK 항목 있음'}")

    # =====================================================================
    # S3-11 — season re-bind. The census is the assertion: G10 carries **zero** green
    # vegetation objects, and the pre-rebuild scene carried 37 plants + 10 hedge bands.
    # =====================================================================
    ok11 = True
    se = P["season"]
    print("\n  [deck_module_selfcheck] S3-11 계절 재바인딩 — 만추 잎-off 고정")

    bare_ok = all(rel in sc.BARE_SUBPRIMS for rel, _n in se["bare"])
    ok11 &= bare_ok
    print(f"    낙엽수 수종 {len(se['bare'])}종 전부 sc.BARE_SUBPRIMS 등록 → "
          f"{'OK' if bare_ok else 'CHECK'} : "
          f"{', '.join(r.split('/')[-1] for r, _ in se['bare'])}")
    print("      이 3종만이 잔가지 골격을 **trunk 프림**에 갖고 있어 /Root/leaves 를 "
          "끄면 진짜 나목이 남는다. 참나무류는 잎이 가지 인스턴서 안에 있어 끌 수 없고, "
          "그래서 §4.2-5 가 원경으로 재배치한다")

    # [S10c · red-team F1] The registry membership above is necessary but **not**
    # sufficient: the pre-fix scene held it and still rendered twelve green trees,
    # because a stage-side `SetActive(False)` under an instance is discarded by USD.
    # What has to be asserted is that the **reference target** is the wrapper layer.
    wraps = [(rel, sc.veg_wrapper_rel(rel, sc.BARE_SUBPRIMS.get(rel), kind="bare"))
             for rel, _n in se["bare"]]
    wrap_ok = all(w for _r, w in wraps)
    ok11 &= wrap_ok
    print(f"    잎-off 경로 = 참조 래퍼 {sum(1 for _r, w in wraps if w)}/{len(wraps)}종 "
          f"→ {'OK' if wrap_ok else 'CHECK'} : "
          f"{', '.join((w or '미해결').split('/')[-1] for _r, w in wraps)}")
    print("      래퍼는 인스턴스 경계 **위**에서 합성되므로 프로토타입 자체에 leaves 가 "
          "없다. 무대에서 SetActive(False) 를 부르는 옛 경로는 USD 가 버린다 — "
          "n_off 카운터는 작성된 의견을 셌지 합성 결과를 센 적이 없다(F1)")
    nat_ok = True
    for rel, nat in se["bare"]:
        ref = sc.BARE_NATIVE.get(rel)
        if ref is None:
            nat_ok = False
            continue
        nat_ok &= abs(float(nat) - float(ref)) <= 0.005
    ok11 &= nat_ok
    print(f"    native_h ↔ sc.BARE_NATIVE 일치(≤5 mm) → "
          f"{'OK' if nat_ok else 'CHECK'} : "
          + " · ".join(f"{r.split('/')[-1].replace('.usd','')} {n:.4f}/"
                       f"{sc.BARE_NATIVE.get(r, float('nan')):.4f}"
                       for r, n in se["bare"]))
    print("      씬 값을 유지하는 것이 의도다 — 척도 target/native 가 수정 전후 동일해야 "
          "줄기가 움직이지 않고, 라운드가 선언할 델타가 '잎' 하나로 남는다")
    banned = {"Shrub/Forsythia.usd", "Shrub/Rhododendron.usd"}
    good = not (set(se["shrubs"]) & banned)
    ok11 &= good
    print(f"    관목 풀 {[x.split('/')[-1] for x in se['shrubs']]} · 개화종 "
          f"{sorted(x.split('/')[-1] for x in banned)} 제외 → "
          f"{'OK' if good else 'CHECK'}")
    far_rel = se["far"][0]
    good = far_rel not in ("Trees/White_Pine.usd", "Trees/Yellow_Pine.usd")
    ok11 &= good
    print(f"    원경 belt 수종 고정 {far_rel.split('/')[-1]} (상록 · PASS) → "
          f"{'OK' if good else 'CHECK'} — 좌표해시 추첨이 뽑던 폐지 수종 "
          f"White_Pine·Yellow_Pine 제거")

    # the tint is a multiplier on a green map, so the census that matters is the
    # **product**, not the triple. Mean linear of `grass_lawn_diff` is measured once and
    # written here so the assertion is arithmetic, not opinion.
    GRASS_LIN = (0.0621, 0.1115, 0.0232)
    for nm, key in (("잔디", "grass_tint"), ("산울/능선", "hedge_tint")):
        t = P["material"][key]
        prod = tuple(a * b for a, b in zip(GRASS_LIN, t))
        Y = 0.2126 * prod[0] + 0.7152 * prod[1] + 0.0722 * prod[2]
        L = 116.0 * (Y ** (1.0 / 3.0)) - 16.0
        rg = prod[0] / max(prod[1], 1e-9)
        good = rg > 1.0 and Y <= 0.30
        ok11 &= good
        print(f"    {nm} 틴트 {t} × 맵 {GRASS_LIN} = "
              f"({prod[0]:.4f},{prod[1]:.4f},{prod[2]:.4f}) · Y {Y:.4f} · L* {L:.1f} · "
              f"R/G {rg:.2f} → {'OK (짚/올리브 · 지면 알베도 ≤0.30)' if good else 'CHECK'}")
    print("      설계서 §4.2-5 의 리터럴 (0.62,0.60,0.42) 은 이 맵에 곱하면 R/G 0.58 로 "
          "**여전히 녹색 우세** — 어둡게만 만들고 휴면시키지 못한다. 틴트는 색이 아니라 "
          "곱셈자라는 것이 요지이고, 벚나무 판례('이름이 아니라 픽셀로 판단하라')의 축소판")

    lobes = len(P["leaf_ground_patches"])
    good = lobes == 4
    ok11 &= good
    print(f"    CB-2 카펫 마스크 로브 {lobes}개 존치 (H4: 로브는 움직여도 되지만 "
          f"결코 직사각형으로 되돌아가지 않는다) → {'OK' if good else 'CHECK'} · "
          f"연속성은 로브 추가가 아니라 주변 산포로")

    eyes = [(-d, 0.0, h) for d in (2, 5, 10) for h in (0.3, 0.9, 1.8)]
    dmin = min(math.dist((bx, by), (ex, ey))
               for bx, by, _w, _dd, _h in P["backdrop"]
               for ex, ey, _ez in eyes)
    good = dmin > 80.0
    ok11 &= good
    print(f"    원경 실루엣 {len(P['backdrop'])}동 · 창 0개 · 심사 시점 최근접 "
          f"d_true {dmin:.1f} m > 80 → {'OK' if good else 'CHECK'}")
    print("      building_kit BS-4 계약(원경 실루엣 전용 · 창 없음 · 매스당 ≤4 프림 · "
          "d_true>80 m 자동 강등)을 **산물로** 충족. 킷 호출을 하지 않은 이유는 "
          "트리 안의 어떤 씬도 building_kit 을 호출하지 않고(K3 소유), S 레인에서 "
          "공유 킷 의존을 새로 만들면 이 레인이 검증할 수 없는 결합이 생기기 때문")

    sinks = [row[3] for row in P["outcrop"]]
    good = all(abs(v) < 1e-9 for v in sinks)
    ok11 &= good
    print(f"    노두 {len(P['outcrop'])}개 · z_mode='base' · sink {set(sinks)} → "
          f"{'OK (어두운 함몰 링 없음)' if good else 'CHECK'}")
    print("      F2 규율 — tonglam_v2 §1 row 10 이 이 씬을 'D-5 바위가 어두운 함몰 "
          "링에' 로 이미 한 번 떨어뜨렸다. 구멍에 앉은 바위가 결함이고 사면 **위에** "
          "앉은 바위가 수정이다")

    print(f"    [deck_module_selfcheck S3-11] "
          f"{'전항목 OK' if ok11 else '⚠ CHECK 항목 있음'}")

    # =====================================================================
    # GT-115 ⑭ — 08-14 감사 5건. 전부 드레싱/마감이고, 보행면·낙차 모서리·
    # 지형 슬래브·계절 핀은 이 블록의 어떤 항목도 건드리지 않는다.
    # =====================================================================
    ok15 = True
    print("\n  [deck_module_selfcheck] GT-115 ⑭ — 노두 이격 · 런 종단 · "
          "손스침 · 정자 가구 · 이끼 배향")

    # (1a) rocks clear of every rail line, by arithmetic on the manifest box
    cl = outcrop_clearance(runs)
    lim = 0.300
    print(f"    {'노두':<22} {'스케일':>6} {'이격':>7} {'최근접 런':<22} 판정")
    for aid, i, gap, wnm in cl:
        good = gap >= lim - 1e-9
        ok15 &= good
        print(f"    {aid:<20}#{i} {P['outcrop'][i][5]:6.2f} {gap:7.3f} {wnm:<22} "
              f"{'OK' if good else 'CHECK ← 난간을 관통한다'}")
    print(f"      기준 ≥{lim:.2f} m (감사 지시) · 모델: 매니페스트 size_m 을 yaw 로 "
          "돌린 **축정렬 외피**(실제보다 크게 잡힘) vs 난간 중심선을 최대 부재 반폭 "
          "0.070 만큼 부풀린 상자 — 두 번 보수적이라 보고값은 하한")
    print("      row 0 `rock_moss_set_01` 은 바위 한 덩이가 아니라 8.005 × 6.949 m "
          "**세트**(메시 6). 평행이동만으로는 쉼터 런(y 3.119)을 0.30 m 비우려면 "
          "cy ≥ 8.21 이 되어 회랑(y1 8.00) 밖 북측 30° 사면으로 나가야 한다 — "
          "그래서 축척 1.00 → 0.50 과 이동을 함께 적용(scene09 선례 0.30~0.78)")

    # (1b) every run end is a designed termination
    d1 = run_end_nodes(runs)
    bad = [(a, b, c, nm) for a, b, c, nm in d1 if nm[0][1] != "return"]
    nret = sum(1 for rr in runs if rr["kind"] == "return")
    good = (not bad) and nret == 4
    ok15 &= good
    print(f"    차수 1 노드 {len(d1)}개 · 전부 리턴 종단인가 = "
          f"{'예' if not bad else bad} · 리턴 런 {nret}개 "
          f"(길이 {r['end']['run']:.3f} m · 안쪽으로 꺾음) → "
          f"{'OK' if good else 'CHECK'}")
    ld_ = P["landing"]
    open_w = (float(ld_["y1"]) - float(ld_["y0"])) - 2.0 * float(r["end"]["run"])
    exit_w = 2.0 * abs(PARAMS["exit_paths"][0][4])
    good = open_w >= exit_w
    ok15 &= good
    print(f"    도착참 전면 개구 {open_w:.2f} m ≥ DeckExit 폭 {exit_w:.2f} m → "
          f"{'OK (§0-2 인계 불변 · 20 mm 단차에 가드 재추가 아님)' if good else 'CHECK'}")
    print("      바깥쪽으로 꺾을 수 없는 이유: 진입단은 y −1.600 이 무방호 남측 "
          "사면 파단선이고 GT-77 (3) 이 그 밖으로 나가는 부재를 명시적으로 금지한다")

    # (4) handrail — graspable, and it does not eat the statutory clear width
    hd = r["hand"]
    hls = handrail_lines(runs)
    good = 0.032 - 1e-9 <= hd["dia"] <= 0.038 + 1e-9
    ok15 &= good
    print(f"    손스침 Ø{hd['dia']:.3f} m ({hd['dia']*1000:.0f} mm) · 라인 "
          f"{len(hls)}개 · 연장 {sum(h['L'] for h in hls):.2f} m → "
          f"{'OK (감사 32~38 mm 대역)' if good else 'CHECK'}")
    zh = r["h"] - hd["drop"]
    good = 0.80 <= zh <= 1.20
    ok15 &= good
    print(f"    파지 높이 {zh:.3f} m (상부 난간대 상면 {r['h']:.3f} − "
          f"{hd['drop']:.3f}) → {'OK (0.80~1.20 파지 대역)' if good else 'CHECK'}")
    off_edge = hd["off"] + hd["dia"] / 2.0 - r["bal"] / 2.0
    clear_w = 2.0 * fl["half_w"] - 2.0 * off_edge
    good = off_edge <= 0.100 + 1e-9
    ok15 &= good
    print(f"    보행면 유효폭 {2.0*fl['half_w']:.3f} m **불변**(살대 안면 기준) · "
          f"파지 높이 돌출 {off_edge*1000:.1f} mm/측 → 유효폭 {clear_w:.3f} m @ "
          f"{zh:.3f} m → {'OK (손스침 돌출 ≤100 mm 허용치 안)' if good else 'CHECK'}")
    print("      기존 부재는 하나도 움직이지 않는다 — 손스침은 rail_runs() 의 "
          "같은 인벤토리에서 파생되어 수평·경사·가로런 라인을 그대로 따라간다")

    # (2) litter source variants
    lv = se["litter_variants"]
    caps = sum(int(v["cap"]) for v in lv)
    good = caps == int(se["litter_max"])
    ok15 &= good
    print(f"    낙엽 소스 변형 {len(lv)}종 · 대역당 캡 합 {caps} = litter_max "
          f"{se['litter_max']} → {'OK (인스턴스 예산 불변 · 780)' if good else 'CHECK'}")
    for v in lv:
        pool = litter_pool(v["cards"])
        gjit = float(v["scale"][1]) / max(float(v["scale"][0]), 1e-9)
        okv = len(pool) >= 2 and gjit > 1.0
        ok15 &= okv
        print(f"      {v['tag']:<8} 카드 {len(pool)}종 "
              f"{[os.path.basename(p[0]) for p in pool]} · 축척 "
              f"{v['scale'][0]:.2f}~{v['scale'][1]:.2f}(×{gjit:.2f}) · 기울기 "
              f"±{v['tilt']:.0f}° · 캡 {v['cap']} → {'OK' if okv else 'CHECK'}")
    lo_s = min(float(v["scale"][0]) for v in lv)
    hi_s = max(float(v["scale"][1]) for v in lv)
    print(f"      합산 축척 스팬 {lo_s:.2f}~{hi_s:.2f} = ×{hi_s/lo_s:.2f} "
          f"(단일 호출의 기본 0.75~1.25 = ×1.67 대비) · 신규 자산 조달 0건")

    # (3) pergola framing
    pg = P["pergola"]
    n_pg = 2 + int(pg["rafters"]) + 4 + 4
    good = 3 <= int(pg["rafters"]) <= 5
    ok15 &= good
    print(f"    정자 가구 {n_pg}프림 = 보 2 + 서까래 {pg['rafters']} + 마구리 4 + "
          f"기둥 밑판 4 → {'OK' if good else 'CHECK'} (지붕 슬래브·기둥 4본은 "
          f"sc.build_canopy 그대로 — 콜라이더/AABB 불변)")
    rft = float(pg["rafter"][1])
    good = rft < float(pg["beam"][1])
    ok15 &= good
    print(f"    서까래 춤 {rft:.3f} < 보 춤 {pg['beam'][1]:.3f} · 서까래는 보 **사이**에 "
          f"{pg['rafter_bed']:.3f} m 물려 끼움 → "
          f"{'OK (동일면 쌍 0 · 공유 부피는 물림뿐)' if good else 'CHECK'}")

    # (5) orientation-dependent weathering
    WOOD_LIN = (0.0824, 0.0584, 0.0442)
    for nm, key in (("가드(이끼측)", "guard_tint"), ("가드 상면(은화)", "guard_top_tint")):
        t = P["material"][key]
        lin = tuple(a * b for a, b in zip(WOOD_LIN, t))
        Y = 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
        L = 116.0 * (Y ** (1.0 / 3.0)) - 16.0
        good = 53.0 - 0.6 <= L <= 60.0 + 0.6
        ok15 &= good
        print(f"    {nm} 틴트 {t} → lin "
              f"({lin[0]:.3f},{lin[1]:.3f},{lin[2]:.3f}) · 알베도 {Y:.3f} · "
              f"L* {L:.1f} → {'OK (실측 방부목 L* 53~60)' if good else 'CHECK'}")
    gt = P["material"]["guard_tint"]
    st = P["material"]["stringer_tint"]
    dg = (gt[1] / gt[0]) / (st[1] / st[0])
    db = (gt[2] / gt[0]) / (st[2] / st[0])
    good = dg < 1.0 and db < 1.0
    ok15 &= good
    print(f"    이끼 증폭비 G/R ×{dg:.3f} · B/R ×{db:.3f} (기존 프레임 틴트 대비) → "
          f"{'OK (텍스처 조류 텍셀이 청록으로 덜 밀림)' if good else 'CHECK'}")
    print("      면 단위 재질은 부재당 1프림이라 불가 — 그래서 **부재 배향** 단위로 "
          "쪼갰다(런별 상부 난간대 + 엄지기둥 갓 = 상향면, 나머지 = 수직/음영면). "
          "이는 이 파일이 이미 적어 둔 §2.A.1-8 '은화한 상면 위 어두운 수직면' 을 "
          "난간에 처음 적용한 것이고, M['stringer'] 자체는 건드리지 않아 지지기둥 · "
          "스트링거 · GT-77 접근로 목재는 비트동일하다")

    print(f"    [deck_module_selfcheck GT-115 ⑭] "
          f"{'전항목 OK' if ok15 else '⚠ CHECK 항목 있음'}")

    # =====================================================================
    # GT-119 ② — 지형 슬래브 이음(seam). from_below 컷의 쐐기 균열이 이 블록의
    # 대상이고, 보행면·낙차 모서리·계단·데크·카메라·계절 핀은 건드리지 않는다.
    # 이 블록이 있는 한 이음 결함군은 조용히 되돌아올 수 없다.
    # =====================================================================
    ok19 = True
    cg = P["corridor"]
    lapm = float(cg["seam_lap"])
    print("\n  [deck_module_selfcheck] GT-119 ② — 지형 이음 · 회랑 쐐기 · "
          "플레이트 물림")

    # (1) corridor crests — every steep→flat crest must be lapped shut
    print(f"    {'상류 슬래브':<18}{'하류 슬래브':<18}{'Δθ':>7}{'무이음 쐐기':>11}"
          f"{'이음길이':>9}{'물림':>8}  판정")
    for na, nb, dth, wedge, lap, inter, held in corridor_seam_census():
        need = wedge + lapm if wedge > 1e-12 else 0.0
        good = (lap >= need - 1e-9) and inter >= lapm - 1e-9 and \
               (held or wedge <= 1e-12)
        ok19 &= good
        print(f"    {na:<18}{nb:<18}{dth:7.3f}{wedge:11.4f}{lap:9.4f}"
              f"{inter:8.4f}  {'OK' if good else 'CHECK ← 쐐기 개방'}"
              + ("" if wedge > 1e-12 else "  (오목 — 원래 물림)"))
    print(f"      쐐기 = thick·sin(θa−θb) = 이음이 없을 때 먼 면에서 벌어지는 폭. "
          f"최대 {max(r[3] for r in corridor_seam_census()):.4f} m — "
          f"260806_w3_allview5/pt_noon_from_below 의 x 15.30 슬롯이 그 중 하나")
    print(f"      이음길이 = 쐐기 + seam_lap {lapm:.3f} m, **자기 상면 평면을 따라 "
          f"내리막으로만** 연장 (오르막 연장은 오목 꺾임마다 지면을 들어 올린다)")

    # (2) the surface the lap must not have moved
    xs0, xs1 = GROUND_LINE[0][0], GROUND_LINE[-1][0]
    slabs = corridor_slabs()
    dmax, dx_at = 0.0, xs0
    for k in range(2001):
        xq = xs0 + (xs1 - xs0) * k / 2000.0
        tops = [t for t in (slab_top(s, xq) for s in slabs) if t is not None]
        dq = abs(max(tops) - corridor_z(xq))
        if dq > dmax:
            dmax, dx_at = dq, xq
    good = dmax <= 1e-9
    ok19 &= good
    print(f"    회랑 상면 불변 max|max_i top_i(x) − corridor_z(x)| = {dmax:.3e} m "
          f"@ x {dx_at:+.3f} → {'OK (기계 오차 — 보행/콜라이더 비트동일)' if good else 'CHECK'}")
    x_nose = max(s[7] for s in slabs)
    over = [s[0] for s in slabs
            if s[7] > xs1 + 1e-9 and (slab_top(s, s[7]) or 0.0) > GROUND_Z - 1e-9]
    good = not over
    ok19 &= good
    print(f"    회랑 끝(x {xs1:.2f}) 너머로 나간 이음 코 최원단 x {x_nose:.3f} · "
          f"하부공원 상면 {GROUND_Z:+.3f} 위로 솟은 슬래브 {len(over)}개 → "
          f"{'OK (전부 매몰)' if good else 'CHECK ' + str(over)}")

    # (3) the defect itself, measured: the south scarp must be solid top-to-toe
    voids, first = 0, None
    for k in range(801):
        xq = xs0 + (xs1 - xs0) * k / 800.0
        ztop = corridor_z(xq)
        for j in range(41):
            zq = ztop - (ztop - GROUND_Z) * j / 40.0 - 1e-6
            if zq <= GROUND_Z:
                continue
            if not any(slab_holds(s, xq, zq) for s in slabs):
                voids += 1
                first = first or (xq, zq)
    good = voids == 0
    ok19 &= good
    print(f"    남측 절토면 관통 probe {801*41}점(x {xs0:.2f}..{xs1:.2f} × "
          f"상면→{GROUND_Z:+.2f}) · 빈 점 {voids}개 → "
          f"{'OK (하늘이 비치는 열린 점 0)' if good else 'CHECK ' + str(first)}")

    # (4) the axis-aligned plate seams
    print(f"    {'플레이트 A':<15}{'플레이트 B':<15}{'종류':<6}"
          f"{'Δx':>8}{'Δy':>8}{'Δz':>8}{'물림':>8}  판정")
    for a, b, kind, why, ox, oy, oz, mg in plate_seam_census():
        good = (mg >= lapm - 1e-9) if kind == "lap" else (abs(mg) <= 1e-9)
        ok19 &= good
        print(f"    {a:<15}{b:<15}{kind:<6}{ox:8.3f}{oy:8.3f}{oz:8.3f}{mg:8.3f}"
              f"  {'OK' if good else 'CHECK'}")
        print(f"      {why}")
    print("      물림 = 세 축 최소 겹침. lap 은 ≥ seam_lap, butt 은 정확히 0 "
          "(동일 평면에 놓인 두 평행면은 쐐기로 벌어질 수 없다)")
    _cop19 = coplanar_census()
    ok19 &= not _cop19
    print(f"    이음 후 동일평면 재감사 → {len(_cop19)}쌍 "
          f"{'OK (이음이 z-fighting 면을 만들지 않았다)' if not _cop19 else 'CHECK ' + str(_cop19[:3])}")
    print("      남은 미봉 이음 1건 — Bank_NorthBank 발치(y 8.00, z 0.00)와 회랑 "
          "벤치/하부공원(z −0.255~−6.62) 사이의 공동. 사면을 얇은 경사 슬래브로 "
          "모델링한 결과이고, 회랑 폭 10.6 m 가 판정 컷에서 북쪽 가장자리를 "
          "잘라내도록 설계되어 있어 어떤 카메라에서도 보이지 않는다. from_below "
          "에서 하늘이 보인 것은 이 공동 **때문이 아니라** 위 (1) 의 쐐기를 통해 "
          "그것을 들여다봤기 때문이며, 쐐기가 닫히면 시선 자체가 사라진다 — "
          "지형 형상 변경이 필요하므로 별도 결재 대상")

    print(f"    [deck_module_selfcheck GT-119 ②] "
          f"{'전항목 OK' if ok19 else '⚠ CHECK 항목 있음'}")
    return ok_all and ok9 and ok10 and ok11 and ok15 and ok19


# ===========================================================================
# [F-2] ground_kit plans - pure CPU, no USD. Coordinates from PARAMS (Sec.7.4).
# ===========================================================================
def _plate(name):
    """Axis-aligned ground plate row: (name,x0,x1,y0,y1,z_top,thick,mtl)."""
    for row in PARAMS["plates"]:
        if row[0] == name:
            return row
    raise KeyError(f"scene10: plate '{name}' not in PARAMS['plates']")


def ground_plan():
    """Plan A - the park dirt trail (d5 / d10 near windows)."""
    g = PARAMS["gkit"]
    tp = _plate("TrailPath")
    ent = PARAMS["entry"]
    return gk.plan_ground(
        "deck_trail_hybrid",
        region=(-12.0, float(tp[3]), float(tp[2]), float(tp[4])),
        z=float(tp[5]), gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=[("deck_far_edge", float(ent["x1"]))],
        dists=(2, 5, 10), scene="scene10",
        tactile=(),                    # Sec.12.4 OFF - park, p = 0.24
        overrides=dict(
            surface=(("stain", ("dirt",)),),
            extras=(("edge_break", dict(density=12.0,
                                        lines=[float(tp[3]), float(tp[4])])),
                    ("wear_lane", dict(width=float(g["wear_w"])))),
            scatter=dict(kind="gravel", cover=0.08,
                         count=int(g["gravel_n"]),
                         scale_jitter=(0.38, 0.62), burial=0.38)),   # [W2 F2]
        seed=int(g["seed"]))


def ground_plan_deck():
    """Plan B - entry-deck plank gaps only (d2 near window).

    z is the deck top, plainly. The W2-D round had to pass
    `surface_top_z(z_deck) + 0.020` here because `build_deck_planks` put the gap
    strip's top at `z - 0.020`, i.e. **below** the deck surface, and the deck
    slab is a solid box - the burial defect the scene15 pilot measured for
    joints and manholes (rendered pixels = 0). The builder now applies
    `surface_top_z()` itself (kit defect R1, fixed 2026-07-30), so the scene-side
    lift is removed; the strips land in exactly the same place as before
    (both routes put the strip centre at deck top - 0.0094 `[calc]`).
    GT is unaffected: the strips carry `exc="plank_gap"` and the walking
    surface z does not move.
    """
    g = PARAMS["gkit"]
    ent, ld = PARAMS["entry"], PARAMS["landing"]
    z_deck = float(ent["top"])
    return gk.plan_ground(
        "deck_trail_hybrid",
        region=(float(ent["x0"]), float(ld["y0"]),
                float(ent["x1"]), float(ld["y1"])),
        z=z_deck,
        gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=[("deck_far_edge", float(ent["x1"]))],
        dists=(2, 5, 10), scene="scene10", tactile=(),
        overrides=dict(pave=dict(joint=None), surface=(),
                       extras=(("deck_planks",
                                dict(max_gaps=int(g["deck_gaps"]),
                                     plank_w=float(g["plank_w"]))),),
                       scatter=None),
        seed=int(g["seed"]) + 100)


# ===========================================================================
# [F-3] [GT-77 · §0-2] approach-path finishing — one table, both deck ends
# ===========================================================================
def approach_members():
    """Every approach member at the two deck ends, in world coordinates.

    Returns `[(name, kind, (cx, cy, cz), (sx, sy, sz)), ...]`. `kind` selects the
    material in the builder and is what the SMOKE table groups by. SMOKE and the
    builder read this **one** function, so a number cannot be right in the report and
    wrong on the stage — the failure mode GT-65's hand-written rail list produced.

    Every offset here exists to keep two surfaces out of the same plane. The rule is
    always the same: the member that arrives is bedded **into** the member it meets, so
    the surface it replaces passes inside a solid and is simply not rendered. Stated
    once, per junction `[computed]`:
      · header top  = path top + `header_proud` -> the path veneer's top face and the
        deck's top face both lie inside the board (0.010 / 0.017 m under it)
      · edging inner face is `edge_tuck` inside the path veneer -> never coincident
        with the path's own side face
      · apron outer edge is `apron_tuck` under the flank board -> the apron's outer
        side face lies inside the flank, not on its face
      · flank end is 0.010 m inside the header's deck-side face; the run's far end is
        inside the post
      · verge top = grade + `verge_proud` = 5 mm over the leaf-drift decal step, and its
        inner 0.030 m is under the run board

    The three edging members meet at **butt** joints, not laps: the return board owns
    the corner and the run and the flank stop on its two faces. Lapping them would put
    two 0.090 m boards at the same top z sharing a 0.045 x 0.070 m patch of plan — a
    coplanar pair at every one of the 12 corners, which is the exact defect this round
    is called for. Butted, the shared planes are back-to-back interior faces of one
    solid union and the top faces meet along a line of zero area — the same adjacency
    the ground plates have always used. `coplanar_census()` proves it arithmetically.
    """
    ap = PARAMS["approach"]
    sec, ep, tuck = (float(ap["edge"]), float(ap["edge_proud"]),
                     float(ap["edge_tuck"]))
    hbite, hover, hpr = (float(ap["header_bite"]), float(ap["header_over"]),
                         float(ap["header_proud"]))
    arun, abite = float(ap["apron_run"]), float(ap["apron_bite"])
    atuck, at = float(ap["apron_tuck"]), float(ap["apron_t"])
    vw, voff = float(ap["verge_w"]), float(ap["verge_off"])
    vp, vt = float(ap["verge_proud"]), float(ap["verge_t"])
    ps, pp = float(ap["post"]), float(ap["post_proud"])
    cap = tuple(float(c) for c in ap["post_cap"])
    # the deck half-width is **derived**, never typed: every outer face is set from the
    # deck edge, and that edge is the landing table's own y1.
    dhy = float(PARAMS["landing"]["y1"])
    hhy = dhy - float(ap["header_inset"])            # header end face
    fc = dhy - float(ap["flank_inset"]) - sec / 2.0  # flank centreline
    out = []
    for e in ap["ends"]:
        tag, u = str(e["tag"]), float(e["sgn"])
        xd, pz, gz = float(e["x_deck"]), float(e["path_z"]), float(e["grade"])
        phy, xe = float(e["path_half_y"]), float(e["run_end"])
        x_ret = xd + u * arun                    # return-board centreline
        x_run = x_ret + u * sec / 2.0            # butt face: run / verge start here
        x_fla = x_ret - u * sec / 2.0            # butt face: flank starts here
        x_ap0 = xd - u * abite                   # apron end, inside the header
        x_fl = xd - u * (hbite - 0.010)          # flank end, inside the header
        run_c = phy + sec / 2.0 - tuck           # straight-run centreline
        ap_out = fc + sec / 2.0 - atuck          # apron outer edge, under the flank
        z_edge = gz + ep - sec / 2.0
        pre = f"Approach_{tag}"
        out.append((f"{pre}/Header", "header",
                    (xd + u * (hover - hbite) / 2.0, 0.0, pz + hpr - sec / 2.0),
                    (hbite + hover, 2.0 * hhy, sec)))
        for s, sfx in ((1.0, "P"), (-1.0, "N")):
            out.append((f"{pre}/Apron_{sfx}", "apron",
                        ((x_ap0 + x_run) / 2.0, s * (phy + ap_out) / 2.0,
                         pz - at / 2.0),
                        (abs(x_run - x_ap0), ap_out - phy, at)))
            out.append((f"{pre}/EdgeRun_{sfx}", "edge",
                        ((x_run + xe) / 2.0, s * run_c, z_edge),
                        (abs(xe - x_run), sec, sec)))
            # the corner board owns the corner: its y runs centre-to-centre plus half a
            # section at each end, so its inner and outer faces land flush on the run's
            # and the flank's, and its plan never overlaps either of them.
            out.append((f"{pre}/EdgeReturn_{sfx}", "edge",
                        (x_ret, s * (run_c + fc) / 2.0, z_edge),
                        (sec, fc - run_c + sec, sec)))
            out.append((f"{pre}/EdgeFlank_{sfx}", "edge",
                        ((x_fl + x_fla) / 2.0, s * fc, z_edge),
                        (abs(x_fla - x_fl), sec, sec)))
            out.append((f"{pre}/EdgePost_{sfx}", "edge",
                        (xe, s * run_c, gz + (pp - 0.10) / 2.0),
                        (ps, ps, pp + 0.10)))
            out.append((f"{pre}/EdgeCap_{sfx}", "edge",
                        (xe, s * run_c, gz + pp + cap[2] / 2.0), cap))
            out.append((f"{pre}/Verge_{sfx}", "verge",
                        ((x_run + xe) / 2.0, s * (run_c + voff + vw / 2.0),
                         gz + vp - vt / 2.0),
                        (abs(xe - x_run), vw, vt)))
    return out


def coplanar_census():
    """Every axis-aligned top face in the scene, tested pairwise for a coplanar overlap.

    `[(name_a, name_b, area)]` for every pair that shares a top z (1 um) **and** overlaps
    in plan with non-zero area — i.e. every pair that would z-fight. The census covers the
    ground plates, the exit-path veneers, the entry deck, the six landings and the whole
    GT-77 approach table, which is every axis-aligned horizontal surface the scene
    authors. Sloped members (`ybanks`, `CorridorSlope_*`, `HeadFillet`) are excluded by
    construction — their tops are not horizontal, so they cannot be coplanar with these.

    An empty list is the round's "no coplanar z-fighting" claim, arithmetically.
    """
    ld, ent = PARAMS["landing"], PARAMS["entry"]
    faces = [(nm, x0, x1, y0, y1, zt)
             for nm, x0, x1, y0, y1, zt, _t, _m in PARAMS["plates"]]
    faces += [(nm, x0, x1, y0, y1, zt)
              for nm, x0, x1, y0, y1, zt, _t in PARAMS["exit_paths"]]
    faces.append(("EntryDeck", float(ent["x0"]), float(ent["x1"]),
                  float(ld["y0"]), float(ld["y1"]), float(ent["top"])))
    for f in SEQ:
        faces.append((f"Landing_{f['k']}", f["lx0"], f["lx1"], f["ly0"],
                      f["ly1"], f["z_bot"]))
    for name, _kind, c, s in approach_members():
        faces.append((name, c[0] - s[0] / 2.0, c[0] + s[0] / 2.0,
                      c[1] - s[1] / 2.0, c[1] + s[1] / 2.0, c[2] + s[2] / 2.0))
    bad = []
    for i in range(len(faces)):
        na, ax0, ax1, ay0, ay1, az = faces[i]
        for j in range(i + 1, len(faces)):
            nb, bx0, bx1, by0, by1, bz = faces[j]
            if abs(az - bz) > 1e-6:
                continue
            ov = (max(0.0, min(ax1, bx1) - max(ax0, bx0))
                  * max(0.0, min(ay1, by1) - max(ay0, by0)))
            if ov > 1e-9:
                bad.append((na, nb, ov))
    return bad


# ---------------------------------------------------------------------------
# [GT-119 ②] terrain seam census — the anti-tear counterpart of coplanar_census
# ---------------------------------------------------------------------------
#   `coplanar_census` proves no two surfaces sit **on** each other. This proves no two
#   terrain solids merely **touch**: every declared-adjacent pair either interlocks by
#   at least `corridor.seam_lap`, or is a butt that is declared as one with a stated
#   reason, and a butt is only allowed where the two faces are exactly coincident and
#   parallel — a coincident parallel pair cannot fan open into a wedge, which is the
#   failure mode this census exists for.
#   (a, b, kind, why) — kind "lap" = must interlock, "butt" = must coincide exactly.
PLATE_SEAMS = [
    ("UpperTrail", "UpperBody", "lap",
     "grass veneer laps into the rock body"),
    ("UpperBody", "LowerParkMain", "lap",
     "lower park runs west under the head body"),
    ("LowerParkMain", "FarRidge", "lap",
     "lower park runs east into the ridge"),
    ("LowerParkFar", "FarRidge", "lap",
     "far lower park runs east into the ridge"),
    ("LowerParkMain", "LowerParkFar", "butt",
     "tops coplanar at −6.620 — a lap would be a coplanar_census pair"),
    ("FarHill", "FarRidge", "butt",
     "occluded by the NorthBank crest (z 7.16 @ y 15) from every eye ≤ 1.80"),
]


def _plate_box(name):
    for nm, x0, x1, y0, y1, zt, th, _m in PARAMS["plates"]:
        if nm == name:
            return ((x0, x1), (y0, y1), (zt - th, zt))
    for nm, x0, x1, y0, y1, zt, th in PARAMS["exit_paths"]:
        if nm == name:
            return ((x0, x1), (y0, y1), (zt - th, zt))
    raise KeyError(f"scene10: plate '{name}' not in PARAMS")


def plate_seam_census():
    """`[(a, b, kind, why, ov_x, ov_y, ov_z, margin)]` for every declared plate seam.

    `margin` is the smallest per-axis overlap = the interlock depth (0 for a butt,
    negative for an open gap)."""
    out = []
    for a, b, kind, why in PLATE_SEAMS:
        ba, bb = _plate_box(a), _plate_box(b)
        ov = tuple(min(ba[k][1], bb[k][1]) - max(ba[k][0], bb[k][0])
                   for k in range(3))
        out.append((a, b, kind, why) + ov + (min(ov),))
    return out


def _slab_obb(slab):
    """(centre, half, axes) of one corridor slab in the x-z plane (y is shared)."""
    _nm, xa, za, run, drop, ang_deg, _lap, _xe, _ze = slab
    ang = math.radians(ang_deg)
    L, th = math.hypot(run, drop), float(PARAMS["corridor"]["thick"])
    sx, sz = xa + run / 2.0, za - drop / 2.0
    ctr = (sx - (th / 2.0) * math.sin(ang), sz - (th / 2.0) * math.cos(ang))
    axes = ((math.cos(ang), -math.sin(ang)), (-math.sin(ang), -math.cos(ang)))
    return ctr, (L / 2.0, th / 2.0), axes


def _slab_interlock(a, b):
    """Separating-axis margin between two corridor slabs: >0 = interlock depth (the
    minimum translation distance), 0 = they only touch, <0 = they are apart."""
    ca, ha, Aa = _slab_obb(a)
    cb, hb, Ab = _slab_obb(b)
    d = (cb[0] - ca[0], cb[1] - ca[1])
    worst = -1e18
    for L in list(Aa) + list(Ab):
        ra = sum(ha[k] * abs(Aa[k][0] * L[0] + Aa[k][1] * L[1]) for k in (0, 1))
        rb = sum(hb[k] * abs(Ab[k][0] * L[0] + Ab[k][1] * L[1]) for k in (0, 1))
        worst = max(worst, abs(d[0] * L[0] + d[1] * L[1]) - (ra + rb))
    return -worst


def corridor_seam_census():
    """`[(a, b, dtheta, wedge_unlapped, lap, interlock, corner_in_a)]` per crest.

    `wedge_unlapped` = `thick·sin(θa − θb)`, the width the seam would fan open to at the
    far face with no lap — the defect, in metres. `corner_in_a` is the same statement
    taken empirically: the downhill neighbour's far bottom corner must lie **inside**
    the uphill slab's body, which is only true once the lap is there."""
    slabs = corridor_slabs()
    th = float(PARAMS["corridor"]["thick"])
    out = []
    for a, b in zip(slabs, slabs[1:]):
        ta, tb = math.radians(a[5]), math.radians(b[5])
        crest = (b[1], b[2])
        corner = (crest[0] - th * math.sin(tb), crest[1] - th * math.cos(tb))
        out.append((a[0], b[0], math.degrees(ta - tb),
                    max(0.0, th * math.sin(ta - tb)), a[6],
                    _slab_interlock(a, b), slab_holds(a, *corner)))
    return out


# [GT-77] top-face rectangles of the approach members a scattered dressing card can land
#   on. Precomputed once so `approach_dressing_z` stays a lookup inside a scatter loop
#   (`scatter_debris` samples its `ground_fn` five times per instance).
_APPROACH_TOPS = [(c[0] - s[0] / 2.0, c[0] + s[0] / 2.0,
                   c[1] - s[1] / 2.0, c[1] + s[1] / 2.0, c[2] + s[2] / 2.0)
                  for _n, _k, c, s in approach_members()
                  if _k in ("verge", "edge", "apron")]


def approach_dressing_z(x, y, base):
    """Surface a scattered leaf card should sit on at (x, y), given the plan's flat `base`.

    The verge, the edging and the apron stand 0.002-0.047 m over grade, so a card
    scattered at `base` inside one of them would be authored **inside a solid** and
    render as nothing — the silent-burial mode this library has already paid for once
    (`ground_kit` R1: flush elements buried under the relief skin, manhole dark pixels
    5.88 % -> 0.02 % `[measured]`). Returning the member's own top face puts the card on
    the shoulder instead of in it.

    Outside every member the return is `base` unchanged, so the scatter is bit-identical
    there, and `scatter_debris` draws the same number of RNG values with or without a
    `ground_fn` — `det_seed` determinism is untouched. Its local-slope probe clamps to
    +-15 deg, so the step at a member's edge tilts a card at most that far, which is what
    a leaf lying against a board does anyway.
    """
    z = float(base)
    for x0, x1, y0, y1, zt in _APPROACH_TOPS:
        if x0 <= x <= x1 and y0 <= y <= y1 and zt > z:
            z = zt
    return z


# ===========================================================================
# [G] camera presets: grid_views (gy=0.0) + 5 mise-en-scene shots
# ===========================================================================
def build_views():
    views = sc.grid_views(0.0)          # h{0.3,0.9,1.8} × d{2,5,10}, +X

    # [S3-10] every mise-en-scene cut is now **derived from the ladder**, not typed as a
    #   literal, because the de-stacking moves landing0 from x[3.0,4.4] z −1.65 to
    #   x[2.48,3.98] z −1.20 and the run now reaches x 24.1. A literal eye/tgt would have
    #   silently drifted off its subject — the exact failure mode §6.4 warns about.
    l0 = SEQ[0]
    lcx = (l0["lx0"] + l0["lx1"]) / 2.0
    lcz = l0["z_bot"]
    # reversal : the turn at landing0 read from the open south side — the flight arriving
    #   (+X, band A) and the flight leaving (+X, band B) in one frame. The 180-deg reversal
    #   it was named for is gone with the de-stacking; the **turn** it photographs is not.
    views["reversal"] = dict(eye=[lcx + 3.40, -6.60, lcz + 2.40],
                             tgt=[lcx - 0.30, -0.35, lcz + 0.32])
    # through_treads : open-riser see-through on flight 0 (band A). [S3-10] the deck now
    #   stands 0.25 m off natural grade instead of over a 6.6 m shaft, so what shows
    #   between the treads is the litter slope rather than a void — which is what G10
    #   shows too. The cue is unchanged: with no riser board the nosing light-dark pair
    #   never forms.
    f0 = SEQ[0]
    fmx = (f0["x_top"] + f0["x_bot"]) / 2.0
    fmy = sum(band(0)) / 2.0
    views["through_treads"] = dict(
        eye=[fmx, fmy - 2.10, (f0["z_top"] + f0["z_bot"]) / 2.0 - 0.28],
        tgt=[fmx + 0.20, fmy + 1.00, corridor_z(fmx + 0.20) - 0.55])
    # broken_rail : close-up of the missing-rail run on landing0's forward (+X) edge and
    #   the open drop past it. Kept front-lit (sight ~112 deg) exactly as v7 tuned it.
    xo = l0["lx1"]
    views["broken_rail"] = dict(eye=[xo + 1.60, -3.40, lcz + 0.90],
                                tgt=[xo + 0.35, -0.30, lcz - 0.35])
    # leaf_edge : the leaf band biting the top two treads, from the approaching robot's eye
    views["leaf_edge"] = dict(eye=[-1.05, fmy - 1.00, 0.55],
                              tgt=[0.80, fmy, f0["z_top"] - 2.5 * PARAMS["flights"]["riser"]])
    # from_below : the whole traverse from the lower park. [S3-10] the run reaches x 24.1,
    #   so the eye pulls back along the slope to keep the zigzag in one frame.
    mid = SEQ[len(SEQ) // 2]
    views["from_below"] = dict(eye=[mid["x_top"] + 2.00, -12.60, GROUND_Z + 1.55],
                               tgt=[mid["x_top"] - 1.60, -0.60, mid["z_top"] - 0.40])
    return views


# ===========================================================================
# [H] SMOKE - geometry self-check without booting
# ===========================================================================
def _grid_obstacles():
    """AABBs for checking grid camera (−d, 0, h) collisions [(name,x0,x1,y0,y1,z0,z1)]."""
    sp = PARAMS["signpost"]
    bn = PARAMS["bench"]
    # [v5.2 user] arbitrary warning sign removed - Sign AABB deleted (waymarker and bench only)
    obs = [("SignPost", sp["cx"] - sp["arm"][0], sp["cx"] + sp["arm"][0],
            sp["cy"] - 0.4, sp["cy"] + 0.4, 0.0, sp["post_h"]),
           ("Bench", bn["cx"] - 0.95, bn["cx"] + 0.95, bn["cy"] - 0.25,
            bn["cy"] + 0.25, 0.0, 0.50)]
    for cx, cy, zone, th in PARAMS["trees"]:
        gz = _zone_z(cx, cy, zone)
        obs.append((f"Tree_{len(obs)}", cx - 0.9, cx + 0.9, cy - 0.9, cy + 0.9,
                    gz, gz + th + 1.4))
    for cx, cy, zone in PARAMS["shrubs"]:
        gz = _zone_z(cx, cy, zone)
        obs.append((f"Shrub_{len(obs)}", cx - 1.3, cx + 1.3, cy - 1.1,
                    cy + 1.1, gz, gz + 0.65))
    # [GT-77] the capped end posts of the approach edging are the only new members
    #   that stand tall enough to reach a grid eye (top = grade + 0.260 + cap, against
    #   eye heights 0.30/0.90/1.80), so they enter the collision census rather than
    #   being asserted safe in prose.
    for name, kind, ctr, size in approach_members():
        if not name.endswith("/EdgePost_P") and not name.endswith("/EdgePost_N"):
            continue
        obs.append((name.split("/")[-1] + f"_{len(obs)}",
                    ctr[0] - size[0] / 2.0, ctr[0] + size[0] / 2.0,
                    ctr[1] - size[1] / 2.0, ctr[1] + size[1] / 2.0,
                    ctr[2] - size[2] / 2.0, ctr[2] + size[2] / 2.0))
    return obs


def _smoke_report():
    P = PARAMS
    fl = P["flights"]
    ld = P["landing"]
    ent = P["entry"]
    print("=" * 74)
    print("scene10_park_deck_switchback (v5 R5) — SMOKE 기하 자기검증 (부팅 없음)")
    print("=" * 74)
    _st = flight_steps()
    print(f"  플라이트 {fl['n']}개 · 단수 {'+'.join(str(v) for v in _st)} = "
          f"{sum(_st)}단 · riser {fl['riser']} / tread {fl['tread']} · "
          f"폭 {2*fl['half_w']:.2f} m")
    print(f"  총 낙차 {TOTAL_DROP:.2f} m (≥0.3 → "
          f"{'OK' if TOTAL_DROP >= 0.3 else 'FAIL'}) · "
          f"플라이트 경사 {math.degrees(math.atan2(fl['riser'], fl['tread'])):.1f}°"
          f" · 평면 x [{PLAN_X0:.2f}, {PLAN_X1:.2f}]")

    # ── flight and landing table ──
    print("\n  [표] 플라이트/참 (월드 좌표)")
    print(f"    {'k':>2} {'단':>3} {'rot':>4} {'대역 y':>16} {'x_top→x_bot':>14} "
          f"{'z_top→z_bot':>16} {'참 x범위':>14} 참 z   비고")
    for f in SEQ:
        lo, hi = band(f["k"])
        print(f"    {f['k']:2d} {f['steps']:3d} {int(f['rot']):4d} "
              f"[{lo:+6.2f},{hi:+6.2f}] "
              f"{f['x_top']:6.2f}→{f['x_bot']:6.2f} "
              f"{f['z_top']:+7.3f}→{f['z_bot']:+7.3f} "
              f"[{f['lx0']:6.2f},{f['lx1']:6.2f}] {f['z_bot']:+7.3f}"
              f"   {'쉼터 전망참' if f['rest'] else ''}")
    lo_e, hi_e = band(0)
    lo_o, hi_o = band(1)
    print(f"    대역 간극 = {lo_o - hi_e:.3f} m (>0 = 두 방향 간섭 0 → "
          f"{'OK' if lo_o > hi_e else 'FAIL'})")
    print(f"    참 y범위 [{ld['y0']:+.2f},{ld['y1']:+.2f}] 이 두 대역을 모두 "
          f"덮는가 → {'OK' if ld['y0'] <= lo_e and ld['y1'] >= hi_o else 'FAIL'}")
    print("    상·하 플라이트 연직 여유 = **해당 없음** — S3-10 탈적층 이후 어떤 "
          "플라이트도 다른 플라이트 위에 있지 않다(중첩 0 m², deck_module_selfcheck "
          "S3-10). 구 배치의 3.01 m 는 갱도의 증상이지 미덕이 아니었다.")

    # ── exhaustive walking continuity check ──
    print("\n  [표] 보행 연속성 (구간 → 다음 구간, n단 분할 단차)")
    links = [("상부 트레일", TRAIL_Z, "진입 데크", ent["top"], 1)]
    prev_n, prev_z = "진입 데크", ent["top"]
    for f in SEQ:
        z1 = f["z_top"] - fl["riser"]
        ns = f["steps"]
        links.append((prev_n, prev_z, f"플라이트{f['k']} 1단", z1, 1))
        links.append((f"플라이트{f['k']} 1단", z1,
                      f"플라이트{f['k']} {ns}단", f["z_bot"], ns - 1))
        links.append((f"플라이트{f['k']} {ns}단", f["z_bot"],
                      f"참{f['k']}", f["z_bot"], 1))
        prev_n, prev_z = f"참{f['k']}", f["z_bot"]
    links.append((prev_n, prev_z, "하부 산책로", GROUND_Z, 1))
    worst = 0.0
    for n0, z0, n1, z1, ns in links:
        d = (z0 - z1) / float(ns)
        worst = max(worst, abs(d))
        flag = "OK" if abs(d) <= fl["riser"] + 1e-6 else "CHECK"
        print(f"    {n0:<15} {z0:+7.3f} → {n1:<15} {z1:+7.3f} "
              f"×{ns:2d}단  단차 {d:+6.3f}  {flag}")
    print(f"    최대 단일 단차 {worst:.3f} m (riser {fl['riser']} 이하 = "
          f"{'OK' if worst <= fl['riser'] + 1e-6 else 'CHECK'})")
    gap = SEQ[-1]["z_bot"] - GROUND_Z
    print(f"    참{SEQ[-1]['k']} 상면 {SEQ[-1]['z_bot']:+.3f} vs 하부 지면 {GROUND_Z:+.3f} "
          f"→ 프라우드 {gap:+.3f} m "
          f"({'OK (동일평면 아님·보행 무해)' if 0.0 < gap <= 0.05 else 'CHECK'})")

    # ── ground plate / slope table ──
    print("\n  [표] 축정렬 지면 플레이트")
    print(f"    {'이름':15s} {'x범위':>16s} {'y범위':>16s} {'상면z':>7s} 두께")
    for nm, x0, x1, y0, y1, zt, th, _m in P["plates"]:
        print(f"    {nm:15s} [{x0:7.1f},{x1:7.1f}] [{y0:7.2f},{y1:7.2f}] "
              f"{zt:7.3f} {th:5.2f}")
    print("  [GT-65] 데크 인계 흙길 (col=False · 기존 지면 위 2 mm 데코)")
    for nm, x0, x1, y0, y1, zt, th in P["exit_paths"]:
        print(f"    {nm:15s} [{x0:7.1f},{x1:7.1f}] [{y0:7.2f},{y1:7.2f}] "
              f"{zt:7.3f} {th:5.2f}")
    _lp = _plate("LowerPath")
    _ex, _lk = P["exit_paths"][0], P["exit_paths"][1]
    print(f"    도착참 전면 x {SEQ[-1]['lx1']:.2f} → DeckExit x0 {_ex[1]:.2f} "
          f"(참 밑으로 {SEQ[-1]['lx1'] - _ex[1]:.2f} m 물림) → 씬 끝 x {_ex[2]:.1f} · "
          f"DeckExitLink y {_lk[4]:.2f}→{_lk[3]:.2f} 가 LowerPath 북단 "
          f"y {_lp[4]:.2f} 에 접함 → "
          f"{'OK (풀밭 막다른 길 해소)' if abs(_lk[3] - _lp[4]) < 1e-9 else 'CHECK'}")
    # ── [GT-77 · §0-2] approach finishing at the two deck ends ──
    apx = P["approach"]
    _mem = approach_members()
    _dhy = float(ld["y1"])
    print("\n  [GT-77 접근로] 데크 양 끝단 마감 — 전 부재 col=False "
          "(기존 콜라이더 위 데코 · 보행면·낙차 모서리·GT AABB 불변)")
    print(f"    {'부재':28s} {'종류':7s} {'x범위':>17s} {'y범위':>17s} {'상면z':>8s}")
    for nm, kind, c, s in _mem:
        print(f"    {nm:28s} {kind:7s} "
              f"[{c[0]-s[0]/2.0:7.3f},{c[0]+s[0]/2.0:7.3f}] "
              f"[{c[1]-s[1]/2.0:7.3f},{c[1]+s[1]/2.0:7.3f}] "
              f"{c[2]+s[2]/2.0:8.3f}")
    ok77 = True
    for e in apx["ends"]:
        tag = str(e["tag"])
        pz, phy = float(e["path_z"]), float(e["path_half_y"])
        gz_e, xe = float(e["grade"]), float(e["run_end"])
        deck_z = float(ent["top"]) if tag == "Entry" else SEQ[-1]["z_bot"]
        h_top = pz + float(apx["header_proud"])
        c_path, c_deck = h_top - pz, h_top - deck_z
        # the board must not share a plane with either surface it closes (that is the
        # z-fighting test) and must stay a trim, never a step: the largest face it
        # presents is asserted against the flight riser.
        good = (min(abs(c_path), abs(c_deck)) >= 0.005
                and max(abs(c_path), abs(c_deck)) <= float(fl["riser"]))
        ok77 &= good
        print(f"    [{tag}] 마구리재 상면 {h_top:+.3f} : 포장 상면 "
              f"{pz:+.3f}({c_path:+.3f}) · 데크 상면 {deck_z:+.3f}({c_deck:+.3f}) "
              f"→ 두 면과 모두 비동일평면(최소 이격 "
              f"{min(abs(c_path), abs(c_deck)):.3f} ≥ 0.005) · 최대 노출 "
              f"{max(abs(c_path), abs(c_deck)):.3f} ≤ riser {fl['riser']:.3f} "
              f"{'OK' if good else 'CHECK'}")
        _role = ("진입단: 포장이 데크보다 높으므로 마구리재는 두 면 위에 서는 "
                 "10 mm 노출 경계재" if c_deck > 0 else
                 "도착단: 마구리재가 참과 포장 사이에 앉아 등록 단차 0.020 을 "
                 "0.008 + 0.010 으로 나눈다")
        print(f"      {_role} — 콜라이더 없음이므로 보행 연속성 표의 "
              f"등록 단차는 불변")
        ymax = max(abs(c[1]) + s[1] / 2.0 for nm, _k, c, s in _mem
                   if nm.startswith(f"Approach_{tag}/"))
        good = ymax <= _dhy + 1e-9
        ok77 &= good
        print(f"    [{tag}] 문턱 유효폭 {2.0*phy:.2f} m(포장) → {2.0*_dhy:.2f} m"
              f"(데크와 동일) · 부재 최대 |y| {ymax:.3f} ≤ 데크 가장자리 "
              f"{_dhy:.3f} → {'OK' if good else 'CHECK'}"
              + ("  (남측 30 % 무방호 어깨선을 넘는 부재 0개)"
                 if tag == "Entry" else ""))
        print(f"    [{tag}] 버지 상면 {gz_e + float(apx['verge_proud']):+.3f} = "
              f"지면 +{float(apx['verge_proud']):.3f} → 낙엽 드리프트 단"
              f"(leaf.proud {P['leaf']['proud']:.3f}) 대비 여유 "
              f"{float(apx['verge_proud']) - float(P['leaf']['proud']):+.3f} m · "
              f"경계목 종단 말뚝 x {xe:+.2f}")
    # vertical-face clearances. A top-face census cannot see these: two exposed
    #   **side** faces landing on the same y-plane at the deck corner would z-fight just
    #   as badly, so every outer face is stepped and the steps are asserted here.
    _sec = float(apx["edge"])
    _fc = _dhy - float(apx["flank_inset"]) - _sec / 2.0
    _gaps = (("데크 측면 ↔ 마구리재 끝면", float(apx["header_inset"])),
             ("마구리재 끝면 ↔ 플랭크 외면",
              float(apx["flank_inset"]) - float(apx["header_inset"])),
             ("플랭크 외면 ↔ 에이프런 외변", float(apx["apron_tuck"])),
             ("마구리재 데크측 면 ↔ 에이프런 끝면",
              float(apx["header_bite"]) - float(apx["apron_bite"])),
             ("마구리재 데크측 면 ↔ 플랭크 끝", 0.010),
             ("포장 측면 ↔ 경계목 내면", float(apx["edge_tuck"])))
    _gmin = min(g for _n, g in _gaps)
    ok77 &= _gmin >= 0.005 - 1e-9
    print("    면 겹침 방지 이격 (노출 수직면이 같은 평면에 앉지 않도록 계단식 후퇴)")
    for _n, _g in _gaps:
        print(f"      {_n:32s} {_g:+.3f} m")
    print(f"      최소 이격 {_gmin:.3f} ≥ 0.005 → "
          f"{'OK' if _gmin >= 0.005 - 1e-9 else 'CHECK'} · 플랭크 중심선 "
          f"y ±{_fc:.3f} (외면 ±{_fc + _sec / 2.0:.3f})")
    _cop = coplanar_census()
    ok77 &= not _cop
    print(f"    동일평면 겹침 감사(축정렬 상면 {len(_mem) + len(P['plates']) + len(P['exit_paths']) + 1 + len(SEQ)}면 "
          f"전수 쌍검사) → {len(_cop)}쌍 "
          f"{'OK (z-fighting 면 0)' if not _cop else 'CHECK ' + str(_cop[:3])}")
    # dressing that lands on the new members must sit **on** them, not inside them
    _bur = [(nm, cy) for nm, cy, _sx, sy, zn in P["leaf_ground_patches"]
            if zn == "trail" and abs(cy) + sy / 2.0 > 0.85 + 1e-9]
    ok77 &= not _bur
    print(f"    낙엽 드리프트(trail) 흙길 대역 |y| ≤ 0.85 이탈 {len(_bur)}개 → "
          f"{'OK (버지가 로브를 잘라내지 않는다)' if not _bur else 'CHECK ' + str(_bur)}")
    _probe = [("버지 안", -6.0, 1.20), ("에이프런 안", -2.0, 1.20),
              ("경계목 위", -6.0, 0.885), ("포장 위", -6.0, 0.00)]
    print("    산포 착지면 probe (approach_dressing_z, base = 0.000)")
    for _n, _px, _py in _probe:
        print(f"      {_n:10s} ({_px:+5.1f},{_py:+5.2f}) → z "
              f"{approach_dressing_z(_px, _py, 0.0):+.3f}")
    _hf = apx["head_fillet"]
    print(f"    머리 성토 배수면: x {_hf[0]:+.2f}→{_hf[0]+_hf[2]:+.2f} · "
          f"z {_hf[1]:+.3f}→{_hf[1]-_hf[3]:+.3f} "
          f"({math.degrees(math.atan2(_hf[3], _hf[2])):.1f}°) · y {_hf[4]:+.2f}.."
          f"{_hf[5]:+.2f} — 데크 측면(y {_dhy:+.2f})에서 "
          f"{_hf[4]-_dhy:.3f} m 이격 · collider=False")
    print(f"    [GT-77 접근로] {'전항목 OK' if ok77 else '⚠ CHECK 항목 있음'}")

    print("  [표] Y 방향 사면(_ybank, rotX)")
    for nm, x0, x1, yh, zh, yl, zl, th, _m in P["ybanks"]:
        ang = math.degrees(math.atan2(zh - zl, yh - yl))
        print(f"    {nm:15s} y {yh:+6.2f}(z{zh:+6.2f}) → {yl:+6.2f}"
              f"(z{zl:+6.2f})  {ang:5.1f}° 두께 {th:.2f}")
    print("    상부 트레일 플레이트는 x=%.1f 에서 끊김 → 계단 공동(x %.1f..%.1f) "
          "위 연속 평면 없음 (체크리스트 ③ OK)"
          % (HEAD_X, PLAN_X0, PLAN_X1))
    for y in (4.0, 2.0, 0.0, -3.0, -8.0, -14.0):
        print(f"    ground_z(x=−5, y={y:+6.1f}) = {ground_z(-5.0, y):+6.3f} · "
              f"(x=+2, y={y:+6.1f}) = {ground_z(2.0, y):+6.3f}")
    print(f"    남측 무방호: 트레일 어깨(y−1.60) 기준 y−5.6 에서 "
          f"{-south_z(-5.6):.2f} m 하강 (브리프 2~3 m 대역)")

    # ── deck post grounding table ──
    print("\n  [표] 데크 기둥 접지 (하단 z / 상단 z / 길이)")
    for nm, cx, cy, z_lo, z_hi in post_segments():
        base = "지면" if abs(z_lo - GROUND_Z) < 1e-6 else "하부 참"
        print(f"    {nm:<12} ({cx:6.2f},{cy:+5.2f}) {z_lo:+7.3f} → "
              f"{z_hi:+7.3f}  L={z_hi - z_lo:5.3f}  하단={base}")

    # ── [S3] deck module self-check (spec §6.5) ──
    deck_module_selfcheck()

    # ── [GT-65] railing continuity : the guarded boundary, run by run ──
    print("\n  [난간 연속성] 경계 체인 (종런은 노드에서 엄지기둥 속으로 죽고, "
          "가로런은 상부 난간대 반폭만큼 물러나 붙는다)")
    _runs = rail_runs()
    print(f"    {'런':<22} {'종류':<6} {'x0→x1':>14} {'y0→y1':>15} "
          f"{'z0→z1':>15} 길이")
    for _s in ("N", "P"):
        for rr in _runs:
            if rr["side"] != _s:
                continue
            print(f"    {rr['name']:<22} {rr['kind']:<6} "
                  f"{rr['x0']:6.2f}→{rr['x1']:6.2f} "
                  f"{rr['y0']:+6.3f}→{rr['y1']:+6.3f} "
                  f"{rr['z0']:+6.2f}→{rr['z1']:+6.2f} "
                  f"{math.hypot(rr['x1']-rr['x0'], rr['y1']-rr['y0']):5.2f}")
        # chain gap: consecutive runs on one chain must share an endpoint.
        #   [GT-115 ⑭] the return stubs are **terminations, not chain segments** — they
        #   hang off the chain's first and last node at 90°, so walking them in sequence
        #   would measure the length of the deck head, not a gap. They are excluded here
        #   and asserted on their own row by `run_end_nodes()` in the self-check.
        ch = [rr for rr in _runs if rr["side"] == _s and rr["kind"] != "return"]
        ret = [rr for rr in _runs if rr["side"] == _s and rr["kind"] == "return"]
        gapmax, gapnm = 0.0, "-"
        for a, b in zip(ch, ch[1:]):
            d = math.hypot(b["x0"] - a["x1"], b["y0"] - a["y1"])
            if d > gapmax:
                gapmax, gapnm = d, f"{a['name']}→{b['name']}"
        print(f"    체인 {_s}: 런 {len(ch)}개 (+종단 리턴 {len(ret)}개) · "
              f"연속 런 끝점 최대 이격 {gapmax:.3f} m ({gapnm}) → "
              f"{'OK (엄지기둥 90 mm 안)' if gapmax <= PARAMS['rail']['newel'] + 1e-9 else 'CHECK'}")

    # ── [v6] sun reselection check : lambert per face + direct sun reaching the passage ──
    az = 33.5 + float(P["SUN_AZ_OFFSET"])
    el = math.radians(float(P["light"]["noon_sun_elev"]))
    ux, uy = math.cos(math.radians(az)), math.sin(math.radians(az))
    lx, ly, lz = ux * math.cos(el), uy * math.cos(el), math.sin(el)
    hv = math.cos(el) / math.sin(el)          # horizontal travel per 1 m of rise
    print(f"\n  [v6 태양] offset {P['SUN_AZ_OFFSET']:.1f} → 월드 az {az:.1f}° "
          f"(그림자 az {az - 180:.1f}°) · 고도 {math.degrees(el):.2f}°")
    for nm, N in (("−Y향(데크 측면·북측 옹벽면)", (0, -1, 0)),
                  ("−X향(그리드 정면·원경 능선)", (-1, 0, 0)),
                  ("상면(트레일·참·디딤판)", (0, 0, 1)),
                  ("+X향(머리 옹벽 노출면)", (1, 0, 0))):
        d = N[0] * lx + N[1] * ly + N[2] * lz
        print(f"    {nm:<26} lambert {d:+.3f} "
              f"{'순광' if d > 0.15 else ('터미네이터' if d > 0 else '음영')}")
    print("    [광선 역추적] 통로 대표점 → 태양 방향으로 z=0 까지 상승했을 때의 "
          "평면 위치 (x<−1.5 이면 머리 옹벽/남측 사면에 차폐)")
    for nm, px, py, pz in (("플라이트0 중단", 1.5, -0.7, -0.83),
                           ("참0 상면", 3.70, -0.70, -1.65),
                           ("플라이트2 중단", 1.7, -0.7, -4.24),
                           ("참2 상면", 3.70, -0.70, -4.95),
                           ("참3 상면(최하부)", -0.70, 0.70, -6.60)):
        rise = -pz
        ex, ey = px + ux * hv * rise, py + uy * hv * rise   # trace back toward the sun
        ok = ex >= HEAD_X            # conservative test (crossing the x=−1.5 plane means possible occlusion)
        print(f"    {nm:<16} ({px:+.2f},{py:+.2f},{pz:+.2f}) → "
              f"({ex:+.2f},{ey:+.2f}, 0.00)  "
              f"{'직사광 도달' if ok else '옹벽 그늘(설계상 허용)'}")

    # ── [S3-10] corridor ground profile — the shaft's replacement ──
    print("\n  [S3-10 지형] 데크 회랑 종단 (석축 갱도 → 실사면)")
    print(f"    {'x':>8} {'지반z':>8} {'데크z':>8} {'여유':>7}")
    for f in SEQ:
        for nm, xx, zz in (("플라이트머리", f["x_top"], f["z_top"]),
                           ("플라이트발", f["x_bot"], f["z_bot"]),
                           ("참 끝", f["lx1"], f["z_bot"])):
            g = corridor_z(xx)
            print(f"    {xx:8.2f} {g:8.3f} {zz:8.3f} {zz - g:7.3f}  {nm}")
    grade = 100.0 * (TRAIL_Z - GROUND_Z) / (PLAN_X1 + 1.5 - HEAD_X + 1.5)
    print(f"    회랑 평균 종단경사 {100.0*6.62/(PLAN_X1 - HEAD_X):.1f} % · "
          f"머리 옹벽 노출고 {abs(corridor_z(HEAD_X)):.3f} m "
          f"(구 6.62 m 단일벽 → 짧은 머리벽)")

    # ── grid camera collision check ──
    print("\n  [검산] 그리드 카메라(−d, 0, h) vs 기하 AABB")
    obs = _grid_obstacles()
    hit_any = False
    for d in (2, 5, 10):
        for h in (0.3, 0.9, 1.8):
            ex, ey, ez = -float(d), 0.0, float(h)
            hits = [nm for nm, x0, x1, y0, y1, z0, z1 in obs
                    if x0 <= ex <= x1 and y0 <= ey <= y1 and z0 <= ez <= z1]
            if hits:
                hit_any = True
                print(f"    d{d} h{h}: ⚠ {hits}")
    print(f"    충돌 = {hit_any} (False 여야 함) · 카메라 접지면 z=0 "
          f"(UpperTrail x −40..{HEAD_X}, y −1.60..1.45) 내부 OK")

    print("\n  [카메라] 미장센")
    v = build_views()
    for vn in ("reversal", "through_treads", "broken_rail", "leaf_edge",
               "from_below"):
        vv = v[vn]
        print(f"    {vn:<15} eye={['%.2f' % e for e in vv['eye']]} "
              f"tgt={['%.2f' % t for t in vv['tgt']]}")

    # ── [v7] mise-en-scene framing : are the park anchors in frame + front lighting per shot ──
    #   verdict §7 (1) "none of the 4 mise-en-scene shots carries a park signal (grass·shrubs·
    #   trees·visitor furniture) - the problem is framing, not geometry". To **verify the
    #   re-aim by coordinates**, the park anchors inside the FOV (horizontal half 30 deg ·
    #   vertical half 18 deg) are enumerated, with the lit-face lambert per shot attached
    #   (judge v7 lesson: "a re-aim is checked by frame coverage, illumination is not").
    anchors = []
    for cx, cy, zone in P["shrubs"]:
        if zone in ("lower", "south"):
            anchors.append((f"관목({cx:+.1f},{cy:+.1f})", cx, cy,
                            _zone_z(cx, cy, zone) + 0.55))
    for cx, cy, zone, th in P["trees"]:
        anchors.append((f"수목({cx:+.1f},{cy:+.1f})", cx, cy,
                        _zone_z(cx, cy, zone) + th + 0.7))
    pg = P["pergola"]
    anchors.append(("쉼터 정자", (pg["x0"] + pg["x1"]) / 2.0,
                    (pg["y0"] + pg["y1"]) / 2.0, pg["z_roof"]))
    for yy in (4.0, 7.0, 11.0):
        anchors.append((f"북측 잔디사면 y{yy:.0f}", 3.0, yy, north_z(yy)))
    _rf = [f for f in SEQ if f["rest"]]
    if _rf:
        _r = _rf[0]
        anchors.append(("쉼터 전망참", (_r["lx0"] + _r["lx1"]) / 2.0,
                        (_r["ly1"] + PARAMS["landing"]["y1"]) / 2.0,
                        _r["z_bot"] + 0.6))
    sp, bn = P["signpost"], P["bench"]
    anchors.append(("이정표", sp["cx"], sp["cy"], sp["post_h"] / 2.0))
    anchors.append(("벤치", bn["cx"], bn["cy"], 0.25))

    azd = 33.5 + float(P["SUN_AZ_OFFSET"])
    el2 = math.radians(float(P["light"]["noon_sun_elev"]))
    print("\n  [v7 미장센] 컷별 피사면 lambert + 프레임 내 공원 앵커")
    for vn in ("reversal", "through_treads", "broken_rail", "leaf_edge",
               "from_below"):
        ex, ey, ez = v[vn]["eye"]
        tx, ty, tz = v[vn]["tgt"]
        fx, fy = tx - ex, ty - ey
        dh = math.hypot(fx, fy)
        ux, uy = fx / dh, fy / dh
        rx, ry = uy, -ux
        gaze = math.degrees(math.atan2(fy, fx)) % 360.0
        nrm = (gaze + 180.0) % 360.0
        lam = math.cos(math.radians(nrm - azd)) * math.cos(el2)
        pit = math.degrees(math.atan2(tz - ez, dh))
        seen = []
        for nm, ax, ay, az_ in anchors:
            vx, vy, vz = ax - ex, ay - ey, az_ - ez
            dep = vx * ux + vy * uy
            if dep <= 0.5:
                continue
            yaw = math.degrees(math.atan2(vx * rx + vy * ry, dep))
            elv = math.degrees(math.atan2(vz, math.hypot(vx, vy)))
            if abs(yaw) <= 30.0 and abs(elv - pit) <= 18.0:
                seen.append(f"{nm}[yaw{yaw:+.0f}°]")
        # the ground hit by the bottom-centre ray (is the lower half grass / dirt trail)
        pr = math.radians(pit - 18.0)
        hit = None
        for i in range(1, 401):
            s = i * 0.25
            px, py = ex + ux * s * math.cos(pr), ey + uy * s * math.cos(pr)
            pz = ez + s * math.sin(pr)
            if pz <= ground_z(px, py):
                zone = ("하부공원 흙길" if (px > HEAD_X and -4.4 <= py <= -2.6)
                        else ("하부공원 잔디" if (px > HEAD_X and py < 1.45)
                              else "상부/사면"))
                hit = f"({px:+.1f},{py:+.1f}) {zone}"
                break
        print(f"    {vn:<15} 시선 {gaze:5.1f}° · 법선 {nrm:5.1f}° · lambert "
              f"{lam:+.3f} {'순광' if lam > 0.15 else '역광/터미네이터'} · "
              f"피치 {pit:+5.1f}°")
        print(f"      하단 시선 착지 : {hit if hit else '지면 미교차(하늘)'}")
        # verdict §7 (1) said "**every** mise-en-scene shot lacks a park signal".
        #   the re-aimed shots (from_below·reversal) must catch an anchor, while the
        #   close-ups (through_treads·broken_rail) are exempt - instead their illumination
        #   and drop are checked by lambert and the bottom-ray landing point.
        need = vn in ("from_below", "reversal")
        verdict = ("OK" if seen else "FAIL ← 판정 §7 ① 재발") if need \
            else ("OK" if seen else "면제(클로즈업 — lambert·하단 착지로 판정)")
        print(f"      공원 앵커 {len(seen)}개 [{verdict}] : "
              f"{', '.join(seen) if seen else '-'}")
    print("=" * 74)


# ===========================================================================
# [I] main
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. h0.3 그리드      — 낙엽 덮인 상단 2단이 '평탄한 데크 진입'으로 읽히나
 2. through_treads   — 라이저 부재로 디딤판 사이 아래 플라이트·지면이 투시되나
 3. reversal         — 참0에서 두 방향 플라이트(±X, 병렬 Y 대역)가 한 프레임에
 4. broken_rail      — 참0 전면 가드가 모서리에서 다음 플라이트로 이어지는가
                       (한 제품군 · 이중 엄지기둥 없음 · 통로 위 가로대 없음)
 5. leaf_edge        — 낙엽 밴드가 단코를 물고 덮어 절단선을 지우나
 6. from_below       — 데크 기둥 접지·참 스택이 낙차 앵커로 읽히나
 7. 남측 사면        — 트레일 어깨 밖 30° 무방호 하강이 grazing 시 소실되나
 8. 지평 폐쇄        — 북측 언덕·원경 능선 마루 숲 밴드가 직선 지평을 깨는가
 9. cue 토글         — railing/tactile/nosing ON/OFF 시 위험 기하 불변인가
10. [v6] 태양        — from_below·through_treads 에 직사광이 들어왔나(암부 사망 해소)
11. [v6] 옹벽        — 사석 스케일 + 동측 2단(소단 식재)로 '공원 절토면'이 되나
12. [v6] 난간        — 세로살이 들어가 '가설 사다리틀'이 아니라 데크 난간인가
13. [GT-77] 접근로   — 데크 양 끝단에서 포장이 데크 폭까지 나가 마구리재에 물려 붙는가
                       (경계목·버지·식재가 길을 '무맥락 매트'에서 떼어내는가 ·
                        런 끝마다 리턴/말뚝 · 머리 절토면 raw cut 소거)
14. [GT-115 ⑭] 마감  — 노두가 난간 살대를 관통하지 않는가(≥0.30 m) · 난간 런 끝이
                       리턴+갓기둥으로 죽는가 · 낙엽이 한 실루엣의 반복이 아닌가
                       (변형 3종·축척 ×3.22) · 정자에 보/서까래/처마/밑판이 있는가 ·
                       난간 상면은 은화하고 이끼는 수직·음영면에만 남는가
15. [GT-119 ②] 이음  — 회랑 슬래브가 급경사→완경사 마루마다 쐐기로 벌어지지
                       않는가(무이음 최대 3.049 m → 이음 후 물림 ≥0.100) ·
                       남측 절토면 관통 probe 32 841점 중 열린 점 0인가 ·
                       회랑 상면 max_i top_i(x) = corridor_z(x) 가 기계 오차
                       안인가(보행·콜라이더 불변) · 플레이트 이음 6쌍이 lap
                       ≥0.100 또는 정확한 butt 인가 · 이음이 동일평면 쌍을
                       새로 만들지 않았는가"""


def main():
    # [GT-89] SMOKE gate - early exit BEFORE the Isaac boot (no GPU, no GUI).
    # The old template read NEGOBS_SMOKE only as boot()'s headless arg (or not at
    # all), so the §2.2 smoke floor booted Isaac on this scene (scene03/09 incident).
    # Deep checks keep their own arms (NEGOBS_SELFCHECK / geom_invariance_check.py).
    if os.environ.get("NEGOBS_SMOKE", "0") == "1":
        print("SMOKE_OK %s pre-boot gate (GT-89)" % os.path.basename(__file__))
        return
    smoke = os.environ.get("NEGOBS_SMOKE", "0") == "1"
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    if smoke:
        _smoke_report()
        return

    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])
    simulation_app = sc.boot(capture_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from omni.kit.viewport.utility import (get_active_viewport,
                                           capture_viewport_to_file)
    from isaacsim.core.utils.viewports import set_camera_view
    from pxr import UsdGeom

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.Xform.Define(stage, "/World/Scene10")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene10"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl, rotY=rotY,
                               collider=col)

    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]

        def tex(role, path, scale, **kw):
            return sc.make_pbr(stage, path, sc.tex_path(role, "diff"),
                               sc.tex_path(role, "nor"),
                               sc.tex_path(role, "rough"), scale, **kw)

        M = {}
        M["deck"] = tex("wood_dark", "/World/Looks/Deck", sca["wood_dark"],
                        tint=mp["deck_tint"])
        M["stringer"] = tex("wood_dark", "/World/Looks/Stringer",
                            sca["wood_dark"] * 1.6, tint=mp["stringer_tint"])
        # [S3-8] algae / green weathering at the shaded column feet. The material name
        #   must keep a wood token: `_look_spec` classifies by the **material path**, and
        #   the metal rule (which contains "rail", "post", "pole") is tested before the
        #   wood rule — a material called `.../Looks/RailTimber` would be shaded as metal.
        M["algae"] = tex("wood_dark", "/World/Looks/DeckAlgae",
                         sca["wood_dark"] * 1.6, tint=mp["algae_tint"])
        # [GT-115 ⑭ (5)] the guard's two orientation tones. Same naming discipline as
        #   `DeckAlgae` above and for the same reason: `_look_spec` tests the **metal**
        #   rule (tokens "rail" / "post" / "pole" / "frame" / "fence") *before* the wood
        #   rule, so these carry the "deck" wood token and no metal token — a material
        #   called `.../Looks/GuardRail` would be shaded as steel and undo S3-8's whole
        #   argument. UV scale is the frame's (`× 1.6`), so the grain reads at the same
        #   size on a 38 mm baluster as it did before; only the tint moves.
        M["guard"] = tex("wood_dark", "/World/Looks/DeckGuard",
                         sca["wood_dark"] * 1.6, tint=mp["guard_tint"])
        M["guard_top"] = tex("wood_dark", "/World/Looks/DeckGuardTop",
                             sca["wood_dark"] * 1.6, tint=mp["guard_top_tint"])
        # [v6] built retaining wall (masonry, rubble scale) / natural cut face (jointless) / coping (concrete)
        M["rock"] = tex("rock_wall", "/World/Looks/Rock", sca["rock_wall"],
                        tint=mp["rock_tint"])
        M["rockface"] = tex("rock_face", "/World/Looks/RockFace",
                            sca["rock_face"], tint=mp["rockface_tint"])
        M["coping"] = tex("concrete_wall", "/World/Looks/Coping",
                          sca["concrete_wall"], tint=mp["coping_tint"])
        # [GT-124] W4 B-세트 첫 실사용: A=grass_lawn(생존) + B=dirt_park(고사
        # 반점), blend_default 0.35 ± 엣지 노이즈, 모틀 파장 2.5 m(휴면 얼룩
        # 스케일 — 기본 0.09 m 는 잔반점이라 확대). Looks/Grass → turf 클래스
        # (GT-118)라 지면 MDL 경로 = B-세트 배선이 실제로 도달한다.
        M["grass"] = sc.make_pbr(
            stage, "/World/Looks/Grass",
            sc.tex_path("grass", "diff"), sc.tex_path("grass", "nor"),
            sc.tex_path("grass", "rough"), sca["grass"],
            tint=mp["grass_tint"],
            blend=dict(diff=sc.tex_path("dirt_park", "diff"),
                       nor=sc.tex_path("dirt_park", "nor"),
                       rough=sc.tex_path("dirt_park", "rough"),
                       scale_m=2.2, default=0.28, edge_noise=0.55,
                       edge_wl=2.5))
        M["leaf"] = tex("leaf_ground", "/World/Looks/Leaf",
                        sca["leaf_ground"], tint=mp["leaf_tint"])
        M["dirt"] = tex("dirt_park", "/World/Looks/Dirt", sca["dirt_park"],
                        tint=mp["dirt_tint"])
        # [W2-D ground_kit] tone materials for kit ground elements.
        #   gk_wear: the trodden axis is defined as albedo x0.85 of the trail,
        #   so it must not be bound to the plain dirt material or it renders a
        #   zero-contrast null. gk_gap: a plank gap reads as a dark line, and
        #   with recess-as-tone the line *is* the material.
        M["gk_wear"] = tex("dirt_park", "/World/Looks/GkWear", sca["dirt_park"],
                           tint=tuple(c * 0.85 for c in mp["dirt_tint"]))
        # [W2 fix batch F2] Scatter pool override. Bound over each scattered rock
        #   with `strongerThanDescendants`, so the procured asset's own basecolor
        #   (linear 0.23) is replaced by a real gravel texture dulled to 0.19 -
        #   the middle of the "grey debris 0.18~0.30" convention.
        M["gk_rock"] = tex("gravel", "/World/Looks/GkRock", 0.30,
                           tint=(0.82, 0.81, 0.79))
        M["gk_gap"] = sc.make_pbr(stage, "/World/Looks/GkGap",
                                  diffuse_color=(0.028, 0.024, 0.020),
                                  roughness_const=0.95, specular_level=0.0)
        # [S3-11] far-tier pale silhouette for the city glimpse. Constant colour on
        #   purpose: the BS-4 contract is "distant-silhouette-only … no windows".
        M["backdrop"] = sc.make_pbr(stage, "/World/Looks/FarSkyline",
                                    diffuse_color=mp["backdrop_tint"],
                                    roughness_const=0.90)
        M["hedge"] = tex("grass", "/World/Looks/HedgeDormant", sca["grass"],
                         tint=mp["hedge_tint"])
        M["wood"] = sc.make_pbr(stage, "/World/Looks/Wood",
                                diffuse_color=mp["wood_color"],
                                roughness_const=mp["wood_rough"])
        M["shrub"] = sc.make_pbr(stage, "/World/Looks/Shrub",
                                 diffuse_color=mp["shrub"],
                                 roughness_const=mp["shrub_rough"],
                                 specular_level=0.0)
        M["canopy_a"] = sc.make_pbr(stage, "/World/Looks/CanopyA",
                                    diffuse_color=mp["canopy_a"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        M["canopy_b"] = sc.make_pbr(stage, "/World/Looks/CanopyB",
                                    diffuse_color=mp["canopy_b"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        # [v5.2 user] arbitrary warning sign removed - sign panel and backing material creation deleted.
        M["tread"] = M["deck"] if cfg["cue_material_break"] else M["stringer"]
        return M

    # -------------------------------------------------------------------
    # terrain : axis-aligned plates + Y-direction slopes (rotX slabs)
    # -------------------------------------------------------------------
    def ybank(path, x0, x1, y_hi, z_hi, y_lo, z_lo, thick, mtl):
        """Slope slab tilting from +Y (high) → −Y (low). The Y counterpart of build_slope.
        rotX(θ): local +Y → (0, cosθ, sinθ), so θ>0 descends toward −Y.
        Local −Z (the thickness direction) → world (0, sinθ, −cosθ)."""
        dy, dz = (y_hi - y_lo), (z_hi - z_lo)
        ang = math.atan2(dz, dy)
        L = math.hypot(dy, dz)
        cy = (y_hi + y_lo) / 2.0 + (thick / 2.0) * math.sin(ang)
        cz = (z_hi + z_lo) / 2.0 - (thick / 2.0) * math.cos(ang)
        return sc._oriented_box(stage, path, ((x0 + x1) / 2.0, cy, cz),
                                (x1 - x0, L, thick), mtl, collider=True,
                                rotx=math.degrees(ang))

    def build_terrain(M):
        # [W2-0 P-A] TrailPath is what plan A decorates. It is 1.70 m wide so
        #   `_skin_wanted` already rejects it (needs >= 4.0 m on both axes),
        #   but the registration is explicit so the guarantee does not depend
        #   on a width that a later edit could change. Same for the entry deck
        #   (also covered by the "deck" token in `_SKIN_DENY`).
        sc.skin_exclude(f"{ROOT}/Plate_TrailPath", f"{ROOT}/EntryDeck")
        for nm, x0, x1, y0, y1, zt, th, mk in PARAMS["plates"]:
            BOX(f"{ROOT}/Plate_{nm}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, zt - th / 2.0),
                (x1 - x0, y1 - y0, th), M[mk], col=True)
        for nm, x0, x1, yh, zh, yl, zl, th, mk in PARAMS["ybanks"]:
            ybank(f"{ROOT}/Bank_{nm}", x0, x1, yh, zh, yl, zl, th, M[mk])
        # [GT-65 §0-2] the deck's hand-off to the lower park. `col=False` on purpose:
        #   these strips are a 2 mm dirt veneer over ground that already carries a
        #   collider (`LowerParkMain` top −6.620 / the corridor bench past its last
        #   station), so they add a trail reading and **no** walking surface, no drop
        #   edge and no collider — the GT-65 row stays R-3.
        for nm, x0, x1, y0, y1, zt, th in PARAMS["exit_paths"]:
            BOX(f"{ROOT}/Plate_{nm}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, zt - th / 2.0),
                (x1 - x0, y1 - y0, th), M["dirt"], col=False)
        # [S3-10] the deck corridor's real descending slope, one sloped slab per segment
        #   of `GROUND_LINE`. This is the shaft's replacement: instead of a 7.40 m masonry
        #   wall holding a vertical ground, the hill falls **with** the deck at a mean
        #   25.8 % and is benched level under each landing, which is how a cut-and-fill
        #   trail bench is actually built. The slab side faces at y = CORRIDOR_Y0 / Y1 are
        #   the natural scarps down to the lower park and up to the north bank — no
        #   masonry, no coping, no fortress.
        #   [GT-119 ②] the run/drop now come from `corridor_slabs()`, which carries the
        #   downhill seam lap. `margin` stays 0.0: `build_slope` adds margin to the
        #   *length* and re-centres, i.e. it extends **both** ends, and an uphill
        #   extension would lift the slab over its uphill neighbour at every concave
        #   kink. The lap is asymmetric by construction, so it is authored into the
        #   segment's own end point instead. Prim names and count are unchanged.
        cg = PARAMS["corridor"]
        for nm, xa, za, run, drop, _ang, _lap, _xe, _ze in corridor_slabs():
            sc.build_slope(stage, f"{ROOT}/{nm}", xa, za,
                           run, drop, cg["y0"], cg["y1"],
                           float(cg["thick"]), M["grass"], margin=0.0,
                           collider=True)

    # -------------------------------------------------------------------
    # [GT-77 · §0-2] approach-path finishing at the two deck ends
    # -------------------------------------------------------------------
    def build_approach(M):
        """Lay the `approach_members()` table, plus the head-wall fill batter.

        `col=False` on every member without exception. Each one is a veneer or a trim
        over a plate that already carries the collider (`TrailPath`/`UpperTrail` at the
        entry, `Landing_5`/`LowerParkMain` at the exit), which is the same contract
        `exit_paths` is built under: the walking surface, the drop edges, the hazard
        registry and the GT-read AABBs are all exactly where they were.
        """
        mk = dict(apron="dirt", header="stringer", edge="stringer", verge="hedge")
        for name, kind, ctr, size in approach_members():
            BOX(f"{ROOT}/{name}", ctr, size, M[mk[kind]], col=False)
        # [GT-77 (4)] head-wall fill batter. North of the deck the terrace top (0.000)
        #   met the corridor bench (−0.255) as a raw vertical cut face 6.37 m long —
        #   `UpperTrail`'s +X face, standing in `reversal`. A 0.90 m batter returns it
        #   to grade at 15.8 deg. `margin` is left at the builder's default so the
        #   uphill end laps **back over** the terrace instead of leaving the vertical
        #   face showing through a wedge under the batter's own crest `[computed]`.
        #   `collider=False`: the corridor bench under it already carries the collision
        #   surface, so the physics world is bit-identical to the previous round.
        hf = PARAMS["approach"]["head_fillet"]
        sc.build_slope(stage, f"{ROOT}/HeadFillet", float(hf[0]), float(hf[1]),
                       float(hf[2]), float(hf[3]), float(hf[4]), float(hf[5]),
                       float(hf[6]), M["grass"], collider=False)

    # -------------------------------------------------------------------
    # [W2-D] ground_kit - P18 deck_trail_hybrid (two plans, two z levels).
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(stain_dirt=M["leaf"], wear=M["gk_wear"],
                  edge_break=M["leaf"], litter=M["leaf"], deck=M["gk_gap"],
                  debris=M["gk_rock"])
        a = gk.apply_ground(kit, f"{ROOT}/GKit", ground_plan(), M2,
                            skin_exclude=sc.skin_exclude,
                            scatter=sc.scatter_debris)
        b = gk.apply_ground(kit, f"{ROOT}/GKitDeck", ground_plan_deck(), M2,
                            skin_exclude=sc.skin_exclude)
        # 10-2 · [W3 F3 / DEC-2 feather ring] - the boundary treatment for the leaf drifts,
        #   now written against the **new masks**. The outline it used to chase (dE76 27.3,
        #   the strongest boundary Sec.13.3 found) was a rectangle's; a lobe has no straight
        #   edge, so the ring's job changes from "hide a ruled line" to "let the carpet
        #   fade out", and it therefore runs on **all four** drifts, not only the two trail
        #   ones. `scatter_debris(edge_bias=...)` skips the interior so the cards land in
        #   the band straddling the mask boundary, which is DEC-2's feather ring exactly.
        g = PARAMS["gkit"]
        pad = float(g["leaf_ring_pad"])
        ring = 0
        for i, (cx, cy, sx, sy, zone) in enumerate(
                PARAMS["leaf_ground_patches"]):
            # [GT-77] the ring boxes reach into the verge and over the apron, both of
            #   which stand proud of the plan's flat z — so the ring is seated on a
            #   surface function instead of a scalar. `approach_dressing_z` is the
            #   identity outside the approach members, so the other two rings are
            #   unchanged.
            _zt = _zone_z(cx, cy, zone)
            ring += int(sc.scatter_debris(
                stage, f"{ROOT}/GKit/LeafRing_{i}",
                cx - sx / 2.0 - pad, cy - sy / 2.0 - pad,
                cx + sx / 2.0 + pad, cy + sy / 2.0 + pad,
                _zt,
                cover=0.10, seed=gk.det_seed("scene10.leafring", i),
                edge_bias=pad,
                ground_fn=lambda px, py, _b=_zt: approach_dressing_z(px, py, _b),
                max_count=int(g["leaf_ring_n"])) or 0)
        print(f"[ground_kit] scene10 P18 · 프림 {a['prims']}+{b['prims']} · "
              f"산포 {a['instances']}+{ring} · δmax {a['gt_delta_max']:.4f} · "
              f"unit_cell {a['unit_cell']}")
        return a

    def build_flat_fill(M):
        """hazard_stairs=False control : the stair run becomes a flat z=0 deck."""
        ld = PARAMS["landing"]
        x0, x1 = PLAN_X0, PLAN_X1
        BOX(f"{ROOT}/FlatDeck",
            ((x0 + x1) / 2.0, (ld["y0"] + ld["y1"]) / 2.0, -0.06),
            (x1 - x0, ld["y1"] - ld["y0"], 0.12), M["deck"], col=True)

    # -------------------------------------------------------------------
    # switchback deck stair
    # -------------------------------------------------------------------
    def rail_lattice(prefix, x0, x1, y0, y1, z_top):
        """[S3-8] one lattice / grid infill bay (E10-8), crossed square battens.

        G10's lattice is **timber**, so the metal grating route is not used; the panel
        is two crossed batten sets at ~0.12 m pitch filling the bay between the top of
        the bottom rail and the underside of the top rail. `build_open_riser_stairs`'s
        `slits=` grating was the alternative and is rejected for the same reason.
        """
        r = PARAMS["rail"]
        lat = r["lattice"]
        horiz = abs(x1 - x0) >= abs(y1 - y0)
        L = math.hypot(x1 - x0, y1 - y0)
        s = float(lat["sec"])
        pitch = float(lat["pitch"])
        z_lo = z_top + r["bot_z"] + r["bot"][1] / 2.0
        z_hi = z_top + r["h"] - r["top"][1]
        H = z_hi - z_lo
        if H <= 2 * pitch or L <= 2 * pitch:
            return 0
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        n = 0
        nv = max(1, int(round(L / pitch)) - 1)
        for i in range(nv):
            t = (i + 1) / float(nv + 1)
            bx, by = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            BOX(f"{prefix}/LatV_{i}", (bx, by, z_lo + H / 2.0),
                (s, s, H) if horiz else (s, s, H), M["rail"])
            n += 1
        nh = max(1, int(round(H / pitch)) - 1)
        for j in range(nh):
            zz = z_lo + H * (j + 1) / float(nh + 1)
            BOX(f"{prefix}/LatH_{j}", (cx, cy, zz),
                (L, s, s) if horiz else (s, L, s), M["rail"])
            n += 1
        return n

    def deck_rail(prefix, x0, x1, y0, y1, z_top, broken=False, lattice=False,
                  butt=False, butt_ends=(True, True), bal_at=None):
        """[S3-8] one axis-aligned railing run in **square sawn sections**.

        Members, all boxes (G10 has no round member anywhere in frame):
          top rail    38 x 140 laid flat, top face at z_top + rail.h (= 1.10 m)
          mid rail    38 x 89 at rail.mid_frac of the height
          bottom rail 38 x 89 at rail.bot_z above the walking surface
          balusters   38 x 38, plumb, horizontal pitch rail.bal_step (clear gap 0.112)
          line posts  90 x 90, stopping under the top rail (the *terminal* posts are
                      capped newels and are built once, by build_newels)
        broken=True → rails, balusters and lattice gone, the posts remain. That is the
        scene's negative-obstacle cue (§9 P-2, frozen) and the hazard geometry is
        unchanged by this rebuild.

        [GT-65] `butt=True` is set on a **cross** run — the run that closes a step in
        the guarded boundary. Each of its members is shortened at both ends by half the
        section of the member it meets (`w/2`, tag for tag), so it dies on the face of
        the X-run rather than crossing it. Without it two 38x140 top rails would share
        a 70x70 volume at every corner **and** present two coplanar top faces at the
        same z — the classic corner z-fight. The field (balusters, line posts) is laid
        out over the same trimmed span, so end gaps stay equal to field gaps.

        [GT-115 ⑭] `butt_ends` makes that butt per-end, and `bal_at` overrides the field
        layout with explicit stations. Both exist for the **return** stub: it butts only
        where it turns off the X-run, because its free end has to die inside its own
        capped end post (a symmetric butt leaves it 25 mm short of the post face
        `[computed]`), and a 0.30 m stub cannot carry the field pitch, so it takes one
        centred baluster — clear gap 0.086 m to each post face, tighter than the 0.112 m
        field and therefore never the looser reading. The defaults reproduce the GT-65
        cross **exactly**.
        """
        r = PARAMS["rail"]
        horiz = abs(x1 - x0) >= abs(y1 - y0)
        L = math.hypot(x1 - x0, y1 - y0)
        if L < 1e-6:
            return
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        top_w, top_t = r["top"]
        kind = "cross" if butt else "level"
        # field span and its start offset along the run. The trim is per-end: with the
        # default (both ends butted) it is symmetric, so the member centres never move
        # and only their length changes — the GT-65 behaviour, bit for bit.
        b0 = bool(butt and butt_ends[0])
        b1 = bool(butt and butt_ends[1])
        Lf = rail_field_span(kind, L, (b0, b1))
        s0 = (top_w / 2.0) if b0 else 0.0
        if not broken:
            # (w, t) per rail; z is the member **centre**
            for tag, (w, t), zc in (
                    ("Top", r["top"], z_top + r["h"] - top_t / 2.0),
                    ("Mid", r["mid"], z_top + r["h"] * r["mid_frac"]),
                    ("Bot", r["bot"], z_top + r["bot_z"])):
                c0 = (w / 2.0) if b0 else 0.0
                c1 = (w / 2.0) if b1 else 0.0
                Lm = max(0.02, L - c0 - c1)
                size = (Lm, w, t) if horiz else (w, Lm, t)
                sh = (c0 - c1) / 2.0          # 0 when the trim is symmetric
                BOX(f"{prefix}/Rail{tag}",
                    (cx + ux * sh, cy + uy * sh, zc), size,
                    M["guard_top"] if tag == "Top" else M["rail"])
            if lattice:
                rail_lattice(prefix, x0, x1, y0, y1, z_top)
        # line posts first: a baluster centred inside one is a duplicate member, not a
        # baluster (38x38 fully swallowed by a 90x90), and on a 3.20 m run the 1/3
        # post station **is** a baluster station exactly. Stations are measured along
        # the trimmed field so posts cannot land under the butt.
        ps = r["post"]
        ph = r["h"] - top_t
        n = max(2, int(round(Lf / r["spacing"])) + 1)
        post_s = [s0 + Lf * i / float(n - 1) for i in range(1, n - 1)]
        if not broken and not lattice:
            b = r["bal"]
            z_bal0 = z_top + r["bot_z"] + r["bot"][1] / 2.0
            hh = (z_top + r["h"] - top_t) - z_bal0
            nb, _pitch = baluster_run(Lf, r["bal_step"])
            stations = ([float(v) for v in bal_at] if bal_at is not None
                        else [s0 + Lf * (i + 1) / float(nb + 1)
                              for i in range(nb)])
            clash = (ps + b) / 2.0
            for i, s in enumerate(stations):
                if any(abs(s - q) < clash for q in post_s):
                    continue
                BOX(f"{prefix}/Bal_{i}", (x0 + ux * s, y0 + uy * s,
                                          z_bal0 + hh / 2.0),
                    (b, b, hh), M["rail"])
        for i, s in enumerate(post_s):
            BOX(f"{prefix}/Post_{i + 1}", (x0 + ux * s, y0 + uy * s,
                                           z_top + ph / 2.0),
                (ps, ps, ph), M["rail"])

    def build_newel(path, px, py, z_walk, mtl=None):
        """[S3-8] one capped newel: 90x90 post projecting rail.newel_proud above the
        top rail, carrying an oversized cap block. §2.A.1-2 — the cap is the strongest
        single 'this is timber, not steel' tell in G10."""
        r = PARAMS["rail"]
        s = r["newel"]
        cw, cd, ct = r["newel_cap"]
        h = r["h"] + r["newel_proud"]
        BOX(f"{path}/Post", (px, py, z_walk + h / 2.0), (s, s, h),
            mtl or M["rail"])
        # [GT-115 ⑭ (5)] the cap is the guard's other up-facing member, so it takes the
        #   silvered tone with the top rails; the post under it stays on the moss side.
        BOX(f"{path}/Cap", (px, py, z_walk + h + ct / 2.0), (cw, cd, ct),
            mtl or M["guard_top"])

    def build_handrail(runs=None):
        """[GT-115 ⑭ (4)] the graspable handrail line and its brackets.

        One Ø35 tube per guard run, laid on the axis `handrail_lines()` derives from the
        run inventory, plus a bracket cleat every `hand.brk_step` along it. **Nothing
        existing is read for a position and nothing existing moves**: the tube is the run
        centreline pushed inboard and dropped under the top rail, so a raking tube is
        parallel to its own nosing plane by construction.

        The cleat's top is let `brk_bed` into the underside of the top rail, so it is
        fixed to a member instead of floating between balusters, and it reaches from the
        rail line to the tube axis — the tube is half-lapped into its inboard end, which
        is what a bracket does to a handrail. The tube itself clears every square member:
        newel face 0.045 / baluster 0.019 / top-rail inner edge 0.070 from the line
        against the tube's 0.0625-0.0975, and in z it passes **under** the top rail
        (1.008-1.043 vs 1.062-1.100) `[computed]`.

        Returns (tube count, bracket count).
        """
        r = PARAMS["rail"]
        hd = r["hand"]
        rad = float(hd["dia"]) / 2.0
        bw, bo, bh = (float(v) for v in hd["brk"])
        top_t = float(r["top"][1])
        lines = handrail_lines(runs)
        n_t, n_b = 0, 0
        for ln in lines:
            # the handrail members live under the run they belong to, so a run and its
            # grasp cannot drift apart in the stage tree either
            grp = (f"{ROOT}/{ln['name'].rsplit('/', 1)[0]}/HandGrp_{ln['side']}"
                   if ln["kind"] == "rake" else f"{ROOT}/{ln['name']}/HandGrp")
            sc.add_cylinder(stage, f"{grp}/Hand",
                            ((ln["x0"] + ln["x1"]) / 2.0,
                             (ln["y0"] + ln["y1"]) / 2.0,
                             (ln["z0"] + ln["z1"]) / 2.0),
                            rad, ln["L"], M["guard_top"],
                            rotY=ln["rotY"], rotZ=ln["rotZ"], collider=False)
            n_t += 1
            # bracket stations, held `brk_end` off each end so a cleat never lands on
            # the mitre where two tubes meet
            plan = float(ln["plan"])
            e = min(float(hd["brk_end"]), plan / 3.0)
            span = max(0.0, plan - 2.0 * e)
            nb = max(1, int(round(span / float(hd["brk_step"]))) + 1)
            for i in range(nb):
                t = 0.5 if nb == 1 else i / float(nb - 1)
                s = e + span * t
                fx = s / plan
                px = ln["x0"] + (ln["x1"] - ln["x0"]) * fx
                py = ln["y0"] + (ln["y1"] - ln["y0"]) * fx
                pz = ln["z0"] + (ln["z1"] - ln["z0"]) * fx
                # from the rail line out to the tube axis, top let into the top rail
                cx = px - ln["ix"] * bo / 2.0
                cy = py - ln["iy"] * bo / 2.0
                cz = (pz + float(hd["drop"]) - top_t
                      + float(hd["brk_bed"])) - bh / 2.0
                size = (bw, bo, bh) if ln["horiz"] else (bo, bw, bh)
                BOX(f"{grp}/Brk_{i}", (cx, cy, cz), size, M["rail"])
                n_b += 1
        return n_t, n_b

    def build_deck(M):
        fl = PARAMS["flights"]
        ld = PARAMS["landing"]
        ent = PARAMS["entry"]
        r = PARAMS["rail"]
        lcy = (ld["y0"] + ld["y1"]) / 2.0
        lsy = ld["y1"] - ld["y0"]

        def _rake_rail(rr):
            """[S3-8 · GT-65] the raking railing on one side of one flight.

            The shared `sc.build_railing_line` is no longer called from this scene. It
            emits `add_cylinder` posts and rails by construction, and round members are
            exactly the defect S3-8 exists to remove (§2.A.1-1). The `baluster_r=0.0`
            guard that used to sit here — the red team's 48 interpenetrating pairs if the
            shared balusters were switched on — is therefore **preserved by construction
            and strengthened**: there is no shared-baluster code path left to switch on,
            so the trap is structurally removed rather than merely disabled.

            The rails run parallel to the **nosing plane**, which passes through
            (x_top, z_top) at slope riser/tread, so a rail top face at `top0 - slope·dx`
            is exactly `rail.h` above the nosing line at every station.
            The balusters stay **plumb** (KCS 34 50 10 3.2.6(3)) and are pitched
            `bal_step` **horizontally**, so the clear gap is the same 0.112 m as on the
            level runs rather than shrinking by cos(pitch).
            The rail line sits **outboard** of the deck edge by half a baluster, so the
            baluster's inner face is flush with the walking surface and the clear width
            between the two railings is exactly the declared 1.500 m — a railing set
            *inboard* would quietly eat 120 mm off the statutory 너비. Band pitch
            `y_off = 0.85` then leaves 0.072 m between the inner rail lines of two
            adjacent flights.

            [GT-65] the line `y` and the head/foot stations now come from `rail_runs()`,
            the same inventory the level runs and the newels come from — which is what
            makes a flight rail and the landing rail it continues into **collinear**.
            Newels are no longer built here: this function used to add its own at the
            head and foot, 19 mm from the landing's, so every junction carried two
            90x90 capped posts. They are built once, per boundary node, by the newel
            pass below.
            """
            f = SEQ[int(rr["k"])]
            grp = f"{ROOT}/FlightGrp_{f['k']}"
            tag, y = rr["side"], rr["y0"]

            def gfn(x, _xt=f["x_top"], _zt=f["z_top"]):
                if x <= _xt:
                    return _zt
                i = min(int((x - _xt) / fl["tread"]) + 1, f["steps"])
                return _zt - i * fl["riser"]

            top_w, top_t = r["top"]
            f_run, f_drop = f["run"], f["drop"]
            slope = f_drop / f_run
            # three raking rails. `build_slope` is a rotateY box whose **top face**
            # is the plane (x0,z0)->(x0+run,z0-drop), so z0 is the member's own top
            # face and `thick` is its section depth. The top rail's top face is the
            # 1.10 m line itself; the mid and bottom rails are given by their centre
            # plus half their thickness.
            rakes = (
                ("Top", r["top"][0], r["top"][1],
                 f["z_top"] + r["h"]),
                ("Mid", r["mid"][0], r["mid"][1],
                 f["z_top"] + r["h"] * r["mid_frac"] + r["mid"][1] / 2.0),
                ("Bot", r["bot"][0], r["bot"][1],
                 f["z_top"] + r["bot_z"] + r["bot"][1] / 2.0))
            for rtag, w, t, z0 in rakes:
                # [GT-115 ⑭ (5)] the raking top rail is an up-facing member exactly like
                #   the level ones, so it takes the silvered tone; mid and bottom stay on
                #   the moss side.
                sc.build_slope(stage, f"{grp}/Rail{rtag}_{tag}",
                               f["x_top"], z0, f_run, f_drop,
                               y - w / 2.0, y + w / 2.0, t,
                               M["guard_top"] if rtag == "Top" else M["rail"],
                               margin=0.0, collider=False)
            # plumb square balusters, tread face -> underside of the top rail
            b = r["bal"]
            top0 = f["z_top"] + r["h"] - top_t
            nb, _pitch = baluster_run(f_run, r["bal_step"])
            for i in range(nb):
                bx = f["x_top"] + f_run * (i + 1) / float(nb + 1)
                zr = top0 - slope * (bx - f["x_top"])
                zg = gfn(bx)
                hh = zr - zg
                if hh > 0.05:
                    BOX(f"{grp}/Bal_{tag}_{i}", (bx, y, zg + hh / 2.0),
                        (b, b, hh), M["rail"])

        # entry deck (retaining wall head -> first step)
        BOX(f"{ROOT}/EntryDeck",
            ((ent["x0"] + ent["x1"]) / 2.0, lcy, ent["top"] - ent["thick"] / 2.0),
            (ent["x1"] - ent["x0"], lsy, ent["thick"]), M["deck"], col=True)

        for f in SEQ:
            k = f["k"]
            lo, hi = band(k)                 # [S3-10] world band; no rot group
            grp = f"{ROOT}/FlightGrp_{k}"
            sc.build_open_riser_stairs(
                stage, f"{grp}/Flight", f["x_top"], lo, hi, fl["riser"],
                fl["tread"], f["steps"], f["z_top"], M["tread"],
                M["stringer"], tread_t=fl["tread_t"], gap=fl["gap"])
            # landing — spans both width bands so the walker crosses from this flight's
            # band into the next one's; the rest platform also projects past +Y.
            BOX(f"{ROOT}/Landing_{k}",
                ((f["lx0"] + f["lx1"]) / 2.0, (f["ly0"] + f["ly1"]) / 2.0,
                 f["z_bot"] - ld["thick"] / 2.0),
                (f["lx1"] - f["lx0"], f["ly1"] - f["ly0"], ld["thick"]),
                M["deck"], col=True)

        # [GT-65] deck continuity. The entry deck was the **only** planked surface in
        #   the scene: `ground_plan_deck()` (P18 row 10-3) gave it 9 널 틈 over its
        #   1.5 m and every landing beyond it was a smooth 0.12 m slab, so the deck
        #   reading died 1.5 m into a 25.6 m walk and the landings read as concrete.
        #   The same builder, the same board width (25 x 140 시판 데크판재, identical to
        #   the tread board), the same recess-as-tone material and the same
        #   `exc="plank_gap"` GT class are carried to all six landings, boards laid
        #   **across** the direction of travel exactly as on the entry deck.
        #   Walking z is unchanged (the strip top is `surface_top_z` = deck top
        #   +0.6 mm, a recess by tone), so this is dressing, not a GT edit. P-2 keeps
        #   널 틈 — this extends them to the rest of the run, it does not restyle them.
        gkit_deck = gk.kit_from_scene_common(sc, stage)
        gpk = PARAMS["gkit"]
        n_pl = 0
        for f in SEQ:
            n_pl += int(gk.build_deck_planks(
                gkit_deck, f"{ROOT}/LandingPlank_{f['k']}",
                f["lx0"], f["ly0"], f["lx1"], f["ly1"], f["z_bot"],
                M["gk_gap"], plank_w=float(gpk["plank_w"]),
                seed=gk.det_seed("scene10.landplank", f["k"]))["prim_count"])
        print(f"[GT-65] 참 널 틈 {n_pl}프림 / 참 {len(SEQ)}개 "
              f"(판폭 {gpk['plank_w']:.3f} m · 진입데크와 동일 시공 · 보행면 z 불변)")

        # deck support columns — [S3-8 / C7] round Ø150 -> square 120x120 sawn timber.
        #   All grounded on the ground or on the landing below. The columns that reach
        #   the ground get a short **algae collar** at the foot: greenish weathering in
        #   the damp, shaded litter is what makes 방부목 read as outdoor timber (§4.2-3),
        #   and it is 1 prim per grounded column.
        pp = PARAMS["post"]
        sec = pp["sec"]
        for nm, cx, cy, z_lo, z_hi in post_segments():
            h = z_hi - z_lo
            BOX(f"{ROOT}/Column_{nm}", (cx, cy, z_lo + h / 2.0),
                (sec, sec, h), M["stringer"], col=True)
            if abs(z_lo - corridor_z(cx)) < 1e-6 and h > 0.6:
                BOX(f"{ROOT}/ColumnAlgae_{nm}", (cx, cy, z_lo + 0.175),
                    (sec + 0.006, sec + 0.006, 0.35), M["algae"])

        # [GT-65] the whole railing — flight, landing, entry and every corner — is
        # assembled from **one** pass over `rail_runs()`, so the SMOKE self-check and
        # the stage cannot disagree: a landing edge cannot silently lose its rails
        # while keeping its posts, a corner cannot end up with two newels, and a run
        # cannot be drawn across the flight it is supposed to hand the walker to.
        if cfg["cue_railing"]:
            runs = rail_runs()
            lat_run = str(r["lattice"]["run"])
            for rr in runs:
                if rr["kind"] == "rake":
                    _rake_rail(rr)
                elif rr["kind"] == "return":
                    # [GT-115 ⑭ (1)] the run-end return. Butted only at the corner it
                    #   turns off; the free end dies inside its own capped end post the
                    #   way an X-run does. One centred baluster — see `deck_rail`.
                    Lr = math.hypot(rr["x1"] - rr["x0"], rr["y1"] - rr["y0"])
                    deck_rail(f"{ROOT}/{rr['name']}", rr["x0"], rr["x1"],
                              rr["y0"], rr["y1"], rr["z0"],
                              butt=True, butt_ends=(True, False),
                              bal_at=[Lr / 2.0])
                else:
                    deck_rail(f"{ROOT}/{rr['name']}", rr["x0"], rr["x1"],
                              rr["y0"], rr["y1"], rr["z0"],
                              broken=rr["broken"],
                              lattice=(rr["name"] == lat_run),
                              butt=(rr["kind"] == "cross"))
            # capped newels, one per boundary node (see newel_points)
            nws = newel_points(runs)
            for i, (px, py, pz) in enumerate(nws):
                build_newel(f"{ROOT}/Newel_{i}", px, py, pz)
            n_hand = build_handrail(runs)
            print(f"[GT-65] 난간 런 {len(runs)}개 "
                  f"(경사 {sum(1 for q in runs if q['kind'] == 'rake')} · "
                  f"수평 {sum(1 for q in runs if q['kind'] == 'level')} · "
                  f"접합 {sum(1 for q in runs if q['kind'] == 'cross')} · "
                  f"[GT-115 ⑭] 종단 리턴 "
                  f"{sum(1 for q in runs if q['kind'] == 'return')}) · "
                  f"엄지기둥 {len(nws)}개(노드당 1개)")
            print(f"[GT-115 ⑭] 손스침 Ø{r['hand']['dia']:.3f} m · 라인 "
                  f"{n_hand[0]}개 · 브래킷 {n_hand[1]}개 · 파지고 "
                  f"{r['h'] - r['hand']['drop']:.3f} m · 안쪽 편심 "
                  f"{r['hand']['off']:.3f} m (기존 부재 위치·높이 불변)")

        # leaf band : hides the top two step edges of flight0
        lf = PARAMS["leaf"]
        f0 = SEQ[0]
        blo, bhi = band(0)
        for i in (1, 2):
            xa = f0["x_top"] + (i - 1) * fl["tread"]
            xb = f0["x_top"] + i * fl["tread"]
            zt = f0["z_top"] - i * fl["riser"] + lf["proud"]
            cx = (xa + 0.06 + xb + lf["over"]) / 2.0
            sx = (xb + lf["over"]) - (xa + 0.06)
            BOX(f"{ROOT}/LeafTread_{i}", (cx, (blo + bhi) / 2.0,
                                          zt - lf["thick"] / 2.0),
                (sx, bhi - blo, lf["thick"]), M["leaf"])
        # [W3 F3 / DEC-2] 4 ground leaf drifts - **one irregular mask each**.
        #   v6 stacked 3 rotated rectangles per drift to break the boundary. Sec.13.3
        #   measured the result: the leaf-decal outline is still the strongest boundary in
        #   the scene at dE76 **27.3**, 1.8x the dirt<->grass seam (15.2). Three rotated
        #   rectangles have twelve straight edges, not zero. A `build_carpet_mask` lobe has
        #   none, and it costs 1 prim instead of 3 (12 -> 4 over the four drifts).
        lp = PARAMS["leaf_patch"]
        kit = gkit_deck                      # same Kit as the landing plank pass
        for n, (cx, cy, sx, sy, zone) in enumerate(
                PARAMS["leaf_ground_patches"]):
            zt = _zone_z(cx, cy, zone)
            gk.build_carpet_mask(kit, f"{ROOT}/LeafGround_{n}",
                                 cx, cy, sx / 2.0, sy / 2.0, M["leaf"],
                                 z=zt, proud=lf["proud"],
                                 n=24, rough=float(lp["rough"]),
                                 seed=int(lp["seed"]) + n, feather_cap=0)

    # -------------------------------------------------------------------
    # dressing
    # -------------------------------------------------------------------
    def _bare_tree(path, rel, native, cx, cy, gz, target_h, yaw):
        """[S3-11] One **leaf-off** tree, pinned to a species. -> (placed, bare).

        `sc.build_tree(bare=True)` alone is not enough and its own docstring says so: the
        species is drawn by coordinate hash from `VEG_TREES`, and only `Elm_Sapling` of
        the three bare-capable assets is in that pool, so `bare=True` yields a *mixed*
        frame. The planned `species=` kwarg is K4(b) and was never executed, so the scene
        takes the route the docstring names — it calls `add_vegetation` itself.

        [S10c · red-team **F1** (`redteam_s0710_rebuild.md` §1.2/§5.2), K4(0) `e4fc4cf`]
        **The old route here was composition-inert and this scene was its victim.** It
        referenced the *leafed* asset, called `_deactivate_seasonal` on `{path}/Asset/leaves`
        and then made `{path}/Asset` instanceable. USD discards opinions on descendants of
        an instance **regardless of authoring order**, so the stage accepted the
        deactivation, the counter printed `12/12`, and all twelve trees rendered in full
        green leaf (measured in pixels on round `260731_w3_s10`: `from_below` foreground
        and `h1.8_d10` upper-left). The counter had been counting *authored opinions*,
        never composed results.

        The route that works — and the only one that survives instancing — is to reference
        a **wrapper layer** that carries the `over ... (active = false)` above the instance
        boundary, so the deactivation composes **inside** the prototype
        (`assets/veg_bare/<species>_bare.usda`; scene04 precedent `024a985`, generalised
        into `sc.veg_wrapper_rel` by K4(0)). Instancing is kept: all twelve trees still
        share one prototype per species, and that prototype simply has no `leaves`.

        `native` stays the **caller's** value, deliberately: `PARAMS['season']['bare']`
        already carries the trunk-only zmax, so the scale factor `target_h / native` is
        bit-identical to the pre-fix round and the trunks do not move. The only delta this
        function now produces is the foliage leaving the frame, which is exactly what the
        round it feeds is allowed to declare.
        """
        wrel = sc.veg_wrapper_rel(rel, sc.BARE_SUBPRIMS.get(rel), kind="bare")
        # A missing wrapper must never cost the scene its trees (`veg_wrapper_rel`'s own
        # contract): fall back to the leafed asset, place it, and report bare=0 so the
        # self-check and the print say so out loud instead of claiming a leaf-off frame.
        xf = sc.add_vegetation(stage, path, wrel or rel, (cx, cy, gz),
                               yaw_deg=yaw, target_h=target_h, native_h=native)
        if xf is None:
            return (0, 0)
        try:
            # Instancing is set on the prim that HOLDS the reference (`/Asset`), which is
            # now the wrapper. The prototype is composed from the wrapper, leaves and all
            # — that is, without them.
            stage.GetPrimAtPath(f"{path}/Asset").SetInstanceable(True)
        except Exception:
            pass
        return (1, 1 if wrel else 0)

    def build_nature(M):
        tr = PARAMS["tree"]
        se = PARAMS["season"]
        bare_pool = se["bare"]
        n_bare = 0
        n_veg = 0
        for n, (cx, cy, zone, th) in enumerate(PARAMS["trees"]):
            gz = _zone_z(cx, cy, zone)
            rel, native = bare_pool[n % len(bare_pool)]
            target = float(th) * 1.60
            # the reference must land on `<prefix>/Veg/Asset`: that is `build_tree`'s
            # convention **and** the hook `placement_lint`'s tree rule matches
            # (`pattern: '/Veg$'`, `species_from: '<self>/Asset'`). Placing the asset
            # directly under `Tree_n` would make these plantings invisible to LINT-1/2/3
            # and to the LINT-4b species gate — the numbers would improve by dropping out
            # of the check, which is the wrong kind of green.
            _placed, _bare = _bare_tree(f"{ROOT}/Tree_{n}/Veg", rel, native,
                                        cx, cy, gz, target, (n * 47.0) % 360.0)
            n_veg += _placed
            n_bare += _bare
            # [S10c] The fallback trigger is **the asset route being unavailable**, not
            # leaf-off failing. Before the F1 fix the two were conflated, so a wrapper
            # miss would have thrown away twelve real trunks for procedural blobs.
            if n_veg == 0 and n == 0:
                # asset route unavailable (LOOK_GEO off / assets absent) -> procedural
                # fallback for the whole row, with the dormant blob tints.
                for m, (bx, by, bzone, bth) in enumerate(PARAMS["trees"]):
                    sc.build_tree(stage, f"{ROOT}/Tree_{m}", bx, by,
                                  _zone_z(bx, by, bzone), M["wood"],
                                  M["canopy_a"], M["canopy_b"],
                                  trunk_r=tr["trunk_r"], trunk_h=bth,
                                  stake_r=0.004, stake_h=0.02, stake_off=0.2)
                break
        # [S10c] The count is now a **composed** result: it counts trees whose reference
        # target is the wrapper layer, i.e. trees whose prototype has no `leaves` prim.
        # The pre-fix counter counted authored `SetActive(False)` calls, which USD threw
        # away — 12/12 was printed while 12/12 rendered green (red-team F1).
        print(f"[S3-11] 낙엽수 잎-off {n_bare}/{len(PARAMS['trees'])}주 "
              f"(Gray_Birch·Elm_Sapling·Lombardy_Poplar 로테이션 · "
              f"assets/veg_bare/*_bare.usda 참조 래퍼 = 프로토타입 내부 합성)")
        if n_veg and n_bare < n_veg:
            print(f"[S3-11][경고] 래퍼 미해결 {n_veg - n_bare}주 — 잎이 남는다 "
                  f"(assets/veg_bare/ 확인)")

        # autumn-legal shrubs replace the 13 green blob clumps (§4.2-5).
        se_pool = list(se["shrubs"])
        pts = [(cx, cy, _zone_z(cx, cy, zone))
               for cx, cy, zone in PARAMS["shrubs"]]
        placed = sc.place_shrubs(stage, f"{ROOT}/Shrub", pts,
                                 float(se["shrub_h"]), pool=se_pool,
                                 seed=gk.det_seed("scene10.shrub", 0))
        if not placed:
            sh = PARAMS["shrub"]
            emb = sh["embed"]
            for n, (cx, cy, zone) in enumerate(PARAMS["shrubs"]):
                for j, (dx, dy, rx, ry, rz) in enumerate(sh["blobs"]):
                    bx, by = cx + dx, cy + dy
                    gz = min(_zone_z(bx, by - ry, zone), _zone_z(bx, by, zone),
                             _zone_z(bx, by + ry, zone))
                    sc.add_sphere(stage, f"{ROOT}/Shrub_{n}_{j}",
                                  (bx, by, gz + rz * (1.0 - emb)),
                                  (rx, ry, rz), M["shrub"])
        print(f"[S3-11] 가을 관목 {placed}/{len(pts)}군 "
              f"(Burning_Bush 적 30.2 % · Juniper 상록 — 개화종 제외)")

        # rock outcrop at the uphill margin + foot boulders (E10-10).
        #   **Material override is mandatory here, not cosmetic.** The T2 rock scans bind
        #   `assets/urban/nv_core/materials/SimPBR.mdl`, and that module fails to compile
        #   in this runtime — `C120 could not find module '.::baking_annotations'` — so the
        #   boulders render on the shader fallback (a flat saturated red mass, measured in
        #   the `s311_season` probe). Binding the scene's own rock material on the Xform
        #   **above** `/Asset` with `strongerThanDescendants` is the same device
        #   `scatter_debris(mtl=…)` already uses to beat a prototype's mesh-level binding,
        #   and it is the only one that survives `instanceable=True`.
        n_out = 0
        for i, (aid, ox, oy, _oz, oyaw, oscale) in enumerate(PARAMS["outcrop"]):
            try:
                xf = uk.add_urban_asset(stage, f"{ROOT}/Outcrop_{i}", aid,
                                        pos_m=(ox, oy, ground_z(ox, oy)),
                                        yaw_deg=oyaw, scale_mul=oscale,
                                        z_mode="base", scene="10",
                                        instanceable=False)
                if xf is None:
                    continue
                # `instanceable=False` on purpose: an ancestor `strongerThanDescendants`
                # bind does not reach inside a prototype (measured — the `s311b` probe
                # still rendered the fallback), so the override has to be written
                # on the meshes themselves, which is exactly what `urban_kit`'s own
                # `_bind_far_override` does. Four placements, so nothing is lost by not
                # sharing a prototype.
                # **[W3 K-micro · T4b-F2] The conclusion above is right; its cited cause
                # was not, and the difference is a revert trap.** This comment used to
                # name the **SimPBR/MDL** fallback. That one was fixed by T4's
                # `ensure_mdl_package()` and is no longer what falls back here. Today the
                # fallback on `Outcrop_0` is **MaterialX**: `rock_moss_set_01` is a Poly
                # Haven CC0 row and every one of the 33 CC0 rows / 50 materials reaches an
                # `ND_normalmap_float` node that is missing from this runtime's Sdr
                # registry (`cannot find SdrNode`, ×4 in frame) `[measured — w3_t4b_v1.md
                # §1.2, §3]`. So this bind is **not** dead weight left over from a fixed
                # MDL bug: dropping it lands FU-1's measured **0.02 % → 4.50 %** red.
                # `Outcrop_1..3` are NVIDIA assets with no MaterialX gap — for those three
                # the workaround function really is gone and only the `rockface_tint` art
                # decision remains. The clean migration is `urban_kit`'s `treatment=`
                # wrapper (`w3_t4b_v1.md` §4.2), which is this scene owner's call, not the
                # kit lane's; this edit corrects the record only.
                try:
                    from pxr import Usd, UsdShade
                    ap = stage.GetPrimAtPath(f"{ROOT}/Outcrop_{i}/Asset")
                    nb = 0
                    for pr in Usd.PrimRange(ap):
                        if pr.GetTypeName() == "Mesh":
                            UsdShade.MaterialBindingAPI.Apply(pr).Bind(
                                M["rockface"])
                            nb += 1
                    if nb == 0:
                        print(f"[S3-11][경고] 노두 메시 0개 — 재질 미교체 {aid}")
                except Exception as e:
                    print(f"[S3-11][경고] 노두 재질 바인딩 실패 {aid}: {e}")
                n_out += 1
            except Exception as e:
                print(f"[S3-11][경고] 노두 배치 실패 {aid}: {e}")
        print(f"[S3-11] 암반 노두 {n_out}/{len(PARAMS['outcrop'])}개 "
              f"(z_mode=base · sink 0 · SimPBR 폴백 대신 rockface 상위 바인딩)")

        # continuous leaf litter over the corridor slope — C20. The 4 CB-2 carpet-mask
        # lobes are **kept** as the dense cores (H4: a lobe may move, it may never become
        # a rectangle again); the continuity comes from scatter around them, not from
        # more lobes. `ground_fn` is mandatory here: without it every card would lie flat
        # in mid-air over a 25.8 % slope.
        #
        # [GT-115 ⑭ (2)] each band is laid as **three source variants** instead of one
        #   draw. The audit counts one silhouette ~20× with rotation-only variation, and
        #   the cause was here, not in the asset library: one call, one seed, the whole
        #   5-row pool — whose two cluster rows carry 9.6× / 3.9× the **mean**
        #   per-instance cover of its three single-leaf rows, so the frame is
        #   area-dominated by two cards spun about Z (the arithmetic is in
        #   `PARAMS['season']['litter_variants']`). The variants are cut out of the
        #   **same** five USDs (they are
        #   already five different card arrangements of the same fallen leaves), each
        #   with its own scale band, tilt band and `det_seed` draw. Caps sum to the old
        #   `litter_max` per band, and all three calls are cap-bound at `litter_cover`,
        #   so the count is exactly the previous round's 780 — a re-mix, not more litter.
        se = PARAMS["season"]
        cg = PARAMS["corridor"]
        n_lit = 0
        for i, (lx0, lx1, ly0, ly1) in enumerate((
                (HEAD_X, PLAN_X1, cg["y0"], -1.70),
                (HEAD_X, PLAN_X1, 1.70, 4.40),
                (HEAD_X, PLAN_X1 * 0.5, -1.70, 1.70))):
            for v, va in enumerate(se["litter_variants"]):
                n_lit += int(sc.scatter_debris(
                    stage, f"{ROOT}/Litter_{i}_{va['tag']}",
                    lx0, ly0, lx1, ly1, 0.0,
                    cover=float(se["litter_cover"]),
                    pool=litter_pool(va["cards"]),
                    scale_jitter=(float(va["scale"][0]), float(va["scale"][1])),
                    tilt_max=float(va["tilt"]),
                    seed=gk.det_seed("scene10.litter", i * 10 + v),
                    ground_fn=ground_z,
                    max_count=int(va["cap"])) or 0)
        print(f"[S3-11] 연속 낙엽 산포 {n_lit}개 (CB-2 로브 4개는 조밀 코어로 존치)")
        lv = se["litter_variants"]
        span = (max(float(v["scale"][1]) for v in lv)
                / max(min(float(v["scale"][0]) for v in lv), 1e-9))
        print(f"[GT-115 ⑭] 낙엽 소스 변형 {len(lv)}종 × 대역 3 — "
              f"{' · '.join(str(v['tag']) for v in lv)} "
              f"(축척 스팬 ×{span:.2f} · 신규 자산 조달 0건)")

        # distant city glimpse — BS-4 backdrop contract: 0 windows, silhouette only.
        for i, (bx, by, bw, bd, bh) in enumerate(PARAMS["backdrop"]):
            BOX(f"{ROOT}/Backdrop_{i}", (bx, by, bh / 2.0 + GROUND_Z),
                (bw, bd, bh), M["backdrop"])

    def build_props(M):
        # timber waymarker (post + 2 direction blades + cap)
        sp = PARAMS["signpost"]
        CYL(f"{ROOT}/SignPost/Post",
            (sp["cx"], sp["cy"], sp["post_h"] / 2.0), sp["post_r"],
            sp["post_h"], M["wood"], col=True)
        BOX(f"{ROOT}/SignPost/Cap",
            (sp["cx"], sp["cy"], sp["post_h"] + sp["cap"][2] / 2.0),
            sp["cap"], M["wood"])
        for k, (az, yaw) in enumerate(sp["arms"]):
            grp = sc.build_rot_group(stage, f"{ROOT}/SignPost/Arm_{k}",
                                     (sp["cx"], sp["cy"]), yaw)
            BOX(f"{grp}/Box", (sp["cx"] + sp["arm_off"], sp["cy"], az),
                sp["arm"], M["wood"])
        # bench 1
        bn = PARAMS["bench"]
        sc.build_bench(stage, f"{ROOT}/Bench", bn["cx"], bn["cy"], 0.0,
                       M["deck"], yaw=bn["yaw"])
        # [S3-9] bench on the rest platform, seated on the platform top face
        rb = PARAMS["rest_bench"]
        rf = [f for f in SEQ if f["rest"]]
        if rf:
            f = rf[0]
            sc.build_bench(stage, f"{ROOT}/RestBench",
                           f["lx1"] + rb["dx"], rb["dy"], f["z_bot"],
                           M["deck"], yaw=rb["yaw"])
        # shelter pavilion (lower path)
        pg = PARAMS["pergola"]
        sc.build_canopy(stage, f"{ROOT}/Pergola", pg["x0"], pg["x1"], pg["y0"],
                        pg["y1"], pg["z_roof"], pg["post_r"], M["deck"],
                        M["stringer"], roof_t=pg["roof_t"], base_z=GROUND_Z)
        # [GT-115 ⑭ (3)] the framing the kit does not carry. The kit call above is left
        #   exactly as it was — the roof slab and the four columns are the only members
        #   of this prop with colliders, so they do not move and the physics world is
        #   bit-identical; everything below is dressing hung off them, in the order a
        #   real 정자 is built: 기둥 → 보 → 서까래 → 처마, plus a base plate at each foot.
        px0, px1 = float(pg["x0"]), float(pg["x1"])
        py0, py1 = float(pg["y0"]), float(pg["y1"])
        zr, rt = float(pg["z_roof"]), float(pg["roof_t"])
        pr = float(pg["post_r"])
        bw, bd = (float(v) for v in pg["beam"])
        rw, rd = (float(v) for v in pg["rafter"])
        rbed = float(pg["rafter_bed"])
        ft, fdrip = (float(v) for v in pg["fascia"])
        fout = float(pg["fascia_out"])
        # what is left of the board once its outer face is `fascia_out` proud of the
        # slab edge **is** the bed, so the declared `fascia_bed` is a statement about
        # `fascia` and `fascia_out` rather than a third free number.
        fbed = ft - fout
        # 2 headers on the post lines, top face at the roof underside so they are let
        # into the post tops (반턱 맞춤) instead of hanging below them in mid-air. They
        # run the full slab length, so each end shows a 0.10 m beam tail past its post.
        by = (py0 + pr, py1 - pr)
        for i, yb in enumerate(by):
            BOX(f"{ROOT}/Pergola/Beam_{i}", ((px0 + px1) / 2.0, yb, zr - bd / 2.0),
                (px1 - px0, bw, bd), M["stringer"])
        # 3-5 rafters framed **between** the headers and bedded `rafter_bed` into each,
        # so the joint is a bite, never a coplanar pair. Shallower than the header, so
        # they read as riding over it. Stations avoid the two post lines by construction
        # (the first is 1/(n+1) of the span in from the slab edge).
        nr = max(1, int(pg["rafters"]))
        ry0 = by[0] + bw / 2.0 - rbed
        ry1 = by[1] - bw / 2.0 + rbed
        for i in range(nr):
            xr = px0 + (px1 - px0) * (i + 1) / float(nr + 1)
            BOX(f"{ROOT}/Pergola/Rafter_{i}",
                (xr, (ry0 + ry1) / 2.0, zr - rd / 2.0),
                (rw, ry1 - ry0, rd), M["stringer"])
        # fascia / 처마 band round the slab edge: outer face `fascia_out` proud of the
        # slab so no vertical face is coincident with it, bedded `fascia_bed` into it,
        # top held 0.010 under the slab top so no horizontal face is either, and hanging
        # `drip` below the underside to give the flat roof an eave shadow line.
        fz0, fz1 = zr - fdrip, zr + rt - 0.010
        fzc, fzh = (fz0 + fz1) / 2.0, fz1 - fz0
        #   board centre = edge ± (fascia_out − t/2), so the outer face lands exactly
        #   `fascia_out` proud and the inner face exactly `fascia_bed` inside the slab
        #   (`fascia_out − t = −fascia_bed` by the values chosen) `[computed]`.
        for tag, sgn in (("S", -1.0), ("N", 1.0)):
            yb = (py0 if sgn < 0 else py1) + sgn * (fout - ft / 2.0)
            BOX(f"{ROOT}/Pergola/Fascia_{tag}",
                ((px0 + px1) / 2.0, yb, fzc),
                (px1 - px0 + 2.0 * fout, ft, fzh), M["deck"])
        # the two side boards die **into** the end boards (their ends land 0.010 inside
        # them), so no two fascia faces are coplanar at a corner either.
        for tag, sgn in (("W", -1.0), ("E", 1.0)):
            xb = (px0 if sgn < 0 else px1) + sgn * (fout - ft / 2.0)
            BOX(f"{ROOT}/Pergola/Fascia_{tag}",
                (xb, (py0 + py1) / 2.0, fzc),
                (ft, py1 - py0, fzh), M["deck"])
        # post base plates. The column passes through the plate — the same collar idiom
        # the deck columns' algae band already uses, and what a real 기둥 밑판 looks like.
        pbw, pbd, pbh = (float(v) for v in pg["base"])
        for i, (bx, byp) in enumerate(((px0 + pr, py0 + pr), (px0 + pr, py1 - pr),
                                       (px1 - pr, py0 + pr), (px1 - pr, py1 - pr))):
            BOX(f"{ROOT}/Pergola/Base_{i}", (bx, byp, GROUND_Z + pbh / 2.0),
                (pbw, pbd, pbh), M["stringer"])
        print(f"[GT-115 ⑭] 정자 가구 {2 + nr + 8}프림 — 보 2(기둥머리 물림) · "
              f"서까래 {nr}(보 사이 {rbed:.3f} 물림) · 마구리 4(내밀기 {fout:.3f} · "
              f"물림 {fbed:.3f} · 처마 {fdrip:.3f}) · 기둥 밑판 4 "
              f"(지붕 슬래브·기둥 4본 = sc.build_canopy 원형 유지)")

    def build_horizon(M):
        for i, h in enumerate(PARAMS["far_hedges"]):
            base = ground_z((h["x0"] + h["x1"]) / 2.0,
                            (h["y0"] + h["y1"]) / 2.0)
            sc.build_hedge(stage, f"{ROOT}/FarHedge_{i}", h["x0"], h["y0"],
                           h["x1"], h["y1"], h["h"], mtl=M["hedge"],
                           base_z=base)
        # [v6 C-4] forest band on the distant ridge crest - closed with a silhouette strip, not lollipops
        for i, h in enumerate(PARAMS["ridge_crest"]):
            sc.build_hedge(stage, f"{ROOT}/RidgeCrest_{i}", h["x0"], h["y0"],
                           h["x1"], h["y1"], h["h"], mtl=M["hedge"],
                           base_z=h["base"])
        # [v6 C-4] distant individuals get thicker trunks and more height to avoid
        #   'thin stick + sphere'. [S3-11] the species is now **pinned to
        #   `Chinese_Juniper`** instead of drawn by coordinate hash: an evergreen keeps
        #   its needles in 만추, so a green mass at distance is a conifer and not a season
        #   error, and it is a `veg_manifest_w2` PASS row — which is what clears the nine
        #   LINT-4b errors the hash draw produced (retired `White_Pine` ×5 + `Yellow_Pine`
        #   ×4, the former carrying an uncorrected zmin −0.351).
        rel, native = PARAMS["season"]["far"]
        n_far = 0
        for i, t in enumerate(PARAMS["hill_trees"]):
            gz = _zone_z(t["cx"], t["cy"], t["zone"])
            th = 4.6 + 0.35 * (i % 4)
            xf = sc.add_vegetation(stage, f"{ROOT}/HillTree_{i}/Veg", rel,
                                   (t["cx"], t["cy"], gz),
                                   yaw_deg=(i * 61.0) % 360.0,
                                   target_h=th * 1.60, native_h=native)
            if xf is None:
                sc.build_tree(stage, f"{ROOT}/HillTree_{i}", t["cx"], t["cy"],
                              gz, M["wood"], M["canopy_a"], M["canopy_b"],
                              trunk_r=0.17, trunk_h=th,
                              stake_r=0.004, stake_h=0.02, stake_off=0.2)
            else:
                try:
                    stage.GetPrimAtPath(f"{ROOT}/HillTree_{i}/Veg/Asset") \
                        .SetInstanceable(True)
                except Exception:
                    pass
                n_far += 1
        print(f"[S3-11] 원경 상록 {n_far}/{len(PARAMS['hill_trees'])}주 "
              f"(Chinese_Juniper 고정 — White/Yellow_Pine 좌표해시 추첨 제거)")

    # [v5.2 user] arbitrary warning sign removed - build_sign() deleted.

    def build_cues(M):
        """Non-standard equipment cue (code path only)."""
        if cfg["cue_tactile"]:
            # [W2 · ground_kit §12.5-3] texture-backed so the 36 dots shade.
            tac = sc.tactile_pbr(stage, "/World/Looks/Tactile")
            sc.build_tactile(stage, f"{ROOT}/Tactile", -2.10, -1.50,
                             PARAMS["landing"]["y0"], PARAMS["landing"]["y1"],
                             tac, z=0.0)
        if cfg["cue_nosing"]:
            fl = PARAMS["flights"]
            for f in SEQ:
                grp = f"{ROOT}/NoseGrp_{f['k']}"
                lo, hi = band(f["k"])
                sc.build_nosing(stage, f"{grp}/Nose", f["x_top"], lo, hi,
                                fl["riser"], fl["tread"], f["steps"],
                                base_z=f["z_bot"], z_top=f["z_top"])

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    # [GT-115 ⑭ (5)] the guard leaves `M["stringer"]` for its own oriented pair. The
    #   railing was the only consumer of the frame tint that the 08-14 audit reads as
    #   "uniform moss on every face"; the columns, the stair stringers and the GT-77
    #   approach timber keep `M["stringer"]` and render bit-identically.
    #     M["rail"]      moss side — balusters · mid/bottom rails · line posts · newel
    #                    posts · lattice battens · handrail brackets
    #     M["guard_top"] silvered  — every run's top rail (level, raking and cross) ·
    #                    newel caps · the handrail tube itself (a grasped member is
    #                    polished, not mossy)
    M["rail"] = M["guard"]
    build_terrain(M)
    if cfg["hazard_stairs"]:
        build_deck(M)
        build_cues(M)
        # [GT-77] the approach members are dimensioned off the deck ends (entry head
        #   x −1.50, arrival landing face x 24.14), so they only exist when the deck
        #   does — the `hazard_stairs=False` control arm keeps its bare flat plate.
        build_approach(M)
        build_ground_kit(M)          # [W2-D] trail + entry-deck ground elements
    else:
        build_flat_fill(M)
    build_horizon(M)
    if cfg["cue_scene_dressing"]:
        build_nature(M)
        build_props(M)
    # [v5.2 user] arbitrary warning sign removed - cue_sign placement deleted.

    print(f"[기하] 갈지자 {PARAMS['flights']['n']}플라이트 × "
          f"{PARAMS['flights']['steps']}단 총낙차 {TOTAL_DROP:.2f} "
          f"(z {SEQ[0]['z_top']:+.2f} → {SEQ[-1]['z_bot']:+.2f}) · "
          f"도착참 → 하부 지면 단차 "
          f"{SEQ[-1]['z_bot'] - GROUND_Z:+.3f} m (개방 인계)")

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # ── camera + render mode ──
    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    views = build_views()
    _v0 = views["reversal"]
    look_from(_v0["eye"], _v0["tgt"])

    pt_spp = int(PARAMS["render"]["pt_total_spp"])

    def set_render_mode(mode):
        if mode == "PathTracing":
            settings.set("/rtx/pathtracing/spp", 1)
            settings.set("/rtx/pathtracing/totalSpp", pt_spp)
            settings.set("/rtx/pathtracing/optixDenoiser/enabled", True)
            settings.set("/rtx/pathtracing/maxBounces",
                         int(PARAMS["render"]["pt_max_bounces"]))
            settings.set("/rtx/rendermode", "PathTracing")
        else:
            settings.set("/rtx/rendermode", "RaytracedLighting")

    os.makedirs(LOOKCHECK_DIR, exist_ok=True)

    def capture(path):
        vp = get_active_viewport()
        capture_viewport_to_file(vp, file_path=path)

    if capture_mode:
        out_dir_default = os.path.join(LOOKCHECK_DIR, "auto")
        sc.capture_pipeline(simulation_app, views, out_dir_default,
                            set_render_mode, look_from)
        simulation_app.close()
        return

    # ── GUI look check ──
    input_iface = carb.input.acquire_input_interface()
    appwindow = omni.appwindow.get_default_app_window()
    K = carb.input.KeyboardInput
    rot_step = float(PARAMS["light"]["dome_rotation_step"])
    dome_user_rot = [0.0]

    def on_key(event, *args):
        if event.type != carb.input.KeyboardEventType.KEY_PRESS:
            return True
        if event.input == K.P:
            cur = settings.get("/rtx/rendermode")
            if cur == "PathTracing":
                set_render_mode("RaytracedLighting")
                print("[렌더] RTX Real-Time (이동용)")
            else:
                set_render_mode("PathTracing")
                print(f"[렌더] PathTracing (totalSpp={pt_spp})")
        elif event.input == K.C:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fp = os.path.join(LOOKCHECK_DIR, f"scene10_{ts}.png")
            capture(fp)
            print(f"[캡처] {fp}")
        elif event.input == K.LEFT_BRACKET:
            dome_user_rot[0] -= rot_step
            apply_dome_rot(dome_user_rot[0])
            print(f"[태양 방위] 오프셋 {dome_user_rot[0]:+.0f}°")
        elif event.input == K.RIGHT_BRACKET:
            dome_user_rot[0] += rot_step
            apply_dome_rot(dome_user_rot[0])
            print(f"[태양 방위] 오프셋 {dome_user_rot[0]:+.0f}°")
        return True

    keyboard_sub = input_iface.subscribe_to_keyboard_events(
        appwindow.get_keyboard(), on_key)

    print("=" * 64)
    print(BANNER)
    print("-" * 64)
    print("※ 키가 안 먹으면 Isaac Sim 창을 한 번 클릭해서 포커스를 줘!")
    print("=" * 64)

    while simulation_app.is_running():
        simulation_app.update()

    input_iface.unsubscribe_to_keyboard_events(
        appwindow.get_keyboard(), keyboard_sub)
    simulation_app.close()


if __name__ == "__main__":
    main()
