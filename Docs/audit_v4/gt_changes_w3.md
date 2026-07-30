# GT change ledger — W3 (live)

> **Wave**: W3 · **Kind**: live ledger (append-only) · **Opened**: 2026-07-30
> **Branch**: `feat/realism-v1` · **Owner**: WP **T5** (`Docs/briefs/w3_execution_spec_v1.md` §4.1)
> **Materialises**: spec §8 (13 rows) · **Authority**: the spec. This file never overrides it —
> it tracks execution against it and records what actually happened.
>
> **Project law** (spec §8): *a geometry edit without a declared GT consequence is exactly how the
> W2 regressions happened.*

---

## 0. The append-before-land rule

**No GT-affecting change lands until its row exists here, and no row is closed until it records the
command that was actually run.**

1. **Declare before you commit.** A commit that moves a walked surface, adds or removes a drop edge,
   changes a hazard/collision box, or moves an element AABB that GT reads **must** be preceded by an
   appended (or updated) row in §3. The commit message names the row id (`GT-n`).
2. **One re-cache per scene per batch.** Where several GT rows land in one commit batch on one scene,
   one row carries the re-cache and the others declare that they ride it (see GT-1/GT-2/GT-3).
3. **Record the command, do not guess it.** Spec §8: *"the exact data-pipeline invocation is the data
   owner's — the ledger row records the command actually used."* §4's landing record stays empty
   until the owner pastes the real invocation. An empty landing record means the row is **not** closed,
   whatever the commit history says.
4. **A held row may be prepared, never enforced.** Rows marked `HELD` are under ruling §1.8 — write
   the builder, leave the scene-side value and the gate untouched.
5. **An invariance proof is a result, not a promise.** For `PROOF-ONLY` rows a non-empty prim-hash /
   GT-delta diff is a **defect**, not a new baseline (spec §8 GT-6). Do not re-baseline out of it.
6. **This ledger has a code-level twin.** `ground_kit.py:2363-2370` already refuses to build any
   element carrying `exc="gt_change"` unless the plan's in-code `gt_changes` list is non-empty
   (`GT_DELTA = 0.020`, `ground_kit.py:122`). That guard covers ground-kit elements only; this file
   covers everything else. Neither replaces the other.

---

## 1. What "re-cache" means (spec §8, verbatim scope)

| step | Action |
|---|---|
| **R-1** | The scene's own self-check re-derives and **prints** the hazard/drop registry from the changed geometry |
| **R-2** | A mini data render of that scene is re-run and checked with `scripts/check_data_run.py` (default run id `260730_data_mini`, `scripts/check_data_run.py:25,51`; producer `scripts/run_data_render.py --run <id> --scenes <scene>`) |
| **R-3** | The OCCL/GRAZE baseline is re-stamped in the next `regr_*.json` |

**Full re-cache** = R-1 + R-2 + R-3. Rows that name a subset name it explicitly.
Current comparison baseline: `Docs/reports/regr_260730_w2d_fix.json` — **retired at CB-2 by GT-8**.

---

## 2. Status vocabulary

| status | Meaning |
|---|---|
| `OPEN` | Declared, gate assigned, not yet landed |
| `BLOCKED` | Cannot land until a named dependency clears (dependency in the row) |
| `HELD` | Blocked by an evidence gate under ruling §1.8 — prepare only, do not enforce |
| `PROOF-ONLY` | Designed GT-invariant; the deliverable is a proof, and re-cache fires only if the proof fails |
| `LANDED` | Committed **and** §4's landing record filled with the real command and its result |
| `CARRIED-IN` | Landed in an earlier wave, still owes a label or a downstream action (§5) |

---

## 3. The ledger

Schema: **row id · scene · change · z-profile effect · re-cache step · gate · status**.

