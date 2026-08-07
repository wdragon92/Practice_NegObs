# -*- coding: utf-8 -*-
"""
scene06_overpass_spiral.py — NegObs synthetic scene 6: pedestrian overpass spiral entry stair
(Isaac Sim 4.5) · new in v5 (old scene06_spiral_towerstone → scenes/archive_v3/)

Type    : R1 urban pedestrian overpass, circular spiral entry (inherits the curvature self-occlusion axis)
Spec    : Docs/briefs/multi_scene_brief_v5.md §R1 + shared layer section
Shared  : scene_common.py (build_helix_steps / build_arc_steps / build_helix_ramp /
          build_rot_group / build_straight_stairs / build_tactile)
World   : shares the overpass convention with scene11_footbridge_stairs.py
          (roadway asphalt 0.045 · kerb 0.15 · sidewalk paving_interlock · street lamps)

────────────────────────────────────────────────────────────────────────────
Hazard (= the reality of falling short of code)
  A pedestrian overpass (deck z=+5.0) over a 4-lane crossing, at its circular spiral
  entry. The outer pipe railing of the spiral **is missing over the upper 90° arc
  (azimuth 180~270°)**, leaving only the posts. The open edge of that arc (r=3.3) is
  a 3.46~4.81 m drop to grade (mean 4.14 m) with no guard at all. The railing survives
  intact over the remaining 210°, so it is easily misread as "fully equipped".
  Second axis — from ground grazing (robot h0.3) the spiral reads as a **cylindrical
  silhouette** in which the central column and the stair ribbon overlap, so the spiral
  descent (the 5 m interior void + the entry passage) is concealed.
  Third — the annular void inside the spiral (r 0.5~1.5, depth 5 m) has an inner
  railing but no kick plate, so it is open at robot height.
  [GT-68 · 08-05] Axes 1 and 3 above are kept as written for history but are **no longer
  the build**: axis 1 went with the 08-05 continuous-guard doctrine, and axis 3 goes with
  the glazed guard landed here (shoe + pane from the tread up, both runs). Neither axis
  was ever a GT registry entry — the drop edges, the 5.005 m well drop and every walking
  surface are untouched by this row.

  [GT-76 · 08-06] Both vertical accesses rebuilt for craftsmanship, nothing else. The
  gallery verdict was that the spiral is sloppy, that its edges are unfinished and that the
  opposite stair does not read as part of the same overpass. Five members changed and every
  one of them is a guard prim under `cue_railing` (the one exception is the north stair's
  cheek, which is demoted from a 0.95 m parapet to the stringer upstand the new guard stands
  on): the cap/shoe/upstand are ONE bent member per run instead of 13 chords; a raked
  stringer upstand carries the guard clear of the stepped tread edge; panes are housed in
  shoe and cap; every run terminal is a newel under a bronze head; the deck's floating tube
  handrail is gone and the cap line is continuous, 0 mm at all three junctions.
  **GT invariance re-verified**: the SMOKE front profile (y −13.0…−18.0), the h0.3
  concealment table, the camera-collision set and every sight-line block fraction are
  byte-identical to the pre-row run [measured, diff of the SMOKE logs].

  [GT-92 · 08-07] Passage un-blocking — two prim-level blockages, nothing else. The
  gallery read "the stair connection at the overpass is blocked" and both causes were
  real, each a blind spot of an earlier row:
  (1) GT-76 cut the deck rail at the landing newel but still ran the WEST rail from the
  slab corner, so its apron-return bay (kick + pane + cap on the x 2.0 line,
  y −13.000…−10.128) stood across the deck↔west-lobe crossing — the ONLY floor route to
  the spiral head (step 0 is entered over the az-180 ray at x 0.20…2.00, wholly west of
  that line). The bay guarded no edge (floor z 5.000 on both sides of the line); it is
  now a formal opening between two bronze-headed newels (DeckNewel_S0 at (2.0, −10.128),
  shared with the arriving landing guard · the spiral's own a0 inner newel at
  (1.94, −13.0), which also retires the near-coincident DeckNewel_E0 six centimetres
  away). The EAST apron bay stays closed on purpose: the east lobe's az-0 radial edge is
  unguarded over the spiral (drop 2.9…5.0 m) and may not be exposed by this R-3 row.
  (2) The north verge tree row carried (3.6, 20.2) — a dropped minus sign against the
  south row's (−3.6, −20.2) — standing mid-flight-B (tread top 1.160 there), trunk
  through the treads, canopy over x 2.5…4.7 = 73 % of the stair width [measured]. Moved
  to (−3.4, 20.2); `_corridor_hits` now asserts the north stair corridor too.
  Drop registry, well depth 5.005, every walking-surface z, both spiral guard runs, the
  landing lobes and the h0.3 concealment table are untouched; the W4 carry-over
  (robot-height opening closure, GT-68) is not an input of any change here.

GT drop invariance: the cue_railing toggle only turns railing prims on and off. The
  transforms of spiral, landing, deck and column, and the riser / radius / azimuth
  values, never change under any toggle.

────────────────────────────────────────────────────────────────────────────
Walking continuity self-check table (entry → up → deck → down → exit)

  #  Segment                      Coordinates (world, m)            Step
  ─  ───────────────────────────  ────────────────────────────────  ──────
  1  South sidewalk approach      (x −30…0.2, y −13.0, z −0.005)    —
  2  Spiral lower entry passage   az 120~180° at grade, no steps    0.000
     (spiral centre C = (3.5, −13.0), piloti space under the landing)
  3  Step up onto bottom step 25  az 108.46~120°, top z=+0.008      0.013
  4  Spiral up 26 steps/25 rises  riser 0.192 × 25 = 4.800          0.192/step
     (centre angle of step i = 180 + (i+0.5)·11.53846°, top = 5.0 −(i+1)·0.192)
  5  Top step 0 → round landing   step 0 top 4.808 → landing 5.000  0.192
     (landing = north-half annular landing r 0.48…3.30, clipped at the deck
      edge to azimuth 0~62.964° and 117.036~180° — GT-29)
  6  Landing → overpass deck      landing 5.000 → deck 5.000        0.000
  7  Deck run                     x 2.0…5.0, y −13.0…13.0, z 5.0    —
     (clearance over the roadway y −8…8 = 4.65 −(−0.15) = 4.80 m)
  8  North stair A, 13 steps      y 13.0…16.9, z 5.0 → 2.504        0.192/step
  9  North mid-landing            y 16.9…18.3, z 2.504              0.000
 10  North stair B, 13 steps      y 18.3…22.2, z 2.504 → 0.008      0.192/step
 11  North sidewalk exit          (x 2…5, y 22.2…30, z −0.005)      0.013

  Total rise = total fall = 4.992 m. Max step 0.192 (normal riser), joints ≤0.013 m.
  [W3 S06] the 0.190 / 0.002 pair above was the old 4.998 landing: one short riser at the
  top of the flight and a 2 mm lip at the deck joint. GT-29's +2 mm removes both — the
  flight now runs 26 identical 0.192 risers and the landing is flush with the deck.
  [GT-92] Row 6 was true in z and false in plan until this row: the deck rail's WEST
  apron-return bay stood on the x 2.0 line over y −13.000…−10.128 — the only stretch
  where deck slab (east) and landing west lobe (west) meet at one floor — so rows 5/6
  connected on paper and were fenced in build. That bay is now the formal opening (see
  `build_deck_rail`). Row 11 as written is STALE and left for the history: the built
  sidewalk ends at yn1 19.0 and the flight foot (y 22.2) lands on lawn z −0.16
  (Δ 0.168 m, 3.2 m past the pavement). Not repaired here — new pavement at the foot
  is a ground-plan / drop-registry change beyond this row's R-3 scope; recorded as a
  residual grounding defect owed its own row.

────────────────────────────────────────────────────────────────────────────
W3 S06 — the G6 rebuild (user: "정체성 그렇게 안 겹치도록 이미지 참조해서 나선 구조 고쳐줘")
  Target image: `Docs/reference_photos/Generated Image - Scene06.jpg` (G6), **summer**,
  high sun, blue sky — pinned per §7 ruling 8; every deciduous element is leaf-ON and no
  `build_tree(bare=)` call belongs in this scene.
  G6 settles three open questions and all three are executed here:
    1. the spiral is a **smooth continuous helicoid soffit** with **scalloped tread ends**,
       not a stack of boxes under an interpolated fascia ribbon → K4(d) true annular
       sectors (`mesh=True`) + `top_face=True` soffit + per-step fascia;
    2. the railing is **bronze/brown horizontal tube, 4 rails** — against scene11's
       painted-steel vertical bar. This pair IS the identity separation the user asked
       for, so it is geometry and colour, not a texture swap;
       **[GT-68 · 08-05 supersedes the section, not the identity]** the deck run had
       already gone to glass under a bronze cap (`DeckGlass_*`), so the tube survived
       only on the spiral and the one structure carried two guard languages. Every run
       is now the same three parts — steel shoe · laminated pane · **bronze cap** — and
       the bronze is what still separates 06 from scene11's painted steel;
    3. the deck is carried on **white tapered V-form pillars**, not plain cylinders.
  Plus G6's foreground boundary set (timber road guardrail with yellow reflective bands,
  green mesh fence, 야면석-edged bed with ornamental grasses and a tripod-staked sapling)
  and S06-B's unit-block kerb line. No humans, no vehicles (standing rule; G6's are
  composition only — and G6 in fact shows neither).

────────────────────────────────────────────────────────────────────────────
4-box opening convention: this scene has no cavity (pit) piercing the ground — the
  spiral and deck are entirely above-grade structures, so laying the sidewalk /
  roadway slabs as continuous boxes does not violate §A-3 (the case of ground
  covering a cavity never arises).

────────────────────────────────────────────────────────────────────────────
Camera axis note [v6 verdict revision · supervisor approved — scene11 precedent]
  v6 RT verdict: all 9 grid shots stood on the **ground sidewalk** (eye y=−13,
  z 0.3~1.8), so there was no drop in front of the robot (an ascending stair, if
  anything). grid_views is the convention of "putting the drop boundary in the centre
  of the frame", so the grid is moved onto the **deck run axis**.
    origin = deck south end = edge of the spiral opening (well) (3.5, −13.0, z 5.000)
    travel = −Y (north → south, deck centreline x=3.5) · eye = (3.5, −13+d, 5.0+h)
  On this axis the profile straight ahead of the robot (x=3.5, y decreasing) is
    y −13.0…−13.5 column-head top z 5.000 (**flush with the deck — the basis of the continuity misread**)
    y −13.5…−14.5 annular void (inner r 0.5…1.5) → ground −0.005 = **drop 5.005 m**
    y −14.56     inner guard (cap top 4.506 — 0.494 m below the deck face)
                 [GT-68] was y −14.44 / top 4.456 when the inner run stood at r 1.44
    y −14.5…−16.3 spiral treads (near azimuth 270°, top ≈3.46) = 1.54 m below the deck
    y −16.24     outer guard — **azimuth 270° is the edge of the damaged arc (180~270)**
                 [GT-68] the −16.36 printed here was stale from outer_r 3.36 (GT-6 took it
                 to 3.24); the guard radius itself is unchanged by this row
    y < −16.3    ground −0.005 = drop 5.005 m
  So the damaged-railing arc (180~270°) enters the centre-to-right of the frame and the
  GT drop is present in every h0.3/h0.9/h1.8 shot. The ground approach (the old grid
  axis) is preserved as the mise-en-scene shots `ground_graze` / `ground_approach`.

Camera / sun alignment [v7 verdict revision — judge_v7_rt_A.md §4]
  v6 **moved the grid axis only and left the sun where it was.** As a result the lit
  face of the new sight line (−Y, normal +Y) fell to lambert −0.273 at sun az 205 =
  fully backlit, leaving `h1.8_d2` (mean 26.3·dark 81.3 %)·`h0.9_d2`·`h1.8_d5`
  unreadable and dropping the upper 70 % of `deck_entry` into shadow. v7 fixes all
  three together.
  (1) **sun az 205 → 145** (offset 171.5 → 111.5) : grid lit face +0.370, every
      mise-en-scene shot lambert +0.264~+0.545 = front lit (SMOKE [v7 sun] prints a
      per-shot table).
      Convention — **|lit-face normal of the sight axis − sun az| ≤ 60°** (55° here).
  (2) **lower the d2 pitch** : the depression to the edge (h0.9 24.2° / h1.8 42.0°)
      exceeded the bottom of the frame (pitch −10° → 28°), so the near ground fell
      entirely outside the frame → h0.9_d2 −20° · h1.8_d2 −28°. h0.3_d2 stays at −10°
      (keeping the horizon = the concealment axis).
  (3) **`spiral_up` pitch +11 → +19°** (tgt z 2.15 → 2.75) : the top of the frame is
      capped by the landing soffit, cutting the "60 % distant brick facade".
  (4) **`overview` viewpoint (−16,−28,14) → (−20,−16,15)** : turns the lit face killed
      by (1) (normal 228°, +0.074) to normal 207° (+0.303). Spiral, deck, roadway and
      north stair staying inside the frame is checked by yaw / depression angle.

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene06_overpass_spiral.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python scene06_overpass_spiral.py
Smoke early exit (before boot): NEGOBS_SMOKE=1 python scene06_overpass_spiral.py

Coordinates: Z-up, m. Walk axis +X (ground approach) · roadway axis +X · deck axis +Y.
  Spiral centre C=(3.5, −13.0), deck centreline x=3.5, roadway centre y=0, sidewalk top −0.005.
"""

import os
import sys
import math
import json
import datetime

import numpy as np

import scene_common as sc
import ground_kit as gk
import infra_kit as ik
import props_kit as pk


