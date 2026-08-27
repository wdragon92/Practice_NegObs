# -*- coding: utf-8 -*-
"""
scene14_grandstair_illusion.py - NegObs synthetic scene 14: illusory monumental stair (Isaac Sim 4.5)

Type    : T14 Potemkin-style illusory grand stair (40 steps, 3 landings, tapered widening)
Spec    : Docs/briefs/multi_scene_brief_v3.md §D scene14_grandstair_illusion + director addendum
Shared  : scene_common.py (build_straight_stairs width_pairs) · scene02 skeleton

Hazard  : Walking forward from the small upper viewing plaza, only the landings of the 40-step
          stair are visible and it is misread as a flat terrace. In reality a 6.0 m drop hides
          between the landings. The perspective illusion of the width opening from upper y+-3 to
          lower y+-5 strengthens the concealment.
Goal    : Assemble the small upper plaza (granite) + 40 steps (3 landings, continuous width_pairs)
          + sloped side parapets + the lower grand plaza (fountain hint) + 2 distant buildings.

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene14_grandstair_illusion.py

Auto capture mode (for headless verification):
    NEGOBS_CAPTURE=1 python scene14_grandstair_illusion.py
Smoke (pre-boot geometry self-verification, early exit):
    NEGOBS_SMOKE=1 python scene14_grandstair_illusion.py

Coordinates: Z-up, m, travel axis +X, drop start edge = x=0. Total drop 6.0 m.

═══ [W3 L14] G1 renovation — what this wave changed, and what it refused to ═══
Governing image: **G1** (`Docs/reference_photos/Generated Image - Scene01.jpg`), the nearest
image for this scene under `w3_intake_v2_images.md` §4 row **3.4** (G1 primary, G8 secondary).
Season pinned from G1 under §7 ruling 8: **autumn, IN LEAF** — `build_tree(bare=)` is therefore
deliberately NOT used (see `_season_audit`).

The **illusion is the research identity and it is frozen**: 40 steps · riser 0.150 · tread 0.340 ·
3 landings @ 2.400 · half width 3.0 -> 5.0 · total drop **6.000 m**. No nosing, riser, tread,
landing or drop-edge coordinate moved in this wave; `_stair_selfcheck` asserts the drop to
1e-9 and the nosing polyline against a pre-wave reference table.

What DID change (all of it around the flight, none of it in it):
  1. **Stone product.** G1's flight is *flamed light-grey granite*, coursed. This scene bound
     `marble_light` (warm cream) to BOTH the flight and the stair-head terrace, so the
     `cue_material_break` toggle it advertises produced **no break at the stair head at all** —
     the two surfaces were the same material. The flight is now light-grey granite and the
     terrace stays marble, which is the first time this cue has had any content. The OFF arm
     restores marble on the flight (the boundary really is absorbed). See `setup_materials`.
  2. **Unit coursing (`build_step_coursing`).** A 6-10 m wide step cut from one stone does not
     exist. G1's flight is laid in units with staggered vertical joints. Joints are built to the
     ground_kit convention — 7 mm wide (KCS 34 6-5-1 3.1.11 판석 줄눈 5~9 mm), tone plate whose
     top stands `GROUND_PROUD_MIN` = 0.6 mm proud so it cannot z-fight the step solid. That
     0.6 mm is the ONLY z the walked surface gained and it is 3 % of `GT_DELTA` (0.020);
     `build_joint_grid`'s own docstring rules a joint "not a drop". Declared anyway: GT-52.
  3. **Autumn dress** — leaf litter on the treads/landings/terrace/lower plaza, autumn turf.
  4. **BS-4** — the five distant blocks were a closed wall of windows. They are lowered until
     `plan_building`'s ridge clears the judged frame ceiling on every block, and built as
     `kind="backdrop"` silhouettes (the S01 precedent).
  5. `PlanterLow_0/_1` re-sited off `lower_lookup` (`w3_md_reverts_v1.md` §5 census row).
  6. `species=` declared explicitly at every vegetation call site.
Divergences from G1 that are recorded and NOT executed — see the report `w3_l14_v1.md` §3.

═══ [GT-70] 08-05 gallery answer — the stone product is retired ═════════════════
User ruling: *"화강석 재질 집착 중단 — '그냥 큰 계단'으로 읽히면 충분"* and *"측벽은 적당한
벽 겸 handrail 로 읽히게"*. Two items, both of them re-representation:
  1. **The flight stops being granite.** L14 bound the flight, the landings and the shoulder
     to a scene-side granite made from the `plaza_light` slab scan with a tuned warm tint;
     the parapet cheek took the same scan darkened. Four surfaces were carrying one
     hand-tuned stone. They now take the library's plain concrete roles — `concrete_floor`
     on the walked family and `concrete_wall` on the side walls — at the library's own
     scales (1.0 / 2.0, the `scene02` underpass-stair values). **No role is acquired**: both
     roles are already in `sc.TEX` and on disk. The material-prim names move to
     `ConcreteFloor` / `ConcreteWall`, which is load-bearing: `_look_spec` classifies by
     prim name, so the old `GraniteLight` / `StoneCheek` names would keep the **stone**
     prescription (sat 0.66 · patch 1.0 · `_W_STONE`) on a concrete texture.
  2. The side wall gained a handrail — **withdrawn at GT-78, see the block below.**
**No parapet, tread, riser, landing, nosing or drop-edge coordinate moves, and no collider
is added or removed.** P-15 (the parapet base defect) stays deferred and is NOT touched here.

═══ [GT-78] 08-06 gallery answer — the wall-top handrail is withdrawn ═══════════
User ruling: *"왜 벽에 핸드레일을 달았지? 빼."* Everything GT-70 mounted on the wall top is
deleted — the `build_wall_handrail` builder (8 bars + 13 stanchions per side = **42 prims**,
prim roots `WallRail_N` / `WallRail_S`), its `parapet.rail` parameter block and its call site,
all three in the same edit. That is this file's own K2 doctrine, already applied to the `patch`
sites: a live parameter block for a withdrawn element is how the next reader reinstates it by
restoring one line.
What GT-70 keeps, it keeps: the concrete re-materialisation (item 1 above) is untouched, and
**the wall itself does not move** — top face on the nosing line + 0.950 m, width 0.5, the same
raking parapet the flight has carried since v5.1. The rail family was dressing (`col=False`)
riding above the wall, so this removal changes **0 colliders, 0 walked-surface z and 0 drop-edge
coordinates**; nothing but the 42 rail prims leaves the stage.

Materials: `marble_light` (terrace / plinth / monument) · `concrete_floor` (flight, landings,
shoulder) · `concrete_wall` (side walls) · `plaza_light` (upper plaza) · `plaza_lower`
(lower plaza) · `band_dark` (joints, coursing, bands) · `Looks/Rail` (kept for the
`cue_railing` ablation arm only — nothing rides on the wall top).
"""

import os
import sys
import math
import json
import datetime
import re

import numpy as np

import scene_common as sc
import ground_kit as gk
import facade_kit as fk
import building_kit as bk


