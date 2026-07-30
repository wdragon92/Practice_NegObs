# -*- coding: utf-8 -*-
"""building_kit — upper layer that **assembles the mass** of Korean buildings.

Where `facade_kit` makes the **surface attachments** of a facade (plinth,
shopfront, AC units, signage, balconies, pipework, the fire-access triangle),
this module decides **which volumes they go on and in what order**. It is the
composition layer above facade_kit and never re-implements what facade_kit
already provides.

Why a full rewrite (diagnosis of the current `scene_common.build_building`)
--------------------------------------------------------------------------
The current composition = **one cuboid shell + a uniform grid of glass quads +
a parapet** (plus the door, downpipe, penthouse, plinth and AC units bolted on
recently). It diverges from real Korean buildings in three ways.

1. **There is only one mass.** Korean buildings have at least 2~4 volumes: the
   setback between low-rise retail and upper-floor housing, the protruding
   stair/lift core, piloti, and the rooftop penthouse.
2. **Windows are a uniform grid.** Cores have almost no windows or tall narrow
   ones, housing repeats per balcony unit, and retail is full glazing. An
   evenly spaced `col_step` grid is an office pattern and simply does not exist
   on apartments or multi-family housing (survey §3.2).
3. **The roof is a flat white lid.** In reality there is a penthouse, a water
   tank (on older stock), an antenna and a railing, and buildings in
   residential zones have their upper mass cut back in steps by the northern
   daylight-setback rule.

The prim budget is the overriding constraint (a measured fact)
--------------------------------------------------------------
The primary judging viewpoint is a camera at h0.3 m, pitch -10 deg, vFOV
36 deg, so the top of frame is only **+8.0 deg** above the horizon. The tallest
thing entering frame at distance d is

    z = 0.3 + d*tan(8 deg) ~= 0.3 + 0.14*d
    d=10 -> 1.7, d=20 -> 3.1, d=34 -> 5.1, d=50 -> 7.3, d=90 -> 12.9

The starting point for this work was that the 33 scenes held 4,173 window prims
and most of them sat above that ceiling, i.e. **outside the frame**. So this
module **demotes the type itself** with distance (`fk.lod_tier`). Beyond
d>80 m any type drops to `backdrop` (3~4 prims).

Type x LOD prim budget table (per building, geometry prims only)
— **v1 re-baseline 2026-07-29**
----------------------------------------------------------------
`selfcheck()` **measures** with MockKit and compares against this table
(exceeding it fails). Table values are the budget (upper bound) and the
**measured values are in parentheses**. Representative facade W=24 m, depth
12 m, standard floor counts per type (shop_house 4, apt 14, office 9, villa 5,
low_shop 1, backdrop 10).

| kind        | near (<20 m) | mid (20~40) | far (40~80) | silhouette (>80) |
|-------------|--------------|-------------|-------------|------------------|
| `shop_house`| **65** (62)  | **38** (35) | **9** (6)   | 4 (3)            |
| `apt`       | **57** (54)  | **23** (20) | **15** (12) | 4 (4)            |
| `office`    | **31** (28)  | **15** (12) | **11** (8)  | 4 (3)            |
| `villa`     | **57** (54)  | **28** (25) | **10** (7)  | 4 (3)            |
| `low_shop`  | **44** (41)  | **27** (24) | **7** (4)   | 4 (3)            |
| `backdrop`  | 4 (3)        | 4 (3)       | 4 (3)       | 4 (3)            |

Budget = **measured + 3** (the worst case where the water tank, antenna and
roof sign all switch on at once, 1 prim each `[measured]`). Only the `backdrop`
row and the `silhouette` column are exempt and use the **builder's structural
maximum of 4** (shell 1~2 + parapet 1 + penthouse 1). The table's evidence
grade is `[estimated]` and its role is not a design target but a **regression
freeze line** — see the `BUDGET` comment for the full story. The width-dependent
part of the cap is **not** in the table; it lives in `prim_budget(kind, tier, W)`.

`backdrop` is **distant-silhouette-only** regardless of distance. No windows,
3~4 prims.

W3 CB-4 (2026-07-31) — B-F1 · B-F2 · B-F3 · BS-4
------------------------------------------------
Survey R3 (`Docs/surveys/w3r_building_ab_v1.md`) rendered this module against
`scene_common.build_building` and against an asset backdrop, and found the mass,
plinth, attachment and rooftop layers correct but three defects that blocked
adoption. All four rows are `[ruled 07-30]` W3 spec §4.2 K3.

* **B-F1 — 62 of 62 glazing prims were buried inside the solid shell.** Every
  window, shopfront and entrance asked `Facade.world` for a *negative* `out`,
  i.e. it was pushed **into** the mass. `Facade.world`'s own docstring says `out`
  is "the distance **outward** from the wall face (always positive)".
  → `Plan.out_at(u0,u1,z0,z1)` now reports the outward face of whatever volume
  actually covers a facade window, and every `glass`/`sign`/`decal` element sits
  `fk.WALL_PROUD` = 5 mm proud of it. Three distinct burial mechanisms were
  present and all three are covered: the plain shell, the **office podium** in
  front of a set-back tower, and the **protruding apartment core** (a positive
  `out` of 0.55 was still 30 mm inside the 0.60 core, and the fire-access decal
  sat **588 mm** inside it).
* **The new self-check `[11]`** is the reason this row exists at all: the suite
  was 135/135 green while nothing was visible, because `[5]` counted prims,
  `[7]` checked `z ≥ base_z − 0.05` and `[8]` checked path uniqueness — **none
  of them asked whether a facade prim is on the outside of the wall.** `[11]`
  asserts `out_max > 0` per **material role** against every overlapping mass box,
  and `[11a]` cross-validates the mass model against the emitted prims so the
  check cannot be satisfied by a stale model. On the pre-CB-4 tree `[11]` reports
  **73** burial pairs on the standard grid and **712** over the W × base_z sweep
  `[measured]`.
* **B-F2 — the shopfront bay count was a per-tier constant, so `W` was absent
  from the parameterisation.** A 28 m facade got three butted 8.93 m glazing
  panels against a real Korean bay of 3.0–4.5 m. → `shopfront_bays(W, tier)`,
  and `prim_budget` grew a `W` term because a bay costs 2 prims.
* **B-F3 — `lod_dist` defaulted to `|facade plane|`**, i.e. it assumed the camera
  sits at the origin. → `judged_eyes()` / `eye_distance()` derive the distance
  from the real `grid_views` eye set. Opt-in via `eyes=`.
* **BS-4 — `kind="backdrop"` for out-of-frame buildings.** `facade_in_frame()`
  applies the spec's ±30° rule to the whole facade segment; a facade no judged
  eye can see is demoted to the 3-prim silhouette builder.

**Nothing here is wired to a scene.** With `eyes=None` the plan is byte-identical
to the pre-CB-4 one apart from the glazing offsets, and no scene file imports
this module yet (integration is BS-2, 24 call sites, a later batch).

Design conventions (same as facade_kit — each has caused a real incident)
------------------------------------------------------------------------
1. Coordinates Z-up, units in metres.
2. **Never import `scene_common`.** Primitive helpers are injected via
   `facade_kit.Kit`. `pxr` is lazily imported inside functions only.
3. **RNG 100 % deterministic** — the builtin `hash()` is banned (it changes per
   process under PYTHONHASHSEED; this actually bit this project). Use
   `zlib.crc32` + `random.Random`.
4. **Scale anchors are inviolable** — door 2.10, railing 1.20, AC unit
   0.80x0.55x0.30, parking clear height 2.10, stair riser 0.15~0.18.
   Per-instance variation only via `_jit()` and only **within +-8 %**.
5. **Must work with the existing `bd` keys alone** (x0,x1,y0,y1,h,floors,axis,
   facade_x/y,face_dir,base_z). `kind` is optional; without it `infer_kind()`
   infers it. -> **Integration must require no scene-file edits.**
6. **v5.2 §6 "empty is the default"** — functionally required items only. No
   decoration.
7. **No aerial perspective.** Two surveys independently concluded it is
   excessive, since Seoul's measured b_ext costs only 2.6~7 % contrast at 90 m.
8. Any figure without a source is tagged `[estimated]`/`[knowledge]`/
   `[no source]` with a reason.

**Total-height invariant**: `bd["h"]` is read by other scene code (occlusion
checks `obs`, rooftop placement, etc.), so the top of the shell must stay at
`base_z + h`. Even when floor heights are made non-uniform they are **scaled
proportionally** to the total height (§`plan_levels`).

Source documents
----------------
* `Docs/surveys/korean_urban_backdrop.md` (2026-07-28)
  — §2 typology, §3.1 mass/floor height, §3.2 windows, §3.3 lower floors,
  §3.5 rooftop, §4 priorities, §5 per-scene composition table, §6 LOD table,
  §6.1 confirmed parameters
* `Docs/surveys/_dimension_index.md`
  — rooftop penthouse (horizontal projection <= 1/8 of building area and <=12 m
    is excluded from height and floor count, Building Act Enforcement Decree
    §119), **floor-count-to-height conversion 4.0 m/floor** (same §119 (1)9),
    roof signage (floors 5~15, max length 30 m, height <=15 m and at most half
    the building height, Outdoor Advertisements Act Enforcement Decree §15),
    parapet 1.2 m
* Northern daylight setback — **Building Act §61(1) -> Enforcement Decree
  §86(1)**: in exclusive and general residential zones, the portion **up to
  10 m must be set back at least 1.5 m from the adjoining lot boundary**, and
  the portion **above 10 m by at least half that portion's height** (amended
  2023.9.12; previously 9 m).
  Grade **statutory (secondary)** — the law.go.kr article body is JS-rendered
  so quoting the primary text directly failed, and two independent secondary
  sources (bigcase.ai and a casenote.kr search summary) agree.
  -> The stepped upper setback applies by default only to `villa` (low-rise
    housing in a residential zone). `shop_house`/`office` presuppose commercial
    zones, which §61(1) does not cover, so they do not get it.
"""

import math
import random
import zlib

import facade_kit as fk

__all__ = [
    "Mtls", "Plan", "KINDS",
    "build_korean_building", "infer_kind", "plan_building", "plan_levels",
    "prim_budget", "BUDGET", "selfcheck",
    "mass_faces", "shopfront_bays",
    "judged_eyes", "eye_distance", "facade_in_frame", "should_backdrop",
]

KINDS = ("shop_house", "apt", "office", "villa", "low_shop", "backdrop")

# ===========================================================================
# [0] Constants — scale anchors must **never be randomized**
# ===========================================================================
# Anchors that facade_kit already defines are referenced, never redefined.
DOOR_H = fk.DOOR_H            # 2.10  statutory: Evacuation/Fire-Protection Rule §16
RAIL_H = fk.RAIL_H            # 1.20  statutory: Building Act Enforcement Decree §40
SLAB_T = fk.SLAB_T            # 0.21  statutory: Housing Construction Standards §14-2 (1)

# --- Floor heights (survey §3.1) ----------------------------------------
FH_APT = 2.80          # certain: Korea PM "apartment floor height", currently 2.80~2.85
FH_VILLA = 2.80        # [knowledge]
FH_SHOP_G = 4.00       # [estimated] neighbourhood retail ground floor 3.9~4.2 (no primary source)
FH_SHOP_U = 3.30       # [estimated] neighbourhood retail, 2nd floor and up
FH_LEGAL = 4.00        # statutory: Building Act Enforcement Decree §119 (1)9 — 4 m/floor
                       #       when floor division is unclear -> used as the default
                       #       office floor height (no separate primary source).

# --- Piloti (survey §3.3(e)) --------------------------------------------
PILOTI_CLEAR = 2.10    # **statutory**: Parking Lot Act Enforcement Rule §6, parking
                       #   area clear height of at least 2.1
                       #   (the commonly cited 2.3 has no basis — the survey confirmed this)
PILOTI_H = 2.90        # [estimated] piloti floor height 2.7~3.0 (clear 2.1~2.4 + beams/services)
PILOTI_COL = 0.45      # [estimated] RC column section 0.45x0.45
PILOTI_PITCH = 5.40    # [estimated] column centre spacing — derived from
                       #   parking bays 2.5x2 = 5.0~5.2
PILOTI_PORCH = 5.20    # [estimated] open depth — parking length 5.0 (statutory bay) + clearance

# --- Core (stairs / lift) (survey §3.2) ---------------------------------
CORE_W = 3.00          # [knowledge] core width between units, 2.5~3.5
CORE_PROUD = 0.60      # [estimated] core protrusion. Kept smaller than a balcony
                       #   (statutory 1.50) to minimize how far it extends beyond the
                       #   bd bounding box (integration caveat).
CORE_WIN_W = 0.90      # [estimated] width of the tall narrow stairwell window

# --- Unit bays (survey §3.2) --------------------------------------------
BAY_APT = 9.00         # [knowledge] facade width of one apartment unit, 8~12
BAY_VILLA = 4.50       # [knowledge] multi-family unit width
BAY_SHOP = 5.00        # [knowledge] shop frontage 4~6

# --- Shopfront bay derivation (B-F2, survey R3 §5.2) ---------------------
# The bay count used to be the **constant** 4/3/1 per LOD tier with
# `bay_w = max(3.0, W/nb)`, i.e. `W` was absent from the parameterisation. On
# scene20's building C (W = 28 m, mid) that produced three butted glazing panels
# of **8.93 m** each with no pier `[measured — survey R3 §5.2]`. Real Korean
# neighbourhood shopfront bays are **3.0–4.5 m**, so the count is now derived
# from W.
SHOP_BAY_MIN, SHOP_BAY_MAX = 3.00, 4.50   # [knowledge] Korean shopfront bay band
SHOP_BAY_TARGET = 3.60                    # survey R3 §5.2's prescribed divisor
# Prim guard, **not** a design target: the shopfront costs 2 prims per bay, so an
# unbounded count would walk straight through the budget table. When the cap binds
# the resulting bay exceeds SHOP_BAY_MAX and `shopfront_bays` says so via
# `bay_width()`. far / silhouette build no shopfront at all (survey §6 LOD table).
SHOP_BAY_CAP = {"near": 10, "mid": 8, "far": 0, "silhouette": 0}

# --- Rooftop penthouse (Building Act Enforcement Decree §119 (1)5, 9 — statutory) ---
PH_AREA_FRAC = 0.125   # statutory: horizontal projection <= 1/8 of building area is
                       #   excluded from the floor count
PH_H = 2.90            # [knowledge] penthouse height 2.5~3.5 (statutory cap 12 — only
                       #   the excess counts)
TANK_R = 0.90          # [knowledge] elevated water tank — **older low-rise stock only**.
TANK_H = 1.60          #   Almost absent on new builds (source: Mechanical Facilities
                       #   News, "Where did the rooftop water tanks go?")
ANT_H = 2.20           # [knowledge] antenna — on older buildings' roofs

# --- Roof signage (Outdoor Advertisements Act Enforcement Decree §15 — statutory) ---
ROOFSIGN_LEN_MAX = 30.0    # statutory: maximum length 30 m
ROOFSIGN_H_MAX = 15.0      # statutory: height <= 15 m **and** <= half the building height
ROOFSIGN_FLOORS = (5, 15)  # statutory: buildings of 5~15 floors

# --- Awning (Seoul Outdoor Advertisements Ordinance — statutory) --------
AWNING_OUT_ROAD = 1.00     # statutory: within 1.00 when occupying the road
AWNING_OUT_FREE = 0.70     # statutory: within 0.70 when not occupying it
AWNING_Z = 2.60            # [knowledge] mounting height at the lower edge, 2.4~2.8

# --- Podium setback (office) ---------------------------------------------
SETBACK_OFFICE = 1.20      # [estimated] tower setback relative to the podium. No primary
                           #   source (a formal consequence of survey §5, "granite podium
                           #   + canopy")
# --- Northern daylight setback steps (Enforcement Decree §86(1) — statutory, secondary) ---
DAYLIGHT_STEP_Z = 10.0     # statutory: the setback tightens above a height of 10 m
DAYLIGHT_STEP_IN = 1.60    # [estimated] actual setback depth of one step. The article says
                           #   "set back by at least half the height", so the value varies
                           #   with lot shape -> a representative value that leaves only
                           #   the visual signature.

# --- Type-inference boundaries (infer_kind) ------------------------------
VILLA_GFA_MAX = 660.0  # statutory: Building Act Enforcement Decree table 1, item 2(c) —
                       #   multi-family housing is "one building whose floor area used as
                       #   housing totals 660 m2 or less, with 4 floors or fewer". The
                       #   former constant 600 (regardless of floor count) was [no source].
VILLA_MIN_DEPTH = 7.0  # [estimated, derived] minimum depth at which a residential unit
                       #   works. A studio-type unit of 30 m2 net / frontage 4.50
                       #   (BAY_VILLA) ~= 6.7 m is the lower bound, and a regular
                       #   40~60 m2 unit gives 8.9~13.3 m. A 4-storey building only 6 m
                       #   deep cannot hold a unit plan -> treat it as roadside
                       #   neighbourhood retail / a shop house.
RESI_FH_MAX = 3.05     # [estimated] upper bound of the residential floor-height band.
                       #   Apartment typical floors are 2.80~2.85 (certain) plus slack for
                       #   piloti and plant floors. Above that, assume neighbourhood
                       #   retail (ground floor 3.9~4.2 [estimated]) or office (statutory
                       #   4.0 conversion) is mixed in.
                       #   **The low-rise and high-rise branches use the same value**
                       #   (a single unified boundary).

# --- LOD floor-count caps (survey §6 LOD table) --------------------------
ROW_CAP = {"near": 8, "mid": 5, "far": 2, "silhouette": 0}

