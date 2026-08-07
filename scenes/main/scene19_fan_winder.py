# -*- coding: utf-8 -*-
"""
scene19_fan_winder.py — NegObs synthetic scene 19: T7 fan corner stairs (winder)
(Isaac Sim 4.5)

Spec : Docs/multi_scene_brief_v3.md §D scene19_fan_winder (the only spec)
Shared library : scene_common.py (§A) — boot · make_pbr · build_arc_steps · lighting · capture
Motif reference : scene05_amphitheater.py (main skeleton · arc step tiers · cue toggles)

Type identity: the nosings are radial — no straight-line vanishing point.
  12 fan steps (r_in1.2/r_out4.0, 7.5 deg sector each, drop 1.8m) wind a 1/4 turn (90 deg)
  around a building corner. From the upper approach direction (+X), the radial nosings break
  the vanishing-point rule.

[accessibility v2] (2026-07-27, see the look_refs/scene19 study): in the old version the parapet blocked
  all 12 sectors, and the wedge between the outer arc and the sidewalk plus the pocket beside the L wall
  were open drops, so pedestrian entry was impossible. Fix: keep the parapet on sectors 2..9 only
  (opening the entry and exit) + gate posts, a corner slab (the wedge floor = an extension of the lower
  plaza), an upper threshold sliver, an edge guard retaining wall, and the L wall flush with the radial
  edges (sealing the pockets). See PARAMS["access"].

[rooftop v3] (2026-07-27, user instruction "widen the approach + rooftop scene context"):
  (1) approach widened — entry sectors 0..2 are merged into a kite landing (same top face −0.15),
    parapet sectors 3..9 → the entry opens over a 22.5 deg arc (outer arc 1.53m, was 1.05m). The remaining
    9 steps divide riser (1.8−0.15)/9 evenly, so the total drop stays 1.8. See _step_top.
  (2) rooftop reframing — the upper sidewalk (z0) = the roof terrace of a low wing, the L wall = the
    rooftop core, the lower sidewalk (−1.95) = the terrace one floor down. The ground drops −2.31→−6.0
    (road level) and the sidewalk slabs extend into the building body. Rooftop parapet (perimeter edge
    guard = a cue for inferring the plant), HVAC · vent · pipe run · rooftop door (plant cues), and roofs of
    surrounding low-rise buildings (scale anchors at or below eye height, build_building with base_z
    support). See PARAMS["roof"] and build_rooftop.

[rooftop v4] (2026-07-27, judge_v6_rt_light8 §scene19 rework — 2 re-aimed cuts failed 2 rounds running):
  The cause of both failures was **not doing the occlusion check on coordinates**. So section [C]
  (_solid_at · _frame_scan · _geom_report) is added, porting and simplifying the
  `_obstacle_boxes`/`_solid_at` sight-line test of scene08_sunken_plaza, and with NEGOBS_SMOKE=1 it
  **checks every preset on coordinates before booting** (sparse ray marching of the frame → occupancy).
  (1) roof_skyline — building E's roof was being occluded tangentially by the rooftop parapet (U_N top 1.1).
    To keep the human eye-height limit (2.0 m), instead of raising the camera **distant building E is moved
    north** (old x−28..−14·y8..22 → x6..20·y16..42, height 4.5 unchanged).
    The bearing becomes due north, where the lower terrace parapet (top −0.75) is out of the sight line,
    so building E's roof (−1.5, cap −1.0) opens up 3.0 m below eye height.
  (2) radial_nosing — the old eye(5.2,0.7) was inside the L wall and edge guard, so no tgt could avoid the
    white mass. Following the judgment's recommendation it moves **near winder_mid (above the kite
    landing)** and tgt drops to the foot of the newel, taking in all 12 steps from above. White mass 0 %.
  (3) (additional director instruction) lower_lookup — the old eye faced the parapet ring head-on, so the
    sight-line axis was blocked by `Parapet_9` 0.60 m ahead and the white mass was 54 %.
    Replaced by stepping down **onto the last step of the descent (sector 10)** and looking back up the
    fan — riser faces 47 %, white 0 %. It pairs with radial_nosing (down-view = treads).
  (4) (additional director instruction) roof_context — the rooftop planter is pushed to the west end
    (6.0,−6.8) and the depression eased so the canopy top comes inside the frame (sy +0.86).
  ※ Not fixed (structural): the whole winder corridor lies in the shadow of the L wall (top 3.5). Lighting
    adjustment is out of scope for this instruction — read the PT judgment on the premise that
    "the corridor cuts receive sky light only".

[W3 L19] (2026-07-31, lane L19 — `Docs/reports/w3_l19_v1.md`; ledger **GT-50 · GT-51**)
  scene19 is **imageless** and rides **G8** (`w3_intake_v2_images.md` §4 Lane-3 row 3.7 —
  the only target image with curved steps, curved parapets and a modern Korean urban
  roofscape), with **G13** secondary for rooftop/utility hardware. Season is therefore
  pinned **summer** from G8 (§7 ruling 8) and `_season_audit()` asserts it.
  (1) **GT-50 — K4(d) `mesh=True`** on all four arc families. The box convention's
    1.03 chord margin let each tread overshoot its own design ray by 3.045° at r_in;
    where two treads overlapped the higher one won the top face, so the walked surface
    sat **one riser (183.333 mm) too high** in 9 wedge slivers. `_arc_split_proof()`
    measures it: 205,257 samples, 17,019 differ, **all in one stratum**, new-void 0.
  (2) **GT-51** — era rider §6.2-B (stair guard 1.00 → **1.10 m**) · **N-A3** rooftop
    plant as measured CC0 scans through `urban_kit(treatment="mtlxoff")` · the 옥상
    planter rebuilt to 조경기준 제12조 토심 0.75 m with `juniper` / `Yew` pinned ·
    19-4 membrane patches 4 → 2 re-materialled to read as **우레탄 덧방**, not asphalt.
  ※ Carried, not fixed: the winder corridor's photometry (finding **L19-F1**) — see the
    report. The v4 note below already recorded the cause; L19 measures it.

[GT-82] (2026-08-06, user verdict "this scene only needs the stairs going down from the
  rooftop — why another building · it is too dark near the stairs · entrance and exit still
  read narrow"). Four changes, all sourced from the 260731_w3_full cuts.
  (1) **Backdrop buildings C · D · E deleted.** They were the "another building" and they were
    also the floating-plate defect: `build_building` runs `facade_kit.build_aircon_units(
    mode="eaves", eaves_z=2.30)` and `Facade.world()` takes that z as a **world absolute**,
    so D's 4 units sat at z 2.30 while D's roof deck is at z −2.50 and its parapet crown at
    −1.30 — **3.60 m of open air under a 0.06 m bracket** [measured]. In `pt_noon_roof_context`
    they project to sx +0.122 / +0.271 / +0.432 (the 4th at +0.609 is behind the juniper),
    sy +0.340 — which is the row of 3 dark plates the audit flagged. Deleting the buildings
    deletes the plates by construction; the scene is now the host L-core and nothing else.
    Consequence: `roof_skyline` keeps its eye/tgt but its gate is re-based from "building E
    occupancy" to "the 6 m drop to the alley + the north parapet crown", which is what a
    rooftop north view actually has to read once the backdrop is gone.
  (2) **The black flanking masses take real concrete.** `granite_dark` measures linear
    luminance **0.0767** [measured, assets/scene01/granite_dark_diff.jpg] and it was bound to
    the two L-core walls and the newel — the whole surround of the descent. In shadow that is
    indistinguishable from black, which is what `upper_approach` and `entry_gate` show. The
    walls move to `concrete_wall` (texture mean 0.2372) tinted to **0.290** = **3.78x**;
    the newel to the same texture tinted to **0.159** = 2.08x, still 0.48x of the tread value
    (`plaza_light` 0.4627 x 0.72 = 0.333) so it keeps its job as the dark radial datum.
    The rooftop planter box leaves `granite` for the same reason (it is the near-black box in
    `roof_context`).
  (3) **The core is lowered 3.50 -> 2.55 m and capped.** Sun bearing is az **245.0 deg**,
    elev **49.79 deg** [computed from `light.noon_dome_rot` −110 + `SUN_AZ_OFFSET` 171.5 +
    `hdri_sun_rotz_offset` 233.5 and `noon_sun_elev`], so shadow offset per metre of height is
    (**+0.766 x, +0.357 y**) — `_sun_dir` / `_shadow_reach` derive both from the same PARAMS
    the stage lighting reads, so the number cannot drift from the render. At 3.50 the west
    wall's crown threw its shadow to **x 4.06** on the lowest tread, i.e. past `r_out` 4.00 —
    **the whole fan was in shade at the bottom, 0.00 m of it lit** — and the south wall's to
    y 1.30 across a 1.53 m landing, leaving **0.23 m** lit. With the crown at 2.55 (+0.12
    coping) those become **x 3.42** (0.58 m of the fan lit) and **y 1.01** on a 2.00 m landing
    (**0.99 m lit, 15 % -> 50 %**). 2.55 is the floor a rooftop stair core can take
    (2.10 door + 0.05 frame head + 0.40 lintel). The wall top was a raw box face, so an L of
    three non-overlapping coping boxes (`CoreCap_S/W_S/W_N`, 0.12 thick, 0.08 proud) caps it —
    split at y −1.08 / +0.08 so no two caps are ever coplanar.
  (4) **Entry and exit widened, and both parapet run ends get a pier.** `parapet_first`
    3 -> 4 and `parapet_last` 9 -> 8: the retained ring is sectors 4..8, so the entry opens
    over 0..29.5 deg and the exit over 68.0..90 deg. Measured by `_clear_widths`: the entry
    throat at the first nosing line goes **1.530 -> 1.958 m** and the exit's open-arc chord
    **1.044 -> 1.526 m** — the old exit was **below** the 1.20 m stair clear-width floor this
    project works to, which is the "exit looks narrow" reading. The threshold and the edge guard follow the
    new 30 deg arc (`x0` 3.70 -> **3.46** = 4·cos30, which is what stops a sliver drop opening
    between the arc and the threshold; `y` 1.53 -> **2.00** = 4·sin30) and they now share one
    west face plane instead of jogging 0.24 m. The run ends were a sawn radial face with a
    0.05 m cylinder standing beside it; they are now `ParapetEnd_entry/exit` — annular piers
    r 3.78..4.09 (0.04 proud of the ring on both radii, so the cut face is inside the pier),
    3.0 deg wide, 0.14 m proud of the guard crown — with the gate post kept as a **finial on
    the pier** so the prim path and the "post is the tell" reading both survive.

Run / capture / smoke : the same env convention as scene05 and scene06.
    NEGOBS_CAPTURE=1 / NEGOBS_SMOKE=1 / NEGOBS_PARAMS_OVERRIDE / NEGOBS_SCENE_CONFIG

Coordinates: Z-up, m. Winder centre (the building corner newel) (0, 0). First step direction +X.
  Preset axis = the upper approach direction (looking down the descent from +X toward −X): grid_views
  mirrored about x=6 → the axis looking down at the winder from the upper sidewalk [brief §D 'preset axis'].
"""

import os
import sys
import math
import json
import datetime

import numpy as np

import scene_common as sc
import ground_kit as gk


