# -*- coding: utf-8 -*-
"""
scene16_canopy_shadow.py — NegObs synthetic scene 16: canopy shadow stair (Isaac Sim 4.5)

Type    : T20 canopy stair (the inverse of T3 — the upper shadow band is the danger signal)
Spec    : Docs/multi_scene_brief_v3.md §D scene16_canopy_shadow
Shared  : scene_common.py (verified API helpers) · scene02_underpass.py (urban skeleton)

Hazard   : a descending stair (14 steps) sits in the middle of a bright sidewalk, with a solid
           canopy over it. In noon light the whole stair is sunk in the canopy shadow and reads
           as a dark band — the inverse of T3 (dark below): here the **upper shadow band** that
           floats above is what signals the drop. The cue_nosing yellow strip survives inside
           the shadow at low contrast.
Goal     : assemble the bright sidewalk (plaza_lower) + descending stair (plaza_light) + canopy
           (solid roof + 4 columns) + lower passage + planters·buildings, and judge by render (render only).

Run (GUI look check — default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene16_canopy_shadow.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python scene16_canopy_shadow.py
Smoke early exit:         NEGOBS_SMOKE=1  python scene16_canopy_shadow.py

Coordinates: Z-up, m, travel axis +X, drop start edge = x=0.

═══ W3 renovation (intake v2 §2 scene16 row · §7 rulings 4 & 8) ═════════════
Target image: `Docs/reference_photos/Generated Image - Scene02.jpg` (**G2**) — 16 and 02
are the same archetype, so G2 is effectively this scene's own reference.

1. **§7-4 BOTH BANDS.** The far `tactile_entrance` band (`gkit`, x −6.00…−5.40) is the
   scene's **cue+/label− quadrant filler** (§12.6): a statutory band in front of a
   *building entrance*, i.e. deliberately at a spot with **no drop**. It is left exactly
   where it was. A **second, correct stair-head warning band** is added at the statutory
   position — 0.30 m in front of the first riser, 0.60 m deep, full stair width — so the
   scene carries a true cue *and* a false one, which is what a real Korean street shows
   (guidance blocks at a building entrance **and** warning blocks at a stair head).
   The band reuses scene01's registered generator and texture (`infra_kit.build_tactile_pair`
   dot type + the `tactile` role, `relief="normal"`; §12.5 ③ prim-cap route). See
   `Docs/reports/w3_s16_v1.md` §2 for the GT-E1′ / GT-E2 / EXPECTED_FP arithmetic.
   **[W3 Lane-1 K1]** the band was built scene-side in `f831d61` only because `ground_kit.py`
   belonged to another workflow that window. It is now a **registered ground_kit site**
   (`TACTILE_SITES["scene16"]["stair_top"]`) emitted by `build_ground_kit` through the same
   `_ik_tactile → infra_kit.build_tactile_pair` route scene01 uses, so B11's registry
   describes what the kit actually emits and gates B6/B7/B9 see the band. Geometry is
   unchanged by the move (prim-hash A/B); only the prim path moves,
   `Tactile_StairHead` → `GKit/Tactile_stair_top`.

2. **BS-4 street-wall backdrop.** The scene used to be a plaza with **grass on both sides
   of the walk**, which is the opposite of G2's dense downtown block. Both verges are now
   a continuous **street wall** built by `building_kit` with an explicit
   `kind="backdrop"` and the real judged eye set (`bk.judged_eyes(0.0)`), i.e. 3–4 prims
   per block and **no windows at backdrop tier**. Buildings C/D (the +X / −X horizon
   closers) are untouched — this row is about the two verges.

3. **U-6 sweep.** `gkit` repair patches 2 → **1**, and the survivor is re-sited against a
   real cause (the manhole reinstatement cut) instead of floating on open pavement.
   §3(ii) N2 reconciliation: a repair patch **stays rectangular** — what is swept is the
   count and the causeless placement, not the shape.

4. **U-5 is already satisfied** and is only *stated* here, not changed: canopy
   x −1.00…+4.60 against a descent of x 0.00…4.48 (14 × 0.32) — the roof covers the whole
   flight plus 1.00 m of approach. 16 is the in-library model for the continuous-canopy
   form (02-A), not a defect.

DEFERRED to a Lane-1 follow-up (recorded, not attempted here): **K4(b)** street-row species,
and the `PLACEMENT` block that would promote the eight `placement_lint` `nodata` WARNs into
real gates. (**K5** curb geometry is no longer deferred — see GT-79 below.)

═══ GT-79 — the crossed road (scene identity) ═══════════════════════════════
User verdict: *"I do not know Scene16 identity. If it is an underground passage,
should it not be installed so that it feels like it crosses the road?"* — the descending
stair and the lower passage were built, but **nothing in the scene said what the passage
crosses under**, so the trench read as a decorative sunken slot in a plaza.

Added: a two-lane carriageway running **along Y, perpendicular to the passage axis**, over
the lower passage — kerb lines (`infra_kit.build_curb_line`, the scene02 GT-2 section),
a yellow centre line and two white edge lines, street footways, and a **covered box
section** where the trench passes under the carriageway. The east exit stair (x 14.00…18.48)
now stands on the **far footway**, so the read is descend / pass under the road / come up
on the other side. `PARAMS["xroad"]` carries every coordinate.

Three measured facts this row must state, because each one is a compromise forced by
geometry the brief freezes:

1. **Clear headroom under the box = 1.75 m** `[computed]`. The passage invert (−2.100)
   and the plaza datum (0.000) are both fixed by the T20 stair (14 × 0.150), and the
   carriageway datum is fixed at −0.130 by the GT-2 kerb section (150 mm exposure with
   the kerb top at +0.020 over a 0.000 footway). That leaves 1.970 m for structure +
   headroom over a 3.00 m clear span; the box roof is built at the minimum credible
   depth (0.170 m RC slab + 0.050 m wearing course = 0.220) → soffit −0.350, clear
   1.750 m. A statutory 지하보도 wants 2.30–2.50 m; reaching it would require moving the
   passage invert, which this round may not touch. Recorded, not hidden.
2. **The 150 mm trench parapet may not stand inside a carriageway.** `Wall_S`/`Wall_N`
   therefore run at `parapet_top` (+0.150) outside the crossing and are **capped at the
   box soffit** (−0.350) inside it, in one extra segment per side; the roof slab bears on
   that segment. Prim roots `Wall_S`/`Wall_N` are kept (they become the west run).
   The two parapet terminations get **end piers** and the pit guardrail is split into two
   runs with **end posts** on those piers — the craftsmanship rule for this round.
   The guardrail's x = 0.00 end is left exactly as it was: it sits inside the frozen
   judged band (T20 stair head) and is recorded for a later round.
3. **Sun geometry** `[computed]`. `SUN_AZ_OFFSET` 146.5 puts the shadow azimuth at 0°,
   i.e. **along +X**, at 49.79° elevation (shadow length = 0.845 × height). Every member
   added by GT-79 stands at x ≥ 5.60, so none of them can throw a shadow west of its own
   footprint: the judged stair band (x 0.00…4.48) keeps the canopy as its only shadow
   source, unchanged. The canopy, the stair, the nosing, the stair-head tactile band and
   the GT-71 hedge bands are untouched.

GT note: the two kerb lines are a **new 150 mm linear drop** at x 7.80 / 13.80 (the
`build_curb_line` `gt_drop`), 7.80 m east of the judged stair head. The scene's registered
hazard inputs — `edges=[("stair_top", 0.00)]`, `voids=((0.00, −1.50, 4.48, 1.50),)` and
`TACTILE_SITES["scene16"]` — are unchanged, but the GT cache needs a re-run.
"""

import os
import sys
import math
import json
import datetime

import scene_common as sc
import ground_kit as gk
import stair_kit as sk       # [realism v1] statutory handrail (§15(3)/(4))
import infra_kit as ik       # [GT-79] kerb line + road markings (K5 route)
import facade_kit as fk      # [W3 S16 · BS-4] primitive injection for building_kit
import building_kit as bk    # [W3 S16 · BS-4] street-wall backdrop (kind="backdrop")


