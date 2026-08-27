# -*- coding: utf-8 -*-
"""
scene03_riverbank.py — NegObs synthetic scene 3: river levee descending stair (Isaac Sim 4.5)

Spec   : Docs/briefs/multi_scene_brief_v2.md §C(scene03_riverbank) — sole spec
Shared library : scene_common.py (§A) / skeleton convention : scene01_campus_stairs.py

Type (T5 river levee): **no railing × water-surface anchor**.
  The stair descends through a cut in the slope from the flat levee crest → from a low
  viewpoint stair and slope fold into the slope and vanish completely. The only evidence
  of the drop is **the water (the lowest point) + the far bank + tree crowns below eye
  height**. **Having no railing is the identity of this type** (cue_railing defaults to False).

Run (GUI look check — default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene03_riverbank.py

Auto capture mode (for headless verification):
    NEGOBS_CAPTURE=1 python scene03_riverbank.py
      NEGOBS_CAPTURE_DIR  : output folder (default look_check/scene03/auto)
      NEGOBS_CAPTURE_MODE : rt | pt | both (default rt)
      NEGOBS_VIEWS        : comma-separated view name filter (default all)

Coordinates: Z-up, m, travel axis +X, drop start edge = x=0 (levee crest shoulder).

────────────────────────────────────────────────────────────────────────────
Geometry correction (supervisor ruling applied):
  The 16 steps of brief §C give a drop of 16×0.16=2.56, inconsistent with the slope/beach drop 3.2.
  → Supervisor decision: **extend the stair to 20 steps**. drop 20×0.16=3.2 (matches slope·beach),
    run 20×0.35=7.0 → slope run=7.0, beach start x=7.0, stair base_z=-3.6 kept.
    Trim beam drop=3.2; cue_railing ground_fn·run·drop also follow 20 steps. No landing.
  Waterside realignment: beach x 7.0..18.0, riprap strip x0=17.0, water x0=17.5 (effective waterline x≈18).
────────────────────────────────────────────────────────────────────────────
[v5.1 realism — meandering river rebuild]  User feedback: "the river bends unnaturally (a straight channel)".

  * Coordinate convention change: the PARAMS x values of river-parallel elements (levee crest·
    crest walk·slope·beach·walkway·riprap·water·far bank) are now **not world X but the
    cross-section coordinate s** (the offset from the river centerline). World X = s + dx(y).
      dx(y) = A1·(cos(2πy/L1) − 1) + A3·(y/40)³      [river_dx]
      A1=6.0 · L1=110 · A3=−2.0
    Design constraints:
      · dx(0)=0, dx′(0)=0  → in the stair corridor (y ±0.95) the centerline points exactly
        along +Y with offset 0 → **the hazard geometry (stair·trim·spur) transform is wholly unchanged**.
      · 19 segs (meets the required 10+, seg_dy 5.0, y −47.5..47.5).
      · |yaw|max 23.2° · yaw change between adjacent segs ≤6.5° · lateral dx amplitude 14.8 m.
    The channel narrows 22.5 → 15.8 m (far_bank s 40→34, water s1 40→36), so
    meander amplitude/channel width = 0.94 ≈ the floor of the brief's required "1~2x". A larger
    amplitude pushes the bank tangent past 45° (oxbow territory) and looks unnatural inside a 95 m view.

  * Band assembly: each seg is an axis-aligned build_slope box placed inside
    build_rot_group(pivot=seg centre, yaw) (shear-free placement — folding·self-intersection impossible by construction).
      · seg local run = width/cos(yaw) → **the world X projection of the top face is exactly the width**
        → adjacent bands always **overlap** by (width sum/2)·(1/cos−cos) (zero gap).
      · seg length = span/cos(yaw) + 0.8 overlap → zero opening at the longitudinal joints.
        (blocks a recurrence of audit v4's most frequent defect, 'water-ground junction floating')
      · Coplanar Z-fighting at equal z is avoided by a 1.5 mm stagger per seg·sub-band index.
────────────────────────────────────────────────────────────────────────────
[v7 W3 · S03 lane]  Target image **G3** (`Docs/reference_photos/Generated Image - Scene03.jpg`),
  season pinned **summer / full leaf** (§7-8 season policy: every scene pins its own image's
  season). Governing law: `w3_intake_v2_images.md` §2 scene03 row + §7 **R03-1** + §3(ii)
  rectangular-pattern sweep; carried items 03-A / 03-B / 03-C / 03-D.

  (1) **R03-1 — the channel goes back WIDER THAN v4.** The v5.1 narrowing (22.5 → 15.8 m) is
      **superseded**: effective water 15.8 → **33.8 m** (far_bank s 34 → 52, water s1 36 → 54),
      i.e. +114 % over v5.1 and +50 % over the v4 width the ruling names as the floor. The
      meander amplitude is raised with it (A1 6.0 → 10.0, A3 −2.0 → −3.4, amplitude
      14.81 → **24.79 m**) so the bend is not flattened by the widening; |yaw|max
      23.17° → **35.64°**, still well short of the 45° oxbow limit the v5.1 note draws.
      amplitude/width lands at **0.73** (was 0.94) — the two constraints are in direct
      arithmetic conflict and R03-1 rules which one gives. **No camera edit**: all 9 judge
      presets and all 7 mise-en-scène cuts keep their coordinates to the digit.
      Measured effect (`river_width_selfcheck`): water screen-area share of the frame
      +36…+50 % on every cut that sees it.
  (2) **03-C / K4-F4 — one silhouette class per bank.** The far-bank tree line now passes
      `belt=True`, which activates `SCENE_SPECIES["Scene03"]`'s declared belt (`oak_black`,
      Black_Oak) instead of planting the route species on both banks. Near bank (levee crest
      + 둔치) stays `poplar` — `w3_intake_v2_images.md` §2 scene03 (e) rules the
      `Lombardy_Poplar` levee assignment stands.
  (3) **03-D — the never-replaced bushes.** The 6 × 3 = 18 flattened-ellipsoid blobs on the
      slope become **real shrub USDs** through `sc.place_shrubs`, one bed = the whole slope
      band (monospecific by construction, K4(b) S-2). The blob path is kept as the
      assets-absent fallback (scene10 precedent), so LOOK_GEO=0 does not empty the slope.
  (4) **03-A + user ban on 사각형 무늬** — every decorative ground rectangle leaves the scene:
      the 8 `levee_paved` repair patches (→ 0), the D8 beach sports-field rectangle, and the
      D6 levee-crest cycle-track centre line (a painted line on a *gravel* road, which also
      contradicted the 07-29 "03 stays natural, the cycle track holds only for scene17"
      ruling). The 둔치 cycle-track markings (D4) **stay** — functional road markings, not a
      decorative pattern.
  (5) **03-B — bollards onto the line they defend** (G-3 / PE-7): cx −1.2 → −1.0 (the spur
      entry line), cy ±2.2 → **±1.2** (the spur edge). The third centre post the 03-B build
      spec asks for is **declined, with a measured reason** — see `PARAMS["bollards"]`.

[v8 W3 · P03 lane]  Ledger rows **GT-46** (paving, FULL) · **GT-47** (its consequences).
  Ruling: `w3_intake_v2_images.md` **§7.2 S03** — *"S03 crest promenade — PAVE, image doctrine
  wins. G3's 점토블록 promenade supersedes the 07-29 'natural' ruling."* This closes the item
  the S03 lane raised and refused to decide on its own (`w3_s03_v1.md` §7-9).

  (6) **The crest walk is PAVED.** `levee_road` (3.0 m gravel, `/…/LeveeRoad`) →
      `crest_walk` (**4.0 m 점토블록**, `/…/CrestWalk`) + `crest_band` (**0.4 m light-grey
      block edge band = 2 courses of the 200 mm module**, `/…/CrestBand`), and the stair-head
      apron takes the same paving. Hard walked surface **3.0 → 4.4 m**; 1.4 m × 95 m of mown
      turf becomes walkable. The river-side paving edge stays at **x = −1.0**, so the 1.0 m
      grass shoulder in front of the *unguarded* drop survives and **no new drop-parallel
      line enters the near window**. `proud` stays **0.0015** — raising it to scene17's 0.006
      would push the stair's first riser 0.1615 → 0.1660 m against 19 uniform 0.160 risers
      (편의증진법 별표1 uniform 챌면), for zero visual return. **The drop edge at x = 0 does
      not move: 3.2015 m, unchanged.**
  (7) **The tone item `w3_s03_v1.md` §7-3 handed on is closed at its cause.** The near-white
      near ground (h0.3_d2 `wht% 39.1 · mean 194 · σ_LF 0.94`) was never a missing-element
      problem — it was the **gravel scan's highlight tail**: `gravel_diff` reads luminance
      p99 **215.4** / >204 **3.56 %** where `paving_interlock_diff` reads **173.6** / **0.09 %**
      at the same 0.28 mean albedo. Unit paving has no bright-stone tail, so the
      region-restricted scatter that lane asked the kit for is no longer this scene's blocker.
  (8) **The G3 river-edge timber post-and-rail fence stays DECLINED** (§7.2: *"the scene's
      no-railing × water-anchor research identity outranks one image element"*). The
      divergence is documented in `w3_p03_v1.md`, not silently absorbed. The 07-29 ruling's
      **cycle-track** clause is also untouched — there is still no bike road and no centre
      line on this crest; only its *natural surface* clause is superseded.
  (9) **Consequences (GT-47)**: ground-plan region x0 −12.0 → −5.4 · `pave.module` declared
      truthfully at (0.200, 0.100) while `joint` stays declined · edge break x −4.0 → −5.4 ·
      the `cue_material_break=False` and `hazard_stairs=False` arms re-bound so the paving
      cannot smuggle a material break into a control · `wear` re-bound off `dirt_park` ·
      the pergola moved 0.8 m landward out of the new paving.
────────────────────────────────────────────────────────────────────────────
[GT-83 · crossing rebuilt as an overpass]  User verdict on `pt_noon_levee_walk`: the crossing
  sits low, in the middle of the walk cut, and reads as purposeless — *"if it is an overpass,
  make it even higher and move it to the side"*.

  * **Higher.** soffit −1.00 → **+1.80** (deck top −0.20 → +2.90, deck depth 0.80 → 1.10):
    **5.15 m over the water · 5.00 m over the 둔치 · 4.98 m over the 둔치 cycle track**.
  * **To the side.** deck centre y −18.0 → **−23.0**; the in-frame band in `levee_walk` moves
    from u/half [0.34, 1.00] to **[0.85, 0.92]**, entirely above the frame centre. Upper bound
    on both moves: `bank_oblique`'s frozen eye clears the parapet top by 4.00 m and stands
    2.12 m off the deck centreline, so neither height nor lateral travel may go further.
  * **Lands on something.** Bank-seat abutments (body + spread footing) at both deck ends —
    near end on the 둔치 (s 12.84…16.49), far end on the far bank (s 58.01…61.58) — with the
    deck and both parapets ending 1.10 m INSIDE the block. Piers 7 → 3 hammerhead T-piers on a
    uniform 10.40 m bay, all three standing in open water.
  * Consequences: the reed band takes a `y_gap` across the near bridgehead; one far-bank tree
    (cy −31.0 → −41.0) leaves the deck footprint it would have grown through; a `bridge_wear`
    asphalt carriageway tone joins the material table. Levee, slope, stair, drop edge, water
    level, riprap and P-13 are untouched.
────────────────────────────────────────────────────────────────────────────
[GT-83 pass 2 · the crossing becomes buildable]  User verdict on `pt_noon_meander_air`
  (probe `260806_w3_s03probe`): *"make it more REALISTICALLY IMPLEMENTABLE"*. GT-83's
  alignment is **frozen**: `x0/x1`, `y0/y1` (−27.5/−18.5), `deck_top` +2.90, `deck_thick`
  1.10 and `parapet_h` 1.10 are all unchanged, so the 5.15/5.00/4.98 m clearances, the
  `levee_walk` u/half [0.85, 0.92] band and `bank_oblique`'s 4.00 m eye clearance carry over
  to the digit. What changes is what the structure is MADE OF.

  (1) **Neither bank is a dead end any more.** Both GT-83 abutments are **wall piers**
      (`abut_z0` −3.45 → soffit +1.85): the near one is **5.30 m** where GT-83 left 7.45 m
      of blank face, with a **stone scour apron** 0.80 m proud of its footing lifting the
      base out of the mown grass and two **belt courses** breaking what is left. The
      bridgehead members — two **bearing pedestals** in a 0.35 m shelf gap, a **back wall**
      set back 0.12 m, an **approach slab** nosing 0.10 m past the seat with its asphalt
      stopping 0.08 m short, two **parapet end posts** 0.025 m proud of the coping — moved to
      the two places the ribbon actually ends.
  (2) **The carriageway continues on BOTH sides, to the modelled ground's edge.**
      Far: a **23.0 m viaduct** at 2.5 % on two more T-piers to an end bridgehead 1.4 m
      inside s 88. Near **[pass 3, 08-06 ruling]**: a **42.4 m curved southward viaduct** —
      90.0° of turn over 13.0 m in 11 eased chords (2.25° at the bridgehead, 9.00° max),
      then 6 river-parallel chords holding s 5.29 down to an end bridgehead at y −45.8.
      It never crosses the drop edge (deck envelope **s 0.33…14.84**), clears the promenade
      by 1.33 m and everything under it by ≥ **1.40 m**, and its parapet tops out 1.5 mm
      **below** the main deck's +4.00.
  (3) **The deck edge is a section, not a slab.** Same 1.10 m depth, split into a 0.38 m
      **slab fascia** over a 0.72 m **girder band** recessed 0.30 m behind it, with a
      **drip nose** at the fascia bottom; the parapet keeps its 1.10 m but gives its top
      0.16 m to a **coping** proud on both faces. Tones alternate cope 0.28 / parapet 0.22 /
      fascia 0.28 / girder 0.235 (`concrete_girder` is the one new material). Every run of
      the ribbon — river span, both approaches, all 17 near chords — is the SAME `deck_run`
      call, and consecutive chords are **mitred** (extended by 4.55·tan(kink/2)) so the
      section is carried through all 29 joints without a wedge or a member break.
  * Consequences: the reed `y_gap` lower end opens −20.3 → −21.0 for the apron flanks (band
    stays 17 segs); one beach tree moves (9.0, −10.0) → (13.4, −6.0), out from under the new
    deck edge; `river_view_selfcheck` gains the near-approach chords as occluders **and now
    reports meander_air 51/131 = 38.9 % against its own 35 % criterion — a declared, ruling-
    caused FAIL, not a tuned gate** (see that function: the visible waterline still spans
    65.0 m with an 18.37 % bow). Levee, slope, stair, drop edge x=0, water level, riprap,
    P-13, the far-tree stand and every camera preset are untouched.
────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import math
import json
import random
import datetime

import numpy as np

import scene_common as sc
import ground_kit as gk


# ===========================================================================
# [A] SCENE_CONFIG - scene01 6 keys + cue_nosing (new). Cues that are
#     meaningless here default to False (code path exists). Only hazard_stairs moves geometry.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False -> stairs+slope+beach become z=0 flat (only geometry toggle)
    "cue_railing":        False,   # **the identity of this type** - if True, one pipe rail on the stair right (y=+0.85) only
    "cue_tactile":        False,   # tactile paving is not the practice on levees - code path reserved only (unused here)
    "cue_material_break": True,    # [P03] crest 점토블록 vs stair concrete. False->stair takes the crest paving
    "cue_sign":           False,   # [optional] not implemented - config key reserved only
    "cue_scene_dressing": True,    # bollards·benches·shrubs·trees·dirt path, all together
    "cue_nosing":         False,   # [new] True -> non-slip nosing strip on every step
}


# ===========================================================================
# [B] PARAMS - §C dimensions + material/light/capture. NEGOBS_PARAMS_OVERRIDE merges in.
#     The light dict keeps scene01's verified noon constants. SUN_AZ_OFFSET=171.5.
# ===========================================================================
PARAMS = dict(
    # --- [v5.1] meander centerline (read by the module fns river_dx/river_yaw) ---
    #   y0/y1 are the band assembly range (7.5 beyond the terrain y +-40 - keeps the seg
    #   ends from curling inward as they rotate and tearing a sky hole in the far view).
    # [v7 R03-1] A1 6.0 -> 10.0 · A3 -2.0 -> -3.4. The channel widening below would otherwise
    #   flatten the bend (amplitude/width would fall to 0.44), so the amplitude is raised with
    #   it: 14.81 -> 24.79 m. Everything the v5.1 note gates on is re-measured, not assumed:
    #     |yaw|max        23.17 -> 35.64 deg   (the note's oxbow limit is 45 deg)
    #     adj-seg d(yaw)   6.48 -> 10.82 deg
    #     overlap lip @ |yaw|max, shoulder band w=3.0   0.25 -> 0.63 m  (far field, |y| ~ 40)
    #   **dx(0)=0 and dx'(0)=0 hold for ANY A1/A3**, so the hazard corridor (y +-0.95) transform
    #   is bit-identical to v6: stair · trim · spur · drop edge x=0 do not move. That invariance
    #   is the reason this is not a walked-surface GT change.
    meander=dict(A1=10.0, L1=110.0, A3=-3.4, y_ref=40.0,
                 seg_dy=5.0, y0=-47.5, y1=47.5, over=0.8, z_stagger=0.0015),
    # --- terrain ---
    # levee crest: grass base + a 점토블록 promenade band along Y (river-parallel, with its
    #   grey edge band) + the stair-head apron   [P03 · GT-46]
    # v4-A1/A2: levee crest y +-10 -> +-40 (matches the beach), x0 −20 -> −45.
    #   Previously no prim existed at x<−20 or |y|>10, so the main walk axis (levee path)
    #   was cut off into thin air, and a notch 3.2 deep lay open beside the slope (x 0..7, |y| 10..40).
    levee=dict(x0=-45.0, x1=0.0, y0=-40.0, y1=40.0, z_top=0.0, thick=0.5),
    # === [P03 · GT-46] the crest walk is PAVED in G3's 점토블록 ==================
    # Ruling: `w3_intake_v2_images.md` §7.2 S03 — *"S03 crest promenade — PAVE, image
    #   doctrine wins. G3's 점토블록 promenade supersedes the 07-29 'natural' ruling
    #   (that ruling predates the target-image doctrine)."* The conflict was **raised**
    #   by the S03 lane (`w3_s03_v1.md` §7-9, *"the single largest archetype divergence
    #   from the target image"*) and deliberately left for a ruling; this is that ruling
    #   executed.
    # Pre-state (v7): `levee_road=dict(x0=-4.0, x1=-1.0, ...)` — a 3.0 m **gravel**
    #   maintenance band. G3 shows no gravel anywhere on the crest: the walk is a
    #   tan/beige interlocking clay-block promenade with a light-grey block edge band.
    # Post-state: a 4.0 m 점토블록 field + a 0.4 m grey edge band = 4.4 m of hard walked
    #   surface, replacing 3.0 m of gravel and taking 1.4 m from the mown verge.
    #
    # **Widths.** 4.0 m clear + 0.4 m band. A Hangang 둔치/제방 산책로 runs 4~6 m; 4.0 is
    #   the low end of that band and is the widest this crest can carry while leaving the
    #   **1.0 m grass shoulder** (x −1..0) between the paving and the *unguarded* 3.2 m
    #   drop at x=0. The band is 0.400 m = **exactly 2 courses of the 200 mm module**.
    # **The band sits on the LANDWARD margin, not the river margin where G3 puts it, and
    #   that is a declared divergence with a research reason**: a light/dark line running
    #   parallel to the drop edge, 1.0~1.4 m in front of it, would sit 0.6~1.0 m ahead of
    #   the h0.3 d2 judged eye and act as a **drop cue this scene never declared**
    #   (`cue_*` in SCENE_CONFIG is the scene's cue vector; adding one silently
    #   contaminates the design). On the landward margin it is 4.0~4.4 m from the drop and
    #   cues nothing. See `w3_p03_v1.md`.
    # **`proud` stays 0.0015 — held, not overlooked, and the reason is the stair.**
    #   `_stair_steps` starts the flight at `z_top = 0.000`, so the first riser measured
    #   from the walked surface is `0.160 + proud`:
    #       proud 0.0015 → first riser 0.1615 m  (+0.94 % on 19 uniform 0.160 risers)
    #       proud 0.0060 → first riser 0.1660 m  (+3.75 %)   ← scene17's crown value
    #   편의증진법 별표1 requires uniform 챌면, and 0.006 has no visual return here: the
    #   landward paving edge is behind the d5 eye and 4.6 m ahead of the d10 eye, where a
    #   4.5 mm step subtends ~0.02 px. So the drop edge at x=0 keeps **3.2015 m** exactly.
    crest_walk=dict(x0=-5.0, x1=-1.0, proud=0.0015, embed=0.05),   # 점토블록 promenade (4.0 m)
    crest_band=dict(x0=-5.4, x1=-5.0),                             # light-grey block edge band (2×200 mm)
    levee_spur=dict(x0=-1.0, x1=0.0, y0=-1.2, y1=1.2),             # stair-head apron (same 점토블록)

    # === [W2-D ground_kit] P13 levee_paved (spec §5.7) ======================
    # **[P03 · GT-47] The 07-29 hold is lifted on the SURFACE clause only.** That ruling
    #   said *"03 stays natural, the cycle track holds only for the scene17 levee"*, i.e.
    #   two things at once: (a) no paving and (b) no bike road. §7.2 supersedes (a);
    #   **(b) is untouched** — there is still no cycle track, no lane marking and no
    #   centre line on this crest, and D6's deleted centre line stays deleted.
    #   -> `natural=True` is **kept** in `overrides`, and that is a deliberate choice, not
    #      an oversight. The flag's only effect is to make ground_kit raise on urban infra
    #      (manhole / gully / gutter / marking). G3 shows none of those on the promenade,
    #      the "03 stays kerbless pending the S06-B photo check" deferral (intake §2
    #      scene03 (e)) is still live, and K5/infra_kit is a Lane-1 dependency this lane
    #      does not have. Flipping it to False would *permit* infrastructure the scene must
    #      not have and would delete the code-enforced guard that keeps it out.
    #   -> `pave.module` is now **(0.200, 0.100)** — truthful, because the crest IS laid in
    #      blocks. It is a measured no-op in prims: the only readers of `pave["module"]`
    #      are `build_patch_field` and `build_relaid_units`, and this scene builds neither.
    #   -> **`pave.joint` stays None, declined with coordinates rather than by taste.**
    #      `joint="interlock"` composes `build_joint_grid` from the profile's
    #      `step_x = 3.0` as **x = const grooves spanning the whole y range**, i.e. lines
    #      running **parallel to the drop edge at x = 0** — measured at x = −12.000 /
    #      −9.000 / −6.000 / −3.000 on the old region and x = −3.000 on the paved band,
    #      the last of which lands on the d10 GT-E2 E-band boundary [0.7d, 2.2d]. And the
    #      archetype is wrong anyway: flexible block paving has **no 3 m 시공줄눈** — its
    #      joints are the 3.5 mm sand joints between every unit (`joint_interlock_w`,
    #      `ground_kit.py:250`), which the `paving_interlock` map delivers geometrically
    #      free at `scale_m` 1.2 = the measured 200 mm block long side.
    # z: elements sit on the **paving top** (crest_walk proud, +1.5 mm).
    #   Using the grass top (0.0) instead would bury every element on the walk,
    #   which is exactly the burial class the pilots found (spec §1.1).
    # [v7 · 03-A + user ban "바닥에 이상한 사각형 무늬는 웬만하면 다 제거해"]
    #   **`patch` 8 -> 0, and the site list is deleted with it.** The old rationale ("trampled
    #   bare soil at the gravel/grass margins, not asphalt repairs") does not survive contact
    #   with the shape: `build_patch_field` draws **axis-locked rectangles** (DEC-3), and
    #   trampled soil has no straight edge. `w3_intake_v2_images.md` §3(ii) states the rule
    #   the whole sweep runs on — a rectangle on the ground is legitimate only as a **saw-cut
    #   asphalt repair on an asphalt road** — and this crest is grass + gravel, so the legitimate
    #   count here is **0**, not the "1 or 0" the table allows the paved half of P13.
    #   What carries the trampled-soil intent instead: the `stain` row, which has been
    #   **irregular lobes** since DEC-1 (`ground_kit.py:671`, `:1250-1298`), plus the wear lane
    #   and the edge break. Nothing is left un-modelled by the deletion.
    #
    #   **GT-24's `levee_paved` extension reaches this scene NOWHERE — measured, not assumed.**
    #   The SB closure batch deleted `("patch", 4)` from the P13 profile row, and `ground_kit.py`
    #   `:1984-1986` records the reach check itself: *"`scene03` authors its own `surface` row
    #   (8 patches, `scene03_riverbank.py:911`) and is **unreachable**; `scene17` does not
    #   override and loses 4 `Patch_*` prims."* The module-snap half is inert here too: this
    #   scene overrides `pave=dict(module=(None, None), ...)`, so its patches never snapped to
    #   the 인터로킹 200 cell in the first place. The 8 patches therefore leave by **this
    #   scene's own decision under the user ban**, and the inherited delta from GT-24 is **nil**.
    #   **[P03] That deletion is NOT re-opened by the paving.** GT-24's vocabulary rule is
    #   the reason: on unit paving a real repair is a *re-laid unit group*, never a saw-cut
    #   rectangle — and a promenade in its first decade has no cause for one (the GT-40
    #   scene08 precedent, where `relaid` was refused for exactly this reason).
    # **[P03] region x0 −12.0 -> −5.4 = the paved band's outer edge.** Measured, on a CPU
    #   A/B of `plan_ground` (prims 17 -> 17, elements 17 -> 17, so this buys nothing and
    #   costs nothing in count): with the old 12 m region **4 of the 8 `stain` decals landed
    #   at x <= −6.254**, i.e. on mown grass, floating 1.5 mm above turf; with the new
    #   region every stain lands on paving, where a dirt/water stain has a surface to be on.
    # wear lane runs **along the river (+-Y)**, i.e. along the walking route on
    #   the crest, offset to x=-3.50 so it falls inside the d5 near window
    #   (x -4.44..-3.00). Length is capped at |y| <= 10 because the band is
    #   straight while the walk follows the meander. **[v7] Re-measured against A1=10.0:
    #   |dx(10)| = 1.638 m** (was 0.95), so at |y|=10 the 4.0 m paving spans x −6.638…−2.638
    #   and the straight 0.90 m wear band (−3.95…−3.05) is still wholly inside it, with
    #   1.412 m to spare at the inner edge. `wear_y` therefore stays at 10.
    #   **[P03] `wear_x` stays −3.50** rather than moving to the new centre (−3.00): the
    #   desire line on a levee crest with an *unguarded* 3.2 m drop hugs the landward half,
    #   and −3.50 keeps the lane inside the d5 near window it was placed for.
    # NO silt band. Spec §5.7 lists one, but the crest top (z=0) is 3.35 m
    #   above the water line (riprap bottom -3.35): silt deposition belongs to
    #   the beach at z=-3.2, which is outside every h0.3 near window.
    # [v7] `break_y` 3.0 -> 2.4. The edge break is a STRAIGHT strip laid on a MEANDERING
    #   seam, so its half-length is bounded by |dx(y)| <= 0.10 m (the half width of the
    #   transition band). A1=6.0 gave |dx(3.0)| = 0.088 m; A1=10.0 gives 0.148 m — off the
    #   seam. Solving 10.0*(1 - cos(2*pi*y/110)) = 0.10 gives y = 2.477, so 2.4 is the
    #   largest 0.1-rounded value that still holds: |dx(2.4)| = 0.0946 m (re-measured [P03]).
    #   **[P03] The seam the break sits on moves x −4.0 -> −5.4** (the paving/turf edge is
    #   now the band's outer face); `break_y` is unchanged because the bound above depends
    #   only on |dx(y)|, not on x.
    gkit=dict(x0=-5.4, half_y=3.0, wear_x=-3.50, wear_y=10.0,
              break_y=2.4),
    slope=dict(x0=0.0, z0=0.0, run=7.0, drop=3.2, thick=0.4,   # 20-step match: run 7.0
               y0=-40.0, y1=40.0),
    # corridor bounding stairs + side trim (slope cut width). [v5.1] band_gap = the inner
    #   limit of the meandering slope bands - so that even with rotation drift (+-0.044) it
    #   tucks under the trim (0.75~0.95), 0.95 -> 0.88 bites 0.07 in. Stair side 0.75 is off limits.
    corridor=dict(y0=-0.95, y1=0.95, band_gap=0.88),
    # --- stairs : 20 steps (drop 3.2 = matches slope·beach, run 7.0) ---
    stairs=dict(x0=0.0, riser=0.16, tread=0.35, nsteps=20,     # run 7.0, drop 3.2
                y0=-0.75, y1=0.75, base_z=-3.6, z_top=0.0),
    # v4-A4: margin 0.3 -> 0.0, z0 0.05 -> 0.02. The trim beam used to stick out to
    #   x~−0.13, leaving two concrete stubs about 0.10 m above the levee crest top.
    trim=dict(width=0.2, drop=3.2, z0=0.02, thick=0.4, margin=0.0),
    # --- beach : x 7.0..18.0, z=-3.2, two dirt|grass strips (border x=12) ---
    #     widened to y +-40 to remove the far-view sky hole (near terrain stays +-10)
    beach=dict(x0=7.0, x1=18.0, y0=-40.0, y1=40.0, z_top=-3.2,
               thick=0.4, split_x=12.0),
    # v4-A3: lower trail re-laid river-parallel (Y axis). The old x 7..18 x y +-1.2 was
    #   a walk-logic error: the only path off the stairs ran straight into the water.
    beach_path=dict(x0=9.4, x1=12.4, y0=-40.0, y1=40.0, z_top=-3.18,
                    thick=0.12),
    # v4-D4 cycle track road markings (reads instantly as a Han river beach)
    path_lines=dict(edge_x=(9.6, 12.2), w=0.12, z_top=-3.175, thick=0.02,
                    mid_x=10.9, dash_len=2.0, dash_step=8.0, dash_y0=-32.0,
                    dash_n=9),
    # --- riprap strip : low sloped beam between water and beach ---
    riprap=dict(x0=17.0, z0=-3.2, run=1.2, drop=0.15, thick=0.3,
                y0=-40.0, y1=40.0),
    # --- water surface & far bank (effective waterline exposed at s~18) ---
    # v4-B2: eases the uniform cyan slab (misread as a swimming pool) - 3-band roughness variation
    # [v5.1] channel narrowed (far_bank s0 40->34, water s1 40->36 - 34~36 is the
    #   overlap tucked under the far bank). Effective water s 18.2..34 = 15.8 m.
    #   meander amplitude 14.8 / channel width 15.8 = 0.94 -> meets the required "1~2x" floor.
    # **[v7 R03-1 — this SUPERSEDES the v5.1 narrowing, per `w3_intake_v2_images.md` §7.**
    #   User (2nd review): *"Scene3 도 참조, 강 뷰를 좀 더 넓히는걸 추천"*; the ruling asks for a
    #   channel **wider than v4** to match G3, where the water holds the whole right third of
    #   the frame and runs to the vanishing point.
    #     far_bank s0  34 -> 52 · water s1  36 -> 54  (52..54 is the overlap tucked under the bank)
    #     effective water s 18.2..52 = **33.8 m**  (v5.1 15.8 · v4 22.5)
    #   The waterline itself (s 18.2, the riprap toe) does NOT move, so the riprap, the reed
    #   band, the water gauge and the whole near bank are untouched — the widening is spent
    #   entirely on the far side, which is where G3 puts it.
    #   amplitude/width = 24.79 / 33.8 = **0.73** (was 0.94). The brief's "1~2x" and the user's
    #   "widen it" cannot both be honoured — the amplitude is already at 35.6 deg of bank
    #   tangent and 45 deg is oxbow — so the ruling decides, and the shortfall is declared
    #   rather than engineered away.
    # [GT-129] `end_cap` — the terminal-seg end cap (see `river_end_geom`). A water surface
    #   can never show a castellated silhouette, and the last seg's yaw makes one: the cap is
    #   an un-yawed slab per water band, laid on the tooth row so the far edge is ONE straight
    #   world segment. `dz` puts it 3 mm below its own band (> the 1.5 mm seg stagger), so the
    #   meandering band always wins where the two overlap and only the notches read the cap;
    #   `tuck` hides the cap's near face under the water body, `over` carries the straight edge
    #   past the longest tooth. Nothing here moves the water z, the waterline (s 18.2) or any
    #   surface a judging camera reads.
    water=dict(x0=16.5, y0=-40.0, x1=54.0, y1=40.0, z=-3.35,
               bands=((16.5, 26.0, 0.06), (26.0, 38.0, 0.10),
                      (38.0, 54.0, 0.15)),
               #   Measured on this scene's own numbers: last seg yaw 32.27°, so the cap
               #   spans y 46.483…49.944 against a tooth row of 46.827…48.849 — 0.34 m of
               #   live water over the near face, 1.10 m of straight edge past the longest
               #   tooth (screen clearance −0.42/−0.66/−0.57 % of frame half-height on
               #   river_along/meander_air/bank_oblique = 2.3…3.6 px; `over` 0.50 halves that
               #   to ~1.3 px, which the caps' 5.5 mm depth under the water no longer clearly
               #   dominates at the grazing river_along horizon).
               end_cap=dict(tuck=0.25, over=1.00, dz=0.003)),
    far_bank=dict(x0=52.0, x1=88.0, y0=-40.0, y1=40.0, z_top=-3.2, thick=0.4),
    # v4-B3/D11: 3 far_hedge slabs (60 m grass-texture strips) drew regular hatching stripes
    #   on the horizon and read as a printed backdrop -> replaced by 7 tree lines.
    # [v5.1] The waterline moved in to s34, so the tree line moves to s38. An even 10 m
    #   spacing would break global convention 3 (no grids), so spacing·offset are irregular.
    # [v7] Far bank at s52 -> the tree line rides it out to s56 (same +4 m stand-off). The
    #   irregular per-tree dx offsets are carried over unchanged (convention 3).
    # **[GT-83] One entry moves: cy −31.0 -> −41.0.** With the raised crossing at deck centre
    #   y −23.0 the deck occupies world y −34.8…−25.8 where it passes s 56 [measured], and a
    #   `belt=True` far-bank crown tops out at −3.20 + 4.2×1.25 + 1.1 = **+3.15 m**, i.e.
    #   1.35 m ABOVE the +1.80 soffit — the tree would have grown through the deck. At −41.0
    #   the crown centre stands **6.59 m** clear of the deck's south edge. Count stays 8 and
    #   the stand-off from the bank line is untouched; only the along-bank spacing opens to
    #   18.5 m at the bridgehead, which is where a real bank clears its trees anyway.
    far_trees=[dict(cx=56.0 + dxo, cy=cy) for dxo, cy in
               ((0.0, -41.0), (1.8, -22.5), (-1.2, -13.0), (2.4, -3.0),
                (-0.6, 7.5), (1.5, 16.0), (-1.8, 27.5), (0.9, 35.0))],

    # --- props ---
    # both sides of the spur (blocks vehicle entry) - [v5.1 global convention 2] bollards are functional.
    #   The placement rationale (facing the stair entry) stands, but height 0.75 -> 0.90
    #   (statutory 0.8~1.0m) with a white reflective band on top. A 2-post gate, not a decorative colonnade.
    # [v6 ruling (3)] "in the levee_walk near view the two posts take up 1/3 of the frame
    #   height - the entry gate becomes the star of the main cut". Retreating along −X would
    #   bring them nearer the camera (−6) and enlarge them, so instead **spread them
    #   off the sight axis (laterally) and retreat only to the road-spur line (s −1.0)**; 1.0 m outside the spur edge (y +-1.2).
    #   Azimuth from levee_walk |az| 14.8 deg -> 25.3 deg (frame edge).
    # **[v7 · 03-B] The v6 lateral spread is REVERSED and the pair lands on the line it
    #   defends.** `w3_intake_01_05.md` §03-B measured the defect: the posts sat at y = ±2.2
    #   against a spur edge at y = ±1.2, i.e. **1.0 m outside**, standing on turf — *"they read
    #   as free-standing monuments"*. G-3 / PE-7 is absolute: a bollard stands **on** the
    #   보도·차도 경계 line it defends, offset 0.00 m, and the frame-occupancy problem the v6
    #   ruling solved is to be solved by moving the camera or the spur, never the bollard.
    #     cx −1.2 -> **−1.0** (the spur entry line, x=−1.0) · cy ±2.2 -> **±1.2** (the spur edge)
    #   Dimensions were already lawful and are untouched (h 0.90 ∈ [0.8,1.0] · Ø0.15 ∈
    #   [0.1,0.2] · reflective band z 0.74–0.84, 교통약자법 시행규칙 별표2 제7호).
    # **The third, centre post of the 03-B build spec is DECLINED — with the measurement, not
    #   by preference.** The spec asks for a row of 3 at a 1.2 m interval across the 2.4 m
    #   spur (inside "1.5 m 안팎"). The centre post would stand at (−1.0, 0.0): the h0.3/h0.9
    #   **d2 judged eye is at (−2.0, 0.0)**, so the post lands **1.00 m dead ahead on the
    #   sight axis**, spanning z 0…0.90 — it fills the near window and destroys the very cut
    #   the drop label is read from. The judge presets are frozen this window, so the spec's
    #   own escape hatch ("move the camera or the spur") is not available, and H16 forbids
    #   trading a live gate for a dressing refinement. Declared deviation: post interval
    #   **2.4 m** against 별표2's "1.5 m 안팎". Re-open with the renumbering round, where the
    #   preset axis can move. 점형블록 in front stays default-OFF (supervisor ruling,
    #   `user_feedback_v5_1.md` §7) — restated here so it is not re-litigated.
    bollards=[dict(cx=-1.0, cy=1.2), dict(cx=-1.0, cy=-1.2)],
    bollard=dict(h=0.90, r=0.075, band_z=0.74, band_h=0.10),
    # v4-D7: benches 1 -> 4 (2 levee crest + 2 beach). (cx, cy, base_z, yaw)
    # [v5.1 global convention 3] The old layout was 2 symmetric y=+-6 pairs (a grid) -> now
    #   asymmetric against anchors (inside the pergola, beside a tree, walkway edge) + non-integer yaw.
    benches=[(-6.5, 4.4, 0.0, 5.0),        # inside the pergola (s −8..−5, y 3..6)
             (-6.4, -7.6, 0.0, 172.0),     # 1.75 m beside the levee-crest tree (−8,−7)
             (12.9, -4.6, -3.2, 93.0),     # 0.5 from the beach walkway edge (s12.4)
             (15.2, 6.4, -3.2, 187.0)],    # 1.60 m beside the beach tree (16,5)
    # v4-B1 [critical look]: slope shrubs were axis-aligned boxes, so gradient 0.457 x half-width 0.6 ->
    #   0.37 buried upstream / 0.17 floating downstream. Switched to build_slope (sloped slab)
    #   with 3 overlapping slabs per clump (size·height variation), which also kills the blocky look.
    # [v5.1 re-fix] That same 3-slab stack was identified in the scene04 v5 ruling as the
    #   'angular slab poking out of the grass' (same implementation). Here too it becomes
    #   **3 overlapping flattened ellipsoids** - axis-aligned solids of revolution have no
    #   cut face, and the gradient enters only via placement height (slope_z). Ground: rz·embed >= rx·grad(0.457):
    #     0.34x0.55=0.187 >= 0.40x0.457=0.183 ✓ (rx capped at 0.40)
    # **[v7 · 03-D] These blobs are no longer what is built.** The carried item is *"shrub /
    #   bush replacement"* — the slope clumps are the last never-replaced procedural
    #   vegetation in this scene — and K4(b) landed the instrument: `sc.place_shrubs` stands
    #   real shrub USDs and draws **one species per bed** (S-2). The 6 clump centres and the
    #   3 per-clump offsets below are **kept as the placement grammar** (they are the authored
    #   composition, and re-inventing coordinates would be a change nobody asked for): they
    #   now generate 18 shrub *points*, and the ellipsoids survive only as the assets-absent
    #   fallback (`build_dressing`, scene10 precedent). See `hedge["target_h"]` for the one
    #   number that is genuinely new, and why it is not G3's number.
    hedges=[dict(cx=1.5, cy=-4.0), dict(cx=3.0, cy=6.0),
            dict(cx=2.2, cy=8.0), dict(cx=4.0, cy=-7.0),
            dict(cx=1.8, cy=-11.5), dict(cx=3.4, cy=13.0)],
    hedge=dict(embed=0.55,
               blobs=((0.00, 0.00, 0.40, 0.62, 0.34),
                      (0.30, 0.52, 0.30, 0.46, 0.25),
                      (-0.26, -0.44, 0.33, 0.40, 0.29)),  # (dx,dy,rx,ry,rz)
               # [v7] `hedge_evergreen` = Holly (h 1.526) / Privet (h 1.114), one drawn for
               #   the whole band. Both are evergreen broadleaf, so the summer pin of G3 is
               #   satisfied without a seasonal strip, and neither carries a flower prim
               #   (K4-F1's Rhododendron loss does not touch this scene).
               species="hedge_evergreen",
               # **target_h 0.85 is set by the scene's IDENTITY, not by G3.** G3's slope mass
               #   is ~1.5 m. Here the highest bed sits at s=1.5, i.e. slope_z = −0.686, so a
               #   1.5 m shrub tops out at **+0.814 m — 0.514 m ABOVE the h0.3 judged eye** and
               #   would cut into the water band that is this scene type's ONLY drop evidence
               #   ("no railing × water-surface anchor"). At 0.85 m the same crown tops at
               #   **+0.164 m, 0.136 m BELOW** that eye. The instrument outranks the reference
               #   photo on this one number (H16); the shortfall is declared, not hidden.
               target_h=0.85),
    # 2 beach trees (crown top z~-0.15, below the levee-crest eye height 1.5 - series (3) anchor)
    trees=[dict(cx=10.0, cy=-4.0), dict(cx=16.0, cy=5.0)],
    # v4-D10: trees 2 -> 8 (3 more on the levee crest + 3 on the beach)
    # **[GT-83 pass 3] one entry moves: (9.0, −10.0) -> (13.4, −6.0).** The near approach's
    #   transition chords pass 3.27 m from that trunk, i.e. the tree stood **1.23 m inside the
    #   deck edge** [measured]. It did not physically intersect — a `trunk_h` 2.2 crown tops
    #   at −3.20 + 2.2×1.25 + 1.1 = **+0.65** against a soffit of +1.78, so 1.13 m of air —
    #   but a crown pinched under a deck edge is exactly the un-natural reading this pass
    #   exists to remove. At (13.4, −6.0) it stands **3.58 m clear of the deck edge**, on the
    #   둔치 grass strip between the cycle track (s ≤ 12.4) and the reeds (s ≥ 16.0), 2.08 m
    #   clear of the bridgehead apron and 1.43 m from `benches[2]` — which is the scene's own
    #   "bench beside a beach tree" idiom (`benches[3]`), not a new one. Count and species
    #   are unchanged; the far-bank stand is untouched.
    trees_extra=[dict(cx=-8.0, cy=-7.0, gz=0.0), dict(cx=-8.0, cy=7.0, gz=0.0),
                 dict(cx=-14.0, cy=0.0, gz=0.0),
                 dict(cx=13.4, cy=-6.0, gz=-3.2), dict(cx=14.5, cy=-24.0, gz=-3.2),
                 dict(cx=9.0, cy=12.0, gz=-3.2)],

    # === v4-D context dressing (so it reads as a river levee) ===
    # D1 [top priority] distant crossing - the river axis is Y, so it crosses along X.
    # **[GT-83] The v7 arrangement was judged purposeless in `pt_noon_levee_walk`.** Measured
    #   pre-state: deck top −0.20 m (0.20 m BELOW the levee crest), soffit −1.00 m = only
    #   2.35 m over the water, the near end stopping in mid-air at s≈10 over the 둔치 with an
    #   open cut face, and the nearest deck corner projecting at **u/half 0.34** — a low slab
    #   crossing the middle of the main cut and landing on nothing. Three changes:
    #   (1) **Overpass clearance.** soffit −1.00 -> **+1.80** [computed: deck_top 2.90 −
    #       deck_thick 1.10]. Clearance **5.15 m over the water (−3.35)**, **5.00 m over the
    #       둔치 (−3.20)**, **4.98 m over the 둔치 cycle track (−3.18)** — at or above the
    #       4.5 m 건축한계 a road route passing over another route has to hold.
    #   (2) **Off the levee-walk axis.** Deck centre y −18.0 -> **−23.0**. [computed, all
    #       deck/abutment corners projected through `build_views()`] the in-frame band in
    #       `levee_walk` moves u/half **[0.34, 1.00] -> [0.85, 0.92]**: nothing of it is left
    #       inside 85 % of the frame half-width, where it used to reach in to 34 %, and every
    #       point of it sits above the frame centre (v/half −0.11…0.25 -> **0.31…0.73**). The judged grid
    #       frames follow: u/half min **0.36 -> 0.87** at h0.3_d5, **0.28 -> 0.77** at
    #       h0.3_d10, **0.28 -> 0.76** at h1.8_d10 (same 164-point edge sampling on both arms).
    #       **−23.0 is bounded, not free.** `bank_oblique`'s frozen eye (s40, y−26, z8) sits
    #       2.12 m from the deck centreline and **4.00 m above the parapet top** [measured],
    #       so the deck cannot be raised further and its centre cannot travel into
    #       y −20.7…−29.8 without putting a judging camera inside the structure.
    #   (3) **Both ends land on a bank.** Each authored deck end is the CENTRE of a bank-seat
    #       abutment (`abut_t` 2.20 m), so the end face is buried 1.10 m inside a founded
    #       block that runs from a spread footing 0.25 m proud of the bank up to the parapet
    #       top. Footprints in the meander cross-section frame [measured]:
    #         near abutment **s 12.84…16.49 on the 둔치** — 0.44 m clear of the cycle track
    #           (s ≤ 12.4), short of the riprap (s ≥ 17.0);
    #         far  abutment **s 58.01…61.58 on the far bank** — 6.0 m in from the bank line
    #           (s 52), 4.4 m short of city block A's facade (s 66).
    #   Piers 7 -> **3** on a uniform 10.40 m bay (the equal division of the 41.6 m
    #   abutment-to-abutment span). A 5.50 m tall support line carries fewer, taller columns,
    #   and all three stand in open water (column s 24.55…49.87 against water s 18.2…52)
    #   [measured]. Each is a hammerhead T-pier (column + cap), so a round column no longer
    #   stabs a flat soffit. G3's "regular pier line" reading is kept; only the pitch is
    #   re-derived from the shorter span.
    # ---------------------------------------------------------------------
    # **[GT-83 pass 2] Buildability pass — the crossing is finished as a piece of engineering.**
    #   User verdict on `pt_noon_meander_air` (probe `260806_w3_s03probe`): *"make it more
    #   REALISTICALLY IMPLEMENTABLE"*. Three named defects, and what each one gets:
    #   (a) *the near abutment is a featureless 7 m concrete bunker on the lawn* -> **[pass 3]**
    #       it is not an abutment at all any more: the carriageway runs over it, so it is a
    #       **wall pier**, `abut_z0` −3.45 up to the soffit +1.85 = **5.30 m** [computed:
    #       wp_top 1.85 − abut_z0 −3.45] against GT-83's 7.45 m, of which **5.05 m** stands
    #       above the 둔치 (−3.20) and only **3.40 m** above the stone scour apron (−1.55),
    #       broken twice more by belt courses. The members a bridgehead needs (bearing
    #       pedestals · back wall · approach slab · parapet end posts) moved with the job, to
    #       the two END bridgeheads where the ribbon actually stops.
    #   (b) *the deck stops at the abutment — a road bridge to nowhere* -> a **23.0 m graded
    #       approach viaduct** now carries the carriageway past the far bridgehead out to the
    #       far bank's modelled edge (`far_bank.x1` = s 88). See `appr_len` below for the
    #       measured length and the NEAR-side refusal, which is geometric, not a preference.
    #   (c) *deck + parapet read as one thick white slab* -> the side profile is split into
    #       **thin slab fascia (0.38) / recessed girder band (0.72) / drip nose / parapet
    #       (0.94) / coping (0.16)**; `deck_thick` and `parapet_h` are unchanged, so
    #       **parapet top stays at exactly +4.00** and `bank_oblique`'s frozen eye keeps its
    #       4.00 m clearance to the digit.
    #
    # **[GT-83 pass 3] The NEAR-side approach is BUILT — as a curved southward viaduct.**
    #   The pass-2 refusal was argued for the STRAIGHT continuation, and those coordinates
    #   stand: run the carriageway straight on down the deck axis (bearing −25.09°) and it
    #   crosses the drop edge x = 0 at world y −8.77 still +2.26 m above the levee crest,
    #   severs the crest promenade over world y −12.39…−2.17 with its near edge reaching
    #   **y −0.95 — the hazard corridor boundary itself — at x = −8.00**, sweeps `meander_air`
    #   u/half +0.44 → −1.18, and only touches down at world (−41.0, +10.4). That road is
    #   still not buildable here.
    #   **The 08-06 ruling ("근측 접속도로 어떻게든 만들어봐") is answered by the alternative the
    #   refusal never evaluated: turn south and run along the 둔치.** The ribbon leaves the
    #   bridgehead on the deck axis, turns **90.0° left over a 13.0 m transition** and then
    #   holds the meander frame at **s 5.29** down to the modelled ground's south edge. What
    #   that buys, all measured on this scene's own bands:
    #     · **The drop edge is never crossed.** The deck's whole corner envelope is
    #       **s 0.33…14.84** — it stops **0.33 m short of s = 0** and **1.33 m short of the
    #       promenade's outer edge (s −1.0)**. The hazard corridor (y ±0.95) is 17 m away.
    #     · **Nothing climbs.** The 둔치 sits at −3.20 and the levee slope at −0.457·s, so the
    #       ribbon descends the whole way and still clears everything it crosses: minimum
    #       soffit clearance **1.40 m** (over the top of the levee slope at the far south end,
    #       grass, walked by nobody) and **4.94 / 4.04 / 3.82 / 3.61 m** at the four piers.
    #       Parapet top never exceeds the main deck's +4.00, so `bank_oblique`'s frozen eye
    #       keeps its 4.00 m clearance to the digit.
    #     · **It stays out of the cut the user cleared.** `levee_walk` sees it only at
    #       u/half **+0.91…+0.99** (8 of 131 sampled points, at the extreme right edge);
    #       `bank_oblique` at **−0.99…−0.88**; the h*_d2 judged frames not at all. In
    #       `meander_air` it occupies u/half **−0.48…+0.45** at v/half −0.90…−0.14 — the lower
    #       band, curving out of the bottom edge — instead of the +0.44 → −1.18 sweep the
    #       straight road would have cut across the whole frame.
    #   **The cost is measured and NOT hidden: `river_view_selfcheck`'s meander_air occlusion
    #   goes 24.4 % → 38.9 %, over its own 35 % criterion.** See that function for the full
    #   note — the threshold is deliberately left untouched.
    #   **Declared shortfall — curve radius.** The 90° turn costs ~1.13·R of cross-section
    #   offset, so holding the ribbon on the 둔치 caps the transition at 13.0 m of arc, i.e.
    #   **R_min 7.53 m** against the 15 m that 도로구조규칙 asks of a 20 km/h 연결로. Raising R
    #   to 15 m would put the alignment at s −2.4 and the deck squarely over the promenade.
    #   The radius gives way, the promenade does not, and the shortfall is declared here.
    #
    # Far-approach numbers, all measured in this scene's own frames:
    #   `appr_len` **23.0 m**. The deck's own corners leave the modelled far bank
    #   (s > `far_bank.x1` = 88, or y < −47.5) at t = 26.4 m and the end bridgehead's footing
    #   corners at t = 25.5 m, so 23.0 puts the end block at t 21.9…24.1 — **1.4 m inside the
    #   ground it stands on**, with the approach slab reaching t 24.3.
    #   `appr_grade` **2.5 %** (0.575 m over the run; 도로구조규칙 allows 7 % at 60 km/h, so this
    #   is a gentle real profile, not a token). Deck top at the end **+2.325**, soffit +1.225,
    #   i.e. **4.43 m over the far bank** [computed: 1.225 − (−3.20)].
    #   Clearance to city block A: the approach's coping line passes **2.04 m** from A's nearest
    #   world corner (56.97, −28.16) [measured, both rot groups composed]. That is *wider* than
    #   the pre-existing gap — the far bridgehead itself, being 10.20 m across, already stands
    #   **1.49 m** from the same corner — so the approach introduces no new tightest pair and
    #   block A is left where v7 put it (backdrop identity outranks a 3 m nudge).
    # ---------------------------------------------------------------------
    bridge=dict(x0=16.4, x1=58.0, y0=-27.5, y1=-18.5,
                deck_top=2.90, deck_thick=1.10,          # soffit +1.80
                parapet_h=1.10, parapet_w=0.40,
                wear_t=0.07, joint=0.02,                 # carriageway course + burial depth
                # --- [GT-83 p2] deck side profile: 1.10 total, split not thickened ---
                girder_h=0.72, girder_in=0.30,           # 0.38 fascia over a recessed girder band
                drip_h=0.16, drip_out=0.07, drip_in=0.04,  # drip nose under the fascia
                cope_h=0.16, cope_out=0.05,              # parapet coping (top stays +4.00)
                pier_r=1.10, pier_x=(26.8, 37.2, 47.6), pier_z0=-3.70,
                cap_t=2.80, cap_w=7.40, cap_h=0.95,      # hammerhead cap under the soffit
                cap_bite=0.05,                           # cap top sunk into the (graded) soffit
                abut_t=2.20, abut_over=1.20, abut_z0=-3.45,
                foot_t=2.60, foot_over=1.60, foot_z0=-3.55,
                foot_top=-2.95,                          # 0.25 m proud of the bank (−3.20)
                # --- [GT-83 p2] bridgehead members (shared by both heads) ---
                bear_h=0.35, ped_t=1.00, ped_w=1.30, ped_y=3.00,   # bearing shelf + pedestals
                back_t=1.18, back_in=0.12, back_w_off=-0.40,       # back wall (흉벽)
                post_t=1.30, post_w=0.55,                          # parapet end post
                slab_t=0.30, slab_out=0.10, slab_wear_in=0.08,     # approach slab (접속슬래브)
                belt_h=0.14, belt_out=0.05, belt_dz=(0.55, 1.95),  # belt courses on the seat
                apron_out=0.80, apron_xout=0.05, apron_top=-1.55,  # stone scour apron (near only)
                # --- [GT-83 p2] far approach viaduct ---
                appr_len=23.0, appr_grade=0.025, appr_pier_x=(7.7, 15.4),
                pier_far_w=8.40, pier_near_w=9.60,       # both heads become wall piers
                # --- [GT-83 pass 3] near approach: curved southward viaduct -----------
                # The alignment is a **chord polyline**, not an arc primitive, because every
                #   river-parallel element in this scene is already chorded (`river_band`) and
                #   a chord run can be built by the same `build_slope` section as the deck.
                # `napp_deltas` — per-chord heading change. 11 chords, **eased at both ends**
                #   (4.5 / 9×9 / 4.5): the entry step is halved so the joint with the frozen
                #   main deck kinks by only **2.25°**, and the exit step is halved into the
                #   river-parallel run. Max inter-chord kink **9.00°**, mean 7.03°.
                # `napp_curve_len` 13.0 m — the binding number. s_hold = 14.50 − 1.13·R and the
                #   deck must stay off the promenade, so this is the longest (largest-radius)
                #   transition the cross-section allows: 13.0 m of arc -> **s_hold 5.29**,
                #   R_min 7.53 m. 14.5 m would give R 8.4 but drop the deck edge to s −0.72.
                # `napp_ypar` — the river-parallel run's y stations, held at s_hold in the
                #   meander frame so the ribbon follows the same bend as the bands under it.
                #   It ends at y −45.8, **1.7 m inside** the modelled ground (y −47.5).
                # `napp_grade` 2.0 % with an 8.0 m parabolic `napp_vlen` off the level deck —
                #   the grade is 0 at the bridgehead and only reaches 2.0 % 8 m out, so there
                #   is no pitch step where the ribbon leaves the frozen span.
                # `napp_lead` 1.30 m — chord 0 is extended BACK past the deck end (> abut_t/2
                #   1.10), so the main deck's end face is buried inside it.
                # `napp_pier_j` — chord joints carrying a T-pier. Joint 6 rather than 5:
                #   at joint 5 the Ø2.20 column would span s 7.41…9.61 and clip the 둔치 cycle
                #   track (s ≥ 9.4) by 0.21 m; at joint 6 it spans **6.45…8.65**, clear by
                #   0.75 m [measured]. Joints 11/13/15 all sit at s 5.29.
                napp_curve_len=13.0,
                napp_deltas=(4.5, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 4.5),
                napp_ypar=(-23.0, -28.0, -33.0, -38.0, -42.5, -45.8),
                napp_grade=0.020, napp_vlen=8.0, napp_lead=1.30,
                napp_pier_j=(6, 11, 13, 15),
                # south end bridgehead, narrowed: the corridor between the promenade (s −1.0)
                #   and the cycle track (s 9.4) is 10.4 m wide and the standard head is 10.20,
                #   which would leave 0.1 m either side. At −1.80/−1.40 the seat is 7.20 and
                #   the footing 7.60, measuring **s 1.59…8.95 / 1.37…9.15** -> 0.45 m and
                #   0.25 m of clear ground. The 9.00 m deck simply cantilevers over it, which
                #   is what a deck does.
                send_over=-1.80, send_foot_over=-1.40),
    # D2 far-side city silhouette (horizon closure + river-width scale anchor). base_z=far_bank top
    # [v5.1] Pulled in to s 55->48 with the narrower channel (far beach stays 14 m wide), and
    #   each block goes in its own rot_group for the meander tangent + placement jitter (yaw +-4 deg).
    # [v7] The blocks ride the far bank out: facade s 48 -> 66 (unchanged 14 m of far 둔치
    #   between the bank line and the first facade). Pushing them back 18 m without touching
    #   the heights would shrink the skyline by a factor 54/72 = 0.75 from the levee_walk eye,
    #   i.e. the widening would COST the horizon closure G3 relies on. Heights are therefore
    #   re-derived, not left: h x 1.45~1.56 with the floor count kept at a Korean 2.90 m
    #   storey (A 7 -> 11 floors, B 5 -> 8, C 8 -> 14). Net angular height vs v6: +9~17 %,
    #   i.e. slightly MORE horizon closure than before, which is the direction G3 asks for
    #   (its far bank is a continuous 한강변 apartment line). Honest limit: G3's towers read
    #   as 20~25 storeys and these are 8~14 — a full backdrop rebuild is not in this lane.
    city=dict(
        A=dict(x0=66.0, x1=73.0, y0=-30.0, y1=-14.0, h=31.9, floors=11,
               axis="x", facade_x=66.0, face_dir=-1.0, base_z=-3.2, jyaw=3.5),
        B=dict(x0=66.0, x1=75.0, y0=-6.0, y1=8.0, h=23.2, floors=8,
               axis="x", facade_x=66.0, face_dir=-1.0, base_z=-3.2, jyaw=-4.0),
        C=dict(x0=66.0, x1=71.0, y0=16.0, y1=30.0, h=40.6, floors=14,
               axis="x", facade_x=66.0, face_dir=-1.0, base_z=-3.2, jyaw=2.5),
    ),
    # D5 reed band (waterline transition) - [v5.1] old 5-part axis-aligned boxes -> meander band
    #   (it must follow the waterline curvature to read as 'riverside reeds'). segs key dropped.
    # **[GT-83] `y_gap` is new.** The near bridgehead now stands on the 둔치 at s 12.84…16.49,
    #   which overlaps this band (s 16…17) over world y −19.53…−9.57 [measured]. Reeds are a
    #   continuous band, so without a cut they would grow through the abutment. The gap covers
    #   the abutment's own world-y footprint (−19.53…−8.83) with **0.77 m / 1.33 m** to spare;
    #   the upper end is put exactly on a `river_segments` boundary (seg_dy 5.0 from y0 −47.5
    #   -> …, −12.5, **−7.5**, −2.5, …) so that seg is dropped whole instead of leaving a
    #   sub-metre stub. Band 19 -> 17 segs. Nothing else in the band moves, and a cleared
    #   bridgehead is the real-world state anyway.
    # **[GT-83 p2] the lower end opens −20.3 -> −21.0.** The bridgehead now carries a stone scour
    #   apron 0.80 m proud of the footing on each flank, whose rotated corners reach world
    #   y **−20.28…−8.08** [measured]. Against the old gap that left only 0.02 m at the lower
    #   end — inside the 1.5 mm stagger's own noise — so reeds would have grown out of the
    #   stone. −21.0 restores a **0.72 m / 0.58 m** margin. The seg partition is untouched
    #   (both −20.3 and −21.0 fall inside the same −22.5…−17.5 seg, which is clipped either
    #   way), so the band stays at **17 segs** and the upper end keeps its exact seg boundary.
    reeds=dict(x0=16.0, x1=17.0, h=0.9, base_z=-3.2,
               y_gap=(-21.0, -7.5)),
    # D6 levee-crest cycle track centre line + distance markers
    # **[v7] The centre line is DELETED** — three independent reasons, any one sufficient:
    #   (a) the user ban on ground patterns, read through §3(ii): a painted line is a road
    #       marking and road markings are painted on **pavement**, never on a gravel
    #       maintenance track — this one was a 0.12 x 80 m stripe lying on loose gravel;
    #   (b) it is the last surviving fragment of the levee-crest **cycle track**, which the
    #       07-29 supervisor ruling removed from this scene (*"03 stays natural, the cycle
    #       track holds only for the scene17 levee"*) — the paving went, the line did not;
    #   (c) G3 shows the crest promenade carrying **no longitudinal marking at all**.
    #   The 둔치 markings (`path_lines`, D4) are a different object and STAY: a 자전거도로 on
    #   the floodplain terrace really is line-marked, and G3's archetype depends on it.
    #   The builder block goes with the parameter; nothing else reads `levee_line`.
    # [v5.1] 3 posts at an even 6 m had nothing to do with real river distance markers
    #   (hundreds of m apart); it was a decorative row -> cut to 2.
    # [v6 ruling (4) / v5.2 §6] The remaining 2 were judged "barber poles standing alone in
    #   the middle of the beach grass" -> **all removed** (weak functional basis · empty is the default).
    #   The builder code path stays (refill the list and they come back).
    markers=[],                                        # (s, y, yaw_jit)
    marker=dict(post_r=0.04, post_h=1.2, plate=(0.06, 0.35, 0.25),
                plate_z=1.02),
    # D7 pergola 1
    # **[P03] Moved 0.8 m landward.** Its river post line stood at x = −5.000, which the
    #   paving now occupies (the grey edge band spans −5.400…−5.000), i.e. four posts
    #   standing *in* the walking surface — the PROP-EDGE class G-3/PE-7 exists to stop.
    #   x0/x1 −8.0/−5.0 -> −8.8/−5.8 keeps the 3.0 × 3.0 footprint and the y range, and
    #   leaves the posts **0.400 m clear** of the paving. `benches[0]` (−6.500, 4.400) is
    #   still inside the footprint (−8.8 <= −6.5 <= −5.8), checked, so its "inside the
    #   pergola" rationale survives the move.
    pergola=dict(x0=-8.8, x1=-5.8, y0=3.0, y1=6.0, z_roof=2.4, post_r=0.09,
                 roof_t=0.14, jyaw=-3.0),
    # D8 beach sports-field lines (beach identity)
    # (placed in the +Y far view so it missed the crossing · benches y +-6)
    # **[v7] DELETED.** This was four white lines forming a 3.0 x 12.0 m **rectangle painted
    #   on the ground** — the most literal instance in this scene of what the user named
    #   (*"바닥에 이상한 사각형 무늬는 웬만하면 다 제거해"*). It is also not a sports field: a
    #   3 x 12 m outline is no court in any code, so the "beach identity" it was bought for
    #   was never actually delivered, and G3 carries nothing like it. Deleted outright rather
    #   than resized — a correctly sized court would be a new prop, which nobody asked for.
    #   The builder block goes with the parameter; nothing else reads `field`.
    # D9 water-level gauge (fixes it as river infrastructure)
    gauge=dict(cx=17.4, cy=-3.0, r=0.09, z0=-3.35, z1=0.2,
               band_z=(-2.6, -1.6, -0.6), band_h=0.25),

    # --- materials: physical size for texture_scale [m/tile] + constants ---
    material=dict(
        scale=dict(gravel=0.6, grass=1.4, concrete_floor=0.8,   # grass 4.0: eases moss clumping
                   dirt_park=1.0, rock_wall=1.5, wood_dark=1.0,
                   # [P03] 1.2 is not a taste value: `scene_common.py:158-163` records that
                   #   the PavingStones015 map carries 12 repeats per tile, so the long side
                   #   of a block is 0.17 / 0.20 / 0.25 m at scale_m 1.0 / 1.2 / 1.5.
                   #   **1.2 == the 인터로킹 200 x 100 standard**, i.e. the same module the
                   #   kit ledger declares (`GROUND_DIMENSIONS["unit_cell"]["levee_paved"]`).
                   paving_interlock=1.2),
        # === [P03 · GT-46] 점토블록 promenade tones ==============================
        # The `paving_interlock` scan is neutral grey concrete block (mean sRGB
        # 141.0/141.2/140.2, linear albedo 0.2777). G3's promenade is a **warm tan clay
        # paver**; its sunlit field measures sRGB 210/172/130 at full resolution
        # `[ref, measured this session]`. `paving_tint` takes it there with **every channel
        # <= 1.0**, so the tint can only attenuate the map and can never amplify its
        # highlights — which matters, because the highlight tail is the whole tone defect
        # this row is closing:
        #     gravel_diff           lum p99 215.4 · >204 3.56 %  · albedo 0.2855
        #     paving_interlock_diff lum p99 173.6 · >204 0.09 %  · albedo 0.2777
        # Same mean albedo, **40x fewer near-white texels**. The near-white crest the
        # S03 lane handed on (`w3_s03_v1.md` §7-3, h0.3_d2 `wht% 39.1 / mean 194`) was the
        # gravel scan's bright stone tail, and unit paving simply does not have one.
        #   paving_tint  (1.000, 0.717, 0.471) -> linear (0.2766, 0.1995, 0.1294)
        #                = sRGB (145, 125, 101), luminance albedo **0.211**
        #   band_tint    = scene17's own measured `paving_tint`, unchanged, so the two
        #                  Hangang levee scenes share one grey-block value: albedo **0.231**,
        #                  i.e. the band reads 10 % lighter and neutral against the tan
        #                  field, which is what G3's "light-grey block edge band" is.
        #   wear_tint    = paving_tint x 0.85 (`wear_albedo_gain`, ground_kit.py:282).
        # All three are under `ALBEDO_CAP` 0.30 (ground_kit.py:128).
        paving_tint=(1.00, 0.717, 0.471),
        paving_band_tint=(0.84, 0.83, 0.81),
        paving_wear_tint=(0.85, 0.609, 0.400),
        # **[P03-F2 — found on the pilot's first pass, fixed before the round was kept.]**
        #   The two `stain` kinds were bound to `dirt_park` and `concrete_dark`, which were
        #   right against *gravel* and are wrong against 점토블록: measured on
        #   `pt_noon_levee_walk.png`, the `concrete_dark` water lobes rendered sRGB
        #   (202,185,160) against paving at (199,181,156) — **lighter than the surface they
        #   soil, flat, and untextured**, i.e. they read as spilled cement, not water; and
        #   the `dirt_park` lobe read as a heap of loose gravel lying on the blocks.
        #   A stain is the *same surface seen through a film*, so both are re-derived from
        #   `paving_tint` and keep the block pattern showing through — which is also what
        #   stops them reading as decals at all:
        #     wet   = paving x 0.70                  -> albedo 0.148  (a damp block is
        #             0.5~0.7 x its dry reflectance)
        #     soil  = paving x (0.78, 0.70, 0.56)    -> albedo 0.161, browner and duller
        paving_wet_tint=(0.700, 0.502, 0.330),
        paving_soil_tint=(0.780, 0.502, 0.264),
        grass_tint=(0.55, 0.68, 0.42),        # eases tile repetition + green tint (kept)
        hedge_tint=(0.48, 0.60, 0.34),        # v4-B1 slope shrubs
        reed_tint=(0.78, 0.72, 0.40),         # v4-D5 reeds (dry silvergrass tone)
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,        # scene01 final value (tree trunk·stakes)
        # v4-B4: (0.33,·,0.36)+metallic 0.4 blew out to white PVC pipe under direct noon sun
        #   -> darker galvanised tone + less metallic.
        bollard_color=(0.16, 0.16, 0.17), bollard_metallic=0.15,
        bollard_rough=0.6,
        # v4-B (shared): crown albedo raised (black blob -> leaf silhouette)
        canopy_a=(0.035, 0.052, 0.024), canopy_b=(0.042, 0.060, 0.030),
        canopy_rough=1.0,
        water_color=(0.05, 0.10, 0.11), water_rough=0.08,      # less mirror-like (0.03->0.08)
        # [v5 ruling applied] The v4-D1 bridge albedo 0.055 turned deck·parapet·piers all into
        #   a black silhouette carrying zero information (a black mass right of levee_walk +
        #   a black reflection on the water; across_river showed a 'black slab hanging in mid-air').
        #   It is the 'black box' defect flagged by audit v4, recurring at a larger scale.
        #   -> deck·piers raised to a real exposed-concrete tone (0.28),
        #     and the parapet split off at 0.22 as the ruling advised, keeping a face break from the deck.
        concrete_dark=(0.28, 0.28, 0.275), concrete_dark_rough=0.8,   # v4-D1 bridge deck·piers·abutments
        concrete_parapet=(0.22, 0.22, 0.215),                         # bridge parapet (guard wall)
        # [GT-83 p2] girder band under the deck fascia. The 0.30 m recess already draws the
        #   shadow line, but a bridge soffit is in permanent shade and this scene is judged
        #   at noon with a 49.8 deg sun, so on the sunlit (north) fascia the recess alone can
        #   flatten out. 0.235 is one step under the deck's 0.28 and one step over the
        #   parapet's 0.22 -> read from the side the section is light/dark/light/dark
        #   (cope 0.28 · parapet 0.22 · fascia 0.28 · girder 0.235) instead of one white slab.
        concrete_girder=(0.235, 0.235, 0.230),
        # [GT-83] carriageway wearing course on the deck. Asphalt luminance albedo is
        #   0.09~0.12; `concrete_dark` (0.28) on the deck top is what let the aerial cuts read
        #   the deck as a bare slab rather than a road, which is half of "what is it for".
        bridge_wear=(0.105, 0.105, 0.108), bridge_wear_rough=0.88,
        city_color=(0.16, 0.16, 0.17), city_glass=(0.05, 0.07, 0.10),
        city_parapet=(0.22, 0.22, 0.21),      # v4-D2 distant city
        line_color=(0.55, 0.55, 0.52),        # v4-D4/D8 road·sports-field white lines
        gauge_band=(0.30, 0.045, 0.035),      # v4-D9 water-gauge red bands
        # [v5.1 global convention 2] bollard top reflective band (no pure white - 0.72 glossy off-white)
        bollard_band=(0.72, 0.72, 0.70), bollard_band_rough=0.35,
        # [v5.1 global convention 4] per-instance tint jitter amplitude
        tint_jitter=0.05,
    ),

    # --- lighting: scene01's verified noon constants, unchanged ---
    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        noon_sun_enable=True, noon_sun_elev=49.79,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    SUN_AZ_OFFSET=171.5,               # same default as scene01 (to check the sky reflection on the water)

    render=dict(pt_total_spp=512, pt_max_bounces=8),
)


def _deep_update(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_update(dst[k], v)
        else:
            dst[k] = v


# parameter override (for A/B render comparison - scene01 pattern)
_ov = os.environ.get("NEGOBS_PARAMS_OVERRIDE", "")
if _ov:
    _deep_update(PARAMS, json.loads(_ov))
    print(f"[PARAMS] override 적용: {_ov}")

# SCENE_CONFIG env-var override (for the toggle-integrity verification pipeline)
_sc_ov = os.environ.get("NEGOBS_SCENE_CONFIG", "")
if _sc_ov:
    _deep_update(SCENE_CONFIG, json.loads(_sc_ov))
    print(f"[SCENE_CONFIG] override 적용: {_sc_ov}")


# ===========================================================================
# [B'] keep_dressing — the arm-C control, resolved ONCE at module scope
# ===========================================================================
#   Ported from scenes/batch1/sceneC2_leaf_stairs.py:496-520. Arm C of the v3
#   plan (RENDER_PLAN_V3 §1.2) is `{"hazard_stairs": false, "keep_dressing":
#   true}` with every `cue_*` left at its arm-A default: the DROP geometry goes,
#   the cue and dressing objects stay in the transform they have with the hazard
#   ON. Every use below reads this one constant, so `grep KEEP_DRESSING` is the
#   whole audit surface, and with the key absent from SCENE_CONFIG (the value in
#   both existing arms) every guarded expression collapses to exactly the
#   pre-patch code path.
#   THIS SCENE IS THE ONE THE PORT EXISTS FOR. `:2713` reads
#   `if cfg["cue_scene_dressing"] and cfg["hazard_stairs"]`, i.e. the whole
#   dressing layer — bollards, benches, shrubs, trees, reeds, pergola, gauge —
#   DIES with the hazard (CUE_COVERAGE binding class HZ). Without the third
#   branch below, arm C would be byte-identical to arm D and the (A,C)
#   counterfactual would measure nothing.
#   The two contradictions below are FATAL rather than silently resolved: an arm
#   whose config does not say what it means must not render 72 cuts and be
#   discovered later in a metrics table (sceneC2:503-507, verbatim reasoning).
KEEP_DRESSING = bool(SCENE_CONFIG.get("keep_dressing", False))
if KEEP_DRESSING:
    if SCENE_CONFIG.get("hazard_stairs", True):
        raise SystemExit(
            "[FATAL scene03] keep_dressing=True requires hazard_stairs=False — "
            "with the hazard ON there is nothing to keep and the arm would be "
            "an unlabelled duplicate of arm A. Fix the render config.")
    if not SCENE_CONFIG.get("cue_scene_dressing", True):
        raise SystemExit(
            "[FATAL scene03] keep_dressing=True contradicts "
            "cue_scene_dressing=False — the dressing IS what this arm exists "
            "to preserve, and this scene's dressing is HZ-bound (:2713).")
    print("[keep_dressing] scene03 ON — hazard geometry only (side slopes · "
          "20-step stair · trims · beach · riprap -> one z=0 fill from the "
          "levee crest to x18); `build_dressing` is restored over that fill "
          "(:2713) and everything the ON arm stands on the BEACH datum "
          "(beach.z_top -3.20) rides it up to z=0; `slope_z` returns 0.0 so the "
          "slope shrubs sit on the fill instead of inside it. Cues "
          "(`build_cues`), ground_kit and the river are already outside the "
          "hazard branch. Camera datum untouched — the strip x in [-12,-1.2] · "
          "|y|<=0.90 is levee crest in both arms and carries no dressing.")


# ===========================================================================
# [C] paths (scene_common owns the actual texture·mdl·hdri assets)
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene03")

# texture roles used by this scene (tactile unused)
# [P03] `paving_interlock` joins the list — the crest walk is 점토블록 from GT-46 on.
#   `gravel` STAYS: it is still the material of the `hazard_stairs=False` flat control's
#   surroundings check and of the debris pool binding, and dropping a role from this list
#   only turns a load failure from loud into silent.
ASSET_ROLES = ["gravel", "grass", "concrete_floor", "dirt_park",
               "rock_wall", "wood_dark", "paving_interlock", "hdri", "mdl"]


# ===========================================================================
# [C2] [v5.1] meander centerline - the coordinate transform basis for river-parallel elements
#   world X = s + river_dx(y),  band seg heading = river_yaw(y)
#   dx(0)=0 · dx'(0)=0, so in the stair corridor (y +-0.95) it is the identity -> the hazard
#   geometry (stairs·trim·spur·corridor) transforms are bit-identical to v5.
# ===========================================================================
def river_dx(y):
    """X offset of the centerline [m]."""
    mn = PARAMS["meander"]
    k1 = 2.0 * math.pi / mn["L1"]
    return (mn["A1"] * (math.cos(k1 * y) - 1.0)
            + mn["A3"] * (y / mn["y_ref"]) ** 3)


def river_ddx(y):
    """dx/dy — tangent slope of the centerline."""
    mn = PARAMS["meander"]
    k1 = 2.0 * math.pi / mn["L1"]
    return (-mn["A1"] * k1 * math.sin(k1 * y)
            + 3.0 * mn["A3"] * y * y / mn["y_ref"] ** 3)


def river_yaw(y):
    """Seg heading [deg]. Applied as rotZ, the seg's local +Y matches the centerline tangent."""
    return -math.degrees(math.atan(river_ddx(y)))