# ===========================================================================
# [A] SCENE_CONFIG — 7 keys. hazard_stairs = winder descent geometry toggle (↔ flat corner).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,    # fan winder (False → z=0 flat corner plaza)
    "cue_railing":        True,    # handrail on top of the outer parapet (usual for public corner stairs)
    "cue_tactile":        False,   # True → warning tactile strip on the upper approach
    "cue_material_break": True,    # upper sidewalk (plaza_light) vs lower sidewalk (plaza_lower)
    "cue_nosing":         False,   # True → radial nosing anti-slip arc bands
    "cue_sign":           False,   # [reserved]
    "cue_scene_dressing": True,    # [GT-82] rooftop planter · parapets · plant · grass
                                   #   (the 3 backdrop buildings are gone — see PARAMS)
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    center=dict(cx=0.0, cy=0.0),
    # 12 fan steps: step i = build_arc_steps(r_in1.2/r_out4.0, i*7.5 deg..+7.5 deg, seg3,
    #   top_z=−0.15*(i+1), base −2.3) → 90 deg of total turn, drop 1.8
    # [rooftop v3] kite_n: entry sectors 0..kite_n-1 are merged into a single kite landing (top −riser).
    #   The remaining (n−kite_n) steps divide the (n·riser − riser) drop evenly → total drop stays 1.8.
    # [W3 L19 · GT-41] `mesh=True` — the K4(d) true annular sector. The builder landed
    #   default-OFF at `5ceb76a` (ledger GT-6 `RELEASED`) and 05 · 06 · 19 flip it inside
    #   their own pilots; scene06's is GT-29, this is scene19's. The box convention lays a
    #   Cube of chord `2·r_out·sin(Δθ/2)·1.03` per sub-segment, so at Δθ = 2.5° the half
    #   chord is **89.877 mm** and the angular overshoot past the design ray is
    #   `asin(89.877/r) − 1.25°` = **3.0453° at r 1.2 → 0.0375° at r 4.0** (arc 63.78 →
    #   2.62 mm). Where two treads overlap the higher one wins the top face, so the tread
    #   hand-over sat that far past its own design ray. See §[C] `_arc_split_proof`.
    winder=dict(r_in=1.2, r_out=4.0, n=12, sector_deg=7.5, a0=0.0,
                riser=0.15, base_z=-2.3, seg=3, kite_n=3, mesh=True,
                arc_seg=6),
    # inner corner newel: Cylinder r1.1 (z −2.3..0.5)
    newel=dict(r=1.1, z_bot=-2.3, z_top=0.5),
    # building corner L wall: flush with the winder radial edges (y=0 / x=0) — seals the side drop pockets
    #   [accessibility v2] south x1 1→4·y1 −0.2→0, west x1 −0.2→0·y1 1→4
    # [GT-82(3)] `z_top` 3.5 -> **2.55**, plus a coping cap. 2.55 = door 2.10 + frame head
    #   0.05 + lintel 0.40, i.e. the lowest a stair core that carries a 2.1 m door can be.
    #   The 0.95 m removed is worth (0.95 x 0.766) = **0.73 m** of shadow pulled back off the
    #   winder in x and (0.95 x 0.357) = 0.34 m in y at every level [computed, sun az 245.0 /
    #   elev 49.79]. `cap_t/cap_over` build the L coping that terminates the wall top.
    walls=dict(z_bot=-6.0, z_top=2.55,  # [rooftop v3] extended down to ground −6.0 (rooftop core body)
               cap_t=0.12, cap_over=0.08,
               south=dict(x0=-8.0, x1=4.0, y0=-1.0, y1=0.0),
               west=dict(x0=-1.0, x1=0.0, y0=-8.0, y1=4.0)),
    # outer low parapet: per-step arc ring (r 3.82..4.05), +h above each step top (arc ring)
    # [W3 L19 · era rider §6.2-B] **h 1.00 → 1.10.** "Rail height 0.90 m outdoors is the
    #   wrong default. Outdoor = 1.10 m … **scene19 → 1.1 m**"
    #   (`w3_execution_spec_v1.md` §10.7). This is the **stair** guard on the winder's
    #   outer arc — a 1.8 m fall to the corner slab — and 1.00 m was below the outdoor
    #   line. The **rooftop perimeter** parapet (`roof.pp_h` 1.20) is a different fixture
    #   under a different clause (건축법 시행령 제40조 옥상광장 난간 1.2 m) and is NOT
    #   moved here; `roof.pp_h_inner` is already 1.10 and the `roof_skyline` sight-line
    #   budget is computed against it, so touching it would move a judged cut.
    parapet=dict(r_in=3.82, r_out=4.05, h=1.1),
    # [accessibility v2] entry and exit opened (per the look_refs study): parapet on sectors 2..9 only.
    #   corner   = corner slab (the wedge floor between the outer arc and the straight sidewalk edge, lower plaza extension −1.95)
    #   threshold= upper threshold sliver (gap between sidewalk x=4 and the entry sector outer arc, max 0.14, z0)
    #   guard    = upper sidewalk edge retaining wall (guards the 1.95 drop above the wedge, top +1.0)
    # [rooftop v3] entry widened: open sectors 0..2 (kite landing) → parapet 3..9.
    #   threshold x0 3.86→3.70 (at 22.5 deg the outer arc retreats to x=3.70 — prevents a sliver gap;
    #   the inner band bites in as a z0 plate above the kite top face −0.15 = effective tread boundary x<=3.70),
    #   y1 1.05→1.53 (=4·sin22.5 deg). guard follows at x0 3.7·y0 1.53 (seals the junction slot).
    # [GT-82(4)] entry and exit widened again — `parapet_first` 3→**4**, `parapet_last` 9→**8**,
    #   i.e. the retained ring is sectors 4..8 and the openings become 0..30 deg / 67.5..90 deg.
    #   Measured (`_clear_widths`): entry throat at the first nosing line **1.530 → 1.958**,
    #   exit open-arc chord **1.044 → 1.526**. The old exit sat below the 1.20 m stair
    #   clear-width floor. The fan itself does not move: `winder` (n 12 · kite_n 3 · riser
    #   0.15 · drop 1.8) is untouched — only which sectors carry the outer guard.
    #   threshold `x0` 3.70→**3.46** is forced, not cosmetic: at 30 deg the outer arc retreats
    #   to x = 4·cos30 = 3.4641, so a threshold that stopped at 3.70 would leave a
    #   0.236 m open drop between the arc edge and the sliver. `y1` 1.53→**2.00** = 4·sin30.
    #   The guard takes the same `x0` so the entry throat's west face is one plane instead of
    #   a 0.24 m jog.
    access=dict(parapet_first=4, parapet_last=8,
                corner=dict(x0=-1.0, y0=-1.0, x1=4.0, y1=4.0),
                threshold=dict(x0=3.46, y0=0.0, y1=2.00),
    #   [W3 L19 · era rider §6.2-B] guard `h_top` 1.00 → 1.10 (same outdoor line as the
    #   winder parapet). `post_h` 1.15 → 1.25 is **not** a second era move: the post foot
    #   is buried 0.05 below its step top, so 1.15 put the cap at `top + 1.10`, exactly
    #   flush with the old 1.00 parapet + 0.10. Against a 1.10 parapet the same 0.10 m
    #   proud gate-post reading needs 1.25. The 0.10 m tell is the point of the post.
                guard=dict(x0=3.46, x1=4.0, y0=2.00, y1=4.0, h_top=1.1),
    #   [GT-82(4)] The gate post is no longer ground-founded: it stands on the end pier, so
    #   `post_h` 1.25 → **0.34** and its foot is buried 0.04 into the pier crown, which puts
    #   the cap at `pier_top + 0.30`. The 0.10 m proud tell that 1.25 was carrying is now
    #   carried by the pier's own `rise` (0.14 above the guard crown) plus the post above it —
    #   the run reads as pier + finial instead of a sawn face with a stick beside it.
                post_r=0.05, post_h=0.34,
    #   [GT-82(4)] `end_pier` — the terminal pilaster of the outer guard run. r 3.78..4.09 is
    #   0.04 proud of the ring (3.82..4.05) on **both** radii, so the ring's radial cut face
    #   sits inside the pier volume; `lead` 0.5 deg is how far it reaches past the run end and
    #   `span` 3.0 deg its total width, so it eats 0.5 deg of the opening and 2.5 deg of the
    #   retained ring. `drop` buries the foot 0.30 below the lower of the two straddled step
    #   tops — no floating end at either terminal.
                end_pier=dict(r_in=3.78, r_out=4.09, lead=0.5, span=3.0,
                              rise=0.14, drop=0.30)),
    # upper/lower sidewalks (material boundary cue) — solid slabs (down to ground −2.31)
    upper=dict(x0=4.0, x1=17.0, y0=-9.0, y1=4.0, top_z=0.0),
    lower=dict(x0=-9.0, x1=4.0, y0=4.0, y1=17.0, top_z=-1.95),
    # ground (grass) floor — [rooftop v3] road level −6.0 (upper sidewalk z0 = a rooftop 6m above ground)
    ground=dict(x0=-60.0, x1=60.0, y0=-60.0, y1=60.0, top_z=-6.0),

    # ═══ [W2-D ground_kit] P6 roof_membrane — spec §5.6 scene19 row ═════════
    #  19-1 urethane membrane waterproofing (green) + roll seam pitch 0.9~1.1 m, albedo **0.16~0.22**
    #       (director approved M2; the special-effects band 0.10~0.16 and the C4 props band 0.20~0.35
    #        have an empty intersection, so the spec ruled for the mid band of an aged coat) — kit ledger default 0.19.
    #  19-2 parapet turn-up + coping  -> build_rooftop (`roof.turnup_h/coping_w` above)
    #  19-3 roof drains at 2 places (10.5, -0.6) [in every F cut] · (6.0, -7.5)
    #  19-4 membrane repair overcoat patches · radial water marks around the drains · runoff below the parapet
    #    ★ [W3 L19] **4 → 2, and they are re-materialled so they READ as 우레탄 덧방.**
    #      Two separate defects, both measured at HEAD:
    #      (a) COUNT. The intake row (`w3_intake_v2_images.md` §2 scene19 (c)) calls the
    #          patch prescription "the second-highest count in the set, on a **roof
    #          membrane** … three of them on one small roof is not [real]" — and the file
    #          shipped **four**, on a 12.5 x 12.5 m deck. A urethane deck fails where water
    #          stands, which is the drain sump and the parapet turn-up, not four scattered
    #          spots. The two surviving 덧방 are re-sited **onto the two drains** (0.9 m
    #          off-centre, the ponding ring), which is where a real 보수 goes.
    #      (b) MATERIAL. Both patch roles were bound to `M["coating"]` — **the identical
    #          material as the deck**. A 2 mm proud plate in the same green at the same
    #          roughness is not a repair, it is nothing; the only way it could ever read
    #          was as a silhouette rectangle, which is the vocabulary U-6 bans. A real
    #          우레탄 덧방 is *the same product applied again*: same hue, **fresher value
    #          and markedly more sheen** because it has not chalked yet. So the patch takes
    #          its own material `patch_coat` (same green hue, +18 % value, roughness
    #          0.72 → 0.46) and the lap edge takes `patch_lap` (a slightly darker feathered
    #          band of the same coat) — NOT `gk_stain`, which is the dark asphalt saw-cut
    #          line and is exactly the "reads as asphalt" failure this row exists to fix.
    #          `build_patch_field(cutline=False)` is the kit default and `apply_ground`
    #          never overrides it, so no cut line is built at all — the saw-cut vocabulary
    #          is absent by construction and `patch_cut` is bound only so a future
    #          `cutline=True` cannot silently fall back to the dark stain.
    #  --   **no joint grid** — P6 has `joint=None`, so the kit cannot emit one.
    #  ★ Tactile **OFF** (§12.4): private rooftop, not a facility covered by the
    #    accessibility act. The scene keeps a `cue_tactile` path for ablation
    #    only; nothing is installed by default.
    #  ★ Frame origin: `build_views` mirrors `grid_views` about xref 5.8, so the
    #    preset grid origin is world x = 2*5.8 = **11.6** and the progression is
    #    **-X**. `plan_ground(origin=...)` wants that grid origin (the frame
    #    model puts the eye at s = -d), **not** the drop edge. The drop edge is
    #    the roof deck's west lip `upper.x0` = 4.0, i.e. s = 11.6 - 4.0 = **7.6**.
    #    dists are (2, 3.5, 5) to match `build_views` (d10 would be off-roof).
    gkit=dict(
        grid_origin_x=11.6,                    # = 2 * xref(5.8), build_views
        region_inset=0.25,                     # = roof.pp_t (inside parapets)
        drains=[(10.50, -0.60), (6.00, -7.50)],
        # [W3 L19] 4 → 2, and the two survivors carry **two different causes**, which is
        #   what makes them read as maintenance rather than as decoration:
        #     (11.60, −0.60) — the ponding ring of drain 1 (10.50, −0.60), the classic
        #        우레탄 방수 failure. 1.10 m off the gully centre, so it laps the sump
        #        surround without covering it.
        #     ( 8.00,  2.60) — the maintenance walking line out of the rooftop core door
        #        (x 4.04, y −0.50) toward the north parapet, where a coat wears through
        #        under dragged plant. Clear of the planter (x 4.5…7.5 · y −8.3…−5.3),
        #        the pipe run (y −8.55) and the U_N inner face (y 3.75) by ≥ 0.73 m.
        #   Drain 2 (6.00, −7.50) gets **no** patch: it is under the rooftop planter box,
        #   which is a pre-existing siting conflict this lane records rather than hides
        #   (finding L19-F2) — a 덧방 that nobody could reach is not evidence of repair.
        patches=[(11.60, -0.60), (8.00, 2.60)],
        seam_pitch=1.00,
        wear_n=5,
    ),
    # [GT-82(1)] **The three backdrop buildings are deleted, not disabled.**
    #   They were `C` (x44..54, h15), `D` (x−30..−16, h3.5) and `E` (x6..20·y16..42, h4.5),
    #   added in rooftop v3/v4 as horizon closure and as a below-eye-height scale anchor.
    #   Two reasons they go:
    #     (a) the scene is a rooftop-down fan stair and nothing else — a second building mass
    #         is the thing the reviewer could not account for;
    #     (b) every one of them shipped a **floating fixture**. `build_building` calls
    #         `facade_kit.build_aircon_units(mode="eaves", eaves_z=2.30)` and `Facade.world()`
    #         reads that z as a world absolute rather than relative to `base_z`, so on D
    #         (roof −2.50, parapet crown −1.30) the 4 units hang at z 2.30..2.855 —
    #         **3.60 m above the crown on a 0.06 m bracket** [measured]. That is the row of
    #         dark plates in `pt_noon_roof_context`; their projected sx +0.122/+0.271/+0.432
    #         and sy +0.340 match the audit frame to within 16 px [computed].
    #   The kit-side z bug is **not** fixed here — it is `facade_kit`, which this lane does not
    #   own. Nothing in scene19 references `PARAMS["buildings"]` any more, so the key is gone
    #   rather than left empty: an empty dict would read as "temporarily off".
    # [rooftop v3] rooftop parapet (perimeter guard) · plant props · rooftop door — build_rooftop
    roof=dict(pp_t=0.25, pp_h=1.2, pp_h_inner=1.1,
              # [W2-D §5.6 19-2] turn-up 0.30 m · coping 0.50, the middle of 0.45~0.55
              turnup_h=0.30, coping_w=0.50,
              # [W3 L19 · N-A3, `w3_execution_spec_v1.md` §3.3 — **P0 for scene19**]
              #   "scene19 rooftop equipment: `ac_unit_04/05/06` re-tasked as rooftop
              #   plant + PH `utility_box_01/02`, `power_box_01`". The two procedural
              #   0.9 x 0.35 x 0.8 boxes were a **wall-hung 가정용 실외기 silhouette put
              #   on a roof deck**: nothing on a real Korean office rooftop looks like
              #   that. Asset-first (§1.1) replaces them with measured scans:
              #     `exterior_aircon_unit` 1.800 x 0.374 x **0.928** m (zmin −0.320) — the
              #        Korean 실외기 bank, x2 on the existing concrete plinths. **This is a
              #        declared divergence from N-A3's literal `ac_unit_04`, and the reason
              #        is measured, not aesthetic**: `ac_unit_04` is 3.604 x 4.203 x 1.985 m,
              #        and on this 12.5 x 12.5 m deck every siting that clears the pipe run
              #        (y −8.61), the planter box (x 4.5…7.5) and the U_S parapet puts a
              #        **2.1 m** mass — 0.2 m ABOVE the `roof_context` eye at z 1.9 — inside
              #        that cut's sight line to the planter canopy, with a clearance of
              #        0.15 m on the ray to the crown top. Losing a judged cut to fit a named
              #        asset is the wrong trade (§7 ruling 7's posture). `exterior_aircon_unit`
              #        carries **4 MTLX materials** (`…_01`, `…_02`, `…_rusted_01`,
              #        `…_rusted_02`), i.e. the RF-2 age ladder inside one scan.
              #        `ac_unit_04` stays owed for a scene with deck to spare.
              #     `power_box_01` 0.512 x 0.362 x 0.506 m — the 배전함 on the deck beside
              #        the core door. There is **no wall to hang it on**: the L wall's only
              #        surface facing the upper deck is its 1.0 m end face at x = 4, and the
              #        0.9 m door takes all of it — so it stands free on a plinth, which is
              #        what a real 옥상 배전함 does.
              #     `utility_box_01` 0.520 x 0.432 x **1.120** m — the 옥외 배전반 on the
              #        east run. Together these two are G13's transformer/box hardware
              #        vocabulary brought onto the roof, which is the secondary-image job.
              #   All three are CC0 MaterialX rows, so **every one goes through the T4b
              #   wrapper** (`treatment="mtlxoff"`, `w3_t4b_v1.md` **T4b-F1**: a raw CC0 call
              #   site renders **red**; this is library-wide, not a per-asset quirk).
              #   `power_box_01` measures `zmin −0.252` (49.8 % of its height below its own
              #   origin) and `exterior_aircon_unit` `zmin −0.320` (34.5 %), so both are
              #   placed `z_mode="base"` — the scene09 `build_bed_features` precedent.
              plant=dict(
                  ac=[dict(aid="exterior_aircon_unit", cx=12.20, cy=-7.00,
                           yaw=0.0, size=(1.800, 0.374, 0.928)),
                      dict(aid="exterior_aircon_unit", cx=14.20, cy=-7.00,
                           yaw=0.0, size=(1.800, 0.374, 0.928))],
                  plinth_h=0.10, plinth_over=0.10,
                  boxes=[dict(aid="power_box_01", cx=4.90, cy=-1.90, yaw=0.0,
                              size=(0.512, 0.362, 0.506), plinth=0.08),
                         dict(aid="utility_box_01", cx=15.90, cy=2.60,
                              yaw=-90.0, size=(0.432, 0.520, 1.120),
                              plinth=0.08)]),
              vent=dict(cx=8.0, cy=-5.5, r=0.15, h=0.8),
              pipe=dict(x0=5.0, x1=16.0, y=-8.55, r=0.06),
              # position = centre of the L wall south end face (x=4)
              # [GT-82(2)] The leaf was a bare 0.04 m plate on a 1.0 m wide wall end — in
              #   `upper_approach` it is the flat pale slab that fills a third of the frame
              #   with no frame, no reveal and no head. `frame_w/frame_t` add a steel jamb-and-
              #   head set: outer width `w + 2·frame_w` = **1.00** = exactly the wall end face,
              #   so the frame terminates on the wall arris instead of overhanging it, and the
              #   leaf sits 0.02 m back inside the frame face.
              door=dict(w=0.9, h=2.1, frame_w=0.05, frame_t=0.06),
              # [rooftop v4] the rooftop planter position is promoted into PARAMS (single source for
              #   assembly and occlusion checks). The old (11,−6) was 5.9 m in front of the roof_context eye, so the
              #   canopy top was cropped at sy=1.95, outside the top of frame (v6 judgment extra observation (1)).
              #   Pushed to the west end for a 10.8 m viewing distance → sy 0.83, inside the frame.
              #   0.19 m clear of the pipe run (y −8.61..−8.49) and 0.25 m clear of the U_W parapet (x4.25).
              #   canopy_*: the measured upper bound of the tree form that scene_common.build_tree
              #   builds from a coordinate-hash RNG (trunk 2.42 + canopy) — for the occlusion AABB and frame checks.
              #   [W3 L19] Two corrections, both sourced, neither cosmetic.
              #   ① **토심.** `build_planter`'s defaults gave `curb_h 0.45 / grass_h 0.40`,
              #      i.e. **0.40 m of soil** — and the bed carried a 3.24–3.80 m 교목.
              #      조경기준(국토교통부 고시) 제12조 인공지반 조경의 최소 토심: 초화류·
              #      지피식물 0.15 · 소관목 0.30 · 대관목 0.45 · **교목 0.70 m**. A tree on
              #      0.40 m of substrate on a roof deck is not merely unrealistic, it is
              #      below the standard the drawing would have been approved against.
              #      → `curb_h 0.90 / soil_h 0.75`, a raised 옥상 플랜터 box, which is also
              #      what the real thing looks like (a box you can sit on, not a kerb).
              #   ② **수종.** `SCENE_SPECIES["Scene19"]` resolves to `ash` (`Fraxinus.usd`,
              #      native 5.341 m) — the civic street-plaza species, inherited because
              #      `build_planter` does **not** forward `species=` to `build_tree`
              #      (K4(c) signature-preserving; the kit is frozen this window). A 5 m
              #      이팝나무 substitute on an exposed roof is the wrong plant: 옥상조경
              #      uses wind- and shallow-soil-tolerant evergreens. Pinned to
              #      **`juniper`** (`Chinese_Juniper.usd`, native 2.516 m, §10.2 role
              #      "temple / office **evergreen**") by calling `build_tree` directly at
              #      the scene, which is the only scene-side route to `species=`.
              #      An evergreen also makes the bed **season-neutral**, which is the
              #      honest answer for a scene whose season is pinned from an image
              #      (§7 ruling 8) and which must carry neither bloom nor leaf-off.
              #   ③ **관목** pinned to `planter_accent` (`Yew.usd`, 주목) — S-2's "formal
              #      planter accent" row, one species per bed. This removes the last
              #      `Rhododendron` from scene19, so **K4-F1's library-wide magenta loss
              #      cannot show up here at all**; the delta is declared, not discovered.
              #   The tree is seated off-centre at (cx − 0.62, cy + 0.62) because
              #   `build_planter(tree_mtls=None)` puts its third shrub at the bed centre;
              #   교목 offset + 관목 massed is the normal planting layout anyway.
              planter=dict(cx=6.0, cy=-6.8, size=3.0,
                           curb_h=0.90, soil_h=0.75,
                           tree_dx=-0.62, tree_dy=0.62,
                           tree_species="juniper", shrub_species="planter_accent",
                   #   `trunk_h 1.55` makes `build_tree`'s target `1.55 x 1.60 x U(0.92,
                   #   1.08)`; at the pinned coordinate (5.38, −6.18) the deterministic
                   #   draw is **2.5065 m** — i.e. the Juniper is placed at essentially
                   #   its own native 2.516 m (scale 0.9961) instead of being stretched
                   #   1.4x, which is the whole point of matching `trunk_h` to the species.
                   #   Crown top = soil 0.750 + 2.5065 = **3.2565 m**; measured crown
                   #   radius 0.537 m (asset bbox 107.74 x 106.02 x 254.42 asset-units).
                   #   `canopy_top` / `canopy_r` below are the **conservative upper
                   #   bounds** used by the occlusion AABB and the frame checks, per the
                   #   convention the v4 note set (it declared 3.90 against a measured
                   #   3.81). K4-F7 applies: a MASH-instanced species cannot be crown-
                   #   measured from mesh points, so the margin is not decoration.
                           trunk_h=1.55,
                           canopy_top=3.30, canopy_r=0.75)),

    material=dict(
        scale=dict(plaza_light=1.80, plaza_lower=0.8, granite_dark=1.0,
                   concrete_wall=2.0, core_newel=1.2, grass=1.4),
        # [GT-82(2)] The L-core walls and the newel leave `granite_dark`.
        #   [measured] linear texture means — granite_dark 0.0761/0.0768/0.0775 (lum
        #   **0.0767**), concrete_wall 0.2653/0.2366/0.1602 (lum 0.2372, and warm: B/R 0.60).
        #   `core_tint` lands the wall at (0.300, 0.291, 0.260), lum **0.290** — inside the
        #   0.20~0.35 weathered exposed-concrete band, neutral, and one step below the
        #   `parapet_color` 0.40 coping so the hierarchy coping > wall still reads.
        #   `newel_tint` lands the newel at (0.165, 0.160, 0.150), lum **0.159** = 2.08x
        #   granite_dark but still **0.48x** the tread value (plaza_light 0.4627 x 0.72
        #   = 0.333), so the radial convergence datum keeps its contrast without being a
        #   black hole in the middle of the fan.
        core_tint=(1.131, 1.230, 1.623),
        newel_tint=(0.622, 0.676, 0.936),
        lower_warm_tint=(1.06, 1.0, 0.94),
        grass_tint=(0.55, 0.68, 0.42),
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        rail_color=(0.80, 0.82, 0.85), rail_metallic=0.9, rail_rough=0.35,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.025, 0.045, 0.015), canopy_b=(0.035, 0.060, 0.020),
        canopy_rough=1.0,
        # [W2-D · spec §5.6 19-2] The near-white parapet constant is retired.
        #   scene19 is the #1 near-white offender of the whole set and this
        #   single constant is bound to every parapet, guard and gate post in
        #   the scene. Weathered concrete coping measures 0.35~0.45; 0.40 is
        #   the middle and is unambiguously not near-white.
        parapet_color=(0.40, 0.40, 0.385), parapet_rough=0.66,
        # 19-2 coating turn-up: the lower 0.30 m of the parapet's inner face takes the same colour as the deck coat.
        #   The value is the middle of the director-approved M2 band 0.16~0.22 (= ground_kit
        #   GROUND_DIMENSIONS["membrane_albedo"] 0.19), given in green.
        #   [W2 fix batch F1/B3] The bound value was **0.1405 luminance** against the
        #   0.16~0.22 band it cites - below its own declaration, which is why the
        #   membrane collapsed to a single near-black blob in building shadow
        #   (`entry_gate` mean -47, `upper_approach` -57). Rescaled to luminance 0.19,
        #   the declared mid, keeping the green hue exactly.
        coating_color=(0.155, 0.203, 0.162), coating_rough=0.72,
        # [W3 L19 · 19-4] **우레탄 덧방 (repair overcoat)** — its own material, because
        #   binding the patch to `coating` (what HEAD did) makes it invisible: same hue,
        #   same value, same roughness, 2 mm proud. The real tell of a 덧방 on a weathered
        #   deck is that it is *the same product applied again*: identical hue, a fresher
        #   value, and much more sheen because it has not chalked. Value +18 % on the
        #   declared M2 mid (luminance 0.19 → 0.224, still inside the director-approved
        #   0.16~0.22 band's neighbourhood and far from the 0.10~0.16 special-effects
        #   band), hue held exactly (G/R and G/B ratios preserved to 3 decimals);
        #   roughness 0.72 → 0.46, the single strongest cue and the only one that
        #   survives a shadowed frame. `patch_lap` is the feathered coat edge — the same
        #   overcoat brushed thin, one step DOWN in value, never the dark `gk_stain`
        #   saw-cut line (that is the asphalt vocabulary this row exists to remove).
        patch_coat_color=(0.183, 0.240, 0.191), patch_coat_rough=0.46,
        patch_lap_color=(0.132, 0.173, 0.138), patch_lap_rough=0.60,
        nosing_color=(0.85, 0.72, 0.10), nosing_rough=0.7,
        hvac_color=(0.60, 0.61, 0.62), hvac_rough=0.5,      # [rooftop v3] HVAC unit
        # r5 judgment: a dark door was buried in the dark granite wall → painted steel plate in blue-grey for contrast
        door_color=(0.28, 0.30, 0.33), door_rough=0.6,      # [rooftop v3] rooftop steel door
    ),

    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        noon_sun_enable=True, noon_sun_elev=49.79,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    SUN_AZ_OFFSET=171.5,

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


