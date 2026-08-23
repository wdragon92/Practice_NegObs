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

Smoke / self-check (no Isaac boot):  NEGOBS_SMOKE=1 python3 scene02_underpass.py

===========================================================================
W3 · CB-7 respec (2026-07-31) — GT-1 flood sill · GT-2 curb · GT-3 canopy REBUILD
===========================================================================
LAW: `Docs/surveys/w3_intake_v2_images.md` §2 scene02 row + §3(i) + §7-1 ·
     `Docs/audit_v4/gt_changes_w3.md` §3 GT-1/GT-2/GT-3 (as amended by the
     07-31 supervisor batch §9-1) · `Docs/briefs/w3_execution_spec_v1.md` §1.5
     (Option-A canopy-deletion clause **superseded**; sill/curb/landing-block
     clauses stand) · target image `Docs/reference_photos/Generated Image - Scene02.jpg`
     (**G2**) · user 2nd review *"Scene2 참조해서 좀 더 지하도 느낌으로"* and
     *"지하 진입로 … 캐노피 진입로 끝까지"*.

**The stale v8 landing / mid-rail proposal that used to live here is DELETED**, per
spec §1.5 and `era_consistency_survey_v1.md:881` (*02 landing (L1) = CANCEL* — 지하보도
is a 도로 부속물, outside 건축법 in every era, and landings are never retrofitted).
It was never in the code, so nothing is removed from the stage by the deletion; the
pit end stays at `x1 = 7.0`.

[GT-1] Flood sill — 침수방지 진입 단차  `[law - 행안부 「지하공간 침수방지를 위한
       수방기준 실무매뉴얼」 3-1-1 해설(2): 18 cm 계단 1~3개 + 난간 반드시 설치]`
  · raised apron  x −1.20 … 0.00 · y ±2.10 · top **z = +0.18** (1 step of 0.18 ≤ 0.18)
  · **one 0.18 m riser at x = −1.20 — an UP-STEP, not a drop.** Label accordingly.
  · the descent now begins from +0.18, so the drop edge at x = 0 carries **3.380 m**
    (was 3.200). The stair keeps 20 steps and tread 0.320 (run 6.400 unchanged, nosing
    period unchanged); the riser becomes 3.380/20 = **0.169 m** (≤ 0.18 statutory), so the
    foot still lands exactly on the lower landing at −3.200 and neither the landing, the
    tunnel nor the portal moves.
  · parapet/lintel top +0.15 → **+0.18**, flush with the apron: the 계단폭 doubles as the
    둑마루 the manual names, and the seam at x = 0 closes.
  · **난간 반드시 설치**: a short handrail line on each flank of the sill, y = ±1.68,
    x −1.12 … −0.32, 0.85 m above the apron, meeting the stair handrail's top extension at
    x = −0.32 so the two read as one line. Posts stand on **RF-1 bolted base plates**
    (`props_kit.build_base_plate`) in the **RF-2** `sts304_10s` rung — the sill is a 2024
    retrofit, the entrance is not, and *that contrast is the deliverable*. Every other post
    in the scene stays cast-in.
  · NOT built: the spec §1.5 companion 1:12 ramp and the x = −1.30 linear trench grating.
    Both would be **undeclared GT geometry** (GT-1's row fixes the apron and *one* riser),
    and the trench is refused by this scene's own measured B7 finding
    (`Docs/reports/w2d_edit_g1.md` §3). Recorded in `Docs/reports/w3_cb7_v1.md` §8.

[GT-2] Curb reshape — the library's one outright shape error
  · was: `curb_top +0.10` above a 0.0 footway = a 100 mm trip line along the walk.
  · now: `infra_kit.build_curb_line`, 1 m unit blocks with a 6 mm joint recess and the
    R = 10 mm arris carried by `LOOK_CLASS["curb"]`. Carriageway datum −0.02 → **−0.130**
    (the only way exposure 150 mm and "curb top flush … +20 mm above the footway" hold at
    the same time), exposure above carriageway **0.150**, curb top **+0.020**.
  · `gutter=False` — this scene already switched `gutter_L` off with a measured reason
    (see `gkit` below), so `gt_drop` = 0.150 exactly.

[GT-3] Canopy — **content FLIPPED by the supervisor**: deletion → full-length enclosure
  · the old `EntryCanopy` (4 free posts + a 2.40 × 4.90 m slab covering 0.60 m of a
    ≈7.6 m descent) is **deleted**; none of its 5 prims carried a hazard or drop label.
  · new: a continuous canopy **x −1.90 … 7.15** (9.05 m) — 1.90 m of approach measured
    from the pit edge (GT-3/U-5 require ≥ 1.00 m; scene16 has exactly 1.00), the sill
    riser and its apron, the whole 6.40 m descent, the lower landing and the pit rear.
    Roof springs from the parapet walls on a **column line** (5 pairs at 2.26 m),
    **side infill** (glazing + spandrel between the columns, closing the flank against the
    parapet and the perimeter rail), and **soffit lighting** — 2 rows × 5 recessed 1.20 m
    battens at 2.20 m pitch, the spacing G2 shows. scene16 (`:84`, x −1.0 … 4.6) is the
    in-library reference form; this is the same form at 02's length.
  · GT class: **R-3 only.** A canopy moves no walked surface. The OCCL baseline moves and
    the prim delta is **positive** — see the ledger row.

[G2 finishes] the pit's flanking walls get **tile cladding** (inner 40 mm of the 300 mm
  retaining wall) under a **granite coping** (top 60 mm, 20 mm proud each side), which is
  what G2 shows and what a Korean 지하보도 mouth is actually built of. The structural
  parapet height and the perimeter guard rail are **not** re-litigated: the rail is this
  scene's grazing-angle identity cue and the guard for a 3.38 m hole.

[BS-4] dense downtown backdrop on **both** verges (`building_kit`, `kind="backdrop"`,
  judged-eye framing), with the corner gap the cross-street at x 8…13 requires. The old
  `Building_B` brick slab (x −14…10, y 9…13) overlapped the carriageway and is replaced by
  the north row; `Building_C` (the +X vista) stays.

[Walking-continuity z ladder]  approach → UP-STEP → sill → descend → landing → tunnel
  ┌ #  section              x range          top z       step / verdict
  │ 0  ground sidewalk       ≤ −1.20         +0.000      flat
  │ 1  **sill riser**        x = −1.20       —           **+0.180 UP-STEP** (not a drop)
  │ 2  sill apron       −1.20 … 0.00         +0.180      flat 1.200 (y ±2.10)
  │ 3  drop edge             x = 0.00        +0.180      **drop 3.380** to the pit floor
  │ 4  stair step 1     0.00 … 0.32          +0.011      0.169
  │ 5  stair step 10    2.88 … 3.20          −1.510      0.169 × 9
  │ 6  stair step 20    6.08 … 6.40          −3.200      0.169 × 10
  │ 7  lower landing    6.40 … 7.00          −3.200      0.000 (flush)
  └ 8  tunnel floor     7.00 … 11.00         −3.200      0.000 (flush)
  * 20 × 0.169 = 3.380 = 0.180 (sill) + 3.200 (old drop). Run 6.400 and the 0.320 nosing
    period are **bit-identical to the pre-state** — the silhouette cue is untouched.
  * Every riser ≤ 0.180 「지하도로시설기준에 관한 규칙」 · every riser ≤ 0.200 outdoor rule.

[Camera occlusion check]
  · grid gy stays 0.000 — no mid rail exists (the v8 proposal is deleted), so the scene01
    R2-1 central-railing avoidance does not apply.
  · h0.3 concealment is **strengthened, not weakened**: the sill raises the near lip by
    0.18 m, so the sight line grazing the new edge (x = 0, z = +0.18) is steeper than
    before and reaches even less of the pit floor.
  · The canopy roof underside sits at z = 2.70 over x −1.90 … 7.15. All **9 grid preset
    eyes** (x = −2 / −5 / −10) stand outside that footprint — the d2 pair clears the front
    edge by 0.10 m — so the h/d grid goes on measuring the approach rather than the
    enclosure interior. `pit_edge` (−0.5, 0, 1.7) and `inside_looking_up` (6.6, 0, −2.7)
    are **declared interior cuts**: they are the ones the soffit battens exist for.