# ===========================================================================
# [A] SCENE_CONFIG - standard 7 keys. Only hazard_stairs toggles geometry (False->pit filled flat).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False -> pit/stairs/passage become z=0 flat (only geometry toggle)
    # [realism v1] The four stair lines (west + east exit) are now statutory
    #   **handrails** (§15(3)/(4)) - one pipe per side, no mid rail, no balusters.
    #   Both stairs are wall to wall, so §15(1)2 is met by the "wall". The pit
    #   perimeter guard is unchanged. Docs/reports/scene15_railing_fix_v1.md §8.
    "cue_railing":        True,   # one handrail per stair side + guardrail around the pit at ground level
    # [v5.2 user] tactile paving is rare in reality - OFF by default (path kept for ablation).
    # [W3 S16 · §7-4] What this toggle still owns: the **lower landing** band and the
    #   bollard-frontage band. It no longer owns the **stair head** — the §7-4 ruling puts a
    #   statutory warning band there unconditionally so that the user's position check is
    #   satisfied in the *shipped* build, exactly as the entrance band already is. The
    #   ablation consequence (scene16's cue-OFF arm now retains one drop-correlated band)
    #   is written up in `Docs/reports/w3_s16_v1.md` §2.4 for the supervisor — it is a
    #   dataset-semantics decision, not a scene decision.
    "cue_tactile":        False,  # dot tactile paving: lower passage landing + bollard frontage
    "cue_material_break": True,   # False -> stairs·passage also take the sidewalk material (plaza_lower)
    "cue_nosing":         True,   # yellow non-slip strip on every step (low contrast inside the shadow - the signature)
    "cue_sign":           True,   # [v5 shared layer] one sign_exit (underpass exit)
    "cue_scene_dressing": True,   # planters·buildings·distant vista, all together
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    walk=dict(x_w=-12.0, x_e=22.0, y_s=-8.0, y_n=8.0, z_top=0.0, thick=0.5),
    # descending pit (trench): stair width 3 (y +-1.5), outer wall faces +-1.8
    pit=dict(x0=0.0, x1=4.48, y0=-1.5, y1=1.5),
    # 14 steps x riser 0.15 · tread 0.32 -> drop 2.1m, run 4.48m
    stairs=dict(x0=0.0, riser=0.15, tread=0.32, nsteps=14,
                y0=-1.5, y1=1.5, z_top=0.0, base_z=-2.6),
    # lower passage (plaza_lower), continuing +X and rising again at the east exit stair.
    passage=dict(x0=4.48, x1=14.0, z_top=-2.1, base_z=-2.6),
    # [audit v4 A1] east exit stair - there used to be a full-width blocking wall (Wall_E) at x=14,
    #   so you went down 2.1 m, walked 9.5 m and hit a dead end with no way out.
    #   A descending stair is built inside a rot_group 180 deg (pivot x=(14+18.48)/2) and maps
    #   to an ascending stair: local x=14(z=0) -> world x=18.48, local x=18.48(z=-2.1) ->
    #   world x=14.0 (flush with the passage top). This completes the scene as an "underpass".
    east_stairs=dict(x0=14.0, riser=0.15, tread=0.32, nsteps=14,
                     y0=-1.5, y1=1.5, z_top=0.0, base_z=-2.6),
    # [realism v1] `x_start` retired — it is now derived as x0 − ext_top.
    east_rail=dict(y=1.43),
    # east end of wall·trench = top of the east stair (14.0 + 14*0.32 = 18.48)
    wall=dict(thick=0.3, y_in=1.5, parapet_top=0.15, base_z=-2.6, x1=18.48),

    # canopy: covers the whole stair (x 0..4.48) + 1m past the head (x -1). Roof z=2.6, 4 columns.
    canopy=dict(x0=-1.0, x1=4.6, y0=-2.0, y1=2.0, z_roof=2.6, post_r=0.13,
                roof_t=0.14, base_z=-0.05),

    # cue
    # [audit v4 B1] perim_rail y 1.9 -> 1.65. y=1.9 sat outside the parapet (y 1.5..1.8), leaving
    #   a 15 cm gap between the post foot (z=0.15) and the sidewalk (z=0). y=1.65 is the
    #   parapet wall centreline -> the posts sit exactly on the parapet top (0.15).
    #   x1 4.48 -> 18.48 : guards the whole trench (including the east exit stair).
    perim_rail=dict(y=1.65, x0=0.0, x1=18.48, x_rear=None,
                    parapet_top=0.15, rail_h=0.9, post_r=0.03,
                    rail_r=0.03, rail_mid_r=0.018, mid_h=0.45, spacing=1.2),
    # ═══ [realism v1] Stair rail → statutory handrail (§15(3)/(4)) ══════════
    #  Old: `y=1.4, x_start=-0.5, rail_h=0.9, post_r=0.02, rail_r=0.03,
    #        rail_mid_r=0.018, rail_mid_drop=0.45, spacing=1.2` through
    #        `sc.build_railing_line`, used by **both** the west stair and the
    #        east exit stair — a full guardrail per side (top + mid rail + 43
    #        balusters + 5 posts + a second coaxial LOOK_GEO handrail with its
    #        own 5 posts) × 4 lines = 240 prims, **39.7 % of the scene**
    #        `[measured]`.
    #  Both stairs are **wall to wall**: width 3.00 = 2 × `wall.y_in` 1.50, and
    #  the walls run x 0…18.48 (`Lx = wall.x1 − pit.x0`), covering every rail
    #  span `[measured]`. So §15(1)2 is met by the "wall" and §15(3) prescribes
    #  a **handrail** - one pipe per side, no infill.
    #  **Post-mounted, not wall-bracketed**, for the same measured reason as
    #  scene02: `wall.parapet_top` = +0.15, so the 850 mm rail line runs 0.70 m
    #  above the wall top at the stair head and only meets the wall from
    #  x = 1.60 (step 5) — 36 % of this 4.48 m run would have had nothing to
    #  bracket to `[computed]`. Posts also make the statutory ≥300 mm end
    #  extensions buildable (§15(4)3).
    #  y = `wall.y_in` − 0.07 → pipe face 53 mm / post face 50 mm clear of the
    #  wall, both ≥ statutory 50 mm (§15(4)2) `[computed]`.
    stair_rail=dict(y=1.43, dia=0.034, height=0.85, post_r=0.020,
                    post_spacing=1.20, ext_top=0.30, ext_bot=0.30),
    # `ahead`/`depth`/`proud` drive the toggle-bound bands (lower landing, bollard front).
    # `head_*` is the **statutory stair-head warning band** added by §7-4 (BOTH BANDS):
    #   교통약자법 시행규칙 별표1 2호 차목 (점형 300 그리드 · 돌기 36개 · 높이 6±1 mm) +
    #   국도 실무요령 7.5 (점형 깊이 60 cm 표준 = 2줄) + 계단 첫 단 0.30 m 이격.
    #   The same three numbers ground_kit carries as `tactile_setback` 0.300 /
    #   `tactile_band_depth` 0.600 / `tactile_dot_h` 0.006. **[W3 Lane-1 K1]** the band is
    #   now emitted by `build_ground_kit` from the registered `stair_top` site; these
    #   values stay here because §7.4 makes the scene PARAMS the source of truth for
    #   coordinates, and `build_ground_kit` asserts them against ground_kit's own
    #   dimension table so the two can never drift apart silently.
    tactile=dict(ahead=0.3, depth=0.3, proud=0.004, land_depth=0.4,
                 head_setback=0.30, head_depth=0.60, head_dot_h=0.006),
    nosing=dict(color=(0.85, 0.72, 0.10), width=0.05, proud=0.001),

    # ═══ [GT-79] the crossed road — what the passage runs under ══════════════
    #  Section, west → east (all values metres, plaza datum z = 0.000):
    #    fw0  5.60 ─ street footway ─ kb0 7.60 │ kerb 0.20 │ car0 7.80
    #      … 6.00 m two-lane carriageway (centre 10.80) …
    #    car1 13.80 │ kerb 0.20 │ kb1 14.00 ─ street footway ─ fw1 16.00
    #  * `car0/car1` are the **kerb face** lines (`build_curb_line` p0/p1); the block
    #    body runs 0.20 m away from the road, so `kb0/kb1` are the block back faces and
    #    therefore the line the plaza walk is cut on — the kerb seals the walk's cut
    #    face exactly (scene02 `walk_a/walk_b` idiom).
    #  * `pv0/pv1` (0.05 m outside `kb0/kb1`) are the pavement and box-slab extents. The
    #    0.05 m offset exists so **no face of the carriageway slab is coplanar with a
    #    face of a kerb block or of the cut walk** — the only way to keep a buried kerb
    #    bed z-fight-free `[computed]`.
    #  * `fw0/fw1` are the street corridor edges and are the **same numbers as the gap in
    #    the BS-4 street wall** below, so the road runs between the blocks to the scene
    #    rim (§0-2) instead of dying into a facade.
    #  * `y0/y1` = ±`ground.size`/2: the carriageway ends **on the ground plate rim**, so
    #    it has no raw end face anywhere inside the world.
    #  * `kb1` 14.00 is exactly the east exit stair head, so the box mouth opens straight
    #    into the stair well and the far footway is the one the stair climbs to. There is
    #    **no crossing marked on this road** — that absence is the reason the underpass
    #    exists, and it is deliberate, not an omission.
    #  * `box_soffit` / `box_wear`: see docstring GT-79 note 1 for the 1.75 m headroom
    #    arithmetic. The roof bears on the capped wall segment (`Wall_*_Box`).
    #  * `pier`: the parapet end pier at each box mouth — 0.36 m along X, 0.02 m proud of
    #    the 0.30 m wall on both faces (so no coplanar face with the wall), capped at
    #    +0.280, i.e. 0.130 above the parapet. It is what the split guardrail's end post
    #    stands on.
    xroad=dict(car0=7.80, car1=13.80, kb0=7.60, kb1=14.00,
               pv0=7.55, pv1=14.05, fw0=5.60, fw1=16.00,
               y0=-70.0, y1=70.0, z_road=-0.130, thick=0.50,
               box_soffit=-0.350, box_wear=-0.180,
               pier=dict(length=0.36, out=0.02, top=0.280),
               lane=dict(centre_x=10.80, w_centre=0.15, w_edge=0.15,
                         edge_in=0.25, proud=0.003)),
    # [GT-79 · K5] `build_curb_line` arguments. Identical section to scene02 GT-2:
    #   exposure 0.150 above the carriageway datum −0.130 → kerb top +0.020, i.e.
    #   flush…+20 mm above the 0.000 footway, which is the builder's strict band.
    #   `gutter=False` (this street has no L-gutter pan) → gt_drop = height = 0.150.
    #   `lod_half` 12.0 keeps the 1 m unit rhythm inside |y| ≤ 12 (the judged window on a
    #   140 m line) and coarsens to 12 m blocks outside it `[measured — dry run]`.
    curb=dict(height=0.150, width=0.20, unit=1.0, embed=0.20, joint_w=0.006,
              arris="look", far_unit=12.0, lod_half=12.0),

    # ═══ [W2-D ground_kit] P3 sidewalk_block - spec §5.2 scene16 row ══════════
    #  Row prescription: "edge weeds on both walk verges · 1 manhole · canopy
    #  drip staining band (eaves projection)"; manhole (-3.9, -0.8).
    #  ★ Tactile is **ON, newly installed** (§12.4, the only ON scene in this
    #    batch): 0.6 m x full width in front of the **building entrance**,
    #    i.e. deliberately at a spot with **no drop**. That is the point — this
    #    scene is what fills the cue+/label- quadrant (§12.6). Defect type
    #    applied: "obstruction/occupation" — ground_kit only leaves the space
    #    clear, the pot/bicycle that occupies it belongs to the props team.
    #  ★ Placed unconditionally, not under `cue_tactile`, following the
    #    sceneN5 pilot: a band that is unrelated to the drop cannot leak a
    #    hazard cue into a cue-OFF cut, so toggle integrity is not at stake.
    #    The scene's own stair-head / bollard tactile paths stay toggle-bound.
    #  ★ `gutter_L` is overridden to 0: an L gutter is a carriageway edge
    #    detail and this walk has grass on both sides, no roadway (§4.2).
    #  ★ The canopy eaves projection line (x = canopy.x0 = -1.0) is only 1.0 m
    #    in front of the drop; drow(-1.0, d10) = 5.65 rows @1080 against a
    #    16-row floor, so a continuous transverse drip band there is a GT-E2
    #    violation [computed]. The drip is therefore carried as **decals**
    #    (`stain` kind "drip") inside the trimmed region instead of a line.
    #  ★ [W3 S16 · U-6] **patch 2 → 1.** Intake v2 §3(ii) rules `sidewalk_block`
    #    (02·08·16) down to one patch per main scene, and the N2 reconciliation is
    #    explicit that a repair patch **keeps its rectangle** (saw-cut 커터 geometry,
    #    DEC-3 module snap + axis lock) — what the sweep removes is the **count** and
    #    the **causeless placement**. Deleted: (−1.20, +0.35), a 0.9 × 0.6 m rectangle
    #    floating 1.2 m in front of the stair head with nothing to explain it, and the
    #    single most conspicuous decorative rectangle in the near field of the d2 cut.
    #    Deleted: (−8.60, −0.30), same objection at range. Survivor (−4.85, −0.80) is
    #    butted to the manhole at (−3.90, −0.80) with a 0.10 m gap — a utility-cut
    #    reinstatement, which is the one repair on a Korean footway that always has a
    #    visible cause. Gate effect `[measured, gk.plan_ground dry run]`: B1 1 (≥1) ·
    #    B2 51.0 % (≥20) · B6/B7/B9/B10/B11 unchanged PASS; B4/B5 were already WARN
    #    before this edit and are untouched by it.
    gkit=dict(
        region=(-12.0, -2.5, 0.0, 2.5),
        manholes=[(-3.9, -0.8)],
        gullies=[(-6.0, -2.2), (-1.5, 2.2)],
        patches=[(-4.85, -0.80)],
        # entrance tactile band: 0.60 m deep, walk-corridor width
        tactile_entrance=(-6.00, -2.5, -5.40, 2.5),
        wear_lane=((-12.0, 0.0), (-0.85, 0.0)),   # desire line to the stairs
    ),

    # surrounding ground / dressing
    #   gx1 14.5 -> 19.0 : also clears the east exit stair footprint (x 14..18.48) from the grass.
    ground=dict(size=140.0, z_top=-0.03, gx0=-0.5, gx1=19.0, gy0=-1.85, gy1=1.85),
    # [GT-79] B (8.00, −4.50) and C (12.00, 5.00) stood **inside** the new carriageway
    #   (x 7.80…13.80): a 3.00 m planter box centred at x 8.00 spans 6.50…9.50, C spans
    #   10.50…13.50 `[computed]`. Both move to the far footway (x 15.70…18.70), east of
    #   the kerb back 14.00 and west of the bollard block 20.20, where they read as the
    #   planting of the street the passage comes up onto. A and D are unchanged — they
    #   are the two that share the judged frame with the stair.
    planters=[dict(name="A", cx=-4.0, cy=4.0, base_z=0.0),
              dict(name="B", cx=17.2, cy=-4.6, base_z=0.0),
              dict(name="C", cx=17.2, cy=4.6, base_z=0.0),
              dict(name="D", cx=2.0, cy=6.5, base_z=0.0)],
    planter=dict(size=3.0, curb_h=0.45, curb_t=0.25, cap_over=0.05,
                 cap_h=0.05, grass_h=0.40),
    buildings=dict(
        # blocks the distant vista (+X horizon): facade -X plane
        C=dict(x0=26.0, x1=32.0, y0=-12.0, y1=12.0, h=12.0, floors=4,
               axis="x", facade_x=26.0, face_dir=-1.0),
        # the -X horizon is closed too (only one side used to be blocked, leaving the other empty)
        D=dict(x0=-30.0, x1=-24.0, y0=-14.0, y1=14.0, h=15.0, floors=5,
               axis="x", facade_x=-24.0, face_dir=1.0),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.5, margin=2.0),

    # ═══ [W3 S16 · BS-4] G2 street wall — the backdrop rebuild ═══════════════
    #  What it replaces: `ground` grass, visible on **both verges** beyond the walk
    #  (|y| > 8) in every judged cut. G2 closes both sides of the entrance with a
    #  continuous downtown block, and the intake row names that as the main work.
    #
    #  Why `kind="backdrop"` and not a tiered type `[measured — bk.plan_building]`:
    #    * `bk.eye_distance` measures to the **nearest point of the facade rectangle**.
    #      For a wall that runs *past* the camera that nearest point is the lateral
    #      standoff (8.00 m), not the nearest point that is ever **in** frame. The blocks
    #      therefore compute `tier="near"` and `z_ceil` 1.42–3.59 m, and the §10.8
    #      backdrop-policy (2) cap ("build nothing above z_ceil") would cut a 4-storey
    #      street wall off at first-floor sill height. Policy (2) is written for a
    #      building the camera faces, not for a wall it travels along.
    #    * The frame test agrees with the eye: the ±30° cone only reaches |y| = 8 at
    #      X ≥ 13.9 m, so the wall enters frame from world x ≈ +4.7 (d10) / +12.7 (d2) —
    #      i.e. **only the far run is ever seen, and only in silhouette**.
    #    * 4 of the 12 blocks (S0·S1·N0·N1) are behind every judged eye and BS-4 demotes
    #      them on its own (`in_frame=False`); forcing the kind makes the whole row one
    #      decision instead of eight.
    #  Prims 38 for 12 blocks (`prim_budget("backdrop", …) = 4` each) and **0 windows**.
    #
    #  Heights: the four blocks flanking the stair head (x −9…+5.5) are held to
    #  9.8–14.0 m on purpose. The walk is a 16 m canyon floor; at h = 14 the sky-view
    #  factor on the centreline is cos(atan(14/8)) ≈ 0.50, and the judged subject is a
    #  stair already sitting in canopy shadow (`under_canopy` runs mean 52.7 / dark 40.7 %
    #  in the 260730_w2d_fix baseline `[measured]`). The two taller blocks (24.0 / 26.0 m)
    #  sit **east of the flight**, where the sky they take is behind the descent.
    #  Sun check: `SUN_AZ_OFFSET` puts the shadow azimuth at 0°, i.e. **along +X**, so a
    #  wall running along X casts its shadow onto its own footprint and never across the
    #  walk — the canopy stays the only thing shadowing the stair.
    #  Blocks: (x0, x1, h, floors, shell material key).
    #  ── r2, after the first pilot `[measured — 260731_w3_s16 r1 vs 260730_w2d_fix]` ──
    #  r1 put the facades on the walk edge (|y| = 8.0) with a brick shell in the mix and
    #  paid for it on two instruments at once:
    #    * **OCCL** newdark 4.7 % / blob 1.9 % (h1.8_d2), 3.1 % (h0.9_d2), 2.3 %
    #      (shadow_band) — and the mask was **entirely in the top third at the left and
    #      right edges** (row bands 0–3, col bands 0–1 and 6–7), i.e. sky→wall, not
    #      "camera swallowed". The pixels crossed the <25 line because the facades face
    #      ±y while the sun sits on the **−X axis**: a street running along X gets *zero*
    #      direct sun on its street wall, so the shells live on skylight alone, and
    #      `brick_red` is a **0.087 linear-albedo** map `[measured]` — with r1's 0.78
    #      tint the worst blocks were an effective **0.050**.
    #    * **under_canopy** dark 40.7 → 57.1 % — the sky-view factor on a 16 m canyon
    #      floor at h ≈ 14 is cos(atan(14/8)) ≈ 0.50, and the judged subject already
    #      lives on indirect light.
    #  r2 fixes both causes rather than shrinking the deliverable: the canyon opens from
    #  16 to 20 m (facade |y| 8.0 → **10.0**, SVF 0.50 → 0.58), the two tall blocks come
    #  down 26/24 → 22/21 m, and `brick_red` leaves the street-wall palette for
    #  `marble_light` (0.325) — Korean 근생 street walls are tile / 석재 / 미장 far more
    #  often than face brick anyway, and G2's own two flanks are grey tile and metal.
    #  Effective shell albedo now 0.20–0.33 against r1's 0.05–0.25, all inside §1.11's
    #  ≤0.55 band. `brick_red` is untouched elsewhere (building C keeps it).
    #  ── [GT-79] the street corridor is cut through both rows ──────────────────
    #  A road that dies into a facade is not a road (§0-2, and the scene13 GT-64 note
    #  "the carriageway no longer dies in the lawn"). Both rows now leave a **gap at
    #  x 5.60…16.00** — exactly `xroad.fw0…fw1`, the street footway edges — so the
    #  carriageway and its two footways run between the blocks and on to the scene rim.
    #  Blocks per row 6 → 5: S3 (5.5…12.0, h 22.0) and S4 (12.0…20.0, h 15.2) are
    #  replaced by (16.0…21.0, h 22.0) and (21.0…26.0, h 15.2); N3 (4.0…11.5, h 16.0)
    #  and N4 (11.5…19.0, h 21.0) by (16.0…21.5, h 21.0) and (21.5…26.0, h 19.0), and the
    #  block that flanks the stair grows to the corridor edge (S2 5.5 → 5.6, N2 4.0 →
    #  5.6). The **tall pair stays east of the flight**, which is the r2 rule the row was
    #  built on. Sky opened by the gap is all at x ≥ 5.60, i.e. behind the judged stair
    #  band, and the shadow azimuth is 0° (+X), so nothing about the stair's lighting
    #  moves `[computed]`.
    backdrop=dict(
        base_z=-0.35,             # foot buried below the walk (0.0) and the grass (−0.03)
        S=dict(y0=-24.0, y1=-10.0, facade_y=-10.0, face_dir=1.0, blocks=(
            (-16.0,  -8.0, 12.0, 4, "city_stone"),
            (-8.0,   -2.0, 10.4, 3, "city_plaster"),
            (-2.0,    5.6, 13.2, 4, "city_wall"),
            (16.0,   21.0, 22.0, 7, "city_plaster"),
            (21.0,   26.0, 15.2, 5, "city_stone"))),
        N=dict(y0=10.0, y1=24.0, facade_y=10.0, face_dir=-1.0, blocks=(
            (-16.0,  -9.0, 11.2, 3, "city_wall"),
            (-9.0,   -2.5, 13.6, 4, "city_stone"),
            (-2.5,    5.6,  9.8, 3, "city_plaster"),
            (16.0,   21.5, 21.0, 7, "city_stone"),
            (21.5,   26.0, 19.0, 6, "city_plaster"))),
        # The verge the street wall cannot cover: the 2 m strips between the walk edge
        # (|y| = 8) and the new building line (|y| = 10), plus the 4 m band between the
        # walk's east end (x 22) and building C's facade (x 26) — a lawn closing a
        # downtown street at 32–36 m. All three are paved at the **existing ground top**
        # (`ground.z_top` −0.03) + 10 mm to defeat z-fighting, i.e. a material change of
        # a surface that is already there: no walked surface moves (GT class A) and the
        # only step introduced is the 20 mm the walk already has against the verge.
        # Kept as three strips, not one slab, so that nothing is laid over the trench
        # void (GT-V) — the east strip starts 3.52 m past the trench end at x 18.48.
        # [GT-79] the two long strips are cut on `xroad.pv0/pv1` (7.55 / 14.05), not on
        #   the kerb backs: cutting them on the kerb backs would have left the apron's
        #   cut face coplanar with the street footway plate's face over the same 0.30 m
        #   of z `[computed]` — a z-fight. At pv0/pv1 the apron's cut face meets the
        #   carriageway slab's face back to back instead, and the 0.05 m it gives up is
        #   covered by the street footway plate above it (top 0.000 vs apron −0.020).
        apron=dict(z_top=-0.02, thick=0.30, strips=(
            (-16.0, -10.0,  7.55, -8.0),
            (14.05, -10.0, 26.0,  -8.0),
            (-16.0,   8.0,  7.55, 10.0),
            (14.05,   8.0, 26.0,  10.0),
            (22.0,   -8.0, 26.0,   8.0))),
    ),

    # --- context dressing (cue_scene_dressing) : "a downtown plaza with an underpass entrance" ---
    # entrance sign gate (portal-type sign) - spans the top of the opening
    # [v5.1 realism, critical] Feedback: "the blue sign panel floats in mid-air - why up there?"
    #   Cause: the old Gate/Beam was a box of size (2.4, 0.15, 0.45) at (x −1.2, **y 0**, z 2.55).
    #   That is, **a 2.4 m slab lying along X** hung above the middle of the opening,
    #   and with the columns at y +-2.0 the slab never physically touched them ->
    #   a floating blue panel with no structural support.
    #   Fix: the beam becomes **a real lintel joining the columns**. It spans 4.12 m in Y
    #   (= 2·(y_half + post/2), out to both column faces), is 0.22 thick in X, and its top
    #   (z 2.60) is flush with the column heads -> the portal closes.
    #   The lintel itself is the sign band mounted at the opening head (gate material = navy),
    #   so no separate floating panel. Korean wayfinding is consolidated into the one N-4
    #   sign_exit (side post-mounted, −1.6, 2.6) - no duplicate signage.
    gate=dict(x=-1.2, y_half=2.0, post=0.12, post_h=2.6,
              beam_t=0.22, beam_h=0.40, beam_top=2.60),
    # [v5.1 §2] bollards brought to code - old: 6 posts at 2.5 m x spacing on both trench sides (y +-3.2)
    #   (a **decorative row** lining the opening; unrelated to any vehicle entry, spacing off code).
    #   New: **one row at the sidewalk entry** (x 20.5) beyond the east exit stair head (x 18.48),
    #   6 posts at 1.5 m spacing with a 1.5 m central gap (wheelchair passage). Dot tactile paving
    #   runs 0.3 m across the pedestrian approach face (west, x 20.2..20.5).
    #   Camera: 21~30 m away in every preset (eye x <= −0.5, looking +X) -
    #   zero near occlusion, unrelated to the judging subject (stairs·canopy shadow, x 0..4.6).
    bollards=dict(x=20.5, ys=(-3.75, -2.25, -0.75, 0.75, 2.25, 3.75),
                  block=dict(x0=20.2, x1=20.5, y0=-4.05, y1=4.05)),
    # [GT-79] bench 2 (9.00, 5.00) sat in the carriageway → moved to the far footway at
    #   (17.00, 6.90), 0.80 m clear of planter C (y 3.10…6.10) `[computed]`.
    benches=[(-5.0, 5.5, 180.0), (-5.0, -5.5, 0.0), (17.0, 6.9, 180.0)],
    # [GT-79] streetlight 2 (9.00, −6.50) sat in the carriageway. It becomes the **road's
    #   own** light on the east street footway (x 14.00…16.00): pole at x 15.00, arms
    #   ±0.90 → 14.10…15.90, inside the footway. Shadow runs +X (0.845 × 5.00 = 4.23 m,
    #   to x 19.23), i.e. away from the judged stair band `[computed]`.
    streetlights=[(-3.0, 6.5), (15.0, -6.5)],
    streetlight=dict(pole_h=5.0, pole_r=0.07, arm_len=0.9, arm_r=0.04,
                     head=0.24),
    hedges=[(-12.0, 6.5, -9.0, 7.3), (14.0, -7.3, 18.0, -6.5)],
    # 2 sidewalk paving bands (indicate the plaza scale)
    walk_bands=dict(ys=(-6.0, 6.0), width=0.45, z=0.007),
    # [v5 shared layer] Korean signs - (tag, TEX key, cx, cy, base_z, yaw, w, h)
    #   Exit(−1.6, 2.6): the underpass entrance exit sign. From the trench opening (y +-1.5) it is
    #     1.10 m, from the retaining wall face (y +-1.8) 0.80 m - meets the >=0.5 m hazard clearance.
    #     0.57 m from the sign gate column (x −1.2, y +-2.0, r 0.12); from the bollard
    #     (−1.0, 3.2) 0.92 m; outside the canopy (x −1.0..4.6) on the west.
    #   Camera check (grid gy=0, eye x −2/−5/−10, FOV +-30 deg):
    #     −2 -> outside at 81.3 deg (2.63 m to the side) · −5 -> outside at 37.4 deg · −10 -> 17.2 deg (8.81 m)
    #     approach(−7,0) 25.7 deg (frame edge) · shadow_band(−5,0) outside at 37.4 deg ·
    #     under_canopy(−0.5,0) behind · beauty_overview(−7,−5) 23.6 deg at the edge
    #     -> none of them hides the judging subject (stairs·shadow) at frame centre.
    signs=[("Exit", "sign_exit", -1.6, 2.6, 0.0, 180.0, 0.9, 0.45)],

    material=dict(
        # `brick_red` 2.0 is the library-wide value BS-1 will re-derive (0.90–1.10) across
        # 17 scenes in K3 — deliberately **not** touched here, and the new street-wall
        # brick shell reads the same key so that sweep still lands in one place.
        scale=dict(plaza_lower=0.7, plaza_light=1.80, grass=1.4,
                   brick_red=2.0, tactile=0.3,
                   concrete_wall=2.0, plaster=2.2, marble_light=1.6,
                   asphalt=3.0),          # [GT-79] PolyHaven asphalt_02, measured 3.0 m tile
        # [GT-79] Carriageway. Textured, never a constant: a carriageway is a **ground**
        #   prim and `scripts/const_color_audit.py` forbids a texture-less constant there
        #   (scene02's `asphalt_color` predates that rule). Tint is deliberately light for
        #   a Korean urban street — aged 아스콘 is mid-grey, not black — and R ≥ B so the
        #   scene13 blue-cast check ("청기 제거") passes.
        asphalt_tint=(0.58, 0.57, 0.55),
        # [GT-79 · K5] the kerb is a real product now, so it takes a stone map (the
        #   `marble_light` role already loaded for the street wall) rather than the
        #   colour-only `curb_color` the planters keep. Path token `Curb` →
        #   LOOK_CLASS["curb"], which is what `arris="look"` needs for its R10 arris.
        road_curb_tint=(0.80, 0.79, 0.76),
        # Road markings stay **constant colours**: `_LOOK_RULES` puts the paint family
        #   ahead of asphalt on purpose, because a marking that takes an aggregate
        #   texture stops working as a cue. White is held at 0.80 (v5.1 §4, no pure white).
        lane_white=(0.80, 0.80, 0.78), lane_yellow=(0.78, 0.62, 0.10),
        lane_rough=0.55,
        # [W3 S16 · BS-4] Street-wall shells. Three tones, mixed along both rows, because
        #   a Korean downtown block is never one material: 회색 콘크리트·타일 / 석재 /
        #   미장. Tints are **near-unity on purpose** — see the r2 note in
        #   `PARAMS["backdrop"]`: these facades never see direct sun (the sun is on the
        #   −X axis and the wall runs along X), so anything that scales the map down
        #   drives the shaded facade under the OCCL <25 line. Linear albedo after tint
        #   0.198 / 0.257 / 0.328 `[measured on the maps]`, all inside §1.11's ≤0.55 band
        #   and all still textures, never constants.
        city_wall_tint=(0.94, 0.95, 0.97),      # cool grey concrete / tile
        city_stone_tint=(0.92, 0.90, 0.87),     # light granite / stone cladding
        city_plaster_tint=(0.95, 0.94, 0.90),   # warm beige render
        grass_tint=(0.55, 0.68, 0.42),
        roof_color=(0.72, 0.72, 0.74), roof_rough=0.55,     # light grey roof
        post_color=(0.55, 0.55, 0.58), post_metallic=0.5, post_rough=0.5,
        wall_tint=(0.85, 0.85, 0.86),
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        # [v5.1 §4] parapet 0.90 -> 0.72 (no large pure-white areas)
        parapet_color=(0.72, 0.72, 0.69), parapet_rough=0.6,
        curb_color=(0.75, 0.75, 0.72), curb_rough=0.6,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        # dark constant colours for dressing (albedo 0.02~0.06 convention)
        band_color=(0.05, 0.05, 0.055), band_rough=0.7,
        gate_color=(0.03, 0.05, 0.09), gate_rough=0.45,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.4,
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
    # ─── SUN_AZ_OFFSET: the key parameter behind this scene's signature (the canopy
    #     shadow covering the stairs). Supervisor r1 C-16: 171.5->146.5. Sun mapping world az ~
    #     33.5+offset = 180 -> shadow az = az−180 = 0 -> the roof (z=2.6, noon elevation
    #     elev~49.79 deg) casts its shadow toward +X (the stair descent direction), covering the pit
    #     opening and the whole stair. Shadow-stair alignment is re-judged by the supervisor on renders.
    #     The [ ] keys (dome_rotation_step 15 deg) allow a further sweep in the GUI. ───
    SUN_AZ_OFFSET=146.5,

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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene16")

# [W3 S16 · BS-4] `concrete_wall` / `plaster` join for the street-wall shells.
# [GT-79] `asphalt` joins for the crossed carriageway.
ASSET_ROLES = ["plaza_lower", "plaza_light", "grass", "tactile",
               "brick_red", "concrete_wall", "plaster", "marble_light",
               "asphalt", "sign_exit", "hdri", "mdl"]   # [v5] sign_exit


def curb_lines():
    """[GT-79 · K5] the two kerb **face** lines: `(tag, p0, p1, road_side)`.

    `road_side` names the side the carriageway is on, so the block body extends the other
    way and its back face lands on `kb0`/`kb1` — the same line the plaza walk is cut on.
    West line: the carriageway lies at +X of the face with the line running −Y → +Y, so
    the body must go toward −X → `road_side="right"` (the scene02 convention).
    """
    r = PARAMS["xroad"]
    return (("W", (r["car0"], r["y0"]), (r["car0"], r["y1"]), "right"),
            ("E", (r["car1"], r["y0"]), (r["car1"], r["y1"]), "left"))


def curb_kwargs():
    """[GT-79 · K5] `build_curb_line` keyword set, in one place so the scene and the
    printed self-check cannot drift apart."""
    cu, r, w = PARAMS["curb"], PARAMS["xroad"], PARAMS["walk"]
    s_mid = (r["y1"] - r["y0"]) / 2.0          # arc length of y = 0 on either line
    return dict(height=cu["height"], width=cu["width"], unit=cu["unit"],
                arris_r=0.010, gutter=False, z_road=r["z_road"],
                walk_z=w["z_top"], embed=cu["embed"], joint_w=cu["joint_w"],
                arris=cu["arris"], collider=True, strict=True,
                lod_span=(s_mid - cu["lod_half"], s_mid + cu["lod_half"]),
                far_unit=cu["far_unit"])


def build_views():
    """Camera presets: grid_views(gy=0.0) + 4 mise-en-scene cuts."""
    views = sc.grid_views(0.0)
    # approach: from the bright sidewalk toward stairs·canopy (impression of the upper shadow band)
    views["approach"] = dict(eye=[-7.0, 0.0, 1.6], tgt=[3.0, 0.0, -0.6])
    # shadow_band: low viewpoint - only the stairs read as a dark band on the bright sidewalk
    views["shadow_band"] = dict(eye=[-5.0, 0.0, 0.35], tgt=[4.0, 0.0, -0.4])
    # under_canopy: from above the stairs, looking down into the canopy shadow and lower passage
    views["under_canopy"] = dict(eye=[-0.5, 0.0, 1.7], tgt=[4.5, 0.0, -1.6])
    # beauty_overview: oblique high-angle impression
    views["beauty_overview"] = dict(eye=[-7.0, -5.0, 3.2], tgt=[3.0, 1.0, -1.0])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. approach / beauty  — 밝은 보도·하강 계단·캐노피(지붕+기둥4) 식별
 2. shadow_band·h0.3   — 계단 전체가 캐노피 그림자로 어두운 밴드가 되는가(특색)
 3. under_canopy       — 암부 속 황색 노징이 저대비로 잔존하는가
 4. cue ON vs OFF      — nosing/railing/tactile 토글 시 기하 트랜스폼 불변
 5. 재질·태양방위      — [ ]키로 그림자가 계단을 덮는 방위 확인·Z파이팅 없는가
 6. [v4] 동측 출구 계단(x14→18.48 상승)·둘레난간 파라펫 접지·사인 게이트
 7. [v5] 공통 레이어 — 점자띠(하부 랜딩·볼라드) + sign_exit(진입부 y +2.6) 판독
 8. [W3] 점자 2본 — 계단머리 경고(x −0.90…−0.30, 낙차 있음) + 주출입구(x −6.00…−5.40,
        낙차 없음)가 한 프레임에 같이 읽히는가(§7-4 BOTH BANDS)
 9. [W3] 양측 가로벽 — 잔디 소실·창 0·프레임 좌우가 도심 블록으로 닫히는가(BS-4)
10. [W3] 보수 패치 1매가 맨홀 옆에 붙어 '원인 있는 절삭 보수'로 읽히는가(U-6)
11. [GT-79] 교차 도로 — 통로가 '도로 밑을 지나간다'로 읽히는가(차도·연석·중앙선·
        복개 박스 입구, 동측 계단이 도로 건너편에서 올라오는가) · 계단 그림자 밴드 불변"""


def main():
    # [GT-89] SMOKE gate - early exit BEFORE the Isaac boot (no GPU, no GUI).
    # The old template read NEGOBS_SMOKE only as boot()'s headless arg (or not at
    # all), so the §2.2 smoke floor booted Isaac on this scene (scene03/09 incident).
    # Deep checks keep their own arms (NEGOBS_SELFCHECK / geom_invariance_check.py).
    if os.environ.get("NEGOBS_SMOKE", "0") == "1":
        print("SMOKE_OK %s pre-boot gate (GT-89)" % os.path.basename(__file__))
        return
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
    UsdGeom.Xform.Define(stage, "/World/Scene16")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene16"

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
        M["walk"] = PBR(
            f"{ROOT}/Looks/Walk", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
            sca["plaza_lower"])
        M["stair"] = PBR(
            f"{ROOT}/Looks/Stair", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            sca["plaza_light"], tint=(0.72, 0.72, 0.72))   # [T1 T-1] x0.72
        M["wall"] = PBR(
            f"{ROOT}/Looks/Wall", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
            sca["plaza_lower"], tint=mp["wall_tint"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            sca["brick_red"])
        # [W3 S16 · BS-4] street-wall shells. The material **name** is what the look layer
        #   classifies on (`scene_common._look_spec` reads the last path segment), so the
        #   "city"/"wall"/"plaster"/"brick" tokens are load-bearing: CityWall/CityParapet
        #   land in the concrete family and CityBrick/CityPlaster in the brick family,
        #   which is what earns them texture promotion and the detail normal.
        M["city_wall"] = PBR(
            f"{ROOT}/Looks/CityWall", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"), sca["concrete_wall"],
            tint=mp["city_wall_tint"])
        M["city_stone"] = PBR(
            f"{ROOT}/Looks/CityStone", sc.tex_path("marble_light", "diff"),
            sc.tex_path("marble_light", "nor"),
            sc.tex_path("marble_light", "rough"), sca["marble_light"],
            tint=mp["city_stone_tint"])
        M["city_plaster"] = PBR(
            f"{ROOT}/Looks/CityPlaster", sc.tex_path("plaster", "diff"),
            sc.tex_path("plaster", "nor"), sc.tex_path("plaster", "rough"),
            sca["plaster"], tint=mp["city_plaster_tint"])
        M["tactile"] = PBR(
            f"{ROOT}/Looks/Tactile", sc.tex_path("tactile", "diff"),
            sc.tex_path("tactile", "nor"), None, sca["tactile"])
        M["roof"] = PBR(f"{ROOT}/Looks/Roof", diffuse_color=mp["roof_color"],
                        roughness_const=mp["roof_rough"], metallic=0.0)
        M["post"] = PBR(f"{ROOT}/Looks/Post", diffuse_color=mp["post_color"],
                        metallic=mp["post_metallic"],
                        roughness_const=mp["post_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        # [v5.1 §2/§4] materials for the code-compliant bollards - 3 body variants (tint jitter +-5%) + reflective band.
        #   The band is small in area, so high luminance is allowed (the no-large-pure-white rule does not apply).
        for _i, _f in enumerate((0.95, 1.0, 1.05)):
            M[f"bollard_{_i}"] = PBR(
                f"{ROOT}/Looks/Bollard_{_i}",
                diffuse_color=tuple(min(c * _f, 1.0) for c in mp["rail_color"]),
                metallic=mp["rail_metallic"],
                roughness_const=mp["rail_rough"] * (1.0 + 0.05 * (_i - 1)))
        M["bollard_band"] = PBR(f"{ROOT}/Looks/BollardBand",
                                diffuse_color=(0.86, 0.86, 0.84),
                                roughness_const=0.35)
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        M["curb"] = PBR(f"{ROOT}/Looks/Curb", diffuse_color=mp["curb_color"],
                        roughness_const=mp["curb_rough"])
        # [GT-79] carriageway + kerb product + the two paint tones.
        M["asphalt"] = PBR(
            f"{ROOT}/Looks/RoadAsphalt", sc.tex_path("asphalt", "diff"),
            sc.tex_path("asphalt", "nor"), sc.tex_path("asphalt", "rough"),
            sca["asphalt"], tint=mp["asphalt_tint"])
        M["road_curb"] = PBR(
            f"{ROOT}/Looks/RoadCurb", sc.tex_path("marble_light", "diff"),
            sc.tex_path("marble_light", "nor"),
            sc.tex_path("marble_light", "rough"), sca["marble_light"],
            tint=mp["road_curb_tint"])
        M["lane_w"] = PBR(f"{ROOT}/Looks/LaneWhite",
                          diffuse_color=mp["lane_white"],
                          roughness_const=mp["lane_rough"])
        M["lane_y"] = PBR(f"{ROOT}/Looks/LaneYellow",
                          diffuse_color=mp["lane_yellow"],
                          roughness_const=mp["lane_rough"])
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"])
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"])
        M["band"] = PBR(f"{ROOT}/Looks/Band", diffuse_color=mp["band_color"],
                        roughness_const=mp["band_rough"])
        # [W2 fix batch F1] Ground-class decal materials for the kit — see the
        #   `scripts/const_color_audit.py` rule: a *ground* prim may not carry a
        #   texture-less constant. paint / metal / water / misc are excluded from
        #   `_CONST_MDL_CLASSES` by design, so binding a kit crack or stain to one
        #   left it as a dead flat ribbon.
        M["gk_crack"] = PBR(f"{ROOT}/Looks/GKitCrack",
                            diffuse_color=(0.055, 0.055, 0.056),
                            roughness_const=0.92)
        M["gk_stain"] = PBR(f"{ROOT}/Looks/GKitStain",
                            diffuse_color=(0.20, 0.20, 0.195),
                            roughness_const=0.86)
        M["gate"] = PBR(f"{ROOT}/Looks/Gate", diffuse_color=mp["gate_color"],
                        roughness_const=mp["gate_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        return M

    # -------------------------------------------------------------------
    # ground - grass base (4 boxes cut around the pit footprint) : never covers the cavity
    # -------------------------------------------------------------------
    def build_ground(M):
        g = PARAMS["ground"]
        cz = g["z_top"] - 0.25
        th = 0.5
        H = g["size"] / 2.0
        gx0, gx1 = g["gx0"], g["gx1"]
        gy0, gy1 = g["gy0"], g["gy1"]
        r = PARAMS["xroad"]
        BOX(f"{ROOT}/Grass_W", ((-H + gx0) / 2.0, 0.0, cz),
            (gx0 + H, g["size"], th), M["grass"])
        BOX(f"{ROOT}/Grass_E", ((gx1 + H) / 2.0, 0.0, cz),
            (H - gx1, g["size"], th), M["grass"])
        # [GT-79] the S/N verge grass is cut on the carriageway slab (x pv0…pv1). The
        #   grass top is −0.030 and the carriageway datum −0.130, so grass left under
        #   the road would stand 100 mm proud of it `[computed]`. Cutting on pv0/pv1
        #   (not on the kerb backs) puts the grass end face **back to back** with the
        #   slab face instead of co-facing it, and the 0.05 m strip it gives up is
        #   covered by the walk (|y| ≤ 8) or by the street footway plate (|y| ≥ 8).
        for tag, ya, yb in (("S", -H, gy0), ("N", gy1, H)):
            for sfx, xa, xb in (("", gx0, r["pv0"]), ("_E", r["pv1"], gx1)):
                BOX(f"{ROOT}/Grass_{tag}{sfx}",
                    ((xa + xb) / 2.0, (ya + yb) / 2.0, cz),
                    (xb - xa, yb - ya, th), M["grass"])

    # -------------------------------------------------------------------
    # ground-level sidewalk - around the trench (x 0..14, outer wall faces +-1.8): west + south·north flanks
    # -------------------------------------------------------------------
    def build_walk(M):
        w = PARAMS["walk"]
        p = PARAMS["pit"]
        wl = PARAMS["wall"]
        top, th = w["z_top"], w["thick"]
        cz = top - th / 2.0
        y_out = p["y1"] + wl["thick"]            # 1.8
        x_tr1 = wl["x1"]                          # trench east end 18.48
        # [W2-0 · P-A] Walk_W is the ground_kit stage — register the skin
        #   exclusion **before** BOX (add_box calls `_skin_wanted` inline).
        sc.skin_exclude(f"{ROOT}/Walk_W")
        # west: x_w..0, full width
        BOX(f"{ROOT}/Walk_W",
            ((w["x_w"] + p["x0"]) / 2.0, (w["y_s"] + w["y_n"]) / 2.0, cz),
            (p["x0"] - w["x_w"], w["y_n"] - w["y_s"], th), M["walk"], col=True)
        # south / north flanks of the trench.
        # [GT-79] each flank is cut on the kerb **back** faces (kb0 / kb1) so the kerb
        #   block, whose body runs 0.20 m back from the face, seals the walk's cut face
        #   over its whole exposed height (z −0.330…+0.020) with no gap `[computed]` —
        #   the scene02 `walk_a/walk_b` rule. Below −0.330 the cut face is inside the
        #   carriageway slab. Prim roots `Walk_S`/`Walk_N` stay on the west run.
        r = PARAMS["xroad"]
        for tag, ya, yb in (("S", w["y_s"], -y_out), ("N", y_out, w["y_n"])):
            for sfx, xa, xb in (("", p["x0"], r["kb0"]), ("_E", r["kb1"], x_tr1)):
                BOX(f"{ROOT}/Walk_{tag}{sfx}",
                    ((xa + xb) / 2.0, (ya + yb) / 2.0, cz),
                    (xb - xa, yb - ya, th), M["walk"], col=True)
        # east: trench end (x18.48 = east stair head)..x_e, full width
        BOX(f"{ROOT}/Walk_E",
            ((x_tr1 + w["x_e"]) / 2.0, (w["y_s"] + w["y_n"]) / 2.0, cz),
            (w["x_e"] - x_tr1, w["y_n"] - w["y_s"], th), M["walk"], col=True)

    # -------------------------------------------------------------------
    # [W2-D] ground_kit - P3 sidewalk_block (spec §5.2 scene16 row)
    #   Drop edge = pit head x=0 (PARAMS["pit"]["x0"], §7.4). The pit itself is
    #   declared as a **void** so gate B8 (GT-V) refuses any element that would
    #   lay a ground plane over the opening (§6.3).
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["gkit"]
        p = PARAMS["pit"]
        # --- [W3 Lane-1 K1] §7-4 statutory stair-head band, now a registered site ------
        #   The band used to be built scene-side (`build_tactile_head`) because ground_kit
        #   was another workflow's file when §7-4 landed. It is the same generator with the
        #   same numbers — `_ik_tactile → infra_kit.build_tactile_pair`, dot type,
        #   relief="normal", the `tactile` texture role — so the move is geometry-neutral;
        #   what it buys is that gates B6 (GT-E1′), B7 (GT-E2) and B9 (albedo) finally see
        #   the band, and B11's registry describes something the kit actually emits.
        #   Bound to `hazard_stairs`, not to `cue_tactile`: the ruling exists to satisfy a
        #   position check on the shipped build, and with the trench filled there is no
        #   first riser to warn about, so the flat control arm inherits nothing.
        st = PARAMS["stairs"]
        tc = PARAMS["tactile"]
        gd = gk.GROUND_DIMENSIONS
        assert abs(tc["head_setback"] - gd["tactile_setback"][0]) < 1e-9 \
            and abs(tc["head_depth"] - gd["tactile_band_depth"][0]) < 1e-9 \
            and abs(tc["head_dot_h"] - gd["tactile_dot_h"][0]) < 1e-9 \
            and abs(float(st["z_top"]) - float(PARAMS["walk"]["z_top"])) < 1e-9, \
            "계단머리 점형: 씬 PARAMS 와 ground_kit 법정 치수가 어긋났다"
        head_x1 = st["x0"] - tc["head_setback"]
        head = (head_x1 - tc["head_depth"], st["y0"], head_x1, st["y1"])
        tactile_sites = dict(entrance=tuple(g["tactile_entrance"]))
        if cfg["hazard_stairs"]:
            tactile_sites["stair_top"] = head
        gp = gk.plan_ground(
            "sidewalk_block", region=tuple(g["region"]),
            z=float(PARAMS["walk"]["z_top"]), gy=0.0, origin=(0.0, 0.0, 0.0),
            edges=[("stair_top", float(p["x0"]))],
            voids=((p["x0"], p["y0"], p["x1"], p["y1"]),),
            dists=(2, 5, 10), scene="scene16",
            tactile=tuple(tactile_sites),
            overrides=dict(
                infra=dict(manhole=1, gully=2, gutter_L=0),
                # "drip" added to the stain kinds = canopy eaves run-off.
                # [W3 S16 · U-6] patch 2 → 1. The count lives here; `gkit["patches"]`
                #   only supplies the site, so leaving it at 2 would have auto-placed
                #   the second one back.
                surface=(("patch", 1), ("crack", 4),
                         ("stain", ("dirt", "gum", "drip")), ("weed", 8)),
                extras=(("wear_lane", dict(width=0.90)),)),
            extras_args=dict(wear_lane=dict(centerline=tuple(g["wear_lane"]))),
            sites=dict(manhole=[tuple(v) for v in g["manholes"]],
                       gully=[tuple(v) for v in g["gullies"]],
                       patch=[tuple(v) for v in g["patches"]],
                       tactile=tactile_sites),
            seed=16)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["band"], crack=M["gk_crack"], patch=M["walk"],
                  patch_cut=M["band"], manhole=M["band"], gully=M["band"],
                  gutter=M["band"], gutter_cover=M["band"],
                  trench=M["band"], trench_frame=M["band"],
                  marking=M["band"], weed=M["grass"], wear=M["wall"],
                  stain_dirt=M["wall"], stain_gum=M["gk_stain"],
                  stain_drip=M["wall"], tactile=M["tactile"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] scene16 P3 · 프림 {res['prims']} · "
              f"δmax {res['gt_delta_max']:.4f} · unit_cell {res['unit_cell']}")
        if "stair_top" in tactile_sites:
            need = gk.EDGE_K * gd["tactile_dot_h"][0]
            print(f"[점자·계단머리] x {head[0]:+.2f}…{head[2]:+.2f} · 첫 단 "
                  f"{tc['head_setback']:.2f} m 전 · 깊이 {tc['head_depth']:.2f} · 전폭 "
                  f"{st['y1'] - st['y0']:.2f} · 돌기 h{gd['tactile_dot_h'][0] * 1000:.0f} mm "
                  f"Ø35 · 알베도 상한 {gk.TACTILE_ALBEDO_CAP:.2f} · "
                  f"등재 site TACTILE_SITES['scene16']['stair_top'] (B11)")
            print(f"[점자·계단머리] GT-E1′ 이격 {tc['head_setback']:.3f} ≥ "
                  f"{need:.3f} m (EDGE_K {gk.EDGE_K:.0f} × proud "
                  f"{gd['tactile_dot_h'][0]:.3f}) — 충족. 먼 밴드(x −6.00…−5.40)는 "
                  f"그대로 — cue+/label− 사분면 유지")
        return res

    def build_flat_fill(M):
        """hazard_stairs=False control: the trench is filled, everything flat at z=0.

        [GT-79] the road is site context, not a cue, so it is built in **both** arms; the
        flat twin therefore takes the same carriageway cut (kb0 / kb1) as `build_walk`,
        which is what keeps the two arms differing by the trench alone.
        """
        w = PARAMS["walk"]
        r = PARAMS["xroad"]
        for sfx, xa, xb in (("", w["x_w"], r["kb0"]), ("_E", r["kb1"], w["x_e"])):
            # [W2-0 · P-A] the twin gets the same conditions — register before BOX.
            sc.skin_exclude(f"{ROOT}/FlatWalk{sfx}")
            BOX(f"{ROOT}/FlatWalk{sfx}",
                ((xa + xb) / 2.0, (w["y_s"] + w["y_n"]) / 2.0,
                 w["z_top"] - w["thick"] / 2.0),
                (xb - xa, w["y_n"] - w["y_s"], w["thick"]),
                M["walk"], col=True)

    # -------------------------------------------------------------------
    # walls + stairs + lower passage
    # -------------------------------------------------------------------
    def build_walls(M):
        """Trench retaining walls.

        [GT-79] The wall used to be one box per side, x 0.00…18.48, topped at
        `parapet_top` +0.150. Under the new carriageway that 150 mm upstand would stand
        **inside the road**, 0.280 m above the carriageway datum −0.130 `[computed]`, so
        the run is cut into three: parapet outside the crossing, and a segment capped at
        the box soffit (−0.350) under it, which is also what the roof slab bears on. The
        prim roots `Wall_S` / `Wall_N` stay on the west run.
        Each of the two parapet terminations gets an **end pier**: 0.36 m along X, 0.02 m
        proud of the 0.30 m wall on both faces (so it shares no face plane with the wall
        and cannot z-fight), capped at +0.280. It finishes the parapet's cut end and
        carries the split guardrail's end post.
        """
        p = PARAMS["pit"]
        wl = PARAMS["wall"]
        r = PARAMS["xroad"]
        pi = r["pier"]
        y_out = wl["y_in"] + wl["thick"]          # 1.8
        y_ctr = (wl["y_in"] + y_out) / 2.0
        top = wl["parapet_top"]
        bot = wl["base_z"]
        sof = r["box_soffit"]
        runs = (("", p["x0"], r["pv0"], top),          # approach trench, parapet on
                ("_Box", r["pv0"], r["pv1"], sof),     # under the carriageway, capped
                ("_E", r["pv1"], wl["x1"], top))       # far trench, parapet on
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            for sfx, xa, xb, zt in runs:
                BOX(f"{ROOT}/Wall_{tag}{sfx}",
                    ((xa + xb) / 2.0, sgn * y_ctr, (zt + bot) / 2.0),
                    (xb - xa, wl["thick"], zt - bot), M["wall"], col=True)
            for k, xc in enumerate((r["pv0"] - pi["length"] / 2.0,
                                    r["pv1"] + pi["length"] / 2.0)):
                BOX(f"{ROOT}/WallPier_{tag}{k}",
                    (xc, sgn * y_ctr, (sof + pi["top"]) / 2.0),
                    (pi["length"], wl["thick"] + 2.0 * pi["out"],
                     pi["top"] - sof), M["parapet"], col=True)
        # (audit v4 A1) east blocking wall Wall_E removed - the east exit stair stands there instead.

    def build_stairs(stair_mtl, passage_mtl):
        st = PARAMS["stairs"]
        sc.build_straight_stairs(
            stage, f"{ROOT}/Stairs", st["x0"], st["y0"], st["y1"],
            st["riser"], st["tread"], st["nsteps"], st["base_z"], stair_mtl,
            z_top=st["z_top"], collider=True)
        # lower passage
        pa = PARAMS["passage"]
        st = PARAMS["stairs"]
        BOX(f"{ROOT}/Passage",
            ((pa["x0"] + pa["x1"]) / 2.0, 0.0,
             (pa["z_top"] + pa["base_z"]) / 2.0),
            (pa["x1"] - pa["x0"], st["y1"] - st["y0"],
             pa["z_top"] - pa["base_z"]), passage_mtl, col=True)

    def build_east_exit(M, stair_mtl):
        """East exit stair (ascending) — the descending stair mirrored by a rot_group 180°.
        Local x0(z=0)=14.0 → world 18.48 (sidewalk top), local end (z=-2.1) → world
        14.0, flush with the passage top. Nosing·tactile·railing mirror inside the same group."""
        es = PARAMS["east_stairs"]
        run = es["tread"] * es["nsteps"]
        px = es["x0"] + run / 2.0                      # 16.24
        grp = sc.build_rot_group(stage, f"{ROOT}/EastExit", (px, 0.0), 180.0)
        sc.build_straight_stairs(
            stage, f"{grp}/Stairs", es["x0"], es["y0"], es["y1"],
            es["riser"], es["tread"], es["nsteps"], es["base_z"], stair_mtl,
            z_top=es["z_top"], collider=True)
        if cfg["cue_nosing"]:
            ns = PARAMS["nosing"]
            sc.build_nosing(
                stage, f"{grp}/Nosing", es["x0"], es["y0"], es["y1"],
                es["riser"], es["tread"], es["nsteps"], color=ns["color"],
                width=ns["width"], proud=ns["proud"], z_top=es["z_top"])
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            sc.build_tactile(stage, f"{grp}/Tactile_East",
                             es["x0"] - tc["ahead"], es["x0"],
                             es["y0"], es["y1"], M["tactile"], z=0.0,
                             proud=tc["proud"])
        # [realism v1] East exit stair: guardrail -> handrail (§15(3)), same
        #   rationale as the west stair (PARAMS.stair_rail). Built in the
        #   rot_group's **local** frame; the 180° flip preserves |y|, so the
        #   wall inner faces are at local y = ±1.50 exactly as in world.
        if cfg["cue_railing"]:
            er = PARAMS["east_rail"]
            sr = PARAMS["stair_rail"]

            def east_ground(x):
                if x <= es["x0"] + 1e-9:
                    return 0.0
                i = int((x - es["x0"]) / es["tread"]) + 1
                return -es["riser"] * min(max(i, 1), es["nsteps"])

            for sgn, tag in ((-1.0, "S"), (1.0, "N")):
                res = sk.build_handrail(
                    stage, f"{grp}/EastRail_{tag}", sgn * er["y"],
                    es["x0"], run, es["riser"] * es["nsteps"],
                    M["rail"], sc.add_cylinder, z_top=es["z_top"],
                    height=sr["height"], dia=sr["dia"],
                    ext_top=sr["ext_top"], ext_bot=sr["ext_bot"],
                    post_r=sr["post_r"], post_spacing=sr["post_spacing"],
                    ground_fn=east_ground, strict=False)
                for w in res["warnings"]:
                    print(f"[cue_railing] 규정 미달(동측) — {w}")

    # -------------------------------------------------------------------
    # canopy (solid roof + 4 columns) - covers the whole stair + 1m past the head
    # -------------------------------------------------------------------
    def build_canopy(M):
        cp = PARAMS["canopy"]
        sc.build_canopy(stage, f"{ROOT}/Canopy", cp["x0"], cp["x1"],
                        cp["y0"], cp["y1"], cp["z_roof"], cp["post_r"],
                        M["roof"], M["post"], roof_t=cp["roof_t"],
                        base_z=cp["base_z"])

    # -------------------------------------------------------------------
    # cues - nosing / tactile / railing
    # -------------------------------------------------------------------
    def build_signs():
        """[v5 shared layer] Korean sign (sc.build_sign). The exit sign at the underpass entrance =
        a cue for inferring a drop from adjacent infrastructure (series (1)). Coordinate checks are in the PARAMS['signs'] comment."""
        back = sc.make_pbr(stage, f"{ROOT}/Looks/SignBack",
                           diffuse_color=(0.16, 0.17, 0.18),
                           metallic=0.6, roughness_const=0.5)
        for tag, key, cx, cy, bz, yaw, w, h in PARAMS["signs"]:
            panel = sc.make_pbr(stage, f"{ROOT}/Looks/Sign{tag}",
                                diff=sc.tex_path(key, "diff"), uv_mode=True,
                                roughness_const=0.6)
            sc.build_sign(stage, f"{ROOT}/Sign_{tag}", cx, cy, bz, yaw, panel,
                          w=w, h=h, back_mtl=back)

    def build_cues(M, stair_mtl):
        st = PARAMS["stairs"]
        if cfg["cue_nosing"]:
            ns = PARAMS["nosing"]
            sc.build_nosing(
                stage, f"{ROOT}/Nosing", st["x0"], st["y0"], st["y1"],
                st["riser"], st["tread"], st["nsteps"],
                color=ns["color"], width=ns["width"], proud=ns["proud"],
                z_top=st["z_top"])
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            pa = PARAMS["passage"]
            # [W3 S16 · §7-4] `Tactile_Top` **retired**. It sat at x −0.30…0.00, i.e. flush
            #   against the first riser with **zero setback and 0.30 m depth**, which is
            #   neither the statutory position (0.30 m clear) nor the statutory depth
            #   (0.60 m = 2 rows). The §7-4 band supersedes it — see the `stair_top` site
            #   in `build_ground_kit`.
            #   Keeping both would have laid 0.90 m of continuous yellow at the stair head
            #   in the cue-ON arm.
            sc.build_tactile(stage, f"{ROOT}/Tactile_Land",
                             pa["x0"], pa["x0"] + tc["land_depth"],
                             st["y0"], st["y1"], M["tactile"],
                             z=pa["z_top"], proud=tc["proud"])
        if cfg["cue_railing"]:
            sr = PARAMS["stair_rail"]

            def stair_ground(x):
                if x <= 1e-9:
                    return 0.0
                return -st["riser"] * min(max(int(x / st["tread"]) + 1, 1),
                                          st["nsteps"])

            run = st["tread"] * st["nsteps"]
            drop = st["riser"] * st["nsteps"]
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
                  f"h{sr['height'] * 1000:.0f}) · 프림 {n_hr} — 방호는 좌우 "
                  f"옹벽 + 피트 둘레 난간")
            # ground-level guardrail around the pit (south·north edges, over the stair width)
            pr = PARAMS["perim_rail"]
            base_z = pr["parapet_top"]
            top_z = base_z + pr["rail_h"]
            mid_z = base_z + pr["mid_h"]

            def hrail(prefix, const_c, a0, a1, ends=(False, False)):
                """One guardrail run. `ends` asks for a **terminating post** at a0 / a1;
                the top and mid rails end on that post's axis, so the run has no rail
                stub hanging in air."""
                mid_c = (a0 + a1) / 2.0
                length = a1 - a0
                CYL(f"{prefix}/Top", (mid_c, const_c, top_z),
                    pr["rail_r"], length, M["rail"], rotY=90.0)
                CYL(f"{prefix}/Mid", (mid_c, const_c, mid_z),
                    pr["rail_mid_r"], length, M["rail"], rotY=90.0)
                ph = top_z - base_z
                n = 0
                a = a0 + pr["spacing"] / 2.0
                while a <= a1 - pr["spacing"] / 2.0 + 1e-6:
                    CYL(f"{prefix}/Post_{n}", (a, const_c, base_z + ph / 2.0),
                        pr["post_r"], ph, M["rail"])
                    a += pr["spacing"]
                    n += 1
                for tag_e, a_e, want in (("EndA", a0, ends[0]),
                                         ("EndB", a1, ends[1])):
                    if want:
                        CYL(f"{prefix}/{tag_e}",
                            (a_e, const_c, base_z + ph / 2.0),
                            pr["post_r"], ph, M["rail"])
                return n + sum(1 for e in ends if e)

            # [GT-79] the pit guardrail used to be one 18.48 m run per side. Under the
            #   carriageway (x pv0…pv1) the trench is covered, so a guardrail there would
            #   stand in the road: the run is split at the two parapet **end piers**
            #   (their centres, so the rails die on the end post that stands on the pier)
            #   and each new termination gets that post. The east run's far end (18.48)
            #   gets one too — it was a bare rail stub. The west run's x = 0.00 end is
            #   **left exactly as it was**: it lies inside the frozen judged band at the
            #   T20 stair head, so its termination is deferred, not fixed here.
            pi = PARAMS["xroad"]["pier"]
            c_w = PARAMS["xroad"]["pv0"] - pi["length"] / 2.0
            c_e = PARAMS["xroad"]["pv1"] + pi["length"] / 2.0
            n_pr = 0
            for sgn, tag in ((-1.0, "S"), (1.0, "N")):
                n_pr += hrail(f"{ROOT}/PerimRail_{tag}", sgn * pr["y"],
                              pr["x0"], c_w, ends=(False, True))
                n_pr += hrail(f"{ROOT}/PerimRail_{tag}_E", sgn * pr["y"],
                              c_e, pr["x1"], ends=(True, True))
            print(f"[GT-79] 피트 둘레난간 2런×2측 · 지주 {n_pr} "
                  f"(끝기둥 6 — 서측 x {c_w:.2f} · 동측 x {c_e:.2f}/"
                  f"{pr['x1']:.2f}) · x 0.00 단부는 판정대역 동결로 미변경")

    # -------------------------------------------------------------------
    # [GT-79] the crossed road — carriageway · kerbs · markings · covered box
    # -------------------------------------------------------------------
    def build_road(M):
        """The road the passage runs under.

        Build order, west → east and bottom → top:
          `Road/Pave_S|_N`   asphalt carriageway body, y rim → −1.80 and +1.80 → rim
          `Road/BoxSlab`     RC box roof over the trench (y ±1.80), soffit −0.350
          `Road/BoxWear`     its 50 mm wearing course, top flush with the carriageway
          `Road/Footway_*`   the street's own footways where the plaza stops (|y| ≥ 8)
          `Curb_W|_E`        `infra_kit.build_curb_line` — the K5 kerb product
          `Road/Lane*`       yellow centre line + two white edge lines

        The trench band is the only part that is decked. West of the box the trench
        stays open for 3.07 m between the stair foot (4.48) and the mouth (7.55), and
        east of it the box mouth opens straight onto the east exit stair head (14.00),
        which is the open-cut / box / open-cut section a real 지하보도 has.
        """
        r = PARAMS["xroad"]
        w = PARAMS["walk"]
        ln = r["lane"]
        wl = PARAMS["wall"]
        y_out = wl["y_in"] + wl["thick"]                 # 1.80 — outer wall faces
        pv0, pv1 = r["pv0"], r["pv1"]
        pxc, pxl = (pv0 + pv1) / 2.0, pv1 - pv0
        zr, th = r["z_road"], r["thick"]
        cz = zr - th / 2.0
        if cfg["hazard_stairs"]:
            spans = (("S", r["y0"], -y_out), ("N", y_out, r["y1"]))
        else:
            spans = (("S", r["y0"], r["y1"]),)           # flat control: no trench to deck
        for tag, ya, yb in spans:
            BOX(f"{ROOT}/Road/Pave_{tag}", (pxc, (ya + yb) / 2.0, cz),
                (pxl, yb - ya, th), M["asphalt"], col=True)
        if cfg["hazard_stairs"]:
            sof, wear = r["box_soffit"], r["box_wear"]
            BOX(f"{ROOT}/Road/BoxSlab", (pxc, 0.0, (sof + wear) / 2.0),
                (pxl, 2.0 * y_out, wear - sof), M["wall"], col=True)
            BOX(f"{ROOT}/Road/BoxWear", (pxc, 0.0, (wear + zr) / 2.0),
                (pxl, 2.0 * y_out, zr - wear), M["asphalt"])
        # Street footways: the plaza is the footway inside |y| ≤ 8, so these only run
        #   from the plaza edge out to the rim. Top 0.000 — 20 mm above the BS-4 apron
        #   and 30 mm above the grass, so both are covered with no coplanar face.
        for xt, xa, xb in (("W", r["fw0"], r["kb0"]), ("E", r["kb1"], r["fw1"])):
            for tag, ya, yb in (("S", r["y0"], w["y_s"]), ("N", w["y_n"], r["y1"])):
                BOX(f"{ROOT}/Road/Footway_{xt}{tag}",
                    ((xa + xb) / 2.0, (ya + yb) / 2.0,
                     w["z_top"] - w["thick"] / 2.0),
                    (xb - xa, yb - ya, w["thick"]), M["walk"], col=True)
        # [K5] kerb lines — the colour-only `M["curb"]` finally has geometry.
        kit = ik.kit_from_scene_common(sc, stage)
        ok_arris, got, msg = ik.check_arris_role(sc)
        if not ok_arris:
            print(f"[GT-79] 연석 아리스 경고 — {msg}")
        kw = curb_kwargs()
        n_blk = n_prim = 0
        top_z = expo = gt_drop = unit = 0.0
        for tag, p0, p1, side in curb_lines():
            res = ik.build_curb_line(kit, f"{ROOT}/Curb_{tag}", p0, p1,
                                     M["road_curb"], road_side=side, **kw)
            for wmsg in res["warnings"]:
                print(f"[GT-79] 경계석 경고({tag}) — {wmsg}")
            n_blk += res["n_blocks"]
            n_prim += res["prim_count"]
            top_z, expo = res["curb_top_z"], res["exposure_road"]
            gt_drop, unit = res["gt_drop"], res["unit_actual"]
        # Markings. No crosswalk: the underpass **is** the crossing here.
        for tag, mx, mtl, wdt in (("Centre", ln["centre_x"], M["lane_y"],
                                   ln["w_centre"]),
                                  ("EdgeW", r["car0"] + ln["edge_in"],
                                   M["lane_w"], ln["w_edge"]),
                                  ("EdgeE", r["car1"] - ln["edge_in"],
                                   M["lane_w"], ln["w_edge"])):
            ik.build_road_marking(kit, f"{ROOT}/Road/Lane{tag}", "line", mtl,
                                  mx, r["y0"], z=zr, yaw_deg=90.0,
                                  proud=ln["proud"], line_w=wdt,
                                  length=r["y1"] - r["y0"])
        head = (r["box_soffit"] - PARAMS["passage"]["z_top"]) if cfg["hazard_stairs"] else 0.0
        print(f"[GT-79] 교차 도로 · 차도 x {r['car0']:.2f}…{r['car1']:.2f} "
              f"({r['car1'] - r['car0']:.2f} m 2차로, 중앙선 x {ln['centre_x']:.2f}) · "
              f"y {r['y0']:.0f}…{r['y1']:.0f} (지반 림 — 절단면 없음) · "
              f"가로 회랑 x {r['fw0']:.2f}…{r['fw1']:.2f} = 가로벽 개구부")
        cu = PARAMS["curb"]
        print(f"[GT-79] 연석 2선 · 블록 {n_blk} · 프림 {n_prim} · 평균 블록 "
              f"{unit:.2f} m (판정창 |y|≤{cu['lod_half']:.0f} 은 단위 "
              f"{cu['unit']:.2f} · 바깥 {cu['far_unit']:.2f} LOD) · "
              f"상단 z {top_z:+.3f} (보도 flush…+0.020) · 차도노출 {expo:.3f} · "
              f"gt_drop {gt_drop:.3f} (신규 선형 낙차 — GT 재캐시 필요)")
        # Sun check, restated where the road is built: shadow azimuth 0° (+X) at 49.79°
        #   elevation → shadow length 0.845 × height, always toward +X. The westernmost
        #   member GT-79 adds is the west end pier at x = pv0 − pier/2 − pier/2.
        _sun_tan = math.tan(math.radians(PARAMS["light"]["noon_sun_elev"]))
        _west = min(r["fw0"], r["pv0"] - r["pier"]["length"])
        print(f"[GT-79] 태양 검증 · 그림자 방위 0°(+X) · 고도 "
              f"{PARAMS['light']['noon_sun_elev']:.2f}° (그림자 길이 "
              f"{1.0 / _sun_tan:.3f}×높이) · 신규 부재 최서단 x {_west:+.2f} → "
              f"판정 계단대역 x 0.00…"
              f"{PARAMS['stairs']['tread'] * PARAMS['stairs']['nsteps']:.2f} 에 "
              f"신규 그림자 0 — 캐노피가 계속 그림자 소유")
        if cfg["hazard_stairs"]:
            print(f"[GT-79] 복개 박스 x {pv0:.2f}…{pv1:.2f} · 슬래브 "
                  f"{r['z_road'] - r['box_soffit']:.3f} m · 소핏 "
                  f"{r['box_soffit']:+.3f} · 유효고 {head:.3f} m "
                  f"(지하보도 기준 2.30 미달 — 통로 바닥 −2.100 동결에 따른 결과, 문서화) · "
                  f"서측 개착 {pv0 - PARAMS['passage']['x0']:.2f} m · "
                  f"동측 입구 = 동측 계단머리 {PARAMS['east_stairs']['x0']:.2f}")

    # -------------------------------------------------------------------
    # [W3 S16 · BS-4] G2 street wall — both verges, kind="backdrop"
    # -------------------------------------------------------------------
    def build_backdrop(M):
        """The dense downtown block G2 shows on both sides of the entrance.

        `bk.judged_eyes(0.0)` is the scene's own preset eye set (`sc.grid_views(0.0)` —
        `build_views` uses gy = 0.0), so `d_true` / `in_frame` / `z_ceil` are computed
        from the real judging geometry (B-F3) instead of `|facade plane|`.
        `kind="backdrop"` is forced — see the `PARAMS["backdrop"]` note for why the
        tier that `eye_distance` returns is the wrong instrument for a wall the camera
        travels **along** rather than faces.
        """
        eyes = bk.judged_eyes(0.0)
        kit = fk.Kit(sc.add_box, sc.add_cylinder,
                     getattr(sc, "_oriented_box", None))
        bp = PARAMS["backdrop"]
        n_blk = sum(len(bp[t]["blocks"]) for t in ("S", "N"))
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
                print(f"[backdrop] {tag}{i} W {p.W:4.1f} h {h:5.1f} m · "
                      f"kind {p.kind} / tier {p.tier} · d_true {p.d_true:5.2f} m · "
                      f"in_frame {str(p.in_frame):5s} · z_ceil {p.z_ceil:4.2f} · "
                      f"프림 {len(prims)}/{bk.prim_budget('backdrop', p.tier, p.W)} "
                      f"· 창 0")
        ap = bp["apron"]
        for i, (ax0, ay0, ax1, ay1) in enumerate(ap["strips"]):
            BOX(f"{ROOT}/StreetApron_{i}",
                ((ax0 + ax1) / 2.0, (ay0 + ay1) / 2.0,
                 ap["z_top"] - ap["thick"] / 2.0),
                (ax1 - ax0, ay1 - ay0, ap["thick"]), M["walk"])
        print(f"[backdrop] 가로벽 {n_tot} 프림 / {n_blk} 동 (프레임 안 {n_frame} · "
              f"BS-4 자동 강등 {n_blk - n_frame}) + 전면 포장 {len(ap['strips'])} "
              f"— 양측 잔디 대체 · [GT-79] x "
              f"{PARAMS['xroad']['fw0']:.2f}…{PARAMS['xroad']['fw1']:.2f} 가로 회랑 개방")

    # -------------------------------------------------------------------
    # dressing - 2 planters + distant buildings
    # -------------------------------------------------------------------
    def build_bollard_std(M, prefix, cx, cy, bz, k=0):
        """[v5.1 §2] One code-compliant bollard — height 0.90 m · diameter 0.15 m (r 0.075) +
        a white reflective band on top (0.09 wide). Basis: Enforcement Rule of the Act on
        Promotion of Mobility Convenience for the Mobility Impaired, Table 2 (height 0.8~1.0 ·
        diameter 0.1~0.2 · spacing around 1.5 m · a bright reflective band).
        The old sc.build_bollard defaults (r 0.06 · h 0.75) fall short of the statutory floor,
        so the dimensions are stated here (scene_common unmodified). The body material takes a
        per-instance tint jitter (bollard_0..2) to remove the 'identical copies' impression."""
        h, r = 0.90, 0.075
        sc.build_bollard(stage, f"{prefix}/Post", cx, cy, bz,
                         mtl=M[f"bollard_{k % 3}"], radius=r, height=h)
        sc.add_cylinder(stage, f"{prefix}/Band", (cx, cy, bz + h - 0.14),
                        r * 1.05, 0.09, M["bollard_band"])

    def build_dressing(M):
        pl = PARAMS["planter"]
        for pdef in PARAMS["planters"]:
            sc.build_planter(
                stage, f"{ROOT}/Planter_{pdef['name']}", pdef["cx"], pdef["cy"],
                pdef["base_z"], M["curb"], M["grass"],
                tree_mtls=(M["wood"], M["canopy_a"], M["canopy_b"]),
                size=pl["size"], curb_h=pl["curb_h"], curb_t=pl["curb_t"],
                cap_over=pl["cap_over"], cap_h=pl["cap_h"], grass_h=pl["grass_h"])
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])
        # entrance sign gate - a portal sign spanning the opening head ("underpass entrance")
        # [v5.1] The beam becomes a lintel that really joins the columns (floating panel removed).
        ga = PARAMS["gate"]
        for sgn, tag in ((-1.0, "S"), (1.0, "N")):
            BOX(f"{ROOT}/Gate/Post_{tag}",
                (ga["x"], sgn * ga["y_half"], ga["post_h"] / 2.0),
                (ga["post"], ga["post"], ga["post_h"]), M["gate"], col=True)
        span = 2.0 * (ga["y_half"] + ga["post"] / 2.0)     # 4.12 (outer column faces)
        BOX(f"{ROOT}/Gate/Beam",
            (ga["x"], 0.0, ga["beam_top"] - ga["beam_h"] / 2.0),
            (ga["beam_t"], span, ga["beam_h"]), M["gate"], col=True)
        # [v5.1 §2] one row of code-compliant bollards (east sidewalk entry) + 0.3 m dot tactile paving
        bl = PARAMS["bollards"]
        for i, by in enumerate(bl["ys"]):
            build_bollard_std(M, f"{ROOT}/Bollard_{i}", bl["x"], by, 0.0, k=i)
        # Dot tactile paving belongs to the 'tactile paving' cue family, so it is bound to cue_tactile
        #   (so no yellow warning strip survives outside the toggle in an OFF cut - toggle integrity).
        if cfg["cue_tactile"]:
            bk = bl["block"]
            sc.build_tactile(stage, f"{ROOT}/Tactile_Bollard",
                             bk["x0"], bk["x1"], bk["y0"], bk["y1"],
                             M["tactile"], z=0.0,
                             proud=PARAMS["tactile"]["proud"])
        for i, (bx, by, yaw) in enumerate(PARAMS["benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{i}", bx, by, 0.0,
                           M["wood"], yaw=yaw)
        sl = PARAMS["streetlight"]
        for i, (lx, ly) in enumerate(PARAMS["streetlights"]):
            base = f"{ROOT}/Streetlight_{i}"
            CYL(f"{base}/Pole", (lx, ly, sl["pole_h"] / 2.0), sl["pole_r"],
                sl["pole_h"], M["post"], col=True)
            for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                CYL(f"{base}/Arm_{tag}",
                    (lx + sgn * sl["arm_len"] / 2.0, ly, sl["pole_h"] - 0.1),
                    sl["arm_r"], sl["arm_len"], M["post"], rotY=90.0)
                BOX(f"{base}/Head_{tag}",
                    (lx + sgn * sl["arm_len"], ly, sl["pole_h"] - 0.15),
                    (sl["head"], sl["head"], 0.12), M["lamp"])
        # [GT-63] clipped hedge bands: box+crown blobs -> fused rows of real
        #   shrub USDs (place_hedge_row; rects/heights/prim roots unchanged;
        #   legacy build_hedge fallback inside).
        # [GT-71 pilot] Density loosening, **call site only** — the shared helper,
        #   the band rects, h 0.8, base_z, the prim roots and the det_seed are all
        #   untouched; only three kwargs move. User verdict on the GT-63 hedgeswap
        #   was "a bit more natural, but still pretty dense", so pitch_frac
        #   0.53 -> 0.62 and the jitter 0.06/0.04 -> 0.10/0.06. §4-1 still governs:
        #   the band must read as ONE fused clipped mass, just less packed.
        #   Fusion holds by the helper's own width math `[measured — Privet
        #   1.7039 x 1.6378 x 1.1135 m off the asset; VEG_SHRUBS carries w 1.704 /
        #   h 1.114]` + `[computed]`: place_shrubs scales by h/nat_h, so a shrub's
        #   plan footprint is 1.704 x (0.8/1.114) x U(0.92,1.08) = 1.126…1.322 m,
        #   against pitch = (1.704/1.114) x 0.8 x 0.62 = 0.759 m. n = ceil(span/
        #   pitch)+1 then snaps the row to step 0.667 m (band 0, span 2.00) and
        #   0.750 m (band 1, span 3.00) = 46 % / 39 % overlap at nominal size, and
        #   still +0.13 m of overlap in the compound worst case (both neighbours
        #   at U 0.92, jitter pulling them 0.20 m apart, and the 1.638 m minor plan
        #   axis — not the 1.704 m major — facing the row under the random yaw).
        #   Counts 5+6 = 11 -> 4+5 = 9 shrubs. 0.62 sits just above the 0.613
        #   threshold at which band 1 sheds its 6th shrub and the plateau runs to
        #   0.817, i.e. it is the smallest step that actually thins **both** bands.
        n_hedge = 0
        for i, (hx0, hy0, hx1, hy1) in enumerate(PARAMS["hedges"]):
            n_hedge += sc.place_hedge_row(
                stage, f"{ROOT}/Hedge_{i}", hx0, hy0, hx1, hy1,
                0.8, gk.det_seed("scene16.hedge", i), base_z=0.0,
                pitch_frac=0.62, jit_along=0.10, jit_across=0.06)
        print(f"[GT-63] 생울타리 실관목 {n_hedge}주 "
              f"(place_hedge_row · 폴백 {'무' if n_hedge else 'build_hedge'})")
        print(f"[GT-71] 밀도 완화 파일럿(호출부 한정) · pitch_frac 0.53→0.62 · "
              f"지터 0.06/0.04→0.10/0.06 · 밴드 rect·h 0.8·seed·prim root 불변 · "
              f"설계 주수 11→9(실배치 {n_hedge} · 0 = build_hedge 폴백) · "
              f"공칭 중첩 46 %/39 %(최악 +0.13 m) — 융합 유지")
        # 2 sidewalk paving bands (indicate the plaza scale) - outside the trench at y=+-6
        # [GT-79] each band is cut on the kerb backs (kb0 / kb1): it sits 13 mm below the
        #   walk top, so across the carriageway (datum −0.130) it would have hung 117 mm
        #   in the air `[computed]`. The kerb block covers both cut ends.
        w = PARAMS["walk"]
        wb = PARAMS["walk_bands"]
        r = PARAMS["xroad"]
        for i, by in enumerate(wb["ys"]):
            for sfx, xa, xb in (("", w["x_w"], r["kb0"]),
                                ("_E", r["kb1"], w["x_e"])):
                BOX(f"{ROOT}/WalkBand_{i}{sfx}",
                    ((xa + xb) / 2.0, by, wb["z"] - 0.01),
                    (xb - xa, wb["width"], 0.02), M["band"])

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    stair_mtl = M["stair"] if cfg["cue_material_break"] else M["walk"]
    # passage material: the bright sidewalk material (plaza_lower) keeps the lower tone
    passage_mtl = M["walk"]

    build_ground(M)
    if cfg["hazard_stairs"]:
        build_walk(M)
        build_walls(M)
        build_stairs(stair_mtl, passage_mtl)
        build_east_exit(M, stair_mtl)
        build_canopy(M)
        build_cues(M, stair_mtl)
        # [W3 Lane-1 K1] the §7-4 stair-head band is emitted by `build_ground_kit` from
        #   the registered `stair_top` site — it is still gated on `hazard_stairs`, by the
        #   `cfg["hazard_stairs"]` test that selects the site there.
        # [U-5] stated, not changed — the canopy already covers the whole descent.
        _cp, _st = PARAMS["canopy"], PARAMS["stairs"]
        _run = _st["tread"] * _st["nsteps"]
        print(f"[U-5] 캐노피 x {_cp['x0']:+.2f}…{_cp['x1']:+.2f} vs 하강 x "
              f"{_st['x0']:+.2f}…{_st['x0'] + _run:+.2f} "
              f"({_st['nsteps']}×{_st['tread']:.2f}={_run:.2f}) → 접근로 "
              f"{_st['x0'] - _cp['x0']:.2f} m + 전 구간 + 하단 여유 "
              f"{_cp['x1'] - (_st['x0'] + _run):.2f} m — 이미 충족(16 이 표준형)")
    else:
        build_flat_fill(M)
    # [GT-79] site context, not a cue: the crossed road is built in **both** hazard arms
    #   and in the dressing-OFF arm, exactly like the walk and the walls. It is what
    #   makes the scene an underpass rather than a slot in a plaza, and it carries no
    #   drop-correlated signal, so toggle integrity is untouched.
    build_road(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
        build_backdrop(M)           # [W3 S16 · BS-4] G2 street wall, both verges
    build_ground_kit(M)             # [W2-D] ground elements - after the dressing (scatter order convention)
    if cfg.get("cue_sign"):
        build_signs()               # [v5 shared layer]

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] scene16 조립 완료 · 프림 {n}개 · 조기 종료")
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene16_{ts}.png")
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