# ===========================================================================
# [A] SCENE_CONFIG - standard 7 keys. Only hazard_stairs toggles geometry.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False -> remove spiral/landing/deck/stairs (flat sidewalk control)
    "cue_railing":        True,   # spiral railing (upper 90 deg missing variant) + deck railing
    "cue_tactile":        False,  # [v5.2 user] tactile paving is rare in reality - default OFF (path kept for ablation)   # urban-practice scene - tactile band at the stair head default ON (brief v5)
    "cue_material_break": True,   # kerb (granite)·lane paint·deck edge band
    "cue_nosing":         False,  # spiral nosing non-slip band (optional)
    "cue_sign":           False,  # [v5.2 user] arbitrary warning sign removed - nothing placed (key reserved only)
    "cue_scene_dressing": True,   # roadway·street lamps·street trees·bus stop pole·distant buildings
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # --- spiral stair (brief R1 dimensions as-is) ---
    #   sweep 300 deg / 26 steps -> step_deg = 11.538462 deg, riser 0.192 -> drop 4.992
    #   a0=180 deg : the deck south-end corner (= the y=−13 line through the spiral
    #     centre) is chosen to coincide exactly with the azimuth-180 deg radial.
    #     Step 0 [180,191.54] touches the landing (north half 0~180) at the boundary;
    #     the last step 25 [108.46,120] sits at grade **below** it, so azimuth 120~180 deg is left wholly free as the entry passage.
    #   [W3 S06 · GT-6 pilot] `mesh=True` turns the treads into **true annular sectors**
    #     (`scene_common._annular_sector_mesh`, landed default-OFF at `5ceb76a`). The box
    #     convention approximated the sector with an axis-aligned Cube given the OUTER
    #     chord, so the solid overshot the design rays at r_in by `margin*r_out/r_in`
    #     = **7.08125x** — 190.9 mm of tooth, in 24 teeth, on the landing seam. The sector
    #     mesh is exact at both rays, which is also what makes the **chord margin 1.03 -> 1.000**
    #     term of GT-6 real rather than nominal: a true sector needs no wedge-gap cover.
    spiral=dict(cx=3.5, cy=-13.0, r_in=1.5, r_out=3.3, a0=180.0, sweep=300.0,
                n=26, riser=0.192, z0=5.0, base_drop=0.5,
                mesh=True, arc_seg=6),
    # [W3 S06 · G6 · GT-6 "fascia stepped"] The v6 fascia was a **continuous helical ribbon**
    #   whose top line was linearly interpolated while the treads step, so it rode
    #   +0.154 m above the tread at each step start and −0.038 m below it at each step end —
    #   a ±154/−38 mm sawtooth, 26x round the helix, and (measured on HEAD, `gt_probe.py`)
    #   the ribbon **won the top-face sample** at r 3.15…3.25 over most of the sweep, i.e. it
    #   was standing proud of the walking surface it was supposed to trim.
    #   G6 shows the opposite: a **smooth continuous helicoid soffit** with the **scalloped
    #   tread ends** exposed on the outer rim. So the ribbon becomes **one annular sector per
    #   step**, its top pinned 2 mm BELOW that step's own tread face (the tread keeps the
    #   walked surface) and its outer radius flush with `r_out` — the scallop of G6, and a
    #   sawtooth of exactly 0 because there is no longer an interpolated line to sawtooth.
    fascia=dict(r_in=3.20, r_out=3.30, drop_below=0.002, thick=0.62, arc_seg=6),
    #   soffit : one lower helical slab (RC spiral slab) — G6's continuous helicoid soffit.
    #     `top_face=True` is the NF-1 fix (`scene_common.build_helix_ramp`): the builder
    #     places the box CENTRE and then tilts about it, so the surface it was asked to put
    #     at z_top actually landed (t/2)(1/cos−1) high and (t/2)sin off along the tangent.
    #     Measured on this ring at HEAD: 63.0 mm tangential, +13.03 mm lift.
    soffit=dict(r_in=1.46, r_out=3.34, thick=0.34, drop=0.42,
                seg_per_deg=0.5, top_face=True),
    # central column r0.5 (brief). The 1.0 m annular void between it and r_in 1.5 is
    #   guarded by the inner railing but has no kick plate - open at robot height (extra hazard).
    column=dict(r=0.5, z_bot=-0.30, z_top=5.00),
    # circular landing atop the spiral (= widened deck south end). North half only - south half is stair.
    #   r_in 0.48 : embedded 2 cm into the column (r0.5) to avoid coplanarity.
    #   [W3 S06 · GT-6, the row's own +2 mm] top_z **4.998 -> 5.000**. The 2 mm offset bought
    #     z-fighting immunity against the deck at the price of a 2 mm step in the walked route
    #     (continuity table row 6). It is only needed where landing and deck are **coplanar in
    #     plan**, and `clip=True` below removes exactly that region, so the two land together:
    #     the clip is what makes the +2 mm safe, and the +2 mm is what makes the joint flush.
    #   [W3 S06 · GT-6 "landing azimuth clipped at the deck edge"] the north-half annulus ran
    #     the full 0…180 deg and therefore interpenetrated the deck slab over **9.196 m²**
    #     (re-derived this session; the intake's 9.9 m² is the same defect at coarser bounds).
    #     The deck edges x = 2.0 / 5.0 meet the landing rim r_out = 3.30 at
    #     `acos(1.5/3.30)` = **62.964 deg**, so the landing is clipped to the two lobes
    #     [0, 62.964] and [117.036, 180] and the wedge between them is left to the deck.
    #     **No hole is opened**: every point of the removed wedge has |x−3.5| <= 1.5 and is
    #     therefore deck. Residual overlap (the two slivers where a lobe still passes under the
    #     slab at r < 3.30) measured **4.166 m², −54.7 %**; closing it needs either a deck
    #     south-end move or a non-annular primitive — see the report, it is declared, not hidden.
    landing=dict(r_in=0.48, r_out=3.30, a0=0.0, a1=180.0, seg=24,
                 top_z=5.000, base_z=4.498, clip=True, mesh=True, arc_seg=6),
    # --- overpass deck (width 3, runs along y) ---
    #   [v6 verdict (1)] the old build was one unsegmented panel per side -> it read as a **closed box girder**.
    #   Real overpasses segment every 2~3 m at the posts, alternating sound panels / open bars. rail_bay below
    #   segments the bays and leaves odd bays **open (vertical bars)** so what lies beyond the deck shows
    #   through (essential for both judging and training now that the grid runs along the deck).
    # [GT-76] `panel_h` 0.95 -> **1.040**. The level cap top is `panel_h + cap_h`, so this
    #   puts every level run's cap at **1.100 m** over its own floor and lets the raked runs
    #   meet it at exactly 0 mm (see `railing.rail_h`). It also makes the cap the guard head
    #   in its own right: the deck used to reach its 1.25 m barrier height only through a
    #   separate round tube floating 0.240 m above the cap on over-long posts, and that tube
    #   ended in a raw cut circle in mid-air at both deck ends [measured, `pt_noon_overview`].
    #   `parapet_h` is retired with the tube and kept only so the history reads.
    deck=dict(x0=2.0, x1=5.0, y0=-13.0, y1=13.0, z_top=5.0, thick=0.35,
              parapet_h=1.25, parapet_t=0.08, panel_h=1.04),

    # === [W2-D ground_kit] P9 bridge_deck (spec §5.3 row "06 deck") ========
    # The h0.3 grid of this scene runs **along the deck**: origin = deck south
    # end = spiral well rim (3.5, -13.0, 5.000), travel -Y (spec §2.3 lists 06
    # explicitly). So the plan is given origin=(3.5,-13,5), axis="-y" and the
    # drop edge at s=0; the deck itself is the decorated surface, z = 5.000.
    #  * expansion joints at y = -9 / 0 / +9 (spec §5.3), driven by step_y=9.0.
    #    step_x is switched off: on this axis a constant-x line is longitudinal,
    #    not a bridge joint. NOTE - ground_kit tags constant-y lines "long" and
    #    constant-x lines "cross" regardless of `axis`, so on a -Y scene the
    #    line class is inverted and B7 does not see these joints. They are safe
    #    anyway (measured: the y=-9 joint is 33 rows @1080 from the edge row at
    #    d10, floor 16), but the mis-tagging is reported as a kit defect.
    #  * 4 scuppers at the deck edges, 0.35 m in from the parapet face.
    #  * the non-slip coating band (spec §5.3, width 2.0) is carried by `wear_lane`
    #    with an explicit centre line: `build_membrane` is a P6 builder whose
    #    region is the whole trimmed plan area, so it cannot express a 2.0 m
    #    band on a 3.0 m deck. Its albedo target 0.14~0.22 is a T1 material
    #    matter in any case (spec §4.4).
    #  * NO tactile: spec §12.4 puts scene06 on **hold** (the "full width" of a
    #    helical flight is undefined; supervisor call, filed with M10), so it is
    #    absent from TACTILE_SITES and ground_kit would raise B11 on it.
    gkit=dict(joint_step=9.0, wear=((3.5, -12.2), (3.5, -0.5)), wear_w=2.0,
              gully=[(2.35, -11.0), (4.65, -11.0), (2.35, -4.0), (4.65, -4.0)]),
    # [GT-68] `glass_t` was a literal 0.019 inside `build_deck_rail`. It is lifted into
    #   PARAMS unchanged because the spiral and landing runs now read the SAME key — the
    #   section is shared by construction, not by two copies of the same number.
    # [GT-76] `post_h` 1.28 -> **1.100** = the level cap top: with the floating tube gone the
    #   mullion has nothing to carry above the cap, and a post standing 0.270 m proud of the
    #   cap is what made the deck run read as a different product from the stair runs
    #   [measured, `pt_noon_overview` junction crop]. `glass_set` / `cap_grip` are the depths
    #   the pane is HOUSED by: the pane used to start exactly at the shoe top and stop exactly
    #   at the cap bottom, i.e. two coplanar faces per bay and a pane that reads as laid
    #   against the metal instead of set into it.
    rail_bay=dict(post_t=0.10, post_h=1.10, n_bay=13, joint=0.05,
                  kick_h=0.12, cap_h=0.06, cap_over=0.03, glass_t=0.019,
                  glass_set=0.035, cap_grip=0.025,
                  baluster_r=0.018, n_baluster=5),
    #   deck support columns - they land on the sidewalk outside the kerb (y +-8.0…8.6). y +-9.0 is
    #   0.7 m clear of the spiral outer edge (C.y −13 + r 3.3 = −9.7), so no interference.
    # [W3 S06 · G6 point 3] the deck is carried on white **tapered "V"-form pillars**, not on
    #   plain cylinders. This is the third design question G6 settles outright and it is the
    #   single most recognisable thing about the real structure: two splayed legs rising from
    #   one small footing to the deck soffit, each tapering as it rises. Modelled as `n_seg`
    #   stacked cylinders per leg with a linear radius taper (a Cylinder cannot taper), tilted
    #   about X so the splay opens along the deck axis. `r` is kept as the FOOTING radius so
    #   the camera-collision AABB and `_solid_at` keep a single conservative envelope.
    deck_posts=dict(x=3.5, ys=(-9.0, 9.0), r=0.35, z_bot=-0.30,
                    splay=0.95, leg_r0=0.30, leg_r1=0.17, n_seg=5),
    # --- north entry stair (rot_group 90 deg - local +X descent becomes world +Y descent) ---
    #   rotation: (x,y) -> (16.5 − y, 9.5 + x)  [pivot (3.5,13.0), +90 deg]
    #   local y 11.5…14.5 -> world x 2.0…5.0 (matches the deck width)
    #   local x 3.5…12.7 -> world y 13.0…22.2
    # [GT-76 · gallery "반대편 오르막 계단도 마찬가지 / 하나의 육교로 안 보인다"] the north
    #   stair was the ONE vertical access still wearing the pre-glass product: a 0.95 m solid
    #   `build_slope` cheek under a granite coping, no pane, no bronze, no mullion. Against a
    #   deck and a spiral that are both glass + bronze cap it read as a different structure
    #   [measured, `pt_noon_overview` north crop]. The cheek is not deleted — it is **demoted
    #   to the stringer upstand** the glazed guard stands on, exactly as on the spiral:
    #     `cheek_h` 0.95 -> **0.108** (offset above the stair MID line, the spiral's `up_top`)
    #     `cheek_t` 0.22 -> **0.12**, and the band is now centred ON the guard line (local
    #       y0 / y1 = world x 5.0 / 2.0 = the deck rail line) instead of lying inboard of it,
    #       so deck rail, north guard and stringer are one plane [computed].
    #   `bays` 3 per flight = **1.300 m** panels, the outer spiral run's own bay chord 1.296 m,
    #     so the three runs carry one panel width to within 4 mm [computed].
    #   `cap_h` / `cap_over` are retired with the granite coping (the guard takes its cap from
    #     `rail_bay`); kept so the history reads.
    north=dict(pivot=(3.5, 13.0), rot=90.0, x0=3.5, y0=11.5, y1=14.5,
               riser=0.192, tread=0.30, n=13, z_top=5.0, base_z=-0.30,
               land_len=1.4, cheek_t=0.12, cheek_h=0.108, bays=3,
               cap_h=0.08, cap_over=0.03),
    # --- roadway (4 lanes both ways, x axis) ---
    road=dict(x0=-70.0, x1=70.0, y0=-8.0, y1=8.0, z_top=-0.15, thick=0.60),
    #   lane paint: double yellow centreline + white dashed lane divider each way
    lane=dict(center_ys=(-0.20, 0.20), dash_ys=(-4.10, 4.10), w=0.15,
              z=-0.142, t=0.02, seg=3.0, gap=5.0, x0=-68.0, x1=68.0),
    # --- sidewalk (interlocking) + kerb ---
    #   [v6 verdict C-2] the old 22 m wide sidewalk was not "openness" but an **empty lot**
    #   (a straight horizon meeting the sky). Real 4-lane streets give 3~6 m of usable
    #   sidewalk, but the spiral outer edge (y −16.3) must fit, so it is cut to 11 m south /
    #   11 m north and **bounded** beyond by a verge + street tree row + distant tree band.
    walk=dict(x0=-70.0, x1=70.0, ys0=-19.0, ys1=-8.0, yn0=8.0, yn1=19.0,
              z_top=-0.005, thick=0.50),
    # [W3 S06 · S06-B] the kerb was **one box 140 m long** per side — the audit's own
    #   headline example of "colour without a curb": a 140 m extrusion has no joint and
    #   therefore no scale, so at h0.3 it reads as a painted band, not as 연석.
    #   `infra_kit.build_curb_line` emits **1 m unit blocks** (KS F 4006 is a 1 m product;
    #   the joint rhythm is the cue), an R10 top arris via the `curb` look class, and a
    #   chained L-gutter. `gt_drop = height + gutter cross-fall = 0.150 + 0.018 = 0.168`,
    #   which is why this needs a GT row of its own and does not ride GT-6.
    #   `lod_span` keeps the 1 m rhythm only inside the judged window and coarsens to 8 m
    #   outside it — the lever the builder documents for exactly this 140 m case.
    curb=dict(w=0.60, z_top=0.0, thick=0.40,
              height=0.150, width=0.20, unit=1.0, embed=0.25,
              lod_x=(-26.0, 26.0), far_unit=8.0),
    # --- verge (outer boundary of the sidewalk) : granite edging + ground-cover top ---
    verge=dict(w=2.40, curb_t=0.20, curb_top=0.14, soil_top=0.10,
               x0=-70.0, x1=70.0),
    # --- ground plane (grass slab that closes the horizon) ---
    #   z_top −0.16 : set 1 cm below the roadway top (−0.15) so the grass slab does not
    #   poke up through the asphalt (0.155 below the sidewalk −0.005). The slab itself
    #   extends to +-150 and handles the §A-4 horizon closure.
    ground=dict(x0=-150.0, x1=150.0, y0=-150.0, y1=150.0, z_top=-0.16,
                thick=1.40),
    # --- spiral + landing guard (cue_railing) --- glass panes under a bronze cap
    #   [W3 S06 · R06-2] G6 guards helix and deck with **bronze/brown** metal; G11 guards
    #     scene11 with **painted-steel vertical bars**. That pair is the formal identity
    #     separation the user asked for ("정체성 그렇게 안 겹치도록"), and the bronze cap
    #     carries it after GT-68 replaced the tube section.
    #   [W3 S06 · GT-6] `outer_r` **3.36 -> 3.24**. At 3.36 the posts stood **60 mm outboard of
    #     the tread edge** (r_out 3.30) — floating in air off the slab, the S06-A finding.
    #     3.24 puts the post centreline 60 mm INBOARD, which is where a real post baseplate goes.
    #   [GT-68 · 08-05 gallery] the spiral was the last 2-rail tube run in a structure whose
    #     deck guard is already glass + bronze cap (`DeckGlass_*`). Both spiral runs and both
    #     landing lobes are rebuilt from the deck's own three parts (steel shoe · laminated
    #     pane · bronze cap); the widths are READ from `deck`/`rail_bay` at build time
    #     (`_guard_section`), so the runs cannot drift into three sections. `rails`,
    #     `bottom`, `pipe_r`, `post_step_deg` and `seg_per_deg` are gone with the tube —
    #     Q2 (how many horizontal rails) is answered by the unification, not by a count.
    #   [GT-68] `inner_r` **1.44 -> 1.56** = tread r_in 1.50 + 0.06, the mirror of the outer
    #     60 mm inset. The old note claimed 1.44 kept the bases supported and it did not:
    #     the whole footprint (posts r 1.41…1.47) lay INSIDE the tread inner edge 1.50, i.e.
    #     in mid-air over the annular void [measured]. Clear stair width between the guard
    #     faces: 1.600 m at the shoe (3.200 − 1.600) and 1.540 m at the cap, the narrowest
    #     section, against the 1.20 m statutory minimum [computed].
    #   [GT-68] `steps_per_bay` 2 -> **13 bays**, the deck's own `rail_bay.n_bay`. The deck
    #     rule is "one pane per bay between posts"; on the curve the bay is pinned to the
    #     stair rhythm so every post lands on a riser line. Bay chord 1.296 m at the outer
    #     run (0.65 of the deck's 2.00 m) is set by the facet limit, not by taste: a 2.00 m
    #     bay on r 3.24 bows 158 mm off the arc against 65 mm here [computed].
    #   [GT-68] `joint` 0.020 against the deck's 0.050 — the deck value is a post-shoulder
    #     allowance on a 2.00 m straight bay; on the 0.624 m inner bay it would cut the pane
    #     from 0.486 to 0.368 m, i.e. 59 % of the bay instead of 78 % [computed].
    #     0.020 sits inside the real laminated-glass joint band (12…20 mm).
    #   `arc_seg` 1 = each pane is ONE flat facet with its ends on the guard circle. Real
    #     curved balustrades are built from flat panes; a subdivided pane would be a
    #     procedural tell.
    #   [GT-76 · gallery "나선 구조가 지저분하다 / 마감을 더 깔끔하게"] four measured defects
    #     drove this row, all of them on the OUTSIDE face of the guard where it is read:
    #     (a) the cap was **13 separate raked chords per run**. Each chord's plumb end face sat
    #         at a different z from its neighbour's start, so the cap line zig-zagged 23.077°
    #         at every post and left a 2*d_sc dead slot in between — the "kinked, unevenly
    #         stepped cap" of `pt_noon_spiral_up` / `pt_noon_overview`. `cap_seg_deg` replaces
    #         the chord chain with ONE bent member per run: facet sagitta at r 3.24 falls
    #         3.24*(1-cos 11.539°) = **65.5 mm -> 0.49 mm** [computed].
    #     (b) the shoe rode the MID-step line, so the tread edge (r_out 3.30, one full riser
    #         per step) crossed it in elevation and the exposed kick swung **0.120 <-> 0.312 m,
    #         26x round the helix** — the concrete sawtooth of `pt_noon_broken_rail`.
    #         `up_*` casts the raked **stringer upstand** the guard actually stands on: its top
    #         is a smooth helix 12 mm over the highest tread edge (+0.096), so no stepped
    #         concrete reaches the guard and the exposed kick is a constant 0.120 m [computed].
    #     (c) the pane sat face-to-face on shoe and cap (two coplanar pairs per bay).
    #     (d) every run ended in a raw plumb cut. `newel_t` is the terminal post that each run
    #         now dies into, under a bronze newel head that closes the cap's end face.
    #   `rail_h` 1.10 -> **1.196** = landing floor + level cap top (1.100) − the 0.096 m
    #     mid-line offset, i.e. the raked cap now meets the level cap at the a0 newel with
    #     **Δ 0 mm** instead of 6 mm, and the same identity holds at the deck/north joint.
    #     Guard height measured where code measures it — at the nosing — is 1.100 m [computed].
    #   `up_side` 0.050 = the walking-side face of the upstand, `up_rim` 0.002 = how far it
    #     stands proud of the structure rim it trims (fascia r_out 3.30 outboard, tread r_in
    #     1.50 inboard). The 2 mm is a second-pour offset and it is what keeps the upstand
    #     off the rim plane: no coplanar face anywhere on the run [computed].
    #   `post_r` is retired — the mullion is now the deck's own `rail_bay.post_t` square,
    #     radially oriented on the curves, so 06 carries ONE mullion section end to end.
    railing=dict(outer_r=3.24, inner_r=1.56, rail_h=1.196,
                 steps_per_bay=2, landing_bays=3, arc_seg=1,
                 cap_seg_deg=2.0, up_top=0.108, up_bot=-0.30,
                 up_side=0.050, up_rim=0.002, newel_t=0.13,
                 post_embed=0.05, joint=0.020),
    # --- tactile paving (cue_tactile) ---
    #   lower: in front of the azimuth-180 deg entry passage (sidewalk) / upper: deck south-end stair head
    tactile=dict(low=(-0.45, 0.20, -13.95, -12.05), low_z=0.0,
                 high=(2.0, 5.0, -11.30, -10.90), high_z=5.0, proud=0.004),
    # [v5.2 user] arbitrary warning sign removed - the stair-caution sign (PARAMS['sign']) is deleted.
    # --- dressing ---
    dress=dict(
        # street lamps (sidewalk, 1 m inside the kerb). 3.4 m clear of the grid sight axis y=−13.
        lamps=((-30.0, -9.60), (-10.0, -9.60), (18.0, -9.60), (38.0, -9.60),
               (-30.0, 9.60), (-10.0, 9.60), (18.0, 9.60), (38.0, 9.60)),
        lamp=dict(pole_h=6.0, pole_r=0.10, arm_len=1.1, arm_r=0.055, head=0.32),
        # street tree row - [v6 verdict C-2] one row on the verge (y ∓20.2). 7 m spacing +- jitter
        #   turns the sidewalk-grass boundary into a **line** (openness = a boundary existing).
        #   The spiral outer edge (y −16.3) and the area under the deck are left clear.
        #   [GT-92] the NORTH row must skip the north stair exactly as the south row's
        #   13.8 m gap (−3.6 → 10.2) skips the spiral: the stair plan is x 2.0…5.0,
        #   y 13.0…22.2, the row rides y 20.2, and the tree AABB is ±1.1, so
        #   x ∈ [0.9, 6.1] is banned. The old (3.6, 20.2) — a dropped minus sign against
        #   the south row's (−3.6, −20.2) — stood mid-flight-B (tread top 1.160 there),
        #   trunk through the treads, canopy over x 2.5…4.7 = 73 % of the stair width
        #   [measured]. Moved to (−3.4, 20.2): rhythm 6.8 m then the 13.8 m skip, the
        #   south row's own figures, and `_corridor_hits` now asserts the corridor.
        trees=((-38.2, -20.2), (-31.0, -20.2), (-24.4, -20.2), (-17.6, -20.2),
               (-10.4, -20.2), (-3.6, -20.2), (10.2, -20.2),
               (17.0, -20.2), (24.2, -20.2), (31.4, -20.2), (38.0, -20.2),
               (-31.2, 20.2), (-24.0, 20.2), (-17.4, 20.2), (-10.2, 20.2),
               (-3.4, 20.2), (10.4, 20.2), (17.2, 20.2), (24.0, 20.2),
               (31.0, 20.2)),
        # [v5.1 §3] benches sit beside an anchor (street tree) - no anchorless placement mid-field.
        benches=((-24.4, -18.4, -6.0), (17.0, -18.4, 5.0), (-17.4, 18.4, 175.0)),
        # bollard row - outer boundary of the spiral entry passage (sidewalk / roadway split)
        bollards=((-6.0, -9.30), (-3.0, -9.30), (0.0, -9.30),
                  (9.0, -9.30), (12.0, -9.30), (15.0, -9.30)),
        # bus stop pole (stop sign) - prop shared with the overpass world
        bus_pole=(24.0, -9.20, 3.2),
    ),
    # [W3 S06 · G6] the three near-field elements the image puts in front of everything else.
    #   All of them are *boundary* devices — G6's foreground is read almost entirely through
    #   them, and their absence is why the old frame's near field was bare paving.
    g6=dict(
        # brown timber road guardrail with yellow reflective bands, along the south kerb.
        #   `props_kit.build_tube_railing` is the correct builder here and this is the ONE
        #   run in the scene on its supported axis (X-aligned) — see the report finding on
        #   its rotY=90 restriction. `rails=4` is the template's compliant default.
        guard=dict(y=-8.85, x0=-30.0, x1=30.0, h=0.90, rails=3,
                   tube_r=0.045, post_r=0.055, pitch=2.20,
                   band_h=0.055, band_w=0.10),
        # green PVC-coated welded mesh fence — G6's right margin, beyond the planting.
        mesh=dict(y=-18.30, x0=-6.0, x1=34.0, h=1.80, post_pitch=2.50,
                  post_r=0.030, wire_r=0.006, n_wire=9),
        # landscaped bed at the tower foot: 야면석 rubble edge, ornamental grasses,
        #   flowering shrubs, one sapling on a timber tripod support. Sited SOUTH-WEST of
        #   the tower so it never enters the deck-run sight corridor (x 2…5) nor the
        #   r <= 4.2 near frame that `_corridor_hits` protects.
        bed=dict(cx=-1.60, cy=-15.60, rx=3.40, ry=2.10, edge_h=0.42,
                 n_edge=26, grass_h=1.05, shrub_h=0.70,
                 sapling=(-1.10, -15.10), tripod_r=0.62, tripod_h=1.55),
    ),
    # [v6 verdict C-2/C-4] distant closure - (1) pull the building blocks nearer the street and
    #   (2) lay a **tree silhouette band** (distant LOD) in front of them so the grass slab
    #   never meets the sky directly. The band is a ridge-like row of blocks, not individual
    #   trees, so no "lollipop parade" appears.
    #   height 4.4~4.8 (jitter +-1.2) - set to land **around eye level** from the deck
    #   viewpoint (z 5.3~6.8), covering the horizon but leaving the distant skyline.
    # [W3 S06 · G6 · BS-4] G6's backdrop is a **forested hill, a low-rise village and open
    #   sky** — the intake's own words are *"G6 is open-sky — the far tier must not close the
    #   horizon"*. The v6 build closed it completely: six blocks of 13.5…24 m at 78…94 m,
    #   which the first pilot render showed as an unbroken brick wall filling the whole
    #   background of `overview` and 60 % of `spiral_up` (the very complaint v7 §4(3) tried
    #   to fix by re-aiming the camera, i.e. by treating a scene defect as a framing defect).
    #   The fix is on the geometry side, where it belongs: the wooded band is raised and
    #   pushed out to become the **hill**, and the blocks drop to **village** scale (2–3
    #   storeys) and retreat behind it, so they read between the trees instead of over them.
    #   **Two pilot renders were spent finding out that the band is the wrong instrument for
    #   the hill, and the band is therefore left exactly as v6 built it.** Attempt 1 raised
    #   it in place (h 8.8-9.6 at y ∓33…40): at 20 m the 7 m segments stopped reading as a
    #   ridge and became a row of green monoliths with dome caps — a wall of vegetation
    #   replacing a wall of brick, which is not an improvement. Attempt 2 pushed it to
    #   y ∓46…54 and widened the segment to 14 m: still a wall, because a 10-11 m band at
    #   33-41 m subtends ~17 deg and the h1.8/d10 eye sits 5 m up on the deck looking
    #   straight into it. The band only works at the height v6 chose, where it sits BELOW
    #   the deck eye and merely stops the grass slab meeting the sky.
    #   So the horizon is opened the other way, and only the other way: **the village
    #   blocks drop from 13.5-24 m to 6.0-9.0 m (2-3 storeys) and retreat** — see
    #   `buildings` below. What is genuinely NOT delivered is G6's *forested hill*, which
    #   needs a real landform (a displaced ground mesh or a billboard ridge), not this
    #   block-row LOD. Recorded as owed in the report rather than faked with a taller band.
    treeband=dict(rows=((-33.0, -29.0, 4.8), (29.0, 33.0, 4.4)),
                  x0=-74.0, x1=74.0, seg=7.0, jitter=1.2),
    buildings=dict(
        E=dict(x0=104.0, x1=120.0, y0=-42.0, y1=42.0, h=9.0, floors=3,
               axis="x", facade_x=104.0, face_dir=-1.0, base_z=-0.16),
        W=dict(x0=-120.0, x1=-104.0, y0=-42.0, y1=42.0, h=7.5, floors=2,
               axis="x", facade_x=-104.0, face_dir=1.0, base_z=-0.16),
        N=dict(x0=-44.0, x1=8.0, y0=66.0, y1=80.0, h=8.0, floors=3,
               axis="y", facade_y=66.0, face_dir=-1.0, base_z=-0.16),
        N2=dict(x0=14.0, x1=52.0, y0=69.0, y1=81.0, h=6.5, floors=2,
                axis="y", facade_y=69.0, face_dir=-1.0, base_z=-0.16),
        S=dict(x0=-40.0, x1=6.0, y0=-82.0, y1=-68.0, h=8.5, floors=3,
               axis="y", facade_y=-68.0, face_dir=1.0, base_z=-0.16),
        S2=dict(x0=12.0, x1=54.0, y0=-78.0, y1=-66.0, h=6.0, floors=2,
                axis="y", facade_y=-66.0, face_dir=1.0, base_z=-0.16),
    ),
    #   [v6 verdict (5)] window decals repeated on the same grid on every block, so the tiling showed ->
    #   window size and row spacing now differ per block to break the rhythm (key = buildings key).
    window=dict(w=1.3, h=1.7, inset=0.15, col_step=2.8, margin=2.5),
    window_by=dict(
        E=dict(w=1.5, h=1.6, inset=0.15, col_step=3.2, margin=3.0),
        W=dict(w=1.2, h=1.8, inset=0.15, col_step=2.6, margin=2.0),
        N=dict(w=1.4, h=1.5, inset=0.15, col_step=3.0, margin=2.8),
        N2=dict(w=1.1, h=1.9, inset=0.15, col_step=2.3, margin=1.8),
        S=dict(w=1.3, h=1.7, inset=0.15, col_step=2.8, margin=2.5),
        S2=dict(w=1.6, h=1.4, inset=0.15, col_step=3.4, margin=3.2),
    ),

    # --- materials (sRGB gamma: dark constant colours live in 0.02~0.06 - §A-1) ---
    material=dict(
        # [v6 verdict (5)] the spiral and column read as "brown wood grain (particle board)" because
        #   concrete_floor diff averages RGB (107,93,77) = warm brown earth. To fix it without
        #   swapping textures, (1) hand the role to concrete_wall (141,133,111), which has
        #   joints and tie holes, and (2) equalise the channels with a tint for **neutral grey**.
        #   tint (0.72,0.77,0.92) -> mean (101,102,102) ~ albedo 0.40 (§4 no pure white ·
        #   real concrete value). Fascia / parapet are a touch brighter (0.435) to split the layers.
        scale=dict(paving_interlock=1.0, concrete_wall=2.0,
                   granite_dark=1.0, brick_red=2.0, grass=1.4, tactile=0.3),
        asphalt_color=(0.045, 0.045, 0.050), asphalt_rough=0.92,
        concrete_tint=(0.72, 0.77, 0.92),
        deck_tint=(0.76, 0.81, 0.97),
        parapet_tint=(0.78, 0.83, 0.99),
        soil_tint=(0.42, 0.44, 0.34),
        # S06-B item 3 — pale flamed granite kerb (G6), lifted off `granite_dark`
        curb_light_tint=(1.55, 1.58, 1.62),
        # G6 foreground: brown timber road guardrail + yellow reflective bands
        guard_wood=(0.185, 0.115, 0.062), guard_band=(0.62, 0.47, 0.05),
        # G6 right margin: green PVC-coated welded mesh fence
        mesh_green=(0.030, 0.098, 0.052),
        # G6 planting bed: rough-stone (야면석) edge
        rubble=(0.128, 0.124, 0.116),
        line_white=(0.55, 0.55, 0.52), line_yellow=(0.52, 0.40, 0.06),
        # [W3 S06 · G6 · R06-2] **bronze/brown tube railing** — the 06 identity, against
        #   scene11's painted-steel bar. The old teal (0.045,0.105,0.115) was the generic
        #   Korean municipal guardrail colour that 06 and 11 shared, i.e. exactly the
        #   overlap the user asked to break. Brown powder-coat / bronze anodise, kept
        #   inside the repo's dark-constant band (§A-1) and one notch warmer and lighter
        #   than `wood_color` (0.30,0.20,0.12) so tube and timber do not read as one material.
        rail_color=(0.255, 0.150, 0.082), rail_rough=0.42, rail_metallic=0.45,
        steel_color=(0.055, 0.058, 0.060), steel_rough=0.50,
        steel_metallic=0.45,
        # [v6 verdict C-3] the old panel_rough 0.18 = near-mirror -> it reflected the whole sky and
        #   rendered as a large "pure white panel" (deck parapet, landing parapet). Lowered to the
        #   real gloss of painted steel plate (0.48).
        panel_color=(0.075, 0.095, 0.105), panel_rough=0.48,
        # soiling band (darkened base) - lower 0.25 m of the parapet and cheek
        grime_color=(0.085, 0.085, 0.080), grime_rough=0.85,
        pole_color=(0.30, 0.31, 0.32), pole_metallic=0.75, pole_rough=0.35,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.40,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        # (old constant-colour parapet - replaced by a textured material in v6 C-3. Kept for history)
        parapet_color=(0.58, 0.58, 0.56), parapet_rough=0.60,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        leaf_a=(0.025, 0.045, 0.015), leaf_b=(0.035, 0.060, 0.020),
        grass_tint=(0.55, 0.68, 0.42),
        nosing_color=(0.85, 0.72, 0.10),
    ),

    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        noon_sun_enable=True, noon_sun_elev=49.79,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    # [v7 verdict §4 (3) - grid sight axis <-> sun azimuth alignment]
    #   the old 171.5 (world az 205, sun in the −X·−Y sky) dates from when the grid was the
    #   **ground approach (+X)**. Moving the grid onto the deck run (−Y sight line) in v6 drove
    #   the lambert of the camera-facing surface (normal +Y) to **−0.273 = fully backlit**
    #   (h1.8_d2 mean 26.3 · dark 81.3 %).
    #   new 111.5 = world az **145** (sun in the −X·+Y sky = behind-left of the grid camera).
    #     grid lit face (facing +Y) +0.370 · deck_entry (facing 102 deg) +0.473 ·
    #     spiral_up (facing −X) +0.529 · ground_approach +0.545 · broken_rail +0.340 ·
    #     ground_graze +0.264 - **every shot front lit** (SMOKE [v7 sun] prints it per shot).
    #   As a convention: keep the difference between the lit-face normal of the grid sight
    #     axis (= sight line +180 deg) and the sun az within +-60 deg. Here |90 − 145| = 55 deg.
    #   shadow azimuth = az − 180 = −35 deg -> shadows fall toward +X·−Y (the direction of
    #     travel = into the screen), so they do not cover the near deck surface.
    SUN_AZ_OFFSET=111.5,

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
# [C] paths + texture roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene06")
ASSET_ROLES = ["paving_interlock", "concrete_wall", "granite_dark",
               "brick_red", "grass", "tactile",   # [v5.2 user] arbitrary warning sign removed
               "hdri", "mdl"]


