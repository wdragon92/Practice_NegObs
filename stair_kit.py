# -*- coding: utf-8 -*-
"""
stair_kit.py - Korean statutory stair component kit (landings, wide-stair mid rails, handrails)

For Isaac Sim 4.5 / procedural USD generation. **Z-up coordinate system, metres.**
Statute text gives dimensions in mm/cm, so every constant is converted to metres
**exactly once** at the top of this file; no mm literals appear later in the code
(this blocks conversion mistakes).

--------------------------------------------------------------------------
Why this file exists - the 3 P0 violations the survey confirmed
--------------------------------------------------------------------------
The "not applied" table in `Docs/surveys/korean_pedestrian_geometry.md` §2 /
`_dimension_index.md` lists items that are **legally mandatory yet absent from
all 33 scenes**:

  P0-1  Wide-stair mid rail: stairs wider than 3 m need a rail every 3 m.
        Exemption applies only when (riser <=150 mm **and** tread >=300 mm).
        Note: it is not "or". `mid_rail_lines()` is the single decision point.
  P0-2  Landing: every 3 m of rise (2 m inside housing complexes), depth >=1.20 m.
        A long uninterrupted flight is a "stair that cannot exist in Korea".
  P0-3  Outdoor stair spec: riser <=200 mm, tread >=240 mm - **steeper than indoor.**
        An outdoor stair built to the indoor rule (riser <=180) is too shallow.

--------------------------------------------------------------------------
Design conventions (project-wide)
--------------------------------------------------------------------------
- **Do not import scene_common.** Functions that create USD prims receive the
  creation helpers (`add_box` / `add_cylinder`) **by injection**. The injected
  signatures match scene_common:
      add_box(stage, path, center, size, mtl=None, collider=False)
      add_cylinder(stage, path, center, radius, height, mtl=None,
                   rotY=0.0, rotX=0.0, collider=False)
- **Deterministic RNG.** This module uses no randomness at all (not even `hash()`).
  If jitter is needed, the caller builds `random.Random(seed)` and passes it in.
- **No unsourced numbers.** Values absent from the index are tagged
  `[estimate]` / `[no source]`.
- Descent convention matches scene_common `_stair_steps`:
  **descends from x0 towards +X**; ground at the top is z = z_top; tread i sits at
  z_top - riser*(i+1) and spans x in [x0+i*tread, x0+(i+1)*tread].

--------------------------------------------------------------------------
GT (drop label) overview - also read the `GT:` line in each function docstring
--------------------------------------------------------------------------
The key cue for this research is the **nosing line**. Among the parts here:
  - **Mid rails and handrails** are vertical/diagonal members standing *above* the
    stair surface, so they do not change the drop geometry z(x,y) -> **GT invariant**
    (only self-occlusion and shadows change).
  - **Landings** change the z(x) profile itself -> **GT changes**. Total drop is
    preserved, but the run grows by (landing depth x count), the landing top becomes
    a flat band of zero local drop, and **the landing front edge becomes a new drop
    edge**.
    -> Any scene that gains a landing must invalidate its cached drop/depth GT.
"""

import math

__all__ = [
    "K", "stair_landings", "build_stair_landing", "mid_rail_lines",
    "build_handrail", "check_stair_compliance", "flight_nosing_lines",
]

# Float comparison tolerance. Many scenes sit exactly on a statutory threshold
# (3.000 m, 0.150 m ...) - scene16 width 3.0, scene14 riser 0.15 - so this value decides.
TOL = 1e-9


