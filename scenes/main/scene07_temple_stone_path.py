# -*- coding: utf-8 -*-
"""
scene07_temple_stone_path.py — NegObs synthetic scene 7 (v5 R2): sparse natural stone stair at a mountain temple

Type    : R2 (v5 redesign) — **discrete natural stepping stones** (large slabs set sparsely)
Spec    : Docs/briefs/multi_scene_brief_v5.md §R2 + Docs/archive/legacy/scene_redesign_v5_proposal.md
Shared  : scene_common.py (unmodified) / skeleton convention : scenes/main/scene04_parktrail.py
Inherit : scenes/archive_v3/scene07_wornstone_temple.py (worn_stone·mountain-temple dressing vocabulary)

────────────────────────────────────────────────────────────────────────────
[Hazard]
  The approach path to a Korean mountain temple. Not a standard stair: **large natural stones
  set sparsely** do the job of one. The hazard is not 'exotic terrain' but three layers of
  **reality falling short of code**.

  (1) Broken stepping rhythm — the gaps between stones (0.05~0.30 m) and the rises
     (0.04~0.31 m) are uneven, so the stair prior "the nth nosing = n×riser" does not hold.
     From the robot viewpoint (h0.3) the next tread height cannot be extrapolated.
  (2) A 1.8 m lateral slope drop, **unguarded** — beyond the south shoulder of the corridor
     (y ±1.7) a stone retaining wall falls 1.8 m straight down. There is no railing, kerb or
     tactile paving of any kind (not the practice at mountain temples). Under grazing the leaf
     surface of the lower terrace reads as **one continuous sheet of ground** with the corridor
     face and the border vanishes — the core of this scene's positive GT.
  (3) Partial leaf occlusion — the leaf_ground band bites over the stone edges and erases the
     nosing cut lines (series (2), partial occlusion).

  GT rule: outside the stone path (corridor), the south slope drop = positive. The rises of the
  stones themselves come close to 0.3 m (max 0.31), so the scene doubles as a borderline case of a 'small drop'.

[Walk continuity self-check table]  — entry → descent → exit (coordinates on the y=0 walk line)
  ┌ Section ─────────────┬ Coords (x, z) ───────────┬ Step / basis ───────────┐
  │ Precinct yard (entry)│ x −24..0,  z 0.000       │ flat (granite soil)     │
  │ through the gate     │ x −5.6,    z 0.000       │ posts y ±1.35 (gap 2.7) │
  │ yard edge → stone 1  │ x 0 → 0.24, 0.000→−0.02x │ step = see table [1]    │
  │ descend 24 stones    │ x 0.06..12.05            │ rise min/max = table [2]│
  │ last stone → approach│ x 12.05→12.2, →−4.200    │ step = see table [3]    │
  │ lower approach (exit)│ x 12.2..90, z −4.200     │ flat (leafy dirt path)  │
  └──────────────────────┴──────────────────────────┴─────────────────────────┘
  · Every stone must cover the walk line |y| ≤ 0.22, so the cy jitter is tied to the width
    (|cy| ≤ w/2 − 0.22) → zero "stretches with no stone to step on" (SMOKE checks them all).
  · The actual figures and verdicts are printed by `NEGOBS_SMOKE=1` in tables [1][2][3].

[Geometry core]
  · The stones do not use scene_common.build_worn_stone_stairs (that builder splits each step
    into transverse blocks, a 'continuous stone stair', which cannot give a sparse setting).
    **Individual boxes per stone** are generated scene-locally with a seed-fixed random:
      width w U(0.50,1.10) · depth U(0.28,0.40) · gap U(0.05,0.30) ·
      thickness = proud + U(0.10,0.18) (0.12~0.26) · top-face proud U(0.02,0.08) ·
      yaw rz U(−4,4)° · top-face unevenness rx U(−2.5,2.5)°  → sc._oriented_box
    The ground between the stones is filled by a leaf_ground slope (the corridor slab).
  · Stone top z = P(cx) + proud,  P(x) = −(4.2/12.2)·x  (slope 19.0°)
    → embedded depth = thickness − proud ∈ [0.10, 0.18] m (zero floating, minimum embedment 0.10).
  · Total drop 4.2 m / total run 12.2 m / 24 stones.

[v6 ruling re-fix — judge_v6_rt_new7.md §2 + supervisor decision item 2]
  (1) **Sun re-selection** (supervisor approved). The old `SUN_AZ_OFFSET=0.0` (world az 33.5 = sun
     in the +X·+Y sky) was **fully backlit** on the main camera axis (+X viewing), so the distant
     ridge (−X-facing faces)·south stone wall (−Y-facing faces) had lambert 0 → the upper 40~60 %
     of the frame was pure black.
     → `SUN_AZ_OFFSET=191.5` (world az = 33.5+191.5 = **225**, shadow az 45).
       Per-face direct lambert = dot(N, L) (sun elevation 49.79° → horizontal part 0.6456):
         −X facing (distant ridge·gate front·stone risers) 0.707×0.6456 = **0.456**
         −Y facing (south unguarded stone wall·lower terrace cut face)  = **0.456**
         top face (yard·corridor·stone tops)      sin49.79              = **0.763**
       i.e. the grid (+X)·`side_slope`·`grazing_edge` cuts are all front-lit. Shadows fall to +X·+Y
       (into the frame·north) and do not cover the foreground.
     · (v6 comment error — corrected in v7) "the eave shadow lands at x ≈ 0.69 and only grazes
       1~2 stones" came from projecting **the single eave end line only**. A roof is a surface, so
       the shadow is a **band** over x −3.17…+0.57, and that band covered the near yard.
       → see the [v7] section below. SMOKE now recomputes caster footprints from every AABB corner.
     · Only `gate_frame` (looking back) leaves the gate's +X face on the shaded side — structurally
       unavoidable in the az 180~270 range (clearing the pure-black background outranks it). Instead
       the plinths·2-tier eaves·podium brightness reinforce the silhouette reading.
  (2) **The natural stones rendered as 'brick slabs'** → the cause was twofold.
     (a) the material `stone_worn` = **a masonry joint texture** (regular bricks + mortar joints),
     (b) `make_pbr` uses **world-space projection**, so every stone shared one joint grid
         → joints ran on across the stone borders = a concrete pavement slab.
     → The material was replaced with `rock_face` (jointless natural rock diff/nor) and a
       **per-stone material pool** (8 variants of scale·tint·texture_rotate·texture_translate
       jitter) was built so that the grain·colour·relief of adjacent stones disagree. bump 1.5 strengthens the relief.
     → Silhouette: each stone carried one **canted knob** (a subsidiary lump 1~3 cm lower than the
       main stone with different rz·rx) to break the rectangular outline.
       **[W3 S3-3 · GT-16] the knob is DELETED.** It was a cure for a rectangular *silhouette*
       that the archetype rebuild removes at source: a course of 2~4 slabs with a ragged front
       edge has no rectangle to break. The archetype has no subsidiary lump anywhere in G7.
  (3) **Background horizon closure** — the ridge albedo sat at the sRGB dark floor (0.030), so even
     front-lit it became a black wall. Distant aerial perspective was baked into the albedo, raising
     it to near 0.052 / mid 0.088 / far 0.142 (more blue with distance), the near ridge was split
     into **3 staggered pieces** (y offset·height jitter), and a forest band (build_hedge round
     crowns) was laid on each crest, clearing the straight ridgeline and the black wall at once.
  (4) The leaf band was **an axis-aligned horizontal slab**, so over the 19° corridor its upper end
     was buried and its lower end floated 0.17 m → the identity of the "two black square holes" in
     `gate_frame`. Slope-following (`build_slope`) + 3 rotated overlaps per patch clear the floating
     and the rectangular decal together.

[v7 ruling re-fix — judge_v7_rt_A.md §5 "the shadow moved into the near yard"]
  Diagnosis: v6 chose the bearing looking only at **per-face lambert**. Every face did become
    front-lit, but **the cast shadow** had not vanished; it had simply moved from up there
    (background) to down here (foreground). At az 225 the z=0 projection of the only large caster,
    the Iljumun gate (flying rafter width 5.14 m · eave z 2.81), covers x −3.17…+0.57 · y ≥ −0.89
    → it swallowed the grid's **lower-half ground band** (h0.3_d2 = x −1.44…−0.30, half-width ±0.33)
    whole (lower-half mean 27.5). Rotating the sun cannot shorten the shadow (2.38 m), so three axes are used together.
  (1) **Sun az 225 → 240** (offset 191.5 → 206.5) : the shadow az tips 45 → 60, pushing the shadow
     further toward +Y. A side effect is that **−Y-facing faces (the south unguarded stone wall =
     the grazing judging face) rise in lambert, 0.456 → 0.559**. The cost is −X facing (distant ridge) 0.456 → 0.323.
  (2) **Gate cx −3.0 → −5.6** (stone lanterns·notice board move −2.6 with it) : the shadow's x band
     retreats to −6.26…−2.25, emptying the h0.3_d2 lower-half ground band completely.
  (3) **Gable overhang roof_y 2.35 → 1.90** (flying rafter 2.57 → 2.12) : the shadow's south edge
     moves north from y −0.89 to **−0.06** → the south half of the walk line and the south (right)
     side of the frame are in direct sun. (The flying rafter is wider than the shadow shift, so az alone cannot avoid it entirely.)
  (4) **Distant ridge albedo ×1.42** : offsets the cost of (1) and **preserves render luminance
     (albedo × lambert) at the v7 level** — without this correction the "background pure-black fix"
     reverts. + the mid and far ridges were split into 2 staggered pieces (heights 15.0/18.4 ·
     25.0/29.2), breaking the **horizontal straight crest ("stage backdrop")** of a single box.
  Checks: SMOKE `[v6 sun]` (per-face lambert + albedo×lambert product comparison) ·
        `[v7 shadow]` (z=0 projected footprint per caster) ·
        `[v7 lower-half ground band]` (9 presets × the ground span in the lower half of the frame).
────────────────────────────────────────────────────────────────────────────

Run (GUI look check — default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene07_temple_stone_path.py

Auto capture : NEGOBS_CAPTURE=1 python scene07_temple_stone_path.py
Smoke        : NEGOBS_SMOKE=1 python3 scene07_temple_stone_path.py  (no boot)

Coordinates: Z-up, m, travel axis +X descending (convention). Drop start edge = x=0 (yard shoulder).
        The grid axis (y=0) runs precinct → gate → stone descent → lower approach road.
"""

import os
import sys
import math
import json
import random
import datetime

import scene_common as sc
import ground_kit as gk


# ===========================================================================
# [A] SCENE_CONFIG - standard 7 keys. Only hazard_stairs toggles hazard geometry.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # False -> flatten stepping stones·slope·south drop to z=0
    "cue_railing":        False,   # railings are not the practice on temple stone paths (unguarded) - code path only
    "cue_tactile":        False,   # not the practice (v5 brief §shared) - code path only
    "cue_material_break": True,    # yard decomposed granite vs worn stone contrast
    "cue_sign":           False,   # [GT-84 user: remove the guide sign] the entrance notice board
                                   #   is OUT of the default build. v5.2 precedent: the code path
                                   #   is NOT deleted - PARAMS["sign"], build_sign, the sign_info
                                   #   material/asset role and the `notice_face` PLACEMENT anchor
                                   #   all stay, so the ablation arm still builds with True and
                                   #   only the default flips. The board carried no cue and no
                                   #   hazard-registry entry, so no walked surface or drop moves
    "cue_scene_dressing": True,    # Iljumun gate·stone lanterns·stone wall·pines·Dharma hall silhouette
    "cue_nosing":         False,   # non-slip strips are not the practice on natural-stone nosings - code path only
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
STAIR_RUN = 12.2                   # horizontal length of the stepping-stone run
STAIR_DROP = 4.2                   # total drop over the stepping-stone run (slope 19.0 deg)
SIDE_DROP = 1.8                    # unguarded lateral drop on the south (−Y) side

