# -*- coding: utf-8 -*-
"""
sceneN1_shadow_band.py - NegObs synthetic scene 22: building shadow band (Isaac Sim 4.5)

Type    : N1 Hard Negative - a dark band crossing a flat plaza (GT = no drop in any pixel)
Spec    : Docs/nanobanana_batch1_geometry_map.md §A sceneN1_shadow_band
Look ref: look_refs/n1_shadow.jpg
Shared  : scene_common.py (verified API helpers) · scene16_canopy_shadow.py (skeleton)

Hazard (counter-example): **there is no drop anywhere.** The shadow of an
           elevated slab (skybridge type) crosses a perfectly flat, large
           concrete-tile plaza as a 4m wide band, and both sides of it are
           bright. A dark band with two crisp edges is close to **pixel-level
           indistinguishable** from the positive cues of T3 (underside dark zone)
           and T20 (canopy dark zone) - the first counter-example that tests
           whether the model learned the shortcut "dark band = drop". Even inside
           the band the paving texture and joints must read continuously (pure
           black would make it useless as a counter-example).
Goal     : assemble a flat plaza (3m joint grid) + 1 elevated slab outside the
           frame + dressing, and judge by render (render only). GT drop map = 0
           in every pixel.

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python sceneN1_shadow_band.py

Auto capture (headless):   NEGOBS_CAPTURE=1 python sceneN1_shadow_band.py
Smoke early exit:          NEGOBS_SMOKE=1  python sceneN1_shadow_band.py
Slab frame-in check:       NEGOBS_GEOCHECK=1 python3 sceneN1_shadow_band.py  (no Isaac)

Coordinates: Z-up, m, travel axis +X. No drop - the feature (shadow band) is the x=0..4 stretch.
"""

import os
import sys
import math
import json
import datetime

import scene_common as sc
import batch1_common as bc
import ground_kit as gk