# ===========================================================================
# [0] Statutory constants - mm/cm statute text is converted to metres here, once
# ===========================================================================
class K:
    """Statutory dimension constants (metres). Each value cites its clause in a comment.

    Sources: Rules on Evacuation and Fire Protection Structures of Buildings §15
             (hereafter "evac/fire")
             Regulations on Housing Construction Standards §16/§18 (hereafter "housing")
             Docs/surveys/korean_pedestrian_geometry.md §2, §6.2
             Docs/surveys/_dimension_index.md "not applied" table
    """

    # --- Landings (evac/fire §15(1)1 / housing §16(2)1) ---
    LANDING_MAX_RISE = 3.00          # Stairs over 3 m rise -> a landing at least every 3 m
    LANDING_MAX_RISE_HOUSING = 2.00  # Buildings and outdoor stairs inside a housing complex
    LANDING_MAX_RISE_ENTRY = 2.50    # Entrance stairs of each building block (1st floor only)
    LANDING_DEPTH_MIN = 1.20         # "effective width 120 cm" = depth along the direction of travel

    # --- Wide-stair mid rail (evac/fire §15(1)3) ---
    MIDRAIL_MAX_SPAN = 3.00          # "wider than 3 m" -> a rail every 3 m or less
    MIDRAIL_EXEMPT_RISER = 0.150     # Proviso: riser <=15 cm  **and**
    MIDRAIL_EXEMPT_TREAD = 0.300     #          tread >=30 cm  - exempt only if both hold

    # --- Rails on both sides (evac/fire §15(1)2) ---
    RAIL_REQUIRED_DROP = 1.00        # Stairs/landings over 1 m high -> rails on both sides
    #   -> Stairs with drop <=1.00 m (5 steps at outdoor riser 0.20, 6 at riser 0.15)
    #     **have no rail obligation.** This also justifies rail-free scenes.

    # --- Stair section (housing §16(1)) ---
    OUTDOOR_RISER_MAX = 0.200        # Outdoor stairs of a building - steeper than indoor
    OUTDOOR_TREAD_MIN = 0.240
    OUTDOOR_WIDTH_MIN = 0.900
    COMMON_RISER_MAX = 0.180         # Stairs in shared use
    COMMON_TREAD_MIN = 0.260
    COMMON_WIDTH_MIN = 1.200

    # --- Handrail (evac/fire §15(4)) ---
    HANDRAIL_DIA_MIN = 0.032         # Max diameter >=3.2 cm
    HANDRAIL_DIA_MAX = 0.038         #              <=3.8 cm
    HANDRAIL_H = 0.850               # 85 cm above the stair
    HANDRAIL_WALL_GAP = 0.050        # >=5 cm clear of the wall etc.
    HANDRAIL_EXT_MIN = 0.300         # >=30 cm outward past the horizontal end section

    # --- Convention/estimate (not statutory - always use with the tag) ---
    HANDRAIL_POST_SPACING = 1.20     # `[no source]` No regulation on handrail post spacing.
    #   Unlike guardrail posts at 2.0 m (mesh fence 2.08 applied by analogy,
    #   _dimension_index), handrails are conventionally denser -> 1.2 m `[estimate]`.
    LANDING_CROSS_SLOPE = 0.02       # `[estimate]` Sidewalk cross slope 1/25 applied by analogy (1-2 %)
    NOSING_BAND_W = 0.050            # Non-slip strip width - no statutory figure.
    #   KS F 4527 nominal 50 mm + standard building specification practice `[verified-nonstatutory]`


# ===========================================================================
# [1] Landing planning - pure computation (USD-independent, unit testable)
# ===========================================================================
def stair_landings(total_drop, riser, tread,
                   max_rise=K.LANDING_MAX_RISE,
                   landing_depth=K.LANDING_DEPTH_MIN,
                   x0=0.0, z_top=0.0):
    """Split the total drop by the statutory period into a **flight / landing plan**.

    Evac/fire §15(1)1: stairs rising more than 3 m need a landing at least every
    3 m with effective width >=1.2 m. Buildings and outdoor stairs inside a housing
    complex use `max_rise=2.0` (housing §16(2)1); 1st-floor block entrance stairs
    use `max_rise=2.5`.

    The coordinate convention matches scene_common `_stair_steps`: descend from
    (x0, z_top) **towards +X**. A landing top sits at the **same z** as the last
    tread of the preceding flight (i.e. that tread extended by landing_depth), so
    inserting landings **preserves the z ladder of the nosing line**.

    Args
      total_drop    : total drop [m] (positive)
      riser         : riser height [m]
      tread         : tread depth [m]
      max_rise      : maximum rise/fall a single flight may cover [m]
      landing_depth : landing depth along travel [m]; below 1.20 a warning is logged
      x0, z_top     : stair start point

    Returns dict
      n_steps       : total step count (= round(total_drop/riser))
      riser_eff     : total_drop/n_steps - the actual uniform riser
      n_flights     : number of flights
      n_landings    : number of landings (= n_flights - 1)
      flights       : [{i, n_steps, x0, x1, z_top, z_bot, rise, run}]
      landings      : [{i, x0, x1, z, depth}]
      total_run     : total X length including landings
      run_delta     : extra run caused by landings (= n_landings x landing_depth)
      compliant     : whether the plan itself meets the statutory period and depth
      notes         : list of warning strings

    Distribution rule (deterministic - no randomness): with m = floor(max_rise/riser)
    steps per flight, n_flights = ceil(n_steps/m); the remainder is handed out
    **one step at a time starting from the first flight**. Same input, same output.

    GT: **changes the drop label.** Total drop is preserved, but (a) the run grows by
        run_delta so the z(x) profile is translated and lengthened, (b) the
        landing_depth band of the landing top is a **flat strip of zero local drop**,
        and (c) the landing front edge becomes a **new drop edge** (residual drop =
        sum of the downstream flights).
        -> Scenes using this plan must regenerate their drop/depth GT.
        (Unlike mid rails and handrails, the landing is the only part that touches GT.)
    """
    total_drop = float(total_drop)
    riser = float(riser)
    tread = float(tread)
    notes = []

    if riser <= TOL:
        raise ValueError("riser must be > 0 (m)")
    if tread <= TOL:
        raise ValueError("tread must be > 0 (m)")
    if total_drop < 0.0:
        raise ValueError("total_drop must be >= 0 (m)")
    if max_rise <= TOL:
        raise ValueError("max_rise must be > 0 (m)")

    n_steps = int(round(total_drop / riser))
    if n_steps < 1:
        n_steps = 1
    riser_eff = total_drop / n_steps
    if abs(riser_eff - riser) > 1e-6:
        notes.append(
            "total_drop/riser 가 정수가 아니다 → riser_eff %.4f 로 균등화"
            % riser_eff)

    if landing_depth < K.LANDING_DEPTH_MIN - TOL:
        notes.append(
            "계단참 깊이 %.3f < 법정 최소 %.2f m (피난방화 §15①1)"
            % (landing_depth, K.LANDING_DEPTH_MIN))

    # Max steps per flight - the rise coverable without a landing
    m = int(math.floor(max_rise / riser_eff + TOL))
    if m < 1:
        m = 1
        notes.append(
            "단높이 %.3f 가 max_rise %.2f 보다 크다 → flight 당 1단으로 강제"
            % (riser_eff, max_rise))

    n_flights = int(math.ceil(float(n_steps) / m - TOL))
    if n_flights < 1:
        n_flights = 1

    base, rem = divmod(n_steps, n_flights)
    counts = [base + (1 if i < rem else 0) for i in range(n_flights)]

    flights = []
    landings = []
    x = float(x0)
    z = float(z_top)
    for i, c in enumerate(counts):
        run = c * tread
        rise = c * riser_eff
        flights.append(dict(i=i, n_steps=c, x0=x, x1=x + run,
                            z_top=z, z_bot=z - rise, rise=rise, run=run))
        x += run
        z -= rise
        if i < n_flights - 1:
            landings.append(dict(i=i, x0=x, x1=x + landing_depth,
                                 z=z, depth=float(landing_depth)))
            x += landing_depth

    max_flight_rise = max(f["rise"] for f in flights)
    compliant = (max_flight_rise <= max_rise + 1e-6
                 and landing_depth >= K.LANDING_DEPTH_MIN - TOL)

    return dict(
        total_drop=total_drop, riser=riser, riser_eff=riser_eff, tread=tread,
        n_steps=n_steps, n_flights=n_flights, n_landings=len(landings),
        flights=flights, landings=landings,
        max_rise=float(max_rise), landing_depth=float(landing_depth),
        max_flight_rise=max_flight_rise,
        total_run=x - float(x0),
        run_delta=len(landings) * float(landing_depth),
        z_bottom=z, compliant=compliant, notes=notes,
    )