_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene19")


# ===========================================================================
# [C] geometry self-verification — point containment (_solid_at) + sight-line ray marching
#   [v6 judgment §scene19] the 2 re-aimed cuts failed on **occlusion 2 rounds running**. The cause was
#   assuming occlusion by eye alone. The scene08_sunken_plaza `_obstacle_boxes`/
#   `_solid_at` sight-line test is ported and simplified so the check runs on coordinates before rendering.
#   The single source of the coordinates is PARAMS — it reads the same values as the assembly code (no duplicate definitions).
#   Approximation: winder steps and parapet arcs are tested as **annular sectors** instead of the
#   segment boxes of build_arc_steps (they come out slightly smaller than reality by the 1.03x segment-chord
#   margin, which errs toward 'underestimating occlusion' rather than being conservative, so pass verdicts carry a safety margin).
# ===========================================================================
def _step_top(i):
    """[rooftop v3] sectors 0..kite_n-1 = the kite landing (same top face −riser).
    The remaining (n−kite_n) steps divide (total drop−riser) evenly → total drop n·riser unchanged."""
    w = PARAMS["winder"]
    kn = int(w.get("kite_n", 0))
    if kn <= 0 or i < kn:
        if kn <= 0:
            return -w["riser"] * (i + 1)
        return -w["riser"]
    rem = (w["riser"] * w["n"] - w["riser"]) / (w["n"] - kn)
    return -w["riser"] - rem * (i - kn + 1)


# ---------------------------------------------------------------------------
# [W3 L19 · GT-41] The K4(d) split proof, run in the scene's own smoke check.
#   GT-6's acceptance test is "a prim-hash / GT-delta diff … proven, not asserted".
#   For scene19 the two conventions differ **only** in which azimuth a tread owns, so
#   the honest instrument is a walked-top-face sampler over the annulus that evaluates
#   both conventions from the same PARAMS and classifies every differing sample.
#   GPU 0, no boot, ~0.6 s.
# ---------------------------------------------------------------------------
def _arc_top_box(x, y):
    """Top face of the winder step **boxes** (the pre-K4(d) convention) at (x, y)."""
    w = PARAMS["winder"]
    cx, cy = PARAMS["center"]["cx"], PARAMS["center"]["cy"]
    dth = math.radians(w["sector_deg"] / float(w["seg"]))
    half = w["r_out"] * math.sin(dth / 2.0) * 1.03      # = chord/2
    radial, r_mid = w["r_out"] - w["r_in"], (w["r_in"] + w["r_out"]) / 2.0
    dx, dy, best = x - cx, y - cy, None
    for i in range(w["n"]):
        for k in range(w["seg"]):
            a_mid = math.radians(w["a0"] + i * w["sector_deg"]) + (k + 0.5) * dth
            ca, sa = math.cos(a_mid), math.sin(a_mid)
            lx, ly = dx * ca + dy * sa - r_mid, -dx * sa + dy * ca
            if abs(lx) <= radial / 2.0 and abs(ly) <= half:
                t = _step_top(i)
                best = t if best is None or t > best else best
    return best


def _arc_top_mesh(x, y):
    """Top face of the winder step **true annular sectors** (K4(d)) at (x, y)."""
    w = PARAMS["winder"]
    cx, cy = PARAMS["center"]["cx"], PARAMS["center"]["cy"]
    dx, dy = x - cx, y - cy
    r = math.hypot(dx, dy)
    if not (w["r_in"] <= r <= w["r_out"]):
        return None
    a = math.degrees(math.atan2(dy, dx)) % 360.0
    if not (w["a0"] <= a <= w["a0"] + w["n"] * w["sector_deg"]):
        return None
    return _step_top(min(int((a - w["a0"]) / w["sector_deg"]), w["n"] - 1))


def _arc_split_proof(nr=57, na=3601):
    """GT-41's split proof. Returns (samples, strata, new_void, new_solid, per_boundary).

    The winder steps are *not* the only solid over the annulus — the L walls, the newel,
    the corner slab and the threshold all bid for the same (x, y). The walked surface is
    the max of the two, which is why the a0/a1 ends come out clean: the box overshoot
    past 0° and 90° falls **inside** `Wall_south` / `Wall_west` (`z_top` 3.5), so it can
    never win a top face. GT-29 had to declare that term for scene06 because scene06's
    landing ray overshot into open air; here it is proved absent rather than assumed.
    """
    w = PARAMS["winder"]
    nw, up, lo = PARAMS["newel"], PARAMS["upper"], PARAMS["lower"]
    wl, ac = PARAMS["walls"], PARAMS["access"]
    co, th, gd = ac["corner"], ac["threshold"], ac["guard"]

    def other(x, y):
        c = []
        if math.hypot(x - PARAMS["center"]["cx"],
                      y - PARAMS["center"]["cy"]) <= nw["r"]:
            c.append(nw["z_top"])
        for tag in ("south", "west"):
            b = wl[tag]
            if b["x0"] <= x <= b["x1"] and b["y0"] <= y <= b["y1"]:
                c.append(wl["z_top"])
        if co["x0"] <= x <= co["x1"] and co["y0"] <= y <= co["y1"]:
            c.append(lo["top_z"])
        if th["x0"] <= x <= up["x0"] and th["y0"] <= y <= th["y1"]:
            c.append(up["top_z"])
        if gd["x0"] <= x <= gd["x1"] and gd["y0"] <= y <= gd["y1"]:
            c.append(gd["h_top"])
        if x >= up["x0"]:
            c.append(up["top_z"])
        if y >= lo["y1"] - 13.0 and x <= lo["x1"]:
            c.append(lo["top_z"])
        return max(c) if c else None

    def walked(x, y, fn):
        s, o = fn(x, y), other(x, y)
        if s is None:
            return o
        return s if o is None else max(s, o)

    span = w["n"] * w["sector_deg"]
    r0, r1 = w["r_in"] - 0.10, w["r_out"] + 0.10
    a0, a1 = w["a0"] - 4.0, w["a0"] + span + 4.0
    strata, per = {}, {}
    n_tot = nv = ns = 0
    for ir in range(nr):
        r = r0 + (r1 - r0) * ir / (nr - 1)
        for ia in range(na):
            a = a0 + (a1 - a0) * ia / (na - 1)
            x, y = r * math.cos(math.radians(a)), r * math.sin(math.radians(a))
            zb = walked(x, y, _arc_top_box)
            zm = walked(x, y, _arc_top_mesh)
            n_tot += 1
            if zb is None and zm is None:
                continue
            if zb is None:
                ns += 1
                continue
            if zm is None:
                nv += 1
                continue
            if abs(zm - zb) < 1e-9:
                continue
            strata[round((zm - zb) * 1000.0, 3)] = \
                strata.get(round((zm - zb) * 1000.0, 3), 0) + 1
            b = min(range(w["n"] + 1),
                    key=lambda i: abs(a - (w["a0"] + i * w["sector_deg"])))
            per[b] = per.get(b, 0) + 1
    return n_tot, strata, nv, ns, per