def river_segments(y_gap=None):
    """Band seg partition → [(yc_ref, y_lo, y_hi, clip_lo, clip_hi), ...].

    * Every band uses **the same y partition (the same chord frame)**. If the partition
      differed per band, at a given y the chords of neighbouring bands would approximate the
      curve at different angles and open real gaps of up to several cm (2 cm measured with the
      verification script). The corridor (y_gap) must not change the partition; it only
      **cuts that seg lengthwise** — the rotation axis (yc_ref) and the width-wise edge lines
      stay put, so alignment with the neighbouring bands holds. No longitudinal overlap (over)
      is added at a cut end (it would intrude on the corridor).
      seg_dy=5.0 · y ±47.5 → 19 segs (of which the y=0 seg is split in two at the corridor).
    """
    mn = PARAMS["meander"]
    y0, y1, dy = mn["y0"], mn["y1"], mn["seg_dy"]
    n = max(1, int(round((y1 - y0) / dy)))
    h = (y1 - y0) / n
    out = []
    for i in range(n):
        a = y0 + i * h
        b = a + h
        yc = (a + b) / 2.0
        if y_gap is None:
            out.append((yc, a, b, False, False))
            continue
        glo, ghi = y_gap
        if b <= glo or a >= ghi:
            out.append((yc, a, b, False, False))
        elif a < glo and b > ghi:
            out.append((yc, a, glo, False, True))
            out.append((yc, ghi, b, True, False))
        elif a < glo:
            out.append((yc, a, glo, False, True))
        elif b > ghi:
            out.append((yc, ghi, b, True, False))
    return out