def flight_nosing_lines(plan):
    """Extract only the **(x, z) list of the nosing line** from a plan. For GT checking.

    Each element = (x_nose, z_tread): the +X end of that tread (the nosing) and its z.
    A landing front edge is included as a nosing too (landing front = new drop edge).

    GT: not a generator (creates no prims). Used to **diff the drop-edge set before
        and after landings are introduced**, yielding the GT change scope.
    """
    lines = []
    for f in plan["flights"]:
        for k in range(1, f["n_steps"] + 1):
            lines.append((f["x0"] + k * plan["tread"],
                          f["z_top"] - k * plan["riser_eff"]))
    for l in plan["landings"]:
        lines.append((l["x1"], l["z"]))
    lines.sort(key=lambda t: t[0])
    return lines


# ===========================================================================
# [2] Landing slab generation
# ===========================================================================
def build_stair_landing(stage, path, landing, y0, y1, base_z, mtl,
                        add_box, collider=True, edge_lip=0.0):
    """Turn one landing dict returned by `stair_landings()` into a solid slab.

    Args
      landing  : {"x0","x1","z","depth"} - an element of the stair_landings() output
      y0, y1   : stair width (Y). The statute requires "at least the effective width
                 of that stair" (housing §16(2)1), so **matching the stair width** is
                 the default.
      base_z   : slab underside z (match the stair solid base_z to avoid floating)
      mtl      : material (caller's make_pbr output)
      add_box  : injected helper with the same signature as scene_common.add_box
      edge_lip : extra +X protrusion of the landing front edge [m]. 0 keeps the plan.
                 `[no source]` - no rule on landing drip edge/nose overhang. Default 0.

    Drainage slope is **deliberately omitted.** There is no landing-specific slope
    rule, and applying the sidewalk cross slope 1/25 by analogy is an `[estimate]`
    (K.LANDING_CROSS_SLOPE). A slope would require injecting a rotatable box helper
    (scene_common `_oriented_box`), so this function builds a **level slab** only.

    Returns: the prim returned by add_box.

    GT: the slab **top (z)** is flat ground with zero local drop; the **+X front edge**
        becomes a new drop edge (the entire flight drop below it hangs on that edge).
        The slab top shares z with the last tread of the preceding flight, so the
        **upstream nosing z ladder is unchanged**; all that appears is one long tread.
        This property is why landing insertion does not destroy the nosing cue.
    """
    x0 = float(landing["x0"])
    x1 = float(landing["x1"]) + float(edge_lip)
    z_top = float(landing["z"])
    cx = (x0 + x1) / 2.0
    cy = (float(y0) + float(y1)) / 2.0
    hz = z_top - float(base_z)
    if hz <= 0.0:
        raise ValueError("landing z (%.3f) must be above base_z (%.3f)"
                         % (z_top, base_z))
    return add_box(stage, path, (cx, cy, z_top - hz / 2.0),
                   (x1 - x0, abs(float(y1) - float(y0)), hz),
                   mtl, collider=collider)


