# -*- coding: utf-8 -*-
"""
scene02_underpass.py — NegObs synthetic scene 2: underpass / subway entrance (Isaac Sim 4.5)

Type    : T3 underpass (fully equipped × dark lower level)
Spec    : Docs/multi_scene_brief_v2.md §C scene02_underpass (sole spec)
Shared  : scene_common.py (verified API helpers) · scene01_campus_stairs.py (skeleton)

Hazard  : a descending pit cut into the ground-level sidewalk. From a low viewpoint
           (h0.3, far) the pit reads as completely flat ground with only the railing and
           tactile paving floating above it → the 20-step stair's 3.2 m drop is hidden at
           grazing angles. The lower level is naturally dark, occluded from the dome.
Goal     : bring up the ground sidewalk (with opening) + retaining-wall pit + 20-step stair
           + lower landing + tunnel portal in the GUI and judge from renders (render only,
           physics colliders only — no sim steps).

Run (GUI look check — default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene02_underpass.py

Auto capture mode (for headless verification):
    NEGOBS_CAPTURE=1 python scene02_underpass.py
      NEGOBS_CAPTURE_DIR  : output folder (default look_check/scene02/auto)
      NEGOBS_CAPTURE_MODE : rt | pt | both (default rt)
      NEGOBS_VIEWS        : comma-separated view-name filter (default all)

Coordinates: Z-up, m, travel axis +X, drop start edge = x=0.

===========================================================================
⚠️ What follows is a **DESIGN PROPOSAL AND IS NOT YET REFLECTED IN THE CODE**
   (2026-07-29). The session that was writing it was cut off by a usage limit.
   The coordinate check is finished, so the next session can implement it
   exactly as tabulated here. **Delete this warning block once implemented.**
===========================================================================
Geometry core (numeric check) — [v8 design proposal] statutory landing + wide mid rail
===========================================================================
Diagnosis   : Docs/reports/stair_compliance_v1.md §1 scene02 row (P0-L1 · P0-R1)
Calc tools  : stair_kit.stair_landings() / mid_rail_lines() / build_stair_landing()
              — this file **does not compute landing coordinates itself** (single source of truth).

  L1 landing  : drop 3.20 > statutory 3.00 (Fire/Evacuation Rule §15①1) → 1 landing required.
      stair_landings(3.20, 0.160, 0.320) ⇒ m = floor(3.00/0.160) = 18,
      n_flights = ceil(20/18) = 2, 20 = 10 + 10 (front-first allocation, deterministic).
      run 6.40 → **7.60** (+1.20 = landing depth, exactly the statutory minimum 1.20).
  R1 mid rail : width 3.50 > 3.00, and the exemption conditions are **AND**-ed, so it already
      fails at riser 0.160 > 0.150 → required. mid_rail_lines(−1.75, 1.75, 0.160, 0.320)
      ⇒ n_bays = ceil(3.50/3.00) = 2 → **1 line at y = 0.000** (each bay 1.75).

[Walking-continuity z ladder]  enter → descend → landing → descend → exit (every step ≤ 0.160)
  ┌ #  section            x range          top z       step / verdict
  │ 0  ground sidewalk     ≤ 0.00          +0.000      flat (opening front edge = drop 3.200)
  │ 1  flight0 step 1   0.00 … 0.32        −0.160      0.160
  │ 2  flight0 step 5   1.28 … 1.60        −0.800      0.160 × 4
  │ 3  flight0 step 10  2.88 … 3.20        −1.600      0.160 × 5   ← end of flight0
  │ 4  **landing**      3.20 … 4.40        −1.600      0.000 (flat 1.200)
  │ 5  flight1 step 1   4.40 … 4.72        −1.760      0.160       ← landing front edge
  │ 6  flight1 step 5   5.68 … 6.00        −2.400      0.160 × 4
  │ 7  flight1 step 10  7.28 … 7.60        −3.200      0.160 × 5
  │ 8  lower landing    7.60 … 8.20        −3.200      0.000 (flush)
  └ 9  tunnel floor     8.20 … 12.20       −3.200      0.000 (flush)
  * Total drop preserved: 10×0.160 + 0 + 10×0.160 = 3.200 = the old 20×0.160.
  * Discontinuity 0: flight0.z_bot = landing.z = flight1.z_top = −1.600 (stair_kit self-check (4)).
  * Downstream shift +1.20 : pit x1 7.0→8.2 · lower landing 6.4→7.6 · tunnel x0 7.0→8.2 ·
    perimeter railing x1/x_rear · grass opening gx1 7.6→8.8 · road 8.0→9.2 (kerb and lane
    markings follow) · 3 tunnel lamps · Exit sign 7.8→9.0. (the x ≤ 3.20 stretch is **completely unchanged**)

[GT change] — the landing alters the z(x) profile, so the drop/depth GT cache must be regenerated
  · drop edge count : 20 → **21** (20 nosings + **1 landing front edge**)
  · new edge        : x = 4.400, y ±1.75, top z = −1.600.
                      residual drop caught at this edge = sum of downstream flight1 = **1.600 m**
  · new flat strip  : x 3.200…4.400 × y −1.75…1.75 = 1.20 × 3.50 = **4.20 m²**,
                      local drop **0** (landing top face; labelled flat ground, not a stair face)
  · unchanged       : total drop 3.200 at the opening front edge x=0 · nosing period 0.320 · riser 0.160
                      (the period is broken exactly 1 time, only over the landing — the nosing silhouette cue survives)
  · The mid rail and handrails create no z(x,y), so **GT is unchanged** (self-occlusion only increases).

[Camera occlusion check]  (substituting the build_views coordinates directly)
  · grid gy : 0.000 → **−0.875** (centre of the south bay). Avoids the y=0 mid rail masking
    the preset axis head-on — same precedent as scene01 R2-1 (central-railing avoidance gy=−2.75).
    −0.875 is still inside the |y| ≤ 1.75 opening, so the head-on view into the pit is kept.
  · h0.3 concealment preserved : the sight line grazing the edge (x=0, z=0) meets the landing
    top face (−1.600) at x = 1.600·d/0.3 = 5.33·d → 10.7 m at d=2 > the landing's downstream
    end 4.40 → **the landing stays hidden**.
    (the landing became shallower at −1.600, but the grazing sight line still cannot reach it.)
  · h1.8/d2 sees the landing top face from x=3.56 onward (the 0.9/… judging cut — intended exposure).
  · No eye falls inside the landing AABB (x 3.20…4.40 · y ±1.75 · z −3.50…−1.600).
  · inside_looking_up : eye x 6.60 → **7.80** (+1.20, keeping 0.50 m above the lower landing),
    y 0.00 → −0.875 (avoiding the y=0 mid rail head-on). The sight line clears the landing top
    face by 0.065 m at x=4.40 → the landing does not block it.
"""

import os
import sys
import math
import json
import datetime

import scene_common as sc
import ground_kit as gk
import stair_kit as sk           # Statutory landing / mid rail (single source of truth for coordinate calculation)