def _step_deg():
    sp = PARAMS["spiral"]
    return sp["sweep"] / float(sp["n"])


def _spiral_top_z(i):
    """Tread-face z of step i (0-based)."""
    sp = PARAMS["spiral"]
    return sp["z0"] - (i + 1) * sp["riser"]


def _spiral_mid_deg(i):
    """Centre azimuth of step i (degrees, ccw)."""
    return PARAMS["spiral"]["a0"] + (i + 0.5) * _step_deg()


def _spiral_z_at(a_deg):
    """Continuous approximation of the tread z at azimuth a (shared with the railing-top calculation)."""
    sp = PARAMS["spiral"]
    t = (a_deg - sp["a0"]) / _step_deg()
    return sp["z0"] - sp["riser"] * (t + 0.5)


def _fascia_span():
    """Azimuth range of the fascia / soffit rings = the whole spiral [a0, a0+sweep]."""
    sp = PARAMS["spiral"]
    return (sp["a0"], sp["a0"] + sp["sweep"])


def _soffit_z(a_deg):
    """Top surface of the continuous helicoid soffit at azimuth a.

    [W3 S06] This used to be `_fascia_z(a) − drop`, i.e. it hung off the fascia ribbon's
    interpolated top line. The ribbon is now stepped (one sector per tread), so the soffit
    is referenced directly to the **continuous** tread line — which is what a cast RC
    helicoid actually is, and what G6 shows: the treads step, the underside does not."""
    return _spiral_z_at(a_deg) - PARAMS["soffit"]["drop"]


def _landing_arcs():
    """The landing's azimuth lobes after the GT-6 clip at the deck edge.

    Returns [(a0, a1), ...]. The clip azimuth is where the deck's own edge lines
    x = deck.x0 / deck.x1 cross the landing rim r_out, i.e. `acos(half_deck_w / r_out)`;
    the wedge between the two lobes is covered by the deck slab at the same z, so
    clipping it removes solid/solid interpenetration without opening a walking hole."""
    la, dk = PARAMS["landing"], PARAMS["deck"]
    if not la.get("clip"):
        return [(la["a0"], la["a1"])]
    half = (dk["x1"] - dk["x0"]) / 2.0
    ac = math.degrees(math.acos(min(1.0, half / la["r_out"])))
    return [(la["a0"], ac), (180.0 - ac, la["a1"])]


def _in_landing(az, r):
    """Is plan point (az [0,360), r) on the clipped landing?"""
    la = PARAMS["landing"]
    if not (la["r_in"] <= r <= la["r_out"]):
        return False
    return any(a0 - 1e-9 <= az <= a1 + 1e-9 for a0, a1 in _landing_arcs())


# ===========================================================================
# [C1a] guard geometry (GT-68) - one glazed family for spiral · landing · deck
# ===========================================================================
def _guard_bays():
    """Azimuth boundaries of the spiral guard bays (n_bay+1 values, a0 … a0+sweep).

    The deck rule is one pane per bay between posts. On the curve the bay is pinned to the
    stair's own rhythm — `railing.steps_per_bay` treads per bay — so every post lands on a
    riser line and 26/2 gives **13 bays, the deck's `rail_bay.n_bay` exactly**."""
    sp, rl = PARAMS["spiral"], PARAMS["railing"]
    n = max(1, int(sp["n"]) // max(1, int(rl["steps_per_bay"])))
    d = sp["sweep"] / float(n)
    return [sp["a0"] + k * d for k in range(n + 1)]


def _guard_section(raked):
    """Guard cross-section as z offsets from the walking line the run stands on.

    Every value is read from the deck guard's own PARAMS, so the spiral, the landing lobes,
    the north stair and `build_deck_rail` cannot drift into four sections. Stacking order is
    the same on every run — **upstand · steel shoe · laminated pane · bronze cap** — and each
    part is HOUSED in the one below it (`glass_set`, `cap_grip`), so no two faces of the
    assembly are ever coplanar.

      raked=False (deck, landing lobes) — a level floor needs no upstand:
        shoe 0…0.120 · pane 0.085…1.040 · cap 1.015…1.100 [computed].
      raked=True (spiral runs, north flights AND the north mid-landing, which is referenced
        to `z_mid − riser/2` so the three north segments join at 0 mm) — offsets from the
        MID-step line: upstand -0.300…+0.108 · shoe +0.088…+0.228 · pane +0.193…+1.136 ·
        cap +1.111…+1.196 [computed].

    [GT-76] The raked branch is where the round's defect lived. `_spiral_z_at` is the MID-step
    line and the treads sit +-riser/2 = +-0.096 m about it, so ANY member pinned to that line
    is crossed by the tread edge once per step. The old shoe was pinned there and its exposed
    height swung 0.120…0.312 m, 26x round the helix, with the stepped concrete rim cutting
    across it in elevation. The fix is not to move the shoe but to give it something straight
    to stand on: `up_top` +0.108 clears the highest tread edge (+0.096) by 12 mm, so the
    upstand's own top IS the smooth raked line, the shoe sits 20 mm into it (`kick_bot`
    +0.088) and the exposed kick is a **constant 0.120 m** everywhere [computed]. The upstand
    bottom -0.300 is below the lowest fascia top (-0.098) and inside the step solid
    (tread - base_drop = -0.596 at worst), so it is buried at every azimuth — no floating
    edge, no gap [computed]. Pane height 0.943 m raked / 0.955 m level."""
    rb, dk, rl = PARAMS["rail_bay"], PARAMS["deck"], PARAMS["railing"]
    if not raked:
        cap_top = dk["panel_h"] + rb["cap_h"]
        return dict(up_bot=0.0, up_top=0.0,
                    kick_bot=0.0, kick_top=rb["kick_h"],
                    glass_bot=rb["kick_h"] - rb["glass_set"],
                    glass_top=dk["panel_h"],
                    cap_bot=dk["panel_h"] - rb["cap_grip"], cap_top=cap_top,
                    post_bot=-rl["post_embed"],
                    post_top=dk["panel_h"] - rb["cap_grip"] + 0.02)
    up = rl["up_top"]
    kick_top = up + rb["kick_h"]
    glass_top = rl["rail_h"] - rb["cap_h"]
    cap_bot = glass_top - rb["cap_grip"]
    return dict(up_bot=rl["up_bot"], up_top=up,
                kick_bot=up - 0.02, kick_top=kick_top,
                glass_bot=kick_top - rb["glass_set"], glass_top=glass_top,
                cap_bot=cap_bot, cap_top=rl["rail_h"],
                post_bot=up - 0.06, post_top=cap_bot + 0.02)


def _landing_guard_arcs():
    """Azimuth arcs of the landing guard, ended on the deck's own edge lines.

    `_landing_arcs` clips the SLAB where the deck edges cross the rim r_out 3.30; the guard
    stands at `railing.outer_r` 3.24 and therefore crosses those same edges at a different
    azimuth (62.422 vs 62.964 deg). Ending the guard on the slab azimuth would leave its
    terminal post 27 mm off the deck rail line; ending it here puts the post exactly on
    x = deck.x0 / deck.x1, where the deck guard already stands, so the junction is one
    newel instead of two near-coincident posts. The arc stays inside the slab lobe at both
    ends, and the slab sliver left beyond it lies inside the deck plan, where the deck's
    own run guards it — no gap opens in the guard line."""
    la, dk, rl = PARAMS["landing"], PARAMS["deck"], PARAMS["railing"]
    half = (dk["x1"] - dk["x0"]) / 2.0
    ac = math.degrees(math.acos(min(1.0, half / rl["outer_r"])))
    return [(la["a0"], ac), (180.0 - ac, la["a1"])]


def _deck_rail_y():
    """Y of the deck-rail / landing-guard shared newel, and the deck rail's bay boundaries.

    [GT-76] The landing guard leaves the deck edge line x = deck.x0 / x1 at azimuth
    `acos(half / outer_r)`, i.e. at y = cy + sqrt(outer_r^2 - half^2) = **-10.128**. The deck
    run used to be divided into 13 equal 2.000 m bays over the WHOLE slab (y -13…13), so its
    posts landed at y -13, -11, -9 … and the arriving landing guard crossed the run 0.872 m
    past a post with nothing shared: two cap lines meeting in mid-bay, which is the crossed
    joint visible in `pt_noon_overview`. The run is now cut at that point — one **apron return
    bay** from the deck's south edge to the newel (2.872 m, the stretch where the landing rim
    is outboard of the deck edge and the guard is therefore doubled today), then the 13
    regular bays from the newel to the north stair head at 1.779 m each. Nothing is removed:
    the guard is continuous over the whole slab edge and the two runs now share one post.
    [GT-92] On the WEST side the apron stretch is no longer a bay but the OPENING through
    which the deck connects to the west landing lobe and the spiral head — the "doubled
    today" above was the tell: a rail doubled over a floor-to-floor line guards nothing.
    The bay split this function returns is unchanged; `build_deck_rail` reads it and
    starts the west run at `yj`."""
    dk, rl = PARAMS["deck"], PARAMS["railing"]
    half = (dk["x1"] - dk["x0"]) / 2.0
    yj = PARAMS["spiral"]["cy"] + math.sqrt(max(0.0, rl["outer_r"] ** 2 - half ** 2))
    n = int(PARAMS["rail_bay"]["n_bay"])
    bays = [dk["y0"]] + [yj + (dk["y1"] - yj) * k / float(n) for k in range(n + 1)]
    return yj, bays


def _raked_sector_mesh(stage, path, cx, cy, r_in, r_out, a0_deg, a1_deg,
                       zb0, zt0, zb1, zt1, mtl=None, arc_seg=1):
    """Annular-sector prism whose bottom and top faces RAKE linearly across the span.

    `scene_common._annular_sector_mesh` takes one z_bot/z_top pair, so on a helix it can
    only step the guard once per bay. Here the pair is given per end ray, which makes the
    panel a **parallelogram in elevation**: bottom and top edges follow the walking line,
    end faces stay plumb — what a raked balustrade panel is.
    This is also why the tube guard could ride `build_helix_ramp` and a 0.82 m pane cannot:
    that builder tilts the whole box about its radial axis, so at the inner run's 31.6 deg
    helix angle the 0.824 m pane head would swing 0.432 m along the tangent — 69 % of the
    0.624 m bay chord — and open a slot beside every (plumb) post [computed].
    `arc_seg=1` leaves the panel ONE flat facet with both ends exactly on the guard circle.
    Point order per ring i: [inner_bot, outer_bot, inner_top, outer_top], the same
    arithmetic as `_annular_sector_mesh`. No collider: this scene's guard carries none
    (see `_obstacle_boxes`)."""
    from pxr import Gf, UsdGeom, Vt
    n = max(1, int(arc_seg))
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)
    pts = []
    for i in range(n + 1):
        f = i / float(n)
        a = a0 + (a1 - a0) * f
        zb = zb0 + (zb1 - zb0) * f
        zt = zt0 + (zt1 - zt0) * f
        ca, sa = math.cos(a), math.sin(a)
        ix, iy = cx + r_in * ca, cy + r_in * sa
        ox, oy = cx + r_out * ca, cy + r_out * sa
        pts += [Gf.Vec3f(ix, iy, zb), Gf.Vec3f(ox, oy, zb),
                Gf.Vec3f(ix, iy, zt), Gf.Vec3f(ox, oy, zt)]

    def v(i, k):                                   # k: 0 ib, 1 ob, 2 it, 3 ot
        return i * 4 + k
    counts, idx = [], []

    def quad(a_, b_, c_, d_):
        counts.append(4)
        idx.extend([a_, b_, c_, d_])
    for i in range(n):
        quad(v(i, 2), v(i, 3), v(i + 1, 3), v(i + 1, 2))     # top (raked)
        quad(v(i, 0), v(i + 1, 0), v(i + 1, 1), v(i, 1))     # bottom (raked)
        quad(v(i, 1), v(i + 1, 1), v(i + 1, 3), v(i, 3))     # outer face
        quad(v(i, 0), v(i, 2), v(i + 1, 2), v(i + 1, 0))     # inner face
    quad(v(0, 0), v(0, 1), v(0, 3), v(0, 2))                 # plumb end at a0
    quad(v(n, 0), v(n, 2), v(n, 3), v(n, 1))                 # plumb end at a1
    m = UsdGeom.Mesh.Define(stage, path)
    m.CreatePointsAttr(Vt.Vec3fArray(pts))
    m.CreateFaceVertexCountsAttr(Vt.IntArray(counts))
    m.CreateFaceVertexIndicesAttr(Vt.IntArray(idx))
    m.CreateSubdivisionSchemeAttr(UsdGeom.Tokens.none)
    lo = Gf.Vec3f(min(p[0] for p in pts), min(p[1] for p in pts),
                  min(p[2] for p in pts))
    hi = Gf.Vec3f(max(p[0] for p in pts), max(p[1] for p in pts),
                  max(p[2] for p in pts))
    m.CreateExtentAttr([lo, hi])
    sc._bind_mtl(m.GetPrim(), mtl)
    return m


# ===========================================================================
# [C1b] camera numeric-check base - AABB obstacles + solid lookup (single ray-march source)
#   [v6 verdict instruction] check the basis for the grid-axis move and the mise-en-scene re-aim by coordinates.
#   follows the scene08 `_obstacle_boxes` / `_solid_at` convention as-is.
# ===========================================================================
def _north_local(x, y):
    """Inverse transform, world → local coordinates of the north stair rot_group (+90° @ pivot).
    Inverse of the forward map (lx,ly) → (px−(ly−py), py+(lx−px)): lx = px+(wy−py),
    ly = py−(wx−px)."""
    px, py = PARAMS["north"]["pivot"]
    return (px + (y - py), py - (x - px))


def _north_top(lx):
    """Top-face z at local x of the north stair (stepped). None if outside the range."""
    no = PARAMS["north"]
    runA = no["n"] * no["tread"]
    z_mid = no["z_top"] - no["n"] * no["riser"]
    a0, a1 = no["x0"], no["x0"] + runA
    m1 = a1 + no["land_len"]
    b1 = m1 + runA
    if lx < a0 or lx > b1:
        return None
    if lx <= a1:
        i = min(no["n"], int((lx - a0) / no["tread"]) + 1)
        return no["z_top"] - i * no["riser"]
    if lx <= m1:
        return z_mid
    i = min(no["n"], int((lx - m1) / no["tread"]) + 1)
    return z_mid - i * no["riser"]


def _spiral_top_at(r, az_raw):
    """Spiral tread top z at radius r and azimuth az (0~360). None if outside the stair."""
    sp = PARAMS["spiral"]
    if not (sp["r_in"] <= r <= sp["r_out"]):
        return None
    sd = _step_deg()
    for a in (az_raw, az_raw + 360.0):
        t = (a - sp["a0"]) / sd
        if -1e-9 <= t < sp["n"]:
            return _spiral_top_z(int(t))
    return None


def _in_sweep(az_raw):
    """Whether the azimuth falls in the spiral range [a0, a0+sweep] → returns the continuous parameter a."""
    sp = PARAMS["spiral"]
    for a in (az_raw, az_raw + 360.0):
        if sp["a0"] - 1e-9 <= a <= sp["a0"] + sp["sweep"] + 1e-9:
            return a
    return None


