# -*- coding: utf-8 -*-
"""
scene11_footbridge_stairs.py - NegObs synthetic scene 11: steel stairs of a
pedestrian overpass (Isaac Sim 4.5) · new in v5 (old scene11_grating_fireescape → scenes/archive_v3/)

Type    : R6 steel footbridge, **H-plan** (S11-H) over 6 lanes (inherits the
          open-riser · grating see-through axis)
Spec    : Docs/briefs/multi_scene_brief_v5.md §R6 + the shared-layer section
Law     : Docs/surveys/w3_intake_06_10.md **§S · S11-H** ("한국 육교는 H형이야")
          + Docs/surveys/w3_intake_v2_images.md §2 scene11 **R11-1 / R11-2**
          + §3 S06-B (curb legibility) · §7 R16-2 (stair-cue-first)
Image   : Docs/reference_photos/"Generated Image - Scene11.jpg" (**G11**) — season
          **summer** (full leaf, cumulus sky), beige-tan painted steel throughout.
Shared  : scene_common.py (build_open_riser_stairs / build_rot_group /
          build_railing_line / build_canopy / build_sign / build_tactile) ·
          infra_kit.build_curb_line (S06-B) · props_kit RF-1 / RF-5 / G13
World   : shares the footbridge convention with scene06_overpass_spiral.py
          (roadway asphalt 0.045 · kerb 0.15 · sidewalk paving_interlock · streetlights)
          — **but not its stair identity**: 06 = spiral tower, 11 = H-form +
          grating see-through (§S differentiation, user: "양쪽으로 다르게 읽힐 수 있잖아").

────────────────────────────────────────────────────────────────────────────
S11-H — why the plan was rebuilt (the I-plan is gone)
  The old build ran both stair sets **inline with the deck axis** (x 15…30.88 and
  its mirror), so the structure sprawled 62 m along the bridge direction. The user
  rejected exactly that: *"육교가 너무 양쪽으로 뻗어있어. 한국 육교는 H형이야"*.
  A Korean 육교 is an **H in plan**: the stair towers run **parallel to the
  carriageway** on each sidewalk, and the deck crosses between them.
  **R11-1** refines it from G11: the H is **asymmetric** — one straight form and one
  switchback form — which is what the photograph shows, not a symmetric double
  switchback.

  **GT-80 completes the H.** The first S11-H build gave each tower a *single* leg, so
  each head landing was a **T, not a cross**: a walker reaching a deck end could turn
  one way only, and the two remaining head-landing faces were closed with balustrade.
  An H has **four feet**, two per sidewalk, and every deck end must descend. Both
  towers therefore carry **two legs** that share one head landing and descend in
  opposite directions along the carriageway (±Y):
    · **west tower = STRAIGHT legs** (flight A → mid landing → flight B), hugging the
      west sidewalk at x −15.00…−13.20, feet at y +17.08 (N) and −17.08 (S).
    · **east tower = SWITCHBACK legs** (flight A → mid landing → flight B back on the
      neighbouring lane), hugging the east sidewalk at x 13.20…16.90, structure
      y −10.04…+10.04; both return lanes land on one shared ground apron at
      x 15.10…16.90, y −1.20…+1.20, immediately beside the head landing.
  The R11-1 asymmetry is untouched — it is simply carried one level up: one **tower**
  is straight and one is switchback, instead of one leg of each. Footprint asymmetry
  is still measured by the smoke report (east 3.70 m wide × 20.08 m long · west
  1.80 × 34.16), not asserted.

  A leg is authored in a canonical local frame (a = travel, +a descends; b =
  transverse) and placed by `build_rot_group`. A tower's **second leg is the mirror
  of the first, not its rotation**: pivot = the head landing's back edge ([computed]
  from `tower.head`), rotation = the first leg's negated, transverse coordinate
  negated (`bsign` = −1). The mirror is what keeps b = BA0 on the deck face and the
  switchback return lane **outboard**; a pure rotation would swing that lane inboard
  to x 11.30…13.10, i.e. onto the kerb and through the deck pier at x 11.80.

────────────────────────────────────────────────────────────────────────────
Hazard (= the reality of falling short of the code)
  ① **Deck-end / tower-head drop.** A robot crossing the deck (+X) meets the east
  head landing's outer edge at x = 15.00: beyond it is a **5.505 m** fall to the
  sidewalk (−0.005). At h0.3 the balustrade's lower band is open, so the far
  sidewalk and roadway show through and the floor reads as continuous. This is the
  drop the h0.3 preset grid frames head-on (grid origin unchanged at 15.00/0/5.50).
  ② **The east mid landings (z = 2.75) have no kickplate.** At h0.3 the railing bars
  pass above the field of view and the band below is open, so the 2.755 m drop past
  the landing reads as "the floor continues". The **west** mid landings carry the
  kickplate on the matched edge class — the code-compliant control.
  **Honest limitation of R11-1**: the asymmetric H means the mid landings are
  no longer *identical* boxes (east 1.80 × 3.70, west 1.80 × 1.80). The control
  pair is therefore held on the **matched edge class** — each landing's 1.80 m
  transverse side edge, same 2.755 m drop, same 1.10 m railing — and not on the
  whole landing. Stated rather than implied; see Docs/reports/w3_s11_v1.md §3.
  [GT-80] The leg completion doubles the pair (east S+N vs west N+S) and does not
  move it: the `midlanding` cut still frames the **east south** landing, and both
  matched Side1 edges are now carried by the same builder (`build_railing_line`'s
  rake line) instead of one of them doubling a balustrade 0.03 m away.
  ③ **Grating see-through.** Treads are grating (3 slits) — with no riser you see
  straight through to below, and in noon light the slit shadows stripe the sidewalk
  and erase the nosing edge.

GT drop invariance: the cue_* toggles only switch railing · kickplate · tactile ·
  sign prims on and off. The transforms of the deck · landings · stairs
  (riser 0.125 / tread 0.32 / 22 steps × 2 per tower) never change with a cue flag.

────────────────────────────────────────────────────────────────────────────
Walking-continuity self-check table — an H offers **four** routes off the deck, and
  each is 22 + 22 steps of riser 0.125, so every one of them totals 5.500 m.

  #  section                          coordinates (world, m)                 step
  ─  ───────────────────────────────  ─────────────────────────────────────  ──────
  0  deck run (+X)                    x −13.20…13.20, y ±1.20, z 5.500       —
     (clearance over the roadway x −10.5…10.5 = 5.10 −(−0.15) = 5.25 m)
  1  head landing = a CROSS landing   x ±13.20…±15.00, y −1.20…1.20, z 5.500 0.000
       open to the deck (b = BA0) · open at BOTH stair heads (each leg's a = 0)
       · guarded on the outer edge only (b = BA1) — the 5.505 m free edge
  2  W-N straight     y  1.20 →  8.24 → mid 10.04 → foot  17.08              0.125/step
  3  W-S straight     y −1.20 → −8.24 → mid −10.04 → foot −17.08             0.125/step
  4  E-N switchback   y  1.20 →  8.24 (lane x 13.20…15.00) → mid 10.04
     [GT-96 2판 · 08-11] the EAST tower descends ONCE, to the NORTH — the mirror
     pair read as a diamond/X and the user removed one side; the SOUTH leg went
     (its foot crowded the bus shelter), the freed head face is closed by the
     ribbon guard (L run). H stands on three feet.
                      → back to y −1.20 (lane x 15.10…16.90)                 0.125/step
                      → back to y  1.20 (lane x 15.10…16.90)                 0.125/step
  6  four feet → sidewalk            z 0.000 → −0.005                        0.005

  total rise = total fall = 5.500 m (= 44 × 0.125) on **every** route — invariant,
  unchanged by the H rebuild and by GT-80's leg completion (the crossing height
  z 5.50 did not move). Joint step ≤ 0.005 m.
  slope = atan(0.125/0.32) = 21.34° - a gentle footbridge stair (2R+T = 0.570).
  All four feet stand on the continuous sidewalk slab (y −60…60), so each connects to
  the scene edge without a spur (§0-2).

Guard doctrine (GT-80 edge finishing) — one member class per surface class:
  landings are guarded by `build_guard_run` (a CONTINUOUS polyline: shared corner
  post, kick band, 100 mm 안목 balusters, top + mid rail, knuckle cap at every node
  and run end); flights are guarded by `build_railing_line` starting **at** the stair
  head (`x_start == x_top`, so it emits no horizontal extension). The two meet
  end-to-end on the same line (`rail.y_inset` inboard of the pad edge), so a hand runs
  deck rail → head guard → rake rail → mid-landing guard → rake rail → foot newel
  without a break, a doubled line or an open cylinder mouth.

────────────────────────────────────────────────────────────────────────────
4-box opening convention: no cavity pierces the ground (deck and stairs are all
  above-ground structures). Sidewalk/roadway slabs may be laid as continuous boxes
  without breaching §A-3.

Camera axis note: the grid keeps the **deck run axis (+X)** and the origin
  **(15.00, 0, 5.50)** it already had — under the H-plan that point is the east
  head landing's outer edge, i.e. the drop a deck-travelling robot meets head-on.
  The approach corridor (d = 2/5/10 m behind it) is the deck itself, so no preset
  eye floats off the structure and **no judge preset had to be edited** to make the
  H-plan legible (the scene17 R17-1 principle: legibility comes from geometry).
  The stair head, which under the H-plan lies 1.20 m off that axis, is carried by
  the dedicated `stair_head` mise-en-scene cut.
  (Judging priority 1 = does hazard concealment hold at the robot's h0.3 - brief
  v5 shared layer 4)

Run (GUI look check - default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene11_footbridge_stairs.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python scene11_footbridge_stairs.py
Smoke (early exit before boot): NEGOBS_SMOKE=1 python scene11_footbridge_stairs.py

Coordinates: Z-up, m. Walk/deck axis +X · roadway axis +Y (6 lanes) · sidewalk top face −0.005.
"""

import os
import sys
import math
import json
import datetime

import numpy as np

import scene_common as sc
import ground_kit as gk
import infra_kit as ik
import props_kit as pk


