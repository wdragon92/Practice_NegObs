# -*- coding: utf-8 -*-
"""
probe_common.py — shared layer for the three HOLE-TYPE probe scenes
(`probeH1_near_hole`, `probeH2_offpath_hole`, `probeH3_hidden_hole`).

WHAT THESE SCENES ARE FOR
-------------------------
OVERNIGHT_BRIEF_0820 §4 C1: a **zero-shot, evaluation-only** probe of whether
the frozen v2 checkpoints generalise from stair/edge drops to a *hole* — "a
local depression surrounded by ground on every side, depth >= 0.3 m, opening
0.5–1.5 m". Nothing here may ever enter training (brief C1, "훈련 편입 절대 금지"),
and nothing here writes into the frozen corpus (absolute rules 1, 2, 4).

WHY A SEPARATE COMMON FILE
--------------------------
The three probes share one geometric contract and it is the contract, not the
dressing, that has to be right. Putting it in one file means the twin rule is
implemented once and self-checked once.

THE TWIN CONTRACT (this is the whole file, in five lines)
---------------------------------------------------------
1. Ground is authored as **four paving boxes around the opening** — never one
   box with a hole punched in it, because there is no CSG here and a covering
   box is what makes a hole invisible to `AabbPrefilter.ground_z`.
2. The ONLY prims that differ between the arms are the pit liner + pit floor
   (hazard ON) and the flush fill patch (hazard OFF). Everything else —
   paving, surround, kerbs, planters, facade, props — is authored identically
   in both arms.
3. Every arm-varying prim lies at **x > 0** in world space... more precisely at
   `x > TWIN_SAFE_X`, while every camera stands at `x = -d`, `d in [1.2, 12]`.
   So `pre.ground_z(-d, y)` reads the same paving in both arms and the camera
   datum cannot move. This is the D15/D17 lesson: a toggle that shifts
   `ground_z` under the camera breaks the pair, and D20 then has to rescue it
   with a 0.15 m pose tolerance (see nightrun B5).
4. The paving and the fill patch are `skin_exclude`d, so the top face is
   exactly z = 0.000 in both arms and the labeller's twin heightmap diff over
   the opening is exactly `0.000 - (-depth)`, auditable by hand.
5. No dressing is hazard-correlated. In the C2/N3 caveat the off arm lost its
   leaf mound with the drop, so the twin delta mixed "the drop went away" with
   "the decoration went away". Here the off arm is the on arm minus the void,
   plus a patch of the same paving. Any twin delta these scenes produce is
   attributable to the hole and to nothing else.

ASSETS: Isaac primitives (`add_box` / `add_cylinder`) plus the repository's own
texture set only. No external-repository asset is imported (brief rule 6).

Coordinates: Z-up, metres, travel axis +X, cameras at x = -d looking toward +X.
"""

import math

import scene_common as sc


# ===========================================================================
# [0] Constants shared by the three probes
# ===========================================================================
# Cameras stand at x = -d with d drawn LogU[1.2, 12] (`variation_kit.CAM_DIST`).
# Anything the hazard toggle touches must sit strictly east of this line, with
# margin. -1.0 is 0.2 m east of the closest a camera can ever stand.
TWIN_SAFE_X = -1.00

PAVING_Z = 0.0           # walked surface, both arms, every probe
PAVING_T = 0.22          # slab thickness
SURROUND_Z = -0.03       # surrounding ground top (3 cm kerb-less step down)
SURROUND_T = 1.00
SURROUND_HALF = 60.0

# Pit liner: the inner face is set this far OUTSIDE the opening so it is never
# coplanar with the paving's cut face (sceneD2's skirt convention, brief §A-8).
LINER_INSET = 0.01
LINER_T = 0.22
# Liner top sits 1 cm under the paving top face, so the paving's own cut face
# is what the camera sees for the first 0.22 m of the drop.
LINER_TOP_UNDER = 0.01
PIT_FLOOR_T = 0.30
PIT_FLOOR_MARGIN = 0.18   # floor plate overhang past the liner outer face


