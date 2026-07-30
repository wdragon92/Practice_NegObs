#!/usr/bin/env python3
"""Automatic regression checker for render rounds - works from images + manifest.json alone.

It automates the items of the §A regression-prevention checklist in
`Docs/briefs/multi_scene_brief_v3.md` **that can be decided from render output alone**.
No GPU, no Isaac.

Motivation (project lesson, `Docs/audit_v4/fixlog_W7.md` §0):
  "A regression where new geometry swallows a preset camera recurred 4 times
   (scene19 d5 blackout, scene17 fill burial, scene05 planter burial, scene19 skyline
   tangential occlusion).
   Occlusion checks done by eye misdiagnose the occluding object itself."
  "Gate framing checks on **pixel occupancy**, not on the anchor **count**"
   (`Docs/audit_v4/judge_v8_rt.md` §376)

The 6 checks
  [DARK]  black frame        - mean luminance and dark ratio (the main symptom of a
                               camera swallowed by geometry)
  [BLOWN] overexposure, 255 clipping
  [WHITE] large pure-white area - the v5.1 §4 ban (the absolute value is a reference,
                               the increase decides)
  [OCCL]  camera occlusion regression - **new dark pixels** versus the previous round
                               and their largest connected blob
  [FRAME] abrupt frame occupancy change - 16x9 block occupancy shift after global tone
                               normalisation
  [GRAZE] suspected grazing concealment - horizontal coherence change in the **drop edge
                               projection band** (metric v2)

**EXPECTED_FP** (D14, 2026-07-31). `ground_kit.EXPECTED_FP` is the GT-E2-x registry whose whole
job is to tell an adjudicator *"the transverse line at these rows is a mandated statutory tactile
band, not the drop edge"*. Until now this checker never read it, so every registered band
manufactured the same GRAZE finding on every new baseline (3+ live instances - `w3_k1t4_v1.md`,
`w3_cb7_v1.md`, `w2d_round_v1.md` §3.2). The `expected_fp_*` block below (registry source:
`ground_kit.py` §7) is the **minimal reader**: it suppresses a loud finding **only** on an exact
`(scene, cut, row-band)` register match and re-reports it as the verdict `EXPECTED_FP` - never as
a silent `PASS`, because a registered row is a *waived* finding, not an absent one.
`--no-expected-fp` restores the raw pre-D14 behaviour, byte for byte.
Basis and the no-collateral proof: `Docs/reports/w3_mc_d14_v1.md`.

Usage
  # single scene A/B
  python scripts/regression_check.py --before look_check/scene07/p2g2_off                                      --after  look_check/scene07/p2g2_on

  # all 33 scenes (round names fall back through commas - the first existing one is used)
  python scripts/regression_check.py --scenes 'look_check/scene*'       --before-round w2c_g2,w2_pilot,r2b_on,wall,facade,r2_on --after-round <new round>       --fail-only --json Docs/reports/regr_<new round>.json

  # when rounds differ per scene, use a list file (scene path TAB before TAB after, # comments)
  python scripts/regression_check.py --list rounds.tsv

**Baseline doctrine** (`graze_recalibration_v1.md` §9 · `look_check/README.md` §4).
  The chain this docstring used to print - `final_pt_r2,final_pt,ctx2_pt,ctx2` - is dead:
  `final_pt` and `final_pt_r2` were deleted by the 07-30 look_check cleanup, so it
  resolved to `ctx2_pt,ctx2` for batch1 and to **nothing at all** for the main scenes,
  i.e. it silently compared the new round against no baseline.
  The standing baseline is **`r2_on`**, and the chain above is `r2_on` preceded by the
  scenes that have since been re-judged, newest first - so each scene resolves to **its
  own latest judged round**: `sceneC2 -> w2c_g2` · `scene13/15/N5 -> w2_pilot` ·
  `sceneC1 -> r2b_on` · `sceneN4 -> wall` · `scene05 -> facade` · everything else
  `-> r2_on`. Extend the head of the chain when a round is judged, never the tail.

Dependencies: numpy + PIL only (scipy and opencv are banned - deployment environment
assumption).
Related tool: `scripts/imgstats.py` (low-level realism statistics). This tool is for
**regression** only.

Metric versions
  Only GRAZE is v2 (recalibrated 2026-07-29). The other 6 are unchanged v1.
  Basis and before/after comparison: `Docs/reports/graze_recalibration_v1.md`
"""
import argparse
import glob
import json
import math
import os
import re
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from PIL import Image

# ===========================================================================
# Thresholds - all collected here. The basis of each value is left as a comment.
#
# The bases come from three sources.
#   (a) Measured bands from the supervisor verdicts - `Docs/audit_v4/judge_v7_rt_A.md`
#       and `judge_v8_rt.md` photometered all 9 preset shots as "mean / dark<25 / 255
#       clipping". This tool uses **the same definitions** (compatible).
#   (b) Control measurements - 4 look-layer A/B pairs (scene07/sceneD3 p2g1/p2g2 off<->on,
#       56 shots total) + a small-fix round (sceneD3 r2->r3) + a render mode swap
#       (scene07 v8_rt->v8_pt). The noise ceiling of **pairs that should show no regression**.
#   (c) Real regression measurements - scene07 v6->v7 and v7->v8 (the shots the verdicts
#       actually flagged as occlusion or blackout).
# Thresholds sit between the ceiling of (b) and the floor of (c).
# ===========================================================================

# --- [DARK] absolute blackout ----------------------------------------------
# judge_v7_rt_A §128: mean 26.3, dark 81.3 % was judged "effectively unjudgeable".
# judge_v8_rt §78 : passing grids run mean 127-185, dark 1.8-10.4 %.
# judge_v8_rt §240: mean 49.4, dark 53.4 % was left as a residual "still the darkest part of the scene".
DARK_MEAN_FAIL = 30.0
DARK_MEAN_WARN = 55.0
DARK_PCT_FAIL = 70.0
DARK_PCT_WARN = 45.0
DARK_LEVEL = 25          # Dark definition - identical to the supervisor photometry (0-255 luminance < 25)

# --- [BLOWN] overexposure ---------------------------------------------------
# Measured over all 412 final-round shots of the 33 passing scenes (this tool): mean p95 = 188, max = 238.3
# (scene14 h0.3_d10 - a genuinely blown white frame). 255 clipping peaks at 0.35 %,
# i.e. effectively absent, so a low clipping threshold produces no over-detection.
BLOWN_MEAN_FAIL = 235.0
BLOWN_MEAN_WARN = 210.0
CLIP_PCT_FAIL = 1.0
CLIP_PCT_WARN = 0.2
CLIP_LEVEL = 254         # Channel maximum >= 254 counts as 255 clipping

# --- [WHITE] large pure-white area (v5.1 §4 "no large pure-white (>0.8) areas") ---
# A pixel value > 0.8 is **not the same as albedo > 0.8** (under noon sun plus ACES tone
# mapping even albedo-0.5 concrete passes it easily). 12 of the 33 passing scenes trip the absolute value.
# -> The absolute value is a reference (WARN) only, and **the verdict comes from the increase over the previous round**.
WHITE_LEVEL = 204        # = 0.8 x 255, on the channel minimum (= achromatic pure white)
WHITE_PCT_WARN = 60.0    # Measured over the lower 2/3. Median across 33 scenes 0.97 %, p95 88.6 % (bimodal)
WHITE_DELTA_FAIL = 25.0  # Increase in pp. Maximum control A/B increase +2.4 pp
WHITE_DELTA_WARN = 10.0

# --- [OCCL] camera occlusion regression -------------------------------------
# newdark = fraction of pixels with (previous luminance >= 60) & (new luminance < 25).
#   56 control shots peak at 0.67 % / small fix 0.26 % / mode swap 0.00 %
#   real regressions: 8.2, 14.0, 14.5, 17.3, 23.0, 26.5, 39.3, 47.7 %
OCCL_NEWDARK_FAIL = 8.0
OCCL_NEWDARK_WARN = 2.0
# Largest **connected** new dark blob (large-area verdict). Control max 0.05 %, real regressions 2.3-41.6 %.
OCCL_BLOB_FAIL = 5.0
OCCL_BLOB_WARN = 1.5
OCCL_BRIGHT_BEFORE = 60  # Floor for "it used to be bright"
NEAR_BAND = 0.60         # Lower 40 % of the frame = the near band (where geometry that swallows the camera sits)

# --- [FRAME] abrupt frame occupancy change ---------------------------------
# Global tone (brightness, contrast, sky swap, RT<->PT) is removed by percentile matching,
# then 16x9 block means are compared. Without tone normalisation **an intended look change alone alarms every shot**
# (measured: scene07 v8_rt->v8_pt has 55 % changed pixels before normalisation, 0 % block shift after).
#   control A/B  : blk_shift 0.0-25.0 % (the maximum is scene07 side_slope - the look layer
#                 really did change the slope there, so a WARN is correct)
#   small fix    : 0.0-4.2 %
#   mode swap    : 0.0 %
#   real regress.: 36.8 - 97.9 %
FRAME_SHIFT_FAIL = 40.0
FRAME_SHIFT_WARN = 20.0
FRAME_BLOCK_DELTA = 10.0   # A block mean off by this much (0-255) counts as a "shifted block"
# Maximum block deviation. Look-layer A/B control max 32.7, real regressions 78.8-207.
# The batch-1 ctx rounds land harmlessly in the 46-64 band, so WARN is set at 55
# (1.7x the control, below the real-regression floor of 78.8).
FRAME_MAXBLK_FAIL = 100.0
FRAME_MAXBLK_WARN = 55.0
BLOCKS_Y, BLOCKS_X = 9, 16

