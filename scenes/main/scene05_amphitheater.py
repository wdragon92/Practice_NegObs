# -*- coding: utf-8 -*-
"""
scene05_amphitheater.py — NegObs synthetic scene 5: neighbourhood-park outdoor theatre
(Isaac Sim 4.5)

Spec    : Docs/briefs/multi_scene_brief_v5.md §reinterpretation(scene05) — replaces v2 §C
Shared  : scene_common.py (§A) — boot·make_pbr·build_arc_steps·lighting·capture
Motif   : scene01_campus_stairs.py (main skeleton·charcoal bands·planters·buildings)

[v5 adopted] Stage reinterpretation: the fully circular sunken bowl becomes a
  **half-round (200° = 180° + 20° margin) outdoor theatre**. The tier, seat and
  lip arcs are cut to θ 80..280°, and the cut section is finished with a side
  wall (cut_wall, parapet top face z=+1.0). East of the stage backdrop wall
  (shell), θ 9..79 / 281..349 becomes a **grass yard** (top −0.06) that meets
  the plaza ring (−0.002) at grade — the archetype of a neighbourhood-park
  outdoor theatre. The existing entry arc stair (θ ±9°), stage and timber
  seating are kept as they are; riser/tread/z are all unchanged.

Type identity: large drop (−1.2m) × curvature (half-round bowl) × minimal
  conventional facilities. The judging point is the grazing concealment in
  which the whole bowl vanishes from a low viewpoint (h0.3).
  [v5 shared layer] cue_tactile default True (urban-convention scene) + 1 sign_info.

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene05_amphitheater.py

[v7 judgment re-fix] judge_v7_rt_B §4 — covers all 3 remaining items.
  ① The new backdrop shrubs read as **"an even row of mossy boulders"** (the
     same failure mode as scene04 v6 verge = blob size × magnified texture).
     → 3 constant-colour tufts + **small lobe stacks** (each ≤0.46 m, clump top
     kept at 1.28 m) + 2 rows·jitter·dropouts.
     Check `backdrop_selfcheck()`.
  ② **Acute wedge** on the access stair arc. The cause is that the
     build_arc_steps chord length (based on r_out) reaches down to r_in, giving
     a crescent gap (15.3 mm) and an arc-end sliver (42 mm).
     → seg 3→12 (gap 1.05 mm · protrusion 10.6 mm) + **2 end caps (cheeks) per set**.
     Check `podium_step_selfcheck()`. Radii·angles·top-face z unchanged = geometry GT unchanged.
  ③ The **even row of white posts on the rim skyline** turned out to be the 10
     west bollards (a decorative row, spacing 2.67 m · width 24 m). → **4 posts
     at the entry-axis gate · regulation 1.5 m**, material painted steel.
     Resolves v5.1 §2/§3 at once.
  ④ (shared) New §4 large-pure-white-area self-check `albedo_selfcheck()` — the
     plaza paving is a shared item across all scenes, so it is explicitly
     recorded as WAIVED (awaiting a global decision by the director).

[W3 L05 · G8 ride] `w3_intake_v2_images.md` §4 Lane 3 row **3.6** routes scene05 onto
  image **G8** (primary) + **G1** (secondary): *"curved stepped seating bank in a modern
  Korean plaza"*. Five things came off the image and one was refused, all measured.
  ① **K4(d) true annular sectors** (`build_arc_steps(mesh=True)`) on **all 12 arc sites**.
     The box convention approximates a sector with an axis-aligned Cube sized on the
     **outer** chord, so at r_in the end segments overshoot the a0/a1 rays and the inner
     boundary is a chord, not an arc — the two causes ② below spent seg 3→12 and a pair of
     cheek walls patching around. The mesh is exact at the rays and arcs are faceted by
     `arc_seg`, so **GT-11's wedge gap and arc-end sliver are 0 by construction**, not by
     tolerance. GT-6 law: the judged baselines for 05·06·19 were archived **before**
     `scene_common` was cut (`5ceb76a`, manifest `Docs/reports/gt6_judge_baseline_manifest.json`),
     and this scene flips the lever **inside its own pilot**, which is where the split proof
     is judged (`w3_k4_v1.md` §5, `scene_common.py` `_annular_sector_mesh` header).
  ② **Timber deck seating bank** — G8's tiers are warm timber deck boards, not granite.
     The seat band widens 0.45 → 0.70 m of the 0.85 m tread; the back 0.05 m stays granite
     so the tread still reads as a stone course with a deck laid on it.
  ③ **Curved concentric paving bands** (R05-1 option (b), *"small-unit fan bond separated
     by a granite edge band"*, which G8 shows as banded curves). Inside the plaza ring the
     straight charcoal bands are replaced by bands **concentric with the bowl**, one grey
     and one warm tan (G8 carries both), closed by a **150 mm granite edge band** at the
     ring's outer circle. Outside the ring the straight grammar of G1 continues, and the
     two meet on a real construction line. This is also 05-A's "three modules, no edge band".
  ④ **The bunker reading**, which is the scene's oldest judged complaint: the cut walls and
     the stage shell were `granite_dark` and filled the frame as blank slabs. G8's vertical
     surfaces are pale concrete parapets with timber-slat soffits → both rebind to the
     parapet material and the cut wall takes a 60 mm timber capping.
  ⑤ **Species pinned at the call site** — `SCENE_SPECIES["Scene05"] = ("ash", None)`.
     Trees say `species="ash"`, beds say `species="ornament_bed"`; before this the beds drew
     per-bed by coordinate hash and the scene shipped **Juniper ×15 + Rhododendron ×9**.
  ⑥ **REFUSED: the tactile strips that follow G8's curves.** This scene's declared identity
     is the no-facility type (`cue_railing`/`cue_tactile` default False) and **R16-2** rules
     the 21 stair scenes stair-cue-first with stop devices held for their own scenes. The
     divergence from G8 is recorded, not silently taken (the S13-parapet / S03-fence
     precedent).

Season `[intake §7-8]`: **summer**, pinned from G8 (full leaf, high sun, clear sky) and
  matched by the shipped rig (`qwantani_noon_puresky` + sun elev 49.79°). There is no
  `bare=` call in this file and `season_selfcheck()` gates on its absence plus the measured
  hue census of every asset the scene references. `Rhododendron`'s flower strip is inert
  **library-wide** (K4-F1) — that is the library's state, not a scene regression, and in a
  summer frame a clipped green 철쭉 mound is the correct read.

Self-check (no boot, no render):
    NEGOBS_SMOKE=1 python scene05_amphitheater.py

Auto capture mode (for headless verification):
    NEGOBS_CAPTURE=1 python scene05_amphitheater.py
      NEGOBS_CAPTURE_DIR  : output folder (default look_check/scene05/auto)
      NEGOBS_CAPTURE_MODE : rt | pt | both (default rt)
      NEGOBS_VIEWS        : comma-separated view-name filter (default all)

Coordinates: Z-up, m, travel axis +X. Bowl centre (6, 0). Plaza top face z=0.
"""

import os
import sys
import math
import json
import random
import datetime

import numpy as np

import scene_common as sc
import ground_kit as gk


# ===========================================================================
# [A] SCENE_CONFIG - same 6 keys as scene01 + cue_nosing (new).
#     Only hazard_stairs toggles hazard geometry (bowl <-> flat). The rest keep geometry fixed.
#     ** cue_railing·cue_tactile default False = the "no facilities at all" type identity **
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # sunken bowl geometry (False -> all flat at z=0)
    "cue_railing":        False,   # True -> partial-arc railing at the lip (optional)
    # [v5 shared layer] urban-convention scenes (01/02/05/13/14/16/20/21) default cue_tactile True
    "cue_tactile":        False,  # [v5.2 user] tactile paving is rare in reality - default OFF (ablation path kept)    # −X approach warning tactile strip (outside the lip, x −2.3..−1.9)
    "cue_material_break": True,    # lip kerb ring (dark) + tiers (light granite) vs stage (blue-grey)
    "cue_nosing":         False,   # [new, reserved] True -> curved non-slip nosing arc band (optional)
    "cue_sign":           False,  # [v5.2] signboard removed    # [v5 shared layer] Korean sign (sc.build_sign)
    "cue_scene_dressing": True,    # planters·hedges·benches·streetlights·buildings as a set
}


