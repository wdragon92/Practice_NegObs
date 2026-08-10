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
  ramp deck compresses into a plane of the same brightness and material as the ground
  (08-05: the full-length canopy shades the trench, so the *brightness* leg of the
  illusion weakens by design — the geometric compression leg is untouched).
  Beyond that, the x >= 24 m stretch is roofed by the upper slab (surface planting), so
  **the ground beyond the opening (z=0) reads as continuous with the near sidewalk**
  -> a textbook negative obstacle.
  Guarding (08-05): the railing around the ramp opening is **continuous** — the old
  south-side 3 m removal (x 10.5~13.5) is repaired per the user's gallery answer and
  the 08-05 doctrine (the guard itself is the drop cue, not its damage). The flush
  coping (no G13 parapet) remains the scene's below-code identity.
  [08-06 · GT-64] The stair head keeps its registered 3.96 m drop edge at x = 11.20
  (unmoved), but it is no longer an *open* mouth: the east face of the stair box is
  a Korean basement-stair entrance — a steel frame over the descending flight, fixed
  glass over the rest — so the only passage is the door and nobody can step past its
  edge into the shaft.
  [08-06 · GT-72] The double leaf becomes a **single leaf modelled OPEN** (95 deg
  hold-open on the south jamb) with a fixed sidelight filling the rest of the clear
  opening. With the leaf swung clear, the descent is directly visible through the
  doorway — that is now the primary drop cue, backed by the centre guard line and
  the coped east rim. GT-73 makes the glazing translucent, so the descent also
  reads *through* the fixed panes.

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

[08-05 user override · U-5 literal] The gallery answer (08-05) re-reads U-5 as written:
  the open trench is covered for its whole length after all ("이런 입구에는 보통 캐노피가
  달려있다 — 덮여 있어야 한다"). R13-1's real-practice reading is superseded **for the
  canopy clause only**; everything else in §7-5 (gantry sign, height bar, wall graphics,
  markings) stands. The cover is the library's flat-deck canopy idiom (scene02 GT-3 /
  scene16, no new geometry idiom): RC deck x 0…24.0 on coping-mounted steel columns.
  [08-05 user, 5th answer] the deck connects to the mouth (x0 2.75 → 0.0): the
  free-standing gantry frame is deleted — the height bar hangs from the mouth
  beam and the sign panel mounts on the west parapet band. The soffit carries 16
  recessed lamp battens (scene02 GT-3 precedent; 실무 관행) — without them the
  covered trench falls to DARK (baseline wall-shadow band measures mean 11).
  `portal_look` and `ramp_graze` are **declared under-canopy cuts** (photometric
  change intended; judged under soffit light, scene02 `pit_edge` 방식).
  Ledger row **GT-58**
  (`Docs/audit_v4/gt_changes_w3.md` §14): R-3 re-stamp — no walked surface moves,
  the OCCL baseline over the trench changes; R-1 is inert here (registry is
  drop/grade-only, all new colliders are above-ground positive obstacles).

Goal
  (1) ground split into 6 boxes that **do not cover** the ramp trench opening
      (x 0..24, y +-3.3) or the stair shaft opening (x 5..11.2, y 3.3..6.9)
  (2) straight ramp in 3 segments (transition-main-transition) + side walls and coping +
      parapet-mounted entry sign + canopy-hung height-limit bar + fee board +
      full-length flat-deck canopy x 0…24.0 (08-05 · U-5 literal, 5th: to the mouth) +
      pedestrian stair-entry canopy (08-05 2차 — U-5 는 보행 진입구에도 적용)
  (3) adjoining pedestrian stair, 24 steps (riser 0.165, width 1.4, 2 switchback flights
      + mid landing) -> basement corridor -> basement 1 car park (dim lighting — PT assumed)
  (4) statutory bollards (h0.9 · r0.08 · spacing 1.5 · reflective top band) + 0.3 m dot
      tactile in front — **only at the sidewalk/road crossing points**
  (5) estate dressing: interlocking sidewalks · planting beds · trees (build_tree v2) ·
      hedges · **4 apartment blocks, all due-south-facing E-W slabs on a 2 x 2 grid**
      (08-06 · GT-64 — base_z · inset windows)
  (6) [08-06 · GT-64] estate ROAD NETWORK: the approach carriageway no longer dies in
      the lawn at x −14 — it runs on to a north–south road (T-junction, carriageway +
      kerbs + both footways running to the scene rims y ±25.9), and the ramp crossing
      is trimmed back to run sidewalk → crossing → sidewalk instead of spearing 6.8 m
      of grass at each end.

Walking-continuity self-check table (surface -> stair -> basement -> ramp -> surface; step <= 0.165)
  ┌ #  section                 coord (x, y, z)        step / verdict
  │ 0  estate north sidewalk   (13.0,  8.20,  0.000)      flat (interlocking)
  │ 1  stair spur sidewalk     (12.4,  5.50,  0.000)      flat
  │ 2  tactile warning band    (11.65, 4.25,  0.004)      0.004 (cue_tactile)
  │ 2b entrance door threshold (11.30, 4.08,  0.000)      flat (single leaf, held
  │                                                       open 95 deg — clear 0.95 m)
  │ 3  stair head (coped rim)  (11.20, 4.25,  0.000)      ← **drop 3.96, door-guarded**
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
# [GT-73 frosted pilot · 08-11 user] NEGOBS_GLASS_FROST=1 splits the 31 vision
# panes by the `scripts/glass_boundary_check_s13.py` verdict (08-10(4), re-run
# 08-11 at HEAD — same 23/8): the 23 boundary-occluding panes take OmniGlass
# `frosting_roughness` = NEGOBS_GLASS_FROST_ROUGH (PT rough transmission — the
# descent behind them mushes instead of showing sharp), the 8 irrelevant panes
# go clear (frosting 0.0). Only meaningful with NEGOBS_GLASS_MDL=glass; OmniPBR
# has no transmission to frost. Default arm (FROST=0) authors no new material
# and binds exactly as before — byte-identical to the pre-pilot build.
# Clear-pane names are the checker's world-AABB verdict at the frozen s13
# geometry; if s13 geometry ever moves, re-run the checker before trusting them.
GLASS_FROST = os.environ.get("NEGOBS_GLASS_FROST", "0") == "1"
GLASS_FROST_ROUGH = float(os.environ.get("NEGOBS_GLASS_FROST_ROUGH", "0.35"))
GLASS_CLEAR_BAYS = {"N7", "N8", "N9", "N10", "S1", "S10"}  # Canopy/Glass_* 무관 6
#   + StairCanopy/DoorTransom · DoorSidelight (bound directly at their sites) = 8