# ---------------------------------------------------------------------------
# [W3 L19 · §7 ruling 8] Seasonal audit — every scene pins the season of its
#   governing image and audits its own dressing against it. scene19 is imageless and
#   rides **G8** (`w3_intake_v2_images.md` §4 Lane 3 row 3.7), whose read is
#   **summer, high sun, clear sky**. The audit asserts, rather than states, that
#   nothing in the scene carries a competing seasonal cue.
# ---------------------------------------------------------------------------
SCENE_SEASON = "summer"          # inherited from G8 (nearest image, Lane-3 3.7)


def _season_audit():
    """Print the seasonal ledger and return the list of violations."""
    import scene_common as _sc
    rf = PARAMS["roof"]
    pl = rf["planter"]
    bad = []
    rows = []
    # 1. the only vegetation in the scene
    tree = _sc.resolve_species("/World/Scene19/Planter_A",
                               species=pl["tree_species"])[0]
    rows.append(("교목", tree, "상록 (계절 중립)"
                 if "Juniper" in tree or "Fir" in tree or "Spruce" in tree
                 else "낙엽 — 계절 표기 필요"))
    if not ("Juniper" in tree or "Fir" in tree or "Spruce" in tree):
        bad.append(f"tree {tree} is deciduous under a summer pin")
    shr = _sc.SHRUB_SPECIES.get(pl["shrub_species"], [])
    rows.append(("관목", ", ".join(shr) or "(none)",
                 f"1종/화단 = {len(shr)}"))
    if len(shr) != 1:
        bad.append(f"shrub role {pl['shrub_species']} is not single-species")
    for s in shr:
        if s in _sc.SEASONAL_SUBPRIMS:
            bad.append(f"{s} carries a seasonal sub-prim ({_sc.SEASONAL_SUBPRIMS[s]})")
    # 2. leaf-off must not be reachable
    rows.append(("bare=", "호출 없음", "낙엽기 표현 0"))
    # 3. no seasonal scatter: the roof profile's debris pool
    rows.append(("낙엽 스캐터", "roof_membrane 프로파일", "지붕 도막 — 낙엽 처방 없음"))
    print("  [계절 감사] 기준 이미지 G8 = 여름·고각 태양·맑음 → "
          f"SCENE_SEASON={SCENE_SEASON}")
    for a, b, c in rows:
        print(f"    {a:12s} {b:44s} {c}")
    print(f"    → {'OK' if not bad else 'FAIL ' + str(bad)}")
    return bad


_BOXES_CACHE = [None]


def _solid_boxes():
    """Obstacle AABB list (name, x0,x1, y0,y1, z0,z1) — the same coordinates as the assembly code.
    Arcs (winder steps, parapet) and the cylinder (newel) are tested separately, in polar coordinates, in _solid_at."""
    if _BOXES_CACHE[0] is not None:
        return _BOXES_CACHE[0]
    up, lo, gr = PARAMS["upper"], PARAMS["lower"], PARAMS["ground"]
    ac, wl, rf = PARAMS["access"], PARAMS["walls"], PARAMS["roof"]
    base = gr["top_z"]
    t, h, hi = rf["pp_t"], rf["pp_h"], rf["pp_h_inner"]
    th, gd, co = ac["threshold"], ac["guard"], ac["corner"]
    B = [
        ("Ground", gr["x0"], gr["x1"], gr["y0"], gr["y1"], base - 1.0, base),
        ("Walk_upper", up["x0"], up["x1"], up["y0"], up["y1"], base,
         up["top_z"]),
        ("Walk_lower", lo["x0"], lo["x1"], lo["y0"], lo["y1"], base,
         lo["top_z"]),
        ("CornerSlab", co["x0"], co["x1"], co["y0"], co["y1"], base,
         lo["top_z"]),
        ("Threshold", th["x0"], up["x0"], th["y0"], th["y1"], lo["top_z"],
         up["top_z"]),
        ("EdgeGuard", gd["x0"], gd["x1"], gd["y0"], gd["y1"], lo["top_z"],
         gd["h_top"]),
    ]
    # [GT-82(3)] The AABB top is the **coping** top, not the wall top. The 0.08 m coping
    #   overhang is deliberately NOT added to x/y: the wall footprint is flush with the
    #   winder's a0/a1 radial edges, so widening it here would swallow an 0.08 m sliver of
    #   Step_0 in every scan. Erring toward under-occlusion is this section's stated rule.
    for tag in ("south", "west"):
        b = wl[tag]
        B.append((f"Wall_{tag}", b["x0"], b["x1"], b["y0"], b["y1"],
                  wl["z_bot"], wl["z_top"] + wl["cap_t"]))
    # 7 rooftop parapet runs (same z as pp() in build_rooftop: base−0.05 .. base+hh)
    for tag, x0, x1, y0, y1, bz, hh in (
            ("U_E", up["x1"] - t, up["x1"], up["y0"], up["y1"], up["top_z"], h),
            ("U_S", up["x0"], up["x1"] - t, up["y0"], up["y0"] + t,
             up["top_z"], h),
            ("U_W", up["x0"], up["x0"] + t, up["y0"] + t, -1.0, up["top_z"], h),
            ("U_N", up["x0"], up["x1"], up["y1"] - t, up["y1"], up["top_z"],
             hi),
            ("L_W", lo["x0"], lo["x0"] + t, lo["y0"], lo["y1"], lo["top_z"], h),
            ("L_N", lo["x0"] + t, lo["x1"], lo["y1"] - t, lo["y1"],
             lo["top_z"], h),
            ("L_E", lo["x1"] - t, lo["x1"], lo["y0"], lo["y1"] - t,
             lo["top_z"], h)):
        B.append((f"RoofPP_{tag}", x0, x1, y0, y1, bz - 0.05, bz + hh))
    # plant, rooftop door, planter (approximated including the canopy)
    # [W3 L19 · N-A3] The two procedural boxes became two `exterior_aircon_unit` scans on
    #   the same plinths; the AABB is the asset's measured footprint + the plinth overhang,
    #   so the occlusion test still reads the same coordinates the assembly uses.
    pl_h, pl_o = rf["plant"]["plinth_h"], rf["plant"]["plinth_over"]
    for i, u in enumerate(rf["plant"]["ac"]):
        sx, sy, sz = u["size"]
        B.append((f"Hvac_{i}", u["cx"] - sx / 2 - pl_o, u["cx"] + sx / 2 + pl_o,
                  u["cy"] - sy / 2 - pl_o, u["cy"] + sy / 2 + pl_o,
                  up["top_z"], up["top_z"] + pl_h + sz))
    for u in rf["plant"]["boxes"]:
        sx, sy, sz = u["size"]
        B.append((f"Plant_{u['aid']}", u["cx"] - sx / 2 - 0.06,
                  u["cx"] + sx / 2 + 0.06, u["cy"] - sy / 2 - 0.06,
                  u["cy"] + sy / 2 + 0.06, up["top_z"],
                  up["top_z"] + u["plinth"] + sz))
    v = rf["vent"]
    B.append(("Vent", v["cx"] - v["r"], v["cx"] + v["r"] * 2.2,
              v["cy"] - v["r"], v["cy"] + v["r"], up["top_z"],
              up["top_z"] + v["h"] + v["r"]))
    p = rf["pipe"]
    B.append(("PipeRun", p["x0"], p["x1"], p["y"] - p["r"], p["y"] + p["r"],
              up["top_z"] + 0.02, up["top_z"] + 0.02 + 2 * p["r"]))
    # [GT-82(2)] the AABB is the **frame** outer face (x1 + frame_t) and the frame outer
    #   width (w + 2·frame_w), which is what a sight line now meets.
    d, ws = rf["door"], wl["south"]
    d_half = d["w"] / 2 + d["frame_w"]
    B.append(("CoreDoor", ws["x1"], ws["x1"] + d["frame_t"],
              (ws["y0"] + ws["y1"]) / 2 - d_half,
              (ws["y0"] + ws["y1"]) / 2 + d_half, up["top_z"],
              up["top_z"] + d["h"] + d["frame_w"]))
    pl = rf["planter"]
    # [W3 L19] the crown is now off-centre, so the AABB is the union of the box and the
    #   crown disc rather than one square about the bed centre.
    tx, ty = pl["cx"] + pl["tree_dx"], pl["cy"] + pl["tree_dy"]
    hb, cr = pl["size"] / 2.0, pl["canopy_r"]
    B.append(("Planter_A", min(pl["cx"] - hb, tx - cr), max(pl["cx"] + hb, tx + cr),
              min(pl["cy"] - hb, ty - cr), max(pl["cy"] + hb, ty + cr),
              0.0, pl["canopy_top"]))
    # [GT-82(1)] the `Bldg*` / `Bldg*_roof` rows are gone with the buildings themselves.
    _BOXES_CACHE[0] = B
    return B


def _solid_at(x, y, z):
    """Name of the solid containing the point (x,y,z) (None if there is none).
    The single source for the camera-eye-buried and sight-line-blocked (ray march) tests."""
    for nm, x0, x1, y0, y1, z0, z1 in _solid_boxes():
        if x0 <= x <= x1 and y0 <= y <= y1 and z0 <= z <= z1:
            return nm
    cx, cy = PARAMS["center"]["cx"], PARAMS["center"]["cy"]
    w, ac, pp = PARAMS["winder"], PARAMS["access"], PARAMS["parapet"]
    nw = PARAMS["newel"]
    dx, dy = x - cx, y - cy
    r = math.hypot(dx, dy)
    if r <= nw["r"] and nw["z_bot"] <= z <= nw["z_top"]:
        return "Newel"
    a = math.degrees(math.atan2(dy, dx)) % 360.0
    span = w["n"] * w["sector_deg"]
    if w["a0"] <= a <= w["a0"] + span:
        i = min(int((a - w["a0"]) / w["sector_deg"]), w["n"] - 1)
        top = _step_top(i)
        if w["r_in"] <= r <= w["r_out"] and w["base_z"] <= z <= top:
            return f"Step_{i}"
        # parapet arc ring + top handrail (+0.06) as one band
        if ac["parapet_first"] <= i <= ac["parapet_last"] \
                and pp["r_in"] <= r <= pp["r_out"] \
                and top - 0.1 <= z <= top + pp["h"] + 0.06:
            return f"Parapet_{i}"
    # [GT-82(4)] the two end piers reach `lead` deg **past** the retained span, so they fall
    #   outside the loop above and would otherwise be invisible to the white-mass gate —
    #   which is the one number the entry/exit widening is judged on. They are tested here
    #   against their own radii and their own crown (`pp.h + rise`).
    ep = ac["end_pier"]
    for a_end, lo_d, hi_d, i_ref in (
            (w["a0"] + ac["parapet_first"] * w["sector_deg"],
             -ep["lead"], ep["span"] - ep["lead"], ac["parapet_first"]),
            (w["a0"] + (ac["parapet_last"] + 1) * w["sector_deg"],
             ep["lead"] - ep["span"], ep["lead"], ac["parapet_last"])):
        top = _step_top(i_ref)
        if a_end + lo_d <= a <= a_end + hi_d \
                and ep["r_in"] <= r <= ep["r_out"] \
                and top - ep["drop"] <= z <= top + pp["h"] + ep["rise"]:
            return f"Parapet_end{i_ref}"
    return None


def _ray_hit(eye, dirv, step=0.1, tmax=80.0):
    """March from eye along dirv (unit) in steps of step — (distance, solid name|None)."""
    for k in range(1, int(tmax / step) + 1):
        t = k * step
        s = _solid_at(eye[0] + dirv[0] * t, eye[1] + dirv[1] * t,
                      eye[2] + dirv[2] * t)
        if s is not None:
            return t, s
    return tmax, None


def _cam_basis(eye, tgt, hfov=60.0, aspect=16.0 / 9.0):
    """(eye, forward, right, up, tan(hfov/2), tan(vfov/2)) — 1920×1080 = 60°."""
    e = np.array(eye, dtype=float)
    f = np.array(tgt, dtype=float) - e
    f /= np.linalg.norm(f)
    rt = np.cross(f, np.array([0.0, 0.0, 1.0]))
    rt /= np.linalg.norm(rt)
    th = math.tan(math.radians(hfov / 2.0))
    return e, f, rt, np.cross(rt, f), th, th / aspect


def _screen_uv(eye, tgt, p):
    """Normalised screen coordinates of the world point p (sx, sy, whether it is in frame). |s|<=1 = in frame."""
    e, f, rt, uu, th, tv = _cam_basis(eye, tgt)
    v = np.array(p, dtype=float) - e
    d = float(v @ f)
    if d <= 1e-6:
        return None, None, False
    sx, sy = float(v @ rt) / d / th, float(v @ uu) / d / tv
    return sx, sy, (abs(sx) <= 1.0 and abs(sy) <= 1.0)


def _frame_scan(eye, tgt, nx=21, ny=12, step=0.12, tmax=80.0, face=False):
    """Scan the viewport (1920x1080 = 60 deg horizontal FOV) sparsely with nx x ny rays.
    Returns: {solid name: screen occupancy %} — no contact is '<SKY>'.
    With face=True the winder steps are split into `Step_i:tread` / `Step_i:riser` (if the hit point z
    equals that step's top face it is the tread, otherwise the riser face) — for reading ascending sight-line cuts.
    *The convention answering the v6 judgment 'occlusion-check failures recur': after re-aiming, always run
     ray casting through this function, including every parapet member.*"""
    e, f, rt, uu, th, tv = _cam_basis(eye, tgt)
    cnt = {}
    for iy in range(ny):
        sy = (1.0 - (iy + 0.5) * 2.0 / ny) * tv
        for ix in range(nx):
            sx = ((ix + 0.5) * 2.0 / nx - 1.0) * th
            d = f + sx * rt + sy * uu
            d /= np.linalg.norm(d)
            t, s = _ray_hit(e, d, step, tmax)
            k = s if s is not None else "<SKY>"
            if face and k.startswith("Step_"):
                zh = e[2] + d[2] * t
                k += ":tread" if abs(zh - _step_top(int(k.split("_")[1]))) \
                    <= step else ":riser"
            cnt[k] = cnt.get(k, 0) + 1
    tot = float(nx * ny)
    return {k: 100.0 * v / tot for k, v in cnt.items()}


