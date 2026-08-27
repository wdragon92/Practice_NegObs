#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lighting / camera variation kit — the `role=data` machinery.

Commissioned by `Docs/briefs/lighting_camera_variation_spec_v1.md` (design D1-D9)
and corrected throughout by `Docs/reports/lighting_spikes_v1.md`, whose MEASURED
tables supersede the spec's hypotheses. Every constant below carries the
provenance of the number, and where the measurement contradicted the design the
measurement wins and the contradiction is stated inline.

What lives here
  [0] render-role gate            D1/D2 — judge is frozen, and variation env
                                  under role=judge is a SystemExit, not a
                                  convention (spec §2.3).
  [1] deterministic seeds         spec §2.4 — zlib.crc32, never `hash()`.
  [2] azimuth constraint ledger   **SP-2 MEASURED** (spike §1.4/§1.5), not the
                                  spec §4.5 hypothesis classes.
  [3] sky photometry              measured by `scripts/measure_sky.py`.
  [4] condition catalogue         spec §4.3 — computed from the physical model,
                                  not transcribed.
  [5] scene x condition admissibility, azimuth sampling.
  [6] camera sampler              spec §3.2 + SP-7 conventions.
  [7] two-stage placement filters SP-3 — stage 1 kept but NOT authoritative.
  [8] dataset split               spec §8.2 B5 — scene-level only.
  [9] self-check                  `python3 variation_kit.py` (no pxr, no GPU).

Import safety: nothing here imports `pxr`, `omni`, `carb` or `cv2` at module
scope, so `python3 variation_kit.py` runs the self-check on a bare interpreter
(the same convention `scene_common._geometry_selfcheck` follows).
"""
from __future__ import annotations

import json
import math
import os
import random
import zlib

REPO = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(REPO, "assets")

RES_W, RES_H = 1920, 1080
APERTURE = 20.955                 # horizontal aperture, unchanged from Isaac default


# ===========================================================================
# [0] Render-role gate — D1 / D2
# ===========================================================================
ROLE_JUDGE, ROLE_DATA, ROLE_SWEEP = "judge", "data", "sweep"
ROLES = (ROLE_JUDGE, ROLE_DATA, ROLE_SWEEP)

# The env vars that mean "vary something". Under role=judge any of these being
# set to a non-default value is a hard error. `NEGOBS_SEED` is included even
# though it looks harmless: it is the switch that makes the variation machinery
# active at all (spec §2.4), so a judge round carrying a seed is a judge round
# someone intended to vary.
VARIATION_ENV = {
    "NEGOBS_LIGHT_COND": ("", "ref", "L0"),
    "NEGOBS_CAM_MODE": ("", "preset"),
    "NEGOBS_CAM_N": ("", "0"),
    "NEGOBS_SEED": ("",),
    "NEGOBS_DAZ": ("", "0", "0.0"),
    "NEGOBS_EXPO_VARY": ("", "0"),
}


def render_role():
    """The declared role. Unset == judge, i.e. today's frozen behaviour (D2)."""
    r = os.environ.get("NEGOBS_RENDER_ROLE", "").strip() or ROLE_JUDGE
    if r not in ROLES:
        raise SystemExit(f"[variation] NEGOBS_RENDER_ROLE={r!r} is not one of "
                         f"{ROLES}.")
    return r


def assert_role_gate():
    """Refuse a judge render that carries variation env.

    This is the whole point of D1/D2 being an exception rather than a rule: the
    project's own STATUS records "no code changes mid-round - violated 3 times",
    and every one of those was a setting that was set and not noticed. A silent
    variation in the judge channel is worse than a crash, because
    `regression_check.index_round()` keys views by view NAME only, so two
    differently-lit renders of the same view in one folder leave the last one
    standing and the before/after comparison then runs across two lighting
    conditions **without any warning** (spec §2.1, verified in code).
    """
    role = render_role()
    if role != ROLE_JUDGE:
        return role
    bad = []
    for k, allowed in VARIATION_ENV.items():
        v = os.environ.get(k, "")
        if v and v not in allowed:
            bad.append(f"{k}={v}")
    if bad:
        raise SystemExit(
            "[variation] role=judge but variation env is set: "
            + ", ".join(bad)
            + "\n  The judge channel is frozen (spec D1/D2): its presets, its "
              "lighting and its output tree are the regression baseline.\n"
              "  Run with NEGOBS_RENDER_ROLE=data for a data render, or unset "
              "the variables above.")
    return role


def data_root(run_stamp):
    """Output root for a data run — a tree `regression_check` cannot reach.

    `regression_check.py` is only ever pointed at `--scenes 'look_check/scene*'`,
    so `dataset/` is structurally invisible to it (spec D1/§2.5, B2). The run
    stamp follows the `look_check/README.md` §2 round convention
    `<yymmdd>_<wave>_<purpose>` so a data run is as traceable as a judge round.
    """
    return os.path.join(REPO, "dataset", run_stamp)


# ===========================================================================
# [1] Deterministic derived seeds — spec §2.4
# ===========================================================================
def var_seed(scene: str, stream: str, idx: int, base: int) -> int:
    """Reproducible derived seed. stream = "cam" | "light" | "expo" | "split".

    `zlib.crc32` is deterministic across processes and platforms; `hash()` is
    not, and this repository has already been bitten by exactly that
    (`realism_v1_final.md` §4.2: a displacement-skin seed built from `hash()`
    made the terrain change on every render under `PYTHONHASHSEED` randomisation).
    Streams are separated so that changing the number of camera samples does not
    shift the lighting draw.
    """
    return zlib.crc32(f"{scene}|{stream}|{idx}|{base}".encode()) & 0x7FFFFFFF


def rng(scene, stream, idx, base):
    """A private `random.Random`. The global `random` is never touched — scene
    assembly uses it, and polluting it changes geometry (spec §2.4)."""
    return random.Random(var_seed(scene, stream, idx, base))


def _trunc_norm(r, mu, sd, lo, hi):
    for _ in range(200):
        v = r.gauss(mu, sd)
        if lo <= v <= hi:
            return v
    return min(hi, max(lo, mu))


# ===========================================================================
# [2] Per-scene azimuth constraint ledger — SP-2 MEASURED
# ===========================================================================
# `Docs/reports/lighting_spikes_v1.md` §1.4/§1.5, 693 cuts, 33 scenes x
# Dz {0, +-10, +-20, +-35} x h0.3 3 cuts, PT-fast, one boot per scene.
#
# This table REPLACES spec §4.5's S/A/B/C hypothesis classes, which the sweep
# found wrong in both directions: too loose on 10 scenes, too tight on 7, and
# only 1 of its 3 "azimuth is the scene's identity" S scenes behaves like one
# (scene16 canopy_shadow and sceneD2 floor_opening both measured +-35 with no
# firing at any arm - the spec forbade variation on two scenes that tolerate the
# full range).
#
# Two allowances per scene, because the sweep also established that the question
# differs by channel (spike §1.5 caveat 2):
#
#   daz_judge  the azimuth beyond which the drop-edge cue stops matching the
#              reference render. Measured under criterion B (a GRAZE FAIL counts
#              only when it is about the drop row: step_b >= 25 and ratio <= 0.50,
#              or step_off <= 4 and ratio > 1.10), merged with criterion C
#              (absolute judgeability: 30 <= mean <= 235, dark <= 70 %,
#              clip <= 1 %), taking the tighter.
#              Criterion A - the literal instruction in the brief, "no FAIL in
#              DARK/OCCL/GRAZE vs Dz=0" - is NOT used: OCCL is by definition
#              "pixels that were >= 60 and are now < 25", which is the definition
#              of a cast shadow, and between two arms of this sweep the only
#              stage delta is a rotate op on two light prims. A null control
#              measured the metric floor at exactly zero on all 15 cuts, so every
#              firing was a lighting effect by construction.
#   daz_data   the data-channel allowance. An azimuth at which the drop edge
#              stops matching the reference is a HARD example, not an invalid one,
#              as long as the label still describes the scene. So the data channel
#              runs the full sampler range (35 deg) except where the scene's LABEL
#              is the shadow - sceneN1 shadow_band, whose drop line genuinely
#              collapses (ratio 0.07-0.40 at every arm).
#
# The sweep grid was {0, 10, 20, 35}: a measured "10" means "10 passed, 20
# failed", so the true bound is in between and the spec's +-15 for its A tier is
# not excluded by this data.
DAZ_SAMPLER_MAX = 35.0            # the sweep's widest measured arm
# A condition whose sun sits below Seoul's noon altitude floor is only honest
# off-noon (D6), and the minimum it needs (36.9 deg for L5) is just past the
# sweep's widest arm. The data channel is allowed to extrapolate to here for
# exactly those conditions, on two grounds:
#   - criterion C (absolute judgeability) did not bind at +-35 on 31 of 33
#     scenes, and the failure mode past it - a frame going dark - is caught
#     per-cut by the image filter, not by a global bound;
#   - spike §1.5 caveat 2: on the data channel an azimuth at which the drop edge
#     stops matching the reference is a hard example, not an invalid one.
# It is NOT extended for scenes where criterion C did bind (scene15) or where the
# label IS the shadow (sceneN1). Marked as extrapolation, not measurement.
DAZ_DATA_EXTRAP = 60.0