| # | Scene(s) | Change | z-profile effect | Re-cache step | Gate | Status |
|---|---|---|---|---|---|---|
| **GT-1** | 02 | Flood sill: raised apron `x −1.20…0.00`, `y ±2.10`, top **z = +0.18**; one 0.18 m riser at `x = −1.20`; descent begins from +0.18 | Drop edge at `x = 0` carries **3.38 m** instead of 3.20 m. A **new 0.18 m up-step** appears at `x = −1.20` — **label it an up-step, not a drop** | **Full re-cache** (R-1+R-2+R-3) — carries GT-2 and GT-3 | CB-7 · GATE-1 pilot **02** | `OPEN` |
| **GT-2** | 02 | Curb reshape: top **+0.10 above footway → flush … +0.02**; exposure above carriageway 150 mm | 100 mm vertical change on a walked surface; below the drop threshold but adjacent to the sill | **Rides GT-1's single re-cache** | CB-7 · GATE-1 pilot **02** | `OPEN` |
| **GT-3** | 02 | Canopy deletion (ruling §1.5, Option A) | No walked-surface z change; **OCCL baseline moves** — four posts and a 2.4 × 4.9 m slab leave every cut | **R-3 only** (re-stamp OCCL) | CB-7 · GATE-1 pilot **02** | `OPEN` |
| **GT-4** | 01 | `upper_plaza` extended to the building faces (turf `z = −0.63` → paving `z = 0`) + ground_kit region → `(−16, −8, 0, 8)` | **Height-field change** *and* every decal AABB moves (decorated area ×1.7). RT-I §4-N3's first missing flag | **Full re-cache + regr re-baseline.** `prim_cap = 60` re-checked — expect to *reduce* per-element counts, **not** raise the cap | CB-11 · GATE-2b partial | `HELD` — ruling §1.8 / P-5: released only when T2 lands 5 plaza-to-plinth frames |
| **GT-5** | 13 | `walk_north` / `walk_south` `proud = 0.007` → a real **150 mm** curb step | Real geometry change on a walked surface. RT-I §4-N3's second missing flag | **Full re-cache** — coordinate with the carried-in ramp-curb record R-1 (§5), same scene | CB-9 · GATE-1 pilots **06 · 13** | `OPEN` |
| **GT-6** | 06 (+ 05 · 19 share the builder — **scene13 REMOVED: 0 call sites** [T3 §refuted]; scene05 has **12** sites, not 10) | S06-A: landing top **4.998 → 5.000** (**this IS a +2 mm walked-top-face GT change** — supervisor amendment 07-31 resolving the row's self-inconsistency [T3 blocker]), landing azimuth clipped at the deck edge, fascia stepped, railing `outer_r` **3.36 → 3.24**, chord margin **1.03 → 1.000** | **GT class B (micro)**: top-face +2 mm on landings only; all other terms (`r_in`, `r_out`, azimuths, tread z-ladder) invariant | **Split proof**: prim-hash / GT-delta diff must be empty **except** the enumerated landing-top rows (+2 mm exactly); any OTHER non-empty row is a defect. Re-cache the landing-top strip only. **Archive the judge baselines for 05 · 06 · 19 before `scene_common` is touched** | CB-5 / CB-9 · GATE-1 pilots **06 · 13** + split prim-hash proof | `RELEASED` — T3 published (w3_geom_reverify_v1.md, C-3 99.0 mm struck → 7.46 mm; NF-1 must land in the same K4(d) commit) |
| **GT-7** | 08 | Tempbar / line-barrier deletion `[ruled 07-30]` §1.6 — removes **2 `TempPost_*` collision boxes** | Hazard/collision box list changes; no walked-surface z change | **R-3** (re-stamp the OCCL/GT baseline) + R-1 to prove the boxes left the registry | CB-8 · GATE-1 pilot **08** + OCCL re-stamp | `OPEN` |
| **GT-8** | all 33 | `_obb_aabb → _box_aabb` collapse on every patch and stain | Element-registry AABBs become exact rather than OBB envelopes; `frame_budget` B1/B2/B5 inputs move. **Not** a hazard change | **Regression re-baseline + a note in the round stamp.** `regr_260730_w2d_fix.json` is **retired here** | CB-2 · GATE-1 pilots **03 · 07 · C2 · 01** | `LANDED` — see §4 |
| **GT-9** | ~~22 scenes / 139 instances~~ → **13 scenes / 85 instances** (A1 deletes `plaza_granite`'s weed row, −54 over 9 scenes; see §4 and §7-W6) | A1 weed cube → `Grass_Short_C` (footprint **0.10 → 0.272 m**) | GT class stays **A** (z unchanged) **only while h ≤ 0.12**. `_elem` aabb, `EDGE_STANDOFF = 0.80` and the **GT-E5 ramp clamp** all read the footprint | Recompute `_elem` from the **scaled** bbox; drive the asset scale from the **GT-E5-clamped `proud`**, not from native height, or the ramp becomes decorative. See the watch item in §6-W1 — native `Grass_Short_C` is **0.125 m**, i.e. above the h ≤ 0.12 condition | CB-2 · GATE-1 pilots **03 · 07 · C2 · 01** | `LANDED` — see §4 |
| **GT-10** | 09 | Mooring / land posts moved off the stair face to the terrace edge or the lowest landing (n = **6**, currently `cx = −1.2`, `cy = ±3.8 / ±13.5 / ±19.0`) | Props, not walked surface | Verify **no new occlusion of a hazard row** (R-1 registry print; R-3 if OCCL moves) | CB-1 · GATE-1 pilot **09** | `OPEN` |
| **GT-11** | 05 | Arc-step / stage-disc wedge-gap closure | Real geometry defect repair; check whether the closed wedge touches a hazard face | **Declare at the gate; expect class A.** Promote to full re-cache if the closure touches a hazard face | CB-10 · GATE-2 full round | `OPEN` |
| **GT-12** | 23 scenes | `building_kit` B-F1 glazing un-burial (glazing moves 5 mm proud) | Above ground, **no GT** | **None** — OCCL re-check only | CB-4 · GATE-1 pilots **20 · 21** | `OPEN` |
| **GT-13** | 03 · 09 · 12 · 17 + N-series | Far-tier skyline albedo override `[ruled 07-30]` §1.11 | **No geometry.** GI rebound moves the judged ground band (Δσ_LF up to **−0.32**, ≈4× the noise floor) | No re-cache. **Re-gate on B45/B30, not only on B-HZ** (`scripts/near_ground_stats.py`) | CB-10 · GATE-2 full round | `OPEN` |
| **GT-14** | 07 | **Stone stair archetype rebuild** (`s3_scene07_10_rebuild_spec_v1.md` §4.1-1, OQ-7 ruled 28). 24 discrete 디딤돌 pavers (inter-stone gap 0.050–0.276 m = **34.0 % of the run bare slope**; tread 0.270–0.384; rise 0.111–0.232 mean 0.174) → **28 courses of 2–4 bedded 자연석 slabs** spanning the corridor `y ±1.70`, flight `x 0.00 → 12.20` (the frozen run), `tread_mu` **0.43571**, slab thickness **0.250** (KFS-TRAIL 13-2 가 300×300×250), **back-overlap `ov` 0.12 with an unjittered back edge ⇒ open-slope fraction 0 % by construction and interlock 0.06–0.18 m ≥ the heritage-spec 50 mm** (표준시방서 0400-3.2 ㄷ); front edge only jittered ±0.06 so neighbours differ ≤0.12 (the ragged nosing); within-course joints ≤ 0.06 m, dry-laid, **no pointing** (표준시방서 0400-1.3 ㄹ 건식쌓기); rise = dressed **σ 10 mm** white noise **plus a correlated settlement wave ±20 mm over 8–12 courses** (`s3_research_numbers_v1.md` §B4 — white noise reads fake), clamped to the declared band **0.120–0.180**, mean **0.1489**; one 속채움 bed slab per course so no joint bottoms out in air | **Every nosing z on the walk line moves.** Entry step at the yard shoulder **+0.002 → ≈ 0.149 m down** (one rise). Exit step at `x = 12.2` **+0.201 → +0.030 m**, and it stays labelled an **UP-STEP** onto/off the approach road, never a drop (GT-1 rule (b)); 30 mm is 조경설계기준 21.5(6)'s 디딤돌 proud. **Consequential ground move, declared here rather than discovered at the gate**: the `PathCorridor` and `SouthScarp` slope plates drop `z0` 0.00 → **−0.22 m** because a *level* tread back would otherwise be pierced by the 19.0° plane; `path_z()` itself, `STAIR_RUN`, `STAIR_DROP`, `SIDE_DROP` and the `x = 12.2 / z = −4.2` junction are **unchanged and re-confirmed, not re-baselined**. The realised south lateral drop (stone top → `SouthTerraceB`) therefore reads ≈1.67–1.82 m instead of ≈1.82–1.88 m — **not softened**, still ≫ 0.30 | **Full re-cache** (R-1+R-2+R-3) — carries GT-15, GT-16 and GT-17 | CB-S3-07 · GATE-1 pilot **07** | `OPEN` |
| **GT-15** | 07 | **Kerb 야면석 boulders + fern margins + framing trunks** (spec §3.2 mapping, §4.1-2). Discontinuous boulder line on both corridor shoulders at `y = ±1.55` (inboard of the `±1.70` edge), 0.40–0.90 m across, standing 0.15–0.35 m proud of the adjacent tread, mean 1.6 m centre-to-centre with deliberate ≥3 m gaps; fern-band stand-ins densified on both margins; the two framing trees up-scaled | **New collision/hazard boxes beside the walk line.** No walked-surface z change on the walk line itself (`\|y\| ≤ 0.22`); every boulder is asserted at `\|y\| ≥ foot_half + 0.10 = 0.32`. The boulders occlude the south shoulder in grazing cuts, which is the face the scene's positive GT is read from. **H8 holds**: they sit on the corridor shoulder, not on the terrace edge at `y −1.7`, so they are not a guard, a kerb or a rail | **Rides GT-14's re-cache**; additionally verify **no new occlusion of a hazard row** (GT-10 precedent) | CB-S3-07 · GATE-1 pilot **07** | `OPEN` |
| **GT-16** | 07 | **Canted-knob deletion + jitter caps.** 24 `StoneKnob_*` prims deleted (`collider=False`, built 50–80 mm below the stone top by construction). With them, the two jitter rows the spec pairs into the same commit: **A6** course lateral offset `cy` ±0.35 → **0** (an archetype error, not a jitter question) and **A7** per-slab yaw ±4.0° → **±3.0°** (adopted J-14). Row widened past spec §5.2's draft text to cover A6/A7 because spec §6.2 puts them in this one commit — stated, not silently done | **No walked-surface z change.** `top = path_z(cx) + proud` is independent of both `cy` and `rz`, and the SMOKE rise/gap/entry/exit table is **bit-identical** across this commit (the seeded stream still draws the abolished `u`). Element AABBs move in `y` where a stone recentres. **OCCL baseline moves**: 24 prims leave every cut | **R-3 only** (re-stamp OCCL) — rides GT-14's round | CB-S3-07 · GATE-1 pilot **07** | `OPEN` |
| **GT-17** | 07 | **Season re-bind, summer pin** `[ruled 07-31]` §8.R OQ-1. `PathCorridor` + `SouthTerraceA/B/C` + `Approach` come **off `leaf_ground`** (an autumn texture, `scene_common.py:121-123`) onto a summer forest floor; `leaf_ground` stays on the **margin lobes only**; moss becomes zone-driven per §4.1-3 (walked centre band 0.00–0.10 · tread outer 0.35–0.55 · riser faces 0.60–0.85 · joints 1.00 · boulder tops 0.70–0.90) instead of the blind `moss_every = 3`, using the new `sc.TEX["moss"]` (K4 micro-commit `1346b70`). `sct_debris_leaves_dry_*` stays **unplaced** in 07 — the `SCENE_SCOPE` permission is not a recommendation (H10) | **No geometry, no z change.** Element AABBs move where a lobe's `cx/cy` moves (GT-8 class). Albedo change on the terrace face that the grazing cut judges → treat as a **render-gate** item, not a GT item | **R-3 only** + re-gate on the grazing cut | CB-S3-07 · GATE-1 pilot **07** | `OPEN` |
| **GT-18** | 10 | **Deck stair re-table** (S3-9, spec §4.2-1). 4 flights × 10 at riser **0.165** / tread **0.300** / clear width **1.38** (2R+T = 0.630, 28.8°) → **6 flights, 8+7+8+7+7+7 = 44 risers** at riser **0.150** / tread **0.310** (2R+T = **0.610**, 25.8°), clear width **1.500 m**, with **4 turn landings 1.50 (travel) × 3.20 (across)** + **1 쉼터/전망 rest platform 3.00 × 3.20 at z −3.450** carrying a bench, plus the ground-arrival landing. Tread plate 0.050 → **0.025** (a stocked 25 × 140 데크판재) and the entry-deck plank field's width is now **stated at 0.140**, not left on `ground_kit`'s 0.145 specification default. Band pitch `y_off` 0.70 → **0.85** so the two 1.50 m bands clear each other by 0.20 m and the railings, which now sit outboard of the deck edge, leave the clear width at exactly 1.500. **Three identities, re-derived by `deck_module_selfcheck` and not retyped**: `44 × 0.150 = 6.600` exactly · `8+7+8+7+7+7 = 44` · `2R + T = 2(0.150) + 0.310 = 0.610 ∈ [0.600, 0.650]` `[law]` KCS 34 50 10 3.2.8(3), which also requires the ratio be **uniform over the whole run** — only the *step count* varies between flights. **The honest headline: the old ratio was never the defect** — 0.630 is inside the governing window and 〈표 13-1〉's 30° row is 170/300, so this is a fidelity change. The real compliance failures were the **width** (`[law]` 산지관리법 시행령 별표 3의3 제4호 다 caps 숲길 at 1.5 m and `[data]` KNPS-STAIR's 데크 subset n = 155 has median 1.50 / mode 47.7 %, against 1.80 at only 9.0 %) and the **landing** (`[law]` 조경설계기준 5.10.2(3) requires 참 ≥ the stair's own 유효폭 **and** ≥1,200 mm, with 5.9(4) fixing 1.5 × 1.5 m — the old 1.40 m landing **failed** it). Landing pitch is now ≤ **1.200 m** of rise, comfortably inside 5.10.2(3)'s 2 m rule; the 건축법 3 m rule (PIRAN-15 제15조) is **not cited** because it binds 건축물 only and the landscape rule is stricter | **The entire descent z ladder moves.** Landing tops −1.65 / −3.30 / −4.95 / −6.60 → **−1.200 / −2.250 / −3.450 / −4.500 / −5.550 / −6.600**; every tread top moves; the entry step trail 0.000 → deck −0.005 is unchanged but the **first riser becomes 0.145 m** (was 0.160). Hazard cue (3)'s leaf band is **re-derived, not re-typed** — it still bites treads 1·2 of flight 0, now at tops **−0.145 / −0.295**. The `landing_last → lower path` proud is re-verified at **+0.020 m**, inside `0 < proud ≤ 0.05`. Total drop **6.600 m unchanged** (§9 P-2). Plan grows x [−1.40, 4.40] → **[−1.19, 5.79]**, y ±1.40 → **±1.60**. Prim count 1038 → **1266 (+228)**. **Declared intermediate defect**: with 7-riser flights still stacked two-deep, the vertical clearance between a flight and the one above falls to 2 × 1.05 − 0.29 = **1.81 m**, below the 2.0 m the SMOKE table wants; **S3-10's de-stacking removes the stacking entirely and with it the question**, and this row is written so the intermediate state is on record rather than discovered | **Full re-cache** (R-1+R-2+R-3) — **carries GT-19, GT-20 and GT-21** | CB-S3-10 · GATE-1 pilot **10** | `OPEN` |
| **GT-19** | 10 | **De-stacking — Option A** (S3-10, spec §4.2-4A, `[ruled 07-31]` §8.R OQ-6). The 4 flights that sat two-deep inside a **3.0 × 2.8 m plan** become **6 flights that tile the X axis end to end**, alternating between two 1.50 m Y bands and turning 90° on each landing: f0 x[0.00, 2.48] band −Y · f1 x[3.98, 6.15] band +Y · f2 x[7.65, 10.13] band −Y · f3 x[13.13, 15.30] band +Y · f4 x[16.80, 18.97] band −Y · f5 x[20.47, 22.64] band +Y. **Flight-to-flight plan overlap 0.000000 m² and flight-to-landing overlap 0.000000 m²**, both asserted by `deck_module_selfcheck` — the 180° reversal is given up because it is *provably* incompatible with de-stacking in two bands (flight k+2 always lands back on flight k's footprint; the scene's own v5 docstring says the same thing from the other side — *"A pure switchback makes no horizontal progress … the ground along the stair must therefore be effectively vertical"*). **The masonry shaft is deleted**: plates `BankCut` (a 7.40 m single wall over the whole deck run), `EastTierLow`, `EastTierUp`, all three `copings` (BankW/BankE/Tier) and the `berm_hedges`/`berm` planting band are gone (§2.B-2 C15/C16); 0 masonry plates remain over the deck run and what survives is the **short head wall** — `UpperBody`'s exposed face at x = −1.5, now **0.255 m** tall instead of 6.62 m. In their place a **real descending slope**: 15 sloped `CorridorSlope_i` slabs spanning y[−2.60, 8.00] following `GROUND_LINE`, mean longitudinal grade **25.8 %**, steepest segment **48.4 %** (the flight's own grade), level benches under every landing. `NorthBank`'s foot retreats y 2.60 → **8.00** and `UpperTrail`/`UpperBody` widen to y 8.00 to meet it | **Walked-surface z is covered by GT-18** (the ladder itself is unchanged by this row). **The ground field changes underneath, everywhere**: `ground_z(x, y)` inside the corridor band returns `corridor_z(x)` instead of the flat shaft floor at −6.62, so **every dressing seat z under the new footprint is re-derived** (`_zone_z`, `north_z`'s pivot, `post_segments`' footings — every deck column now founds on the sloped ground rather than on a landing below it). The designed air gap under the deck is **0.020–0.600 m**, all positive, with the **stair foot at 0.250 m ≤ 0.300 m** — `[law]` KFS-TRAIL 특별시방서 12-3 마 (p.165) *"계단하단부와 지반과의 높이차가 30cm 이상으로 올라가지 않도록 시공"*. **Plan grows x [−1.19, 5.79] → [−1.50, 24.14], y ±1.60 → [−1.60, 3.10].** **Divergence from the spec's estimate, declared with its arithmetic**: §4.2-4A guessed *roughly* x[−1.5, 12]; the exact figure is Σruns 13.64 + 4 turn landings × 1.50 + rest platform 3.00 + arrival landing 1.50 = **24.14**. The estimate counted Σruns only and omitted the X the landings consume. That consumption is not removable: pushing the landings sideways into the neighbouring band instead makes net progress run − 1.50 = 0.67 m per 1.05 m of drop = **157 %**, i.e. a vertical ground — the shaft again. All five mise-en-scène cuts are now **derived from the ladder** rather than typed as literals, so they cannot drift off their subject. Prim count 1266 → **1219 (−47)**: the wall/coping/berm deletions outweigh the two extra flights. **OCCL and near_ground_stats will both move a long way and that is the intended result** | **Rides GT-18's full re-cache** (§0-2, one per scene per batch) | CB-S3-10 · GATE-1 pilot **10** | `OPEN` |
| **GT-20** | 10 | **Railing rebuild** (S3-8, spec §4.2-2) — declared ahead of GT-18 because spec §6.2 lands the railing first. Round → square throughout: landing/entry newels Ø150 `CYL` → **90 × 90 capped newels** (cap 120 × 120 × 45, projecting **0.150 m** above the top rail, 20 of them, one per shared corner); raking-flight posts Ø100 → the same 90 × 90 stock; rails Ø60 → **38 × 140 laid flat** (top) + **38 × 89** (mid) + **38 × 89** (bottom, *new*); balusters Ø44 @ **0.300 m** → **38 × 38 @ 0.150 m horizontal pitch**, clear gap **0.112 m** (worst run 0.1094, `LandRail_k_Out`); deck support columns Ø150 → **120 × 120**, each ground-founded one gaining a 0.35 m algae collar; **one lattice infill bay** on `EntryRail_P`. Rail height **1.05 → 1.10 m**, redefined as the **top face of the top rail** (how the KNPS register measures 폭높이). Sections are Korean **stocked** 방부각재 (`s3_research_numbers_v1.md` §D2, 5 suppliers): 90각/120각 posts, 38-series rails and balusters — KFS-TRAIL's 2010 drawing sizes 80 × 80 / 100 × 100 are **not** retail stock and are deliberately not used. `sc.build_railing_line` is **no longer called from this scene**, so the `baluster_r = 0.0` guard against the red team's 48 interpenetrating baluster pairs is preserved by **path removal**, which is strictly stronger than a flag. `broken_landing = 0` **unchanged** (§9 P-2) and asserted. **Rail-height authority, both sides recorded, per the user's real-case-first doctrine**: `[data]` KNPS-RAIL built reality — median **1.10 m**, **n = 1,227**, modes 1.00 (35.8 %) · 1.20 (19.9 %) · 1.10 (15.1 %), i.e. **71 % of real Korean trail railings are 1.0–1.2 m**; `[law]` **조경설계기준 16.20.2(2)** (관찰데크) *"안전을 위한 난간의 높이는 120cm 이상으로 하며"* is the **code counterpoint** — a 데크 is held to ≥1,200 mm where a plain 산책로 안전난간 is ≥1,100 mm (16.13.2(2)). PIRAN-15's 850 mm handrail binds 건축물 only, HOUSE-18's 1,200 mm binds 주택단지 only, and KCS 34 50 10 3.2.6 fixes no height at all, so **no statute binds this scene**; 1.10 m is taken on built reality per §8.R OQ-5, and the ≥1.2 m clause is written here so a reviewer meets the divergence **declared, not discovered**. Same treatment for the gap: 조경설계기준 16.13.2(3) is 안목 ≤100 mm **with a 단서 of ≤150 mm for a 계단중간 난간**, and 0.112 m sits inside the 단서 | **No walked-surface z change** — every member is above the walking plane; tread, landing and entry-deck tops are untouched and the SMOKE continuity table is unchanged. Hazard/collision list changes: the 14 `Post_*` cylinder colliders become 14 `Column_*` **box** colliders of a different section (Ø0.150 → 0.120 square); railing members carry no collider, before or after. **OCCL baseline moves substantially** — prim count **888 → 1038 (+150)**, the largest prim-count change in the scene | **R-1 + R-3** (registry re-derive + OCCL re-stamp); **rides GT-18's R-2**, which lands one commit later in the same batch (§0-2: one re-cache per scene per batch, and GT-18 carries it) | CB-S3-10 · GATE-1 pilot **10** | `OPEN` |
| **GT-21** | 10 | **Season re-bind — 만추 leaf-off pin** (S3-11, spec §2.A.3/§4.2-5). The census this closes `[measured]`: 12 trail trees + 12 hill trees + 13 shrub clumps = **37 green plants** plus **10 green hedge/crest bands**, against 4 brown leaf lobes; G10 carries **zero** green vegetation objects and wall-to-wall litter. After: **12/12 trail trees leaf-off** (`Gray_Birch` / `Elm_Sapling` / `Lombardy_Poplar` rotated — the only three USDs whose branch armature lives in the trunk prim, so `/Root/leaves` can be deactivated; registered in `sc.BARE_SUBPRIMS` by the K4 micro-commit `1346b70`, which reported success, so the §8.R contingency did **not** fire); **12/12 hill trees pinned to `Chinese_Juniper`** (an evergreen keeps its needles in 만추, so a green mass at distance is a conifer, not a season error — this is §4.2-5's oak re-assignment, since the oaks' leaves ride inside branch instancers and cannot be stripped); **13/13 shrub clumps** become real `Burning_Bush` / `Juniper` USDs (`Forsythia` and `Rhododendron` excluded — blossom-only and 76.7 % magenta); grass and hedge tints go dormant; litter becomes **continuous, 780 scattered instances** over the corridor and both margins, seated by `ground_fn` on the 25.8 % slope; **rock outcrop** `rock_moss_set_01` + 2 × `rock_03_broken` + `rock_02` at the uphill margin, `z_mode='base'`, **sink 0**; **3 distant windowless silhouette masses** at d_true ≥ **81.4 m** from the judged eyes. **Correction to the spec's tint, recorded rather than silently applied**: §4.2-5 gives the dormant grass tint as the literal `(0.62, 0.60, 0.42)`. A tint is a **multiplier**, not a colour, and `grass_lawn_diff` measures mean linear **(0.0621, 0.1115, 0.0232)** `[measured]`, so that triple yields (0.0385, 0.0669, 0.0097) — **R/G = 0.58, still green-dominant**: it darkens the lawn without dormanting it. The shipped tint is derived from a straw target instead — **(3.40, 1.55, 3.30)** → #7F734E, linear (0.211, 0.173, 0.077), Y 0.174, L* 48.8, **R/G 1.22**, inside the ≤0.30 ground albedo clamp, clipped fraction 0.02 %. Same arithmetic for the hedge bands. This is the cherry-blossom ruling applied again: judge by pixels, not by the value's name | **No geometry from the material half.** The vegetation half **is** a geometry change and is declared as such: all 24 trees leave the `build_tree` procedural/blob path for a pinned `add_vegetation` reference and all 13 shrub clumps leave the 3-ellipsoid blob for a real USD, so **every tree and shrub AABB moves** and `_grid_obstacles` must be read from the new census. Prim count 1219 → **2777 (+1558)**, almost all of it the 780 litter instances and the shrub/tree references. **No walked-surface z change** — nothing in this row touches the deck. The 4 CB-2 carpet-mask lobes are **kept** as the dense litter cores (H4: a lobe may move, it may never become a rectangle again); the continuity comes from scatter around them, not from more lobes | **R-1 + R-3** — R-1 because the tree/shrub AABBs move, R-3 to re-stamp OCCL; **rides GT-18's R-2** | CB-S3-10 · GATE-1 pilot **10** | `OPEN` |

---

## 4. Landing record — filled at land, never before

One line per row, appended by the **owning WP** at the moment it commits. A row without a landing
record is not `LANDED`.

| # | Owner WP | CB | Commit | Command actually used | Result (registry / diff / baseline) | Date |
|---|---|---|---|---|---|---|
| GT-1 | S2 | CB-7 | — | — | — | — |
| GT-2 | S2 | CB-7 | — | *(rides GT-1)* | — | — |
| GT-3 | S2 | CB-7 | — | — | — | — |
| GT-4 | S1 | CB-11 | — | — | — | — |
| GT-5 | S4 | CB-9 | — | — | — | — |
| GT-6 | K4(d) → S4 | CB-5 / CB-9 | — | — | — | — |
| GT-7 | S6 | CB-8 | — | — | — | — |
| GT-8 | K1 | CB-2 | *(CB-2 batch commit)* | `python3 scripts/placement_lint.py --scenes all --rules Docs/briefs/placement_rules_v1.yaml` · `python3 ground_kit.py` · `python3 scripts/geom_invariance_check.py` | **LINT-8 (no `rotz ≠ 0` on any patch/stain) 295 ERROR → 0**, measured A/B on the same tree at the same instant (every other check byte-identical: 374→79 ERROR total, WARN 359, BLOCK 29, INFO 2 unchanged). `ground_kit.py` 33/33 PASS. `geom_invariance_check` R-4 33/33 · R-6 33/33. **`frame_budget` movement, as the row predicted**: B2 area-share `scene08` 81.9→44.8 % · `scene19` 92.4→68.8 % · `scene15` 87.6→83.2 % · `sceneN1` 76.7→79.9 % · `scene05` 68.2→69.3 %; **B5 near-field decal count `sceneD2` 6→5, so D2 gains a soft B5 warn** — the only new soft-gate warning in the library and exactly the B1/B2/B5 movement spec §6.2-K1 told K1 to expect. **`regr_260730_w2d_fix.json` is retired from this commit**; the new baseline is stamped at CB-2's GATE-1 round `260731_w3_cb2`. R-2 (mini data render) **not owed** — no walked surface, no hazard box and no drop edge moves | 2026-07-31 |
| GT-9 | K1 | CB-2 | *(CB-2 batch commit)* | `python3 ground_kit.py` · per-scene element dump over all 33 `SCENE_PLANS` (`_fixture_plan` → elements of kind `weed`) · `python3 scripts/geom_invariance_check.py` | **Clamp factor, as required by §6-W1**: native exposure `zmax` **0.1229 m** `[measured — veg_manifest_w2.json]`, so the nominal ceiling scale is **s = 0.12 / 0.1229 = 0.9764** → exposure **0.1200 m** (exactly the class-A bound, not above it) and footprint **0.2789 × 0.9764 = 0.2723 m**. Scale is driven by the **GT-E5-clamped** `proud`, written back into the op by `_writeback_weed_heights` after `_clamp_gt_e5`; the largest height actually shipped is **0.1182 m** (`scene13`) → s **0.9618**, footprint **0.2683 m**. **25 of 85 clumps are clamped by the ramp, 0 dropped.** The bigger footprint bites as designed: profile δmax falls (`plaza_granite`-family 0.1182 → 0.0060–0.0103, `sceneC2`/`C4`/`15` 0.1182 → 0.0798, `02` → 0.0867, `08` → 0.0947, `16`/`N5` → 0.1041, `03`/`17`/`D3`/`N2`/`N4` → 0.1121). `_elem` aabb recomputed from the scaled bbox, and re-shrunk for clamped clumps so the registry cannot carry a footprint the stage does not have. **Count correction**: 85 instances / 13 scenes, not 139 / 22 — A1's own text deletes `plaza_granite`'s weed row (§7-W6). Class **A** confirmed: no clump exceeds 0.12 m, so no re-cache | 2026-07-31 |
| GT-10 | S5 | CB-1 | — | — | — | — |
| GT-11 | S1 | CB-10 | — | — | — | — |
| GT-12 | K3 | CB-4 | — | — | — | — |
| GT-13 | T4 → S3 · S4 | CB-10 | — | — | — | — |
| GT-14 | S3 | CB-S3-07 | — | — | — | — |
| GT-15 | S3 | CB-S3-07 | — | *(rides GT-14)* | — | — |
| GT-16 | S3 | CB-S3-07 | — | *(rides GT-14)* | — | — |
| GT-17 | S3 | CB-S3-07 | — | *(rides GT-14)* | — | — |

Owner column derived from spec §4.2/§4.3 file ownership (GT-1..GT-3 → S2 owns `scene02`; GT-4 → S1
owns `scene01`; GT-5 → S4 owns `scene13`; GT-6 → K4 owns the `scene_common` builders and S4 cuts
scene06; GT-7 → S6 owns `scene08`; GT-8/GT-9 → K1 owns `ground_kit`; GT-10 → S5 owns `scene09`;
GT-11 → S1 owns `scene05`; GT-12 → K3 owns `building_kit`; GT-13 → T4 owns the loader that binds
the override, consumed by S3/S4).

---

## 5. Carried-in records — GT debt from earlier waves

Not part of spec §8's 13. Listed because the ledger is the live file and these still owe an action.

| # | Scene | Change | z-profile effect | Re-cache step | Gate | Status |
|---|---|---|---|---|---|---|
| **R-1** | 13 | W2 ramp kerbs both sides **h 0.12 · w 0.30** (Parking Lot Act Enforcement Rule §6(1)5(c)) — built in W2 under supervisor approval **M4** | **A drop line that ought to exist was missing**; the W2 output gained **1 unlabelled drop** of 0.120 m | Label owed: the drop is recorded via the in-code `gt_changes` record (`ground_kit.py:1416-1420`, echoed by `scene13:833-837`) and is **reclaimed by the W4 GT drop map** | — (landed in W2) | `CARRIED-IN` — label owner **W4** |

**Why it matters to W3.** R-1 and **GT-5** are the same scene and the same kind of object (a 150 mm
statutory curb step vs the landed 120 mm ramp kerb). When GT-5 re-caches scene13 at CB-9, the R-1
drop must still be present and still unlabelled-but-recorded afterwards — a re-cache that quietly
absorbs or drops it is a regression, not a fix. It is the only in-code `gt_changes` record in the
whole tree (`redteam_w2d_edits.md:53`).

---

## 6. Cross-check log — each row against the source cited in spec §8

Method: every number in §3 re-derived from the tree at HEAD `04cc85c`, not from the source prose.
`[repro]` = reproduced exactly · `[confirm]` = the cited artefact exists and says what is claimed.

| # | Claim checked | Evidence | Verdict |
|---|---|---|---|
| GT-1 | Current total drop is 3.200 m, so +0.18 sill ⇒ **3.38 m** | `scenes/main/scene02_underpass.py:63` *"Total drop preserved: 10×0.160 + 0 + 10×0.160 = 3.200"*; `:53` *"opening front edge = drop 3.200"*; `:75` | `[repro]` 3.20 + 0.18 = 3.38 |
| GT-1 | Pit end is `x1 = 7.0`, not 8.2 (C-11 / RT-I R9) | `scene02:132` `pit=dict(x0=0.0, x1=7.0, y0=-1.75, y1=1.75)` | `[repro]` |
| GT-2 | Curb top currently **+0.10** above a 0.00 footway; road top −0.02 | `scene02:222` `curb_top=0.10, curb_base=-0.5`; docstring `scene02:860-861` *"The road top face −0.02 … Kerb top face +0.10 (10 cm above the sidewalk at 0.0)"* | `[repro]` — the spec's line citation is exact |
| GT-3 | Canopy is **four posts + a 2.4 × 4.9 m slab** | `scene02:240` `canopy=dict(x0=-1.8, x1=0.6, y0=-2.45, y1=2.45, …)` ⇒ 2.40 × 4.90 m; `scene_common.py:2013` *"1 roof slab + 4 corner columns"*, corners built at `:2022-2026` | `[repro]` both figures |
| GT-4 | Turf top **−0.63**, plaza top **0.0**; `prim_cap = 60` | `scene01:62` `upper_plaza=dict(…, z_top=0.0, thick=0.7)`; `scene01:873` grass plate top `z = −0.63`; `ground_kit.py:1440` `prim_cap=60` | `[repro]` |
| GT-4 | RT-I §4-N3 is the source of the missing flag | `Docs/reports/redteam_w3_intake.md:211` names **A 01-B** | `[confirm]` |
| GT-5 | `walk_north` / `walk_south` really are `proud = 0.007` | `scene13:182` and `scene13:184` | `[repro]` (`walk_cross:181` and `walk_spur:183` carry the same 0.007 and are **not** in the row — see §6-W2) |
| GT-6 | Landing `top_z = 4.998`, deck 5.000, `outer_r = 3.36`, chord margin 1.03 | `scene06:166` `top_z=4.998, base_z=4.498`; `:164` *"2 mm offset from the deck top 5.000"*; `:238` `railing=dict(outer_r=3.36, …)`; `:625` `chord = 2.0*r_out*sin(sd/2)*1.03` | `[repro]` all four |
| GT-6 | The `96968f3` method is a prim-hash proof | `git log 96968f3` — *"AST 해시 33/33 동일 · 프림 해시 33/33 동일"* | `[confirm]` |
| GT-6 | The 99.0 mm headline is unconfirmed | spec C-3 / `redteam_w3_intake.md:192` (√(3.30²+0.2223²) = 3.3075 ⇒ 7.5 mm) | `[confirm]` — row carries the T3 block |
| GT-7 | Exactly **2** `TempPost_*` collision boxes | `scene08:399-401` — `for i, gy in enumerate((pr["gap_y0"], pr["gap_y1"]))` appends `TempPost_{i}` | `[repro]` n = 2 |
| GT-7 | C-7's material-key correction | `scene08:913` `M["temtape"]` (not `M["tape"]`) | `[repro]` |
| GT-8 | Both AABB helpers exist and are in live use | `ground_kit.py:559` `_box_aabb`, `:564` `_obb_aabb`; `_obb_aabb` call sites `:737, :786, :818, :827, :838, :865, :879` | `[repro]` |
| GT-9 | **139** weed instances across **22** scenes | `Docs/reports/redteam_w3r.md:249` — *"8 of 19 profiles carry `("weed", n)`; × `SCENE_PLANS` = 22 scenes / 139 cubes"*, graded **exact** | `[confirm]` |
| GT-9 | Weed footprint is 0.10 m; `EDGE_STANDOFF = 0.80`; the GT-E5 ramp exists | `ground_kit.py:2803` `0.10, 0.10, hh`; `:123` `EDGE_STANDOFF = 0.80`; `:2050` *"GT-E5 ramp"*, `:2784` `exc="weed"` | `[repro]` |
| GT-10 | scene09 mooring posts, count and position | `scene09:215-218` — 6 entries at `cx = −1.2`, `cy = ±3.8 / ±13.5 / ±19.0`, `mooring_r=0.09, mooring_h=0.50`; `:212` records the v6 deletion of the \|y\| 8.5 pair | `[repro]` n = 6 |
| GT-11 | scene05 has a live wedge-gap defect and a self-check for it | `scene05:192` *"acute wedge / knife edge on the access stair arc"*; `:199` *"a crescent gap of up to 15 mm"*; `:222` *"wedges of up to 0.09 m on both sides"*; check at `:592, :616` | `[repro]` |
| GT-12 | Glazing is buried and the fix is a 5 mm proud pull | `Docs/surveys/w3r_building_ab_v1.md:23` *"All glazing is placed at out = −0.07 … −0.10 m, i.e. inside the solid mass"*; `:59` arm (b2) *"pulls the buried glazing 5 mm proud"*; `:296` `_unbury_glazing` moved **31** prims `[measured]` | `[confirm]` |
| GT-13 | Δσ_LF −0.32 is the worst-cut value, not the `h0.3_d5` value | spec C-20 (worst per-cut `h0.9_d5`: Δmean +1.50 · Δ`edge%` −1.69 · Δ`w80` +1.06 · **Δσ_LF −0.32**) | `[confirm]` |
| R-1 | The carried-in scene13 record exists in code | `ground_kit.py:1416-1420` `gt_changes=[dict(scene=None, item="ramp_curb", drop=…, label_owner="W4", …)]`; consumed at `scene13:833-837`; guard at `ground_kit.py:2363-2370` | `[repro]` |

**Result: 13 / 13 rows cross-check.** No §8 row was contradicted by the tree. Two watch items and
one source-prose discrepancy are recorded below rather than silently corrected.

---

## 7. Watch items and open discrepancies

These are **not** authorised changes to spec §8. They are recorded so the owning WP meets them with
its eyes open; a correction, if any, is the spec's to make.

- **W1 · GT-9's `h ≤ 0.12` condition is not free.** Native `Grass_Short_C` measures
  **0.279 × 0.304 × 0.125 m** (`assets/download_vegetation.py:433,447`). Native height **0.125 m is
  above** the `h ≤ 0.12` condition under which GT-9 declares "GT class stays A". So the row's own
  instruction — drive the scale from the **GT-E5-clamped `proud`** — is load-bearing, not advisory:
  placed at native scale the weed leaves class A and GT-9 becomes a GT change. K1 must state the
  applied scale factor and the resulting height in the landing record.
- **W2 · GT-5 names two of scene13's four `proud = 0.007` walks.** `walk_cross` (`scene13:181`) and
  `walk_spur` (`scene13:183`) carry the identical 7 mm and are **not** in the row. Under spec §12-11
  this ledger does not widen the row; S4 should confirm at CB-9 whether leaving two 7 mm walks beside
  two 150 mm curbed walks is the intended reading of the sample, and if the row needs widening, get
  it widened in the spec first — then append here.
- **W3 · RT-I §4-N3 names three geometry rows, spec §8 says "two".** `redteam_w3_intake.md:211`
  lists A 01-B (→ GT-4), B S06-B step 5 (scene13 walks → GT-5) **and** B S06-B step 2 (the scene02
  curb reshape → GT-2). All three are flagged in §3, so the ledger is complete either way; only the
  §8 preamble's count is short by one. No action beyond this note.
- **W4 · The `regr` baseline dies mid-wave.** `regr_260730_w2d_fix.json` is the comparison baseline
  for CB-1 only. From CB-2 (GT-8) every later row compares against the **new** baseline stamped at
  CB-2's gate. Rows GT-1, GT-5, GT-7, GT-11 and GT-13 all land after that point — their landing
  records must name **which** baseline they were checked against.
- **W6 · GT-9's instance census moved, and the spec is the reason.** §3 inherited
  *"22 scenes / 139 instances"* from `redteam_w3r.md:249`, which counted `("weed", n)` across
  8 of 19 profiles at intake. Spec §10.5's **A1 row itself** then ordered
  *"scene01's `plaza_granite` weed count → 0 (a maintained campus plaza has no weeds in the
  field)"*. `plaza_granite` is a **profile**, not a scene, and it carries 01 · 05 · 14 · 18 ·
  20 · 21 · C1 · N1 · N3, so honouring that row removes 9 × 6 = **54** instances and the
  census lands at **85 / 13**. K1 took the literal profile-level reading rather than
  special-casing scene01, because the spec names the profile and because a per-scene
  exception would have to be re-litigated for the other eight anyway. **The same row also
  moves DEC-3's patch count** (`plaza_granite` `("patch", 2)` → `("patch", 1)`, −9 prims
  library-wide). If the supervisor intended scene01 only, this is the row to amend — the
  change is one tuple in `GROUND_PROFILES`.
  **Supervisor ruling (07-31): profile-level reading CONFIRMED — W6 CLOSED.** The defect is
  profile-level (a maintained plaza carries no weed tufts regardless of which scene renders it);
  a scene01-only fork would leave the identical defect live in the 8 sibling scenes. RT's
  shipped-side census is adopted as the figure of record: **81 instances / 12 scenes shipped**
  (03 · C2 override `surface` to zero weeds, D3 to 8, scene18 re-adds 6 via its scene-side
  override that the profile-row deletion cannot reach → net −48 over 8 scenes), all 81 are
  `Grass_Short_C`, max shipped exposure **0.1174 m** (sceneN2) ≤ 0.12 — **class A holds
  shipped-side**. Per W7/C-12 any row depending on the count must re-derive from scene
  `PARAMS`. scene18's deliberate-looking weed override is NOT ruled here — its owning S-WP
  reconciles it against the scene archetype in WINDOW 3.
