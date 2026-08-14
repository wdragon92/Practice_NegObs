# -*- coding: utf-8 -*-
"""facade_kit - procedural kit for the **lower storeys (0-5 m)** of Korean city buildings.

Source documents
----------------
* `Docs/surveys/korean_urban_backdrop.md` (2026-07-28) - priorities 1-8,
  §3.3 lower storeys, §3.4 envelope attachments, §6.1 quick-reference parameter
  table, §5 per-scene-type composition table
* `Docs/surveys/_dimension_index.md` - index of confirmed measured dimensions

Why this module exists (measured facts - survey §1.1/§1.3)
---------------------------------------------------------
The 33 scenes hold **4,050 window prims**. The primary evaluation viewpoint is
camera h0.3 m, pitch -10 deg, vFOV 36 deg, so the top of the frame is only
**+8.0 deg** above the horizon. The highest point entering the frame at distance d
is `z = 0.3 + d*tan(8 deg) ~= 0.3 + 0.14*d`:

    d=10 m -> 1.7 m, d=20 m -> 3.1 m, d=34 m -> 5.1 m, d=90 m -> 12.9 m

-> **About 88 % of windows are off-frame** (19 % of all prims are spent where they
cannot be seen). Meanwhile the 0-5 m band that actually fills the image holds
nothing but one face of a shell box. This module moves that budget downwards.

Design conventions
------------------
1. **Z-up coordinate system, metres.**
2. **Do not import scene_common** (avoids a circular import). Primitive helpers are
   **injected** through the `Kit` container. Only `pxr` is imported lazily inside
   functions.
3. **RNG 100 % deterministic** - the builtin `hash()` is banned (PYTHONHASHSEED makes
   it vary per process; this actually broke once in this project). Use
   `zlib.crc32` + `random.Random`.
4. **Scale anchors are inviolable** - door height 2.10, AC outdoor unit
   0.80x0.55x0.30, guardrail 1.20, stair riser 0.15-0.18 and fire triangle 0.20 are
   cues **by their physical magnitude itself**. Never randomise them. Where
   per-instance variation is needed, use `_jit()` and stay **within +-8 %**.
   (A past incident smeared a riser into uniform(1.45,1.85) and erased the cue.)
5. All new geometry must be called **only inside the `LOOK_GEO` gate at the call
   site** (preserving the A/B control arm). The functions here know nothing about the
   gate - and do not need to.
6. Unsourced numbers get `[estimate]`/`[knowledge]`/`[no source]` in the docstring
   plus a reason.

Prim budget (per building) - must stay below the 2,500-3,000 saved by the window cap
------------------------------------------------------------------------------------
| function                  | prims per building        | typical (facade 20 m, 5 fl) |
|---------------------------|---------------------------|-----------------------------|
| `build_plinth`            | **1**                     | 1                           |
| `build_shopfront`         | 2*bays + 3-5              | bays=4 -> 11                |
| `build_aircon_units`      | 3/unit (1 without bracket/pipe) | 4 units -> 12         |
| `build_signage`           | 1 + n_proj                | n_proj=2 -> 3               |
| `build_balcony_stack`     | 2 x bays x floors         | 2 bays x 3 fl -> 12         |
| `build_downpipe_run`      | 2*n_pipes + gas(2 to 2+2F)| n=2, gas A -> 6             |
| `build_fire_access_marks` | 1/floor/station (thin quad) | 3                         |
| **total (shop type)**     | -                         | **about 36**                |
| **total (apartment type)**| -                         | **about 22**                |

The library holds about 60 urban backdrop buildings, so applying this everywhere costs
**36 x 60 ~= 2,160 prims < the 2,500-3,000 saved by the window cap**. Net prims drop.
"""

import math
import random
import zlib

__all__ = [
    "Kit", "Facade", "facade_from_bd", "WALL_PROUD",
    "frame_ceiling", "lod_tier", "floor_levels", "window_rows_visible",
    "build_plinth", "build_shopfront", "build_aircon_units", "build_signage",
    "build_balcony_stack", "build_downpipe_run", "build_fire_access_marks",
]

# ===========================================================================
# [0] Scale anchor constants - **do not randomise**
# ===========================================================================
# The grade tag next to each value follows survey §6.1.
#   statutory = clause verified, confirmed = standard/catalogue measurement, [estimate], [knowledge]
DOOR_H = 2.10            # statutory: Evac/fire structure rules §16, ceiling height 2.1 (same as the existing convention)
RAIL_H = 1.20            # statutory: Building Act Enforcement Decree §40 - balcony/roof guardrail >=1.2
BALUSTER_GAP = 0.10      # statutory: Procedures and Standards for Balcony Structural Alteration, <=0.10
BALCONY_DEPTH = 1.50     # statutory: Building Act Enforcement Decree §119(1)3(b) - balcony deduction 1.5 m
SLAB_T = 0.21            # statutory: Housing Construction Standards §14-2(1) - slab >=210 mm
AC_W, AC_H, AC_D = 0.80, 0.55, 0.30   # [estimate] Samsung AR08HVAD1WK 0.720x0.548x0.265 +
                                      # LG SQ06EZAU 0.660x0.459x0.276, taken as an enclosing value
AC_WALL_GAP = 0.10       # confirmed: manufacturer installation clearance (rear 0.10-0.15)
FIRE_TRI_D = 0.20        # statutory: Evac/fire structure rules §18-2 - red inverted triangle, diameter >=0.20
FIRE_SILL_MAX = 0.80     # statutory: entry window sill height within 0.80 of the floor
FIRE_SPACING = 40.0      # statutory: one extra station every 40 m of horizontal wall distance
GRANITE_T = 0.030        # confirmed: standard building specification, stonework - dry-set granite 30 mm
SIGN_BAND_PROUD = 0.30   # statutory: wall-mounted sign projection <=0.30 (Seoul)
SIGN_PROJ_OUT = 1.00     # statutory: projecting sign projection <=1.00 (Seoul; 1.2 with review)
SIGN_PROJ_T = 0.30       # statutory: projecting sign thickness <=0.30 (Seoul)
SIGN_PROJ_BOTTOM = 3.00  # statutory: ground to underside >=3.0 (4.0 where there is no sidewalk)
STAIR_RISER = 0.16       # statutory range: rules §15 riser 0.15-0.18 (<=0.15 exempts the mid rail)
STAIR_TREAD = 0.32       # statutory: rules §15 tread >=0.30
WALL_PROUD = 0.005       # convention: **inner** face of a facade-plane attachment sits
                         # 5 mm outside the wall it is mounted on. Identical to
                         # `scene_common.build_building`'s `WIN_EPS` (scene_common.py:2644),
                         # which settled on the same figure for the same reason: the shell
                         # is a **solid** box, so any recess buries the glass. Without
                         # reveal geometry the deepest expressible recess is zero, and a
                         # coplanar face z-fights. See `build_shopfront(wall_out=...)`.
