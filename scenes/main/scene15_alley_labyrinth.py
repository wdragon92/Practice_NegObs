# -*- coding: utf-8 -*-
"""
scene15_alley_labyrinth.py — NegObs synthetic scene 15: Gamcheon/Alfama-type alley stair (Isaac Sim 4.5)

Type    : T15 alley labyrinth (wall-compressed perspective × drop hidden by a narrow field of view)
Spec    : Docs/multi_scene_brief_v3.md §D scene15_alley_labyrinth
Shared  : scene_common.py (verified API helpers) · scene02_underpass.py (urban skeleton)

Hazard  : a 1.2 m wide concrete stair descends between pastel houses on both flanks. The walls
           crowd to within 0.3 m of the stair and compress the field of view, and the lower
           alley vanishes behind the mid-descent bend (rot_group 25°) — a total drop of 4.25 m
           is concealed inside a narrow frame.
Goal     : assemble 25 steps (25° bend after 12 steps + a 1.5 m landing) + 12 pastel houses on
           both flanks (inset windows·doors, roof overhang) + the lower alley (no dead-end wall);
           render and judge.

[v5.1 realism] User verdict: "drop the sculptural objects — it only got less natural".
  Rooftop water tanks·satellite dishes (+brackets)·meter boxes·clotheslines/laundry·utility
  poles·wires are **removed entirely**; the traces of daily life left are 5 flower pots +
  2 AC outdoor units + the skirting band. Alley floor·stair·house body geometry is unchanged
  (0 transform edits). The pastel palette is lowered to a max channel ≤0.80 to meet the
  no-large-pure-white convention, and facades·roofs get a per-instance ±5 % tint jitter.

[realism v1 · railing] The scene carried a **code-standard freestanding guardrail**
  (top + mid rail, posts @1.1 m, balusters @0.116 m, plus the LOOK_GEO handrail —
  3 rail lines × 3 flights = 116 prims) standing at y=0.55, i.e. **10 mm off a
  house facade at y=0.58**. A statutory fall barrier bolted onto a wall it does
  not need to protect, eating half of a 1.2 m alley stair — the single most
  artificial object in the scene.
  Korean hillside alley stairs do not build that. A 12-photo tally (report §1)
  found **0/12** two-sided code guardrails and **0/12** stairs railed on both
  flanks; 1/12 had no rail at all and the rest carried a single minimal pipe on
  slim posts, always one-sided or down the centre. And the NONE bucket is
  under-counted — the ordinary-alley photos came from stair-retrofit news
  coverage, which structurally over-samples stairs that just received a rail.
  Two things settle it for this geometry:
    · The corridor is walled on **both** sides for the whole descent, so the
      walls carry the guard (evac/fire §15(1)2 admits a "wall" in place of a
      railing — the same reading that passed scene05's arc stair on its cheek
      walls, Docs/reports/stair_compliance_v1.md §1).
    · §15(3) then states the matching rule outright: "where there are walls or the
      like on both sides and therefore no railing, a handrail shall be installed" —
      a both-sides-walled stair takes a **handrail**, not a guardrail. The old
      geometry was the wrong part.
  Redesign: guardrail deleted (116 prims → 0). `cue_railing` defaults **False**
  (bare stair, walls guard); ON builds one wall-bracketed φ34 pipe handrail over
  the upper flight + landing only, and the lower flight past the 25° bend stays
  bare either way.
  Rationale, photo tally and self-check: Docs/reports/scene15_railing_fix_v1.md.
  GT invariant — rails create no terrain z, so the drop label is untouched.

Run (GUI look check — default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene15_alley_labyrinth.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python scene15_alley_labyrinth.py
Smoke early exit:         NEGOBS_SMOKE=1  python scene15_alley_labyrinth.py

Coordinates: Z-up, m, travel axis +X (first flight), drop start edge = x=0.
"""

import os
import sys
import math
import json
import random
import datetime

import scene_common as sc
import ground_kit as gk
import stair_kit as sk       # [realism v1] wall-mounted handrail (§15(4))