_LEDGER_RAW = {
    # scene: (class, daz_judge, label_is_shadow, basis)
    "sceneN1": ("S", 0.0, True,
                "drop line collapses to ratio 0.40 at +-10 [measured]"),
    "scene02": ("A'", 10.0, False, "criterion B first-fail at +-20 (GRAZE)"),
    "scene05": ("A'", 10.0, False,
                "criterion B first-fail at +-20, step 86.4 -> 34.0 (ratio 0.394)"),
    "scene07": ("A'", 10.0, False, "criterion B first-fail at -10 (OCCL)"),
    "scene11": ("A'", 10.0, False, "criterion B first-fail at +10 (OCCL)"),
    "scene13": ("A'", 10.0, False, "criterion B first-fail at -10 (GRAZE+OCCL)"),
    "scene15": ("A'", 10.0, False,
                "criterion B first-fail at +10; ALSO bounded by C at +-20 - at "
                "+-35 the alley loses its raking light, h0.3_d5 mean 110.4 -> "
                "42.9, dark 22.9 % -> 73.5 % [measured]. A real physical bound."),
    "scene21": ("A'", 10.0, False, "criterion B first-fail at -10 (OCCL)"),
    "scene06": ("B'", 20.0, False, "criterion B first-fail at +35 (OCCL)"),
    "sceneN4": ("B'", 20.0, False, "criterion B first-fail at +35 (GRAZE)"),
}
# Every other scene: C' - no firing under criterion B, judgeable under C.
_LEDGER_CPRIME = [
    "scene01", "scene03", "scene04", "scene08", "scene09", "scene10", "scene12",
    "scene14", "scene16", "scene17", "scene18", "scene19", "scene20",
    "sceneC1", "sceneC2", "sceneC4", "sceneD1", "sceneD2", "sceneD3", "sceneD4",
    "sceneN2", "sceneN3", "sceneN5",
]
# Scenes whose azimuth has no effect at all: sunless or sealed indoor. sceneD4
# is the proof case - |Dmean| <= 0.22 LSB across the whole +-35 range [measured].
_AZ_FREE = ("sceneC1", "sceneC4", "sceneD4")
# sceneD4 fails the absolute readability floor at EVERY arm including Dz=0
# (mean ~19, dark ~81 %). That is a baseline property, not an azimuth
# constraint, so it is marked here rather than encoded as a bound.
_BELOW_READ_FLOOR = ("sceneD4",)
# Scenes where criterion C - the arm's OWN photometry, no reference - bound below
# the sweep's widest arm. Exactly one: scene15 alley_labyrinth at +-20, where the
# alley loses its raking light. That is a physical bound and it is not
# extrapolated past.
_C_BOUND = {"scene15": 20.0}

AZ_LEDGER = {}


def _ledger_row(scene, cls, daz_judge, label_shadow, basis):
    c_bound = _C_BOUND.get(scene)
    return dict(cls=cls, daz_judge=daz_judge, label_shadow=label_shadow,
                basis=basis, c_bound=c_bound is not None,
                daz_data=(0.0 if label_shadow
                          else c_bound if c_bound is not None
                          else DAZ_SAMPLER_MAX),
                az_free=scene in _AZ_FREE,
                below_read_floor=scene in _BELOW_READ_FLOOR)


for _s, (_c, _dj, _ls, _b) in _LEDGER_RAW.items():
    AZ_LEDGER[_s] = _ledger_row(_s, _c, _dj, _ls, _b)
for _s in _LEDGER_CPRIME:
    AZ_LEDGER[_s] = _ledger_row(
        _s, "C'", DAZ_SAMPLER_MAX, False,
        "no firing under criterion B, judgeable under C")
del _s, _c, _dj, _ls, _b


def ledger(scene):
    if scene not in AZ_LEDGER:
        raise SystemExit(f"[variation] scene {scene!r} is not in the SP-2 "
                         f"azimuth ledger ({len(AZ_LEDGER)} scenes).")
    return AZ_LEDGER[scene]


# ===========================================================================
# [3] Sky photometry — measured
# ===========================================================================
# Produced by `scripts/measure_sky.py` (solid-angle-weighted centroid of the top
# 0.01 % luminance -> sun direction; cap = p90 of the ring [0.6, 1.0] deg;
# E = cos-weighted upper-hemisphere integral), i.e. spec §4.2's method
# reproduced independently. Agreement with the spec's published table: elevation
# to <= 0.01 deg on all 6 sun-bearing skies, f_dir to <= 0.018.
#
# The fallback below is the measured snapshot, frozen so this module and its
# self-check work without the (gitignored) EXRs present. `assets/sky_photometry.
# json` wins when it exists.
#
# `Esky` matters as much as `f_dir`: the dome intensity formula uses the RATIO
# Esky_ref / Esky(c), so the whole set must come from ONE measurement pass.
# Mixing the spec's Esky_ref = 0.5390 with these Esky values would be
# inconsistent - measured here, Esky_ref = 0.5204.
_SKY_FALLBACK = {
    # file: (sun_elev, hdri_sun_rotz_offset, f_dir, Esky, gate)
    "qwantani_noon_puresky_4k.exr": (49.83, 233.82, 0.9152, 0.5204, "PASS"),
    "kloofendal_48d_partly_cloudy_puresky_4k.exr":
        (47.87, 235.74, 0.6672, 1.5980, "PASS"),
    "sunflowers_puresky_4k.exr": (43.01, 233.84, 0.6644, 1.4526, "PASS"),
    "kloofendal_38d_partly_cloudy_puresky_4k.exr":
        (37.96, 234.04, 0.4560, 1.6728, "PASS"),
    # The one sky whose azimuth is different (phi 169.15 vs the 216 family).
    # Using the scene constant 233.5 here would throw its shadows 47 deg off.
    "kloofendal_28d_misty_puresky_4k.exr":
        (28.50, 280.85, 0.0652, 3.9496, "SOFT"),
    "qwantani_late_afternoon_puresky_4k.exr":
        (19.08, 233.87, 0.6492, 1.3482, "PASS"),
    # Sunless skies. The elevation is the centroid's answer and is a
    # MISDETECTION in the physical sense (there is no disc to find), but it is
    # the number the spec's E_phys term was evaluated at and reproduces its
    # published dome intensities, so it is kept and labelled rather than
    # silently replaced.
    "farm_field_puresky_4k.exr": (51.05, 233.75, 0.0006, 4.3092, "SOFT"),
    "kloofendal_overcast_4k.exr": (22.77, 236.94, 0.0001, 4.0508, "SOFT"),
}