GAS_BAND_W = 0.030       # statutory: KGS FU551 2.5.7.2 - yellow band width 30 mm
GAS_BAND_Z = 1.00        # statutory: +1 m above each floor level
GAS_VALVE_Z = (1.60, 2.00)   # confirmed: LH city gas specification - riser main valve at floor +1.6-2.0
DOWNPIPE_DN100 = 0.114   # confirmed: KDS 31 30 35 DN100 -> outer diameter about 0.114
CAM_H = 0.30             # Primary evaluation viewpoint (grid_views)
CAM_PITCH = -10.0
CAM_VFOV = 36.0          # fixlog_W4 §155, W5 §66 - back-computed from the v6 render

# Colours (reference only - materials are made by the caller)
GAS_YELLOW = (0.86, 0.72, 0.10)   # statutory: KGS FU551, above-ground piping is yellow
FIRE_RED = (0.72, 0.09, 0.08)     # statutory: red inverted triangle of the fire entry window


# ===========================================================================
# [1] Deterministic RNG - hash() banned
# ===========================================================================
def _rng(*keys):
    """Deterministic `random.Random`. The builtin `hash()` varies per process via
    PYTHONHASHSEED and is therefore **never used** (a bug that actually hit this
    project). crc32 uses a fixed standard-library polynomial, so it is identical
    across runs and platforms."""
    s = "|".join(str(k) for k in keys)
    return random.Random(zlib.crc32(s.encode("utf-8")) & 0xFFFFFFFF)


def _jit(rng, v, frac=0.08):
    """Per-instance jitter. **Hard cap of +-8 %** so scale anchors are not smeared.
    A frac above 0.08 is clipped to 0.08 (preventing a repeat of the incident)."""
    f = min(abs(float(frac)), 0.08)
    return float(v) * (1.0 + rng.uniform(-f, f))


# ===========================================================================
# [2] Helper injection container, facade coordinate system
# ===========================================================================
class Kit:
    """Injection container for scene_common primitive helpers (avoids a circular import).

    Usage (inside scene_common.build_building)::

        import facade_kit as fk
        K = fk.Kit(add_box, add_cylinder, _oriented_box)

    The signatures expected are exactly the current scene_common ones::

        add_box(stage, path, center, size, mtl=None, collider=False)
        add_cylinder(stage, path, center, radius, height, mtl=None,
                     rotY=0.0, rotX=0.0, collider=False)
        oriented_box(stage, path, center, size, mtl=None, collider=False,
                     rotz=0.0, rotx=0.0)        # optional - falls back to add_box
    """

    def __init__(self, add_box, add_cylinder=None, oriented_box=None):
        if not callable(add_box):
            raise TypeError("Kit: add_box 는 호출 가능해야 한다")
        self.add_box = add_box
        self.add_cylinder = add_cylinder
        self.oriented_box = oriented_box

    def box(self, stage, path, center, size, mtl=None, collider=False):
        return self.add_box(stage, path, center, size, mtl, collider)

    def cyl(self, stage, path, center, radius, height, mtl=None, **kw):
        """Fall back to a box of the same volume when add_cylinder is not injected (same prim count)."""
        if self.add_cylinder is None:
            d = 2.0 * float(radius)
            return self.add_box(stage, path, center, (d, d, float(height)), mtl)
        return self.add_cylinder(stage, path, center, radius, height, mtl, **kw)


class Facade:
    """Local coordinate system of one facade. The adapter that lets every builder work
    regardless of axis.

      axis_y=True  -> the wall is the plane y = `plane`, horizontal (u) is **world X**
      axis_y=False -> the wall is the plane x = `plane`, horizontal (u) is **world Y**
      fdir (+1/-1) : direction pointing out of the wall (world axis sign). Taken
                     straight from bd["face_dir"].
      u0,u1        : horizontal range (world). base_z : building plinth world z.

    `out` means the **distance outward from the wall face (always positive)**. Facade
    absorbs the fdir sign, so callers and builders never deal with signs.
    """

    def __init__(self, plane, fdir, u0, u1, base_z=0.0, axis_y=True,
                 depth_ref=None):
        self.plane = float(plane)
        self.fdir = 1.0 if float(fdir) >= 0 else -1.0
        self.u0 = float(min(u0, u1))
        self.u1 = float(max(u0, u1))
        self.base_z = float(base_z)
        self.axis_y = bool(axis_y)
        # depth_ref: building depth perpendicular to the facade (optional, for plinth wrap)
        self.depth_ref = depth_ref

    # -- Geometric transforms -------------------------------------------
    @property
    def width(self):
        return self.u1 - self.u0

    @property
    def mid(self):
        return 0.5 * (self.u0 + self.u1)

    def world(self, u, out, z):
        """(horizontal u, outward distance out, height z) -> world (x, y, z)."""
        p = self.plane + self.fdir * float(out)
        if self.axis_y:
            return (float(u), p, float(z))
        return (p, float(u), float(z))

    def size(self, w_u, d_out, h):
        """(horizontal width, thickness along the wall normal, height) -> world size 3-tuple."""
        if self.axis_y:
            return (float(w_u), float(d_out), float(h))
        return (float(d_out), float(w_u), float(h))

    def tangent(self):
        """World unit vector (x, y) along the horizontal (u) direction."""
        return (1.0, 0.0) if self.axis_y else (0.0, 1.0)

    def normal(self):
        """World unit vector (x, y) pointing out of the wall."""
        return (0.0, self.fdir) if self.axis_y else (self.fdir, 0.0)


def facade_from_bd(bd):
    """Build a Facade from the existing `bd` dictionary of `build_building`.
    The key adapter for integrating without editing scene files - it only reads
    keys that already exist."""
    axis_y = bd.get("axis", "y") == "y"
    base = float(bd.get("base_z", 0.0))
    if axis_y:
        return Facade(bd["facade_y"], bd["face_dir"], bd["x0"], bd["x1"],
                      base, True, depth_ref=abs(bd["y1"] - bd["y0"]))
    return Facade(bd["facade_x"], bd["face_dir"], bd["y0"], bd["y1"],
                  base, False, depth_ref=abs(bd["x1"] - bd["x0"]))


# ===========================================================================
# [3] Visibility ceiling of the evaluation camera - the basis of the window prim budget
# ===========================================================================
def frame_ceiling(dist_m, cam_h=CAM_H, cam_pitch_deg=CAM_PITCH,
                  vfov_deg=CAM_VFOV):
    """World z [m] reached by the **top edge** of the evaluation camera frame at
    distance dist_m.

    Frame-top elevation angle = pitch + vFOV/2 = (-10 deg) + 18 deg = **+8.0 deg above
    the horizon**
      -> `z = cam_h + dist*tan(8 deg) ~= cam_h + 0.1405*dist`
    Check (matches the survey §1.3 table): d=10->1.71, 20->3.11, 34->5.08, 50->7.32,
    90->12.94

    Sources: `Docs/audit_v4/fixlog_W4.md` §155, `fixlog_W5.md` §66 (vFOV 36 deg
          back-computed from the v6 render),
          `grid_views(heights=(0.3,0.9,1.8), pitch=-10)`.
    0 prims.
    """
    up_deg = float(cam_pitch_deg) + float(vfov_deg) / 2.0
    return float(cam_h) + float(dist_m) * math.tan(math.radians(up_deg))


