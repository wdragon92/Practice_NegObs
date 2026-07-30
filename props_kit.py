#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""props_kit — W3 K4(c) prop form templates.

WHAT THIS MODULE IS FOR
-----------------------
`w3r_prop_mapping_v1.md` graded the standing props of all 33 scenes and returned a
uniform verdict: the *placement* passes and the *form* fails. A bench is a 60 mm slab on
four 60 mm legs, a bin is a two-prim drum, a bollard is a bare cylinder with no cap and
no plate, a canopy is a flat 140 mm slab with no rafters and no slope. Each of those is a
**shared builder**, so each defect is reproduced everywhere the builder is called - 58
bench instances over 14 scenes, ~53 streetlight poles over 14, 47 planters over 12.

This file holds the replacement forms. It is **additive**: nothing in the tree imports it
yet, so landing it moves zero geometry, and each scene adopts a template on its own pass
with its own gate. `scene_common`'s existing builders are deliberately left in place -
deleting them would be a 33-scene edit, and spec §6.2-K4c authorises signature-preserving
work only.

DIMENSIONS ARE SOURCED, NOT INVENTED
------------------------------------
Every number below carries one of four tags:
  `[law]`      a statute, ordinance or national standard
  `[KS]`       a Korean Standard product dimension
  `[practice]` measured or catalogued market practice, cited in the surveys
  `[measured]` measured from the repo's own assets or renders this wave
Anything that would otherwise be a guess is a **named parameter with a documented
default**, so a scene can state its own value rather than inherit an invention.

CONVENTIONS
-----------
* Local frame. Every builder defines an `Xform` at `prefix`, places it at
  `(cx, cy, base_z)` with an optional yaw, and authors children in that local frame.
  This is `scene_common.build_bench`'s convention and the reason yaw costs one op.
* Materials come from the caller. This module creates a material only where the *form*
  is the material (the RF-2 age ladder, RF-5's statutory yellow, G8's glass).