PARAMS = dict(
    # =======================================================================
    # [W3 S3-4 · GT-14] 자연석 계단 — the course table
    # =======================================================================
    #  What died here: 24 discrete `디딤돌` pavers with U(0.05, 0.30) gaps between them,
    #  i.e. **34.0 % of the run was bare slope**. 조경설계기준 21.5(6)(7) puts a 디딤돌 on
    #  *level* ground, 30 mm proud, long axis across travel — it is the wrong product for a
    #  19.0 deg approach. What replaces it is 자연석 계단석 laid in courses
    #  (조경설계기준 21.8 계단돌 쌓기 · KFS-TRAIL 특별시방서 13-2).
    #
    #  Every row is cited in `Docs/briefs/s3_scene07_10_rebuild_spec_v1.md` §4.1-1 and
    #  `Docs/surveys/s3_research_numbers_v1.md` §B0/§B3/§B4:
    #    n = 28                supervisor ruling §8.R OQ-7 (0.150 / 0.428 confirmed)
    #    flight x 0.00..12.20  the **whole** frozen run. The old flight stopped at 12.05 and
    #                          that 0.15 m shortfall, plus `proud`, IS the +0.201 m orphan
    #                          exit lip: path_z(11.85) + 0.08 = -3.999 against a road at -4.200.
    #    thick 0.250           KFS-TRAIL 13-2 가 자연석 계단석 300x300x250 mm [law]
    #    ov 0.12               back-overlap. The back edge is **not** jittered, so the realised
    #                          interlock is 0.12 + U(-jt/2, +jt/2) = 0.06..0.18 m, i.e. always
    #                          above 표준시방서 0400-3.2 ㄷ's "아랫돌의 뒤뿌리는 윗돌에 50mm
    #                          이상 물리도록" [law], and the open-slope fraction is **0 by
    #                          construction**, not by budget.
    #    jt 0.12               FRONT edge only: U(-0.06, +0.06), so neighbouring slabs in one
    #                          course differ by up to 0.12 m. This is G7's ragged nosing
    #                          (50-120 mm read) and the real negative-obstacle cue.
    #    riser_sigma 0.010     dressed 마름돌 sigma, research §B4, truncated +-2.5 sigma
    #    settle_amp/period     **correlated** long-wave settlement, +-20 mm over 8-12 courses.
    #                          Research §B4: hand-laid stone on an earth core settles in
    #                          patches — "white noise reads as fake". This is the row that
    #                          makes the rise table look built rather than sampled.
    #    rise_band             the declared band the self-check asserts. Realised rises are
    #                          clamped into it and then renormalised so the total is exact.
    #    exit_up 0.030         the last course stands 30 mm above the approach road =
    #                          조경설계기준 21.5(6)'s 디딤돌 proud, and it is an **UP-STEP**
    #                          (GT-14, GT-1 rule (b)) — never a drop.
    #    blocks 2..4 (mode 3)  G7: "each step is a course of 2-4 large irregular slabs".
    #    walk_clear 0.35       no lateral seam inside the walked centre band, so the walk line
    #                          |y| <= foot_half never straddles a joint and the GT top face of
    #                          a course is one slab. Also §4.1-3's zone-0 boundary.
    #    bed_drop / bed_thick  속채움: one core slab per course, top 60 mm under the tread, so
    #                          a lateral joint bottoms out on stone instead of on air
    #                          (표준시방서 0400-3.2 ㄹ "내부는 속채움한다") [law].
    #    corridor_bed 0.33     the `PathCorridor` / `SouthScarp` slope plates drop by this much.
    #                          A course tread is **level** (조경설계기준 21.8(1) "지면과 수평이
    #                          되게"), so its back edge sits up to one rise below the 19.0 deg
    #                          plane; without the drop the frozen plane would pierce every
    #                          tread. `path_z()` itself is untouched — this moves the *plate*,
    #                          not the datum. Declared in GT-14.
    courses=dict(n=28, seed=7075, x0=0.0, x1=STAIR_RUN, y0=-1.70, y1=1.70,
                 exit_up=0.030, rise_band=(0.120, 0.180), riser_sigma=0.010,
                 settle_amp=0.020, settle_period=(8.0, 12.0),
                 ov=0.12, jt=0.12, blocks=(2, 3, 4), blocks_w=(0.18, 0.64, 0.18),
                 seam_jit=0.15, seam_gap=(0.0, 0.030), min_slab_w=0.45,
                 walk_clear=0.35, thick=0.250, jyaw=3.0, jroll=2.5, jz=0.020,
                 bed_drop=0.060, bed_thick=0.40, foot_half=0.22,
                 corridor_bed=0.33,
                 # 고임돌 + 틈메우기돌 (KFS-TRAIL 13-2 나) — shim / gap-filling stones at the
                 # foot of every riser. `sc.VEG_ROCKS` is 0.128-0.314 m wide, i.e. 조약돌
                 # (100-200 mm) to 호박돌 (200-400 mm), which is exactly the two products the
                 # clause names. Without them the joints read open even though they are closed.
                 # `cover` is a target ground-cover FRACTION, not a count, and `scatter_debris`
                 # back-computes n = A*(-ln(1-cover)) / effective-area-per-instance. The joint
                 # band is 0.09 x 3.30 m = 0.30 m2 and `VEG_ROCKS` effective areas run
                 # 0.031-0.128 m2, so the first pilot's 0.16 rounded to **0 instances**. 0.80 is
                 # both the value that yields 4-5 shims and the physically right one: a
                 # 틈메우기돌 band IS ~80 % filled with stone.
                 shim_n=5, shim_band=(0.02, 0.11), shim_cover=0.80,
                 # 돌깔기 aprons, KFS-TRAIL p.72: 하단부 1,000 / 상단부 >=500 mm, 자연석 판석
                 # T100. Laid 6 mm proud (below the 20 mm GT_DELTA) so they are a material
                 # change, not a step: the exit step is measured to the road plate, not to these.
                 apron_lo=1.00, apron_up=0.60, apron_half_y=1.40,
                 apron_t=0.10, apron_proud=0.006, apron_seed=7076),
    # --- [v6] per-stone material pool : breaks the 'continuous joints' of a shared world projection ---
    #     Based on rock_face (jointless natural rock) · scale/tint/rotate/translate jitter.
    #  [W3 S3-3 · LINT-10 adjudication] the key was named `jitter=`, which is the token
    #  `placement_lint` LINT-10 flags with `needs-adjudication`. Adjudicated by the owning WP:
    #  this is a **material tint** spread on 8 pool variants, i.e. neither placement jitter
    #  (abolished by §1.2) nor size jitter (kept by §1.2 X2) — spec §12-15 puts `jit_tint`
    #  explicitly out of scope. Renamed `tint_jit` so the static token stops firing and the
    #  adjudication is recorded in the file rather than in a report nobody re-reads.
    #  [W3 S3-6 · GT-17] `moss_every = 3` — a blind "every third stone is mossy" — is replaced
    #  by the **zone-driven** rule of spec §4.1-3. The pool splits into three tiers and the
    #  selection reads the slab's zone, not its index. `[law]` 조경설계기준 2.6.2(1) makes moss
    #  a *specifiable, preservable* design attribute on 산석 ("이끼 등 착생식물의 보존이 필요한
    #  산석은 설계서에 이를 명시한다"), so this is a specified quantity, not weathering flavour.
    #  Coverage percentages themselves are `[ref]` G7 + `[assumed]` — no Korean document gives a
    #  tread-specific figure (research §B4b), so SMOKE **prints** them and 통람 judges them.
    stone_mtl=dict(n=8, seed=7071, scale=(0.55, 1.35), bump=1.5,
                   # [pilot fix 2] the moss and mid tiers carry 85 % of the riser bodies and
                   #   41 % of the tread caps, and every riser on a +X-descending stair under
                   #   this scene's frozen sun bearing is a shaded face — the two together read
                   #   near-black. Both tiers are lifted; the zone *fractions* are untouched.
                   tint_dry=(0.90, 0.88, 0.84), tint_moss=(0.82, 0.90, 0.78),
                   tint_mid=(0.88, 0.90, 0.84), tint_jit=0.06,
                   n_dry=3, n_mid=3, n_moss=2),
    #  Zone targets, spec §4.1-3. `p_*` are the draw probabilities that realise them; the
    #  achieved fractions are measured from the built table and printed by the self-check.
    moss_zone=dict(seed=7080, cap_t=0.060,
                   walk=(0.00, 0.10), p_walk=0.05,
                   tread_outer=(0.35, 0.55), p_outer=0.66,
                   riser=(0.60, 0.85), p_riser=0.76,
                   joint=1.00, boulder_top=(0.70, 0.90), p_boulder=0.80,
                   margin=0.20),
    # --- [v6] canted knob : breaks the rectangular silhouette (below the main stone top, so GT is unchanged) ---
    #     [W3 S3-3 · GT-16] **DELETED.** 24 prims, yaw 10-20 deg, tilt 3-9 deg, hung 50-80 mm
    #     under the stone top. The v6 knob existed to break a *rectangular* silhouette; the
    #     archetype has no subsidiary lump anywhere (`s3_scene07_10_rebuild_spec_v1.md` §1.B-1
    #     A8, spec §9 P-1 "the knob dies with whichever archetype wins"). The silhouette break
    #     is now the job of the course structure itself (S3-4): 2-4 slabs across a course with
    #     a +-0.06 m ragged front edge. `knob=` is gone from PARAMS, `knob_layout()` and the
    #     `StoneKnob_*` build loop with it.
    # --- corridor (ground between the stones) : leaf_ground slope ---
    corridor=dict(y0=-1.7, y1=1.7, thick=0.60),

    # =======================================================================
    # [W3 S3-5 · GT-15] 야면석 kerb boulders — E7-3 / E7-4, spec §4.1-2
    # =======================================================================
    #  조경설계기준 2.6.2(6) 야면석 = "표면 미가공, 운반 가능한 비교적 큰 석괴" — the product
    #  is named, not invented. Asset route first (spec §1.1 / §3.2): `rock_03_broken`
    #  (1.318 x 1.714 x 0.640 m, 9,832 tri, PASS) is the big one, `rock_02` and `rock_01`
    #  the fillers, all `instanceable=True` so 3 prototypes carry ~26 placements.
    #
    #  **Two deviations from §4.1-2, both forced by this scene's own geometry, both declared:**
    #  1. The spec's fixed line `y = +-1.55` is replaced by "outer edge at `y_edge = +-1.68`",
    #     i.e. `cy = +-(1.68 - across/2)` = +-1.23..+-1.48. Reason: at `y = +-1.55` a 0.6-0.9 m
    #     boulder spans past the corridor edge `+-1.70`. On the SOUTH that overhangs the
    #     unguarded 1.8 m drop, which is the scene's primary positive GT and H8 forbids
    #     softening it; on the NORTH the `NorthWall` slope already occupies `y 1.70..2.15` at
    #     `path_z + 0.75`, so the boulder would be inside a wall. Edge-anchoring keeps every
    #     boulder wholly on the tread and still puts it far outboard of the walk line — the
    #     nearest inner edge is 0.78 m, against the §6.5 floor of `foot_half + 0.10 = 0.32`.
    #  2. §4.1-2's own two rows disagree: "mean 1.6 m centre-to-centre" against "12-16 per
    #     flank over the 12.2 m run" (12.2 / 1.6 = 7.6). The **count** row is the visual one
    #     (it is what G7 shows), so spacing is 0.46 m in the occupied stretches with one >=3.0 m
    #     gap and two ~1.1 m gaps per flank -> 15 per flank, discontinuous.
    #
    #  F2 discipline (`tonglam_v2` §1 row 07 already failed 07 for "boulder-scale D-5 rocks in
    #  dark sink-rings"): `z_mode='base'` and `sink <= 0.05`. A boulder that sits in a hole is
    #  the defect; a boulder that sits ON the tread with a moss collar is the fix.
    #  Native sizes are `[measured - assets/urban_manifest_w3.json]` and repeated here so the
    #  layout stays boot-free; `build_kerb` asserts them against `urban_kit.spec()` at build
    #  time, so a manifest drift is a loud failure and not a silently wrong boulder.
    kerb=dict(seed=7078, y_edge=1.68, x0=0.30, x1=11.95,
              pitch=0.46, pitch_jit=0.12, sink=0.035, tilt=7.0,
              big_gap=3.2, small_gap=1.10, foot_clear=0.10,
              # (asset_id, native sx, sy, sz, scale_lo, scale_hi, weight)
              pool=(("rock_03_broken", 1.3176, 1.7142, 0.6396, 0.36, 0.52, 45),
                    ("rock_02", 0.4035, 0.4629, 0.2851, 0.90, 1.20, 35),
                    ("rock_01", 0.2413, 0.3164, 0.1639, 1.50, 2.10, 20))),

    # --- [W3 S3-5 · GT-15] fern margins (E7-5 / E7-6) and the two framing trunks (B3) ---
    #   Fern is gap **G2**: 0 hits across all 291 manifest rows and all 44 vegetation USDs.
    #   `Shrub/Switchgrass.usd` (2.01 x 2.03 x 1.37, 8,934 tri, green 100 %) is the spec's
    #   named stand-in — the arching-blade silhouette is the closest available read. Recorded
    #   as a stand-in, not as a fern: the real fix is a CC0 fern atlas on crossed quads (R7-3).
    ferns=dict(seed=7079, target_h=(0.62, 1.05),
               north=dict(x=(0.4, 11.6), y=(2.32, 3.85), n=15),
               south=dict(x=(0.4, 11.6), y=(-3.70, -2.15), n=11)),
    #   G7's framing trunks are 0.6-1.2 m diameter old growth standing right at the margin,
    #   not the 0.22 m courtyard pines 4-6 m off axis. Two are added at the corridor margins.
    #   On the asset path `build_tree` scales the tree by `trunk_h * 1.60`, so `trunk_h` is
    #   what makes a big trunk; `trunk_r` is carried for the procedural fallback arm.
    #   [pilot fix] The first pilot put these at |cy| 2.55-2.62 with `trunk_h` 6.4/6.8.
    #   `Shumard_Oak` is 10.4 x 10.3 m **wide** at its 10.9 m native height, so at that
    #   offset the south tree's crown swallowed the corridor and `stone_rhythm` came back as
    #   a wall of leaves with no stair in it at all. The south margin is also 1.8 m BELOW the
    #   corridor, which puts that crown at exactly walk height. They move out to |cy| 5.6 /
    #   7.5 and grow: at `trunk_h` 9.0-9.4 the asset stands 14.4-15.0 m with its crown base
    #   ~4 m up, so what reaches over the corridor is canopy at the top of the frame — E7-8's
    #   tunnel — instead of foliage across the walk line.
    #   **SHIPPED EMPTY, and this is a measured result, not an omission.**
    #   Three placements were rendered: |cy| 2.6 (first pilot), |cy| 5.6 / 7.5, and
    #   |cy| 3.6 / −4.8 at `trunk_h` 9.0-9.4 (= 14.4-15.0 m of `Shumard_Oak`, whose crown is
    #   10.4 x 10.3 m at its 10.9 m native height). An A/B with `frame_trees` forced empty
    #   isolates them as **the entire DARK / OCCL delta of this rebuild** `[measured, PT_FAST,
    #   same round, same commit]`:
    #       cut              with trees        without      CB-2 baseline
    #       h0.3_d2          94.0 / 34.8 %   114.5 / 13.8 %   115.9 / 13.9 %
    #       h0.9_d2          48.0 / 64.4 %    98.1 / 19.5 %    86.8 / 19.5 %
    #       side_slope       10.1 / 93.9 %    87.9 / 24.4 %    82.5 / 26.4 % (w2d_fix)
    #       stone_rhythm     73.3 / 48.5 %   127.9 /  7.3 %    97.8 /  6.2 % (w2d_fix)
    #   Without them every DARK / OCCL gate lands **at or better than baseline** and the only
    #   thing left moving is FRAME, which §6.4 declares in advance. With them `side_slope`
    #   loses 78 luminance points and reads 94 % dark — that is not a look, it is a blackout.
    #   The cause is structural, not a placement mistake: this asset's crown radius is ~0.48x
    #   its height, the corridor is 3.4 m wide, and the south margin is 1.8 m BELOW the walk,
    #   so any tree big enough to read as G7's old growth also roofs the walk line from
    #   30-40 % of its own height. **E7-8's canopy tunnel therefore needs a distant belt or a
    #   high-crown species, not two near-field trunks** — recorded as a follow-up, because
    #   trading a live gate for a dressing item is exactly what H16 forbids. The builder path
    #   below is left intact and driven by this list, so re-enabling is a one-line change.
    frame_trees=[],
    #   Species is **pinned**, not hashed — see `build_ferns`. `native_h` is zmax
    #   [measured — scene_common.VEG_TREES / veg_manifest_w2.json].
    frame_tree_veg=dict(rel="Trees/Shumard_Oak.usd", native_h=10.8989),

    # === [W2-D ground_kit] P12 `courtyard_dg` - spec Sec.5.7 row 07 =========
    #  Natural scene: `natural=True` makes plan_ground raise on any urban infra
    #  (manhole / gully / gutter / marking), so the whole prescription is
    #  tone + scatter. Three bands, exactly as Sec.5.7 asks for:
    #    07-1  3.0 m decomposed-granite walking band  = region y +-1.50, and
    #          `edge_break` on both band lines (the "3-band split" of the
    #          24 x 45.7 m single plate).
    #    07-2  trodden wear axis, width 1.20, albedo x0.85  -> `wear_lane`
    #    07-3  exposed gravel 8/m^2  -> scatter 270 over 33.6 m^2 = 8.04/m^2
    #    07-4  plinth moss band + soil staining -> stain(dirt, water)
    #  region x1 = -0.80 (= EDGE_STANDOFF), NOT the plate edge x=0. Reason:
    #  `apply_ground` runs the profile scatter over the **untrimmed** region,
    #  so only the region itself can keep 6 cm gravel off the shoulder edge.
    #  Surface elements are trimmed to the same -0.80 by `_trim_region`.
    #  Dropped from the profile: `edge_litter`. `_compose_ops` forces its
    #  width to the region span (3.0 m here, 12x the 0.25 m the ledger gives
    #  it) and the two bands then cover y -3.0..3.0, which overlaps the wear
    #  lane at an identical top z -> coplanar decals. Carried as a kit defect.
    gkit=dict(
        region=(-12.0, -1.50, -0.80, 1.50),
        wear_w=1.20,                       # Sec.5.7 "trodden wear axis 1.2"
        band_lines=(-1.50, 1.50),          # the 3.0 m granite-sand band edges
        gravel_n=180,                      # [W2 F2] 270 -> 180; the walked forecourt is
                                           #   gravel, not a rubble yard (8/m^2 was the
                                           #   boulder-era figure)
        seed=7,
    ),
    # --- axis-aligned ground plate table (name, x0, x1, y0, y1, z_top, thick, mtl) ---
    #     v5 regression checklist (3) : no plane covers a cavity - at the south drop y=−1.7
    #     the plates are **split** at that border (no continuous slab bridges it).
    #  [W3 S3-6 · GT-17] **Season re-bind, summer pin** `[ruled 07-31]` §8.R OQ-1.
    #    `leaf` = `TEX["leaf_ground"]`, whose own role comment is "Fallen-leaf ground (C2)" —
    #    an **autumn** texture. It was bound to the corridor, all three south terraces and the
    #    approach, i.e. scene07 was a summer canopy over an autumn floor. The cherry-blossom
    #    precedent applies in reverse (`scene_common.py:2098-2101` deleted `Japanese_Cherry`
    #    for being 0.0 % green): **judge by pixels, not by the role's name**. These five
    #    surfaces move to `forest` = `dirt_park` darkened and damped; `leaf_ground` survives
    #    on the margin lobes only, which is where G7 actually shows brown litter.
    plates=[
        ("Courtyard",     -24.0,   0.0,  -1.7,  44.0,   0.0, 0.50, "gravel"),
        ("CourtyardBody", -24.0,   0.0,  -1.7,  44.0,  -0.5, 2.20, "rock"),
        ("BackField",     -46.0, -24.0,  -1.7,  44.0,   0.0, 2.40, "grass"),
        ("SouthTerraceA", -46.0,   0.0, -34.0,  -1.7,  -1.8, 1.20, "forest"),
        ("SouthTerraceC",  12.2,  90.0, -34.0,  -1.7,  -6.0, 1.20, "forest"),
        ("Approach",       12.2,  90.0,  -1.7,   2.15, -4.2, 1.00, "forest"),
        ("NorthWallFlat",  12.2,  90.0,   2.15,  2.6,  -1.25, 3.20, "rock"),
        ("NorthBankFlat",  12.2,  90.0,   2.6,  44.0,  -2.0, 1.20, "grass"),
        ("ScarpFlatBot",   12.2,  90.0,  -1.80, -1.66, -4.2, 2.00, "rock"),
    ],
    # --- slope plates (build_slope) : (name, z0, drop, y0, y1, thick, mtl) ---
    #     All x0=0, run=STAIR_RUN. margin=0.0 (plate borders match exactly).
    slopes=[
        ("PathCorridor",  0.00, STAIR_DROP, -1.70,  1.70, 0.60, "forest"),
        ("SouthTerraceB", -1.80, STAIR_DROP, -34.0, -1.70, 1.20, "forest"),
        ("SouthScarp",    0.00, STAIR_DROP, -1.80, -1.66, 2.00, "rock"),
        ("NorthWall",     0.75, 2.00,        1.70,  2.15, 3.20, "rock"),
        # [GT-126] StairCheekN — 북측 계단 뺨돌(측벽). `side_slope` showed the tread
        #   ends and the NorthWall face **co-planar at y=1.70**: yaw-jittered slab
        #   corners cross to y 1.7154 [measured, course table], so the wall face was
        #   z-fighting the tread end faces (stair-shaped notches punched into the
        #   masonry) and the across-course seam slots exposed wall texture floating
        #   between slabs. The cheek encloses that joint instead of moving anything:
        #   face at y=1.62 (0.08 m proud of the wall, so the treads visibly DIE INTO
        #   a raking flank wall — 계단 옆막이, standard practice), north edge y=1.78
        #   tucked into the wall body, top = chord + 0.22 (flank slab corner max is
        #   chord + 0.058 [measured] → 0.16 m clearance; NorthWall crest is chord
        #   + 0.75..+2.95, always above). No tread/bed/drop prim is touched — the
        #   south drop edge, walk-line z and both wall *outer* faces are unchanged.
        ("StairCheekN",   0.22, STAIR_DROP,  1.62,  1.78, 0.90, "rock"),
        ("NorthBank",     0.00, 2.00,        2.15, 44.00, 1.20, "grass"),
    ],
    # --- leaf-litter band (partial occlusion of stone edges) : thin slabs over the corridor (cx, cy, sx, sy) ---
    #     [v6] axis-aligned horizontal slabs -> **slope-following slabs** (19 deg) + 3 rotated overlaps per patch.
    #     The old way buried the upper end and floated the lower one by 0.17 m (= gate_frame's black square holes).
    #  [W3 S3-6 · GT-17] **Re-sited to the margins.** These six were carpets laid ACROSS the
    #    walked surface at |cy| 0.35-0.75; G7 puts brown litter only at the flight margins and
    #    in the joints, never on the walk. Each is now a small lobe on the shoulder at
    #    |cy| >= 1.15 (§4.1-5's floor is 1.0), sized `sx` 0.38 so it lands **inside one tread**
    #    — with `z_fn = course_top` a wider lobe would drape over a riser and read as a torn
    #    sheet. The mechanism (`build_carpet_mask` + feather ring) is unchanged: H4 forbids
    #    turning a CB-2 lobe back into a rectangle, and none of these does.
    #    `cx` values are **tread centres** `0.43571 * (k + 0.5)` for k = 3, 7, 12, 16, 21, 25.
    leaf_drifts=[(1.525, 1.28, 0.38, 0.80), (3.267, -1.34, 0.38, 0.92),
                 (5.446, 1.42, 0.38, 0.74), (7.188, -1.22, 0.38, 0.86),
                 (9.366, 1.20, 0.38, 0.78), (11.107, -1.40, 0.38, 0.70)],
    # [W2 F3] proud 0.012 -> 0.004. A 12 mm rim all the way round each drift is
    #   the "edge shadow" that made the leaf drifts read as carpets laid on the DG.
    # [W3 F3 / DEC-2] `thick` and the three `sub_*` rectangle-stacking knobs are retired:
    #   the mask is a single zero-thickness N-gon, so there is no rim left to shade and no
    #   stack of rectangles to hide behind. `subs` stays at 1 for the self-check line.
    #   `feather` = the leaf-card band straddling the boundary (inner 0.30 / outer 0.50 m,
    #   spec §10.5 DEC-2); `feather_cap` bounds the instance cost per mask.
    # [W3 S3-2] Near-field chord polish (redteam_w3_window1.md §3.1). On scene07's
    #   `h0.3_d2` the 24-gon chord facets of the nearest masks are faintly readable at
    #   ~1 m. The sanctioned cure is "raise `n` ... for near-field masks (cosmetic knob)".
    #   Only the masks that stand inside `chord_near_x` are raised, so the fix stays a
    #   near-field fix and the far masks keep their measured 24-gon budget.
    #   [measured] polygonisation sagitta = r*(1-cos(pi/n)) at the largest near mask
    #   (YardLeaf_0, rx 1.20): n 24 -> 10.3 mm, n 48 -> 2.6 mm. Capture is 1920x1080 at a
    #   36 deg vertical FOV = 0.582 mrad/px, so at the 1 m standoff that is 17.7 px -> 4.4 px.
    #   Cost on the mask itself is zero prims: a `build_blot` N-gon is ONE Mesh whatever `n`
    #   is (spec §10.5 DEC-1), so this adds points, not prims (3 masks x 24 extra vertices
    #   = +72 points). [measured] the scene total moves 1088 -> 1090 all the same, because
    #   `build_carpet_mask` derives the feather-ring *region* from the mask AABB and a
    #   48-gon inscribes the (rx, ry) box more tightly than a 24-gon: the ring region moves
    #   by a few mm and `scatter_debris` lands 2 more leaf cards. Second-order, declared.
    #   Side effect, declared: the radius ring is drawn per vertex, so a 48-gon edge carries
    #   finer boundary detail than a 24-gon one. `_blot_ring`'s smoothing pass has a zero at
    #   Nyquist ((1+cos w)/2), so no vertex spikes appear - the edge gets crinklier, not spiky,
    #   which is what a real leaf-carpet boundary does at that scale.
    #   Near-field set = the 3 masks the redteam names: yard drifts at cx -2.6 / -7.6 and
    #   corridor drift 0 at cx ~ 1.30. The yard drift at -13.2 and corridor drifts from
    #   cx 3.05 down are far-field and stay at 24.
    leaf_band=dict(proud=0.004, seed=7073, subs=1,
                   feather=(0.30, 0.50), feather_cap=22,
                   cover_corridor=0.035, cover_yard=0.06,
                   n_far=24, n_near=48, chord_near_x=(-8.6, 2.2)),
    # [v6] 3 leaf drifts on the yard (decomposed granite) - eases the 'large high-reflectance beige plane' (ruling (5)).
    #      A yard is flat by practice, so material variation, not curvature, breaks the monotony.
    #      All at y >= −1.55 (never past the south border −1.7 = zero floating).
    yard_drifts=[(-2.6, 2.2, 2.4, 1.8), (-7.6, -0.72, 2.1, 1.6),
                 (-13.2, 1.7, 2.6, 2.0)],
    yard_leaf=dict(seed=7074, subs=2, scale=(0.6, 0.9), off=0.38, rz=30.0),

    # --- Iljumun gate (2 pillars + gable roof) : behind the yard shoulder, 2.7 m opening on the grid axis ---
    #   [v7 ruling §5 (2)] This gate is the **only large caster** of the near-view yard shadow.
    #     Old cx −3.0 · roof_y 2.35 (flying rafter 2.57) · az 225 -> shadow x −3.17…+0.57 ·
    #     y >= −0.89, covering the whole lower-half ground band of h0.3_d2 (x −1.44…−0.30, y +-0.98)
    #     (measured lower-half mean 27.5). Rotating the sun alone cannot shorten the x-direction
    #     shadow length (flying rafter 2.81 m x cot49.79 = 2.38 m), so **the gate retreats 2.6 m
    #     west** and the gable overhang shrinks 1.00 -> 0.55 m, moving the shadow's south edge north to y~0
    #     (the SMOKE [v7 shadow] table compares it against each preset's lower-half ground band).
    gate=dict(cx=-5.6, half_y=1.35, post_r=0.24, post_h=3.05,
              beam_t=0.30, beam_over=0.45,
              roof_half_run=1.55, roof_drop=0.62, roof_t=0.22,
              roof_y=1.90, ridge_z=4.00),
    # --- 2 stone lanterns (in front of the gate) ---
    #   [v6] The old shape (prism + square cap + cylinder) read as a **brick chimney**.
    #   Causes: (1) a masonry texture (stone_worn), (2) no standard granite-lantern members.
    #   -> base stone·lower pedestal·round shaft·upper pedestal·light chamber (4 posts + dark
    #      light windows)·2-tier roof stone·jewel finial instead, in a jointless granite tone.
    #   [v7] Moved −2.6 m with the gate (keeps its 1.3 m relative position in front of it).
    lanterns=[dict(cx=-6.9, cy=2.45), dict(cx=-6.9, cy=-1.15)],
    lantern=dict(plinth_w=0.86, plinth_h=0.14, lower_r=0.30, lower_h=0.20,
                 shaft_r=0.13, shaft_h=0.62, upper_r=0.26, upper_h=0.16,
                 fire_w=0.46, fire_h=0.42, pillar=0.075,
                 cap_w=0.94, cap_h=0.11, cap2_w=0.66, cap2_h=0.09,
                 jewel_r=0.085),
    # --- Dharma hall silhouette (upper) : podium + pillar row + gable roof ---
    #   pillar top (0.9+2.4=3.30) < roof soffit (3.72) over the outermost pillar (+-4.1) - zero interpenetration
    hall=dict(cx=-18.0, cy=3.5, sx=9.0, sy=5.6, base_h=0.9,
              post_r=0.20, post_h=2.4, n_posts=5,
              roof_half_run=5.6, roof_drop=1.6, roof_t=0.30, roof_y=4.2,
              ridge_z=5.20),
    # =======================================================================
    # [W3 S3-7] Crest roof cluster — PROCEDURAL, `gate_frame`-tier only
    # =======================================================================
    #  Gap **G1** `[ruled 07-31]` §8.R OQ-8: the catalogue has **zero** Korean tile-roofed
    #  geometry. A keyword sweep returns 172 hits but 162 are `signs_kr` rows matching "korea"
    #  in `root_key`; the only tile-roofed asset in 291 + 33 rows is `typical_building_18`, a
    #  generic Western low-rise with no 처마 curve, no 팔작 hip-gable and no rafter row. So the
    #  cluster stays procedural and the row stays open in the procurement queue.
    #  **H16 governs the budget**: `gate_frame` is 1 of 14 cuts and is NOT one of the 5 preset
    #  cuts the baseline round judges, so this is the lowest-value item in the whole rebuild.
    #  It gets two clone masses, an upturned eave, one dentil row and one red wall fragment —
    #  and not one minute more. `hall` itself does not move: it is a caster in the v7 shadow
    #  table and H12 forbids disturbing a working v6/v7 fix for a backdrop.
    #  `z0` is a **stepped terrace**, not decoration: from `gate_frame`'s eye at
    #  (7.00, −0.91) the crest sightline over the yard shoulder (x 0, z 0) rises 0.13 m per
    #  metre going −X, so it stands at z 3.31 at cx −25.5 and z 4.42 at cx −34. A flat-ground
    #  0.85x / 0.70x clone (ridge 4.42 / 3.64) would be **behind the crest and invisible**.
    #  A Korean 산사 does exactly this — the upper courts step up the hillside on 축대 — so
    #  each clone gets a terrace and the clearance is asserted in SMOKE, not assumed.
    roof_cluster=[dict(name="Mid", cx=-25.5, cy=11.5, s=0.85, z0=1.20),
                  dict(name="Far", cx=-34.0, cy=-2.5, s=0.70, z0=2.70)],
    #  처마 곡선 is a curve; a two-segment approximation is the cheapest read that is not a
    #  flat plane. `[assumed]` — spec §4.1-4.
    eave=dict(run=0.80, lift=0.35, dentil_n=22, dentil=(0.10, 0.16, 0.22),
              red=(0.55, 0.14, 0.11)),
    #  E7-10: one slender dark timber pole, ~0.15 m diameter, left of the stair, no crossarm.
    #  One prim; no asset can beat that on cost (spec §3.2). CC0 pier-pole maps.
    pole=dict(cx=-2.0, cy=2.60, r=0.055, h=4.5),
    # --- pines (build_tree) : slope·yard·terrace (name, cx, cy, zone, trunk_h) ---
    pines=[("N0", 2.5, 4.6, "north", 3.0), ("N1", 7.4, 6.2, "north", 3.4),
           ("N2", 11.6, 4.2, "north", 2.8), ("N3", -6.0, 6.5, "flat", 3.2),
           ("S0", 4.2, -4.4, "south", 2.6), ("S1", 9.0, -6.0, "south", 3.0),
           ("S2", -8.0, -5.2, "south", 2.8), ("S3", 15.0, -4.0, "south", 3.1)],
    tree=dict(trunk_r=0.11),
    # --- shrub clumps (overlapping flattened ellipsoids - scene04 v5 convention) ---
    # [v6] North shrubs y 3.0~3.6 -> 4.4~5.0 : right behind the stone wall (y 1.70~2.15, 0.75 m
    #      lower at the back), they read from the corridor as 'floating on top of the wall'.
    shrubs=[(1.8, 4.5, "north"), (6.0, 4.9, "north"), (10.4, 4.6, "north"),
            (2.0, -2.9, "south"), (7.6, -3.4, "south"), (12.0, -3.0, "south"),
            (-9.0, 3.0, "flat"), (-14.0, -3.4, "south")],
    shrub=dict(embed=0.25,
               blobs=((0.00, 0.00, 0.78, 0.62, 0.36),
                      (0.55, 0.42, 0.52, 0.44, 0.26),
                      (-0.46, -0.38, 0.58, 0.40, 0.30))),
    # --- temple notice board (sign_info) : at the entrance (before the gate), facing the approach (yaw 180) ---
    #   [v7] Moved −2.6 m with the gate (keeps its 0.65 m relative position behind it).
    #   [GT-84] `cue_sign` defaults to False, so this block builds only on the ablation arm.
    #   Kept verbatim — the geometry is still the one the arm must reproduce.
    sign=dict(cx=-4.95, cy=-1.15, yaw=180.0, w=0.78, h=0.62, pole_h=1.95),

    # --- distant ridgelines (horizon closure, straight ahead on the main camera axis +X) ---
    #   [v6] The old near ridge was a single sy 130 box -> **a straight ridgeline + a black wall**.
    #   The near ridge is split into 3 staggered pieces (x 41.0~46.5 · heights 7.6/10.4/8.6) and each crest
    #   carries a forest band (ridge_crest) to roughen the ridgeline. The y union −74..+79 covers
    #   the grid FOV (+-30 m @ 50 m) with room to spare.
    ridge=[dict(cx=42.5, cy=-46.0, sx=7.0, sy=56.0, h=7.6, z0=-6.0,
                tone="near"),
           dict(cx=46.5, cy=6.0, sx=8.0, sy=52.0, h=10.4, z0=-6.0,
                tone="near"),
           dict(cx=41.0, cy=52.0, sx=6.5, sy=54.0, h=8.6, z0=-6.0,
                tone="near"),
           # [v7 ruling §5 (2)] The mid and far ridges were **single boxes** of sy 170/210, so their crests
           #   were perfectly horizontal = "a stage backdrop with a horizontal seam". Treated the same
           #   way as the near ridge: split into 2 staggered pieces (3~4 m height difference) to break the skyline.
           #   The y union still covers the grid FOV (+-48 m @ 84 m).
           dict(cx=62.0, cy=-52.0, sx=11.0, sy=104.0, h=15.0, z0=-6.0,
                tone="mid"),
           dict(cx=66.0, cy=48.0, sx=10.0, sy=112.0, h=18.4, z0=-6.0,
                tone="mid"),
           dict(cx=84.0, cy=-58.0, sx=14.0, sy=132.0, h=25.0, z0=-6.0,
                tone="far"),
           dict(cx=88.0, cy=56.0, sx=13.0, sy=140.0, h=29.2, z0=-6.0,
                tone="far")],
    # ridge-crest forest bands : (ridge index, height, tone, f0, f1) - build_hedge round
    # crowns treat distant trees as a **silhouette band** rather than individuals (avoids
    # the C-4 lollipop). GT-63 keeps this cheap idiom for the RidgeCrest family.
    # [GT-126] f0/f1 = fractional span of the ridge's y extent. The near bands are split
    #   into two segments of different height (Δh 0.5~0.7): one full-length band seeded
    #   from a single centre gave crowns of one pitch and one apex line — the audited
    #   "identical green domes in a row". Two segments re-seed the crown hash and stagger
    #   the apex line; total band length is unchanged. [measured] crest prims 196 → 224
    #   (+28: the lower-height segment draws a tighter crown pitch, h*1.2*0.9) — all
    #   distant-mass spheres, declared backdrop cost.
    ridge_crest=[(0, 3.4, "near", 0.00, 0.56), (0, 2.8, "near", 0.56, 1.00),
                 (1, 4.2, "near", 0.00, 0.47), (1, 3.5, "near", 0.47, 1.00),
                 (2, 3.8, "near", 0.00, 0.52), (2, 3.1, "near", 0.52, 1.00),
                 (3, 5.0, "far", 0.00, 1.00), (4, 4.2, "far", 0.00, 1.00)],
    # individual trees only on the near ridge crest, a few (for edge silhouette variation)
    ridge_trees=[dict(ri=0, cy=-30.0), dict(ri=1, cy=-6.0),
                 dict(ri=1, cy=14.0), dict(ri=2, cy=38.0)],
    # rear (−X) forest line : 3 background hedges + 3 trees. base is the ground in that y band.
    back_hedge=dict(cx=-34.0, sx=1.4, length=20.0, h=2.0),
    back_hedges=[dict(cy=8.5, base=0.0), dict(cy=29.0, base=0.0),
                 dict(cy=-16.0, base=-1.8)],
    back_trees=[dict(cx=-38.0, cy=-12.0, gz=-1.8, trunk_h=3.4),
                dict(cx=-38.0, cy=6.0, gz=0.0, trunk_h=3.8),
                dict(cx=-38.0, cy=24.0, gz=0.0, trunk_h=3.2)],
    # distant forest bands (name, x0, x1, y0, y1, h, base_z) - south terrace / north slope
    far_hedges=[("S0", -40.0, 0.0, -30.0, -27.0, 2.4, -1.80),
                ("S1", 12.2, 80.0, -30.0, -27.0, 2.4, -6.00),
                ("N0", -40.0, 0.0, 40.0, 43.0, 2.6, 0.00),
                ("N1", 12.2, 80.0, 40.0, 43.0, 2.6, -2.00)],

    # --- materials ---
    material=dict(
        # [v6] rock_face = jointless natural rock for the stones / granite = lanterns·plinths
        # [GT-126] rock_wall 3.5 → 4.6: at 3.5 the ~0.40 m block module repeated 3.5
        #   times across the 12.2 m wall run and the same 7~8-block motif recurred in
        #   frame (audit: "석축 텍스처가 명확한 타일 반복"). 4.6 puts blocks at ~0.53 m
        #   (호박돌급 — the larger product is the correct one for a 1.8~3 m revetment)
        #   and cuts the visible period count to 2.65. The residual periodicity is
        #   killed by the per-period unit-cell albedo jitter wired in setup_materials.
        scale=dict(rock_wall=4.6, rock_face=0.95,
                   granite=3.2, leaf_ground=2.0, gravel=0.35, grass=1.4,
                   dirt_park=1.10, moss=2.40),
        # [W3 S3-6 · GT-17] summer forest floor + the first moss tint in this scene.
        # [pilot fix 2] 0.70/0.71/0.62 was measured 40 luminance points darker than the
        #   `leaf_ground` x leaf_tint it replaced and drove the DARK gate on 5 cuts;
        #   `dirt_park` is already a dark damp-soil scan, so the tint is now near-neutral and
        #   the damp read comes from the map, not from a multiplier.
        forest_tint=(1.00, 0.98, 0.90),
        moss_tint=(0.95, 1.00, 0.92),
        # [W3 S3-7] 기와 tone. Dark grey-blue, kept under the sRGB dark-colour floor the
        #   v6 ruling set for roofs (the old flat constant was 0.045/0.030/0.018).
        tile_tint=(0.62, 0.64, 0.68),
        stone_moss_tint=(0.86, 0.95, 0.82),   # (old stepping-stone moss tone - unused in v6)
        leaf_tint=(0.95, 0.90, 0.82),
        gravel_tint=(0.84, 0.81, 0.76),       # [v6] eases the yard's high-reflectance beige
        granite_tint=(1.0, 1.0, 1.0),
        grass_tint=(0.55, 0.68, 0.42),
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        roof_color=(0.045, 0.030, 0.018),     # dark timber and roof tile (sRGB dark-colour rule)
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        shrub=(0.030, 0.047, 0.021), shrub_rough=1.0,
        # [v6] Aerial perspective baked into the distant albedos (old 0.030~0.052 = a black wall even lit).
        #   Brightness and blue rise with distance - the 3 ridge tiers read as separate layers.
        # [v7] With the sun az 225 -> 240, the −X-facing lambert drops 0.456 -> 0.323 (x0.708).
        #   To **preserve render luminance (= albedo x lambert) at the v7 level**, the ridge and
        #   crest albedos are all scaled x1.42 (=0.456/0.323), staying under the pure-white
        #   ceiling of 0.72. Without this correction the "background pure-black fix" reverts
        #   - the SMOKE [v6 sun] block compares the albedo x lambert product against the v6 values.
        # [GT-126] These five are now **effective-albedo targets**, not raw constants:
        #   setup_materials realises each one as `rock_face` × (target / texture linear
        #   mean), so tint×mean lands exactly on the value stated here and the SMOKE
        #   [v6 태양] 휘도곱 preservation table keeps reading the true number. The
        #   constant-colour ridge walls were the audited "세로 줄무늬 상수색 녹색 벽";
        #   the texture is world-projected at ridge_tex_scale so the mottle reads as
        #   soil/rock tonal bands on a far hillside, and the aerial-perspective tiering
        #   (bluer + brighter with distance, v6/v7) is preserved bit-for-bit at the mean.
        ridge_near=(0.074, 0.088, 0.064),
        ridge_mid=(0.125, 0.139, 0.131),
        ridge_far=(0.202, 0.222, 0.250),
        crest_near=(0.060, 0.078, 0.051),     # ridge-crest forest band (near)
        crest_far=(0.102, 0.122, 0.111),
        ridge_tex_scale=(22.0, 30.0, 40.0),   # near/mid/far projection [m per tile]
        crest_tex_scale=6.0,                  # crown blobs — canopy-clump wavelength
        sign_back=(0.055, 0.050, 0.045),
        rail_color=(0.20, 0.18, 0.16), rail_metallic=0.25, rail_rough=0.75,
    ),

    # --- lighting: scene01's verified noon constants ---
    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        noon_sun_enable=True, noon_sun_elev=49.79,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    # Per-scene sun. World sun az ~ 33.5+offset (the bearing the sun is at); shadows fall at az−180.
    # [v6 ruling §2 (6) + supervisor decision item 2 - re-selection approved]
    #   Old 0.0 (az 33.5) = sun in the +X·+Y sky -> fully backlit on the +X viewing axis.
    #     Distant ridge (−X facing) lambert −0.538 -> 0, south stone wall (−Y facing) −0.553 -> 0 = pure black.
    #   Old 191.5 (az 225) = sun in the −X·−Y sky. Face lambert was saved, but **the gate's
    #     shadow fell straight onto the near yard (the grid's lower-half ground band)** (v7 §5 (2)).
    #   New 206.5 (az 240, shadow az 60) = lays the shadow further toward +Y, clearing the south
    #     half of the walk line. −X facing 0.323 / −Y facing 0.559 / top face 0.763.
    #     · −Y facing (south unguarded stone wall = the grazing judging face) **rises** 0.456 -> 0.559.
    #     · −X facing (distant ridge) falls 0.456 -> 0.323 -> ridge albedo corrected x1.35.
    #     Detailed checks in the SMOKE [v7 shadow]·[v7 sun] tables.
    SUN_AZ_OFFSET=206.5,

    render=dict(pt_total_spp=512, pt_max_bounces=8),
)


