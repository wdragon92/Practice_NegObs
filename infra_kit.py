# -*- coding: utf-8 -*-
"""infra_kit.py - procedural kit for drainage, road surface and retaining wall detail
(Isaac Sim 4.5 / USD)

Written 2026-07-29, target: the 33 NegObs scenes (21 main + 12 batch 1)

## Why this file exists (measured facts)

1. **Drainage elements are absent from all 33 scenes.**
   `cue_arrangement_survey.md` §4.3(1) - an exhaustive grep for
   drainage/rainwater/gutter/manhole/catch-basin terms found **not one** in the
   21 main scenes. On real Korean sidewalks and roads, gullies are **mandatory** at
   20-25 m intervals on straight sections (National Highway Construction Design
   Practice Guide, 3. Drainage, item pa), and L-type gutters run continuously along
   the carriageway edge (same document, 3. Drainage 2)). Without them the result is
   "a stage that has paving but nowhere for water to go".

2. **scene13 is missing the ramp-side curbs mandated by the Parking Lot Act
   Enforcement Rules §6(1)5(c) entirely.**
   (h 10-15 cm, at least 30 cm from each wall face) - this is not a cosmetic issue but
   **a drop line that should exist and does not**, so it bears directly on the research
   labels.

3. Gutters, gullies and manholes are **linear cues** on the road surface and are
   small drops in themselves. They feed straight into the input signal of this research
   (RGB context cues -> invisible drop estimation).

## Conventions (all functions)

- **Z-up coordinate system, metres.**
- **RNG 100 % deterministic** - `hash()` is strictly banned (PYTHONHASHSEED makes it
  vary per process; this actually broke once). Only `zlib.crc32` ->
  `random.Random(seed)` is used.
- **Do not import `scene_common`.** Primitive helpers are injected via `Kit`
  (preventing a circular import). `kit_from_scene_common(sc, stage)` **takes an
  already-imported module object as an argument**; it does not import.
- **Joints and seams are handled without a prim explosion.** A gutter joint is the
  **gap between panels** in a two-layer "base slab + panel" build (real recessed
  geometry); a retaining wall contraction joint is a 1 mm proud dark strip (standing in
  for a recess). Each function docstring states **prims per metre / per unit**.
- Unsourced numbers are never invented. If it is not in the index
  (`Docs/surveys/_dimension_index.md`), it is tagged `[estimate]` / `[no source]`
  with a stated rationale.
- The **`GT:` line** in each function docstring defines whether what the function
  builds counts as a GT drop. An integrator can read that line alone and know the label
  impact.

## GT drop impact summary (this table alone is enough)

| function | creates GT drop | note |
|---|---|---|
| `build_gutter_L`        | **no** | but curb exposure grows by `width*cross_slope` (about 18-30 mm) -> recompute the curb GT |
| `build_gully`           | `lid=True` no / **`lid=False` yes** | uncovered, drop = `body_h` (0.64 m) |
| `build_manhole`         | `lid=True` no / **`lid=False` yes** | flush +-10 mm is below a minor step |
| `build_ramp_curb`       | **yes** | curb top -> carriageway = `height` (0.10-0.15 m). **New drop line** |
| `build_road_marking`    | no | paint thickness <=4 mm. Scale anchor only |
| `build_retaining_wall_details` | no (default) | with `cope_flush=False` the wall-top GT **increases** by `cope_h` |
| `build_tactile_pair`    | no | dots 5-6 mm |

## Usage

```python
import infra_kit as ik
kit = ik.kit_from_scene_common(sc, stage)          # sc = already-imported scene_common
ik.build_gutter_L(kit, f"{ROOT}/Gutter", 0.0, -4.0, 60.0, -4.0,
                  top_z=0.0, mtl=M["concrete"])
for x in ik.gully_positions(0.0, 60.0, sag_points=(23.5,)):
    ik.build_gully(kit, f"{ROOT}/Gully_{x:.0f}", x, -3.75, 0.0, M["steel"])
```

Check prim counts and geometry without Isaac: `python3 infra_kit.py`
"""

from __future__ import annotations

import math
import random
import zlib

__all__ = [
    "Kit", "kit_from_scene_common", "dry_kit",
    "det_seed", "det_rng",
    "INFRA_DIMENSIONS", "TACTILE_YELLOW",
    "build_gutter_L", "gully_positions", "build_gully", "build_manhole",
    "build_ramp_curb", "build_road_marking", "wall_joint_positions",
    "build_retaining_wall_details", "build_tactile_pair",
]


# ===========================================================================
# [0] Dimension ledger - every number baked into the code has its source here, in one place.
#     To change a value, **update the basis in this table first**. Putting a number that is
#     not in the table into a function default is forbidden (this prevents invented values).
# ===========================================================================
INFRA_DIMENSIONS = {
    # -- L-type gutter --------------------------------------------------
    "gutter_L_width":       (0.30, "확인", "국도건설공사 설계실무요령 3.배수공 2) 형식-1 도면 (300/500)"),
    "gutter_L_width_alt":   (0.50, "확인", "동 (형식-1 대안 폭)"),
    "gutter_L_thick":       (0.20, "확인", "동 (두께 200)"),
    "gutter_contraction":   (6.00, "확인", "동 ※ 수축줄눈 간격 6 m (형식-1,2,4,5)"),
    "gutter_expansion":     (20.0, "확인", "동 ※ 신축이음재(스치로폴) 간격 20 m (형식-3 은 12 m)"),
    "gutter_floor_grade":   (0.06, "추정", "원문은 바닥경사 4~10 % 범위. 6 % 는 그 중앙값 [추정]"),
    "gutter_groove_w":      (0.008, "추정", "L형 측구 줄눈 폭 원문 없음. 옹벽 수축이음 6~8 mm 준용 [추정]"),
    "gutter_groove_d":      (0.014, "추정", "동. 옹벽 수축이음 깊이 12~16 mm 준용 [추정]"),
    # -- Gully ----------------------------------------------------------
    "grate_across":         (0.40, "확인", "국도 실무요령 수량내역서 집수정용 스틸그레이팅 400×500×50"),
    "grate_along":          (0.50, "확인", "동"),
    "grate_thick":          (0.05, "확인", "동"),
    "gully_body_across":    (0.410, "추정", "업계 통용 410×510×H640. 원문 미확인 [추정]"),
    "gully_body_along":     (0.510, "추정", "동 [추정]"),
    "gully_body_h":         (0.640, "추정", "동 [추정]"),
    "gully_spacing":        (22.0, "확인", "동 3.배수공 파: 직선부 20~25 m. 22 는 그 중앙"),
    "gully_spacing_max":    (25.0, "확인", "동 (상한)"),
    # -- Manhole --------------------------------------------------------
    "manhole_d_648":        (0.648, "확인", "KS D 4040 인증제품 / 국도 실무요령 3.17 (차도 회주철·보도 칼라 공통)"),
    "manhole_d_766":        (0.766, "확인", "동 (옵션)"),
    "manhole_d_918":        (0.918, "확인", "동 (옵션)"),
    "manhole_thick":        (0.110, "확인", "동 110t"),
    "manhole_flush_tol":    (0.010, "확인", "노면과 동일면 ±10 mm (임무 지시 / 실무 ±10~20 mm)"),
    "manhole_frame_w":      (0.045, "추정", "틀 링 폭. 원문 없음 [추정]"),
    # -- Parking ramp curb ----------------------------------------------
    "ramp_curb_h_min":      (0.10, "확인", "주차장법 시행규칙 §6①5다 — 높이 10~15 cm"),
    "ramp_curb_h_max":      (0.15, "확인", "동"),
    "ramp_curb_offset":     (0.30, "확인", "동 — 양쪽 벽면으로부터 30 cm 이상 지점"),
    # -- Road markings --------------------------------------------------
    "stall_w":              (2.50, "확인", "주차장법 시행규칙 §3 일반형 2.5×5.0 (확장형 2.6×5.2)"),
    "stall_l":              (5.00, "확인", "동"),
    "crosswalk_stripe":     (0.45, "확인", "도로교통법 시행규칙 별표6 노면표시 / scene_composition_audit §(6)"),
    "crosswalk_gap":        (0.45, "확인", "동"),
    "marking_line_w":       (0.15, "추정", "주차구획 실선 두께. 통상 10~15 cm, 원문 미확인 [추정]"),
    "marking_proud":        (0.003, "추정", "도색 두께. 원문 없음 [추정]. 4 mm 이하면 낙차 아님"),
    # -- Retaining wall -------------------------------------------------
    "weep_d":               (0.100, "확인", "도로설계요령 3권 8-7편 옹벽 6 — 직경 100 mm 정도"),
    "weep_spacing":         (4.00, "확인", "동 — 약 4 m 간격, 부벽 사이 최소 1개"),
    "weep_area":            (3.00, "확인", "건축법 시행규칙 §25 — 3 ㎡마다 1개 이상"),
    "weep_z":               (0.35, "추정", "설치 높이. 지표+300~500 mm [추정] (원문 없음)"),
    "wall_contraction":     (9.00, "확인", "도로설계요령 8-7편 6(다) — 홈 6~8 × 깊이 12~16 mm, 9 m 이하"),
    "wall_groove_w":        (0.007, "확인", "동 (6~8 mm 의 중앙)"),
    "wall_groove_d":        (0.014, "확인", "동 (12~16 mm 의 중앙)"),
    "wall_exp_gravity":     (10.0, "확인", "동 (라) — 중력식 10 m 이하"),
    "wall_exp_cantilever":  (17.5, "확인", "동 (라) — 캔틸레버·부벽식 15~20 m 의 중앙"),
    "wall_cope_over":       (0.04, "추정", "갓돌 좌우 내밀기 30~50 mm [추정] (국내 규정 부재 확인)"),
    # -- Tactile paving -------------------------------------------------
    "tactile_tile":         (0.300, "확인", "교통약자법 시행규칙 별표1 — 300×300"),
    "tactile_dot_n":        (36, "확인", "동 — 점형 36점"),
    "tactile_dot_h":        (0.006, "확인", "동 — h 6±1 mm"),
    "tactile_bar_n":        (4, "확인", "동 — 선형 4선"),
    "tactile_bar_h":        (0.005, "확인", "동 — h 5±1 mm"),
}

# The statute specifies only "yellow" for tactile paving and gives no colour coordinates `[no source]`.
# The RGB below approximates the yellow used in practice `[estimate]`. Unrelated to v5.1 §4 (no pure white).
TACTILE_YELLOW = (0.86, 0.66, 0.10)