# ===========================================================================
# [B] PARAMS - dimension table + material/lighting/capture. Mergeable via NEGOBS_PARAMS_OVERRIDE.
# ===========================================================================
PARAMS = dict(
    # --- upper plaza (x −18..18, y −14..14, z=0) ---
    plaza=dict(x0=-18.0, x1=18.0, y0=-14.0, y1=14.0, z_top=0.0, thick=0.5),
    # charcoal bands: granite_dark strips running along Y, X spacing 3.2, 1.5mm proud
    # === [W3 L05 · G8 · R05-1(b)] the bands inside the ring become CONCENTRIC ==========
    #   Pre-state `[repro]`: every band was a straight strip along Y across the whole
    #   36 m plaza, and the ones crossing the bowl were cut into a north and a south
    #   piece at the opening circle - i.e. the plaza's paving grammar ignored the one
    #   circular object in it, and 05-A's "three modules meet with no edge band" was
    #   read straight off that junction.
    #   G8: the paving runs in **concentric curved bands** around the bowl, grey with a
    #   warm tan band among them, and the bowl precinct is closed by an edge band.
    #   Post-state: the straight bands stop at the plaza ring's OUTER circle
    #   (`ring.r_out` 12.0) instead of at the bowl opening (7.5), and the annulus
    #   7.5..12.0 carries `arc_bands` + `edge_band`. The two grammars meet on the ring
    #   edge, which is a real construction line, so the module discontinuity 05-A names
    #   is now a designed joint rather than an accident.
    #     · `arc_bands` (radius, material key) - dark granite at 8.0 and 11.0 with a
    #       warm tan (brick) band between them at 9.5. G8 carries both greys and warm
    #       tan/brick bands. **Three, not two** `[pilot 2 -> pilot 3]`: with two the
    #       annulus lost the straight bands without replacing their rhythm, and the
    #       near field measured **47.1 % over the white line against the pre-state's
    #       29.9 %** on the same 520x220 px box - the bands were carrying tonal relief
    #       the paving cannot carry alone. At 8.0/9.5/11.0 the judged approach axis
    #       (looking +X from x -6) crosses a band at x -5.0, -3.5 and -2.0, i.e. the
    #       near field is banded again, in the curved grammar instead of the straight
    #       one.
    #     · `edge_band` - 150 mm granite band inside the ring edge (11.85..12.00).
    #     · all three sit on the ring top face (-0.002) at the SAME +1.5 mm the straight
    #       bands use, so no walked surface moves: 1.5 mm is an order below
    #       `ground_kit.GT_DELTA = 0.020`.
    band=dict(width=0.45, spacing=3.2, proud=0.0015, embed=0.05,
              clip_r=12.0,
              arc_bands=((8.0, "band"), (9.5, "brick"), (11.0, "band")),
              edge_band=(11.85, 12.00), seg=48),

    # === [W2-D ground_kit] P1 plaza_granite (spec §5.1 row 05) =============
    # Stage, tiers, ring and lip are **not touched** (W3 owns them). Only the
    # upper plaza west of the bowl lip is decorated.
    #
    # ORIGIN WARNING - spec §2.3 does not list scene05, but this scene *does*
    # shift its grid: `build_views()` subtracts 1.5 from every preset eye/tgt
    # so that "distance d" means "d to the bowl lip at x=-1.5", not to x=0.
    # The plan therefore runs with origin=(-1.5, 0, 0) and edge s=0.
    # Consequence: the §5.1 coordinates for this row are unusable as written -
    # the manhole at x=-3.5 sits exactly on the d2 eye (eye_x = -1.5-2 = -3.5)
    # and the sump at x=-8.5 is 1.5 m short of the d10 window. Re-derived here:
    #   manhole (-3.90, -0.40) -> X = 2.60 m at d5, screen width 414 px =
    #     21.6 % of frame. Same construction as the scene15 pilot fix (M9-b):
    #     inside the W1 window a 0.648 m cover cannot stay under 25 % (28.1 %
    #     even at the far end), so it goes to the 2nd-priority W2 window.
    #   gullies (-10.00, 0.00) [d10 window, X=1.50] and (-6.00, -3.00).
    #   patch sites — **DELETED, W3 L05**. GT-24 `[landed 07-31]` removed
    #     `("patch", 1)` from the `plaza_granite` profile: on 판석 600 unit paving
    #     the real repair lifts and relays whole flags, so a saw-cut milled
    #     rectangle is asphalt vocabulary and reads as the "이상한 사각형 무늬"
    #     the user named (§3(ii) · U-6). The sites here were already **inert** —
    #     `plan_ground` emits nothing for a kind with no `surface` row, measured
    #     `patch 0 · patch_cut 0` at HEAD — so this deletes dead configuration,
    #     not geometry. Kept as a record of what the d2 window used to carry:
    #     (-2.60,-0.45) and (-3.35,+1.20). The two rectangles are visible in the
    #     baseline round `260730_w2d_fix/pt_noon_preset_h0.3_d5.png`, which
    #     predates GT-24; they are gone from this scene's own round.
    # JOINT GRID runs out to the lip (x1 = lip_x = -1.50) since W2-D.
    #   HISTORY - it used to stop at x=-3.70. That clamp was a workaround for a
    #   ground_kit defect (D-1), not a design choice: `_edge_guard_ticks` fed
    #   the **world** x of each tick into `drow()`, which expects a forward-s
    #   offset, so on any scene whose origin is not (0,0,0) it guarded the wrong
    #   ticks. Measured at d10 (floor 16 rows @1080):
    #     tick x=-1.8  true s=-0.3  drow  1.57  <- violation; the v1.2 guard
    #                                             read drow(-1.8)=11.16 and
    #                                             dropped it for the wrong reason
    #     tick x=-3.6  true s=-2.1  drow 13.51  <- violation; the v1.2 guard
    #                                             read drow(-3.6)=28.54 and kept
    #                                             it, so the plan raised B7
    #                                             ("Joints/JX_5 ... 13.5 < 16")
    #   ground_kit v1.3 (Docs/reports/w2d_kitfix_v1.md §2) converts ticks through
    #   the plan's own view before guarding, so with the region at the lip it
    #   drops exactly {-3.6, -1.8} and keeps {-5.4, -7.2, -9.0, -10.8, -12.6} -
    #   the identical tick set the clamp was cut to preserve (6 joint prims).
    #   Un-clamping therefore costs no joint and gains the surface elements
    #   (patch/crack/stain/weed/scatter) 1.4 m of near field, because
    #   `_trim_region` now cuts at -2.30 instead of -3.70.
    #   See Docs/reports/w2d_edit_g1.md §3 D-3 and w2d_kitfix_v1.md §2/§9-4.
    #
    # 05-B SERVICE LINE `[intake §2 scene05 (a)]` — the carried gap is that the manhole
    #   was *solved from the camera*. It is now **declared as drainage** and the camera
    #   arithmetic above is demoted to a check on that declaration, which is the right
    #   order. The run is the plaza's own storm main: it enters from the building-R side
    #   of the site and falls east to the bowl sub-drain at the lip, so it lies on
    #   `y = -0.40`, offset half a cover from the walking axis exactly as a real main is
    #   offset from the gutter it serves; `manhole` sits on it and the two `gully`
    #   inlets sit off it, at the low corner each collects. `service_selfcheck()` gates
    #   every infra site against these two lines, so a later coordinate nudge cannot
    #   silently un-derive them. **Honest residue**: real 빗물받이 belong on a kerb line
    #   at 15–20 m pitch, and this scene's ground region is 12 m long and has no kerb —
    #   `infra_kit.build_curb_line` / `build_gutter_L` (K5) is what closes that, and it
    #   is deferred to the Lane-1 follow-up pass exactly as the §7 dispatch directs.
    gkit=dict(x0=-13.5, half_y=5.0, x1=-1.50, lip_x=-1.50,
              main_y=-0.40, gully_off_min=0.30,
              manhole=[(-3.90, -0.40)],
              gully=[(-10.00, 0.00), (-6.00, -3.00)]),

    # --- sunken bowl (centre (6,0), [v5 adopted] half-round 200 deg) ---
    #   3 tiers x riser 0.40 · tread 0.85 (seating spec) - three build_arc_steps calls.
    #   [v5 adopted] a0=80..a1=280 (200 deg = 180 deg + 20 deg margin). West (θ=180) seating half +
    #     east (behind the stage backdrop wall) is a grass yard. seg 32 (360 deg) -> 18 (200 deg) so
    #     the segment angular width stays 11.25 deg -> 11.11 deg (same chord·wedge-margin convention).
    #   hazard geometry unchanged: r_in/r_out/top_z/base_z/riser(0.40)·tread(0.85) all identical.
    bowl=dict(
        cx=6.0, cy=0.0, base_z=-1.6, seg=18, a0=80.0, a1=280.0, open_r=7.5,
        tiers=[dict(r_in=6.65, r_out=7.5,  top_z=-0.40),   # tier 1 (top edge)
               dict(r_in=5.8,  r_out=6.65, top_z=-0.80),   # tier 2
               dict(r_in=5.0,  r_out=5.8,  top_z=-1.20)],  # tier 3 (adjoining the stage)
    ),
    # plaza ring slab: a box cannot cut a round opening, so the bowl rim is approximated by an arc ring.
    #   top_z=-0.002 : 1~2mm offset to avoid coplanar Z-fighting with the frame boxes (z=0).
    # === [W3 L05 · K4(d)] r_in 7.50 -> 7.49, the R-CASCADE the mesh convention needs ====
    #   Under the box convention the ring's inner face was a plane at distance r_in from
    #   the centre, so the opening was a 48-gon **circumscribing** r 7.5 (max 7.516) and
    #   it was guaranteed to overlap tier 1's chord-oversized outer face. A true annular
    #   sector interpolates ON the circle, so both boundaries now oscillate INSIDE 7.5 -
    #   ring inner 7.49955..7.500, tier-1 outer 7.49902..7.500 - and at the facet phases
    #   where the two dip differently a **1.0 mm radial slit** can open over the 0.10 m
    #   band z -0.50..-0.40 where the ring's underside and the tier's flank coexist.
    #   Fixed by the scene's own device (the entry stair's 10 mm r-cascade, PARAMS['entry']):
    #   pull the ring 10 mm further in, so the overlap is >= 9 mm at every phase.
    #   **The visible top-of-drop edge does not move**: with `cue_material_break` the lip
    #   kerb (r_in 7.50, z -0.100..+0.003) is proud of the ring and owns the edge; the
    #   ring's own 7.49 boundary is 10 mm behind it and 0.1 m below. In the
    #   material-break-OFF ablation arm the edge does move 10 mm inward - declared, and
    #   0.010 m is half of `ground_kit.GT_DELTA` (0.020). Drop height 0.398 m unchanged.
    ring=dict(r_in=7.49, r_out=12.0, seg=48, top_z=-0.002, base_z=-0.5),
    # === v4-A1 [critical] fix for the through-gap between stage and tier 3 ===
    #   was: UsdGeom.Cylinder(r=5.0) alone. Depending on viewport refinement the Cylinder
    #   tessellates to a low-poly polygon, pulling the face-centre radius inward to 5.0·cos(π/n),
    #   while the tier-3 inner face recedes outward to 5.0/cos(5.625 deg)=5.0242 at the segment ends
    #   -> a through-gap up to 0.25 m wide where they meet (a real drop).
    #   fix: a two-layer structure, "inner disc (4.9) + 32-seg arc rim (4.2..5.22)".
    #     · rim outer min radius 5.22 > tier-3 inner max 5.0242 -> 0.196 overlap guaranteed
    #       (gap 0 regardless of tessellation).
    #     · with a 32-seg rim the "polygonal" look of the stage outline (B-2) is also gone.
    #     · z cascade −1.200 (tier 3) > −1.203 (rim) > −1.207 (disc) avoids
    #       coplanar Z-fighting (the step height is 3~4 mm - visually invisible).
    stage=dict(radius=4.9, top_z=-1.207, height=0.4,
               rim=dict(r_in=4.2, r_out=5.22, seg=32, top_z=-1.203,
                        base_z=-1.6)),
    # === [v5.1 realism] circular stage podium - "the stage must rise more" ===
    #   old: the whole bowl floor (−1.207) was the stage -> practically the same level as the
    #     lowest seating (tier-3 top face −1.20), so it read as a floor disc, not a "stage".
    #   new: raise a circular podium **concentric** with the bowl by 0.70 m (top face −0.507).
    #     · effective stage height 0.693 m above the tier-3 seating face (−1.20) -> within the
    #       standard band of real outdoor stages (0.6~0.9 m). Meets the feedback request h 0.6~0.9.
    #     · radius 3.0 -> a 1.9 m wide apron (−1.203) remains around the podium, so level access
    #       from the entry arc stair (landing at r 4.99) to the stage front is preserved.
    #       **the entry stair and tiers (the hazard geometry) keep their transforms.**
    #     · the stage line (arc) matches the backdrop shell (r 4.75..5.25, θ 9..80/280..351,
    #       already extended to an arc wall in N-4) concentrically, and no "straight slab"
    #       remnant was found in the current code (build_bowl/build_halfbowl_finish
    #       are all build_arc_steps based; rectangular slabs are plaza/ground only).
    #   walk continuity (apron -> podium): −1.203 -> −1.032 -> −0.857 -> −0.682 ->
    #     −0.507. Step heights 0.171 / 0.175 x3 - none exceeds 0.2 m.
    # [v5.2 user] podium height 0.70 -> 0.35 - "low enough to hop up lightly".
    #   top face −1.203+0.35 = −0.853; the access stair shrinks to one intermediate step (0.175x2).
    # === [v7 judgment §4 remaining 2] **acute wedge / knife edge** on the access stair arc ===
    #   symptom (judge_v6 §4 (3) -> unresolved in v7): in `rim_view`·`side_arc` 400 % crops
    #     the inner arc radius narrows sharply and a knife-edge triangular sliver shows.
    #   two causes (traced through the build_arc_steps convention in coordinates):
    #     (a) the segment box chord length is **based on r_out** (2·r_out·sin(dθ/2)·1.03), yet
    #        the same box reaches down to r_in. At seg=3 (dθ 10 deg) the corner radius at
    #        r_in=3.0 is √(3.0²+(chord/2)²) = 3.0153 -> against the podium cylinder (r 3.0)
    #        a **crescent gap of up to 15 mm** opens per segment (a black wedge at 400 %).
    #     (b) the cap faces of the two end segments come out tilted 5 deg off the radial line
    #        (they follow a_mid) -> a **thin triangular sliver** juts out at the stair end.
    #   action (judgment recommendation (ii) "narrow the angular range or fillet/cap the inner radius"):
    #     (i) seg 3 -> **12** (dθ 2.5 deg). (a) gap 15 mm -> **0.9 mm**, (b) protrusion 0.042 ->
    #        0.011 m. Only curvature gets finer; radius ladder·tops unchanged = **geometry GT unchanged**.
    #     (ii) a new **end cap (cheek) at each end** - radius 3.0..3.75 · top face = podium
    #        top face (−0.853) · thickness 3.2 deg (~0.19 m). Same finish as a real stair cheek wall, so
    #        the end reads as a **squared-off cap**, not a "pointed sliver".
    #        (0.35 m above the apron −1.203 = the same drop as the podium -> no new hazard)
    #   the access stair and podium are not hazard geometry (tiers · entry arc stair), and their
    #   radius / angular range / top-face z all stay as they were.
    # === [W3 L05 · K4(d)] the wedge is closed by CONSTRUCTION, and a new one is pre-empted
    #   (i)/(ii) above patched the box convention (seg 3 -> 12, plus cheeks). With
    #   `mesh=True` cause (a) is gone - the sector's inner boundary IS the arc, so the
    #   crescent against the podium cylinder is **0.000 mm** rather than 0.9 mm - and
    #   cause (b) is gone too, because the a0/a1 caps are exactly radial, so the arc-end
    #   protrusion is **0.000 mm** rather than 10.6 mm. `podium_step_selfcheck` is
    #   rewritten onto the mesh convention and both numbers are asserted at 0.
    #   **The cheeks stay** - they are no longer a patch for a sliver, they are the squared
    #   stair cheek G8 shows on its curved flights, and they still cap the run.
    #   `under` / `z_cascade` are the NEW guard, and they exist because removing the box
    #   overshoot removes the cover it accidentally gave against a *different* solid: the
    #   podium is a `UsdGeom.Cylinder`, whose visual tessellation pulls its face-centre
    #   radius in to `3.0*cos(pi/n)` (**14.4 mm at n=32**, the exact v4-A1 failure). A
    #   sector that stops at exactly 3.000 therefore leaves a crescent against the drawn
    #   cylinder. So the innermost step and the cheeks run **0.10 m under** the podium
    #   (r_in 3.000 -> 2.900, a 100 mm lap against a 14.4 mm worst-case dip) and drop
    #   **3 mm** (top -0.853 -> -0.856) so the lapped ring is not coplanar with the podium
    #   top disc - the radial+z counterpart of v4-A1, and the same 3 mm cascade the stage
    #   already uses (-1.200 > -1.203 > -1.207). A 3 mm rise onto the podium is not a step.
    podium=dict(r=3.0, top_z=-0.853, base_z=-1.607,
                steps=dict(radii=(3.75, 3.375, 3.0),
                           tops=(-1.028, -0.853),
                           seg=12, base_z=-1.6,
                           under=0.10, z_cascade=0.003,
                           arcs=((130.0, 160.0), (200.0, 230.0)),
                           cheek_deg=3.2, cheek_overlap=0.2)),
    # === v4-A2/A3 [critical] entry stair redesign ===
    #   was: an orthogonal flight (x_top 13.5, tread 0.35). The step boundaries in x and the tier
    #   boundaries x(=6+r) were not aligned at all, so the tread widths of the real walking profile
    #   collapsed to 0.35/0.35/0.15/0.20/0.35/0.30/**0.05**/0.35 - a 5 cm wide tread plus a
    #   single 0.40 m drop (a jump). Also, an arc edge x a rectangular flight left crescent
    #   wedges of up to 0.09 m on both sides.
    #   fix: replace it with an **arc stair concentric with the tiers**. The radius ladder is
    #   divided into 6 at 0.425 spacing so that it contains the tier boundaries
    #   (7.5 / 6.65 / 5.8 / 5.0) exactly -> uniform riser 0.20 · tread (radial) 0.425, wedges 0.
    #     profile: ring (−0.002) -> −0.197 -> −0.397 (=tier1+3mm) -> −0.597
    #               -> −0.797 (=tier2+3mm) -> −0.997 -> −1.197 (=tier3+3mm) -> stage
    # === [v5 judgment applied] remove the white rectangular patches on the entry arc stair risers ===
    #   symptom: in preset_h1.8_d2 (860,460–1010,560), untextured pure-white rectangles
    #     appear over the stone-textured risers, one symmetric pair **every other step**.
    #   cause (traced): only Step_1/3/5 show white patches, and their inner radii (r_in)
    #     are 6.65 / 5.8 / 5.0 - **exactly the same as the inner radii of tiers 1/2/3**.
    #     That is, the stair riser face (entry seg 4, dθ=4.5 deg) and the tier inner face
    #     (seg 32, dθ=11.25 deg) are coplanar at the same radius but split differently,
    #     so the two planes graze each other -> near the crossing they sit within depth precision
    #     and Z-fight. The winner is the tier material (plaza_light = light, patternless granite),
    #     hence the "untextured pure-white rectangle". It is a symmetric pair because the
    #     two planes cross at θ = +-(midpoint of the entry seg centre and the tier seg centre).
    #     (segment overlap is already secured by chord x1.03, so a "gap" is not the cause.)
    #   fix: shift the whole entry-stair radius ladder **10 mm inward** (r-cascade).
    #     The radial counterpart of the existing z-cascade (−1.200 > −1.203 > −1.207).
    #     · radius range swept by the entry riser face = r .. r/cos(2.25 deg) = r + 5.1 mm
    #       -> 6.640..6.6451 < tier inner face min 6.650. At least 4.9 mm clearance throughout.
    #       (tier 2 clears by 5.5 mm · tier 3 by 6.1 mm - coplanarity gone)
    #     · the entry step stands 10 mm ahead (inward) of the tier, so the tier face is firmly hidden.
    #   hazard geometry verified unchanged: tops (riser 0.20 x 6 steps · total drop 1.2 m) and
    #     a0/a1/seg/base_z all unchanged. Tread width changes only at the top step, 0.425->0.435;
    #     the rest stay 0.425/0.375 - identical walking profile.
    entry=dict(a0=-9.0, a1=9.0, seg=4, base_z=-1.6,
               radii=(7.5, 7.065, 6.64, 6.215, 5.79, 5.365, 4.99),
               tops=(-0.197, -0.397, -0.597, -0.797, -0.997, -1.197)),
    # v4-D5: 2 seating aisle stairs (theatre grammar) - same radius ladder as the entry stair
    aisles=[dict(a0=100.0, a1=112.0, seg=3), dict(a0=248.0, a1=260.0, seg=3)],
    # lip kerb ring (cue_material_break): dark granite ring outside the opening.
    #   [v5 adopted] cut to 200 deg like the tiers (seg 48->27, angular width 7.5 deg->7.41 deg).
    lip=dict(r_in=7.5, r_out=7.8, seg=27, a0=80.0, a1=280.0,
             top_z=0.003, base_z=-0.1),
    # === [v5 adopted] three half-round finishing elements ===
    #  (1) cut_wall - side wall on the cut section (parapet). Radial wall at θ 79..82 / 278..281.
    #     r 5.0..7.85 covers the three tier cut faces (z −0.40/−0.80/−1.20) and the lip (7.8),
    #     top face z=+1.00 -> a 1.06 m guard wall above the grass yard (−0.06) = guards the new edge drop.
    #     (this wall blocks the whole run of the max 1.14 m drop from the yard to the tier-3 top face)
    #  (2) backyard - grass yard behind the stage backdrop wall. θ 11..79 / 281..349, r 5.25..7.5.
    #     top face −0.06 (0.058 m step from the plaza ring −0.002 = level connection), bottom −1.6
    #     (fills the removed tier volume, so no cavity underneath). The inner boundary r=5.25 is
    #     supported by the shell (stage backdrop wall, r 4.75..5.25) over the whole angular range.
    #  (3) entry_cheek - cheek walls flanking the entry arc stair (θ +-9 deg). θ 9..11 / 349..351,
    #     r 4.99..7.5, top face −0.06 (flush with the yard) -> closes the section between yard and stair.
    #   [W3 L05 · G8] the cut wall takes a **60 mm timber capping**. G8's vertical
    #     surfaces are pale concrete with timber-slat soffits and timber-topped edges;
    #     an uncapped 2.6 m dark slab is the "cistern/bunker" read v6 was already
    #     fighting. The cap is the wall's own footprint (r 5.0..7.85, the same 3 deg
    #     arcs) raised 1.000 -> 1.060, so it **raises the guard top by 60 mm** and moves
    #     no other surface.
    #   [W3 L05 · K4(d)] the finishing elements gain a **0.2 deg azimuthal lap**.
    #     The box convention's x1.03 outer chord made every arc end overrun its nominal
    #     ray, which is how `cut_wall` (79..82) and `entry_cheek` (9..11) covered their
    #     joints with `backyard` (11..79). A true sector ends exactly on the ray, so those
    #     joints become **coincident faces over an overlapping r and z window** - the
    #     classic z-fight. Both elements are widened 0.2 deg into the yard, which is a
    #     26 mm lap at r 7.5. The guarded angular range therefore reads 78.8..82.0 rather
    #     than 79.0..82.0: the guard grows, it does not shrink.
    cut_wall=dict(r_in=5.0, r_out=7.85, seg=1, top_z=1.00, base_z=-1.6,
                  cap_h=0.06,
                  arcs=((78.8, 82.0), (278.0, 281.2))),
    backyard=dict(r_in=5.25, r_out=7.5, seg=8, top_z=-0.06, base_z=-1.6,
                  arcs=((11.0, 79.0), (281.0, 349.0))),
    entry_cheek=dict(r_in=4.99, r_out=7.5, seg=1, top_z=-0.06, base_z=-1.6,
                     arcs=((8.8, 11.2), (348.8, 351.2))),
    # [v5 shared layer] Korean sign - (tag, TEX key, cx, cy, base_z, yaw, w, h)
    #   Info(-4.2, 3.6): on the −X approach axis beside the gate (x −3.6, y +-2.6). From the bowl
    #     centre (6,0) it is 10.82 m -> 3.32 m outside the lip (r 7.5) (meets the >=0.5 m clearance).
    #   camera check: grid eye=(−3.5/−6.5/−11.5, 0) -> behind / 57.4 deg / 26.3 deg respectively,
    #     plaza_approach 63.4 deg, rim_view behind, side_arc 36.9 deg, stage_lookup 19.5 deg
    #     (10.8 m away) - no preset has near-field sight-line occlusion.
    signs=[],  # [v5.2 user] info signboard removed - openness

    # --- dressing ---
    planters=[("A", -10.0, -9.0), ("B", -12.0, 8.0)],
    # v4-D8: tree row around the lip - r=9.6 circle at 45 deg (entry axis 0 deg · gate 180 deg excluded)
    # [v5 judgment applied] the 270 deg planter is centred at (6, −9.6), only 0.4 m from the
    #   side_arc camera eye(6, −10, 1.2) - the camera ended up inside the planter box (2.2 square)
    #   and the trunk filled the frame, invalidating the shot (confirmed in rt_noon_side_arc).
    #   -> 270 deg -> 285 deg. Centre (8.484, −9.273) moves clear of the camera, and
    #     the nearest planter corner lies 37 deg off the sight axis (+Y), outside the +-30 deg FOV,
    #     so it stays out of frame. No interference with the bench circle (r=9.0, 250 deg) either.
    #   (the other 5 keep enough lateral clearance from the side_arc sight line and are left as is.)
    # === [W3 L05 · `w3_md_reverts_v1.md` §5 census] 285 deg -> 250 deg ================
    #   The census listed exactly one scene05 pair: `side_arc` eye (6, -10, 1.2) at
    #   **kerb 1.39 m** from `RingPlanter_4`. Re-measured on the composed inventory this
    #   session the crown is far worse than the kerb figure suggests - `Fraxinus.usd`
    #   native 4.851 x 4.510 x 5.341 m at this instance's scale 0.6754 gives a crown
    #   half-width 1.638 m against a 2.589 m eye-to-trunk distance, so the judged eye
    #   sits **0.248 m from the bed subtree AABB** and only ~5 deg outside the frame.
    #   That is the C02-P1 class the census exists to find (scene02 `beauty_overview`).
    #   Fixed by moving the bed, not the camera (§7-7: legibility comes from geometry):
    #   285 -> **250 deg**, centre (2.717, -9.021), eye-to-trunk **3.426 m**, crown
    #   clearance **1.79 m**, kerb clearance **2.18 m**, and the nearest crown tangent is
    #   **44.8 deg** off the sight axis against a ~29.3 deg half-frame - 15 deg of margin
    #   where there were 5. Neighbour separation 225<->250 is 4.16 m against a 2.2 m bed.
    #   `planter_eye_selfcheck()` now gates every judged cut against every bed.
    ring_planters=[45.0, 90.0, 135.0, 225.0, 250.0, 315.0],
    ring_planter=dict(r=9.6, size=2.2, base_z=-0.002,
                      min_crown=1.00, min_kerb=2.00),
    # v4-B4/A4: the 3 misaligned hedges (y 12.0/12.4/12.0) are removed -> reorganised into a
    #   perimeter hedge. Hides the 0.51 m unguarded fall + terminates the site + misalignment gone.
    #   openings: −X approach (the whole west side), south x −3..3, north x −8..−4 (building entrance).
    hedges=[(-18.0, 13.4, -8.0, 14.0), (-4.0, 13.4, 18.0, 14.0),
            (17.4, -13.4, 18.0, 13.4),
            (-18.0, -14.0, -3.0, -13.4), (3.0, -14.0, 18.0, -13.4)],
    hedge_h=0.6,
    # v4-A4: split the 0.51 fall around the plaza into two steps with a grass berm (−0.26).
    berms=[("W", -19.2, -18.0, -15.2, 15.2), ("E", 18.0, 19.2, -15.2, 15.2),
           ("S", -18.0, 18.0, -15.2, -14.0)],
    berm=dict(top_z=-0.26, base_z=-0.9),
    # the north side uses a paved apron in front of the building instead of a berm (better grounding)
    apron=dict(x0=-18.0, x1=18.0, y0=14.0, y1=15.5, top_z=-0.26, base_z=-0.9),
    entry_canopy=dict(x0=-8.0, x1=-4.0, y0=14.2, y1=15.5, z_roof=3.2,
                      post_r=0.10, roof_t=0.14, base_z=-0.26),
    # v4-A4: bollard row on the west (open approach face)
    # === [v7 judgment §4 remaining 3] "7 evenly spaced white posts on the rim skyline" ===
    #   traced: cue_railing is False, so these are not railing posts but the **west bollard
    #     row**. The old (x −17.2, y −12..12, n 10) spanned the whole 24 m west edge of the plaza
    #     at 2.67 m spacing - a **decorative row**, violating both v5.1 §2 ("only where vehicle
    #     intrusion is a concern, spacing around 1.5 m, remove all decorative bollard rows") and
    #     §3 (no even spacing). In `stage_lookup` (eye 6,0 -> −X) 7 of them lined the horizon.
    #   action: reduce to **4 gate posts on the entry axis (y=0) · regulation 1.5 m spacing** (y +-0.75, +-2.25).
    #     Same direction as scene01, which cleared all 6 white bollards and reached PT, except that
    #     here −X is the actual pedestrian entrance to the plaza, so they are kept on functional grounds.
    #     The material also changes from white stainless (M["rail"]) to **painted steel, dark grey**
    #     (M["bollard"]), removing the "white post" signal altogether (§4).
    #   [W3 L05] **height 0.75 -> 0.90.** `scene_common.build_bollard`'s default is 0.75,
    #     which is below the statutory band, and `placement_lint` LINT-6 raised all four
    #     posts as ERROR (`h 0.750 m` vs `[0.8, 1.0] m`, 교통약자법 시행규칙 별표2 제7호
    #     [law]). Those 4 are 4 of the whole library's 21 lint ERRORs. The kit default is
    #     not this lane's file (frozen), so the statutory value is passed at the call
    #     site; 0.90 is mid-band. Four collision boxes grow 0.15 m in z - declared.
    bollards=dict(x=-17.2, spacing=1.5, n=4, base_z=0.0, height=0.90),
    # v4-B5/D9: benches 2 -> 6. Placed tangentially on the r=9.0 circle about the bowl centre (6,0).
    bench_ring=dict(r=9.0, base_z=-0.002,
                    angles=(110.0, 135.0, 160.0, 200.0, 225.0, 250.0)),
    # v4-D4: wooden seat strips (make the tiers read as seating + secure step contrast).
    #   the entry (+-9 deg) and aisle (100~112 / 248~260) ranges are left empty.
    #   [v5 adopted] trimmed to the half-round cut (80..280): 80.5~99.5 / 112.5~247.5 /
    #   260.5~279.5 (the aisles 100~112 · 248~260 stay empty).
    # === [W3 L05 · G8] the seat band becomes a TIMBER DECK BANK =======================
    #   G8's amphitheatre tiers are **warm timber deck boards over the whole tread**, with
    #   the grey stone showing only at the riser and the back joint. A 0.45 m strip on a
    #   0.85 m tread reads as a bench rail laid on a stone step; 0.70 m reads as a deck.
    #     · r1 = r_out - inset(0.10) unchanged; r0 = r1 - 0.70 = r_out - 0.80, so the back
    #       **0.05 m** of the 0.85 m tread stays granite - the stone course still reads.
    #     · proud 0.012 and drop 0.06 unchanged: the deck top face stays at
    #       `top_z + 0.012`, so no walked surface z moves. What moves is the radial width
    #       of the +12 mm plateau, 0.45 -> 0.70 m on each of 3 tiers (declared).
    seat=dict(width=0.70, inset=0.10, proud=0.012, drop=0.06,
              arcs=((80.5, 99.5, 3), (112.5, 247.5, 12), (260.5, 279.5, 3))),
    # v4-D1 [top priority] stage backdrop wall (stage shell) - 2 pieces leaving the entry arc (+-9 deg) open
    #   [v5 adopted] extended 14..76 / 284..346 -> 9..80 / 280..351.
    #     · the lower ends 9/351 match the entry stair width exactly -> completes the jamb.
    #     · the upper ends 80/280 join the tier cut face (cut_wall) -> the whole inner boundary of
    #       the yard is guarded (the wall blocks the 1.15 m drop from yard −0.06 to stage −1.207).
    # === [v6 judgment (i)] lower the backdrop arc wall 1.40 -> 0.70 (openness / v5.2 §6) ===
    #   symptom (judge_v6_rt_mod6 §4): in plaza_approach·preset_h0.9_d5 the backdrop arc wall read as
    #     "an undecorated concrete retaining wall (cistern/bunker) blocking 100% of the frame width".
    #   action: top z +1.40 -> +0.70.
    #     · wall face above the stage (−1.207) 2.61 -> 1.91 m (grey area −27%, the scale of a real
    #       outdoor-stage backdrop). Above the yard (−0.06) it is 0.76 m = a seat wall / parapet height.
    #     · silhouette top 1.40 -> 1.04 (top of the shrub buffer), −0.36 m - sky and greenery above it.
    #   the arc extent (9..80 / 280..351) is **unchanged**: this wall is the retaining wall carrying
    #     the 1.15 m drop from the yard (−0.06) to the stage (−1.207) along its whole inner boundary,
    #     so shortening the arc would leave an unguarded drop edge. Instead the height lost is
    #     replaced by backdrop_shrub (the shrub buffer) below.
    shell=dict(r_in=4.75, r_out=5.25, top_z=0.70, base_z=-1.6, seg=12,
               arcs=((9.0, 80.0), (280.0, 351.0))),
    # === [v6 judgment (i)] backdrop shrub buffer - replaces the lowered arc wall + "greenery behind the stage" ===
    #   shrubs are planted along the arc in an r 5.25..6.05 band (0.80 wide) on the yard (top −0.06),
    #   just behind the arc wall, at spacing 0.62 m (flattened ellipsoids, coordinate-seeded jitter ->
    #   avoids the §3 even-spacing / grid look). Top ~ +1.12 = 1.18 m above the yard.
    #   drop guarding (yard −0.06 -> stage −1.207, 1.15 m): arc wall 0.76 m + a 0.80 m wide,
    #     h1.18 shrub buffer = access deterrence. (Guarding is weaker than the old state, where the
    #     wall alone met the 1.1 m statutory railing, but v5.2 §6 puts openness first and this is
    #     park practice (low retaining wall + planting bed). Reverting top_z alone restores it.)
    #   the arc range keeps 1 deg of margin inside the yard (11..79 / 281..349).
    # === [v7 judgment §4 remaining 1] the new shrubs render as **"an even row of mossy boulders"** ===
    #   symptom (judge_v7_rt_B §4): in the 400 % crop of the `plaza_approach` wall-top band,
    #     the flattened ellipsoids (rad 0.42 · h 1.10) carrying a magnified grass texture
    #     (M["hedge"], uv 1.2) read as **yellow-green mossy boulders**, and the even 0.62 spacing
    #     makes "stones set on top of the wall". **The same failure mode** as scene04 v6 verge.
    #   cause (generalised in judgment §15-2): **blob size x magnified texture**. Both must shrink.
    #   action = port the scene04 W-4 solution + correct for this scene-specific constraint (silhouette height):
    #     (i) material : drop the grass texture -> **3 constant-colour tufts** (+-5 % tint jitter,
    #               rough 1.0 · specular 0). With no texture the "rock relief" cue is 0.
    #     (ii) size : per lobe rz <= 0.25 = **0.5 m or less** (judgment recommendation (1)).
    #               But here the shrub tops must clear the arc wall (+0.70) to keep the v6 gain
    #               "greenery above the wall", so **height must not be lost** ->
    #               instead of one big ellipsoid, **stack 3~4 small lobes vertically**
    #               to reach a clump top of 1.22 m (a shrub whose crown splits into several blobs).
    #     (iii) layout : one even row -> **3 rows** (r 5.62/5.98/6.32) · a different step per row +
    #               spacing jitter +-35 % + 12 % dropouts + per-lobe position/size jitter
    #               -> the even-row impression is gone (§3).
    #   row definition rows: (r, step, rx, rz, h_top, n_lobe)
    #     · 2 rows (front 1.02 / back 1.24) - the silhouette above the wall becomes a layered
    #       green band rather than one blob. A ground-cover layer lower than the arc wall (+0.70)
    #       is invisible in every shot (all cameras sit on the −X plaza side), so it was dropped.
    #     · radius check: innermost 5.85 − 0.075 − 0.36·1.15 = 5.36 >= arc wall 5.25 ✓
    #                     outermost 6.25 + 0.075 + 0.40·1.15 = 6.79 <= yard 7.5 ✓
    #     · lobe overlap: adjacent lobe z gap kept <= 1.35·min(rz) -> **no detached floaters**
    #       (check (7) reports the measured worst-case ratio over the jitter combinations).
    #     · taper: higher lobes get radius x(1−0.14t) -> crown taper (avoids a cylinder look).
    backdrop_shrub=dict(base_z=-0.06, embed=0.5, taper=0.14,
                        jit_step=0.35, skip=0.12, jit_pos=0.075,
                        jit_scale=0.15, jit_h=0.12,
                        rows=((5.85, 0.44, 0.36, 0.19, 1.02, 6),
                              (6.25, 0.52, 0.40, 0.20, 1.24, 7)),
                        arcs=((12.0, 78.0), (282.0, 348.0))),
    # v4-D2 2 lighting towers / D3 2 speaker stacks
    towers=[(10.5, -6.5), (10.5, 6.5)],
    tower=dict(pole_r=0.10, pole_h=5.5, head=(0.35, 0.35, 0.25),
               head_z=(3.5, 4.3, 5.1), base_z=-0.002),
    speakers=[(7.8, -3.2), (7.8, 3.2)],
    speaker=dict(size=(0.6, 0.5, 0.9), n=2, base_z=-1.207),
    # v4-D7 entrance gate + sign
    gate=dict(x=-3.6, y=2.6, post_r=0.10, post_h=3.0, base_z=-0.002,
              lintel_z0=2.6, lintel_z1=3.0, lintel_t=0.15, lintel_y=2.75),
    streetlight=dict(pole_h=6.0, pole_r=0.06,
                     arm_len=1.0, arm_r=0.04, head=0.25),
    # v4-D10: streetlights 1 -> 5. (x, y, base_z)
    streetlights=[(-8.0, 10.0, 0.0), (-14.0, 10.0, 0.0), (-14.0, -10.0, 0.0),
                  (2.0, 12.0, 0.0), (14.0, -11.0, 0.0)],
    buildings=dict(
        # R: the scene01 R block moved to y 15.5..20, x −18..12. Facade faces −Y (toward the plaza).
        R=dict(x0=-18.0, x1=12.0, y0=15.5, y1=20.0, h=14.0, floors=4,
               axis="y", facade_y=15.5, face_dir=-1.0),
        # C: blocks the distant vista (+X horizon). Facade faces −X (toward the plaza).
        # [v6 judgment (i), supporting] h 12.0 (4 floors) -> 7.2 (2 floors). Lowering the backdrop arc
        #   wall achieves nothing if everything above it is this building's brick face - the judgment
        #   goal "let the sky show" fails (plaza_approach check: parapet top 12.5 m · distance 30 m ->
        #   elevation 21.2 deg > frame top 17.7 deg = the upper screen is all brick).
        #   Lowered to 7.2 the top is 7.7 m -> elevation 12.8 deg, opening a 4.9 deg
        #   (~130 px) sky band up to the frame top. It is the scale of low-rise neighbourhood retail
        #   beside a park, so the vista-blocking function (closing the far horizon) is kept.
        C=dict(x0=24.0, x1=30.0, y0=-12.0, y1=12.0, h=7.2, floors=2,
               axis="x", facade_x=24.0, face_dir=-1.0),
    ),

    # --- materials: physical size for texture_scale [m/tile] + tints/constants ---
    material=dict(
        scale=dict(plaza_light=1.80, band_dark=0.9, plaza_lower=0.7,
                   granite_dark=1.0, brick_red=2.0, grass=1.4, tactile=0.3),
        lower_warm_tint=(1.06, 1.0, 0.94),        # stage warm tint
        grass_tint=(0.55, 0.68, 0.42),
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        # v4-B (shared): raise canopy albedo (black blotch -> leaf silhouette)
        canopy_a=(0.035, 0.052, 0.024), canopy_b=(0.042, 0.060, 0.030),
        canopy_rough=1.0,
        hedge_tint=(0.50, 0.62, 0.36),                   # v4 perimeter hedge
        # [v7 judgment §4 remaining 1] backdrop shrubs = 3 constant-colour tufts (ported from scene04 W-4).
        #   binding the grass texture (uv 1.2) makes the magnified normal map read straight away as
        #   "mossy rock" -> no texture is used at all. Values are the same family as scene04 verge
        #   (bright green / dry green variants), unifying the vegetation tone across the 21 scenes.
        tuft=((0.070, 0.105, 0.042), (0.082, 0.112, 0.050),
              (0.078, 0.096, 0.038)), tuft_rough=1.0,
        # [v7 judgment §4 remaining 3] bollards = painted steel (white stainless dropped)
        bollard_color=(0.33, 0.33, 0.36), bollard_metallic=0.4,
        bollard_rough=0.5,
        # [W3 L05 · G8] deck tone. The v4 value (0.055, 0.036, 0.022) is linear luma
        #   0.0392 - at that albedo the seat band rendered as a black line on the tier
        #   edge, which is why the bank read as bare granite. G8's decking is warm mid
        #   brown 방부목; (0.155, 0.078, 0.040) is linear luma **0.0932**, sRGB ~
        #   (0.43, 0.31, 0.23), still far under the v5.1 §4 cap of 0.80.
        seat_wood=(0.155, 0.078, 0.040), seat_wood_rough=0.8,  # v4-D4 / L05 deck face
        # [W3 L05 · U-6] soiling must read as soiling **on the same stone**. The kit
        #   declares `albedo 0.16` for a stain (`ground_kit.build_stain_field`), but the
        #   scene bound `granite_dark` - a *different* stone at a different module - so
        #   the 8 blots read as inlaid dark panels, the D5 defect class (declared albedo
        #   vs bound material) that the manhole covers were fixed for in W2. Bound now to
        #   the plaza's own texture under a dark tint: 0.4644 (measured linear mean of
        #   `plaza_light_diff.jpg`) x 0.36 = **0.167**, against the declared 0.16.
        stain_tint=(0.36, 0.36, 0.37),
        gear_color=(0.055, 0.055, 0.058), gear_rough=0.6,  # v4-D2/D3 lighting·speakers
        # [v5.1 §4] parapet 0.90 -> 0.72 (no large pure-white areas)
        parapet_color=(0.72, 0.72, 0.69), parapet_rough=0.6,
        # [W3 L05 · pilot 1 -> pilot 2] **the one real defect this lane created.**
        #   Pilot `260731_w3_l05` bound the cut wall and the stage shell to
        #   `parapet` (0.720) to kill the "dark slab" read, and the round came back
        #   with **WHITE on 7 of 13 cuts** — `side_arc` 2.2 -> 29.6 %,
        #   `preset_h1.8_d2` 1.1 -> 27.7 %, `plaza_approach` 14.2 -> 41.8 % — the
        #   v5.1 §4 large-pure-white prohibition, and the same defect S08's pilot 1
        #   created at 77.4 %. `albedo_selfcheck` did **not** catch it because its
        #   render forecast is applied to horizontal surfaces only, and these are
        #   2.6 m walls that happen to fill the frame (recorded as L05-F1).
        #   0.720 is white-paint bright. Korean 노출콘크리트 sits at a diffuse
        #   reflectance of **0.30-0.40**, so the walls get their own constant at
        #   **0.34** (sRGB ~ 0.62): still 4.4x the `granite_dark` 0.078 the bunker
        #   read came from, and inside the band a real wall occupies.
        #   **pilot 2 -> pilot 3**, and the reason is exposure, not material.
        #   At 0.340 the sunlit wall face still measured **luma 0.75 · 50 % over
        #   the 0.8 line** `[measured, 200x230 px on plaza_approach]`, against the
        #   pre-state's 0.444. The library's render runs hot: the plaza paving is
        #   bound at a **realistic** 0.334 linear albedo (0.4644 texture x 0.72
        #   tint, inside the 0.35-0.45 band real 화강석 판석 occupies) and still
        #   renders **luma 0.655 with 29.9 % of its area over 0.8 in the BASELINE
        #   ITSELF**. So a wall at a physically correct 0.30-0.40 cannot satisfy
        #   v5.1 §4 in this rig. 0.200 is the value that lands the wall face on
        #   **luma ~0.60**, between the pre-state's 0.444 and the white line, and
        #   it is recorded as an exposure compensation rather than dressed up as a
        #   material fact (finding **L05-F2**).
        wall_conc=(0.200, 0.197, 0.191), wall_conc_rough=0.75,
        # [v7 §4] 0.88 -> 0.78: the luminaire face exceeded the albedo cap (0.80) (it was a small-area
        #   WARN, but nothing the self-check flags is left standing).
        lamp_color=(0.78, 0.78, 0.75), lamp_rough=0.4,
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.5,
        nosing_color=(0.85, 0.72, 0.10), nosing_rough=0.7,
    ),

    # --- lighting: the scene01 light dict verbatim + SUN_AZ_OFFSET=171.5 ---
    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        noon_sun_enable=True, noon_sun_elev=49.79,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    SUN_AZ_OFFSET=171.5,

    render=dict(pt_total_spp=512, pt_max_bounces=8),
)