# ===========================================================================
# [3] Wide-stair mid rail positions - the single decision point for P0-1
# ===========================================================================
def mid_rail_lines(y0, y1, max_span=K.MIDRAIL_MAX_SPAN,
                   riser=None, tread=None):
    """Return the **list of y coordinates where mid rails belong**, given the stair width.

    Evac/fire §15(1)3, verbatim:
      "Stairs wider than 3 metres shall have a rail in the middle of the stair at
       intervals of no more than 3 metres. This does not apply where the stair
       **riser is 15 centimetres or less and** the **tread is 30 centimetres or more**."

    Note: the exemption is an **AND**. Only riser <= 0.150 **and** tread >= 0.300
      together exempt. If just one holds, the mid rail is still mandatory.
      (If either riser or tread is None, no exemption is decided = conservative.)

    Note: the threshold is **strictly greater** (>). A width of exactly 3.000 m is not
      "wider than 3 m", so no obligation arises. scene16/17 sit exactly on this edge.

    Args
      y0, y1   : stair width interval (order irrelevant)
      max_span : maximum spacing between rails [m]
      riser    : riser [m] (for the exemption test; None disables the exemption)
      tread    : tread [m] (for the exemption test; None disables the exemption)

    Returns: ascending list of y coordinates. No obligation -> empty list.
          Spacing is an **even split** of the width into ceil(width/max_span) bays
          (deterministic). E.g. width 12 m -> 3 lines at [-3, 0, +3] (span 3.0 each).

    GT: **drop label invariant.** A mid rail is a vertical member standing on the stair
        surface and does not touch the z(x,y) terrain. It is however a linear structure
        running along the drop direction (+X), cutting the nosing line lengthwise and
        creating self-occlusion and shadow -> the RGB context cue gains a lot of
        information while the drop GT stays as is.
    """
    a, b = float(y0), float(y1)
    lo, hi = (a, b) if a <= b else (b, a)
    width = hi - lo

    if riser is not None and tread is not None:
        exempt = (float(riser) <= K.MIDRAIL_EXEMPT_RISER + TOL
                  and float(tread) >= K.MIDRAIL_EXEMPT_TREAD - TOL)
        if exempt:
            return []

    if width <= float(max_span) + TOL:      # "wider than" = strictly greater. 3.000 does not qualify
        return []

    n_bays = int(math.ceil(width / float(max_span) - TOL))
    return [lo + width * k / float(n_bays) for k in range(1, n_bays)]