def _pct(scan, *prefixes):
    return sum(v for k, v in scan.items() if k.startswith(prefixes))


# ---------------------------------------------------------------------------
# [GT-82(4)] Entry / exit clear width, measured at the outer arc rather than asserted.
#   The opening is bounded by the end pier's leading edge on one side and by the L wall face
#   (a0 = the y=0 face, a1 = the x=0 face) on the other, so the honest quantity is the chord
#   between those two points at r_out. 1.20 m is the stair clear-width floor this project
#   works to; the entry also has to stay wide enough that the kite landing is not a slot.
# ---------------------------------------------------------------------------
_CLEAR_MIN = 1.20


def _clear_widths():
    """(entry, exit) clear width [m], printed with the 1.20 m gate.

    entry = the throat at the first nosing line `threshold.x0`. South bound is the a0 wall
      face (y = 0); north bound is whichever comes first of the edge guard's south face
      (`threshold.y1`) and the entry pier's leading ray — the pier is at r 3.78..4.09 and
      that ray crosses x0 inside that band, so it is a real obstruction, not a notional one.
    exit  = the chord of the **open** outer arc, from the exit pier's leading ray to the a1
      wall face, at r_out — this is the gap a descender steps out through onto the wedge.
    """
    w, ac = PARAMS["winder"], PARAMS["access"]
    ro, ep = w["r_out"], ac["end_pier"]
    th, gd = ac["threshold"], ac["guard"]
    a_in = w["a0"] + ac["parapet_first"] * w["sector_deg"] - ep["lead"]
    a_out = w["a0"] + (ac["parapet_last"] + 1) * w["sector_deg"] + ep["lead"]
    a_end = w["a0"] + w["n"] * w["sector_deg"]
    y_pier = th["x0"] * math.tan(math.radians(a_in))
    r_pier = th["x0"] / math.cos(math.radians(a_in))
    if not (ep["r_in"] <= r_pier <= ep["r_out"]):
        y_pier = float("inf")                  # the pier ray misses the nosing line
    entry = min(gd["y0"] - th["y0"], y_pier)
    p0 = (ro * math.cos(math.radians(a_out)), ro * math.sin(math.radians(a_out)))
    p1 = (ro * math.cos(math.radians(a_end)), ro * math.sin(math.radians(a_end)))
    exit_ = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    ok = min(entry, exit_) >= _CLEAR_MIN
    print(f"  진입/탈출 유효폭 입구 {entry:.3f} m "
          f"(x {th['x0']:.2f} 코선 · 벽면 y0 ~ 가드/피어 {min(gd['y0'], y_pier):.3f}) · "
          f"출구 {exit_:.3f} m ({a_out:.1f}~{a_end:.1f}° 개방호 현) → "
          f"{'OK' if ok else 'FAIL'} (기준 ≥{_CLEAR_MIN:.2f} m)")
    return entry, exit_


def _sun_dir():
    """Unit vector toward the sun, from the same PARAMS the stage lighting reads.

    `setup_lighting` authors the DistantLight as `[rotateZ, rotateX]`; USD applies the list in
    reverse, so rotX(90 − elev) tilts the emit direction off −Z first and rotZ swings it. The
    dome/sun azimuth is `noon_dome_rot + SUN_AZ_OFFSET + hdri_sun_rotz_offset`.
    """
    lp = PARAMS["light"]
    rz = math.radians(lp["noon_dome_rot"] + PARAMS["SUN_AZ_OFFSET"]
                      + lp["hdri_sun_rotz_offset"])
    rx = math.radians(90.0 - lp["noon_sun_elev"])
    ey, ez = math.sin(rx), -math.cos(rx)          # emit dir after rotX, from (0,0,−1)
    ex2 = -ey * math.sin(rz)
    ey2 = ey * math.cos(rz)
    return -ex2, -ey2, -ez                        # toward the sun


def _shadow_reach():
    """[GT-82(3)] How far the L-core crown throws its shadow onto the winder.

    The winder is the only thing under it, so this is the number the "too dark near the
    stairs" verdict is about. Offset per metre of height = (−Sx/Sz, −Sy/Sz).
    """
    sx, sy, sz = _sun_dir()
    kx, ky = -sx / sz, -sy / sz
    az = math.degrees(math.atan2(sx, sy)) % 360.0
    wl, w = PARAMS["walls"], PARAMS["winder"]
    z_low = _step_top(w["n"] - 1)                 # lowest tread
    crown = wl["z_top"] + wl["cap_t"]
    reach_x = (crown - z_low) * kx                # west wall (x=0 face) → +x
    reach_y = (crown - (-w["riser"])) * ky        # south wall (y=0) → kite landing
    print(f"  태양 az {az:.1f}° · elev {PARAMS['light']['noon_sun_elev']:.2f}° → "
          f"그림자 {kx:+.3f}x/{ky:+.3f}y per m")
    print(f"    서측 코어 마루 {crown:+.2f} → 최하단 디딤({z_low:+.2f})에서 x {reach_x:.2f} "
          f"(r_out {w['r_out']:.2f} 중 {max(0.0, w['r_out'] - reach_x):.2f} m 채광) · "
          f"남측 코어 → 카이트 랜딩에서 y {reach_y:.2f} "
          f"(랜딩 폭 {PARAMS['access']['threshold']['y1']:.2f} 중 "
          f"{max(0.0, PARAMS['access']['threshold']['y1'] - reach_y):.2f} m 채광)")
    return reach_x, reach_y


def _geom_report():
    """Pre-boot geometry and camera self-verification (NEGOBS_SMOKE=1)."""
    views = build_views()
    up = PARAMS["upper"]
    print("=" * 70)
    print("scene19_fan_winder — SMOKE 기하 자기검증 (부팅 전)")
    print("=" * 70)
    print(f"  총낙차 {abs(_step_top(PARAMS['winder']['n'] - 1)):.2f} m "
          f"(카이트 {PARAMS['winder']['kite_n']}섹터 + 잔여 "
          f"{PARAMS['winder']['n'] - PARAMS['winder']['kite_n']}단) — 불변 검사")
    _clear_widths()
    _shadow_reach()

    # ---- [W3 L19 · GT-41] K4(d) split proof -------------------------------
    w = PARAMS["winder"]
    n_tot, strata, nv, ns, per = _arc_split_proof()
    riser_mm = round((_step_top(w["kite_n"] - 1)
                      - _step_top(w["kite_n"])) * 1000.0, 3)
    n_diff = sum(strata.values())
    print(f"  [GT-41 분할증명] mesh={w['mesh']} · 표본 {n_tot} · 상이 {n_diff} "
          f"({100.0 * n_diff / n_tot:.2f} %) · new-void {nv} · new-solid {ns}")
    for d, c in sorted(strata.items(), key=lambda kv: -kv[1]):
        print(f"    {d:+10.3f} mm  n={c}")
    lone = (len(strata) == 1 and abs(list(strata)[0] + riser_mm) < 1e-3
            and nv == 0 and ns == 0)
    print(f"    단 하나의 계층 = 정확히 −1 라이저({riser_mm:.3f} mm) · "
          f"디딤면 z 이동 0 → {'OK' if lone else 'FAIL'}")
    ends = [b for b in per if b in (0, w["n"])]
    kite = [b for b in per if 1 <= b <= w["kite_n"] - 1]
    print(f"    인계 경계 {sorted(b for b in per)} · a0/a1 끝단 {ends} "
          f"(L 벽에 매몰) · 카이트 경계 {kite} (라이저 0) → "
          f"{'OK' if not ends and not kite else 'FAIL'}")

    _season_audit()

    hits = [(n, _solid_at(*v["eye"])) for n, v in sorted(views.items())]
    hits = [(n, s) for n, s in hits if s is not None]
    for n, s in hits:
        print(f"    [FAIL] {n} eye 가 {s} 내부(매몰)")
    print(f"  [eye 매몰] {len(hits)}건 → {'OK' if not hits else 'FAIL'}")

    print("  [프레임 레이마칭] 21×12 광선 · 60° 수평화각")
    # [GT-82(1)] roof_skyline keeps its eye/tgt — only the **gate** is re-based. With
    #   building E deleted the cut can no longer carry a below-eye-height scale anchor, and
    #   pretending otherwise would be the same "checked by eye" failure the v4 note records.
    #   What the cut still has to prove is the thing that makes it a *rooftop*: the north
    #   parapet crown in the near field and, past it, the ground **6 m below** (upper deck 0.0
    #   vs `ground.top_z` −6.0). Both must be present; the drop is the depth cue.
    v = views["roof_skyline"]
    sc_sky = _frame_scan(v["eye"], v["tgt"])
    p_gnd = _pct(sc_sky, "Ground")
    p_pp = _pct(sc_sky, "RoofPP")
    print(f"    roof_skyline  eye{tuple(v['eye'])} → tgt{tuple(v['tgt'])}")
    for k in sorted(sc_sky, key=lambda k: -sc_sky[k])[:6]:
        print(f"      {k:16s} {sc_sky[k]:5.1f}%")
    ok_sky = p_gnd >= 4.0 and p_pp >= 3.0
    print(f"      6 m 아래 지반 {p_gnd:.1f}% (≥4) · 옥상 파라펫 {p_pp:.1f}% (≥3) → "
          f"{'OK' if ok_sky else 'FAIL'} (배경 건물 없음 = GT-82(1))")

    def _stair_cut(name, min_step, min_tier, max_white):
        v = views[name]
        sc_ = _frame_scan(v["eye"], v["tgt"], tmax=20.0, step=0.03, face=True)
        steps_ = _pct(sc_, "Step_")
        riser = sum(val for k, val in sc_.items() if k.endswith(":riser"))
        tiers = sorted({int(k.split("_")[1].split(":")[0])
                        for k, val in sc_.items()
                        if k.startswith("Step_") and val >= 0.4})
        white_ = _pct(sc_, "Parapet_", "RoofPP", "EdgeGuard", "Threshold")
        print(f"    {name:13s} eye{tuple(v['eye'])} → tgt{tuple(v['tgt'])}")
        print(f"      단 점유 {steps_:.1f}%(라이저 {riser:.1f} / 디딤 "
              f"{steps_ - riser:.1f}) · 시인 단 {len(tiers)}/"
              f"{PARAMS['winder']['n']} {tiers} · 뉴얼 "
              f"{sc_.get('Newel', 0.0):.1f}% · 백색 매스 {white_:.1f}%")
        ok = (steps_ >= min_step and len(tiers) >= min_tier
              and white_ <= max_white)
        print(f"      → {'OK' if ok else 'FAIL'} (기준 단≥{min_step:.0f}% · "
              f"시인≥{min_tier}단 · 백색≤{max_white:.0f}%)")

    # radial_nosing = descending down-view (mostly treads) / lower_lookup = ascending up-view (risers)
    _stair_cut("radial_nosing", 60.0, 8, 5.0)
    _stair_cut("lower_lookup", 60.0, 6, 5.0)

    v = views["roof_context"]
    rf = PARAMS["roof"]
    pl, hv = rf["planter"], rf["plant"]["ac"]
    probes = [("수관 정상", (pl["cx"] + pl["tree_dx"], pl["cy"] + pl["tree_dy"],
                             pl["canopy_top"])),
              ("화단 연석 상단", (pl["cx"], pl["cy"] + pl["size"] / 2.0,
                                  pl["curb_h"]))]
    for i, u in enumerate(hv):
        probes.append((f"실외기{i}", (u["cx"], u["cy"],
                                      rf["plant"]["plinth_h"] + u["size"][2])))
    probes += [("환기구", (rf["vent"]["cx"], rf["vent"]["cy"], 0.8)),
               ("배관", (10.0, rf["pipe"]["y"], 0.14)),
               ("남 파라펫 상단", (10.0, PARAMS["upper"]["y0"] + 0.12,
                                   rf["pp_h"]))]
    print(f"    roof_context  eye{tuple(v['eye'])} → tgt{tuple(v['tgt'])}")
    bad = []
    for nm, p in probes:
        sx, sy, ok = _screen_uv(v["eye"], v["tgt"], p)
        print(f"      {nm:14s} sx {sx:+.2f} sy {sy:+.2f} → "
              f"{'프레임 안' if ok else '프레임 밖'}")
        if not ok:
            bad.append(nm)
    print(f"      → {'OK' if not bad else 'FAIL ' + str(bad)} "
          f"(수관 잘림 0 · 설비 클러스터 전원 프레임 안)")

    print("  [미장센 시선축 첫 접촉]")
    for n in ("upper_approach", "winder_mid", "lower_lookup", "entry_gate",
              "roof_context", "radial_nosing", "roof_skyline"):
        v = views[n]
        e = np.array(v["eye"], float)
        d = np.array(v["tgt"], float) - e
        L = float(np.linalg.norm(d))
        t, s = _ray_hit(e, d / L, 0.05, L * 3.0)
        print(f"    {n:16s} t={t:5.2f} ({L:5.2f} 까지 tgt) → "
              f"{s if s else '무접촉(지평/하늘)'}")
    print("=" * 70)