* Return value is a dict of counts, so a scene's self-check can assert them.
* No humans, no vehicles, no seasonal or event-specific element (§12 do-not-touch).
"""

import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import scene_common as sc                                    # noqa: E402


# ===========================================================================
# 0. Shared material vocabulary
# ===========================================================================

# **RF-2 · the three-rung metal age ladder** `[practice - spec §10.7 RF-2]`.
# The library's universal `metallic 0.9 / roughness 0.35` mirror stainless is wrong *as a
# default*: it is one era of one product. The deliverable is the **mismatch inside one
# frame** - a 1980s painted rail next to a 2010s brushed one is what a real Korean street
# looks like after thirty years of piecemeal renewal.
#   Two rules that are easy to lose:
#     - repaint does **not** reach behind brackets or under the top rail -> author a tonal
#       split, do not repaint the whole member;
#     - galvanizing fails at welds and feet **first** -> rust-map those, not the surface.
METAL_AGE = {
    # era key      albedo         rough        metallic  note
    "painted_80s": ((0.28, 0.30, 0.29), 0.65, 0.0),   # mild steel, chip/rust at joints+feet
    "galv_90s":    ((0.50, 0.51, 0.52), 0.52, 0.6),   # hot-dip, faint spangle, white bloom
    "sts304_10s":  ((0.55, 0.56, 0.58), 0.35, 0.9),   # brushed anisotropy along the tube
}

# Grip diameters `[law - 편의증진법 별표1; practice - RF-2]`. O34 is the compliant default;
# **O42.4 STS304 is a real retrofit value, not an error** - do not "correct" it.
GRIP_D_COMPLIANT = 0.034
GRIP_D_RETROFIT = 0.0424

# **RF-5 · statutory safety yellow** `[law - 산업안전보건법 별표8, 5Y 8.5/12]`.
# This is the one yellow that is allowed to appear on a nosing or a chevron. The library's
# invented chrome yellows on 16 / C4 / N4 are discharged by using this value.
SAFETY_YELLOW = (0.941, 0.745, 0.000)          # #F0BE00
SAFETY_BLACK = (0.08, 0.08, 0.08)


def _mtl(stage, path, rgb, rough=0.6, metal=0.0):
    """A constant-colour PBR, created once per path."""
    return sc.make_pbr(stage, path, diffuse_color=tuple(float(v) for v in rgb),
                       roughness_const=float(rough), metallic=float(metal))


def age_mtl(stage, path, era="sts304_10s"):
    """Material for one rung of the RF-2 age ladder."""
    rgb, rough, metal = METAL_AGE.get(era, METAL_AGE["sts304_10s"])
    return _mtl(stage, path, rgb, rough, metal)


def _root(stage, prefix, cx, cy, base_z, yaw=0.0):
    from pxr import Gf, UsdGeom
    root = UsdGeom.Xform.Define(stage, prefix)
    xf = UsdGeom.Xformable(root)
    xf.AddTranslateOp().Set(Gf.Vec3d(float(cx), float(cy), float(base_z)))
    if abs(float(yaw)) > 1e-9:
        xf.AddRotateZOp().Set(float(yaw))
    return root


# ===========================================================================
# 1. C1 · slatted bench  (14 scenes / 58 instances)
# ===========================================================================

def build_bench_slat(stage, prefix, cx, cy, base_z, mtl, frame_mtl=None,
                     length=1.60, depth=0.54, seat_h=0.42, back=False,
                     slats=5, slat_t=0.045, slat_gap=0.012, yaw=0.0):
    """C1 replacement: a **slatted** seat on two end frames.

    `scene_common.build_bench` builds a single 60 mm slab on four 60 mm legs. There is no
    Korean street bench of that form - the survey found none in any catalogue - and at
    grid distance it reads as "a brown board", which is exactly what 통람 recorded.

    Dimensions `[practice - w3r_prop_mapping_v1 §C1]`: **1600 x 540 x 700 overall**, seat
    height 420 mm, **five 45 mm slats at 12 mm gaps**. Seat height 420 is the amenity
    figure; 700 is the overall height *with* a back, so `back=False` (the street default,
    and what every current call site draws) stops at the seat.

    The end frames are the load path and the reason the form reads: two upside-down
    U frames of 50 x 50 mm section, inset 80 mm from the ends, not four separate legs.
    """
    fm = frame_mtl or mtl
    _root(stage, prefix, cx, cy, base_z, yaw)
    n = max(1, int(slats))
    span = n * slat_t + (n - 1) * slat_gap
    y0 = -span / 2.0 + slat_t / 2.0
    for i in range(n):
        sc.add_box(stage, f"{prefix}/Slat_{i}",
                   (0.0, y0 + i * (slat_t + slat_gap), seat_h - slat_t / 2.0),
                   (length, slat_t, slat_t), mtl, collider=(i == n // 2))
    # two end frames: uprights + a cross member under the slats
    fx = length / 2.0 - 0.08
    for sx, tag in ((fx, "P"), (-fx, "N")):
        for sy, t2 in ((depth / 2.0 - 0.05, "a"), (-depth / 2.0 + 0.05, "b")):
            sc.add_box(stage, f"{prefix}/Leg_{tag}{t2}",
                       (sx, sy, (seat_h - slat_t) / 2.0),
                       (0.05, 0.05, seat_h - slat_t), fm)
        sc.add_box(stage, f"{prefix}/Frame_{tag}",
                   (sx, 0.0, seat_h - slat_t - 0.025),
                   (0.05, depth - 0.10, 0.05), fm)
    made = dict(slat=n, leg=4, frame=2, backrest=0)
    if back:
        # Backrest: 3 slats on a 12 deg rake, top at 700 mm overall.
        for j in range(3):
            sc.add_box(stage, f"{prefix}/Back_{j}",
                       (0.0, -depth / 2.0 + 0.06,
                        seat_h + 0.10 + j * (slat_t + slat_gap + 0.04)),
                       (length, slat_t, slat_t), mtl)
        made["backrest"] = 3
    return made


# ===========================================================================
# 2. C1b · platform gang seat  (sceneD4)
# ===========================================================================

def build_bench_bucket(stage, prefix, cx, cy, base_z, shell_mtl, frame_mtl,
                       gangs=4, seat_w=0.45, seat_d=0.44, seat_h=0.43,
                       wall_fixed=True, yaw=0.0):
    """C1b: the **3-4 gang bucket seat** of a Korean subway platform.

    sceneD4 currently stands timber park benches on a platform - the wrong *class* of
    object, not the wrong dimensions `[w3r_prop_mapping_v1 §C1b]`. The real fixture is a
    row of moulded stainless or plastic bucket shells on a single tubular frame, usually
    cantilevered off the wall so the platform floor can be washed under it.

    The shell is what makes it read: a dished seat (a shallow box with a raised lip) and a
    low back per gang, all on one continuous frame - not `gangs` separate benches.
    """
    _root(stage, prefix, cx, cy, base_z, yaw)
    span = gangs * seat_w
    for g in range(int(gangs)):
        gy = -span / 2.0 + seat_w * (g + 0.5)
        sc.add_box(stage, f"{prefix}/Shell_{g}", (0.0, gy, seat_h - 0.03),
                   (seat_d, seat_w - 0.02, 0.06), shell_mtl, collider=(g == 0))
        sc.add_box(stage, f"{prefix}/Lip_{g}", (seat_d / 2.0 - 0.02, gy, seat_h),
                   (0.04, seat_w - 0.02, 0.05), shell_mtl)
        sc.add_box(stage, f"{prefix}/Back_{g}",
                   (-seat_d / 2.0 + 0.03, gy, seat_h + 0.16),
                   (0.05, seat_w - 0.04, 0.30), shell_mtl)
    sc.add_box(stage, f"{prefix}/Rail", (0.0, 0.0, seat_h - 0.10),
               (0.06, span, 0.06), frame_mtl)
    made = dict(gang=int(gangs), rail=1, leg=0, bracket=0)
    if wall_fixed:
        for s, tag in ((1, "P"), (-1, "N")):
            sc.add_box(stage, f"{prefix}/Bracket_{tag}",
                       (-seat_d / 2.0 - 0.04, s * (span / 2.0 - 0.10),
                        seat_h - 0.10), (0.10, 0.06, 0.06), frame_mtl)
        made["bracket"] = 2
    else:
        for s, tag in ((1, "P"), (-1, "N")):
            sc.add_cylinder(stage, f"{prefix}/Leg_{tag}",
                            (0.0, s * (span / 2.0 - 0.12), (seat_h - 0.10) / 2.0),
                            0.03, seat_h - 0.10, frame_mtl)
        made["leg"] = 2
    return made


# ===========================================================================
# 3. C3 · two-gang sorting bin  (11 bins / 4 scenes)
# ===========================================================================

def build_binsort(stage, prefix, cx, cy, base_z, body_mtl, lid_mtl,
                  label_mtl=None, gangs=2, w=0.42, d=0.42, h=0.90, yaw=0.0):
    """C3: the **2-gang sort bin**, not a lidded drum.

    The library's bin is two prims - a O520-560 cylinder and a lid - which is a 1990s
    drum. Korean street furniture since the mid-2000s is a **sorting** bin: an open steel
    frame carrying two liners, a moulded opening ring per gang, a rain lid, a colour-coded
    label band and anchors to the pavement `[practice - w3r_prop_mapping_v1 §C3]`.
    The opening ring and the label band are the two features that make it legible at grid
    distance; the drum has neither.
    """
    _root(stage, prefix, cx, cy, base_z, yaw)
    lab = label_mtl or lid_mtl
    span = gangs * w
    for g in range(int(gangs)):
        gy = -span / 2.0 + w * (g + 0.5)
        sc.add_box(stage, f"{prefix}/Body_{g}", (0.0, gy, h / 2.0),
                   (d, w - 0.02, h), body_mtl, collider=(g == 0))
        # opening ring: a thin frame set 60 mm below the lid
        sc.add_box(stage, f"{prefix}/Ring_{g}", (0.0, gy, h - 0.06),
                   (d - 0.04, w - 0.06, 0.03), lid_mtl)
        sc.add_box(stage, f"{prefix}/Label_{g}", (d / 2.0 + 0.002, gy, h * 0.62),
                   (0.004, w - 0.08, 0.14), lab)
    sc.add_box(stage, f"{prefix}/Lid", (0.0, 0.0, h + 0.025),
               (d + 0.04, span + 0.04, 0.05), lid_mtl)
    for s, tag in ((1, "P"), (-1, "N")):
        sc.add_box(stage, f"{prefix}/Anchor_{tag}",
                   (0.0, s * (span / 2.0 - 0.05), 0.008),
                   (d + 0.02, 0.06, 0.016), body_mtl)
    return dict(gang=int(gangs), lid=1, ring=int(gangs), label=int(gangs), anchor=2)


# ===========================================================================
# 4. C4 · rafter canopy
# ===========================================================================

def build_canopy_rafter(stage, prefix, cx, cy, base_z, roof_mtl, post_mtl,
                        width=4.0, depth=2.6, z_roof=2.7, slope=0.06,
                        rafter_pitch=0.40, eaves=0.20, post_r=0.06,
                        fascia_h=0.12, yaw=0.0):
    """C4: a canopy with **rafters, a slope, a fascia and eaves**.

    `scene_common.build_canopy` is a flat 140 mm slab on four posts: zero slope (so it
    cannot shed water), no rafters (so the soffit is a blank plane) and no eaves (so it
    ends in a knife edge). All three are visible at h0.9-h1.8 because the soffit is what a
    pedestrian under a canopy actually sees.

    Defaults `[practice]`: fall **6 %** to the front, rafters at **400 mm** (band
    300-450), eaves **200 mm** (min 150), fascia 120 mm. `depth` is the structural depth;
    an entry canopy needs 2-3 m to shed rain clear of the door - a 1.4 m entry canopy is
    the defect C0-4 recorded on scene01.
    """
    _root(stage, prefix, cx, cy, base_z, yaw)
    hw, hd = width / 2.0, depth / 2.0
    drop = depth * float(slope)
    n_raf = max(2, int(round(depth / max(rafter_pitch, 0.05))) + 1)
    made = dict(post=0, beam=2, rafter=0, deck=1, fascia=1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            sc.add_cylinder(stage, f"{prefix}/Post_{sx}{sy}".replace("-", "N"),
                            (sx * (hw - 0.15), sy * (hd - 0.15),
                             (z_roof - 0.25) / 2.0),
                            post_r, z_roof - 0.25, post_mtl, collider=True)
            made["post"] += 1
    for sy, tag in ((1, "B"), (-1, "F")):
        sc.add_box(stage, f"{prefix}/Beam_{tag}",
                   (0.0, sy * (hd - 0.15), z_roof - 0.18 - (drop / 2.0 if sy < 0 else 0.0)),
                   (width, 0.12, 0.16), roof_mtl)
    for i in range(n_raf):
        ry = -hd + depth * i / float(n_raf - 1)
        t = (ry + hd) / depth                       # 0 at back, 1 at front
        sc.add_box(stage, f"{prefix}/Rafter_{i}", (0.0, ry, z_roof - 0.06 - drop * t),
                   (width + 2 * eaves, 0.05, 0.09), roof_mtl)
        made["rafter"] += 1
    sc.add_box(stage, f"{prefix}/Deck", (0.0, -drop * 0.0, z_roof - drop / 2.0),
               (width + 2 * eaves, depth + 2 * eaves, 0.04), roof_mtl)
    sc.add_box(stage, f"{prefix}/Fascia", (0.0, -hd - eaves, z_roof - drop - fascia_h / 2.0),
               (width + 2 * eaves, 0.04, fascia_h), roof_mtl)
    return made


# ===========================================================================
# 5. C5 · kerbed planter  (12 scenes / 47 instances)
# ===========================================================================

def build_planter_kerb(stage, prefix, cx, cy, base_z, kerb_mtl, soil_mtl,
                       size=3.0, kerb_t=0.15, kerb_h=0.30, cap_over=0.03,
                       cap_h=0.04, soil_proud=0.01, yaw=0.0):
    """C5: a planter built from **1 m kerb units**, with the soil **above** the cap.

    Two defects in the current builder `[w3r_prop_mapping_v1 §C5]`:
      1. `curb_t = 0.25` is a 250 mm kerb. The Korean product is **KS F 4006 150 x 150 x
         1000** `[KS]`, so 150 mm - the 250 mm block reads as a monument plinth, which is
         exactly the "dark stone box" 통람 flagged as scene01's largest h0.3 occupant.
      2. The soil top sits 100 mm **below** the cap, so the bed reads as an empty stone
         tray. Real beds are filled proud of the kerb - soil settles, it is not excavated.
    The unit joints are modelled, not textured: a 1 m joint rhythm is the single strongest
    cue that a line of stone is a kerb and not a painted band (the same argument K5 makes
    for `build_curb_line`).
    """
    _root(stage, prefix, cx, cy, base_z, yaw)
    half = size / 2.0
    n_unit = max(1, int(round(size / 1.0)))          # 1 m kerb units [KS F 4006]
    made = dict(kerb=0, cap=4, soil=1)
    for tag, ax in (("S", (0.0, -1.0)), ("N", (0.0, 1.0)),
                    ("W", (-1.0, 0.0)), ("E", (1.0, 0.0))):
        for u in range(n_unit):
            t = -half + size * (u + 0.5) / n_unit
            ux = t if ax[0] == 0 else ax[0] * (half - kerb_t / 2.0)
            uy = ax[1] * (half - kerb_t / 2.0) if ax[0] == 0 else t
            sx = (size / n_unit - 0.004) if ax[0] == 0 else kerb_t
            sy = kerb_t if ax[0] == 0 else (size / n_unit - 0.004)
            sc.add_box(stage, f"{prefix}/Kerb_{tag}{u}", (ux, uy, kerb_h / 2.0),
                       (sx, sy, kerb_h), kerb_mtl, collider=True)
            made["kerb"] += 1
        sc.add_box(stage, f"{prefix}/Cap_{tag}",
                   (0.0 if ax[0] == 0 else ax[0] * (half - kerb_t / 2.0),
                    ax[1] * (half - kerb_t / 2.0) if ax[0] == 0 else 0.0,
                    kerb_h + cap_h / 2.0),
                   (size + 2 * cap_over if ax[0] == 0 else kerb_t + 2 * cap_over,
                    kerb_t + 2 * cap_over if ax[0] == 0 else size + 2 * cap_over,
                    cap_h), kerb_mtl)
    inner = size - 2 * kerb_t
    top = kerb_h + cap_h + soil_proud
    sc.add_box(stage, f"{prefix}/Soil", (0.0, 0.0, top / 2.0),
               (inner, inner, top), soil_mtl)
    return made


# ===========================================================================
# 6. C6 · bollard  (>=10 scenes, 60+ instances)
# ===========================================================================

# `[law]` 보도용 볼라드: height **0.80-1.00 m**, spacing about 1.5 m, a reflective band.
# The repo's `scene_common.build_bollard` default is h0.75 - **below the legal minimum**.
BOLLARD_H_MIN = 0.80
BOLLARD_H_MAX = 1.00
BOLLARD_PITCH = 1.5


def build_bollard_v2(stage, prefix, cx, cy, base_z, body_mtl, band_mtl=None,
                     radius=0.055, height=0.85, plate=True, dome=True,
                     band_z=0.62, band_h=0.06, compliant=True, seed=0):
    """C6: dome cap + base plate + anchor cover + reflective band.

    The current bollard is a bare cylinder that penetrates the slab - no cap, no flange,
    mirror-stainless everywhere. Four features carry the read `[practice - §C6]`: the
    **dome cap** (a flat-topped bollard is a pipe offcut), the **base plate with an anchor
    cover ring**, the **reflective band** at knee height, and a body colour that is not a
    mirror.

    `compliant=False` reproduces the measured field population rather than the statute -
    about **three quarters of installed Korean bollards miss at least one of the height,
    spacing or band requirements** `[practice - §C6]`. It is a *deterministic* choice from
    `seed`, not a jitter: the wave abolishes jitter, and "this one is a non-compliant
    installation" is a fact about the site, not noise.
    """
    h = float(height)
    if not compliant:
        # deterministic pick from the three real failure modes
        h = (0.72, 0.75, 0.78)[int(seed) % 3]
    _root(stage, prefix, cx, cy, base_z)
    made = dict(body=1, dome=0, plate=0, cover=0, band=0,
                height=h, compliant=bool(compliant))
    sc.add_cylinder(stage, f"{prefix}/Body", (0.0, 0.0, h / 2.0),
                    radius, h, body_mtl, collider=True)
    if dome:
        sc.add_sphere(stage, f"{prefix}/Dome", (0.0, 0.0, h),
                      (radius, radius, radius * 0.55), body_mtl)
        made["dome"] = 1
    if plate:
        # 100 x 100 mm plate is the RF-1 stock size; a round anchor cover hides the nuts.
        sc.add_box(stage, f"{prefix}/Plate", (0.0, 0.0, 0.004),
                   (0.10, 0.10, 0.008), body_mtl)
        sc.add_cylinder(stage, f"{prefix}/Cover", (0.0, 0.0, 0.022),
                        radius * 1.45, 0.028, body_mtl)
        made["plate"] = made["cover"] = 1
    if band_mtl is not None and (compliant or int(seed) % 3 != 2):
        sc.add_cylinder(stage, f"{prefix}/Band", (0.0, 0.0, min(band_z, h - 0.08)),
                        radius * 1.02, band_h, band_mtl)
        made["band"] = 1
    return made


# ===========================================================================
# 7. C7c · two-post pedestrian sign
# ===========================================================================

def build_sign_2post(stage, prefix, cx, cy, base_z, panel_mtl, post_mtl,
                     panel_w=1.20, panel_h=0.60, panel_bottom=2.50,
                     post_r=0.0303, panel_t=0.06, yaw=0.0):
    """C7c: **two** posts, panel bottom **2.5-3.0 m**.

    `scene_common.build_sign` hangs a 1.0 m wide panel on a single O80 post with its
    bottom edge at 1.40-1.75 m: structurally a cantilever nobody builds, and low enough to
    be a head-strike in the walking zone. The rule `[law - 주소정보시설규칙 준용;
    practice - §C7c]` is a **2.5-3.0 m clear bottom** for pedestrian signage, on two posts
    of O60.5 (or a panel narrow enough - <=0.6 m - to justify one).

    The re-adjudication measured the nearest catalogue asset,
    `pole_fxd_pedestrian_signage_01`, at **373 x 373 x 2122 mm** - shorter than the
    requirement, so it is a dimensional control only and cannot replace this template.
    """
    _root(stage, prefix, cx, cy, base_z, yaw)
    top = panel_bottom + panel_h
    single = panel_w <= 0.60
    xs = (0.0,) if single else (-panel_w / 2.0 + 0.12, panel_w / 2.0 - 0.12)
    for i, px in enumerate(xs):
        sc.add_cylinder(stage, f"{prefix}/Post_{i}", (px, 0.0, top * 0.5),
                        post_r, top, post_mtl, collider=True)
    sc.add_box(stage, f"{prefix}/Panel", (0.0, 0.0, panel_bottom + panel_h / 2.0),
               (panel_w, panel_t, panel_h), panel_mtl)
    return dict(post=len(xs), panel=1, panel_bottom=panel_bottom)


# ===========================================================================
# 8. RF-1 · base plate and its scars
# ===========================================================================

PLATE_STOCK_T = (0.006, 0.008, 0.009)          # 6T / 8T / 9T `[practice - market stock]`


def build_base_plate(stage, prefix, px, py, gz, plate_mtl, bed_mtl=None,
                     plate=0.100, thick=0.008, anchors=4, anchor_d=0.016,
                     anchor_pitch=0.090, bedding=0.010, dust_ring=True):
    """RF-1: **the post does not grow out of the ground; it stands on a bolted plate.**

    The single highest-value retrofit row in the map, and it costs no geometry budget: a
    100 x 100 mm plate in 6/8/9T, **4 x O16 anchors at 90 mm pitch**, one levelling-nut
    course, a 5-15 mm mortar/epoxy bedding smear, and the **drill-dust ring that never
    cleans off** `[practice - RF-1]`.

    Apply to the **retrofit** posts of 02 / 11 / 15 / 16 / 17. Leave the EXPECTED scenes
    (01 / 06 / 08 / 13 / 14 / 20 / 21) embedded with a mortar collar - **the contrast
    between the two is the deliverable, not the plate.**
    """
    made = dict(plate=1, anchor=0, nut=0, bedding=0, ring=0)
    if bed_mtl is not None and bedding > 0:
        sc.add_box(stage, f"{prefix}/Bedding", (px, py, gz + bedding / 2.0),
                   (plate + 0.012, plate + 0.012, bedding), bed_mtl)
        made["bedding"] = 1
    z0 = gz + (bedding if bed_mtl is not None else 0.0)
    sc.add_box(stage, f"{prefix}/Plate", (px, py, z0 + thick / 2.0),
               (plate, plate, thick), plate_mtl)
    hp = anchor_pitch / 2.0
    for i, (sx, sy) in enumerate(((hp, hp), (hp, -hp), (-hp, hp), (-hp, -hp))[:anchors]):
        sc.add_cylinder(stage, f"{prefix}/Anchor_{i}", (px + sx, py + sy,
                                                        z0 + thick + 0.012),
                        anchor_d / 2.0, 0.024, plate_mtl)
        sc.add_cylinder(stage, f"{prefix}/Nut_{i}", (px + sx, py + sy, z0 + thick * 0.5),
                        anchor_d * 0.85, thick, plate_mtl)
        made["anchor"] += 1
        made["nut"] += 1
    if dust_ring and bed_mtl is not None:
        # A 2 mm-proud halo of drill dust and cut slurry, 1.6x the plate. It is dressing,
        # but it is the tell that separates a retrofit from a cast-in post.
        sc.add_box(stage, f"{prefix}/DustRing", (px, py, gz + 0.001),
                   (plate * 1.6, plate * 1.6, 0.002), bed_mtl)
        made["ring"] = 1
    return made


# ===========================================================================
# 9. RF-3 · Korean stainless shape vocabulary
# ===========================================================================

def build_newel_ball(stage, prefix, px, py, top_z, mtl, r=0.045):
    """RF-3: the polished spherical newel ball that terminates a Korean stainless post."""
    sc.add_sphere(stage, f"{prefix}/Ball", (px, py, top_z + r * 0.8), (r, r, r), mtl)
    return dict(ball=1)


def build_gooseneck_return(stage, prefix, px, py, rail_z, mtl, drop=0.30,
                           reach=0.22, r=0.017, seg=6):
    """RF-3: the curved **goose-neck return** that takes a handrail down to its post.

    A Korean stair handrail does not stop dead in mid-air; it curls down and back into the
    post. Approximated by `seg` short cylinders on a quarter-circle in the XZ plane, which
    is enough at every distance the judge cuts use.
    """
    n = 0
    for i in range(int(seg)):
        a0 = math.pi / 2.0 * i / seg
        a1 = math.pi / 2.0 * (i + 1) / seg
        x0, z0 = px + reach * math.sin(a0), rail_z - drop * (1 - math.cos(a0))
        x1, z1 = px + reach * math.sin(a1), rail_z - drop * (1 - math.cos(a1))
        dx, dz = x1 - x0, z1 - z0
        L = math.hypot(dx, dz) or 1e-6
        sc.add_cylinder(stage, f"{prefix}/Neck_{i}",
                        ((x0 + x1) / 2.0, py, (z0 + z1) / 2.0), r, L, mtl,
                        rotY=math.degrees(math.atan2(dx, dz)))
        n += 1
    return dict(neck=n)


def build_beaded_baluster(stage, prefix, px, py, z0, z1, mtl, r=0.009,
                          rings=2, ring_r=0.014, ring_h=0.018):
    """RF-3: a baluster with **turned bead rings** - the cheapest tell of a real product."""
    h = z1 - z0
    sc.add_cylinder(stage, f"{prefix}/Bar", (px, py, z0 + h / 2.0), r, h, mtl)
    for i in range(int(rings)):
        zr = z0 + h * (0.30 + 0.40 * i / max(1, rings - 1) if rings > 1 else 0.35)
        sc.add_cylinder(stage, f"{prefix}/Bead_{i}", (px, py, zr),
                        ring_r, ring_h, mtl)
    return dict(bar=1, bead=int(rings))


def build_hoop_row(stage, prefix, x, y0, y1, gz, mtl, n=4, hoop_w=0.60,
                   hoop_h=0.75, r=0.021, seg=5):
    """RF-3: the **inverted-U stainless hoop row across a stair head**.

    A standard Korean fixture - a row of hoops perpendicular to travel at the top of a
    flight, to stop a running approach - with **zero instances in all 33 scenes** and no
    asset anywhere in the reachable catalogues. The highest-value new prop in the map.
    """
    made = dict(hoop=0, leg=0, arc=0)
    for k in range(int(n)):
        cy = y0 + (y1 - y0) * (k + 0.5) / n
        for s in (-1, 1):
            sc.add_cylinder(stage, f"{prefix}/H{k}_Leg{'P' if s > 0 else 'N'}",
                            (x, cy + s * hoop_w / 2.0,
                             gz + (hoop_h - hoop_w / 2.0) / 2.0),
                            r, hoop_h - hoop_w / 2.0, mtl, collider=True)
            made["leg"] += 1
        for i in range(int(seg)):
            a0 = math.pi * i / seg
            a1 = math.pi * (i + 1) / seg
            y_a = cy + (hoop_w / 2.0) * math.cos(a0)
            z_a = gz + hoop_h - hoop_w / 2.0 + (hoop_w / 2.0) * math.sin(a0)
            y_b = cy + (hoop_w / 2.0) * math.cos(a1)
            z_b = gz + hoop_h - hoop_w / 2.0 + (hoop_w / 2.0) * math.sin(a1)
            dy, dz = y_b - y_a, z_b - z_a
            L = math.hypot(dy, dz) or 1e-6
            sc.add_cylinder(stage, f"{prefix}/H{k}_Arc{i}",
                            (x, (y_a + y_b) / 2.0, (z_a + z_b) / 2.0), r, L, mtl,
                            rotX=math.degrees(math.atan2(-dy, dz)))
            made["arc"] += 1
        made["hoop"] += 1
    return made


# ===========================================================================
# 10. RF-5 · the three nosing tiers
# ===========================================================================

NOSING_TIERS = ("retrofit_strip", "paint_only", "partial_tile")

# Era-conditional application `[practice - spec §10.7 RF-5]`. This mapping is the whole
# point of the row: the library collapsed three different construction eras into one
# chrome-yellow strip.
NOSING_BY_SCENE = {
    "retrofit_strip": ("Scene02", "Scene11", "Scene15", "Scene18"),   # pre-code
    "cast_groove":    ("Scene08", "Scene10", "Scene12", "Scene14"),   # 2010s - NO strip
    "absent":         ("Scene07", "Scene03", "Scene04", "Scene09"),   # stone / natural
}


def build_nosing_tier(stage, prefix, steps, y0, y1, tier="retrofit_strip",
                      mtl=None, width=0.060, proud=0.004, tile_w=0.150,
                      screw_pitch=0.30):
    """RF-5: one of **three** nosing constructions, not one chrome-yellow bar.

    `steps` is `[(xa, xb, z_top), ...]` - the same tuple `scene_common._stair_steps`
    returns, so a scene can hand its own step list straight in.

      `retrofit_strip` - an aluminium profile **60 mm wide** (600-790 mm lengths in 10 mm
          increments) with a ceramic-grit insert. Tells: a regular row of screw heads,
          a height step that casts a shadow at the uphill edge, and the strip **ending
          short of the tread ends** (`inset`), because stock lengths do not match treads.
      `paint_only` - 흰여울 practice: white paint on every nosing, no railing at all.
      `partial_tile` - 감천 practice: anti-slip tile over only the front ~150 mm.

    And the statutory alternative that licenses **absence**: 편의증진법 별표1 제8호 마.(2)
    accepts cast-in 줄눈 grooves with no strip at all, so a visible strip is nearly always
    an add-on. That is why `NOSING_BY_SCENE` has a `cast_groove` and an `absent` class.

    Colour is `SAFETY_YELLOW` = 5Y 8.5/12 `[law]` for the retrofit tier, white for paint.
    """
    if mtl is None:
        rgb = (0.90, 0.90, 0.88) if tier == "paint_only" else SAFETY_YELLOW
        mtl = _mtl(stage, prefix + "/NosingMtl", rgb, rough=0.62)
    inset = 0.06 if tier == "retrofit_strip" else 0.0
    cy, Ly = (y0 + y1) / 2.0, (y1 - y0) - 2 * inset
    made = dict(tier=tier, strip=0, screw=0)
    for i, (xa, xb, ztop) in enumerate(steps, 1):
        if tier == "partial_tile":
            w, thick, zc = tile_w, 0.012, ztop - 0.006
        elif tier == "paint_only":
            w, thick, zc = width, 0.0015, ztop + 0.00075
        else:
            w, thick, zc = width, proud + 0.004, ztop + proud - (proud + 0.004) / 2.0
        sc.add_box(stage, f"{prefix}/Nose_{i}", (xb - w / 2.0, cy, zc),
                   (w, Ly, thick), mtl)
        made["strip"] += 1
        if tier == "retrofit_strip" and screw_pitch > 0:
            n_s = max(2, int(Ly / screw_pitch))
            for k in range(n_s):
                sy = cy - Ly / 2.0 + Ly * (k + 0.5) / n_s
                sc.add_cylinder(stage, f"{prefix}/Screw_{i}_{k}",
                                (xb - w / 2.0, sy, ztop + proud + 0.001),
                                0.004, 0.002, mtl)
                made["screw"] += 1
    return made


# ===========================================================================
# 11. G6 · bronze horizontal-tube railing
# ===========================================================================

def build_tube_railing(stage, prefix, pts, gz_fn, mtl, rails=4, rail_h=1.10,
                       tube_r=0.024, post_r=0.030, post_pitch=1.80,
                       bottom=0.12):
    """G6: **bronze horizontal tube railing**, 3-4 rails, on a polyline.

    The image the wave is matching (G6, scene06) shows the helix and the deck both guarded
    by horizontal bronze tubes - *not* the vertical-baluster guardrail the library builds
    everywhere. It is a different product with a different silhouette, and on a curved
    structure it is what reads.

    **Statutory note the caller must not lose**: a horizontal-rail guard does not satisfy
    the 안목 <=100 mm rule the way a baluster guard does; the compliant version is 4 rails
    inside a 1.10 m height, which is why `rails=4` is the default and `rails=3` is offered
    only for a deck edge that is not a fall hazard. `scene_common.BALUSTER_CLEAR_MAX` is
    the reference value; with 4 rails over 1.10 m the largest clear span is
    (1.10 - 0.12) / 3 - 2 * 0.024 = **0.279 m**, i.e. a *deliberately* non-baluster form.
    Do not blend the two: the mixture is what makes a railing read as procedural.
    """
    made = dict(post=0, rail=0, clear_max=0.0)
    if len(pts) < 2:
        return made
    total = 0.0
    segs = []
    for a, b in zip(pts, pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        segs.append((a, b, L))
        total += L
    # posts at pitch along the polyline
    n_post = max(2, int(round(total / post_pitch)) + 1)
    for i in range(n_post):
        s = total * i / (n_post - 1)
        acc = 0.0
        for a, b, L in segs:
            if acc + L >= s or (a, b, L) is segs[-1]:
                t = (s - acc) / L if L > 1e-9 else 0.0
                px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                break
            acc += L
        g = float(gz_fn(px, py))
        sc.add_cylinder(stage, f"{prefix}/Post_{i}", (px, py, g + rail_h / 2.0),
                        post_r, rail_h, mtl, collider=True)
        made["post"] += 1
    # rails: one run of cylinders per level, per polyline segment
    for r in range(int(rails)):
        z_off = bottom + (rail_h - bottom) * r / max(1, rails - 1)
        for j, (a, b, L) in enumerate(segs):
            mx, my = (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0
            g = float(gz_fn(mx, my))
            ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
            sc.add_cylinder(stage, f"{prefix}/Rail_{r}_{j}", (mx, my, g + z_off),
                            tube_r, L, mtl, rotY=90.0)
            # rotY=90 lays the Z axis along +X; the bearing is applied by the caller's
            # frame when the polyline is axis-aligned, which is the only case shipped.
            made["rail"] += 1
            del ang
    made["clear_max"] = (rail_h - bottom) / max(1, rails - 1) - 2 * tube_r
    return made


# ===========================================================================
# 12. G8 · glass balustrade
# ===========================================================================

def build_glass_balustrade(stage, prefix, pts, gz_fn, glass_mtl, cap_mtl,
                           shoe_mtl=None, panel_h=1.10, panel_t=0.019,
                           panel_len=1.50, joint=0.012, cap_r=0.025,
                           shoe_h=0.10):
    """G8: **structural-glass balustrade** - shoe channel, glass panels, capping rail.

    The sunken-plaza image guards its curved stair and its pit edge with glass, which is
    what a 2010s Korean civic plaza actually uses. Three parts and no posts: a stainless
    **shoe channel** cast into the slab, **laminated panels** (17.5-21.5 mm; 19 mm here)
    in `panel_len` bays with a **12 mm joint**, and a round **capping rail**.

    The panel joints are the whole read - a single continuous glass sheet is the give-away
    of a procedural balustrade. Glass gets `opacity`/roughness from the caller's material;
    this builder only decides the form.
    """
    made = dict(panel=0, shoe=0, cap=0)
    for j, (a, b) in enumerate(zip(pts, pts[1:])):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(round(L / panel_len)))
        for k in range(n):
            t0, t1 = k / n, (k + 1) / n
            x0, y0 = a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0
            x1, y1 = a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1
            mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
            g = float(gz_fn(mx, my))
            seg_len = math.hypot(x1 - x0, y1 - y0) - joint
            sc.add_box(stage, f"{prefix}/Panel_{j}_{k}",
                       (mx, my, g + shoe_h + panel_h / 2.0),
                       (seg_len, panel_t, panel_h), glass_mtl)
            made["panel"] += 1
        mx, my = (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0
        g = float(gz_fn(mx, my))
        if shoe_mtl is not None:
            sc.add_box(stage, f"{prefix}/Shoe_{j}", (mx, my, g + shoe_h / 2.0),
                       (L, panel_t + 0.030, shoe_h), shoe_mtl)
            made["shoe"] += 1
        sc.add_cylinder(stage, f"{prefix}/Cap_{j}",
                        (mx, my, g + shoe_h + panel_h + cap_r * 0.6),
                        cap_r, L, cap_mtl, rotY=90.0)
        made["cap"] += 1
    return made


# ===========================================================================
# 13. G13 · gantry sign, chevron band, trench grating
# ===========================================================================

def build_gantry_sign(stage, prefix, x, y0, y1, gz, clear_h, post_mtl, panel_mtl,
                      post_w=0.20, panel_h=0.70, panel_t=0.10):
    """G13: the **stainless gantry sign** over a basement ramp mouth.

    Two square posts outside the traffic envelope carrying a full-width panel above a
    stated clear height. `clear_h` is the *signed* clearance of the garage (usually
    2.1-2.3 m for a passenger-car basement) and must be authored, never assumed: the sign
    exists precisely because the clearance is binding.
    """
    for s, tag in ((y0, "N"), (y1, "P")):
        sc.add_box(stage, f"{prefix}/Post_{tag}", (x, s, gz + (clear_h + panel_h) / 2.0),
                   (post_w, post_w, clear_h + panel_h), post_mtl, collider=True)
    sc.add_box(stage, f"{prefix}/Panel", (x, (y0 + y1) / 2.0, gz + clear_h + panel_h / 2.0),
               (panel_t, abs(y1 - y0), panel_h), panel_mtl)
    return dict(post=2, panel=1, clear_h=clear_h)


def build_chevron_band(stage, prefix, x, y, z, mtl_y=None, mtl_k=None,
                       width=0.60, height=0.90, n=6, stripe_t=0.006,
                       yaw=0.0, stage_mtl_prefix=None):
    """G13: the **yellow/black diagonal chevron band** on a wall end.

    Colour is the statutory pair `[law - 산업안전보건법 별표8]`: 5Y 8.5/12 yellow with
    black. Stripes run at 45 deg; `n` alternating bands across `width`. Modelled as thin
    proud boxes rather than a texture so the band survives at grazing angles, which is
    where a painted decal disappears.
    """
    pfx = stage_mtl_prefix or prefix
    my = mtl_y or _mtl(stage, pfx + "/ChevYellow", SAFETY_YELLOW, rough=0.55)
    mk = mtl_k or _mtl(stage, pfx + "/ChevBlack", SAFETY_BLACK, rough=0.55)
    _root(stage, prefix, x, y, z, yaw)
    made = dict(stripe=0)
    for i in range(int(n)):
        sy = -width / 2.0 + width * (i + 0.5) / n
        sc.add_box(stage, f"{prefix}/Stripe_{i}", (0.0, sy, 0.0),
                   (stripe_t, width / n, height * 1.35),
                   my if i % 2 == 0 else mk)
        made["stripe"] += 1
    return made


def build_trench_grating(stage, prefix, cx, cy, gz, frame_mtl, bar_mtl,
                         length=6.0, width=0.30, bar_t=0.005, bar_pitch=0.030,
                         frame_t=0.040, recess=0.010, yaw=0.0):
    """G13: the **linear trench grating across a ramp mouth**.

    A ramp mouth always carries one: it is the interception line that stops surface water
    entering the basement. Form `[practice]`: an angle frame cast into the slab, the
    grating **recessed 10 mm** below the finished surface (so a wheel does not strike the
    frame), and cross bars at a **30 mm pitch** - the pitch is what makes it a grating and
    not a painted rectangle, and it is also what a pedestrian heel notices.
    """
    _root(stage, prefix, cx, cy, gz, yaw)
    made = dict(frame=2, bar=0)
    for s, tag in ((1, "P"), (-1, "N")):
        sc.add_box(stage, f"{prefix}/Frame_{tag}",
                   (0.0, s * (width / 2.0 + frame_t / 2.0), -recess / 2.0),
                   (length, frame_t, recess + 0.05), frame_mtl, collider=True)
    n = max(2, int(length / bar_pitch))
    for i in range(n):
        bx = -length / 2.0 + length * (i + 0.5) / n
        sc.add_box(stage, f"{prefix}/Bar_{i}", (bx, 0.0, -recess - 0.012),
                   (bar_t, width, 0.024), bar_mtl)
        made["bar"] += 1
    return made


# ===========================================================================
# 14. G4 · rope-on-timber-post handline  (lifted from scene04)
# ===========================================================================

def rope_span_points(a, b, sag=0.10, seg=6):
    """Catenary-ish span from tie `a` to tie `b`, approximated by `seg` chords.

    A parabola is used rather than a true catenary: over a 1.2-2.0 m span the two differ
    by well under a millimetre, and the parabola has no numerical edge cases.
    """
    pts = []
    for i in range(int(seg) + 1):
        t = i / float(seg)
        x = a[0] + (b[0] - a[0]) * t
        y = a[1] + (b[1] - a[1]) * t
        z = a[2] + (b[2] - a[2]) * t - sag * 4.0 * t * (1.0 - t)
        pts.append((x, y, z))
    return pts


def build_rope_handline(stage, prefix, line, ground_fn, post_mtl, rope_mtl,
                        offset=1.35, pitch_max=2.0, post_h=1.00, post_r=0.060,
                        post_embed=0.30, rope_r=0.009, tie_drop=0.08, sag=0.10,
                        seg=6, sides=(1.0, -1.0), seed=40451):
    """G4: round timber posts + a catenary rope - **DRESSING, NOT A GUARD** (ruling R04-1).

    Lifted verbatim in behaviour from `scene04_parktrail.py`, which wrote it lift-ready
    and keeps its own local copy; migrating that scene is optional and is **not** owed by
    this commit. The only scene coupling was the centreline and the ground function, so
    the lift is a signature change and no logic change:
        `line`      : [(x, y), ...] walk centreline, already resolved to values
        `ground_fn` : x -> ground z

    **Why it is not a guard**, in construction rather than in prose:
      * no rigid rail, no infill, no toe board - one O18 mm rope per span;
      * it stands `offset` outboard of the walking corridor, so it neither narrows the
        walking band nor stands between the walker and the drop;
      * nothing crosses the drop edge.
    A scene using it must **build it in both hazard arms**, so its presence carries zero
    bits about the negative-obstacle label. That is the property R04-1 needs; assert it in
    the scene's registry print, as scene04 does.

    Dimensions from the reference image `[measured - G4]`: round posts O~0.12 m about
    1.0 m tall at about 1.2 m pitch, white/cream rope in visible catenary sag.
    """
    import random as _random
    if len(line) < 2:
        return dict(post=0, span=0)
    # arc-length parameterisation of the centreline
    acc = [0.0]
    for a, b in zip(line, line[1:]):
        acc.append(acc[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    total = acc[-1]

    def at(s):
        for i in range(len(acc) - 1):
            if s <= acc[i + 1] or i == len(acc) - 2:
                L = acc[i + 1] - acc[i] or 1e-9
                t = (s - acc[i]) / L
                a, b = line[i], line[i + 1]
                d = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
                return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), d
        return line[-1], (1.0, 0.0)

    n_span = max(1, int(math.ceil(total / pitch_max)))
    ties, n_post = {}, 0
    for k in range(n_span + 1):
        (cx, cy), (dx, dy) = at(total * k / n_span)
        nx, ny = -dy, dx
        for side in sides:
            tag = "P" if side > 0 else "N"
            px, py = cx + side * offset * nx, cy + side * offset * ny
            gz = float(ground_fn(px))
            rnd = _random.Random(seed + k * 31 + (0 if side > 0 else 7))
            h = post_h * (1.0 + rnd.uniform(-0.04, 0.04))
            tot = h + post_embed
            sc.add_cylinder(stage, f"{prefix}/RopePost_{tag}_{k}",
                            (px, py, gz + h - tot / 2.0), post_r, tot,
                            post_mtl, collider=True)
            ties[(tag, k)] = (px, py, gz + h - tie_drop)
            n_post += 1
    n_seg = 0
    for side in sides:
        tag = "P" if side > 0 else "N"
        for k in range(n_span):
            pts = rope_span_points(ties[(tag, k)], ties[(tag, k + 1)], sag, seg)
            for j, (a, b) in enumerate(zip(pts, pts[1:])):
                d = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
                L = math.sqrt(sum(v * v for v in d)) or 1e-6
                ux, uy, uz = d[0] / L, d[1] / L, d[2] / L
                # `add_cylinder` authors [translate, rotateY, rotateX]; under the USD
                # row-vector convention points apply in reverse (rotX -> rotY ->
                # translate), so a local +Z maps to (cos a sin b, -sin a, cos a cos b).
                ax = math.degrees(math.asin(max(-1.0, min(1.0, -uy))))
                by = math.degrees(math.atan2(ux, uz))
                sc.add_cylinder(stage, f"{prefix}/RopeSpan_{tag}_{k}_{j}",
                                ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0,
                                 (a[2] + b[2]) / 2.0),
                                rope_r, L, rope_mtl, rotY=by, rotX=ax)
                n_seg += 1
    return dict(post=n_post, span=n_seg, pitch=total / n_span)


# ===========================================================================
# 15. Self-check
# ===========================================================================

def _selfcheck():
    """Assemble every template on a stub stage and assert its counts and statutes.

    `props_kit` has **no consumer yet** - that is deliberate, it is what makes landing it
    a zero-geometry commit - so the 33-scene invariance check cannot exercise a single
    line of it. This is the substitute evidence: every builder is called, its prim
    inventory is counted, and the numbers the docstrings claim are asserted rather than
    described. Run it with `python3 props_kit.py`.
    """
    fails, checks = [], 0

    def ck(cond, msg):
        nonlocal checks
        checks += 1
        if not cond:
            fails.append(msg)

    class _P:                      # minimal recording stub, same shape as the R-4 harness
        def __init__(self):
            self.prims = []

    rec = _P()

    def _box(stage, path, center, size, mtl=None, collider=False):
        rec.prims.append(path)

    def _cyl(stage, path, center, radius, height, mtl=None, rotY=0.0, rotX=0.0,
             collider=False):
        rec.prims.append(path)

    def _sph(stage, path, center, scale3, mtl=None):
        rec.prims.append(path)

    def _pbr(stage, path, **kw):
        return path

    class _Xf:
        @staticmethod
        def AddTranslateOp():
            return _Op()

        @staticmethod
        def AddRotateZOp():
            return _Op()

    class _Op:
        @staticmethod
        def Set(v):
            return None

    class _Geom:
        class Xform:
            @staticmethod
            def Define(stage, path):
                rec.prims.append(path)
                return _Xf()

        @staticmethod
        def Xformable(p):
            return _Xf()

    class _Gf:
        @staticmethod
        def Vec3d(*a):
            return a

    real = (sc.add_box, sc.add_cylinder, sc.add_sphere, sc.make_pbr)
    sc.add_box, sc.add_cylinder, sc.add_sphere, sc.make_pbr = _box, _cyl, _sph, _pbr
    mod = sys.modules[__name__]
    real_root = mod._root

    def _root_stub(stage, prefix, cx, cy, base_z, yaw=0.0):
        rec.prims.append(prefix)
        return prefix
    mod._root = _root_stub
    try:
        st = None
        r = build_bench_slat(st, "/B", 0, 0, 0, "m")
        ck(r["slat"] == 5 and r["leg"] == 4 and r["frame"] == 2,
           "C1 bench: 5 slats on 2 end frames")
        ck(abs((5 * 0.045 + 4 * 0.012) - 0.273) < 1e-9,
           "C1 slat span arithmetic")
        r = build_bench_bucket(st, "/Bb", 0, 0, 0, "m", "f")
        ck(r["gang"] == 4 and r["bracket"] == 2 and r["leg"] == 0,
           "C1b: 4 gangs, wall-fixed")
        r = build_binsort(st, "/Bs", 0, 0, 0, "b", "l")
        ck(r["gang"] == 2 and r["ring"] == 2 and r["label"] == 2 and r["lid"] == 1,
           "C3: 2 gangs with rings and labels")
        r = build_canopy_rafter(st, "/C", 0, 0, 0, "r", "p")
        ck(r["post"] == 4 and r["rafter"] >= 7 and r["fascia"] == 1,
           "C4: rafters + fascia present")
        ck(0.30 <= (2.6 / (r["rafter"] - 1)) <= 0.45,
           "C4: rafter pitch inside 300-450 mm")
        r = build_planter_kerb(st, "/P", 0, 0, 0, "k", "s")
        ck(r["kerb"] == 12 and r["soil"] == 1, "C5: 3 kerb units per side")
        r = build_bollard_v2(st, "/Bo", 0, 0, 0, "b", "band")
        ck(r["dome"] == 1 and r["plate"] == 1 and r["band"] == 1, "C6: cap+plate+band")
        ck(BOLLARD_H_MIN <= r["height"] <= BOLLARD_H_MAX,
           "C6: default height inside the statutory 0.80-1.00 m")
        r2 = build_bollard_v2(st, "/Bo2", 0, 0, 0, "b", "band", compliant=False, seed=1)
        ck(r2["height"] < BOLLARD_H_MIN, "C6: non-compliant arm is below the minimum")
        r = build_sign_2post(st, "/S", 0, 0, 0, "p", "o")
        ck(r["post"] == 2 and 2.5 <= r["panel_bottom"] <= 3.0,
           "C7c: two posts, bottom 2.5-3.0 m")
        ck(build_sign_2post(st, "/S2", 0, 0, 0, "p", "o", panel_w=0.5)["post"] == 1,
           "C7c: a <=0.6 m panel may keep one post")
        r = build_base_plate(st, "/R1", 0, 0, 0, "p", "b")
        ck(r["anchor"] == 4 and r["nut"] == 4 and r["ring"] == 1 and r["bedding"] == 1,
           "RF-1: 4 anchors, nuts, bedding, dust ring")
        ck(0.008 in PLATE_STOCK_T and 0.005 <= 0.010 <= 0.015,
           "RF-1: 8T stock plate, bedding inside 5-15 mm")
        ck(len(METAL_AGE) == 3 and METAL_AGE["sts304_10s"][1] < METAL_AGE["galv_90s"][1]
           < METAL_AGE["painted_80s"][1],
           "RF-2: three rungs, roughness ordered new->old")
        ck(build_newel_ball(st, "/R3", 0, 0, 1.0, "m")["ball"] == 1, "RF-3: newel ball")
        ck(build_gooseneck_return(st, "/R3g", 0, 0, 1.0, "m")["neck"] == 6,
           "RF-3: goose-neck return")
        ck(build_beaded_baluster(st, "/R3b", 0, 0, 0, 1.0, "m")["bead"] == 2,
           "RF-3: beaded rings")
        r = build_hoop_row(st, "/R3h", 0, -1, 1, 0, "m")
        ck(r["hoop"] == 4 and r["leg"] == 8 and r["arc"] == 20, "RF-3: hoop row")
        steps = [(0.0, 0.30, 0.0), (0.30, 0.60, -0.17)]
        r = build_nosing_tier(st, "/R5", steps, -1, 1)
        ck(r["strip"] == 2 and r["screw"] > 0, "RF-5: strip + screw row")
        ck(build_nosing_tier(st, "/R5p", steps, -1, 1, tier="paint_only")["screw"] == 0,
           "RF-5: paint tier has no screws")
        ck(SAFETY_YELLOW == (0.941, 0.745, 0.000), "RF-5: 5Y 8.5/12 = #F0BE00")
        ck(set(NOSING_BY_SCENE) == {"retrofit_strip", "cast_groove", "absent"},
           "RF-5: three era classes")
        r = build_tube_railing(st, "/G6", [(0, 0), (6, 0)], lambda x, y: 0.0, "m")
        ck(r["rail"] == 4 and r["post"] >= 4, "G6: 4 tube rails")
        ck(abs(r["clear_max"] - ((1.10 - 0.12) / 3 - 0.048)) < 1e-9,
           "G6: declared clear span 0.279 m, deliberately not a baluster guard")
        r = build_glass_balustrade(st, "/G8", [(0, 0), (6, 0)], lambda x, y: 0.0,
                                   "g", "c", "s")
        ck(r["panel"] == 4 and r["cap"] == 1 and r["shoe"] == 1,
           "G8: 1.5 m panel bays with cap and shoe")
        ck(build_gantry_sign(st, "/G13g", 0, -3, 3, 0, 2.2, "p", "n")["post"] == 2,
           "G13: gantry on two posts")
        ck(build_chevron_band(st, "/G13c", 0, 0, 1)["stripe"] == 6, "G13: chevron band")
        r = build_trench_grating(st, "/G13t", 0, 0, 0, "f", "b")
        ck(r["bar"] == 200 and r["frame"] == 2, "G13: 30 mm bar pitch over 6 m")
        r = build_rope_handline(st, "/G4", [(0, 0), (6, 0)], lambda x: 0.0, "p", "r")
        ck(r["post"] == 8 and r["span"] == 36, "G4: 4 bays x 2 sides, 6 chords per span")
        ck(r["pitch"] <= 2.0, "G4: post pitch within pitch_max")
        pts = rope_span_points((0, 0, 1), (2, 0, 1), sag=0.10, seg=6)
        ck(abs(min(p[2] for p in pts) - 0.90) < 1e-9, "G4: mid-span sag = 0.10 m")
    finally:
        sc.add_box, sc.add_cylinder, sc.add_sphere, sc.make_pbr = real
        mod._root = real_root

    print(f"[props_kit] self-check {checks - len(fails)}/{checks}"
          f"  · prims built {len(rec.prims)}")
    for m in fails:
        print("  [FAIL]", m)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(_selfcheck())
