# -*- coding: utf-8 -*-
"""
sceneN2_asphalt_patch.py - NegObs synthetic scene 32: black asphalt patch (Isaac Sim 4.5)

Type    : N2 Hard Negative - a new asphalt patch on flat pavement (GT = no drop in any pixel)
Spec    : Docs/archive/legacy/nanobanana_batch1_geometry_map.md §D sceneN2_asphalt_patch
Look ref: look_refs/n2_asphalt_patch.jpg (v2 regeneration)
Shared  : scene_common.py (verified API helpers) · scene16_canopy_shadow.py (skeleton)

Hazard (counter-example): **there is no drop anywhere.** A rectangular patch of
           new asphalt with crisp cut lines is laid perfectly flush in the middle
           of grey weathered pavement. The new asphalt has albedo 0.030 - 1/14 of
           the surrounding concrete (0.42) and 1/5 of the existing asphalt (0.16)
           - and **reading like a "punched hole"** is this scene's feature. To
           form the **strongest black-rectangle confusion pair** with sceneD2 (a
           1.5×2.0m unguarded construction opening, a positive with a 3.0m drop),
           a small patch of the same size (1.5×2.0m) is placed at x 2.6~4.6m
           ahead of the camera in the same approach framing (4m·h0.9).
Goal     : assemble a flat concrete apron + 2 new patches (large 4×5 / small
           1.5×2.0) + 3 near-window maintenance repairs + a far old-asphalt
           roadway, gravel verge and buildings, and judge by render (render
           only). GT drop map = 0 in every pixel.

[W3 N2-CLEAN] "The patches must read as **neat contractor work**" (user, 07-30).
           Real Korean road repair *is* regular geometry, so the fix is not to
           delete rectangles but to make every repair mark obey one contractor
           vocabulary. Four rules, all research-grounded (see
           `Docs/reports/w3_n2_clean_v1.md` §1):
             R1 rectangle    - 소파보수 saws the damage back to a right-angled
                               rectangle ~0.30 m beyond the broken edge
                               [국토교통부 아스팔트 콘크리트 포장 시공 지침 5장];
                               min side 0.30 m [Caltrans FPMTAG ch.5].
             R2 axis         - `street_asphalt` is 무모듈 (no paving cell), so the
                               alignment datum is the **lane/stall axis**, not a
                               flag grid: every repair edge is parallel or normal
                               to +X. No splayed, rotated or free-form patch.
             R3 drum width   - a repair is as wide as the mill takes: 1.00-1.20 m
                               (utility class) or 2.00 m (carriageway class).
                               The 4.0 m main patch is therefore **two 2.00 m
                               passes** and carries the longitudinal cold joint
                               that proves it.
             R4 sealed joint - the cut face is tack-coated with emulsified bitumen
                               and the perimeter is overbanded, so the edge reads
                               as a **dark 60 mm sealant band with a slight sheen**
                               - not the bright grey ruled line it used to be
                               (that was vector art, `tonglam_v2.md` §2.13-2).
           Tone is separated on top of that: fresh 0.030 · cured 0.050 · aged
           0.068, three dated campaigns instead of one uniform black blanket.
           The library-wide decal-rectangle ban ("바닥에 이상한 사각형 무늬는
           웬만하면 다 제거해") targets *decorative* stains and marks; a repair
           patch is the standing exception named in spec §10.6 - "no decal has a
           straight edge that is not a construction joint, **a saw cut** or a
           kerb" - because a saw cut is exactly what makes it straight.

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneN2_asphalt_patch.py

Auto capture (headless):   NEGOBS_CAPTURE=1 python sceneN2_asphalt_patch.py
Smoke early exit:          NEGOBS_SMOKE=1  python sceneN2_asphalt_patch.py
Marking / dressing check:  NEGOBS_GEOCHECK=1 python3 sceneN2_asphalt_patch.py (no Isaac)

Coordinates: Z-up, m, travel axis +X. No drop - the feature (small patch) is the x=2.6~4.6 stretch.
"""

import os
import sys
import math
import json
import random
import datetime

import scene_common as sc
import batch1_common as bc
import ground_kit as gk