# ===========================================================================
# [A] SCENE_CONFIG - scene01's 6 keys + cue_nosing (new). Toggles leave the hazard geometry unchanged
#     (hazard_stairs is the only exception: False -> fills the pit to flat ground at z=0).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False -> pit/stair/retaining wall/tunnel become flat ground at z=0 (the only geometry toggle)
    # [realism v1] Semantics narrowed: the two stair lines are now statutory
    #   **handrail** (§15(3)/(4)) - one pipe per side, no mid rail, no balusters.
    #   The stair is wall to wall, so §15(1)2 is met by "wall" and no stair
    #   guardrail is required. The pit perimeter guard is unchanged.
    #   See Docs/reports/scene15_railing_fix_v1.md §8.
    "cue_railing":        True,   # One handrail line on each side of the stair + 3-sided railing around the pit at ground level
    "cue_tactile":        False,  # [v5.2 user] Tactile paving is rare in reality - OFF by default (ablation path kept)   # Dot tactile paving: top warning strip at x=-0.3 + lower landing
    "cue_material_break": True,   # False -> stair and landing also unified to the sidewalk-block material (plaza_lower)
    "cue_nosing":         True,   # [new] Yellow anti-slip strip on every step (subway practice)
    "cue_sign":           True,   # [v5 shared layer] 1 Korean-language sign (tunnel exit marker)
    "cue_scene_dressing": True,   # Brick building, hedge, street lamps and distant vista in one go
}