# ===========================================================================
# [1] Ground: four paving boxes around the opening + a surround ring
# ===========================================================================
def paving_boxes(rect, opening, z_top=PAVING_Z, thick=PAVING_T):
    """(name, center, size) for the 4 paving boxes that tile `rect` while
    leaving `opening` empty.

    rect     = (x0, y0, x1, y1) of the paved area
    opening  = (x0, y0, x1, y1) of the void, strictly inside rect

    The split is W / E over the full width, then S / N over the opening's x
    span only — sceneD2's `build_slab` layout, which guarantees that no box's
    XY footprint ever covers the opening. That is the property the labeller's
    heightmap depends on: `AabbPrefilter.ground_z` is `max(hi_z)` over the boxes
    whose footprint contains the cell, so one covering box would silently erase
    the hole from the GT while leaving it perfectly visible in the render.
    """
    rx0, ry0, rx1, ry1 = rect
    ox0, oy0, ox1, oy1 = opening
    if not (rx0 < ox0 < ox1 < rx1 and ry0 < oy0 < oy1 < ry1):
        raise ValueError(f"opening {opening} is not strictly inside rect {rect}")
    cz = z_top - thick / 2.0
    return [
        ("Paving_W", ((rx0 + ox0) / 2.0, (ry0 + ry1) / 2.0, cz),
         (ox0 - rx0, ry1 - ry0, thick)),
        ("Paving_E", ((ox1 + rx1) / 2.0, (ry0 + ry1) / 2.0, cz),
         (rx1 - ox1, ry1 - ry0, thick)),
        ("Paving_S", ((ox0 + ox1) / 2.0, (ry0 + oy0) / 2.0, cz),
         (ox1 - ox0, oy0 - ry0, thick)),
        ("Paving_N", ((ox0 + ox1) / 2.0, (oy1 + ry1) / 2.0, cz),
         (ox1 - ox0, ry1 - oy1, thick)),
    ]


def surround_boxes(rect, z_top=SURROUND_Z, thick=SURROUND_T,
                   half=SURROUND_HALF, overlap=0.06):
    """Four boxes filling the annulus between `rect` and a `half` x `half`
    square, 3 cm below the paving. Pushed `overlap` inside the paved rectangle
    so the vertical faces are never coplanar with the paving sides (Z-fighting).

    It can never cover an opening, because an opening is strictly inside
    `rect` and these four boxes are strictly outside `rect` minus `overlap`.
    """
    rx0, ry0, rx1, ry1 = rect
    x0, x1 = rx0 + overlap, rx1 - overlap
    y0, y1 = ry0 + overlap, ry1 - overlap
    cz = z_top - thick / 2.0
    H = half
    return [
        ("Ground_W", ((-H + x0) / 2.0, 0.0, cz), (x0 + H, 2.0 * H, thick)),
        ("Ground_E", ((x1 + H) / 2.0, 0.0, cz), (H - x1, 2.0 * H, thick)),
        ("Ground_S", ((x0 + x1) / 2.0, (-H + y0) / 2.0, cz),
         (x1 - x0, y0 + H, thick)),
        ("Ground_N", ((x0 + x1) / 2.0, (y1 + H) / 2.0, cz),
         (x1 - x0, H - y1, thick)),
    ]


# ===========================================================================
# [2] The hazard itself — pit liner + floor (ON) / flush patch (OFF)
# ===========================================================================
def pit_boxes(opening, depth, paving_z=PAVING_Z, paving_t=PAVING_T):
    """(name, center, size, role) for the hazard-ON prims: 4 liner walls + the
    pit floor plate.

    `role` is "wall" or "floor" so the caller can bind two materials without
    re-deriving the layout.

    Geometry notes, all of them anti-coplanarity, all of them sceneD2's:
      * the liner inner face is `LINER_INSET` OUTSIDE the opening, so the 0.22 m
        of paving cut face and the liner face are 1 cm apart in plan;
      * W/E run long in y and S/N run long in x, overlapping at the corners, so
        no two liner boxes share a face;
      * S/N lose 4 mm of height so the corner overlaps are not coplanar in z
        either;
      * the floor plate overhangs the liner by `PIT_FLOOR_MARGIN` and its top is
        the hazard datum: `z_top - depth`.
    """
    ox0, oy0, ox1, oy1 = opening
    xa, xb = ox0 - LINER_INSET, ox1 + LINER_INSET
    ya, yb = oy0 - LINER_INSET, oy1 + LINER_INSET
    z_floor = paving_z - depth
    z_top = paving_z - LINER_TOP_UNDER
    z_bot = z_floor - 0.06                    # liner foot buried in the plate
    cz, hz = (z_bot + z_top) / 2.0, z_top - z_bot
    t, e = LINER_T, 0.02
    out = [
        ("Pit_Wall_W", (xa - t / 2.0, (ya + yb) / 2.0, cz),
         (t, yb - ya + 2.0 * e, hz), "wall"),
        ("Pit_Wall_E", (xb + t / 2.0, (ya + yb) / 2.0, cz),
         (t, yb - ya + 2.0 * e, hz), "wall"),
        ("Pit_Wall_S", ((xa + xb) / 2.0, ya - t / 2.0, cz),
         (xb - xa + 2.0 * (t + e), t, hz - 0.004), "wall"),
        ("Pit_Wall_N", ((xa + xb) / 2.0, yb + t / 2.0, cz),
         (xb - xa + 2.0 * (t + e), t, hz - 0.004), "wall"),
        ("Pit_Floor", ((xa + xb) / 2.0, (ya + yb) / 2.0,
                       z_floor - PIT_FLOOR_T / 2.0),
         (xb - xa + 2.0 * (t + PIT_FLOOR_MARGIN),
          yb - ya + 2.0 * (t + PIT_FLOOR_MARGIN), PIT_FLOOR_T), "floor"),
    ]
    return out