# --- [GT-129] the +Y terminal end of the meander bands ---------------------
WATER_MAX_W = 3.5          # the `max_w` river_band() lays the 3 water bands with
WATER_Z_STEP = 0.002       # its `z_bias` step between bands (anti Z-fight)


def river_end_geom():
    """[GT-129] Closed form of a meander band's **last (+Y) seg end edge**.

    `river_band` lays each seg as an axis-aligned box inside a rot group yawed by
    `river_yaw(yc)`, so at the assembly's last seg that rotation **tilts the end edge**:
    across one sub-band of width w the edge travels `w·tan(yaw)` in world Y, and because
    sub-bands are butted in world X the assembly's end comes out as a **sawtooth of pitch w
    and amplitude w·tan|yaw|**. At the last seg (yc = +45.0) the tilt is 32.27°, i.e. 2.0 m
    of Y across each 3.2 m water sub-band, over 12 sub-bands (3+4+5). Nothing at all is
    modelled beyond y = +47.5, so from every +Y-looking cut that sawtooth **is** the water's
    silhouette against the sky — audit v4 GT-129, measured in `260816_w4_final33_on` as
    12 teeth of 54 px pitch in `meander_air`, a 5~6 px staircase in `bank_oblique` and a
    serrated right horizon in `river_along`.
    The −Y end needs no such treatment and gets none: at yc = −45.0 the cosine and cubic
    terms of `river_ddx` very nearly cancel (yaw = +0.83°), so that end is flat to 0.044 m,
    and it is behind every camera in `build_views()` (checked: 0 of its 24 corners project
    inside any frustum).

    Returns dict(yc, yaw, x_shear, y_lo, y_hi):
      world corner at the sub-band boundary of cross-section s
        x = river_dx(yc) + s − x_shear
        y = (y_lo + y_hi)/2 ∓ (w/2)·tan(yaw)     (− on the boundary's −X corner, + on its +X)
      `y_lo`/`y_hi` bracket **any** sub-band up to `WATER_MAX_W` wide, so a cap laid on them
      swallows the whole tooth row whatever the sub-band split turns out to be.
    One function, two clients — `build_river` stands the end cap on it and
    `river_view_selfcheck` tests the silhouette against it — so neither can drift from the
    geometry it describes.
    """
    mn = PARAMS["meander"]
    yc, _ylo, yhi, _cl, _ch = river_segments(None)[-1]
    yaw = river_yaw(yc)
    cw = math.cos(math.radians(yaw))
    y_mid = yhi + mn["over"] * cw / 2.0
    half = WATER_MAX_W / 2.0 * abs(math.tan(math.radians(yaw)))
    return dict(yc=yc, yaw=yaw,
                x_shear=((yhi - yc) / cw + mn["over"] / 2.0)
                * math.sin(math.radians(yaw)),
                y_lo=y_mid - half, y_hi=y_mid + half)