def lod_tier(dist_m):
    """Band name from the survey §6 LOD table. "near"(<20) / "mid"(20-40) / "far"(40-80)
    / "silhouette"(>80). 0 prims."""
    d = float(dist_m)
    if d < 20.0:
        return "near"
    if d < 40.0:
        return "mid"
    if d <= 80.0:
        return "far"
    return "silhouette"


def floor_levels(n_floors, floor_h=2.80, ground_h=None, base_z=0.0):
    """List of **floor z levels** (length n_floors+1; the last element is the top-floor
    ceiling / roof).

    A required rule from survey §3.1 - the current equal spacing `fstep = h / floors`
    is to be retired (equal spacing on every floor is a major reason the result now
    "reads as CG")::

        z[0] = base_z
        z[1] = base_z + ground_h        # only the ground floor differs
        z[i] = z[1] + (i-1)*floor_h

    Default rationale: apartment typical floor height **2.80-2.85** (confirmed -
    Korea PM); neighbourhood-facility ground floor 3.9-4.2 and 3.3 above are
    **[estimate]** (no primary source obtained).
    With ground_h=None the ground floor matches the typical floor (= current
    behaviour preserved).
    0 prims.
    """
    n = max(1, int(n_floors))
    fh = float(floor_h)
    gh = fh if ground_h is None else float(ground_h)
    z = [float(base_z), float(base_z) + gh]
    for _ in range(n - 1):
        z.append(z[-1] + fh)
    return z[:n + 1]


def window_rows_visible(dist_m, floor_h, n_floors, ground_h=None, base_z=0.0,
                        cam_h=CAM_H, cam_pitch_deg=CAM_PITCH,
                        vfov_deg=CAM_VFOV, sill_up=0.90, margin_m=1.0,
                        near_dist=40.0, min_rows=1, cam_ground_z=0.0):
    """Number of floors that will **actually get windows** in that building (an upper
    bound). At least one floor is guaranteed.

    The prim budget reallocation rule of survey §4::

        if distance > 40 m : windows only on floors with z_sill <= (cam_h + d*tan 8)
        else               : all floors + lower-storey detail

    - `sill_up` : floor level to window sill (default 0.90 - typical sill height
      [estimate]; the fire entry window sill is statutorily within 0.80, so this sits
      slightly above it).
    - `margin_m`: headroom at the top of the frame. A safety margin that stops the
      cutoff floor from appearing sliced at the frame edge [estimate - visual safety
      margin, no figure in the source documents].
    - `cam_ground_z`: world z of the ground the camera stands on (specify only when it
      differs from the building base_z).

    Returns: an int with 1 <= rows <= n_floors. 0 prims.

    Measured savings (AST parse of `buildings`/`far_buildings` across 33 scenes,
    distance approximated by |facade plane|. Current window total 4,173 - within
    parsing difference of the 4,050 in survey §1.1)::

        near_dist=40, min_rows=1  (survey §4 literally)   -> 3,075  (-1,098)
        near_dist=20, min_rows=2  (recommended compromise)-> 2,000  (-2,173)
        near_dist=0,  min_rows=2  (pure physics)          -> 1,830  (-2,343)

    **The recommendation is near_dist=20, min_rows=2.** It approaches the 2,500-3,000
    saving the survey predicted while keeping every floor on buildings within 20 m as
    a safety margin for close viewpoints. min_rows=2 guarantees at least two rows so
    the lower-storey detail is never attached to a "windowless wall".
    """
    n = max(1, int(n_floors))
    if float(dist_m) <= float(near_dist):
        return n
    ceil_z = frame_ceiling(dist_m, cam_h, cam_pitch_deg, vfov_deg) \
        + float(cam_ground_z) + float(margin_m)
    lv = floor_levels(n, floor_h, ground_h, base_z)
    rows = 0
    for f in range(n):
        if lv[f] + float(sill_up) <= ceil_z:
            rows += 1
        else:
            break
    return max(int(min_rows), min(rows, n))


# ===========================================================================
# [4] Priority 1 - granite plinth band
# ===========================================================================
def build_plinth(K, stage, prefix, x0, x1, y0, y1, base_z, mtl,
                 height=1.10, proud=0.025, wrap=True, fac=None,
                 door_gap=None):
    """Plinth stone band (ground level to about 1.2 m). **1 prim per building.**

    Survey priority **1** - it fills the bottom of the h0.3 frame directly, yet today
    there is only a single shell texture there. The best effect-per-prim in the whole
    library.

    Dimension basis
      - stone panel thickness **0.030** (confirmed - standard building specification,
        stonework / Korea Passive Building Association "external granite thickness".
        Wall minimum is 0.020, but 0.030 with dry fixing)
      - protrusion beyond the facade plane 0.02-0.03 `[knowledge]` -> default
        `proud=0.025`
      - **the band height is `[no source]`** - a design choice with no statutory rule.
        Of the two patterns the survey lists, the below-sill type **0.9-1.2 m** is the
        default `[estimate]`. Pass `height` for the full-ground-floor type (3.0-3.6).
      - the top drip groove has a source but no dimension `[no source]` ->
        **not implemented** (about 0.01 wide, sub-pixel at evaluation distance).

    wrap=True: one box wrapping the whole building footprint (all 4 faces, 1 prim).
    wrap=False: only the single facade given by `fac` (1 prim). It always sits `proud`
    outward to avoid z-fighting with the shell.

    Material: flamed granite (dark grey). The existing `granite_dark` texture can be
    reused. A material path containing "granite"/"stone" makes the look layer classify
    it in the stone role (scene_common `_LOOK_RULES`).
    """
    h = max(0.05, float(height))
    p = float(proud)
    zc = float(base_z) + h / 2.0
    if wrap or fac is None:
        cx = 0.5 * (float(x0) + float(x1))
        cy = 0.5 * (float(y0) + float(y1))
        sx = abs(float(x1) - float(x0)) + 2.0 * p
        sy = abs(float(y1) - float(y0)) + 2.0 * p
        if door_gap is None:
            return [K.box(stage, f"{prefix}/PlinthStone", (cx, cy, zc),
                          (sx, sy, h), mtl)]
        # [GT-115 ⑧] The single wrap box crossed every entrance door and cut it
        # in half at 1.10 m (audit N1~N4: "기단 띠가 출입문을 두 동강"). With a
        # `door_gap=(axis, plane, center, width)` the wrap becomes 5 perimeter
        # bands whose OUTER faces sit exactly where the wrap box's faces were, and
        # the band on the door facade is split around the opening — so the door
        # glass (facade +0.020) now reads through granite jambs (+0.025 proud).
        # `door_gap=None` (all other callers) stays 1 box, byte-identical.
        ax, plane, ctr, gw = door_gap
        tb = 0.15                       # visual shell depth [derived — face-only]
        lo_x, hi_x = float(x0) - p, float(x1) + p
        lo_y, hi_y = float(y0) - p, float(y1) + p
        g0, g1 = float(ctr) - float(gw) / 2.0, float(ctr) + float(gw) / 2.0
        out = []

        def band(tag, bx0, bx1, by0, by1):
            if bx1 - bx0 > 1e-4 and by1 - by0 > 1e-4:
                out.append(K.box(stage, f"{prefix}/PlinthStone_{tag}",
                                 ((bx0 + bx1) / 2.0, (by0 + by1) / 2.0, zc),
                                 (bx1 - bx0, by1 - by0, h), mtl))
        if ax == "y":
            door_lo = abs(float(plane) - float(y0)) <= \
                abs(float(plane) - float(y1))
            fy = (lo_y, lo_y + tb) if door_lo else (hi_y - tb, hi_y)
            oy = (hi_y - tb, hi_y) if door_lo else (lo_y, lo_y + tb)
            band("F0", lo_x, max(lo_x, g0), fy[0], fy[1])
            band("F1", min(hi_x, g1), hi_x, fy[0], fy[1])
            band("B", lo_x, hi_x, oy[0], oy[1])
            band("W", lo_x, lo_x + tb, min(fy[1], oy[1]), max(fy[0], oy[0]))
            band("E", hi_x - tb, hi_x, min(fy[1], oy[1]), max(fy[0], oy[0]))
        else:
            door_lo = abs(float(plane) - float(x0)) <= \
                abs(float(plane) - float(x1))
            fx = (lo_x, lo_x + tb) if door_lo else (hi_x - tb, hi_x)
            ox = (hi_x - tb, hi_x) if door_lo else (lo_x, lo_x + tb)
            band("F0", fx[0], fx[1], lo_y, max(lo_y, g0))
            band("F1", fx[0], fx[1], min(hi_y, g1), hi_y)
            band("B", ox[0], ox[1], lo_y, hi_y)
            band("S", min(fx[1], ox[1]), max(fx[0], ox[0]), lo_y, lo_y + tb)
            band("N", min(fx[1], ox[1]), max(fx[0], ox[0]), hi_y - tb, hi_y)
        return out
    c = fac.world(fac.mid, p / 2.0, zc)
    s = fac.size(fac.width + 2.0 * p, p, h)
    return [K.box(stage, f"{prefix}/PlinthStone", c, s, mtl)]