# --- [PHOTO] abrupt luminance distribution change (change in absolute mean/dark) ---
#   control |dmean| <= 7.0, ddark <= +0.0 pp
#   mode swap |dmean| <= 8.8
#   real regressions dmean -25.0 / ddark +15.8, +11.8 pp
# Only the darkening direction counts as FAIL (getting brighter is usually an improvement, not a regression).
PHOTO_DMEAN_FAIL = -45.0
PHOTO_DMEAN_WARN = -20.0
PHOTO_DMEAN_UP_WARN = 25.0     # Brightening - abrupt, so it is reported but not escalated to FAIL
PHOTO_DDARK_FAIL = 25.0
PHOTO_DDARK_WARN = 12.0

# ===========================================================================
# --- [GRAZE] suspected grazing concealment - metric **v2** (recalibrated 2026-07-29) ---
# ===========================================================================
# Full basis: `Docs/reports/graze_recalibration_v1.md`
#
# * Why v1 was wrong (a geometric error, [geometry])
#   v1 measured the **macro-structure total** of "ground band = lower 55 % of the frame". But
#   the image row of a ground point is fixed by the camera geometry -
#       row(X) = H/2 · (1 − tan(−atan(h/X) − pitch) / tan(vFOV/2))
#   plugging in h0.3, pitch -10 deg, vFOV 36 deg (1920x1080, hFOV 60 deg) gives
#       X = 1 m → 0.68H · 2 m → 0.46H · 5 m → 0.32H · 10 m → 0.28H · ∞ → 0.23H
#   i.e. **the only ground entering the lower 55 % (row >= 0.45H) is X <~ 2.05 m**.
#   But by definition the drop edge of the preset `preset_h{h}_d{d}` is at a horizontal
#   distance of **exactly d** from the camera (`scene_common.grid_views` plus the per-scene
#   datum shift, e.g. scene05 "so that d means the distance to the lip" §build_views). Hence
#     - the d5 and d10 edges were **outside** the v1 band (0.32H, 0.28H), and
#     - what v1 actually measured was the **near clutter zone** (X < 2 m).
#   ground_kit near-field filling fills exactly that zone -> a structural false-positive flood was guaranteed.
#
# * Measured support
#   - False positive: on sceneC2 `balust`->`leaf3d` (3D leaf scatter = near-field filling itself)
#           v1 returned a `h0.3_d5` GRAZE **FAIL** (vgrad x1.46, erow +0.50). By eye the
#           edge band is unchanged and the entire change is in the near field.
#   - Detection power: of 844 shots with drop exposure injected via physical parameters
#           (exposed riser height, surface contrast), v1 detected **7.2 %**. v2 detects 70.5 % (78.5 % for risers <=0.4 m).
#   - Consistency with the verdict history: v6->v7 and v7->v8 are rounds the verdicts fixed as "0 concealment (grazing) regressions"
#           (`judge_v8_rt.md` §46, `judge_v7_rt_B.md`), yet
#           v1 returned 11 FAIL and 7 WARN out of 92 shots. v2 returns 1 FAIL and 3 WARN.
#
# * What v2 measures - the **horizontal coherence change** in the edge projection band
#   E band (edge) = projected rows of ground distance [0.7*d, 2.2*d] +- an FOV error margin
#   G band (guard) = the rows a 0.5 m exposed riser would fill (excluded from measurement)
#   N band (near) = everything below = the clutter control
#   Signal = the **column mean** of the vertical step field (after tone normalisation). Isotropic clutter
#   (leaves, gravel, props) cancels in the column mean and only lines crossing the screen (= drop edges) survive.
#   The decision value spec = max|delta|_E - max|delta|_N -> "is the change **local** to the edge band?".
#
# * v2.1 (2026-07-29) - **two secondary discriminators added**. Bands, signal and thresholds stay as in v2.
#   Basis: `w2_gate_preflight.md` §3.4 (visual inspection of the 2 residual T3 WARN crops) +
#         `graze_recalibration_v1.md` §11-2 (separating the gate by direction).
#   What T3 established: the 2 residual v2 firings were **not concealment regressions but albedo swaps
#   of the ground on both sides of the edge**. `dcoh` is the **absolute change** of the step field and cannot tell them apart.
#   What was missing is a secondary test asking "did that change alter the concealment?", and v2.1 is that test.
#
#   (a) **Edge persistence gate** - measure the absolute vertical step of **before and after separately**
#       at the drop row +-GRAZE_SLACK, and if **both** are at least GRAZE_STEP_MIN, demote the firing to
#       quiet (a material change) even when spec is exceeded. On a real burial the after step collapses (the line vanishes),
#       so detection power is retained. T3 measurements: scene13 115.9->67.8, scene07 109.6->86.4 (single row at native resolution).
#   (b) **Direction separation** - the exposure direction (a line appears) is gated as in v2 by the **column agreement of the change**,
#       while the burial direction (a line weakens) is gated by the **step ratio** `step_after / step_before`.
#       Physically a burial is "a line that existed disappears", so this matches the definition (§11-2).
#       Albedo swaps in the realism rounds cluster in the 0.5-0.9 ratio band while a real burial approaches 0
#       (T3 measurements 0.585, 0.788). Also, **if there was no line in the previous round** (step_before below the floor)
#       the word burial does not even apply, so it is demoted to quiet.
#   (c) `GRAZE_SLACK` **stays at 2**. The "2->3" proposal of T3 §3.4-3 was not adopted -
#       (a) already quiets scene07, so there is no reason to touch the slack, and changing it
#       would require recomputing the whole injection test (a condition T3 set for itself).
GRAZE_VER = "v2.1"
GRAZE_HFOV = 60.0          # [code] Horizontal field of view of the 1920x1080 viewport. Multiple bases:
#   `scenes/main/facade_kit.py` §231 "pitch −10° · vFOV 36°"
#   `scenes/main/scene19_fan_winder.py` `_cam_basis(hfov=60, aspect=16/9)`
#   `sceneC2/C1` "[camera check] FOV assumed horizontal +-30 deg / vertical +-18 deg"
#   The original source is `fixlog_W4.md` §155 and `fixlog_W5.md` §66 (back-computed from the v6 render).
#   W5 also left a different back-computation of 32.6 deg / 19.8 deg half-angles -> a vertical scale
#   error of up to 11 % -> absorbed by GRAZE_FOV_TOL below.
GRAZE_KN = 0.7             # E band near end = 0.7*d  (30 % in front of the edge)
GRAZE_KF = 2.2             # E band far end = 2.2*d  (just before the background begins beyond the edge)
GRAZE_FOV_TOL = 0.13       # Field-of-view uncertainty margin (13 % of the offset from the frame centre)
GRAZE_GUARD_DZ = 0.5       # Guard band = the exposure of a 0.5 m riser. This much is subtracted from N
#   (without it a large exposure bleeds into N and spec cancels itself - measured:
#    detection rate for a 0.4 m riser is 55 % with no guard, the same with a 0.5 m guard, and 24 % with 0.8 m.
#    Exposures of the 0.8 m class fall under PHOTO/OCCL anyway, so the guard is not enlarged further.)
# Decision thresholds - measured over 157 control shots (mode swap, look A/B, context ctx, realism r2, P4 near field)
#   spec p50 0.0-1.3, p90 0.2-9.8, max 24.8.  At thresholds 8/20 the control yields 1 WARN.
GRAZE_SPEC_WARN = 8.0
GRAZE_SPEC_FAIL = 20.0
GRAZE_AGREE_MIN = 0.70     # **Column sign agreement** of the change. 0.5 = random (isotropic clutter),
#   1.0 = a line across the full width. Measured: leaf scatter 0.5-0.6 / injected drop line 0.9-1.0
GRAZE_BAND_MU_MIN = 35.0   # Absolute luminance floor of the E band. Darker than this and the verdict is withheld
#   (scene06 spiral interior mean 2.7, sceneD4 tunnel 12.9 - tone normalisation amplifies the noise)
GRAZE_PHOTO_DMEAN = 20.0   # If the frame photometry moves this much, the GRAZE verdict is withheld
GRAZE_PHOTO_DDARK = 12.0   #   (= the PHOTO WARN threshold. Fix the lighting regression first)
GRAZE_HW = 3               # Half-width of the step matching filter (rows)
GRAZE_SMOOTH = 3           # Profile moving average (rows)
GRAZE_SLACK = 2            # Row misalignment tolerance - an existing edge shifted by 1-2 rows is not a change
GRAZE_EDGE_GUARD = 6       # Truncated section at the top and bottom of the frame (where the filter is cut off)
GRAZE_LONG = 960           # GRAZE-only working resolution (at 384 the d10 band is only 13 rows)
# --- v2.1 secondary discriminator constants --------------------------------
GRAZE_STEP_MIN = 25.0      # [v2.1a] The vertical step (levels) accepted as "there is a line on that row".
#   It is measured at the maximum-change row +-GRAZE_SLACK, on the **column-mean step profile**
#   (smoothed the same way as graze_delta). The threshold of 25 is the W2 directive and sits far below
#   the T3 measurements (before 115.9/109.6, after 67.8/86.4, single row at native resolution), so
#   "the line persists" is granted generously. A real burial (line gone) has after near 0 and is unaffected.
GRAZE_BURY_RATIO = 0.50    # [v2.1b] Upper bound for firing in the burial direction = step_after / step_before.
#   T3 measurements 0.585 (scene13) and 0.788 (scene07) = the albedo swap band. A burial is near 0.
#   0.5 lies between the two groups and follows the "0.5-0.9 band vs 0" separation line proposed in T3 §3.4-2.
# --- Two v2.1 detection-power protection guards (**extra conditions** absent from the T3 proposal) ---
# T3 §3.4-1 wrote that "on a real burial the after step collapses, so detection power is retained", but
# that argument holds **only for the burial direction** and was not validated against the §6 injection
# test (the exposure direction). Applying the persistence gate unconditionally does in fact collapse
# injection detection from **70.4 % to 46.8 %** `[measured - w2_tools_v1.md §4.5]`. The cause is that the §6
# injection model darkens the area **below** the drop row, so the step at the drop row actually **shrinks**, and that
# is indistinguishable from an albedo swap. The two guards below strip that overlap away (reproduced: detection stays at 65.8 %).
GRAZE_PERSIST_ROWTOL = 4   # The maximum-change row must be within this many rows of the drop row to count as "a change of that line".
#   The 2 T3 cases measured 3.3 and 3.7 rows (on the 960 px reduction). Anything beyond that is **a different object** in the E band,
#   so there is no basis for applying the persistence gate (scene17 74.7, scene18 36.7, scene19 30.3 -> firing retained).
GRAZE_PERSIST_DOM = 3.5    # The persisting line must dominate the change by this much to read as an "albedo swap".
#   step_after / dE - T3 measurements 3.97 (scene13) and 6.41 (scene07). A newly exposed riser has
#   a change magnitude of the same order as the line contrast, so this ratio is small.