def water_end_cap():
    """[GT-129] The end-cap slabs, `(x0, x1, y0, y1, z)` in water-band order.

    Single source for `build_river` (which stands them up) and `river_view_selfcheck` (which
    tests the silhouette against them). x spans are exactly the bands' own end corners, so
    the caps butt on the seams the bands already have and never reach outside the channel.
    **One z for all three**, below the LOWEST band top (`WATER_Z_STEP` per band plus the
    1.5 mm seg stagger): the meandering bands then always win where they overlap a cap, and
    the far edge is a single coplanar straight line. Carrying the per-band z step into the
    caps instead would put a ~1 px riser back into the grazing `river_along` horizon at each
    band seam — measurably (1.12 px, 5 reversals), which is the very thing the cap removes.
    """
    wt = PARAMS["water"]
    ec, eg = wt["end_cap"], river_end_geom()
    z = (wt["z"] - WATER_Z_STEP * (len(wt["bands"]) - 1)
         - PARAMS["meander"]["z_stagger"] - ec["dz"])
    xb = river_dx(eg["yc"]) - eg["x_shear"]
    return [(xb + s0, xb + s1, eg["y_lo"] - ec["tuck"], eg["y_hi"] + ec["over"], z)
            for s0, s1, _rgh in wt["bands"]]


def _ang(a):
    """Normalise a bearing difference to (−180, 180]."""
    return (a + 180.0) % 360.0 - 180.0


def near_approach_chords():
    """[GT-83 pass 3] Chord polyline of the **near-side approach viaduct**.

    One function, two clients — `build_river` stands the geometry on it and
    `river_view_selfcheck` tests occlusion against it — so the occluder can never drift
    away from the thing it models.

    Shape: leave the near bridgehead on the deck axis, turn 90.0° left over
    `napp_curve_len` (per-chord steps `napp_deltas`, eased at both ends), then hold the
    meander cross-section coordinate reached at the end of the turn down the `napp_ypar`
    stations. Because the parallel run is expressed in the **meander frame** it follows
    exactly the same bend as the 둔치 bands beneath it.

    Elevation: a parabolic vertical curve of length `napp_vlen` off the level deck, then a
    constant `napp_grade`. The whole profile is dropped by one `z_stagger`, so no face of
    the approach is ever coplanar with the frozen main deck it grows out of.

    Returns `(chords, s_hold)` where each chord is a dict with the world end points, the
    chord bearing, the top-of-deck elevations and the **mitre extensions** (`back`/`fwd`)
    that make consecutive chords overlap instead of leaving a wedge open on the outside of
    the turn: `back/fwd = (deck half width + cope_out) · tan(kink/2)`.
    """
    bg = PARAMS["bridge"]
    stag = PARAMS["meander"]["z_stagger"]
    cy = (bg["y0"] + bg["y1"]) / 2.0
    cx = (bg["x0"] + bg["x1"]) / 2.0
    dx0 = river_dx(cy)
    yaw = river_yaw(cy)
    cc, ss = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    pvx, pvy = dx0 + cx, cy
    # the near deck end, carried through the bridge group's own pivot rotation
    ex, ey = dx0 + bg["x0"], cy
    p0 = (pvx + (ex - pvx) * cc - (ey - pvy) * ss,
          pvy + (ex - pvx) * ss + (ey - pvy) * cc)
    a0 = 180.0 + yaw                       # travel bearing leaving the bridgehead
    n = len(bg["napp_deltas"])
    seg = bg["napp_curve_len"] / n
    pts, brs = [p0], []
    b = a0
    for d in bg["napp_deltas"]:
        bc = b + d / 2.0                   # chord bearing = the mid-arc heading
        pts.append((pts[-1][0] + seg * math.cos(math.radians(bc)),
                    pts[-1][1] + seg * math.sin(math.radians(bc))))
        brs.append(bc)
        b += d
    s_hold = pts[-1][0] - river_dx(pts[-1][1])
    for yk in bg["napp_ypar"]:
        pts.append((river_dx(yk) + s_hold, yk))
        brs.append(math.degrees(math.atan2(pts[-1][1] - pts[-2][1],
                                           pts[-1][0] - pts[-2][0])))
    grade, vlen = bg["napp_grade"], bg["napp_vlen"]

    def z_of(t):
        if t <= vlen:
            return bg["deck_top"] - stag - grade * t * t / (2.0 * vlen)
        return bg["deck_top"] - stag - grade * (t - vlen / 2.0)

    href = (bg["y1"] - bg["y0"]) / 2.0 + bg["cope_out"]
    out, t = [], 0.0
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        ln = math.hypot(x1 - x0, y1 - y0)
        d_prev = abs(_ang(brs[i] - (brs[i - 1] if i else a0)))
        d_next = abs(_ang(brs[i + 1] - brs[i])) if i + 1 < len(brs) else 0.0
        out.append(dict(
            i=i, brg=brs[i], L=ln, x0=x0, y0=y0, x1=x1, y1=y1,
            mx=(x0 + x1) / 2.0, my=(y0 + y1) / 2.0,
            z0=z_of(t), z1=z_of(t + ln),
            back=(bg["napp_lead"] if i == 0
                  else href * math.tan(math.radians(d_prev / 2.0))),
            fwd=href * math.tan(math.radians(d_next / 2.0))))
        t += ln
    return out, s_hold


def tint_jitter(color, seed, amp=None):
    """[v5.1 global convention 4] Per-instance ±amp colour jitter (seed-deterministic)."""
    if amp is None:
        amp = PARAMS["material"]["tint_jitter"]
    rnd = random.Random(1000003 * (int(seed) + 13))
    return tuple(round(max(0.005, c * (1.0 + rnd.uniform(-amp, amp))), 5)
                 for c in color)


# ===========================================================================
# [D] camera presets: grid_views(gy=0.0) + 4 mise-en-scene cuts (§C)
#     No centre railing in this scene -> the preset axis runs through the stair centre y=0.
# ===========================================================================
def build_views():
    views = sc.grid_views(0.0)                 # h{0.3,0.9,1.8}×d{2,5,10}, +X pitch -10°
    # levee_walk: from the levee crest, looking ahead - the stairs fold into the slope and vanish, only water catches
    views["levee_walk"] = dict(eye=[-6.0, 0.0, 1.2], tgt=[4.0, 0.0, 0.3])
    # stair_down: looking down from above the stairs (the shoulder)
    views["stair_down"] = dict(eye=[-0.6, 0.0, 1.6], tgt=[4.5, 0.0, -2.0])
    # beach_lookup: from the beach, looking back (-X) - up at the slope·stairs
    views["beach_lookup"] = dict(eye=[9.0, 2.0, -2.6], tgt=[0.5, 0.0, -0.8])
    # across_river: view of the far bank across the water
    views["across_river"] = dict(eye=[17.0, 0.0, -2.5], tgt=[42.0, 0.0, -2.9])

    # ===================================================================
    # [v6 ruling (1)] **3 new along-river / oblique mise-en-scene cuts** - geometry untouched, cameras only.
    #   Reason: all 4 old cuts were perpendicular to the river (sight azimuth ~ 0 deg), so only
    #   15~40 m of river fell in the FOV -> a 110 m wavelength meander is effectively straight there.
    #   The 3 cuts below turn the sight line onto the **river axis (+Y)** and hold y 45~90 m in
    #   one frame. Lateral centerline travel over that span = 14.8 m (dx(0)=0 -> dx(+-47.5)).
    #   All coordinates are computed in the meander frame via river_dx() - they follow any amplitude change.
    #   (the occlusion check is river_view_selfcheck() below - NEGOBS_SELFCHECK=1)
    # ===================================================================
    def W(s, y):                               # cross-section s -> world X
        return river_dx(y) + s

    # (1) river_along [mise-en-scene, non-judging] - a **walking sight line** (h1.65) on the
    #    levee crest promenade, looking upstream. [GT-83, measured] the whole crossing projects
    #    to |u| ≥ 15 frame half-widths here, i.e. it is not in this cut at all.
    #    The eye is only 5 m above the water, so the on-screen meander bow is a small 0.4 %
    #    (check below) - not a judging cut but a realism cut of "walking the levee path".
    views["river_along"] = dict(eye=[W(-2.5, -10.0), -10.0, 1.65],
                                tgt=[W(14.0, 35.0), 35.0, -3.30])
    # (2) meander_air [judging] - 15.4 deg downward tilt. The bend over y −44..+20 plus the
    #    bridge crossing in one frame. Waterline screen bow 14.1 % (of frame half-width).
    views["meander_air"] = dict(eye=[W(10.2, -44.0), -44.0, 16.0],
                                tgt=[W(20.0, 25.0), 25.0, -3.35])
    # (3) bank_oblique [judging] - oblique upstream view from the **far side of the channel**
    #    (12.7 deg down). Opposite side and a different angle from (2), cross-checking that
    #    the meander is no camera fluke.
    #    **[v7] The coordinates are DELIBERATELY NOT TOUCHED.** R03-1 is to be met by geometry,
    #    never by a camera edit, and this is a judging cut — moving it would break its own
    #    comparability with the baseline round. One consequence is recorded rather than
    #    smoothed: the far bank moved from s34 to s52, so this eye (s40) that used to stand
    #    **above the far bank** now stands **12 m out over the water** at the same height. The
    #    cut still does its job (an aerial cross-check of the bend from the opposite side);
    #    only the old "above the far bank" wording was wrong after the widening, and it is
    #    corrected here rather than the camera being bent to fit it.
    views["bank_oblique"] = dict(eye=[W(40.0, -26.0), -26.0, 8.0],
                                 tgt=[W(20.0, 20.0), 20.0, -3.20])
    return views


def _cam_basis(eye, tgt):
    """World → camera normalised image coordinate transformer. up=+Z, image u(right)·v(up).
    Returns: project(P) → (u, v, depth). u,v are in tan units (= tan of the FOV)."""
    ex, ey, ez = eye
    fx, fy, fz = tgt[0] - ex, tgt[1] - ey, tgt[2] - ez
    fl = math.sqrt(fx * fx + fy * fy + fz * fz)
    f = (fx / fl, fy / fl, fz / fl)
    # right = f x Z  (normalised). Assumes the sight line is not near vertical (tilt <= 60 deg).
    rx, ry, rz = f[1] * 1.0 - 0.0, 0.0 - f[0] * 1.0, 0.0
    rl = math.hypot(rx, ry)
    r = (rx / rl, ry / rl, 0.0)
    u_ = (r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2],
          r[0] * f[1] - r[1] * f[0])            # up = r × f

    def project(p):
        dx_, dy_, dz_ = p[0] - ex, p[1] - ey, p[2] - ez
        d = dx_ * f[0] + dy_ * f[1] + dz_ * f[2]
        if d <= 1e-6:
            return None
        return ((dx_ * r[0] + dy_ * r[1] + dz_ * r[2]) / d,
                (dx_ * u_[0] + dy_ * u_[1] + dz_ * u_[2]) / d, d)
    return project


def _seg_hits_box(eye, p, box):
    """True if the segment eye→p passes through AABB box=(x0,x1,y0,y1,z0,z1) (slab method).
    Near the end point (t>0.995) it is the target itself, so that range is excluded."""
    x0, x1, y0, y1, z0, z1 = box
    t0, t1 = 0.0, 0.995
    for a, b, lo, hi in ((eye[0], p[0], x0, x1), (eye[1], p[1], y0, y1),
                         (eye[2], p[2], z0, z1)):
        d = b - a
        if abs(d) < 1e-9:
            if a < lo or a > hi:
                return False
            continue
        ta, tb = (lo - a) / d, (hi - a) / d
        if ta > tb:
            ta, tb = tb, ta
        t0, t1 = max(t0, ta), min(t1, tb)
        if t0 > t1:
            return False
    return True


def _rot_xy(p, pivot, yaw_deg):
    """Rotate a world point by `yaw_deg` about `pivot` in XY (z untouched)."""
    c = math.cos(math.radians(yaw_deg))
    s = math.sin(math.radians(yaw_deg))
    dx_, dy_ = p[0] - pivot[0], p[1] - pivot[1]
    return (pivot[0] + dx_ * c - dy_ * s, pivot[1] + dx_ * s + dy_ * c, p[2])


def _seg_hits_rot_box(eye, p, box, pivot, yaw_deg):
    """[v7] `_seg_hits_box` for a prim that lives inside a `build_rot_group`.

    A rotation about +Z is rigid, so instead of inflating the box to an axis-aligned envelope
    the segment is carried into the group's own frame (rotate both endpoints by −yaw about the
    pivot) and tested against the box **as authored**. `t` is preserved by a rigid motion, so
    the 0.995 end-point exclusion still means the same thing.
    """
    return _seg_hits_box(_rot_xy(eye, pivot, -yaw_deg),
                         _rot_xy(p, pivot, -yaw_deg), box)