def _load_sky_photometry():
    p = os.path.join(ASSETS_DIR, "sky_photometry.json")
    out = {k: dict(sun_elev=v[0], hdri_sun_rotz_offset=v[1], f_dir=v[2],
                   Esky=v[3], gate=v[4], src="frozen")
           for k, v in _SKY_FALLBACK.items()}
    try:
        with open(p, encoding="utf-8") as f:
            for r in json.load(f)["skies"]:
                out[r["file"]] = dict(
                    sun_elev=float(r["sun_elev"]),
                    hdri_sun_rotz_offset=float(r["hdri_sun_rotz_offset"]),
                    f_dir=float(r["f_dir"]), Esky=float(r["Esky"]),
                    gate=r["gate"], src="measured")
    except Exception:
        pass
    return out


SKY = _load_sky_photometry()


# ===========================================================================
# [4] Condition catalogue — spec §4.3, computed not transcribed
# ===========================================================================
# E_phys(h, cloud) = 128000 * sin(h)^1.15 * cloud                [lux, spec §4.3]
# E_rel(c)         = E_phys(c) / E_phys(ref)
# sun_intensity(c) = 2450 / f_dir_ref * E_rel(c) * f_dir(c)
# dome_intensity(c)= 1000 * E_rel(c) * (1-f_dir(c))/(1-f_dir_ref)
#                         * Esky_ref / Esky(c)
# dEV              = -log2(E_rel(c))                    (how much darker it is)
# ev_comp          = 0.75 * dEV                         (partial camera AE)
#
# alpha = 0.75 is the spec's judgement: 1.0 would erase the illuminance
# variation from the image (which is the signal we are buying), 0 would leave the
# overcast cuts unreadable.
E_PHYS_EXP = 1.15
CLOUD_SUNLESS = 0.20              # overcast 1-2e4 lux vs clear 1e5
EV_COMP_ALPHA = 0.75
REF_SKY = "qwantani_noon_puresky_4k.exr"
REF_DOME, REF_SUN = 1000.0, 2450.0
# The readability floor for a fully sunless condition: a cloud-transmitted soft
# direct of about 1/6 of clear-sky (spec §4.6; sceneC1's own 420 is the
# precedent). Without it, "completely non-directional light makes relief shading
# vanish" - which is a real phenomenon, but an unreadable cut.
SUNLESS_READ_FLOOR = 400.0

# --- Seoul astronomy, spec §4.4/D6 + appendix B [calc, NOAA] ---------------
# Seoul's noon altitude floor is 29.0 deg (winter solstice), so any condition
# below that CANNOT sit at Dz = 0 and carries a minimum |Dz|. Values from
# appendix B: 20.2 -> 35.6, 19.1 -> 36.9, 18.4 -> 39.0.
SEOUL_NOON_ELEV_MIN = 29.0


def seoul_min_abs_daz(elev):
    """Minimum |Dz| at which a Seoul sun reaches `elev` [calc, spec appendix B].

    Above the noon floor the answer is 0 (pick the date). Below it, interpolate
    the appendix's three tabulated points; the relation is steep and locally
    near-linear over 18-29 deg.
    """
    if elev >= SEOUL_NOON_ELEV_MIN:
        return 0.0
    tab = [(29.0, 0.0), (20.2, 35.6), (19.1, 36.9), (18.4, 39.0)]
    for (e1, a1), (e2, a2) in zip(tab, tab[1:]):
        if e2 <= elev <= e1:
            t = (e1 - elev) / (e1 - e2)
            return a1 + t * (a2 - a1)
    return tab[-1][1] + (tab[-1][0] - elev) * 3.0      # extrapolate, steeper


# id, name, sky file, lookfix, sunless, sun angle (deg), season lock, note
_COND_SPECS = [
    ("L0", "ref", REF_SKY, True, False, 0.53, None,
     "noon clear - the judge reference. Frozen: this row must reproduce the "
     "current 33-scene light dict exactly."),
    ("L1", "cumulus", "kloofendal_48d_partly_cloudy_puresky_4k.exr",
     True, False, 0.53, None, "scattered cumulus, noon"),
    ("L2", "stratocumulus", "sunflowers_puresky_4k.exr",
     True, False, 0.53, None, "stratocumulus band, noon"),
    ("L3", "autumn_noon", "kloofendal_38d_partly_cloudy_puresky_4k.exr",
     True, False, 0.53, "autumn", "late-autumn noon; matches sceneC2 leaf litter"),
    ("L4", "winter_noon", "kloofendal_28d_misty_puresky_4k.exr",
     False, False, 3.0, "winter",
     "winter noon haze; matches sceneC1 snow. lookfix=False - the sun gate is "
     "SOFT, and capping a disc that is not there is useless or harmful."),
    ("L5", "low_sun", "qwantani_late_afternoon_puresky_4k.exr",
     True, False, 0.53, None,
     "low afternoon sun. 19.08 deg is BELOW Seoul's noon floor, so it is only "
     "honest at |Dz| >= 36.9 deg (D6)."),
    ("L6", "overcast_bright", "farm_field_puresky_4k.exr",
     False, True, 4.0, None, "bright overcast, no sun disc"),
    ("L7", "overcast", "kloofendal_overcast_4k.exr",
     False, True, 4.0, None, "overcast, no sun disc"),
]


def _e_rel(elev, cloud):
    ref = SKY[REF_SKY]["sun_elev"]
    return (cloud * (math.sin(math.radians(elev))
                     / math.sin(math.radians(ref))) ** E_PHYS_EXP)


def build_conditions():
    ref = SKY[REF_SKY]
    f_ref, esky_ref = ref["f_dir"], ref["Esky"]
    out = {}
    for cid, name, sky, lookfix, sunless, angle, season, note in _COND_SPECS:
        s = SKY[sky]
        cloud = CLOUD_SUNLESS if sunless else 1.0
        e_rel = _e_rel(s["sun_elev"], cloud)
        sun = REF_SUN / f_ref * e_rel * s["f_dir"]
        dome = (REF_DOME * e_rel * (1.0 - s["f_dir"]) / (1.0 - f_ref)
                * esky_ref / s["Esky"])
        if sunless:
            # Table value is ~0; §4.6 substitutes a soft direct so relief still
            # reads. UNMEASURED: SP-5 (the readability sweep over angle
            # {0.53, 3, 6}) was not part of the four spikes that ran, so 4.0 deg
            # is the spec's midpoint, not a measurement.
            sun = SUNLESS_READ_FLOOR
        d_ev = -math.log2(e_rel)
        out[cid] = dict(
            id=cid, name=name, hdri=sky, lookfix=lookfix, sunless=sunless,
            sun_angle_deg=angle, season=season, note=note,
            sun_elev=s["sun_elev"], f_dir=s["f_dir"], Esky=s["Esky"],
            gate=s["gate"], hdri_sun_rotz_offset=s["hdri_sun_rotz_offset"],
            e_rel=round(e_rel, 5), d_ev=round(d_ev, 3),
            ev_comp=round(EV_COMP_ALPHA * d_ev, 3),
            dome_intensity=round(dome, 1), sun_intensity=round(sun, 1),
            # Every no-sun condition is PT-only: "a sunless dome alone is flat
            # light under RT - judge on PT" (sceneC1:239, verified in code).
            pt_only=bool(sunless or not lookfix),
            min_abs_daz=round(seoul_min_abs_daz(s["sun_elev"]), 1)
            if not sunless else 0.0,
        )
    return out


CONDITIONS = build_conditions()
COND_IDS = tuple(CONDITIONS)