def fill_patch_box(opening, paving_z=PAVING_Z, thick=PAVING_T):
    """The single hazard-OFF prim: a paving slab exactly filling the opening,
    top face flush with the surrounding paving.

    Exactly filling (not oversized) matters: an oversized patch would overlap
    the paving boxes in plan and its AABB would then also sit over ground the
    ON arm has at the same height — harmless for z, but it would make the
    "which prims differ between the arms" audit read wrong.
    """
    ox0, oy0, ox1, oy1 = opening
    return ("Fill_Patch",
            ((ox0 + ox1) / 2.0, (oy0 + oy1) / 2.0, paving_z - thick / 2.0),
            (ox1 - ox0, oy1 - oy0, thick))


# ===========================================================================
# [3] Twin self-check — runs on CPU, no Isaac, called by every scene's main()
# ===========================================================================
def twin_audit(opening, depth, twin_safe_x=TWIN_SAFE_X):
    """Return a dict proving the twin contract for this opening; raise on a
    violation. Called before the Isaac boot so `NEGOBS_SMOKE=1` exercises it.

    The check is deliberately about the ARM-VARYING PRIMS ONLY. Whatever else a
    probe scene builds, it builds identically in both arms, so the pair can only
    break here.
    """
    ox0, oy0, ox1, oy1 = opening
    on = pit_boxes(opening, depth)
    off_name, off_c, off_s = fill_patch_box(opening)

    # (a) THE AIRTIGHT ONE. `AabbPrefilter.ground_z` is max(hi_z) over the boxes
    #     whose XY footprint contains the cell. Every hazard-ON prim's TOP is
    #     strictly below the paving top, so wherever an ON prim's footprint
    #     overlaps a paving box the paving still wins the max and the reading is
    #     the same as in the OFF arm. That is what makes the pit liner harmless
    #     even where it reaches back under the walked surface.
    tops = [c[2] + s[2] / 2.0 for _n, c, s, _r in on]
    if max(tops) >= PAVING_Z:
        raise AssertionError(
            f"[twin] a hazard-ON prim tops out at z={max(tops):.4f} >= the "
            f"paving top z={PAVING_Z:.4f}. It would out-rank the paving in "
            f"`AabbPrefilter.ground_z` and move the heightmap outside the "
            f"opening, breaking the pair.")
    # (b) The single hazard-OFF prim must be EXACTLY the opening in plan, so it
    #     only ever fills ground the ON arm left void and never overlaps a
    #     paving box it is flush with.
    px0, px1 = off_c[0] - off_s[0] / 2.0, off_c[0] + off_s[0] / 2.0
    py0, py1 = off_c[1] - off_s[1] / 2.0, off_c[1] + off_s[1] / 2.0
    if max(abs(px0 - ox0), abs(px1 - ox1),
           abs(py0 - oy0), abs(py1 - oy1)) > 1e-9:
        raise AssertionError(
            f"[twin] the OFF-arm fill patch {(px0, py0, px1, py1)} is not "
            f"exactly the opening {opening}")

    # (c) Belt and braces: nothing the toggle touches may reach the strip a
    #     camera can stand on. Cameras are at x = -d, d in [1.2, 12].
    west = min([c[0] - s[0] / 2.0 for _n, c, s, _r in on] + [px0])
    if west <= twin_safe_x:
        raise AssertionError(
            f"[twin] an arm-varying prim reaches x={west:.3f}, at or west of "
            f"the camera-safe line x={twin_safe_x:.2f}. A camera at d="
            f"{-west:.2f} m would stand on ground that MOVES with the hazard "
            f"toggle, which is exactly the D15/D17 defect.")
    off = [(off_name, off_c, off_s)]
    if depth < 0.30:
        raise AssertionError(f"[twin] depth {depth} m is under the "
                             f"0.30 m hazard threshold (gridspec hazard_depth_m)")
    # heightmap window of the labeller (run_data_render.HM_*): x [-2, 14],
    # y [-8, 8]. A footprint outside it cannot become GT.
    if not (-2.0 <= ox0 and ox1 <= 14.0 and -8.0 <= oy0 and oy1 <= 8.0):
        raise AssertionError(f"[twin] opening {opening} leaves the heightmap "
                             f"window x[-2,14] y[-8,8]")
    return dict(
        opening=list(opening), depth=depth,
        size=[round(ox1 - ox0, 3), round(oy1 - oy0, 3)],
        area=round((ox1 - ox0) * (oy1 - oy0), 4),
        westmost_arm_prim=round(west, 3), twin_safe_x=twin_safe_x,
        margin_m=round(west - twin_safe_x, 3),
        n_prims_on=len(on), n_prims_off=len(off),
        on_prim_top_max=round(max(tops), 4), paving_z=PAVING_Z,
        hm_z_on=round(-depth, 3), hm_z_off=0.0,
        hm_diff=round(depth, 3))