# ===========================================================================
# [D] camera presets — grid_views mirrored about x=6 (upper approach axis) + 4 mise-en-scene cuts
# ===========================================================================
def build_views():
    """Preset axis = the upper approach direction. grid_views (gazing +X) is mirrored about x=6 to
    convert it into the axis that looks down the winder descent toward −X from the upper sidewalk (+X, z=0)."""
    # [rooftop v3] xref 6.0→5.8: after mirroring, d5 eye x=17.0 fell inside the east rooftop parapet (16.75~17,
    #   h1.2), blacking out the whole h0.3/0.9_d5 frame → moved inward to 16.6.
    #   d10 (21.6) is kept as an off-roof hover cut = the "rooftop seen from outside" context cut.
    xref = 5.8
    # [v5 judgment] d10 (x21.6 after mirroring) is empty air off the roof — a viewpoint no pedestrian
    #   can occupy, which invalidated 1/3 of the grid. Replaced with physically possible on-roof distances (2, 3.5, 5).
    v = sc.grid_views(0.0, dists=(2, 3.5, 5))
    out = {}
    for k, val in v.items():
        e, t = list(val["eye"]), list(val["tgt"])
        e[0] = 2.0 * xref - e[0]                # mirror → camera on the +X side, gazing −X
        t[0] = 2.0 * xref - t[0]
        out[k] = dict(eye=e, tgt=t)
    out["upper_approach"] = dict(eye=[9.0, -1.0, 1.0], tgt=[1.0, 2.0, -1.2])
    # [v5 judgment] the winder_mid and lower_lookup compositions sat outside the parapet, so the fan
    #   steps were entirely hidden (0 step sightings across 15 cuts). Re-aimed to a viewpoint **inside** the stair corridor:
    #   walk line r~2.6, entry (angle 11 deg) → exit (angle 79 deg).
    #   winder_mid: looking down the fan descent from above the kite landing (the entry shoulder)
    out["winder_mid"]     = dict(eye=[3.4, 0.9, 1.3],  tgt=[1.1, 2.4, -1.3])
    # [rooftop v4 / v6 judgment extra observation] lower_lookup re-aimed. The old eye(0.9,4.4,−0.35) stood
    #   on the lower sidewalk looking at the parapet ring **head-on** — the sight-line axis was
    #   blocked by `Parapet_9` 0.60 m ahead and the white parapet filled 54.1 % of the frame
    #   (matching the v6 judgment "left half → 55 %"). The "corner slab" only has width near angle 45 deg
    #   in the first place, and that span is exactly the parapet-retained span (22.5~75 deg), so it was a
    #   structurally impossible spot. → replaced by stepping down **onto the last step of the descent (sector 10)**
    #   and looking back up the fan (the parapet ring falls behind the sight line).
    #   eye polar r 3.40 / angle 80.0 deg (sector 10, top face −1.617), eye height 1.60 m above it.
    #   [_frame_scan check] steps 88.8 % (**riser 41.8 / tread 47.0** — an ascending sight line, so the
    #   riser faces are exposed in alternation) · 8 steps sighted (sector 2~9) · white mass 0.0 % ·
    #   newel 11.2 % (the radial convergence datum) · dark L wall 0.1 %.
    #   [W3 L19 · doc drift corrected] the "8 steps (sector 2~9)" line above is **stale** and was
    #   already stale at HEAD: re-run on the untouched tree the check reports **7/12, sectors
    #   3~9**. The gate is `>= 6`, so it passed either way and nobody re-read it. Annotated in
    #   place rather than rewritten (GT-6's precedent); the live number is what `_geom_report`
    #   prints, not what this comment claims.
    out["lower_lookup"]   = dict(eye=[0.59, 3.35, -0.02], tgt=[1.55, 1.55, -0.9])
    # [rooftop v4 / v6 judgment (2)] the old eye(5.2,0.7,1.5) sat inside the L wall and edge guard, so no
    #   tgt could avoid the white mass (0 fan steps visible). Following the judgment's recommendation it
    #   moves to **near the successful winder_mid = above the kite landing** and tgt drops to the
    #   foot of the newel. eye is 1.60 m of eye height above the kite top face (−0.15), polar
    #   r 3.15 / angle 17.6 deg (sector 2 = the kite) → tgt r 1.73 / angle 56.8 deg (sector 7),
    #   depression 57 deg. [_frame_scan check] steps 84.9 % · all 12/12 steps sighted (per step
    #   1.8~13.4 %) · newel 5.7 % (the radial convergence datum point) · parapet/rail/guard/threshold/
    #   gate post 0.0 % · dark L wall 8.3 % (1/3 of winder_mid's 22.5 %).
    out["radial_nosing"]  = dict(eye=[3.0, 0.95, 1.45], tgt=[0.95, 1.45, -1.85])
    out["entry_gate"]     = dict(eye=[6.5, 0.5, 1.2], tgt=[1.8, 1.8, -1.2])  # accessibility v2 entry route
    # [rooftop v3] roof_context: plant cluster (HVAC · vent · pipe run) + parapet, a level cut
    # [rooftop v4 / v6 judgment extra observation (1)] canopy cropping resolved. The old tgt z 0.2 (depression 10.7 deg)
    #   combined with the old planter (11,−6) (viewing distance 5.9 m) put the canopy top at sy=1.95 = a point
    #   2x outside the top of frame. The planter is pushed to the west end (6.0,−6.8), stretching the viewing distance to 10.8 m
    #   and the depression eased to 4.4 deg (tgt z 0.2→1.15, eye z 1.8→1.9 = human eye height kept).
    #   [check sy (= normalised vertical screen coordinate, |sy|<=1 is inside the frame)]
    #   canopy top +0.86 · HVAC0 −0.67 · HVAC1 −0.67 · vent −0.14 ·
    #   pipe run −0.41 · south parapet top ±0.00 → **all inside the frame**
    #   (the canopy uses roof.planter.canopy_top 3.90 = the conservative upper bound on the measured 3.81).
    #   [_frame_scan] sky 30.1 / roof deck 20.9 / planter and tree 19.0 (was 44.2 →
    #   over-occupancy eased) / south and west parapets 13.9 / HVAC 11.0 / vent 0.5 %.
    out["roof_context"]   = dict(eye=[16.6, -4.2, 1.9], tgt=[9.0, -8.0, 1.15])
    # [rooftop v4 / v6 judgment (1)] roof_skyline re-aimed for the 3rd time. The north-west bearing of v5 and v6 was
    #   checked by eye only and failed both times — the real occluders were not the winder arc rings but
    #   (a) the U_N rooftop parapet right in front (top 1.1) and (b) the lower terrace parapets L_W/L_N
    #   (top −0.75); building E's cap (−1.0) sank below silhouette (b), leaving only 2 % of the roof
    #   exposed (the v6 frame was reproduced and confirmed with _frame_scan).
    #   Solution: keep the eye height at a human 2.0 m and **move building E due north** (see PARAMS
    #   buildings) — looking due north from the rooftop's north edge (y3.75), the lower terrace
    #   (x<=4) and its parapet do not enter the sight line at all.
    #   [check] eye(10.0,2.0,2.0): 1.76 m to the inner face of U_N → the sight line's depression limit is
    #   atan(0.9/1.76)=27.1 deg. Building E's near end (y16, cap −1.0) is 12.0 deg down · its far end (y42)
    #   4.3 deg → the 7.7 deg roof band (21 % of the 36 deg vertical FOV) is inside the limit (15.1 deg to spare).
    #   For L_N (y16.75..17, x<=4) the sight line is at x11.7 by y17 → no crossing.
    #   [_frame_scan] sky 44.6 % · building E 38.9 % (roof top face 12.3 %) · ground (the alley 6 m
    #   below) 7.7 % · U_N parapet foreground 6.7 % · dark wall 0 %.
    out["roof_skyline"]   = dict(eye=[10.0, 2.0, 2.0], tgt=[13.0, 29.0, -2.0])
    return out


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. upper_approach — 상부 보도에서 방사형 단코, 직선 소실점 부재
 2. h0.3·d5~10     — 코너 winder 낙차(1.8m) 인지
 3. winder_mid     — 1/4회전 하강의 부채꼴 단 형태
 4. radial_nosing  — 방사선 단코가 세그(3) 각짐 없이 읽히는가(하강 부감=디딤면)
 4b. lower_lookup  — [옥상 v4] 마지막 단에서 팬을 거슬러 올려다본 **라이저 면**
                     (4번과 짝: 부감=디딤 84 % / 앙각=라이저 47 %)
 5. cue            — 상/하부 보도 재질경계 / 외측 파라펫·핸드레일
 6. entry_gate     — [GT-82] 문턱→카이트 랜딩 연속(**입구 유효폭 1.96**, 이전
                     1.53)·단부 피어+게이트 기둥·에지 가드, 하부는 출구
                     (**1.53**, 이전 1.04) sector→코너 슬래브→하부 보도 연속
 7. roof_context   — [옥상 v3] 실외기·환기구·배관·옥상 파라펫 + 옥상 화단·수목
                     [옥상 v4] 수관 정상이 프레임 안에 온전히 들어오는가
                     [GT-82] 화단 박스·코어 벽이 검은 덩어리로 죽지 않는가
 8. roof_skyline   — [GT-82] 배경 건물 3동 삭제. 북측 파라펫 마루와 그 너머
                     **6 m 아래 지반**만으로 옥상 높이가 읽히는가"""


def main():
    # [GT-89] SMOKE gate - early exit BEFORE the Isaac boot (no GPU, no GUI).
    # The old template read NEGOBS_SMOKE only as boot()'s headless arg (or not at
    # all), so the §2.2 smoke floor booted Isaac on this scene (scene03/09 incident).
    # Deep checks keep their own arms (NEGOBS_SELFCHECK / geom_invariance_check.py).
    if os.environ.get("NEGOBS_SMOKE", "0") == "1":
        print("SMOKE_OK %s pre-boot gate (GT-89)" % os.path.basename(__file__))
        return
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"
    smoke_mode = os.environ.get("NEGOBS_SMOKE", "0") == "1"

    if smoke_mode:
        # [rooftop v4] coordinate check before booting — the convention that stops occlusion failures recurring (v6 judgment §lessons).
        _geom_report()

    # [GT-82] `brick_red` out (the three backdrop buildings were its only consumer),
    #   `concrete_wall` in (the L core and the newel).
    sc.check_assets(
        ["plaza_light", "plaza_lower", "granite_dark",
         "concrete_wall", "grass", "hdri", "mdl"],
        hdri=PARAMS["light"]["hdri"])

    simulation_app = sc.boot(capture_mode or smoke_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from pxr import UsdGeom
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.Xform.Define(stage, "/World/Scene19")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    C = PARAMS["center"]
    cx, cy = C["cx"], C["cy"]

    # -------------------------------------------------------------------
    # materials
    # -------------------------------------------------------------------
    def setup_materials():
        scl = mp["scale"]
        M = {}
        M["upper"] = sc.make_pbr(
            stage, "/World/Looks/Upper", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            scl["plaza_light"], tint=(0.72, 0.72, 0.72))   # [T1 T-1] x0.72
        M["lower"] = sc.make_pbr(
            stage, "/World/Looks/Lower", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"), sc.tex_path("plaza_lower", "rough"),
            scl["plaza_lower"], tint=mp["lower_warm_tint"])
        # step material = light plaza_light (contrasts with the granite_dark walls) [A-19(1)]
        M["step"] = sc.make_pbr(
            stage, "/World/Looks/Step", sc.tex_path("plaza_light", "diff"),
            sc.tex_path("plaza_light", "nor"), sc.tex_path("plaza_light", "rough"),
            scl["plaza_light"], tint=(0.72, 0.72, 0.72))   # [T1 T-1] x0.72
        # dark granite — kept only for the small deck-level bases (HVAC / PH plinths),
        #   which sit in full sun and read as 기초 stone. [GT-82(2)] it is NO LONGER the
        #   surround of the descent.
        M["granite"] = sc.make_pbr(
            stage, "/World/Looks/Granite", sc.tex_path("granite_dark", "diff"),
            sc.tex_path("granite_dark", "nor"), sc.tex_path("granite_dark", "rough"),
            scl["granite_dark"])
        # [GT-82(2)] the rooftop core (L wall + coping) — exposed concrete, lum 0.290.
        #   `/World/Looks/CoreWall` resolves to the look layer's **concrete** class (the
        #   `"wall"` token), so it takes the concrete bevel 0.020, the structure weather
        #   profile and bump 1.6 — the same prescription the parapets already get.
        M["core"] = sc.make_pbr(
            stage, "/World/Looks/CoreWall", sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"),
            scl["concrete_wall"], tint=mp["core_tint"])
        # [GT-82(2)] the newel = the core's rounded corner, same concrete one value down.
        #   `/World/Looks/NewelConcrete` carries the `"concrete"` token for the same reason.
        M["newel"] = sc.make_pbr(
            stage, "/World/Looks/NewelConcrete",
            sc.tex_path("concrete_wall", "diff"),
            sc.tex_path("concrete_wall", "nor"),
            sc.tex_path("concrete_wall", "rough"),
            scl["core_newel"], tint=mp["newel_tint"])
        M["grass"] = sc.make_pbr(
            stage, "/World/Looks/Grass", sc.tex_path("grass", "diff"),
            sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
            scl["grass"], tint=mp["grass_tint"])
        M["glass"] = sc.make_pbr(stage, "/World/Looks/Glass",
                                 diffuse_color=mp["glass_color"],
                                 roughness_const=mp["glass_rough"], metallic=0.0)
        M["rail"] = sc.make_pbr(stage, "/World/Looks/Rail",
                                diffuse_color=mp["rail_color"],
                                metallic=mp["rail_metallic"],
                                roughness_const=mp["rail_rough"])
        M["wood"] = sc.make_pbr(stage, "/World/Looks/Wood",
                                diffuse_color=mp["wood_color"],
                                roughness_const=mp["wood_rough"])
        M["canopy_a"] = sc.make_pbr(stage, "/World/Looks/CanopyA",
                                    diffuse_color=mp["canopy_a"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        M["canopy_b"] = sc.make_pbr(stage, "/World/Looks/CanopyB",
                                    diffuse_color=mp["canopy_b"],
                                    roughness_const=mp["canopy_rough"],
                                    specular_level=0.0)
        M["parapet"] = sc.make_pbr(stage, "/World/Looks/Parapet",
                                   diffuse_color=mp["parapet_color"],
                                   roughness_const=mp["parapet_rough"])
        M["hvac"] = sc.make_pbr(stage, "/World/Looks/Hvac",
                                diffuse_color=mp["hvac_color"], metallic=0.3,
                                roughness_const=mp["hvac_rough"])
        M["door"] = sc.make_pbr(stage, "/World/Looks/Door",
                                diffuse_color=mp["door_color"], metallic=0.4,
                                roughness_const=mp["door_rough"])
        # [W2-D · §5.6] urethane membrane waterproofing (green) — deck coat + parapet turn-up in the same colour.
        #   `[spec-doc]` Nara Marketplace R25BK00911379 "the surface colour is green".
        M["coating"] = sc.make_pbr(stage, "/World/Looks/Coating",
                                   diffuse_color=mp["coating_color"],
                                   roughness_const=mp["coating_rough"])
        # [W3 L19 · 19-4] 우레탄 덧방 (repair overcoat) + its feathered lap edge.
        M["patch_coat"] = sc.make_pbr(stage, "/World/Looks/PatchCoat",
                                      diffuse_color=mp["patch_coat_color"],
                                      roughness_const=mp["patch_coat_rough"])
        M["patch_lap"] = sc.make_pbr(stage, "/World/Looks/PatchLap",
                                     diffuse_color=mp["patch_lap_color"],
                                     roughness_const=mp["patch_lap_rough"])
        M["gk_iron"] = sc.make_pbr(stage, "/World/Looks/GKitIron",
                                   diffuse_color=(0.09, 0.09, 0.095),
                                   metallic=0.55, roughness_const=0.55)
        M["gk_stain"] = sc.make_pbr(stage, "/World/Looks/GKitStain",
                                    diffuse_color=(0.17, 0.19, 0.16),
                                    roughness_const=0.88)
        return M

    # -------------------------------------------------------------------
    # ground floor (grass) — full-area slab (below the drop = the floor). Tiled as 4 boxes.
    # -------------------------------------------------------------------
    def build_ground(M):
        g = PARAMS["ground"]
        top, th = g["top_z"], 1.0
        cz = top - th / 2.0
        xm = (g["x0"] + g["x1"]) / 2.0
        ym = (g["y0"] + g["y1"]) / 2.0
        for tag, (x0, x1, y0, y1) in (
                ("SW", (g["x0"], xm, g["y0"], ym)),
                ("SE", (xm, g["x1"], g["y0"], ym)),
                ("NW", (g["x0"], xm, ym, g["y1"])),
                ("NE", (xm, g["x1"], ym, g["y1"]))):
            sc.add_box(stage, f"/World/Scene19/Ground_{tag}",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0, cz),
                       (x1 - x0, y1 - y0, th), M["grass"])

    # -------------------------------------------------------------------
    # upper/lower sidewalks (material boundary) — solid slabs (down to ground −2.31). Outside the stairs (r>=4).
    # -------------------------------------------------------------------
    def build_walkways(M, hazard):
        base = PARAMS["ground"]["top_z"]
        for name, mtl in (("upper", M["upper"]), ("lower", M["lower"])):
            w = PARAMS[name]
            top = w["top_z"] if hazard else 0.0    # the flat control is z=0 throughout
            # [W2-0 · P-A] The upper roof deck is the ground_kit stage.
            sc.skin_exclude(f"/World/Scene19/Walk_{name}")
            sc.add_box(stage, f"/World/Scene19/Walk_{name}",
                       ((w["x0"] + w["x1"]) / 2.0, (w["y0"] + w["y1"]) / 2.0,
                        (top + base) / 2.0),
                       (w["x1"] - w["x0"], w["y1"] - w["y0"], top - base),
                       mtl, collider=True)
        # [accessibility v2] corner slab: between the winder outer arc (r4) and the straight sidewalk edges (x=4/y=4),
        #   the floor that fills the wedge (max width 1.66). hazard = lower plaza extension (−1.95),
        #   flat control = z0. The x/y<0 band that overlaps the wall interior is buried in the wall volume (not visible).
        co = PARAMS["access"]["corner"]
        top = PARAMS["lower"]["top_z"] if hazard else 0.0
        sc.add_box(stage, "/World/Scene19/CornerSlab",
                   ((co["x0"] + co["x1"]) / 2.0, (co["y0"] + co["y1"]) / 2.0,
                    (top + base) / 2.0),
                   (co["x1"] - co["x0"], co["y1"] - co["y0"], top - base),
                   M["lower"], collider=True)

    # -------------------------------------------------------------------
    # [W2-D] ground_kit — P6 roof_membrane (spec §5.6 scene19 row)
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        g = PARAMS["gkit"]
        up = PARAMS["upper"]
        ins = float(g["region_inset"])
        ox = float(g["grid_origin_x"])
        s_edge = ox - float(up["x0"])          # axis "-x": s = origin_x - x
        gp = gk.plan_ground(
            "roof_membrane",
            region=(up["x0"] + ins, up["y0"] + ins,
                    up["x1"] - ins, up["y1"] - ins),
            z=float(up["top_z"]), gy=0.0, origin=(ox, 0.0, 0.0), axis="-x",
            edges=[("roof_edge", s_edge)], dists=(2, 3.5, 5),
            scene="scene19", tactile=(),
            # [W3 L19 · 19-4] `("patch", 4)` → `("patch", 2)`. Both survivors carry a
            #   cause (see PARAMS["gkit"]["patches"]); `patch_proud` is 0.002 m, two
            #   orders below `GT_DELTA` 0.020, so this is dressing, not a GT row.
            overrides=dict(infra=dict(gully=2),
                           surface=(("patch", 2),
                                    ("stain", ("water", "drip", "dirt")))),
            extras_args=dict(membrane=dict(seam_pitch=float(g["seam_pitch"]),
                                           wear_n=int(g["wear_n"]))),
            sites=dict(gully=[tuple(v) for v in g["drains"]],
                       patch=[tuple(v) for v in g["patches"]]),
            seed=19)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(membrane=M["coating"], membrane_seam=M["gk_stain"],
                  # [W3 L19 · 19-4] the 덧방 gets its own coat, and the lap edge is a
                  #   feathered coat rather than the dark asphalt saw-cut stain.
                  membrane_wear=M["coating"], patch=M["patch_coat"],
                  patch_cut=M["patch_lap"], gully=M["gk_iron"],
                  manhole=M["gk_iron"], trench=M["gk_iron"],
                  trench_frame=M["gk_iron"], joint=M["gk_stain"],
                  crack=M["gk_stain"], weed=M["grass"], wear=M["gk_stain"],
                  stain_water=M["gk_stain"], stain_drip=M["gk_stain"],
                  stain_dirt=M["gk_stain"])
        res = gk.apply_ground(kit, "/World/Scene19/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        print(f"[ground_kit] scene19 P6 · 프림 {res['prims']} · "
              f"δmax {res['gt_delta_max']:.4f} · unit_cell {res['unit_cell']}")
        return res

    # -------------------------------------------------------------------
    # winder 12 steps + newel + building L wall + outer parapet
    # -------------------------------------------------------------------
    # [rooftop v4] _step_top uses the module-scope definition from section [C] as is
    #   (single-sourced so that assembly ↔ occlusion check read the same step top faces).

    def build_winder(M):
        w = PARAMS["winder"]
        for i in range(w["n"]):
            a0 = w["a0"] + i * w["sector_deg"]
            # [W3 L19 · GT-41] `mesh=` — true annular sectors. See PARAMS["winder"].
            sc.build_arc_steps(stage, f"/World/Scene19/Step_{i}", cx, cy,
                               w["r_in"], w["r_out"], a0, a0 + w["sector_deg"],
                               w["seg"], _step_top(i), w["base_z"], M["step"],
                               mesh=w["mesh"], arc_seg=w["arc_seg"])
        # inner corner newel — [GT-82(2)] core concrete, not granite_dark
        nw = PARAMS["newel"]
        sc.add_cylinder(stage, "/World/Scene19/Newel",
                        (cx, cy, (nw["z_top"] + nw["z_bot"]) / 2.0),
                        nw["r"], nw["z_top"] - nw["z_bot"], M["newel"],
                        collider=True)
        # 2 faces of the building corner L wall
        wl = PARAMS["walls"]
        zc = (wl["z_top"] + wl["z_bot"]) / 2.0
        hz = wl["z_top"] - wl["z_bot"]
        for tag in ("south", "west"):
            b = wl[tag]
            sc.add_box(stage, f"/World/Scene19/Wall_{tag}",
                       ((b["x0"] + b["x1"]) / 2.0, (b["y0"] + b["y1"]) / 2.0, zc),
                       (b["x1"] - b["x0"], b["y1"] - b["y0"], hz), M["core"],
                       collider=True)
        # [GT-82(3)] L coping over the core. The two wall boxes overlap in
        #   x −1..0 · y −1..0, so a cap per wall would put two coplanar plates on the same
        #   z = z_top+cap_t and z-fight there. The cap is therefore cut as **three
        #   non-overlapping runs**: the south run carries the corner, and the west run is
        #   split either side of it at y = south.y0 − over / south.y1 + over.
        ov, ct = wl["cap_over"], wl["cap_t"]
        bs, bw = wl["south"], wl["west"]
        cap_z = wl["z_top"] + ct / 2.0
        for tag, x0, x1, y0, y1 in (
                ("S", bs["x0"] - ov, bs["x1"] + ov, bs["y0"] - ov, bs["y1"] + ov),
                ("W_S", bw["x0"] - ov, bw["x1"] + ov, bw["y0"] - ov,
                 bs["y0"] - ov),
                ("W_N", bw["x0"] - ov, bw["x1"] + ov, bs["y1"] + ov,
                 bw["y1"] + ov)):
            sc.add_box(stage, f"/World/Scene19/CoreCap_{tag}",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0, cap_z),
                       (x1 - x0, y1 - y0, ct), M["parapet"])
        # outer low parapet: the entry (sector 0..1) and exit (10..11) are open [accessibility v2],
        #   arc rings on the middle sectors only (each step top +h)
        pp = PARAMS["parapet"]
        ac = PARAMS["access"]
        for i in range(ac["parapet_first"], ac["parapet_last"] + 1):
            a0 = w["a0"] + i * w["sector_deg"]
            top = _step_top(i)
            # [W3 L19 · GT-41] The parapet ring is a **guard**, not a walked surface, so
            #   its `mesh=` flip is R-3 and not GT — but it is the ring the eye actually
            #   reads as "curved" (G8's concentric vocabulary), and the box convention
            #   left each 7.5° arc 0.34° proud of its neighbour at r_in, i.e. a stepped
            #   ledge every 7.5° along a nominally smooth curve.
            sc.build_arc_steps(stage, f"/World/Scene19/Parapet_{i}", cx, cy,
                               pp["r_in"], pp["r_out"], a0, a0 + w["sector_deg"],
                               1, top + pp["h"], top - 0.1, M["parapet"],
                               collider=True, mesh=w["mesh"],
                               arc_seg=w["arc_seg"])
        # [GT-82(4)] Run ends. Each terminal is now **pier + finial**, replacing "a sawn
        #   radial face with a 0.05 m stick standing next to it":
        #     ParapetEnd_* — an annular pier 0.04 proud of the ring on both radii and
        #       `lead` deg past the run end, so the ring's cut face (and the handrail's cut
        #       end, which shares the same radial plane) is enclosed, not exposed. Its foot
        #       is `drop` below the LOWER of the two step tops it straddles, so neither
        #       terminal can float over the step below it.
        #     GatePost_*  — the same metal post, kept at the same prim path, now standing on
        #       the pier crown (foot buried 0.04) rather than rising from the step.
        r_mid = (pp["r_in"] + pp["r_out"]) / 2.0
        ep = ac["end_pier"]
        for tag, i_ref, ang, sgn in (
                ("entry", ac["parapet_first"],
                 w["a0"] + ac["parapet_first"] * w["sector_deg"], +1.0),
                ("exit", ac["parapet_last"],
                 w["a0"] + (ac["parapet_last"] + 1) * w["sector_deg"], -1.0)):
            top = _step_top(i_ref)
            a_lo = min(ang - sgn * ep["lead"],
                       ang + sgn * (ep["span"] - ep["lead"]))
            a_hi = a_lo + ep["span"]
            # the foot must clear the lower of the two straddled step tops
            i_out = i_ref - 1 if sgn > 0 else i_ref + 1
            base = min(top, _step_top(max(0, min(w["n"] - 1, i_out)))) \
                - ep["drop"]
            pier_top = top + pp["h"] + ep["rise"]
            sc.build_arc_steps(stage, f"/World/Scene19/ParapetEnd_{tag}", cx, cy,
                               ep["r_in"], ep["r_out"], a_lo, a_hi, 1,
                               pier_top, base, M["parapet"], collider=True,
                               mesh=w["mesh"], arc_seg=w["arc_seg"])
            a = math.radians((a_lo + a_hi) / 2.0)
            sc.add_cylinder(stage, f"/World/Scene19/GatePost_{tag}",
                            (cx + r_mid * math.cos(a), cy + r_mid * math.sin(a),
                             pier_top - 0.04 + ac["post_h"] / 2.0),
                            ac["post_r"], ac["post_h"], M["rail"])

    # -------------------------------------------------------------------
    # [accessibility v2] upper threshold + edge guard — walk continuity (look_refs study)
    # -------------------------------------------------------------------
    def build_access(M):
        ac = PARAMS["access"]
        up = PARAMS["upper"]
        low_z = PARAMS["lower"]["top_z"]
        # threshold sliver: fills the gap between the sidewalk (z0) and the entry sector outer arc with sidewalk paving.
        #   The band biting inward (r<4) is buried outside the entry steps (step0/1) → the effective tread
        #   boundary stays consistently at x=3.86
        # [GT-82(4)] with the opening at 30 deg the arc retreats to x = 4·cos30 = **3.4641**,
        #   so `x0` is 3.46 and the effective boundary is a single straight 2.00 m nosing at
        #   x = 3.46 instead of the old 1.53 m one at 3.70. The guard shares that x0, so the
        #   throat's west face is one plane from y 0 to y 4 — no 0.24 m jog to catch the eye.
        th = ac["threshold"]
        sc.add_box(stage, "/World/Scene19/Threshold",
                   ((th["x0"] + up["x0"]) / 2.0, (th["y0"] + th["y1"]) / 2.0,
                    (up["top_z"] + low_z) / 2.0),
                   (up["x0"] - th["x0"], th["y1"] - th["y0"],
                    up["top_z"] - low_z), M["upper"], collider=True)
        # edge guard retaining wall: guards the sidewalk edge north of the threshold (a 1.95 drop to the corner slab).
        #   From the corner slab top face (−1.95) up to +1.0 above the sidewalk
        gd = ac["guard"]
        sc.add_box(stage, "/World/Scene19/EdgeGuard",
                   ((gd["x0"] + gd["x1"]) / 2.0, (gd["y0"] + gd["y1"]) / 2.0,
                    (low_z + gd["h_top"]) / 2.0),
                   (gd["x1"] - gd["x0"], gd["y1"] - gd["y0"],
                    gd["h_top"] - low_z), M["parapet"], collider=True)
        # [GT-82(4)] The guard is the westward continuation of the north rooftop parapet —
        #   both crowns are 1.10 — but `RoofPP_U_N` carries a coping and the guard did not,
        #   so the run changed section mid-crown. Same 0.012 m plate as `RoofCope_*`, proud
        #   0.06 on the two free faces (west over the wedge, south over the throat) and
        #   **flush at x = up.x0** so it butts the U_N coping instead of overlapping it —
        #   a coplanar overlap at the same z is exactly the z-fight this round is fixing.
        #   Its north edge takes U_N's own coping overhang so the two read as one line.
        cw, t = PARAMS["roof"]["coping_w"], PARAMS["roof"]["pp_t"]
        cap_n = up["y1"] + (cw - t) / 2.0
        sc.add_box(stage, "/World/Scene19/EdgeGuardCap",
                   ((gd["x0"] - 0.06 + gd["x1"]) / 2.0,
                    (gd["y0"] - 0.06 + cap_n) / 2.0, gd["h_top"] + 0.006),
                   (gd["x1"] - gd["x0"] + 0.06, cap_n - gd["y0"] + 0.06, 0.012),
                   M["parapet"])

    # -------------------------------------------------------------------
    # [rooftop v3] rooftop parapet (perimeter guard) + plant props + rooftop door
    #   — scene context cues (plant back-inference · scale anchor). Hazard geometry (winder) unchanged.
    # -------------------------------------------------------------------
    def build_plant(M):
        """[W3 L19 · N-A3] rooftop plant + PH boxes as measured CC0 scans.

        Every asset here is a MaterialX row, so **every call passes `treatment="mtlxoff"`**
        — `w3_t4b_v1.md` **T4b-F1**: all 33 CC0 rows bind `ND_normalmap_float`, which is
        missing from this runtime's Sdr registry, and a raw call site renders **red**.
        The wrapper puts the material opinion inside the prototype, which is the only
        route that survives `instanceable=True` (a scene-side bind cannot reach into a
        prototype — measured twice, `w3_t4b_v1.md` §1.2 and GT-21's rock fix).
        `z_mode="base"` because these scans carry geometry below their own origin
        (`exterior_aircon_unit` zmin −0.320 = 34.5 %, `power_box_01` −0.252 = 49.8 %);
        the default `grade` mode would sink them to the waist (scene09 precedent).
        Failure is **non-fatal**: an unloadable urban row must not cost the roof its
        plinths, so the plinths are built first and unconditionally.
        """
        rf, up = PARAMS["roof"], PARAMS["upper"]
        pl = rf["plant"]
        z0 = up["top_z"]
        for i, u in enumerate(pl["ac"]):          # concrete 기초, always built
            sx, sy, _ = u["size"]
            sc.add_box(stage, f"/World/Scene19/HvacBase_{i}",
                       (u["cx"], u["cy"], z0 + pl["plinth_h"] / 2.0),
                       (sx + 2 * pl["plinth_over"], sy + 2 * pl["plinth_over"],
                        pl["plinth_h"]), M["granite"])
        for u in pl["boxes"]:
            sx, sy, _ = u["size"]
            sc.add_box(stage, f"/World/Scene19/PlantBase_{u['aid']}",
                       (u["cx"], u["cy"], z0 + u["plinth"] / 2.0),
                       (sx + 0.12, sy + 0.12, u["plinth"]), M["granite"])
        try:
            import urban_kit as uk
        except Exception as e:
            print(f"[urban][경고] urban_kit 로드 실패 — 옥상 설비 생략: {e}")
            return 0
        n = 0
        for i, u in enumerate(pl["ac"]):
            try:
                if uk.add_urban_asset(
                        stage, f"/World/Scene19/Hvac_{i}", u["aid"],
                        pos_m=(u["cx"], u["cy"], z0 + pl["plinth_h"]),
                        yaw_deg=u["yaw"], z_mode="base", scene="19",
                        instanceable=True, treatment="mtlxoff") is not None:
                    n += 1
            except Exception as e:
                print(f"[urban][경고] {u['aid']} 배치 실패: {e}")
        for u in pl["boxes"]:
            try:
                if uk.add_urban_asset(
                        stage, f"/World/Scene19/Plant_{u['aid']}", u["aid"],
                        pos_m=(u["cx"], u["cy"], z0 + u["plinth"]),
                        yaw_deg=u["yaw"], z_mode="base", scene="19",
                        instanceable=True, treatment="mtlxoff") is not None:
                    n += 1
            except Exception as e:
                print(f"[urban][경고] {u['aid']} 배치 실패: {e}")
        print(f"[옥상 설비] N-A3 실측 스캔 {n}/{len(pl['ac']) + len(pl['boxes'])}점 "
              f"· treatment=mtlxoff · z_mode=base · instanceable")
        return n

    def build_rooftop(M):
        rf = PARAMS["roof"]
        up, lo = PARAMS["upper"], PARAMS["lower"]
        t, h, hi = rf["pp_t"], rf["pp_h"], rf["pp_h_inner"]

        cw = rf["coping_w"]
        tu = rf["turnup_h"]

        def pp(tag, x0, x1, y0, y1, base, hh, ref=None):
            sc.add_box(stage, f"/World/Scene19/RoofPP_{tag}",
                       ((x0 + x1) / 2.0, (y0 + y1) / 2.0,
                        base - 0.05 + (hh + 0.05) / 2.0),
                       (x1 - x0, y1 - y0, hh + 0.05), M["parapet"],
                       collider=True)
            ref = ref or up                    # deck this parapet belongs to
            # [W2-D · spec §5.6 19-2] **turn-up + coping**.
            #   ① turn-up: the waterproofing coat wraps the parapet's inner
            #      face for `turnup_h` (0.30 m) — it is the same green as the
            #      deck, not concrete. `[spec-doc]` "coated wrapping the whole of the inner wall and the top".
            #   ② coping: a cap `coping_w` (0.45~0.55) wide **centred** on the
            #      parapet, so it overhangs 0.125 m each side with a drip edge
            #      instead of cantilevering over the deck. Both are 12 mm
            #      plates — no GT change, no camera occlusion (the roof_context
            #      eye sits at z 1.9, above the 1.15~1.20 parapet crown).
            #   Orientation is derived from the box: the long axis is the run,
            #   the short axis is the thickness, and "inner" is the side that
            #   faces the centre of the deck this parapet belongs to (`ref`) —
            #   passing `ref` matters for the lower terrace ring, whose
            #   east parapet has the deck on its **-X** side, the opposite of
            #   the upper deck's.
            sx, sy = x1 - x0, y1 - y0
            cxm, cym = (x0 + x1) / 2.0, (y0 + y1) / 2.0
            top = base - 0.05 + (hh + 0.05)
            if sx <= sy:                       # runs along Y, thickness in X
                inner = 1.0 if cxm < (ref["x0"] + ref["x1"]) / 2.0 else -1.0
                sc.add_box(stage, f"/World/Scene19/RoofTurn_{tag}",
                           (cxm + inner * (sx / 2.0 + 0.006), cym,
                            base + tu / 2.0), (0.012, sy, tu), M["coating"])
                sc.add_box(stage, f"/World/Scene19/RoofCope_{tag}",
                           (cxm, cym, top + 0.006),
                           (cw, sy, 0.012), M["parapet"])
            else:                              # runs along X, thickness in Y
                inner = 1.0 if cym < (ref["y0"] + ref["y1"]) / 2.0 else -1.0
                sc.add_box(stage, f"/World/Scene19/RoofTurn_{tag}",
                           (cxm, cym + inner * (sy / 2.0 + 0.006),
                            base + tu / 2.0), (sx, 0.012, tu), M["coating"])
                sc.add_box(stage, f"/World/Scene19/RoofCope_{tag}",
                           (cxm, cym, top + 0.006),
                           (sx, cw, 0.012), M["parapet"])

        # upper rooftop (z0) perimeter: east (x1) · south (y0) · west (x0, south end..L wall y0) · north (lower terrace boundary)
        pp("U_E", up["x1"] - t, up["x1"], up["y0"], up["y1"], up["top_z"], h)
        pp("U_S", up["x0"], up["x1"] - t, up["y0"], up["y0"] + t, up["top_z"], h)
        pp("U_W", up["x0"], up["x0"] + t, up["y0"] + t, -1.0, up["top_z"], h)
        pp("U_N", up["x0"], up["x1"], up["y1"] - t, up["y1"], up["top_z"], hi)
        # lower terrace (−1.95) perimeter: west (x0) · north (y1) · east (x1, outside the upper body, y>4)
        pp("L_W", lo["x0"], lo["x0"] + t, lo["y0"], lo["y1"], lo["top_z"], h, lo)
        pp("L_N", lo["x0"] + t, lo["x1"], lo["y1"] - t, lo["y1"], lo["top_z"], h, lo)
        pp("L_E", lo["x1"] - t, lo["x1"], lo["y0"], lo["y1"] - t, lo["top_z"], h, lo)

        # [W3 L19 · N-A3] rooftop plant — the two procedural boxes and the two PH boxes
        #   are real scans through `urban_kit`, on the concrete plinths that were already
        #   there (a 실외기 sits on 기초 + 방진패드, not on the membrane).
        build_plant(M)
        v = rf["vent"]
        sc.add_cylinder(stage, "/World/Scene19/Vent",
                        (v["cx"], v["cy"], up["top_z"] + v["h"] / 2.0),
                        v["r"], v["h"], M["hvac"])
        sc.add_cylinder(stage, "/World/Scene19/VentCap",
                        (v["cx"] + v["r"] * 1.2, v["cy"],
                         up["top_z"] + v["h"] + v["r"] * 0.4),
                        v["r"] * 0.9, v["r"] * 2.6, M["hvac"], rotY=90.0)
        p = rf["pipe"]
        sc.add_cylinder(stage, "/World/Scene19/PipeRun",
                        ((p["x0"] + p["x1"]) / 2.0, p["y"],
                         up["top_z"] + p["r"] + 0.02),
                        p["r"], p["x1"] - p["x0"], M["hvac"], rotY=90.0)
        # rooftop steel door — at upper terrace level on the L wall south end face (x=4, width 1m).
        #   Right beside the entry threshold, so the route "out of the rooftop core and onto the corner stairs" reads.
        # [GT-82(2)] the leaf now sits inside a steel frame instead of being a bare plate on
        #   a blank wall end. Frame outer face x = x1 + frame_t (4.06), leaf outer face
        #   x1 + 0.04 → the leaf is **0.02 m recessed**, which is the reveal that makes it
        #   read as a door at all. Frame outer width w + 2·frame_w = 1.00 = the wall end
        #   face exactly, so the jambs die on the wall arris with nothing overhanging.
        d = rf["door"]
        ws = PARAMS["walls"]["south"]
        dcy = (ws["y0"] + ws["y1"]) / 2.0
        fw, ft = d["frame_w"], d["frame_t"]
        sc.add_box(stage, "/World/Scene19/CoreDoor",
                   (ws["x1"] + 0.02, dcy, up["top_z"] + d["h"] / 2.0),
                   (0.04, d["w"], d["h"]), M["door"])
        for tag, dy in (("L", -(d["w"] + fw) / 2.0), ("R", (d["w"] + fw) / 2.0)):
            sc.add_box(stage, f"/World/Scene19/CoreDoorJamb_{tag}",
                       (ws["x1"] + ft / 2.0, dcy + dy,
                        up["top_z"] + (d["h"] + fw) / 2.0),
                       (ft, fw, d["h"] + fw), M["rail"])
        sc.add_box(stage, "/World/Scene19/CoreDoorHead",
                   (ws["x1"] + ft / 2.0, dcy,
                    up["top_z"] + d["h"] + fw / 2.0),
                   (ft, d["w"] + 2 * fw, fw), M["rail"])

    # -------------------------------------------------------------------
    # dressing — rooftop planter + [rooftop v3] rooftop context elements
    #   ([GT-82] the distant-building tier is deleted)
    # -------------------------------------------------------------------
    def build_dressing(M):
        tree_mtls = (M["wood"], M["canopy_a"], M["canopy_b"])
        pl = PARAMS["roof"]["planter"]     # [rooftop v4] position comes from the single source PARAMS
        # [W3 L19] 옥상 플랜터: 토심 0.75 m (조경기준 제12조 교목 0.70 이상) ·
        #   관목 1종 pinned (`planter_accent` = 주목) · 교목은 `species=` 를 넘기기 위해
        #   **직접** `build_tree` 로 심는다 — `build_planter` 는 `species=` 를
        #   `place_shrubs` 로만 넘기고 `build_tree` 로는 넘기지 않는다(K4(c) 시그니처 보존,
        #   킷은 이번 창에서 동결). `tree_mtls=None` 이면 세 번째 관목이 화단 중앙에
        #   앉으므로 교목은 (−0.62, +0.62) 오프셋에 심는다.
        # [GT-82(2)] the bed leaves `granite` for the core concrete: a 3.0 x 3.0 x 0.90 box in
        #   a 0.0767-luminance stone is the second near-black mass in `roof_context`, and a
        #   raised 옥상 플랜터 is a cast box, not a granite monolith. Geometry unchanged, so
        #   the `Planter_A` occlusion AABB and the `roof_context` frame probes do not move.
        sc.build_planter(stage, "/World/Scene19/Planter_A",
                         pl["cx"], pl["cy"], 0.0,
                         M["core"], M["grass"], tree_mtls=None,
                         size=pl["size"], curb_h=pl["curb_h"],
                         grass_h=pl["soil_h"], species=pl["shrub_species"])
        sc.build_tree(stage, "/World/Scene19/Planter_A",
                      pl["cx"] + pl["tree_dx"], pl["cy"] + pl["tree_dy"],
                      pl["soil_h"], *tree_mtls,
                      trunk_h=pl["trunk_h"], species=pl["tree_species"])
        # [GT-82(1)] the `Building_C/D/E` loop is deleted — see PARAMS. The scene's only
        #   built mass is the host L core the fan winds around.
        build_rooftop(M)

    # -------------------------------------------------------------------
    # cue toggles (geometry unchanged)
    # -------------------------------------------------------------------
    def build_cues(M):
        w = PARAMS["winder"]
        pp = PARAMS["parapet"]
        # cue_railing: handrail on the parapet top (per-step arc cap) — only on the parapet-retained span
        if cfg.get("cue_railing"):
            ac = PARAMS["access"]
            for i in range(ac["parapet_first"], ac["parapet_last"] + 1):
                a0 = w["a0"] + i * w["sector_deg"]
                top = _step_top(i) + pp["h"]
                sc.build_arc_steps(stage, f"/World/Scene19/Rail_{i}", cx, cy,
                                   pp["r_out"] - 0.06, pp["r_out"], a0,
                                   a0 + w["sector_deg"], 1, top + 0.06,
                                   top - 0.06, M["rail"], collider=False,
                                   mesh=w["mesh"], arc_seg=w["arc_seg"])
        # cue_tactile: warning tactile strip on the upper approach (in front of the first step)
        if cfg.get("cue_tactile"):
            # [W2 · ground_kit §12.5-3] texture-backed so the 36 dots shade.
            tac = sc.tactile_pbr(stage, "/World/Looks/Tactile")
            sc.build_tactile(stage, "/World/Scene19/Tactile",
                             4.1, 4.5, -1.0, 1.0, tac, z=0.0)
        # cue_nosing: radial nosing anti-slip arc bands
        if cfg.get("cue_nosing"):
            nos = sc.make_pbr(stage, "/World/Looks/Nosing",
                              diffuse_color=mp["nosing_color"],
                              roughness_const=mp["nosing_rough"])
            for i in range(w["n"]):
                a0 = w["a0"] + i * w["sector_deg"]
                top = _step_top(i)
                # default-OFF ablation arm — flipped with the rest so the arm is not
                #   left on the retired convention (GT-40's tactile-arc precedent).
                sc.build_arc_steps(stage, f"/World/Scene19/Nosing_{i}", cx, cy,
                                   w["r_out"] - 0.06, w["r_out"], a0,
                                   a0 + w["sector_deg"], 1, top + 0.004,
                                   top - 0.02, nos, collider=False,
                                   mesh=w["mesh"], arc_seg=w["arc_seg"])

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    hazard = cfg["hazard_stairs"]
    build_ground(M)
    build_walkways(M, hazard)
    if hazard:
        build_winder(M)
        build_access(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)
    if hazard:
        build_cues(M)
    build_ground_kit(M)             # [W2-D] ground elements — after the dressing (scatter order convention)
    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        nprim = sum(1 for pr in stage.Traverse() if pr.IsA(UsdGeom.Gprim))
        print(f"SMOKE_OK prims={nprim}")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

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

    VIEWS = build_views()
    _v0 = VIEWS["upper_approach"]
    look_from(_v0["eye"], _v0["tgt"])

    os.makedirs(LOOKCHECK_DIR, exist_ok=True)

    if capture_mode:
        sc.capture_pipeline(simulation_app, VIEWS,
                            os.path.join(LOOKCHECK_DIR, "auto"),
                            set_render_mode, look_from)
        simulation_app.close()
        return

    from omni.kit.viewport.utility import get_active_viewport, \
        capture_viewport_to_file

    def capture(path):
        vp = get_active_viewport()
        capture_viewport_to_file(vp, file_path=path)

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene19_{ts}.png")
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