# ===========================================================================
# [1] Deterministic RNG - hash() banned. Only zlib.crc32 is used.
#     (scene_common._ground_skin was switched to crc32 for the same reason)
# ===========================================================================
def det_seed(*keys):
    """A **process-independent** 32-bit seed from coordinate/string keys.

    Floats are quantised to 0.1 mm and stringified - this stops repr wobble from
    changing the seed. Python's builtin `hash()` is randomised on every run by
    PYTHONHASHSEED and is therefore **never used**.
    """
    parts = []
    for k in keys:
        if isinstance(k, str):
            parts.append(k)
        elif isinstance(k, (int,)) and not isinstance(k, bool):
            parts.append("i%d" % k)
        else:
            parts.append("f%.4f" % float(k))
    return zlib.crc32("|".join(parts).encode("utf-8")) & 0xFFFFFFFF


def det_rng(*keys):
    """Deterministic `random.Random`. Same key -> always the same sequence."""
    return random.Random(det_seed(*keys))


# ===========================================================================
# [2] Kit - primitive helper injection container
#
#     Importing scene_common would create a scene <-> kit circular import (scenes already
#     import scene_common). So **the caller passes the helpers in.**
#     The expected signatures match the local closures already present in each scene file:
#
#       box  (path, center, size, mtl=None, col=False)
#       cyl  (path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False)
#       obox (path, center, size, mtl=None, rotz=0.0, rotx=0.0, col=False)
#       slope(path, x0, z0, run, drop, y0, y1, thick, mtl, margin=0.3, col=True)
#
#     obox/slope are optional. If one is missing while rotation/slope is needed, a clear
#     exception is raised (better than a silent misplacement).
# ===========================================================================
class Kit:
    """Bundle of primitive helpers. The first argument of every build_* function."""

    def __init__(self, box, cyl=None, obox=None, slope=None, stage=None,
                 disc=None):
        self.box = box
        self.cyl = cyl
        self.obox = obox
        self.slope = slope
        self.disc = disc                      # [W2 F5] n-gon prism (silhouette-controlled)
        self.stage = stage
        self.prims = []                       # Log of created paths (for checking and prim counting)

    # -- Shared internal entry point -------------------------------------
    def B(self, path, center, size, mtl=None, rotz=0.0, rotx=0.0, col=False):
        """Box that decides on rotation by itself. With rot 0 it uses an axis-aligned box."""
        self.prims.append(path)
        if abs(rotz) < 1e-9 and abs(rotx) < 1e-9:
            return self.box(path, center, size, mtl, col)
        if self.obox is None:
            raise ValueError(
                "infra_kit: 회전 박스가 필요한데 Kit(obox=...) 가 없다. "
                "scene_common._oriented_box 를 주입하거나 회전을 0 으로 두라. "
                f"(path={path}, rotz={rotz}, rotx={rotx})")
        return self.obox(path, center, size, mtl, rotz, rotx, col)

    def C(self, path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        self.prims.append(path)
        if self.cyl is None:
            raise ValueError(
                f"infra_kit: 실린더 헬퍼가 없다. Kit(cyl=...) 주입 필요. ({path})")
        return self.cyl(path, center, r, h, mtl, rotY, rotX, col)

    def D(self, path, center, r, h, mtl=None, seg=32, col=False):
        """[W2 fix batch F5] Disc whose **silhouette segment count is explicit**.

        Same (center, r, h) contract as `C` and the same 1-prim cost, but the Hydra
        default tessellation of an analytic `UsdGeom.Cylinder` (the octagon / 12-gon
        of defect D4) is replaced by an n-gon prism mesh. Degrades to `C` when no
        `disc` helper was injected, so any Kit built the old way still works.
        """
        if self.disc is None:
            return self.C(path, center, r, h, mtl, col=col)
        self.prims.append(path)
        return self.disc(path, center, r, h, mtl, seg, col)

    def S(self, path, x0, z0, run, drop, y0, y1, thick, mtl,
          margin=0.0, col=True):
        self.prims.append(path)
        if self.slope is None:
            raise ValueError(
                f"infra_kit: 경사 슬래브 헬퍼가 없다. Kit(slope=...) 주입 필요. ({path})")
        return self.slope(path, x0, z0, run, drop, y0, y1, thick, mtl,
                          margin, col)

    def count_since(self, mark):
        return len(self.prims) - mark

    def mark(self):
        return len(self.prims)

    # -- facade_kit compatible constructor -------------------------------
    @classmethod
    def from_sc_helpers(cls, stage, add_box, add_cylinder=None,
                        oriented_box=None, build_slope=None):
        """Same style as `facade_kit.Kit` - takes the **raw functions, not stage-bound ones**.

        An alternative constructor kept so that anyone used to
        `facade_kit.Kit(add_box, add_cylinder, _oriented_box)` is not confused. The
        expected signatures are the current scene_common ones:

            add_box(stage, path, center, size, mtl=None, collider=False)
            add_cylinder(stage, path, center, r, h, mtl=None,
                         rotY=0.0, rotX=0.0, collider=False)
            oriented_box(stage, path, center, size, mtl=None, collider=False,
                         rotz=0.0, rotx=0.0)
            build_slope(stage, path, x0, z0, run, drop, y0, y1, thick, mtl,
                        margin=0.3, collider=True)
        """
        def _b(path, center, size, mtl=None, col=False):
            return add_box(stage, path, center, size, mtl, col)

        def _c(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
            return add_cylinder(stage, path, center, r, h, mtl,
                                rotY=rotY, rotX=rotX, collider=col)

        def _o(path, center, size, mtl=None, rotz=0.0, rotx=0.0, col=False):
            return oriented_box(stage, path, center, size, mtl,
                                collider=col, rotz=rotz, rotx=rotx)

        def _s(path, x0, z0, run, drop, y0, y1, thick, mtl,
               margin=0.0, col=True):
            return build_slope(stage, path, x0, z0, run, drop, y0, y1,
                               thick, mtl, margin=margin, collider=col)

        return cls(_b,
                   _c if add_cylinder is not None else None,
                   _o if oriented_box is not None else None,
                   _s if build_slope is not None else None,
                   stage=stage)


def kit_from_scene_common(sc, stage):
    """Build a Kit from an already-imported `scene_common` module object (`sc`).
    **The recommended path.**

    **This function does not import anything** - it only uses the module object the
    caller passed.
    In a scene:  `kit = infra_kit.kit_from_scene_common(sc, stage)`
    (To pass raw functions directly, use `Kit.from_sc_helpers(stage, ...)` -
    facade_kit style.)
    """
    def _box(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def _cyl(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def _obox(path, center, size, mtl=None, rotz=0.0, rotx=0.0, col=False):
        return sc._oriented_box(stage, path, center, size, mtl,
                                collider=col, rotz=rotz, rotx=rotx)

    def _slope(path, x0, z0, run, drop, y0, y1, thick, mtl,
               margin=0.0, col=True):
        return sc.build_slope(stage, path, x0, z0, run, drop, y0, y1,
                              thick, mtl, margin=margin, collider=col)

    def _disc(path, center, r, h, mtl=None, seg=32, col=False):
        return sc.add_disc(stage, path, center, r, h, mtl,
                           seg=seg, collider=col)

    return Kit(_box, _cyl, _obox, _slope, stage=stage,
               disc=(_disc if hasattr(sc, "add_disc") else None))


def dry_kit():
    """Dummy Kit that only records prim counts and coordinates, without Isaac (for checks and unit tests)."""
    def _rec(kind):
        def f(path, *a, **kw):
            return ("dry", kind, path, a, kw)
        return f
    return Kit(_rec("box"), _rec("cyl"), _rec("obox"), _rec("slope"),
               disc=_rec("disc"))


# ===========================================================================
# [3] Shared line geometry (used by gutters, markings and retaining walls)
# ===========================================================================
def _line_frame(x0, y0, x1, y1):
    """Segment -> (length, bearing [deg], unit direction, left normal). Raises on zero length."""
    dx, dy = float(x1) - float(x0), float(y1) - float(y0)
    L = math.hypot(dx, dy)
    if L < 1e-9:
        raise ValueError("infra_kit: 길이 0 인 선분은 만들 수 없다.")
    a = math.atan2(dy, dx)
    return L, math.degrees(a), (math.cos(a), math.sin(a)), (-math.sin(a),
                                                            math.cos(a))


def _bay_joints(length, expansion, contraction):
    """**Single source of truth** for joint positions (shared by gutters and retaining
    walls). Returns `[(s, kind), ...]`.

    ### Why you cannot just enumerate "every 6 m / every 20 m"
    6 and 20 have no common divisor. Plain enumeration produces **2 m offcut panels**
    (e.g. between 18 m and 20 m). Real construction never yields such a fragment - the
    contractor **divides the run into bays at the expansion joints first, then splits
    each bay evenly to at most the specified spacing**.

    So this function solves it in two stages.
      (1) expansion joints: `n_bay = ceil(L / expansion)` -> bay length `L/n_bay`
          (the rule is "at most", so an even split always satisfies it)
      (2) contraction joints: split each bay into `ceil(bay / contraction)`

    L=60, expansion 20, contraction 6 -> three 20 m bays, each split into 4 =
    **uniform 5.0 m panels** (5.0 <= 6 satisfies the rule, zero offcut). That uniform
    rhythm is itself the silhouette cue.

    Passing 0/None for `expansion` or `contraction` omits that joint type.
    """
    L = float(length)
    out = []
    n_bay = (max(1, int(math.ceil(L / float(expansion) - 1e-9)))
             if expansion and expansion > 0 else 1)
    bay = L / n_bay
    for i in range(n_bay):
        a = bay * i
        if i > 0:
            out.append((a, "expansion"))
        if contraction and contraction > 0:
            n_p = max(1, int(math.ceil(bay / float(contraction) - 1e-9)))
            for j in range(1, n_p):
                out.append((a + bay * j / n_p, "contraction"))
    out.sort(key=lambda t: t[0])
    return out


# ===========================================================================
# [4] L-type gutter
# ===========================================================================
def build_gutter_L(kit, prefix, x0, y0, x1, y1, top_z, mtl,
                   width=0.30, thick=0.20, cross_slope=0.06,
                   road_side="left", contraction=6.0, expansion=20.0,
                   groove_w=0.008, expansion_w=0.020, groove_d=0.014,
                   panel_mtl=None, collider=True, jitter=0.0,
                   seed_tag="gutter"):
    """**L-type gutter** - the concrete drainage band running along the carriageway edge.

    Entirely **absent** from the current 33-scene sections
    (`cue_arrangement_survey` §4.3(1)). The real Korean road section order is
    `asphalt -> L-type gutter -> curb (trapezoidal) -> sidewalk block` (same survey
    §3.6), while our scenes go "asphalt -> curb box -> sidewalk" with no gutter.

    ### Dimension basis
    - width **300 / 500**, thickness **200** - National Highway Construction Design
      Practice Guide, 3. Drainage 2), read off the type-1 section drawing `[verified]`
    - **contraction joints every 6 m, expansion joints every 20 m** - same source, the
      note clause `[verified]` (only type-3 uses 12 m expansion). **This joint rhythm is
      the repeating silhouette cue.**
      Actual positions follow the `_bay_joints()` convention: **divide into expansion
      bays first, then split each bay to at most 6 m** (60 m -> uniform 5.0 m panels).
      This avoids the 2 m offcut panel that plain enumeration produces.
    - floor slope 4-10 % -> default 6 % `[estimate - midpoint of the range]`
    - joint groove width and depth are absent from the L-gutter source -> the retaining
      wall contraction joint (6-8 x 12-16 mm) is applied by analogy `[estimate]`

    ### Args
    - `(x0,y0)-(x1,y1)`: the **curb-side edge line** (the low side of the gutter, not
      the high side). The gutter pan extends `width` from here towards `road_side`.
    - `top_z`: **z of the road-side (outer) top edge** - flush with the asphalt.
      The curb-side edge drops to `top_z - width*sin(atan(cross_slope))`.
    - `road_side`: `"left"` (+normal) / `"right"` (-normal) relative to travel direction.
    - **`Kit(obox=...)` is required** because the cross slope always tilts the pan.
      With `cross_slope=0.0` and an axis-parallel segment it works without obox (a flat
      gutter).
    - `jitter`: joint position jitter [m]. Default 0 (real joints are exactly evenly
      spaced - the jitter recommendation in §3.4 concerns **placed objects** such as
      bollards and trees, not construction joints). Use 0.02-0.05 only when poor
      workmanship must be reproduced.

    ### Prim count
    **1** base slab + `ceil(L/6) + (L/20)` panels.
    -> **about 0.18-0.20 prims/m** (a 100 m gutter = 19-21 prims).
    A joint is **not a separate prim but the real gap between panels** (8 mm wide,
    14 mm deep). The base slab top acts as the groove floor, so it is a true recess
    without any boolean subtraction.

    GT: **creates no drop.** The gutter's own step is `width*cross_slope`, about 18 mm
        (width 300) to 30 mm (width 500), below the minor-step threshold (0.10 m).
        **However**, placing this in front of a curb increases the curb exposure by the
        same amount -> **recompute** as
        `curb GT drop = curb_h + width*cross_slope`.
        (Just use the returned `drop_at_curb`.)

    Returns: dict(base, panels[], joints[(s,kind)], drop_at_curb, z_curb_edge,
               z_road_edge, prim_count)
    """
    if road_side not in ("left", "right"):
        raise ValueError("road_side 는 'left' 또는 'right'.")
    if width <= 0 or thick <= groove_d:
        raise ValueError("width>0, thick>groove_d 이어야 한다.")

    m0 = kit.mark()
    L, yaw, (ux, uy), (nx, ny) = _line_frame(x0, y0, x1, y1)
    side = 1.0 if road_side == "left" else -1.0
    off = side * width / 2.0                    # Curb line -> pan centre line

    t = math.atan(float(cross_slope))           # Cross slope angle
    # Local +Y rising is rotX(+). The road side must be higher, so:
    #   road_side='left'  -> road = local +Y -> rotx = +t
    #   road_side='right' -> road = local -Y -> rotx = -t
    rotx = math.degrees(t) * side
    dz_half = (width / 2.0) * abs(math.sin(t))
    z_top_center = float(top_z) - dz_half       # z of the pan top centre
    z_road_edge = float(top_z)
    z_curb_edge = float(top_z) - width * abs(math.sin(t))
    cos_t = math.cos(t)

    # -- Joint positions (arc length s from the curb line start) - see the `_bay_joints` convention --
    joints = _bay_joints(L, expansion, contraction)
    if jitter and jitter > 0.0:
        jj = []
        for s, k in joints:
            r = det_rng(seed_tag, prefix, s, k)
            jj.append((min(max(s + r.uniform(-jitter, jitter), 0.05), L - 0.05), k))
        joints = sorted(jj, key=lambda q: q[0])

    def _center(s_mid):
        px = float(x0) + ux * s_mid + nx * off
        py = float(y0) + uy * s_mid + ny * off
        return px, py

    # -- One base slab (top = joint groove floor) ------------------------
    base_t = float(thick) - float(groove_d)
    bx, by = _center(L / 2.0)
    base_top = z_top_center - groove_d
    kit.B(f"{prefix}/Base", (bx, by, base_top - base_t / 2.0 * cos_t),
          (L, width, base_t), mtl, rotz=yaw, rotx=rotx, col=collider)

    # -- Panels (between joints) - the gap between panels is the joint groove --
    panel_mtl = mtl if panel_mtl is None else panel_mtl
    bounds = [0.0] + [s for s, _ in joints] + [L]
    kinds = ["end"] + [k for _, k in joints] + ["end"]
    panels = []
    for i in range(len(bounds) - 1):
        a, b = bounds[i], bounds[i + 1]
        wa = 0.0 if kinds[i] == "end" else (
            expansion_w if kinds[i] == "expansion" else groove_w)
        wb = 0.0 if kinds[i + 1] == "end" else (
            expansion_w if kinds[i + 1] == "expansion" else groove_w)
        pa, pb = a + wa / 2.0, b - wb / 2.0
        plen = pb - pa
        if plen <= 0.02:                       # Skip excessively short fragments
            continue
        px, py = _center((pa + pb) / 2.0)
        path = f"{prefix}/Panel_{i:02d}"
        kit.B(path, (px, py, z_top_center - groove_d / 2.0 * cos_t),
              (plen, width, groove_d), panel_mtl, rotz=yaw, rotx=rotx,
              col=False)                        # Thin panels need no collider
        panels.append(path)

    return dict(base=f"{prefix}/Base", panels=panels, joints=joints,
                length=L, yaw_deg=yaw,
                drop_at_curb=width * abs(math.sin(t)),
                z_curb_edge=z_curb_edge, z_road_edge=z_road_edge,
                prim_count=kit.count_since(m0))


# ===========================================================================
# [5] Gully - placement rule + body
# ===========================================================================
def gully_positions(x0, x1, spacing=22.0, sag_points=(), curve_points=(),
                    max_spacing=25.0, jitter=0.0, seed_tag="gully",
                    with_kind=False):
    """Implements the **gully placement rule**. Returns a list of coordinates.

    National Highway Construction Design Practice Guide, 3. Drainage (quantity
    take-off), item pa, verbatim `[verified]`:

    > Rainwater inlets shall **always be installed at downgrade inflection points,
    > concave areas where rainwater collects, and at the start and end of road corner
    > curves** so that surface water is collected smoothly; **on straight sections they
    > are installed at 20-25 m intervals**.

    So the rule has two layers.
      (1) **Mandatory points** - `sag_points` (sags and downgrade inflections) plus
         `curve_points` (curve start/end). One is always placed here.
      (2) **Straight-section interpolation** - fill between mandatory points without
         exceeding 20-25 m.

    (Note: the sewerage facility standards family says 10-30 m along the curb line -
     `cue_arrangement_survey` §1.2. The road design guide's 20-25 m is the tighter
     range, so it was adopted. For a denser 10 m class spacing, pass
     `spacing=12.0, max_spacing=15.0` explicitly.)

    - `spacing`: target spacing (default 22 = the midpoint of 20-25)
    - `max_spacing`: **absolute limit** (default 25). If interpolation exceeds it, the
      count is increased.
    - `jitter`: deterministic jitter [m] applied only to interpolated straight-section
      points. Mandatory points are not moved (they are functional). Default 0.
    - `with_kind=True`: returns `[(x, "sag"|"curve"|"straight"), ...]`.

    0 prims (coordinates only). GT: not applicable.
    """
    a, b = (float(x0), float(x1)) if x1 >= x0 else (float(x1), float(x0))
    span = b - a
    if span <= 1e-6:
        return []
    if spacing <= 0 or max_spacing <= 0:
        raise ValueError("spacing / max_spacing 는 양수여야 한다.")

    anchors = []
    for p in sag_points:
        if a - 1e-6 <= p <= b + 1e-6:
            anchors.append((float(p), "sag"))
    for p in curve_points:
        if a - 1e-6 <= p <= b + 1e-6:
            if all(abs(p - q) > 1e-6 for q, _ in anchors):
                anchors.append((float(p), "curve"))
    anchors.sort(key=lambda t: t[0])

    out = list(anchors)
    bounds = [a] + [p for p, _ in anchors] + [b]
    for i in range(len(bounds) - 1):
        s0, s1 = bounds[i], bounds[i + 1]
        seg = s1 - s0
        if seg <= 1e-6:
            continue
        n = max(0, int(round(seg / spacing)) - 1)
        while seg / (n + 1) > max_spacing + 1e-9:
            n += 1
        for k in range(n):
            x = s0 + seg * (k + 1) / (n + 1)
            if jitter and jitter > 0.0:
                r = det_rng(seed_tag, x, i, k)
                x = min(max(x + r.uniform(-jitter, jitter), a), b)
            out.append((x, "straight"))

    out.sort(key=lambda t: t[0])
    return out if with_kind else [p for p, _ in out]


def _ring4(kit, prefix, cx, cy, z_top, inner_x, inner_y, w, t, mtl,
           yaw_deg=0.0, col=False):
    """A **4-sided ring** around the opening (4 prims). A solid slab would seal the
    opening, so the uncovered and slat modes must use this ring. Local X=`across`, Y=`along`."""
    a = math.radians(float(yaw_deg))
    ca, sa = math.cos(a), math.sin(a)
    ox, oy = (inner_x + w) / 2.0, (inner_y + w) / 2.0
    specs = (("Xn", -ox, 0.0, w, inner_y + 2 * w),
             ("Xp", +ox, 0.0, w, inner_y + 2 * w),
             ("Yn", 0.0, -oy, inner_x, w),
             ("Yp", 0.0, +oy, inner_x, w))
    out = []
    for tag, lx, ly, sx, sy in specs:
        wx = float(cx) + lx * ca - ly * sa
        wy = float(cy) + lx * sa + ly * ca
        p = f"{prefix}/Frame_{tag}"
        kit.B(p, (wx, wy, float(z_top) - float(t) / 2.0), (sx, sy, float(t)),
              mtl, rotz=float(yaw_deg), col=col)
        out.append(p)
    return out


def build_gully(kit, prefix, cx, cy, top_z, grate_mtl, pit_mtl=None,
                frame_mtl=None, along=0.50, across=0.40, grate_t=0.05,
                body_along=0.510, body_across=0.410, body_h=0.640,
                yaw_deg=0.0, lid=True, frame=True, frame_w=0.06,
                slats=0, wall_t=0.05, seat=0.002, collider=True):
    """**Gully (rainwater inlet) + grating.**

    ### Dimension basis
    - **grating 400 x 500 x 50** - National Highway Construction Design Practice Guide
      bill of quantities, "steel grating for catch basin" `[verified]`. For the long
      400x995x50 type use `along=0.995`.
    - **body 410 x 510 x H640** - the value used in the trade. **Not verified against a
      primary source `[estimate]`.**
      (Survey §3.3: gully bodies of 40x50/40x100/40x150 cm appear only in secondary
      material and are unverified `[unverified]`. So an **inner width of 400** was
      back-computed from the 400 grating, plus wall thickness, giving 410x510.
      "Road Drainage Facility Design and Management Guideline 2025.02" is likely the
      primary basis but could not be obtained - survey §9, blocked path.)
    - For placement see `gully_positions()`.

    ### Placement rule (the caller's responsibility, noted here for reference)
    **Just inside the curb (road side)**. When used together with an L-type gutter it
    sits inside the gutter pan. The `along` axis is parallel to the curb line (use
    `yaw_deg` to match the curb bearing).

    ### Three modes and prim counts
    | mode | composition | prims |
    |---|---|---|
    | `lid=True, slats=0` **(default)** | 1 solid frame + 1 solid grating | **2** |
    | `lid=True, slats=n` (close view) | 1 pit + 4 frame ring + n slats | **5+n** |
    | `lid=False` (uncovered) | 4 pit walls + 1 floor + 4 frame ring | **9** |

    Why the default mode builds no pit: the solid grating covers it, so it is **never
    visible**. Even one prim is not free. The grid pattern comes from the material
    (normal/albedo).
    In slat mode the frame is a **4-sided ring rather than a solid slab** - a solid slab
    would seal the space below the slots and the grid would not read as dark.
    `seat=0.002`: the frame top sits 2 mm below the grating. Putting both faces at the
    same z causes **coplanar z-fighting** (and real products seat the lid inside the
    frame, so it is physically right too).

    GT: `lid=True` -> **not a drop** (flush with the paving; Accessibility Act annex 1
        1-(d)(3) "the same height as the approach route"). `lid=False` -> **drop =
        `body_h` (0.64 m)** and is a GT label target. Uncovered mode builds a **genuinely
        open box** from 4 walls plus a floor, so the drop geometry is real. Uncovered
        gullies do exist (survey §1.3g: "many gutters are installed with no cover and the
        floor fully exposed") but should be the exception in urban scenes.
    """
    m0 = kit.mark()
    z = float(top_z)
    pmtl = pit_mtl if pit_mtl is not None else grate_mtl
    fmtl = frame_mtl if frame_mtl is not None else grate_mtl
    prims = {}

    if lid and not slats:
        # -- Default: solid frame (2 mm lower) + solid grating (flush) ------
        if frame:
            prims["frame"] = f"{prefix}/Frame"
            kit.B(prims["frame"],
                  (float(cx), float(cy),
                   z - seat - (grate_t + 0.03) / 2.0),
                  (across + 2 * frame_w, along + 2 * frame_w, grate_t + 0.03),
                  fmtl, rotz=yaw_deg, col=collider)
        prims["grate"] = f"{prefix}/Grate"
        kit.B(prims["grate"], (float(cx), float(cy), z - grate_t / 2.0),
              (across, along, grate_t), grate_mtl, rotz=yaw_deg, col=collider)

    elif lid:
        # -- Slat mode: the pit must be visible, so the frame is a ring ------
        prims["pit"] = f"{prefix}/Pit"
        kit.B(prims["pit"],
              (float(cx), float(cy), z - grate_t - body_h / 2.0),
              (body_across, body_along, body_h), pmtl, rotz=yaw_deg, col=False)
        if frame:
            prims["frame"] = _ring4(kit, prefix, cx, cy, z - seat,
                                    across, along, frame_w, grate_t + 0.03,
                                    fmtl, yaw_deg, collider)
        bar_w = across / (2.0 * int(slats) + 1.0)      # Slat width = slot width
        a = math.radians(float(yaw_deg))
        bars = []
        for i in range(int(slats)):
            u = -across / 2.0 + bar_w * (2 * i + 1.5)
            p = f"{prefix}/Slat_{i:02d}"
            kit.B(p, (cx + u * math.cos(a), cy + u * math.sin(a),
                      z - grate_t / 2.0),
                  (bar_w, along, grate_t), grate_mtl, rotz=yaw_deg, col=False)
            bars.append(p)
        prims["slats"] = bars

    else:
        # -- Uncovered: a genuinely open box (4 walls + 1 floor) ------------
        a = math.radians(float(yaw_deg))
        ca, sa = math.cos(a), math.sin(a)
        ox = (body_across + wall_t) / 2.0
        oy = (body_along + wall_t) / 2.0
        walls = []
        for tag, lx, ly, sx, sy in (
                ("Xn", -ox, 0.0, wall_t, body_along + 2 * wall_t),
                ("Xp", +ox, 0.0, wall_t, body_along + 2 * wall_t),
                ("Yn", 0.0, -oy, body_across, wall_t),
                ("Yp", 0.0, +oy, body_across, wall_t)):
            p = f"{prefix}/Wall_{tag}"
            kit.B(p, (cx + lx * ca - ly * sa, cy + lx * sa + ly * ca,
                      z - body_h / 2.0), (sx, sy, body_h), pmtl,
                  rotz=yaw_deg, col=collider)
            walls.append(p)
        prims["walls"] = walls
        prims["floor"] = f"{prefix}/Floor"
        kit.B(prims["floor"], (float(cx), float(cy), z - body_h - wall_t / 2.0),
              (body_across + 2 * wall_t, body_along + 2 * wall_t, wall_t),
              pmtl, rotz=yaw_deg, col=collider)
        if frame:
            prims["frame"] = _ring4(kit, prefix, cx, cy, z, across, along,
                                    frame_w, grate_t + 0.03, fmtl, yaw_deg,
                                    collider)

    return dict(prims=prims, gt_drop=(0.0 if lid else float(body_h)),
                is_gt_hazard=(not lid), prim_count=kit.count_since(m0))


# ===========================================================================
# [6] Manhole
# ===========================================================================
def build_manhole(kit, prefix, cx, cy, top_z, lid_mtl, frame_mtl=None,
                  d_frame=0.648, d_lid=None, frame_w=0.045, thick=0.110,
                  lid_t=0.055, flush_tol=0.010, proud=None, seat=0.002,
                  lid=True, pit_depth=1.20, pit_mtl=None, boss=False,
                  collider=True, seed_tag="manhole"):
    """**Manhole cover + frame.** Common to carriageway and sidewalk.

    ### Dimension basis and a **notice of conflict between documents**
    - `_dimension_index.md`: "manhole cover **frame outer diameter 648** (carriageway
      and sidewalk alike) / 766 / 918, thickness 110t - KS D 4040 certified product"
      `[verified]`
    - `korean_pedestrian_geometry.md` §3.2: the highway practice-guide bill of
      quantities says "manhole cover, carriageway type **grey cast iron d648**, sidewalk
      type coloured d648", and the same document adds "about **d760-780** including the
      frame outline `[estimate]`".
    -> So **the two documents disagree on whether 648 is the cover or the frame outer
      diameter.** This function takes the index reading (**frame outer diameter 648**) as
      the default and derives the cover as `d_frame - 2*frame_w` (= d558). To use the
      reading where 648 is the **cover**, call explicitly with
      `build_manhole(..., d_frame=0.765, d_lid=0.648)`.
      `frame_w=0.045` is `[estimate]` (no source for the frame ring width).
    - thickness **110t** `[verified]`. `lid_t` is the cover-only thickness `[estimate]`.
    - optional diameters: **766 / 918** `[verified]`.

    ### flush
    "Level with the road surface, +-10 mm". With `proud=None` a coordinate-seeded
    deterministic draw of `U(-flush_tol, +flush_tol)` is used - if many covers sit at
    exactly the same height, the result reads as CG (survey §3.1, construction
    tolerance).

    `seat=0.002`: the frame top sits 2 mm below the cover. At the same z the two discs
    produce **coplanar z-fighting** (and real covers rest on the frame ledge, so it is
    physically right too).

    ### Prim count
    Default **2** (1 frame + 1 cover). `boss=True` -> 3. `lid=False` -> **1**.
    One manhole = 1-2 circular discs. Survey §7 P1-7 rates it "the best effect for the
    cost".

    ### `lid=False` is an **approximation** - read before use
    A Cube/Cylinder combination **cannot cut a circular through-hole** (no subtraction).
    This mode places only one **dark cylinder** whose top is `top_z` (an approximation
    of the void). From above it reads as an open manhole, but **at grazing angles (the
    h0.3 robot viewpoint) it reads as a flat disc.** If a real opening carrying a drop
    label is needed, either (1) use `build_gully(lid=False)` if a rectangular shape is
    acceptable (4 walls + floor = a genuinely open box), or (2) have the caller split the
    paving slab around the opening and use this cylinder as the vertical wall face.
    sceneD2 (floor opening) is a precedent for the latter.

    GT: `lid=True` -> **not a drop** (+-10 mm is below the 0.10 m minor-step threshold).
        `lid=False` -> **drop = `pit_depth`** and is a GT label target (reproducing an
        unguarded opening per Industrial Safety Rules §43). Confirm the approximation
        limits above before use. The default is closed.
    """
    m0 = kit.mark()
    if proud is None:
        proud = det_rng(seed_tag, prefix, cx, cy).uniform(-flush_tol, flush_tol)
    proud = float(proud)
    if d_lid is None:
        d_lid = max(0.05, float(d_frame) - 2.0 * float(frame_w))
    z0 = float(top_z) + proud
    prims = {}

    # [W2 fix batch F5] Frame / lid / boss go through `kit.D` (n-gon prism, 32 segments)
    #   instead of `kit.C` (analytic cylinder). Defect D4 - "polygonal manholes" - was
    #   never a modelling choice: an analytic `UsdGeom.Cylinder` is tessellated by Hydra
    #   at its own low default, which reads as an octagon / 12-gon at d2-d5. Same prim
    #   count, same dimensions, same GT; only the silhouette changes. The pit keeps a
    #   cylinder - it is a hole below the surface, never seen in silhouette.
    if lid:
        # Frame (ring) - thickness 110t. Its top is `seat` below the cover (avoids z-fighting).
        prims["frame"] = f"{prefix}/Frame"
        kit.D(prims["frame"],
              (float(cx), float(cy), z0 - float(seat) - float(thick) / 2.0),
              float(d_frame) / 2.0, float(thick),
              frame_mtl if frame_mtl is not None else lid_mtl, col=collider)
        prims["lid"] = f"{prefix}/Lid"
        kit.D(prims["lid"], (float(cx), float(cy), z0 - float(lid_t) / 2.0),
              float(d_lid) / 2.0, float(lid_t), lid_mtl, col=collider)
        if boss:
            # Central lifting boss - the minimum feature that stops the cover reading as a plain plate up close.
            prims["boss"] = f"{prefix}/Boss"
            kit.D(prims["boss"], (float(cx), float(cy), z0 + 0.004),
                  0.045, 0.010, lid_mtl, col=False)
    else:
        # Uncovered approximation - top = road surface. No frame, since a frame would cover the hole again.
        prims["pit"] = f"{prefix}/Pit"
        kit.C(prims["pit"],
              (float(cx), float(cy), z0 - float(pit_depth) / 2.0),
              float(d_lid) / 2.0, float(pit_depth),
              pit_mtl if pit_mtl is not None else lid_mtl, col=False)

    return dict(prims=prims, proud=proud, d_lid=float(d_lid),
                gt_drop=(0.0 if lid else float(pit_depth)),
                is_gt_hazard=(not lid), prim_count=kit.count_since(m0))


# ===========================================================================
# [7] Parking ramp side curbs  * required by scene13
# ===========================================================================
def build_ramp_curb(kit, prefix, profile, y_neg, y_pos, mtl,
                    height=0.12, width=0.30, sides="both", embed=0.10,
                    margin=0.0, collider=True, seg_len=None,
                    z_fn=None):
    """**Curbs on both sides of a parking entry ramp.** The part missing from scene13, and
    a general-purpose function.

    ### Statutory basis `[verified]`
    **Parking Lot Act Enforcement Rules Article 6(1)5(c)** - a ramp must have
    **curbs 10-15 cm high at least 30 cm from each wall face**, and **the curb portion is
    deemed included in the carriageway width**.
    (`cue_arrangement_survey` §1.3(c) / §4.5 priority 12)

    -> The standard reading that satisfies the rule is therefore a curb set against the
      wall whose **carriageway-side face is 30 cm from the wall**. Hence `width` defaults
      to **0.30** and the curb is placed touching the wall. To stand it off the wall,
      reduce `width` and adjust `y_neg/y_pos` directly.

    ### Why it matters (direct research impact)
    scene13 matched the ramp gradients (17 % / 8.5 % transition) exactly to the statutory
    values yet **omitted this curb entirely**. That is not cosmetics: **a drop line that
    should exist inside the ramp is missing**. From the carriageway to the curb top is
    0.10-0.15 m - right at the minor-step threshold, the most confusing size from a low
    viewpoint.

    ### Args
    - `profile`: `[(x0, z0, run, drop), ...]` - **exactly the return format of scene13
      `ramp_profile()`**. `z0` is the **road surface z** at the segment start, descending
      by `drop` towards `+X`.
    - `y_neg`, `y_pos`: y of the **inner wall faces** on each side (-Y and +Y).
    - `sides`: `"both" | "neg" | "pos"`.
    - `embed`: how deep the curb is buried below the road surface (clearance from the
      slab / z-fighting prevention).
    - `seg_len`, `z_fn`: the **fallback** when `kit.slope` is absent. Given `z_fn(x)->z`,
      the curb is approximated by stepped boxes of `seg_len` (default 1.0 m). Prims grow
      a lot in that case, so injecting `kit.slope` is recommended.

    ### Prim count
    With `kit.slope`: **segments x sides** = 3 x 2 = **6** for scene13.
    With the fallback: `(length/seg_len) x sides` (a 30 m ramp at 1 m = 60) - ten times more.

    GT: **creates a new drop line.** Curb top -> ramp road surface = `height`
        (0.10-0.15 m). It is a **continuous linear drop** running the whole ramp and is a
        separate label from the slope drop of the ramp surface itself. scene13's GT must
        be regenerated.
    """
    if sides not in ("both", "neg", "pos"):
        raise ValueError("sides 는 'both' | 'neg' | 'pos'.")
    if not (0.09 <= height <= 0.16):
        raise ValueError(
            f"ramp_curb height={height} 는 법정 10~15 cm 범위 밖이다. "
            "의도적 규정 미달이면 이 검사를 우회하지 말고 씬 주석에 명시하라.")
    m0 = kit.mark()

    lanes = []
    if sides in ("both", "neg"):
        lanes.append(("N", float(y_neg), float(y_neg) + float(width)))
    if sides in ("both", "pos"):
        lanes.append(("P", float(y_pos) - float(width), float(y_pos)))

    paths = []
    thick = float(height) + float(embed)
    use_slope = kit.slope is not None
    for tag, ya, yb in lanes:
        if use_slope:
            for i, (sx, sz, run, drop) in enumerate(profile, 1):
                p = f"{prefix}/Curb_{tag}{i}"
                # build_slope takes the 'top plane' from (x0,z0) to (x0+run, z0-drop) and
                # gives it `thick` of thickness downwards. Curb top = road surface + height.
                kit.S(p, float(sx), float(sz) + float(height),
                      float(run), float(drop), ya, yb, thick, mtl,
                      margin=margin, col=collider)
                paths.append(p)
        else:
            if z_fn is None:
                raise ValueError(
                    "kit.slope 도 z_fn 도 없다. scene_common.build_slope 를 "
                    "Kit(slope=...) 로 주입하거나 z_fn 을 넘겨라.")
            step = float(seg_len or 1.0)
            xa = float(profile[0][0])
            xb = float(profile[-1][0]) + float(profile[-1][2])
            n = max(1, int(math.ceil((xb - xa) / step)))
            for i in range(n):
                x_a = xa + step * i
                x_b = min(xa + step * (i + 1), xb)
                zc = 0.5 * (z_fn(x_a) + z_fn(x_b))
                p = f"{prefix}/Curb_{tag}{i:03d}"
                kit.B(p, ((x_a + x_b) / 2.0, (ya + yb) / 2.0,
                          zc + height - thick / 2.0),
                      (x_b - x_a, yb - ya, thick), mtl, col=collider)
                paths.append(p)

    return dict(prims=paths, gt_drop=float(height), is_gt_hazard=True,
                sides=[t for t, _, _ in lanes], prim_count=kit.count_since(m0))


# ===========================================================================
# [8] Road markings - scale anchors
# ===========================================================================
def build_road_marking(kit, prefix, kind, mtl, x0, y0, z=0.0,
                       yaw_deg=0.0, proud=0.003, collider=False,
                       # kind="parking"
                       n=1, stall_w=2.50, stall_l=5.00, line_w=0.15,
                       closed=False,
                       # kind="crosswalk"
                       band_w=4.00, walk_len=8.00,
                       stripe_w=0.45, gap_w=0.45,
                       # kind="line"
                       length=3.00):
    """**Road markings** - parking stalls / crosswalk / plain lines.

    ### Why this passes v5.2 §6 ("empty is the default")
    The point raised in `scene_composition_audit.md` §(5)(6): the README names
    **"scale anchors"** as a context cue, yet **the dataset contains zero anchors**. The
    model has no reference by which to fix size. And road markings are not decoration but
    **functionally mandatory** (a parking lot with no stall lines, or a crosswalk with no
    paint, does not exist). The same audit concluded that "adding just the four items -
    stall paint, crosswalk paint, doors and manholes - catches half of all scale
    misreadings".

    ### Dimension basis
    - **parking stall 2.50 x 5.00 m** (extended 2.60 x 5.20) - Parking Lot Act
      Enforcement Rules §3 `[verified, statutory]` (`korean_urban_backdrop` dimension
      table)
    - **crosswalk stripe 45 cm wide, 45 cm gap** - Road Traffic Act Enforcement Rules
      annex 6, road markings `[verified]` (`scene_composition_audit` §(6) anchor table)
    - the solid line width `line_w=0.15` is **`[estimate]`** (typically 10-15 cm, not
      source-verified).
    - the paint thickness `proud=0.003` is **`[estimate]`** (unregulated). Keep it at or
      below 4 mm - above that a minor-step argument arises.

    ### Geometry convention
    In the local frame `+X` is the "length direction" and `+Y` the "width direction"; the
    whole thing is rotated by `yaw_deg` about `(x0,y0)`.
    - `parking`: `(x0,y0)` = the **inner corner of the first stall** in the row. Stalls
      run `n` deep along +X and the depth (`stall_l`) is along +Y. `n+1` dividing lines +
      1 inner end line (+ 1 outer end line if `closed=True`).
    - `crosswalk`: `(x0,y0)` = the starting corner of the band. Total width along travel
      (+X) is `band_w`; the crossing length (+Y) is `walk_len`. Stripes lie long along +Y.
    - `line`: a single line of `length` along +X from `(x0,y0)`, `line_w` wide.

    ### Prim count
    - `parking`: **n + 2** (n + 3 when closed). 5 stalls = 7 prims.
    - `crosswalk`: `floor((band_w+gap)/(stripe+gap))` - 4 m wide at 45/45 = **4-5**.
    - `line`: **1**.

    GT: **not a drop** (paint thickness <=4 mm). A pure scale anchor plus a linear cue.
    """
    m0 = kit.mark()
    a = math.radians(float(yaw_deg))
    ca, sa = math.cos(a), math.sin(a)
    zc = float(z) + float(proud) / 2.0

    def put(tag, lx, ly, sx, sy):
        """Local centre (lx,ly) and size (sx,sy) -> rotated placement."""
        wx = float(x0) + lx * ca - ly * sa
        wy = float(y0) + lx * sa + ly * ca
        p = f"{prefix}/{tag}"
        kit.B(p, (wx, wy, zc), (sx, sy, float(proud)), mtl,
              rotz=float(yaw_deg), col=collider)
        return p

    paths = []
    if kind == "parking":
        n = int(n)
        if n < 1:
            raise ValueError("parking: n >= 1")
        total = n * float(stall_w)
        for i in range(n + 1):                       # Dividing lines (stall boundaries)
            paths.append(put(f"Div_{i:02d}", i * stall_w, stall_l / 2.0,
                             line_w, stall_l))
        paths.append(put("Back", total / 2.0, stall_l, total, line_w))
        if closed:
            paths.append(put("Front", total / 2.0, 0.0, total, line_w))
        info = dict(n_stall=n, stall=(float(stall_w), float(stall_l)))

    elif kind == "crosswalk":
        pitch = float(stripe_w) + float(gap_w)
        n_s = int(math.floor((float(band_w) + float(gap_w)) / pitch + 1e-9))
        if n_s < 1:
            raise ValueError("crosswalk: band_w 가 스트라이프 1개보다 좁다.")
        # Distribute the leftover evenly at both ends -> the band is not biased to one side.
        used = n_s * pitch - float(gap_w)
        pad = (float(band_w) - used) / 2.0
        for i in range(n_s):
            lx = pad + stripe_w / 2.0 + i * pitch
            paths.append(put(f"Stripe_{i:02d}", lx, walk_len / 2.0,
                             stripe_w, walk_len))
        info = dict(n_stripe=n_s, pitch=pitch, walk_len=float(walk_len))

    elif kind == "line":
        paths.append(put("Line", float(length) / 2.0, 0.0,
                         float(length), float(line_w)))
        info = dict(length=float(length), width=float(line_w))

    else:
        raise ValueError("kind 는 'parking' | 'crosswalk' | 'line'.")

    return dict(prims=paths, kind=kind, gt_drop=0.0, is_gt_hazard=False,
                prim_count=kit.count_since(m0), **info)


# ===========================================================================
# [9] Retaining wall detail
# ===========================================================================
def wall_joint_positions(length, wall_type="cantilever", contraction=9.0):
    """Compute retaining wall joint positions. Returns `(contraction[], expansion[])` in
    metres from the wall start.

    Road Design Guide vol. 3, part 8-7, retaining walls, 6. Structural details
    `[verified]`:
      - **contraction joint** groove 6-8 mm wide, 12-16 mm deep, spaced **<=9 m**
      - **expansion joint** gravity type **<=10 m** / cantilever and counterfort
        **15-20 m**; **reinforcement is interrupted** at an expansion joint -> a slit
        through the full section

    `wall_type`: `"gravity"` (10 m) | `"cantilever"` (17.5 m = midpoint of 15-20) |
    `"counterfort"` (same spacing as cantilever; note the source states that counterfort
    walls have plenty of horizontal reinforcement and **may omit contraction joints** ->
    pass 0 for `contraction`).

    Positions follow the `_bay_joints()` convention (split into expansion bays, then split
    within each bay). Every rule is "at most", so an even split always satisfies it and no
    offcut panel appears. L20 cantilever -> expansion [10.0], contraction [5.0, 15.0].

    0 prims. GT: not applicable.
    """
    exp_pitch = {"gravity": 10.0,
                 "cantilever": 17.5,
                 "counterfort": 17.5}.get(wall_type)
    if exp_pitch is None:
        raise ValueError("wall_type 은 'gravity'|'cantilever'|'counterfort'.")
    js = _bay_joints(length, exp_pitch, contraction)
    con = [s for s, k in js if k == "contraction"]
    exp = [s for s, k in js if k == "expansion"]
    return con, exp


def build_retaining_wall_details(kit, prefix, x0, x1, face_y, z_ground, z_top,
                                 mtl_dark, mtl_cope=None,
                                 axis="x", normal_sign=1.0, wall_t=0.35,
                                 weep_d=0.100, weep_mode="linear",
                                 weep_spacing=4.0, weep_area=3.0,
                                 weep_z=0.35, weep_depth=0.12,
                                 wall_type="cantilever", contraction=9.0,
                                 groove_w=0.007, groove_d=0.014,
                                 expansion_w=0.020, joints=True,
                                 coping=True, cope_h=0.10, cope_over=0.04,
                                 cope_flush=True, stain=False,
                                 stain_h=0.60, stain_w=0.09,
                                 collider=False, seed_tag="rwall"):
    """**Retaining wall detail** - weep holes, expansion/contraction joints, coping. It does
    not build the wall body itself.

    The retaining walls in the current 33 scenes are **blank walls**. The visual identity
    of a real Korean retaining wall comes from three things: (1) the regular row of weep
    holes, (2) the **vertical rhythm** created by the joints, and (3) efflorescence and
    rust streaks running down below the weep holes
    (`korean_pedestrian_geometry` §4.1-4.2).

    ### Dimension basis
    - **weep hole d100 mm at about 4 m spacing**, at least one between counterforts -
      Road Design Guide vol. 3 part 8-7, retaining walls 6 `[verified]`
    - alternative: **at least one per 3 m2** - Building Act Enforcement Rules §25
      `[verified]`. That is `weep_mode="grid"`. Solved as a square grid the pitch is
      sqrt(3) ~= **1.73 m** `[estimate - the grid form is not specified]`
    - weep hole **height above ground 300-500 mm** `[estimate]` (no source - survey §8
      list, item 13)
    - **contraction joint** groove 6-8 x 12-16 mm deep, **<=9 m** `[verified]`
    - **expansion joint** gravity <=10 m / cantilever 15-20 m `[verified]`
    - **coping overhang 30-50 mm each side** `[estimate]` (the absence of a domestic rule
      was confirmed)

    ### How joints are expressed - without a prim explosion
    - **contraction joint (6-8 mm)**: a **dark strip standing 1 mm proud** of the wall
      face. Cutting a 6 mm recess in a pipeline without booleans would require splitting
      the wall, and that costs more than the effect is worth. At medium and long range the
      strip reads exactly like a groove: a **dark vertical line**. Up close at grazing
      angles it may read as a raised strip, so for close-range scenes switch it off with
      `joints=False` and handle it in the normal map (the original survey also judged that
      "a normal map is enough for the contraction joint").
    - **expansion joint (through the full section)**: the original survey explicitly asked
      for the **wall to be segmented in geometry**. This function does not build the wall,
      so it **only returns positions** (`wall_joint_positions()`). The caller splits the
      wall panels at those positions, and the 20 mm dark strip this function places in the
      gap completes it.

    ### Args
    - `axis="x"`: the wall runs along X and the exposed face normal is
      `normal_sign * (+Y)`. With `axis="y"` the wall runs along Y and the normal is
      `normal_sign * (+X)`.
      (Only axis-parallel walls are supported - `add_cylinder` takes no rotZ, so a
      horizontal cylinder at an arbitrary bearing cannot be made. Call skewed retaining
      walls inside a rotation group.)
    - `face_y`: coordinate of the exposed face (y when axis="x", x when axis="y").
    - `wall_t`: wall thickness. Used only to compute the coping width.
    - `cope_flush=True`: **coping top = `z_top`** (assuming the wall body is built `cope_h`
      lower). The GT drop does not change - **the default**.
      With `False` the coping sits on top of `z_top` and **the drop grows by `cope_h`**.
    - `stain`: efflorescence/rust marks below the weep holes (dark vertical bands).
      Survey §4.2 calls this "a powerful RGB context cue on the wall right above the drop".
      OFF by default (the look layer is the better place, and enabling it adds one prim per
      weep hole).

    ### Prim count
    `weep_mode="linear"`: `L/4` weep holes (+ the same again with `stain`).
    `weep_mode="grid"`  : `(L/1.73) x (H_eff/1.73)` - **it grows fast.**
                          H 5 m, L 20 m gives 11x2 = 22. Enable only when the 3 m2 rule
                          must be used.
    Joint strips: contraction `L/9` + expansion `L/10-17.5`.
    Coping: **1**.
    -> a standard call for a 20 m, H5 m cantilever wall = 5 + 2 + 1 + 1 = **9 prims**
      (**0.45 prims/m**).

    GT: **creates no drop.** The wall-top drop = `z_top - front ground z` already exists
        and this function merely decorates that face. **However**, with `cope_flush=False`
        the top rises by `cope_h` and **the GT drop increases** - check the returned
        `gt_delta` and update the scene GT.
        Note: there is **no statutory obligation for a fall-protection guardrail** on top
        of a retaining wall (`cue_arrangement_survey` §1.3(d)) - which is why no guardrail
        is attached automatically.
    """
    if axis not in ("x", "y"):
        raise ValueError("axis 는 'x' 또는 'y'.")
    if z_top <= z_ground:
        raise ValueError("z_top > z_ground 이어야 한다.")
    m0 = kit.mark()
    ns = 1.0 if float(normal_sign) >= 0 else -1.0
    a, b = (float(x0), float(x1)) if x1 >= x0 else (float(x1), float(x0))
    L = b - a
    H = float(z_top) - float(z_ground)
    fy = float(face_y)

    def place(tag, s, zc, size_along, size_out, size_up, mtl,
              out_center=None, col=False):
        """Wall coordinates (s along the wall, out along the normal, up=z) -> world placement."""
        oc = fy + ns * (0.001 - size_out / 2.0) if out_center is None else out_center
        if axis == "x":
            c = (a + s, oc, zc)
            sz = (size_along, size_out, size_up)
        else:
            c = (oc, a + s, zc)
            sz = (size_out, size_along, size_up)
        p = f"{prefix}/{tag}"
        kit.B(p, c, sz, mtl, col=col)
        return p

    prims = {"weep": [], "contraction": [], "expansion": [], "stain": []}

    # -- Weep holes ------------------------------------------------------
    r = float(weep_d) / 2.0
    hole_out = fy + ns * (0.001 - float(weep_depth) / 2.0)   # Outer end = face +1 mm
    rotY, rotX = (0.0, 90.0) if axis == "x" else (90.0, 0.0)
    if weep_mode == "linear":
        rows = [float(z_ground) + float(weep_z)]
        pitch = float(weep_spacing)
    elif weep_mode == "grid":
        pitch = math.sqrt(float(weep_area))                  # 3 ㎡ → 1.73 m
        nrow = max(1, int(math.floor((H - float(weep_z)) / pitch)) + 1)
        rows = [float(z_ground) + float(weep_z) + pitch * k for k in range(nrow)
                if float(z_ground) + float(weep_z) + pitch * k < float(z_top) - 0.15]
    else:
        raise ValueError("weep_mode 는 'linear' 또는 'grid'.")

    ncol = max(1, int(math.floor(L / pitch)))
    pad = (L - pitch * (ncol - 1)) / 2.0
    for ri, zc in enumerate(rows):
        for ci in range(ncol):
            s = pad + pitch * ci
            cen = (a + s, hole_out, zc) if axis == "x" else (hole_out, a + s, zc)
            p = f"{prefix}/Weep_{ri}_{ci:02d}"
            kit.C(p, cen, r, float(weep_depth), mtl_dark,
                  rotY=rotY, rotX=rotX, col=False)
            prims["weep"].append(p)
            if stain:
                # Vertical stain below the weep hole - survey §5 [estimate] item 11 (50-200 mm x 0.3-1.5 m)
                jr = det_rng(seed_tag, prefix, s, zc, "stain")
                hh = float(stain_h) * jr.uniform(0.7, 1.3)
                zz = max(float(z_ground) + hh / 2.0, zc - hh / 2.0)
                prims["stain"].append(
                    place(f"Stain_{ri}_{ci:02d}", s, zz,
                          float(stain_w), 0.012, hh, mtl_dark))

    # -- Joints ----------------------------------------------------------
    con, exp = wall_joint_positions(L, wall_type, contraction if joints else 0.0)
    if joints:
        for i, s in enumerate(con):
            prims["contraction"].append(
                place(f"JC_{i:02d}", s, (float(z_ground) + float(z_top)) / 2.0,
                      float(groove_w), max(0.02, float(groove_d)), H, mtl_dark))
        for i, s in enumerate(exp):
            prims["expansion"].append(
                place(f"JE_{i:02d}", s, (float(z_ground) + float(z_top)) / 2.0,
                      float(expansion_w), 0.03, H, mtl_dark))

    # -- Coping ----------------------------------------------------------
    gt_delta = 0.0
    if coping:
        cw = float(wall_t) + 2.0 * float(cope_over)
        zc = (float(z_top) - float(cope_h) / 2.0 if cope_flush
              else float(z_top) + float(cope_h) / 2.0)
        oc = fy - ns * (float(wall_t) / 2.0 - float(cope_over) * 0.0)
        prims["cope"] = place("Cope", L / 2.0, zc, L, cw, float(cope_h),
                              mtl_cope if mtl_cope is not None else mtl_dark,
                              out_center=oc, col=collider)
        if not cope_flush:
            gt_delta = float(cope_h)

    return dict(prims=prims, contraction=con, expansion=exp,
                weep_pitch=pitch, n_weep=len(prims["weep"]),
                gt_drop=H + gt_delta, gt_delta=gt_delta, is_gt_hazard=False,
                prim_count=kit.count_since(m0))


# ===========================================================================
# [10] Tactile paving (dot / bar type)  - note: OFF by default in this project
# ===========================================================================
def build_tactile_pair(kit, prefix, kind, x0, y0, x1, y1, mtl, z=0.0,
                       relief="normal", walk_axis="x", tile=0.300,
                       dot_h=0.006, bar_h=0.005, n_dot=36, n_bar=4,
                       base_t=0.060, collider=False, seed_tag="tactile"):
    """**Dot-type / bar-type tactile paving.**

    ### Warning: do not call by default - the v5.2 convention
    Tactile paving is **OFF by default** in this project (v5.2 §7). The reason is not
    appearance but **real-world frequency** - `cue_arrangement_survey` §2.3 measured that
    a drop with no tactile paving is common, and conversely **most installations exist
    where there is no drop at all** (P(no drop | dot block) = 0.65-0.80 `[estimate]`).
    All 21 main scenes have it switched off via the `cue_tactile` toggle, and as a result
    P(drop | dot block) = 0.375 happens to sit close to the target band (0.20-0.35).
    **This function only provides the capability. Do not call it in a default scene build.**
    Enable it only in the `cue_tactile=True` variant (the cue-removal experiment).

    ### Dimension basis `[verified - Transportation Weak Persons Act Enforcement Rules annex 1]`
    - block **300 x 300**
    - **dot type: 36 dots, dot height 6+-1 mm**
    - **bar type: 4 bars, bar height 5+-1 mm**
    - **yellow** (no colour coordinates are specified `[no source]` -> `TACTILE_YELLOW`
      is `[estimate]`)
    - placement (highway practice guide 7.5 `[verified]`): dot type depth
      **30-90 cm, 60 cm standard** = 2 rows. Bar type 60 cm (2 rows), 30 cm (1 row) for
      continuous straight guidance only.
      Bar direction is **parallel to the direction of travel**.

    ### relief
    - `"normal"` (**default**): no dots are built, just the plate (dots come from the
      normal/albedo map). Same strategy as the existing `scene_common.build_tactile`.
      **1** prim.
    - `"geom"`: real dots.
      - `kind="bar"` -> the ribs are **continuous lines along travel**, so very cheap.
        Prims = `1 + round(width/0.3)*4`. A 0.6 m strip = **9 prims**.
      - `kind="dot"` -> 36 dots per 300 mm tile. A 0.6x3.0 m strip = 2x10 tiles x 36 =
        **721 prims**. Do not use it for more than one close-up location (the function
        returns a warning).

    ### Args
    - `kind`: `"dot"` | `"bar"`
    - `walk_axis`: direction of travel (`"x"`/`"y"`). Bar ribs become parallel to this axis.

    GT: **not a drop** (dots 5-6 mm). It is only a **cue** that creates correlation with
        drops; enabling it shifts the quadrant ratios of §2.5 - recount the conditional
        probabilities before turning it on.
    """
    if kind not in ("dot", "bar"):
        raise ValueError("kind 는 'dot' 또는 'bar'.")
    if relief not in ("normal", "geom"):
        raise ValueError("relief 는 'normal' 또는 'geom'.")
    if walk_axis not in ("x", "y"):
        raise ValueError("walk_axis 는 'x' 또는 'y'.")
    m0 = kit.mark()

    xa, xb = (float(x0), float(x1)) if x1 >= x0 else (float(x1), float(x0))
    ya, yb = (float(y0), float(y1)) if y1 >= y0 else (float(y1), float(y0))
    sx, sy = xb - xa, yb - ya
    if sx <= 0 or sy <= 0:
        raise ValueError("점자블록 밴드의 폭·길이가 0 이다.")
    h = float(dot_h if kind == "dot" else bar_h)
    z_top = float(z) + h
    z_bot = float(z) - float(base_t)

    base = f"{prefix}/Base"
    kit.B(base, ((xa + xb) / 2.0, (ya + yb) / 2.0, (z_top + z_bot) / 2.0),
          (sx, sy, z_top - z_bot), mtl, col=collider)

    warn = None
    nubs = []
    if relief == "geom":
        if kind == "bar":
            # Bar type: ribs run continuously along travel. 4 bars per 300 mm -> pitch 75 mm.
            across = sy if walk_axis == "x" else sx
            n_line = max(1, int(round(across / float(tile)))) * int(n_bar)
            pitch = across / n_line
            bw = pitch * 0.45                       # Rib width ~= 45 % of the pitch [estimate]
            for i in range(n_line):
                u = (pitch * (i + 0.5))
                if walk_axis == "x":
                    c = ((xa + xb) / 2.0, ya + u, z_top - h / 2.0)
                    s = (sx, bw, h)
                else:
                    c = (xa + u, (ya + yb) / 2.0, z_top - h / 2.0)
                    s = (bw, sy, h)
                p = f"{prefix}/Bar_{i:02d}"
                kit.B(p, c, s, mtl, col=False)
                nubs.append(p)
        else:
            # Dot type: 36 dots (6x6) per tile. Prims explode, so a warning is returned.
            g = int(round(math.sqrt(float(n_dot))))     # 6
            ntx = max(1, int(round(sx / float(tile))))
            nty = max(1, int(round(sy / float(tile))))
            est = ntx * nty * g * g
            if est > 400:
                warn = (f"tactile dot geom: 예상 돌기 프림 {est} 개. "
                        "근접뷰 1개소 외에는 relief='normal' 을 쓸 것.")
            tw, th = sx / ntx, sy / nty
            rad = min(tw, th) / float(g) * 0.35        # Dot radius [estimate]
            for ti in range(ntx):
                for tj in range(nty):
                    for i in range(g):
                        for j in range(g):
                            px = xa + tw * (ti + (i + 0.5) / g)
                            py = ya + th * (tj + (j + 0.5) / g)
                            p = f"{prefix}/Dot_{ti}_{tj}_{i}{j}"
                            kit.C(p, (px, py, z_top - h / 2.0), rad, h,
                                  mtl, col=False)
                            nubs.append(p)

    return dict(base=base, nubs=nubs, kind=kind, relief=relief,
                nub_h=h, warning=warn, gt_drop=0.0, is_gt_hazard=False,
                prim_count=kit.count_since(m0), default_enabled=False)


# ===========================================================================
# [11] Self-check - Isaac not required. `python3 infra_kit.py`
# ===========================================================================
def _selfcheck():
    ok = True

    def chk(label, cond, detail=""):
        nonlocal ok
        mark = "OK " if cond else "FAIL"
        if not cond:
            ok = False
        print(f"  [{mark}] {label}{('  — ' + detail) if detail else ''}")

    print("=" * 74)
    print("infra_kit — 기하·프림수 자기검산 (Isaac 부팅 없음)")
    print("=" * 74)

    # -- Determinism -----------------------------------------------------
    print("\n[0] 결정적 RNG")
    s1 = det_seed("a", 1.23456, 7)
    s2 = det_seed("a", 1.23456, 7)
    chk("det_seed 재현", s1 == s2, f"{s1}")
    chk("det_rng 재현",
        det_rng("k", 2.0).random() == det_rng("k", 2.0).random())

    # -- L-type gutter ---------------------------------------------------
    print("\n[1] build_gutter_L — 60 m 직선")
    k = dry_kit()
    g = build_gutter_L(k, "/W/Gutter", 0.0, -4.0, 60.0, -4.0, 0.0, None)
    per_m = g["prim_count"] / g["length"]
    print(f"      프림 {g['prim_count']} / 길이 {g['length']:.1f} m "
          f"= {per_m:.3f} 프림/m")
    print(f"      줄눈 {len(g['joints'])} 개: "
          + ", ".join(f"{s:.0f}({kd[:3]})" for s, kd in g["joints"]))
    chk("줄눈 11개 (신축 2 + 수축 9)", len(g["joints"]) == 11)
    chk("20/40 은 신축이음",
        all(kd == "expansion" for s, kd in g["joints"] if abs(s % 20.0) < 1e-6))
    _pl = [g["joints"][0][0]] + [g["joints"][i + 1][0] - g["joints"][i][0]
                                 for i in range(len(g["joints"]) - 1)]
    chk("패널 전부 5.0 m 균일 (자투리 없음)",
        max(_pl) - min(_pl) < 1e-9 and abs(_pl[0] - 5.0) < 1e-9,
        f"{min(_pl):.2f}~{max(_pl):.2f} m")
    chk("수축 패널 ≤ 6 m 규정", max(_pl) <= 6.0 + 1e-9)
    chk("프림/m ≤ 0.25", per_m <= 0.25, f"{per_m:.3f}")
    chk("연석측 낙차 ≈ 18 mm", abs(g["drop_at_curb"] - 0.0180) < 0.002,
        f"{g['drop_at_curb'] * 1000:.1f} mm")
    chk("연석측 모서리가 차도측보다 낮다", g["z_curb_edge"] < g["z_road_edge"])

    # -- Gully placement -------------------------------------------------
    print("\n[2] gully_positions — 0~100 m, 오목부 37 m, 커브 12·64 m")
    ps = gully_positions(0.0, 100.0, sag_points=(37.0,),
                         curve_points=(12.0, 64.0), with_kind=True)
    print("      " + ", ".join(f"{p:.1f}{kd[0]}" for p, kd in ps))
    xs = [p for p, _ in ps]
    gaps = [xs[i + 1] - xs[i] for i in range(len(xs) - 1)]
    chk("필수 지점 포함", all(v in xs for v in (37.0, 12.0, 64.0)))
    chk("모든 간격 ≤ 25 m", max(gaps) <= 25.0 + 1e-9, f"max {max(gaps):.2f}")
    chk("시작~첫 받이 ≤ 25 m", xs[0] <= 25.0 + 1e-9)
    chk("끝~마지막 ≤ 25 m", 100.0 - xs[-1] <= 25.0 + 1e-9)
    ps2 = gully_positions(0.0, 100.0, sag_points=(37.0,),
                          curve_points=(12.0, 64.0), jitter=0.4)
    ps3 = gully_positions(0.0, 100.0, sag_points=(37.0,),
                          curve_points=(12.0, 64.0), jitter=0.4)
    chk("지터도 결정적", ps2 == ps3)

    # -- Gully body ------------------------------------------------------
    print("\n[3] build_gully")
    k = dry_kit()
    r1 = build_gully(k, "/W/Gully_A", 22.0, -3.75, 0.0, None)
    chk("기본(솔리드) = 2 프림", r1["prim_count"] == 2, str(r1["prim_count"]))
    chk("기본 = GT 낙차 아님", not r1["is_gt_hazard"])
    k = dry_kit()
    r2 = build_gully(k, "/W/Gully_B", 44.0, -3.75, 0.0, None, lid=False)
    chk("무개구 = GT 0.64 m", r2["is_gt_hazard"] and abs(r2["gt_drop"] - 0.64) < 1e-9)
    chk("무개구 = 벽4+바닥1+링4 = 9 프림", r2["prim_count"] == 9,
        str(r2["prim_count"]))
    k = dry_kit()
    r3 = build_gully(k, "/W/Gully_C", 0.0, 0.0, 0.0, None, slats=10)
    chk("슬랫 10 = 피트1+링4+슬랫10 = 15 프림", r3["prim_count"] == 15,
        str(r3["prim_count"]))

    # -- Manhole ---------------------------------------------------------
    print("\n[4] build_manhole")
    k = dry_kit()
    m1 = build_manhole(k, "/W/MH_A", 3.0, 1.0, 0.0, None)
    m2 = build_manhole(k, "/W/MH_B", 9.0, 1.0, 0.0, None)
    chk("2 프림", m1["prim_count"] == 2, str(m1["prim_count"]))
    chk("flush ±10 mm", abs(m1["proud"]) <= 0.010,
        f"{m1['proud'] * 1000:+.1f} mm")
    chk("개체마다 다른 오차", abs(m1["proud"] - m2["proud"]) > 1e-6,
        f"{m1['proud'] * 1000:+.1f} vs {m2['proud'] * 1000:+.1f} mm")
    k2 = dry_kit()
    m1b = build_manhole(k2, "/W/MH_A", 3.0, 1.0, 0.0, None)
    chk("재실행 동일", abs(m1["proud"] - m1b["proud"]) < 1e-12)
    chk("뚜껑 φ558 (틀 648 해석)", abs(m1["d_lid"] - 0.558) < 1e-9,
        f"{m1['d_lid'] * 1000:.0f} mm")
    k3 = dry_kit()
    m3 = build_manhole(k3, "/W/MH_C", 3.0, 1.0, 0.0, None, lid=False)
    chk("무개구 근사 = 1 프림", m3["prim_count"] == 1, str(m3["prim_count"]))
    chk("무개구 = GT 1.20 m", m3["is_gt_hazard"] and abs(m3["gt_drop"] - 1.2) < 1e-9)

    # -- Ramp curb -------------------------------------------------------
    print("\n[5] build_ramp_curb — scene13 램프 프로파일")
    prof = [(0.0, 0.0, 3.60, 0.306),
            (3.60, -0.306, 23.29, 3.348),
            (26.89, -3.654, 3.60, 0.306)]
    k = dry_kit()
    rc = build_ramp_curb(k, "/W/RampCurb", prof, y_neg=-3.0, y_pos=3.0,
                         mtl=None)
    chk("3 세그 × 2 측 = 6 프림", rc["prim_count"] == 6, str(rc["prim_count"]))
    chk("GT 낙차 0.12 m 신설", rc["is_gt_hazard"] and abs(rc["gt_drop"] - 0.12) < 1e-9)
    bad = False
    try:
        build_ramp_curb(dry_kit(), "/W/X", prof, -3.0, 3.0, None, height=0.25)
    except ValueError:
        bad = True
    chk("법정 범위 밖 높이 거부", bad)

    # -- Road markings ---------------------------------------------------
    print("\n[6] build_road_marking")
    k = dry_kit()
    pk = build_road_marking(k, "/W/Stall", "parking", None, 0.0, 0.0, n=5)
    chk("주차 5구획 = 7 프림", pk["prim_count"] == 7, str(pk["prim_count"]))
    chk("구획 2.5×5.0", pk["stall"] == (2.5, 5.0))
    k = dry_kit()
    cw = build_road_marking(k, "/W/CW", "crosswalk", None, 0.0, 0.0,
                            band_w=4.0, walk_len=8.0)
    chk("횡단보도 폭 4 m → 스트라이프 4", cw["n_stripe"] == 4, str(cw["n_stripe"]))
    chk("피치 0.90 m", abs(cw["pitch"] - 0.90) < 1e-9)
    k = dry_kit()
    ln = build_road_marking(k, "/W/L", "line", None, 0.0, 0.0, length=6.0,
                            yaw_deg=31.0)
    chk("사선 단선 = 1 프림", ln["prim_count"] == 1)

    # -- Retaining wall --------------------------------------------------
    print("\n[7] build_retaining_wall_details — L20 × H5 캔틸레버")
    con, exp = wall_joint_positions(20.0, "cantilever")
    chk("신축 1개(베이 10 m ≤ 15~20)", exp == [10.0], str(exp))
    chk("수축 2개·간격 5 m ≤ 9 m", con == [5.0, 15.0], str(con))
    con2, exp2 = wall_joint_positions(20.0, "gravity")
    chk("중력식 신축 10 m ≤ 10 m", exp2 == [10.0], str(exp2))
    chk("자투리 패널 없음", con2 == [5.0, 15.0], str(con2))
    con3, exp3 = wall_joint_positions(60.0, "counterfort", contraction=0.0)
    chk("부벽식 수축 생략 가능", con3 == [] and len(exp3) == 3, str(exp3))
    k = dry_kit()
    w = build_retaining_wall_details(k, "/W/RW", 0.0, 20.0, face_y=2.0,
                                     z_ground=0.0, z_top=5.0, mtl_dark=None)
    print(f"      프림 {w['prim_count']} (배수공 {w['n_weep']}, "
          f"수축 {len(w['contraction'])}, 신축 {len(w['expansion'])}, 갓돌 1)")
    chk("배수공 4 m 간격 5개", w["n_weep"] == 5, str(w["n_weep"]))
    chk("프림/m ≤ 0.5", w["prim_count"] / 20.0 <= 0.5,
        f"{w['prim_count'] / 20.0:.2f}")
    chk("cope_flush 기본 → GT 불변", abs(w["gt_delta"]) < 1e-12)
    k = dry_kit()
    w2 = build_retaining_wall_details(k, "/W/RW2", 0.0, 20.0, face_y=2.0,
                                      z_ground=0.0, z_top=5.0, mtl_dark=None,
                                      cope_flush=False)
    chk("cope_flush=False → GT +0.10", abs(w2["gt_delta"] - 0.10) < 1e-9)
    k = dry_kit()
    w3 = build_retaining_wall_details(k, "/W/RW3", 0.0, 20.0, face_y=2.0,
                                      z_ground=0.0, z_top=5.0, mtl_dark=None,
                                      weep_mode="grid")
    print(f"      grid 모드(3 ㎡/개): 배수공 {w3['n_weep']} 개, "
          f"피치 {w3['weep_pitch']:.2f} m")
    chk("grid 피치 √3", abs(w3["weep_pitch"] - math.sqrt(3.0)) < 1e-9)
    chk("grid 가 linear 보다 많다", w3["n_weep"] > w["n_weep"])

    # -- Tactile paving --------------------------------------------------
    print("\n[8] build_tactile_pair (기본 OFF 함수)")
    k = dry_kit()
    t1 = build_tactile_pair(k, "/W/TacA", "bar", 0.0, 0.0, 5.0, 0.6, None,
                            relief="geom", walk_axis="x")
    chk("선형 geom = 1 + 8 = 9 프림", t1["prim_count"] == 9, str(t1["prim_count"]))
    chk("선형 돌기 5 mm", abs(t1["nub_h"] - 0.005) < 1e-9)
    k = dry_kit()
    t2 = build_tactile_pair(k, "/W/TacB", "dot", 0.0, 0.0, 0.6, 0.6, None,
                            relief="normal")
    chk("점형 normal = 1 프림", t2["prim_count"] == 1)
    chk("점형 돌기 6 mm", abs(t2["nub_h"] - 0.006) < 1e-9)
    chk("기본 비활성 표기", t2["default_enabled"] is False)
    k = dry_kit()
    t3 = build_tactile_pair(k, "/W/TacC", "dot", 0.0, 0.0, 0.6, 3.0, None,
                            relief="geom")
    chk("점형 geom 폭증 경고", t3["warning"] is not None,
        f"{t3['prim_count']} 프림")

    # -- GT summary ------------------------------------------------------
    print("\n[9] GT 낙차 영향 요약")
    for label, val in (
            ("build_gutter_L        ", "낙차 아님 (단 연석 노출고 +18~30 mm)"),
            ("build_gully(lid=True) ", "낙차 아님"),
            ("build_gully(lid=False)", "★ GT 0.64 m"),
            ("build_manhole(lid=T)  ", "낙차 아님 (flush ±10 mm)"),
            ("build_manhole(lid=F)  ", "★ GT = pit_depth"),
            ("build_ramp_curb       ", "★ GT 0.10~0.15 m — 낙차선 신설"),
            ("build_road_marking    ", "낙차 아님 (스케일 앵커)"),
            ("build_retaining_...   ", "낙차 아님 (cope_flush=False 면 +cope_h)"),
            ("build_tactile_pair    ", "낙차 아님")):
        print(f"      {label} : {val}")

    print("\n" + "=" * 74)
    print("검산 결과: " + ("전 항목 통과" if ok else "★ 실패 항목 있음"))
    print("=" * 74)
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    sys.exit(_selfcheck())