# --- Judged-eye set (B-F3 / BS-4, survey R3 §2 · §5.3) -------------------
# `scene_common.grid_views(gy, heights=(0.3,0.9,1.8), dists=(2,5,10), pitch=-10)`
# puts the eye at `(-d, gy, h)` looking along **+X**. 21 of the 33 scenes call it
# as `sc.grid_views(0.0)`; the exceptions pass their own gy `[measured — grep]`,
# which is why `judged_eyes` takes gy rather than hard-coding 0.
EYE_HEIGHTS = (0.3, 0.9, 1.8)
EYE_DISTS = (2.0, 5.0, 10.0)
EYE_YAW_HALF = 30.0    # deg. **Measured, not a convention**: the capture is
                       #   1920x1080 (`scene_common.py:852`) and vFOV is 36
                       #   (`fk.CAM_VFOV`), so the horizontal half-angle is
                       #   atan(tan(18 deg) * 16/9) = **30.006 deg**. The scenes'
                       #   own camera checks already write it as +-30
                       #   (e.g. `scene21:181`). It is the frame **width** test and
                       #   is deliberately independent of `fk.frame_ceiling`, which
                       #   is the height test.


# ===========================================================================
# [1] Deterministic RNG — builtin hash() banned
# ===========================================================================
def _rng(*keys):
    """A deterministic `random.Random`. The builtin `hash()` changes per process
    under PYTHONHASHSEED and is therefore **never used**. crc32 uses a fixed
    standard-library polynomial, so it is identical across runs and platforms."""
    s = "|".join(str(k) for k in keys)
    return random.Random(zlib.crc32(s.encode("utf-8")) & 0xFFFFFFFF)


def _seed_of(*keys):
    s = "|".join(str(k) for k in keys)
    return zlib.crc32(s.encode("utf-8")) & 0xFFFFFFFF


def _builtin_hash_uses(src=None, path=None):
    """Exhaustively decide whether this source **actually uses the builtin
    hash**. 0 prims.

    The former check searched the source string for the needle as a substring,
    but the needle literal sat on the checking code's own line, so it
    **self-matched and failed forever** (self-contradiction). Here the verdict
    comes from two paths that never look at strings or comments at all.

      (a) AST — `Name(id="hash", ctx=Load)` nodes. Catches not just calls like
          `hash(x)` but aliases such as `f = hash`. Redefinitions
          (`hash = ...`, `def hash`) are not the builtin, so Store contexts are
          counted separately and only reported.
      (b) tokenize — search for `hash(` in what remains **after removing**
          STRING and COMMENT tokens. This also catches calls routed through an
          Attribute, such as `builtins.hash(x)`, complementing (a). This file's
          needle literal is a STRING token and is removed, so self-matching is
          **structurally** impossible.

    Limitation: a name assembled at runtime, e.g.
    `getattr(builtins, "ha"+"sh")`, cannot be caught statically
    `[limitation stated]`.

    Returns: (ast_hits, token_hits, shadow_lines) — unused if the first two are
    empty.
    """
    import ast
    import io
    import tokenize
    if src is None:
        with open(path or __file__, encoding="utf-8") as fh:
            src = fh.read()
    name = "ha" + "sh"                      # split across tokens — prevents self-matching
    tree = ast.parse(src)
    ast_hits, shadow = [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == name:
            (ast_hits if isinstance(node.ctx, ast.Load) else shadow).append(
                f"L{node.lineno}")
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)) \
                and node.name == name:
            shadow.append(f"L{node.lineno}")
    skip = {tokenize.STRING, tokenize.COMMENT}
    for nm in ("FSTRING_START", "FSTRING_MIDDLE", "FSTRING_END"):
        if hasattr(tokenize, nm):        # 3.12+ emits f-strings as piecewise tokens
            skip.add(getattr(tokenize, nm))
    code_only = []
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type not in skip:
            code_only.append(tok.string)
    joined = "".join(code_only)
    tok_hits = [] if (name + "(") not in joined else [
        f"L{i + 1}" for i, ln in enumerate(joined.splitlines())
        if (name + "(") in ln]
    return ast_hits, tok_hits, shadow


def _jit(rng, v, frac=0.08):
    """Per-instance jitter. **Fixed +-8 % ceiling** — a hard cap so scale
    anchors are never smeared. Passing frac above 0.08 still clamps to 0.08
    (prevents the incident from recurring)."""
    f = min(abs(float(frac)), 0.08)
    return float(v) * (1.0 + rng.uniform(-f, f))


def _clamp(v, lo, hi):
    return lo if v < lo else (hi if v > hi else v)


# ===========================================================================
# [1b] B-F2 — shopfront bay count derived from the facade width
# ===========================================================================
def shopfront_bays(W, tier):
    """Number of ground-floor shopfront bays for a facade of width `W`. 0 prims.

    `n = clamp(round(W / SHOP_BAY_TARGET), 1, SHOP_BAY_CAP[tier])` — survey R3
    §5.2's prescription verbatim. Returns 0 where no shopfront is built.

    The band cannot always be met with an integer split: below W ≈ 7.2 m there is
    no n with `W/n` inside 3.0–4.5 (W = 5.0 gives 5.00 at n=1 or 2.50 at n=2), and
    above `cap · SHOP_BAY_MAX` the prim guard binds. Both cases pick the count
    nearest the band and are reported by `bay_width()` rather than hidden.
    """
    cap = int(SHOP_BAY_CAP.get(str(tier), 0))
    if cap <= 0:
        return 0
    w = float(W)
    if w < 1.5:                                  # `fk.build_shopfront`'s own floor
        return 0
    return int(_clamp(round(w / SHOP_BAY_TARGET), 1, cap))


def bay_width(W, tier):
    """Resulting bay width [m], or 0.0 when no shopfront is built. 0 prims."""
    n = shopfront_bays(W, tier)
    return (float(W) / n) if n else 0.0


# ===========================================================================
# [1c] B-F3 / BS-4 — the judged eye set, true distance, and the frame test
# ===========================================================================
def judged_eyes(gy=0.0, heights=EYE_HEIGHTS, dists=EYE_DISTS):
    """The judged camera positions as `[(x, y, z), ...]`. 0 prims.

    Mirrors `scene_common.grid_views(gy, heights, dists, pitch=-10)`: eye at
    `(-d, gy, h)`, view direction **+X**. The pitch is irrelevant here — the
    horizontal test uses the +X bearing and the vertical test is
    `fk.frame_ceiling`, which already contains the pitch.
    """
    return [(-float(d), float(gy), float(h))
            for h in heights for d in dists]


def _facade_rect(p):
    """The facade rectangle as `(plane, u0, u1, z0, z1, axis_y)` — the surface a
    judged eye can actually see. 0 prims."""
    return (p.plane, p.fac.u0, p.fac.u1, p.base_z, p.top_z, p.axis_y)


def eye_distance(p, eyes):
    """**B-F3.** Shortest distance from any judged eye to the nearest point of the
    facade rectangle [m]. 0 prims.

    The default `dist` is `abs(facade plane coordinate)`, which assumes the camera
    sits at the origin and ignores both the eye's standoff and the building's
    lateral offset. Over the 89 `bd` dicts in the 33 scenes that assigns the
    **wrong LOD tier to 16 (18.0 %)**, `d_default − d_true` mean −4.4 m, range
    −49.0 … +10.0 `[measured — survey R3 §2]`. Under-estimating the distance is
    the expensive direction: it promotes a tier and spends prims off-frame.
    """
    plane, u0, u1, z0, z1, axis_y = _facade_rect(p)
    best = float("inf")
    for (ex, ey, ez) in eyes:
        # nearest point of the axis-aligned rectangle to the eye
        eu, en = (ex, ey) if axis_y else (ey, ex)
        du = max(u0 - eu, 0.0, eu - u1)
        dz = max(z0 - ez, 0.0, ez - z1)
        dn = en - plane
        d = math.sqrt(du * du + dz * dz + dn * dn)
        if d < best:
            best = d
    return best


def facade_in_frame(p, eyes, half_deg=EYE_YAW_HALF):
    """**BS-4 policy (1).** True when **any** point of the facade falls inside
    `±half_deg` of **any** judged eye's +X view axis. 0 prims.

    The facade is a segment in plan, so the whole segment is tested, not its
    centre: a long wall can be out of frame at both ends and still cross the axis.
    Points behind the eye (x ≤ eye x) never count.
    """
    plane, u0, u1, z0, z1, axis_y = _facade_rect(p)
    lim = math.tan(math.radians(float(half_deg)))
    # segment endpoints in world (x, y)
    ends = [(u0, plane), (u1, plane)] if axis_y else [(plane, u0), (plane, u1)]
    for (ex, ey, _ez) in eyes:
        fs = []
        for (px, py) in ends:
            dx = px - ex
            if dx <= 1e-9:                       # at or behind the eye plane
                fs.append(None)
                continue
            fs.append((py - ey) / dx)            # tan(bearing)
        a, b = fs
        if a is not None and abs(a) <= lim:
            return True
        if b is not None and abs(b) <= lim:
            return True
        if a is not None and b is not None and (a > lim) != (b > lim) \
                and (a < -lim) != (b < -lim):
            return True                          # the segment straddles the axis
    return False


def should_backdrop(p, eyes, half_deg=EYE_YAW_HALF):
    """**BS-4.** `True` when the building earns no facade geometry at all.
    0 prims.

    Survey R3 §7.2 measured **4 of 12** buildings in the five repeated-brick
    scenes to be outside ±30° of every judged eye in every judged cut. A backdrop
    is 3–4 prims against 6–56, so this row has a **negative** prim cost.
    """
    return not facade_in_frame(p, eyes, half_deg)


# ===========================================================================
# [2] Material-role container
# ===========================================================================
class Mtls:
    """Bundle of material roles. A **fallback chain** fills every role even when
    the current call sites pass only three (shell, glass, parapet) — the
    prerequisite for integrating without editing scene files.

    Roles
      shell   exterior wall body   glass  windows / full glazing
      parapet parapet, railing, metal
      stone   plinth granite (falls back to parapet)
      metal   AC units, pipework, brackets (falls back to parapet)
      sign    signage panels (falls back to parapet)
      decal   red fire-access triangle (falls back to sign)
      dark    piloti interior and opening shadow (falls back to shell)

    If the call site follows the material-path naming convention
    (scene_common `_LOOK_RULES`) and includes the "granite"/"stone" and
    "sign"/"placard" tokens, the look layer classifies them into the stone and
    sign roles respectively.
    """

    __slots__ = ("shell", "glass", "parapet", "stone", "metal", "sign",
                 "decal", "dark")

    def __init__(self, shell, glass=None, parapet=None, stone=None,
                 metal=None, sign=None, decal=None, dark=None):
        self.shell = shell
        self.glass = glass if glass is not None else shell
        self.parapet = parapet if parapet is not None else shell
        self.stone = stone if stone is not None else self.parapet
        self.metal = metal if metal is not None else self.parapet
        self.sign = sign if sign is not None else self.parapet
        self.decal = decal if decal is not None else self.sign
        self.dark = dark if dark is not None else shell

    @classmethod
    def from_legacy(cls, shell_mtl, glass_mtl, parapet_mtl):
        """Adapter taking the current
        `build_building(stage, prefix, bd, shell, glass, parapet)` signature
        as-is."""
        return cls(shell_mtl, glass_mtl, parapet_mtl)

    @classmethod
    def coerce(cls, x):
        if isinstance(x, Mtls):
            return x
        if isinstance(x, dict):
            return cls(**{k: v for k, v in x.items()
                          if k in cls.__slots__})
        if isinstance(x, (tuple, list)):
            return cls(*x[:8])
        return cls(x)


# ===========================================================================
# [3] Pure computation — type inference, floor levels, mass planning (0 prims)
# ===========================================================================
def infer_kind(bd, dist=None):
    """Infer the type when `bd` has no `kind`. **The heart of integrating
    without editing scene files.**

    The only inputs are the existing keys (floor count, mean floor height,
    footprint, distance).

        dist > 80                            -> "backdrop"  (distant silhouette only)
        floors <= 1                          -> "low_shop"  (single-storey retail)
        floors <= 4 and total floor area > 660 -> "shop_house" (over the statutory
                                                  multi-family size)
        floors <= 4 and depth < 7.0          -> "shop_house" (no viable unit plan)
        floors <= 4 and h/floors > 3.05      -> "shop_house" (retail floor heights mixed in)
        floors <= 4                          -> "villa"     (multi-family / villa)
        floors <= 8                          -> "office"    (business facility)
        floors >= 9 and h/floors <= 3.05     -> "apt"       (apartment: floor height 2.8~3.0)
        floors >= 9                          -> "office"    (office: floor height 3.1~4.0)

    Basis for the 9-floor rule: apartment typical floor heights are
    **2.80~2.85** (certain, survey §3.1) and offices are taller. Measured over
    the 33 scenes it gets 15 of the 22 buildings with 9+ floors right (68 %).
    **When accuracy matters, override with `bd["kind"]`** — inference is only
    ever the default.

    The 4-floors-or-fewer branch (v1 fix: the former single criterion
    "footprint < 600 m2" was `[no source]` and misclassified a 24x6 m, 4-storey,
    h12 shop house as villa)::

      (1) **Size** — multi-family housing is "one building whose floor area used
         as housing totals **660 m2 or less** with **4 floors or fewer**"
         `[statute]` Building Act Enforcement Decree table 1, item 2(c).
         -> If footprint per floor x floor count exceeds 660, it cannot be
         multi-family.
      (2) **Depth** — unit depth = net area / frontage (4.50 = `BAY_VILLA`).
         Even a studio unit of 30 m2 net needs 6.7 m `[estimated, derived]`
         -> below **7.0 m** it is not housing but one-room-deep roadside retail.
         This is the criterion that separates the 24x6 m case (area and floor
         height alone cannot).
      (3) **Mean floor height** — the boundary `RESI_FH_MAX` **3.05** is
         **identical** to the value used by the 9+ floor branch (one unified
         boundary). Real multi-family mean floor heights are 2.7~3.0 and stay
         under 3.05, whereas mixing in ground-floor retail (3.9~4.2
         `[estimated]`) puts a 4-storey building around 3.4.

    All three criteria use only the existing `bd` keys (x0..y1, h, floors,
    axis). 0 prims.
    """
    d = float(dist) if dist is not None else float(bd.get("lod_dist", 0.0))
    if d > 80.0:
        return "backdrop"
    n = max(1, int(bd.get("floors", 1)))
    h = float(bd.get("h", n * FH_LEGAL))
    area = abs(float(bd["x1"]) - float(bd["x0"])) * \
        abs(float(bd["y1"]) - float(bd["y0"]))
    if n <= 1:
        return "low_shop"
    if n <= 4:
        if area * n > VILLA_GFA_MAX:        # (1) over the statutory size -> not multi-family
            return "shop_house"
        axis_y = (bd.get("axis", "y") == "y")
        depth = abs(float(bd["y1"]) - float(bd["y0"])) if axis_y else \
            abs(float(bd["x1"]) - float(bd["x0"]))
        if depth < VILLA_MIN_DEPTH:         # (2) depth too small for a unit plan
            return "shop_house"
        return "villa" if (h / n) <= RESI_FH_MAX else "shop_house"   # (3) floor height
    if n <= 8:
        return "office"
    return "apt" if (h / n) <= RESI_FH_MAX else "office"


def plan_levels(kind, total_h, floors, base_z=0.0):
    """List of each floor's **floor z** (length floors+1). The last element is
    the top floor's ceiling, i.e. the roof.

    Mandatory rule from survey §3.1: **only the ground floor has a different
    height**. The current even spacing `fstep = h/floors` is one of the big
    "reads as CG" axes and is slated for removal.

    `total_h` is nevertheless **left unchanged** (other scene code reads it), so
    only the per-type preferred `ground/typical` ratio is honoured and the
    result is scaled to the total height::

        r = ground_h_pref / floor_h_pref
        floor_h  = total_h / (r + floors - 1)
        ground_h = r * floor_h

    Sanity check: at r=1 this gives floor_h = total_h/floors, identical to the
    current behaviour.
    Returns: (levels, ground_h, floor_h). 0 prims.
    """
    n = max(1, int(floors))
    H = float(total_h)
    g, t = _KIND_FH.get(kind, (FH_LEGAL, FH_LEGAL))
    r = float(g) / float(t)
    fh = H / (r + n - 1)
    gh = r * fh
    return fk.floor_levels(n, fh, gh, base_z), gh, fh


# Preferred (ground-floor height, typical-floor height) per type. Only the ratio
# is used; absolute values are scaled to total_h.
_KIND_FH = {
    "shop_house": (FH_SHOP_G, FH_SHOP_U),   # [estimated] retail 4.0 / 3.3
    "apt":        (PILOTI_H, FH_APT),       # piloti 2.9 [estimated] / typical 2.80 (certain)
    "office":     (FH_LEGAL + 0.5, FH_LEGAL),  # [estimated] the lobby floor is taller
    "villa":      (PILOTI_H, FH_VILLA),     # piloti 2.9 [estimated] / 2.80 [knowledge]
    "low_shop":   (FH_SHOP_G, FH_SHOP_G),
    "backdrop":   (FH_LEGAL, FH_LEGAL),     # statutory conversion 4.0 m/floor
}


