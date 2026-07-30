# -*- coding: utf-8 -*-
"""
sceneC2_leaf_stairs.py — NegObs synthetic scene 27: leaf-buried stone stair (Isaac Sim 4.5)

Type    : C2 condition variant (geometry invariant · cue buried under an environment layer)
Spec    : Docs/nanobanana_batch1_geometry_map.md §B sceneC2_leaf_stairs
          Docs/multi_scene_brief_v3.md §A regression-prevention checklist
Shared  : scene_common.py · skeleton convention scene16_canopy_shadow.py
Look ref: look_refs/c2_leaf_stairs.jpg (the generated image is a view from below — **the
          implementation follows the prompt intent: upper approach viewpoint, top 3 steps buried**)

Hazard  : a 14-step park stone stair descends in +X from the upper approach path. A thick
          leaf layer **completely buries the first 3 steps**, so the stair start edge (the
          drop boundary) is lost, and the crest line of the leaf mound (x≈-0.25, z≈+0.20)
          hides everything beyond it. Steps 4~6 are partly buried at the centre only
          (progressive exposure); only step 7 and below stay fully exposed.
          **The only cue that the descent continues = the descending diagonal of the
          one-sided railing, 1 line.**
Goal    : assemble upper approach path + stone stair (+ coping on both flanks) + a 2-tier
          leaf layer (burial mound + near-field scatter) + 1 railing line + side grass
          slopes and autumn trees; render and judge.
GT      : stair drop positive (geometry invariant, drop 2.24 m). Extreme case of cue burial.

Run (GUI look check — default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneC2_leaf_stairs.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python sceneC2_leaf_stairs.py
Smoke early exit:         NEGOBS_SMOKE=1  python sceneC2_leaf_stairs.py

Coordinates: Z-up, m, travel axis +X, drop start edge = x=0 (stair top = approach shoulder).

────────────────────────────────────────────────────────────────────────────
Geometry core (numeric check — for the director to re-verify)
  riser 0.16 · tread 0.34 · n 14  → run 4.76 · drop 2.24 (z_bot −2.24)
  nosing line   z(x) = −(riser/tread)·x = −0.4706·x
  coping        top face = nosing line + 0.12 (both flanks y 1.28..1.62, symmetric)
  3 leaf mounds (build_slope = rotateY sloped box):
    A approach carpet : x −3.20..−0.10, top +0.06 → +0.13 (reverse slope = edge deposition)
    B burial ramp     : x −0.25.. 1.02, top +0.20 → −0.390 (slope 0.4643 < 0.4706)
                    → covers the tops of steps 1~3 (−0.16/−0.32/−0.48) by +0.086~0.090 at all times
                    → **at x=0 the leaf surface is +0.084 = a crest above the approach (0)** ⇒
                      the stair start edge geometrically disappears from the sight line
    C transition ramp : x  1.02.. 2.38, the top follows 0.03~0.06 below the nosing line,
                    width y ±0.90 (centre only) → fills the tread hollows of steps 4~7
                    **at the centre only**, leaving the nosing edges and 0.4m at each end
                    exposed (progressive exposure); step 8 and below fully exposed
  * the spec's "_oriented_box sloped plate" needs rotY (+X descending slope), but _oriented_box
    supports only rotZ/rotX → implemented with sc.build_slope (rotateY sloped box) for the same
    purpose. _oriented_box is used for the 2 side leaf drifts, which need **rotX (transverse crown)**.
────────────────────────────────────────────────────────────────────────────
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
# [A] SCENE_CONFIG - standard 7 keys + 1 scene-identity key (leaf_cover)
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False -> stair·slope become z=0 flat ground (geometry toggle)
    "cue_railing":        True,    # **one-sided railing, 1 line** - the only cue over the buried run (identity)
    "cue_tactile":        False,   # not the practice on park stone stairs (code path only)
    "cue_material_break": True,    # approach dirt path vs stone stair material contrast
    "cue_nosing":         False,   # anti-slip strip is not the practice on worn park stone (code path only)
    "cue_sign":           False,   # [optional] not implemented - key reserved only
    "cue_scene_dressing": True,    # autumn trees·hedges·distant ridges, all together
    # ─ identity toggle: False -> remove every leaf mound·scatter = same-geometry twin ─
    "leaf_cover":         True,
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # --- stone stair, 14 steps (riser 0.16 · tread 0.34 -> run 4.76 · drop 2.24) ---
    stairs=dict(x0=0.0, riser=0.16, tread=0.34, nsteps=14,
                y0=-1.30, y1=1.30, z_top=0.0, base_z=-3.30),
    # --- coping on both flanks (stone coping) : 0.12 above the nosing line, y 1.28..1.62 ---
    coping=dict(y_in=1.28, y_out=1.62, rise=0.12, ext=0.25, thick=0.55),
    # --- upper approach path (dirt) : x −20 .. +0.02 (0.02 overlap with the stair = step-1 riser) ---
    upper=dict(x0=-20.0, x1=0.02, y_half=1.62, z_top=0.0, thick=0.60),

    # ═══ [W2 ground_kit] P3 sidewalk_block - spec §5.2 C2 · §8.4 ═══════════
    #  * **minimal intervention is the prescription.** Leaf globalisation (G2)
    #    alone already fills the near window here and passes at σ_LF 7.82 -
    #    scatter on top only eats budget, the frame does not change `[spec §8.3]`. So:
    #      · ground_kit **scatter allocation 0** (no `scatter` callback is injected)
    #      · urban infrastructure (manhole·gully·gutter) **0 items** - this is a park dirt path
    #      · random surface elements (patch·crack·grime·weed) **0 items**
    #    What remains is two things, **5 prims** in total.
    #  (1) approach paving division joints - step 3.0 m, **width 0.05** (§8.4 (2) - at
    #     Poisson cover 0.32 1 leaf averages 0.0435 ㎡ (0.21 m a side), so the value
    #     was raised 0.04 -> 0.05 so a leaf cannot cover the line whole). The x range,
    #     per the §8.4 (1) judgment, **aligns with the G2 upstream start x=−10.60**
    #     (the leading 0.40 m of the old −11.00 sits behind the d10 eye(−10.0) = out of frame).
    #     * the material binds to `stone` - the approach path in this scene is a
    #       `dirt_park` dirt path, so a "block joint" does not hold. A flush 50 mm
    #       wide stone strip is a real detail of Korean park dirt paths (a compaction-
    #       section division strip) and still satisfies the **line visibility** spec §8.4 requires.
    #  (2) 2 leaf<->ground **lateral** boundary break-up bands - §8.4 (3) judgment. G2
    #     pushed the travel-axis boundary behind the d10 eye ("no leaf-field boundary
    #     inside the frame"), so v1's travel-axis band would **decorate a boundary that
    #     is not there**. Relocated to the lateral boundary `|y| = 3.60`.
    #     * the x range **cuts §8.4 (3)'s `−3.76…6.26` down to −3.76…0.00**:
    #       at x>0 the `\|y\|=3.60` locus is the side grass **slope** (z = −0.4706·x),
    #       so a flat z=0 band would float 2.24 m at x=4.76 `[computed]`.
    gkit=dict(
        joint_x0=-10.60, joint_x1=-0.30, joint_step=3.0, joint_w=0.05,
        joint_recess=-0.003,
        edge_break_y=3.60, edge_break_x0=-3.76, edge_break_x1=0.0,
        edge_break_w=0.20,
    ),
    # --- lower entry path : 1.0 underlap beneath the stair + top face sunk 0.002 (no coplanar faces) ---
    # x_pad 46 : the ground must reach the distant ridges (RUN+24 / RUN+33, thickness
    #            6~8) so no ridge base floats and no void opens at the ground edge (brief §A-4)
    lower=dict(x_pad=46.0, under_lap=1.0, y_half=1.62, sink=0.002, thick=0.60),
    # --- side grass slope (stair corridor y +-1.58 left empty, top face sunk 0.005) ---
    slopes=dict(y_in=1.58, y_edge=40.0, thick=0.80, sink=0.005),
    # --- ground slabs (upper·lower, outside the slopes) ---
    ground=dict(y_edge=40.0, thick=0.60),

    # --- leaf (1) burial mound (3 build_slope sloped plates) ---
    #     dict(x0, z0, run, drop, y_half, thick) - top face = (x0,z0)->(x0+run, z0−drop)
    mound=[
        # A approach carpet: top face +0.06 -> +0.13 (reverse slope drop<0 = edge deposition).
        #   bottom face −0.09..−0.02 -> buried into the approach path (z=0), no floating.
        dict(name="A", x0=-3.20, z0=0.06, run=3.10, drop=-0.07,
             y_half=2.40, thick=0.15),
        # B burial ramp: crest x=−0.25(z=+0.20) -> x=+1.02(z=−0.390) = **rear of step 3**.
        #   slope 0.4643 < nosing line 0.4706 -> always covers the top of steps 1~3 by +0.086~0.090.
        #   at the end (x=1.02) the bottom face −0.540 < step-3 top −0.48 -> the plate ends
        #   buried in the stair solid => the per-tread inner pocket (~9 cm between plate
        #   bottom and tread) is sealed by **upstream=mound A / downstream=B's buried part /
        #   flanks=coping (y1.28~1.62, B is +-1.33)** - no light leak, no visible slit. All that
        #   is exposed is the leaf layer's end section (h~0.115~0.15), matching a real leaf bank edge.
        dict(name="B", x0=-0.25, z0=0.20, run=1.27, drop=0.5897,
             y_half=1.33, thick=0.15),
        # C transition ramp: the top face follows 0.03~0.06 below the nosing line (−0.4706x)
        #   -> fills only the tread hollow and **leaves the nosing edge exposed** (progressive-exposure run).
        #   at its end (x=2.38) it sinks inside the step-7 solid, so no end face is exposed.
        dict(name="C", x0=1.02, z0=-0.505, run=1.36, drop=0.675,
             y_half=0.90, thick=0.15),
    ],
    # --- leaf (1)' side drift (_oriented_box rotX = transverse crown) ---
    drift=[dict(name="N", sgn=1.0), dict(name="S", sgn=-1.0)],
    #   placed only on the upper flat (x −3.40..−0.10, z=0) - straddling the slope would float it.
    #   the rotX sign applies −sgn in code **so the corridor-side (inner) edge rises**:
    #   top face z 0.012~0.108, bottom face at most −0.012 -> buried into the ground full width (no floating).
    drift_geo=dict(cx=-1.75, len_x=3.30, cy=1.95, len_y=1.10, center_z=0.0,
                   thick=0.12, rotx=5.0),
    # --- leaf (2) near-field scatter (flat ellipsoids) - count tunes the render cost ---
    leaf_scatter=dict(count=900, seed=2702,
                      scale=(0.038, 0.028, 0.006), jitter=(0.75, 1.30),  # r1: pancaked -> shrunk
                      x0=-4.20, x_pad=3.00, y_wide=3.60, y_band=1.70,
                      band_frac=0.70, lift=0.006,
                      # real USD scatter (look v1) - near band only. cover is the target coverage ratio.
                      cover=0.55, y_near=2.20, x_pad_near=1.50, max_count=900,
                      # ── [W2] G2 leaf globalisation (leaf_globalization_budget_v2 §6-a) ──
                      # The old near-band stopped at x −4.20, which leaves 69.0 %
                      # of the h0.3_d10 lower frame as bare dirt [measured]: the
                      # upstream rect must start BEHIND the farthest preset eye
                      # (x −10.0), hence −10.60. Non-overlapping 5-way split;
                      # inhomogeneity comes from splitting rects and varying
                      # `cover`, never from `edge_bias` (which silently
                      # under-covers — it drops interior samples after n is
                      # fixed and never compensates, §3-e-1).
                      # `max_count` is a truncation guard only, set at ~1.15n.
                      # Rect 1 widened to |y| 2.60 (was 2.20) so mound A (2.40)
                      # and drift (2.50) keep a 0.10 m margin — kills the
                      # texture fringe of §4.
                      g2=[
                          dict(tag="core",  x0=-4.20, x1=6.26, y0=-2.60, y1=2.60,
                               cover=0.55, max_count=1150),
                          dict(tag="up",    x0=-10.60, x1=-4.20, y0=-3.60, y1=3.60,
                               cover=0.32, max_count=470),
                          dict(tag="sideN", x0=-4.20, x1=6.26, y0=2.60, y1=3.60,
                               cover=0.32, max_count=110),
                          dict(tag="sideS", x0=-4.20, x1=6.26, y0=-3.60, y1=-2.60,
                               cover=0.32, max_count=110),
                          dict(tag="down",  x0=6.26, x1=7.76, y0=-3.60, y1=3.60,
                               cover=0.32, max_count=110),
                      ]),

    # --- cue ---
    rail=dict(y=1.45, x_start=-1.60, rail_h=0.90, post_r=0.022,
              rail_r=0.028, rail_mid_r=0.018, rail_mid_drop=0.42,
              spacing=1.20),
    nosing=dict(color=(0.80, 0.76, 0.62), width=0.05, proud=0.001),
    tactile=dict(ahead=0.35, depth=0.35, proud=0.004),

    # --- dressing / horizon closure ---
    trees=[dict(cx=-6.0, cy=5.5, where="upper"),
           dict(cx=-11.0, cy=-6.5, where="upper"),
           dict(cx=3.0, cy=7.5, where="lower"),
           dict(cx=8.0, cy=-6.0, where="lower"),
           dict(cx=14.0, cy=5.0, where="lower"),
           dict(cx=19.0, cy=-8.0, where="lower")],
    back_hedge=dict(cx=-15.0, sx=1.4, length=24.0, h=1.7),
    back_hedges=[dict(cy=-20.0), dict(cy=4.0), dict(cy=26.0)],
    far_hedge=dict(sx=1.4, length=26.0, h=1.8, x_pad=17.0),
    far_hedges=[dict(cy=-24.0), dict(cy=0.0), dict(cy=24.0)],
    # sy 76 (= y +-38) : inside the site y +-40 - keeps the ridge ends from running off the ground
    ridge=[dict(x_pad=24.0, h=5.0, sy=76.0, t=6.0),
           dict(x_pad=33.0, h=7.5, sy=76.0, t=8.0)],

    # ═══ [context dressing v2 · 07-27] prop layer that reads "this is a park" ═══
    #  Answers the audit v4 integration plan §emptiness. Stair·coping·leaf layers
    #  (mound/drift/scatter)·railing·lighting are wholly unchanged; new prims stand only
    #  on the flat grass beside the upper approach (x<0, z=0) and the lower entry (x>RUN, z=Z_BOT).
    #  where="upper" -> absolute x, "lower" -> RUN + cx (same convention as the existing trees).
    #
    #  [camera check - build_views() 8+4 shots, FOV assumed horizontal +-30 deg / vertical +-18 deg]
    #   grid eye(-2/-5/-10, 0, h) +X (stair bearing band +-7.4 deg @d10) ·
    #   approach_walk eye(-4,0,1.55) az 0 · buried_edge eye(-1.7,0.2,0.35) az -1.9 ·
    #   rail_cue eye(-2.4,2.2,1.6) az -14.4 (frame -44.4..15.6) ·
    #   beauty_side eye(-3.2,-7.5,3.3) az 51.1 (frame 21.1..81.1)
    #   rules (1) no new solid within 1.5 m of a camera eye (rail_cue especially)
    #        (2) every lower prop is x>RUN -> **farther** than the stair, cannot hide the buried run
    #        (3) no intrusion into the walk corridor |y|<1.62 (approach·entry paths)
    # ───────────────────────────────────────────────────────────────────────
    # 2 backed benches - the upper one is the rest pocket (grid d10 az 22.4 deg / beauty), the lower
    #   one sits in approach_walk mid-ground (az -14.1 deg, farther than the stair so no occlusion).
    benches=[dict(cx=-5.0, cy=3.4, yaw=0.0, where="upper"),
             dict(cx=4.0, cy=-3.2, yaw=0.0, where="lower")],
    bench=dict(length=1.8, width=0.50, height=0.45, back_h=0.42),
    # 2 litter bins (body + rim)
    bins=[dict(cx=-5.6, cy=2.3, where="upper"),
          dict(cx=4.9, cy=-2.5, where="lower")],
    bin_spec=dict(r=0.26, h=0.85),
    # park lamps (bollard-type low-level lights) - 2 pairs flanking the lower entry give it a promenade character.
    #   (RUN+2.8, +-2.1) / (RUN+6.8, +-2.1) sit on grass outside the corridor (1.62).
    parklamps=[dict(cx=-4.6, cy=2.1, where="upper"),
               dict(cx=-6.0, cy=-2.1, where="upper"),
               dict(cx=2.8, cy=2.1, where="lower"),
               dict(cx=2.8, cy=-2.1, where="lower"),
               dict(cx=6.8, cy=2.1, where="lower"),
               dict(cx=6.8, cy=-2.1, where="lower")],
    parklamp=dict(post_r=0.07, post_h=1.05, head_r=0.115, head_h=0.18,
                  cap_t=0.04),
    # hints a promenade branch - dirt/gravel patch (top face proud 0.006, 0.16 thick, buried).
    #   upper: the rest pocket carrying bench·bin·park lamp. lower: a spur branching toward +Y.
    patches=[dict(x0=-6.4, x1=-2.6, y0=1.50, y1=4.50, where="upper"),
             dict(x0=5.0, x1=6.5, y0=1.40, y1=9.50, where="lower")],
    patch=dict(proud=0.006, thick=0.16),
    # distant pergola (4 posts + roof slab + 3 rafters) - park-facility silhouette.
    pergola=dict(x0=9.0, x1=12.4, y0=6.0, y1=9.5, post_r=0.09, post_h=2.40,
                 roof_t=0.14, eave=0.30, rafter_t=0.08, rafters=3,
                 where="lower"),
    # a light leaf scatter on the props - its own fixed seed (separate from the main scatter seed 2702).
    prop_leaves=dict(seed=2711, per_bench=10, pergola=22, per_prop=6,
                     scale=(0.038, 0.028, 0.006), jitter=(0.75, 1.25),
                     lift=0.008),

    material=dict(
        # [W2 · leaf_globalization_budget_v2 §6-b] leaf_ground 0.9 -> 2.2.
        # The texture plate cannot be deleted — `LeafMound_A/B/C` + `LeafDrift_N/S`
        # ARE the burial geometry that hides the drop, so removing them removes
        # the hazard. It is demoted to an UNDERLAYER instead: at 0.9 m the
        # printed leaves rendered at 39 % of their real size against the 3D
        # leaves now lying on top, and that size discontinuity is what read as
        # "linoleum". 2.2 m matches the source texture's own physical scale, so
        # the plate reads as ground tone under the scatter rather than as a
        # competing second leaf layer.
        scale=dict(stone_worn=1.1, dirt_park=1.0, grass=1.4, leaf_ground=2.2),
        stone_tint=(0.88, 0.92, 0.84),        # stone moss tone (light)
        grass_tint=(0.55, 0.62, 0.38),        # standard grass tint + autumn dryness
        leaf_tex_tint=(0.95, 0.72, 0.48),     # leaf_ground texture autumn correction
        # 4 leaf scatter colours (spec-fixed values - mid-tone constants, so the sRGB dark-colour rule does not apply)
        leaf_tints=((0.20, 0.09, 0.03), (0.26, 0.13, 0.04),   # r1: desaturated
                    (0.16, 0.07, 0.025), (0.30, 0.19, 0.06)),
        leaf_rough=0.90,
        # [W3 F3] leaf-bank **section** (vertical faces only). Darker and less saturated
        #   than any scatter tint - the inside of a litter bank is shaded, damp and packed,
        #   and it sits below the darkest scatter colour (0.16, 0.07, 0.025) on purpose so
        #   the section reads as depth rather than as another leaf. Matt (0.94): a cut
        #   section of packed litter has no specular lobe at all.
        leaf_section_color=(0.085, 0.052, 0.028), leaf_section_rough=0.94,
        rail_color=(0.14, 0.14, 0.15), rail_metallic=0.8, rail_rough=0.45,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        # autumn canopy: keeps the sRGB dark band of the standard canopy (0.025,0.045,0.015)
        # and rotates hue only to autumn (russet/tan). Total brightness matches the standard.
        canopy_a=(0.055, 0.030, 0.010), canopy_b=(0.075, 0.048, 0.014),
        canopy_rough=1.0,
        ridge_color=(0.28, 0.26, 0.24),       # distant ridge (mid neutral · slight brown cast)
        lamp_color=(0.86, 0.86, 0.80), lamp_rough=0.40,   # park lamp head (daytime)
    ),

    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        # [ctx2] 49.79 -> 42.0 (survey §1·§5): peak leaf fall (late Oct ~ mid Nov).
        #   Seoul (37.5°N) noon sun elevation sits in the 35~42 deg band. 49.79 deg is the
        #   late-Sep / March noon value, contradicting the "late-autumn leaf fall" season premise.
        #   -> shadow length cot(49.79°)=0.845·h -> cot(42.0°)=1.111·h (+31%).
        noon_sun_enable=True, noon_sun_elev=42.0,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    # ─── SUN_AZ_OFFSET rationale: keeps the default 171.5 family (brief §A-7).
    #     world sun az ~ 33.5+171.5 = 205 -> shadow az 25 (~ the +X travel direction).
    #     (1) the main viewpoint is **upper (−X)**, so the scene07/09-type "risers as a
    #        black silhouette when viewed head-on" trap does not apply (an upper viewpoint
    #        sees treads, not risers).  (2) the sun enters from behind the camera (right)
    #        and hits the leaf mound slope (normal tilted 25 deg toward −X) nearly head-on ->
    #        the shading gradient on the mound top vanishes, **maximising the loss of the buried edge** (identity strengthened).
    #        (3) the exposed lower steps stay readable via cast shadows of the railing·scattered leaves.
    #     Sweep in the GUI with the [ ] keys (15 deg step), then have the director re-judge. ───
    #  ─── [ctx2] **azimuth check** after lowering sun elevation to 42.0 deg (SUN_AZ_OFFSET unchanged) ───
    #    shadow unit vector = (cos25°, sin25°) = (+0.906, +0.423), length 1.111·h.
    #    (1) **0 new shadows** over the buried run (mound B, x −0.25..1.02 · |y| <= 1.33):
    #       the only solids upstream (−X) are the upper trees (−6.0, +5.5)·(−11.0, −6.5),
    #       and both cast toward +Y, ending outside the corridor (|y| < 1.62)
    #       (the −11 tree: tip y = −6.5 + 1.55 = −4.95, 3.3 m of margin to the corridor).
    #    (2) only the park lamp (−6.0, −2.1, overall height 1.27) has its tip at
    #       (−4.72, −1.50), 0.12 m inside the corridor - 4.7 m upstream of the stair head
    #       (x=0) and outside mound A (x>=−3.20), so identity·judgment are unaffected (at the old elevation it fell just outside at y=−1.65).
    #    (3) stair readability improves: the 0.16 riser's shadow covers 36% -> 47% of the
    #       0.34 tread, so **step separation on the exposed lower steps gets sharper**.
    #    (4) tonal contrast: mound top (slope 24.9 deg) / flat luminance ratio 0.585 -> 0.484.
    #       The mound goes 17% darker in relative terms, but the burial identity rests on
    #       **geometric continuity** (nosing line 0.4706 vs mound 0.4643), not on equal
    #       luminance, so the judgment still holds. The autumn raking-light feel is strengthened.
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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneC2")

ASSET_ROLES = ["stone_worn", "leaf_ground", "dirt_park", "grass",
               "hdri", "mdl"]


def ground_plans():
    """[W2 ground_kit] Ground plan — the scene assembly and the CPU check use the same function.

    Minimal-intervention profile: keep only the joints, turn infrastructure·surface·scatter all off (§5.2·§8.3).
    """
    g = PARAMS["gkit"]
    up = PARAMS["upper"]
    gp = gk.plan_ground(
        "sidewalk_block",
        region=(float(g["joint_x0"]), -float(up["y_half"]),
                float(g["joint_x1"]), float(up["y_half"])),
        z=float(up["z_top"]), gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=[("stair_top", float(PARAMS["stairs"]["x0"]))],
        dists=(2, 5, 10), scene="sceneC2",
        tactile=(),                     # §12.4 - p=0.24 below threshold (park) -> not installed
        overrides=dict(
            pave=dict(module=(0.300, 0.300), joint="interlock",
                      step_x=float(g["joint_step"]),
                      groove_w=float(g["joint_w"]),
                      recess=float(g["joint_recess"])),
            # * `infra=dict()` does not turn it off - `plan_ground` overrides
            #   **merge** dicts, so an empty dict leaves the original intact.
            #   0 must be written out for the urban infrastructure to actually disappear.
            infra=dict(manhole=0, gully=0, gutter_L=0, gutter_U=0,
                       trench=0, marking=()),
            surface=(), extras=(), scatter=None),
        seed=27)
    return [("approach", gp)]


# ===========================================================================
# [D] camera presets: grid_views(gy=0.0) + 4 mise-en-scene shots
# ===========================================================================
def build_views(run, z_bot):
    views = sc.grid_views(0.0)                 # h{0.3,0.9,1.8}×d{2,5,10}, +X
    # approach_walk: walking viewpoint on the upper approach - the stair start edge is lost beyond the leaf crest
    views["approach_walk"] = dict(eye=[-4.0, 0.0, 1.55],
                                  tgt=[3.2, 0.0, -0.90])
    # buried_edge: low grazing viewpoint - does the buried run read as a gentle leaf slope?
    views["buried_edge"] = dict(eye=[-1.70, 0.20, 0.35],
                                tgt=[4.20, 0.0, -1.10])
    # rail_cue: oblique from the railing side - can the drop be estimated from the descending diagonal (the only cue) alone?
    views["rail_cue"] = dict(eye=[-2.40, 2.20, 1.60],
                             tgt=[4.60, 0.40, -1.60])
    # beauty_side: oblique high angle - contrasts the 3 runs, buried (steps 1~3) / transition (4~6) / exposed (7~)
    views["beauty_side"] = dict(eye=[-3.20, -7.50, 3.30],
                                tgt=[run * 0.7, 0.60, z_bot + 0.60])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. approach_walk      — 낙엽 마루 너머로 계단 시작 에지가 소실되는가(특색)
 2. h0.3·d2~5          — 그레이징에서 매몰부가 '완만한 낙엽 경사'로 읽히는가
 3. rail_cue           — 난간 1선 하강 사선이 유일 단서로 잔존하는가
 4. beauty_side        — 1~3단 완전매몰 / 4~6단 중앙피복 / 7단~ 노출 3구간 성립
 5. leaf_cover ON/OFF  — OFF 시 계단·난간 트랜스폼 완전 불변(대응쌍)
 6. 재질·접지          — 낙엽판 부유/틈, 경계석-사면 이음, Z파이팅 없는가"""


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"
    smoke_mode = os.environ.get("NEGOBS_SMOKE", "0") == "1"
    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])

    simulation_app = sc.boot(capture_mode or smoke_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from pxr import Usd, UsdGeom
    from omni.kit.viewport.utility import (get_active_viewport,
                                           capture_viewport_to_file)
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.Xform.Define(stage, "/World/Scene27")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene27"

    st = PARAMS["stairs"]
    RISER, TREAD, NSTEP = st["riser"], st["tread"], st["nsteps"]
    RUN = TREAD * NSTEP                        # 4.76
    DROP = RISER * NSTEP                       # 2.24
    Z_BOT = st["z_top"] - DROP                 # −2.24
    SLOPE = RISER / TREAD                      # 0.4706 (nosing line slope)

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # -------------------------------------------------------------------
    # materials
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]

        def tex(role, path, scale, **kw):
            return PBR(path, sc.tex_path(role, "diff"),
                       sc.tex_path(role, "nor"), sc.tex_path(role, "rough"),
                       scale, **kw)

        M = {}
        M["stone"] = tex("stone_worn", f"{ROOT}/Looks/Stone",
                         sca["stone_worn"], tint=mp["stone_tint"])
        # [v5.1 §4] per-instance +-5% tint jitter on the 2 coping strips - if the two
        #   sides shared one material a 'copy-paste' impression would remain. Texture is shared (same stone grain).
        for _tag in ("N", "S"):
            M[f"coping_{_tag}"] = tex(
                "stone_worn", f"{ROOT}/Looks/Coping{_tag}",
                sca["stone_worn"],
                tint=bc.jit_tint(mp["stone_tint"], 0.0,
                                 1.0 if _tag == "N" else -1.0,
                                 "copingC2", amp=0.05))
        M["dirt"] = tex("dirt_park", f"{ROOT}/Looks/Dirt", sca["dirt_park"])
        M["grass"] = tex("grass", f"{ROOT}/Looks/Grass", sca["grass"],
                         tint=mp["grass_tint"])
        M["leafbed"] = tex("leaf_ground", f"{ROOT}/Looks/LeafBed",
                           sca["leaf_ground"], tint=mp["leaf_tex_tint"])
        # [W3 F3 · DEC-2 §10.5 "sceneC2 additionally"] The **vertical-face binding bug**.
        #   `leaf_ground` is a plan-view photograph of a leaf carpet. Bound to a box it also
        #   lands on that box's vertical faces, where the same image reads as pressed-leaf
        #   laminate - a sheet material, not a bank of litter. The largest instance is mound
        #   A's upstream end face: 4.80 x 0.15 m, vertical, aimed straight at every preset
        #   eye. A leaf bank cut through is not a photograph of leaves seen from above; it is
        #   a dark, matt, compressed humus section with no legible leaf shapes at all, so the
        #   section material is a **constant** - no plan-view texture on a vertical face.
        M["leafsec"] = PBR(f"{ROOT}/Looks/LeafSection",
                           diffuse_color=mp["leaf_section_color"],
                           roughness_const=mp["leaf_section_rough"],
                           metallic=0.0)
        for i, c in enumerate(mp["leaf_tints"]):
            M[f"leaf_{i}"] = PBR(f"{ROOT}/Looks/Leaf_{i}", diffuse_color=c,
                                 roughness_const=mp["leaf_rough"],
                                 metallic=0.0)
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
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
        M["ridge"] = PBR(f"{ROOT}/Looks/Ridge", diffuse_color=mp["ridge_color"],
                         roughness_const=0.95, specular_level=0.0)
        # ─ context dressing v2: park lamp head (daytime non-emissive diffuser) ─
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        return M

    # -------------------------------------------------------------------
    # ground - upper/lower/side slopes are **placed as separate pieces** (never covering the stair corridor)
    # -------------------------------------------------------------------
    def build_terrain(M):
        up = PARAMS["upper"]
        lo = PARAMS["lower"]
        sl = PARAMS["slopes"]
        gr = PARAMS["ground"]
        path_mtl = M["dirt"] if cfg["cue_material_break"] else M["stone"]

        # (1) upper approach path (dirt) - x1=+0.02 overlaps the stair and carries the step-1 riser face
        # [W2-0 · P-A] the approach top face is a ground_kit decoration target -> displacement skin
        #   OFF (registered **before the BOX call**). A flush 0.05-wide strip would vanish
        #   entirely under the skin (+6.5~16.5 mm) `[spec §1.1]`.
        sc.skin_exclude(f"{ROOT}/UpperPath")
        BOX(f"{ROOT}/UpperPath",
            ((up["x0"] + up["x1"]) / 2.0, 0.0, up["z_top"] - up["thick"] / 2.0),
            (up["x1"] - up["x0"], 2.0 * up["y_half"], up["thick"]),
            path_mtl, col=True)
        # (2) upper grass (outside the corridor, south·north)
        for tag, ya, yb in (("N", up["y_half"], gr["y_edge"]),
                            ("S", -gr["y_edge"], -up["y_half"])):
            BOX(f"{ROOT}/UpperGrass_{tag}",
                ((up["x0"] + up["x1"]) / 2.0, (ya + yb) / 2.0,
                 up["z_top"] - gr["thick"] / 2.0),
                (up["x1"] - up["x0"], yb - ya, gr["thick"]), M["grass"],
                col=True)
        # (3) side grass slope (x 0..RUN, top face sunk 0.005 -> the upper·lower slabs cover it)
        for tag, ya, yb in (("N", sl["y_in"], sl["y_edge"]),
                            ("S", -sl["y_edge"], -sl["y_in"])):
            sc.build_slope(stage, f"{ROOT}/SideSlope_{tag}", 0.0,
                           -sl["sink"], RUN, DROP, ya, yb, sl["thick"],
                           M["grass"], margin=0.0, collider=True)
        # (4) lower entry path - under_lap underlap beneath the stair (anti-float) + 0.002 sink
        lx0 = RUN - lo["under_lap"]
        lx1 = RUN + lo["x_pad"]
        BOX(f"{ROOT}/LowerPath",
            ((lx0 + lx1) / 2.0, 0.0,
             Z_BOT - lo["sink"] - lo["thick"] / 2.0),
            (lx1 - lx0, 2.0 * lo["y_half"], lo["thick"]), path_mtl, col=True)
        # (5) lower grass (outside the corridor) - covers the slope end by 0.02 to seal the joint
        for tag, ya, yb in (("N", lo["y_half"], gr["y_edge"]),
                            ("S", -gr["y_edge"], -lo["y_half"])):
            BOX(f"{ROOT}/LowerGrass_{tag}",
                ((RUN - 0.02 + lx1) / 2.0, (ya + yb) / 2.0,
                 Z_BOT - gr["thick"] / 2.0),
                (lx1 - RUN + 0.02, yb - ya, gr["thick"]), M["grass"], col=True)

    # -------------------------------------------------------------------
    # stone stair + coping on both flanks
    # -------------------------------------------------------------------
    def build_stairs(M):
        sc.build_straight_stairs(
            stage, f"{ROOT}/Stairs", st["x0"], st["y0"], st["y1"],
            RISER, TREAD, NSTEP, st["base_z"], M["stone"],
            z_top=st["z_top"], collider=True)
        # coping: a sloped strip whose top face is the nosing line + rise (both flanks)
        cp = PARAMS["coping"]
        cx0 = -cp["ext"]
        crun = RUN + 2.0 * cp["ext"]
        cz0 = -SLOPE * cx0 + cp["rise"]        # top face z at x=cx0
        cdrop = SLOPE * crun
        for tag, ya, yb in (("N", cp["y_in"], cp["y_out"]),
                            ("S", -cp["y_out"], -cp["y_in"])):
            sc.build_slope(stage, f"{ROOT}/Coping_{tag}", cx0, cz0, crun,
                           cdrop, ya, yb, cp["thick"], M[f"coping_{tag}"],
                           margin=0.0, collider=True)
        print(f"[기하] 계단 {NSTEP}단 run={RUN:.3f} drop={DROP:.3f} "
              f"z_bot={Z_BOT:.3f} 단코선기울기={SLOPE:.4f}")

    # -------------------------------------------------------------------
    # leaf (1) burial mound (3 sloped plates) + side drift (_oriented_box rotX)
    # -------------------------------------------------------------------
    def build_leaf_mound(M):
        for md in PARAMS["mound"]:
            sc.build_slope(stage, f"{ROOT}/LeafMound_{md['name']}",
                           md["x0"], md["z0"], md["run"], md["drop"],
                           -md["y_half"], md["y_half"], md["thick"],
                           M["leafbed"], margin=0.0, collider=False)
        dg = PARAMS["drift_geo"]
        for df in PARAMS["drift"]:
            sgn = df["sgn"]
            # rotX(-+5 deg): transverse crown - a leaf bank outside the corridor (higher inside, thinner outside).
            # rotX(θ): local +Y -> world (cosθ, sinθ). The outside (+y·−y respectively) must go down,
            # hence the sign is −sgn.
            sc._oriented_box(
                stage, f"{ROOT}/LeafDrift_{df['name']}",
                (dg["cx"], sgn * dg["cy"], dg["center_z"]),
                (dg["len_x"], dg["len_y"], dg["thick"]), M["leafbed"],
                collider=False, rotx=-sgn * dg["rotx"])
        build_leaf_sections(M)

    def build_leaf_sections(M):
        """[W3 F3] Re-skin the **exposed vertical faces** of the leaf layer.

        The geometry of `LeafMound_A/B/C` and `LeafDrift_N/S` is **untouched** - it is what
        buries steps 1~3 and it *is* this scene's negative-obstacle identity (the docstring
        arithmetic at PARAMS['mound'] is load-bearing). What changes is only which material
        the vertical faces carry: a thin section skin, 2 mm proud of each exposed face, on
        the constant `leafsec` instead of the plan-view `leaf_ground` photograph.

        Every mound gets its upstream end face and both flanks, and each side drift gets
        its outboard flank. The two that matter most to the judged cuts are **mound B's
        crest end at x = −0.25, z +0.05…+0.20** - the scene docstring calls that crest line
        this scene's identity and it stands 1.75 m in front of the h0.3_d2 eye - and
        **mound C's flanks at y = ±0.90**, which run the length of the buried risers inside
        the corridor and are the "compressed-leaf laminate" the row names. Faces that turn
        out to be buried (mound C's upstream end sits inside the stair solid) keep their
        skin harmlessly: a 2 mm plate inside a solid renders nothing.

        GT: none. Every plate stands on an existing vertical face above grade, adds no
        walked surface, no drop edge and no collider.
        """
        t = 0.002                              # skin offset off the host face
        for md in PARAMS["mound"]:
            nm, yh, th = md["name"], md["y_half"], md["thick"]
            # (1) upstream end section — vertical, `thick` tall, facing −X.
            sc.add_box(stage, f"{ROOT}/LeafSec_{nm}_End",
                       (md["x0"] - t, 0.0, md["z0"] - th / 2.0),
                       (2.0 * t, 2.0 * yh, th), M["leafsec"], collider=False)
            # (2) the two flanks — sloped exactly like the host plate, so the skin cannot
            #     shear off it at the downstream end.
            for tag, sgn in (("N", 1.0), ("S", -1.0)):
                yy = sgn * (yh + t)
                sc.build_slope(stage, f"{ROOT}/LeafSec_{nm}_{tag}",
                               md["x0"], md["z0"], md["run"], md["drop"],
                               yy - t, yy + t, th,
                               M["leafsec"], margin=0.0, collider=False)
        # (3) the side drifts' outboard flanks.
        dg = PARAMS["drift_geo"]
        for df in PARAMS["drift"]:
            sgn = df["sgn"]
            sc._oriented_box(
                stage, f"{ROOT}/LeafSec_Drift_{df['name']}",
                (dg["cx"], sgn * (dg["cy"] + dg["len_y"] / 2.0 + t),
                 dg["center_z"]),
                (dg["len_x"], 2.0 * t, dg["thick"]), M["leafsec"],
                collider=False, rotx=-sgn * dg["rotx"])

    # -------------------------------------------------------------------
    # leaf (2) near-field scatter - count flat ellipsoids (fixed seed)
    #   surface z is the max of the terrain (approach/stair/slope/lower) and the mound top,
    #   so leaves settle without floating or sinking.
    # -------------------------------------------------------------------
    def build_leaf_scatter(M):
        ls = PARAMS["leaf_scatter"]
        rng = random.Random(int(ls["seed"]))
        UsdGeom.Xform.Define(stage, f"{ROOT}/Leaves")
        mats = [M[f"leaf_{i}"] for i in range(len(mp["leaf_tints"]))]
        cp = PARAMS["coping"]
        y_stair = st["y1"]
        plates = [(m["x0"], m["x0"] + m["run"], m["y_half"], m["z0"],
                   m["drop"] / m["run"]) for m in PARAMS["mound"]]

        def terrain_z(x, y):
            if x <= 0.0:
                return 0.0
            if x >= RUN:
                return Z_BOT
            ay = abs(y)
            if ay <= y_stair:                  # stair corridor -> step top face
                i = min(int(x / TREAD) + 1, NSTEP)
                return -RISER * i
            if ay <= cp["y_out"]:              # coping top face (nosing line + rise)
                return cp["rise"] - SLOPE * x
            # side slope (linear) - lower by build_slope's sink (anti-float)
            return -DROP * (x / RUN) - PARAMS["slopes"]["sink"]

        def surface_z(x, y):
            z = terrain_z(x, y)
            if cfg["leaf_cover"]:
                for px0, px1, pyh, pz0, pslope in plates:
                    if px0 <= x <= px1 and abs(y) <= pyh:
                        z = max(z, pz0 - pslope * (x - px0))
            return z

        sx, sy, sz = ls["scale"]
        jlo, jhi = ls["jitter"]
        x_lo = ls["x0"]
        x_hi = RUN + ls["x_pad"]
        n = int(ls["count"])
        x_hi_near = RUN + ls.get("x_pad_near", 1.5)

        # [realism v1] real leaf USD scatter.
        #   The old 900 flat ellipsoids gave **only 0.96 m² of total coverage** (measured),
        #   so the leaves visible on screen were effectively all leaf_ground texture pattern.
        #   = the "linoleum" the user pointed at. Specify by coverage ratio and lay real geometry.
        # The gate is `sc.LOOK_GEO` - the scatter creates new prims, so it is geometry. If the
        # leaves vanished in the material A/B arms it would be a different scene from the render the §7.1 threshold table came from (T1 §1.7.1 note).
        if sc.LOOK_GEO and sc.veg_available():
            # [W2 · G2] The 3D leaves go GLOBAL, not just to the near band.
            # Only the large clusters (fallcluster) are used: per-instance
            # coverage is 12~20x a single leaf, so the same prim budget covers
            # far more ground. Instancing keeps the unique vertex data flat —
            # the prototype is shared, only the instance table grows.
            # One scatter call per rect, seed = base + k, so re-runs are
            # deterministic and the rects stay independent.
            pool = [p for p in sc.VEG_DEBRIS if "fallcluster" in p[0]]
            gfn = lambda x, y: surface_z(x, y) + ls["lift"]
            got = 0
            for k, r in enumerate(ls["g2"]):
                got += sc.scatter_debris(
                    stage, f'{ROOT}/Leaves/{r["tag"]}',
                    r["x0"], r["y0"], r["x1"], r["y1"], 0.0,
                    cover=r["cover"], seed=int(ls["seed"]) + k, pool=pool,
                    ground_fn=gfn, edge_bias=0.0,
                    max_count=int(r["max_count"]), tilt_max=10.0)
            if got:
                # Budget doc predicted 1,689 with the pre-A3 coverage ledger
                # (mean_cov 0.0435). B-audit A3 lowered the two cluster rows,
                # so mean_cov is 0.04115 and the same target cover now needs
                # ~1,784 instances (~10.8 M logical tris, under the 12 M cap of
                # ground_kit §8.3). Count is printed, never assumed.
                print(f"[낙엽] 실물 USD 전역 산포(G2) {got}개 / "
                      f"{len(ls['g2'])} rect · seed={ls['seed']}+k")
                return
        for i in range(n):
            x = rng.uniform(x_lo, x_hi)
            if rng.random() < ls["band_frac"]:
                y = rng.uniform(-ls["y_band"], ls["y_band"])
            else:
                y = rng.uniform(-ls["y_wide"], ls["y_wide"])
            j = rng.uniform(jlo, jhi)
            a, b = sx * j, sy * j
            if rng.random() < 0.5:             # long-axis direction variation (stand-in for rotation)
                a, b = b, a
            z = surface_z(x, y) + ls["lift"]
            sc.add_sphere(stage, f"{ROOT}/Leaves/Leaf_{i}", (x, y, z),
                          (a, b, sz * j), mats[rng.randrange(len(mats))])
        print(f"[낙엽] 산포 {n}개 (seed={ls['seed']}) · 마운드 판 "
              f"{len(PARAMS['mound'])}매 + 드리프트 {len(PARAMS['drift'])}매")

    # -------------------------------------------------------------------
    # cues
    # -------------------------------------------------------------------
    def build_cues(M):
        cp = PARAMS["coping"]
        if cfg["cue_nosing"]:
            ns = PARAMS["nosing"]
            sc.build_nosing(
                stage, f"{ROOT}/Nosing", st["x0"], st["y0"], st["y1"],
                RISER, TREAD, NSTEP, color=ns["color"], width=ns["width"],
                proud=ns["proud"], z_top=st["z_top"])
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            sc.build_tactile(stage, f"{ROOT}/Tactile_Top",
                             st["x0"] - tc["ahead"], st["x0"],
                             st["y0"], st["y1"], M["stone"], z=0.0,
                             proud=tc["proud"])
        if cfg["cue_railing"]:
            rl = PARAMS["rail"]

            def rail_ground(x):
                """Post landing face = coping top face (over the stair) / approach path ground."""
                if x < -cp["ext"]:
                    return 0.0
                xx = min(max(x, 0.0), RUN)
                return cp["rise"] - SLOPE * xx

            sc.build_railing_line(
                stage, f"{ROOT}/Rail", rl["y"], rl["x_start"], st["x0"],
                RUN, DROP, rail_ground, M["rail"], rail_h=rl["rail_h"],
                post_r=rl["post_r"], spacing=rl["spacing"],
                rail_r=rl["rail_r"], rail_mid_r=rl["rail_mid_r"],
                rail_mid_drop=rl["rail_mid_drop"])

    # -------------------------------------------------------------------
    # dressing + horizon closure
    # -------------------------------------------------------------------
    def build_dressing(M):
        for i, t in enumerate(PARAMS["trees"]):
            if t["where"] == "upper":
                gx, gz = t["cx"], 0.0
            else:
                gx, gz = RUN + t["cx"], Z_BOT
            sc.build_tree(stage, f"{ROOT}/Tree_{i}", gx, t["cy"], gz,
                          M["wood"], M["canopy_a"], M["canopy_b"])
        build_park_context(M)

    # -------------------------------------------------------------------
    # context dressing v2 - bench · litter bin · park lamp · branch promenade patch · pergola
    #   + a light leaf scatter on the props (fixed seed). Stair·leaf layers·railing unchanged.
    #   coordinate convention: where="upper" -> absolute x (ground z=0),
    #              where="lower" -> RUN + cx (ground z=Z_BOT). All on flat faces.
    # -------------------------------------------------------------------
    def build_park_context(M):
        pl = PARAMS["prop_leaves"]
        rng = random.Random(int(pl["seed"]))
        lmats = [M[f"leaf_{i}"] for i in range(len(mp["leaf_tints"]))]
        sx0, sy0, sz0 = pl["scale"]
        jlo, jhi = pl["jitter"]
        counter = [0]

        # the hazard_stairs=False control is flat throughout (z=0) -> keeps lower props from floating
        low_z = Z_BOT if cfg["hazard_stairs"] else 0.0

        def place(where, cx):
            """(gx, gz) — ground coordinates per `where`."""
            return (cx, 0.0) if where == "upper" else (RUN + cx, low_z)

        def leaves(cx, cy, z, rx, ry, n):
            """Scatter n leaves on and around a prop's top face (fixed seed · flat ellipsoids)."""
            for _ in range(int(n)):
                j = rng.uniform(jlo, jhi)
                a, b = sx0 * j, sy0 * j
                if rng.random() < 0.5:
                    a, b = b, a
                sc.add_sphere(
                    stage, f"{ROOT}/Leaves/Prop_{counter[0]}",
                    (cx + rng.uniform(-rx, rx), cy + rng.uniform(-ry, ry),
                     z + pl["lift"]),
                    (a, b, sz0 * j), lmats[rng.randrange(len(lmats))])
                counter[0] += 1

        # (1) promenade branch patch (dirt/gravel) - laid under the props first so they sit grounded
        pa = PARAMS["patch"]
        for i, pd in enumerate(PARAMS["patches"]):
            gx0, gz = place(pd["where"], pd["x0"])
            gx1, _ = place(pd["where"], pd["x1"])
            z_hi = gz + pa["proud"]
            z_lo = z_hi - pa["thick"]
            BOX(f"{ROOT}/PathPatch_{i}",
                ((gx0 + gx1) / 2.0, (pd["y0"] + pd["y1"]) / 2.0,
                 (z_hi + z_lo) / 2.0),
                (gx1 - gx0, pd["y1"] - pd["y0"], z_hi - z_lo), M["dirt"])

        # (2) backed bench - a few leaves on the seat·backrest
        bs = PARAMS["bench"]
        for i, bd in enumerate(PARAMS["benches"]):
            gx, gz = place(bd["where"], bd["cx"])
            # [v5.1 §3] breaks axis-parallel·exact placement (deterministic jitter from a coordinate hash).
            #   The bench already sits by the dirt patch (rest pocket)·tree anchor, so only jitter is applied.
            _dx, _dy = bc.jit_pos(bd["cx"], bd["cy"], "benchC2", amp=0.20)
            _yaw = bc.jit_yaw(bd["cx"], bd["cy"], "benchC2", lo=3.0, hi=8.0,
                              base=bd["yaw"])
            gx, bcy = gx + _dx, bd["cy"] + _dy
            pfx = f"{ROOT}/Bench_{i}"
            sc.build_bench(stage, pfx, gx, bcy, gz, M["wood"],
                           length=bs["length"], width=bs["width"],
                           height=bs["height"], yaw=_yaw)
            back_y = -(bs["width"] / 2.0 - 0.04)      # local coordinates (inherits rotation)
            BOX(f"{pfx}/Back", (0.0, back_y, bs["height"] + bs["back_h"] / 2.0),
                (bs["length"], 0.06, bs["back_h"]), M["wood"])
            leaves(gx, bcy, gz + bs["height"],
                   bs["length"] / 2.0 - 0.10, bs["width"] / 2.0 - 0.08,
                   pl["per_bench"])
            leaves(gx, bcy + 0.55, gz, 1.10, 0.35, pl["per_prop"])

        # (3) litter bin
        bn = PARAMS["bin_spec"]
        for i, bd in enumerate(PARAMS["bins"]):
            gx, gz = place(bd["where"], bd["cx"])
            _dx, _dy = bc.jit_pos(bd["cx"], bd["cy"], "binC2", amp=0.18)
            gx, bcy = gx + _dx, bd["cy"] + _dy      # [v5.1 §3] position jitter
            sc.add_cylinder(stage, f"{ROOT}/Bin_{i}/Body",
                            (gx, bcy, gz + bn["h"] / 2.0),
                            bn["r"], bn["h"], M["rail"], collider=True)
            sc.add_cylinder(stage, f"{ROOT}/Bin_{i}/Rim",
                            (gx, bcy, gz + bn["h"] + 0.015),
                            bn["r"] * 1.12, 0.05, M["rail"])
            leaves(gx, bcy, gz, 0.55, 0.55, pl["per_prop"])

        # (4) park lamp (bollard-type) - post + diffuser head + cap
        pk = PARAMS["parklamp"]
        for i, ld in enumerate(PARAMS["parklamps"]):
            gx, gz = place(ld["where"], ld["cx"])
            # [v5.1 §3] +-0.18 m jitter. |y| must stay outside the corridor (1.62), so the
            #   coordinates guarantee |cy| >= 1.92 even after jitter (original 2.1 − 0.18).
            _dx, _dy = bc.jit_pos(ld["cx"], ld["cy"], "lampC2", amp=0.18)
            gx, lcy = gx + _dx, ld["cy"] + _dy
            pfx = f"{ROOT}/ParkLamp_{i}"
            sc.add_cylinder(stage, f"{pfx}/Post",
                            (gx, lcy, gz + pk["post_h"] / 2.0),
                            pk["post_r"], pk["post_h"], M["rail"],
                            collider=True)
            sc.add_cylinder(stage, f"{pfx}/Head",
                            (gx, lcy,
                             gz + pk["post_h"] + pk["head_h"] / 2.0 - 0.02),
                            pk["head_r"], pk["head_h"], M["lamp"])
            sc.add_cylinder(stage, f"{pfx}/Cap",
                            (gx, lcy,
                             gz + pk["post_h"] + pk["head_h"] + pk["cap_t"] / 2.0
                             - 0.03),
                            pk["head_r"] * 1.08, pk["cap_t"], M["rail"])

        # (5) pergola (4 posts + roof slab + rafters) - distant park facility
        pg = PARAMS["pergola"]
        gx0, gz = place(pg["where"], pg["x0"])
        gx1, _ = place(pg["where"], pg["x1"])
        cy = (pg["y0"] + pg["y1"]) / 2.0
        cx = (gx0 + gx1) / 2.0
        for tag, px, py in (("A", gx0, pg["y0"]), ("B", gx1, pg["y0"]),
                            ("C", gx0, pg["y1"]), ("D", gx1, pg["y1"])):
            sc.add_cylinder(stage, f"{ROOT}/Pergola/Post_{tag}",
                            (px, py, gz + pg["post_h"] / 2.0),
                            pg["post_r"], pg["post_h"], M["wood"],
                            collider=True)
        z_roof = gz + pg["post_h"]
        BOX(f"{ROOT}/Pergola/Roof",
            (cx, cy, z_roof + pg["roof_t"] / 2.0 - 0.02),
            (gx1 - gx0 + 2.0 * pg["eave"], pg["y1"] - pg["y0"]
             + 2.0 * pg["eave"], pg["roof_t"]), M["wood"])
        for r in range(int(pg["rafters"])):
            ry = pg["y0"] + (pg["y1"] - pg["y0"]) * (r + 1.0) \
                / (pg["rafters"] + 1.0)
            BOX(f"{ROOT}/Pergola/Rafter_{r}",
                (cx, ry, z_roof + pg["roof_t"] + pg["rafter_t"] / 2.0 - 0.03),
                (gx1 - gx0 + 2.0 * pg["eave"], pg["rafter_t"] * 1.6,
                 pg["rafter_t"]), M["wood"])
        leaves(cx, cy, z_roof + pg["roof_t"] - 0.02,
               (gx1 - gx0) / 2.0, (pg["y1"] - pg["y0"]) / 2.0, pl["pergola"])
        print(f"[드레싱] 공원 소품 {len(PARAMS['benches'])}벤치 · "
              f"{len(PARAMS['bins'])}휴지통 · {len(PARAMS['parklamps'])}공원등 · "
              f"파고라 1 · 패치 {len(PARAMS['patches'])} · "
              f"소품 낙엽 {counter[0]}장 (seed={pl['seed']})")

    # -------------------------------------------------------------------
    # [W2] ground_kit - P3 sidewalk_block, **minimal intervention** (spec §5.2 · §8.4).
    #   call-order convention (§8.4 (4)): it comes **after** the leaf scatter. The z
    #   stratigraphy is joint top +0.6 mm < leaf instances (scattered on the ground), at least 3.6 mm apart.
    #   The scatter callback is **not injected** - C2's ground_kit scatter allocation is 0.
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["gkit"]
        (_tag, gp), = ground_plans()
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["stone"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude)   # scatter not injected
        # §8.4 (3) 2 lateral boundary break-up bands - outside the plan's `region`
        #   (approach width +-1.62), so the builder is called directly. 2 prims, GT unchanged (+0.6 mm decal).
        n_eb = 0
        # In the `NEGOBS_GKIT=0` OFF arm the out-of-plan direct call is switched off too (§7.5 A3).
        for tag, sgn in (("N", 1.0), ("S", -1.0)) if gk.GKIT_ON else ():
            yy = sgn * float(g["edge_break_y"])
            r = gk.build_edge_break(
                kit, f"{ROOT}/GKit/EdgeBreak_{tag}",
                ((float(g["edge_break_x0"]), yy),
                 (float(g["edge_break_x1"]), yy)),
                float(PARAMS["upper"]["z_top"]), M["leafbed"],
                width=float(g["edge_break_w"]), scatter_only=False)
            n_eb += r["prim_count"]
        print(f"[ground_kit] sceneC2 P3 · 프림 {res['prims']} + 경계밴드 "
              f"{n_eb} · 산포 0(낙엽 G2 가 담당) · "
              f"δmax {res['gt_delta_max']:.4f} · unit_cell {res['unit_cell']}")
        return res

    def build_horizon(M):
        bh = PARAMS["back_hedge"]
        for i, h in enumerate(PARAMS["back_hedges"]):
            sc.build_hedge(stage, f"{ROOT}/BackHedge_{i}",
                           bh["cx"] - bh["sx"] / 2.0,
                           h["cy"] - bh["length"] / 2.0,
                           bh["cx"] + bh["sx"] / 2.0,
                           h["cy"] + bh["length"] / 2.0,
                           bh["h"], base_z=0.0)
        fh = PARAMS["far_hedge"]
        fx = RUN + fh["x_pad"]
        for i, h in enumerate(PARAMS["far_hedges"]):
            sc.build_hedge(stage, f"{ROOT}/FarHedge_{i}",
                           fx - fh["sx"] / 2.0, h["cy"] - fh["length"] / 2.0,
                           fx + fh["sx"] / 2.0, h["cy"] + fh["length"] / 2.0,
                           fh["h"], base_z=Z_BOT)
        for i, r in enumerate(PARAMS["ridge"]):
            BOX(f"{ROOT}/Ridge_{i}",
                (RUN + r["x_pad"], 0.0, Z_BOT + r["h"] / 2.0),
                (r["t"], r["sy"], r["h"]), M["ridge"], col=True)

    def build_flat_fill(M):
        """hazard_stairs=False control : stair·slope unified to z=0 flat ground."""
        up = PARAMS["upper"]
        lo = PARAMS["lower"]
        gr = PARAMS["ground"]
        x0, x1 = up["x0"], RUN + lo["x_pad"]
        # [W2-0 · P-A] the approach joints are laid in the control arm too -> skin OFF.
        sc.skin_exclude(f"{ROOT}/FlatPath")
        BOX(f"{ROOT}/FlatFill", ((x0 + x1) / 2.0, 0.0, -gr["thick"] / 2.0),
            (x1 - x0, 2.0 * gr["y_edge"], gr["thick"]), M["grass"], col=True)
        BOX(f"{ROOT}/FlatPath", ((x0 + x1) / 2.0, 0.0, 0.002 - 0.30),
            (x1 - x0, 2.0 * up["y_half"], 0.60),
            M["dirt"] if cfg["cue_material_break"] else M["grass"], col=True)

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()

    if cfg["hazard_stairs"]:
        build_terrain(M)
        build_stairs(M)
        if cfg["leaf_cover"]:
            build_leaf_mound(M)
        build_leaf_scatter(M)
        build_cues(M)
    else:
        build_flat_fill(M)
        if cfg["leaf_cover"]:
            build_leaf_scatter(M)

    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    build_ground_kit(M)                  # [W2] ground elements - after the leaves (stratigraphy convention §8.4 (4))
    build_horizon(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneC2 조립 완료 · 프림 {n}개 · 조기 종료")
        # ── [W2-C · B12] G2 instancing runtime verification ────────────────────────
        #   `leaf_globalization_budget_v2` gate 0. `SetInstanceable(True)` can fail
        #   silently (a prim with no reference, etc.) and a static CPU check has no way
        #   to see whether the prototype is shared - the pxr runtime is required.
        #   If the 1,784 do **not share** a prototype, unique vertices multiply by
        #   1,784x and the §8.3 triangle budget becomes meaningless.
        protos = stage.GetPrototypes()
        leaves, inst = [], 0
        for p in stage.Traverse():
            sp = str(p.GetPath())
            if "/Leaves/" in sp and sp.endswith("/Asset"):
                leaves.append(p)
                if p.IsInstance():
                    inst += 1
        print(f"[B12] 프로토타입 {len(protos)}개 "
              f"(≥1 필요) · 낙엽 Asset 프림 {len(leaves)}개 · "
              f"IsInstance True {inst}개 "
              f"({100.0 * inst / max(1, len(leaves)):.1f} %)")
        for pr in protos:
            print(f"       · 프로토타입 {pr.GetPath()} "
                  f"자손 {sum(1 for _ in Usd.PrimRange(pr))}")
        ok = (len(protos) >= 1 and leaves and inst == len(leaves))
        print(f"[B12] {'PASS' if ok else 'FAIL'} — "
              f"프로토타입 ≥1 ∧ 전 낙엽 인스턴스화")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    views = build_views(RUN, Z_BOT)
    _v0 = views["approach_walk"]
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
        sc.capture_pipeline(simulation_app, views, out_dir,
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneC2_{ts}.png")
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