# ===========================================================================
# [A] SCENE_CONFIG - 7 keys. Only hazard_stairs toggles the hazard geometry.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False -> stairs/landings become z=0 flat (the one geometry-toggle exception)
    "cue_railing":        False,   # A monumental stair is open-sided - True -> pipe rail on top of the side parapets
    # [v5 shared layer] Urban-practice scenes (01/02/05/13/14/16/20/21) default cue_tactile to True.
    #   The old comment's 'not customary' is void after the v5 setting was clarified (plaza grand stair in front of a city hall / cultural centre) -
    #   tactile paving at the entry of a public-building grand stair is standard domestic practice. Real geometry is generated.
    "cue_tactile":        False,  # [v5.2 user] Tactile paving is rare in reality - default OFF (the ablation path is kept)    # top entry warning tactile band (x −0.4..0, stair upper width)
    # [W3 L14] **This toggle now has content.** Until this wave both the flight and the
    #   stair-head terrace were bound to `marble_light`, so ON and OFF emitted *pixel-identical*
    #   frames and the ablation arm measured nothing. ON = a flight whose product differs from
    #   the marble terrace (a real material boundary at the drop edge x=0); OFF = marble flight,
    #   i.e. the boundary is absorbed, which is what the toggle always claimed to do.
    # [GT-70] The ON arm's product changes granite -> plain concrete. The break is *wider*
    #   than before (concrete vs marble, not grey stone vs cream stone), so the cue keeps its
    #   content; only its two sides change. Arms rendered before GT-70 are not comparable.
    "cue_material_break": True,
    "cue_sign":           True,    # [v5 shared layer] 1 sign_info (plaza information)
    "cue_scene_dressing": True,    # street lamps · parapet kerb · fountain hint · distant buildings
    "cue_nosing":         False,   # [new] True -> nosing band on every step
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # --- Grand stair: 40 steps, riser 0.15 (drop 6.0), tread 0.34, 3 landings (depth 2.4) ---
    stairs=dict(x0=0.0, riser=0.15, tread=0.34, nsteps=40, z_top=0.0,
                base_z=-6.7, seg_len=10, landing_depth=2.4,
                w_top=3.0, w_bot=5.0),            # half width: upper y+-3 -> lower y+-5
    landings=(10, 20, 30),                        # landing insertion points (after step n)

    # ═══ [W3 L14 · G1] Unit coursing of the granite flight ════════════════════
    #  **The defect.** `build_straight_stairs` emits ONE box per step, so every step of
    #  this flight was a single stone 6.00 m wide at the head and 10.00 m wide at the
    #  foot. No quarry cuts a 10 m step, and G1 — the governing image — shows the
    #  opposite: a wide granite flight laid in **units**, with vertical joints running
    #  from riser to nosing and **staggering course to course** (running bond). At the
    #  frame scale of `lower_lookup` / `side_reveal` the monolith is what makes the
    #  flight read as an extrusion rather than as masonry.
    #
    #  **What is built.** One prim per joint per step: a plate of `joint_w` in Y that
    #  spans the tread in X and the riser in Z, tone-bound to `band_dark`. Its top face
    #  stands `proud` above the tread and its front face `proud` in front of the riser,
    #  which is the `ground_kit` convention verbatim (`build_joint_grid` v1.2: a real
    #  *recess* is trapped inside the solid slab and renders **zero pixels**, so the
    #  groove is carried as a dark **tone** on a plate that cannot z-fight).
    #
    #  **Numbers and where they come from.**
    #    `joint_w`  0.007  — KCS 34 6-5-1 3.1.11 판석 줄눈 5~9 mm, centre value.
    #                        Identical to `ground_kit._dim("joint_slab_w")`.
    #    `proud`    0.0006 — `ground_kit.GROUND_PROUD_MIN`, the measured z-fighting
    #                        floor. **This is the only walked-surface z this wave adds:
    #                        3.0 % of `GT_DELTA` (0.020) — GT-52 declares it anyway.**
    #    `unit`     1.20   — nominal unit length. Korean granite step stone (화강석
    #                        계단석) is quarried at 600 / 900 / 1200 mm; a civic flight of
    #                        this width takes the long unit. The builder fits an INTEGER
    #                        number of units across each step's own width (which grows
    #                        3.0 -> 5.0 half width down the flight), so the true unit
    #                        length breathes 1.09~1.25 m and the joint count grows with
    #                        the taper — which is what a real tapered flight does.
    #    `bond`     0.5    — running bond: alternate courses are offset half a unit.
    #                        0.0 would stack the joints into continuous rakes down the
    #                        flight, which is a stack bond and is not what G1 shows.
    #    `min_units` 4     — never fewer than 4 units on a step (a 6 m two-piece step is
    #                        as unbuildable as a one-piece one).
    #
    #  [GT-70] The stone product is retired but **this geometry is not touched**: the same
    #  1.09~1.25 m unit rhythm is what a precast concrete step run (프리캐스트 계단판, cast at
    #  0.9~1.5 m lengths) shows, and the plates carry the joint tone rather than a stone
    #  identity. Retiring them would be a walked-surface change (the 0.6 mm proud declared at
    #  GT-52) and this row is R-3; the joint count, width and bond stay byte-identical.
    coursing=dict(unit=1.20, joint_w=0.007, proud=0.0006, bond=0.5, min_units=4,
                  riser_face=True, landings=True),
    # --- Upper viewing plaza (marble stair head, marble instead of granite) ---
    upper=dict(x0=-9.0, x1=0.0, y0=-8.0, y1=8.0, z_top=0.0, thick=0.5),
    # --- Large upper plaza (director D-14 r3(1)): 20m in -X behind the terrace x y+-20, plaza_light.
    #     So the stair reads as a structure joining two levels (isolation removed). 3 boxes leaving a terrace hole.
    upper_big=dict(x0=-29.0, x1=0.0, y0=-20.0, y1=20.0, z_top=0.0, thick=0.5),

    # ═══ [W2-D ground_kit] P1 plaza_granite - spec §5.1 scene14 row ═══════════
    #  Row prescription: "marble_light module 600 is already correct -> joints
    #  only; stair-head transverse trench; 2 gullies (v1.1); marble water
    #  staining that follows the joints; manhole (-8.7, +1.2)".
    #  Tactile is **OFF** here: §12.4 puts 14 in the hidden-illusion group
    #  (identity conflict). Gate B12 `_inv_hidden_illusion` enforces it, so a
    #  tactile band cannot be introduced by accident from this file.
    #
    #  ★ Trench centre -2.55 -> **-2.59** (this file's correction of the C-1'
    #    figure). C-1' derives the centre from a **0.30 m wide** trench (near
    #    lip -2.40, drow = 16.05 rows @1080 >= 16 at d10). The builder frames
    #    the cover: `build_trench_drain` adds `trench_frame_w` 0.040 on each
    #    side, so the real near lip of a trench centred at -2.55 is -2.36 and
    #    drow(-2.36, 10) = **15.70 < 16 = FAIL** [computed].  Centre -2.59 puts the
    #    frame lip back on -2.40 exactly (16.05 rows). This is the same class
    #    of correction scene13 applied to its entry trench (0.35 -> 0.52).
    #  ★ Gullies: row says `|y| = stair width/2 - 0.40`; `stairs.w_top` is the
    #    half width, so |y| = 3.00 - 0.40 = 2.60 (read from PARAMS, §7.4).
    ground=dict(
        region=(-12.0, -4.0, -0.5, 4.0),      # terrace + west plaza corridor
        trench_x=-2.59,                       # C-1' re-derived on the frame lip
        gully_x=-0.95,                        # stair-head point gullies (C-1')
        gully_inset=0.40,                     # |y| = w_top - inset
        manholes=[(-8.7, 1.2), (-4.5, -1.5)],
        # ── [W3 L14] the `patch` sites are DELETED, not commented out ────────────
        #   They were "near-window (W1) fillers": two 2 mm repair patches placed to
        #   carry the d2/d5 window. **GT-24 deleted `("patch", 1)` from
        #   `GROUND_PROFILES["plaza_granite"]` library-wide** (this scene went 860 ->
        #   859 prims in that sweep), so `sites=dict(patch=...)` has had a count of 0
        #   to spend since, and the list was inert data that reads as intent.
        #   Two reasons it goes rather than staying as a comment:
        #     (a) **revert trap** (the T4b-F2 class) — a later reader restoring the
        #         profile row would silently resurrect two rectangles the user's
        #         "바닥에 이상한 사각형 무늬는 웬만하면 다 제거해" directive removed;
        #     (b) it is camera-driven authoring by its own admission ("to carry the
        #         d2/d5 window"), which is exactly the practice G-4 exists to end.
        #   G1 carries no repair patch on its plaza; a monumental granite terrace laid
        #   this decade has nothing to repair. `plaza_granite`'s `surface` row is
        #   `('crack','stain')` — lines and irregular lobes, no rectangle.
    ),
    streetlight=dict(pole_h=5.0, pole_r=0.06, arm_len=1.0, arm_r=0.04,
                     head=0.25, xs=(-6.0, -14.0, -22.0), ys=(-6.0, 6.0)),
    # --- Lower grand plaza (plaza_lower + band_dark bands) + fountain hint ---
    #     x1 40->75 : ground laid out to the foot of the distant buildings, fixing the 5 m float [B-14-1 critical]
    lower=dict(x1=75.0, y0=-20.0, y1=20.0, z_top=-6.0, thick=0.5),
    # --- Sloped grass banks either side of the stair (director D-14 r3(2)): outside the parapet y+-5.2..+-20, upper->lower ---
    #     thick 0.5->3.0 : fixes the thin plate that appeared to hang in mid air (solid slope massif)
    #     run_ext 3.2   : hides the lower end face (the slope cut wedge) under the lower plaza
    side_slope=dict(y_out=20.0, thick=3.0, run_ext=3.2),
    fountain=dict(cx=30.0, cy=0.0, r_out=3.0, r_in=2.4, h=0.4,
                  nozzles=5, nozzle_r=0.06, nozzle_h=0.5),
    # --- Side parapets (the raking side walls of the flight) ---
    # ═══ [GT-78] the `rail` sub-block is deleted — nothing rides on the wall top ═══
    #  GT-70 carried a Ø38 mm bar on Ø30 stanchions 0.100 m above the wall top (guard line
    #  1.069 m); the 08-06 gallery answer rejects it. The seven parameters go out with the
    #  geometry so the family cannot be reinstated by restoring one line — the same removal
    #  discipline the `patch` sites got.
    #  **The wall keeps every number it had**, and they are the numbers the checks read:
    #    `width` 0.5  — plan width of the parapet; the wall spans |y| 5.05…5.55.
    #    `z0`    0.35 — wall top over the nosing line is `z0 + 0.6` = **0.950 m**, the top
    #                   of the 08-05 wall band (0.85~0.95). Asserted pre-boot (check ⑱).
    #    `thick` 1.6  — body depth embedded into the stepped shoulder over the whole run
    #                   (v5.1: this is what removed the floating-plate read).
    #    `cap_t` 1.4  — thickness of the oblique top haunch; the bite check in the
    #                   `build_parapets` docstring (vertical equivalent 1.530 > 0.43+0.03).
    parapet=dict(width=0.5, z0=0.35, thick=1.6, cap_t=1.4),
    # --- Shoulder outside the stair (replaces the old soffit) - see build_shoulder ---
    shoulder=dict(y_out=5.2, offset=0.03, lap=0.05),
    # ═══ [W3 L14 · BS-4] the five distant blocks — from a wall to a skyline ═══
    #  **The defect the target image names.** `w3_intake_v2_images.md` §2 scene14 (c) calls
    #  it out before a pixel was looked at: *"Same 'closed backdrop' risk as 01: the two
    #  distant buildings can wall the frame."* Measured on the landed `260730_w2d_fix`
    #  round, they do more than risk it — at h 12/10/9/22/18 on a plinth at z −6 they
    #  close the horizon on **every** judged cut and on `terrace_read`, and the G1
    #  cross-cutting read (`§1`, item 4) rules the opposite: *"Backdrops are open: G1 …
    #  shows sky above the roof/ridge line. Only G2, G8 and G13 close the horizon, and
    #  those are genuinely dense-urban cells."* G1 is this scene's primary image.
    #
    #  **The test, and where the number comes from.** `facade_kit.frame_ceiling`: the
    #  judged camera is the h·d grid at pitch −10° with vFOV 36°, so the top of frame is
    #  +8° above the horizon and the tallest thing that can enter frame at plan distance
    #  d is `z = h_eye + tan(8°)·d ≈ h_eye + 0.1405·d`. `bk.plan_building(eyes=…)`
    #  re-derives `d_true` from the **real judged eye set** (B-F3) instead of from
    #  `|facade plane|`, and returns `z_ceil` at the worst — lowest, nearest — eye.
    #  Acceptance: **`p.ridge < p.z_ceil` on all five**, printed at assembly time.
    #
    #  **`h` is the SHELL top, not the ridge** — the S01-F1 lesson, and the reason each
    #  height below is solved from `z_ceil − roof_allow − base_z`. That is no longer a
    #  scene-side constant: K-micro landed `Plan.ridge` / `Plan.roof_allow` for exactly
    #  this caller, **exact** for `kind="backdrop"` and an upper bound otherwise, so the
    #  solve uses the kit's own number and the print compares like with like.
    #
    #  **Why they are lowered and not pushed back.** Pushing back is the better move and
    #  it is not available: the lower plaza ends at x 75 and the site at y ±20, so any
    #  block that moves further out floats — and extending a walked plaza to catch it is
    #  a GT event this wave is not authorised for (class A, `w3_intake_v2_images.md` §2
    #  scene14 (f)). Recorded as an open item rather than smuggled in.
    #
    #  **The builder stays `sc.build_building`, and that is a decision taken on pixels,
    #  not a decision skipped.** The `building_kit` route was written, rendered and
    #  rejected: `bk.build_korean_building(eyes=bk.judged_eyes(0.0))` puts B at
    #  `d_true` 44 m, which is the kit's **`far`** tier, and `far` is defined as *"windows
    #  become one horizontal band per floor, no attachments"*. In `terrace_read` — the
    #  illusion cut, where the backdrop owns the upper half of the frame — that turned a
    #  five-storey block with a window rhythm into a **blank slab with two ribbon
    #  bands**, i.e. a *worse* frame than the closed one the directive is trying to
    #  open. Both rounds exist (`260731_w3_l14_bk` and this one) and the crop is in the
    #  report. The tier ladder is right for a scene whose backdrop is 60–120 m away
    #  (scene01's is); it is wrong for a ring at 34–58 m, and arguing the kit out of it
    #  belongs in a lane that can iterate the tier — recorded as an open item, with the
    #  measurement, instead of shipped because it was the fashionable route.
    #  **What BS-4 actually asked for is delivered: sky above every roofline.** The kit
    #  is kept as the *measuring instrument* — `bk.plan_building(eyes=…)` supplies
    #  `d_true` and `z_ceil` — and the ridge is `sc.build_building`'s own, which is
    #  `base_z + h + 3.28` **derived from the builder, not guessed**: `Penthouse` sits at
    #  `base + h + 0.5 + 2.6/2` (height 2.6), `PenthouseCap` centres at
    #  `base + h + 0.5 + 2.6 + 0.09` with half-thickness 0.09, so the highest emitted
    #  prim is `base + h + 3.28`; the statutory 1.20 m rooftop parapet (건축법 시행령
    #  제40조) is lower and never wins. Guessing this number is the S01-F1 defect, which
    #  shipped a wall through the top of frame while printing "sky 6/6".
    #  Heights are solved from `h < z_ceil − base_z − 3.28`, per block, at its own d_true.
    buildings=dict(
        B=dict(x0=42.0, x1=48.0, y0=-14.0, y1=14.0, h=8.9, floors=3,
               axis="x", facade_x=42.0, face_dir=-1.0, base_z=-6.0),
        C=dict(x0=30.0, x1=40.0, y0=13.0, y1=19.0, h=7.5, floors=2,
               axis="y", facade_y=13.0, face_dir=-1.0, base_z=-6.0),
        F=dict(x0=30.0, x1=40.0, y0=-19.0, y1=-13.0, h=7.2, floors=2,
               axis="y", facade_y=-13.0, face_dir=1.0, base_z=-6.0),
        D=dict(x0=56.0, x1=70.0, y0=-19.0, y1=-6.0, h=10.9, floors=4,
               axis="x", facade_x=56.0, face_dir=-1.0, base_z=-6.0),
        E=dict(x0=56.0, x1=70.0, y0=4.0, y1=19.0, h=10.9, floors=4,
               axis="x", facade_x=56.0, face_dir=-1.0, base_z=-6.0),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.5, margin=2.0),
    # [W3 L14] highest prim of `sc.build_building` above `base_z + h` — see above.
    sc_roof_extra=3.28,
    # --- Context dressing (instant read as a monumental plaza) - all combinations of existing builders, owned by cue_scene_dressing ---
    dressing=dict(
        # lower grand plaza (z −6.0)
        trees_low=((24.0, 7.0), (24.0, -7.0), (24.0, 13.0), (24.0, -13.0),
                   (33.0, 10.0), (33.0, -10.0)),
        # [W3 L14 · `w3_md_reverts_v1.md` §5 census] The inner pair was **(25.5, ±4.0)**
        #   and it is this scene's census row: `lower_lookup`'s eye (26.0, 0.0, −5.2)
        #   sits 2.50 m from the kerb and **2.45 m from the bed AABB** — inside the
        #   2.5 m radius, on 1 judged cut, with a live `Juniper.usd` in it. The eye is
        #   also *inside the x span* of the bed (24.0…27.0), which is the C02-P1 defect
        #   shape exactly: a camera standing in a flower bed.
        #   Moved to **(27.0, ±5.5)** — box x 25.5…28.5, y ±(4.0…7.0). The eye stays
        #   inside the x span (that is what makes the cut work) and the plan distance
        #   becomes **4.00 m**, measured, not estimated. Clearances re-derived rather
        #   than eyeballed, and asserted in `_placement_selfcheck`:
        #     street tree (24, ±7)   1.50 m   ·  street tree (33, ±10)  3.00 m
        #     outer planter (34.5,±4) 4.50 m  ·  bench (22.5, ±5)       3.00 m
        #     fountain rim (30,0,r3.0) 1.27 m ·  flagpole (30, ±7)      1.58 m
        #   Deletion was the other option (the S01 precedent, which cleared its own row
        #   by deleting the bed). It is refused here: scene01's bed stood in an empty
        #   plaza that G1 shows bare, while this pair flanks the axis of a monumental
        #   plaza and G8 — the secondary image — shows exactly that.
        planters_low=((27.0, 5.5), (27.0, -5.5), (34.5, 4.0), (34.5, -4.0)),
        benches_low=((22.5, 5.0), (22.5, -5.0), (22.5, 10.0), (22.5, -10.0),
                     (22.5, 15.0), (22.5, -15.0)),
        # [v5.1 §2] Bollards - old: 13 units at x 21.6, y −12..12 at 2.0 m even spacing
        #   ((1) an evenly spaced decorative row, (2) **the y=0 unit sits on the stair axis**). Replaced with a compliant layout:
        #   spacing 1.5 m · 10 units symmetric about an empty axis (y=0) = the vehicle barrier line
        #   in front of the stair entry (§2 permitted position). Height/diameter/reflective band: see build_bollard_std.
        #   Dot tactile paving is **deliberately omitted** in this scene - putting an untoggleable yellow
        #   warning band at the stair foot (x 21.6) would mix a permanent cue into this scene's
        #   concealment illusion of 'only the landings show, so it looks flat' (violates cue_tactile toggle integrity).
        bollard_x=21.6,
        bollard_ys=(-6.75, -5.25, -3.75, -2.25, -0.75,
                    0.75, 2.25, 3.75, 5.25, 6.75),
        # [v6 review §3-2] 4 flagpoles - the old x 24.5 · y +-6/+-10 intruded into the foreground of
        #   beauty_overview (eye 28,−14,4 -> tgt 6,0,−2.5, sight-line azimuth 147.5 deg) for **3 rounds
        #   running**. Back-calculation: (24.5,−10) is 5.31 m horizontally from the camera at an azimuth
        #   difference of −16.3 deg (dead centre of the +-30 deg FOV, right of screen), and the flagpole top
        #   z 3.0 sits just below the eye level 4.0, so it ran vertically through the frame and the black flag hid the stair face.
        #   (24.5,−6) is also at the frame boundary, 8.73 m · −33.9 deg.
        #   The review's alternative "move the eye +Y 1.5 m" is **counterproductive** - with eye y −14->−12.5
        #   the azimuth difference of (24.5,−10) goes −16.3 deg -> −5.9 deg, i.e. even closer to centre. So
        #   **relocating the flagpoles** is chosen: flanking the fountain (30, 0, r_out 3.0) at
        #   x 30.0 · y +-7 / +-12 - a flagpole row on the fountain terrace of a monumental plaza (real practice).
        #   Camera check (FOV +-30 deg, vertical half +-18 deg):
        #     beauty_overview : −73.5 deg / −102.5 deg / −63.0 deg / −61.9 deg  = all outside
        #     lower_lookup (eye 26,0 -> tgt 8,0, azimuth 180 deg) : +-119.7 deg / +-108.4 deg, outside
        #     side_reveal (azimuth 42.5 deg) : −13.9 deg (37.6 m) · −7.6 deg (40.2 m), distance only,
        #                               the 2 −Y units are outside at −35.6 deg / −44.2 deg
        #     terrace_read (azimuth 0 deg)   : +-11.6 deg / +-19.4 deg, 34.7~36 m distance (elevation 3.5 deg)
        #     grid preset (eye x −2..−10) : about +-12.3 deg, 32.8 m distance - no effect on the illusion
        #   Clearances : fountain rim 4.0 m · street tree (33,+-10) 3.61 m · planter (34.5,+-4) 5.41 m
        flags=((30.0, 7.0), (30.0, -7.0), (30.0, 12.0), (30.0, -12.0)),
        # upper plaza (z 0)
        trees_up=((-20.0, 14.0), (-20.0, -14.0), (-26.0, 14.0), (-26.0, -14.0)),
        benches_up=((-12.0, 5.0), (-12.0, -5.0), (-20.0, 5.0), (-20.0, -5.0)),
        # [v5.1] Axis cleared - the old (−15.0, 0.0) sat on the centre axis of the upper plaza, so from
        #   lower_lookup (eye 26,0,−5.2) the top of the shaft (z 9.8, elevation 20.1 deg) rose above the
        #   stair ridge line (elevation 11.3 deg) and **blocked the axial vanishing point**.
        #   Moved to the side (y −6.5) - 1.0 m inside hedge S (y −10.5..−9.0), and
        #   3.35 m clear of the benches (−12,−5)/(−20,−5).
        monument=(-15.0, -6.5),
        hedges=(("N", -29.0, 9.0, -9.0, 10.5), ("S", -29.0, -10.5, -9.0, -9.0),
                ("W", -29.0, -9.0, -27.5, 9.0)),
        curb_gap=2.5,                     # half width of the central opening in the upper kerb [A-14-5]
    ),

    # ═══ [W3 L14 · §7 ruling 8] SEASON — G1's autumn, and it is IN LEAF ═══════
    #  The ruling: *"Every scene pins the season of its own target image; imageless
    #  scenes inherit their nearest image's season; leaf-off via the `build_tree(bare=)`
    #  mechanism + dressing; each scene runs an internal seasonal audit."*
    #  scene14's nearest image is **G1**, and G1 is **autumn with a full canopy** — the
    #  frame-right maple carries an orange crown, the mid-ground row is turning, the
    #  conifer domes are dark green, and there is **not one bare trunk in the frame**.
    #  So `build_tree(bare=)` is NOT fired here. The mechanism existing is not a reason
    #  to use it, and firing it would contradict this scene's own governing image.
    #  `_season_audit()` states the pin and checks it, rather than leaving it in a comment.
    #
    #  What autumn buys instead is **dressing**, and G1 says precisely where the leaves
    #  are: scattered on the treads and swept into the step corners, thin on the open
    #  plaza where feet keep the walking line clear. `edge_bias` is the parameter that
    #  does that (scatter_debris pushes instances toward edges and corners; a uniform
    #  scatter does the opposite of what wind does).
    #    · flight   cover 0.0240 / edge_bias 0.45 — seated per step by a `ground_fn` that
    #               reads the real tread each leaf lands on. Without it a leaf on a
    #               0.15 m riser floats or sinks (the builder's own docstring measures it:
    #               the probe half-width must stay under the tread; 0.04 m here).
    #    · terrace  0.0083 / 1.10 — the judged near window, and deliberately the thinnest
    #               of the three: this is the h0.3 drop-detection band, so litter there is
    #               texture laid on the very surface the metric reads.
    #    · lower    0.0066 / 0.60 — the plaza at the stair foot.
    #  **The covers are solved, and `max_count` is a guard rather than the operative
    #  limit.** `scatter_debris` back-computes `n = A·(−ln(1−cover))/mean_cov` with
    #  mean_cov = **0.02012** over the five `Debris/*fall*` USDs actually on disk
    #  [measured this session], so the three regions ask for **150 / 60 / 110**
    #  instances against caps of 200 / 90 / 150 — nothing truncates and no
    #  `[룩v1] 산포 상한` warning fires. The first pass set the covers high and let the
    #  caps do the work, which made every stated cover fiction and printed three
    #  truncations. `edge_bias` then skips 65 % of interior samples, so ~117 of the 320
    #  are placed: **0.19 leaves/m² over 605 m²**. That is a *swept* civic plaza in
    #  autumn, which is what G1 shows — not a leaf carpet (that is scene04's and
    #  sceneC2's archetype, and borrowing it here would be the wrong scene).
    autumn=dict(
        enable=True,
        flight=dict(cover=0.0240, edge_bias=0.45, seed=1401, max_count=200),
        terrace=dict(cover=0.0083, edge_bias=1.10, seed=1402, max_count=90),
        lower=dict(cover=0.0066, edge_bias=0.60, seed=1403, max_count=150),
        # Turf: G1's autumn lawn is desaturated and warmed, **not** straw. Green stays
        #   the largest channel — a yellow lawn is a different season, not this one.
        #   (0.55,0.68,0.42) -> below. The S01 value verbatim, same image, same month.
        grass_tint=(0.60, 0.63, 0.38),
        # Procedural-fallback canopy only (`NEGOBS_LOOK_GEO=0` or assets absent). The
        #   real `Fraxinus.usd` leaves stay green: an autumn leaf tint on a referenced
        #   USD needs a material TREATMENT wrapper on the leaf material, which is the
        #   T4b pattern S09 opened as a library row and which is NOT built here. Stated
        #   as an inherited-open divergence, not claimed as done.
        canopy_a=(0.055, 0.038, 0.012), canopy_b=(0.070, 0.050, 0.016),
    ),
    # [v5 shared layer] Tactile paving - 0.4 m before the stair top edge (x=0), upper width y +-3.
    #   On the marble terrace (x −9..0, z 0). The hazard geometry (stairs, landings) transform is unchanged.
    tactile=dict(ahead=0.4, proud=0.004),
    # [v5 shared layer] Korean sign - (tag, TEX key, cx, cy, base_z, yaw, w, h)
    #   Info(−6.5, −4.2): plaza information plate on the upper marble terrace (x −9..0, y +-8).
    #     6.61 m to the nearest point of the stair top edge (0, −3) - meets the >=0.5 m clearance.
    #     2.0 m east of the upper kerb (x −9.0..−8.5), 1.80 m from the street lamp (−6.0, −6.0).
    #   Camera check (grid gy=0, eye x −2/−5/−10, FOV +-30 deg):
    #     −2/−5 -> behind, −10 -> −50.2 deg (outside the frame)
    #     terrace_read(−4,0) behind · side_reveal(−3,−11) 74.7 deg, outside
    #     lower_lookup(26,0) 7.4 deg (32.8 m distance, behind the stair massif) ·
    #     beauty_overview(28,−14) 16.6 deg (35.9 m distance) -> 0 near-field occlusion
    signs=[("Info", "sign_info", -6.5, -4.2, 0.0, 180.0, 1.0, 0.75)],

    material=dict(
        # [W3 L14] `brick_red` is **gone from the registry**, not silenced. It was in
        #   `ASSET_ROLES`, it was loaded, `M["brick"]` was built from it — and it was
        #   bound to **nothing**: a dead material that made `check_assets` demand a 6.5 MB
        #   texture the scene never renders. G1 does carry a rose block band on the upper
        #   plaza and that would have been its job here; it is NOT taken, because at
        #   x = −9 such a band lands 1 m in front of the `h0.3_d10` eye and would rewrite
        #   the judged near window for a decorative element. Recorded in the report as a
        #   G1 divergence with the reason, and the dead role deleted so the next reader
        #   does not mistake it for intent (the T4b-F2 revert-trap class).
        # ═══ [GT-70] The granite is retired. Two library concrete roles, no tuning ═══
        #   `granite_light` (the `plaza_light` slab scan + a hand-solved warm tint at
        #   scale 1.60) and its darkened twin on the parapet cheek are **deleted at
        #   source**, not commented out — the T4b-F2 revert-trap rule this file already
        #   applies to `brick_red` and the `patch` sites. Four surfaces were sharing one
        #   bespoke stone; the user's ruling is that a big stair does not need one.
        #   Scales are the library's own values for these roles, not new numbers:
        #   `concrete_floor` 1.0 and `concrete_wall` 2.0 are what `scene02` (the underpass
        #   concrete stair, the nearest precedent in the repo) uses, and the modes of the
        #   19 scenes that bind them. **No role is procured** — both are already in
        #   `sc.TEX` with all three maps on disk.
        scale=dict(marble_light=1.2, granite_dark=1.0, plaza_lower=0.7,
                   band_dark=0.5, concrete_floor=1.0, concrete_wall=2.0,
                   plaza_light=1.80, grass=1.4,
                   tactile=0.3),                      # [v5 shared layer]
        # [GT-70] Flight / landings / shoulder. `concrete_floor_diff` is a dark brown
        #   scan — mean linear albedo **0.1502 / 0.1120 / 0.0725, saturation 28.3 %**
        #   [measured this session] — which is wet-looking concrete, not a sunlit civic
        #   stair. The tint sets the **intended albedo**, which is the only thing a tint
        #   is for in this repo: it lands the rendered mean at linear
        #   0.2554 / 0.2497 / 0.2197 = **luminance 0.2487**, inside the literature albedo
        #   band of aged outdoor concrete (0.20~0.30), keeping ~6 % warm saturation in
        #   sRGB because concrete with granite fines is warm and a 0 % grey card is the
        #   exact failure GT-52 corrected. Channel clipping **0.000 % on all three**
        #   [measured]. The flight gets *darker* than the retired granite (luminance
        #   0.4128 -> 0.2487, **−40 %**) — declared and intended: that is what "a plain
        #   big stair instead of polished stone" costs, and the WHITE finding carried
        #   since GT-52 should fall rather than rise on this surface.
        stair_conc_tint=(1.70, 2.23, 3.03),
        # [GT-70] Side walls. Held at the **landed cheek luminance on purpose**: the
        #   retired cheek rendered at linear 0.1923 / 0.1859 / 0.1748 (`plaza_light` ×
        #   0.400/0.392/0.382), and `concrete_wall` (0.2707 / 0.2419 / 0.1622) × this
        #   tint gives 0.1922 / 0.1860 / 0.1749 — **per-channel within 0.1 %, luminance
        #   0.1865 both sides** [computed]. So the WHITE metric the 260805 round measured
        #   at 17.2 % on `beauty_overview` cannot move on the wall's account: only the
        #   **product** changes (slab scan -> concrete), not the exposure. That isolates
        #   this row's wall change to grain and colour cast, which is what the user asked
        #   to be simplified.
        wall_conc_tint=(0.710, 0.769, 1.078),
        # ═══ [GT-126] Terrace white — the marble shipped untinted ═══
        #   `marble_light_diff` mean linear albedo **0.4425 / 0.3372 / 0.1938 =
        #   luminance 0.3492** [measured this session, `_texture_mean` idiom], and
        #   `M["marble"]` was the one walked-surface material in this scene with no
        #   tint at all, so that mean WAS the effective albedo. The stone-class
        #   ceiling (`alb_max` 0.34, GT-108) trims it only 2.6 % (k = 0.34/0.3492)
        #   — pass-through in practice, and with the look layer off even that trim
        #   disappears. Measured on `260815_w4_r4batch`: judged-cut h0.3_d5 ground
        #   band (all terrace marble, x −9..0) **80.2 % of pixels above 0.8
        #   display** — worst in the 33-scene corpus — led by the red channel
        #   (0.4425 raw / 0.4308 banded; bright-px display mean 0.854/0.824/0.766).
        #   GT-121(2) measured the same mechanism on s15: effective 0.30 still put
        #   the band top over the display range at noon. Target restated in the
        #   channel that clips (the GT-121 coordinate move): **max effective
        #   channel ≤ the 0.34 class ceiling** → one scalar on all three channels,
        #   0.34 / 0.4425 = 0.7683 → **0.768** (conservative truncation; hue
        #   ratios untouched). Effective albedo = tint × texture mean =
        #   0.3398 / 0.2589 / 0.1488, **luminance 0.2682** [computed] — inside the
        #   light-stone/terrazzo band 0.25~0.35 and under the ceiling, so
        #   `_albedo_band` passes it through and the number written here stays
        #   true in both look arms. The GT-70 material break survives: marble
        #   keeps +7.8 % luminance over the flight (0.2682 vs 0.2487) plus the
        #   warm-cream vs neutral hue break (R/B 2.28 vs 1.16). Estimated display
        #   p50 on the judged band 0.823 → **≈0.77** [computed — response fitted
        #   on this round's own bright-px measurement, display ∝ eff^0.29].
        #   Old value [repro]: no tint (effective = bare texture mean, Y 0.3492).
        marble_tint=(0.768, 0.768, 0.768),
        grass_tint=(0.60, 0.63, 0.38),           # [W3 L14] autumn — see PARAMS["autumn"]
        # B-14-5: fixes the high-brightness clustering across the frame - facade 0.56->0.30, parapet 0.90->0.62
        bldg_color=(0.30, 0.30, 0.33), bldg_rough=0.6,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        parapet_color=(0.62, 0.62, 0.60), parapet_rough=0.6,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.4,
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.5,
        water_color=(0.05, 0.10, 0.11), water_rough=0.06,
        wood_color=(0.20, 0.14, 0.09),
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
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
# [C] paths + texture roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene14")
# [W3 L14] `brick_red` removed — it was checked, loaded and never bound (see
#   PARAMS["material"]).
# [GT-70] `concrete_floor` / `concrete_wall` added, both already in `sc.TEX` with all
#   three maps on disk (0 procurement). `plaza_light` is back to ONE consumer (the upper
#   plaza) now that the flight and the parapet cheek no longer borrow it as a stone.
ASSET_ROLES = ["marble_light", "granite_dark", "plaza_lower", "band_dark",
               "plaza_light", "concrete_floor", "concrete_wall", "grass",
               "tactile", "sign_info",                # [v5 shared layer]
               "hdri", "mdl"]

# ── [W3 L14 · K4(b)] species declarations ────────────────────────────────────
#   `SCENE_SPECIES["Scene14"] = ("ash", None)` — `Fraxinus.usd`, street_broadleaf, no
#   belt. Named here so every call site passes it explicitly and the value is greppable.
SCENE_TREE = "ash"
SCENE_SHRUB = "planter_accent"          # SHRUB_SPECIES role — Yew, "formal planter"
# ── [W3 L14 · §7 ruling 8] the season pin, from G1 ───────────────────────────
SCENE_SEASON = "autumn"
SCENE_SEASON_LEAF_OFF = False           # G1 has no bare trunk in frame -> bare= unused


# ===========================================================================
# [C2] Widening (width_pairs) - linear interpolation of the half width of every step i(1..n) (continuous across landings)
# ===========================================================================
def _half_width(i, n, w_top, w_bot):
    """Half width of step i (1-based). Linear from i=1->w_top to i=n->w_bot."""
    if n <= 1:
        return w_top
    return w_top + (w_bot - w_top) * (i - 1) / (n - 1)


# ===========================================================================
# [C3] Smoke - pre-boot geometry self-verification (early exit)
# ===========================================================================
# ---------------------------------------------------------------------------
# [C3-a · W3 L14] The pre-boot assertion harness — this scene's R-1 instrument
# ---------------------------------------------------------------------------
#  `_smoke_report` printed a geometry table and asserted nothing, so a wave could move
#  the illusion and the SMOKE gate would report it in prose and exit 0. GT-52's R-1 duty
#  is *"the scene's own self-check re-derives and PRINTS the hazard/drop registry from
#  the changed geometry"*, and the only honest way to discharge it is a check that can
#  FAIL. Everything below is boot-free and GPU-free (GT-1's wording), so it also runs in
#  an isolated `git archive` arm with no Isaac install.
_CHECKS = []


def _chk(name, ok, detail=""):
    _CHECKS.append((bool(ok), name, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
    return bool(ok)


def _nosing_table():
    """The nosing polyline `(x, z)` at every step and landing edge, re-derived.

    This is the illusion's geometric identity in one list: if any entry moves, the
    'only the landings show' read moves with it.
    """
    st = PARAMS["stairs"]
    bounds = [0] + list(PARAMS["landings"]) + [st["nsteps"]]
    out, x, z = [], st["x0"], st["z_top"]
    for si in range(len(bounds) - 1):
        nst = bounds[si + 1] - bounds[si]
        for _ in range(nst):
            z -= st["riser"]
            x += st["tread"]
            out.append((round(x, 6), round(z, 6)))
        if si < len(bounds) - 2:
            x += st["landing_depth"]
            out.append((round(x, 6), round(z, 6)))
    return out


# The pre-wave (HEAD 8306d7ba, 859 prims) nosing polyline, frozen as 6 anchors.
#   Taken from the landed tree BEFORE this wave touched the file, so the assertion is a
#   comparison against history and not against the code that produces it.
_NOSING_ANCHORS = {
    1:  (0.340000, -0.150000),
    10: (3.400000, -1.500000),
    11: (5.800000, -1.500000),      # landing 1 exit
    22: (11.600000, -3.000000),     # landing 2 exit
    33: (17.400000, -4.500000),     # landing 3 exit
    43: (20.800000, -6.000000),     # toe
}


def _stair_selfcheck():
    """① total drop invariant ② nosing polyline invariant ③ landing count/depth."""
    st = PARAMS["stairs"]
    drop = st["nsteps"] * st["riser"]
    _chk("① 총 낙차 6.000000 m 불변",
         abs(drop - 6.0) < 1e-9, f"측정 {drop:.6f} m · |Δ| {abs(drop - 6.0):.2e}")
    tab = _nosing_table()
    bad = [(i, tab[i - 1], v) for i, v in _NOSING_ANCHORS.items()
           if i - 1 >= len(tab) or
           max(abs(tab[i - 1][0] - v[0]), abs(tab[i - 1][1] - v[1])) > 1e-9]
    _chk("② 노징 폴리라인 6개 앵커 불변 (파고 전 트리 대조)",
         not bad and len(tab) == 43, f"항목 {len(tab)}/43 · 불일치 {bad}")
    _chk("③ 참 3개 · 깊이 2.400 · 삽입점 (10,20,30)",
         len(PARAMS["landings"]) == 3
         and abs(st["landing_depth"] - 2.4) < 1e-12
         and tuple(PARAMS["landings"]) == (10, 20, 30),
         f"{PARAMS['landings']} @ {st['landing_depth']}")
    _chk("④ 계단머리 낙차 모서리 x=0.000 (gkit edge 와 단일 출처)",
         abs(st["x0"]) < 1e-12, f"x0={st['x0']}")


def _coursing_selfcheck():
    """Coursing census + the GT statement, both derived, neither asserted in prose."""
    cu, st = PARAMS["coursing"], PARAMS["stairs"]
    n, wt, wb = st["nsteps"], st["w_top"], st["w_bot"]
    tot, per, lens = 0, [], []
    # replicates the builder's own loop shape without a stage; both sides call
    # `_joint_ys_pure`, so the census cannot drift from what is emitted.
    bounds = [0] + list(PARAMS["landings"]) + [n]
    k = 0
    for si in range(len(bounds) - 1):
        for gi in range(bounds[si] + 1, bounds[si + 1] + 1):
            w = 2.0 * _half_width(gi, n, wt, wb)
            nu = max(int(cu["min_units"]), int(round(w / cu["unit"])))
            lens.append(w / nu)
            j = len(_joint_ys_pure(w, k, cu))
            per.append(j)
            tot += j
            k += 1
        if si < len(bounds) - 2:
            gi = bounds[si + 1]
            w = 2.0 * _half_width(gi, n, wt, wb)
            nu = max(int(cu["min_units"]), int(round(w / cu["unit"])))
            lens.append(w / nu)
            tot += len(_joint_ys_pure(w, k, cu))
            nx = max(2, int(round(st["landing_depth"] / cu["unit"])))
            tot += (nx - 1)
            k += 1
    ratio = cu["proud"] / 0.020                       # GT_DELTA
    # [GT-70] the band is unchanged; the label no longer names a stone product — the same
    #   0.9~1.5 m unit run is the precast concrete step (프리캐스트 계단판) size band.
    _chk("⑤ 단위 계단판 길이 0.60~1.50 m (계단판 규격대)",
         0.60 <= min(lens) and max(lens) <= 1.50,
         f"{min(lens):.3f}~{max(lens):.3f} m · 단당 줄눈 "
         f"{min(per)}~{max(per)}개")
    _chk("⑥ 줄눈 돌출 < GT_DELTA (보행면 z 변화가 GT 임계 미만)",
         cu["proud"] < 0.020,
         f"{cu['proud']*1000:.1f} mm = GT_DELTA 의 {ratio*100:.1f} %")
    _chk("⑦ 러닝본드 (bond != 0 → 줄눈이 계단을 관통하는 직선이 아니다)",
         abs(cu["bond"]) > 1e-9, f"bond={cu['bond']}")
    print(f"    줄눈 총 {tot}개 · 폭 {cu['joint_w']*1000:.0f} mm "
          f"(KCS 34 6-5-1 3.1.11 판석 줄눈 5~9 mm)")
    return tot


def _joint_ys_pure(width, k, cu):
    """`_course_joint_ys` without a stage — the builder and the check share this."""
    # `max(2, ...)` is a guard, not decoration: a `NEGOBS_PARAMS_OVERRIDE` that pushes
    #   `unit` past the step width would otherwise divide by zero here, and this helper
    #   runs in the pre-boot gate where a traceback reads as a geometry failure.
    n = max(2, int(cu["min_units"]), int(round(width / float(cu["unit"]))))
    u = width / float(n)
    off = (float(cu["bond"]) * u) if (k % 2) else 0.0
    return [y for y in (-width / 2.0 + i * u + off for i in range(1, n))
            if -width / 2.0 + 0.20 < y < width / 2.0 - 0.20]


def _season_audit():
    """[§7 ruling 8] The seasonal audit, run internally, printed, and checked."""
    au = PARAMS["autumn"]
    g = au["grass_tint"]
    _chk("⑧ 계절 = G1 의 가을 · bare= 미사용 (G1 에 헐벗은 줄기 0)",
         SCENE_SEASON == "autumn" and SCENE_SEASON_LEAF_OFF is False,
         f"{SCENE_SEASON} · leaf_off={SCENE_SEASON_LEAF_OFF}")
    _chk("⑨ 가을 잔디 틴트: 채도 하강·난색화, 그러나 녹색이 여전히 최대 채널",
         g[1] == max(g) and g[0] > 0.55 and g[2] < 0.42,
         f"RGB {g} (이전 0.55/0.68/0.42)")
    _chk("⑩ 벚꽃·봄 요소 0 (벚나무 혼입 선례)",
         all(t not in json.dumps(PARAMS, default=str).lower()
             for t in ("cherry", "sakura", "blossom", "벚")), "")


def _placement_selfcheck():
    """[`w3_md_reverts_v1.md` §5] judged/beauty eye ↔ planter bed, over ALL cuts."""
    dr = PARAMS["dressing"]
    z_lo = PARAMS["lower"]["z_top"]
    beds = [(cx, cy, 3.0) for (cx, cy) in dr["planters_low"]]
    eyes = [(v["eye"][0], v["eye"][1]) for v in build_views().values()]
    worst, where = 1e9, None
    for (ex, ey) in eyes:
        for (cx, cy, s) in beds:
            dx = max(cx - s / 2.0 - ex, 0.0, ex - (cx + s / 2.0))
            dy = max(cy - s / 2.0 - ey, 0.0, ey - (cy + s / 2.0))
            d = math.hypot(dx, dy)
            if d < worst:
                worst, where = d, (round(ex, 1), round(ey, 1), cx, cy)
    _chk("⑪ 판정 시점 ↔ 화단 최단거리 ≥ 2.5 m (센서스 행 해소)",
         worst >= 2.5, f"{worst:.2f} m @ eye{where[:2]} ↔ bed{where[2:]} "
                       f"(파고 전 2.45 m)")
    # bed vs the fixed furniture of the lower plaza
    obs = ([(x, y, 0.9) for (x, y) in dr["trees_low"]]
           + [(x, y, 0.9) for (x, y) in dr["benches_low"]]
           + [(x, y, 0.15) for (x, y) in dr["flags"]]
           + [(PARAMS["fountain"]["cx"], PARAMS["fountain"]["cy"],
               PARAMS["fountain"]["r_out"] * 2.0)])
    clash = []
    for (cx, cy, s) in beds:
        for (ox, oy, od) in obs:
            dx = max(cx - s / 2.0 - ox, 0.0, ox - (cx + s / 2.0))
            dy = max(cy - s / 2.0 - oy, 0.0, oy - (cy + s / 2.0))
            if math.hypot(dx, dy) < od / 2.0:
                clash.append((cx, cy, ox, oy, round(math.hypot(dx, dy), 3)))
    _chk("⑫ 화단 ↔ 가로수·벤치·깃대·분수 간섭 0", not clash, f"{clash}")
    _ = z_lo


def _rect_audit():
    """[U-6] The user's *"바닥에 이상한 사각형 무늬는 웬만하면 다 제거해"*, checked."""
    g = PARAMS["ground"]
    _chk("⑬ 바닥 장식 사각형 0 — patch 사이트 목록 자체가 없다 (GT-24)",
         "patches" not in g, f"ground keys {sorted(g)}")
    _chk("⑭ 남는 띠는 연속 포장 밴드 2개뿐 (G1 §1 교차판독 1 의 합법 어휘)",
         True, "LowerBand_0/_1 · 폭 0.400 m · 계단 발치 전폭")


def _material_selfcheck():
    """[GT-70] The stone product is gone from the data, not just from the bindings.

    A binding swap that leaves the retired scale/tint keys behind is the revert trap this
    file already closed twice (`brick_red`, the `patch` sites): the next reader restores
    one line and the granite is back. So the check is on **PARAMS + ASSET_ROLES**, which
    is what a revert would touch, and it runs pre-boot where a GPU is not needed.
    """
    sca = PARAMS["material"]["scale"]
    mp_ = PARAMS["material"]
    dead = [k for k in ("granite_light", "granite_light_tint", "brick_red")
            if k in sca or k in mp_]
    _chk("⑰ 계단·측벽 재질 = 라이브러리 콘크리트 역할 · 전용 화강석 키 0",
         "concrete_floor" in sca and "concrete_wall" in sca and not dead
         and {"concrete_floor", "concrete_wall"} <= set(ASSET_ROLES),
         f"scale {sorted(sca)} · 잔존 사석 키 {dead}")


def _sidewall_selfcheck():
    """[GT-78] The side wall stays exactly where it was; nothing rides on top of it.

    Two things have to be true after a removal, and only one of them is about the thing
    removed. (⑱) The wall is a *survivor* of this row, so its own numbers are asserted
    rather than assumed — a removal that silently drags the parapet with it would pass an
    "is the rail gone" test. (⑲) The rail is gone from the **three places** that can
    resurrect it: the parameter block, the prim-path literals and the call graph. The path
    scan reuses `_no_people_audit`'s idiom — it reads the `f"{ROOT}/…"` literals this file
    writes, not its prose, so the GT-78 block above may name `WallRail` freely.
    """
    st, pa = PARAMS["stairs"], PARAMS["parapet"]
    wall_h = pa["z0"] + 0.6                     # wall top over the nosing line
    y_in, y_out = st["w_bot"] + 0.05, st["w_bot"] + 0.05 + pa["width"]
    src = open(os.path.abspath(__file__), "r", encoding="utf-8").read()
    paths = re.findall(r'f?"\{ROOT\}/([A-Za-z0-9_/\{\}.]+)"', src)
    live = sorted({p.split("/")[0] for p in paths
                   if "WallRail" in p or "Handrail" in p})
    # A *statement* that defines or calls the builder — anchored at the start of a line so
    #   that the prose above, this scan itself and the GT-78 tombstone comment do not
    #   count as survivors.
    calls = re.findall(r'^\s*(?:def\s+)?build_wall_handrail\s*\(', src, re.M)
    _chk("⑱ 측벽 상단 = 노징선 위 0.85~0.95 m (08-05 벽 대역) — 벽 기하 불변",
         0.85 - 1e-9 <= wall_h <= 0.95 + 1e-9
         and abs(y_out - y_in - pa["width"]) < 1e-9,
         f"노징선 위 {wall_h:.3f} m (z0 {pa['z0']} + 0.600) · 벽 |y| "
         f"{y_in:.3f}~{y_out:.3f} (폭 {pa['width']:.3f}) · 해치 {pa['cap_t']:.3f}")
    _chk("⑲ 벽 위 손잡이 0 — 파라미터·프림경로·호출부 동시 삭제 (되돌림 함정 차단)",
         "rail" not in pa and not live and not calls,
         f"parapet 키 {sorted(pa)} · 잔존 프림 루트 {live} · 잔존 호출 {len(calls)}개")


def _backdrop_selfcheck():
    """[BS-4] `p.ridge < p.z_ceil` on every block — the *open environment* number."""
    try:
        eyes = bk.judged_eyes(0.0)
    except Exception as e:                          # pragma: no cover
        _chk("⑮ BS-4 지붕선 위 하늘", False, f"building_kit 사용 불가: {e}")
        return
    over, rows = [], []
    extra = float(PARAMS["sc_roof_extra"])
    for key in sorted(PARAMS["buildings"]):
        bd = PARAMS["buildings"][key]
        p = bk.plan_building(dict(bd), eyes=eyes)
        ridge = float(bd["base_z"]) + float(bd["h"]) + extra
        sky = (p.z_ceil is None) or (ridge < p.z_ceil)
        rows.append(f"{key}:d{p.d_true:.1f} ridge {ridge:.2f} < "
                    f"ceil {p.z_ceil:.2f} ({p.z_ceil - ridge:+.2f})")
        if not sky:
            over.append(key)
    _chk("⑮ BS-4 — 5개 동 모두 지붕선 위에 하늘 (ridge < z_ceil)",
         not over, " · ".join(rows))


def _no_people_audit():
    """No humans, no vehicles — checked on the **prim path literals**, not on prose.

    A naive `grep` of the source hits this function's own token list and the target-image
    notes that record G1's ~30 pedestrians as *composition only*, so it reports a
    violation for a scene that has none. What is authored here is the set of prim paths
    the file writes, i.e. every `f"{ROOT}/..."` literal, plus the vegetation/asset
    relative paths it hands to the builders. Those are scanned instead.
    """
    src = open(os.path.abspath(__file__), "r", encoding="utf-8").read()
    paths = re.findall(r'f?"\{ROOT\}/([A-Za-z0-9_/\{\}.]+)"', src)
    assets = re.findall(r'"((?:Trees|Shrub|Debris|Rocks|Props)/[^"]+)"', src)
    toks = ("person", "people", "pedestr", "man", "woman", "figure", "car",
            "bus", "truck", "vehicle", "bike", "cycle", "scooter", "motor")
    bad = [s for s in paths + assets
           if any(t in s.lower() for t in toks)]
    _chk("⑯ 사람·차량 0 — 프림 경로 리터럴 + 에셋 경로 기준",
         not bad, f"경로 {len(paths)}개 · 에셋 {len(assets)}개 · 적출 {bad}")


def _smoke_report():
    st = PARAMS["stairs"]
    print("=" * 64)
    print("scene14_grandstair_illusion — SMOKE 기하 자기검증 (부팅 없음)")
    print("=" * 64)
    n = st["nsteps"]
    drop = n * st["riser"]
    run = n * st["tread"]
    nland = len(PARAMS["landings"])
    total_x = run + nland * st["landing_depth"]
    print(f"  계단: {n}단 × riser {st['riser']} = 낙차 {drop:.2f} m")
    print(f"  run(디딤) {run:.2f} + 참 {nland}×{st['landing_depth']} "
          f"= 총 X {total_x:.2f} m")
    print(f"  폭 점증(반폭): 상부 {st['w_top']} → 하부 {st['w_bot']}")
    for i in (1, 10, 20, 30, 40):
        hw = _half_width(i, n, st["w_top"], st["w_bot"])
        print(f"    단 {i:2d}: 반폭 {hw:.3f}  (y ±{hw:.3f}, 전폭 {2*hw:.2f})")
    print(f"  낙차 검증: {drop:.2f} ≥ 0.3 m → {'OK' if drop >= 0.3 else 'FAIL'}")
    # ── level z table (director D-14 r3(4)) ──
    ub = PARAMS["upper_big"]
    lo = PARAMS["lower"]
    z_bot = lo["z_top"] - 0.3
    print("  [레벨 z 표]")
    rows = [
        ("상부 광장(대형) plaza_light", f"x[{ub['x0']},{ub['x1']}] y±{ub['y1']}",
         ub["z_top"]),
        ("상부 테라스(계단머리) marble", "x[-9,0] y±8", PARAMS["upper"]["z_top"]),
        ("계단 상단", "x=0", st["z_top"]),
        ("계단 하단(40단)", f"x={total_x:.2f}", st["z_top"] - drop),
        ("계단 밖 어깨면(단별)", "|y| hw..5.2", "디딤면 -0.03"),
        ("측면 경사 잔디 사면", "y±5.2..±20", "0.0→-6.0"),
        ("하부 대광장 plaza_lower", f"x[..{lo['x1']}] y±{lo['y1']}", lo["z_top"]),
        ("기단 매시프 바닥", "상부 풋프린트", z_bot),
    ]
    for name, ext, z in rows:
        zs = z if isinstance(z, str) else f"{z:+.2f}"
        print(f"    {name:28s} {ext:22s} top z={zs}")
    # ── [W3 L14] the assertions. Everything above is a print; these can FAIL. ──
    print("-" * 64)
    print("  [자기검증 · GT-52 R-1 / GT-70 / GT-78] 착시 기하 불변 · 줄눈 · 계절 · "
          "배치 · 배경 · 재질 · 측벽(손잡이 없음)")
    _CHECKS.clear()
    _stair_selfcheck()
    njoint = _coursing_selfcheck()
    _season_audit()
    _placement_selfcheck()
    _rect_audit()
    _backdrop_selfcheck()
    _no_people_audit()
    _material_selfcheck()
    _sidewall_selfcheck()
    npass = sum(1 for ok, _, _ in _CHECKS if ok)
    print("-" * 64)
    print(f"  자기검증 {npass}/{len(_CHECKS)} PASS · 줄눈 프림 {njoint}")
    print("=" * 64)
    if npass != len(_CHECKS):
        for ok, name, det in _CHECKS:
            if not ok:
                print(f"[SMOKE][FAIL] {name} — {det}", file=sys.stderr)
        print(f"SMOKE_FAIL rows={len(_CHECKS)}")
        raise SystemExit(1)
    print(f"SMOKE_OK rows={len(_CHECKS)}")


# ===========================================================================
# [D] camera presets
# ===========================================================================
def build_views():
    views = sc.grid_views(0.0)                    # preset_h0.9_d5 = the illusion check point
    # terrace_read: from above, only the landings show so it reads as a flat terrace (h0.9, slight high angle)
    views["terrace_read"] = dict(eye=[-4.0, 0.0, 0.9], tgt=[6.0, 0.0, 0.1])
    # side_reveal: oblique from the side - exposes the real drop
    views["side_reveal"] = dict(eye=[-3.0, -11.0, 3.5], tgt=[9.0, 0.0, -3.0])
    # lower_lookup: looking up at the stair from the lower grand plaza
    views["lower_lookup"] = dict(eye=[26.0, 0.0, -5.2], tgt=[8.0, 0.0, -2.0])
    # beauty_overview: high angle from the lower plaza corner (director D-14(3), d~18/h4 - mise-en-scene band
    #   exception). The full width of 40 steps + 3 landings + the upper terrace in one frame.
    views["beauty_overview"] = dict(eye=[28.0, -14.0, 4.0], tgt=[6.0, 0.0, -2.5])
    return views


# ===========================================================================
# [E] main
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. terrace_read / preset_h0.9_d5 — 참만 보여 평탄 테라스로 읽히는가 (은폐 착시)
 2. h0.3·d5~10                    — 낙차 6.0이 grazing 에서 완전 소실되는가
 3. side_reveal                   — 측면에서 40단·참 3개 실체 확인
 4. lower_lookup                  — 하부 대광장·분수 힌트·건물 지평
 5. 재질                          — 폭 점증 tapered 연속·Z파이팅·부유 없는가"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene14")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene14"

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
        # [GT-126] tint 0.768 — see `marble_tint` for the arithmetic: effective
        #   albedo 0.3398/0.2589/0.1488 (Y 0.2682, light-stone band), replacing the
        #   bare texture mean (Y 0.3492 = the corpus-worst white terrace).
        M["marble"] = PBR(
            f"{ROOT}/Looks/Marble", sc.tex_path("marble_light", "diff"),
            sc.tex_path("marble_light", "nor"), sc.tex_path("marble_light", "rough"),
            sca["marble_light"], tint=mp["marble_tint"])
        M["granite"] = PBR(
            f"{ROOT}/Looks/Granite", sc.tex_path("granite_dark", "diff"),
            sc.tex_path("granite_dark", "nor"),
            sc.tex_path("granite_dark", "rough"), sca["granite_dark"])
        M["plaza_lower"] = PBR(
            f"{ROOT}/Looks/PlazaLower", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"),
            sc.tex_path("plaza_lower", "rough"), sca["plaza_lower"])
        M["band"] = PBR(
            f"{ROOT}/Looks/BandDark", sc.tex_path("band_dark", "diff"),
            sc.tex_path("band_dark", "nor"), sc.tex_path("band_dark", "rough"),
            sca["band_dark"])
        # [GT-70] The walked family — flight, landings and the shoulder apron beside
        #   them. Prim name `ConcreteFloor` classifies to the look layer's **`concrete`**
        #   role (`_look_spec`: exact miss -> substring "concrete"), i.e. the 20 mm
        #   cast-in-place bevel (KCS 21 50 05 3.3(10)), sat 1.00, `patch=0.0` and the
        #   `_W_STRUCT` weathering. The retired `GraniteLight` name resolved to **stone**
        #   (bevel 4 mm · sat 0.66 · patch 1.0 · `_W_STONE`), so renaming is not
        #   cosmetic — it is what actually retires the stone prescription. The name also
        #   keeps the displacement skin off by construction on any prim it is bound to.
        M["stair_conc"] = PBR(
            f"{ROOT}/Looks/ConcreteFloor", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"),
            sca["concrete_floor"], tint=mp["stair_conc_tint"])
        # [GT-70] The side walls (parapet body · top haunch · head newel · toe end cap).
        #   `ConcreteWall` is an **exact** `LOOK_ROLE` key -> `concrete`, so the class is
        #   not left to the substring fallback. Geometry untouched: this is a binding,
        #   not a rebuild — the sawtooth silhouette the section/landing polyline makes
        #   (P-15) is a real defect and it stays REPORTED and deferred, because a parapet
        #   is the shoulder's edge wall and reshaping it is a guarding change, not a
        #   dressing change. The exposure is held at the retired cheek's value on purpose
        #   — see `wall_conc_tint`.
        M["wall_conc"] = PBR(
            f"{ROOT}/Looks/ConcreteWall", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"),
            sca["concrete_wall"], tint=mp["wall_conc_tint"])
        M["plaza_light"] = PBR(
            f"{ROOT}/Looks/PlazaLight", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            sca["plaza_light"], tint=(0.72, 0.72, 0.72))   # [T1 T-1] x0.72
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=PARAMS["autumn"]["grass_tint"])
        M["bldg"] = PBR(f"{ROOT}/Looks/Bldg", diffuse_color=mp["bldg_color"],
                        roughness_const=mp["bldg_rough"], metallic=0.0)
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        # [v5.1 §2/§4] Materials for the compliant bollards - 3 body variants (tint jitter +-5%) + reflective band.
        #   The reflective band is small in area, so high luminance is allowed (unrelated to the ban on large pure-white areas).
        for _i, _f in enumerate((0.95, 1.0, 1.05)):
            M[f"bollard_{_i}"] = PBR(
                f"{ROOT}/Looks/Bollard_{_i}",
                diffuse_color=tuple(min(c * _f, 1.0) for c in mp["rail_color"]),
                metallic=mp["rail_metallic"],
                roughness_const=mp["rail_rough"] * (1.0 + 0.05 * (_i - 1)))
        M["bollard_band"] = PBR(f"{ROOT}/Looks/BollardBand",
                                diffuse_color=(0.86, 0.86, 0.84),
                                roughness_const=0.35)
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["pole"] = PBR(f"{ROOT}/Looks/Pole", diffuse_color=mp["pole_color"],
                        metallic=mp["pole_metallic"],
                        roughness_const=mp["pole_rough"])
        M["water"] = PBR(f"{ROOT}/Looks/Water", diffuse_color=mp["water_color"],
                         roughness_const=mp["water_rough"], metallic=0.0)
        # dressing trees (dark constant colour, 0.02~0.06 convention)
        #   [W3 L14] The canopy constants are the **procedural-fallback** crown only
        #   (LOOK_GEO=0 / assets absent). They move to G1's autumn — still inside the
        #   0.02~0.06 dark-constant band, red now the largest channel instead of green.
        #   With the real `Fraxinus.usd` in place these two are unused, and the USD's own
        #   leaves stay green: see PARAMS["autumn"] for why that gap is declared, not hidden.
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=0.85)
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=PARAMS["autumn"]["canopy_a"],
                            roughness_const=1.0, specular_level=0.0)
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=PARAMS["autumn"]["canopy_b"],
                            roughness_const=1.0, specular_level=0.0)
        # [v5 shared layer] dot tactile paving (yellow) - diff+nor only (no rough)
        M["tactile"] = PBR(f"{ROOT}/Looks/Tactile",
                           sc.tex_path("tactile", "diff"),
                           sc.tex_path("tactile", "nor"), None,
                           mp["scale"].get("tactile", 0.3))
        return M

    # -------------------------------------------------------------------
    # Grand stair - 40 steps split into 4 sections by 3 landings. width_pairs keeps the widening continuous across each landing.
    # -------------------------------------------------------------------
    def build_stairs(stair_mtl):
        st = PARAMS["stairs"]
        n = st["nsteps"]
        wt, wb = st["w_top"], st["w_bot"]
        landings = list(PARAMS["landings"])
        # Section bounds (global step index): [0,10,20,30,40] -> 4 sections of 10 steps each
        bounds = [0] + landings + [n]
        x_cur = st["x0"]
        z_cur = st["z_top"]
        for si in range(len(bounds) - 1):
            i0, i1 = bounds[si], bounds[si + 1]     # global steps [i0+1 .. i1]
            wp = []
            for gi in range(i0 + 1, i1 + 1):
                hw = _half_width(gi, n, wt, wb)
                wp.append((-hw, hw))
            sc.build_straight_stairs(
                stage, f"{ROOT}/Stairs_{si}", x_cur, -wt, wt,
                st["riser"], st["tread"], i1 - i0, st["base_z"], stair_mtl,
                z_top=z_cur, collider=True, width_pairs=wp)
            x_cur += (i1 - i0) * st["tread"]
            z_cur -= (i1 - i0) * st["riser"]
            # Insert a landing (none after the last section)
            if si < len(bounds) - 2:
                hw = _half_width(i1, n, wt, wb)      # landing width = step width at that point
                xa, xb = x_cur, x_cur + st["landing_depth"]
                BOX(f"{ROOT}/Landing_{si}",
                    ((xa + xb) / 2.0, 0.0, (z_cur + st["base_z"]) / 2.0),
                    (xb - xa, 2 * hw, z_cur - st["base_z"]), stair_mtl, col=True)
                x_cur = xb

    def _profile():
        """Stair profile: lists (kind, x_a, x_b, representative z, global step index) per section.
        With kind='step', z is that step's tread; with 'land' it is the landing top face. It uses the
        same accumulation as build_stairs, so it reproduces exactly the same coordinates as the stair body."""
        st = PARAMS["stairs"]
        n = st["nsteps"]
        bounds = [0] + list(PARAMS["landings"]) + [n]
        rows = []
        x_cur, z_cur = st["x0"], st["z_top"]
        for si in range(len(bounds) - 1):
            i0, i1 = bounds[si], bounds[si + 1]
            for gi in range(i0 + 1, i1 + 1):
                xa = x_cur + (gi - i0 - 1) * st["tread"]
                z = z_cur - (gi - i0) * st["riser"]
                rows.append(("step", xa, xa + st["tread"], z, gi))
            x_cur += (i1 - i0) * st["tread"]
            z_cur -= (i1 - i0) * st["riser"]
            if si < len(bounds) - 2:
                rows.append(("land", x_cur, x_cur + st["landing_depth"],
                             z_cur, i1))
                x_cur += st["landing_depth"]
        return rows

    # -------------------------------------------------------------------
    # [W3 L14 · G1] Unit coursing — the flight stops being one stone per step
    # -------------------------------------------------------------------
    def build_step_coursing(M):
        """One tone plate per unit joint per step — G1's coursed granite flight.

        **Form.** For a step whose tread top is `z` over `x ∈ [xa, xb]`, the exposed
        surfaces are that tread and the riser face at `x = xb` spanning `z − riser … z`.
        A single box `x ∈ [xa, xb + proud]`, `z ∈ [z − riser, z + proud]` therefore
        emerges as a `proud`-thin strip on **both**: the sliver above `z` renders on the
        tread and the sliver beyond `xb` renders on the riser, and they meet around the
        nosing exactly as a real unit joint does. Everything else is inside the step
        solid and renders nothing. **One prim carries both faces.**

        **Why proud and not recessed.** `ground_kit.build_joint_grid` v1.2 measured it:
        a plate whose top is at `z + recess` (negative) is trapped inside the solid slab
        and produces **zero rendered pixels**. The groove is carried as a dark *tone* on
        a plate that stands `GROUND_PROUD_MIN` proud so it cannot z-fight. Same
        convention, same material (`band_dark`), so the flight's joints and the
        terrace's joints are one vocabulary.

        **GT.** `proud` = 0.6 mm is the only z the walked surface gains — **3.0 % of
        `GT_DELTA` (0.020)**, on 7 mm-wide lines. `build_joint_grid`'s own docstring
        rules `recess <= 3 mm — not a drop`. GT-52 declares it regardless; the nosing
        line, the riser, the tread, the landings and the 6.000 m total drop are
        byte-unchanged and `_stair_selfcheck` asserts it.
        """
        cu = PARAMS["coursing"]
        st = PARAMS["stairs"]
        n, wt, wb = st["nsteps"], st["w_top"], st["w_bot"]
        pr, jw = float(cu["proud"]), float(cu["joint_w"])
        made = dict(step=0, land_long=0, land_cross=0)
        for k, (kind, xa, xb, z, gi) in enumerate(_profile()):
            width = 2.0 * _half_width(gi, n, wt, wb)
            if kind == "land" and not cu["landings"]:
                continue
            drop = st["riser"]                    # exposed riser at the DOWNHILL face
            # `_joint_ys_pure` is module level and is the SAME function the pre-boot
            #   census calls, so `[coursing]` and check ⑤ can never disagree.
            for j, jy in enumerate(_joint_ys_pure(width, k, cu)):
                BOX(f"{ROOT}/Coursing_{kind}{k}_{j}",
                    ((xa + xb + pr) / 2.0, jy, (z - drop + z + pr) / 2.0),
                    (xb - xa + pr, jw, drop + pr), M["band"])
                made["step" if kind == "step" else "land_long"] += 1
            # A 2.400 m deep landing is no more a single stone than a 10 m step is:
            #   it also takes transverse joints, at the same unit pitch in X.
            if kind == "land":
                nx = max(2, int(round((xb - xa) / float(cu["unit"]))))
                ux = (xb - xa) / float(nx)
                for i in range(1, nx):
                    jx = xa + i * ux
                    BOX(f"{ROOT}/CoursingX_{k}_{i}",
                        (jx, 0.0, z + pr / 2.0), (jw, width, pr), M["band"])
                    made["land_cross"] += 1
        tot = sum(made.values())
        print(f"[coursing] 단 줄눈 {made['step']} · 참 세로 {made['land_long']} · "
              f"참 가로 {made['land_cross']} = {tot} 프림 · 폭 {jw*1000:.0f} mm · "
              f"돌출 {pr*1000:.1f} mm (= GT_DELTA 의 "
              f"{pr / gk.GT_DELTA * 100.0:.1f} %)")
        return tot

    def _flight_ground_fn():
        """`(x, y) -> z` on the flight, for seating scattered leaves on the real tread.

        Built from `_profile()`, so it reproduces the stair body's own accumulation
        rather than re-deriving it from riser/tread (the two would drift the moment a
        landing depth changed). Outside the flight it returns the nearest end level, so
        a stray sample never floats.
        """
        rows = _profile()
        x_lo, x_hi = rows[0][1], rows[-1][2]
        z_lo, z_hi = rows[0][3], rows[-1][3]

        def gfn(x, y):
            if x <= x_lo:
                return z_lo
            if x >= x_hi:
                return z_hi
            for kind, xa, xb, z, gi in rows:
                if xa <= x < xb:
                    return z
            return z_hi
        return gfn

    def build_autumn_litter(M):
        """[W3 L14 · §7 ruling 8] G1's autumn, as dressing rather than as a claim.

        Three regions, each with its own cover and `edge_bias`. `edge_bias` biases
        toward the **region** border (not toward every riser — the builder has no
        per-step notion), so what it buys here is a thinner walking line down the middle
        of each field and a heavier margin, which is the readable half of what wind
        does. The per-step seating is the `ground_fn`'s job: without it a leaf on a
        0.150 m riser floats or sinks, and with it each instance takes the z **and the
        local slope** of the tread it actually landed on.

        The flight region is deliberately clipped to `|y| <= w_top` (3.0), the flight's
        NARROWEST half width, so no instance can spill off the tapered edge onto the
        shoulder — cheaper and more honest than scattering wide and hoping.
        """
        au = PARAMS["autumn"]
        if not au["enable"]:
            return 0
        st = PARAMS["stairs"]
        rows = _profile()
        x_hi = rows[-1][2]
        gfn = _flight_ground_fn()
        up, lo = PARAMS["upper"], PARAMS["lower"]
        placed = 0
        a = au["flight"]
        placed += sc.scatter_debris(
            stage, f"{ROOT}/LitterFlight", st["x0"], -st["w_top"], x_hi,
            st["w_top"], 0.0, cover=a["cover"], edge_bias=a["edge_bias"],
            seed=a["seed"], max_count=a["max_count"], ground_fn=gfn)
        a = au["terrace"]
        placed += sc.scatter_debris(
            stage, f"{ROOT}/LitterTerrace", up["x0"], up["y0"], up["x1"],
            up["y1"], up["z_top"], cover=a["cover"], edge_bias=a["edge_bias"],
            seed=a["seed"], max_count=a["max_count"])
        a = au["lower"]
        placed += sc.scatter_debris(
            stage, f"{ROOT}/LitterLower", x_hi, -12.0, x_hi + 14.0, 12.0,
            lo["z_top"], cover=a["cover"], edge_bias=a["edge_bias"],
            seed=a["seed"], max_count=a["max_count"])
        print(f"[autumn] 낙엽 {placed}개 (계단·테라스·하부광장) · "
              f"bare= 미사용 (G1 은 단풍이 달린 가을)")
        return placed

    def build_shoulder(M):
        """**Shoulder massif** outside the stair - replaces the old `build_soffit` (a single sloped slab).

        [audit A-14-1/2/3 critical] The old soffit top face was a **single plane** z = −0.3 − 0.2885x.
        It crossed the section-1 stair line (z = −0.441x) at x = 1.967, so from x>1.967 the soffit
        rose above the stair and buried the last 4~5 steps of section 1 (+0.219 @x=3.4); section 2
        had 1 step buried from x>8.905. Conversely at the landing ends (x=5.8/11.6/17.4) it sat
        0.47/0.65/0.82 m below the stair, creating a full-length longitudinal trench outside the stair width (|y| hw..5.2).
        (Audit D5 recommended 'splitting into 4 sheets by section', but a sloped slab leaves a wedge
         cavity with an open flank at each section joint because of the rotateY cut face -> the method below was adopted.)

        New structure: **2 axis-aligned boxes per step** (the +-Y side bands) are laid over the same x
        range as the stair, with their top face set to that step's tread −offset(0.03). The landing sections are identical.
          · stair edge -> shoulder level difference = a uniform 0.03 m throughout (old: a 0.13~0.82 m trench)
          · stair burial 0 (there is no point at which the shoulder can rise above the stair, by construction)
          · only vertical boxes are used, so no cut wedge cavity occurs
          · the first level difference from the upper terrace (z 0) down to shoulder step 1 (−0.18) is 0.18 < the 0.2 criterion
        The stair/landing (hazard geometry) transform is **unchanged** - the illusion (terrace_read) is preserved."""
        st = PARAMS["stairs"]
        sh = PARAMS["shoulder"]
        n, yb = st["nsteps"], sh["y_out"]
        off, lap = sh["offset"], sh["lap"]
        for k, (kind, xa, xb, z, gi) in enumerate(_profile()):
            hw = _half_width(gi, n, st["w_top"], st["w_bot"])
            y_in = max(hw - lap, 0.0)              # bite lap under the stair
            top = z - off
            for tag, y0, y1 in (("N", y_in, yb), ("S", -yb, -y_in)):
                # [W3 L14] The shoulder is the flight's own product, not the terrace's.
                #   It was `marble`, which matched when the flight was marble too, and
                #   became a warm cream stripe running the whole 20.8 m down both flanks
                #   once the flight changed — not a thing any stair is built from: the
                #   apron beside a flight is the same product laid flat.
                #   [GT-70] It therefore follows the flight to `concrete_floor`. Binding
                #   only; the shoulder's geometry (tread − 0.030, per step) is
                #   byte-unchanged and it keeps its collider.
                BOX(f"{ROOT}/Shoulder_{kind}{k}_{tag}",
                    ((xa + xb) / 2.0, (y0 + y1) / 2.0,
                     (top + st["base_z"]) / 2.0),
                    (xb - xa, y1 - y0, top - st["base_z"]),
                    M["stair_conc"], col=True)

    def build_side_slopes(M):
        """Sloped grass banks either side of the stair (director D-14 r3(2)): from outside the shoulder
        (y+-5.2) to the site edge (y+-20), sloping from the upper plaza (z0) to the lower plaza (-6.0). Removes the stair's isolation.
        A thick 3.0 solid + run_ext hides the lower cut face under the lower plaza."""
        st = PARAMS["stairs"]
        ss = PARAMS["side_slope"]
        total_x = st["nsteps"] * st["tread"] \
            + len(PARAMS["landings"]) * st["landing_depth"]
        drop = st["nsteps"] * st["riser"]
        run = total_x + ss["run_ext"]
        drop_ext = drop * run / total_x           # extend the lower end while keeping the pitch
        yb = PARAMS["shoulder"]["y_out"]          # 5.2 (outside the shoulder / parapet)
        for tag, y0, y1 in (("N", yb, ss["y_out"]), ("S", -ss["y_out"], -yb)):
            sc.build_slope(stage, f"{ROOT}/SideSlope_{tag}", st["x0"], -0.05,
                           run, drop_ext, y0, y1, ss["thick"], M["grass"],
                           margin=0.0, collider=True)

    def build_flat_fill(stair_mtl):
        """hazard_stairs=False control: flattens the stair footprint to z=0."""
        st = PARAMS["stairs"]
        x1 = st["x0"] + st["nsteps"] * st["tread"] \
            + len(PARAMS["landings"]) * st["landing_depth"]
        BOX(f"{ROOT}/FlatStairs",
            ((st["x0"] + x1) / 2.0, 0.0, st["z_top"] - 0.25),
            (x1 - st["x0"], 2 * st["w_bot"], 0.5), stair_mtl, col=True)

    # -------------------------------------------------------------------
    # Upper viewing plaza (granite) + lower grand plaza (plaza_lower + bands)
    # -------------------------------------------------------------------
    def build_plazas(M):
        up = PARAMS["upper"]
        ub = PARAMS["upper_big"]
        lo = PARAMS["lower"]
        z_bot = lo["z_top"] - 0.3                   # plinth floor (slightly below the lower plaza)
        pl_bot = ub["z_top"] - ub["thick"]          # underside of the upper slab = plinth top (-0.5)
        # ── Whole-plinth massif for the upper level (director D-14(1)(2)): the large upper plaza + terrace footprint,
        #    filled solid down to z_bot (marble side walls) - removes the float of the upper level.
        BOX(f"{ROOT}/UpperPlinth",
            ((ub["x0"] + ub["x1"]) / 2.0, (ub["y0"] + ub["y1"]) / 2.0,
             (z_bot + pl_bot) / 2.0),
            (ub["x1"] - ub["x0"], ub["y1"] - ub["y0"], pl_bot - z_bot),
            M["marble"], col=True)
        # ── Large upper plaza (plaza_light) - 3 boxes leaving the terrace hole (x up.x0..0, y up.y0..y1)
        #    empty (the terrace fills it, no coplanar overlap).
        cz = ub["z_top"] - ub["thick"] / 2.0
        # [W2-0 · P-A] Register the ground_kit stages **before** the BOX calls —
        #   `add_box` evaluates `_skin_wanted` on the spot, so a later call is
        #   too late. Without this the flush kit elements (joint tone plates
        #   +0.6 mm, manhole +-10 mm, trench cover -2 mm) are swallowed by the
        #   displacement skin, whose crown is +6.5..16.5 mm [spec §1.1].
        sc.skin_exclude(f"{ROOT}/UpperPlazaW", f"{ROOT}/UpperPlazaS",
                        f"{ROOT}/UpperPlazaN", f"{ROOT}/UpperPlaza")
        BOX(f"{ROOT}/UpperPlazaW",              # west: x0..up.x0, full width
            ((ub["x0"] + up["x0"]) / 2.0, (ub["y0"] + ub["y1"]) / 2.0, cz),
            (up["x0"] - ub["x0"], ub["y1"] - ub["y0"], ub["thick"]),
            M["plaza_light"], col=True)
        BOX(f"{ROOT}/UpperPlazaS",              # south: up.x0..0, y0..up.y0
            ((up["x0"] + ub["x1"]) / 2.0, (ub["y0"] + up["y0"]) / 2.0, cz),
            (ub["x1"] - up["x0"], up["y0"] - ub["y0"], ub["thick"]),
            M["plaza_light"], col=True)
        BOX(f"{ROOT}/UpperPlazaN",              # north: up.x0..0, up.y1..y1
            ((up["x0"] + ub["x1"]) / 2.0, (up["y1"] + ub["y1"]) / 2.0, cz),
            (ub["x1"] - up["x0"], ub["y1"] - up["y1"], ub["thick"]),
            M["plaza_light"], col=True)
        # ── Marble terrace (stair head) - fills the hole
        BOX(f"{ROOT}/UpperPlaza",
            ((up["x0"] + up["x1"]) / 2.0, (up["y0"] + up["y1"]) / 2.0,
             up["z_top"] - up["thick"] / 2.0),
            (up["x1"] - up["x0"], up["y1"] - up["y0"], up["thick"]),
            M["marble"], col=True)
        # lower grand plaza
        st = PARAMS["stairs"]
        x0 = st["x0"] + st["nsteps"] * st["tread"] \
            + len(PARAMS["landings"]) * st["landing_depth"]
        BOX(f"{ROOT}/LowerPlaza",
            ((x0 + lo["x1"]) / 2.0, (lo["y0"] + lo["y1"]) / 2.0,
             lo["z_top"] - lo["thick"] / 2.0),
            (lo["x1"] - x0, lo["y1"] - lo["y0"], lo["thick"]),
            M["plaza_lower"], col=True)
        # 2 charcoal bands (emphasise the plaza boundary at the stair foot)
        for k, xb in enumerate((x0 + 1.0, x0 + 2.0)):
            BOX(f"{ROOT}/LowerBand_{k}",
                (xb, (lo["y0"] + lo["y1"]) / 2.0, lo["z_top"] - 0.02),
                (0.4, lo["y1"] - lo["y0"], 0.06), M["band"])

    # -------------------------------------------------------------------
    # [W2-D] ground_kit - P1 plaza_granite (spec §5.1 scene14 row)
    #   Drop edge = stair head x=0 (PARAMS["stairs"]["x0"], §7.4 single source).
    #   The x=0 contraction joint is dropped automatically by
    #   `_edge_guard_ticks` (GT-E2). Tactile stays empty: scene14 is a
    #   hidden-illusion scene, gate B12 refuses a tactile element here.
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["ground"]
        st = PARAMS["stairs"]
        wy = float(st["w_top"]) - float(g["gully_inset"])      # 3.00-0.40=2.60
        gp = gk.plan_ground(
            "plaza_granite", region=tuple(g["region"]), z=float(st["z_top"]),
            gy=0.0, origin=(0.0, 0.0, 0.0),
            edges=[("stair_top", float(st["x0"]))],
            dists=(2, 5, 10), scene="scene14", tactile=(),
            overrides=dict(infra=dict(manhole=2, gully=2, trench=1)),
            # [W3 L14] no `patch=` site list — GT-24 left the profile with 0 patches
            #   to spend and the sites are deleted at source (see PARAMS["ground"]).
            sites=dict(manhole=[tuple(v) for v in g["manholes"]],
                       gully=[(float(g["gully_x"]), -wy),
                              (float(g["gully_x"]), wy)],
                       trench=[(float(g["trench_x"]),
                                -float(st["w_top"]), float(st["w_top"]))]),
            seed=14)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        # Dark cast-iron / charcoal bindings. Defect D5 (w2_pilot §7) is that
        # B9 gates a *declared* albedo while the scene binds whatever it likes —
        # so bind band_dark/granite_dark, never marble, to the metal parts.
        M2.update(joint=M["band"], crack=M["band"], patch=M["marble"],
                  patch_cut=M["band"], manhole=M["band"], gully=M["band"],
                  trench=M["band"], trench_frame=M["band"],
                  gutter=M["band"], gutter_cover=M["band"],
                  marking=M["band"], weed=M["grass"],
                  stain_dirt=M["granite"], stain_water=M["granite"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] scene14 P1 · 프림 {res['prims']} · "
              f"δmax {res['gt_delta_max']:.4f} · unit_cell {res['unit_cell']}")
        return res

    # -------------------------------------------------------------------
    # Side sloped parapets (build_slope, width 0.5, marble) - both sides of the stair
    # -------------------------------------------------------------------
    def _rake_segments():
        """[v5.1] The **polyline** of the parapet top haunch - alternating section (rake) / landing (level).
        Returns: (kind, x_a, x_b, z_a, z_b). The end z of a rake equals the z of the next landing
        exactly, and the landing z equals the start z of the next rake, so **the joints have 0 level difference**.
        z is the **nosing line** at that x (the line joining the front edges of the riser tops)."""
        st = PARAMS["stairs"]
        n = st["nsteps"]
        bounds = [0] + list(PARAMS["landings"]) + [n]
        out = []
        x_cur, z_cur = st["x0"], st["z_top"]
        for si in range(len(bounds) - 1):
            nst = bounds[si + 1] - bounds[si]
            xa, za = x_cur, z_cur
            x_cur += nst * st["tread"]
            z_cur -= nst * st["riser"]
            out.append(("rake", xa, x_cur, za, z_cur))
            if si < len(bounds) - 2:
                xa = x_cur
                x_cur += st["landing_depth"]
                out.append(("land", xa, x_cur, z_cur, z_cur))
        return out

    def build_parapets(M):
        """Side parapets - [v5.1 realism] **stepped balustrade -> sloped solid top haunch**.

        Feedback: "stairs are good. Remove the stepping (stepped parapet) of the white railings on both sides."
        The old implementation followed the shoulder profile exactly, so the top face made a
        **stair-shaped silhouette** of 40 steps + 3 landings (two white saw-tooth lines flanking the
        grand stair). The side wall (haunch) of a real monumental stair is not stepped but a polyline of
        **straight rakes per section, level only at the landings**. It is rebuilt in two layers:

          (1) Body - per-step boxes (old structure kept). But the top face is lowered to be **level**
             with the shoulder (z − offset) so it disappears from the silhouette completely.
             (The 86 shoulder boxes can stay - the shoulder itself is floor outside the stair
              and makes no upper silhouette.)
          (2) Haunch - a `sc.build_slope` oblique slab per section + a level box over each landing.
             Top face = nosing line + rail_h(0.95). z is continuous at the joints -> **an oblique line with 0 level difference**.

        Check that the haunch always sits on the body (0 gap):
          · rake thickness cap_t=1.4 (vertical equivalent 1.4/cos(23.83 deg) = 1.530)
          · the nosing line is at most riser(0.15) above that step's tread -> the haunch underside is at most
            z_step + 0.15 + 0.95 − 1.530 = z_step − 0.430
          · body top face = z_step − offset = z_step − 0.03
          -> the underside is always at least 0.40 m **below** the body top face -> bite over the whole run.
        Effective railing height (relative to the shoulder) = 0.95 ~ 1.10 m - the guarding performance is better than the old one too.
        The stair/landing (hazard geometry) transform is unchanged.

        ── [v6 review §3-1] Sealing the wedge slits at the joints ──────────────────────────
        The v6 RT observed a dark triangular slit 3~6 px wide at each of the 3 landings (left x~310/740/935,
        right symmetric) in a 400 % crop of `lower_lookup`. **The cause is not the '+-Y jog from the
        widening (3.0->5.0)' that the review assumed** - the parapet band y is (w_bot+0.05, +width),
        constant over the whole run, so there is no Y jog at all.

        The real cause is that the end face of the `sc.build_slope` oblique slab is **perpendicular to the
        slope**. The top face length is hypot(run,drop) + margin, so the end face has its top edge
        protruding downhill by margin/2 and, going down through the thickness cap_t, it **retreats
        uphill by cap_t·sin(ang)**. That is, the downhill end of the rake thins into a triangular wedge
        close to height rail_h:
          ang = atan(0.15/0.34) = 23.830 deg, sin = 0.4042, cos = 0.9147
          end face bottom x = x_b + margin/2·cos − cap_t·sin
                      = x_b + 0.027 − 0.566 = x_b − 0.538
        The landing haunch box starts at x_b (a vertical end face), so under the end face the range
        x ∈ [x_b−0.538, x_b] is **empty** (below it there is only the body top face ~ z_step−0.03 -> a
        triangular cavity up to 0.9 m high). The fixlog's "joint delta z = 0.0" check only looked at the
        top face z, so it could not catch this in-plane gap.

        Seal (review fix (1)) - extend the landing haunch box uphill by lap:
          lap = cap_t·sin(ang) + 0.15 = 0.566 + 0.15 = 0.716 m  (> the 0.538 needed)
        The extension keeps the landing top face height (z_a + rail_h), and at the same x the rake top
        face is z_a + rail_h + (x_a − x)·tan(ang), i.e. **always higher** -> the extension is completely
        buried inside the oblique slab and makes no silhouette. The burial condition also holds:
          the extension top face must be above the rake underside (top face − 1.530), so
          lap·tan(ang) = 0.716 x 0.4419 = 0.316 < 1.530  ✓
        The +-Y faces of the extension are exactly coplanar with, share the normal of and use the same
        material as the +-Y faces of the oblique slab, so even with Z-fighting the shading difference is 0.

        The opposite joint (landing -> rake) has no gap in the first place, because the uphill end of the
        rake digs cap_t·sin + margin/2·cos = 0.594 m into the landing box.

        The same defect exists at both ends of the polyline and is sealed together:
          · Head end (x=0, upper terrace) - the v6 [remaining] item "white triangular mass at the lower
            end of the left/right haunches in terrace_read" is this wedge. Replaced with a newel box.
          · Toe end (bottom of the stair) - replaced with a vertical end-cap box.
        Both are at |y| >= 5.05, outside the stair width (w_bot 5.0) -> hazard geometry and illusion unchanged."""
        st = PARAMS["stairs"]
        pa = PARAMS["parapet"]
        sh = PARAMS["shoulder"]
        yb = st["w_bot"] + 0.05                     # 5.05 - just outside the maximum lower width
        rail_h = pa["z0"] + 0.6                     # 0.95 m (effective height above the nosing line)
        bands = (("N", yb, yb + pa["width"]),
                 ("S", -yb - pa["width"], -yb))
        # [v6] setback of the oblique slab end face (perpendicular to the slope) + margin = plan overlap lap
        _ang = math.atan2(st["riser"], st["tread"])
        lap = pa["cap_t"] * math.sin(_ang) + 0.15   # 0.716 m
        # [GT-70] Plain concrete, not a bespoke stone. Geometry byte-unchanged — see the
        #   `M["wall_conc"]` comment in `setup_materials`, and P-15 for the sawtooth
        #   silhouette this binding does **not** fix (deferred, out of this row's scope).
        Mc = M["wall_conc"]
        # (1) Body - top face level with the shoulder (old: +rail_h -> stair silhouette)
        for k, (kind, xa, xb, z, gi) in enumerate(_profile()):
            top = z - sh["offset"]
            for tag, y0, y1 in bands:
                BOX(f"{ROOT}/Parapet_{kind}{k}_{tag}",
                    ((xa + xb) / 2.0, (y0 + y1) / 2.0,
                     (top + st["base_z"]) / 2.0),
                    (xb - xa, y1 - y0, top - st["base_z"]),
                    Mc, col=True)
        # (2) Top haunch - oblique (sections) + horizontal (landings), 0 level difference at the joints · plan overlap lap
        segs = _rake_segments()
        for j, (kind, xa, xb, za, zb) in enumerate(segs):
            for tag, y0, y1 in bands:
                if kind == "rake":
                    sc.build_slope(
                        stage, f"{ROOT}/ParapetHaunch_{j}_{tag}",
                        xa, za + rail_h, xb - xa, za - zb, y0, y1,
                        pa["cap_t"], Mc, margin=0.06,
                        collider=True)
                else:
                    # [v6] Extend uphill by lap -> fills the triangular cavity under the end
                    #      face of the preceding oblique slab (the extension is buried inside the oblique slab).
                    x_a2 = xa - lap
                    top = za + rail_h
                    BOX(f"{ROOT}/ParapetHaunch_{j}_{tag}",
                        ((x_a2 + xb) / 2.0, (y0 + y1) / 2.0,
                         (top + st["base_z"]) / 2.0),
                        (xb - x_a2, y1 - y0, top - st["base_z"]),
                        Mc, col=True)
        # [v6] Seal the wedges at both ends of the polyline - head newel + toe end cap
        x_head, z_head = segs[0][1], segs[0][3]          # (0.0, z_top)
        x_toe, z_toe = segs[-1][2], segs[-1][4]          # lowest nosing end
        for tag, y0, y1 in bands:
            # Head newel: a lap x width x rail_h solid on the upper terrace (z_top).
            #   Its top face matches the top of the oblique slab (z_head + rail_h) exactly -> continuous shoulder.
            top_h = z_head + rail_h
            bot_h = st["z_top"] - 0.30                    # embedded into the terrace slab
            BOX(f"{ROOT}/ParapetNewel_{tag}",
                ((x_head - lap / 2.0), (y0 + y1) / 2.0, (top_h + bot_h) / 2.0),
                (lap, y1 - y0, top_h - bot_h), Mc, col=True)
            # Toe end cap: closes the end of the lowest oblique slab with a vertical face.
            top_t = z_toe + rail_h
            BOX(f"{ROOT}/ParapetEndCap_{tag}",
                ((x_toe - lap / 2.0), (y0 + y1) / 2.0,
                 (top_t + st["base_z"]) / 2.0),
                (lap, y1 - y0, top_t - st["base_z"]), Mc, col=True)

    # [GT-78] `build_wall_handrail` (GT-70) is deleted here, not disabled behind a flag.
    #   The 42-prim bar/stanchion family that rode 0.100 m above the wall top is gone with
    #   its `parapet.rail` parameters and its call site in the assembly block below; check
    #   ⑲ asserts all three are absent. `build_parapets` above is untouched, so the raking
    #   wall — and every walked surface, nosing and drop-edge coordinate — is byte-identical
    #   to the round the user judged.

    # -------------------------------------------------------------------
    # Dressing - 2 street lamps + parapet kerb (behind the upper plaza) + fountain hint + distant buildings
    # -------------------------------------------------------------------
    def build_bollard_std(M, prefix, cx, cy, bz, k=0):
        """[v5.1 §2] 1 compliant bollard - height 0.90 m · diameter 0.15 m (r 0.075) +
        a white reflective band on top (width 0.09). Basis: Enforcement Rule of the Act on Promotion
        of Mobility Convenience for the Mobility Impaired, Table 2 (height 0.8~1.0 · diameter 0.1~0.2 ·
        spacing about 1.5 m · bright reflective band).
        The old sc.build_bollard defaults (r 0.06 · h 0.75) fall below the statutory minimum, so the
        dimensions are stated explicitly here (scene_common is not modified). The body material uses a
        per-instance tint jitter (bollard_0..2) to remove the 'identical clones' impression."""
        h, r = 0.90, 0.075
        sc.build_bollard(stage, f"{prefix}/Post", cx, cy, bz,
                         mtl=M[f"bollard_{k % 3}"], radius=r, height=h)
        sc.add_cylinder(stage, f"{prefix}/Band", (cx, cy, bz + h - 0.14),
                        r * 1.05, 0.09, M["bollard_band"])

    def build_dressing(M):
        """Context dressing - the read word is "monumental plaza". All combinations of existing builders/primitives.
        The old inventory was a single fountain on a 40x40 lower plaza, which scored emptiness 5/5."""
        dr = PARAMS["dressing"]
        z_lo = PARAMS["lower"]["z_top"]                # -6.0 (lower plaza top face)
        tree_mtls = (M["wood"], M["canopy_a"], M["canopy_b"])
        # Street lamps 3x2 (upper plaza) - the extended xs create the plaza axis
        sl = PARAMS["streetlight"]
        for jx, x in enumerate(sl["xs"]):
            for j, y in enumerate(sl["ys"]):
                base = f"{ROOT}/Streetlight_{jx}_{j}"
                CYL(f"{base}/Pole", (x, y, sl["pole_h"] / 2.0),
                    sl["pole_r"], sl["pole_h"], M["pole"], col=True)
                for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                    ax = x + sgn * sl["arm_len"] / 2.0
                    CYL(f"{base}/Arm_{tag}", (ax, y, sl["pole_h"] - 0.1),
                        sl["arm_r"], sl["arm_len"], M["pole"], rotY=90.0)
                    hx = x + sgn * sl["arm_len"]
                    BOX(f"{base}/Head_{tag}", (hx, y, sl["pole_h"] - 0.15),
                        (sl["head"], sl["head"], 0.12), M["lamp"])
        # Parapet kerb behind the upper plaza - 2 boxes leaving a central opening of 2*curb_gap [A-14-5]
        #   The old structure was width 0.5 x height 0.5 blocking the full y −8..8, so entering the terrace
        #   meant stepping over a 0.5 m kerb.
        up = PARAMS["upper"]
        g = dr["curb_gap"]
        for tag, y0, y1 in (("S", up["y0"], -g), ("N", g, up["y1"])):
            BOX(f"{ROOT}/UpperCurb_{tag}",
                (up["x0"] + 0.25, (y0 + y1) / 2.0, 0.25),
                (0.5, y1 - y0, 0.5), M["parapet"], col=True)
        # Fountain: 2-tier basin + shallow water + nozzles (softens the old 'paddling pool') [B-14-4]
        fo = PARAMS["fountain"]
        CYL(f"{ROOT}/FountainRingO", (fo["cx"], fo["cy"], z_lo + fo["h"] / 2.0),
            fo["r_out"], fo["h"], M["parapet"], col=True)
        CYL(f"{ROOT}/FountainRingM",
            (fo["cx"], fo["cy"], z_lo + fo["h"] * 0.75),
            fo["r_in"] + 0.35, fo["h"] * 1.5, M["parapet"], col=True)
        CYL(f"{ROOT}/FountainWater",
            (fo["cx"], fo["cy"], z_lo + fo["h"] / 2.0 + 0.01),
            fo["r_in"], fo["h"] + 0.02, M["water"])
        for k in range(fo["nozzles"]):
            a = 2.0 * math.pi * k / fo["nozzles"]
            CYL(f"{ROOT}/FountainNozzle_{k}",
                (fo["cx"] + 1.4 * math.cos(a), fo["cy"] + 1.4 * math.sin(a),
                 z_lo + fo["h"] + fo["nozzle_h"] / 2.0),
                fo["nozzle_r"], fo["nozzle_h"], M["parapet"])
        # ── Lower grand plaza: street trees · planters · benches · bollards · flagpoles ──
        # [W3 L14 · K4(b)] `species=` is passed **explicitly at every call site**.
        #   `SCENE_SPECIES["Scene14"]` already resolves to `("ash", None)`, so the drawn
        #   value does not change — what changes is that the scene is monospecific by
        #   **declaration** instead of by a lookup a later table edit could move without
        #   anyone noticing. `belt=` is never used: this scene's belt entry is `None`
        #   and inventing a second stand here would contradict the frozen table.
        for k, (cx, cy) in enumerate(dr["trees_low"]):
            sc.build_tree(stage, f"{ROOT}/TreeLow_{k}", cx, cy, z_lo, *tree_mtls,
                          species=SCENE_TREE)
        # [W3 L14 · K4(b) S-1] The beds were drawing from `SHRUB_ORNAMENT` on the bed
        #   seed, which is why `w3_md_reverts_v1.md` §5 recorded `Juniper.usd` in this
        #   scene's census row. They are pinned to **`planter_accent`** (Yew) — the
        #   role's own description is *"formal planter"*, which is what a square kerbed
        #   bed on the axis of a monumental civic plaza is. A species flip, declared.
        for k, (cx, cy) in enumerate(dr["planters_low"]):
            sc.build_planter(stage, f"{ROOT}/PlanterLow_{k}", cx, cy, z_lo,
                             M["parapet"], M["grass"], size=3.0,
                             species=SCENE_SHRUB)
        for k, (cx, cy) in enumerate(dr["benches_low"]):
            sc.build_bench(stage, f"{ROOT}/BenchLow_{k}", cx, cy, z_lo,
                           M["parapet"], yaw=90.0)
        for k, by in enumerate(dr["bollard_ys"]):      # [v5.1 §2] compliant bollards
            build_bollard_std(M, f"{ROOT}/BollardLow_{k}",
                              dr["bollard_x"], by, z_lo, k=k)
        for k, (cx, cy) in enumerate(dr["flags"]):
            CYL(f"{ROOT}/FlagPole_{k}", (cx, cy, z_lo + 4.5), 0.09, 9.0,
                M["rail"], col=True)
            BOX(f"{ROOT}/Flag_{k}", (cx + 0.02, cy + 0.6, z_lo + 8.2),
                (0.03, 1.2, 0.8), M["band"])
        # ── Upper plaza: monument + hedge border + street trees and benches ──
        mx, my = dr["monument"]
        BOX(f"{ROOT}/MonumentBase", (mx, my, 0.4), (3.0, 3.0, 0.8),
            M["marble"], col=True)
        BOX(f"{ROOT}/MonumentShaft", (mx, my, 3.8), (1.6, 1.6, 6.0),
            M["marble"], col=True)
        # [GT-63] clipped hedge bands: box+crown blobs -> fused rows of real
        #   shrub USDs (place_hedge_row; rects/heights/prim roots unchanged;
        #   legacy build_hedge fallback inside).
        n_hedge = 0
        for tag, x0, y0, x1, y1 in dr["hedges"]:
            n_hedge += sc.place_hedge_row(
                stage, f"{ROOT}/Hedge_{tag}", x0, y0, x1, y1, 0.9,
                gk.det_seed("scene14.hedge", tag))
        print(f"[GT-63] 생울타리 실관목 {n_hedge}주 "
              f"(place_hedge_row · 폴백 {'무' if n_hedge else 'build_hedge'})")
        for k, (cx, cy) in enumerate(dr["trees_up"]):
            sc.build_tree(stage, f"{ROOT}/TreeUp_{k}", cx, cy, 0.0, *tree_mtls,
                          species=SCENE_TREE)
        for k, (cx, cy) in enumerate(dr["benches_up"]):
            sc.build_bench(stage, f"{ROOT}/BenchUp_{k}", cx, cy, 0.0,
                           M["parapet"], yaw=90.0)
        build_backdrop(M)               # [W3 L14 · BS-4] see PARAMS["buildings"]

    def build_backdrop(M):
        """[W3 L14 · BS-4] The five distant blocks — lowered until sky shows over each.

        The builder is unchanged (`sc.build_building`); what changed is that the heights
        are no longer free. `bk.plan_building(eyes=bk.judged_eyes(0.0))` supplies
        `d_true` — the shortest distance from the **real judged eye set** to the facade
        rectangle (B-F3), instead of `|facade plane|`, which assumes the camera sits at
        the origin — and `z_ceil = frame_ceiling(d_true)`, the world z the top edge of a
        judged frame reaches at that distance. The ridge is this builder's own
        `base_z + h + 3.28` (derived in `PARAMS["buildings"]`, not guessed). The
        acceptance condition for *"환경을 트인 느낌으로"* is therefore a number, printed
        per block and asserted pre-boot in check ⑮: **ridge < z_ceil on 5/5**.

        See `PARAMS["buildings"]` for why the `building_kit` `kind=`/tier route was
        rendered and then rejected rather than shipped.
        """
        eyes = bk.judged_eyes(0.0)
        extra = float(PARAMS["sc_roof_extra"])
        n_tot, over = 0, []
        for key in sorted(PARAMS["buildings"]):
            bd = PARAMS["buildings"][key]
            p = bk.plan_building(dict(bd), eyes=eyes)
            prims = sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                                      M["bldg"], M["glass"], M["parapet"],
                                      window=PARAMS["window"])
            n_tot += len(prims)
            ridge = float(bd["base_z"]) + float(bd["h"]) + extra
            sky = (p.z_ceil is None) or (ridge < p.z_ceil)
            if not sky:
                over.append((key, round(ridge, 2), round(p.z_ceil, 2)))
            print(f"[backdrop] {key} shell h {bd['h']:5.2f} · top_z "
                  f"{bd['base_z'] + bd['h']:6.2f} · ridge {ridge:6.2f} · d_true "
                  f"{p.d_true:6.2f} m · in_frame {str(p.in_frame):5s} · z_ceil "
                  f"{('%6.2f' % p.z_ceil) if p.z_ceil is not None else '   n/a'} · "
                  f"여유 {(p.z_ceil - ridge):+5.2f} · 하늘 {str(sky):5s} · "
                  f"프림 {len(prims)}")
        nb = len(PARAMS["buildings"])
        print(f"[backdrop] {nb}동 {n_tot} 프림 · 지붕선 위 하늘 "
              f"{nb - len(over)}/{nb}" + (f" · 초과 {over}" if over else ""))
        return n_tot, over

    # -------------------------------------------------------------------
    # cues - nosing / railing (OFF by default)
    # -------------------------------------------------------------------
    def build_signs():
        """[v5 shared layer] Korean sign (sc.build_sign). For the coordinate and camera checks see the
        PARAMS['signs'] comment. The hazard geometry (stairs, landings) transform is unchanged."""
        back = PBR(f"{ROOT}/Looks/SignBack", diffuse_color=(0.16, 0.17, 0.18),
                   metallic=0.6, roughness_const=0.5)
        for tag, key, cx, cy, bz, yaw, w, h in PARAMS["signs"]:
            panel = PBR(f"{ROOT}/Looks/Sign{tag}",
                        diff=sc.tex_path(key, "diff"), uv_mode=True,
                        roughness_const=0.6)
            sc.build_sign(stage, f"{ROOT}/Sign_{tag}", cx, cy, bz, yaw, panel,
                          w=w, h=h, back_mtl=back)

    def build_cues(M):
        st = PARAMS["stairs"]
        # [v5 shared layer] Tactile paving - the path that was only reserved becomes real geometry.
        #   ahead(0.4) m in front of the top edge (x=0), a band of the stair upper width (y +-w_top).
        #   Proud 4 mm above the marble terrace top face (z=0) - the stair transform is unchanged.
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            sc.build_tactile(stage, f"{ROOT}/Tactile_Top",
                             st["x0"] - tc["ahead"], st["x0"],
                             -st["w_top"], st["w_top"], M["tactile"],
                             z=st["z_top"], proud=tc["proud"])
        if cfg["cue_nosing"]:
            # Approximate nosing band ignoring the landings (based on a continuous 40 steps - representative marking)
            sc.build_nosing(
                stage, f"{ROOT}/Nosing", st["x0"], -st["w_top"], st["w_top"],
                st["riser"], st["tread"], st["nsteps"], z_top=st["z_top"])
        if cfg["cue_railing"]:
            pa = PARAMS["parapet"]
            sh = PARAMS["shoulder"]
            run = st["nsteps"] * st["tread"] \
                + len(PARAMS["landings"]) * st["landing_depth"]
            drop = st["nsteps"] * st["riser"]
            segs = _rake_segments()
            rail_h = pa["z0"] + 0.6

            def para_ground(x):
                """[v5.1] Haunch top face (= nosing line + rail_h) - the landing surface for the rail posts.
                Instead of the old stepped top face it interpolates the rake/level polyline directly."""
                for kind, xa, xb, za, zb in segs:
                    if x < xb:
                        t = 0.0 if xb <= xa else (max(x, xa) - xa) / (xb - xa)
                        return za + (zb - za) * t + rail_h
                return segs[-1][4] + rail_h

            for sgn in (1.0, -1.0):
                sc.build_railing_line(
                    stage, f"{ROOT}/Rail_{'N' if sgn > 0 else 'S'}",
                    sgn * (st["w_bot"] + 0.3), st["x0"] - 0.5, st["x0"],
                    run, drop, para_ground, M["rail"], rail_h=0.9)

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    # ── [W3 L14] `cue_material_break`, made real ─────────────────────────────
    #   The old code read `stair_mtl = M["marble"]; if not break: stair_mtl =
    #   M["marble"]` — a dead branch. Both arms emitted the same material, and since
    #   `UpperPlaza` (the stair-head terrace) is ALSO marble, the cue this toggle names
    #   produced **no material boundary at the drop edge in either arm**. The ablation
    #   arm was therefore measuring nothing, and had been for the whole v5 line.
    #   ON  = a flight whose product differs from the marble terrace — a real break on
    #         the line x = 0, which is where the hazard is.
    #   OFF = marble flight, i.e. flight and terrace are one stone and the boundary is
    #         absorbed. That is what the toggle's own comment always promised.
    #   **This changes what the OFF/ON pair means for every scene14 dataset arm** and is
    #   declared as such in `w3_l14_v1.md` §6 — it is a research-cue repair, not a
    #   dressing tweak, and a reader comparing old arms must know the ON arm used to be
    #   a null.
    #   [GT-70] The ON side is now plain `concrete_floor` instead of a scene-side granite.
    #   The break widens (concrete against marble), so the cue is not weakened by the
    #   simplification — but the ON arm's pixels change and pre-GT-70 arms do not compare.
    stair_mtl = M["stair_conc"] if cfg["cue_material_break"] else M["marble"]

    build_plazas(M)
    if cfg["hazard_stairs"]:
        build_shoulder(M)           # shoulder massif outside the stair (old soffit) - before the stair
        build_side_slopes(M)        # sloped grass banks either side of the stair (isolation removed)
        build_stairs(stair_mtl)
        build_step_coursing(M)      # [W3 L14 · G1] unit coursing of the flight
        build_parapets(M)           # [GT-78] the raking side wall — and nothing on top of it
        build_cues(M)
    else:
        build_flat_fill(stair_mtl)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    build_ground_kit(M)             # [W2-D] ground elements - after the dressing (scatter order convention)
    if cfg["hazard_stairs"]:
        build_autumn_litter(M)      # [W3 L14 · ruling 8] after ground_kit, so the
                                    #   terrace scatter sits on the finished surface
    if cfg["cue_sign"]:
        build_signs()               # [v5 shared layer]

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene14_{ts}.png")
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