class Plan:
    """The **entirely pure-computed** layout plan for one building. 0 prims.

    `build_korean_building` builds a Plan and then merely executes it, which is
    what makes prim counts and coordinates verifiable without a stage
    (`selfcheck()`).
    """

    __slots__ = (
        "kind", "kind_raw", "tier", "dist", "seed",
        "x0", "x1", "y0", "y1", "base_z", "h", "top_z", "floors",
        "axis_y", "fdir", "plane", "Lx", "Ly", "W", "depth", "cx", "cy",
        "levels", "ground_h", "floor_h", "rows", "fac",
        "piloti", "n_col", "porch", "core_bays", "runs", "bay_w",
        "setback", "step_top", "rooftop", "tank", "antenna", "roof_sign",
        "shopfront", "awning", "signs", "balcony", "gas", "downpipe",
        "fire", "ac_mode", "ac_units", "opts",
        # --- computed, never bd switches -----------------------------------
        "mass",        # B-F1: solid volumes as (u0, u1, z0, z1, out_face)
        "n_bays",      # B-F2: shopfront bay count derived from W
        "d_true",      # B-F3: nearest judged eye -> facade rectangle [m]
        "z_ceil",      # B-F3: frame ceiling at d_true (backdrop policy (2))
        "in_frame",    # BS-4: any facade point inside +-30 deg of a judged eye
        "roof_allow",  # S01-F1: roof furniture height above top_z [m]
        "ridge",       # S01-F1: z of the highest prim the builders will emit
        "roof_under_ceil",   # S01-F1: opt-in clamp of the roof furniture to z_ceil
    )

    def __init__(self):
        for s in self.__slots__:
            setattr(self, s, None)

    def __repr__(self):
        return (f"<Plan {self.kind}/{self.tier} d={self.dist:.0f} "
                f"W={self.W:.1f} floors={self.floors} rows={self.rows}>")

    # -- B-F1: which surface is actually there at (u, z) --------------------
    def out_at(self, u0, u1, z0, z1):
        """Outward face of the **outermost solid volume** covering the facade
        window `[u0,u1] x [z0,z1]`, in `Facade` `out` units. 0 prims.

        Returns `0.0` (the facade plane) when nothing covers the window, and
        never less than 0.0: the reference surface for a facade attachment is at
        worst the plane the `bd` box declares. That floor is what keeps a
        set-back tower (`out = -1.20`) or a roof penthouse (`out ≈ -4`) from
        dragging an attachment *backwards* into the building.

        This is the single mechanism behind B-F1. Every `glass` / `sign` /
        `decal` placement asks it where the wall is instead of assuming the
        facade plane, which is why `selfcheck [11]` is green **by construction**
        rather than by per-site tuning.
        """
        o = 0.0
        for (a0, a1, b0, b1, face) in (self.mass or ()):
            if min(u1, a1) - max(u0, a0) > 1e-9 \
                    and min(z1, b1) - max(z0, b0) > 1e-9 and face > o:
                o = face
        return o


# **Plan switches** that may be read straight out of the `bd` dictionary. Only
# values a scene is allowed to toggle belong here. Derived geometry
# (x0..y1, W, levels, fac), the type (kind), the tier and the distance are
# computed results and must **never** be listed — listing them would undo the
# computation.
_BD_SWITCHES = frozenset((
    "rows", "piloti", "porch", "n_col", "core_bays", "bay_w",
    "setback", "step_top", "rooftop", "tank", "antenna", "roof_sign",
    "shopfront", "awning", "signs", "balcony", "gas", "downpipe",
    "fire", "ac_mode", "ac_units",
))


def _bd_plane(bd, axis_y):
    """Recover the facade plane from face_dir + the bounding box even when
    facade_x/facade_y are absent."""
    fd = float(bd.get("face_dir", -1.0))
    if axis_y:
        if "facade_y" in bd and bd["facade_y"] is not None:
            return float(bd["facade_y"])
        return float(bd["y1"] if fd > 0 else bd["y0"])
    if "facade_x" in bd and bd["facade_x"] is not None:
        return float(bd["facade_x"])
    return float(bd["x1"] if fd > 0 else bd["x0"])


def plan_building(bd, dist=None, kind=None, seed=None, eyes=None, **over):
    """`bd` -> `Plan`. **0 prims.** Every decision is made here.

    Distance priority: explicit `dist` -> `bd["lod_dist"]` -> **the judged eye
    set** (`eyes`, B-F3) -> `|facade plane coordinate|`. The last is the historical
    default and is wrong by construction — it assumes the camera sits at the
    origin. Pass `eyes=judged_eyes(gy)` (or set `bd["lod_dist"]`) and the tier is
    derived from the real geometry instead.

    `eyes` also drives **BS-4**: when no point of the facade falls inside ±30° of
    any judged eye, the building is demoted to `kind="backdrop"` (3–4 prims). An
    explicit `kind=`/`bd["kind"]` does **not** veto this — the whole point of the
    row is that a building nobody can see earns no facade — but passing
    `backdrop_demote=False` in `over` does, for the A/B control arm.

    With `eyes=None` (the default) nothing above applies and the plan is byte-for
    byte what it was before, which is what keeps this an unwired, zero-regression
    change.

    `over` can force any plan field (`piloti=False`, `rows=3`, ...). If `bd`
    carries an optional key of the same name, that is read too (so scenes can
    tune it).
    """
    backdrop_demote = bool(over.pop("backdrop_demote", True))
    p = Plan()
    p.x0 = float(min(bd["x0"], bd["x1"]))
    p.x1 = float(max(bd["x0"], bd["x1"]))
    p.y0 = float(min(bd["y0"], bd["y1"]))
    p.y1 = float(max(bd["y0"], bd["y1"]))
    p.base_z = float(bd.get("base_z", 0.0) or 0.0)
    p.h = float(bd["h"])
    p.top_z = p.base_z + p.h
    p.floors = max(1, int(bd["floors"]))
    p.Lx = p.x1 - p.x0
    p.Ly = p.y1 - p.y0
    p.cx = 0.5 * (p.x0 + p.x1)
    p.cy = 0.5 * (p.y0 + p.y1)
    p.axis_y = (bd.get("axis", "y") == "y")
    p.fdir = 1.0 if float(bd.get("face_dir", -1.0)) >= 0 else -1.0
    p.plane = _bd_plane(bd, p.axis_y)
    p.W = p.Lx if p.axis_y else p.Ly          # facade width
    p.depth = p.Ly if p.axis_y else p.Lx      # depth perpendicular to the facade

    # --- B-F3 / BS-4: the judged eye set ---------------------------------
    # `p.fac` is not built yet, so the two helpers are fed the facade rectangle
    # through the same Plan fields they read (`plane`, `axis_y`, `base_z`,
    # `top_z`) plus a provisional `fac`; see `_facade_rect`.
    p.fac = fk.Facade(p.plane, p.fdir, *((p.x0, p.x1) if p.axis_y
                                         else (p.y0, p.y1)),
                      base_z=p.base_z, axis_y=p.axis_y, depth_ref=p.depth)
    if eyes:
        p.d_true = eye_distance(p, eyes)
        p.in_frame = facade_in_frame(p, eyes)
        p.z_ceil = fk.frame_ceiling(p.d_true)

    if dist is None:
        dist = bd.get("lod_dist")
    if dist is None:
        dist = p.d_true                          # B-F3
    if dist is None:
        dist = abs(p.plane)
    p.dist = float(dist)
    p.tier = fk.lod_tier(p.dist)

    p.kind_raw = str(kind or bd.get("kind") or infer_kind(bd, p.dist))
    if p.kind_raw not in KINDS:
        p.kind_raw = infer_kind(bd, p.dist)
    # **Distance-driven type demotion** — requirement 1 — and **BS-4**: a facade
    # that never enters a judged frame earns the silhouette builder regardless of
    # how close it is.
    p.kind = "backdrop" if p.tier == "silhouette" else p.kind_raw
    if backdrop_demote and p.in_frame is False:
        p.kind = "backdrop"

    p.seed = int(seed) if seed is not None else _seed_of(
        p.kind, round(p.x0, 2), round(p.y0, 2), p.floors, round(p.h, 2))
    rng = _rng("plan", p.seed)

    p.levels, p.ground_h, p.floor_h = plan_levels(
        p.kind, p.h, p.floors, p.base_z)

    # --- Repeat count for windows/balconies (survey §6 LOD table + §4 prim
    #     reallocation rule) ------------------------------------------------
    cap = ROW_CAP[p.tier]
    if cap <= 0:
        p.rows = 0
    else:
        vis = fk.window_rows_visible(p.dist, p.floor_h, p.floors,
                                     ground_h=p.ground_h, base_z=p.base_z,
                                     near_dist=20.0, min_rows=2)
        p.rows = int(_clamp(min(vis, p.floors), 1, cap))

    # --- Per-type default switches ---------------------------------------
    k, t = p.kind, p.tier
    near = (t == "near")
    midp = (t in ("near", "mid"))

    p.piloti = (k in ("apt", "villa")) and midp and p.depth > (
        PILOTI_PORCH * 0.6 + 1.0) and p.ground_h >= PILOTI_CLEAR + 0.2
    p.porch = min(PILOTI_PORCH, max(2.0, p.depth * 0.45))
    p.n_col = int(_clamp(round(p.W / PILOTI_PITCH), 2, 5)) if p.piloti else 0

    # Core bays — apartments only. Two of them above 26 m width [knowledge]
    p.core_bays = (1 if p.W < 26.0 else 2) if (k == "apt" and t != "silhouette") \
        else 0
    p.bay_w = {"apt": BAY_APT, "villa": BAY_VILLA}.get(k, BAY_SHOP)
    p.runs = _unit_runs(p.fac.u0, p.fac.u1, p.core_bays, CORE_W)

    p.setback = SETBACK_OFFICE if (k == "office" and p.floors >= 4) else 0.0
    # Northern daylight setback steps — **residential type (villa) only**.
    # Commercial zones are outside §61(1).
    p.step_top = (k == "villa" and p.h > DAYLIGHT_STEP_Z + 1.0
                  and p.floors >= 4)

    p.rooftop = (k != "backdrop") or True          # penthouse on every type and tier
    # Older low-rise = candidate for a water tank and antenna, but only at
    # **3 floors or more**.
    #  - An elevated tank exists to give upper floors water pressure, so it is
    #    absent from the roofs of 1~2 storey retail where direct supply
    #    suffices `[knowledge]` (source: Mechanical Facilities News — the shift
    #    to booster-pump direct supply).
    #  - An antenna on a single-storey shop roof has no functional
    #    justification and would violate v5.2 §6 "empty is the default —
    #    functionally required items only, no decoration".
    old = (k in ("villa", "shop_house", "low_shop")) and p.floors >= 3
    p.tank = old and midp and rng.random() < 0.55
    p.antenna = old and near
    lo, hi = ROOFSIGN_FLOORS
    p.roof_sign = (k in ("shop_house", "office") and lo <= p.floors <= hi
                   and t in ("mid", "far") and rng.random() < 0.34)

    # Shopfronts only up to near and mid. Survey §6's LOD table states flatly
    # that **">40 m: lower floors = plinth only"**, yet the former condition
    # (`t != "silhouette"`) still built full glazing, kickplates and doors at
    # far (40~80 m). That contradicted the table and was the direct cause of
    # the low_shop/far budget overrun (9>7). At d=55 m a single glazing panel
    # is a few pixels wide on screen.
    p.shopfront = k in ("shop_house", "low_shop") and t in ("near", "mid")
    p.awning = k in ("shop_house", "low_shop") and near
    p.signs = 2 if (k in ("shop_house", "low_shop") and near) else (
        1 if (k in ("shop_house", "low_shop") and t == "mid") else 0)
    p.balcony = (k == "apt" and t != "silhouette")
    p.gas = (k == "villa" and midp)         # exposed gas piping = the multi-family signature
    p.downpipe = 2 if near else (1 if t == "mid" else 0)
    p.fire = midp and p.floors >= 2 and k != "backdrop"
    if k in ("shop_house", "low_shop"):
        p.ac_mode, p.ac_units = "eaves", (4 if near else (2 if t == "mid" else 0))
    elif k == "villa":
        p.ac_mode, p.ac_units = "perfloor", (5 if near else (3 if t == "mid" else 0))
    else:
        p.ac_mode, p.ac_units = None, 0     # new apartments house them in the balcony (§3.4 a)

    # Apply optional bd keys and explicit overrides.
    # **Whitelist only** (`_BD_SWITCHES`). Previously the loop walked all of
    # `p.__slots__` and overwrote each with the same-named bd key, which undid
    # what had just been computed and broke two things:
    #   (1) `kind` — bd["kind"] resurrected the d>80 demotion
    #      (`p.kind = "backdrop"`), so distant buildings were assembled by a
    #      near-type builder (the cause of selfcheck [5] failing).
    #   (2) `x0..y1` — coordinates normalized above via min/max were reverted to
    #      the originals, so passing a flipped bd (x0>x1) produced boxes of
    #      negative size.
    # No information is lost: the type already arrives via the
    # `bd["kind"]` -> `p.kind_raw` path.
    for key in _BD_SWITCHES:
        if key in bd:
            setattr(p, key, bd[key])
    for key, val in over.items():
        if key in p.__slots__:
            setattr(p, key, val)
    p.opts = dict(over)

    # --- Derived from the *final* switch values ---------------------------
    # `runs` is a function of `core_bays`, which is a bd switch, so it has to be
    # recomputed here or a scene that passes `core_bays` gets a stale run list
    # (and, since B-F1, a `mass` list that disagrees with the built cores).
    p.runs = _unit_runs(p.fac.u0, p.fac.u1, p.core_bays, CORE_W)
    p.n_bays = shopfront_bays(p.W, p.tier) if p.shopfront else 0   # B-F2
    p.mass = mass_faces(p)                                          # B-F1
    if p.roof_under_ceil is None:
        p.roof_under_ceil = False
    p.roof_allow = roof_allow(p)                                    # S01-F1
    p.ridge = p.top_z + p.roof_allow                                # S01-F1
    return p


def backdrop_penthouse(p):
    """The backdrop penthouse footprint `(pw, pdp)`, or `None`. 0 prims.

    Second expression of `_b_backdrop`'s own three lines, and deterministic there
    (unlike `build_rooftop`, which draws the footprint from an rng seeded on the
    **prim prefix**). Having it as a function is what lets `plan_building` state an
    **exact** ridge for `kind="backdrop"` instead of a bound.
    """
    side = math.sqrt(max(0.5, p.Lx * p.Ly * PH_AREA_FRAC)) * 0.85
    pw = min(side, p.Lx * 0.5, 8.0)
    pdp = min(side, p.Ly * 0.5, 8.0)
    return (pw, pdp) if (pw > 1.2 and pdp > 1.2) else None


# A penthouse shorter than this is not a penthouse — it is a plinth on a roof.
# When the `roof_under_ceil` clamp cannot leave at least this much, the penthouse
# is dropped instead of squashed.
PH_MIN_H = 1.00


def backdrop_ph_h(p):
    """Penthouse height `_b_backdrop` will actually build [m]. 0 prims.

    `PH_H` normally. With the **opt-in** `roof_under_ceil=True` it is clamped so the
    penthouse top lands on `z_ceil`, which is the "clamp the roof elements" half of
    S01-F1's remedy.

    **Why the clamp is opt-in and not the default.** Measured on this tree
    (`_b_backdrop` probe, isolated arm at `4bae470`, all 33 scenes): of the **33**
    backdrop blocks that are planned with a judged eye set, only scene01's **6** keep
    their ridge under `z_ceil` (by 0.449–0.573 m). scene02 (10), scene08 (5) and
    scene16 (12) sit **+10.645 to +38.706 m above** it — deliberately, and scene16's
    own code says so in as many
    words: *"policy (2) is written for a building the camera faces, not for a wall it
    travels along"*, a downtown street wall that is supposed to close the horizon.
    Defaulting this clamp on would delete 27 of 33 blocks' skylines to satisfy a rule
    those scenes have argued their way out of on the record. So the kit's default duty
    is to **tell the truth** (`p.ridge`, which is what scene01 actually needed and had
    to hand-derive as a scene-local constant), and the clamp is there for the caller
    who wants policy (2) enforced rather than merely checked.
    """
    if p.roof_under_ceil and p.z_ceil is not None:
        return max(0.0, min(PH_H, float(p.z_ceil) - p.top_z))
    return PH_H


def roof_allow(p):
    """Height of the roof furniture **above `top_z`** [m]. 0 prims.

    **This is finding S01-F1's fix.** `building_kit`'s total-height invariant is
    *"the top of the shell stays at `base_z + h`"*, and backdrop policy (2) says
    *"build nothing above `z_ceil`"* — but `build_rooftop` and `_b_backdrop` both
    emit a parapet band and a penthouse **above** `top_z`, and policy (2) never
    gated them. A caller that sized a backdrop from `h` — which is what the
    invariant tells it to do — shipped a mass **+2.90 m** taller than the ceiling
    it had just checked against. scene01 measured exactly that on all six of its
    blocks, printed *"sky above roof 6/6"*, and rendered a brick wall running off
    the top edge of `h0.3_d10`; it now carries a scene-local `ROOF_ALLOW` constant
    to work around the kit. This function is that constant, computed rather than
    copied, so the next caller does not have to rediscover it.

    `kind="backdrop"` -> **exact**: `_b_backdrop` uses no rng for the penthouse.
    Every other kind -> an **upper bound**, because `build_rooftop` jitters the
    penthouse height +-8 % off `_rng(prefix, "roof", seed)` and the prim prefix does
    not exist at plan time. A bound is the honest answer for "will this break
    frame?", and `selfcheck [12]` asserts emitted <= bound for every kind x tier.
    """
    if p.kind == "backdrop":
        if backdrop_penthouse(p) is None:
            return RAIL_H
        ph = backdrop_ph_h(p)
        # The parapet is statutory 1.20 m and is **not** clamped: a shell whose own
        # parapet already breaks the ceiling is too tall, and the fix for that is the
        # caller's `h`, not a sub-statutory railing.
        return max(RAIL_H, ph if ph >= PH_MIN_H else 0.0)
    allow = RAIL_H                                   # parapet, always emitted
    area_max = p.Lx * p.Ly * PH_AREA_FRAC
    # `build_rooftop`'s footprint gate, evaluated at the rng's most generous draw
    # (uniform 0.72..1.0 -> take 1.0; pdp grows as pw shrinks, so 1.0 bounds both).
    side = math.sqrt(max(0.5, area_max))
    pw = min(side, p.Lx * 0.5, 8.0)
    pdp = min(max(0.5, area_max / max(0.5, pw)), p.Ly * 0.5, 8.0)
    if pw > 1.4 and pdp > 1.4:
        ph = PH_H * 1.08                             # `_jit`'s hard +-8 % ceiling
        allow = max(allow, ph + (ANT_H if p.antenna else 0.0))
        if p.tier in ("near", "mid"):
            allow = max(allow, ph + 0.09 + 0.18 / 2.0)   # PenthouseCap top
    if p.roof_sign:
        allow = max(allow, RAIL_H + min(3.5, ROOFSIGN_H_MAX, p.h * 0.5))
    return allow