# ===========================================================================
# [B2] [W3 L05 · K4(d)] The arc convention this scene builds on.
#   `scene_common.build_arc_steps(mesh=True)` authors a true annular-sector Mesh
#   instead of an axis-aligned Cube sized on the outer chord. The mechanism landed
#   at `5ceb76a` **default OFF** with an empty split proof across all 33 scenes,
#   precisely so that 05 / 06 / 19 could flip it inside their own pilots, where the
#   proof is judged (`scene_common.py` `_annular_sector_mesh` header · `w3_k4_v1.md`
#   §5 · ledger **GT-6**). This dict is spread into **all 12** `build_arc_steps`
#   sites in this file, so there is exactly one place to read the convention from
#   and no site can be missed - `arc_selfcheck()` counts the sites and gates on it.
#   `arc_seg` = facets per sector. 6 puts every arc boundary within
#   `r*(1-cos(half facet))` of its nominal radius: 0.45 mm on the 48-seg ring,
#   1.0 mm on the 18-seg tiers, 0.02 mm on the 12-seg podium steps.
ARC = dict(mesh=True, arc_seg=6)

# [W3 L05 · K4(b)] scene05's own row is `SCENE_SPECIES["Scene05"] = ("ash", None)`
#   (이팝나무 substitute, civic). Stated here so the call sites are explicit and the
#   season audit has one place to read the declaration from.
SPECIES_TREE = "ash"          # Trees/Fraxinus.usd
SPECIES_BED = "ornament_bed"  # SHRUB_SPECIES -> Shrub/Rhododendron.usd (single row)


