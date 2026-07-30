# -*- coding: utf-8 -*-
"""
scene13_apartment_parking_entry.py — NegObs synthetic scene 13 (v5.1 R8):
underground car park entrance of an apartment estate (Isaac Sim 4.5)

Type    : T10 family redefined — the spiral parking ramp (old scene13, archive_v3) is
          dropped and replaced by a **straight underground car park entry ramp +
          an adjoining pedestrian stair**.
Spec    : Docs/audit_v4/user_feedback_v5_1.md §per-scene instructions, row 13 (R8),
          Docs/briefs/multi_scene_brief_v5.md (file structure · shared layers)
Shared  : scene_common.py (build_slope/build_straight_stairs/build_rot_group/
          build_canopy/build_planter/build_tree/build_building/build_sign/
          build_tactile/build_bollard) · follows scene16 (latest file structure)

[v5.1] Why it was replaced (user: "too much of a simulation look — base it on reality")
  The old scene13 was a spiral parking ramp standing alone above ground. No real estate
  has such a structure on its own. In a Korean apartment estate, the place where "cars
  disappear below grade" is almost always a **straight underground car park entry ramp**
  -> that gives both generality (every estate has one) and realism (dimensions and
  equipment are fixed by regulation).

Hazard
  Walking the estate sidewalk (z=0) you meet a 6 m wide ramp opening cutting into the
  ground. The ramp drops 3.96 m through transition 8.5% -> main 17% -> transition 8.5%,
  and **at robot eye height (h0.3) that descent vanishes in principle**: from d >= 3.5 m
  back from the near edge (x=0) the sight line grazes the deck at an angle
  (atan(0.3/d)) smaller than the ramp's initial slope angle (4.86 deg), so on screen the
  ramp deck compresses into a plane of the same brightness and material as the ground.
  Beyond that, the x >= 24 m stretch is roofed by the upper slab (surface planting), so
  **the ground beyond the opening (z=0) reads as continuous with the near sidewalk**
  -> a textbook negative obstacle.
  The guarding is a "below-code reality": the railing around the ramp opening has been
  removed on the south side over x 10.5~13.5 (3 m), and the adjoining stair shaft
  (depth 3.96) is left with bare coping and no railing.

[W3 S13 · G13] What the target image changed (ruling `w3_intake_v2_images.md` §7-5)
  U-5 ("지하 진입로는 캐노피를 진입로 끝까지") is read **real-practice**, not literally:
  G13 shows **no canopy over the ramp at all**. The approach is covered for its whole
  length by the **building slab over the portal** (already built: `garage.ceil_z = -1.2`
  from `portal.x = 24.0` eastward, with estate ground above it), and what spans the mouth
  is a **stainless gantry sign**. So the 5.8 m free-standing porch (a canopy over 24 % of
  the approach, which appears in **no** reference image) is **deleted** and replaced by
  `props_kit.build_gantry_sign` + the height-limit bar re-hung from it.
  Also from G13: yellow/black bands and a reflective guidance strip on the trench wall
  faces, yellow/black kerb blocks on the ramp cheeks, a yellow ramp centre line, a ginkgo
  street row at 8.0 m pitch, and the 보차도 kerb the footways never had (GT-5).

Goal
  (1) ground split into 6 boxes that **do not cover** the ramp trench opening
      (x 0..24, y +-3.3) or the stair shaft opening (x 5..11.2, y 3.3..6.9)
  (2) straight ramp in 3 segments (transition-main-transition) + side walls and coping +
      gantry sign over the mouth + barrier gate + height-limit bar + fee board
  (3) adjoining pedestrian stair, 24 steps (riser 0.165, width 1.4, 2 switchback flights
      + mid landing) -> basement corridor -> basement 1 car park (dim lighting — PT assumed)
  (4) statutory bollards (h0.9 · r0.08 · spacing 1.5 · reflective top band) + 0.3 m dot
      tactile in front — **only at the sidewalk/road crossing points**
  (5) estate dressing: interlocking sidewalks · planting beds · trees (build_tree v2) ·
      hedges · 3 apartment blocks (base_z · inset windows)

Walking-continuity self-check table (surface -> stair -> basement -> ramp -> surface; step <= 0.165)
  ┌ #  section                 coord (x, y, z)        step / verdict
  │ 0  estate north sidewalk   (13.0,  8.20,  0.000)      flat (interlocking)
  │ 1  stair spur sidewalk     (12.4,  5.50,  0.000)      flat
  │ 2  tactile warning band    (11.65, 4.25,  0.004)      0.004 (cue_tactile)
  │ 3  stair head (open edge)  (11.20, 4.25,  0.000)      ← **drop 3.96, no railing**
  │ 4  tread 1                 (11.05, 4.25, -0.165)      0.165
  │ 5  tread 12                ( 7.75, 4.25, -1.980)      0.165 x 11
  │ 6  mid landing (180 turn)  ( 6.40, 5.10, -1.980)      flat (x 5.25..7.6)
  │ 7  tread 13                ( 7.75, 5.95, -2.145)      0.165
  │ 8  tread 24                (11.05, 5.95, -3.960)      0.165 x 11
  │ 9  basement corridor       (12.00, 5.95, -3.960)      flat (headroom 2.76)
  │10  car park entry          (24.50, 5.95, -3.960)      flat
  │11  ramp foot merge         (26.89, 0.00, -3.960)      flat
  │12  ramp main climb         (23.29, 0.00, -3.654)      grade 8.5%
  │13  ramp top transition     ( 3.60, 0.00, -0.306)      grade 17%
  └14  back to surface road    ( 0.00, 0.00,  0.000)      grade 8.5% -> flat
  * Stair drop (24 x 0.165 = 3.96) = ramp drop -> both routes land on the same
    basement 1 floor (-3.96) (auto-checked in the smoke run).

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene13_apartment_parking_entry.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python scene13_apartment_parking_entry.py
Smoke (no boot):          NEGOBS_SMOKE=1  python scene13_apartment_parking_entry.py

Coordinates: Z-up, m, travel axis +X (estate sidewalk -> ramp descent). **Drop start edge x=0.**
  surface z=0, basement 1 floor z=-3.96, upper slab underside z=-1.2.
  **Footway top z=+0.150** (GT-5) — the four `walk_*` plates and the two crossing
  turn-down ramps; carriageway datum stays z=0.
  Sun: SUN_AZ_OFFSET=171.5 (default for every scene).
"""

import os
import sys
import math
import json
import datetime

import scene_common as sc
import ground_kit as gk
import infra_kit as ik
import props_kit as pk


# ===========================================================================
# [A] SCENE_CONFIG — standard 7 keys. Only hazard_stairs toggles geometry (openings filled).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False -> ramp · stairs · basement become flat z=0 (sole geometry toggle)
    "cue_railing":        True,   # railing around the ramp opening (south 3 m always missing) + around the shaft
    "cue_tactile":        False,  # [v5.2 user] tactile paving is rare in reality — OFF by default (path kept for ablation)   # [v5 shared] urban practice — dot tactile in front of bollards and at stair head/foot
    "cue_material_break": True,   # sidewalk interlocking vs ramp/stair concrete. False -> all sidewalk paving
    "cue_sign":           True,   # [v5.2 user] arbitrary warning signs removed — only the fee board (sign_info)
    "cue_scene_dressing": True,   # planters · trees · hedges · benches · lamps · 3 apartment blocks
    "cue_nosing":         False,  # True -> non-slip nosing bands (weak by custom on basement stairs)
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
_RISER = 0.165
_NSTEP = 24                        # 12 steps x 2 flights (switchback)
_DROP = round(_RISER * _NSTEP, 4)  # 3.96 = basement 1 floor
_FLOOR_Z = -_DROP