- **W7 · The weed census is a `SCENE_PLANS` figure, and C-12 applies to it.** The 85 / 13
  above is measured on the **fixture**. `scene03`'s shipped plan overrides `surface` to
  `(("patch", …), ("stain", …))` with no weed row at all, so the shipped tree carries fewer
  weeds than the fixture claims. Nothing in GT-9 depends on the count — the clamp is
  per-instance — but a later row that *does* depend on it must re-derive from the scenes'
  own `PARAMS`, per C-12.
- **W5 · GT-6 has two gates, one proof.** The builder change lands in CB-5 (`scene_common`, K4-d)
  and the scene cut lands in CB-9 (S4, blocked on T3). The invariance proof belongs to whichever
  lands first and must be **re-run** at the second — 05 · 19 · 13 share the builder and are not in
  CB-9's pilot set.

---

## 8. Append template

Copy, fill, append to §3 (and to §4 at land). Delete nothing.

```
| **GT-nn** | <scene(s)> | <change, with the numbers> | <z-profile effect; say "no walked-surface
z change" explicitly if that is the case> | <Full re-cache | R-1/R-2/R-3 subset | rides GT-mm |
proof only> | <CB-n · GATE-x pilot NN> | OPEN |
```

Rules for a new row: (a) name the failing/target millimetre, not an adjective; (b) if the change
adds a step **upward**, say so — an up-step mislabelled as a drop poisons the GT map (GT-1);
(c) if the row claims invariance, name the proof method; (d) if the row is gated by evidence,
mark it `HELD` and name the gate from spec §9.
