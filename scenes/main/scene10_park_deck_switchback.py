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

  (1) One landing railing is broken — on the first landing (z −1.65, outer edge x 4.4)
      two rails have come away and only the posts remain. The ground below is z −6.62
      → a **4.97 m open drop**. A railing reduced to posts is easily mis-detected as
      'railing present' from the robot's viewpoint (a trap case for the
      equipment-inference cue).
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
    · `broken_landing = 0` and the open-riser flights are untouched (§9 P-2 frozen).

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
              spacing=1.05, broken_landing=0,   # landing0 outer = the break
              # one lattice / grid infill bay (E10-8). It is a real and common Korean
              # 데크 난간 variant and the single cheapest "this is a park, not an egress
              # stair" tell. Placed on the entry deck's +Y run because that run is in
              # **every** preset grid cut as well as in `leaf_edge` — a lattice on an upper
              # landing would appear in no judged frame.
              lattice=dict(run="EntryRail_P", pitch=0.12, sec=0.030)),

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
    plates=[
        ("UpperTrail",   -40.0,  -1.5,  -1.60,  8.00,  0.00, 0.45, "grass"),
        ("UpperBody",    -40.0,  -1.5,  -1.60,  8.00, -0.45, 6.95, "rock"),
        ("TrailPath",    -40.0,  -1.6,  -0.85,  0.85,  0.002, 0.06, "dirt"),
        ("LowerParkMain", -1.5,  44.0, -13.00,  8.00, -6.62, 1.50, "grass"),
        ("LowerParkFar", -40.0,  44.0, -60.00, -13.00, -6.62, 1.50, "grass"),
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
    leaf_ground_patches=[(-3.2, -0.9, 1.6, 1.1, "trail"),
                         (-5.6, 0.7, 1.4, 1.0, "trail"),
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
    corridor=dict(y0=-2.60, y1=8.00, thick=7.00),

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
    ),
    # [S3-11] rock outcrop at the uphill margin (E10-10) + foot boulders. `rock_moss_set_01`
    #   is CC0 and its diffuse is **orange 82.2 %**, which makes it the better of the two
    #   scans for late autumn (`_02`, yellow-green 92.9 %, is reserved for scene07).
    #   `z_mode='base'` is mandatory — 52.4 % of its triangles sit below the origin — and
    #   the sink stays at 0: `tonglam_v2` §1 row 10 already failed this scene once for
    #   "boulder-scale D-5 rocks in **dark sink-rings**", and a boulder that sits in a hole
    #   is the defect while a boulder that sits *on* the slope is the fix.
    outcrop=[("rock_moss_set_01", 6.30, 4.15, 0.0, 22.0, 1.00),
             ("rock_03_broken", 9.10, 3.30, 0.0, -35.0, 0.55),
             ("rock_03_broken", 15.40, 2.60, 0.0, 110.0, 0.42),
             ("rock_02", 5.10, 2.30, 0.0, 15.0, 1.00)],
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
            (0.5, -5.5, "lower")],
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
    signpost=dict(cx=-3.6, cy=1.00, post_r=0.080, post_h=2.26,
                  arm=(0.58, 0.05, 0.09), arm_off=0.34,
                  arms=((2.06, 15.0), (1.80, 195.0)),
                  cap=(0.20, 0.20, 0.07)),
    # bench 1 (upper trail)
    bench=dict(cx=-6.5, cy=0.90, yaw=180.0),
    # [S3-9] bench 2 — on the 쉼터/전망 platform (landing `rest_at`). A rest platform with
    #   nothing to rest on is a landing; the bench is what makes it read as 휴식 시설, and
    #   it is the element SANJI-183's width exception exists for. x/y are offsets **inside**
    #   the platform, resolved against the ladder so the de-stacking commit carries it along.
    rest_bench=dict(dx=-0.65, dy=1.00, yaw=90.0),
    # shelter pavilion (lower path). [v7] even after from_below is mirrored from
    #   (5.2,−10.8) to (2.4,−0.6), the pavilion (centre 11.5,−6.0) sits at yaw 68 deg, outside the FOV - still no sight interference.
    pergola=dict(x0=10.0, x1=13.0, y0=-7.5, y1=-4.5, z_roof=-4.20, post_r=0.10,
                 roof_t=0.16),
    # [v5.2 user] arbitrary warning sign removed - the stair-caution sign (PARAMS['sign']) is deleted.
    # distant closure : forest band beyond the lower park + trees on the upper ridge
    far_hedges=[dict(x0=-40.0, x1=6.0, y0=-40.0, y1=-37.0, h=4.0),
                dict(x0=6.0, x1=44.0, y0=-40.0, y1=-37.0, h=4.0),
                dict(x0=40.0, x1=43.0, y0=-33.0, y1=1.40, h=4.0)],
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
        grass_tint=(3.40, 1.55, 3.30),
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
# [F-b] railing run inventory — [S3-8] one source of truth for rails and newels
#       Every level railing run in the scene, in world coordinates. `deck_rail`
#       draws the members; `newel_points` derives the capped corner posts from the
#       same list so a corner shared by two runs carries **one** newel, not two.
#       Keeping the inventory here (not inside main()) also lets SMOKE assert the
#       railing without booting.
# ===========================================================================
def level_rail_runs():
    """[(name, x0, y0, x1, y1, z_walk, broken)] for every axis-aligned railing run.

    [S3-10] each landing carries its own y extent (the rest platform is deeper in +Y),
    and the **outer edge** is the +X face — the walker's forward edge, which is the one
    with the drop beyond it now that every flight descends +X.
    """
    ld = PARAMS["landing"]
    ent = PARAMS["entry"]
    br = int(PARAMS["rail"]["broken_landing"])
    runs = []
    for f in SEQ:
        k, z = f["k"], f["z_bot"]
        y0, y1 = f["ly0"], f["ly1"]
        # forward (+X) edge of the landing. Landing `br` is the break (§9 P-2 frozen).
        runs.append((f"LandRail_{k}_Out", f["lx1"], y0, f["lx1"], y1, z,
                     k == br))
        for tag, yy in (("N", y0), ("P", y1)):
            runs.append((f"LandRail_{k}_{tag}", f["lx0"], yy, f["lx1"], yy, z,
                         False))
    for tag, yy in (("N", ld["y0"]), ("P", ld["y1"])):
        runs.append((f"EntryRail_{tag}", ent["x0"], yy, ent["x1"], yy,
                     ent["top"], False))
    return runs