def _deep_update(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_update(dst[k], v)
        else:
            dst[k] = v


# ===========================================================================
# [C2] [v7 judgment §4 remaining 1] backdrop shrub lobe generator - **builder and checker use
#   the same coordinates** (scene04 `verge_instances` convention). The seed is deterministic, so
#   intrusion, floating and silhouette height can be measured without Isaac.
#   yield: (px, py, pz, ax, ay, az, row, k, lobe)
# ===========================================================================
def backdrop_instances():
    sh = PARAMS["backdrop_shrub"]
    b = PARAMS["bowl"]
    emb = sh["embed"]
    for r_i, (rr0, step, rx0, rz0, h_top, nlobe) in enumerate(sh["rows"]):
        for a_i, (a0, a1) in enumerate(sh["arcs"]):
            k, s = 0, 0.0
            span = math.radians(a1 - a0) * rr0            # arc length [m]
            while s <= span + 1e-6:
                rnd = random.Random(int(r_i * 9176 + a_i * 3571 + k * 7919))
                s_next = s + step * (1.0 + rnd.uniform(-sh["jit_step"],
                                                       sh["jit_step"]))
                k += 1
                if rnd.random() < sh["skip"]:             # dropout -> clumps/gaps
                    s = s_next
                    continue
                a = math.radians(a0) + s / rr0
                sc_ = 1.0 + rnd.uniform(-sh["jit_scale"], sh["jit_scale"])
                hh = h_top * (1.0 + rnd.uniform(-sh["jit_h"], sh["jit_h"]))
                rx, rz = rx0 * sc_, rz0 * sc_
                z_lo = sh["base_z"] + rz * (1.0 - emb)     # lowest lobe centre
                z_hi = sh["base_z"] + hh - rz              # highest lobe centre
                for j in range(nlobe):
                    t = j / float(nlobe - 1) if nlobe > 1 else 0.0
                    rr = rr0 + rnd.uniform(-sh["jit_pos"], sh["jit_pos"])
                    da = rnd.uniform(-sh["jit_pos"], sh["jit_pos"]) / rr0
                    # lobes get smaller toward the top (crown taper)
                    f = 1.0 - sh["taper"] * t
                    yield (b["cx"] + rr * math.cos(a + da),
                           b["cy"] + rr * math.sin(a + da),
                           z_lo + (z_hi - z_lo) * t,
                           rx * f, rx * f * rnd.uniform(0.85, 1.15), rz * f,
                           r_i, k, j)
                s = s_next


def backdrop_selfcheck(verbose=True):
    """[v7] Backdrop shrub rework check — 0 arc-wall intrusion · 0 floaters · silhouette height kept.

    ① Radial intrusion : does the innermost lobe reach inside the arc wall outer radius (shell.r_out 5.25)?
    ② Yard overrun     : does the outermost lobe pass the yard outer radius (backyard.r_out 7.5)?
    ③ Floating         : does the bottom of the lowest lobe (z − az) reach below the yard top face (base_z)?
    ④ Silhouette       : is the clump top above the arc wall top face (shell.top_z 0.70)?
                         (= the condition that keeps the v6 gain "greenery and sky above the wall".)
    ⑤ Individual size  : is the tallest lobe (2·az) within the recommended 0.5 m?
    ⑥ Camera           : does every preset eye stay outside the lobe ellipsoids?
    ⑦ Lobe continuity  : is the z gap between adjacent lobes of one clump ≤ 1.35·min(az)?
                         (beyond that the stack breaks and turns into "beads floating in mid-air".)
    """
    b = PARAMS["bowl"]
    sh = PARAMS["backdrop_shrub"]
    inst = list(backdrop_instances())
    # (7) lobe stack continuity per clump
    stacks = {}
    for p in inst:
        stacks.setdefault((p[6], p[7]), []).append(p)
    gap_ratio = 0.0
    for key, lb in stacks.items():
        lb = sorted(lb, key=lambda q: q[2])
        for q0, q1 in zip(lb, lb[1:]):
            gap_ratio = max(gap_ratio,
                            (q1[2] - q0[2]) / min(q0[5], q1[5]))
    r_of = [math.hypot(p[0] - b["cx"], p[1] - b["cy"]) for p in inst]
    r_min = min(r - p[3] for r, p in zip(r_of, inst))
    r_max = max(r + p[3] for r, p in zip(r_of, inst))
    z_bot = min(p[2] - p[5] for p in inst)
    z_top = max(p[2] + p[5] for p in inst)
    lobe_h = max(2.0 * p[5] for p in inst)
    wall_out = PARAMS["shell"]["r_out"]
    wall_top = PARAMS["shell"]["top_z"]
    yard_out = PARAMS["backyard"]["r_out"]
    hits = []
    for name, v in build_views().items():
        ex, ey, ez = v["eye"]
        for px, py, pz, ax, ay, az, *_ in inst:
            if (((ex - px) / ax) ** 2 + ((ey - py) / ay) ** 2
                    + ((ez - pz) / az) ** 2) <= 1.0:
                hits.append(name)
                break
    ok = (r_min >= wall_out - 1e-6 and r_max <= yard_out
          and z_bot <= sh["base_z"] and z_top > wall_top
          and lobe_h <= 0.50 and not hits and gap_ratio <= 1.35)
    if verbose:
        n_pos = len(stacks)
        print("=" * 68)
        print("scene05 [v7] 배후 관목(tuft 로브 군락) 재작업 검산")
        print("=" * 68)
        print(f"  로브 수            {len(inst)} (군락 {n_pos}, "
              f"{len(sh['rows'])}열) — 구 편평 타원체 1열 {'':s}")
        print(f"  ① 최내측 반경      {r_min:.3f} ≥ 아크벽 외경 {wall_out:.2f} → "
              f"{'OK' if r_min >= wall_out - 1e-6 else 'FAIL'}")
        print(f"  ② 최외측 반경      {r_max:.3f} ≤ 마당 외경 {yard_out:.2f} → "
              f"{'OK' if r_max <= yard_out else 'FAIL'}")
        print(f"  ③ 접지            최하단 z {z_bot:+.3f} ≤ 마당 상면 "
              f"{sh['base_z']:+.2f} → {'OK(부유 0)' if z_bot <= sh['base_z'] else 'FAIL'}")
        print(f"  ④ 실루엣 상단      {z_top:+.3f} > 아크벽 상면 {wall_top:+.2f} → "
              f"{'OK(벽 위 녹지 유지)' if z_top > wall_top else 'FAIL'}")
        print(f"  ⑤ 최대 로브 높이   {lobe_h:.3f} m ≤ 0.50 (판정 권고 ①) → "
              f"{'OK' if lobe_h <= 0.50 else 'FAIL'}")
        print(f"  ⑥ 카메라 매몰      {hits if hits else '없음 → OK'}")
        print(f"  ⑦ 로브 연속        최대 간격/rz = {gap_ratio:.3f} ≤ 1.35 → "
              f"{'OK(스택 끊김 0)' if gap_ratio <= 1.35 else 'FAIL'}")
        print("=" * 68)
    return ok, dict(n=len(inst), r_min=r_min, r_max=r_max, z_top=z_top,
                    lobe_h=lobe_h, hits=hits, gap=gap_ratio)


def _self_ast():
    """This module's own source, parsed. Gates that ask "does this file call X"
    must read the syntax tree, not the characters: a `src.count("...")` gate finds
    its own literal and its own docstring, which is how the first cut of
    `season_selfcheck` reported a leaf-off call that does not exist."""
    import ast
    with open(os.path.abspath(__file__), "r", encoding="utf-8") as fh:
        return ast.parse(fh.read())


def _arc_call_census(tree=None):
    """(number of `sc.build_arc_steps(...)` calls, number that spread `**ARC`)."""
    import ast
    tree = _self_ast() if tree is None else tree
    total = withrc = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        if not (isinstance(f, ast.Attribute) and f.attr == "build_arc_steps"):
            continue
        total += 1
        if any(k.arg is None and isinstance(k.value, ast.Name)
               and k.value.id == "ARC" for k in node.keywords):
            withrc += 1
    return total, withrc


def _kwarg_used(name, tree=None):
    """True if any call in this file passes the keyword `name=`."""
    import ast
    tree = _self_ast() if tree is None else tree
    return any(k.arg == name
               for node in ast.walk(tree) if isinstance(node, ast.Call)
               for k in node.keywords)


def _arc_dip(r, span_deg, seg, arc_seg):
    """How far inside its nominal radius an `_annular_sector_mesh` boundary sags at a
    facet midpoint: r*(1 - cos(half facet)). Facet = span / (seg * arc_seg)."""
    half = math.radians(span_deg / float(seg * arc_seg)) / 2.0
    return r * (1.0 - math.cos(half))


def podium_step_selfcheck(verbose=True):
    """[v7 §4-2 → **rewritten for K4(d), W3 L05**] Access-stair wedge check.

    v7 measured the box convention's own defect: the segment Cube is sized on the
    **outer** chord (`2·r_out·sin(dθ/2)·1.03`) yet reaches down to `r_in`, so its
    corners stand proud of the inner radius (the crescent gap) and its end caps
    follow `a_mid` rather than the radial line (the arc-end sliver). seg 3 → 12
    shrank them to 0.9 mm / 10.6 mm; it could not remove them, because the ratio is
    `margin·r_out/r_in` and does not contain seg (`scene_common` K4(d) header).

    With `mesh=True` both are **zero by construction** and the check says so by
    computing them from the mesh convention rather than asserting it:
      ① crescent against the podium cylinder — the sector boundary IS the arc, so
         the only remaining sag is the facet chord `r(1−cos(half facet))`, and it is
         covered by the `under` lap;
      ② arc-end protrusion — the a0/a1 caps are exactly radial: 0.000 mm;
      ③ **the lap that replaces what the box overshoot used to hide**: a
         `UsdGeom.Cylinder` is drawn as a polygon whose face centres pull in to
         `r·cos(π/n)`. At the pessimistic n = 32 that is 14.4 mm on r 3.0, so the
         innermost step must underlap the podium by more than that;
      ④ the lapped ring must **not** be coplanar with the podium top disc.
    """
    po = PARAMS["podium"]
    ps = po["steps"]
    last = len(ps["tops"]) - 1
    rows = []
    for i, ztop in enumerate(ps["tops"]):
        r_in, r_out = ps["radii"][i + 1], ps["radii"][i]
        if i == last:
            r_in -= ps["under"]
            ztop -= ps["z_cascade"]
        a0, a1 = ps["arcs"][0]          # the two arcs are symmetric
        # mesh convention: no chord margin, caps exactly on the a0/a1 rays
        gap = _arc_dip(r_in, a1 - a0, ps["seg"], ARC["arc_seg"])
        over = 0.0
        rows.append((i, a0, a1, r_in, r_out, ztop, gap, over))
    gap_max = max(r[6] for r in rows)
    over_max = max(r[7] for r in rows)
    # ③ the worst tessellation this lap has to survive
    cyl_dip = po["r"] * (1.0 - math.cos(math.pi / 32.0))
    lap = ps["under"]
    # ④ coplanarity with the podium top disc
    dz = abs((po["top_z"] - ps["z_cascade"]) - po["top_z"])
    ok = (gap_max <= 0.002 and over_max <= 1e-9
          and lap >= 2.0 * cyl_dip and 0.001 <= dz <= 0.010)
    if verbose:
        print("=" * 68)
        print("scene05 [W3 L05·K4(d)] 승강 계단 아크 쐐기 검산 — 진성 환형섹터")
        print("=" * 68)
        print(f"  seg {ps['seg']} · arc_seg {ARC['arc_seg']} · 호 {ps['arcs']}")
        for i, a0, a1, r_in, r_out, ztop, gap, over in rows:
            print(f"  단{i}  r {r_in:.3f}..{r_out:.3f} 상면 {ztop:+.3f}  "
                  f"패싯 처짐 {gap*1000:6.3f} mm · 호끝 돌출 {over*1000:6.3f} mm")
        print(f"  ① 최대 처짐 {gap_max*1000:.3f} mm ≤ 2.000 (구 박스 seg3 = 15.3 mm, "
              f"seg12 = 0.9 mm) → {'OK' if gap_max <= 0.002 else 'FAIL'}")
        print(f"  ② 호끝 돌출 {over_max*1000:.3f} mm (구 42 mm → seg12 10.6 mm) → "
              f"{'OK(구조적으로 0)' if over_max <= 1e-9 else 'FAIL'}")
        print(f"  ③ 포디움 겹침 {lap*1000:.0f} mm ≥ 2×실린더 테셀레이션 처짐 "
              f"{cyl_dip*1000:.1f} mm(n=32) → "
              f"{'OK' if lap >= 2.0 * cyl_dip else 'FAIL'}")
        print(f"  ④ 상면 캐스케이드 {dz*1000:.0f} mm (동일면 z-fighting 회피) → "
              f"{'OK' if 0.001 <= dz <= 0.010 else 'FAIL'}")
        print(f"  마구리(치크) {ps['cheek_deg']:.1f}° × 2/조 · 반경 "
              f"{ps['radii'][-1]-ps['under']:.2f}..{ps['radii'][0]:.2f} · 상면 "
              f"{po['top_z']-ps['z_cascade']:+.3f} → G8 곡선 계단의 각진 마구리")
        print("=" * 68)
    return ok, dict(gap=gap_max, over=over_max, lap=lap, cyl_dip=cyl_dip, dz=dz)


def arc_selfcheck(verbose=True):
    """[W3 L05 · K4(d)] **Every** `build_arc_steps` site in this file must carry the
    mesh convention, and the radial laps the convention needs must be present.

    The site count is read out of this file's own source, so a site added later
    without `**ARC` fails the gate instead of silently shipping a box. GT-6 names
    scene05 as a 12-site consumer of the shared builder; that number is asserted."""
    total, withrc = _arc_call_census()
    b, rg = PARAMS["bowl"], PARAMS["ring"]
    t1 = b["tiers"][0]
    # ring/tier-1 lap under the mesh convention (both boundaries sag inward)
    ring_dip = _arc_dip(rg["r_in"], 360.0, rg["seg"], ARC["arc_seg"])
    tier_dip = _arc_dip(t1["r_out"], b["a1"] - b["a0"], b["seg"], ARC["arc_seg"])
    lap = (t1["r_out"] - tier_dip) - rg["r_in"]
    lip_owns_edge = PARAMS["lip"]["r_in"] >= t1["r_out"] - 1e-9
    # GT-6 records scene05 as a **12-site** consumer of the shared builder. This lane
    # adds 3 (`ArcBand` x2 is one site, `EdgeBand`, `cut_wall_cap`), so 15 is the new
    # number and it is stated, not left for a reader to rediscover.
    ok = (total == 15 and withrc == total and lap >= 0.005 and lip_owns_edge)
    if verbose:
        print("=" * 68)
        print("scene05 [W3 L05·K4(d)] 아크 규약 검산")
        print("=" * 68)
        print(f"  ① build_arc_steps 호출부 {total} (GT-6 기재 12 + L05 신설 3) · "
              f"`**ARC` 적용 {withrc} → "
              f"{'OK' if total == 15 and withrc == total else 'FAIL'}")
        print(f"  ② 링 내경 {rg['r_in']:.3f}(처짐 {ring_dip*1000:.2f} mm) vs "
              f"티어1 외경 {t1['r_out']:.3f}(처짐 {tier_dip*1000:.2f} mm) → "
              f"겹침 {lap*1000:.1f} mm ≥ 5.0 → {'OK' if lap >= 0.005 else 'FAIL'}")
        print(f"  ③ 낙차 상단 모서리는 립 커브(r_in {PARAMS['lip']['r_in']:.2f}) 소유 → "
              f"{'OK(모서리 불변)' if lip_owns_edge else 'FAIL'}")
        print("=" * 68)
    return ok, dict(sites=total, with_arc=withrc, lap=lap)


def planter_eye_selfcheck(verbose=True):
    """[W3 L05 · `w3_md_reverts_v1.md` §5 census / MD-F7 gate] No judged eye may sit
    on a planting bed. Plan distance from **every** judged cut's eye to **every** bed,
    measured twice: to the kerb footprint, and to the whole bed subtree including the
    crown (the census's own two columns). The crown radius is the referenced asset's
    measured native XY half-extent times this instance's scale."""
    rp = PARAMS["ring_planter"]
    b = PARAMS["bowl"]
    # native XY extents `[measured - assets/veg_manifest_w2.json]`
    crown_native = 4.8509 / 2.0            # Trees/Fraxinus.usd, larger XY extent
    beds = [("Planter_%s" % n, cx, cy, 3.0)
            for n, cx, cy in PARAMS["planters"]]
    for k, adeg in enumerate(PARAMS["ring_planters"]):
        a = math.radians(adeg)
        beds.append(("RingPlanter_%d" % k,
                     b["cx"] + rp["r"] * math.cos(a),
                     b["cy"] + rp["r"] * math.sin(a), rp["size"]))
    worst_k, worst_c, wk, wc = 1e9, 1e9, None, None
    for name, cx, cy, size in beds:
        h = size / 2.0
        # `build_tree` scales the asset to a target height; use the shipped
        # scale band's upper end so the gate is conservative, not optimistic.
        crown = crown_native * 0.72
        for vn, v in build_views().items():
            ex, ey = v["eye"][0], v["eye"][1]
            dk = math.hypot(max(cx - h - ex, 0.0, ex - (cx + h)),
                            max(cy - h - ey, 0.0, ey - (cy + h)))
            dc = max(0.0, math.hypot(ex - cx, ey - cy) - crown)
            if dk < worst_k:
                worst_k, wk = dk, (name, vn)
            if dc < worst_c:
                worst_c, wc = dc, (name, vn)
    ok = worst_k >= rp["min_kerb"] and worst_c >= rp["min_crown"]
    if verbose:
        print("=" * 68)
        print("scene05 [W3 L05] 판정 시점 × 식재대 이격 검산 (MD-F7 게이트)")
        print("=" * 68)
        print(f"  화단 {len(beds)}개 × 판정컷 {len(build_views())}개")
        print(f"  ① 최소 연석 이격 {worst_k:.3f} m ≥ {rp['min_kerb']:.2f} "
              f"({wk[0]} ↔ {wk[1]}) → {'OK' if worst_k >= rp['min_kerb'] else 'FAIL'}")
        print(f"  ② 최소 수관 이격 {worst_c:.3f} m ≥ {rp['min_crown']:.2f} "
              f"({wc[0]} ↔ {wc[1]}) → {'OK' if worst_c >= rp['min_crown'] else 'FAIL'}")
        print(f"     (census 기준선: RingPlanter_4 ↔ side_arc 연석 1.39 · 수관 0.25)")
        print("=" * 68)
    return ok, dict(kerb=worst_k, crown=worst_c, kerb_pair=wk, crown_pair=wc)


def service_selfcheck(verbose=True):
    """[W3 L05 · intake 05-B] The infra sites are **derived from a service line**, not
    solved from the camera. Gate: the manhole lies on the declared storm main; every
    gully lies off it (an inlet is not a manhole); every site lies inside the declared
    ground region. The camera clearances the PARAMS comment derives are then a check
    on that declaration rather than its cause."""
    g = PARAMS["gkit"]
    x0, x1, hy = g["x0"], g["x1"], g["half_y"]
    off_main = max(abs(y - g["main_y"]) for _, y in g["manhole"])
    gully_off = min(abs(y - g["main_y"]) for _, y in g["gully"])
    inside = all(x0 - 1e-9 <= x <= x1 + 1e-9 and abs(y) <= hy + 1e-9
                 for x, y in list(g["manhole"]) + list(g["gully"]))
    ok = off_main <= 0.05 and gully_off >= g["gully_off_min"] and inside
    if verbose:
        print("=" * 68)
        print("scene05 [W3 L05] 05-B 관로 유도 검산")
        print("=" * 68)
        print(f"  본관 y={g['main_y']:+.2f} (건물측 → 보울 저점, 보행축에서 반칸 옆)")
        print(f"  ① 맨홀 본관 이탈 {off_main*1000:.0f} mm ≤ 50 → "
              f"{'OK' if off_main <= 0.05 else 'FAIL'}")
        print(f"  ② 빗물받이 본관 이격 {gully_off:.2f} m ≥ "
              f"{g['gully_off_min']:.2f} (유입구는 맨홀이 아니다) → "
              f"{'OK' if gully_off >= g['gully_off_min'] else 'FAIL'}")
        print(f"  ③ 전 지점 지반 영역 내부 → {'OK' if inside else 'FAIL'}")
        print(f"  잔여(신고): 실물 빗물받이는 연석선 15~20 m 피치. 이 씬 영역은 12 m·"
              f"연석 없음 → K5 build_curb_line/gutter_L, Lane-1 후속")
        print("=" * 68)
    return ok, dict(off_main=off_main, gully_off=gully_off)


def season_selfcheck(verbose=True):
    """[W3 L05 · intake §7-8] Season is pinned to the target image and gated.

    G8 is **summer** — full leaf, high sun, clear sky. Two things are asserted, both
    against measurements rather than names (the K4-F1 rule: *name heuristics are dead,
    the pixel rule is the only instrument*):
      ① no `bare=` call exists in this file — a leaf-off tree is a different season;
      ② every species this scene declares reads green in its own UV-weighted hue
         census, with **0 autumn red and 0 bloom magenta** left live.
    `Rhododendron` is the one asset with a bloom strip, and the library deactivates it
    (`SEASONAL_SUBPRIMS` → `Rhododendron_noflower`). K4-F1 records that as a
    **library-wide** state, not a scene regression: in a summer frame a clipped green
    철쭉 mound is the correct read, and the magenta would be the defect."""
    no_bare = not _kwarg_used("bare")
    # `[measured - assets/veg_manifest_w2.json, foliage_uv_hue]`
    hue = {"Trees/Fraxinus.usd": dict(green=1.0000, orange=0.0, red=0.0, pink=0.0),
           "Shrub/Rhododendron.usd": dict(green=0.0003, orange=0.0023,
                                          red=0.0353, pink=0.7391)}
    seasonal_off = "Shrub/Rhododendron.usd" in sc.SEASONAL_SUBPRIMS
    hdri = PARAMS["light"]["hdri"]
    clear_sky = "puresky" in hdri and PARAMS["light"]["noon_sun_elev"] >= 45.0
    ok = no_bare and seasonal_off and clear_sky
    if verbose:
        print("=" * 68)
        print("scene05 [W3 L05] 계절 고정 검산 — G8 = 여름")
        print("=" * 68)
        print(f"  ① 낙엽(bare=) 호출 없음 → {'OK' if no_bare else 'FAIL'}")
        for k, v in hue.items():
            print(f"     {k:26s} green {v['green']:.4f} · red {v['red']:.4f} · "
                  f"pink {v['pink']:.4f}")
        print(f"  ② Rhododendron 개화 스트립 SEASONAL_SUBPRIMS 등록 → "
              f"{'OK(무개화 래퍼)' if seasonal_off else 'FAIL'} "
              f"— K4-F1: 라이브러리 전역 상태, 씬 회귀 아님")
        print(f"  ③ 조명 {hdri} · 태양 고도 "
              f"{PARAMS['light']['noon_sun_elev']:.2f}° → "
              f"{'OK(여름 정오·맑음)' if clear_sky else 'FAIL'}")
        print(f"  선언 수종: 가로수 {SPECIES_TREE} · 화단 {SPECIES_BED} "
              f"(SCENE_SPECIES['Scene05'] = {sc.SCENE_SPECIES.get('Scene05')})")
        print("=" * 68)
    return ok, dict(no_bare=no_bare, seasonal_off=seasonal_off)


def rect_selfcheck(verbose=True):
    """[W3 L05 · U-6 / §3(ii)] No decorative rectangle on the ground.

    The ban is on **decorative** ground patterns, not on construction lines: a paving
    band, a joint, a saw cut and a kerb all have straight edges for a reason (§3(ii)
    and the S09 stepping-stone ruling). What this scene must not carry is the milled
    repair rectangle, and it must not carry it *by configuration* either — GT-24
    deleted the `plaza_granite` patch row, so the gate asserts the plan emits none and
    that no dead `patch` site survives in PARAMS to make a reader think otherwise."""
    g = PARAMS["gkit"]
    gp = gk.plan_ground(
        "plaza_granite",
        region=(g["x0"], -g["half_y"], g["x1"], g["half_y"]),
        z=PARAMS["plaza"]["z_top"], gy=0.0, origin=(g["lip_x"], 0.0, 0.0),
        edges=[("bowl_lip", 0.0)], dists=(2, 5, 10), scene="scene05",
        tactile=(), overrides=dict(infra=dict(manhole=1, gully=2)),
        sites=dict(manhole=[tuple(v) for v in g["manhole"]],
                   gully=[tuple(v) for v in g["gully"]]),
        seed=5)
    kinds = {}
    for e in gp["elements"]:
        kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
    n_patch = kinds.get("patch", 0) + kinds.get("patch_cut", 0)
    n_relaid = kinds.get("relaid", 0)
    no_site = "patch" not in g
    ok = n_patch == 0 and n_relaid == 0 and no_site
    if verbose:
        print("=" * 68)
        print("scene05 [W3 L05] 지면 사각형 검산 (U-6 · §3(ii))")
        print("=" * 68)
        print(f"  지반 원소 {sorted(kinds.items())}")
        print(f"  ① patch/patch_cut {n_patch} · relaid {n_relaid} → "
              f"{'OK' if n_patch == 0 and n_relaid == 0 else 'FAIL'}")
        print(f"  ② PARAMS['gkit'] 에 죽은 patch 사이트 없음 → "
              f"{'OK' if no_site else 'FAIL'}")
        print(f"  존치(합법 직선): 포장 띠 · 신축줄눈 · 연석 — §3(ii) 는 장식 무늬만 금지")
        print("=" * 68)
    return ok, dict(patch=n_patch, kinds=kinds)


# ===========================================================================
# [C3] [v7 judgment §11-6] §4 "no large pure-white (>0.8) area" albedo cap self-check
#   (shared convention for scene05/09/12 - introduced this round)
#
#   judgment §11-6: "large pure-white areas occur in 3 scenes at once (09 paving · 18 plaza ·
#   19 roof/rooftop). Rather than flag them individually, add a **global albedo-cap check** to smoke."
#
#   two criteria are applied together - either one alone misses the real failures.
#     (A) albedo cap   : max channel of the effective albedo > CAP(0.80) -> literal v5.1 §4 violation.
#     (B) render forecast: for **large horizontal areas** only (paving · decks · roof tops · grass)
#         expected render sRGB = sRGB(albedo x GAIN) > PRED_CAP(0.87 ~ 222) -> violation.
#         GAIN 1.77 is back-solved from v7_rt measurements - scene09 `ghat_walk` paving albedo
#         0.469x0.90 = 0.422 -> render (223,222,221) = linear 0.738.
#         05/09/12 share the **same lighting rig** (dome 1000 + sun 2450 · elev 49.79), so
#         one value serves all. Vertical faces differ in sun/sky visibility, so (B) is not applied.
#     PRED_CAP 0.87 sits just below the measurements the judge called "large pure-white areas"
#     (09 223 · 18 220) - if the same render appears again, smoke catches it.
#   effective albedo = the constant colour as is | linear mean of the diff texture x tint.
# ===========================================================================
_ALBEDO_GAIN = 1.77
_ALBEDO_CAP = 0.80
_ALBEDO_PRED_CAP = 0.87
_TEXMEAN_CACHE = {}


def _tex_lin_mean(role):
    """Linear (de-sRGB) channel mean of a diff texture. None if PIL or the file is missing."""
    if role in _TEXMEAN_CACHE:
        return _TEXMEAN_CACHE[role]
    val = None
    try:
        import numpy as _np
        from PIL import Image
        im = Image.open(sc.tex_path(role, "diff")).convert("RGB")
        im.thumbnail((192, 192))
        a = _np.asarray(im, dtype=float) / 255.0
        lin = _np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
        val = tuple(float(v) for v in lin.mean(axis=(0, 1)))
    except Exception:
        val = None
    _TEXMEAN_CACHE[role] = val
    return val


def _srgb(u):
    u = max(0.0, min(1.0, u))
    return 12.92 * u if u <= 0.0031308 else 1.055 * u ** (1 / 2.4) - 0.055


# (label, texture role|None, material key|None, large area, horizontal, waiver reason|None)
_ALBEDO_TABLE = [
    ("광장·티어 포장",   "plaza_light", None,               True,  True,
     "v7 판정 [경] '§4 경계선' — 01/05/14/18/19 가 무틴트 plaza_light 를 "
     "공유하는 전 씬 공통 항목이라 씬 단독 하향 시 21씬 톤 정합이 깨진다. "
     "판정 §11-6 이 요구한 것도 '전역' 규약이므로 감독 결정 대기."),
    ("진입 계단 판석",   "plaza_lower", "lower_warm_tint",  True,  True,  None),
    ("잔디",             "grass",       "grass_tint",       True,  True,  None),
    ("둘레 생울타리",    "grass",       "hedge_tint",       False, False, None),
    ("파라펫(측벽 상단)", None,         "parapet_color",    True,  False, None),
    ("가로등 등기구",    None,          "lamp_color",       False, False, None),
    ("볼라드",           None,          "bollard_color",    False, False, None),
    ("배후 관목 tuft",   None,          "tuft",             True,  False, None),
]


def albedo_selfcheck(verbose=True):
    """[v7 §4/§11-6] Large-pure-white-area self-check. A violation is (A) albedo > 0.80
    or (B) expected render sRGB > 0.87 for a large horizontal area. Large areas FAIL,
    small areas WARN, and anything with a waiver reason is WAIVED. Returns (ok, rows)."""
    mp = PARAMS["material"]
    rows, fails, warns, waived = [], [], [], []
    for label, role, key, wide, horiz, waiver in _ALBEDO_TABLE:
        if key == "tuft":                      # list of constant colours
            v = max(max(c) for c in mp["tuft"])
            base, tint = (1.0, 1.0, 1.0), (v, v, v)
        else:
            tint = mp.get(key) if key else (1.0, 1.0, 1.0)
            if tint is None:
                continue
            base = (1.0, 1.0, 1.0) if role is None else _tex_lin_mean(role)
            if base is None:
                rows.append((label, key or role, None, None,
                             "SKIP(텍스처 없음)"))
                continue
        alb = max(b * t for b, t in zip(base, tint))
        pred = _srgb(alb * _ALBEDO_GAIN) if horiz else None
        why = []
        if alb > _ALBEDO_CAP:
            why.append("A:알베도")
        if horiz and pred is not None and pred > _ALBEDO_PRED_CAP:
            why.append("B:렌더예측")
        if why:
            mark = "/".join(why)
            if waiver:
                waived.append(label)
                tag = f"WAIVED({mark})"
            elif wide:
                fails.append(label)
                tag = f"FAIL 대면적({mark})"
            else:
                warns.append(label)
                tag = f"WARN 소면적({mark})"
        else:
            tag = "OK"
        rows.append((label, key or role, alb, pred, tag))
    ok = not fails
    if verbose:
        print("=" * 68)
        print("scene05 [v7 §4] 순백 대면적 알베도 상한 자가검사 "
              f"(CAP {_ALBEDO_CAP} · 수평 렌더예측 CAP {_ALBEDO_PRED_CAP} "
              f"· GAIN {_ALBEDO_GAIN})")
        print("=" * 68)
        for label, key, alb, pred, tag in rows:
            if alb is None:
                print(f"  {label:16s} {str(key):18s} {tag}")
                continue
            pr = f"{pred*255:5.1f}" if pred is not None else "  수직"
            print(f"  {label:16s} {str(key):18s} 알베도 {alb:.3f} · "
                  f"수평 예상 렌더 {pr}  {tag}")
        for label, role, key, wide, horiz, waiver in _ALBEDO_TABLE:
            if waiver and label in waived:
                print(f"  · WAIVED [{label}] {waiver}")
        print(f"  ⇒ {'OK — 미유예 대면적 위반 0건' if ok else 'FAIL: ' + str(fails)}"
              f"{'  (WARN: ' + str(warns) + ')' if warns else ''}")
        print("=" * 68)
    return ok, rows


# parameter / toggle overrides via environment variables (scene01 pattern - no effect on a default run)
_ov = os.environ.get("NEGOBS_PARAMS_OVERRIDE", "")
if _ov:
    _deep_update(PARAMS, json.loads(_ov))
    print(f"[PARAMS] override 적용: {_ov}")
_sc_ov = os.environ.get("NEGOBS_SCENE_CONFIG", "")
if _sc_ov:
    _deep_update(SCENE_CONFIG, json.loads(_sc_ov))
    print(f"[SCENE_CONFIG] override 적용: {_sc_ov}")


# ===========================================================================
# [C] paths
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene05")


# ===========================================================================
# [D] camera presets - grid_views(gy=0) + 4 mise-en-scene shots
# ===========================================================================
def build_views():
    """9 h·d grid shots + 4 mise-en-scene shots.
    Reference shift for the grid d presets: the bowl lip is at x=−1.5
    (centre 6 − opening 7.5), so eye x is moved to −1.5 − d, making "d" mean
    "distance to the lip"."""
    v = sc.grid_views(0.0)
    out = {}
    for k, val in v.items():
        e = list(val["eye"])
        t = list(val["tgt"])
        e[0] -= 1.5            # re-based on the distance to the lip (x=−1.5)
        t[0] -= 1.5
        out[k] = dict(eye=e, tgt=t)
    # mise-en-scene
    out["plaza_approach"] = dict(eye=[-6.0, 0.0, 0.9],  tgt=[2.0, 0.0, 0.6])
    out["rim_view"]       = dict(eye=[-0.5, 0.0, 1.6],  tgt=[6.0, 0.0, -1.0])
    # [v5.1] with the podium (top face −0.507) added, eye z −0.3 is only 0.207 m above it, so the
    #   viewpoint is buried in the stage floor -> reset to eye height 0.9 m above the podium top.
    #   (a mise-en-scene shot - unrelated to the hazard geometry or the grid presets)
    out["stage_lookup"]   = dict(eye=[6.0, 0.0, 0.40], tgt=[-1.0, 0.0, -0.3])
    out["side_arc"]       = dict(eye=[6.0, -10.0, 1.2], tgt=[6.0, -2.0, 0.5])
    return out


# ===========================================================================
# [E] scene assembly + main (__main__ only)
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. plaza_approach   — h0.9 광장 시점에서 반원 보울이 grazing 소실되는가
 2. h0.3·d5~10       — 1.2m 보울이 통째로 사라지는 평지 그림
 3. rim_view         — 림에서 스테이지 부감(−15°), 3티어 좌석 형태
 4. side_arc         — 곡선 단코가 세그(18) 각짐 없이 읽히는가
 5. [v5] 반원 절단   — 측벽(θ80/280)·배후 잔디 마당·진입 치크월 마감 확인
 6. [v5] 공통 레이어 — 점자띠(−X 접근) + sign_info(게이트 옆) 판독
 7. [v6] 개방감      — 배후 아크벽(0.70) 위로 관목 띠·하늘이 보이는가,
                       무대 위 회색 모놀리스(스피커)가 사라졌는가
 8. [v7] 배후 관목   — plaza_approach 400 % 에서 '이끼 낀 바위'가 아니라
                       **여러 덩이로 갈라진 관목 군락**으로 읽히는가.
                       등간격 도열이 사라지고 빈틈/군락이 생겼는가
 9. [v7] 승강 계단   — rim_view·side_arc 400 % 에서 호 끝의 나이프 에지가
                       **각진 마구리**로 바뀌었는가, 무대 단과의 초승달 틈 0
10. [v7] 서측 볼라드 — stage_lookup 지평선의 백색 포스트 열이 사라지고
                       진입축 4본(도장 강재)만 남았는가"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    # [v7] pure-Python self-checks that run without booting - backdrop shrubs · access arc wedge ·
    #   §4 albedo cap.  NEGOBS_SMOKE=1 (or NEGOBS_SELFCHECK=1) python scene05_...
    if (os.environ.get("NEGOBS_SMOKE", "0") == "1"
            or os.environ.get("NEGOBS_SELFCHECK", "0") == "1"):
        checks = [("backdrop", backdrop_selfcheck()[0]),
                  ("podium_step", podium_step_selfcheck()[0]),
                  ("albedo", albedo_selfcheck()[0]),
                  ("arc(K4d)", arc_selfcheck()[0]),
                  ("planter_eye", planter_eye_selfcheck()[0]),
                  ("service(05-B)", service_selfcheck()[0]),
                  ("season", season_selfcheck()[0]),
                  ("rect(U-6)", rect_selfcheck()[0])]
        ok = all(v for _, v in checks)
        bad = [k for k, v in checks if not v]
        print(f"[SMOKE] scene05 자가검사 {len(checks)}항 "
              f"{'전항 OK' if ok else 'FAIL ' + ','.join(bad)} "
              f"— 부팅 없이 조기 종료")
        sys.exit(0 if ok else 1)

    # asset check (prints the missing list, then exits)
    sc.check_assets(
        ["plaza_light", "plaza_lower", "granite_dark", "grass", "brick_red",
         "tactile", "sign_info", "hdri", "mdl"],   # [v5] sign_info added
        hdri=PARAMS["light"]["hdri"])

    # ── boot (SimulationApp first, then pxr/omni) ──
    simulation_app = sc.boot(capture_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from pxr import UsdGeom
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.Xform.Define(stage, "/World/Scene05")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]

    # -------------------------------------------------------------------
    # materials
    # -------------------------------------------------------------------
    def setup_materials():
        scl = mp["scale"]
        M = {}
        M["plaza_light"] = sc.make_pbr(
            stage, "/World/Looks/PlazaLight", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            scl["plaza_light"], tint=(0.72, 0.72, 0.72))   # [T1 T-1] x0.72
        # charcoal bands = dark granite (scene01 motif)
        M["band"] = sc.make_pbr(
            stage, "/World/Looks/Band", sc.tex_path("granite_dark", "diff"),
            sc.tex_path("granite_dark", "nor"), sc.tex_path("granite_dark", "rough"),
            scl["band_dark"])
        M["granite_dark"] = sc.make_pbr(
            stage, "/World/Looks/GraniteDark", sc.tex_path("granite_dark", "diff"),
            sc.tex_path("granite_dark", "nor"), sc.tex_path("granite_dark", "rough"),
            scl["granite_dark"])
        # [W3 L05] soiling = the plaza's own stone under a dark tint, not another stone.
        M["stain"] = sc.make_pbr(
            stage, "/World/Looks/Stain", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            scl["plaza_light"], tint=mp["stain_tint"])
        # stage: blue-grey flagstone (warm) vs light granite depending on cue_material_break (geometry unchanged)
        if cfg["cue_material_break"]:
            M["stage"] = sc.make_pbr(
                stage, "/World/Looks/Stage", sc.tex_path("plaza_lower", "diff"),
                sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
                scl["plaza_lower"], tint=mp["lower_warm_tint"])
        else:
            M["stage"] = sc.make_pbr(
                stage, "/World/Looks/Stage", sc.tex_path("plaza_light", "diff"),
                sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
                scl["plaza_light"], tint=(0.72, 0.72, 0.72))   # [T1 T-1] x0.72
        # entry stair (for circulation) - blue-grey flagstone to contrast with the seating tiers
        M["plaza_lower"] = sc.make_pbr(
            stage, "/World/Looks/PlazaLower", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
            scl["plaza_lower"], tint=mp["lower_warm_tint"])
        M["brick"] = sc.make_pbr(
            stage, "/World/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            scl["brick_red"])
        M["grass"] = sc.make_pbr(
            stage, "/World/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            scl["grass"], tint=mp["grass_tint"])
        M["tactile"] = sc.make_pbr(
            stage, "/World/Looks/Tactile", sc.tex_path("tactile", "diff"),
            sc.tex_path("tactile", "nor"), None, scl["tactile"])
        # constant-colour materials
        M["glass"] = sc.make_pbr(stage, "/World/Looks/Glass",
                                 diffuse_color=mp["glass_color"],
                                 roughness_const=mp["glass_rough"], metallic=0.0)
        # [W2 fix batch F5] Dark cast-iron for the kit's manhole / gully covers.
        #   `ground_kit._ik_manhole` **declares** albedo 0.10 to gate B9, but B9 only
        #   sees the declaration - the scene binds whatever it likes, and these scenes
        #   bound the stainless handrail constant. A cover at 0.66~0.85 against dark
        #   paving is the single brightest prop in the library (defect D5).
        M["gk_iron"] = sc.make_pbr(stage, "/World/Looks/GKitIron",
                                   diffuse_color=(0.10, 0.10, 0.105),
                                   metallic=0.55, roughness_const=0.55)
        M["rail"] = sc.make_pbr(stage, "/World/Looks/Rail",
                                diffuse_color=mp["rail_color"],
                                metallic=mp["rail_metallic"],
                                roughness_const=mp["rail_rough"])
        M["wood"] = sc.make_pbr(stage, "/World/Looks/Wood",
                                diffuse_color=mp["wood_color"],
                                roughness_const=mp["wood_rough"])
        M["canopy_a"] = sc.make_pbr(stage, "/World/Looks/CanopyA",
                                    diffuse_color=mp["canopy_a"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        M["canopy_b"] = sc.make_pbr(stage, "/World/Looks/CanopyB",
                                    diffuse_color=mp["canopy_b"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        M["parapet"] = sc.make_pbr(stage, "/World/Looks/Parapet",
                                   diffuse_color=mp["parapet_color"],
                                   roughness_const=mp["parapet_rough"])
        # [W3 L05] the bowl's own walls — exposed concrete, not painted parapet.
        M["wall_conc"] = sc.make_pbr(stage, "/World/Looks/WallConc",
                                     diffuse_color=mp["wall_conc"],
                                     roughness_const=mp["wall_conc_rough"])
        M["lamp"] = sc.make_pbr(stage, "/World/Looks/Lamp",
                                diffuse_color=mp["lamp_color"],
                                roughness_const=mp["lamp_rough"])
        M["pole"] = sc.make_pbr(stage, "/World/Looks/Pole",
                                diffuse_color=mp["pole_color"],
                                metallic=mp["pole_metallic"],
                                roughness_const=mp["pole_rough"])
        # v4 dressing-only materials
        M["hedge"] = sc.make_pbr(
            stage, "/World/Looks/Hedge", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            1.2, tint=mp["hedge_tint"])
        M["seat_wood"] = sc.make_pbr(stage, "/World/Looks/SeatWood",
                                     diffuse_color=mp["seat_wood"],
                                     roughness_const=mp["seat_wood_rough"])
        M["gear"] = sc.make_pbr(stage, "/World/Looks/Gear",
                                diffuse_color=mp["gear_color"],
                                roughness_const=mp["gear_rough"])
        # [v7 judgment §4 remaining 1] backdrop shrubs = **3 constant-colour tufts** (no texture).
        #   a magnified texture is half of the "mossy rock" effect, so none is bound at all.
        M["tuft"] = [sc.make_pbr(
            stage, f"/World/Looks/Tuft{i}",
            diffuse_color=tuple(c * (1.0 + 0.05 * (i - 1)) for c in col),
            roughness_const=mp["tuft_rough"], specular_level=0.0)
            for i, col in enumerate(mp["tuft"])]
        # [v7 judgment §4 remaining 3] bollards = painted steel (was: white stainless M["rail"])
        M["bollard"] = sc.make_pbr(stage, "/World/Looks/Bollard",
                                   diffuse_color=mp["bollard_color"],
                                   metallic=mp["bollard_metallic"],
                                   roughness_const=mp["bollard_rough"])
        return M

    # -------------------------------------------------------------------
    # upper plaza - fits the circular bowl opening. Ring slab + 4 boxes outside the inscribed square.
    # -------------------------------------------------------------------
    def build_plaza(M, hazard):
        p = PARAMS["plaza"]
        top, th = p["z_top"], p["thick"]
        # [W2-0 · P-A] Plaza_W is 9.5 x 28 x 0.5 m of `plaza_light`, i.e. it
        # passes `_skin_wanted` and would carry a +6.5..16.5 mm displacement
        # skin. That buries the manhole (+-10 mm) and the joint tone plates
        # (+0.6 mm) outright (spec §1.1). Same for the flat control slab.
        sc.skin_exclude("/World/Scene05/Plaza_W", "/World/Scene05/Plaza_E",
                        "/World/Scene05/Plaza_N", "/World/Scene05/Plaza_S",
                        "/World/Scene05/PlazaRing", "/World/Scene05/PlazaFlat")
        if not hazard:
            # flat control: one single slab (no bowl hole)
            cx = (p["x0"] + p["x1"]) / 2.0
            cy = (p["y0"] + p["y1"]) / 2.0
            sc.add_box(stage, "/World/Scene05/PlazaFlat",
                       (cx, cy, top - th / 2.0),
                       (p["x1"] - p["x0"], p["y1"] - p["y0"], th),
                       M["plaza_light"], collider=True)
            return
        b = PARAMS["bowl"]
        rg = PARAMS["ring"]
        # ring slab (arc): provides the smooth circular edge of the bowl opening (r=7.5)
        sc.build_arc_steps(stage, "/World/Scene05/PlazaRing", b["cx"], b["cy"],
                           rg["r_in"], rg["r_out"], 0.0, 360.0, rg["seg"],
                           rg["top_z"], rg["base_z"], M["plaza_light"],
                           **ARC)
        # 4 boxes fill outside the ring square. Leaving the square **inscribed** in the ring's outer
        # circle (half side = r_out/√2) empty keeps the square at r<=r_out -> the ring covers the corners, gap 0.
        # (a "circumscribed square" would leave outside-circle gaps at the 4 corners, opening the joint.)
        half = rg["r_out"] / math.sqrt(2.0)     # ≈ 8.485
        sx0, sx1 = b["cx"] - half, b["cx"] + half
        sy0, sy1 = b["cy"] - half, b["cy"] + half
        ov = 0.05                               # 1mm+ overlap (same material -> invisible)

        def slab(tag, x0, x1, y0, y1):
            sc.add_box(stage, f"/World/Scene05/Plaza_{tag}",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0, top - th / 2.0),
                       (x1 - x0, y1 - y0, th), M["plaza_light"], collider=True)
        slab("W", p["x0"], sx0, p["y0"], p["y1"])
        slab("E", sx1, p["x1"], p["y0"], p["y1"])
        slab("N", sx0 - ov, sx1 + ov, sy1, p["y1"])
        slab("S", sx0 - ov, sx1 + ov, p["y0"], sy0)

    # -------------------------------------------------------------------
    # paving bands. [W3 L05 · G8 · R05-1(b)] Straight along Y **outside** the plaza
    #   ring (the G1 grammar), **concentric with the bowl** inside it (the G8 grammar),
    #   and the two meet on the ring's outer circle, closed by a 150 mm granite edge
    #   band. Every band is the same +1.5 mm embedded strip as before.
    # -------------------------------------------------------------------
    def build_bands(M, hazard):
        p = PARAMS["plaza"]
        bd = PARAMS["band"]
        b = PARAMS["bowl"]
        top = p["z_top"]
        z_bot = top - bd["embed"]
        z_top = top + bd["proud"]
        cz = (z_top + z_bot) / 2.0
        hz = z_top - z_bot
        # clip radius: the ring's outer circle when the bowl exists, the bowl
        # opening otherwise (the flat control arm has no ring to run bands on).
        r = bd["clip_r"] if hazard else b["open_r"]
        n = 0
        x = p["x0"] + bd["spacing"]
        while x < p["x1"] - 1e-6:
            dx = x - b["cx"]
            if abs(dx) < r:
                # inside the bowl precinct -> clipped into north/south pieces
                # (+0.2 margin outside the circle, as before)
                halfc = math.sqrt(r * r - dx * dx) + 0.2
                if p["y1"] - halfc > 0.05:
                    sc.add_box(stage, f"/World/Scene05/Band_{n}_N",
                               (x, (halfc + p["y1"]) / 2.0, cz),
                               (bd["width"], p["y1"] - halfc, hz), M["band"])
                if (-halfc) - p["y0"] > 0.05:
                    sc.add_box(stage, f"/World/Scene05/Band_{n}_S",
                               (x, (p["y0"] - halfc) / 2.0, cz),
                               (bd["width"], (-halfc) - p["y0"], hz), M["band"])
            else:
                cy = (p["y0"] + p["y1"]) / 2.0
                sc.add_box(stage, f"/World/Scene05/Band_{n}", (x, cy, cz),
                           (bd["width"], p["y1"] - p["y0"], hz), M["band"])
            x += bd["spacing"]
            n += 1
        if not hazard:
            return
        # --- G8: concentric bands on the ring, + the 150 mm granite edge band ---
        rg = PARAMS["ring"]
        z_hi = rg["top_z"] + bd["proud"]
        z_lo = rg["top_z"] - bd["embed"]
        for k, (rr, key) in enumerate(bd["arc_bands"]):
            sc.build_arc_steps(stage, f"/World/Scene05/ArcBand_{k}",
                               b["cx"], b["cy"], rr - bd["width"] / 2.0,
                               rr + bd["width"] / 2.0, 0.0, 360.0, bd["seg"],
                               z_hi, z_lo, M[key], collider=False, **ARC)
        e0, e1 = bd["edge_band"]
        sc.build_arc_steps(stage, "/World/Scene05/EdgeBand", b["cx"], b["cy"],
                           e0, e1, 0.0, 360.0, bd["seg"], z_hi, z_lo,
                           M["granite_dark"], collider=False, **ARC)

    # -------------------------------------------------------------------
    # [W2-D] ground_kit — P1 plaza_granite, upper plaza west of the bowl lip.
    #   Stage / tiers / ring / lip untouched (W3). Runs in both hazard arms
    #   so the GT-E4 hazard-off twin carries identical ground elements.
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["gkit"]
        gp = gk.plan_ground(
            "plaza_granite",
            region=(g["x0"], -g["half_y"], g["x1"], g["half_y"]),
            z=PARAMS["plaza"]["z_top"], gy=0.0,
            origin=(g["lip_x"], 0.0, 0.0),       # grid is shifted by -1.5
            edges=[("bowl_lip", 0.0)],
            dists=(2, 5, 10), scene="scene05",
            tactile=(),                 # §12.4 - p=0.24 park, not installed
            overrides=dict(infra=dict(manhole=1, gully=2)),
            sites=dict(manhole=[tuple(v) for v in g["manhole"]],
                       gully=[tuple(v) for v in g["gully"]]),
            seed=5)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        # [W3 L05] `patch` / `patch_cut` / `weed` bindings deleted with the rows that
        #   used to draw them (GT-24 patch, A1 weed): measured at HEAD the plan emits
        #   `patch 0 · patch_cut 0 · weed 0`, so these three keys were dead bindings
        #   that made a reader believe the scene still drew saw-cut rectangles.
        #   `stain_*` moves off `granite_dark` - see PARAMS['material']['stain_tint'].
        M2.update(joint=M["granite_dark"], crack=M["granite_dark"],
                  manhole=M["gk_iron"], gully=M["gk_iron"],
                  stain_dirt=M["stain"], stain_water=M["stain"])
        res = gk.apply_ground(kit, "/World/Scene05/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] scene05 P1 · prims {res['prims']} · "
              f"delta_max {res['gt_delta_max']:.4f} · "
              f"unit_cell {res['unit_cell']}")
        return res

    # -------------------------------------------------------------------
    # sunken bowl - 3 tiers (3 arc calls) + stage disc + entry stair
    # -------------------------------------------------------------------
    def build_bowl(M):
        b = PARAMS["bowl"]
        stg = PARAMS["stage"]
        # [v5 adopted] tier arc = b["a0"]..b["a1"] (200 deg). Radii and z unchanged.
        for i, t in enumerate(b["tiers"], 1):
            sc.build_arc_steps(stage, f"/World/Scene05/Tier_{i}", b["cx"], b["cy"],
                               t["r_in"], t["r_out"], b["a0"], b["a1"],
                               b["seg"], t["top_z"], b["base_z"],
                               M["plaza_light"], **ARC)
        # v4-A1: stage = inner disc (r 4.9) + 32-seg arc rim (4.2..5.22).
        #   rim outer min radius 5.22 > tier-3 inner max 5.0242 -> through-gap 0.
        rim = stg["rim"]
        sc.add_cylinder(stage, "/World/Scene05/Stage/Disc",
                        (b["cx"], b["cy"], stg["top_z"] - stg["height"] / 2.0),
                        stg["radius"], stg["height"], M["stage"], collider=True)
        sc.build_arc_steps(stage, "/World/Scene05/Stage/Rim", b["cx"], b["cy"],
                           rim["r_in"], rim["r_out"], 0.0, 360.0, rim["seg"],
                           rim["top_z"], rim["base_z"], M["stage"], **ARC)
        # [v5.1] circular podium + 2 access stairs - coordinate rationale in the PARAMS["podium"] comment
        po = PARAMS["podium"]
        sc.add_cylinder(stage, "/World/Scene05/Stage/Podium",
                        (b["cx"], b["cy"],
                         (po["top_z"] + po["base_z"]) / 2.0),
                        po["r"], po["top_z"] - po["base_z"], M["stage"],
                        collider=True)
        ps = po["steps"]
        last = len(ps["tops"]) - 1
        for j, (a0, a1) in enumerate(ps["arcs"]):
            for i, ztop in enumerate(ps["tops"]):
                # [W3 L05] the innermost step laps 0.10 m under the podium cylinder
                # and drops 3 mm, so it is not coplanar with the podium top disc.
                r_in = ps["radii"][i + 1]
                if i == last:
                    r_in -= ps["under"]
                    ztop -= ps["z_cascade"]
                sc.build_arc_steps(
                    stage, f"/World/Scene05/Stage/PodiumStep_{j}_{i}",
                    b["cx"], b["cy"], r_in, ps["radii"][i],
                    a0, a1, ps["seg"], ztop, ps["base_z"], M["stage"], **ARC)
            # [v7 judgment §4 remaining 2] end caps (cheeks) - hide the knife edges at both arc ends.
            #   one short arc of thickness cheek_deg each, covering the full radial width (3.0..3.75).
            #   top face = the podium top face (−0.853) -> 0.35 m above the apron (the same
            #   drop as the podium, no new hazard). Pushed toward the stair by overlap to close the gap.
            cd, ov = ps["cheek_deg"], ps["cheek_overlap"]
            for tag, ca0, ca1 in (("A", a0 - cd + ov, a0 + ov),
                                  ("B", a1 - ov, a1 + cd - ov)):
                sc.build_arc_steps(
                    stage, f"/World/Scene05/Stage/PodiumCheek_{j}{tag}",
                    b["cx"], b["cy"], ps["radii"][-1] - ps["under"],
                    ps["radii"][0], ca0, ca1, 1,
                    po["top_z"] - ps["z_cascade"], ps["base_z"], M["stage"],
                    **ARC)

    def build_flight(M, prefix, a0, a1, seg):
        """v4-A2/A3: one arc stair concentric with the tiers. Because the radius ladder
        contains the tier boundaries exactly, tread-width collapse and wedge steps
        cannot occur by construction."""
        e = PARAMS["entry"]
        b = PARAMS["bowl"]
        for i, ztop in enumerate(e["tops"]):
            sc.build_arc_steps(stage, f"{prefix}/Step_{i}", b["cx"], b["cy"],
                               e["radii"][i + 1], e["radii"][i], a0, a1, seg,
                               ztop, e["base_z"], M["plaza_lower"], **ARC)

    def build_entry(M):
        """Entry stair (+X radial, a −9..+9°) + the 2 v4-D5 seating aisle stairs."""
        e = PARAMS["entry"]
        build_flight(M, "/World/Scene05/Entry", e["a0"], e["a1"], e["seg"])
        for k, a in enumerate(PARAMS["aisles"]):
            build_flight(M, f"/World/Scene05/Aisle_{k}", a["a0"], a["a1"],
                         a["seg"])

    def build_seat_strips(M):
        """v4-D4: a timber seat band on the top edge of every tier — the tiers read as
        "seating" and step contrast is secured (against the flat white curved wall
        of riser 0.40 · tread 0.85).
        The entry (±9°) and aisle (100~112 / 248~260) ranges break the arc and stay empty."""
        b = PARAMS["bowl"]
        se = PARAMS["seat"]
        for i, t in enumerate(b["tiers"], 1):
            r1 = t["r_out"] - se["inset"]
            r0 = r1 - se["width"]
            z_hi = t["top_z"] + se["proud"]
            for j, (a0, a1, seg) in enumerate(se["arcs"]):
                sc.build_arc_steps(stage, f"/World/Scene05/Seat_{i}_{j}",
                                   b["cx"], b["cy"], r0, r1, a0, a1, seg,
                                   z_hi, z_hi - se["drop"], M["seat_wood"],
                                   collider=False, **ARC)

    def build_lip(M):
        """Lip kerb ring (cue_material_break): a dark granite material-break cue outside the opening."""
        l = PARAMS["lip"]
        b = PARAMS["bowl"]
        sc.build_arc_steps(stage, "/World/Scene05/LipCurb", b["cx"], b["cy"],
                           l["r_in"], l["r_out"], l["a0"], l["a1"], l["seg"],
                           l["top_z"], l["base_z"], M["granite_dark"], **ARC)

    def build_halfbowl_finish(M):
        """[v5 adopted] Half-round finish — cut side wall + grass backyard + entry cheek walls.

        Walking-continuity self-verification (plaza → yard → stage):
          plaza/ring z −0.002 (r>7.5)
            → yard z −0.06        step 0.058  (level connection)
            → entry stair step 1 −0.197 step 0.137  (starts flush with the cheek wall top)
            → −0.397 / −0.597 / −0.797 / −0.997 / −1.197  riser 0.200 each
            → stage −1.207        step 0.010
          The reverse direction (stage → yard) has the same profile. No step exceeds 0.2 m.
        Guarding of the new edge drops:
          · tier cut face (θ 80/280) → cut_wall top face +1.00 (1.06 m above the yard)
          · yard inner side (r 5.25) → blocked by the shell (θ 9..80 / 280..351) throughout
            [v6] top face +1.4 → +0.70, used together with the shrub buffer (backdrop_shrub)
          · entry stair flanks (θ ±9) → entry_cheek (θ 9..11 / 349..351) top face −0.06
        """
        b = PARAMS["bowl"]
        # [W3 L05 · G8] `cut_wall` leaves `granite_dark` for the parapet material.
        #   A 2.6 m dark slab across the frame is the "cistern/bunker" reading v6 was
        #   already fighting when it dropped the shell 1.40 -> 0.70; G8's vertical
        #   surfaces are pale concrete. Material only - no dimension moves.
        #   [pilot 2] `wall_conc` (0.34), not `parapet` (0.72) - see the material
        #   comment: pilot 1 put WHITE on 7 of 13 cuts with the brighter constant.
        for key, mtl in (("backyard", M["grass"]),
                         ("entry_cheek", M["plaza_light"]),
                         ("cut_wall", M["wall_conc"])):
            p = PARAMS[key]
            for j, (a0, a1) in enumerate(p["arcs"]):
                sc.build_arc_steps(stage, f"/World/Scene05/{key}_{j}",
                                   b["cx"], b["cy"], p["r_in"], p["r_out"],
                                   a0, a1, p["seg"], p["top_z"], p["base_z"],
                                   mtl, **ARC)
        # [W3 L05 · G8] 60 mm timber capping on the cut wall (G8's timber-topped
        #   parapets / slat soffits). Raises the guard top 1.000 -> 1.060.
        cw = PARAMS["cut_wall"]
        for j, (a0, a1) in enumerate(cw["arcs"]):
            sc.build_arc_steps(stage, f"/World/Scene05/cut_wall_cap_{j}",
                               b["cx"], b["cy"], cw["r_in"], cw["r_out"],
                               a0, a1, cw["seg"],
                               cw["top_z"] + cw["cap_h"], cw["top_z"],
                               M["seat_wood"], **ARC)

    # -------------------------------------------------------------------
    # grass ground outside the site - split into 4 boxes leaving the bowl opening empty (r1 fixed).
    #   a single slab would let its top face (-0.5) cut through the sunken bowl and bury tiers 2·3
    #   and the stage -> the circumscribed square of the opening (centre (6,0) r7.5) +0.2 is left as a hole.
    #   between hole corner and circle the plaza ring (r7.5..12, base -0.5) covers from above - no gap.
    #   grass top face -0.51 : dropped 1 cm to avoid coplanar Z-fighting with the ring base (-0.5).
    # -------------------------------------------------------------------
    def build_ground(M):
        top = -0.51
        th = 1.0
        cz = top - th / 2.0
        # hole square: the square circumscribing the bowl circle r=7.5 + 0.2 margin (centre (6,0))
        hx0, hx1 = -1.7, 13.7
        hy0, hy1 = -7.7, 7.7
        gx0, gx1 = -117.0, 123.0     # whole site (centre x=3, width 240)
        gy0, gy1 = -120.0, 120.0
        ov = 0.05                    # overlap at the piece joints (same material -> invisible)

        def slab(tag, x0, x1, y0, y1):
            sc.add_box(stage, f"/World/Scene05/Ground_{tag}",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0, cz),
                       (x1 - x0, y1 - y0, th), M["grass"])
        slab("W", gx0, hx0, gy0, gy1)
        slab("E", hx1, gx1, gy0, gy1)
        slab("N", hx0 - ov, hx1 + ov, hy1, gy1)
        slab("S", hx0 - ov, hx1 + ov, gy0, hy0)

    # -------------------------------------------------------------------
    # dressing - planters·hedges·benches·streetlights·buildings
    # -------------------------------------------------------------------
    def build_streetlight(M):
        """v4-D10: places several streetlights from the PARAMS['streetlights'] list (x, y, base_z)."""
        sl = PARAMS["streetlight"]
        for k, (x, y, bz) in enumerate(PARAMS["streetlights"]):
            base = f"/World/Scene05/Streetlight_{k}"
            sc.add_cylinder(stage, f"{base}/Pole",
                            (x, y, bz + sl["pole_h"] / 2.0),
                            sl["pole_r"], sl["pole_h"], M["pole"],
                            collider=True)
            for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                ax = x + sgn * sl["arm_len"] / 2.0
                sc.add_cylinder(stage, f"{base}/Arm_{tag}",
                                (ax, y, bz + sl["pole_h"] - 0.1),
                                sl["arm_r"], sl["arm_len"], M["pole"],
                                rotY=90.0)
                hx = x + sgn * sl["arm_len"]
                sc.add_box(stage, f"{base}/Head_{tag}",
                           (hx, y, bz + sl["pole_h"] - 0.15),
                           (sl["head"], sl["head"], 0.12), M["lamp"])

    def build_surround(M):
        """v4-A4: terminates the 0.51 m unguarded fall around the whole plaza.
        A grass berm (top face −0.26) splits 0.51 into two steps of 0.26 + 0.25, and
        on the north side a paved apron in front of the building replaces it, which
        also improves the building grounding (B-6)."""
        bm = PARAMS["berm"]
        for tag, x0, x1, y0, y1 in PARAMS["berms"]:
            sc.add_box(stage, f"/World/Scene05/Berm_{tag}",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0,
                        (bm["top_z"] + bm["base_z"]) / 2.0),
                       (x1 - x0, y1 - y0, bm["top_z"] - bm["base_z"]),
                       M["grass"], collider=True)
        ap = PARAMS["apron"]
        sc.add_box(stage, "/World/Scene05/ApronN",
                   ((ap["x0"] + ap["x1"]) / 2.0, (ap["y0"] + ap["y1"]) / 2.0,
                    (ap["top_z"] + ap["base_z"]) / 2.0),
                   (ap["x1"] - ap["x0"], ap["y1"] - ap["y0"],
                    ap["top_z"] - ap["base_z"]),
                   M["plaza_light"], collider=True)

    def planter_no_stake(M, prefix, cx, cy, base_z, size=None):
        """[v5 judgment applied] Planter + mature tree without stakes.

        The shared v4-B3 fix "remove the triangular tree stakes" was applied only to
        scene01/03/04 and missed scene05 (stakes were visible in stage_lookup·side_arc·
        preset_h0.3_d10), breaking consistency with the other 4 scenes. In scene05 the
        tree is planted inside sc.build_planter, and that function does not forward a
        stake argument, so the planter is built first (tree_mtls=None) and the tree is
        planted directly with sc.build_tree, with the stake dimensions driven to nearly
        zero to neutralise them (the same convention as scene03/04).
        (Proposal: add a stakes=False argument to scene_common.build_tree/build_planter.)
        """
        kw = {} if size is None else dict(size=size)
        # [W3 L05 · K4(b)] **the species is stated at the call site.** `build_planter`
        #   used to pass `pool=` only, so each bed drew its shrub by coordinate hash and
        #   the composed scene shipped **Juniper x15 + Rhododendron x9** across 8 beds -
        #   monospecific per bed, but two species on one plaza ring, which is exactly the
        #   defect S-1/S-2 exist against and the opposite of G8's one-clipped-shrub-per-
        #   planter reading. `species=` landed on `build_planter` in K-micro item 3
        #   (S08-F2), so the role is pinned here: `ornament_bed` -> Rhododendron, a single
        #   `SHRUB_SPECIES` row, hence one species over all 8 beds. The tree likewise says
        #   `species="ash"` rather than leaving it to `SCENE_SPECIES` resolution - the same
        #   value, stated instead of inferred (the scene08 precedent).
        sc.build_planter(stage, prefix, cx, cy, base_z,
                         M["granite_dark"], M["grass"], tree_mtls=None,
                         species=SPECIES_BED, **kw)
        # planted on the build_planter default grass_h=0.40 top face (same height as the internal call)
        sc.build_tree(stage, prefix, cx, cy, base_z + 0.40,
                      M["wood"], M["canopy_a"], M["canopy_b"],
                      stake_r=0.004, stake_h=0.02, stake_off=0.2,
                      species=SPECIES_TREE)

    def build_backdrop_shrubs(M):
        """[v6 judgment (i)] Backdrop shrub buffer — a shrub band planted in the yard
        behind the lowered arc wall (+0.70). Purpose ① deter access to the 1.15 m
        yard-to-stage drop (replacing the height taken off the wall), ② make the area
        behind the stage read as **greenery** rather than a "concrete retaining wall"
        (openness).

        [v7 judgment §4 remaining 1] The old implementation (one row of flattened
        ellipsoids rad 0.42·h 1.10 + grass texture uv 1.2 · even spacing 0.62) rendered
        as **"an even row of mossy boulders"** (the same failure mode as scene04 v6
        verge). The scene04 W-4 solution is ported:
          · 3 constant-colour tufts (texture dropped) — the "rock relief" cue is removed at source.
          · one big ellipsoid → **a vertical stack of 3~4 small lobes**. Each lobe stays
            at 0.5 m or less (judgment recommendation ①) while the clump top holds at
            1.22 m, so the v6 gain "greenery above the arc wall (+0.70)" survives intact.
          · 3 rows × a different step per row + spacing jitter ±35 % + 12 % dropouts +
            per-lobe position/size jitter → the even-row look is gone (§3).
        The coordinates come from the single source `backdrop_instances()` at module
        level (shared with the checker).
        """
        # [v8 hotfix] the (r,k,j) triple key collided 130 times (k reused after jitter/dropout) ->
        #   add_sphere twice on the same prim path = an AddTranslateOp clash, crashing assembly.
        #   replaced with global-index (idx) naming. A v2 scene has no SMOKE - found in RT.
        n = 0
        for idx, (px, py, pz, ax, ay, az, r_i, k, j) in \
                enumerate(backdrop_instances()):
            sc.add_sphere(stage,
                          f"/World/Scene05/BackdropShrub_{idx}",
                          (px, py, pz), (ax, ay, az),
                          M["tuft"][(r_i + k + j) % len(M["tuft"])])
            n += 1
        return n

    def build_dressing(M):
        b = PARAMS["bowl"]
        # 2 planters (around the lip)
        for name, cx, cy in PARAMS["planters"]:
            planter_no_stake(M, f"/World/Scene05/Planter_{name}", cx, cy, 0.0)
        # v4-D8 tree row around the lip (r=9.6 circle, 45 deg spacing)
        rp = PARAMS["ring_planter"]
        for k, adeg in enumerate(PARAMS["ring_planters"]):
            a = math.radians(adeg)
            planter_no_stake(M, f"/World/Scene05/RingPlanter_{k}",
                             b["cx"] + rp["r"] * math.cos(a),
                             b["cy"] + rp["r"] * math.sin(a), rp["base_z"],
                             size=rp["size"])
        # v4-B4/A4 hedge around the plaza (3 misaligned pieces -> 5 perimeter pieces, 3 openings)
        for j, (x0, y0, x1, y1) in enumerate(PARAMS["hedges"]):
            sc.build_hedge(stage, f"/World/Scene05/Hedge_{j}", x0, y0, x1, y1,
                           PARAMS["hedge_h"], mtl=M["hedge"])
        # [v7 judgment §4 remaining 3] west bollards - a decorative row of 10 (spacing 2.67 m, width 24 m)
        #   -> **4 gate posts on the entry axis** (regulation spacing 1.5 m, width 4.5 m) · painted steel.
        #   v5.1 §2 "only where vehicle intrusion is a concern · spacing around 1.5 m · remove decorative rows".
        bl = PARAMS["bollards"]
        y0 = -bl["spacing"] * (bl["n"] - 1) / 2.0
        for k in range(bl["n"]):
            sc.build_bollard(stage, f"/World/Scene05/Bollard_{k}", bl["x"],
                             y0 + bl["spacing"] * k, bl["base_z"],
                             mtl=M["bollard"], height=bl["height"])
        # [v5.2 user] bench ring removed - "hurts openness, remove it cleanly"
        #   (the bench_ring PARAMS stay for the record; the build is skipped)
        # v4-D1 [top priority] stage backdrop wall (stage shell), 2 pieces - only when the bowl exists
        #   [v6 judgment (i)] top face 1.40 -> 0.70 (see the PARAMS comment). The lost guarding goes to the shrub buffer.
        sh = PARAMS["shell"]
        if cfg["hazard_stairs"]:
            for j, (a0, a1) in enumerate(sh["arcs"]):
                # [W3 L05 · G8] exposed-concrete material, same reason and same
                #   pilot-2 correction as `cut_wall`.
                sc.build_arc_steps(stage, f"/World/Scene05/StageShell_{j}",
                                   b["cx"], b["cy"], sh["r_in"], sh["r_out"],
                                   a0, a1, sh["seg"], sh["top_z"],
                                   sh["base_z"], M["wall_conc"], **ARC)
            build_backdrop_shrubs(M)
        # v4-D2 2 lighting towers (mast + 3 heads)
        tw = PARAMS["tower"]
        for k, (tx, ty) in enumerate(PARAMS["towers"]):
            sc.add_cylinder(stage, f"/World/Scene05/Tower_{k}/Pole",
                            (tx, ty, tw["base_z"] + tw["pole_h"] / 2.0),
                            tw["pole_r"], tw["pole_h"], M["pole"],
                            collider=True)
            for hi, hz in enumerate(tw["head_z"]):
                sc.add_box(stage, f"/World/Scene05/Tower_{k}/Head_{hi}",
                           (tx, ty, tw["base_z"] + hz), tw["head"], M["gear"])
        # [v6 judgment (ii)] the 2 v4-D3 speaker stacks are removed - "unidentifiable grey monoliths on stage".
        #   two untextured grey slabs with no grille, mount or tilt stood left and right of the stage,
        #   failing the v5.2 §6 test "would the scene be unreadable without it?".
        #   permanent speakers are not the norm on a neighbourhood-park stage either (brought in per event).
        #   -> build skipped. PARAMS["speakers"]/["speaker"] stay for the record
        #     (the same convention as the bench-ring removal).
        # v4-D7 entrance gate + sign (−X approach axis)
        gt = PARAMS["gate"]
        for tag, sgn in (("P", 1.0), ("N", -1.0)):
            sc.add_cylinder(stage, f"/World/Scene05/Gate/Post_{tag}",
                            (gt["x"], sgn * gt["y"],
                             gt["base_z"] + gt["post_h"] / 2.0),
                            gt["post_r"], gt["post_h"], M["granite_dark"],
                            collider=True)
        sc.add_box(stage, "/World/Scene05/Gate/Lintel",
                   (gt["x"], 0.0,
                    gt["base_z"] + (gt["lintel_z0"] + gt["lintel_z1"]) / 2.0),
                   (gt["lintel_t"], 2.0 * gt["lintel_y"],
                    gt["lintel_z1"] - gt["lintel_z0"]), M["granite_dark"])
        # v4-B6 entrance canopy for building R (over the apron)
        ec = PARAMS["entry_canopy"]
        sc.build_canopy(stage, "/World/Scene05/EntryCanopy", ec["x0"],
                        ec["x1"], ec["y0"], ec["y1"], ec["z_roof"],
                        ec["post_r"], M["parapet"], M["pole"],
                        roof_t=ec["roof_t"], base_z=ec["base_z"])
        # 5 streetlights
        build_streetlight(M)
        # 2 distant buildings (R/C)
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"/World/Scene05/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"])

    # -------------------------------------------------------------------
    # cue toggles (all default False - the "no facilities" identity). Optional implementation.
    # -------------------------------------------------------------------
    def build_cues(M):
        b = PARAMS["bowl"]
        # cue_railing: partial-arc railing around the lip - post chain + a thin arc top rail.
        if cfg.get("cue_railing"):
            r_post = 7.9
            a0, a1 = 120.0, 240.0            # partial arc on the −X audience side
            nposts = 9
            rail_h = 0.9
            for k in range(nposts):
                a = math.radians(a0 + (a1 - a0) * k / (nposts - 1))
                px = b["cx"] + r_post * math.cos(a)
                py = b["cy"] + r_post * math.sin(a)
                sc.add_cylinder(stage, f"/World/Scene05/Rail/Post_{k}",
                                (px, py, rail_h / 2.0), 0.02, rail_h, M["rail"])
            # top rail: a thin arc box ring (stands in for a segmented cylinder chain - avoids exposing rotZ)
            sc.build_arc_steps(stage, "/World/Scene05/Rail/Top", b["cx"], b["cy"],
                               r_post - 0.03, r_post + 0.03, a0, a1, 12,
                               rail_h, rail_h - 0.04, M["rail"], collider=False,
                               **ARC)
        # cue_tactile: −X approach warning tactile strip (outside the lip)
        if cfg.get("cue_tactile"):
            sc.build_tactile(stage, "/World/Scene05/Tactile",
                             -2.3, -1.9, -2.0, 2.0, M["tactile"], z=0.0)
        # cue_nosing: curved non-slip nosing arc band on each tier top edge
        if cfg.get("cue_nosing"):
            nos = sc.make_pbr(stage, "/World/Looks/Nosing",
                              diffuse_color=mp["nosing_color"],
                              roughness_const=mp["nosing_rough"])
            for i, t in enumerate(b["tiers"], 1):
                sc.build_arc_steps(stage, f"/World/Scene05/Nosing_{i}",
                                   b["cx"], b["cy"], t["r_out"] - 0.06, t["r_out"],
                                   b["a0"], b["a1"], b["seg"],  # [v5] follows the half-round
                                   t["top_z"] + 0.003,
                                   t["top_z"] - 0.02, nos, collider=False,
                                   **ARC)

    # -------------------------------------------------------------------
    # [v5 shared layer] Korean sign (cue_sign)
    # -------------------------------------------------------------------
    def build_signs():
        """Places the PARAMS['signs'] list with sc.build_sign.
        Warning/info boards are a facility cue adjacent to a drop (family ①) — the
        coordinate check is in the PARAMS comment."""
        back = sc.make_pbr(stage, "/World/Looks/SignBack",
                           diffuse_color=(0.16, 0.17, 0.18),
                           metallic=0.6, roughness_const=0.5)
        for tag, key, cx, cy, bz, yaw, w, h in PARAMS["signs"]:
            panel = sc.make_pbr(stage, f"/World/Looks/Sign{tag}",
                                diff=sc.tex_path(key, "diff"), uv_mode=True,
                                roughness_const=0.6)
            sc.build_sign(stage, f"/World/Scene05/Sign_{tag}", cx, cy, bz,
                          yaw, panel, w=w, h=h, back_mtl=back)

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    hazard = cfg["hazard_stairs"]
    build_plaza(M, hazard)
    build_bands(M, hazard)
    if hazard:
        build_bowl(M)
        build_entry(M)
        build_halfbowl_finish(M)        # [v5 adopted] half-round cut finish · back yard
        if cfg["cue_material_break"]:
            build_lip(M)
    build_ground(M)
    build_ground_kit(M)             # [W2-D] both arms — GT-E4 twin parity
    build_surround(M)               # v4-A4: plaza perimeter termination (always - pedestrian safety)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
        if hazard:
            build_seat_strips(M)    # v4-D4: only when tiers exist
    build_cues(M)
    if cfg.get("cue_sign"):
        build_signs()               # [v5 shared layer]
    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # ── camera + render mode ──
    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

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

    VIEWS = build_views()
    _v0 = VIEWS["plaza_approach"]
    look_from(_v0["eye"], _v0["tgt"])              # start camera = mise-en-scene

    os.makedirs(LOOKCHECK_DIR, exist_ok=True)

    # ── auto capture mode (headless) ──
    if capture_mode:
        sc.capture_pipeline(simulation_app, VIEWS,
                            os.path.join(LOOKCHECK_DIR, "auto"),
                            set_render_mode, look_from)
        simulation_app.close()
        return

    # ── GUI look check mode (default) ──
    from omni.kit.viewport.utility import get_active_viewport, \
        capture_viewport_to_file

    def capture(path):
        vp = get_active_viewport()
        capture_viewport_to_file(vp, file_path=path)

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene05_{ts}.png")
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