# ===========================================================================
# [A] SCENE_CONFIG - standard 7 keys. This is a hard negative scene, so hazard_* toggles not a drop but
#     the "scene feature element (asphalt patch)". Cue keys that do not apply are False + a reason comment.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_asphalt_patch": True,  # False -> remove patch and cut lines (uniform pavement control)
    "cue_railing":        False,  # no drop -> guardrail not customary. Key reserved only
    "cue_tactile":        False,  # vehicle-route pavement -> tactile paving not customary. Key reserved only
    "cue_material_break": True,   # sealed saw-cut joint (실란트 오버밴드) + pavement joints. False ->
                                  #   a harder counter-example with no boundary emphasis (just the
                                  #   patch, bare - an unsealed cut, which is how a *bad* repair reads)
    "cue_nosing":         False,  # no step -> a non-slip strip is meaningless. Key reserved only
    "cue_sign":           False,  # [optional] not implemented - config key reserved only
    "cue_scene_dressing": True,   # lane dashes · bollards · hedge · backdrop buildings together
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # ─ 3 pavement bodies (all flat, no opening at all). Adjacent plates drop z by 2mm each to bar coplanarity.
    apron=dict(x0=-70.0, x1=16.05, y0=-70.0, y1=70.0, z_top=0.0, thick=0.5),
    road=dict(x0=16.0, x1=30.05, y0=-70.0, y1=70.0, z_top=-0.002, thick=0.5),
    verge=dict(x0=30.0, x1=70.0, y0=-70.0, y1=70.0, z_top=-0.004, thick=0.5),

    # ─ new asphalt patches (perfectly flush: proud 0.002 <= 0.002 convention)
    #   small : separate from the large one in map §D - same size and framing as the sceneD2 opening 1.5x2.0m
    #   main  : map §D read-off 4(Y)x5(X) m. Offset to -Y (prevents visual merging with the small one)
    #   `tone` selects the oxidation age (see material.patch_tones). The small patch is the
    #   judged feature and stays the freshest/darkest; the 4.0 m main patch is `passes=2`
    #   because 4.0 m is two 2.00 m mill passes (R3) and gets the longitudinal cold joint.
    patches=[
        dict(name="small", x0=2.6, x1=4.6, y0=-0.75, y1=0.75,     # 2.0 × 1.5
             tone="fresh", passes=1),
        dict(name="main",  x0=7.0, x1=12.0, y0=-4.8, y1=-0.8,     # 5.0 × 4.0
             tone="cured", passes=2),
    ],

    # ─ [W3 N2-CLEAN] near-window maintenance repairs ────────────────────────
    #   These replace the 3 `ground_kit` patch blobs that used to fill the d2/d5/d10 near
    #   windows. The kit draws a patch from a random area draw (0.63 m² × 0.85~1.15) and a
    #   random aspect ratio (0.7~1.6) and `street_asphalt` declares no module, so nothing
    #   snapped them: three differently-proportioned dark quads at unrelated y offsets, on
    #   top of the 2 feature patches, is exactly the "지저분해" the user flagged.
    #   `build_patch_field`'s per-call dims are not
    #   reachable from a scene (`_compose_ops` fixes its kwargs), so the honest fix is to
    #   draw them here, in the same vocabulary as the two feature patches.
    #   Window coverage is preserved exactly (`grid_views` eye = [−d, 0, h], HFOV 60°,
    #   NEAR_W1 = 0.564~2.00 m ahead ⇒ d2 x −1.436…0 · d5 x −4.436…−3 · d10 x −9.436…−8):
    #     xing   x −4.55…−3.35 → d5   · soft_a x −1.70…−0.70 → d2
    #     soft_b x −9.40…−8.20 → d10
    #   `xing`'s west edge is set at −4.55 rather than −4.30 for a paint reason: the near
    #   stall row starts at x −4.60, so cutting at −4.30 left a 0.21 m paint stub west of the
    #   trench. A 21 cm orphan of a stall line reads as a botched repaint, i.e. as the exact
    #   opposite of the brief. At −4.55 the sealant band (−4.61) reaches past the paint start
    #   and the stub is swallowed `[computed - geocheck ①]`.
    #   `xing` is a transverse service-crossing reinstatement (횡단 관로 복구), the commonest
    #   neat repair on a Korean carriageway: one 1.20 m mill pass across the aisle, both
    #   saw cuts sealed. It cuts the near stall line at y=0 - the same "repaving makes the
    #   line vanish and resume" event the scene already narrates - and stops at |y| 2.10, so
    #   it never lands *on* the y=±2.5 stall lines (an edge coincident with paint reads as a
    #   mistake, not as work).
    repairs=[
        dict(name="xing",   x0=-4.55, x1=-3.35, y0=-2.10, y1=2.10,   # 1.2 × 4.2
             tone="cured", passes=1),
        dict(name="soft_a", x0=-1.70, x1=-0.70, y0=-0.50, y1=0.50,   # 1.0 × 1.0
             tone="fresh", passes=1),
        dict(name="soft_b", x0=-9.40, x1=-8.20, y0=-0.70, y1=0.30,   # 1.2 × 1.0
             tone="aged",  passes=1),
    ],
    #   cut_w 0.08 → 0.06 : 실란트 오버밴드 band 50~80 mm, midpoint.
    #   seam_* : the longitudinal cold joint between two mill passes. It sits **on** the
    #   patch (proud 0.0023 > patch 0.0020), so the z ladder gains one rung and stays
    #   strictly increasing - no coplanarity anywhere.
    patch=dict(proud=0.0020, thick=0.05,
               cut_w=0.06, cut_proud=0.0012, cut_thick=0.02,
               pass_w=2.00, seam_w=0.05, seam_proud=0.0023, seam_thick=0.010),
    # ─ pavement joints (concrete slab boundaries) - the lowest proud layer
    joints=dict(spacing=4.0, width=0.03, proud=0.0006,
                x0=-20.0, x1=16.0, y0=-20.0, y1=20.0),
    # ─ lane dashes on the far roadway (the road runs along Y -> the dashes line up along Y too)
    lane=dict(x=23.0, y0=-30.0, y1=30.0, dash=3.0, gap=6.0,
              width=0.12, proud=0.002, thick=0.01),
    # ─ 2 solid edge lines on the roadway (with the dashes they fix it as a "2-lane road"). Same layer as the dashes.
    edge_lines=[dict(name="W", x=17.0), dict(name="E", x=29.2)],
    edge_line=dict(y0=-30.0, y1=30.0, width=0.15),

    # ═══ road markings (cue_scene_dressing) - use: "car park -> roadway" ═══
    #  * repaving realism [user instruction]: the stall lines are **deleted** where they overlap
    #    a patch (+ sealant band width and clear margin) -> the line vanishes under the patch and resumes beyond it.
    #    paint_line_segments() cuts them automatically from repair_rects() (feature patches + repairs).
    #  * z stratigraphy: joint 0.0006 < marking 0.0010 < sealant band 0.0012 < patch 0.0020
    #            < cold joint 0.0023 < manhole frame 0.0026 < lid 0.0032 < boss 0.0038 (nothing coplanar)
    marking=dict(proud=0.0010, thick=0.012, clear=0.030,
                 tile=0.90, gap_prob=0.10, seed=20260727),
    #   near/far parking stall lines (running along the travel axis X). The small patch cuts the y=0 line,
    #   the large patch cuts the far row's y=−2.5 line.
    #   * [W2 §5.3 N2] `near` start 0.4 -> **−4.6**. "Plenty of elements, but the coordinates
    #     are outside the frame" is this scene's paradox - if the near stall lines start at x 0.4
    #     they hit **none of the h0.3 near windows** (d2 = x −1.436…0 · d5 = −4.436…−3 ·
    #     d10 = −9.436…−8) `[measured - spec §5.3 "the N2 paradox"]`.
    #     Extending to −4.6 runs through the d5 window and reaches the d2 window. The row head line
    #     (stall_heads N x=5.6) is unchanged, so only the stall length grows to 10.2 m.
    stall=dict(ys=(-5.0, -2.5, 0.0, 2.5, 5.0), width=0.12,
               near=(-4.6, 5.6), far=(9.0, 13.6)),
    #   stall head line (closed end) - the line crossing the +X end of each row
    stall_heads=[dict(name="N", x=5.6), dict(name="F", x=13.6)],
    stall_head=dict(y0=-5.0, y1=5.0, width=0.12),
    #   stop line (car park -> roadway exit) + 1 aisle direction arrow (+Y one-way)
    stopline=dict(x=15.2, y0=-6.0, y1=6.0, width=0.45),
    arrow=dict(cx=7.3, cy=3.2, yaw=90.0, shaft_len=2.0, shaft_w=0.22,
               head_len=0.85, head_w=0.20, head_ang=32.0),
    #   1 small manhole (in the aisle, flush)
    manhole=dict(cx=6.3, cy=1.4, r_frame=0.36, r_lid=0.30, r_boss=0.08,
                 h=0.03, proud_frame=0.0026, proud_lid=0.0032,
                 proud_boss=0.0038),

    # ═══ [W2 ground_kit] P4 street_asphalt - spec §5.3 N2 row ══════════════
    #  the diagnosis for this scene is not "there are no elements" but **"there are plenty of
    #  elements, but the coordinates are outside the near window"** - the exact
    #  mechanism behind σ_LF 1.36 despite having 9 kinds `[spec §0-3]`.
    #  so the kit's role is limited to **filling the near windows**:
    #    (1) add 1 manhole (the old manhole at x=6.3 stays - spec "or add 1")
    #    (2) 2 near-view cracks · tyre stains · edge weeds
    #  banned / omitted:
    #    · **joints**: the scene already lays a 4 m grid over x −20…16 and it passes all 3
    #      windows (d2 x=0 · d5 x=−4 · d10 x=−8 `[computed]`) -> 0 kit joints
    #      (`street_asphalt` has `joint=None` to begin with). Avoids the D6 double grid.
    #    · **L-shaped gutter and lane paint**: the kerb (y=9.50) is outside the near windows and
    #      the paint is already handled by `build_markings()` -> `gutter_L=0`, `marking=()`.
    #    · **[W3 N2-CLEAN] patches -> 0**: the near-window repairs are now drawn by
    #      `build_patches()` from `PARAMS["repairs"]` in the contractor vocabulary (R1-R4).
    #      The kit's patch op is dropped rather than left inert, so the tree does not carry a
    #      call site that reads as intent (spec §6.2 K2).
    #    · **[W3 N2-CLEAN] crack 6 -> 2 · oil stain dropped · weed 4 -> 2**: the count that
    #      made the frame read as neglect rather than as maintenance. 2 sealed cracks is the
    #      "occasional crack-seal squiggle" a maintained apron actually carries; 4 free-form
    #      `oil` blots were bound to `M["patch"]` (albedo 0.030), i.e. 4 near-black lobes
    #      scattered over grey concrete, which is the opposite of "깔끔하게 작업된". `tire`
    #      stays: a wheel track is a straight-edged band because a tyre bounds it, and it is
    #      what says "vehicles use this aisle".
    ground=dict(
        region=(-12.0, -4.0, 2.0, 4.0),
        #  manhole - applying the criterion of the pilot-approved M9-(b) 2nd correction
        #  (areal element screen width <=25 %), it is placed in the W2 window (2.00~3.00 m).
        #  x=−2.40 ⇒ d5 ground distance 2.60 m · screen width 414 px = 21.6 % `[computed - W_px = f·0.648/X]`.
        #  y=+0.50: it sits midway between the near stall lines y ∈ {−5,−2.5,0,2.5,5}, so it does not
        #  overlap the paint (0 Z-fighting).
        manhole=(-2.40, 0.50),
        #  [W3 N2-CLEAN] `patches=[...]` retired here - see the ban list above. The §2.2
        #  prescription ("at least 1 discrete element in each of the three windows") is
        #  discharged by `PARAMS["repairs"]`, which covers the same d2/d5/d10 windows at the
        #  same x anchors, so no window loses its element.
        gullies=[(-3.0, -3.6), (-8.0, -3.6)],
        tactile_depth=0.60, tactile_setback=0.30,
    ),

    # ═══ context dressing - kerb/sidewalk, streetlights, trees, skyline ═════
    #  * GT unchanged: the kerb is a **raised z>=0 strip on flat ground** (ground on both sides is z~0)
    #    -> not a real drop. The sidewalk slab is also a flush plate at proud 0.003.
    #  * camera corridor: every view's eye is at (x −6..−1.4, y 0) - new solid objects go only at
    #    |y| >= 9.5 or x >= 14.5 (rules out burial and occlusion at source).
    curb=dict(x0=-30.0, x1=15.0, y=9.50, t=0.35, h=0.14),   # 2 runs, symmetric in +-y
    walk=dict(x0=-30.0, x1=15.0, y_in=9.85, y_out=14.0, z_top=0.0030),
    streetlights=[dict(name="A", cx=0.0, cy=11.6), dict(name="B", cx=-8.0, cy=11.6),
                  dict(name="C", cx=12.0, cy=-12.2)],
    streetlight=dict(pole_h=5.2, pole_r=0.075, arm_len=0.9, arm_r=0.04, head=0.26),
    planters=[dict(name="A", cx=4.0, cy=12.0), dict(name="B", cx=-4.0, cy=-12.0)],
    planter=dict(size=2.4, curb_h=0.42, curb_t=0.22, cap_over=0.05,
                 cap_h=0.05, grass_h=0.36),
    # ── bollards [v5.1 §2 · ctx2] ─────────────────────────────────────────
    #   old: y=8.5 (= the middle of the roadway, 1 m inside the kerb y9.5) · spacing 4.0 · h0.75 ·
    #   no reflective band or dot tactile paving -> both position and spec unrealistic.
    #   new: **keep the sidewalk-roadway interface** but move them **onto the sidewalk outside**
    #   the kerb (y 9.50..9.85), to y=10.30 (0.45 m clear of the kerb face = usual practice). Spacing 1.5 m.
    #   the dot tactile paving is flush on the **sidewalk side (+Y)** (the walking guidance direction).
    #   base_z = walk.z_top(0.0030) - they stand on the sidewalk plate.
    #   * only now is the camera corridor |y| >= 9.5 convention satisfied (the old y=8.5 violated it).
    bollards=dict(y=10.30, x0=2.0, x1=14.0, spacing=1.5, r=0.06, h=0.90,
                  front=(0.0, 1.0)),
    hedge=dict(x0=31.0, x1=32.2, y0=-26.0, y1=26.0, h=0.9),
    buildings=dict(
        # blocks the far vista (+X horizon): facade on the -X plane
        C=dict(x0=40.0, x1=50.0, y0=-26.0, y1=26.0, h=11.0, floors=3,
               axis="x", facade_x=40.0, face_dir=-1.0, base_z=-0.004),
        # ─ skyline (silhouette steps): a tower behind C + mid-rise at the sides ─
        T=dict(x0=52.0, x1=64.0, y0=-18.0, y1=12.0, h=30.0, floors=9,
               axis="x", facade_x=52.0, face_dir=-1.0, base_z=-0.004),
        E=dict(x0=42.0, x1=52.0, y0=28.0, y1=44.0, h=20.0, floors=6,
               axis="x", facade_x=42.0, face_dir=-1.0, base_z=-0.004),
        # ─ street wall beyond the sidewalk (both sides) : facade on the y plane. x1=14.5 (no roadway intrusion) ─
        L=dict(x0=-24.0, x1=14.5, y0=15.0, y1=25.0, h=12.0, floors=4,
               axis="y", facade_y=15.0, face_dir=-1.0),
        R=dict(x0=-24.0, x1=14.5, y0=-25.0, y1=-15.0, h=12.0, floors=4,
               axis="y", facade_y=-15.0, face_dir=1.0),
    ),
    window=dict(w=1.4, h=1.7, inset=0.15, col_step=3.2, margin=2.5),

    material=dict(
        scale=dict(plaza_lower=0.9, plaza_light=1.0, gravel=0.6, grass=1.4,
                   brick_red=2.0),
        # ─ pavement: plaza_lower source mean sRGB 0.49 (neutral grey) + weathering tint -> ~0.42
        apron_tint=(0.86, 0.86, 0.84),
        # ─ new asphalt: the darkest end of the sRGB perception convention (0.02~0.06 band).
        #   1/5 of the existing asphalt constant colour 0.16 (scene11/17) -> "looks like a hole" is the feature
        patch_color=(0.030, 0.030, 0.033), patch_rough=0.92,
        # ─ [W3 N2-CLEAN] tone ladder. New AC oxidises: the binder film burns off the surface
        #   aggregate and the mat greys, fast in the first season and then slowly. Three
        #   campaigns are enough to read as a maintenance history and few enough to stay
        #   restrained. All three stay far below the old asphalt roadway (0.16) and the
        #   concrete apron (0.42), so the checklist tone ladder is unbroken and strictly
        #   monotone: 0.42 ≫ 0.16 ≫ 0.082 > 0.055 > 0.030.
        #   `fresh` is untouched (= patch_color): it carries the sceneD2 confusion pair and
        #   must stay the darkest thing in the frame.
        #   The three values are **rendered**, not nominal: `Looks/Patch*` classifies as
        #   `asphalt`, so `make_pbr` promotes the constant colour onto the asphalt role
        #   texture (`_promote_const_to_texture`) and the aggregate then carries the albedo.
        #   Promotion is superlinear in the bright grains, so the first cut of this batch
        #   (`_experiments/twins/sceneN2/260730_w3_n2clean_tone0`) put `aged` 0.082 at
        #   **mean 132/255 against an apron of 163** at h0.3_d10 - a 1.23:1 step that reads
        #   as a dirty concrete slab, not as an asphalt repair. Retuned against the measured
        #   render `[measured - imgstats on the tone0 round]`.
        patch_tones=dict(
            fresh=((0.030, 0.030, 0.033), 0.92),   # this season's repaving
            cured=((0.050, 0.050, 0.053), 0.90),   # ~1 season, binder film gone
            aged=((0.068, 0.068, 0.071), 0.88),    # ~2 seasons, aggregate showing
        ),
        # ─ sealed saw-cut joint: emulsified bitumen tack coat on the cut face + 실란트
        #   overband over the seam. Bituminous black, and **smoother than the mat around it**
        #   (0.55 vs 0.88~0.92) - that roughness step is the one cue that separates a sealed
        #   joint from a bare cut, and it is why the old bright-grey 0.34 lip read as a ruled
        #   line drawn on the ground instead of as contractor work.
        #   `CutLine` classifies as **paint**, which is deliberately outside
        #   `_CONST_MDL_CLASSES`, so it is *not* promoted and the constant colour is what
        #   ships. That makes it directly comparable to the mat only after rendering: at
        #   0.045 the band came back **brighter than the mat it borders** (116 vs 77 at
        #   h0.9_d5), i.e. still a light ruled frame. 0.018 lands the band on the fresh mat
        #   (~79) and far under the apron - a seam, which is the point `[measured - tone0]`.
        cut_color=(0.018, 0.017, 0.017), cut_rough=0.55,
        joint_color=(0.06, 0.06, 0.06), joint_rough=0.85,
        asphalt_color=(0.16, 0.16, 0.17), asphalt_rough=0.90,  # old asphalt (standard)
        lane_color=(0.55, 0.55, 0.53), lane_rough=0.70,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        parapet_color=(0.88, 0.86, 0.82), parapet_rough=0.6,
        hedge_tint=(0.35, 0.45, 0.28),
        # ─ road markings: 3 wear tones (new -> faded). They must be brighter than the concrete
        #   pavement (~0.42) to read as "white paint". The faded tone is close to the pavement, so it looks missing.
        paint_tints=((0.68, 0.67, 0.64), (0.56, 0.55, 0.53), (0.45, 0.45, 0.43)),
        paint_rough=0.72,
        # ─ manhole (cast iron) : sRGB 0.02~0.06 dark colour convention
        iron_color=(0.048, 0.048, 0.050), iron_rough=0.60, iron_metallic=0.4,
        lid_color=(0.040, 0.040, 0.045), lid_rough=0.50, lid_metallic=0.6,
        # ─ context dressing
        walk_tint=(0.90, 0.89, 0.86),
        curb_color=(0.72, 0.72, 0.69), curb_rough=0.6,
        post_color=(0.55, 0.55, 0.58), post_metallic=0.5, post_rough=0.5,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.40,
        grass_tint=(0.55, 0.68, 0.42),
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        # ─ bollard v5.1: stainless body + white reflective band on top (small area) +
        #   dot tactile paving at the front (yellow). The band is 0.08 m² per unit, so not a "large pure-white area".
        bollard_color=(0.78, 0.80, 0.83), bollard_metallic=0.85,
        bollard_rough=0.34,
        bollard_band_color=(0.88, 0.88, 0.86),
        tactile_color=(0.80, 0.66, 0.14), tactile_rough=0.70,
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
    # ─── SUN_AZ_OFFSET = 171.5 (v3 §A-7 standard kept).
    #     sun mapping: world sun az ~ 33.5 + 171.5 = 205 deg -> behind and left of the camera (facing +X).
    #     shadow azimuth az_s = 205 − 180 = 25 deg -> shadows fall towards +X (slightly +Y), i.e.
    #     behind the object (away from the camera).
    #     ⇒ it is **front light**, so no long cast shadow reaches into the frame. What this scene
    #        judges is the "material dark zone (the patch)", so mixing it with shadow dark zones would
    #        contaminate the counter-example reading - an active reason to keep the standard azimuth. (The
    #        exact opposite purpose to sceneN1, which made the shadow its feature with 146.5.)
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
# [C] path constants + required texture roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneN2")

ASSET_ROLES = ["plaza_lower", "plaza_light", "gravel", "grass", "brick_red",
               "hdri", "mdl"]


# ===========================================================================
# [C2] cutting the road markings - "repaving makes the stall line vanish under the patch"
#      (no stage needed · pure geometry -> shared with markcheck())
# ===========================================================================
def repair_rects():
    """Every saw-cut repair on the apron: the 2 judged feature patches **then** the 3
    near-window maintenance repairs.

    One list, one vocabulary - `build_patches()` draws it, `paint_line_segments()` cuts the
    paint with it, and `geocheck()` tabulates it, so a repair can never exist for the
    renderer and not for the checks. Order is load-bearing only for the printed table.
    The occlusion check deliberately reads `PARAMS["patches"]` alone: it asks "can anything
    hide **the feature**", and widening that bearing span with a 1 m repair sitting 0.7 m off
    the lens would answer a different question.
    """
    return list(PARAMS["patches"]) + list(PARAMS["repairs"])


def paint_line_segments(axis, fixed, a0, a1):
    """Remove from a straight marking [a0,a1] the stretches taken by a repair (+ sealant band width + clear margin).

    axis="x": the line runs along X and `fixed` is that line's y coordinate.
    axis="y": the line runs along Y and `fixed` is its x coordinate.
    return: [(a, b), ...] (pieces shorter than 0.05 m are discarded).
    Under a patch the surface is new asphalt and no marking exists, so the line
    breaks on one side of the patch and reappears on the other = repaving realism
    (user instruction).
    At the same time any XY overlap between the marking (proud 0.0010) and the
    sealant band (0.0012) is removed at source.

    [W3 N2-CLEAN] The loop now runs over `repair_rects()`, i.e. the near-window repairs cut
    the paint too. That is not extra bookkeeping: an unbroken stall line running straight
    across a patch is the single loudest tell that the patch is a decal rather than a hole
    cut in the surface.
    """
    m = float(PARAMS["patch"]["cut_w"]) + float(PARAMS["marking"]["clear"])
    segs = [(float(a0), float(a1))]
    for pd in repair_rects():
        if axis == "x":
            if not (pd["y0"] - m <= fixed <= pd["y1"] + m):
                continue
            ca, cb = pd["x0"] - m, pd["x1"] + m
        else:
            if not (pd["x0"] - m <= fixed <= pd["x1"] + m):
                continue
            ca, cb = pd["y0"] - m, pd["y1"] + m
        nxt = []
        for a, b in segs:
            if cb <= a or ca >= b:
                nxt.append((a, b))
                continue
            if ca > a:
                nxt.append((a, ca))
            if cb < b:
                nxt.append((cb, b))
        segs = nxt
    return [(a, b) for a, b in segs if b - a > 0.05]


def build_views():
    """Camera presets: grid_views(gy=0.0) + 4 mise-en-scene cuts."""
    views = sc.grid_views(0.0)
    # approach: walking from the apron towards the patch (how the two patches read together)
    views["approach"] = dict(eye=[-6.0, 0.0, 1.6], tgt=[5.0, 0.0, 0.1])
    # patch_confusion: **same framing as sceneD2 (the opening)** - 4m back from the small patch's
    #   near end x=2.6, h0.9. Put the two scenes' captures side by side to judge the confusion pair.
    views["patch_confusion"] = dict(eye=[-1.4, 0.0, 0.9], tgt=[4.6, 0.0, 0.05])
    # patch_grazing: low-viewpoint grazing - verifies flushness (no thickness shadow)
    views["patch_grazing"] = dict(eye=[-3.0, 0.0, 0.35], tgt=[6.0, 0.0, 0.1])
    # beauty_oblique: oblique high angle - the contrast cut that reveals the patch is flat
    views["beauty_oblique"] = dict(eye=[-5.0, -4.5, 2.4], tgt=[6.0, -1.0, -0.2])
    return views


# ===========================================================================
# [C3b] irregular placement (v5.1 §3) - deterministic jitter. Builder and check use the same function.
#   Excluded (functional repeating rows, so alignment is realistic): stall lines · lane dashes · joints · stop line.
# ===========================================================================
def streetlight_placements():
    """[(name, x, y, yaw), ...] - streetlights on the kerb bearing.

    [W3 CB-3 · J-3/J-4 abolished, spec §1.2 / §10.1] The +-0.2 m position and
    +-3~8 deg arm-bearing jitter is deleted: a lamp column stands on the kerb
    line and its arm reaches over the carriageway it lights.
    """
    return [(s["name"], s["cx"], s["cy"], 0.0) for s in PARAMS["streetlights"]]


def planter_placements():
    """[(name, x, y), ...] - street-tree planters at their nominal centres.

    [W3 CB-3 · J-4 abolished] The +-0.15 m jitter is deleted; the docstring
    already conceded the planters are kerb-aligned, so the offset was pure
    decoration.
    """
    return [(p["name"], p["cx"], p["cy"]) for p in PARAMS["planters"]]


def bollard_points():
    """[v5.1 §2] Centres of the bollard row at the sidewalk-roadway interface [(x, y), ...] (spacing 1.5 m)."""
    bo = PARAMS["bollards"]
    return bc.bollard_line(bo["x0"], bo["y"], bo["x1"], bo["y"],
                           spacing=bo["spacing"])


def tactile_band_rect():
    """[W2 §12.5 (2)] **Continuous dot tactile strip** in front of the bollard row (x0, y0, x1, y1).

    Statutory position "0.3 m in front of the bollard" + the 60 cm dot depth
    standard. In this scene the front is +Y (the sidewalk side), so the strip
    extends in +Y from the bollards' front face. Coordinates derived from PARAMS (§7.4).
    """
    bo, g = PARAMS["bollards"], PARAMS["ground"]
    sb, dp = float(g["tactile_setback"]), float(g["tactile_depth"])
    fy = float(bo["front"][1])
    y_face = bo["y"] + fy * bo["r"]
    ya, yb = y_face + fy * sb, y_face + fy * (sb + dp)
    return (bo["x0"] - 0.15, min(ya, yb), bo["x1"] + 0.15, max(ya, yb))


def ground_plans():
    """[W2 ground_kit] Ground plan - the scene assembly and the CPU check use the same function."""
    g = PARAMS["ground"]
    gp = gk.plan_ground(
        "street_asphalt", region=tuple(g["region"]),
        z=float(PARAMS["apron"]["z_top"]), gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=(),                       # hard negative - 0 drop edges
        dists=(2, 5, 10), scene="sceneN2",
        tactile=("bollard",) if SCENE_CONFIG["cue_scene_dressing"] else (),
        sites=dict(manhole=[tuple(g["manhole"])],
                   gully=[tuple(p) for p in g["gullies"]],
                   tactile=dict(bollard=tactile_band_rect())),
        #  [W3 N2-CLEAN] `surface` is a **tuple** in the profile, so an override replaces it
        #  wholesale (`plan_ground`: non-dict values are assigned, not merged). Declaring the
        #  full tuple is therefore how the patch op is dropped - there is no per-op switch,
        #  and `build_patch_field`'s dims are not reachable from a caller anyway
        #  (`_compose_ops` fixes its kwargs), which is why the repairs are drawn scene-side.
        overrides=dict(infra=dict(manhole=1, gully=2, gutter_L=0,
                                  marking=()),
                       surface=(("crack", 2), ("stain", ("tire",)),
                                ("weed", 2))),
        seed=32)
    return [("apron", gp)]


# ===========================================================================
# [C4] numeric checks (no Isaac) - NEGOBS_GEOCHECK=1 python3 sceneN2_asphalt_patch.py
#   (1) marking cut table: does the stall line break at the patch and resume beyond it
#   (2) camera burial: is every view's eye outside the new solid objects' AABBs (margin 0.35)
#   (3) feature occlusion: is any new solid object inside the +-30 deg view cone between camera and patch
# ===========================================================================
def dressing_aabbs():
    """(name, xa, xb, ya, yb, z_top) for new and existing **solid** dressing. Flush
    elements such as markings and manholes are irrelevant to occlusion and burial,
    so they are excluded."""
    out = []
    cb, wk = PARAMS["curb"], PARAMS["walk"]
    for sgn, tag in ((1.0, "N"), (-1.0, "S")):
        y0 = sgn * cb["y"]
        y1 = sgn * (cb["y"] + cb["t"])
        out.append((f"Curb_{tag}", cb["x0"], cb["x1"], min(y0, y1),
                    max(y0, y1), cb["h"]))
        w0, w1 = sgn * wk["y_in"], sgn * wk["y_out"]
        out.append((f"Walk_{tag}", wk["x0"], wk["x1"], min(w0, w1),
                    max(w0, w1), wk["z_top"]))
    sl = PARAMS["streetlight"]
    ex = sl["arm_len"] + sl["head"] / 2.0
    ey = ex * math.sin(math.radians(8.0)) + sl["head"] / 2.0   # yaw jitter bound
    for name, sx, sy, _yaw in streetlight_placements():
        out.append((f"Streetlight_{name}", sx - ex, sx + ex,
                    sy - ey, sy + ey, sl["pole_h"]))
    pl = PARAMS["planter"]
    ph = pl["size"] / 2.0
    top_tree = PARAMS["walk"]["z_top"] + pl["grass_h"] + 2.2 + 0.85 + 0.24
    for name, px, py in planter_placements():
        out.append((f"Planter_{name}", px - ph, px + ph,
                    py - ph, py + ph, top_tree))
    bo = PARAMS["bollards"]
    for i, (bx, by) in enumerate(bollard_points()):
        out.extend(bc.bollard_v51_aabbs(
            f"Bollard_{i}", bx, by, PARAMS["walk"]["z_top"],
            front_dir=bo["front"], radius=bo["r"], height=bo["h"]))
    hg = PARAMS["hedge"]
    out.append(("Hedge", hg["x0"], hg["x1"], hg["y0"], hg["y1"], hg["h"]))
    for k, bd in PARAMS["buildings"].items():
        out.append((f"Building_{k}", bd["x0"], bd["x1"], bd["y0"], bd["y1"],
                    bd["h"] + 0.5))
    return out


def geocheck():
    print("=" * 72)
    print("sceneN2 검산 ① 노면 도색 절단 (패치가 구획선을 끊는가)")
    m = float(PARAMS["patch"]["cut_w"]) + float(PARAMS["marking"]["clear"])
    print("  절단 여유 m = cut_w %.3f + clear %.3f = %.3f"
          % (PARAMS["patch"]["cut_w"], PARAMS["marking"]["clear"], m))
    #  [W3 N2-CLEAN] R1~R3 are checkable numbers, so they are checked here rather than
    #  asserted in a comment: every repair is axis-aligned by construction (the rects are
    #  x0/x1/y0/y1, there is no yaw anywhere in this scene), min side >= 0.30 m
    #  [Caltrans FPMTAG ch.5], and the cross dimension is a mill-drum width.
    n_small = 0
    for pd in repair_rects():
        w, h = pd["x1"] - pd["x0"], pd["y1"] - pd["y0"]
        side = min(w, h)
        n_small += 1 if side < 0.30 - 1e-9 else 0
        print("  보수 %-7s x[%+6.2f,%+6.2f] y[%+6.2f,%+6.2f]  %.2f×%.2f m  "
              "최소변 %.2f  톤 %-5s  포설 %d패스"
              % (pd["name"], pd["x0"], pd["x1"], pd["y0"], pd["y1"], w, h,
                 side, pd["tone"], pd["passes"]))
    print("  R1 최소변 0.30 m 위반 %d건 · R2 축정렬: 전 보수 yaw 0 (구조상)"
          % n_small)
    st = PARAMS["stall"]
    n_cut = 0
    for ri, (rx0, rx1) in (("근열", st["near"]), ("원열", st["far"])):
        for yy in st["ys"]:
            segs = paint_line_segments("x", yy, rx0, rx1)
            cut = len(segs) != 1 or abs(segs[0][0] - rx0) > 1e-9 \
                or abs(segs[0][1] - rx1) > 1e-9
            n_cut += 1 if cut else 0
            print("  %s y=%+5.2f  x[%.2f,%.2f] → %s%s"
                  % (ri, yy, rx0, rx1,
                     " ".join("(%.2f..%.2f)" % s for s in segs),
                     "   ★패치가 절단★" if cut else ""))
    print("  절단된 구획선 %d개 (근열 y=0.00 / 원열 y=−2.50 이 기대값)" % n_cut)
    zs = [PARAMS["joints"]["proud"], PARAMS["marking"]["proud"],
          PARAMS["patch"]["cut_proud"], PARAMS["patch"]["proud"],
          PARAMS["patch"]["seam_proud"], PARAMS["manhole"]["proud_frame"],
          PARAMS["manhole"]["proud_lid"], PARAMS["manhole"]["proud_boss"]]
    print("  z 층서: 줄눈 %.4f < 도색 %.4f < 실란트 %.4f < 패치 %.4f "
          "< 시공이음 %.4f < 맨홀 %.4f/%.4f/%.4f" % tuple(zs))
    print("  층서 단조증가: %s"
          % ("합격" if all(b > a for a, b in zip(zs, zs[1:])) else "★불합격★"))
    boxes = dressing_aabbs()
    views = build_views()
    print("sceneN2 검산 ② 카메라 매몰 (여유 0.35 m)")
    mm, hit, worst = 0.35, 0, (None, 1e9)
    for vn, v in sorted(views.items()):
        ex_, ey_, ez_ = v["eye"]
        for nm, xa, xb, ya, yb, zt in boxes:
            if (xa - mm <= ex_ <= xb + mm and ya - mm <= ey_ <= yb + mm
                    and -mm <= ez_ <= zt + mm):
                print("  %-20s ★매몰★ %s" % (vn, nm))
                hit += 1
            d = max(xa - ex_, ex_ - xb, ya - ey_, ey_ - yb, 0.0)
            if d < worst[1]:
                worst = ("%s vs %s" % (vn, nm), d)
    print("  최근접(수평) %s = %.2f m → %s"
          % (worst[0], worst[1], "합격" if hit == 0 else "불합격"))
    print("sceneN2 검산 ③ 특색(패치) 폐색 — 방위구간 중첩 × 패치보다 근접")
    #   occlusion holds when (1) the object's horizontal bearing span overlaps the patch's span and
    #   (2) the object is nearer than the patch. (They sit on the ground, so if the bearings do not
    #    overlap the object is off to one side on screen and cannot hide the patch.)
    def _bearing_span(ex_, ey_, vyaw, corners):
        rels = []
        for cx_, cy_ in corners:
            rels.append((math.degrees(math.atan2(cy_ - ey_, cx_ - ex_))
                         - vyaw + 540.0) % 360.0 - 180.0)
        lo, hi = min(rels), max(rels)
        if hi - lo > 180.0:                 # plates that wrap around the camera (sidewalk, kerb, etc.)
            return -180.0, 180.0
        return lo, hi

    bad = 0
    for vn, v in sorted(views.items()):
        ex_, ey_ = v["eye"][0], v["eye"][1]
        vyaw = math.degrees(math.atan2(v["tgt"][1] - ey_, v["tgt"][0] - ex_))
        pc = [(px, py) for pd in PARAMS["patches"]
              for px in (pd["x0"], pd["x1"]) for py in (pd["y0"], pd["y1"])]
        plo, phi = _bearing_span(ex_, ey_, vyaw, pc)
        d_far = max(math.hypot(px - ex_, py - ey_) for px, py in pc)
        for nm, xa, xb, ya, yb, zt in boxes:
            if zt < 0.05:                   # a flush plate (sidewalk slab) cannot occlude
                continue
            cor = [(cx_, cy_) for cx_ in (xa, xb) for cy_ in (ya, yb)]
            olo, ohi = _bearing_span(ex_, ey_, vyaw, cor)
            d_min = min(math.hypot(cx_ - ex_, cy_ - ey_) for cx_, cy_ in cor)
            if ohi < plo or olo > phi:      # bearings do not overlap -> off to one side
                continue
            if d_min < d_far:
                print("  %-20s ★폐색 위험★ %s (방위 %.1f..%.1f vs 패치 %.1f..%.1f,"
                      " 거리 %.1f < %.1f)"
                      % (vn, nm, olo, ohi, plo, phi, d_min, d_far))
                bad += 1
    print("  판정 ③: %s" % ("전 뷰 무폐색 (합격)" if bad == 0
                            else "%d건 (검토 필요)" % bad))
    print("=" * 72)


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]  ※ 이 씬은 GT = 전 픽셀 "낙차 없음" (hard negative)
 1. patch_confusion (PT) — 소형 패치(1.5×2.0)가 sceneD2 개구부처럼 "구멍"으로
                            읽히는가 = 혼동쌍 성립 여부 [1순위]
 2. approach / h0.9_d5   — 대형 패치 절단면이 크리스프한가, 실란트 밴드가 **그려진
                            선이 아니라 이음매**로 읽히는가(어둡고 약간 매끈)
 2b. 시공 규율 [W3]      — 전 보수가 (a) 직사각형 (b) 차로축 정렬 (c) 절삭폭 어휘
                            (1.0~1.2 / 2.0 m) (d) 4.0 m 대형 패치의 종방향
                            시공이음 1줄이 보이는가. 아니면 "작업"이 아니라
                            "얼룩"으로 읽힌다
 3. patch_grazing        — 완전 flush(proud 0.002): 패치 두께 그림자·단차 부재
 4. 톤 서열              — 콘크리트(~0.42) ≫ 구 아스팔트(0.16) ≫ 노후(0.068) >
                            경화(0.050) > 신설(0.030). 3개 보수 시기가 구분되는가
 5. 기하                 — 줄눈(0.0006)<도색(0.0010)<실란트(0.0012)<패치(0.0020)
                            <시공이음(0.0023)<맨홀(0.0026/32/38) 6층 Z분리,
                            평판 겹침 없음
 6. 노면 문양            — 주차 구획선이 **패치 아래로 사라졌다 반대편에서
                            이어지는가**(근열 y=0 / 원열 y=−2.5). 마모 3톤·
                            10% 결락이 도색으로 읽히는가
 7. 맥락(드레싱)         — 연석·보도·가로등·가로수·정지선·차도 실선/파선으로
                            "주차장 → 차도"가 읽히는가 (NEGOBS_GEOCHECK=1 대조)"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene32")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene32"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def DISC(path, center, r, h, mtl=None, seg=32, col=False):
        """[W2 fix batch F5] n-gon prism - the manhole silhouette. An analytic
        `UsdGeom.Cylinder` is tessellated by Hydra at its own low default, which is
        what renders these covers as an octagon / 12-gon at d2 (defect D4)."""
        return sc.add_disc(stage, path, center, r, h, mtl, seg=seg, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    def SLAB(path, p, mtl, col=True):
        """Axis-aligned pavement plate with top face z_top and thickness thick."""
        return BOX(path,
                   ((p["x0"] + p["x1"]) / 2.0, (p["y0"] + p["y1"]) / 2.0,
                    p["z_top"] - p["thick"] / 2.0),
                   (p["x1"] - p["x0"], p["y1"] - p["y0"], p["thick"]),
                   mtl, col=col)

    # -------------------------------------------------------------------
    # materials
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["apron"] = PBR(
            f"{ROOT}/Looks/Apron", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
            sca["plaza_lower"], tint=mp["apron_tint"])
        M["gravel"] = PBR(
            f"{ROOT}/Looks/Gravel", sc.tex_path("gravel", "diff"),
            sc.tex_path("gravel", "nor"), sc.tex_path("gravel", "rough"),
            sca["gravel"])
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            sca["brick_red"])
        M["patch"] = PBR(f"{ROOT}/Looks/Patch",
                         diffuse_color=mp["patch_color"],
                         roughness_const=mp["patch_rough"], metallic=0.0)
        # ─ [W3 N2-CLEAN] one material per oxidation age. `fresh` is deliberately a **second
        #   prim bound to the same numbers** as `Looks/Patch` rather than an alias, so the
        #   tone table stays readable as a table; the cost is 2 extra Looks prims.
        M["patch_tone"] = {}
        for _name, (_col, _rgh) in mp["patch_tones"].items():
            M["patch_tone"][_name] = PBR(
                f"{ROOT}/Looks/Patch_{_name}", diffuse_color=_col,
                roughness_const=_rgh, metallic=0.0)
        M["cut"] = PBR(f"{ROOT}/Looks/CutLine",
                       diffuse_color=mp["cut_color"],
                       roughness_const=mp["cut_rough"], metallic=0.0)
        M["joint"] = PBR(f"{ROOT}/Looks/Joint",
                         diffuse_color=mp["joint_color"],
                         roughness_const=mp["joint_rough"], metallic=0.0)
        # [W2 fix batch F1] Ground-class decal materials for the kit.
        #   Binding kit crack / stain / wear elements to the scene's joint-sealant
        #   (`paint` class), steel (`metal`) or kerb constants is what rendered them
        #   as flat texture-less ribbons and mats: those classes are excluded from
        #   `_CONST_MDL_CLASSES` **by design** (a constant colour is physically right
        #   for paint and metal), so a *ground* prim bound to one gets no texture at
        #   all. `GKitCrack` / `GKitStain` classify as concrete, so they are promoted
        #   to a real ground texture with the intended albedo preserved.
        M["gk_crack"] = PBR(f"{ROOT}/Looks/GKitCrack",
                            diffuse_color=(0.055, 0.055, 0.056),
                            roughness_const=0.92)
        M["gk_stain"] = PBR(f"{ROOT}/Looks/GKitStain",
                            diffuse_color=(0.20, 0.20, 0.195),
                            roughness_const=0.86)
        M["asphalt"] = PBR(f"{ROOT}/Looks/Asphalt",
                           diffuse_color=mp["asphalt_color"],
                           roughness_const=mp["asphalt_rough"], metallic=0.0)
        M["lane"] = PBR(f"{ROOT}/Looks/Lane", diffuse_color=mp["lane_color"],
                        roughness_const=mp["lane_rough"], metallic=0.0)
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        # ─ road markings, 3 tones (wear) ─
        M["paint"] = []
        for i, t in enumerate(mp["paint_tints"]):
            M["paint"].append(PBR(f"{ROOT}/Looks/Paint_{i}", diffuse_color=t,
                                  roughness_const=mp["paint_rough"],
                                  metallic=0.0))
        M["iron"] = PBR(f"{ROOT}/Looks/Iron", diffuse_color=mp["iron_color"],
                        metallic=mp["iron_metallic"],
                        roughness_const=mp["iron_rough"], specular_level=0.3)
        M["lid"] = PBR(f"{ROOT}/Looks/Lid", diffuse_color=mp["lid_color"],
                       metallic=mp["lid_metallic"],
                       roughness_const=mp["lid_rough"], specular_level=0.3)
        # ─ context dressing ─
        M["walk"] = PBR(
            f"{ROOT}/Looks/Walk", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            sca["plaza_light"], tint=mp["walk_tint"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["curb"] = PBR(f"{ROOT}/Looks/Curb", diffuse_color=mp["curb_color"],
                        roughness_const=mp["curb_rough"])
        M["post"] = PBR(f"{ROOT}/Looks/Post", diffuse_color=mp["post_color"],
                        metallic=mp["post_metallic"],
                        roughness_const=mp["post_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
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
        # ─ bollard v5.1 (body / reflective band / front dot tactile paving) ─
        M["bollard_body"] = PBR(f"{ROOT}/Looks/BollardBody",
                                diffuse_color=mp["bollard_color"],
                                metallic=mp["bollard_metallic"],
                                roughness_const=mp["bollard_rough"])
        M["bollard_band"] = PBR(f"{ROOT}/Looks/BollardBand",
                                diffuse_color=mp["bollard_band_color"],
                                roughness_const=0.30)
        # [W2 · ground_kit §12.5-3] texture-backed so the 36 dots actually shade.
        M["tactile"] = bc.tactile_mtl(stage, f"{ROOT}/Looks/Tactile")
        return M

    # -------------------------------------------------------------------
    # pavement - apron / old asphalt roadway / gravel verge (all flat, no opening at all)
    #   Adjacent plates overlap by 0.05 in X but drop z_top by 2mm each, avoiding coplanarity and gaps at once.
    # -------------------------------------------------------------------
    def build_ground(M):
        # [W2-0 · P-A] the apron top face is what ground_kit decorates -> displacement skin
        #   OFF. `add_box` calls `_skin_wanted` right there, so register it **before the SLAB
        #   call** `[spec §1.2]`. The roadway (Road) follows the same rule because its markings
        #   and dashes are flush (0.002).
        sc.skin_exclude(f"{ROOT}/Apron", f"{ROOT}/Road")
        SLAB(f"{ROOT}/Apron", PARAMS["apron"], M["apron"])
        SLAB(f"{ROOT}/Road", PARAMS["road"], M["asphalt"])
        SLAB(f"{ROOT}/Verge", PARAMS["verge"], M["gravel"])

    # -------------------------------------------------------------------
    # [W2] ground_kit - P4 street_asphalt. For filling the near windows only (joints, gutter and
    #   markings are already in the scene). 0 drop edges -> GT-E1′/GT-E2 are vacuously true.
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        (_tag, gp), = ground_plans()
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        #  [W3 N2-CLEAN] `patch_cut` / `stain_oil` retired with the ops that requested them
        #  (kit patch -> 0, oil stain dropped). `M["patch"]` survives under its own key from
        #  `dict(M)` and is still what `build_patches` falls back to.
        M2.update(joint=M["joint"], crack=M["gk_crack"], manhole=M["lid"],
                  gully=M["iron"], gutter=M["curb"], weed=M["grass"],
                  tactile=M["tactile"], stain_tire=M["gk_stain"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] sceneN2 P4 · 프림 {res['prims']} · 산포 "
              f"{res['instances']} · δmax {res['gt_delta_max']:.4f} · "
              f"unit_cell {res['unit_cell']}")
        return res

    def build_joints(M):
        """Apron slab joints - the lowest layer (proud 0.0006). Where they run under a
        patch they are fully contained in the patch plate volume (0.05 thick) and
        are naturally hidden."""
        j = PARAMS["joints"]
        w, pr = j["width"], j["proud"]
        thk = pr + 0.006
        cz = PARAMS["apron"]["z_top"] + pr - thk / 2.0
        Lx = j["x1"] - j["x0"]
        Ly = j["y1"] - j["y0"]
        n = int(round(Ly / j["spacing"])) + 1
        for i in range(n):
            yy = j["y0"] + i * j["spacing"]
            BOX(f"{ROOT}/JointX_{i}", ((j["x0"] + j["x1"]) / 2.0, yy, cz),
                (Lx, w, thk), M["joint"])
        m = int(round(Lx / j["spacing"])) + 1
        for i in range(m):
            xx = j["x0"] + i * j["spacing"]
            BOX(f"{ROOT}/JointY_{i}", (xx, (j["y0"] + j["y1"]) / 2.0, cz),
                (w, Ly, thk), M["joint"])

    # -------------------------------------------------------------------
    # saw-cut repairs: mat + sealed joint + cold joint (the feature - GT is still "no drop")
    #
    # [W3 N2-CLEAN] One builder for all 5 repairs (2 judged feature patches + 3 near-window
    #   maintenance repairs), which is what makes them read as one contractor's work rather
    #   than as two unrelated systems. Per repair:
    #     mat   1 prim - the milled-and-filled rectangle, tone by oxidation age (R4 ladder)
    #     seal  4 prims - the 실란트 overband over the tack-coated saw cut, laid **outside**
    #                     the perimeter so it sits on the old surface, which is where a real
    #                     overband goes and which keeps it clear of the mat in XY *and* z
    #     seam  passes-1 prims - the longitudinal cold joint between mill passes, laid **on**
    #                     the mat (proud 0.0023 > 0.0020). Only the 4.0 m main patch has one.
    #   Prim delta vs the old builder: 2 patches × 5 = 10  ->  5 repairs × 5 + 1 seam = 26.
    # -------------------------------------------------------------------
    def build_patches(M):
        pc = PARAMS["patch"]
        z_apron = PARAMS["apron"]["z_top"]
        for pd in repair_rects():
            nm = pd["name"]
            x0, x1, y0, y1 = pd["x0"], pd["x1"], pd["y0"], pd["y1"]
            z_hi = z_apron + pc["proud"]
            mtl = M["patch_tone"].get(pd.get("tone"), M["patch"])
            BOX(f"{ROOT}/Patch_{nm}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, z_hi - pc["thick"] / 2.0),
                (x1 - x0, y1 - y0, pc["thick"]), mtl)
            #  cold joint between mill passes. A 4.0 m cross dimension is two 2.00 m drum
            #  passes, and the seam between them is sealed exactly like the perimeter - it
            #  is the detail that says "a machine laid this in passes", not "a dark
            #  rectangle was placed here". Seams run along the **long** axis of the mat.
            n_pass = int(pd.get("passes", 1))
            if n_pass > 1:
                along_x = (x1 - x0) >= (y1 - y0)
                zs = z_apron + pc["seam_proud"] - pc["seam_thick"] / 2.0
                for k in range(1, n_pass):
                    f = float(k) / n_pass
                    if along_x:
                        sy_ = y0 + f * (y1 - y0)
                        BOX(f"{ROOT}/Seam_{nm}_{k}",
                            ((x0 + x1) / 2.0, sy_, zs),
                            (x1 - x0, pc["seam_w"], pc["seam_thick"]), M["cut"])
                    else:
                        sx_ = x0 + f * (x1 - x0)
                        BOX(f"{ROOT}/Seam_{nm}_{k}",
                            (sx_, (y0 + y1) / 2.0, zs),
                            (pc["seam_w"], y1 - y0, pc["seam_thick"]), M["cut"])
            if not cfg["cue_material_break"]:
                continue
            # sealant overband: cut_w outside the repair perimeter (no XY overlap with the
            #   mat + separated in z too). Prim path kept as `CutLine_*` on purpose - it is
            #   the same saw cut, now sealed, and renaming it would break every round stamp,
            #   crop reference and report that names the prim.
            w = pc["cut_w"]
            zc = z_apron + pc["cut_proud"] - pc["cut_thick"] / 2.0
            strips = (
                ("S", (x0 + x1) / 2.0, y0 - w / 2.0, x1 - x0 + 2.0 * w, w),
                ("N", (x0 + x1) / 2.0, y1 + w / 2.0, x1 - x0 + 2.0 * w, w),
                ("W", x0 - w / 2.0, (y0 + y1) / 2.0, w, y1 - y0),
                ("E", x1 + w / 2.0, (y0 + y1) / 2.0, w, y1 - y0),
            )
            for tag, cx, cy, sx, sy in strips:
                BOX(f"{ROOT}/CutLine_{nm}_{tag}", (cx, cy, zc),
                    (sx, sy, pc["cut_thick"]), M["cut"])

    # -------------------------------------------------------------------
    # road markings - parking stall lines (wear and gaps) + stop line + aisle arrow + manhole
    #   * the stall lines have their patch stretches cut out by paint_line_segments():
    #     "the line vanishes under the patch and resumes beyond it" (repaving realism).
    #   * wear: split into 0.9 m tiles -> 3-tone random tint + 10% gaps (fixed seed).
    #     The first and last tile of a segment are never dropped, so the line's start and end always read.
    # -------------------------------------------------------------------
    def build_markings(M):
        mk = PARAMS["marking"]
        rng = random.Random(int(mk["seed"]))
        z_top = PARAMS["apron"]["z_top"] + mk["proud"]
        zc = z_top - mk["thick"] / 2.0
        n_tile = [0]

        def paint_run(tag, axis, fixed, a0, a1, width, wear=True):
            """Cut [a0,a1] with the patches, split into tiles and lay the marking plates."""
            for si, (a, b) in enumerate(paint_line_segments(axis, fixed, a0, a1)):
                nt = max(1, int(round((b - a) / mk["tile"])))
                for i in range(nt):
                    ta = a + (b - a) * i / nt
                    tb = a + (b - a) * (i + 1) / nt
                    if wear and 0 < i < nt - 1 and rng.random() < mk["gap_prob"]:
                        continue                    # gap (stretch worn away)
                    mtl = M["paint"][rng.randrange(len(M["paint"]))] if wear \
                        else M["paint"][0]
                    if axis == "x":
                        c, s = ((ta + tb) / 2.0, fixed), (tb - ta, width)
                    else:
                        c, s = (fixed, (ta + tb) / 2.0), (width, tb - ta)
                    BOX(f"{ROOT}/Mark/{tag}_{si}_{i}", (c[0], c[1], zc),
                        (s[0], s[1], mk["thick"]), mtl)
                    n_tile[0] += 1

        st = PARAMS["stall"]
        for ri, (rx0, rx1) in (("N", st["near"]), ("F", st["far"])):
            for yi, yy in enumerate(st["ys"]):
                paint_run(f"Stall{ri}_{yi}", "x", yy, rx0, rx1, st["width"])
        sh = PARAMS["stall_head"]
        for hd in PARAMS["stall_heads"]:
            paint_run(f"StallHead_{hd['name']}", "y", hd["x"], sh["y0"],
                      sh["y1"], sh["width"])
        sl = PARAMS["stopline"]
        paint_run("StopLine", "y", sl["x"], sl["y0"], sl["y1"], sl["width"],
                  wear=False)
        # solid roadway edge lines (far and continuous - no tile split needed)
        el = PARAMS["edge_line"]
        zr = PARAMS["road"]["z_top"] + PARAMS["lane"]["proud"] \
            - PARAMS["lane"]["thick"] / 2.0
        for ed in PARAMS["edge_lines"]:
            BOX(f"{ROOT}/Mark/Edge_{ed['name']}",
                (ed["x"], (el["y0"] + el["y1"]) / 2.0, zr),
                (el["width"], el["y1"] - el["y0"], PARAMS["lane"]["thick"]),
                M["lane"])
        # aisle direction arrow (+Y one-way) - shaft (1) + 2 oblique head strokes (3 prims total)
        ar = PARAMS["arrow"]
        a = math.radians(float(ar["yaw"]))
        ux, uy = math.cos(a), math.sin(a)             # arrow travel direction
        BOX(f"{ROOT}/Mark/Arrow/Shaft",
            (ar["cx"], ar["cy"], zc),
            (ar["shaft_w"] if abs(ux) < 0.5 else ar["shaft_len"],
             ar["shaft_len"] if abs(ux) < 0.5 else ar["shaft_w"],
             mk["thick"]), M["paint"][0])
        tip = (ar["cx"] + ux * ar["shaft_len"] * 0.5,
               ar["cy"] + uy * ar["shaft_len"] * 0.5)
        for sgn, tag in ((1.0, "P"), (-1.0, "N")):
            ang = ar["yaw"] + 180.0 - sgn * ar["head_ang"]
            ra = math.radians(ang)
            cxh = tip[0] + math.cos(ra) * ar["head_len"] / 2.0
            cyh = tip[1] + math.sin(ra) * ar["head_len"] / 2.0
            sc._oriented_box(stage, f"{ROOT}/Mark/Arrow/Head_{tag}",
                             (cxh, cyh, zc),
                             (ar["head_len"], ar["head_w"], mk["thick"]),
                             M["paint"][0], rotz=ang)
        # 1 small manhole (cast iron, flush). Its 3 proud layers sit above the markings and patch [see stratigraphy]
        mh = PARAMS["manhole"]
        for tag, r, pr, mtl in (("Frame", mh["r_frame"], mh["proud_frame"], M["iron"]),
                                ("Lid", mh["r_lid"], mh["proud_lid"], M["lid"]),
                                ("Boss", mh["r_boss"], mh["proud_boss"], M["lid"])):
            DISC(f"{ROOT}/Manhole/{tag}",
                (mh["cx"], mh["cy"],
                 PARAMS["apron"]["z_top"] + pr - mh["h"] / 2.0),
                r, mh["h"], mtl)
        print(f"[도색] 구획·정지선 타일 {n_tile[0]}매 · 화살표 3 · 맨홀 3 · "
              f"차도 실선 {len(PARAMS['edge_lines'])}")

    # -------------------------------------------------------------------
    # dressing - lane dashes + kerb and sidewalk + streetlights and street trees + bollards + hedge
    #          + far buildings (skyline + street wall beyond the sidewalk)
    # -------------------------------------------------------------------
    def build_dressing(M):
        ln = PARAMS["lane"]
        period = ln["dash"] + ln["gap"]
        n = int((ln["y1"] - ln["y0"]) / period) + 1
        zc = PARAMS["road"]["z_top"] + ln["proud"] - ln["thick"] / 2.0
        for i in range(n):
            ya = ln["y0"] + i * period
            yb = min(ya + ln["dash"], ln["y1"])
            if yb - ya < 0.2:
                continue
            BOX(f"{ROOT}/LaneDash_{i}", (ln["x"], (ya + yb) / 2.0, zc),
                (ln["width"], yb - ya, ln["thick"]), M["lane"])
        # kerb + sidewalk (symmetric in +-Y). The kerb is a raised strip on flat ground - the ground on
        # both sides is z~0, so it is **not a drop** (GT unchanged). The sidewalk plate is flush at proud 0.003.
        cb, wk = PARAMS["curb"], PARAMS["walk"]
        for sgn, tag in ((1.0, "N"), (-1.0, "S")):
            BOX(f"{ROOT}/Curb_{tag}",
                ((cb["x0"] + cb["x1"]) / 2.0,
                 sgn * (cb["y"] + cb["t"] / 2.0), cb["h"] / 2.0),
                (cb["x1"] - cb["x0"], cb["t"], cb["h"]), M["curb"], col=True)
            BOX(f"{ROOT}/Walk_{tag}",
                ((wk["x0"] + wk["x1"]) / 2.0,
                 sgn * (wk["y_in"] + wk["y_out"]) / 2.0,
                 wk["z_top"] - 0.20),
                (wk["x1"] - wk["x0"], wk["y_out"] - wk["y_in"], 0.4),
                M["walk"], col=True)
        sl = PARAMS["streetlight"]
        for name, sx, sy, syaw in streetlight_placements():
            # v5.1 §3: rotate the arm bearing slightly off axis-parallel to remove the cloned look
            base = sc.build_rot_group(stage, f"{ROOT}/Streetlight_{name}",
                                      (sx, sy), syaw)
            CYL(f"{base}/Pole", (sx, sy, sl["pole_h"] / 2.0),
                sl["pole_r"], sl["pole_h"], M["post"], col=True)
            for sg, tag in ((1.0, "P"), (-1.0, "N")):
                CYL(f"{base}/Arm_{tag}",
                    (sx + sg * sl["arm_len"] / 2.0, sy,
                     sl["pole_h"] - 0.10), sl["arm_r"], sl["arm_len"],
                    M["post"], rotY=90.0)
                BOX(f"{base}/Head_{tag}",
                    (sx + sg * sl["arm_len"], sy, sl["pole_h"] - 0.15),
                    (sl["head"], sl["head"], 0.12), M["lamp"])
        pl = PARAMS["planter"]
        for name, px, py in planter_placements():
            sc.build_planter(
                stage, f"{ROOT}/Planter_{name}", px, py,
                PARAMS["walk"]["z_top"], M["curb"], M["grass"],
                tree_mtls=(M["wood"], M["canopy_a"], M["canopy_b"]),
                size=pl["size"], curb_h=pl["curb_h"], curb_t=pl["curb_t"],
                cap_over=pl["cap_over"], cap_h=pl["cap_h"],
                grass_h=pl["grass_h"])
        # bollards [v5.1 §2] - sidewalk-roadway interface, 0.45 m outside the kerb, spacing 1.5 m,
        #   white reflective band on top + 0.3 m dot tactile paving at the front (sidewalk side +Y).
        bo = PARAMS["bollards"]
        for i, (bx, by) in enumerate(bollard_points()):
            # [W2 §12.5 (2)] the per-unit small plate -> replaced by ground_kit's
            #   **continuous 0.60 m strip** (legibility). If not turned off here the dot band becomes 0.9 m.
            bc.build_bollard_v51(stage, f"{ROOT}/Bollard_{i}", bx, by,
                                 PARAMS["walk"]["z_top"], None,
                                 M["bollard_body"], M["bollard_band"],
                                 M["tactile"], front_dir=bo["front"],
                                 radius=bo["r"], height=bo["h"],
                                 tactile=False)
        # [GT-63] clipped hedge bands: box+crown blobs -> fused rows of real
        #   shrub USDs (place_hedge_row; rects/heights/prim roots unchanged;
        #   legacy build_hedge fallback inside).
        hg = PARAMS["hedge"]
        n_hedge = sc.place_hedge_row(
            stage, f"{ROOT}/Hedge", hg["x0"], hg["y0"], hg["x1"],
            hg["y1"], hg["h"], gk.det_seed("sceneN2.hedge", 0),
            base_z=PARAMS["verge"]["z_top"], fallback_tint=mp["hedge_tint"])
        print(f"[GT-63] 생울타리 실관목 {n_hedge}주 "
              f"(place_hedge_row · 폴백 {'무' if n_hedge else 'build_hedge'})")
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()

    build_ground(M)
    if cfg["cue_material_break"]:
        build_joints(M)
    if cfg["hazard_asphalt_patch"]:
        build_patches(M)
    if cfg["cue_scene_dressing"]:
        build_markings(M)                # road markings (the patch cuts the stall lines)
        build_dressing(M)
    build_ground_kit(M)                  # [W2] ground elements - after the dressing (scatter order convention)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneN2 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["beauty_oblique"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneN2_{ts}.png")
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
    if os.environ.get("NEGOBS_GEOCHECK", "0") == "1":
        geocheck()                     # check only markings and dressing, without booting Isaac
    else:
        main()