def print_twin_audit(tag, audit):
    print(f"[twin] {tag}: opening {audit['size'][0]:.2f} x {audit['size'][1]:.2f} m "
          f"({audit['area']:.2f} m2) · depth {audit['depth']:.2f} m · "
          f"heightmap on {audit['hm_z_on']:+.2f} / off {audit['hm_z_off']:+.2f} "
          f"-> diff {audit['hm_diff']:.2f} m (threshold 0.30)")
    print(f"[twin] arm-varying prims: {audit['n_prims_on']} on / "
          f"{audit['n_prims_off']} off · highest ON prim top "
          f"{audit['on_prim_top_max']:+.4f} < paving {audit['paving_z']:+.4f} "
          f"· westmost x {audit['westmost_arm_prim']:+.3f} vs camera-safe line "
          f"{audit['twin_safe_x']:+.2f} (margin {audit['margin_m']:.3f} m) "
          f"-> ground_z under every camera is arm-invariant")


# ===========================================================================
# [4] Shared lighting — copied from sceneD2 (the measured C' outdoor noon rig)
# ===========================================================================
def probe_light():
    """The sceneD2 noon rig verbatim.

    Reused rather than re-tuned because the ledger class these probes are
    registered under is sceneD2's (`C'`, no criterion-B firing at +-35 deg), and
    reusing the rig is what makes that borrowing honest. `run_data_render`
    replaces the values per condition through `LightingControl.apply_cond`
    anyway; this dict is only the L0 baseline and the GUI look-check rig.
    """
    return dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        noon_sun_enable=True, noon_sun_elev=49.79,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    )


# ===========================================================================
# [5] Small builders every probe uses (Isaac primitives only)
# ===========================================================================
def build_kerb_line(BOX, root, mtl, y, x0, x1, top=0.12, width=0.18,
                    z_base=PAVING_Z):
    """A granite kerb run along `y`. Present in BOTH arms — it is the paved-area
    boundary, not a hazard cue."""
    BOX(f"{root}/Kerb_{int(round(y * 100))}",
        ((x0 + x1) / 2.0, y, z_base + top / 2.0 - 0.01),
        (x1 - x0, width, top), mtl)


def build_bollard_row(CYL, root, mtl, xs, y, r=0.06, h=0.90):
    """Statutory bollards (dia 0.12 x h 0.90, `batch1_common.BOLLARD_V51`).
    Placed only where they cannot guard the opening — these probes are about an
    UNGUARDED hole, and a bollard ring around it would be the drop cue itself
    (the 08-05 'guard = drop cue' doctrine)."""
    for i, x in enumerate(xs):
        CYL(f"{root}/Bollard_{i}", (x, y, h / 2.0 - 0.01), r, h, mtl)