# ===========================================================================
# [A] SCENE_CONFIG - standard 7 keys. Only hazard_stairs is a geometry toggle (False->flat alley).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False -> stair·bend removed, the upper alley extends flat at z=0
    # [realism v1] **Default flipped True → False**, and the semantics changed:
    #   this key no longer builds a *guardrail* at all. OFF = bare stair, the
    #   flanking walls carry the guard function (evac/fire §15(1)2 "wall"). ON =
    #   one wall-bracketed φ34 pipe **handrail** (§15(4)) over the upper flight
    #   and landing — never a guardrail, and never on both flanks.
    #   Why OFF is the default `[survey N=12, report §1]`: 0/12 photographed
    #   Korean hillside alley stairs carry a two-sided code guardrail, 0/12 rail
    #   both flanks at once, and the "no rail at all" bucket is under-counted
    #   because the ordinary-alley sample came from stair-retrofit news coverage
    #   (Busan Ilbo, of a 147-location retrofit programme: "there are still many
    #   alleys with no stair handrail"). For an un-renovated hillside-slum maze, bare is the modal
    #   state. Ledger: scene15 leaves the "has railing" column — report §4.
    "cue_railing":        False,  # no railing (guard = the flanking walls). True -> 1 wall-mounted pipe on the north side
    "cue_tactile":        False,  # old alley - tactile paving is not the practice (key reserved)
    "cue_material_break": True,   # False -> the stair takes the alley floor material
    "cue_nosing":         False,  # painted nosing is not the practice (key reserved)
    "cue_sign":           False,  # [optional] not implemented - config key reserved only
    "cue_scene_dressing": True,   # flanking houses·overhead wires·lower alley vanishing, all together
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # flight1, 12 steps (x0=0, z 0->-2.04), width 1.2
    flight1=dict(x0=0.0, riser=0.17, tread=0.30, nsteps=12,
                 y0=-0.6, y1=0.6, z_top=0.0, base_z=-6.0),
    # landing 1.5 m (x 3.6..5.1, z=-2.04)
    landing=dict(x0=3.6, x1=5.1, z_top=-2.04, base_z=-6.0),
    # flight2, 13 steps, bent by rot_group(pivot (5.1,0), 25 deg) (x0=5.1, z -2.04->-4.25)
    flight2=dict(x0=5.1, riser=0.17, tread=0.30, nsteps=13,
                 y0=-0.6, y1=0.6, z_top=-2.04, base_z=-6.0),
    bend=dict(pivot=(5.1, 0.0), deg=25.0),
    # lower alley: continues in +X from the end of flight2 (x~9.0, z~-4.25) and vanishes (inside rot_group)
    lower_alley=dict(x0=9.0, x1=20.0, y0=-0.9, y1=0.9, z_top=-4.25, base_z=-6.0),
    # ═══ [realism v1] Railing — freestanding guardrail → wall-mounted pipe ═══
    #  Old: `y_side=0.55, rail_h=0.92, post_r=0.02, rail_r=0.026,
    #        rail_mid_r=0.02, rail_mid_drop=0.46, spacing=1.1` on THREE lines
    #        (flight1 · landing · flight2). Under LOOK_GEO each line also grew
    #        balusters @0.116 and a second, coaxial `stair_kit.build_handrail`
    #        post line — 116 prims, 21 % of the scene, all of it inside the
    #        30 mm slot between y=0.55 and the facade at y=0.58 `[measured]`.
    #  New: nothing by default; one pipe **bracketed to the wall** when
    #        `cue_railing` is ON. The wall-bracket form is what §15(3)
    #        prescribes for a both-sides-walled stair, but note the honest gap:
    #        the photo sample found **0/12** wall-bracketed pipes in alleys
    #        (report §1.2) — field retrofits use slim posts, plausibly because
    #        the flanking walls are private property. The highest-fidelity
    #        alternative for exactly this geometry is a **single centre pipe**
    #        (survey S10/S11, Choryang 180-stairs: walls both sides, one pipe
    #        down the middle). Rejected here because a post line on the y=0
    #        camera axis would sit in the centre of every h0.3 grazing frame
    #        and is a live GRAZE-regression risk in a 1.2 m corridor.
    #        Reversible — logged for the v2 read-through (report §6).
    rail=dict(
        wall_y=0.58,            # north house facade plane (House[4]/[5], face=-1)
        wall_side=-1.0,         # the corridor is on the y < wall_y side
        dia=0.034,              # φ34 — inside the statutory φ32~38 (§15(4)1)
        height=0.85,            # 850 mm above the nosing line (§15(4)2)
        wall_gap=0.050,         # 50 mm clear of the wall face (§15(4)2)
        bracket_r=0.011, bracket_spacing=1.20,
        # Top end extension 0. The flanking wall itself only starts at x=0 (the
        #   drop edge: House[4] spans x 0..2.8), so there is no wall to bracket
        #   to before it — the pipe physically cannot extend. Statutory minimum
        #   is 300 mm (§15(4)3), so this is a deliberate **H3 shortfall**, i.e.
        #   the "sub-code reality" this project studies. Bottom end runs 1.5 m
        #   over the landing (x 3.6..5.1, wall continues on House[5]) → H3 met.
        ext_top=0.0, ext_bot=1.50,
        # Lower flight (past the 25° bend, inside the rot_group) gets **no**
        #   rail by default: the piecemeal resident-installed pipe stops at the
        #   landing. The walls (House[8]/[10] facades at local y=±0.58) still
        #   guard it, and leaving the bend uncued is the scene's research
        #   identity — the 2.21 m that the bend hides carries no cue at all.
        lower_flight=False,
    ),

    # upper alley flat (x -12..0, z=0)
    upper_alley=dict(x0=-12.0, x1=0.0, y0=-0.9, y1=0.9, z_top=0.0, base_z=-6.0),

    # ═══ [W2 ground_kit] P5 alley_concrete - 0 elements -> full fill (spec §5.4) ═══
    #  the scene with the largest gap vs the photo sample. 8 elements pass in one go:
    #   15-1 transverse construction joints step 3.0·width 0.010·recess 3 mm  (x=0 dropped per the edge exclusion)
    #   15-2 manhole φ0.648  * **director approved M9-(b) - relocated to the d5 window**
    #        (the old x=−1.15 gave a screen width of 1,268 px at d2 = 66.0 % of the frame,
    #         one element monopolising the near window `[computed - W_px=f·0.648/0.85]`. At the
    #         d5 window x=−4.0 it is 280 px = 14.6 %, normal. B1 of the d2 window is filled by one 15-4 patch.)
    #   15-3 wall-side U gutter (covered) y=−0.75 · 15-4 2 repair patches
    #   15-5 wall-floor grime band · 15-6 grating at the stair foot (bend group local)
    #   15-7 3~5 cracks · 15-8 6~10 weeds (auto-clamped near the edge by the GT-E5 ramp)
    #  forbidden: plain bare soil (0/12 in the sample) · fallen leaves · **tactile paving** (§12 - p~0.05, not installed)
    ground=dict(
        region=(-12.0, -0.9, 0.0, 0.9),
        #  15-2 manhole - **2nd correction** of the M9-(b) relocation (old −1.15).
        #  * [W2 pre-check] at d5 the −4.00 position is only X=1.00 m of ground distance, so
        #    the screen width was f·0.648/1.00 = **1,078 px = 56.1 %** `[computed - red team G-2]`.
        #    M9's intent was "break the near-window monopoly", and 66 % (old) -> 56 % (new) is
        #    not a fix. Worse, **<=25 % is impossible in principle anywhere inside W1**
        #    (ground distance 0.564~2.00 m) - even at the far end X=2.00 it is 539 px = 28.1 %.
        #    -> moved out to the second-priority window **W2 (2.00~3.00 m)**. x=−2.40 gives
        #    X=2.60 m · **414 px = 21.6 %** at d5 `[computed]`. At d2 it is behind the eye
        #    (X=−0.40) hence invisible -> patch #1(x=−1.20) keeps covering the d2 window as designed.
        #    At d10 it is X=7.60 · 142 px = 7.4 %.
        #  interference check `[computed]`: radius 0.324 -> x[−2.724,−2.076]·y[−0.474,0.174].
        #    outside joint JX_3(x=−3.00) · outside patch#1(x −1.557…−0.843) ·
        #    outside the U gutter (y −0.875…−0.625) · outside the grime band (|y|>=0.75) -> 0 Z-fighting.
        manhole_d5=(-2.40, -0.15),
        #  the first one covers B1·B2 of the d2 window (W1 = x −1.436…0). At x=−1.20 the
        #  screen width is 1,663 px (86.6 %) - unlike the old manhole (1,268 px) this is a
        #  **flat tone change**, so the visual burden of the near-window monopoly is far smaller.
        patch_sites=[(-1.20, 0.10), (-7.60, -0.30)],
        gutter_y=-0.75,
        grating_local=(9.30, -0.90, 0.90),         # bend rot_group local
        grating_z=-4.25,
    ),
    # upper alley retaining wall (A-15-3 critical): the old structure had no house or
    #   retaining wall flanking x −12..−0.5 - a 1.8 m wide ridge with a 4.35 m cliff down
    #   to the valley (−4.35). Both flanks are closed by a retaining wall of top z=1.2, with 4 houses seated behind it.
    retwall=dict(x0=-12.0, x1=0.0, y_in=0.9, y_out=1.4, z_top=1.2),
    # landing<->bend −Y wedge seal (A-15-4): between the landing front edge (straight x=5.1)
    #   and the west edge of flight2's first step, rotated 25 deg ((4.846,0.544)->(5.354,−0.544)),
    #   a triangular opening up to 0.254 m. Filled with a top face 5 mm below the first step top (−2.21).
    wedge=dict(x0=5.05, x1=5.42, y0=-0.66, y1=0.05, z_top=-2.215, base_z=-6.0),
    # valley (lower) ground slab - fills the hill slope (no cavity)
    valley=dict(size=90.0, z_top=-4.35),

    # 12 flanking houses (cycling 5 pastel colours). base_z steps down with the descending stair.
    #  face_dir: which facade faces the alley (+1=+Y face, -1=-Y face).
    #  grp=True : **local coordinates inside the bend rot_group (pivot (5.1,0), +25 deg)**.
    #    [answers A-15-1/2 critical] the old House[2]/[3] (world axis-aligned) fully occluded
    #    the 25 deg-rotated flight2 and lower alley. Pushing them out per the audit proposal
    #    (cy 3.6/5.0) would strip the alley bare, so instead both were **moved into the rotation
    #    group** to flank the bent alley at local y=+-0.58 (flight2) / +-0.88 (lower alley) -> 0
    #    occlusion, the alley-corridor identity kept, centreline offset = the alley half-width unchanged.
    #  life=True : [v5.1] only 1 AC outdoor unit attached (meter box·water tank·satellite dish dropped).
    #    Given only to the two houses actually visible from the alley (north of flight1 · north of the bend).
    #    The skirting band is a paint trace, so every house keeps it (it is not a prop).
    houses=[
        # upper alley (behind the retaining wall, z=0 level)
        dict(cx=-2.6, cy=2.58, base_z=0.0, w=3.2, d=2.4, h=3.0, tint=4, face=-1),
        dict(cx=-2.6, cy=-2.58, base_z=0.0, w=3.2, d=2.4, h=2.6, tint=1, face=1),
        dict(cx=-6.6, cy=2.58, base_z=0.0, w=3.4, d=2.4, h=2.7, tint=3, face=-1),
        dict(cx=-6.6, cy=-2.58, base_z=0.0, w=3.4, d=2.4, h=3.2, tint=0, face=1),
        # flight1·landing (world axis-aligned). Facades at y=+-0.58/+-0.55 bite 0.02~0.05 into
        #   the stair flanks (+-0.6), removing the old 0.10 m crevasse (A-15-6).
        dict(cx=1.40, cy=1.78, base_z=-0.2, w=2.8, d=2.4, h=4.2, tint=0, face=-1,
             life=True),
        dict(cx=3.95, cy=1.78, base_z=-1.9, w=2.3, d=2.4, h=3.6, tint=1, face=-1),
        # the south (y−) houses are low, 2.5~3 m, to keep sun in the alley (director r1 C-15(3), as at Gamcheon)
        dict(cx=1.40, cy=-1.78, base_z=-0.2, w=2.8, d=2.4, h=2.8, tint=2, face=1),
        # the house beside the south landing extends to x1=5.45, closing the 0.29 m gap to the
        #   outer bend corner (House[10] west end, world X=5.390). The facade (−0.58) lies outside
        #   the flight2 −Y edge (Y=−0.499 at X=5.45), so there is no corridor intrusion.
        dict(cx=4.125, cy=-1.78, base_z=-1.9, w=2.65, d=2.4, h=3.0, tint=3,
             face=1),
        # bend group local (flight2 local x 5.1..9.0 / lower alley 9.0..20)
        dict(cx=7.075, cy=1.88, base_z=-3.6, w=3.85, d=2.6, h=4.6, tint=2,
             face=-1, grp=True, life=True),
        dict(cx=11.05, cy=2.18, base_z=-4.25, w=4.1, d=2.6, h=3.8, tint=3,
             face=-1, grp=True),
        dict(cx=7.075, cy=-1.88, base_z=-3.6, w=3.85, d=2.6, h=2.7, tint=4,
             face=1, grp=True),
        dict(cx=11.05, cy=-2.18, base_z=-4.25, w=4.1, d=2.6, h=2.9, tint=0,
             face=1, grp=True),
    ],
    # opposite hill backdrop (distant horizon closure, the slope across the valley - not a dead-end wall)
    backdrop=[
        dict(cx=24.0, cy=8.0, base_z=-1.5, w=4.5, d=4.0, h=5.0, tint=1, face=-1),
        dict(cx=28.0, cy=2.0, base_z=-0.5, w=4.5, d=4.0, h=4.5, tint=3, face=-1),
        dict(cx=26.0, cy=-6.0, base_z=-2.5, w=4.5, d=4.0, h=5.5, tint=0, face=1),
        dict(cx=31.0, cy=-1.0, base_z=0.5, w=5.0, d=4.5, h=4.8, tint=4, face=1),
    ],
    # [v5 judgment applied] roof_over 0.25 -> 0.14 : at the 25 deg bend the eaves of the world
    #   axis-aligned houses (House 5/7) and the rotation-group houses (House 8/10) crossed at
    #   different z (1.88·1.28·1.18·−0.72), making 'floating white plate' slivers above the
    #   corridor. Shrinking the overhang removes them (house body transforms unchanged).
    house=dict(win_w=0.7, win_h=1.0, door_w=0.9, door_h=1.9, inset=0.06,
               roof_over=0.14, roof_t=0.18),
    # [v5.1 realism · removal] 2 utility poles + 2 wires dropped.
    #   Rationale: poleA(2.0, −0.48, r0.11)·poleB(10.5, 0.72) stood **inside** the stair
    #   corridor (y +-0.6) and the lower alley (y +-0.9) respectively, piercing the walkway.
    #   Real alley poles stand on the retaining-wall·fence line, never mid-pavement.
    #   Per the "remove it if it looks wrong" instruction, poles and wires are all deleted
    #   (relocating them would cross the facades·roof overhangs again, so keeping them gains nothing).
    # traces of daily life - cut down to 5 flower pots: (x, y, z, grp).
    #   y=+-0.40 (stair half-width 0.6, pot r 0.20 -> never reaches the facade at 0.58).
    #   6 evenly spaced pairs would read as a 'display', so they are left asymmetric, one side at a time.
    pots=[(0.9, 0.40, -0.68, False), (2.1, -0.40, -1.36, False),
          (4.2, 0.40, -2.04, False), (6.4, 0.40, -2.89, True),
          (10.5, -0.68, -4.25, True)],
    pot=dict(r=0.20, h=0.34, leaf_r=0.19),   # [v5 judgment applied] leaf_r 0.26 -> 0.19
    # [v5.1 realism · removal] 3 clotheslines + 9 hanging garments dropped - they read as
    #   floating slabs strung above the alley and contributed nothing to reading the narrow corridor (drop concealment).

    material=dict(
        # [v5 judgment applied] retwall=3.5 added - the retaining wall is separated by texture
        #   scale from both the pavement (concrete_floor, scale 1.0) and the house plaster (plaster, scale 2.0).
        scale=dict(plaza_lower=0.7, concrete_floor=1.0, plaster=2.0,
                   retwall=3.5),
        # 5 pastel colours (brief §D scene15).
        # [v5.1 realism] global convention "no large pure-white (>0.8) areas" - the facades are
        #   the widest surfaces in this scene, so 0.90~0.95 channels blew out to white plates in noon light.
        #   Hue is kept and everything is dimmed to a max channel <=0.80 (about x0.86).
        pastel=[(0.78, 0.65, 0.60), (0.65, 0.73, 0.78), (0.80, 0.76, 0.60),
                (0.69, 0.77, 0.65), (0.77, 0.69, 0.77)],
        # [v5.1] per-instance tint jitter amplitude (+-5 %) - shared by facade·roof
        tint_jitter=0.05,
        roof_tints=[(0.55, 0.31, 0.22), (0.42, 0.42, 0.44)],  # orange·grey
        # B-15-1 [critical]: 0.60 pure white clipped in noon light and the tread/riser boundary
        #   was lost entirely (the drop label lost its visual evidence). Changed to 0.20 neutral concrete.
        stair_color=(0.20, 0.20, 0.19), stair_rough=0.82,
        # [v5 judgment applied · critical] the 2 retaining-wall rows reused M["alley"] (pavement
        #   concrete_floor) as-is, so every h0.3/h0.9 preset became a context-free corridor of
        #   'brown plates left and right + a floor of the same material'. The dedicated retaining-wall
        #   material = plaster texture + blue-grey stonework tint (0.28 band, judgment recommends
        #   0.10~0.35) + scale 3.5, separated in value·hue·texture scale from the pastel facades (0.75~0.95) and the pavement.
        retwall_tint=(0.30, 0.29, 0.27), retwall_rough=0.88,
        # [v5 judgment applied] the pot foliage used M["roof"][1] (0.45,0.45,0.47 grey) and
        #   rendered as a white blob in noon light -> dedicated deep-green constant colour + smaller radius.
        foliage_color=(0.13, 0.22, 0.11), foliage_rough=0.80,
        window_color=(0.05, 0.06, 0.08), window_rough=0.2,    # dark glass
        frame_color=(0.72, 0.70, 0.66), frame_rough=0.65,     # window·door frame
        skirt_color=(0.10, 0.10, 0.12), skirt_rough=0.8,      # facade skirting
        # `rail_*` is now used ONLY by the ground_kit metal parts (manhole lid,
        #   gutter cover, trench frame) — the guardrail that used to own it is
        #   gone. Kept as-is so the ground_kit wiring of pilot cb40ae8 is
        #   untouched.
        rail_color=(0.30, 0.30, 0.32), rail_metallic=0.5, rail_rough=0.5,
        # [realism v1] Alley wall pipe — painted mild steel gone chalky. Alley
        #   pipes are painted (green/blue-grey is the common Korean choice) and
        #   then weather, so this is NOT the bright half-metallic of `rail_*`:
        #   low metallic + high roughness so it stays a dull line against the
        #   pastel plaster instead of a specular highlight.
        pipe_color=(0.31, 0.34, 0.31), pipe_metallic=0.2, pipe_rough=0.72,
        pot_color=(0.35, 0.12, 0.10), pot_rough=0.7,          # terracotta pot (formerly tank_color)
        gear_color=(0.045, 0.05, 0.045), gear_rough=0.7,      # AC outdoor unit
        valley_tint=(0.85, 0.85, 0.82),
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
    # director r1 C-15(1): 171.5->153.0. Sun mapping world az ~ 33.5+offset = 186.5,
    #   shadow az = az−180 = 6.5 -> rays enter low, nearly parallel to the alley axis (+X),
    #   licking the stair floor (removes the solid dark mass). Keeps sun in the narrow alley.
    SUN_AZ_OFFSET=153.0,

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
# [C] path constants + required texture roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene15")

ASSET_ROLES = ["plaster", "plaza_lower", "concrete_floor", "hdri", "mdl"]


def tint_jitter(color, seed, amp=None, cap=0.80):
    """[v5.1 global convention 4] Per-instance ±amp tint jitter.

    If 12 houses simply cycle the same 5 pastel colours they read as 'copy-paste blocks'.
    Rather than design new materials, the existing colours are shaken ±5 % from an instance
    seed (deterministic — the same slot is identical on re-run). cap blocks large pure-white
    (>0.8) areas at the source."""
    if amp is None:
        amp = PARAMS["material"]["tint_jitter"]
    rnd = random.Random(1000003 * (int(seed) + 7))
    return tuple(round(min(cap, max(0.02, c * (1.0 + rnd.uniform(-amp, amp)))), 4)
                 for c in color)


def build_views():
    """Camera presets: grid_views(gy=0, flight1 axis) + 4 mise-en-scene shots."""
    views = sc.grid_views(0.0)               # flight1 axis = +X, y=0
    # top_compress: looks down the stair descent from the upper alley (wall compression)
    views["top_compress"] = dict(eye=[-3.0, 0.0, 1.6], tgt=[5.0, 0.0, -1.6])
    # bend_landing: from the landing, sees the vanishing beyond the 25 deg bend
    views["bend_landing"] = dict(eye=[3.4, 0.0, -0.4], tgt=[9.0, 1.5, -3.6])
    # narrow_up: looks up the narrow alley from below into backlight. Re-picked in v2 [B-15-5] -
    #   the old eye (7.5,0.4,−3.8) was bend-local (7.44,−0.65) = **inside** the south house
    #   solid, so 95 % of the frame was black. Moved to 1.5 m above the bent alley centre
    #   (local (7.4,0) = world (7.185,0.972), stair top there −3.40), with the sight line
    #   turned back inside the bend (landing·flight1). It passes through world y <= 0.49,
    #   so it never reaches the north house front (y 0.55).
    views["narrow_up"] = dict(eye=[7.185, 0.972, -1.90], tgt=[3.0, -0.2, 0.2])
    # beauty_overview: re-picked in v4 [v5 judgment applied · critical]. v3 (eye (0,−1.2,10),
    #   pitch −49 deg) was CLEAR on the occlusion check, but 70 % of the real frame was a
    #   top-down of house roofs·rooftop water tanks with the alley a 5 %-wide slit - an
    #   abstract colour field, not a 'hillside-slum alley'. v4 switches to a **high angle on
    #   the corridor axis** so corridor·stair descent·both pastel facades fit one frame.
    #     eye (−5.5, −0.2, 4.6) / tgt (4.6, 0.35, −2.04)  -> pitch −33.3 deg
    #   Pitch is slightly steeper than the judgment recommendation (−25~−30) because flight1's
    #   slope is atan(0.17/0.30)=29.5 deg, and the depression must exceed it for treads to resolve.
    #   occlusion check - sight line P(x) : y(x) = −0.2 + 0.05446(x+5.5),
    #                          z(x) = 4.6 − 0.65743(x+5.5)
    #     · eye : above the upper alley corridor (|y|<0.9), above the retaining wall 1.2·hedge 1.7 ✓
    #     · House[3](x −8.3..−4.9, y ≤ −1.38) / House[1](x −4.2..−1.0) :
    #       sight line y over that run = −0.352..−0.129 -> outside their y band ✓
    #     · retaining wall, 2 rows (|y| 0.9..1.4, top 1.2 · hedge 1.7) : over the whole run
    #       |sight line y| <= 0.377 -> it never enters the wall y band at all ✓
    #     · House[2]/[0] (north, y >= 1.38) : sight line y < 0 over the same run ✓
    #     · House[4] (x 0..2.8, y >= 0.58) : y=0.252 at x=2.8 -> 0.33 m margin ✓
    #     · House[5] (x 2.8..5.1, y >= 0.58) : y=0.377 at x=5.1 -> 0.20 m margin ✓
    #     · House[6]/[7] (south, y <= −0.58) : sight line y >= −0.20 ✓
    #     · (pole A was removed in [v5.1] - 0 obstacles inside the corridor)
    #     · ground : sight line z (−0.857 / −1.383) sits 0.66~0.84 m above the stair top
    #       (−1.70 at x=2.8 / −2.04 at x=3.6) -> lands on the landing (−2.04) at x=4.615 ✓
    #       (depression 33.3 deg > flight1 slope 29.5 deg, so all 12 steps resolve)
    views["beauty_overview"] = dict(eye=[-5.5, -0.2, 4.6],
                                    tgt=[4.6, 0.35, -2.04])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. top_compress / beauty — 좌우 주택·계단·25° 꺾임·하부 소실 식별
 2. h0.3·d5~10            — 좁은 시야에서 낙차 4.25m가 벽 압축에 은닉되는가
 3. bend_landing          — 참 뒤 꺾임 너머로 하부 골목이 소실(막다른 벽 없음)
 4. cue ON vs OFF         — railing/material_break 토글 시 기하 트랜스폼 불변
 5. 재질                  — 파스텔 회벽·지붕 오버행·Z파이팅·부유 없는가
 6. [realism v1] 난간     — 기본 무난간(방호=좌우 벽). 자립식 가드레일 0.
                            cue_railing ON 이면 북측 벽부착 파이프 1선만,
                            꺾임 아래는 ON/OFF 무관하게 무난간인가"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"
    smoke_mode = os.environ.get("NEGOBS_SMOKE", "0") == "1"
    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])

    simulation_app = sc.boot(capture_mode or smoke_mode)

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
    UsdGeom.Xform.Define(stage, "/World/Scene15")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene15"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # -------------------------------------------------------------------
    # materials
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["stair"] = PBR(f"{ROOT}/Looks/Stair",
                         diffuse_color=mp["stair_color"],
                         roughness_const=mp["stair_rough"], metallic=0.0)
        M["alley"] = PBR(
            f"{ROOT}/Looks/Alley", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"), sca["concrete_floor"])
        # [v5 judgment applied] dedicated retaining-wall material - separated from both the pavement (alley) and the pastel facades
        M["retwall"] = PBR(
            f"{ROOT}/Looks/RetWall", sc.tex_path("plaster", "diff"),
            sc.tex_path("plaster", "nor"), sc.tex_path("plaster", "rough"),
            sca["retwall"], tint=mp["retwall_tint"],
            roughness_const=mp["retwall_rough"])
        # [v5 judgment applied] dedicated deep-green material for pot foliage (old: M["roof"][1] grey -> white blob)
        M["foliage"] = PBR(f"{ROOT}/Looks/Foliage",
                           diffuse_color=mp["foliage_color"],
                           roughness_const=mp["foliage_rough"])
        M["valley"] = PBR(
            f"{ROOT}/Looks/Valley", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"),
            sc.tex_path("plaza_lower", "rough"), sca["plaza_lower"],
            tint=mp["valley_tint"])
        # pastel plaster - [v5.1] 5 shared colours -> +-5 % tint jitter **per house instance**.
        #   No new material parameters (the existing 5 pastel · 2 roof colours stay as the base).
        #   Slot = houses index, then backdrop index.
        specs = list(PARAMS["houses"]) + list(PARAMS["backdrop"])
        M["plaster_i"], M["roof_i"] = [], []
        for i, hs in enumerate(specs):
            base = mp["pastel"][hs["tint"] % len(mp["pastel"])]
            M["plaster_i"].append(PBR(
                f"{ROOT}/Looks/Plaster_{i}", sc.tex_path("plaster", "diff"),
                sc.tex_path("plaster", "nor"), sc.tex_path("plaster", "rough"),
                sca["plaster"], tint=tint_jitter(base, i)))
            rbase = mp["roof_tints"][hs["tint"] % len(mp["roof_tints"])]
            M["roof_i"].append(PBR(
                f"{ROOT}/Looks/Roof_{i}",
                diffuse_color=tint_jitter(rbase, 100 + i, cap=0.70),
                roughness_const=0.7))
        M["window"] = PBR(f"{ROOT}/Looks/Window",
                          diffuse_color=mp["window_color"],
                          roughness_const=mp["window_rough"], metallic=0.0)
        M["frame"] = PBR(f"{ROOT}/Looks/Frame",
                         diffuse_color=mp["frame_color"],
                         roughness_const=mp["frame_rough"])
        M["skirt"] = PBR(f"{ROOT}/Looks/Skirt",
                         diffuse_color=mp["skirt_color"],
                         roughness_const=mp["skirt_rough"])
        # [v5.1] 3 terracotta pot variants - +-5 % jitter of the same base colour (eases the 'display' impression)
        M["pot"] = [PBR(f"{ROOT}/Looks/Pot_{i}",
                        diffuse_color=tint_jitter(mp["pot_color"], 200 + i,
                                                  cap=0.55),
                        roughness_const=mp["pot_rough"]) for i in range(3)]
        M["gear"] = PBR(f"{ROOT}/Looks/Gear", diffuse_color=mp["gear_color"],
                        roughness_const=mp["gear_rough"])
        M["rail"] = PBR(f"{ROOT}/Looks/Rail",
                        diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        # [realism v1] Wall pipe handrail — separate from M["rail"], which now
        #   serves the ground_kit metalwork only.
        M["pipe"] = PBR(f"{ROOT}/Looks/Pipe",
                        diffuse_color=mp["pipe_color"],
                        metallic=mp["pipe_metallic"],
                        roughness_const=mp["pipe_rough"])
        return M

    # -------------------------------------------------------------------
    # ground - valley slab (fills the slope) + flat upper alley
    # -------------------------------------------------------------------
    def build_ground(M):
        v = PARAMS["valley"]
        H = v["size"] / 2.0
        th = 1.0
        BOX(f"{ROOT}/Valley", (5.0, 0.0, v["z_top"] - th / 2.0),
            (v["size"], v["size"], th), M["valley"], col=True)
        ua = PARAMS["upper_alley"]
        # upper alley: solid mesa (filled down to the valley), top z=0
        cx = (ua["x0"] + ua["x1"]) / 2.0
        cy = (ua["y0"] + ua["y1"]) / 2.0
        top, bot = ua["z_top"], v["z_top"]
        # [W2-0 · P-A] the upper alley top face is a ground_kit decoration target -> displacement
        #   skin OFF. Leave it on and the recessed joints (−3 mm)·manhole (+-10 mm) are buried
        #   whole under the skin (+6.5~16.5 mm) `[measured - spec §1.1]`.
        sc.skin_exclude(f"{ROOT}/UpperAlley")
        BOX(f"{ROOT}/UpperAlley", (cx, cy, (top + bot) / 2.0),
            (ua["x1"] - ua["x0"], ua["y1"] - ua["y0"], top - bot),
            M["alley"], col=True)
        # upper alley retaining wall, 2 rows (A-15-3 critical): a 1.8 m wide ridge -> both flanks closed.
        #   Top z=1.2, solid down to the valley (−4.35) -> the 4.35 m cliff is gone.
        rw = PARAMS["retwall"]
        for tag, y0, y1 in (("N", rw["y_in"], rw["y_out"]),
                            ("S", -rw["y_out"], -rw["y_in"])):
            BOX(f"{ROOT}/RetWall_{tag}",
                ((rw["x0"] + rw["x1"]) / 2.0, (y0 + y1) / 2.0,
                 (rw["z_top"] + v["z_top"]) / 2.0),
                (rw["x1"] - rw["x0"], y1 - y0, rw["z_top"] - v["z_top"]),
                M["retwall"], col=True)   # [v5 judgment applied] M["alley"] -> dedicated retaining wall
            # hedge on top of the retaining wall (helps read the alley)
            sc.build_hedge(stage, f"{ROOT}/RetHedge_{tag}",
                           rw["x0"], y0 + 0.05, rw["x0"] + 8.0, y1 - 0.05,
                           0.5, base_z=rw["z_top"])

    # -------------------------------------------------------------------
    # [W2] ground_kit - P5 alley_concrete. Full fill of the upper alley (x −12…0).
    #   Drop edge = the first step of flight1 at x=0. The joint at x=0 is dropped automatically
    #   by `_edge_guard_ticks` (GT-E2 Δ>=16 row). Only the stair-foot grating (15-6) uses
    #   bend-group local coordinates, so it is attached by a separate call.
    # -------------------------------------------------------------------
    def build_ground_kit(M, grp):
        g = PARAMS["ground"]
        gp = gk.plan_ground(
            "alley_concrete", region=tuple(g["region"]), z=0.0, gy=0.0,
            origin=(0.0, 0.0, 0.0),
            edges=[("stair_top", float(PARAMS["flight1"]["x0"]))],
            dists=(2, 5, 10), scene="scene15",
            tactile=(),                       # §12 - p~0.05, 0/12 in the sample -> not installed
            sites=dict(manhole=[tuple(g["manhole_d5"])],
                       gutter_U=[float(g["gutter_y"])],
                       trench=[],             # 15-6 is done separately in the bend group
                       patch=[tuple(v) for v in g["patch_sites"]]),
            overrides=dict(infra=dict(manhole=1, gutter_U=1, trench=0)),
            seed=15)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["stair"], crack=M["stair"], patch=M["alley"],
                  patch_cut=M["stair"], manhole=M["rail"], gutter=M["stair"],
                  gutter_cover=M["stair"], weed=M["foliage"],
                  stain_grime_band=M["skirt"], stain_dirt=M["skirt"],
                  trench=M["rail"], trench_frame=M["rail"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        # 15-6 linear grating at the stair foot - bend rot_group **local** coordinates.
        #   The lower alley top is z=−4.25, a different coordinate frame from the upper alley plan.
        gx, gy0, gy1 = g["grating_local"]
        gk.build_trench_drain(kit, f"{grp}/GKit_Grating", gx, gy0, gx, gy1,
                              float(g["grating_z"]), M["rail"],
                              mtl_frame=M["rail"], width=0.20)
        print(f"[ground_kit] scene15 P5 · 프림 {res['prims']} + 그레이팅 2 · "
              f"δmax {res['gt_delta_max']:.4f} · unit_cell {res['unit_cell']}")
        return res

    # -------------------------------------------------------------------
    # stairs - flight1 + landing + flight2 (25 deg bend) + lower alley
    # -------------------------------------------------------------------
    def build_stairs(M, grp):
        stair_mtl = M["stair"] if cfg["cue_material_break"] else M["alley"]
        f1 = PARAMS["flight1"]
        sc.build_straight_stairs(
            stage, f"{ROOT}/Flight1", f1["x0"], f1["y0"], f1["y1"],
            f1["riser"], f1["tread"], f1["nsteps"], f1["base_z"], stair_mtl,
            z_top=f1["z_top"], collider=True)
        # landing
        la = PARAMS["landing"]
        BOX(f"{ROOT}/Landing",
            ((la["x0"] + la["x1"]) / 2.0, 0.0,
             (la["z_top"] + la["base_z"]) / 2.0),
            (la["x1"] - la["x0"], f1["y1"] - f1["y0"],
             la["z_top"] - la["base_z"]), stair_mtl, col=True)

        # landing<->bend −Y wedge seal (A-15-4). Set 5 mm below the first step top (−2.21) to
        #   avoid coplanar Z-fighting; under the landing (x<5.1) it is buried in the landing solid.
        we = PARAMS["wedge"]
        BOX(f"{ROOT}/BendWedge",
            ((we["x0"] + we["x1"]) / 2.0, (we["y0"] + we["y1"]) / 2.0,
             (we["z_top"] + we["base_z"]) / 2.0),
            (we["x1"] - we["x0"], we["y1"] - we["y0"],
             we["z_top"] - we["base_z"]), stair_mtl, col=True)

        # flight2 + lower alley: rot_group 25 deg bend (grp is created once by the caller)
        f2 = PARAMS["flight2"]
        sc.build_straight_stairs(
            stage, f"{grp}/Flight2", f2["x0"], f2["y0"], f2["y1"],
            f2["riser"], f2["tread"], f2["nsteps"], f2["base_z"], stair_mtl,
            z_top=f2["z_top"], collider=True)
        # lower alley (inside the bend group - boundary aligned, vanishes toward +X)
        lo = PARAMS["lower_alley"]
        BOX(f"{grp}/LowerAlley",
            ((lo["x0"] + lo["x1"]) / 2.0, (lo["y0"] + lo["y1"]) / 2.0,
             (lo["z_top"] + lo["base_z"]) / 2.0),
            (lo["x1"] - lo["x0"], lo["y1"] - lo["y0"],
             lo["z_top"] - lo["base_z"]), M["alley"], col=True)

        # ── [realism v1] Guarding: the flanking walls ARE the guard ─────────
        #   The corridor is walled on **both** sides for the whole descent
        #   `[measured from PARAMS]`:
        #     upper alley x −12..0   retaining walls, inner faces |y| = 0.90
        #     flight1     x 0..3.6   House[4] y=+0.58 / House[6] y=−0.58
        #     landing     x 3.6..5.1 House[5] y=+0.58 / House[7] y=−0.58
        #     flight2     local 5.1..9.0  House[8] / House[10] local y=±0.58
        #   against stair edges at y=±0.60 — i.e. the walls sit 20 mm *inside*
        #   the stair, so no side is ever open to the 4.25 m drop. Evac/fire
        #   §15(1)2 is therefore satisfied by "wall" and **no guardrail is
        #   required anywhere in this scene** (same reading as the scene05 arc
        #   stair on its cheek walls — Docs/reports/stair_compliance_v1.md §1).
        #   The removed A-15-5 fix answered the wrong question: it extended a
        #   guardrail along a corridor that never lacked a guard.
        #   What `cue_railing` builds now is a *handrail* (§15(4)), not a guard:
        #   one φ34 pipe on the north wall over flight1 + the landing, stopping
        #   dead at the bend. Photo tally behind this choice: report §1.
        #   GT: unchanged. A pipe above the treads adds no terrain z — see the
        #   "drop label invariant" note on stair_kit.build_handrail. The drop
        #   edge at x=0 also loses its 116-prim occluder, so grazing exposure of
        #   that edge can only improve, never regress.
        if cfg["cue_railing"]:
            rl = PARAMS["rail"]

            def _wall_pipe(prefix, spec, z_top, ext_top, ext_bot):
                res = sk.build_handrail(
                    stage, prefix, rl["wall_y"], spec["x0"],
                    spec["tread"] * spec["nsteps"],
                    spec["riser"] * spec["nsteps"],
                    M["pipe"], sc.add_cylinder, z_top=z_top,
                    height=rl["height"], dia=rl["dia"],
                    ext_top=ext_top, ext_bot=ext_bot,
                    post_spacing=rl["bracket_spacing"],
                    wall_y=rl["wall_y"], wall_side=rl["wall_side"],
                    wall_gap=rl["wall_gap"], bracket_r=rl["bracket_r"],
                    strict=False)      # sub-code by design — warn, never raise
                for w in res["warnings"]:
                    print(f"[cue_railing] 규정 미달(의도) — {w}")
                return res

            # Upper flight + landing. `ext_bot` 1.5 carries the pipe flat over
            #   the landing to the bend, which is where the wall run ends.
            r1 = _wall_pipe(f"{ROOT}/WallPipe", f1, f1["z_top"],
                            rl["ext_top"], rl["ext_bot"])
            n_pipe = len(r1["prims"])
            # Optional lower-flight pipe (rot_group local — turns with the bend).
            #   OFF by default: see the `lower_flight` note in PARAMS.
            if rl["lower_flight"]:
                r2 = _wall_pipe(f"{grp}/WallPipe2", f2, f2["z_top"],
                                0.0, 0.0)
                n_pipe += len(r2["prims"])
            print(f"[cue_railing] 벽부착 파이프 손잡이 · 프림 {n_pipe} · "
                  f"y={r1['y']:.3f} (벽 {rl['wall_y']:+.2f}) · "
                  f"하부 플라이트 {'유' if rl['lower_flight'] else '무'}난간 "
                  f"— 방호는 좌우 벽이 담당")

    def build_flat_control(M):
        """hazard_stairs=False: the upper alley extends flat at z=0 (stair removed)."""
        f1 = PARAMS["flight1"]
        v = PARAMS["valley"]
        x0, x1 = 0.0, 12.0
        BOX(f"{ROOT}/FlatAlley",
            ((x0 + x1) / 2.0, 0.0, (0.0 + v["z_top"]) / 2.0),
            (x1 - x0, f1["y1"] - f1["y0"], 0.0 - v["z_top"]),
            M["alley"], col=True)

    # -------------------------------------------------------------------
    # houses (pastel plaster box + window·door inset + roof overhang)
    # -------------------------------------------------------------------
    def _opening(prefix, tag, cx, yf, face, z, ow, oh, M):
        """1 window·door = a dark panel + 4 frame edges.

        [B-15-2 fix] The old code **added** `ny = 0.02*face` to
        `gy = cy + face*(d/2−0.005)` (5 mm inside the wall face) as `wy = gy + ny`, so the
        centre of the 0.04-thick panel ended up 0.015 m outside the wall face → a black
        plate floating 3.5 cm off the wall, with its side thickness showing in the render.
        A true inset is impossible because the shell is solid, so the sign is corrected so
        that the panel **outer face** lands at wall face +5 mm (effectively flush), and
        4 frame edges projecting 3 cm are placed around it to read as an 'inset window'."""
        t_p, t_f, fw = 0.04, 0.05, 0.06
        py = yf + face * (0.005 - t_p / 2.0)       # panel outer face = wall face +5 mm
        BOX(f"{prefix}/{tag}_Panel", (cx, py, z), (ow, t_p, oh), M["window"])
        fy = yf + face * (0.03 - t_f / 2.0)        # frame outer face = wall face +3 cm
        for nm, ox, oz, sx, sz in (
                ("T", 0.0, oh / 2 + fw / 2, ow + 2 * fw, fw),
                ("B", 0.0, -oh / 2 - fw / 2, ow + 2 * fw, fw),
                ("L", -ow / 2 - fw / 2, 0.0, fw, oh),
                ("R", ow / 2 + fw / 2, 0.0, fw, oh)):
            BOX(f"{prefix}/{tag}_F{nm}", (cx + ox, fy, z + oz),
                (sx, t_f, sz), M["frame"])

    def build_house(prefix, hs, M, slot, life=False):
        h = PARAMS["house"]
        cx, cy = hs["cx"], hs["cy"]
        w, d, ht = hs["w"], hs["d"], hs["h"]
        base = hs["base_z"]
        face = hs["face"]
        v = PARAMS["valley"]
        shell_mtl = M["plaster_i"][slot]     # [v5.1] per-instance tint jitter
        top = base + ht
        bot = v["z_top"]                          # solid down to the valley (no floating, no cavity)
        BOX(f"{prefix}/Shell", (cx, cy, (top + bot) / 2.0),
            (w, d, top - bot), shell_mtl, col=True)
        # facade (alley-side) wall plane: face=-1 -> -Y face (y=cy-d/2), face=+1 -> +Y face
        yf = cy + face * (d / 2.0)
        z_win = base + ht * 0.55
        for c, off in enumerate((-w * 0.28, w * 0.28)):
            _opening(prefix, f"Win_{c}", cx + off, yf, face, z_win,
                     h["win_w"], h["win_h"], M)
        _opening(prefix, "Door", cx, yf, face, base + h["door_h"] / 2.0,
                 h["door_w"], h["door_h"], M)
        # roof slab (overhang)
        BOX(f"{prefix}/Roof", (cx, cy, top + h["roof_t"] / 2.0),
            (w + 2 * h["roof_over"], d + 2 * h["roof_over"], h["roof_t"]),
            M["roof_i"][slot], col=True)
        # skirting band (dark band at the facade base) - a paint trace, so every house keeps it.
        #   [v5.1 global convention 4] it doubles as the 'base grime band' (blocks large pure-white areas).
        BOX(f"{prefix}/Skirt", (cx, yf + face * 0.015, base + 0.425),
            (w, 0.03, 0.85), M["skirt"])
        if not life:
            return
        # ── [v5.1] traces of daily life = 1 AC outdoor unit only ──
        #   The old spec (meter box·satellite dish+bracket·rooftop water tank) was cloned onto
        #   all 12 houses at the same position and size, reading as a 'prop catalogue' (user review).
        #   The wall-mounted AC unit is the only functional fixture flush with the facade, so only it stays.
        BOX(f"{prefix}/AC", (cx - w * 0.30, yf + face * 0.16,
                             base + ht * 0.78), (0.70, 0.32, 0.55), M["gear"])

    def build_dressing(M, grp):
        # 12 houses. Those with grp=True sit under the bend rotation group (local coordinates)
        #   and flank the 25 deg-rotated alley directly [resolves A-15-1/2 critical].
        #   [v5.1] life applies to only the 2 houses the scene parameters name (old: all 12).
        n_house = len(PARAMS["houses"])
        for i, hs in enumerate(PARAMS["houses"]):
            root = grp if hs.get("grp") else ROOT
            build_house(f"{root}/House_{i}", hs, M, i,
                        life=bool(hs.get("life")))
        # opposite hill backdrop cluster (distant horizon closure - not a dead-end wall, a
        #   Gamcheon-style house group terraced on the far slope across the valley). It closes
        #   the horizon behind the vanishing point of the bending alley (checklist §A-4).
        for i, bh in enumerate(PARAMS["backdrop"]):
            build_house(f"{ROOT}/Backdrop_{i}", bh, M, n_house + i)
        # [v5.1] utility poles·wires·clotheslines removed (see the rationale in the PARAMS comment).
        # 5 flower pots (alley edge, one per stair level) - pot + foliage blob, 2 prims
        po = PARAMS["pot"]
        for i, (px, py, pz, in_grp) in enumerate(PARAMS["pots"]):
            root = grp if in_grp else ROOT
            CYL(f"{root}/Pot_{i}", (px, py, pz + po["h"] / 2.0),
                po["r"], po["h"], M["pot"][i % len(M["pot"])], col=True)
            sc.add_sphere(stage, f"{root}/PotLeaf_{i}",
                          (px, py, pz + po["h"] + po["leaf_r"] * 0.6),
                          (po["leaf_r"], po["leaf_r"], po["leaf_r"] * 0.8),
                          M["foliage"])   # [v5 judgment applied] grey -> deep green

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    # the bend rotation group is shared by stairs·houses·dressing, so it is created once at the top of assembly
    #   (dressing under the group still rotates correctly in the hazard_stairs=False control).
    _bd = PARAMS["bend"]
    GRP = sc.build_rot_group(stage, f"{ROOT}/Bend", _bd["pivot"], _bd["deg"])
    build_ground(M)
    if cfg["hazard_stairs"]:
        build_stairs(M, GRP)
    else:
        build_flat_control(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M, GRP)
    build_ground_kit(M, GRP)             # [W2] ground elements - after the dressing (scatter order convention)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] scene15 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene15_{ts}.png")
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