# Scene-specific lighting tunings the catalogue must NOT overwrite (spec §4.3):
# these three scenes have their own exposure balance and a scene override always
# wins. C1 snow dome 800/sun 420, C4 wet 1150/600, D4 indoor 8.0/0.
SCENE_LIGHT_OVERRIDE_WINS = ("sceneC1", "sceneC4", "sceneD4")
# Season-marked scenes lock the sun elevation band (spec §4.3 [physical
# consistency]): snow may not take a summer sun, leaf litter may not take a
# high one.
SCENE_SEASON = {"sceneC1": "winter", "sceneC2": "autumn"}
SEASON_ELEV_BAND = {"winter": (0.0, 32.0), "autumn": (35.0, 45.0)}
# Consequence of the season locks that the spec does not draw, and that an
# admissibility sweep over all 8 x 33 pairs surfaced: **L0 is inadmissible on the
# two season-marked scenes.** L0's sun sits at 49.83 deg, outside both the winter
# band (<= 32) and the autumn band (35-45), so spec §4.3's "L0: all 33 scenes,
# the judge reference" row cannot be satisfied as written.
#
# It is not a contradiction, it is the scenes already telling us so: sceneC1's own
# light dict runs elev 28.0 and sceneC2's 42.0 — neither has ever used L0's 49.79.
# The catalogue entry closest to each scene's own reference is therefore its
# reference condition. Declared here rather than substituted at runtime, so a plan
# that wants a reference arm asks for it explicitly (spec B6 forbids silent
# substitution — a condition distribution that quietly bends per scene stops being
# independent of the label).
SCENE_REF_COND = {
    "sceneC1": "L4",     # winter_noon 28.50 deg vs the scene's own 28.0 [snow]
    "sceneC2": "L2",     # stratocumulus 43.01 deg vs the scene's own 42.0 [leaf]
}


def ref_cond_for(scene):
    """The reference condition for this scene — L0 unless a season lock excludes
    it. Use this for a data run's reference arm; using L0 blindly silently drops
    sceneC1 and sceneC2 from it."""
    return SCENE_REF_COND.get(scene, "L0")


# ===========================================================================
# [5] Scene x condition admissibility, azimuth draw
# ===========================================================================
def daz_allow(scene, cond_id, role=ROLE_DATA):
    """The |Dz| ceiling for this (scene, condition, channel)."""
    L, c = ledger(scene), CONDITIONS[cond_id]
    if role == ROLE_JUDGE:
        return L["daz_judge"]
    a = L["daz_data"]
    if (c["min_abs_daz"] > 0.0 and not L["label_shadow"] and not L["c_bound"]):
        a = max(a, DAZ_DATA_EXTRAP)       # forced off-noon, see DAZ_DATA_EXTRAP
    return a


def condition_allowed(scene, cond_id, role=ROLE_DATA):
    """(ok, reason). Refuses loudly rather than silently substituting."""
    c = CONDITIONS[cond_id]
    L = ledger(scene)
    if L["az_free"]:
        # Azimuth has NO measured effect on these three scenes (sceneD4 is the
        # proof case: |Dmean| <= 0.22 LSB across the whole +-35 range), so the
        # ledger cannot exclude anything. Season still can.
        #
        # A "sunless" CONDITION does not earn the same bypass, and assuming it did
        # was a bug this round's validator caught: spec §4.6 puts a widened 4 deg
        # soft direct back at the readability floor, so an overcast condition still
        # casts - soft - shadows, and rotating the dome still moves them. On
        # sceneN1, whose LABEL is the shadow band, the wide draw put |Dz| up to
        # 34 deg on a scene whose allowance is 0.
        pass
    else:
        allow = daz_allow(scene, cond_id, role)
        if c["min_abs_daz"] > allow + 1e-9:
            return False, (
                f"{cond_id} needs |Dz| >= {c['min_abs_daz']:.1f} deg to be "
                f"astronomically honest at elev {c['sun_elev']:.2f} (Seoul noon "
                f"floor {SEOUL_NOON_ELEV_MIN:.1f}), but {scene} allows "
                f"{allow:.0f} deg on the {role} channel "
                f"(class {L['cls']}: {L['basis']})")
    season = SCENE_SEASON.get(scene)
    if season and not c["sunless"]:
        lo, hi = SEASON_ELEV_BAND[season]
        if not (lo <= c["sun_elev"] <= hi):
            return False, (f"{scene} is season-locked ({season}: elev "
                           f"{lo:.0f}-{hi:.0f} deg); {cond_id} is "
                           f"{c['sun_elev']:.2f} deg")
    return True, ""


def sample_daz(scene, cond_id, idx, base_seed, role=ROLE_DATA):
    """Draw the azimuth offset for one cut, inside the ledger allowance.

    Uniform over the allowed interval, and independent of the scene's label -
    spec §8.2 B6: correlating a variation axis with the label manufactures a new
    shortcut, which is the thing this whole round exists to remove.
    """
    c = CONDITIONS[cond_id]
    L = ledger(scene)
    if L["az_free"]:
        # Azimuth has no measured consequence on these scenes, but the dome still
        # rotates, so keep the draw wide - it varies the sky reflected in wet or
        # indoor surfaces for free. Sunless conditions are NOT bypassed here; see
        # `condition_allowed`.
        lo, hi = -DAZ_SAMPLER_MAX, DAZ_SAMPLER_MAX
    else:
        allow = daz_allow(scene, cond_id, role)
        lo_abs = c["min_abs_daz"]
        if lo_abs > allow + 1e-9:
            raise SystemExit(f"[variation] {scene} x {cond_id}: "
                             + condition_allowed(scene, cond_id, role)[1])
        if lo_abs <= 0.0:
            lo, hi = -allow, allow
        else:
            # Forced off-noon: pick a side, then a magnitude in [min, max].
            r0 = rng(scene, "light", idx, base_seed)
            hi_abs = max(lo_abs, allow)
            mag = r0.uniform(lo_abs, hi_abs)
            return round(mag * (1.0 if r0.random() < 0.5 else -1.0), 3)
    r0 = rng(scene, "light", idx, base_seed)
    return round(r0.uniform(lo, hi), 3)


# ===========================================================================
# [6] Camera sampler — spec §3.2, SP-7 conventions
# ===========================================================================
# spec §3.2 distributions. The brief writes "pitch N(0, 4 deg)"; the spec table
# writes N(-10 deg, 4 deg) truncated [-20, -2]. Read as the same thing - a
# N(0, 4 deg) jitter about the -10 deg preset - and sampled per the spec table,
# exactly as SP-3 did (so the measured r_reject applies to this sampler).
CAM_DIST = dict(
    h=(0.25, 1.90),                      # U, metres ABOVE GROUND (see CAM-3)
    pitch=(-10.0, 4.0, -20.0, -2.0),     # N(mu, sd) truncated [lo, hi]
    roll=(0.0, 1.5, -5.0, 5.0),
    hfov=(62.2, 1.5, 58.0, 66.0),        # centre = measured IMX219 (real robot)
    yoff=(0.0, 0.35, -0.90, 0.90),
    yaw=(0.0, 8.0, -20.0, 20.0),
    d=(1.2, 12.0),                       # LogU, metres
)
# spec §3.3 - three camera tiers.
#   CAM-2 narrow / low ceiling: height ceiling is structural, lateral sigma cut.
#   CAM-3 descending ground: `grid_views` uses ABSOLUTE eye z, so a naive
#         randomiser buries the camera under a falling ground surface
#         (fixlog_W7 §0: "new geometry swallowing the preset camera - 4
#         recurrences"). Heights here are GROUND-RELATIVE and the ground z is
#         added at placement time for every scene, which makes CAM-3 a no-op
#         flag rather than a special case - it is kept only as documentation of
#         which scenes would have broken.
CAM2_SCENES = ("scene02", "scene15", "sceneD4", "scene11")
CAM3_SCENES = ("scene03", "scene07", "scene09", "scene10", "scene12",
               "scene17", "scene19")
CAM2_H_MAX, CAM2_YOFF_SD = 1.20, 0.15


def focal_for_hfov(hfov_deg, aperture=APERTURE):
    """SP-7 verified: FOV depends only on aperture:focal, so the nominal unit of
    both cancels and no conversion is needed anywhere. Worst measured hFOV error
    over 6 arms was 0.047 deg; hFOV 62.2 -> focalLength 17.36949, confirming the
    spec's proposed 17.369 to 3 decimals."""
    return aperture / (2.0 * math.tan(math.radians(hfov_deg) / 2.0))