def build_planter(BOX, root, tag, rect, top, mtl_shell, mtl_soil,
                  shell_t=0.12, soil_drop=0.06):
    """A raised planter box: concrete shell + a recessed soil face.

    Two prims per side would be six prims; a solid shell plus one soil slab is
    two, reads the same at every distance this probe uses, and keeps the AABB
    that matters (the occluding silhouette) exactly `top`.
    """
    x0, y0, x1, y1 = rect
    BOX(f"{root}/Planter_{tag}_Shell",
        ((x0 + x1) / 2.0, (y0 + y1) / 2.0, top / 2.0 - 0.01),
        (x1 - x0, y1 - y0, top), mtl_shell)
    BOX(f"{root}/Planter_{tag}_Soil",
        ((x0 + x1) / 2.0, (y0 + y1) / 2.0, top - soil_drop / 2.0 - 0.005),
        (x1 - x0 - 2.0 * shell_t, y1 - y0 - 2.0 * shell_t, soil_drop),
        mtl_soil)


def build_facade_wall(BOX, root, mtl, x_face, y0, y1, h=7.0, t=0.6):
    """A blank building wall that closes the +X horizon so the frame is a place,
    not a plane. Far enough east that it never enters a hazard wedge."""
    BOX(f"{root}/Facade", (x_face + t / 2.0, (y0 + y1) / 2.0, h / 2.0 - 0.05),
        (t, y1 - y0, h), mtl)


def build_railing_run(BOX, CYL, root, tag, y, x0, x1, mtl,
                      rail_h=1.10, post_r=0.025, rail_r=0.020, n_post=5):
    """One statutory railing LINE (not a ring). Used by probeH3 only, and only
    because a planter edge at 0.80 m beside a walked route is where a real site
    puts one — it guards the planter, not the pit. Off by default; the pit stays
    unguarded in every arm of every probe."""
    for i in range(n_post):
        x = x0 + (x1 - x0) * i / max(1, n_post - 1)
        CYL(f"{root}/Rail_{tag}_P{i}", (x, y, rail_h / 2.0 - 0.01),
            post_r, rail_h, mtl)
    for k, zc in enumerate((rail_h - 0.05, rail_h * 0.55)):
        CYL(f"{root}/Rail_{tag}_R{k}", ((x0 + x1) / 2.0, y, zc),
            rail_r, x1 - x0, mtl, rotY=90.0)


# ===========================================================================
# [6] Composition report — the numbers the scene headers quote
# ===========================================================================
def sight_report(tag, opening, depth, cam_h, cam_d, occluder=None):
    """One line of geometric evidence per camera the scene wants to talk about.

    `wall_exposed` = how far the grazing ray over the NEAR lip has fallen by the
    time it reaches the FAR lip: > 0 means interior surface is in view (tier V
    is reachable), >= depth means the pit floor itself is.
    `x_reveal` (with an occluder) = the x beyond which ground becomes visible
    again over the occluder's far top edge; the opening is hidden when
    `x_reveal >= opening far lip` (tier H by construction).
    """
    ox0, _oy0, ox1, _oy1 = opening
    d_near = ox0 + cam_d
    wall = cam_h * (ox1 - ox0) / max(1e-6, d_near)
    line = (f"[sight] {tag}: d {cam_d:.2f} h {cam_h:.2f} -> near lip "
            f"{d_near:.2f} m, wall_exposed {wall:.3f} m")
    if occluder is not None:
        x_occ, h_occ = occluder
        if cam_h <= h_occ:
            line += "  · occluder is TALLER than the eye -> hidden"
        else:
            x_rev = x_occ + h_occ * (x_occ + cam_d) / (cam_h - h_occ)
            line += (f"  · x_reveal {x_rev:.2f} vs far lip {ox1:.2f} -> "
                     f"{'HIDDEN' if x_rev >= ox1 else 'VISIBLE'}")
    return line


def vfov_deg(hfov_deg, res_w=1920, res_h=1080):
    return math.degrees(2.0 * math.atan(
        math.tan(math.radians(hfov_deg) / 2.0) * res_h / res_w))


# ===========================================================================
# [7] Scene-file boilerplate helpers
# ===========================================================================
def deep_update(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            deep_update(dst[k], v)
        else:
            dst[k] = v
    return dst


def views_for(gy, approach, brink, graze, overview):
    """`sc.grid_views` plus four named cuts.

    `sc.grid_views` MUST be called: `run_data_render.scene_proc` patches it in
    order to learn the scene's walk axis `gy`, and a scene that never calls it
    silently renders every camera at gy = 0.
    """
    views = sc.grid_views(gy)
    views["approach"] = dict(eye=approach[0], tgt=approach[1])
    views["brink"] = dict(eye=brink[0], tgt=brink[1])
    views["graze"] = dict(eye=graze[0], tgt=graze[1])
    views["beauty_overview"] = dict(eye=overview[0], tgt=overview[1])
    return views