# --- Carried-over defect handling ------------------------------------------
# An absolute defect (DARK/BLOWN) that already existed in the previous round is not a regression. The
# grade is kept only when it got worse by at least this much. The value is about 1.5x the control A/B noise
# (|dmean| <= 7.0, ddark <= 0.0 pp).
CARRY_DMEAN = 10.0
CARRY_DDARK = 10.0

# --- [UNCHANGED] no-change detection ---------------------------------------
# Upper bound of PT sample noise. Measured in realism_phase1 §3.2: the mean difference between PT legacy and fast
# is 0.6-0.7/255. The maximum difference spikes on a single noisy pixel (measured max 89 LSB on an unchanged shot),
# so the test uses the **mean difference + the fraction of significantly changed pixels**, not the maximum.
#   unchanged measurements : mean difference 0.017-0.235, above 4 LSB 0.000-0.012 %
#   look-layer change      : mean difference 15.3     , above 4 LSB 55.3 %
IDENTICAL_MEAN = 0.5     # Mean absolute difference (0-255)
IDENTICAL_FRAC = 0.1     # Fraction of pixels above 4 LSB (%)

# --- Processing resolutions -------------------------------------------------
SMALL_LONG = 384     # Reduction for structural comparison (BOX = area mean -> preserves the mean)
BLOB_LONG = 192      # For connected components (only large areas matter, so it can be coarser)

SEV = {"PASS": 0, "INFO": 1, "WARN": 2, "FAIL": 3}
SEV_NAME = ["PASS", "INFO", "WARN", "FAIL"]

# ===========================================================================
# --- [EXPECTED_FP] the GT-E2-x pre-registration reader (D14) ----------------
# ===========================================================================
# `ground_kit.EXPECTED_FP` maps (scene, cut) -> the row band a **statutory tactile band**
# occupies in that cut, on both axes:
#     rows       (lo, hi) @ scale       = 1080, the spec §12.3 notation
#     rows_work  (lo, hi) @ scale_work  =  540, the axis THIS checker works on (GRAZE_LONG 960
#                                         on a 16:9 frame -> 540 rows), already widened by the
#                                         step-response footprint (GRAZE_FOOTPRINT_WORK = 8)
# The rows are **computed from the statutory geometry**, never hard-coded, so the registry stays
# correct when stair width or origin differ per scene. This reader only consumes it.
#
# **Deliberately minimal — three rules, and nothing else.**
#  (1) It fires **only** on an exact `(scene, cut)` key plus `rows_work[0] <= row <= rows_work[1]`.
#      No fuzzy band, no per-scene tolerance, no "close enough". A registered scene whose finding
#      sits outside its registered rows stays loud - that is a *different* line and must be judged.
#  (2) It **never produces PASS.** A suppressed finding keeps its full original text and is
#      re-reported at verdict `EXPECTED_FP`, so the round record still shows that the tool saw a
#      line there and why it was waived. Auditability is the point; silence would be worse than
#      the false positive it replaces.
#  (3) It refuses to guess across axes. If the register's `scale_work` and this run's actual
#      GRAZE working height disagree, **no match is attempted** and the finding stays loud with a
#      diagnostic - a row number compared across two different row axes is meaningless
#      (`ground_kit` §7 v1.2 exists because that exact mistake was once shipped).
#
# Only findings that carry a **row anchor** can be matched, because the registry's unit is a row
# band. Today that is GRAZE alone: OCCL/FRAME/PHOTO are frame-global statistics with no row
# coordinate in their metrics, so the registry can never match them and this table is the honest
# statement of that. Add a code here the day it grows a row anchor.
FP_ROW_METRIC = {"GRAZE": "gz_row"}

_FP_CACHE = None          # None = not loaded yet · dict = loaded (possibly empty)
_FP_SOURCE = ""


def expected_fp_register():
    """`ground_kit.EXPECTED_FP` as `{(scene, cut): entry}`, loaded once per process.

    `ground_kit` sits at the repository root, imports numpy only and prints nothing at import
    (measured 22 ms), so this stays true to the tool's "no GPU, no Isaac" contract. If the import
    fails the reader degrades to **off** with a warning on stderr - a checker that cannot read the
    registry must keep reporting the findings, never assume them waived.
    """
    global _FP_CACHE, _FP_SOURCE
    if _FP_CACHE is not None:
        return _FP_CACHE
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if repo not in sys.path:
        sys.path.insert(0, repo)
    try:
        import ground_kit
        _FP_CACHE = dict(ground_kit.EXPECTED_FP)
        _FP_SOURCE = os.path.abspath(ground_kit.__file__)
    except Exception as e:
        print(f"[경고] EXPECTED_FP 등록부를 못 읽었다 ({e}) — GT-E2-x 사전등재 판독을 "
              f"끄고 계속한다(모든 소견을 그대로 보고).", file=sys.stderr)
        _FP_CACHE, _FP_SOURCE = {}, ""
    return _FP_CACHE


def expected_fp_match(scene, view, row, work_h):
    """The register entry for this exact (scene, cut, row), or `None`.

    `row` is the checker's own `gz_row` and `work_h` the row count of the reduction it was
    measured on - both must be present, and `work_h` must equal the register's `scale_work`.
    """
    if row is None or work_h is None:
        return None
    reg = expected_fp_register().get((scene, view))
    if not reg:
        return None
    rows = reg.get("rows_work")
    if not rows or len(rows) != 2:
        return None
    if int(reg.get("scale_work") or 0) != int(work_h):
        return dict(_axis_mismatch=True, scale_work=reg.get("scale_work"),
                    work_h=work_h, src=reg.get("src", "?"))
    lo, hi = int(rows[0]), int(rows[1])
    if lo <= float(row) <= hi:
        return dict(rows_work=(lo, hi), rows=tuple(reg.get("rows", ())),
                    scale_work=int(reg["scale_work"]), src=reg.get("src", "?"))
    return None


def apply_expected_fp(r):
    """Rewrite every loud finding of `r` that lands on a registered row. Returns the hit list.

    Mutates the issue **in place** so the original severity, code and message survive inside the
    JSON: the record must read "the tool fired here, and here is the registry row that waives it".
    """
    hits = []
    m = r.get("metrics") or {}
    for i in r.get("issues", []):
        if SEV.get(i.get("sev"), 0) < SEV["WARN"]:
            continue
        key = FP_ROW_METRIC.get(i.get("code"))
        if not key:
            continue
        hit = expected_fp_match(r["scene"], r["view"], m.get(key), m.get("gz_work_h"))
        if hit is None:
            continue
        if hit.get("_axis_mismatch"):
            i["msg"] = (f"{i['msg']}  [EXPECTED_FP 미적용 — 등록부 축 {hit['scale_work']} 행 "
                        f"≠ 이 실행의 작업 축 {hit['work_h']} 행. 행 번호를 축 넘어 비교하지 "
                        f"않는다]")
            continue
        lo, hi = hit["rows_work"]
        hits.append(dict(code=i["code"], sev=i["sev"], row=m.get(key),
                         rows_work=[lo, hi], scale_work=hit["scale_work"],
                         rows_1080=list(hit["rows"]), src=hit["src"]))
        i["fp"] = hits[-1]
        i["was"] = dict(sev=i["sev"], code=i["code"])
        i["sev"] = "INFO"
        i["code"] = "EXPECTED_FP"
        i["msg"] = (f"GT-E2-x 사전등재 오탐 — 최대 변화 y{m.get(key)} 가 "
                    f"`ground_kit.EXPECTED_FP[({r['scene']!r}, {r['view']!r})]` 의 "
                    f"rows_work {lo}~{hi}@{hit['scale_work']} 안에 있다(출처 {hit['src']}). "
                    f"이 행의 횡단선은 **법정 점자블록 대역**이지 낙차 에지가 아니다. "
                    f"원 소견[{hits[-1]['sev']}][{hits[-1]['code']}]은 지우지 않고 보존한다: "
                    f"{i['msg']}")
    return hits