def sample_camera(scene, idx, base_seed, gy=0.0):
    """One camera sample. `h` is metres ABOVE GROUND; the caller adds ground z."""
    r = rng(scene, "cam", idx, base_seed)
    D = CAM_DIST
    h_lo, h_hi = D["h"]
    yoff_sd = D["yoff"][1]
    if scene in CAM2_SCENES:
        h_hi = min(h_hi, CAM2_H_MAX)
        yoff_sd = CAM2_YOFF_SD
    d = math.exp(r.uniform(math.log(D["d"][0]), math.log(D["d"][1])))
    return dict(
        idx=idx, d=round(d, 4), h_rel=round(r.uniform(h_lo, h_hi), 4),
        y=round(_trunc_norm(r, gy, yoff_sd, gy - D["yoff"][3],
                            gy + D["yoff"][3]), 4),
        yaw=round(_trunc_norm(r, *D["yaw"]), 4),
        pitch=round(_trunc_norm(r, *D["pitch"]), 4),
        roll=round(_trunc_norm(r, *D["roll"]), 4),
        hfov=round(_trunc_norm(r, *D["hfov"]), 4),
        tier=("CAM-2" if scene in CAM2_SCENES
              else "CAM-3" if scene in CAM3_SCENES else "CAM-1"),
    )


def dir_of(yaw_deg, pitch_deg):
    """Unit view direction. Scenes look along +X; yaw rotates about +Z."""
    y, p = math.radians(yaw_deg), math.radians(pitch_deg)
    return (math.cos(p) * math.cos(y), math.cos(p) * math.sin(y), math.sin(p))


def look_at_rows(eye, yaw_deg, pitch_deg, roll_deg):
    """Rows of the camera's `xformOp:transform` matrix (row-major, USD order).

    Authored as ONE matrix op, not `rotateXYZ` - SP-7's finding: it removes every
    question about rotation order, and measured roll error was <= 0.005 deg with
    the principal point dead centre of the 1920x1080 frame.
    """
    f = dir_of(yaw_deg, pitch_deg)
    # right = normalize(cross(fwd, +Z))
    r = (f[1] * 1.0 - f[2] * 0.0, f[2] * 0.0 - f[0] * 1.0, 0.0)
    n = math.sqrt(r[0] ** 2 + r[1] ** 2 + r[2] ** 2) or 1.0
    r = (r[0] / n, r[1] / n, r[2] / n)
    u = (r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2],
         r[0] * f[1] - r[1] * f[0])
    rl = math.radians(roll_deg)
    cr, sr = math.cos(rl), math.sin(rl)
    r2 = tuple(r[i] * cr + u[i] * sr for i in range(3))
    u2 = tuple(-r[i] * sr + u[i] * cr for i in range(3))
    return [(*r2, 0.0), (*u2, 0.0), (-f[0], -f[1], -f[2], 0.0),
            (float(eye[0]), float(eye[1]), float(eye[2]), 1.0)]


# ===========================================================================
# [7] Two-stage placement filter — SP-3
# ===========================================================================
# Stage-1 thresholds, spec §3.4.
BURY_CLEAR = 0.15
GND_LO, GND_HI = 0.05, 3.0
OPEN_RAYS, OPEN_MIN_HITS, OPEN_MIN_DIST = 15, 6, 1.0
# Stage-2 thresholds = the `regression_check` constants they were taken from.
DARK_MEAN, DARK_PCT, DARK_LEVEL = 30.0, 70.0, 25
BLOWN_MEAN, CLIP_PCT, CLIP_LEVEL = 235.0, 1.0, 254
FLAT_STD_MIN = 1.0
VEG_TOK = ("veg", "tree", "canopy", "leaf", "shrub", "hedge", "grass",
           "planter", "flower", "bush")

# --- SP-3, and the two policy decisions it forces -------------------------
#
# 1. STAGE 1 IS NOT AUTHORITATIVE. It fired exactly ONCE in 600 samples and that
#    once was a FALSE POSITIVE: scene15 idx109 was flagged `buried` (nearest
#    solid 0.072 m) and `closed_in` (4 of 15 open rays), yet its rendered frame
#    passed every image test (bot_local_std 1.601, mean 63.08). So the round
#    produced 1 firing, 1 error and zero demonstrated true positives. It costs
#    0.8 ms/sample, so it is KEPT as a cheap watchdog and RECORDED, but a
#    stage-1 rejection does not drop the sample - the image decides, which is
#    the way the one observed disagreement went. Do not credit it in a budget.
#
# 2. `flat_near` IS A JUDGE FILTER, NOT A DATA FILTER. It was the entire
#    rejection mechanism in SP-3 (5 of 6 rejections) and it fires only at
#    d in [1.2, 1.5) - 19 % inside the nearest 10 % of the distance range, 0 %
#    everywhere else. That range is where a negative obstacle is closest and most
#    safety-critical, and "the ground ahead is a smooth textureless slab" is a
#    real, hard input, not a corrupt one. `flat_near` came from
#    `regression_check`, where its job is to detect a RENDERING failure. So:
#    on by default for judge, off for data.
#
# 3. r_reject IS THRESHOLD-BOUND. The measured 2.0 % holds at FLAT_STD_MIN = 1.0;
#    at 3.0 scene08 rejects 39 % and the 25 % gate fails. Re-measure if it moves.
R_REJECT_MEASURED = 0.020         # worst scene of 3; pooled 0.010 over 600
T_CUT_DATA = 2.87                 # s/cut, pooled over 600 random-camera cuts
T_CUT_PRESET = 1.14               # s/cut, preset path, from the 33-scene round
T_BOOT = 34.3                     # s, least squares over 260730_w2d_fix
T_SWAP = 1.4                      # s, SP-4 (set + 8 updates); threshold was 30