def mass_faces(p):
    """**Pure** description of every solid volume of building `p`, as
    `[(u0, u1, z0, z1, out_face), ...]` in facade coordinates. 0 prims.

    `out_face` is the outward distance of the volume's outermost face from
    `p.plane` — 0.0 for a volume flush with the facade plane, negative for a
    set-back one, `CORE_PROUD` for a protruding core.

    This mirrors the conditionals of `build_mass`, `build_core` and
    `_b_backdrop`. It is a **second expression of the same geometry**, so
    `selfcheck [11a]` cross-validates it prim-for-prim against the boxes those
    builders actually emit, for every kind x tier. A silent divergence here would
    make the visibility check lie, which is the one failure mode that matters.

    Excluded on purpose: `PilotiCol` (a 0.45 m column, not a wall — role `stone`,
    and no glazing is built in the piloti band) and `Parapet` (above `top_z`).
    """
    out = []
    if p.kind == "backdrop":
        # `_b_backdrop` does not call `build_mass`; it splits at 0.72*h instead.
        if p.floors >= 12:
            z_mid = p.base_z + p.h * 0.72
            out.append((p.fac.u0, p.fac.u1, p.base_z, z_mid, 0.0))
            out.append((p.fac.u0, p.fac.u1, z_mid, p.top_z,
                        -min(2.0, p.depth * 0.2)))
        else:
            out.append((p.fac.u0, p.fac.u1, p.base_z, p.top_z, 0.0))
        return out
    z_bot = p.base_z
    if p.piloti:
        z_bot = p.base_z + min(p.ground_h, PILOTI_H + 0.4)
        if (p.depth - p.porch) > 0.4:
            # `_inner_range(p, porch)` insets the facade-normal axis only.
            out.append((p.fac.u0, p.fac.u1, p.base_z, z_bot, -float(p.porch)))
    if p.step_top:
        z_step = p.base_z + DAYLIGHT_STEP_Z
        out.append((p.fac.u0, p.fac.u1, z_bot, z_step, 0.0))
        out.append((p.fac.u0, p.fac.u1, z_step, p.top_z, -DAYLIGHT_STEP_IN))
    elif p.setback > 0.0:
        z_pod = min(p.levels[min(2, p.floors)], p.top_z - 0.5)
        out.append((p.fac.u0, p.fac.u1, z_bot, z_pod, 0.0))
        out.append((p.fac.u0, p.fac.u1, z_bot, p.top_z, -float(p.setback)))
    else:
        out.append((p.fac.u0, p.fac.u1, z_bot, p.top_z, 0.0))
    # Protruding stair/lift cores. `build_core` is called from `_b_apt` only, so
    # the kind is tested here too — otherwise a scene that forces `core_bays` on a
    # non-apt bd would make `out_at` promise a core that never gets built.
    if p.kind == "apt":
        _, core_us = p.runs if isinstance(p.runs, tuple) else (None, [])
        for u in core_us:
            out.append((u - CORE_W / 2.0, u + CORE_W / 2.0,
                        p.base_z, p.top_z, CORE_PROUD))
    return out


def _unit_runs(u0, u1, n_core, core_w):
    """List of **unit runs** [(ua, ub), ...] with cores wedged between them,
    plus the cores' u centres.

    Returns (runs, core_us). With n_core=0, runs=[(u0,u1)] and core_us=[].
    n_core=1 -> [run][core][run]; n_core=2 -> [run][core][run][core][run].
    Distributing the cores evenly is what breaks the facade rhythm the way a
    real slab block does (survey §3.2).
    0 prims.
    """
    W = float(u1) - float(u0)
    n = max(0, int(n_core))
    if n == 0 or W - n * core_w < 3.0:
        return [(float(u0), float(u1))], []
    wr = (W - n * core_w) / (n + 1)
    runs, cores, u = [], [], float(u0)
    for i in range(n + 1):
        runs.append((u, u + wr))
        u += wr
        if i < n:
            cores.append(u + core_w / 2.0)
            u += core_w
    return runs, cores


# ===========================================================================
# [4] Mass builders — these actually create prims
# ===========================================================================
def _box(K, stage, path, c, s, mtl, collider=False):
    return K.box(stage, path, c, s, mtl, collider)


def _span_center_size(a0, a1, b0, b1, z0, z1, axis_y_is_x=True):
    """(x range, y range, z range) -> (center, size)."""
    return ((0.5 * (a0 + a1), 0.5 * (b0 + b1), 0.5 * (z0 + z1)),
            (abs(a1 - a0), abs(b1 - b0), abs(z1 - z0)))


def _inner_range(p, inset):
    """Footprint (x0,x1,y0,y1) pulled in by `inset` on the facade side."""
    x0, x1, y0, y1 = p.x0, p.x1, p.y0, p.y1
    if p.axis_y:
        if p.fdir > 0:
            y1 -= inset
        else:
            y0 += inset
    else:
        if p.fdir > 0:
            x1 -= inset
        else:
            x0 += inset
    return x0, x1, y0, y1


def build_mass(K, stage, prefix, p, M):
    """The mass (volumes). **1~3 boxes** depending on type. Includes piloti,
    setback and the daylight step.

    Prims
      base 1, office podium setback +1, villa daylight step +1,
      piloti (apt/villa at near/mid) lifts the shell and adds
      **1 rear wall + n_col columns**
    """
    prims = []
    z_bot = p.base_z
    if p.piloti:
        z_bot = p.base_z + min(p.ground_h, PILOTI_H + 0.4)
        # Piloti rear wall — only the open depth `porch` is cleared; the rest
        # stays solid (collider retained).
        rx0, rx1, ry0, ry1 = _inner_range(p, p.porch)
        if (rx1 - rx0) > 0.4 and (ry1 - ry0) > 0.4:
            c, s = _span_center_size(rx0, rx1, ry0, ry1, p.base_z, z_bot)
            prims.append(_box(K, stage, f"{prefix}/PilotiRear", c, s,
                              M.dark, True))
        # Columns — lined up at the open end (facade side). The statutory
        # 2.10 clear height is preserved.
        for i in range(p.n_col):
            u = p.fac.u0 + (i + 0.5) * p.W / max(1, p.n_col)
            c = p.fac.world(u, PILOTI_COL * 0.5 + 0.05,
                            p.base_z + (z_bot - p.base_z) / 2.0)
            s = p.fac.size(PILOTI_COL, PILOTI_COL, z_bot - p.base_z)
            prims.append(_box(K, stage, f"{prefix}/PilotiCol_{i}", c, s,
                              M.stone, True))

    z_top = p.top_z
    if p.step_top:
        # Northern daylight setback (Enforcement Decree §86(1)) steps — the
        # portion above 10 m is set back.
        z_step = p.base_z + DAYLIGHT_STEP_Z
        # lower mass
        c, s = _span_center_size(p.x0, p.x1, p.y0, p.y1, z_bot, z_step)
        prims.append(_box(K, stage, f"{prefix}/Shell", c, s, M.shell, True))
        sx0, sx1, sy0, sy1 = _inner_range(p, DAYLIGHT_STEP_IN)
        c, s = _span_center_size(sx0, sx1, sy0, sy1, z_step, z_top)
        prims.append(_box(K, stage, f"{prefix}/ShellStep", c, s, M.shell, True))
    elif p.setback > 0.0:
        # Office podium setback — the podium (2 floors) keeps the full
        # footprint, the tower is set back.
        z_pod = min(p.levels[min(2, p.floors)], z_top - 0.5)
        c, s = _span_center_size(p.x0, p.x1, p.y0, p.y1, z_bot, z_pod)
        prims.append(_box(K, stage, f"{prefix}/Podium", c, s, M.shell, True))
        sx0, sx1, sy0, sy1 = _inner_range(p, p.setback)
        c, s = _span_center_size(sx0, sx1, sy0, sy1, z_bot, z_top)
        prims.append(_box(K, stage, f"{prefix}/Shell", c, s, M.shell, True))
    else:
        c, s = _span_center_size(p.x0, p.x1, p.y0, p.y1, z_bot, z_top)
        prims.append(_box(K, stage, f"{prefix}/Shell", c, s, M.shell, True))
    return prims


def build_core(K, stage, prefix, p, M):
    """**Protruding** stair/lift core + tall narrow window + entrance door.
    2~3 prims per core.

    Survey §3.2: "the stair/lift core between units (width 2.5~3.5) is the
    decisive element that breaks the facade rhythm, and it is absent today."
    Cores have almost no windows, or **tall narrow** ones.

    **Integration caveat**: the core extends `CORE_PROUD` (0.60) beyond the bd
    bounding box on the facade side. That is not a new constraint, since
    balconies on the same facade already extend the statutory 1.50, but it does
    become an underestimate in scenes whose occlusion checks use only the bd
    box.
    """
    prims = []
    _, core_us = p.runs if isinstance(p.runs, tuple) else (None, [])
    for i, u in enumerate(core_us):
        h = p.top_z - p.base_z
        prims.append(_box(
            K, stage, f"{prefix}/Core_{i}",
            p.fac.world(u, CORE_PROUD / 2.0, p.base_z + h / 2.0),
            p.fac.size(CORE_W, CORE_PROUD, h), M.shell, True))
        # Tall narrow stairwell window — one strip from above floor 1 to below the roof
        zw0 = p.levels[min(1, p.floors)] + 0.4
        zw1 = p.top_z - 0.5
        if zw1 - zw0 > 1.0:
            # **B-F1**: `CORE_PROUD − 0.05` put the 0.04-thick strip's outer face
            # 30 mm *inside* the core it belongs to — buried, and missed by the
            # 135/135 suite because its `out` was positive. It now sits 5 mm proud
            # of whatever surface `out_at` reports at this window.
            t = 0.04
            wo = p.out_at(u - CORE_WIN_W / 2.0, u + CORE_WIN_W / 2.0, zw0, zw1)
            prims.append(_box(
                K, stage, f"{prefix}/CoreStrip_{i}",
                p.fac.world(u, wo + fk.WALL_PROUD + t / 2.0, (zw0 + zw1) / 2.0),
                p.fac.size(CORE_WIN_W, t, zw1 - zw0), M.glass))
        if p.tier == "near":
            # Communal entrance — the 2.10 height is a **scale anchor**. Never randomize.
            t = 0.06
            wo = p.out_at(u - 0.80, u + 0.80, p.base_z, p.base_z + DOOR_H)
            prims.append(_box(
                K, stage, f"{prefix}/CoreDoor_{i}",
                p.fac.world(u, wo + fk.WALL_PROUD + t / 2.0,
                            p.base_z + DOOR_H / 2.0),
                p.fac.size(1.60, t, DOOR_H), M.glass))
    return prims


def build_rooftop(K, stage, prefix, p, M):
    """Parapet + penthouse + (older stock only) water tank and antenna +
    (floors 5~15 only) roof sign.

    Prims: parapet 1 + penthouse 1~2 + water tank 0~1 + antenna 0~1 +
    roof sign 0~1.

    Statutory basis
      - Parapet (roof railing) **at least 1.2 m** — Building Act Enforcement
        Decree §40. The current 0.5 fell short of the rule, and the distant
        silhouette was flattened by exactly that much.
      - A penthouse whose horizontal projection is **<= 1/8 of the building
        area** and whose height is **<= 12 m** is excluded from the floor count
        and height — Building Act Enforcement Decree §119 (1)5, 9. -> the
        footprint cap is used verbatim.
      - Roof signage on **floors 5~15**, maximum length **30 m**, height
        **<= 15 m and at most half the building height** — Outdoor
        Advertisements Act Enforcement Decree §15.

    The water tank goes on **older low-rise buildings only**. Putting one on a
    new apartment roof is actively wrong (source: Mechanical Facilities News —
    the shift to booster-pump direct supply).
    The penthouse sits not at the roof centre but **offset toward the core
    axis** (survey §3.5).
    """
    prims = []
    rng = _rng(prefix, "roof", p.seed)
    zt = p.top_z

    # --- Parapet (statutory 1.20) ----------------------------------------
    prims.append(_box(K, stage, f"{prefix}/Parapet",
                      (p.cx, p.cy, zt + RAIL_H / 2.0),
                      (p.Lx + 0.20, p.Ly + 0.20, RAIL_H), M.parapet))

    # --- Penthouse (statutory 1/8 cap) -----------------------------------
    area_max = p.Lx * p.Ly * PH_AREA_FRAC
    side = math.sqrt(max(0.5, area_max)) * rng.uniform(0.72, 1.0)
    pw = min(side, p.Lx * 0.5, 8.0)
    pdp = min(max(0.5, area_max / max(0.5, pw)), p.Ly * 0.5, 8.0)
    if pw > 1.4 and pdp > 1.4:
        ph = _jit(rng, PH_H)                    # +-8 % — small regardless of the statutory 12 m
        # offset toward the core axis
        ox = p.cx + (p.Lx * 0.5 - pw * 0.5 - 0.6) * rng.uniform(-0.8, 0.8)
        oy = p.cy + (p.Ly * 0.5 - pdp * 0.5 - 0.6) * rng.uniform(-0.8, 0.8)
        prims.append(_box(K, stage, f"{prefix}/Penthouse",
                          (ox, oy, zt + ph / 2.0), (pw, pdp, ph), M.shell))
        if p.tier in ("near", "mid"):
            prims.append(_box(K, stage, f"{prefix}/PenthouseCap",
                              (ox, oy, zt + ph + 0.09),
                              (pw + 0.24, pdp + 0.24, 0.18), M.parapet))
        if p.tank:
            prims.append(K.cyl(stage, f"{prefix}/WaterTank",
                               (ox + pw * 0.5 + TANK_R + 0.3, oy,
                                zt + 0.35 + TANK_H / 2.0),
                               TANK_R, TANK_H, M.metal))
        if p.antenna:
            prims.append(K.cyl(stage, f"{prefix}/Antenna",
                               (ox - pw * 0.4, oy + pdp * 0.3,
                                zt + ph + ANT_H / 2.0),
                               0.035, ANT_H, M.metal))

    # --- Roof sign (statutory dimensions) --------------------------------
    if p.roof_sign:
        ln = min(p.W * 0.8, ROOFSIGN_LEN_MAX)
        sh = min(3.5, ROOFSIGN_H_MAX, p.h * 0.5)
        if ln > 3.0 and sh > 1.0:
            prims.append(_box(
                K, stage, f"{prefix}/RoofSign",
                p.fac.world(p.fac.mid, -0.6, zt + RAIL_H + sh / 2.0),
                p.fac.size(ln, 0.25, sh), M.sign))
    return prims


def build_window_bands(K, stage, prefix, p, M, mode="bay"):
    """Windows. **No uniform grid** (survey §3.2).

    mode
      "bay"        windows per unit bay. `nb` per floor (nb = run width / bay
                   width, capped at 4). Upper floors of shop_house, villa and
                   low_shop.
      "band"       one horizontal window band per floor. **Office mid LOD** —
                   1 prim per floor.
      "curtain"    curtain wall: one glazing sheet + a mullion band per floor.
                   Office near/mid.

    Prims
      bay     -> rows x nb          (nb <= 4)
      band    -> rows
      curtain -> 1 + rows

    The current `col_step` grid produced 8~9 per floor on a 24 m facade. bay
    mode gives 3~4 per floor and band/curtain give 1. This is the bulk of the
    window-prim saving.
    """
    prims = []
    rows = int(p.rows or 0)
    if rows <= 0 or p.W < 2.0:
        return prims
    lv = p.levels
    f0 = 1 if p.kind in ("shop_house", "low_shop", "apt", "villa") else 0
    f0 = min(f0, max(0, p.floors - 1))
    idx = [f for f in range(f0, min(p.floors, f0 + rows))]
    if not idx:
        return prims

    # **B-F1** — every glazing prim below asked `Facade.world` for a *negative*
    # `out`, i.e. it was pushed **into** a solid mass box. Survey R3 §5.1 measured
    # 62 of 62 GLASS prims invisible across 5 types x 4 tiers. `out_at` reports the
    # outward face of whatever volume actually covers the window (the shell, an
    # office podium in front of a set-back tower, a protruding core), and the
    # glazing sits `fk.WALL_PROUD` = 5 mm outside it.
    u0, u1 = p.fac.u0, p.fac.u1

    if mode == "curtain":
        z0 = lv[idx[0]] + 0.6
        z1 = min(lv[idx[-1]] + p.floor_h - 0.3, p.top_z - 0.3)
        wo = p.out_at(u0, u1, z0, z1)
        if z1 - z0 > 1.0:
            t = 0.05
            prims.append(_box(
                K, stage, f"{prefix}/CurtainGlass",
                p.fac.world(p.fac.mid, wo + fk.WALL_PROUD + t / 2.0,
                            (z0 + z1) / 2.0),
                p.fac.size(p.W - 0.8, t, z1 - z0), M.glass))
        for j, f in enumerate(idx):
            zb = lv[f] - 0.10
            if zb <= p.base_z + 0.2:
                continue
            # The mullion band rides the same reference so it stays proud of the
            # glass it is supposed to shade (0.10 out vs the glass's 0.055).
            prims.append(_box(
                K, stage, f"{prefix}/Mullion_{f}",
                p.fac.world(p.fac.mid, wo + 0.04, zb),
                p.fac.size(p.W - 0.6, 0.12, 0.30), M.parapet))
        return prims

    if mode == "band":
        t, bh = 0.04, 1.40
        for f in idx:
            zc = lv[f] + min(1.6, p.floor_h * 0.55)
            wo = p.out_at(u0, u1, zc - bh / 2.0, zc + bh / 2.0)
            prims.append(_box(
                K, stage, f"{prefix}/WinBand_{f}",
                p.fac.world(p.fac.mid, wo + fk.WALL_PROUD + t / 2.0, zc),
                p.fac.size(p.W - 2.0, t, bh), M.glass))
        return prims

    # --- bay mode --------------------------------------------------------
    # Sash maximum 1.50 x 2.70 (certain — KCC/Eagon). Bedroom window
    # 1.5~1.8 x 1.4~1.5 [knowledge].
    nb = int(_clamp(round((p.W - 1.6) / max(2.5, p.bay_w)), 1, 4))
    bw = (p.W - 1.6) / nb
    ww = min(1.70, bw * 0.55)
    wh = 1.45
    t = 0.04
    for f in idx:
        zc = lv[f] + 0.90 + wh / 2.0          # sill 0.90 [estimated]
        for b in range(nb):
            u = p.fac.u0 + 0.8 + (b + 0.5) * bw
            wo = p.out_at(u - ww / 2.0, u + ww / 2.0,
                          zc - wh / 2.0, zc + wh / 2.0)
            prims.append(_box(
                K, stage, f"{prefix}/Win_{f}_{b}",
                p.fac.world(u, wo + fk.WALL_PROUD + t / 2.0, zc),
                p.fac.size(ww, t, wh), M.glass))
    return prims