# ===========================================================================
# [A] SCENE_CONFIG - the standard 7 keys.
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False -> deck and stairs removed (flat sidewalk control)
    "cue_railing":        True,   # pipe railings on stairs and landings + deck noise panels
    "cue_tactile":        False,  # [v5.2 user] tactile paving is rare in reality - default OFF (ablation path kept)   # urban-practice scene - stair head/foot tactile bands default ON (brief v5)
    "cue_material_break": True,   # kerb · lane paint · road band under the stair
    "cue_nosing":         True,   # yellow non-slip nosing band on the grating (footbridge practice)
    "cue_sign":           True,   # Korean sign sign_info (footbridge guidance) - shared layer
    "cue_scene_dressing": True,   # roadway · bus shelter · streetlights · street trees · distant buildings
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # --- two steel flights (brief R6: width 1.8, 22 steps x 2, mid landing, grating) ---
    #   riser 0.125 = 5.5 / 44 (deck height split evenly into 44 steps -> zero step at the joints).
    #   tread 0.32 -> run 7.04 per flight, slope 21.34 deg, 2R+T = 0.570.
    #   slits 3 : the tread is cut into 4 pieces with three 0.02 m gaps - see-through below, grid shadows.
    stair=dict(riser=0.125, tread=0.32, n=22, y0=-0.90, y1=0.90,
               tread_t=0.045, gap=0.025, slits=3),
    # --- H-plan tower geometry (S11-H · R11-1) ------------------------------
    #   Both towers are authored in a **canonical local frame** whose +X is the
    #   direction of descent and whose local Y is the flight width, then placed by
    #   `build_rot_group` so that +X lands on the carriageway axis (±Y in world).
    #   `head` = depth of the head landing along the travel axis (= deck width, so
    #   the 90° turn off the deck has a full flight-width square to turn in);
    #   `mid` = depth of the mid landing; `lane_gap` = the gap between the two
    #   parallel lanes of the switchback leg.
    tower=dict(width=1.80, head=2.40, mid=1.80, lane_gap=0.10,
               z_top=5.50, pad_t=0.40, kick_h=0.14,
               col_r=0.13, col_inset=0.34, col_z_bot=-0.30),
    # --- east tower = SWITCHBACK, the hazard side (kickplate ABSENT) ---------
    #   `pivot`/`rot` describe the tower's **primary** leg; the second leg is derived
    #   by `_tower_legs` (pivot = the head landing's back edge, rot negated, bsign −1)
    #   so the pair is one typed coordinate, not two.
    #   primary, rot −90° : local (px+a, py+b) -> world (px + b, py − a), descent −Y.
    #   second,  rot +90° · bsign −1 : -> world (px + b, py + a), descent +Y.
    #   Tower footprint x 13.20…16.90, y −10.04…+10.04; feet on the shared apron
    #   x 15.10…16.90, y ±1.20.
    east=dict(pivot=(14.10, -1.20), rot=-90.0, kind="switchback",
              kickplate=False),
    # --- west tower = STRAIGHT, the code-compliant control (kickplate ON) -----
    #   primary, rot +90° : local (px+a, py+b) -> world (px − b, py + a), descent +Y.
    #   second,  rot −90° · bsign −1 : -> world (px − b, py − a), descent −Y.
    #   Tower footprint x −15.00…−13.20, y −17.08…+17.08 — two narrow straight legs
    #   hugging the road edge, which is what G11's left tower is.
    west=dict(pivot=(-14.10, 1.20), rot=90.0, kind="straight",
              kickplate=True),
    # --- footbridge deck (width 2.4, runs along x) ---
    # [GT-96 · 08-11 user] rail_z 1.95 -> **1.25**: the 1.95 deck fence was the old
    #   noise-rail height surviving its panels — one of four mixed guard vocabularies
    #   the user read as untidy. One ribbon height for the whole H now; the stepped
    #   end-bay tapers die with the step they existed to hide.
    deck=dict(x0=-13.20, x1=13.20, y0=-1.20, y1=1.20, z_top=5.50, thick=0.40,
              panel_h=1.80, panel_t=0.07, rail_z=1.25, rail_r=0.035),
    #   [v6 ruling (5)] the old noise railing = **one large unbroken panel** (26.4 m long).
    #   with no posts, joints, top cap or see-through bays the deck read as a concrete
    #   bunker corridor, and its shadow side turned 30~45 % of the grid cuts pure black ((4)).
    #   -> posts every 2.2 m + **alternating noise-panel / open bays**. make_pbr has no
    #   transparency input (a literal "clear polycarbonate" cannot be built), so the
    #   see-through stretch is built as **open bays with vertical balusters** - the light
    #   and sight purpose is identical, and it matches real Korean footbridge practice (partial noise panels).
    #   post_h 1.98 = top rail centre rail_z 1.95 + pipe radius 0.035 -> the post
    #   **carries** the rail (so the rail does not float as in the old build).
    #   [W3 S11 · G11] The noise panels are **deleted**. G11 shows a Korean arterial
    #   footbridge whose deck balustrade is a **uniform vertical-baluster guard** for its
    #   whole length — no acoustic infill anywhere on the span — and the v6 "bunker
    #   corridor / pure-black shadow side" finding was a symptom of the panels, not of the
    #   bay rhythm. Every bay is now an open baluster bay, and the baluster pitch is put on
    #   the statutory 안목: `baluster_gap` 0.100 m clear (도로안전시설 지침, the same value
    #   `scene_common.BALUSTER_CLEAR_MAX` gates on `build_railing_line`). The old local loop
    #   ran 6 balusters per 2.05 m bay = **0.32 m clear**, i.e. 3.2× the statute, and it was
    #   invisible to the K4(a) gate because it is scene-local geometry, not a kit call.
    rail_bay=dict(post_t=0.10, post_h=1.29, n_bay=12, joint=0.05,  # [GT-96] 1.98->1.29
                  kick_h=0.16, cap_h=0.07, cap_over=0.03,
                  baluster_r=0.009, baluster_gap=0.100),
    #   support piers - they land on the sidewalk outside the kerb (x +-10.5…11.1). Up to the deck soffit.
    deck_posts=dict(xs=(-11.80, 11.80), y=0.0, r=0.40, z_bot=-0.30,
                    cap_sx=1.0, cap_sy=2.8, cap_h=0.36),
    # --- roadway (6 lanes both ways, along y) ---
    road=dict(x0=-10.50, x1=10.50, y0=-60.0, y1=60.0, z_top=-0.15, thick=0.60),
    #   lane lines: double yellow centre + two sets of white dashes splitting 3 lanes each way (= the "3 lanes" family)
    lane=dict(center_xs=(-0.20, 0.20), dash_xs=(-7.10, -3.60, 3.60, 7.10),
              w=0.15, z=-0.142, t=0.02, seg=3.0, gap=5.0, y0=-58.0, y1=58.0),
    # --- sidewalk (interlocking pavers) + kerb ---
    #   [v6 ruling C-2] the old 34.5 m wide sidewalk read not as openness but as **waste ground**, and the
    #   grass plate met the sky in a straight line. The sidewalk shrank to 29.5 m (the minimum that held
    #   the I-plan stair foot 30.88 + the sign 31.6 + the bench 36) and outside it a planting strip + a
    #   street-tree row + a distant tree band formed the boundary.
    #   [W3 **P11** · `w3_intake_v2_images.md` §7.2 *"S11 §10-1 sidewalk narrowing ADOPTED in principle —
    #   execute per the report's filed coordinates"*] 29.5 m was never a footway; G11's is **4–6 m**.
    #   The two numbers filed in `w3_s11_v1.md` §10-1 are used verbatim and nothing else in the
    #   cross-section is re-opened: `xe1 40.0 → 22.0` and `xw0 −40.0 → −22.0`, i.e. **11.50 m** of
    #   paving per side. The 29.5 m figure was v6 ruling C-2's, but its own justification died with the
    #   I-plan: it was sized to hold a stair foot at x 30.88, and the H-plan put that foot at 16.90.
    #   The planting strip, the street-tree row, the benches, the bus shelter and the stop pole all move
    #   inboard with the edge (`verge` is derived from `xe1`/`xw0`, so it follows without being typed);
    #   the distant tree band and the buildings do **not** move, so strip → band is grass, which is the
    #   other half of what §10-1 filed (*"식재대와 수목 띠 사이는 지면(잔디)로 둔다"*).
    #   **Residual, declared not hidden**: 11.50 m is still ~2× G11's footway. It is the filed number,
    #   and this lane does not re-open a supervisor-adopted coordinate; the measured gap is in the report.
    walk=dict(y0=-60.0, y1=60.0, xw0=-22.0, xw1=-10.50, xe0=10.50, xe1=22.0,
              z_top=-0.005, thick=0.50),
    # --- 보차도 경계석 (S06-B) : `infra_kit.build_curb_line`, NOT a 120 m box -----
    #   The audit's finding for 06/11 was never "add a curb" — the 150 mm exposure was
    #   already right. It was three legibility defects, and all three are closed here:
    #     B-1 material : `granite_dark` ("reads as a black hole", scene01:235) → a light
    #                    granite role (`plaza_light`), per S06-B 3.'s `curb_granite_light`.
    #     B-2 monolith : one 120 m box → **1 m unit blocks** with a 6 mm joint gap and the
    #                    R = 10 mm top arris (`arris="look"`, MOLIT directive 321 fig 2.17,
    #                    carried by `LOOK_CLASS["curb"].bevel`; the material prim is named
    #                    `.../Looks/Curb` so `_look_spec` classes it correctly).
    #     B-3 no gutter: `build_gutter_L` is chained by `gutter=True`, so the section is
    #                    asphalt → L-gutter → curb → sidewalk block, as infra_kit:409 says
    #                    the real Korean section is.
    #   `lod_span` keeps the 1 m rhythm only inside the judged window (world y −22…+24,
    #   which covers both stair feet and every mise-en-scene cut) and coarsens to 8 m
    #   blocks outside it — 1.08 prims/m is unaffordable over 120 m and buys nothing at
    #   40 m distance.
    #   **GT**: `gt_drop = height + gutter drop_at_curb = 0.150 + 0.018 = 0.168 m`, a
    #   continuous linear step along both carriageway edges. Sub-threshold (< 0.30 m), so
    #   it is a step, **not** a negative-obstacle drop — declared as such in the ledger row.
    curb=dict(z_road=-0.150, height=0.150, width=0.20, unit=1.0,
              y0=-60.0, y1=60.0, lod=(38.0, 84.0), far_unit=8.0),
    # --- planting strip (outer sidewalk boundary) : granite kerbstones + groundcover top ---
    #   [W3 P11] the strip is **derived** from the footway edge (`xw0 − w` … `xw0`, `xe1` … `xe1 + w`),
    #   so the narrowing translates it 18.00 m inboard — `x ±40.00…±42.40` → **`x ±22.00…±24.40`** —
    #   without a coordinate being typed. Its outer kerb face is the one ≥ 0.30 m line in the
    #   cross-section (`curb_top +0.14` → site grass `−0.16` = **0.300 m**, at the negative-obstacle
    #   threshold, so a drop and not a step). That line is **translated, not created**; it is declared
    #   in the ledger because it now stands 2.40 m outboard of the footway instead of 20.40 m.
    #   Seen from the footway the strip is an **up-kerb (+0.145)**, so nothing a walker meets falls.
    verge=dict(w=2.40, curb_t=0.20, curb_top=0.14, soil_top=0.10,
               y0=-60.0, y1=60.0),
    # --- site ground (closes the horizon) : 1 cm below the road top face (−0.15) ---
    ground=dict(x0=-150.0, x1=150.0, y0=-150.0, y1=150.0, z_top=-0.16,
                thick=1.40),
    # --- railings (cue_railing) ---
    #   rail_h 1.10 (footbridge standard). Kickplates on the landings only - missing on the east side (the hazard).
    # [GT-105] `rail_mid_*` retired — the descending guards run a single top rail over
    #   the picket screen (ribbon language). Keys kept so the ledger of what the old
    #   build read stays greppable; no builder reads them any more.
    rail=dict(rail_h=1.10, post_r=0.026, rail_r=0.032, rail_mid_r=0.022,
              rail_mid_drop=0.52, spacing=1.00, y_inset=0.03),
    # --- tactile paving (cue_tactile) : 4 stair head/foot locations ---
    #  [W2-D Sec.12.4] scene11 = registered sites `stair_top` / `stair_foot`,
    #  p = 0.54 (Seoul 2015: 430 of 797 km of footway conforming), statutory
    #  trigger "0.3 m before the first tread / after the last". Sec.12.4 keeps
    #  it on **this** scene path, so no `gk` tactile op is emitted. The
    #  non-conforming variant assigned to scene11 is "bearing off by 15 deg"
    #  (mis-installation, 325 of 2,847 complaints) - `skew_deg`.
    #  [W3 S11 · **R11-2**] G11 shows the band **across the walk at the stair foot**, and
    #  that is confirmed here as the standard placement for a footbridge foot (06 and 11
    #  both): a 0.60 m-deep warning band spanning the full flight width, set back
    #  `setback` = 0.30 m from the last riser (편의증진법). The head band keeps the same
    #  0.30 m setback before the first riser. This is a **stair cue**, which R16-2 keeps —
    #  it is not a stop-type device at a halt point, and none is added.
    #  `cue_tactile` stays **OFF by default** (the standing v5.2 user directive); this row
    #  fixes where the band goes when the ablation arm turns it on. See report §4.
    tactile=dict(band_d=0.60, setback=0.30, proud=0.004, skew_deg=15.0),

    # === [W2-D ground_kit] P9 `bridge_deck` - spec Sec.5.3 rows 11 ==========
    #  Grid origin is NOT the world origin: `_grid_shift()` puts it at the east
    #  drop edge (x = east.a_x0 = 15.0, z = 5.50), travel +X. So the plan is
    #  given `origin=(15,0,5.5)` and the edge at forward s = 0.
    #  Prescription:
    #    expansion joints across the deck, span-wise      -> profile step_x 9.0
    #    trodden wear band, centre 0.6-0.9 m, albedo x0.85 -> wear_lane 0.75
    #    rail-foot rundown bands at y = +-1.0             -> edge_break lines
    #    concrete cracking + repair patches                -> crack / patch
    #  `gully` is overridden to 0: `infra_kit.build_gully` sinks a 0.640 m body
    #  and the deck slab is 0.400 m thick, so it would pierce the soffit -
    #  which is the exact surface the `under_grating` preset looks at. A deck
    #  scupper has no builder in the kit; carried as a rider, not faked.
    #  [W3 S11 · user rectangle ban] the two `patch` sites are **deleted**. The user's
    #  standing ban on decorative rectangular ground patterns admits exactly one legitimate
    #  rectangle — a contractor saw-cut asphalt repair on an **asphalt road**. This deck is
    #  a concrete slab bound to `M["concrete"]`, so a saw-cut rectangle on it is the banned
    #  vocabulary, not the licensed one. `crack` / `stain` / `wear_lane` / `edge_break` are
    #  unaffected: none of them is a rectangle. (This is the same reasoning GT-24 applied to
    #  the unit-paved profiles; `bridge_deck` was simply not in that row's scope.)
    gkit=dict(
        deck_pad_x1=15.00,             # include the steel head landing for the
                                       # longitudinal bands (d2 W1 sits on it)
        wear_w=0.75,
        drip_y=(-1.00, 1.00),          # rail-foot rundown, Sec.5.3
        seed=11,
    ),
    # --- Korean sign (cue_sign) : sign_info (footbridge guidance) 768x512 -> w:h = 3:2 ---
    #   at the east stair foot approach + the west foot. 2.6 m clear of the grid sight axis (y=0).
    #   [v6 ruling (4) - cause established] the "unidentified pure-black rectangular panel"
    #   dead centre of `sidewalk_approach` (eye 38,−5,0.9 -> tgt 26,−0.4,3.2) is **not a
    #   floating defect but the back of this sign**. The old yaw 180 deg put the panel
    #   normal on −X, so approaching the stair from the east sidewalk (+X) only the backing shows.
    #   The backing material was M["steel"](0.055,0.058,0.060), hence a pure-black rectangle.
    #   -> (1) east sign yaw 0 (= facing +X, toward the approaching viewer) / west flipped to yaw 180
    #      (2) backing swapped for aluminium grey (M["signback"], 0.44)
    #      (3) keep the 2.6 m clearance from the sight axis (y=0) (corridor-clearing convention).
    #   [W3 S11] the H rebuild moved both stair feet, so the two signs follow them: the east
    #   foot is now at (x 15.10…16.90, y −1.20) and the west foot at (x −15.00…−13.20,
    #   y 17.08). Each sign stands beside its foot, faces the pedestrian walking toward it
    #   along the sidewalk, and keeps clear of the deck sight corridor (|y| ≤ 1.2, x ≤ 15.0).
    sign=dict(w=0.90, h=0.60, pole_h=2.40,
              spots=((18.60, -2.80, 180.0), (-18.60, 15.40, 0.0))),
    # --- dressing ---
    dress=dict(
        # one bus shelter (east sidewalk) - off the grid sight axis (y −9.6…−5.6)
        #   [v6 ruling (5)] the old build was just a roof slab + 4 posts, so it read as a "carport".
        #   the real minimum = rear glass wall + **2 side walls** + bench + **route-map panel**.
        #   [W3 S11] pushed east from x 17.0 to 19.6: the east switchback tower now occupies
        #   x 13.20…16.90, and a shelter 100 mm off the mid-landing face reads as a collision.
        #   [W3 P11] `x 19.60…25.60` no longer fits an 11.50 m footway — 3.60 m of it would have
        #   stood in the planting bed and on the lawn. Squeezing the box to fit between the tower face
        #   (16.90) and the new edge (22.00) would have left a 3.80 m stub marooned 7.4 m from the
        #   kerb, so the shelter keeps its **6.00 × 4.00 m box unchanged** and moves instead to where
        #   a bus shelter belongs — **at the kerb, clear of the tower in y**: `x 11.40…17.40`
        #   (0.90 m back from the kerb block's back face at 10.70) × `y −18.00…−14.00`
        #   (3.96 m south of the east tower footprint, which ends at y −10.04).
        #   `bench_y` follows the back wall (`y0 + 0.10 + 0.90`) so the seat keeps its 0.90 m clearance.
        shelter=dict(x0=11.4, x1=17.4, y0=-18.00, y1=-14.00, z_roof=2.55,
                     post_r=0.08, bench_y=-17.0, side_t=0.05, side_h=2.20,
                     side_inset=0.9, route_w=0.90, route_h=1.10),
        #   [W3 P11] the stop pole cannot keep its old "1.6 m beyond the shelter's outer end" relation
        #   (that lands at x 23.30, in the planting bed). A 정류장 표지 stands at the kerb anyway, so
        #   it goes to `(11.80, −19.60)` — 1.30 m from the kerb block, 1.60 m upstream of the shelter.
        bus_pole=(11.80, -19.60, 3.20),
        #   [W3 S11] lamps moved off the tower footprints (old x ±16.0 stood 1.0 m from the
        #   west leg and 0.9 m from the east one) to x ±19.0, y ±13.0.
        lamps=((19.0, -13.0), (19.0, 13.0), (-19.0, -13.0), (-19.0, 13.0)),
        # street-tree row - [v6 ruling C-2] one row on the planting strip, spacing 7.5 m +- jitter.
        #   [W3 P11] the strip centre moves 41.2 -> **23.2** (= xe1 22.0 + w/2), so the whole 16-tree
        #   row translates 18.0 m inboard. Its y rhythm is untouched.
        #   it draws the sidewalk-grass boundary as a line. The stair corridor (y −2.4…2.4) is left empty.
        lamp=dict(pole_h=6.0, pole_r=0.10, arm_len=1.1, arm_r=0.055, head=0.32),
        #   [W3 S11] the four sidewalk trees at x ±14 / ±26, y ±20 are re-sited to x ±21 /
        #   ±30, y ±23. Under the H-plan `(−14.0, 20.0)` stood 2.9 m in front of the west
        #   stair foot, dead on the tower axis. G11 also shows the ground beside a footbridge
        #   foot **kept clear** — the street-tree row is the middle-distance element there.
        #   [W3 P11] those 8 filler trees existed only to break up a 29.5 m expanse that no longer
        #   exists. They are **not** scaled proportionally into the new footway: (21.0, 30.0) × 11.5/29.5
        #   lands at x 14.6 / 18.1, and x 14.6 sits inside the west tower's x-band (−15.00…−13.20),
        #   i.e. it would put a tree back on the tower axis 5.9 m in front of the west stair foot —
        #   the exact defect the line above records removing. They become **one inner row of 4 per
        #   side at x ±18.60** (outboard of the east tower's 16.90 face and of the west tower's
        #   −15.00 face by 1.70 m / 3.60 m), keeping the street-tree y rhythm at ±23.0 / ±30.0.
        trees=((23.2, -34.0), (23.2, -26.6), (23.2, -19.2), (23.2, -11.6),
               (23.2, 11.8), (23.2, 19.4), (23.2, 26.8), (23.2, 34.2),
               (-23.2, -34.2), (-23.2, -26.8), (-23.2, -19.4), (-23.2, -11.8),
               (-23.2, 11.6), (-23.2, 19.2), (-23.2, 26.6), (-23.2, 34.0),
               (18.6, -23.0), (18.6, 23.0), (18.6, -30.0), (18.6, 30.0),
               (-18.6, -23.0), (-18.6, 23.0), (-18.6, -30.0), (-18.6, 30.0)),
        # [v5.1 §3] benches sit beside street-tree anchors (no even spacing · yaw jitter)
        #   [W3 P11] the bench keeps its **1.40 m offset from the footway edge** (38.6 = 40.0 − 1.4
        #   → 20.6 = 22.0 − 1.4) and therefore stays beside the street-tree anchor at y ∓19.2/19.4.
        benches=((20.6, -19.2, 86.0), (-20.6, 19.2, -94.0)),
        bollards=((12.6, -5.6), (12.6, 5.6), (-12.6, -5.6), (-12.6, 5.6)),
        # [W3 S11 · G13] the storm-water trench grating G11 puts in the sidewalk beside the
        #   stair foot. It is a real drainage fixture with a 30 mm bar pitch — the pitch is
        #   what makes it a grating and not a painted rectangle — so it is outside the
        #   decorative-rectangle ban, not an exception to it.
        #   [GT-80] one per stair foot, and the H now has four feet. The east pair share
        #   one trench on their common apron: the two switchback legs both discharge into
        #   x 15.10…16.90, y −1.20…+1.20, so the trench goes on the apron centreline
        #   (16.00, 0.00) — its old station (16.00, 1.60) would sit **under** the new
        #   north leg's bottom treads. The west legs are straight and end 1.52 m short of
        #   y ±18.60, so the north trench keeps its coordinate and the south one mirrors it.
        gratings=((16.00, 0.00, 0.0), (-14.10, 18.60, 0.0),
                  (-14.10, -18.60, 0.0)),
        grating_len=2.60,
    ),
    # [v6 ruling C-2/C-4] distant closure - a tree silhouette band (distant LOD, a ridge-like row of blocks)
    #   is laid outside the sidewalk so the grass plate never meets the sky directly. It is not a file of
    #   individual trees, so no "lollipop repetition" appears. rows = (x0, x1, h).
    #   [v7 ruling (6)-2] the old build (one **solid box**, 7.5 m segment x 4 m wide x 4.4~4.8 high,
    #   plus one small blob on top) was a continuous plate with a flat top, so against the `midlanding` ·
    #   `deck_walk` background it read as a **painted noise wall (green slab)**.
    #   -> (1) the box is lowered to h·base_frac(0.36) so it only carries the understorey,
    #      (2) the top is made by blobs(3) overlapping canopy blobs per segment (height jittered
    #         0.72~1.16x -> a saw-toothed skyline) (3) segments are cut down to 5.0 m and x jitter +-1.7
    #         gives fore/aft depth (4) the tint is not near-field foliage (deep green) but **three
    #         low-saturation grey-greens reflecting aerial perspective** (leaf_far_*), cycled to kill the flat-slab look.
    #   [J-11 adjudication — this scene WP, as `placement_lint` asks] `jitter` / `x_jit`
    #   here are **size and height variation of a distant LOD silhouette**, which spec
    #   §1.2 X2 explicitly KEEPS; they are not placement jitter of a placed object, which
    #   X2 abolishes. The band is one continuous 100 m-long backdrop element whose only
    #   job is to stop the grass plate meeting the sky in a straight line — remove the
    #   variation and the v7 "painted green slab" finding returns verbatim. Classified,
    #   not silenced: the WARN stays visible in the linter and is answered here.
    treeband=dict(rows=((44.5, 48.5, 4.8), (-48.5, -44.5, 4.4)),
                  y0=-58.0, y1=58.0, seg=5.0, jitter=1.2,
                  base_frac=0.36, blobs=3, x_jit=1.2),
    buildings=dict(
        E=dict(x0=50.0, x1=64.0, y0=-52.0, y1=52.0, h=26.0, floors=8,
               axis="x", facade_x=50.0, face_dir=-1.0, base_z=-0.16),
        W=dict(x0=-64.0, x1=-50.0, y0=-52.0, y1=52.0, h=23.0, floors=7,
               axis="x", facade_x=-50.0, face_dir=1.0, base_z=-0.16),
        NE=dict(x0=16.0, x1=42.0, y0=34.0, y1=48.0, h=19.0, floors=6,
                axis="y", facade_y=34.0, face_dir=-1.0, base_z=-0.16),
        NW=dict(x0=-42.0, x1=-18.0, y0=38.0, y1=50.0, h=14.0, floors=5,
                axis="y", facade_y=38.0, face_dir=-1.0, base_z=-0.16),
        SW=dict(x0=-42.0, x1=-16.0, y0=-48.0, y1=-34.0, h=21.0, floors=7,
                axis="y", facade_y=-34.0, face_dir=1.0, base_z=-0.16),
        SE=dict(x0=18.0, x1=42.0, y0=-50.0, y1=-38.0, h=15.5, floors=5,
                axis="y", facade_y=-38.0, face_dir=1.0, base_z=-0.16),
    ),
    #   [v6 ruling (5)] the window decals **repeated on an exact grid** (deck_walk background), making it
    #   the cut with the worst visible tiling -> window size and column spacing are split per building to break the rhythm.
    window=dict(w=1.3, h=1.7, inset=0.15, col_step=2.8, margin=2.5),
    window_by=dict(
        E=dict(w=1.5, h=1.55, inset=0.15, col_step=3.3, margin=3.4),
        W=dict(w=1.15, h=1.85, inset=0.15, col_step=2.5, margin=2.0),
        NE=dict(w=1.35, h=1.5, inset=0.15, col_step=3.0, margin=2.6),
        NW=dict(w=1.6, h=1.35, inset=0.15, col_step=3.5, margin=3.0),
        SW=dict(w=1.2, h=1.8, inset=0.15, col_step=2.4, margin=1.9),
        SE=dict(w=1.45, h=1.6, inset=0.15, col_step=3.1, margin=2.8),
    ),

    # --- materials (sRGB gamma: dark constant colours live in the 0.02~0.06 band - §A-1) ---
    material=dict(
        # [v7 ruling (6)-1 - cause established] W-1's `metal_rust` UV reduction 1.0 -> 0.25
        #   **did take effect** (passed as make_pbr's 6th positional argument scale_m ->
        #   texture_scale = 1/scale_m = 4.0; since this is OmniPBR "Texture Tiling", a larger
        #   value means more repetition = a smaller pattern. Not `inverted`. The horizontal
        #   autocorrelation half-width of the v6 vs v7 midlanding render also measured 20 px -> 10 px).
        #   The ruling recurred because the cause was **contrast and colour, not scale**:
        #     · metal_rust_diff luminance p5 29 / p95 130 (sRGB) = 18:1 linear contrast.
        #       shrinking the tile leaves the blotch contrast untouched (measured std 33.2 -> 34.7).
        #     · the channel-equalising tint (0.61,0.80,1.00) neutralises **only the mean**.
        #       per pixel it pushes dark rust pixels to red-brown (R 31.7 : B 11.0) and bright
        #       bare-metal pixels to blue-white (R 80.5 : B 127.0), **splitting them further**
        #       and so reinforcing the "white/brown high-contrast blotching".
        #   -> action: (1) tile 0.25 -> 0.55 m (3.3 tiles per 1 m² = the ruling's target band of
        #      "3~5 blotches/m²") (2) compress the albedo range to linear 0.045~0.090 (2.0:1)
        #      with OmniPBR albedo_add/brightness (3) remove the rust / bare-metal colour split
        #      with albedo_desaturation (4) the tint carries a neutral cool grey only.
        #      the normal and roughness textures stay as they are, avoiding a "textureless styrofoam slab" (§4).
        #   [v6] the deck and piers using concrete_floor (107,93,77, a warm brown earth) read as
        #   "rusted steel" (under_grating) -> swapped for concrete_wall (joints and tie holes) plus
        #   an equalising tint (0.72,0.77,0.92) = mean 102 ~ albedo 0.40, a neutral concrete.
        # [GT-108 ⑥ · survey §3.3 / §5 F7] `brick_red` 2.0 → **0.87**, this scene only.
        #   This is the one surface in the survey where the repeat was measured directly:
        #   the s11 brick wall autocorrelates at **0.861 @ 57 px** — i.e. the pattern
        #   visibly restarts every 57 px on screen, which is F7's definition of a tiling
        #   artefact. The cause is the tile: 2.0 m/tile stretches the map to 2.3× real
        #   coursing (a Korean 190 mm brick + 10 mm joint courses at 67 mm), which both
        #   makes each brick oversized and drags the repeat period up into the band the
        #   eye tracks. 0.87 m is the map's real tile. Ledger row 64 ⑥ scopes the
        #   correction to this batch's two scenes; the other 15 are lever-1 spread.
        scale=dict(paving_interlock=1.0, metal_rust=0.55, concrete_wall=2.0,
                   granite_dark=1.0, plaza_light=0.55, brick_red=0.87,
                   grass=1.4, tactile=0.3),
        asphalt_color=(0.045, 0.045, 0.050), asphalt_rough=0.92,
        # [W3 S11 · G11 measured] The footbridge in the target photograph is painted the
        #   standard Korean arterial-overpass **beige-tan**, not grey. Sampled off
        #   `Generated Image - Scene11.jpg`: the sunlit girder face is sRGB (152,144,136)
        #   = linear (0.321, 0.285, 0.249), the shaded lower band sRGB (95,86,72). The v7
        #   ruling's target ("linear median 0.051 ≈ painted-steel dark grey") is therefore
        #   **6× too dark for this scene's own reference**, and its neutral-cool-grey tint is
        #   the wrong hue. The v7 *mechanism* is kept in full — it is the only thing that can
        #   narrow a texture's tonal range, and the white/brown rust blotching it killed must
        #   stay killed — and only its target band is re-aimed:
        #     metal_rust linear p5 0.0116 / p95 0.216  →  0.220 … 0.340
        #     brightness = (0.340−0.220)/(0.216−0.0116) = 0.587
        #     add       = 0.220 − 0.0116·0.587        = 0.213
        #   desaturation is raised 0.55 → 0.78 (the split is wider at the higher level) and
        #   the tint carries the measured beige ratio R:G:B = 1.00 : 0.90 : 0.79.
        metal_tint=(1.00, 0.90, 0.79),          # painted-steel beige-tan (G11 measured)
        # [v7 ruling (6)-1] OmniPBR albedo correction - the texture lookup gets
        #   diffuse = tex*brightness + add to compress the contrast (linear
        #   p5 0.0116/p95 0.216 -> 0.045/0.090), and desaturation erases the colour split.
        #   expected result: linear median 0.051 ~ sRGB 63 = painted-steel dark grey.
        # [GT-107 · 08-11 user] 0.587/0.213/0.78 → 0.42/0.30/0.92: at the judged eye
        #   the residual rust-map variation still read as white peeling ("카펫 조각")
        #   on the walked pads. Mean albedo is preserved (0.45×0.42+0.30 ≈ 0.489 vs
        #   0.477 [computed]); the texture's own range shrinks another 28 % and the
        #   rust hue split closes — painted steel, relief carried by nor/rough only.
        metal_albedo=dict(brightness=0.42, add=0.30, desaturation=0.92),
        concrete_tint=(0.72, 0.77, 0.92),
        parapet_tint=(0.78, 0.83, 0.99),
        soil_tint=(0.42, 0.44, 0.34),
        curb_tint=(0.86, 0.83, 0.78),           # light granite 연석 (S06-B B-1)
        line_white=(0.55, 0.55, 0.52), line_yellow=(0.52, 0.40, 0.06),
        # [W3 S11 · G11] railings, balusters, mesh panels and stringers are the **same
        #   beige-tan paint job** as the girder in the photograph — one paint spec for the
        #   whole structure, which is how a real 육교 is coated. The old dark teal
        #   (0.050, 0.098, 0.108) and near-black steel (0.055) are gone.
        rail_color=(0.300, 0.270, 0.235), rail_rough=0.55, rail_metallic=0.12,
        steel_color=(0.262, 0.236, 0.205), steel_rough=0.55,
        steel_metallic=0.12,
        mesh_color=(0.238, 0.214, 0.186), mesh_rough=0.62,
        # [v6 ruling C-3 family] panel_rough 0.18 = near-specular -> sky reflection makes it look
        #   like a large white board. Lowered to the real gloss of painted steel sheet (0.48).
        panel_color=(0.075, 0.095, 0.105), panel_rough=0.48,
        pole_color=(0.30, 0.31, 0.32), pole_metallic=0.75, pole_rough=0.35,
        lamp_color=(0.88, 0.88, 0.84), lamp_rough=0.40,
        glass_color=(0.06, 0.09, 0.12), glass_rough=0.08,
        parapet_color=(0.58, 0.58, 0.56), parapet_rough=0.60,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        leaf_a=(0.025, 0.045, 0.015), leaf_b=(0.035, 0.060, 0.020),
        # [v7 ruling (6)-2] for the distant (44~48 m) tree band only - three grey-greens whose
        #   saturation and contrast are dropped by aerial perspective. Reusing the near-field leaf_a/b
        #   (deep green) freezes the distance into a "painted board". In sRGB (76,89,70)/(66,79,61)/(86,96,79).
        leaf_far_a=(0.075, 0.100, 0.062),
        leaf_far_b=(0.055, 0.078, 0.048),
        leaf_far_c=(0.095, 0.118, 0.082),
        grass_tint=(0.55, 0.68, 0.42),
        nosing_color=(0.85, 0.72, 0.10),
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
    # [W3 S11 · KEPT AT 171.5 — a rule was broken by the rotation and the break is declared,
    #  not papered over.] Brief R6 fixed this value by a rule: *"the grating slit shadows
    #  stretch along the stair direction, maximising the stripes (the see-through cue)"*. The
    #  slit gaps run along the **descent axis**, so the rule reads "shadow bearing ≈ descent
    #  axis". Old descent +X · φ = 171.5 −110 +233.5 = 295° · shadow bearing (φ−270) = **25°**
    #  ≈ +X ✔. S11-H rotates the descent to **±Y**, so the rule now asks for a shadow bearing
    #  of 90/270°, i.e. SUN_AZ_OFFSET ≈ 56.5.
    #
    #  **That was built and measured, and it is rejected on evidence.** A sun aligned with the
    #  tower axis (±Y) is necessarily *grazing* on the X-facing backdrop façades, which are what
    #  fill the h0.9/h1.8 judged frames. Three-arm probe, same 6 cuts, PT_FAST, one GPU session
    #  (`look_check/_experiments/gates/scene11/260731_sunaz_*`), mean / dark<40:
    #        SUN_AZ   h1.8_d2        h1.8_d5        h0.9_d2        h0.3_d5        under_grating
    #        171.5    139.3 / 3.0 %  142.0 / 2.6 %  156.0 / 1.1 %  160.5 / 3.0 %   81.0 / 2.2 %
    #        131.5    140.8 / 3.0 %  141.4 / 3.5 %  156.6 / 1.7 %  162.9 / 2.1 %   79.6 / 2.6 %
    #         96.5    124.0 / 6.0 %  126.4 / 5.6 %  137.1 / 3.4 %  144.6 / 5.3 %   68.3 / 7.0 %
    #         56.5     77.2 /50.4 %   77.5 /39.1 %   74.8 /26.6 %  116.0 /19.3 %   59.1 /11.2 %
    #  The rule-satisfying value costs the judged grid **−62 mean and +47 pp dark** at h1.8_d2 to
    #  buy one diagnostic cut. 171.5 keeps the grid brighter than its own I-plan baseline
    #  (122.0 / 6.9 %) and `under_grating` reads the open risers, the receding soffits and the
    #  sky through the slits (81.0 / 2.2 % against the baseline's 31.7 / 90.3 %).
    #  **Consequence, stated**: brief R6's shadow-alignment rule is NOT satisfied after S11-H
    #  and cannot be, since it is in direct conflict with backdrop lighting once the descent
    #  axis is ±Y. The smoke report therefore **measures and reports** the backlight angle
    #  instead of asserting it. Supervisor question in `w3_s11_v1.md` §8.
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


# ===========================================================================
# [C] paths + texture roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene11")
ASSET_ROLES = ["paving_interlock", "metal_rust", "concrete_wall",
               "concrete_floor",   # [GT-107] walked-slab family (see M["concrete"])
               "granite_dark", "plaza_light", "brick_red", "grass", "tactile",
               "sign_info", "hdri", "mdl"]


def _flight_run():
    st = PARAMS["stair"]
    return st["n"] * st["tread"]


def _flight_drop():
    st = PARAMS["stair"]
    return st["n"] * st["riser"]


# ===========================================================================
# [C1a] H-plan leg frames — the single source for geometry AND for the numeric
#       self-checks. Everything below is expressed in a leg's **canonical local
#       frame**:
#         a = travel / descent coordinate (a = 0 at the stair head; +a descends)
#         b = transverse coordinate (b = 0 is the centre of the first flight,
#             b = BA0 is the deck face, b = BA1 the outer free edge)
#       A leg is placed by `build_rot_group(pivot, rot)` with a transverse sign
#       `bs` (+1 primary leg, −1 the mirrored second leg of the same tower):
#         rot −90° : world = (px + bs·b, py − a)  →  a = −(y−py), b = bs·(x−px)
#         rot +90° : world = (px − bs·b, py + a)  →  a =  (y−py), b = bs·(px−x)
#       [GT-80] `bs` exists because a tower's two legs are **mirror images**, and a
#       mirror is not in the rotation group `build_rot_group` implements. Negating b
#       in the authoring frame and negating the rotation composes to exactly the
#       mirror, with no negative scale (which would invert prim normals).
# ===========================================================================
def _tower_nodes():
    """(a-coordinates of the leg nodes) — head back, head/stair head, A foot,
    mid landing far edge, and the straight leg's B foot."""
    tw = PARAMS["tower"]
    run = _flight_run()
    a_head = -float(tw["head"])          # −2.40 : back edge of the head landing
    a_A1 = run                           #   7.04 : foot of flight A
    a_M1 = a_A1 + float(tw["mid"])       #   8.84 : far edge of the mid landing
    a_B1 = a_M1 + run                    #  15.88 : straight-leg foot
    return a_head, a_A1, a_M1, a_B1


def _lane_b():
    """Transverse extents (b0, b1) of lane A and of the switchback's lane B."""
    tw = PARAMS["tower"]
    h = float(tw["width"]) / 2.0
    g = float(tw["lane_gap"])
    return (-h, h), (h + g, h + g + float(tw["width"]))


def _leg_to_world(piv, rot, bs, a, b):
    """A leg's canonical (a, b) → world (x, y)."""
    px, py = float(piv[0]), float(piv[1])
    if rot < 0.0:
        return px + bs * b, py - a
    return px - bs * b, py + a


def _world_to_leg(piv, rot, bs, x, y):
    """World (x, y) → that leg's canonical (a, b)."""
    px, py = float(piv[0]), float(piv[1])
    if rot < 0.0:
        return -(y - py), bs * (x - px)
    return (y - py), bs * (px - x)


def _tower_legs(tag):
    """[GT-80] The two legs of a tower, as (name, pivot, rot, bsign).

    An H descends from **both** ends of each head landing. `PARAMS[tag]` types the
    primary leg only; the second is derived — its pivot is the head landing's back
    edge (a = `a_head`, [computed], never typed), its rotation is the primary's
    negated, and its transverse sign is −1 so it is the primary's mirror. Leg names
    carry the world descent bearing, "N" for +Y and "S" for −Y."""
    cfgt = PARAMS[tag]
    px, py = float(cfgt["pivot"][0]), float(cfgt["pivot"][1])
    rot = float(cfgt["rot"])
    a_head = _tower_nodes()[0]
    # world y of the head landing's back edge = the second leg's stair head
    py2 = (py - a_head) if rot < 0.0 else (py + a_head)
    legs = ((f"{tag}_{'N' if rot > 0 else 'S'}", (px, py), rot, 1.0),
            (f"{tag}_{'S' if rot > 0 else 'N'}", (px, py2), -rot, -1.0))
    # [GT-96 · 08-11 user] the EAST tower loses its mirror leg: the double-switchback
    #   pair stacked as a diamond/X in elevation ("계단 다이아 형태로 할 거 같으면
    #   한쪽은 없애면 좋겠어. 굳이 저렇겐 안 만들거든"). The judged cuts keep the
    #   primary (midlanding frames the east SOUTH landing) — east_N goes. GT-80's
    #   "an H has four feet" premise is amended by the user: east descends once.
    if tag == "east":
        # [GT-96 2판 · 08-11 user] keep the NORTH leg, not the south: the bus shelter
        #   sits by the south foot ("버스정류장이 있어서 반대껄 살렸으면 좋았을 것").
        return legs[1:]
    return legs


def _all_legs():
    """(tag, name, pivot, rot, bsign) for all four legs of the H."""
    return [(tag,) + leg for tag in ("east", "west")
            for leg in _tower_legs(tag)]


def _world_to_local(tag, x, y):
    """World (x, y) → that tower's PRIMARY leg canonical (a, b).

    Kept as the tower-level alias the camera code and the grid checks already use;
    the head landing is shared, so a primary-leg (a, b) still names it."""
    _nm, piv, rot, bs = _tower_legs(tag)[0]
    return _world_to_leg(piv, rot, bs, x, y)


def _local_to_world(tag, a, b):
    """That tower's PRIMARY leg canonical (a, b) → world (x, y)."""
    _nm, piv, rot, bs = _tower_legs(tag)[0]
    return _leg_to_world(piv, rot, bs, a, b)


# ===========================================================================
# [C1b] camera numeric-check base - AABB obstacles + solid lookup (single source for ray marching)
#   [v6 ruling instruction] the grounds for the re-aim (`under_grating`) and the sign bearing fix
#   are checked in coordinates. Follows the scene08 `_obstacle_boxes` / `_solid_at` convention.
#   [GT-80] the four legs are no longer reducible to |x|: the tower forms differ and
#   each tower's two legs are mirrors, so the lookup iterates `_all_legs()`.
# ===========================================================================
def _leg_top(kind, a, b):
    """(class, top-face z) of a leg at canonical (a, b); None outside the leg.

    `class` is "pad" for a landing (a 0.40 m steel-deck box, like the bridge deck) and
    "tread" for a grating step (a `tread_t` slab — the slits are ignored so that the
    occlusion test stays conservative)."""
    st = PARAMS["stair"]
    tw = PARAMS["tower"]
    a_head, a_A1, a_M1, a_B1 = _tower_nodes()
    (bA0, bA1), (bB0, bB1) = _lane_b()
    z_top = float(tw["z_top"])
    z_mid = z_top - _flight_drop()
    switch = kind == "switchback"
    # head landing
    if a_head <= a <= 0.0 and bA0 <= b <= bA1:
        return "pad", z_top
    # flight A
    if 0.0 < a <= a_A1 and bA0 <= b <= bA1:
        i = min(st["n"], int(a / st["tread"]) + 1)
        return "tread", z_top - i * st["riser"]
    # mid landing (the switchback leg's landing spans both lanes)
    b_mid1 = bB1 if switch else bA1
    if a_A1 < a <= a_M1 and bA0 <= b <= b_mid1:
        return "pad", z_mid
    # flight B
    if switch:
        if 0.0 <= a <= a_A1 and bB0 <= b <= bB1:
            i = min(st["n"], int((a_A1 - a) / st["tread"]) + 1)
            return "tread", z_mid - i * st["riser"]
    else:
        if a_M1 < a <= a_B1 and bA0 <= b <= bA1:
            i = min(st["n"], int((a - a_M1) / st["tread"]) + 1)
            return "tread", z_mid - i * st["riser"]
    return None


def _tower_top(tag, a, b):
    """Tower-level alias kept for the grid / camera checks (primary-leg frame)."""
    return _leg_top(PARAMS[tag]["kind"], a, b)


def _leg_footprint(tag, piv, rot, bs):
    """World AABB (x0, x1, y0, y1) of one leg's plan footprint (head landing included)."""
    a_head, a_A1, a_M1, a_B1 = _tower_nodes()
    (bA0, bA1), (bB0, bB1) = _lane_b()
    switch = PARAMS[tag]["kind"] == "switchback"
    a_lo, a_hi = a_head, (a_M1 if switch else a_B1)
    b_lo, b_hi = bA0, (bB1 if switch else bA1)
    xs, ys = [], []
    for a in (a_lo, a_hi):
        for b in (b_lo, b_hi):
            wx, wy = _leg_to_world(piv, rot, bs, a, b)
            xs.append(wx)
            ys.append(wy)
    return min(xs), max(xs), min(ys), max(ys)


def _tower_footprint(tag):
    """World AABB (x0, x1, y0, y1) of a tower = the union of its two legs."""
    boxes = [_leg_footprint(tag, piv, rot, bs)
             for _nm, piv, rot, bs in _tower_legs(tag)]
    return (min(b[0] for b in boxes), max(b[1] for b in boxes),
            min(b[2] for b in boxes), max(b[3] for b in boxes))


# ===========================================================================
# [C1c] [GT-80] guard / opening plan model — the gate that would have caught
#       the 08-06 audit finding before it reached a render.
#   Three line families, all in canonical (a, b) and mapped out per leg:
#     guard   : where a guard line is laid (rake rails + landing guard runs)
#     opening : a face a walker must pass through (deck threshold, stair head,
#               flight foot). A guard crossing one is a wall across the route —
#               "the deck dead-ends into a rail".
#     free    : a face with a ≥ 0.30 m drop beyond it, which must be guarded.
#   It is a second expression of the builder's numbers, deliberately: a check
#   written from the same variables catches nothing.
# ===========================================================================
def _leg_lines(tag, piv, rot, bs, with_head):
    """(guards, openings, free_edges) of one leg as world plan segments
    (name, (x0, y0), (x1, y1))."""
    a_head, a_A1, a_M1, a_B1 = _tower_nodes()
    (bA0, bA1), (bB0, bB1) = _lane_b()
    ins = float(PARAMS["rail"]["y_inset"])
    switch = PARAMS[tag]["kind"] == "switchback"
    b_mid1 = bB1 if switch else bA1
    a_foot = 0.0 if switch else a_B1
    bF0, bF1 = (bB0, bB1) if switch else (bA0, bA1)

    wrap = float(PARAMS["tower"]["mid"]) / 4.0
    g = [("RailA0", (0.0, bA0 + ins), (a_A1, bA0 + ins)),
         ("RailA1", (0.0, bA1 - ins), (a_A1, bA1 - ins))]
    if switch:
        g += [("RailB0", (0.0, bB1 - ins), (a_A1, bB1 - ins)),
              ("RailB1", (0.0, bB0 + ins), (a_A1, bB0 + ins)),
              ("MidGuardS0", (a_A1, bA0 + ins), (a_M1 - ins, bA0 + ins)),
              ("MidGuardOut", (a_M1 - ins, bA0 + ins), (a_M1 - ins, bB1 - ins)),
              ("MidGuardS1", (a_M1 - ins, bB1 - ins), (a_A1, bB1 - ins)),
              ("Newel0", (a_A1, bA1 - ins), (a_A1 + wrap, bA1 - ins)),
              ("Newel1", (a_A1 + wrap, bA1 - ins), (a_A1 + wrap, bB0 + ins)),
              ("Newel2", (a_A1 + wrap, bB0 + ins), (a_A1, bB0 + ins))]
    else:
        g += [("RailB0", (a_M1, bA0 + ins), (a_B1, bA0 + ins)),
              ("RailB1", (a_M1, bA1 - ins), (a_B1, bA1 - ins)),
              ("MidGuardS0", (a_A1, bA0 + ins), (a_M1, bA0 + ins)),
              ("MidGuardS1", (a_A1, bA1 - ins), (a_M1, bA1 - ins))]

    o = [("StairHead", (0.0, bA0), (0.0, bA1)),
         ("FlightAFoot", (a_A1, bA0), (a_A1, bA1)),
         ("FlightBHead", (a_A1, bB0), (a_A1, bB1)) if switch
         else ("FlightBHead", (a_M1, bA0), (a_M1, bA1)),
         ("FlightBFoot", (a_foot, bF0), (a_foot, bF1))]

    f = [("FlightA_b0", (0.0, bA0), (a_A1, bA0)),
         ("FlightA_b1", (0.0, bA1), (a_A1, bA1)),
         ("Mid_b0", (a_A1, bA0), (a_M1, bA0)),
         ("Mid_b1", (a_A1, b_mid1), (a_M1, b_mid1))]
    if switch:
        f += [("FlightB_b0", (0.0, bB0), (a_A1, bB0)),
              ("FlightB_b1", (0.0, bB1), (a_A1, bB1)),
              ("Mid_outer", (a_M1, bA0), (a_M1, bB1))]
    else:
        f += [("FlightB_b0", (a_M1, bA0), (a_B1, bA0)),
              ("FlightB_b1", (a_M1, bA1), (a_B1, bA1))]
    if with_head:
        # the shared head landing: outer face guarded, deck face and BOTH stair
        # heads open. The second leg's stair head is this leg's a = a_head face.
        g.append(("HeadGuardOuter", (a_head, bA1 - ins), (0.0, bA1 - ins)))
        f.append(("Head_outer", (a_head, bA1), (0.0, bA1)))
        o.append(("DeckThreshold", (a_head, bA0), (0.0, bA0)))
        if len(_tower_legs(tag)) == 1:
            # [GT-96] no second leg any more: its stair-head face is a 5.505 m
            #   free edge now, closed by the ribbon guard (build side matches).
            g.append(("HeadGuardBack", (a_head, bA0 + ins), (a_head, bA1 - ins)))
            f.append(("Head_back", (a_head, bA0), (a_head, bA1)))

    def _map(rows):
        return [(f"{tag}_{'N' if rot > 0 else 'S'}.{nm}",
                 _leg_to_world(piv, rot, bs, p0[0], p0[1]),
                 _leg_to_world(piv, rot, bs, p1[0], p1[1]))
                for nm, p0, p1 in rows]

    return _map(g), _map(o), _map(f)


def _plan_lines():
    """(guards, openings, free_edges) for the whole H, in world coordinates."""
    G, O, F = [], [], []
    # [GT-96 2판] with_head = each tower's FIRST leg (the old i % 2 assumed two legs
    #   per tower and, at three legs, hung the west head on its mirror — symmetric so
    #   the world segments coincided, but structurally wrong; fixed with the swap).
    for tag in ("east", "west"):
        for j, (_nm, piv, rot, bs) in enumerate(_tower_legs(tag)):
            g, o, f = _leg_lines(tag, piv, rot, bs, with_head=(j == 0))
            G += g
            O += o
            F += f
    return G, O, F


def _seg_blocks(o0, o1, g0, g1, tol=0.08):
    """Does guard segment g **cross** opening segment o, or lie along it?

    A guard that merely terminates on the opening line (a rake rail starting at the
    stair head, a landing guard ending at the corner) is not a block: the crossing
    test excludes the guard's own endpoints."""
    dox, doy = o1[0] - o0[0], o1[1] - o0[1]
    dgx, dgy = g1[0] - g0[0], g1[1] - g0[1]
    wx, wy = g0[0] - o0[0], g0[1] - o0[1]
    den = dox * dgy - doy * dgx
    Lo = math.hypot(dox, doy)
    if Lo < 1e-9:
        return False
    if abs(den) < 1e-9:                    # parallel — a rail laid ON the opening
        if abs(wx * doy - wy * dox) / Lo > tol:
            return False
        ux, uy = dox / Lo, doy / Lo
        ta = wx * ux + wy * uy
        tb = (g1[0] - o0[0]) * ux + (g1[1] - o0[1]) * uy
        return (min(Lo, max(ta, tb)) - max(0.0, min(ta, tb))) > 0.10
    t = (wx * dgy - wy * dgx) / den
    u = (wx * doy - wy * dox) / den
    return (-0.02 <= t <= 1.02) and (0.02 < u < 0.98)


def _guard_termini():
    """World points where a guard run may end without meeting another guard run.

    Two classes only: the four **deck-rail end posts** (0.10 m box, and the deck-side
    rake rail's first post stands inside it, so the deck screen's end standard is the
    stair rail's newel), and each **flight-B foot**, where `build_rail_end` sets a
    newel and knuckle caps. Anything else is a rail terminating in mid-air."""
    dk = PARAMS["deck"]
    _ah, _aA, _aM, a_B1 = _tower_nodes()
    (bA0, bA1), (bB0, bB1) = _lane_b()
    ins = float(PARAMS["rail"]["y_inset"])
    pts = [(dk["x0"], dk["y0"]), (dk["x0"], dk["y1"]),
           (dk["x1"], dk["y0"]), (dk["x1"], dk["y1"])]
    for tag, _nm, piv, rot, bs in _all_legs():
        if PARAMS[tag]["kind"] == "switchback":
            feet = ((0.0, bB0 + ins), (0.0, bB1 - ins))
        else:
            feet = ((a_B1, bA0 + ins), (a_B1, bA1 - ins))
        pts += [_leg_to_world(piv, rot, bs, a, b) for a, b in feet]
    return pts


def _seg_covers(f0, f1, g0, g1, tol=0.08):
    """Length of free edge f that guard segment g runs alongside (parallel, ≤ tol)."""
    dfx, dfy = f1[0] - f0[0], f1[1] - f0[1]
    dgx, dgy = g1[0] - g0[0], g1[1] - g0[1]
    Lf = math.hypot(dfx, dfy)
    if Lf < 1e-9 or abs(dfx * dgy - dfy * dgx) > 1e-6:
        return 0.0                          # not parallel
    ux, uy = dfx / Lf, dfy / Lf
    if abs((g0[0] - f0[0]) * dfy - (g0[1] - f0[1]) * dfx) / Lf > tol:
        return 0.0                          # parallel but on another line
    ta = (g0[0] - f0[0]) * ux + (g0[1] - f0[1]) * uy
    tb = (g1[0] - f0[0]) * ux + (g1[1] - f0[1]) * uy
    return max(0.0, min(Lf, max(ta, tb)) - max(0.0, min(ta, tb)))


def _solid_at(x, y, z):
    """Name of the terrain / structure solid that contains the point (x,y,z), None if there is none.
    Single source for the buried-camera-eye and sight-line (ray march) checks.
    The grating tread is modelled as a thin slab of thickness tread_t (the slits
    are ignored - to keep the occlusion test conservative)."""
    g = PARAMS["ground"]
    rd = PARAMS["road"]
    wk = PARAMS["walk"]
    dk = PARAMS["deck"]
    e = PARAMS["east"]
    st = PARAMS["stair"]
    if g["x0"] <= x <= g["x1"] and g["y0"] <= y <= g["y1"] \
            and g["z_top"] - g["thick"] <= z <= g["z_top"]:
        return "Ground"
    if rd["x0"] <= x <= rd["x1"] and rd["y0"] <= y <= rd["y1"] \
            and rd["z_top"] - rd["thick"] <= z <= rd["z_top"]:
        return "Road"
    for tag, xa, xb in (("Walk_W", wk["xw0"], wk["xw1"]),
                        ("Walk_E", wk["xe0"], wk["xe1"])):
        if xa <= x <= xb and wk["y0"] <= y <= wk["y1"] \
                and wk["z_top"] - wk["thick"] <= z <= wk["z_top"]:
            return tag
    vg = PARAMS["verge"]
    for tag, xa, xb in (("Verge_W", wk["xw0"] - vg["w"], wk["xw0"]),
                        ("Verge_E", wk["xe1"], wk["xe1"] + vg["w"])):
        if xa <= x <= xb and vg["y0"] <= y <= vg["y1"] \
                and -0.30 <= z <= vg["curb_top"]:
            return tag
    # ── deck · support piers · deck railing ──
    if dk["x0"] <= x <= dk["x1"] and dk["y0"] <= y <= dk["y1"] \
            and dk["z_top"] - dk["thick"] <= z <= dk["z_top"]:
        return "Deck"
    dp = PARAMS["deck_posts"]
    for i, px in enumerate(dp["xs"]):
        if math.hypot(x - px, y - dp["y"]) <= dp["r"] \
                and dp["z_bot"] <= z <= dk["z_top"] - dk["thick"]:
            return f"DeckPost_{i}"
    rb = PARAMS["rail_bay"]
    for i, ye in enumerate((dk["y0"], dk["y1"])):
        if abs(y - ye) <= max(dk["panel_t"], rb["post_t"]) / 2.0 \
                and dk["x0"] <= x <= dk["x1"] \
                and dk["z_top"] <= z <= dk["z_top"] + rb["post_h"]:
            return f"DeckRail_{i}"
    # ── the four H-plan legs (no longer symmetric — R11-1 · GT-80) ──
    #   The two legs of a tower share one head landing, so both report it; they
    #   report the same (class, z) for it, which makes the duplicate harmless.
    tw = PARAMS["tower"]
    for tag, _nm, piv, rot, bs in _all_legs():
        a, b = _world_to_leg(piv, rot, bs, x, y)
        hit = _leg_top(PARAMS[tag]["kind"], a, b)
        if hit is None:
            continue
        kind, top = hit
        if kind == "pad":
            if top - float(tw["pad_t"]) <= z <= top:
                return "StairPad"
        elif top - st["tread_t"] <= z <= top:
            return "StairTread"
    # ── bus shelter (roof slab) ──
    sh = PARAMS["dress"]["shelter"]
    if sh["x0"] <= x <= sh["x1"] and sh["y0"] <= y <= sh["y1"] \
            and sh["z_roof"] <= z <= sh["z_roof"] + 0.10:
        return "ShelterRoof"
    # ── distant tree band · buildings ──
    tb = PARAMS["treeband"]
    #   [v7 ruling (6)-2] with the two-tier build (low shrub box + canopy blobs) the silhouette
    #   top rises to h·1.04·1.16 and the x spread grows to +-3.1.
    #   the occlusion test must be **conservative (= larger than reality)**, so the envelope is widened.
    for ri, (xa_, xb_, hh) in enumerate(tb["rows"]):
        if xa_ - 3.2 <= x <= xb_ + 3.2 and tb["y0"] <= y <= tb["y1"] \
                and g["z_top"] <= z <= g["z_top"] \
                + (hh + tb["jitter"]) * 1.21:
            return f"TreeBand_{ri}"
    for key, bd in PARAMS["buildings"].items():
        if bd["x0"] <= x <= bd["x1"] and bd["y0"] <= y <= bd["y1"] \
                and bd.get("base_z", 0.0) - 1.0 <= z \
                <= bd.get("base_z", 0.0) + bd["h"]:
            return f"Building_{key}"
    return None


def _obstacle_boxes():
    """Dressing and railing AABBs for the camera collision check (name, x0,x1, y0,y1, z0,z1).
    Terrain and structure solids are `_solid_at`'s job - only thin prims here."""
    d = PARAMS["dress"]
    gz = PARAMS["walk"]["z_top"]
    boxes = []
    lp = d["lamp"]
    for i, (lx, ly) in enumerate(d["lamps"]):
        boxes.append((f"Lamp_{i}", lx - 1.3, lx + 1.3, ly - 0.6, ly + 0.6,
                      gz, gz + lp["pole_h"]))
    for i, (tx, ty) in enumerate(d["trees"]):
        boxes.append((f"Tree_{i}", tx - 1.1, tx + 1.1, ty - 1.1, ty + 1.1,
                      gz, gz + 4.2))
    for i, (bx, by, _yaw) in enumerate(d["benches"]):
        boxes.append((f"Bench_{i}", bx - 0.4, bx + 0.4, by - 1.0, by + 1.0,
                      gz, gz + 0.5))
    for i, (bx, by) in enumerate(d["bollards"]):
        boxes.append((f"Bollard_{i}", bx - 0.1, bx + 0.1, by - 0.1, by + 0.1,
                      gz, gz + 0.75))
    for i, (gx_, gy_, _yaw) in enumerate(d["gratings"]):
        L = float(d["grating_len"]) / 2.0
        boxes.append((f"Grating_{i}", gx_ - L, gx_ + L, gy_ - 0.25, gy_ + 0.25,
                      gz - 0.10, gz + 0.01))
    bx, by, bh = d["bus_pole"]
    boxes.append(("BusPole", bx - 0.3, bx + 0.3, by - 0.3, by + 0.3, gz,
                  gz + bh))
    sh = d["shelter"]
    boxes.append(("Shelter", sh["x0"], sh["x1"], sh["y0"], sh["y1"], gz,
                  sh["z_roof"] + 0.10))
    for i, (sx, sy, _yaw) in enumerate(PARAMS["sign"]["spots"]):
        boxes.append((f"Sign_{i}", sx - 0.5, sx + 0.5, sy - 0.5, sy + 0.5,
                      gz, gz + PARAMS["sign"]["pole_h"]))
    return boxes


# ===========================================================================
# [C2-b] P11 footway census - the gate the narrowing needs
# ===========================================================================
def _zone_of(x, y):
    """Which ground zone the plan point (x, y) lies in: road / walk / verge / ground.

    The narrowing moves the walk edge 18.00 m inboard, so every ground-standing
    element has to be re-checked against it. This is the single source both the
    census and the eye check below use - nothing is asserted from a typed number."""
    wk = PARAMS["walk"]
    vg = PARAMS["verge"]
    rd = PARAMS["road"]
    if not (wk["y0"] <= y <= wk["y1"]):
        return "ground"
    if rd["x0"] <= x <= rd["x1"]:
        return "road"
    if (wk["xw0"] <= x <= wk["xw1"]) or (wk["xe0"] <= x <= wk["xe1"]):
        return "walk"
    if (wk["xw0"] - vg["w"] <= x <= wk["xw0"]) \
            or (wk["xe1"] <= x <= wk["xe1"] + vg["w"]):
        return "verge"
    return "ground"


def _footway_census():
    """[W3 P11] Every ground-standing dressing element, against the narrowed footway.

    Returns `(name, x, y, zone, allowed, ok)` rows. The street-tree row is the only
    family allowed to stand on the planting strip; everything else must be on the
    paving. Extended elements (shelter, gratings, benches, trees) are tested at
    their AABB extremes as well as at their anchor, so a box that merely *starts*
    on the footway does not pass."""
    d = PARAMS["dress"]
    vsoil_x = PARAMS["walk"]["xe1"] + 0.001
    rows = []

    def _add(name, x, y, hx=0.0, hy=0.0, allowed=("walk",)):
        zs = {_zone_of(x, y)}
        for sx in (-hx, hx):
            for sy in (-hy, hy):
                zs.add(_zone_of(x + sx, y + sy))
        ok = zs.issubset(set(allowed))
        rows.append((name, x, y, "+".join(sorted(zs)), "|".join(allowed), ok))

    for i, (tx, ty) in enumerate(d["trees"]):
        # the street-tree row is the family that stands on the strip; the inner row
        # stands on the paving. Which one a tree is, is decided by the same test the
        # builder uses for its base z (`|x| >= xe1`), never by index.
        on_strip = abs(tx) >= vsoil_x
        _add(f"Tree_{i}{' (strip)' if on_strip else ' (inner)'}", tx, ty,
             1.1, 1.1, ("verge",) if on_strip else ("walk",))
    for i, (bx, by, _yaw) in enumerate(d["benches"]):
        _add(f"Bench_{i}", bx, by, 0.4, 1.0)
    for i, (bx, by) in enumerate(d["bollards"]):
        _add(f"Bollard_{i}", bx, by, 0.1, 0.1)
    for i, (lx, ly) in enumerate(d["lamps"]):
        _add(f"Lamp_{i}", lx, ly, 0.1, 0.1)
    for i, (gx_, gy_, _yaw) in enumerate(d["gratings"]):
        _add(f"Grating_{i}", gx_, gy_, float(d["grating_len"]) / 2.0, 0.15)
    sh = d["shelter"]
    _add("Shelter", (sh["x0"] + sh["x1"]) / 2.0, (sh["y0"] + sh["y1"]) / 2.0,
         (sh["x1"] - sh["x0"]) / 2.0, (sh["y1"] - sh["y0"]) / 2.0)
    _add("BusPole", d["bus_pole"][0], d["bus_pole"][1], 0.3, 0.3)
    for i, (sx, sy, _yaw) in enumerate(PARAMS["sign"]["spots"]):
        _add(f"Sign_{i}", sx, sy, 0.5, 0.5)
    for i, px in enumerate(PARAMS["deck_posts"]["xs"]):
        _add(f"DeckPost_{i}", px, PARAMS["deck_posts"]["y"],
             PARAMS["deck_posts"]["r"], PARAMS["deck_posts"]["r"])
    return rows


# ===========================================================================
# [C2] smoke - geometry self-check before boot (early exit)
# ===========================================================================
def _smoke_report():
    st = PARAMS["stair"]
    e = PARAMS["east"]
    tw = PARAMS["tower"]
    dk = PARAMS["deck"]
    wk = PARAMS["walk"]
    run, drop = _flight_run(), _flight_drop()
    a_head, a_A1, a_M1, a_B1 = _tower_nodes()
    (bA0, bA1), (bB0, bB1) = _lane_b()
    z_top = float(tw["z_top"])
    gz = wk["z_top"]
    print("=" * 68)
    print("scene11_footbridge_stairs — SMOKE 기하 자기검증 (부팅 없음) · H형(S11-H)")
    print("=" * 68)
    print(f"  계단: 폭 {tw['width']:.2f} · {st['n']}단 × 2련/타워 · "
          f"riser {st['riser']} · tread {st['tread']} · 그레이팅 슬릿 {st['slits']}")
    print(f"    련당 run {run:.2f} / drop {drop:.3f} · 경사 "
          f"{math.degrees(math.atan2(st['riser'], st['tread'])):.2f}° · "
          f"2R+T = {2*st['riser']+st['tread']:.3f}")
    tot = 2 * drop
    print(f"    총 낙차 {tot:.3f} = 상판고 {z_top:.2f} → "
          f"{'OK' if abs(tot-z_top) < 1e-9 else 'FAIL'} (접속 단차 0) "
          f"— **I→H 재구축 불변량**")
    print(f"    낙차 ≥ 0.3 m → {'OK' if tot >= 0.3 else 'FAIL'}")
    # ── H-plan: tower footprints, parallel-to-carriageway check ──
    print("  [H형 타워 배치] 차도축 = ±Y · 상판축 = +X · 타워당 다리 2련(GT-80)")
    for tag, nm in (("east", "동측(스위치백)"), ("west", "서측(직선)")):
        fx0, fx1, fy0, fy1 = _tower_footprint(tag)
        span_x, span_y = fx1 - fx0, fy1 - fy0
        par = span_y > span_x            # long axis along the carriageway?
        on_walk = ((wk["xe0"] <= fx0 and fx1 <= wk["xe1"]) or
                   (wk["xw0"] <= fx0 and fx1 <= wk["xw1"]))
        print(f"    {nm:14s} x {fx0:+7.2f}…{fx1:+7.2f} ({span_x:5.2f} m) · "
              f"y {fy0:+7.2f}…{fy1:+7.2f} ({span_y:5.2f} m)")
        print(f"      차도 평행(장축=Y) {'OK' if par else 'FAIL'} · "
              f"보도 위 {'OK' if on_walk else 'FAIL'} · "
              f"차도(±{PARAMS['road']['x1']:.2f}) 침범 "
              f"{'OK(없음)' if fx0 > PARAMS['road']['x1'] or fx1 < PARAMS['road']['x0'] else 'FAIL'}")
        for lnm, piv, lrot, lbs in _tower_legs(tag):
            lx0, lx1, ly0, ly1 = _leg_footprint(tag, piv, lrot, lbs)
            print(f"      · {lnm:8s} pivot ({piv[0]:+7.2f},{piv[1]:+7.2f}) "
                  f"rot {lrot:+6.1f}° bsign {lbs:+.0f} → "
                  f"x {lx0:+7.2f}…{lx1:+7.2f} · y {ly0:+7.2f}…{ly1:+7.2f}")
    fe = _tower_footprint("east")
    fw = _tower_footprint("west")
    asym = abs((fe[1]-fe[0]) - (fw[1]-fw[0])) > 0.5
    print(f"    R11-1 비대칭 H (직선 타워 + 스위치백 타워) "
          f"{'OK' if asym else 'FAIL'}")
    n_legs = len(_all_legs())
    # [GT-96 · 08-11 user] the east tower descends ONCE now (diamond read removed):
    #   GT-80's four-feet premise is amended — the H stands on THREE feet.
    print(f"    다리 수 {n_legs} · 발(하단) 수 {n_legs} → 개정 H형(동측 단일) 3각 "
          f"{'OK' if n_legs == 3 else 'FAIL'}")
    print(f"  [타워 로컬 마디 a] 상부참 {a_head:.2f}…0.00 · A 0.00…{a_A1:.2f} "
          f"· 중간참 {a_A1:.2f}…{a_M1:.2f} · B(직선) {a_M1:.2f}…{a_B1:.2f} "
          f"/ B(스위치백) {a_A1:.2f}→0.00 @ b {bB0:.2f}…{bB1:.2f}")
    # ── walking continuity — one route per leg (GT-80: an H has four) ──
    z_mid = z_top - drop
    print("  [보행 연속성 검증표] 상판 → 상부참(십자) → 각 다리 → 보도 (4경로)")
    bad = 0
    for tag, lnm, piv, lrot, lbs in _all_legs():
        rows = [
            ("상판 → 상부참", dk["z_top"], z_top, "flat"),
            ("계단 A(22단)", z_top, z_mid, "flight"),
            ("중간참", z_mid, z_mid, "flat"),
            ("계단 B(22단)", z_mid, 0.0, "flight"),
            ("계단 → 보도", 0.0, gz, "join"),
        ]
        tot = 0.0
        for nm, z0, z1, kind in rows:
            dz = abs(z1 - z0)
            if kind == "flight":
                ok = abs(dz - drop) < 1e-9
                tot += dz
            elif kind == "flat":
                ok = dz < 1e-9
            else:
                ok = dz <= 0.02
            bad += 0 if ok else 1
            print(f"    [{lnm:7s}] {nm:16s} z {z0:+.3f} → {z1:+.3f}  "
                  f"Δ{dz:+.3f}  {'OK' if ok else 'FAIL'}")
        okt = abs(tot - z_top) < 1e-9
        bad += 0 if okt else 1
        print(f"    [{lnm:7s}] 경로 총 낙차 {tot:.3f} = 상판고 {z_top:.2f} "
              f"{'OK' if okt else 'FAIL'}")
    print(f"    연속성 판정: {'OK' if bad == 0 else f'FAIL({bad})'}")
    # ── hazard ① : the deck-end / tower-head drop the h0.3 grid frames ──
    gx0, gy0, gz0 = _grid_shift()
    print(f"  [위험①] 상판 진행 끝 = 동측 상부참 외측 연단 x {gx0:.2f} · "
          f"상면 {gz0:.3f} → 보도 {gz:+.3f} 낙차 {gz0-gz:.3f} m "
          f"{'OK' if gz0-gz >= 0.3 else 'FAIL'}")
    # [GT-105] 중간 가로대 소거 후에도 은닉축 불변: h0.3 시선은 살대 사이(안목
    #   0.100)로 통과한다 — 개방 판독의 담체는 원래부터 살대 스크린이지 중간
    #   가로대(z 0.58, 눈높이 위)가 아니었다.
    print(f"    난간 개방부(킥 상단 {0.16:.2f}…상부 레일 "
          f"{PARAMS['rail']['rail_h']:.2f} m, 살대 안목 0.100)가 "
          f"h0.3 시야를 통과 → 원거리 보도·차도면이 비쳐 '바닥 연속' 오독")
    # ── hazard ② : missing kickplate on the east mid landings ──
    print(f"  [위험②] 동측 중간참 킥플레이트 {'有' if e['kickplate'] else '無'} "
          f"— 참 상면 {z_mid:.3f} → 보도 {gz:+.3f} 낙차 {z_mid-gz:.3f} m "
          f"{'OK' if not e['kickplate'] else 'FAIL(대조군)'}")
    print(f"    서측 중간참 킥플레이트 "
          f"{'有' if PARAMS['west']['kickplate'] else '無'} (대조군)")
    print(f"    ※ GT-80 로 중간참은 타워당 2개(동 S/N · 서 N/S) — 대조 변수는 "
          f"**타워 단위**로 유지되고 쌍만 2배가 된다. `midlanding` 컷이 겨누는 것은 "
          f"여전히 동측 S 중간참({_local_to_world('east', (a_A1+a_M1)/2.0, (bA1+bB0)/2.0)[0]:+.2f},"
          f"{_local_to_world('east', (a_A1+a_M1)/2.0, (bA1+bB0)/2.0)[1]:+.2f}) 이다.")
    # matched edge class — R11-1 costs the identical-box control, so the pair is
    # held on the 1.80 m transverse side edge that BOTH landings have.
    e_edge = _local_to_world("east", (a_A1 + a_M1) / 2.0, bB1)
    w_edge = _local_to_world("west", (a_A1 + a_M1) / 2.0, bA1)
    print(f"    [대조 쌍 = 정합 연단 등급] 동측 측면 연단 "
          f"({e_edge[0]:+.2f}, {e_edge[1]:+.2f}) vs 서측 ({w_edge[0]:+.2f}, "
          f"{w_edge[1]:+.2f}) — 길이 {tw['mid']:.2f} m · 낙차 {z_mid-gz:.3f} m · "
          f"난간고 {PARAMS['rail']['rail_h']:.2f} m 동일, 킥플레이트만 상이 "
          f"{'OK' if e['kickplate'] != PARAMS['west']['kickplate'] else 'FAIL'}")
    print(f"    ※ R11-1 비대칭 H 의 대가: 두 중간참 자체는 더 이상 합동이 아니다 "
          f"(동 {tw['mid']:.2f}×{bB1-bA0:.2f} · 서 {tw['mid']:.2f}×{bA1-bA0:.2f}).")
    print(f"  [위험③] 그레이팅 투과: 디딤판 {st['slits']}슬릿 × 0.02 m + 전후 "
          f"gap {st['gap']} → 라이저 부재로 하부 직시")
    # ── deck clearance · piers ──
    deck_bot = dk["z_top"] - dk["thick"]
    print(f"  [상판] 상면 {dk['z_top']:.2f} 저면 {deck_bot:.2f} · 차도 "
          f"{PARAMS['road']['z_top']:+.2f} → 유효고 "
          f"{deck_bot-PARAMS['road']['z_top']:.2f} m "
          f"{'OK' if deck_bot-PARAMS['road']['z_top'] >= 4.5 else 'FAIL'}")
    dp = PARAMS["deck_posts"]
    for i, px in enumerate(dp["xs"]):
        on_walk = (wk["xw0"] <= px <= wk["xw1"]) or (wk["xe0"] <= px <= wk["xe1"])
        print(f"    지지 기둥 x={px:+.2f} · 보도 위 {'OK' if on_walk else 'FAIL'} "
              f"· 연석(±{PARAMS['road']['x1']:.2f}) 바깥 "
              f"{'OK' if abs(px) > PARAMS['road']['x1'] else 'FAIL'}")
    # ── rot_group placement check: local (a, b) node → world, all four legs ──
    print("  [rot_group 검산] 로컬 (a,b) → 월드 (x,y) · 다리 4련")
    nodes = (("상부참 후단", a_head, 0.0), ("계단머리", 0.0, 0.0),
             ("A 하단", a_A1, 0.0), ("중간참 외단", a_M1, 0.0))
    n_foot = 0
    for tag, lnm, piv, lrot, lbs in _all_legs():
        outs = []
        for lbl, aa, bb in nodes:
            wx, wy = _leg_to_world(piv, lrot, lbs, aa, bb)
            outs.append(f"{lbl} ({wx:+.2f},{wy:+.2f})")
        print(f"    {lnm:8s} pivot ({piv[0]:+.2f},{piv[1]:+.2f}) : "
              + " · ".join(outs))
        # foot of the descending leg — the last tread's centre line
        if PARAMS[tag]["kind"] == "switchback":
            fx, fy = _leg_to_world(piv, lrot, lbs, 0.0, (bB0 + bB1) / 2.0)
        else:
            fx, fy = _leg_to_world(piv, lrot, lbs, a_B1, 0.0)
        on_walk = ((wk["xe0"] <= fx <= wk["xe1"]) or
                   (wk["xw0"] <= fx <= wk["xw1"])) and wk["y0"] <= fy <= wk["y1"]
        n_foot += 1 if on_walk else 0
        print(f"      계단 하단 ({fx:+.2f}, {fy:+.2f}) ⊂ 보도 "
              f"{'OK' if on_walk else 'FAIL'} · 보도 y {wk['y0']:+.0f}…"
              f"{wk['y1']:+.0f} 연속 → 장면 경계까지 접속 OK (§0-2)")
    print(f"    발 전부 보도 착지 {n_foot}/{len(_all_legs())} "
          f"{'OK' if n_foot == len(_all_legs()) else 'FAIL'}")

    # ── [GT-80] H 완결 게이트: 개구부 폐쇄 0 · 자유 연단 난간 100 % ─────────
    #   The 08-06 audit read "the deck dead-ends into a rail with a building face on
    #   axis". The cause was geometric, not a look problem: the rake rail's horizontal
    #   extension ran the full depth of the head landing, so on the deck side a rail
    #   line sat 0.03 m off the deck face across the whole 2.40 m threshold, and on a
    #   straight leg the mid-landing "Outer" balustrade sat exactly on flight B's top
    #   riser. This gate is what refuses that geometry.
    G, O, F = _plan_lines()
    print(f"  [GT-80 개구부 게이트] 난간선 {len(G)} · 개구부 {len(O)} · "
          f"자유 연단 {len(F)}")
    blocked = []
    for onm, o0, o1 in O:
        for gnm, g0, g1 in G:
            if _seg_blocks(o0, o1, g0, g1):
                blocked.append((onm, gnm))
    for onm, gnm in blocked:
        print(f"    [FAIL] 개구부 {onm} 를 난간 {gnm} 가 가로막음")
    print(f"    개구부 폐쇄 {len(blocked)}건 → "
          f"{'OK(상판 끝·계단머리·계단발 전부 개방)' if not blocked else 'FAIL'}")
    unguarded = []
    for fnm, f0, f1 in F:
        Lf = math.hypot(f1[0] - f0[0], f1[1] - f0[1])
        cov = max([_seg_covers(f0, f1, g0, g1) for _g, g0, g1 in G] + [0.0])
        if Lf > 1e-9 and cov / Lf < 0.90:
            unguarded.append((fnm, cov / Lf))
    for fnm, r in unguarded:
        print(f"    [FAIL] 자유 연단 {fnm} 난간 피복 {r*100:.0f} %")
    print(f"    자유 연단 미피복 {len(unguarded)}건 → "
          f"{'OK(≥90 % 전 연단)' if not unguarded else 'FAIL'}")
    # duplicated lines — two guards in one plane, 0.03 m apart, each with its own
    #   baluster screen. This is what the rake rail's horizontal extension did to the
    #   head-landing and mid-landing guards, and it is a look defect the render shows
    #   as a doubled fence, not a numeric one.
    dup = []
    for i in range(len(G)):
        for j in range(i + 1, len(G)):
            n1, p0, p1 = G[i]
            n2, q0, q1 = G[j]
            ov = _seg_covers(p0, p1, q0, q1, tol=0.10)
            if ov > 0.10:
                dup.append((n1, n2, ov))
    for n1, n2, ov in dup:
        print(f"    [FAIL] 난간선 중복 {n1} ∥ {n2} · 겹침 {ov:.2f} m (≤0.10 m 이격)")
    print(f"    난간선 중복 {len(dup)}건 → "
          f"{'OK(한 면에 난간 한 줄)' if not dup else 'FAIL'}")
    # run ends — every guard endpoint must meet another guard, a deck-rail end post
    #   or a stair-foot newel. Nothing may terminate in mid-air.
    ends = [(nm, p) for nm, p0, p1 in G for p in (p0, p1)]
    term = _guard_termini()
    loose = []
    for nm, p in ends:
        if any(nm2 != nm and math.hypot(p[0]-q[0], p[1]-q[1]) <= 0.05
               for nm2, q in ends):
            continue
        if any(math.hypot(p[0]-t[0], p[1]-t[1]) <= 0.05 for t in term):
            continue
        loose.append((nm, p))
    for nm, p in loose:
        print(f"    [FAIL] 난간 끝단 {nm} ({p[0]:+.2f},{p[1]:+.2f}) 가 허공에서 종료")
    print(f"    난간 끝단 미종결 {len(loose)}건 / 종결점 {len(ends)}개 · "
          f"허용 종단 {len(term)}개(상판 난간 단부주 4 + 계단 발치 뉴엘 8) → "
          f"{'OK' if not loose else 'FAIL'}")
    # ── grid camera vs new geometry coordinate check ──
    gx, gy, gzc = _grid_shift()
    print(f"  [그리드] 원점 = 상판 진행 끝(동측 상부참 외측 연단) "
          f"(x {gx:.2f}, y {gy:.2f}, z {gzc:.2f}) — I형 시절과 **동일 좌표**")
    for d in (2, 5, 10):
        ex = gx - d
        a_e, b_e = _world_to_local("east", ex, gy)
        on_deck = (dk["x0"] <= ex <= dk["x1"]) or \
            (_tower_top("east", a_e, b_e) is not None)
        in_w = dk["y0"] < gy < dk["y1"]
        print(f"    d={d:2d}  eye ({ex:+.2f}, {gy:+.2f}, {gzc+0.3:.2f}~"
              f"{gzc+1.8:.2f}) · 상판/참 위 {'OK' if on_deck else 'FAIL'} "
              f"· 폭 안 {'OK' if in_w else 'FAIL'}")
    print(f"    지지 기둥(x ±11.80, z ≤ {deck_bot:.2f})은 상판 **아래** — "
          f"eye z ≥ {gzc+0.3:.2f} 시선 폐색 없음 OK")
    print(f"    시선 회랑(y −1.2…1.2, x {dk['x0']:.1f}…{gx:.1f} + 타워 발치) "
          f"드레싱 침입: {_corridor_hits()} 개 → "
          f"{'OK' if _corridor_hits() == 0 else 'FAIL'}")

    # ── [W3 P11] 보도 폭 축소 (§10-1 · §7.2 채택) 게이트 ────────────────────
    vg = PARAMS["verge"]
    rdx = PARAMS["road"]["x1"]
    w_e = wk["xe1"] - wk["xe0"]
    w_w = wk["xw1"] - wk["xw0"]
    tb_in = min(min(abs(a), abs(b)) for a, b, _h in PARAMS["treeband"]["rows"])
    print("  [P11 보도 축소] §10-1 등재 좌표 · §7.2 채택")
    print(f"    보도 폭 동 {w_e:.2f} m · 서 {w_w:.2f} m "
          f"(구 29.50 m · G11 실측 4~6 m) → 좌우 대칭 "
          f"{'OK' if abs(w_e - w_w) < 1e-9 else 'FAIL'} · "
          f"G11 대비 잔여차 {w_e - 6.0:+.2f} m **미해소로 신고**")
    print(f"    식재대 x {wk['xe1']:.2f}…{wk['xe1']+vg['w']:.2f} "
          f"(구 40.00…42.40) · 보도측 단차 "
          f"{vg['curb_top']-wk['z_top']:+.3f} m (올라섬) · 외측 연단 낙차 "
          f"{vg['curb_top']-PARAMS['ground']['z_top']:.3f} m "
          f"({'낙차' if vg['curb_top']-PARAMS['ground']['z_top'] >= 0.30 else '단차'}, "
          f"임계 0.30) — **이설이지 신설이 아니다** (x ±42.40 → ±"
          f"{wk['xe1']+vg['w']:.2f})")
    print(f"    식재대 → 수목 띠 사이 잔디 {tb_in - (wk['xe1']+vg['w']):.2f} m "
          f"(수목 띠 x ±{tb_in:.1f} 불변 · §10-1 '지면(잔디)로 둔다')")
    cen = _footway_census()
    bad = [r for r in cen if not r[5]]
    print(f"  [P11 지면 요소 전수] {len(cen)}건 · 위반 {len(bad)}건 → "
          f"{'OK' if not bad else 'FAIL'}")
    for name, x, y, zone, allowed, ok in cen:
        if not ok:
            print(f"    [FAIL] {name:18s} ({x:+7.2f},{y:+7.2f}) zone={zone} "
                  f"허용={allowed}")
    n_strip = sum(1 for r in cen if r[0].endswith("(strip)"))
    n_inner = sum(1 for r in cen if r[0].endswith("(inner)"))
    print(f"    가로수 열 {n_strip}주(식재대) · 내측 열 {n_inner}주(보도) · "
          f"차도(±{rdx:.2f}) 침범 0 "
          f"{'OK' if not any('road' in r[3] for r in cen) else 'FAIL'}")
    # ground-level eyes must stand on the footway - this is the check that caught
    # `sidewalk_approach` at x 24.00, 2.00 m outside the narrowed edge.
    gnd_eyes = [(n, v) for n, v in sorted(build_views().items())
                if abs(v["eye"][2] - wk["z_top"]) < 2.0]
    egood = 0
    for n, v in gnd_eyes:
        z = _zone_of(v["eye"][0], v["eye"][1])
        ok = z == "walk"
        egood += 1 if ok else 0
        print(f"    지면 시점 {n:18s} eye ({v['eye'][0]:+.2f},"
              f"{v['eye'][1]:+.2f},{v['eye'][2]:+.2f}) zone={z} "
              f"{'OK' if ok else 'FAIL(보도 밖)'}")
    print(f"    지면 시점 판정 {egood}/{len(gnd_eyes)} "
          f"{'OK' if egood == len(gnd_eyes) else 'FAIL'}")

    # ── front profile (grid axis y=0, increasing x) - is the drop GT in frame ──
    print("  [정면 프로파일] 그리드 축 y=0.00 · x 15.0 → 20.0 (0.25 m 간격)")
    prof = []
    xx = gx
    while xx <= gx + 5.0:
        topz = None
        zz = 6.5
        while zz > -0.60:
            if _solid_at(xx, gy, zz) is not None:
                topz = zz
                break
            zz -= 0.01
        prof.append((xx, topz))
        xx += 0.25
    for xx, topz in prof:
        print(f"    x {xx:+6.2f}  상면 "
              f"{'개방(지면)' if topz is None else f'{topz:+.3f}'}  "
              f"(상판면 대비 "
              f"{(gz if topz is None else topz) - gzc:+.3f})")
    dmax = max(gzc - (t if t is not None else gz) for _, t in prof)
    print(f"    프로파일 최대 낙차 {dmax:.3f} m ≥ 0.3 → "
          f"{'OK(낙차 GT 프레임 내)' if dmax >= 0.3 else 'FAIL'}")

    # ── h0.3 concealment check (sight line grazing the head-landing edge) ──
    ftx1 = _tower_footprint("east")[1]
    print(f"  [h0.3 은닉 검산] 상부참 연단(x={gx:.1f}, z {gzc:.3f}) 스치는 시선")
    for dd in (2.0, 5.0, 10.0):
        x_hit = gx + (gzc - gz) * dd / 0.3
        print(f"    d={dd:4.1f} m → 보도 재출현 x {x_hit:7.1f} vs 동측 타워 "
              f"외곽 {ftx1:.2f} → 타워 전 구간 은닉 "
              f"{'OK' if x_hit > ftx1 else 'FAIL'}")

    # ── camera collision and sight-line occlusion check (scene08 convention) ──
    boxes = _obstacle_boxes()
    views = build_views()
    print(f"  [카메라 충돌 검산] 뷰 {len(views)}개 × AABB {len(boxes)}개")
    hits = []
    for name, v in sorted(views.items()):
        ex, ey, ez = v["eye"]
        for bn, x0, x1, y0, y1, z0, z1 in boxes:
            if x0 <= ex <= x1 and y0 <= ey <= y1 and z0 <= ez <= z1:
                hits.append((name, bn))
        s = _solid_at(ex, ey, ez)
        if s is not None:
            hits.append((name, f"{s}(지형 매몰)"))
    for name, bn in hits:
        print(f"    [FAIL] {name} eye 가 {bn} 내부")
    print(f"    충돌: {len(hits)}건 → {'OK' if not hits else 'FAIL'}")
    print("    [시선 차단] 미장센 컷 ray march 0.1 m (첫 차단 비율 ≥ 0.90 = OK)")
    print("      ※ preset_* 그리드는 pitch −10° 로 바닥을 겨냥하는 규약 — 제외")
    print("      ※ stair_head 도 동일 등급(로봇 h0.3 이 자기가 선 참 상면을 겨냥)이라 제외")
    # The test asks "did dressing get in the way?". A cut that deliberately aims at the
    # walked surface it stands on cannot pass it — that is why `preset_*` is excluded, and
    # `stair_head` is the same class of cut (h0.3 on the head landing, pitch −10°).
    floor_aimed = ("stair_head",)
    blocked = []
    for name, v in sorted(views.items()):
        if name.startswith("preset_") or name in floor_aimed:
            continue
        eA = np.array(v["eye"], dtype=float)
        tg = np.array(v["tgt"], dtype=float)
        Ln = float(np.linalg.norm(tg - eA))
        frac, hit = 1.0, None
        for k in range(1, int(Ln / 0.1) + 1):
            f = k * 0.1 / Ln
            s = _solid_at(*(eA + (tg - eA) * f))
            if s is not None:
                frac, hit = f, s
                break
        ok = frac >= 0.90
        print(f"      {name:18s} 첫 차단 {frac:5.2f} "
              f"({hit if hit else '없음'}) → {'OK' if ok else 'FAIL'}")
        if not ok:
            blocked.append(name)
    print(f"      차단 컷: {blocked if blocked else '없음 → OK'}")

    # ── under_grating backlight axis check (grounds for the v6 ruling (4) re-aim) ──
    ug = build_views()["under_grating"]
    ve = np.array(ug["tgt"], dtype=float) - np.array(ug["eye"], dtype=float)
    ve /= np.linalg.norm(ve)
    # dome rotation φ = SUN_AZ_OFFSET + noon_dome_rot + hdri_sun_rotz_offset,
    #   horizontal shadow bearing = atan2(cosφ, −sinφ), sun bearing = shadow + 180 deg
    phi = (PARAMS["SUN_AZ_OFFSET"] - 110.0 + 233.5) % 360.0
    shadow_az = math.degrees(math.atan2(math.cos(math.radians(phi)),
                                        -math.sin(math.radians(phi)))) % 360.0
    sun_az = (shadow_az + 180.0) % 360.0
    cam_az = math.degrees(math.atan2(ve[1], ve[0])) % 360.0
    cam_el = math.degrees(math.asin(max(-1.0, min(1.0, ve[2]))))
    daz = abs((cam_az - sun_az + 180.0) % 360.0 - 180.0)
    print(f"  [under_grating 역광 축 — 측정·판정 보류] 그림자 방위 {shadow_az:.1f}° → "
          f"태양 방위 {sun_az:.1f}°/고도 {PARAMS['light']['noon_sun_elev']:.1f}°")
    print(f"    카메라 시선 방위 {cam_az:.1f}° · 고도 {cam_el:+.1f}° → 태양과 "
          f"방위차 {daz:.1f}°  ({'역광대(≤45°)' if daz <= 45.0 else '측광/순광(>45°)'})")
    print("    ※ S11-H 로 하강축이 ±Y 로 회전하면서 브리핑 R6 의 '그림자 방위 ≈ 하강축'")
    print("      규칙과 배경 입면 조명이 구조적으로 충돌한다. 3팔 실측 결과 규칙 충족값")
    print("      (SUN_AZ 56.5)은 판정 그리드를 h1.8_d2 기준 mean −62·dark +47 pp 파괴한다.")
    print("      → 171.5 유지, 이 항목은 **FAIL 게이트가 아니라 측정 보고**로 강등. 근거는")
    print("        PARAMS 주석의 3팔 표와 look_check/_experiments/gates/scene11/260731_sunaz_*")

    # ── [v7 ruling (6)-3] under_grating frame occupancy check ──
    #   the v6->v7 re-aim failed because "the backlight is right but the sky eats the frame",
    #   so an axis check alone is not enough. With `_solid_at` as the single source the frame
    #   is ray-cast coarsely (32x18) to measure the sky fraction and the main subject directly.
    #   the FOV is back-computed from the v6 render (hFOV half-angle 32.6 deg / vFOV half-angle 19.8 deg, 16:9).
    def _frame_occupancy(eye, tgt, nx=32, ny=18, far=70.0):
        e = np.array(eye, dtype=float)
        fwd = np.array(tgt, dtype=float) - e
        fwd /= np.linalg.norm(fwd)
        rgt = np.cross(fwd, np.array([0.0, 0.0, 1.0]))
        rgt /= np.linalg.norm(rgt)
        upv = np.cross(rgt, fwd)
        th, tv = math.tan(math.radians(32.6)), math.tan(math.radians(19.8))
        sky, cnt = 0, {}
        for j in range(ny):
            sv = (1.0 - 2.0 * (j + 0.5) / ny) * tv
            for i in range(nx):
                su = (2.0 * (i + 0.5) / nx - 1.0) * th
                d = fwd + rgt * su + upv * sv
                d /= np.linalg.norm(d)
                t, what = 0.05, None
                while t < far:
                    what = _solid_at(*(e + d * t))
                    if what is not None:
                        break
                    t += 0.05 if t < 10.0 else 0.30
                if what is None:
                    sky += 1
                else:
                    cnt[what] = cnt.get(what, 0) + 1
        return sky / float(nx * ny), cnt

    sky_f, subj = _frame_occupancy(ug["eye"], ug["tgt"])
    top = sorted(subj.items(), key=lambda kv: -kv[1])[:3]
    print(f"    프레임 점유(레이캐스트 32×18) 하늘 {sky_f*100:.1f} % → "
          f"{'OK(≤30 % — 슬릿 투광 판독 가능)' if sky_f <= 0.30 else 'FAIL(하늘 과다)'}")
    print(f"    주 피사체 {[(n, c) for n, c in top]}  "
          f"(구 컷 eye(22.0,0,0.60)→tgt(16.0,0,4.20) 은 하늘 64.7 %)")
    print("=" * 68)


def _grid_shift():
    """Grid origin = **the drop edge a deck-travelling robot meets head-on**.

    Under the H-plan that is the outer (+X) edge of the east head landing, which the
    tower geometry places at exactly the coordinate the I-plan grid already used
    (x 15.00, y 0, z 5.50) — so the judge presets did not move. Beyond it is a
    5.505 m fall to the east sidewalk."""
    tw = PARAMS["tower"]
    (_, bA1), _ = _lane_b()
    px, _py = PARAMS["east"]["pivot"]
    return (px + bA1, 0.0, float(tw["z_top"]))


def _corridor_hits():
    """Dressing prims standing inside a sight corridor that could hide a drop.

    Two corridors, not one: (1) the deck + head-landing run the h0.3 grid travels
    (|y| ≤ 1.2, x −13.2…15.0) and (2) each tower's plan footprint, because a lamp or
    a tree inside a tower would occlude the very flights the mise-en-scene cuts judge.
    **Flush ground fixtures are excluded by construction** — the trench gratings sit
    at or below the walk surface and cannot occlude anything."""
    d = PARAMS["dress"]
    pts = list(d["trees"]) + list(d["lamps"]) + list(d["bollards"]) \
        + [(b[0], b[1]) for b in d["benches"]] + [d["bus_pole"][:2]]
    sh = d["shelter"]
    pts += [((sh["x0"]+sh["x1"])/2.0, (sh["y0"]+sh["y1"])/2.0)]
    pts += [(s[0], s[1]) for s in PARAMS["sign"]["spots"]]
    gx, _, _ = _grid_shift()
    boxes = [(PARAMS["deck"]["x0"], gx, -1.2, 1.2)]
    boxes += [_tower_footprint(t) for t in ("east", "west")]
    n = 0
    for x, y in pts:
        for x0, x1, y0, y1 in boxes:
            if x0 <= x <= x1 and y0 <= y <= y1:
                n += 1
                break
    return n


# ===========================================================================
# [C-2] ground_kit plan - pure CPU, no USD. Coordinates from PARAMS (Sec.7.4).
# ===========================================================================
def ground_plan():
    """P9 `bridge_deck` plan for the footbridge deck (z = 5.50, travel +X)."""
    g = PARAMS["gkit"]
    dk = PARAMS["deck"]
    gx, gy, gz = _grid_shift()
    return gk.plan_ground(
        "bridge_deck",
        region=(float(dk["x0"]), float(dk["y0"]),
                float(g["deck_pad_x1"]), float(dk["y1"])),
        z=float(dk["z_top"]), gy=float(gy), origin=(gx, gy, gz), axis="+x",
        edges=[("deck_end", 0.0)],
        dists=(2, 5, 10), scene="scene11",
        tactile=(),                 # Sec.12.4 - kept on the scene's own path
        sites=dict(),
        overrides=dict(
            infra=dict(gully=0),    # see the PARAMS note: soffit pierce
            surface=(("patch", 0), ("crack", 4),
                     ("stain", ("water", "drip"))),
            extras=(("wear_lane", dict(width=float(g["wear_w"]))),
                    ("edge_break", dict(density=0.0,
                                        lines=list(g["drip_y"]))))),
        seed=int(g["seed"]))


# ===========================================================================
# [D] camera presets - grid_views (along the deck, +X) + 5 mise-en-scene cuts
# ===========================================================================
def build_views():
    """Shift the grid origin to (east drop start x=15.0, deck z=5.5).
    Judging priority 1: at the robot's h0.3 (= z 5.8), do the grating see-through,
    the vanishing nosing and the open mid landing hold? The ground-level sidewalk
    approach is provided separately as the sidewalk_approach cut."""
    gx, gy, gz = _grid_shift()
    v = sc.grid_views(gy)
    out = {}
    for k, val in v.items():
        e, t = list(val["eye"]), list(val["tgt"])
        e[0] += gx
        e[2] += gz
        t[0] += gx
        t[2] += gz
        out[k] = dict(eye=e, tgt=t)
    a_head, a_A1, a_M1, a_B1 = _tower_nodes()
    (bA0, bA1), (bB0, bB1) = _lane_b()
    z_mid = float(PARAMS["tower"]["z_top"]) - _flight_drop()
    # under_grating: [v7 ruling (6)-3 re-aim - cause of the repeat failure]
    #   v6->v7 got the axis right (dead centre of the y=0 slit · ascending −X · backlit) but
    #   **eye z 0.60 · elevation +31 deg** was the problem. With a low eye and a shallow aim
    #   the whole soffit hangs **above** the sight line (from that same eye the soffit rises at
    #   34 deg at the far end x=15 and 90 deg at the near end x=22). The frame centre was
    #   effectively aimed at the **sky beyond** the stair head, so the sky ate 64.7 %
    #   (measured by the _solid_at ray cast). The sun (bearing 205 deg · elevation 49.8 deg) also
    #   sat unoccluded at the top of the frame and threw flare.
    #   -> raise the eye to just under the flight A soffit (x 21.70, headroom 0.83 m) and
    #      pitch the aim up to **+50 deg**. tgt is set at the **point on the tread soffit**
    #      that sight line first meets (x 20.79, z 3.08 - the smoke below checks it), so the
    #      sight-line occlusion test (first block >=0.90) still passes unchanged.
    #   measured (same ray cast): sky 18.5 % · frame subject 100 % StairTread ·
    #      the sun is **occluded** by the tread (no direct disc = only slit light remains).
    #   [W3 S11] re-derived for the H-plan. The east flight A now descends along −Y at
    #   x 13.20…15.00, so the backlit under-soffit station moves under **that** flight.
    #   The backlight condition (sun bearing 205°, so the camera bearing must be within
    #   45° of it) is re-checked numerically by the smoke report, not assumed.
    #   Station: on the sidewalk under east flight A near its low end, aimed **up the
    #   slope** (+Y, bearing 90°) so the soffit fills the frame and the sun (bearing 90°
    #   after the SUN_AZ_OFFSET re-derivation) sits straight ahead = maximum slit light.
    #   Numbers, not taste: eye z 2.00 keeps the v7 headroom convention exactly
    #   (0.83 m under the flight-A soffit at that station) and pitch +48° measures
    #   **sky 13.9 % · StairTread 78.5 %** on the same 32×18 `_solid_at` raycast the
    #   v7 ruling used — the v7 cut measured 18.5 % sky, the v6 one 64.7 %.
    #   [GT-80] the cut is **unmoved**; the reading shifted 14.2 → 13.9 % sky only
    #   because the completed north leg now occupies part of the upper frame that was
    #   open sky. It stands under the east SOUTH flight A, which the leg completion
    #   does not touch, and the sight-line block test is unchanged.
    # [GT-96 2판] mirrored +Y with the kept NORTH leg (fixed-coordinate cut).
    out["under_grating"] = dict(eye=[14.10, 7.90, 2.00],
                                tgt=[14.10, 5.76, 4.38])
    # deck_walk: pedestrian view along the deck (h1.6) — now an all-open baluster corridor
    out["deck_walk"] = dict(eye=[-9.00, 0.00, 7.10], tgt=[8.00, 0.00, 6.30])
    # midlanding: robot view on the east mid landing (h0.3) - head-on at the open band left by the missing kickplate
    mx, my = _local_to_world("east", (a_A1 + a_M1) / 2.0 - 0.55, (bA1 + bB0) / 2.0)
    tx, ty = _local_to_world("east", a_M1 + 3.20, (bA1 + bB0) / 2.0)
    out["midlanding"] = dict(eye=[mx, my, z_mid + 0.30],
                             tgt=[tx, ty, z_mid - 0.45])
    # sidewalk_approach: brief R6 "sidewalk approach" - along the east sidewalk toward the
    #   switchback tower's foot (now at x 15.10…16.90, y −1.20)
    #   [W3 P11] the old eye (24.00, 3.20, 0.90) is 2.00 m **outside** the narrowed footway — it
    #   would stand in the planting bed, which is not a sidewalk approach.
    #   The first fix slid it 3.00 m forward along its own ground bearing to (21.40, 1.70, 0.90).
    #   **The pilot refuted that** and the numbers are kept rather than hidden: on the same 48×27
    #   `_solid_at` raycast the cut's own subject disappeared — footway occupancy **10.9 % → 0.0 %**,
    #   tower 12.7 → 21.6 %, eye-to-foot 8.78 → 5.78 m — i.e. a 5.8 m portrait of a stringer, which
    #   cannot answer this cut's checklist question (sign facing the approacher · trench grating ·
    #   walk + kerb read as 육교 at a glance), and it is what the OCCL flag on the first pilot was
    #   measuring. A sidewalk approach is walked **along the sidewalk**, so the eye is re-sited to
    #   (19.60, 8.60, 0.90) — on the footway, 2.40 m inside its outer edge, approaching the foot
    #   from +Y with **the target, the eye height and the frame composition unchanged**:
    #   sky 37.3 → 37.3 % · tower 12.7 → 12.5 % · footway 10.9 → **17.2 %** · d 8.78 → 10.31 m.
    #   **This is a mise-en-scène cut, not one of the 9 judge presets** — those come out of
    #   `sc.grid_views` above and are byte-identical across both rounds.
    #   [GT-96 2판] tgt y −1.20 → +1.20: the surviving east foot is the NORTH one.
    out["sidewalk_approach"] = dict(eye=[19.60, 8.60, 0.90],
                                    tgt=[16.40, 1.20, 2.80])
    # overview: high-angle full view of the footbridge (6 lanes, deck and both towers at once)
    out["overview"] = dict(eye=[44.00, -34.00, 17.00], tgt=[0.00, 2.00, 3.60])
    # stair_head: [W3 S11 · new] the H-plan puts the stair head 1.20 m off the deck axis,
    #   so the stair-cue judgement gets its own robot-height cut: h0.3 on the east head
    #   landing, head-on at the first riser line and the flight falling away along −Y.
    hx, hy = _local_to_world("east", -1.70, 0.0)
    sx, sy = _local_to_world("east", 3.60, 0.0)
    out["stair_head"] = dict(eye=[hx, hy, float(PARAMS["tower"]["z_top"]) + 0.30],
                             tgt=[sx, sy, float(PARAMS["tower"]["z_top"]) - 1.05])
    return out


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트 — GT-80 S11 H형 완결(다리 4련)]
 1. overview         — **H형인가**: 계단 타워 2기가 차도(±Y)에 평행하고 상판이
                       그 사이를 건너는가 · 서측 2련 + 동측 1련[GT-96 2판] = 발 3개 ·
                       비대칭(서=직선 타워 / 동=스위치백 타워)
 1b. deck_walk 끝     — 상판 끝이 **난간 벽으로 막히지 않고** 십자 참에서 좌우로
                       계단이 갈라져 내려가는가 (구: 난간 + 배경 벽면)
 1c. 서측 중간참       — 중간참에서 하행 계단이 **난간으로 막히지 않는가**
                       (구: 직선 다리 a=A_M1 에 전폭 난간이 서 있었다)
 2. h0.3 그리드      — 상판 진행 끝(x=15.0) 5.505 m 낙차가 난간 하부 개방대로
                       은닉되는가 (원경 보도·차도면이 '바닥 연속'으로 읽히나)
 3. stair_head       — 계단머리(축에서 1.20 m 옆)에서 하강이 즉독되는가
 4. midlanding       — 동측 S 중간참 난간 하부 개방대(킥플레이트 無) 2.755 m 낙차
                       · 서측 정합 연단은 킥플레이트 有
 4b. 마감            — 난간이 두 줄로 겹치거나(30 mm 간격) 모서리에 기둥이
                       2개 겹쳐 서 있지 않은가 · 계단 발치 난간 끝에 뉴엘/캡이
                       있는가 · 중간 가로대가 참에서 끊기지 않는가
 5. under_grating    — 역광: 라이저 부재 하부 투시 + 슬릿 투광 스트라이프
 6. deck_walk        — **방음판 폐지** 후 전 구간 개방 간살 회랑(G11) ·
                       간살 안목 100 mm · 상판 유효고 5.25 m
 7. sidewalk_approach— 안내 사인이 접근자를 마주보는지 · 트렌치 그레이팅 ·
                       보도/연석(1 m 단위 줄눈)/식재대로 '육교' 즉독
 8. [G11] 도장색     — 상판 거더·계단 스트링거·난간이 **베이지톤 도장**인가
                       (구 중성 다크그레이 0.051 이 아니라 선형 0.22~0.34)
 9. [S06-B] 연석     — 1 m 단위 블록 줄눈 + L형 측구 + R10 모서리가 읽히는가
                       (구 120 m 단일 박스 · granite_dark '검은 구멍' 폐지)