# ===========================================================================
# [1] Basic measurements
# ===========================================================================
def _lum(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def _load(path, graze=False):
    """Build the full-resolution RGB plus 2 reductions (+1 GRAZE-only reduction) in one pass.

    The GRAZE reduction is built for h0.3 shots only - in the 384 px reduction the d10
    edge band is just 13 rows, too few for statistics (34 rows at 960 px).
    """
    im = Image.open(path).convert("RGB")
    w, h = im.size
    full = np.asarray(im).astype(np.float32)

    def rs(n):
        s = n / max(w, h)
        return np.asarray(im.resize((max(1, int(w * s)), max(1, int(h * s))),
                                    Image.BOX)).astype(np.float32)
    return full, rs(SMALL_LONG), rs(BLOB_LONG), (_lum(rs(GRAZE_LONG)) if graze
                                                 else None)


def photometry(full):
    """Absolute photometry with the same definitions as the supervisor verdicts (at full resolution)."""
    g = _lum(full)
    h = g.shape[0]
    return dict(
        mean=float(g.mean()),
        dark=100.0 * float((g < DARK_LEVEL).mean()),
        dark_near=100.0 * float((g[int(h * NEAR_BAND):] < DARK_LEVEL).mean()),
        clip=100.0 * float((full.max(-1) >= CLIP_LEVEL).mean()),
        white=100.0 * float((full.min(-1)[h // 3:] > WHITE_LEVEL).mean()),
        w=int(g.shape[1]), h=int(h),
    )


def tone_match(src, ref):
    """Percentile-match src to the luminance distribution of ref - removes global tone changes.

    This is the core premise of the tool. A look-layer round **changes brightness,
    saturation and sky across every scene at once.** Comparing pixels without
    normalisation turns every intended change into an alarm and makes the tool useless
    (measured: 55 % changed pixels before normalisation -> 0 % block shift after,
    scene07 v8_rt->v8_pt).
    """
    qs = np.linspace(0.0, 100.0, 33)
    xs = np.percentile(src, qs)
    ys = np.percentile(ref, qs)
    xs = np.maximum.accumulate(xs) + np.arange(33) * 1e-6   # Guarantee monotonic increase
    return np.interp(src, xs, ys)


def block_means(l):
    h, w = l.shape
    return np.array([[l[y * h // BLOCKS_Y:(y + 1) * h // BLOCKS_Y,
                        x * w // BLOCKS_X:(x + 1) * w // BLOCKS_X].mean()
                      for x in range(BLOCKS_X)] for y in range(BLOCKS_Y)])


def largest_blob_pct(mask):
    """Screen fraction (%) of the largest 4-neighbour connected component. Scanline union-find, pure Python."""
    if not mask.any():
        return 0.0
    H, W = mask.shape
    parent = [0]
    lab = np.zeros((H, W), np.int32)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    nxt = 1
    m = mask
    for y in range(H):
        row = m[y]
        if not row.any():
            continue
        prev_row = lab[y - 1] if y else None
        cur = lab[y]
        for x in np.flatnonzero(row):
            up = prev_row[x] if y else 0
            left = cur[x - 1] if x else 0
            if up and left:
                cur[x] = min(up, left)
                union(up, left)
            elif up or left:
                cur[x] = up or left
            else:
                parent.append(nxt)
                cur[x] = nxt
                nxt += 1
    flat = lab.ravel()
    nz = flat[flat > 0]
    if nz.size == 0:
        return 0.0
    roots = np.array([find(int(v)) for v in np.unique(nz)])
    remap = dict(zip(np.unique(nz).tolist(), roots.tolist()))
    counts = {}
    for v, c in zip(*np.unique(nz, return_counts=True)):
        r = remap[int(v)]
        counts[r] = counts.get(r, 0) + int(c)
    return 100.0 * max(counts.values()) / mask.size


# ---------------------------------------------------------------------------
# GRAZE v2 - locate the drop edge band from the camera geometry and look only there
# ---------------------------------------------------------------------------
def ground_row(X, h, pitch_deg, H, tanv):
    """Image row of a ground point (horizontal distance X, h below the eye). Rows increase downwards.

    Point elevation = -atan(h/X), optical axis elevation = pitch -> offset above the axis
    a = -atan(h/X) - pitch.
    """
    X = max(float(X), 1e-6)
    a = -math.atan2(h, X) - math.radians(pitch_deg)
    return H / 2.0 * (1.0 - math.tan(a) / tanv)


def graze_geom(view, eye, tgt):
    """(eye height h above the ground, horizontal distance d to the drop edge, pitch in degrees, kind) or None.

    - `preset_h{h}_d{d}` - the name is the geometry. Under the `grid_views` convention the
      eye is (-d, gy, h) and the drop edge is at the origin (x=0), so **the distance to the
      edge = d** and **the eye height above the ground = h**. Even when a scene moves its
      datum (scene05 -1.5, scene19 mirrored) it was moved precisely to keep the meaning
      "distance to the lip = d", so this reading holds.
      The eye z in the manifest is a **world absolute z** and cannot be used here
      (see the §is_graze_view docstring).
    - Other `*graz*` mise-en-scene shots - by author convention **tgt is the hazard
      geometry**. So the ground is the z plane of tgt and the edge distance is the
      eye->tgt horizontal distance.
    """
    m = re.search(r"h([0-9.]+)_d([0-9.]+)", view)
    e = [float(v) for v in eye]
    t = [float(v) for v in tgt]
    horiz = math.hypot(t[0] - e[0], t[1] - e[1])
    if horiz < 1e-6:
        return None
    pitch = math.degrees(math.atan2(t[2] - e[2], horiz))
    if m:
        return dict(h=float(m.group(1)), d=float(m.group(2)), pitch=pitch,
                    kind="preset")
    h = e[2] - t[2]
    if h <= 0.02 or horiz < 0.3:
        return None                      # Horizontal or upward line of sight -> no ground band is captured
    return dict(h=h, d=horiz, pitch=pitch, kind="aimed")


def graze_bands(g, H, W):
    """Row ranges of the edge (E), guard and near (N) bands."""
    tanv = math.tan(math.radians(GRAZE_HFOV / 2.0)) * H / float(W)
    h, d, p = g["h"], g["d"], g["pitch"]
    y_hor = ground_row(1e9, h, p, H, tanv)         # Horizon
    y_haz = ground_row(d, h, p, H, tanv)           # Drop edge
    y_far = ground_row(d * GRAZE_KF, h, p, H, tanv)
    y_near = ground_row(d * GRAZE_KN, h, p, H, tanv)
    pad = GRAZE_FOV_TOL * max(abs(y_far - H / 2.0), abs(y_near - H / 2.0))
    e_top = max(y_hor + 1.0, y_far - pad, float(GRAZE_EDGE_GUARD))
    e_bot = min(H - GRAZE_EDGE_GUARD, max(e_top + 6.0, y_near + pad))
    n_top = min(H - GRAZE_EDGE_GUARD,
                max(e_bot, ground_row(d, h + GRAZE_GUARD_DZ, p, H, tanv)))
    n_bot = H - GRAZE_EDGE_GUARD
    if n_bot - n_top < 20:               # The guard has eaten the whole near band (d2 + a deep drop)
        n_top = max(min(n_top, H * 0.80), e_bot)
    return dict(e_top=e_top, e_bot=e_bot, n_top=n_top, n_bot=n_bot,
                y_haz=y_haz, y_hor=y_hor, tanv=tanv)


def step_field(l):
    """Per-pixel vertical step response = (mean of the GRAZE_HW rows below) - (mean of the GRAZE_HW rows above)."""
    H = l.shape[0]
    c = np.cumsum(np.pad(l, ((1, 0), (0, 0))), axis=0)
    i = np.arange(H)
    a0, a1 = np.clip(i - GRAZE_HW, 0, H), i
    b0, b1 = np.clip(i + 1, 0, H), np.clip(i + 1 + GRAZE_HW, 0, H)
    up = (c[a1] - c[a0]) / np.maximum(1, a1 - a0)[:, None]
    dn = (c[b1] - c[b0]) / np.maximum(1, b1 - b0)[:, None]
    return dn - up


def graze_delta(Da, Db):
    """Per-row (|coherence change|, column sign agreement of the change).

    **The column mean is the key.** Isotropic clutter such as leaves, gravel and props has
    a different sign in every column and cancels in the mean, while only lines crossing
    the screen (drop edges, nosings) survive.
    The row slack exists so that an edge that already existed but shifted by 1-2 rows is
    not counted as a change.
    """
    k = np.ones(GRAZE_SMOOTH) / GRAZE_SMOOTH
    best_c = best_a = None
    for s in range(-GRAZE_SLACK, GRAZE_SLACK + 1):
        dD = Db - np.roll(Da, s, axis=0)
        c = np.convolve(dD.mean(1), k, mode="same")
        a = np.maximum((dD > 0).mean(1), (dD < 0).mean(1))
        if best_c is None:
            best_c, best_a = c, a
        else:
            take = np.abs(c) < np.abs(best_c)
            best_c = np.where(take, c, best_c)
            best_a = np.where(take, a, best_a)
    return np.abs(best_c), best_a


def _band_peak(mag, agr, top, bot):
    n = len(mag)
    a = max(GRAZE_EDGE_GUARD, min(n - 1 - GRAZE_EDGE_GUARD, int(round(top))))
    b = max(a + 1, min(n - GRAZE_EDGE_GUARD, int(round(bot))))
    k = a + int(np.argmax(mag[a:b]))
    return float(mag[k]), k, float(agr[k])


def graze_v2(la, lbn, view, vw):
    """la = before, lbn = tone-normalised new (luminance of the GRAZE_LONG reduction). None when absent."""
    if not vw or "eye" not in vw or "tgt" not in vw:
        return None
    g = graze_geom(view, vw["eye"], vw["tgt"])
    if g is None:
        return None
    H, W = la.shape
    B = graze_bands(g, H, W)
    Da, Db = step_field(la), step_field(lbn)
    mag, agr = graze_delta(Da, Db)
    dE, rE, agE = _band_peak(mag, agr, B["e_top"], B["e_bot"])
    dN = (_band_peak(mag, agr, B["n_top"], B["n_bot"])[0]
          if B["n_bot"] - B["n_top"] > 4 else 0.0)
    a, b = int(B["e_top"]), int(B["e_bot"])
    ca = np.convolve(Da.mean(1), np.ones(GRAZE_SMOOTH) / GRAZE_SMOOTH, mode="same")
    cb = np.convolve(Db.mean(1), np.ones(GRAZE_SMOOTH) / GRAZE_SMOOTH, mode="same")
    # [v2.1] Absolute vertical step of before and after at the **drop row +- slack**, and their ratio.
    # v2 looked only at `dcoh` (the change of the step field) and so had no way to separate "the line
    # persists but the albedo on both sides changed" from "the line is gone" - these two values fill that gap.
    # The measurement position is **the drop row y_haz, not the maximum-change row rE** (T3 §3.4-1, verbatim).
    # Measuring at rE would, for a thick exposure (riser 0.4-0.8 m), push rE to the **lower** edge of the band and
    # read the step of an object unrelated to the drop row, quieting a true positive as a result
    # (measured: on the rE basis, injection detection falls from 66.7 % to 55.9 %).
    y_h = int(round(min(max(B["y_haz"], B["e_top"]), B["e_bot"])))
    s0 = max(0, y_h - GRAZE_SLACK)
    s1 = min(len(ca), y_h + GRAZE_SLACK + 1)
    if s1 <= s0:
        s0, s1 = max(0, y_h), max(1, y_h + 1)
    step_b = float(np.abs(ca[s0:s1]).max())
    step_a = float(np.abs(cb[s0:s1]).max())
    ratio = step_a / step_b if step_b > 1e-6 else float("inf")
    return dict(spec=dE - dN, dE=dE, dN=dN, agree=agE, row=rE,
                step_b=step_b, step_a=step_a, ratio=ratio,
                row_off=abs(rE - y_h),
                dom=(step_a / dE if dE > 1e-6 else float("inf")),
                up=bool(abs(cb[rE]) > abs(ca[rE])),
                band_mu=min(float(la[a:b].mean()), float(lbn[a:b].mean())),
                d=g["d"], h=g["h"], kind=g["kind"],
                e_top=B["e_top"], e_bot=B["e_bot"], y_haz=B["y_haz"])


# ===========================================================================
# [2] View indexing - manifest.json first, otherwise the filename convention
# ===========================================================================
def index_round(d, root):
    """Round folder -> {view: dict(path, mode, ok)}.

    manifest.json is assumed to have the structure written by
    `scene_common.capture_pipeline` (views/shots, shots[i] = file, mode, sky, view, ok).
    The file path is recorded relative to the repository root, so root is prefixed to
    resolve it. If the manifest is missing or corrupt, it falls back to the filename
    convention `{mode}_{sky}_{view}.png`.
    """
    out = {}
    cams = {}
    mf = os.path.join(d, "manifest.json")
    if os.path.isfile(mf):
        try:
            j = json.load(open(mf))
            # views[name] = dict(eye, tgt) - required for the GRAZE v2 edge band projection
            cams = {k: v for k, v in (j.get("views") or {}).items()
                    if isinstance(v, dict) and "eye" in v and "tgt" in v}
            for s in j.get("shots", []):
                f = s.get("file", "")
                p = f if os.path.isabs(f) else os.path.join(root, f)
                if not os.path.isfile(p):
                    p2 = os.path.join(d, os.path.basename(f))
                    p = p2 if os.path.isfile(p2) else p
                if os.path.isfile(p):
                    out[s["view"]] = dict(path=p, mode=s.get("mode", "?"),
                                          ok=bool(s.get("ok", True)),
                                          cam=cams.get(s["view"]))
        except Exception as e:                       # Corrupt manifest -> fallback
            print(f"[경고] manifest 판독 실패 {mf}: {e}", file=sys.stderr)
    for p in sorted(glob.glob(os.path.join(d, "*.png"))):
        parts = os.path.basename(p)[:-4].split("_", 2)
        if len(parts) == 3 and parts[2] not in out:
            out[parts[2]] = dict(path=p, mode=parts[0], ok=True,
                                 cam=cams.get(parts[2]))
    return out


def is_graze_view(view):
    """Views subject to the grazing check = the h0.3 presets (primary evaluation) plus the
    grazing mise-en-scene family.

    The eye z in the manifest is a **world absolute z** and is therefore no indicator of
    robot eye height in scenes where the ground descends (the eye z of scene07 side_slope
    is -2.67). So the selection is made by the naming convention that grid_views produces
    (`preset_h0.3_*`).
    """
    v = view.lower()
    return ("h0.3" in v) or ("graz" in v)


# ===========================================================================
# [3] Verdict for one shot
# ===========================================================================
def _add(iss, sev, code, msg):
    iss.append(dict(sev=sev, code=code, msg=msg))


def check_view(scene, view, before, after, use_expected_fp=False):
    """Verdict for one (scene, view). before/after are the value dicts from index_round.

    **`use_expected_fp` defaults to OFF, and that is deliberate.** The GT-E2-x waiver is a
    *round-adjudication* policy, not part of the metric: `scripts/valset.py` - the corpora that
    license every GRAZE threshold in the project - calls this function positionally and counts
    findings by `code == "GRAZE"`, so a waived hit would silently leave the corpus and the
    thresholds would look like they had drifted. Defaulting off makes that structurally
    impossible instead of merely true today. The CLI in `main()` opts in; `--no-expected-fp`
    opts back out.

    The flag is carried per job rather than read from a module global so that its value is
    identical in the parent and in every pool worker regardless of the start method.
    """
    r = dict(scene=scene, view=view, verdict="PASS", issues=[], metrics={})
    iss = r["issues"]

    if before is None:
        _add(iss, "INFO", "NEW-VIEW", "이전 라운드에 없던 뷰 — 비교 불가")
    if after is None:
        _add(iss, "FAIL", "MISSING", "신규 라운드에 이 뷰가 없다 — 렌더 누락")
        r["verdict"] = "FAIL"
        return r
    if not after.get("ok", True):
        # `Docs/reports/realism_baseline.md` §known harmless phenomena - the file-size
        # stabilisation polling (40 attempts) of capture_pipeline finished prematurely; the file itself is fine.
        # So it is recorded as INFO only.
        _add(iss, "INFO", "CAPTURE",
             "manifest ok=false — 캡처 폴링 조기 종료(파일은 정상인 경우가 대부분)")

    gz_want = is_graze_view(view)
    fullB, smallB, blobB, grazB = _load(after["path"], gz_want)
    pb = photometry(fullB)
    r["metrics"].update({("after_" + k): v for k, v in pb.items()})

    # ---- Absolute checks -------------------------------------------------
    pa = None
    if before is not None:
        fullA, smallA, blobA, grazA = _load(before["path"], gz_want)
        pa = photometry(fullA)
        r["metrics"].update({("before_" + k): v for k, v in pa.items()})
        if before.get("mode", "?") != after.get("mode", "?"):
            _add(iss, "INFO", "MODE",
                 f"렌더 모드 상이 {before['mode']}→{after['mode']} — "
                 f"톤 정규화로 흡수하지만 절대 측광 비교는 주의")

    def grade(bad, warn, was_bad, worsened):
        """This tool is a **regression** checker. If the same defect existed in the
        previous round (= carried over), the grade is lowered. Otherwise the
        inherently dark scenes (scene06 spiral interior, scene13 underground,
        sceneD4 tunnel - 4 of the 33 passing scenes) would pour out the same alarm
        every round and make the table unreadable. But **if it got worse** the grade is kept."""
        sev = "FAIL" if bad else ("WARN" if warn else None)
        if sev is None or not was_bad:
            return sev, "[신규]"
        if worsened:
            return ("WARN" if bad else "INFO"), "[이월 — 악화]"
        return "INFO", "[이월 — 변화 없음, 회귀 아님]"

    # [DARK]
    dark_bad = pb["mean"] < DARK_MEAN_FAIL or pb["dark"] > DARK_PCT_FAIL
    dark_warn = pb["mean"] < DARK_MEAN_WARN or pb["dark"] > DARK_PCT_WARN
    if dark_bad or dark_warn:
        was = pa is not None and (pa["mean"] < DARK_MEAN_WARN
                                  or pa["dark"] > DARK_PCT_WARN)
        wor = pa is not None and (pb["mean"] < pa["mean"] - CARRY_DMEAN
                                  or pb["dark"] > pa["dark"] + CARRY_DDARK)
        sev, tag = grade(dark_bad, dark_warn, was, wor)
        if sev:
            _add(iss, sev, "DARK",
                 f"암흑 mean {pb['mean']:.1f} · dark {pb['dark']:.1f} %  {tag}")

    # [BLOWN]
    blown_bad = pb["mean"] > BLOWN_MEAN_FAIL or pb["clip"] > CLIP_PCT_FAIL
    blown_warn = pb["mean"] > BLOWN_MEAN_WARN or pb["clip"] > CLIP_PCT_WARN
    if blown_bad or blown_warn:
        was = pa is not None and (pa["mean"] > BLOWN_MEAN_WARN
                                  or pa["clip"] > CLIP_PCT_WARN)
        wor = pa is not None and (pb["mean"] > pa["mean"] + CARRY_DMEAN
                                  or pb["clip"] > pa["clip"] + 0.2)
        sev, tag = grade(blown_bad, blown_warn, was, wor)
        if sev:
            _add(iss, sev, "BLOWN",
                 f"과노출 mean {pb['mean']:.1f} · 255클리핑 {pb['clip']:.2f} %  {tag}")

    # [WHITE] - the absolute value is a reference, the increase decides
    if pa is not None:
        dw = pb["white"] - pa["white"]
        r["metrics"]["d_white"] = dw
        if dw > WHITE_DELTA_FAIL:
            _add(iss, "FAIL", "WHITE",
                 f"순백(>0.8) 대면적 증가 {pa['white']:.1f}→{pb['white']:.1f} % "
                 f"(+{dw:.1f} pp) — v5.1 §4 금지 규약")
        elif dw > WHITE_DELTA_WARN:
            _add(iss, "WARN", "WHITE",
                 f"순백 면적 증가 {pa['white']:.1f}→{pb['white']:.1f} % (+{dw:.1f} pp)")
        elif pb["white"] > WHITE_PCT_WARN:
            _add(iss, "INFO", "WHITE",
                 f"순백 대면적 {pb['white']:.1f} % [이월 — 픽셀>0.8 은 알베도>0.8 이 "
                 f"아니다. 절대치는 참고값]")
    elif pb["white"] > WHITE_PCT_WARN:
        _add(iss, "WARN", "WHITE", f"순백 대면적 {pb['white']:.1f} %")

    # ---- Regression checks (only when before exists) ---------------------
    if before is not None:
        la, lb = _lum(smallA), _lum(smallB)
        if la.shape != lb.shape:
            _add(iss, "WARN", "SIZE",
                 f"해상도 불일치 {pa['w']}×{pa['h']} → {pb['w']}×{pb['h']} — 구조 비교 생략")
        else:
            # PT always wobbles by +-1-2 LSB from sample noise. If nothing beyond that
            # changed, **the re-render or the toggle did not take effect**. There is a
            # precedent: scene01 uses its own capture block, so the shared toggle has no effect
            # (`Docs/reports/realism_phase1.md` §3.4).
            if fullA.shape == fullB.shape:
                d = np.abs(fullA - fullB)
                dmu = float(d.mean())
                dfr = 100.0 * float((d > 4).mean())
                r["metrics"].update(diff_mean=dmu, diff_frac=dfr)
                if dmu < IDENTICAL_MEAN and dfr < IDENTICAL_FRAC:
                    _add(iss, "WARN", "UNCHANGED",
                         f"이전 라운드와 사실상 동일(평균차 {dmu:.2f} LSB · "
                         f"4 LSB 초과 픽셀 {dfr:.3f} %) — 재렌더·룩 토글이 "
                         f"이 컷에 반영되지 않았을 가능성")

            # [PHOTO] abrupt luminance distribution change
            dmean = pb["mean"] - pa["mean"]
            ddark = pb["dark"] - pa["dark"]
            r["metrics"].update(d_mean=dmean, d_dark=ddark)
            if dmean <= PHOTO_DMEAN_FAIL or ddark >= PHOTO_DDARK_FAIL:
                _add(iss, "FAIL", "PHOTO",
                     f"휘도 급락 mean {pa['mean']:.1f}→{pb['mean']:.1f} "
                     f"({dmean:+.1f}) · dark {ddark:+.1f} pp")
            elif dmean <= PHOTO_DMEAN_WARN or ddark >= PHOTO_DDARK_WARN:
                _add(iss, "WARN", "PHOTO",
                     f"휘도 하락 mean {dmean:+.1f} · dark {ddark:+.1f} pp")
            elif dmean >= PHOTO_DMEAN_UP_WARN:
                _add(iss, "WARN", "PHOTO",
                     f"휘도 급상승 mean {pa['mean']:.1f}→{pb['mean']:.1f} "
                     f"({dmean:+.1f}) — 밝아지는 방향(대개 개선). 의도 확인")

            # [OCCL] new dark pixels = direct evidence of camera occlusion
            nd = (la >= OCCL_BRIGHT_BEFORE) & (lb < DARK_LEVEL)
            nd_pct = 100.0 * float(nd.mean())
            H = nd.shape[0]
            nd_near = 100.0 * float(nd[int(H * NEAR_BAND):].mean())
            ga, gb = _lum(blobA), _lum(blobB)
            blob = largest_blob_pct((ga >= OCCL_BRIGHT_BEFORE) & (gb < DARK_LEVEL))
            r["metrics"].update(newdark=nd_pct, newdark_near=nd_near, newdark_blob=blob)
            if nd_pct > OCCL_NEWDARK_FAIL or blob > OCCL_BLOB_FAIL:
                _add(iss, "FAIL", "OCCL",
                     f"신규 암부 {nd_pct:.1f} % (근거리대 {nd_near:.1f} %) · "
                     f"최대 연결 덩어리 {blob:.1f} % — 신설 기하가 카메라를 삼켰을 가능성")
            elif nd_pct > OCCL_NEWDARK_WARN or blob > OCCL_BLOB_WARN:
                _add(iss, "WARN", "OCCL",
                     f"신규 암부 {nd_pct:.1f} % (근거리대 {nd_near:.1f} %) · "
                     f"덩어리 {blob:.1f} %")

            # [FRAME] block occupancy shift after global tone normalisation
            lbn = tone_match(lb, la)
            bA, bB = block_means(la), block_means(lbn)
            dblk = np.abs(bA - bB)
            shift = 100.0 * float((dblk > FRAME_BLOCK_DELTA).mean())
            mx = float(dblk.max())
            r["metrics"].update(blk_shift=shift, blk_max=mx)
            if shift > FRAME_SHIFT_FAIL or mx > FRAME_MAXBLK_FAIL:
                _add(iss, "FAIL", "FRAME",
                     f"프레임 점유율 급변 — 이동 블록 {shift:.0f} % "
                     f"(최대 편차 {mx:.0f}/255). 톤 정규화 후 값이므로 "
                     f"밝기 변경이 아니라 **화면 구성**이 바뀐 것")
            elif shift > FRAME_SHIFT_WARN or mx > FRAME_MAXBLK_WARN:
                _add(iss, "WARN", "FRAME",
                     f"프레임 점유율 이동 {shift:.0f} % (최대 편차 {mx:.0f}/255)")

            # [GRAZE v2] horizontal coherence change in the drop edge projection band
            if gz_want:
                gz = None
                if grazA is not None and grazB is not None \
                        and grazA.shape == grazB.shape:
                    gz = graze_v2(grazA, tone_match(grazB, grazA), view,
                                  (after.get("cam") or (before or {}).get("cam")))
                if gz is None:
                    _add(iss, "INFO", "GRAZE",
                         f"[{GRAZE_VER}] 판정 유보 — manifest 에 이 뷰의 eye/tgt 가 "
                         f"없거나 시선이 지면을 안 물어 에지 대역을 못 세웠다")
                else:
                    r["metrics"].update(
                        # Row axis the GRAZE numbers live on. Recorded because `gz_row` is
                        # meaningless without it - the EXPECTED_FP register carries its own
                        # `scale_work` and the two must be compared, never assumed equal.
                        gz_work_h=int(grazA.shape[0]),
                        gz_ver=GRAZE_VER, gz_spec=gz["spec"], gz_dE=gz["dE"],
                        gz_dN=gz["dN"], gz_agree=gz["agree"], gz_row=gz["row"],
                        gz_band=[round(gz["e_top"], 1), round(gz["e_bot"], 1)],
                        gz_haz_row=round(gz["y_haz"], 1), gz_d=gz["d"],
                        gz_band_mu=gz["band_mu"],
                        gz_step_b=round(gz["step_b"], 2),
                        gz_step_a=round(gz["step_a"], 2),
                        gz_step_ratio=(round(gz["ratio"], 3)
                                       if math.isfinite(gz["ratio"]) else None),
                        gz_step_off=gz["row_off"],
                        gz_step_dom=(round(gz["dom"], 2)
                                     if math.isfinite(gz["dom"]) else None))
                    band = (f"에지대역 y{gz['e_top']:.0f}~{gz['e_bot']:.0f}"
                            f"/{grazA.shape[0]} (낙차 {gz['d']:.1f} m 지점 y"
                            f"{gz['y_haz']:.0f})")
                    if gz["band_mu"] < GRAZE_BAND_MU_MIN:
                        _add(iss, "INFO", "GRAZE",
                             f"[{GRAZE_VER}] 판정 유보 — 에지 대역이 너무 어둡다"
                             f"(휘도 {gz['band_mu']:.0f} < {GRAZE_BAND_MU_MIN:.0f}). {band}")
                    elif (abs(dmean) > GRAZE_PHOTO_DMEAN
                          or abs(ddark) > GRAZE_PHOTO_DDARK):
                        _add(iss, "INFO", "GRAZE",
                             f"[{GRAZE_VER}] 판정 유보 — 프레임 측광이 흔들렸다"
                             f"(Δmean {dmean:+.1f} · Δdark {ddark:+.1f} pp). "
                             f"조명 회귀를 먼저 처리하고 재실행할 것. {band}")
                    elif (gz["spec"] > GRAZE_SPEC_WARN
                          and gz["agree"] >= GRAZE_AGREE_MIN):
                        # --- [v2.1] Secondary discrimination ------------------
                        # Asks firings that passed the primary (v2) test "did that change alter the concealment?".
                        # The conditions are T3 §3.4-1 (persistence) and §3.4-2 / §11-2 (direction-wise step ratio)
                        # **merged into one** - T3 itself wrote that "implementing item 2 in this form
                        # solves the burial direction at the same time".
                        sev = "FAIL" if gz["spec"] > GRAZE_SPEC_FAIL else "WARN"
                        step = (f"단차 {gz['step_b']:.1f}→{gz['step_a']:.1f}"
                                f"(비 {gz['ratio']:.2f})"
                                if math.isfinite(gz["ratio"])
                                else f"단차 {gz['step_b']:.1f}→{gz['step_a']:.1f}")
                        quiet = None
                        # Applicability conditions - all must hold before secondary discrimination is attempted.
                        #  - WARN grade only (a FAIL is never demoted)
                        #  - a significant line exists on the drop row both before and after
                        #  - the maximum-change row lies on that line (it is not another object changing)
                        #  - the persisting line dominates the change (it is not a new riser)
                        eligible = (sev == "WARN"
                                    and gz["step_b"] >= GRAZE_STEP_MIN
                                    and gz["step_a"] >= GRAZE_STEP_MIN
                                    and gz["row_off"] <= GRAZE_PERSIST_ROWTOL
                                    and gz["dom"] >= GRAZE_PERSIST_DOM)
                        if eligible:
                            if gz["ratio"] > 1.0:
                                # Exposure direction - the line actually got stronger. Fire as in v2.
                                pass
                            elif gz["ratio"] > GRAZE_BURY_RATIO:
                                quiet = ("에지 존속 — 낙차행의 선이 이전·신규 양쪽에 "
                                         f"유의하게 남아 있고({step}) 변화량을 "
                                         f"{gz['dom']:.1f}배 압도한다. 변화의 실체는 에지 "
                                         "양쪽 **지면 알베도**이지 은닉 상태가 아니다")
                        if quiet:
                            _add(iss, "INFO", "GRAZE",
                                 f"[{GRAZE_VER}] 정숙(2차 판별) — 국소도 "
                                 f"{gz['spec']:.1f} 은 임계 초과지만 {quiet}. {band}")
                        else:
                            # The direction label is read from the **drop row step ratio** (the `up` of v2
                            # compares magnitudes at the maximum-change row and can disagree with the drop row).
                            grew = (gz["ratio"] > 1.0 if math.isfinite(gz["ratio"])
                                    else gz["up"])
                            why = ("에지 대역에 화면을 가로지르는 선이 **생겼다/굵어졌다** → "
                                   "숨어 있어야 할 낙차가 드러났을 가능성" if grew
                                   else "낙차행의 선이 **무너졌다** → 낙차가 과도하게 "
                                        "은폐·매몰됐을 가능성")
                            _add(iss, sev, "GRAZE",
                                 f"[{GRAZE_VER}][의심] 은닉 — 국소도 {gz['spec']:.1f} "
                                 f"(에지 {gz['dE']:.1f} − 근경 {gz['dN']:.1f}) · "
                                 f"열 일치율 {gz['agree']:.2f} · {step} · "
                                 f"최대 변화 y{gz['row']}. "
                                 f"{why}. {band}. **그 대역만 잘라서 육안 확인**"
                                 f"(자동 확정 불가)")

    # [D14] GT-E2-x pre-registration. Runs last, over the finished issue list, so there is exactly
    # one place in the tool where a finding can be waived and it is auditable in one read.
    fp = apply_expected_fp(r) if use_expected_fp else []
    if fp:
        r["expected_fp"] = fp

    worst = max((SEV[i["sev"]] for i in iss), default=0)
    r["verdict"] = SEV_NAME[worst] if worst >= 2 else ("INFO" if worst else "PASS")
    # A waived finding is not a pass. The row is only labelled EXPECTED_FP when the registry is
    # the **whole** reason it is no longer loud - if anything else is still WARN/FAIL that grade
    # stands, because the registry waives one line, not the cut.
    if fp and worst < SEV["WARN"]:
        r["verdict"] = "EXPECTED_FP"
    return r


def _job(args):
    try:
        return check_view(*args)
    except Exception as e:                          # So one failed shot does not kill the whole run
        scene, view = args[0], args[1]
        return dict(scene=scene, view=view, verdict="FAIL", metrics={},
                    issues=[dict(sev="FAIL", code="ERROR", msg=f"검사 예외: {e}")])


# ===========================================================================
# [4] Scene pair collection
# ===========================================================================
def resolve_round(scene_dir, spec):
    """Accepts a comma fallback such as `w2c_g2,w2_pilot,r2_on` and returns the first folder that exists."""
    for name in [s.strip() for s in spec.split(",") if s.strip()]:
        d = name if os.path.isabs(name) else os.path.join(scene_dir, name)
        if os.path.isdir(d) and glob.glob(os.path.join(d, "*.png")):
            return d
    return None


def collect_pairs(args, root):
    """Build [(scene name, before_dir, after_dir)]."""
    pairs = []
    if args.list:
        for ln in open(args.list, encoding="utf-8"):
            ln = ln.split("#")[0].strip()
            if not ln:
                continue
            f = [c.strip() for c in ln.replace("\t", " ").split() if c.strip()]
            if len(f) < 3:
                print(f"[경고] 목록 행 무시(3열 필요): {ln}", file=sys.stderr)
                continue
            sd = f[0] if os.path.isabs(f[0]) else os.path.join(root, f[0])
            b, a = resolve_round(sd, f[1]), resolve_round(sd, f[2])
            pairs.append((os.path.basename(sd.rstrip("/")), b, a))
    elif args.scenes:
        for sd in sorted(glob.glob(args.scenes)):
            if not os.path.isdir(sd):
                continue
            b = resolve_round(sd, args.before_round or "")
            a = resolve_round(sd, args.after_round or "")
            if a is None:
                continue                     # Scenes with no new round yet are skipped
            pairs.append((os.path.basename(sd.rstrip("/")), b, a))
    else:
        a = args.after
        b = args.before
        name = os.path.basename(os.path.dirname(a.rstrip("/"))) or "scene"
        pairs.append((name, b, a))
    return pairs


# ===========================================================================
# [5] Output
# ===========================================================================
MARK = {"PASS": "  ", "INFO": "· ", "WARN": "! ", "FAIL": "✗ ", "EXPECTED_FP": "= "}
VERDICT_W = 12   # widened from 6 for the EXPECTED_FP verdict token
_CONT = 2 + 22 + VERDICT_W + 7 + 7 + 9 + 8 + 9   # continuation-line indent, kept derived


def print_scene(scene, b, a, rows):
    tag = f"{scene}  [{os.path.basename(b) if b else '(이전 없음)'} → " \
          f"{os.path.basename(a)}]"
    print(f"\n{'='*100}\n{tag}\n{'-'*100}")
    print(f"{'':2}{'view':<22}{'판정':<{VERDICT_W}}{'mean':>7}{'dark%':>7}{'신규암부':>9}"
          f"{'덩어리':>8}{'블록이동':>9}  사유")
    for r in rows:
        m = r["metrics"]
        def g(k, f="{:.1f}"):
            return f.format(m[k]) if k in m else "-"
        head = (f"{MARK.get(r['verdict'], '? ')}{r['view'][:22]:<22}"
                f"{r['verdict']:<{VERDICT_W}}"
                f"{g('after_mean'):>7}{g('after_dark'):>7}{g('newdark'):>9}"
                f"{g('newdark_blob'):>8}{g('blk_shift','{:.0f}'):>9}")
        # All FAIL/WARN reasons are shown, INFO only as a count (alarm fatigue prevention -
        # listing everything makes priorities unreadable. The full text stays in --json).
        loud = [i for i in r["issues"] if SEV[i["sev"]] >= SEV["WARN"]]
        quiet = [i for i in r["issues"] if SEV[i["sev"]] < SEV["WARN"]]
        if not loud:
            note = ("· " + ", ".join(i["code"] for i in quiet)) if quiet else "—"
            print(head + "  " + note)
            continue
        first = True
        for i in sorted(loud, key=lambda i: -SEV[i["sev"]]):
            print((head if first else " " * _CONT) + f"  [{i['code']}] {i['msg']}")
            first = False
        if quiet:
            print(" " * _CONT + "  · " + ", ".join(i["code"] for i in quiet))


def print_summary(all_rows):
    order = {"FAIL": 0, "WARN": 1, "INFO": 2, "PASS": 3}
    bad = [r for r in all_rows if r["verdict"] in ("FAIL", "WARN")]
    n = len(all_rows)
    cnt = {k: sum(1 for r in all_rows if r["verdict"] == k)
           for k in SEV_NAME + ["EXPECTED_FP"]}
    print(f"\n{'='*100}\n총평 — {n} 컷 중 "
          f"FAIL {cnt['FAIL']} · WARN {cnt['WARN']} · "
          f"EXPECTED_FP {cnt['EXPECTED_FP']} · "
          f"INFO {cnt['INFO']} · PASS {cnt['PASS']}\n{'='*100}")
    # GT-E2-x pre-registered false positives. Printed **unconditionally and before everything
    # else** - a waiver the round record does not show is the failure mode this reader exists to
    # avoid, so it is never folded into the INFO count and never hidden by --fail-only.
    waived = [(r, f) for r in all_rows for f in r.get("expected_fp", [])]
    if waived:
        print(f"\nEXPECTED_FP — GT-E2-x 사전등재로 유보한 소견 {len(waived)} 건 "
              f"(무시가 아니라 **면제**. 등록부: ground_kit.EXPECTED_FP):")
        for r, f in sorted(waived, key=lambda kv: (kv[0]["scene"], kv[0]["view"])):
            print(f"  {r['scene']:<10} {r['view']:<24} "
                  f"{f['sev']}/{f['code']} → EXPECTED_FP  "
                  f"y{f['row']} ∈ {f['rows_work'][0]}~{f['rows_work'][1]}"
                  f"@{f['scale_work']}  ({f['src']})")
    # Carried-over defects - not regressions, but absolute states the supervisor should know about
    carry = {}
    for r in all_rows:
        for i in r["issues"]:
            if i["sev"] == "INFO" and i["code"] in ("DARK", "BLOWN", "WHITE"):
                carry.setdefault(i["code"], {}).setdefault(r["scene"], 0)
                carry[i["code"]][r["scene"]] += 1
    if carry:
        print("\n이월 결함 (이전 라운드에도 있던 절대 상태 — 회귀 아님, 참고):")
        for code, sc in sorted(carry.items()):
            tot = sum(sc.values())
            top = ", ".join(f"{s}×{n}" for s, n in
                            sorted(sc.items(), key=lambda kv: -kv[1])[:6])
            print(f"  {code:<6} {tot:>3} 컷 — {top}")

    if not bad:
        print("\n회귀 없음.")
        return
    print("\n우선순위 (FAIL → WARN, 씬순):")
    for r in sorted(bad, key=lambda r: (order[r["verdict"]], r["scene"], r["view"])):
        codes = ",".join(sorted({i["code"] for i in r["issues"]
                                 if i["sev"] in ("FAIL", "WARN")}))
        print(f"  {r['verdict']:<5} {r['scene']:<10} {r['view']:<24} {codes}")
    scenes = {}
    for r in all_rows:
        s = scenes.setdefault(r["scene"], {"FAIL": 0, "WARN": 0})
        if r["verdict"] in s:
            s[r["verdict"]] += 1
    worst = sorted(scenes.items(), key=lambda kv: (-kv[1]["FAIL"], -kv[1]["WARN"]))
    print("\n씬 우선순위:")
    for s, c in worst:
        if c["FAIL"] or c["WARN"]:
            print(f"  {s:<12} FAIL {c['FAIL']:>2} · WARN {c['WARN']:>2}")


# ===========================================================================
# [6] Self-test - the §6.1 smoke for this file (no images, no GPU, no Isaac)
# ===========================================================================
def selftest():
    """Exercise the EXPECTED_FP reader against the **live** registry.

    It deliberately uses a real `ground_kit` key instead of a fabricated one, so the test also
    proves the registry is importable and shaped the way this reader assumes. Run it with
    `python3 scripts/regression_check.py --selftest`.
    """
    fails = []

    def chk(name, ok, detail=""):
        print(f"  {'✔' if ok else '✗'} {name}" + (f"  [{detail}]" if detail else ""))
        if not ok:
            fails.append(name)

    print("regression_check EXPECTED_FP 자기검사")
    reg = expected_fp_register()
    chk("등록부 적재", bool(reg), f"{len(reg)} 행 · {_FP_SOURCE}")
    if not reg:
        print("  → 등록부 없이는 나머지 항목을 검사할 수 없다.")
        return False

    work_h = GRAZE_LONG * 9 // 16          # 16:9 frame -> the axis gz_row is measured on
    chk("작업 축 = 등록부 소비자 축", all(int(v["scale_work"]) == work_h
                                          for v in reg.values()),
        f"{work_h} 행")
    chk("모든 행이 (lo ≤ hi) 2원소 밴드 + 출처",
        all(len(v["rows_work"]) == 2 and v["rows_work"][0] <= v["rows_work"][1]
            and v.get("src") for v in reg.values()))

    key = ("scene16", "preset_h0.3_d5")
    chk("표본 키 존재 (K1 이 착지시킨 행)", key in reg, str(reg.get(key)))
    if key not in reg:
        return False
    lo, hi = reg[key]["rows_work"]
    sc, vw = key

    # --- expected_fp_match: exactness, both edges, both misses ---------------
    chk("밴드 하단 경계 포함", expected_fp_match(sc, vw, lo, work_h) is not None)
    chk("밴드 상단 경계 포함", expected_fp_match(sc, vw, hi, work_h) is not None)
    chk("밴드 밖(하단−1) 불일치", expected_fp_match(sc, vw, lo - 1, work_h) is None)
    chk("밴드 밖(상단+1) 불일치", expected_fp_match(sc, vw, hi + 1, work_h) is None)
    chk("다른 씬 불일치", expected_fp_match("scene99", vw, lo, work_h) is None)
    chk("다른 컷 불일치", expected_fp_match(sc, "preset_h0.9_d5", lo, work_h) is None)
    chk("행 없음 → 불일치", expected_fp_match(sc, vw, None, work_h) is None)
    ax = expected_fp_match(sc, vw, lo, work_h * 2)
    chk("축 불일치는 매치가 아니라 진단",
        isinstance(ax, dict) and ax.get("_axis_mismatch") is True)

    # --- apply_expected_fp: end to end on synthetic rows ---------------------
    def row(code, sev, r_row, extra=None):
        m = dict(gz_row=r_row, gz_work_h=work_h)
        iss = [dict(sev=sev, code=code, msg=f"원문-{code}")]
        if extra:
            iss.append(dict(sev=extra[1], code=extra[0], msg=f"원문-{extra[0]}"))
        return dict(scene=sc, view=vw, verdict="PASS", issues=iss, metrics=m)

    def verdict_of(r, hits):
        worst = max((SEV[i["sev"]] for i in r["issues"]), default=0)
        v = SEV_NAME[worst] if worst >= 2 else ("INFO" if worst else "PASS")
        return "EXPECTED_FP" if (hits and worst < SEV["WARN"]) else v

    r1 = row("GRAZE", "FAIL", (lo + hi) // 2)
    h1 = apply_expected_fp(r1)
    chk("등재행 GRAZE FAIL → EXPECTED_FP 판정", len(h1) == 1
        and verdict_of(r1, h1) == "EXPECTED_FP", str(verdict_of(r1, h1)))
    chk("원 소견 텍스트·등급·코드 보존(감사성)",
        r1["issues"][0].get("was") == {"sev": "FAIL", "code": "GRAZE"}
        and "원문-GRAZE" in r1["issues"][0]["msg"]
        and r1["issues"][0]["code"] == "EXPECTED_FP"
        and r1["issues"][0]["sev"] == "INFO")
    chk("등재행이라도 PASS 로 죽지 않는다", verdict_of(r1, h1) != "PASS")

    r2 = row("GRAZE", "FAIL", (lo + hi) // 2, extra=("FRAME", "FAIL"))
    h2 = apply_expected_fp(r2)
    chk("다른 소견이 남으면 컷 등급은 유지", len(h2) == 1
        and verdict_of(r2, h2) == "FAIL", str(verdict_of(r2, h2)))

    r3 = row("GRAZE", "FAIL", hi + 40)
    h3 = apply_expected_fp(r3)
    chk("등재 밖 GRAZE 는 그대로 크게 남는다", not h3
        and verdict_of(r3, h3) == "FAIL" and r3["issues"][0]["code"] == "GRAZE")

    r4 = row("OCCL", "FAIL", (lo + hi) // 2)
    h4 = apply_expected_fp(r4)
    chk("행 앵커 없는 코드(OCCL)는 절대 면제되지 않는다", not h4
        and r4["issues"][0]["code"] == "OCCL")

    r5 = row("GRAZE", "INFO", (lo + hi) // 2)
    h5 = apply_expected_fp(r5)
    chk("이미 조용한 소견은 건드리지 않는다", not h5
        and r5["issues"][0]["code"] == "GRAZE")

    r6 = row("GRAZE", "FAIL", (lo + hi) // 2)
    r6["metrics"].pop("gz_work_h")
    chk("작업 축 미기록이면 면제하지 않는다", not apply_expected_fp(r6)
        and r6["issues"][0]["code"] == "GRAZE")

    print(f"\n{'전 항목 통과' if not fails else '실패 ' + str(len(fails)) + ' 건: ' + ', '.join(fails)}")
    return not fails


# ===========================================================================
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="렌더 라운드 회귀 검사기 (이미지 + manifest.json 만 사용)")
    ap.add_argument("--before", help="이전 라운드 폴더 (단일 씬 모드)")
    ap.add_argument("--after", help="신규 라운드 폴더 (단일 씬 모드)")
    ap.add_argument("--scenes", help="씬 폴더 글롭 (예: 'look_check/scene*')")
    ap.add_argument("--before-round", help="씬 안의 이전 라운드 이름. 쉼표 폴백 가능")
    ap.add_argument("--after-round", help="씬 안의 신규 라운드 이름. 쉼표 폴백 가능")
    ap.add_argument("--list", help="씬별 라운드 목록 파일 (씬경로 이전 이후)")
    ap.add_argument("--json", help="기계 판독용 JSON 출력 경로")
    ap.add_argument("--only", help="뷰 이름 부분일치 필터 (쉼표)")
    ap.add_argument("--fail-only", action="store_true", help="FAIL/WARN 컷만 출력")
    ap.add_argument("--no-expected-fp", action="store_true",
                    help="GT-E2-x 사전등재(ground_kit.EXPECTED_FP) 판독을 끈다 — D14 이전 원판정")
    ap.add_argument("--selftest", action="store_true",
                    help="EXPECTED_FP 판독기 자기검사만 실행하고 종료(이미지 불필요)")
    ap.add_argument("--jobs", type=int, default=min(8, os.cpu_count() or 1))
    ap.add_argument("--root", default=os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))),
        help="저장소 루트 (manifest 의 상대경로 해석 기준)")
    a = ap.parse_args(argv)

    if a.selftest:
        return 0 if selftest() else 1

    if not (a.list or a.scenes or (a.before and a.after)):
        ap.error("--before/--after, 또는 --scenes + --after-round, 또는 --list 중 하나가 필요합니다.")
    if a.scenes and not a.after_round:
        ap.error("--scenes 모드에는 --after-round 가 필요합니다.")

    root = a.root
    pairs = collect_pairs(a, root)
    if not pairs:
        print("[에러] 비교할 씬을 못 찾았습니다.")
        return 2
    only = [s.strip() for s in a.only.split(",")] if a.only else None

    jobs, meta = [], []
    for scene, bdir, adir in pairs:
        if adir is None or not os.path.isdir(adir):
            print(f"[경고] {scene}: 신규 라운드 폴더 없음 — 건너뜀", file=sys.stderr)
            continue
        A = index_round(adir, root)
        B = index_round(bdir, root) if bdir else {}
        if bdir is None:
            print(f"[경고] {scene}: 이전 라운드 폴더 없음 — 절대 검사만 수행",
                  file=sys.stderr)
        views = sorted(set(A) | set(B))
        if only:
            views = [v for v in views if any(o in v for o in only)]
        for v in views:
            jobs.append((scene, v, B.get(v), A.get(v), not a.no_expected_fp))
        meta.append((scene, bdir, adir, views))

    if not jobs:
        print("[에러] 비교할 컷이 없습니다.")
        return 2

    if a.jobs > 1 and len(jobs) > 1:
        with ProcessPoolExecutor(max_workers=a.jobs) as ex:
            results = list(ex.map(_job, jobs, chunksize=1))
    else:
        results = [_job(j) for j in jobs]

    by = {}
    for r in results:
        by.setdefault(r["scene"], {})[r["view"]] = r
    for scene, bdir, adir, views in meta:
        rows = [by[scene][v] for v in views if v in by.get(scene, {})]
        if a.fail_only:
            rows = [r for r in rows if r["verdict"] in ("FAIL", "WARN")]
            if not rows:
                continue
        print_scene(scene, bdir, adir, rows)
    print_summary(results)

    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)) or ".", exist_ok=True)
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(dict(
                pairs=[dict(scene=s, before=b, after=c) for s, b, c, _ in meta],
                results=results), f, indent=2, ensure_ascii=False)
        print(f"\n[JSON] {a.json}")

    # Exit code: 1 when there is a FAIL (so batch scripts can use it as a gate)
    return 1 if any(r["verdict"] == "FAIL" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