def _solid_at(x, y, z):
    """Name of the terrain / structural solid containing the point (x,y,z), else None.
    Single source for the camera-eye burial and sight-line (ray march) checks."""
    sp = PARAMS["spiral"]
    dk = PARAMS["deck"]
    la = PARAMS["landing"]
    wk = PARAMS["walk"]
    rd = PARAMS["road"]
    g = PARAMS["ground"]
    fa, so = PARAMS["fascia"], PARAMS["soffit"]
    # ── ground·roadway·sidewalk·kerb·verge ──
    if g["x0"] <= x <= g["x1"] and g["y0"] <= y <= g["y1"] \
            and g["z_top"] - g["thick"] <= z <= g["z_top"]:
        return "Ground"
    if rd["x0"] <= x <= rd["x1"] and rd["y0"] <= y <= rd["y1"] \
            and rd["z_top"] - rd["thick"] <= z <= rd["z_top"]:
        return "Road"
    for tag, ya, yb in (("Walk_S", wk["ys0"], wk["ys1"]),
                        ("Walk_N", wk["yn0"], wk["yn1"])):
        if wk["x0"] <= x <= wk["x1"] and ya <= y <= yb \
                and wk["z_top"] - wk["thick"] <= z <= wk["z_top"]:
            return tag
    vg = PARAMS["verge"]
    for tag, ya, yb in (("Verge_S", wk["ys0"] - vg["w"], wk["ys0"]),
                        ("Verge_N", wk["yn1"], wk["yn1"] + vg["w"])):
        if vg["x0"] <= x <= vg["x1"] and ya <= y <= yb \
                and -0.30 <= z <= vg["curb_top"]:
            return tag
    # ── spiral·column·landing ──
    r = math.hypot(x - sp["cx"], y - sp["cy"])
    az = math.degrees(math.atan2(y - sp["cy"], x - sp["cx"])) % 360.0
    co = PARAMS["column"]
    if r <= co["r"] and co["z_bot"] <= z <= co["z_top"]:
        return "Column"
    if _in_landing(az, r) and la["base_z"] <= z <= la["top_z"]:
        return "Landing"
    top = _spiral_top_at(r, az)
    if top is not None and top - sp["base_drop"] <= z <= top:
        return "SpiralStep"
    # [W3 S06] the fascia is now **stepped**: its top follows the tread it trims, sitting
    #   `drop_below` under that tread face, so it never stands proud of the walked surface.
    if top is not None and fa["r_in"] <= r <= fa["r_out"]:
        ft = top - fa["drop_below"]
        if ft - fa["thick"] <= z <= ft:
            return "SpiralFascia"
    a_c = _in_sweep(az)
    if a_c is not None:
        sz = _soffit_z(a_c)
        if so["r_in"] <= r <= so["r_out"] and sz - so["thick"] <= z <= sz:
            return "SpiralSoffit"
    # ── deck·support columns·deck railing ──
    if dk["x0"] <= x <= dk["x1"] and dk["y0"] <= y <= dk["y1"] \
            and dk["z_top"] - dk["thick"] <= z <= dk["z_top"]:
        return "Deck"
    dp = PARAMS["deck_posts"]
    for i, py in enumerate(dp["ys"]):
        # [W3 S06] V-form: one conservative envelope covering footing + both splayed legs.
        #   The splay is across the deck (+-X), so the Y half-width stays the leg radius.
        if abs(x - dp["x"]) <= dp["splay"] + dp["leg_r0"] \
                and abs(y - py) <= max(dp["r"], dp["leg_r0"]) + 0.25 \
                and dp["z_bot"] <= z <= dk["z_top"] - dk["thick"]:
            return f"DeckPost_{i}"
    rb = PARAMS["rail_bay"]
    # [GT-92] the WEST run starts at the landing newel yj — its apron stretch is the
    #   deck↔lobe opening, so the solid band must not claim it (single ray-march source).
    yj_rail, _ = _deck_rail_y()
    for i, xe in enumerate((dk["x0"], dk["x1"])):
        y_lo = yj_rail if i == 0 else dk["y0"]
        if abs(x - xe) <= max(dk["parapet_t"], rb["post_t"]) / 2.0 \
                and y_lo <= y <= dk["y1"] \
                and dk["z_top"] <= z <= dk["z_top"] + rb["post_h"]:
            return f"DeckRail_{i}"
    # ── north stair (rot group) ──
    no = PARAMS["north"]
    lx, ly = _north_local(x, y)
    if no["y0"] <= ly <= no["y1"]:
        nt = _north_top(lx)
        if nt is not None and no["base_z"] <= z <= nt:
            return "NorthStair"
    # ── distant tree band · buildings ──
    tb = PARAMS["treeband"]
    for ri, (ya, yb, hh) in enumerate(tb["rows"]):
        if tb["x0"] <= x <= tb["x1"] and ya - 1.0 <= y <= yb + 1.0 \
                and g["z_top"] <= z <= g["z_top"] + hh + tb["jitter"]:
            return f"TreeBand_{ri}"
    for key, bd in PARAMS["buildings"].items():
        if bd["x0"] <= x <= bd["x1"] and bd["y0"] <= y <= bd["y1"] \
                and bd.get("base_z", 0.0) - 1.0 <= z \
                <= bd.get("base_z", 0.0) + bd["h"]:
            return f"Building_{key}"
    return None


def _obstacle_boxes():
    """Dressing / railing AABBs for camera collision checks (name, x0,x1, y0,y1, z0,z1).
    Terrain and structural solids are handled by `_solid_at`, so only thin prims go here."""
    d = PARAMS["dress"]
    gz = PARAMS["walk"]["z_top"]
    boxes = []
    lp = d["lamp"]
    for i, (lx, ly) in enumerate(d["lamps"]):
        boxes.append((f"Lamp_{i}", lx - 0.6, lx + 0.6, ly - 1.3, ly + 1.3,
                      gz, gz + lp["pole_h"]))
    for i, (tx, ty) in enumerate(d["trees"]):
        boxes.append((f"Tree_{i}", tx - 1.1, tx + 1.1, ty - 1.1, ty + 1.1,
                      gz, gz + 4.2))
    for i, (bx, by, _yaw) in enumerate(d["benches"]):
        boxes.append((f"Bench_{i}", bx - 1.0, bx + 1.0, by - 0.4, by + 0.4,
                      gz, gz + 0.5))
    for i, (bx, by) in enumerate(d["bollards"]):
        boxes.append((f"Bollard_{i}", bx - 0.1, bx + 0.1, by - 0.1, by + 0.1,
                      gz, gz + 0.75))
    bx, by, bh = d["bus_pole"]
    boxes.append(("BusPole", bx - 0.1, bx + 0.1, by - 0.3, by + 0.3, gz,
                  gz + bh))
    dk = PARAMS["deck"]
    rb = PARAMS["rail_bay"]
    yj_rail, _ = _deck_rail_y()
    for i, xe in enumerate((dk["x0"], dk["x1"])):
        y_lo = yj_rail if i == 0 else dk["y0"]
        boxes.append((f"DeckRail_{i}", xe - 0.09, xe + 0.09, y_lo, dk["y1"],
                      dk["z_top"], dk["z_top"] + rb["post_h"]))
    # the spiral guard (pane 19 mm · shoe/upstand 80…112 mm · mullion 100 mm) is thinner than
    #   the camera radius, so it is excluded from AABB collision checks (it is a ring, so a
    #   box AABB gives false positives). GT-68 and GT-76 changed the section, not this
    #   exclusion. [GT-92] the WEST `DeckRail_0` box now starts at the landing newel yj:
    #   the run itself is shortened there — its apron stretch is the deck↔lobe opening.
    #   The EAST box still spans the whole slab edge (its apron bay stays closed).
    return boxes