def build_balconies(K, stage, prefix, p, M):
    """Stacked balconies. **Calls `fk.build_balcony_stack` once per unit run.**

    facade_kit's `core_every` assumes uniform bays and cannot produce the mixed
    "core width 3.0 + unit width 9.0" rhythm, so the runs between cores are cut
    out and passed individually.

    Prims = sum over runs of (nb_run x (rows-1) x 2) + (upper vertical strips =
    total bay count)

    **Upper vertical strips**: above `rows`, per-floor slabs and railings are
    compressed into **one vertical box per bay**. On a 15-storey apartment the
    per-floor version costs 30 prims per unit; the strip costs 1. That region
    sits far above the top of the judging frame (d=34 m -> 5.1 m), so §1.3's
    conclusion is that leaving only the silhouette is enough.
    """
    prims = []
    runs, _ = p.runs if isinstance(p.runs, tuple) else ([(p.fac.u0, p.fac.u1)], [])
    rows = int(p.rows or 0)
    if rows <= 1:
        rows = 2                                # at least one floor gets a real balcony
    n_bay_total = 0
    for i, (ua, ub) in enumerate(runs):
        if ub - ua < 3.0:
            continue
        sub = fk.Facade(p.plane, p.fdir, ua, ub, p.base_z, p.axis_y,
                        depth_ref=p.depth)
        nb = max(1, int(round((ub - ua) / max(3.0, p.bay_w))))
        n_bay_total += nb
        prims += fk.build_balcony_stack(
            K, stage, f"{prefix}/Run{i}", sub, p.levels, M.parapet, M.parapet,
            bay_w=p.bay_w, core_every=0, start_floor=1,
            max_floors=rows, balusters=False, seed=p.seed + i)
        # upper compressed strip
        z0 = p.levels[min(rows, p.floors)]
        z1 = p.top_z
        if z1 - z0 > 1.5:
            bw = (ub - ua) / nb
            for b in range(nb):
                u = ua + (b + 0.5) * bw
                prims.append(_box(
                    K, stage, f"{prefix}/BalStrip_{i}_{b}",
                    sub.world(u, fk.BALCONY_DEPTH * 0.5, (z0 + z1) / 2.0),
                    sub.size(bw - 0.30, fk.BALCONY_DEPTH, z1 - z0), M.parapet))
    return prims


def build_awning(K, stage, prefix, p, M):
    """Awning — above the ground-floor shop. **1 prim.**

    Statutory (Seoul Outdoor Advertisements Ordinance): projection **within
    1.00 when occupying the road**, **within 0.70 when not**. Mounting height
    at the lower edge 2.4~2.8 `[knowledge]`, tilted 15~25 deg downward
    `[knowledge]` — the tilt would need a rotated prim and is therefore **not
    implemented** (prim budget takes priority).
    """
    out = AWNING_OUT_ROAD
    zc = p.base_z + AWNING_Z + 0.06
    if zc > p.top_z - 0.3:
        return []
    return [_box(K, stage, f"{prefix}/Awning",
                 p.fac.world(p.fac.mid, out / 2.0, zc),
                 p.fac.size(min(p.W - 1.0, 12.0), out, 0.12), M.sign)]


def build_ext_stair(K, stage, prefix, p, M):
    """Exposed external stair — the signature of shop houses and villas.
    **3 prims.**

    Statutory (Housing Construction Standards §16): external stair riser
    **<= 0.20**, tread **>= 0.24** (steeper than an internal stair). Making
    each step a prim would cost 15~18 per floor and blow the budget -> it is
    compressed into **1 sloped stringer + 1 landing + 1 railing**.
    If a rotated prim (`oriented_box`) has been injected, the sloped slab is
    actually tilted.
    The railing height **1.20** (statutory §40) is a scale anchor: never
    randomize.
    """
    prims = []
    z0 = p.base_z
    z1 = p.levels[min(2, p.floors)]
    if z1 - z0 < 2.0 or p.W < 6.0:
        return prims
    u = p.fac.u1 - 1.6
    run = (z1 - z0) / 0.55                      # slope about 29 deg [estimated]
    run = _clamp(run, 3.0, 7.0)
    out = 1.30                                  # stair clear width 1.2 + slack [estimated]
    if K.oriented_box is not None:
        ang = math.degrees(math.atan2(z1 - z0, run))
        c = p.fac.world(u, out / 2.0, (z0 + z1) / 2.0)
        s = p.fac.size(math.hypot(run, z1 - z0), out, 0.22)
        prims.append(K.oriented_box(stage, f"{prefix}/ExtStairSlab", c, s,
                                    M.stone, False, 0.0, -ang))
    else:
        prims.append(_box(K, stage, f"{prefix}/ExtStairSlab",
                          p.fac.world(u, out / 2.0, (z0 + z1) / 2.0),
                          p.fac.size(run, out, 0.22), M.stone))
    prims.append(_box(K, stage, f"{prefix}/ExtStairLanding",
                      p.fac.world(u, out / 2.0, z1 - 0.11),
                      p.fac.size(1.30, out, 0.22), M.stone))
    prims.append(_box(K, stage, f"{prefix}/ExtStairRail",
                      p.fac.world(u, out - 0.05, (z0 + z1) / 2.0 + RAIL_H / 2.0),
                      p.fac.size(run, 0.05, RAIL_H), M.metal))
    return prims


def build_meter_box(K, stage, prefix, p, M):
    """Meter box — lower floors of multi-family housing. **1 prim.**
    Dimensions `[no source]` (no manufacturer standard obtained) ->
    0.60 x 0.20 x 0.70, bottom at +1.10 `[estimated]`.
    Survey §3.4(c) lists "meter box, hydrant, siamese connection" as mandatory
    multi-family attachments, and the statutory mounting height for a standpipe
    siamese connection is **ground +0.50~1.00**, so this sits above that.
    """
    return [_box(K, stage, f"{prefix}/MeterBox",
                 p.fac.world(p.fac.u0 + 1.2, 0.11, p.base_z + 1.10 + 0.35),
                 p.fac.size(0.60, 0.22, 0.70), M.metal)]


def build_entrance(K, stage, prefix, p, M, canopy=True):
    """Main entrance of a business facility — full glazing + canopy.
    **1~3 prims.**
    The door height is raised only to 2.40, as a two-leaf automatic door built
    off the **2.10 scale anchor**.
    Canopy projection 2.0 `[estimated]` — survey §5, "granite podium, large
    canopy".
    """
    prims = []
    u = p.fac.mid
    dh = 2.40                                   # [estimated] automatic-door clear height
    t = 0.06
    # **B-F1** — was `out = −0.10`, which buried the entrance inside the office
    # podium (the podium keeps the full footprint while the tower is set back
    # `SETBACK_OFFICE`, so the podium face is the surface that counts here).
    wo = p.out_at(u - 1.80, u + 1.80, p.base_z, p.base_z + dh)
    prims.append(_box(K, stage, f"{prefix}/EntryGlass",
                      p.fac.world(u, wo + fk.WALL_PROUD + t / 2.0,
                                  p.base_z + dh / 2.0),
                      p.fac.size(3.60, t, dh), M.glass))
    if canopy:
        out = 2.00
        prims.append(_box(K, stage, f"{prefix}/EntryCanopy",
                          p.fac.world(u, out / 2.0, p.base_z + 3.30),
                          p.fac.size(6.00, out, 0.24), M.stone))
        prims.append(K.cyl(stage, f"{prefix}/EntryPost",
                           p.fac.world(u + 2.6, out - 0.25,
                                       p.base_z + 3.30 / 2.0),
                           0.09, 3.30, M.metal))
    return prims


def build_unit_number(K, stage, prefix, p, M):
    """Large building-number marking — apartment gable wall / above the core.
    **1 prim.**
    Survey §5: a mandatory element for the background apartments in scenes 12,
    13 and 17. Size is `[knowledge]` (in the 1.5~2.5 m class).
    """
    w, t = 1.80, 0.05
    z = min(p.top_z - 1.2, p.levels[min(p.floors, 2)] + 1.2)
    u = p.fac.u0 + 1.8
    # **B-F1**: on a narrow slab (W ≈ 8 m) the plate's default u half-overlaps the
    # protruding core and 0.515 m of it ends up **inside** the core `[measured]`.
    # Snap it onto the core rather than leaving it straddling — mounting the 동
    # 번호 above the communal entrance is the canonical Korean position anyway,
    # and it is where the survey §5 photos put it.
    _, core_us = p.runs if isinstance(p.runs, tuple) else (None, [])
    for cu in core_us:
        if abs(cu - u) < (CORE_W + w) / 2.0:
            u = cu
            break
    wo = p.out_at(u - w / 2.0, u + w / 2.0, z - w / 2.0, z + w / 2.0)
    return [_box(K, stage, f"{prefix}/UnitNo",
                 p.fac.world(u, wo + fk.WALL_PROUD + t / 2.0, z),
                 p.fac.size(w, t, w), M.sign)]


# ===========================================================================
# [5] Per-type assembly
# ===========================================================================
def _fire(K, stage, prefix, p, M):
    """Firefighter access window triangle (statutory §18-2). Where pxr is
    unavailable (verification), a thin box substitutes — the **prim count is
    identical**, so budget verification still holds."""
    if not p.fire:
        return []
    r = fk.FIRE_TRI_D / 2.0

    def _out(u, zc):
        """**B-F1** — the triangle sits on whatever wall is at (u, z), not on the
        nominal facade plane. An apartment core protrudes `CORE_PROUD` = 0.60 m
        and the single 40 m station lands dead centre on it, which buried the
        decal **588 mm** deep `[measured]`."""
        return p.out_at(u - r, u + r, zc - r, zc + r) + fk.WALL_PROUD

    try:
        return fk.build_fire_access_marks(
            stage, prefix, p.fac, p.levels, M.decal,
            max_floors=max(1, int(p.rows or 1)), out_fn=_out)
    except ImportError:
        prims = []
        n_st = max(1, int(math.ceil(p.W / fk.FIRE_SPACING)))
        lv = p.levels[:-1][:max(1, int(p.rows or 1))]
        t = 0.004
        for s in range(n_st):
            u = p.fac.u0 + (s + 0.5) * (p.W / n_st)
            for f, zf in enumerate(lv):
                if not (2 <= f + 1 <= 11):
                    continue
                zc = zf + 0.80 + 0.60
                prims.append(_box(
                    K, stage, f"{prefix}/FireMark_{s}_{f + 1}",
                    p.fac.world(u, _out(u, zc) + t / 2.0, zc),
                    p.fac.size(fk.FIRE_TRI_D, t, fk.FIRE_TRI_D), M.decal))
        return prims


def _shopfront(K, stage, prefix, p, M):
    """Ground-floor shopfront for the two retail types. **2·bays + 3~5 prims.**

    **B-F2**: the bay count is `p.n_bays`, derived from the facade width by
    `shopfront_bays`. It used to be the tier constant 4/3/1 with a
    `bay_w = max(3.0, W/nb)` floor that could only ever make bays *wider*, so a
    28 m facade got three butted 8.93 m panels `[measured — survey R3 §5.2]`
    against a real Korean bay of 3.0–4.5 m.

    **B-F1**: `wall_out` hands `fk.build_shopfront` the outward face of the volume
    that actually covers the ground-floor band, so the glazing lands 5 mm proud of
    it instead of 100 mm inside it.
    """
    if not p.shopfront:
        return []
    nb = int(p.n_bays or 0)
    if nb <= 0:
        return []
    wo = p.out_at(p.fac.u0, p.fac.u1, p.base_z, p.base_z + p.ground_h)
    return fk.build_shopfront(
        K, stage, prefix, p.fac, M.glass, M.parapet, M.stone,
        ground_h=p.ground_h, bay_w=p.W / nb,
        steps=(1 if p.tier == "near" else 0),
        shutter_box=(p.tier == "near"), max_bays=nb, seed=p.seed,
        wall_out=wo)


def _attachments(K, stage, prefix, p, M):
    """Shared envelope attachments — AC units, downpipe/gas, fire triangle."""
    prims = []
    if p.ac_units:
        lv = p.levels
        if (p.ac_mode or "eaves") == "perfloor" and len(lv) > 2:
            # **Skip floor 1.** Two reasons —
            #  - Geometry: `fk.build_aircon_units` places a unit at floor level
            #    +0.35 and drops the refrigerant pipe (length 0.90) downward
            #    from its underside. On floor 1 the pipe bottom would be
            #    base_z + 0.35 - 0.45 - 0.45 = **base_z - 0.55**, punching
            #    through the ground (the cause of selfcheck [7] failing for
            #    villa at d=14; measured -0.550).
            #  - Reality: the ground floor of multi-family housing is either
            #    ancillary parking (piloti) or retail, so there are no units —
            #    the lowest floor with a household AC unit is floor 2
            #    `[knowledge]`. Hanging units under a parking piloti ceiling
            #    does happen, but that is the "eaves" mode's job and mixing it
            #    into the perfloor unit layout is wrong.
            lv = lv[1:]
        # In "eaves" mode, fk's `eaves_z` is an **absolute world z** (default
        # 2.30). Left alone, buildings with base_z != 0 — exactly what sloped
        # and drop scenes are — end up with AC units below their own ground
        # (measured: base_z=3.4 -> pipe bottom base_z-2.00). **Convert it to be
        # relative to base_z before passing it on.**
        #   Upper bound 2.30 = fk's default `[knowledge]`; lower bound 1.60 =
        #   the bottom of the 1.5~2.6 AC mounting-height band `[knowledge]`;
        #   `ground_h - 1.30` is the value that keeps the unit's top (+0.55)
        #   below the signage band's underside (= ground_h - 0.85)
        #   `[estimated]`.
        eaves_z = p.base_z + _clamp(p.ground_h - 1.30, 1.60, 2.30)
        prims += fk.build_aircon_units(
            K, stage, prefix, p.fac, M.metal, M.metal,
            levels=lv, mode=(p.ac_mode or "eaves"), eaves_z=eaves_z,
            per_level=2, count=p.ac_units, max_units=p.ac_units,
            bracket=(p.tier == "near"), pipe=(p.tier == "near"),
            seed=p.seed)
    if p.downpipe:
        prims += fk.build_downpipe_run(
            K, stage, prefix, p.fac, p.top_z, M.metal,
            n_pipes=int(p.downpipe), elbow=(p.tier == "near"),
            gas=bool(p.gas), gas_levels=p.levels, mtl_gas=M.metal,
            gas_variant="A", seed=p.seed)
    prims += _fire(K, stage, prefix, p, M)
    return prims


def _b_backdrop(K, stage, prefix, p, M):
    """Distant silhouette only. **3~4 prims.** No windows, no attachments, no
    plinth.

    Beyond d>80 m only heights above 12.9 m enter frame and the on-screen width
    is a few pixels, so nothing beyond the silhouette is conveyed (§1.3). Shell
    + parapet + penthouse suffices; only buildings of 12+ floors add one
    setback upper mass to break the skyline.
    """
    prims = []
    z_top = p.top_z
    if p.floors >= 12:
        z_mid = p.base_z + p.h * 0.72
        c, s = _span_center_size(p.x0, p.x1, p.y0, p.y1, p.base_z, z_mid)
        prims.append(_box(K, stage, f"{prefix}/Shell", c, s, M.shell, True))
        sx0, sx1, sy0, sy1 = _inner_range(p, min(2.0, p.depth * 0.2))
        c, s = _span_center_size(sx0, sx1, sy0, sy1, z_mid, z_top)
        prims.append(_box(K, stage, f"{prefix}/ShellTop", c, s, M.shell))
    else:
        c, s = _span_center_size(p.x0, p.x1, p.y0, p.y1, p.base_z, z_top)
        prims.append(_box(K, stage, f"{prefix}/Shell", c, s, M.shell, True))
    prims.append(_box(K, stage, f"{prefix}/Parapet",
                      (p.cx, p.cy, z_top + RAIL_H / 2.0),
                      (p.Lx + 0.20, p.Ly + 0.20, RAIL_H), M.parapet))
    rng = _rng(prefix, "bdrop", p.seed)
    # [W3 K-micro · S01-F1] The footprint moves to `backdrop_penthouse` so
    # `plan_building` can state an **exact** `p.ridge` from the same three lines,
    # and the height comes from `backdrop_ph_h` so the opt-in `roof_under_ceil`
    # clamp has somewhere to act. With the default (`roof_under_ceil=False`) this
    # is the pre-K-micro geometry expression for expression.
    ph_xy = backdrop_penthouse(p)
    if ph_xy is not None:
        pw, pdp = ph_xy
        ph_h = backdrop_ph_h(p)
        if ph_h >= PH_MIN_H:
            prims.append(_box(
                K, stage, f"{prefix}/Penthouse",
                (p.cx + (p.Lx * 0.5 - pw * 0.5 - 0.4) * rng.uniform(-0.8, 0.8),
                 p.cy + (p.Ly * 0.5 - pdp * 0.5 - 0.4) * rng.uniform(-0.8, 0.8),
                 z_top + ph_h / 2.0), (pw, pdp, ph_h), M.shell))
    return prims