def river_view_selfcheck(verbose=True):
    """[v6 ruling (1)] Coordinate check of **meander legibility + occlusion** for the new along-river cuts.

    Key property: **a straight line in 3D projects to a straight line under any projection.**
    So the maximum deviation of the projected waterline (s=18.2, the effective waterline) from
    the chord joining its two end points is a pure meander signal — "0 if the channel were
    straight". That value is converted to **a % of the frame half-width (tan30° = 0.577)** to
    quantify legibility.
    (The old 4 cuts were perpendicular to the river, so only 15~40 m of waterline was in frame → deviation ≈ 0.)

    Occlusion: whether the segment from the camera to each waterline sample pierces the AABB of a
    near element (bridge+parapet·beach/levee-crest trees·pergola·bollards·water gauge), by the slab method.
    Returns: (ok, diagnostic dict). Pure maths — no Isaac boot needed.
    """
    views = build_views()
    s_edge = 18.2                              # effective waterline (riprap toe)
    TU, TV = math.tan(math.radians(30.0)), math.tan(math.radians(18.0))

    # --- near-view occluder AABBs (rot groups conservatively approximated by their bounding box) ---
    # **[v7] The bridge occluder is rebuilt: ROTATED frame + deck/pier split.**
    #   It used to be a single axis-aligned box spanning the pier feet (−3.70) to the parapet
    #   top (+0.70), with the y range inflated by `byw` to swallow the rotated deck. Two errors
    #   in one box, and both are the error this function already names and fixes for tree
    #   crowns a few lines below — *"one solid box would falsely count the empty space under
    #   the crown as occlusion"*:
    #     · the **open space under the deck** (−3.70…−1.00, everything but 7 slender piers)
    #       was solid;
    #     · the **AABB inflation** counted the empty corners either side of the skewed deck.
    #       At the v6 skew (14.75°, 34 m deck) that inflation was ±4.33 m; the R03-1 widening
    #       takes the deck to 52 m and the local tangent to 23.65°, i.e. ±10.43 m, so the box
    #       grows from 17.7 m to 29.9 m of y — **3.4× more phantom occluder than real deck
    #       width (9.0 m)**, purely from a modelling shortcut.
    #   With the old box the widening alone drives `meander_air` 31.8 % → 44.3 % occluded and
    #   trips a 35 % gate on an occluder that does not physically exist. The fix is to test the
    #   segment **inside the rot group's own frame** (`_seg_hits_rot_box`) against the deck as
    #   authored, plus one box per pier. A/B on BOTH geometry arms is in `w3_s03_v1.md` §4:
    #   the correction moves the v6 arm too, which is what makes it an instrument fix rather
    #   than a gate tuned to a result.
    # **[GT-83] The member split follows the rebuilt crossing.** Same principle, more members:
    #   the deck is 4.98~5.15 m clear of everything it crosses now, so the open air under it
    #   is a far larger share of the structure's bounding box than in v7 and must stay open.
    #   Added: one box per hammerhead cap (the column box no longer reaches the soffit) and
    #   one per abutment (solid ground→parapet-top blocks that DO occlude).
    # **[GT-83 p2] The member split follows the buildability pass.** Three edits, each of them
    #   the same "model the void as void" rule this function already runs on:
    #     · the far abutment became a **wall pier**, so its box now stops at the soffit — the
    #       1.10 m of parapet above it is deck, and the deck box already covers that;
    #     · the **approach viaduct** (x1 → x1+appr_len, graded) is its own box, plus one
    #       column/cap pair per approach pier — the open air under it stays open;
    #     · the **end bridgehead** is a solid ground→parapet-top block, like the near one.
    bg = PARAMS["bridge"]
    b_cy = (bg["y0"] + bg["y1"]) / 2.0
    b_xm = (bg["x0"] + bg["x1"]) / 2.0
    bdx = river_dx(b_cy)
    b_yawd = river_yaw(b_cy)
    b_piv = (bdx + b_xm, b_cy)
    b_sof = bg["deck_top"] - bg["deck_thick"]
    b_cap_bot = b_sof - bg["cap_h"]
    b_x2 = bg["x1"] + bg["appr_len"]
    b_top2 = bg["deck_top"] - bg["appr_grade"] * bg["appr_len"]
    deck_hw = (bg["y1"] - bg["y0"]) / 2.0
    rot_boxes = [
        # deck + parapet, authored frame: soffit (deck_top − deck_thick) → parapet top
        (bdx + bg["x0"], bdx + bg["x1"], bg["y0"], bg["y1"],
         b_sof, bg["deck_top"] + bg["parapet_h"]),
        # approach viaduct: lowest soffit → highest parapet top over its whole run
        (bdx + bg["x1"], bdx + b_x2, bg["y0"], bg["y1"],
         b_top2 - bg["deck_thick"], bg["deck_top"] + bg["parapet_h"]),
    ]
    _cols = [(px, b_cap_bot, b_sof) for px in bg["pier_x"]]
    _cols += [(bg["x1"] + pt,
               b_sof - bg["appr_grade"] * pt - bg["cap_h"],
               b_sof - bg["appr_grade"] * pt) for pt in bg["appr_pier_x"]]
    for _px, _cb, _ct in _cols:                # column feet → cap bottom, then the cap
        rot_boxes.append((bdx + _px - bg["pier_r"], bdx + _px + bg["pier_r"],
                          b_cy - bg["pier_r"], b_cy + bg["pier_r"],
                          bg["pier_z0"], _cb))
        rot_boxes.append((bdx + _px - bg["cap_t"] / 2.0,
                          bdx + _px + bg["cap_t"] / 2.0,
                          b_cy - bg["cap_w"] / 2.0, b_cy + bg["cap_w"] / 2.0,
                          _cb, _ct))
    for _ax, _atop in ((bg["x0"], b_sof),          # [pass 3] both heads are wall piers now
                       (bg["x1"], b_sof),
                       (b_x2, b_top2 + bg["parapet_h"])):
        rot_boxes.append((bdx + _ax - bg["abut_t"] / 2.0,
                          bdx + _ax + bg["abut_t"] / 2.0,
                          bg["y0"] - bg["abut_over"] / 2.0,
                          bg["y1"] + bg["abut_over"] / 2.0,
                          bg["abut_z0"], _atop))
    # **[GT-83 pass 3] the near approach viaduct.** It lives in 17 rot groups of its own, so
    #   it cannot go in `rot_boxes` (one shared pivot/yaw); it gets its own list, tested with
    #   the same `_seg_hits_rot_box` against each chord's own frame. The geometry comes from
    #   `near_approach_chords()` — the SAME call the builder uses — so this occluder can
    #   never drift away from the structure it models. Each box spans soffit -> parapet top
    #   over the chord's full deck width: a deck really is solid, and unlike the piers there
    #   is no void here to model.
    napp_boxes = []
    for _c in near_approach_chords()[0]:
        napp_boxes.append(((_c["mx"] - _c["L"] / 2.0 - _c["back"],
                            _c["mx"] + _c["L"] / 2.0 + _c["fwd"],
                            _c["my"] - deck_hw, _c["my"] + deck_hw,
                            min(_c["z0"], _c["z1"]) - bg["deck_thick"],
                            max(_c["z0"], _c["z1"]) + bg["parapet_h"]),
                           (_c["mx"], _c["my"]), _c["brg"]))
    boxes = []
    # trees: crown (sphere blobs) and trunk kept separate - one solid box would falsely count
    #   the empty space under the crown as occlusion (build_tree: th = trunk_h·U(0.85,1.25)).
    trees = ([(t["cx"], t["cy"], PARAMS["beach"]["z_top"], 2.2)
              for t in PARAMS["trees"]]
             + [(t["cx"], t["cy"], t["gz"], 2.2)
                for t in PARAMS["trees_extra"]]
             # [v7] far-bank stand trunk_h 3.0 -> 4.2, mirroring `build_river`
             + [(t["cx"], t["cy"], PARAMS["far_bank"]["z_top"], 4.2)
                for t in PARAMS["far_trees"]])
    for cx0, cy0, gz, th in trees:
        cx = river_dx(cy0) + cx0
        boxes.append((cx - 1.0, cx + 1.0, cy0 - 1.0, cy0 + 1.0,
                      gz + th * 0.85, gz + th * 1.25 + 1.1))     # crown
        boxes.append((cx - 0.12, cx + 0.12, cy0 - 0.12, cy0 + 0.12,
                      gz, gz + th * 0.85))                       # trunk
    pg = PARAMS["pergola"]
    pcy = (pg["y0"] + pg["y1"]) / 2.0
    pdx = river_dx(pcy)
    boxes.append((pdx + pg["x0"], pdx + pg["x1"], pg["y0"], pg["y1"], 0.0,
                  pg["z_roof"] + pg["roof_t"]))
    for b in PARAMS["bollards"]:
        bx = river_dx(b["cy"]) + b["cx"]
        boxes.append((bx - 0.09, bx + 0.09, b["cy"] - 0.09, b["cy"] + 0.09,
                      0.0, PARAMS["bollard"]["h"]))
    gg = PARAMS["gauge"]
    gx = river_dx(gg["cy"]) + gg["cx"]
    boxes.append((gx - 0.1, gx + 0.1, gg["cy"] - 0.1, gg["cy"] + 0.1,
                  gg["z0"], gg["z1"]))

    for key, bd in PARAMS["city"].items():
        ccy = (bd["y0"] + bd["y1"]) / 2.0
        cdx = river_dx(ccy)
        boxes.append((cdx + bd["x0"], cdx + bd["x1"], bd["y0"], bd["y1"],
                      bd["base_z"], bd["base_z"] + bd["h"]))

    # --- [GT-129] terminal-end silhouette of the water ----------------------
    #   The relation this encodes: **no meander band end may reach past the end cap**, i.e.
    #   the far edge of the water is the cap's single straight world segment and never the
    #   sawtooth of the last seg. Both sides come out of `river_end_geom()`, the same call
    #   `build_river` builds the cap from, so this cannot certify geometry that is not there.
    #   Reported per cut as the worst tooth's screen clearance under the cap line, in % of the
    #   frame half-height (negative = under the line = no castellation). Screen space rather
    #   than world space on purpose: what the audit measured was a silhouette in a frame.
    _eg, _caps = river_end_geom(), water_end_cap()
    _zw = PARAMS["water"]["z"]
    _tan = math.tan(math.radians(_eg["yaw"]))
    _ymid = (_eg["y_lo"] + _eg["y_hi"]) / 2.0
    _xb = river_dx(_eg["yc"]) - _eg["x_shear"]
    teeth = []
    for _s0, _s1, _rgh in PARAMS["water"]["bands"]:
        _n = max(1, int(math.ceil(abs(_s1 - _s0) / WATER_MAX_W)))
        _w = (_s1 - _s0) / _n
        for _j in range(_n):                       # both end corners of every sub-band
            teeth.append((_xb + _s0 + _w * _j, _ymid - _w / 2.0 * _tan, _zw))
            teeth.append((_xb + _s0 + _w * (_j + 1), _ymid + _w / 2.0 * _tan, _zw))
    cap_edge = ((_caps[0][0], _caps[0][3], _caps[0][4]),      # the one straight far edge
                (_caps[-1][1], _caps[-1][3], _caps[-1][4]))

    # (cut name, is it a judging cut) - the bow floor is not applied to mise-en-scene-only cuts.
    diag, ok = {}, True
    for name, judge in (("river_along", False), ("meander_air", True),
                        ("bank_oblique", True)):
        v = views[name]
        eye, tgt = v["eye"], v["tgt"]
        proj = _cam_basis(eye, tgt)
        pts = []
        for k in range(191):
            y = -47.5 + 95.0 * k / 190.0
            p = (river_dx(y) + s_edge, y, PARAMS["water"]["z"])
            q = proj(p)
            if q is None or abs(q[0]) > TU or abs(q[1]) > TV:
                continue
            pts.append((y, q[0], q[1], p))
        if len(pts) < 3:
            ok = False
            diag[name] = dict(n=0)
            continue
        # max deviation from the screen chord -> % of frame half-width
        u0, v0, u1, v1 = pts[0][1], pts[0][2], pts[-1][1], pts[-1][2]
        cl = math.hypot(u1 - u0, v1 - v0)
        dev = 0.0
        for _, u, vv, _p in pts:
            dev = max(dev, abs((u1 - u0) * (vv - v0) - (v1 - v0) * (u - u0))
                      / cl if cl > 1e-9 else 0.0)
        occ = sum(1 for _, _, _, p in pts
                  if any(_seg_hits_box(eye, p, b) for b in boxes)
                  or any(_seg_hits_rot_box(eye, p, b, b_piv, b_yawd)
                         for b in rot_boxes)
                  or any(_seg_hits_rot_box(eye, p, _b, _pv, _br)
                         for _b, _pv, _br in napp_boxes))
        span = pts[-1][0] - pts[0][0]
        pit = math.degrees(math.atan2(tgt[2] - eye[2],
                                      math.hypot(tgt[0] - eye[0],
                                                 tgt[1] - eye[1])))
        # [GT-129] worst tooth vs the cap line at the same u (a straight 3D segment
        #   projects to a straight screen segment, so the line is exact, not a fit).
        qa, qb = proj(cap_edge[0]), proj(cap_edge[1])
        tdv = None
        if qa and qb and abs(qb[0] - qa[0]) > 1e-9:
            tdv = -1e9
            for tp in teeth:
                qt = proj(tp)
                if qt is None:
                    continue
                tdv = max(tdv, qt[1] - (qa[1] + (qb[1] - qa[1])
                                        * (qt[0] - qa[0]) / (qb[0] - qa[0])))
        diag[name] = dict(pitch=round(pit, 1), y_span=round(span, 1),
                          bow_pct=round(100.0 * dev / TU, 2),
                          occluded=occ, n=len(pts), judge=judge,
                          tooth_pct=(None if tdv is None
                                     else round(100.0 * tdv / TV, 3)))
        # **[GT-83 pass 3] The 35 % occlusion criterion is LEFT EXACTLY WHERE IT WAS, and
        #   `meander_air` now exceeds it — on purpose, by ruling, and it is reported as a
        #   failure rather than tuned away.** Measured, on this scene's own sampling:
        #     occlusion 32/131 = **24.4 %** -> 51/131 = **38.9 %** once the 08-06 ruling's
        #     near-side approach exists. The 19 extra samples come from the three chords
        #     immediately outboard of the near bridgehead: they fill the wedge of sky between
        #     the frozen deck's end face and the levee, through which this camera used to see
        #     the waterline at y −3.5…+12.5. **No alignment avoids it** — the whole sweep
        #     measures 36.6…38.9 % (eased/uniform/front-loaded turns, transition 9.5…14.5 m),
        #     and relocating the one tree in the corridor recovers nothing (51/131 either way).
        #   What the criterion is a proxy FOR is unharmed, and that is measured too: on the
        #   **visible** samples only, `meander_air` still spans **65.0 m** of waterline with an
        #   **18.37 %** bow (criteria: 40 m and 5 %), against 65.0 m / 20.41 % before the
        #   approach; `bank_oblique` is untouched at 26/119 = 21.8 %.
        #   Raising the threshold to make this pass would be tuning a gate to a result, which
        #   this file refuses to do elsewhere (see the v7 note in this same function). So the
        #   number stands, the cut reports FAIL, and the trade — a road that goes somewhere
        #   against 14.5 points of waterline occlusion in one aerial cut — is a ruling for the
        #   supervisor, recorded here with the arithmetic rather than absorbed silently.
        if judge and (span < 40.0 or dev / TU < 0.05
                      or occ > len(pts) * 0.35):
            ok = False
        # [GT-129] a castellated water edge fails every cut, mise-en-scene included: the
        #   defect is a physical impossibility, not a legibility target, so it carries no
        #   judging/mise-en-scene split and no tolerance band.
        if tdv is None or tdv >= 0.0:
            ok = False
    if verbose:
        print("=" * 64)
        print("scene03 [v6] 종방향 컷 — 사행 판독성 + 차폐 검산")
        print("=" * 64)
        for k, d in diag.items():
            print(f"  {k:13s}{'[판정]' if d['judge'] else '[미장센]':7s}"
                  f" pitch{d.get('pitch', 0):+6.1f}°  "
                  f"프레임내 수변 y {d.get('y_span', 0):5.1f} m  "
                  f"직선대비 휨 {d.get('bow_pct', 0):5.2f}% 프레임반폭  "
                  f"차폐 {d.get('occluded', 0)}/{d.get('n', 0)}  "
                  f"끝니 여유 "
                  f"{d['tooth_pct'] if d.get('tooth_pct') is not None else float('nan'):+7.3f}"
                  f"% 프레임반높이")
        print("  판정컷 기준: 종방향 ≥40 m · 휨 ≥5 % · 차폐 ≤35 %")
        print("  [GT-129] 끝니 여유 < 0 = 사행 밴드 끝 톱니가 끝단 캡 선 아래 → 수면 실루엣 직선 "
              "(전 컷 공통 기준)")
        print("  (3차원 직선은 어떤 투영에서도 직선 → 휨 > 0 자체가 사행 신호)")
        print(f"  → {'OK' if ok else 'FAIL'}")
        print("=" * 64)
    return ok, diag


def river_width_selfcheck(verbose=True):
    """[v7 R03-1] Coordinate check of **how much river is actually in frame**.

    R03-1's own wording — *"water subtends >= 1/3 of the d5 frame width"* — is satisfied
    **trivially and was already satisfied before this edit**: the water is a horizontal band,
    so wherever it appears at all it spans the full frame width. Stating that plainly instead
    of quoting it as a pass is the point of this function. The quantity that actually moves
    when the channel is widened, and the one this scene is judged on, is the **share of the
    frame the water occupies** — reported here two ways:

      * `v_pct`    vertical subtense of the water band on the sight axis, as % of frame height
      * `area_pct` share of the frame the water polygon covers, by a 240 x 135 ray sample

    Both are pure projective geometry over the same `_cam_basis` the v6 check uses — no Isaac
    boot, no GPU, no render. Occlusion by near geometry is **not** modelled here (the v6 check
    owns that), so `area_pct` is an upper bound; it is used as a **relative** before/after
    number, which is what R03-1 asks for.

    Also reported, because widening and bending trade against each other and the trade must be
    visible: effective channel width, meander amplitude, their ratio, and |yaw|max.

    Returns: (ok, diagnostic dict).
    """
    views = build_views()
    wt, fb = PARAMS["water"], PARAMS["far_bank"]
    s_near, s_far = 18.2, fb["x0"]            # riprap toe .. far bank line
    zw = wt["z"]
    TU, TV = math.tan(math.radians(30.0)), math.tan(math.radians(18.0))

    ys = [-47.5 + 95.0 * k / 500.0 for k in range(501)]
    xs = [river_dx(y) for y in ys]
    amp = max(xs) - min(xs)
    yaw_max = max(abs(river_yaw(y)) for y in ys)
    width = s_far - s_near

    diag = {}
    for name in ("preset_h0.3_d2", "preset_h0.3_d5", "preset_h0.3_d10",
                 "preset_h0.9_d2", "preset_h0.9_d5", "preset_h0.9_d10",
                 "preset_h1.8_d2", "preset_h1.8_d5", "preset_h1.8_d10",
                 "levee_walk", "stair_down", "beach_lookup", "across_river",
                 "river_along", "meander_air", "bank_oblique"):
        v = views.get(name)
        if not v:
            continue
        eye, tgt = v["eye"], v["tgt"]
        proj = _cam_basis(eye, tgt)
        # (a) vertical subtense on the sight axis (y = 0 column of the water band)
        col = []
        for s in (s_near, s_far):
            q = proj((river_dx(0.0) + s, 0.0, zw))
            col.append(q[1] if q else None)
        if None in col:
            v_pct = 0.0
        else:
            lo, hi = sorted(col)
            lo, hi = max(lo, -TV), min(hi, TV)
            v_pct = 100.0 * max(0.0, hi - lo) / (2.0 * TV)
        # (b) screen-area share: project a dense (s, y) lattice of the water polygon and
        #     count the 240 x 135 frame cells it lands in. Cell counting, not point counting,
        #     so the number does not depend on the lattice density once it saturates.
        cells = set()
        NS, NY = 90, 260
        for i in range(NS + 1):
            s = s_near + (s_far - s_near) * i / NS
            for j in range(NY + 1):
                y = -47.5 + 95.0 * j / NY
                q = proj((river_dx(y) + s, y, zw))
                if q is None or abs(q[0]) > TU or abs(q[1]) > TV:
                    continue
                cells.add((int((q[0] + TU) / (2 * TU) * 240),
                           int((q[1] + TV) / (2 * TV) * 135)))
        diag[name] = dict(v_pct=round(v_pct, 2),
                          area_pct=round(100.0 * len(cells) / (240.0 * 135.0), 2))

    ok = width > 22.5                          # R03-1: "wider than v4" (v4 = 22.5 m)
    if verbose:
        print("=" * 72)
        print("scene03 [v7] R03-1 — 강 뷰 폭 검산 (기하만, GPU 0)")
        print("=" * 72)
        print(f"  유효 수면 폭 s {s_near:.1f}..{s_far:.1f} = {width:.1f} m "
              f"(v5.1 15.8 · v4 22.5 · 기준: v4 초과)")
        print(f"  사행 진폭 {amp:.2f} m · 진폭/폭 {amp / width:.2f} · "
              f"|yaw|max {yaw_max:.2f}° (한계 45°)")
        print("  프레임 내 수면 점유 —")
        for k, d in diag.items():
            print(f"    {k:20s} 세로각 {d['v_pct']:6.2f} %  화면면적 {d['area_pct']:6.2f} %")
        print("  주: R03-1 문구의 '프레임 폭 1/3'은 수면이 가로 밴드라 "
              "보이기만 하면 항상 100 % — 실질 지표는 위 두 값이다.")
        print(f"  → {'OK' if ok else 'FAIL'}")
        print("=" * 72)
    return ok, dict(width=width, amp=amp, ratio=amp / width,
                    yaw_max=yaw_max, views=diag)


# ===========================================================================
# [E] main - boot -> assemble -> light -> views -> capture/GUI
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. levee_walk       — h1.2 둑길에서 계단·사면 소실 + 수면·건너편 둔치만 남는가
 2. h0.3·d5~10       — 제방 어깨가 평지로 보이고 낙차 증거가 물면뿐인가
 3. stair_down       — 계단 16단이 명확히 보이는가 (부감)
 4. beach_lookup     — 둔치 나무 수관이 둑마루 눈높이 아래인가 (계열③ 앵커)
 5. across_river     — 수면 하늘 반사 + 건너편 둔치 재출현
 6. cue_railing OFF/ON — 위험 기하(계단·사면) 트랜스폼 동일한가
 7. [v6] meander_air / bank_oblique — 사행이 프레임 안에서 휘어 보이는가
                     (검산: NEGOBS_SELFCHECK=1 python scene03_riverbank.py)
 8. [v6] river_along — 둑길 보행 시점에서 하천 종방향 원근이 자연스러운가
 9. [v7] 강 뷰 — 수면이 v5.1 대비 확실히 넓어졌는가 (유효폭 15.8 → 33.8 m)
