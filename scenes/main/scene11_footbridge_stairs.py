# -*- coding: utf-8 -*-
"""
scene11_footbridge_stairs.py - NegObs synthetic scene 11: steel stairs of a
pedestrian overpass (Isaac Sim 4.5) · new in v5 (old scene11_grating_fireescape → scenes/archive_v3/)

Type    : R6 steel footbridge stairs over 6 lanes (inherits the open-riser ·
          grating see-through axis)
Spec    : Docs/briefs/multi_scene_brief_v5.md §R6 + the shared-layer section
Shared  : scene_common.py (build_open_riser_stairs / build_rot_group /
          build_railing_line / build_canopy / build_sign / build_tactile)
World   : shares the footbridge convention with scene06_overpass_spiral.py
          (roadway asphalt 0.045 · kerb 0.15 · sidewalk paving_interlock · streetlights)

────────────────────────────────────────────────────────────────────────────
Hazard (= the reality of falling short of the code)
  A footbridge crossing 6 lanes. From the deck (z=+5.5) two east steel flights
  (22 steps × 2, with a mid landing) descend to the sidewalk. The treads are
  grating (3 slits) - with no riser **you see straight through to below**, and in
  noon light the slit shadows lay stripes on the road that erase the nosing edge.
  Main defect - **the outer railing on the east mid landing (z=2.75) has no
  kickplate below it.** At robot eye height (h0.3) the railing bars pass above the
  field of view and the whole 0~0.35 m band below is open, so the 2.755 m drop
  past the landing reads as "the floor continues".
  The west mid landing has the same geometry but **does** have a kickplate, making
  it the code-compliant control (same geometry × fitting present/absent = a
  contrast pair for cue learning).
  Third - the sides of the deck and the upper stair drop 5.65 m to the road
  surface (−0.15), and the noise panels block the view, erasing the depth cue of
  the drop (the floor texture).

GT drop invariance: the cue_* toggles only switch railing · panel · kickplate ·
  tactile · sign prims on and off. The transforms of the deck · landings · stairs
  (riser 0.125 / tread 0.32 / 22 steps × 2) never change.

────────────────────────────────────────────────────────────────────────────
Walking-continuity self-check table (west sidewalk → up → deck → down → east sidewalk)

  #  section                  coordinates (world, m)                 step
  ─  ───────────────────────  ─────────────────────────────────────  ──────
  1  W sidewalk approach      (x −45…−30.88, y ±0.9, z −0.005)       —
  2  W flight B 22 steps up   x −30.88…−23.84, z 0.000 → 2.750       0.125/step
  3  W mid landing            x −23.84…−22.04, z 2.750 (kickplate Y) 0.000
  4  W flight A 22 steps up   x −22.04…−15.00, z 2.750 → 5.500       0.125/step
  5  W top landing            x −15.00…−13.20, z 5.500               0.000
  6  deck run                 x −13.20…13.20, y −1.2…1.2, z 5.500    —
     (clearance over the roadway x −10.5…10.5 = 5.10 −(−0.15) = 5.25 m)
  7  E top landing            x 13.20…15.00, z 5.500                 0.000
  8  E flight A 22 steps down x 15.00…22.04, z 5.500 → 2.750         0.125/step
  9  E mid landing            x 22.04…23.84, z 2.750 (kickplate N)   0.000
 10  E flight B 22 steps down x 23.84…30.88, z 2.750 → 0.000         0.125/step
 11  E sidewalk exit          (x 30.88…45, y ±0.9, z −0.005)         0.005

  total rise = total fall = 5.500 m (= 44 × 0.125). Step at the joints ≤ 0.005 m.
  slope = atan(0.125/0.32) = 21.34° - a gentle footbridge stair (2R+T = 0.570).

────────────────────────────────────────────────────────────────────────────
4-box opening convention: no cavity pierces the ground (deck and stairs are all
  above-ground structures). Sidewalk/roadway slabs may be laid as continuous boxes
  without breaching §A-3.

Camera axis note: brief R6 called for a "sidewalk approach grid", but grid_views
  follows the convention of **putting the drop boundary head-on in frame**
  (eye_x = origin −d), so taken as a ground-level approach the robot would face
  the ascending stair and the drop GT would leave the frame.
  → the grid is therefore taken on the **deck run axis (+X, origin = the east
  stair drop start x=15.0, z 5.5)**, and the sidewalk approach the brief asked for
  is provided as the mise-en-scene cut `sidewalk_approach`.
  (Judging priority 1 = does hazard concealment hold at the robot's h0.3 - brief
  v5 shared layer 4)

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene11_footbridge_stairs.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python scene11_footbridge_stairs.py
Smoke (early exit before boot): NEGOBS_SMOKE=1 python scene11_footbridge_stairs.py

Coordinates: Z-up, m. Walk/deck axis +X · roadway axis +Y (6 lanes) · sidewalk top face −0.005.
"""

import os
import sys
import math
import json
import datetime

import numpy as np

import scene_common as sc
import ground_kit as gk