# ===========================================================================
# [C2] smoke - geometry self-check before boot (early exit)
# ===========================================================================
def _smoke_report():
    sp = PARAMS["spiral"]
    dk = PARAMS["deck"]
    la = PARAMS["landing"]
    no = PARAMS["north"]
    rl = PARAMS["railing"]
    sd = _step_deg()
    drop = sp["n"] * sp["riser"]
    print("=" * 68)
    print("scene06_overpass_spiral — SMOKE 기하 자기검증 (부팅 없음)")
    print("=" * 68)
    print(f"  나선: r_in {sp['r_in']} / r_out {sp['r_out']} / sweep {sp['sweep']}° "
          f"/ {sp['n']}단 · step {sd:.6f}°")
    print(f"    riser {sp['riser']} × {sp['n']} = 낙차 {drop:.3f} m  "
          f"(z0 {sp['z0']:.3f} → 단{sp['n']-1} 상면 {_spiral_top_z(sp['n']-1):+.3f})")
    r_w = sp["r_in"] + (2.0 / 3.0) * (sp["r_out"] - sp["r_in"])
    tread_w = r_w * math.radians(sd)
    chord = 2.0 * sp["r_out"] * math.sin(math.radians(sd) / 2.0) * 1.03
    arc_out = sp["r_out"] * math.radians(sd)
    print(f"    walkline r_w {r_w:.3f} → tread {tread_w:.4f} m, 2R+T = "
          f"{2*sp['riser']+tread_w:.3f}")
    print(f"    세그 현길이(외경×1.03) {chord:.4f} ≥ 외경 호 {arc_out:.4f} → "
          f"{'OK' if chord >= arc_out else 'FAIL'} (교훈 4 쐐기 틈)")
    print(f"    단 0  방위 [{sp['a0']:.2f}, {sp['a0']+sd:.2f}]  상면 "
          f"{_spiral_top_z(0):+.3f}")
    print(f"    단 {sp['n']-1} 방위 [{(sp['a0']+(sp['n']-1)*sd) % 360:.2f}, "
          f"{(sp['a0']+sp['n']*sd) % 360:.2f}]  상면 "
          f"{_spiral_top_z(sp['n']-1):+.3f}")
    # ── entry passage: the azimuth band the stair does not occupy ──
    free0 = (sp["a0"] + sp["sweep"]) % 360.0          # 120°
    free1 = sp["a0"] % 360.0                          # 180°
    print(f"  [진입 통로] 지상 무단(無段) 방위 [{free0:.2f}, {free1:.2f}] "
          f"= {free1-free0:.1f}° — 랜딩(z {la['top_z']:.3f}) 아래 필로티")
    print(f"    통로 유효고 = 랜딩 저면 {la['base_z']:.3f} − 지면 "
          f"{PARAMS['walk']['z_top']:+.3f} = "
          f"{la['base_z']-PARAMS['walk']['z_top']:.3f} m → "
          f"{'OK' if la['base_z']-PARAMS['walk']['z_top'] > 2.1 else 'FAIL'}")
    # ── walking continuity table ──
    print("  [보행 연속성 검증표]")
    rows = [
        ("남측 보도 → 진입 통로", PARAMS["walk"]["z_top"], PARAMS["walk"]["z_top"]),
        ("진입 통로 → 하단 단", PARAMS["walk"]["z_top"], _spiral_top_z(sp["n"]-1)),
        # the number of steps between the top of step 25 and the top of step 0 is (n−1). The
        #   remaining riser is carried by "step 0 -> landing" (0.190) - ground to landing rises 5.003 m.
        ("나선 상행(디딤 25단차)", _spiral_top_z(sp["n"]-1), _spiral_top_z(0)),
        ("단 0 → 원형 랜딩", _spiral_top_z(0), la["top_z"]),
        ("랜딩 → 데크", la["top_z"], dk["z_top"]),
        ("데크 → 북측 계단 A", dk["z_top"], dk["z_top"] - no["n"]*no["riser"]),
        ("북측 중간참", dk["z_top"] - no["n"]*no["riser"],
         dk["z_top"] - no["n"]*no["riser"]),
        ("북측 계단 B", dk["z_top"] - no["n"]*no["riser"],
         dk["z_top"] - 2*no["n"]*no["riser"]),
        ("북측 보도 탈출", dk["z_top"] - 2*no["n"]*no["riser"],
         PARAMS["walk"]["z_top"]),
    ]
    bad = 0
    for nm, z0, z1 in rows:
        d = abs(z1 - z0)
        # on a stair run it is the riser (rise divided by step count) that is judged
        if "상행" in nm or "계단" in nm:
            ok = abs(d - ((sp["n"]-1)*sp["riser"] if "상행" in nm
                          else no["n"]*no["riser"])) < 1e-6
        else:
            ok = d <= 0.20
        bad += 0 if ok else 1
        print(f"    {nm:22s} z {z0:+.3f} → {z1:+.3f}  Δ{d:+.3f}  "
              f"{'OK' if ok else 'FAIL'}")
    print(f"    연속성 판정: {'OK' if bad == 0 else f'FAIL({bad})'}")
    # ── guard continuity ──
    a0, a1 = sp["a0"], sp["a0"] + sp["sweep"]
    rb = PARAMS["rail_bay"]
    bays = _guard_bays()
    gs, gl = _guard_section(True), _guard_section(False)
    bay_deg = (a1 - a0) / float(len(bays) - 1)
    print("  [가드 통일 GT-76] 업스탠드 + 슈 + 유리판 + 브론즈 캡 — 전 구간 1계열")
    print(f"    내·외측 가드 방위 [{a0:.0f}, {a1:.0f}] 전 구간 연결 · 베이 "
          f"{len(bays)-1}개 ({rl['steps_per_bay']}단/베이 {bay_deg:.4f}°) = 데크 베이 "
          f"{rb['n_bay']}개와 동수 → "
          f"{'OK' if len(bays)-1 == rb['n_bay'] else 'FAIL'}")
    # [GT-76] the cap is ONE member per run now, so what matters is the FACET sagitta of the
    #   member, not the bay chord sagitta the old per-bay chain carried.
    cap_sag = rl["outer_r"] * (1.0 - math.cos(math.radians(rl["cap_seg_deg"]
                                                           / 2.0)))
    bay_sag = rl["outer_r"] * (1.0 - math.cos(math.radians(bay_deg / 2.0)))
    print(f"    캡·슈·업스탠드 = run 당 1本 (facet {rl['cap_seg_deg']:.1f}° → "
          f"새기타 {cap_sag*1000:.2f} mm, 구 베이현 {bay_sag*1000:.1f} mm) · "
          f"포스트 조인트 단절 0 → "
          f"{'OK' if cap_sag <= 0.001 else 'FAIL'}(≤1 mm)")
    for tag, rad in (("외측", rl["outer_r"]), ("내측", rl["inner_r"])):
        ch = 2.0 * rad * math.sin(math.radians(bay_deg / 2.0))
        sag = rad * (1.0 - math.cos(math.radians(bay_deg / 2.0)))
        pitch = math.degrees(math.atan2(sp["riser"] * rl["steps_per_bay"], ch))
        print(f"    {tag} r{rad:.2f}: 유리 베이 현 {ch:.3f} m · 판 새기타 "
              f"{sag*1000:5.1f} mm · 헬릭스 경사 {pitch:5.2f}° → "
              f"{'OK' if sag <= 0.08 else 'FAIL'}(≤80 mm)")
    print(f"    단면(보행선 기준, 데크 값 그대로): 업스탠드 {gs['up_bot']:+.3f}…"
          f"{gs['up_top']:+.3f} · 슈 {gs['kick_bot']:+.3f}…{gs['kick_top']:+.3f}"
          f" · 유리 {gs['glass_bot']:+.3f}…{gs['glass_top']:+.3f} "
          f"(판高 {gs['glass_top']-gs['glass_bot']:.3f} m, 데크 "
          f"{gl['glass_top']-gl['glass_bot']:.3f}) · 캡 {gs['cap_bot']:+.3f}…"
          f"{gs['cap_top']:+.3f}")
    half_r = sp["riser"] / 2.0
    cover = gs["up_top"] - half_r
    ek = gs["kick_top"] - gs["up_top"]
    print(f"    업스탠드 상면이 최고 디딤 연단(+{half_r:.3f}) 위 {cover*1000:.0f} mm "
          f"→ 계단상 콘크리트가 가드를 가로지르지 않음 · 노출 킥 {ek:.3f} m 일정"
          f"(구 {rb['kick_h']:.3f}…{rb['kick_h']+sp['riser']:.3f} 진동) → "
          f"{'OK' if cover > 0 else 'FAIL'}")
    bury = -gs["up_bot"] - half_r
    print(f"    업스탠드 하단 {gs['up_bot']:+.3f} < 최저 파시아 상면 "
          f"{-half_r-PARAMS['fascia']['drop_below']:+.3f} · 단 솔리드 저면 "
          f"{-half_r-sp['base_drop']:+.3f} 위 → 매립 {bury:.3f} m "
          f"{'OK' if bury > 0 else 'FAIL'}")
    print(f"    유리 물림 슈 {rb['glass_set']*1000:.0f} mm · 캡 "
          f"{rb['cap_grip']*1000:.0f} mm → 동일면 접합 0쌍 "
          f"(구 슈상면=판저면·판상면=캡저면 각 1쌍/베이)")
    cap_dk = dk["z_top"] + gl["cap_top"]
    cap_ld = la["top_z"] + gl["cap_top"]
    cap_sp = _spiral_z_at(a0) + gs["cap_top"]
    cap_no = no["z_top"] - no["riser"] / 2.0 + gs["cap_top"]
    d1, d2, d3 = (abs(cap_ld - cap_dk), abs(cap_sp - cap_ld),
                  abs(cap_no - cap_dk))
    print(f"    [캡 라인 연속] 데크 {cap_dk:.3f} = 랜딩 {cap_ld:.3f} "
          f"(Δ{d1*1000:.0f} mm) = 나선 접합(방위 {a0:.0f}°) {cap_sp:.3f} "
          f"(Δ{d2*1000:.0f} mm) = 북측 계단 두부 {cap_no:.3f} (Δ{d3*1000:.0f} mm)"
          f" → {'OK' if max(d1, d2, d3) < 1e-6 else 'FAIL'}")
    ga, sl = _landing_guard_arcs(), _landing_arcs()
    print(f"    랜딩 가드 호 [{ga[0][0]:.3f},{ga[0][1]:.3f}]·[{ga[1][0]:.3f},"
          f"{ga[1][1]:.3f}] ⊂ 슬래브 로브 [{sl[0][0]:.3f},{sl[0][1]:.3f}] · "
          f"종단 x = 데크 연단 {dk['x0']:.2f}/{dk['x1']:.2f} → "
          f"{'OK' if ga[0][1] <= sl[0][1] + 1e-9 else 'FAIL'}")
    yj, ybays = _deck_rail_y()
    print(f"    [데크↔랜딩 접합] 데크 난간 분절 y {dk['y0']:.3f} → 뉴얼 "
          f"{yj:.3f}(= 랜딩 가드가 x {dk['x1']:.2f} 를 지나는 점) → {dk['y1']:.3f}"
          f" · 에이프런 리턴 1 + 정규 {len(ybays)-2} 베이 "
          f"({(dk['y1']-yj)/(len(ybays)-2):.3f} m) → "
          f"{'OK' if abs(ybays[1]-yj) < 1e-9 else 'FAIL'}")
    # [GT-92] passage opening — the deck↔west-lobe crossing the west apron bay sealed
    xw = PARAMS["spiral"]["cx"] - rl["inner_r"]           # a0 inner newel = south jamb
    clr = (yj - rl["newel_t"]/2.0) - (dk["y0"] + rl["newel_t"]/2.0)
    flush = abs(la["top_z"] - dk["z_top"])
    print(f"    [GT-92 개구] 서측 런 y {yj:.3f}→{dk['y1']:.3f} · 개구 x {dk['x0']:.3f}"
          f" 선, y {dk['y0']:.3f}…{yj:.3f} 유효폭 {clr:.3f} m ≥ 1.20 · 잼 뉴얼 "
          f"S({dk['x0']:.2f},{yj:.3f})/a0내측({xw:.2f},{PARAMS['spiral']['cy']:.1f})"
          f" · 횡단 바닥 데크 {dk['z_top']:.3f} = 로브 {la['top_z']:.3f} "
          f"(Δ{flush*1000:.0f} mm) → "
          f"{'OK' if clr >= 1.20 and flush < 1e-9 else 'FAIL'}")
    print(f"    [GT-92 경로] 개구 → 서측 로브(az 117.036…180, r 0.48…3.30, z "
          f"{la['top_z']:.3f}) → az180 레이 x {PARAMS['spiral']['cx']-sp['r_out']:.2f}"
          f"…{PARAMS['spiral']['cx']-sp['r_in']:.2f} → 단0 상면 "
          f"{_spiral_top_z(0):+.3f} (Δ{la['top_z']-_spiral_top_z(0):.3f} = riser) → "
          f"{'OK' if abs(la['top_z']-_spiral_top_z(0)-sp['riser']) < 1e-9 else 'FAIL'}")
    sh = dk["parapet_t"] / 2.0
    foot = ((rl["inner_r"] - sh, rl["inner_r"] + sh),
            (rl["outer_r"] - sh, rl["outer_r"] + sh))
    on_tread = all(sp["r_in"] - 0.01 <= f0 and f1 <= sp["r_out"] for f0, f1 in foot)
    up_o = (rl["outer_r"] - rl["up_side"], PARAMS["fascia"]["r_out"]
            + rl["up_rim"])
    up_i = (sp["r_in"] + rl["up_rim"], rl["inner_r"] + rl["up_side"])
    clr_up = up_o[0] - up_i[1]
    print(f"    슈 반경대 내측 [{foot[0][0]:.3f},{foot[0][1]:.3f}] · 외측 "
          f"[{foot[1][0]:.3f},{foot[1][1]:.3f}] ⊂ 디딤 [{sp['r_in']:.2f},"
          f"{sp['r_out']:.2f}] → {'OK' if on_tread else 'FAIL'}")
    print(f"    업스탠드 반경대 내측 [{up_i[0]:.3f},{up_i[1]:.3f}] · 외측 "
          f"[{up_o[0]:.3f},{up_o[1]:.3f}] — 내측 하단이 보이드 연단 "
          f"{sp['r_in']:.3f} 을 침범 안 함 → "
          f"{'OK' if up_i[0] >= sp['r_in'] else 'FAIL'}")
    print(f"    가드 사이 유효폭(업스탠드 면) {clr_up:.3f} m ≥ 1.20 → "
          f"{'OK' if clr_up >= 1.20 else 'FAIL'}")
    # ── deck clearance · column interference ──
    deck_bot = dk["z_top"] - dk["thick"]
    print(f"  [데크] 상면 {dk['z_top']:.2f} 저면 {deck_bot:.2f} · 차도 상면 "
          f"{PARAMS['road']['z_top']:+.2f} → 유효고 "
          f"{deck_bot-PARAMS['road']['z_top']:.2f} m "
          f"{'OK' if deck_bot-PARAMS['road']['z_top'] >= 4.5 else 'FAIL'}")
    dp = PARAMS["deck_posts"]
    for py in dp["ys"]:
        dist = math.hypot(dp["x"] - sp["cx"], py - sp["cy"])
        clr = dist - sp["r_out"] - dp["r"]
        print(f"    지지 기둥 y={py:+.1f} → 나선 중심 거리 {dist:.3f}, "
              f"외주 여유 {clr:+.3f} {'OK' if clr > 0 else 'FAIL'}")
    # ── rot_group 90 deg coordinate check (north stair) ──
    px, py = no["pivot"]

    def _rot90(x, y):
        return (px - (y - py), py + (x - px))
    runA = no["n"] * no["tread"]
    locs = [("계단A 상단", no["x0"], no["y0"]), ("계단A 하단", no["x0"]+runA, no["y1"]),
            ("중간참 끝", no["x0"]+runA+no["land_len"], no["y0"]),
            ("계단B 하단", no["x0"]+2*runA+no["land_len"], no["y1"])]
    print("  [북측 rot_group 90° 검산]  (x,y) → (16.5−y, 9.5+x)")
    for nm, lx, ly in locs:
        wx, wy = _rot90(lx, ly)
        print(f"    {nm:10s} 로컬({lx:6.2f},{ly:6.2f}) → 월드({wx:6.2f},{wy:6.2f})")
    # [GT-76] stringer upstand check — the demoted cheek. Judged the same way the spiral's
    #   upstand is: does the top clear the highest tread edge, and is the underside buried?
    angn = math.atan2(no["n"]*no["riser"], runA)
    ct = 0.60 * math.cos(angn)
    up_top0 = no["z_top"] - no["riser"]/2.0 + no["cheek_h"]
    pb_top = up_top0 - ct
    print(f"    치크→스트링거 업스탠드: 경사 {math.degrees(angn):.2f}° · thick 0.60 "
          f"→ 상면 {up_top0:+.3f} (최고 디딤 연단 "
          f"{no['z_top']-no['riser']/2.0+no['riser']/2.0:+.3f} 위 "
          f"{(no['cheek_h']-no['riser']/2.0)*1000:.0f} mm "
          f"{'OK' if no['cheek_h'] > no['riser']/2.0 else 'FAIL'}) · 밑면 "
          f"{pb_top:+.3f} (1단 디딤 {no['z_top']-no['riser']:+.3f} 아래 "
          f"{'OK' if pb_top < no['z_top']-no['riser'] else 'FAIL'})")
    print(f"    업스탠드 y대역 [{no['y0']-no['cheek_t']/2.0:.3f},"
          f"{no['y0']+no['cheek_t']/2.0:.3f}] / "
          f"[{no['y1']-no['cheek_t']/2.0:.3f},{no['y1']+no['cheek_t']/2.0:.3f}]"
          f" — 가드선 = 로컬 y {no['y0']:.2f}/{no['y1']:.2f} = 월드 x "
          f"{dk['x1']:.2f}/{dk['x0']:.2f} = 데크 난간선 → "
          f"{'OK' if no['cheek_t'] < (no['y1']-no['y0']) else 'FAIL'}")
    nseg = [("계단 A 두부", no["x0"]), ("계단 A 하단", no["x0"]+runA),
            ("중간참 끝", no["x0"]+runA+no["land_len"]),
            ("계단 B 하단", no["x0"]+2*runA+no["land_len"])]
    gsn = _guard_section(True)
    print(f"    북측 가드 캡 라인({int(no['bays'])*2+1} 베이/측, 판폭 "
          f"{runA/no['bays']:.3f} m = 외측 나선 현 "
          f"{2*rl['outer_r']*math.sin(math.radians(sp['sweep']/(sp['n']/rl['steps_per_bay'])/2.0)):.3f} m):")
    for nm, lx in nseg:
        zr = no["z_top"] - no["riser"]*((lx-no["x0"])/no["tread"] + 0.5) \
            if lx <= no["x0"]+runA else (
                no["z_top"] - no["n"]*no["riser"] - no["riser"]/2.0
                if lx <= no["x0"]+runA+no["land_len"] else
                no["z_top"] - no["n"]*no["riser"]
                - no["riser"]*((lx-no["x0"]-runA-no["land_len"])/no["tread"]
                               + 0.5))
        print(f"      {nm:10s} 로컬 x {lx:6.2f} · 기준선 {zr:+.3f} · 캡 상면 "
              f"{zr+gsn['cap_top']:+.3f}")
    wx0, _ = _rot90(no["x0"], no["y1"])
    wx1, _ = _rot90(no["x0"], no["y0"])
    print(f"    계단 폭 월드 x [{min(wx0,wx1):.2f}, {max(wx0,wx1):.2f}] ⊂ 데크 "
          f"[{dk['x0']:.2f}, {dk['x1']:.2f}] → "
          f"{'OK' if abs(min(wx0,wx1)-dk['x0'])<1e-6 and abs(max(wx0,wx1)-dk['x1'])<1e-6 else 'FAIL'}")
    # ── grid camera vs new geometry, coordinate check [v6 revision: deck run axis] ──
    gx, gy, gz = _grid_shift()
    print(f"  [그리드] 원점 = 데크 남단 = 나선 개구 연단 "
          f"(x {gx:.2f}, y {gy:.2f}, z {gz:.3f}) · 진행 −Y")
    dk = PARAMS["deck"]
    for d in (2, 5, 10):
        ey = gy + d
        on_deck = dk["y0"] <= ey <= dk["y1"] and dk["x0"] <= gx <= dk["x1"]
        print(f"    d={d:2d}  eye ({gx:+.2f}, {ey:+.2f}, "
              f"{gz+0.3:.2f}~{gz+1.8:.2f}) · 데크 위 "
              f"{'OK' if on_deck else 'FAIL'}")
    print(f"    시선·보행 회랑(데크 x {dk['x0']:.1f}…{dk['x1']:.1f} / 나선 r≤4.2 / "
          f"북측 계단 y 13.0…22.2 [GT-92]) 드레싱 침입: {_corridor_hits()} 개 → "
          f"{'OK' if _corridor_hits() == 0 else 'FAIL'}")

    # ── front profile (grid axis x=3.5, decreasing y) - is the drop GT in the frame ──
    print("  [정면 프로파일] 그리드 축 x=3.50 · y −13.0 → −18.0 (0.25 m 간격)")
    gzw = PARAMS["walk"]["z_top"]
    prof = []
    yy = gy
    while yy >= gy - 5.0:
        top = None
        zz = 6.0
        while zz > -0.60:                      # first solid top face scanning downward
            if _solid_at(gx, yy, zz) is not None:
                top = zz
                break
            zz -= 0.01
        prof.append((yy, top))
        yy -= 0.25
    for yy, top in prof:
        if top is None:
            print(f"    y {yy:+6.2f}  상면 없음(개방) → 지면 {gzw:+.3f} "
                  f"낙차 {gz-gzw:.3f} m")
        else:
            print(f"    y {yy:+6.2f}  상면 {top:+.3f}  (데크면 대비 "
                  f"{top-gz:+.3f})")
    dmax = max((gz - (t if t is not None else gzw)) for _, t in prof)
    print(f"    프로파일 최대 낙차 {dmax:.3f} m ≥ 0.3 → "
          f"{'OK(낙차 GT 프레임 내)' if dmax >= 0.3 else 'FAIL'}")

    # ── h0.3 concealment check (grazing sight line along the near edge) ──
    print("  [h0.3 은닉 검산] 데크 연단(y=−13.0, z 5.000) 스치는 시선")
    for d in (2.0, 5.0, 10.0):
        drop = gz - gzw
        y_hit = gy - drop * d / 0.3
        print(f"    d={d:4.1f} m → 지면 재출현 y {y_hit:8.1f} "
              f"(연단에서 {abs(y_hit-gy):.1f} m 밖) · 그 사이 "
              f"{'전 구간 은닉 OK' if abs(y_hit-gy) > 16.3 else 'FAIL'}")
    print("    ⇒ 나선 개구·디딤·지면이 전부 시선 아래로 숨고 기둥머리 상면"
          "(5.000, 데크 동일면)만 남는다 = negative obstacle 성립")

    # ── camera collision · sight-line blocking check (scene08 convention) ──
    boxes = _obstacle_boxes()
    views = build_views()
    print(f"  [카메라 충돌 검산] 뷰 {len(views)}개 × AABB {len(boxes)}개")
    hits = []
    for name, v in sorted(views.items()):
        ex, ey, ez = v["eye"]
        for bn, x0, x1, y0, y1, z0, z1 in boxes:
            if x0 <= ex <= x1 and y0 <= ey <= y1 and z0 <= ez <= z1:
                hits.append((name, bn))
        s = _solid_at(ex, ey, ez)
        if s is not None:
            hits.append((name, f"{s}(지형 매몰)"))
    for name, bn in hits:
        print(f"    [FAIL] {name} eye 가 {bn} 내부")
    print(f"    충돌: {len(hits)}건 → {'OK' if not hits else 'FAIL'}")
    print("    [시선 차단] 미장센 컷 ray march 0.1 m (첫 차단 비율 ≥ 0.90 = OK)")
    print("      ※ preset_* 그리드는 pitch −10°(d2 의 h0.9/h1.8 은 v7 에서")
    print("        −20/−28°)로 **바닥을 겨냥**하는 규약이라 tgt 가 데크면")
    print("        아래에 놓인다 — 차단 검사 대상이 아니다.")
    blocked = []
    for name, v in sorted(views.items()):
        if name.startswith("preset_"):
            continue
        e = np.array(v["eye"], dtype=float)
        tg = np.array(v["tgt"], dtype=float)
        Ln = float(np.linalg.norm(tg - e))
        frac, hit = 1.0, None
        for k in range(1, int(Ln / 0.1) + 1):
            f = k * 0.1 / Ln
            s = _solid_at(*(e + (tg - e) * f))
            if s is not None:
                frac, hit = f, s
                break
        ok = frac >= 0.90
        print(f"      {name:18s} 첫 차단 {frac:5.2f} "
              f"({hit if hit else '없음'}) → {'OK' if ok else 'FAIL'}")
        if not ok:
            blocked.append(name)
    print(f"      차단 컷: {blocked if blocked else '없음 → OK'}")

    # ── [v7] sight axis <-> sun azimuth alignment (lambert per shot) ──
    #   lesson (judge_v7): move the axis and the sun must move with it. A per-face table alone
    #   cannot tell "which shot is backlit" -> derive it from the **lit-face normal per shot**.
    azd = 33.5 + float(PARAMS["SUN_AZ_OFFSET"])
    el = math.radians(float(PARAMS["light"]["noon_sun_elev"]))
    lx = math.cos(math.radians(azd)) * math.cos(el)
    ly = math.sin(math.radians(azd)) * math.cos(el)
    lz = math.sin(el)
    print(f"  [v7 태양] offset {PARAMS['SUN_AZ_OFFSET']:.1f} → 월드 az "
          f"{azd:.1f}° (그림자 az {azd - 180:.1f}°) · 고도 "
          f"{math.degrees(el):.2f}°")
    for nm, N in (("+Y향(그리드 피사면)", (0, 1, 0)),
                  ("−X향(spiral_up 피사면)", (-1, 0, 0)),
                  ("−Y향(데크 남단 페시아)", (0, -1, 0)),
                  ("+X향", (1, 0, 0)),
                  ("상면(데크·디딤·지면)", (0, 0, 1))):
        d = N[0] * lx + N[1] * ly + N[2] * lz
        print(f"    {nm:<24} lambert {d:+.3f} "
              f"{'순광' if d > 0.15 else ('터미네이터' if d > 0 else '음영')}")
    print("    [컷별] 시선 방위 → 피사면 법선(시선+180°) 의 직사광 lambert")
    worst = None
    for name, vv in sorted(views.items()):
        e, t = vv["eye"], vv["tgt"]
        gaze = math.degrees(math.atan2(t[1] - e[1], t[0] - e[0])) % 360.0
        nrm = (gaze + 180.0) % 360.0
        lam = math.cos(math.radians(nrm - azd)) * math.cos(el)
        if name.startswith("preset_") and name != "preset_h0.3_d2":
            continue                      # the 9 grid shots share one axis - one representative shot
        tag = "그리드 대표" if name.startswith("preset_") else ""
        worst = lam if worst is None else min(worst, lam)
        print(f"      {name:<16} 시선 {gaze:6.1f}° · 법선 {nrm:6.1f}° · "
              f"lambert {lam:+.3f} {'순광' if lam > 0.15 else '역광/터미네이터'}"
              f" {tag}")
    print(f"      최저 컷 lambert {worst:+.3f} (>0.15 = 전 컷 순광 → "
          f"{'OK' if worst > 0.15 else 'CHECK'})")
    dk = PARAMS["deck"]
    rb = PARAMS["rail_bay"]
    sdx = -math.cos(math.radians(azd)) * math.cos(el) / math.sin(el)
    sdy = -math.sin(math.radians(azd)) * math.cos(el) / math.sin(el)
    x_sh = dk["x0"] + sdx * rb["post_h"]
    print(f"    [근경 데크 그림자] 서측 난간(x {dk['x0']:.1f}, h "
          f"{rb['post_h']:.2f}) 그림자 → x {x_sh:+.2f} (데크 폭 "
          f"{dk['x0']:.1f}…{dk['x1']:.1f} 중 "
          f"{max(0.0, x_sh - dk['x0']) / (dk['x1'] - dk['x0']) * 100:.0f} % "
          f"점유) · y 이동 {sdy * rb['post_h']:+.2f}(시선 진행방향)")

    # ── [v7] d2 preset framing : is the drop GT inside the frame ──
    #   vertical half FOV 18.0 deg (focal 18.147 / vertical aperture 11.787). A target at
    #   depression dep is in frame when |−pitch − dep| <= 18.
    print("  [v7 프레이밍] d2 프리셋 (연단 2.0 m 앞) — 피치 하향 근거")
    gzw = PARAMS["walk"]["z_top"]
    for h, pit in ((0.3, -10.0), (0.9, -20.0), (1.8, -28.0)):
        row = []
        for nm, ahead, dz, need in (("연단", 2.0, h, True),
                                    ("디딤(방위270°)", 5.0, h + 1.540, True),
                                    ("보이드 저면", 3.5, h + gz - gzw, False)):
            dep = math.degrees(math.atan2(dz, ahead))
            ok = abs(-pit - dep) <= 18.0
            mark = ("OK" if ok else "밖") if need else ("밖=은닉" if not ok
                                                       else "노출")
            row.append(f"{nm} {dep:5.1f}°[{mark}]")
        print(f"    h{h}_d2 pitch {pit:+.0f}° (프레임 {-pit - 18:.1f}…"
              f"{-pit + 18:.1f}° 부각) : " + " · ".join(row))
    print("    ※ 보이드 저면(5.0 m 아래)이 프레임 밖인 것은 결함이 아니라 이 씬의")
    print("      GT 그 자체 — 연단·디딤만 보이고 바닥은 안 보이는 것이 은닉이다.")
    print("    ※ h0.3 은 연단 부각 8.5° 로 −10° 유지 — 피치를 내리면 지평선이")
    print("      프레임 밖이 되어 grazing 연속 평면 오독(GT 양성 축)이 깨진다.")
    print("=" * 68)


def _grid_shift():
    """[v6 revision · supervisor approved] grid origin = **deck south end = edge of the
    spiral opening** (3.5, −13.0, 5.000). The old origin (west end of the spiral outer
    edge, at grade) had no drop in front of the robot, so an h0.3 concealment judgement
    was impossible — the same argument as the scene11 precedent."""
    dk = PARAMS["deck"]
    return ((dk["x0"] + dk["x1"]) / 2.0, dk["y0"], dk["z_top"])


def _to_world(p, org):
    """Map grid_views local (+X travel, origin 0) → world (−Y travel, origin org).
    Rotation R = rotZ(−90°): (lx, ly) → (ly, −lx). The local eye (−d, 0, h) becomes
    world (gx, gy+d, gz+h), standing d north of the origin and h above the deck face."""
    gx, gy, gz = org
    lx, ly, lz = p
    return [gx + ly, gy - lx, gz + lz]


def _corridor_hits():
    """[v6 revision] sight corridor = (1) the deck run corridor (x 2…5, y −13…13, grid axis)
    (2) the front of the spiral opening (r ≤ 4.2 from the centre — the h0.3 near frame)
    (3) [GT-92] the north stair corridor (x 2…5 ⊕ tree AABB 1.1, y 13…22.2 ⊕ 1.1 at the
    foot) — the band (1)/(2) never covered, which is exactly where the (3.6, 20.2) tree
    stood through flight B until this row.
    Dressing (street trees·lamps·bollards·benches·stop pole) entering here would hide
    the drop or block the walked route → the count must be 0."""
    d = PARAMS["dress"]
    sp = PARAMS["spiral"]
    dk = PARAMS["deck"]
    no = PARAMS["north"]
    ny0 = no["pivot"][1]
    ny1 = ny0 + 2.0 * no["n"] * no["tread"] + no["land_len"]
    pts = list(d["trees"]) + [(x, y) for x, y in d["lamps"]] \
        + [(x, y) for x, y in d["bollards"]] \
        + [(b[0], b[1]) for b in d["benches"]] + [d["bus_pole"][:2]]
    n = 0
    for x, y in pts:
        if dk["x0"] <= x <= dk["x1"] and dk["y0"] <= y <= dk["y1"]:
            n += 1
        elif math.hypot(x - sp["cx"], y - sp["cy"]) <= 4.2:
            n += 1
        elif dk["x0"] - 1.1 <= x <= dk["x1"] + 1.1 and ny0 <= y <= ny1 + 1.1:
            n += 1
    return n