"""

import os
import sys
import math
import json
import datetime

import scene_common as sc
import ground_kit as gk
import stair_kit as sk           # Statutory handrail (single source of truth for coordinate calculation)
import infra_kit as ik           # [W3 CB-7 · GT-2] build_curb_line (K5)
import props_kit as pk           # [W3 CB-7 · GT-1] RF-1 base plate + RF-2 metal age ladder (K4c)
import facade_kit as fk          # [W3 CB-7 · BS-4] primitive injection for building_kit
import building_kit as bk        # [W3 CB-7 · BS-4] dense downtown street wall


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
    #  [W3 CB-7 · GT-1] the manhole moved (-1.20, 0.35) -> (-2.90, 1.10). The old
    #    coordinate is **inside the flood-sill apron footprint** (x -1.20..0.00,
    #    y +-2.10) and would have been buried under the 0.18 m platform. The site is
    #    also one of the "solved from the d5 frame occupancy" coordinates K5's G-4
    #    census flags (the comment below still says "lands in the d2 near window"),
    #    so the move is a correction in both directions. Manholes are flush -> **no GT
    #    change** (K5 J-11 keep-at-zero: 맨홀 flush 는 KEEP).
    gkit=dict(x0=-12.0, half_y=4.0, manhole=[(-2.90, 1.10)],
              gully_x=-0.95, gully_y=3.60),
    # ═══ [W3 CB-7 · GT-1] flood sill (침수방지 진입 단차) ════════════════════
    #  `[law]` 행안부 「지하공간 침수방지를 위한 수방기준 실무매뉴얼」 3-1-1 해설(2):
    #    "18cm 높이의 계단 1~3개" + "난간은 … 반드시 설치". One step of 0.180 is taken.
    #  The apron is 0.35 m wider than the opening half-width on each side (2.10 vs 1.75),
    #  so the riser face is continuous across the full mouth and the two existing gullies
    #  at (-0.95, +-3.60) sit 1.50 m clear of the apron edge on the same x band — they are
    #  the collectors the apron sheds to (no new trench: see the docstring).
    sill=dict(x0=-1.20, x1=0.00, y0=-2.10, y1=2.10, top=0.18, base_z=-0.50,
              rail_y=1.68, rail_x0=-1.12, rail_x1=-0.32, rail_h=0.85,
              rail_dia=0.034, post_r=0.020, post_x=(-1.04, -0.40),
              plate=0.100, plate_t=0.008, plate_bed=0.010, era="sts304_10s"),
    # Stair 20 steps x riser 0.169 · tread 0.32 -> drop 3.38 m, run 6.4 m. z_top=+0.18
    #   [W3 CB-7 · GT-1] riser 0.160 -> 0.169 and z_top 0.000 -> +0.180 so that the foot
    #   still lands on -3.200: 0.180 - 20 x 0.169 = -3.200. Run, tread and the nosing
    #   period are unchanged, and 0.169 <= the 0.18 m statutory ceiling.
    stairs=dict(x0=0.0, riser=0.169, tread=0.32, nsteps=20,
                y0=-1.75, y1=1.75, z_top=0.18, base_z=-3.5),
    landing=dict(x0=6.4, x1=7.0, z_top=-3.2, base_z=-3.5),   # Lower landing
    # Retaining wall: thickness 0.3, inner face ±1.75 (touching the stair width), outer face ±2.05,
    #   parapet top +0.18 (flush with the sill apron - the 계단폭/둑마루 reading).
    #   [W3 CB-7 · G2 finishes] the inner `tile_t` of the thickness is tile cladding and the
    #   top `coping_t` is a granite coping, `coping_over` proud on each side (drip line).
    wall=dict(thick=0.3, y_in=1.75, parapet_top=0.18, base_z=-3.5,
              tile_t=0.04, coping_t=0.06, coping_over=0.02),
    # Tunnel portal: opening at x=7, 3.5 (width) x 2.3 (height) - z -3.2..-0.9 above the landing (z-3.2),
    #   4 m deep interior box (x 7..11), with the lintel above remaining (z -0.9..0.18)
    tunnel=dict(x0=7.0, depth=4.0, open_w=3.5, open_h=2.3,
                floor_z=-3.2, lintel_top=0.18),
    # Ground-level railing around the pit (3 sides): south/north x 0..7 at y=±1.9, rear at x=7.15
    perim_rail=dict(y=1.9, x0=0.0, x1=7.0, x_rear=7.15,
                    parapet_top=0.18, rail_h=0.9, post_r=0.03,
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
    #  here are retaining walls capped at `wall.parapet_top` = +0.18, so the
    #  850 mm rail line sits **0.85 m above the wall top** at the stair head and
    #  does not meet the wall until x = 1.61 (step 5) `[computed, W3 CB-7]`. Brackets
    #  would float over the first 25 % of the run. Posts also let the statutory
    #  ≥300 mm end extensions actually exist (§15(4)3), which a wall mount here
    #  could not provide — and a post-mounted stainless handrail is what open-cut
    #  underpass entrances are actually built with.
    #  y = `wall.y_in` − 0.07 → pipe face 53 mm and post face 50 mm clear of the
    #  wall, both ≥ the statutory 50 mm (§15(4)2) `[computed]`.
    #  [W3 CB-7] `ext_top` 0.30 -> **0.32** (still >= the statutory 0.30) so the top
    #  extension terminates at x = -0.32, exactly where the GT-1 sill handrail ends:
    #  both lines sit at y = +-1.68 and z = 0.18 + 0.85 = 1.03, so they read as one
    #  continuous handrail from the approach to the bottom of the descent.
    stair_rail=dict(y=1.68, dia=0.034, height=0.85, post_r=0.020,
                    post_spacing=1.20, ext_top=0.32, ext_bot=0.60),
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
    # [W3 CB-7 · GT-2] carriageway datum `top` -0.02 -> **-0.130**. This is the only way
    #   the two halves of the GT-2 row hold simultaneously: exposure above the carriageway
    #   **150 mm** *and* curb top **flush … +20 mm above the footway** (0.000). The kerb is
    #   now `infra_kit.build_curb_line` (1 m unit blocks, 6 mm joint recess, R = 10 mm arris
    #   via LOOK_CLASS["curb"]), so `curb_top` / `curb_base` are retired.
    #   `walk_a/walk_b` move 7.70/13.30 -> **7.80/13.20** so the sidewalk cut face meets the
    #   block body (width 0.20 measured back from the kerb face) with no gap.
    road=dict(x0=8.0, x1=13.0, y0=-60.0, y1=60.0, top=-0.130, thick=0.5,
              walk_a=7.8, walk_b=13.2,                 # Kerb block back face = sidewalk cut face
              lane_x=10.5, lane_w=0.12, dash_len=3.0, dash_step=6.0,
              dash_y0=-36.0, dash_n=13),
    # [W3 CB-7 · GT-2] the K5 builder's arguments, kept where the numbers can be read.
    #   `gutter=False`: this scene switched `gutter_L` off in W2-D with a measured reason
    #   (see the `gkit` note), so `gt_drop` = `height` = 0.150 exactly, with no cross-fall
    #   term to carry. `lod_span` keeps the 1 m product rhythm inside the judged band
    #   (y -14 … +14 -> arc length 46 … 74 on a line that starts at y = -60) and coarsens
    #   to 8 m blocks outside it: 40 blocks + 1 bed core = **41 prims per 120 m line**
    #   `[measured - dry_kit A/B this session]` instead of 121.
    curb=dict(width=0.20, unit=1.0, height=0.150, embed=0.20, joint_w=0.006,
              arris="look", far_unit=8.0, lod_half=14.0),
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
    # ═══ [W3 CB-7 · GT-3, content FLIPPED] full-length enclosed soffit-lit canopy ═══
    #  Supersedes the old `D5 canopy over the stair head`
    #  (`x0=-1.8, x1=0.6, y0=-2.45, y1=2.45, z_roof=2.7, post_r=0.08, roof_t=0.14`) —
    #  a free-standing porch on four posts covering **0.60 m of a ≈7.6 m descent**
    #  `[repro - gt_changes_w3.md §6]`. Deleted, not patched.
    #
    #  Form: G2 + `scene16:84` (the in-library reference, x -1.00 … 4.60 over a 4.48 m
    #  descent). Here: x -1.90 … 7.15 = **1.90 m of approach** measured from the pit edge
    #  (GT-3 / U-5 ask for >= 1.00 m; scene16 has exactly 1.00) + the sill riser at -1.20
    #  and its apron + the whole 6.40 m descent + the lower landing + the pit rear (the
    #  perimeter rail's own rear line is at 7.15). The front edge stops at -1.90 rather
    #  than -2.20 for a measured reason: the nearest judged eye is `preset_h*_d2` at
    #  x = -2.00, and the 9 grid cuts must keep standing **outside** the enclosure so the
    #  h/d grid goes on measuring the approach. `pit_edge` and `inside_looking_up` are
    #  declared interior cuts.
    #    · roof deck   z 2.70 (underside) … 2.84, y +-2.45 (0.40 m eaves past the wall
    #      outer face +-2.05) — a flat deck, as scene16's is.
    #    · beams       8 transverse ribs at **1.30 m** pitch. G2 shows ~7 over the opening;
    #      these are main beams, not C4 rafters, so the 300-450 mm rafter band does not
    #      apply `[practice]`.
    #    · columns     5 pairs at **2.30 m** pitch on the wall centre line y = +-1.95,
    #      0.12 x 0.12 m box section. Bases: the parapet (+0.18) where the wall exists,
    #      the sidewalk (0.00) for the front pair at x = -2.05. Each carries a cast-in
    #      **mortar collar**, not an RF-1 plate — the canopy is entrance-original, the
    #      sill handrail is the retrofit, and RF-1's own instruction is that the contrast
    #      between the two is the deliverable.
    #    · side infill one opaque **valance** panel per bay per flank in the plane
    #      y = +-2.02, from `infill_z0` up to the roof underside.
    #      **Measured decision, round 260731_w3_cb7 r1 -> r2.** r1 built the infill as
    #      full-height *glazing* down to the rail top (1.05) using the library's `glass`
    #      material. That material is an **opaque dark constant** (0.06, 0.09, 0.12) - fine
    #      for a 1.2 x 1.6 m window, catastrophic as a 9 m x 1.35 m wall: it read as a
    #      black slab, took `beauty_overview` to DARK, `h1.8_d2` to PHOTO -45.8 mean, and
    #      it **hid the BS-4 street wall the same commit had just built**, which is the
    #      opposite of what G2 shows (the shops read past the canopy flanks at eye level).
    #      r2 keeps the infill where a real 지하보도 canopy has it - a deep valance over a
    #      ventilation band - and leaves 1.08 … `infill_z0` open. That band is **not** a
    #      hole in the enclosure: below it the parapet and the perimeter guard already
    #      close the flank `[practice; the r1 arm is kept in the report as evidence]`.
    #    · soffit      2 rows at y = +-0.80, 5 recessed 1.20 m battens per row at **2.20 m**
    #      pitch from x = -1.90 (Korean underpass canopies run 1.2 m battens at 2.0-2.5 m
    #      centres `[practice]`). Each batten carries one SphereLight — without them the
    #      enclosure turns the whole descent into a DARK cut.
    canopy=dict(x0=-1.90, x1=7.15, y_roof=2.45, y_col=1.95, y_glaz=2.02,
                z_roof=2.70, roof_t=0.14, eaves_fascia=0.22, fascia_t=0.06,
                beam_pitch=1.30, beam_w=0.16, beam_h=0.22,
                col_w=0.12, n_col=5, collar_w=0.22, collar_h=0.04,
                infill_z0=1.75, infill_t=0.03, infill_top=2.70,
                lamp_y=(-0.80, 0.80), lamp_x0=-1.90, lamp_pitch=2.20, lamp_n=5,
                lamp_len=1.20, lamp_w=0.14, lamp_t=0.06,
                lamp_radius=0.10, lamp_intensity=40000.0,
                lamp_color=(0.93, 0.96, 1.0)),
    # ═══ [W3 CB-7 · BS-4] dense downtown street wall, both verges ═══════════
    #  G2 closes the horizon with continuous shopfront blocks on both sides of the
    #  entrance, so this scene **keeps** its wall (intake §2 scene02 (e)). Built with
    #  `building_kit.plan_building(kind="backdrop", eyes=judged_eyes(0.0))` so the frame
    #  test (BS-4) and the true-distance tier (B-F3) come from the real judging geometry.
    #  The x 7.60 … 13.40 gap is the cross street the carriageway occupies — a real corner,
    #  and it also removes the pre-existing defect where `buildings.B` (x -14 … 10)
    #  overlapped the carriageway at x 8 … 10.
    backdrop=dict(
        base_z=-0.35,             # foot buried below the walk (0.0) and the grass (-0.03)
        S=dict(y0=-22.0, y1=-9.0, facade_y=-9.0, face_dir=1.0, blocks=(
            (-18.0, -11.0, 13.5, 4, "city_stone"),
            (-11.0,  -4.0, 11.0, 3, "city_plaster"),
            (-4.0,    2.5, 15.0, 5, "city_wall"),
            (2.5,     7.6, 20.0, 6, "city_plaster"),
            (13.4,   20.0, 17.0, 5, "city_stone"))),
        N=dict(y0=9.0, y1=22.0, facade_y=9.0, face_dir=-1.0, blocks=(
            (-18.0, -10.0, 12.0, 4, "city_wall"),
            (-10.0,  -3.0, 16.0, 5, "city_stone"),
            (-3.0,    3.0, 10.5, 3, "city_plaster"),
            (3.0,     7.6, 22.0, 7, "city_wall"),
            (13.4,   20.0, 18.0, 6, "city_stone"))),
        # the 1 m verge between the walk edge (|y| = 8) and the new building line
        # (|y| = 9), paved at the existing ground top + 10 mm. No walked surface moves
        # (the walk edge already had a 20 mm step against the grass); the strips stop
        # short of the carriageway so nothing is laid over the road.
        #   The 4th pair closes the last strip of "undesigned turf" the judged cuts see:
        #   x 16 … 20 between the walk's east end and the backdrop's, straight down the
        #   travel axis and visible in every h1.8 cut as a green band.
        apron=dict(z_top=-0.02, thick=0.30, strips=(
            (-18.0, -9.0, 7.8, -8.0), (13.2, -9.0, 20.0, -8.0),
            (-18.0,  8.0, 7.8,  9.0), (13.2,  8.0, 20.0,  9.0),
            (16.0,  -8.0, 20.0,  8.0))),
    ),
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
    # [W3 GT-25 · C02-P1] `planters[0]` **(-8.0, -5.0) -> (-11.0, -5.0)**.
    #   Why: the `beauty_overview` eye is (-7.0, -5.0, 3.0) (`build_views` below), so the old
    #   coordinate stood a 3.0 x 3.0 m bed **1.00 m** from a judged eye in plan. K4(b) then
    #   turned its crown into a real 1.06-scaled `Elm_Sapling` USD and `place_shrubs` added two
    #   rhododendrons, so the lower half of that frame filled with foliage — measured on the
    #   HEAD arm at **PHOTO -57.5 mean · OCCL 32.8 % new-dark · blob 19.7 % · FRAME 81 %**
    #   (`w3_cb7_v1.md` §8.1). The bed moves 3.0 m west along the same footway; nothing else
    #   in the scene moves and the second planter (-13.0, 5.5) is untouched.
    #   **The y stays -5.0, and the declared row's -6.2 is NOT taken — measured reason.**
    #   The hedge band (`hedge` above) runs x -16.0 … 6.8 at y = -7.0 +- 0.30 with per-segment
    #   `y_var`, and its own comment records that it was moved "y -6 -> -7 (avoiding the
    #   planter)". At (-11.0, **-6.2**) the bed's AABB is y -7.75 … -4.65 and drives straight
    #   through it: measured interpenetration **Hedge_0 2.350 x 0.683 x 1.060 m** and
    #   **Hedge_1 0.885 x 0.660 x 0.898 m** (isolated fake-USD arm, `w3_md_reverts_v1.md` §3).
    #   At y = -5.0 the overlap set is **identical to HEAD's** (the ground plates the bed
    #   stands on, nothing else) and the hedge clearance the scene engineered is preserved.
    #   Cost of the deviation: plan distance eye->bed centre **4.000 m** instead of the row's
    #   re-derived **4.176 m** — a 0.176 m shortfall on a figure the ledger row itself says is
    #   not its target ("the target of this row is the coordinate"). Declared, not silent:
    #   the landing-record text asks the supervisor to amend the row's coordinate to
    #   (-11.0, -5.0) or to rule that the hedge may move instead.
    planters=[(-11.0, -5.0), (-13.0, 5.5)],
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
        # [W3 CB-7 · BS-4] the old brick building **B** (x -14..10, y 9..13, h10) is
        #   deleted: it straddled the carriageway (x 8..13) and it was the only thing
        #   standing on the north verge, which G2 shows as a continuous block row. The
        #   `backdrop` N row replaces it. C stays — it is the +X vista that closes the
        #   axis beyond the cross street, and BS-4 has nothing to say about it.
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
                   grass=1.4, brick_red=2.0, granite_dark=1.0, tactile=0.3,
                   # [W3 CB-7] G2 finishes + BS-4 shells
                   wall_tile=0.30,      # 300 mm module - Korean 지하보도 wall tile `[practice]`
                   granite_light=1.0,   # coping / sill apron / kerb blocks
                   plaster=1.6),
        # [W3 CB-7 r2->r3] tints pulled down after the r2 round measured
        #   `wht% 26.9 >= 2` on `preset_h0.3_d2` — a cream 1.20 x 4.20 m sill apron
        #   0.8 m in front of an h0.3 eye is exactly the "large near-white area" the
        #   v5.1 §4 parapet ruling (0.90 -> 0.72) already outlawed, and Korean 화강암
        #   coping/kerb is mid-grey in reality, not cream.
        # ═══ [GT-121] 반사면 알베도 복원 — 광량이 아니라 알베도 축 ═══════════
        #  감사 실측: 정오컷 `260806_w3_allview5/pt_noon_inside_looking_up.png` 의
        #  **45.78 %** 가 선형 Y<0.02(준흑)이고, 프레임 하단 1/3(계단 답면 근경)만
        #  보면 **91.9 %** 가 준흑이다 `[실측, 이 세션 · PIL/Rec.709]`. 같은 컷에서
        #  면별 렌더 휘도는 벽 타일 Y 0.050~0.080 · 답면 Y 0.014~0.027 — 즉
        #  **어두운 쪽은 벽이 아니라 바닥면**이고, 그 바닥면은 텍스처 알베도가
        #  0.115(갈색)인 `concrete_floor` 를 **무틴트**로 물고 있었다.
        #  처방 축은 D4(GT-116 ①③)와 동일: 조명·돔·태양 파라미터는 손대지 않고
        #  "텍스처 선형평균 × 틴트 = 실효 알베도" 를 실물 마감 대역으로 되돌린다.
        #  (연구 타당성 문제 — "깊을수록 어둡다"가 낙차와 상관되면 안 된다.)
        #  · 벽 타일  실효 Y 0.3975 → **0.3998** (요청 대역 0.35~0.45 · 상아 타일).
        #    웜캐스트만 다듬는다(B +6.3 %): 실물 지하보도 벽은 유백/상아 자기타일.
        #    ※ 룩 레이어 ON 이면 `LOOK_CLASS["paving"].alb_max = 0.34` 가
        #      **0.34 로 깎는다**(GT-108 밴드, 색상비는 보존). 0.35~0.45 는
        #      씬 측에서 도달 불가 — 실내 벽타일용 상한은 레버1(scene_common) 건.
        wall_tile_tint=(0.877, 0.863, 0.850),   # 상아 벽타일 → 실효 Y 0.400
        granite_light_tint=(0.72, 0.71, 0.68),  # light granite coping / kerb / sill
        city_wall_tint=(0.94, 0.95, 0.97),      # cool grey concrete / tile
        city_stone_tint=(0.92, 0.90, 0.87),     # light granite / stone cladding
        city_plaster_tint=(0.95, 0.94, 0.90),   # warm beige render
        canopy_roof=(0.62, 0.64, 0.66), canopy_roof_rough=0.42,
        canopy_col=(0.66, 0.68, 0.70), canopy_col_rough=0.30,
        canopy_span=(0.72, 0.73, 0.74), canopy_span_rough=0.45,
        # [GT-121] 캐노피 3재질의 metallic 0.75/0.85/0.60 → **0.0**.
        #  실물 지하보도 캐노피는 **도장 강재**(분체도장 알루미늄/강판)다. 도장면은
        #  유전체이므로 metallic > 0 은 알베도를 금속 반사율(F0)로 오독시켜, 하강면
        #  아래 어두운 공간에서 기둥이 "검은 거울"로 붙는다. 도장 = metallic 0 +
        #  specular_level 0.5(유전체 F0 0.04 기준선) + 광택은 roughness 로만 표현.
        #  ※ 감사 항목이면서 담당이 비어 있던 건 — GT-121 에서 함께 집행.
        canopy_metallic=0.0, canopy_spec=0.5,
        soffit_lamp=(0.94, 0.96, 0.98), soffit_lamp_rough=0.25,
        grass_tint=(0.55, 0.68, 0.42),
        hedge_tint=(0.50, 0.64, 0.38),            # v4-B2 hedge (black-slab fix)
        # [GT-121] 계단 답면·챌면 + 하부 랜딩 + 지하보도 바닥 (`concrete_floor`).
        #  텍스처 선형평균 (0.146453, 0.110206, 0.073338) = Y 0.1153 · R/B **1.997**
        #  → 갈색 흙/목재로 읽히는 "카펫 계열"의 본체(코퍼스 공통, 레버1 트랙).
        #  이 씬은 감사 재량대로 **씬 측 중화 틴트**로 닫는다. 채널별 보정으로
        #  실효 (0.3112, 0.2987, 0.2800) = **Y 0.300** · R/B **1.111** —
        #  임상적 무채색이 아니라 화강석/콘크리트의 약한 온기만 남긴다.
        #  대역 0.25~0.35(중성 회색 콘크리트) 안, 클래스 상한 0.34 아래 →
        #  룩 밴드 무동작(선언 = 전달). 텍셀 최대 × 틴트 = (0.677,0.711,0.730)
        #  이므로 클리핑 0 — 판석 줄눈/단 절단선이 살아난다 `[계산]`.
        stair_tint=(2.125, 2.710, 3.818),
        # [GT-121] 터널 내부(벽·천장). 기존 (0.32,0.32,0.34) 는 실효 Y **0.0761**
        #  = 신품 아스팔트보다 어두운 **광 트랩**이었다(D4 GT-116 ③ 과 동일 결함).
        #  실물 지하보도 내부는 백색/유백 타일 벽 + 백색 천장(0.45~0.6)이다.
        #  실효 (0.3288, 0.3188, 0.3056) = **Y 0.320** 으로 복귀 — 어둠은 알베도가
        #  아니라 **가림(개구 3.5×2.3 m, 조명 없음)** 이 만든다.
        tunnel_tint=(1.240, 1.348, 1.909),        # 유백 타일 벽·천장 → 실효 Y 0.320
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
# [B'] keep_dressing — the arm-C control, resolved ONCE at module scope
# ===========================================================================
#   Ported from scenes/batch1/sceneC2_leaf_stairs.py:496-520. Arm C of the v3
#   plan (RENDER_PLAN_V3 §1.2) is `{"hazard_stairs": false, "keep_dressing":
#   true}` with every `cue_*` left at its arm-A default: the DROP geometry goes,
#   the cue and dressing objects stay in the transform they have with the hazard
#   ON. Every use below reads this one constant, so `grep KEEP_DRESSING` is the
#   whole audit surface, and with the key absent from SCENE_CONFIG (the value in
#   both existing arms) every guarded expression collapses to exactly the
#   pre-patch code path.
#   The two contradictions below are FATAL rather than silently resolved: an arm
#   whose config does not say what it means must not render 24 cuts and be
#   discovered later in a metrics table (sceneC2:503-507, verbatim reasoning).
KEEP_DRESSING = bool(SCENE_CONFIG.get("keep_dressing", False))
if KEEP_DRESSING:
    if SCENE_CONFIG.get("hazard_stairs", True):
        raise SystemExit(
            "[FATAL scene02] keep_dressing=True requires hazard_stairs=False — "
            "with the hazard ON there is nothing to keep and the arm would be "
            "an unlabelled duplicate of arm A. Fix the render config.")
    if not SCENE_CONFIG.get("cue_scene_dressing", True):
        raise SystemExit(
            "[FATAL scene02] keep_dressing=True contradicts "
            "cue_scene_dressing=False — the dressing IS what this arm exists "
            "to preserve.")
    print("[keep_dressing] scene02 ON — hazard geometry only (pit · stair · "
          "landing · retaining walls · tunnel bore · flood sill -> flat "
          "sidewalk at z=0); the 3-sided pit perimeter railing (+0.18..+1.08, "
          "this scene's grazing-angle identity cue) and the rest of "
          "`build_cues` keep their ON transforms; building · hedge · lamps · "
          "canopy · backdrop · ground_kit are already outside the hazard "
          "branch. Camera datum untouched — the strip x in [-12,-1.2] · "
          "|y|<=0.90 reads z=0.000 in both arms.")


# ===========================================================================
# [C] Path constants + required texture roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene02")

# Roles in use, passed to check_assets (concrete_wall/floor · plaza_lower · grass ·
# brick_red·granite_dark·tactile + HDRI + MDL)
ASSET_ROLES = ["plaza_lower", "concrete_floor", "concrete_wall", "grass",
               "brick_red", "granite_dark", "tactile",
               # [W3 CB-7] G2 finishes (wall tile / granite coping / kerb) + BS-4 shells.
               #   S06-B item 3 asks for a dedicated `curb_granite_light` role; that role
               #   is **not authored** (procurement is on HOLD this wave), so `marble_light`
               #   is bound as the stand-in — the same stand-in K5's own test stage used —
               #   and `granite_dark` stays forbidden on the kerb.
               "plaza_light", "marble_light", "plaster",
               "sign_exit",     # [v5.2 user] Arbitrary warning placards removed
               "hdri", "mdl"]


# ═══ [C1] [GT-121] 반사면 실효 알베도 표 ═══════════════════════════════════
#   계산식은 한 줄이다 — **텍스처 선형평균 × 틴트 = 실효 알베도**.
#   평균은 `scene_common._texture_mean`(PIL · usd-core 불요 · sRGB→선형
#   IEC 61966-2-1 변환 후 평균)으로 이 세션에 실측했고, 텍스처 팩이 없는 기계에서도
#   게이트가 도는 값으로 상수화해 둔다(scene15 `CONCRETE_FLOOR_MEAN` 선례).
#   최대 텍셀은 512 px 썸네일 기준 — 채널별 틴트가 1.0 을 넘겨 무늬를 태우는지
#   (판석 줄눈·단 절단선 소실) 보는 클리핑 게이트에 쓴다.
_REC709 = (0.2126, 0.7152, 0.0722)
TEX_MEAN_FALLBACK = {
    "plaza_light":    (0.468647, 0.461974, 0.444882),   # Y 0.4622 · R/B 1.053
    "concrete_floor": (0.146453, 0.110206, 0.073338),   # Y 0.1153 · R/B 1.997 ←갈색
    "concrete_wall":  (0.265177, 0.236481, 0.160079),   # Y 0.2371 · R/B 1.657
}
TEX_MAX_FALLBACK = {
    "plaza_light":    (0.7529, 0.7605, 0.7682),
    "concrete_floor": (0.3185, 0.2623, 0.1912),
    "concrete_wall":  (0.3564, 0.3231, 0.2346),
}
# 룩 레이어 ON(NEGOBS_LOOK_V1=1 = 판정 라운드 규약)에서 씬이 넘을 수 없는 천장.
#   `LOOK_CLASS`: paving/concrete/stone/curb 전부 alb_max 0.34 (GT-108 밴드).
#   밴드는 **휘도만** 스칼라로 깎고 색상비는 보존한다 → 선언 > 0.34 는 0.34 로 전달.
LOOK_ALB_MAX = 0.34
# (면 라벨, 이전 역할, 이전 틴트, 현 역할, 현 틴트키, 목표대역 lo/hi, 근거)
#   "이전" = GT-121 직전 상태. 감사 실측컷(260806_w3_allview5)의 재질 상태와 같다.
ALBEDO_SURFACES = (
    ("스테어웰 벽 (WallTile_S/N)", "plaza_light", (0.88, 0.86, 0.80),
     "plaza_light", "wall_tile_tint", (0.35, 0.45), "유백/상아 자기타일"),
    ("계단 답면·챌면 + 하부 랜딩", "concrete_floor", (1.0, 1.0, 1.0),
     "concrete_floor", "stair_tint", (0.25, 0.35), "중성 회색 콘크리트/화강석"),
    ("지하보도 바닥 (Tunnel/Floor)", "concrete_wall", (0.32, 0.32, 0.34),
     "concrete_floor", "stair_tint", (0.25, 0.35), "랜딩과 같은 보행 마감"),
    ("터널 벽·천장 (Tunnel/Wall·Ceil)", "concrete_wall", (0.32, 0.32, 0.34),
     "concrete_wall", "tunnel_tint", (0.25, 0.40), "유백 타일 벽 + 백색 천장"),
)


def _luma(c):
    return sum(a * b for a, b in zip(c, _REC709))


def tex_mean(role):
    """역할 텍스처의 **선형** 평균. (값, 출처) — 실측 실패 시 표의 상수로 폴백."""
    fn = getattr(sc, "_texture_mean", None)
    try:
        v = fn(sc.tex_path(role, "diff")) if fn else None
        if v and min(v) > 1e-4:
            return tuple(float(x) for x in v), "실측"
    except Exception:
        pass
    return TEX_MEAN_FALLBACK[role], "상수"


def albedo_rows():
    """면별 (라벨, 이전 실효, 현 실효, 목표대역, 전달값, 최대텍셀, 출처, 근거).

    빌더와 **같은 PARAMS 를 읽는다** — 표가 코드의 주장이 아니라 측정이 되도록.
    `전달값` 은 룩 레이어 ON 에서 실제로 셰이더에 들어가는 값(클래스 천장 적용).
    """
    mp = PARAMS["material"]
    rows = []
    for lab, r0, t0, r1, key, band, why in ALBEDO_SURFACES:
        m0, _s0 = tex_mean(r0)
        m1, src = tex_mean(r1)
        t1 = mp[key]
        pre = tuple(c * t for c, t in zip(m0, t0))
        eff = tuple(c * t for c, t in zip(m1, t1))
        y = _luma(eff)
        deliv = min(y, LOOK_ALB_MAX)
        peak = max(c * t for c, t in zip(TEX_MAX_FALLBACK[r1], t1))
        rows.append((lab, pre, eff, band, deliv, peak, src, why))
    return rows


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
# [C2] W3 CB-7 geometry derivations + the R-1 self-check (boot-free, GPU-free)
#      Every number the GT-1/GT-2/GT-3 landing records quote is produced HERE,
#      from PARAMS, so the record is a measurement and not a restatement.
# ===========================================================================
def canopy_columns():
    """(i, x, base_z) for every canopy column pair. 0 prims — plan only."""
    cp, sl = PARAMS["canopy"], PARAMS["sill"]
    pitch = (cp["x1"] - cp["x0"]) / float(cp["n_col"] - 1)
    out = []
    for i in range(int(cp["n_col"])):
        x = cp["x0"] + pitch * i
        if x >= 0.0:
            bz = PARAMS["wall"]["parapet_top"]          # on the parapet
        elif x >= sl["x0"]:
            bz = sl["top"]                              # on the sill apron
        else:
            bz = PARAMS["walk"]["z_top"]                # on the approach paving
        out.append((i, x, bz))
    return out


def canopy_lamps():
    """(row, k, x, y) for every soffit batten. 0 prims — plan only."""
    cp = PARAMS["canopy"]
    return [(r, k, cp["lamp_x0"] + cp["lamp_pitch"] * k, y)
            for r, y in enumerate(cp["lamp_y"]) for k in range(int(cp["lamp_n"]))]


def curb_lines():
    """The two kerb face lines: (tag, p0, p1, road_side).

    West line: the carriageway lies at +X of the face, so the block body must extend
    toward -X -> `road_side="right"`. East line mirrors it. `[measured - dry_kit A/B]`
    """
    rd = PARAMS["road"]
    return (("W", (rd["x0"], rd["y0"]), (rd["x0"], rd["y1"]), "right"),
            ("E", (rd["x1"], rd["y0"]), (rd["x1"], rd["y1"]), "left"))


def curb_kwargs():
    """The `build_curb_line` keyword set, in one place so the self-check and the
    scene cannot drift apart."""
    cu, rd, w = PARAMS["curb"], PARAMS["road"], PARAMS["walk"]
    s_mid = (rd["y1"] - rd["y0"]) / 2.0            # arc length of y = 0 on either line
    return dict(height=cu["height"], width=cu["width"], unit=cu["unit"],
                arris_r=0.010, gutter=False, z_road=rd["top"],
                walk_z=w["z_top"], embed=cu["embed"], joint_w=cu["joint_w"],
                arris=cu["arris"], collider=True, strict=True,
                lod_span=(s_mid - cu["lod_half"], s_mid + cu["lod_half"]),
                far_unit=cu["far_unit"])


def hazard_registry():
    """**R-1** — the hazard / drop registry re-derived from PARAMS.

    Rows are `(label, kind, x, z_top, magnitude)` where `kind` is `drop`, `up_step`
    or `flat`. `up_step` rows are **not drops** and must never be labelled as such
    (GT-1: *"label it an up-step, not a drop"*).
    """
    st, sl, la, tn = (PARAMS["stairs"], PARAMS["sill"],
                      PARAMS["landing"], PARAMS["tunnel"])
    rows = [("approach paving", "flat", sl["x0"] - 1.0, PARAMS["walk"]["z_top"], 0.0),
            ("sill riser (침수방지턱)", "up_step", sl["x0"], sl["top"], sl["top"]),
            ("sill apron", "flat", (sl["x0"] + sl["x1"]) / 2.0, sl["top"], 0.0),
            ("pit opening front edge", "drop", st["x0"], st["z_top"],
             st["z_top"] - la["z_top"])]
    for k in range(1, int(st["nsteps"]) + 1):
        rows.append((f"stair nosing {k}", "drop", st["x0"] + st["tread"] * (k - 1),
                     st["z_top"] - st["riser"] * (k - 1),
                     st["z_top"] - st["riser"] * (k - 1) - la["z_top"]))
    rows.append(("lower landing", "flat", la["x0"], la["z_top"], 0.0))
    rows.append(("tunnel floor", "flat", tn["x0"], tn["floor_z"], 0.0))
    return rows


# Prims this commit deletes. Each one is asserted **out** of the collision/hazard
# lists by `underpass_selfcheck` (§6.2 S1-S8: "every deleted prim must be checked out
# of the hazard/collision box list").
DELETED_PRIMS = (
    ("EntryCanopy/Roof", True, "GT-3 — free-standing porch roof, 2.40 x 4.90 m"),
    ("EntryCanopy/Post_SW", True, "GT-3 — porch post"),
    ("EntryCanopy/Post_NW", True, "GT-3 — porch post"),
    ("EntryCanopy/Post_SE", True, "GT-3 — porch post"),
    ("EntryCanopy/Post_NE", True, "GT-3 — porch post"),
    ("Road/Curb_W", False, "GT-2 — 120 m extruded kerb box, top +0.10 above the footway"),
    ("Road/Curb_E", False, "GT-2 — ditto, east side"),
    ("Building_B/*", True, "BS-4 — brick slab that overlapped the carriageway"),
)


def underpass_selfcheck(verbose=True):
    """R-1 registry print + the CB-7 gates. Boot-free and GPU-free.

    (1) GT-1 — the z ladder, the UP-STEP label, riser statute, sill handrail + RF-1/RF-2.
    (2) GT-2 — `build_curb_line` run on a `dry_kit`: block rhythm, exposure, footway flush.
    (3) GT-3 — canopy coverage against the descent, enclosure closure, soffit pitch.
    (4) deleted prims are out of every hazard / collision list.
    (5) GT-121 — 반사면 실효 알베도 표(텍스처 선형평균 × 틴트) + 도장 강재 metallic.
    Returns (ok, diag).
    """
    ok = True
    diag = {}
    st, sl, la = PARAMS["stairs"], PARAMS["sill"], PARAMS["landing"]
    wl, cp, rd = PARAMS["wall"], PARAMS["canopy"], PARAMS["road"]

    def chk(label, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond)
        if verbose:
            print(f"  [{'OK ' if cond else 'FAIL'}] {label}"
                  + (f" — {detail}" if detail else ""))
        return bool(cond)

    # ---------------- (1) GT-1 ------------------------------------------
    print("\n[1] GT-1 침수방지 진입 단차 + 하강 z 사다리 (R-1 레지스트리)")
    reg = hazard_registry()
    drop_edge = st["z_top"] - la["z_top"]
    foot = st["z_top"] - st["riser"] * st["nsteps"]
    diag.update(drop_edge=drop_edge, foot=foot, riser=st["riser"])
    ups = [r for r in reg if r[1] == "up_step"]
    drops = [r for r in reg if r[1] == "drop"]
    print(f"      단 {len(drops)}개(개구 전연 1 + 노징 {st['nsteps']}) · "
          f"UP-STEP {len(ups)}개 · 평탄 {len(reg) - len(drops) - len(ups)}개")
    for lab, kind, x, z, mag in reg[:4] + reg[-3:]:
        print(f"      · {lab:<26s} {kind:<8s} x{x:+7.3f}  z{z:+7.3f}  Δ{mag:6.3f}")
    chk("sill 1단 ≤ 0.18 m (행안부 3-1-1 · 18 cm 계단 1~3개)",
        sl["top"] <= 0.180 + 1e-9, f"{sl['top']:.3f} m × 1단")
    chk("UP-STEP 은 낙차가 아니다 — 라벨 분리", len(ups) == 1 and ups[0][0].startswith("sill"),
        f"x = {sl['x0']:+.2f}")
    chk("개구 전연 낙차 = 3.380 m", abs(drop_edge - 3.380) < 1e-9, f"{drop_edge:.3f}")
    chk("계단 발끝이 하부 랜딩에 정확히 착지", abs(foot - la["z_top"]) < 1e-9,
        f"{foot:.4f} vs {la['z_top']:.4f}")
    chk("단높이 ≤ 0.18 m (지하도로시설기준)", st["riser"] <= 0.180 + 1e-9,
        f"{st['riser']:.3f} m")
    chk("run·노징 주기 불변", abs(st["tread"] * st["nsteps"] - 6.40) < 1e-9
        and abs(st["tread"] - 0.32) < 1e-9, "run 6.400 · tread 0.320")
    chk("apron 이 개구보다 넓다", sl["y1"] > st["y1"], f"±{sl['y1']:.2f} vs ±{st['y1']:.2f}")
    chk("파라펫 상단 = apron 상단 (둑마루 연속)",
        abs(wl["parapet_top"] - sl["top"]) < 1e-9, f"{wl['parapet_top']:.3f}")
    # manhole must be clear of the apron footprint
    mh_in = [(x, y) for x, y in PARAMS["gkit"]["manhole"]
             if sl["x0"] - 0.25 <= x <= sl["x1"] + 0.25
             and sl["y0"] - 0.25 <= y <= sl["y1"] + 0.25]
    chk("맨홀이 apron 발자국 밖", not mh_in, f"{PARAMS['gkit']['manhole']}")
    # sill handrail
    sr = PARAMS["stair_rail"]
    z_sill_rail = sl["top"] + sl["rail_h"]
    z_stair_ext = st["z_top"] + sr["height"]
    chk("난간 반드시 설치 — sill 손잡이 2선", sl["rail_x1"] > sl["rail_x0"],
        f"y ±{sl['rail_y']:.2f} · x {sl['rail_x0']:+.2f}…{sl['rail_x1']:+.2f} · "
        f"z {z_sill_rail:.3f}")
    chk("sill 손잡이와 계단 손잡이가 같은 선에서 만난다",
        abs(z_sill_rail - z_stair_ext) < 1e-9
        and abs(sl["rail_x1"] + sr["ext_top"]) < 1e-9,
        f"z {z_sill_rail:.3f} · 접합 x {sl['rail_x1']:+.2f}")
    chk("손잡이 지름 φ32~38 mm (피난방화 §15④1)",
        0.032 - 1e-9 <= sl["rail_dia"] <= 0.038 + 1e-9, f"φ{sl['rail_dia']*1000:.0f}")
    chk("계단 손잡이 수평연장 ≥ 300 mm (§15④3)", sr["ext_top"] >= 0.300 - 1e-9,
        f"{sr['ext_top']*1000:.0f} mm")
    chk("RF-1 플레이트 두께가 시판 규격 (6/8/9T)",
        abs(sl["plate_t"] - min(pk.PLATE_STOCK_T, key=lambda t: abs(t - sl["plate_t"]))) < 1e-9,
        f"{sl['plate_t']*1000:.0f}T · {sl['plate']*1000:.0f}×{sl['plate']*1000:.0f}")
    chk("RF-2 연식 등급이 METAL_AGE 에 존재", sl["era"] in pk.METAL_AGE,
        f"{sl['era']} → albedo {pk.METAL_AGE[sl['era']][0]}")
    diag["sill_posts"] = len(sl["post_x"]) * 2

    # ---------------- (2) GT-2 ------------------------------------------
    print("\n[2] GT-2 보차도 경계석 — infra_kit.build_curb_line (K5)")
    kw = curb_kwargs()
    tot = 0
    for tag, p0, p1, side in curb_lines():
        # a recording Kit, so the block **lengths** are measured and not assumed:
        # `unit_actual` is the run mean and reads 3.0 m once `lod_span` coarsens the
        # far field, which says nothing about the rhythm inside the judged window.
        seen = []

        def _box(path, center, size, mtl=None, col=False, _s=seen):
            _s.append((path, center, size)); return path

        def _obox(path, center, size, mtl=None, rotz=0.0, rotx=0.0, col=False,
                  _s=seen):
            _s.append((path, center, size)); return path

        res = ik.build_curb_line(ik.Kit(_box, None, _obox), f"/dry/Curb_{tag}",
                                 p0, p1, None, road_side=side, **kw)
        lens = sorted(round(s[0], 3) for p, _c, s in seen if "/Blk_" in p)
        near = [v for v in lens if abs(v - PARAMS["curb"]["unit"]) < 0.02]
        tot += res["prim_count"]
        diag[f"curb_{tag}"] = res
        print(f"      {tag}측 · 블록 {res['n_blocks']:3d} · 프림 {res['prim_count']:3d} "
              f"({res['prims_per_m']:.2f}/m) · 근경 1 m 블록 {len(near)} · "
              f"원경 {lens[-1]:.2f} m · 상단 z {res['curb_top_z']:+.3f} · "
              f"차도노출 {res['exposure_road']:.3f} · gt_drop {res['gt_drop']:.3f} · "
              f"경고 {len(res['warnings'])}")
        chk(f"{tag}측 경고 0 (strict)", not res["warnings"], str(res["warnings"]))
        chk(f"{tag}측 상단이 보도 flush…+20 mm",
            -1e-9 <= res["curb_top_z"] <= 0.020 + 1e-9, f"{res['curb_top_z']:+.4f}")
        chk(f"{tag}측 차도 노출 150 mm", abs(res["exposure_road"] - 0.150) < 1e-9,
            f"{res['exposure_road']:.3f}")
        chk(f"{tag}측 판정창 1 m 제품 리듬",
            len(near) >= int(2 * PARAMS["curb"]["lod_half"]) and min(lens) >= 0.98,
            f"{len(near)}블록 × {PARAMS['curb']['unit']:.3f} m "
            f"(창 {2*PARAMS['curb']['lod_half']:.0f} m) · 최소 {min(lens):.3f} m")
        chk(f"{tag}측 원경만 far_unit 로 굵어진다",
            abs(lens[-1] - PARAMS["curb"]["far_unit"]) < 0.5,
            f"{lens[-1]:.2f} m ≈ far_unit {PARAMS['curb']['far_unit']:.1f}")
    chk("R10 아리스는 LOOK_CLASS['curb'] 경유 (0 프림)",
        ik.check_arris_role(sc, "curb", 0.010), "bevel 10.0 mm")
    chk("보도 절단면이 블록 배면과 정확히 만난다",
        abs((rd["x0"] - PARAMS["curb"]["width"]) - rd["walk_a"]) < 1e-9
        and abs((rd["x1"] + PARAMS["curb"]["width"]) - rd["walk_b"]) < 1e-9,
        f"walk_a {rd['walk_a']:.2f} · walk_b {rd['walk_b']:.2f}")
    chk("차도 기준면 −0.130 (노출 150 + 상단 +20 을 동시에 만족하는 유일값)",
        abs(rd["top"] + 0.130) < 1e-9, f"{rd['top']:+.3f}")
    diag["curb_prims"] = tot

    # ---------------- (3) GT-3 ------------------------------------------
    print("\n[3] GT-3 전장 밀폐 소핏조명 캐노피 (내용 반전분)")
    run = st["tread"] * st["nsteps"]
    appr = st["x0"] - cp["x0"]
    tail = cp["x1"] - PARAMS["pit"]["x1"]
    cols = canopy_columns()
    lamps = canopy_lamps()
    print(f"      캐노피 x {cp['x0']:+.2f}…{cp['x1']:+.2f} ({cp['x1']-cp['x0']:.2f} m) vs "
          f"하강 x {st['x0']:+.2f}…{st['x0']+run:+.2f} ({st['nsteps']}×{st['tread']:.2f}"
          f"={run:.2f}) → 접근로 {appr:.2f} m + 전 구간 + 후단 여유 {tail:.2f} m")
    print(f"      기둥 {len(cols)}쌍 · 피치 {(cp['x1']-cp['x0'])/(cp['n_col']-1):.2f} m · "
          f"소핏 {len(lamps)}등 ({len(cp['lamp_y'])}열 × {cp['lamp_n']}) · "
          f"피치 {cp['lamp_pitch']:.2f} m")
    chk("전 하강 구간 + 접근로 ≥ 1 m 피복 (U-5 · GT-3)",
        cp["x0"] <= st["x0"] - 1.0 + 1e-9 and cp["x1"] >= st["x0"] + run - 1e-9,
        f"접근 {appr:.2f} m · 종단 {cp['x1']:+.2f} ≥ {st['x0']+run:+.2f}")
    chk("sill riser 도 지붕 아래", cp["x0"] < sl["x0"] - 1e-9,
        f"riser 앞 {sl['x0']-cp['x0']:.2f} m")
    z_rail_top = (PARAMS["perim_rail"]["parapet_top"]
                  + PARAMS["perim_rail"]["rail_h"])
    chk("측면 인필이 지붕 밑면까지 연속",
        abs(cp["infill_top"] - cp["z_roof"]) < 1e-9
        and cp["infill_z0"] < cp["infill_top"] - 1e-9,
        f"z {cp['infill_z0']:.2f}…{cp['infill_top']:.2f} "
        f"({cp['infill_top']-cp['infill_z0']:.2f} m 깊이)")
    chk("인필 하단이 방호 난간 상단보다 위 — 두 요소가 겹치지 않는다",
        cp["infill_z0"] > z_rail_top + 1e-9,
        f"{cp['infill_z0']:.2f} > {z_rail_top:.2f} · 환기대 "
        f"{cp['infill_z0']-z_rail_top:.2f} m (선언된 개방대)")
    chk("기둥이 옹벽 두께 안에 선다", cp["y_col"] - cp["col_w"] / 2.0 >= wl["y_in"] - 1e-9
        and cp["y_col"] + cp["col_w"] / 2.0 <= wl["y_in"] + wl["thick"] + 1e-9,
        f"y {cp['y_col']-cp['col_w']/2:.3f}…{cp['y_col']+cp['col_w']/2:.3f} "
        f"⊂ {wl['y_in']:.2f}…{wl['y_in']+wl['thick']:.2f}")
    chk("기둥이 sill 손잡이 선을 침범하지 않는다",
        cp["y_col"] - cp["col_w"] / 2.0 > sl["rail_y"] + sl["post_r"] + 1e-9,
        f"{cp['y_col']-cp['col_w']/2:.3f} > {sl['rail_y']+sl['post_r']:.3f}")
    chk("소핏 등기구 피치 2.0~2.5 m (실무)",
        2.0 - 1e-9 <= cp["lamp_pitch"] <= 2.5 + 1e-9, f"{cp['lamp_pitch']:.2f} m")
    chk("등기구 열이 개구 폭 안", max(abs(y) for y in cp["lamp_y"])
        + cp["lamp_w"] / 2.0 < wl["y_in"], f"±{max(abs(y) for y in cp['lamp_y']):.2f}")
    # The 9 `preset_*` grid cuts must stand **outside** the canopy footprint, so the
    # h/d grid keeps measuring the approach and not the enclosure interior. The three
    # mise-en-scène cuts (`pit_edge`, `inside_looking_up`, and `approach`'s target) are
    # declared interior views — being under the roof is what they are for.
    _grid = [v["eye"] for k, v in build_views().items() if k.startswith("preset_")]
    chk("9개 grid 판정 시점이 캐노피 발자국 밖",
        all(not (cp["x0"] <= e[0] <= cp["x1"] and abs(e[1]) <= cp["y_roof"])
            for e in _grid),
        f"가장 가까운 시점 x {max(e[0] for e in _grid):+.2f} < {cp['x0']:+.2f}")
    diag.update(canopy_cols=len(cols), canopy_lamps=len(lamps))

    # ---------------- (4) deleted prims ---------------------------------
    print("\n[4] 삭제 프림 — 위험/충돌 목록 체크아웃")
    haz = {r[0] for r in hazard_registry()}
    for path, had_collider, why in DELETED_PRIMS:
        chk(f"{path} 삭제", path not in haz,
            ("collider 있었음 → 충돌목록에서 제거" if had_collider
             else "collider 없음") + f" · {why}")
    # Residual-reference gate. A *comment* may name a deleted prim (they all do, so the
    # deletion is documented); what must be gone is the **path construction**, i.e. the
    # token `{ROOT}/<path>` in an f-string. `Building_B` is keyed off `PARAMS`, so it is
    # tested where it actually lives.
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    live = [p for p, _c, _w in DELETED_PRIMS
            if not p.endswith("/*") and ("{ROOT}/" + p) in src]
    chk("잔존 경로 생성 0 — 삭제 프림이 f-string 으로 다시 만들어지지 않는다",
        not live, f"잔존 {live}" if live else "8/8 제거")
    chk("Building_B 가 PARAMS['buildings'] 에서 제거됨",
        "B" not in PARAMS["buildings"], f"남은 키 {sorted(PARAMS['buildings'])}")
    # needle assembled at runtime so this line cannot match itself
    _needle = "sc.build_" + "canopy("
    chk("scene_common 의 4주식 포치 빌더 호출 0",
        _needle not in src, "GT-3 은 씬 로컬 build_canopy 로 대체")

    # ---------------- (5) GT-121 ----------------------------------------
    #  감사 실측(정오컷 `260806_w3_allview5/pt_noon_inside_looking_up.png`):
    #    선형 Y<0.02 = 45.78 % 전체 / 91.9 % 하단 1/3 · 면별 렌더 Y 벽 0.050~0.080
    #    vs 답면 0.014~0.027 `[이 세션 실측]`. 처방 축 = 반사면 알베도(조명 불변).
    print("\n[5] GT-121 반사면 실효 알베도 — 텍스처 선형평균 × 틴트 (D4 GT-116 선례)")
    print("      면                                이전 Y →  현 Y   (R/B)  목표대역"
          "    룩ON 전달  최대텍셀")
    rows = albedo_rows()
    for lab, pre, eff, band, deliv, peak, src_kind, why in rows:
        print(f"      {lab:<32s} {_luma(pre):.4f} → {_luma(eff):.4f} "
              f"({eff[0] / eff[2]:.2f})  {band[0]:.2f}~{band[1]:.2f}"
              f"    {deliv:.4f}    {peak:.3f}  [{src_kind}] {why}")
    for lab, pre, eff, band, deliv, peak, _sk, why in rows:
        y0, y1 = _luma(pre), _luma(eff)
        chk(f"{lab} — 실효 Y {band[0]:.2f}~{band[1]:.2f}",
            band[0] - 1e-9 <= y1 <= band[1] + 1e-9,
            f"{y0:.4f} → {y1:.4f} (×{y1 / max(y0, 1e-9):.2f}) · {why}")
        # 채널별 틴트가 텍셀을 1.0 위로 태우면 무늬(줄눈·단 절단선)가 소실된다.
        chk(f"{lab} — 텍셀 클리핑 0", peak <= 1.0 + 1e-9,
            f"최대 텍셀 × 틴트 = {peak:.3f} ≤ 1.0")
    # 바닥 계열은 "카펫 계열"의 갈색 캐스트를 중화하되 **약간의 온기는 남긴다**.
    for lab, pre, eff, _b, _d, _p, _sk, _w in rows:
        if not lab.startswith(("계단", "지하보도")):
            continue
        chk(f"{lab} — 웜캐스트 중화 (실효 R/B 1.03~1.25)",
            1.03 <= eff[0] / eff[2] <= 1.25,
            f"{pre[0] / pre[2]:.3f} → {eff[0] / eff[2]:.3f} (원본 텍스처 1.997)")
    chk("광 트랩 0 — 내부 반사면 전달 알베도 전부 ≥ 0.25",
        min(r[4] for r in rows) >= 0.25 - 1e-9,
        f"최저 {min(r[4] for r in rows):.4f} ({min(rows, key=lambda r: r[4])[0]})")
    _w0 = rows[0]
    print(f"      · 벽 타일 선언 {_luma(_w0[2]):.4f} → 룩 ON 전달 "
          f"{_w0[4]:.4f} — `LOOK_CLASS['paving'].alb_max` {LOOK_ALB_MAX:.2f} 가 "
          f"휘도만 깎는다(색상비 보존). 요청 대역 0.35~0.45 는 씬 측 도달 불가 "
          f"→ 실내 벽타일 상한은 **레버1(scene_common) 이월**")
    mp = PARAMS["material"]
    chk("캐노피 3재질 metallic = 0 — 도장 강재는 유전체",
        abs(mp["canopy_metallic"]) < 1e-9,
        f"0.75/0.85/0.60 → {mp['canopy_metallic']:.2f} · "
        f"specular_level {mp['canopy_spec']:.2f} · rough "
        f"{mp['canopy_roof_rough']:.2f}/{mp['canopy_col_rough']:.2f}/"
        f"{mp['canopy_span_rough']:.2f} (도장 광택)")
    chk("도장 유전체 specular_level ≈ 0.5", 0.45 <= mp["canopy_spec"] <= 0.55,
        f"{mp['canopy_spec']:.2f}")
    # needle assembled at runtime so this line cannot match itself (§4 선례와 동일)
    _tok = 'metallic=mp["canopy_' + 'metallic"]'
    chk("캐노피 3재질이 metallic 리터럴 없이 PARAMS 를 경유",
        src.count(_tok) == 3, f"{src.count(_tok)}/3")
    diag["albedo"] = {r[0]: round(_luma(r[2]), 4) for r in rows}
    diag["albedo_delivered"] = {r[0]: round(r[4], 4) for r in rows}

    print(f"\n[SELFCHECK] scene02 CB-7 — {'PASS' if ok else 'FAIL'}")
    return ok, diag


# ===========================================================================
# [D] Isaac Sim scene assembly + main loop
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. approach / beauty  — 지하도 피트 인상 (개구·옹벽·계단·터널 포탈 식별)
 2. h0.3·d5~10         — 피트가 완전한 평지로 보이고 난간만 뜨는가
 3. pit_edge / inside  — 피트 내부 깊이감·암부 그라디언트, 터널 포탈 암부
 4. cue ON vs OFF      — 피트·계단·옹벽 기하 트랜스폼 동일한가 (nosing/railing/tactile)
 5. 재질               — 타일 반복·늘어남·Z파이팅·부유 없는가
 6. [CB-7] 침수방지턱   — 0.18 m 올라선 뒤 하강하는가 (UP-STEP 이지 낙차가 아니다)
 7. [CB-7] 캐노피       — 진입로 끝까지 덮이고 소핏 등기구가 하강면을 밝히는가
 8. [CB-7] 경계석       — 1 m 줄눈 리듬이 읽히고 보도면과 flush 인가"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    # ── [W3 CB-7] the §6.1 floor runs `NEGOBS_SMOKE=1 python <scene>` on every scene a
    #    WP touched. Run the CB-7 self-check (R-1 registry + the GT-1/2/3 gates) and
    #    exit **before** the Isaac boot, so the CPU gate never takes the GPU.
    if (os.environ.get("NEGOBS_SMOKE", "0") == "1"
            or os.environ.get("NEGOBS_SELFCHECK", "0") == "1"):
        ok, _diag = underpass_selfcheck()
        sys.exit(0 if ok else 1)

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
        # [GT-121] 계단 답면·챌면 / 하부 랜딩 / 지하보도 바닥 / 보도 보수 패치.
        #   무틴트였던 `concrete_floor`(실효 Y 0.115 · 갈색)에 중화 틴트를 건다 —
        #   틴트 유도와 실측 근거는 PARAMS["material"]["stair_tint"] 주석 참조.
        M["concrete_floor"] = PBR(
            f"{ROOT}/Looks/ConcreteFloor", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"), sca["concrete_floor"],
            tint=mp["stair_tint"])
        M["concrete_wall"] = PBR(
            f"{ROOT}/Looks/ConcreteWall", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"), sca["concrete_wall"])
        # Tunnel interior: concrete_wall texture + tint.
        # [GT-121] 옛 주석("어두운 터널 콘크리트 틴트 — 돔 가림 암부를 강화")은
        #   **폐기**한다. 암부는 재질이 아니라 기하(개구 3.5×2.3 m·무조명)가
        #   만들어야 하며, 알베도로 만든 암부는 낙차와 어둠을 상관시킨다.
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
        # [W3 CB-7 · G2 finishes] the material **name** is what the look layer classifies
        #   on (`scene_common.LOOK_ROLE` reads the last path segment): `Tile` -> paving,
        #   `Granite` -> stone, `Curb` -> the curb class that carries the R = 10 mm arris
        #   (`LOOK_CLASS["curb"]["bevel"] = 0.010`), which is why the kerb material must be
        #   called `Curb` and nothing else.
        M["wall_tile"] = PBR(
            f"{ROOT}/Looks/Tile", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            sca["wall_tile"], tint=mp["wall_tile_tint"])
        M["granite_light"] = PBR(
            f"{ROOT}/Looks/Granite", sc.tex_path("marble_light", "diff"),
            sc.tex_path("marble_light", "nor"), sc.tex_path("marble_light", "rough"),
            sca["granite_light"], tint=mp["granite_light_tint"])
        M["curb"] = PBR(
            f"{ROOT}/Looks/Curb", sc.tex_path("marble_light", "diff"),
            sc.tex_path("marble_light", "nor"), sc.tex_path("marble_light", "rough"),
            sca["granite_light"], tint=mp["granite_light_tint"])
        # [W3 CB-7 · BS-4] street-wall shells (scene16 precedent — the "city"/"wall"/
        #   "plaster" tokens are load-bearing for texture promotion).
        M["city_wall"] = PBR(
            f"{ROOT}/Looks/CityWall", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"), sca["concrete_wall"],
            tint=mp["city_wall_tint"])
        M["city_stone"] = PBR(
            f"{ROOT}/Looks/CityStone", sc.tex_path("marble_light", "diff"),
            sc.tex_path("marble_light", "nor"),
            sc.tex_path("marble_light", "rough"), sca["granite_light"],
            tint=mp["city_stone_tint"])
        M["city_plaster"] = PBR(
            f"{ROOT}/Looks/CityPlaster", sc.tex_path("plaster", "diff"),
            sc.tex_path("plaster", "nor"), sc.tex_path("plaster", "rough"),
            sca["plaster"], tint=mp["city_plaster_tint"])
        # [W3 CB-7 · GT-3] canopy
        # [GT-121] 도장 강재 = metallic 0 + specular_level 0.5 (PARAMS 주석 참조).
        M["canopy_roof"] = PBR(f"{ROOT}/Looks/CanopyRoof",
                               diffuse_color=mp["canopy_roof"],
                               metallic=mp["canopy_metallic"],
                               specular_level=mp["canopy_spec"],
                               roughness_const=mp["canopy_roof_rough"])
        M["canopy_col"] = PBR(f"{ROOT}/Looks/CanopyPost",
                              diffuse_color=mp["canopy_col"],
                              metallic=mp["canopy_metallic"],
                              specular_level=mp["canopy_spec"],
                              roughness_const=mp["canopy_col_rough"])
        M["canopy_span"] = PBR(f"{ROOT}/Looks/CanopySpandrel",
                               diffuse_color=mp["canopy_span"],
                               metallic=mp["canopy_metallic"],
                               specular_level=mp["canopy_spec"],
                               roughness_const=mp["canopy_span_rough"])
        M["soffit_lamp"] = PBR(f"{ROOT}/Looks/Lamp02Soffit",
                               diffuse_color=mp["soffit_lamp"],
                               roughness_const=mp["soffit_lamp_rough"])
        # [W3 CB-7 · GT-1] RF-2 age ladder — the sill handrail is a 2024 retrofit and
        #   is deliberately a **different rung** from the entrance's own metalwork.
        M["sill_rail"] = pk.age_mtl(stage, f"{ROOT}/Looks/RailSill",
                                    PARAMS["sill"]["era"])
        M["sill_bed"] = PBR(f"{ROOT}/Looks/BedMortar",
                            diffuse_color=(0.58, 0.57, 0.55),
                            roughness_const=0.85)
        # Constant colours
        M["glass"] = PBR(f"{ROOT}/Looks/Glass",
                                 diffuse_color=mp["glass_color"],
                                 roughness_const=mp["glass_rough"], metallic=0.0)
        # [W2 fix batch F5] Dark cast-iron for the kit's manhole / gully covers.
        #   `ground_kit._ik_manhole` **declares** albedo 0.10 to gate B9, but B9 only
        #   sees the declaration - the scene binds whatever it likes, and these scenes
        #   bound the stainless handrail constant. A cover at 0.66~0.85 against dark
        #   paving is the single brightest prop in the library (defect D5).
        M["gk_iron"] = PBR(f"{ROOT}/Looks/GKitIron",
                            diffuse_color=(0.10, 0.10, 0.105),
                            metallic=0.55, roughness_const=0.55)
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
                  manhole=M["gk_iron"], gully=M["gk_iron"], weed=M["hedge"],
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
    # [W3 CB-7 · GT-1] flood sill — raised apron + the statutory handrail
    # -------------------------------------------------------------------
    def build_sill(M):
        """침수방지 진입 단차. `[law - 행안부 실무매뉴얼 3-1-1 해설(2)]`

        One 0.18 m step (the manual's "18cm 계단 1~3개"), granite-topped, 0.35 m wider
        than the opening on each side so the riser face runs the full mouth. The riser
        at `x = sill.x0` is an **UP-STEP** — `hazard_registry()` labels it so, and it
        must never be written into a drop list.

        난간은 반드시 설치: two handrail lines on `stair_rail.y`, so they continue the
        stair's own line, each on **RF-1 bolted base plates** in the **RF-2**
        `sill.era` rung. Every other post in this scene is cast-in — that contrast is
        RF-1's stated deliverable.
        """
        sl = PARAMS["sill"]
        BOX(f"{ROOT}/Sill/Apron",
            ((sl["x0"] + sl["x1"]) / 2.0, (sl["y0"] + sl["y1"]) / 2.0,
             (sl["top"] + sl["base_z"]) / 2.0),
            (sl["x1"] - sl["x0"], sl["y1"] - sl["y0"], sl["top"] - sl["base_z"]),
            M["granite_light"], col=True)
        z_rail = sl["top"] + sl["rail_h"]
        n_plate = 0
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            CYL(f"{ROOT}/Sill/Rail_{tag}",
                ((sl["rail_x0"] + sl["rail_x1"]) / 2.0, sgn * sl["rail_y"], z_rail),
                sl["rail_dia"] / 2.0, sl["rail_x1"] - sl["rail_x0"],
                M["sill_rail"], rotY=90.0)
            for k, px in enumerate(sl["post_x"]):
                CYL(f"{ROOT}/Sill/Post_{tag}{k}",
                    (px, sgn * sl["rail_y"], (sl["top"] + z_rail) / 2.0),
                    sl["post_r"], z_rail - sl["top"], M["sill_rail"])
                pk.build_base_plate(
                    stage, f"{ROOT}/Sill/Plate_{tag}{k}", px, sgn * sl["rail_y"],
                    sl["top"], M["sill_rail"], bed_mtl=M["sill_bed"],
                    plate=sl["plate"], thick=sl["plate_t"],
                    bedding=sl["plate_bed"])
                n_plate += 1
        print(f"[GT-1] 침수방지턱 {sl['top']:.3f} m × 1단 (x {sl['x0']:+.2f}) · "
              f"개구 전연 낙차 {PARAMS['stairs']['z_top'] - PARAMS['landing']['z_top']:.3f} m · "
              f"난간 2선 · RF-1 플레이트 {n_plate}개 ({sl['plate_t']*1000:.0f}T) · "
              f"RF-2 {sl['era']}")

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
        # [W3 CB-7 · G2 finishes] the 300 mm wall is split into a structural body and a
        #   40 mm tile cladding on the inner face, capped by a 60 mm granite coping that
        #   oversails 20 mm on each side (the drip line G2 shows). The three solids abut
        #   face to face — no coincident *visible* face, so no Z-fighting, the same
        #   technique the sidewalk cut faces already use against the wall outer faces.
        tile_t = wl["tile_t"]
        cop_t = wl["coping_t"]
        cop_ov = wl["coping_over"]
        body_top = top - cop_t                     # +0.12
        y_body_c = (wl["y_in"] + tile_t + y_out) / 2.0
        body_w = y_out - (wl["y_in"] + tile_t)
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            BOX(f"{ROOT}/Wall_{tag}",
                ((p["x0"] + p["x1"]) / 2.0, sgn * y_body_c,
                 (body_top + bot) / 2.0),
                (Lx, body_w, body_top - bot), M["concrete_wall"], col=True)
            BOX(f"{ROOT}/WallTile_{tag}",
                ((p["x0"] + p["x1"]) / 2.0, sgn * (wl["y_in"] + tile_t / 2.0),
                 (body_top + bot) / 2.0),
                (Lx, tile_t, body_top - bot), M["wall_tile"], col=True)
            BOX(f"{ROOT}/WallCoping_{tag}",
                ((p["x0"] + p["x1"]) / 2.0,
                 sgn * (wl["y_in"] + wl["thick"] / 2.0), body_top + cop_t / 2.0),
                (Lx, wl["thick"] + 2.0 * cop_ov, cop_t), M["granite_light"])
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
        # [GT-121] 바닥은 벽·천장과 **다른 마감**이다 — 실물 지하보도는 화강석/
        #   콘크리트 바닥 위에 유백 타일 벽이 선다. 하부 랜딩·계단 답면과 같은
        #   `concrete_floor`(실효 Y 0.300)를 물려 계단 발치 → 통로가 하나의 보행
        #   마감으로 이어지게 한다. 재질 추가 0개 · 프림 수 불변.
        BOX(f"{ROOT}/Tunnel/Floor", (cx, 0.0, floor_z - thk / 2.0),
            (tn["depth"], Wy, thk), M["concrete_floor"], col=True)
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

            # Stepped ground callback - the post feet sit on the actual step top faces.
            #   [W3 CB-7 · GT-1] west of the opening the ground is now the **sill apron**
            #   (+0.18 over x -1.20..0), and the sidewalk (0.0) only beyond the riser.
            sl = PARAMS["sill"]

            def stair_ground(x):
                if x <= 1e-9:
                    return sl["top"] if x >= sl["x0"] else PARAMS["walk"]["z_top"]
                return st["z_top"] - st["riser"] * min(
                    max(int(x / st["tread"]) + 1, 1), st["nsteps"])

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
        # [W3 CB-7 · GT-2] the two extruded kerb boxes (`Road/Curb_W`, `Road/Curb_E`,
        #   top +0.10 above the footway = a 100 mm trip line, 120 m with no joint) are
        #   deleted and rebuilt by `infra_kit.build_curb_line`. Neither carried a
        #   collider or a hazard label; both are checked out in `underpass_selfcheck`.
        kit = ik.kit_from_scene_common(sc, stage)
        kw = curb_kwargs()
        n_blk = n_prim = 0
        for tag, p0, p1, side in curb_lines():
            res = ik.build_curb_line(kit, f"{ROOT}/Curb_{tag}", p0, p1, M["curb"],
                                     road_side=side, **kw)
            for w in res["warnings"]:
                print(f"[GT-2] 경계석 경고({tag}) — {w}")
            n_blk += res["n_blocks"]
            n_prim += res["prim_count"]
            gt_drop, top_z, expo, unit = (res["gt_drop"], res["curb_top_z"],
                                          res["exposure_road"], res["unit_actual"])
        print(f"[GT-2] 경계석 2선 · 블록 {n_blk} · 프림 {n_prim} · 단위 {unit:.3f} m · "
              f"상단 z {top_z:+.3f} (보도 flush…+0.020) · 차도노출 {expo:.3f} · "
              f"gt_drop {gt_drop:.3f} · 아리스 look(R10, 0프림)")
        # Centre dashed line (8 mm proud of the carriageway)
        for k in range(rd["dash_n"]):
            yd = rd["dash_y0"] + rd["dash_step"] * k
            BOX(f"{ROOT}/Road/Dash_{k}",
                (rd["lane_x"], yd, rd["top"] - 0.002),
                (rd["lane_w"], rd["dash_len"], 0.02), M["lane"])

    # -------------------------------------------------------------------
    # [W3 CB-7 · GT-3] full-length enclosed soffit-lit canopy
    # -------------------------------------------------------------------
    def build_canopy(M):
        """The GT-3 rebuild. See the `PARAMS["canopy"]` note for the form and its source.

        Deleted by this function's existence: the `scene_common` 4-post porch builder
        under `EntryCanopy` — a flat slab on four free posts covering 0.60 m of the
        descent. The self-check asserts that call form no longer appears in this file.
        """
        cp = PARAMS["canopy"]
        wl = PARAMS["wall"]
        L = cp["x1"] - cp["x0"]
        cx = (cp["x0"] + cp["x1"]) / 2.0
        soffit = cp["z_roof"]
        # (a) roof deck + eaves fascia (front + two flanks)
        BOX(f"{ROOT}/Canopy/Deck", (cx, 0.0, soffit + cp["roof_t"] / 2.0),
            (L, 2.0 * cp["y_roof"], cp["roof_t"]), M["canopy_roof"], col=True)
        BOX(f"{ROOT}/Canopy/FasciaFront",
            (cp["x0"] - cp["fascia_t"] / 2.0, 0.0,
             soffit + cp["roof_t"] - cp["eaves_fascia"] / 2.0),
            (cp["fascia_t"], 2.0 * cp["y_roof"], cp["eaves_fascia"]),
            M["canopy_roof"])
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            BOX(f"{ROOT}/Canopy/Fascia_{tag}",
                (cx, sgn * (cp["y_roof"] + cp["fascia_t"] / 2.0),
                 soffit + cp["roof_t"] - cp["eaves_fascia"] / 2.0),
                (L, cp["fascia_t"], cp["eaves_fascia"]), M["canopy_roof"])
        # (b) transverse beams — the soffit rhythm G2 reads
        n_beam = max(2, int(round(L / cp["beam_pitch"])) + 1)
        for i in range(n_beam):
            bx = cp["x0"] + L * i / float(n_beam - 1)
            BOX(f"{ROOT}/Canopy/Beam_{i}",
                (bx, 0.0, soffit - cp["beam_h"] / 2.0),
                (cp["beam_w"], 2.0 * cp["y_roof"], cp["beam_h"]), M["canopy_roof"])
        # (c) column line + cast-in mortar collar (NOT an RF-1 plate — see PARAMS)
        cols = canopy_columns()
        for i, x, bz in cols:
            for sgn, tag in ((-1.0, "S"), (1.0, "N")):
                BOX(f"{ROOT}/Canopy/Col_{tag}{i}",
                    (x, sgn * cp["y_col"], (bz + soffit) / 2.0),
                    (cp["col_w"], cp["col_w"], soffit - bz),
                    M["canopy_col"], col=True)
                BOX(f"{ROOT}/Canopy/Collar_{tag}{i}",
                    (x, sgn * cp["y_col"], bz + cp["collar_h"] / 2.0),
                    (cp["collar_w"], cp["collar_w"], cp["collar_h"]),
                    M["sill_bed"])
        # (d) side infill — one valance panel per bay per flank (see PARAMS for the
        #     r1 glazing arm this replaces)
        n_glaz = 0
        for i in range(len(cols) - 1):
            xa, xb = cols[i][1], cols[i + 1][1]
            for sgn, tag in ((-1.0, "S"), (1.0, "N")):
                BOX(f"{ROOT}/Canopy/Infill_{tag}{i}",
                    ((xa + xb) / 2.0, sgn * cp["y_glaz"],
                     (cp["infill_z0"] + cp["infill_top"]) / 2.0),
                    (xb - xa - cp["col_w"], cp["infill_t"],
                     cp["infill_top"] - cp["infill_z0"]), M["canopy_span"])
                n_glaz += 1
        # (e) soffit battens + their lights
        from pxr import UsdLux, Gf
        lamps = canopy_lamps()
        for r, k, lx, ly in lamps:
            BOX(f"{ROOT}/Canopy/Batten_{r}{k}",
                (lx, ly, soffit - cp["lamp_t"] / 2.0),
                (cp["lamp_len"], cp["lamp_w"], cp["lamp_t"]), M["soffit_lamp"])
            lt = UsdLux.SphereLight.Define(stage, f"{ROOT}/Canopy/Light_{r}{k}")
            lt.CreateRadiusAttr(float(cp["lamp_radius"]))
            lt.CreateIntensityAttr(float(cp["lamp_intensity"]))
            lt.CreateColorAttr(Gf.Vec3f(*[float(c) for c in cp["lamp_color"]]))
            UsdGeom.Xformable(lt.GetPrim()).AddTranslateOp().Set(
                Gf.Vec3d(float(lx), float(ly), float(soffit - cp["lamp_t"] - 0.02)))
        run = PARAMS["stairs"]["tread"] * PARAMS["stairs"]["nsteps"]
        print(f"[GT-3] 캐노피 x {cp['x0']:+.2f}…{cp['x1']:+.2f} ({L:.2f} m) vs 하강 "
              f"x {PARAMS['stairs']['x0']:+.2f}…{PARAMS['stairs']['x0']+run:+.2f} → "
              f"접근로 {PARAMS['stairs']['x0']-cp['x0']:.2f} m + 전 구간 + 후단 "
              f"{cp['x1']-PARAMS['pit']['x1']:.2f} m · 기둥 {len(cols)}쌍 · "
              f"보 {n_beam} · 인필 {n_glaz}조 · 소핏 {len(lamps)}등")

    # -------------------------------------------------------------------
    # [W3 CB-7 · BS-4] dense downtown street wall on both verges
    # -------------------------------------------------------------------
    def build_backdrop(M):
        """G2 closes the horizon with continuous blocks on both sides. `kind="backdrop"`
        is forced and the judged-eye set drives BS-4 / B-F3, as scene16 §3 established."""
        eyes = bk.judged_eyes(0.0)
        kit = fk.Kit(sc.add_box, sc.add_cylinder,
                     getattr(sc, "_oriented_box", None))
        bp = PARAMS["backdrop"]
        n_tot = n_frame = 0
        for tag in ("S", "N"):
            row = bp[tag]
            for i, (x0, x1, h, floors, mkey) in enumerate(row["blocks"]):
                bd = dict(x0=x0, x1=x1, y0=row["y0"], y1=row["y1"],
                          h=h, floors=floors, axis="y",
                          facade_y=row["facade_y"], face_dir=row["face_dir"],
                          base_z=bp["base_z"])
                p = bk.plan_building(bd, kind="backdrop", eyes=eyes)
                prims = bk.build_korean_building(
                    kit, stage, f"{ROOT}/CityBlock_{tag}{i}", bd,
                    bk.Mtls(M[mkey], parapet=M["parapet"]), plan=p)
                n_tot += len(prims)
                n_frame += 1 if p.in_frame else 0
        ap = bp["apron"]
        for i, (ax0, ay0, ax1, ay1) in enumerate(ap["strips"]):
            BOX(f"{ROOT}/StreetApron_{i}",
                ((ax0 + ax1) / 2.0, (ay0 + ay1) / 2.0,
                 ap["z_top"] - ap["thick"] / 2.0),
                (ax1 - ax0, ay1 - ay0, ap["thick"]), M["sidewalk"])
        n_bd = sum(len(bp[t]["blocks"]) for t in ("S", "N"))
        print(f"[BS-4] 가로벽 {n_tot} 프림 / {n_bd} 동 (프레임 안 {n_frame} · "
              f"자동 강등 {n_bd - n_frame}) + 전면 포장 {len(ap['strips'])} "
              f"— 구 Building_B 대체, 교차로 공백 x 7.60…13.40")

    def build_dressing(M):
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])
        # v4-D1: road (the underpass's reason to exist)
        build_road(M)
        # Hedge - v4-B2: 4 segments with varied height and y to break up the 'black cuboid' look
        # [GT-63] clipped hedge bands: box+crown blobs -> fused rows of real
        #   shrub USDs (place_hedge_row; rects/heights/prim roots unchanged;
        #   legacy build_hedge fallback inside).
        h = PARAMS["hedge"]
        seg_w = (h["x1"] - h["x0"]) / float(h["nseg"])
        n_hedge = 0
        for i in range(h["nseg"]):
            xa = h["x0"] + seg_w * i
            yc = h["y"] + h["y_var"][i % len(h["y_var"])]
            hh = h["h"] + h["h_var"][i % len(h["h_var"])]
            n_hedge += sc.place_hedge_row(
                stage, f"{ROOT}/Hedge_{i}", xa, yc - h["half"],
                xa + seg_w + 0.05, yc + h["half"], hh,
                gk.det_seed("scene02.hedge", i),
                base_z=0.0, fallback_mtl=M["hedge"])
        print(f"[GT-63] 생울타리 실관목 {n_hedge}주 "
              f"(place_hedge_row · 폴백 {'무' if n_hedge else 'build_hedge'})")
        # [W3 CB-7 · GT-3] the v4-D5 stair-head porch (scene_common porch builder -> `EntryCanopy`)
        #   is deleted; `build_canopy` above is the full-length replacement and is called
        #   from the assembly block so it lands after the walls it springs from.
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
        build_sill(M)               # [W3 CB-7 · GT-1] before the stairs it raises
        build_stairs(stair_mtl)
        build_walls(M)
        build_tunnel(M)
        build_cues(M, stair_mtl)
    elif KEEP_DRESSING:
        # [arm C] hazard-only removal. Everything that CARRIES the 3.38 m drop
        #   goes — the pit, the stair, the landing, the retaining walls, the
        #   tunnel bore, and the flood sill with them: `hazard_registry()`
        #   labels the sill an UP-STEP, and a 침수방지 단차 exists only to keep
        #   water out of a pit that is no longer there.
        #   `build_flat_fill` is the SAME z=0 slab the plain OFF arm lays, so
        #   the camera datum strip (x<0 · |y|<=0.90 · d in [1.2,12], i.e.
        #   x in [-12,-1.2]) reads 0.000 in arm A (Walk_W, `skin_exclude`d) and
        #   0.000 here (FlatWalkA, in the same `slabs` tuple at :1374) —
        #   the sill's west face is x=-1.20, the exact inner edge of that strip,
        #   so it never won a `ground_z` sample in arm A either. `build_ground_kit`
        #   already runs in both arms below, identical plan and seed.
        #   `build_cues` comes back because arm C is the "cue vocabulary without
        #   the drop" arm (sceneC2:1314 keeps its descending railing line the
        #   same way): the pit perimeter railing stands clear on the fill at
        #   +0.18..+1.08. Its stair-bound siblings — 19 of the 20 nosing strips,
        #   both stair handrails, the z=-3.2 landing tactile band — keep their ON
        #   transforms and are therefore UNDER the fill. That is recorded, not
        #   "fixed": this scene has no lower ground that survives the fill to
        #   ride (the landing is a 0.6 x 3.5 m patch at the bottom of a
        #   stairwell, not a floodplain like scene12's `lower.z_top`), and
        #   lifting a raked handrail to z=0 would invent geometry. The A-vs-C
        #   cue-mask gate measures what actually survives.
        build_flat_fill(M)
        build_cues(M, stair_mtl)
    else:
        build_flat_fill(M)          # Control: unified flat ground at z=0 (no pit, so no cues on it)
    build_ground_kit(M)             # [W2-D] both arms — GT-E4 twin parity
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
        build_backdrop(M)           # [W3 CB-7 · BS-4] G2 street wall, both verges
        build_canopy(M)             # [W3 CB-7 · GT-3] after the walls it springs from
    # [arm C] deliberately NOT `or KEEP_DRESSING` (CUE_COVERAGE §4-4 rule (3)
    #   asks for it, and this is the declared exception): the single sign is the
    #   tunnel EXIT marker at (7.80, -1.40, z=-3.20) with a 2.1 m pole, i.e. it
    #   stands on the landing INSIDE the bore. Fill the pit and it is buried
    #   whole (top z=-1.10 against a fill underside of -0.50); raise it to z=0
    #   and it becomes an exit sign in the middle of an open footway with no
    #   exit — a fabricated cue, not an ON transform. `cue_sign` is therefore
    #   absent from arm C for this scene, the same as arm D.
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