# ===========================================================================
# [A] SCENE_CONFIG - the standard 7 keys.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False -> deck and stairs removed (flat sidewalk control)
    "cue_railing":        True,   # pipe railings on stairs and landings + deck noise panels
    "cue_tactile":        False,  # [v5.2 user] tactile paving is rare in reality - default OFF (ablation path kept)   # urban-practice scene - stair head/foot tactile bands default ON (brief v5)
    "cue_material_break": True,   # kerb · lane paint · road band under the stair
    "cue_nosing":         True,   # yellow non-slip nosing band on the grating (footbridge practice)
    "cue_sign":           True,   # Korean sign sign_info (footbridge guidance) - shared layer
    "cue_scene_dressing": True,   # roadway · bus shelter · streetlights · street trees · distant buildings
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # --- two steel flights (brief R6: width 1.8, 22 steps x 2, mid landing, grating) ---
    #   riser 0.125 = 5.5 / 44 (deck height split evenly into 44 steps -> zero step at the joints).
    #   tread 0.32 -> run 7.04 per flight, slope 21.34 deg, 2R+T = 0.570.
    #   slits 3 : the tread is cut into 4 pieces with three 0.02 m gaps - see-through below, grid shadows.
    stair=dict(riser=0.125, tread=0.32, n=22, y0=-0.90, y1=0.90,
               tread_t=0.045, gap=0.025, slits=3),
    # --- east (main hazard side) stair layout ---
    #   top landing -> flight A -> mid landing -> flight B -> sidewalk
    #   the landings (top and mid) are steel-deck boxes as thick as the bridge deck (deck.thick 0.40).
    #   kickplate=False is this scene's main defect (brief R6).
    east=dict(pad_x0=13.20, pad_x1=15.00, a_x0=15.00,
              mid_len=1.80, z_top=5.50, pad_y0=-1.20, pad_y1=1.20,
              kick_h=0.14, kickplate=False),
    # --- west (code-compliant control) - mirrored with rot_group 180 deg ---
    #   pivot (−7.5, 0) · 180 deg : local (x,y) -> world (−15 − x, −y).
    #   local x 0 -> world −15.00 (top landing west end), local x 15.88 -> world −30.88 (foot).
    west=dict(pivot=(-7.5, 0.0), rot=180.0, kickplate=True),
    # --- footbridge deck (width 2.4, runs along x) ---
    deck=dict(x0=-13.20, x1=13.20, y0=-1.20, y1=1.20, z_top=5.50, thick=0.40,
              panel_h=1.80, panel_t=0.07, rail_z=1.95, rail_r=0.035),
    #   [v6 ruling (5)] the old noise railing = **one large unbroken panel** (26.4 m long).
    #   with no posts, joints, top cap or see-through bays the deck read as a concrete
    #   bunker corridor, and its shadow side turned 30~45 % of the grid cuts pure black ((4)).
    #   -> posts every 2.2 m + **alternating noise-panel / open bays**. make_pbr has no
    #   transparency input (a literal "clear polycarbonate" cannot be built), so the
    #   see-through stretch is built as **open bays with vertical balusters** - the light
    #   and sight purpose is identical, and it matches real Korean footbridge practice (partial noise panels).
    #   post_h 1.98 = top rail centre rail_z 1.95 + pipe radius 0.035 -> the post
    #   **carries** the rail (so the rail does not float as in the old build).
    rail_bay=dict(post_t=0.10, post_h=1.98, n_bay=12, joint=0.05,
                  kick_h=0.16, cap_h=0.07, cap_over=0.03,
                  baluster_r=0.018, n_baluster=6),
    #   support piers - they land on the sidewalk outside the kerb (x +-10.5…11.1). Up to the deck soffit.
    deck_posts=dict(xs=(-11.80, 11.80), y=0.0, r=0.40, z_bot=-0.30,
                    cap_sx=1.0, cap_sy=2.8, cap_h=0.36),
    # --- roadway (6 lanes both ways, along y) ---
    road=dict(x0=-10.50, x1=10.50, y0=-60.0, y1=60.0, z_top=-0.15, thick=0.60),
    #   lane lines: double yellow centre + two sets of white dashes splitting 3 lanes each way (= the "3 lanes" family)
    lane=dict(center_xs=(-0.20, 0.20), dash_xs=(-7.10, -3.60, 3.60, 7.10),
              w=0.15, z=-0.142, t=0.02, seg=3.0, gap=5.0, y0=-58.0, y1=58.0),
    # --- sidewalk (interlocking pavers) + kerb ---
    #   [v6 ruling C-2] the old 34.5 m wide sidewalk read not as openness but as **waste ground**, and the
    #   grass plate met the sky in a straight line. The sidewalk shrinks to 29.5 m (the minimum that holds
    #   the stair foot 30.88 + the sign 31.6 + the bench 36) and outside it a planting strip + a street-tree
    #   row + a distant tree band form the boundary.
    walk=dict(y0=-60.0, y1=60.0, xw0=-40.0, xw1=-10.50, xe0=10.50, xe1=40.0,
              z_top=-0.005, thick=0.50),
    curb=dict(w=0.60, z_top=0.0, thick=0.40),
    # --- planting strip (outer sidewalk boundary) : granite kerbstones + groundcover top ---
    verge=dict(w=2.40, curb_t=0.20, curb_top=0.14, soil_top=0.10,
               y0=-60.0, y1=60.0),
    # --- site ground (closes the horizon) : 1 cm below the road top face (−0.15) ---
    ground=dict(x0=-150.0, x1=150.0, y0=-150.0, y1=150.0, z_top=-0.16,
                thick=1.40),
    # --- railings (cue_railing) ---
    #   rail_h 1.10 (footbridge standard). Kickplates on the landings only - missing on the east side (the hazard).
    rail=dict(rail_h=1.10, post_r=0.026, rail_r=0.032, rail_mid_r=0.022,
              rail_mid_drop=0.52, spacing=1.00, y_inset=0.03),
    # --- tactile paving (cue_tactile) : 4 stair head/foot locations ---
    #  [W2-D Sec.12.4] scene11 = registered sites `stair_top` / `stair_foot`,
    #  p = 0.54 (Seoul 2015: 430 of 797 km of footway conforming), statutory
    #  trigger "0.3 m before the first tread / after the last". Sec.12.4 keeps
    #  it on **this** scene path, so no `gk` tactile op is emitted. The
    #  non-conforming variant assigned to scene11 is "bearing off by 15 deg"
    #  (mis-installation, 325 of 2,847 complaints) - `skew_deg`.
    tactile=dict(pad_len=0.40, low_len=0.40, proud=0.004, skew_deg=15.0),

    # === [W2-D ground_kit] P9 `bridge_deck` - spec Sec.5.3 rows 11 ==========
    #  Grid origin is NOT the world origin: `_grid_shift()` puts it at the east
    #  drop edge (x = east.a_x0 = 15.0, z = 5.50), travel +X. So the plan is
    #  given `origin=(15,0,5.5)` and the edge at forward s = 0.
    #  Prescription:
    #    expansion joints across the deck, span-wise      -> profile step_x 9.0
    #    trodden wear band, centre 0.6-0.9 m, albedo x0.85 -> wear_lane 0.75
    #    rail-foot rundown bands at y = +-1.0             -> edge_break lines
    #    concrete cracking + repair patches                -> crack / patch
    #  `gully` is overridden to 0: `infra_kit.build_gully` sinks a 0.640 m body
    #  and the deck slab is 0.400 m thick, so it would pierce the soffit -
    #  which is the exact surface the `under_grating` preset looks at. A deck
    #  scupper has no builder in the kit; carried as a rider, not faked.
    gkit=dict(
        deck_pad_x1=15.00,             # include the steel top landing for the
                                       # longitudinal bands (d2 W1 sits on it)
        wear_w=0.75,
        drip_y=(-1.00, 1.00),          # rail-foot rundown, Sec.5.3
        patches=((11.20, 0.30), (6.30, -0.35)),   # d5 / d10 near windows
        seed=11,
    ),
    # --- Korean sign (cue_sign) : sign_info (footbridge guidance) 768x512 -> w:h = 3:2 ---
    #   at the east stair foot approach + the west foot. 2.6 m clear of the grid sight axis (y=0).
    #   [v6 ruling (4) - cause established] the "unidentified pure-black rectangular panel"
    #   dead centre of `sidewalk_approach` (eye 38,−5,0.9 -> tgt 26,−0.4,3.2) is **not a
    #   floating defect but the back of this sign**. The old yaw 180 deg put the panel
    #   normal on −X, so approaching the stair from the east sidewalk (+X) only the backing shows.
    #   The backing material was M["steel"](0.055,0.058,0.060), hence a pure-black rectangle.
    #   -> (1) east sign yaw 0 (= facing +X, toward the approaching viewer) / west flipped to yaw 180
    #      (2) backing swapped for aluminium grey (M["signback"], 0.44)
    #      (3) keep the 2.6 m clearance from the sight axis (y=0) (corridor-clearing convention).
    sign=dict(w=0.90, h=0.60, pole_h=2.40,
              spots=((31.60, -2.60, 0.0), (-31.60, 2.60, 180.0))),
    # --- dressing ---
    dress=dict(
        # one bus shelter (east sidewalk) - off the grid sight axis (y −9.6…−5.6)
        #   [v6 ruling (5)] the old build was just a roof slab + 4 posts, so it read as a "carport".
        #   the real minimum = rear glass wall + **2 side walls** + bench + **route-map panel**.
        shelter=dict(x0=17.0, x1=23.0, y0=-9.60, y1=-5.60, z_roof=2.55,
                     post_r=0.08, bench_y=-8.6, side_t=0.05, side_h=2.20,
                     side_inset=0.9, route_w=0.90, route_h=1.10),
        bus_pole=(24.6, -7.60, 3.20),
        lamps=((16.0, -12.0), (16.0, 12.0), (-16.0, -12.0), (-16.0, 12.0)),
        # street-tree row - [v6 ruling C-2] one row on the planting strip (x +-41.2), spacing 7.5 m +- jitter.
        #   it draws the sidewalk-grass boundary as a line. The stair corridor (y −2.4…2.4) is left empty.
        lamp=dict(pole_h=6.0, pole_r=0.10, arm_len=1.1, arm_r=0.055, head=0.32),
        trees=((41.2, -34.0), (41.2, -26.6), (41.2, -19.2), (41.2, -11.6),
               (41.2, 11.8), (41.2, 19.4), (41.2, 26.8), (41.2, 34.2),
               (-41.2, -34.2), (-41.2, -26.8), (-41.2, -19.4), (-41.2, -11.8),
               (-41.2, 11.6), (-41.2, 19.2), (-41.2, 26.6), (-41.2, 34.0),
               (14.0, -20.0), (14.0, 20.0), (26.0, -20.0), (26.0, 20.0),
               (-14.0, -20.0), (-14.0, 20.0), (-26.0, -20.0), (-26.0, 20.0)),
        # [v5.1 §3] benches sit beside street-tree anchors (no even spacing · yaw jitter)
        benches=((38.6, -19.2, 86.0), (-38.6, 19.2, -94.0)),
        bollards=((12.6, -4.0), (12.6, 4.0), (-12.6, -4.0), (-12.6, 4.0)),
        # road band under the stair (cue_material_break) - contrast surface for the grating shadows
        band=dict(x0=15.0, x1=31.5, y0=-1.40, y1=1.40, z=0.004, t=0.03),
    ),
    # [v6 ruling C-2/C-4] distant closure - a tree silhouette band (distant LOD, a ridge-like row of blocks)
    #   is laid outside the sidewalk so the grass plate never meets the sky directly. It is not a file of
    #   individual trees, so no "lollipop repetition" appears. rows = (x0, x1, h).
    #   [v7 ruling (6)-2] the old build (one **solid box**, 7.5 m segment x 4 m wide x 4.4~4.8 high,
    #   plus one small blob on top) was a continuous plate with a flat top, so against the `midlanding` ·
    #   `deck_walk` background it read as a **painted noise wall (green slab)**.
    #   -> (1) the box is lowered to h·base_frac(0.36) so it only carries the understorey,
    #      (2) the top is made by blobs(3) overlapping canopy blobs per segment (height jittered
    #         0.72~1.16x -> a saw-toothed skyline) (3) segments are cut down to 5.0 m and x jitter +-1.7
    #         gives fore/aft depth (4) the tint is not near-field foliage (deep green) but **three
    #         low-saturation grey-greens reflecting aerial perspective** (leaf_far_*), cycled to kill the flat-slab look.
    treeband=dict(rows=((44.5, 48.5, 4.8), (-48.5, -44.5, 4.4)),
                  y0=-58.0, y1=58.0, seg=5.0, jitter=1.2,
                  base_frac=0.36, blobs=3, x_jit=1.2),
    buildings=dict(
        E=dict(x0=50.0, x1=64.0, y0=-52.0, y1=52.0, h=26.0, floors=8,
               axis="x", facade_x=50.0, face_dir=-1.0, base_z=-0.16),
        W=dict(x0=-64.0, x1=-50.0, y0=-52.0, y1=52.0, h=23.0, floors=7,
               axis="x", facade_x=-50.0, face_dir=1.0, base_z=-0.16),
        NE=dict(x0=16.0, x1=42.0, y0=34.0, y1=48.0, h=19.0, floors=6,
                axis="y", facade_y=34.0, face_dir=-1.0, base_z=-0.16),
        NW=dict(x0=-42.0, x1=-18.0, y0=38.0, y1=50.0, h=14.0, floors=5,
                axis="y", facade_y=38.0, face_dir=-1.0, base_z=-0.16),
        SW=dict(x0=-42.0, x1=-16.0, y0=-48.0, y1=-34.0, h=21.0, floors=7,
                axis="y", facade_y=-34.0, face_dir=1.0, base_z=-0.16),
        SE=dict(x0=18.0, x1=42.0, y0=-50.0, y1=-38.0, h=15.5, floors=5,
                axis="y", facade_y=-38.0, face_dir=1.0, base_z=-0.16),
    ),
    #   [v6 ruling (5)] the window decals **repeated on an exact grid** (deck_walk background), making it
    #   the cut with the worst visible tiling -> window size and column spacing are split per building to break the rhythm.
    window=dict(w=1.3, h=1.7, inset=0.15, col_step=2.8, margin=2.5),
    window_by=dict(
        E=dict(w=1.5, h=1.55, inset=0.15, col_step=3.3, margin=3.4),
        W=dict(w=1.15, h=1.85, inset=0.15, col_step=2.5, margin=2.0),
        NE=dict(w=1.35, h=1.5, inset=0.15, col_step=3.0, margin=2.6),
        NW=dict(w=1.6, h=1.35, inset=0.15, col_step=3.5, margin=3.0),
        SW=dict(w=1.2, h=1.8, inset=0.15, col_step=2.4, margin=1.9),
        SE=dict(w=1.45, h=1.6, inset=0.15, col_step=3.1, margin=2.8),
    ),

    # --- materials (sRGB gamma: dark constant colours live in the 0.02~0.06 band - §A-1) ---
    material=dict(
        # [v7 ruling (6)-1 - cause established] W-1's `metal_rust` UV reduction 1.0 -> 0.25
        #   **did take effect** (passed as make_pbr's 6th positional argument scale_m ->
        #   texture_scale = 1/scale_m = 4.0; since this is OmniPBR "Texture Tiling", a larger
        #   value means more repetition = a smaller pattern. Not `inverted`. The horizontal
        #   autocorrelation half-width of the v6 vs v7 midlanding render also measured 20 px -> 10 px).
        #   The ruling recurred because the cause was **contrast and colour, not scale**:
        #     · metal_rust_diff luminance p5 29 / p95 130 (sRGB) = 18:1 linear contrast.
        #       shrinking the tile leaves the blotch contrast untouched (measured std 33.2 -> 34.7).
        #     · the channel-equalising tint (0.61,0.80,1.00) neutralises **only the mean**.
        #       per pixel it pushes dark rust pixels to red-brown (R 31.7 : B 11.0) and bright
        #       bare-metal pixels to blue-white (R 80.5 : B 127.0), **splitting them further**
        #       and so reinforcing the "white/brown high-contrast blotching".
        #   -> action: (1) tile 0.25 -> 0.55 m (3.3 tiles per 1 m² = the ruling's target band of
        #      "3~5 blotches/m²") (2) compress the albedo range to linear 0.045~0.090 (2.0:1)
        #      with OmniPBR albedo_add/brightness (3) remove the rust / bare-metal colour split
        #      with albedo_desaturation (4) the tint carries a neutral cool grey only.
        #      the normal and roughness textures stay as they are, avoiding a "textureless styrofoam slab" (§4).
        #   [v6] the deck and piers using concrete_floor (107,93,77, a warm brown earth) read as
        #   "rusted steel" (under_grating) -> swapped for concrete_wall (joints and tie holes) plus
        #   an equalising tint (0.72,0.77,0.92) = mean 102 ~ albedo 0.40, a neutral concrete.
        scale=dict(paving_interlock=1.0, metal_rust=0.55, concrete_wall=2.0,
                   granite_dark=1.0, brick_red=2.0, grass=1.4, tactile=0.3),
        asphalt_color=(0.045, 0.045, 0.050), asphalt_rough=0.92,
        metal_tint=(0.90, 0.94, 1.00),          # painted-steel tone (neutral cool grey)
        # [v7 ruling (6)-1] OmniPBR albedo correction - the texture lookup gets
        #   diffuse = tex*brightness + add to compress the contrast (linear
        #   p5 0.0116/p95 0.216 -> 0.045/0.090), and desaturation erases the colour split.
        #   expected result: linear median 0.051 ~ sRGB 63 = painted-steel dark grey.
        metal_albedo=dict(brightness=0.220, add=0.0425, desaturation=0.55),
        concrete_tint=(0.72, 0.77, 0.92),
        parapet_tint=(0.78, 0.83, 0.99),
        soil_tint=(0.42, 0.44, 0.34),
        line_white=(0.55, 0.55, 0.52), line_yellow=(0.52, 0.40, 0.06),
        band_color=(0.070, 0.070, 0.075), band_rough=0.88,
        rail_color=(0.050, 0.098, 0.108), rail_rough=0.55, rail_metallic=0.35,
        steel_color=(0.055, 0.058, 0.060), steel_rough=0.50,
        steel_metallic=0.45,
        # [v6 ruling C-3 family] panel_rough 0.18 = near-specular -> sky reflection makes it look
        #   like a large white board. Lowered to the real gloss of painted steel sheet (0.48).
        panel_color=(0.075, 0.095, 0.105), panel_rough=0.48,
        pole_color=(0.30, 0.31, 0.32), pole_metallic=0.75, pole_rough=0.35,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.40,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        parapet_color=(0.58, 0.58, 0.56), parapet_rough=0.60,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        leaf_a=(0.025, 0.045, 0.015), leaf_b=(0.035, 0.060, 0.020),
        # [v7 ruling (6)-2] for the distant (44~48 m) tree band only - three grey-greens whose
        #   saturation and contrast are dropped by aerial perspective. Reusing the near-field leaf_a/b
        #   (deep green) freezes the distance into a "painted board". In sRGB (76,89,70)/(66,79,61)/(86,96,79).
        leaf_far_a=(0.075, 0.100, 0.062),
        leaf_far_b=(0.055, 0.078, 0.048),
        leaf_far_c=(0.095, 0.118, 0.082),
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
    # value specified by brief R6. Shadow azimuth φ = 171.5 −110 +233.5 = 295 deg ->
    #   horizontal shadow bearing ~25 deg (almost +X = the deck's long axis). The grating slit shadows
    #   stretch along the stair direction, maximising the road stripes (the see-through cue).
    SUN_AZ_OFFSET=171.5,

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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene11")
ASSET_ROLES = ["paving_interlock", "metal_rust", "concrete_wall",
               "granite_dark", "brick_red", "grass", "tactile", "sign_info",
               "hdri", "mdl"]


def _flight_run():
    st = PARAMS["stair"]
    return st["n"] * st["tread"]


def _flight_drop():
    st = PARAMS["stair"]
    return st["n"] * st["riser"]


def _east_x():
    """East x nodes: (top landing start, A head, A foot = mid landing start, mid landing end, B foot)."""
    e = PARAMS["east"]
    run = _flight_run()
    a1 = e["a_x0"] + run                       # 22.04
    m1 = a1 + e["mid_len"]                     # 23.84
    b1 = m1 + run                              # 30.88
    return (e["pad_x0"], e["a_x0"], a1, m1, b1)


# ===========================================================================
# [C1b] camera numeric-check base - AABB obstacles + solid lookup (single source for ray marching)
#   [v6 ruling instruction] the grounds for the re-aim (`under_grating`) and the sign bearing fix
#   are checked in coordinates. Follows the scene08 `_obstacle_boxes` / `_solid_at` convention.
#   east and west stairs are **symmetric about x=0** through rot_group 180 deg, so ax=|x| serves both.
# ===========================================================================
def _stair_top(ax):
    """Top-face z of the stair or landing at |x| (None outside the stair band). The width test is the caller's."""
    e = PARAMS["east"]
    st = PARAMS["stair"]
    run = _flight_run()
    a0 = e["a_x0"]
    a1 = a0 + run
    m1 = a1 + e["mid_len"]
    b1 = m1 + run
    z_mid = e["z_top"] - _flight_drop()
    if e["pad_x0"] <= ax <= a0:
        return e["z_top"]
    if a0 < ax <= a1:
        i = min(st["n"], int((ax - a0) / st["tread"]) + 1)
        return e["z_top"] - i * st["riser"]
    if a1 < ax <= m1:
        return z_mid
    if m1 < ax <= b1:
        i = min(st["n"], int((ax - m1) / st["tread"]) + 1)
        return z_mid - i * st["riser"]
    return None


def _solid_at(x, y, z):
    """Name of the terrain / structure solid that contains the point (x,y,z), None if there is none.
    Single source for the buried-camera-eye and sight-line (ray march) checks.
    The grating tread is modelled as a thin slab of thickness tread_t (the slits
    are ignored - to keep the occlusion test conservative)."""
    g = PARAMS["ground"]
    rd = PARAMS["road"]
    wk = PARAMS["walk"]
    dk = PARAMS["deck"]
    e = PARAMS["east"]
    st = PARAMS["stair"]
    if g["x0"] <= x <= g["x1"] and g["y0"] <= y <= g["y1"] \
            and g["z_top"] - g["thick"] <= z <= g["z_top"]:
        return "Ground"
    if rd["x0"] <= x <= rd["x1"] and rd["y0"] <= y <= rd["y1"] \
            and rd["z_top"] - rd["thick"] <= z <= rd["z_top"]:
        return "Road"
    for tag, xa, xb in (("Walk_W", wk["xw0"], wk["xw1"]),
                        ("Walk_E", wk["xe0"], wk["xe1"])):
        if xa <= x <= xb and wk["y0"] <= y <= wk["y1"] \
                and wk["z_top"] - wk["thick"] <= z <= wk["z_top"]:
            return tag
    vg = PARAMS["verge"]
    for tag, xa, xb in (("Verge_W", wk["xw0"] - vg["w"], wk["xw0"]),
                        ("Verge_E", wk["xe1"], wk["xe1"] + vg["w"])):
        if xa <= x <= xb and vg["y0"] <= y <= vg["y1"] \
                and -0.30 <= z <= vg["curb_top"]:
            return tag
    # ── deck · support piers · deck railing ──
    if dk["x0"] <= x <= dk["x1"] and dk["y0"] <= y <= dk["y1"] \
            and dk["z_top"] - dk["thick"] <= z <= dk["z_top"]:
        return "Deck"
    dp = PARAMS["deck_posts"]
    for i, px in enumerate(dp["xs"]):
        if math.hypot(x - px, y - dp["y"]) <= dp["r"] \
                and dp["z_bot"] <= z <= dk["z_top"] - dk["thick"]:
            return f"DeckPost_{i}"
    rb = PARAMS["rail_bay"]
    for i, ye in enumerate((dk["y0"], dk["y1"])):
        if abs(y - ye) <= max(dk["panel_t"], rb["post_t"]) / 2.0 \
                and dk["x0"] <= x <= dk["x1"] \
                and dk["z_top"] <= z <= dk["z_top"] + rb["post_h"]:
            return f"DeckRail_{i}"
    # ── the two stair sets (east/west symmetric) ──
    ax = abs(x)
    top = _stair_top(ax)
    if top is not None:
        run = _flight_run()
        a0, a1 = e["a_x0"], e["a_x0"] + run
        m1 = a1 + e["mid_len"]
        on_pad = (e["pad_x0"] <= ax <= a0) or (a1 < ax <= m1)
        half = (e["pad_y1"] if on_pad else st["y1"])
        if abs(y) <= half:
            if on_pad:
                if top - PARAMS["deck"]["thick"] <= z <= top:
                    return "StairPad"
            elif top - st["tread_t"] <= z <= top:
                return "StairTread"
    # ── bus shelter (roof slab) ──
    sh = PARAMS["dress"]["shelter"]
    if sh["x0"] <= x <= sh["x1"] and sh["y0"] <= y <= sh["y1"] \
            and sh["z_roof"] <= z <= sh["z_roof"] + 0.10:
        return "ShelterRoof"
    # ── distant tree band · buildings ──
    tb = PARAMS["treeband"]
    #   [v7 ruling (6)-2] with the two-tier build (low shrub box + canopy blobs) the silhouette
    #   top rises to h·1.04·1.16 and the x spread grows to +-3.1.
    #   the occlusion test must be **conservative (= larger than reality)**, so the envelope is widened.
    for ri, (xa_, xb_, hh) in enumerate(tb["rows"]):
        if xa_ - 3.2 <= x <= xb_ + 3.2 and tb["y0"] <= y <= tb["y1"] \
                and g["z_top"] <= z <= g["z_top"] \
                + (hh + tb["jitter"]) * 1.21:
            return f"TreeBand_{ri}"
    for key, bd in PARAMS["buildings"].items():
        if bd["x0"] <= x <= bd["x1"] and bd["y0"] <= y <= bd["y1"] \
                and bd.get("base_z", 0.0) - 1.0 <= z \
                <= bd.get("base_z", 0.0) + bd["h"]:
            return f"Building_{key}"
    return None


def _obstacle_boxes():
    """Dressing and railing AABBs for the camera collision check (name, x0,x1, y0,y1, z0,z1).
    Terrain and structure solids are `_solid_at`'s job - only thin prims here."""
    d = PARAMS["dress"]
    gz = PARAMS["walk"]["z_top"]
    boxes = []
    lp = d["lamp"]
    for i, (lx, ly) in enumerate(d["lamps"]):
        boxes.append((f"Lamp_{i}", lx - 1.3, lx + 1.3, ly - 0.6, ly + 0.6,
                      gz, gz + lp["pole_h"]))
    for i, (tx, ty) in enumerate(d["trees"]):
        boxes.append((f"Tree_{i}", tx - 1.1, tx + 1.1, ty - 1.1, ty + 1.1,
                      gz, gz + 4.2))
    for i, (bx, by, _yaw) in enumerate(d["benches"]):
        boxes.append((f"Bench_{i}", bx - 0.4, bx + 0.4, by - 1.0, by + 1.0,
                      gz, gz + 0.5))
    for i, (bx, by) in enumerate(d["bollards"]):
        boxes.append((f"Bollard_{i}", bx - 0.1, bx + 0.1, by - 0.1, by + 0.1,
                      gz, gz + 0.75))
    bx, by, bh = d["bus_pole"]
    boxes.append(("BusPole", bx - 0.3, bx + 0.3, by - 0.3, by + 0.3, gz,
                  gz + bh))
    sh = d["shelter"]
    boxes.append(("Shelter", sh["x0"], sh["x1"], sh["y0"], sh["y1"], gz,
                  sh["z_roof"] + 0.10))
    for i, (sx, sy, _yaw) in enumerate(PARAMS["sign"]["spots"]):
        boxes.append((f"Sign_{i}", sx - 0.5, sx + 0.5, sy - 0.5, sy + 0.5,
                      gz, gz + PARAMS["sign"]["pole_h"]))
    return boxes


# ===========================================================================
# [C2] smoke - geometry self-check before boot (early exit)
# ===========================================================================
def _smoke_report():
    st = PARAMS["stair"]
    e = PARAMS["east"]
    dk = PARAMS["deck"]
    wk = PARAMS["walk"]
    run, drop = _flight_run(), _flight_drop()
    pad0, a0, a1, m1, b1 = _east_x()
    gz = wk["z_top"]
    print("=" * 68)
    print("scene11_footbridge_stairs — SMOKE 기하 자기검증 (부팅 없음)")
    print("=" * 68)
    print(f"  계단: 폭 {st['y1']-st['y0']:.2f} · {st['n']}단 × 2련 · "
          f"riser {st['riser']} · tread {st['tread']} · 그레이팅 슬릿 {st['slits']}")
    print(f"    련당 run {run:.2f} / drop {drop:.3f} · 경사 "
          f"{math.degrees(math.atan2(st['riser'], st['tread'])):.2f}° · "
          f"2R+T = {2*st['riser']+st['tread']:.3f}")
    tot = 2 * drop
    print(f"    총 낙차 {tot:.3f} = 상판고 {e['z_top']:.2f} → "
          f"{'OK' if abs(tot-e['z_top']) < 1e-9 else 'FAIL'} (접속 단차 0)")
    print(f"    낙차 ≥ 0.3 m → {'OK' if tot >= 0.3 else 'FAIL'}")
    print(f"  [동측 x 마디] 상부참 {pad0:.2f}…{a0:.2f} · A {a0:.2f}…{a1:.2f} "
          f"· 중간참 {a1:.2f}…{m1:.2f} · B {m1:.2f}…{b1:.2f}")
    # ── walking continuity table ──
    z_mid = e["z_top"] - drop
    rows = [
        ("서측 보도 → 계단 B", gz, 0.0, "join"),
        ("서측 계단 B(22단)", 0.0, z_mid, "flight"),
        ("서측 중간참", z_mid, z_mid, "flat"),
        ("서측 계단 A(22단)", z_mid, e["z_top"], "flight"),
        ("서측 상부 참 → 상판", e["z_top"], dk["z_top"], "flat"),
        ("상판 → 동측 상부 참", dk["z_top"], e["z_top"], "flat"),
        ("동측 계단 A(22단)", e["z_top"], z_mid, "flight"),
        ("동측 중간참", z_mid, z_mid, "flat"),
        ("동측 계단 B(22단)", z_mid, 0.0, "flight"),
        ("동측 계단 → 보도", 0.0, gz, "join"),
    ]
    print("  [보행 연속성 검증표]")
    bad = 0
    for nm, z0, z1, kind in rows:
        d = abs(z1 - z0)
        if kind == "flight":
            ok = abs(d - drop) < 1e-9
        elif kind == "flat":
            ok = d < 1e-9
        else:
            ok = d <= 0.02
        bad += 0 if ok else 1
        print(f"    {nm:22s} z {z0:+.3f} → {z1:+.3f}  Δ{d:+.3f}  "
              f"{'OK' if ok else 'FAIL'}")
    print(f"    연속성 판정: {'OK' if bad == 0 else f'FAIL({bad})'}")
    # ── hazard: missing kickplate on the mid landing ──
    print(f"  [위험①] 동측 중간참 킥플레이트 {'有' if e['kickplate'] else '無'} "
          f"— 참 상면 {z_mid:.3f} → 보도 {gz:+.3f} 낙차 {z_mid-gz:.3f} m")
    print(f"    로봇 h0.3 시야 하단이 난간 하부 개방대(0…"
          f"{PARAMS['rail']['rail_h']-PARAMS['rail']['rail_mid_drop']:.2f} m)를 "
          f"통과 → 낙차 은닉 성립 {'OK' if not e['kickplate'] else 'FAIL(대조군)'}")
    print(f"    서측 중간참 킥플레이트 "
          f"{'有' if PARAMS['west']['kickplate'] else '無'} (동일 기하 대조군)")
    print(f"  [위험②] 상판·계단 상부 측면 → 차도면 "
          f"{PARAMS['road']['z_top']:+.2f} 낙차 "
          f"{dk['z_top']-PARAMS['road']['z_top']:.3f} m (방음 패널이 바닥 단서 차단)")
    print(f"  [위험③] 그레이팅 투과: 디딤판 {st['slits']}슬릿 × 0.02 m + 전후 "
          f"gap {st['gap']} → 라이저 부재로 하부 직시")
    # ── deck clearance · piers ──
    deck_bot = dk["z_top"] - dk["thick"]
    print(f"  [상판] 상면 {dk['z_top']:.2f} 저면 {deck_bot:.2f} · 차도 "
          f"{PARAMS['road']['z_top']:+.2f} → 유효고 "
          f"{deck_bot-PARAMS['road']['z_top']:.2f} m "
          f"{'OK' if deck_bot-PARAMS['road']['z_top'] >= 4.5 else 'FAIL'}")
    dp = PARAMS["deck_posts"]
    for i, px in enumerate(dp["xs"]):
        on_walk = (wk["xw0"] <= px <= wk["xw1"]) or (wk["xe0"] <= px <= wk["xe1"])
        print(f"    지지 기둥 x={px:+.2f} · 보도 위 {'OK' if on_walk else 'FAIL'} "
              f"· 연석(±{PARAMS['road']['x1']:.2f}) 바깥 "
              f"{'OK' if abs(px) > PARAMS['road']['x1'] else 'FAIL'}")
    # ── rot_group 180 deg coordinate check (west) ──
    w = PARAMS["west"]
    px, py = w["pivot"]

    def _rot180(x, y):
        return (2*px - x, 2*py - y)
    locs = [("상부참 서단", 0.0, 0.0), ("A 하단", run, 0.0),
            ("중간참 끝", run + e["mid_len"], 0.0),
            ("B 하단", 2*run + e["mid_len"], 0.0)]
    print("  [서측 rot_group 180° 검산]  (x,y) → (−15 − x, −y)")
    for nm, lx, ly in locs:
        wx, wy = _rot180(lx, ly)
        print(f"    {nm:10s} 로컬 x {lx:6.2f} → 월드 x {wx:7.2f}")
    wxb, _ = _rot180(2*run + e["mid_len"], 0.0)
    print(f"    서측 하단 x {wxb:.2f} ⊂ 서측 보도 [{wk['xw0']:.1f}, "
          f"{wk['xw1']:.1f}] → {'OK' if wk['xw0'] <= wxb <= wk['xw1'] else 'FAIL'}")
    # ── grid camera vs new geometry coordinate check ──
    gx, gy, gzc = _grid_shift()
    print(f"  [그리드] 원점 = 동측 낙차 시작 (x {gx:.2f}, y {gy:.2f}, z {gzc:.2f})")
    for d in (2, 5, 10):
        ex = gx - d
        on_deck = dk["x0"] <= ex <= e["pad_x1"]
        in_w = dk["y0"] < gy < dk["y1"]
        print(f"    d={d:2d}  eye ({ex:+.2f}, {gy:+.2f}, {gzc+0.3:.2f}~"
              f"{gzc+1.8:.2f}) · 상판/참 위 {'OK' if on_deck else 'FAIL'} "
              f"· 폭 안 {'OK' if in_w else 'FAIL'}")
    print(f"    지지 기둥(x ±11.80, z ≤ {deck_bot:.2f})은 상판 **아래** — "
          f"eye z ≥ {gzc+0.3:.2f} 시선 폐색 없음 OK")
    print(f"    시선 회랑(y −1.2…1.2, x {dk['x0']:.1f}…{b1:.1f}) 드레싱 침입: "
          f"{_corridor_hits()} 개 → {'OK' if _corridor_hits() == 0 else 'FAIL'}")

    # ── front profile (grid axis y=0, increasing x) - is the drop GT in frame ──
    print("  [정면 프로파일] 그리드 축 y=0.00 · x 15.0 → 20.0 (0.25 m 간격)")
    prof = []
    xx = gx
    while xx <= gx + 5.0:
        topz = None
        zz = 6.5
        while zz > -0.60:
            if _solid_at(xx, gy, zz) is not None:
                topz = zz
                break
            zz -= 0.01
        prof.append((xx, topz))
        xx += 0.25
    for xx, topz in prof:
        print(f"    x {xx:+6.2f}  상면 "
              f"{'개방(지면)' if topz is None else f'{topz:+.3f}'}  "
              f"(상판면 대비 "
              f"{(gz if topz is None else topz) - gzc:+.3f})")
    dmax = max(gzc - (t if t is not None else gz) for _, t in prof)
    print(f"    프로파일 최대 낙차 {dmax:.3f} m ≥ 0.3 → "
          f"{'OK(낙차 GT 프레임 내)' if dmax >= 0.3 else 'FAIL'}")

    # ── h0.3 concealment check (sight line grazing the deck edge) ──
    print("  [h0.3 은닉 검산] 상판 연단(x=15.0, z 5.500) 스치는 시선")
    for dd in (2.0, 5.0, 10.0):
        x_hit = gx + (gzc - gz) * dd / 0.3
        print(f"    d={dd:4.1f} m → 보도 재출현 x {x_hit:7.1f} vs 계단 하단 "
              f"{b1:.2f} → 계단 전 구간 은닉 "
              f"{'OK' if x_hit > b1 else 'FAIL'}")

    # ── camera collision and sight-line occlusion check (scene08 convention) ──
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
    print("      ※ preset_* 그리드는 pitch −10° 로 바닥을 겨냥하는 규약 — 제외")
    blocked = []
    for name, v in sorted(views.items()):
        if name.startswith("preset_"):
            continue
        eA = np.array(v["eye"], dtype=float)
        tg = np.array(v["tgt"], dtype=float)
        Ln = float(np.linalg.norm(tg - eA))
        frac, hit = 1.0, None
        for k in range(1, int(Ln / 0.1) + 1):
            f = k * 0.1 / Ln
            s = _solid_at(*(eA + (tg - eA) * f))
            if s is not None:
                frac, hit = f, s
                break
        ok = frac >= 0.90
        print(f"      {name:18s} 첫 차단 {frac:5.2f} "
              f"({hit if hit else '없음'}) → {'OK' if ok else 'FAIL'}")
        if not ok:
            blocked.append(name)
    print(f"      차단 컷: {blocked if blocked else '없음 → OK'}")

    # ── under_grating backlight axis check (grounds for the v6 ruling (4) re-aim) ──
    ug = build_views()["under_grating"]
    ve = np.array(ug["tgt"], dtype=float) - np.array(ug["eye"], dtype=float)
    ve /= np.linalg.norm(ve)
    # dome rotation φ = SUN_AZ_OFFSET + noon_dome_rot + hdri_sun_rotz_offset,
    #   horizontal shadow bearing = atan2(cosφ, −sinφ), sun bearing = shadow + 180 deg
    phi = (PARAMS["SUN_AZ_OFFSET"] - 110.0 + 233.5) % 360.0
    shadow_az = math.degrees(math.atan2(math.cos(math.radians(phi)),
                                        -math.sin(math.radians(phi)))) % 360.0
    sun_az = (shadow_az + 180.0) % 360.0
    cam_az = math.degrees(math.atan2(ve[1], ve[0])) % 360.0
    cam_el = math.degrees(math.asin(max(-1.0, min(1.0, ve[2]))))
    daz = abs((cam_az - sun_az + 180.0) % 360.0 - 180.0)
    print(f"  [under_grating 역광 축] 그림자 방위 {shadow_az:.1f}° → 태양 방위 "
          f"{sun_az:.1f}°/고도 {PARAMS['light']['noon_sun_elev']:.1f}°")
    print(f"    카메라 시선 방위 {cam_az:.1f}° · 고도 {cam_el:+.1f}° → 태양과 "
          f"방위차 {daz:.1f}° → {'OK(역광 = 슬릿 투광 최대)' if daz <= 45.0 else 'FAIL(순광/측광)'}")

    # ── [v7 ruling (6)-3] under_grating frame occupancy check ──
    #   the v6->v7 re-aim failed because "the backlight is right but the sky eats the frame",
    #   so an axis check alone is not enough. With `_solid_at` as the single source the frame
    #   is ray-cast coarsely (32x18) to measure the sky fraction and the main subject directly.
    #   the FOV is back-computed from the v6 render (hFOV half-angle 32.6 deg / vFOV half-angle 19.8 deg, 16:9).
    def _frame_occupancy(eye, tgt, nx=32, ny=18, far=70.0):
        e = np.array(eye, dtype=float)
        fwd = np.array(tgt, dtype=float) - e
        fwd /= np.linalg.norm(fwd)
        rgt = np.cross(fwd, np.array([0.0, 0.0, 1.0]))
        rgt /= np.linalg.norm(rgt)
        upv = np.cross(rgt, fwd)
        th, tv = math.tan(math.radians(32.6)), math.tan(math.radians(19.8))
        sky, cnt = 0, {}
        for j in range(ny):
            sv = (1.0 - 2.0 * (j + 0.5) / ny) * tv
            for i in range(nx):
                su = (2.0 * (i + 0.5) / nx - 1.0) * th
                d = fwd + rgt * su + upv * sv
                d /= np.linalg.norm(d)
                t, what = 0.05, None
                while t < far:
                    what = _solid_at(*(e + d * t))
                    if what is not None:
                        break
                    t += 0.05 if t < 10.0 else 0.30
                if what is None:
                    sky += 1
                else:
                    cnt[what] = cnt.get(what, 0) + 1
        return sky / float(nx * ny), cnt

    sky_f, subj = _frame_occupancy(ug["eye"], ug["tgt"])
    top = sorted(subj.items(), key=lambda kv: -kv[1])[:3]
    print(f"    프레임 점유(레이캐스트 32×18) 하늘 {sky_f*100:.1f} % → "
          f"{'OK(≤30 % — 슬릿 투광 판독 가능)' if sky_f <= 0.30 else 'FAIL(하늘 과다)'}")
    print(f"    주 피사체 {[(n, c) for n, c in top]}  "
          f"(구 컷 eye(22.0,0,0.60)→tgt(16.0,0,4.20) 은 하늘 64.7 %)")
    print("=" * 68)


def _grid_shift():
    """Grid origin = the drop-start edge of the east stair (east end of the top landing, deck level)."""
    e = PARAMS["east"]
    return (e["a_x0"], 0.0, e["z_top"])


def _corridor_hits():
    """Number of dressing prims inside the grid sight corridor (y −1.2…1.2, x −13.2…30.88)."""
    d = PARAMS["dress"]
    _, _, _, _, b1 = _east_x()
    pts = list(d["trees"]) + list(d["lamps"]) + list(d["bollards"]) \
        + [(b[0], b[1]) for b in d["benches"]] + [d["bus_pole"][:2]]
    sh = d["shelter"]
    pts += [((sh["x0"]+sh["x1"])/2.0, (sh["y0"]+sh["y1"])/2.0)]
    pts += [(s[0], s[1]) for s in PARAMS["sign"]["spots"]]
    n = 0
    for x, y in pts:
        if PARAMS["deck"]["x0"] <= x <= b1 and -1.2 <= y <= 1.2:
            n += 1
    return n


# ===========================================================================
# [C-2] ground_kit plan - pure CPU, no USD. Coordinates from PARAMS (Sec.7.4).
# ===========================================================================
def ground_plan():
    """P9 `bridge_deck` plan for the footbridge deck (z = 5.50, travel +X)."""
    g = PARAMS["gkit"]
    dk = PARAMS["deck"]
    gx, gy, gz = _grid_shift()
    return gk.plan_ground(
        "bridge_deck",
        region=(float(dk["x0"]), float(dk["y0"]),
                float(g["deck_pad_x1"]), float(dk["y1"])),
        z=float(dk["z_top"]), gy=float(gy), origin=(gx, gy, gz), axis="+x",
        edges=[("stair_head", 0.0)],
        dists=(2, 5, 10), scene="scene11",
        tactile=(),                 # Sec.12.4 - kept on the scene's own path
        sites=dict(patch=[tuple(v) for v in g["patches"]]),
        overrides=dict(
            infra=dict(gully=0),    # see the PARAMS note: soffit pierce
            surface=(("patch", 2), ("crack", 4),
                     ("stain", ("water", "drip"))),
            extras=(("wear_lane", dict(width=float(g["wear_w"]))),
                    ("edge_break", dict(density=0.0,
                                        lines=list(g["drip_y"]))))),
        seed=int(g["seed"]))


# ===========================================================================
# [D] camera presets - grid_views (along the deck, +X) + 5 mise-en-scene cuts
# ===========================================================================
def build_views():
    """Shift the grid origin to (east drop start x=15.0, deck z=5.5).
    Judging priority 1: at the robot's h0.3 (= z 5.8), do the grating see-through,
    the vanishing nosing and the open mid landing hold? The ground-level sidewalk
    approach is provided separately as the sidewalk_approach cut."""
    gx, gy, gz = _grid_shift()
    v = sc.grid_views(gy)
    out = {}
    for k, val in v.items():
        e, t = list(val["eye"]), list(val["tgt"])
        e[0] += gx
        e[2] += gz
        t[0] += gx
        t[2] += gz
        out[k] = dict(eye=e, tgt=t)
    _, _, a1, m1, b1 = _east_x()
    z_mid = PARAMS["east"]["z_top"] - _flight_drop()
    # under_grating: [v7 ruling (6)-3 re-aim - cause of the repeat failure]
    #   v6->v7 got the axis right (dead centre of the y=0 slit · ascending −X · backlit) but
    #   **eye z 0.60 · elevation +31 deg** was the problem. With a low eye and a shallow aim
    #   the whole soffit hangs **above** the sight line (from that same eye the soffit rises at
    #   34 deg at the far end x=15 and 90 deg at the near end x=22). The frame centre was
    #   effectively aimed at the **sky beyond** the stair head, so the sky ate 64.7 %
    #   (measured by the _solid_at ray cast). The sun (bearing 205 deg · elevation 49.8 deg) also
    #   sat unoccluded at the top of the frame and threw flare.
    #   -> raise the eye to just under the flight A soffit (x 21.70, headroom 0.83 m) and
    #      pitch the aim up to **+50 deg**. tgt is set at the **point on the tread soffit**
    #      that sight line first meets (x 20.79, z 3.08 - the smoke below checks it), so the
    #      sight-line occlusion test (first block >=0.90) still passes unchanged.
    #   measured (same ray cast): sky 18.5 % · frame subject 100 % StairTread ·
    #      the sun is **occluded** by the tread (no direct disc = only slit light remains).
    out["under_grating"] = dict(eye=[21.70, 0.00, 2.00],
                                tgt=[20.79, 0.00, 3.08])
    # deck_walk: pedestrian view along the deck (h1.6) - the corridor between the noise panels
    out["deck_walk"] = dict(eye=[-9.00, 0.00, 7.10], tgt=[8.00, 0.00, 6.30])
    # midlanding: robot view on the east mid landing (h0.3) - head-on at the open band left by the missing kickplate
    out["midlanding"] = dict(eye=[a1 + 0.30, 0.00, z_mid + 0.30],
                             tgt=[m1 + 1.60, -1.90, z_mid - 0.35])
    # sidewalk_approach: brief R6 "sidewalk approach" - from the east sidewalk toward the stair foot
    out["sidewalk_approach"] = dict(eye=[38.00, -5.00, 0.90],
                                    tgt=[26.00, -0.40, 3.20])
    # overview: high-angle full view of the footbridge (6 lanes, deck and both stairs at once)
    out["overview"] = dict(eye=[44.00, -34.00, 17.00], tgt=[2.00, 0.00, 4.00])
    return out


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. h0.3 그리드      — 그레이팅 투과·단코 소실로 하강 시작(x=15.0)이 은닉되나
                       (방음판 그림자면 순흑 대역이 개방 베이로 걷혔는지 함께)
 2. midlanding       — 동측 중간참 난간 하부 개방대(킥플레이트 無) 2.755 m 낙차
 3. under_grating    — 역광 재조준: 라이저 부재 하부 투시 + 슬릿 투광 스트라이프
 4. deck_walk        — 지주 분절 + 개방 베이 교대 회랑 · 상판 유효고 5.25 m
 5. sidewalk_approach— 안내 사인이 **접근자를 마주보는지**(구 흑색 배면 패널
                       오독 제거) · 보도/연석/식재대로 '육교' 즉독
 6. overview         — 왕복 6차로·차선·양측 계단 접지·서측 킥플레이트 有 대조
 7. cue              — 점자띠 4개소·단코 황색 띠·연석/차선 재질 경계
 8. 경계·지평        — 식재대·가로수 열·원경 수목 띠로 양측 지평이 폐쇄됐나
 9. [v7] 강재 얼룩   — midlanding 참 상면·계단 스트링거가 **백·갈 고대비 얼룩**
                       이 아니라 도장 강판(중성 다크그레이 + 미세 발청)인가
                       (albedo add/brightness/desaturation 로 레인지 압축)
10. [v7] 수목 띠     — 배경 수목 띠가 **평평한 초록 슬래브 벽**이 아니라
                       상단이 톱니인 저채도 회록 수관 군락으로 읽히는가"""


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
    ROOT = "/World/Scene11"
    UsdGeom.Xform.Define(stage, ROOT)

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    st = PARAMS["stair"]
    E = PARAMS["east"]
    RUN, DROP = _flight_run(), _flight_drop()
    Z_MID = E["z_top"] - DROP

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *a, **kw):
        return sc.make_pbr(stage, path, *a, **kw)

    def PBR_ALBEDO(path, *a, albedo=None, **kw):
        """[v7 ruling (6)-1] make_pbr + the OmniPBR albedo range correction inputs.

        `scene_common.make_pbr` does not expose albedo_add/brightness/desaturation
        (and scene_common is shared by 21 scenes, so the rule is not to modify it).
        → here we only **add inputs** to the shader prim make_pbr created.
        By the OmniPBR.mdl definition (file lines 62 · 68 · 74) all three are float,
        and they apply in the order base::file_texture(color_offset=add,
        color_scale=brightness) → lerp(tint, mono, desaturation), i.e.
            diffuse = lerp(tex*brightness + add,  mono(...),  desaturation)
        so **the tonal range of the texture itself can be compressed** (a tint is a
        multiply and cannot narrow the range — the cause of the v6/v7 re-rulings).
        """
        mtl = sc.make_pbr(stage, path, *a, **kw)
        if albedo:
            from pxr import UsdShade, Sdf
            sh = UsdShade.Shader.Get(stage, path + "/Shader")
            for key in ("brightness", "add", "desaturation"):
                if key in albedo:
                    sh.CreateInput(f"albedo_{key}",
                                   Sdf.ValueTypeNames.Float).Set(
                        float(albedo[key]))
        return mtl

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
        # steel stairs and landings - [v7 ruling (6)-1] metal_rust is used only as **relief (normal,
        #   roughness)**, while the albedo range is compressed with add/brightness and the rust /
        #   bare-metal colour split is removed with desaturation -> a "painted steel sheet with local rust" look.
        M["metal"] = PBR_ALBEDO(f"{ROOT}/Looks/Metal",
                                sc.tex_path("metal_rust", "diff"),
                                sc.tex_path("metal_rust", "nor"),
                                sc.tex_path("metal_rust", "rough"),
                                s["metal_rust"], tint=mp["metal_tint"],
                                albedo=mp["metal_albedo"])
        M["concrete"] = PBR(f"{ROOT}/Looks/Concrete",
                            sc.tex_path("concrete_wall", "diff"),
                            sc.tex_path("concrete_wall", "nor"),
                            sc.tex_path("concrete_wall", "rough"),
                            s["concrete_wall"], tint=mp["concrete_tint"])
        M["soil"] = PBR(f"{ROOT}/Looks/Soil", sc.tex_path("grass", "diff"),
                        sc.tex_path("grass", "nor"),
                        sc.tex_path("grass", "rough"), 1.2,
                        tint=mp["soil_tint"])
        M["curb"] = PBR(f"{ROOT}/Looks/Curb",
                        sc.tex_path("granite_dark", "diff"),
                        sc.tex_path("granite_dark", "nor"),
                        sc.tex_path("granite_dark", "rough"), s["granite_dark"])
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
        M["band"] = PBR(f"{ROOT}/Looks/Band", diffuse_color=mp["band_color"],
                        roughness_const=mp["band_rough"])
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
        # [v6 C-3 family] avoids a textureless flat slab (styrofoam look) - a concrete texture.
        #   reused for the sign backing as well, to block the "pure-black floating panel" misreading.
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           sc.tex_path("concrete_wall", "diff"),
                           sc.tex_path("concrete_wall", "nor"),
                           sc.tex_path("concrete_wall", "rough"),
                           s["concrete_wall"], tint=mp["parapet_tint"])
        M["signback"] = PBR(f"{ROOT}/Looks/SignBack",
                            diffuse_color=(0.44, 0.45, 0.46),
                            metallic=0.25, roughness_const=0.55)
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["leaf_a"] = PBR(f"{ROOT}/Looks/LeafA", diffuse_color=mp["leaf_a"],
                          roughness_const=1.0, specular_level=0.0)
        M["leaf_b"] = PBR(f"{ROOT}/Looks/LeafB", diffuse_color=mp["leaf_b"],
                          roughness_const=1.0, specular_level=0.0)
        # [v7 ruling (6)-2] three low-saturation grey-greens for the distant tree band only (aerial perspective)
        for tag in ("a", "b", "c"):
            M[f"leaf_far_{tag}"] = PBR(
                f"{ROOT}/Looks/LeafFar{tag.upper()}",
                diffuse_color=mp[f"leaf_far_{tag}"],
                roughness_const=1.0, specular_level=0.0)
        M["nosing"] = PBR(f"{ROOT}/Looks/Nosing",
                          diffuse_color=mp["nosing_color"],
                          roughness_const=0.7)
        # [v5 shared layer] Korean sign panel - sign_info (footbridge guidance), uv_mode 1:1
        M["sign"] = PBR(f"{ROOT}/Looks/SignPanel",
                        diff=sc.tex_path("sign_info", "diff"),
                        uv_mode=True, roughness_const=0.6)
        return M

    # -------------------------------------------------------------------
    # site ground · roadway · sidewalk · kerb · lane lines
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
        for i, (xa, xb) in enumerate(((wk["xw0"], wk["xw1"]),
                                      (wk["xe0"], wk["xe1"]))):
            BOX(f"{ROOT}/Walk_{i}",
                ((xa+xb)/2.0, (wk["y0"]+wk["y1"])/2.0,
                 wk["z_top"] - wk["thick"]/2.0),
                (xb-xa, wk["y1"]-wk["y0"], wk["thick"]), M["paving"], col=True)
        cb = PARAMS["curb"]
        for i, xe in enumerate((rd["x0"], rd["x1"])):
            xc = xe - cb["w"]/2.0 if i == 0 else xe + cb["w"]/2.0
            BOX(f"{ROOT}/Curb_{i}",
                (xc, (wk["y0"]+wk["y1"])/2.0, cb["z_top"] - cb["thick"]/2.0),
                (cb["w"], wk["y1"]-wk["y0"], cb["thick"]), M["curb"], col=True)
        # [v6 ruling C-2] planting strip - one row on the outer sidewalk boundary (2 kerb lines + groundcover).
        vg = PARAMS["verge"]
        vy0, vy1 = vg["y0"], vg["y1"]
        for i, (xa, xb) in enumerate(((wk["xw0"] - vg["w"], wk["xw0"]),
                                      (wk["xe1"], wk["xe1"] + vg["w"]))):
            for j, xc in enumerate((xa + vg["curb_t"]/2.0,
                                    xb - vg["curb_t"]/2.0)):
                BOX(f"{ROOT}/VergeCurb_{i}_{j}",
                    (xc, (vy0+vy1)/2.0, vg["curb_top"] - 0.22),
                    (vg["curb_t"], vy1-vy0, 0.44), M["curb"], col=True)
            BOX(f"{ROOT}/VergeSoil_{i}",
                ((xa+xb)/2.0, (vy0+vy1)/2.0, vg["soil_top"] - 0.20),
                ((xb-xa) - 2*vg["curb_t"], vy1-vy0, 0.40), M["soil"], col=True)

    def build_lanes(M):
        ln = PARAMS["lane"]
        for i, x in enumerate(ln["center_xs"]):
            BOX(f"{ROOT}/CenterLine_{i}", (x, (ln["y0"]+ln["y1"])/2.0, ln["z"]),
                (ln["w"], ln["y1"]-ln["y0"], ln["t"]), M["line_y"])
        period = ln["seg"] + ln["gap"]
        ndash = int((ln["y1"] - ln["y0"]) / period)
        for j, x in enumerate(ln["dash_xs"]):
            for k in range(ndash):
                yc = ln["y0"] + k*period + ln["seg"]/2.0
                BOX(f"{ROOT}/Dash_{j}_{k}", (x, yc, ln["z"]),
                    (ln["w"], ln["seg"], ln["t"]), M["line_w"])
        # road band under the stair - the contrast surface catching the grating slit shadows
        # two road bands under the stairs (east/west symmetric) - contrast surface for the grating slit shadows
        bd = PARAMS["dress"]["band"]
        xc = (bd["x0"] + bd["x1"]) / 2.0
        for i, sgn in enumerate((1.0, -1.0)):
            BOX(f"{ROOT}/GratingBand_{i}", (sgn * xc, 0.0, bd["z"]),
                (bd["x1"]-bd["x0"], bd["y1"]-bd["y0"], bd["t"]), M["band"])

    # -------------------------------------------------------------------
    # deck + support piers
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # [W2-D] ground_kit - P9 bridge_deck on the footbridge deck.
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["steel"], crack=M["steel"], patch=M["concrete"],
                  patch_cut=M["steel"], stain_water=M["band"],
                  stain_drip=M["band"], wear=M["band"], edge_break=M["band"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", ground_plan(), M2,
                              skin_exclude=sc.skin_exclude)
        print(f"[ground_kit] scene11 P9 · 프림 {res['prims']} · "
              f"δmax {res['gt_delta_max']:.4f} · unit_cell {res['unit_cell']}")
        return res

    def build_deck(M):
        dk = PARAMS["deck"]
        # [W2-0 P-A] The deck is what ground_kit decorates. `_SKIN_DENY`
        #   already contains "deck", but the registration is explicit so the
        #   guarantee does not rest on a path token.
        sc.skin_exclude(f"{ROOT}/Deck")
        BOX(f"{ROOT}/Deck",
            ((dk["x0"]+dk["x1"])/2.0, (dk["y0"]+dk["y1"])/2.0,
             dk["z_top"] - dk["thick"]/2.0),
            (dk["x1"]-dk["x0"], dk["y1"]-dk["y0"], dk["thick"]),
            M["concrete"], col=True)
        dp = PARAMS["deck_posts"]
        z1 = dk["z_top"] - dk["thick"]
        for i, px in enumerate(dp["xs"]):
            CYL(f"{ROOT}/DeckPost_{i}", (px, dp["y"], (dp["z_bot"]+z1)/2.0),
                dp["r"], z1-dp["z_bot"], M["concrete"], col=True)
            BOX(f"{ROOT}/DeckCap_{i}",
                (px, dp["y"], z1 - dp["cap_h"]/2.0),
                (dp["cap_sx"], dp["cap_sy"], dp["cap_h"]), M["concrete"])

    # -------------------------------------------------------------------
    # one stair set (top landing -> A -> mid landing -> B). Serves local and world under prefix.
    #   x0_pad : west end of the top landing, everything after it descends in +X. kick = kickplate or not.
    # -------------------------------------------------------------------
    def build_stair_set(M, prefix, x0_pad, x1_pad, kick, tag):
        a0 = x1_pad
        a1 = a0 + RUN
        m1 = a1 + E["mid_len"]
        b1 = m1 + RUN
        py0, py1 = E["pad_y0"], E["pad_y1"]
        dk_t = PARAMS["deck"]["thick"]
        # top landing (steel deck as thick as the bridge deck)
        BOX(f"{prefix}/PadTop",
            ((x0_pad+x1_pad)/2.0, (py0+py1)/2.0, E["z_top"] - dk_t/2.0),
            (x1_pad-x0_pad, py1-py0, dk_t), M["metal"], col=True)
        # flight A (grating, open risers)
        sc.build_open_riser_stairs(
            stage, f"{prefix}/FlightA", a0, st["y0"], st["y1"], st["riser"],
            st["tread"], st["n"], E["z_top"], M["metal"], M["metal"],
            tread_t=st["tread_t"], gap=st["gap"], slits=st["slits"])
        # mid landing (steel deck + 4 support posts)
        BOX(f"{prefix}/MidLanding",
            ((a1+m1)/2.0, (py0+py1)/2.0, Z_MID - dk_t/2.0),
            (m1-a1, py1-py0, dk_t), M["metal"], col=True)
        for i, (lx, ly) in enumerate(((a1+0.30, py0+0.30), (a1+0.30, py1-0.30),
                                      (m1-0.30, py0+0.30), (m1-0.30, py1-0.30))):
            zt = Z_MID - dk_t
            CYL(f"{prefix}/MidPost_{i}", (lx, ly, (-0.30+zt)/2.0), 0.11,
                zt+0.30, M["metal"], col=True)
        # flight B
        sc.build_open_riser_stairs(
            stage, f"{prefix}/FlightB", m1, st["y0"], st["y1"], st["riser"],
            st["tread"], st["n"], Z_MID, M["metal"], M["metal"],
            tread_t=st["tread_t"], gap=st["gap"], slits=st["slits"])
        # non-slip nosing band
        if cfg["cue_nosing"]:
            for j, (bx, ztop) in enumerate(((a0, E["z_top"]), (m1, Z_MID))):
                sc.build_nosing(stage, f"{prefix}/Nosing_{j}", bx, st["y0"],
                                st["y1"], st["riser"], st["tread"], st["n"],
                                mtl=M["nosing"], width=0.06, proud=0.003,
                                z_top=ztop)
        # railing + kickplate
        if cfg["cue_railing"]:
            ra = PARAMS["rail"]

            def _gnd(bx, ztop):
                def f(x):
                    if x <= bx:
                        return ztop
                    if x >= bx + RUN:
                        return ztop - DROP
                    i = min(int((x - bx) / st["tread"]), st["n"] - 1)
                    return ztop - st["riser"] * (i + 1)
                return f
            for k, y in enumerate((st["y0"] + ra["y_inset"],
                                   st["y1"] - ra["y_inset"])):
                sc.build_railing_line(
                    stage, f"{prefix}/RailA_{k}", y, x0_pad, a0, RUN, DROP,
                    _gnd(a0, E["z_top"]), M["rail"], rail_h=ra["rail_h"],
                    post_r=ra["post_r"], spacing=ra["spacing"],
                    rail_r=ra["rail_r"], rail_mid_r=ra["rail_mid_r"],
                    rail_mid_drop=ra["rail_mid_drop"])
                sc.build_railing_line(
                    stage, f"{prefix}/RailB_{k}", y, a1, m1, RUN, DROP,
                    _gnd(m1, Z_MID), M["rail"], rail_h=ra["rail_h"],
                    post_r=ra["post_r"], spacing=ra["spacing"],
                    rail_r=ra["rail_r"], rail_mid_r=ra["rail_mid_r"],
                    rail_mid_drop=ra["rail_mid_drop"])
            # kickplate (toe board) - both sides of the mid landing. Its **absence** on the east side is the hazard.
            if kick:
                for k, ye in enumerate((py0, py1)):
                    BOX(f"{prefix}/Kick_{k}",
                        ((a1+m1)/2.0, ye, Z_MID + E["kick_h"]/2.0),
                        (m1-a1, 0.05, E["kick_h"]), M["rail"])
        # tactile bands at the stair head and foot
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            # [W2-D Sec.12.4] non-conforming variant for scene11 = bearing off
            #   by `skew_deg`. The band is pulled back by half_w*sin(skew) so
            #   that even the leading corner stops at the tread line - a skewed
            #   band that overhangs the first tread would be a GT change, not a
            #   mis-installation. skew_deg = 0 reproduces the old geometry.
            skew = float(tc.get("skew_deg", 0.0))
            hw = abs(st["y1"] - st["y0"]) / 2.0
            back = abs(math.sin(math.radians(skew))) * hw
            cy = (st["y0"] + st["y1"]) / 2.0
            for nm, x_in, ln, zb, sgn in (
                    ("TactileTop", a0, tc["pad_len"], E["z_top"], -1.0),
                    ("TactileLow", b1, tc["low_len"], 0.0, +1.0)):
                cx = x_in + sgn * (ln / 2.0 + back)
                sc._oriented_box(
                    stage, f"{prefix}/{nm}_{tag}",
                    (cx, cy, zb + (tc["proud"] - 0.01) / 2.0),
                    (ln, abs(st["y1"] - st["y0"]), tc["proud"] + 0.01),
                    M["tactile"], rotz=skew)
        return b1

    def build_east(M):
        return build_stair_set(M, f"{ROOT}/East", E["pad_x0"], E["pad_x1"],
                               E["kickplate"], 0)

    def build_west(M):
        """rot_group 180° — local (x,y) → world (−15 − x, −y). The local top landing is
        x −1.8…0 (= world −13.2…−15.0), and from there a local +X descent becomes a
        world −X descent. Geometry and fittings match the east side except that the
        **kickplate is present** (the code-compliant control)."""
        w = PARAMS["west"]
        RG = sc.build_rot_group(stage, f"{ROOT}/WestGroup", w["pivot"], w["rot"])
        pad_len = E["pad_x1"] - E["pad_x0"]
        return build_stair_set(M, RG, -pad_len, 0.0, w["kickplate"], 1)

    # -------------------------------------------------------------------
    # deck noise panels + longitudinal railing (cue_railing)
    # -------------------------------------------------------------------
    def build_deck_rails(M):
        """[v6 ruling (5)] noise railing — segmented by posts + alternating noise-panel /
        open bays. The old build (one unbroken panel) was the direct cause of the
        bunker corridor and of the pure-black shadow side (30~45 % of the frame).
        Even bays = noise panel (+ top cap), odd bays = open (a low kick band + 6
        vertical balusters), which lets light and sight through. GT-neutral (railing prims)."""
        dk = PARAMS["deck"]
        rb = PARAMS["rail_bay"]
        x0, x1 = dk["x0"], dk["x1"]
        nb = int(rb["n_bay"])
        L = (x1 - x0) / float(nb)
        zt = dk["z_top"]
        for i, ye in enumerate((dk["y0"], dk["y1"])):
            for k in range(nb + 1):                      # posts
                BOX(f"{ROOT}/DeckRailPost_{i}_{k}",
                    (x0 + k*L, ye, zt + rb["post_h"]/2.0),
                    (rb["post_t"], rb["post_t"], rb["post_h"]), M["steel"])
            for k in range(nb):
                xa = x0 + k*L + rb["post_t"]/2.0 + rb["joint"]
                xb = x0 + (k+1)*L - rb["post_t"]/2.0 - rb["joint"]
                xc, Lx = (xa + xb)/2.0, xb - xa
                if k % 2 == 0:                           # noise-panel bay
                    BOX(f"{ROOT}/DeckPanel_{i}_{k}",
                        (xc, ye, zt + dk["panel_h"]/2.0),
                        (Lx, dk["panel_t"], dk["panel_h"]), M["panel"])
                    BOX(f"{ROOT}/DeckPanelCap_{i}_{k}",
                        (xc, ye, zt + dk["panel_h"] + rb["cap_h"]/2.0),
                        (Lx, dk["panel_t"] + 2*rb["cap_over"], rb["cap_h"]),
                        M["rail"])
                else:                                    # open bay (see-through, light-through)
                    BOX(f"{ROOT}/DeckKick_{i}_{k}",
                        (xc, ye, zt + rb["kick_h"]/2.0),
                        (Lx, dk["panel_t"], rb["kick_h"]), M["panel"])
                    nbal = int(rb["n_baluster"])
                    bz0 = zt + rb["kick_h"]
                    bz1 = zt + dk["rail_z"] - 0.06
                    for b in range(nbal):
                        xb_ = xa + (b + 0.5) * Lx / float(nbal)
                        CYL(f"{ROOT}/DeckBal_{i}_{k}_{b}",
                            (xb_, ye, (bz0 + bz1)/2.0), rb["baluster_r"],
                            bz1 - bz0, M["rail"])
            CYL(f"{ROOT}/DeckRail_{i}",
                ((dk["x0"]+dk["x1"])/2.0, ye, dk["z_top"] + dk["rail_z"]),
                dk["rail_r"], dk["x1"]-dk["x0"], M["rail"], rotY=90.0)

    # -------------------------------------------------------------------
    # sign (cue_sign) - footbridge guidance sign_info
    # -------------------------------------------------------------------
    def build_signs(M):
        sg = PARAMS["sign"]
        for i, (sx, sy, yaw) in enumerate(sg["spots"]):
            sc.build_sign(stage, f"{ROOT}/Sign_{i}", sx, sy,
                          PARAMS["walk"]["z_top"], yaw, M["sign"],
                          w=sg["w"], h=sg["h"], pole_h=sg["pole_h"],
                          pole_mtl=M["pole"], back_mtl=M["signback"])

    # -------------------------------------------------------------------
    # dressing
    # -------------------------------------------------------------------
    def build_dressing(M):
        d = PARAMS["dress"]
        gz = PARAMS["walk"]["z_top"]
        sh = d["shelter"]
        sc.build_canopy(stage, f"{ROOT}/Shelter", sh["x0"], sh["x1"], sh["y0"],
                        sh["y1"], sh["z_roof"], sh["post_r"], M["panel"],
                        M["pole"], roof_t=0.10, base_z=gz)
        BOX(f"{ROOT}/ShelterBack",
            ((sh["x0"]+sh["x1"])/2.0, sh["y0"] + 0.10, gz + 1.10),
            (sh["x1"]-sh["x0"], 0.06, 2.20), M["glass"])
        # [v6 ruling (5)] 2 side walls + route-map panel - removes the "four-legged carport" misreading.
        for i, xe in enumerate((sh["x0"] + sh["side_inset"]/2.0,
                                sh["x1"] - sh["side_inset"]/2.0)):
            BOX(f"{ROOT}/ShelterSide_{i}",
                (xe, (sh["y0"]+sh["y1"])/2.0 - 0.35,
                 gz + sh["side_h"]/2.0),
                (sh["side_t"], (sh["y1"]-sh["y0"]) - 1.4, sh["side_h"]),
                M["glass"])
        BOX(f"{ROOT}/ShelterRoute",
            (sh["x0"] + 1.35, sh["y0"] + 0.20, gz + 1.55),
            (sh["route_w"], 0.05, sh["route_h"]), M["panel"])
        sc.build_bench(stage, f"{ROOT}/ShelterBench",
                       (sh["x0"]+sh["x1"])/2.0, sh["bench_y"], gz, M["wood"],
                       yaw=0.0)
        bx, by, bh = d["bus_pole"]
        CYL(f"{ROOT}/BusPole", (bx, by, gz + bh/2.0), 0.055, bh, M["pole"],
            col=True)
        BOX(f"{ROOT}/BusSign", (bx, by, gz + bh - 0.30), (0.06, 0.55, 0.55),
            M["panel"])
        lp = d["lamp"]
        for i, (lx, ly) in enumerate(d["lamps"]):
            base = f"{ROOT}/Lamp_{i}"
            CYL(f"{base}/Pole", (lx, ly, gz + lp["pole_h"]/2.0), lp["pole_r"],
                lp["pole_h"], M["pole"], col=True)
            sgn = 1.0 if lx < 0 else -1.0
            CYL(f"{base}/Arm", (lx + sgn*lp["arm_len"]/2.0, ly,
                                gz + lp["pole_h"] - 0.12),
                lp["arm_r"], lp["arm_len"], M["pole"], rotY=90.0)
            BOX(f"{base}/Head", (lx + sgn*lp["arm_len"], ly,
                                 gz + lp["pole_h"] - 0.18),
                (lp["head"]*1.5, lp["head"], 0.14), M["lamp"])
        # trees on the planting strip sit on the groundcover top (0.10), trees on the sidewalk on the paving.
        vsoil = PARAMS["verge"]["soil_top"]
        vx = PARAMS["walk"]["xe1"] + 0.001
        for i, (tx, ty) in enumerate(d["trees"]):
            tz = vsoil if abs(tx) >= vx else gz
            sc.build_tree(stage, f"{ROOT}/Tree_{i}", tx, ty, tz, M["wood"],
                          M["leaf_a"], M["leaf_b"])
        for i, (bx2, by2, yaw) in enumerate(d["benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{i}", bx2, by2, gz, M["wood"],
                           yaw=yaw)
        for i, (bx2, by2) in enumerate(d["bollards"]):
            sc.build_bollard(stage, f"{ROOT}/Bollard_{i}", bx2, by2, gz,
                             mtl=M["pole"])
        build_treeband(M)
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd, M["brick"],
                              M["glass"], M["parapet"],
                              window=PARAMS["window_by"].get(
                                  key, PARAMS["window"]))

    def build_treeband(M):
        """[v6 ruling C-2/C-4 · v7 ruling (6)-2] distant tree silhouette band.

        The v6 build (one solid box + one small blob per segment) was a **continuous
        plate with a flat top** and read as a "painted noise wall (green slab)". The
        structure is changed to two tiers.
          · lower box = the shrub layer below the canopy. Lowered to h·base_frac
            (0.36) so it **makes no silhouette** (excluded from skyline duty).
          · upper canopy = `blobs` overlapping oblate blobs per segment. Individual
            heights are scattered by a 0.72~1.16× jitter so the **top line is
            saw-toothed**, and x is shaken by ±x_jit to give fore/aft depth.
          · the material cycles three aerial-perspective low-saturation grey-greens
            by coordinate hash (prevents a flat monochrome slab).
        Grounding guarantee: blob centre z = gz + hj·0.62, rz = hj·0.42 →
          bottom = gz + hj·0.20 ≤ gz + h·0.36 = box top face (since hj ≤ 1.16 h,
          0.20·1.16 h = 0.232 h < 0.36 h). So **zero floating blobs**.
        Deterministic jitter (index hash) — reproducibility preserved."""
        tb = PARAMS["treeband"]
        import random as _random
        gz = PARAMS["ground"]["z_top"]
        far = (M["leaf_far_a"], M["leaf_far_b"], M["leaf_far_c"])
        nb = int(tb.get("blobs", 3))
        bf = float(tb.get("base_frac", 0.36))
        xj = float(tb.get("x_jit", 1.7))
        for r, (xa_, xb_, hh) in enumerate(tb["rows"]):
            n = max(2, int(round((tb["y1"] - tb["y0"]) / tb["seg"])))
            xc0 = (xa_ + xb_) / 2.0
            for k in range(n):
                ya = tb["y0"] + k * (tb["y1"] - tb["y0"]) / n
                yb = tb["y0"] + (k + 1) * (tb["y1"] - tb["y0"]) / n
                rnd = _random.Random((r * 7717) ^ (k * 3413))
                h = hh + rnd.uniform(-tb["jitter"], tb["jitter"])
                dx = rnd.uniform(-0.8, 0.8)
                BOX(f"{ROOT}/TreeBand_{r}_{k}",
                    (xc0 + dx, (ya+yb)/2.0, gz + h*bf/2.0),
                    ((xb_ - xa_) * rnd.uniform(0.8, 1.25), yb - ya + 0.6,
                     h * bf),
                    far[(k + r) % 3])
                # the canopy radius is based on **the band width** (not on height) - so that even a large
                #   height jitter cannot spread in x and encroach on the planting strip / street-tree row
                #   (x +-41.2). Maximum x spread = x_jit 1.2 + rx 1.9 = 3.1 m.
                rw = (xb_ - xa_) * 0.5
                for j in range(nb):
                    hj = h * rnd.uniform(0.72, 1.16)
                    rx = rw * rnd.uniform(0.55, 0.95)
                    sc.add_sphere(
                        stage, f"{ROOT}/TreeBlob_{r}_{k}_{j}",
                        (xc0 + rnd.uniform(-xj, xj),
                         ya + (j + 0.5) * (yb - ya) / nb
                         + rnd.uniform(-0.7, 0.7),
                         gz + hj * 0.62),
                        (rx, rx * rnd.uniform(0.90, 1.60), hj * 0.42),
                        far[(k + r + j + 1) % 3])

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_site(M)
    if cfg["cue_material_break"]:
        build_lanes(M)
    if cfg["hazard_stairs"]:
        build_deck(M)
        build_ground_kit(M)          # [W2-D] deck ground elements
        build_east(M)
        build_west(M)
        if cfg["cue_railing"]:
            build_deck_rails(M)
    if cfg["cue_sign"]:
        build_signs(M)
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene11_{ts}.png")
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