# ===========================================================================
# [D] camera presets - grid_views (ground approach, +X) + 5 mise-en-scene shots
# ===========================================================================
def build_views():
    """[v6 revision] the grid is moved onto the **deck run axis (−Y)** (supervisor approved).
    Origin = deck south end (3.5, −13.0, 5.000) = edge of the spiral well.
    eye = (3.5, −13+d, 5.0+h) · sight line −Y · pitch −10°.
    The first thing to judge is whether, at robot h0.3, the column-head top (5.000,
    flush with the deck) and the far ground read as one continuous plane, concealing the
    annular void (drop 5.005 m) and the spiral descent. The ground approach is preserved
    as ground_approach / ground_graze."""
    org = _grid_shift()
    # [v7 verdict §4 (3)(b)] lower the d2 preset pitch - the **near ground fell outside the frame**.
    #   vertical half FOV 18.0 deg · pitch −10 deg -> frame bottom −28 deg. At d2, only 2 m from
    #   the edge, the depression to the edge is h0.9 -> 24.2 deg · h1.8 -> **42.0 deg**, so at h1.8
    #   the deck face, the edge and the opening all dropped below the frame, leaving only dark background.
    #   -> lower the pitch for d2 only, **putting the edge and the annular void in frame**:
    #        h0.9_d2 −20 deg (bottom 38.0 deg > 24.2 deg) · h1.8_d2 −28 deg (bottom 46.0 deg > 42.0 deg)
    #   h0.3_d2 stays at −10 deg - the edge depression is only 8.5 deg, and lowering the pitch
    #   pushes the horizon out of frame, breaking the **grazing continuous-plane misread**
    #   (the GT-positive axis of this scene). d5/d10 stay at −10 deg at every height (depression <= 24 deg).
    v = sc.grid_views(0.0, dists=(5, 10))
    v.update(sc.grid_views(0.0, heights=(0.3,), dists=(2,)))
    v.update(sc.grid_views(0.0, heights=(0.9,), dists=(2,), pitch=-20))
    v.update(sc.grid_views(0.0, heights=(1.8,), dists=(2,), pitch=-28))
    out = {}
    for k, val in v.items():
        out[k] = dict(eye=_to_world(val["eye"], org),
                      tgt=_to_world(val["tgt"], org))
    # spiral_up: looking up from inside the spiral. [v6 verdict C-8] the old shot (eye east at
    #   x6.13, facing west) lost 90 % of the frame to the **shaded outer wall + dark deck soffit**.
    #   The front-lit axis = **putting the sight line on +X**. Standing at the spiral bottom
    #   (entry passage side, azimuth 135 deg, r 2.55) and looking up-slope (azimuth 45 deg, r 2.55)
    #   gives sight azimuth 0 deg and lit-face normal 180 deg -> 35 deg from sun az 145 = lambert +0.529, front lit
    #   (it was +0.585 at the v6 az 205 as well, and stays front lit after the v7 reselection).
    #   [v7 verdict §4 (3)] "60 % of the frame is distant brick facade" -> keep eye as-is
    #   (its value is pinned by the 1.8 m column clearance and passage headroom checks) and
    #   **raise tgt only**, lifting the pitch +11.0 deg -> +18.8 deg. The sight end (x 5.30,
    #   r 2.55, azimuth 45 deg) sits at z 2.75, below the landing underside (4.498), so the frame
    #   top is capped by the **landing soffit** and the tread ribbon (azimuth 0~300 deg, z 1.9~2.9) fills the lower and middle frame.
    out["spiral_up"] = dict(eye=[1.70, -11.20, 1.45], tgt=[5.30, -11.20, 2.75])
    # deck_entry: entering the spiral descent from the deck (pedestrian view h1.6).
    out["deck_entry"] = dict(eye=[3.50, -9.50, 6.60], tgt=[4.60, -14.60, 4.30])
    # broken_rail: close-up of the upper outer-guard arc (azimuth 225 deg, r3.3, z 4.155).
    #   [08-05] the missing-rail hazard is gone (continuous guard doctrine); the
    #   name is kept so regression rounds keep pairing.
    #   eye to the southwest - lit-face normal 203.2 deg, 58 deg from sun az 145 -> lambert
    #   +0.340 (lower than the +0.645 at v6 az 205 but still front lit, SMOKE per-shot table).
    out["broken_rail"] = dict(eye=[-1.42, -16.44, 5.60],
                              tgt=[1.17, -15.33, 4.16])
    # ground_approach: h0.9 shot preserving the old grid axis (ground sidewalk approach, west -> east).
    #   tgt aims above the entry passage so it does not fall inside the central column (r0.5).
    out["ground_approach"] = dict(eye=[-6.30, -13.00, 0.90],
                                  tgt=[2.30, -13.40, 1.60])
    # ground_graze: oblique ground grazing - shot reinforcing the cylindrical-silhouette concealment.
    out["ground_graze"] = dict(eye=[-5.00, -17.50, 0.35],
                               tgt=[3.20, -12.60, 0.90])
    # overview: high-angle view of the whole overpass (roadway·deck·spiral·north stair at once).
    #   [v7] moving the sun az 205 -> 145 kills the lit face of the old viewpoint (southwest
    #   −16,−28; normal 228 deg) at lambert +0.074 = the terminator. Pulling the viewpoint west
    #   to (−20,−16) turns the lit-face normal to 207 deg, giving +0.303, front lit.
    #   framing check (horizontal half FOV 30 deg · vertical 18 deg): spiral centre yaw +19.8 deg,
    #   depression 24.1 deg (+0.3 deg against pitch −24.4 deg) · north stair yaw −27.9 deg, depression 17.0 deg
    #   -> spiral, deck, roadway and north stair are all in frame (SMOKE [v7 framing]).
    out["overview"] = dict(eye=[-20.00, -16.00, 15.00], tgt=[3.50, -4.00, 3.00])
    return out


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. h0.3 그리드(데크 종주) — 기둥머리 상면(5.000)과 원측 지면이 하나의 평면으로
                            읽혀 환형 보이드(5.005 m)·나선 하강이 은닉되나
 2. broken_rail    — [GT-76] 캡이 run 당 1本 연속(꺾임·틈 0)인가 · 업스탠드 상면이
                     계단상 디딤 연단을 덮어 톱니가 사라졌는가 · 판이 슈/캡에 물렸는가
 3. spiral_up      — 나선 내부 상행(피치 +19°): 랜딩 소핏이 상단을 막았나
 3b. d2 프리셋      — h0.9/h1.8 은 pitch −20/−28° : 연단·디딤이 프레임 안인가
 3c. 태양 az 145    — 그리드 피사면(+Y향)·deck_entry 상반의 암부가 걷혔나
 4. deck_entry     — 데크 → 원형 랜딩 → 단 0 접속(단차 0.002/0.190) 연속성
 5. ground_approach/graze — 지상 접근에서 진입 통로·내측 보이드가 읽히나
 6. overview       — [GT-76] 나선·데크·북측 계단이 **하나의 제품**으로 읽히는가
                     (업스탠드+슈+유리+브론즈 캡 1계열 · 캡 라인 6.100 전 구간 동일)
 7. 데크 난간      — 유리 베이 + 연속 캡 · 종단 뉴얼(동측 연단/랜딩/북측) 마감
 8. 경계·지평      — 식재대·가로수 열·원경 수목 띠로 지평이 폐쇄됐나
 9. [GT-92] 접속    — 서측 에이프런 개구(잼 뉴얼 2본, 유효 2.742 m)로 데크→로브→
                     단0 이 열렸는가 · 동측 에이프런 베이는 폐쇄 유지(az0 로브 연단)
                     · 북측 계단 회랑에 수목 0(구 (3.6,20.2) → (−3.4,20.2))"""


# ===========================================================================
# [E] main
# ===========================================================================
def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    if os.environ.get("NEGOBS_SMOKE", "0") == "1":
        _smoke_report()
        return

    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])
    simulation_app = sc.boot(capture_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from pxr import UsdGeom
    from omni.kit.viewport.utility import (get_active_viewport,
                                           capture_viewport_to_file)
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    ROOT = "/World/Scene06"
    UsdGeom.Xform.Define(stage, ROOT)

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    sp = PARAMS["spiral"]
    CX, CY = sp["cx"], sp["cy"]

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *a, **kw):
        return sc.make_pbr(stage, path, *a, **kw)

    # -------------------------------------------------------------------
    # materials
    # -------------------------------------------------------------------
    def setup_materials():
        s = mp["scale"]
        M = {}
        M["paving"] = PBR(f"{ROOT}/Looks/Paving",
                          sc.tex_path("paving_interlock", "diff"),
                          sc.tex_path("paving_interlock", "nor"),
                          sc.tex_path("paving_interlock", "rough"),
                          s["paving_interlock"])
        M["concrete"] = PBR(f"{ROOT}/Looks/Concrete",
                            sc.tex_path("concrete_wall", "diff"),
                            sc.tex_path("concrete_wall", "nor"),
                            sc.tex_path("concrete_wall", "rough"),
                            s["concrete_wall"], tint=mp["concrete_tint"])
        M["deck"] = PBR(f"{ROOT}/Looks/DeckConcrete",
                        sc.tex_path("concrete_wall", "diff"),
                        sc.tex_path("concrete_wall", "nor"),
                        sc.tex_path("concrete_wall", "rough"),
                        s["concrete_wall"] * 1.6, tint=mp["deck_tint"])
        # fascia·parapet·cheek - separate scale (3.2 m) so the formwork joints read large
        M["fascia"] = PBR(f"{ROOT}/Looks/Fascia",
                          sc.tex_path("concrete_wall", "diff"),
                          sc.tex_path("concrete_wall", "nor"),
                          sc.tex_path("concrete_wall", "rough"),
                          s["concrete_wall"] * 1.6, tint=mp["parapet_tint"])
        M["grime"] = PBR(f"{ROOT}/Looks/Grime",
                         diffuse_color=mp["grime_color"],
                         roughness_const=mp["grime_rough"])
        M["soil"] = PBR(f"{ROOT}/Looks/Soil", sc.tex_path("grass", "diff"),
                        sc.tex_path("grass", "nor"),
                        sc.tex_path("grass", "rough"), 1.2,
                        tint=mp["soil_tint"])
        M["curb"] = PBR(f"{ROOT}/Looks/Curb",
                        sc.tex_path("granite_dark", "diff"),
                        sc.tex_path("granite_dark", "nor"),
                        sc.tex_path("granite_dark", "rough"), s["granite_dark"])
        # [W3 S06 · S06-B item 3] the kerb must NOT reuse `granite_dark` — scene01 recorded
        #   that it "reads as a black hole", and G6's kerb is pale grey flamed granite.
        #   S06-B asks for a `curb_granite_light` **texture role**; no such role exists in
        #   `scene_common.TEX` and asset procurement is not this lane's, so the light granite
        #   is made here from the granite maps with a lightening tint. The prim path token
        #   `Curb` is what routes it to `LOOK_CLASS["curb"]`, i.e. to the R10 arris.
        M["curb_light"] = PBR(f"{ROOT}/Looks/CurbGraniteLight",
                              sc.tex_path("granite_dark", "diff"),
                              sc.tex_path("granite_dark", "nor"),
                              sc.tex_path("granite_dark", "rough"),
                              s["granite_dark"], tint=mp["curb_light_tint"])
        M["brick"] = PBR(f"{ROOT}/Looks/Brick",
                         sc.tex_path("brick_red", "diff"),
                         sc.tex_path("brick_red", "nor"),
                         sc.tex_path("brick_red", "rough"), s["brick_red"])
        M["grass"] = PBR(f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
                         sc.tex_path("grass", "nor"),
                         sc.tex_path("grass", "rough"), s["grass"],
                         tint=mp["grass_tint"])
        M["tactile"] = PBR(f"{ROOT}/Looks/Tactile",
                           sc.tex_path("tactile", "diff"),
                           sc.tex_path("tactile", "nor"), None, s["tactile"])
        M["asphalt"] = PBR(f"{ROOT}/Looks/Asphalt",
                           diffuse_color=mp["asphalt_color"],
                           roughness_const=mp["asphalt_rough"])
        M["line_w"] = PBR(f"{ROOT}/Looks/LineWhite",
                          diffuse_color=mp["line_white"], roughness_const=0.7)
        M["line_y"] = PBR(f"{ROOT}/Looks/LineYellow",
                          diffuse_color=mp["line_yellow"], roughness_const=0.7)
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        M["steel"] = PBR(f"{ROOT}/Looks/Steel", diffuse_color=mp["steel_color"],
                         metallic=mp["steel_metallic"],
                         roughness_const=mp["steel_rough"])
        M["panel"] = PBR(f"{ROOT}/Looks/Panel", diffuse_color=mp["panel_color"],
                         roughness_const=mp["panel_rough"])
        M["pole"] = PBR(f"{ROOT}/Looks/Pole", diffuse_color=mp["pole_color"],
                        metallic=mp["pole_metallic"],
                        roughness_const=mp["pole_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"])
        # [v6 verdict C-3] the old parapet = untextured flat panel (styrofoam impression) ->
        #   concrete diff/nor/rough + neutral tint (albedo 0.435). Coping and soiling band are
        #   given as separate prims in build_north / build_cues.
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           sc.tex_path("concrete_wall", "diff"),
                           sc.tex_path("concrete_wall", "nor"),
                           sc.tex_path("concrete_wall", "rough"),
                           s["concrete_wall"], tint=mp["parapet_tint"])
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["leaf_a"] = PBR(f"{ROOT}/Looks/LeafA", diffuse_color=mp["leaf_a"],
                          roughness_const=1.0, specular_level=0.0)
        M["leaf_b"] = PBR(f"{ROOT}/Looks/LeafB", diffuse_color=mp["leaf_b"],
                          roughness_const=1.0, specular_level=0.0)
        # [W3 S06 · G6] foreground boundary materials
        M["guard_wood"] = PBR(f"{ROOT}/Looks/GuardWood",
                              diffuse_color=mp["guard_wood"],
                              roughness_const=0.82)
        M["guard_band"] = PBR(f"{ROOT}/Looks/GuardBand",
                              diffuse_color=mp["guard_band"],
                              roughness_const=0.45)
        M["mesh"] = PBR(f"{ROOT}/Looks/MeshFence",
                        diffuse_color=mp["mesh_green"], roughness_const=0.55)
        M["rubble"] = PBR(f"{ROOT}/Looks/Rubble",
                          sc.tex_path("granite_dark", "diff"),
                          sc.tex_path("granite_dark", "nor"),
                          sc.tex_path("granite_dark", "rough"), 0.55,
                          tint=mp["rubble"])
        M["nosing"] = PBR(f"{ROOT}/Looks/Nosing",
                          diffuse_color=mp["nosing_color"],
                          roughness_const=0.7)
        # [v5.2 user] arbitrary warning sign removed - sign panel material creation deleted.
        return M

    # -------------------------------------------------------------------
    # ground · roadway · sidewalk · kerb · lane markings
    # -------------------------------------------------------------------
    def build_site(M):
        g = PARAMS["ground"]
        BOX(f"{ROOT}/Ground",
            ((g["x0"]+g["x1"])/2.0, (g["y0"]+g["y1"])/2.0,
             g["z_top"] - g["thick"]/2.0),
            (g["x1"]-g["x0"], g["y1"]-g["y0"], g["thick"]), M["grass"], col=True)
        rd = PARAMS["road"]
        BOX(f"{ROOT}/Road",
            ((rd["x0"]+rd["x1"])/2.0, (rd["y0"]+rd["y1"])/2.0,
             rd["z_top"] - rd["thick"]/2.0),
            (rd["x1"]-rd["x0"], rd["y1"]-rd["y0"], rd["thick"]),
            M["asphalt"], col=True)
        wk = PARAMS["walk"]
        for i, (ya, yb) in enumerate(((wk["ys0"], wk["ys1"]),
                                      (wk["yn0"], wk["yn1"]))):
            BOX(f"{ROOT}/Walk_{i}",
                ((wk["x0"]+wk["x1"])/2.0, (ya+yb)/2.0,
                 wk["z_top"] - wk["thick"]/2.0),
                (wk["x1"]-wk["x0"], yb-ya, wk["thick"]), M["paving"], col=True)
        # [W3 S06 · S06-B] kerb = `infra_kit.build_curb_line`, unit blocks + L-gutter.
        cb = PARAMS["curb"]
        ok, bevel, note = ik.check_arris_role(sc)
        print(f"[S06-B] arris role · {note} · {'OK' if ok else 'MISMATCH'}")
        ikit = ik.kit_from_scene_common(sc, stage)
        s_lo = cb["lod_x"][0] - wk["x0"]          # arc length runs from p0 at x0
        s_hi = cb["lod_x"][1] - wk["x0"]
        curb_res = []
        for i, (ye, side) in enumerate(((rd["y0"], "left"), (rd["y1"], "right"))):
            res = ik.build_curb_line(
                ikit, f"{ROOT}/CurbLine_{i}",
                (wk["x0"], ye), (wk["x1"], ye), M["curb_light"],
                height=cb["height"], width=cb["width"], unit=cb["unit"],
                gutter=True, z_road=rd["z_top"], walk_z=wk["z_top"],
                road_side=side, embed=cb["embed"],
                lod_span=(s_lo, s_hi), far_unit=cb["far_unit"],
                joint_mtl=M["grime"], gutter_mtl=M["curb_light"],
                collider=True)
            curb_res.append(res)
            print(f"[S06-B] CurbLine_{i} · blocks {res.get('n_block', '?')} · "
                  f"prims {res.get('prim_count', '?')} "
                  f"({res.get('prims_per_m', 0.0):.3f}/m) · "
                  f"gt_drop {res.get('gt_drop', 0.0):.3f} · "
                  f"hazard {res.get('is_gt_hazard')} · warn {res.get('warnings')}")
        # [v6 verdict C-2] verge - one row bounding the outside of the sidewalk (edging + ground cover).
        #   near-field boundary that stops the sidewalk meeting grass on a hard edge, i.e. an "empty lot".
        vg = PARAMS["verge"]
        vx0, vx1 = vg["x0"], vg["x1"]
        for i, (ya, yb) in enumerate(((wk["ys0"] - vg["w"], wk["ys0"]),
                                      (wk["yn1"], wk["yn1"] + vg["w"]))):
            # edging (2 lines, sidewalk side and grass side)
            for j, yc in enumerate((ya + vg["curb_t"]/2.0,
                                    yb - vg["curb_t"]/2.0)):
                BOX(f"{ROOT}/VergeCurb_{i}_{j}",
                    ((vx0+vx1)/2.0, yc, vg["curb_top"] - 0.22),
                    (vx1-vx0, vg["curb_t"], 0.44), M["curb"], col=True)
            BOX(f"{ROOT}/VergeSoil_{i}",
                ((vx0+vx1)/2.0, (ya+yb)/2.0, vg["soil_top"] - 0.20),
                (vx1-vx0, (yb-ya) - 2*vg["curb_t"], 0.40), M["soil"], col=True)

    def build_lanes(M):
        ln = PARAMS["lane"]
        for i, y in enumerate(ln["center_ys"]):
            BOX(f"{ROOT}/CenterLine_{i}",
                ((ln["x0"]+ln["x1"])/2.0, y, ln["z"]),
                (ln["x1"]-ln["x0"], ln["w"], ln["t"]), M["line_y"])
        period = ln["seg"] + ln["gap"]
        ndash = int((ln["x1"] - ln["x0"]) / period)
        for j, y in enumerate(ln["dash_ys"]):
            for k in range(ndash):
                xc = ln["x0"] + k*period + ln["seg"]/2.0
                BOX(f"{ROOT}/Dash_{j}_{k}", (xc, y, ln["z"]),
                    (ln["seg"], ln["w"], ln["t"]), M["line_w"])

    # -------------------------------------------------------------------
    # spiral stair + central column + circular landing
    # -------------------------------------------------------------------
    def build_spiral(M):
        # [W3 S06 · GT-6 / K4(d)] treads as **true annular sectors**. `mesh=True` is the
        #   K4(d) mechanism that landed default-OFF at `5ceb76a`; this scene is the pilot
        #   that turns it on, which is where GT-6 said the split proof would actually be
        #   judged. r_in / r_out / azimuths / tread z-ladder are passed unchanged — the
        #   only thing that changes is that the solid now STOPS at the design rays instead
        #   of overshooting them by margin*r_out/r_in = 7.08x at the inner radius.
        sc.build_helix_steps(stage, f"{ROOT}/Spiral", CX, CY, sp["r_in"],
                             sp["r_out"], sp["a0"], _step_deg(), sp["n"],
                             sp["riser"], sp["z0"], M["concrete"],
                             ccw=True, collider=True,
                             base_drop=sp["base_drop"],
                             mesh=sp["mesh"], arc_seg=sp["arc_seg"])
        # [W3 S06 · G6] **stepped** fascia — one sector per tread, pinned below that tread's
        #   own face. This is GT-6's "fascia stepped" term and it is what produces G6's
        #   scalloped outer rim. No interpolated top line survives, so the ±154/−38 mm
        #   sawtooth is not reduced, it is structurally absent.
        fa = PARAMS["fascia"]
        sd = _step_deg()
        for i in range(sp["n"]):
            a_i = sp["a0"] + i * sd
            ft = _spiral_top_z(i) - fa["drop_below"]
            sc._annular_sector_mesh(
                stage, f"{ROOT}/SpiralFascia/Seg_{i}", CX, CY,
                fa["r_in"], fa["r_out"], a_i, a_i + sd,
                ft - fa["thick"], ft, M["fascia"], collider=False,
                arc_seg=fa["arc_seg"])
        # [W3 S06 · G6 · NF-1] the **continuous helicoid soffit** — the one element G6
        #   settles outright, and the reason K4(d)'s true-sector mesh was made mandatory
        #   rather than budget-optional: a stack of boxes cannot produce it. `top_face=True`
        #   is the NF-1 correction, so the surface lands where it is asked to.
        a_lo, a_hi = _fascia_span()
        so = PARAMS["soffit"]
        sc.build_helix_ramp(stage, f"{ROOT}/SpiralSoffit", CX, CY,
                            so["r_in"], so["r_out"], a_lo, a_hi,
                            max(8, int(round((a_hi-a_lo) * so["seg_per_deg"]))),
                            _soffit_z(a_lo), _soffit_z(a_hi), so["thick"],
                            M["concrete"], collider=False,
                            top_face=so["top_face"])
        co = PARAMS["column"]
        CYL(f"{ROOT}/Column", (CX, CY, (co["z_top"]+co["z_bot"])/2.0),
            co["r"], co["z_top"]-co["z_bot"], M["concrete"], col=True)
        la = PARAMS["landing"]
        # [W3 S06 · GT-6] landing = **two lobes**, clipped at the deck edge azimuth, built as
        #   true sectors. The old note here recorded a 0.11 deg overshoot past 180 deg as
        #   "no effect"; with `mesh=True` the overshoot is 0.00 deg by construction, and the
        #   9.196 m² slab interpenetration the full annulus caused is down to 4.166 m².
        for k, (pa0, pa1) in enumerate(_landing_arcs()):
            nseg = max(2, int(round(la["seg"] * (pa1 - pa0) / 180.0)))
            sc.build_arc_steps(stage, f"{ROOT}/Landing_{k}", CX, CY, la["r_in"],
                               la["r_out"], pa0, pa1, nseg,
                               la["top_z"], la["base_z"], M["deck"],
                               mesh=la["mesh"], arc_seg=la["arc_seg"])

    # -------------------------------------------------------------------
    # overpass deck + support columns
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # [W2-D] ground_kit — P9 bridge_deck. Deck top (z=5.000), travel -Y.
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["gkit"]
        dk = PARAMS["deck"]
        gp = gk.plan_ground(
            "bridge_deck",
            region=(dk["x0"], dk["y0"], dk["x1"], dk["y1"]),
            z=dk["z_top"], gy=0.0,
            origin=(3.5, dk["y0"], dk["z_top"]), axis="-y",
            edges=[("well_edge", 0.0)],
            dists=(2, 5, 10), scene="scene06",
            tactile=(),                 # §12.4 - hold (supervisor call, M10)
            overrides=dict(pave=dict(module=(None, None), joint="expansion",
                                     step_x=None, step_y=g["joint_step"]),
                           infra=dict(gully=len(g["gully"]))),
            sites=dict(gully=[tuple(v) for v in g["gully"]]),
            extras_args=dict(wear_lane=dict(centerline=tuple(g["wear"]),
                                            width=g["wear_w"])),
            seed=6)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["curb"], crack=M["curb"], gully=M["steel"],
                  wear=M["curb"], stain_water=M["curb"], stain_drip=M["curb"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris,
                              slabs=(f"{ROOT}/Deck",))
        print(f"[ground_kit] scene06 P9 · prims {res['prims']} · "
              f"delta_max {res['gt_delta_max']:.4f} · "
              f"unit_cell {res['unit_cell']}")
        return res

    def build_deck(M):
        dk = PARAMS["deck"]
        # [W2-0 · P-A] Registered before the slab exists, because `_skin_wanted`
        # is evaluated inside `sc.add_box`. (The deck is 3.0 m wide, i.e. under
        # the 4.0 m skin threshold today, so this is a forward guard.)
        sc.skin_exclude(f"{ROOT}/Deck")
        BOX(f"{ROOT}/Deck",
            ((dk["x0"]+dk["x1"])/2.0, (dk["y0"]+dk["y1"])/2.0,
             dk["z_top"] - dk["thick"]/2.0),
            (dk["x1"]-dk["x0"], dk["y1"]-dk["y0"], dk["thick"]),
            M["deck"], col=True)
        # [08-06 orchestrator, GT-76 pass 2 — "naturally continuous form"] The landing
        #   lobes are UV-less meshes, so the tile texture flattens to its average tone
        #   there; where a lobe sliver laps the deck plan the pale patch read as a
        #   curved intrusion into the tiled field (`deck_entry`). A 4 mm tiled apron
        #   overlay (a BOX — real UVs) covers the junction zone with one straight
        #   threshold edge, so deck→landing reads as an intended paving→concrete
        #   material break at a threshold, not as a stain. Dressing only: +4 mm lip,
        #   same idiom as the scene13 walk plates (proud 0.150 precedent).
        sc.skin_exclude(f"{ROOT}/DeckApronTile")
        BOX(f"{ROOT}/DeckApronTile",
            ((dk["x0"]+dk["x1"])/2.0, dk["y0"] + 1.30,
             dk["z_top"] + 0.002),
            (dk["x1"]-dk["x0"], 2.60, 0.004), M["deck"])
        # [W3 S06 · G6] tapered V-form pillars
        dp = PARAMS["deck_posts"]
        z1 = dk["z_top"] - dk["thick"]
        for i, py in enumerate(dp["ys"]):
            # footing pad — the V springs from one block, which is what makes it read as a V
            BOX(f"{ROOT}/DeckFoot_{i}", (dp["x"], py, dp["z_bot"] + 0.22),
                (1.10, 1.10, 0.44), M["concrete"], col=True)
            z0 = dp["z_bot"] + 0.36
            H = z1 - z0
            tilt = math.degrees(math.atan2(dp["splay"], H))
            L = math.hypot(dp["splay"], H)         # true leg length along its own axis
            # The splay opens **across the deck (+-X)**, not along it. Two reasons, both
            # measured: (a) the V then reads frontally, which is the axis `overview`,
            # `ground_approach` and `ground_graze` actually look down; (b) a +-Y splay of
            # 0.95 m would push the south leg head to y −9.95, i.e. 0.25 m INSIDE the
            # spiral's r_out 3.30 plan footprint (centre distance 4.000 − 3.30 = 0.70 m of
            # clearance is all there is). Across the deck the leg heads sit at x 2.55/4.45,
            # inside the 3.0 m deck width and 4.11 m from the spiral centre.
            for s, sgn in enumerate((-1.0, 1.0)):
                for k in range(dp["n_seg"]):
                    tm = (k + 0.5) / float(dp["n_seg"])
                    rr = dp["leg_r0"] + (dp["leg_r1"] - dp["leg_r0"]) * tm
                    CYL(f"{ROOT}/DeckPost_{i}/Leg_{s}_{k}",
                        (dp["x"] + sgn * dp["splay"] * tm, py, z0 + H * tm),
                        rr, L / dp["n_seg"] * 1.06, M["concrete"],
                        rotY=sgn * tilt, col=(k == 0))
            # column-head cap beam spanning the two leg heads
            BOX(f"{ROOT}/DeckCap_{i}", (dp["x"], py, z1 - 0.16),
                (dk["x1"]-dk["x0"]+0.4, 0.9, 0.32), M["concrete"])

    # -------------------------------------------------------------------
    # north entry stair (rot_group 90 deg)  - local +X descent -> world +Y descent
    # -------------------------------------------------------------------
    def build_north(M):
        no = PARAMS["north"]
        RG = sc.build_rot_group(stage, f"{ROOT}/NorthGroup",
                                no["pivot"], no["rot"])
        runA = no["n"] * no["tread"]
        z_mid = no["z_top"] - no["n"]*no["riser"]
        # upper flight
        sc.build_straight_stairs(stage, f"{RG}/FlightA", no["x0"], no["y0"],
                                 no["y1"], no["riser"], no["tread"], no["n"],
                                 no["base_z"], M["concrete"],
                                 z_top=no["z_top"], collider=True)
        # mid-landing
        lx0 = no["x0"] + runA
        lx1 = lx0 + no["land_len"]
        BOX(f"{RG}/MidLanding",
            ((lx0+lx1)/2.0, (no["y0"]+no["y1"])/2.0,
             (z_mid + no["base_z"])/2.0),
            (lx1-lx0, no["y1"]-no["y0"], z_mid-no["base_z"]),
            M["concrete"], col=True)
        # lower flight
        sc.build_straight_stairs(stage, f"{RG}/FlightB", lx1, no["y0"],
                                 no["y1"], no["riser"], no["tread"], no["n"],
                                 no["base_z"], M["concrete"],
                                 z_top=z_mid, collider=True)
        # [GT-76] stringer upstand — what the 0.95 m solid cheek became. The cheek was cast as
        #   a `build_slope` parapet 1.5 m thick under a granite coping and it was the whole
        #   reason the north stair read as a different structure from the deck it belongs to.
        #   It is now the same member the spiral carries: a raked band whose top runs
        #   `cheek_h` (= the spiral's `railing.up_top`, 0.108 m) over the stair's MID line, so
        #   it clears the highest tread edge (+riser/2 = +0.096) by 12 mm and the glazed guard
        #   above it stands on ONE straight line instead of on 13 steps [computed].
        #   Slope angle atan2(2.496, 3.9) = 32.62°, cos 0.8422; thick 0.60 puts the underside
        #   0.505 m below the line, buried in the stair solid over both flights [computed].
        #   The band is centred ON the guard line (local y0 / y1 = world x 5.0 / 2.0 = the deck
        #   rail line), so 0.06 m of it oversails the stair face as a coping does — deck rail,
        #   north guard and stringer are one plane end to end.
        drop_f = no["n"] * no["riser"]
        half_c = no["cheek_t"] / 2.0
        for fi, (fx0, fz0) in enumerate(((no["x0"], no["z_top"]),
                                         (lx1, z_mid))):
            for i, ye in enumerate((no["y0"], no["y1"])):
                sc.build_slope(stage, f"{RG}/Cheek_{fi}_{i}", fx0,
                               fz0 - no["riser"]/2.0 + no["cheek_h"],
                               runA, drop_f, ye - half_c, ye + half_c,
                               0.60, M["fascia"], margin=0.004, collider=True)
        # upstand over the mid-landing — same 0.108 m over the same MID line, which on a level
        #   run is `z_mid − riser/2`, so it joins both flights with a 0 mm step [computed]
        for i, ye in enumerate((no["y0"], no["y1"])):
            BOX(f"{RG}/CheekMid_{i}",
                ((lx0+lx1)/2.0, ye,
                 z_mid - no["riser"]/2.0 + no["cheek_h"] - 0.30),
                (lx1-lx0, 2*half_c, 0.60), M["fascia"])
        # [v5.1 §4 / v6 C-3] base soiling band - lower 0.30 m of the stair solid's side face
        for i, ye in enumerate((no["y0"], no["y1"])):
            sgn = 1.0 if i == 0 else -1.0
            BOX(f"{RG}/StairGrime_{i}",
                (no["x0"] + (2*runA + no["land_len"])/2.0,
                 ye + sgn*0.012, PARAMS["walk"]["z_top"] + 0.15),
                (2*runA + no["land_len"], 0.024, 0.30), M["grime"])
        return RG

    def _north_ref(lx):
        """MID-step line of the north stair at local x — the line its guard is set out from.

        [GT-76] Both flights and the mid-landing are referenced to ONE function, and the
        landing branch is `z_mid − riser/2` rather than `z_mid`. That is what makes the three
        segments join with a 0 mm step: flight A ends at z_top − riser*(n+0.5) = 2.408 and
        flight B starts at z_mid − riser/2 = 2.408, the same number [computed]. Referencing
        the landing to its floor instead would have put a 96 mm break in the cap at both
        landing joints — the same class of break the spiral cap carried at every post."""
        no = PARAMS["north"]
        rA = no["n"] * no["tread"]
        zm = no["z_top"] - no["n"] * no["riser"]
        a1 = no["x0"] + rA
        if lx <= a1:
            return no["z_top"] - no["riser"] * ((lx - no["x0"]) / no["tread"]
                                                + 0.5)
        if lx <= a1 + no["land_len"]:
            return zm - no["riser"] / 2.0
        return zm - no["riser"] * ((lx - a1 - no["land_len"]) / no["tread"]
                                   + 0.5)

    def build_north_guard(M):
        """[GT-76] The north stair's glazed guard — the same product as the deck and spiral.

        The gallery verdict was that the two vertical accesses of one overpass do not read as
        one structure, and this is the member that was missing: the north stair had a solid
        concrete cheek and no guard at all, while the deck it lands on and the spiral at the
        other end are both steel shoe · laminated pane · bronze cap.
        Set-out: the guard line is local y0 / y1 = **world x 5.0 / 2.0**, i.e. the deck rail
        line itself, so the run continues off the deck without a dogleg. Section comes from
        `_guard_section(True)` on both flights and — because `_north_ref` puts the landing on
        the same mid line — from the same section on the mid-landing, so the cap is one
        unbroken line from the deck newel at y 13.0 to the ground newel at y 22.2.
        Bay 1.300 m = the outer spiral run's own chord to within 4 mm [computed]. Returns the
        pane count. Under `cue_railing` like every other guard run in the scene."""
        no, rb, rl = (PARAMS["north"], PARAMS["rail_bay"], PARAMS["railing"])
        RG = f"{ROOT}/NorthGroup"
        gs = _guard_section(True)
        rA = no["n"] * no["tread"]
        a1 = no["x0"] + rA
        b0 = a1 + no["land_len"]
        b1 = b0 + rA
        nb = max(1, int(no["bays"]))
        # (segment start, run, drop, bay count) — flight A · mid-landing · flight B
        segs = ((no["x0"], rA, no["n"] * no["riser"], nb),
                (a1, no["land_len"], 0.0, 1),
                (b0, rA, no["n"] * no["riser"], nb))
        half_t = PARAMS["deck"]["parapet_t"] / 2.0
        n_pane = 0
        for i, ye in enumerate((no["y0"], no["y1"])):
            for si, (sx, run, drop, bn) in enumerate(segs):
                cs = run / math.hypot(run, drop)      # perpendicular/vertical ratio
                z0 = _north_ref(sx)
                # continuous shoe + continuous cap over the whole segment; the 4 mm margin
                #   laps 2 mm into each neighbour so no two segment end faces are coincident
                sc.build_slope(stage, f"{RG}/NGShoe_{i}_{si}", sx,
                               z0 + gs["kick_top"], run, drop,
                               ye - half_t, ye + half_t,
                               (gs["kick_top"] - gs["kick_bot"]) * cs,
                               M["steel"], margin=0.004, collider=False)
                sc.build_slope(stage, f"{RG}/NGCap_{i}_{si}", sx,
                               z0 + gs["cap_top"], run, drop,
                               ye - half_t - rb["cap_over"],
                               ye + half_t + rb["cap_over"],
                               (gs["cap_top"] - gs["cap_bot"]) * cs,
                               M["rail"], margin=0.004, collider=False)
                for k in range(bn):
                    p0 = sx + run * k / float(bn) + rb["post_t"]/2.0 \
                        + rl["joint"]
                    p1 = sx + run * (k + 1) / float(bn) - rb["post_t"]/2.0 \
                        - rl["joint"]
                    sc.build_slope(stage, f"{RG}/NGGlass_{i}_{si}_{k}", p0,
                                   _north_ref(p0) + gs["glass_top"],
                                   p1 - p0, drop * (p1 - p0) / run,
                                   ye - rb["glass_t"]/2.0,
                                   ye + rb["glass_t"]/2.0,
                                   (gs["glass_top"] - gs["glass_bot"]) * cs,
                                   M["glass"], margin=0.0, collider=False)
                    n_pane += 1
                    if k == 0 and si == 0:
                        continue                     # the deck newel carries this joint
                    px = sx + run * k / float(bn)
                    zb = _north_ref(px) + gs["post_bot"]
                    zt = _north_ref(px) + gs["post_top"]
                    BOX(f"{RG}/NGPost_{i}_{si}_{k}", (px, ye, (zb + zt)/2.0),
                        (rb["post_t"], rb["post_t"], zt - zb), M["steel"])
            zg = _north_ref(b1)
            _newel(f"{RG}/NorthNewel_{i}", b1, ye, 0.0, zg + gs["up_bot"],
                   zg + gs["cap_bot"], zg + gs["cap_top"], M)
        return n_pane

    # -------------------------------------------------------------------
    # dressing
    # -------------------------------------------------------------------
    def build_dressing(M):
        d = PARAMS["dress"]
        lp = d["lamp"]
        gz = PARAMS["walk"]["z_top"]
        for i, (lx, ly) in enumerate(d["lamps"]):
            base = f"{ROOT}/Lamp_{i}"
            CYL(f"{base}/Pole", (lx, ly, gz + lp["pole_h"]/2.0), lp["pole_r"],
                lp["pole_h"], M["pole"], col=True)
            sgn = 1.0 if ly < 0 else -1.0
            CYL(f"{base}/Arm", (lx, ly + sgn*lp["arm_len"]/2.0,
                                gz + lp["pole_h"] - 0.12),
                lp["arm_r"], lp["arm_len"], M["pole"], rotX=90.0)
            BOX(f"{base}/Head", (lx, ly + sgn*lp["arm_len"],
                                 gz + lp["pole_h"] - 0.18),
                (lp["head"], lp["head"]*1.5, 0.14), M["lamp"])
        # every street tree stands on the verge - the ground there is the ground-cover top
        #   (0.10), not the sidewalk (−0.005), so they are planted at that height and the root collar is not buried.
        tz = PARAMS["verge"]["soil_top"]
        for i, (tx, ty) in enumerate(d["trees"]):
            sc.build_tree(stage, f"{ROOT}/Tree_{i}", tx, ty, tz, M["wood"],
                          M["leaf_a"], M["leaf_b"])
        for i, (bx, by, yaw) in enumerate(d["benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{i}", bx, by, gz, M["wood"],
                           yaw=yaw)
        for i, (bx, by) in enumerate(d["bollards"]):
            sc.build_bollard(stage, f"{ROOT}/Bollard_{i}", bx, by, gz,
                             mtl=M["pole"])
        bx, by, bh = d["bus_pole"]
        CYL(f"{ROOT}/BusPole", (bx, by, gz + bh/2.0), 0.055, bh, M["pole"],
            col=True)
        BOX(f"{ROOT}/BusSign", (bx, by, gz + bh - 0.30),
            (0.06, 0.55, 0.55), M["panel"])
        build_g6_boundary(M)
        build_treeband(M)
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd, M["brick"],
                              M["glass"], M["parapet"],
                              window=PARAMS["window_by"].get(
                                  key, PARAMS["window"]))

    def build_g6_boundary(M):
        """[W3 S06 · G6] the image's foreground boundary set — timber road guardrail,
        green mesh fence, and the landscaped bed at the tower foot.

        None of these is decoration in G6: the frame is *composed* out of them, and their
        absence is the reason the old near field was 11 m of empty block paving. They also
        carry no GT — every one of them stands outside the deck-run sight corridor and
        outside the r <= 4.2 near frame (asserted by `_corridor_hits`, which stays 0)."""
        g6 = PARAMS["g6"]
        gz = PARAMS["walk"]["z_top"]

        # --- brown timber road guardrail, yellow reflective bands -------------
        gd = g6["guard"]
        made = pk.build_tube_railing(
            stage, f"{ROOT}/RoadGuard", [(gd["x0"], gd["y"]), (gd["x1"], gd["y"])],
            lambda x, y: gz, M["guard_wood"], rails=gd["rails"],
            rail_h=gd["h"], tube_r=gd["tube_r"], post_r=gd["post_r"],
            post_pitch=gd["pitch"], bottom=0.30)
        # the yellow reflective band is a wrap on each post, which is what a Korean
        #   차선분리 guardrail actually carries — it is not painted on the rails.
        n_post = int(made["post"])
        for k in range(n_post):
            px = gd["x0"] + (gd["x1"] - gd["x0"]) * k / max(1, n_post - 1)
            BOX(f"{ROOT}/RoadGuardBand_{k}",
                (px, gd["y"], gz + gd["h"] - 0.16),
                (gd["band_w"], gd["band_w"], gd["band_h"]), M["guard_band"])
        print(f"[G6] road guardrail · posts {made['post']} · rails {made['rail']} · "
              f"clear_max {made['clear_max']:.3f} m")

        # --- green PVC-coated welded mesh fence -------------------------------
        mh = g6["mesh"]
        npm = max(2, int(round((mh["x1"] - mh["x0"]) / mh["post_pitch"])) + 1)
        for k in range(npm):
            px = mh["x0"] + (mh["x1"] - mh["x0"]) * k / (npm - 1)
            CYL(f"{ROOT}/MeshPost_{k}", (px, mh["y"], gz + mh["h"]/2.0),
                mh["post_r"], mh["h"], M["mesh"])
        for w in range(mh["n_wire"]):
            zw = gz + 0.10 + (mh["h"] - 0.20) * w / float(mh["n_wire"] - 1)
            CYL(f"{ROOT}/MeshWireH_{w}",
                ((mh["x0"]+mh["x1"])/2.0, mh["y"], zw), mh["wire_r"],
                mh["x1"] - mh["x0"], M["mesh"], rotY=90.0)

        # --- landscaped bed at the tower foot ---------------------------------
        #   야면석 (rough-stone) edge: individual blocks round an ellipse, NOT a smooth
        #   ring — the whole point of 야면석 is that the units are irregular. Deterministic
        #   jitter off a coordinate hash, so the bed is identical on every re-run.
        bd = g6["bed"]
        import random as _random
        pts_grass, pts_shrub = [], []
        for k in range(bd["n_edge"]):
            th = 2.0 * math.pi * k / bd["n_edge"]
            rnd = _random.Random(k * 7919 + 31)
            ex = bd["cx"] + bd["rx"] * math.cos(th)
            ey = bd["cy"] + bd["ry"] * math.sin(th)
            hh = bd["edge_h"] * rnd.uniform(0.78, 1.18)
            BOX(f"{ROOT}/BedEdge_{k}", (ex, ey, gz + hh/2.0 - 0.06),
                (rnd.uniform(0.26, 0.42), rnd.uniform(0.24, 0.38), hh),
                M["rubble"], col=True)
        # soil pan, proud of the edge (real beds settle proud, they are not excavated)
        BOX(f"{ROOT}/BedSoil", (bd["cx"], bd["cy"], gz + 0.14),
            (2*bd["rx"] - 0.30, 2*bd["ry"] - 0.30, 0.40), M["soil"])
        for k in range(14):
            rnd = _random.Random(k * 6607 + 101)
            th = 2.0 * math.pi * k / 14.0
            rr = rnd.uniform(0.30, 0.80)
            p = (bd["cx"] + bd["rx"] * rr * math.cos(th),
                 bd["cy"] + bd["ry"] * rr * math.sin(th), gz + 0.34)
            (pts_grass if k % 2 == 0 else pts_shrub).append(p)
        # [K4(b) S-2] one species per bed — `species=` names a SHRUB_SPECIES role and the
        #   draw happens ONCE per bed, so each bed is monospecific and deterministic.
        # [W3 S06 · finding S06-F2] G6's bed is **miscanthus + flowering shrub**, and the
        #   obvious role for the grasses is `riparian` -> `Shrub/Switchgrass.usd`. That file
        #   EXISTS on disk but is **absent from `scene_common.VEG_SHRUBS`**, which is the
        #   table `place_shrubs` filters every candidate through — so the role resolves to
        #   an empty list and falls back **silently** to `SHRUB_ORNAMENT` (Rhododendron),
        #   returning a healthy count for a bed that is not what was asked for. The first
        #   render of this scene put two Rhododendron beds side by side and reported
        #   "grasses 14". No sanctioned call can reach Switchgrass (a `pool=` argument is
        #   filtered through the same table), and kits are frozen this window, so the
        #   ornamental-grass read is **not achieved**; `border_narrow` is used instead so the
        #   two beds are at least two deliberate species rather than one species twice.
        n_g = sc.place_shrubs(stage, f"{ROOT}/BedGrass", pts_grass,
                              bd["grass_h"], seed=6061, tag="Gr",
                              species="border_narrow")
        n_s = sc.place_shrubs(stage, f"{ROOT}/BedShrub", pts_shrub,
                              bd["shrub_h"], seed=6062, tag="Sh",
                              species="ornament_bed")
        # sapling on a timber tripod support — G6 shows this explicitly
        sx, sy = bd["sapling"]
        sc.build_tree(stage, f"{ROOT}/BedSapling", sx, sy, gz + 0.30,
                      M["wood"], M["leaf_a"], M["leaf_b"], canopy_spread=0.62)
        for k in range(3):
            th = math.radians(90.0 + 120.0 * k)
            tx = sx + bd["tripod_r"] * math.cos(th)
            ty = sy + bd["tripod_r"] * math.sin(th)
            lean = math.degrees(math.atan2(bd["tripod_r"], bd["tripod_h"]))
            CYL(f"{ROOT}/BedTripod_{k}",
                ((sx + tx)/2.0, (sy + ty)/2.0, gz + 0.30 + bd["tripod_h"]/2.0),
                0.035, math.hypot(bd["tripod_r"], bd["tripod_h"]),
                M["wood"], rotY=lean * math.cos(th), rotX=-lean * math.sin(th))
        print(f"[G6] tower-foot bed · edge {bd['n_edge']} · grasses {n_g} · "
              f"shrubs {n_s} · sapling 1 on a 3-leg timber tripod")

    def build_treeband(M):
        """[v6 verdict C-2/C-4] distant tree silhouette band — a ridge-like row of blocks
        with height jitter instead of a parade of individual (lollipop) trees. Its
        purpose is to erase the straight horizon where the grass slab meets the sky,
        and it becomes the far background of the grid sight axis (deck run −Y).
        Deterministic jitter (coordinate hash) — identical on re-run."""
        tb = PARAMS["treeband"]
        import random as _random
        for r, (ya, yb, hh) in enumerate(tb["rows"]):
            n = max(2, int(round((tb["x1"] - tb["x0"]) / tb["seg"])))
            for k in range(n):
                xa = tb["x0"] + k * (tb["x1"] - tb["x0"]) / n
                xb = tb["x0"] + (k + 1) * (tb["x1"] - tb["x0"]) / n
                rnd = _random.Random((r * 7717) ^ (k * 3413))
                h = hh + rnd.uniform(-tb["jitter"], tb["jitter"])
                dy = rnd.uniform(-0.8, 0.8)
                BOX(f"{ROOT}/TreeBand_{r}_{k}",
                    ((xa+xb)/2.0, (ya+yb)/2.0 + dy,
                     PARAMS["ground"]["z_top"] + h/2.0),
                    (xb - xa + 0.6, (yb - ya) * rnd.uniform(0.8, 1.25), h),
                    M["leaf_a"] if (k + r) % 2 == 0 else M["leaf_b"])
                # one blob above the canopy - the minimum element that breaks the box ridge
                sc.add_sphere(stage, f"{ROOT}/TreeBlob_{r}_{k}",
                              ((xa+xb)/2.0 + rnd.uniform(-1.5, 1.5),
                               (ya+yb)/2.0 + dy,
                               PARAMS["ground"]["z_top"] + h),
                              (rnd.uniform(1.8, 3.0), rnd.uniform(1.4, 2.2),
                               rnd.uniform(1.0, 1.8)),
                              M["leaf_b"] if (k + r) % 2 == 0 else M["leaf_a"])

    # -------------------------------------------------------------------
    # cues - glazed guard (GT-68) · tactile paving · nosing
    # -------------------------------------------------------------------
    def _guard_band(prefix, tag, r_in, r_out, a0, a1, z_of, zb, zt, mtl):
        """ONE continuous member of a curved run — upstand, shoe or cap.

        [GT-76] This is the row's central change. The three continuous parts of the guard
        used to be re-emitted per bay, which put a plumb cut face and a dead slot at every
        post and let each bay's rake start where the previous one had already dropped: a cap
        that zig-zagged 23.077° 13 times per run instead of turning smoothly. They are now
        one bent member per run, faceted by `railing.cap_seg_deg` (2.0° -> sagitta 0.49 mm at
        r 3.24 against the 65.5 mm the old chord chain carried [computed]). The end faces of
        the member are exactly the two run terminals, and each of those is closed by a newel
        head, so the run has no raw cut face anywhere.
        `z_of(a) + zb/zt` is evaluated at both terminals only — legitimate because both
        `_spiral_z_at` and a level line are affine in azimuth, so the raked parallelogram
        `_raked_sector_mesh` interpolates IS the exact member, not an approximation."""
        rl = PARAMS["railing"]
        seg = max(8, int(round(abs(a1 - a0) / rl["cap_seg_deg"])))
        return _raked_sector_mesh(stage, f"{prefix}/{tag}", CX, CY, r_in, r_out,
                                  a0, a1, z_of(a0) + zb, z_of(a0) + zt,
                                  z_of(a1) + zb, z_of(a1) + zt, mtl,
                                  arc_seg=seg)

    def _guard_run(prefix, rad, bays, z_of, off, M, upstand=None):
        """One glazed guard run on a curve: [upstand ·] shoe · panes · bronze cap.

        [GT-68] `z_of(a)` returns the walking-line z at azimuth a and the section comes from
        `_guard_section`, so the raked spiral runs and the level landing lobes are the same
        code. Radial widths are the deck's: shoe `deck.parapet_t`, pane `rail_bay.glass_t`,
        cap the shoe + `rail_bay.cap_over` each side.
        [GT-76] Only the PANE is still per bay — that is what a laminated balustrade is, and
        its ends are the only place a joint belongs. The angular deduction is read as arc at
        the run's radius so the 0.020 m joint gap is constant on runs whose bay chord differs
        2.08x; it is taken off `rail_bay.post_t/2` now that the mullion is the deck's square
        section rather than a Ø60 tube. `upstand=(r_in, r_out)` casts the raked stringer the
        run stands on — level runs pass None because a level floor has no stepped edge to
        trim. Returns the pane count."""
        rl, rb, dk = PARAMS["railing"], PARAMS["rail_bay"], PARAMS["deck"]
        a0, a1 = bays[0], bays[-1]
        half_t = dk["parapet_t"] / 2.0
        if upstand is not None:
            _guard_band(prefix, "Upstand", upstand[0], upstand[1], a0, a1,
                        z_of, off["up_bot"], off["up_top"], M["fascia"])
        _guard_band(prefix, "Shoe", rad - half_t, rad + half_t, a0, a1,
                    z_of, off["kick_bot"], off["kick_top"], M["steel"])
        _guard_band(prefix, "Cap", rad - half_t - rb["cap_over"],
                    rad + half_t + rb["cap_over"], a0, a1,
                    z_of, off["cap_bot"], off["cap_top"], M["rail"])
        d_gl = math.degrees((rb["post_t"] / 2.0 + rl["joint"]) / rad)
        hw = rb["glass_t"] / 2.0
        for k in range(len(bays) - 1):
            b0, b1 = bays[k] + d_gl, bays[k + 1] - d_gl
            _raked_sector_mesh(
                stage, f"{prefix}/Glass_{k}", CX, CY, rad - hw, rad + hw,
                b0, b1, z_of(b0) + off["glass_bot"], z_of(b0) + off["glass_top"],
                z_of(b1) + off["glass_bot"], z_of(b1) + off["glass_top"],
                M["glass"], arc_seg=rl["arc_seg"])
        return len(bays) - 1

    def _guard_posts(prefix, rad, bays, z_of, off, M, skip=()):
        """Plumb mullions at the bay joints (= riser lines on the spiral runs).

        [GT-76] The mullion is the deck's own `rail_bay.post_t` square, radially oriented on
        a curve, so the whole structure carries ONE mullion section; it used to be a Ø60 tube
        on the curves against a 100 mm square on the deck. It stops 20 mm INSIDE the cap
        (`post_top`) rather than flush with it: the cap is continuous now, so a post reaching
        the cap top would only put its own square face in the cap's top plane. `skip` drops a
        post that a newel already carries."""
        rb = PARAMS["rail_bay"]
        n = 0
        for k, a in enumerate(bays):
            if k in skip:
                continue
            zb = z_of(a) + off["post_bot"]
            zt = z_of(a) + off["post_top"]
            sc.add_box(stage, f"{prefix}_{k}",
                       (CX + rad * math.cos(math.radians(a)),
                        CY + rad * math.sin(math.radians(a)), (zb + zt) / 2.0),
                       (rb["post_t"], rb["post_t"], zt - zb), M["steel"],
                       rotZ=a)
            n += 1
        return n

    def _newel(path, x, y, yaw, z_bot, cap_lo, cap_hi, M):
        """Terminal post + bronze newel head — how every run in this scene now ENDS.

        [GT-76] Before this row each run simply stopped: the cap's plumb cut face stood in
        the open at the spiral foot, at both landing-lobe ends and at both deck ends, and the
        deck's tube handrail ended as a raw cut circle in mid-air. A newel is the member that
        makes an end an end. The post is `railing.newel_t` (0.13 m) square — wider than the
        0.10 m intermediate mullion, as a newel is — and it is sized to cover the widest
        thing that dies into it: the outer upstand's radial band is 0.112 m, so 0.13 m closes
        it with 9 mm each side [computed]. The head is the cap section squared off and run
        0.080 m past the newel centreline, i.e. past the cap's end face, so the cut face is
        inside solid bronze."""
        rl, rb, dk = PARAMS["railing"], PARAMS["rail_bay"], PARAMS["deck"]
        t = rl["newel_t"]
        sc.add_box(stage, f"{path}/Post", (x, y, (z_bot + cap_lo + 0.02) / 2.0),
                   (t, t, cap_lo + 0.02 - z_bot), M["steel"], rotZ=yaw)
        sc.add_box(stage, f"{path}/Head", (x, y, (cap_lo + cap_hi) / 2.0),
                   (dk["parapet_t"] + 2.0 * rb["cap_over"] + 0.02, t + 0.03,
                    cap_hi - cap_lo), M["rail"], rotZ=yaw)

    def build_deck_rail(M):
        """[v6 verdict (1)] deck sound railing — post segmentation + alternating sound-panel
        and open bays. The old build (one unsegmented panel per side + a top pipe) read
        as a closed box girder, and now that the grid has moved onto the deck run axis it
        would make **both corridor walls pure black shadow faces**, killing both the
        judgement and the training data (the same defect as scene11).
        Even bays = sound panel (+coping cap), odd bays = open (kick band + 5 vertical bars).
        GT-irrelevant (railing prims) — under the cue_railing toggle.

        [GT-76] Three finishes land here. (1) The shoe and the cap are now ONE box per side
        over the whole run instead of 13 each: the deck's cap used to break at every post
        exactly as the spiral's did, which is why the two ends of one bridge could not read
        as one member. (2) The run is cut at the landing newel (`_deck_rail_y`) so the
        arriving landing guard shares a post instead of crossing the deck run in mid-bay.
        (3) The round tube that floated 0.240 m over the cap on 1.28 m posts, ended in a raw
        cut circle at both deck ends and had no counterpart on any stair run, is gone; the
        cap at 1.100 m is the guard head on every run of the structure.

        [GT-92] The WEST run no longer starts at the slab corner y0 but at the landing
        newel yj = −10.128. Its apron-return stretch (kick 5.000…5.120 · pane
        5.085…6.040 · cap 6.015…6.100, all on the x 2.000 line over y −13.000…−10.128)
        stood over a line with FLOOR at z 5.000 on BOTH sides — deck slab east, landing
        west lobe west — so it guarded no edge; what it did was seal the only floor
        crossing between the deck and the lobe, and the lobe is the only way onto the
        spiral head (step 0, az 180…191.5°, is entered over the az-180 ray at
        x 0.20…2.00, wholly west of the line). The 08-07 gallery read exactly that:
        "the stair connection at the overpass is blocked". The stretch is now a FORMAL
        OPENING, 2.742 m clear between two bronze-headed posts — DeckNewel_S0
        (2.0, −10.128), shared with the arriving landing-lobe guard, and the spiral's
        own a0 inner newel (1.94, −13.0) — so every guard member still dies into a
        newel (no raw cut) and the guard line runs unbroken around the drop rim:
        deck cap → S newel → landing lobe cap (r 3.24, az 117.578…180) → a0 newels →
        spiral caps. DeckNewel_E0, which overlapped that inner newel by construction
        (centres 60 mm apart), is retired with the bay. The EAST apron bay is kept
        closed on purpose: the east lobe's az-0 radial edge stands unguarded over the
        spiral (drop 2.9…5.0 m), so opening it would expose a drop this row has no
        authority to declare."""
        dk = PARAMS["deck"]
        rb = PARAMS["rail_bay"]
        y0, y1 = dk["y0"], dk["y1"]
        gl = _guard_section(False)
        yj, ybays = _deck_rail_y()
        nb = len(ybays) - 1
        zt = dk["z_top"]
        for i, xe in enumerate((dk["x0"], dk["x1"])):
            west = (i == 0)
            # [GT-92] west run: apron stretch = opening; east run: full span
            y_lo = yj if west else y0
            # continuous shoe + continuous cap, end to end
            BOX(f"{ROOT}/DeckKick_{i}",
                (xe, (y_lo + y1)/2.0, zt + (gl["kick_bot"] + gl["kick_top"])/2.0),
                (dk["parapet_t"], y1 - y_lo, gl["kick_top"] - gl["kick_bot"]),
                M["steel"])
            BOX(f"{ROOT}/DeckPanelCap_{i}",
                (xe, (y_lo + y1)/2.0, zt + (gl["cap_bot"] + gl["cap_top"])/2.0),
                (dk["parapet_t"] + 2*rb["cap_over"], y1 - y_lo,
                 gl["cap_top"] - gl["cap_bot"]), M["rail"])
            # intermediate mullions — k 0/1/nb are newels (well rim · landing · north head)
            for k in range(2, nb):
                BOX(f"{ROOT}/DeckRailPost_{i}_{k}",
                    (xe, ybays[k],
                     zt + (gl["post_bot"] + gl["post_top"])/2.0),
                    (rb["post_t"], rb["post_t"],
                     gl["post_top"] - gl["post_bot"]), M["steel"])
            for k in range(nb):
                if west and k == 0:
                    continue      # [GT-92] the west apron bay is the opening — no pane
                ya = ybays[k] + rb["post_t"]/2.0 + rb["joint"]
                yb = ybays[k+1] - rb["post_t"]/2.0 - rb["joint"]
                yc, Ly = (ya + yb)/2.0, yb - ya
                # [W3 S06 · G6] **glass panels on the approach span.** G6 guards the deck
                #   with laminated glass under a bronze tube rail; the v6 build alternated
                #   opaque sound panels with open bar bays. Glass satisfies v6's own reason
                #   for the open bays — *"both corridor walls pure black shadow faces"* —
                #   strictly better than an open bay does, because it is see-through over
                #   the FULL bay instead of between bars. So every bay is now glazed: shoe
                #   kick band, a laminated panel with a real joint at each post, and the
                #   bronze cap rail above. `build_glass_balustrade` is the right template
                #   but is X-axis-only (`rotY=90` cap, same restriction as
                #   `build_tube_railing`, finding S06-F1) and this run is Y-aligned, so its
                #   three-part form — shoe / jointed panel / capping rail — is reproduced.
                BOX(f"{ROOT}/DeckGlass_{i}_{k}",
                    (xe, yc,
                     zt + (gl["glass_bot"] + gl["glass_top"])/2.0),
                    (rb["glass_t"], Ly - 2*rb["joint"],
                     gl["glass_top"] - gl["glass_bot"]),
                    M["glass"])
            # newels — the points where this run ENDS or hands over. `E` (the slab corner
            #   on the well rim) survives on the EAST side only: [GT-92] the west run now
            #   ends at the landing newel `S`, and the opening's south jamb is the
            #   spiral's own a0 inner newel 60 mm away — with the bay gone, keeping E0
            #   would leave two overlapping newels at one corner.
            tags = (("S", yj), ("N", y1)) if west else \
                   (("E", y0), ("S", yj), ("N", y1))
            for tag, ye in tags:
                _newel(f"{ROOT}/DeckNewel_{tag}{i}", xe, ye, 0.0,
                       zt + gl["post_bot"], zt + gl["cap_bot"],
                       zt + gl["cap_top"], M)
        return 2 * nb - 1        # [GT-92] west run carries nb−1 panes (opening), east nb

    def build_cues(M):
        rl = PARAMS["railing"]
        if cfg["cue_railing"]:
            # [GT-68] ONE guard family for the whole route — steel shoe · laminated pane ·
            #   bronze cap. Spiral runs are raked off `_spiral_z_at`, the landing lobes are
            #   level off `landing.top_z`, the deck run is `build_deck_rail`; all three take
            #   their section from `_guard_section`, i.e. from `deck`/`rail_bay`.
            #   Both spiral runs are uninterrupted over the full sweep (the pre-08-05 outer
            #   run resumed only after 270°, leaving a quadrant of posts with no infill).
            la, rb, fa = (PARAMS["landing"], PARAMS["rail_bay"],
                          PARAMS["fascia"])
            bays = _guard_bays()
            gs, gl = _guard_section(True), _guard_section(False)
            cap_land = la["top_z"] + gl["cap_top"]
            a_end = sp["a0"] + sp["sweep"]
            n_bay = 0
            # [GT-76] `upstand` is per run because the stringer trims a DIFFERENT rim on each
            #   side: outboard it is the fascia rim r_out 3.30, inboard the tread rim r_in
            #   1.50 (= the well edge, which is why the inner band recedes 2 mm FROM it and
            #   never encroaches on the 5.005 m drop). The walking-side face is `up_side`
            #   0.050 off the rail line on both, so the clear stair width between the two
            #   upstands is 1.580 m against the 1.20 m statutory minimum [computed].
            runs = (("Outer", rl["outer_r"],
                     (rl["outer_r"] - rl["up_side"], fa["r_out"] + rl["up_rim"])),
                    ("Inner", rl["inner_r"],
                     (sp["r_in"] + rl["up_rim"], rl["inner_r"] + rl["up_side"])))
            for tag, rad, ups in runs:
                n_bay += _guard_run(f"{ROOT}/Rail{tag}", rad, bays,
                                    _spiral_z_at, gs, M, upstand=ups)
                # both terminals are newels, so the run's own posts skip them
                _guard_posts(f"{ROOT}/RailPost{tag}", rad, bays, _spiral_z_at,
                             gs, M, skip={0, len(bays) - 1})
                for k, a in ((0, sp["a0"]), (len(bays) - 1, a_end)):
                    zw = _spiral_z_at(a)
                    _newel(f"{ROOT}/Newel{tag}_{k}",
                           CX + rad * math.cos(math.radians(a)),
                           CY + rad * math.sin(math.radians(a)), a,
                           # the a0 newel also receives the landing lobe, so it is founded on
                           # the lower of the two floors it serves
                           min(zw + gs["up_bot"], la["top_z"] + gl["post_bot"])
                           if k == 0 else zw + gs["up_bot"],
                           zw + gs["cap_bot"], zw + gs["cap_top"], M)
            # landing lobes = the run that carries the guard from the deck onto the spiral.
            #   Ended on the deck edge LINE (`_landing_guard_arcs`) rather than on the slab
            #   clip azimuth, so the terminal post stands on the deck rail line and the two
            #   guards share one newel instead of crossing 27 mm apart.
            for i, (pa0, pa1) in enumerate(_landing_guard_arcs()):
                nb = max(1, int(rl["landing_bays"]))
                lb = [pa0 + (pa1 - pa0) * k / float(nb) for k in range(nb + 1)]
                n_bay += _guard_run(f"{ROOT}/LandingParapet_{i}", rl["outer_r"],
                                    lb, lambda a: la["top_z"], gl, M)
                # the lobe that ends on the spiral a0 ray hands its last post to that newel,
                #   the one that ends on the deck edge line hands it to `DeckNewel_S*`
                _guard_posts(f"{ROOT}/LandingParapet_{i}/Post", rl["outer_r"],
                             lb, lambda a: la["top_z"], gl, M, skip={0, nb})
                if abs(lb[0] - la["a0"]) < 1e-6:
                    # the free end of the east lobe (azimuth 0) — the only run terminal that
                    #   meets no other run, so it needs its own newel to stop being a cut face
                    _newel(f"{ROOT}/LandingNewel_{i}",
                           CX + rl["outer_r"] * math.cos(math.radians(lb[0])),
                           CY + rl["outer_r"] * math.sin(math.radians(lb[0])),
                           lb[0], la["top_z"] + gl["post_bot"],
                           la["top_z"] + gl["cap_bot"],
                           la["top_z"] + gl["cap_top"], M)
            # deck run - [v6 verdict (1)] post segmentation, glazed bays (W3 S06 · G6)
            n_bay += build_deck_rail(M)
            n_bay += build_north_guard(M)
            yj, ybays = _deck_rail_y()
            cap_sp = _spiral_z_at(sp["a0"]) + gs["cap_top"]
            print(f"[GT-76] guard unified · upstand+shoe+pane+bronze cap · spiral "
                  f"{len(bays)-1} bays x 2 runs + landing "
                  f"{int(rl['landing_bays'])} x 2 + deck {len(ybays)-2}(W, 개구 "
                  f"[GT-92])+{len(ybays)-1}(E) + "
                  f"north {int(PARAMS['north']['bays'])*2+1} x 2 = {n_bay} panes · "
                  f"cap line deck {PARAMS['deck']['z_top']+gl['cap_top']:.3f} = "
                  f"landing {cap_land:.3f} = spiral {cap_sp:.3f} "
                  f"(Δ{abs(cap_sp-cap_land)*1000:.0f} mm) · 캡 연속 1本/run · "
                  f"newel {rl['newel_t']:.2f} sq")
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            lx0, lx1, ly0, ly1 = tc["low"]
            sc.build_tactile(stage, f"{ROOT}/TactileLow", lx0, lx1, ly0, ly1,
                             M["tactile"], z=tc["low_z"], proud=tc["proud"])
            hx0, hx1, hy0, hy1 = tc["high"]
            sc.build_tactile(stage, f"{ROOT}/TactileHigh", hx0, hx1, hy0, hy1,
                             M["tactile"], z=tc["high_z"], proud=tc["proud"])
        # [v5.2 user] arbitrary warning sign removed - cue_sign placement deleted.
        if cfg["cue_nosing"]:
            sd = _step_deg()
            for i in range(sp["n"]):
                aa = sp["a0"] + i * sd
                top = _spiral_top_z(i)
                sc.build_arc_steps(stage, f"{ROOT}/Nosing_{i}", CX, CY,
                                   sp["r_out"] - 0.07, sp["r_out"], aa,
                                   aa + sd, 1, top + 0.004, top - 0.02,
                                   M["nosing"], collider=False)

    def build_flat_control(M):
        """hazard_stairs=False — flat sidewalk control with the whole overpass structure removed."""
        wk = PARAMS["walk"]
        BOX(f"{ROOT}/FlatFill", (CX, CY, wk["z_top"] - 0.25),
            (2*sp["r_out"] + 1.0, 2*sp["r_out"] + 1.0, 0.5), M["paving"])

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_site(M)
    if cfg["cue_material_break"]:
        build_lanes(M)
    if cfg["hazard_stairs"]:
        build_spiral(M)
        build_deck(M)
        build_ground_kit(M)    # [W2-D] deck ground elements (deck must exist)
        build_north(M)
        build_cues(M)          # no geometry means no railing (prevents floating)
    else:
        build_flat_control(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    VIEWS = build_views()
    _v0 = VIEWS["overview"]
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

    if capture_mode:
        sc.capture_pipeline(simulation_app, VIEWS,
                            os.path.join(LOOKCHECK_DIR, "auto"),
                            set_render_mode, look_from)
        simulation_app.close()
        return

    input_iface = carb.input.acquire_input_interface()
    appwindow = omni.appwindow.get_default_app_window()
    K = carb.input.KeyboardInput
    rot_step = float(PARAMS["light"]["dome_rotation_step"])
    dome_user_rot = [0.0]

    def capture(path):
        vp = get_active_viewport()
        capture_viewport_to_file(vp, file_path=path)

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene06_{ts}.png")
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