10. 사각 패턴        — 지면에 장식 사각형이 남아 있지 않은가(구 GratingBand 2매
                       · 상판 보수패치 2매 삭제 — 그레이팅은 30 mm 바 피치 실물)
11. 계절            — G11 = 여름. 낙엽·개화 혼입이 없는가
12. [v7] 수목 띠     — 배경 수목 띠가 톱니 상단 저채도 회록 수관 군락인가"""


# ===========================================================================
# [E] main
# ===========================================================================
def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"

    if os.environ.get("NEGOBS_SMOKE", "0") == "1":
        _smoke_report()
        return

    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])
    simulation_app = sc.boot(capture_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from pxr import UsdGeom
    from omni.kit.viewport.utility import (get_active_viewport,
                                           capture_viewport_to_file)
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    ROOT = "/World/Scene11"
    UsdGeom.Xform.Define(stage, ROOT)

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    st = PARAMS["stair"]
    TW = PARAMS["tower"]
    RUN, DROP = _flight_run(), _flight_drop()
    Z_TOP = float(TW["z_top"])
    Z_MID = Z_TOP - DROP
    A_HEAD, A_A1, A_M1, A_B1 = _tower_nodes()
    (BA0, BA1), (BB0, BB1) = _lane_b()

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *a, **kw):
        return sc.make_pbr(stage, path, *a, **kw)

    def PBR_ALBEDO(path, *a, albedo=None, **kw):
        """[v7 ruling (6)-1] make_pbr + the OmniPBR albedo range correction inputs.

        `scene_common.make_pbr` does not expose albedo_add/brightness/desaturation
        (and scene_common is shared by 21 scenes, so the rule is not to modify it).
        → here we only **add inputs** to the shader prim make_pbr created.
        By the OmniPBR.mdl definition (file lines 62 · 68 · 74) all three are float,
        and they apply in the order base::file_texture(color_offset=add,
        color_scale=brightness) → lerp(tint, mono, desaturation), i.e.
            diffuse = lerp(tex*brightness + add,  mono(...),  desaturation)
        so **the tonal range of the texture itself can be compressed** (a tint is a
        multiply and cannot narrow the range — the cause of the v6/v7 re-rulings).
        """
        mtl = sc.make_pbr(stage, path, *a, **kw)
        if albedo:
            from pxr import UsdShade, Sdf
            sh = UsdShade.Shader.Get(stage, path + "/Shader")
            for key in ("brightness", "add", "desaturation"):
                if key in albedo:
                    sh.CreateInput(f"albedo_{key}",
                                   Sdf.ValueTypeNames.Float).Set(
                        float(albedo[key]))
        return mtl

    # -------------------------------------------------------------------
    # materials
    # -------------------------------------------------------------------
    def setup_materials():
        s = mp["scale"]
        M = {}
        M["paving"] = PBR(f"{ROOT}/Looks/Paving",
                          sc.tex_path("paving_interlock", "diff"),
                          sc.tex_path("paving_interlock", "nor"),
                          sc.tex_path("paving_interlock", "rough"),
                          s["paving_interlock"])
        # [GT-108 ③ · survey §4.4] Tint split — same roll, second tint. The two
        #   footways sit on opposite sides of a carriageway and are physically two
        #   separate laying jobs; a single material across both is the "one continuous
        #   tone" §2.2 read as "면". −6 % [computed: eff linear 0.268 → 0.252, gap
        #   0.016, far inside survey §7's ≤ 0.10 rule], and the boundary is the road
        #   itself, so there is no shared edge that could read as a cut-out (survey
        #   §4.5 condition (a)).
        M["paving_e"] = PBR(f"{ROOT}/Looks/PavingE",
                            sc.tex_path("paving_interlock", "diff"),
                            sc.tex_path("paving_interlock", "nor"),
                            sc.tex_path("paving_interlock", "rough"),
                            s["paving_interlock"], tint=(0.94, 0.94, 0.95))
        # steel stairs and landings - [v7 ruling (6)-1] metal_rust is used only as **relief (normal,
        #   roughness)**, while the albedo range is compressed with add/brightness and the rust /
        #   bare-metal colour split is removed with desaturation -> a "painted steel sheet with local rust" look.
        M["metal"] = PBR_ALBEDO(f"{ROOT}/Looks/Metal",
                                sc.tex_path("metal_rust", "diff"),
                                sc.tex_path("metal_rust", "nor"),
                                sc.tex_path("metal_rust", "rough"),
                                s["metal_rust"], tint=mp["metal_tint"],
                                albedo=mp["metal_albedo"])
        # [GT-107 · 08-11 user] concrete_wall → concrete_floor: this material skins
        #   WALKED slabs (deck slab, landings, pier caps), and the wall texture's
        #   whitewash blotches read on a floor as "카펫 이상한 모양 자른" peeling.
        #   The parapet (vertical) keeps concrete_wall below — that is what the
        #   texture is for. Scale key unchanged (same tiling density class).
        M["concrete"] = PBR(f"{ROOT}/Looks/Concrete",
                            sc.tex_path("concrete_floor", "diff"),
                            sc.tex_path("concrete_floor", "nor"),
                            sc.tex_path("concrete_floor", "rough"),
                            s["concrete_wall"], tint=mp["concrete_tint"])
        # [GT-108 ③] third tint on the concrete roll — the pier shafts and caps. They
        #   are a separate pour from the deck they carry, they are vertical (so they
        #   take run-down streaking the walked slab never gets) and they stand in the
        #   splash zone of the carriageway. −8 % [computed: eff linear 0.088 → 0.081].
        #   Kept on the `Concrete` name stem so `_look_spec` still lands on the concrete
        #   class — the survey's §8-4 lesson is that the name **is** the classifier.
        M["concrete_pier"] = PBR(f"{ROOT}/Looks/ConcretePier",
                                 sc.tex_path("concrete_floor", "diff"),
                                 sc.tex_path("concrete_floor", "nor"),
                                 sc.tex_path("concrete_floor", "rough"),
                                 s["concrete_wall"],
                                 tint=tuple(c * 0.92 for c in mp["concrete_tint"]))
        M["soil"] = PBR(f"{ROOT}/Looks/Soil", sc.tex_path("grass", "diff"),
                        sc.tex_path("grass", "nor"),
                        sc.tex_path("grass", "rough"), 1.2,
                        tint=mp["soil_tint"])
        # [S06-B B-1] `curb_granite_light`. The material prim keeps the name `Curb` so
        #   `_look_spec` classes it as the curb class and `LOOK_CLASS["curb"].bevel` =
        #   10 mm supplies the R10 arris `build_curb_line(arris="look")` relies on
        #   (verified at build time by `ik.check_arris_role`). `granite_dark` is
        #   **prohibited** here — scene01:235 recorded that it "reads as a black hole".
        M["curb"] = PBR(f"{ROOT}/Looks/Curb",
                        sc.tex_path("plaza_light", "diff"),
                        sc.tex_path("plaza_light", "nor"),
                        sc.tex_path("plaza_light", "rough"), s["plaza_light"],
                        tint=mp["curb_tint"])
        M["brick"] = PBR(f"{ROOT}/Looks/Brick",
                         sc.tex_path("brick_red", "diff"),
                         sc.tex_path("brick_red", "nor"),
                         sc.tex_path("brick_red", "rough"), s["brick_red"])
        M["grass"] = PBR(f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
                         sc.tex_path("grass", "nor"),
                         sc.tex_path("grass", "rough"), s["grass"],
                         tint=mp["grass_tint"])
        M["tactile"] = PBR(f"{ROOT}/Looks/Tactile",
                           sc.tex_path("tactile", "diff"),
                           sc.tex_path("tactile", "nor"), None, s["tactile"])
        M["asphalt"] = PBR(f"{ROOT}/Looks/Asphalt",
                           diffuse_color=mp["asphalt_color"],
                           roughness_const=mp["asphalt_rough"])
        M["line_w"] = PBR(f"{ROOT}/Looks/LineWhite",
                          diffuse_color=mp["line_white"], roughness_const=0.7)
        M["line_y"] = PBR(f"{ROOT}/Looks/LineYellow",
                          diffuse_color=mp["line_yellow"], roughness_const=0.7)
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        # [W2 fix batch F1] Ground-class decal materials for the kit.
        #   Binding kit crack / stain / wear elements to the scene's joint-sealant
        #   (`paint` class), steel (`metal`) or kerb constants is what rendered them
        #   as flat texture-less ribbons and mats: those classes are excluded from
        #   `_CONST_MDL_CLASSES` **by design** (a constant colour is physically right
        #   for paint and metal), so a *ground* prim bound to one gets no texture at
        #   all. `GKitCrack` / `GKitStain` classify as concrete, so they are promoted
        #   to a real ground texture with the intended albedo preserved.
        M["gk_crack"] = PBR(f"{ROOT}/Looks/GKitCrack",
                            diffuse_color=(0.055, 0.055, 0.056),
                            roughness_const=0.92)
        M["gk_stain"] = PBR(f"{ROOT}/Looks/GKitStain",
                            diffuse_color=(0.20, 0.20, 0.195),
                            roughness_const=0.86)
        M["steel"] = PBR(f"{ROOT}/Looks/Steel", diffuse_color=mp["steel_color"],
                         metallic=mp["steel_metallic"],
                         roughness_const=mp["steel_rough"])
        # [G11] the expanded-metal infill panel at each tower head, built as a real bar
        #   grid (make_pbr has no transparency input, so a literal perforated sheet is
        #   not buildable — the grid is the honest construction, not a fake).
        # [GT-108 ④ · survey §8-4] `Looks/Mesh` → **`Looks/MeshSteel`**. "mesh" matches
        #   no `_LOOK_RULES` token and no `LOOK_ROLE` key, so this expanded-metal panel
        #   was falling to **`misc`** — the deliberately conservative bucket for genuinely
        #   unknown materials — while it is plainly steel. Same failure mode as the four
        #   §8-4 catalogued and as `PostTimber`/`Looks/Polish` before it: the name **is**
        #   the classifier. Adding a "mesh" token to `_LOOK_RULES` would reclassify all
        #   33 scenes, which ledger row 64 ④ scopes out, so the fix is local: the "steel"
        #   token lands it on metal. Visual delta is the class bevel only, 0.003 → 0.002 m
        #   — sub-pixel at the judged distance; metal carries no detail normal (nothing
        #   procured, `_DETAIL_FALLBACK["metal"]` is empty) and stays an OmniPBR constant
        #   in both classes, so `metallic=0.10` is unaffected.
        M["mesh"] = PBR(f"{ROOT}/Looks/MeshSteel",
                        diffuse_color=mp["mesh_color"],
                        metallic=0.10, roughness_const=mp["mesh_rough"])
        M["panel"] = PBR(f"{ROOT}/Looks/Panel", diffuse_color=mp["panel_color"],
                         roughness_const=mp["panel_rough"])
        M["pole"] = PBR(f"{ROOT}/Looks/Pole", diffuse_color=mp["pole_color"],
                        metallic=mp["pole_metallic"],
                        roughness_const=mp["pole_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/Glass", diffuse_color=mp["glass_color"],
                         roughness_const=mp["glass_rough"])
        # [v6 C-3 family] avoids a textureless flat slab (styrofoam look) - a concrete texture.
        #   reused for the sign backing as well, to block the "pure-black floating panel" misreading.
        M["parapet"] = PBR(f"{ROOT}/Looks/Parapet",
                           sc.tex_path("concrete_wall", "diff"),
                           sc.tex_path("concrete_wall", "nor"),
                           sc.tex_path("concrete_wall", "rough"),
                           s["concrete_wall"], tint=mp["parapet_tint"])
        M["signback"] = PBR(f"{ROOT}/Looks/SignBack",
                            diffuse_color=(0.44, 0.45, 0.46),
                            metallic=0.25, roughness_const=0.55)
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["leaf_a"] = PBR(f"{ROOT}/Looks/LeafA", diffuse_color=mp["leaf_a"],
                          roughness_const=1.0, specular_level=0.0)
        M["leaf_b"] = PBR(f"{ROOT}/Looks/LeafB", diffuse_color=mp["leaf_b"],
                          roughness_const=1.0, specular_level=0.0)
        # [v7 ruling (6)-2] three low-saturation grey-greens for the distant tree band only (aerial perspective)
        for tag in ("a", "b", "c"):
            M[f"leaf_far_{tag}"] = PBR(
                f"{ROOT}/Looks/LeafFar{tag.upper()}",
                diffuse_color=mp[f"leaf_far_{tag}"],
                roughness_const=1.0, specular_level=0.0)
        M["nosing"] = PBR(f"{ROOT}/Looks/Nosing",
                          diffuse_color=mp["nosing_color"],
                          roughness_const=0.7)
        # [v5 shared layer] Korean sign panel - sign_info (footbridge guidance), uv_mode 1:1
        M["sign"] = PBR(f"{ROOT}/Looks/SignPanel",
                        diff=sc.tex_path("sign_info", "diff"),
                        uv_mode=True, roughness_const=0.6)
        return M

    # -------------------------------------------------------------------
    # site ground · roadway · sidewalk · kerb · lane lines
    # -------------------------------------------------------------------
    def build_site(M):
        g = PARAMS["ground"]
        BOX(f"{ROOT}/Ground",
            ((g["x0"]+g["x1"])/2.0, (g["y0"]+g["y1"])/2.0,
             g["z_top"] - g["thick"]/2.0),
            (g["x1"]-g["x0"], g["y1"]-g["y0"], g["thick"]), M["grass"], col=True)
        rd = PARAMS["road"]
        BOX(f"{ROOT}/Road",
            ((rd["x0"]+rd["x1"])/2.0, (rd["y0"]+rd["y1"])/2.0,
             rd["z_top"] - rd["thick"]/2.0),
            (rd["x1"]-rd["x0"], rd["y1"]-rd["y0"], rd["thick"]),
            M["asphalt"], col=True)
        wk = PARAMS["walk"]
        for i, (xa, xb) in enumerate(((wk["xw0"], wk["xw1"]),
                                      (wk["xe0"], wk["xe1"]))):
            BOX(f"{ROOT}/Walk_{i}",
                ((xa+xb)/2.0, (wk["y0"]+wk["y1"])/2.0,
                 wk["z_top"] - wk["thick"]/2.0),
                (xb-xa, wk["y1"]-wk["y0"], wk["thick"]),
                M["paving"] if i == 0 else M["paving_e"],   # [GT-108 ③]
                col=True)
        # ── 보차도 경계석 · S06-B (K5 `build_curb_line`) ─────────────────────
        #   The `road_side` argument names **where the carriageway is** relative to the
        #   direction of travel p0→p1; the block body extends the other way. Both lines
        #   run +Y, so the west line (road to its right) is "right" and the east line
        #   (road to its left) is "left". Getting this backwards would push the blocks
        #   into the carriageway, so it is asserted below rather than trusted.
        cb = PARAMS["curb"]
        kit = ik.kit_from_scene_common(sc, stage)
        ik.check_arris_role(sc)
        for i, (xe, side) in enumerate(((rd["x0"], "right"), (rd["x1"], "left"))):
            res = ik.build_curb_line(
                kit, f"{ROOT}/Curb_{i}",
                (xe, cb["y0"]), (xe, cb["y1"]), M["curb"],
                height=float(cb["height"]), width=float(cb["width"]),
                unit=float(cb["unit"]), gutter=True,
                z_road=float(cb["z_road"]), walk_z=float(wk["z_top"]),
                road_side=side, arris="look",
                lod_span=tuple(cb["lod"]), far_unit=float(cb["far_unit"]),
                gutter_mtl=M["concrete"], joint_mtl=M["gk_crack"])
            print(f"[S06-B] Curb_{i} · 블록 {res['n_blocks']} · 단위 "
                  f"{res['unit_actual']:.3f} m · 노출 {res['exposure_road']:.3f} · "
                  f"연석면 {res['face_h_at_kerb']:.3f} · gt_drop {res['gt_drop']:.3f} "
                  f"· 위험낙차 {res['is_gt_hazard']} · 프림 {res['prim_count']} "
                  f"({res['prims_per_m']:.2f}/m)")
            for w in res["warnings"]:
                print(f"[S06-B][경고] Curb_{i}: {w}")
        # [v6 ruling C-2] planting strip - one row on the outer sidewalk boundary (2 kerb lines + groundcover).
        vg = PARAMS["verge"]
        vy0, vy1 = vg["y0"], vg["y1"]
        for i, (xa, xb) in enumerate(((wk["xw0"] - vg["w"], wk["xw0"]),
                                      (wk["xe1"], wk["xe1"] + vg["w"]))):
            for j, xc in enumerate((xa + vg["curb_t"]/2.0,
                                    xb - vg["curb_t"]/2.0)):
                BOX(f"{ROOT}/VergeCurb_{i}_{j}",
                    (xc, (vy0+vy1)/2.0, vg["curb_top"] - 0.22),
                    (vg["curb_t"], vy1-vy0, 0.44), M["curb"], col=True)
            BOX(f"{ROOT}/VergeSoil_{i}",
                ((xa+xb)/2.0, (vy0+vy1)/2.0, vg["soil_top"] - 0.20),
                ((xb-xa) - 2*vg["curb_t"], vy1-vy0, 0.40), M["soil"], col=True)

    def build_lanes(M):
        ln = PARAMS["lane"]
        for i, x in enumerate(ln["center_xs"]):
            BOX(f"{ROOT}/CenterLine_{i}", (x, (ln["y0"]+ln["y1"])/2.0, ln["z"]),
                (ln["w"], ln["y1"]-ln["y0"], ln["t"]), M["line_y"])
        period = ln["seg"] + ln["gap"]
        ndash = int((ln["y1"] - ln["y0"]) / period)
        for j, x in enumerate(ln["dash_xs"]):
            for k in range(ndash):
                yc = ln["y0"] + k*period + ln["seg"]/2.0
                BOX(f"{ROOT}/Dash_{j}_{k}", (x, yc, ln["z"]),
                    (ln["w"], ln["seg"], ln["t"]), M["line_w"])
        # [W3 S11] the two `GratingBand_*` road slabs are **deleted**. They were a pair of
        #   16.5 × 2.8 m dark rectangles laid on the carriageway purely as a contrast
        #   surface for the grating slit shadows — decorative rectangular ground patterns
        #   of exactly the kind the user banned, and under the H-plan the stairs no longer
        #   overhang the carriageway at all, so the device had lost even its pretext.

    # -------------------------------------------------------------------
    # deck + support piers
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # [W2-D] ground_kit - P9 bridge_deck on the footbridge deck.
    # -------------------------------------------------------------------
    def build_ground_kit(M):
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        M2.update(joint=M["steel"], crack=M["gk_crack"], patch=M["concrete"],
                  patch_cut=M["gk_crack"], stain_water=M["gk_stain"],
                  stain_drip=M["gk_stain"], wear=M["gk_stain"],
                  edge_break=M["gk_stain"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", ground_plan(), M2,
                              skin_exclude=sc.skin_exclude)
        print(f"[ground_kit] scene11 P9 · 프림 {res['prims']} · "
              f"δmax {res['gt_delta_max']:.4f} · unit_cell {res['unit_cell']}")
        return res

    def build_deck(M):
        dk = PARAMS["deck"]
        # [W2-0 P-A] The deck is what ground_kit decorates. `_SKIN_DENY`
        #   already contains "deck", but the registration is explicit so the
        #   guarantee does not rest on a path token.
        sc.skin_exclude(f"{ROOT}/Deck")
        BOX(f"{ROOT}/Deck",
            ((dk["x0"]+dk["x1"])/2.0, (dk["y0"]+dk["y1"])/2.0,
             dk["z_top"] - dk["thick"]/2.0),
            (dk["x1"]-dk["x0"], dk["y1"]-dk["y0"], dk["thick"]),
            M["concrete"], col=True)
        dp = PARAMS["deck_posts"]
        z1 = dk["z_top"] - dk["thick"]
        for i, px in enumerate(dp["xs"]):
            # [GT-108 ③] pier tint — see `Looks/ConcretePier`
            CYL(f"{ROOT}/DeckPost_{i}", (px, dp["y"], (dp["z_bot"]+z1)/2.0),
                dp["r"], z1-dp["z_bot"], M["concrete_pier"], col=True)
            BOX(f"{ROOT}/DeckCap_{i}",
                (px, dp["y"], z1 - dp["cap_h"]/2.0),
                (dp["cap_sx"], dp["cap_sy"], dp["cap_h"]), M["concrete_pier"])

    # -------------------------------------------------------------------
    # one stair set (top landing -> A -> mid landing -> B). Serves local and world under prefix.
    #   x0_pad : west end of the top landing, everything after it descends in +X. kick = kickplate or not.
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # [W3 S11 · GT-80] shared landing balustrade — the deck-end / landing-perimeter
    #   guard G11 shows: posts, a kick band, vertical balusters at the statutory
    #   100 mm 안목, a capping top rail and a mid rail. Used wherever
    #   `build_railing_line` (a *stair* railing: it needs a run and a drop) does not
    #   apply, i.e. on every landing.
    # -------------------------------------------------------------------
    def build_guard_run(M, prefix, pts, z_base, height=None, kick=0.16,
                        post_pitch=2.0, post_t=0.08):
        """One **continuous** guard polyline through `pts` (world XY, axis-aligned).

        [GT-80] Three finishing rules the previous two-point builder could not keep:
          · a corner carries **one shared post**. Two abutting 2-point runs stacked
            two coincident 0.08 m posts on the shared node — identical coplanar faces,
            i.e. z-fighting, at every mid-landing corner.
          · ~~a mid rail at `rail_mid_drop`~~ — [GT-105 · 08-11 user] deleted: the
            flight rails no longer carry a mid line to meet, and the middle horizontal
            read as a second vocabulary crossing the picket screen.
          · a **knuckle cap** at every node and both run ends, closing each mitre and
            each terminus so no rail shows an open cylinder mouth.
        Nothing here touches a walked surface: guard members only."""
        ra = PARAMS["rail"]
        rb = PARAMS["rail_bay"]
        if height is None:
            height = float(ra["rail_h"])
        P = [(float(p[0]), float(p[1])) for p in pts]
        if len(P) < 2:
            return 0
        z_rail = z_base + height
        # [GT-105] mid rail deleted from the landing/head guards: the balusters below
        #   run kick → top at the statutory 안목, so the middle horizontal carried no
        #   screen and read as a second vocabulary against the GT-96 ribbon.
        pitch = 2.0 * rb["baluster_r"] + rb["baluster_gap"]
        npost = 0
        nbal = 0
        made = 0
        # one post per node — corners shared, never doubled
        for nx, ny in P:
            BOX(f"{prefix}/Post_{npost}", (nx, ny, z_base + height / 2.0),
                (post_t, post_t, height), M["steel"])
            npost += 1
            made += 1
        for s_i in range(len(P) - 1):
            x0, y0 = P[s_i]
            x1, y1 = P[s_i + 1]
            L = math.hypot(x1 - x0, y1 - y0)
            if L < 1e-6:
                continue
            ux, uy = (x1 - x0) / L, (y1 - y0) / L
            along_x = abs(ux) > abs(uy)
            for i in range(1, max(1, int(round(L / post_pitch)))):
                t = L * i / max(1, int(round(L / post_pitch)))
                BOX(f"{prefix}/Post_{npost}",
                    (x0 + ux * t, y0 + uy * t, z_base + height / 2.0),
                    (post_t, post_t, height), M["steel"])
                npost += 1
                made += 1
            BOX(f"{prefix}/Kick_{s_i}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, z_base + kick / 2.0),
                (L if along_x else 0.05, 0.05 if along_x else L, kick),
                M["rail"])
            made += 1
            bz0, bz1 = z_base + kick, z_rail - float(ra["rail_r"])
            n_b = max(2, int(L / pitch))
            for b in range(n_b):
                t = L * (b + 0.5) / n_b
                CYL(f"{prefix}/Bal_{nbal}",
                    (x0 + ux * t, y0 + uy * t, (bz0 + bz1) / 2.0),
                    rb["baluster_r"], bz1 - bz0, M["rail"])
                nbal += 1
                made += 1
            CYL(f"{prefix}/TopRail_{s_i}",
                ((x0 + x1) / 2.0, (y0 + y1) / 2.0, z_rail),
                float(ra["rail_r"]), L, M["rail"],
                rotY=(90.0 if along_x else 0.0),
                rotX=(0.0 if along_x else 90.0))
            made += 1
        for i, (nx, ny) in enumerate(P):
            rr = float(ra["rail_r"])
            CYL(f"{prefix}/TopCap_{i}", (nx, ny, z_rail), rr * 1.15, 2.2 * rr,
                M["rail"])
            made += 1
        return made

    def build_rail_end(M, prefix, tag, x, y, z_base, height=None):
        """A run-end newel + knuckle caps for a `build_railing_line` terminus.

        `build_railing_line` stops its top and mid rails dead at the last post with an
        open cylinder mouth — acceptable where a landing guard continues the line, not
        at a **stair foot**, which is the one end a pedestrian meets at eye level."""
        ra = PARAMS["rail"]
        if height is None:
            height = float(ra["rail_h"])
        BOX(f"{prefix}/{tag}Newel", (x, y, z_base + height / 2.0),
            (0.08, 0.08, height), M["steel"])
        # [GT-105] top cap only — the flight rails this newel closes no longer carry
        #   a mid rail, so a mid-height cap would cap nothing.
        rr = float(ra["rail_r"])
        CYL(f"{prefix}/{tag}CapTop", (x, y, z_base + height), rr * 1.15,
            2.2 * rr, M["rail"])
        return 2

    # -------------------------------------------------------------------
    # [W3 S11 · G11] expanded-metal infill panel over the tower head — the
    #   triangular mesh sheet the photograph shows above the stair top. Built as a
    #   real bar grid: `make_pbr` has no transparency input, so a perforated sheet
    #   cannot be a texture; the grid is the honest construction.
    # -------------------------------------------------------------------
    def build_mesh_panel(M, prefix, p0, p1, z_bot_fn, z_top, pitch=0.22):
        """Trapezoidal expanded-metal infill: a horizontal top edge over a raked
        bottom edge — the panel G11 shows at the head of its left tower, filling the
        triangle between the stair's rake rail and the deck rail level.

        `z_bot_fn(s)` gives the bottom edge at arc length `s` along p0→p1, so the
        panel follows the flight instead of being a flat rectangle. Bars only: the
        material layer has no transparency input, so a perforated sheet is not
        buildable and a solid box would be a lie about what you can see through."""
        x0, y0 = float(p0[0]), float(p0[1])
        x1, y1 = float(p1[0]), float(p1[1])
        L = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        along_x = abs(ux) > abs(uy)
        t = 0.014
        made = 0
        nv = max(2, int(L / pitch))
        for i in range(nv):
            s = L * (i + 0.5) / nv
            zb = float(z_bot_fn(s))
            if z_top - zb < 0.05:
                continue
            BOX(f"{prefix}/V_{i}", (x0 + ux*s, y0 + uy*s, (zb + z_top)/2.0),
                (t, t, z_top - zb), M["mesh"])
            made += 1
        # horizontals only across the stretch where the trapezoid is tall enough
        z_lo = min(float(z_bot_fn(0.0)), float(z_bot_fn(L)))
        nh = max(1, int((z_top - z_lo) / pitch))
        for j in range(nh):
            zz = z_lo + (z_top - z_lo) * (j + 0.5) / nh
            # clip to the part of the run whose bottom edge is already below zz
            ss = [L * (k + 0.5) / (nv * 2) for k in range(nv * 2)]
            inside = [s for s in ss if z_bot_fn(s) <= zz]
            if len(inside) < 2:
                continue
            sa, sb = min(inside), max(inside)
            Ls = sb - sa
            sc_ = (sa + sb) / 2.0
            BOX(f"{prefix}/H_{j}", (x0 + ux*sc_, y0 + uy*sc_, zz),
                (Ls if along_x else t, t if along_x else Ls, t), M["mesh"])
            made += 1
        return made

    # -------------------------------------------------------------------
    # One descending LEG of an H tower. Authored in the canonical local frame
    #   (descent → local +a, local b = flight width) and placed by
    #   `build_rot_group(pivot, rot)`, so the leg lands parallel to the carriageway.
    #   `bs` (+1 / −1) is the transverse sign: a tower's second leg is the **mirror**
    #   of the first, and every authored b passes through `_B` so one body serves all
    #   four legs and no coordinate is typed twice.
    #   `kind` picks the leg form:
    #     "straight"   : head → A → mid landing → B, all in +a  (west, control)
    #     "switchback" : head → A → mid landing → B **back along −a** on the
    #                    neighbouring lane, via a nested 180° rot_group  (east)
    #   `kick` is the mid-landing kickplate: absent on the east tower = the hazard.
    #   `with_head` marks the leg that owns the SHARED head landing (pad, columns,
    #   outer guard) — built once per tower, not once per leg.
    # -------------------------------------------------------------------
    def build_leg(M, prefix, piv, bs, kind, kick, with_head, solo=False):
        px, py = float(piv[0]), float(piv[1])
        ra = PARAMS["rail"]
        ins = float(ra["y_inset"])
        pad_t = float(TW["pad_t"])
        hw = float(TW["width"]) / 2.0
        switch = (kind == "switchback")
        cols = []

        def _A(a):
            return px + float(a)

        def _B(b):
            return py + bs * float(b)

        def _ys(b0, b1):
            """(y_lo, y_hi) of a transverse span — `bs` = −1 reverses the order, and a
            builder must never be handed a negative size (a negative scale would flip
            prim normals)."""
            return (min(_B(b0), _B(b1)), max(_B(b0), _B(b1)))

        def _pad(name, a0, a1, b0, b1, ztop):
            ylo, yhi = _ys(b0, b1)
            BOX(f"{prefix}/{name}",
                (_A((a0+a1)/2.0), (ylo+yhi)/2.0, ztop - pad_t/2.0),
                (a1-a0, yhi-ylo, pad_t), M["metal"], col=True)
            # [GT-102 · 08-11 user] ONE BIG column per landing — the four slim
            #   corner posts mixed vocabularies with the deck's r0.40 piers ("네
            #   기둥으로 받치고.. 큰 기둥으로 받치고.. 왔다갔다"). Same radius as
            #   the deck piers, centred under the pad.
            zt = ztop - pad_t
            R_ = float(PARAMS["deck_posts"]["r"])
            ca, cb = (a0 + a1) / 2.0, (b0 + b1) / 2.0
            CYL(f"{prefix}/{name}Col",
                (_A(ca), _B(cb), (float(TW['col_z_bot'])+zt)/2.0),
                R_, zt - float(TW["col_z_bot"]), M["metal"], col=True)
            cols.append((_A(ca), _B(cb)))

        # ── head landing — a CROSS landing, built by the primary leg only ──
        if with_head:
            _pad("HeadPad", A_HEAD, 0.0, BA0, BA1, Z_TOP)
        # ── flight A ─────────────────────────────────────────────────────
        ylo, yhi = _ys(BA0, BA1)
        sc.build_open_riser_stairs(
            stage, f"{prefix}/FlightA", _A(0.0), ylo, yhi, st["riser"],
            st["tread"], st["n"], Z_TOP, M["metal"], M["metal"],
            tread_t=st["tread_t"], gap=st["gap"], slits=st["slits"])
        # ── mid landing ──────────────────────────────────────────────────
        b_mid1 = BB1 if switch else BA1
        _pad("MidLanding", A_A1, A_M1, BA0, b_mid1, Z_MID)
        # ── flight B ─────────────────────────────────────────────────────
        if switch:
            # 180° about (_A(RUN/2), _B((BA0+BB1)/2)) maps the canonical flight
            #   (a 0…RUN, b BA0…BA1, descending +a) onto (a RUN…0, b BB0…BB1),
            #   i.e. the return lane descending back toward the tower head. The pivot
            #   is taken through `_B`, so the mirrored leg's return lane still lands
            #   outboard instead of swinging over the kerb.
            pb = sc.build_rot_group(stage, f"{prefix}/BackGroup",
                                    (_A(RUN / 2.0), _B((BA0 + BB1) / 2.0)), 180.0)
            a_b0 = 0.0
        else:
            pb = prefix
            a_b0 = A_M1
        sc.build_open_riser_stairs(
            stage, f"{pb}/FlightB", _A(a_b0), ylo, yhi, st["riser"],
            st["tread"], st["n"], Z_MID, M["metal"], M["metal"],
            tread_t=st["tread_t"], gap=st["gap"], slits=st["slits"])
        # ── nosing · RF-5 retrofit strip (scene11 ∈ NOSING_BY_SCENE) ─────
        if cfg["cue_nosing"]:
            for j, (a0_, ztop_, pfx) in enumerate(((0.0, Z_TOP, prefix),
                                                   (a_b0, Z_MID, pb))):
                steps = sc._stair_steps(_A(a0_), st["riser"], st["tread"],
                                        st["n"], ztop_, None, None)
                pk.build_nosing_tier(stage, f"{pfx}/Nosing_{j}", steps,
                                     ylo, yhi, tier="retrofit_strip",
                                     mtl=M["nosing"], width=0.060, proud=0.004)
        # ── railings · kickplate ─────────────────────────────────────────
        if cfg["cue_railing"]:

            def _gnd(a0_, ztop_):
                x0_ = _A(a0_)

                def f(x):
                    if x <= x0_:
                        return ztop_
                    if x >= x0_ + RUN:
                        return ztop_ - DROP
                    i = min(int((x - x0_) / st["tread"]), st["n"] - 1)
                    return ztop_ - st["riser"] * (i + 1)
                return f

            # [GT-80] A rake rail starts **at** the stair head / at flight B's top
            #   riser (`x_start == x_top`, so `build_railing_line` emits no horizontal
            #   extension). The extension used to run the full depth of the landing in
            #   front of the flight, and that is the audited defect: on the deck side
            #   it laid a rail line 0.03 m off the deck face across the whole 2.40 m
            #   threshold — the "deck dead-ends into a rail" of `pt_noon_deck_walk` —
            #   and on the outer side it doubled the landing guard 0.03 m away from it,
            #   two baluster screens in one plane. Landings are guarded by
            #   `build_guard_run`, flights by `build_railing_line`, and the two meet
            #   end-to-end on the same `y_inset` line.
            for k, bb in enumerate((BA0 + ins, BA1 - ins)):
                # [GT-105 · 08-11 user] `rail_mid_r=0` — the flight guard drops its mid
                #   rail: the full-height picket screen already carries the 안목, and the
                #   extra horizontal crossed every raked panel as the "통로 중간의 바".
                #   One top rail + pickets = the GT-96 ribbon language on the rake.
                sc.build_railing_line(
                    stage, f"{prefix}/RailA_{k}", _B(bb), _A(0.0), _A(0.0),
                    RUN, DROP, _gnd(0.0, Z_TOP), M["rail"],
                    rail_h=ra["rail_h"], post_r=ra["post_r"],
                    spacing=ra["spacing"], rail_r=ra["rail_r"],
                    rail_mid_r=0.0)
                sc.build_railing_line(
                    stage, f"{pb}/RailB_{k}", _B(bb), _A(a_b0), _A(a_b0),
                    RUN, DROP, _gnd(a_b0, Z_MID), M["rail"],
                    rail_h=ra["rail_h"], post_r=ra["post_r"],
                    spacing=ra["spacing"], rail_r=ra["rail_r"],
                    rail_mid_r=0.0)
                # stair-foot newel: flight B's rails end at grade, the one terminus a
                #   pedestrian meets at eye level. Everything else on the run is closed
                #   by the next member (RailA's foot by the mid-landing guard, RailA's
                #   head by the head guard / the deck rail's 0.10 m end post at
                #   x ±13.20, which the rail's first post stands inside).
                build_rail_end(M, pb, f"Foot{k}", _A(a_b0) + RUN, _B(bb),
                               Z_MID - DROP)
            # head-landing guard — the tower's ONLY closed head-landing face.
            #   In the canonical frame b = BA0 is the DECK side (open, the walker
            #   enters there), a = 0 is this leg's stair head and a = A_HEAD is the
            #   second leg's stair head (both open — that is what makes the H a cross
            #   and not a T). b = BA1 is the 5.505 m free edge that is hazard ①, and it
            #   is guarded on the `y_inset` line so the two rake rails continue it
            #   without a 0.03 m jog at the corner.
            if with_head:
                pts_head = [(_A(A_HEAD), _B(BA1 - ins)),
                            (_A(0.0), _B(BA1 - ins))]
                if solo:
                    # [GT-96] single-leg tower: the retired second-leg face is
                    #   closed too — one continuous L run, shared corner post.
                    pts_head.insert(0, (_A(A_HEAD), _B(BA0 + ins)))
                build_guard_run(M, f"{prefix}/HeadGuardOuter", pts_head,
                                Z_TOP, height=ra["rail_h"])
            # G11's expanded-metal sheet at the tower head, in the **stair plane**
            #   (a 0…3.0), filling the trapezoid between flight A's rake rail and a
            #   horizontal top 0.90 m above the deck rail. One per leg, so the two
            #   heads of a tower read alike.
            #   It is deliberately NOT across the head landing's outer face: the pilot
            #   round `260731_w3_s11` measured that placement filling the whole
            #   h1.8_d2 / h0.9_d2 frame (mean 122.6 → 76.2, dark +34.3 pp) — the panel
            #   became a fence photographed at 2 m, and G11 does not put it there.
            #   [GT-80] hung 0.015 m outboard of the pad edge (b = BA1 + 0.015) instead
            #   of on it: at b = BA1 the 0.014 m bars overlapped the rake rail's
            #   0.026 m posts by 3 mm [computed], which is an interpenetration, and a
            #   real infill panel is bolted to the outside face of the guard anyway.
            # [GT-96] the sheet is re-anchored INTO the fence line: top = the deck
            #   ribbon height (rail_z 1.25) instead of +0.90 above the rail — the
            #   old value made it a free-standing billboard over the head. Run
            #   shortened so the triangle reads like G11's modest head infill.
            mesh_run = 1.6
            rake = st["riser"] / st["tread"]

            def _mesh_bot(s, _z0=Z_TOP + ra["rail_h"], _r=rake):
                return _z0 - _r * s
            build_mesh_panel(M, f"{prefix}/HeadMesh",
                             (_A(0.0), _B(BA1 + 0.015)),
                             (_A(mesh_run), _B(BA1 + 0.015)),
                             _mesh_bot, Z_TOP + PARAMS["deck"]["rail_z"])
            # mid-landing perimeter — every edge that carries the 2.755 m drop, and
            #   ONLY those. [GT-80] the old build guarded "Outer" (a = A_M1) on both
            #   forms; on a straight leg that line is where flight B's top riser is, so
            #   the west legs had a full-width balustrade barring the way down. It is
            #   an opening on a straight leg and a free edge on a switchback, and the
            #   two cases are now distinguished. Each guard is one continuous run, so a
            #   corner carries one shared post instead of two coincident ones.
            if switch:
                # …plus the NEWEL WRAP. On a 되돌음 leg the two inner rake rails
                #   (flight A's b = BA1 line and flight B's b = BB0 line, 0.16 m
                #   apart across the lane gap) both die on the mid-landing floor —
                #   two rails stopping in open air at hand height. A real switchback
                #   wraps the handrail round the newel, which is what this U does:
                #   it closes both ends into one member and stands where the 180°
                #   turn is made. Depth `mid/4` = 0.45 m, so it occupies a 7.04…7.49
                #   of a 1.80 m deep landing and neither flight's exit is narrowed.
                wrap = float(TW["mid"]) / 4.0
                guards = [[(A_A1, BA0 + ins), (A_M1 - ins, BA0 + ins),
                           (A_M1 - ins, BB1 - ins), (A_A1, BB1 - ins)],
                          [(A_A1, BA1 - ins), (A_A1 + wrap, BA1 - ins),
                           (A_A1 + wrap, BB0 + ins), (A_A1, BB0 + ins)]]
            else:
                guards = [[(A_A1, BA0 + ins), (A_M1, BA0 + ins)],
                          [(A_A1, BA1 - ins), (A_M1, BA1 - ins)]]
            for g_i, gpts in enumerate(guards):
                build_guard_run(M, f"{prefix}/MidGuard_{g_i}",
                                [(_A(ga), _B(gb)) for ga, gb in gpts],
                                Z_MID, height=ra["rail_h"])
            # KICKPLATE — present on the west tower, absent on the east.
            #   This is the scene's control variable and nothing else changes: it stays
            #   on the pad edge (not on the guard's inset line), and the matched control
            #   pair is the two 1.80 m transverse Side edges both landings have.
            if kick:
                edges = [("Side0", (A_A1, BA0), (A_M1, BA0)),
                         ("Side1", (A_A1, b_mid1), (A_M1, b_mid1))]
                if switch:
                    edges.append(("Outer", (A_M1, BA0), (A_M1, b_mid1)))
                for nm, (ea0, eb0), (ea1, eb1) in edges:
                    L = math.hypot(ea1-ea0, eb1-eb0)
                    along_a = abs(ea1-ea0) > abs(eb1-eb0)
                    BOX(f"{prefix}/MidKick{nm}",
                        (_A((ea0+ea1)/2.0), _B((eb0+eb1)/2.0),
                         Z_MID + float(TW["kick_h"])/2.0),
                        (L if along_a else 0.05, 0.05 if along_a else L,
                         float(TW["kick_h"])), M["rail"])
        # ── RF-1 base plates on the tower columns (props_kit) ────────────
        #   scene11 is on the retrofit list (02·11·15·16·17): its posts stand on a
        #   bolted plate with a drill-dust halo, not embedded in a mortar collar.
        for i, (cx_, cy_) in enumerate(cols):
            pk.build_base_plate(stage, f"{prefix}/ColPlate_{i}", cx_, cy_,
                                PARAMS["walk"]["z_top"], M["steel"],
                                bed_mtl=M["concrete"], plate=0.34,
                                thick=0.014, anchor_d=0.022, anchor_pitch=0.24)
        # ── tactile bands (cue_tactile · R11-2) ─────────────────────────
        if cfg["cue_tactile"]:
            tc = PARAMS["tactile"]
            # [W2-D Sec.12.4] scene11's non-conforming variant is "bearing off by
            #   `skew_deg`". The band is pulled back by half_w·sin(skew) so even the
            #   leading corner stops short of the tread line — a skewed band that
            #   overhangs the first tread would be a GT change, not a mis-installation.
            # [R11-2] placement = a band ACROSS the walk, `setback` clear of the riser,
            #   at the stair head and at the stair foot. Confirmed against G11.
            skew = float(tc.get("skew_deg", 0.0))
            back = abs(math.sin(math.radians(skew))) * hw
            d_ = float(tc["band_d"])
            sb = float(tc["setback"])
            if switch:
                foot_a, foot_b, foot_s = 0.0, (BB0 + BB1) / 2.0, -1.0
            else:
                foot_a, foot_b, foot_s = A_B1, 0.0, +1.0
            for nm, aa, bb, zb, sgn in (
                    ("TactileHead", 0.0, 0.0, Z_TOP, -1.0),
                    ("TactileFoot", foot_a, foot_b, 0.0, foot_s)):
                ca = aa + sgn * (sb + d_ / 2.0 + back)
                sc._oriented_box(
                    stage, f"{prefix}/{nm}",
                    (_A(ca), _B(bb), zb + (tc["proud"] - 0.01) / 2.0),
                    (d_, float(TW["width"]), tc["proud"] + 0.01),
                    M["tactile"], rotz=skew)

    def build_tower(M, tag):
        """[GT-80] Both legs of one H tower. The primary leg keeps the historical
        `{Tag}Tower` prim root; the second is named by its world descent bearing."""
        cfgt = PARAMS[tag]
        kind, kick = cfgt["kind"], cfgt["kickplate"]
        for i, (lnm, piv, rot, bs) in enumerate(_tower_legs(tag)):
            suffix = "" if i == 0 else ("N" if rot > 0 else "S")
            prefix = sc.build_rot_group(
                stage, f"{ROOT}/{tag.capitalize()}Tower{suffix}", piv, rot)
            build_leg(M, prefix, piv, bs, kind, kick, with_head=(i == 0),
                      solo=(len(_tower_legs(tag)) == 1))
            print(f"[S11-H] {lnm} pivot ({piv[0]:+.2f},{piv[1]:+.2f}) "
                  f"rot {rot:+.1f}° bsign {bs:+.0f} · {kind} · "
                  f"kickplate {'有' if kick else '無'}")

    def build_east(M):
        return build_tower(M, "east")

    def build_west(M):
        return build_tower(M, "west")

    # -------------------------------------------------------------------
    # deck noise panels + longitudinal railing (cue_railing)
    # -------------------------------------------------------------------
    def build_deck_rails(M):
        """[W3 S11 · G11] The deck guard is a **uniform vertical-baluster railing** for
        the whole span — no acoustic infill. G11 shows exactly that, and it also closes
        the v6 finding for good: the alternating noise-panel bays were what turned the
        shadow side of the corridor into a 30~45 % pure-black band, so deleting them is
        the same fix carried to its end rather than a new experiment.

        The baluster pitch is now the statutory 안목 (`baluster_gap` 0.100 m clear). The
        previous local loop ran 6 balusters per 2.05 m bay = **0.32 m clear**, 3.2× the
        limit — invisible to the K4(a) gate because this is scene-local geometry, not a
        `build_railing_line` call. GT-neutral (railing prims only)."""
        dk = PARAMS["deck"]
        rb = PARAMS["rail_bay"]
        x0, x1 = dk["x0"], dk["x1"]
        nb = int(rb["n_bay"])
        L = (x1 - x0) / float(nb)
        zt = dk["z_top"]
        pitch = 2.0 * rb["baluster_r"] + rb["baluster_gap"]
        for i, ye in enumerate((dk["y0"], dk["y1"])):
            for k in range(nb + 1):                      # posts
                BOX(f"{ROOT}/DeckRailPost_{i}_{k}",
                    (x0 + k*L, ye, zt + rb["post_h"]/2.0),
                    (rb["post_t"], rb["post_t"], rb["post_h"]), M["steel"])
            # [GT-96] the stepped end-bay tapers are RETIRED with the height they
            #   bridged: at rail_z 1.25 the fork step down to the 1.10 landing guard
            #   is 0.15 m and knuckles at the shared end post — no transition bays.
            for k in range(nb):
                xa = x0 + k*L + rb["post_t"]/2.0 + rb["joint"]
                xb = x0 + (k+1)*L - rb["post_t"]/2.0 - rb["joint"]
                xc, Lx = (xa + xb)/2.0, xb - xa
                BOX(f"{ROOT}/DeckKick_{i}_{k}",
                    (xc, ye, zt + rb["kick_h"]/2.0),
                    (Lx, dk["panel_t"], rb["kick_h"]), M["rail"])
                nbal = max(2, int(Lx / pitch))
                bz0 = zt + rb["kick_h"]
                bz1 = zt + dk["rail_z"] - 0.06
                for b in range(nbal):
                    xb_ = xa + (b + 0.5) * Lx / float(nbal)
                    CYL(f"{ROOT}/DeckBal_{i}_{k}_{b}",
                        (xb_, ye, (bz0 + bz1)/2.0), rb["baluster_r"],
                        bz1 - bz0, M["rail"])
            # [GT-96] main top rail spans end to end again (no taper bays), its
            #   ends landing inside the deck-end posts.
            CYL(f"{ROOT}/DeckRail_{i}",
                ((dk["x0"]+dk["x1"])/2.0, ye, dk["z_top"] + dk["rail_z"]),
                dk["rail_r"], (dk["x1"]-dk["x0"]) + rb["post_t"],
                M["rail"], rotY=90.0)

    # -------------------------------------------------------------------
    # sign (cue_sign) - footbridge guidance sign_info
    # -------------------------------------------------------------------
    def build_signs(M):
        sg = PARAMS["sign"]
        for i, (sx, sy, yaw) in enumerate(sg["spots"]):
            sc.build_sign(stage, f"{ROOT}/Sign_{i}", sx, sy,
                          PARAMS["walk"]["z_top"], yaw, M["sign"],
                          w=sg["w"], h=sg["h"], pole_h=sg["pole_h"],
                          pole_mtl=M["pole"], back_mtl=M["signback"])

    # -------------------------------------------------------------------
    # dressing
    # -------------------------------------------------------------------
    def build_dressing(M):
        d = PARAMS["dress"]
        gz = PARAMS["walk"]["z_top"]
        sh = d["shelter"]
        sc.build_canopy(stage, f"{ROOT}/Shelter", sh["x0"], sh["x1"], sh["y0"],
                        sh["y1"], sh["z_roof"], sh["post_r"], M["panel"],
                        M["pole"], roof_t=0.10, base_z=gz)
        BOX(f"{ROOT}/ShelterBack",
            ((sh["x0"]+sh["x1"])/2.0, sh["y0"] + 0.10, gz + 1.10),
            (sh["x1"]-sh["x0"], 0.06, 2.20), M["glass"])
        # [v6 ruling (5)] 2 side walls + route-map panel - removes the "four-legged carport" misreading.
        for i, xe in enumerate((sh["x0"] + sh["side_inset"]/2.0,
                                sh["x1"] - sh["side_inset"]/2.0)):
            BOX(f"{ROOT}/ShelterSide_{i}",
                (xe, (sh["y0"]+sh["y1"])/2.0 - 0.35,
                 gz + sh["side_h"]/2.0),
                (sh["side_t"], (sh["y1"]-sh["y0"]) - 1.4, sh["side_h"]),
                M["glass"])
        BOX(f"{ROOT}/ShelterRoute",
            (sh["x0"] + 1.35, sh["y0"] + 0.20, gz + 1.55),
            (sh["route_w"], 0.05, sh["route_h"]), M["panel"])
        sc.build_bench(stage, f"{ROOT}/ShelterBench",
                       (sh["x0"]+sh["x1"])/2.0, sh["bench_y"], gz, M["wood"],
                       yaw=0.0)
        bx, by, bh = d["bus_pole"]
        CYL(f"{ROOT}/BusPole", (bx, by, gz + bh/2.0), 0.055, bh, M["pole"],
            col=True)
        BOX(f"{ROOT}/BusSign", (bx, by, gz + bh - 0.30), (0.06, 0.55, 0.55),
            M["panel"])
        lp = d["lamp"]
        for i, (lx, ly) in enumerate(d["lamps"]):
            base = f"{ROOT}/Lamp_{i}"
            CYL(f"{base}/Pole", (lx, ly, gz + lp["pole_h"]/2.0), lp["pole_r"],
                lp["pole_h"], M["pole"], col=True)
            sgn = 1.0 if lx < 0 else -1.0
            CYL(f"{base}/Arm", (lx + sgn*lp["arm_len"]/2.0, ly,
                                gz + lp["pole_h"] - 0.12),
                lp["arm_r"], lp["arm_len"], M["pole"], rotY=90.0)
            BOX(f"{base}/Head", (lx + sgn*lp["arm_len"], ly,
                                 gz + lp["pole_h"] - 0.18),
                (lp["head"]*1.5, lp["head"], 0.14), M["lamp"])
        # trees on the planting strip sit on the groundcover top (0.10), trees on the sidewalk on the paving.
        vsoil = PARAMS["verge"]["soil_top"]
        vx = PARAMS["walk"]["xe1"] + 0.001
        for i, (tx, ty) in enumerate(d["trees"]):
            tz = vsoil if abs(tx) >= vx else gz
            sc.build_tree(stage, f"{ROOT}/Tree_{i}", tx, ty, tz, M["wood"],
                          M["leaf_a"], M["leaf_b"])
        for i, (bx2, by2, yaw) in enumerate(d["benches"]):
            sc.build_bench(stage, f"{ROOT}/Bench_{i}", bx2, by2, gz, M["wood"],
                           yaw=yaw)
        # [K4 C6] `sc.build_bollard` is a bare 0.75 m cylinder and `placement_lint`
        #   has been reporting it as a **statutory ERROR** (교통약자법 시행규칙 별표2
        #   제7호: 0.80–1.00 m) on all four posts since the linter landed. props_kit's
        #   C6 builder carries the compliant 0.85 m height plus the dome cap, base
        #   plate + anchor cover and the knee-height reflective band — and its own
        #   plate makes a separate RF-1 call on these posts redundant.
        for i, (bx2, by2) in enumerate(d["bollards"]):
            pk.build_bollard_v2(stage, f"{ROOT}/Bollard_{i}", bx2, by2, gz,
                                M["pole"], band_mtl=M["nosing"], seed=i)
        # [G13 · G11] trench gratings across the walk at each stair foot
        for i, (gx_, gy_, gyaw) in enumerate(d["gratings"]):
            pk.build_trench_grating(stage, f"{ROOT}/Grating_{i}", gx_, gy_, gz,
                                    M["steel"], M["rail"],
                                    length=float(d["grating_len"]),
                                    width=0.30, yaw=gyaw)
        build_treeband(M)
        for key, bd in PARAMS["buildings"].items():
            sc.build_building(stage, f"{ROOT}/Building_{key}", bd, M["brick"],
                              M["glass"], M["parapet"],
                              window=PARAMS["window_by"].get(
                                  key, PARAMS["window"]))

    def build_treeband(M):
        """[v6 ruling C-2/C-4 · v7 ruling (6)-2] distant tree silhouette band.

        The v6 build (one solid box + one small blob per segment) was a **continuous
        plate with a flat top** and read as a "painted noise wall (green slab)". The
        structure is changed to two tiers.
          · lower box = the shrub layer below the canopy. Lowered to h·base_frac
            (0.36) so it **makes no silhouette** (excluded from skyline duty).
          · upper canopy = `blobs` overlapping oblate blobs per segment. Individual
            heights are scattered by a 0.72~1.16× jitter so the **top line is
            saw-toothed**, and x is shaken by ±x_jit to give fore/aft depth.
          · the material cycles three aerial-perspective low-saturation grey-greens
            by coordinate hash (prevents a flat monochrome slab).
        Grounding guarantee: blob centre z = gz + hj·0.62, rz = hj·0.42 →
          bottom = gz + hj·0.20 ≤ gz + h·0.36 = box top face (since hj ≤ 1.16 h,
          0.20·1.16 h = 0.232 h < 0.36 h). So **zero floating blobs**.
        Deterministic jitter (index hash) — reproducibility preserved."""
        tb = PARAMS["treeband"]
        import random as _random
        gz = PARAMS["ground"]["z_top"]
        far = (M["leaf_far_a"], M["leaf_far_b"], M["leaf_far_c"])
        nb = int(tb.get("blobs", 3))
        bf = float(tb.get("base_frac", 0.36))
        xj = float(tb.get("x_jit", 1.7))
        for r, (xa_, xb_, hh) in enumerate(tb["rows"]):
            n = max(2, int(round((tb["y1"] - tb["y0"]) / tb["seg"])))
            xc0 = (xa_ + xb_) / 2.0
            for k in range(n):
                ya = tb["y0"] + k * (tb["y1"] - tb["y0"]) / n
                yb = tb["y0"] + (k + 1) * (tb["y1"] - tb["y0"]) / n
                rnd = _random.Random((r * 7717) ^ (k * 3413))
                h = hh + rnd.uniform(-tb["jitter"], tb["jitter"])
                dx = rnd.uniform(-0.8, 0.8)
                BOX(f"{ROOT}/TreeBand_{r}_{k}",
                    (xc0 + dx, (ya+yb)/2.0, gz + h*bf/2.0),
                    ((xb_ - xa_) * rnd.uniform(0.8, 1.25), yb - ya + 0.6,
                     h * bf),
                    far[(k + r) % 3])
                # the canopy radius is based on **the band width** (not on height) - so that even a large
                #   height jitter cannot spread in x and encroach on the planting strip / street-tree row
                #   ([W3 P11] now at x +-23.2, 21.3 m clear instead of 3.3 m). Maximum x spread =
                #   x_jit 1.2 + rx 1.9 = 3.1 m; the band itself does not move (§10-1 leaves the
                #   strip-to-band gap as grass).
                rw = (xb_ - xa_) * 0.5
                for j in range(nb):
                    hj = h * rnd.uniform(0.72, 1.16)
                    rx = rw * rnd.uniform(0.55, 0.95)
                    sc.add_sphere(
                        stage, f"{ROOT}/TreeBlob_{r}_{k}_{j}",
                        (xc0 + rnd.uniform(-xj, xj),
                         ya + (j + 0.5) * (yb - ya) / nb
                         + rnd.uniform(-0.7, 0.7),
                         gz + hj * 0.62),
                        (rx, rx * rnd.uniform(0.90, 1.60), hj * 0.42),
                        far[(k + r + j + 1) % 3])

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    build_site(M)
    if cfg["cue_material_break"]:
        build_lanes(M)
    if cfg["hazard_stairs"]:
        build_deck(M)
        build_ground_kit(M)          # [W2-D] deck ground elements
        build_east(M)
        build_west(M)
        if cfg["cue_railing"]:
            build_deck_rails(M)
    if cfg["cue_sign"]:
        build_signs(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    VIEWS = build_views()
    _v0 = VIEWS["overview"]
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

    if capture_mode:
        sc.capture_pipeline(simulation_app, VIEWS,
                            os.path.join(LOOKCHECK_DIR, "auto"),
                            set_render_mode, look_from)
        simulation_app.close()
        return

    input_iface = carb.input.acquire_input_interface()
    appwindow = omni.appwindow.get_default_app_window()
    K = carb.input.KeyboardInput
    rot_step = float(PARAMS["light"]["dome_rotation_step"])
    dome_user_rot = [0.0]

    def capture(path):
        vp = get_active_viewport()
        capture_viewport_to_file(vp, file_path=path)

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
            fp = os.path.join(LOOKCHECK_DIR, f"scene11_{ts}.png")
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