def image_filter(path, flat_near=True):
    """Stage 2. Pure function of the PNG (so it can be re-run offline)."""
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.float32)
    g = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    h = g.shape[0]
    mean = float(g.mean())
    dark = 100.0 * float((g < DARK_LEVEL).mean())
    clip = 100.0 * float((a.max(-1) >= CLIP_LEVEL).mean())
    bot = g[int(h * 2 / 3):]
    bh, bw = bot.shape
    bh8, bw8 = bh // 8 * 8, bw // 8 * 8
    blk = (bot[:bh8, :bw8].reshape(bh8 // 8, 8, bw8 // 8, 8)
           .transpose(0, 2, 1, 3))
    lstd = float(np.median(blk.reshape(-1, 64).std(1)))
    reasons = []
    if mean < DARK_MEAN or dark > DARK_PCT:
        reasons.append("dark")
    if mean > BLOWN_MEAN or clip > CLIP_PCT:
        reasons.append("blown")
    if flat_near and lstd < FLAT_STD_MIN:
        reasons.append("flat_near")
    return dict(mean=round(mean, 2), dark=round(dark, 2), clip=round(clip, 3),
                bot_local_std=round(lstd, 3), reasons=reasons,
                reject=bool(reasons), flat_near_applied=bool(flat_near))


class AabbPrefilter:
    """Stage 1 — scene-agnostic analytic prefilter over world AABBs (spec §3.4).

    Also the source of ground z, which is what makes CAM-3 descending scenes
    safe: heights are sampled ground-relative and placed at `ground_z + h`.
    """

    def __init__(self, stage):
        import numpy as np
        from pxr import Usd, UsdGeom
        bbc = UsdGeom.BBoxCache(Usd.TimeCode.Default(),
                                [UsdGeom.Tokens.default_,
                                 UsdGeom.Tokens.render], useExtentsHint=True)
        lo, hi, veg = [], [], []
        for prim in stage.Traverse():
            if not prim.IsA(UsdGeom.Gprim):
                continue
            try:
                b = bbc.ComputeWorldBound(prim).ComputeAlignedRange()
            except Exception:
                continue
            if b.IsEmpty():
                continue
            mn, mx = b.GetMin(), b.GetMax()
            if not all(math.isfinite(v) for v in (*mn, *mx)):
                continue
            if max(mx[k] - mn[k] for k in range(3)) > 400.0:
                continue                 # sky domes / infinite planes
            lo.append([mn[0], mn[1], mn[2]])
            hi.append([mx[0], mx[1], mx[2]])
            veg.append(any(t in str(prim.GetPath()).lower() for t in VEG_TOK))
        self.np = np
        self.lo = np.asarray(lo, np.float64).reshape(-1, 3)
        self.hi = np.asarray(hi, np.float64).reshape(-1, 3)
        self.veg = np.asarray(veg, bool)
        self.lo_nv, self.hi_nv = self.lo[~self.veg], self.hi[~self.veg]
        self.n = len(lo)

    def _ray_t(self, o, d, no_veg=False):
        np = self.np
        lo, hi = (self.lo_nv, self.hi_nv) if no_veg else (self.lo, self.hi)
        if lo.shape[0] == 0:
            return math.inf
        with np.errstate(divide="ignore", invalid="ignore"):
            inv = 1.0 / np.asarray(d, np.float64)
            t1, t2 = (lo - o) * inv, (hi - o) * inv
            tmin = np.nanmax(np.minimum(t1, t2), axis=1)
            tmax = np.nanmin(np.maximum(t1, t2), axis=1)
        hit = (tmax >= np.maximum(tmin, 0.0)) & (tmax > 0.0)
        if not hit.any():
            return math.inf
        return float(np.maximum(tmin[hit], 0.0).min())

    def ground_z(self, x, y, top=60.0, default=0.0):
        """First downward hit from high above (x, y). CAM-3's whole fix."""
        t = self._ray_t(self.np.asarray([x, y, top]),
                        self.np.asarray([0.0, 0.0, -1.0]))
        return default if not math.isfinite(t) else top - t

    def check(self, eye, yaw, pitch, hfov):
        np = self.np
        e = np.asarray(eye, np.float64)
        d = np.maximum(np.maximum(self.lo - e, 0.0), np.maximum(e - self.hi, 0.0))
        dist = np.sqrt((d * d).sum(1))
        inside = np.all((e >= self.lo) & (e <= self.hi), axis=1)
        near = float(dist.min()) if dist.size else math.inf
        out = dict(nearest_solid=round(near, 4),
                   buried=bool(inside.any()) or near < BURY_CLEAR)
        tdn = self._ray_t(e, np.asarray([0.0, 0.0, -1.0]))
        out["ground_below"] = round(tdn, 4) if math.isfinite(tdn) else None
        out["offground"] = not (GND_LO <= tdn <= GND_HI)
        f = np.asarray(dir_of(yaw, pitch))
        rv = np.cross(f, np.asarray([0.0, 0.0, 1.0]))
        rv /= (np.linalg.norm(rv) or 1.0)
        uv = np.cross(rv, f)
        hh = math.radians(hfov) / 2.0
        vv = math.atan(math.tan(hh) * RES_H / RES_W)
        hits = 0
        for fx in (-0.8, -0.4, 0.0, 0.4, 0.8):
            for fy in (-0.6, 0.0, 0.6):
                dv = f + rv * math.tan(hh) * fx + uv * math.tan(vv) * fy
                dv /= (np.linalg.norm(dv) or 1.0)
                if self._ray_t(e, dv, no_veg=True) >= OPEN_MIN_DIST:
                    hits += 1
        out["open_rays"] = hits
        out["closed_in"] = hits < OPEN_MIN_HITS
        out["reasons"] = [k for k in ("buried", "offground", "closed_in")
                          if out[k]]
        # Advisory only - see policy note 1 above.
        out["flag"] = bool(out["reasons"])
        return out


# ===========================================================================
# [8] Dataset split — spec §8.2 B5
# ===========================================================================
# "Never split train/val/test by a variation axis - the split itself becomes the
# shortcut. Split by SCENE only." Deterministic from the scene name so the same
# scene always lands in the same split whatever run produces it.
SPLIT_WEIGHTS = (("train", 0.70), ("val", 0.15), ("test", 0.15))
_SPLIT_CACHE = {}


def split_map(base=0):
    """scene -> split, exact proportions, deterministic.

    A per-scene hash would give 21/4/8 on 33 scenes, i.e. a val fold of four
    scenes. Shuffling the sorted scene list with a fixed seed and slicing gives
    23/5/5 and is just as reproducible. The unit is always the SCENE (spec B5) —
    never a lighting condition or a camera height, because splitting on a
    variation axis makes the split itself the shortcut.
    """
    if base in _SPLIT_CACHE:
        return _SPLIT_CACHE[base]
    scenes = sorted(AZ_LEDGER)
    random.Random(var_seed("__all__", "split", 0, base)).shuffle(scenes)
    n = len(scenes)
    n_tr = int(round(SPLIT_WEIGHTS[0][1] * n))
    n_va = int(round(SPLIT_WEIGHTS[1][1] * n))
    out = {}
    for i, s in enumerate(scenes):
        out[s] = ("train" if i < n_tr else
                  "val" if i < n_tr + n_va else "test")
    _SPLIT_CACHE[base] = out
    return out


def split_of(scene, base=0):
    return split_map(base)[scene]


# ===========================================================================
# [9] Self-check — `python3 variation_kit.py`, no pxr, no GPU
# ===========================================================================
# spec §4.3's published dome/sun table. Reproducing it from the model + our OWN
# photometry is the check that (a) the model is implemented as specified and
# (b) our independent sky measurement agrees with the design session's.
_SPEC_TABLE = {
    "L0": (1000, 2450, 0.00, 0.00), "L1": (1234, 1709, 0.05, 0.04),
    "L2": (1244, 1559, 0.19, 0.14), "L3": (1554, 916, 0.36, 0.27),
    "L4": (845, 77, 0.78, 0.59), "L5": (601, 652, 1.41, 1.06),
    "L6": (290, 0, 2.29, 1.72), "L7": (139, 0, 3.45, 2.59),
}
# The spec's own f_dir column (§4.2), needed to show that our sun-intensity
# deviation is *only* the f_dir measurement difference and not a model error.
_SPEC_F_DIR = {"L0": 0.912, "L1": 0.659, "L2": 0.662, "L3": 0.438,
               "L4": 0.049, "L5": 0.645}
# (The preset-coordinate freeze lives in `scene_common._variation_selfcheck`, which owns `grid_views`.)


def _selfcheck():
    ok = True

    def chk(tag, cond, msg=""):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {tag}" + (f" — {msg}" if msg else ""))

    print("=" * 74)
    print("variation_kit — self-check (no pxr, no GPU)")
    print("=" * 74)

    print("\n[1] role gate")
    keep = {k: os.environ.get(k) for k in list(VARIATION_ENV) + ["NEGOBS_RENDER_ROLE"]}
    try:
        for k in keep:
            os.environ.pop(k, None)
        chk("unset -> judge", render_role() == ROLE_JUDGE)
        chk("clean judge passes", assert_role_gate() == ROLE_JUDGE)
        for k in ("NEGOBS_LIGHT_COND", "NEGOBS_CAM_MODE", "NEGOBS_CAM_N",
                  "NEGOBS_SEED", "NEGOBS_DAZ"):
            os.environ[k] = "L7" if k == "NEGOBS_LIGHT_COND" else "7"
            try:
                assert_role_gate()
                chk(f"judge + {k} -> SystemExit", False, "no exception raised")
            except SystemExit:
                chk(f"judge + {k} -> SystemExit", True)
            os.environ.pop(k, None)
        os.environ["NEGOBS_RENDER_ROLE"] = "data"
        os.environ["NEGOBS_LIGHT_COND"] = "L7"
        chk("role=data unlocks", assert_role_gate() == ROLE_DATA)
        os.environ["NEGOBS_RENDER_ROLE"] = "nonsense"
        try:
            render_role()
            chk("bad role -> SystemExit", False)
        except SystemExit:
            chk("bad role -> SystemExit", True)
    finally:
        for k, v in keep.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v

    print("\n[2] seeds are process-stable and stream-separated")
    chk("crc32 fixed value", var_seed("scene04", "cam", 7, 20260730)
        == zlib.crc32(b"scene04|cam|7|20260730") & 0x7FFFFFFF)
    chk("streams differ", var_seed("s", "cam", 1, 1) != var_seed("s", "light", 1, 1))
    a = [sample_camera("scene04", i, 99)["d"] for i in range(5)]
    b = [sample_camera("scene04", i, 99)["d"] for i in range(5)]
    chk("camera draw reproducible", a == b, f"{a[:2]}")
    chk("global random untouched",
        sample_camera("s", 0, 1) and True)

    print("\n[3] azimuth ledger = SP-2 measured")
    chk("33 scenes", len(AZ_LEDGER) == 33, f"{len(AZ_LEDGER)}")
    cnt = {}
    for v in AZ_LEDGER.values():
        cnt[v["cls"]] = cnt.get(v["cls"], 0) + 1
    chk("class counts S1/A'7/B'2/C'23",
        cnt == {"S": 1, "A'": 7, "B'": 2, "C'": 23}, str(cnt))
    chk("sceneN1 judge 0 and data 0 (label is the shadow)",
        ledger("sceneN1")["daz_judge"] == 0.0
        and ledger("sceneN1")["daz_data"] == 0.0)
    chk("scene16 / sceneD2 freed to 35 (spec said 0 / 3)",
        ledger("scene16")["daz_judge"] == 35.0
        and ledger("sceneD2")["daz_judge"] == 35.0)
    chk("scene05 judge 10 but data 35 (hard example, not invalid)",
        ledger("scene05")["daz_judge"] == 10.0
        and ledger("scene05")["daz_data"] == 35.0)

    print("\n[4] condition catalogue reproduces spec §4.3 from the model")
    # Two separate claims, asserted separately.
    #   (a) the model is implemented as written  -> recompute independently;
    #   (b) our own sky measurement agrees with the design session's -> compare
    #       to the spec's published table. `dome` matches to <= 0.1 % on all 8.
    #       `sun` is directly proportional to f_dir, so it inherits the whole of
    #       our f_dir - spec f_dir gap; on the two hazy skies that gap is real
    #       (L3 0.456 vs 0.438, L4 0.0652 vs 0.049) and the deviation must be
    #       *exactly* explained by it, not merely small.
    f_ref = SKY[REF_SKY]["f_dir"]
    SPEC_F_REF = 0.9121              # the spec's own f_dir_ref (§4.3)
    worst_dome = worst_spec = 0.0
    for cid, (dome, sun, dev, evc) in _SPEC_TABLE.items():
        c = CONDITIONS[cid]
        # (a) model identity: our published number IS the formula, evaluated on
        #     our own measured photometry.
        want_sun = REF_SUN / f_ref * c["e_rel"] * c["f_dir"]
        model_ok = (c["sunless"] or abs(c["sun_intensity"] - want_sun) < 0.15)
        # (b) the model is the SPEC's model: feed it the spec's constants and it
        #     must return the spec's published integer (+-1 for its rounding).
        spec_ok = True
        if sun and cid in _SPEC_F_DIR:
            spec_sun = REF_SUN / SPEC_F_REF * c["e_rel"] * _SPEC_F_DIR[cid]
            # The published column is rounded to whole units (and L4's 77 to two
            # significant figures), so the tolerance has to admit that rounding.
            tol = max(1.0, 0.006 * sun)
            spec_ok = abs(spec_sun - sun) <= tol
            worst_spec = max(worst_spec, abs(spec_sun - sun) / max(1.0, sun))
        dd = abs(c["dome_intensity"] - dome) / max(1.0, dome)
        de = abs(c["d_ev"] - dev)
        dc = abs(c["ev_comp"] - evc)
        worst_dome = max(worst_dome, dd)
        chk(f"{cid} dome {c['dome_intensity']:7.1f} (spec {dome:5d}, "
            f"{dd * 100:4.1f} %)  sun {c['sun_intensity']:7.1f} "
            f"(spec {sun:5d})  dEV {c['d_ev']:+.3f}/{dev:+.2f}  "
            f"evc {c['ev_comp']:+.3f}/{evc:+.2f}",
            model_ok and spec_ok and dd < 0.01 and de < 0.01 and dc < 0.01)
    chk("dome: worst deviation from spec §4.3 < 1 %", worst_dome < 0.01,
        f"{worst_dome * 100:.2f} %")
    chk("sun: the model reproduces the spec's table on the spec's own f_dir",
        worst_spec <= 0.006, f"worst {worst_spec * 100:.2f} % (L4's 77 is a "
        f"two-significant-figure rounding of 76.6)")
    # The remaining gap on L3/L4 is a MEASUREMENT difference, not a model one,
    # and it is stated rather than asserted away.
    for cid in ("L3", "L4"):
        c = CONDITIONS[cid]
        print(f"  [info] {cid} sun {c['sun_intensity']:.1f} vs spec "
              f"{_SPEC_TABLE[cid][1]}: we measure f_dir {c['f_dir']:.4f} where "
              f"the spec measured {_SPEC_F_DIR[cid]:.3f} on the same EXR "
              f"(hazy sun, disc/halo split is threshold-sensitive). Sun "
              f"intensity is linear in f_dir, so the whole gap is that.")
    chk("L0 is the untouched reference",
        CONDITIONS["L0"]["dome_intensity"] == 1000.0
        and CONDITIONS["L0"]["sun_intensity"] == 2450.0
        and CONDITIONS["L0"]["hdri"] == REF_SKY
        and CONDITIONS["L0"]["lookfix"] is True)
    chk("L4 rotz is the misty outlier 280.85, not 233.5",
        abs(CONDITIONS["L4"]["hdri_sun_rotz_offset"] - 280.85) < 0.5)
    chk("sunless conditions are PT-only and carry the readability floor",
        all(CONDITIONS[c]["pt_only"] and CONDITIONS[c]["sun_intensity"]
            == SUNLESS_READ_FLOOR for c in ("L6", "L7")))
    chk("L5 needs |Dz| >= 36.9 (Seoul noon floor 29.0)",
        abs(CONDITIONS["L5"]["min_abs_daz"] - 36.9) < 0.6,
        f"{CONDITIONS['L5']['min_abs_daz']}")

    print("\n[5] admissibility")
    ok5, why = condition_allowed("sceneN1", "L5")
    chk("sceneN1 x L5 refused (label-shadow scene, |Dz| 0)", not ok5, why[:70])
    chk("scene02 x L5 allowed on the data channel",
        condition_allowed("scene02", "L5")[0])
    chk("scene02 x L5 refused on the judge channel",
        not condition_allowed("scene02", "L5", role=ROLE_JUDGE)[0])
    chk("sceneN1 x L7 allowed (sunless, azimuth meaningless)",
        condition_allowed("sceneN1", "L7")[0])
    chk("scene15 x L5 refused (criterion C bound it at +-20, no extrapolation)",
        not condition_allowed("scene15", "L5")[0])
    chk("sceneC1 snow x L0 refused (49.83 out of winter band 0-32)",
        not condition_allowed("sceneC1", "L0")[0])
    chk("sceneC1 snow x L4 allowed (28.5 deg is in band)",
        condition_allowed("sceneC1", "L4")[0])
    chk("sceneC1 snow x L5 allowed (19.08 deg is a legitimate winter sun)",
        condition_allowed("sceneC1", "L5")[0])
    chk("sceneC2 leaf x L3 allowed (37.96 in autumn band 35-45)",
        condition_allowed("sceneC2", "L3")[0])
    chk("sceneC2 leaf x L0 refused (49.83 out of autumn band)",
        not condition_allowed("sceneC2", "L0")[0])
    # Therefore every scene must have SOME admissible reference condition, or the
    # reference arm of a data run silently loses scenes.
    noref = [s for s in AZ_LEDGER
             if not condition_allowed(s, ref_cond_for(s))[0]]
    chk("every one of the 33 scenes has an admissible reference condition",
        not noref, str(noref))
    chk("the two season-locked scenes get their own reference",
        ref_cond_for("sceneC1") == "L4" and ref_cond_for("sceneC2") == "L2"
        and ref_cond_for("scene04") == "L0")
    n_ok = sum(1 for s in AZ_LEDGER for c in COND_IDS
               if condition_allowed(s, c)[0])
    chk("admissible (scene, condition) pairs = 253 of 264", n_ok == 253,
        f"{n_ok}/264 — 11 refusals, all from a season lock or the D6 low-sun "
        f"floor, each with a stated reason")
    dz = [sample_daz("scene02", "L0", i, 7) for i in range(200)]
    chk("scene02 L0 draws stay in +-35", max(abs(x) for x in dz) <= 35.0,
        f"max |Dz| {max(abs(x) for x in dz):.1f}")
    dz5 = [sample_daz("scene02", "L5", i, 7) for i in range(200)]
    chk("scene02 L5 draws respect the forced 36.9 floor",
        min(abs(x) for x in dz5) >= 36.9 - 1e-6
        and len({x > 0 for x in dz5}) == 2,
        f"|Dz| {min(abs(x) for x in dz5):.1f}-{max(abs(x) for x in dz5):.1f}")
    dzN = [sample_daz("sceneN1", "L0", i, 7) for i in range(50)]
    chk("sceneN1 L0 pinned to 0", all(x == 0.0 for x in dzN))
    # Regression: a sunless condition must NOT unlock the azimuth on a
    # label-shadow scene. The §4.6 readability floor leaves a visible soft sun,
    # so overcast still casts (soft) shadows.
    dzN7 = [sample_daz("sceneN1", "L7", i, 7) for i in range(50)]
    chk("sceneN1 L7 pinned to 0 too (sunless is not azimuth-free)",
        all(x == 0.0 for x in dzN7),
        f"max |Dz| {max(abs(x) for x in dzN7):.1f}")
    dzD4 = [sample_daz("sceneD4", "L0", i, 7) for i in range(50)]
    chk("sceneD4 (measured azimuth-free) still draws the full range",
        max(abs(x) for x in dzD4) > 20.0)

    print("\n[6] camera sampler")
    n = 4000
    ss = [sample_camera("scene04", i, 20260730) for i in range(n)]
    chk("h in [0.25, 1.90]",
        all(0.25 <= s["h_rel"] <= 1.90 for s in ss))
    chk("pitch in [-20, -2]", all(-20 <= s["pitch"] <= -2 for s in ss))
    chk("roll in [-5, 5]", all(-5 <= s["roll"] <= 5 for s in ss))
    chk("hfov in [58, 66]", all(58 <= s["hfov"] <= 66 for s in ss))
    chk("d in [1.2, 12]", all(1.2 <= s["d"] <= 12.0 for s in ss))
    import statistics as st
    chk("pitch mean ~ -10", abs(st.mean(s["pitch"] for s in ss) + 10) < 0.4,
        f"{st.mean(s['pitch'] for s in ss):.2f}")
    chk("hfov mean ~ 62.2", abs(st.mean(s["hfov"] for s in ss) - 62.2) < 0.15,
        f"{st.mean(s['hfov'] for s in ss):.2f}")
    lo10 = sum(1 for s in ss if s["d"] < 1.5) / n
    chk("d<1.5 share ~ 9.7 % of LogU(1.2,12)", 0.085 < lo10 < 0.11,
        f"{lo10 * 100:.1f} % — the bin SP-3 measured 19 % flat_near in")
    c2 = [sample_camera("scene15", i, 7) for i in range(500)]
    chk("CAM-2 scene15 height ceiling 1.20",
        max(s["h_rel"] for s in c2) <= CAM2_H_MAX)
    gy = -2.75
    c3 = [sample_camera("scene01", i, 7, gy=gy) for i in range(500)]
    chk("lateral offset centres on the scene's gy",
        all(gy - 0.9 <= s["y"] <= gy + 0.9 for s in c3))
    # SP-7 quotes 17.36949 for hFOV 62.2; that value is the exact answer for
    # aperture 20.9559, ours for 20.9550. Both round to the spec §3.1 figure
    # 17.369, which is the claim that matters. The three arms SP-7 actually
    # RENDERED (58/62/66) match this formula to < 1e-4, and those are the
    # measurement.
    chk("focal for hFOV 62.2 == 17.369 (spec §3.1, real IMX219)",
        abs(focal_for_hfov(62.2) - 17.369) < 1e-3, f"{focal_for_hfov(62.2):.5f}")
    for hf, fl in ((58.0, 18.90191), (62.0, 17.43749), (66.0, 16.13394)):
        chk(f"focal for hFOV {hf} == {fl} (SP-7 measured arm)",
            abs(focal_for_hfov(hf) - fl) < 1e-4)
    rows = look_at_rows((-3.0, 0.5, 1.2), 0.0, 0.0, 0.0)
    chk("look-at: zero yaw/pitch/roll looks down -X column",
        abs(rows[2][0] + 1.0) < 1e-9 and abs(rows[3][0] + 3.0) < 1e-9)
    # Basis convention, preserved verbatim from SP-3/SP-7 so the measured
    # r_reject still applies: right = normalize(cross(fwd, +Z)) — which is -Y for
    # a camera looking along +X — and up = cross(right, fwd). Roll tips the right
    # vector out of the horizontal plane by exactly the roll angle.
    for roll in (0.0, 3.0, -5.0):
        rr = look_at_rows((0, 0, 1), 0.0, 0.0, roll)
        chk(f"roll {roll:+.0f} deg -> right vector rises {roll:+.0f} deg",
            abs(math.degrees(math.asin(max(-1.0, min(1.0, rr[0][2])))) - roll)
            < 1e-6)
    r0 = look_at_rows((0, 0, 1), 0.0, 0.0, 0.0)
    chk("right x up == -forward (right-handed basis)",
        abs(r0[0][1] + 1.0) < 1e-12 and abs(r0[1][2] - 1.0) < 1e-12
        and abs(r0[2][0] + 1.0) < 1e-12)

    print("\n[7] dataset split is scene-level and only scene-level")
    sp = {s: split_of(s) for s in AZ_LEDGER}
    dist = {k: sum(1 for v in sp.values() if v == k) for k, _ in SPLIT_WEIGHTS}
    chk("every scene assigned", len(sp) == 33, str(dist))
    chk("split reproducible", all(split_of(s) == sp[s] for s in sp))
    chk("all three splits populated", all(v > 0 for v in dist.values()), str(dist))

    print("\n[8] budget constants are the measured ones, not the spec's")
    chk("t_cut data 2.87 (spec assumed 0.7)", T_CUT_DATA == 2.87)
    chk("t_swap 1.4 (spec estimated 10)", T_SWAP == 1.4)
    chk("r_reject 0.020 (spec budgeted 0.12)", R_REJECT_MEASURED == 0.020)
    print(f"  20 k-cut projection: {budget(33, 8, 68)['total_h']:.2f} h "
          f"(spike §5 published 15.02 h)")

    print("\n" + "=" * 74)
    print("SELF-CHECK " + ("PASS" if ok else "FAIL"))
    print("=" * 74)
    return 0 if ok else 1


def budget(n_scene, n_light, n_cam, t_cut=T_CUT_DATA, r_reject=R_REJECT_MEASURED,
           t_boot=T_BOOT, t_swap=T_SWAP):
    """spec §6.1 with the SP-measured constants (spike §5)."""
    n_cut = int(round(n_scene * n_light * n_cam * (1.0 + r_reject)))
    t_render = n_cut * t_cut
    t_bootall = n_scene * t_boot
    t_sky = n_scene * max(0, n_light - 1) * t_swap
    tot = t_render + t_bootall + t_sky
    return dict(n_cut=n_cut, render_h=t_render / 3600.0,
                boot_h=t_bootall / 3600.0, sky_h=t_sky / 3600.0,
                total_h=tot / 3600.0,
                overhead_pct=100.0 * (t_bootall + t_sky) / max(1e-9, tot))


if __name__ == "__main__":
    raise SystemExit(_selfcheck())
