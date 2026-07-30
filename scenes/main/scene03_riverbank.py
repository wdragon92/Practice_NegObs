# -*- coding: utf-8 -*-
"""
scene03_riverbank.py — NegObs synthetic scene 3: river levee descending stair (Isaac Sim 4.5)

Spec   : Docs/multi_scene_brief_v2.md §C(scene03_riverbank) — sole spec
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
    water=dict(x0=16.5, y0=-40.0, x1=54.0, y1=40.0, z=-3.35,
               bands=((16.5, 26.0, 0.06), (26.0, 38.0, 0.10),
                      (38.0, 54.0, 0.15))),
    far_bank=dict(x0=52.0, x1=88.0, y0=-40.0, y1=40.0, z_top=-3.2, thick=0.4),
    # v4-B3/D11: 3 far_hedge slabs (60 m grass-texture strips) drew regular hatching stripes
    #   on the horizon and read as a printed backdrop -> replaced by 7 tree lines.
    # [v5.1] The waterline moved in to s34, so the tree line moves to s38. An even 10 m
    #   spacing would break global convention 3 (no grids), so spacing·offset are irregular.
    # [v7] Far bank at s52 -> the tree line rides it out to s56 (same +4 m stand-off). The
    #   irregular per-tree dx offsets are carried over unchanged (convention 3).
    far_trees=[dict(cx=56.0 + dxo, cy=cy) for dxo, cy in
               ((0.0, -31.0), (1.8, -22.5), (-1.2, -13.0), (2.4, -3.0),
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
    trees_extra=[dict(cx=-8.0, cy=-7.0, gz=0.0), dict(cx=-8.0, cy=7.0, gz=0.0),
                 dict(cx=-14.0, cy=0.0, gz=0.0),
                 dict(cx=9.0, cy=-10.0, gz=-3.2), dict(cx=14.5, cy=-24.0, gz=-3.2),
                 dict(cx=9.0, cy=12.0, gz=-3.2)],

    # === v4-D context dressing (so it reads as a river levee) ===
    # D1 [top priority] distant bridge - fixes 'river' in one cut. The river axis is Y, so the bridge crosses along X.
    # [v7] The deck must still land on BOTH banks after the widening: x1 46 -> 64 (the far
    #   bank now starts at s52, so 12 m of deck sits over land on the far side, as before).
    #   Piers go 5 -> 7 at the same 8.0 m bay (14·22·30·38·46·54·62) — a bridge is the one
    #   place a constant pitch is correct, and G3 shows exactly that: a long low girder deck
    #   on a regular pier line.
    bridge=dict(x0=12.0, x1=64.0, y0=-22.5, y1=-13.5, deck_top=-0.2,
                deck_thick=0.8, parapet_h=0.9, parapet_w=0.3,
                pier_r=1.2,
                pier_x=(14.0, 22.0, 30.0, 38.0, 46.0, 54.0, 62.0),
                pier_z0=-3.7),
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
    reeds=dict(x0=16.0, x1=17.0, h=0.9, base_z=-3.2),
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
    # (placed in the +Y far view so it misses the bridge y −22.5..−13.5 · benches y +-6)
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
        concrete_dark=(0.28, 0.28, 0.275), concrete_dark_rough=0.8,   # v4-D1 bridge deck·piers
        concrete_parapet=(0.22, 0.22, 0.215),                         # bridge parapet (guard wall)
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
    #    levee crest promenade, looking upstream. It starts north of the bridge (y −22.5..−13.5) so nothing blocks the view.
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
    bg = PARAMS["bridge"]
    b_cy = (bg["y0"] + bg["y1"]) / 2.0
    b_xm = (bg["x0"] + bg["x1"]) / 2.0
    bdx = river_dx(b_cy)
    b_yawd = river_yaw(b_cy)
    b_piv = (bdx + b_xm, b_cy)
    rot_boxes = [
        # deck + parapet, authored frame: soffit (deck_top − deck_thick) → parapet top
        (bdx + bg["x0"], bdx + bg["x1"], bg["y0"], bg["y1"],
         bg["deck_top"] - bg["deck_thick"], bg["deck_top"] + bg["parapet_h"]),
    ]
    for _px in bg["pier_x"]:                   # piers, authored frame, feet → soffit
        rot_boxes.append((bdx + _px - bg["pier_r"], bdx + _px + bg["pier_r"],
                          b_cy - bg["pier_r"], b_cy + bg["pier_r"],
                          bg["pier_z0"], bg["deck_top"] - bg["deck_thick"]))
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
                         for b in rot_boxes))
        span = pts[-1][0] - pts[0][0]
        pit = math.degrees(math.atan2(tgt[2] - eye[2],
                                      math.hypot(tgt[0] - eye[0],
                                                 tgt[1] - eye[1])))
        diag[name] = dict(pitch=round(pit, 1), y_span=round(span, 1),
                          bow_pct=round(100.0 * dev / TU, 2),
                          occluded=occ, n=len(pts), judge=judge)
        if judge and (span < 40.0 or dev / TU < 0.05
                      or occ > len(pts) * 0.35):
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
                  f"차폐 {d.get('occluded', 0)}/{d.get('n', 0)}")
        print("  판정컷 기준: 종방향 ≥40 m · 휨 ≥5 % · 차폐 ≤35 %")
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
        # N side: y -0.95..-0.75, P side: y 0.75..0.95
        for tag, y0, y1 in (("N", -0.95, st["y0"]), ("P", st["y1"], 0.95)):
            sc.build_slope(stage, f"{ROOT}/Trim_{tag}", st["x0"], tr["z0"],
                           st["tread"] * st["nsteps"], tr["drop"], y0, y1,
                           tr["thick"], M["concrete"], margin=tr["margin"],
                           collider=True)

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
                       M[f"water_{bi}"], max_w=3.5, z_bias=-0.002 * bi,
                       collider=False)
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
        # v4-D1 [top priority]: distant bridge - crosses the river axis (Y) along X. The deck x 12..46
        #   spans beach (−3.2)·water (−3.35)·far bank (−3.2), so 'river' is fixed in a single
        #   cut. The 5 piers run from their own ground up to the deck soffit (−1.0).
        # [v5.1] A bridge must **cross the river perpendicularly** -> the whole thing rotates by the
        #   local tangent angle at the deck centre y (river_prop), then the s->world X transform is applied.
        #   The deck underside stays below -1.0 and the piers reach -3.7, so even when the ground
        #   shifts sideways with the meander, the pier feet stay buried in the terrain.
        bg = PARAMS["bridge"]
        deck_cy = (bg["y0"] + bg["y1"]) / 2.0
        deck_ly = bg["y1"] - bg["y0"]
        bdx = river_dx(deck_cy)
        bgrp = river_prop(f"{ROOT}/Bridge", (bg["x0"] + bg["x1"]) / 2.0,
                          deck_cy)
        sc.add_box(stage, f"{bgrp}/Deck",
                   (bdx + (bg["x0"] + bg["x1"]) / 2.0, deck_cy,
                    bg["deck_top"] - bg["deck_thick"] / 2.0),
                   (bg["x1"] - bg["x0"], deck_ly, bg["deck_thick"]),
                   M["concrete_dark"], collider=True)
        for tag, yc in (("S", bg["y0"] + bg["parapet_w"] / 2.0),
                        ("N", bg["y1"] - bg["parapet_w"] / 2.0)):
            sc.add_box(stage, f"{bgrp}/Parapet_{tag}",
                       (bdx + (bg["x0"] + bg["x1"]) / 2.0, yc,
                        bg["deck_top"] + bg["parapet_h"] / 2.0),
                       (bg["x1"] - bg["x0"], bg["parapet_w"], bg["parapet_h"]),
                       M["concrete_parapet"])   # [v5 ruling applied] 0.22 tone split
        pier_top = bg["deck_top"] - bg["deck_thick"]
        for i, px in enumerate(bg["pier_x"]):
            ph = pier_top - bg["pier_z0"]
            sc.add_cylinder(stage, f"{bgrp}/Pier_{i}",
                            (bdx + px, deck_cy, bg["pier_z0"] + ph / 2.0),
                            bg["pier_r"], ph, M["concrete_dark"], collider=True)
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
                           bz_, M["wood_dark"], yaw=yaw + river_yaw(by))
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
        bz = PARAMS["beach"]["z_top"]
        for i, t in enumerate(PARAMS["trees"]):
            tree_no_stake(M, f"{ROOT}/Tree_{i}", river_dx(t["cy"]) + t["cx"],
                          t["cy"], bz, slot=i)
        for i, t in enumerate(PARAMS["trees_extra"]):
            tree_no_stake(M, f"{ROOT}/TreeX_{i}", river_dx(t["cy"]) + t["cx"],
                          t["cy"], t["gz"], slot=i + 2)
        # v4-D5: reed band (waterline transition) - [v5.1] meander band following the waterline curvature
        rd = PARAMS["reeds"]
        river_band(f"{ROOT}/Reed", rd["x0"], rd["x1"], rd["base_z"] + rd["h"],
                   rd["h"], M["reed"], max_w=1.0, collider=False)
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
    else:
        build_flat_fill(M)          # control: everything flattened to z=0
    build_ground_kit(M)             # [W2-D] both arms — GT-E4 twin parity
    build_river(M)                  # water·far bank are always on (far-view evidence)
    if cfg["cue_scene_dressing"] and cfg["hazard_stairs"]:
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