def _b_low_shop(K, stage, prefix, p, M):
    """Single-storey neighbourhood retail. Flat roof, **signage covers most of
    the facade**."""
    prims = build_mass(K, stage, prefix, p, M)
    prims += fk.build_plinth(K, stage, prefix, p.x0, p.x1, p.y0, p.y1,
                             p.base_z, M.stone, height=1.10)
    prims += _shopfront(K, stage, prefix, p, M)
    if p.signs:
        # The signage band covers most of the facade — band_h uses the
        # statutory cap of 0.80 verbatim.
        prims += fk.build_signage(
            K, stage, prefix, p.fac, M.sign, M.sign,
            band_z=p.base_z + min(2.95, p.ground_h - 0.85), band_h=0.80,
            n_projecting=(1 if p.tier == "near" else 0), seed=p.seed)
    if p.awning:
        prims += build_awning(K, stage, prefix, p, M)
    prims += _attachments(K, stage, prefix, p, M)
    prims += build_rooftop(K, stage, prefix, p, M)
    return prims


def _b_shop_house(K, stage, prefix, p, M):
    """Shop house — full-glazing retail on floor 1 + housing on floors 2~4.
    **No podium setback** (the lot is narrow). The signage band and exposed
    stair are its signature."""
    prims = build_mass(K, stage, prefix, p, M)
    prims += fk.build_plinth(K, stage, prefix, p.x0, p.x1, p.y0, p.y1,
                             p.base_z, M.stone, height=1.10)
    prims += _shopfront(K, stage, prefix, p, M)
    if p.signs:
        prims += fk.build_signage(
            K, stage, prefix, p.fac, M.sign, M.sign,
            band_z=p.base_z + min(3.30, p.ground_h - 0.70),
            n_projecting=p.signs, seed=p.seed)
    if p.awning:
        prims += build_awning(K, stage, prefix, p, M)
    prims += build_window_bands(K, stage, prefix, p, M,
                                mode=("bay" if p.tier != "far" else "band"))
    if p.tier == "near":
        prims += build_ext_stair(K, stage, prefix, p, M)
    prims += _attachments(K, stage, prefix, p, M)
    prims += build_rooftop(K, stage, prefix, p, M)
    return prims


def _b_villa(K, stage, prefix, p, M):
    """Multi-family / villa — 4~5 floors, parking piloti, external stair,
    exposed (yellow) gas piping.
    The **single most common backdrop** from a Korean urban pedestrian
    viewpoint, yet the current library contains zero of them (survey §2)."""
    prims = build_mass(K, stage, prefix, p, M)
    if not p.piloti:
        prims += fk.build_plinth(K, stage, prefix, p.x0, p.x1, p.y0, p.y1,
                                 p.base_z, M.stone, height=1.10)
    prims += build_window_bands(K, stage, prefix, p, M,
                                mode=("bay" if p.tier != "far" else "band"))
    if p.tier == "near":
        prims += build_ext_stair(K, stage, prefix, p, M)
        prims += build_meter_box(K, stage, prefix, p, M)
    prims += _attachments(K, stage, prefix, p, M)
    prims += build_rooftop(K, stage, prefix, p, M)
    return prims


def _b_apt(K, stage, prefix, p, M):
    """Apartment — stacked balconies + **protruding core** + piloti ground
    floor + penthouse.
    No AC units are built (since the 2021 amendment to Enforcement Decree §119
    (1)3(d) they live inside the balcony — survey §3.4(a)). No window grid
    either: the living-room glazing sits behind the balcony and is not
    visible."""
    prims = build_mass(K, stage, prefix, p, M)
    prims += build_core(K, stage, prefix, p, M)
    if not p.piloti:
        prims += fk.build_plinth(K, stage, prefix, p.x0, p.x1, p.y0, p.y1,
                                 p.base_z, M.stone, height=1.10)
    if p.balcony:
        prims += build_balconies(K, stage, prefix, p, M)
    if p.tier in ("near", "mid"):
        prims += build_unit_number(K, stage, prefix, p, M)
    prims += _attachments(K, stage, prefix, p, M)
    prims += build_rooftop(K, stage, prefix, p, M)
    return prims


def _b_office(K, stage, prefix, p, M):
    """Business facility — curtain wall / window bands + **podium setback** +
    rooftop plant room.
    The lower floors get a granite plinth + a large canopy (the composition of
    scenes 06, 08, 11 and 14 in survey §5)."""
    prims = build_mass(K, stage, prefix, p, M)
    prims += fk.build_plinth(K, stage, prefix, p.x0, p.x1, p.y0, p.y1,
                             p.base_z, M.stone, height=1.60)
    if p.tier in ("near", "mid"):
        prims += build_entrance(K, stage, prefix, p, M,
                                canopy=(p.tier == "near"))
    prims += build_window_bands(
        K, stage, prefix, p, M,
        mode=("curtain" if p.tier in ("near", "mid") else "band"))
    prims += _attachments(K, stage, prefix, p, M)
    prims += build_rooftop(K, stage, prefix, p, M)
    return prims


_BUILDERS = {
    "backdrop": _b_backdrop, "low_shop": _b_low_shop,
    "shop_house": _b_shop_house, "villa": _b_villa,
    "apt": _b_apt, "office": _b_office,
}

# Type x LOD prim cap (per building, geometry prims). selfcheck compares it
# against the measured values.
#
# **This table's evidence grade is `[estimated]`.** Survey §6's LOD table gives
# only *qualitative* per-distance rules (how far to build windows, lower floors
# and attachments) and no per-type prim-cap numbers. These figures are
# therefore not external evidence but a **regression freeze line** — their only
# job is to catch "if it grows past here, somebody grew it quietly".
#
# v1 re-baseline rule (2026-07-29) — every cell was refilled by **one rule**:
#   cap = **measured + 3** for the representative bd (W=24, depth=12, the
#         standard floor count per type)
#   +3 = the worst case where all three probabilistic attachments (water tank,
#        antenna, roof sign) switch on at once. 1 prim each `[measured]`.
#        Shape and seed variation fit inside this slack.
#   The `backdrop` row and the `silhouette` column instead keep the **builder's
#   structural maximum of 4** (the most `_b_backdrop` can emit = shell 1~2 +
#   parapet 1 + penthouse 1). That comes from code structure rather than a
#   measurement, so it needs no headroom.
#
# The former table had aged behind the code and was off by 4~8 prims per cell
# (the module docstring's parenthesised "representative measured values" had
# gone stale alongside it). The re-baseline moved **more cells down than up** —
# apt/mid 34->23, office/mid 22->15 — so the table did not get looser.
#
# **v2 re-baseline 2026-07-31 (W3 CB-4 / B-F2).** Four cells move, all of them
# the retail types, all of them for one reason: the shopfront bay count is now
# derived from the facade width instead of a per-tier constant, and a bay costs
# 2 prims. At the reference `BUDGET_REF_W = 24 m` the count goes 4->7 (near) and
# 3->7 (mid) for `shop_house`, 3->7 and 2->7 for `low_shop`. Same rule as v1
# (cap = measured + 3 at W=24); the width-dependent part lives in
# `prim_budget(kind, tier, W)`, not in the table. Every other cell is byte-equal
# to v1 — B-F1 moves glazing, it does not create any.
BUDGET = {
    "shop_house": {"near": 65, "mid": 38, "far": 9, "silhouette": 4},
    "apt":        {"near": 57, "mid": 23, "far": 15, "silhouette": 4},
    "office":     {"near": 31, "mid": 15, "far": 11, "silhouette": 4},
    "villa":      {"near": 57, "mid": 28, "far": 10, "silhouette": 4},
    "low_shop":   {"near": 44, "mid": 27, "far": 7, "silhouette": 4},
    "backdrop":   {"near": 4, "mid": 4, "far": 4, "silhouette": 4},
}

# The measured values the table above was built from (the baseline when
# recomputing under the same rule). selfcheck [5] re-measures these every run
# and compares against the table, so update this whenever the code changes.
BUDGET_MEASURED = {
    "shop_house": {"near": 62, "mid": 35, "far": 6, "silhouette": 3},
    "apt":        {"near": 54, "mid": 20, "far": 12, "silhouette": 4},
    "office":     {"near": 28, "mid": 12, "far": 8, "silhouette": 3},
    "villa":      {"near": 54, "mid": 25, "far": 7, "silhouette": 3},
    "low_shop":   {"near": 41, "mid": 24, "far": 4, "silhouette": 3},
    "backdrop":   {"near": 3, "mid": 3, "far": 3, "silhouette": 3},
}


BUDGET_REF_W = 24.0    # the representative facade width every cell was measured at


def prim_budget(kind, tier, W=None):
    """**Per-building prim cap** for a type, LOD tier and facade width. 0 prims.

    **B-F2 added the `W` term.** Before it, the table had no width term at all
    (`fix_building_kit_v1.md` §7-1 already listed that as a known limitation),
    which was tolerable only because the bay count was a constant. Now the
    shopfront costs `2` prims per bay and the bay count follows `W`, so the cap
    has to follow it too or a wide facade fails a budget it never had a chance of
    meeting.

    The term is deliberately narrow — `2 × (bays(W) − bays(24 m))`, i.e. exactly
    the shopfront's own per-bay cost against the width every cell was measured at.
    Nothing else in the builder grows monotonically with `W`: `build_window_bands`
    bay mode is capped at 4 columns and is already at that cap at 24 m, and the
    balcony run count is bounded by `_unit_runs`.

    `W=None` reproduces the old two-argument behaviour exactly, so existing
    callers are unaffected.
    """
    base = BUDGET.get(kind, BUDGET["backdrop"]).get(tier, 4)
    if W is None or kind not in ("shop_house", "low_shop"):
        return base
    return base + 2 * max(0, shopfront_bays(W, tier)
                          - shopfront_bays(BUDGET_REF_W, tier))


# ===========================================================================
# [6] Top-level API
# ===========================================================================
def build_korean_building(kit, stage, prefix, bd, mtls, dist=None, kind=None,
                          seed=None, plan=None, eyes=None, **over):
    """One Korean building. **The replacement for the current
    `build_building`.**

    Arguments
      kit    `facade_kit.Kit(add_box, add_cylinder, oriented_box)` — primitive
             injection.
      stage  USD stage.
      prefix prim path prefix.
      bd     the existing dictionary. **Required keys are unchanged**
             (x0,x1,y0,y1,h,floors,axis,facade_x/y,face_dir,base_z). Optional
             keys: `kind`, `lod_dist`, and any field of `Plan.__slots__`
             (`piloti`, `rows`, `signs`, ...).
      mtls   `Mtls`, dict, tuple or a single material — `Mtls.coerce` absorbs
             them all. The current 3-argument call is
             `Mtls.from_legacy(shell, glass, parapet)`.
      dist   distance to the judging camera [m]. If None, `bd["lod_dist"]` then
             `|facade plane|`.
      kind   force the type. If None, `bd["kind"]` then `infer_kind()`.
      plan   reuse a pre-built `Plan` (for verification and layout
             optimization).
      eyes   the judged camera positions, e.g. `judged_eyes(gy)`. Supplying them
             switches on **B-F3** (`dist` from the real eye-to-facade geometry
             instead of `|facade plane|`) and **BS-4** (a facade outside ±30° of
             every judged eye is demoted to `kind="backdrop"`). Ignored when
             `plan` is given — build the Plan with `eyes` instead.

    Returns: the list of prims created.

    Demotion with distance happens **at the type level**:
      d>80 m -> `backdrop` regardless of type (3~4 prims, 0 windows).
      40<d<=80 -> windows become one horizontal band per floor, no
                  attachments, lower floors get the plinth only.
      20<d<=40 -> lower-floor detail + AC units and downpipes, repeating
                  elements up to 5 floors.
      d<=20 -> everything.
    """
    K = kit
    M = Mtls.coerce(mtls)
    p = plan if plan is not None else plan_building(
        bd, dist=dist, kind=kind, seed=seed, eyes=eyes, **over)
    return _BUILDERS[p.kind](K, stage, prefix, p, M)


# ===========================================================================
# [7] Self-check — `python3 building_kit.py`
# ===========================================================================
class _MockKit(fk.Kit):
    """A Kit that creates no prims and only **counts** them. For budget and
    coordinate verification only.

    Record layout: `(shape, path, center, size, collider, mtl)`. `mtl` was added
    for check **[11]**, which has to know a prim's **material role** — it is a
    role check, not a path-name heuristic, so it cannot be fooled by a rename and
    it automatically covers roles that arrive later. Indices 0–4 are unchanged, so
    every older check still reads `c[2]` / `c[3]` as before.
    """

    def __init__(self, oriented=False):
        self.calls = []
        self.add_box = self._box
        self.add_cylinder = self._cyl
        self.oriented_box = self._obox if oriented else None

    def _box(self, stage, path, center, size, mtl=None, collider=False):
        rec = ("box", path, tuple(float(v) for v in center),
               tuple(float(v) for v in size), collider, mtl)
        self.calls.append(rec)
        return rec

    def _cyl(self, stage, path, center, radius, height, mtl=None, **kw):
        rec = ("cyl", path, tuple(float(v) for v in center),
               (2 * float(radius), 2 * float(radius), float(height)), False, mtl)
        self.calls.append(rec)
        return rec

    def _obox(self, stage, path, center, size, mtl=None, collider=False,
              rotz=0.0, rotx=0.0):
        rec = ("obox", path, tuple(float(v) for v in center),
               tuple(float(v) for v in size), collider, mtl)
        self.calls.append(rec)
        return rec

    def box(self, stage, path, center, size, mtl=None, collider=False):
        return self._box(stage, path, center, size, mtl, collider)

    def cyl(self, stage, path, center, radius, height, mtl=None, **kw):
        return self._cyl(stage, path, center, radius, height, mtl, **kw)


def _demo_bd(kind, dist, floors=None, W=24.0, depth=12.0, base_z=0.0):
    """Representative bd per type. Floor counts come from each type's real
    distribution."""
    nf = floors if floors is not None else {
        "shop_house": 4, "apt": 14, "office": 9, "villa": 5,
        "low_shop": 1, "backdrop": 10}[kind]
    hh = {"shop_house": 3.3, "apt": 3.0, "office": 3.6, "villa": 2.9,
          "low_shop": 4.2, "backdrop": 4.0}[kind] * nf
    return dict(x0=-W / 2.0, x1=W / 2.0, y0=dist, y1=dist + depth,
                h=hh, floors=nf, axis="y", facade_y=dist, face_dir=-1.0,
                base_z=base_z, kind=kind)


def _run(kind, dist, **kw):
    K = _MockKit(oriented=True)
    bd = _demo_bd(kind, dist, **kw)
    p = plan_building(bd, dist=dist)
    prims = build_korean_building(K, None, "/W/B", bd, Mtls("sh", "gl", "pa"),
                                  dist=dist, plan=p)
    return p, K, prims


# ---------------------------------------------------------------------------
# [7a] B-F1 — the outward-visibility instrument
# ---------------------------------------------------------------------------
# Every role gets its **own** sentinel so check [11] reads the real material
# role. `Mtls("sh","gl","pa")` (what `_run` uses, mirroring the legacy 3-argument
# call) collapses stone/metal/sign/decal onto `parapet` through the fallback
# chain, which would make a role check meaningless.
_ROLE_NAMES = ("shell", "glass", "parapet", "stone", "metal", "sign",
               "decal", "dark")
_ROLE_MTLS = Mtls(*_ROLE_NAMES)
# Roles that must be **visible from outside**: glazing, signage panels and
# decals only exist to be seen. `parapet`/`stone`/`metal` are legitimately
# allowed to be flush or recessed (a kick plate, a plinth, a bracket).
VISIBLE_ROLES = ("glass", "sign", "decal")
# Roles that form a **solid volume** a facade attachment can be buried in.
# `dark` is the piloti rear wall; `stone` is not here because `PilotiCol` is a
# 0.45 m column and the plinth is a 25 mm band, neither of which is a mass.
MASS_ROLES = ("shell", "dark")


def _out_face(p, rec):
    """Outward distance of a recorded prim's outermost face from `p.plane`, in
    `Facade` `out` units. 0 prims."""
    n = 1 if p.axis_y else 0
    return p.fdir * (rec[2][n] - p.plane) + rec[3][n] / 2.0


def _span(rec, ax):
    return (rec[2][ax] - rec[3][ax] / 2.0, rec[2][ax] + rec[3][ax] / 2.0)


def _overlaps(a, b):
    return min(a[1], b[1]) - max(a[0], b[0]) > 1e-9