# ===========================================================================
# [4] Handrail - dia 32-38, h 850, horizontal end extension >=300
# ===========================================================================
def build_handrail(stage, prefix, y, x_top, run, drop, mtl, add_cylinder,
                   z_top=0.0, height=K.HANDRAIL_H, dia=0.034,
                   ext_top=K.HANDRAIL_EXT_MIN, ext_bot=K.HANDRAIL_EXT_MIN,
                   post_r=0.020, post_spacing=K.HANDRAIL_POST_SPACING,
                   ground_fn=None, wall_y=None, wall_side=1.0,
                   wall_gap=K.HANDRAIL_WALL_GAP, bracket_r=0.012,
                   strict=True):
    """One statutory handrail line. Evac/fire §15(4).

      1. Max diameter **32-38 mm**, round/oval section        -> `dia`
      2. **>=50 mm** clear of the wall etc.; height **850 mm** above the stair
         -> `wall_gap`, `height`
      3. **>=300 mm** outward past the horizontal section where the stair ends
         -> `ext_top`, `ext_bot`

    Note: the horizontal end extension is this part's **Korean signature in
      silhouette**. The sloped rail does not simply stop at the stair end; at both top
      and bottom it continues horizontally at least 30 cm over level ground before
      terminating. At distance it reads as "two right-angle bends".

    Geometry (same descent convention as scene_common)
      x_top          : x where the slope starts (z = z_top here)
      run, drop      : horizontal length and drop of the sloped run -> ends at
                       x_top+run, z_top-drop
      top extension  : x_top-ext_top .. x_top,        z = z_top + height
      bottom ext.    : x_top+run .. x_top+run+ext_bot, z = z_top - drop + height
      height datum   : the **nosing connection line** (the diagonal through the tread
                       noses). This is how we read the statute's "height from the
                       stair" `[estimate]` - the statute does not name a measurement
                       datum `[no source]`.

    Wall-mounted mode: if `wall_y` is given, y is ignored and
      y_rail = wall_y + wall_side x (wall_gap + dia/2)
    and **brackets** (short Y-axis cylinders) are hung instead of posts.
    With `wall_y=None` the rail is free-standing on posts.

    The default post spacing `post_spacing` of 1.2 m is `[no source]` (no clause
    regulates handrail post spacing) - denser than the 2.0 m guardrail post
    convention `[estimate]`.

    With strict=True a statutory-minimum violation raises ValueError; with False it is
    returned as a warning only.

    Returns dict: {"prims": [...], "y": actual rail y, "warnings": [...],
                "x_start": topmost x, "x_end": bottommost x}

    GT: **drop label invariant.** A handrail creates no terrain z. The horizontal end
        extensions float over level ground outside the stair (a zero-drop area), so
        they add no pixel to the drop mask. Only silhouette and shadow change.
    """
    warns = []
    dia = float(dia)
    if not (K.HANDRAIL_DIA_MIN - TOL <= dia <= K.HANDRAIL_DIA_MAX + TOL):
        msg = ("손잡이 지름 %.4f m 가 법정 φ%.3f~%.3f 밖 (피난방화 §15④1)"
               % (dia, K.HANDRAIL_DIA_MIN, K.HANDRAIL_DIA_MAX))
        if strict:
            raise ValueError(msg)
        warns.append(msg)
    for nm, v in (("ext_top", ext_top), ("ext_bot", ext_bot)):
        if float(v) < K.HANDRAIL_EXT_MIN - TOL:
            msg = ("%s %.3f m < 법정 수평 연장 %.2f m (피난방화 §15④3)"
                   % (nm, float(v), K.HANDRAIL_EXT_MIN))
            if strict:
                raise ValueError(msg)
            warns.append(msg)
    if float(wall_gap) < K.HANDRAIL_WALL_GAP - TOL and wall_y is not None:
        msg = ("벽 이격 %.3f m < 법정 %.2f m (피난방화 §15④2)"
               % (float(wall_gap), K.HANDRAIL_WALL_GAP))
        if strict:
            raise ValueError(msg)
        warns.append(msg)

    r = dia / 2.0
    run = float(run)
    drop = float(drop)
    x_top = float(x_top)
    z_top = float(z_top)
    height = float(height)
    ext_top = float(ext_top)
    ext_bot = float(ext_bot)

    if wall_y is None:
        y_rail = float(y)
    else:
        y_rail = float(wall_y) + float(wall_side) * (float(wall_gap) + r)

    x_start = x_top - ext_top
    x_slope_end = x_top + run
    x_end = x_slope_end + ext_bot
    z_rail_top = z_top + height              # Rail centre z of the top horizontal section
    z_rail_bot = z_top - drop + height       # Rail centre z of the bottom horizontal section

    prims = []

    # (a) Top horizontal extension - lay the cylinder axis (Z) along X (rotY=90)
    if ext_top > TOL:
        prims.append(add_cylinder(
            stage, "%s/ExtTop" % prefix,
            ((x_start + x_top) / 2.0, y_rail, z_rail_top),
            r, ext_top, mtl, rotY=90.0))

    # (b) Sloped section
    if run > TOL or drop > TOL:
        L = math.hypot(run, drop)
        ang = math.degrees(math.atan2(drop, run))
        prims.append(add_cylinder(
            stage, "%s/Slope" % prefix,
            (x_top + run / 2.0, y_rail, z_rail_top - drop / 2.0),
            r, L, mtl, rotY=90.0 + ang))

    # (c) Bottom horizontal extension
    if ext_bot > TOL:
        prims.append(add_cylinder(
            stage, "%s/ExtBot" % prefix,
            ((x_slope_end + x_end) / 2.0, y_rail, z_rail_bot),
            r, ext_bot, mtl, rotY=90.0))

    # (d) Support - posts when free-standing, brackets when wall-mounted
    def _nose_z(x):
        """Nosing connection line z (the rail height datum)."""
        if x <= x_top:
            return z_top
        if x >= x_slope_end:
            return z_top - drop
        return z_top - drop * (x - x_top) / run if run > TOL else z_top - drop

    def _rail_z(x):
        return _nose_z(x) + height

    gz_fn = ground_fn if ground_fn is not None else _nose_z

    n_sup = int(math.floor((x_end - x_start) / float(post_spacing) + TOL)) + 1
    for i in range(n_sup):
        xp = x_start + i * float(post_spacing)
        if xp > x_end + TOL:
            break
        rz = _rail_z(xp)
        if wall_y is None:
            gz = float(gz_fn(xp))
            h = rz - gz
            if h > 1e-3:
                prims.append(add_cylinder(
                    stage, "%s/Post_%d" % (prefix, i),
                    (xp, y_rail, gz + h / 2.0), post_r, h, mtl))
        else:
            arm = abs(y_rail - float(wall_y))
            if arm > 1e-3:
                prims.append(add_cylinder(
                    stage, "%s/Brk_%d" % (prefix, i),
                    (xp, (y_rail + float(wall_y)) / 2.0, rz),
                    bracket_r, arm, mtl, rotX=90.0))

    return dict(prims=prims, y=y_rail, warnings=warns,
                x_start=x_start, x_end=x_end,
                z_top_rail=z_rail_top, z_bot_rail=z_rail_bot)