PARAMS = dict(
    # --- Ramp (straight, width 6) : transition 3.6@8.5% -> main @17% -> transition 3.6@8.5% ---
    #     Parking Lot Act Enforcement Rule, table: straight ramp grade <=17%, 2-lane
    #     width >=6 m, transitions top and bottom (half grade · 3.6 m) — all practice values.
    ramp=dict(y0=-3.0, y1=3.0, drop=_DROP, thick=0.6,
              trans_run=3.6, trans_grade=0.085, main_grade=0.17,
              seg_margin=0.10),
    # --- Trench side walls (retaining wall) + top coping ---
    wall=dict(thick=0.3, z_bot=-4.4, z_top=0.0,
              cope_over=0.06, cope_h=0.12),
    # --- Basement structure: upper slab underside = ground plate bottom (-1.2) ---
    #     Portal (east end of the surface opening) x=24.0 -> deck -3.714 -> headroom 2.514
    #     (posted height limit 2.3 < actual — the customary real-world margin)
    portal=dict(x=24.0, head_clear=2.3),
    garage=dict(x0=24.0, x1=38.0, y0=-9.3, y1=9.3, floor_z=_FLOOR_Z,
                floor_thick=0.8, wall_t=0.3, ceil_z=-1.2),
    # --- Adjoining pedestrian stair (2 switchback flights) : shaft x 5.0..11.2, y 3.3..6.9 ---
    stair=dict(riser=_RISER, tread=0.30, n_flight=12, width=1.4,
               x_head=11.2, x_turn=7.6, land_x0=5.25,
               y_a0=3.55, y_a1=4.95,          # flight 1 (descending -X)
               y_b0=5.25, y_b1=6.65,          # flight 2 (descending +X)
               mid_z=-1.98, base_z=-4.4),
    shaft=dict(x0=5.0, x1=11.2, y0=3.3, y1=6.9, wall_t=0.25),
    # --- Basement corridor (stairs -> garage) ---
    corridor=dict(x0=11.2, x1=24.0, y0=5.25, y1=6.65, wall_t=0.25,
                  floor_z=_FLOOR_Z, floor_thick=0.6, ceil_z=-1.2),
    # --- Ground (estate surface) : 6 boxes leaving the 2 openings clear ---
    ground=dict(x0=-34.0, x1=46.0, y0=-26.0, y1=26.0, z_top=0.0, thick=1.2),
    # --- Paving overlay (proud of the ground) ---
    drive=dict(x0=-14.0, x1=0.0, flare_x0=-6.0, flare_y=4.2, proud=0.004),

    # ═══ [W2 ground_kit] P7 ramp_parking — 2 statutory gaps closed (spec §5.5) ═══
    #  * 13-1 **ramp kerbs both sides h0.12 · w0.30** = Parking Lot Act Enforcement Rule §6(1)5(c).
    #    Not cosmetic: **a drop line that ought to exist is missing**.
    #    Supervisor approved M4 — GT changes go to W4, but **this one runs in W2** (pre-approved).
    #    -> the W2 output gains **1 unlabelled drop**. It is recorded via `gt_changes`
    #      and reclaimed by the W4 GT drop map (§6.4 · §9.2 step 7).
    #  * 13-2/3/5/6 ramp deck elements are **d2 only** `[computed — §5.0 C-2]`:
    #    the crest grazing ray slope h/d must exceed the 0.085 transition grade for the
    #    deck to be visible -> d2 (0.150) visible · d5 (0.060) · d10 (0.030) **hidden**.
    #    The main filler for the 3 shots moves to the **entry asphalt x −14…0** (13-8).
    gkit=dict(
        region=(-14.0, -3.3, 0.6, 3.3),
        curb=dict(h=0.12, width=0.30),        # touches the walls (y=+-3.0) -> road-side face +-2.70
        #  13-3 entry storm-water cut-off (d2 only).
        #  * [W2 pre-check · row-axis correction] 0.35 -> **0.52**. The trench frame
        #    half-width is 0.19 m, so the near end sat at crest +0.16 m, and the d2 row
        #    separation was 18.1 rows @1080 = **9.1 rows @540**. GT-E2's guidance strength is
        #    `(GRAZE_HW 3 + SMOOTH 3 + SLACK 2)x2 = 16 rows`, but those constants are on the
        #    GRAZE working axis (960x540), so **16 @540 = 32 @1080** is the canonical figure
        #    (red team G-1). Pushing the near end to +0.33 m gives 34.7 @1080 = **17.4 @540**
        #    `[computed]`. Beyond the crest nothing changes, so C-2 (ramp deck d2 only) holds.
        trench_entry=0.52,
        trench_sump=23.4,                     # 13-4 sump at the ramp foot (mise-en-scene)
        #  13-8 one manhole — **d5 window**. y=0 because at the far end of d5's W1 (X=1.1 m)
        #  the frame half-width is only 0.64 m, so y=1.6 falls off screen `[computed — 0.5774·X]`.
        #  x=−3.90 dodges both the DriveLine dashes (i=3 −6.05…−4.55 / i=4 −3.45…−1.95)
        #  and the tyre polish bands (|y| 0.575…1.125) -> zero Z-fighting.
        manhole_d5=(-3.90, 0.00),
        #  13-5 **[W3 S13 · G13] the two white ramp edge lines are DELETED.** G13's ramp
        #  carries one **yellow centre line** and nothing else; the two white boundary
        #  lines at y=+-2.40 are not in the image and not in Korean ramp practice (the
        #  2-lane ramp is divided, not edge-marked). The centre line is scene-owned
        #  (`ramp_line`) because a `gkit` marking is a flat plate at plan z and cannot
        #  ride the 8.5 %/17 % deck.
        lane_lines=[],
        #  [W3 S13] GD patch 2 -> 1 (intake §2 scene13 (e)). The remaining patch is a
        #  contractor **saw-cut asphalt patch on the asphalt approach**, which the user's
        #  rectangle ban explicitly exempts; a second one reads as the "지저분한" N2 case.
        patch_n=1,
        groove=(3.6, -3.0, 20.4, 3.0),        # 13-2 grooving — delegated to T1 stripes
        tactile_bollard=(-2.90, 4.35, -1.40, 4.65),   # §12.4 sidewalk part only
    ),
    # ═══ [W3 GT-5] footway 150 mm — proud 0.007 (a 3 mm step) → a real kerb step ═══
    #  All four walk plates rise together. GT-5 names walk_north/walk_south only; raising
    #  those two alone would leave a **143 mm step** where walk_cross and walk_spur join
    #  them (ledger §7 watch item W2), which is a new unlabelled drop on a walked route.
    #  The two crossing arms that meet the carriageway (CrossN1 / CrossS1) become
    #  **turn-down ramps** (4.9 % / 4.6 %) instead of plates, so the 146 mm step at the
    #  driveway edge does not exist either. See `hazard_registry()`.
    walk_cross=dict(x0=-3.2, x1=-1.2, y_far=16.0, proud=0.150),   # sidewalk crossing the ramp
    walk_north=dict(y0=7.2, y1=9.2, x0=-14.0, x1=30.0, proud=0.150),
    walk_spur=dict(x0=11.4, x1=14.4, y0=3.3, y1=7.2, proud=0.150),
    walk_south=dict(y0=-9.4, y1=-7.4, x0=-14.0, x1=30.0, proud=0.150),
    walk_plate_t=0.12,                 # buried depth below the plate top (top = z + proud)
    #  The spur is widened 2.0 → 3.0 m in x so its turn-down can be 2.0 m long: at the
    #  old 1.0 m the ramp toward the stair head would have been **15 %**, which is not a
    #  pedestrian approach. 0.150 / 2.0 = 7.5 % ≤ 1/12.
    spur_ramp=dict(x0=11.4, run=2.0),  # spur turn-down toward the stair head (−X)
    # ═══ [W3 GT-5 · K5] 보차도 경계석 — infra_kit.build_curb_line ═══
    #  1 m precast units · R10 top arris via the `curb` look class (0 prims) · no L-gutter
    #  (the kerb faces a planted verge, not a carriageway pan — `build_gutter_L` would
    #  invent a road gutter where there is no road), so **gt_drop = height = 0.150**.
    curb=dict(height=0.150, width=0.20, unit=1.0, embed=0.20, joint_w=0.006,
              arris="look", arris_r=0.010, far_unit=8.0,
              lod_span=(8.0, 28.0),    # arc length from x=-14 → the judged window x −6…14
              drop_h=0.020, drop_taper=1.0),
    # --- Statutory bollards (per Enforcement Rule of the Act on Promotion of Mobility Convenience for the Mobility Impaired, Table 2) ---
    #     h0.9 · r0.08 · spacing 1.5 · reflective top band · 0.3 m dot tactile in front.
    #     Placed **only where vehicles might intrude** = the 2 sidewalk/road crossings.
    bollard=dict(h=0.9, r=0.08, gap=1.5, band_h=0.09, band_z=0.74,
                 band_r=0.086),
    bollard_rows=[dict(y=4.35, xs=(-2.9, -1.4), tac_y0=4.35, tac_y1=4.65),
                  dict(y=-4.35, xs=(-2.9, -1.4), tac_y0=-4.65, tac_y1=-4.35)],
    # --- [W3 S13 · G13] Gantry sign over the mouth + height-limit bar + barrier gate ---
    #  The porch canopy (x −1.6…4.2, 5.8 m of a 24 m approach) is DELETED — ruling §7-5.
    #  Posts stand on solid ground at |y| = 3.55, i.e. 40 mm clear of the trench coping
    #  outer face (3.36) and outside the 6 m traffic envelope; the panel spans the mouth.
    #  `clear_h` is the **structural** clearance under the panel; the posted limit is the
    #  2.30 m bar hung from the same frame (Korean practice puts both at the mouth).
    #  `clear_h` 3.05 `[measured, pilot 260730_w3_s13]`: at 4.00 the panel sat **above**
    #  `entry_approach`'s frame top (z 3.81 at the gantry plane for eye 1.55 → tgt −0.50,
    #  vertical half-angle 18.0° at 16:9), i.e. the scene's identity element rendered
    #  off-frame. 3.05 m clear over a ramp whose posted limit is 2.30 m is also the
    #  ordinary Korean estate figure; G13's ≈4.5 m belongs to a shopping-mall portal.
    #  Fixed by geometry, not by moving the camera (R17-1 doctrine).
    gantry=dict(x=0.40, y0=-3.55, y1=3.55, clear_h=3.05,
                post_w=0.30, panel_h=0.80, panel_t=0.12),
    height_bar=dict(x=0.40, z=2.30, r=0.09, y0=-3.2, y1=3.2, nseg=8,
                    hanger_t=0.05, hang_y=2.95),
    # --- [W3 S13 · G13] wall-face safety graphics on the trench cheeks ---
    #  Bands sit on the **inner** wall faces (y = ±3.0) where the deck has dropped far
    #  enough to expose them; scene13's cheeks are flush-coped by design (the below-code
    #  reality this scene exists to carry), so there is no above-ground parapet to paint.
    chevron=dict(xs=(8.0, 12.0), width=1.20, height=0.55, n=6, stripe_t=0.006,
                 dz=(0.45, 0.58)),      # band centre above the deck, per xs entry
    wall_strip=dict(x0=7.0, x1=23.294, dz=0.60, h=0.08, t=0.014),
    # --- [W3 S13 · G13] ramp deck markings (scene-owned: they must ride the slope) ---
    ramp_line=dict(x_start=0.85, half_w=0.075, proud=0.004, thick=0.02),
    kerb_stripe=dict(x0=0.90, x1=3.60, unit=0.45, thick=0.03, proud=0.006),
    gate=dict(x=2.2, y=3.15, box=(0.34, 0.30, 1.00), base_z=0.12,
              arm_r=0.05, arm_z=0.97, arm_y0=-2.6, arm_y1=3.0, nseg=7),
    # --- Signs (cue_sign) ---
    sign_info=dict(cx=-1.1, cy=4.75, yaw=170.0, w=0.9, h=0.7, pole_h=2.2),
    # [v5.2 user] arbitrary warning signs removed — stair-caution sign (sign_step) deleted.
    # --- Railing (cue_railing) : sits **on** the opening coping (base_z = coping top).
    #     On the south side x 10.5~13.5 has been removed (a below-code reality).
    #     c = coping centreline = wall centreline (trench +-3.15 / shaft N 6.775 · W 5.125)
    rail=dict(h=0.95, post_r=0.03, rail_r=0.028, mid_r=0.018, mid_h=0.46,
              spacing=1.45, base_z=0.12),
    rail_runs=[dict(axis="x", c=-3.15, a0=0.0,  a1=10.5),
               dict(axis="x", c=-3.15, a0=13.5, a1=24.0),   # ← 10.5~13.5 missing
               dict(axis="x", c=3.15,  a0=3.2,  a1=5.0),    # from the east side of the gate box
               dict(axis="x", c=3.15,  a0=11.2, a1=24.0),
               dict(axis="x", c=6.775, a0=5.0,  a1=11.2),
               dict(axis="y", c=5.125, a0=3.3,  a1=6.9)],
    # --- Tactile paving (cue_tactile) ---
    tactile=dict(depth=0.30, proud=0.004,
                 head_x0=11.5, head_x1=11.8,        # warning band at the stair head
                 foot_x0=11.25, foot_x1=11.55),     # warning band at the basement landing
    # --- Dressing (irregular placement: no even spacing or grids, yaw jitter) ---
    #  [W3 S13 · GT-5] `(4.3, −8.9)` sat **inside** walk_south (y −9.4…−7.4); at proud
    #  0.007 that was invisible, at 0.150 the bed would be sunk 150 mm. Moved clear.
    #  Planter trees are placed by the scene (not by `build_planter`) so they can carry
    #  `species=` — `build_planter` has no species argument and would fall back to the
    #  `SCENE_SPECIES` row, making the scene two-species (K4(b) S-1 forbids that).
    planters=[dict(cx=-8.6, cy=6.4, size=3.4, tree=True),
              dict(cx=-12.9, cy=-5.2, size=2.8, tree=True),
              dict(cx=16.8, cy=10.9, size=3.8, tree=True),
              dict(cx=4.3, cy=-11.4, size=3.0, tree=True),
              dict(cx=27.4, cy=-6.1, size=3.2, tree=False)],
    planter=dict(curb_h=0.42, curb_t=0.22, cap_over=0.05, cap_h=0.05,
                 grass_h=0.38),
    # [W3 S13 · K4(b)] **G13's ginkgo street row.** Two monospecific rows at the library
    #  pitch `TREE_PITCH_M = 8.0`, one each side of the estate footway, replacing eight
    #  scattered specimens. Species: see `TREE_SPECIES` below.
    tree_rows=[dict(y=9.55, x0=-12.0, n=6), dict(y=-9.75, x0=-12.0, n=6)],
    tree_pitch=8.0,
    #  `[measured, pilot 260730_w3_s13]` 4.70 (≈ 7.5 m) put a `Fraxinus` crown mass over
    #  the whole beauty cut; a Korean estate 가로수 is 5–7 m and pruned narrow. 3.90 →
    #  target 3.90 × 1.60 ≈ **6.24 m**. Both rows stay at |y| ≥ 9.55, i.e. beyond
    #  CANOPY_TUNNEL_RECIPE's `d_min_broadleaf` 7.50 from the judged y = 0 axis (H16).
    tree_trunk_h=3.90,                 # → target height 3.90 × 1.60 ≈ 6.2 m (street row)
    hedges=[(-22.0, 6.9, -14.6, 7.5), (14.2, -6.9, 21.3, -6.3),
            (2.4, 12.2, 9.6, 12.8)],
    # (bx, by, yaw, base_z) — bench 0 stands on walk_north, which is now at +0.150
    benches=[(-9.4, 8.3, 174.0, 0.150), (17.3, 12.6, -6.0, 0.0),
             (-13.6, -7.1, 3.0, 0.0)],
    # [W3 S13 · G13] mid-rise-street backdrop signature: utility pole + transformer +
    #  overhead spans. Backdrop only — outside every judged near-ground cone.
    poles=[(-6.0, 11.6, True), (18.0, 11.6, False)],
    pole=dict(h=9.0, r=0.11, arm_len=1.8, arm_t=0.09, arm_zs=(8.10, 7.50),
              tr_r=0.28, tr_h=0.90, tr_z=6.60, wire_r=0.018, sag=0.35, seg=3,
              wire_ys=(-0.75, 0.0, 0.75)),
    streetlights=[(-7.2, 6.95), (12.6, 7.05), (26.9, -7.2)],
    streetlight=dict(pole_h=5.2, pole_r=0.075, arm_len=1.0, arm_r=0.045,
                     head=0.26),
    # 3 apartment blocks — facade inset windows (build_building). base_z=0 (surface plinth)
    buildings=dict(
        A101=dict(x0=34.0, x1=46.0, y0=-15.0, y1=7.4, h=45.0, floors=15,
                  axis="x", facade_x=34.0, face_dir=-1.0, base_z=0.0),
        A102=dict(x0=30.5, x1=42.0, y0=13.6, y1=25.0, h=39.0, floors=13,
                  axis="x", facade_x=30.5, face_dir=-1.0, base_z=0.0),
        A103=dict(x0=-46.0, x1=-34.0, y0=-20.0, y1=11.5, h=42.0, floors=14,
                  axis="x", facade_x=-34.0, face_dir=1.0, base_z=0.0),
    ),
    window=dict(w=1.3, h=1.5, inset=0.15, col_step=2.7, margin=2.2),
    # Basement garage interior (dim emission — PT assumed)
    garage_cols=[(27.5, -5.6), (27.5, 2.4), (32.4, -5.6), (32.4, 2.4),
                 (35.8, 6.2)],
    garage_col=dict(size=0.55),
    garage_lights=[(26.0, 0.0), (30.5, 4.4), (34.5, -3.2), (30.0, -7.4)],
    corridor_lights=[(14.0, 5.95), (18.5, 5.95), (22.5, 5.95)],
    garage_lamp=dict(size=(1.2, 0.24, 0.06), z=-1.28),
    park_lines=[(26.6, -8.4), (29.3, -8.4), (32.0, -8.4), (34.7, -8.4)],
    park_line=dict(w=0.12, len=5.0, z_off=0.006),

    material=dict(
        scale=dict(paving_interlock=1.2, concrete_floor=1.0,
                   concrete_wall=1.4, grass=1.4, tactile=0.3, plaster=2.4,
                   marble_light=1.1),
        # [W3 GT-5 · K5 3.] the kerb binds a **curb-class** material (path token `Curb`
        #   → LOOK_CLASS["curb"], bevel 10 mm = the R10 arris `arris="look"` relies on).
        #   S06-B item 3's `curb_granite_light` role is not authored (procurement HOLD),
        #   so `marble_light` is the stand-in — the same one scene02/CB-7 bound — and
        #   `granite_dark` stays forbidden on a kerb.
        curb_tint=(0.80, 0.79, 0.76),
        # stainless gantry (STS304 hairline) — brighter and flatter than the tube railing
        gantry_color=(0.72, 0.735, 0.75), gantry_metallic=0.85, gantry_rough=0.30,
        # ramp centre line — Korean ramp practice is a YELLOW divider, not white edge lines
        line_y_color=(0.72, 0.60, 0.10), line_y_rough=0.58,
        grass_tint=(0.52, 0.63, 0.40),
        grass_tint_b=(0.47, 0.60, 0.37),        # planter grass (+-5% tint jitter)
        paving_tint=(0.86, 0.85, 0.83),
        conc_tint=(0.80, 0.79, 0.77),
        wall_tint=(0.74, 0.73, 0.71),
        wall_tint_b=(0.70, 0.70, 0.69),
        # [v6 judgment (5)] asphalt = an untextured dark navy slab (40~60 % of frame) ->
        #   **aggregate texture (gravel diff/nor/rough) + a neutral grey-black tint**.
        #   gravel diff average ~0.45 x tint 0.21 ~ 0.095 (top of the sRGB rule band),
        #   B is set below R to kill the blue cast (the old colour had B > R = the navy).
        asphalt_color=(0.135, 0.135, 0.145), asphalt_rough=0.88,  # (kept, unused)
        asphalt_tint=(0.215, 0.210, 0.198), asphalt_scale=0.35,
        # Tyre polish bands — wheel tracks where the aggregate is pressed dark and smooth
        polish_color=(0.048, 0.047, 0.044), polish_rough=0.46,
        paint_color=(0.70, 0.70, 0.66), paint_rough=0.62,   # no pure white (<0.8)
        rail_color=(0.66, 0.68, 0.70), rail_metallic=0.7, rail_rough=0.42,
        bollard_color=(0.30, 0.31, 0.33), bollard_metallic=0.4,
        bollard_rough=0.5,
        band_color=(0.72, 0.72, 0.70), band_rough=0.35,     # reflective band (below pure white)
        cope_color=(0.62, 0.62, 0.60), cope_rough=0.65,
        wood_color=(0.28, 0.19, 0.12), wood_rough=0.85,
        glass_color=(0.055, 0.075, 0.10), glass_rough=0.08,
        parapet_color=(0.60, 0.60, 0.58), parapet_rough=0.62,
        shell_tint=(0.86, 0.84, 0.80), shell_tint_b=(0.80, 0.79, 0.78),
        # [v6 C-3] canopy slab = a 6x5 m untextured white board (styrofoam carport) ->
        #   concrete texture + fascia band + soffit lights.
        roof_color=(0.42, 0.42, 0.44), roof_rough=0.60,   # (kept, unused)
        roof_tint=(0.78, 0.77, 0.75), roof_scale=1.6,
        fascia_tint=(0.60, 0.60, 0.58), fascia_scale=0.8,
        post_color=(0.36, 0.36, 0.38), post_metallic=0.35, post_rough=0.5,
        lamp_color=(0.78, 0.78, 0.74), lamp_rough=0.4,
        # dark constant colour (sRGB albedo 0.02~0.06 rule)
        dark_color=(0.035, 0.035, 0.040), dark_rough=0.7,
        warn_y=(0.72, 0.58, 0.06), warn_r=(0.52, 0.10, 0.09),
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        # dim basement emission (PT 8 bounces assumed — negligible in RT)
        emit_color=(0.85, 0.87, 0.80), emit_intensity=340.0,
        sign_back_color=(0.05, 0.05, 0.055), sign_back_rough=0.5,
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
# [C] Path constants + required texture roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene13")

ASSET_ROLES = ["paving_interlock", "concrete_floor", "concrete_wall",
               "grass", "tactile", "plaster",
               "gravel",                     # [v6 (5)] asphalt aggregate texture
               "marble_light",               # [W3 GT-5] kerb stand-in (curb look class)
               "sign_info", "hdri", "mdl"]   # [v5.2 user] arbitrary warning signs removed

# [W3 S13 · K4(b)] **Species declaration — recorded honestly.**
#   G13 shows a ginkgo (은행나무) street row. The vegetation library holds **no ginkgo**:
#   `Docs/CREDITS.md:110` and `w3r_asset_map_v1.md:679` both record 0 hits for
#   `ginkgo`/`maidenhair` across 275,368 asset keys. `SCENE_SPECIES["Scene13"]` is
#   `("birch", None)`, and `Gray_Birch`'s white bark is the one silhouette a Korean
#   street row never has, so the scene **declares its own species at the call site** —
#   which is exactly the hand-over `scene_common`'s SCENE_SPECIES block documents
#   ("a scene gets its ... species only by passing `species=` explicitly").
#   `ash` = `Trees/Fraxinus.usd`, the library's `street_broadleaf` role and the species
#   scene11 (arterial sidewalk) already uses. It is a **form surrogate**, not a ginkgo:
#   the fan leaf is not reproducible without procurement and is not claimed here.
TREE_SPECIES = "ash"


# ===========================================================================
# [C2] Ramp longitudinal profile — transition / main / transition (single source of truth)
# ===========================================================================
def ramp_profile():
    """Returns: (segs, total_run)
      segs = [(x0, z0, run, drop), ...]  — same convention as build_slope's arguments
      (z0 = deck z at the segment top, descending by drop toward +X)"""
    rp = PARAMS["ramp"]
    t_run = float(rp["trans_run"])
    t_drop = t_run * float(rp["trans_grade"])
    main_drop = float(rp["drop"]) - 2.0 * t_drop
    main_run = main_drop / float(rp["main_grade"])
    segs = [(0.0, 0.0, t_run, t_drop),
            (t_run, -t_drop, main_run, main_drop),
            (t_run + main_run, -(t_drop + main_drop), t_run, t_drop)]
    return segs, 2.0 * t_run + main_run


def ramp_z(x):
    """Ramp deck z(x). 0 outside the opening (x<0), floor level past the bottom."""
    segs, total = ramp_profile()
    if x <= 0.0:
        return 0.0
    if x >= total:
        return -float(PARAMS["ramp"]["drop"])
    for x0, z0, run, drop in segs:
        if x <= x0 + run + 1e-9:
            return z0 - drop * (x - x0) / run
    return -float(PARAMS["ramp"]["drop"])


# ===========================================================================
# [C2b] W3 GT-5 derivations — kerb lines, crossing turn-downs, hazard registry.
#       Every number the GT-5 landing record quotes is produced HERE, from PARAMS,
#       so the record is a measurement and not a restatement (scene02/CB-7 precedent).
# ===========================================================================
def curb_lines():
    """The four kerb face lines: `(tag, p0, p1, road_side, drop_spans)`.

    `road_side` names the side the **carriageway/verge** is on; the block body extends
    `width` the other way, i.e. under the footway plate, so the kerb top is flush with
    the footway and the 150 mm face is exposed to the verge (`infra_kit._line_frame`
    convention: for a +X run the left normal is +Y).

    `drop_spans` are 턱낮춤 in **arc length from `p0`** (= `x + 14`) wherever another
    footway plate abuts the line — the kerb must not wall off a footway-to-footway
    junction. `walk_cross` meets both long walks at `x −3.2…−1.2` (s 10.8…12.8) and
    `walk_spur` meets `walk_north`'s inner line at `x 11.4…13.4` (s 25.4…27.4).
    """
    wn, ws, wc, wsp = (PARAMS["walk_north"], PARAMS["walk_south"],
                       PARAMS["walk_cross"], PARAMS["walk_spur"])
    x0, x1 = wn["x0"], wn["x1"]
    s_c = (wc["x0"] - x0, wc["x1"] - x0)          # crossing arm, arc length
    s_s = (wsp["x0"] - x0, wsp["x1"] - x0)        # spur, arc length
    return (("N_in",  (x0, wn["y0"]), (x1, wn["y0"]), "right", (s_c, s_s)),
            ("N_out", (x0, wn["y1"]), (x1, wn["y1"]), "left",  (s_c,)),
            ("S_in",  (x0, ws["y1"]), (x1, ws["y1"]), "left",  (s_c,)),
            ("S_out", (x0, ws["y0"]), (x1, ws["y0"]), "right", (s_c,)))


def curb_kwargs():
    """`build_curb_line` keyword set, in one place so scene and self-check cannot drift."""
    cu = PARAMS["curb"]
    return dict(height=cu["height"], width=cu["width"], unit=cu["unit"],
                arris_r=cu["arris_r"], arris=cu["arris"],
                gutter=False,                     # verge-side kerb — no carriageway pan
                z_road=PARAMS["ground"]["z_top"],
                walk_z=PARAMS["walk_north"]["proud"],
                embed=cu["embed"], joint_w=cu["joint_w"],
                drop_h=cu["drop_h"], drop_taper=cu["drop_taper"],
                lod_span=cu["lod_span"], far_unit=cu["far_unit"],
                collider=True, strict=True)


def cross_ramps():
    """The two driveway turn-downs, `(tag, pivot, rot, x0_local, z0, run, drop, y0, y1)`.

    `walk_cross`'s two road-facing arms are built as **ramps**, not plates: the footway
    top is +0.150 and the carriageway apron is +0.004, and a 146 mm step across a
    pedestrian crossing is a drop the scene never declared. `build_slope` descends along
    +X, so each arm is authored in a `build_rot_group` whose rotation maps local +X onto
    the arm's own (−Y / +Y) direction of fall.
    """
    wc, wn, ws, dr = (PARAMS["walk_cross"], PARAMS["walk_north"],
                      PARAMS["walk_south"], PARAMS["drive"])
    z_hi, z_lo = wc["proud"], dr["proud"]
    xm, hw = (wc["x0"] + wc["x1"]) / 2.0, (wc["x1"] - wc["x0"]) / 2.0
    out = []
    # North arm: falls from walk_north's face (y0) down to the flare edge (+flare_y).
    run_n = wn["y0"] - dr["flare_y"]
    out.append(("N", (xm, wn["y0"]), -90.0, xm, z_hi, run_n, z_hi - z_lo,
                wn["y0"] - hw, wn["y0"] + hw))
    # South arm: falls from walk_south's face (y1) up to −flare_y (i.e. toward +Y).
    run_s = -dr["flare_y"] - ws["y1"]
    out.append(("S", (xm, ws["y1"]), 90.0, xm, z_hi, run_s, z_hi - z_lo,
                ws["y1"] - hw, ws["y1"] + hw))
    return out


def cross_ramp_z(y):
    """Walked-surface z on the crossing arms at |y| between the flare edge and the walk."""
    wc, wn, dr = PARAMS["walk_cross"], PARAMS["walk_north"], PARAMS["drive"]
    a, b = dr["flare_y"], wn["y0"]
    t = min(1.0, max(0.0, (abs(y) - a) / (b - a)))
    return dr["proud"] + t * (wc["proud"] - dr["proud"])


def hazard_registry():
    """**R-1** — the hazard / drop registry, re-derived from PARAMS after the GT-5 edit.

    Rows are `(label, kind, where, z_top, magnitude)`; `kind` is `drop`, `up_step`,
    `grade` or `flat`. A `grade` row is a walked slope, **not** a drop. The registry is
    printed by the smoke run so the GT-5 landing record quotes measurements.
    """
    rp, st, sh, wl = (PARAMS["ramp"], PARAMS["stair"], PARAMS["shaft"],
                      PARAMS["wall"])
    cu, wn, ws, wc = (PARAMS["curb"], PARAMS["walk_north"],
                      PARAMS["walk_south"], PARAMS["walk_cross"])
    g = PARAMS["gkit"]
    segs, total = ramp_profile()
    rows = [
        ("ramp crest (개구 연단)", "drop", "x = 0.000", 0.0, rp["drop"]),
        ("ramp cheek kerb N (R-1, 반입)", "drop", "y = −2.700",
         0.0, float(g["curb"]["h"])),
        ("ramp cheek kerb P (R-1, 반입)", "drop", "y = +2.700",
         0.0, float(g["curb"]["h"])),
        # magnitudes are measured to the **walked** surface below (basement floor
        # −3.960), not to the structural base (−4.400)
        ("stair head (무난간)", "drop", f"x = {st['x_head']:.2f}", 0.0, rp["drop"]),
        ("shaft coping W", "drop", f"x = {sh['x0']:.2f}", wl["cope_h"],
         wl["cope_h"] + rp["drop"]),
        ("shaft coping N", "drop", f"y = {sh['y1']:.2f}", wl["cope_h"],
         wl["cope_h"] + rp["drop"]),
    ]
    for tag, p0, _p1, _side, spans in curb_lines():
        span_txt = " · ".join(f"턱낮춤 s {a:.1f}…{b:.1f}" for a, b in spans)
        rows.append((f"footway kerb {tag} (GT-5)", "drop",
                     f"y = {p0[1]:+.2f} · {span_txt}", cu["height"], cu["height"]))
    for tag, key in (("N", "walk_north"), ("S", "walk_south")):
        w = PARAMS[key]
        rows.append((f"walk_{tag} plate end x={w['x0']:.1f} (미장식)", "drop",
                     f"x = {w['x0']:.1f}", w["proud"], w["proud"]))
        rows.append((f"walk_{tag} plate end x={w['x1']:.1f} (미장식)", "drop",
                     f"x = {w['x1']:.1f}", w["proud"], w["proud"]))
    rows.append(("walk_cross far end N (미장식)", "drop",
                 f"y = {wc['y_far']:.1f}", wc["proud"], wc["proud"]))
    rows.append(("walk_cross far end S (미장식)", "drop",
                 f"y = {-wc['y_far']:.1f}", wc["proud"], wc["proud"]))
    for tag, _piv, _rot, _x0, _z0, run, drop, _y0, _y1 in cross_ramps():
        rows.append((f"crossing turn-down {tag} (차량진출입부)", "grade",
                     f"{abs(drop / run) * 100:.1f} %", wc["proud"], 0.0))
    sr = PARAMS["spur_ramp"]
    rows.append(("spur turn-down (계단머리 접근)", "grade",
                 f"{PARAMS['walk_spur']['proud'] / sr['run'] * 100:.1f} %",
                 PARAMS["walk_spur"]["proud"], 0.0))
    rows.append(("ramp deck 종단", "grade",
                 f"8.5 → 17 → 8.5 % · run {total:.2f}", 0.0, 0.0))
    return rows


# ===========================================================================
# [C3] Smoke — pre-boot geometry self-check (early exit)
# ===========================================================================
def _smoke_report():
    rp = PARAMS["ramp"]
    st = PARAMS["stair"]
    sh = PARAMS["shaft"]
    gr = PARAMS["ground"]
    ga = PARAMS["garage"]
    co = PARAMS["corridor"]
    po = PARAMS["portal"]
    segs, total_run = ramp_profile()

    print("=" * 72)
    print("scene13_apartment_parking_entry — SMOKE 기하 자기검증 (부팅 없음)")
    print("=" * 72)

    # ── Ramp longitudinal profile ──
    print("  [램프 종단 프로파일]  폭 "
          f"{rp['y1'] - rp['y0']:.1f} m (2차로 규정 6 m 이상)")
    for i, (x0, z0, run, drop) in enumerate(segs, 1):
        print(f"    seg{i}: x {x0:6.3f} → {x0 + run:6.3f}  z {z0:+.3f} → "
              f"{z0 - drop:+.3f}  경사 {drop / run * 100:5.2f}%")
    tot_drop = sum(s[3] for s in segs)
    print(f"    총 run {total_run:.3f} m · 총 낙차 {tot_drop:.3f} m · "
          f"최대 경사 {max(s[3] / s[2] for s in segs) * 100:.1f}% ≤ 17% → "
          f"{'OK' if max(s[3] / s[2] for s in segs) <= 0.1701 else 'FAIL'}")
    print(f"    낙차 검증: {tot_drop:.3f} ≥ 0.3 m → "
          f"{'OK' if tot_drop >= 0.3 else 'FAIL'}")

    # ── Contrast pair: stair drop = ramp drop ──
    sdrop = st["riser"] * st["n_flight"] * 2
    print("  [계단 ↔ 램프 낙차 정합]")
    print(f"    계단 {st['n_flight'] * 2}단 × riser {st['riser']} = "
          f"{sdrop:.3f} · 램프 {tot_drop:.3f} → "
          f"{'OK' if abs(sdrop - tot_drop) < 1e-6 else 'FAIL'} "
          f"(두 경로가 같은 지하 1층 바닥에 착지)")
    run_f = st["n_flight"] * st["tread"]
    print(f"    1련 run {run_f:.2f} m · 되돌음 참 x "
          f"[{st['land_x0']:.2f},{st['x_turn']:.2f}] "
          f"= {st['x_turn'] - st['land_x0']:.2f} m ≥ 1.2 → "
          f"{'OK' if st['x_turn'] - st['land_x0'] >= 1.2 else 'FAIL'}")
    print(f"    1련 상단 x {st['x_head']:.2f} → 하단 x "
          f"{st['x_head'] - run_f:.2f} (= 참 동단 {st['x_turn']:.2f}) → "
          f"{'OK' if abs(st['x_head'] - run_f - st['x_turn']) < 1e-6 else 'FAIL'}")

    # ── Headroom (height limit) ──
    z_portal = ramp_z(po["x"])
    clear = ga["ceil_z"] - z_portal
    print("  [지하 진입 유효고]")
    print(f"    포털 x={po['x']:.1f} 노면 z {z_portal:+.3f} · 슬래브 밑면 "
          f"{ga['ceil_z']:+.2f} → 유효고 {clear:.3f} m "
          f"(표기 높이제한 {po['head_clear']:.1f}) → "
          f"{'OK' if clear >= po['head_clear'] else 'FAIL'}")
    print(f"    지하 복도 유효고 {ga['ceil_z'] - co['floor_z']:.2f} m ≥ 2.1 → "
          f"{'OK' if ga['ceil_z'] - co['floor_z'] >= 2.1 else 'FAIL'}")

    # ── Ground plate table: is any plane covering an opening ──
    x_p = po["x"]
    plates = [
        ("Ground_W(grass)", gr["x0"], 0.0, gr["y0"], gr["y1"]),
        ("Ground_S(grass)", 0.0, x_p, gr["y0"], -3.3),
        ("Ground_N1(grass)", 0.0, sh["x0"], 3.3, gr["y1"]),
        ("Ground_N2(grass)", sh["x1"], x_p, 3.3, gr["y1"]),
        ("Ground_N3(grass)", sh["x0"], sh["x1"], sh["y1"], gr["y1"]),
        ("Ground_E(grass)", x_p, gr["x1"], gr["y0"], gr["y1"]),
    ]
    opens = [("램프 트렌치", 0.0, x_p, -3.3, 3.3),
             ("계단 샤프트", sh["x0"], sh["x1"], sh["y0"], sh["y1"])]
    print("  [지반 플레이트 표] (개구 2곳을 비운 6박스 · 상면 z=0 · 두께 "
          f"{gr['thick']:.1f})")
    print(f"    {'이름':20s} {'x범위':>16s} {'y범위':>16s}")
    bad = []
    for nm, x0, x1, y0, y1 in plates:
        print(f"    {nm:20s} [{x0:6.1f},{x1:6.1f}] [{y0:6.1f},{y1:6.1f}]")
        for onm, ox0, ox1, oy0, oy1 in opens:
            if not (x1 <= ox0 + 1e-9 or x0 >= ox1 - 1e-9 or
                    y1 <= oy0 + 1e-9 or y0 >= oy1 - 1e-9):
                bad.append(f"{nm}∩{onm}")
    print(f"    개구 위를 덮는 플레이트: {bad if bad else '없음 → OK'}")

    # ── h0.3 grazing concealment check (the core of the study) ──
    print("  [h0.3/h0.9 grazing 은닉 검산] 연단(x=0,z=0) 스치는 시선 vs 노면")
    ang_ramp = math.degrees(math.atan(rp["trans_grade"]))
    for h in (0.3, 0.9):
        for d in (2.0, 5.0, 10.0):
            ang_eye = math.degrees(math.atan(h / d))
            hid = ang_eye <= ang_ramp
            print(f"    h{h:.1f} d{d:4.1f} → 시선 부각 {ang_eye:5.2f}° vs "
                  f"램프 초기 경사 {ang_ramp:.2f}° → "
                  f"{'은닉(노면 평면 압축)' if hid else '노면 일부 노출'}")
    print(f"    ⇒ 개구 너머 지반(x ≥ {x_p:.0f}, z=0)은 상부 슬래브 위 조경이라"
          f" 근측 보도와 **연속 평면**으로 읽힌다(negative obstacle 성립).")

    # ── Statutory bollard check ──
    bo = PARAMS["bollard"]
    print("  [규정 볼라드] (교통약자법 시행규칙 별표2)")
    for i, row in enumerate(PARAMS["bollard_rows"]):
        xs = row["xs"]
        gaps = [round(abs(xs[k + 1] - xs[k]), 2) for k in range(len(xs) - 1)]
        print(f"    row{i}: y={row['y']:+.2f} · {len(xs)}본 · 간격 {gaps} "
              f"· 점형블록 y [{row['tac_y0']:+.2f},{row['tac_y1']:+.2f}] "
              f"(깊이 {abs(row['tac_y1'] - row['tac_y0']):.2f})")
    print(f"    h {bo['h']:.2f}(0.8~1.0) · 지름 {2 * bo['r']:.2f}(0.1~0.2) · "
          f"간격 {bo['gap']:.1f} 내외 · 상단 반사띠 z {bo['band_z']:.2f} → "
          f"{'OK' if 0.8 <= bo['h'] <= 1.0 and 0.1 <= 2 * bo['r'] <= 0.2 else 'FAIL'}")

    # ── Missing railing (a below-code reality) ──
    runs = [r for r in PARAMS["rail_runs"] if r["axis"] == "x"
            and abs(r["c"] + 3.15) < 1e-6]
    if len(runs) >= 2:
        gap = runs[1]["a0"] - runs[0]["a1"]
        print("  [난간 결손]")
        print(f"    남측 개구 난간: x [0,{runs[0]['a1']:.1f}] + "
              f"[{runs[1]['a0']:.1f},{runs[1]['a1']:.1f}] → 결손 {gap:.1f} m "
              f"(x {runs[0]['a1']:.1f}~{runs[1]['a0']:.1f}) — 그 지점 낙차 "
              f"{-ramp_z((runs[0]['a1'] + runs[1]['a0']) / 2.0):.2f} m 무방호")
    # ── [v6 judgment (5)] material fix check ──
    mp_ = PARAMS["material"]
    dr_ = PARAMS["drive"]
    print("  [v6 재질 수정 검산] — 아스팔트 (치수 불변)")
    print(f"    아스팔트 : gravel diff/nor/rough · scale "
          f"{mp_['asphalt_scale']:.2f} m · 틴트 {mp_['asphalt_tint']} → "
          f"청기 {'제거 OK' if mp_['asphalt_tint'][2] < mp_['asphalt_tint'][0] else 'FAIL(B>R)'}"
          f" (구 상수색 {mp_['asphalt_color']} = B>R 남청)")
    print(f"    폴리시 밴드 : 중심선 ±0.85 · 폭 0.55 · x "
          f"[{dr_['x0']:.1f},{dr_['x1']:.1f}] · 상면 돌출 4 mm "
          f"(저면 매입 → Z파이팅 없음)")

    # ── [W3 S13 · G13] gantry replaces the porch canopy (ruling §7-5) ──
    ga_ = PARAMS["gantry"]
    hb_ = PARAMS["height_bar"]
    wl_ = PARAMS["wall"]
    cope_out = rp["y1"] + wl_["thick"] / 2.0 + wl_["cope_over"]
    clr = abs(ga_["y1"]) - ga_["post_w"] / 2.0 - cope_out
    print("  [G13 갠트리] 캐노피 포치 삭제 → 스테인리스 갠트리 사인")
    print(f"    기둥 x {ga_['x']:+.2f} · y ±{abs(ga_['y1']):.2f} · "
          f"{ga_['post_w']:.2f} 각 · 코핑 외면 {cope_out:.2f} 대비 여유 "
          f"{clr * 1000:+.0f} mm → {'OK' if clr > 0 else 'FAIL(간섭)'}")
    print(f"    패널 폭 {ga_['y1'] - ga_['y0']:.2f} m · 하단 z "
          f"{ga_['clear_h']:.2f} · 높이 {ga_['panel_h']:.2f} · "
          f"교통 유효폭 {rp['y1'] - rp['y0']:.1f} m 침범 "
          f"{'없음 OK' if abs(ga_['y0']) > rp['y1'] else 'FAIL'}")
    print(f"    높이제한바 z {hb_['z']:.2f} < 패널 하단 {ga_['clear_h']:.2f} → "
          f"{'OK' if hb_['z'] < ga_['clear_h'] else 'FAIL'} "
          f"· 행어 {hb_['hang_y']:.2f} < 패널 반폭 {ga_['y1']:.2f} → "
          f"{'OK' if hb_['hang_y'] < ga_['y1'] else 'FAIL'}")

    # ── [W3 S13 · G13] wall bands must sit between the deck and grade ──
    ch_ = PARAMS["chevron"]
    print("  [G13 벽면 그래픽] 트렌치 내측면 (본 씬은 평코핑 = 규정미달 현실 유지)")
    for i, xc in enumerate(ch_["xs"]):
        z_deck_hi = ramp_z(xc - ch_["width"] / 2.0)
        zc = z_deck_hi + ch_["dz"][i]
        lo, hi = zc - ch_["height"] * 1.35 / 2.0, zc + ch_["height"] * 1.35 / 2.0
        print(f"    황흑대 x {xc:5.2f} · 노면 {z_deck_hi:+.3f} · 띠 z "
              f"[{lo:+.3f},{hi:+.3f}] → "
              f"{'OK' if lo > z_deck_hi and hi < 0.0 else 'FAIL(노면/지표 간섭)'}")
    ws_ = PARAMS["wall_strip"]
    s_lo = ramp_z(ws_["x1"]) + ws_["dz"] - ws_["h"]
    s_hi = ramp_z(ws_["x0"]) + ws_["dz"]
    print(f"    반사띠 x [{ws_['x0']:.2f},{ws_['x1']:.2f}] · 상단 z "
          f"{s_hi:+.3f} → {'OK' if s_hi < 0.0 else 'FAIL(지표 돌출)'} · 하단 "
          f"{s_lo:+.3f}")

    # ── [W3 GT-5] footway 150 mm + kerb lines ──
    cu_ = PARAMS["curb"]
    print("  [GT-5 보도 150 mm · 보차도 경계석]")
    for key in ("walk_north", "walk_south", "walk_cross", "walk_spur"):
        print(f"    {key:11s} proud {PARAMS[key]['proud']:.3f} m "
              f"(구 0.007 = 3 mm 단차)")
    n_line = 0
    for tag, p0, p1, side, spans in curb_lines():
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        n_line += 1
        print(f"    {tag:6s} y={p0[1]:+.2f} · L {L:.1f} m · road_side {side} · "
              f"턱낮춤 {[(round(a, 1), round(b, 1)) for a, b in spans]}")
    ok_h = 0.100 - 1e-9 <= cu_["height"] <= 0.250 + 1e-9
    print(f"    노출고 {cu_['height']:.3f} m (S06-B 0.10~0.25) → "
          f"{'OK' if ok_h else 'FAIL'} · gt_drop {cu_['height']:.3f} "
          f"(gutter=False → 측구 낙차 0) · 단위 {cu_['unit']:.2f} m · "
          f"아리스 look R{cu_['arris_r'] * 1000:.0f} (0 프림) · 선 {n_line}개")
    print(f"    연석 상단 {cu_['height']:.3f} = 보도면 {PARAMS['walk_north']['proud']:.3f} "
          f"→ flush ({'OK' if abs(cu_['height'] - PARAMS['walk_north']['proud']) <= 0.020 else 'FAIL'}) "
          "· 턱낮춤 ≤ 20 mm")
    for tag, _piv, _rot, _x0, _z0, run, drop, _y0, _y1 in cross_ramps():
        gr = abs(drop / run) * 100.0
        print(f"    횡단 턱낮춤 {tag} · run {abs(run):.2f} m · 낙차 {drop:.3f} → "
              f"{gr:.1f} % ({'OK ≤ 8.3 %' if gr <= 8.34 else 'FAIL'})")

    # ── R-1 hazard / drop registry ──
    print("  [R-1 위험·낙차 레지스트리] (GT-5 재캐시 R-1 — PARAMS 에서 재유도)")
    print(f"    {'항목':34s} {'종류':6s} {'위치':26s} {'z_top':>8s} {'크기':>8s}")
    for lab, kind, where, ztop, mag in hazard_registry():
        print(f"    {lab:34s} {kind:6s} {where:26s} {ztop:+8.3f} {mag:8.3f}")
    print("=" * 72)


# ===========================================================================
# [D] Camera presets
# ===========================================================================
def build_views():
    """grid_views(gy=0.0 — road centre axis) + 6 mise-en-scene shots."""
    views = sc.grid_views(0.0)
    # entry_approach: vehicle-eye approach (canopy · height bar · gate · opening)
    views["entry_approach"] = dict(eye=[-12.0, 0.0, 1.55], tgt=[2.0, 0.0, -0.5])
    # ramp_graze: pedestrian-eye grazing — does the ramp descent compress into a plane
    views["ramp_graze"] = dict(eye=[-6.0, 0.0, 0.90], tgt=[8.0, 0.0, -0.55])
    # bollard_walk: heading south on the north sidewalk — bollard row + tactile + crossing
    views["bollard_walk"] = dict(eye=[-2.2, 11.0, 1.50], tgt=[-2.2, 1.5, 0.15])
    # stair_head: looking down the 2 switchback flights and mid landing from the head
    views["stair_head"] = dict(eye=[13.6, 4.30, 1.60], tgt=[6.6, 4.90, -2.20])
    # portal_look: from mid-ramp toward the basement portal (dimly lit garage)
    views["portal_look"] = dict(eye=[13.0, 0.0, -0.95], tgt=[27.0, 0.5, -3.20])
    # beauty_overview: oblique overhead of the estate (ramp · stairs · blocks · planting)
    views["beauty_overview"] = dict(eye=[-17.0, -15.0, 12.0],
                                    tgt=[9.0, 3.0, -1.2])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. entry_approach   — 갠트리 사인·높이제한바·차단기·안내판이 진입부로 읽히는가(G13)
 2. ramp_graze·h0.3  — 램프 하강이 평면으로 압축되고 개구 너머가 연속되는가(특색)
 3. bollard_walk     — 볼라드 h0.9·간격1.5·반사띠 + 전면 0.3 m 점형블록(규정)
 4. stair_head       — 되돌음 2련·중간참·무난간 코핑(규정 미달의 현실)
 5. portal_look      — 포털 유효고·지하 약발광(PT 필수, RT 는 새까맣게 나옴)
 6. beauty_overview  — 아파트 3동·조경 화단·수목 v2 배치가 비정형인가"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene13")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene13"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # -------------------------------------------------------------------
    # Materials — including tint-jitter variants (+-5%) for per-instance variation
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["paving"] = PBR(
            f"{ROOT}/Looks/Paving", sc.tex_path("paving_interlock", "diff"),
            sc.tex_path("paving_interlock", "nor"),
            sc.tex_path("paving_interlock", "rough"),
            sca["paving_interlock"], tint=mp["paving_tint"])
        M["conc"] = PBR(
            f"{ROOT}/Looks/Concrete", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"),
            sca["concrete_floor"], tint=mp["conc_tint"])
        M["wall"] = PBR(
            f"{ROOT}/Looks/Wall", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"),
            sca["concrete_wall"], tint=mp["wall_tint"])
        M["wall_b"] = PBR(
            f"{ROOT}/Looks/WallB", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"),
            sca["concrete_wall"], tint=mp["wall_tint_b"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["grass_b"] = PBR(
            f"{ROOT}/Looks/GrassB", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint_b"])
        M["tactile"] = PBR(
            f"{ROOT}/Looks/Tactile", sc.tex_path("tactile", "diff"),
            sc.tex_path("tactile", "nor"), None, sca["tactile"])
        M["shell"] = PBR(
            f"{ROOT}/Looks/Shell", sc.tex_path("plaster", "diff"),
            sc.tex_path("plaster", "nor"), sc.tex_path("plaster", "rough"),
            sca["plaster"], tint=mp["shell_tint"])
        M["shell_b"] = PBR(
            f"{ROOT}/Looks/ShellB", sc.tex_path("plaster", "diff"),
            sc.tex_path("plaster", "nor"), sc.tex_path("plaster", "rough"),
            sca["plaster"], tint=mp["shell_tint_b"])
        # [v6 (5)] asphalt : constant colour -> aggregate texture + neutral grey-black tint.
        #   scale 0.35 m keeps the aggregate patches dense on screen (the old constant
        #   colour turned 40~60 % of the h0.3 shots into zero-information area).
        M["asphalt"] = PBR(
            f"{ROOT}/Looks/Asphalt", sc.tex_path("gravel", "diff"),
            sc.tex_path("gravel", "nor"), sc.tex_path("gravel", "rough"),
            mp["asphalt_scale"], tint=mp["asphalt_tint"])
        M["polish"] = PBR(f"{ROOT}/Looks/Polish",
                          diffuse_color=mp["polish_color"],
                          roughness_const=mp["polish_rough"])
        M["paint"] = PBR(f"{ROOT}/Looks/Paint", diffuse_color=mp["paint_color"],
                         roughness_const=mp["paint_rough"])
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        M["bollard"] = PBR(f"{ROOT}/Looks/Bollard",
                           diffuse_color=mp["bollard_color"],
                           metallic=mp["bollard_metallic"],
                           roughness_const=mp["bollard_rough"])
        M["band"] = PBR(f"{ROOT}/Looks/Band", diffuse_color=mp["band_color"],
                        roughness_const=mp["band_rough"])
        M["cope"] = PBR(f"{ROOT}/Looks/Cope", diffuse_color=mp["cope_color"],
                        roughness_const=mp["cope_rough"])
        # [W3 GT-5 · K5 3.] kerb — path token `Curb` binds LOOK_CLASS["curb"] (R10 arris)
        M["curb"] = PBR(
            f"{ROOT}/Looks/Curb", sc.tex_path("marble_light", "diff"),
            sc.tex_path("marble_light", "nor"),
            sc.tex_path("marble_light", "rough"), sca["marble_light"],
            tint=mp["curb_tint"])
        # [W3 S13 · G13] stainless gantry (STS304 hairline)
        M["gantry"] = PBR(f"{ROOT}/Looks/Gantry",
                          diffuse_color=mp["gantry_color"],
                          metallic=mp["gantry_metallic"],
                          roughness_const=mp["gantry_rough"])
        # [W3 S13 · G13] yellow ramp centre line (`LineYellow` → paint look class)
        M["line_y"] = PBR(f"{ROOT}/Looks/LineYellow",
                          diffuse_color=mp["line_y_color"],
                          roughness_const=mp["line_y_rough"])
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"])
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        # [W3 S13] `Looks/Roof` + `Looks/Fascia` are **deleted with the porch canopy** —
        #   nothing binds them any more, and an unbound material is still 2 prims and 2
        #   rows in the material census. `roof_*` / `fascia_*` stay in PARAMS as the
        #   record of what the v6 C-3 fix had been (they are now unread).
        M["post"] = PBR(f"{ROOT}/Looks/Post", diffuse_color=mp["post_color"],
                        metallic=mp["post_metallic"],
                        roughness_const=mp["post_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["dark"] = PBR(f"{ROOT}/Looks/Dark", diffuse_color=mp["dark_color"],
                        roughness_const=mp["dark_rough"])
        M["warn_y"] = PBR(f"{ROOT}/Looks/WarnY", diffuse_color=mp["warn_y"],
                          roughness_const=0.6)
        M["warn_r"] = PBR(f"{ROOT}/Looks/WarnR", diffuse_color=mp["warn_r"],
                          roughness_const=0.6)
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["emit"] = PBR(f"{ROOT}/Looks/Emit", diffuse_color=mp["lamp_color"],
                        roughness_const=0.4,
                        emission_color=mp["emit_color"],
                        emission_intensity=mp["emit_intensity"])
        M["sign_back"] = PBR(f"{ROOT}/Looks/SignBack",
                             diffuse_color=mp["sign_back_color"],
                             roughness_const=mp["sign_back_rough"])
        for key in ("info",):        # [v5.2 user] arbitrary warning signs removed
            M[f"sign_{key}"] = PBR(
                f"{ROOT}/Looks/Sign_{key}",
                diff=sc.tex_path(f"sign_{key}", "diff"), uv_mode=True,
                roughness_const=0.45)
        return M

    # -------------------------------------------------------------------
    # Ground — 6 boxes leaving the 2 openings (ramp trench · stair shaft) clear
    # -------------------------------------------------------------------
    def build_ground(M):
        gr = PARAMS["ground"]
        sh = PARAMS["shaft"]
        x_p = PARAMS["portal"]["x"]
        cz = gr["z_top"] - gr["thick"] / 2.0
        segs = [("W", gr["x0"], 0.0, gr["y0"], gr["y1"]),
                ("S", 0.0, x_p, gr["y0"], -3.3),
                ("N1", 0.0, sh["x0"], 3.3, gr["y1"]),
                ("N2", sh["x1"], x_p, 3.3, gr["y1"]),
                ("N3", sh["x0"], sh["x1"], sh["y1"], gr["y1"]),
                ("E", x_p, gr["x1"], gr["y0"], gr["y1"])]
        for tag, x0, x1, y0, y1 in segs:
            sc.skin_exclude(f"{ROOT}/Ground_{tag}")     # [W2-0 · P-A]
            BOX(f"{ROOT}/Ground_{tag}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, cz),
                (x1 - x0, y1 - y0, gr["thick"]), M["grass"], col=True)

    def build_flat_fill(M):
        """hazard_stairs=False control: both openings filled flat at z=0."""
        gr = PARAMS["ground"]
        sh = PARAMS["shaft"]
        x_p = PARAMS["portal"]["x"]
        cz = gr["z_top"] - gr["thick"] / 2.0
        BOX(f"{ROOT}/FlatFill_Ramp", (x_p / 2.0, 0.0, cz),
            (x_p, 6.6, gr["thick"]), M["paving"], col=True)
        BOX(f"{ROOT}/FlatFill_Shaft",
            ((sh["x0"] + sh["x1"]) / 2.0, (sh["y0"] + sh["y1"]) / 2.0, cz),
            (sh["x1"] - sh["x0"], sh["y1"] - sh["y0"], gr["thick"]),
            M["paving"], col=True)

    # -------------------------------------------------------------------
    # Surface paving overlay — road (asphalt) + sidewalk (interlocking) bands
    #   The sidewalk stops outside the road flare (y +-4.2); crossings use road paving (practice).
    # -------------------------------------------------------------------
    def build_paving(M):
        dr = PARAMS["drive"]
        z = PARAMS["ground"]["z_top"]
        # road: straight section + flared entry
        # [W2-0 · P-A] The entry asphalt is the stage for 13-8's 3-shot filler -> skin OFF.
        sc.skin_exclude(f"{ROOT}/Drive_Main", f"{ROOT}/Drive_Flare")
        BOX(f"{ROOT}/Drive_Main",
            ((dr["x0"] + dr["flare_x0"]) / 2.0, 0.0, z + dr["proud"] - 0.05),
            (dr["flare_x0"] - dr["x0"], 6.6, 0.1), M["asphalt"], col=True)
        BOX(f"{ROOT}/Drive_Flare",
            ((dr["flare_x0"] + dr["x1"]) / 2.0, 0.0, z + dr["proud"] - 0.05),
            (dr["x1"] - dr["flare_x0"], 2 * dr["flare_y"], 0.1),
            M["asphalt"], col=True)
        # [v6 (5)] tyre polish bands — 2 wheel tracks (centreline +-0.85, width 0.55).
        #   Base buried below the road, top proud 4 mm -> no coplanar Z-fighting.
        for tag, yc in (("L", -0.85), ("R", 0.85)):
            BOX(f"{ROOT}/DrivePolish_{tag}",
                ((dr["x0"] + dr["x1"]) / 2.0, yc,
                 z + dr["proud"] - 0.006),
                (dr["x1"] - dr["x0"], 0.55, 0.02), M["polish"])
        # road centre guide line (5 dashes)
        for i in range(5):
            bx = dr["x0"] + 0.9 + i * 2.6
            BOX(f"{ROOT}/DriveLine_{i}", (bx, 0.0, z + 0.008),
                (1.5, 0.12, 0.02), M["paint"])
        walks = []
        wc = PARAMS["walk_cross"]
        wn = PARAMS["walk_north"]
        ws_ = PARAMS["walk_south"]
        # The crossing sidewalk is cut into 4 pieces so it **never overlaps** walk_north/south
        #   (two plates sharing a top z would Z-fight — audit v4 lesson).
        # [W3 GT-5] CrossN1 / CrossS1 are no longer plates: they are the **turn-down
        #   ramps** built by `build_cross_ramps`, because at proud 0.150 a flat plate
        #   would put a 146 mm step across the carriageway edge.
        walks.append(("CrossN2", wc["x0"], wc["x1"], wn["y1"], wc["y_far"],
                      wc["proud"]))
        walks.append(("CrossS2", wc["x0"], wc["x1"], -wc["y_far"], ws_["y0"],
                      wc["proud"]))
        for key in ("walk_north", "walk_south"):
            w = PARAMS[key]
            walks.append((key[5:].capitalize(), w["x0"], w["x1"], w["y0"],
                          w["y1"], w["proud"]))
        # [W3 GT-5] the spur's west metre is its own turn-down toward the stair head,
        #   so the flat part starts one run east of x0.
        ws = PARAMS["walk_spur"]
        sr = PARAMS["spur_ramp"]
        walks.append(("Spur", ws["x0"] + sr["run"], ws["x1"], ws["y0"], ws["y1"],
                      ws["proud"]))
        # [W3 GT-5] plate thickness follows `proud` so the underside stays buried
        #   `walk_plate_t` below the ground plate top — at 0.150 the old fixed 0.12 box
        #   would have floated 30 mm clear of the ground.
        t_bury = PARAMS["walk_plate_t"]
        for tag, x0, x1, y0, y1, pr in walks:
            th = pr + t_bury
            BOX(f"{ROOT}/Walk_{tag}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, z + pr - th / 2.0),
                (x1 - x0, y1 - y0, th), M["paving"], col=True)

    def build_cross_ramps(M):
        """[W3 GT-5] driveway turn-downs — `cross_ramps()` + the spur's own west run."""
        t_bury = PARAMS["walk_plate_t"]
        for tag, piv, rot, x0l, z0, run, drop, y0l, y1l in cross_ramps():
            grp = sc.build_rot_group(stage, f"{ROOT}/WalkRamp_{tag}", piv, rot)
            sc.build_slope(stage, f"{grp}/Plate", x0l, z0, abs(run), drop,
                           y0l, y1l, PARAMS["walk_cross"]["proud"] + t_bury,
                           M["paving"], margin=0.0, collider=True)
        ws = PARAMS["walk_spur"]
        sr = PARAMS["spur_ramp"]
        # Rises toward +X (a negative `drop` in build_slope's convention).
        sc.build_slope(stage, f"{ROOT}/WalkRamp_Spur", sr["x0"],
                       PARAMS["drive"]["proud"], sr["run"],
                       PARAMS["drive"]["proud"] - ws["proud"],
                       ws["y0"], ws["y1"], ws["proud"] + t_bury,
                       M["paving"], margin=0.0, collider=True)

    def build_curbs(M):
        """[W3 GT-5 · K5] the 보차도 경계석 the footways never had.

        Four `build_curb_line` runs, 1 m precast units, R10 arris from the bound
        `curb` look class (0 prims), no L-gutter (verge side), 턱낮춤 wherever another
        footway plate abuts. `build_ramp_curb` is **already wired** through
        `ground_kit` extras (`w3_k5_v1.md` §6-1) and is deliberately not called here.
        """
        ok, got, note = ik.check_arris_role(sc, role="curb",
                                            arris_r=PARAMS["curb"]["arris_r"])
        print(f"[GT-5] 아리스 룩클래스 검증 — {note}")
        if not ok:
            raise ValueError(f"scene13: {note}")
        kit = ik.kit_from_scene_common(sc, stage)
        kw = curb_kwargs()
        n_blk = n_prim = 0
        res = None
        for tag, p0, p1, side, spans in curb_lines():
            res = ik.build_curb_line(kit, f"{ROOT}/Curb_{tag}", p0, p1, M["curb"],
                                     road_side=side, drop_spans=list(spans), **kw)
            for w in res["warnings"]:
                print(f"[GT-5] 경계석 경고({tag}) — {w}")
            n_blk += res["n_blocks"]
            n_prim += res["prim_count"]
        print(f"[GT-5] 보차도 경계석 4선 · 블록 {n_blk} · 프림 {n_prim} · "
              f"상단 z {res['curb_top_z']:+.3f} (보도면 "
              f"{PARAMS['walk_north']['proud']:+.3f} flush) · 노출 "
              f"{res['exposure_road']:.3f} · gt_drop {res['gt_drop']:.3f} · "
              f"단위 {res['unit_actual']:.2f} m · 아리스 look(R10, 0프림)")
        return dict(blocks=n_blk, prims=n_prim, gt_drop=res["gt_drop"])

    # -------------------------------------------------------------------
    # [W2] ground_kit — P7 ramp_parking
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["gkit"]
        segs, _total = ramp_profile()
        rp = PARAMS["ramp"]
        gp = gk.plan_ground(
            "ramp_parking", region=tuple(g["region"]), z=0.0, gy=0.0,
            origin=(0.0, 0.0, 0.0),
            # [W3 S13] intake §2 scene13 (e): GD patch 2 → 1, and the two white ramp
            #   boundary lines are dropped (G13 shows a yellow centre line only).
            overrides=dict(
                surface=(("patch", int(g["patch_n"])), ("crack", 6),
                         ("stain", ("tire",)), ("weed", 5)),
                infra=dict(marking=())),
            # Ramp crest = the drop edge. Deck grade 0.085 beyond -> [F] at d2 only.
            edges=[("ramp_crest", 0.0,
                    dict(beyond_grade=float(rp["trans_grade"])))],
            dists=(2, 5, 10), scene="scene13",
            tactile=("bollard",) if cfg["cue_tactile"] else (),
            sites=dict(
                manhole=[tuple(g["manhole_d5"])],
                trench=[(float(g["trench_entry"]), rp["y0"], rp["y1"]),
                        (float(g["trench_sump"]), rp["y0"], rp["y1"])],
                marking=[(x, y, 0.0, 6.0) for x, y in g["lane_lines"]],
                tactile=dict(bollard=tuple(g["tactile_bollard"]))),
            extras_args=dict(
                ramp_curb=dict(profile=segs, y_neg=float(rp["y0"]),
                               y_pos=float(rp["y1"]),
                               height=float(g["curb"]["h"]),
                               width=float(g["curb"]["width"])),
                groove_band=dict(region=tuple(g["groove"]))),
            seed=13)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["dark"], crack=M["dark"], patch=M["asphalt"],
                  patch_cut=M["dark"], manhole=M["dark"], marking=M["paint"],
                  trench=M["dark"], trench_frame=M["dark"], curb=M["conc"],
                  weed=M["grass_b"], stain_tire=M["polish"],
                  groove=M["dark"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        # ── M4 handover — record the **unlabelled drop** in both the scene log and gt_changes ──
        for chg in res["gt_changes"]:
            print(f"[GT 인계 · W4] scene13 {chg['item']} 낙차 "
                  f"{chg['drop']:.3f} m 신설 — 라벨 담당 {chg['label_owner']}. "
                  f"{chg['note']}")
        print(f"[ground_kit] scene13 P7 · 프림 {res['prims']} · "
              f"δmax {res['gt_delta_max']:.4f} · "
              f"재질요청 {len(res['materials_needed'])}건(T1)")
        return res

    # -------------------------------------------------------------------
    # Ramp — 3 segments (transition · main · transition) + side walls and coping
    # -------------------------------------------------------------------
    def build_ramp(M, ramp_mtl):
        rp = PARAMS["ramp"]
        segs, total_run = ramp_profile()
        for i, (x0, z0, run, drop) in enumerate(segs, 1):
            # the first segment must be exactly flush with the road, so margin=0
            mg = 0.0 if i == 1 else rp["seg_margin"]
            sc.build_slope(stage, f"{ROOT}/Ramp_Seg{i}", x0, z0, run, drop,
                           rp["y0"], rp["y1"], rp["thick"], ramp_mtl,
                           margin=mg, collider=True)

    def build_trench_walls(M):
        wl = PARAMS["wall"]
        rp = PARAMS["ramp"]
        x_p = PARAMS["portal"]["x"]
        y_in, t = rp["y1"], wl["thick"]
        y_ctr = y_in + t / 2.0
        cz = (wl["z_top"] + wl["z_bot"]) / 2.0
        hz = wl["z_top"] - wl["z_bot"]
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            BOX(f"{ROOT}/TrenchWall_{tag}", (x_p / 2.0, sgn * y_ctr, cz),
                (x_p, t, hz), M["wall"], col=True)
            BOX(f"{ROOT}/TrenchCope_{tag}",
                (x_p / 2.0, sgn * y_ctr, wl["z_top"] + wl["cope_h"] / 2.0),
                (x_p, t + 2 * wl["cope_over"], wl["cope_h"]), M["cope"],
                col=True)

    # -------------------------------------------------------------------
    # Stair shaft — 2 switchback flights + mid landing + walls
    # -------------------------------------------------------------------
    def build_stair(M, stair_mtl):
        st = PARAMS["stair"]
        sh = PARAMS["shaft"]
        # flight 1: descends -X. Built locally (+X descending) and flipped by rot_group 180 deg.
        px = (st["x_turn"] + st["x_head"]) / 2.0
        py = (st["y_a0"] + st["y_a1"]) / 2.0
        grp = sc.build_rot_group(stage, f"{ROOT}/StairA", (px, py), 180.0)
        sc.build_straight_stairs(
            stage, f"{grp}/Steps", st["x_turn"], st["y_a0"], st["y_a1"],
            st["riser"], st["tread"], st["n_flight"], st["base_z"], stair_mtl,
            z_top=0.0, collider=True)
        if cfg["cue_nosing"]:
            sc.build_nosing(
                stage, f"{grp}/Nosing", st["x_turn"], st["y_a0"], st["y_a1"],
                st["riser"], st["tread"], st["n_flight"], z_top=0.0)
        # mid landing
        BOX(f"{ROOT}/StairLanding",
            ((st["land_x0"] + st["x_turn"]) / 2.0,
             (st["y_a0"] + st["y_b1"]) / 2.0,
             (st["mid_z"] + st["base_z"]) / 2.0),
            (st["x_turn"] - st["land_x0"], st["y_b1"] - st["y_a0"],
             st["mid_z"] - st["base_z"]), stair_mtl, col=True)
        # flight 2: descends +X (landing -> basement corridor)
        sc.build_straight_stairs(
            stage, f"{ROOT}/StairB", st["x_turn"], st["y_b0"], st["y_b1"],
            st["riser"], st["tread"], st["n_flight"], st["base_z"], stair_mtl,
            z_top=st["mid_z"], collider=True)
        if cfg["cue_nosing"]:
            sc.build_nosing(
                stage, f"{ROOT}/StairB_Nosing", st["x_turn"], st["y_b0"],
                st["y_b1"], st["riser"], st["tread"], st["n_flight"],
                z_top=st["mid_z"])
        # shaft walls: west (x0..x0+t) · north (y1-t..y1) · centre wall between the flights
        t = sh["wall_t"]
        wz = (0.0 + st["base_z"]) / 2.0
        wh = 0.0 - st["base_z"]
        BOX(f"{ROOT}/ShaftWall_W",
            (sh["x0"] + t / 2.0, (sh["y0"] + sh["y1"]) / 2.0, wz),
            (t, sh["y1"] - sh["y0"], wh), M["wall_b"], col=True)
        BOX(f"{ROOT}/ShaftWall_N",
            ((sh["x0"] + sh["x1"]) / 2.0, sh["y1"] - t / 2.0, wz),
            (sh["x1"] - sh["x0"], t, wh), M["wall_b"], col=True)
        BOX(f"{ROOT}/ShaftWall_Mid",
            ((st["x_turn"] + st["x_head"]) / 2.0,
             (st["y_a1"] + st["y_b0"]) / 2.0, wz),
            (st["x_head"] - st["x_turn"], st["y_b0"] - st["y_a1"], wh),
            M["wall_b"], col=True)
        # shaft top coping (unrailed by custom — a below-code reality)
        wl = PARAMS["wall"]
        BOX(f"{ROOT}/ShaftCope_W",
            (sh["x0"] + t / 2.0, (sh["y0"] + sh["y1"]) / 2.0,
             wl["cope_h"] / 2.0),
            (t + 2 * wl["cope_over"], sh["y1"] - sh["y0"], wl["cope_h"]),
            M["cope"])
        BOX(f"{ROOT}/ShaftCope_N",
            ((sh["x0"] + sh["x1"]) / 2.0, sh["y1"] - t / 2.0,
             wl["cope_h"] / 2.0),
            (sh["x1"] - sh["x0"], t + 2 * wl["cope_over"], wl["cope_h"]),
            M["cope"])

    # -------------------------------------------------------------------
    # Basement — corridor + garage (floor · walls · columns · bay lines · dim lights)
    # -------------------------------------------------------------------
    def build_underground(M):
        co = PARAMS["corridor"]
        ga = PARAMS["garage"]
        t = co["wall_t"]
        # corridor floor
        BOX(f"{ROOT}/Corridor_Floor",
            ((co["x0"] + co["x1"]) / 2.0, (co["y0"] + co["y1"]) / 2.0,
             co["floor_z"] - co["floor_thick"] / 2.0),
            (co["x1"] - co["x0"], (co["y1"] - co["y0"]) + 2 * t,
             co["floor_thick"]), M["conc"], col=True)
        # 2 corridor walls (ceiling = ground plate underside)
        wz = (co["floor_z"] + co["ceil_z"]) / 2.0
        wh = co["ceil_z"] - co["floor_z"]
        for sgn, tag, yc in ((-1.0, "S", co["y0"] - t / 2.0),
                             (1.0, "N", co["y1"] + t / 2.0)):
            BOX(f"{ROOT}/Corridor_Wall_{tag}",
                ((co["x0"] + co["x1"]) / 2.0, yc, wz),
                (co["x1"] - co["x0"], t, wh), M["wall_b"], col=True)
        # garage floor
        BOX(f"{ROOT}/Garage_Floor",
            ((ga["x0"] + ga["x1"]) / 2.0, (ga["y0"] + ga["y1"]) / 2.0,
             ga["floor_z"] - ga["floor_thick"] / 2.0),
            (ga["x1"] - ga["x0"], ga["y1"] - ga["y0"], ga["floor_thick"]),
            M["conc"], col=True)
        # garage walls (south · north · east) + 3 pieces closing the west end
        #   The west face at x=x0 is closed **except the ramp (y +-3) and corridor openings**.
        #   Without it the basement cavity opens into the soil and PT renders a black hole.
        gz = (ga["floor_z"] + ga["ceil_z"]) / 2.0
        gh = ga["ceil_z"] - ga["floor_z"]
        gt = ga["wall_t"]
        rp = PARAMS["ramp"]
        for tag, yc in (("S", ga["y0"] + gt / 2.0), ("N", ga["y1"] - gt / 2.0)):
            BOX(f"{ROOT}/Garage_Wall_{tag}",
                ((ga["x0"] + ga["x1"]) / 2.0, yc, gz),
                (ga["x1"] - ga["x0"], gt, gh), M["wall_b"], col=True)
        BOX(f"{ROOT}/Garage_Wall_E",
            (ga["x1"] - gt / 2.0, (ga["y0"] + ga["y1"]) / 2.0, gz),
            (gt, ga["y1"] - ga["y0"], gh), M["wall_b"], col=True)
        for tag, y0, y1 in (("a", ga["y0"], rp["y0"]),
                            ("b", rp["y1"], co["y0"]),
                            ("c", co["y1"], ga["y1"])):
            if y1 - y0 <= 1e-6:
                continue
            BOX(f"{ROOT}/Garage_Wall_W{tag}",
                (ga["x0"] + gt / 2.0, (y0 + y1) / 2.0, gz),
                (gt, y1 - y0, gh), M["wall_b"], col=True)
        # columns
        cs = PARAMS["garage_col"]["size"]
        for i, (cx, cy) in enumerate(PARAMS["garage_cols"]):
            BOX(f"{ROOT}/Garage_Col_{i}", (cx, cy, gz), (cs, cs, gh),
                M["wall"], col=True)
        # parking bay painted lines
        pl = PARAMS["park_line"]
        for i, (lx, ly) in enumerate(PARAMS["park_lines"]):
            BOX(f"{ROOT}/ParkLine_{i}",
                (lx, ly + pl["len"] / 2.0, ga["floor_z"] + pl["z_off"]),
                (pl["w"], pl["len"], 0.02), M["paint"])
        # dim ceiling lights (PT 8 bounces assumed)
        gl = PARAMS["garage_lamp"]
        for i, (lx, ly) in enumerate(PARAMS["garage_lights"]):
            BOX(f"{ROOT}/GarageLamp_{i}", (lx, ly, gl["z"]), gl["size"],
                M["emit"])
        for i, (lx, ly) in enumerate(PARAMS["corridor_lights"]):
            BOX(f"{ROOT}/CorridorLamp_{i}", (lx, ly, gl["z"]),
                (gl["size"][0] * 0.7, gl["size"][1], gl["size"][2]),
                M["emit"])

    # -------------------------------------------------------------------
    # Entry equipment — canopy + height-limit bar + barrier gate
    # -------------------------------------------------------------------
    def build_entry_gear(M):
        """[W3 S13 · ruling §7-5] the porch canopy is gone; the mouth carries a gantry.

        `sc.build_canopy` is **not called by this scene any more** — the 5.8 m slab on
        four free posts covered 24 % of a 24 m approach and appears in no reference
        image. The full-length cover is the building slab over the portal (`garage`),
        which was already built; what the image adds is the sign frame.
        """
        gy = PARAMS["gantry"]
        pk.build_gantry_sign(stage, f"{ROOT}/Gantry", gy["x"], gy["y0"], gy["y1"],
                             0.0, gy["clear_h"], M["gantry"], M["gantry"],
                             post_w=gy["post_w"], panel_h=gy["panel_h"],
                             panel_t=gy["panel_t"])
        # height-limit bar — now hung from the gantry panel (8 yellow/black segments)
        hb = PARAMS["height_bar"]
        seg_len = (hb["y1"] - hb["y0"]) / hb["nseg"]
        for i in range(hb["nseg"]):
            yc = hb["y0"] + (i + 0.5) * seg_len
            CYL(f"{ROOT}/HeightBar/Seg_{i}", (hb["x"], yc, hb["z"]),
                hb["r"], seg_len * 1.02,
                M["warn_y"] if i % 2 == 0 else M["dark"], rotX=90.0)
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            BOX(f"{ROOT}/HeightBar/Hanger_{tag}",
                (hb["x"], sgn * hb["hang_y"],
                 (hb["z"] + gy["clear_h"]) / 2.0),
                (hb["hanger_t"], hb["hanger_t"], gy["clear_h"] - hb["z"]),
                M["gantry"])

    def build_wall_graphics(M):
        """[W3 S13 · G13] yellow/black bands + reflective guidance strip on the cheeks.

        They sit on the **inner** faces (y = ±3.0), the only wall surface this scene
        exposes: G13's above-ground parapet is a *compliant* guarding condition, while
        scene13's identity is the below-code one (flush coping, 3 m of railing missing
        on the south side). Adding the parapet would delete the scene's research content,
        so it is deliberately not adopted — recorded in `Docs/reports/w3_s13_v1.md` §3.
        """
        ch = PARAMS["chevron"]
        rp = PARAMS["ramp"]
        n = 0
        for i, xc in enumerate(ch["xs"]):
            zc = ramp_z(xc - ch["width"] / 2.0) + ch["dz"][i]
            for sgn, tag in ((1.0, "N"), (-1.0, "S")):
                pk.build_chevron_band(
                    stage, f"{ROOT}/Chevron_{tag}{i}", xc,
                    sgn * (rp["y1"] - ch["stripe_t"] / 2.0 - 0.001), zc,
                    width=ch["width"], height=ch["height"], n=ch["n"],
                    stripe_t=ch["stripe_t"], yaw=90.0,
                    stage_mtl_prefix=f"{ROOT}/Looks")
                n += 1
        ws = PARAMS["wall_strip"]
        run = ws["x1"] - ws["x0"]
        drop = run * float(rp["main_grade"])
        for sgn, tag in ((1.0, "N"), (-1.0, "S")):
            y_face = sgn * rp["y1"]
            y0 = y_face - sgn * ws["t"]
            sc.build_slope(stage, f"{ROOT}/WallStrip_{tag}", ws["x0"],
                           ramp_z(ws["x0"]) + ws["dz"], run, drop,
                           min(y0, y_face), max(y0, y_face), ws["h"],
                           M["band"], margin=0.0, collider=False)
        print(f"[G13] 벽면 그래픽 — 황흑대 {n}개소 · 반사띠 2선 "
              f"(x {ws['x0']:.1f}…{ws['x1']:.1f}, 노면 위 {ws['dz']:.2f} m)")

    def build_ramp_marks(M):
        """[W3 S13 · G13] yellow ramp centre line + yellow/black cheek kerb blocks.

        Both must ride the 8.5 %/17 % deck, so they are `build_slope` slabs rather than
        `ground_kit` markings (a gkit marking is a flat plate at plan z).
        """
        rl = PARAMS["ramp_line"]
        segs, _total = ramp_profile()
        n_line = 0
        for i, (x0, z0, run, drop) in enumerate(segs, 1):
            xs = max(x0, rl["x_start"])           # break the line at the entry trench
            if xs >= x0 + run - 1e-6:
                continue
            r = x0 + run - xs
            sc.build_slope(stage, f"{ROOT}/RampLine_{i}", xs,
                           ramp_z(xs) + rl["proud"], r, drop * r / run,
                           -rl["half_w"], rl["half_w"], rl["thick"],
                           M["line_y"], margin=0.0, collider=False)
            n_line += 1
        ks = PARAMS["kerb_stripe"]
        g = PARAMS["gkit"]
        rp = PARAMS["ramp"]
        cw, chh = float(g["curb"]["width"]), float(g["curb"]["h"])
        n_st = 0
        x = ks["x0"]
        i = 0
        while x < ks["x1"] - 1e-6:
            r = min(ks["unit"], ks["x1"] - x)
            for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                ya = sgn * rp["y1"] - sgn * cw
                sc.build_slope(stage, f"{ROOT}/KerbStripe_{tag}{i}", x,
                               ramp_z(x) + chh + ks["proud"], r,
                               r * float(rp["trans_grade"]),
                               min(ya, sgn * rp["y1"]), max(ya, sgn * rp["y1"]),
                               ks["thick"],
                               M["warn_y"] if i % 2 == 0 else M["dark"],
                               margin=0.0, collider=False)
                n_st += 1
            x += r
            i += 1
        print(f"[G13] 램프 노면 — 황색 중앙선 {n_line}구간 · "
              f"황흑 연석블록 {n_st}개 (x {ks['x0']:.2f}…{ks['x1']:.2f})")
        # barrier gate — box on the retaining wall coping + lowered arm (7 red/white segments)
        gt = PARAMS["gate"]
        BOX(f"{ROOT}/Gate/Box",
            (gt["x"], gt["y"], gt["base_z"] + gt["box"][2] / 2.0),
            gt["box"], M["post"], col=True)
        aseg = (gt["arm_y1"] - gt["arm_y0"]) / gt["nseg"]
        for i in range(gt["nseg"]):
            yc = gt["arm_y1"] - (i + 0.5) * aseg
            CYL(f"{ROOT}/Gate/Arm_{i}", (gt["x"], yc, gt["arm_z"]),
                gt["arm_r"], aseg * 1.02,
                M["warn_r"] if i % 2 == 0 else M["band"], rotX=90.0)

    # -------------------------------------------------------------------
    # Cue — bollards and dot tactile / railing / signs
    # -------------------------------------------------------------------
    def build_bollards(M):
        """[v5.1 statutory bollards] height 0.9 · diameter 0.16 · spacing 1.5 · reflective top
        band + 0.3 m dot tactile in front. Placed only at the 2 points where the sidewalk
        crosses the road."""
        bo = PARAMS["bollard"]
        wc = PARAMS["walk_cross"]
        for r, row in enumerate(PARAMS["bollard_rows"]):
            # [W3 GT-5] the bollard rows stand on the crossing turn-downs, whose
            #   surface is no longer z=0 — seat them on the ramp, not in it.
            gz = cross_ramp_z(row["y"])
            for i, bx in enumerate(row["xs"]):
                sc.build_bollard(stage, f"{ROOT}/Bollard_{r}_{i}", bx,
                                 row["y"], gz, mtl=M["bollard"],
                                 radius=bo["r"], height=bo["h"])
                CYL(f"{ROOT}/BollardBand_{r}_{i}", (bx, row["y"],
                                                    gz + bo["band_z"]),
                    bo["band_r"], bo["band_h"], M["band"])
            if cfg["cue_tactile"]:
                sc.build_tactile(stage, f"{ROOT}/Tactile_Bollard_{r}",
                                 wc["x0"], wc["x1"], row["tac_y0"],
                                 row["tac_y1"], M["tactile"],
                                 z=cross_ramp_z(row["tac_y0"]),
                                 proud=PARAMS["tactile"]["proud"])

    def build_railings(M):
        ra = PARAMS["rail"]
        top_z = ra["base_z"] + ra["h"]
        mid_z = ra["base_z"] + ra["mid_h"]

        def line(prefix, axis, c, a0, a1):
            mid_a = (a0 + a1) / 2.0
            L = a1 - a0
            rotY, rotX = (90.0, 0.0) if axis == "x" else (0.0, 90.0)
            for tag, r, z in (("Top", ra["rail_r"], top_z),
                              ("Mid", ra["mid_r"], mid_z)):
                ctr = (mid_a, c, z) if axis == "x" else (c, mid_a, z)
                CYL(f"{prefix}/{tag}", ctr, r, L, M["rail"],
                    rotY=rotY, rotX=rotX)
            n = 0
            a = a0 + 0.25
            while a <= a1 - 0.2 + 1e-6:
                ctr = ((a, c, ra["base_z"] + ra["h"] / 2.0) if axis == "x"
                       else (c, a, ra["base_z"] + ra["h"] / 2.0))
                CYL(f"{prefix}/Post_{n}", ctr, ra["post_r"], ra["h"],
                    M["rail"], col=True)
                a += ra["spacing"]
                n += 1

        for i, rr in enumerate(PARAMS["rail_runs"]):
            line(f"{ROOT}/Rail_{i}", rr["axis"], rr["c"], rr["a0"], rr["a1"])

    def build_tactiles(M):
        tc = PARAMS["tactile"]
        st = PARAMS["stair"]
        # warning band at the stair head (surface) + at the stair foot landing (basement)
        sc.build_tactile(stage, f"{ROOT}/Tactile_StairHead",
                         tc["head_x0"], tc["head_x1"], st["y_a0"], st["y_a1"],
                         M["tactile"], z=0.0, proud=tc["proud"])
        sc.build_tactile(stage, f"{ROOT}/Tactile_StairFoot",
                         tc["foot_x0"], tc["foot_x1"], st["y_b0"], st["y_b1"],
                         M["tactile"], z=-PARAMS["ramp"]["drop"],
                         proud=tc["proud"])

    def build_signs(M):
        """[v5.2 user] arbitrary warning signs removed — only 1 pole-mounted fee board."""
        for key, prm in (("info", PARAMS["sign_info"]),):
            sc.build_sign(stage, f"{ROOT}/Sign_{key}", prm["cx"], prm["cy"],
                          0.0, prm["yaw"], panel_mtl=M[f"sign_{key}"],
                          w=prm["w"], h=prm["h"], pole_h=prm["pole_h"],
                          pole_mtl=M["post"], back_mtl=M["sign_back"])

    # -------------------------------------------------------------------
    # Dressing — planters · trees · hedges · benches · lamps · 3 apartment blocks
    # -------------------------------------------------------------------
    def build_dressing(M):
        pl = PARAMS["planter"]
        tree_mtls = (M["wood"], M["canopy_a"], M["canopy_b"])
        # [W3 K4(b) · TREE_BANDS] **route band vs verge band.** The bed trees stay on
        #   `build_planter`'s own call, i.e. on the `SCENE_SPECIES["Scene13"]` row — the
        #   verge band declares `species=None` and is not required to match the route.
        #   Passing a species here is impossible without also losing the reserved centre
        #   (`build_planter` adds a third bed shrub *at* `(cx, cy)` when `tree_mtls` is
        #   None, which would stand inside the trunk). See the report §4 for the kit-side
        #   follow-up: `SCENE_SPECIES["Scene13"]` should become `("ash", None)`, after
        #   which the beds and the row are one species with no scene edit at all.
        for i, p in enumerate(PARAMS["planters"]):
            sc.build_planter(
                stage, f"{ROOT}/Planter_{i}", p["cx"], p["cy"], 0.0,
                M["cope"] if i % 2 else M["wall_b"],
                M["grass_b"] if i % 2 else M["grass"],
                tree_mtls=tree_mtls if p["tree"] else None,
                size=p["size"], curb_h=pl["curb_h"], curb_t=pl["curb_t"],
                cap_over=pl["cap_over"], cap_h=pl["cap_h"],
                grass_h=pl["grass_h"])
        # [W3 K4(b) · G13] the monospecific street row, at TREE_PITCH_M = 8.0 m
        n_tree = 0
        for r, row in enumerate(PARAMS["tree_rows"]):
            for k in range(int(row["n"])):
                tx = row["x0"] + k * PARAMS["tree_pitch"]
                sc.build_tree(stage, f"{ROOT}/Tree_{r}_{k}", tx, row["y"], 0.0,
                              *tree_mtls, species=TREE_SPECIES,
                              trunk_h=PARAMS["tree_trunk_h"])
                n_tree += 1
        print(f"[K4(b)] 노선대(route) 가로수 {n_tree}주 · 단일수종 "
              f"'{TREE_SPECIES}' · 피치 {PARAMS['tree_pitch']:.1f} m "
              f"(TREE_PITCH_M) · 갓길대(verge) 화단수 "
              f"{sum(1 for p in PARAMS['planters'] if p['tree'])}주 = "
              "SCENE_SPECIES['Scene13'] 행")
        for i, (hx0, hy0, hx1, hy1) in enumerate(PARAMS["hedges"]):
            sc.build_hedge(stage, f"{ROOT}/Hedge_{i}", hx0, hy0, hx1, hy1,
                           0.85, base_z=0.0)
        for i, (bx, by, yaw, bz) in enumerate(PARAMS["benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{i}", bx, by, bz,
                           M["wood"], yaw=yaw)
        sl = PARAMS["streetlight"]
        for i, (lx, ly) in enumerate(PARAMS["streetlights"]):
            base = f"{ROOT}/Streetlight_{i}"
            CYL(f"{base}/Pole", (lx, ly, sl["pole_h"] / 2.0), sl["pole_r"],
                sl["pole_h"], M["post"], col=True)
            CYL(f"{base}/Arm", (lx - sl["arm_len"] / 2.0, ly,
                                sl["pole_h"] - 0.12),
                sl["arm_r"], sl["arm_len"], M["post"], rotY=90.0)
            BOX(f"{base}/Head", (lx - sl["arm_len"], ly, sl["pole_h"] - 0.17),
                (sl["head"], sl["head"], 0.12), M["lamp"])
        for i, (key, bd) in enumerate(PARAMS["buildings"].items()):
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["shell"] if i % 2 == 0 else M["shell_b"],
                              M["glass"], M["parapet"],
                              window=PARAMS["window"])
        build_utility(M)

    def build_utility(M):
        """[W3 S13 · G13] utility pole + transformer + overhead spans (backdrop only).

        G13's single strongest "Korean mid-rise street" cue after the gantry. It stands
        on the far verge (y ≈ 11.6), outside every judged near-ground cone, and carries
        no collider — it is scenery, not an obstacle.
        """
        po = PARAMS["pole"]
        anchors = []
        for i, (px, py, has_tr) in enumerate(PARAMS["poles"]):
            CYL(f"{ROOT}/Pole_{i}/Shaft", (px, py, po["h"] / 2.0), po["r"],
                po["h"], M["post"], col=True)
            for k, az in enumerate(po["arm_zs"]):
                BOX(f"{ROOT}/Pole_{i}/Arm_{k}", (px, py, az),
                    (po["arm_t"], po["arm_len"], po["arm_t"]), M["post"])
            if has_tr:
                CYL(f"{ROOT}/Pole_{i}/Transformer",
                    (px + po["r"] + po["tr_r"] * 0.6, py, po["tr_z"]),
                    po["tr_r"], po["tr_h"], M["post"])
            anchors.append((px, py))
        # spans between consecutive poles — parabolic sag, chords tilted about Y
        for s, (a, b) in enumerate(zip(anchors[:-1], anchors[1:])):
            for w, dy in enumerate(po["wire_ys"]):
                z = po["arm_zs"][0] if abs(dy) > 1e-6 else po["arm_zs"][1]
                pts = pk.rope_span_points((a[0], a[1] + dy, z),
                                          (b[0], b[1] + dy, z),
                                          sag=po["sag"], seg=int(po["seg"]))
                for c, (p, q) in enumerate(zip(pts[:-1], pts[1:])):
                    dx, dz = q[0] - p[0], q[2] - p[2]
                    L = math.hypot(dx, dz)
                    CYL(f"{ROOT}/Wire_{s}_{w}_{c}",
                        ((p[0] + q[0]) / 2.0, p[1], (p[2] + q[2]) / 2.0),
                        po["wire_r"], L, M["dark"],
                        rotY=90.0 - math.degrees(math.atan2(dz, dx)))

    # ── Scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    ramp_mtl = M["conc"] if cfg["cue_material_break"] else M["paving"]
    stair_mtl = M["conc"] if cfg["cue_material_break"] else M["paving"]

    build_ground(M)
    build_paving(M)
    build_cross_ramps(M)             # [W3 GT-5] driveway / stair-head turn-downs
    build_curbs(M)                   # [W3 GT-5 · K5] 보차도 경계석 4선
    if cfg["hazard_stairs"]:
        build_ramp(M, ramp_mtl)
        build_ground_kit(M)          # [W2] kerbs (M4) · entry asphalt · trench · paint
        build_trench_walls(M)
        build_stair(M, stair_mtl)
        build_underground(M)
        build_entry_gear(M)          # [W3 S13] gantry sign (the porch canopy is gone)
        build_wall_graphics(M)       # [W3 S13 · G13] chevrons + reflective strip
        build_ramp_marks(M)          # [W3 S13 · G13] yellow centre line + kerb blocks
        build_bollards(M)
        if cfg["cue_railing"]:
            build_railings(M)
        if cfg["cue_tactile"]:
            build_tactiles(M)
        if cfg["cue_sign"]:
            build_signs(M)
    else:
        build_flat_fill(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

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

    if capture_mode:
        out_dir = os.path.join(LOOKCHECK_DIR, "auto")
        sc.capture_pipeline(simulation_app, build_views(), out_dir,
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene13_{ts}.png")
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