# ===========================================================================
# [B] PARAMS - dimensions, materials, lighting. Merged with NEGOBS_PARAMS_OVERRIDE / NEGOBS_SCENE_CONFIG.
# ===========================================================================
PARAMS = dict(
    # --- Ground sidewalk (split into 4 boxes around the opening) ---
    walk=dict(x_w=-18.0, x_e=16.0, y_s=-8.0, y_n=8.0, z_top=0.0, thick=0.5),
    # Descending pit opening: stair width = 3.5 between the retaining-wall inner faces (y ±1.75)
    pit=dict(x0=0.0, x1=7.0, y0=-1.75, y1=1.75),

    # === [W2-D ground_kit] P3 sidewalk_block (spec §5.2 row "02 ground") ====
    # Scope for this round is the **upper sidewalk only** (Walk_W, x -12..0).
    # The pit, the stairs and the lower landing are untouched: the landing
    # redesign is W4, and the underground branch (`tunnel_under` profile) is a
    # different slab at z=-3.2 that this call deliberately does not touch.
    #
    #  * manhole 1 at (-1.20, +0.35) - spec coordinate, lands in the d2 near
    #    window (X=0.80).
    #  * gullies 2 at x=-0.95, y=+-3.60 - stair-head drainage per ruling C-1'
    #    (spec §5.0). Flush, so GT-E1' stand-off is 0 m.
    #  * gutter_L is switched OFF. Spec §5.2 puts scene02's L gutter on the
    #    kerb line at x=7.85 (the road runs across +X at x 8..13), which is
    #    behind the pit and outside every h0.3 near window; the composer would
    #    otherwise draw it along the region's own y0 edge, i.e. across the open
    #    sidewalk where no kerb exists.
    #  * NO stair-head trench, for the two measured B7 reasons recorded in
    #    Docs/reports/w2d_edit_g1.md §3 (frame lip pushes drow to 15.7 rows at
    #    d10; and it would be a second singular cross line against the
    #    statutory tactile band, which GT-E2 caps at one).
    #  * tactile: spec §12.4 registers scene02 stair_top **and** stair_foot,
    #    with "fully sound" (no defect injection). ground_kit takes stair_top
    #    (statutory x -0.90..-0.30, full opening width); the lower landing band
    #    stays on the existing `sc.build_tactile` path because it lives at
    #    z=-3.2, a different surface from this plan.
    gkit=dict(x0=-12.0, half_y=4.0, manhole=[(-1.20, 0.35)],
              gully_x=-0.95, gully_y=3.60),
    # Stair 20 steps x riser 0.16 · tread 0.32 -> drop 3.2 m, run 6.4 m. z_top=0
    stairs=dict(x0=0.0, riser=0.16, tread=0.32, nsteps=20,
                y0=-1.75, y1=1.75, z_top=0.0, base_z=-3.5),
    landing=dict(x0=6.4, x1=7.0, z_top=-3.2, base_z=-3.5),   # Lower landing
    # Retaining wall: thickness 0.3, inner face ±1.75 (touching the stair width), outer face ±2.05, parapet top +0.15
    wall=dict(thick=0.3, y_in=1.75, parapet_top=0.15, base_z=-3.5),
    # Tunnel portal: opening at x=7, 3.5 (width) x 2.3 (height) - z -3.2..-0.9 above the landing (z-3.2),
    #   4 m deep interior box (x 7..11), with the lintel above remaining (z -0.9..0.15)
    tunnel=dict(x0=7.0, depth=4.0, open_w=3.5, open_h=2.3,
                floor_z=-3.2, lintel_top=0.15),
    # Ground-level railing around the pit (3 sides): south/north x 0..7 at y=±1.9, rear at x=7.15
    perim_rail=dict(y=1.9, x0=0.0, x1=7.0, x_rear=7.15,
                    parapet_top=0.15, rail_h=0.9, post_r=0.03,
                    rail_r=0.03, rail_mid_r=0.018, mid_h=0.45, spacing=1.2),
    # ═══ [realism v1] Stair rail → statutory handrail (§15(3)/(4)) ══════════
    #  Old: `y=1.65, x_start=-0.5, rail_h=0.9, post_r=0.02, rail_r=0.03,
    #        rail_mid_r=0.018, rail_mid_drop=0.45, spacing=1.2` through
    #        `sc.build_railing_line` — a full **guardrail** per side (top rail +
    #        mid rail + 59 balusters + 6 posts, plus a second coaxial LOOK_GEO
    #        handrail with its own 6 posts) = 156 prims, **29.8 % of the whole
    #        scene** `[measured]`.
    #  The stair is **wall to wall**: width 3.50 = 2 × `wall.y_in` 1.75, so no
    #  side is ever open and §15(1)2 ("railings on both sides") is satisfied by "wall" - the
    #  scene05 cheek-wall reading, Docs/reports/stair_compliance_v1.md §1. No
    #  guardrail is required on the stair at all. §15(3) states what *is*
    #  required: "where there are walls or the like on both sides and therefore no railing, a
    #  **handrail** shall be installed." One pipe per side, no infill.
    #  **Post-mounted, not wall-bracketed** — and that is a measured decision,
    #  not a shortcut. Unlike scene15's 3~4 m house facades, the flanking walls
    #  here are retaining walls capped at `wall.parapet_top` = +0.15, so the
    #  850 mm rail line sits **0.70 m above the wall top** at the stair head and
    #  does not meet the wall until x = 1.60 (step 5) `[computed]`. Brackets
    #  would float over the first 25 % of the run. Posts also let the statutory
    #  ≥300 mm end extensions actually exist (§15(4)3), which a wall mount here
    #  could not provide — and a post-mounted stainless handrail is what open-cut
    #  underpass entrances are actually built with.
    #  y = `wall.y_in` − 0.07 → pipe face 53 mm and post face 50 mm clear of the
    #  wall, both ≥ the statutory 50 mm (§15(4)2) `[computed]`.
    stair_rail=dict(y=1.68, dia=0.034, height=0.85, post_r=0.020,
                    post_spacing=1.20, ext_top=0.30, ext_bot=0.60),
    tactile=dict(ahead=0.3, depth=0.3, proud=0.004,   # Top warning strip x=-0.3..0
                 land_depth=0.4),                      # Landing tactile width
    # v4-B1: width 0.05 / proud 0.001 vanished under 512spp denoising -> the 20 steps read as a
    #   ramp. Enlarged to 0.08 / 0.004 (belongs to the cue toggle - hazard geometry transform unchanged).
    nosing=dict(color=(0.85, 0.72, 0.10), width=0.08, proud=0.004),

    # Surrounding ground / dressing
    # Grass ground (3 cm below the sidewalk at 0). Split into 4 boxes that clear the pit footprint (gx/gy)
    #  - prevents the grass slab (z=-0.03) from covering the opening, since it sits above the stair top (-0.16..).
    #  The tunnel (x 7..11, underground) has its own ceiling, so keeping grass beyond gx1 (7.6) is harmless.
    ground=dict(size=140.0, z_top=-0.03,
                gx0=-0.5, gx1=7.6, gy0=-2.3, gy1=2.3),
    # v4-B2: the hedge read as a 'black cuboid' -> tint raised and height varied across 4 segments to
    #   break up the blockiness. Ends before the road (x 8..13) at x1 6.8, y -6 -> -7 (avoiding the planter).
    hedge=dict(x0=-16.0, x1=6.8, y=-7.0, half=0.3, h=1.0, nseg=4,
               h_var=(0.0, -0.15, 0.05, -0.10), y_var=(0.0, 0.08, -0.06, 0.05)),

    # === v4-D1 road (top-priority context cue: the underpass's 'reason to exist') ===
    #   Establishes the narrative that the tunnel (x 7..11, ceiling top face -0.6) passes under the road.
    #   The east sidewalk (formerly Walk_E x 7..16) is cut by the road width and split into E1/E2.
    road=dict(x0=8.0, x1=13.0, y0=-60.0, y1=60.0, top=-0.02, thick=0.5,
              walk_a=7.7, walk_b=13.3,                 # Kerb outer face = sidewalk cut face
              curb_top=0.10, curb_base=-0.5,
              lane_x=10.5, lane_w=0.12, dash_len=3.0, dash_step=6.0,
              dash_y0=-36.0, dash_n=13),
    # === v4-D other context dressing ===
    # D4 underpass entrance sign (2 posts + 1 panel) - establishes 'underpass' in a single cut
    # [v5.1 realism] Feedback "the board (panel) position is unnatural" -> moved to the **side of the entrance**.
    #   Old: y -2.6..-0.6 (intruding 0.6 m into the walk axis y=0) · z 2.0..2.6 (reading as a gantry
    #     hung from the tops of the posts = a floating panel).
    #   New: y +1.9..+3.7 (**flanking**, touching the pit railing line y=+1.9, 0.15 m outside the
    #     y ±1.75 opening) · z 1.5..2.25 (top-hung on h2.25 posts = a standard post-mounted sign board).
    #   Camera check (grid gy=0 · FOV ±30 deg): eye(-2) behind · eye(-5) outside at 60.3 deg ·
    #     eye(-10) 23.0 deg (7.2 m, background) · approach(-6,0) outside at 47.1 deg ·
    #     pit_edge(-0.5,0) behind · beauty_overview(-7,-5) outside at 65.2 deg against a 31.0 deg
    #     sight axis (34.2 deg off) · inside_looking_up has it 10.4 m away in the background (above the
    #     parapet) -> zero cases of close range (<1.2 m) AND inside the FOV.
    sign=dict(x=-3.4, y0=1.9, y1=3.7, z0=1.5, z1=2.25, thick=0.08,
              post_r=0.05, post_h=2.25),
    # D5 canopy over the stair head (subway-entrance silhouette)
    canopy=dict(x0=-1.8, x1=0.6, y0=-2.45, y1=2.45, z_roof=2.7, post_r=0.08,
                roof_t=0.14, base_z=0.0),
    # D6 route-map / information board - [v5.1] **deleted** (count reduction).
    #   Feedback "reduce the count / if redundant, cut the board" -> the board is removed and
    #   entrance signage is consolidated into the single D4 underpass entrance sign.
    # [v5 shared layer] Korean-language signs - (tag, TEX key, cx, cy, base_z, yaw, w, h, pole_h)
    #   [v5.2 user] Arbitrary warning placards removed - Caution (stair warning) deleted, exit marker only.
    #   Exit(7.8, -1.4, z -3.2): **inside** the tunnel (x 7..11, floor -3.2, clear height 2.3).
    #     Panel top = -3.2+2.1-0.05 = -1.15 < lintel underside -0.9 -> 0.25 m ceiling clearance.
    #     0.35 m from the south wall given the tunnel width y ±1.75 - the centre of travel (y=0) is left clear.
    #   Camera check (grid gy=0, eye x -2/-5/-10, FOV ±30 deg):
    #     Exit    -> inside the tunnel opening (head-on) - the judged subject of approach/pit_edge (reading the dark zone)
    #     inside_looking_up(6.6,0,-2.7) looks towards -X, so Exit is behind it.
    signs=[("Exit", "sign_exit", 7.8, -1.4, -3.2, 180.0, 0.9, 0.45, 2.1)],
    # D7 bollards (sidewalk boundary) - only at y values that do not clash with the sign and canopy posts
    bollards=[(-1.0, -6.0), (-1.0, -4.3), (-1.0, 4.3), (-1.0, 6.0)],
    # D8 2 benches + 2 litter bins
    benches=[(-6.0, -4.0, 0.0), (-6.0, 4.0, 0.0)],
    bins=[(-2.0, -4.0), (-2.0, 4.0)],
    bin_spec=dict(r=0.28, h=0.9),
    # D11 2 planters (replacing the hedge on its own)
    planters=[(-8.0, -5.0), (-13.0, 5.5)],
    # D10 3 fluorescent lamps inside the tunnel (gives the dark zone information - secures data value)
    # [v5 verdict applied] At the exposure set by the noon sun (2450) + dome (1000), intensity 1500
    #   contributed effectively nothing to the image, so the tunnel opening was 'pure black' in every RT cut.
    #   (no dark-zone gradient in pit_edge / approach / beauty_overview alike)
    #   Since this scene's judging point is 'can the lower stair and the tactile paving be read inside
    #   the dark opening', it is raised 1500 -> 45000 (the midpoint of the recommended 30k-60k).
    #   Light positions, count and radius are unchanged - no effect on the geometry or exposure profile.
    tunnel_lights=dict(pos=[(8.0, 0.0, -1.05), (9.5, 0.0, -1.05),
                            (10.5, 0.0, -1.05)],
                       radius=0.12, intensity=45000.0,
                       color=(0.92, 0.95, 1.0)),
    buildings=dict(
        # 1 brick building: y 9..13, x -14..10, h10. Facade on the -Y plane (sidewalk side), windows arrayed along x
        B=dict(x0=-14.0, x1=10.0, y0=9.0, y1=13.0, h=10.0, floors=4,
               axis="y", facade_y=9.0, face_dir=-1.0),
        # Distant vista: 1 building at +X. Facade on the -X plane, windows arrayed along y
        C=dict(x0=22.0, x1=28.0, y0=-10.0, y1=10.0, h=10.0, floors=4,
               axis="x", facade_x=22.0, face_dir=-1.0),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.5, margin=2.0),
    streetlight=dict(pole_h=6.0, pole_r=0.06,
                     arm_len=1.0, arm_r=0.04, head=0.25),
    # v4-D9: street lamps 1 -> 4 (urban rhythm). (x, y, base_z)
    streetlights=[(-4.0, 6.5, 0.0), (-10.0, 6.5, 0.0), (2.0, 6.5, 0.0),
                  (14.5, 6.5, 0.0)],

    # --- Materials: physical size for texture_scale [m/tile] + tint/constants ---
    material=dict(
        scale=dict(plaza_lower=0.7, concrete_floor=1.0, concrete_wall=2.0,
                   grass=1.4, brick_red=2.0, granite_dark=1.0, tactile=0.3),
        grass_tint=(0.55, 0.68, 0.42),
        hedge_tint=(0.50, 0.64, 0.38),            # v4-B2 hedge (black-slab fix)
        tunnel_tint=(0.32, 0.32, 0.34),           # Dark tunnel concrete tint
        asphalt_color=(0.045, 0.045, 0.047), asphalt_rough=0.75,  # v4-D1 road surface
        lane_color=(0.55, 0.55, 0.52),            # v4-D2 lane markings
        sign_color=(0.045, 0.085, 0.19), sign_face=(0.55, 0.56, 0.58),
        seat_wood=(0.13, 0.085, 0.05), seat_wood_rough=0.8,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,   # Tree trunk
        canopy_a=(0.035, 0.052, 0.024), canopy_b=(0.042, 0.060, 0.030),
        canopy_rough=1.0,                          # v4-B (shared): canopy albedo raised
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        # [v5.1 §4] Parapet 0.90 -> 0.72 (no large pure-white areas)
        parapet_color=(0.72, 0.72, 0.69), parapet_rough=0.6,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.4,
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.5,
    ),

    # --- Lighting: scene01's light dict as-is + SUN_AZ_OFFSET=171.5 ---
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


def _deep_update(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_update(dst[k], v)
        else:
            dst[k] = v


# Parameter override (for A/B render comparison - no effect on a default run)
_ov = os.environ.get("NEGOBS_PARAMS_OVERRIDE", "")
if _ov:
    _deep_update(PARAMS, json.loads(_ov))
    print(f"[PARAMS] override 적용: {_ov}")

# SCENE_CONFIG environment-variable override (for the toggle-integrity verification pipeline)
_sc_ov = os.environ.get("NEGOBS_SCENE_CONFIG", "")
if _sc_ov:
    _deep_update(SCENE_CONFIG, json.loads(_sc_ov))
    print(f"[SCENE_CONFIG] override 적용: {_sc_ov}")


# ===========================================================================
# [C] Path constants + required texture roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene02")

# Roles in use, passed to check_assets (concrete_wall/floor · plaza_lower · grass ·
# brick_red·granite_dark·tactile + HDRI + MDL)
ASSET_ROLES = ["plaza_lower", "concrete_floor", "concrete_wall", "grass",
               "brick_red", "granite_dark", "tactile",
               "sign_exit",     # [v5.2 user] Arbitrary warning placards removed
               "hdri", "mdl"]


def build_views():
    """Camera presets: 9 grid_views(gy=0.0) + 4 mise-en-scene cuts (§C)."""
    views = sc.grid_views(0.0)               # This scene has no central railing -> gy=0
    # approach: approaching the pit along the sidewalk
    views["approach"] = dict(eye=[-6.0, 0.0, 1.5], tgt=[3.0, 0.0, -0.6])
    # pit_edge: over the edge looking down at -15 deg (dx5, dz-1.3 -> -14.6 deg)
    views["pit_edge"] = dict(eye=[-0.5, 0.0, 1.7], tgt=[4.5, 0.0, 0.4])
    # inside_looking_up: from the landing, looking up towards the backlit ground level
    views["inside_looking_up"] = dict(eye=[6.6, 0.0, -2.7], tgt=[-3.0, 0.0, 1.0])
    # beauty_overview: oblique high-angle impression
    views["beauty_overview"] = dict(eye=[-7.0, -5.0, 3.0], tgt=[3.0, 1.0, -1.2])
    return views


# ===========================================================================
# [D] Isaac Sim scene assembly + main loop
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. approach / beauty  — 지하도 피트 인상 (개구·옹벽·계단·터널 포탈 식별)
 2. h0.3·d5~10         — 피트가 완전한 평지로 보이고 난간·점자만 뜨는가
 3. pit_edge / inside  — 피트 내부 깊이감·암부 그라디언트, 터널 포탈 암부
 4. cue ON vs OFF      — 피트·계단·옹벽 기하 트랜스폼 동일한가 (nosing/railing/tactile)
 5. 재질               — 타일 반복·늘어남·Z파이팅·부유 없는가"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"
    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])

    # -- Stage 1: boot Isaac Sim (SimulationApp must always come first) --
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
    UsdGeom.Xform.Define(stage, "/World/Scene02")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene02"

    # Thin geometry wrapper (captures stage)
    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        # scene_common.make_pbr takes stage as its first positional argument - injected here
        return sc.make_pbr(stage, path, *args, **kwargs)

    # -------------------------------------------------------------------
    # Materials
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["sidewalk"] = PBR(
            f"{ROOT}/Looks/Sidewalk", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
            sca["plaza_lower"])
        M["concrete_floor"] = PBR(
            f"{ROOT}/Looks/ConcreteFloor", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"), sca["concrete_floor"])
        M["concrete_wall"] = PBR(
            f"{ROOT}/Looks/ConcreteWall", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"), sca["concrete_wall"])
        # Tunnel interior: concrete_wall texture + dark tint (reinforces the dome-occluded dark zone)
        M["tunnel"] = PBR(
            f"{ROOT}/Looks/Tunnel", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"), sca["concrete_wall"],
            tint=mp["tunnel_tint"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            sca["brick_red"])
        M["granite_dark"] = PBR(
            f"{ROOT}/Looks/GraniteDark", sc.tex_path("granite_dark", "diff"),
            sc.tex_path("granite_dark", "nor"),
            sc.tex_path("granite_dark", "rough"), sca["granite_dark"])
        M["tactile"] = PBR(
            f"{ROOT}/Looks/Tactile", sc.tex_path("tactile", "diff"),
            sc.tex_path("tactile", "nor"), None, sca["tactile"])
        # Constant colours
        M["glass"] = PBR(f"{ROOT}/Looks/Glass",
                                 diffuse_color=mp["glass_color"],
                                 roughness_const=mp["glass_rough"], metallic=0.0)
        M["rail"] = PBR(f"{ROOT}/Looks/Rail",
                                diffuse_color=mp["rail_color"],
                                metallic=mp["rail_metallic"],
                                roughness_const=mp["rail_rough"])
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                                   diffuse_color=mp["parapet_color"],
                                   roughness_const=mp["parapet_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp",
                                diffuse_color=mp["lamp_color"],
                                roughness_const=mp["lamp_rough"])
        M["pole"] = PBR(f"{ROOT}/Looks/Pole",
                                diffuse_color=mp["pole_color"],
                                metallic=mp["pole_metallic"],
                                roughness_const=mp["pole_rough"])
        # Materials specific to the v4-D dressing
        M["asphalt"] = PBR(f"{ROOT}/Looks/Asphalt",
                           diffuse_color=mp["asphalt_color"],
                           roughness_const=mp["asphalt_rough"])
        M["lane"] = PBR(f"{ROOT}/Looks/Lane",
                        diffuse_color=mp["lane_color"], roughness_const=0.75)
        M["hedge"] = PBR(
            f"{ROOT}/Looks/Hedge", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            1.2, tint=mp["hedge_tint"])
        M["sign"] = PBR(f"{ROOT}/Looks/Sign", diffuse_color=mp["sign_color"],
                        roughness_const=0.5)
        M["sign_face"] = PBR(f"{ROOT}/Looks/SignFace",
                             diffuse_color=mp["sign_face"],
                             roughness_const=0.6)
        M["seat_wood"] = PBR(f"{ROOT}/Looks/SeatWood",
                             diffuse_color=mp["seat_wood"],
                             roughness_const=mp["seat_wood_rough"])
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        return M

    # -------------------------------------------------------------------
    # Ground (always): grass ground at z=-0.03 (3 cm below the sidewalk at 0, prevents void beyond the site)
    # -------------------------------------------------------------------
    def build_ground(M):
        g = PARAMS["ground"]
        cz = g["z_top"] - 0.25
        th = 0.5
        H = g["size"] / 2.0                       # ±70
        gx0, gx1 = g["gx0"], g["gx1"]             # Pit footprint x (-0.5..7.6)
        gy0, gy1 = g["gy0"], g["gy1"]             # Pit footprint y (-2.3..2.3)
        # 4 boxes that clear the pit footprint (same technique as the sidewalk opening)
        # West: -H..gx0, full width
        BOX(f"{ROOT}/Grass_W", ((-H + gx0) / 2.0, 0.0, cz),
            (gx0 + H, g["size"], th), M["grass"])
        # East: gx1..H, full width
        BOX(f"{ROOT}/Grass_E", ((gx1 + H) / 2.0, 0.0, cz),
            (H - gx1, g["size"], th), M["grass"])
        # South: gx0..gx1, -H..gy0
        BOX(f"{ROOT}/Grass_S", ((gx0 + gx1) / 2.0, (-H + gy0) / 2.0, cz),
            (gx1 - gx0, gy0 + H, th), M["grass"])
        # North: gx0..gx1, gy1..H
        BOX(f"{ROOT}/Grass_N", ((gx0 + gx1) / 2.0, (gy1 + H) / 2.0, cz),
            (gx1 - gx0, H - gy1, th), M["grass"])

    # -------------------------------------------------------------------
    # Ground sidewalk - split into 4 boxes around the opening (x 0..7, retaining-wall outer face ±2.05).
    #   West (x<0) and east (x>7) run the full y width; south (y<-y_out) and north (y>y_out) only span the opening's x range.
    #   The sidewalk cut faces meet the retaining-wall outer faces (±y_out) exactly -> no Z-fighting.
    # -------------------------------------------------------------------
    def build_sidewalk(M):
        w = PARAMS["walk"]
        p = PARAMS["pit"]
        wl = PARAMS["wall"]
        top, th = w["z_top"], w["thick"]
        cz = top - th / 2.0
        y_out = p["y1"] + wl["thick"]        # Retaining-wall outer face = 2.05 (sidewalk cut position)
        # [W2-0 · P-A] Walk_W is the slab ground_kit decorates. Without the
        # exclusion the displacement skin (+6.5..16.5 mm) buries every flush
        # element on it - manhole (+-10 mm) and the 6 mm tactile dots (spec
        # §1.1/§12.5-1).
        sc.skin_exclude(f"{ROOT}/Walk_W")
        # West: x_w..pit.x0, full width
        BOX(f"{ROOT}/Walk_W",
            ((w["x_w"] + p["x0"]) / 2.0, (w["y_s"] + w["y_n"]) / 2.0, cz),
            (p["x0"] - w["x_w"], w["y_n"] - w["y_s"], th),
            M["sidewalk"], col=True)
        # East: pit.x1..x_e, full width.  v4-D1: when the road is present, cut out the road width
        #   (kerb outer faces walk_a..walk_b) and split it in two. With the dressing OFF it stays one slab
        #   as before (either way there is no hole in the walking surface - toggle integrity).
        rd = PARAMS["road"]
        if cfg["cue_scene_dressing"]:
            spans = [("E1", p["x1"], rd["walk_a"]),
                     ("E2", rd["walk_b"], w["x_e"])]
        else:
            spans = [("E", p["x1"], w["x_e"])]
        for tag, xa, xb in spans:
            BOX(f"{ROOT}/Walk_{tag}",
                ((xa + xb) / 2.0, (w["y_s"] + w["y_n"]) / 2.0, cz),
                (xb - xa, w["y_n"] - w["y_s"], th),
                M["sidewalk"], col=True)
        # South: opening x range, y_s..-y_out
        BOX(f"{ROOT}/Walk_S",
            ((p["x0"] + p["x1"]) / 2.0, (w["y_s"] - y_out) / 2.0, cz),
            (p["x1"] - p["x0"], (-y_out) - w["y_s"], th),
            M["sidewalk"], col=True)
        # North: opening x range, +y_out..y_n
        BOX(f"{ROOT}/Walk_N",
            ((p["x0"] + p["x1"]) / 2.0, (y_out + w["y_n"]) / 2.0, cz),
            (p["x1"] - p["x0"], w["y_n"] - y_out, th),
            M["sidewalk"], col=True)

    # -------------------------------------------------------------------
    # [W2-D] ground_kit — P3 sidewalk_block, upper sidewalk only.
    #   Runs in **both** hazard arms on purpose: GT-E4 compares this scene
    #   with its hazard-off twin, and that comparison is only meaningful if
    #   the ground elements are byte-identical in the two arms.
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["gkit"]
        p = PARAMS["pit"]
        gp = gk.plan_ground(
            "sidewalk_block",
            region=(g["x0"], -g["half_y"], p["x0"], g["half_y"]),
            z=PARAMS["walk"]["z_top"], gy=0.0, origin=(0.0, 0.0, 0.0),
            edges=[("pit_edge", float(p["x0"]))],
            dists=(2, 5, 10), scene="scene02",
            tactile=("stair_top",) if cfg["cue_tactile"] else (),
            overrides=dict(infra=dict(manhole=1, gully=2, gutter_L=0)),
            sites=dict(manhole=[tuple(v) for v in g["manhole"]],
                       gully=[(g["gully_x"], -g["gully_y"]),
                              (g["gully_x"], g["gully_y"])]),
            seed=2)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["granite_dark"], crack=M["granite_dark"],
                  patch=M["concrete_floor"], patch_cut=M["granite_dark"],
                  manhole=M["rail"], gully=M["rail"], weed=M["hedge"],
                  stain_dirt=M["granite_dark"], stain_gum=M["granite_dark"],
                  tactile=M["tactile"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris,
                              slabs=(f"{ROOT}/Walk_W", f"{ROOT}/FlatWalkA",
                                     f"{ROOT}/FlatWalk"))
        print(f"[ground_kit] scene02 P3 · prims {res['prims']} · "
              f"delta_max {res['gt_delta_max']:.4f} · "
              f"unit_cell {res['unit_cell']}")
        return res

    def build_flat_fill(M):
        """hazard_stairs=False control: fill the opening and unify everything to flat ground at z=0.
        v4-D1: if the road is on, leave the road width clear so the carriageway is not buried."""
        w = PARAMS["walk"]
        rd = PARAMS["road"]
        if cfg["cue_scene_dressing"]:
            spans = [("A", w["x_w"], rd["walk_a"]),
                     ("B", rd["walk_b"], w["x_e"])]
        else:
            spans = [("", w["x_w"], w["x_e"])]
        for tag, xa, xb in spans:
            BOX(f"{ROOT}/FlatWalk{tag}",
                ((xa + xb) / 2.0, (w["y_s"] + w["y_n"]) / 2.0,
                 w["z_top"] - w["thick"] / 2.0),
                (xb - xa, w["y_n"] - w["y_s"], w["thick"]),
                M["sidewalk"], col=True)

    # -------------------------------------------------------------------
    # Stair + landing (material: cue_material_break)
    # -------------------------------------------------------------------
    def build_stairs(stair_mtl):
        st = PARAMS["stairs"]
        sc.build_straight_stairs(
            stage, f"{ROOT}/Stairs", st["x0"], st["y0"], st["y1"],
            st["riser"], st["tread"], st["nsteps"], st["base_z"], stair_mtl,
            z_top=st["z_top"], collider=True)
        la = PARAMS["landing"]
        st = PARAMS["stairs"]
        BOX(f"{ROOT}/Landing",
            ((la["x0"] + la["x1"]) / 2.0, (st["y0"] + st["y1"]) / 2.0,
             (la["z_top"] + la["base_z"]) / 2.0),
            (la["x1"] - la["x0"], st["y1"] - st["y0"],
             la["z_top"] - la["base_z"]),
            stair_mtl, col=True)

    # -------------------------------------------------------------------
    # Retaining wall - both sides (south/north) + rear lintel. Inner face ±1.75 (touching the stair width), parapet +0.15.
    # -------------------------------------------------------------------
    def build_walls(M):
        p = PARAMS["pit"]
        wl = PARAMS["wall"]
        tn = PARAMS["tunnel"]
        y_out = wl["y_in"] + wl["thick"]          # 2.05
        y_ctr = (wl["y_in"] + y_out) / 2.0        # 1.9
        top = wl["parapet_top"]                   # 0.15
        bot = wl["base_z"]                        # -3.5
        cz = (top + bot) / 2.0
        hz = top - bot
        Lx = p["x1"] - p["x0"]
        # Retaining walls on both sides (south y=-1.9 / north y=+1.9), x 0..7
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            BOX(f"{ROOT}/Wall_{tag}",
                ((p["x0"] + p["x1"]) / 2.0, sgn * y_ctr, cz),
                (Lx, wl["thick"], hz), M["concrete_wall"], col=True)
        # Rear retaining wall: only the lintel above the tunnel opening (z -3.2..-0.9) remains (z -0.9..0.15)
        lintel_bot = tn["floor_z"] + tn["open_h"]  # -0.9
        lintel_top = tn["lintel_top"]              # 0.15
        BOX(f"{ROOT}/Wall_RearLintel",
            (tn["x0"] + wl["thick"] / 2.0, 0.0,
             (lintel_bot + lintel_top) / 2.0),
            (wl["thick"], 2.0 * y_out, lintel_top - lintel_bot),
            M["concrete_wall"], col=True)

    # -------------------------------------------------------------------
    # Tunnel - 4 m deep interior box (floor/ceiling/both walls/dead-end rear wall), dark tint.
    # -------------------------------------------------------------------
    def build_tunnel(M):
        tn = PARAMS["tunnel"]
        wl = PARAMS["wall"]
        p = PARAMS["pit"]
        x0 = tn["x0"]
        x1 = tn["x0"] + tn["depth"]               # 11.0
        cx = (x0 + x1) / 2.0
        floor_z = tn["floor_z"]                    # -3.2
        ceil_z = floor_z + tn["open_h"]            # -0.9
        y_in = wl["y_in"]                          # 1.75
        y_out = y_in + wl["thick"]                 # 2.05
        Wy = 2.0 * y_in                            # 3.5 (opening width)
        thk = wl["thick"]                          # 0.3
        # Floor (top face floor_z)
        BOX(f"{ROOT}/Tunnel/Floor", (cx, 0.0, floor_z - thk / 2.0),
            (tn["depth"], Wy, thk), M["tunnel"], col=True)
        # Ceiling (underside ceil_z). Starts at x0+thk - avoids Z-fighting between the ceiling underside
        #   and the underside of the rear lintel (x0..x0+thk), which faces down at z=ceil_z.
        ce_x0 = x0 + thk
        BOX(f"{ROOT}/Tunnel/Ceil",
            ((ce_x0 + x1) / 2.0, 0.0, ceil_z + thk / 2.0),
            (x1 - ce_x0, Wy, thk), M["tunnel"], col=True)
        # Both walls (inner faces ±y_in), z floor..ceil
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            BOX(f"{ROOT}/Tunnel/Wall_{tag}",
                (cx, sgn * (y_in + thk / 2.0), (floor_z + ceil_z) / 2.0),
                (tn["depth"], thk, ceil_z - floor_z), M["tunnel"], col=True)
        # Dead-end rear wall (x1)
        BOX(f"{ROOT}/Tunnel/Back",
            (x1 + thk / 2.0, 0.0, (floor_z + ceil_z) / 2.0),
            (thk, 2.0 * y_out, ceil_z - floor_z), M["tunnel"], col=True)

    # -------------------------------------------------------------------
    # [v5 shared layer] Korean-language sign (cue_sign)
    # -------------------------------------------------------------------
    def build_signs():
        """sc.build_sign placement. [v5.2 user] Arbitrary warning placards removed - exit sign only.
        Coordinate and camera checks are in the PARAMS['signs'] comment. Hazard geometry unchanged."""
        back = sc.make_pbr(stage, f"{ROOT}/Looks/SignBack",
                           diffuse_color=(0.16, 0.17, 0.18),
                           metallic=0.6, roughness_const=0.5)
        for tag, key, cx, cy, bz, yaw, w, h, ph in PARAMS["signs"]:
            panel = sc.make_pbr(stage, f"{ROOT}/Looks/Sign{tag}",
                                diff=sc.tex_path(key, "diff"), uv_mode=True,
                                roughness_const=0.6)
            sc.build_sign(stage, f"{ROOT}/Sign_{tag}", cx, cy, bz, yaw, panel,
                          w=w, h=h, pole_h=ph, back_mtl=back)

    # -------------------------------------------------------------------
    # Cues - nosing / tactile / railing
    # -------------------------------------------------------------------
    def build_cues(M, stair_mtl):
        st = PARAMS["stairs"]

        # -- cue_nosing: yellow anti-slip strip on every step --
        if cfg["cue_nosing"]:
            ns = PARAMS["nosing"]
            sc.build_nosing(
                stage, f"{ROOT}/Nosing", st["x0"], st["y0"], st["y1"],
                st["riser"], st["tread"], st["nsteps"],
                color=ns["color"], width=ns["width"], proud=ns["proud"],
                z_top=st["z_top"])

        # -- cue_tactile: lower landing --
        #   [W2-D] The **upper** band moved to ground_kit (spec §12.4 registry
        #   scene02/stair_top). The old `Tactile_Top` sat at x -0.30..0.00:
        #   no statutory 0.30 m set-back, and GT-E1' needs 40*0.006 = 0.24 m of
        #   clearance for a 6 mm dot, so it was a B6 violation as built.
        #   The landing band stays here - it is on the z=-3.2 surface, which is
        #   not part of the upper-sidewalk plan.
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            la = PARAMS["landing"]
            # Lower landing: warning strip in front of the portal entrance
            sc.build_tactile(stage, f"{ROOT}/Tactile_Land",
                             la["x1"] - tc["land_depth"], la["x1"],
                             st["y0"], st["y1"], M["tactile"],
                             z=la["z_top"], proud=tc["proud"])

        # -- cue_railing: one handrail line on each side of the stair (§15③) + 3-sided railing around the pit --
        #   [realism v1] The two stair *guardrails* became two **handrails**.
        #   Rationale and the wall-height measurement are in PARAMS.stair_rail.
        #   The pit perimeter guard below is untouched — that one is the real
        #   fall protection in this scene (a 3.2 m hole in a public sidewalk)
        #   and it is also the scene's grazing-angle identity cue: from h0.3 at
        #   distance the pit reads flat and only the perimeter rail floats.
        #   The stair lines never carried that read — their rail line drops
        #   below the sidewalk plane by x = 1.7 `[computed]`.
        #   GT: handrails create no terrain z — no drop label change.
        if cfg["cue_railing"]:
            sr = PARAMS["stair_rail"]

            # Stepped ground callback - the post feet sit on the actual step top faces
            #   (x<0 = ground 0.0, stair range = step top face, lower landing = clamped to -3.2).
            def stair_ground(x):
                if x <= 1e-9:
                    return 0.0
                return -st["riser"] * min(max(int(x / st["tread"]) + 1, 1),
                                          st["nsteps"])

            run = st["tread"] * st["nsteps"]          # 6.4
            drop = st["riser"] * st["nsteps"]         # 3.2
            n_hr = 0
            for sgn, tag in ((-1.0, "S"), (1.0, "N")):
                res = sk.build_handrail(
                    stage, f"{ROOT}/StairRail_{tag}", sgn * sr["y"],
                    st["x0"], run, drop, M["rail"], sc.add_cylinder,
                    z_top=st["z_top"], height=sr["height"], dia=sr["dia"],
                    ext_top=sr["ext_top"], ext_bot=sr["ext_bot"],
                    post_r=sr["post_r"], post_spacing=sr["post_spacing"],
                    ground_fn=stair_ground, strict=False)
                for w in res["warnings"]:
                    print(f"[cue_railing] 규정 미달 — {w}")
                n_hr += len(res["prims"])
            print(f"[cue_railing] 계단 손잡이 2선 (φ{sr['dia'] * 1000:.0f} · "
                  f"h{sr['height'] * 1000:.0f} · 끝단연장 "
                  f"{sr['ext_top'] * 1000:.0f}/{sr['ext_bot'] * 1000:.0f}) · "
                  f"프림 {n_hr} — 방호는 좌우 옹벽 + 피트 둘레 난간")

            # Ground-level railing on 3 sides of the pit (horizontal rail on the parapet - add_cylinder directly)
            pr = PARAMS["perim_rail"]
            base_z = pr["parapet_top"]                # 0.15
            top_z = base_z + pr["rail_h"]             # 1.05
            mid_z = base_z + pr["mid_h"]              # 0.60

            def hrail(prefix, along, const_c, a0, a1):
                """One horizontal railing run: top + middle rail with posts. along='x'|'y'."""
                mid_c = (a0 + a1) / 2.0
                length = a1 - a0
                if along == "x":
                    CYL(f"{prefix}/Top", (mid_c, const_c, top_z),
                        pr["rail_r"], length, M["rail"], rotY=90.0)
                    CYL(f"{prefix}/Mid", (mid_c, const_c, mid_z),
                        pr["rail_mid_r"], length, M["rail"], rotY=90.0)
                else:                                  # along Y (rotX=90)
                    CYL(f"{prefix}/Top", (const_c, mid_c, top_z),
                        pr["rail_r"], length, M["rail"], rotX=90.0)
                    CYL(f"{prefix}/Mid", (const_c, mid_c, mid_z),
                        pr["rail_mid_r"], length, M["rail"], rotX=90.0)
                # Posts: from the parapet top face (base_z) up to the top rail
                ph = top_z - base_z
                n = 0
                a = a0 + pr["spacing"] / 2.0
                while a <= a1 - pr["spacing"] / 2.0 + 1e-6:
                    if along == "x":
                        pxy = (a, const_c, base_z + ph / 2.0)
                    else:
                        pxy = (const_c, a, base_z + ph / 2.0)
                    CYL(f"{prefix}/Post_{n}", pxy, pr["post_r"], ph, M["rail"])
                    a += pr["spacing"]
                    n += 1

            # South and north edges (x 0..7), rear (x=7.15, y -1.9..1.9)
            hrail(f"{ROOT}/PerimRail_S", "x", -pr["y"], pr["x0"], pr["x1"])
            hrail(f"{ROOT}/PerimRail_N", "x", pr["y"], pr["x0"], pr["x1"])
            hrail(f"{ROOT}/PerimRail_R", "y", pr["x_rear"], -pr["y"], pr["y"])

    # -------------------------------------------------------------------
    # Dressing - 1 brick building + distant vista + hedge + street lamps
    # -------------------------------------------------------------------
    def build_road(M):
        """v4-D1/D2 [top priority]: asphalt road crossing over the tunnel + kerb + lane markings.

        Coordinate basis - the tunnel is x 7..11 (ceiling top face -0.6), rear wall x 11..11.3.
        The carriageway x 8..13 covers it, so the narrative of "an underpass running beneath a
        road" holds and the dead-end rear wall (x 11.3) is not a problem. The road top face
        -0.02 sits 1 cm above the grass ground top face -0.03, so nothing is buried. Kerb top
        face +0.10 (10 cm above the sidewalk at 0.0).
        """
        rd = PARAMS["road"]
        cy = (rd["y0"] + rd["y1"]) / 2.0
        Ly = rd["y1"] - rd["y0"]
        BOX(f"{ROOT}/Road/Surface",
            ((rd["x0"] + rd["x1"]) / 2.0, cy, rd["top"] - rd["thick"] / 2.0),
            (rd["x1"] - rd["x0"], Ly, rd["thick"]), M["asphalt"], col=True)
        # 2 kerb lines (between the sidewalk cut faces walk_a/walk_b and the carriageway)
        for tag, xa, xb in (("W", rd["walk_a"], rd["x0"]),
                            ("E", rd["x1"], rd["walk_b"])):
            BOX(f"{ROOT}/Road/Curb_{tag}",
                ((xa + xb) / 2.0, cy,
                 (rd["curb_top"] + rd["curb_base"]) / 2.0),
                (xb - xa, Ly, rd["curb_top"] - rd["curb_base"]),
                M["granite_dark"], col=True)
        # Centre dashed line (8 mm proud of the carriageway)
        for k in range(rd["dash_n"]):
            yd = rd["dash_y0"] + rd["dash_step"] * k
            BOX(f"{ROOT}/Road/Dash_{k}",
                (rd["lane_x"], yd, rd["top"] - 0.002),
                (rd["lane_w"], rd["dash_len"], 0.02), M["lane"])

    def build_dressing(M):
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])
        # v4-D1: road (the underpass's reason to exist)
        build_road(M)
        # Hedge - v4-B2: 4 segments with varied height and y to break up the 'black cuboid' look
        h = PARAMS["hedge"]
        seg_w = (h["x1"] - h["x0"]) / float(h["nseg"])
        for i in range(h["nseg"]):
            xa = h["x0"] + seg_w * i
            yc = h["y"] + h["y_var"][i % len(h["y_var"])]
            hh = h["h"] + h["h_var"][i % len(h["h_var"])]
            sc.build_hedge(stage, f"{ROOT}/Hedge_{i}", xa, yc - h["half"],
                           xa + seg_w + 0.05, yc + h["half"], hh,
                           mtl=M["hedge"], base_z=0.0)
        # v4-D5 canopy over the stair head (subway-entrance silhouette)
        cp = PARAMS["canopy"]
        sc.build_canopy(stage, f"{ROOT}/EntryCanopy", cp["x0"], cp["x1"],
                        cp["y0"], cp["y1"], cp["z_roof"], cp["post_r"],
                        M["parapet"], M["pole"], roof_t=cp["roof_t"],
                        base_z=cp["base_z"])
        # v4-D4 underpass entrance sign (panel + white pictogram face + 2 posts)
        sg = PARAMS["sign"]
        zc = (sg["z0"] + sg["z1"]) / 2.0
        BOX(f"{ROOT}/Sign/Panel", (sg["x"], (sg["y0"] + sg["y1"]) / 2.0, zc),
            (sg["thick"], sg["y1"] - sg["y0"], sg["z1"] - sg["z0"]), M["sign"])
        BOX(f"{ROOT}/Sign/Face",
            (sg["x"] - sg["thick"] / 2.0 - 0.006,
             (sg["y0"] + sg["y1"]) / 2.0, zc),
            (0.012, (sg["y1"] - sg["y0"]) - 0.5,
             (sg["z1"] - sg["z0"]) - 0.22), M["sign_face"])
        for tag, py in (("A", sg["y0"] + 0.1), ("B", sg["y1"] - 0.1)):
            CYL(f"{ROOT}/Sign/Post_{tag}", (sg["x"], py, sg["post_h"] / 2.0),
                sg["post_r"], sg["post_h"], M["pole"], col=True)
        # v4-D6 route-map / information board - [v5.1] deleted (redundant in function and position;
        #   the PARAMS["board"] entry itself was removed). Entrance signage is the single D4 sign.
        # v4-D7 bollards
        for k, (bx, by) in enumerate(PARAMS["bollards"]):
            sc.build_bollard(stage, f"{ROOT}/Bollard_{k}", bx, by, 0.0,
                             mtl=M["rail"])
        # v4-D8 2 benches + 2 litter bins
        for k, (bx, by, yaw) in enumerate(PARAMS["benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{k}", bx, by, 0.0,
                           M["seat_wood"], yaw=yaw)
        bn = PARAMS["bin_spec"]
        for k, (bx, by) in enumerate(PARAMS["bins"]):
            CYL(f"{ROOT}/Bin_{k}/Body", (bx, by, bn["h"] / 2.0),
                bn["r"], bn["h"], M["pole"], col=True)
            CYL(f"{ROOT}/Bin_{k}/Rim", (bx, by, bn["h"] + 0.02),
                bn["r"] * 1.1, 0.04, M["rail"])
        # v4-D11 2 planters (including trees)
        tree_mtls = (M["wood"], M["canopy_a"], M["canopy_b"])
        for k, (px, py) in enumerate(PARAMS["planters"]):
            sc.build_planter(stage, f"{ROOT}/Planter_{k}", px, py, 0.0,
                             M["granite_dark"], M["grass"],
                             tree_mtls=tree_mtls)
        # v4-D9 street lamps (1 -> 4)
        sl = PARAMS["streetlight"]
        for k, (x, y, bz) in enumerate(PARAMS["streetlights"]):
            base = f"{ROOT}/Streetlight_{k}"
            CYL(f"{base}/Pole", (x, y, bz + sl["pole_h"] / 2.0),
                sl["pole_r"], sl["pole_h"], M["pole"], col=True)
            for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                ax = x + sgn * sl["arm_len"] / 2.0
                CYL(f"{base}/Arm_{tag}", (ax, y, bz + sl["pole_h"] - 0.1),
                    sl["arm_r"], sl["arm_len"], M["pole"], rotY=90.0)
                hx = x + sgn * sl["arm_len"]
                BOX(f"{base}/Head_{tag}", (hx, y, bz + sl["pole_h"] - 0.15),
                    (sl["head"], sl["head"], 0.12), M["lamp"])
        # v4-D10 3 fluorescent lamps inside the tunnel (gives the lower dark zone information)
        if cfg["hazard_stairs"]:
            from pxr import UsdLux, Gf
            tl = PARAMS["tunnel_lights"]
            for k, (lx, ly, lz) in enumerate(tl["pos"]):
                lt = UsdLux.SphereLight.Define(stage, f"{ROOT}/TunnelLight_{k}")
                lt.CreateRadiusAttr(float(tl["radius"]))
                lt.CreateIntensityAttr(float(tl["intensity"]))
                lt.CreateColorAttr(Gf.Vec3f(*[float(c) for c in tl["color"]]))
                UsdGeom.Xformable(lt.GetPrim()).AddTranslateOp().Set(
                    Gf.Vec3d(float(lx), float(ly), float(lz)))

    # -- Scene assembly --
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    stair_mtl = M["concrete_floor"] if cfg["cue_material_break"] else M["sidewalk"]

    build_ground(M)
    if cfg["hazard_stairs"]:
        build_sidewalk(M)
        build_stairs(stair_mtl)
        build_walls(M)
        build_tunnel(M)
        build_cues(M, stair_mtl)
    else:
        build_flat_fill(M)          # Control: unified flat ground at z=0 (no pit, so no cues on it)
    build_ground_kit(M)             # [W2-D] both arms — GT-E4 twin parity
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    if cfg.get("cue_sign") and cfg["hazard_stairs"]:
        build_signs()               # [v5 shared layer] (Exit is inside the tunnel -> requires the pit)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # -- Camera + render mode --
    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["beauty_overview"]
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

    # ===================================================================
    # Auto capture mode (headless verification pipeline - noon only)
    # ===================================================================
    if capture_mode:
        out_dir = os.path.join(LOOKCHECK_DIR, "auto")
        sc.capture_pipeline(simulation_app, build_views(), out_dir,
                            set_render_mode, look_from)
        simulation_app.close()
        return

    # ===================================================================
    # GUI look check mode (default)
    # ===================================================================
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene02_{ts}.png")
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