# ===========================================================================
# [5] Priority 2 - ground-floor shopfront
# ===========================================================================
def build_shopfront(K, stage, prefix, fac, mtl_glass, mtl_frame,
                    mtl_stone=None, ground_h=4.00, bay_w=5.00,
                    opening_h=2.60, kick_h=0.25, inset=0.12,
                    shutter_box=True, steps=1, door_bay=None,
                    max_bays=6, seed=0, wall_out=0.0):
    """Ground-floor shopfront: opening + kick plate + shutter box + entrance steps.
    **Prims per building = 2*bays + 3-5** (bays=4 -> 11-13; bays capped by `max_bays`).

    Survey priority **2** - the 0-3 m band is most of the h0.3 frame.

    Dimension basis
      - shop bay width 4-6 m `[knowledge]` -> default 5.0
      - glazed opening height **2.4-2.8**, kick plate 0.15-0.30 `[knowledge]`
      - door width 0.9-1.2, height **2.10** `[estimate - inferred from the >=0.9
        effective width of a rooftop refuge doorway (Building Act)]`.
        **2.10 is a scale anchor: do not randomise.**
      - entrance steps 1-2, riser **0.15-0.18**, tread **>=0.30**
        (statutory - evac/fire rules §15. riser <=0.15 plus tread >=0.30 exempts the
        mid rail)
      - a stair rail is mandatory only **above 1 m** (rules §15), so 1-2 steps
        (<=0.36) correctly have none. That also saves prims.
      - shutter box height 0.25-0.40, guide rail width 0.06-0.08 `[estimate -
        manufacturer drawings exist only inside DWG files, not obtained]` ->
        default 0.32. Guide rails would be 2 per bay and double the prim count, so
        they are **not implemented** (60 mm vanishes at evaluation distance).

    `wall_out` [B-F1] is the outward offset of the **wall surface this shopfront is
    mounted on**, measured from `fac.plane` in `Facade` `out` units. 0.0 means the
    facade plane itself. Callers that build a set-back mass (an office podium, a
    daylight step, a protruding core) pass the outward face of whichever volume
    actually covers this band, so the glazing lands on the surface that is really
    there. See `building_kit.Plan.out_at`.

    `inset` **[retained for API compatibility, currently a no-op]**. It used to push
    the glazing `inset` metres *into* the wall, but the shell is a **solid** box:
    survey R3 §5.1 measured that this buried **62 of 62** glazing prims across five
    types and four LOD tiers, so no window in the library was ever visible. Without
    reveal geometry (4 extra prims per bay, which the prim budget forbids) the
    deepest expressible recess is **zero**, and a coplanar face z-fights — the exact
    conclusion `scene_common.build_building` reached at its `WIN_EPS` block
    (`scene_common.py:2637-2645`). Glazing therefore sits `WALL_PROUD` (5 mm) proud
    of `wall_out`. The parameter is kept so the reveal decomposition can restore it
    without a signature change (a signature change is a 24-call-site edit).

    Kick plate and shutter box protrude further than the glazing so they still cast
    their shadow line onto it.
    """
    rng = _rng(prefix, "shopfront", seed)
    prims = []
    W = fac.width
    if W < 1.5:
        return prims
    wo = float(wall_out)                        # [B-F1] wall surface this sits on
    nb = max(1, min(int(max_bays), int(round(W / max(2.0, float(bay_w))))))
    bw = W / nb
    z0 = fac.base_z
    gh = float(ground_h)

    # Entrance steps (in front of the door) - built first to fix the opening base level
    ns = max(0, min(2, int(steps)))
    step_top = z0
    di = (nb // 2) if door_bay is None else max(0, min(nb - 1, int(door_bay)))
    du = fac.u0 + (di + 0.5) * bw
    dw = 1.00                                   # Door width [estimate], midpoint of 0.9-1.2
    for s in range(ns):
        # Riser varies only within the statutory range (0.15-0.18) - anchor preserved
        r = 0.15 + rng.random() * 0.03
        zt = step_top + r
        tread = STAIR_TREAD * (ns - s)          # Lower steps are deeper (nosing overlap)
        prims.append(K.box(
            stage, f"{prefix}/ShopStep_{s}",
            fac.world(du, wo + tread / 2.0, (step_top + zt) / 2.0),
            fac.size(dw + 0.80, tread, r + 0.02),
            mtl_stone if mtl_stone is not None else mtl_frame))
        step_top = zt

    kb = float(kick_h)
    op_h = float(opening_h)
    op_z0 = z0 + kb
    op_z1 = min(op_z0 + op_h, z0 + gh - 0.45)   # Reserve room for the slab and sign band
    op_h = max(1.2, op_z1 - op_z0)

    g_t, d_t = 0.04, 0.06                       # glazing / door slab thickness
    for b in range(nb):
        u = fac.u0 + (b + 0.5) * bw
        gw = max(0.6, bw - 0.40)                # Bay minus 0.40 (columns and frames)
        # Kick plate - stone/metal band. Sits further out than the glazing so its
        # shadow line still falls on the glass.
        prims.append(K.box(
            stage, f"{prefix}/ShopKick_{b}",
            fac.world(u, wo + 0.03, z0 + kb / 2.0),
            fac.size(bw, 0.06, kb),
            mtl_stone if mtl_stone is not None else mtl_frame))
        # Glazed opening - **5 mm proud of the wall surface** [B-F1]. See the
        # `inset` note in the docstring for why it is not recessed.
        prims.append(K.box(
            stage, f"{prefix}/ShopGlass_{b}",
            fac.world(u, wo + WALL_PROUD + g_t / 2.0, (op_z0 + op_z1) / 2.0),
            fac.size(gw, g_t, op_h), mtl_glass))

    # Entrance door - **height 2.10 is a scale anchor**. Not randomised.
    prims.append(K.box(
        stage, f"{prefix}/ShopDoor",
        fac.world(du, wo + WALL_PROUD + d_t / 2.0, step_top + DOOR_H / 2.0),
        fac.size(dw, d_t, DOOR_H), mtl_frame))

    # Shutter box - lintel above the opening
    if shutter_box:
        sb_h = 0.32                             # [estimate] 0.25-0.40
        prims.append(K.box(
            stage, f"{prefix}/ShutterBox",
            fac.world(fac.mid, wo + 0.09, op_z1 + sb_h / 2.0),
            fac.size(W - 0.20, 0.18, sb_h), mtl_frame))
    return prims


# ===========================================================================
# [6] Priority 3 - AC outdoor units (the strongest Korean identification cue)
# ===========================================================================
def build_aircon_units(K, stage, prefix, fac, mtl_body, mtl_bracket=None,
                       levels=None, mode="perfloor", per_level=2,
                       eaves_z=2.30, count=None, bracket=True, pipe=True,
                       max_units=14, u_margin=0.8, z_max=6.0, seed=0):
    """AC outdoor units + wall brackets + refrigerant piping. **3 prims per unit**
    (down to 1 per unit with bracket=False, pipe=False).

    Survey priority **3** - the **strongest cue** separating a "Korean building" from a
    generic Western one. The 1.5-2.6 m mounting height is **straight ahead at robot eye
    level**, so it occupies a lot of the evaluation frame. Today the whole library has
    outdoor units only on the two houses of scene15, one each.

    Dimension basis (**all scale anchors - do not randomise; variation within +-8 %**)
      - Samsung wall type AR08HVAD1WK outdoor unit **0.720 x 0.548 x 0.265**
        (source: Samsung Electronics)
      - LG stand type SQ06EZAU outdoor unit **0.660 x 0.459 x 0.276**
        (source: LG Electronics, secondary)
      - -> modelling representative **0.80 (W) x 0.55 (H) x 0.30 (D)**
        `[estimate - enclosing value of the two above]`
      - wall clearance (rear) **0.10-0.15** (same sources) -> `AC_WALL_GAP = 0.10`
      - wall bracket: high-strength aluminium angle, retail widths in the
        **800 / 900** series (source: Yuseong Mall)
      - bracket mounting height (underside) = floor level +0.2-0.6 `[estimate]`
      - density: 1-2 per dwelling; shops line up several under the ground-floor eaves
        `[knowledge]`

    mode
      "perfloor" : `per_level` units at floor level +0.35 for each level in `levels`
                   (= the `floor_levels()` result). For multiplex and apartment blocks.
      "eaves"    : one row under the ground-floor eaves (underside at `eaves_z`,
                   default 2.30). For shops `[knowledge]`.

    Note: after the 2021 amendment of Building Act Enforcement Decree §119(1)3(d),
      **new construction** tends to put outdoor units in a dedicated balcony space
      (<=1 m2). The existing multiplex and shop stock (most of our scene backdrops)
      still exposes them on the outer wall. Enabling this only on older buildings
      makes the period read correctly.
    """
    rng = _rng(prefix, "ac", seed)
    prims = []
    W = fac.width
    if W < 2.0:
        return prims

    slots = []
    if mode == "eaves":
        n = int(count) if count else max(2, int(W / 2.4))
        n = min(n, int(max_units))
        for i in range(n):
            u = fac.u0 + u_margin + (i + 0.5) * (W - 2 * u_margin) / max(1, n)
            slots.append((u, float(eaves_z)))
    else:
        lv = list(levels) if levels else [fac.base_z + 1.6]
        if len(lv) > 1:
            lv = lv[:-1]                        # The last level is the roof slab
        # **Generate only within the eye-level band (floor level <= base_z + z_max, default 6 m).**
        # Above that it is outside the evaluation frame at d<=40 m (§1.3) - wasted prims.
        # For a shop with a 4 m ground floor only floors 1-2 remain, i.e. under 12 prims per building.
        lv = [z for z in lv if z <= fac.base_z + float(z_max)] or lv[:1]
        for f, zf in enumerate(lv):
            for k in range(max(1, int(per_level))):
                if len(slots) >= int(max_units):
                    break
                u = fac.u0 + u_margin + (k + 0.5) * \
                    (W - 2 * u_margin) / max(1, int(per_level))
                # ---- KEEP `[ruled 07-30]` W3 spec §1.2 -----------------------
                # This `U(-0.35, +0.35)` u-offset survives the W3 jitter abolition
                # **on purpose**, and is listed as a KEEP so nobody "fixes" it.
                # Reason it is not decorative wobble: an outdoor unit is mounted
                # wherever the dwelling's own indoor unit and refrigerant run put
                # it, which follows the **room layout behind the wall**, not the
                # facade grid. Neighbouring flats in the same block have different
                # room layouts, so the real column of units is genuinely irregular
                # - lining them up on a ruler is what would be the fabrication.
                # This closes RT-R §4-N1 (the row C's "complete inventory" missed)
                # and it is the reason the W3 spec's abolish list is 13 rows, not
                # 14. `facade_kit.py` gas-valve z `U(*GAS_VALVE_Z)` is KEEP for the
                # same class of reason (it carries a stated real basis).
                # Determinism is unaffected: `rng` is crc32-seeded, never `hash()`.
                u += rng.uniform(-0.35, 0.35)
                slots.append((u, zf + 0.35))    # [estimate] floor level +0.2-0.6

    for i, (u, zb) in enumerate(slots):
        w = _jit(rng, AC_W)                     # Per-instance variation within +-8 % only
        hgt = _jit(rng, AC_H)
        dep = _jit(rng, AC_D)
        out_c = AC_WALL_GAP + dep / 2.0
        prims.append(K.box(
            stage, f"{prefix}/AcUnit_{i}",
            fac.world(u, out_c, zb + hgt / 2.0),
            fac.size(w, dep, hgt), mtl_body))
        if bracket:
            # Wall mounting angle - retail widths 800/900 (source: Yuseong Mall)
            prims.append(K.box(
                stage, f"{prefix}/AcBracket_{i}",
                fac.world(u, (AC_WALL_GAP + dep) / 2.0, zb - 0.03),
                fac.size(w + 0.10, AC_WALL_GAP + dep, 0.06),
                mtl_bracket if mtl_bracket is not None else mtl_body))
        if pipe:
            # Refrigerant/drain pipe cover - hugs the wall and runs downwards.
            # Standard pipe length is 5 m for wall type / 8 m for stand type (source: LG installation
            # guide), but the exposed length is `[estimate]` - only 0.9 m below the unit is modelled.
            prims.append(K.cyl(
                stage, f"{prefix}/AcPipe_{i}",
                fac.world(u + w / 2.0 + 0.07, 0.05, zb - 0.45),
                0.028, 0.90,
                mtl_bracket if mtl_bracket is not None else mtl_body))
    return prims


# ===========================================================================
# [7] Priority 4 - signage (wall-mounted and projecting)
# ===========================================================================
def build_signage(K, stage, prefix, fac, mtl_panel, mtl_frame=None,
                  band_z=None, band_h=0.80, band_len_max=10.0,
                  n_projecting=2, proj_seg_h=1.20, proj_gap=0.22,
                  sidewalk=True, corner="u1", seed=0):
    """Wall-mounted sign band + **vertical stack** of projecting signs.
    **Prims per building = 1 + n_projecting** (3 by default).

    Survey priority **4** - it changes the lower-storey silhouette the most.
    The figures are **fixed by law**, making this the highest-confidence item in the
    document. (Sources: Outdoor Advertisement Act Enforcement Decree + the **Seoul
    Metropolitan Government outdoor advertisement ordinance**. The scenes are set in
    Seoul, so Seoul values are used - Incheon and Uiseong differ.)

    Wall-mounted sign - statutory
      - 1 per business; horizontal length within the building width, **max 10 m**
      - vertical height may not exceed 1/2 of the building height (panel type on a
        window: **0.80**)
      - **projection within 0.30** (0.40 by exception, 1.80 for illuminated types)

    Projecting sign - statutory (Seoul)
      - ground to underside **>=3.0** (**4.0** where there is no sidewalk; 2.0 for
        medical, pharmacy and hairdressing)
      - projection **<=1.00** (1.2 with review), thickness **<=0.30** (0.5 with review)
      - vertical length **<=3.5**, gap from the wall face **<=0.30**
      - 1 per business; multiple businesses are **aligned in a straight line** - this
        alignment is the strongest visual signature of a Korean shopping street, which
        is why the stack shares one u coordinate.
      - the default `proj_seg_h` of 1.20 is the vertical length of one segment in a
        multi-business stack `[estimate]` (clamped internally so the statutory limit of
        3.5 is not exceeded).

    With band_z=None the band sits at the top of the ground-floor opening,
    z ~= base_z + 3.30 `[estimate]`.
    corner: "u1" (the far horizontal end) / "u0" - which facade corner carries the
    projecting stack.
    """
    rng = _rng(prefix, "sign", seed)
    prims = []
    W = fac.width
    if W < 2.0:
        return prims

    # --- Wall-mounted band (statutory: max 10 m, projection <=0.30) -------
    bz = (fac.base_z + 3.30) if band_z is None else float(band_z)
    bh = min(float(band_h), 0.80)
    blen = min(W - 0.40, float(band_len_max))
    if blen > 0.8:
        prims.append(K.box(
            stage, f"{prefix}/SignBand",
            fac.world(fac.mid, SIGN_BAND_PROUD / 2.0, bz + bh / 2.0),
            fac.size(blen, SIGN_BAND_PROUD, bh), mtl_panel))

    # --- Projecting sign vertical stack (straight-line alignment) --------
    n = max(0, int(n_projecting))
    if n:
        # Gap from the wall <=0.30 -> near end out=0.10, far end out=1.00
        near_out, far_out = 0.10, SIGN_PROJ_OUT
        d = far_out - near_out
        u = (fac.u1 - 0.70) if corner == "u1" else (fac.u0 + 0.70)
        z = fac.base_z + (SIGN_PROJ_BOTTOM if sidewalk else 4.00)
        seg = min(float(proj_seg_h), 3.50)      # Statutory vertical length <=3.5
        for i in range(n):
            h_i = _jit(rng, seg)                # Per-instance variation within +-8 %
            prims.append(K.box(
                stage, f"{prefix}/SignProj_{i}",
                fac.world(u, near_out + d / 2.0, z + h_i / 2.0),
                fac.size(SIGN_PROJ_T, d, h_i),  # Horizontal = thickness 0.30, wall normal = projection
                mtl_frame if mtl_frame is not None else mtl_panel))
            z += h_i + float(proj_gap)
    return prims


# ===========================================================================
# [8] Priority 5 - balcony slabs + guardrails (what makes an apartment read as one)
# ===========================================================================
def build_balcony_stack(K, stage, prefix, fac, levels, mtl_slab, mtl_rail,
                        bay_w=9.00, core_every=3, depth=BALCONY_DEPTH,
                        slab_t=SLAB_T, rail_h=RAIL_H, start_floor=1,
                        max_floors=None, balusters=False,
                        baluster_r=0.010, seed=0):
    """Balcony slab + guardrail stack. **Prims per building = 2 x (bays used) x (floors)**
    (with balusters=True the baluster count per bay and floor is added - default False).

    Survey priority **5**, and an important fact: **this is cheaper in prims than the
    current window grid.** (Current = floors x ncols windows + one SillBand per floor.
    Balcony = floors x dwellings x 2. A 9 m bay is 3.6x the 2.5 m col_step, so prims
    drop to about 1/1.8.)

    Dimension basis
      - balcony depth **1.50** (max 2.00 with a planter) - **statutory**:
        Building Act Enforcement Decree §119(1)3(b) (balcony deduction = length along
        the outer wall x 1.5)
      - guardrail height **>=1.20** - **statutory**: Building Act Enforcement Decree §40
      - baluster spacing **<=0.10** - **statutory**: Procedures and Standards for
        Balcony Structural Alteration
      - slab thickness **>=0.21** - **statutory**: Housing Construction Standards §14-2(1)
      - dwelling facade width 8-12 m; the stair/lift core between dwellings is
        2.5-3.5 m wide `[knowledge]`
        -> **the core bay is the decisive element that breaks the facade rhythm** and is
          absent today. `core_every=3` empties one bay in every three as a core.

    **Guardrail 1.20 is a scale anchor: do not randomise.** Only depth and slab get
    +-8 % variation. Pass the `floor_levels()` result (list of floor z) as `levels`.
    `max_floors` lets the `window_rows_visible()` cap be inherited directly.
    """
    rng = _rng(prefix, "balcony", seed)
    prims = []
    W = fac.width
    if W < 3.0 or not levels:
        return prims
    nb = max(1, int(round(W / max(3.0, float(bay_w)))))
    bw = W / nb
    lv = list(levels)[:-1]                      # The last level is the roof slab
    f0 = max(0, int(start_floor))
    if max_floors is not None:
        lv = lv[:max(1, int(max_floors))]
    dep = _jit(rng, float(depth))
    st = max(0.10, float(slab_t))
    rh = float(rail_h)                          # Anchor - no jitter

    for f in range(f0, len(lv)):
        zf = lv[f]
        for b in range(nb):
            if core_every and (b % int(core_every)) == int(core_every) - 1:
                continue                        # Stair/lift core bay - no balcony
            u = fac.u0 + (b + 0.5) * bw
            # Slab - top flush with the floor level
            prims.append(K.box(
                stage, f"{prefix}/BalconySlab_{f}_{b}",
                fac.world(u, dep / 2.0, zf - st / 2.0),
                fac.size(bw - 0.30, dep, st), mtl_slab))
            # Guardrail - height 1.20 (statutory minimum). Stands at the outer slab edge.
            prims.append(K.box(
                stage, f"{prefix}/BalconyRail_{f}_{b}",
                fac.world(u, dep - 0.04, zf + rh / 2.0),
                fac.size(bw - 0.30, 0.06, rh), mtl_rail))
            if balusters:
                # Statutory clear spacing <=0.10 - real ones are dense without exception.
                # Prims explode to (bw-0.3)/0.12 ~= 70 per bay, so enable this only on
                # **close buildings (<20 m)**.
                pitch = 2.0 * float(baluster_r) + BALUSTER_GAP
                x = u - (bw - 0.30) / 2.0 + pitch * 0.5
                k = 0
                while x < u + (bw - 0.30) / 2.0:
                    prims.append(K.cyl(
                        stage, f"{prefix}/BalconyBal_{f}_{b}_{k}",
                        fac.world(x, dep - 0.04, zf + rh / 2.0),
                        float(baluster_r), rh, mtl_rail))
                    x += pitch
                    k += 1
    return prims


# ===========================================================================
# [9] Priority 6 - downpipe verticals + exposed gas piping
# ===========================================================================
def build_downpipe_run(K, stage, prefix, fac, top_z, mtl_pipe,
                       n_pipes=2, dn=DOWNPIPE_DN100, wall_gap=0.05,
                       elbow=True, gas=False, gas_levels=None,
                       mtl_gas=None, mtl_band=None, gas_variant="A",
                       gas_u=None, seed=0):
    """Rainwater downpipe verticals + exposed gas piping on the outer wall.
    **Prims per building = 2*n_pipes + gas (variant A: 2 / variant B: 2 + 2 x floors)**
    (defaults n_pipes=2, gas=True, variant A -> **6**).

    Survey priority **6** - 1-3 prims break the flatness of the facade. **A single
    vertical line** at the facade corner is the cheapest silhouette contribution there is.

    Downpipe basis
      - pipe size vs horizontally projected roof area (rainfall 100 mm/h): **DN 50 ->
        67 m2, DN 100 -> 427 m2, DN 150 -> 1,254 m2**
        (source: **KDS 31 30 35 : 2016**, rainwater drainage design standard)
      - branches under 3 m total length may be DN 75; horizontal branch slope
        >=1/100 (same source)
      - **half the outer wall area is included in the roof area** when sizing, with a
        safety factor of 1.5 (same source)
      - -> recommended for modelling multiplex and shop buildings: **DN 100 (outer
        diameter 0.114)** `[estimate - derived from the table above]`
      - spacing: at the facade corner plus one every 8-12 m `[estimate]`
      - wall clearance 0.05 (band fixing) `[knowledge]`; 90 deg elbow at ground +0.3
        `[estimate]`
      - material and colour are `[estimate]` (the KDS text has no material clause) -
        grey PVC assumed

    Gas piping basis - **KGS FU551 2.5.7.2** (distinctly Korean. Verified.)
      - **above-ground piping surface colour = yellow** (after anti-corrosion coating)
      - **yellow substitution**: exposed above-ground piping on interior/exterior walls
        may skip the yellow coating if marked with **two 0.030 m wide yellow bands at
        1 m above the floor** (above the 2nd floor, above each floor level)
      - in-dwelling pipe diameter **0.020** (source: LH city gas installation
        specification 201206_54510)
      - shared riser 0.032-0.040 `[estimate]`
      - **riser main valve mounting height 1.6-2.0 m above the floor** (same source)
        -> straight ahead at **robot eye level (0.3-1.8 m)**, so the effect is large
      - pipe support spacing is `[no source]` (PDF extraction of Enforcement Rules
        annex 7 failed) -> not implemented

    gas_variant
      "A" : whole riser painted yellow. Very common on older multiplexes `[knowledge]`.
            2 prims.
      "B" : grey paint + two 0.030 wide yellow bands at floor +1.00 on each floor
            (**the statutory substitution**). 2 + 2 x floors prims. `mtl_band` must be
            passed.
    """
    rng = _rng(prefix, "downpipe", seed)
    prims = []
    W = fac.width
    z0 = fac.base_z
    zt = float(top_z)
    if zt - z0 < 1.0:
        return prims
    r = max(0.02, float(dn) / 2.0)
    out_c = float(wall_gap) + r

    n = max(1, int(n_pipes))
    for i in range(n):
        # Corners first (survey: facade corner plus one every 8-12 m [estimate])
        if n == 1:
            u = fac.u1 - 0.45
        else:
            u = fac.u0 + 0.45 + i * (W - 0.90) / (n - 1)
        h = zt - z0 - 0.30
        prims.append(K.cyl(
            stage, f"{prefix}/Downpipe_{i}",
            fac.world(u, out_c, z0 + 0.30 + h / 2.0), r, h, mtl_pipe))
        if elbow:
            # Discharges through a 90 deg elbow at ground +0.3 [estimate]
            prims.append(K.box(
                stage, f"{prefix}/DownpipeElbow_{i}",
                fac.world(u, out_c + 0.06, z0 + 0.18),
                fac.size(2 * r, 2 * r + 0.12, 0.26), mtl_pipe))

    if not gas:
        return prims

    mg = mtl_gas if mtl_gas is not None else mtl_pipe
    gu = fac.u0 + 0.95 if gas_u is None else float(gas_u)
    gr = 0.018                                  # Shared riser 0.032-0.040 [estimate]
    gh = zt - z0 - 0.10
    prims.append(K.cyl(
        stage, f"{prefix}/GasRiser",
        fac.world(gu, 0.06 + gr, z0 + gh / 2.0), gr, gh, mg))
    # Riser main valve - floor +1.6-2.0 (confirmed). Straight ahead at eye level.
    vz = z0 + rng.uniform(*GAS_VALVE_Z)
    prims.append(K.box(
        stage, f"{prefix}/GasValve",
        fac.world(gu, 0.06 + gr, vz),
        fac.size(0.16, 2 * gr + 0.10, 0.14), mg))

    if str(gas_variant).upper() == "B" and gas_levels:
        # Statutory substitution: **two** 0.030 wide yellow bands at floor +1.00 on each floor.
        # The gap between bands is unregulated -> 0.06 [estimate] (survey recommends 0.05-0.10).
        mb = mtl_band if mtl_band is not None else mg
        for f, zf in enumerate(list(gas_levels)[:-1] or list(gas_levels)):
            for k in range(2):
                prims.append(K.box(
                    stage, f"{prefix}/GasBand_{f}_{k}",
                    fac.world(gu, 0.06 + gr,
                              zf + GAS_BAND_Z + k * 0.06),
                    fac.size(2 * gr + 0.01, 2 * gr + 0.01, GAS_BAND_W), mb))
    return prims


# ===========================================================================
# [10] Priority 7.5 - fire entry window red inverted triangle decal (the cheapest Korean signal)
# ===========================================================================
def _bind(prim, mtl):
    if mtl is not None:
        from pxr import UsdShade
        UsdShade.MaterialBindingAPI.Apply(prim).Bind(mtl)


def build_fire_access_marks(stage, prefix, fac, levels, mtl_decal,
                            tri_d=FIRE_TRI_D, spacing_m=FIRE_SPACING,
                            floor_min=2, floor_max=11, sill_up=FIRE_SILL_MAX,
                            win_h=1.20, out=0.010, max_floors=None,
                            hit_mark=False, out_fn=None):
    """**Fire entry window red inverted triangle decal.**
    **Prims per building = (stations) x (marked floors)** - one thin triangular quad
    per location.
    Most of our buildings have facades under 40 m wide, so one station and 2-4 marked
    floors -> **2-4 prims per building**. The cheapest Korean signal available.

    Survey priority **7.5** - **statutorily mandatory** on 2- to 11-storey buildings, so
    in reality it is present 100 % of the time. The library currently has zero.

    Statutory basis: Rules on Evacuation and Fire Protection Structures of Buildings
    **Article 18-2**
      - placement: at least one per floor, plus one every **40 m of horizontal wall
        distance**
      - window size: width **>=0.9**, height **>=1.2** (>=1.0 after the 2024-08-26
        amendment)
      - sill height: within **0.8** of the interior floor (within 1.2 for a balcony with
        a guardrail)
      - **marking: a red inverted triangle (diameter >=0.20) at the window centre** -
        retroreflective at night
      - strike point: a circular mark of diameter >=0.03 at the corner
        -> created only with `hit_mark=True`. 0.03 is sub-pixel at evaluation distance
          (>=10 m), so it is **off** by default (prim saving).

    Geometry: an equilateral triangle inscribed in a circle of diameter `tri_d`, with
    the **vertex pointing down**. A 3-point Mesh offset `out` (default 0.010) from the
    wall face - the minimum that avoids z-fighting.

    `out_fn(u, z) -> out` **[B-F1]** overrides the flat `out` per station. The facade
    plane is not always the outermost surface at a given (u, z): an apartment's
    stair/lift core protrudes `building_kit.CORE_PROUD` = 0.60 m, so a mark placed at
    a flat 0.010 lands **588 mm inside the core** and is invisible. Pass a resolver
    (`building_kit.Plan.out_at`) and each station sits on whatever wall is really
    there. With `out_fn=None` the behaviour is exactly the flat `out` as before.
    `subdivisionScheme="none"` is **authored explicitly** (the USD default catmullClark
    rounds the triangle and destroys the shape - same reason as build_sign).
    doubleSided=True removes any winding-direction bug at the root (same prim count).

    Material: a red constant colour (`FIRE_RED`) is recommended. Putting a
    "sign"/"placard" style token in the material path makes the look layer classify it
    in the sign role and preserve the constant colour
    (v5.1 §4 - constant colours of signs and painted markings are inviolable).
    """
    from pxr import UsdGeom, Gf

    prims = []
    if not levels:
        return prims
    W = fac.width
    R = max(0.03, float(tri_d) / 2.0)
    lv = list(levels)[:-1] if len(levels) > 1 else list(levels)
    if max_floors is not None:
        lv = lv[:max(1, int(max_floors))]

    n_st = max(1, int(math.ceil(W / float(spacing_m))))

    for s in range(n_st):
        u = fac.u0 + (s + 0.5) * (W / n_st)
        for f, zf in enumerate(lv):
            fl = f + 1                          # 1-based floor number
            if fl < int(floor_min) or fl > int(floor_max):
                continue
            # Window centre z = floor level + sill height (statutory max 0.8) + window height/2
            zc = zf + float(sill_up) + float(win_h) / 2.0
            o = float(out) if out_fn is None else float(out_fn(u, zc))
            # Equilateral triangle (vertex down): angles -90, 30, 150 deg
            pts = []
            for ang in (-90.0, 30.0, 150.0):
                a = math.radians(ang)
                du, dz = R * math.cos(a), R * math.sin(a)
                pts.append(Gf.Vec3f(*[float(v) for v in
                                      fac.world(u + du, o, zc + dz)]))
            path = f"{prefix}/FireMark_{s}_{fl}"
            mesh = UsdGeom.Mesh.Define(stage, path)
            mesh.CreatePointsAttr(pts)
            mesh.CreateFaceVertexCountsAttr([3])
            mesh.CreateFaceVertexIndicesAttr([0, 1, 2])
            mesh.CreateSubdivisionSchemeAttr("none")
            mesh.CreateDoubleSidedAttr(True)
            # extent is computed by hand. UsdGeom.PointBased.ComputeExtent is not safe:
            # the static vs instance signature differs between binding versions.
            mesh.CreateExtentAttr([
                Gf.Vec3f(*[min(p[i] for p in pts) for i in range(3)]),
                Gf.Vec3f(*[max(p[i] for p in pts) for i in range(3)])])
            _bind(mesh.GetPrim(), mtl_decal)
            prims.append(mesh)

            if hit_mark:
                # Strike point circle, diameter 0.03 (statutory) - near the corner (top right)
                hp = []
                for ang in (0.0, 120.0, 240.0):
                    a = math.radians(ang)
                    du, dz = 0.015 * math.cos(a), 0.015 * math.sin(a)
                    hp.append(Gf.Vec3f(*[float(v) for v in fac.world(
                        u + 0.35 + du, o, zc + R + 0.10 + dz)]))
                hm = UsdGeom.Mesh.Define(stage, f"{prefix}/FireHit_{s}_{fl}")
                hm.CreatePointsAttr(hp)
                hm.CreateFaceVertexCountsAttr([3])
                hm.CreateFaceVertexIndicesAttr([0, 1, 2])
                hm.CreateSubdivisionSchemeAttr("none")
                hm.CreateDoubleSidedAttr(True)
                _bind(hm.GetPrim(), mtl_decal)
                prims.append(hm)
    return prims