def _deep_update(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_update(dst[k], v)
        else:
            dst[k] = v


_ov = os.environ.get("NEGOBS_PARAMS_OVERRIDE", "")
if _ov:
    _deep_update(PARAMS, json.loads(_ov))
    print(f"[PARAMS] override 적용: {_ov}")

_sc_ov = os.environ.get("NEGOBS_SCENE_CONFIG", "")
if _sc_ov:
    _deep_update(SCENE_CONFIG, json.loads(_sc_ov))
    print(f"[SCENE_CONFIG] override 적용: {_sc_ov}")


# ===========================================================================
# [B-2] PLACEMENT — the geometry-free declaration `scripts/placement_lint.py` reads
#       (spec §10.4, expectations in `s3_scene07_10_rebuild_spec_v1.md` §6.6).
#       Additive and static: it authors no prim and changes no coordinate. It is read as a
#       module-level literal, so every value here must stay a literal.
# ===========================================================================
PLACEMENT = dict(
    # **Deliberately empty, and this is a finding, not an omission.** `walk_edges` is read by
    # LINT-5 as a *보도 footway boundary* and it applies PE-8 = 「도로의 구조·시설 기준에 관한
    # 규칙」 제16조's 1.5 m effective-width floor to anything standing near it. Declaring the
    # corridor shoulders `y = ∓1.70` as walk edges was tried and measured: it raises LINT-5 to
    # **2 ERROR** against the two framing trunks, which stand 0.85 / 0.92 m outside the
    # corridor — on the north bank and on the south terrace 1.8 m below, i.e. not in anybody's
    # footway. 제16조 governs a 도로 보도; this is a mountain-temple 자연석 계단 whose south
    # shoulder is a cliff edge (the scene's primary positive GT) and whose north shoulder is
    # the foot of a retaining wall. Neither is a footway boundary, so the datum is declared
    # absent rather than mis-declared — the same reasoning §4.0 F-1/F-3 used to refuse
    # PIRAN-15 and HOUSE-18 on a trail deck.
    walk_edges=[],
    # §6.6: **there is no kerb line in a temple approach.** Declared empty on purpose — the
    # 야면석 boulders are a discontinuous retaining/edging device on the shoulder, not a 연석,
    # and LINT-1's tree-to-kerb rule is vacuous here rather than unmeasured.
    kerb_lines=[],
    # §6.6: the boulders are NOT furniture — a boulder has no build axis, the same reason
    # §12-15 exempts `build_tree`'s yaw. They carry a full U(0, 360) yaw by design and are
    # named `Kerb_*`, which matches no prop class in the linter's taxonomy, so no exemption
    # entry is needed in T1's rules file (which S3 may not edit in any case).
    anchors={
        "gate_axis": dict(face_bearing_deg=0.0,
                          props=["Lantern_.*"]),
        "notice_face": dict(face_bearing_deg=180.0,
                            props=["SignInfo.*"]),
    },
    # §6.6: 07's trees are a **courtyard group**, not a street route — the same call X4 made
    # for scene13's apartment planting. Declaring a `route` here would import a 6-8 m pitch
    # rule that no temple precinct has ever obeyed. Left empty deliberately; LINT-2/3/4 then
    # report `nodata` plus inferred runs, and an inferred finding may never fail a build.
    routes={},
)


# ===========================================================================
# [C] paths / asset roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene07")

ASSET_ROLES = ["rock_wall", "rock_face", "granite_dark",
               "leaf_ground", "gravel", "grass", "sign_info", "hdri", "mdl"]


# ===========================================================================
# [D] terrain maths (no boot needed - reused as is by SMOKE)
# ===========================================================================
def path_z(x):
    """Corridor (stone slope) top z. x 0..run → 0..−drop, clamped outside."""
    t = max(0.0, min(x / STAIR_RUN, 1.0))
    return -STAIR_DROP * t


def bank_z(x):
    """North (+Y) cut slope top z (gentle 9.3° — a hillside cut face)."""
    t = max(0.0, min(x / STAIR_RUN, 1.0))
    return -2.0 * t


def ground_z(x, y):
    """Ground z for landing the dressing. Corridor/yard/approach · north slope · south terrace."""
    if y >= 2.15:
        return bank_z(x)
    if y <= -1.7:
        return path_z(x) - SIDE_DROP
    return path_z(x)


def _zone_z(x, y, zone):
    """Pick the landing surface by zone tag: north/south/flat (yard z=0)."""
    if zone == "north":
        return bank_z(x)
    if zone == "south":
        return path_z(x) - SIDE_DROP
    if zone == "flat":
        return 0.0
    return ground_z(x, y)


# ===========================================================================
# [E] 자연석 계단 course layout - seed-fixed random (reproducible, no boot needed)
# ===========================================================================
def _rise_table(rng, cp):
    """The 28 riser heights, in order, summing **exactly** to `STAIR_DROP − exit_up`.

    Construction (research §B4, both halves of it):
      1. `w_i ~ N(0, riser_sigma)` truncated at +-2.5 sigma — the *dressed* stone spread.
      2. `s_i = A·sin(2*pi*i/T + phi)`, `A = settle_amp`, `T ∈ settle_period` — the
         **correlated** settlement of the earth core. It is a displacement of the course
         *top*, so it enters the rise table as a first difference `s_i − s_{i−1}`, and
         `s_-1` is evaluated at the notional course before the first one (the yard shoulder).
         This is the whole point: an i.i.d. rise error reads as noise, a long-wave one reads
         as a stair that has been walked on for three hundred years.
      3. Clamp into `rise_band`, then push the residual back onto the courses in proportion
         to their remaining headroom until the sum is exact. The total drop is frozen, so
         the table has to absorb its own noise rather than let the junction drift.

    Returns the rise list `R` where `R[0]` is the **entry** step (yard z 0 -> course 0 top)
    and `R[i]` is the step from course i−1 onto course i.
    """
    n = int(cp["n"])
    sig = float(cp["riser_sigma"])
    amp = float(cp["settle_amp"])
    per = rng.uniform(*cp["settle_period"])
    pha = rng.uniform(0.0, 2.0 * math.pi)

    def settle(i):
        return amp * math.sin(2.0 * math.pi * i / per + pha)

    lo, hi = (float(v) for v in cp["rise_band"])
    mu = (STAIR_DROP - float(cp["exit_up"])) / n
    R = []
    for i in range(n):
        w = rng.gauss(0.0, sig)
        w = max(-2.5 * sig, min(2.5 * sig, w))          # truncated, research §B4
        R.append(mu + w + (settle(i) - settle(i - 1)))
    target = STAIR_DROP - float(cp["exit_up"])
    for _ in range(64):
        R = [min(hi, max(lo, r)) for r in R]
        err = target - sum(R)
        if abs(err) < 1e-12:
            break
        head = [(hi - r) if err > 0 else (r - lo) for r in R]
        tot = sum(head)
        if tot <= 1e-12:
            break
        R = [r + err * h / tot for r, h in zip(R, head)]
    return [min(hi, max(lo, r)) for r in R]


def _course_seams(rng, cp, blocks):
    """Lateral seam positions inside one course, y0..y1, `blocks−1` of them.

    Nominal even split, jittered by `seam_jit` so course seams do not line up down the
    flight, then two guards: no seam inside the walked centre band `|y| <= walk_clear`
    (so the walk-line GT face of a course is always ONE slab), and no slab narrower
    than `min_slab_w`.
    """
    y0, y1 = float(cp["y0"]), float(cp["y1"])
    span = y1 - y0
    mw = float(cp["min_slab_w"])
    wc = float(cp["walk_clear"])
    sj = float(cp["seam_jit"])
    seams = []
    for b in range(1, int(blocks)):
        s = y0 + span * b / float(blocks) + rng.uniform(-sj, sj)
        if abs(s) <= wc:                                 # off the walked centre band
            s = wc + 0.10 if (s >= 0.0) else -(wc + 0.10)
        seams.append(s)
    seams.sort()
    lim = y0
    for k in range(len(seams)):                          # forward min-width pass
        seams[k] = max(seams[k], lim + mw)
        lim = seams[k]
    lim = y1
    for k in range(len(seams) - 1, -1, -1):              # backward pass
        seams[k] = min(seams[k], lim - mw)
        lim = seams[k]
    return [s for s in seams if y0 + mw - 1e-9 <= s <= y1 - mw + 1e-9]


def course_layout():
    """Return the 28-course 자연석 계단 table (computable without booting).

    Each course: dict(i, xa, xb, top, rise, blocks=[slab, ...], bed=dict(...))
      · `xa`/`xb`  nominal tread back / front (`xb` = the nosing line)
      · `top`      the course's **level** tread z = the walk-line GT face
      · slab       dict(k, y0, y1, xb_f, xback, top, yaw, roll, walk)
                   `xback = xa − ov` is NOT jittered, which is what guarantees both the
                   0 % open-slope fraction and the >=50 mm interlock; `xb_f` is.
    """
    cp = PARAMS["courses"]
    rng = random.Random(int(cp["seed"]))
    n = int(cp["n"])
    x0, x1 = float(cp["x0"]), float(cp["x1"])
    tread = (x1 - x0) / n
    ov, jt = float(cp["ov"]), float(cp["jt"])
    fh = float(cp["foot_half"])
    R = _rise_table(rng, cp)
    tops, z = [], 0.0
    for r in R:
        z -= r
        tops.append(z)
    out = []
    for i in range(n):
        xa, xb = x0 + i * tread, x0 + (i + 1) * tread
        nb = rng.choices(list(cp["blocks"]), weights=list(cp["blocks_w"]))[0]
        seams = _course_seams(rng, cp, nb)
        edges = [float(cp["y0"])] + seams + [float(cp["y1"])]
        slabs = []
        for k in range(len(edges) - 1):
            g = rng.uniform(*cp["seam_gap"]) / 2.0
            sy0 = edges[k] + (g if k > 0 else 0.0)
            sy1 = edges[k + 1] - (g if k + 1 < len(edges) - 1 else 0.0)
            walk = (sy0 <= -fh + 1e-9) and (sy1 >= fh - 1e-9)
            # the last course's nosing lands **on** the frozen junction: no front jitter,
            # so x = 12.2 / z = -4.2 cannot drift out from under the approach road.
            xf = xb if i == n - 1 else xb + rng.uniform(-jt / 2.0, jt / 2.0)
            slabs.append(dict(
                k=k, y0=sy0, y1=sy1, xback=xa - ov, xb_f=xf,
                # only a NON-walk slab carries bedding z jitter: the walked face of a
                # course is the rise table's own value, so the GT stays the declared table
                top=tops[i] + (0.0 if walk
                               else rng.uniform(-cp["jz"], cp["jz"])),
                yaw=rng.uniform(-cp["jyaw"], cp["jyaw"]),
                roll=rng.uniform(-cp["jroll"], cp["jroll"]), walk=walk))
        out.append(dict(i=i, xa=xa, xb=xb, top=tops[i], rise=R[i], slabs=slabs,
                        bed=dict(x0=xa - ov, x1=xb, y0=float(cp["y0"]),
                                 y1=float(cp["y1"]),
                                 top=tops[i] - float(cp["bed_drop"]),
                                 thick=float(cp["bed_thick"]))))
    return out


COURSES = course_layout()


def course_top(x, y=0.0):
    """Walked-surface z at station `(x, y)` on the flight.

    With the default `y = 0` this is the course's own level tread z, i.e. the walk-line GT.
    With a real `y` it returns **that slab's** top, which differs from the course value by the
    non-walk slabs' bedding jitter (`jz`) — a mask or a scatter laid on the shoulder has to
    sit on the slab that is actually there, not on the course's nominal plane.
    Outside the flight it degrades to the yard (`x < 0`) or the approach road (`x > run`), so
    it is safe to hand to any `ground_fn` / `z_fn` callback.
    """
    cp = PARAMS["courses"]
    if x < float(cp["x0"]):
        return 0.0
    if x >= float(cp["x1"]):
        return -STAIR_DROP
    tread = (float(cp["x1"]) - float(cp["x0"])) / int(cp["n"])
    i = min(int(cp["n"]) - 1, int((x - float(cp["x0"])) / tread))
    c = COURSES[i]
    for s in c["slabs"]:
        if s["y0"] - 1e-9 <= y <= s["y1"] + 1e-9:
            return s["top"]
    return c["top"]


def kerb_layout():
    """[W3 S3-5 · GT-15] 야면석 kerb boulders, both flanks, discontinuous.

    Each entry: dict(name, asset, cx, cy, seat_z, scale, across, proud, yaw, tilt, flank)
      · `cy` is **edge-anchored**: `sgn*(y_edge − across/2)`, so the boulder's outer edge
        lands just inside the corridor and it never overhangs the south drop (H8) nor
        intersects the north wall. See the PARAMS block for the two declared deviations.
      · `seat_z` is `course_top(cx) − sink`, and `sink <= 0.05` is the F2 no-sink-ring rule.
    """
    kp = PARAMS["kerb"]
    rng = random.Random(int(kp["seed"]))
    pool = list(kp["pool"])
    wts = [float(p[6]) for p in pool]
    x0, x1 = float(kp["x0"]), float(kp["x1"])
    out = []
    span = x1 - x0
    big, small = float(kp["big_gap"]), float(kp["small_gap"])
    pitch = float(kp["pitch"])
    # Station plan, per flank: `nb` stations spanning x0..x1 exactly, with ONE >=3 m gap and
    # TWO ~1.1 m gaps inserted at drawn indices. The residual is spread over the *non-gap*
    # increments only, so a deliberate gap keeps the length it was declared with instead of
    # being scaled away — the earlier "advance and test" form could skip the big gap entirely
    # when a small one had already jumped past its station.
    nb = int(round((span - big - 2.0 * small) / pitch)) + 1
    for flank, sgn in (("S", -1.0), ("N", 1.0)):
        inc = [pitch + rng.uniform(-kp["pitch_jit"], kp["pitch_jit"])
               for _ in range(nb - 1)]
        gi = rng.sample(range(nb - 1), 3)
        inc[gi[0]] += big
        inc[gi[1]] += small
        inc[gi[2]] += small
        free = [j for j in range(nb - 1) if j not in gi]
        resid = span - sum(inc)
        for j in free:
            inc[j] += resid / len(free)
        x = x0
        for k in range(nb):
            a = pool[rng.choices(range(len(pool)), weights=wts)[0]]
            sc_mul = rng.uniform(float(a[4]), float(a[5]))
            across = max(float(a[1]), float(a[2])) * sc_mul
            proud = float(a[3]) * sc_mul
            cy = sgn * (float(kp["y_edge"]) - across / 2.0)
            out.append(dict(name=f"{flank}{k}", asset=a[0], cx=x, cy=cy,
                            seat_z=course_top(x) - float(kp["sink"]),
                            scale=sc_mul, across=across, proud=proud,
                            yaw=rng.uniform(0.0, 360.0),
                            tilt=(rng.uniform(-kp["tilt"], kp["tilt"]),
                                  rng.uniform(-kp["tilt"], kp["tilt"])),
                            flank=flank))
            if k < nb - 1:
                x += inc[k]
    return out


KERB = kerb_layout()


def assign_moss():
    """[W3 S3-6 · GT-17] Zone-driven moss plan (spec §4.1-3), computed once, CPU-only.

    Writes `cap_moss` / `body_moss` onto every slab and `moss` onto every kerb boulder, so
    the SMOKE table and the builder read **one** plan and can never disagree. The slab is
    split into a **cap** (the walked top, `cap_t` thick) and a **body** (the rest, whose front
    face IS the riser), which is the only way to give a tread and its own riser different moss
    without authoring a proud strip along the nosing — and a proud strip along the nosing is
    exactly what H2 / RF-5 forbid on this scene.
    """
    mz = PARAMS["moss_zone"]
    rng = random.Random(int(mz["seed"]))
    walk = []
    for c in COURSES:
        for s in c["slabs"]:
            s["cap_moss"] = (False if s["walk"]
                             else rng.random() < float(mz["p_outer"]))
            s["body_moss"] = rng.random() < float(mz["p_riser"])
            if s["walk"]:
                walk.append(s)
    # The walked centre band's target is 0.00-0.10, i.e. one or two courses out of 28. At
    # that rate a Bernoulli draw's own variance is the whole budget (2 hits already overshoots
    # by area weighting), so this zone is filled by **quota**, not by probability: exactly
    # `round(p_walk_area * n)` courses are picked. Every other zone is wide enough that a
    # draw lands inside its band, and is left as a draw so the pattern stays irregular.
    k = int(round(float(mz["p_walk"]) * len(walk)))
    for s in rng.sample(walk, min(k, len(walk))):
        s["cap_moss"] = True
    for b in KERB:
        b["moss"] = rng.random() < float(mz["p_boulder"])


assign_moss()


def moss_fractions():
    """Achieved moss coverage by §4.1-3 zone, as area fractions. `[measured]` per build."""
    mz = PARAMS["moss_zone"]
    cp = PARAMS["courses"]
    wc = float(cp["walk_clear"])
    a_walk = m_walk = a_out = m_out = a_ris = m_ris = 0.0
    for c in COURSES:
        for s in c["slabs"]:
            dx = s["xb_f"] - s["xback"]
            dy = s["y1"] - s["y0"]
            if s["walk"]:
                aw = dx * (2.0 * wc)          # the walked centre band on this cap
                a_walk += aw
                m_walk += aw if s["cap_moss"] else 0.0
                ao = dx * max(0.0, dy - 2.0 * wc)
            else:
                ao = dx * dy
            a_out += ao
            m_out += ao if s["cap_moss"] else 0.0
            ar = dy * (float(cp["thick"]) - float(mz["cap_t"]))
            a_ris += ar
            m_ris += ar if s["body_moss"] else 0.0
    nb = len(KERB) or 1
    return dict(walk=m_walk / (a_walk or 1.0),
                tread_outer=m_out / (a_out or 1.0),
                riser=m_ris / (a_ris or 1.0),
                joint=1.0,
                boulder_top=sum(1 for b in KERB if b["moss"]) / nb)

def leaf_patches():
    """Leaf carpets → **DEC-2 masks**. `(name, cx, cy, rx, ry)`, one entry per drift.

    [W3 F3 / DEC-2 `[ruled 07-30]` spec §10.5 · CB-2 pilot criterion §7.2]
      The v6 construction laid `subs=3` overlapping **rectangles** per drift and relied on
      the union of their borders to look irregular. It does not: at h0.3 the union of three
      axis-aligned rectangles reads as three axis-aligned rectangles, which is the whole of
      `tonglam_v2.md` §2.13-2's "photographic carpets laid on the DG" and is the named
      pass condition for this pilot (*"07's leaf carpets ... stop being rectangles"*).
      One `ground_kit.build_carpet_mask` lobe now replaces each 3-rectangle stack:
      **18 prims -> 6**, no straight edge anywhere on the boundary, and the mask follows
      the 19 deg corridor exactly because `build_blot` takes a per-vertex `z_fn`
      (= `path_z`) instead of a slope-slab approximation.
      `sub_scale` / `sub_off` / `sub_rz` are retired with the rectangles; `subs` stays in
      PARAMS at 1 so the self-check line keeps reporting the same quantity.
    """
    out = []
    for n, (cx, cy, sx, sy) in enumerate(PARAMS["leaf_drifts"]):
        rx, ry = sx / 2.0, sy / 2.0
        cxc = min(max(float(cx), 0.04 + rx), STAIR_RUN - 0.05 - rx)
        cyc = min(max(float(cy), -1.66 + ry), 1.66 - ry)
        out.append((f"{n}", cxc, cyc, rx, ry))
    return out


LEAF_PATCHES = leaf_patches()


def mask_n(cx):
    """[W3 S3-2] N-gon order for a carpet mask centred at `cx` (see PARAMS['leaf_band']).

    Near-field masks get the raised order; everything else keeps the 24-gon budget.
    One function, used by both the SMOKE table and the builder, so the two can never
    disagree about which mask was polished.
    """
    lb = PARAMS["leaf_band"]
    x0, x1 = lb["chord_near_x"]
    near = float(x0) <= float(cx) <= float(x1)
    return int(lb["n_near"] if near else lb["n_far"])


def stone_metrics():
    """Course-table verification metrics — (rise list, open-gap list, entry/exit steps).

    `gaps` is the **course-to-course open-slope gap** measured per lateral band:
    `slab_back(i) − slab_front(i−1)`. A positive value is bare corridor showing between two
    courses, which is exactly the 34.0 % defect A2; the back-overlap construction makes every
    entry negative, and the self-check asserts `max(gaps) < 0`.
    `enter` = yard z 0 -> course 0 top. `exit_` = course 27 top -> approach road −4.2,
    **positive = the stone stands above the road = an UP-STEP** (GT-14 / GT-1 rule (b)).
    """
    rises = [c["rise"] for c in COURSES]
    gaps = []
    for i in range(1, len(COURSES)):
        prev_front = max(s["xb_f"] for s in COURSES[i - 1]["slabs"])
        back = COURSES[i]["slabs"][0]["xback"]
        gaps.append(back - prev_front)
    enter = 0.0 - COURSES[0]["top"]
    exit_ = COURSES[-1]["top"] - (-STAIR_DROP)
    return rises, gaps, enter, exit_


def course_interlock():
    """Per-course-pair interlock (m): how far course i's back tail runs under course i−1.

    표준시방서 0400-3.2 ㄷ [law]: "아랫돌의 뒤뿌리는 윗돌에 50mm 이상 물리도록 한다".
    Measured per lateral band against the *nearest* slab of the course above, because the
    two courses may be split into a different number of slabs.
    """
    out = []
    for i in range(1, len(COURSES)):
        for s in COURSES[i]["slabs"]:
            ymid = (s["y0"] + s["y1"]) / 2.0
            above = min(COURSES[i - 1]["slabs"],
                        key=lambda t: abs((t["y0"] + t["y1"]) / 2.0 - ymid))
            out.append(above["xb_f"] - s["xback"])
    return out


# ===========================================================================
# [E-2] ground_kit plan - pure CPU, no USD. Coordinates come from PARAMS
#       (spec Sec.7.4: the scene, not the spec table, is the source of truth).
# ===========================================================================
def _plate(name):
    """Axis-aligned ground plate row by name: (name,x0,x1,y0,y1,z_top,t,mtl)."""
    for row in PARAMS["plates"]:
        if row[0] == name:
            return row
    raise KeyError(f"scene07: plate '{name}' not in PARAMS['plates']")


def ground_plan():
    """P12 `courtyard_dg` plan for the temple forecourt (x -24..0, z=0).

    The drop edge is the courtyard shoulder = the Courtyard plate's x1, which
    is also where the discrete stepping stones start. Everything the profile
    would emit as urban infrastructure is blocked by `natural=True`.
    """
    g = PARAMS["gkit"]
    cy = _plate("Courtyard")
    return gk.plan_ground(
        "courtyard_dg",
        region=tuple(float(v) for v in g["region"]),
        z=float(cy[5]), gy=0.0, origin=(0.0, 0.0, 0.0),
        edges=[("courtyard_shoulder", float(cy[2]))],
        dists=(2, 5, 10), scene="scene07",
        tactile=(),                    # Sec.12.4: natural scene -> not listed
        overrides=dict(
            # water = the plinth moss / damp band of Sec.5.7; dirt = tracked soil
            surface=(("stain", ("dirt", "water")),),
            extras=(("wear_lane", dict(width=float(g["wear_w"]))),
                    ("edge_break", dict(density=10.0,
                                        lines=list(g["band_lines"])))),
            scatter=dict(kind="gravel", cover=0.09,
                         count=int(g["gravel_n"]),
                         scale_jitter=(0.38, 0.62), burial=0.38)),   # [W2 F2]
        seed=int(g["seed"]))


# ===========================================================================
# [F] camera presets: grid_views(gy=0.0) + 5 mise-en-scene cuts
#     Every coordinate comes from path_z() - no hardcoding (guarantees slope alignment).
# ===========================================================================
def build_views():
    views = sc.grid_views(0.0)          # h{0.3,0.9,1.8} × d{2,5,10}, +X

    # temple_walk : eye height on the yard, looking ahead - the stones melt into slope and leaves, drop vanishes
    #   [v7] The gate retreated to −5.6 -> the eye pulls back to 3.0 m in front of it, so the gate
    #   frames the path inside the shot (the old −6.0 would sit right under the gate).
    views["temple_walk"] = dict(eye=[-8.6, 0.0, 1.30],
                                tgt=[4.0, 0.0, path_z(4.0) + 0.30])
    # stone_rhythm : close-up of the stones - uneven gaps and rises (broken stepping rhythm)
    views["stone_rhythm"] = dict(eye=[1.0, -1.05, path_z(1.0) + 0.60],
                                 tgt=[5.4, 0.10, path_z(5.4) + 0.05])
    # gate_frame : looking back from mid-descent - frames the gate·lanterns·Dharma hall silhouette
    #   [v7] tgt realigned to the moved gate (cx −5.6). The gate's +X face being shaded is a
    #   structural consequence of sun az 180~270 - awaiting a supervisor decision (mirror the cut).
    views["gate_frame"] = dict(eye=[7.0, 0.0, path_z(7.0) + 1.50],
                               tgt=[PARAMS["gate"]["cx"], 0.0, 1.60])
    # side_slope : section of the unguarded 1.8 m drop, from the lower south terrace
    views["side_slope"] = dict(
        eye=[6.0, -5.2, path_z(6.0) - SIDE_DROP + 1.20],
        tgt=[6.6, -1.5, path_z(6.6) - 0.35])
    # grazing_edge : robot view at the corridor's south shoulder - the lower terrace looks continuous with the corridor
    #   sight pitch (−17.4 deg) < slope angle (19.0 deg) -> the lower terrace compresses toward the horizon
    views["grazing_edge"] = dict(eye=[2.0, 1.10, path_z(2.0) + 0.30],
                                 tgt=[12.0, -1.50, path_z(12.0) + 0.60])
    return views


# ===========================================================================
# [G] SMOKE - geometry self-verification without booting
# ===========================================================================
def lantern_height():
    """Total lantern height (base stone underside → top of the jewel finial)."""
    ln = PARAMS["lantern"]
    return (ln["plinth_h"] + ln["lower_h"] + ln["shaft_h"] + ln["upper_h"]
            + ln["fire_h"] + ln["cap_h"] + ln["cap2_h"] + 2 * ln["jewel_r"])


def _grid_obstacles():
    """AABB list for the grid camera (−d, 0, h) collision check [(name,x0,x1,y0,y1,z0,z1)]."""
    g = PARAMS["gate"]
    hl = PARAMS["hall"]
    sg = PARAMS["sign"]
    ln = PARAMS["lantern"]
    obs = []
    for tag, sgn in (("P", 1.0), ("N", -1.0)):
        cy = sgn * g["half_y"]
        pr = g["post_r"] * 1.55            # [v6] includes the plinth radius
        obs.append((f"GatePost_{tag}", g["cx"] - pr, g["cx"] + pr,
                    cy - pr, cy + pr, 0.0, g["post_h"]))
    # [v6] Includes the flying rafter (2nd-tier eave) - the lowest eave z is ridge−0.45−drop'−0.11
    obs.append(("GateRoof", g["cx"] - g["roof_half_run"] - 0.35,
                g["cx"] + g["roof_half_run"] + 0.35,
                -(g["roof_y"] + 0.22), g["roof_y"] + 0.22,
                g["ridge_z"] - 0.45 - g["roof_drop"] * 1.20 - 0.11,
                g["ridge_z"]))
    obs.append(("Hall", hl["cx"] - hl["sx"] / 2.0, hl["cx"] + hl["sx"] / 2.0,
                hl["cy"] - hl["roof_y"], hl["cy"] + hl["roof_y"],
                0.0, hl["ridge_z"]))
    # [GT-84] gated with the build: an obstacle that is not built is not an obstacle. The AABB
    #   stays here for the `cue_sign=True` ablation arm.
    if SCENE_CONFIG["cue_sign"]:
        obs.append(("SignPost", sg["cx"] - 0.06, sg["cx"] + 0.06,
                    sg["cy"] - sg["w"] / 2.0, sg["cy"] + sg["w"] / 2.0,
                    0.0, sg["pole_h"]))
    for i, p in enumerate(PARAMS["lanterns"]):
        r = ln["cap_w"] / 2.0
        obs.append((f"Lantern_{i}", p["cx"] - r, p["cx"] + r,
                    p["cy"] - r, p["cy"] + r, 0.0, lantern_height()))
    for name, cx, cy, zone, th in PARAMS["pines"]:
        gz = _zone_z(cx, cy, zone)
        obs.append((f"Pine_{name}", cx - 0.9, cx + 0.9, cy - 0.9, cy + 0.9,
                    gz, gz + th + 1.4))
    # [S3-5] the two framing trunks stand close to the corridor, so they belong in the
    #   grid-camera collision list even though the grid eyes sit at x −2 / −5 / −10.
    for t in PARAMS["frame_trees"]:
        gz = _zone_z(t["cx"], t["cy"], t["zone"])
        r = 1.6
        obs.append((f"FrameTree_{t['name']}", t["cx"] - r, t["cx"] + r,
                    t["cy"] - r, t["cy"] + r, gz, gz + t["trunk_h"] * 1.6))
    return obs


def stone_course_selfcheck():
    """[W3 S3-4 · spec §6.5] The 자연석 계단 course table, asserted line by line.

    House style is `scene05.podium_step_selfcheck` / `scene09.roof_normal_selfcheck`:
    print the measured quantity next to the threshold and the authority, and say OK/FAIL
    rather than leaving the reader to compare two numbers in their head.
    """
    P = PARAMS
    cp = P["courses"]
    n = int(cp["n"])
    tread = (float(cp["x1"]) - float(cp["x0"])) / n
    rises, gaps, enter, exit_ = stone_metrics()
    lo, hi = (float(v) for v in cp["rise_band"])
    bed = float(cp["corridor_bed"])
    thick = float(cp["thick"])

    print("\n  [표] 자연석 계단 코스표 (i, xa..xb, 판수, 상면 z, 답차, "
          "코스간 개방, 물림)")
    print(f"    {'i':>2} {'xa':>6} {'xb':>6} {'판':>3} {'top z':>8} "
          f"{'답차':>6} {'개방':>7} {'물림':>6} {'선단요철':>8} 워크라인")
    ok_walk, ok_seam = True, True
    ilk = course_interlock()
    for c in COURSES:
        i = c["i"]
        # a course covers the walk line iff SOME slab spans |y| <= foot_half
        covers = any(s["walk"] for s in c["slabs"])
        ok_walk = ok_walk and covers
        # exactly one slab may own the walk band (no joint on the walk line)
        ok_seam = ok_seam and (sum(1 for s in c["slabs"] if s["walk"]) == 1)
        gp = gaps[i - 1] if i > 0 else float("nan")
        fronts = [s["xb_f"] for s in c["slabs"]]
        ragged = max(fronts) - min(fronts)
        il = float("nan")
        if i > 0:
            per = []
            for s in c["slabs"]:
                ym = (s["y0"] + s["y1"]) / 2.0
                above = min(COURSES[i - 1]["slabs"],
                            key=lambda t: abs((t["y0"] + t["y1"]) / 2.0 - ym))
                per.append(above["xb_f"] - s["xback"])
            il = min(per)
        print(f"    {i:2d} {c['xa']:6.2f} {c['xb']:6.2f} "
              f"{len(c['slabs']):3d} {c['top']:8.3f} {c['rise']:6.3f} "
              f"{gp:+7.3f} {il:6.3f} {ragged:8.3f} "
              f"{'OK' if covers else 'MISS'}")

    # A2 — the headline defect. open-slope fraction = sum(positive course gaps) / run
    openslope = sum(max(0.0, g) for g in gaps)
    frac = openslope / (float(cp["x1"]) - float(cp["x0"]))
    print(f"\n    [A2] 개방 사면 비율 = Σ(코스간 양의 간격)/run = "
          f"{openslope:.4f}/{float(cp['x1']) - float(cp['x0']):.2f} = "
          f"{frac*100:.3f} %  (목표 0.000 %, 재건 전 34.0 % → "
          f"{'OK' if frac < 1e-9 else 'FAIL'})")
    print(f"         최대 코스간 간격 {max(gaps):+.4f} m (<0 = 항상 겹침 → "
          f"{'OK' if max(gaps) < 0.0 else 'FAIL'}) · 뒤물림 min "
          f"{min(ilk):.4f} / max {max(ilk):.4f} m "
          f"(표준시방서 0400-3.2 ㄷ ≥0.050 → "
          f"{'OK' if min(ilk) >= 0.050 - 1e-9 else 'FAIL'})")

    # within-course joints: seam gap + the two neighbours' yaw at the far end
    jmax = 0.0
    for c in COURSES:
        for k in range(len(c["slabs"]) - 1):
            a, b = c["slabs"][k], c["slabs"][k + 1]
            la = (a["xb_f"] - a["xback"]) / 2.0
            lb = (b["xb_f"] - b["xback"]) / 2.0
            jmax = max(jmax, (b["y0"] - a["y1"])
                       + la * abs(math.sin(math.radians(a["yaw"])))
                       + lb * abs(math.sin(math.radians(b["yaw"]))))
    print(f"    [줄눈] 코스 내 최대 가시 줄눈 {jmax:.4f} m "
          f"(G7 0.00~0.06 → {'OK' if jmax <= 0.060 + 1e-9 else 'FAIL'}) · "
          f"건식(모르타르 0) — 표준시방서 0400-1.3 ㄹ 건식쌓기")
    print(f"    [워크라인] 전 코스가 |y| ≤ {cp['foot_half']} 를 덮는가 → "
          f"{'OK' if ok_walk else 'FAIL'} · 워크밴드에 줄눈 없음(1판 전담) → "
          f"{'OK' if ok_seam else 'FAIL'}")

    # A3 — rise table against the declared band
    mu = sum(rises) / len(rises)
    print(f"    [A3 답차] min {min(rises):.4f} / max {max(rises):.4f} / "
          f"평균 {mu:.4f} / 편차폭 {max(rises)-min(rises):.4f} m "
          f"(선언대 {lo:.3f}~{hi:.3f} → "
          f"{'OK' if min(rises) >= lo - 1e-9 and max(rises) <= hi + 1e-9 else 'FAIL'})"
          f" · 합 {sum(rises):.6f} = 낙차−탈출 "
          f"{STAIR_DROP - float(cp['exit_up']):.6f} → "
          f"{'OK' if abs(sum(rises) - (STAIR_DROP - float(cp['exit_up']))) < 1e-9 else 'FAIL'}")
    print(f"         구성: 마름돌 σ{cp['riser_sigma']*1000:.0f} mm 백색잡음 + "
          f"상관 침하 ±{cp['settle_amp']*1000:.0f} mm / "
          f"{cp['settle_period'][0]:.0f}~{cp['settle_period'][1]:.0f}단 "
          f"(연구 §B4 — 백색잡음만으로는 가짜로 읽힌다)")
    print(f"    [2H+B] 2×{mu:.4f} + {tread:.4f} = {2*mu + tread:.4f} m · "
          f"KFS 표 13-1 20° 행 0.710 대비 {(2*mu + tread - 0.710)*1000:+.0f} mm · "
          f"KCS 34 50 10 3.2.8(3) 0.600~0.650 밖 — 28코스는 §8.R OQ-7 결재값이고 "
          f"run·drop 이 동결이라 n 이 2H+B 를 유일하게 결정한다(20.39/n). 게이트 아님, 기록값")

    # A11 — entry / exit
    print(f"    [A11 진입] 마당 z0 → 코스0 상면 = {enter:+.4f} m "
          f"(≈1답차 {mu:.3f} → {'OK' if 0.10 <= enter <= 0.20 else 'CHECK'}, "
          f"재건 전 +0.002)")
    print(f"    [A11 탈출] 코스{n-1} 상면 {COURSES[-1]['top']:.3f} vs 진입로 "
          f"{-STAIR_DROP:.3f} = {exit_:+.4f} m → **UP-STEP** "
          f"(돌이 노면보다 높다 = 진입로에서 오르는 단, 낙차 아님; GT-14·GT-1 규칙(b)) · "
          f"≤0.05 → {'OK' if 0.0 < exit_ <= 0.050 else 'FAIL'} · "
          f"조경설계기준 21.5(6) 디딤돌 돌출 30 mm · 재건 전 +0.201")

    # A9 — bedding: nothing floats, nothing pokes through
    mint, maxb = 1e9, -1e9
    for c in COURSES:
        pt_back = path_z(c["xa"] - float(cp["ov"])) - bed
        pt_front = path_z(c["xb"]) - bed
        for s in c["slabs"]:
            roll = (s["y1"] - s["y0"]) / 2.0 * math.sin(
                math.radians(abs(s["roll"])))
            mint = min(mint, s["top"] - roll - pt_back)      # >0 = no poke-through
        maxb = max(maxb, (c["bed"]["top"] - c["bed"]["thick"]) - pt_front)
    print(f"    [A9 정착] 회랑 베드 z0 −{bed:.2f} m (path_z 자체는 불변) · "
          f"트레드 최저 모서리 − 베드 상면 min {mint:+.4f} m "
          f"(>0 = 19° 평면이 수평 트레드를 뚫지 않음 → "
          f"{'OK' if mint > 0.0 else 'FAIL'})")
    print(f"         속채움 하면 − 베드 상면 max {maxb:+.4f} m "
          f"(<0 = 공중 부양 없음 → {'OK' if maxb < 0.0 else 'FAIL'}) · "
          f"판 두께 {thick:.3f} m (KFS 13-2 가 자연석 계단석 300×300×250)")

    # walk-line flatness under the out-of-level roll
    dev = float(cp["foot_half"]) * math.sin(math.radians(float(cp["jroll"])))
    print(f"    [수평] 판 out-of-level ±{cp['jroll']:.1f}° (연구 §B4 "
          f"U(−2.5,+2.5)) → 워크밴드 |y|≤{cp['foot_half']} 안 z 편차 "
          f"≤{dev*1000:.1f} mm · 코스 상면은 수평 (조경설계기준 21.8(1) "
          f"'지면과 수평이 되게')")

    # the frozen junction must not drift
    reach = max(s["xb_f"] + (s["y1"] - s["y0"]) / 2.0
                * abs(math.sin(math.radians(s["yaw"])))
                for c in COURSES for s in c["slabs"])
    print(f"    [동결] run {STAIR_RUN:.2f} · drop {STAIR_DROP:.2f} · "
          f"SIDE_DROP {SIDE_DROP:.2f} 불변 · 최말단 코스 선단 = "
          f"{COURSES[-1]['xb']:.3f} (지터 0, 접합부 x=12.2 고정) · "
          f"요 포함 최대 x 도달 {reach:.3f} m")

    # [S3-3 · GT-16] the knob / jitter-cap row keeps reporting after the rebuild
    print(f"    [S3-3] 노브 0프림(GT-16 삭제 유지) · 코스 측방 오프셋 0 (A6) · "
          f"판당 요 캡 ±{cp['jyaw']:.1f}° (J-14 ≤3.0 → "
          f"{'OK' if cp['jyaw'] <= 3.0 else 'FAIL'})")

    # ── [S3-5 · GT-15] kerb boulders ──
    kp = P["kerb"]
    fh = float(cp["foot_half"])
    clear = fh + float(kp["foot_clear"])
    inner = min(abs(b["cy"]) - b["across"] / 2.0 for b in KERB)
    outer = max(abs(b["cy"]) + b["across"] / 2.0 for b in KERB)
    ns = sum(1 for b in KERB if b["flank"] == "S")
    nn = len(KERB) - ns
    xs_s = sorted(b["cx"] for b in KERB if b["flank"] == "S")
    xs_n = sorted(b["cx"] for b in KERB if b["flank"] == "N")
    gaps_s = [b - a for a, b in zip(xs_s, xs_s[1:])]
    gaps_n = [b - a for a, b in zip(xs_n, xs_n[1:])]
    prd = [b["proud"] - float(kp["sink"]) for b in KERB]
    acr = [b["across"] for b in KERB]
    print(f"\n  [S3-5 · GT-15] 야면석 연석 {len(KERB)}괴 (남 {ns} / 북 {nn}, "
          f"목표 12~16/측 → "
          f"{'OK' if 12 <= ns <= 16 and 12 <= nn <= 16 else 'CHECK'})")
    print(f"    워크라인 이격: 최소 내측 |y| {inner:.3f} m "
          f"(≥ foot_half+{kp['foot_clear']:.2f} = {clear:.2f} → "
          f"{'OK' if inner >= clear - 1e-9 else 'FAIL'}) · 최대 외측 |y| "
          f"{outer:.3f} m (≤ 회랑 가장자리 1.70 = 남측 낙차 위 돌출 없음 → "
          f"{'OK' if outer <= 1.70 + 1e-9 else 'FAIL'})")
    print(f"    크기 {min(acr):.3f}~{max(acr):.3f} m (§4.1-2 0.40~0.90 → "
          f"{'OK' if min(acr) >= 0.40 - 1e-9 and max(acr) <= 0.90 + 1e-9 else 'CHECK'})"
          f" · 트레드 위 돌출 {min(prd):.3f}~{max(prd):.3f} m "
          f"(0.15~0.35 → "
          f"{'OK' if min(prd) >= 0.15 - 1e-9 and max(prd) <= 0.35 + 1e-9 else 'CHECK'})"
          f" · 매몰 {kp['sink']:.3f} m (F2 ≤0.05 = 검은 침하링 금지 → "
          f"{'OK' if kp['sink'] <= 0.05 else 'FAIL'})")
    print(f"    불연속: 남 최대 간격 {max(gaps_s):.2f} m / 북 "
          f"{max(gaps_n):.2f} m (≥3.0 m 의도적 공백 1회 이상 → "
          f"{'OK' if max(gaps_s) >= 3.0 and max(gaps_n) >= 3.0 else 'CHECK'}) · "
          f"연속 연석이 아니어야 한다(장대석 소맷돌 오독 방지)")
    print(f"    H8: 연석은 회랑 어깨(|y| {inner:.2f}~{outer:.2f})에 있고 테라스 "
          f"가장자리 y −1.70 에는 없다 — 남측 1.8 m 무방호 낙차는 방호되지 않는다")

    # ── [S3-5] fern margins + framing trunks ──
    fp = P["ferns"]
    # ── [S3-6 · GT-17] season re-bind + moss zones ──
    leaf_surf = [nm for nm, *_r, mk in P["plates"] if mk == "leaf"] \
        + [nm for nm, _z0, _d, _y0, _y1, _t, mk in P["slopes"] if mk == "leaf"]
    mz = P["moss_zone"]
    mf = moss_fractions()
    print(f"\n  [S3-6 · GT-17] 여름 고정 — leaf_ground 결합 지면 플레이트/사면 "
          f"{len(leaf_surf)}면 (재바인딩 전 5면: PathCorridor·SouthTerraceA/B/C·"
          f"Approach → forest) → "
          f"{'OK' if not leaf_surf else 'FAIL ' + str(leaf_surf)}")
    print(f"    낙엽 로브: 회랑 {len(P['leaf_drifts'])}매 |cy| min "
          f"{min(abs(c[1]) for c in P['leaf_drifts']):.2f} "
          f"(§4.1-5 ≥1.0 = 여백 이동 → "
          f"{'OK' if min(abs(c[1]) for c in P['leaf_drifts']) >= 1.0 else 'FAIL'}) · "
          f"워크라인 |y|≤{cp['foot_half']} 침범 없음 → "
          f"{'OK' if min(abs(c[1]) - c[3] / 2.0 for c in P['leaf_drifts']) > cp['foot_half'] else 'FAIL'}"
          f" · 마당 로브 {len(P['yard_drifts'])}매 유지 · 페더 cover 회랑 "
          f"{P['leaf_band']['cover_corridor']:.3f} / 마당 "
          f"{P['leaf_band']['cover_yard']:.3f}")
    print(f"    sct_debris_leaves_dry_* 배치 0건 (SCENE_SCOPE 은 '07' 을 허용하지만 "
          f"07 은 여름 — 허용은 권고가 아니다, H10)")
    print(f"    [§4.1-3 이끼 구역] 실측 커버리지 (목표는 [ref]+[assumed], "
          f"게이트 아님 — 통람이 판정)")
    for zk, lab in (("walk", "보행 중앙대 |y|≤0.35"),
                    ("tread_outer", "답면 외측"),
                    ("riser", "챌면(판 몸통)"),
                    ("joint", "줄눈·속채움"),
                    ("boulder_top", "야면석 상면")):
        tgt = mz[zk]
        band = f"{tgt[0]:.2f}~{tgt[1]:.2f}" if isinstance(tgt, tuple) \
            else f"{float(tgt):.2f}"
        ok = (tgt[0] - 1e-9 <= mf[zk] <= tgt[1] + 1e-9) \
            if isinstance(tgt, tuple) else abs(mf[zk] - float(tgt)) < 1e-9
        print(f"      {lab:<20} 실측 {mf[zk]:.3f}  목표 {band}  "
              f"{'IN' if ok else 'OUT'}")
    print(f"      여백 |y|>1.70          목표 {mz['margin']:.2f} — 고사리대 "
          f"{P['ferns']['north']['n'] + P['ferns']['south']['n']}주 + gk 이끼 "
          f"stain 으로 구성, 재질 분할 아님(측정 안 함)")

    print(f"  [S3-5] 고사리대 스탠드인 {fp['north']['n'] + fp['south']['n']}주 "
          f"(북 {fp['north']['n']} y{fp['north']['y']} / 남 "
          f"{fp['south']['n']} y{fp['south']['y']}) — G2 공백, "
          f"Switchgrass 대체(실물 고사리 아틀라스는 R7-3 조달행) · "
          f"프레이밍 노거수 {len(P['frame_trees'])}주 "
          f"(trunk_h {'/'.join('%.1f' % t['trunk_h'] for t in P['frame_trees'])} "
          f"→ 에셋 경로 총고 ×1.60)")


def _smoke_report():
    P = PARAMS
    print("=" * 72)
    print("scene07_temple_stone_path (v5 R2) — SMOKE 기하 자기검증 (부팅 없음)")
    print("=" * 72)
    slope_deg = math.degrees(math.atan2(STAIR_DROP, STAIR_RUN))
    cp = P["courses"]
    tread = (float(cp["x1"]) - float(cp["x0"])) / int(cp["n"])
    nslab = sum(len(c["slabs"]) for c in COURSES)
    print(f"  사면: run {STAIR_RUN:.2f} m / drop {STAIR_DROP:.2f} m "
          f"= {slope_deg:.1f}°  · 자연석 계단 {len(COURSES)}코스 / "
          f"{nslab}판 (seed {cp['seed']})")
    print(f"  낙차 검증: 주낙차 {STAIR_DROP:.2f} ≥ 0.3 → "
          f"{'OK' if STAIR_DROP >= 0.3 else 'FAIL'} · "
          f"측방 {SIDE_DROP:.2f} ≥ 0.3 → "
          f"{'OK' if SIDE_DROP >= 0.3 else 'FAIL'}")

    # ── stone_course_selfcheck (spec §6.5) ──
    stone_course_selfcheck()

    # ── [W3 F3] leaf carpets : DEC-2 masks — slope alignment + corridor containment ──
    #    The mask is a `build_blot` N-gon normalised to max radius 1, so the lobe
    #    **inscribes** (cx±rx, cy±ry) and the containment test is exact on the bbox.
    lb = P["leaf_band"]
    ferr, dk = 0.0, gk.dry_kit()
    for nm, cx, cy, rx, ry in LEAF_PATCHES:
        b = gk.build_blot(dk, f"/dry/LeafMask_{nm}", cx, cy, rx, ry, None,
                          n=mask_n(cx), rough=0.18,
                          seed=int(lb["seed"]) + int(nm),
                          z=0.0, proud=lb["proud"],
                          z_fn=course_top)
        for (px, py), pz in zip(b["points"], b["zs"]):
            ferr = max(ferr, abs(pz - (course_top(px, py) + lb["proud"])))
    yout = max(abs(cy) + ry for _n, _cx, cy, _rx, ry in LEAF_PATCHES)
    xout = max(cx + rx for _n, cx, _cy, rx, _ry in LEAF_PATCHES)
    xin = min(cx - rx for _n, cx, _cy, rx, _ry in LEAF_PATCHES)
    print(f"\n  [W3 낙엽] 마스크 {len(LEAF_PATCHES)}매(드리프트 "
          f"{len(P['leaf_drifts'])}×{lb['subs']}, 직사각 0매) · "
          f"정점 z = course_top(x)+{lb['proud']:.3f} 정합 오차 "
          f"{ferr:.4f} m ({'OK' if ferr < 1e-6 else 'FAIL'})")
    print(f"    최대 |y| {yout:.3f} (<1.70 = 남측 공동 위 부유 없음 → "
          f"{'OK' if yout < 1.70 else 'FAIL'}) · x 범위 {xin:.2f}..{xout:.2f} "
          f"(≤{STAIR_RUN:.2f} → "
          f"{'OK' if xout <= STAIR_RUN + 1e-9 and xin >= 0.0 else 'CHECK'})")
    # [S3-2] chord polish table - which masks were raised and what it bought (sagitta)
    allm = ([(f"LeafDrift_{nm}", cx, rx) for nm, cx, _cy, rx, _ry in LEAF_PATCHES]
            + [(f"YardLeaf_{i}", cx, sx / 2.0)
               for i, (cx, _cy, sx, _sy) in enumerate(P["yard_drifts"])])
    nn_near = sum(1 for _nm, cx, _r in allm if mask_n(cx) == lb["n_near"])
    sag24 = max(r * (1.0 - math.cos(math.pi / lb["n_far"]))
                for _nm, cx, r in allm if mask_n(cx) == lb["n_near"]) \
        if nn_near else 0.0
    sagn = max(r * (1.0 - math.cos(math.pi / mask_n(cx)))
               for _nm, cx, r in allm if mask_n(cx) == lb["n_near"]) \
        if nn_near else 0.0
    print(f"    [S3-2 현폭] 근경 마스크 {nn_near}매 n {lb['n_far']}→"
          f"{lb['n_near']} (근경대 x{lb['chord_near_x']}) · 최대 현-호 새지타 "
          f"{sag24*1000:.1f}→{sagn*1000:.1f} mm "
          f"(1 m 시거·0.582 mrad/px → {sag24/0.000582:.1f}→{sagn/0.000582:.1f} px) · "
          f"프림 증가 0 (N-gon 1 Mesh)")
    for nm, cx, r in allm:
        print(f"      {nm:<14} cx {cx:+7.2f} r {r:4.2f} n {mask_n(cx):3d} "
              f"{'근경' if mask_n(cx) == lb['n_near'] else '원경'}")

    # ── [S3-7] crest roof cluster — sightline, computed, not eyeballed ──
    #    §4.1-4: "the roofs must be visible over the crest from `gate_frame`'s eye … compute
    #    it in SMOKE, do not eyeball it". G7's own perspective (roof top surfaces seen from a
    #    camera below the crest) is not self-consistent; what IS buildable is a numeric
    #    clearance above the crest sightline, so that is what is asserted.
    hl = P["hall"]
    ep = P["eave"]
    v_gf = build_views()["gate_frame"]
    ex, _ey, ez = (float(v) for v in v_gf["eye"])
    crest_x, crest_z = 0.0, 0.0            # the yard shoulder is the crest for this cut
    print("\n  [S3-7 지붕군] gate_frame 시선 위 여유 (눈 "
          f"({ex:.2f}, {ez:.2f}) → 마루 x{crest_x:.1f} z{crest_z:.2f})")
    ok_sl = True
    for nm, cx, s, z0 in ([("Hall", hl["cx"], 1.0, 0.0)]
                          + [(r["name"], r["cx"], float(r["s"]),
                              float(r["z0"])) for r in P["roof_cluster"]]):
        ridge = z0 + hl["ridge_z"] * s
        # the crest sightline extended to this roof's x
        t = (cx - ex) / (crest_x - ex) if abs(crest_x - ex) > 1e-9 else 1.0
        z_line = ez + (crest_z - ez) * t
        clr = ridge - z_line
        ok_sl = ok_sl and clr > 0.0
        print(f"    {nm:<5} cx {cx:+7.2f} 용마루 z {ridge:5.2f} vs 시선 z "
              f"{z_line:5.2f} → 여유 {clr:+.2f} m "
              f"{'OK' if clr > 0.0 else 'FAIL(마루에 가림)'}")
    eave_z = hl["ridge_z"] - hl["roof_drop"] + float(ep["lift"])
    print(f"    처마: 직선 평면 대비 끝단 +{ep['lift']:.2f} m / 마지막 "
          f"{ep['run']:.2f} m (x 연장 없음 = 새 그림자 없음) · 끝단 z "
          f"{eave_z:.2f} · 서까래 {ep['dentil_n']}개(근경 지붕 +X 처마 한정) · "
          f"단청 벽편 1 · 목주 Ø{P['pole']['r']*2*1000:.0f} mm × "
          f"{P['pole']['h']:.1f} m @ ({P['pole']['cx']:+.1f}, "
          f"{P['pole']['cy']:+.1f}) → {'OK' if ok_sl else 'CHECK'}")
    print("    ※ H16: gate_frame 은 판정 프레임이 아니다(프리셋 5컷에 없음). "
          "이 절은 기록용이며 계단 충실도와 교환하지 않는다.")

    # ── [v6] sun bearing -> per-face direct-light lambert check ──
    az = 33.5 + float(P["SUN_AZ_OFFSET"])
    el = math.radians(float(P["light"]["noon_sun_elev"]))
    lx = math.cos(math.radians(az)) * math.cos(el)
    ly = math.sin(math.radians(az)) * math.cos(el)
    lz = math.sin(el)
    print(f"\n  [v6 태양] offset {P['SUN_AZ_OFFSET']:.1f} → 월드 az {az:.1f}° "
          f"(그림자 az {az - 180:.1f}°) · 고도 {math.degrees(el):.2f}°")
    for nm, N in (("−X향(원경 능선·문 정면)", (-1, 0, 0)),
                  ("−Y향(남측 무방호 석축)", (0, -1, 0)),
                  ("상면(마당·회랑·배석)", (0, 0, 1)),
                  ("+X향(gate_frame 문 배면)", (1, 0, 0))):
        d = N[0] * lx + N[1] * ly + N[2] * lz
        print(f"    {nm:<24} lambert {d:+.3f} "
              f"{'순광' if d > 0.15 else ('터미네이터' if d > 0 else '음영')}")
    lam_x = -lx                                   # −X-facing lambert (distant ridge)
    for nm, key, old_a, old_l in (("근경 능선", "ridge_near", 0.052, 0.456),
                                  ("중경 능선", "ridge_mid", 0.088, 0.456),
                                  ("원경 능선", "ridge_far", 0.142, 0.456),
                                  ("마루 숲(근)", "crest_near", 0.042, 0.456)):
        a_new = P["material"][key][0]
        print(f"    {nm:<12} 알베도 {old_a:.3f}→{a_new:.3f} · 휘도곱 "
              f"{old_a*old_l:.4f} → {a_new*lam_x:.4f} "
              f"({'보존 OK' if a_new*lam_x >= old_a*old_l else 'CHECK(어두워짐)'}"
              f") · 순백 상한 0.72 "
              f"{'OK' if a_new <= 0.72 else 'FAIL'}")

    # ── [v7] cast shadow footprint x grid lower-half ground band ──
    #   Lesson (end of judge_v7): "shadows do not vanish, they move". A per-face lambert table
    #   does not tell you **where the cast shadow goes** - the cell W2 missed was the
    #   'grid near-view ground'. Here the two tables are compared on one screen.
    #   · shadow projection : P -> P − L·(P.z/L.z),  horizontal shift = −(cos az, sin az)·z·cot(el)
    #   · lower-half ground band : vertical half-FOV 18.0 deg (focal 18.147 / vertical aperture 11.787),
    #     pitch −10 deg -> the x span where the frame-bottom −28 deg · centre −10 deg rays meet the yard (z=0)
    cot = math.cos(el) / math.sin(el)
    sdx = -math.cos(math.radians(az)) * cot
    sdy = -math.sin(math.radians(az)) * cot
    g = P["gate"]
    ln_h = lantern_height()
    casters = [
        ("일주문 주지붕", g["cx"] - g["roof_half_run"],
         g["cx"] + g["roof_half_run"], -g["roof_y"], g["roof_y"],
         g["ridge_z"] - g["roof_drop"], g["ridge_z"]),
        ("일주문 부연", g["cx"] - g["roof_half_run"] - 0.30,
         g["cx"] + g["roof_half_run"] + 0.30, -(g["roof_y"] + 0.22),
         g["roof_y"] + 0.22,
         g["ridge_z"] - 0.45 - g["roof_drop"] * (g["roof_half_run"] + 0.30)
         / g["roof_half_run"], g["ridge_z"] - 0.45),
        ("일주문 기둥", g["cx"] - 0.24, g["cx"] + 0.24, -g["half_y"] - 0.24,
         g["half_y"] + 0.24, 0.0, g["post_h"]),
        ("석등(남)", P["lanterns"][1]["cx"] - 0.47,
         P["lanterns"][1]["cx"] + 0.47, P["lanterns"][1]["cy"] - 0.47,
         P["lanterns"][1]["cy"] + 0.47, 0.0, ln_h),
        ("법당", P["hall"]["cx"] - P["hall"]["sx"] / 2.0,
         P["hall"]["cx"] + P["hall"]["sx"] / 2.0,
         P["hall"]["cy"] - P["hall"]["roof_y"],
         P["hall"]["cy"] + P["hall"]["roof_y"], 0.0, P["hall"]["ridge_z"]),
    ]
    # [GT-84] The notice board is a caster only on the `cue_sign=True` ablation arm. The table
    #   reports what is actually built, so the row is gated rather than deleted.
    if SCENE_CONFIG["cue_sign"]:
        casters.insert(4, ("안내판", P["sign"]["cx"] - 0.06,
                           P["sign"]["cx"] + 0.06,
                           P["sign"]["cy"] - P["sign"]["w"] / 2.0,
                           P["sign"]["cy"] + P["sign"]["w"] / 2.0,
                           0.0, P["sign"]["pole_h"]))
    print("\n  [v7 그림자] 캐스터 → 마당(z=0) 투영 발자국 · 워크라인 |y|≤0.22")
    shade = []                       # (name, x0, x1, y_south) - shadow on the yard
    for nm, x0, x1, y0, y1, zlo, zhi in casters:
        xs = [x + sdx * z for x in (x0, x1) for z in (zlo, zhi)]
        ys = [y + sdy * z for y in (y0, y1) for z in (zlo, zhi)]
        sx0, sx1, sy0, sy1 = min(xs), max(xs), min(ys), max(ys)
        cross = (sy0 <= 0.22 and sy1 >= -0.22)
        shade.append((nm, sx0, sx1, sy0))
        print(f"    {nm:<12} x[{sx0:+6.2f},{sx1:+6.2f}] y[{sy0:+6.2f},"
              f"{sy1:+6.2f}]  워크라인 {'가로지름' if cross else '비껴감'}")
    big = [s for s in shade if (s[2] - s[1]) * 1.0 >= 2.0]     # large casters only
    print("  [v7 하반 지면대] 프리셋별 프레임 아래절반이 찍는 마당 구간 "
          "(x_하단…x_중앙) vs 대형 그림자")
    for h in (0.3, 0.9, 1.8):
        for d in (2, 5, 10):
            xe = -float(d)
            xn = xe + h / math.tan(math.radians(28.0))
            xm = xe + h / math.tan(math.radians(10.0))
            half_w = (xn - xe) * math.tan(math.radians(30.0))   # near-end half-width
            ov = []
            for nm, sx0, sx1, sy0 in big:
                if sx1 > xn and sx0 < xm and sy0 < half_w:
                    ov.append(nm if sy0 <= -half_w else f"{nm}(북측만)")
            state = "직사광" if not ov else ("부분(" + ",".join(ov) + ")")
            print(f"    h{h}_d{d:<3} 지면대 x[{xn:+6.2f},{xm:+6.2f}] "
                  f"반폭 ±{half_w:.2f} → {state}")
    print("    ※ x_중앙 > 0 인 프리셋은 하반이 배석·회랑(사면)이라 마당 투영이"
          " 아니라 SMOKE 사면 표로 판정한다.")

    # ── ground plate table + south drop verification ──
    print("\n  [표] 축정렬 지면 플레이트 (상면 z / 두께)")
    print(f"    {'이름':16s} {'x범위':>16s} {'y범위':>16s} {'상면z':>7s} 두께")
    for nm, x0, x1, y0, y1, zt, th, _m in P["plates"]:
        print(f"    {nm:16s} [{x0:7.1f},{x1:7.1f}] [{y0:7.2f},{y1:7.2f}] "
              f"{zt:7.2f} {th:5.2f}")
    print("  [표] 사면 플레이트 (x0=0, run=%.2f)" % STAIR_RUN)
    for nm, z0, drop, y0, y1, th, _m in P["slopes"]:
        print(f"    {nm:16s} z0 {z0:+6.2f} → {z0 - drop:+6.2f}  "
              f"y[{y0:7.2f},{y1:7.2f}] 두께 {th:.2f}")

    # ── [GT-126] StairCheekN 포함검산 — 디딤판 무이동으로 벽·계단 얽힘 해소 ──
    #   (a) 뺨돌 상단 라킹선(코드 z + z0)이 북측 플랭크 판의 모든 모서리 상단을
    #       덮는가 (roll 모서리 + jz 포함), (b) yaw 지터 북측 모서리 y 가 뺨돌
    #       북변(1.78) 안에 갇히는가, (c) 뺨돌 상단이 NorthWall 마루 아래인가.
    ck = next(r for r in P["slopes"] if r[0] == "StairCheekN")
    _, ck_z0, _ck_drop, ck_y0, ck_y1, _ck_th, _ = ck
    hz = float(cp["thick"]) / 2.0
    worst_dz, ymax_c = -9.9, -9.9
    for c in COURSES:
        for s in c["slabs"]:
            if s["y1"] < float(cp["y1"]) - 1e-9:
                continue
            hy = (s["y1"] - s["y0"]) / 2.0
            hx = (s["xb_f"] - s["xback"]) / 2.0
            corner = (s["top"] + abs(hy * math.sin(math.radians(s["roll"]))))
            worst_dz = max(worst_dz, corner - path_z(s["xb_f"]))
            ymax_c = max(ymax_c, (s["y0"] + s["y1"]) / 2.0
                         + abs(hx * math.sin(math.radians(s["yaw"])))
                         + abs(hy * math.cos(math.radians(s["yaw"]))))
    nw = next(r for r in P["slopes"] if r[0] == "NorthWall")
    crest_min = min(nw[1] - nw[2] * (x / STAIR_RUN) - (path_z(x) + ck_z0)
                    for x in (0.0, STAIR_RUN))
    print(f"  [GT-126 뺨돌] 면 y={ck_y0:.2f} (디딤판 끝 {cp['y1']:.2f} 대비 "
          f"{cp['y1'] - ck_y0:.2f} m 매입) · 상단 코드+{ck_z0:.2f}")
    print(f"    (a) 플랭크 모서리 최고 코드+{worst_dz:.3f} → 여유 "
          f"{ck_z0 - worst_dz:+.3f} m "
          f"{'OK' if ck_z0 - worst_dz > 0.0 else 'FAIL(디딤판 관통)'}")
    print(f"    (b) yaw 북측 모서리 y 최대 {ymax_c:.4f} ≤ {ck_y1:.2f} → "
          f"{'OK' if ymax_c <= ck_y1 else 'FAIL(벽면 재관통)'}")
    print(f"    (c) NorthWall 마루 대비 최소 여유 {crest_min:+.2f} m → "
          f"{'OK' if crest_min > 0.0 else 'FAIL(마루 돌출)'} · "
          f"디딤판·낙차연부·판정카메라 무수정 (probe diff 별도)")

    for x in (0.0, 3.0, 6.0, 9.0, 12.2):
        print(f"    x={x:5.1f}: 회랑 {path_z(x):+6.3f} / 남측테라스 "
              f"{path_z(x) - SIDE_DROP:+6.3f} (낙차 {SIDE_DROP:.2f}) / "
              f"북측사면 {bank_z(x):+6.3f} / 담 상단 {bank_z(x) + 0.75:+6.3f}")
    print("    남측 낙차는 y=−1.7 에서 플레이트가 갈라짐 → 공동 위 연속 평면 "
          "없음 (체크리스트 ③ OK)")

    # ── grid camera vs geometry collision check ──
    print("\n  [검산] 그리드 카메라(−d, 0, h) vs 기하 AABB")
    obs = _grid_obstacles()
    hit_any = False
    for d in (2, 5, 10):
        for h in (0.3, 0.9, 1.8):
            ex, ey, ez = -float(d), 0.0, float(h)
            hits = [nm for nm, x0, x1, y0, y1, z0, z1 in obs
                    if x0 <= ex <= x1 and y0 <= ey <= y1 and z0 <= ez <= z1]
            if hits:
                hit_any = True
                print(f"    d{d} h{h}: ⚠ {hits}")
    print(f"    충돌 = {hit_any} (False 여야 함)  · 카메라 접지면 z=0 "
          "(Courtyard x −24..0, y −1.7..44) 내부 OK")

    # ── mise-en-scene camera coordinates ──
    print("\n  [카메라] 미장센")
    v = build_views()
    for vn in ("temple_walk", "stone_rhythm", "gate_frame", "side_slope",
               "grazing_edge"):
        vv = v[vn]
        print(f"    {vn:<14} eye={['%.2f' % e for e in vv['eye']]} "
              f"tgt={['%.2f' % t for t in vv['tgt']]}")
    print("=" * 72)


# ===========================================================================
# [H] main
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. h0.3 그리드      — 배석 너머 사면이 평지로 접히고 남측 낙차가 소실되나
 2. stone_rhythm     — 돌 간 간격·답차 불균일(디딤 리듬 파괴)이 읽히나
 3. grazing_edge     — 회랑면과 하부 테라스가 한 장 지면으로 이어져 보이나
 4. side_slope       — 무방호 1.8 m 석축 낙차 단면이 명확한가
 5. gate_frame       — 일주문·석등·석축담·법당이 '산사'로 판독되나
 6. 낙엽 밴드        — 돌 에지를 물고 덮어 단코 절단선을 지우나
 7. 접지             — 배석 매입(≥0.10)·석등·기둥에 부유·틈이 없나
 8. 지평 폐쇄        — 근경 능선 3분절 + 마루 숲 밴드가 검은 벽 없이 닫히나
10. [v6] 배석 재질   — 인접 돌의 결·색이 어긋나 '연속 줄눈 판석'이 사라졌나
11. [v6] 낙엽 밴드   — 사면에 밀착(하류단 부유·검은 사각 구멍 소멸)했나
12. [v6] 석등        — 굴뚝이 아니라 화사석·옥개석 갖춘 석등으로 읽히나
 9. cue 토글         — railing/tactile/nosing ON/OFF 시 위험 기하 불변인가"""


def main():
    # [GT-89] SMOKE gate - early exit BEFORE the Isaac boot (no GPU, no GUI).
    # The old template read NEGOBS_SMOKE only as boot()'s headless arg (or not at
    # all), so the §2.2 smoke floor booted Isaac on this scene (scene03/09 incident).
    # Deep checks keep their own arms (NEGOBS_SELFCHECK / geom_invariance_check.py).
    if os.environ.get("NEGOBS_SMOKE", "0") == "1":
        print("SMOKE_OK %s pre-boot gate (GT-89)" % os.path.basename(__file__))
        return
    smoke = os.environ.get("NEGOBS_SMOKE", "0") == "1"
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    if smoke:
        _smoke_report()
        return

    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])
    simulation_app = sc.boot(capture_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from omni.kit.viewport.utility import (get_active_viewport,
                                           capture_viewport_to_file)
    from isaacsim.core.utils.viewports import set_camera_view
    from pxr import UsdGeom

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.Xform.Define(stage, "/World/Scene07")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene07"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl, rotY=rotY,
                               collider=col)

    # -------------------------------------------------------------------
    # materials
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]

        def tex(role, path, scale, **kw):
            return sc.make_pbr(stage, path, sc.tex_path(role, "diff"),
                               sc.tex_path(role, "nor"),
                               sc.tex_path(role, "rough"), scale, **kw)

        def tex_xform(mtl, translate=None, rotate=None):
            """[v6] World-projection UV offset·rotation. Under the `scene_common` no-edit rule,
            inputs are added scene-locally to the OmniPBR shader that make_pbr created
            (texture_translate/texture_rotate of OmniPBR.mdl — effective when project_uvw=True).
            The grain of adjacent stones disagrees and the 'continuous joints' disappear."""
            from pxr import UsdShade, Sdf, Gf
            sh = UsdShade.Shader(
                stage.GetPrimAtPath(mtl.GetPath().AppendChild("Shader")))
            if translate is not None:
                sh.CreateInput("texture_translate",
                               Sdf.ValueTypeNames.Float2).Set(
                    Gf.Vec2f(float(translate[0]), float(translate[1])))
            if rotate is not None:
                sh.CreateInput("texture_rotate",
                               Sdf.ValueTypeNames.Float).Set(float(rotate))
            return mtl

        M = {}
        # [v6] The old M["stone"] (stone_worn = masonry joints) is **dropped** - the stones now
        #      draw from the rock_face pool below (the cause behind ruling §2 (5) 'brick-jointed slabs').
        # [v6] lanterns·plinths = jointless granite tone (old stone_cap = masonry texture -> chimney)
        M["stone_cap"] = tex("granite_dark", "/World/Looks/StoneCap",
                             sca["granite"], tint=mp["granite_tint"])
        # [GT-126] Masonry de-repetition: `unit_cell` = one cell per texture period
        #   (cell == scale, origin 0, σ/악센트 = T1 §1.8-3 defaults). Adjacent repeats
        #   of the block motif get different log-normal albedo gains, so the 4.6 m
        #   period stops reading as wallpaper; the stone class's own patch rotation
        #   (patch 1.0 @ 4 m) and macro band (0.12 @ 0.55 m, GT-108) stay untouched.
        #   NB the MDL quantises **world XY** (`NegObsGround.mdl` `float2(pw_w.x,
        #   pw_w.y)`), so on these x-running wall faces the cells land as 4.6 m
        #   construction-section bands — the real 석축 구간 이음 tonal break. A
        #   sub-metre cell here would column-stripe a vertical face (the plan grid
        #   degenerates on walls); do not shrink it until the MDL projects the cell
        #   on the dominant plane. GT-113 W3 (scene21 marble) is the wiring precedent;
        #   the value is authored at creation because no ground_kit ledger covers the
        #   wall family — the LOOK_MTL=0 arm ignores the kwarg (byte-identical).
        M["rock"] = tex("rock_wall", "/World/Looks/Rock", sca["rock_wall"],
                        unit_cell=(sca["rock_wall"], (0.0, 0.0)))
        M["leaf"] = tex("leaf_ground", "/World/Looks/Leaf",
                        sca["leaf_ground"], tint=mp["leaf_tint"])
        M["gravel"] = tex("gravel", "/World/Looks/Gravel", sca["gravel"],
                          tint=mp["gravel_tint"])
        M["grass"] = tex("grass", "/World/Looks/Grass", sca["grass"],
                         tint=mp["grass_tint"])
        M["wood"] = sc.make_pbr(stage, "/World/Looks/Wood",
                                diffuse_color=mp["wood_color"],
                                roughness_const=mp["wood_rough"])
        M["roof"] = sc.make_pbr(stage, "/World/Looks/Roof",
                                diffuse_color=mp["roof_color"],
                                roughness_const=0.9, specular_level=0.0)
        M["canopy_a"] = sc.make_pbr(stage, "/World/Looks/CanopyA",
                                    diffuse_color=mp["canopy_a"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        M["canopy_b"] = sc.make_pbr(stage, "/World/Looks/CanopyB",
                                    diffuse_color=mp["canopy_b"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        M["shrub"] = sc.make_pbr(stage, "/World/Looks/Shrub",
                                 diffuse_color=mp["shrub"],
                                 roughness_const=mp["shrub_rough"],
                                 specular_level=0.0)
        M["rail"] = sc.make_pbr(stage, "/World/Looks/Rail",
                                diffuse_color=mp["rail_color"],
                                metallic=mp["rail_metallic"],
                                roughness_const=mp["rail_rough"])
        # [W2-D ground_kit] tone-only materials for the kit's ground elements.
        #   Sec.4.4 hands colour to T1, but a wear lane and a moss band *are*
        #   tone by definition - bound to the plain courtyard gravel they would
        #   render a zero-contrast null (the scene15 pilot measured exactly
        #   that for patches). Both are tints of the gravel texture already in
        #   use, so no new asset and no new texture role is introduced.
        M["gk_wear"] = tex("gravel", "/World/Looks/GkWear", sca["gravel"],
                           tint=tuple(c * 0.85 for c in mp["gravel_tint"]))
        # [W2 fix batch F2] Scatter pool override. Bound over each scattered rock
        #   with `strongerThanDescendants`, so the procured asset's own basecolor
        #   (linear 0.23) is replaced by a real gravel texture dulled to 0.19 -
        #   the middle of the "grey debris 0.18~0.30" convention.
        M["gk_rock"] = tex("gravel", "/World/Looks/GkRock", 0.30,
                           tint=(0.82, 0.81, 0.79))
        M["gk_moss"] = tex("gravel", "/World/Looks/GkMoss", sca["gravel"],
                           tint=PARAMS["stone_mtl"]["tint_moss"])
        # [GT-126] Distant ridge + crest: constant colour → textured, same mean.
        #   The audit read the ridge walls as "세로 줄무늬가 들어간 상수색 녹색 벽 =
        #   무대 배경막". Two causes, two cures, no new asset:
        #   · constant colour — replaced by `rock_face` (already in the tree) world-
        #     projected at 22/30/40 m (ridges) and 6 m (crest crowns), so the mottle
        #     reads as soil/rock tonal bands on a far hillside, not a flat card.
        #   · striping — [measured, headless make_pbr probe] the old names
        #     (`Ridge_near`…) matched no exact/strip key and fell through to the
        #     **concrete** catch-all, whose `_W_STRUCT` weathering puts `streak
        #     0.12` = run-down streaks on vertical faces — a 15~29 m face of
        #     nothing but streak IS the audited "세로 줄무늬". The new
        #     `Ridge_{i}`/`Crest_{i}` names strip to the `Ridge`/`Crest` table keys
        #     → soil class → no streak, NegObsGround normal-weighted triplanar
        #     (the B2 cure), so nothing can smear or streak a vertical face.
        #   Tint = target / texture linear mean (per channel, `sc._texture_mean`), so
        #   the effective albedo equals `ridge_*`/`crest_*` exactly and the v6/v7
        #   luminance-preservation contract (SMOKE [v6 태양] table) still holds.
        #   Multiplier spread max 2.4 — inside the F1 blue-noise cap of 3.0
        #   [computed: rock_face linear mean (0.159, 0.118, 0.083)]. If PIL is
        #   unavailable the mean is None and the old constants build verbatim.
        _rf_mean = sc._texture_mean(sc.tex_path("rock_face", "diff"))

        def _backdrop_mtl(path, target, scale, rough):
            if _rf_mean:
                tint = tuple(t / max(m, 1e-4)
                             for t, m in zip(target, _rf_mean))
                return tex("rock_face", path, scale, tint=tint,
                           specular_level=0.0)
            return sc.make_pbr(stage, path, diffuse_color=target,
                               roughness_const=rough, specular_level=0.0)

        for i, tone in enumerate(("near", "mid", "far")):
            M[f"ridge_{tone}"] = _backdrop_mtl(
                f"/World/Looks/Ridge_{i}", mp[f"ridge_{tone}"],
                mp["ridge_tex_scale"][i], 0.95)
        for i, tone in enumerate(("near", "far")):
            M[f"crest_{tone}"] = _backdrop_mtl(
                f"/World/Looks/Crest_{i}", mp[f"crest_{tone}"],
                mp["crest_tex_scale"], 1.0)
        # [W3 S3-6 · GT-17] Summer forest floor. `dirt_park` is already in the tree and already
        #   tuned for this scene family; darkened and cooled it reads as damp mountain soil
        #   under a closed canopy, which is what G7's between-stone ground is.
        M["forest"] = tex("dirt_park", "/World/Looks/Forest",
                          sca["dirt_park"], tint=mp["forest_tint"])
        # [W3 S3-6] The first real moss material in this scene. Source: `sc.TEX["moss"]`
        #   (Poly Haven `rock_moss_set_02`, **CC0**, registered by the K4 micro-commit).
        #   **`nor` is dropped on purpose**: that role ships a Poly Haven `_nor_gl` **EXR**,
        #   i.e. OpenGL green, while every other map in this registry is DX. The K4 note gives
        #   the consumer two choices — flip green or drop `nor` — and dropping it is the one
        #   that cannot silently invert the lighting on a judged surface.
        # [W3 S3-7] Crest-cluster tile roof. The **geometry** stays procedural (gap G1) — this
        #   only replaces the flat `roof_color` constant with the real 기와 map from the
        #   shared texture pool. T2, local use only, never redistributed.
        _shared = os.path.join(sc.ASSETS_DIR, "urban", "nv_content",
                               "common_assets", "shared_textures")
        _tile_a = os.path.join(_shared, "tile_roof_01_a.png")
        _tile_n = os.path.join(_shared, "tile_roof_01_n.png")
        if os.path.isfile(_tile_a):
            M["tile"] = sc.make_pbr(stage, "/World/Looks/TileRoof", _tile_a,
                                    _tile_n if os.path.isfile(_tile_n) else None,
                                    None, 1.6, tint=mp["tile_tint"],
                                    roughness_const=0.86, specular_level=0.0)
        else:
            M["tile"] = M["roof"]
        # 단청 red wall fragment + the E7-10 timber pole (CC0 pier-pole maps).
        M["red"] = sc.make_pbr(stage, "/World/Looks/DancheongRed",
                               diffuse_color=PARAMS["eave"]["red"],
                               roughness_const=0.82, specular_level=0.0)
        _pier = os.path.join(sc.ASSETS_DIR, "urban_cc0", "modular_wooden_pier",
                             "textures")
        _pd = os.path.join(_pier, "modular_wooden_pier_poles_diff_1k.png")
        _pr = os.path.join(_pier, "modular_wooden_pier_poles_rough_1k.png")
        M["pole"] = (sc.make_pbr(stage, "/World/Looks/Pole", _pd, None, _pr,
                                 1.1, tint=(0.72, 0.68, 0.62))
                     if os.path.isfile(_pd) else M["wood"])
        M["moss"] = sc.make_pbr(stage, "/World/Looks/Moss",
                                sc.tex_path("moss", "diff"), None,
                                sc.tex_path("moss", "rough"),
                                sca["moss"], tint=mp["moss_tint"],
                                bump=1.2)
        # [v6 -> W3 S3-6] stepping-stone material pool. Was 8 variants with a blind
        #   `moss_every = 3`; now **three tiers** so the selection can read the zone
        #   (§4.1-3): dry = the walked centre band, mid = the tread outer band, moss = the
        #   riser bodies, the joints and the boulder tops. The `rock_face` jointless base,
        #   the per-variant world-UV offset and the bump are unchanged — that machinery is
        #   what cured the v6 "brick-jointed slabs" defect and is not in scope here.
        smp = PARAMS["stone_mtl"]
        rng = random.Random(int(smp["seed"]))
        jt = float(smp["tint_jit"])
        M["stone_pool"] = []
        for tier, base in (("dry", smp["tint_dry"]),
                           ("mid", smp["tint_mid"]),
                           ("moss", smp["tint_moss"])):
            lst = []
            for k in range(int(smp[f"n_{tier}"])):
                tint = tuple(max(0.0, c * (1.0 + rng.uniform(-jt, jt)))
                             for c in base)
                m = tex("rock_face", f"/World/Looks/StoneNat_{tier}{k}",
                        rng.uniform(*smp["scale"]), tint=tint,
                        bump=float(smp["bump"]))
                tex_xform(m, translate=(rng.uniform(-4.0, 4.0),
                                        rng.uniform(-4.0, 4.0)),
                          rotate=rng.uniform(0.0, 360.0))
                lst.append(m)
                M["stone_pool"].append(m)
            M[f"stone_{tier}"] = lst
        # [pilot fix] `M["moss"]` is deliberately **NOT** appended to the slab tier. K4's
        #   caution 1 is exact: `rock_moss_set_02` is a 1k scan of an 8 m rock group, so at a
        #   slab-sized world projection it repeats into a hard-edged green camouflage
        #   patchwork — which is what the first pilot's `stone_rhythm` showed. The scan stays
        #   on the **boulders** (large, singular, its native subject) at a 2.40 m projection;
        #   the slab moss tier is the tinted `rock_face` variants, i.e. the repo's existing
        #   green-tint-on-stone convention (spec §3.0 C-A2).
        # [v5 shared layer] Korean sign panel - uv_mode=True (mesh st matched 1:1)
        M["sign_info"] = sc.make_pbr(
            stage, "/World/Looks/SignInfo",
            sc.tex_path("sign_info", "diff"), None, None, 1.0,
            roughness_const=0.55, uv_mode=True)
        M["sign_back"] = sc.make_pbr(stage, "/World/Looks/SignBack",
                                     diffuse_color=mp["sign_back"],
                                     roughness_const=0.7)
        # yard material toggle (cue_material_break=False -> the stones take the decomposed-granite tone too)
        #   [v6] The stones draw from the material pool. With the toggle OFF they all share one decomposed-granite material.
        if not cfg["cue_material_break"]:
            M["stone_pool"] = [M["gravel"]]
        return M

    # -------------------------------------------------------------------
    # terrain : axis-aligned plate table + slope plate table
    # -------------------------------------------------------------------
    def build_terrain(M):
        # [W2-0 P-A] The courtyard plate is what ground_kit decorates, so its
        #   displacement skin must be off *before* the box is created - the
        #   skin top sits at +6.5..16.5 mm and would bury every 0.6 mm decal
        #   (spec Sec.1.1). Registration is prefix-matched.
        sc.skin_exclude(f"{ROOT}/Plate_Courtyard")
        for nm, x0, x1, y0, y1, zt, th, mk in PARAMS["plates"]:
            BOX(f"{ROOT}/Plate_{nm}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, zt - th / 2.0),
                (x1 - x0, y1 - y0, th), M[mk], col=True)
        # [S3-4 · GT-14] `PathCorridor` and `SouthScarp` are the two slope plates the stair
        #   beds into, and they drop by `corridor_bed`. A course tread is LEVEL, so its back
        #   edge sits up to one rise below the 19.0 deg plane; leaving the plate on the plane
        #   would push it up through the back of every tread. `path_z()` — the datum every
        #   other plate, the dressing and `ground_z()` read — is untouched.
        bed = float(PARAMS["courses"]["corridor_bed"])
        for nm, z0, drop, y0, y1, th, mk in PARAMS["slopes"]:
            dz = bed if nm in ("PathCorridor", "SouthScarp") else 0.0
            sc.build_slope(stage, f"{ROOT}/Slope_{nm}", 0.0, z0 - dz,
                           STAIR_RUN, drop, y0, y1, th + dz, M[mk],
                           margin=0.0, collider=True)

    def build_flat_fill(M):
        """hazard_stairs=False control : stones·slope·south drop flattened to z=0."""
        BOX(f"{ROOT}/FlatFill", (22.0, 5.0, -0.5), (136.0, 78.0, 1.0),
            M["gravel"], col=True)

    # -------------------------------------------------------------------
    # 자연석 계단 : 28 courses of 2-4 bedded slabs (scene-local generator, §4.1-1 route (ii))
    # -------------------------------------------------------------------
    def build_stones(M):
        """[S3-4 · GT-14] Courses, 속채움 bed, 고임돌/틈메우기돌 shims, 돌깔기 aprons.

        `sc.build_worn_stone_stairs` is the shared archetype builder and it was weighed:
        it gives lateral blocks, `jyaw`, `jz` and a solid base for one call, but it has
        **no back-overlap term** — each block spans `xa + U(-jt/2, jt/2) .. xb + U(...)`,
        so a course's back edge can stand up to `jt` behind the course above and A2 comes
        back in miniature. Adding an `ov=` kwarg is a `scene_common` edit, i.e. K4's, not
        S3's (spec §H15). Spec §4.1-1 route **(ii)** — keep the scene-local generator and
        rewrite it as courses — is the recommended one and is what this is.
        """
        cp = PARAMS["courses"]
        mz = PARAMS["moss_zone"]
        thick = float(cp["thick"])
        cap_t = float(mz["cap_t"])
        body_t = thick - cap_t

        def pick(tier, key):
            lst = M[f"stone_{tier}"]
            return lst[key % len(lst)]

        for c in COURSES:
            i = c["i"]
            b = c["bed"]
            # 속채움 core: one slab per course, 60 mm under the tread, so a lateral joint
            #   bottoms out on stone. 표준시방서 0400-3.2 ㄹ "내부는 속채움한다".
            #   Zone "joint" = moss 1.00 (§4.1-3): it is only ever seen through the joints.
            BOX(f"{ROOT}/CourseBed_{i}",
                ((b["x0"] + b["x1"]) / 2.0, (b["y0"] + b["y1"]) / 2.0,
                 b["top"] - b["thick"] / 2.0),
                (b["x1"] - b["x0"], b["y1"] - b["y0"], b["thick"]),
                # zone "joint" = moss 1.00, and this is `TEX["moss"]`'s one correct home:
                #   a flat horizontal face seen through a 0-60 mm joint, where a
                #   world-projected rock-with-moss scan reads as damp mottled fill.
                M["moss"] if (i % 2 == 0) else pick("moss", i), col=True)
            for s in c["slabs"]:
                dx = s["xb_f"] - s["xback"]
                dy = s["y1"] - s["y0"]
                cx0 = (s["xback"] + s["xb_f"]) / 2.0
                cy0 = (s["y0"] + s["y1"]) / 2.0
                th = math.radians(s["yaw"])
                ra = math.radians(s["roll"])
                # cap = the walked top face; body = the rest, and the body's front face IS the
                #   riser. Splitting the slab is the only way to give a tread and its own riser
                #   different moss without authoring a proud strip along the nosing — and a
                #   proud strip along the nosing is exactly what H2 / RF-5 forbid here.
                #   The body centre is the cap centre displaced by (0, 0, -h) **in the slab's
                #   own frame**, so the offset is rotated by the same rotX then rotZ that
                #   `_oriented_box` applies (op order translate -> rotZ -> rotX -> scale).
                #   Displacing it in world z instead would slide the body sideways by
                #   h*sin(roll) — up to 5.5 mm — and open a ledge under the cap.
                h = (cap_t + body_t) / 2.0
                ox = -h * math.sin(ra) * math.sin(th)
                oy = h * math.sin(ra) * math.cos(th)
                oz = -h * math.cos(ra)
                cap_tier = ("moss" if s["cap_moss"]
                            else ("dry" if s["walk"] else "mid"))
                sc._oriented_box(
                    stage, f"{ROOT}/Course_{i}_{s['k']}",
                    (cx0, cy0, s["top"] - cap_t / 2.0), (dx, dy, cap_t),
                    pick(cap_tier, i * 5 + s["k"] * 3), collider=True,
                    rotz=s["yaw"], rotx=s["roll"])
                sc._oriented_box(
                    stage, f"{ROOT}/CourseBody_{i}_{s['k']}",
                    (cx0 + ox, cy0 + oy, s["top"] - cap_t / 2.0 + oz),
                    (dx, dy, body_t),
                    pick("moss" if s["body_moss"] else "mid",
                         i * 7 + s["k"] * 2), collider=False,
                    rotz=s["yaw"], rotx=s["roll"])
        mf = moss_fractions()
        print(f"[S3-4] scene07 자연석 계단 {len(COURSES)}코스 · 판 "
              f"{sum(len(c['slabs']) for c in COURSES)} · 속채움 "
              f"{len(COURSES)} · 개방사면 0 % · 이끼 보행대 "
              f"{mf['walk']*100:.0f}% / 답면외측 {mf['tread_outer']*100:.0f}% / "
              f"챌면 {mf['riser']*100:.0f}% / 줄눈 100%")

    def build_stone_dressing(M):
        """고임돌/틈메우기돌 shims at every riser foot + the 돌깔기 aprons (KFS-TRAIL p.72)."""
        cp = PARAMS["courses"]
        b0, b1 = (float(v) for v in cp["shim_band"])
        n_shim = 0
        for c in COURSES[:-1]:
            xf = min(s["xb_f"] for s in c["slabs"])
            below = COURSES[c["i"] + 1]["top"]
            n_shim += int(sc.scatter_debris(
                stage, f"{ROOT}/JointShim_{c['i']}",
                xf + b0, float(cp["y0"]) + 0.05, xf + b1,
                float(cp["y1"]) - 0.05, below,
                cover=float(cp["shim_cover"]), pool=sc.VEG_ROCKS,
                seed=gk.det_seed("s07.shim", str(c["i"]), 0),
                max_count=int(cp["shim_n"]), scale_jitter=(0.6, 1.1),
                sink=0.03, mtl=M["gk_rock"]) or 0)
        # 돌깔기 aprons — 자연석 판석 T100, 6 mm proud so they are a material change and
        #   not a step (the exit step is measured to the road plate, GT-14).
        rng = random.Random(int(cp["apron_seed"]))
        hy = float(cp["apron_half_y"])
        pr = float(cp["apron_proud"])
        at = float(cp["apron_t"])
        # [pilot fix] The first pilot laid these as a 3-cell grid of 0.60 x 0.93 m boxes and
        #   they read as **cast concrete paving** across the near field of `h0.3_d2` — the one
        #   thing a temple approach must not have. 자연석 판석 is riven, irregular and laid to
        #   an irregular joint (§4.1-1b), so the field is now 4 x 4 with per-flag size jitter,
        #   +-6 deg yaw and a drawn joint, and it draws from the mid/moss stone tiers rather
        #   than from a pale variant.
        for tag, x0, x1, ztop in (
                ("Lo", float(cp["x1"]), float(cp["x1"]) + float(cp["apron_lo"]),
                 -STAIR_DROP + pr),
                ("Up", -float(cp["apron_up"]), float(cp["x0"]) - 0.02, pr)):
            nx = max(2, int(round((x1 - x0) / 0.34)))
            ny = 4
            for a in range(nx):
                for c2 in range(ny):
                    fx0 = x0 + (x1 - x0) * a / nx
                    fx1 = x0 + (x1 - x0) * (a + 1) / nx
                    fy0 = -hy + 2.0 * hy * c2 / ny
                    fy1 = -hy + 2.0 * hy * (c2 + 1) / ny
                    jx = rng.uniform(0.04, 0.11)
                    jy = rng.uniform(0.04, 0.13)
                    tier = "moss" if rng.random() < 0.35 else "mid"
                    sc._oriented_box(
                        stage, f"{ROOT}/Apron{tag}_{a}_{c2}",
                        ((fx0 + fx1) / 2.0 + rng.uniform(-0.02, 0.02),
                         (fy0 + fy1) / 2.0 + rng.uniform(-0.03, 0.03),
                         ztop - at / 2.0),
                        (max(0.16, fx1 - fx0 - jx),
                         max(0.20, fy1 - fy0 - jy), at),
                        M[f"stone_{tier}"][(a * 3 + c2)
                                           % len(M[f"stone_{tier}"])],
                        collider=True, rotz=rng.uniform(-6.0, 6.0))
        print(f"[S3-4] 고임돌·틈메우기돌 {n_shim} 인스턴스 · 돌깔기 에이프런 "
              f"하단 {cp['apron_lo']:.2f} m / 상단 {cp['apron_up']:.2f} m")

    def build_kerb(M):
        """[S3-5 · GT-15] 야면석 kerb boulders on both corridor shoulders.

        Asset route (spec §1.1 / §3.2). `urban_kit` is imported lazily and the whole block
        degrades to a procedural boulder if the loader or the row is unavailable — the T2
        `assets/urban/` tree is gitignored, so a clone without it must still build a scene.
        """
        kp = PARAMS["kerb"]
        uk = None
        try:
            import urban_kit as _uk
            uk = _uk
            for a in kp["pool"]:                 # manifest-drift guard, see PARAMS
                s = uk.spec(a[0])
                for j, want in enumerate((a[1], a[2], a[3])):
                    got = float(s.size_m[j])
                    if abs(got - float(want)) > 0.002:
                        raise ValueError(
                            f"kerb pool {a[0]} size drift: PARAMS {want} vs manifest {got}")
        except Exception as e:
            print(f"[S3-5][경고] urban_kit 야면석 경로 불가 ({e}) — 절차적 폴백")
            uk = None
        n_asset = 0
        for b in KERB:
            path = f"{ROOT}/Kerb_{b['name']}"
            if uk is not None:
                try:
                    uk.add_urban_asset(
                        stage, path, b["asset"],
                        pos_m=(b["cx"], b["cy"], b["seat_z"]),
                        yaw_deg=b["yaw"], scale_mul=b["scale"],
                        tilt_deg=b["tilt"], z_mode="base", scene="07",
                        instanceable=False)
                    n_asset += 1
                    # [S3-5 pilot fix] **Two things are happening here and both are load-bearing.**
                    #   (a) The moss zone: boulder tops carry 0.70-0.90 moss (§4.1-3), so a
                    #       drawn subset takes `M["moss"]` and the rest a `rock_face` stone
                    #       tier. Every boulder is bound — see (b).
                    #   (b) **scene07 is the first scene in the tree that actually loads an
                    #       urban asset** (spec §3.0: "the only call site in the tree is
                    #       `batch1_common.py:185`", and it is unreached). The first pilot
                    #       round found out what that costs: `assets/urban/nv_core/materials/
                    #       SimPBR.mdl` fails to compile — "could not find module
                    #       `.::baking_annotations`" — so every rock arrived with an invalid
                    #       material and rendered as **flat bright red** in `h0.3_d2`,
                    #       `temple_walk` and `side_slope`. `instanceable=True` made it
                    #       unfixable from the scene: the broken binding lives inside
                    #       `/__Prototype_N/...`, and an ancestor `strongerThanDescendants`
                    #       binding does not reach into an instance prototype. With
                    #       `instanceable=False` the referenced prims are real descendants and
                    #       the ancestor binding wins. Cost is ~30 x 3-10 k unique triangles,
                    #       which §12-14 explicitly does not budget on. The MDL search-path
                    #       defect itself belongs to whoever owns `assets/urban` — it is
                    #       recorded in the report, not worked around anywhere else.
                    try:
                        from pxr import UsdShade
                        UsdShade.MaterialBindingAPI.Apply(
                            stage.GetPrimAtPath(path)).Bind(
                            # [pilot fix 2] the boulders take the **tinted-stone** moss
                            #   convention, not the raw scan: `make_pbr` projects in world
                            #   space, so on a rounded 0.4-0.9 m boulder `rock_moss_set_02`
                            #   smears into a wet-plastic sheet at any projection scale that
                            #   was tried. The raw scan keeps exactly the one job K4's note
                            #   says it is right for — the flat 속채움 bed seen through the
                            #   joints, below.
                            M["stone_moss"][b["name"].__hash__()
                                            % len(M["stone_moss"])] if b["moss"]
                            else M["stone_mid"][b["cx"].__hash__()
                                                % len(M["stone_mid"])],
                            UsdShade.Tokens.strongerThanDescendants)
                    except Exception as e:
                        print(f"[S3-5][경고] {b['name']} 재질 바인딩 실패: {e}")
                    continue
                except Exception as e:
                    print(f"[S3-5][경고] {b['name']} {b['asset']}: {e} — 폴백")
            # fallback: a flattened ellipsoid at the same footprint, moss-tinted
            sc.add_sphere(stage, path,
                          (b["cx"], b["cy"], b["seat_z"] + b["proud"] * 0.42),
                          (b["across"] / 2.0, b["across"] / 2.4,
                           b["proud"] * 0.85), M["gk_moss"])
        print(f"[S3-5] 야면석 연석 {len(KERB)}괴 (에셋 {n_asset} · 남 "
              f"{sum(1 for b in KERB if b['flank'] == 'S')} / 북 "
              f"{sum(1 for b in KERB if b['flank'] == 'N')})")

    def build_ferns(M):
        """[S3-5 · GT-15] Fern-band stand-in on both margins + the two framing trunks."""
        fp = PARAMS["ferns"]
        rng = random.Random(int(fp["seed"]))
        rel = "Shrub/Switchgrass.usd"
        use_asset = sc.LOOK_GEO and sc.veg_available()
        n_f = 0
        for side in ("north", "south"):
            b = fp[side]
            for i in range(int(b["n"])):
                fx = rng.uniform(*b["x"])
                fy = rng.uniform(*b["y"])
                th = rng.uniform(*fp["target_h"])
                gz = _zone_z(fx, fy, side)
                path = f"{ROOT}/Fern_{side[0].upper()}{i}"
                if use_asset:
                    vx = sc.add_vegetation(stage, path, rel, (fx, fy, gz),
                                           yaw_deg=rng.uniform(0.0, 360.0),
                                           target_h=th, native_h=1.37)
                    if vx is not None:
                        try:
                            stage.GetPrimAtPath(path + "/Asset") \
                                .SetInstanceable(True)
                        except Exception:
                            pass
                        n_f += 1
                        continue
                # blob fallback keeps the margin populated on the GEO=0 arm
                sc.add_sphere(stage, path, (fx, fy, gz + th * 0.42),
                              (th * 0.62, th * 0.58, th * 0.50), M["shrub"])
        # Framing trunks. **Not** `build_tree`: that draws its species from a coordinate hash
        #   over `VEG_TREES`, and at these two coordinates it draws `Yellow_Pine`, which is a
        #   LINT-4b **retired** species (rules `retired: [White_Pine, Yellow_Pine]`) — measured,
        #   not guessed. The K4(b) `species=` kwarg does not exist yet, so the species is
        #   pinned the way `build_tree`'s own docstring says to ("...or must call
        #   `add_vegetation` itself"): `Shumard_Oak`, PASS, green/olive 100 %, and §3.2's named
        #   canopy-tunnel primary for this scene. `native_h` is the asset's **zmax**, per the
        #   §3.2 caution — the bbox height would scale it wrong.
        fr = PARAMS["frame_tree_veg"]
        tr = PARAMS["tree"]
        for t in PARAMS["frame_trees"]:
            gz = _zone_z(t["cx"], t["cy"], t["zone"])
            path = f"{ROOT}/FrameTree_{t['name']}"
            done = False
            if use_asset:
                vx = sc.add_vegetation(
                    stage, f"{path}/Veg", fr["rel"], (t["cx"], t["cy"], gz),
                    yaw_deg=rng.uniform(0.0, 360.0),
                    target_h=float(t["trunk_h"]) * 1.60,
                    native_h=float(fr["native_h"]))
                if vx is not None:
                    try:
                        stage.GetPrimAtPath(f"{path}/Veg/Asset") \
                            .SetInstanceable(True)
                    except Exception:
                        pass
                    done = True
            if not done:
                sc.build_tree(stage, path, t["cx"], t["cy"], gz, M["wood"],
                              M["canopy_a"], M["canopy_b"],
                              trunk_r=float(t.get("trunk_r", tr["trunk_r"])),
                              trunk_h=float(t["trunk_h"]), stake_r=0.004,
                              stake_h=0.02, stake_off=0.2)
        print(f"[S3-5] 고사리대 스탠드인 {n_f}주(Switchgrass, G2 대체) · "
              f"프레이밍 노거수 {len(PARAMS['frame_trees'])}주")

    def build_leaf_masks(M):
        # [W3 F3 / DEC-2] leaf carpets - one irregular mask per drift, no rectangles.
        #   The corridor masks take `z_fn=path_z`, so every vertex sits on the 19 deg
        #   corridor plane and the "floating / buried end" the v6 slope slabs were built to
        #   cure cannot come back. The yard masks are flat (the yard is flat by practice -
        #   material variation, not curvature, breaks its monotony).
        lb = PARAMS["leaf_band"]
        yl = PARAMS["yard_leaf"]
        kit = gk.kit_from_scene_common(sc, stage)
        # Feather-ring clip boxes. A leaf card that lands off its host plate sits at the
        #   mask's own z over different ground and floats: the corridor cards must stay
        #   inside the PathCorridor slope (|y| <= 1.70, x 0..STAIR_RUN) and the yard cards
        #   inside the Courtyard plate (x −24..0, y >= −1.70).
        clip_cor = (0.0, -1.66, STAIR_RUN, 1.66)
        clip_yard = (-23.9, -1.66, -0.10, 12.0)
        masks = []
        for nm, cx, cy, rx, ry in LEAF_PATCHES:
            masks.append((f"LeafDrift_{nm}",
                          gk.build_carpet_mask(
                              kit, f"{ROOT}/LeafDrift_{nm}", cx, cy, rx, ry,
                              M["leaf"], z=0.0, proud=lb["proud"],
                              n=mask_n(cx), rough=0.18,
                              seed=int(lb["seed"]) + int(nm),
                              feather=lb["feather"],
                              feather_cap=int(lb["feather_cap"]),
                              feather_clip=clip_cor,
                              # [S3-4] the walked surface is the stone tops now, not the
                              #   19 deg plane. Bound to `path_z` the mask would be buried
                              #   inside the courses over most of the flight and would poke
                              #   through at the nosings. S3-6 then re-sites these lobes to
                              #   the margins, where G7 actually puts the litter.
                              z_fn=course_top),
                          course_top, 0.0))
        for n, (cx, cy, sx, sy) in enumerate(PARAMS["yard_drifts"]):
            masks.append((f"YardLeaf_{n}",
                          gk.build_carpet_mask(
                              kit, f"{ROOT}/YardLeaf_{n}", cx, cy,
                              sx / 2.0, sy / 2.0, M["leaf"],
                              z=0.0, proud=lb["proud"], n=mask_n(cx),
                              rough=0.20,
                              seed=int(yl["seed"]) + n,
                              feather=lb["feather"],
                              feather_cap=int(lb["feather_cap"]),
                              feather_clip=clip_yard),
                          (lambda x, y: 0.0), 0.0))
        # DEC-2 feather ring: individual leaf cards straddling the mask boundary, density
        #   falling to zero outward. Delegated to `scatter_debris` exactly the way
        #   `ground_kit.apply_ground` consumes `build_edge_break`'s `scatter_req`, so the
        #   asset pool stays in one place. `sct_debris_leaves_dry_*` / VEG_DEBRIS are
        #   season-scoped to the leaf scenes (C2 · 07 · 10 · D3) - PROC §6.1 - and 07 is one.
        #   **Every ring gets a two-argument `ground_fn`.** `scatter_debris` calls it as
        #   `ground_fn(px, py)` and wraps the call in `except Exception: pass`
        #   (`scene_common.py:2368-2381`), so handing it the scene's own one-argument
        #   `path_z` does not raise - it silently falls back to the flat `z` argument and
        #   lays every card at z = 0 over a corridor that descends 4.2 m. That is a real
        #   defect this pilot caught in its first render: a band of leaves hanging in mid-air
        #   across the frame. The lambda is the fix and the reason it must stay a lambda.
        # [W3 S3-6 · GT-17] `cover` is now **per host**: the corridor ring drops 0.06 -> 0.035
        #   because 07 is summer and a summer margin carries an accumulation, not a carpet
        #   (§4.1-5, "reduce `cover` to the margin density"). The pool stays `sc.VEG_DEBRIS`;
        #   the urban `sct_debris_leaves_dry_*` rows are **never placed in 07** even though
        #   `SCENE_SCOPE` permits '07' — a scope permission is not a recommendation (H10).
        nfeather = 0
        for nm, res, gfn, z0 in masks:
            cov = (lb["cover_corridor"] if nm.startswith("LeafDrift")
                   else lb["cover_yard"])
            for i, req in enumerate(res["scatter_req"]):
                rx0, ry0, rx1, ry1 = req["region"]
                nfeather += int(sc.scatter_debris(
                    stage, f"{ROOT}/{nm}_Feather_{i}",
                    rx0, ry0, rx1, ry1, z0,
                    cover=float(cov), seed=gk.det_seed("s07.feather", nm, i),
                    edge_bias=float(req["edge_bias"]),
                    max_count=int(req["count"]), ground_fn=gfn,
                    scale_jitter=(0.7, 1.15)) or 0)
        print(f"[W3 F3] scene07 낙엽 마스크 {len(masks)}매(직사각 0) · "
              f"페더 링 인스턴스 {nfeather}")

    # -------------------------------------------------------------------
    # gable roof : 2 build_slope slabs (each falling +-X from the ridge)
    # -------------------------------------------------------------------
    def gable_roof(prefix, x_ridge, z_ridge, half_run, drop, y0, y1, thick,
                   mtl, upturn=False):
        """From the ridge (x_ridge, z_ridge), **fall** by drop on each side along ±X.
        build_slope only descends toward +X, so the −X half is given a start point at the eave
        (x_ridge−half_run, z_ridge−drop) with drop=−drop (a rise).

        [W3 S3-7] `upturn=True` splits each half into a main plane plus a shallower **처마**
        segment over the last `eave.run` metres, so the eave tip finishes `eave.lift` higher
        than a straight plane would put it. The x extent of the roof is unchanged — the lift
        comes out of the drop, not out of an added overhang, so nothing new casts a shadow.
        """
        ep = PARAMS["eave"]
        run2 = float(ep["run"]) if upturn else 0.0
        if not upturn or half_run <= run2 * 1.5:
            sc.build_slope(stage, f"{prefix}/RoofP", x_ridge, z_ridge,
                           half_run, drop, y0, y1, thick, mtl, margin=0.10,
                           collider=False)
            sc.build_slope(stage, f"{prefix}/RoofN", x_ridge - half_run,
                           z_ridge - drop, half_run, -drop, y0, y1, thick,
                           mtl, margin=0.10, collider=False)
            return
        run1 = half_run - run2
        d1 = drop * run1 / half_run
        d2 = drop * run2 / half_run - float(ep["lift"])
        sc.build_slope(stage, f"{prefix}/RoofP", x_ridge, z_ridge, run1, d1,
                       y0, y1, thick, mtl, margin=0.10, collider=False)
        sc.build_slope(stage, f"{prefix}/RoofPE", x_ridge + run1, z_ridge - d1,
                       run2, d2, y0, y1, thick, mtl, margin=0.10,
                       collider=False)
        sc.build_slope(stage, f"{prefix}/RoofN", x_ridge - run1,
                       z_ridge - d1, run1, -d1, y0, y1, thick, mtl,
                       margin=0.10, collider=False)
        sc.build_slope(stage, f"{prefix}/RoofNE", x_ridge - half_run,
                       z_ridge - d1 - d2, run2, -d2, y0, y1, thick, mtl,
                       margin=0.10, collider=False)

    # -------------------------------------------------------------------
    # dressing : Iljumun gate · 2 stone lanterns · Dharma hall silhouette · pines · shrubs
    # -------------------------------------------------------------------
    def build_gate(M):
        g = PARAMS["gate"]
        for tag, sgn in (("P", 1.0), ("N", -1.0)):
            CYL(f"{ROOT}/Gate/Post_{tag}",
                (g["cx"], sgn * g["half_y"], g["post_h"] / 2.0),
                g["post_r"], g["post_h"], M["wood"], col=True)
            # [v6] plinth stones - eases the 'beige box' look of timber posts stuck straight into the ground
            CYL(f"{ROOT}/Gate/Plinth_{tag}",
                (g["cx"], sgn * g["half_y"], 0.15),
                g["post_r"] * 1.55, 0.30, M["stone_cap"], col=True)
        # architrave (horizontal lintel)
        BOX(f"{ROOT}/Gate/Beam",
            (g["cx"], 0.0, g["post_h"] + g["beam_t"] / 2.0),
            (g["post_r"] * 2.2, 2 * (g["half_y"] + g["beam_over"]),
             g["beam_t"]), M["wood"])
        gable_roof(f"{ROOT}/Gate", g["cx"], g["ridge_z"], g["roof_half_run"],
                   g["roof_drop"], -g["roof_y"], g["roof_y"], g["roof_t"],
                   M["roof"])
        # [v6] flying rafter (2nd-tier eave) - 0.34 m below the main roof and 0.30 m further out, making
        #      a two-tier eave shadow (a cue for the double eaves of a Korean temple gate). No interpenetration:
        #      the lower eave top (ridge−0.34) sits below the main roof soffit (ridge−roof_t).
        gable_roof(f"{ROOT}/GateEave", g["cx"], g["ridge_z"] - 0.45,
                   g["roof_half_run"] + 0.30,
                   g["roof_drop"] * (g["roof_half_run"] + 0.30)
                   / g["roof_half_run"],
                   -(g["roof_y"] + 0.22), g["roof_y"] + 0.22, 0.11,
                   M["wood"])

    def build_lanterns(M):
        """2 stone lanterns — base stone·lower pedestal·shaft·upper pedestal·light chamber·2-tier roof stone·jewel finial.
        [v6] The old shape (square body + square cap) combined with the masonry texture to read as a
        'brick chimney'. The member layout was changed to a standard lantern profile and the light
        chamber given dark light windows so it reads from the silhouette alone. Total height = lantern_height()."""
        ln = PARAMS["lantern"]
        pw, ph = ln["plinth_w"], ln["plinth_h"]
        for i, p in enumerate(PARAMS["lanterns"]):
            gz = ground_z(p["cx"], p["cy"])
            pre = f"{ROOT}/Lantern_{i}"
            BOX(f"{pre}/Plinth", (p["cx"], p["cy"], gz + ph / 2.0),
                (pw, pw, ph), M["stone_cap"], col=True)           # base stone
            z = gz + ph
            CYL(f"{pre}/Lower", (p["cx"], p["cy"], z + ln["lower_h"] / 2.0),
                ln["lower_r"], ln["lower_h"], M["stone_cap"])      # lower pedestal
            z += ln["lower_h"]
            CYL(f"{pre}/Shaft", (p["cx"], p["cy"], z + ln["shaft_h"] / 2.0),
                ln["shaft_r"], ln["shaft_h"], M["stone_cap"])      # shaft
            z += ln["shaft_h"]
            CYL(f"{pre}/Upper", (p["cx"], p["cy"], z + ln["upper_h"] / 2.0),
                ln["upper_r"], ln["upper_h"], M["stone_cap"])      # upper pedestal
            z += ln["upper_h"]
            # light chamber : 4 corner posts + dark interior (light window) - no interpenetration (posts are outboard)
            fo = (ln["fire_w"] - ln["pillar"]) / 2.0
            for j, (sx, sy) in enumerate(((1, 1), (1, -1), (-1, 1), (-1, -1))):
                BOX(f"{pre}/Fire_{j}",
                    (p["cx"] + sx * fo, p["cy"] + sy * fo,
                     z + ln["fire_h"] / 2.0),
                    (ln["pillar"], ln["pillar"], ln["fire_h"]), M["stone_cap"])
            BOX(f"{pre}/FireCore",
                (p["cx"], p["cy"], z + ln["fire_h"] / 2.0),
                (ln["fire_w"] - 2 * ln["pillar"] - 0.02,
                 ln["fire_w"] - 2 * ln["pillar"] - 0.02,
                 ln["fire_h"] * 0.92), M["roof"])
            z += ln["fire_h"]
            BOX(f"{pre}/Cap", (p["cx"], p["cy"], z + ln["cap_h"] / 2.0),
                (ln["cap_w"], ln["cap_w"], ln["cap_h"]), M["stone_cap"])
            z += ln["cap_h"]
            BOX(f"{pre}/Cap2", (p["cx"], p["cy"], z + ln["cap2_h"] / 2.0),
                (ln["cap2_w"], ln["cap2_w"], ln["cap2_h"]), M["stone_cap"])
            z += ln["cap2_h"]
            sc.add_sphere(stage, f"{pre}/Jewel",
                          (p["cx"], p["cy"], z + ln["jewel_r"]),
                          (ln["jewel_r"],) * 3, M["stone_cap"])    # jewel finial

    def build_hall(M):
        """Upper Dharma hall silhouette : podium (stone wall) + pillar row + gable roof."""
        hl = PARAMS["hall"]
        BOX(f"{ROOT}/Hall/Base", (hl["cx"], hl["cy"], hl["base_h"] / 2.0),
            (hl["sx"] + 1.2, hl["sy"] + 1.2, hl["base_h"]), M["rock"],
            col=True)
        n = int(hl["n_posts"])
        for j in range(n):
            t = (j / float(n - 1)) - 0.5
            px = hl["cx"] + t * (hl["sx"] - 0.8)
            for tag, sgn in (("P", 1.0), ("N", -1.0)):
                CYL(f"{ROOT}/Hall/Post_{j}_{tag}",
                    (px, hl["cy"] + sgn * (hl["sy"] / 2.0 - 0.4),
                     hl["base_h"] + hl["post_h"] / 2.0),
                    hl["post_r"], hl["post_h"], M["wood"])
        # body (wall) - a dark panel inside the pillar row
        BOX(f"{ROOT}/Hall/Body",
            (hl["cx"], hl["cy"], hl["base_h"] + hl["post_h"] / 2.0),
            (hl["sx"] - 1.0, hl["sy"] - 1.2, hl["post_h"]), M["wood"])
        gable_roof(f"{ROOT}/Hall", hl["cx"], hl["ridge_z"],
                   hl["roof_half_run"], hl["roof_drop"],
                   hl["cy"] - hl["roof_y"], hl["cy"] + hl["roof_y"],
                   hl["roof_t"], M["tile"], upturn=True)
        # [S3-7] rafter-end dentil row under the **+X** eave only — that is the face
        #   `gate_frame` looks at (eye x 7.0 -> target x −5.6), and G7 shows the dentils on
        #   the nearest roof only. 22 boxes, one row, no second tier.
        ep = PARAMS["eave"]
        dw, dd, dh = (float(v) for v in ep["dentil"])
        ex = hl["cx"] + hl["roof_half_run"]
        ez = hl["ridge_z"] - hl["roof_drop"] + float(ep["lift"])
        n_d = int(ep["dentil_n"])
        for j in range(n_d):
            dy = hl["cy"] - hl["roof_y"] * 0.92 \
                + 2.0 * hl["roof_y"] * 0.92 * (j + 0.5) / n_d
            BOX(f"{ROOT}/Hall/Dentil_{j}", (ex - dd / 2.0, dy, ez - dh * 0.75),
                (dd, dw, dh), M["wood"])

    def build_roof_cluster(M):
        """[S3-7] Two further roof masses at staggered depth (§4.1-4), plus the 단청-red wall
        fragment under the mid roof's eave. `gate_frame`-tier only — see the PARAMS note."""
        hl = PARAMS["hall"]
        ep = PARAMS["eave"]
        for r in PARAMS["roof_cluster"]:
            s = float(r["s"])
            z0 = float(r["z0"])
            pre = f"{ROOT}/Roof{r['name']}"
            BOX(f"{pre}/Terrace", (r["cx"], r["cy"], (z0 - 0.4) / 2.0),
                ((hl["sx"] + 3.4) * s, (hl["sy"] + 3.4) * s, z0 + 0.4),
                M["rock"])
            BOX(f"{pre}/Base",
                (r["cx"], r["cy"], z0 + hl["base_h"] * s / 2.0),
                ((hl["sx"] + 1.2) * s, (hl["sy"] + 1.2) * s,
                 hl["base_h"] * s), M["rock"])
            BOX(f"{pre}/Body",
                (r["cx"], r["cy"],
                 z0 + hl["base_h"] * s + hl["post_h"] * s / 2.0),
                ((hl["sx"] - 1.0) * s, (hl["sy"] - 1.2) * s,
                 hl["post_h"] * s), M["wood"])
            gable_roof(pre, r["cx"], z0 + hl["ridge_z"] * s,
                       hl["roof_half_run"] * s, hl["roof_drop"] * s,
                       r["cy"] - hl["roof_y"] * s, r["cy"] + hl["roof_y"] * s,
                       hl["roof_t"] * s, M["tile"], upturn=True)
        rm = PARAMS["roof_cluster"][0]
        s0 = float(rm["s"])
        BOX(f"{ROOT}/RoofMid/RedWall",
            (rm["cx"] + hl["roof_half_run"] * s0 * 0.55, rm["cy"],
             float(rm["z0"]) + hl["base_h"] * s0 + hl["post_h"] * s0 * 0.45),
            (0.30, hl["sy"] * s0 * 0.80, hl["post_h"] * s0 * 0.72),
            M["red"])
        # E7-10 wooden pole — one cylinder, CC0 pier-pole maps, no crossarm.
        pp = PARAMS["pole"]
        CYL(f"{ROOT}/Pole", (pp["cx"], pp["cy"],
                             _zone_z(pp["cx"], pp["cy"], "flat")
                             + pp["h"] / 2.0),
            pp["r"], pp["h"], M["pole"], col=True)
        print(f"[S3-7] 지붕군 {1 + len(PARAMS['roof_cluster'])}동(처마 들림 "
              f"{ep['lift']:.2f} m / {ep['run']:.2f} m) · 서까래 "
              f"{ep['dentil_n']} · 단청 벽편 1 · 목주 1 — gate_frame 전용")

    def build_nature(M):
        tr = PARAMS["tree"]
        for name, cx, cy, zone, th in PARAMS["pines"]:
            gz = _zone_z(cx, cy, zone)
            sc.build_tree(stage, f"{ROOT}/Pine_{name}", cx, cy, gz,
                          M["wood"], M["canopy_a"], M["canopy_b"],
                          trunk_r=tr["trunk_r"], trunk_h=th,
                          stake_r=0.004, stake_h=0.02, stake_off=0.2)
        # shrub = 3 overlapping flattened ellipsoids (scene04 v5 convention - no angular slabs)
        #   [v6] On a slope (zones north/south fall along X), grounding by the blob centre z leaves
        #   **the downhill side floating by rx·tan19 deg** -> the ground at the downhill end (x+rx)
        #   is used as the datum instead, removing the float structurally.
        sh = PARAMS["shrub"]
        emb = sh["embed"]
        for n, (cx, cy, zone) in enumerate(PARAMS["shrubs"]):
            for j, (dx, dy, rx, ry, rz) in enumerate(sh["blobs"]):
                bx, by = cx + dx, cy + dy
                gz = min(_zone_z(bx - rx, by, zone), _zone_z(bx, by, zone),
                         _zone_z(bx + rx, by, zone))
                sc.add_sphere(stage, f"{ROOT}/Shrub_{n}_{j}",
                              (bx, by, gz + rz * (1.0 - emb)),
                              (rx, ry, rz), M["shrub"])

    def build_horizon(M):
        """Horizon closure : front ridges (near, in 3 pieces + mid·far) + crest forest bands + rear forest line.
        [v6] The near ridge is broken into 3 staggered slabs and each crest carries a round-crown
        forest band, clearing the 'straight ridgeline + black wall' (albedo: see material)."""
        rg = PARAMS["ridge"]
        for i, r in enumerate(rg):
            BOX(f"{ROOT}/Ridge_{i}", (r["cx"], r["cy"], r["z0"] + r["h"] / 2.0),
                (r["sx"], r["sy"], r["h"]), M[f"ridge_{r['tone']}"], col=True)
        # [GT-126] f0/f1 fractional spans: the near bands run as two segments of
        #   different height (see the PARAMS row) so the crown hash re-seeds and the
        #   apex line staggers — the audited single-height "green dome row" breaks
        #   without leaving the GT-63 box+crown idiom.
        for n, (ri, hh, tone, f0, f1) in enumerate(PARAMS["ridge_crest"]):
            r = rg[ri]
            top = r["z0"] + r["h"]
            ya = r["cy"] - r["sy"] / 2.0
            sc.build_hedge(stage, f"{ROOT}/RidgeCrest_{n}",
                           r["cx"] - r["sx"] * 0.62, ya + r["sy"] * f0,
                           r["cx"] + r["sx"] * 0.62, ya + r["sy"] * f1,
                           hh, mtl=M[f"crest_{tone}"], base_z=top - 0.4)
        for i, t in enumerate(PARAMS["ridge_trees"]):
            r = rg[t["ri"]]
            sc.build_tree(stage, f"{ROOT}/RidgeTree_{i}", r["cx"], t["cy"],
                          r["z0"] + r["h"] - 0.4,
                          M["wood"], M["canopy_a"], M["canopy_b"],
                          trunk_r=0.16, trunk_h=4.2, stake_r=0.004,
                          stake_h=0.02, stake_off=0.2)
        bh = PARAMS["back_hedge"]
        for i, h in enumerate(PARAMS["back_hedges"]):
            sc.build_hedge(stage, f"{ROOT}/BackHedge_{i}",
                           bh["cx"] - bh["sx"] / 2.0,
                           h["cy"] - bh["length"] / 2.0,
                           bh["cx"] + bh["sx"] / 2.0,
                           h["cy"] + bh["length"] / 2.0, bh["h"],
                           base_z=h["base"])
        for i, t in enumerate(PARAMS["back_trees"]):
            sc.build_tree(stage, f"{ROOT}/BackTree_{i}", t["cx"], t["cy"],
                          t["gz"], M["wood"], M["canopy_a"], M["canopy_b"],
                          trunk_h=t["trunk_h"], stake_r=0.004, stake_h=0.02,
                          stake_off=0.2)
        for nm, x0, x1, y0, y1, hh, bz in PARAMS["far_hedges"]:
            sc.build_hedge(stage, f"{ROOT}/FarHedge_{nm}", x0, y0, x1, y1, hh,
                           base_z=bz)

    def build_sign(M):
        """[v5 shared layer] Temple notice board — at the entrance (before the gate), facing the approach."""
        sg = PARAMS["sign"]
        sc.build_sign(stage, f"{ROOT}/SignInfo", sg["cx"], sg["cy"], 0.0,
                      sg["yaw"], M["sign_info"], w=sg["w"], h=sg["h"],
                      pole_h=sg["pole_h"], pole_mtl=M["wood"],
                      back_mtl=M["sign_back"])

    # -------------------------------------------------------------------
    # [W2-D] ground_kit - P12 courtyard_dg. Runs after the dressing so the
    #   scatter callback is invoked last (spec Sec.8.4 call-order rule).
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        gp = ground_plan()
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(stain_dirt=M["leaf"], stain_water=M["gk_moss"],
                  wear=M["gk_wear"], edge_break=M["leaf"], litter=M["leaf"],
                  debris=M["gk_rock"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] scene07 P12 · 프림 {res['prims']} · "
              f"산포 {res['instances']} · δmax {res['gt_delta_max']:.4f} · "
              f"unit_cell {res['unit_cell']}")
        return res

    def build_cues(M):
        """Cues that are not the practice here (code path only — all False by default)."""
        if cfg["cue_railing"]:
            def gfn(x):
                return path_z(x)
            sc.build_railing_line(stage, f"{ROOT}/Rail", -1.55, 0.0, 0.0,
                                  STAIR_RUN, STAIR_DROP, gfn, M["rail"],
                                  rail_h=0.9, post_r=0.035, spacing=1.4,
                                  rail_r=0.035)
        if cfg["cue_tactile"]:
            # [W2 · ground_kit §12.5-3] texture-backed so the 36 dots shade.
            tac = sc.tactile_pbr(stage, "/World/Looks/Tactile")
            sc.build_tactile(stage, f"{ROOT}/Tactile", -0.62, -0.02,
                             -1.6, 1.6, tac, z=0.0)
        if cfg["cue_nosing"]:
            # H2 / RF-5 / KFS-TRAIL 13-2 나: a natural-stone stair's anti-slip measure IS
            #   the rough face. This path stays dead (`cue_nosing = False`) and exists only
            #   so the toggle can be exercised; it is never called from a shipped 07.
            for c in COURSES:
                for s in c["slabs"]:
                    BOX(f"{ROOT}/Nose_{c['i']}_{s['k']}",
                        (s["xb_f"] - 0.03, (s["y0"] + s["y1"]) / 2.0,
                         s["top"] + 0.002),
                        (0.06, (s["y1"] - s["y0"]) * 0.9, 0.012),
                        M["stone_cap"])

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    if cfg["hazard_stairs"]:
        build_terrain(M)
        build_stones(M)
        build_stone_dressing(M)
        build_kerb(M)
        build_ferns(M)
        build_leaf_masks(M)
        build_cues(M)
    else:
        build_flat_fill(M)
    build_horizon(M)
    if cfg["cue_scene_dressing"] and cfg["hazard_stairs"]:
        build_gate(M)
        build_lanterns(M)
        build_hall(M)
        build_roof_cluster(M)
        build_nature(M)
    if cfg["cue_sign"] and cfg["hazard_stairs"]:
        build_sign(M)
    if cfg["hazard_stairs"]:
        build_ground_kit(M)          # [W2-D] ground elements, dressing last

    rises, gaps, enter, exit_ = stone_metrics()
    print(f"[기하] 자연석 계단 {len(COURSES)}코스 run={STAIR_RUN:.2f} drop="
          f"{STAIR_DROP:.2f} · 답차 {min(rises):.3f}~{max(rises):.3f} · "
          f"코스간 최대 개방 {max(gaps):+.3f}(<0) · 진입 {enter:+.3f} · "
          f"탈출 {exit_:+.3f} UP-STEP · 측방 낙차 {SIDE_DROP:.2f}")

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    # ── camera + render mode ──
    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    views = build_views()
    _v0 = views["temple_walk"]
    look_from(_v0["eye"], _v0["tgt"])

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

    if capture_mode:
        out_dir_default = os.path.join(LOOKCHECK_DIR, "auto")
        sc.capture_pipeline(simulation_app, views, out_dir_default,
                            set_render_mode, look_from)
        simulation_app.close()
        return

    # ── GUI look check ──
    input_iface = carb.input.acquire_input_interface()
    appwindow = omni.appwindow.get_default_app_window()
    K = carb.input.KeyboardInput
    rot_step = float(PARAMS["light"]["dome_rotation_step"])
    dome_user_rot = [0.0]

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene07_{ts}.png")
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