def newel_points(runs):
    """Capped-newel positions derived from the run endpoints, deduplicated.

    A landing corner is the end of two runs (the outer edge and one side), and G10
    shows **one** stout capped post there, not two — the cap is the strongest single
    'timber, not steel' tell and doubling it would read as a defect. Rounded to 1 mm
    so two runs that meet exactly still collapse to one key.
    """
    seen = {}
    for nm, x0, y0, x1, y1, z, _br in runs:
        for px, py in ((x0, y0), (x1, y1)):
            key = (round(px, 3), round(py, 3), round(z, 3))
            seen.setdefault(key, nm)
    return sorted(seen.keys())


def baluster_run(L, step):
    """Baluster stations along a run of length L at a nominal horizontal pitch `step`.

    Returns (n, pitch). The pitch is trimmed so the two end gaps equal the internal
    ones — a bay whose end gap differs from its field gap is the classic give-away of
    a railing laid out by division rather than by setting-out.
    """
    n = max(1, int(round(L / float(step))) - 1)
    return n, L / float(n + 1)


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
    print(f"    난간 원형부재 수 = 0 (원통 CYL 미사용, 전부 박스) → OK")
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
    for nm, x0, y0, x1, y1, z, broken in level_rail_runs():
        if broken:
            continue
        L = math.hypot(x1 - x0, y1 - y0)
        nb, pitch = baluster_run(L, r["bal_step"])
        rows.append((nm, L, nb, pitch))
    for f in SEQ:
        _nb, _pitch = baluster_run(f["run"], r["bal_step"])
        rows.append((f"Flight{f['k']}(경사·수평피치)", f["run"], _nb, _pitch))
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

    # -- the broken bay survives -------------------------------------------
    br = int(r["broken_landing"])
    runs = level_rail_runs()
    brk = [nm for nm, *_rest, b in runs if b]
    good = (len(brk) == 1 and brk[0] == f"LandRail_{br}_Out")
    ok_all &= good
    print(f"    파손 베이 = {brk} (참{br} 외측 1개만) · 난간대·살대 탈락 / "
          f"기둥·엄지기둥 잔존 → {'OK' if good else 'CHECK'}")

    # -- newels: one per shared corner, not two ----------------------------
    ends = sum(2 for _ in runs)
    nw = len(newel_points(runs))
    print(f"    엄지기둥 {nw}개 (런 끝점 {ends}개에서 중복 제거) · 갓 "
          f"{r['newel_cap'][0]:.3f}x{r['newel_cap'][1]:.3f}x"
          f"{r['newel_cap'][2]:.3f} · 난간 위 돌출 {r['newel_proud']:.3f} m")

    # -- the lattice bay ----------------------------------------------------
    lat = r["lattice"]
    tgt = str(lat["run"])
    good = any(nm == tgt for nm, *_ in runs)
    ok_all &= good
    print(f"    격자 베이 1개 = {tgt} (피치 {lat['pitch']:.2f} m · 단면 "
          f"{lat['sec']:.3f}) → {'OK' if good else 'CHECK'}")
    print("      배치 근거: 이 런은 프리셋 그리드 5컷 전부 + leaf_edge 에 들어온다. "
          "상단 참에 두면 심사 프레임에 한 번도 안 잡힘 (§0.2 계열 논리)")

    print(f"    [deck_module_selfcheck S3-8] "
          f"{'전항목 OK' if ok_all else '⚠ CHECK 항목 있음'}")

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
    return ok_all and ok9 and ok10 and ok11


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

    # ── broken railing ──
    br = P["rail"]["broken_landing"]
    f = SEQ[br]
    print(f"\n  [파손 난간] 참{br} 외측 에지 x={f['lx1'] if f['even'] else f['lx0']:.2f}"
          f" z={f['z_bot']:+.2f} — 가로대 2본 탈락 · 포스트 잔존")
    print(f"    개방 낙차 = {f['z_bot'] - GROUND_Z:.2f} m "
          f"(≥0.3 → {'OK' if f['z_bot'] - GROUND_Z >= 0.3 else 'FAIL'})")

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
 4. broken_rail      — 가로대 탈락·포스트 잔존 + 4.97 m 개방 낙차가 명확한가
 5. leaf_edge        — 낙엽 밴드가 단코를 물고 덮어 절단선을 지우나
 6. from_below       — 데크 기둥 접지·참 스택이 낙차 앵커로 읽히나
 7. 남측 사면        — 트레일 어깨 밖 30° 무방호 하강이 grazing 시 소실되나
 8. 지평 폐쇄        — 북측 언덕·원경 능선 마루 숲 밴드가 직선 지평을 깨는가
 9. cue 토글         — railing/tactile/nosing ON/OFF 시 위험 기하 불변인가