# ===========================================================================
# [A] SCENE_CONFIG - standard 7 keys. This is a hard negative scene, so hazard_* toggles not a drop but
#     the "scene feature element (occluder slab)". Cue keys that do not apply are False + a reason comment.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_shadow_band": True,   # False -> remove the elevated slab (uniform-light control with no band)
    "cue_railing":        False,  # no drop -> railing not customary. Key reserved only
    "cue_tactile":        False,  # no drop -> warning tactile paving not customary. Key reserved only
    "cue_material_break": True,   # paving joint grid (tile boundary strips). False -> no joints
    "cue_nosing":         False,  # no step -> a non-slip strip is meaningless. Key reserved only
    "cue_sign":           False,  # [optional] not implemented - config key reserved only
    "cue_scene_dressing": True,   # planters · benches · bollards · backdrop buildings (horizon closure) together
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # 1 flat plaza slab (no opening -> no 4-box split needed). Top face z=0.
    plaza=dict(size=140.0, z_top=0.0, thick=0.5),

    # target shadow band (ground X range). The slab position is back-computed from this - see _slab_x().
    band=dict(x0=0.0, x1=4.0),
    # occluder: elevated slab outside the frame (skybridge type). H=height (soffit), half_y=half length.
    slab=dict(H=12.0, thick=0.8, half_y=30.0),

    # ═══ joints - [W2 §5.1 N1] single 3 m grid -> **two tiers** ═══════════
    #  old: spacing 3.0, one grid. A real granite flagstone plaza has **expansion joints (width
    #    20~30 mm)** and **construction joints (width ~3 mm)** overlapping at different periods.
    #  new: two tiers - expansion `exp_spacing` 6.0 m + construction `con_spacing` 1.8 m.
    #    * 1.8 m is **3x the flagstone cell 0.600** - it satisfies spec §4.5 U2 (the joint period
    #      must be an integer multiple of the unit cell). The v1 note "1.5~2 m" is 2.5x, which
    #      makes a **double grid** with the T1 MDL unit jitter `[spec §4.5 U2·§5.1]`.
    #    * at ticks where the two periods coincide (18 m period) the construction joint is dropped -
    #      2 prims at the same position = Z-fighting.
    #  * in this scene ground_kit **makes no joints** (`pave.joint=None`
    #    override). If the kit joints (1.8/6.0) overlap the scene grid on the same face,
    #    pilot defect D6 (sceneN5 double joint grid) recurs `[W2-B §7 D-list]`.
    joints=dict(exp_spacing=6.0, exp_width=0.045, con_spacing=1.8,
                con_width=0.022, proud=0.001,
                x0=-21.0, x1=30.0, y0=-21.0, y1=21.0),

    # ═══ [W2 ground_kit] P1 plaza_granite - spec §5.1 N1 row ═══════════════
    #  scene-specific prescription: (1) two-tier joints (enforced by the scene in `joints` above)
    #                (2) 1 manhole - **must pass the band-preservation invariant** (§7.3)
    #  * band preservation (§7.3 B12, `ground_kit._inv_n1_band`): the occluder in this scene
    #    must be the elevated slab and **nothing else**. The sun shadow is pure +X with length
    #    0.84536·h, so any new element must satisfy
    #      (in front) `xb + 0.84536·h < band.x0`  or  (behind) `xa > band.x1`
    #    Cropping the region blank at `band.x0 − 0.60` makes the in-front condition hold
    #    automatically, weeds (h <= 0.12 after clamping) included
    #    `[computed - −0.60 + 0.84536x0.12 = −0.499 < 0]`.
    #  * tactile paving: §12.4 "keep the N1 bollard frontage + correct the form (§12.5 (2))" -
    #    the small plates 0.40x0.30 (0.12 ㎡ each) are 212 px per unit in the approach view, so
    #    they were illegible. Replace them with a **continuous 0.60 m strip** along the bollard row
    #    frontage (`relief="normal"`, so 1 prim). The bollard row is x 11…17 = **behind**
    #    (xa = 11 > 4.0), so it passes the band invariant.
    ground=dict(
        region_pad_x=0.60,                  # clearance in front of the band (computed above)
        region_x0=-12.0, region_y=4.0,
        #  manhole - spec §5.1 states (−1.0, +0.4), but it is relocated by applying the
        #  criterion set by the **pilot-approved M9-(b) 2nd correction** (scene15):
        #  "one areal element must not monopolise the near window (screen width <= 25 %)":
        #    x=−1.0 -> ground distance 1.0 m at d2 · screen width f·0.648/1.0 = **1,078 px
        #    = 56.1 %** `[computed]`. Inside W1 (0.564~2.00 m), even at the far end X=2.00 it is
        #    28.1 %, so <=25 % is **impossible in principle**.
        #    -> move to the 2nd-priority window W2 (2.00~3.00 m): x=−2.40 ⇒ d5 X=2.60 m ·
        #      414 px = **21.6 %**, d10 X=7.60 m · 7.4 % `[computed]`.
        #      at d2 it is behind the eye (X=−0.40) and invisible -> patch #1 covers the d2 window.
        #  2 units - spec §5.1 "1~2 manholes (1 must be in W1)". The patch takes W1 and
        #  the manhole goes in the W2 window (screen-width computation above). The 2nd goes in
        #  d10's W2 window (X=3.4 m · 317 px = 16.5 %) to fill the areal element of the far cut.
        manholes=[(-2.40, 0.40), (-6.60, -1.50)],
        #  patch #1 covers the d2 near window (W1 = x −1.436…0.0). It is a flat tone change, so
        #  unlike a disc (the manhole) it carries little visual burden of monopolising the near view `[pilot #2]`.
        #  2 patches cover the d2 and d10 near windows (W1). The d5 W1 is taken by a gully.
        #    d2  W1 = x −1.436…0.0   → (−1.20, +0.10)
        #    d10 W1 = x −9.436…−8.0  → (−8.80, −0.20)
        #  the frame half width is only 0.46 m at X=0.8 m, so **|y| <= 0.4** is required to be
        #  in frame `[computed - half width 0.5774·X]`.
        patches=[(-1.20, 0.10), (-8.80, -0.20)],
        #  gullies - one in the d5 W1 (x −4.436…−3.0), one at the plaza edge.
        gullies=[(-3.80, 0.40), (-9.00, 2.60)],
        tactile_depth=0.60,                 # national highway practice guide 7.5 - dot tactile 60 cm standard
        tactile_setback=0.30,               # statutory 0.3 m in front of the bollard
    ),

    # ═══ dressing (cue_scene_dressing) - "urban plaza" context ════════════
    #  * band-preservation invariant [this scene's feature = the elevated slab is the only occluder]
    #    sun world az = 180.0 · elev 49.79 -> the shadow is **pure +X** (0 y shift),
    #    length = 0.84536·h. So an element with world AABB x∈[xa,xb] and top height h must satisfy
    #       (in front)  xb + 0.84536·h < band.x0 (=0.0)      … shadow ends before the band
    #       (behind)    xa > band.x1 (=4.0)                   … shadow falls only behind the band
    #    one of the two, or a new shadow reaches the band.
    #    every element is checked automatically by dresscheck() (NEGOBS_GEOCHECK=1).
    #  * walk corridor preserved: grid_views camera eye = (−10/−5/−2, 0, h). New prims use
    #    only |y| >= 5.0 or x >= 6.0 -> camera burial and band occlusion ruled out at source.
    #
    # planters - the 4 plaza corners. tree=False is on the band's front (-X) side (to leave canopy shadow clearance).
    planters=[dict(name="A", cx=-6.0, cy=-9.0, base_z=0.0, tree=False),
              dict(name="B", cx=12.0, cy=10.0, base_z=0.0, tree=True),
              dict(name="C", cx=17.0, cy=-13.0, base_z=0.0, tree=True),
              dict(name="D", cx=9.0, cy=15.0, base_z=0.0, tree=True)],
    planter=dict(size=3.0, curb_h=0.45, curb_t=0.25, cap_over=0.05,
                 cap_h=0.05, grass_h=0.40),
    # benches - all next to an anchor (planter or hedge), and each carries that anchor's bearing.
    #   [W3 CB-3] the v5.1 §3 `bc.jit_yaw/jit_pos` coordinate-hash jitter is ABOLISHED (spec §1.2).
    benches=[dict(name="A", cx=-6.0, cy=-6.6, yaw=0.0),     # 0.9 m in front of planter A
             dict(name="B", cx=12.0, cy=7.6, yaw=0.0),      # 0.9 m in front of planter B
             dict(name="C", cx=8.0, cy=-7.4, yaw=0.0),      # 0.6 m beside streetlight B
             dict(name="D", cx=17.0, cy=-10.6, yaw=0.0),    # 0.9 m in front of planter C
             dict(name="E", cx=-9.0, cy=10.3, yaw=0.0)],    # 1.2 m in front of hedge A
    # (`bench_jitter` deleted with the J-3/J-4 abolition — it fed nothing else.)
    # ── bollards [v5.1 §2 · ctx2 relocation] ──────────────────────────────
    #   old: 12 decorative bollards in 2 rows at the plaza edge y=+-9 (spacing 4 m · h0.75 · no reflective
    #   band or dot tactile paving) -> **removed entirely**. Decorative bollard rows are banned (v5.1 §2).
    #   new: a single row only where vehicle entry is a risk = the **entry throat where the
    #   shopfront sidewalk meets the plaza** on the south side. h0.90 · φ0.12 · spacing 1.5 m ·
    #   white reflective band on top · 0.3 m dot tactile plate at the front (sidewalk side −Y).
    #   * band preservation: xa = 11.0−0.062 = 10.94 > band.x1(4.0) -> **behind**, so
    #     the shadow cannot reach the band (shadows run in pure +X).
    #   * frame-in: from approach (eye −8), x=11 is 19 m ahead with a horizontal half width of 11.0 m
    #     > |y|=7 -> the whole row is in frame. From band_grazing (eye −3, z0.35) too,
    #     14 m ahead · half width 8.1 m -> visible. It is **behind** the band (x 0..4), so no occlusion.
    bollard_entry=dict(y=-7.0, x0=11.0, x1=17.0, spacing=1.5,
                       front=(0.0, -1.0)),   # dot tactile paving = sidewalk (−Y) side
    bollard=dict(r=0.06, h=0.90),
    # streetlights - pole 5.2 m (shadow 4.40 m). Only A is in front of the band: head max x −6.6 -> −2.20 < 0.
    streetlights=[dict(name="A", cx=-7.5, cy=7.5), dict(name="B", cx=8.0, cy=-8.0),
                  dict(name="C", cx=15.0, cy=8.5), dict(name="D", cx=21.0, cy=-9.0)],
    streetlight=dict(pole_h=5.2, pole_r=0.075, arm_len=0.9, arm_r=0.04, head=0.26),
    # plaza water feature (reflecting pool) - build_planter reused (water material in place of the grass slab)
    pool=dict(cx=19.0, cy=6.0, size=4.4, curb_h=0.45, curb_t=0.28,
              cap_over=0.06, cap_h=0.06, water_h=0.30),
    # hedges - mark the outer boundary of the plaza
    hedges=[dict(name="A", x0=-14.0, y0=11.5, x1=-4.0, y1=12.3, h=0.85),
            dict(name="B", x0=14.0, y0=-16.3, x1=24.0, y1=-15.5, h=0.85)],
    buildings=dict(
        # blocks the far vista (+X horizon): facade on the -X plane
        C=dict(x0=34.0, x1=44.0, y0=-22.0, y1=22.0, h=16.0, floors=5,
               axis="x", facade_x=34.0, face_dir=-1.0),
        # ─ skyline (silhouette steps) : 1 tower behind C + 2 mid-rise left and right ─
        T=dict(x0=54.0, x1=66.0, y0=-14.0, y1=10.0, h=38.0, floors=10,
               axis="x", facade_x=54.0, face_dir=-1.0),
        E=dict(x0=40.0, x1=50.0, y0=24.0, y1=42.0, h=24.0, floors=7,
               axis="x", facade_x=40.0, face_dir=-1.0),
        W=dict(x0=38.0, x1=48.0, y0=-44.0, y1=-24.0, h=21.0, floors=6,
               axis="x", facade_x=38.0, face_dir=-1.0),
        # ─ low-rise shops flanking the plaza (street wall) : facade on the y plane. x0=6.0 > band.x1 ─
        L=dict(x0=6.0, x1=30.0, y0=18.0, y1=30.0, h=10.0, floors=3,
               axis="y", facade_y=18.0, face_dir=-1.0),
        R=dict(x0=6.0, x1=30.0, y0=-30.0, y1=-18.0, h=10.0, floors=3,
               axis="y", facade_y=-18.0, face_dir=1.0),
    ),
    window=dict(w=1.2, h=1.6, inset=0.15, col_step=2.8, margin=2.5),

    material=dict(
        scale=dict(plaza_light=1.1, grass=1.4, brick_red=2.0),
        # ─ sRGB perception convention: plaza_light source mean sRGB 0.714 (neutral off-white) ->
        #   about 0.65 with a warm tint. Matches the bright warm concrete plaza of the reference (n1). ─
        plaza_tint=(0.92, 0.88, 0.82),
        joint_color=(0.05, 0.05, 0.05), joint_rough=0.85,   # dark joints (0.02~0.06 band)
        slab_color=(0.55, 0.55, 0.56), slab_rough=0.75,     # slab (outside the frame · irrelevant)
        grass_tint=(0.55, 0.68, 0.42),
        curb_color=(0.75, 0.75, 0.72), curb_rough=0.6,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        parapet_color=(0.90, 0.90, 0.87), parapet_rough=0.6,
        # ─ new dressing ─ (the dark canopy colour sits in the sRGB 0.02~0.06 convention band)
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        post_color=(0.55, 0.55, 0.58), post_metallic=0.5, post_rough=0.5,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.40,
        water_color=(0.05, 0.10, 0.11), water_rough=0.05,
        hedge_tint=(0.35, 0.45, 0.28),
        # ─ bollard v5.1 ─ the reflective band is bright white but totals only 0.08 m²/unit (small area), so
        #   it does not breach "no pure white over large areas" (v5.1 §4).
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
    # ─── SUN_AZ_OFFSET = 146.5 [the key parameter that defines this scene's feature]
    #     sun mapping (convention fixed in scene16): world sun az ~ 33.5 + offset = 180.0
    #       -> shadow azimuth az_s = sun az − 180 = 0.0 = **exactly +X**.
    #     ⇒ the shadow displacement is a pure +X component, so the shadow band of a Y-long slab has
    #        2 straight edges at x=const = **orthogonal to the camera axis (+X)**. (requirement)
    #     ⇒ the sun is at −X (behind the camera), i.e. front light - as in reference n1 the plaza is
    #        bright and only the band is dark (not a back-lit silhouette).
    #     sweeping in the GUI with the [ ] keys (dome_rotation_step 15 deg) translates the band along X
    #     and tilts it obliquely at the same time - keep offset 0 (default) when judging.
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
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneN1")

ASSET_ROLES = ["plaza_light", "grass", "brick_red", "hdri", "mdl"]


# ===========================================================================
# [D] back-compute the occluder slab position (band spec -> slab X range)
# ===========================================================================
def _slab_x():
    """Back-compute the slab X range from the target band [x0,x1] · height H · thickness t.

    Derivation (sun elevation e=49.79°, shadow azimuth pure +X - see the
    SUN_AZ_OFFSET comment):
      a point p=(x,z) above the ground z=0 projects into shadow at x + z·cot(e).
      For a slab (solid box) x∈[sx0,sx1], z∈[H,H+t] the shadow (umbra) range is
        start = min(x + z·cot) = sx0 + H·cot      (soffit −X corner)
        end   = max(x + z·cot) = sx1 + (H+t)·cot  (top face +X corner)
      ⇒ band width = (sx1−sx0) + t·cot  ⇒ W_s = band width − t·cot
        *The W_s ≈ band width·sin(e) formula in map §A assumes a plate normal to
         the rays - for a horizontal slab the shadow is a pure translation, so the
         formula above is the exact one (requested by the director's check).*
      defaults (H=12, t=0.8, band 0..4): cot=0.84536 → W_s=3.3237,
        slab x=[-10.1444, -6.8207], band x=[0.0000, 4.0000] (check agrees).
      penumbra (sun angular diameter 0.53°): light path H/sin(e)=15.71m → width
        0.190m along ground X - a reference-grade crisp edge (not perfectly hard;
        judged in PT).
    return: (sx0, sx1, cot_e)
    """
    e = math.radians(float(PARAMS["light"]["noon_sun_elev"]))
    cot = 1.0 / math.tan(e)
    b, s = PARAMS["band"], PARAMS["slab"]
    sx0 = float(b["x0"]) - float(s["H"]) * cot
    sx1 = sx0 + (float(b["x1"]) - float(b["x0"])) - float(s["thick"]) * cot
    return sx0, sx1, cot


def build_views():
    """Camera presets: grid_views(gy=0.0) + 4 mise-en-scene cuts."""
    views = sc.grid_views(0.0)
    # approach: walking towards the band across the bright plaza (does the band read as a drop)
    views["approach"] = dict(eye=[-8.0, 0.0, 1.6], tgt=[4.0, 0.0, 0.2])
    # band_grazing: low-viewpoint grazing - the extreme where horizon compression makes the band look like a "step"
    views["band_grazing"] = dict(eye=[-3.0, 0.0, 0.35], tgt=[7.0, 0.0, 0.15])
    # band_edge_close: close up just before entering the band - edge sharpness, legibility of the texture inside
    views["band_edge_close"] = dict(eye=[-1.2, 0.0, 1.1], tgt=[3.0, 0.0, -0.4])
    # beauty_oblique: oblique high angle - the contrast cut that reveals the band is flat
    views["beauty_oblique"] = dict(eye=[-7.0, -6.0, 2.6], tgt=[3.0, 1.0, -0.2])
    return views


# ===========================================================================
# [D1b] irregular placement (v5.1 §3) - computes the deterministic jittered layout.
#       The builder and the numeric check call the **same function**, so the AABBs always match reality.
# ===========================================================================
def bench_placements():
    """[(name, x, y, yaw), ...] - the 5 benches on their anchors' bearings.

    [W3 CB-3 · J-3/J-4 abolished, spec §1.2 / §10.1] Each bench sits at its
    nominal PARAMS coordinate and takes the bearing of the planter or hedge it
    stands in front of (`b["yaw"]`), which for this plaza is the axis set.
    Deleting the +-0.22 m / +-3~8 deg coordinate-hash jitter can only widen the
    clearances the dressing check measures, never narrow them.
    """
    return [(b["name"], b["cx"], b["cy"], b["yaw"]) for b in PARAMS["benches"]]


def streetlight_placements():
    """[(name, x, y, yaw), ...] - the 4 streetlights, arms on the plaza axis.

    [W3 CB-3 · J-3/J-4 abolished] A lamp arm points where the carriageway or
    the walkway it lights runs; it is not a decorative angle. Bearing 0.0.
    """
    return [(s["name"], s["cx"], s["cy"], 0.0) for s in PARAMS["streetlights"]]


def bollard_entry_points():
    """[v5.1 §2] Centre coordinates of the single entry bollard row [(x, y), ...] (even 1.5 m spacing)."""
    e = PARAMS["bollard_entry"]
    return bc.bollard_line(e["x0"], e["y"], e["x1"], e["y"],
                           spacing=e["spacing"])


def tactile_band_rect():
    """[W2 §12.5 (2)] Rectangle of the **continuous dot tactile strip** in front of
    the bollard row (x0, y0, x1, y1).

    The statutory position is "0.3 m in front of the bollard" (Enforcement Rule of
    the Act on Promotion of Mobility Convenience for the Mobility Impaired,
    Table 1, item 2, sub-item (cha)); the depth is the 60 cm dot standard of
    national highway practice guide 7.5. `front_dir` is −Y, so the strip stands
    off the bollard body's front face by setback in −Y and extends by depth.
    The coordinates are **derived from PARAMS** (no hard-coded document
    coordinates - spec §7.4).
    """
    e, bo, g = PARAMS["bollard_entry"], PARAMS["bollard"], PARAMS["ground"]
    fx, fy = e["front"]
    sb, dp = float(g["tactile_setback"]), float(g["tactile_depth"])
    if abs(fy) > abs(fx):                       # front faces +-Y (this scene: −Y)
        y_face = e["y"] + fy * bo["r"]
        ya, yb = y_face + fy * sb, y_face + fy * (sb + dp)
        return (e["x0"] - 0.15, min(ya, yb), e["x1"] + 0.15, max(ya, yb))
    x_face = e["x0"] + fx * bo["r"]
    xa, xb = x_face + fx * sb, x_face + fx * (sb + dp)
    return (min(xa, xb), e["y"] - 0.15, max(xa, xb), e["y"] + 0.15)


def ground_plans():
    """[W2 ground_kit] Ground plan - the scene assembly and the CPU check use the
    **same function**.

    Returns `[(tag, GroundPlan), ...]`. `plan_ground` creates no USD, so the gates
    (B6~B12) can be run as they are without Isaac `[spec §3.3]`.
    """
    g = PARAMS["ground"]
    b = PARAMS["band"]
    x1 = float(b["x0"]) - float(g["region_pad_x"])
    gp = gk.plan_ground(
        "plaza_granite",
        region=(float(g["region_x0"]), -float(g["region_y"]),
                x1, float(g["region_y"])),
        z=float(PARAMS["plaza"]["z_top"]), gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=(),                       # hard negative - 0 drop edges
        dists=(2, 5, 10), scene="sceneN1",
        # * hung on `cue_scene_dressing`, not `cue_tactile` - in this scene
        #   `cue_tactile` is the key reserved for "stair warning tactile paving" (always
        #   False, since there is no drop), while the dot tactile paving in front of the
        #   bollards is **one body with the bollard** and must follow the dressing
        #   toggle `[spec §12.4 - keep the N1 bollard frontage]`.
        tactile=("bollard",) if SCENE_CONFIG["cue_scene_dressing"] else (),
        sites=dict(manhole=[tuple(p) for p in g["manholes"]],
                   gully=[tuple(p) for p in g["gullies"]],
                   patch=[tuple(p) for p in g["patches"]],
                   tactile=dict(bollard=tactile_band_rect())),
        # joints are enforced in two tiers by the scene's `build_joints()` (PARAMS comment above · D6)
        overrides=dict(pave=dict(joint=None)),
        seed=22)
    return [("plaza", gp)]


# ===========================================================================
# [D2] context dressing AABB list (conservative upper bound) - for the band shadow and camera burial checks only.
#      Recomputes from PARAMS the **bounding box** of the prims build_dressing() actually
#      creates (dimensions inside the builder are bounded from the scene_common comments).
# ===========================================================================
def dressing_aabbs():
    """Returns [(name, xa, xb, ya, yb, z_top), ...]. z_top = highest point used for the shadow projection."""
    out = []
    pl = PARAMS["planter"]
    half = pl["size"] / 2.0
    top_curb = pl["curb_h"] + pl["cap_h"]
    # build_tree bound: grass surface (grass_h) + trunk_h 2.2 + highest blob (dz .85 + r .30*0.8)
    top_tree = pl["grass_h"] + 2.2 + 0.85 + 0.24
    for p in PARAMS["planters"]:
        t = top_tree if p.get("tree") else top_curb
        out.append((f"Planter_{p['name']}", p["cx"] - half, p["cx"] + half,
                    p["cy"] - half, p["cy"] + half, t))
    # bench 1.8(x) x 0.4(y) x h0.45 - half widths widened by the yaw jitter (<=8 deg) bound
    #   after rotation half width <= (0.9·cos8 + 0.2·sin8, 0.9·sin8 + 0.2·cos8) = (0.92, 0.32)
    for name, bx, by, _yaw in bench_placements():
        out.append((f"Bench_{name}", bx - 0.92, bx + 0.92,
                    by - 0.32, by + 0.32, 0.45))
    # bollard v5.1 (body + reflective band / dot tactile plate) - the single entry row
    bo = PARAMS["bollard"]
    e = PARAMS["bollard_entry"]
    for i, (bx, by) in enumerate(bollard_entry_points()):
        out.extend(bc.bollard_v51_aabbs(f"Bollard_{i}", bx, by, 0.0,
                                        front_dir=e["front"],
                                        radius=bo["r"], height=bo["h"]))
    sl = PARAMS["streetlight"]
    # arms +-X + head half width. yaw jitter (<=8 deg) bound -> x half width ex, y half width ex·sin8+head/2
    for name, sx, sy, _yaw in streetlight_placements():
        ex = sl["arm_len"] + sl["head"] / 2.0
        ey = ex * math.sin(math.radians(8.0)) + sl["head"] / 2.0
        out.append((f"Streetlight_{name}", sx - ex, sx + ex,
                    sy - ey, sy + ey, sl["pole_h"]))
    po = PARAMS["pool"]
    ph = po["size"] / 2.0
    out.append(("Pool", po["cx"] - ph, po["cx"] + ph, po["cy"] - ph,
                po["cy"] + ph, po["curb_h"] + po["cap_h"]))
    for h in PARAMS["hedges"]:
        out.append((f"Hedge_{h['name']}", h["x0"], h["x1"], h["y0"], h["y1"],
                    h["h"]))
    for k, bd in PARAMS["buildings"].items():
        out.append((f"Building_{k}", bd["x0"], bd["x1"], bd["y0"], bd["y1"],
                    bd["h"] + 0.5))                  # + parapet
    return out


def dresscheck():
    """Two dressing checks.
      (1) band shadow intrusion: sun az=180 → shadows are pure +X, length 0.84536·z.
          The condition for an element not to cast into the band [x0,x1] is
            xb + cot·z_top < band.x0   (in front)   or   xa > band.x1 (behind)
      (2) camera burial: no view's eye may lie inside any AABB (dilated by 0.35 m).
    """
    cot = 1.0 / math.tan(math.radians(float(PARAMS["light"]["noon_sun_elev"])))
    b0, b1 = float(PARAMS["band"]["x0"]), float(PARAMS["band"]["x1"])
    boxes = dressing_aabbs()
    print("-" * 68)
    print("sceneN1 드레싱 검산 ① 밴드 그림자 침입 (밴드 x=[%.1f, %.1f], cot=%.5f)"
          % (b0, b1, cot))
    bad = 0
    for name, xa, xb, ya, yb, zt in boxes:
        sh_end = xb + cot * zt                       # far end of the shadow (+X)
        if xa > b1:
            verdict = "뒤배치 OK (xa %.2f > %.1f)" % (xa, b1)
        elif sh_end < b0:
            verdict = "앞배치 OK (그림자 끝 %.2f < %.1f, 여유 %.2f m)" % (
                sh_end, b0, b0 - sh_end)
        else:
            verdict = "★밴드 침입★ (그림자 %.2f..%.2f)" % (xa, sh_end)
            bad += 1
        print("  %-16s x[%7.2f,%7.2f] z_top %5.2f → %s"
              % (name, xa, xb, zt, verdict))
    print("  판정 ①: %s" % ("전 요소 밴드 무침입 (합격)" if bad == 0
                            else "%d개 침입 (불합격)" % bad))
    print("sceneN1 드레싱 검산 ② 카메라 매몰 (여유 0.35 m)")
    m = 0.35
    hit = 0
    worst = (None, 1e9)
    for vname, v in sorted(build_views().items()):
        ex, ey, ez = v["eye"]
        for name, xa, xb, ya, yb, zt in boxes:
            if (xa - m <= ex <= xb + m and ya - m <= ey <= yb + m
                    and -m <= ez <= zt + m):
                print("  %-20s ★매몰★ %s" % (vname, name))
                hit += 1
            d = max(xa - ex, ex - xb, ya - ey, ey - yb, 0.0)
            if d < worst[1]:
                worst = ("%s vs %s" % (vname, name), d)
    print("  최근접(수평 거리) %s = %.2f m" % worst)
    print("  판정 ②: %s" % ("전 뷰 클리어 (합격)" if hit == 0
                            else "%d건 매몰 (불합격)" % hit))
    print("-" * 68)


# ─── slab frame-in check (requirement: slab invisible in all cuts) ────────────
#  Isaac's default perspective camera = focal 18.147mm / horizontal aperture 20.955mm, 16:9
#    -> horizontal FOV 60.0 deg, vertical FOV 35.98 deg. The check runs at h70/v46 deg with safety margin.
#  results (default PARAMS, reproduce with NEGOBS_GEOCHECK=1):
#    · preset_h*_d2 / d5, approach, band_grazing, band_edge_close
#        -> the slab (x<=−6.82) is **entirely behind the camera** -> invisible by construction
#    · preset_h0.3/0.9/1.8_d10 (eye x=−10, directly under the slab)
#        -> min vertical angle of the part still ahead 84.8/84.0/82.7 deg ≫ frame top 23 deg
#    · beauty_oblique (eye −7,−6,2.6)
#        -> min horizontal angle 58.3 deg ≫ frame side 35 deg  (vertical min 37.3 deg also exceeds)
#    ⇒ every cut OUT. Only the band is visible and the occluder is off screen = N1 spec met.
#  ─ summary of the context dressing check (dresscheck) [ctx2 re-check, 07-27] ─
#    (1) 0 band shadow intrusions - the in-front elements are only Planter_A (clearance 4.08 m),
#       Bench_A (4.85), Bench_E (7.63), Hedge_A (3.28) and Streetlight_A (2.13) - 5 in all,
#       and all the rest (including the 5 entry bollards and the dot tactile paving) are behind, xa > 4.0.
#       * the bollard raise h0.75->0.90 is entirely in the behind group, so it does not affect the invariant.
#    (2) 0 camera burials - closest horizontal 0.23 m (beauty_oblique eye vs Bench_A).
#       eye z 2.60 · the bottom frame ray meets the ground 4.3 m ahead ⇒ the near part is off screen.
def geocheck():
    """Project the slab AABB into the view frustum and check whether it is in frame (no Isaac needed)."""
    sx0, sx1, cot = _slab_x()
    s = PARAMS["slab"]
    z0, z1, hy = float(s["H"]), float(s["H"]) + float(s["thick"]), float(s["half_y"])
    hfov, vfov = 70.0, 46.0                      # actual 60/36 + safety margin
    print("=" * 68)
    print("sceneN1 오클루더 슬래브 프레임인 검산")
    print("  cot(elev)=%.5f  슬래브 x=[%.4f, %.4f] (폭 %.4f) z=[%.2f, %.2f] "
          "y=±%.1f" % (cot, sx0, sx1, sx1 - sx0, z0, z1, hy))
    print("  → umbra 밴드 x=[%.4f, %.4f] (폭 %.4f)"
          % (sx0 + z0 * cot, sx1 + z1 * cot,
             (sx1 + z1 * cot) - (sx0 + z0 * cot)))
    print("  검사 FOV h%.0f°/v%.0f° (실제 h60/v36 + 마진)" % (hfov, vfov))
    pts = []
    for i in range(9):
        px = sx0 + (sx1 - sx0) * i / 8.0
        for j in range(201):
            py = -hy + 2.0 * hy * j / 200.0
            for pz in (z0, (z0 + z1) / 2.0, z1):
                pts.append((px, py, pz))
    bad = 0
    for name, v in sorted(build_views().items()):
        ex, ey, ez = v["eye"]
        fx, fy, fz = (v["tgt"][0] - ex, v["tgt"][1] - ey, v["tgt"][2] - ez)
        fn = math.sqrt(fx * fx + fy * fy + fz * fz)
        fx, fy, fz = fx / fn, fy / fn, fz / fn
        rx, ry, rz = fy * 1.0 - fz * 0.0, fz * 0.0 - fx * 1.0, 0.0   # f × Z
        rn = math.hypot(rx, ry)
        rx, ry = rx / rn, ry / rn
        ux = ry * fz - rz * fy
        uy = rz * fx - rx * fz
        uz = rx * fy - ry * fx
        n_front = 0
        min_h = 180.0
        min_v = 180.0
        inside = 0
        for px, py, pz in pts:
            dx, dy, dz = px - ex, py - ey, pz - ez
            fw = dx * fx + dy * fy + dz * fz
            if fw <= 1e-6:
                continue
            n_front += 1
            ah = math.degrees(math.atan2(abs(dx * rx + dy * ry), fw))
            av = math.degrees(math.atan2(abs(dx * ux + dy * uy + dz * uz), fw))
            min_h = min(min_h, ah)
            min_v = min(min_v, av)
            if ah < hfov / 2.0 and av < vfov / 2.0:
                inside += 1
        if n_front == 0:
            print("  %-20s OUT — 슬래브 전부 카메라 후방" % name)
        elif inside:
            bad += 1
            print("  %-20s ★FRAME-IN★ (샘플 %d개)" % (name, inside))
        else:
            print("  %-20s OUT — 최소 수평각 %.1f° / 수직각 %.1f°"
                  % (name, min_h, min_v))
    print("  판정: %s" % ("전 컷 OUT (합격)" if bad == 0 else "%d컷 프레임인 (불합격)" % bad))
    dresscheck()
    print("=" * 68)


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]  ※ 이 씬은 GT = 전 픽셀 "낙차 없음" (hard negative)
 1. approach / h0.9_d5   — 폭 4m 암 밴드가 광장을 횡단, 양쪽 모두 밝은가
 2. band_edge_close (PT) — 밴드 **내부에 포장 텍스처·줄눈이 연속 판독**되는가
                            (완전 흑이면 실패 — 반례로서 무의미)
 3. band_grazing         — 저시점에서 밴드 에지가 "단"처럼 읽히는 혼동 강도
 4. 전 컷               — 오클루더 슬래브가 화면에 **절대 보이지 않는가**
                            (NEGOBS_GEOCHECK=1 검산과 대조)
 5. 기하                 — 밴드 에지가 x=const 직선(시축 직교)·평면 Z파이팅 없음
 6. 맥락(드레싱)         — 가로등·벤치·볼라드열·상가 가로벽·원경 스카이라인으로
                            "도심 광장"이 읽히는가. **밴드(x 0~4) 위·주변에는
                            신규 그림자가 하나도 없어야** 한다(dresscheck ① 대조)"""


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
    UsdGeom.Xform.Define(stage, "/World/Scene22")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene22"

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
        M["plaza"] = PBR(
            f"{ROOT}/Looks/Plaza", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            sca["plaza_light"], tint=mp["plaza_tint"])
        M["grass"] = PBR(
            f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            sca["grass"], tint=mp["grass_tint"])
        M["brick"] = PBR(
            f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
            sc.tex_path("brick_red", "nor"), sc.tex_path("brick_red", "rough"),
            sca["brick_red"])
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
        M["slab"] = PBR(f"{ROOT}/Looks/Slab", diffuse_color=mp["slab_color"],
                        roughness_const=mp["slab_rough"], metallic=0.0)
        M["curb"] = PBR(f"{ROOT}/Looks/Curb", diffuse_color=mp["curb_color"],
                        roughness_const=mp["curb_rough"])
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"], metallic=0.0)
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           diffuse_color=mp["parapet_color"],
                           roughness_const=mp["parapet_rough"])
        # ─ new context dressing ─
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"],
                            specular_level=0.0)
        # [W2 fix batch F5] Dark cast-iron for the kit's manhole / gully covers.
        #   `ground_kit._ik_manhole` **declares** albedo 0.10 to gate B9, but B9 only
        #   sees the declaration - the scene binds whatever it likes, and these scenes
        #   bound the stainless handrail constant. A cover at 0.66~0.85 against dark
        #   paving is the single brightest prop in the library (defect D5).
        M["gk_iron"] = PBR(f"{ROOT}/Looks/GKitIron",
                            diffuse_color=(0.10, 0.10, 0.105),
                            metallic=0.55, roughness_const=0.55)
        M["post"] = PBR(f"{ROOT}/Looks/Post", diffuse_color=mp["post_color"],
                        metallic=mp["post_metallic"],
                        roughness_const=mp["post_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["water"] = PBR(f"{ROOT}/Looks/Water", diffuse_color=mp["water_color"],
                         roughness_const=mp["water_rough"], metallic=0.0)
        # ─ bollard v5.1 (stainless body / top reflective band / front dot tactile paving) ─
        M["bollard_body"] = PBR(f"{ROOT}/Looks/BollardBody",
                                diffuse_color=mp["bollard_color"],
                                metallic=mp["bollard_metallic"],
                                roughness_const=mp["bollard_rough"])
        M["bollard_band"] = PBR(f"{ROOT}/Looks/BollardBand",
                                diffuse_color=mp["bollard_band_color"],
                                roughness_const=0.30)
        # [W2 · ground_kit §12.5-3] texture-backed so the 36 dots shade.
        M["tactile"] = bc.tactile_mtl(stage, f"{ROOT}/Looks/Tactile")
        return M

    # -------------------------------------------------------------------
    # plaza - a single perfectly flat slab (no cavity or opening at all: GT drop 0)
    # -------------------------------------------------------------------
    def build_plaza(M):
        p = PARAMS["plaza"]
        # [W2-0 · P-A] the plaza top face is what ground_kit decorates -> displacement skin OFF.
        #   `add_box` calls `_skin_wanted` right there, so it must be registered **before the BOX**
        #   call. If it is left on, the manhole (+-10 mm) and decals (0.6 mm) are buried whole
        #   under the skin (+6.5~16.5 mm) `[measured - spec §1.1]`.
        sc.skin_exclude(f"{ROOT}/Plaza")
        BOX(f"{ROOT}/Plaza",
            (0.0, 0.0, p["z_top"] - p["thick"] / 2.0),
            (p["size"], p["size"], p["thick"]), M["plaza"], col=True)

    def build_joints(M):
        """[W2 §5.1 N1] **Two-tier joints** - expansion 6.0 m + construction 1.8 m.

        The dark thin plate at proud 0.001 (the reference cue for reading inside
        the band) is unchanged. What changed is not one period but **the layering
        of two periods** - that is how a real flagstone plaza looks, and 1.8 m is
        an integer multiple of the flagstone cell 0.600, so it stays in phase with
        the T1 unit jitter `[spec §4.5 U2]`. At the ticks where the two periods
        coincide the construction joint is dropped.
        """
        j = PARAMS["joints"]
        p = PARAMS["plaza"]
        pr = j["proud"]
        thk = pr + 0.006                        # partly embedded + proud protrusion
        cz = p["z_top"] + pr - thk / 2.0
        Lx = j["x1"] - j["x0"]
        Ly = j["y1"] - j["y0"]

        def ticks(a0, a1, step):
            n = int(math.floor((a1 - a0) / step + 1e-9)) + 1
            return [a0 + i * step for i in range(n)]

        exp_x = ticks(j["x0"], j["x1"], j["exp_spacing"])
        exp_y = ticks(j["y0"], j["y1"], j["exp_spacing"])
        exp_xs = set(round(v, 4) for v in exp_x)
        exp_ys = set(round(v, 4) for v in exp_y)
        n = 0
        # joints along the X axis (= y=const lines) : parallel to the camera axis
        for yy in exp_y:
            BOX(f"{ROOT}/JointX_{n}", ((j["x0"] + j["x1"]) / 2.0, yy, cz),
                (Lx, j["exp_width"], thk), M["joint"])
            n += 1
        for yy in ticks(j["y0"], j["y1"], j["con_spacing"]):
            if round(yy, 4) in exp_ys:          # 2 prims at the same position = Z-fighting
                continue
            BOX(f"{ROOT}/JointX_{n}", ((j["x0"] + j["x1"]) / 2.0, yy, cz),
                (Lx, j["con_width"], thk), M["joint"])
            n += 1
        # joints along the Y axis (= x=const lines) : parallel to the band edges - reinforces the confusion
        m = 0
        for xx in exp_x:
            BOX(f"{ROOT}/JointY_{m}", (xx, (j["y0"] + j["y1"]) / 2.0, cz),
                (j["exp_width"], Ly, thk), M["joint"])
            m += 1
        for xx in ticks(j["x0"], j["x1"], j["con_spacing"]):
            if round(xx, 4) in exp_xs:
                continue
            BOX(f"{ROOT}/JointY_{m}", (xx, (j["y0"] + j["y1"]) / 2.0, cz),
                (j["con_width"], Ly, thk), M["joint"])
            m += 1
        print(f"[줄눈] 2단화 — 신축 {j['exp_spacing']} m · 시공 "
              f"{j['con_spacing']} m · X {n}본 · Y {m}본")

    # -------------------------------------------------------------------
    # [W2] ground_kit - P1 plaza_granite. This is a hard negative with no drop edge, so
    #   GT-E1′/GT-E2 are vacuously true and the verdict rests on the **B12 band-preservation
    #   invariant** (§7.3), the prim budget and albedo. Joints are enforced by the scene itself (avoids D6).
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        (_tag, gp), = ground_plans()
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["joint"], crack=M["gk_crack"], patch=M["plaza"],
                  patch_cut=M["gk_crack"], manhole=M["gk_iron"],
                  gully=M["gk_iron"],
                  gutter=M["curb"], weed=M["grass"], tactile=M["tactile"],
                  stain_dirt=M["gk_stain"], stain_water=M["gk_stain"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] sceneN1 P1 · 프림 {res['prims']} · 산포 "
              f"{res['instances']} · δmax {res['gt_delta_max']:.4f} · "
              f"unit_cell {res['unit_cell']}")
        return res

    # -------------------------------------------------------------------
    # occluder - elevated slab outside the frame (skybridge type). Position back-computed by _slab_x().
    # -------------------------------------------------------------------
    def build_occluder(M):
        s = PARAMS["slab"]
        sx0, sx1, cot = _slab_x()
        hy = s["half_y"]
        BOX(f"{ROOT}/SkyBridgeSlab",
            ((sx0 + sx1) / 2.0, 0.0, s["H"] + s["thick"] / 2.0),
            (sx1 - sx0, 2.0 * hy, s["thick"]), M["slab"])
        print("[기하] 슬래브 x=[%.4f, %.4f] z=[%.2f, %.2f] → 밴드 x=[%.4f, %.4f]"
              % (sx0, sx1, s["H"], s["H"] + s["thick"],
                 sx0 + s["H"] * cot, sx1 + (s["H"] + s["thick"]) * cot))

    # -------------------------------------------------------------------
    # dressing - the urban plaza context that makes "where this is" readable from the render alone:
    #   4 planters (corner planting) + 5 benches + 1 entry bollard row (v5.1 spec) + 4 streetlights +
    #   1 water feature + 2 hedges + 6 buildings (far skyline + shop street walls flanking the plaza).
    #   Every element is checked by dresscheck() for (1) no band shadow intrusion (2) no camera burial.
    # -------------------------------------------------------------------
    def build_dressing(M):
        pl = PARAMS["planter"]
        tree_mtls = (M["wood"], M["canopy_a"], M["canopy_b"])
        for pdef in PARAMS["planters"]:
            # tree=False (band front, -X side): leaves ample clearance for the canopy shadow.
            sc.build_planter(
                stage, f"{ROOT}/Planter_{pdef['name']}", pdef["cx"], pdef["cy"],
                pdef["base_z"], M["curb"], M["grass"],
                tree_mtls=(tree_mtls if pdef.get("tree") else None),
                size=pl["size"], curb_h=pl["curb_h"], curb_t=pl["curb_t"],
                cap_over=pl["cap_over"], cap_h=pl["cap_h"],
                grass_h=pl["grass_h"])
        # benches - next to an anchor (planter or hedge) + deterministic yaw/position jitter (v5.1 §3)
        for name, bx, by, byaw in bench_placements():
            sc.build_bench(stage, f"{ROOT}/Bench_{name}", bx, by, 0.0,
                           M["wood"], yaw=byaw)
        # bollards [v5.1 §2] - a single entry row where the south sidewalk meets the plaza (spacing 1.5 m).
        #   The 2 decorative rows (y=+-9, 12 units) are removed. Dot tactile paving sits flush on the sidewalk side (−Y).
        bo = PARAMS["bollard"]
        e = PARAMS["bollard_entry"]
        for i, (bx, by) in enumerate(bollard_entry_points()):
            # [W2 §12.5 (2)] the per-unit small plate (0.40x0.30) is **replaced by
            #   ground_kit's continuous 0.60 m strip** - the small plate is 212 px per unit
            #   in the approach view, and even all 5 together are under 0.05 % of the frame,
            #   so it was illegible `[measured - spec §12.5 (2)]`. If it is not turned off
            #   here, strip and plate touch and the dot band grows to 0.9 m (over the statutory 0.60).
            bc.build_bollard_v51(stage, f"{ROOT}/Bollard_{i}", bx, by, 0.0,
                                 None, M["bollard_body"], M["bollard_band"],
                                 M["tactile"], front_dir=e["front"],
                                 radius=bo["r"], height=bo["h"],
                                 tactile=False)
        sl = PARAMS["streetlight"]
        for name, sx, sy, syaw in streetlight_placements():
            # rotate the arm bearing slightly off axis-parallel to remove the 'cloned placement' look (v5.1 §3)
            base = sc.build_rot_group(stage, f"{ROOT}/Streetlight_{name}",
                                      (sx, sy), syaw)
            CYL(f"{base}/Pole", (sx, sy, sl["pole_h"] / 2.0),
                sl["pole_r"], sl["pole_h"], M["post"], col=True)
            for sgn, tag in ((1.0, "P"), (-1.0, "N")):
                CYL(f"{base}/Arm_{tag}",
                    (sx + sgn * sl["arm_len"] / 2.0, sy,
                     sl["pole_h"] - 0.10), sl["arm_r"], sl["arm_len"],
                    M["post"], rotY=90.0)
                BOX(f"{base}/Head_{tag}",
                    (sx + sgn * sl["arm_len"], sy,
                     sl["pole_h"] - 0.15),
                    (sl["head"], sl["head"], 0.12), M["lamp"])
        # water feature (reflecting pool) - the "grass slab" of build_planter replaced by a water material.
        #   water top z = water_h(0.30) < kerb 0.45 -> all geometry z >= 0 (GT unchanged)
        po = PARAMS["pool"]
        sc.build_planter(stage, f"{ROOT}/Pool", po["cx"], po["cy"], 0.0,
                         M["curb"], M["water"], tree_mtls=None,
                         size=po["size"], curb_h=po["curb_h"],
                         curb_t=po["curb_t"], cap_over=po["cap_over"],
                         cap_h=po["cap_h"], grass_h=po["water_h"])
        # [GT-63] clipped hedge bands: box+crown blobs -> fused rows of real
        #   shrub USDs (place_hedge_row; rects/heights/prim roots unchanged;
        #   legacy build_hedge fallback inside).
        n_hedge = 0
        for hg in PARAMS["hedges"]:
            n_hedge += sc.place_hedge_row(
                stage, f"{ROOT}/Hedge_{hg['name']}", hg["x0"],
                hg["y0"], hg["x1"], hg["y1"], hg["h"],
                gk.det_seed("sceneN1.hedge", hg["name"]), base_z=0.0,
                fallback_tint=mp["hedge_tint"])
        print(f"[GT-63] 생울타리 실관목 {n_hedge}주 "
              f"(place_hedge_row · 폴백 {'무' if n_hedge else 'build_hedge'})")
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd,
                              M["brick"], M["glass"], M["parapet"],
                              window=PARAMS["window"])

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()

    build_plaza(M)
    if cfg["cue_material_break"]:
        build_joints(M)
    if cfg["hazard_shadow_band"]:
        build_occluder(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    build_ground_kit(M)                  # [W2] ground elements - after the dressing (scatter order convention)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneN1 조립 완료 · 프림 {n}개 · 조기 종료")
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneN1_{ts}.png")
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
        geocheck()                     # check only the slab frame-in, without booting Isaac
    else:
        main()