# ===========================================================================
# [5] Compliance decision
# ===========================================================================
def _v(code, sev, rule, expected, actual, msg):
    return dict(code=code, severity=sev, rule=rule,
                expected=expected, actual=actual, msg=msg)


def check_stair_compliance(riser, tread, width, total_drop, outdoor=True,
                           has_rail=None, n_mid_rails=0, n_landings=0,
                           landing_depth=None, housing_complex=False,
                           handrail=None, label="", note=""):
    """Check one stair specification against the statute and return a **violation dict**.

    Args
      riser, tread  : riser and tread [m]. If non-uniform, pass (max riser, min tread)
                      = **the worst case**.
      width         : effective stair width [m]
      total_drop    : total drop [m]
      outdoor       : True -> outdoor stair rule (riser <=0.20 / tread >=0.24 /
                      width >=0.90)
                      False -> shared-use stair rule (<=0.18 / >=0.26 / >=1.20)
      has_rail      : "both" | "one" | "none" | True | False | None (unknown)
      n_mid_rails   : number of **mid** rail lines in the scene (side rails excluded)
      n_landings    : number of **intermediate** landings in the scene (level ground at
                      top and bottom excluded)
      landing_depth : current landing depth [m] (None -> test skipped)
      housing_complex : building/outdoor stair inside a housing complex -> 2 m period
      handrail      : {"dia":..., "h":..., "ext":...} or None (test skipped)

    Returns dict - fields shaped so one diagnostic-table row can be built directly.
      req_landings / have_landings / req_mid_rails / have_mid_rails /
      mid_rail_exempt / outdoor_ok / rail_required / violations / ok / p0

    GT: **decision only. Creates no prims, so it is unrelated to the drop label.**
        However, a scene flagged for P0-2 (landing) will have its GT change once fixed
        (see the GT: line of stair_landings). That distinction is the point of the
        diagnostic table.
    """
    riser = float(riser)
    tread = float(tread)
    width = float(width)
    total_drop = float(total_drop)
    V = []

    # --- Section spec (P0-3) ---
    r_max = K.OUTDOOR_RISER_MAX if outdoor else K.COMMON_RISER_MAX
    t_min = K.OUTDOOR_TREAD_MIN if outdoor else K.COMMON_TREAD_MIN
    w_min = K.OUTDOOR_WIDTH_MIN if outdoor else K.COMMON_WIDTH_MIN
    kind = "옥외계단" if outdoor else "공동사용 계단"

    if riser > r_max + TOL:
        V.append(_v("D1", "P0", "주택기준 §16①",
                    "단높이 ≤%.3f" % r_max, "%.3f" % riser,
                    "%s 단높이 초과 (%.3f > %.3f)" % (kind, riser, r_max)))
    if tread < t_min - TOL:
        V.append(_v("D2", "P0", "주택기준 §16①",
                    "단너비 ≥%.3f" % t_min, "%.3f" % tread,
                    "%s 단너비 미달 (%.3f < %.3f)" % (kind, tread, t_min)))
    if width < w_min - TOL:
        V.append(_v("D3", "P1", "주택기준 §16①",
                    "유효폭 ≥%.3f" % w_min, "%.3f" % width,
                    "%s 유효폭 미달 (%.3f < %.3f)" % (kind, width, w_min)))
    outdoor_ok = not any(x["code"] in ("D1", "D2", "D3") for x in V)

    # --- Landings (P0-2) ---
    max_rise = (K.LANDING_MAX_RISE_HOUSING if housing_complex
                else K.LANDING_MAX_RISE)
    if total_drop > max_rise + TOL:
        req_landings = int(math.ceil(total_drop / max_rise - TOL)) - 1
    else:
        req_landings = 0
    if n_landings < req_landings:
        V.append(_v("L1", "P0", "피난방화 §15①1 / 주택기준 §16②1",
                    "계단참 %d 개(%.1f m 마다)" % (req_landings, max_rise),
                    "%d 개" % n_landings,
                    "계단참 %d 개 부족 — 낙차 %.2f m 직통은 한국에 존재할 수 "
                    "없는 계단" % (req_landings - n_landings, total_drop)))
    if (landing_depth is not None and n_landings > 0
            and float(landing_depth) < K.LANDING_DEPTH_MIN - TOL):
        V.append(_v("L2", "P1", "피난방화 §15①1",
                    "깊이 ≥%.2f" % K.LANDING_DEPTH_MIN,
                    "%.3f" % float(landing_depth),
                    "계단참 깊이 미달"))

    # --- Wide-stair mid rail (P0-1) ---
    lines = mid_rail_lines(-width / 2.0, width / 2.0,
                           riser=riser, tread=tread)
    exempt = (riser <= K.MIDRAIL_EXEMPT_RISER + TOL
              and tread >= K.MIDRAIL_EXEMPT_TREAD - TOL)
    req_mid = len(lines)
    if n_mid_rails < req_mid:
        V.append(_v("R1", "P0", "피난방화 §15①3",
                    "중간난간 %d 열(3 m 이내마다)" % req_mid,
                    "%d 열" % n_mid_rails,
                    "폭 %.2f m 광폭계단 중간난간 %d 열 부족 "
                    "(면제조건 riser≤0.15 AND tread≥0.30 미충족)"
                    % (width, req_mid - n_mid_rails)))

    # --- Rails on both sides (threshold: over 1 m high) ---
    rail_required = total_drop > K.RAIL_REQUIRED_DROP + TOL
    hr = has_rail
    if hr is True:
        hr = "both"
    elif hr is False:
        hr = "none"
    if rail_required and hr in ("none", "one"):
        V.append(_v("R2", "P1", "피난방화 §15①2",
                    "양옆 난간(벽 포함)", hr,
                    "낙차 %.2f m > 1 m — 양옆 난간 의무 "
                    "(교통약자법은 편측 허용이나 건축법 계열은 양옆)"
                    % total_drop))

    # --- Handrail spec ---
    if handrail:
        d = handrail.get("dia")
        h = handrail.get("h")
        e = handrail.get("ext")
        if d is not None and not (K.HANDRAIL_DIA_MIN - TOL <= float(d)
                                  <= K.HANDRAIL_DIA_MAX + TOL):
            V.append(_v("H1", "P1", "피난방화 §15④1",
                        "φ0.032~0.038", "%.3f" % float(d), "손잡이 지름 이탈"))
        if h is not None and abs(float(h) - K.HANDRAIL_H) > 0.05:
            V.append(_v("H2", "P1", "피난방화 §15④2",
                        "h=0.850", "%.3f" % float(h), "손잡이 높이 이탈"))
        if e is not None and float(e) < K.HANDRAIL_EXT_MIN - TOL:
            V.append(_v("H3", "P1", "피난방화 §15④3",
                        "수평연장 ≥0.300", "%.3f" % float(e),
                        "끝단 수평 연장 미달"))

    p0 = sum(1 for x in V if x["severity"] == "P0")
    return dict(
        label=label, note=note,
        riser=riser, tread=tread, width=width, total_drop=total_drop,
        outdoor=outdoor, housing_complex=housing_complex,
        req_landings=req_landings, have_landings=int(n_landings),
        req_mid_rails=req_mid, have_mid_rails=int(n_mid_rails),
        mid_rail_lines=lines, mid_rail_exempt=exempt,
        outdoor_ok=outdoor_ok, rail_required=rail_required, has_rail=hr,
        violations=V, ok=(len(V) == 0), p0=p0, n_violations=len(V),
    )