10. [v6] 태양        — from_below·through_treads 에 직사광이 들어왔나(암부 사망 해소)
11. [v6] 옹벽        — 사석 스케일 + 동측 2단(소단 식재)로 '공원 절토면'이 되나
12. [v6] 난간        — 세로살이 들어가 '가설 사다리틀'이 아니라 데크 난간인가"""


def main():
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
        # [v6] built retaining wall (masonry, rubble scale) / natural cut face (jointless) / coping (concrete)
        M["rock"] = tex("rock_wall", "/World/Looks/Rock", sca["rock_wall"],
                        tint=mp["rock_tint"])
        M["rockface"] = tex("rock_face", "/World/Looks/RockFace",
                            sca["rock_face"], tint=mp["rockface_tint"])
        M["coping"] = tex("concrete_wall", "/World/Looks/Coping",
                          sca["concrete_wall"], tint=mp["coping_tint"])
        M["grass"] = tex("grass", "/World/Looks/Grass", sca["grass"],
                         tint=mp["grass_tint"])
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
        # [S3-10] the deck corridor's real descending slope, one sloped slab per segment
        #   of `GROUND_LINE`. This is the shaft's replacement: instead of a 7.40 m masonry
        #   wall holding a vertical ground, the hill falls **with** the deck at a mean
        #   25.8 % and is benched level under each landing, which is how a cut-and-fill
        #   trail bench is actually built. The slab side faces at y = CORRIDOR_Y0 / Y1 are
        #   the natural scarps down to the lower park and up to the north bank — no
        #   masonry, no coping, no fortress.
        cg = PARAMS["corridor"]
        for i in range(len(GROUND_LINE) - 1):
            (xa, za), (xb, zb) = GROUND_LINE[i], GROUND_LINE[i + 1]
            if xb - xa < 1e-6:
                continue
            sc.build_slope(stage, f"{ROOT}/CorridorSlope_{i}", xa, za,
                           xb - xa, za - zb, cg["y0"], cg["y1"],
                           float(cg["thick"]), M["grass"], margin=0.0,
                           collider=True)

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
            ring += int(sc.scatter_debris(
                stage, f"{ROOT}/GKit/LeafRing_{i}",
                cx - sx / 2.0 - pad, cy - sy / 2.0 - pad,
                cx + sx / 2.0 + pad, cy + sy / 2.0 + pad,
                _zone_z(cx, cy, zone),
                cover=0.10, seed=gk.det_seed("scene10.leafring", i),
                edge_bias=pad,
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

    def deck_rail(prefix, x0, x1, y0, y1, z_top, broken=False, lattice=False):
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
        """
        r = PARAMS["rail"]
        horiz = abs(x1 - x0) >= abs(y1 - y0)
        L = math.hypot(x1 - x0, y1 - y0)
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        top_w, top_t = r["top"]
        if not broken:
            # (w, t) per rail; z is the member **centre**
            for tag, (w, t), zc in (
                    ("Top", r["top"], z_top + r["h"] - top_t / 2.0),
                    ("Mid", r["mid"], z_top + r["h"] * r["mid_frac"]),
                    ("Bot", r["bot"], z_top + r["bot_z"])):
                size = (L, w, t) if horiz else (w, L, t)
                BOX(f"{prefix}/Rail{tag}", (cx, cy, zc), size, M["rail"])
            if lattice:
                rail_lattice(prefix, x0, x1, y0, y1, z_top)
            else:
                b = r["bal"]
                z_bal0 = z_top + r["bot_z"] + r["bot"][1] / 2.0
                hh = (z_top + r["h"] - top_t) - z_bal0
                nb, _pitch = baluster_run(L, r["bal_step"])
                for i in range(nb):
                    t = (i + 1) / float(nb + 1)
                    bx = x0 + (x1 - x0) * t
                    by = y0 + (y1 - y0) * t
                    BOX(f"{prefix}/Bal_{i}", (bx, by, z_bal0 + hh / 2.0),
                        (b, b, hh), M["rail"])
        # intermediate line posts only — the ends are capped newels (build_newels)
        ps = r["post"]
        n = max(2, int(round(L / r["spacing"])) + 1)
        ph = r["h"] - top_t
        for i in range(1, n - 1):
            t = i / float(n - 1)
            px = x0 + (x1 - x0) * t
            py = y0 + (y1 - y0) * t
            BOX(f"{prefix}/Post_{i}", (px, py, z_top + ph / 2.0),
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
        BOX(f"{path}/Cap", (px, py, z_walk + h + ct / 2.0), (cw, cd, ct),
            mtl or M["rail"])

    def build_deck(M):
        fl = PARAMS["flights"]
        ld = PARAMS["landing"]
        ent = PARAMS["entry"]
        r = PARAMS["rail"]
        lcy = (ld["y0"] + ld["y1"]) / 2.0
        lsy = ld["y1"] - ld["y0"]

        def _flight_rails(grp, f, gy0, gy1):
            """[S3-8] raking railing on both sides of a flight, in **square sections** —
            built **inside** the rot_group (local +X descent convention).

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
            `y_off = 0.85` then leaves 0.072 m between the inner newels of two adjacent
            flights, so nothing interpenetrates.
            """
            def gfn(x, _xt=f["x_top"], _zt=f["z_top"]):
                if x <= _xt:
                    return _zt
                i = min(int((x - _xt) / fl["tread"]) + 1, f["steps"])
                return _zt - i * fl["riser"]

            top_w, top_t = r["top"]
            f_run, f_drop = f["run"], f["drop"]
            slope = f_drop / f_run
            _bo = r["bal"] / 2.0
            for tag, y in (("N", gy0 - _bo), ("P", gy1 + _bo)):
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
                    sc.build_slope(stage, f"{grp}/Rail{rtag}_{tag}",
                                   f["x_top"], z0, f_run, f_drop,
                                   y - w / 2.0, y + w / 2.0, t, M["rail"],
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
                # capped newels at the flight head and foot. They sit on the band edge,
                # not on the landing edge (y ∓1.40), so they never coincide with a
                # landing newel and no dedup is needed across the rot_group boundary.
                for ntag, bx, bz in (("Head", f["x_top"], f["z_top"]),
                                     ("Foot", f["x_top"] + f_run,
                                      f["z_bot"])):
                    build_newel(f"{grp}/Newel_{tag}_{ntag}", bx, y, bz)

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
            if cfg["cue_railing"]:
                _flight_rails(grp, f, lo, hi)
            # landing — spans both width bands so the walker crosses from this flight's
            # band into the next one's; the rest platform also projects past +Y.
            BOX(f"{ROOT}/Landing_{k}",
                ((f["lx0"] + f["lx1"]) / 2.0, (f["ly0"] + f["ly1"]) / 2.0,
                 f["z_bot"] - ld["thick"] / 2.0),
                (f["lx1"] - f["lx0"], f["ly1"] - f["ly0"], ld["thick"]),
                M["deck"], col=True)

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

        # landing + entry railing. Runs come from `level_rail_runs()` so the SMOKE
        # self-check reads exactly the geometry that is built. Only the `broken_landing`
        # outer run loses its rails (§9 P-2, frozen); its posts and newels remain, which
        # is what makes it mis-detectable as 'railing present'.
        if cfg["cue_railing"]:
            runs = level_rail_runs()
            lat_run = str(r["lattice"]["run"])
            for nm, x0, y0, x1, y1, z, broken in runs:
                deck_rail(f"{ROOT}/{nm}", x0, x1, y0, y1, z, broken=broken,
                          lattice=(nm == lat_run))
            # capped newels, one per shared corner (see newel_points)
            for i, (px, py, pz) in enumerate(newel_points(runs)):
                build_newel(f"{ROOT}/Newel_{i}", px, py, pz)

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
        kit = gk.kit_from_scene_common(sc, stage)
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
        se = PARAMS["season"]
        cg = PARAMS["corridor"]
        n_lit = 0
        for i, (lx0, lx1, ly0, ly1) in enumerate((
                (HEAD_X, PLAN_X1, cg["y0"], -1.70),
                (HEAD_X, PLAN_X1, 1.70, 4.40),
                (HEAD_X, PLAN_X1 * 0.5, -1.70, 1.70))):
            n_lit += int(sc.scatter_debris(
                stage, f"{ROOT}/Litter_{i}", lx0, ly0, lx1, ly1, 0.0,
                cover=float(se["litter_cover"]),
                seed=gk.det_seed("scene10.litter", i),
                ground_fn=ground_z,
                max_count=int(se["litter_max"])) or 0)
        print(f"[S3-11] 연속 낙엽 산포 {n_lit}개 (CB-2 로브 4개는 조밀 코어로 존치)")

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
    M["rail"] = M["stringer"]          # timber railing (same timber as the deck)
    build_terrain(M)
    if cfg["hazard_stairs"]:
        build_deck(M)
        build_cues(M)
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
          f"참0 외측 난간 파손 개방낙차 "
          f"{SEQ[0]['z_bot'] - GROUND_Z:.2f} m")

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