10. [v7] 원경 — 건너편 수목선이 근경 양버들과 다른 실루엣(먹참나무)인가
11. [v7] 바닥 — 사각형 무늬(보수패치·구장선·둑마루 중앙선)가 전부 사라졌는가"""


def main():
    # [GT-89] SMOKE gate - early exit BEFORE the Isaac boot (no GPU, no GUI).
    # The old template read NEGOBS_SMOKE only as boot()'s headless arg (or not at
    # all), so the §2.2 smoke floor booted Isaac on this scene (scene03/09 incident).
    # Deep checks keep their own arms (NEGOBS_SELFCHECK / geom_invariance_check.py).
    if os.environ.get("NEGOBS_SMOKE", "0") == "1":
        print("SMOKE_OK %s pre-boot gate (GT-89)" % os.path.basename(__file__))
        return
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    # ── [v6] run the coordinate check only, then exit (no Isaac boot needed) ──
    if os.environ.get("NEGOBS_SELFCHECK", "0") == "1":
        ok_v, _ = river_view_selfcheck()
        ok_w, _ = river_width_selfcheck()      # [v7 R03-1]
        print(f"[selfcheck] 사행 {'OK' if ok_v else 'FAIL'} · "
              f"강폭 {'OK' if ok_w else 'FAIL'}")
        return

    # ── stage 0: asset existence check (before boot) ──
    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])

    # ── stage 1: boot Isaac Sim (SimulationApp always first) ──
    simulation_app = sc.boot(capture_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from omni.kit.viewport.utility import (get_active_viewport,
                                           capture_viewport_to_file)
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    from pxr import UsdGeom
    UsdGeom.Xform.Define(stage, "/World/Scene03")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene03"

    # -------------------------------------------------------------------
    # setup_materials - every material built via scene_common.make_pbr
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]

        def tex(role, path, scale, **kw):
            return sc.make_pbr(stage, path, sc.tex_path(role, "diff"),
                               sc.tex_path(role, "nor"),
                               sc.tex_path(role, "rough"), scale, **kw)

        M = {}
        M["gravel"] = tex("gravel", "/World/Looks/Gravel", sca["gravel"])
        # [P03 · GT-46] 점토블록 promenade + its light-grey edge band + the wear tone.
        #   Three materials, one map. The prim names end in `Paving`, which is what the
        #   realism look layer reads to class them as modular paving (`patch_mix` 0 —
        #   the block pattern is protected instead of being broken up like natural ground).
        M["paving"] = tex("paving_interlock", "/World/Looks/Paving",
                          sca["paving_interlock"], tint=mp["paving_tint"])
        M["paving_band"] = tex("paving_interlock", "/World/Looks/PavingBand",
                               sca["paving_interlock"],
                               tint=mp["paving_band_tint"])
        M["paving_wear"] = tex("paving_interlock", "/World/Looks/PavingWear",
                               sca["paving_interlock"],
                               tint=mp["paving_wear_tint"])
        # [P03-F2] the two stain kinds, re-derived from the paving (see `material` PARAMS)
        M["paving_wet"] = tex("paving_interlock", "/World/Looks/PavingWet",
                              sca["paving_interlock"], tint=mp["paving_wet_tint"])
        M["paving_soil"] = tex("paving_interlock", "/World/Looks/PavingSoil",
                               sca["paving_interlock"], tint=mp["paving_soil_tint"])
        M["grass"] = tex("grass", "/World/Looks/Grass", sca["grass"],
                         tint=mp["grass_tint"])
        M["concrete"] = tex("concrete_floor", "/World/Looks/Concrete",
                            sca["concrete_floor"])
        M["dirt"] = tex("dirt_park", "/World/Looks/Dirt", sca["dirt_park"])
        M["rock"] = tex("rock_wall", "/World/Looks/Rock", sca["rock_wall"])
        M["wood_dark"] = tex("wood_dark", "/World/Looks/WoodDark",
                             sca["wood_dark"])
        # constant-colour materials
        M["rail"] = sc.make_pbr(stage, "/World/Looks/Rail",
                                diffuse_color=mp["rail_color"],
                                metallic=mp["rail_metallic"],
                                roughness_const=mp["rail_rough"])
        M["wood"] = sc.make_pbr(stage, "/World/Looks/Wood",
                                diffuse_color=mp["wood_color"],
                                roughness_const=mp["wood_rough"])
        M["bollard"] = sc.make_pbr(stage, "/World/Looks/Bollard",
                                   diffuse_color=mp["bollard_color"],
                                   metallic=mp["bollard_metallic"],
                                   roughness_const=mp["bollard_rough"])
        M["water"] = sc.make_pbr(stage, "/World/Looks/Water",
                                 diffuse_color=mp["water_color"],
                                 roughness_const=mp["water_rough"], metallic=0.0)
        # v4-B2: water in 3 bands (roughness variation eases the uniform cyan slab)
        for bi, (_, _, rgh) in enumerate(PARAMS["water"]["bands"]):
            M[f"water_{bi}"] = sc.make_pbr(
                stage, f"/World/Looks/Water_{bi}",
                diffuse_color=mp["water_color"],
                roughness_const=rgh, metallic=0.0)
        # [v5.1 global convention 2] bollard top reflective band
        M["bollard_band"] = sc.make_pbr(
            stage, "/World/Looks/BollardBand",
            diffuse_color=mp["bollard_band"], metallic=0.2,
            roughness_const=mp["bollard_band_rough"])
        # materials used only by the v4 dressing
        # [v5.1] 3 shrub variants with +-5 % tint jitter (individual variation within a clump - instead
        #   of new materials, only diffuse_tint on the existing hedge_tint is shaken)
        M["hedge_v"] = [tex("grass", f"/World/Looks/Hedge{i}", 1.2,
                            tint=tint_jitter(mp["hedge_tint"], 30 + i))
                        for i in range(3)]
        M["hedge"] = M["hedge_v"][0]
        M["reed"] = tex("grass", "/World/Looks/Reed", 0.8,
                        tint=mp["reed_tint"])
        M["concrete_dark"] = sc.make_pbr(
            stage, "/World/Looks/ConcreteDark",
            diffuse_color=mp["concrete_dark"],
            roughness_const=mp["concrete_dark_rough"])
        # [v5 ruling applied] parapet-only tone (deck 0.28 vs parapet 0.22)
        M["concrete_parapet"] = sc.make_pbr(
            stage, "/World/Looks/ConcreteParapet",
            diffuse_color=mp["concrete_parapet"],
            roughness_const=mp["concrete_dark_rough"])
        # [GT-83 p2] recessed girder band (see the `concrete_girder` PARAMS note)
        M["concrete_girder"] = sc.make_pbr(
            stage, "/World/Looks/ConcreteGirder",
            diffuse_color=mp["concrete_girder"],
            roughness_const=mp["concrete_dark_rough"])
        # [GT-83] bridge carriageway (asphalt) - the only non-concrete tone on the crossing
        M["bridge_wear"] = sc.make_pbr(
            stage, "/World/Looks/BridgeWear",
            diffuse_color=mp["bridge_wear"],
            roughness_const=mp["bridge_wear_rough"])
        M["city"] = sc.make_pbr(stage, "/World/Looks/City",
                                diffuse_color=mp["city_color"],
                                roughness_const=0.8)
        M["city_glass"] = sc.make_pbr(stage, "/World/Looks/CityGlass",
                                      diffuse_color=mp["city_glass"],
                                      roughness_const=0.15)
        M["city_parapet"] = sc.make_pbr(stage, "/World/Looks/CityParapet",
                                        diffuse_color=mp["city_parapet"],
                                        roughness_const=0.7)
        M["line"] = sc.make_pbr(stage, "/World/Looks/Line",
                                diffuse_color=mp["line_color"],
                                roughness_const=0.75)
        M["gauge_band"] = sc.make_pbr(stage, "/World/Looks/GaugeBand",
                                      diffuse_color=mp["gauge_band"],
                                      roughness_const=0.6)
        # [v5.1] 4 crown variants (2 base colours x 2 jitters of +-5 %) - each tree gets a different pair.
        M["canopy"] = []
        for i, base in enumerate((mp["canopy_a"], mp["canopy_b"])):
            for j in range(2):
                M["canopy"].append(sc.make_pbr(
                    stage, f"/World/Looks/Canopy{i}{j}",
                    diffuse_color=tint_jitter(base, 10 * i + j),
                    roughness_const=mp["canopy_rough"], specular_level=0.0))
        M["canopy_a"], M["canopy_b"] = M["canopy"][0], M["canopy"][2]
        return M

    # -------------------------------------------------------------------
    # v4-B5: new-planting stakes on mature/distant trees are unrealistic -> stakes effectively removed.
    #   scene_common.build_tree always makes 3 stakes, so their dimensions are driven
    #   to near zero to neutralise them. (Proposal: add a stakes=False arg to build_tree - fix log)
    # -------------------------------------------------------------------
    def tree_no_stake(M, prefix, cx, cy, gz, trunk_h=2.2, slot=0, belt=False):
        """[v5.1] Swap the crown material pair per tree (shape·size·tilt variation is
        already done by scene_common.build_tree v2 from the coordinate seed).

        [v7 · 03-C / K4-F4] `belt=` is forwarded to `build_tree`. K4-F4 recorded that the
        declared belts of 03·07·09·10·17 are **inert until the scene passes the flag** — this
        scene passes it for the far-bank stand only, so `SCENE_SPECIES["Scene03"]` finally
        resolves as authored: route `poplar` on the near bank, belt `oak_black` across the
        water. Nothing is hard-coded here; the species table stays the single source of truth
        (`species="oak_black"` would fork it)."""
        ca, cb = ((0, 2), (1, 3), (2, 1), (3, 0))[int(slot) % 4]
        sc.build_tree(stage, prefix, cx, cy, gz, M["wood"], M["canopy"][ca],
                      M["canopy"][cb], trunk_h=trunk_h, belt=belt,
                      stake_r=0.004, stake_h=0.02, stake_off=0.2)

    # -------------------------------------------------------------------
    # [v5.1] meander band assembler - the only entry point for river-parallel elements
    # -------------------------------------------------------------------
    def river_band(prefix, s0, s1, z_top, thick, mtl, drop=0.0, y_gap=None,
                   max_w=4.0, z_bias=0.0, collider=True, mtl_fn=None):
        """Lay the cross-section span [s0,s1] as meandering polyline segs.

        · sub-band : split to at most max_w wide. The overlap lip between adjacent bands is
          (width sum/2)·(1/cos yaw − cos yaw), so the narrower the width the smaller it gets.
          max_w is small at borders where height/material change (levee crest↔slope,
          water↔far bank) and large on homogeneous background faces (inside the levee crest·far bank).
        · seg     : the river_segments() partition (shared by all bands). Each seg is an
          axis-aligned build_slope box inside
          build_rot_group(pivot=(seg top-face centre x, yc_ref), yaw).
          - local run = width/cos(yaw)  → world X projection of the top face = width (band alignment)
          - local y range = yc + (y_lo−yc)/cos, yc + (y_hi−yc)/cos (arc length correction)
            + over/2 overlap at every uncut end
        · z stagger: a 1.5 mm step (by sub-band·seg index parity) that stops Z-fighting in the
          coplanar overlap. A material border off by 1.5 mm is invisible at distance.
        With mtl_fn(j) the material is per sub-band (the 3-band water roughness variation, etc.).
        Returns: number of segs created."""
        mn = PARAMS["meander"]
        over, stag = mn["over"], mn["z_stagger"]
        width = s1 - s0
        nsub = max(1, int(math.ceil(abs(width) / max_w)))
        segs = river_segments(y_gap)
        n = 0
        for j in range(nsub):
            a = s0 + width * j / nsub
            b = s0 + width * (j + 1) / nsub
            zt_j = z_top - drop * (a - s0) / width if width else z_top
            drop_j = drop / nsub
            for i, (yc, ylo, yhi, clip_lo, clip_hi) in enumerate(segs):
                yaw = river_yaw(yc)
                cw = math.cos(math.radians(yaw))
                run = (b - a) / cw
                sx = river_dx(yc) + (a + b) / 2.0
                zt = zt_j + z_bias - stag * ((i + j) % 2)
                y_lo = yc + (ylo - yc) / cw - (0.0 if clip_lo else over / 2.0)
                y_hi = yc + (yhi - yc) / cw + (0.0 if clip_hi else over / 2.0)
                grp = sc.build_rot_group(stage, f"{prefix}/S{j}_{i}",
                                         (sx, yc), yaw)
                sc.build_slope(stage, f"{grp}/B", sx - run / 2.0, zt, run,
                               drop_j, y_lo, y_hi, thick,
                               mtl_fn(j) if mtl_fn else mtl,
                               margin=0.0, collider=collider)
                n += 1
        return n

    def river_prop(path, s, y, yaw_extra=0.0):
        """[v5.1] Rotation group for a single prop placed in the meander frame.
        (s, y) → world (s+dx(y), y), rotated by the local tangent + placement jitter."""
        return sc.build_rot_group(stage, path,
                                  (river_dx(y) + s, y),
                                  river_yaw(y) + yaw_extra)

    # -------------------------------------------------------------------
    # slope top z(x) - approximate landing height for shrubs (linear z0->z0-drop over x0..x0+run)
    # -------------------------------------------------------------------
    def slope_z(x):
        # [arm C] the fill IS the ground in the keep_dressing arm — the side
        #   slope is not built, so the shrub beds that read their landing height
        #   from here would otherwise be planted 0.69…1.83 m INSIDE a z=0 slab.
        #   Same switch as sceneC2's `terrain_z` (:941). This function has
        #   exactly two callers, both inside `build_dressing` (:2591, :2607), so
        #   nothing else in the scene changes; with the flag off it is unreached
        #   and the two lines below are byte-unchanged.
        if KEEP_DRESSING:
            return 0.0
        sl = PARAMS["slope"]
        t = max(0.0, min((x - sl["x0"]) / sl["run"], 1.0))
        return sl["z0"] - sl["drop"] * t

    # stair tread height (ground_fn for landing the rail posts) - matches build_straight_stairs
    def stair_ground(x):
        st = PARAMS["stairs"]
        x0, riser, tread, n = st["x0"], st["riser"], st["tread"], st["nsteps"]
        if x <= x0:
            return 0.0
        if x >= x0 + tread * n:
            return -riser * n
        idx = min(int((x - x0) / tread), n - 1)
        return -riser * (idx + 1)

    # -------------------------------------------------------------------
    # terrain·stair builders
    # -------------------------------------------------------------------
    def build_levee(M):
        """Levee crest: grass base + a river-parallel **점토블록 promenade** (4.0 m) with a
        light-grey block edge band (0.4 m) on its landward margin + the stair-head apron in
        the same paving. The paving is 1.5 mm proud of the top slab and 5 cm embedded.
        [v5.1] Every band follows the meander polyline. The sub-band touching the shoulder (s=0)
        is cut to 2.5 m to minimise the overlap lip against the slope; the land behind is 12 m wide.
        [P03 · GT-46] `LeveeRoad` (gravel) is renamed **`CrestWalk`** and `CrestBand` is new —
        the prim paths change with the archetype so a later reader is not told "road"."""
        lv = PARAMS["levee"]
        top = lv["z_top"]
        # [W2-0 · P-A] Crest slabs are what ground_kit decorates. river_band
        # builds them through `sc.build_slope`, which carries no displacement
        # skin today, so this is a forward guard (prefix match covers the
        # per-segment rot groups).
        sc.skin_exclude(f"{ROOT}/LeveeBack", f"{ROOT}/Levee",
                        f"{ROOT}/CrestWalk", f"{ROOT}/CrestBand",
                        f"{ROOT}/LeveeSpur")
        river_band(f"{ROOT}/LeveeBack", lv["x0"], -8.0, top, lv["thick"],
                   M["grass"], max_w=12.0)
        # the shoulder side is 2.5 wide - overlap lip against the slope = (2.5+3.5)/2·(1/cos−cos)
        #   = 0.46 m @yaw 23 deg (y~+-35) · 0.09 m @yaw 10 deg (y~+-10) · 0 @corridor.
        river_band(f"{ROOT}/Levee", -8.0, lv["x1"], top, lv["thick"],
                   M["grass"], max_w=2.5, z_bias=-0.0005)
        # 점토블록 promenade (river-parallel) - 1.5 mm proud of the top face · 5 cm embedded.
        #   max_w stays 3.5 (the crest hard band's existing convention), so a 4.0 m field
        #   splits into 2 x 2.0 m sub-bands: two narrow interfaces instead of one wide one,
        #   which is exactly the trade the river_band docstring prescribes at a material
        #   border. 2 sub-bands x 19 segs = 38 prims (was 1 x 19 = 19 for the gravel road).
        cw = PARAMS["crest_walk"]
        cb = PARAMS["crest_band"]
        z_top = top + cw["proud"]
        thick = cw["proud"] + cw["embed"]
        river_band(f"{ROOT}/CrestWalk", cw["x0"], cw["x1"], z_top,
                   thick, M["paving"], max_w=3.5)
        # light-grey block edge band on the LANDWARD margin (2 courses of the 200 mm module).
        #   Same top plane as the field — a kerb here would be a 4th longitudinal line and
        #   03 is one of the three kerbless-by-design scenes pending the S06-B photo check.
        river_band(f"{ROOT}/CrestBand", cb["x0"], cb["x1"], z_top,
                   thick, M["paving_band"], max_w=2.5)
        # stair-head apron (same 점토블록, s -1..0, y -1.2..1.2)
        #   Near the corridor dx~0 · yaw~0, so it stays axis-aligned (hazard geometry match).
        #   **Its top face does not move**: z_top is still `levee.z_top + 0.0015`, so the drop
        #   at x=0 stays 3.2015 m and the stair's first riser stays 0.1615 m. Only the
        #   material and the collider's bound material change.
        ls = PARAMS["levee_spur"]
        z_bot = top - cw["embed"]
        sc.add_box(stage, f"{ROOT}/LeveeSpur",
                   ((ls["x0"] + ls["x1"]) / 2.0, (ls["y0"] + ls["y1"]) / 2.0,
                    (z_top + z_bot) / 2.0),
                   (ls["x1"] - ls["x0"], ls["y1"] - ls["y0"], z_top - z_bot),
                   M["paving"], collider=True)

    # -------------------------------------------------------------------
    # [W2-D] ground_kit — P13 levee_paved forced natural (spec §5.7 row 03).
    #   Runs in both hazard arms: the hazard-off twin must carry the same
    #   ground elements for the GT-E4 comparison to mean anything.
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["gkit"]
        lv, cw = PARAMS["levee"], PARAMS["crest_walk"]
        z = lv["z_top"] + cw["proud"]
        gp = gk.plan_ground(
            "levee_paved",
            region=(g["x0"], -g["half_y"], lv["x1"], g["half_y"]),
            z=z, gy=0.0, origin=(0.0, 0.0, 0.0),
            edges=[("shoulder", float(lv["x1"]))],
            dists=(2, 5, 10), scene="scene03",
            tactile=(),                 # §12.4 - p=0.24 park/beach, not installed
            overrides=dict(
                # [P03] `natural` STAYS True — the surface is paved, the scene still
                #   carries zero urban infrastructure (G3 shows none on the promenade,
                #   and "03 stays kerbless pending the S06-B photo check" is still live).
                #   The flag is the code-enforced guard for exactly that; flipping it
                #   would *permit* what must stay out. See the `gkit` PARAMS comment.
                natural=True,
                infra=dict(manhole=0, gully=0, gutter_L=0, marking=()),
                # [P03] `module` is now declared truthfully (the crest IS blocks) and
                #   `joint` is still None — declined with measured groove coordinates in
                #   the `gkit` PARAMS comment, not by preference.
                pave=dict(module=(0.200, 0.100), joint=None,
                          step_x=None, step_y=None),
                # [v7 · 03-A + user ban] `("patch", 8)` removed; `sites` goes with it.
                #   `stain` stays — DEC-1 lobes, no straight edge, which is what trampled
                #   ground actually looks like. See the `gkit` PARAMS comment for the reach
                #   check against GT-24 (nil: this scene overrides `surface` itself).
                # **[v7, second pass — measured, not anticipated]** Deleting the patches
                #   turned out to strip the near window of its entire tonal budget: the
                #   site at (−1.10, 0.15) sat 0.90 m in front of the **h0.3 d2 judged eye**
                #   and filled the lower frame, so with it gone `near_ground_stats` read
                #   B30 `wht%` **6.8 → 39.3**, `σ_LF` **4.34 → 1.02**, mean **172 → 194** —
                #   an unbroken bright gravel field where a mottled surface used to be.
                #   That is a real blankness, not a metric artefact, and it is fixed with
                #   **the vocabulary the ban explicitly keeps** (§3(ii): soiling, litter and
                #   scatter are lobes and stay; only rectangles go):
                #     · `("weed", 8)` — P13's own post-GT-24 row prescribes 6; a levee
                #       crest margin is less maintained than a 둔치 promenade, and **G3
                #       shows weeds in every joint of the revetment and along both
                #       margins**, so 8 is the reference's direction, not an invention.
                #   **A `scatter` gravel field was tried here and REVERTED on the render.**
                #   It is left written down because the reasoning was sound and the result
                #   was not: `scatter=dict(kind="gravel", cover=0.08, count=130,
                #   scale_jitter=(0.38, 0.62), burial=0.38)` recovered the statistics well
                #   (`σ_LF` 1.02 → 3.35 at d2, and d5 4.14 → 5.66 = the only clean h0.3 cut
                #   in either arm) and looked **wrong**: `apply_ground` scatters over the
                #   whole plan region (−12…0, ±3), which on this crest is **mostly mown
                #   grass**, so the d5/d10 frames filled with pale 0.1–0.2 m stones strewn
                #   across a lawn. A levee crest has stone on its gravel track and none on
                #   its verge. Trading a blank floor for boulders on a lawn is a worse
                #   frame, so the statistics lose: the row is gone and the residual is
                #   handed to the material lane (`w3_s03_v1.md` §7-3) instead of being
                #   papered over. Re-open only if the kit gains a region-restricted scatter.
                # **[P03 · GT-46] That residual is now closed at its cause, and the scatter
                #   stays deleted — measured, not swapped.** §7-3's residual was never a
                #   missing-element problem; it was the **gravel scan's highlight tail**
                #   (`gravel_diff` lum p99 215.4 · >204 3.56 % against `paving_interlock`'s
                #   173.6 · 0.09 %, at the same 0.28 mean albedo). Paving the crest removes
                #   the near-white field itself, so the region-restricted scatter the S03
                #   lane asked the kit lane for is **no longer needed by this scene** —
                #   there is no gravel left in any h0.3 near window to restrict it to. The
                #   ask stays open for the kit's other natural-profile clients; it is simply
                #   not scene03's blocker any more. `("weed", 8)` is kept and is now
                #   *better* placed than before: G3 shows weeds in the paving joints and
                #   along both margins, which is exactly where the kit seeds them.
                surface=(("stain", ("dirt", "water")), ("weed", 8)),
                extras=(("wear_lane", dict(width=0.90)),)),
            extras_args=dict(wear_lane=dict(
                centerline=((g["wear_x"], -g["wear_y"]),
                            (g["wear_x"], g["wear_y"])))),
            seed=3)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        # [v7] `patch`/`patch_cut` keys stay bound even though the row is gone — the kit
        #   only reads a key when the element exists, and leaving them costs nothing while
        #   making the deletion reversible in one line. `weed` is the new key (the asset
        #   path is the kit's own `Shrub/Grass_Short_C.usd`; the material is only the
        #   procedural fallback), `debris` binds the scatter pool.
        # **[P03 · GT-47] `wear` is re-bound `dirt_park` -> the paving at x0.85.** The kit's
        #   own ledger says a wear lane is the road surface times `wear_albedo_gain` 0.85
        #   (`ground_kit.py:282`), i.e. **polished blocks**, not soil. `dirt_park` was right
        #   while the crest was gravel; on 점토블록 it would draw a 0.9 m mud streak straight
        #   down the middle of the promenade, inside the d5 near window.
        #   `edge_break` stays on `dirt` deliberately — that element *is* the soil/paving
        #   seam breaking up, so soil is its correct material.
        M2.update(patch=M["dirt"], patch_cut=M["dirt"], wear=M["paving_wear"],
                  stain_dirt=M["paving_soil"], stain_water=M["paving_wet"],
                  edge_break=M["dirt"], weed=M["hedge_v"][0],
                  debris=M["gravel"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        # edge break (spec §5.7 "edge break") - the hard/soft seam runs **along Y**,
        #   which `_compose_ops` cannot express (its `lines` are constant-y).
        #   Direct call, same builder, same z. `break_y` keeps the straight
        #   strip on the meandering seam: [v7, A1=10.0] |dx(2.4)| = 0.0946 m < the
        #   0.10 m half width of the transition band (at the old |y| <= 3.0 it
        #   would now be 0.1479 m — off the seam; see the `gkit` PARAMS comment).
        #   **[P03] The landward seam moves x -4.0 -> -5.4**: the paving/turf boundary is
        #   now the grey band's outer face, and that is the seam that needs breaking.
        #   The river-side seam at x=-1.0 is unchanged and is still NOT broken: it is
        #   1.0 m in front of the shoulder (drow = 5.65 rows @1080 at d10 against a
        #   16-row floor, i.e. exactly the band GT-E2 keeps clear), and for |y| <= 1.2 it
        #   is **paving-on-paving** (LeveeSpur takes the same 점토블록), so there is still
        #   no material boundary to break there.
        by = g["break_y"]
        nb = 0
        for tag, sx in (("W", PARAMS["crest_band"]["x0"]),):
            nb += gk.build_edge_break(
                kit, f"{ROOT}/GKit/EdgeBreak_{tag}",
                ((sx, -by), (sx, by)), z, M["dirt"])["prim_count"]
        print(f"[ground_kit] scene03 P13(paved crest · no urban infra) · "
              f"prims {res['prims']} + edge_break {nb} · "
              f"delta_max {res['gt_delta_max']:.4f}")
        return res

    def build_slopes(M):
        """Slope grass — the stair corridor is left empty and bands are assembled on both sides.
        [v5.1] The seg holding the corridor has yc=0 (yaw(0)=0 · dx(0)=0), so **both rotation
        and offset are 0** — the corridor border falls exactly on the straight lines y=±0.88.
        0.88 is used instead of 0.95 to bite 0.07 under the trim (y 0.75..0.95) and kill the seam
        line, while never intruding on the stair side 0.75 (verified: min corner |y|=0.88)."""
        sl = PARAMS["slope"]
        g = PARAMS["corridor"]["band_gap"]
        river_band(f"{ROOT}/Slope", sl["x0"], sl["x0"] + sl["run"], sl["z0"],
                   sl["thick"], M["grass"], drop=sl["drop"],
                   y_gap=(-g, g), max_w=3.5)

    def build_stairs(M):
        """Straight concrete stair, 20 steps. With cue_material_break OFF the stair takes the
        **crest's own surface**, so the ablation arm really has no material break.

        [P03 · GT-47] This is a live defect the paving exposed, not a cosmetic. The OFF branch
        was bound to `M["gravel"]` *because the crest was gravel*; against a 점토블록 crest it
        would have rendered **paving vs gravel — a material break in the arm whose entire
        purpose is to have none**, silently converting the ablation control into a second
        cue-on arm. The binding follows the crest, so it cannot drift again."""
        st = PARAMS["stairs"]
        stair_mtl = M["concrete"] if cfg["cue_material_break"] else M["paving"]
        sc.build_straight_stairs(
            stage, f"{ROOT}/Stairs", st["x0"], st["y0"], st["y1"],
            st["riser"], st["tread"], st["nsteps"], st["base_z"],
            stair_mtl, z_top=st["z_top"], collider=True)

    def build_trims(M):
        """Border trim on both sides of the stair: two 0.2-wide concrete sloped beams (y -0.95..-0.75 /
        0.75..0.95). The top face sits 0.05 above the stair nosing line (drop 2.56) — the finish
        between the slope grass and the stair."""
        st = PARAMS["stairs"]
        tr = PARAMS["trim"]
        # [GT-119 ①] The trim's inner face used to sit EXACTLY on the stair side
        # plane (y = ±0.75). Two coplanar faces — one stepped, one sloped — leave a
        # full-length sliver where neither wins, and the h0.3 stair_down cut read
        # the tread-end sawtooth against the pure-black under-stair void (audit
        # crop-confirmed, both sides). Cure: the trim now LAPS the tread ends by
        # `lap` — the way a real stair cheek sits over the tread end. Tread top z,
        # nosing line, drop registry and the outer trim face are unchanged; the
        # clear walking width narrows 1.50 → 1.46 (declared in the ledger row).
        lap = 0.02
        for tag, y0, y1 in (("N", -0.95, st["y0"] + lap),
                            ("P", st["y1"] - lap, 0.95)):
            sc.build_slope(stage, f"{ROOT}/Trim_{tag}", st["x0"], tr["z0"],
                           st["tread"] * st["nsteps"], tr["drop"], y0, y1,
                           tr["thick"], M["concrete"], margin=tr["margin"],
                           collider=True)
        assert st["y0"] + lap > st["y0"] and st["y1"] - lap < st["y1"], \
            "GT-119 ① trim lap must overlap the stair flank"
        print(f"[GT-119 ①] 계단 치크 랩 {lap:.3f} m — 유효 보행폭 "
              f"{(st['y1'] - st['y0']) - 2 * lap:.2f} m (측면 관통 슬롯 폐합)")

    def build_beach(M):
        """Beach, flat at z=-3.2 — two strips, dirt_park / grass (border s=12).
        [v5.1] All meander bands. At the material border (dirt↔grass) the overlap lip becomes the
        curvature of the border line itself, so max_w is kept small to hold the lip under 0.3 m."""
        bc = PARAMS["beach"]
        river_band(f"{ROOT}/BeachDirt", bc["x0"], bc["split_x"], bc["z_top"],
                   bc["thick"], M["dirt"], max_w=2.5)
        river_band(f"{ROOT}/BeachGrass", bc["split_x"], bc["x1"], bc["z_top"],
                   bc["thick"], M["grass"], max_w=3.0, z_bias=-0.002)
        # v4-A3: lower trail - river-parallel walkway s 9.4..12.4 (follows the curvature)
        bp = PARAMS["beach_path"]
        river_band(f"{ROOT}/BeachPath", bp["x0"], bp["x1"], bp["z_top"],
                   bp["thick"], M["dirt"], max_w=3.0)
        # apron linking the stair foot (s 7.0..9.4) to the walkway (y +-1.6)
        #   Near the corridor (dx~0), so it stays axis-aligned.
        sc.add_box(stage, f"{ROOT}/BeachSpur",
                   ((bc["x0"] + bp["x0"]) / 2.0, 0.0,
                    bp["z_top"] - bp["thick"] / 2.0),
                   (bp["x0"] - bc["x0"], 3.2, bp["thick"]),
                   M["dirt"], collider=True)
        # v4-D4: cycle track road markings (2 edge white lines + centre dashes) - follows the curvature
        pl = PARAMS["path_lines"]
        for i, ex in enumerate(pl["edge_x"]):
            river_band(f"{ROOT}/PathLine_{i}", ex - pl["w"] / 2.0,
                       ex + pl["w"] / 2.0, pl["z_top"], pl["thick"],
                       M["line"], max_w=pl["w"], collider=False)
        for k in range(pl["dash_n"]):
            yd = pl["dash_y0"] + pl["dash_step"] * k
            grp = river_prop(f"{ROOT}/PathDash_{k}", pl["mid_x"], yd)
            sc.add_box(stage, f"{grp}/Box",
                       (river_dx(yd) + pl["mid_x"], yd,
                        pl["z_top"] - pl["thick"] / 2.0),
                       (pl["w"], pl["dash_len"], pl["thick"]), M["line"])

    def build_riprap(M):
        """Riprap strip between water and beach: a low rock_wall sloped beam (drop 0.15).
        [v5.1] A meander band. The top (s17) is under the beach (−3.2) and the bottom (s18.2) drops
        below the water (−3.35), so both junctions always overlap = zero waterside floating."""
        rp = PARAMS["riprap"]
        river_band(f"{ROOT}/Riprap", rp["x0"], rp["x0"] + rp["run"], rp["z0"],
                   rp["thick"], M["rock"], drop=rp["drop"], max_w=1.4,
                   z_bias=-0.003)

    def build_river(M):
        """Water (roughness 0.08) + far bank (grass) + distant hedges·trees
        — the 'far side reappears' anchor · scale anchor · horizon closure."""
        wt = PARAMS["water"]
        # [v5.1] The 3 water bands are meander polylines too - the waterline shares the levee·beach curvature.
        #   Thickness raised to 0.4 (old build_water 0.2) so it bites firmly under the riprap
        #   and the far bank. A 1.5 mm stagger between bands avoids coplanar Z-fighting.
        for bi, (bs0, bs1, _) in enumerate(wt["bands"]):
            river_band(f"{ROOT}/Water_{bi}", bs0, bs1, wt["z"], 0.4,
                       M[f"water_{bi}"], max_w=WATER_MAX_W,
                       z_bias=-WATER_Z_STEP * bi, collider=False)
        # [GT-129] terminal end cap. The last seg's 32.27° yaw leaves the water assembly
        #   ending in a 12-tooth sawtooth (2.0 m of Y per 3.2 m sub-band) with nothing
        #   modelled behind it, so all three +Y-looking cuts silhouette a castellated water
        #   edge against the sky. One un-yawed slab per band, in that band's own material and
        #   3 mm under it, carries the surface across the notches to a **single straight end
        #   line** — the least invasive of the two directions in the audit, because the
        #   alternative (running the bands on to a far horizon) would put open water where
        #   the modelled world, banks included, simply stops at y ≈ 48.
        #   x span = exactly the band's own end corners (`river_end_geom`), so the caps butt
        #   each other on the same seams the bands already have and never reach past the
        #   channel; the near face sits `tuck` under live water. collider=False, like the
        #   bands: this is far-view silhouette only.
        for bi, (cx0, cx1, cy0, cy1, cz) in enumerate(water_end_cap()):
            sc.build_slope(stage, f"{ROOT}/WaterEnd_{bi}", cx0, cz,
                           cx1 - cx0, 0.0, cy0, cy1, 0.4,
                           M[f"water_{bi}"], margin=0.0, collider=False)
        fb = PARAMS["far_bank"]
        river_band(f"{ROOT}/FarBank", fb["x0"], fb["x1"], fb["z_top"],
                   fb["thick"], M["grass"], max_w=12.0)
        # v4-B3/D11: distant hedge strips -> 8 tree lines (removes the tiled hatching stripes)
        # [v7 · 03-C] `belt=True` -> Black_Oak (`SCENE_SPECIES` belt), a broad round crown
        #   against the near bank's columnar Lombardy_Poplar: **one silhouette class per
        #   bank**, which is the whole content of the carried "unnatural tree planting" item.
        #   `trunk_h` 3.0 -> 4.2: the stand receded from s38 to s56, i.e. from ~44 m to ~62 m
        #   from the levee_walk eye (factor 1.41), so the old height would have dropped the
        #   far tree line below G3's continuous horizon band. 4.2 x 1.60 = 6.7 m crown top.
        for i, t in enumerate(PARAMS["far_trees"]):
            tree_no_stake(M, f"{ROOT}/FarTree_{i}",
                          river_dx(t["cy"]) + t["cx"], t["cy"],
                          fb["z_top"], trunk_h=4.2, slot=i, belt=True)
        # v4-D1 [top priority]: distant crossing - crosses the river axis (Y) along X, so
        #   'river' is fixed in a single cut.
        # [v5.1] A bridge must **cross the river perpendicularly** -> the whole thing rotates by the
        #   local tangent angle at the deck centre y (river_prop), then the s->world X transform is applied.
        # **[GT-83] Raised to overpass clearance, moved off the levee-walk axis, and seated on
        #   an abutment at each end.**
        # **[GT-83 pass 2] Finished as a piece of engineering** — see the `bridge` PARAMS block.
        # **[GT-83 pass 3] The crossing is now ONE CONTINUOUS RIBBON, end to end**: south end
        #   bridgehead -> 6 river-parallel chords -> 11 transition chords -> the frozen main
        #   span -> the far wall pier -> the 23 m far approach -> the far end bridgehead. Both
        #   old abutments are wall piers now, because the carriageway runs over both of them.
        #   Every run is built by the SAME `deck_run` call, so the 9-part section (fascia ·
        #   girder · drip · parapet · coping · wear) is carried through all 29 joints without
        #   a member ever starting or stopping mid-ribbon.
        #   Member list and the joint rule each member obeys (nothing here changes the
        #   alignment, the deck level or the lateral position — `x0/x1/y0/y1/deck_top/
        #   deck_thick/parapet_h` are all untouched):
        #     Deck_Slab     thin fascia (deck_thick − girder_h = 0.38) — what the deck EDGE is
        #     Deck_Girder   girder band, recessed `girder_in` 0.30 behind each fascia and sunk
        #                   `z_stagger` into the slab -> a real shadow line, not a painted one
        #     Deck_Drip_S/N drip nose at the fascia bottom: 0.07 proud outboard, 0.04 inset INTO
        #                   the slab, hanging 0.02 below it -> no face coincides with any face
        #     Deck_Wear     asphalt carriageway, sunk `joint` into the deck AND into both
        #                   parapet inner faces
        #     Deck_Parapet_ guard wall, body only (parapet_h − cope_h), sunk `joint` into the deck
        #     Deck_Cope_    coping, `cope_out` proud on both faces, top at **exactly +4.00**
        #     Pier_i        column, foot −3.70 (buried), top sunk `z_stagger` into its cap
        #     PierCap_i     hammerhead cap, top sunk `cap_bite` into the soffit
        #     Head_*_*      bridgehead: footing -> (near) stone apron -> seat that stops at the
        #                   BEARING SHELF -> belt courses -> pedestals -> back wall -> approach
        #                   slab + wear -> two parapet end posts. The deck AND both parapets
        #                   still end `abut_t/2` = 1.10 m INSIDE the seat.
        #     Appr_*        23.0 m graded approach viaduct past the far head, on 2 more T-piers
        #     PierWall_*    both v7 abutments, cut down to wall piers because the carriageway
        #                   now runs OVER them (top sunk `cap_bite` into the girder band)
        #     NApp_i/R_*    the 17 near-approach chords, each in its own rot group, each
        #                   extended by its own mitre so the ribbon never opens a wedge
        #     NAppPier_j    T-piers at 4 of the chord joints
        #     Head_SEnd_*   the south end bridgehead at the modelled ground's south edge
        #   Every terminating member ends inside solid neighbouring geometry or in the ground;
        #   no cut face and no coincident face is left in the open.
        bg = PARAMS["bridge"]
        stag = PARAMS["meander"]["z_stagger"]
        jt = bg["joint"]
        deck_cy = (bg["y0"] + bg["y1"]) / 2.0
        deck_ly = bg["y1"] - bg["y0"]
        deck_lx = bg["x1"] - bg["x0"]
        deck_cx = (bg["x0"] + bg["x1"]) / 2.0
        soffit = bg["deck_top"] - bg["deck_thick"]
        parapet_top = bg["deck_top"] + bg["parapet_h"]
        bdx = river_dx(deck_cy)
        bgrp = river_prop(f"{ROOT}/Bridge", deck_cx, deck_cy)
        hy = deck_ly / 2.0
        fascia_t = bg["deck_thick"] - bg["girder_h"]

        def deck_run(prefix, ax0, ay, run, ztop, drop, collider=True):
            """[GT-83 pass 2/3] One carriageway run of the standard section, authored
            at (`ax0`, `ay`) in whatever group `prefix` lives under — the bridge group for the
            river span and the far approach, one per-chord rot group for the near approach.

            Every member is a `sc.build_slope` box whose TOP FACE is the plane
            (ax0, ztop) -> (ax0+run, ztop−drop), so the level river span (`drop`=0), the
            graded far approach and each near-approach chord come out of ONE code path and
            the section cannot drift between them — which is what lets the ribbon read as
            continuous through 29 joints. `margin=0.0`: runs are joined by authored `joint`
            and mitre overlaps, never by a builder's end margin."""
            sc.build_slope(stage, f"{prefix}_Slab", ax0, ztop, run, drop,
                           ay - hy, ay + hy, fascia_t,
                           M["concrete_dark"], margin=0.0, collider=collider)
            sc.build_slope(stage, f"{prefix}_Girder", ax0,
                           ztop - fascia_t + stag, run, drop,
                           ay - hy + bg["girder_in"], ay + hy - bg["girder_in"],
                           bg["girder_h"] + stag, M["concrete_girder"],
                           margin=0.0, collider=False)
            for sfx, sgn in (("S", -1.0), ("N", 1.0)):
                # drip nose: proud outboard, inset into the slab, 0.02 below the fascia
                sc.build_slope(stage, f"{prefix}_Drip_{sfx}", ax0,
                               ztop - fascia_t + bg["drip_h"] - 0.02, run, drop,
                               ay + sgn * (hy - bg["drip_in"]),
                               ay + sgn * (hy + bg["drip_out"]),
                               bg["drip_h"], M["concrete_dark"],
                               margin=0.0, collider=False)
                sc.build_slope(stage, f"{prefix}_Parapet_{sfx}", ax0,
                               ztop + bg["parapet_h"] - bg["cope_h"], run, drop,
                               ay + sgn * hy, ay + sgn * (hy - bg["parapet_w"]),
                               bg["parapet_h"] - bg["cope_h"] + jt,
                               M["concrete_parapet"], margin=0.0,
                               collider=collider)
                sc.build_slope(stage, f"{prefix}_Cope_{sfx}", ax0,
                               ztop + bg["parapet_h"], run, drop,
                               ay + sgn * (hy + bg["cope_out"]),
                               ay + sgn * (hy - bg["parapet_w"] - bg["cope_out"]),
                               bg["cope_h"] + stag, M["concrete_dark"],
                               margin=0.0, collider=False)
            sc.build_slope(stage, f"{prefix}_Wear", ax0,
                           ztop + bg["wear_t"], run, drop,
                           ay - hy + bg["parapet_w"] - jt,
                           ay + hy - bg["parapet_w"] + jt,
                           bg["wear_t"] + jt, M["bridge_wear"],
                           margin=0.0, collider=False)

        def wall_pier(prefix, ax, ay, top_z, width, apron=False, belts=False):
            """[GT-83 pass 3] A wall pier: spread footing -> (optionally) a stone scour apron
            -> body up to `top_z`, which is sunk `cap_bite` into the girder band so the
            carriageway runs OVER it with no gap. Both GT-83 abutments are this now."""
            foot_h = bg["foot_top"] - bg["foot_z0"]
            sc.add_box(stage, f"{prefix}_Foot",
                       (ax, ay, bg["foot_z0"] + foot_h / 2.0),
                       (bg["foot_t"], deck_ly + bg["foot_over"], foot_h),
                       M["concrete_dark"], collider=True)
            if apron:
                ap_h = bg["apron_top"] - (bg["foot_z0"] - 0.05)
                sc.add_box(stage, f"{prefix}_Apron",
                           (ax, ay, bg["foot_z0"] - 0.05 + ap_h / 2.0),
                           (bg["foot_t"] + 2.0 * bg["apron_xout"],
                            deck_ly + bg["foot_over"] + 2.0 * bg["apron_out"], ap_h),
                           M["rock"], collider=True)
            sc.add_box(stage, f"{prefix}_Body",
                       (ax, ay, bg["abut_z0"] + (top_z - bg["abut_z0"]) / 2.0),
                       (bg["abut_t"], width, top_z - bg["abut_z0"]),
                       M["concrete_dark"], collider=True)
            if belts:
                for i, dz in enumerate(bg["belt_dz"]):
                    sc.add_box(stage, f"{prefix}_Belt_{i}",
                               (ax, ay, top_z - dz - bg["belt_h"] / 2.0),
                               (bg["abut_t"] + 2.0 * bg["belt_out"],
                                width + 2.0 * bg["belt_out"], bg["belt_h"]),
                               M["concrete_dark"], collider=False)

        def bridgehead(tag, ax, ay, ztop, land_dir,
                       over=None, foot_over=None, prefix=None):
            """[GT-83 p2] A bank-seat bridgehead centred on authored (`ax`, `ay`), deck top `ztop`.

            `land_dir` = the sign of the authored-x direction in which the LAND (open) side
            lies (+1 for both end heads: the deck arrives from −x). The point of the member
            split is that the tall blank block of GT-83 becomes a **seat that stops at the
            bearing shelf**: everything above `bear_z` is a back wall, an approach slab and
            two end posts, each stepped in or out from its neighbour, so the silhouette is
            broken three times where it used to be one face. `over`/`foot_over` narrow the
            seat and footing where the ground is tight (the south head)."""
            d = float(land_dir)
            pre = prefix or f"{bgrp}/Head_{tag}"
            ov = bg["abut_over"] if over is None else over
            fov = bg["foot_over"] if foot_over is None else foot_over
            foot_h = bg["foot_top"] - bg["foot_z0"]
            bear_z = ztop - bg["deck_thick"] - bg["bear_h"]
            sc.add_box(stage, f"{pre}_Foot",
                       (ax, ay, bg["foot_z0"] + foot_h / 2.0),
                       (bg["foot_t"], deck_ly + fov, foot_h),
                       M["concrete_dark"], collider=True)
            seat_h = bear_z - bg["abut_z0"]
            sc.add_box(stage, f"{pre}_Seat",
                       (ax, ay, bg["abut_z0"] + seat_h / 2.0),
                       (bg["abut_t"], deck_ly + ov, seat_h),
                       M["concrete_dark"], collider=True)
            for i, dz in enumerate(bg["belt_dz"]):        # belt courses (lift lines)
                sc.add_box(stage, f"{pre}_Belt_{i}",
                           (ax, ay, bear_z - dz - bg["belt_h"] / 2.0),
                           (bg["abut_t"] + 2.0 * bg["belt_out"],
                            deck_ly + ov + 2.0 * bg["belt_out"],
                            bg["belt_h"]), M["concrete_dark"], collider=False)
            for i, sgn in enumerate((-1.0, 1.0)):          # bearing pedestals on the shelf
                sc.add_box(stage, f"{pre}_Ped_{i}",
                           (ax - d * 0.55, ay + sgn * bg["ped_y"],
                            bear_z + (bg["bear_h"] - stag) / 2.0),
                           (bg["ped_t"], bg["ped_w"], bg["bear_h"] + 2.0 * stag),
                           M["concrete_dark"], collider=False)
            # everything the head carries at road level sits `z_stagger` under the deck top,
            #   so no head member has a face coplanar with the deck it meets (the 1.5 mm step
            #   is the expansion joint a real deck end has anyway).
            z_road = ztop - stag
            back_h = z_road - (bear_z - 0.10)              # back wall (흉벽)
            sc.add_box(stage, f"{pre}_Back",
                       (ax + d * (bg["abut_t"] / 2.0 - bg["back_in"]
                                  - bg["back_t"] / 2.0),
                        ay, bear_z - 0.10 + back_h / 2.0),
                       (bg["back_t"], deck_ly + bg["back_w_off"], back_h),
                       M["concrete_dark"], collider=True)
            # approach slab: overhangs the seat face by `slab_out` (a nose, not a cut) and
            #   bites 0.05 into the deck end; its asphalt stops `slab_wear_in` short of the
            #   nose, leaving the concrete lip a real 접속슬래브 shows.
            sl_len = bg["abut_t"] / 2.0 + bg["slab_out"] + 0.05
            sl_c = ax + d * (bg["abut_t"] / 2.0 + bg["slab_out"] - sl_len / 2.0)
            sc.add_box(stage, f"{pre}_Slab",
                       (sl_c, ay, z_road - bg["slab_t"] / 2.0),
                       (sl_len, deck_ly, bg["slab_t"]),
                       M["concrete_dark"], collider=True)
            wr_len = sl_len - bg["slab_wear_in"]
            sc.add_box(stage, f"{pre}_Wear",
                       (sl_c - d * bg["slab_wear_in"] / 2.0, ay,
                        z_road + (bg["wear_t"] - jt) / 2.0),
                       (wr_len, deck_ly - 2.0 * (bg["parapet_w"] - jt),
                        bg["wear_t"] + jt), M["bridge_wear"])
            # parapet end posts: 0.025 m proud of the coping on both faces, and long enough
            #   to bury the parapet AND coping end faces. Top = parapet top + `z_stagger`,
            #   i.e. the same 1.5 mm the GT-83 abutment used — nothing rises above +4.00.
            post_c = ax + d * (bg["abut_t"] / 2.0 - 0.10 - bg["post_t"] / 2.0)
            post_z0 = bear_z - 0.16            # 0.06 off the back wall's own base plane
            post_h = (ztop + bg["parapet_h"] + stag) - post_z0
            for sfx, sgn in (("S", -1.0), ("N", 1.0)):
                sc.add_box(stage, f"{pre}_Post_{sfx}",
                           (post_c, ay + sgn * (hy - bg["parapet_w"] / 2.0),
                            post_z0 + post_h / 2.0),
                           (bg["post_t"], bg["post_w"], post_h),
                           M["concrete_dark"], collider=True)

        deck_run(f"{bgrp}/Deck", bdx + bg["x0"], deck_cy, deck_lx,
                 bg["deck_top"], 0.0)
        # T-piers: column + hammerhead cap. Cap width 7.40 < deck 9.00, so the deck keeps a
        #   0.80 m cantilever each side and the cap does not show past the parapet line.
        cap_top = soffit + stag
        cap_bot = cap_top - bg["cap_h"]
        col_h = (cap_bot + stag) - bg["pier_z0"]
        for i, px in enumerate(bg["pier_x"]):
            sc.add_cylinder(stage, f"{bgrp}/Pier_{i}",
                            (bdx + px, deck_cy, bg["pier_z0"] + col_h / 2.0),
                            bg["pier_r"], col_h, M["concrete_dark"],
                            collider=True)
            sc.add_box(stage, f"{bgrp}/PierCap_{i}",
                       (bdx + px, deck_cy, cap_bot + bg["cap_h"] / 2.0),
                       (bg["cap_t"], bg["cap_w"], bg["cap_h"]),
                       M["concrete_dark"], collider=True)
        # ---- both banks: the crossing does NOT stop at either bank ------------------
        # **[GT-83 pass 3]** Both GT-83 abutments become **wall piers**, because the
        #   carriageway runs over both of them now. Each top is sunk `cap_bite` into the
        #   girder band, so the graded approach soffit meets it without a gap at either edge
        #   (the soffit falls at most 0.05 m over the pier's own 2.20 m length).
        #   The near one keeps the pass-2 stone apron and belt courses: it still stands on the
        #   floodplain and is still the tallest thing in `meander_air`'s right-hand band, but
        #   it is a 5.05 m pier now, not a 7.45 m dead end.
        appr_len = bg["appr_len"]
        appr_drop = bg["appr_grade"] * appr_len
        wp_top = soffit + bg["cap_bite"]
        wall_pier(f"{bgrp}/PierWall_Near", bdx + bg["x0"], deck_cy, wp_top,
                  bg["pier_near_w"], apron=True, belts=True)
        wall_pier(f"{bgrp}/PierWall_Far", bdx + bg["x1"], deck_cy, wp_top,
                  bg["pier_far_w"])
        # far approach viaduct. It starts `joint` BEFORE x1, with its profile raised by
        #   `joint`·grade and then dropped by one `z_stagger`: at x1 the two runs overlap by
        #   0.02 m with the approach 1.5 mm low, so **no pair of faces is coincident** and the
        #   grade break sits exactly on the pier the two runs share.
        deck_run(f"{bgrp}/Appr", bdx + bg["x1"] - jt, deck_cy, appr_len + jt,
                 bg["deck_top"] + bg["appr_grade"] * jt - stag,
                 bg["appr_grade"] * (appr_len + jt))
        for i, pt in enumerate(bg["appr_pier_x"]):
            a_sof = soffit - bg["appr_grade"] * pt
            a_cap_top = a_sof + bg["cap_bite"]
            a_cap_bot = a_cap_top - bg["cap_h"]
            a_col_h = (a_cap_bot + stag) - bg["pier_z0"]
            sc.add_cylinder(stage, f"{bgrp}/ApprPier_{i}",
                            (bdx + bg["x1"] + pt, deck_cy,
                             bg["pier_z0"] + a_col_h / 2.0),
                            bg["pier_r"], a_col_h, M["concrete_dark"],
                            collider=True)
            sc.add_box(stage, f"{bgrp}/ApprPierCap_{i}",
                       (bdx + bg["x1"] + pt, deck_cy,
                        a_cap_bot + bg["cap_h"] / 2.0),
                       (bg["cap_t"], bg["cap_w"], bg["cap_h"]),
                       M["concrete_dark"], collider=True)
        # far end bridgehead, on the far bank 1.4 m inside the modelled ground edge. Its deck
        #   top is read off the approach's own profile, `z_stagger` included, so the
        #   approach's end face is buried 1.10 m inside the seat with nothing coincident.
        bridgehead("End", bdx + bg["x1"] + appr_len, deck_cy,
                   bg["deck_top"] - appr_drop - stag, 1.0)
        # ---- near approach: the curved southward viaduct [GT-83 pass 3] --------------
        # The ribbon is a chord polyline (`near_approach_chords`), one rot group per chord,
        #   each carrying the SAME `deck_run` section as the frozen span. Three things make
        #   it read as one continuous form rather than 17 boxes:
        #     · **mitre overlaps** — every chord is extended by `back`/`fwd` =
        #       (4.55) · tan(kink/2) at each end, so consecutive boxes interpenetrate and the
        #       wedge that a plain butt joint would open on the outside of the turn is filled.
        #       Chord 0's back extension is `napp_lead` 1.30 m > `abut_t`/2, so the frozen
        #       deck's own end face is buried inside it.
        #     · **eased steps** — 2.25° at the bridgehead, 9.00° max anywhere.
        #     · **one profile** — `near_approach_chords` hands each chord its own start/end
        #       elevation off a single parabolic-then-constant curve, so the grade is 0 where
        #       it leaves the level span and there is no pitch step anywhere.
        nchords, s_hold = near_approach_chords()
        for c in nchords:
            g_i = (c["z0"] - c["z1"]) / c["L"] if c["L"] > 1e-9 else 0.0
            run = c["back"] + c["L"] + c["fwd"]
            grp = sc.build_rot_group(stage, f"{ROOT}/NApp_{c['i']}",
                                     (c["mx"], c["my"]), c["brg"])
            deck_run(f"{grp}/R", c["mx"] - c["L"] / 2.0 - c["back"], c["my"],
                     run, c["z0"] + g_i * c["back"], g_i * run)
            if c["i"] in bg["napp_pier_j"]:
                # T-pier at this chord's START joint, authored inside the chord's own group
                # so the hammerhead cap is square to the ribbon it carries.
                n_sof = c["z0"] - bg["deck_thick"]
                n_cap_top = n_sof + bg["cap_bite"]
                n_cap_bot = n_cap_top - bg["cap_h"]
                n_col_h = (n_cap_bot + stag) - bg["pier_z0"]
                sc.add_cylinder(stage, f"{grp}/NAppPier",
                                (c["mx"] - c["L"] / 2.0, c["my"],
                                 bg["pier_z0"] + n_col_h / 2.0),
                                bg["pier_r"], n_col_h, M["concrete_dark"],
                                collider=True)
                sc.add_box(stage, f"{grp}/NAppPierCap",
                           (c["mx"] - c["L"] / 2.0, c["my"],
                            n_cap_bot + bg["cap_h"] / 2.0),
                           (bg["cap_t"], bg["cap_w"], bg["cap_h"]),
                           M["concrete_dark"], collider=True)
        # south end bridgehead, at the modelled ground's south edge (y −45.8, 1.7 m inside
        #   the y −47.5 band end). Narrowed seat/footing — see `send_over` in PARAMS.
        last = nchords[-1]
        sgrp = sc.build_rot_group(stage, f"{ROOT}/NAppHead",
                                  (last["x1"], last["y1"]), last["brg"])
        bridgehead("SEnd", last["x1"], last["y1"], last["z1"], 1.0,
                   over=bg["send_over"], foot_over=bg["send_foot_over"],
                   prefix=f"{sgrp}/Head_SEnd")
        # v4-D2: 3 far-side city blocks (base_z = far_bank top −3.2)
        # [v5.1] meander tangent + per-block yaw jitter (global convention 3 - no axis-aligned row of 3)
        for key, bd in PARAMS["city"].items():
            bcy = (bd["y0"] + bd["y1"]) / 2.0
            cdx = river_dx(bcy)
            cgrp = river_prop(f"{ROOT}/City_{key}", (bd["x0"] + bd["x1"]) / 2.0,
                              bcy, yaw_extra=bd.get("jyaw", 0.0))
            shifted = dict(bd)
            shifted["x0"] = bd["x0"] + cdx
            shifted["x1"] = bd["x1"] + cdx
            shifted["facade_x"] = bd["facade_x"] + cdx
            sc.build_building(stage, f"{cgrp}/B", shifted, M["city"],
                              M["city_glass"], M["city_parapet"])

    def build_flat_fill(M):
        """hazard_stairs=False control: stair·slope·beach unified to z=0 flat ground
        (flat ground from the levee crest to x18). Drop/hazard removed.
        Note: water·far bank remain as far-view elements — for a fully flat control,
        combine with cue_scene_dressing=False (skip build_river too to remove the waterside).

        [P03 · GT-47] The fill material follows the **stair-head apron**, not a literal.
        The invariant this control has to hold is that **no line appears at x = 0 where the
        drop used to be**: the apron (|y| <= 1.2, i.e. the whole hazard corridor y ±0.95 the
        label is read from) meets the fill there. It was gravel-on-gravel; after GT-46 the
        apron is 점토블록, so a `gravel` fill would have drawn a fresh material line straight
        across the corridor in the twin that exists to have none."""
        lv = PARAMS["levee"]
        bc = PARAMS["beach"]
        # [v5.1] The control must be laid with the same meander bands or the levee-crest seam misses.
        river_band(f"{ROOT}/FlatFill", 0.0, bc["x1"], lv["z_top"],
                   lv["thick"], M["paving"], max_w=4.0)

    # -------------------------------------------------------------------
    # prop builders (cue_scene_dressing)
    # -------------------------------------------------------------------
    def build_dressing(M):
        # [arm C] LOWER-ANCHOR DATUM. `build_flat_fill` lays ONE z=0 slab from
        #   the levee crest out to `beach.x1` = 18.0, so in the keep_dressing arm
        #   the beach IS z=0 and every prop the ON arm stands on the beach must
        #   ride the fill instead of being buried 3.20 m under it — the same
        #   switch scene12's isolated port makes with `lz` (:2070) and sceneC2
        #   with `Z_LOW` (:666). The test is an EXACT match against
        #   `beach.z_top`, not a threshold: the four beach anchors in PARAMS
        #   (`benches` rows 2-3, `trees` via `bz`, `trees_extra` rows 3-5,
        #   `reeds.base_z`) are all authored as that same literal −3.2.
        #   NOT remapped, on purpose: `gauge` (z0 −3.35) is driven into the
        #   RIVERBED, not the beach, and the river is unchanged in this arm.
        #   With the flag off `kd_z` is the identity and returns its argument
        #   unchanged, so every call site below is byte-identical to the
        #   pre-patch expression.
        _BZ_ON = PARAMS["beach"]["z_top"]

        def kd_z(z):
            return 0.0 if (KEEP_DRESSING and abs(z - _BZ_ON) < 1e-9) else z

        # 2 levee-crest bollards (either side of the spur - stop vehicles at the stair entry).
        # [v5.1 global convention 2] h 0.90 · r 0.075 · white reflective band on top.
        bo = PARAMS["bollard"]
        for i, b in enumerate(PARAMS["bollards"]):
            bx = river_dx(b["cy"]) + b["cx"]
            sc.build_bollard(stage, f"{ROOT}/Bollard_{i}", bx, b["cy"], 0.0,
                             mtl=M["bollard"], radius=bo["r"],
                             height=bo["h"])
            sc.add_cylinder(stage, f"{ROOT}/BollardBand_{i}",
                            (bx, b["cy"], bo["band_z"] + bo["band_h"] / 2.0),
                            bo["r"] * 1.04, bo["band_h"], M["bollard_band"])
            sc.add_cylinder(stage, f"{ROOT}/BollardCap_{i}",
                            (bx, b["cy"], bo["h"] + 0.015),
                            bo["r"] * 1.15, 0.03, M["bollard"])
        # v4-D7: 4 benches (2 levee crest + 2 beach) - [v5.1] asymmetric placement beside anchors,
        #   yaw = local tangent + a given (non-integer) angle.
        for i, (bx, by, bz_, yaw) in enumerate(PARAMS["benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{i}", river_dx(by) + bx, by,
                           kd_z(bz_), M["wood_dark"], yaw=yaw + river_yaw(by))
        # v4-B1 / [v5.1 re-fix]: slope shrubs = 3 overlapping flattened ellipsoids.
        #   The sloped slab (v4) was identified as an 'angular slab' in the v5 ruling, so it is dropped.
        #   The gradient enters only via placement height (slope_z) - an axis-aligned solid of revolution has no cut face.
        # [v7 · 03-D] Real shrub USDs replace the ellipsoids. **One `place_shrubs` call for
        #   the whole slope band = one bed**, which is deliberate under K4(b) S-2: the draw is
        #   per bed, so six separate calls could stand Holly on three clumps and Privet on the
        #   other three — two silhouettes on one continuous 25 m slope, exactly the mixed
        #   border the rule exists to forbid. One call also keeps the per-point scale/yaw
        #   sequence varied, where six same-seed calls would clone one clump six times
        #   (global convention 3, no grids).
        hb = PARAMS["hedge"]
        emb = hb["embed"]
        shrub_pts = [(river_dx(h["cy"] + dy) + h["cx"] + dx, h["cy"] + dy,
                      slope_z(h["cx"] + dx))
                     for h in PARAMS["hedges"]
                     for (dx, dy, _rx, _ry, _rz) in hb["blobs"]]
        placed_sh = sc.place_shrubs(stage, f"{ROOT}/Shrub", shrub_pts,
                                    float(hb["target_h"]),
                                    species=hb["species"],
                                    seed=gk.det_seed("scene03.shrub", 0))
        if not placed_sh:
            # Assets absent or LOOK_GEO=0 -> the v5.1 ellipsoids, unchanged. A missing asset
            # must degrade, not empty the slope (scene10 precedent, `:2394-2404`).
            for i, h in enumerate(PARAMS["hedges"]):
                for j, (dx, dy, rx, ry, rz) in enumerate(hb["blobs"]):
                    cx = h["cx"] + dx
                    cy = h["cy"] + dy
                    sc.add_sphere(stage, f"{ROOT}/Hedge_{i}_{j}",
                                  (river_dx(cy) + cx, cy,
                                   slope_z(cx) + rz * (1.0 - emb)),
                                  (rx, ry, rz),
                                  M["hedge_v"][(i + j) % len(M["hedge_v"])])
        print(f"[03-D] 사면 관목 {placed_sh}/{len(shrub_pts)}주 "
              f"(place_shrubs · 1 bed · role {hb['species']} · h {hb['target_h']} m)"
              if placed_sh else
              f"[03-D] 관목 에셋 부재 -> 타원체 폴백 {len(shrub_pts)}개")
        # 2 beach trees (crown top below the levee-crest eye height - anchor) + 6 more from v4-D10
        bz = kd_z(PARAMS["beach"]["z_top"])
        for i, t in enumerate(PARAMS["trees"]):
            tree_no_stake(M, f"{ROOT}/Tree_{i}", river_dx(t["cy"]) + t["cx"],
                          t["cy"], bz, slot=i)
        for i, t in enumerate(PARAMS["trees_extra"]):
            tree_no_stake(M, f"{ROOT}/TreeX_{i}", river_dx(t["cy"]) + t["cx"],
                          t["cy"], kd_z(t["gz"]), slot=i + 2)
        # v4-D5: reed band (waterline transition) - [v5.1] meander band following the waterline curvature
        # [GT-83] `y_gap` cuts the band open across the near bridgehead. `river_segments`
        #   drops a seg wholly inside the gap and clips the two straddling it (their
        #   clip_lo/clip_hi flags suppress the usual `over` extension), so the cut ends land
        #   on the gap line instead of overshooting into the abutment.
        rd = PARAMS["reeds"]
        river_band(f"{ROOT}/Reed", rd["x0"], rd["x1"],
                   kd_z(rd["base_z"]) + rd["h"],
                   rd["h"], M["reed"], max_w=1.0, collider=False,
                   y_gap=rd["y_gap"])
        # v4-D6: levee-crest cycle track centre line + 2 distance markers
        # [v7] The centre-line band is deleted with its parameter (see PARAMS `levee_line`):
        #   a painted marking on a gravel maintenance track, and the last fragment of a cycle
        #   track the 07-29 ruling took off this scene. The marker builder below stays (the
        #   list has been empty since v5.2 §6; refill it and the posts come back).
        mk = PARAMS["marker"]
        for i, (ms, my, jy) in enumerate(PARAMS["markers"]):
            mx = river_dx(my) + ms
            grp = river_prop(f"{ROOT}/Marker_{i}", ms, my, yaw_extra=jy)
            sc.add_cylinder(stage, f"{grp}/Post",
                            (mx, my, mk["post_h"] / 2.0), mk["post_r"],
                            mk["post_h"], M["bollard"], collider=True)
            sc.add_box(stage, f"{grp}/Plate",
                       (mx, my, mk["plate_z"]), mk["plate"], M["line"])
        # v4-D7: 1 pergola (a rest spot = somewhere people come)
        pg = PARAMS["pergola"]
        pcy = (pg["y0"] + pg["y1"]) / 2.0
        pdx = river_dx(pcy)
        pgrp = river_prop(f"{ROOT}/Pergola", (pg["x0"] + pg["x1"]) / 2.0, pcy,
                          yaw_extra=pg["jyaw"])
        sc.build_canopy(stage, f"{pgrp}/C", pg["x0"] + pdx, pg["x1"] + pdx,
                        pg["y0"], pg["y1"], pg["z_roof"], pg["post_r"],
                        M["wood_dark"], M["wood_dark"], roof_t=pg["roof_t"],
                        base_z=0.0)
        # v4-D8: beach sports-field lines (4 lines of a rectangle) - a rigid rectangle, so rotated as one
        # [v7] Deleted with its parameter — the one literal painted rectangle in this scene
        #   (see PARAMS `field`). `M["line"]` is still used by `path_lines`, so the material
        #   stays; only this block goes.
        # v4-D9: water-level gauge (white post + 3 red bands)
        gg = PARAMS["gauge"]
        gh = gg["z1"] - gg["z0"]
        gx = river_dx(gg["cy"]) + gg["cx"]
        sc.add_cylinder(stage, f"{ROOT}/Gauge/Post",
                        (gx, gg["cy"], gg["z0"] + gh / 2.0), gg["r"],
                        gh, M["line"], collider=True)
        for i, gz in enumerate(gg["band_z"]):
            sc.add_cylinder(stage, f"{ROOT}/Gauge/Band_{i}",
                            (gx, gg["cy"], gz), gg["r"] * 1.06,
                            gg["band_h"], M["gauge_band"])

    # -------------------------------------------------------------------
    # cue builders (cue_railing / cue_nosing / cue_tactile)
    # -------------------------------------------------------------------
    def build_cues(M):
        st = PARAMS["stairs"]
        run = st["tread"] * st["nsteps"]           # 20×0.35 = 7.0
        drop = st["riser"] * st["nsteps"]          # 20×0.16 = 3.2
        # cue_railing (identity): if True, one pipe rail on the stair right at y=+0.85 only
        if cfg["cue_railing"]:
            sc.build_railing_line(
                stage, f"{ROOT}/Rail", 0.85, -1.0, st["x0"], run, drop,
                stair_ground, M["rail"], rail_h=0.9)
        # cue_nosing (new): non-slip nosing strip on every step
        if cfg["cue_nosing"]:
            sc.build_nosing(
                stage, f"{ROOT}/Nosing", st["x0"], st["y0"], st["y1"],
                st["riser"], st["tread"], st["nsteps"], base_z=st["base_z"],
                z_top=st["z_top"])
        # cue_tactile (unused here - code path only): yellow strip 0.3m before the levee-crest shoulder
        if cfg["cue_tactile"]:
            sc.build_tactile(stage, f"{ROOT}/Tactile", st["x0"] - 0.3,
                             st["x0"], st["y0"], st["y1"],
                             sc.make_pbr(stage, f"{ROOT}/TactileMtl",
                                         sc.tex_path("gravel", "diff"),
                                         sc.tex_path("gravel", "nor"),
                                         sc.tex_path("gravel", "rough"), 0.3,
                                         tint=(1.6, 1.3, 0.2)), z=0.0)

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_levee(M)
    if cfg["hazard_stairs"]:
        build_slopes(M)
        build_stairs(M)
        build_trims(M)
        build_beach(M)
        build_riprap(M)
    elif KEEP_DRESSING:
        # [arm C] hazard-only removal. The C and D grounds are the SAME slab
        #   here — `build_flat_fill` already lays the meander-banded z=0 fill
        #   from the crest to x18 and there is no cue builder inside the hazard
        #   branch to restore (`build_cues` is unconditional at :2715). The
        #   branch exists anyway for two reasons: it is where the arm is
        #   declared for `grep KEEP_DRESSING`, and it pins C's ground so a later
        #   D-only edit to the `else` arm cannot silently follow C.
        #   What actually separates C from D in this scene is `build_dressing`
        #   below — see the guard at :2713.
        build_flat_fill(M)
    else:
        build_flat_fill(M)          # control: everything flattened to z=0
    build_ground_kit(M)             # [W2-D] both arms — GT-E4 twin parity
    build_river(M)                  # water·far bank are always on (far-view evidence)
    # [arm C · CUE_COVERAGE §4-4 rule (3)] the `and cfg["hazard_stairs"]` term is
    #   what makes this scene binding class HZ: the entire dressing layer dies
    #   with the drop, so without `or KEEP_DRESSING` on the SAME line arm C would
    #   be a byte-identical duplicate of arm D. Dressing is not hazard geometry —
    #   bollards, benches, shrubs, trees, reeds, pergola and the gauge are all
    #   free-standing props — so it comes back over the fill, with the beach-
    #   anchored ones lifted to the fill top by `kd_z` inside `build_dressing`.
    if cfg["cue_scene_dressing"] and (cfg["hazard_stairs"] or KEEP_DRESSING):
        build_dressing(M)
    build_cues(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # ── camera + render mode ──
    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["levee_walk"]
    look_from(_v0["eye"], _v0["tgt"])              # start camera = mise-en-scene

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

    def capture(path):
        vp = get_active_viewport()
        capture_viewport_to_file(vp, file_path=path)

    # ===================================================================
    # auto capture mode (headless verification pipeline - scene_common.capture_pipeline)
    # ===================================================================
    if capture_mode:
        out_dir_default = os.path.join(LOOKCHECK_DIR, "auto")
        sc.capture_pipeline(simulation_app, build_views(), out_dir_default,
                            set_render_mode, look_from)
        simulation_app.close()
        return

    # ===================================================================
    # GUI look check mode (default)
    # ===================================================================
    input_iface = carb.input.acquire_input_interface()
    appwindow = omni.appwindow.get_default_app_window()
    K = carb.input.KeyboardInput
    rot_step = float(PARAMS["light"]["dome_rotation_step"])
    dome_user_rot = [0.0]                           # [ / ] key user offset

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene03_{ts}.png")
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