# ===========================================================================
# [6] Self-check - pure computation, verified without GPU/USD
# ===========================================================================
def _selfcheck():
    ok = 0

    # (1) The exemption is an AND - these 4 cases are why this file exists
    assert mid_rail_lines(-6, 6, riser=0.150, tread=0.300) == []      # Both hold
    assert mid_rail_lines(-6, 6, riser=0.160, tread=0.340) != []      # riser X
    assert mid_rail_lines(-6, 6, riser=0.150, tread=0.280) != []      # tread X
    assert mid_rail_lines(-6, 6, riser=0.173, tread=0.300) != []      # riser X
    ok += 4

    # (2) The threshold is "greater than". Width 3.000 -> no obligation, 3.001 -> obligation
    assert mid_rail_lines(-1.5, 1.5, riser=0.17, tread=0.30) == []
    assert len(mid_rail_lines(0.0, 3.001, riser=0.17, tread=0.30)) == 1
    # Width 12 -> 3 lines, spacing 3.0
    L = mid_rail_lines(-6, 6, riser=0.17, tread=0.30)
    assert len(L) == 3 and abs(L[0] - (-3.0)) < 1e-9 and abs(L[1]) < 1e-9
    # Width 10 -> 3 lines (ceil(10/3)=4 bays, span 2.5)
    assert len(mid_rail_lines(-5, 5, riser=0.20, tread=0.34)) == 3
    ok += 4

    # (3) Landings: none at 3 m or less, evenly split above
    p = stair_landings(3.0, 0.15, 0.30)
    assert p["n_landings"] == 0 and p["n_flights"] == 1
    p = stair_landings(6.0, 0.15, 0.34)          # scene14 specification
    assert p["n_steps"] == 40 and p["n_flights"] == 2 and p["n_landings"] == 1
    assert p["max_flight_rise"] <= K.LANDING_MAX_RISE + 1e-9
    assert abs(p["run_delta"] - 1.20) < 1e-9
    assert abs(p["z_bottom"] + 6.0) < 1e-9       # Total drop preserved
    p = stair_landings(6.12, 0.17, 0.34)         # scene09 specification (uniform approximation)
    assert p["n_flights"] == 3 and p["n_landings"] == 2
    assert all(f["rise"] <= K.LANDING_MAX_RISE + 1e-9 for f in p["flights"])
    # Housing complex 2 m period
    p2 = stair_landings(6.0, 0.15, 0.34,
                        max_rise=K.LANDING_MAX_RISE_HOUSING)
    assert p2["n_flights"] == 4 and p2["n_landings"] == 3
    assert p2["max_flight_rise"] <= K.LANDING_MAX_RISE_HOUSING + 1e-9
    ok += 4

    # (4) Geometric continuity of the plan - flight end z == next landing z == next flight start z
    p = stair_landings(9.0, 0.18, 0.30)
    for i, l in enumerate(p["landings"]):
        assert abs(p["flights"][i]["z_bot"] - l["z"]) < 1e-9
        assert abs(p["flights"][i + 1]["z_top"] - l["z"]) < 1e-9
        assert abs(p["flights"][i]["x1"] - l["x0"]) < 1e-9
        assert abs(p["flights"][i + 1]["x0"] - l["x1"]) < 1e-9
    assert abs(p["total_run"] - (p["n_steps"] * 0.30
                                 + p["n_landings"] * 1.20)) < 1e-9
    ok += 1

    # (5) Nosing line - landings do not change the step count (total GT edges preserved, plus landings)
    a = stair_landings(2.4, 0.15, 0.30)
    b = stair_landings(6.0, 0.15, 0.30)
    assert len(flight_nosing_lines(a)) == a["n_steps"]
    assert len(flight_nosing_lines(b)) == b["n_steps"] + b["n_landings"]
    ok += 1

    # (6) Compliance decision
    r = check_stair_compliance(0.15, 0.38, 11.0, 0.60, outdoor=True,
                               has_rail="both", n_mid_rails=1)
    assert r["ok"] and r["req_mid_rails"] == 0 and r["mid_rail_exempt"]
    r = check_stair_compliance(0.173, 0.30, 4.0, 4.498, outdoor=True,
                               has_rail="both")
    assert r["req_landings"] == 1 and r["req_mid_rails"] == 1 and r["p0"] == 2
    r = check_stair_compliance(0.40, 0.85, 8.0, 1.20, outdoor=True)
    assert any(x["code"] == "D1" for x in r["violations"])
    r = check_stair_compliance(0.18, 0.30, 2.0, 0.90, outdoor=True,
                               has_rail="none")
    assert r["ok"], "낙차 0.90 ≤ 1 m → 난간 의무 없음"
    r = check_stair_compliance(0.18, 0.30, 2.0, 1.10, outdoor=True,
                               has_rail="none")
    assert any(x["code"] == "R2" for x in r["violations"])
    # Under the indoor (shared-use) rule riser 0.19 is a violation
    assert not check_stair_compliance(0.19, 0.30, 2.0, 0.5,
                                      outdoor=False)["outdoor_ok"]
    assert check_stair_compliance(0.19, 0.30, 2.0, 0.5,
                                  outdoor=True)["outdoor_ok"]
    ok += 6

    # (7) Handrail spec check (strict exception only, no prim creation)
    made = []

    def _fake_cyl(stage, path, center, radius, height, mtl=None,
                  rotY=0.0, rotX=0.0, collider=False):
        made.append((path, center, radius, height, rotY))
        return path

    h = build_handrail(None, "/S/HR", 1.5, 0.0, 6.4, 3.2, None, _fake_cyl)
    names = [m[0] for m in made]
    assert "/S/HR/ExtTop" in names and "/S/HR/ExtBot" in names
    assert abs(dict((m[0], m[3]) for m in made)["/S/HR/ExtTop"] - 0.30) < 1e-9
    assert abs(h["z_top_rail"] - 0.85) < 1e-9
    assert abs(h["z_bot_rail"] - (-3.2 + 0.85)) < 1e-9
    for bad in (dict(dia=0.050), dict(ext_top=0.10)):
        try:
            build_handrail(None, "/S/X", 0.0, 0.0, 1.0, 0.5, None,
                           _fake_cyl, **bad)
            raise AssertionError("strict 위반이 통과했다: %r" % bad)
        except ValueError:
            pass
    # Wall-mounted: offset from the wall by the gap plus the radius
    hw = build_handrail(None, "/S/W", 0.0, 0.0, 3.0, 1.5, None, _fake_cyl,
                        wall_y=2.0, wall_side=-1.0, dia=0.036)
    assert abs(hw["y"] - (2.0 - (0.050 + 0.018))) < 1e-9
    ok += 3

    # (8) Landing slab - verify add_box injection
    boxes = []

    def _fake_box(stage, path, center, size, mtl=None, collider=False):
        boxes.append((path, center, size))
        return path

    plan = stair_landings(6.0, 0.15, 0.34)
    build_stair_landing(None, "/S/Land_0", plan["landings"][0],
                        -2.5, 2.5, -7.0, None, _fake_box)
    (_, ctr, siz) = boxes[0]
    assert abs(siz[0] - 1.20) < 1e-9 and abs(siz[1] - 5.0) < 1e-9
    assert abs(ctr[2] + (7.0 + 3.0) / 2.0) < 1e-9   # Top -3.0, underside -7.0
    ok += 1

    print("stair_kit selfcheck: %d 그룹 통과 (USD/GPU 미사용)" % ok)
    return True


if __name__ == "__main__":
    _selfcheck()