def visibility_violations(p, calls):
    """**The B-F1 gate.** Every `glass`/`sign`/`decal` prim must have
    `out_max > 0` against **every mass box that overlaps it**. 0 prims.

    Returns `[(prim_path, mass_path, margin_m), ...]`; empty means green.

    Why this check and not the ones that already existed: `[5]` counts prims
    against a budget, `[7]` checks `z >= base_z - 0.05`, `[8]` checks path
    uniqueness. **None of them asks whether a facade prim is on the outside of
    the wall**, so `building_kit` shipped 135/135 green while burying 62 of 62
    glazing prims `[measured — survey R3 §5.1]`. That is the defect that stopped
    adoption, so it gets its own instrument.

    `out_max` is measured **against the mass box's own outer face**, not against
    the nominal facade plane: a positive `out` is not enough when the volume in
    front of you is a protruding core (`CORE_PROUD` 0.60) — the pre-fix
    `CoreStrip` sat at `out = +0.55` and was still 30 mm inside its own core.
    Overlap is tested on **both** the tangent and the z axis, because a prim that
    clears the mass horizontally is not buried by it.
    """
    tan_ax = 0 if p.axis_y else 1
    mass = [c for c in calls if c[5] in MASS_ROLES]
    bad = []
    for c in calls:
        if c[5] not in VISIBLE_ROLES:
            continue
        for m in mass:
            if _overlaps(_span(c, tan_ax), _span(m, tan_ax)) \
                    and _overlaps(_span(c, 2), _span(m, 2)):
                margin = _out_face(p, c) - _out_face(p, m)
                if margin <= 0.0:
                    bad.append((c[1], m[1], margin))
    return bad


def _run_roles(kind, dist, **kw):
    """`_run` with one sentinel material per role, for checks [11] and [11a]."""
    K = _MockKit(oriented=True)
    bd = _demo_bd(kind, dist, **kw)
    p = plan_building(bd, dist=dist)
    build_korean_building(K, None, "/W/B", bd, _ROLE_MTLS, dist=dist, plan=p)
    return p, K


def selfcheck(verbose=True):
    """Verify prim counts, coordinates and determinism. Uses no renderer or
    GPU. Raises AssertionError on failure."""
    ok = []

    def chk(name, cond, extra=""):
        ok.append(bool(cond))
        if verbose:
            print(f"  [{'OK ' if cond else 'FAIL'}] {name}{(' — ' + extra) if extra else ''}")
        return bool(cond)

    print("=" * 74)
    print("building_kit 자기검사")
    print("=" * 74)

    # --- 1. Deterministic RNG ----------------------------------------------
    print("\n[1] 결정적 RNG (hash() 미사용)")
    a = [_rng("x", 1).random() for _ in range(3)]
    b = [_rng("x", 1).random() for _ in range(3)]
    chk("_rng 재현성", a == b)
    chk("_rng 키 분리", _rng("x", 1).random() != _rng("x", 2).random())
    # A substring search self-matched the checking code's own literal and
    # failed forever. -> Exhaustive double pass instead: AST (name loads) plus
    # tokenize (call form after stripping strings and comments).
    h_ast, h_tok, h_shadow = _builtin_hash_uses(path=__file__)
    chk("소스에 내장 hash 호출·별칭 없음 (AST+토큰 전수)",
        not h_ast and not h_tok,
        f"AST 이름로드 {len(h_ast)}건 · 토큰 {len(h_tok)}건 · 재정의 {len(h_shadow)}건"
        + (f" {(h_ast + h_tok)[:4]}" if (h_ast or h_tok) else ""))
    r = random.Random(0)
    chk("_jit ±8 % 하드캡", all(
        0.92 - 1e-9 <= _jit(r, 1.0, 0.5) <= 1.08 + 1e-9 for _ in range(500)))

    # --- 2. Frame ceiling (must match facade_kit) --------------------------
    print("\n[2] 판정 프레임 상한 z = 0.3 + 0.14·d")
    for d, want in ((10, 1.71), (20, 3.11), (34, 5.08), (90, 12.94)):
        got = fk.frame_ceiling(d)
        chk(f"d={d} m → {got:.2f} m", abs(got - want) < 0.02)

    # --- 3. Floor levels: total height preserved + only floor 1 differs -----
    print("\n[3] plan_levels — 총 높이 불변 + 1층 비균등")
    for kind in KINDS:
        for (H, n) in ((10.0, 4), (45.0, 15), (4.2, 1), (22.0, 7)):
            lv, gh, fh = plan_levels(kind, H, n, base_z=3.0)
            if not chk(f"{kind} H={H} n={n} 상단 일치",
                       abs(lv[-1] - (3.0 + H)) < 1e-9,
                       f"lv[-1]={lv[-1]:.6f}"):
                break
    lv, gh, fh = plan_levels("shop_house", 20.0, 5)
    chk("shop_house 1층 층고 > 기준층", gh > fh, f"{gh:.2f} vs {fh:.2f}")
    lv, gh, fh = plan_levels("backdrop", 20.0, 5)
    chk("backdrop 은 등간격(법정 4 m/층 비율)", abs(gh - fh) < 1e-9)

    # --- 4. Type inference --------------------------------------------------
    print("\n[4] infer_kind")
    cases = [
        (dict(x0=0, x1=12, y0=0, y1=5.5, h=4.2, floors=1), 13.5, "low_shop"),
        (dict(x0=0, x1=24, y0=0, y1=6, h=12.0, floors=4), 26.0, "shop_house"),
        (dict(x0=0, x1=10, y0=0, y1=8, h=11.0, floors=4), 16.0, "villa"),
        (dict(x0=0, x1=10, y0=0, y1=18, h=26.0, floors=8), 24.0, "office"),
        (dict(x0=0, x1=12, y0=0, y1=22.4, h=45.0, floors=15), 34.0, "apt"),
        (dict(x0=0, x1=12, y0=0, y1=30, h=38.0, floors=10), 54.0, "office"),
        (dict(x0=0, x1=20, y0=0, y1=8, h=44.0, floors=15), 84.0, "backdrop"),
    ]
    for bd, d, want in cases:
        got = infer_kind(bd, d)
        chk(f"floors={bd['floors']} d={d} → {got}", got == want, f"기대 {want}")

    # --- 5. Prim budget -----------------------------------------------------
    print("\n[5] 유형 × LOD 프림 예산 (동당, 파사드 24 m)")
    dists = {"near": 14.0, "mid": 30.0, "far": 55.0, "silhouette": 95.0}
    print(f"    {'kind':12s} {'near':>12s} {'mid':>12s} {'far':>12s} {'sil':>12s}")
    table = {}
    for kind in KINDS:
        row = []
        for tier, d in dists.items():
            p, K, prims = _run(kind, d)
            n = len(K.calls)
            eff = p.kind
            cap = prim_budget(eff, p.tier)
            row.append((n, cap, eff))
            table[(kind, tier)] = n
        print(f"    {kind:12s} " + " ".join(
            f"{n:4d}/{cap:<3d}({e[:3]})" for n, cap, e in row))
    # Only reports drift against the baseline the table was built from
    # (BUDGET_MEASURED); this is not a check.
    drift = [(k, t, table[(k, t)], BUDGET_MEASURED[k][t])
             for k in KINDS for t in dists
             if table[(k, t)] != BUDGET_MEASURED[k].get(t)]
    print("    기준선 드리프트: " + ("없음" if not drift else
                                     f"{len(drift)}칸 {drift[:4]} → BUDGET 재기준선 필요"))
    bad = []
    for kind in KINDS:
        for tier, d in dists.items():
            p, K, _ = _run(kind, d)
            if len(K.calls) > prim_budget(p.kind, p.tier):
                bad.append((kind, tier, len(K.calls),
                            prim_budget(p.kind, p.tier)))
    chk("전 유형·전 티어가 예산 이내", not bad, str(bad))
    chk("backdrop 프림 3~5", 3 <= table[("backdrop", "far")] <= 5)
    chk("d>80 은 유형 무관 강등",
        all(_run(k, 95.0)[0].kind == "backdrop" for k in KINDS))

    # --- 6. Scale-anchor coordinates ----------------------------------------
    print("\n[6] 스케일 앵커 (랜덤화 금지 대상)")
    _, K, _ = _run("shop_house", 14.0)
    doors = [c for c in K.calls if "Door" in c[1] and "Head" not in c[1]]
    chk("상가 출입문 높이 = 2.10", doors and
        all(abs(max(c[3]) - DOOR_H) < 1e-6 or abs(c[3][2] - DOOR_H) < 1e-6
            for c in doors), str([c[3] for c in doors]))
    _, KA, _ = _run("apt", 30.0)
    rails = [c for c in KA.calls if "BalconyRail" in c[1]]
    chk("발코니 난간 높이 = 1.20", rails and
        all(abs(c[3][2] - RAIL_H) < 1e-6 for c in rails),
        f"{len(rails)}개")
    _, KV, _ = _run("villa", 14.0)
    acs = [c for c in KV.calls if "/AcUnit_" in c[1]]

    def _within(v, ref):
        return abs(v - ref) <= ref * 0.08 + 1e-9
    chk("실외기 0.80×0.55×0.30 ±8 % 이내", acs and all(
        _within(c[3][0], fk.AC_W) and _within(c[3][2], fk.AC_H)
        and _within(c[3][1], fk.AC_D) for c in acs), f"{len(acs)}대")
    cols = [c for c in KV.calls if "PilotiCol" in c[1]]
    chk("필로티 기둥 유효높이 ≥ 2.10(법정)", cols and
        all(c[3][2] >= PILOTI_CLEAR - 1e-9 for c in cols),
        f"{len(cols)}본 h={cols[0][3][2]:.2f}" if cols else "없음")

    # --- 7. Geometric consistency -------------------------------------------
    print("\n[7] 기하 정합")
    for kind in KINDS:
        for d in (14.0, 30.0, 55.0, 95.0):
            p, K, _ = _run(kind, d)
            shells = [c for c in K.calls if c[1].endswith(("/Shell",
                                                           "/ShellStep",
                                                           "/ShellTop"))]
            top = max(c[2][2] + c[3][2] / 2.0 for c in shells)
            if not chk(f"{kind} d={d:.0f} 셸 상단 = base+h",
                       abs(top - p.top_z) < 1e-6, f"{top:.3f} vs {p.top_z:.3f}"):
                break
            # Looks at **every prim** (the former version excluded "Step"
            # paths). The measured minimum is a single `ShopStep` (a 1 cm
            # embedment from the 0.02 tread-thickness slack) and everything
            # else sits exactly at base_z -> the tolerance tightens from -0.35
            # to **-0.05**. The old -0.35 was excessive slack that would miss
            # a -0.30 penetration.
            bot = min(c[2][2] - c[3][2] / 2.0 for c in K.calls)
            if not chk(f"{kind} d={d:.0f} 지반 아래 프림 없음",
                       bot >= p.base_z - 0.05, f"최저 {bot:.3f}"):
                break
    # Penthouse statutory cap (1/8 of the building area)
    for kind in KINDS:
        p, K, _ = _run(kind, 30.0)
        ph = [c for c in K.calls if c[1].endswith("/Penthouse")]
        if ph:
            area = ph[0][3][0] * ph[0][3][1]
            chk(f"{kind} 옥탑 수평투영 ≤ 건축면적/8",
                area <= p.Lx * p.Ly * PH_AREA_FRAC + 1e-6,
                f"{area:.1f} ≤ {p.Lx * p.Ly / 8:.1f} m²")
    # Parapet 1.2 (statutory)
    for kind in KINDS:
        _, K, _ = _run(kind, 30.0)
        par = [c for c in K.calls if c[1].endswith("/Parapet")]
        chk(f"{kind} 파라펫 1.20(법정 §40)",
            par and abs(par[0][3][2] - RAIL_H) < 1e-9)

    # --- 8. Path collisions -------------------------------------------------
    print("\n[8] 프림 경로 유일성")
    for kind in KINDS:
        for d in (14.0, 30.0, 55.0, 95.0):
            _, K, _ = _run(kind, d)
            paths = [c[1] for c in K.calls]
            if not chk(f"{kind} d={d:.0f} 경로 중복 없음",
                       len(paths) == len(set(paths)),
                       str([q for q in paths if paths.count(q) > 1][:3])):
                break

    # --- 9. bd compatibility (no new keys) ----------------------------------
    print("\n[9] 기존 bd 키만으로 동작")
    legacy = dict(x0=34.0, x1=46.0, y0=-15.0, y1=7.4, h=45.0, floors=15,
                  axis="x", facade_x=34.0, face_dir=-1.0, base_z=0.0)
    K = _MockKit()
    prims = build_korean_building(K, None, "/W/B", legacy,
                                  Mtls.from_legacy("sh", "gl", "pa"))
    p = plan_building(legacy)
    chk("scene13 A101 (kind 키 없음) 동작",
        len(prims) > 0 and p.kind in KINDS,
        f"kind={p.kind} tier={p.tier} 프림={len(prims)}")
    minimal = dict(x0=0, x1=20, y0=10, y1=18, h=12.0, floors=4)
    K2 = _MockKit()
    prims2 = build_korean_building(K2, None, "/W/B2", minimal, "single_mtl")
    chk("facade_*·face_dir·base_z 결측도 동작", len(prims2) > 0,
        f"프림={len(prims2)}")

    # --- 10. Determinism (two runs are identical) ---------------------------
    print("\n[10] 빌드 결정성")
    same = True
    for kind in KINDS:
        _, K1, _ = _run(kind, 30.0)
        _, K2, _ = _run(kind, 30.0)
        same = same and (K1.calls == K2.calls)
    chk("동일 입력 → 동일 프림·좌표", same)

    # --- 11a. mass_faces == what build_mass/build_core actually emit ---------
    # `out_at` is only as good as `mass_faces`, and `mass_faces` is a *second*
    # expression of `build_mass`'s conditionals. A silent divergence would make
    # check [11] green while the geometry stayed buried, so it is cross-validated
    # prim-for-prim before [11] is allowed to mean anything.
    print("\n[11a] mass_faces ↔ 실제 매스 프림 교차검증")
    MASS_PATHS = ("/Shell", "/ShellStep", "/ShellTop", "/Podium",
                  "/PilotiRear")
    for kind in KINDS:
        for d in (14.0, 30.0, 55.0, 95.0):
            p, K = _run_roles(kind, d)
            built = [c for c in K.calls
                     if c[1].endswith(MASS_PATHS) or "/Core_" in c[1]]
            tan_ax = 0 if p.axis_y else 1
            got = sorted((round(_span(c, tan_ax)[0], 6),
                          round(_span(c, tan_ax)[1], 6),
                          round(_span(c, 2)[0], 6), round(_span(c, 2)[1], 6),
                          round(_out_face(p, c), 6)) for c in built)
            want = sorted((round(a, 6), round(b, 6), round(z0, 6),
                           round(z1, 6), round(f, 6))
                          for (a, b, z0, z1, f) in mass_faces(p))
            if not chk(f"{kind} d={d:.0f} 매스 {len(want)}개 일치",
                       got == want,
                       f"모델 {want}\n            실측 {got}" if got != want
                       else f"{len(got)}개"):
                break
    # Every mass prim must carry a mass role, or [11] would silently skip it.
    role_ok = True
    for kind in KINDS:
        _, K = _run_roles(kind, 14.0)
        for c in K.calls:
            if (c[1].endswith(MASS_PATHS) or "/Core_" in c[1]) \
                    and c[5] not in MASS_ROLES:
                role_ok = False
    chk("매스 프림은 모두 shell/dark 역할", role_ok)

    # --- 11. B-F1 outward visibility (out_max > 0) --------------------------
    print("\n[11] B-F1 외부 가시성 — glass/sign/decal 의 out_max > 0")
    tot_bad, tot_vis = 0, 0
    for kind in KINDS:
        for tier, d in (("near", 14.0), ("mid", 30.0), ("far", 55.0),
                        ("sil", 95.0)):
            p, K = _run_roles(kind, d)
            vis = [c for c in K.calls if c[5] in VISIBLE_ROLES]
            bad = visibility_violations(p, K.calls)
            tot_vis += len(vis)
            tot_bad += len(bad)
            if bad:
                chk(f"{kind}/{tier} 매몰 0", False,
                    f"{len(bad)}건 {[(a.split('/')[-1], b.split('/')[-1], round(m, 3)) for a, b, m in bad[:3]]}")
    chk(f"전 유형·전 티어 glass/sign/decal {tot_vis}개 전부 외부 노출",
        tot_bad == 0, f"매몰 {tot_bad}건")
    # Widths and base offsets the demo bd does not reach — the office podium,
    # the villa daylight step and the apt core are the three burial mechanisms.
    edge = 0
    for kind in KINDS:
        for d in (14.0, 30.0, 55.0):
            for W in (8.0, 12.0, 28.0, 40.0):
                for bz in (0.0, 3.4, -2.15):
                    p, K = _run_roles(kind, d, W=W, base_z=bz)
                    edge += len(visibility_violations(p, K.calls))
    chk("폭 8~40 m × base_z −2.15/0/3.4 전수에서도 매몰 0", edge == 0,
        f"매몰 {edge}건")

    # --- 12. B-F2 shopfront bay band ---------------------------------------
    print("\n[12] B-F2 상가 베이 폭 (한국 3.0~4.5 m)")
    off = []
    for W in (8.0, 12.0, 18.0, 24.0, 28.0, 34.0):
        for tier in ("near", "mid"):
            bw = bay_width(W, tier)
            if not (SHOP_BAY_MIN - 1e-9 <= bw <= SHOP_BAY_MAX + 1e-9):
                off.append((W, tier, round(bw, 2)))
    chk("W 8~34 m · near/mid 전부 3.0~4.5 m 대역", not off, str(off))
    chk("W=28 (scene20 C) 베이 = 3.50 m — 종전 8.93 m",
        abs(bay_width(28.0, "mid") - 3.50) < 1e-9,
        f"{bay_width(28.0, 'mid'):.2f} m")
    chk("far/silhouette 은 상가 미시공(베이 0)",
        shopfront_bays(24.0, "far") == 0
        and shopfront_bays(24.0, "silhouette") == 0)
    # The budget must follow W, or the row breaks its own gate.
    wb = []
    for kind in ("shop_house", "low_shop"):
        for tier, d in (("near", 14.0), ("mid", 30.0)):
            for W in (8.0, 12.0, 18.0, 24.0, 28.0, 34.0):
                p, K = _run_roles(kind, d, W=W)
                cap = prim_budget(p.kind, p.tier, p.W)
                if len(K.calls) > cap:
                    wb.append((kind, tier, W, len(K.calls), cap))
    chk("폭 가변 상가가 prim_budget(kind, tier, W) 이내", not wb, str(wb))
    chk("prim_budget 2인자 호출은 종전과 동일",
        prim_budget("shop_house", "near") == BUDGET["shop_house"]["near"]
        and prim_budget("shop_house", "near", BUDGET_REF_W)
        == BUDGET["shop_house"]["near"])

    # --- 13. B-F3 / BS-4 judged-eye geometry -------------------------------
    print("\n[13] B-F3 판정 시선 거리 · BS-4 프레임 판정")
    eyes = judged_eyes(0.0)
    chk("judged_eyes = grid_views 격자 9안 (−d, gy, h)",
        len(eyes) == 9 and (-10.0, 0.0, 0.3) in eyes
        and (-2.0, 0.0, 1.8) in eyes, str(eyes[:2]))
    # Head-on facade at x = 30 (the scene20-C form). The default `|plane|` = 30
    # ignores the nearest eye's own standoff (x = −2), so d_true must be 32.
    ahead = dict(x0=30.0, x1=36.0, y0=-6.0, y1=6.0, h=12.0, floors=4,
                 axis="x", facade_x=30.0, face_dir=-1.0)
    p0 = plan_building(ahead)
    pe = plan_building(ahead, eyes=eyes)
    chk("기본 dist = |파사드 평면| (종전 동작 보존)",
        abs(p0.dist - 30.0) < 1e-9 and p0.d_true is None, f"{p0.dist:.2f}")
    chk("d_true = 최근접 판정 시선 → 파사드 최근접점 (30 → 32)",
        abs(pe.d_true - 32.0) < 1e-9, f"{pe.d_true:.3f} m")
    # Laterally offset facade: the default ignores the offset entirely.
    side = dict(ahead, y0=20.0, y1=32.0)
    ps = plan_building(side, eyes=eyes)
    chk("횡방향 이격 파사드도 반영 (기본 30 → 실제 √(32²+20²))",
        abs(ps.d_true - math.hypot(32.0, 20.0)) < 1e-9
        and abs(plan_building(side).dist - 30.0) < 1e-9,
        f"{ps.d_true:.2f} m")
    chk("z_ceil = fk.frame_ceiling(d_true)",
        abs(pe.z_ceil - fk.frame_ceiling(pe.d_true)) < 1e-12,
        f"{pe.z_ceil:.2f} m")
    chk("lod_dist 가 있으면 그것이 우선 (씬 오버라이드)",
        abs(plan_building(dict(ahead, lod_dist=55.0),
                          eyes=eyes).dist - 55.0) < 1e-9)
    # BS-4: the same building swung sideways past +-30 deg from every eye.
    aside = dict(ahead, y0=60.0, y1=72.0)
    pout = plan_building(aside, eyes=eyes)
    chk("정면 파사드는 프레임 안", pe.in_frame is True)
    chk("±30° 밖 파사드는 프레임 밖 → kind=backdrop",
        pout.in_frame is False and pout.kind == "backdrop",
        f"in_frame={pout.in_frame} kind={pout.kind} d_true={pout.d_true:.1f}")
    K = _MockKit(oriented=True)
    build_korean_building(K, None, "/W/B", aside, _ROLE_MTLS, eyes=eyes)
    chk("BS-4 강등 = 3~4 프림 (음의 프림 비용)", 3 <= len(K.calls) <= 4,
        f"{len(K.calls)}프림")
    chk("backdrop_demote=False 는 A/B 대조군을 남긴다",
        plan_building(aside, eyes=eyes,
                      backdrop_demote=False).kind != "backdrop",
        plan_building(aside, eyes=eyes, backdrop_demote=False).kind)
    # A wall behind the eye is never in frame, however wide.
    behind = dict(x0=-60.0, x1=-40.0, y0=-6.0, y1=6.0, h=12.0, floors=4,
                  axis="x", facade_x=-40.0, face_dir=1.0)
    chk("카메라 뒤쪽 파사드는 프레임 밖",
        plan_building(behind, eyes=eyes).in_frame is False)
    # Straddling the axis counts even when both ends are outside +-30 deg.
    wide = dict(ahead, y0=-80.0, y1=80.0)
    chk("시선축을 가로지르는 긴 벽은 프레임 안 (양 끝은 밖)",
        plan_building(wide, eyes=eyes).in_frame is True)
    # eyes=None must change nothing at all — this is what makes CB-4 unwired.
    same = True
    for kind in KINDS:
        for d in (14.0, 30.0, 55.0, 95.0):
            b = _demo_bd(kind, d)
            K1 = _MockKit(oriented=True)
            K2 = _MockKit(oriented=True)
            build_korean_building(K1, None, "/W/B", b, _ROLE_MTLS, dist=d)
            build_korean_building(K2, None, "/W/B", b, _ROLE_MTLS, dist=d,
                                  eyes=None)
            same = same and K1.calls == K2.calls
    chk("eyes=None → 좌표 완전 동일 (씬 미배선 보증)", same)

    # --- 14. S01-F1 — the ridge the builders really emit --------------------
    print("\n[14] S01-F1 지붕 부속 상한 — p.ridge vs 실제 최상단 프림")
    over_b, exact_b, worst = [], [], 0.0
    for kind in KINDS:
        for d in (14.0, 30.0, 55.0, 95.0):
            for W in (8.0, 24.0, 40.0):
                for nf in (1, 4, 8, 15):
                    for bz in (0.0, 3.4, -2.15):
                        p, K, _pr = _run(kind, d, W=W, floors=nf, base_z=bz)
                        top = max(c[2][2] + c[3][2] / 2.0 for c in K.calls)
                        if top > p.ridge + 1e-9:
                            over_b.append((p.kind, p.tier, W, nf, round(top, 3),
                                           round(p.ridge, 3)))
                        worst = max(worst, p.ridge - top)
                        if p.kind == "backdrop" and abs(top - p.ridge) > 1e-9:
                            exact_b.append((p.tier, W, nf, round(top, 3),
                                            round(p.ridge, 3)))
    chk("전 kind×tier×W×층×base_z 에서 실제 최상단 ≤ p.ridge", not over_b,
        str(over_b[:4]) if over_b else f"여유 최대 {worst:.3f} m")
    chk("kind=backdrop 은 p.ridge 가 **정확값** (실측 최상단과 일치)",
        not exact_b, str(exact_b[:4]) if exact_b else "일치")
    # The number scene01 had to derive by hand, now stated by the kit.
    bdp = _demo_bd("backdrop", 55.0, W=18.0)
    pb = plan_building(bdp, dist=55.0)
    chk("backdrop 지붕 부속 = +2.90 m (S01 이 여섯 동에서 실측한 값)",
        abs(pb.roof_allow - 2.90) < 1e-9
        and abs(pb.ridge - (pb.top_z + 2.90)) < 1e-9,
        f"roof_allow {pb.roof_allow:.2f} · ridge {pb.ridge:.2f}")
    # The opt-in clamp, and the proof that it is genuinely opt-in.
    eyes2 = judged_eyes(0.0)
    # h chosen so the **shell** clears the ceiling and only the penthouse breaks it
    # (d_true 32 -> z_ceil 4.80; shell top 2.80, so the head-room is 2.00 m: more
    # than the 1.20 statutory parapet, less than the 2.90 penthouse).
    tall = dict(x0=30.0, x1=48.0, y0=-9.0, y1=9.0, h=2.80, floors=1,
                axis="x", facade_x=30.0, face_dir=-1.0)
    pu = plan_building(tall, eyes=eyes2, kind="backdrop")
    pc = plan_building(tall, eyes=eyes2, kind="backdrop", roof_under_ceil=True)
    chk("기본값은 클램프 없음 (roof_under_ceil False · ridge = top+2.90)",
        pu.roof_under_ceil is False
        and abs(pu.ridge - (pu.top_z + PH_H)) < 1e-9, f"{pu.ridge:.2f}")
    chk("roof_under_ceil=True 는 옥탑을 z_ceil 로 자른다",
        pc.ridge <= pc.z_ceil + 1e-9 and pc.ridge < pu.ridge,
        f"clamp {pc.ridge:.2f} ≤ z_ceil {pc.z_ceil:.2f} < 무클램프 {pu.ridge:.2f}")
    Ku, Kc = _MockKit(oriented=True), _MockKit(oriented=True)
    build_korean_building(Ku, None, "/W/B", tall, _ROLE_MTLS, eyes=eyes2,
                          kind="backdrop")
    build_korean_building(Kc, None, "/W/B", tall, _ROLE_MTLS, eyes=eyes2,
                          kind="backdrop", roof_under_ceil=True)
    tu = max(c[2][2] + c[3][2] / 2.0 for c in Ku.calls)
    tc = max(c[2][2] + c[3][2] / 2.0 for c in Kc.calls)
    chk("클램프 팔의 실제 최상단도 z_ceil 이하 (선언과 기하가 같다)",
        abs(tu - pu.ridge) < 1e-9 and abs(tc - pc.ridge) < 1e-9
        and tc <= pc.z_ceil + 1e-9, f"무클램프 {tu:.2f} · 클램프 {tc:.2f}")
    # A shell that already breaks the ceiling cannot be rescued by the clamp: the
    # 1.20 m parapet is statutory and stays. The clamp must **say so**, not fake it.
    huge = dict(tall, h=9.0, floors=3)
    ph_ = plan_building(huge, eyes=eyes2, kind="backdrop", roof_under_ceil=True)
    chk("셸이 이미 천장을 넘으면 클램프는 법정 파라펫을 유지하고 ridge 로 사실을 말한다",
        abs(ph_.roof_allow - RAIL_H) < 1e-9 and ph_.ridge > ph_.z_ceil,
        f"ridge {ph_.ridge:.2f} > z_ceil {ph_.z_ceil:.2f} · allow {ph_.roof_allow:.2f}")

    print("\n" + "=" * 74)
    n_ok, n = sum(ok), len(ok)
    print(f"검사 {n_ok}/{n} 통과")
    print("=" * 74)
    if n_ok != n:
        raise AssertionError(f"자기검사 실패 {n - n_ok}건")
    return True