# ===========================================================================
# [A] SCENE_CONFIG — standard 7 keys. Only hazard_stairs toggles geometry (openings filled).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False -> ramp · stairs · basement become flat z=0 (sole geometry toggle)
    "cue_railing":        True,   # railing around the ramp opening (continuous — 08-05 doctrine) + around the shaft
    "cue_tactile":        False,  # [v5.2 user] tactile paving is rare in reality — OFF by default (path kept for ablation)   # [v5 shared] urban practice — dot tactile in front of bollards and at stair head/foot
    "cue_material_break": True,   # sidewalk interlocking vs ramp/stair concrete. False -> all sidewalk paving
    "cue_sign":           True,   # [v5.2 user] arbitrary warning signs removed — only the fee board (sign_info)
    "cue_scene_dressing": True,   # planters · trees · hedges · benches · lamps · 4 apartment blocks
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
    # --- [08-06 user · GT-64 (d)] shaft EAST rim: wall + coping, was bare ground ---
    #  The W and N rims have had `ShaftWall_*` + `ShaftCope_*` since v5.1; the EAST
    #  rim (x 11.20, y 3.30…6.90) had neither, so what stood at the drop edge was
    #  **Ground_N2's cut face in the grass material** — the lip the 08-06 review saw.
    #  It now takes the trench coping idiom (0.25 m concrete facing + a 0.12 m cap
    #  with `wall.cope_over` 0.06 both sides) on every band EXCEPT the 1.40 m stair
    #  mouth, where a 120 mm upstand would be a new step on the walked route.
    #  (band_y0, band_y1, z_bot) — z_bot None = wall.z_bot (full depth). Every band
    #  edge either LAPS 20 mm into the neighbouring solid or keeps a 20 mm slot: no
    #  new coincident face is created against TrenchWall_N (y ≤ 3.30), ShaftWall_N
    #  (y ≥ 6.65) or the flight slabs (y 4.95 / 5.25).
    #   · 3.28…3.53 full depth — south sliver, lapped into the trench wall
    #   · 4.97…5.25 full depth — the pier `ShaftWall_Mid` leaves behind, held 20 mm
    #     clear of flight A so the 1.40 m clear width is untouched; it carries the
    #     centre guard's head newel and stands behind the door's north jamb
    #   · 5.23…6.67 down to −1.20 ONLY: below that is the basement corridor mouth,
    #     and the 2.76 m headroom of continuity row 9→10 must stay open. The band is
    #     a spandrel over the opening, which is exactly what hides the grass face.
    #  The mouth band gets `face` instead: a 0.10 m facing whose top stops 2 mm below
    #  grade, so it covers the 0.165 m riser-height cut face with no coplanar contact
    #  with the ground top and no change to the walked surface. It laps 20 mm into
    #  the two bands either side.
    #  `cope_drop` 0.001: the east coping sits 1 mm under the W/N coping tops, so the
    #  laps at the trench-cope and shaft-cope corners cannot produce coplanar tops
    #  (the same 1 mm device the canopy N/S parapet bands use).
    shaft_east=dict(t=0.25, cope_drop=0.001,
                    bands=((3.28, 3.53, None), (4.97, 5.25, None),
                           (5.23, 6.67, -1.20)),
                    cope_bands=((3.28, 3.53), (4.97, 6.67)),
                    face=dict(y0=3.51, y1=4.99, t=0.10, drop=0.22, gap=0.002)),
    # --- Basement corridor (stairs -> garage) ---
    corridor=dict(x0=11.2, x1=24.0, y0=5.25, y1=6.65, wall_t=0.25,
                  floor_z=_FLOOR_Z, floor_thick=0.6, ceil_z=-1.2),
    # --- Ground (estate surface) : 6 boxes leaving the 2 openings clear ---
    ground=dict(x0=-34.0, x1=46.0, y0=-26.0, y1=26.0, z_top=0.0, thick=1.2),
    # --- Paving overlay (proud of the ground) ---
    drive=dict(x0=-14.0, x1=0.0, flare_x0=-6.0, flare_y=4.2, proud=0.004),
    # ═══ [08-06 user · GT-64] estate road network — T-junction at the west end ═══
    #  "Make the end of the road continue further north and south as an intersection."
    #  A **T** is the only form the domain takes: a `+` would need buildable land on
    #  both sides of the N-S road, and west of it only 1.6 m of ground remains.
    #  [computed] geometry chain, derived from two data that do NOT move:
    #    · walk_north/walk_south west end x0 = −14.0
    #    · the E-W section's own cross-profile: carriageway half 3.3 → footway inner
    #      edge 7.2, i.e. verge 3.9, footway width 2.0
    #  → east footway  x −16.0 … −14.0  — its EAST edge lands exactly on the E-W
    #      footways' west end, so the corner is a flush plate-to-plate junction
    #      (0 mm step, no overlap): that is why cx is −23.2 and not a round number.
    #    carriageway    x −26.5 … −19.9  (6.6 m two-lane, centre −23.2)
    #    west footway   x −32.4 … −30.4  (1.6 m clear of the ground rim −34.0)
    #  All three run y −25.9 … +25.9: **100 mm short of the ground rim ±26.0** so no
    #  plate end face is coplanar with the ground box (Canopy/EndWall 10 mm rule at
    #  ground-plate scale). At that offset the paths still read as reaching the rim.
    #  The E-W link x −19.9 … −14.0 closes the last carriageway dead end (§0-2).
    #  Carriageway plates are scene-owned boxes, NOT a `ground_kit` profile → they
    #  cannot re-import manholes or weeds (GT-59). No barrier gate, no utility pole
    #  (§4-9 bans poles in scene13), no people, no vehicles.
    xroad=dict(cx=-23.2, half_w=3.3, y0=-25.9, y1=25.9,
               walk_w=2.0, verge=3.9,
               #  The N-S footway is cut by the E-W carriageway. The plates stop
               #  `gap` from the road centre so each turn-down is `ramp_run` long:
               #  0.146 / 1.9 = 7.7 % ≤ 8.3 % (identical rule to `cross_ramps`).
               gap=5.2, ramp_run=1.9, link_bollard_xs=(-15.7, -14.2),
               #  Pedestrian crossing over the N-S carriageway placed on
               #  **walk_north's own band** (y 7.2…9.2) — walk_north → east footway
               #  → crossing → west footway is then one straight line in plan, which
               #  is the alignment the 08-06 review asked for.
               cross_y0=7.2, cross_y1=9.2, cross_ys=(7.5, 9.0),
               dash_len=1.5, dash_pitch=2.6, dash_skip=6.0, polish_off=0.85),

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
        #  [08-05 user, 2nd answer] the 13-8 manhole (d5-window filler, was
        #  (-3.90, 0.00)) is DELETED — "no grass/manholes on roads". The filler
        #  role passes to a sited patch (see the gkit call); profile-level
        #  cleanup lives in ground_kit P4/P7/P8 (GT-59).
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
    #  [08-06 · GT-64] `y_far` is GONE. The crossing used to carry on 6.8 m past
    #  walk_north (to y +16) and 6.6 m past walk_south (to y −16) and stop in the
    #  lawn — the dead end the 08-06 review named. A crossing exists to join two
    #  footways: it now runs walk_south ↔ turn-down ↔ carriageway ↔ turn-down ↔
    #  walk_north and nothing more, so both of its ends land on a walked plate.
    #  (The through-route to the scene rim is the footway network itself: walk_*
    #  → the N-S footways → y ±25.9.)  Plates `Walk_CrossN2` / `Walk_CrossS2` and
    #  their two "walk_cross far end (미장식)" registry rows are deleted with it.
    walk_cross=dict(x0=-3.2, x1=-1.2, proud=0.150),   # sidewalk crossing the ramp
    #  [08-06 · GT-64] x1 30.0 → 45.9: the two long footways used to stop 16 m short
    #  of the ground rim (x 46.0) and end in grass. They now run to 45.9 — 100 mm
    #  inside the rim, the same no-coplanar offset the N-S plates use. Their WEST
    #  end x0 = −14.0 does not move: it is now a flush junction with the N-S east
    #  footway (x −16.0…−14.0) instead of a free 150 mm plate end.
    walk_north=dict(y0=7.2, y1=9.2, x0=-14.0, x1=45.9, proud=0.150),
    walk_spur=dict(x0=11.4, x1=14.4, y0=3.3, y1=7.2, proud=0.150),
    walk_south=dict(y0=-9.4, y1=-7.4, x0=-14.0, x1=45.9, proud=0.150),
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
              #  [GT-64] the N-S lines are 14…18 m west of every judged eye and are
              #  only ever seen obliquely (beauty_overview), so their 1 m rhythm is
              #  bought for the south half only — s 0…26 from y −25.9, i.e. y ≤ 0.1.
              xlod_span=(0.0, 26.0),
              drop_h=0.020, drop_taper=1.0),
    # --- Statutory bollards (per Enforcement Rule of the Act on Promotion of Mobility Convenience for the Mobility Impaired, Table 2) ---
    #     h0.9 · r0.08 · spacing 1.5 · reflective top band · 0.3 m dot tactile in front.
    #     Placed **only where vehicles might intrude** = the 2 sidewalk/road crossings.
    bollard=dict(h=0.9, r=0.08, gap=1.5, band_h=0.09, band_z=0.74,
                 band_r=0.086),
    bollard_rows=[dict(y=4.35, xs=(-2.9, -1.4), tac_y0=4.35, tac_y1=4.65),
                  dict(y=-4.35, xs=(-2.9, -1.4), tac_y0=-4.65, tac_y1=-4.35)],
    # --- [W3 S13 · G13 → 08-05 5th answer] entry sign + height-limit bar,
    #     both CANOPY-MOUNTED — the free-standing gantry frame is DELETED. ---
    #  With the deck connected to the mouth (canopy x0 = 0) a separate portal
    #  frame doubles the structure; the user's 5th answer mounts the height-bar
    #  hardware directly on the canopy. G13's identity pair (sign + bar) stays:
    #  · sign panel on the WEST parapet band: z 2.80..3.60 — laps the parapet
    #    top 3.00 by 0.20 (mounted band, not floating); y ±3.40 inside the band
    #    run (±3.468); back face x −0.01 embedded 10 mm into the fascia solid
    #    (x −0.02..0.04) — welded mount, no coplanar faces. Top 3.60 stays
    #    under `entry_approach`'s frame top at this plane (≈3.72, slope of the
    #    3.81 `[measured, pilot 260730_w3_s13]` figure at x 0.40).
    #  · height bar (posted 2.30) hung from the MOUTH BEAM (station x 0.40):
    #    hangers z 2.35..2.54 — 40 mm into the bar top, 20 mm into the beam
    #    soffit (2.52). Tips y ±3.05 keep clear of the glass planes ±3.15
    #    (4th answer).
    #  [08-06 user · GT-72] the panel was a bare 6.80 × 0.80 m slab whose top and
    #  two ends were raw cut faces 0.60 m clear of the parapet band. It gets the
    #  band's own idiom: a cap coping 20 mm proud on 3 sides + two end stiles, so
    #  every edge of the sign is a member and not a cut.
    entry_sign=dict(x_back=-0.01, panel_t=0.12, y_half=3.40, z0=2.80, z1=3.60,
                    cap_t=0.06, cap_over=0.02, stile_t=0.06),
    height_bar=dict(x=0.40, z=2.30, r=0.09, y0=-3.05, y1=3.05, nseg=8,
                    hanger_t=0.05, hang_y=2.95, hang_z0=2.35, hang_z1=2.54),
    # --- [08-05 user · U-5 literal] full-length ramp canopy — R13-1 superseded ---
    #  Form = the library's flat-deck canopy idiom (scene02 GT-3 / scene16): RC deck +
    #  fascia band + transverse beams + steel columns. No new geometry idiom.
    #  · x0 0.0 [08-05 user, 5th answer]: the deck connects to the mouth — the
    #    old x0 2.75 "gantry daylight" rationale is retired with the gantry
    #    frame itself. The glass walls end under the deck the whole run (the
    #    4th-answer free-pane top channel is deleted). The judged h/d preset
    #    eyes (all x ≤ −2) stay **outside** the deck, same discipline as scene02.
    #  · col_mouth_x 0.40: one extra column pair + beam at the height-bar
    #    station — the bar hangs from this beam (entry_sign note above); the
    #    beam stays clear of the W parapet band (beam x 0.34..0.46 vs band
    #    x −0.02..0.04).
    #  · z_roof 2.70 (underside): > height-bar 2.30; sign band top 3.60 above
    #    deck top 2.84, so the sign reads over the roofline in `entry_approach`.
    #  · columns y=±3.15 stand ON the trench coping (base_z = rail base 0.12), pitch
    #    2.90 = 2 × rail spacing 1.45 with col_x0 on a post station — the south run's
    #    posts at those stations sit fully inside the column section (welded base in
    #    practice; cylinder enclosed by box → no coplanar faces, no Z-fighting).
    #    Column inner face 3.08 > traffic envelope 3.0. North columns x 5–11.2 stand
    #    clear of the shaft rim (opening at y ≥ 3.3, column ≤ 3.22).
    #  · embed 0.02: column/beam/fascia tops sink 20 mm into the deck so no contact
    #    face is coplanar with the deck underside.
    #  · fascia_proud 0.02: the band ring projects 20 mm past the deck rim on all
    #    4 sides (RC drip-edge detail) — verify round r1 found the flush ring
    #    bit-exact coplanar with the deck rim planes over the 20 mm embed band.
    #    Corners: W/E bands run the full width; N/S bands tuck 2 mm INTO the W/E
    #    solids, so every corner is solid and no two fascia faces are coplanar.
    #  · beams ride the 8 column stations (beam_w 0.12 < col_w 0.14 → bearing
    #    reads welded, no coplanar flank) — verify r1 had free-pitch beams
    #    interpenetrating the k=1 columns by 27.5 mm mid-air.
    #  · soffit lamps (scene02 GT-3 precedent — "without them the enclosure turns
    #    the whole descent into a DARK cut", and 램프 조명은 실제 관행): 2 rows of
    #    recessed battens at mid-bay stations (7 × 2 = 14), each with a SphereLight.
    #    Verify r1 measured the baseline's wall-shadow band at mean 11 (DARK < 25)
    #    with the trench OPEN — the deck removes direct sun from all but ~0.4 m of
    #    the 6 m width, so unlit soffit ⇒ portal_look/ramp_graze unjudgeable.
    #  [08-05 user, 3rd answer] **Redefined as a building-form structure**:
    #    (1) fascia -> parapet band (fascia_top 3.00 — 0.16 above the deck top
    #    2.84, 45 mm under the gantry panel bottom 3.05), (2) both flanks take
    #    **glass curtain walls** instead of railings (scene06 DeckGlass 3-part
    #    idiom: kick band + glass t0.019 + joints, columns act as mullions),
    #    (3) the east end x 23.90..24.0 closes with a solid end wall (portal
    #    head — also masks Ground_E's exposed west face). The only opening is
    #    the west entry mouth -> "completely wrapped".
    canopy=dict(x0=0.0, x1=24.0, y_deck=3.45, y_col=3.15,
                z_roof=2.70, roof_t=0.14, fascia_h=0.45, fascia_t=0.06,
                fascia_top=3.00, fascia_proud=0.02,
                col_w=0.14, col_x0=3.15, col_pitch=2.90,
                n_col=8, col_mouth_x=0.40, beam_w=0.12, beam_h=0.20, embed=0.02,
                #  [4th answer] glass_x0 0.0: curtain walls run to the trench
                #  edge. [5th answer] the deck now covers that whole run, so
                #  every pane top embeds into the deck — no free-pane channel.
                #  [08-06 user · GT-72] "protruding glass edges … everything
                #  capped or set back". Bay 0 used to start at x 0.012 and the
                #  kick band at x 0.000, so 2.3 m of RAW PANE EDGE and a raw
                #  band end faced the approach at the mouth (the parapet band
                #  only covers z 2.55…3.00). A curtain wall ends in a mullion:
                #  `mouth_mull` is a 0.14 section at x 0.00…0.14 on the coping,
                #  and bay 0 then measures −0.012 wide and is dropped by the
                #  existing 0.05 m minimum-bay guard — the run starts at the
                #  mullion with the pane joint INSIDE the section. `glass.x0`
                #  stays 0.0, so the smoke's guard-continuity gate is untouched.
                glass=dict(t=0.019, joint=0.012, kick_h=0.12, kick_t=0.05,
                           x0=0.0),
                #  x 0.06 (not 0.07): the section then runs x −0.01…0.13, i.e.
                #  10 mm PAST the kick band's west end face at x 0.00, so that
                #  face is buried instead of coplanar with the mullion's own.
                mouth_mull=dict(x=0.06, w=0.14),
                end_wall=dict(x0=23.90, t_in=0.012),
                #  `[measured]` r1: scene02's 40000 -> portal_look 22.4/87.4 %
                #  (unjudgeable) -> 160000 -> 42.6/29.7 %. [3rd answer] the glass
                #  curtain walls + end wall now block the flank daylight ->
                #  raised again to 280000 (re-measure and adjust if needed).
                lamp_y=(-1.85, 1.85), lamp_len=1.20, lamp_w=0.14, lamp_t=0.06,
                lamp_radius=0.10, lamp_intensity=280000.0,
                lamp_color=(0.93, 0.96, 1.0)),
    # --- [08-05 user, 2nd answer] pedestrian stair-entry canopy — U-5 applies
    #   to the pedestrian entrance too. Same flat-deck idiom, pedestrian scale.
    #   - south fascia outer face y 3.48 vs ramp-canopy fascia outer 3.47 —
    #     10 mm apart: reads as two adjoining roofs, no coplanar faces.
    #   - posts land on SOLID GROUND only, dodging both openings.
    #   - the shaft's south 20 cm strip (y 3.3~3.5) stays uncovered — the cost
    #     of keeping clear of the ramp canopy.
    #  [08-05 user, 3rd answer] The stair box takes the same building form:
    #    parapet band (top 2.67) + the shaft W (x=5.125) / N (y=6.775) railings
    #    replaced by glass walls (mullions @1.55, kick band). East side (stair
    #    head) is the entry opening. W glass starts at y 3.5 — the 3.3~3.5 slot
    #    between the two structures is unreachable.
    #  [verify r2] the old east post pair (11.30, y 3.72/7.08) stood inside the
    #    0.2 m stair-mouth strip, 50 mm off the registered 3.96 m drop edge and
    #    inside flight A's clear width -> replaced by ONE newel at (11.30, 5.10):
    #    between the flight bands (A ..4.95 / B 5.25..), on solid ground east of
    #    the head (x >= 11.2), 100 mm clear of both flights. Deck cantilevers
    #    +-1.6 m in y at the east end (light roof, 3 transverse beams added).
    #    Soffit lamps 2x3 added — an unlit sealed shaft repeats the r1 DARK
    #    failure (stair_head measured 109.9 -> 57.1 without them).
    #  [4th answer] side_mode toggle: "rail" = open canopy with the shaft rail
    #    runs (PARAMS stair_rail_runs); "glass" = the round-3 glazed box.
    #  [08-05 user, 5th answer] mode set to "glass" — the 4th-answer "rail
    #    (current)" reading was a MISREAD of the instruction: the user asked
    #    for the glass wrap plus ONE descending handrail inside (see
    #    `stair_handrail`), not for the glass to be replaced by rails.
    #  [08-06 user · GT-64] the east face stops being an open mouth. Korean
    #    basement-stair standard: steel frame + closed tempered-glass double
    #    leaf over the descending flight, fixed glass over the remainder, so
    #    the DOOR IS THE ONLY PASSAGE and nobody can step past its edge into
    #    the shaft ("block the area next to it to avoid drop-off").
    #    · `east.x` 11.30 = the existing x=11.30 beam station, so the door
    #      plane, the beam over it and the jamb posts are one frame. The plane
    #      sits 0.10 m EAST of the shaft rim x 11.20 — on solid Ground_N2 —
    #      which is what lets the jambs be full posts instead of the r2
    #      half-over-the-void post.
    #    · The lone mid-mouth newel (11.30, 5.10) is DELETED (user item (e)).
    #      Its beam-support duty passes to the two jamb posts (11.30, 3.55)
    #      and (11.30, 5.00) plus a north post (11.30, 6.90): 3 bearings on
    #      the x=11.30 line instead of 1, all clear of the mouth opening.
    #  [08-06 user · GT-72] the east face is rebuilt around a **SINGLE leaf,
    #    modelled OPEN**, and the whole enclosure is re-cornered.
    #    · Clear structural opening y 3.60…4.85 = 1.25 m, split into a 0.95 m
    #      swing leaf (3.60…4.55) + a 0.06 m glazing mullion (4.55…4.61) + a
    #      0.24 m fixed sidelight (4.61…4.85, lapping the north jamb). The
    #      walked clear width is the leaf's 0.95 m ≥ 0.90 m code minimum;
    #      1.25 m in one leaf would not be a door anybody builds.
    #    · The north jamb centre moves 5.00 → **4.90 = the centre-guard rail
    #      line** (see `stair_handrail.inset`), so the guard's head return
    #      dies dead-centre in the jamb post instead of grazing its corner.
    #      Closure now reads jamb 3.50…3.60 · leaf/sidelight 3.60…4.85 ·
    #      jamb 4.85…4.95 · fixed glass 4.90…6.775 (to the NE corner post).
    #    · Hold-open geometry `[computed]`: hinge (11.38, 3.60) — 30 mm east
    #      of the frame's east face 11.35 so the swinging stile clears the
    #      jamb; at 95 deg the leaf tip lands at x 12.326, where the spur
    #      turn-down (7.3 %, top 0.004 at x 11.40) has risen to 0.072. The
    #      leaf is therefore hung at `leaf_z0` 0.080 → **8 mm clearance, zero
    #      interpenetration**, and the undercut is the price of a door that
    #      opens over a turn-down whose start (x 11.40) may not move. A
    #      jamb-mounted stay arm holds it there.
    #    · NE corner: the north glass used to stop at x 11.20 while the east
    #      glass ran on to y 6.90 — two planes crossing with 0.10/0.125 m of
    #      free pane past the corner. Both runs now die in ONE corner post at
    #      (11.30, 6.775), which also takes over the beam bearing the old
    #      (11.30, 6.90) post carried (0.475 m of light-deck cantilever north
    #      of it). NW corner + the W run's south end get the same treatment
    #      (`glass_posts`), so no curtain-wall run ends in a free pane edge.
    stair_canopy=dict(x0=4.60, x1=11.90, y0=3.50, y1=7.30, z_roof=2.45,
                      roof_t=0.10, fascia_h=0.28, fascia_t=0.05,
                      fascia_top=2.67, fascia_proud=0.02, post_w=0.10,
                      embed=0.02, side_mode="glass",
                      posts=((4.85, 3.72), (4.85, 7.08), (11.30, 3.55),
                             (11.30, 4.90), (11.30, 6.775)),
                      beam_xs=(4.85, 8.10, 11.30), beam_w=0.08, beam_h=0.14,
                      glass_w=dict(c=5.125, a0=3.56, a1=6.775),
                      glass_n=dict(c=6.775, a0=5.125, a1=11.30),
                      #  (x, y, section) — curtain-wall terminal posts. They stand
                      #  on the shaft coping (top 0.12), not over the opening.
                      glass_posts=((5.125, 3.56, 0.12), (5.125, 6.775, 0.12)),
                      #  `kick_z0` −0.02 (was `base` − 0.02 = 0.10): the N run now
                      #  reaches x 11.30, i.e. 0.10 m past ShaftCope_N's east end
                      #  (11.20) onto Ground_N2, where a coping-based band would
                      #  float 0.10 m above grade. Taking the band to below grade
                      #  lands it on whatever is actually there — buried inside the
                      #  coping where the coping exists, standing on the ground
                      #  where it does not — with no plinth invented on the apron.
                      kick_z0=-0.02,
                      mullion=dict(w=0.05, spacing=1.55),
                      #  east entrance wall — see the note above
                      #  `y1` 6.90 = the shaft rim; the glazing itself now dies at
                      #  the NE corner post `glass_n.c` 6.775, north of which is
                      #  outside the enclosure (roof overhang), not a gap.
                      east=dict(x=11.30, y0=3.50, y1=6.90,
                                jamb_y=(3.55, 4.90), jamb_w=0.10,
                                door_y0=3.60, door_y1=4.85, door_z1=2.10,
                                #  `lap` 0.010: every infill pane laps 10 mm into
                                #  its frame member instead of sitting flush, the
                                #  same no-coplanar rule the canopy fascia uses.
                                leaf_w=0.95, leaf_t=0.05, glass_t=0.019,
                                stile=0.06, lap=0.010,
                                mull_y=4.58, mull_w=0.06,
                                hinge_x=11.38, hinge_y=3.60, open_deg=95.0,
                                leaf_z0=0.080, bot_rail=0.10,
                                stay_r=0.012, stay_z=1.05, stay_u=0.30,
                                hinge_r=0.022, hinge_h=0.12,
                                sill_t=0.012, sill_over=0.05,
                                handle_r=0.016, head_h=0.06,
                                kick_h=0.14, kick_t=0.05,
                                mullion_w=0.05, mullion_span=1.55),
                      #  `[measured, GT-60]` 160000 took stair_head from dark 24.7 %
                      #  to 8.5 % with the east face still OPEN. Glazing the east
                      #  face removes that daylight path, so `lamp_intensity` is a
                      #  **round-render watch item**: keep 160000 (no guessed value
                      #  lands in the ledger) and re-measure stair_head dark % in
                      #  260806_w3_s13fix6; raise only against a measurement, the
                      #  way 40000 → 160000 → 280000 was decided for the ramp.
                      lamp_rows=(4.40, 6.00), lamp_xs=(6.00, 8.10, 10.20),
                      lamp_len=0.90, lamp_w=0.12, lamp_t=0.05,
                      lamp_radius=0.08, lamp_intensity=160000.0),
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
    # [08-05 user, 2nd answer] barrier gate DELETED on user instruction. The
    #   north rail run extends to x 0, and the canopy x0 rationale becomes the
    #   gantry-cluster daylight + judged-eye standoff (GT-59).
    # --- Signs (cue_sign) ---
    sign_info=dict(cx=-1.1, cy=4.75, yaw=170.0, w=0.9, h=0.7, pole_h=2.2),
    # [v5.2 user] arbitrary warning signs removed — stair-caution sign (sign_step) deleted.
    # --- Railing (cue_railing) : sits **on** the opening coping (base_z = coping top).
    #     [08-05] the south run is **continuous 0…24** — the old x 10.5~13.5 removal
    #     (below-code reality) is repaired per the user's gallery answer + doctrine.
    #     c = coping centreline = wall centreline (trench +-3.15 / shaft N 6.775 · W 5.125)
    rail=dict(h=0.95, post_r=0.03, rail_r=0.028, mid_r=0.018, mid_h=0.46,
              spacing=1.45, base_z=0.12),
    # [08-05 user, 4th answer] the mouth rail stubs are gone too — the glass
    #   curtain walls now run x 0..24 on both flanks, so the trench carries NO
    #   railing at all. Guard continuity = glass wall + end wall (smoke check).
    #   The stair box side guard is mode-switchable (stair_canopy.side_mode):
    #   "rail" builds the two shaft rail runs below; "glass" (current — 5th
    #   answer) builds the round-3 glass walls instead.
    rail_runs=[],
    stair_rail_runs=[dict(axis="x", c=6.775, a0=5.0, a1=11.2),
                     dict(axis="y", c=5.125, a0=3.3, a1=6.9)],
    # [08-05 user, 5th answer] descending handrail INSIDE the glazed box, at 0.85
    #   above the nosing line (BF-code 0.80~0.90) with a U-return round the
    #   landing's west nose (x 7.52). The rail line at the stair head is the
    #   08-05 doctrine's drop cue.
    # [08-06 user · GT-64] `ShaftWall_Mid` is DELETED, so the rail can no longer be
    #   wall-mounted. It is a **free-standing double-sided guard**: one two-tube STS
    #   run per flight, `mid_h` 0.45 because a bare top tube over a 0.30 m well would
    #   leave a 0.85 m gap (same section as the trench guard, `rail.mid_h` 0.46).
    # [08-06 user · GT-72] two defects the review named are fixed here.
    #   (a) "the rail pillars are not standing on the stairs": the posts ran from
    #       `nose(x) − 0.30` on rail lines y 5.00 / 5.20, i.e. inside the 0.30 m
    #       divider **well**, so all six hung in mid air over a bottomless slot.
    #       `inset` 0.05 moves both rail lines ONTO their own flight — y 4.90
    #       (flight A, edge 4.95) and y 5.30 (flight B, edge 5.25) — and every post
    #       now foots on the tread below it (`tread_embed` 20 mm) on a base plate.
    #       `post_xs` are tread MID-points (11.05 − 0.30·k, common to both flights),
    #       not the old 8.3/9.4/10.5 of which 9.4 sat exactly on a nosing.
    #       Cost: the walked width between the shaft wall and the post line is
    #       1.40 − 0.05 − 0.022 = 1.328 m ≥ 1.2 m code `[computed]`.
    #   (b) "the end of the middle rail protrudes sharply": only the TOP tube was
    #       terminated. Every run end now lands in a post or in masonry —
    #       head: `newel_x` 11.16 newel footed on tread 1 + Top/Mid returns into the
    #       door's north jamb (`jamb_x` 11.30, `jamb_embed`);
    #       landing: two U newels at `u_off` on the landing carrying Top **and** Mid
    #       cross tubes and stubs (the old U tied the top tube only);
    #       foot: `foot_newel_x` 11.32 on the corridor floor with Top/Mid returns —
    #       the old foot stub aimed at Corridor_Wall_S (y ≤ 5.25), which the new
    #       rail line y 5.30 no longer meets. Free tube ends: 6 → 0.
    #   `plate_r` 0.045 (not 0.05): at 0.05 the head newel's plate would overhang
    #   the registered drop edge x 11.20 by 5 mm. `newel_x` 11.14 for the same
    #   reason — plate x 11.095…11.185, 15 mm inside the rim, and the level
    #   returns start AT the newel so the raking tube meets it, not past it.
    stair_handrail=dict(r=0.02, h=0.85, mid_h=0.45, inset=0.05,
                        post_r=0.022, post_xs=(8.35, 9.25, 10.15),
                        plate_r=0.045, plate_t=0.012, tread_embed=0.02,
                        u_off=0.08, newel_x=11.14, jamb_x=11.30,
                        jamb_embed=0.04, foot_newel_x=11.32),
    # [08-06 user · GT-72] "there is a space at the side of the stairs — extend it
    #   further to fill the gap". Two open slots, both infilled here. NEITHER the
    #   riser count, the tread x-bands, the flight z's nor the registered 3.96 m
    #   drop edge at x 11.20 move — these are lapped fills against existing solids.
    #   · SOUTH slot y 3.30…3.55 (0.25 m): between the flight/landing south face and
    #     TrenchWall_N's north face 3.30, open to the shaft base for the whole
    #     6.20 m run. Filled per step; at the rim it laps the existing
    #     `shaft_east` band (y 3.28…3.53), so the drop edge silhouette is unchanged.
    #   · WELL slot y 4.95…5.25 (0.30 m) between the two flights: **bottomless** —
    #     nothing exists below −4.40 — which is the black slot in the review cut.
    #     Filled up to flight B's stepped top, so the well keeps the open-well form
    #     GT-64's user approved (no central wall is restored) but now has a floor.
    #   Both fills stop `reveal` 1 mm under the neighbouring tread and lap 10 mm
    #   into the flight side face: the `shaft_east.cope_drop` no-coplanar device.
    #   `reveal` also pulls both fills 1 mm back from the rim plane x 11.20 and
    #   1 mm below the structural base −4.40: the top step of each flight and the
    #   `shaft_east` bands already put a +X-facing face on x 11.20 and a −Z-facing
    #   face on −4.40, and a fill face coincident with those would z-fight over
    #   the lap band. The 1 mm is invisible and the lap is what closes the slot.
    stair_infill=dict(skirt_y0=3.30, skirt_y1=3.56,
                      well_y0=4.95, well_y1=5.26,
                      land_x0=5.24, reveal=0.001),
    # [08-06 user · GT-72] "tidy the turf strip below the door" — the 0.20 m grass
    #   band between the shaft rim (11.20) and the spur turn-down's west end (11.40)
    #   ran straight into the door frame. It becomes an interlocking apron on the
    #   walk-plate idiom: top 0.003 (1 mm under the turn-down's own 0.004 west end,
    #   so no coplanar seam), south edge butted to TrenchCope_N's north face 3.36.
    #   `x0` 11.21, NOT the rim 11.20: Ground_N2's west face sits on that plane
    #   and faces the same way, so a flush apron would z-fight along the
    #   registered drop edge. 10 mm of turf stays in the rim shadow — the same
    #   10 mm no-coplanar offset the footway plates take at the scene rim.
    door_apron=dict(x0=11.21, x1=11.42, y0=3.36, y1=7.30, proud=0.003),
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
    #  [08-06 · GT-64] "sidewalk alignment needs to be fixed" — three of the five beds
    #  overlapped a footway plate and one straddled the new N-S footway. Each bed is
    #  now proved clear of every plate it borders `[computed]`, min clearance 0.20 m:
    #   0 (−8.6, 5.25) s2.8 → y 3.85…6.65 : carriageway edge 3.30 (+0.55) ·
    #       walk_north inner 7.20 (+0.55).  was cy 6.4 s3.4 → y 8.10, 0.90 m INSIDE
    #       walk_north.
    #   1 (−12.3, −5.2) s2.6 → x −13.6…−11.0 : N-S footway east edge −14.0 (+0.40) ·
    #       y −6.50…−3.90 : carriageway −3.30 (+0.60).  was cx −12.9 s2.8 → x −14.3,
    #       i.e. 0.30 m inside the new footway.
    #   2 (16.0, 14.0) s2.4 → y 12.80…15.20 : walk_north outer 9.20 (+3.60) ·
    #       A102 south face 16.0 (+0.80).  was cy 10.9 s3.8 → y 9.00, 0.20 m inside
    #       walk_north.
    #   3 (4.3, −11.2) s2.6 → y −12.50…−9.90 : walk_south outer −9.40 (+0.50) ·
    #       A101 north face −13.0 (+0.50).  was cy −11.4 s3.0 → 0.10 m off A101.
    #   4 (27.4, −5.1) s2.8 → y −6.50…−3.70 : walk_south inner −7.40 (+0.90).
    #       was cy −6.1 s3.2 → y −7.70, 0.30 m inside walk_south.
    #  Beds 1, 2 and 4 also sit ≥ crown radius + 0.50 m off the street-row lines
    #  (`tree_keepout` treats a bed as a structure), so they cost the rows no
    #  station — only bed 3 and the x 26.9 street lamp legitimately do.
    planters=[dict(cx=-8.6, cy=5.25, size=2.8, tree=True),
              dict(cx=-12.3, cy=-5.2, size=2.6, tree=True),
              dict(cx=16.0, cy=14.0, size=2.4, tree=True),
              dict(cx=4.3, cy=-11.2, size=2.6, tree=True),
              dict(cx=27.4, cy=-5.1, size=2.8, tree=False)],
    planter=dict(curb_h=0.42, curb_t=0.22, cap_over=0.05, cap_h=0.05,
                 grass_h=0.38),
    # [W3 S13 · K4(b)] **G13's ginkgo street row.** Two monospecific rows at the library
    #  pitch `TREE_PITCH_M = 8.0`, one each side of the estate footway, replacing eight
    #  scattered specimens. Species: see `TREE_SPECIES` below.
    #  [08-06 · GT-64] the rows now FOLLOW THE ROAD NETWORK: two along the E-W
    #  approach (verges outside each long footway) and two along the new N-S road
    #  (in its 3.9 m verges, x −17.95 / −28.45 = the verge centrelines `[computed]`).
    #  `axis` names the run direction; `c` is the constant coordinate.
    #  Stations are a strict pitch-8.0 arithmetic run — none is nudged. A station
    #  that fails the clearance test in `tree_keepout()` is DROPPED, not moved
    #  (a Korean street row is omitted where a structure or a lamp occupies the
    #  verge; nudging would break §4-4's legal 4~8 m pitch).
    tree_rows=[dict(axis="x", c=9.55, a0=-13.0, n=7),      # E-W road, north verge
               dict(axis="x", c=-9.75, a0=-13.0, n=7),     # E-W road, south verge
               dict(axis="y", c=-17.95, a0=-24.0, n=7),    # N-S road, east verge
               dict(axis="y", c=-28.45, a0=-24.0, n=7)],   # N-S road, west verge
    tree_pitch=8.0,
    #  [08-06 · GT-64] clearance rule the user asked for ("nothing may penetrate
    #  structures"): tree CENTRE to structure envelope ≥ crown radius + `tree_clear`.
    #  Walked plates and carriageways use `tree_clear_walk` instead — a crown may
    #  overhang a footway (that is what a street tree does), only the trunk must not
    #  stand in one.
    tree_clear=0.50, tree_clear_walk=0.15, tree_clear_lamp=0.30,
    #  `[measured, pilot 260730_w3_s13]` 4.70 (≈ 7.5 m) put a `Fraxinus` crown mass over
    #  the whole beauty cut; a Korean estate 가로수 is 5–7 m and pruned narrow. 3.90 →
    #  target 3.90 × 1.60 ≈ **6.24 m**. Both E-W rows stay at |y| ≥ 9.55, i.e. beyond
    #  CANOPY_TUNNEL_RECIPE's `d_min_broadleaf` 7.50 from the judged y = 0 axis (H16).
    #  [08-06 · GT-64] 3.90 → **3.40** (target 3.40 × 1.60 ≈ 5.44 m, still inside the
    #  5–7 m 가로수 band). This is a clearance decision, not a taste one `[computed]`:
    #  the south verge is only 3.60 m wide (walk_south outer −9.40 → the south row's
    #  north facades −13.00). Crown half-width = 4.8509/2 × trunk_h × 1.60 × 1.08 /
    #  5.3408 (Fraxinus native bbox `[measured — assets/veg_manifest_w2.json]`), so
    #    3.90 → R 3.061 → a row at y −9.75 clears the facades by 0.19 m  → the whole
    #           south row would have been culled by the new keepout test;
    #    3.40 → R 2.668 → clearance 0.582 m ≥ 0.50  → the row survives intact.
    tree_trunk_h=3.40,                 # → target height 3.40 × 1.60 ≈ 5.4 m (street row)
    #  [08-06 · GT-64] Hedge_0 moved: it used to run x −22.0…−14.6 at y 6.9…7.5, i.e.
    #  straight across the new N-S carriageway (x −26.5…−19.9) and its east verge, and
    #  its ±0.66 m foliage envelope reached y 7.86 — 0.66 m INSIDE walk_north. The band
    #  is re-laid north of the footway at y 11.4…12.0 (envelope 11.04…12.36): clear of
    #  walk_north outer 9.20 by 1.84 m and of the y 9.55 tree trunks by 1.49 m. Length
    #  7.4 m and the ±0.30 m band depth are unchanged, so the shrub count is unchanged.
    hedges=[(-13.0, 11.4, -5.6, 12.0), (14.2, -6.9, 21.3, -6.3),
            (2.4, 12.2, 9.6, 12.8)],
    # [08-05 user, 5th answer · GT-62] "is that really the best Bush can do? It's
    #  too shiny to be called a bush" — the box+crown-blob hedge (grass-projected
    #  spheres) reads as glossy topiary balls. Each band becomes a row of real
    #  clipped-shrub USDs (place_shrubs); the three rects above and the ~0.85 m
    #  silhouette are unchanged, roots {ROOT}/Hedge_{i} kept for A/B.
    #  · Species pinned to ONE for the whole estate (S-1/S-2 spirit — a Korean
    #    estate clips a single hedge species): `Privet` (쥐똥나무), the classic
    #    Korean hedge and the lightest of the Privet/Boxwood/Holly trio (147 k
    #    tri). Per-band seeds keep jitter sequences distinct (no cloned rhythm).
    #  · target_h 0.78 × (1+overlap 0.10) ≈ 0.86 exposed ≈ the old 0.85 box.
    #    Scaled width ≈ 1.704 × 0.78×1.10/1.114 ≈ 1.31 m (min 1.21 at −8 %
    #    jitter); pitch ≤ 0.70 → neighbours always fuse ≥ 0.5 m into one
    #    continuous clipped band, not discrete balls (§4-1 trimmed-band intent).
    #  · Cross-band envelope ±0.66 m off the centreline: Hedge_1 (cy −6.6)
    #    reaches y −7.31 vs walk_south edge −7.4 (clear 0.09), Hedge_0 foliage
    #    x ≤ −14.44 vs walk_north west end −14.0 (clear 0.44) — no walk overlap.
    hedge=dict(target_h=0.78, overlap=0.10, pitch=0.70, end_margin=0.50,
               jit_along=0.06, jit_across=0.04,
               pool=["Shrub/Privet.usd"]),
    # (bx, by, yaw, base_z) — bench 0 stands on walk_north, which is now at +0.150
    #  [08-06 · GT-64] bench 2 (−13.6, −7.1) sat on bare verge grass 0.40 m off the new
    #  N-S footway edge; it moves onto walk_south itself (y −9.4…−7.4, plate top 0.150).
    #  Seat depth 0.40 about y −7.9 → y −8.10…−7.70, leaving 1.30 m of clear walking
    #  width on the 2.0 m plate `[computed]` (BF minimum 1.2 m).
    benches=[(-9.4, 8.3, 174.0, 0.150), (17.3, 12.6, -6.0, 0.0),
             (-11.0, -7.9, 3.0, 0.150)],
    # [08-05 user, 2nd answer] G13's utility pole / transformer / overhead-wire
    #  signature is DELETED — "don't add assets that weren't instructed". A
    #  deliberate departure from the G13 reference, recorded in ledger GT-59.
    # [verify r2] middle light 12.6 -> 13.4: its 1.0 m arm head (x 11.6) hung
    #   fully over the new stair-canopy roof (deck x1 11.9) and lit the roof,
    #   not the spur walkway.
    streetlights=[(-7.2, 6.95), (13.4, 7.05), (26.9, -7.2)],
    streetlight=dict(pole_h=5.2, pole_r=0.075, arm_len=1.0, arm_r=0.045,
                     head=0.26),
    # ═══ [08-06 user · GT-64] APARTMENT MASTER PLAN — 4 due-south-facing slabs ═══
    #  "Make sure all the apartments face south and line them up … move the current
    #   A103 a bit further south and align it, then add A104 … in a grid-like pattern."
    #  Every block is now an E-W slab with `axis="y"`, `facade_y = y0`, `face_dir −1`:
    #  the windowed face is the SOUTH face, which is Korean 정남향 practice and the
    #  literal instruction. A101 keeps its footprint (x 0…36, y −22…−13) and only
    #  flips its facade (was facade_y −13 / face_dir +1 = north-facing).
    #
    #  Grid `[computed]` — 2 rows x 2 columns, columns aligned to the metre:
    #    south row  y −22.0 … −13.0 : A104 x −13.0…−3.0 · A101 x 0.0…36.0
    #    north row  y  16.0 …  25.0 : A103 x −13.0…−3.0 · A102 x 0.0…36.0
    #  · Row depth 9.0 m for all four (A101's, so the rows read as one grid).
    #  · West column x0 = −13.0: 1.00 m clear of the new N-S footway (x −14.0).
    #    (The centre-ray-only 1.11 m clearance argument for the old beauty_overview
    #    eye proved insufficient — the half-frustum still hit A104's west gable at
    #    4 m, so that eye moved to the open corridor axis; see build_views. The 15
    #    cut names and count are unchanged.)
    #  · West column length 10.0 m is the floor, not a choice: `window.margin` 2.2
    #    x2 + `col_step` 2.7 needs 9.94 m for a second window column, and a
    #    one-column facade reads as a blank tower.
    #
    #  COMPROMISES, stated rather than hidden:
    #  · 인동간격 (채광 이격) wants 0.8H = 36.0 m between rows for A101's H = 45.0.
    #    A101's north face is fixed at y −13.0 and the ground rim is y +26.0, so the
    #    largest row spacing the domain can hold with a 9 m north row and a 1 m rim
    #    margin is **29.0 m = 0.64H** `[computed]`. Taken; recorded.
    #  · Side gap inside a row is 3.0 m (A104 x1 −3.0 → A101 x0 0.0), below the 4 m
    #    측벽 minimum. The south row physically cannot hold two slabs at 6 m: A101
    #    occupies 36 of the 58 m between the N-S footway and the east rim. 3.0 m sits
    #    with this scene's declared below-code identity (flush coping, no tactile).
    #  · Only A101 and A102 are true 판상형 (L/W 4.0). A104/A103 are L/W 1.11 corner
    #    blocks — the honest consequence of a 58 m band with a 36 m fixed slab in it.
    #
    #  NOON SHADOWS `[computed]` — derived in `sun_shadow()` from PARAMS["light"], not
    #  quoted: dome rot −110.0 + SUN_AZ_OFFSET 171.5 = 61.5, sun rotZ 61.5 + 233.5 =
    #  295.0, rotX 90 − 49.79. Sun vector (0.5851, 0.2728, −0.7638) → **shadows run
    #  ENE on bearing 65.0° at 0.8451 m per metre of height**, i.e. offset
    #  (+0.7660 h, +0.3571 h).
    #  · Sweep the footprints forward: a block shades y = 0 only if y1 + 0.3571 h ≥ 0.
    #    A104/A103 h 36 → +12.86; A101 h 45 → +16.07; A102 h 39 → +13.93.
    #    South row y1 = −13.0 → A104 reaches y −0.14 (never crosses the axis) and
    #    A101 reaches y +3.07 but only from x ≥ 27.9, i.e. east of the portal x 24
    #    and 28 m east of the ramp mouth. The north row's shadow travels away from
    #    the road entirely. **The approach carriageway x −19.9…0 stays unshaded.**
    #  · Judged eye stations (y = 0, x −2…−12, h ≤ 1.8) run the test backwards: a
    #    caster must lie at (x_P − 0.9064 d, −0.4226 d) with height ≥ 1.1833 d − z_P.
    #    The south row's y-band −22…−13 is met at d 30.8…52.1 m, i.e. at x −29.9…
    #    −49.2 and a required height of 36.4…61.6 m — outside both the west column
    #    (x −13.0…−3.0) and the domain. **Every preset eye stays in full sun.**
    #  Both legs are re-derived and printed by the smoke run, not restated.
    #  · Basement clearances: garage x 24…38 y ±9.3 and corridor x 11.2…24
    #    y 5.25…6.65 lie between the two rows; nearest block face is A101 y1 −13.0,
    #    3.70 m south of the garage rim, and A102 y0 16.0, 6.70 m north of it.
    #  · §0-2: no block straddles y = 0 (the E-W road axis) and none reaches
    #    x ≤ −14.0 (the N-S road axis) — both corridors run open to the scene rim.
    buildings=dict(
        A101=dict(x0=0.0, x1=36.0, y0=-22.0, y1=-13.0, h=45.0, floors=15,
                  axis="y", facade_y=-22.0, face_dir=-1.0, base_z=0.0),
        A102=dict(x0=0.0, x1=36.0, y0=16.0, y1=25.0, h=39.0, floors=13,
                  axis="y", facade_y=16.0, face_dir=-1.0, base_z=0.0),
        # A103 was the far-west backdrop slab (x −46…−34, y −5…26, N-S, facade
        #   east). It comes south and east into the north row and aligns with A102
        #   on the same y0/y1 and with A104 on the same x column.
        A103=dict(x0=-13.0, x1=-3.0, y0=16.0, y1=25.0, h=36.0, floors=12,
                  axis="y", facade_y=16.0, face_dir=-1.0, base_z=0.0),
        # A104 — new. 12 floors x 3.0 m = 36.0 m, the same as A103 so the west
        #   column reads as a pair.
        A104=dict(x0=-13.0, x1=-3.0, y0=-22.0, y1=-13.0, h=36.0, floors=12,
                  axis="y", facade_y=-22.0, face_dir=-1.0, base_z=0.0),
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
        # [08-06 user · GT-73] vision glass — the canopy curtain walls, the stair
        #   box and the door. `glass_*` above stays the OPAQUE spandrel/window
        #   look and still binds the 4 apartment blocks (a translucent window on a
        #   solid shell would show the shell, not a room). The tint is the pane's
        #   own colour, so at opacity 0.35 the descent behind it stays legible.
        glass_v_color=(0.55, 0.66, 0.68), glass_v_opacity=0.35,
        glass_v_rough=0.05, glass_v_ior=1.49,
        parapet_color=(0.60, 0.60, 0.58), parapet_rough=0.62,
        shell_tint=(0.86, 0.84, 0.80), shell_tint_b=(0.80, 0.79, 0.78),
        # [v6 C-3] canopy slab = a 6x5 m untextured white board (styrofoam carport) ->
        #   concrete texture + fascia band. [08-05] `roof_tint/scale` + `fascia_*`
        #   are read again by the full-length canopy; `roof_color/rough` stay unread.
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


# ===========================================================================
# [C2c] GT-64 derivations — north-south road, sun shadows, street-tree culling.
#       Same discipline as [C2b]: every number the landing record quotes is
#       produced HERE from PARAMS, so it is a measurement and not a restatement.
# ===========================================================================
def xroad_geom():
    """[GT-64] the north-south road's derived coordinates — one source of truth for
    the paving, kerb, ramp, bollard, tree and smoke code.

    `car0/car1` carriageway · `we0/we1` east footway · `ww0/ww1` west footway ·
    `gap` the half-width of the hole the E-W carriageway cuts in the east footway.
    The east footway's OUTER edge is `walk_north["x0"]` by construction, so the
    E-W footways butt onto it with a 0 mm step (checked in the smoke run).
    """
    xr = PARAMS["xroad"]
    car0 = xr["cx"] - xr["half_w"]
    car1 = xr["cx"] + xr["half_w"]
    we1 = float(PARAMS["walk_north"]["x0"])
    we0 = we1 - xr["walk_w"]
    ww1 = car0 - xr["verge"]
    ww0 = ww1 - xr["walk_w"]
    return dict(car0=car0, car1=car1, we0=we0, we1=we1, ww0=ww0, ww1=ww1,
                y0=float(xr["y0"]), y1=float(xr["y1"]), gap=float(xr["gap"]),
                verge_e=(car1 + we0) / 2.0, verge_w=(ww1 + car0) / 2.0)


def xroad_curb_lines():
    """[GT-64] the six kerb face lines of the north-south road.

    Same tuple shape as `curb_lines()` — `(tag, p0, p1, road_side, drop_spans)` with
    `drop_spans` in arc length from `p0`. Runs go +Y, so the LEFT normal is −X
    (`infra_kit._line_frame`): a line whose carriageway is to the west is "left".

    The east footway is CUT by the E-W carriageway, so its two lines are built as
    four segments that stop at `±gap` — the turn-down ramps in between carry no
    kerb, exactly as `walk_cross`'s two arms do not.
    """
    xg = xroad_geom()
    xr = PARAMS["xroad"]
    y0, y1, gp = xg["y0"], xg["y1"], xg["gap"]
    cy0, cy1 = float(xr["cross_y0"]), float(xr["cross_y1"])
    wn, ws = PARAMS["walk_north"], PARAMS["walk_south"]
    out = []
    #  east footway, road-side line (carriageway to the −X side)
    out.append(("XE_in_S", (xg["we0"], y0), (xg["we0"], -gp), "left", ()))
    out.append(("XE_in_N", (xg["we0"], gp), (xg["we0"], y1), "left",
                ((cy0 - gp, cy1 - gp),)))
    #  east footway, far-side line — 턱낮춤 where walk_north / walk_south abut
    out.append(("XE_out_S", (xg["we1"], y0), (xg["we1"], -gp), "right",
                ((ws["y0"] - y0, ws["y1"] - y0),)))
    out.append(("XE_out_N", (xg["we1"], gp), (xg["we1"], y1), "right",
                ((wn["y0"] - gp, wn["y1"] - gp),)))
    #  west footway — uncut (the E-W road terminates on the far side)
    out.append(("XW_in", (xg["ww1"], y0), (xg["ww1"], y1), "right",
                ((cy0 - y0, cy1 - y0),)))
    out.append(("XW_out", (xg["ww0"], y0), (xg["ww0"], y1), "left", ()))
    return out


def xroad_ramps():
    """[GT-64] the four new turn-downs of the intersection.

    `(tag, axis, pivot, rot, x0_local, z_hi, run, drop, a0, a1)`. `axis="y"` entries
    fall along ±Y and are authored inside a `build_rot_group` (the `cross_ramps`
    idiom); `axis="x"` entries fall along ±X and go straight into `build_slope`
    (the `WalkRamp_Spur` idiom, negative drop = rises toward +X).

    · N/S : the east footway meeting the E-W carriageway. Its plates stop at
      ±`gap` and the road edge is at ±ramp.y1, so the run is `ramp_run` = 1.9 m
      → 0.146 / 1.9 = **7.7 %**.
    · E/W : the crossing over the N-S carriageway, on walk_north's own band. Here
      the ramp has to bridge the whole 3.9 m VERGE, footway inner edge to
      carriageway edge, or it would leave a 150 mm step out in the grass
      → run = `verge` 3.9 m, 0.146 / 3.9 = **3.7 %**.
    Both figures are ≤ 8.3 % and both are re-derived in the smoke run.
    """
    xg, xr = xroad_geom(), PARAMS["xroad"]
    z_hi, z_lo = float(PARAMS["walk_north"]["proud"]), float(PARAMS["drive"]["proud"])
    run, drop = float(xr["ramp_run"]), z_hi - z_lo
    vg = float(xr["verge"])
    xm, hw = (xg["we0"] + xg["we1"]) / 2.0, (xg["we1"] - xg["we0"]) / 2.0
    cy0, cy1 = float(xr["cross_y0"]), float(xr["cross_y1"])
    #  `a0/a1` on the `axis="y"` entries are the LOCAL cross-extent, i.e. centred on
    #  the pivot's y — `build_rot_group` maps it onto world x centred on `xm`
    #  (identical convention to `cross_ramps`, whose arms use `wn["y0"] ± hw`).
    return [
        # east footway → E-W carriageway, north arm: falls toward −Y
        ("N", "y", (xm, xg["gap"]), -90.0, xm, z_hi, run, drop,
         xg["gap"] - hw, xg["gap"] + hw),
        # east footway → E-W carriageway, south arm: falls toward +Y
        ("S", "y", (xm, -xg["gap"]), 90.0, xm, z_hi, run, drop,
         -xg["gap"] - hw, -xg["gap"] + hw),
        # N-S crossing, east arm: rises toward +X from the carriageway edge to the
        #   east footway's inner edge (car1 + verge == we0, checked in the smoke)
        ("E", "x", None, 0.0, xg["car1"], z_lo, vg, -drop, cy0, cy1),
        # N-S crossing, west arm: falls toward +X from the west footway's inner
        #   edge down to the carriageway edge (ww1 + verge == car0)
        ("W", "x", None, 0.0, xg["ww1"], z_hi, vg, drop, cy0, cy1),
    ]


def sun_shadow():
    """[GT-64] noon shadow geometry, derived from PARAMS["light"] — not quoted.

    `setup_lighting` builds the DistantLight as rotZ(rz) · rotX(90 − elev) applied
    to −Z, with `rz = noon_dome_rot + SUN_AZ_OFFSET + hdri_sun_rotz_offset`. The
    shadow of a point at height h therefore lands at `h * (dx, dy)`.
    Returns `dict(rz, elev, dx, dy, run_per_m, bearing)`.
    """
    lp = PARAMS["light"]
    rz = math.radians(float(lp["noon_dome_rot"]) + float(PARAMS["SUN_AZ_OFFSET"])
                      + float(lp["hdri_sun_rotz_offset"]))
    a = math.radians(90.0 - float(lp["noon_sun_elev"]))
    #  (0,0,-1) → rotX(a) → (0, sin a, −cos a) → rotZ(rz)
    lx, ly, lz = -math.sin(a) * math.sin(rz), math.sin(a) * math.cos(rz), -math.cos(a)
    horiz = math.hypot(lx, ly)
    run = horiz / abs(lz)                       # metres of shadow per metre of height
    return dict(rz=math.degrees(rz) % 360.0, elev=float(lp["noon_sun_elev"]),
                dx=lx / horiz * run, dy=ly / horiz * run, run_per_m=run,
                bearing=math.degrees(math.atan2(lx, ly)) % 360.0)


def tree_crown_r():
    """[GT-64] worst-case crown half-width of the street row `[computed]`.

    `build_tree` scales the species asset by `trunk_h * 1.60 * U(0.92, 1.08) /
    native_h`; `Fraxinus` measures 4.8509 x 4.5103 x 5.3409 m
    `[measured — assets/veg_manifest_w2.json]`. The +8 % tail is the one that has
    to clear, so the radius is taken at 1.08.
    """
    s = float(PARAMS["tree_trunk_h"]) * 1.60 * 1.08 / 5.3408
    return 4.8509 / 2.0 * s


def tree_keepout():
    """[GT-64] `(tag, x0, y0, x1, y1, clearance)` — what a street tree must stand off.

    `clearance` is measured from the tree CENTRE to the rectangle, so the caller
    never has to know the crown size. Two classes, per the 08-06 instruction:
      structures : crown radius + `tree_clear` (0.50 m) — "nothing may penetrate"
      walked / driven plates : `tree_clear_walk` (0.15 m) — a crown SHOULD overhang
        a footway, only the trunk may not stand in one
    """
    R = tree_crown_r()
    s = R + float(PARAMS["tree_clear"])
    w = float(PARAMS["tree_clear_walk"])
    cp, sp, sh = PARAMS["canopy"], PARAMS["stair_canopy"], PARAMS["shaft"]
    dr, xg = PARAMS["drive"], xroad_geom()
    xr = PARAMS["xroad"]
    out = [
        # -- structures --
        ("ramp canopy", cp["x0"] - cp["fascia_proud"],
         -(cp["y_deck"] + cp["fascia_proud"]), cp["x1"] + cp["fascia_proud"],
         cp["y_deck"] + cp["fascia_proud"], s),
        ("stair box", sp["x0"] - sp["fascia_proud"], sp["y0"] - sp["fascia_proud"],
         max(sp["x1"], sp["east"]["x"]) + sp["fascia_proud"],
         sp["y1"] + sp["fascia_proud"], s),
        ("stair shaft", sh["x0"], sh["y0"], sh["x1"], sh["y1"], s),
    ]
    for key, bd in PARAMS["buildings"].items():
        out.append((key, bd["x0"], bd["y0"], bd["x1"], bd["y1"], s))
    for i, p in enumerate(PARAMS["planters"]):
        h = p["size"] / 2.0
        out.append((f"planter {i}", p["cx"] - h, p["cy"] - h,
                    p["cx"] + h, p["cy"] + h, s))
    for i, (lx, ly) in enumerate(PARAMS["streetlights"]):
        # a crown must not swallow the lamp head (arm reaches −arm_len in x)
        al = float(PARAMS["streetlight"]["arm_len"])
        out.append((f"lamp {i}", lx - al, ly, lx, ly,
                    R + float(PARAMS["tree_clear_lamp"])))
    # -- walked / driven plates: trunk only --
    out.append(("E-W carriageway", dr["x0"] - 0.0, -dr["flare_y"], dr["x1"],
                dr["flare_y"], w))
    out.append(("E-W link", xg["car1"], -PARAMS["ramp"]["y1"], dr["x0"],
                PARAMS["ramp"]["y1"], w))
    out.append(("N-S carriageway", xg["car0"], xg["y0"], xg["car1"], xg["y1"], w))
    out.append(("N-S walk E", xg["we0"], xg["y0"], xg["we1"], xg["y1"], w))
    out.append(("N-S walk W", xg["ww0"], xg["y0"], xg["ww1"], xg["y1"], w))
    out.append(("N-S crossing", xg["ww1"], xr["cross_y0"],
                xg["we0"], xr["cross_y1"], w))
    for key in ("walk_north", "walk_south", "walk_spur"):
        p = PARAMS[key]
        out.append((key, p["x0"], p["y0"], p["x1"], p["y1"], w))
    wc = PARAMS["walk_cross"]
    out.append(("walk_cross", wc["x0"], PARAMS["walk_south"]["y1"], wc["x1"],
                PARAMS["walk_north"]["y0"], w))
    for i, (hx0, hy0, hx1, hy1) in enumerate(PARAMS["hedges"]):
        out.append((f"hedge {i}", hx0 - 0.66, hy0 - 0.20, hx1 + 0.66, hy1 + 0.20, w))
    return out


def _rect_gap(px, py, rect):
    """Planar distance from (px, py) to an axis-aligned rectangle (0 inside)."""
    dx = max(rect[1] - px, 0.0, px - rect[3])
    dy = max(rect[2] - py, 0.0, py - rect[4])
    return math.hypot(dx, dy)


def tree_stations():
    """[GT-64] street-row stations at `tree_pitch`, culled by `tree_keepout()`.

    Returns `(kept, dropped)`; each entry is `(row, k, x, y, tag, gap, need)`.
    A station is DROPPED, never nudged — §4-4 fixes the legal 4~8 m pitch, and a
    Korean street row simply omits a tree where a structure occupies the verge.
    """
    keep, drop = [], []
    ko = tree_keepout()
    pitch = float(PARAMS["tree_pitch"])
    for r, row in enumerate(PARAMS["tree_rows"]):
        for k in range(int(row["n"])):
            a = float(row["a0"]) + k * pitch
            tx, ty = ((a, float(row["c"])) if row["axis"] == "x"
                      else (float(row["c"]), a))
            worst = None
            for rect in ko:
                g = _rect_gap(tx, ty, rect)
                if g < rect[5] - 1e-9 and (worst is None or
                                           rect[5] - g > worst[2] - worst[1]):
                    worst = (rect[0], g, rect[5])
            if worst is None:
                keep.append((r, k, tx, ty, "", 0.0, 0.0))
            else:
                drop.append((r, k, tx, ty, worst[0], worst[1], worst[2]))
    return keep, drop


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
    # [GT-64] the two long footways changed at BOTH ends and the rows say so.
    #   west x −14.0: no longer a free 150 mm plate end — the N-S east footway abuts
    #     it at the same top z, so the row is `flat`, magnitude 0.
    #   east x 45.9: the old x 30.0 end died in grass; it now reaches the ground rim
    #     (46.0) less the 100 mm no-coplanar offset, i.e. off-domain rather than a
    #     hazard in frame. The magnitude is unchanged (the plate is still 150 mm).
    for tag, key in (("N", "walk_north"), ("S", "walk_south")):
        w = PARAMS[key]
        rows.append((f"walk_{tag} plate end x={w['x0']:.1f} (교차로 접속)", "flat",
                     f"x = {w['x0']:.1f}", w["proud"], 0.0))
        rows.append((f"walk_{tag} plate end x={w['x1']:.1f} (씬 경계)", "drop",
                     f"x = {w['x1']:.1f}", w["proud"], w["proud"]))
    # [GT-64] `walk_cross far end N/S` are GONE with the two spur plates that
    #   dead-ended in the lawn (see the `walk_cross` note in PARAMS).
    for tag, _piv, _rot, _x0, _z0, run, drop, _y0, _y1 in cross_ramps():
        rows.append((f"crossing turn-down {tag} (차량진출입부)", "grade",
                     f"{abs(drop / run) * 100:.1f} %", wc["proud"], 0.0))
    # [GT-64] the north-south road: 6 kerb lines + 4 turn-downs + 2 rim plate ends.
    #   These rows are ADDITIONS for geometry that did not exist before; no existing
    #   trench / shaft / stair / E-W kerb row moves.
    xg = xroad_geom()
    for tag, p0, p1, _side, spans in xroad_curb_lines():
        span_txt = (" · ".join(f"턱낮춤 s {a:.1f}…{b:.1f}" for a, b in spans)
                    or "턱낮춤 없음")
        rows.append((f"교차로 kerb {tag} (GT-64)", "drop",
                     f"x = {p0[0]:+.2f} · {span_txt}", cu["height"], cu["height"]))
    for tag, _ax, _piv, _rot, _x0, _z0, run, drop, _a0, _a1 in xroad_ramps():
        rows.append((f"교차로 turn-down {tag} (GT-64)", "grade",
                     f"{abs(drop / run) * 100:.1f} %", wn["proud"], 0.0))
    for tag, yv in (("S", xg["y0"]), ("N", xg["y1"])):
        rows.append((f"교차로 보도 {tag}단 (씬 경계)", "drop",
                     f"y = {yv:+.1f}", wn["proud"], wn["proud"]))
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
def _smoke_gt64(sh, po):
    """[08-06 · GT-64] road network · master plan · noon shadows · street rows."""
    xg, xr = xroad_geom(), PARAMS["xroad"]
    gr, dr = PARAMS["ground"], PARAMS["drive"]
    wn, ws = PARAMS["walk_north"], PARAMS["walk_south"]
    print("  [GT-64 도로망] 진입로 서단 → 남북 도로 T자 교차 (사용자 08-06 ②)")
    print(f"    남북 차도 x [{xg['car0']:.2f},{xg['car1']:.2f}] (폭 "
          f"{xg['car1'] - xg['car0']:.1f} m) · 동측 보도 x [{xg['we0']:.2f},"
          f"{xg['we1']:.2f}] · 서측 보도 x [{xg['ww0']:.2f},{xg['ww1']:.2f}] · "
          f"y [{xg['y0']:.1f},{xg['y1']:.1f}]")
    edge_ok = (xg["ww0"] > gr["x0"] and abs(abs(xg["y0"]) - abs(gr["y0"])) > 0.05
               and abs(xg["y0"] - gr["y0"]) < 0.5)
    print(f"    씬 경계 도달: 남북 끝 y ±{abs(xg['y0']):.1f} vs 지반 rim ±"
          f"{abs(gr['y0']):.1f} (이격 {abs(gr['y0']) - abs(xg['y0']):.2f} m — 공면 "
          f"회피) · 서측 보도 외단 {xg['ww0']:.2f} > 지반 서단 {gr['x0']:.1f} → "
          f"{'OK' if edge_ok else 'FAIL'}")
    join = abs(xg["we1"] - wn["x0"])
    link_ok = abs(xg["car1"] + xr["verge"] - xg["we0"]) < 1e-9
    print(f"    보도 접속: 동측 보도 외단 {xg['we1']:.2f} = walk_north/south 서단 "
          f"{wn['x0']:.2f} → 단차 {join * 1000:.0f} mm "
          f"{'OK (플러시 코너)' if join < 1e-9 else 'FAIL'} · 갓길대 폭 "
          f"{xr['verge']:.2f} 정합 {'OK' if link_ok else 'FAIL'} · 동서 연결차도 x "
          f"[{xg['car1']:.2f},{dr['x0']:.1f}] (구 사장 구간 소멸)")
    print(f"    보도 동단 walk_north/south x1 {wn['x1']:.1f} vs 지반 동단 "
          f"{gr['x1']:.1f} (이격 {gr['x1'] - wn['x1']:.2f}) · 횡단보도 "
          f"walk_cross y [{ws['y1']:.2f},{wn['y0']:.2f}] = 보도↔보도 "
          f"(구 y ±16 잔디 사장부 삭제) → 잔디 사장 0")
    for tag, _ax, _piv, _rot, _x0, _z0, run, drop, _a0, _a1 in xroad_ramps():
        g = abs(drop / run) * 100.0
        print(f"    교차로 턱낮춤 {tag} · run {abs(run):.2f} · 낙차 {abs(drop):.3f} "
              f"→ {g:.1f} % ({'OK ≤ 8.3 %' if g <= 8.34 else 'FAIL'})")
    print(f"    남북 차도: 씬 소유 박스(ground_kit 프로파일 아님) → 맨홀·잡초 "
          f"구조적으로 0 (GT-59) · 차단기 0 · 전주 0 (§4-9) · 사람/차량 0")

    print("  [GT-64 마스터플랜] 정남향 판상 4동 2×2 그리드 (사용자 08-06 ①)")
    bd = PARAMS["buildings"]
    ss = sun_shadow()
    print(f"    {'동':5s} {'x범위':>15s} {'y범위':>15s} {'L×W':>11s} {'h/층':>9s} "
          f"{'파사드':>10s}")
    bad_face = []
    for k in sorted(bd):
        b = bd[k]
        face = (f"y {b['facade_y']:+.1f}" if b.get("axis") == "y"
                else f"x {b.get('facade_x', 0.0):+.1f}")
        if not (b.get("axis") == "y" and abs(b["facade_y"] - b["y0"]) < 1e-9
                and b["face_dir"] < 0):
            bad_face.append(k)
        print(f"    {k:5s} [{b['x0']:6.1f},{b['x1']:6.1f}] "
              f"[{b['y0']:6.1f},{b['y1']:6.1f}] "
              f"{b['x1'] - b['x0']:5.1f}×{b['y1'] - b['y0']:4.1f} "
              f"{b['h']:5.1f}/{b['floors']:2d} {face:>10s}")
    print(f"    정남향(파사드 = y0면 · face_dir −1) 위반: "
          f"{bad_face if bad_face else '없음 → OK (4/4 정남향)'}")
    rows_y = sorted({(b["y0"], b["y1"]) for b in bd.values()})
    cols_x = sorted({(b["x0"], b["x1"]) for b in bd.values()})
    h_max = max(b["h"] for b in bd.values())
    spacing = rows_y[1][0] - rows_y[0][1]
    print(f"    행 {len(rows_y)} {['[%.1f,%.1f]' % r for r in rows_y]} · 열 "
          f"{len(cols_x)} {['[%.1f,%.1f]' % c for c in cols_x]} → 그리드 정렬 OK")
    print(f"    인동간격 {spacing:.1f} m = {spacing / h_max:.2f}H (H {h_max:.0f}) — "
          f"법정 0.8H = {0.8 * h_max:.1f} m 미달, 도메인 한계(A101 북면 y "
          f"{rows_y[0][1]:.1f} 고정 · 지반 rim {gr['y1']:.1f}) → 기재된 타협")
    side_gap = min(c1[0] - c0[1] for c0, c1 in zip(cols_x[:-1], cols_x[1:]))
    print(f"    동 측벽 이격 {side_gap:.1f} m (4 m 기준 미달 — 남측 행은 36 m 고정 "
          f"슬래브가 58 m 대역을 점유, 본 씬의 규정미달 정체성과 정합)")
    print(f"    [정오 그림자] 태양 rotZ {ss['rz']:.1f}° · 고도 {ss['elev']:.2f}° → "
          f"그림자 방위 {ss['bearing']:.1f}° (ENE) · 높이 1 m 당 "
          f"{ss['run_per_m']:.4f} m → 오프셋 ({ss['dx']:+.4f}, {ss['dy']:+.4f})/m")
    #  Forward sweep: the swept shadow of a block covers y ∈ [y0, y1 + dy·h]. A block
    #  north of the road (y0 > 0) can never reach y = 0 — the shadow runs away from it.
    road_hit = []
    for k in sorted(bd):
        b = bd[k]
        y_reach = b["y1"] + ss["dy"] * b["h"]
        if b["y0"] > 0.0:
            print(f"      {k}: 남단 y {b['y0']:+.1f} > 0 → 그림자가 축에서 "
                  f"멀어짐 (미도달 OK)")
            continue
        if y_reach < 0.0:
            print(f"      {k}: 그림자 북단 y {y_reach:+.2f} < 0 → 진입로 축 "
                  f"미도달 OK")
            continue
        span = ss["dy"] * b["h"]
        t_lo = max(0.0, min(1.0, -b["y1"] / span))
        t_hi = max(0.0, min(1.0, -b["y0"] / span))
        xa = b["x0"] + ss["dx"] * b["h"] * t_lo
        xb = b["x1"] + ss["dx"] * b["h"] * t_hi
        print(f"      {k}: y=0 교차 x [{xa:.1f},{xb:.1f}] → "
              f"{'차도(x ≤ 0) 밖 OK' if xa > 0.0 else 'FAIL(진입로 음영)'}")
        if xa <= 0.0:
            road_hit.append(k)
    #  Backward test at the judged eye stations: walk from the eye TOWARDS the sun
    #  (the −(ux, uy) direction). At horizontal distance d the sight ray to the sun
    #  is at z_eye + d / run_per_m, so a caster blocks only if it is that tall.
    ux, uy = ss["dx"] / ss["run_per_m"], ss["dy"] / ss["run_per_m"]
    eye_hit = []
    for ex, ez in ((-2.0, 0.3), (-5.0, 0.3), (-10.0, 0.3), (-12.0, 1.55)):
        for k in sorted(bd):
            b = bd[k]
            d_lo, d_hi = -b["y1"] / uy, -b["y0"] / uy      # caster-y band → d band
            if d_hi <= 0.0:
                continue                                   # north row: never in sun path
            d_lo = max(d_lo, 0.0)
            lo = max(ex - ux * d_hi, b["x0"])              # x decreases as d grows
            hi = min(ex - ux * d_lo, b["x1"])
            if lo > hi:
                continue
            d = (ex - hi) / ux                             # nearest caster = lowest bar
            if b["h"] >= ez + d / ss["run_per_m"]:
                eye_hit.append((ex, k))
    print(f"    판정 아이라인 (y 0, x −2…−12, h 0.3) 음영 캐스터: "
          f"{eye_hit if eye_hit else '없음 → OK (전 프리셋 일광)'} · 접근 차도 "
          f"음영: {road_hit if road_hit else '없음 → OK'}")
    blockers = [k for k, b in bd.items() if b["y0"] < 0.0 < b["y1"]]
    blockers += [k for k, b in bd.items() if b["x0"] < xg["we1"]]
    print(f"    [§0-2 정면축] 동서 축 y=0 · 남북 축 x {xr['cx']:.1f} 정면 건물: "
          f"{blockers if blockers else '없음 → OK (양 축 씬 끝까지 개방)'}")
    ga = PARAMS["garage"]
    near = min(abs(b["y1"] - ga["y0"]) if b["y1"] < 0 else abs(b["y0"] - ga["y1"])
               for b in bd.values())
    print(f"    지하 차고 x [{ga['x0']:.0f},{ga['x1']:.0f}] y ±{ga['y1']:.1f} · "
          f"복도 y [{PARAMS['corridor']['y0']:.2f},{PARAMS['corridor']['y1']:.2f}] "
          f"— 최근접 건물면 이격 {near:.2f} m → "
          f"{'OK' if near > 0.5 else 'FAIL'} · 두 개구 위 건물 0")
    for nm, eye in (("beauty_overview", (-31.0, -8.0, 14.0)),
                    ("bollard_walk", (-2.2, 11.0, 1.5)),
                    ("entry_approach", (-12.0, 0.0, 1.55)),
                    ("stair_head", (11.10, 4.30, 1.60))):
        inside = [k for k, b in bd.items()
                  if b["x0"] < eye[0] < b["x1"] and b["y0"] < eye[1] < b["y1"]
                  and eye[2] < b["h"]]
        print(f"    아이 {nm:15s} ({eye[0]:+.2f},{eye[1]:+.2f},{eye[2]:.2f}) 매몰: "
              f"{inside if inside else '없음 → OK'}")

    print("  [GT-64 가로수·화단] 도로망 추종 · 구조물 이격 (사용자 08-06 ④ · P-6 개정)")
    R = tree_crown_r()
    keep, drop = tree_stations()
    print(f"    수관 반경 {R:.3f} m [computed: Fraxinus 4.8509 폭 × trunk_h "
          f"{PARAMS['tree_trunk_h']:.2f} × 1.60 × 1.08 / 5.3408] · 구조물 이격 "
          f"기준 {R + PARAMS['tree_clear']:.3f} m · 보행판 {PARAMS['tree_clear_walk']:.2f} m")
    for r, row in enumerate(PARAMS["tree_rows"]):
        n_k = sum(1 for e in keep if e[0] == r)
        print(f"    행{r} axis {row['axis']} c {row['c']:+7.2f} · 스테이션 "
              f"{row['n']}(피치 {PARAMS['tree_pitch']:.1f}) → 식재 {n_k} · 제외 "
              f"{row['n'] - n_k}")
    for r, k, tx, ty, tag, g, need in drop:
        print(f"      제외 행{r}#{k} ({tx:+7.2f},{ty:+7.2f}) — {tag} 이격 "
              f"{g:.2f} < {need:.2f} m")
    print(f"    계 {len(keep)}주 · 관통 0 (모든 잔여 스테이션이 기준 충족) · "
          f"단일수종 '{TREE_SPECIES}' 행별 (S-1)")
    walks = [("walk_north", PARAMS["walk_north"]), ("walk_south", PARAMS["walk_south"]),
             ("walk_spur", PARAMS["walk_spur"])]
    worst = None
    for i, p in enumerate(PARAMS["planters"]):
        h = p["size"] / 2.0
        for nm, w in walks:
            #  separation along each axis; the LARGER one is the true gap for two
            #  axis-aligned rects (> 0 = disjoint, ≤ 0 = overlap)
            gap = max(max(w["x0"] - (p["cx"] + h), (p["cx"] - h) - w["x1"]),
                      max(w["y0"] - (p["cy"] + h), (p["cy"] - h) - w["y1"]))
            if worst is None or gap < worst[0]:
                worst = (gap, i, nm)
    print(f"    화단 {len(PARAMS['planters'])}개 · 보행판 최소 이격 "
          f"{worst[0]:.2f} m (화단{worst[1]} vs {worst[2]}) → "
          f"{'OK (중첩 0)' if worst[0] > 0.0 else 'FAIL(보행판 침범)'}")


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

    # -- [08-05 doctrine + 3rd answer] guard continuity: mouth rail stubs +
    #    glass curtain walls + end wall must cover both flanks end to end --
    cp0 = PARAMS["canopy"]
    gx0_ = cp0["glass"]["x0"]
    hb0 = PARAMS["height_bar"]
    glass_full = (abs(gx0_) < 1e-6 and abs(cp0["x0"]) < 1e-6
                  and len(PARAMS["rail_runs"]) == 0)
    print("  [가드 연속성] (08-05 5차 — 트렌치 난간 0, 데크·유리 월 모두 전장)")
    print(f"    유리 월 x [{gx0_:.2f},{cp0['x1']:.2f}] 양측 · 데크 x0 "
          f"{cp0['x0']:.2f} (마우스까지 — 판 상단 전 구간 데크 매입) · 엔드월 x "
          f"{cp0['end_wall']['x0']:.2f} → {'전 구간 무단절 OK' if glass_full else 'FAIL'}")
    print(f"    높이제한바 끝 y ±{abs(hb0['y0']):.2f} < 유리면 ±{cp0['y_col']:.2f} → "
          f"{'OK' if abs(hb0['y0']) < cp0['y_col'] else 'FAIL(유리 관통)'} · "
          f"계단 박스 측면 = {PARAMS['stair_canopy']['side_mode']} 모드 "
          f"(rail ↔ glass 전환 가능, 5차: glass + 하행 핸드레일)")
    # ── [v6 judgment (5)] material fix check ──
    mp_ = PARAMS["material"]
    dr_ = PARAMS["drive"]
    print("  [v6 재질 수정 검산] — 아스팔트 (치수 불변)")
    print(f"    아스팔트 : gravel diff/nor/rough · scale "
          f"{mp_['asphalt_scale']:.2f} m · 틴트 {mp_['asphalt_tint']} → "
          f"청기 {'제거 OK' if mp_['asphalt_tint'][2] < mp_['asphalt_tint'][0] else 'FAIL(B>R)'}"
          f" (구 상수색 {mp_['asphalt_color']} = B>R 남청)")
    print(f"    폴리시 밴드 : 중심선 ±0.85 · 폭 0.55 · 동서 x "
          f"[{xroad_geom()['car1']:.1f},{dr_['x1']:.1f}] (GT-64: 교차로까지 연장) "
          f"· 남북 x {PARAMS['xroad']['cx']:.1f}±"
          f"{PARAMS['xroad']['polish_off']:.2f} · 상면 돌출 4 mm "
          f"(저면 매입 → Z파이팅 없음)")

    # ── [08-05 5차] entry sign(파라펫 부착) + height bar(캐노피 보 직결) ──
    es_ = PARAMS["entry_sign"]
    hb_ = PARAMS["height_bar"]
    cpk = PARAMS["canopy"]
    fw_x0 = cpk["x0"] - cpk["fascia_proud"]            # W 밴드 외면 −0.02
    fw_x1 = fw_x0 + cpk["fascia_t"]                    # W 밴드 내면 +0.04
    beam_lo = cpk["z_roof"] - cpk["beam_h"] + cpk["embed"]   # 보 밑면 2.52
    print("  [5차 진입 장비] 자립 갠트리 프레임 삭제 — 사인·높이제한바 캐노피 부착")
    print(f"    사인 패널 z [{es_['z0']:.2f},{es_['z1']:.2f}] · 파라펫 상단 "
          f"{cpk['fascia_top']:.2f} 랩 {cpk['fascia_top'] - es_['z0']:.2f} m → "
          f"{'OK' if es_['z0'] < cpk['fascia_top'] < es_['z1'] else 'FAIL(부유)'} "
          f"· 배면 x {es_['x_back']:+.2f} ∈ 파시아 ({fw_x0:+.2f},{fw_x1:+.2f}) → "
          f"{'매입 OK' if fw_x0 < es_['x_back'] < fw_x1 else 'FAIL'}")
    print(f"    패널 반폭 ±{es_['y_half']:.2f} < 밴드 런 ±{cpk['y_deck'] + cpk['fascia_proud'] - 0.002:.3f} → "
          f"{'OK' if es_['y_half'] < cpk['y_deck'] + cpk['fascia_proud'] - 0.002 else 'FAIL'} "
          f"· 상단 {es_['z1']:.2f} < entry_approach 프레임 상단 ≈3.72 → "
          f"{'OK' if es_['z1'] < 3.72 else 'FAIL(프레임 밖)'}")
    print(f"    높이제한바 z {hb_['z']:.2f} · 행어 z [{hb_['hang_z0']:.2f},"
          f"{hb_['hang_z1']:.2f}] — 바 상단 {hb_['z'] + hb_['r']:.2f} 관입 · 마우스 보 "
          f"밑면 {beam_lo:.2f} 관입 → "
          f"{'OK' if hb_['hang_z0'] < hb_['z'] + hb_['r'] and hb_['hang_z1'] > beam_lo else 'FAIL(이격)'} "
          f"· 행어 y ±{hb_['hang_y']:.2f} < 보 반폭 ±{cpk['y_col']:.2f} → "
          f"{'OK' if hb_['hang_y'] < cpk['y_col'] else 'FAIL'}")

    # ── [08-05 user · U-5 literal] full-length canopy ──
    cp_ = PARAMS["canopy"]
    cov = (cp_["x1"] - cp_["x0"]) / po["x"] * 100.0
    cols = ([cp_["col_mouth_x"]]
            + [cp_["col_x0"] + k * cp_["col_pitch"]
               for k in range(int(cp_["n_col"]))])
    print("  [U-5 캐노피] 트렌치 전장 플랫데크 (08-05 5차 — 데크 마우스까지 연결)")
    print(f"    범위 x [{cp_['x0']:.2f},{cp_['x1']:.2f}] · 개구 {po['x']:.0f} m 대비 "
          f"피복 {cov:.0f}% → {'OK' if cov >= 100.0 - 1e-6 else 'FAIL(무롭 잔여)'}")
    soffit = min(cp_["z_roof"] - cp_["beam_h"] + cp_["embed"],
                 cp_["fascia_top"] - cp_["fascia_h"])
    print(f"    최저 부재 밑면(보/파라펫 밴드) z {soffit:.2f} > 높이제한바 {hb_['z']:.2f} → "
          f"{'OK' if soffit > hb_['z'] else 'FAIL'} · 마우스 보 x {cp_['col_mouth_x']:.2f} "
          f"vs W 밴드 내면 {fw_x1:+.2f} 이격 "
          f"{cp_['col_mouth_x'] - cp_['beam_w'] / 2.0 - fw_x1:.2f} m → "
          f"{'OK' if cp_['col_mouth_x'] - cp_['beam_w'] / 2.0 > fw_x1 else 'FAIL(간섭)'}")
    gl_ = cp_["glass"]
    print(f"    [3차 건물형] 유리 커튼월 양 플랭크 (킥 {gl_['kick_h']:.2f} + 패널 "
          f"t{gl_['t']:.3f}, 베이 {len(cols) + 1}/측) · 엔드월 x "
          f"[{cp_['end_wall']['x0']:.2f},{po['x'] - 0.01:.2f}] (지면 x=24 와 "
          f"10 mm 이격 — 공면 회피) · 포털 유효고 {abs(-1.25 - (-3.714)):.2f} m "
          f"> 표기 {po['head_clear']:.1f} → OK")
    print(f"    기둥 {len(cols)}쌍 · x {cols[0]:.2f}…{cols[-1]:.2f} (마우스 "
          f"{cp_['col_mouth_x']:.2f} + 정규 @{cp_['col_pitch']:.2f}) · y ±{cp_['y_col']:.2f} "
          f"코핑 위 · 내면 {cp_['y_col'] - cp_['col_w'] / 2.0:.2f} > 유효폭 ±{rp['y1']:.1f} → "
          f"{'OK' if cp_['y_col'] - cp_['col_w'] / 2.0 > rp['y1'] else 'FAIL(침범)'}")
    n_lamp_ = 2 * (len(cols) - 1)
    print(f"    소핏 조명 {n_lamp_}등 (2열 y ±{abs(cp_['lamp_y'][0]):.2f} × 미드베이 "
          f"{len(cols) - 1}) · SphereLight r {cp_['lamp_radius']:.2f} · "
          f"{cp_['lamp_intensity']:.0f} — scene02 GT-3 관행 "
          f"(무조명 시 캐노피 하부 DARK — portal_look·ramp_graze 는 선언된 하부 컷)")

    # -- [08-05 2nd answer] stair canopy + uninstructed-asset removals + road-axis check --
    sp_ = PARAMS["stair_canopy"]
    print("  [계단 캐노피] 보행 진입구 (U-5 확장 — 08-05 2차)")
    cover_ok = (sp_["x0"] <= sh["x0"] and sp_["x1"] >= sh["x1"]
                and sp_["y1"] >= sh["y1"])
    print(f"    데크 x [{sp_['x0']:.2f},{sp_['x1']:.2f}] · y [{sp_['y0']:.2f},"
          f"{sp_['y1']:.2f}] ⊇ 샤프트 [{sh['x0']:.1f},{sh['x1']:.1f}]×"
          f"[{sp_['y0']:.2f}↑,{sh['y1']:.1f}] → {'OK' if cover_ok else 'FAIL'} "
          f"(남측 y {sh['y0']:.1f}~{sp_['y0']:.2f} 는 트렌치 캐노피 이격 코스트)")
    #  [verify r2 → GT-64] posts must dodge the openings and both flight bands.
    #  The r2 rule barred any post inside the mouth strip; from GT-64 the two DOOR
    #  JAMBS are legitimately on that line — a door frame IS the mouth — so they are
    #  exempted and judged instead by the clear opening they leave (≥ 0.90 m code).
    st_ = PARAMS["stair"]
    ea_ = sp_["east"]
    bad_post = []
    hw = sp_["post_w"] / 2.0
    jamb_set = {round(v, 4) for v in ea_["jamb_y"]}
    for px, py in sp_["posts"]:
        if abs(px - ea_["x"]) < 1e-9 and round(py, 4) in jamb_set:
            continue                      # door frame member, checked below
        in_shaft = sh["x0"] < px < sh["x1"] and sh["y0"] < py < sh["y1"]
        in_trench = 0.0 < px < po["x"] and -3.3 < py < 3.3
        in_mouth = (sh["x1"] - hw < px < sh["x1"] + 0.3 + hw and
                    (st_["y_a0"] - hw < py < st_["y_a1"] + hw or
                     st_["y_b0"] - hw < py < st_["y_b1"] + hw))
        if in_shaft or in_trench or in_mouth:
            bad_post.append((px, py))
    off_ground = [(px, py) for px, py in sp_["posts"]
                  if sh["x0"] < px < sh["x1"] and sh["y0"] < py < sh["y1"]]
    print(f"    포스트 {len(sp_['posts'])}본(문틀 잼 2 + NE 코너 1 + 서측 2 — "
          f"GT-72: 북측 (11.30,6.90) → 코너 (11.30,6.775)) 개구·계단머리 침범: "
          f"{bad_post if bad_post else '없음 → OK'} · 개구 위 착지: "
          f"{off_ground if off_ground else '없음 → OK'}")
    print(f"    남측 파시아 외면 {sp_['y0'] - sp_['fascia_proud']:.2f} vs 램프 "
          f"캐노피 외면 {cp_['y_deck'] + cp_['fascia_proud']:.2f} → 이격 "
          f"{(sp_['y0'] - sp_['fascia_proud']) - (cp_['y_deck'] + cp_['fascia_proud']):.3f} m · "
          f"유리 월 W/N + 소핏 {2 * len(sp_['lamp_xs'])}등 → 밀폐 계단실 조명 확보")
    #  [GT-72] curtain-wall corners: every run end must be a post centreline.
    gw_, gn_ = sp_["glass_w"], sp_["glass_n"]
    post_c = ([(px, py) for px, py, _w in sp_["glass_posts"]]
              + list(sp_["posts"]))

    def _has_post(x, y):
        return any(abs(px - x) < 1e-6 and abs(py - y) < 1e-6
                   for px, py in post_c)
    ends = [("W 남단", gw_["c"], gw_["a0"]), ("W 북단(NW)", gw_["c"], gw_["a1"]),
            ("N 서단(NW)", gn_["a0"], gn_["c"]),
            ("N 동단(NE)", gn_["a1"], gn_["c"]),
            ("동측 고정유리 북단(NE)", ea_["x"], gn_["c"])]
    free_end = [t for t, xx, yy in ends if not _has_post(xx, yy)]
    print(f"    [GT-72 코너] 커튼월 종단 {len(ends)}곳 → 자유 판 에지 "
          f"{free_end if free_end else '없음 → OK (전량 포스트 중심선 종단)'} · "
          f"NW 코너 포스트 ({gw_['c']:.3f},{gn_['c']:.3f}) · NE 코너 포스트 "
          f"({ea_['x']:.2f},{gn_['c']:.3f}) = 보 지점 겸용")

    # ── [08-06 · GT-64/GT-72] stair-box door · east glass · coping ──
    print("  [GT-72 계단박스] 외짝문 개방 · 동측면 폐합 · 동측 코핑")
    clear_w = ea_["leaf_w"]
    jw = ea_["jamb_w"] / 2.0
    seg = [("잼S", ea_["y0"], ea_["jamb_y"][0] + jw),
           ("문짝(개방)", ea_["jamb_y"][0] + jw, ea_["mull_y"] - ea_["mull_w"] / 2.0),
           ("멀리언", ea_["mull_y"] - ea_["mull_w"] / 2.0,
            ea_["mull_y"] + ea_["mull_w"] / 2.0),
           ("측창(고정)", ea_["mull_y"] + ea_["mull_w"] / 2.0,
            ea_["jamb_y"][1] - jw),
           ("잼N", ea_["jamb_y"][1] - jw, ea_["jamb_y"][1] + jw),
           ("고정유리(잼 랩)", ea_["jamb_y"][1], sp_["glass_n"]["c"])]
    #  a gap only counts when the next member STARTS after the previous one ends;
    #  a negative delta is a deliberate lap (glass into post), not a hole.
    holes = [f"{a[0]}|{b[0]}" for a, b in zip(seg[:-1], seg[1:])
             if b[1] - a[2] > 1e-9]
    print(f"    동측면 y [{ea_['y0']:.2f},{sp_['glass_n']['c']:.3f}] = "
          + " + ".join(f"{t} {a:.2f}…{b:.2f}" for t, a, b in seg)
          + f" → 틈 {holes if holes else '없음 → OK (문이 유일 통로)'}")
    _th = math.radians(ea_["open_deg"])
    _tip = ea_["hinge_x"] + ea_["leaf_w"] * math.sin(_th)
    _sr, _ws = PARAMS["spur_ramp"], PARAMS["walk_spur"]
    _rz = (PARAMS["drive"]["proud"]
           + max(0.0, min(_sr["run"], _tip - _sr["x0"])) / _sr["run"]
           * (_ws["proud"] - PARAMS["drive"]["proud"]))
    print(f"    유효 통과폭 {clear_w:.2f} m (외짝 문짝) ≥ 0.90 → "
          f"{'OK' if clear_w >= 0.90 else 'FAIL'} · 문틀 x {ea_['x']:.2f} > 샤프트 "
          f"연단 {sh['x1']:.2f} (지반 위 이격 {ea_['x'] - ea_['jamb_w'] / 2.0 - sh['x1']:.2f} m) · "
          f"문 상단 {ea_['door_z1']:.2f} < 보 밑면 "
          f"{sp_['z_roof'] - sp_['beam_h'] + sp_['embed']:.2f} → "
          f"{'OK' if ea_['door_z1'] < sp_['z_roof'] - sp_['beam_h'] + sp_['embed'] else 'FAIL'}")
    print(f"    [GT-72 개방] {ea_['open_deg']:.0f}° 홀드오픈 · 선단 x {_tip:.3f} · "
          f"스퍼 턱낮춤 상면 {_rz:+.3f} vs 문짝 하단 {ea_['leaf_z0']:+.3f} → "
          f"{'OK 관통 0 (이격 %+.3f)' % (ea_['leaf_z0'] - _rz) if ea_['leaf_z0'] > _rz else 'FAIL(포장 관통)'}"
          f" · 힌지 x {ea_['hinge_x']:.2f} > 프레임 동면 "
          f"{ea_['x'] + ea_['jamb_w'] / 2.0:.2f} → "
          f"{'OK' if ea_['hinge_x'] > ea_['x'] + ea_['jamb_w'] / 2.0 else 'FAIL(잼 간섭)'}")
    da_ = PARAMS["door_apron"]
    print(f"    [GT-72 문 하부 포장] 에이프런 x [{da_['x0']:.2f},{da_['x1']:.2f}] · "
          f"y [{da_['y0']:.2f},{da_['y1']:.2f}] · 상면 {da_['proud']:+.3f} "
          f"(스퍼 서단 {PARAMS['drive']['proud']:+.3f} 대비 −1 mm, 공면 회피) · "
          f"남단 = TrenchCope_N 북면 {PARAMS['ramp']['y1'] + PARAMS['wall']['thick'] + PARAMS['wall']['cope_over']:.2f} → "
          f"{'OK' if da_['y0'] >= PARAMS['ramp']['y1'] + PARAMS['wall']['thick'] + PARAMS['wall']['cope_over'] - 1e-9 else 'FAIL(코핑 간섭)'}"
          f" · 서단 {da_['x0']:.3f} vs 샤프트 연단 {sh['x1']:.2f} → 연단 돌출 "
          f"{'0 (동측 %+.0f mm 오프셋 — 공면 회피)' % ((da_['x0'] - sh['x1']) * 1000) if da_['x0'] > sh['x1'] else 'FAIL(연단 침범)'}")
    se_ = PARAMS["shaft_east"]
    wl_ = PARAMS["wall"]
    covered = sorted([(a, b) for a, b, _z in se_["bands"]]
                     + [(se_["face"]["y0"], se_["face"]["y1"])])
    holes2 = [f"{a[1]:.2f}…{b[0]:.2f}" for a, b in zip(covered[:-1], covered[1:])
              if b[0] - a[1] > 1e-9]
    print(f"    동측 연단 벽·코핑 y {covered[0][0]:.2f}…{covered[-1][1]:.2f} "
          f"(밴드 {len(se_['bands'])} + 계단구 페이싱 1) → 잔여 잔디 립 "
          f"{holes2 if holes2 else '없음 → OK'} · 코핑 폭 "
          f"{se_['t'] + 2 * wl_['cope_over']:.2f} · 계단구 밴드는 코핑 없음 "
          f"(120 mm 업스탠드 = 보행면 신규 단차 금지)")
    print(f"    지하 복도 마우스 y [{PARAMS['corridor']['y0']:.2f},"
          f"{PARAMS['corridor']['y1']:.2f}] 밴드 하단 "
          f"{se_['bands'][2][2]:+.2f} = 슬래브 밑면 → 유효고 "
          f"{se_['bands'][2][2] - PARAMS['corridor']['floor_z']:.2f} m ≥ 2.1 → "
          f"{'OK' if se_['bands'][2][2] - PARAMS['corridor']['floor_z'] >= 2.1 else 'FAIL'}")
    #  ── [08-06 · GT-72] side-gap infills ──
    si_ = PARAMS["stair_infill"]
    print(f"    [GT-72 측부 갭] 남측 슬롯 {si_['skirt_y0']:.2f}…{st_['y_a0']:.2f} "
          f"({st_['y_a0'] - si_['skirt_y0']:.2f} m, x {si_['land_x0']:.2f}…"
          f"{st_['x_head']:.2f}) + 중앙 웰 {si_['well_y0']:.2f}…{st_['y_b0']:.2f} "
          f"({st_['y_b0'] - si_['well_y0']:.2f} m, 종전 무저) → 계단형 충전 "
          f"{2 * st_['n_flight'] + 1}개 · 상단 = 인접 답면 −"
          f"{si_['reveal'] * 1000:.0f} mm · 측면 랩 "
          f"{(si_['skirt_y1'] - st_['y_a0']) * 1000:.0f} mm → "
          f"{'OK (공면·부유 0)' if si_['skirt_y1'] > st_['y_a0'] and si_['well_y1'] > st_['y_b0'] else 'FAIL(랩 없음)'}")
    print(f"    불변 확인: 단수 {st_['n_flight']}×2 · 챌판 {st_['riser']:.3f} · "
          f"디딤 {st_['tread']:.2f} · 낙차 연단 x {st_['x_head']:.2f} · "
          f"레지스트리 행 무변동 (충전은 기존 솔리드에 랩되는 인필)")
    hr_ = PARAMS["stair_handrail"]
    y_ra_ = st_["y_a1"] - hr_["inset"]
    y_rb_ = st_["y_b0"] + hr_["inset"]
    on_tread = (st_["y_a0"] + hr_["post_r"] < y_ra_ < st_["y_a1"] - hr_["post_r"]
                and st_["y_b0"] + hr_["post_r"] < y_rb_
                < st_["y_b1"] - hr_["post_r"])
    #  post stations must be tread MID-points, else a post lands on a nosing
    mids = [round(st_["x_head"] - (k + 0.5) * st_["tread"], 4)
            for k in range(st_["n_flight"])]
    off_mid = [bx for bx in hr_["post_xs"] if round(bx, 4) not in mids]
    print(f"    [GT-72 자립 중앙 가드] 답면 위 {hr_['h']:.2f} + 중간대 "
          f"{hr_['mid_h']:.2f} (0.80~0.90 대역) → "
          f"{'OK' if 0.80 <= hr_['h'] <= 0.90 else 'FAIL'} · 레일선 A y "
          f"{y_ra_:.2f} ∈ 플라이트A [{st_['y_a0']:.2f},{st_['y_a1']:.2f}] / "
          f"B y {y_rb_:.2f} ∈ 플라이트B [{st_['y_b0']:.2f},{st_['y_b1']:.2f}] → "
          f"{'OK (기둥 전량 답면 착지)' if on_tread else 'FAIL(웰 위 부유)'} · "
          f"벽~기둥 유효폭 {st_['width'] - hr_['inset'] - hr_['post_r']:.3f} ≥ 1.20 → "
          f"{'OK' if st_['width'] - hr_['inset'] - hr_['post_r'] >= 1.20 else 'FAIL'}")
    print(f"    기둥 스테이션 {hr_['post_xs']} = 디딤 중앙 → "
          f"{'OK' if not off_mid else 'FAIL(코 위 착지 %s)' % off_mid} · "
          f"답면 매입 {hr_['tread_embed'] * 1000:.0f} mm + 베이스 플레이트 r"
          f"{hr_['plate_r']:.2f}")
    print(f"    종단부(Top·Mid 동시): A 수평리턴 → 문틀 잼 x {hr_['jamb_x']:.2f} "
          f"매입 {hr_['jamb_embed'] * 1000:.0f} mm (잼 중심 y "
          f"{ea_['jamb_y'][1]:.2f} = 레일선 → "
          f"{'OK' if abs(ea_['jamb_y'][1] - y_ra_) < 1e-9 else 'FAIL(축 불일치)'}) · "
          f"머리 뉴얼 x {hr_['newel_x']:.2f} (답면 1 착지 · 베이스 플레이트 동단 "
          f"{hr_['newel_x'] + hr_['plate_r']:.3f} < 연단 {st_['x_head']:.2f} → "
          f"{'OK 돌출 0' if hr_['newel_x'] + hr_['plate_r'] < st_['x_head'] else 'FAIL(연단 돌출)'}"
          f") · U 뉴얼 2본 x "
          f"{st_['x_turn'] - hr_['u_off']:.2f} ≥ 참 서단 {st_['land_x0']:.2f} → "
          f"{'OK' if st_['x_turn'] - hr_['u_off'] >= st_['land_x0'] else 'FAIL'} · "
          f"B 하단 복도 뉴얼 x {hr_['foot_newel_x']:.2f} (복도 y "
          f"[{PARAMS['corridor']['y0']:.2f},{PARAMS['corridor']['y1']:.2f}] 내 "
          f"{'OK' if PARAMS['corridor']['y0'] < y_rb_ < PARAMS['corridor']['y1'] else 'FAIL'}) "
          f"→ 공중 종단 0")

    # ── [08-06 · GT-73] glass transparency pilot (material-only, R-2) ──
    mp_ = PARAMS["material"]
    print("  [GT-73 유리 투명화] 사용자 지시에 의한 재질 동결 예외 (기하 불변)")
    print(f"    백엔드 = {sc.glass_backend()} · 불투명도 "
          f"{mp_['glass_v_opacity']:.2f} (0.30~0.45 대역) → "
          f"{'OK' if 0.30 <= mp_['glass_v_opacity'] <= 0.45 else 'FAIL'} · "
          f"거칠기 {mp_['glass_v_rough']:.2f} · IOR {mp_['glass_v_ior']:.2f} · "
          f"틴트 {tuple(round(c, 2) for c in mp_['glass_v_color'])}")
    print(f"    적용 = Canopy/Glass_* · StairCanopy/Glass_* · EastGlass_* · "
          f"DoorTransom · DoorSidelight · Leaf_Glass  |  불투명 유지 = "
          f"Looks/Glass (건물 4동 창호 — 솔리드 셸 뒤에 방이 없다)")
    print("    A/B: NEGOBS_GLASS_V1=0 → 구 Looks/Glass 상수로 make_pbr 폴백 · "
          "NEGOBS_GLASS_MDL=glass → OmniGlass.mdl (PT 에서 OmniPBR opacity 가 "
          "불투명하게 나오면 이 스위치 하나로 전환)")
    print(f"    frosted 파일럿 팔 = {'ON' if GLASS_FROST else 'OFF(기본 — 파일럿 전 빌드와 동일)'} · "
          f"NEGOBS_GLASS_FROST=1 → 차폐 23 frosting {GLASS_FROST_ROUGH:.2f} · "
          f"무관 8 클리어 (경계 판정 = glass_boundary_check_s13, 08-11 재실행 23/8 확인)")

    # ── [08-06 · GT-64] road network · master plan · shadows · street rows ──
    _smoke_gt64(sh, po)

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
    # entry_approach: vehicle-eye approach (canopy · height bar · opening)
    views["entry_approach"] = dict(eye=[-12.0, 0.0, 1.55], tgt=[2.0, 0.0, -0.5])
    # ramp_graze: pedestrian-eye grazing — does the ramp descent compress into a plane
    views["ramp_graze"] = dict(eye=[-6.0, 0.0, 0.90], tgt=[8.0, 0.0, -0.55])
    # bollard_walk: heading south on the north sidewalk — bollard row + tactile + crossing
    views["bollard_walk"] = dict(eye=[-2.2, 11.0, 1.50], tgt=[-2.2, 1.5, 0.15])
    # stair_head: looking down the 2 switchback flights and mid landing from the head
    # [08-06 · GT-64 — the round's ONE eye move, declared for meta honesty (X2)]
    #   eye x 13.6 → 11.10; y/z and the target are untouched, the cut name and the
    #   15-cut set are untouched. Forced, not stylistic: GT-64 closes the east face
    #   with a CLOSED glass door at x 11.25…11.35, and this library had **no
    #   transmissive material** (scene08: "No transmission is available in this
    #   material stack"), so a leaf that is meant to keep the descent visible in
    #   fact renders as an opaque dark pane. The old eye's centre ray met it at
    #   (11.30, 4.50, 0.35) `[computed]` — the cut would have judged a door, not the
    #   flights it exists to judge. The eye therefore steps 2.50 m through the
    #   opening to just inside the box: still outside every solid (above tread 1,
    #   2.85 m under the deck soffit 2.45, same bearing, same subject).
    # [08-06 · GT-72/73] BOTH premises of that move are now void — the leaf is a
    #   single leaf swung 95 deg clear of the opening (GT-72) and the fixed panes
    #   are translucent (GT-73). The eye is nevertheless **left where it is**: this
    #   round's brief holds the preset eyes, and moving it back would confound the
    #   craftsmanship read with a viewpoint change. Restoring x 13.6 is a separate
    #   decision for the round that judges these two rows.
    #   The eye is 0.70 m south of the centre guard, whose rail line moved 5.00 →
    #   4.90 (GT-72) — i.e. 0.60 m clear, still outside every solid.
    views["stair_head"] = dict(eye=[11.10, 4.30, 1.60], tgt=[6.6, 4.90, -2.20])
    # portal_look: from mid-ramp toward the basement portal (dimly lit garage)
    views["portal_look"] = dict(eye=[13.0, 0.0, -0.95], tgt=[27.0, 0.5, -3.20])
    # beauty_overview: estate overview down the open E-W road corridor (§0-2 axis).
    #   [GT-64 eye move, documented per X2] The old eye (-17,-15,12) sat 4 m west of
    #   A104's new west face inside its y-band: the centre ray cleared the corner by
    #   1.11 m but the right half-frustum was filled by the blank west gable at 4 m —
    #   the cut judged a wall, not the estate. New eye rides the corridor axis the
    #   master plan keeps open: intersection foreground, both row facades (south
    #   windows on the north row), street rows, canopy hall roof. Same cut name.
    views["beauty_overview"] = dict(eye=[-31.0, -8.0, 14.0],
                                    tgt=[12.0, 0.0, 0.5])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. entry_approach   — 마우스 종단 멀리언·유리 서단 에지 마감·사인 프레임(GT-72) + 투명 커튼월(GT-73)
 2. ramp_graze·h0.3  — 램프 하강이 평면으로 압축되고 개구 너머가 연속되는가(특색)
 3. bollard_walk     — 계단박스 외짝문 개방·NW/NE 코너 포스트·문 하부 포장(GT-72)
 4. stair_head       — 측부 갭 폐합(남측 슬롯·중앙 웰)·기둥 답면 착지·Top/Mid 종단 결속(GT-72)
 5. portal_look      — 포털 유효고·소핏 조명 하 램프 판독(PT 필수 — 캐노피 하부 선언 컷)
 6. beauty_overview  — 정남향 판상 4동 2×2 그리드·남북 교차로 + 개방 문짝 읽힘(GT-72)"""


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
    from pxr import Gf, UsdGeom, UsdLux
    from omni.kit.viewport.utility import (get_active_viewport,
                                           capture_viewport_to_file)
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.Xform.Define(stage, "/World/Scene13")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene13"

    def BOX(path, center, size, mtl=None, col=False, rotZ=0.0):
        # `rotZ` [GT-72]: the open door leaf's members are the scene's only
        # spun boxes. It is authored only when non-zero (scene_common K-micro),
        # so every existing call site is byte-identical.
        return sc.add_box(stage, path, center, size, mtl, collider=col,
                          rotZ=rotZ)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False,
            rotZ=0.0):
        # `rotZ` [GT-72]: the door's hold-open stay is a bearing-laid tube whose
        # plan bearing is not axis-aligned (rotY 90 lays it along +X, rotZ swings
        # it). Authored only when non-zero — see scene_common.add_cylinder.
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col, rotZ=rotZ)

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
        # [08-06 user · GT-73] translucent vision glass (scene_common.make_glass).
        #   `opaque_*` feeds the NEGOBS_GLASS_V1=0 arm, which hands exactly the old
        #   `Looks/Glass` constants to make_pbr — the fallback is the previous look.
        M["glass_v"] = sc.make_glass(
            stage, f"{ROOT}/Looks/GlassV", color=mp["glass_v_color"],
            opacity=mp["glass_v_opacity"],
            roughness=(GLASS_FROST_ROUGH if GLASS_FROST
                       else mp["glass_v_rough"]),
            ior=mp["glass_v_ior"], opaque_color=mp["glass_color"],
            opaque_roughness=mp["glass_rough"])
        # [GT-73 frosted pilot] clear arm for the 8 boundary-irrelevant panes.
        #   FROST=0 aliases the same material — no new prim, bindings unchanged.
        M["glass_vc"] = (sc.make_glass(
            stage, f"{ROOT}/Looks/GlassVClear", color=mp["glass_v_color"],
            opacity=mp["glass_v_opacity"], roughness=0.0,
            ior=mp["glass_v_ior"], opaque_color=mp["glass_color"],
            opaque_roughness=mp["glass_rough"])
            if GLASS_FROST else M["glass_v"])
        print(f"[GT-73 유리 투명화] 백엔드 = {sc.glass_backend()} · 불투명도 "
              f"{mp['glass_v_opacity']:.2f} · 적용 = 램프 커튼월 · 계단박스 "
              f"W/N · 동측 고정유리 · 문짝/트랜섬/측창 (건물 창호는 기존 불투명 "
              f"Looks/Glass 유지)")
        if GLASS_FROST:
            print(f"[GT-73 frosted 파일럿] 차폐 23 = frosting "
                  f"{GLASS_FROST_ROUGH:.2f} · 무관 8 = 클리어 0.00 "
                  f"(Canopy {sorted(GLASS_CLEAR_BAYS)} + DoorTransom + "
                  f"DoorSidelight)"
                  + ("" if sc.GLASS_MDL in ("glass", "omniglass") else
                     " · 경고: NEGOBS_GLASS_MDL=glass 아님 — OmniPBR 은 "
                     "투과 블러 불가, 이 팔은 무의미"))
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        # [08-05 user · U-5 literal] `Looks/Roof` + `Looks/Fascia` return with the
        #   full-length canopy — the same v6 C-3 recipe the porch had (concrete texture
        #   + fascia band), now binding the whole-trench deck.
        M["roof"] = PBR(
            f"{ROOT}/Looks/Roof", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"),
            mp["roof_scale"], tint=mp["roof_tint"])
        M["fascia"] = PBR(
            f"{ROOT}/Looks/Fascia", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"),
            mp["fascia_scale"], tint=mp["fascia_tint"])
        M["post"] = PBR(f"{ROOT}/Looks/Post", diffuse_color=mp["post_color"],
                        metallic=mp["post_metallic"],
                        roughness_const=mp["post_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["dark"] = PBR(f"{ROOT}/Looks/Dark", diffuse_color=mp["dark_color"],
                        roughness_const=mp["dark_rough"])
        M["warn_y"] = PBR(f"{ROOT}/Looks/WarnY", diffuse_color=mp["warn_y"],
                          roughness_const=0.6)
        # warn_r kept as a palette slot — its only consumer (the barrier arm's
        # red segments) was deleted 08-05 (GT-59)
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
        xg, xr = xroad_geom(), PARAMS["xroad"]
        # road: straight section + flared entry
        # [W2-0 · P-A] The entry asphalt is the stage for 13-8's 3-shot filler -> skin OFF.
        # [08-06 · GT-64] `Drive_Link` carries the carriageway on west from x −14 to
        #   the junction, and `XRoad_Main` is the north-south carriageway. Both are
        #   scene-owned boxes (no `ground_kit` profile), so no manhole or weed can
        #   re-enter through them (GT-59). They BUTT the neighbouring plates exactly
        #   — the Drive_Main / Drive_Flare seam at x −6 is the existing precedent.
        sc.skin_exclude(f"{ROOT}/Drive_Main", f"{ROOT}/Drive_Flare",
                        f"{ROOT}/Drive_Link", f"{ROOT}/XRoad_Main")
        BOX(f"{ROOT}/Drive_Main",
            ((dr["x0"] + dr["flare_x0"]) / 2.0, 0.0, z + dr["proud"] - 0.05),
            (dr["flare_x0"] - dr["x0"], 6.6, 0.1), M["asphalt"], col=True)
        BOX(f"{ROOT}/Drive_Flare",
            ((dr["flare_x0"] + dr["x1"]) / 2.0, 0.0, z + dr["proud"] - 0.05),
            (dr["x1"] - dr["flare_x0"], 2 * dr["flare_y"], 0.1),
            M["asphalt"], col=True)
        BOX(f"{ROOT}/Drive_Link",
            ((xg["car1"] + dr["x0"]) / 2.0, 0.0, z + dr["proud"] - 0.05),
            (dr["x0"] - xg["car1"], 6.6, 0.1), M["asphalt"], col=True)
        BOX(f"{ROOT}/XRoad_Main",
            (xr["cx"], (xg["y0"] + xg["y1"]) / 2.0, z + dr["proud"] - 0.05),
            (xg["car1"] - xg["car0"], xg["y1"] - xg["y0"], 0.1),
            M["asphalt"], col=True)
        # [v6 (5)] tyre polish bands — 2 wheel tracks (centreline +-0.85, width 0.55).
        #   Base buried below the road, top proud 4 mm -> no coplanar Z-fighting.
        #   [GT-64] the E-W pair runs on to the junction so the wheel tracks do not
        #   stop mid-carriageway; the N-S pair is the same section turned 90°.
        for tag, yc in (("L", -0.85), ("R", 0.85)):
            BOX(f"{ROOT}/DrivePolish_{tag}",
                ((xg["car1"] + dr["x1"]) / 2.0, yc,
                 z + dr["proud"] - 0.006),
                (dr["x1"] - xg["car1"], 0.55, 0.02), M["polish"])
        for tag, xc in (("L", xr["cx"] - xr["polish_off"]),
                        ("R", xr["cx"] + xr["polish_off"])):
            BOX(f"{ROOT}/XRoadPolish_{tag}",
                (xc, (xg["y0"] + xg["y1"]) / 2.0, z + dr["proud"] - 0.006),
                (0.55, xg["y1"] - xg["y0"], 0.02), M["polish"])
        # road centre guide line — dashes stop clear of the junction (a real
        #   carriageway carries no centre line through an intersection).
        n_dash = 0
        bx = dr["x0"] + 0.9
        while bx > xg["car1"] + xr["dash_skip"]:
            bx -= xr["dash_pitch"]
        while bx < dr["x1"] - xr["dash_len"] / 2.0:
            BOX(f"{ROOT}/DriveLine_{n_dash}", (bx, 0.0, z + 0.008),
                (xr["dash_len"], 0.12, 0.02), M["paint"])
            bx += xr["dash_pitch"]
            n_dash += 1
        n_xdash = 0
        by = xg["y0"] + xr["dash_pitch"] / 2.0
        while by < xg["y1"] - xr["dash_len"] / 2.0:
            if abs(by) > xr["dash_skip"]:
                BOX(f"{ROOT}/XRoadLine_{n_xdash}", (xr["cx"], by, z + 0.008),
                    (0.12, xr["dash_len"], 0.02), M["paint"])
                n_xdash += 1
            by += xr["dash_pitch"]
        walks = []
        wn = PARAMS["walk_north"]
        # The crossing sidewalk is cut so it **never overlaps** walk_north/south
        #   (two plates sharing a top z would Z-fight — audit v4 lesson).
        # [W3 GT-5] CrossN1 / CrossS1 are no longer plates: they are the **turn-down
        #   ramps** built by `build_cross_ramps`, because at proud 0.150 a flat plate
        #   would put a 146 mm step across the carriageway edge.
        # [08-06 · GT-64] `Walk_CrossN2` / `Walk_CrossS2` are DELETED — they were the
        #   6.8 m and 6.6 m spurs that carried the crossing on past both footways and
        #   stopped in the lawn. What is left is exactly walk_south → ramp →
        #   carriageway → ramp → walk_north.
        # [08-06 · GT-64] the two N-S footways. The east one is CUT by the E-W
        #   carriageway (plates stop at ±gap, the turn-downs bridge the rest), the
        #   west one runs uncut to both scene rims.
        walks.append(("XWalkE_S", xg["we0"], xg["we1"], xg["y0"], -xg["gap"],
                      wn["proud"]))
        walks.append(("XWalkE_N", xg["we0"], xg["we1"], xg["gap"], xg["y1"],
                      wn["proud"]))
        walks.append(("XWalkW", xg["ww0"], xg["ww1"], xg["y0"], xg["y1"],
                      wn["proud"]))
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
        # [08-06 user · GT-72] entrance apron — the grass band that ran into the
        #   door frame. Same plate idiom, `proud` 0.003 so its top is 1 mm under
        #   the turn-down's west end (0.004): a joint line, not a coplanar seam.
        da = PARAMS["door_apron"]
        walks.append(("DoorApron", da["x0"], da["x1"], da["y0"], da["y1"],
                      da["proud"]))
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
        """[W3 GT-5] driveway turn-downs — `cross_ramps()` + the spur's own west run.
        [08-06 · GT-64] plus the four turn-downs of the new intersection."""
        t_bury = PARAMS["walk_plate_t"]
        th = PARAMS["walk_cross"]["proud"] + t_bury
        for tag, piv, rot, x0l, z0, run, drop, y0l, y1l in cross_ramps():
            grp = sc.build_rot_group(stage, f"{ROOT}/WalkRamp_{tag}", piv, rot)
            sc.build_slope(stage, f"{grp}/Plate", x0l, z0, abs(run), drop,
                           y0l, y1l, th, M["paving"], margin=0.0, collider=True)
        for tag, axis, piv, rot, x0l, z0, run, drop, a0, a1 in xroad_ramps():
            if axis == "y":
                grp = sc.build_rot_group(stage, f"{ROOT}/XWalkRamp_{tag}",
                                         piv, rot)
                sc.build_slope(stage, f"{grp}/Plate", x0l, z0, abs(run), drop,
                               a0, a1, th, M["paving"], margin=0.0,
                               collider=True)
            else:
                sc.build_slope(stage, f"{ROOT}/XWalkRamp_{tag}", x0l, z0,
                               abs(run), drop, a0, a1, th, M["paving"],
                               margin=0.0, collider=True)
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
        # [08-06 · GT-64] the intersection's own kerb lines — same builder, same
        #   unit/arris/gutter convention, only the LOD window differs (`xlod_span`:
        #   these runs are 14~18 m west of every judged eye).
        kwx = dict(kw)
        kwx["lod_span"] = PARAMS["curb"]["xlod_span"]
        n_xblk = n_xprim = 0
        for tag, p0, p1, side, spans in xroad_curb_lines():
            r2 = ik.build_curb_line(kit, f"{ROOT}/Curb_{tag}", p0, p1, M["curb"],
                                    road_side=side, drop_spans=list(spans), **kwx)
            for w in r2["warnings"]:
                print(f"[GT-64] 경계석 경고({tag}) — {w}")
            n_xblk += r2["n_blocks"]
            n_xprim += r2["prim_count"]
        print(f"[GT-5] 보차도 경계석 4선 · 블록 {n_blk} · 프림 {n_prim} · "
              f"상단 z {res['curb_top_z']:+.3f} (보도면 "
              f"{PARAMS['walk_north']['proud']:+.3f} flush) · 노출 "
              f"{res['exposure_road']:.3f} · gt_drop {res['gt_drop']:.3f} · "
              f"단위 {res['unit_actual']:.2f} m · 아리스 look(R10, 0프림)")
        print(f"[GT-64] 교차로 경계석 {len(xroad_curb_lines())}선 · 블록 {n_xblk} · "
              f"프림 {n_xprim} · 동측 보도선은 동서 차도에서 절단(램프 구간 무연석) · "
              f"턱낮춤: walk_north/south 접속 2 · 남북 횡단 2")
        return dict(blocks=n_blk + n_xblk, prims=n_prim + n_xprim,
                    gt_drop=res["gt_drop"])

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
            # [08-05 user, 2nd answer] weed 5 -> removed, manhole site removed
            #   — "no grass/manholes on roads" (GT-59). The surface row stays
            #   explicit so profile defaults can never leak back in.
            overrides=dict(
                surface=(("patch", int(g["patch_n"])), ("crack", 6),
                         ("stain", ("tire",))),
                infra=dict(marking=())),
            # Ramp crest = the drop edge. Deck grade 0.085 beyond -> [F] at d2 only.
            edges=[("ramp_crest", 0.0,
                    dict(beyond_grade=float(rp["trans_grade"])))],
            dists=(2, 5, 10), scene="scene13",
            tactile=("bollard",) if cfg["cue_tactile"] else (),
            sites=dict(
                # [verify r2] the manhole deletion emptied the judged W1/d5
                #   near window (ground_kit B1/B2 soft gates went FAIL) — the
                #   scene's one saw-cut patch is sited there instead: a road-
                #   legal area element the user's rectangle ban exempts.
                patch=[(-3.90, 0.00)],
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
        # shaft walls: west (x0..x0+t) · north (y1-t..y1)
        # [08-06 user · GT-64] **ShaftWall_Mid is DELETED.** The user approved
        #   opening the switchback: the 0.30 m strip between the flight bands is now
        #   an open well, guarded by the free-standing double-sided rail below. The
        #   collider removal is declared in ledger GT-64 — it is the round's ONLY
        #   collider deletion. The east 0.25 m of the strip survives as the
        #   `shaft_east` band M pier, which carries the door jamb and the head newel.
        t = sh["wall_t"]
        wz = (0.0 + st["base_z"]) / 2.0
        wh = 0.0 - st["base_z"]
        BOX(f"{ROOT}/ShaftWall_W",
            (sh["x0"] + t / 2.0, (sh["y0"] + sh["y1"]) / 2.0, wz),
            (t, sh["y1"] - sh["y0"], wh), M["wall_b"], col=True)
        BOX(f"{ROOT}/ShaftWall_N",
            ((sh["x0"] + sh["x1"]) / 2.0, sh["y1"] - t / 2.0, wz),
            (sh["x1"] - sh["x0"], t, wh), M["wall_b"], col=True)
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
        # [08-06 user · GT-64 (d)] EAST rim — facing wall + coping where the bare
        #   ground-box cut face (grass material) used to sit at the drop edge.
        #   Geometry rationale in the PARAMS["shaft_east"] note; the mouth band
        #   deliberately gets no coping so the walked route keeps its z.
        se = PARAMS["shaft_east"]
        et = se["t"]
        ex_c = sh["x1"] - et / 2.0
        for i, (by0, by1, bz) in enumerate(se["bands"]):
            z_bot = wl["z_bot"] if bz is None else float(bz)
            BOX(f"{ROOT}/ShaftWall_E{i}",
                (ex_c, (by0 + by1) / 2.0, (0.0 + z_bot) / 2.0),
                (et, by1 - by0, 0.0 - z_bot), M["wall_b"], col=True)
        ch_e = wl["cope_h"] - se["cope_drop"]
        for i, (by0, by1) in enumerate(se["cope_bands"]):
            BOX(f"{ROOT}/ShaftCope_E{i}",
                (ex_c, (by0 + by1) / 2.0, ch_e / 2.0),
                (et + 2 * wl["cope_over"], by1 - by0, ch_e), M["cope"])
        #   mouth band: a facing whose top stops `gap` below grade, so it hides the
        #   0.165 m riser-height cut face without a coplanar contact and without
        #   adding a step. Its east half is buried inside Ground_N2.
        fa = se["face"]
        BOX(f"{ROOT}/ShaftFace_Entry",
            (sh["x1"] + 0.02, (fa["y0"] + fa["y1"]) / 2.0,
             -(fa["drop"] + fa["gap"]) / 2.0),
            (fa["t"] + 0.04, fa["y1"] - fa["y0"], fa["drop"] - fa["gap"]),
            M["cope"])
        # ── [08-06 user · GT-72] the two side slots, infilled ────────────────
        #   Step bands are re-derived from PARAMS (they are NOT read back from the
        #   built prims), so the fills cannot drift from the flights:
        #     flight A step k : x [x_head−(k+1)·tread, x_head−k·tread], top −(k+1)·riser
        #     flight B step k : x [x_turn+k·tread,  x_turn+(k+1)·tread],
        #                       top mid_z−(k+1)·riser
        #   Rationale + the invariance argument live in the PARAMS["stair_infill"] note.
        si = PARAMS["stair_infill"]
        rev = si["reveal"]
        z_bot_f = st["base_z"] - rev
        x_rim = st["x_head"] - rev              # never coincident with the rim
        steps_a = [(st["x_head"] - (k + 1) * st["tread"],
                    min(st["x_head"] - k * st["tread"], x_rim),
                    -(k + 1) * st["riser"]) for k in range(st["n_flight"])]
        steps_b = [(st["x_turn"] + k * st["tread"],
                    min(st["x_turn"] + (k + 1) * st["tread"], x_rim),
                    st["mid_z"] - (k + 1) * st["riser"])
                   for k in range(st["n_flight"])]
        n_fill = 0
        for k, (xa, xb, zt) in enumerate(steps_a):
            BOX(f"{ROOT}/StairSkirt_A{k}",
                ((xa + xb) / 2.0, (si["skirt_y0"] + si["skirt_y1"]) / 2.0,
                 (z_bot_f + zt - rev) / 2.0),
                (xb - xa, si["skirt_y1"] - si["skirt_y0"],
                 zt - rev - z_bot_f), stair_mtl, col=True)
            n_fill += 1
        BOX(f"{ROOT}/StairSkirt_Land",
            ((si["land_x0"] + st["x_turn"]) / 2.0,
             (si["skirt_y0"] + si["skirt_y1"]) / 2.0,
             (z_bot_f + st["mid_z"] - rev) / 2.0),
            (st["x_turn"] - si["land_x0"], si["skirt_y1"] - si["skirt_y0"],
             st["mid_z"] - rev - z_bot_f), stair_mtl, col=True)
        n_fill += 1
        for k, (xa, xb, zt) in enumerate(steps_b):
            BOX(f"{ROOT}/StairWellFill_{k}",
                ((xa + xb) / 2.0, (si["well_y0"] + si["well_y1"]) / 2.0,
                 (z_bot_f + zt - rev) / 2.0),
                (xb - xa, si["well_y1"] - si["well_y0"],
                 zt - rev - z_bot_f), stair_mtl, col=True)
            n_fill += 1
        print(f"[GT-72 측부 갭 폐합] 남측 슬롯 y {si['skirt_y0']:.2f}…"
              f"{st['y_a0']:.2f} ({st['y_a0'] - si['skirt_y0']:.2f} m) + 중앙 웰 "
              f"y {si['well_y0']:.2f}…{st['y_b0']:.2f} "
              f"({st['y_b0'] - si['well_y0']:.2f} m, 무저 → 하행 플라이트 바닥) · "
              f"충전 {n_fill}개 · 상단 리빌 {rev * 1000:.0f} mm (공면 회피) · "
              f"단높이/디딤 x대/연단 x {st['x_head']:.2f} 불변")

        # [08-05 5th answer → 08-06 · GT-64/GT-72] the descending handrail: a
        #   free-standing double-sided guard, one two-tube run per flight, with
        #   every post FOOTED ON A TREAD and every run end tied into a post or
        #   masonry (GT-72 (2)/(3)). Constraints in PARAMS["stair_handrail"].
        hr = PARAMS["stair_handrail"]
        run_f = st["n_flight"] * st["tread"]                  # 3.60
        drop_f = st["n_flight"] * st["riser"]                 # 1.98
        ang = math.degrees(math.atan2(drop_f, run_f))
        slope_L = math.hypot(run_f, drop_f)
        xc_mid = (st["x_head"] + st["x_turn"]) / 2.0
        y_ra = st["y_a1"] - hr["inset"]                       # 4.90 — on flight A
        y_rb = st["y_b0"] + hr["inset"]                       # 5.30 — on flight B

        def _nose_a(x):
            """Flight A nosing line: z 0 at the head x_head, −1.98 at the landing."""
            return (x - st["x_head"]) * drop_f / run_f

        def _nose_b(x):
            """Flight B nosing line: −1.98 at the landing, −3.96 at the corridor."""
            return st["mid_z"] - (x - st["x_turn"]) * drop_f / run_f

        def _tread_a(x):
            """Top of the flight-A tread that carries x (a post foots on THIS, not
            on the nosing line — the line runs up to one riser above the tread)."""
            k = min(st["n_flight"] - 1,
                    max(0, int(math.floor((st["x_head"] - x) / st["tread"]))))
            return -(k + 1) * st["riser"]

        def _tread_b(x):
            k = min(st["n_flight"] - 1,
                    max(0, int(math.floor((x - st["x_turn"]) / st["tread"]))))
            return st["mid_z"] - (k + 1) * st["riser"]

        def _foot_post(path, x, y, z_tread, z_top):
            """Post + base plate, seated `tread_embed` into the tread it stands on."""
            zb = z_tread - hr["tread_embed"]
            CYL(path, (x, y, (zb + z_top) / 2.0), hr["post_r"], z_top - zb,
                M["rail"], col=True)
            CYL(f"{path}_Plate", (x, y, z_tread + hr["plate_t"] / 2.0 - 0.003),
                hr["plate_r"], hr["plate_t"], M["rail"])

        n_tube = n_post = 0
        for tag, yc, nose, tread, sgn in (("A", y_ra, _nose_a, _tread_a, -1.0),
                                          ("B", y_rb, _nose_b, _tread_b, 1.0)):
            for lab, dz, rr in (("Top", hr["h"], hr["r"]),
                                ("Mid", hr["mid_h"], hr["r"] * 0.75)):
                z_w = nose(st["x_turn"]) + dz
                z_e = nose(st["x_head"]) + dz
                CYL(f"{ROOT}/StairHandrail/{lab}{tag}",
                    (xc_mid, yc, (z_w + z_e) / 2.0), rr, slope_L,
                    M["rail"], rotY=90.0 + sgn * ang)
                n_tube += 1
            for bx in hr["post_xs"]:
                _foot_post(f"{ROOT}/StairHandrail/Post{tag}_{int(bx * 100)}",
                           bx, yc, tread(bx), nose(bx) + hr["h"])
                n_post += 1
        # U-return round the landing's west nose. GT-72: the U now carries the MID
        #   tube as well (both flights' mid tubes used to die free at x_turn) and
        #   stands on two newels footed on the landing — it used to float.
        x_u = st["x_turn"] - hr["u_off"]
        z_top_u = st["mid_z"] + hr["h"]
        z_mid_u = st["mid_z"] + hr["mid_h"]
        for yc, tag in ((y_ra, "A"), (y_rb, "B")):
            _foot_post(f"{ROOT}/StairHandrail/UNewel_{tag}", x_u, yc,
                       st["mid_z"], z_top_u + hr["r"])
            n_post += 1
            for lab, zl, rr in (("Top", z_top_u, hr["r"]),
                                ("Mid", z_mid_u, hr["r"] * 0.75)):
                CYL(f"{ROOT}/StairHandrail/UStub{lab}_{tag}",
                    ((x_u + st["x_turn"] + 0.04) / 2.0, yc, zl), rr,
                    st["x_turn"] + 0.04 - x_u, M["rail"], rotY=90.0)
                n_tube += 1
        for lab, zl, rr in (("Top", z_top_u, hr["r"]),
                            ("Mid", z_mid_u, hr["r"] * 0.75)):
            CYL(f"{ROOT}/StairHandrail/UTurn{lab}",
                (x_u, (y_ra + y_rb) / 2.0, zl), rr, y_rb - y_ra,
                M["rail"], rotX=90.0)
            n_tube += 1
        # -- terminations: 0 free tube ends (GT-72 (2)) -----------------------
        #  HEAD (flight A, east): Top AND Mid return level into the door's north
        #    jamb post at x 11.30 — the jamb centre IS the rail line y 4.90 — and
        #    are carried at the rim by a newel footed on tread 1.
        ret_x1 = hr["jamb_x"] + hr["jamb_embed"]
        ret_x0 = min(hr["newel_x"], st["x_head"])
        for lab, dz, rr in (("Top", hr["h"], hr["r"]),
                            ("Mid", hr["mid_h"], hr["r"] * 0.75)):
            CYL(f"{ROOT}/StairHandrail/HeadReturn{lab}",
                ((ret_x0 + ret_x1) / 2.0, y_ra, dz), rr, ret_x1 - ret_x0,
                M["rail"], rotY=90.0)
            n_tube += 1
        _foot_post(f"{ROOT}/StairHandrail/HeadNewel", hr["newel_x"], y_ra,
                   _tread_a(st["x_head"] - st["tread"] / 2.0),
                   hr["h"] + hr["r"])
        n_post += 1
        #  FOOT (flight B, east): the rail line moved off Corridor_Wall_S
        #    (y ≤ 5.25), so the old wall-embedded stub would have ended in air.
        #    Top and Mid now return level to a newel footed on the corridor floor.
        z_f = _nose_b(st["x_head"])                    # −3.960 = corridor floor
        foot_x = hr["foot_newel_x"]
        for lab, dz, rr in (("Top", hr["h"], hr["r"]),
                            ("Mid", hr["mid_h"], hr["r"] * 0.75)):
            CYL(f"{ROOT}/StairHandrail/FootReturn{lab}",
                ((st["x_head"] + foot_x) / 2.0, y_rb, z_f + dz), rr,
                foot_x - st["x_head"], M["rail"], rotY=90.0)
            n_tube += 1
        _foot_post(f"{ROOT}/StairHandrail/FootNewel", foot_x, y_rb, z_f,
                   z_f + hr["h"] + hr["r"])
        n_post += 1
        print(f"[GT-72 자립 중앙 가드] 양면 STS r{hr['r']:.3f} · 답면 위 "
              f"{hr['h']:.2f}+{hr['mid_h']:.2f} · 레일선 A y {y_ra:.2f} "
              f"(플라이트 3.55~4.95 내) / B y {y_rb:.2f} (5.25~6.65 내) → 포스트 "
              f"{n_post}본 전량 답면 착지 (매입 {hr['tread_embed'] * 1000:.0f} mm "
              f"+ 베이스 플레이트) · 튜브 {n_tube}본 · 종단 = 머리 뉴얼+잼 매입 "
              f"{hr['jamb_embed'] * 1000:.0f} mm · U 뉴얼 2 (Top+Mid) · 복도 "
              f"뉴얼 x {foot_x:.2f} → 공중 종단 0")

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
    # Entry equipment — gantry sign + height-limit bar (08-05 2nd answer: gate deleted)
    # -------------------------------------------------------------------
    def build_entry_gear(M):
        """[W3 S13 · ruling §7-5 → 08-05 5th answer] entry sign + height bar,
        both canopy-mounted.

        The free-standing gantry frame is DELETED: with the deck connected to
        the mouth (canopy x0 = 0) a separate portal frame doubles the
        structure. The sign panel mounts on the west parapet band; the height
        bar hangs from the mouth beam (geometry constraints in the
        PARAMS["entry_sign"] note).
        """
        es = PARAMS["entry_sign"]
        xc_p = es["x_back"] - es["panel_t"] / 2.0
        BOX(f"{ROOT}/EntrySign/Panel",
            (xc_p, 0.0, (es["z0"] + es["z1"]) / 2.0),
            (es["panel_t"], 2.0 * es["y_half"], es["z1"] - es["z0"]),
            M["gantry"])
        # [08-06 user · GT-72] frame the panel: a cap coping over the top edge and
        #   two end stiles, each `cap_over` proud of the panel face on 3 sides, so
        #   the sign's top and ends are members instead of raw cut faces. The cap
        #   bottom laps 10 mm into the panel (no coplanar contact).
        #   `2 * cap_over` on the x size (not one-sided): a one-sided frame would
        #   leave the cap/stile FRONT faces bit-exact coplanar with the panel's
        #   own front face at x −0.01. The frame now stands 20 mm proud on both
        #   faces, which is what a capping section does anyway.
        co_, ct_ = es["cap_over"], es["cap_t"]
        BOX(f"{ROOT}/EntrySign/Cap",
            (xc_p, 0.0, es["z1"] - 0.010 + ct_ / 2.0),
            (es["panel_t"] + 2 * co_, 2.0 * (es["y_half"] + co_), ct_),
            M["gantry"])
        for sgn, tag in ((1.0, "N"), (-1.0, "S")):
            BOX(f"{ROOT}/EntrySign/Stile_{tag}",
                (xc_p, sgn * (es["y_half"] + co_ - es["stile_t"] / 2.0),
                 (es["z0"] + es["z1"] - 0.010) / 2.0),
                (es["panel_t"] + 2 * co_, es["stile_t"],
                 es["z1"] - es["z0"] - 0.010),
                M["gantry"])
        # height-limit bar — hung from the mouth beam (8 yellow/black segments)
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
                 (hb["hang_z0"] + hb["hang_z1"]) / 2.0),
                (hb["hanger_t"], hb["hanger_t"], hb["hang_z1"] - hb["hang_z0"]),
                M["gantry"])

    def build_canopy_full(M):
        """[08-05 user · U-5 literal] full-length ramp canopy — R13-1 canopy clause
        superseded by the user's gallery answer ("these entrances are covered").

        Library flat-deck idiom only (scene02 GT-3 / scene16): RC deck + fascia +
        transverse beams + coping-mounted steel columns. Geometry constraints are
        carried in the `PARAMS["canopy"]` note and re-checked by the smoke run.
        Ledger: row **GT-58** — R-3 re-stamp only (no walked surface moves; the
        OCCL baseline over the trench changes).
        """
        cp = PARAMS["canopy"]
        base = PARAMS["rail"]["base_z"]              # coping top = column base
        em = cp["embed"]
        L = cp["x1"] - cp["x0"]
        cx = (cp["x0"] + cp["x1"]) / 2.0
        BOX(f"{ROOT}/Canopy/Deck",
            (cx, 0.0, cp["z_roof"] + cp["roof_t"] / 2.0),
            (L, 2.0 * cp["y_deck"], cp["roof_t"]), M["roof"], col=True)
        # [08-05 3차] parapet band ring, 20 mm proud of the deck rim — wraps the
        #   deck edge and rises 0.16 above the deck top (building massing). W/E
        #   bands run the full width; N/S bands tuck 2 mm INTO the W/E solids
        #   (solid corners, no coplanar fascia/deck faces — see the PARAMS note).
        p = cp["fascia_proud"]
        fz = cp["fascia_top"] - cp["fascia_h"] / 2.0
        y_full = cp["y_deck"] + p
        for xe, tag in ((cp["x0"] - p + cp["fascia_t"] / 2.0, "W"),
                        (cp["x1"] + p - cp["fascia_t"] / 2.0, "E")):
            BOX(f"{ROOT}/Canopy/Fascia_{tag}", (xe, 0.0, fz),
                (cp["fascia_t"], 2.0 * (y_full - 0.002), cp["fascia_h"]),
                M["fascia"])
        # N/S bands sit 1 mm lower than W/E (verify r2: identical fz left the
        #   2 mm corner tuck strips with bit-exact coplanar soffit faces)
        x_in0 = cp["x0"] - p + cp["fascia_t"] - 0.002
        x_in1 = cp["x1"] + p - cp["fascia_t"] + 0.002
        for sgn, tag in ((1.0, "N"), (-1.0, "S")):
            BOX(f"{ROOT}/Canopy/Fascia_{tag}",
                ((x_in0 + x_in1) / 2.0,
                 sgn * (y_full - cp["fascia_t"] / 2.0), fz - 0.001),
                (x_in1 - x_in0, cp["fascia_t"], cp["fascia_h"]), M["fascia"])
        # column stations: mouth pair (height-bar beam, 5th answer) + regular
        #   pitch run — beams bear on every station (beam_w < col_w so no
        #   flank face is coplanar), tops embedded 20 mm.
        stations_col = ([cp["col_mouth_x"]]
                        + [cp["col_x0"] + k * cp["col_pitch"]
                           for k in range(int(cp["n_col"]))])
        for k, xb in enumerate(stations_col):
            BOX(f"{ROOT}/Canopy/Beam_{k}",
                (xb, 0.0, cp["z_roof"] - cp["beam_h"] / 2.0 + em),
                (cp["beam_w"], 2.0 * cp["y_col"], cp["beam_h"]), M["roof"])
        # columns on the coping, both flanks
        h_col = cp["z_roof"] - base + em
        for k, xc in enumerate(stations_col):
            for sgn, tag in ((1.0, "N"), (-1.0, "S")):
                BOX(f"{ROOT}/Canopy/Col_{tag}{k}",
                    (xc, sgn * cp["y_col"], base + h_col / 2.0),
                    (cp["col_w"], cp["col_w"], h_col), M["post"], col=True)
        # [08-05 3차] glass curtain walls on both flanks — scene06 DeckGlass
        #   3-part idiom: continuous steel kick band (swallowed by the column
        #   sections, faces 3.125/3.175 inside 3.08..3.22 → no coplanar) +
        #   jointed glass per column bay, top embedded 20 mm into the deck.
        gl = cp["glass"]
        gx0 = gl["x0"]                # [4th answer] glass runs to the trench edge
        n_glass = 0
        for sgn, tag in ((1.0, "N"), (-1.0, "S")):
            BOX(f"{ROOT}/Canopy/Kick_{tag}",
                ((gx0 + cp["x1"]) / 2.0, sgn * cp["y_col"],
                 (base - 0.02 + base + gl["kick_h"]) / 2.0),
                (cp["x1"] - gx0, gl["kick_t"], gl["kick_h"] + 0.02), M["post"])
        # [5th answer] the free-pane top channel (GlassCap) is deleted — the
        #   deck now covers the whole run and every pane top embeds into it.
        # [08-06 user · GT-72] MOUTH MULLION — the curtain wall's west terminal.
        #   Stations are now (x, half-section) pairs so the mullion, the columns
        #   and the two run ends are handled by one rule: a pane runs from
        #   `station + half + joint` to `next − half − joint`, i.e. every joint
        #   lands inside a section. Bay 0 comes out negative and is dropped by the
        #   0.05 m minimum-bay guard, so the run starts AT the mullion.
        gz0 = base + gl["kick_h"]
        gz1 = cp["z_roof"] + em
        mm = cp["mouth_mull"]
        for sgn, tag in ((1.0, "N"), (-1.0, "S")):
            BOX(f"{ROOT}/Canopy/MouthMullion_{tag}",
                (mm["x"], sgn * cp["y_col"], (base - 0.02 + gz1) / 2.0),
                (mm["w"], mm["w"], gz1 - base + 0.02), M["post"], col=True)
        gstations = ([(gx0, 0.0), (mm["x"], mm["w"] / 2.0)]
                     + [(xc, cp["col_w"] / 2.0) for xc in stations_col]
                     + [(cp["x1"], 0.0)])
        for b in range(len(gstations) - 1):
            (a, ha), (bxt, hb) = gstations[b], gstations[b + 1]
            ga_ = a + ha + gl["joint"]
            gb_ = bxt - hb - gl["joint"]
            if gb_ - ga_ < 0.05:
                continue
            for sgn, tag in ((1.0, "N"), (-1.0, "S")):
                BOX(f"{ROOT}/Canopy/Glass_{tag}{b}",
                    ((ga_ + gb_) / 2.0, sgn * cp["y_col"],
                     (gz0 + gz1) / 2.0),
                    (gb_ - ga_, gl["t"], gz1 - gz0),
                    M["glass_vc" if f"{tag}{b}" in GLASS_CLEAR_BAYS
                      else "glass_v"])
                n_glass += 1
        # [08-05 3차] solid end wall over the portal head — closes the box and
        #   masks Ground_E's west face (the green band portal_look showed).
        #   East face at 23.99 keeps 10 mm clear of the ground plane x=24 (no
        #   coplanar); bottom −1.25 laps the slab underside (−1.2), leaving
        #   2.46 m portal clear > posted 2.3.
        ew = cp["end_wall"]
        ew_x1 = cp["x1"] - 0.01
        BOX(f"{ROOT}/Canopy/EndWall",
            ((ew["x0"] + ew_x1) / 2.0, 0.0, (-1.25 + gz1) / 2.0),
            (ew_x1 - ew["x0"], 2.0 * (cp["y_deck"] - cp["fascia_t"] - 0.002),
             gz1 + 1.25), M["fascia"], col=True)
        # soffit lamps — recessed battens at the 7 mid-bay stations x 2 rows,
        #   each carrying one SphereLight (scene02 GT-3 recipe; ramp luminaires
        #   are Korean practice, not a render hack). Battens sit clear of the
        #   beams (mid-bay) and above the beam soffit line.
        n_lamp = 0
        bz = cp["z_roof"] - cp["lamp_t"] / 2.0 + em
        for k in range(len(stations_col) - 1):
            lx = (stations_col[k] + stations_col[k + 1]) / 2.0
            for r, ly in enumerate(cp["lamp_y"]):
                BOX(f"{ROOT}/Canopy/LampBatten_{r}{k}", (lx, ly, bz),
                    (cp["lamp_len"], cp["lamp_w"], cp["lamp_t"]), M["lamp"])
                lt = UsdLux.SphereLight.Define(
                    stage, f"{ROOT}/Canopy/Light_{r}{k}")
                lt.CreateRadiusAttr(float(cp["lamp_radius"]))
                lt.CreateIntensityAttr(float(cp["lamp_intensity"]))
                lt.CreateColorAttr(
                    Gf.Vec3f(*[float(c) for c in cp["lamp_color"]]))
                UsdGeom.Xformable(lt.GetPrim()).AddTranslateOp().Set(
                    Gf.Vec3d(float(lx), float(ly),
                             float(cp["z_roof"] - cp["lamp_t"] - 0.02)))
                n_lamp += 1
        print(f"[U-5 캐노피] 전장 플랫데크 x {cp['x0']:.2f}…{cp['x1']:.2f} "
              f"({L:.2f} m — 5차: 마우스까지 연결) · 데크 밑면 z {cp['z_roof']:.2f} · "
              f"보 {len(stations_col)}본 · 기둥 {len(stations_col)}쌍 "
              f"(코핑 위 y ±{cp['y_col']:.2f}, 마우스 스테이션 x "
              f"{cp['col_mouth_x']:.2f}) · 유리 {n_glass}판 · "
              f"소핏 {n_lamp}등 (2열 × {len(stations_col) - 1})")
        print(f"[GT-72 마우스 에지] 커튼월 종단 멀리언 2본 x "
              f"{mm['x'] - mm['w'] / 2.0:.2f}…{mm['x'] + mm['w'] / 2.0:.2f} "
              f"(코핑 위 y ±{cp['y_col']:.2f}) → 유리 서단 노출 에지 2.31 m "
              f"→ 0 · 킥밴드 서단면 피복 · 내면 "
              f"{cp['y_col'] - mm['w'] / 2.0:.2f} > 유효폭 3.00 → "
              f"{'OK' if cp['y_col'] - mm['w'] / 2.0 > 3.0 else 'FAIL'}")

    def build_stair_canopy(M):
        """[08-05 user, 2nd/3rd answers] pedestrian stair-entry structure —
        U-5 applies to the pedestrian entrance too. Building form (GT-59/60):
        flat deck + parapet band + glass walls on the shaft W/N rims + soffit
        lamps. Geometry constraints live in the PARAMS["stair_canopy"] note."""
        cp = PARAMS["stair_canopy"]
        em = cp["embed"]
        p = cp["fascia_proud"]
        ft = cp["fascia_t"]
        L = cp["x1"] - cp["x0"]
        W = cp["y1"] - cp["y0"]
        cx = (cp["x0"] + cp["x1"]) / 2.0
        cy = (cp["y0"] + cp["y1"]) / 2.0
        base = PARAMS["rail"]["base_z"]           # shaft coping top
        BOX(f"{ROOT}/StairCanopy/Deck",
            (cx, cy, cp["z_roof"] + cp["roof_t"] / 2.0),
            (L, W, cp["roof_t"]), M["roof"], col=True)
        # parapet band ring — W/E bands full width (end caps 2 mm inside the
        #   N/S solids); N/S bands tuck 2 mm into the W/E solids AND sit 1 mm
        #   lower (verify r2: identical fz left 2 mm corner strips with
        #   bit-exact coplanar soffit faces).
        fz = cp["fascia_top"] - cp["fascia_h"] / 2.0
        x_out0, x_out1 = cp["x0"] - p, cp["x1"] + p
        for xe, tag in ((x_out0 + ft / 2.0, "W"), (x_out1 - ft / 2.0, "E")):
            BOX(f"{ROOT}/StairCanopy/Fascia_{tag}", (xe, cy, fz),
                (ft, W + 2.0 * p - 0.004, cp["fascia_h"]), M["fascia"])
        x_in0, x_in1 = x_out0 + ft - 0.002, x_out1 - ft + 0.002
        for ye, tag in ((cp["y1"] + p - ft / 2.0, "N"),
                        (cp["y0"] - p + ft / 2.0, "S")):
            BOX(f"{ROOT}/StairCanopy/Fascia_{tag}",
                ((x_in0 + x_in1) / 2.0, ye, fz - 0.001),
                (x_in1 - x_in0, ft, cp["fascia_h"]), M["fascia"])
        # transverse beams on the support lines (flat-deck idiom kept honest —
        #   verify r2 flagged a 6.45 m unsupported 0.10 m slab)
        for i, xb in enumerate(cp["beam_xs"]):
            BOX(f"{ROOT}/StairCanopy/Beam_{i}",
                (xb, cy, cp["z_roof"] - cp["beam_h"] / 2.0 + em),
                (cp["beam_w"], W - 0.10, cp["beam_h"]), M["roof"])
        # posts: W pair on solid ground + the three x=11.30 members (GT-64) —
        #   two door jambs and one north post. The single mid-mouth newel of
        #   verify r2 is gone; the x=11.30 beam now bears at 3 points, not 1.
        h = cp["z_roof"] + em
        for i, (px, py) in enumerate(cp["posts"]):
            BOX(f"{ROOT}/StairCanopy/Post_{i}", (px, py, h / 2.0),
                (cp["post_w"], cp["post_w"], h), M["post"], col=True)
        # side guard, mode-switchable [4th answer]: "rail" -> the shaft rail
        #   runs are built by build_railings (PARAMS stair_rail_runs); "glass"
        #   -> DeckGlass 3-part idiom walls (round-3 form) built here.
        n_gp = 0
        # [08-06 user · GT-72] curtain-wall TERMINAL POSTS. Without them the W run
        #   ended in a free pane edge at y 3.50 and the two runs crossed at the NW
        #   corner with 0.10~0.125 m of pane past each other. The NE corner is the
        #   frame post (11.30, 6.775) in `posts`. Each run's a0/a1 is now a post
        #   centreline, so the 12 mm pane joint lands inside the post section.
        gz1_p = cp["z_roof"] + em
        for i, (px, py, pw) in enumerate(cp["glass_posts"]):
            BOX(f"{ROOT}/StairCanopy/GlassPost_{i}",
                (px, py, (base - 0.02 + gz1_p) / 2.0),
                (pw, pw, gz1_p - base + 0.02), M["post"], col=True)
        specs = (((cp["glass_w"], "y", "W"), (cp["glass_n"], "x", "N"))
                 if cp["side_mode"] == "glass" else ())
        for spec, axis, tag in specs:
            run = spec["a1"] - spec["a0"]
            n_bay = max(1, int(round(run / cp["mullion"]["spacing"])))
            mw = cp["mullion"]["w"]
            gz0, gz1 = base + 0.12, cp["z_roof"] + em
            #  [GT-72] band foot at `kick_z0`, not at the coping top — PARAMS note
            kz = (cp["kick_z0"] + gz0) / 2.0
            kh = gz0 - cp["kick_z0"]
            if axis == "y":
                BOX(f"{ROOT}/StairCanopy/Kick_{tag}",
                    (spec["c"], (spec["a0"] + spec["a1"]) / 2.0, kz),
                    (0.05, run, kh), M["post"])
            else:
                BOX(f"{ROOT}/StairCanopy/Kick_{tag}",
                    ((spec["a0"] + spec["a1"]) / 2.0, spec["c"], kz),
                    (run, 0.05, kh), M["post"])
            for b in range(n_bay):
                a = spec["a0"] + b * run / n_bay
                bnd = spec["a0"] + (b + 1) * run / n_bay
                ga_, gb_ = a + 0.012, bnd - 0.012
                ctr = (ga_ + gb_) / 2.0
                if axis == "y":
                    BOX(f"{ROOT}/StairCanopy/Glass_{tag}{b}",
                        (spec["c"], ctr, (gz0 + gz1) / 2.0),
                        (0.019, gb_ - ga_, gz1 - gz0), M["glass_v"])
                else:
                    BOX(f"{ROOT}/StairCanopy/Glass_{tag}{b}",
                        (ctr, spec["c"], (gz0 + gz1) / 2.0),
                        (gb_ - ga_, 0.019, gz1 - gz0), M["glass_v"])
                n_gp += 1
                if b < n_bay - 1:
                    ms = spec["a0"] + (b + 1) * run / n_bay
                    mc = ((spec["c"], ms) if axis == "y" else (ms, spec["c"]))
                    BOX(f"{ROOT}/StairCanopy/Mullion_{tag}{b}",
                        (mc[0], mc[1], (gz0 + gz1) / 2.0),
                        (mw, mw, gz1 - gz0), M["post"])
        # [08-06 user · GT-64 → GT-72] EAST ENTRANCE FACE — steel frame, a SINGLE
        #   leaf modelled OPEN (95 deg hold-open) + a fixed sidelight over the rest
        #   of the clear opening, fixed glass over the remainder of the rim.
        #   Layout, hold-open clearance and the corner rule are proved in the
        #   PARAMS["stair_canopy"]["east"] note and re-checked by the smoke run;
        #   nothing here moves the shaft rect, the stair, or the registered 3.96 m
        #   drop edge at x 11.20.
        ea = cp["east"]
        ex = ea["x"]
        beam_soffit = cp["z_roof"] - cp["beam_h"] + em          # 2.31
        lp = ea["lap"]
        jy0, jy1 = ea["jamb_y"]                                 # jamb centrelines
        n_leaf = 0
        #  threshold sill plate — the frame foot lands on a member, not on turf.
        #  Top 8 mm proud of the apron: a sill, not a step (continuity row 2b).
        BOX(f"{ROOT}/StairCanopy/DoorSill",
            (ex, (jy0 + jy1) / 2.0, ea["sill_t"] / 2.0 - 0.004),
            (ea["leaf_t"] + 2 * ea["sill_over"], jy1 - jy0, ea["sill_t"]),
            M["rail"])
        #  head member over the whole clear opening, jamb centre to jamb centre
        BOX(f"{ROOT}/StairCanopy/DoorHead",
            (ex, (jy0 + jy1) / 2.0, ea["door_z1"] + ea["head_h"] / 2.0),
            (ea["leaf_t"] + 0.02, jy1 - jy0, ea["head_h"]), M["post"])
        #  transom: fixed glass from the door head up into the beam soffit. Both
        #  ends land on the jamb centrelines and the bottom laps into the head, so
        #  the band leaves no slot and no coincident face.
        BOX(f"{ROOT}/StairCanopy/DoorTransom",
            (ex, (jy0 + jy1) / 2.0,
             (ea["door_z1"] + ea["head_h"] - lp + beam_soffit + em) / 2.0),
            (ea["glass_t"], jy1 - jy0,
             beam_soffit + em - ea["door_z1"] - ea["head_h"] + lp),
            M["glass_vc"])
        st_w = ea["stile"]
        #  glazing mullion + fixed sidelight between the leaf and the north jamb.
        #  Both lap `lap` UP into the head member instead of stopping flush on its
        #  soffit, so no member top is coplanar with the head's underside.
        BOX(f"{ROOT}/StairCanopy/DoorMullion",
            (ex, ea["mull_y"], (ea["door_z1"] + lp) / 2.0),
            (ea["leaf_t"], ea["mull_w"], ea["door_z1"] + lp), M["post"])
        sy0 = ea["mull_y"] + ea["mull_w"] / 2.0 - lp
        sy1 = ea["jamb_y"][1]
        BOX(f"{ROOT}/StairCanopy/DoorSideKick",
            (ex, (sy0 + sy1) / 2.0, (ea["kick_h"] - 0.02) / 2.0),
            (ea["kick_t"], sy1 - sy0, ea["kick_h"] + 0.02), M["post"])
        BOX(f"{ROOT}/StairCanopy/DoorSidelight",
            (ex, (sy0 + sy1) / 2.0,
             (ea["kick_h"] - lp + ea["door_z1"] + lp) / 2.0),
            (ea["glass_t"], sy1 - sy0, ea["door_z1"] - ea["kick_h"] + 2 * lp),
            M["glass_vc"])
        n_gp += 1
        #  ── the single leaf, modelled OPEN ────────────────────────────────
        #  Leaf-local (u along the leaf from the hinge, v across its thickness).
        #  `add_box(rotZ=-open_deg)` maps local +y → (sin, cos) and local +x →
        #  (cos, −sin), which is exactly the map below, so member centres and the
        #  prim rotation stay consistent (no member is placed by eye).
        th = math.radians(ea["open_deg"])
        sn, ct = math.sin(th), math.cos(th)
        hx, hy = ea["hinge_x"], ea["hinge_y"]
        rz = -ea["open_deg"]
        lw, lt = ea["leaf_w"], ea["leaf_t"]
        z0l, z1l = ea["leaf_z0"], ea["door_z1"]
        br = ea["bot_rail"]

        def _leafxy(u, v=0.0):
            return (hx + u * sn + v * ct, hy + u * ct - v * sn)

        for lab, uc, uw in (("SH", st_w / 2.0, st_w),          # hinge stile
                            ("SL", lw - st_w / 2.0, st_w)):    # lock stile
            lx, ly = _leafxy(uc)
            BOX(f"{ROOT}/StairCanopy/Leaf_{lab}", (lx, ly, (z0l + z1l) / 2.0),
                (lt, uw, z1l - z0l), M["post"], rotZ=rz)
        for lab, zc_, hz_ in (("RB", z0l + br / 2.0, br),
                              ("RT", z1l - st_w / 2.0, st_w)):
            lx, ly = _leafxy(lw / 2.0)
            BOX(f"{ROOT}/StairCanopy/Leaf_{lab}", (lx, ly, zc_),
                (lt, lw - 2 * st_w, hz_), M["post"], rotZ=rz)
        gz_lo, gz_hi = z0l + br - lp, z1l - st_w + lp
        lx, ly = _leafxy(lw / 2.0)
        BOX(f"{ROOT}/StairCanopy/Leaf_Glass", (lx, ly, (gz_lo + gz_hi) / 2.0),
            (ea["glass_t"], lw - 2 * st_w + 2 * lp, gz_hi - gz_lo),
            M["glass_v"], rotZ=rz)
        #  pull handle on the leaf's outer face, seated 0.6 r into the stile
        hxp, hyp = _leafxy(lw - 0.12, lt / 2.0 + ea["handle_r"] * 0.6)
        CYL(f"{ROOT}/StairCanopy/Leaf_Handle", (hxp, hyp, 1.05),
            ea["handle_r"], 0.30, M["rail"])
        #  two butt hinges: a knuckle on the axis + a strap that reaches 80 mm
        #  INTO the jamb post, so the leaf hangs on hardware and the 30 mm hinge
        #  offset is not an air gap.
        for i, hz in enumerate((0.35, 1.85)):
            CYL(f"{ROOT}/StairCanopy/Leaf_Hinge{i}", (hx, hy, hz),
                ea["hinge_r"], ea["hinge_h"], M["rail"])
            BOX(f"{ROOT}/StairCanopy/Leaf_HingeStrap{i}",
                ((ex + hx) / 2.0, hy, hz),
                (hx - ex + 0.06, 0.045, 0.09), M["rail"])
        #  hold-open stay: jamb anchor → leaf, both ends at `stay_z`, so one
        #  bearing-laid tube (rotY 90 then rotZ = its own plan bearing) does it.
        #  It attaches to the leaf face that TURNS TOWARD the south jamb as the
        #  door swings (leaf-local v = +t/2); anchoring on −t/2 would run the arm
        #  straight through the leaf `[computed: both ends must share the sign]`.
        ax, ay = ex + ea["leaf_t"] / 2.0, jy0
        bx_, by_ = _leafxy(ea["stay_u"], lt / 2.0)
        sdx, sdy = bx_ - ax, by_ - ay
        CYL(f"{ROOT}/StairCanopy/Leaf_Stay",
            ((ax + bx_) / 2.0, (ay + by_) / 2.0, ea["stay_z"]),
            ea["stay_r"], math.hypot(sdx, sdy), M["rail"], rotY=90.0,
            rotZ=math.degrees(math.atan2(sdy, sdx)))
        n_leaf += 1
        #  fixed glass closing the rest of the east face, from the north jamb's
        #  CENTRELINE to the NE corner post's centreline — both 12 mm joints land
        #  inside a post section, so neither end is a free pane edge.
        fy0, fy1 = ea["jamb_y"][1], cp["glass_n"]["c"]
        run_e = fy1 - fy0
        n_bay_e = max(1, int(math.ceil(run_e / ea["mullion_span"])))
        BOX(f"{ROOT}/StairCanopy/EastKick",
            (ex, (fy0 + fy1) / 2.0, (ea["kick_h"] - 0.02) / 2.0),
            (ea["kick_t"], run_e, ea["kick_h"] + 0.02), M["post"])
        for b in range(n_bay_e):
            a = fy0 + b * run_e / n_bay_e
            bnd = fy0 + (b + 1) * run_e / n_bay_e
            BOX(f"{ROOT}/StairCanopy/EastGlass_{b}",
                (ex, (a + bnd) / 2.0 + 0.0,
                 (ea["kick_h"] + beam_soffit + em) / 2.0),
                (ea["glass_t"], bnd - a - 0.024,
                 beam_soffit + em - ea["kick_h"]), M["glass_v"])
            n_gp += 1
            if b < n_bay_e - 1:
                BOX(f"{ROOT}/StairCanopy/EastMullion_{b}",
                    (ex, bnd, (ea["kick_h"] + beam_soffit + em) / 2.0),
                    (ea["mullion_w"], ea["mullion_w"],
                     beam_soffit + em - ea["kick_h"]), M["post"])
        # soffit lamps — the sealed shaft repeats the r1 DARK failure without
        #   them (stair_head 109.9 -> 57.1 measured); same recipe, small scale
        n_sl = 0
        bz = cp["z_roof"] - cp["lamp_t"] / 2.0 + em
        for ly in cp["lamp_rows"]:
            for lx in cp["lamp_xs"]:
                BOX(f"{ROOT}/StairCanopy/LampBatten_{n_sl}", (lx, ly, bz),
                    (cp["lamp_len"], cp["lamp_w"], cp["lamp_t"]), M["lamp"])
                lt = UsdLux.SphereLight.Define(
                    stage, f"{ROOT}/StairCanopy/Light_{n_sl}")
                lt.CreateRadiusAttr(float(cp["lamp_radius"]))
                lt.CreateIntensityAttr(float(cp["lamp_intensity"]))
                lt.CreateColorAttr(Gf.Vec3f(0.93, 0.96, 1.0))
                UsdGeom.Xformable(lt.GetPrim()).AddTranslateOp().Set(
                    Gf.Vec3d(float(lx), float(ly),
                             float(cp["z_roof"] - cp["lamp_t"] - 0.02)))
                n_sl += 1
        print(f"[U-5 계단 캐노피] x {cp['x0']:.2f}…{cp['x1']:.2f} · "
              f"y {cp['y0']:.2f}…{cp['y1']:.2f} · 밑면 z {cp['z_roof']:.2f} · "
              f"포스트 {len(cp['posts'])}본(문틀 잼 2 + 북측 1 + 서측 2) · 측면 "
              f"{'유리 ' + str(n_gp) + '판' if cp['side_mode'] == 'glass' else '난간(rail 모드)'} · "
              f"소핏 {n_sl}등")
        tip_x = hx + lw * sn
        ws_, sr_ = PARAMS["walk_spur"], PARAMS["spur_ramp"]
        ramp_top = (PARAMS["drive"]["proud"]
                    + max(0.0, min(sr_["run"], tip_x - sr_["x0"]))
                    / sr_["run"] * (ws_["proud"] - PARAMS["drive"]["proud"]))
        print(f"[GT-72 계단 출입문] 강재 프레임 + 외짝 {n_leaf}짝 **개방 모델** "
              f"({ea['open_deg']:.0f}° 홀드오픈, 힌지 x {hx:.2f}/y {hy:.2f}) · "
              f"유효 통과폭 {lw:.2f} m ≥ 0.90 → "
              f"{'OK' if lw >= 0.90 else 'FAIL'} · 구조 개구 "
              f"{ea['door_y1'] - ea['door_y0']:.2f} m = 문짝 {lw:.2f} + 멀리언 "
              f"{ea['mull_w']:.2f} + 측창 {ea['door_y1'] - ea['mull_y'] - ea['mull_w'] / 2.0:.2f}")
        print(f"    문짝 선단 x {tip_x:.3f} · 그 지점 스퍼 턱낮춤 상면 "
              f"{ramp_top:+.3f} vs 문짝 하단 {ea['leaf_z0']:+.3f} → 이격 "
              f"{ea['leaf_z0'] - ramp_top:+.3f} m "
              f"{'OK (관통 0)' if ea['leaf_z0'] > ramp_top else 'FAIL(포장 관통)'}"
              f" · 문 상단 {ea['door_z1']:.2f} + 트랜섬 → 보 밑면 "
              f"{beam_soffit:.2f} · 잔여 동측면 고정유리 {n_bay_e}판 "
              f"(y {fy0:.2f}…{fy1:.2f} — NE 코너 포스트까지)")

    def build_wall_graphics(M):
        """[W3 S13 · G13] yellow/black bands + reflective guidance strip on the cheeks.

        They sit on the **inner** faces (y = ±3.0), the only wall surface this scene
        exposes: G13's above-ground parapet is a *compliant* guarding condition, while
        scene13 keeps the flush coping (08-05: the railing gap itself was repaired —
        the flush coping, not the gap, is what remains of the below-code identity).
        Adding the parapet would delete the scene's research content, so it is
        deliberately not adopted — recorded in `Docs/reports/w3_s13_v1.md` §3
        (08-05 caveat: §3-1's "the 3 m gap is this scene's hazard" leg is void —
        the gap is repaired under GT-58; only the flush-coping leg still holds).
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
        # [08-05 user, 2nd answer] barrier gate (Gate/Box + 7-seg arm) deleted (GT-59).

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
        # [08-06 · GT-64] the same convention at the intersection's two crossings.
        #   Rows stand `off` = 0.15 m outside the carriageway edge, i.e. on the
        #   turn-down itself — so they are seated on the RAMP surface at that
        #   station, not on the carriageway datum (the GT-5 lesson `cross_ramp_z`
        #   exists for). Tactile stays OFF (§4-6).
        xg, xr = xroad_geom(), PARAMS["xroad"]
        off = 0.15
        gz_x = (PARAMS["drive"]["proud"] + off / xr["ramp_run"]
                * (PARAMS["walk_north"]["proud"] - PARAMS["drive"]["proud"]))
        n_xb = 0
        rows_x = [("E", (xg["car1"] + off, None)), ("W", (xg["car0"] - off, None)),
                  ("N", (None, PARAMS["ramp"]["y1"] + off)),
                  ("S", (None, PARAMS["ramp"]["y0"] - off))]
        for tag, (cx_, cy_) in rows_x:
            stations = (xr["cross_ys"] if cx_ is not None
                        else xr["link_bollard_xs"])
            for i, a in enumerate(stations):
                bx, by = (cx_, a) if cx_ is not None else (a, cy_)
                sc.build_bollard(stage, f"{ROOT}/XBollard_{tag}_{i}", bx, by,
                                 gz_x, mtl=M["bollard"],
                                 radius=bo["r"], height=bo["h"])
                CYL(f"{ROOT}/XBollardBand_{tag}_{i}",
                    (bx, by, gz_x + bo["band_z"]),
                    bo["band_r"], bo["band_h"], M["band"])
                n_xb += 1
        print(f"[GT-64] 교차로 볼라드 {n_xb}본 (남북 횡단 4 + 동서 차도 횡단 4) · "
              f"h {bo['h']:.2f} · 간격 "
              f"{abs(xr['cross_ys'][1] - xr['cross_ys'][0]):.1f} m · tactile OFF")

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

        runs = list(PARAMS["rail_runs"])
        if PARAMS["stair_canopy"]["side_mode"] == "rail":
            runs += list(PARAMS["stair_rail_runs"])
        for i, rr in enumerate(runs):
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
    # Dressing — planters · trees · hedges · benches · lamps · 4 apartment blocks
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
        # [08-06 user · GT-64] four rows now follow the road network, and every
        #   station is filtered by `tree_stations()` against `tree_keepout()`:
        #   "nothing may penetrate structures — enforce a numeric clearance ≥ 0.5 m,
        #   scaled by crown radius". Offending stations are DROPPED (a Korean street
        #   row is simply omitted where a structure occupies the verge) so the legal
        #   4~8 m pitch of §4-4 is never bent. Parked item **P-6** (scene13 planting)
        #   is overridden by this direct user instruction — GT-59 precedent, and
        #   ledger row GT-64 is the amendment record.
        keep, dropped = tree_stations()
        for r, k, tx, ty, _tag, _g, _need in keep:
            sc.build_tree(stage, f"{ROOT}/Tree_{r}_{k}", tx, ty, 0.0,
                          *tree_mtls, species=TREE_SPECIES,
                          trunk_h=PARAMS["tree_trunk_h"])
        n_tree = len(keep)
        print(f"[K4(b) · GT-64] 노선대(route) 가로수 {n_tree}주 / 스테이션 "
              f"{n_tree + len(dropped)} (제외 {len(dropped)}) · {len(PARAMS['tree_rows'])}행 "
              f"도로망 추종 · 단일수종 '{TREE_SPECIES}' · 피치 "
              f"{PARAMS['tree_pitch']:.1f} m (TREE_PITCH_M) · 수관 반경 "
              f"{tree_crown_r():.2f} m · 구조물 이격 ≥ "
              f"{PARAMS['tree_clear']:.2f} m · 갓길대(verge) 화단수 "
              f"{sum(1 for p in PARAMS['planters'] if p['tree'])}주 = "
              "SCENE_SPECIES['Scene13'] 행")
        for r, k, tx, ty, tag, g, need in dropped:
            print(f"[GT-64] 가로수 제외 행{r}#{k} ({tx:+.2f},{ty:+.2f}) — "
                  f"{tag} 이격 {g:.2f} < {need:.2f} m")
        # [08-05 user, 5th answer · GT-62] hedge bands: box+crown blobs → rows of
        # real clipped shrub USDs (rationale and clearances: PARAMS["hedge"]
        # note). Asset-first, no material authoring — the Privet asset carries
        # its own season-neutral leaf MDL, so the material-work freeze holds.
        # A run without the assets (or LOOK_GEO=0) degrades to the legacy
        # build_hedge instead of emptying the verge (scene03 03-D precedent).
        hg = PARAMS["hedge"]
        n_hedge = 0
        for i, (hx0, hy0, hx1, hy1) in enumerate(PARAMS["hedges"]):
            seed = gk.det_seed("scene13.hedge", i)
            jr = gk.det_rng("scene13.hedge.jit", i)
            cx0, cx1 = hx0 + hg["end_margin"], hx1 - hg["end_margin"]
            cy = (hy0 + hy1) / 2.0
            span = max(cx1 - cx0, 1e-6)
            n = max(2, int(math.ceil(span / hg["pitch"])) + 1)
            step = span / (n - 1)
            pts = [(cx0 + k * step
                    + jr.uniform(-hg["jit_along"], hg["jit_along"]),
                    cy + jr.uniform(-hg["jit_across"], hg["jit_across"]),
                    0.0) for k in range(n)]
            placed = sc.place_shrubs(stage, f"{ROOT}/Hedge_{i}", pts,
                                     hg["target_h"], pool=hg["pool"],
                                     seed=seed, overlap=hg["overlap"])
            if not placed:
                sc.build_hedge(stage, f"{ROOT}/Hedge_{i}", hx0, hy0, hx1,
                               hy1, 0.85, base_z=0.0)
            n_hedge += placed
        print(f"[GT-62] 생울타리 {len(PARAMS['hedges'])}밴드 · 실관목 {n_hedge}주 "
              f"(place_shrubs pool=Privet · h {hg['target_h']:.2f}"
              f"×{1 + hg['overlap']:.2f} · 폴백 {'무' if n_hedge else 'build_hedge'})")
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
        # [08-05 user, 2nd answer] build_utility (poles/transformer/wires) deleted
        #   — uninstructed assets. It was a G13 signature, but the user's
        #   instruction outranks the reference (GT-59).

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
        build_entry_gear(M)          # [W3 S13 · 5차] parapet sign + canopy-hung bar
        build_canopy_full(M)         # [08-05 user · U-5 literal] full-length canopy
        build_stair_canopy(M)        # [08-05, 2nd/3rd answers] stair-entry glazed box
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