# ---------------------------------------------------------------------------
# Measurement over the 33 scenes — if scenes/ sits alongside, compute the prim
# delta against the current implementation.
# ---------------------------------------------------------------------------
def _scan_scenes(verbose=True):
    import ast
    import glob
    import os
    root = os.path.dirname(os.path.abspath(__file__))
    dirs = [os.path.join(root, "scenes", "main"),
            os.path.join(root, "scenes", "batch1")]
    if not any(os.path.isdir(d) for d in dirs):
        if verbose:
            print("\n[33씬 실측] scenes/ 없음 — 건너뜀")
        return None
    REQ = {"x0", "x1", "y0", "y1", "h", "floors"}
    DEF_WIN = dict(w=1.2, h=1.6, inset=0.15, col_step=2.5, margin=2.0)

    def _lit(n):
        try:
            return ast.literal_eval(n)
        except Exception:
            return None

    def _as_dict(node):
        if isinstance(node, ast.Dict):
            o = {}
            for k, v in zip(node.keys, node.values):
                kk = _lit(k)
                if isinstance(kk, str):
                    o[kk] = _lit(v)
            return o
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "dict":
            return {kw.arg: _lit(kw.value) for kw in node.keywords if kw.arg}
        return None

    rows = []
    for d in dirs:
        for f in sorted(glob.glob(os.path.join(d, "scene*.py"))):
            tree = ast.parse(open(f, encoding="utf-8").read())
            win = None
            bds = []
            gy = None
            for node in ast.walk(tree):
                # The scene's own judged-eye centre line, for B-F3. 21 of 33
                # scenes call `sc.grid_views(0.0)`; a few pass their own literal
                # (0.4 / -2.75 / -3.6) and a few pass a name we cannot resolve
                # statically — those fall back to 0.0 and are counted as such.
                if isinstance(node, ast.Call) and getattr(
                        node.func, "attr", None) == "grid_views" and node.args:
                    v = _lit(node.args[0])
                    if isinstance(v, (int, float)) and gy is None:
                        gy = float(v)
                dd = _as_dict(node)
                if not dd:
                    continue
                if REQ.issubset(dd.keys()):
                    if any(dd[k] is None for k in REQ):
                        continue
                    bds.append(dd)
                elif win is None and set(dd.keys()) >= {"w", "h", "inset",
                                                        "col_step", "margin"}:
                    win = dd
            for b in bds:
                b["_scene"] = os.path.basename(f)
                b["_win"] = win or DEF_WIN
                b["_gy"] = 0.0 if gy is None else gy
            rows += bds
    if not rows:
        return None

    def cur_prims(bd, wd):
        """Reproduce the prim count of the current build_building(LOOK_GEO=True)."""
        base = float(bd.get("base_z", 0.0) or 0.0)
        Lx, Ly = bd["x1"] - bd["x0"], bd["y1"] - bd["y0"]
        hh, nfl = float(bd["h"]), int(bd["floors"])
        fstep = hh / nfl
        ay = bd.get("axis", "y") == "y"
        usable = (Lx if ay else Ly) - 2 * wd["margin"]
        ncols = max(1, int(usable / wd["col_step"]))
        dist = float(bd.get("lod_dist",
                            abs(bd.get("facade_y" if ay else "facade_x", 0.0))))
        nrows = fk.window_rows_visible(dist, fstep, nfl, base_z=base,
                                       near_dist=20.0, min_rows=2)
        W = Lx if ay else Ly
        n = 1 + nrows * ncols + nrows + 1 + 1 + 12 + 2
        n += max(1, int(math.ceil(W / 40.0))) * sum(
            1 for i in range(min(nrows, nfl)) if 2 <= i + 1 <= 11)
        n += max(2, int(W / 12.0) + 1)
        if min(4.2, Lx * 0.34) > 1.2 and min(3.4, Ly * 0.34) > 1.2:
            n += 2
        return n, nrows * ncols

    tot_cur = tot_new = win_cur = 0
    kinds = {}
    tiers = {}
    over = []
    bays_out = 0
    d_shift = {"promote": 0, "demote": 0, "same": 0}
    d_delta = []
    bs4 = 0
    for b in rows:
        c, w = cur_prims(b, b["_win"])
        tot_cur += c
        win_cur += w
        K = _MockKit(oriented=True)
        p = plan_building(b)
        build_korean_building(K, None, "/W/B", b, Mtls("s", "g", "p"), plan=p)
        tot_new += len(K.calls)
        kinds[p.kind] = kinds.get(p.kind, 0) + 1
        tiers[p.tier] = tiers.get(p.tier, 0) + 1
        cap = prim_budget(p.kind, p.tier, p.W)          # B-F2: cap follows W
        if len(K.calls) > cap:
            over.append((b["_scene"], p.kind, p.tier, len(K.calls), cap))
            print(f"    [예산초과] {b['_scene']} {p.kind}/{p.tier} "
                  f"{len(K.calls)} > {cap}")
        if p.n_bays:                                    # B-F2 band audit
            bw = p.W / p.n_bays
            if not (SHOP_BAY_MIN - 1e-9 <= bw <= SHOP_BAY_MAX + 1e-9):
                bays_out += 1
        # --- B-F3 / BS-4, measured but **not applied** (scenes are unwired) ---
        pe = plan_building(b, eyes=judged_eyes(b.get("_gy", 0.0)),
                           backdrop_demote=False)
        d_delta.append(p.dist - pe.d_true)
        if pe.tier == p.tier:
            d_shift["same"] += 1
        elif pe.d_true < p.dist:
            d_shift["promote"] += 1
        else:
            d_shift["demote"] += 1
        if pe.in_frame is False:
            bs4 += 1
    if verbose:
        print("\n" + "=" * 74)
        print(f"33씬 실측 ({len(rows)}동, scene18 town 13동은 튜플 생성이라 제외)")
        print("=" * 74)
        print(f"  현행 build_building 총 프림 : {tot_cur:6d} (그중 창 {win_cur})")
        print(f"  building_kit  총 프림       : {tot_new:6d}")
        print(f"  증감                        : {tot_new - tot_cur:+6d} "
              f"({100.0 * (tot_new - tot_cur) / max(1, tot_cur):+.1f} %)")
        print(f"  추론 유형 분포 : {kinds}")
        print(f"  LOD 티어 분포  : {tiers}")
        print(f"  [B-F2] 베이 폭 3.0~4.5 m 밖 : {bays_out}동 "
              f"(상한이 물린 초광폭 파사드)")
        print(f"  [예산] 초과 : {len(over)}동")
        dd = sorted(d_delta)
        print(f"  [B-F3] 씬별 판정 시선 기준 티어 변동 : "
              f"승급 {d_shift['promote']} · 강등 {d_shift['demote']} · "
              f"동일 {d_shift['same']} / {len(rows)}동 "
              f"({100.0 * (len(rows) - d_shift['same']) / max(1, len(rows)):.1f} % 오티어)")
        print(f"  [B-F3] d_default − d_true : 평균 {sum(dd) / max(1, len(dd)):+.1f} · "
              f"중앙 {dd[len(dd) // 2]:+.1f} · 범위 {dd[0]:+.1f} … {dd[-1]:+.1f} m")
        print(f"  [BS-4] ±30° 프레임 밖 (backdrop 대상) : {bs4}동 / {len(rows)}동")
    return tot_cur, tot_new


if __name__ == "__main__":
    selfcheck()
    _scan_scenes()
